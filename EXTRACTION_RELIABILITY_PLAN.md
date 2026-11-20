# JobFather Data Extraction Reliability Audit & Implementation Plan (Step 3)

**Document Status:** DRAFT FOR APPROVAL (Step 3)  
**Governing Authority:** `CANDIDATE_PROFILE_SPEC.md` (Approved v1.1)  
**Core Objective:** Establish reliable, verifiable extraction of job data from all 8 ingestion pipelines, eliminate search snippet pollution, define source-quality tiers, and specify a strict normalized extraction contract before AI classification occurs.

---

## 1. Source-by-Source Extraction Audit

The current implementation in `jobfinder/jobfather.py` relies on 12 distinct extraction sub-pipelines grouped into 8 caller functions.

### Detailed Source Audit Matrix

| Pipeline Identifier | Source Name & Endpoint | Ingestion Mechanism | Responsible Function | Extracted Fields & Provenance | Failure & Missing Field Behavior | Current Vulnerabilities & Data Loss |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SRC-01** | **LinkedIn Direct Search**<br>`linkedin.com/jobs-guest/...` | HTTP GET (HTML fragment parsing) | `fetch_linkedin_jobs` | • `title`: `h3.base-search-card__title`<br>• `company`: `h4.base-search-card__subtitle`<br>• `link`: `a.base-card__full-link` (query params stripped) | Missing title or link skips item. Missing company defaults to `"Company not listed"`. Network failure catches `Exception`, logs notice, returns `[]`. | DOM selector drift can yield 0 jobs silently. Full description, location, and salary are not present in search card list endpoint. |
| **SRC-02** | **Remotive Design API**<br>`remotive.com/api/remote-jobs?category=design` | HTTP GET (JSON REST API) | `fetch_remotive_jobs` | • `title`: `item['title']`<br>• `company`: `item['company_name'] (item['candidate_required_location'])`<br>• `link`: `item['url']` | Missing fields default via `.get()`. Network failure logs notice, returns `[]`. | Merges location into company string (`"Company (Worldwide)"`). Does not extract publication date or experience level from JSON. |
| **SRC-03** | **We Work Remotely (WWR)**<br>`weworkremotely.com/.../remote-design-jobs.rss` | HTTP GET (XML ElementTree parsing) | `fetch_wwr_rss` | • `title`: `item.find('title')`<br>• `link`: `item.find('link')`<br>• `summary`: `item.find('description')[:150]` | Missing XML node defaults to empty string. Network failure logs notice, returns `[]`. | **Data Loss:** Company name is **hardcoded** to `"Remote Global Tech"` rather than extracted from the RSS item's `title` (which WWR formats as `Company: Title`). |
| **SRC-04** | **RemoteOK API**<br>`remoteok.com/api?tag=design` | HTTP GET (JSON REST API) | `fetch_remoteok_jobs` | • `title`: `item['position']`<br>• `company`: `item['company']`<br>• `link`: `item['url']` | Missing fields default via `.get()`. Slices `[1:15]` (index 0 is legal disclaimer). | Discards tags, location requirements, and date posted available in the JSON response. |
| **SRC-05a** | **Bdjobs Official JSON API**<br>`api.bdjobs.com/.../GetJobSearch` | HTTP GET (JSON REST API) | `fetch_bd_and_remote_portals` | • `title`: `item['jobTitle']`<br>• `company`: `item['companyName']`<br>• `deadline`: `item['deadline']`<br>• `link`: `bdjobs.com/h/details/{job_id}` | Missing fields default via `.get()`. Missing `Jobid` skips item. Network failure logs notice. | Highly reliable local metadata. Full job description requires secondary request to details page. |
| **SRC-05b** | **UI/UX Jobs Board Bangladesh**<br>`uiuxjobsboard.com/design-jobs/bangladesh` | HTTP GET (HTML link scraping) | `fetch_bd_and_remote_portals` | • `title`: `a[href*='/job/'].text`<br>• `link`: `href` | Link or title missing skips item. | **Data Loss:** Company name is **hardcoded** to `"UI/UX Jobs Board Employer"`. Does not parse company name from listing text. |
| **SRC-05c** | **Portal Aggregator Search Fallback**<br>DuckDuckGo HTML query | HTTP POST (HTML fragment scraping) | `fetch_bd_and_remote_portals` | • `title`: `snippet.text[:140]` (**Search Snippet**)<br>• `company`: `"Hiring Company"` (**Placeholder**)<br>• `link`: `link_tag['href']` | Missing link or snippet skips item. HTTP 200 required; network error logs notice. | **CRITICAL:** Search snippet text is assigned directly to `title`. Company is a generic placeholder. Incomplete search clue enters pipeline as a verified job. |
| **SRC-06a** | **Facebook Groups via Apify**<br>Apify Actor API | HTTP POST (JSON REST API) | `fetch_facebook_via_apify` | • `title`: `postText[:150]` (**Raw Post Text**)<br>• `company`: `groupTitle` (**Group Name**)<br>• `link`: `postUrl` | Missing text skips item. Actor failure catches `Exception`, triggers fallback. | **CRITICAL:** Unstructured social media post text (including questions, comments, or discussions) is assigned directly to `title`. Company is set to the Facebook group name. |
| **SRC-06b** | **Facebook Community Search Fallback**<br>DuckDuckGo HTML query | HTTP POST (HTML fragment scraping) | `fetch_facebook_via_apify` | • `title`: `snippet.text[:140]` (**Search Snippet**)<br>• `company`: `"Facebook Design Community"`<br>• `link`: `link_tag['href']` | Triggers only if Apify returns $<2$ posts. | **CRITICAL:** Snippet text is assigned to `title`. Post may be discussion, portfolio review request, or question rather than an active job. |
| **SRC-07a** | **Himalayas Startup API**<br>`himalayas.app/jobs/api?category=design` | HTTP GET (JSON REST API) | `fetch_wellfound_jobs` | • `title`: `item['title']`<br>• `company`: `item['companyName']`<br>• `link`: `item['applicationLink']` or `item['url']` | Missing fields default via `.get()`. | Highly reliable startup API. Location requirements and full description available in JSON are currently discarded. |
| **SRC-07b** | **Wellfound Search Fallback**<br>DuckDuckGo HTML query | HTTP POST (HTML fragment scraping) | `fetch_wellfound_jobs` | • `title`: `snippet.text[:140]` (**Search Snippet**)<br>• `company`: `"Seed/Series-A Startup"`<br>• `link`: `link_tag['href']` | Missing link skips item. | **CRITICAL:** Search snippet assigned to `title`. Company is a generic placeholder. |
| **SRC-08a** | **BD Tech Giants LinkedIn Search**<br>`linkedin.com/jobs-guest/...` | HTTP GET (HTML fragment parsing) | `fetch_complete_bd_companies` | • `title`: `h3.base-search-card__title`<br>• `company`: `h4.base-search-card__subtitle` or target company name<br>• `link`: `clean_url` | Missing title/link skips item. | Good local discovery for 12 major employers (bKash, Pathao, Therap, Brain Station 23, etc.). |
| **SRC-08b** | **BD Tech Directory Search Fallback**<br>DuckDuckGo HTML query | HTTP POST (HTML fragment scraping) | `fetch_complete_bd_companies` | • `title`: `snippet.text[:140]` (**Search Snippet**)<br>• `company`: `"Bangladesh Tech Employer"`<br>• `link`: `link_tag['href']` | Missing link skips item. | **CRITICAL:** Search snippet assigned to `title`. Company is a generic placeholder. |

