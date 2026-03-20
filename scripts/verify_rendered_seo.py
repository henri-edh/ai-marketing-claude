#!/usr/bin/env python3
"""
Browser-rendered SEO verification using pluggable browser providers.

This script verifies critical SEO findings on representative pages after the
initial static HTML pass. It is intentionally conservative: if no rendered
provider is available or a page cannot be verified, the result is marked as
needing verification rather than inferred.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

try:
    from analyze_page import ImprovedMarketingParser
except ImportError:  # pragma: no cover - import path differs in tests
    from scripts.analyze_page import ImprovedMarketingParser

try:
    from collect_seo_evidence import collect_site_evidence
except ImportError:  # pragma: no cover - import path differs in tests
    from scripts.collect_seo_evidence import collect_site_evidence


BROWSERLESS_PROVIDER = "browserless"
LOCAL_PLAYWRIGHT_PROVIDER = "local-playwright-cli"
DEFAULT_PROVIDER = BROWSERLESS_PROVIDER
SUPPORTED_PROVIDERS = (BROWSERLESS_PROVIDER, LOCAL_PLAYWRIGHT_PROVIDER)

BROWSERLESS_FUNCTION = """
export default async ({ page, context }) => {
  await page.goto(context.url, {
    waitUntil: "domcontentloaded",
    timeout: context.gotoTimeoutMs || 45000
  });
  await new Promise(resolve => setTimeout(resolve, context.waitTimeMs || 1500));

  const data = await page.evaluate(() => ({
    title: document.title,
    canonical: document.querySelector('link[rel="canonical"]')?.href || '',
    metaDescription: document.querySelector('meta[name="description"]')?.content || '',
    viewport: document.querySelector('meta[name="viewport"]')?.content || '',
    h1: Array.from(document.querySelectorAll('h1')).map(el => el.textContent.trim()).filter(Boolean),
    h2Count: document.querySelectorAll('h2').length,
    h3Count: document.querySelectorAll('h3').length,
    jsonLdScripts: Array.from(document.querySelectorAll('script[type="application/ld+json"]'))
      .map(el => el.textContent.trim())
      .filter(Boolean),
    microdataTypes: Array.from(document.querySelectorAll('[itemscope][itemtype]'))
      .map(el => el.getAttribute('itemtype'))
      .filter(Boolean),
    rdfaTypes: Array.from(document.querySelectorAll('[typeof]'))
      .flatMap(el => (el.getAttribute('typeof') || '').split(/\\s+/))
      .filter(Boolean)
  }));

  return {
    data,
    type: "application/json"
  };
};
""".strip()


def get_pwcli_path():
    codex_home = os.environ.get("CODEX_HOME", os.path.expanduser("~/.codex"))
    pwcli = os.path.join(codex_home, "skills", "playwright", "scripts", "playwright_cli.sh")
    if os.path.exists(pwcli):
        return pwcli
    return None


def parse_cli_json(output):
    output = output.strip()
    if not output:
        return None

    if output.startswith("### Result"):
        lines = output.splitlines()
        for index, line in enumerate(lines):
            if line.strip() == "### Result" and index + 1 < len(lines):
                candidate = lines[index + 1].strip()
                try:
                    parsed = json.loads(candidate)
                    if isinstance(parsed, str):
                        return json.loads(parsed)
                    return parsed
                except json.JSONDecodeError:
                    continue

    parsed = json.loads(output)
    if isinstance(parsed, str):
        return json.loads(parsed)
    return parsed


def extract_json_ld_types_from_text(script_texts):
    parser = ImprovedMarketingParser()
    types = []
    items = []
    for script_text in script_texts:
        text = (script_text or "").strip()
        if not text:
            continue
        try:
            payload = json.loads(text)
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        types.extend(parser._extract_json_ld_types(payload))
        summary = parser._summarize_json_ld_item(payload)
        if summary:
            items.append(summary)
    return {
        "types": sorted(set(types)),
        "items": items,
    }


def build_rendered_payload(raw):
    schema = extract_json_ld_types_from_text(raw.get("jsonLdScripts", []))
    return {
        "title": raw.get("title", ""),
        "canonical": raw.get("canonical", ""),
        "meta_description": raw.get("metaDescription", ""),
        "viewport": raw.get("viewport", ""),
        "headings": {
            "h1": raw.get("h1", []),
            "h2_count": raw.get("h2Count", 0),
            "h3_count": raw.get("h3Count", 0),
        },
        "structured_data": {
            "json_ld_types": schema["types"],
            "json_ld_items": schema["items"],
            "microdata_types": sorted(set(raw.get("microdataTypes", []))),
            "rdfa_types": sorted(set(raw.get("rdfaTypes", []))),
        },
        "evidence_source": "browser_rendered_dom",
    }


class BaseVerifier:
    provider_name = "base"

    def is_available(self):
        raise NotImplementedError

    def open_and_capture(self, url):
        raise NotImplementedError

    def close(self):
        return None


class LocalPlaywrightVerifier(BaseVerifier):
    provider_name = LOCAL_PLAYWRIGHT_PROVIDER

    def __init__(self, runner=None, session=None):
        self.runner = runner or subprocess.run
        self.session = session or f"seo-{uuid.uuid4().hex[:10]}"
        self.pwcli = get_pwcli_path()

    def is_available(self):
        return bool(self.pwcli and shutil.which("npx"))

    def run_cli(self, *args, timeout=90):
        if not self.is_available():
            raise RuntimeError("Playwright CLI wrapper or npx is not available")

        cmd = ["/bin/bash", self.pwcli, "--session", self.session, *args]
        return self.runner(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    def eval_json(self, expression):
        result = self.run_cli("eval", f"JSON.stringify({expression})")
        return parse_cli_json(result.stdout)

    def open_and_capture(self, url):
        self.run_cli("open", url)
        self.run_cli("run-code", "await page.waitForLoadState('domcontentloaded'); await page.waitForTimeout(1500)")
        return self.eval_json(
            """({
                title: document.title,
                canonical: document.querySelector('link[rel="canonical"]')?.href || '',
                metaDescription: document.querySelector('meta[name="description"]')?.content || '',
                viewport: document.querySelector('meta[name="viewport"]')?.content || '',
                h1: Array.from(document.querySelectorAll('h1')).map(el => el.textContent.trim()).filter(Boolean),
                h2Count: document.querySelectorAll('h2').length,
                h3Count: document.querySelectorAll('h3').length,
                jsonLdScripts: Array.from(document.querySelectorAll('script[type="application/ld+json"]'))
                    .map(el => el.textContent.trim())
                    .filter(Boolean),
                microdataTypes: Array.from(document.querySelectorAll('[itemscope][itemtype]'))
                    .map(el => el.getAttribute('itemtype'))
                    .filter(Boolean),
                rdfaTypes: Array.from(document.querySelectorAll('[typeof]'))
                    .flatMap(el => (el.getAttribute('typeof') || '').split(/\\s+/))
                    .filter(Boolean)
            })"""
        )

    def close(self):
        if self.is_available():
            try:
                self.run_cli("close", timeout=30)
            except Exception:
                pass


class BrowserlessVerifier(BaseVerifier):
    provider_name = BROWSERLESS_PROVIDER

    def __init__(self, opener=None):
        self.opener = opener or urllib.request.urlopen
        self.token = os.environ.get("BROWSERLESS_TOKEN", "").strip()
        self.base_url = os.environ.get("BROWSERLESS_BASE_URL", "https://production-sfo.browserless.io").rstrip("/")
        self.proxy_mode = os.environ.get("BROWSERLESS_PROXY", "").strip()
        self.proxy_country = os.environ.get("BROWSERLESS_PROXY_COUNTRY", "").strip()
        self.wait_time_ms = int(os.environ.get("SEO_RENDER_WAIT_MS", "1500"))
        self.goto_timeout_ms = int(os.environ.get("SEO_RENDER_GOTO_TIMEOUT_MS", "45000"))

    def is_available(self):
        return bool(self.token)

    def build_endpoint(self):
        query = [("token", self.token)]
        if self.proxy_mode:
            query.append(("proxy", self.proxy_mode))
        if self.proxy_country:
            query.append(("proxyCountry", self.proxy_country))
        return f"{self.base_url}/function?{urllib.parse.urlencode(query)}"

    def normalize_response(self, payload):
        if isinstance(payload, dict) and "data" in payload and isinstance(payload["data"], dict):
            return payload["data"]
        if isinstance(payload, dict):
            return payload
        raise ValueError("Browserless returned a non-object JSON response")

    def open_and_capture(self, url):
        endpoint = self.build_endpoint()
        body = json.dumps({
            "code": BROWSERLESS_FUNCTION,
            "context": {
                "url": url,
                "waitTimeMs": self.wait_time_ms,
                "gotoTimeoutMs": self.goto_timeout_ms,
            },
        }).encode("utf-8")
        request = urllib.request.Request(
            endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self.opener(request, timeout=max(60, int(self.goto_timeout_ms / 1000) + 15)) as response:
                raw = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Browserless HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Browserless request failed: {exc.reason}") from exc

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Browserless returned invalid JSON: {raw[:200]}") from exc

        return self.normalize_response(payload)


def create_verifier(provider_name=None):
    provider_name = (provider_name or os.environ.get("SEO_RENDER_PROVIDER", DEFAULT_PROVIDER)).strip().lower()
    if provider_name == BROWSERLESS_PROVIDER:
        return BrowserlessVerifier()
    if provider_name == LOCAL_PLAYWRIGHT_PROVIDER:
        return LocalPlaywrightVerifier()
    raise ValueError(f"Unsupported provider: {provider_name}")


def verify_pages(pages, verifier=None, provider_name=None):
    verifier = verifier or create_verifier(provider_name)
    provider_label = getattr(verifier, "provider_name", "custom")
    if not verifier.is_available():
        return {
            "status": "needs_verification",
            "message": f"Rendered provider `{provider_label}` is not available",
            "pages": [],
        }

    verified_pages = []
    try:
        for page in pages:
            analysis = page.get("analysis", {})
            final_url = analysis.get("url_analysis", {}).get("final_url", page.get("requested_url", ""))
            try:
                raw = verifier.open_and_capture(final_url)
                verified_pages.append({
                    "page_type": page.get("page_type", "other"),
                    "page_url": final_url,
                    "confidence": "Confirmed",
                    "verification": {
                        **build_rendered_payload(raw),
                        "provider": provider_label,
                    },
                })
            except Exception as exc:
                verified_pages.append({
                    "page_type": page.get("page_type", "other"),
                    "page_url": final_url,
                    "confidence": "Needs Verification",
                    "verification": {
                        "evidence_source": "browser_rendered_dom",
                        "provider": provider_label,
                        "error": str(exc),
                    },
                })
    finally:
        verifier.close()

    return {
        "status": "success",
        "message": "",
        "provider": provider_label,
        "pages": verified_pages,
    }


def load_evidence(arg):
    if os.path.exists(arg):
        with open(arg, "r", encoding="utf-8") as handle:
            return json.load(handle)
    if arg.endswith(".json"):
        raise FileNotFoundError(f"Evidence file not found: {arg}")
    return collect_site_evidence(arg)


def verify_evidence(evidence, provider_name=None):
    pages = evidence.get("pages", [])
    verification = verify_pages(pages, provider_name=provider_name)
    return {
        "url": evidence.get("url", ""),
        "status": verification["status"],
        "message": verification["message"],
        "static_summary": evidence.get("summary", {}),
        "rendered_verification": verification,
    }


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Verify SEO findings in a browser-rendered DOM using a pluggable provider",
    )
    parser.add_argument("source", help="seo_evidence.json path or site URL")
    parser.add_argument("output_file", nargs="?", help="Optional JSON output path")
    parser.add_argument(
        "--provider",
        choices=SUPPORTED_PROVIDERS,
        default=None,
        help="Rendered browser provider to use",
    )
    return parser.parse_args(argv)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "usage": "uv run python scripts/verify_rendered_seo.py <seo_evidence.json|url> [output-file] [--provider local-playwright-cli|browserless]",
            "description": "Verify SEO findings in a browser-rendered DOM using a pluggable provider",
        }, indent=2))
        return

    args = parse_args(sys.argv[1:])
    evidence = load_evidence(args.source)
    result = verify_evidence(evidence, provider_name=args.provider)
    payload = json.dumps(result, indent=2, default=str)

    if args.output_file:
        with open(args.output_file, "w", encoding="utf-8") as handle:
            handle.write(payload)

    print(payload)


if __name__ == "__main__":
    main()
