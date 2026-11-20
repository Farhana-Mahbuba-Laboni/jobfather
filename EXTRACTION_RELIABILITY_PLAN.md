# JobFather Data Extraction Reliability Audit & Implementation Plan (v1.3 - Step 3.3 Final)

**Document Status:** REVISED FINAL DRAFT FOR APPROVAL (Step 3.3)  
**Governing Authority:** `CANDIDATE_PROFILE_SPEC.md` (Approved v1.1)  
**Core Objective:** Establish reliable extraction across all 13 ingestion sub-pipelines, decouple search snippet origin from general discovery-only status, define strict `source_url` vs. `job_url` handling (allowing `job_url = None` for discovery leads), standardize scraper health reporting including `FAILED_EXCEPTION`, and establish a normalized extraction contract.

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

## 2. Decoupling Search Snippets, Discovery Leads, Missing Fields, and Status

To eliminate architectural contradictions, the pipeline strictly decouples four independent concepts:

```text
[Search Origin]           [Unparsed Lead]          [Field Completeness]      [Overall Status]
is_snippet_only: bool     is_discovery_only: bool  missing_fields: list      extraction_status: str
───────────────────────   ───────────────────────  ────────────────────      ──────────────────────
Did this record come      Has the actual vacancy   Which specific fields     Can this record be fully
strictly from a search    listing not been         evaluated to None         screened, partially
engine result snippet?    parsed yet?              (e.g. ['job_url'])        evaluated, or review-only?
```

### Precise Definitions & Interrelationships:

1. **`is_snippet_only` (Boolean - Search Snippet Origin Flag):**
   * `True`: The candidate record originates **strictly from a search engine result snippet** (the 4 DuckDuckGo fallbacks: SRC-05c, SRC-06b, SRC-07b, SRC-08b) where the actual listing page has not been fetched or parsed.
   * `False`: The candidate record originates from a structured API, an RSS feed, a direct job page scrape, or an Apify social media community post.
   * *Critical Rule:* An Apify social media community post (`SRC-06a`) has `is_snippet_only = False`. Facebook posts are direct community posts, not search engine result snippets. Conversely, the DuckDuckGo Facebook fallback (`SRC-06b`) has `is_snippet_only = True` because it is a search engine result snippet.

2. **`is_discovery_only` (Boolean - Unparsed Lead Flag):**
   * `True`: The candidate record represents an **unparsed discovery clue or lead** where the actual vacancy listing page has not been fetched or parsed (e.g. all 4 DuckDuckGo search snippets, Apify Facebook community posts).
   * `False`: The candidate record originates from a structured API, RSS feed, or direct job page scrape where structured vacancy listing metadata was parsed.
   * *Clarification on Direct Job Cards (SRC-01, SRC-05b, SRC-08a):*
     * A direct job card (such as a LinkedIn search result card or UI/UX Jobs Board card) **counts as parsed listing content** (`is_discovery_only = False`) because it is a verified, portal-rendered vacancy entity with explicit DOM selectors extracting the title, company, and canonical vacancy link.
     * **Important Limitation:** A job card provides list-level metadata (title, company, URL) and does **not** contain a full job description or detailed requirements. Therefore, `description_excerpt` remains empty or brief (`""`), and if key fields like `company_name` are missing from the card, the record is flagged as `extraction_status = "PARTIALLY_EXTRACTED"` (never `"DISCOVERY_ONLY"`).
   * *Matrix of Origins:*
     * **Direct Job Cards & Structured APIs/Feeds (SRC-01, 02, 03, 04, 05a, 05b, 07a, 08a):** `is_snippet_only = False`, `is_discovery_only = False`, `extraction_status = "FULLY_EXTRACTED"` or `"PARTIALLY_EXTRACTED"`.
     * **DuckDuckGo Search Snippets (SRC-05c, SRC-06b, SRC-07b, SRC-08b):** `is_snippet_only = True`, `is_discovery_only = True`, `extraction_status = "DISCOVERY_ONLY"`.
     * **Facebook Community Posts via Apify (SRC-06a):** `is_snippet_only = False`, `is_discovery_only = True`, `extraction_status = "DISCOVERY_ONLY"`.

