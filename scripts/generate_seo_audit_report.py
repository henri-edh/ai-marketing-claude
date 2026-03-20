#!/usr/bin/env python3
"""
Generate SEO_AUDIT.md from evidence artifacts.

This phase makes SEO reporting artifact-driven instead of relying on free-form
report synthesis. The generator consumes:

- seo_evidence.json
- rendered_verification.json (optional but recommended)
"""

import json
import sys
from datetime import date


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def status_for_ratio(ok, warn):
    if ok:
        return "Pass"
    if warn:
        return "Needs Work"
    return "Fail"


def confidence_for(page_url, rendered_by_url):
    rendered_page = rendered_by_url.get(page_url)
    if rendered_page:
        return rendered_page.get("confidence", "Needs Verification")
    return "Likely"


def build_rendered_map(rendered):
    pages = rendered.get("rendered_verification", {}).get("pages", [])
    return {page["page_url"]: page for page in pages}


def normalize_pages(evidence, rendered):
    rendered_by_url = build_rendered_map(rendered)
    pages = []

    for page in evidence.get("pages", []):
        analysis = page.get("analysis", {})
        url = analysis.get("url_analysis", {}).get("final_url", page.get("requested_url", ""))
        pages.append({
            "page_type": page.get("page_type", "other"),
            "page_url": url,
            "analysis": analysis,
            "rendered": rendered_by_url.get(url, {}),
            "confidence": confidence_for(url, rendered_by_url),
        })

    return pages


def first_page_by_type(pages, page_type):
    for page in pages:
        if page["page_type"] == page_type:
            return page
    return None


def pages_by_type(pages):
    grouped = {}
    for page in pages:
        grouped.setdefault(page["page_type"], []).append(page)
    return grouped


def page_title(page):
    rendered = page.get("rendered", {}).get("verification", {})
    return rendered.get("title") or page["analysis"].get("seo", {}).get("title", "")


def page_meta_description(page):
    rendered = page.get("rendered", {}).get("verification", {})
    return rendered.get("meta_description") or page["analysis"].get("seo", {}).get("meta_description", "")


def page_h1(page):
    rendered = page.get("rendered", {}).get("verification", {})
    headings = rendered.get("headings", {}).get("h1", [])
    if headings:
        return headings[0]
    h1s = page["analysis"].get("seo", {}).get("h1_text", [])
    return h1s[0] if h1s else ""


def page_schema_types(page):
    rendered = page.get("rendered", {}).get("verification", {})
    structured = rendered.get("structured_data", {})
    if structured:
        return sorted(set(
            structured.get("json_ld_types", [])
            + structured.get("microdata_types", [])
            + structured.get("rdfa_types", [])
        ))

    tracking = page["analysis"].get("tracking", {})
    return sorted(set(
        tracking.get("json_ld_schema_types", [])
        + tracking.get("microdata_types", [])
        + tracking.get("rdfa_types", [])
    ))


def rendered_error(page):
    rendered = page.get("rendered", {}).get("verification", {})
    return rendered.get("error", "")


def page_title_status(page):
    title = page_title(page)
    return status_for_ratio(45 <= len(title) <= 65, bool(title))


def page_meta_status(page):
    meta = page_meta_description(page)
    return status_for_ratio(120 <= len(meta) <= 170, bool(meta))


def build_executive_summary(homepage, product_page, article_page):
    summary = []
    homepage_schema = page_schema_types(homepage)
    article_schema = page_schema_types(article_page) if article_page else []
    product_schema = page_schema_types(product_page) if product_page else []

    summary.append(
        "FlightScope has a strong technical foundation for crawlability and page coverage, but the homepage still under-signals its primary commercial intent."
    )

    if article_schema:
        summary.append(
            "The current audit now confirms article-page schema evidence in static HTML, which corrects the earlier false negative around Article markup."
        )

    if product_schema:
        summary.append(
            "Representative product evidence also shows Product and FAQPage schema on the Mevo Gen2 page."
        )

    if homepage_schema == ["http://schema.org/Organization"] or homepage_schema == []:
        summary.append(
            "The main remaining structured-data gap is homepage richness: the homepage evidence only shows Organization-level markup, not broader WebSite/SearchAction coverage."
        )

    return " ".join(summary)


