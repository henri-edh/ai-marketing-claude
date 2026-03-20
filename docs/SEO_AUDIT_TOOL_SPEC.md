# SEO Audit Reliability Improvement Spec

## Goal

Make `/market seo` produce accurate, fresh, evidence-backed SEO audits for modern sites, including JavaScript-heavy storefronts and article pages with structured data.

## Problem Summary

The current SEO audit flow has three reliability issues:

1. The skill can reuse prior audit context, which contaminates supposedly fresh audits.
2. The report can make stronger claims than the analyzer actually supports.
3. `scripts/analyze_page.py` has incomplete structured-data handling, especially for Microdata.

## Non-Goals

- Replacing the current markdown report format entirely
- Building a full crawler
- Shipping a full browser automation stack in this phase

## Principles

- Fresh run by default: `/market seo` must not use prior audit files as inputs.
- Evidence before interpretation: every report claim must trace back to a fetched page and observed evidence.
- Confidence must match methodology: static HTML findings cannot be labeled confirmed if rendering-dependent.
- Page-type aware analysis: blog index findings cannot stand in for article-page findings.

## Current Failure Modes

### Prior-context leakage

The skill still instructs the model to cross-reference previous audit outputs. This makes it too easy to carry forward earlier conclusions rather than generating a clean audit from current evidence.

### Unsupported structured-data claims

The report currently mixes:

- static HTML observations
- inferred JavaScript-rendered findings
- recommendations phrased as confirmed gaps

This is how a report can claim article schema is missing even when an actual article page exposes author metadata and schema.

### Incomplete Microdata support

The parser initializes Microdata tracking but does not correctly close and emit items. In practice, that means some pages with valid Microdata are reported as having no structured data.

## Target State

Each SEO audit run should produce:

1. A fresh evidence artifact generated from the current run only
2. A markdown report derived strictly from that artifact
3. Findings labeled with:
   - confidence
   - evidence source
   - page URL checked

## Phased Plan

### Phase 1: Fresh-run isolation and reporting contract

Scope:

- Remove any instruction for `/market seo` to consume prior audit context
- Require every SEO audit run to start from live evidence gathered in the same session
- Add an evidence contract to the skill:
  - every finding includes confidence
  - every critical item must be confirmed
  - every schema claim references the exact page type and URL checked
- Add a mandatory methodology and limitations section to the output

Deliverables:

- Updated `skills/market-seo/SKILL.md`
- Optional README note clarifying that SEO audits are standalone inputs to later reports, not consumers of earlier reports

### Phase 2: Analyzer structured-data reliability

Scope:

- Fix Microdata collection in `scripts/analyze_page.py`
- Support JSON-LD `@type` arrays
- Preserve richer schema evidence instead of only returning unique schema types
- Expose structured-data findings by source:
  - JSON-LD
  - Microdata
  - RDFa

Deliverables:

- Updated `scripts/analyze_page.py`
- Regression tests for JSON-LD and Microdata parsing

### Phase 3: Multi-page SEO evidence collection

Scope:

- Analyze explicit representative pages:
  - homepage
  - one product page
  - blog index
  - one or two article pages discovered from the blog index
- Stop making article-level conclusions without auditing at least one article page

Deliverables:

- Site-level evidence collection workflow
- Clear page inventory in the report

### Phase 4: Rendered verification for critical findings

Scope:

- Add browser-rendered verification for:
  - structured data
  - rendered headings
  - canonical tags where runtime mutation is possible
- Keep static HTML as the baseline, but require rendered confirmation for JS-dependent claims

Deliverables:

- Browser verification workflow
- Updated confidence assignment rules

### Phase 5: Evidence artifact and report generation hardening

Scope:

- Emit `seo_evidence.json` from the current run
- Generate `SEO_AUDIT.md` only from the evidence file
- Standardize output naming across skills and docs

Deliverables:

- Stable evidence schema
- Consistent filenames across repo references

## Evidence Contract

Each report finding must include:

- `confidence`: `Confirmed`, `Likely`, or `Needs Verification`
- `source`: `static_html`, `rendered_dom`, `manual_validation`, or `external_tool`
- `page_url`: exact URL checked
- `evidence`: short factual observation

Critical findings may only use `Confirmed`.

## Data Model Changes

`analyze_page.py` should expose structured-data details in addition to aggregate counts:

- `json_ld_schema_types`
- `json_ld_items`
- `microdata_types`
- `microdata_items`
- `rdfa_types`
- `rdfa_items`
- `schema_summary`

Where possible, each item should preserve:

- schema type
- source format
- key identifying fields such as `name`, `headline`, `author`, `url`, or `image`

## Test Plan

Add parser-level regression tests for:

1. JSON-LD with a single `@type`
2. JSON-LD with `@type` as an array
3. JSON-LD with `@graph`
4. Microdata `Article` with `headline`, `author`, and `image`
5. Mixed-format pages where counts and type summaries remain stable

## Acceptance Criteria

Phase 1 is complete when:

- `/market seo` no longer instructs the model to use prior audit files
- report requirements explicitly enforce confidence and methodology labeling

Phase 2 is complete when:

- Microdata `Article` pages are detected by the parser
- JSON-LD `@type` arrays are flattened correctly
- structured-data output includes richer evidence than a single unique-type count
- regression tests pass locally

## Risks

- More conservative wording may lower apparent certainty in reports, but this is the correct tradeoff.
- Some current examples in existing reports will no longer qualify as confirmed findings.
- Browser verification will add execution time in later phases.

## Implementation Order

1. Phase 1: prompt and report contract
2. Phase 2: parser and tests
3. Phase 3: multi-page coverage
4. Phase 4: rendered verification
5. Phase 5: evidence artifact and filename cleanup
