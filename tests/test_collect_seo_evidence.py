import unittest
from unittest.mock import patch

from scripts.collect_seo_evidence import (
    classify_page,
    discover_candidates,
    extract_sitemap_urls,
    merge_candidates,
    pick_representative_pages,
    quotas_for_profile,
)


class CollectSeoEvidenceTests(unittest.TestCase):
    def test_classify_page_distinguishes_blog_index_and_article(self):
        self.assertEqual(classify_page("https://example.com/"), "homepage")
        self.assertEqual(classify_page("https://example.com/products/mevo-gen2"), "product")
        self.assertEqual(classify_page("https://example.com/collections/launch-monitors"), "collection")
        self.assertEqual(classify_page("https://example.com/pages/about"), "about_trust")
        self.assertEqual(classify_page("https://example.com/policies/privacy-policy"), "policy")
        self.assertEqual(classify_page("https://example.com/pages/mevo-vs-trackman"), "comparison")
        self.assertEqual(classify_page("https://example.com/blogs/news"), "blog_index")
        self.assertEqual(classify_page("https://example.com/blogs/news/how-launch-monitors-work"), "article")

    def test_discover_candidates_only_keeps_internal_urls_by_type(self):
        candidates = discover_candidates(
            "https://example.com",
            [
                "/products/mevo-gen2",
                "/collections/launch-monitors",
                "/pages/about",
                "https://example.com/blogs/news",
                "https://example.com/blogs/news/how-launch-monitors-work",
                "mailto:test@example.com",
                "https://external.example.org/blog",
            ],
        )

        self.assertEqual(candidates["product"], ["https://example.com/products/mevo-gen2"])
        self.assertEqual(candidates["collection"], ["https://example.com/collections/launch-monitors"])
        self.assertEqual(candidates["about_trust"], ["https://example.com/pages/about"])
        self.assertEqual(candidates["blog_index"], ["https://example.com/blogs/news"])
        self.assertEqual(
            candidates["article"],
            ["https://example.com/blogs/news/how-launch-monitors-work"],
        )

    def test_pick_representative_pages_prefers_real_article_urls(self):
        homepage_result = {
            "analysis": {
                "links_found": [
                    "/products/mevo-gen2",
                    "/blogs/news",
                    "/blogs/news/how-launch-monitors-work",
                    "/blogs/news/understanding-spin-rate",
                ],
                "url_analysis": {
                    "final_url": "https://example.com",
                },
                "robots": {
                    "sitemap_urls": []
                },
            }
        }

        selection = pick_representative_pages("https://example.com", homepage_result)

        self.assertEqual(selection["selected"]["product"], ["https://example.com/products/mevo-gen2"])
        self.assertEqual(selection["selected"]["blog_index"], ["https://example.com/blogs/news"])
        self.assertEqual(
            set(selection["selected"]["article"]),
            {
                "https://example.com/blogs/news/how-launch-monitors-work",
                "https://example.com/blogs/news/understanding-spin-rate",
            },
        )

    def test_merge_candidates_deduplicates(self):
        merged = merge_candidates(
            {
                "product": ["https://example.com/products/a"],
                "collection": [],
                "comparison": [],
                "blog_index": ["https://example.com/blogs/news"],
                "article": ["https://example.com/blogs/news/a"],
                "about_trust": [],
                "policy": [],
            },
            {
                "product": ["https://example.com/products/a", "https://example.com/products/b"],
                "collection": ["https://example.com/collections/golf"],
                "comparison": [],
                "blog_index": [],
                "article": ["https://example.com/blogs/news/b"],
                "about_trust": [],
                "policy": [],
            },
        )
        self.assertEqual(
            merged["product"],
            ["https://example.com/products/a", "https://example.com/products/b"],
        )
        self.assertEqual(merged["collection"], ["https://example.com/collections/golf"])

    @patch("scripts.collect_seo_evidence.fetch_text")
    def test_pick_representative_pages_prioritizes_news_articles(self, mock_fetch_text):
        mock_fetch_text.return_value = """
        <urlset>
          <url><loc>https://example.com/blogs/support/article-a</loc></url>
          <url><loc>https://example.com/blogs/videos/article-b</loc></url>
          <url><loc>https://example.com/blogs/news/article-c</loc></url>
        </urlset>
        """

        homepage_result = {
            "analysis": {
                "links_found": ["/blogs/news"],
                "url_analysis": {"final_url": "https://example.com"},
                "robots": {"sitemap_urls": ["https://example.com/sitemap.xml"]},
            }
        }

        selection = pick_representative_pages("https://example.com", homepage_result)
        self.assertEqual(selection["selected"]["article"][0], "https://example.com/blogs/news/article-c")

    def test_quotas_for_deep_profile_expands_sampling(self):
        quotas = quotas_for_profile("deep")
        self.assertEqual(quotas["product"], 4)
        self.assertEqual(quotas["article"], 6)

    @patch("scripts.collect_seo_evidence.fetch_text")
    def test_extract_sitemap_urls_from_index(self, mock_fetch_text):
        mock_fetch_text.side_effect = [
            """
            <sitemapindex>
              <sitemap><loc>https://example.com/sitemap-products.xml</loc></sitemap>
              <sitemap><loc>https://example.com/sitemap-blogs.xml</loc></sitemap>
            </sitemapindex>
            """,
            """
            <urlset>
              <url><loc>https://example.com/products/a</loc></url>
            </urlset>
            """,
            """
            <urlset>
              <url><loc>https://example.com/blogs/news/article-a</loc></url>
            </urlset>
            """,
        ]

        urls = extract_sitemap_urls("https://example.com/sitemap.xml")
        self.assertEqual(
            urls,
            [
                "https://example.com/products/a",
                "https://example.com/blogs/news/article-a",
            ],
        )


if __name__ == "__main__":
    unittest.main()
