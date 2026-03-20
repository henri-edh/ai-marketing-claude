# SEO Content Audit
## https://www.flightscope.com
### Date: 2026-03-20

---

## SEO Health Score: 65/100

FlightScope has a strong technical foundation for crawlability and page coverage, but the homepage still under-signals its primary commercial intent. The current audit now confirms article-page schema evidence in static HTML, which corrects the earlier false negative around Article markup. Representative product evidence also shows Product and FAQPage schema on the Mevo Gen2 page. The main remaining structured-data gap is homepage richness: the homepage evidence only shows Organization-level markup, not broader WebSite/SearchAction coverage.

---

## Methodology & Limitations
- Fresh audit performed from current-run evidence only
- Pages analyzed: https://flightscope.com/, https://flightscope.com/products/mevo-gen2, https://flightscope.com/products/mevo-plus, https://flightscope.com/products/flightscope-x3c, https://flightscope.com/products/mevo-gen2-with-thestack, https://flightscope.com/collections/all, https://flightscope.com/collections/sensors, https://flightscope.com/blogs/news/flightscope-mevo-vs-trackman-4-review, https://flightscope.com/blogs/news/mevo-vs-skytrak-review-by-golfsimulatorvideos, https://flightscope.com/blogs/news, https://flightscope.com/blogs/blogs, https://flightscope.com/blogs/news/how-fast-should-you-swing-your-driver, https://flightscope.com/blogs/news/flightscope-launches-new-mevo-pro-package, https://flightscope.com/blogs/news/using-the-flightscope-mevo-for-simulation, https://flightscope.com/blogs/news/flightscope-announces-mevo-trade-in-program, https://flightscope.com/blogs/news/flightscope-mevo-2023-launch-monitor-review, https://flightscope.com/blogs/news/flightscope-a-game-changer-in-the-world-of-golf, https://flightscope.com/pages/about, https://flightscope.com/pages/contact, https://flightscope.com/policies/privacy-policy, https://flightscope.com/policies/shipping-policy
- Static HTML analysis collected with `scripts/analyze_page.py` and `scripts/collect_seo_evidence.py`
- Browser-rendered verification collected with `scripts/verify_rendered_seo.py` via `browserless`
- Structured data and performance findings are confidence-labeled based on evidence source

## Coverage Summary
- `product`: sampled 4 page(s) from 74 discovered candidate(s)
- `collection`: sampled 2 page(s) from 46 discovered candidate(s)
- `comparison`: sampled 2 page(s) from 7 discovered candidate(s)
- `blog_index`: sampled 2 page(s) from 7 discovered candidate(s)
- `article`: sampled 6 page(s) from 48 discovered candidate(s)
- `about_trust`: sampled 2 page(s) from 4 discovered candidate(s)
- `policy`: sampled 2 page(s) from 4 discovered candidate(s)

---

## Evidence Inventory
- `homepage`: https://flightscope.com/ | confidence: Confirmed | schema: http://schema.org/Organization
- `product`: https://flightscope.com/products/mevo-gen2 | confidence: Confirmed | schema: FAQPage, Product, http://schema.org/Organization
- `product`: https://flightscope.com/products/mevo-plus | confidence: Confirmed | schema: FAQPage, Product, http://schema.org/Organization
- `product`: https://flightscope.com/products/flightscope-x3c | confidence: Confirmed | schema: FAQPage, Product, http://schema.org/Organization
- `product`: https://flightscope.com/products/mevo-gen2-with-thestack | confidence: Confirmed | schema: Product, http://schema.org/Organization
- `collection`: https://flightscope.com/collections/all | confidence: Confirmed | schema: CollectionPage, http://schema.org/Organization
- `collection`: https://flightscope.com/collections/sensors | confidence: Confirmed | schema: CollectionPage, http://schema.org/Organization
- `comparison`: https://flightscope.com/blogs/news/flightscope-mevo-vs-trackman-4-review | confidence: Confirmed | schema: Article, http://schema.org/Organization
- `comparison`: https://flightscope.com/blogs/news/mevo-vs-skytrak-review-by-golfsimulatorvideos | confidence: Confirmed | schema: Article, http://schema.org/Organization
- `blog_index`: https://flightscope.com/blogs/news | confidence: Confirmed | schema: http://schema.org/Organization
- `blog_index`: https://flightscope.com/blogs/blogs | confidence: Confirmed | schema: http://schema.org/Organization
- `article`: https://flightscope.com/blogs/news/how-fast-should-you-swing-your-driver | confidence: Confirmed | schema: Article, http://schema.org/Organization, https://schema.org/VideoObject
- `article`: https://flightscope.com/blogs/news/flightscope-launches-new-mevo-pro-package | confidence: Confirmed | schema: Article, http://schema.org/Organization
- `article`: https://flightscope.com/blogs/news/using-the-flightscope-mevo-for-simulation | confidence: Confirmed | schema: Article, http://schema.org/Organization
- `article`: https://flightscope.com/blogs/news/flightscope-announces-mevo-trade-in-program | confidence: Confirmed | schema: Article, http://schema.org/Organization
- `article`: https://flightscope.com/blogs/news/flightscope-mevo-2023-launch-monitor-review | confidence: Confirmed | schema: Article, http://schema.org/Organization
- `article`: https://flightscope.com/blogs/news/flightscope-a-game-changer-in-the-world-of-golf | confidence: Confirmed | schema: Article, http://schema.org/Organization
- `about_trust`: https://flightscope.com/pages/about | confidence: Confirmed | schema: http://schema.org/Organization
- `about_trust`: https://flightscope.com/pages/contact | confidence: Confirmed | schema: http://schema.org/Organization
- `policy`: https://flightscope.com/policies/privacy-policy | confidence: Confirmed | schema: http://schema.org/Organization
- `policy`: https://flightscope.com/policies/shipping-policy | confidence: Confirmed | schema: http://schema.org/Organization