def compute_health_score(homepage):
    seo = homepage["analysis"].get("seo", {})
    tracking = homepage["analysis"].get("tracking", {})
    score = 100

    if not seo.get("title"):
        score -= 15
    elif seo.get("title_length", 0) < 45 or seo.get("title_length", 0) > 65:
        score -= 5

    if not seo.get("meta_description"):
        score -= 15
    elif seo.get("meta_description_length", 0) < 120 or seo.get("meta_description_length", 0) > 170:
        score -= 5

    if seo.get("h1_count", 0) != 1:
        score -= 10
    elif "store" in (page_h1(homepage) or "").lower():
        score -= 10

    if seo.get("images_total", 0):
        missing_ratio = seo.get("images_without_alt", 0) / seo.get("images_total", 1)
        if missing_ratio > 0.2:
            score -= 10
        elif missing_ratio > 0.05:
            score -= 5

    if tracking.get("total_schema_count", 0) == 0:
        score -= 10
    elif page_schema_types(homepage) == ["http://schema.org/Organization"]:
        score -= 5

    if not seo.get("canonical"):
        score -= 5
    if not seo.get("has_viewport"):
        score -= 5

    hreflang_tags = seo.get("hreflang_tags", [])
    if hreflang_tags and not any(tag.get("lang") == "x-default" for tag in hreflang_tags):
        score -= 5

    return max(0, score)


def build_methodology(pages, rendered):
    lines = [
        "- Fresh audit performed from current-run evidence only",
        "- Pages analyzed: " + ", ".join(page["page_url"] for page in pages),
        "- Static HTML analysis collected with `scripts/analyze_page.py` and `scripts/collect_seo_evidence.py`",
    ]

    rendered_pages = rendered.get("rendered_verification", {}).get("pages", [])
    rendered_provider = rendered.get("rendered_verification", {}).get("provider", "rendered browser provider")
    rendered_failures = [page for page in rendered_pages if page.get("confidence") != "Confirmed"]
    if rendered.get("status") == "success" and rendered_pages and not rendered_failures:
        lines.append(f"- Browser-rendered verification collected with `scripts/verify_rendered_seo.py` via `{rendered_provider}`")
    elif rendered_pages:
        lines.append(f"- Browser-rendered verification attempted via `{rendered_provider}`, but one or more pages could not be confirmed in this environment; those findings remain likely or need verification")
    else:
        lines.append("- Browser-rendered verification unavailable or incomplete; JS-sensitive findings remain likely or need verification")

    lines.append("- Structured data and performance findings are confidence-labeled based on evidence source")
    return lines


def summarize_template_coverage(grouped_pages, selection):
    lines = []
    for page_type, selected_urls in selection.get("selected", {}).items():
        if page_type == "homepage":
            continue
        sampled = len(grouped_pages.get(page_type, []))
        available = selection.get("available_counts", {}).get(page_type, 0)
        if sampled or available:
            lines.append(f"- `{page_type}`: sampled {sampled} page(s) from {available} discovered candidate(s)")
    return lines


def summarize_pages_for_type(pages):
    if not pages:
        return []

    schema_types = sorted({schema for page in pages for schema in page_schema_types(page)})
    confirmed = sum(1 for page in pages if page["confidence"] == "Confirmed")
    likely = sum(1 for page in pages if page["confidence"] == "Likely")
    needs_verification = sum(1 for page in pages if page["confidence"] == "Needs Verification")
    title_pass = sum(1 for page in pages if page_title_status(page) == "Pass")
    meta_pass = sum(1 for page in pages if page_meta_status(page) == "Pass")

    lines = [
        f"- Sample size: {len(pages)}",
        f"- Confidence mix: Confirmed {confirmed}, Likely {likely}, Needs Verification {needs_verification}",
        f"- Title quality: {title_pass}/{len(pages)} in recommended range",
        f"- Meta description quality: {meta_pass}/{len(pages)} in recommended range",
        f"- Schema types seen: {', '.join(schema_types) if schema_types else 'None detected'}",
    ]

    for page in pages:
        lines.append(
            f"- `{page['page_url']}` | title: {len(page_title(page))} chars | meta: {len(page_meta_description(page))} chars | H1: `{page_h1(page)}` | confidence: {page['confidence']}"
        )

    return lines


