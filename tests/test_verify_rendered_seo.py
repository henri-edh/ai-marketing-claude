import json
import os
import unittest
from unittest.mock import patch

from scripts.verify_rendered_seo import (
    BrowserlessVerifier,
    build_rendered_payload,
    create_verifier,
    extract_json_ld_types_from_text,
    load_evidence,
    parse_cli_json,
    verify_pages,
)


class StubVerifier:
    def __init__(self, payload):
        self.payload = payload
        self.closed = False

    def is_available(self):
        return True

    def open_and_capture(self, _url):
        return self.payload

    def close(self):
        self.closed = True


class UnavailableVerifier:
    def is_available(self):
        return False


class FailingVerifier(StubVerifier):
    def open_and_capture(self, _url):
        raise RuntimeError("browser navigation failed")


class BrowserlessOpener:
    def __init__(self, payload):
        self.payload = payload

    def __call__(self, request, timeout=0):
        self.request = request
        self.timeout = timeout
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class VerifyRenderedSeoTests(unittest.TestCase):
    def test_parse_cli_json(self):
        self.assertEqual(parse_cli_json('{"ok": true}\n'), {"ok": True})

    def test_extract_json_ld_types_from_text(self):
        result = extract_json_ld_types_from_text(
            [
                json.dumps(
                    {
                        "@context": "https://schema.org",
                        "@type": ["Article", "NewsArticle"],
                        "headline": "Rendered article",
                        "author": {"@type": "Person", "name": "Cody Hansen"},
                    }
                )
            ]
        )

        self.assertEqual(result["types"], ["Article", "NewsArticle"])
        self.assertEqual(result["items"][0]["author"], "Cody Hansen")

    def test_build_rendered_payload(self):
        payload = build_rendered_payload(
            {
                "title": "Rendered Title",
                "canonical": "https://example.com/article",
                "metaDescription": "Rendered description",
                "viewport": "width=device-width,initial-scale=1",
                "h1": ["Article headline"],
                "h2Count": 2,
                "h3Count": 1,
                "jsonLdScripts": [
                    json.dumps(
                        {
                            "@context": "https://schema.org",
                            "@type": "Article",
                            "headline": "Article headline",
                        }
                    )
                ],
                "microdataTypes": ["https://schema.org/Article"],
                "rdfaTypes": ["Article"],
            }
        )

        self.assertEqual(payload["structured_data"]["json_ld_types"], ["Article"])
        self.assertEqual(payload["structured_data"]["microdata_types"], ["https://schema.org/Article"])
        self.assertEqual(payload["headings"]["h1"], ["Article headline"])

    def test_verify_pages_returns_rendered_confirmation(self):
        verifier = StubVerifier(
            {
                "title": "Rendered Title",
                "canonical": "https://example.com/",
                "metaDescription": "Description",
                "viewport": "width=device-width,initial-scale=1",
                "h1": ["Homepage"],
                "h2Count": 4,
                "h3Count": 1,
                "jsonLdScripts": [json.dumps({"@type": "WebSite"})],
                "microdataTypes": [],
                "rdfaTypes": [],
            }
        )

        result = verify_pages(
            [
                {
                    "page_type": "homepage",
                    "requested_url": "https://example.com",
                    "analysis": {"url_analysis": {"final_url": "https://example.com"}},
                }
            ],
            verifier=verifier,
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["pages"][0]["confidence"], "Confirmed")
        self.assertEqual(result["provider"], "custom")
        self.assertEqual(
            result["pages"][0]["verification"]["structured_data"]["json_ld_types"],
            ["WebSite"],
        )
        self.assertTrue(verifier.closed)

    def test_verify_pages_handles_unavailable_playwright(self):
        result = verify_pages([], verifier=UnavailableVerifier())
        self.assertEqual(result["status"], "needs_verification")

    def test_load_evidence_raises_for_missing_json_file(self):
        with self.assertRaises(FileNotFoundError):
            load_evidence("missing-evidence.json")

    def test_verify_pages_downgrades_failed_browser_verification(self):
        result = verify_pages(
            [
                {
                    "page_type": "homepage",
                    "requested_url": "https://example.com",
                    "analysis": {"url_analysis": {"final_url": "https://example.com"}},
                }
            ],
            verifier=FailingVerifier({}),
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["pages"][0]["confidence"], "Needs Verification")
        self.assertIn("browser navigation failed", result["pages"][0]["verification"]["error"])

    def test_create_verifier_browserless(self):
        with patch.dict(os.environ, {"BROWSERLESS_TOKEN": "token-123"}, clear=False):
            verifier = create_verifier("browserless")
        self.assertIsInstance(verifier, BrowserlessVerifier)

    def test_browserless_verifier_normalizes_data_response(self):
        opener = BrowserlessOpener(
            {
                "data": {
                    "title": "Rendered via Browserless",
                    "canonical": "https://example.com/page",
                    "metaDescription": "Description",
                    "viewport": "width=device-width,initial-scale=1",
                    "h1": ["Heading"],
                    "h2Count": 1,
                    "h3Count": 0,
                    "jsonLdScripts": [],
                    "microdataTypes": [],
                    "rdfaTypes": [],
                }
            }
        )
        with patch.dict(os.environ, {"BROWSERLESS_TOKEN": "token-123"}, clear=False):
            verifier = BrowserlessVerifier(opener=opener)
            payload = verifier.open_and_capture("https://example.com/page")

        self.assertEqual(payload["title"], "Rendered via Browserless")
        self.assertIn("token=token-123", opener.request.full_url)
        self.assertEqual(opener.request.get_method(), "POST")


if __name__ == "__main__":
    unittest.main()