3. **`missing_fields` (List of Strings - Audit Trail):**
   * Enumerates every individual attribute that could not be resolved from the source payload and evaluated to `None`.
   * Example: `["company_name", "job_url", "salary_raw"]`.

4. **`extraction_status` (Enum - Completeness State):**
   * `FULLY_EXTRACTED`: Essential fields (`raw_title`, `company_name`, `job_url`) are present and verified directly from the listing/API. Missing optional metadata (such as salary or deadline) does **not** downgrade a record from `FULLY_EXTRACTED`.
   * `PARTIALLY_EXTRACTED`: Originates from a direct job card or API, but an essential field (e.g. `company_name` or `location_raw`) could not be parsed.
   * `DISCOVERY_ONLY`: Originates from an unparsed discovery lead (`is_discovery_only = True`), such as any search engine snippet or an Apify community post.

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
    "source_url": str,              # Mandatory: The exact URL/permalink where the lead was observed (e.g. search URL or FB post permalink)
    "job_url": str or None,         # Canonical destination URL of actual vacancy, or None if no external link exists
    
    # --- 2. Ground-Truth Listing Metadata (Raw Extracted Values) ---
    "raw_title": str or None,       # Verbatim job title from listing, or None if discovery-only
    "company_name": str or None,    # Verbatim hiring company, or None if unverified (NEVER placeholder)
    "location_raw": str or None,    # Raw location string (e.g., "Dhaka, Bangladesh", "Worldwide")
    "remote_type": str,             # "ON_SITE" | "HYBRID" | "REMOTE_WORLDWIDE" | "REMOTE_REGIONAL" | "UNKNOWN"
    "experience_raw": str or None,  # Stated experience requirement (e.g. "0-2 years", "Freshers encouraged")
    "employment_type": str,         # "FULL_TIME" | "INTERNSHIP" | "TRAINEE" | "CONTRACT" | "UNKNOWN"
    "salary_raw": str or None,      # Stated compensation, or None
    "posted_date": str or None,     # Publication date string or ISO timestamp if available, or None
    "deadline_raw": str or None,    # Application deadline if available, or None
    
    # --- 3. Content Separation: Description vs. Discovery Clue ---
    "description_excerpt": str,     # Real text excerpt from parsed job description / API body (max 500 chars)
    "discovery_snippet": str,       # Search engine snippet or raw social post text (max 500 chars)
    
    # --- 4. Quality & Audit Flags ---
    "is_snippet_only": bool,        # True ONLY if record originates strictly from a search engine result
    "is_discovery_only": bool,      # True if record is an unparsed clue (search snippet or community post)
    "extraction_status": str,       # "FULLY_EXTRACTED" | "PARTIALLY_EXTRACTED" | "DISCOVERY_ONLY"
    "missing_fields": list,         # List of fields that evaluated to None (e.g. ['job_url', 'company_name'])
    "field_provenance": dict        # Maps fields to source mechanism:
                                    # {"raw_title": "DOM_H3", "company_name": "API_FIELD", "job_url": "CANONICAL_LINK"}
}
```

### Purpose and Rules for Core Fields:

* **`source_url` vs `job_url`:**
  * `source_url` is **mandatory** and preserves the exact origin where JobFather encountered the lead (e.g. `https://html.duckduckgo.com/html/` or a Facebook post permalink `https://facebook.com/groups/.../posts/12345`).
  * `job_url` represents the canonical external destination of the actual vacancy listing.
  * **Allowing `job_url = None`:** When a vacancy has an external application link, `job_url` is populated with that destination. However, for discovery leads (especially Facebook community posts where hiring discussions or instructions happen natively without an external website), an external vacancy URL may not exist. In these cases:
    * `job_url` is set to `None`.
    * `"job_url"` is appended to `missing_fields`.
    * **The discovery lead is NOT discarded.** It is preserved with its `source_url` and routed downstream to `NEEDS_REVIEW`.
  * Under no circumstances may `source_url` (such as a Facebook post permalink) be falsely asserted as a verified `job_url`.
