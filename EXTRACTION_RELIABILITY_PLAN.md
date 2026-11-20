# JobFather Data Extraction Reliability Audit & Implementation Plan (v1.1 - Refined)

**Document Status:** REVISED DRAFT FOR APPROVAL (Step 3.1)  
**Governing Authority:** `CANDIDATE_PROFILE_SPEC.md` (Approved v1.1)  
**Core Objective:** Establish reliable extraction across all 13 ingestion sub-pipelines, decouple search snippets from job titles, define strict field-level provenance, standardize scraper health reporting, and establish a normalized extraction contract.

---

## 1. Reconciled Source-by-Source Extraction Inventory

A complete audit of `jobfinder/jobfather.py` reveals exactly **13 extraction sub-pipelines** grouped under 8 caller functions.

### The 13 Sub-Pipelines at a Glance:
* **4 Structured APIs:** Remotive (SRC-02), RemoteOK (SRC-04), Bdjobs (SRC-05a), Himalayas (SRC-07a).
* **1 Structured RSS Feed:** We Work Remotely (SRC-03).
* **3 Direct Web Scrapers:** LinkedIn Direct (SRC-01), UI/UX Jobs Board (SRC-05b), BD Tech Giants LinkedIn (SRC-08a).
* **1 Social Community Scraper:** Facebook Groups via Apify (SRC-06a).
* **4 Search-Engine Discovery Fallbacks:** Portal DDG (SRC-05c), Facebook DDG (SRC-06b), Wellfound DDG (SRC-07b), BD Tech DDG (SRC-08b).

---

### Detailed Source Audit Matrix (All 13 Sub-Pipelines)

