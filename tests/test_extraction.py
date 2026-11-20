import os
import sys
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from jobfinder.jobfather import (
    build_normalized_record,
    VALID_SOURCE_TYPES,
    VALID_REMOTE_TYPES,
    VALID_EMPLOYMENT_TYPES,
    VALID_EXTRACTION_STATUSES,
    VALID_PROVENANCE_TAGS,
)

class TestExtractionContractBuilder(unittest.TestCase):
    """Focused unit tests for build_normalized_record() conforming to
    EXTRACTION_RELIABILITY_PLAN.md v1.3 Phase 3A requirements."""

    def test_build_valid_fully_extracted_record(self):
        """Test building a valid, fully extracted job record from a structured API."""
        record = build_normalized_record(
            run_candidate_id="run_001",
            source_name="Remotive",
            source_type="STRUCTURED_API",
            ingestion_tier=1,
            source_url="https://remotive.com/api/remote-jobs",
            job_url="https://remotive.com/jobs/design/101",
            raw_title="Junior Product Designer",
            company_name="Canva",
            location_raw="Worldwide",
            remote_type="REMOTE_WORLDWIDE",
            experience_raw="0-2 years",
            employment_type="FULL_TIME",
            salary_raw="$40,000 - $60,000",
            posted_date="2026-11-20T00:00:00Z",
            deadline_raw="2026-12-31",
            description_excerpt="We are looking for a Junior Product Designer to join our team...",
            is_snippet_only=False,
            is_discovery_only=False,
            field_provenance={
                "raw_title": "API_FIELD",
                "company_name": "API_FIELD",
                "job_url": "API_FIELD",
                "location_raw": "API_FIELD",
                "experience_raw": "API_FIELD",
                "salary_raw": "API_FIELD",
                "posted_date": "API_FIELD",
                "deadline_raw": "API_FIELD",
                "description_excerpt": "API_FIELD",
            }
        )

        self.assertEqual(record["run_candidate_id"], "run_001")
        self.assertEqual(record["source_name"], "Remotive")
        self.assertEqual(record["source_type"], "STRUCTURED_API")
        self.assertEqual(record["ingestion_tier"], 1)
        self.assertEqual(record["source_url"], "https://remotive.com/api/remote-jobs")
        self.assertEqual(record["job_url"], "https://remotive.com/jobs/design/101")
        self.assertEqual(record["raw_title"], "Junior Product Designer")
        self.assertEqual(record["company_name"], "Canva")
        self.assertEqual(record["location_raw"], "Worldwide")
        self.assertEqual(record["remote_type"], "REMOTE_WORLDWIDE")
        self.assertEqual(record["employment_type"], "FULL_TIME")
        self.assertFalse(record["is_snippet_only"])
        self.assertFalse(record["is_discovery_only"])
        self.assertEqual(record["extraction_status"], "FULLY_EXTRACTED")
        self.assertEqual(record["missing_fields"], [])
        self.assertEqual(record["field_provenance"]["raw_title"], "API_FIELD")
        self.assertEqual(record["field_provenance"]["discovery_snippet"], "NOT_PROVIDED")

        # Verify all 22 contract keys are present
        expected_keys = {
            "run_candidate_id", "source_name", "source_type", "ingestion_tier",
            "source_url", "job_url", "raw_title", "company_name", "location_raw",
            "remote_type", "experience_raw", "employment_type", "salary_raw",
            "posted_date", "deadline_raw", "description_excerpt", "discovery_snippet",
            "is_snippet_only", "is_discovery_only", "extraction_status",
            "missing_fields", "field_provenance"
        }
        self.assertEqual(set(record.keys()), expected_keys)

    def test_build_partially_extracted_record_missing_company(self):
        """Test building a direct job card (e.g. LinkedIn) missing company name."""
        record = build_normalized_record(
            run_candidate_id="run_002",
            source_name="LinkedIn Direct",
            source_type="DIRECT_PAGE_SCRAPE",
            ingestion_tier=3,
            source_url="https://linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search",
            job_url="https://www.linkedin.com/jobs/view/123456",
            raw_title="UI/UX Designer",
            company_name=None,  # Missing company
            location_raw="Dhaka, Bangladesh",
            remote_type="ON_SITE",
            is_snippet_only=False,
            is_discovery_only=False,  # Direct job card counts as parsed listing content
            field_provenance={
                "raw_title": "DOM_SELECTOR",
                "job_url": "DOM_SELECTOR",
                "location_raw": "DOM_SELECTOR",
            }
        )

        self.assertEqual(record["raw_title"], "UI/UX Designer")
        self.assertIsNone(record["company_name"])
        self.assertFalse(record["is_snippet_only"])
        self.assertFalse(record["is_discovery_only"])
        self.assertEqual(record["extraction_status"], "PARTIALLY_EXTRACTED")
        self.assertIn("company_name", record["missing_fields"])
        self.assertEqual(record["field_provenance"]["company_name"], "NOT_PROVIDED")

    def test_build_partially_extracted_record_missing_location(self):
        """Test building a record with title and company but missing location_raw.
        Must result in PARTIALLY_EXTRACTED because location is an essential listing field."""
        record = build_normalized_record(
            run_candidate_id="run_002b",
            source_name="LinkedIn Direct",
            source_type="DIRECT_PAGE_SCRAPE",
            ingestion_tier=3,
            source_url="https://linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search",
            job_url="https://www.linkedin.com/jobs/view/654321",
            raw_title="UI/UX Designer",
            company_name="Brain Station 23",
            location_raw=None,  # Missing location
            is_snippet_only=False,
            is_discovery_only=False,
            field_provenance={
                "raw_title": "DOM_SELECTOR",
                "company_name": "DOM_SELECTOR",
                "job_url": "DOM_SELECTOR",
            }
        )

        self.assertEqual(record["extraction_status"], "PARTIALLY_EXTRACTED")
        self.assertIn("location_raw", record["missing_fields"])
        self.assertEqual(record["field_provenance"]["location_raw"], "NOT_PROVIDED")

    def test_explicit_fully_extracted_rejected_if_essential_field_missing(self):
        """Verify that explicit extraction_status='FULLY_EXTRACTED' is rejected when
        either company_name or location_raw is missing."""
        base_args = {
            "run_candidate_id": "run_002c",
            "source_name": "LinkedIn Direct",
            "source_type": "DIRECT_PAGE_SCRAPE",
            "ingestion_tier": 3,
            "source_url": "https://linkedin.com/jobs/search",
            "job_url": "https://linkedin.com/jobs/view/1",
            "raw_title": "UI Designer",
            "is_snippet_only": False,
            "is_discovery_only": False,
            "extraction_status": "FULLY_EXTRACTED",
        }

        # Missing location_raw
        with self.assertRaises(ValueError) as ctx:
            build_normalized_record(
                **base_args,
                company_name="Canva",
                location_raw=None,
                field_provenance={"raw_title": "DOM_SELECTOR", "company_name": "DOM_SELECTOR", "job_url": "DOM_SELECTOR"}
            )
        self.assertIn("location_raw", str(ctx.exception))

        # Missing company_name
        with self.assertRaises(ValueError) as ctx:
            build_normalized_record(
                **base_args,
                company_name=None,
                location_raw="Dhaka, Bangladesh",
                field_provenance={"raw_title": "DOM_SELECTOR", "location_raw": "DOM_SELECTOR", "job_url": "DOM_SELECTOR"}
            )
        self.assertIn("company_name", str(ctx.exception))

    def test_explicit_partially_extracted_rejected_if_all_essential_fields_present(self):
        """Verify that explicit extraction_status='PARTIALLY_EXTRACTED' is rejected when
        all four essential fields (title, url, company, location) are present."""
        with self.assertRaises(ValueError) as ctx:
            build_normalized_record(
                run_candidate_id="run_002e",
                source_name="Remotive",
                source_type="STRUCTURED_API",
                ingestion_tier=1,
                source_url="https://remotive.com",
                job_url="https://remotive.com/job/1",
                raw_title="Senior Product Designer",
                company_name="Canva",
                location_raw="Worldwide",
                is_snippet_only=False,
                is_discovery_only=False,
                extraction_status="PARTIALLY_EXTRACTED",  # CONTRADICTION: all essential present!
                field_provenance={
                    "raw_title": "API_FIELD",
                    "company_name": "API_FIELD",
                    "job_url": "API_FIELD",
                    "location_raw": "API_FIELD",
                }
            )
        self.assertIn("cannot be 'PARTIALLY_EXTRACTED' when all essential fields are present", str(ctx.exception))

    def test_missing_optional_fields_do_not_downgrade_completeness(self):
        """Verify that missing optional fields (salary, deadline, experience, posted_date)
        do NOT downgrade an otherwise complete record from FULLY_EXTRACTED."""
        record = build_normalized_record(
            run_candidate_id="run_002d",
            source_name="Remotive",
            source_type="STRUCTURED_API",
            ingestion_tier=1,
            source_url="https://remotive.com/api",
            job_url="https://remotive.com/job/10",
            raw_title="Product Designer",
            company_name="Stripe",
            location_raw="Worldwide",
            salary_raw=None,       # Optional missing
            deadline_raw=None,     # Optional missing
            experience_raw=None,   # Optional missing
            posted_date=None,      # Optional missing
            is_snippet_only=False,
            is_discovery_only=False,
            field_provenance={
                "raw_title": "API_FIELD",
                "company_name": "API_FIELD",
                "job_url": "API_FIELD",
                "location_raw": "API_FIELD",
            }
        )

        self.assertEqual(record["extraction_status"], "FULLY_EXTRACTED")
        self.assertIn("salary_raw", record["missing_fields"])
        self.assertIn("deadline_raw", record["missing_fields"])
        self.assertEqual(record["field_provenance"]["salary_raw"], "NOT_PROVIDED")
        self.assertEqual(record["field_provenance"]["deadline_raw"], "NOT_PROVIDED")

    def test_build_discovery_lead_search_snippet(self):
        """Test building a search engine snippet (e.g. DuckDuckGo fallback)."""
        record = build_normalized_record(
            run_candidate_id="run_003",
            source_name="Web-Search",
            source_type="SEARCH_SNIPPET",
            ingestion_tier=5,
            source_url="https://html.duckduckgo.com/html/?q=UI+UX+Designer+Dhaka",
            job_url="https://example.com/jobs/456",
            raw_title=None,
            company_name=None,
            discovery_snippet="Hiring Junior UI/UX Designer in Dhaka. Apply now with portfolio.",
            is_snippet_only=True,
            is_discovery_only=True,
            field_provenance={
                "job_url": "SEARCH_SNIPPET",
                "discovery_snippet": "SEARCH_SNIPPET",
            }
        )

        self.assertIsNone(record["raw_title"])
        self.assertIsNone(record["company_name"])
        self.assertTrue(record["is_snippet_only"])
        self.assertTrue(record["is_discovery_only"])
        self.assertEqual(record["extraction_status"], "DISCOVERY_ONLY")
        self.assertIn("raw_title", record["missing_fields"])
        self.assertIn("company_name", record["missing_fields"])
        self.assertEqual(record["discovery_snippet"], "Hiring Junior UI/UX Designer in Dhaka. Apply now with portfolio.")

    def test_build_discovery_lead_facebook_post_without_external_url(self):
        """Test building a Facebook Apify community post lead lacking an external job URL.
        Crucial requirement: job_url=None must be allowed and the lead preserved with its source_url."""
        record = build_normalized_record(
            run_candidate_id="run_004",
            source_name="Apify-Facebook",
            source_type="COMMUNITY_POST",
            ingestion_tier=4,
            source_url="https://www.facebook.com/groups/uxbd/posts/987654321",
            job_url=None,  # No external application website in post
            raw_title=None,
            company_name=None,
            discovery_snippet="We are looking for a Junior UI Designer. Send CV to our page inbox.",
            is_snippet_only=False,  # Facebook post is NOT a search snippet
            is_discovery_only=True,  # Unparsed community discovery lead
            field_provenance={"discovery_snippet": "COMMUNITY_POST"}
        )

        self.assertIsNone(record["job_url"])
        self.assertEqual(record["source_url"], "https://www.facebook.com/groups/uxbd/posts/987654321")
        self.assertFalse(record["is_snippet_only"])
        self.assertTrue(record["is_discovery_only"])
        self.assertEqual(record["extraction_status"], "DISCOVERY_ONLY")
        self.assertIn("job_url", record["missing_fields"])
        self.assertIn("raw_title", record["missing_fields"])
        self.assertIn("company_name", record["missing_fields"])
        self.assertEqual(record["field_provenance"]["job_url"], "NOT_PROVIDED")

    def test_build_discovery_lead_facebook_post_with_external_url(self):
        """Test building a Facebook Apify community post that includes an external application URL."""
        record = build_normalized_record(
            run_candidate_id="run_005",
            source_name="Apify-Facebook",
            source_type="COMMUNITY_POST",
            ingestion_tier=4,
            source_url="https://www.facebook.com/groups/uxbd/posts/987654322",
            job_url="https://careers.techcorp.com/apply/ux-intern",
            raw_title=None,
            company_name=None,
            discovery_snippet="TechCorp is hiring an intern! Apply here: https://careers.techcorp.com/apply/ux-intern",
            is_snippet_only=False,
            is_discovery_only=True,
            field_provenance={
                "discovery_snippet": "COMMUNITY_POST",
                "job_url": "COMMUNITY_POST",
            }
        )

        self.assertEqual(record["job_url"], "https://careers.techcorp.com/apply/ux-intern")
        self.assertEqual(record["source_url"], "https://www.facebook.com/groups/uxbd/posts/987654322")
        self.assertFalse(record["is_snippet_only"])
        self.assertTrue(record["is_discovery_only"])
        self.assertEqual(record["extraction_status"], "DISCOVERY_ONLY")
        self.assertNotIn("job_url", record["missing_fields"])

    def test_source_type_and_flag_relationships(self):
        """Verify strict enforcement of source-type to flag relationships."""
        # 1. SEARCH_SNIPPET requires is_snippet_only=True and is_discovery_only=True
        with self.assertRaises(ValueError):
            build_normalized_record(
                run_candidate_id="run_011",
                source_name="Search",
                source_type="SEARCH_SNIPPET",
                ingestion_tier=5,
                source_url="https://ddg.gg",
                job_url="https://example.com/job",
                is_snippet_only=False,  # INVALID!
                is_discovery_only=True,
                field_provenance={"job_url": "SEARCH_SNIPPET"}
            )
        with self.assertRaises(ValueError):
            build_normalized_record(
                run_candidate_id="run_012",
                source_name="Search",
                source_type="SEARCH_SNIPPET",
                ingestion_tier=5,
                source_url="https://ddg.gg",
                job_url="https://example.com/job",
                is_snippet_only=True,
                is_discovery_only=False,  # INVALID!
                field_provenance={"job_url": "SEARCH_SNIPPET"}
            )

        # 2. COMMUNITY_POST requires is_snippet_only=False and is_discovery_only=True
        with self.assertRaises(ValueError):
            build_normalized_record(
                run_candidate_id="run_013",
                source_name="Facebook",
                source_type="COMMUNITY_POST",
                ingestion_tier=4,
                source_url="https://facebook.com/post/1",
                job_url="https://example.com/job",
                is_snippet_only=True,  # INVALID: community posts are not search snippets
                is_discovery_only=True,
                field_provenance={"job_url": "COMMUNITY_POST"}
            )
        with self.assertRaises(ValueError):
            build_normalized_record(
                run_candidate_id="run_014",
                source_name="Facebook",
                source_type="COMMUNITY_POST",
                ingestion_tier=4,
                source_url="https://facebook.com/post/1",
                job_url="https://example.com/job",
                is_snippet_only=False,
                is_discovery_only=False,  # INVALID!
                field_provenance={"job_url": "COMMUNITY_POST"}
            )

        # 3. STRUCTURED_API requires both flags False
        with self.assertRaises(ValueError):
            build_normalized_record(
                run_candidate_id="run_015",
                source_name="Remotive",
                source_type="STRUCTURED_API",
                ingestion_tier=1,
                source_url="https://remotive.com",
                job_url="https://remotive.com/job/1",
                raw_title="Designer",
                company_name="Acme",
                location_raw="Remote",
                is_snippet_only=True,  # INVALID!
                is_discovery_only=False,
                field_provenance={"raw_title": "API_FIELD", "company_name": "API_FIELD", "job_url": "API_FIELD", "location_raw": "API_FIELD"}
            )
        with self.assertRaises(ValueError):
            build_normalized_record(
                run_candidate_id="run_016",
                source_name="Remotive",
                source_type="STRUCTURED_API",
                ingestion_tier=1,
                source_url="https://remotive.com",
                job_url="https://remotive.com/job/1",
                raw_title="Designer",
                company_name="Acme",
                location_raw="Remote",
                is_snippet_only=False,
                is_discovery_only=True,  # INVALID!
                field_provenance={"raw_title": "API_FIELD", "company_name": "API_FIELD", "job_url": "API_FIELD", "location_raw": "API_FIELD"}
            )

    def test_wrong_types_for_fields_rejected_with_typeerror(self):
        """Verify that passing wrong types (integers, lists, dicts) for optional or mandatory
        fields raises TypeError instead of silent conversion."""
        base_args = {
            "run_candidate_id": "run_020",
            "source_name": "Remotive",
            "source_type": "STRUCTURED_API",
            "ingestion_tier": 1,
            "source_url": "https://remotive.com",
            "job_url": "https://remotive.com/job/1",
            "raw_title": "Designer",
            "company_name": "Acme",
            "location_raw": "Worldwide",
            "is_snippet_only": False,
            "is_discovery_only": False,
            "field_provenance": {
                "raw_title": "API_FIELD",
                "company_name": "API_FIELD",
                "job_url": "API_FIELD",
                "location_raw": "API_FIELD",
            }
        }

        # Non-string optional fields
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "job_url": 12345})
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "raw_title": ["Designer"]})
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "company_name": {"name": "Acme"}})
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "location_raw": 999})
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "experience_raw": 2})
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "salary_raw": 50000})
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "posted_date": 20261120})
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "deadline_raw": ["2026-12-31"]})
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "description_excerpt": True})
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "discovery_snippet": 100})

        # Non-string mandatory/enum fields
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "run_candidate_id": 10})
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "source_name": 123})
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "source_url": ["url"]})
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "source_type": 1})
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "remote_type": 1})
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "employment_type": 1})

        # Boolean ingestion_tier
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "ingestion_tier": True})
        with self.assertRaises(TypeError):
            build_normalized_record(**{**base_args, "ingestion_tier": "1"})

    def test_provenance_validation(self):
        """Verify strict validation of field_provenance dictionary, tags, and field names."""
        base_args = {
            "run_candidate_id": "run_030",
            "source_name": "Remotive",
            "source_type": "STRUCTURED_API",
            "ingestion_tier": 1,
            "source_url": "https://remotive.com",
            "job_url": "https://remotive.com/job/1",
            "raw_title": "Designer",
            "company_name": "Acme",
            "location_raw": "Worldwide",
            "is_snippet_only": False,
            "is_discovery_only": False,
        }

        # 1. Non-dict field_provenance raises TypeError
        with self.assertRaises(TypeError):
            build_normalized_record(**base_args, field_provenance="API_FIELD")

        # 2. Unknown field name in provenance raises ValueError
        with self.assertRaises(ValueError) as ctx:
            build_normalized_record(
                **base_args,
                field_provenance={
                    "raw_title": "API_FIELD",
                    "company_name": "API_FIELD",
                    "job_url": "API_FIELD",
                    "location_raw": "API_FIELD",
                    "non_existent_key": "API_FIELD",
                }
            )
        self.assertIn("non_existent_key", str(ctx.exception))

        # 3. Invalid provenance tag raises ValueError
        with self.assertRaises(ValueError) as ctx:
            build_normalized_record(
                **base_args,
                field_provenance={
                    "raw_title": "API_FIELD",
                    "company_name": "API_FIELD",
                    "job_url": "API_FIELD",
                    "location_raw": "MADE_UP_TAG",
                }
            )
        self.assertIn("MADE_UP_TAG", str(ctx.exception))

        # 4. Missing field incorrectly labelled with valid extraction tag raises ValueError
        with self.assertRaises(ValueError) as ctx:
            build_normalized_record(
                run_candidate_id="run_031",
                source_name="LinkedIn",
                source_type="DIRECT_PAGE_SCRAPE",
                ingestion_tier=3,
                source_url="https://linkedin.com",
                job_url="https://linkedin.com/job/1",
                raw_title="Designer",
                company_name=None,  # MISSING!
                location_raw="Dhaka",
                is_snippet_only=False,
                is_discovery_only=False,
                field_provenance={
                    "raw_title": "DOM_SELECTOR",
                    "job_url": "DOM_SELECTOR",
                    "location_raw": "DOM_SELECTOR",
                    "company_name": "DOM_SELECTOR",  # INVALID: Cannot claim DOM_SELECTOR for None!
                }
            )
        self.assertIn("company_name", str(ctx.exception))
        self.assertIn("NOT_PROVIDED", str(ctx.exception))

        # 5. Populated field with missing provenance raises ValueError
        with self.assertRaises(ValueError) as ctx:
            build_normalized_record(
                **base_args,
                field_provenance={
                    "raw_title": "API_FIELD",
                    "company_name": "API_FIELD",
                    "job_url": "API_FIELD",
                    # location_raw is populated ("Worldwide") but omitted from provenance!
                }
            )
        self.assertIn("location_raw", str(ctx.exception))

        # 6. Populated field given 'NOT_PROVIDED' raises ValueError
        with self.assertRaises(ValueError) as ctx:
            build_normalized_record(
                **base_args,
                field_provenance={
                    "raw_title": "API_FIELD",
                    "company_name": "API_FIELD",
                    "job_url": "API_FIELD",
                    "location_raw": "NOT_PROVIDED",  # INVALID: Populated field cannot be NOT_PROVIDED!
                }
            )
        self.assertIn("location_raw", str(ctx.exception))

    def test_excerpt_and_snippet_provenance_validation(self):
        """Verify strict provenance validation on description_excerpt and discovery_snippet."""
        base_args = {
            "run_candidate_id": "run_035",
            "source_name": "Remotive",
            "source_type": "STRUCTURED_API",
            "ingestion_tier": 1,
            "source_url": "https://remotive.com",
            "job_url": "https://remotive.com/job/1",
            "raw_title": "Designer",
            "company_name": "Acme",
            "location_raw": "Worldwide",
            "is_snippet_only": False,
            "is_discovery_only": False,
        }

        # 1. Populated description_excerpt with missing provenance raises ValueError
        with self.assertRaises(ValueError) as ctx:
            build_normalized_record(
                **base_args,
                description_excerpt="A real job description excerpt...",
                field_provenance={
                    "raw_title": "API_FIELD",
                    "company_name": "API_FIELD",
                    "job_url": "API_FIELD",
                    "location_raw": "API_FIELD",
                    # description_excerpt is populated but missing from provenance!
                }
            )
        self.assertIn("description_excerpt", str(ctx.exception))

        # 2. Blank description_excerpt given extraction tag raises ValueError
        with self.assertRaises(ValueError) as ctx:
            build_normalized_record(
                **base_args,
                description_excerpt="",  # Blank
                field_provenance={
                    "raw_title": "API_FIELD",
                    "company_name": "API_FIELD",
                    "job_url": "API_FIELD",
                    "location_raw": "API_FIELD",
                    "description_excerpt": "API_FIELD",  # INVALID for blank field!
                }
            )
        self.assertIn("description_excerpt", str(ctx.exception))
        self.assertIn("NOT_PROVIDED", str(ctx.exception))

        # 3. Populated discovery_snippet with missing provenance raises ValueError
        with self.assertRaises(ValueError) as ctx:
            build_normalized_record(
                run_candidate_id="run_036",
                source_name="Web-Search",
                source_type="SEARCH_SNIPPET",
                ingestion_tier=5,
                source_url="https://ddg.gg",
                job_url="https://example.com/job/1",
                discovery_snippet="Hiring junior designer...",
                is_snippet_only=True,
                is_discovery_only=True,
                field_provenance={
                    "job_url": "SEARCH_SNIPPET",
                    # discovery_snippet is populated but missing from provenance!
                }
            )
        self.assertIn("discovery_snippet", str(ctx.exception))

        # 4. Invalid provenance tag on excerpt field raises ValueError
        with self.assertRaises(ValueError) as ctx:
            build_normalized_record(
                **base_args,
                description_excerpt="A real job description excerpt...",
                field_provenance={
                    "raw_title": "API_FIELD",
                    "company_name": "API_FIELD",
                    "job_url": "API_FIELD",
                    "location_raw": "API_FIELD",
                    "description_excerpt": "INVENTED_TAG",  # INVALID!
                }
            )
        self.assertIn("INVENTED_TAG", str(ctx.exception))

    def test_text_truncation_limits(self):
        """Ensure description_excerpt and discovery_snippet are capped at 500 characters."""
        long_text = "A" * 800
        record = build_normalized_record(
            run_candidate_id="run_040",
            source_name="Test Source",
            source_type="STRUCTURED_API",
            ingestion_tier=1,
            source_url="https://example.com/api",
            job_url="https://example.com/job/1",
            raw_title="Designer",
            company_name="Acme",
            location_raw="Worldwide",
            description_excerpt=long_text,
            is_snippet_only=False,
            is_discovery_only=False,
            field_provenance={
                "raw_title": "API_FIELD",
                "company_name": "API_FIELD",
                "job_url": "API_FIELD",
                "location_raw": "API_FIELD",
                "description_excerpt": "API_FIELD",
            }
        )

        self.assertEqual(len(record["description_excerpt"]), 500)
        self.assertEqual(len(record["discovery_snippet"]), 0)

    def test_preserves_none_without_inventing_placeholders(self):
        """Ensure unverified optional fields evaluate strictly to None and are not replaced
        by artificial placeholder strings."""
        record = build_normalized_record(
            run_candidate_id="run_050",
            source_name="Test Source",
            source_type="STRUCTURED_API",
            ingestion_tier=1,
            source_url="https://example.com/api",
            job_url="https://example.com/job/1",
            raw_title="Designer",
            company_name="Acme",
            location_raw="Worldwide",
            salary_raw=None,
            posted_date=None,
            deadline_raw=None,
            is_snippet_only=False,
            is_discovery_only=False,
            field_provenance={
                "raw_title": "API_FIELD",
                "company_name": "API_FIELD",
                "job_url": "API_FIELD",
                "location_raw": "API_FIELD",
            }
        )

        self.assertIsNone(record["salary_raw"])
        self.assertIsNone(record["posted_date"])
        self.assertIsNone(record["deadline_raw"])
        self.assertNotIn("Hiring Company", str(record))
        self.assertNotIn("Seed/Series-A Startup", str(record))

    def test_valid_structured_feed_wwr_without_location(self):
        """Test building a We Work Remotely RSS record where location is genuinely unavailable
        in the feed. Must NOT assume 'Worldwide'; location_raw is None, provenance is NOT_PROVIDED,
        and status is PARTIALLY_EXTRACTED."""
        record = build_normalized_record(
            run_candidate_id="run_060",
            source_name="WWR",
            source_type="STRUCTURED_FEED",
            ingestion_tier=2,
            source_url="https://weworkremotely.com/categories/remote-design-jobs.rss",
            job_url="https://weworkremotely.com/jobs/123",
            raw_title="Junior Product Designer",
            company_name="Canva",
            location_raw=None,  # Location not provided in feed item
            is_snippet_only=False,
            is_discovery_only=False,
            field_provenance={
                "raw_title": "PARSED_TITLE_PREFIX",
                "company_name": "PARSED_TITLE_PREFIX",
                "job_url": "RSS_TAG",
            }
        )

        self.assertEqual(record["extraction_status"], "PARTIALLY_EXTRACTED")
        self.assertIn("location_raw", record["missing_fields"])
        self.assertEqual(record["field_provenance"]["location_raw"], "NOT_PROVIDED")
        self.assertEqual(record["field_provenance"]["raw_title"], "PARSED_TITLE_PREFIX")
        self.assertEqual(record["field_provenance"]["company_name"], "PARSED_TITLE_PREFIX")

    def test_valid_structured_feed_with_explicit_rss_location_tag(self):
        """Test building a structured RSS feed record where location is explicitly extracted
        from an authentic RSS tag (e.g. <region>Worldwide</region>)."""
        record = build_normalized_record(
            run_candidate_id="run_061",
            source_name="WWR",
            source_type="STRUCTURED_FEED",
            ingestion_tier=2,
            source_url="https://weworkremotely.com/categories/remote-design-jobs.rss",
            job_url="https://weworkremotely.com/jobs/124",
            raw_title="Junior Product Designer",
            company_name="Canva",
            location_raw="Worldwide",  # Genuine value from <region> RSS tag
            is_snippet_only=False,
            is_discovery_only=False,
            field_provenance={
                "raw_title": "PARSED_TITLE_PREFIX",
                "company_name": "PARSED_TITLE_PREFIX",
                "job_url": "RSS_TAG",
                "location_raw": "RSS_TAG",
            }
        )

        self.assertEqual(record["extraction_status"], "FULLY_EXTRACTED")
        self.assertEqual(record["field_provenance"]["location_raw"], "RSS_TAG")

if __name__ == "__main__":
    unittest.main()