* **`description_excerpt` vs `discovery_snippet`:**
  * `description_excerpt`: Text extracted from an actual parsed job description or API body. Direct job cards that lack a body text set `description_excerpt = ""`.
  * `discovery_snippet`: Search engine snippet text or raw social media post text.
* **`raw_title` and `company_name`:** If unverified or missing from the listing, set to `None`. Artificial placeholders (`"Hiring Company"`, `"Seed/Series-A Startup"`) are strictly prohibited.
* **`run_candidate_id`:** Ephemeral identifier (`run_001`, `run_002`) used to coordinate LLM input/output within a single execution. It is never treated as a persistent vacancy identifier.

---

## 4. Ingestion Tiers & Field-Level Provenance

Ingestion tiers describe the **transport mechanism**, not a blanket guarantee of field truth.

| Ingestion Tier | Transport Mechanism | Sources | Typical Field Reliability | What It CANNOT Guarantee |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1** | **Structured API** | Remotive, Bdjobs API, RemoteOK, Himalayas | High title, company, and URL stability. | Does not guarantee that the vacancy is currently active or that experience requirements are present in the list endpoint. |
| **Tier 2** | **Structured Feed** | We Work Remotely (WWR RSS) | Clean title and description. | Company name requires parsing from title string (`Company: Title`). |
| **Tier 3** | **Direct Page Scrape** | LinkedIn Guest API, UI/UX Jobs Board, BD Tech Giants | Real title and company card elements. | Experience, salary, and full description are typically absent from list cards. |
| **Tier 4** | **Social Community Scraper** | Facebook Groups via Apify Actor (SRC-06a) | Real community post text and author/post URL. | Cannot guarantee post is a job vacancy (may be question/discussion); often lacks external `job_url`. |
| **Tier 5** | **Search Discovery Result** | DuckDuckGo fallbacks (SRC-05c, SRC-06b, SRC-07b, SRC-08b) | Preserves candidate destination URL. | **Cannot establish title or company.** Snippets are search fragments, not structured listings. |

### Field-Level Provenance Mapping:
Every extracted field records its exact extraction origin in `field_provenance`:
* `"API_FIELD"`: Directly deserialized from an API response key.
* `"RSS_TAG"`: Parsed from an XML element in an RSS/Atom feed.
* `"DOM_SELECTOR"`: Extracted from a specific HTML tag in a direct job card.
* `"PARSED_TITLE_PREFIX"`: Parsed from structured title text (e.g. WWR `Company: Title`).
* `"COMMUNITY_POST"`: Extracted from social media community post text/metadata.
* `"SEARCH_SNIPPET"`: Extracted from search engine snippet text.
* `"NOT_PROVIDED"`: Field was absent in payload and set to `None`.

---

## 5. Strategy for Eliminating Search Snippet & Social Post Pollution

### A. Search Engine Results (The 4 DuckDuckGo Fallbacks: SRC-05c, SRC-06b, SRC-07b, SRC-08b)
All four search engine fallbacks—including the Facebook DuckDuckGo fallback (`SRC-06b`)—adhere to uniform search result rules:
1. `raw_title` **must be set to `None`**. Snippet text must never be assigned to `title`.
2. `company_name` **must be set to `None`**. Placeholders like `"Hiring Company"` or `"Facebook Design Community"` are deleted.
3. `discovery_snippet` receives the search result text. `description_excerpt` is set to `""`.
4. Quality flags: `is_snippet_only = True`, `is_discovery_only = True`.
5. Status: `extraction_status = "DISCOVERY_ONLY"`.
6. Missing fields: `missing_fields` records `["raw_title", "company_name"]` (and `"job_url"` if the external link could not be parsed).

