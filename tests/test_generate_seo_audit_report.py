import unittest

from scripts.generate_seo_audit_report import generate_markdown


class GenerateSeoAuditReportTests(unittest.TestCase):
    def test_generate_markdown_uses_rendered_article_evidence(self):
        evidence = {
            "url": "https://example.com",
            "summary": {
                "structured_data": {
                    "json_ld_types": ["WebSite"],
                    "microdata_types": [],
                    "rdfa_types": [],
                }
            },
            "pages": [
                {
                    "page_type": "homepage",
                    "requested_url": "https://example.com",
                    "analysis": {
                        "seo": {
                            "title": "Example Home",
                            "title_length": 12,
                            "meta_description": "Short description",
                            "meta_description_length": 17,
                            "h1_count": 1,
                            "h1_text": ["Example Store"],
                            "images_without_alt": 2,
                            "images_total": 10,
                            "canonical": "https://example.com/",
                            "has_viewport": True,
                        },
                        "tracking": {
                            "total_schema_count": 0,
                            "json_ld_schema_types": [],
                            "microdata_types": [],
                            "rdfa_types": [],
                        },
                        "technical": {
                            "internal_links": 12,
                            "external_links": 3,
                            "scripts_count": 9,
                        },
                        "robots": {"exists": True},
                        "sitemap": {"exists": True},
                        "url_analysis": {"final_url": "https://example.com"},
                    },
                },
                {
                    "page_type": "article",
                    "requested_url": "https://example.com/blogs/news/test-article",
                    "analysis": {
                        "seo": {
                            "title": "Test Article",
                            "meta_description": "Article description",
                            "h1_count": 1,
                            "h1_text": ["Test Article"],
                        },
                        "tracking": {
                            "total_schema_count": 0,
                            "json_ld_schema_types": [],
                            "microdata_types": [],
                            "rdfa_types": [],
                        },
                        "url_analysis": {"final_url": "https://example.com/blogs/news/test-article"},
                    },
                },
            ],
        }

        rendered = {
            "status": "success",
            "rendered_verification": {
                "pages": [
                    {
                        "page_url": "https://example.com/blogs/news/test-article",
                        "verification": {
                            "title": "Test Article",
                            "meta_description": "Article description",
                            "headings": {"h1": ["Test Article"]},
                            "structured_data": {
                                "json_ld_types": ["Article"],
                                "microdata_types": [],
                                "rdfa_types": [],
                            },
                        },
                    }
                ]
            },
        }

        markdown = generate_markdown(evidence, rendered)

        self.assertIn("## Evidence Inventory", markdown)
        self.assertIn("https://example.com/blogs/news/test-article", markdown)
        self.assertIn("Article-page schema evidence: Article", markdown)
        self.assertIn("[Critical] [Confirmed] Expand the homepage meta description", markdown)


if __name__ == "__main__":
    unittest.main()
