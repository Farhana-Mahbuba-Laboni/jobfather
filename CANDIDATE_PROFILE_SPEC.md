# JobFather Candidate Profile Specification (v1.1 - Refined)

**Document Status:** REVISED DRAFT FOR APPROVAL (Step 2.1)  
**Target Candidate Background:** B.Sc. in Computer Science & Engineering (CSE) graduate transitioning into Product Design / UX Engineering.  
**Core Objective:** Deterministically identify, classify, and filter entry-level and junior digital product design opportunities while eliminating senior bloat, marketing graphic design, and geographically ineligible postings.

---

## 1. Candidate Persona & Target Profile

* **Primary Career Goal:** Junior / Entry-Level Product Designer or UI/UX Designer.
* **Secondary / Strategic Advantage:** Technical & analytical adjacencies that benefit from a CSE foundation (Design Systems, Design Engineering, UX Research, interactive prototypes, and developer handoff).
* **Target Seniority:** 0–2 years of professional experience, Internships, Trainee programs, Associate roles, or Fresh Graduate tracks.
* **Target Geographic Eligibility:** 
  * Any on-site or hybrid location across **Bangladesh** (e.g., Dhaka, Chittagong, Sylhet, Rajshahi, Khulna, or any Bangladeshi tech hub).
  * **Worldwide Remote** or **Regional Remote (APAC / South Asia)** that permits applicants residing in Bangladesh.

---

## 2. Taxonomy & Digest Categorization

Opportunities are partitioned into four discrete deterministic categories:

```text
                                  [Scraped Circular]
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
         [Meets Exclusions?]                             [Geographic Check]
         - Mandatory 3+ yrs                              - In Bangladesh? -> Eligible
         - Senior/Lead/Manager                           - Worldwide Remote? -> Eligible
         - Flyers / Pure Graphics                        - Timezone Overlap only? -> Needs Review
         - Explicitly Unpaid                             - Country Restriction (No BD)? -> Excluded
         - Excludes Bangladesh                           - Remote Unclear? -> Needs Review
                  │                                               │
             YES ─┴─► EXCLUDED                                    ▼
                                                         [Discipline Match]
                                                                  │
                           ┌──────────────────────────────────────┼──────────────────────────────────────┐
                           ▼                                      ▼                                      ▼
                   [Core UX/Product]                     [Technical Adjacent]                   [Ambiguous / Partial]
                  UI, UX, Product,                      Design Engineering,                    - Requires 1-3y
                  Interaction Design                    Systems, Research                      - Unclear remote country
                  (Evidence signals)                    (Evidence signals)                     - Snippet-only data
                           │                                      │                                      │
                           ▼                                      ▼                                      ▼
                     CORE MATCHES                        RELATED OPPORTUNITIES                       NEEDS REVIEW
                   (Primary Digest)                        (Separate Section)                     (needs_review.json)
```

### Category 1: Core Matches (Primary Digest Section)
Directly targets digital product design, user experience workflows, user interfaces, wireframing, and interactive product design.
* **Accepted Titles / Synonyms:**
  * `UI/UX Designer`, `UX/UI Designer`, `User Experience Designer`
  * `Product Designer`, `Associate Product Designer`, `Junior Product Designer`
  * `UI Designer`, `User Interface Designer`
  * `Interaction Designer`, `IxD Designer`
  * `Experience Designer`, `Digital Product Designer`
* **Evidence Signals (Non-Mandatory Heuristic):**
  * Mentions user flows, information architecture, wireframing, component design, low/high-fidelity prototyping, mobile/web interface layouts, or usability evaluation.
  * **Critical Rule:** These responsibilities are **evidence signals, not a mandatory checklist**. A junior UI Designer who focuses purely on wireframes and Figma interface components without doing user testing or developer handoff **fully qualifies as a Core Match**.