| Pipeline ID | Source Name & Endpoint | Ingestion Mechanism | Responsible Function | Extracted Fields & Provenance | Failure & Missing Field Behavior | Current Vulnerabilities & Data Loss |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SRC-01** | **LinkedIn Direct Search**<br>`linkedin.com/jobs-guest/...` | HTTP GET (HTML card fragment) | `fetch_linkedin_jobs` | • `title`: `h3.base-search-card__title`<br>• `company`: `h4.base-search-card__subtitle`<br>• `link`: `a.base-card__full-link` | Missing title or link skips item. Missing company defaults to `"Company not listed"`. Network error logs notice, returns `[]`. | DOM selector drift can yield 0 jobs silently. Full description, location, and experience absent from list card. |
| **SRC-02** | **Remotive Design API**<br>`remotive.com/api/remote-jobs` | HTTP GET (JSON REST API) | `fetch_remotive_jobs` | • `title`: `item['title']`<br>• `company`: `item['company_name']`<br>• `location`: `item['candidate_required_location']`<br>• `link`: `item['url']` | Missing fields default via `.get()`. Network error logs notice, returns `[]`. | Merges location into company string (`"Company (Worldwide)"`). Discards publication date and experience tags present in JSON. |
| **SRC-03** | **We Work Remotely (WWR)**<br>`weworkremotely.com/...rss` | HTTP GET (XML RSS Feed) | `fetch_wwr_rss` | • `title`: `item.find('title')`<br>• `link`: `item.find('link')`<br>• `summary`: `item.find('description')[:150]` | Missing XML node defaults to empty string. Network error logs notice, returns `[]`. | **Data Loss:** Hardcodes company name to `"Remote Global Tech"`, completely ignoring that WWR formats `<title>` as `Company Name: Job Title`. |
| **SRC-04** | **RemoteOK API**<br>`remoteok.com/api?tag=design` | HTTP GET (JSON REST API) | `fetch_remoteok_jobs` | • `title`: `item['position']`<br>• `company`: `item['company']`<br>• `link`: `item['url']` | Slices `[1:15]` (index 0 is legal disclaimer). Missing fields default via `.get()`. | Discards tags, location requirements, and date posted available in JSON. |
| **SRC-05a** | **Bdjobs Official API**<br>`api.bdjobs.com/...` | HTTP GET (JSON REST API) | `fetch_bd_and_remote_portals` | • `title`: `item['jobTitle']`<br>• `company`: `item['companyName']`<br>• `deadline`: `item['deadline']`<br>• `link`: `bdjobs.com/h/details/{id}` | Missing `Jobid` skips item. Network error logs notice. | Reliable local metadata. Detailed job description requires secondary request. |
| **SRC-05b** | **UI/UX Jobs Board BD**<br>`uiuxjobsboard.com/...` | HTTP GET (HTML scraping) | `fetch_bd_and_remote_portals` | • `title`: `a[href*='/job/'].text`<br>• `link`: `href` | Missing title/link skips item. | **Data Loss:** Company name is hardcoded to `"UI/UX Jobs Board Employer"`; does not parse company from card text. |
| **SRC-05c** | **Portals DDG Search Fallback**<br>DuckDuckGo HTML query | HTTP POST (HTML fragment) | `fetch_bd_and_remote_portals` | • `title`: `snippet.text[:140]`<br>• `company`: `"Hiring Company"`<br>• `link`: `link_tag['href']` | Missing link skips item. | **Search Snippet Pollution:** Search snippet sentence is assigned to `title`. Company is a generic placeholder. |
| **SRC-06a** | **Facebook Groups via Apify**<br>Apify Actor API | HTTP POST (JSON REST API) | `fetch_facebook_via_apify` | • `title`: `postText[:150]`<br>• `company`: `groupTitle`<br>• `link`: `postUrl` | Missing text skips item. Actor failure triggers fallback. | **Social Post Pollution:** Raw social post text (including discussions/questions) placed into `title`. Company set to group name. |
| **SRC-06b** | **Facebook DDG Fallback**<br>DuckDuckGo HTML query | HTTP POST (HTML fragment) | `fetch_facebook_via_apify` | • `title`: `snippet.text[:140]`<br>• `company`: `"Facebook Design Community"`<br>• `link`: `link_tag['href']` | Triggers if Apify returns $<2$ posts. | **Search Snippet Pollution:** Snippet text assigned to `title`. Post may be discussion rather than a job vacancy. |
| **SRC-07a** | **Himalayas Startup API**<br>`himalayas.app/jobs/api` | HTTP GET (JSON REST API) | `fetch_wellfound_jobs` | • `title`: `item['title']`<br>• `company`: `item['companyName']`<br>• `link`: `item['applicationLink']` | Missing fields default via `.get()`. | Reliable startup endpoint. Location restrictions available in JSON are currently discarded. |
| **SRC-07b** | **Wellfound DDG Fallback**<br>DuckDuckGo HTML query | HTTP POST (HTML fragment) | `fetch_wellfound_jobs` | • `title`: `snippet.text[:140]`<br>• `company`: `"Seed/Series-A Startup"`<br>• `link`: `link_tag['href']` | Missing link skips item. | **Search Snippet Pollution:** Search snippet assigned to `title`. Company is a generic placeholder. |
| **SRC-08a** | **BD Tech Giants LinkedIn**<br>`linkedin.com/jobs-guest/...` | HTTP GET (HTML fragment) | `fetch_complete_bd_companies` | • `title`: `h3.base-search-card__title`<br>• `company`: `h4.base-search-card__subtitle` or target company<br>• `link`: `clean_url` | Missing title/link skips item. | Good local discovery for 12 major employers (bKash, Pathao, Therap, Brain Station 23, etc.). |
| **SRC-08b** | **BD Tech DDG Fallback**<br>DuckDuckGo HTML query | HTTP POST (HTML fragment) | `fetch_complete_bd_companies` | • `title`: `snippet.text[:140]`<br>• `company`: `"Bangladesh Tech Employer"`<br>• `link`: `link_tag['href']` | Missing link skips item. | **Search Snippet Pollution:** Search snippet assigned to `title`. Company is a generic placeholder. |

---

## 2. Decoupling Extraction Completeness, Snippet Origin, and Field Failures

To eliminate architectural contradictions, the pipeline strictly decouples three independent concepts:

```text
[Record Origin]           [Field Completeness]           [Overall Status]
is_snippet_only: bool      missing_fields: list           extraction_status: str
───────────────────────   ────────────────────           ──────────────────────
Did this record come      Which specific fields          Can this record be fully
from a search snippet     could not be resolved          screened, partially evaluated,
or an actual listing?     (e.g. ['company_name'])        or is it discovery-only?
```