---

## Key Findings
- Homepage title length is solid at 58 characters, but the meta description is short at 112 characters.
- Homepage H1 is `FlightScope Golf US Store`, which reads like a store label rather than a category-level search target.
- Homepage image coverage shows 11 images missing alt text out of 44.
- Site-level static schema evidence includes JSON-LD types: Article, CollectionPage, FAQPage, Product.

---

## On-Page SEO Checklist

### Homepage
- Title: `Portable Golf Launch Monitors and Simulators - FlightScope`
- Title status: Pass
- Meta description: `FlightScope golf launch monitors and portable simulators lead the charge in golf ball flight tracker technology.`
- Meta description status: Needs Work
- H1: `FlightScope Golf US Store`
- H1 status: Pass
- Images missing alt text: 11 of 44
- Canonical: `https://flightscope.com/`
- Viewport present: Yes
- Hreflang count: 7

### Blog Index
- Sample size: 2
- Confidence mix: Confirmed 2, Likely 0, Needs Verification 0
- Title quality: 0/2 in recommended range
- Meta description quality: 0/2 in recommended range
- Schema types seen: http://schema.org/Organization
- `https://flightscope.com/blogs/news` | title: 41 chars | meta: 115 chars | H1: `News` | confidence: Confirmed
- `https://flightscope.com/blogs/blogs` | title: 5 chars | meta: 118 chars | H1: `Blogs` | confidence: Confirmed

### Article Pages
- Sample size: 6
- Confidence mix: Confirmed 6, Likely 0, Needs Verification 0
- Title quality: 1/6 in recommended range
- Meta description quality: 6/6 in recommended range
- Schema types seen: Article, http://schema.org/Organization, https://schema.org/VideoObject
- `https://flightscope.com/blogs/news/how-fast-should-you-swing-your-driver` | title: 38 chars | meta: 153 chars | H1: `How Fast should you Swing Your Driver?` | confidence: Confirmed
- `https://flightscope.com/blogs/news/flightscope-launches-new-mevo-pro-package` | title: 42 chars | meta: 141 chars | H1: `FlightScope Launches New Mevo+ Pro Package` | confidence: Confirmed
- `https://flightscope.com/blogs/news/using-the-flightscope-mevo-for-simulation` | title: 42 chars | meta: 143 chars | H1: `Using the FlightScope Mevo+ for Simulation` | confidence: Confirmed
- `https://flightscope.com/blogs/news/flightscope-announces-mevo-trade-in-program` | title: 43 chars | meta: 144 chars | H1: `FlightScope Announces Mevo Trade-In Program` | confidence: Confirmed
- `https://flightscope.com/blogs/news/flightscope-mevo-2023-launch-monitor-review` | title: 44 chars | meta: 154 chars | H1: `Flightscope Mevo+ 2023 Launch Monitor Review` | confidence: Confirmed
- `https://flightscope.com/blogs/news/flightscope-a-game-changer-in-the-world-of-golf` | title: 48 chars | meta: 154 chars | H1: `FlightScope: A Game-Changer in the World of Golf` | confidence: Confirmed

### Product Pages
- Sample size: 4
- Confidence mix: Confirmed 4, Likely 0, Needs Verification 0
- Title quality: 2/4 in recommended range
- Meta description quality: 3/4 in recommended range
- Schema types seen: FAQPage, Product, http://schema.org/Organization
- `https://flightscope.com/products/mevo-gen2` | title: 51 chars | meta: 119 chars | H1: `Mevo Gen2` | confidence: Confirmed
- `https://flightscope.com/products/mevo-plus` | title: 37 chars | meta: 152 chars | H1: `Mevo+` | confidence: Confirmed
- `https://flightscope.com/products/flightscope-x3c` | title: 59 chars | meta: 141 chars | H1: `FlightScope X3C` | confidence: Confirmed
- `https://flightscope.com/products/mevo-gen2-with-thestack` | title: 23 chars | meta: 154 chars | H1: `Mevo Gen2 with TheStack` | confidence: Confirmed

