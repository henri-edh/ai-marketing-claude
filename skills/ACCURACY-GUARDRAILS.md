# Accuracy Guardrails for Analytical Skills

All skills that fetch and analyze live web pages MUST follow these guardrails to prevent inaccurate reports. These rules exist because static HTML scraping has inherent limitations that can lead to false findings.

## 8 Mandatory Rules

### 1. Never Fabricate URLs
Only reference URLs that you have actually fetched or that appear in the `links_found` output from `analyze_page.py`. Never guess or construct URLs based on common patterns (e.g., don't assume `/about`, `/pricing`, `/blog` exist without verification).

### 2. Trust Script Data Over Assumptions
When `analyze_page.py` or another script provides structured data (headings, meta tags, links, structured data), use that data as the source of truth. Do not override script findings with assumptions about what "should" be on the page.

### 3. Acknowledge JavaScript-Rendering Limitations
Static HTML fetching (via WebFetch or urllib) cannot execute JavaScript. Many modern sites inject content dynamically via JS frameworks (React, Vue, Next.js, Shopify themes). When findings suggest something is "missing," always add: "Note: This element may be rendered via JavaScript and not visible to static HTML analysis. Verify in a browser."

### 4. Verify Canonical and Redirect Behavior
Do not report canonical tag issues or redirect problems without actually checking. www vs non-www, HTTP vs HTTPS, and trailing slash variants require real verification. If you cannot verify, note: "Needs manual verification in browser or via redirect checker."

### 5. Understand Heading Context
Headings (H1-H6) in `<nav>`, `<header>`, `<footer>`, and `<aside>` elements serve structural/navigational purposes and should not be evaluated as content headings. Only flag heading issues for headings in the `<main>` content area. If `analyze_page.py` provides `headings_with_context`, use the context field to filter appropriately.

### 6. Be Transparent About Scraper Limitations
Every report should include a brief "Methodology & Limitations" note that acknowledges:
- Analysis based on static HTML fetching (JavaScript-rendered content may not be captured)
- Performance metrics are estimated, not measured (recommend tools like PageSpeed Insights for precise data)
- Content behind authentication, paywalls, or geo-restrictions was not analyzed

### 7. Design Choices vs SEO/Marketing Failures
Not every deviation from "best practice" is a problem. Recognize that some choices are intentional design decisions:
- Blog posts without author bylines (common in brand-authored content)
- Footer headings used for navigation structure
- Minimal meta descriptions on pages targeting featured snippets
- Single-page sites without deep internal linking

Frame these as "considerations" or "opportunities," not failures.

### 8. Use Confidence Levels
Tag every finding with a confidence level:

| Level | When to Use | Example |
|---|---|---|
| **Confirmed** | Directly observed in fetched HTML/script output | "Title tag is 78 characters (confirmed via script output)" |
| **Likely** | Strong evidence but not 100% certain | "No structured data detected in static HTML (likely missing, but may be JS-injected)" |
| **Needs Verification** | Cannot determine from static analysis alone | "Page speed appears slow based on resource count (needs verification via PageSpeed Insights)" |

## Verification Checklist

Before finalizing any analytical report, verify:

- [ ] Every URL referenced in the report was actually fetched or found in page links
- [ ] Every "missing" element has been qualified with JS-rendering caveat where applicable
- [ ] No copy or text has been quoted that wasn't directly extracted from the page
- [ ] Scores are justified with specific evidence, not generic assessments
- [ ] Design choices are distinguished from actual problems
- [ ] The report includes a Methodology & Limitations section
- [ ] All findings have appropriate confidence levels