### Definitions:

1. **`is_snippet_only` (Boolean - Origin Flag):**
   * `True`: The candidate record originates **strictly from a search engine result snippet** (e.g. DuckDuckGo result) where the actual listing page has not been fetched or parsed.
   * `False`: The candidate record originates from a structured API, an RSS feed, or a direct job card/listing page.
   * *Critical Disambiguation:* A direct LinkedIn card that has a valid job title but fails to extract a company name has `is_snippet_only = False`. A missing company does *not* mean the title came from a search snippet.

2. **`missing_fields` (List of Strings - Audit Trail):**
   * Enumerates every individual attribute that could not be resolved from the source payload and was set to `None`.
   * Example: `["company_name", "salary_raw", "experience_raw"]`.

3. **`extraction_status` (Enum - Completeness State):**
   * `FULLY_EXTRACTED`: Essential fields (`raw_title`, `company_name`, `job_url`) are present and verified directly from the listing/API. Missing optional metadata (such as salary or deadline) does **not** downgrade a record from `FULLY_EXTRACTED`.
   * `PARTIALLY_EXTRACTED`: Originates from a direct job card or API, but an essential field (e.g. `company_name` or `location_raw`) could not be parsed.
   * `DISCOVERY_ONLY`: Originates from a search result snippet or unparsed social media post. The target listing itself has not been parsed.

---

## 3. Standardized Normalized Extraction Contract

Every ingestion pipeline will output records conforming to this Python contract:

```python
normalized_record = {
    # --- 1. Execution & Provenance Tracking ---
    "run_candidate_id": str,        # Ephemeral per-run token: "run_001", "run_002" (NOT a permanent vacancy ID)
    "source_name": str,             # "LinkedIn", "Bdjobs", "Remotive", "WWR", "RemoteOK", "Himalayas", "Apify-Facebook", "Web-Search"
    "source_type": str,             # "STRUCTURED_API" | "STRUCTURED_FEED" | "DIRECT_PAGE_SCRAPE" | "COMMUNITY_POST" | "SEARCH_SNIPPET"
    "ingestion_tier": int,          # Tier 1 (API) to Tier 5 (Search Discovery)
    "source_url": str,              # The exact URL or endpoint where the discovery occurred
    "job_url": str,                 # Canonical, resolved target URL (tracking parameters stripped)
    
    # --- 2. Ground-Truth Listing Metadata (Raw Extracted Values) ---
    "raw_title": str or None,       # Verbatim job title from listing, or None if snippet-only
    "company_name": str or None,    # Verbatim hiring company, or None if unverified (NEVER placeholder)
    "location_raw": str or None,    # Raw location string (e.g., "Dhaka, Bangladesh", "Worldwide")
    "remote_type": str,             # "ON_SITE" | "HYBRID" | "REMOTE_WORLDWIDE" | "REMOTE_REGIONAL" | "UNKNOWN"
    "experience_raw": str or None,  # Stated experience requirement (e.g. "0-2 years", "Freshers encouraged")
    "employment_type": str,         # "FULL_TIME" | "INTERNSHIP" | "TRAINEE" | "CONTRACT" | "UNKNOWN"
    "salary_raw": str or None,      # Stated compensation, or None
    "posted_date": str or None,     # Publication date string or ISO timestamp if available, or None
    "deadline_raw": str or None,    # Application deadline if available, or None
    
    # --- 3. Content Separation: Description vs. Search Snippet ---
    "description_excerpt": str,     # Real text excerpt from job description / API body (max 500 chars)
    "discovery_snippet": str,       # Search engine snippet or raw social text (max 300 chars)
    
    # --- 4. Quality & Audit Flags ---
    "is_snippet_only": bool,        # True if record comes strictly from a search engine result
    "extraction_status": str,       # "FULLY_EXTRACTED" | "PARTIALLY_EXTRACTED" | "DISCOVERY_ONLY"
    "missing_fields": list,         # List of fields that evaluated to None
    "field_provenance": dict        # Maps fields to source mechanism:
                                    # {"raw_title": "DOM_H3", "company_name": "API_FIELD", "job_url": "CANONICAL_LINK"}
}
```

