#!/usr/bin/env python3
"""
Site-level SEO evidence collector.

Builds a representative page set for a site-level SEO audit so the report can
differentiate homepage, product, blog index, and article findings.
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
import ssl
from urllib.parse import urljoin, urlparse

try:
    from analyze_page import analyze
except ImportError:  # pragma: no cover - import path differs in tests
    from scripts.analyze_page import analyze


PAGE_TYPES = (
    "product",
    "collection",
    "comparison",
    "blog_index",
    "article",
    "about_trust",
    "policy",
)

PROFILE_QUOTAS = {
    "standard": {
        "product": 2,
        "collection": 1,
        "comparison": 1,
        "blog_index": 1,
        "article": 3,
        "about_trust": 1,
        "policy": 1,
    },
    "deep": {
        "product": 4,
        "collection": 2,
        "comparison": 2,
        "blog_index": 2,
        "article": 6,
        "about_trust": 2,
        "policy": 2,
    },
}

ABOUT_TRUST_PATTERNS = (
    "/about",
    "/about-us",
    "/contact",
    "/pages/about",
    "/pages/contact",
    "/pages/our-story",
    "/pages/why-",
    "/pages/trust",
)

POLICY_PATTERNS = (
    "/privacy",
    "/privacy-policy",
    "/terms",
    "/terms-of-service",
    "/shipping",
    "/returns",
    "/refund",
    "/warranty",
    "/legal",
    "/policies/",
)


def normalize_url(url):
    if not url.startswith("http"):
        url = "https://" + url
    return url


def fetch_text(url):
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    try:
        response = urllib.request.urlopen(req, timeout=20, context=ctx)
        return response.read().decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError, ssl.SSLError, TimeoutError):
        return None


def canonicalize_internal_url(base_url, href):
    if not href:
        return None
    if href.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None

    absolute = urljoin(base_url, href)
    parsed_base = urlparse(base_url)
    parsed_url = urlparse(absolute)

    if parsed_url.scheme not in ("http", "https"):
        return None

    base_host = parsed_base.netloc.replace("www.", "")
    target_host = parsed_url.netloc.replace("www.", "")
    if target_host and target_host != base_host:
        return None

    path = parsed_url.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    return f"{parsed_url.scheme}://{parsed_url.netloc}{path}"


def classify_page(url):
    path = urlparse(url).path.rstrip("/")

    if path in ("", "/"):
        return "homepage"
    if path.startswith("/products/"):
        return "product"
    if path.startswith("/collections/"):
        return "collection"
    if any(token in path for token in ("/compare", "/comparison", "/vs-", "-vs-", "/vs/")):
        return "comparison"
    if path in ("/blog", "/blogs") or path.startswith("/blog/"):
        return "blog_index"
    if path.startswith("/blogs/"):
        segments = [segment for segment in path.split("/") if segment]
        if len(segments) >= 3:
            return "article"
        return "blog_index"
    if path.startswith("/articles/"):
        return "article"
    if any(path == pattern or path.startswith(pattern + "/") for pattern in ABOUT_TRUST_PATTERNS):
        return "about_trust"
    if any(path == pattern or path.startswith(pattern) for pattern in POLICY_PATTERNS):
        return "policy"
    return "other"


def discover_candidates(base_url, links):
    candidates = {page_type: [] for page_type in PAGE_TYPES}

    seen = set()
    for href in links:
        absolute = canonicalize_internal_url(base_url, href)
        if not absolute or absolute in seen:
            continue
        seen.add(absolute)

        page_type = classify_page(absolute)
        if page_type in candidates:
            candidates[page_type].append(absolute)

    return candidates


def extract_sitemap_urls(sitemap_url, max_urls=200):
    content = fetch_text(sitemap_url)
    if not content:
        return []

    sitemap_entries = re.findall(r"<sitemap>.*?<loc>(.*?)</loc>.*?</sitemap>", content, re.IGNORECASE | re.DOTALL)
    if sitemap_entries:
        urls = []
        for child_sitemap in sitemap_entries[:10]:
            urls.extend(extract_sitemap_urls(child_sitemap.strip(), max_urls=max_urls))
            if len(urls) >= max_urls:
                break
        return urls[:max_urls]

    page_urls = re.findall(r"<loc>(.*?)</loc>", content, re.IGNORECASE | re.DOTALL)
    cleaned = []
    for page_url in page_urls:
        page_url = page_url.strip()
        if page_url and page_url not in cleaned:
            cleaned.append(page_url)
        if len(cleaned) >= max_urls:
            break
    return cleaned


def merge_candidates(*candidate_sets):
    merged = {page_type: [] for page_type in PAGE_TYPES}

    for candidate_set in candidate_sets:
        for key in merged:
            for url in candidate_set.get(key, []):
                if url not in merged[key]:
                    merged[key].append(url)

    return merged


def prioritize_candidates(candidates, homepage_url):
    homepage_host = urlparse(homepage_url).netloc

    def sort_key(url):
        path = urlparse(url).path
        depth = len([segment for segment in path.split("/") if segment])
        same_host = 0 if urlparse(url).netloc == homepage_host else 1

        article_priority = 5
        if path.startswith("/blogs/news/"):
            article_priority = 0
        elif path.startswith("/blogs/blogs/"):
            article_priority = 1
        elif path.startswith("/blogs/videos/"):
            article_priority = 2
        elif path.startswith("/blogs/support/"):
            article_priority = 3

        product_priority = 1
        if any(term in path for term in ("/products/mevo-gen2", "/products/mevo-plus", "/products/flightscope-x3c")):
            product_priority = 0

        collection_priority = 0 if "/collections/" in path else 1
        comparison_priority = 0 if any(token in path for token in ("/compare", "/comparison", "/vs-", "-vs-", "/vs/")) else 1
        trust_priority = 0 if any(token in path for token in ("/about", "/contact", "/trust")) else 1
        policy_priority = 0 if any(token in path for token in ("/privacy", "/terms", "/returns", "/shipping")) else 1

        return (
            same_host,
            article_priority,
            product_priority,
            collection_priority,
            comparison_priority,
            trust_priority,
            policy_priority,
            depth,
            len(path),
            url,
        )

    return {
        key: sorted(urls, key=sort_key)
        for key, urls in candidates.items()
    }


def quotas_for_profile(profile):
    if profile not in PROFILE_QUOTAS:
        raise ValueError(f"Unknown profile: {profile}")
    return PROFILE_QUOTAS[profile]


def pick_representative_pages(base_url, homepage_result, profile="standard", max_sitemap_urls=200):
    links = homepage_result["analysis"].get("links_found", [])
    homepage_candidates = discover_candidates(base_url, links)

    sitemap_urls = []
    for sitemap_url in homepage_result["analysis"].get("robots", {}).get("sitemap_urls", []):
        sitemap_urls.extend(extract_sitemap_urls(sitemap_url, max_urls=max_sitemap_urls))

    sitemap_candidates = discover_candidates(base_url, sitemap_urls)
    candidates = prioritize_candidates(
        merge_candidates(homepage_candidates, sitemap_candidates),
        homepage_result["analysis"]["url_analysis"]["final_url"],
    )
    quotas = quotas_for_profile(profile)

    selected = {
        "homepage": homepage_result["analysis"]["url_analysis"]["final_url"],
    }
    for page_type in PAGE_TYPES:
        selected[page_type] = candidates[page_type][:quotas.get(page_type, 0)]

    return {
        "profile": profile,
        "selected": selected,
        "sources": {
            "homepage_links": homepage_candidates,
            "sitemap": sitemap_candidates,
        },
        "candidates": candidates,
        "available_counts": {key: len(urls) for key, urls in candidates.items()},
        "selected_counts": {
            key: (1 if key == "homepage" else len(urls))
            for key, urls in selected.items()
        },
    }


def summarize_pages(page_results):
    summary = {
        "analyzed_urls": [],
        "by_type": {},
        "sampled_counts": {},
        "structured_data": {
            "json_ld_types": [],
            "microdata_types": [],
            "rdfa_types": [],
        },
    }

    json_ld_types = set()
    microdata_types = set()
    rdfa_types = set()

    for page in page_results:
        page_type = page["page_type"]
        analysis = page["analysis"]
        tracking = analysis.get("tracking", {})
        final_url = analysis.get("url_analysis", {}).get("final_url", page["requested_url"])

        summary["analyzed_urls"].append(final_url)
        summary["by_type"].setdefault(page_type, []).append(final_url)

        json_ld_types.update(tracking.get("json_ld_schema_types", []))
        microdata_types.update(tracking.get("microdata_types", []))
        rdfa_types.update(tracking.get("rdfa_types", []))

    summary["sampled_counts"] = {
        page_type: len(urls)
        for page_type, urls in summary["by_type"].items()
    }
    summary["structured_data"]["json_ld_types"] = sorted(json_ld_types)
    summary["structured_data"]["microdata_types"] = sorted(microdata_types)
    summary["structured_data"]["rdfa_types"] = sorted(rdfa_types)

    return summary


def collect_site_evidence(url, profile="standard", max_sitemap_urls=200):
    normalized_url = normalize_url(url)
    homepage_result = analyze(normalized_url)
    if homepage_result.get("status") != "success":
        return homepage_result

    selection = pick_representative_pages(
        normalized_url,
        homepage_result,
        profile=profile,
        max_sitemap_urls=max_sitemap_urls,
    )
    pages = [
        {
            "page_type": "homepage",
            "requested_url": normalized_url,
            "analysis": homepage_result["analysis"],
        }
    ]

    for page_type in PAGE_TYPES:
        for candidate_url in selection["selected"][page_type]:
            result = analyze(candidate_url)
            pages.append({
                "page_type": page_type,
                "requested_url": candidate_url,
                "status": result.get("status", "error"),
                "analysis": result.get("analysis", {}),
                "message": result.get("message", ""),
            })

    return {
        "url": normalized_url,
        "status": "success",
        "profile": profile,
        "selection": selection,
        "pages": pages,
        "summary": summarize_pages(pages),
    }


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Collect representative page evidence for a site-level SEO audit",
    )
    parser.add_argument("url", help="Site URL to audit")
    parser.add_argument("output_file", nargs="?", help="Optional JSON output path")
    parser.add_argument(
        "--profile",
        choices=sorted(PROFILE_QUOTAS.keys()),
        default="standard",
        help="Sampling profile to use for page selection",
    )
    parser.add_argument(
        "--max-sitemap-urls",
        type=int,
        default=200,
        help="Maximum sitemap URLs to inspect while building candidates",
    )
    return parser.parse_args(argv)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "usage": "uv run python scripts/collect_seo_evidence.py <url> [output-file] [--profile standard|deep] [--max-sitemap-urls N]",
            "description": "Collect representative page evidence for a site-level SEO audit",
        }, indent=2))
        return

    args = parse_args(sys.argv[1:])

    result = collect_site_evidence(
        args.url,
        profile=args.profile,
        max_sitemap_urls=args.max_sitemap_urls,
    )
    payload = json.dumps(result, indent=2, default=str)

    if args.output_file:
        with open(args.output_file, "w", encoding="utf-8") as handle:
            handle.write(payload)

    print(payload)


if __name__ == "__main__":
    main()