### B. Facebook Community Posts via Apify (SRC-06a Only)
Facebook group posts retrieved directly from the Apify Actor are community interactions, not search snippets or structured job boards.
1. **Raw Post Storage:** The complete post text is stored in `discovery_snippet`.
2. **Explicit Title Resolution:** Set `raw_title = None` by default unless an unambiguous standalone job header is present (e.g. lines starting with `Job Title:` or `Position:`).
3. **Company Name Resolution:** Set `company_name = None`. Group names (e.g. *"UX Bangladesh"*) must **never** be assigned as the hiring company.
4. **URL Separation & Handling:**
   * `source_url`: Set to the Facebook post permalink.
   * `job_url`: Extracted external application link if explicitly mentioned in post body, or `None` if no external link exists.
   * If `job_url is None`, `"job_url"` is appended to `missing_fields`. **The post is NOT discarded.**
5. **Quality Flags:**
   * `source_type = "COMMUNITY_POST"`.
   * `is_snippet_only = False` (Facebook posts from Apify are direct community posts, NOT search engine snippets).
   * `is_discovery_only = True` (The actual vacancy listing has not been parsed).
   * `extraction_status = "DISCOVERY_ONLY"`.
6. **Downstream Routing:** In compliance with `CANDIDATE_PROFILE_SPEC.md` Rule #11, all `DISCOVERY_ONLY` leads are routed to `NEEDS_REVIEW` (persisted in `needs_review.json`). They are never presented as verified Core Matches in the primary Telegram digest.

---

## 6. Standardized Scraper Health & Telemetry Reporting

HTTP 200 alone does not prove that extraction succeeded. A scraper receiving HTTP 200 may have encountered a Cloudflare challenge, an empty JSON payload, or broken DOM selectors.

### Standardized Scraper Health Status Vocabulary:

```python
health_status = {
    "SUCCESS_EXTRACTED": 0,    # HTTP 200, valid structure, >= 1 job extracted
    "EMPTY_SUCCESS": 0,        # HTTP 200, valid structure, verified 0 matching listings
    "FAILED_HTTP_ERROR": 0,    # Upstream server responded with HTTP 4xx or 5xx status code
    "FAILED_PARSE_ERROR": 0,   # Upstream responded HTTP 200, but payload corrupt, malformed, or challenge page
    "FAILED_TIMEOUT": 0,       # Network timeout or socket connection drop
    "FAILED_EXCEPTION": 0      # Unexpected Python runtime exception raised during execution
}
```

### Definitions of Failure Categories:
* **`FAILED_HTTP_ERROR`:** Upstream server returned an HTTP status outside 200–299 (e.g. HTTP 403 Forbidden, 429 Rate Limit, 500/502/503 Server Error).
* **`FAILED_PARSE_ERROR`:** Upstream returned HTTP 200, but the payload could not be parsed as expected (e.g. non-JSON payload from a JSON API, Cloudflare anti-bot HTML challenge, or empty/corrupt HTML DOM structure).
* **`FAILED_TIMEOUT`:** Explicit network timeout or socket connection drop during request (`requests.exceptions.Timeout`, `requests.exceptions.ConnectTimeout`).
* **`FAILED_EXCEPTION`:** Any unhandled Python runtime exception raised during pipeline execution not caught by network or parse handlers (e.g. `KeyError`, `IndexError`, `AttributeError`, `TypeError`, unhandled third-party library error).

### Standardized Return Structure:
Every scraper function returns a tuple: `(extracted_records: list, pipeline_status: dict)`.

