# AI Marketing Suite — Future Improvement Plan

## Executive Summary

This plan outlines the roadmap for continuing to improve the AI Marketing Suite's SEO audit tool and broader marketing analytics capabilities. The SEO audit tool has undergone significant improvements (Phases 1-5 complete), but additional work remains to extend these reliability patterns to other skills and address remaining technical debt.

**Status as of March 2026:**
- ✅ **Phase 1-5 Complete**: Core SEO audit reliability improvements
- 🔄 **In Progress**: Extending patterns to other analytical skills
- 📋 **Planned**: Additional enhancements and refinements

---

## Part 1: SEO Audit Tool — Completed Improvements

### ✅ Phase 1: Fresh-Run Isolation and Reporting Contract
**Status:** COMPLETE

**What Was Done:**
- Added explicit "Fresh Run Requirement" to `market-seo/SKILL.md` forbidding use of prior audit context
- Implemented "Evidence-First Reporting Contract" requiring confidence levels, evidence sources, and page URLs for every finding
- Added mandatory "Methodology & Limitations" section to all SEO reports

**Files Modified:**
- `skills/market-seo/SKILL.md`

**Impact:** SEO audits are now isolated from previous runs, eliminating context contamination.

---

### ✅ Phase 2: Analyzer Structured-Data Reliability
**Status:** COMPLETE

**What Was Done:**
- Fixed Microdata collection in `analyze_page.py`
- Added support for JSON-LD `@type` arrays and `@graph` structures
- Preserved richer schema evidence instead of only returning unique schema types
- Exposed structured-data findings by source: JSON-LD, Microdata, RDFa

**Files Modified:**
- `scripts/analyze_page.py`

**Impact:** Structured data detection is now accurate across all formats, eliminating false "no schema" reports on Shopify and similar platforms.

---

### ✅ Phase 3: Multi-Page SEO Evidence Collection
**Status:** COMPLETE

**What Was Done:**
- Created `collect_seo_evidence.py` for site-level evidence collection
- Added representative page sampling: homepage, product, collection, comparison, blog index, article, about/trust, policy pages
- Added `--profile` flag for standard vs deep analysis

**Files Created:**
- `scripts/collect_seo_evidence.py`

**Impact:** Site-level conclusions are now based on actual evidence from multiple page types, not just homepage extrapolation.

---

### ✅ Phase 4: Rendered Verification for Critical Findings
**Status:** COMPLETE

**What Was Done:**
- Created `verify_rendered_seo.py` with pluggable browser providers (Browserless, local Playwright CLI)
- Added browser-rendered verification for structured data, headings, canonical tags, and meta descriptions
- Implemented confidence level system: Confirmed, Likely, Needs Verification

**Files Created:**
- `scripts/verify_rendered_seo.py`

**Impact:** JavaScript-heavy sites (Shopify, React, Vue, Next.js) now have accurate structured data detection.

---

### ✅ Phase 5: Evidence Artifact and Report Generation
**Status:** COMPLETE

**What Was Done:**
- Created `generate_seo_audit_report.py` for artifact-driven report generation
- Reports are now generated from `seo_evidence.json` and `rendered_verification.json`
- Standardized output naming and evidence schema

**Files Created:**
- `scripts/generate_seo_audit_report.py`

**Impact:** Reports are now traceable to source evidence, with no unsupported claims.

---

## Part 2: Remaining SEO Audit Enhancements

### 📋 Priority: HIGH

#### 1. Add Google Rich Results Test API Integration
**Why:** Provide definitive structured data validation without requiring manual browser testing.

**Approach:**
- Add API integration to `verify_rendered_seo.py`
- Include API results in rendered verification output
- Update confidence assignment rules to treat API-verified findings as Confirmed

**Files to Modify:**
- `scripts/verify_rendered_seo.py`
- `skills/market-seo/SKILL.md`

---

#### 2. Add Core Web Vitals Measurement
**Why:** Current performance estimates are based on resource counts, not actual measurements.

**Approach:**
- Integrate with Google PageSpeed Insights API or add local Lighthouse testing
- Include LCP, FID/INP, CLS measurements in evidence
- Update scoring algorithm to use real metrics

**Files to Create:**
- `scripts/measure_core_web_vitals.py`

**Files to Modify:**
- `scripts/collect_seo_evidence.py`
- `scripts/generate_seo_audit_report.py`

---

#### 3. Add JavaScript Framework Detection
**Why:** Automatically trigger browser verification for JS-heavy sites.

**Approach:**
- Add detection for React, Vue, Next.js, Nuxt.js, Angular, Shopify themes
- Automatically recommend browser verification when frameworks detected
- Include framework info in methodology section

**Files to Modify:**
- `scripts/analyze_page.py`
- `scripts/collect_seo_evidence.py`

---

## Part 3: Cross-Skill Reliability Improvements

### 📋 Priority: CRITICAL

#### 4. Extend Guardrails to All Analytical Skills
**Why:** Other skills that fetch/analyze web pages lack the same accuracy safeguards.

**Skills to Update:**
- `market-landing`
- `market-copy`
- `market-funnel`
- `market-competitors`
- `market-brand`

**Action Items:**
- Add reference to shared `ACCURACY-GUARDRAILS.md`
- Add skill-specific accuracy notes
- Implement evidence-first reporting for each

**Status:** Ready to implement

---

#### 5. Add Verification Workflows to Analytical Skills
**Why:** Only `market-seo` has a verification step where script output is cross-checked.

**Action Items:**
- Add verification checklist to each skill's output process
- Require confidence levels on findings
- Add methodology sections to reports