---

## 2. Core Weaknesses in Current Data Flow

1. **Search Snippet Title Pollution:**  
   In 5 out of 12 pipelines (SRC-05c, SRC-06b, SRC-07b, SRC-08b), the text extracted from DuckDuckGo search snippets (e.g., *"Looking for an energetic individual who understands user personas and wireframes. Apply by sending resume..."*) is directly assigned to the `title` field.  
   *Result:* Gemini evaluates an unstructured sentence fragment as a job title.
2. **Generic Company Placeholders:**  
   Pipelines SRC-05c, SRC-07b, and SRC-08b assign hardcoded placeholder strings (`"Hiring Company"`, `"Seed/Series-A Startup"`, `"Bangladesh Tech Employer"`) when the company name cannot be parsed from the search result.  
   *Result:* Gemini cannot classify the hiring company's actual business domain and cannot evaluate company legitimacy.
3. **Facebook Post Text as Job Title:**  
   In SRC-06a and SRC-06b, raw post body text (up to 150 characters) is placed directly into `title`. Posts in design communities often include portfolio feedback requests, discussions, or general questions that mention keywords like "hiring" or "intern" in comments.
4. **Hardcoded Fallbacks Destroying Available Metadata:**  
   In SRC-03 (WWR RSS), the company name is hardcoded to `"Remote Global Tech"`, completely ignoring the fact that WWR feeds provide the real company name in the `<title>` tag before the colon (`Company: Job Title`).