```python
pipeline_status = {
    "source_name": "LinkedIn Direct",
    "status": "SUCCESS_EXTRACTED" | "EMPTY_SUCCESS" | "FAILED_HTTP_ERROR" | "FAILED_PARSE_ERROR" | "FAILED_TIMEOUT" | "FAILED_EXCEPTION",
    "http_code": 200,  # or None if failure occurred before receiving an HTTP response
    "items_discovered": 15,
    "items_fully_extracted": 12,
    "items_partially_extracted": 3,
    "items_discovery_only": 0,
    "error_message": None  # String summary if status is any FAILED_*
}
```

---

## 7. Source-Specific Implementation Plan

### 1. We Work Remotely (SRC-03)
* **Current Code:** `jobs.append({"company": "Remote Global Tech", "title": title, ...})`
* **Improvement:** WWR RSS titles are structured as `Company: Title`.  
  Parse via `parts = title.split(":", 1)`. If `len(parts) == 2`, set `company_name = parts[0].strip()` and `raw_title = parts[1].strip()`. Set `field_provenance["company_name"] = "PARSED_TITLE_PREFIX"`. Set `is_snippet_only = False` and `is_discovery_only = False`.

### 2. UI/UX Jobs Board Bangladesh (SRC-05b)
* **Current Code:** `jobs.append({"company": "UI/UX Jobs Board Employer", "title": title, ...})`
* **Improvement:** Parse company from card subtitle or set `company_name = None`. Never hardcode an artificial company name. Set `is_snippet_only = False`, `is_discovery_only = False`, and `extraction_status = "PARTIALLY_EXTRACTED"` if company is missing.

### 3. Remotive & Himalayas (SRC-02 & SRC-07a)
* **Current Code:** Merges location into company name string.
* **Improvement:** Preserve `company_name` as clean string. Populate `location_raw = item.get("candidate_required_location")`. Extract `posted_date` and `salary_raw` if present in JSON. Set `is_snippet_only = False` and `is_discovery_only = False`.

### 4. DuckDuckGo Fallbacks (SRC-05c, SRC-06b, SRC-07b, SRC-08b)
* **Current Code:** `jobs.append({"title": snippet.text[:140], "company": "Hiring Company" / "Facebook Design Community", ...})`
* **Improvement:** All four DDG fallbacks (including `SRC-06b`) set `raw_title = None`, `company_name = None`, `discovery_snippet = snippet.text[:300]`, `is_snippet_only = True`, `is_discovery_only = True`, `extraction_status = "DISCOVERY_ONLY"`.

### 5. Facebook Groups via Apify (SRC-06a)
* **Current Code:** Assigns `title = postText[:150]` and `company = groupTitle`.
* **Improvement:** Set `raw_title = None`, `company_name = None`, `discovery_snippet = postText[:500]`, `source_url = postUrl`, `job_url = extracted_url or None`. Set `is_snippet_only = False`, `is_discovery_only = True`, `extraction_status = "DISCOVERY_ONLY"`. If `job_url is None`, append `"job_url"` to `missing_fields` and retain the record.

---

## 8. Extraction Test Plan (Mocked Unit Tests)

These 10 unit tests will be implemented in `tests/test_extraction.py` using static mocked payloads:

