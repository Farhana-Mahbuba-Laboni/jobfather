# JobFather Candidate Profile Specification (v1.1)

**Document Status:** DRAFT FOR APPROVAL (Step 2)  
**Target Candidate Background:** B.Sc. in Computer Science & Engineering (CSE) graduate transitioning into Product Design / UX Engineering.  
**Core Objective:** Deterministically identify, classify, and filter entry-level and junior digital product design opportunities while completely eliminating senior bloat, marketing graphic design, and geographically ineligible postings.

---

## 1. Candidate Persona & Target Profile

* **Primary Career Goal:** Junior / Entry-Level Product Designer or UI/UX Designer.
* **Secondary / Strategic Advantage:** Roles that benefit from a CSE technical foundation (Design Systems, Design Engineering, UX Research, interactive prototypes, and developer handoff).
* **Target Seniority:** 0–2 years of professional experience, Internships, Trainee programs, Associate roles, or Fresh Graduate tracks.
* **Target Market:** Bangladesh (On-site / Hybrid in Dhaka or Chittagong) OR Worldwide Remote open to applicants residing in Bangladesh.

---

## 2. Taxonomy & Digest Categorization

Opportunities are partitioned into four discrete deterministic categories:

```text
                                  [Scraped Circular]
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
         [Meets Exclusions?]                             [Valid Geography?]
          (Senior 3+ yrs,                                  (Bangladesh or
          Flyers/Graphics,                                Worldwide Remote)
          Unpaid/Scam)                                            │
                  │                                               ▼
             YES ─┴─► EXCLUDED                           [Discipline Match]
                                                                  │
                           ┌──────────────────────────────────────┼──────────────────────────────────────┐
                           ▼                                      ▼                                      ▼
                   [Core UX/Product]                     [Technical Adjacent]                   [Ambiguous / Partial]
                     (UI, UX, Prod,                        (Design Engineer,                     (Broad ranges 1-3y,
                      Interaction)                         Systems, Research)                    snippets, unclear geo)
                           │                                      │                                      │
                           ▼                                      ▼                                      ▼
                     CORE MATCHES                        RELATED OPPORTUNITIES                       NEEDS REVIEW
                   (Primary Digest)                        (Separate Section)                     (Manual Verification)
```

### Category 1: Core Matches (Primary Digest Section)
Directly targets day-to-day user experience, product workflows, user interfaces, wireframing, and interactive product design.
* **Accepted Titles / Synonyms:**
  * `UI/UX Designer`, `UX/UI Designer`, `User Experience Designer`
  * `Product Designer`, `Associate Product Designer`, `Junior Product Designer`
  * `UI Designer`, `User Interface Designer`
  * `Interaction Designer`, `IxD Designer`
  * `Experience Designer`, `Digital Product Designer`
* **Core Responsibilities Required:** User flows, information architecture, wireframing, low/high-fidelity prototyping, usable web/mobile interface design, user testing, and developer handoff.

### Category 2: Related Opportunities (Separated Digest Section)
High-value adjacencies where a B.Sc. in Computer Science & Engineering provides an immediate competitive advantage over non-technical design candidates. Delivered in a separate section to keep the primary digest pristine.
* **Accepted Titles / Synonyms:**
  * `Design Engineer`, `UX Engineer`, `UI Engineer` (Focus: Bridging Figma and frontend code, interactive components, CSS/React/Flutter UI implementation)
  * `Design System Specialist`, `Design Systems Designer` (Focus: Tokenization, reusable Figma component libraries, multi-brand UI consistency)
  * `UX Researcher`, `Junior UX Researcher` (Focus: Usability benchmarking, user interviews, qualitative & quantitative product analytics)
* **Rule:** A job does not qualify as Related merely because it mentions "Figma" or "Research." Its core day-to-day responsibilities must center on these disciplines.

### Category 3: Needs Review / Insufficient Information (Audit Section)
Postings that exhibit positive intent but lack verifiable attributes (e.g. search snippet fallbacks, unverified remote restrictions, or borderline 1–3 year ranges). Held in an unconfirmed section rather than guessing or silently discarding.

### Category 4: Excluded (Suppressed / Filtered)
Instantly disqualified from notification digests.

---

## 3. Strict Exclusion Rules

A candidate opportunity is **instantly rejected** if it triggers any of the following rules:

1. **Seniority & Experience Ceiling:**
   * Contains explicit seniority keywords in title: `Senior`, `Sr.`, `Lead`, `Principal`, `Staff`, `Director`, `Head of`, `Manager`, `VP`, `Architect`.
   * Explicitly demands **3 or more years** of mandatory professional experience (e.g., "Minimum 3 years", "3-5 years required", "4+ years").
2. **Marketing & Graphic Design Floor:**
   * Roles centered on marketing collateral, social media banners, promotional flyers, packaging, print graphics, billboards, brochures, or video editing.
   * *The "Figma Trap" Rule:* Job circulars titled "UI/UX Designer" whose bullet points demand daily Facebook post designs, Photoshop banner creation, and printing press coordination without web/app UX workflows.
3. **Geographic Ineligibility:**
   * On-site or hybrid roles located outside Bangladesh (e.g., on-site in Berlin, Bangalore, London, New York).
   * Remote roles with explicit geo-fences that exclude South Asia / Bangladesh (e.g., *"US Citizens Only"*, *"Must reside in EU/UK"*, *"Remote - North America Timezones only"*, *"Requires US Work Authorization without sponsorship"*).
4. **Compensation & Legitimacy Exclusions:**
   * Explicitly uncompensated internships (unpaid work), except recognized academic credit programs from verified institutions.
   * Commission-only roles, multi-level marketing, or postings requiring upfront candidate payments.

---

## 4. Location & Remote Eligibility Rules

| Job Location Signal | Evaluation Logic | Result |
| :--- | :--- | :--- |
| **Dhaka, Chittagong, Bangladesh (On-site / Hybrid)** | Verified local employer or subsidiary. | **Eligible** |
| **"Worldwide", "Anywhere", "Global Remote"** | Open international remote listing with no regional bans. | **Eligible** |
| **"Remote - APAC / South Asia / India & BD"** | Explicitly includes candidate's timezone/region. | **Eligible** |
| **"Remote (US / Europe / LatAm Only)"** | Explicit geo-fence excluding Bangladesh. | **Excluded** |
| **"Remote" (No country specified, US company)** | Candidate eligibility ambiguous. | **Needs Review** (Do not assume eligible or ineligible) |
| **Physical location outside BD without "Remote"** | Physical on-site abroad. | **Excluded** |

---

## 5. Classification & Ambiguity Decision Rules

| Ambiguity Scenario | Handling Policy | Assigned Status |
| :--- | :--- | :--- |
| **Broad experience range (e.g. "1–3 years")** | If the lower bound is $\le 2$ years, welcoming candidates with 1 year, do not reject. | **Core Match** (if UI/UX) or **Needs Review** |
| **Missing experience requirements** | If the title is unranked (e.g. "Product Designer") and description does not state years, do not guess 5 years. | **Core Match** (Flag experience as "Not specified") |
| **Conflicting signals: "Junior Lead" or "Junior ... 5 years"** | Experience requirement trumps title. A job demanding 5 years is senior regardless of "Junior" in title. | **Excluded** |
| **Preferred vs. Mandatory experience** | "0-1 year required, 2 years preferred" is treated as an entry-level opening. | **Core Match** |
| **Truncated Search Snippet (DDG Fallback)** | Link is preserved, but snippet lacks description and company is generic. | **Needs Review** (Never hallucinate missing details) |
| **"Web Designer" title** | Inspect responsibilities: if building web app UI/Figma flows -> Core. If building WordPress marketing sites/HTML styling -> Excluded. | **Needs Review / Excluded** |
| **"Frontend Developer" title** | Inspect responsibilities: if building Design Systems / UX Engineer -> Related. If pure backend/APIs/React business logic -> Excluded. | **Related / Excluded** |

---

## 6. Structured Schema Representation (Proposed Specification)

When Gemini or the parsing engine evaluates a candidate, it must populate this normalized JSON contract:

```json
{
  "job_id": "job_001",
  "decision": "CORE_MATCH",
  "category": "core_product_design",
  "assigned_section": "primary_digest",
  "relevance_score": 92,
  "confidence": "high",
  "title_classification": {
    "raw_title": "Associate Product Designer",
    "normalized_title": "Product Designer",
    "seniority_level": "entry_level"
  },
  "eligibility": {
    "experience_years_required": "0-1",
    "experience_status": "verified",
    "location_matched": "Dhaka, Bangladesh",
    "remote_type": "hybrid",
    "bangladesh_eligible": true
  },
  "screening_rationale": "Directly focuses on mobile wallet workflows and design systems. Welcomes fresh graduates.",
  "flags": {
    "is_snippet_only": false,
    "missing_compensation": true,
    "has_marketing_graphics_risk": false
  }
}
```