**Status:** Ready to implement

---

### 📋 Priority: HIGH

#### 6. Fix Security Issues in competitor_scanner.py
**Issues:**
- SSL verification disabled (`ssl.CERT_NONE`) — MITM vulnerability
- Bare `except:` blocks silently swallow errors

**Fix:**
- Re-enable SSL verification with specific error handling
- Replace bare excepts with `except Exception as e:`

**File:** `scripts/competitor_scanner.py`

**Status:** Security fix, should be done immediately

---

#### 7. Expand Pricing Detection in competitor_scanner.py
**Why:** Only tries /pricing, /plans, /price. Many sites use different paths.

**Add Paths:**
- /subscribe, /billing, /packages, /get-started, /buy
- Scan homepage for pricing links

**File:** `scripts/competitor_scanner.py`

**Status:** High value for competitive analysis

---

#### 8. Add Input Validation to social_calendar.py
**Why:** No bounds checking on days, no platform name validation, crashes on bad argv.

**Add:**
- Validate platform names against whitelist
- Cap days at 90
- Graceful error handling

**File:** `scripts/social_calendar.py`

**Status:** Prevents crashes, improves reliability

---

## Part 4: Report Consistency Improvements

### 📋 Priority: HIGH

#### 9. Align PDF Report with Markdown Report
**Problem:** PDF and Markdown reports use different category names and weights, producing inconsistent scores.

**Action:**
- Standardize categories across both formats
- Make PDF script read weights from JSON input
- Ensure same inputs produce same scores

**Files:**
- `scripts/generate_pdf_report.py`
- `skills/market-report/SKILL.md`
- `skills/market-report-pdf/SKILL.md`

**Status:** High priority for user trust

---

#### 10. Fix Cross-Skill File Naming
**Problem:** Skills reference each other's output files but names don't match.

**Action:**
- Audit all output filenames and cross-references
- Standardize naming conventions
- Create shared constants file

**Files:** All skills with cross-references

**Status:** Medium priority but important for automation

---

#### 11. Add Scoring Calibration to Agent Files
**Problem:** 0-10 scoring with no calibration examples produces inconsistent results.

**Action:**
- Add concrete "what a 3, 5, 7, 9 looks like" examples for key dimensions
- Include anchor examples for each score level

**Files:** All files in `agents/`

**Status:** Medium priority, improves consistency

---

## Part 5: Additional Enhancements

### 📋 Priority: MEDIUM

#### 12. Improve market-proposal Auto-Population
**Issue:** Vague guidance on using prior audit data.

**Action:**
- Add specific file-reading instructions
- Add field mapping from audit to proposal

**File:** `skills/market-proposal/SKILL.md`

---

#### 13. Add Deliverability Checklist to market-emails
**Issue:** Generates email sequences without CAN-SPAM compliance warnings.

**Action:**
- Add deliverability checklist section
- Include spam trigger warnings

**File:** `skills/market-emails/SKILL.md`

---

#### 14. Add Policy Compliance to market-ads
**Issue:** Generates ad copy without checking platform policy restrictions.

**Action:**
- Add policy compliance check section per platform
- Include Meta, Google, LinkedIn restrictions

**File:** `skills/market-ads/SKILL.md`

---

#### 15. Fix Bar Chart Label Truncation in PDF Reports
**Issue:** Category names truncated to 22 chars.

**Action:**
- Increase limit or use intelligent abbreviation

**File:** `scripts/generate_pdf_report.py`

---

### 📋 Priority: LOW

#### 16. Add Launch Size Parameter to market-launch
**Issue:** Output is overwhelming. Should support Minimal/Standard/Full scoping.

**File:** `skills/market-launch/SKILL.md`

---

#### 17. Add Assumption Labels to market-funnel
**Issue:** Revenue estimates use placeholders without marking them as assumptions.

**File:** `skills/market-funnel/SKILL.md`

---

#### 18. Expand Hook Variety in social_calendar.py
**Issue:** Only 5-6 hooks per platform; visible repetition in 30-day calendars.

**File:** `scripts/social_calendar.py`

---

## Implementation Priority

### Immediate (This Sprint)
1. Fix security issues in `competitor_scanner.py`
2. Add input validation to `social_calendar.py`

### Short Term (This Month)
3. Extend guardrails to all analytical skills
4. Add verification workflows to analytical skills
5. Align PDF report with markdown report
6. Fix cross-skill file naming
7. Add Google Rich Results Test API integration

### Medium Term (This Quarter)
8. Add Core Web Vitals measurement
9. Add JavaScript framework detection
10. Expand pricing detection
11. Add scoring calibration to agent files
12. Improve market-proposal auto-population

### Long Term (When Resources Allow)
13. Add deliverability checklist to market-emails
14. Add policy compliance to market-ads
15. Fix bar chart label truncation
16. Add launch size parameter to market-launch
17. Add assumption labels to market-funnel
18. Expand hook variety in social_calendar.py

---

## Success Metrics

- **Zero false "no structured data" reports** on sites that actually have it
- **All findings include confidence levels** and evidence sources
- **No security vulnerabilities** in core scripts
- **Consistent scoring** across PDF and markdown reports
- **No crashes** from invalid input
- **Fresh analysis** enforced for all audit-type skills

---

## Notes

- This plan builds on the SEO Audit Reliability Improvement Spec (`docs/SEO_AUDIT_TOOL_SPEC.md`)
- See `TASKS.md` for the original task list from which this plan was derived
- All SEO audit improvements (Phases 1-5) are complete and in production

---

*Last Updated: March 20, 2026*