5. **No Field Provenance or Status Flagging:**  
   Currently, a cleanly extracted official API record from Bdjobs is indistinguishable in the `combined_data` list from a raw search snippet from DuckDuckGo. Downstream AI filtering receives both as identical dictionaries.

---

## 3. Proposed Standardized Extraction Contract

To guarantee data integrity and eliminate hallucinations, every scraper must produce a normalized Python dictionary conforming to this strict contract:

```python
job_record = {
    # 1. Identifiers & Provenance
    "job_id": str,                  # Unique per-run ID: "job_001", "job_002"
    "source_name": str,            # "LinkedIn", "Bdjobs", "Remotive", "WWR", "RemoteOK", "Himalayas", "Apify-Facebook", "Web-Search"
    "source_type": str,            # "OFFICIAL_API" | "OFFICIAL_RSS" | "DIRECT_SCRAPE" | "SEARCH_DISCOVERY" | "COMMUNITY_POST"
    "source_quality_tier": int,    # Tier 1 (Highest) to Tier 5 (Discovery Clue)
    "source_url": str,             # URL of the search/endpoint where discovered
    "job_url": str,                # Canonical, cleaned application/details URL (mandatory)
    
    # 2. Extracted Job Metadata (Original Ground-Truth)
    "raw_title": str,              # Verbatim title from listing, or None if snippet-only
    "normalized_title": str,       # Cleaned title (stripped whitespace, boilerplate), or None
    "company_name": str,           # Verbatim company name, or None if unknown
    "location_raw": str or None,   # Raw location string (e.g. "Dhaka, Bangladesh", "Worldwide")
    "remote_type": str,            # "ON_SITE" | "HYBRID" | "REMOTE_WORLDWIDE" | "REMOTE_REGIONAL" | "UNKNOWN"
    "experience_raw": str or None, # Raw stated experience (e.g. "0-2 years", "Freshers encouraged")
    "employment_type": str,        # "FULL_TIME" | "INTERNSHIP" | "TRAINEE" | "CONTRACT" | "UNKNOWN"
    "salary_raw": str or None,     # Raw compensation string, or None
    "deadline_raw": str or None,   # Raw deadline date, or None
    "description_snippet": str,    # Clean text summary (max 300 chars)
    
    # 3. Extraction Health & Provenance Flags
    "extraction_status": str,      # "FULLY_EXTRACTED" | "PARTIALLY_EXTRACTED" | "DISCOVERY_ONLY"
    "is_snippet_only": bool,       # True if title/company could not be verified from listing
    "missing_fields": list,        # List of missing mandatory/expected fields: ["company_name", "experience_raw"]
    "field_provenance": dict       # Maps each field to its extraction method: {"title": "DOM_H3", "company": "API_FIELD"}
}
```

### Detailed Field Specification Table