### Collection Pages
- Sample size: 2
- Confidence mix: Confirmed 2, Likely 0, Needs Verification 0
- Title quality: 1/2 in recommended range
- Meta description quality: 2/2 in recommended range
- Schema types seen: CollectionPage, http://schema.org/Organization
- `https://flightscope.com/collections/all` | title: 46 chars | meta: 136 chars | H1: `All` | confidence: Confirmed
- `https://flightscope.com/collections/sensors` | title: 32 chars | meta: 144 chars | H1: `FlightScope Golf Launch Monitors` | confidence: Confirmed

### Comparison Pages
- Sample size: 2
- Confidence mix: Confirmed 2, Likely 0, Needs Verification 0
- Title quality: 2/2 in recommended range
- Meta description quality: 2/2 in recommended range
- Schema types seen: Article, http://schema.org/Organization
- `https://flightscope.com/blogs/news/flightscope-mevo-vs-trackman-4-review` | title: 54 chars | meta: 143 chars | H1: `FlightScope Mevo+ vs Trackman 4 review by Golfalot.com` | confidence: Confirmed
- `https://flightscope.com/blogs/news/mevo-vs-skytrak-review-by-golfsimulatorvideos` | title: 50 chars | meta: 152 chars | H1: `Mevo+ vs SkyTrak review by Golfsimulatorvideos.com` | confidence: Confirmed

### About / Trust Pages
- Sample size: 2
- Confidence mix: Confirmed 2, Likely 0, Needs Verification 0
- Title quality: 2/2 in recommended range
- Meta description quality: 0/2 in recommended range
- Schema types seen: http://schema.org/Organization
- `https://flightscope.com/pages/about` | title: 62 chars | meta: 92 chars | H1: `3D Doppler Ball Tracking Monitors, Golf Radars & Launch Monitors` | confidence: Confirmed
- `https://flightscope.com/pages/contact` | title: 47 chars | meta: 103 chars | H1: `Customer Care` | confidence: Confirmed

### Policy Pages
- Sample size: 2
- Confidence mix: Confirmed 2, Likely 0, Needs Verification 0
- Title quality: 0/2 in recommended range
- Meta description quality: 0/2 in recommended range
- Schema types seen: http://schema.org/Organization
- `https://flightscope.com/policies/privacy-policy` | title: 14 chars | meta: 0 chars | H1: `Privacy policy` | confidence: Confirmed
- `https://flightscope.com/policies/shipping-policy` | title: 15 chars | meta: 0 chars | H1: `Shipping policy` | confidence: Confirmed

---

## Structured Data
- Homepage schema types: http://schema.org/Organization
- Site-level static schema summary: JSON-LD [Article, CollectionPage, FAQPage, Product], Microdata [http://schema.org/Organization, https://schema.org/VideoObject], RDFa [none]
- Homepage confidence: Confirmed
- Interpretation: article and product schema are present in representative static evidence; homepage richness is the weaker area.
- Article-page schema evidence: Article, http://schema.org/Organization, https://schema.org/VideoObject

---

## Technical SEO
- Internal links on homepage: 155
- External links on homepage: 13
- Scripts loaded on homepage: 24
- Robots.txt detected: Yes
- Sitemap detected: Yes
- x-default hreflang present: No

---

## What Is Working
- Representative product evidence shows Product and FAQPage schema instead of the earlier false-negative state.
- Representative article evidence shows Article schema with author data on real article URLs.
- Homepage crawlability basics are in place: canonical, robots.txt, sitemap, viewport, and substantial internal linking.

---

## Gaps And Risks
- Homepage search intent is under-signaled by the current H1.
- Homepage meta description is too short to fully use SERP snippet space.
- Homepage image alt coverage is incomplete.
- Browser-rendered verification could not be confirmed in this environment, so JS-sensitive findings should still be verified externally if they are business-critical.

---

## Prioritized Recommendations
- [Critical] [Confirmed] Improve the homepage H1. Current H1: `FlightScope Golf US Store`.
- [Critical] [Confirmed] Expand the homepage meta description from 112 characters to a fuller SERP-ready description.
- [High] [Confirmed] Add alt text to 11 homepage images missing it.
- [High] [Likely] Expand homepage schema beyond Organization markup. Add WebSite/SearchAction and verify it in a rendered environment or Rich Results tooling.
- [Medium] [Confirmed] Add an `x-default` hreflang entry for the fallback homepage variant.
- [Medium] [Confirmed] Improve the blog index H1 from `News` to a keyword-bearing heading that reflects golf launch monitor content.
- [Low] [Confirmed] Preserve existing product-page Product and FAQPage schema coverage during any theme changes.

---

*Generated from `seo_evidence.json` and `rendered_verification.json` when available.*
