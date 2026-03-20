import unittest

from scripts.analyze_page import ImprovedMarketingParser


class AnalyzePageStructuredDataTests(unittest.TestCase):
    def parse(self, html):
        parser = ImprovedMarketingParser()
        parser.feed(html)
        return parser.get_results()

    def test_json_ld_type_arrays_and_graph_are_flattened(self):
        results = self.parse(
            """
            <html>
              <head>
                <script type="application/ld+json">
                {
                  "@context": "https://schema.org",
                  "@type": ["Article", "NewsArticle"],
                  "headline": "Structured data article",
                  "author": {"@type": "Person", "name": "Cody Hansen"},
                  "@graph": [
                    {"@type": "BreadcrumbList"},
                    {"@type": ["Organization", "Brand"], "name": "FlightScope"}
                  ]
                }
                </script>
              </head>
              <body></body>
            </html>
            """
        )

        tracking = results["tracking"]
        self.assertEqual(
            tracking["json_ld_schema_types"],
            ["Article", "Brand", "BreadcrumbList", "NewsArticle", "Organization"],
        )
        self.assertEqual(tracking["json_ld_items"][0]["author"], "Cody Hansen")
        self.assertIn("Article", tracking["schema_summary"]["json_ld_types"])

    def test_microdata_article_is_captured(self):
        results = self.parse(
            """
            <html>
              <body>
                <article itemscope itemtype="https://schema.org/Article">
                  <h1 itemprop="headline">How launch monitors work</h1>
                  <a itemprop="author" href="/authors/cody-hansen">Cody Hansen</a>
                  <img itemprop="image" src="hero.jpg" alt="Hero">
                  <time itemprop="datePublished" datetime="2026-03-20">March 20, 2026</time>
                </article>
              </body>
            </html>
            """
        )

        tracking = results["tracking"]
        self.assertEqual(tracking["microdata_types"], ["https://schema.org/Article"])
        self.assertEqual(tracking["microdata_count"], 1)
        self.assertEqual(
            tracking["microdata_items"][0]["props"]["headline"],
            ["How launch monitors work"],
        )
        self.assertEqual(
            tracking["microdata_items"][0]["props"]["author"],
            ["/authors/cody-hansen"],
        )
        self.assertEqual(
            tracking["microdata_items"][0]["props"]["image"],
            ["hero.jpg"],
        )

    def test_img_alt_none_does_not_crash(self):
        results = self.parse(
            """
            <html>
              <body>
                <img src="hero.jpg" alt>
              </body>
            </html>
            """
        )

        self.assertEqual(results["seo"]["images_total"], 1)
        self.assertEqual(results["seo"]["images_without_alt"], 1)


if __name__ == "__main__":
    unittest.main()