### Purpose and Rule for Key Fields:
* `source_url` vs `job_url`: `source_url` records *where* the lead was discovered (e.g. `https://html.duckduckgo.com/html/` or Remotive API endpoint). `job_url` records the *actual destination vacancy* (e.g. `https://careers.company.com/job/123`). Search result URLs must never be described as verified job pages until resolved.
* `description_excerpt` vs `discovery_snippet`: Text extracted from an actual job page or API body belongs in `description_excerpt`. Search engine result snippets belong strictly in `discovery_snippet`.
* `raw_title` and `company_name`: If unverified, they are set to `None`. Placeholders such as `"Hiring Company"` or `"Seed/Series-A Startup"` are strictly prohibited.
* `run_candidate_id`: A temporary identifier (`run_001`, `run_002`) used to coordinate LLM input/output within a single execution. It is never treated as a persistent vacancy identifier.

---

## 4. Ingestion Tiers & Field-Level Provenance

Ingestion tiers describe the **transport mechanism**, not a blanket guarantee of field truth.

| Ingestion Tier | Transport Mechanism | Sources | Typical Field Reliability | What It CANNOT Guarantee |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | **Structured API** | Remotive, Bdjobs API, RemoteOK, Himalayas | High title, company, and URL stability. | Does not guarantee that the vacancy is currently active or that experience requirements are present in the list endpoint. |
| **Tier 2** | **Structured Feed** | We Work Remotely (WWR RSS) | Clean title and description. | Company name requires parsing from title string (`Company: Title`). |
| **Tier 3** | **Direct Page Scrape** | LinkedIn Guest API, UI/UX Jobs Board, BD Tech Giants | Real title and company card elements. | Experience, salary, and full description are typically absent from list cards. |
| **Tier 4** | **Social Community Scraper** | Facebook Groups via Apify Actor | Real community post text and author URL. | Cannot guarantee that the post is an active job announcement (could be a discussion or inquiry). |
| **Tier 5** | **Search Discovery Result** | DuckDuckGo fallbacks (Portals, Facebook, Wellfound, BD Tech) | Preserves candidate destination URL. | **Cannot establish title or company.** Snippets are search result fragments, not structured listings. |

### Field-Level Provenance Mapping:
Every extracted field records its exact extraction origin in `field_provenance`:
* `"API_FIELD"`: Directly deserialized from an API response key.
* `"RSS_TAG"`: Parsed from an XML element in an RSS/Atom feed.
* `"DOM_SELECTOR"`: Extracted from a specific HTML tag in a direct job card.
* `"PARSED_TITLE_PREFIX"`: Parsed from structured title text (e.g. WWR `Company: Title`).
* `"SEARCH_SNIPPET"`: Extracted from search engine snippet text.
* `"NOT_PROVIDED"`: Field was absent in payload and set to `None`.

---

## 5. Strategy for Eliminating Search Snippet & Social Post Pollution

### A. Search Engine Results (The 4 DuckDuckGo Fallbacks)
For pipelines SRC-05c, SRC-06b, SRC-07b, and SRC-08b:
1. `raw_title` **must be set to `None`**. Snippet text must never be truncated and assigned to `title`.
2. `company_name` **must be set to `None`**. Placeholders like `"Hiring Company"` are deleted.
3. `discovery_snippet` receives the search result text. `description_excerpt` is set to `""`.
4. `is_snippet_only` is set to `True`.
5. `extraction_status` is set to `"DISCOVERY_ONLY"`.
6. `missing_fields` records `["raw_title", "company_name"]`.

