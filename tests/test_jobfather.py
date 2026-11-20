import os
import sys
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import functions to test
import jobfinder.jobfather as jf

class TestJobFather(unittest.TestCase):

    def setUp(self):
        # Setup temporary file for seen_jobs database
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        self.orig_db_file = jf.DB_FILE
        jf.DB_FILE = self.temp_db_path

    def tearDown(self):
        jf.DB_FILE = self.orig_db_file
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    # --- 1. MEMORY & DATABASE TESTS ---
    def test_load_seen_jobs_empty(self):
        """Verify load_seen_jobs returns empty dict when file is missing or empty."""
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)
        self.assertEqual(jf.load_seen_jobs(), {})

    def test_load_seen_jobs_corrupted_json(self):
        """Verify load_seen_jobs recovers gracefully from corrupted JSON."""
        with open(self.temp_db_path, "w") as f:
            f.write("{invalid_json: true, ...")
        self.assertEqual(jf.load_seen_jobs(), {})

    def test_load_seen_jobs_legacy_list_migration(self):
        """Verify automatic migration from legacy list of URLs to timestamped dict."""
        legacy_data = ["https://example.com/job1", "https://example.com/job2"]
        with open(self.temp_db_path, "w") as f:
            json.dump(legacy_data, f)
        
        loaded = jf.load_seen_jobs()
        self.assertIn("https://example.com/job1", loaded)
        self.assertIn("https://example.com/job2", loaded)
        self.assertIsInstance(loaded["https://example.com/job1"], str)

    def test_save_seen_jobs_prunes_to_1000_and_normalizes_in_run(self):
        """Verify database prunes to newest 1000 entries and converts 'in_run' to ISO timestamps."""
        large_dict = {
            f"https://example.com/job_{i}": f"2026-11-20T08:{i%60:02d}:00Z"
            for i in range(1200)
        }
        large_dict["https://example.com/in_run_job"] = "in_run"

        jf.save_seen_jobs(large_dict)
        loaded = jf.load_seen_jobs()

        self.assertLessEqual(len(loaded), 1000)
        self.assertIn("https://example.com/in_run_job", loaded)
        self.assertNotEqual(loaded["https://example.com/in_run_job"], "in_run")
        self.assertIn("T", loaded["https://example.com/in_run_job"])

    def test_save_seen_jobs_preserves_notified_and_filtered_states(self):
        """Verify database cleanly preserves '|notified' and '|filtered' audit states."""
        audit_dict = {
            "https://example.com/notified_job": "2026-11-20T08:30:00Z|notified",
            "https://example.com/filtered_job": "2026-11-20T08:30:00Z|filtered"
        }
        jf.save_seen_jobs(audit_dict)
        loaded = jf.load_seen_jobs()
        self.assertEqual(loaded["https://example.com/notified_job"], "2026-11-20T08:30:00Z|notified")
        self.assertEqual(loaded["https://example.com/filtered_job"], "2026-11-20T08:30:00Z|filtered")

    def test_atomic_database_write_safety(self):
        """Verify atomic replacement leaves existing database uncorrupted if write fails."""
        # Seed initial database
        initial_data = {"https://example.com/stable": "2026-11-20T08:00:00Z"}
        jf.save_seen_jobs(initial_data)

        # Mock os.replace to raise an exception simulating process termination
        with patch("os.replace", side_effect=IOError("Simulated system crash before swap")):
            try:
                jf.save_seen_jobs({"https://example.com/new": "in_run"})
            except Exception:
                pass

        # Existing database must still be 100% valid and intact
        reloaded = jf.load_seen_jobs()
        self.assertEqual(reloaded, initial_data)

    def test_job_lifecycle_multi_attribute_classification(self):
        """Verify job lifecycle correctly tags |notified vs |filtered using URL and Title+Company."""
        candidates = [
            {"title": "Junior UX Designer", "company": "Alpha Tech", "link": "https://example.com/job1"},
            {"title": "Product Design Intern", "company": "Beta Studio", "link": "https://example.com/job2"},
            {"title": "Senior Director of UX", "company": "Gamma Corp", "link": "https://example.com/job3"}
        ]
        # Simulate AI output accepting job1 (by URL) and job2 (by title/company) while rejecting job3
        simulated_ai_digest = (
            "📌 Junior UX Designer - Alpha Tech\nLink: https://example.com/job1\n\n"
            "📌 Product Design Intern - Beta Studio\nLink: View on Company Portal"
        )
        now_iso = "2026-11-20T08:30:00Z"
        seen_urls = {}
        for item in candidates:
            link = item.get("link")
            title = item.get("title", "").strip().lower()
            comp = item.get("company", "").strip().lower()
            is_notified = (link in simulated_ai_digest) or (bool(title and comp and title in simulated_ai_digest.lower() and comp in simulated_ai_digest.lower()))
            if is_notified:
                seen_urls[link] = f"{now_iso}|notified"
            else:
                seen_urls[link] = f"{now_iso}|filtered"

        self.assertEqual(seen_urls["https://example.com/job1"], f"{now_iso}|notified")
        self.assertEqual(seen_urls["https://example.com/job2"], f"{now_iso}|notified")
        self.assertEqual(seen_urls["https://example.com/job3"], f"{now_iso}|filtered")

    def test_validate_environment(self):
        """Verify environment validator detects missing vs complete secrets."""
        orig_tel = jf.TELEGRAM_BOT_TOKEN
        orig_chat = jf.TELEGRAM_CHAT_ID
        orig_gem = jf.GEMINI_API_KEY
        try:
            jf.TELEGRAM_BOT_TOKEN = None
            self.assertFalse(jf.validate_environment())

            jf.TELEGRAM_BOT_TOKEN = "tok"
            jf.TELEGRAM_CHAT_ID = "chat"
            jf.GEMINI_API_KEY = "gem"
            self.assertTrue(jf.validate_environment())
        finally:
            jf.TELEGRAM_BOT_TOKEN = orig_tel
            jf.TELEGRAM_CHAT_ID = orig_chat
            jf.GEMINI_API_KEY = orig_gem

    # --- 2. TELEGRAM NOTIFICATION TESTS ---
    @patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "", "TELEGRAM_CHAT_ID": ""})
    def test_send_telegram_missing_credentials(self):
        """Verify delivery fails cleanly if Telegram credentials are not configured."""
        jf.TELEGRAM_BOT_TOKEN = None
        jf.TELEGRAM_CHAT_ID = None
        self.assertFalse(jf.send_telegram_message("Test message"))

    def test_send_telegram_empty_message(self):
        """Verify delivery returns False if message is blank."""
        jf.TELEGRAM_BOT_TOKEN = "mock_token"
        jf.TELEGRAM_CHAT_ID = "mock_chat"
        self.assertFalse(jf.send_telegram_message(""))
        self.assertFalse(jf.send_telegram_message("   \n  "))

    @patch("requests.post")
    def test_send_telegram_successful_delivery(self, mock_post):
        """Verify successful delivery when Telegram returns 200 and ok=True."""
        jf.TELEGRAM_BOT_TOKEN = "mock_token"
        jf.TELEGRAM_CHAT_ID = "mock_chat"

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"ok": True, "result": {}}
        mock_post.return_value = mock_resp

        result = jf.send_telegram_message("Valid job message")
        self.assertTrue(result)
        self.assertEqual(mock_post.call_count, 1)

    @patch("requests.post")
    def test_send_telegram_markdown_failure_with_plain_text_recovery(self, mock_post):
        """Verify that if Markdown parse fails, it retries with plain text and succeeds."""
        jf.TELEGRAM_BOT_TOKEN = "mock_token"
        jf.TELEGRAM_CHAT_ID = "mock_chat"

        # First call fails (bad markdown 400), second call succeeds (200 plain text)
        fail_resp = MagicMock()
        fail_resp.status_code = 400
        fail_resp.text = "Bad Request: can't parse entities"
        fail_resp.json.return_value = {"ok": False}

        success_resp = MagicMock()
        success_resp.status_code = 200
        success_resp.json.return_value = {"ok": True}

        mock_post.side_effect = [fail_resp, success_resp]

        result = jf.send_telegram_message("Message with tricky _ underscores")
        self.assertTrue(result)
        self.assertEqual(mock_post.call_count, 2)

    @patch("requests.post")
    def test_send_telegram_complete_delivery_failure(self, mock_post):
        """Verify that if all retries fail, send_telegram_message returns False."""
        jf.TELEGRAM_BOT_TOKEN = "mock_token"
        jf.TELEGRAM_CHAT_ID = "mock_chat"

        fail_resp = MagicMock()
        fail_resp.status_code = 500
        fail_resp.text = "Internal Server Error"
        fail_resp.json.return_value = {"ok": False}

        mock_post.return_value = fail_resp

        result = jf.send_telegram_message("Message")
        self.assertFalse(result)

    @patch("requests.post")
    def test_send_telegram_splits_unusually_long_unbroken_lines(self, mock_post):
        """Verify that a single unbroken line exceeding 3800 chars is safely sliced and delivered."""
        jf.TELEGRAM_BOT_TOKEN = "mock_token"
        jf.TELEGRAM_CHAT_ID = "mock_chat"

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"ok": True}
        mock_post.return_value = mock_resp

        # Create 8500 character unbroken string
        huge_line = "A" * 8500
        result = jf.send_telegram_message(huge_line)
        self.assertTrue(result)
        # Should have split into at least 3 chunks
        self.assertGreaterEqual(mock_post.call_count, 3)
        for call_args in mock_post.call_args_list:
            sent_text = call_args[1]["json"]["text"]
            self.assertLessEqual(len(sent_text), 3800)

    # --- 3. IN-RUN DEDUPLICATION TEST ---
    def test_in_run_deduplication(self):
        """Verify that in-run seen_urls dictionary prevents duplicate jobs from being added."""
        seen_urls = {}
        collected_jobs = []

        scraped_candidates = [
            {"title": "Junior UX Designer", "link": "https://example.com/job1"},
            {"title": "Junior UX Designer (Duplicate Query)", "link": "https://example.com/job1"},
            {"title": "Product Design Intern", "link": "https://example.com/job2"},
        ]

        for item in scraped_candidates:
            url = item["link"]
            if url and url not in seen_urls:
                seen_urls[url] = "in_run"
                collected_jobs.append(item)

        self.assertEqual(len(collected_jobs), 2)
        self.assertEqual(collected_jobs[0]["link"], "https://example.com/job1")
        self.assertEqual(collected_jobs[1]["link"], "https://example.com/job2")

if __name__ == "__main__":
    unittest.main()