| Field | Type | Mandatory? | Extraction Method | Missing / Unknown Representation |
| :--- | :--- | :--- | :--- | :--- |
| `job_id` | `str` | **Mandatory** | Generated sequentially at aggregation: `f"job_{idx:03d}"` | N/A (Always generated) |
| `source_name` | `str` | **Mandatory** | Static string per pipeline module | N/A |
| `source_type` | `str` | **Mandatory** | Assigned based on pipeline architecture | N/A |
| `source_quality_tier` | `int` | **Mandatory** | 1 (Official API) to 5 (Search Discovery) | N/A |
| `job_url` | `str` | **Mandatory** | Cleaned HTTP/HTTPS URL (tracking parameters stripped) | If missing/invalid, record is **dropped** |
| `raw_title` | `str` / `None` | Optional | Extracted from DOM title or API field | `None` (Never fill with search snippet) |
| `company_name` | `str` / `None` | Optional | Extracted from DOM subtitle or API field | `None` (Never fill with "Hiring Company") |
| `location_raw` | `str` / `None` | Optional | Extracted from location tag or API attribute | `None` |
| `remote_type` | `str` | **Mandatory** | Rule-based parser on location string | `"UNKNOWN"` |
| `experience_raw` | `str` / `None` | Optional | Extracted from JD text or API experience tag | `None` (Never assume 0 or 5 years) |
| `employment_type` | `str` | **Mandatory** | Keyword rule on title/JD (Intern, Trainee, Full-time) | `"UNKNOWN"` |
| `salary_raw` | `str` / `None` | Optional | Extracted compensation text | `None` |
| `deadline_raw` | `str` / `None` | Optional | Extracted deadline date string | `None` |
| `description_snippet` | `str` | Optional | First 300 chars of job description or snippet | `""` |
| `extraction_status` | `str` | **Mandatory** | Computed: `FULLY_EXTRACTED`, `PARTIALLY_EXTRACTED`, `DISCOVERY_ONLY` | N/A |
| `is_snippet_only` | `bool` | **Mandatory** | `True` if `raw_title` or `company_name` is `None` | N/A |
| `missing_fields` | `list` | **Mandatory** | List of fields that evaluated to `None` | `[]` if fully extracted |

---

## 4. Source-Quality Levels

Pipelines are classified into 5 architectural quality tiers:

| Tier | Quality Level | Sources | What It Reliably Establishes | What It Cannot Guarantee |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | **Structured Official API** | Remotive, Bdjobs API, RemoteOK, Himalayas | Verified job title, verified company name, canonical direct URL, structured deadline/location. | Does not guarantee that the job hasn't closed in the last 24 hours. |
| **Tier 2** | **Official RSS / XML Feed** | We Work Remotely (WWR) | Verified job URL, verified title, clean text description. | Company name requires parsing from title string (`Company: Title`). |
| **Tier 3** | **Direct Job-Page Extraction** | LinkedIn Guest API, UI/UX Jobs Board, BD Tech Giants LinkedIn | Verified job title, verified hiring company, canonical LinkedIn URL. | Full experience requirements and compensation are absent from the list endpoint. |
| **Tier 4** | **Social / Community Scraper** | Facebook Groups via Apify Actor | Real community post URL, author/group name, post body text. | Cannot guarantee that the post is an active hiring notice (could be a question or discussion). |
| **Tier 5** | **Search-Engine Discovery Result** | DuckDuckGo Portals, Wellfound, Facebook & BD Tech directory fallbacks | Canonical web link where target keywords were indexed. | **Cannot establish title or company.** Snippets are search result fragments, not structured job records. |

---

## 5. Strategy for Eliminating Search Snippet Title Pollution

### The Core Rule: "A Search Snippet is a Discovery Clue, Not a Job Record"

To eliminate hallucinated titles and placeholder companies without losing discovery clues, the pipeline must enforce this three-part rule:

1. **Title and Company Sanitization:**
   * When processing DuckDuckGo search results, the scraper **must never** assign `snippet.text` to `raw_title`.
   * The scraper **must never** assign `"Hiring Company"` or `"Seed/Series-A Startup"` to `company_name`.
   * For Tier 5 search results:
     ```python
     job_record["raw_title"] = None
     job_record["company_name"] = None
     job_record["description_snippet"] = snippet.text[:300]
     job_record["is_snippet_only"] = True
     job_record["extraction_status"] = "DISCOVERY_ONLY"
     job_record["missing_fields"] = ["raw_title", "company_name"]
     ```
2. **Facebook Post Text Sanitization:**
   * Apify post text must be stored in `description_snippet`, not `raw_title`.
   * If an explicit job title cannot be regex-extracted from the post (e.g. `r'(?i)hiring\s+(?:a\s+)?([A-Z][a-zA-Z/ ]+Designer)'`), set `raw_title = None`.
   * Set `is_snippet_only = True` and `extraction_status = "DISCOVERY_ONLY"`.