### Category 2: Related Opportunities (Separated Digest Section)
High-value technical and analytical adjacencies where a B.Sc. in Computer Science & Engineering provides an immediate competitive advantage over non-technical design candidates. Delivered in a separate section to keep the primary digest focused.
* **Accepted Titles / Synonyms:**
  * `Design Engineer`, `UX Engineer`, `UI Engineer` (Evidence: Bridging Figma and frontend code, interactive components, CSS/React/Flutter UI implementation)
  * `Design System Specialist`, `Design Systems Designer` (Evidence: Tokenization, reusable Figma component libraries, multi-brand UI consistency)
  * `UX Researcher`, `Junior UX Researcher` (Evidence: Usability benchmarking, user interviews, qualitative & quantitative product analytics)
* **Rule:** A job does not qualify as Related merely because its description mentions "Figma" or "Research." Its overall day-to-day responsibilities must center on these disciplines.

### Category 3: Needs Review / Insufficient Information (`needs_review.json` Audit Record)
Postings that exhibit positive intent but lack verifiable attributes or fall into borderline policies:
* Requires a borderline range of **1–3 years** of mandatory experience.
* Worldwide remote jobs with **unclear country/residence eligibility**.
* Remote jobs with strict **timezone overlap requirements** (e.g., "Must overlap 4 hours with US Eastern Time") where legal residence eligibility is not stated.
* **Search snippet fallbacks** where the full job description could not be scraped.
* **Telegram Delivery Policy:** To prevent notification fatigue, ambiguous jobs are **not** posted as full cards in the main digest. Instead, they are persisted to a local `needs_review.json` audit file, and the daily Telegram digest appends a 1-line summary counter:  
  *`🔍 3 ambiguous circulars logged to needs_review.json for inspection.`*

### Category 4: Excluded (Suppressed / Disqualified)
Instantly disqualified and filtered from notification digests.

---

## 3. Strict Exclusion Rules

A candidate opportunity is **instantly rejected** if it triggers any of the following rules:

1. **Seniority Ceiling:**
   * Contains unambiguous seniority indicators in title: `Senior`, `Sr.`, `Lead`, `Principal`, `Staff`, `Director`, `Head of`, `Manager`, `VP`, `Chief`.
   * *Context-Aware Note on "Architect":* Disqualify managerial enterprise titles (e.g., `Chief Architect`, `Lead Enterprise Architect`). However, do not reject `Information Architect` if junior/entry-level.
2. **Mandatory Experience Floor:**
   * Explicitly demands **3 or more years of minimum mandatory experience** (e.g., *"Minimum 3 years required"*, *"3–5 years experience"*, *"4+ years"*).
3. **Marketing & Graphic Design Floor:**
   * Roles centered on marketing collateral, social media banners, promotional flyers, packaging, print graphics, billboards, brochures, or promotional video editing.
   * *The "Figma Trap" Rule:* Job circulars titled "UI/UX Designer" whose actual bullet points demand daily Facebook post graphics, print press files, and advertising flyers without product/web/app workflows.
4. **Geographic Ineligibility:**
   * On-site or hybrid roles physically located outside Bangladesh.
   * Remote roles with explicit geo-fences that exclude South Asia / Bangladesh (e.g., *"Must reside in US/Canada"*, *"EU citizens only"*, *"Hiring strictly in UK timezone and country"*, *"Requires US Work Authorization without sponsorship"*).
5. **Unpaid Opportunities:**
   * Explicitly unpaid internships, unpaid volunteer positions, or stipends labeled "Unpaid".
   * *Policy:* Excluded by default. University academic-credit programs are excluded unless the candidate explicitly chooses to opt in.

---

## 4. Standardized Experience & Seniority Rules

To eliminate contradictions, experience is evaluated across three distinct parameters:

| Experience Parameter | Definition | Evaluation Rule |
| :--- | :--- | :--- |
| **0–2 years required** | Minimum mandatory requirement is within target junior range. | **Eligible** (Core Match or Related Opportunity based on discipline) |
| **1–3 years required** | Mandatory range overlaps target but extends beyond it. | **Needs Review** (Do not assume eligible or ineligible; log to `needs_review.json`) |
| **1–3 years preferred** | 1–3 years is mentioned as preferred/desired, but mandatory requirement is 0–1 year or unspecified. | **Eligible** (Preferred experience is not a hard barrier; evaluate as Core or Related) |
| **3+ years minimum required** | Mandatory experience ceiling exceeded (e.g. 3+ yrs, 4–6 yrs). | **Excluded** |
| **Missing experience** | Unranked title (e.g. "Product Designer") with no years stated in description. | **Eligible** (Mark experience as "Not specified"; do not hallucinate a requirement) |
| **Title / JD conflict** | Title says "Junior", but description requires "Minimum 4 years". | **Excluded** (Mandatory experience requirement strictly overrides title) |

---

## 5. Location & Remote Eligibility Matrix

| Geographic Scenario | Evaluation Logic | Result |
| :--- | :--- | :--- |
| **Any city in Bangladesh** (Dhaka, Chittagong, Sylhet, Rajshahi, Khulna, etc.) | On-site or hybrid within national borders. | **Eligible** |
| **Worldwide Remote / Global / Anywhere** | Open international listing with no regional bans. | **Eligible** |
| **Remote - APAC / South Asia / India & BD** | Explicitly includes candidate's region. | **Eligible** |
| **Remote with explicit country restriction excluding BD** | e.g. "US Only", "Must be located in Germany". | **Excluded** |
| **Remote with timezone overlap requirement only** | e.g. "Worldwide Remote, must overlap 3 hours with EST". | **Needs Review** (Timezone overlap is not a geographic ban; check practical viability) |
| **Remote with completely unclear country eligibility** | Company is based abroad; listing says "Remote" without specifying hiring regions. | **Needs Review** (Preserve in `needs_review.json` without guessing) |
| **Physical on-site/hybrid outside Bangladesh** | Located abroad without remote option. | **Excluded** |

---

## 6. Structured Schema Representation (Proposed Contract)