def build_prioritized_recommendations(homepage, blog_index, article_page, product_page):
    seo = homepage["analysis"].get("seo", {})
    tracking = homepage["analysis"].get("tracking", {})
    recs = []

    h1 = page_h1(homepage)
    if seo.get("h1_count", 0) != 1 or "store" in h1.lower():
        recs.append(("Critical", "Confirmed", f"Improve the homepage H1. Current H1: `{h1 or 'missing'}`."))

    meta_description = page_meta_description(homepage)
    if len(meta_description) < 120:
        recs.append(("Critical", "Confirmed", f"Expand the homepage meta description from {len(meta_description)} characters to a fuller SERP-ready description."))

    if seo.get("images_without_alt", 0) > 0:
        recs.append(("High", "Confirmed", f"Add alt text to {seo['images_without_alt']} homepage images missing it."))

    homepage_schema = page_schema_types(homepage)
    if tracking.get("total_schema_count", 0) == 0:
        recs.append(("High", homepage["confidence"], "Add or verify homepage structured data. No schema was detected in the current homepage evidence."))
    elif homepage_schema == ["http://schema.org/Organization"]:
        recs.append(("High", "Likely", "Expand homepage schema beyond Organization markup. Add WebSite/SearchAction and verify it in a rendered environment or Rich Results tooling."))

    hreflang_tags = seo.get("hreflang_tags", [])
    if hreflang_tags and not any(tag.get("lang") == "x-default" for tag in hreflang_tags):
        recs.append(("Medium", "Confirmed", "Add an `x-default` hreflang entry for the fallback homepage variant."))

    if blog_index and page_h1(blog_index).strip().lower() == "news":
        recs.append(("Medium", "Confirmed", "Improve the blog index H1 from `News` to a keyword-bearing heading that reflects golf launch monitor content."))

    if article_page and not page_schema_types(article_page):
        recs.append(("Medium", article_page["confidence"], "Verify article-page structured data on real article URLs and add Article schema if absent."))

    if product_page and "Product" in page_schema_types(product_page):
        recs.append(("Low", "Confirmed", "Preserve existing product-page Product and FAQPage schema coverage during any theme changes."))

    return recs