3. **Routing Incomplete Candidates Directly to Needs Review:**
   * Any candidate where `is_snippet_only is True` or `raw_title is None` **must never enter the primary digest as a Core Match**.
   * In compliance with `CANDIDATE_PROFILE_SPEC.md` Rule #11, all `DISCOVERY_ONLY` candidates are deterministically routed to `NEEDS_REVIEW` (persisted to `needs_review.json`).
   * Gemini is instructed to evaluate the snippet solely to determine if it is relevant to UX design; if relevant, it outputs `decision = "NEEDS_REVIEW"` with a clear rationale, preserving the URL for the user without faking a job title.

---

## 6. Extraction Failure & Health Reporting

Currently, when a scraper catches an error, it prints a message to stdout and returns `[]`. The telemetry table displays `⚪ Checked (0 new)`. This hides network failures and rate limits.

### Proposed Five-State Health Status for Scrapers:

```text
                                [Scraper Execution]
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 ▼                       ▼                       ▼
           [HTTP 200 OK]           [HTTP 4xx/5xx]          [Network Timeout/
                 │                  or Cloudflare              Exception]
        ┌────────┴────────┐              │                       │
        ▼                 ▼              ▼                       ▼
 [Records Parsed]   [Zero Records]  FAILED_HTTP_ERROR     FAILED_EXCEPTION
        │                 │        (e.g. 429 Rate Limit) (e.g. ConnectionReset)
        ▼                 ▼
SUCCESS_EXTRACTED   EMPTY_SUCCESS
```

* Every scraper function will return a tuple: `(jobs_list: list, status_report: dict)`.
* `status_report` structure:
  ```python
  {
      "source_name": "LinkedIn Direct",
      "status": "SUCCESS" | "EMPTY" | "FAILED_HTTP" | "FAILED_PARSE" | "FAILED_TIMEOUT",
      "http_code": 200,
      "items_discovered": 12,
      "items_fully_extracted": 10,
      "items_snippet_only": 2,
      "error_message": None
  }
  ```
* **Step Summary Telemetry Upgrade:** GitHub Actions step summary will report:
  * `🟢 Active (12 leads)`
  * `⚪ Checked (0 new leads)`
  * `🔴 Failed (HTTP 429 Too Many Requests)`
  * `⚠️ Partial (Failed to parse DOM selector)`

---

## 7. Source-Specific Improvement Plans (Without Adding New Sources)

### 1. LinkedIn Direct & BD Tech Employers (`fetch_linkedin_jobs` & `fetch_complete_bd_companies`)
* **Current Issue:** Location is not extracted; company defaults to generic string if subtitle tag changes.
* **Fix:**
  * Extract location from `span.job-search-card__location`.
  * If `h4.base-search-card__subtitle` is missing, try `a[data-tracking-control-name*='company']`.
  * Parse remote badge if `span.job-search-card__benefits` mentions "Remote".

### 2. We Work Remotely (`fetch_wwr_rss`)
* **Current Issue:** Company is hardcoded to `"Remote Global Tech"`.
* **Fix:**
  * WWR titles follow the exact format: `Company Name: Job Title`.
  * Parse using `title_raw.split(":", 1)`. Set `company_name = parts[0].strip()` and `raw_title = parts[1].strip()`.
  * Sets quality to **Tier 2 (Official Feed)** with 100% verified company and title.

### 3. UI/UX Jobs Board (`fetch_bd_and_remote_portals`)
* **Current Issue:** Company is hardcoded to `"UI/UX Jobs Board Employer"`.
* **Fix:**
  * Inspect listing card DOM: company name is contained in the sibling `span` or `p` tag beneath the `<a>` job title. Extract company from DOM text rather than hardcoding.

### 4. Search Query Fallbacks (DuckDuckGo in Portals, Wellfound, Facebook, and BD Tech)
* **Current Issue:** Snippet text is forced into the `title` field.
* **Fix:**
  * Explicitly flag all search query results with `is_snippet_only = True`, `raw_title = None`, and `company_name = None`.
  * Store snippet text in `description_snippet`.
  * Preserve link for manual verification via `needs_review.json`.

---

## 8. Proposed Extraction Test Plan (Mocked Test Suite)

To ensure extraction reliability before any LLM processing, the following 10 unit tests will be implemented in `tests/test_extraction.py`:

| Test ID | Target Component | Mocked Input Fixture | Expected Extraction Output Assertion |
| :--- | :--- | :--- | :--- |
| **TEST-EXT-01** | `fetch_remotive_jobs` | Valid Remotive JSON API response with 2 jobs | Both records extracted with `source_quality_tier=1`, clean URLs, and `extraction_status="FULLY_EXTRACTED"`. |
| **TEST-EXT-02** | `fetch_wwr_rss` | Valid WWR XML feed: `<title>Acme Inc: Junior Product Designer</title>` | Correctly splits company (`"Acme Inc"`) and title (`"Junior Product Designer"`). Asserts company is **not** `"Remote Global Tech"`. |
| **TEST-EXT-03** | `fetch_linkedin_jobs` | Mock LinkedIn HTML with title, company, and location spans | Asserts `raw_title`, `company_name`, and `location_raw` are populated cleanly without DOM tags. |
| **TEST-EXT-04** | `fetch_linkedin_jobs` | Malformed LinkedIn HTML (missing company subtitle `<h4>`) | Asserts `company_name=None`, `is_snippet_only=False`, and `"company_name" in missing_fields`. |
| **TEST-EXT-05** | DuckDuckGo Fallback | Search result body with snippet text and target URL | Asserts `raw_title=None`, `company_name=None`, `is_snippet_only=True`, and `extraction_status="DISCOVERY_ONLY"`. |
| **TEST-EXT-06** | `fetch_facebook_via_apify` | Apify dataset with raw user question post ("Does anyone know Figma?") | Asserts `raw_title=None`, `is_snippet_only=True`, and raw text stored in `description_snippet`. |
| **TEST-EXT-07** | `fetch_bd_and_remote_portals` | Bdjobs API response with valid `Jobid`, `jobTitle`, and `deadline` | Asserts canonical URL constructed (`bdjobs.com/h/details/{id}`) and `deadline_raw` preserved. |
| **TEST-EXT-08** | Any API Scraper | HTTP 429 Too Many Requests response | Asserts scraper returns `([], status_report)` where `status_report["status"] == "FAILED_HTTP"` and `http_code == 429`. |
| **TEST-EXT-09** | Any API Scraper | Empty JSON response (`{"jobs": []}`) | Asserts scraper returns `([], status_report)` where `status_report["status"] == "EMPTY"` and `http_code == 200`. |
| **TEST-EXT-10** | Any Scraper | Listing URL missing or malformed (e.g. `javascript:void(0)`) | Asserts record is rejected and not added to candidate list. |

---

## 9. Recommended Implementation Sequence for Step 3

When approved, Step 3 implementation should proceed in four isolated phases:

1. **Phase 3A (Data Contract):** Define `JobRecord` dictionary builder function with strict field typing and `is_snippet_only` flagging.
2. **Phase 3B (API & Feed Cleanup):** Update Tier 1 & 2 scrapers (Remotive, RemoteOK, Bdjobs, WWR RSS parser) to parse real company names and populate all available metadata.
3. **Phase 3C (Snippet Sanitization):** Refactor DuckDuckGo fallbacks to set `raw_title = None`, `company_name = None`, and `is_snippet_only = True`.
4. **Phase 3D (Extraction Unit Tests):** Implement `tests/test_extraction.py` covering all 10 mocked test fixtures and verify 100% pass rate.

---

## 10. Risks & Open Questions for User Approval

1. **Volume of "Needs Review" Leads:**
   * By properly marking search engine snippets as `is_snippet_only: true`, fewer jobs will qualify for the primary digest, and more will route to `needs_review.json`.  
   * *Assessment:* This strictly improves accuracy and eliminates garbage notifications, but total "Core Match" count may drop on days when direct APIs have low volume.
2. **Facebook Post Extraction Strategy:**
   * Apify retrieves raw text posts from Facebook groups. Some are real hiring posts; many are discussions.
   * *Proposed Rule:* If a post does not contain clear hiring intent keywords (`"hiring"`, `"looking for"`, `"intern"`, `"vacancy"`), it is dropped before reaching the candidate list.

---
*End of Data Extraction Reliability Audit & Implementation Plan (Step 3).*
