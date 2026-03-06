# AI Marketing Suite — Improvement Tasks

## Critical (Fix Now)

### 1. Create Shared Accuracy Guardrails
- **File:** `skills/ACCURACY-GUARDRAILS.md`
- **Why:** The guardrails added to market-seo after the FlightScope incident need to apply to all analytical skills. A shared file prevents duplication and ensures consistency.
- **Covers:** Confidence levels, scraper limitations, URL verification, JS-rendering caveats, heading context, never fabricating data.

### 2. Port Guardrails to All Analytical Skills
- **Files:** `skills/market-landing/SKILL.md`, `skills/market-copy/SKILL.md`, `skills/market-funnel/SKILL.md`, `skills/market-competitors/SKILL.md`, `skills/market-brand/SKILL.md`
- **Why:** These skills fetch and analyze live web pages but lack the accuracy safeguards that prevent hallucinated findings (fabricated URLs, misquoted copy, invented page elements).
- **Action:** Add reference to shared guardrails + skill-specific accuracy notes.

### 3. Fix Security Issues in competitor_scanner.py
- **File:** `scripts/competitor_scanner.py`
- **Issues:**
  - SSL verification disabled (`ssl.CERT_NONE`) — MITM vulnerability
  - Bare `except:` blocks silently swallow all errors including KeyboardInterrupt
- **Action:** Re-enable SSL verification with specific error handling; replace bare excepts with `except Exception as e:`.

## High Priority (This Month)

### 4. Align PDF Report with Markdown Report
- **Files:** `scripts/generate_pdf_report.py`, `skills/market-report/SKILL.md`, `skills/market-report-pdf/SKILL.md`
- **Why:** PDF and Markdown reports use different category names and weights, producing inconsistent scores for the same site.
- **Action:** Standardize categories and make PDF script read weights from JSON input.

### 5. Add Verification Workflows to Analytical Skills
- **Files:** Same 5 skills as task #2
- **Why:** market-seo has a verification step where script output is cross-checked against manual analysis. Other skills don't.
- **Action:** Add verification checklist to each skill's output process.

### 6. Expand Pricing Detection in competitor_scanner.py
- **File:** `scripts/competitor_scanner.py`
- **Why:** Only tries /pricing, /plans, /price. Many sites use different paths.
- **Action:** Add /subscribe, /billing, /packages, /get-started, /buy and scan homepage for pricing links.

### 7. Add Input Validation to social_calendar.py
- **File:** `scripts/social_calendar.py`
- **Why:** No bounds checking on days, no platform name validation, crashes on bad argv.
- **Action:** Validate arguments, cap days at 90, check platform names.

## Medium Priority (This Quarter)

### 8. Fix Cross-Skill File Naming
- **Files:** All skills with cross-references
- **Why:** Skills reference each other's output files but names don't match (e.g., skill writes `COMPETITOR-REPORT.md` but report skill looks for `COMPETITOR-ANALYSIS.md`).
- **Action:** Audit all output filenames and cross-references, standardize.

### 9. Add Scoring Calibration to Agent Files
- **Files:** All 5 files in `agents/`
- **Why:** 0-10 scoring with no calibration examples produces inconsistent results between runs.
- **Action:** Add concrete "what a 3, 5, 7, 9 looks like" examples for key dimensions.

### 10. Improve market-proposal Auto-Population
- **File:** `skills/market-proposal/SKILL.md`
- **Why:** Vague guidance on using prior audit data. Should explicitly list which files to read and what to extract.
- **Action:** Add specific file-reading instructions and field mapping.

### 11. Add Deliverability Checklist to market-emails
- **File:** `skills/market-emails/SKILL.md`
- **Why:** Generates email sequences without CAN-SPAM compliance, spam trigger, or sender reputation warnings.
- **Action:** Add deliverability checklist section.

### 12. Add Policy Compliance to market-ads
- **File:** `skills/market-ads/SKILL.md`
- **Why:** Generates ad copy without checking Meta, Google, LinkedIn policy restrictions.
- **Action:** Add policy compliance check section per platform.

### 13. Fix Bar Chart Label Truncation
- **File:** `scripts/generate_pdf_report.py`
- **Why:** Category names truncated to 22 chars — "Content & Messaging" becomes "Content & Messagin".
- **Action:** Increase limit or use intelligent abbreviation.

## Low Priority (When Resources Allow)

### 14. Add Launch Size Parameter to market-launch
- **File:** `skills/market-launch/SKILL.md`
- **Why:** Output is overwhelming. Should support Minimal/Standard/Full scoping.

### 15. Add Assumption Labels to market-funnel
- **File:** `skills/market-funnel/SKILL.md`
- **Why:** Revenue estimates use placeholders without marking them as assumptions.

### 16. Expand Hook Variety in social_calendar.py
- **File:** `scripts/social_calendar.py`
- **Why:** Only 5-6 hooks per platform; visible repetition in 30-day calendars.