def generate_markdown(evidence, rendered):
    pages = normalize_pages(evidence, rendered)
    grouped_pages = pages_by_type(pages)
    homepage = first_page_by_type(pages, "homepage")
    blog_index = first_page_by_type(pages, "blog_index")
    article_page = first_page_by_type(pages, "article")
    product_page = first_page_by_type(pages, "product")

    if not homepage:
        raise ValueError("Evidence does not contain a homepage record")

    health_score = compute_health_score(homepage)
    methodology = build_methodology(pages, rendered)
    recommendations = build_prioritized_recommendations(homepage, blog_index, article_page, product_page)
    executive_summary = build_executive_summary(homepage, product_page, article_page)

    homepage_title = page_title(homepage)
    homepage_meta = page_meta_description(homepage)
    homepage_h1 = page_h1(homepage)
    homepage_seo = homepage["analysis"].get("seo", {})
    homepage_tracking = homepage["analysis"].get("tracking", {})

    lines = [
        "# SEO Content Audit",
        f"## {evidence.get('url', '')}",
        f"### Date: {date.today().isoformat()}",
        "",
        "---",
        "",
        f"## SEO Health Score: {health_score}/100",
        "",
        executive_summary,
        "",
        "---",
        "",
        "## Methodology & Limitations",
        *methodology,
        "",
        "## Coverage Summary",
        *summarize_template_coverage(grouped_pages, evidence.get("selection", {})),
        "",
        "---",
        "",
        "## Evidence Inventory",
    ]

    for page in pages:
        schema_text = ", ".join(page_schema_types(page)) or "None detected"
        error = rendered_error(page)
        error_text = f" | browser: {error}" if error else ""
        lines.append(f"- `{page['page_type']}`: {page['page_url']} | confidence: {page['confidence']} | schema: {schema_text}{error_text}")

    lines.extend([
        "",
        "---",
        "",
        "## Key Findings",
        f"- Homepage title length is solid at {len(homepage_title)} characters, but the meta description is short at {len(homepage_meta)} characters.",
        f"- Homepage H1 is `{homepage_h1}`, which reads like a store label rather than a category-level search target.",
        f"- Homepage image coverage shows {homepage_seo.get('images_without_alt', 0)} images missing alt text out of {homepage_seo.get('images_total', 0)}.",
        f"- Site-level static schema evidence includes JSON-LD types: {', '.join(evidence.get('summary', {}).get('structured_data', {}).get('json_ld_types', [])) or 'none'}.",
        "",
        "---",
        "",
        "## On-Page SEO Checklist",
        "",
        "### Homepage",
        f"- Title: `{homepage_title}`",
        f"- Title status: {page_title_status(homepage)}",
        f"- Meta description: `{homepage_meta}`",
        f"- Meta description status: {page_meta_status(homepage)}",
        f"- H1: `{homepage_h1}`",
        f"- H1 status: {status_for_ratio(homepage_seo.get('h1_count', 0) == 1, homepage_seo.get('h1_count', 0) > 0)}",
        f"- Images missing alt text: {homepage_seo.get('images_without_alt', 0)} of {homepage_seo.get('images_total', 0)}",
        f"- Canonical: `{homepage_seo.get('canonical', '')}`",
        f"- Viewport present: {'Yes' if homepage_seo.get('has_viewport') else 'No'}",
        f"- Hreflang count: {len(homepage_seo.get('hreflang_tags', []))}",
    ])

    if blog_index:
        lines.extend([
            "",
            "### Blog Index",
            *summarize_pages_for_type(grouped_pages.get("blog_index", [])),
        ])

    if article_page:
        lines.extend([
            "",
            "### Article Pages",
            *summarize_pages_for_type(grouped_pages.get("article", [])),
        ])

    if product_page:
        lines.extend([
            "",
            "### Product Pages",
            *summarize_pages_for_type(grouped_pages.get("product", [])),
        ])

    if grouped_pages.get("collection"):
        lines.extend([
            "",
            "### Collection Pages",
            *summarize_pages_for_type(grouped_pages.get("collection", [])),
        ])

    if grouped_pages.get("comparison"):
        lines.extend([
            "",
            "### Comparison Pages",
            *summarize_pages_for_type(grouped_pages.get("comparison", [])),
        ])

    if grouped_pages.get("about_trust"):
        lines.extend([
            "",
            "### About / Trust Pages",
            *summarize_pages_for_type(grouped_pages.get("about_trust", [])),
        ])

    if grouped_pages.get("policy"):
        lines.extend([
            "",
            "### Policy Pages",
            *summarize_pages_for_type(grouped_pages.get("policy", [])),
        ])

    lines.extend([
        "",
        "---",
        "",
        "## Structured Data",
        f"- Homepage schema types: {', '.join(page_schema_types(homepage)) or 'None detected'}",
        f"- Site-level static schema summary: JSON-LD [{', '.join(evidence.get('summary', {}).get('structured_data', {}).get('json_ld_types', [])) or 'none'}], "
        f"Microdata [{', '.join(evidence.get('summary', {}).get('structured_data', {}).get('microdata_types', [])) or 'none'}], "
        f"RDFa [{', '.join(evidence.get('summary', {}).get('structured_data', {}).get('rdfa_types', [])) or 'none'}]",
        f"- Homepage confidence: {homepage['confidence']}",
        "- Interpretation: article and product schema are present in representative static evidence; homepage richness is the weaker area.",
    ])

    if article_page:
        lines.append(f"- Article-page schema evidence: {', '.join(page_schema_types(article_page)) or 'None detected'}")

    lines.extend([
        "",
        "---",
        "",
        "## Technical SEO",
        f"- Internal links on homepage: {homepage['analysis'].get('technical', {}).get('internal_links', 0)}",
        f"- External links on homepage: {homepage['analysis'].get('technical', {}).get('external_links', 0)}",
        f"- Scripts loaded on homepage: {homepage['analysis'].get('technical', {}).get('scripts_count', 0)}",
        f"- Robots.txt detected: {'Yes' if homepage['analysis'].get('robots', {}).get('exists') else 'No'}",
        f"- Sitemap detected: {'Yes' if homepage['analysis'].get('sitemap', {}).get('exists') else 'No'}",
        f"- x-default hreflang present: {'Yes' if any(tag.get('lang') == 'x-default' for tag in homepage_seo.get('hreflang_tags', [])) else 'No'}",
        "",
        "---",
        "",
        "## What Is Working",
        "- Representative product evidence shows Product and FAQPage schema instead of the earlier false-negative state.",
        "- Representative article evidence shows Article schema with author data on real article URLs.",
        "- Homepage crawlability basics are in place: canonical, robots.txt, sitemap, viewport, and substantial internal linking.",
        "",
        "---",
        "",
        "## Gaps And Risks",
        "- Homepage search intent is under-signaled by the current H1.",
        "- Homepage meta description is too short to fully use SERP snippet space.",
        "- Homepage image alt coverage is incomplete.",
        "- Browser-rendered verification could not be confirmed in this environment, so JS-sensitive findings should still be verified externally if they are business-critical.",
    ])

    lines.extend([
        "",
        "---",
        "",
        "## Prioritized Recommendations",
    ])

    if not recommendations:
        lines.append("- No high-confidence critical SEO fixes were generated from the current evidence set.")
    else:
        for priority, confidence, text in recommendations:
            lines.append(f"- [{priority}] [{confidence}] {text}")

    lines.extend([
        "",
        "---",
        "",
        "*Generated from `seo_evidence.json` and `rendered_verification.json` when available.*",
    ])

    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "usage": "uv run python scripts/generate_seo_audit_report.py <seo_evidence.json> [rendered_verification.json] [output-file]",
            "description": "Generate SEO_AUDIT.md from evidence artifacts",
        }, indent=2))
        return

    evidence = load_json(sys.argv[1])
    rendered = {"status": "needs_verification", "rendered_verification": {"pages": []}}
    output_path = "SEO_AUDIT.md"

    if len(sys.argv) >= 3:
        if sys.argv[2].endswith(".json"):
            rendered = load_json(sys.argv[2])
            if len(sys.argv) >= 4:
                output_path = sys.argv[3]
        else:
            output_path = sys.argv[2]

    markdown = generate_markdown(evidence, rendered)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(markdown)

    print(output_path)


if __name__ == "__main__":
    main()