| Test ID | Scenario | Mock Input Fixture | Assertions & Expected Output Contract |
| :--- | :--- | :--- | :--- |
| **TEST-EXT-01** | **WWR Title & Company Split (SRC-03)** | RSS XML item with `<title>Canva: Junior Product Designer</title>` | `company_name == "Canva"`, `raw_title == "Junior Product Designer"`, `is_snippet_only == False`, `is_discovery_only == False`, `extraction_status == "FULLY_EXTRACTED"`. |
| **TEST-EXT-02** | **LinkedIn Missing Company (SRC-01)** | LinkedIn HTML card with valid `<h3>` title but missing `<h4>` subtitle | `raw_title == "UI/UX Designer"`, `company_name == None`, `is_snippet_only == False`, `is_discovery_only == False`, `"company_name" in missing_fields`, `extraction_status == "PARTIALLY_EXTRACTED"`. |
| **TEST-EXT-03** | **LinkedIn Missing Title (SRC-01)** | LinkedIn HTML card with valid `<h4>` company but empty/missing `<h3>` title | Record is rejected as invalid (cannot identify vacancy). `len(jobs) == 0`. |
| **TEST-EXT-04** | **DuckDuckGo Search Snippet (SRC-05c / SRC-07b)** | HTML result body with snippet text and target URL | `raw_title == None`, `company_name == None`, `is_snippet_only == True`, `is_discovery_only == True`, `extraction_status == "DISCOVERY_ONLY"`, `discovery_snippet` contains text. |
| **TEST-EXT-05** | **Facebook Apify Community Post (SRC-06a - No External Link)** | Apify post: *"We are looking for a Junior UI Designer. Send CV to our page inbox."* with post URL | `raw_title == None`, `company_name == None`, `job_url == None`, `source_url == postUrl`, `is_snippet_only == False`, `is_discovery_only == True`, `extraction_status == "DISCOVERY_ONLY"`, `"job_url" in missing_fields`. Record is preserved (not dropped). |
| **TEST-EXT-06** | **Facebook Apify Post (SRC-06a - With External Link)** | Apify post containing hiring text and an external application URL | `raw_title == None`, `company_name == None`, `is_snippet_only == False`, `is_discovery_only == True`, `source_url == postUrl`, `job_url == "https://careers.example.com"`, text in `discovery_snippet`. |
| **TEST-EXT-07** | **Scraper HTTP 429 Error** | Mock requests.Session returning HTTP 429 | Returns `([], status)`. `status["status"] == "FAILED_HTTP_ERROR"`, `status["http_code"] == 429`. |
| **TEST-EXT-08** | **HTTP 200 Bot Challenge** | Mock HTTP 200 returning Cloudflare challenge HTML | Returns `([], status)`. `status["status"] == "FAILED_PARSE_ERROR"` (does not report `EMPTY_SUCCESS`). |
| **TEST-EXT-09** | **Missing Optional Fields** | Remotive API response with valid title, company, URL, but missing salary and deadline | `extraction_status == "FULLY_EXTRACTED"`, `salary_raw == None`, `deadline_raw == None`, missing optional fields do **not** downgrade status. |
| **TEST-EXT-10** | **DuckDuckGo Facebook Fallback (SRC-06b - Search vs Post)** | DuckDuckGo search result linking to a Facebook group post URL | `source_url` starts with `https://html.duckduckgo.com`, `job_url` contains destination Facebook URL, `is_snippet_only == True`, `is_discovery_only == True`, `extraction_status == "DISCOVERY_ONLY"`. |

---

## 9. Implementation Sequence for Step 3

Implementation will be executed in four disciplined, test-verified phases:

* **Phase 3A — Extraction Contract Builder:** Implement `build_normalized_record()` helper with strict field typing and validation.
* **Phase 3B — Structured API & RSS Feed Refinement:** Refactor Remotive, RemoteOK, Bdjobs, and WWR RSS parser to extract real company names and field provenance.
* **Phase 3C — Snippet & Social Sanitization:** Refactor the 4 DuckDuckGo fallbacks (including `SRC-06b`) and Apify scraper (`SRC-06a`) to eliminate title pollution, handle `job_url = None` for community leads, and set accurate `is_snippet_only` and `is_discovery_only` flags.
* **Phase 3D — Extraction Test Suite:** Implement `tests/test_extraction.py` with all 10 mocked test fixtures and verify 100% pass rate.

---

## 10. Final Verification & Constraints Check

* **Zero code modifications:** `jobfinder/jobfather.py`, prompts, tests, and dependencies remain completely untouched.
* **Authority preserved:** `CANDIDATE_PROFILE_SPEC.md` remains the sole governing authority for classification decisions.

---
*End of Refined Extraction Reliability Plan (v1.3 - Step 3.3 Final).*