### B. Facebook Community Posts (Apify SRC-06a & DDG SRC-06b)
Facebook group posts are community interactions, not structured job boards. Relying on a single regex (e.g. `r'hiring.*Designer'`) misses researchers, interns, and design engineers, while falsely capturing questions like *"Are any agencies hiring junior designers right now?"*.
1. **Raw Post Storage:** The complete post text is stored in `discovery_snippet`.
2. **Explicit Title Resolution:** Set `raw_title = None` by default unless an unambiguous, standalone job header is present (e.g., lines starting with `Job Title:` or `Position:`).
3. **Company Name Resolution:** Set `company_name = None`. Group names (e.g., *"UX Bangladesh"*) must **never** be assigned as the hiring company.
4. **Candidate Classification:** All Facebook community leads are flagged as `source_type = "COMMUNITY_POST"`, `is_snippet_only = True`, and `extraction_status = "DISCOVERY_ONLY"`.
5. **Downstream Routing:** In compliance with `CANDIDATE_PROFILE_SPEC.md` Rule #11, all `DISCOVERY_ONLY` leads are routed to `NEEDS_REVIEW` (persisted in `needs_review.json`). They are never presented as verified Core Matches in the primary Telegram digest.

---

## 6. Standardized Scraper Health & Telemetry Reporting

HTTP 200 alone does not prove that extraction succeeded. A scraper receiving HTTP 200 may have encountered a Cloudflare challenge, an empty JSON payload, or broken DOM selectors.

### Standardized Scraper Health Status Vocabulary:

```python
health_status = {
    "SUCCESS_EXTRACTED": 0,    # HTTP 200, valid structure, >= 1 job extracted
    "EMPTY_SUCCESS": 0,        # HTTP 200, valid structure, verified 0 matching listings
    "FAILED_HTTP_ERROR": 0,    # HTTP 4xx/5xx (e.g. 429 rate limit, 403 forbidden)
    "FAILED_PARSE_ERROR": 0,   # HTTP 200, but payload unexpected, malformed, or challenge page
    "FAILED_TIMEOUT": 0,       # Network timeout or socket connection drop
    "FAILED_EXCEPTION": 0      # Unhandled Python runtime exception
}
```

Every scraper function returns a tuple: `(extracted_records: list, pipeline_status: dict)`.

```python
pipeline_status = {
    "source_name": "LinkedIn Direct",
    "status": "SUCCESS_EXTRACTED" | "EMPTY_SUCCESS" | "FAILED_HTTP_ERROR" | "FAILED_PARSE_ERROR" | "FAILED_TIMEOUT",
    "http_code": 200,
    "items_discovered": 15,
    "items_fully_extracted": 12,
    "items_partially_extracted": 3,
    "items_discovery_only": 0,
    "error_message": None
}
```

---

## 7. Source-Specific Implementation Plan

### 1. We Work Remotely (SRC-03)
* **Current Code:** `jobs.append({"company": "Remote Global Tech", "title": title, ...})`
* **Improvement:** WWR RSS titles are structured as `Company: Title`.  
  Parse via `parts = title.split(":", 1)`. If `len(parts) == 2`, set `company_name = parts[0].strip()` and `raw_title = parts[1].strip()`. Set `field_provenance["company_name"] = "PARSED_TITLE_PREFIX"`. Set `is_snippet_only = False`.

### 2. UI/UX Jobs Board Bangladesh (SRC-05b)
* **Current Code:** `jobs.append({"company": "UI/UX Jobs Board Employer", "title": title, ...})`
* **Improvement:** Parse company from card subtitle or set `company_name = None`. Never hardcode an artificial company name. Set `is_snippet_only = False` and `extraction_status = "PARTIALLY_EXTRACTED"` if company is missing.

### 3. Remotive & Himalayas (SRC-02 & SRC-07a)
* **Current Code:** Merges location into company name string.
* **Improvement:** Preserve `company_name` as clean string. Populate `location_raw = item.get("candidate_required_location")`. Extract `posted_date` and `salary_raw` if present in JSON.

### 4. DuckDuckGo Fallbacks (SRC-05c, SRC-06b, SRC-07b, SRC-08b)
* **Current Code:** `jobs.append({"title": snippet.text[:140], "company": "Hiring Company", ...})`
* **Improvement:** Set `raw_title = None`, `company_name = None`, `discovery_snippet = snippet.text[:300]`, `is_snippet_only = True`, `extraction_status = "DISCOVERY_ONLY"`.