### Allowed Enum Values:
* `decision`: `CORE_MATCH` | `RELATED_OPPORTUNITY` | `NEEDS_REVIEW` | `EXCLUDED`
* `category`: `core_product_design` | `design_engineering` | `design_systems` | `ux_research` | `marketing_graphics` | `senior_executive` | `unrelated`
* `seniority_level`: `internship` | `trainee` | `entry_level` | `junior` | `mid_level` | `senior` | `unspecified`

---

## 7. Representative Decision Table (12 Realistic Benchmark Cases)

| ID | Raw Scraped Title | Hiring Company | Location & Requirements | Ground-Truth Classification | Justification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **#1** | Junior UX Designer | bKash Limited | Dhaka / 0–1 yr experience / Mobile wallet flows | **CORE_MATCH** | Perfect entry-level local FinTech UX role. |
| **#2** | Product Designer | Remote Tech Studio | Worldwide Remote / 1–2 yrs / Web app SaaS | **CORE_MATCH** | Unranked product design within 0-2y range, global remote. |
| **#3** | UI/UX Design Intern | Pathao | Dhaka (Gulshan) / Fresh graduates / Figma | **CORE_MATCH** | Explicit local design internship. |
| **#4** | UX Engineer | Ollyo | Dhaka / React + Figma Design Systems / 0–2 yrs | **RELATED_OPPORTUNITY** | Design engineering role leveraging CSE coding + design tokens. |
| **#5** | Design Systems Specialist | Enterprise SaaS | Remote (Worldwide) / Component libraries / 1-2 yrs | **RELATED_OPPORTUNITY** | Pure design systems architecture; technical adjacency. |
| **#6** | UX Researcher (Junior) | UserStudy Corp | Remote (Worldwide) / Usability tests / 0–1 yr | **RELATED_OPPORTUNITY** | Core UX research and analytics; separated from UI/UX design. |
| **#7** | Senior Product Designer | Brain Station 23 | Dhaka / 5+ yrs experience required | **EXCLUDED** | Seniority ceiling exceeded (Senior title + 5+ years). |
| **#8** | UI/UX Designer & Graphic Artist | Creative Agency | Dhaka / Facebook banners, flyers, packaging | **EXCLUDED** | Negative filter: Graphic design masquerading as UX. |
| **#9** | Product Designer (US Only) | Silicon Valley Co | Remote - Must be US Citizen / W2 only | **EXCLUDED** | Geographically restricted; excludes Bangladesh residents. |
| **#10** | Lead UX Researcher | Global Telecom | Worldwide Remote / 7+ yrs experience | **EXCLUDED** | Excluded due to Lead seniority and 7+ years requirement. |
| **#11** | Product Designer - Apply Now... | Hiring Company | Search snippet only / No description text | **NEEDS_REVIEW** | Snippet fallback with unverified JD and company; do not guess. |
| **#12** | Experience Designer | FinTech Startup | Remote / "1–3 years experience preferred" | **NEEDS_REVIEW** | Borderline experience range; lower bound eligible, upper bound mid. |

---

## 8. Summary of Open Questions & Assumptions for Approval

Before implementing Step 3, the following design assumptions require user confirmation:

1. **Handling "Needs Review" in Telegram:**
   * *Proposed Assumption:* Should the daily Telegram digest append a short `🔍 Needs Review (Unconfirmed Details)` section at the very bottom containing links to ambiguous leads, or should unconfirmed leads be held back in a separate audit file until manually reviewed?
2. **Handling Unpaid Internships:**
   * *Proposed Assumption:* Exclude all unpaid circulars unless explicitly branded as credit-based university trainee programs.
3. **Experience Range Upper Bounds (1–3 years):**
   * *Proposed Assumption:* When a job states "1–3 years", if the lower bound is $\le 2$ years, we classify it under **Needs Review** or **Core Match** so the candidate does not miss negotiable junior roles. Confirm if 3-year upper bounds are acceptable to see.

---
*End of Candidate Profile Specification (Step 2).*