When the classifier evaluates a candidate, it outputs this normalized JSON contract:

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
    "experience_rule_matched": "0_to_2_years_required",
    "experience_raw": "1 year required, 2 years preferred",
    "experience_status": "verified",
    "location_matched": "Sylhet, Bangladesh",
    "remote_type": "on_site",
    "bangladesh_eligible": true
  },
  "evidence_signals_detected": [
    "wireframing",
    "figma_components",
    "mobile_ui"
  ],
  "screening_rationale": "Focuses on mobile application user interface. Meets Bangladesh location and junior experience criteria.",
  "flags": {
    "is_snippet_only": false,
    "missing_compensation": true,
    "has_timezone_overlap_clause": false
  }
}
```

### Allowed Enum Values:
* `decision`: `CORE_MATCH` | `RELATED_OPPORTUNITY` | `NEEDS_REVIEW` | `EXCLUDED`
* `category`: `core_product_design` | `design_engineering` | `design_systems` | `ux_research` | `marketing_graphics` | `senior_executive` | `unrelated`
* `seniority_level`: `internship` | `trainee` | `entry_level` | `junior` | `mid_level` | `senior` | `unspecified`

---

## 7. Representative Decision Table (16 Benchmark Test Cases)

| ID | Title & Company | Location & Stated Requirements | Ground-Truth Classification | Justification & Applied Policy |
| :--- | :--- | :--- | :--- | :--- |
| **#1** | Junior UX Designer – bKash | Dhaka / 0–1 yr required / Mobile wallet flows | **CORE_MATCH** | Core UX entry role within Bangladesh. |
| **#2** | Product Designer – SaaS Co | Worldwide Remote / 1–2 yrs required / Web app SaaS | **CORE_MATCH** | Core product design within 0-2y range; global remote. |
| **#3** | UI Designer – Tech Studio | Sylhet, Bangladesh / 0–1 yr / Figma wireframes & layouts | **CORE_MATCH** | Demonstrates location eligibility outside Dhaka; UI-only evidence signals valid. |
| **#4** | Junior Product Designer | Remote / 1–3 years experience preferred (0–1 yr required) | **CORE_MATCH** | 1–3 years is preferred, not mandatory; eligible as Core Match. |
| **#5** | UX Engineer – Ollyo | Dhaka / React + Figma Design Systems / 0–2 yrs | **RELATED_OPPORTUNITY** | Design engineering role leveraging CSE coding + design tokens. |
| **#6** | Design Systems Specialist | Worldwide Remote / Component libraries / 1-2 yrs | **RELATED_OPPORTUNITY** | Pure design systems architecture; technical adjacency. |
| **#7** | Junior UX Researcher | Remote (Worldwide) / Usability tests & interviews / 0–1 yr | **RELATED_OPPORTUNITY** | Core UX research and usability analytics. |
| **#8** | Product Designer | Remote / "Must overlap 4 hours with US Eastern Time" | **NEEDS_REVIEW** | Timezone overlap requirement without explicit geographic ban; evaluate viability. |
| **#9** | Product Designer – FinTech | Worldwide Remote / 1–3 years required | **NEEDS_REVIEW** | Mandatory 1–3 year range overlaps target but extends beyond 2y ceiling. |
| **#10** | UI/UX Designer – Global Corp | Remote / No country restrictions or eligibility stated | **NEEDS_REVIEW** | Remote with unclear country eligibility; preserved in `needs_review.json`. |
| **#11** | Product Designer - Apply Now... | Hiring Company / Search snippet only / No description text | **NEEDS_REVIEW** | Snippet fallback with unverified JD and company; do not guess. |
| **#12** | Information Architect (Junior) | Dhaka / Sitemap & content navigation / 1 yr | **CORE_MATCH** | "Architect" in title is valid discipline when context confirms Information Architecture. |
| **#13** | Senior Product Designer – Brain Station | Dhaka / 5+ yrs experience required | **EXCLUDED** | Seniority ceiling exceeded (Senior title + 5+ years). |
| **#14** | UI/UX Designer & Graphic Artist | Dhaka / Daily Facebook banners, flyers, packaging | **EXCLUDED** | Marketing graphics masquerading as UX. |
| **#15** | Product Designer (US Citizen Only) | Remote US / W2 only / US Residence required | **EXCLUDED** | Explicit country restriction excluding Bangladesh. |
| **#16** | UI/UX Design Intern | Agency / Explicitly Unpaid (3-month duration) | **EXCLUDED** | Unpaid internship; excluded by default policy. |

---

## 8. Summary of Revisions (Step 2.1 Changelog)

1. **Standardized 1–3 Years Rule:** Unified across document and decision table: `1–3 years required` $\rightarrow$ **Needs Review**; `1–3 years preferred` $\rightarrow$ **Core/Related Eligible**; `3+ years mandatory` $\rightarrow$ **Excluded**.
2. **Timezone vs. Geography Decoupling:** Reclassified timezone overlap clauses (e.g. US EST overlap) to **Needs Review** rather than geographic exclusion, unless explicit residency/work authorization bans exist.
3. **Nationwide Bangladesh Coverage:** Expanded location eligibility from Dhaka/Chittagong to **any location in Bangladesh** (demonstrated in Benchmark Case #3 with Sylhet).
4. **Needs Review Telegram Handling:** Defined that ambiguous opportunities are logged to persistent `needs_review.json` with only a 1-line count surfaced to Telegram to prevent notification flooding.
5. **Unpaid Opportunities Policy:** Excluded explicitly unpaid positions by default without automatic academic exceptions.
6. **Non-Mandatory Evidence Signals:** Clarified that responsibilities are heuristic evidence signals, allowing UI-only designers (without research or handoff duties) to qualify cleanly.
7. **Refined Title Exclusions:** Removed rigid bans on words like "Architect" to allow legitimate junior `Information Architect` roles while maintaining strict bans on `Senior`, `Lead`, `Principal`, `Manager`, `Director`, `Head of`, and `VP`.

---
*End of Refined Candidate Profile Specification (Step 2.1).*