---

## 8. Extraction Test Plan (Mocked Unit Tests)

These 10 unit tests will be implemented in `tests/test_extraction.py` using static mocked payloads:

| Test ID | Scenario | Mock Input Fixture | Assertions & Expected Output Contract |
| :--- | :--- | :--- | :--- |
| **TEST-EXT-01** | **WWR Title & Company Split** | RSS XML item with `<title>Canva: Junior Product Designer</title>` | `company_name == "Canva"`, `raw_title == "Junior Product Designer"`, `is_snippet_only == False`, `extraction_status == "FULLY_EXTRACTED"`. |
| **TEST-EXT-02** | **LinkedIn Missing Company** | LinkedIn HTML card with valid `<h3>` title but missing `<h4>` subtitle | `raw_title == "UI/UX Designer"`, `company_name == None`, `is_snippet_only == False`, `"company_name" in missing_fields`, `extraction_status == "PARTIALLY_EXTRACTED"`. |
| **TEST-EXT-03** | **LinkedIn Missing Title** | LinkedIn HTML card with valid `<h4>` company but empty/missing `<h3>` title | Record is rejected as invalid (cannot identify vacancy). `len(jobs) == 0`. |
| **TEST-EXT-04** | **DuckDuckGo Search Snippet** | HTML result body with snippet text and target URL | `raw_title == None`, `company_name == None`, `is_snippet_only == True`, `extraction_status == "DISCOVERY_ONLY"`, `discovery_snippet` contains text. |
| **TEST-EXT-05** | **Facebook Apify Discussion** | Apify post: *"Can anyone recommend a good Figma tutorial?"* | `raw_title == None`, `company_name == None`, `is_snippet_only == True`, `extraction_status == "DISCOVERY_ONLY"`. |
| **TEST-EXT-06** | **Facebook Hiring Post** | Apify post containing unstructured hiring text | `is_snippet_only == True`, `company_name == None`, text stored in `discovery_snippet`. |
| **TEST-EXT-07** | **Scraper HTTP 429 Error** | Mock requests.Session returning HTTP 429 | Returns `([], status)`. `status["status"] == "FAILED_HTTP_ERROR"`, `status["http_code"] == 429`. |
| **TEST-EXT-08** | **HTTP 200 Bot Challenge** | Mock HTTP 200 returning Cloudflare challenge HTML | Returns `([], status)`. `status["status"] == "FAILED_PARSE_ERROR"` (does not report `EMPTY_SUCCESS`). |
| **TEST-EXT-09** | **Missing Optional Fields** | Remotive API response with valid title, company, URL, but missing salary and deadline | `extraction_status == "FULLY_EXTRACTED"`, `salary_raw == None`, `deadline_raw == None`, missing optional fields do **not** downgrade status. |
| **TEST-EXT-10** | **Source URL vs. Job URL** | DuckDuckGo search result linking to external job URL | `source_url` starts with `https://html.duckduckgo.com`, `job_url` contains destination URL. |

---

## 9. Implementation Sequence for Step 3

Implementation will be executed in four disciplined, test-verified phases:

* **Phase 3A — Extraction Contract Builder:** Implement `build_normalized_record()` helper with strict field typing and validation.
* **Phase 3B — Structured API & RSS Feed Refinement:** Refactor Remotive, RemoteOK, Bdjobs, and WWR RSS parser to extract real company names and field provenance.
* **Phase 3C — Snippet & Social Sanitization:** Refactor the 4 DuckDuckGo fallbacks and Apify scraper to eliminate title pollution and set `is_snippet_only = True`.
* **Phase 3D — Extraction Test Suite:** Implement `tests/test_extraction.py` with all 10 mocked test fixtures and verify 100% pass rate.

---

## 10. Final Verification & Constraints Check

* **Zero code modifications:** `jobfinder/jobfather.py`, prompts, tests, and dependencies remain completely untouched.
* **Authority preserved:** `CANDIDATE_PROFILE_SPEC.md` remains the sole governing authority for classification decisions.

---
*End of Refined Extraction Reliability Plan (Step 3.1).*
