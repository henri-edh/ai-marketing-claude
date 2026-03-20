#!/usr/bin/env python3
"""
Marketing Page Analyzer — Utility script for AI Marketing Claude Code Skills
Analyzes a webpage for marketing effectiveness: SEO elements, content structure,
trust signals, CTAs, social proof, and conversion optimization indicators.

Improved version with robust HTML parsing to avoid false positives.
"""

import sys
import json
import re
import urllib.request
import urllib.error
import ssl
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin
from collections import defaultdict


class ImprovedMarketingParser(HTMLParser):
    """
    Robust HTML parser that correctly handles:
    - Title tags (only from <head>, not SVG or other contexts)
    - Headings with nested content and section context (nav/header/footer/main)
    - Multiple structured data formats (JSON-LD, Microdata, RDFa)
    """

    def __init__(self):
        super().__init__()
        # SEO elements
        self.title = ""
        self.meta_description = ""
        self.meta_keywords = ""
        self.og_tags = {}
        self.twitter_tags = {}
        self.headings = {"h1": [], "h2": [], "h3": [], "h4": [], "h5": [], "h6": []}

        # Links and media
        self.links = []
        self.images = []
        self.forms = []
        self.buttons = []
        self.scripts = []

        # Structured data
        self.json_ld_schema = []
        self.microdata_items = []
        self.rdfa_data = []

        # Marketing elements
        self.ctas = []
        self.social_links = []
        self.tracking_scripts = []

        # Technical SEO
        self._canonical = ""
        self._robots_meta = ""
        self._has_viewport = False
        self._hreflang_tags = []

        # State tracking for proper parsing
        self._in_head = False
        self._in_body = False
        self._in_title = False
        self._in_heading_tag = None
        self._in_heading = False
        self._heading_text_parts = []
        self._in_link = False
        self._current_link_attrs = None
        self._link_text_parts = []
        self._in_button = False
        self._button_text_parts = []
        self._in_script = False
        self._script_type = ""
        self._script_content = []
        self._in_svg = False
        self._depth_in_svg = 0

        # Section context tracking (nav/header/footer/main/aside)
        self._section_context = "main"
        self._section_stack = []
        self._headings_with_context = []

        # Microdata state
        self._itemscope_stack = []
        self._current_item = None
        self._itemprop_stack = []

        # RDFa state
        self._in_rdfa = False
        self._current_rdfa_attrs = {}

        # All text content
        self._all_text = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Track SVG depth to avoid parsing internal <title> tags
        if tag == "svg":
            self._in_svg = True
            self._depth_in_svg += 1
            return

        # Skip processing if inside SVG
        if self._in_svg and self._depth_in_svg > 0:
            if tag == "svg":
                self._depth_in_svg += 1
            return

        # Track document sections
        if tag == "head":
            self._in_head = True
        elif tag == "body":
            self._in_body = True
            self._in_head = False

        # Track semantic section context (nav, header, footer, main, aside)
        if tag in ("nav", "header", "footer", "main", "aside"):
            self._section_stack.append(self._section_context)
            self._section_context = tag

        # Handle <title> tag - ONLY in <head>
        if tag == "title" and self._in_head:
            self._in_title = True

        # Handle headings
        elif tag in self.headings:
            self._in_heading_tag = tag
            self._in_heading = True
            self._heading_text_parts = []

        # Handle meta tags
        elif tag == "meta":
            self._process_meta_tag(attrs_dict)

        # Handle link tags (canonical, stylesheets, etc.)
        elif tag == "link":
            self._process_link_tag(attrs_dict)

        # Handle anchors
        elif tag == "a":
            self._in_link = True
            self._current_link_attrs = attrs_dict
            self._link_text_parts = []
            self._check_rdfa_attrs(attrs_dict)

        # Handle images
        elif tag == "img":
            self._process_image(attrs_dict)

        # Handle buttons
        elif tag == "button":
            self._in_button = True
            self._button_text_parts = []

        # Handle forms
        elif tag == "form":
            self._process_form(attrs_dict)

        # Handle form inputs
        elif tag == "input":
            self._process_input(attrs_dict)

        # Handle scripts
        elif tag == "script":
            self._in_script = True
            self._script_type = attrs_dict.get("type", "")
            self._script_content = []
            src = attrs_dict.get("src", "")
            if src:
                self.scripts.append(src)
                self._detect_tracking_scripts(src)

        # Track Microdata itemscope
        if "itemscope" in attrs_dict:
            parent_item = self._itemscope_stack[-1] if self._itemscope_stack else None
            item = {
                "tag": tag,
                "type": attrs_dict.get("itemtype", ""),
                "id": attrs_dict.get("itemid", ""),
                "itemprop": attrs_dict.get("itemprop", ""),
                "props": defaultdict(list)
            }
            self._itemscope_stack.append(item)
            self._current_item = item

            # Preserve parent-child microdata relationships in a lightweight form.
            if parent_item and attrs_dict.get("itemprop"):
                prop_name = attrs_dict["itemprop"]
                child_value = attrs_dict.get("itemid") or attrs_dict.get("itemtype") or attrs_dict.get("href") or attrs_dict.get("src") or tag
                parent_item["props"][prop_name].append(child_value)

        self._check_microdata_attrs(tag, attrs_dict)

        # Track RDFa
        if any(k in attrs_dict for k in ["vocab", "typeof", "property", "prefix"]):
            self._in_rdfa = True
            self._current_rdfa_attrs = attrs_dict

    def handle_endtag(self, tag):
        # Handle SVG end tags
        if tag == "svg":
            self._depth_in_svg -= 1
            if self._depth_in_svg <= 0:
                self._in_svg = False
                self._depth_in_svg = 0
            return

        # Skip if inside SVG
        if self._in_svg:
            return

        # Track document sections
        if tag == "head":
            self._in_head = False
        elif tag == "body":
            self._in_body = False

        # Pop semantic section context
        if tag in ("nav", "header", "footer", "main", "aside"):
            if self._section_stack:
                self._section_context = self._section_stack.pop()
            else:
                self._section_context = "main"

        # Handle title end
        if tag == "title" and self._in_title:
            self._in_title = False

        # Handle heading end
        elif tag in self.headings and self._in_heading_tag == tag:
            text = "".join(self._heading_text_parts).strip()
            if text:  # Only add non-empty headings
                self.headings[tag].append(text)
                self._headings_with_context.append({
                    "tag": tag,
                    "text": text,
                    "context": self._section_context
                })
            self._in_heading = False
            self._in_heading_tag = None
            self._heading_text_parts = []

        # Handle link end
        elif tag == "a" and self._in_link:
            text = "".join(self._link_text_parts).strip()
            href = self._current_link_attrs.get("href", "") if self._current_link_attrs else ""
            self.links.append({
                "href": href,
                "text": text,
                "attrs": self._current_link_attrs or {}
            })
            self._detect_cta(text, href)
            self._detect_social_link(href)
            self._in_link = False
            self._current_link_attrs = None
            self._link_text_parts = []

        # Handle button end
        elif tag == "button" and self._in_button:
            text = "".join(self._button_text_parts).strip()
            if text:
                self.buttons.append(text)
                self.ctas.append({"text": text, "type": "button"})
            self._in_button = False
            self._button_text_parts = []

        # Handle script end
        elif tag == "script" and self._in_script:
            script_content = "".join(self._script_content)
            self._process_script_content(script_content)
            self._in_script = False
            self._script_content = []

        # Handle Microdata property end
        if self._itemprop_stack and self._itemprop_stack[-1]["tag"] == tag:
            prop_capture = self._itemprop_stack.pop()
            if prop_capture["target_item"] is not None and not prop_capture["has_attr_value"]:
                text_value = "".join(prop_capture["text_parts"]).strip()
                if text_value:
                    prop_capture["target_item"]["props"][prop_capture["prop_name"]].append(text_value)

        # Handle Microdata itemscope end
        if self._itemscope_stack and self._itemscope_stack[-1]["tag"] == tag:
            completed_item = self._itemscope_stack.pop()
            if completed_item.get("type") or completed_item.get("props"):
                completed_item["props"] = dict(completed_item["props"])
                self.microdata_items.append(completed_item)
            self._current_item = self._itemscope_stack[-1] if self._itemscope_stack else None

    def handle_data(self, data):
        # Skip if inside SVG
        if self._in_svg:
            return

        # Capture title text (only from <head>)
        if self._in_title:
            self.title += data

        # Capture heading text
        if self._in_heading:
            self._heading_text_parts.append(data)

        # Capture link text
        if self._in_link:
            self._link_text_parts.append(data)

        # Capture button text
        if self._in_button:
            self._button_text_parts.append(data)

        # Capture script content
        if self._in_script:
            self._script_content.append(data)

        # Capture all text content
        self._all_text.append(data)

        # Capture Microdata text properties
        for prop_capture in self._itemprop_stack:
            prop_capture["text_parts"].append(data)

    def _process_meta_tag(self, attrs):
        """Process meta tags for SEO and social media."""
        name = attrs.get("name", "").lower()
        prop = attrs.get("property", "").lower()
        content = attrs.get("content", "")

        if not content:
            return

        # Standard SEO meta tags
        if name == "description":
            self.meta_description = content
        elif name == "keywords":
            self.meta_keywords = content
        elif name == "viewport":
            self._has_viewport = True
        elif name == "robots":
            self._robots_meta = content
        elif name == "canonical":
            self._canonical = content

        # Open Graph tags
        elif prop.startswith("og:"):
            self.og_tags[prop] = content

        # Twitter Card tags
        elif name.startswith("twitter:"):
            self.twitter_tags[name] = content

    def _process_link_tag(self, attrs):
        """Process link tags (canonical, hreflang, etc.)."""
        rel = attrs.get("rel", "")
        href = attrs.get("href", "")

        if "canonical" in rel and href:
            self._canonical = href
        elif "alternate" in rel and "hreflang" in attrs:
            self._hreflang_tags.append({
                "lang": attrs.get("hreflang"),
                "url": href
            })

    def _process_image(self, attrs):
        """Process image tags for alt text analysis."""
        alt_value = attrs.get("alt", "")
        if alt_value is None:
            alt_value = ""

        self.images.append({
            "src": attrs.get("src", ""),
            "alt": alt_value,
            "has_alt": "alt" in attrs,
            "loading": attrs.get("loading", ""),
            "width": attrs.get("width", ""),
            "height": attrs.get("height", "")
        })

    def _process_form(self, attrs):
        """Process form tags."""
        self.forms.append({
            "action": attrs.get("action", ""),
            "method": attrs.get("method", "GET").upper(),
            "fields": [],
            "field_count": 0
        })

    def _process_input(self, attrs):
        """Process input fields within forms."""
        if self.forms:
            field = {
                "type": attrs.get("type", "text"),
                "name": attrs.get("name", ""),
                "placeholder": attrs.get("placeholder", ""),
                "required": "required" in attrs
            }
            self.forms[-1]["fields"].append(field)
            self.forms[-1]["field_count"] += 1

    def _detect_tracking_scripts(self, src):
        """Detect tracking/analytics scripts from URL."""
        tracking_indicators = {
            "gtag": "Google Analytics (gtag)",
            "googletagmanager": "Google Tag Manager",
            "google-analytics": "Google Analytics",
            "analytics": "Analytics",
            "fbevents": "Meta Pixel",
            "facebook": "Meta/Facebook",
            "snap.licdn": "LinkedIn Insight Tag",
            "hotjar": "Hotjar",
            "fullstory": "FullStory",
            "mixpanel": "Mixpanel",
            "amplitude": "Amplitude",
            "segment": "Segment",
            "hubspot": "HubSpot",
            "intercom": "Intercom",
            "crisp": "Crisp Chat",
            "drift": "Drift",
            "tiktok": "TikTok Pixel",
            "clarity": "Microsoft Clarity",
            "bat.bing": "Microsoft Advertising",
            "pixel.wp": "WordPress Stats",
            "mc.yandex": "Yandex Metrica"
        }
        src_lower = src.lower()
        for indicator, name in tracking_indicators.items():
            if indicator in src_lower:
                if name not in self.tracking_scripts:
                    self.tracking_scripts.append(name)

    def _process_script_content(self, content):
        """Process inline script content for tracking and structured data."""
        content = content.strip()

        # Check for inline tracking scripts
        if "gtag" in content or "dataLayer" in content:
            if "Google Analytics" not in self.tracking_scripts and "Google Tag Manager" not in self.tracking_scripts:
                self.tracking_scripts.append("Google Analytics/GTM (inline)")
        if "fbq" in content:
            if "Meta Pixel" not in self.tracking_scripts:
                self.tracking_scripts.append("Meta Pixel (inline)")
        if "ttq" in content or "tiktok" in content.lower():
            if "TikTok Pixel" not in self.tracking_scripts:
                self.tracking_scripts.append("TikTok Pixel (inline)")
        if "ln" in content and "linkedin" in content.lower():
            if "LinkedIn Insight Tag" not in self.tracking_scripts:
                self.tracking_scripts.append("LinkedIn Insight Tag (inline)")

        # Parse JSON-LD structured data
        if self._script_type == "application/ld+json":
            try:
                schemas = json.loads(content)
                if isinstance(schemas, list):
                    self.json_ld_schema.extend(schemas)
                else:
                    self.json_ld_schema.append(schemas)
            except (json.JSONDecodeError, ValueError):
                pass

    def _detect_cta(self, text, href):
        """Detect call-to-action links."""
        if not text:
            return
        cta_words = [
            "sign up", "get started", "try free", "start free", "buy now",
            "subscribe", "join", "register", "download", "book", "schedule",
            "request demo", "contact us", "learn more", "see pricing",
            "start trial", "create account", "claim", "unlock", "shop now",
            "add to cart", "order now", "get quote", "find out more"
        ]
        text_lower = text.lower()
        for cta in cta_words:
            if cta in text_lower:
                self.ctas.append({"text": text, "href": href, "type": "link"})
                break

    def _detect_social_link(self, href):
        """Detect social media platform links."""
        if not href:
            return
        social_platforms = {
            "twitter.com": "twitter",
            "x.com": "x",
            "facebook.com": "facebook",
            "linkedin.com": "linkedin",
            "instagram.com": "instagram",
            "youtube.com": "youtube",
            "tiktok.com": "tiktok",
            "pinterest.com": "pinterest",
            "github.com": "github"
        }
        for domain, platform in social_platforms.items():
            if domain in href:
                self.social_links.append({"platform": platform, "url": href})
                break

    def _check_microdata_attrs(self, tag, attrs):
        """Check for Microdata attributes."""
        if not self._current_item or "itemprop" not in attrs:
            return

        prop_name = attrs["itemprop"]
        if not prop_name:
            return

        attr_value = (
            attrs.get("content")
            or attrs.get("href")
            or attrs.get("src")
            or attrs.get("datetime")
            or attrs.get("title")
            or attrs.get("aria-label")
        )

        has_attr_value = bool(attr_value)
        if has_attr_value:
            self._current_item["props"][prop_name].append(attr_value)

        # For non-void tags, keep collecting text content until the element closes.
        if tag not in {"meta", "link", "img", "source"}:
            self._itemprop_stack.append({
                "tag": tag,
                "prop_name": prop_name,
                "target_item": self._current_item,
                "has_attr_value": has_attr_value,
                "text_parts": []
            })

    def _check_rdfa_attrs(self, attrs):
        """Check for RDFa attributes."""
        if any(k in attrs for k in ["vocab", "typeof", "property"]):
            rdfa_info = {
                "vocab": attrs.get("vocab", ""),
                "typeof": attrs.get("typeof", ""),
                "property": attrs.get("property", ""),
                "content": attrs.get("content", ""),
                "resource": attrs.get("resource", ""),
                "href": attrs.get("href", ""),
                "src": attrs.get("src", "")
            }
            if any(rdfa_info.values()):
                self.rdfa_data.append(rdfa_info)

    def _extract_json_ld_types(self, payload):
        """Recursively extract schema types from JSON-LD payloads."""
        schema_types = []

        if isinstance(payload, list):
            for item in payload:
                schema_types.extend(self._extract_json_ld_types(item))
            return schema_types

        if not isinstance(payload, dict):
            return schema_types

        schema_type = payload.get("@type", "")
        if isinstance(schema_type, list):
            schema_types.extend([value for value in schema_type if isinstance(value, str) and value])
        elif isinstance(schema_type, str) and schema_type:
            schema_types.append(schema_type)

        if "@graph" in payload:
            schema_types.extend(self._extract_json_ld_types(payload["@graph"]))

        return schema_types

    def _summarize_json_ld_item(self, payload):
        """Return a compact summary of a JSON-LD item."""
        if not isinstance(payload, dict):
            return None

        types = self._extract_json_ld_types(payload)
        if not types and "@graph" not in payload:
            return None

        summary = {
            "types": sorted(set(types)),
            "name": payload.get("name", ""),
            "headline": payload.get("headline", ""),
            "url": payload.get("url", ""),
            "image": payload.get("image", ""),
            "author": ""
        }

        author = payload.get("author", "")
        if isinstance(author, dict):
            summary["author"] = author.get("name", "") or author.get("@id", "")
        elif isinstance(author, list):
            author_names = []
            for item in author:
                if isinstance(item, dict):
                    author_names.append(item.get("name", "") or item.get("@id", ""))
                elif isinstance(item, str):
                    author_names.append(item)
            summary["author"] = ", ".join([name for name in author_names if name])
        elif isinstance(author, str):
            summary["author"] = author

        return summary

    def get_full_text(self):
        """Get all text content from the page."""
        return " ".join(self._all_text)

    def get_results(self):
        """Compile all findings into a structured result."""
        # Count images without alt text
        images_without_alt = sum(1 for img in self.images if not img.get("has_alt") or not img.get("alt", "").strip())
        images_with_lazy = sum(1 for img in self.images if img.get("loading") == "lazy")

        # Analyze heading hierarchy
        heading_issues = []
        if not self.headings["h1"]:
            heading_issues.append("Missing H1 tag")
        elif len(self.headings["h1"]) > 1:
            heading_issues.append(f"Multiple H1 tags ({len(self.headings['h1'])})")
        if self.headings["h3"] and not self.headings["h2"]:
            heading_issues.append("H3 used without H2 (skipped level)")

        # Analyze structured data
        schema_types = []
        json_ld_items = []
        for schema in self.json_ld_schema:
            schema_types.extend(self._extract_json_ld_types(schema))
            summary = self._summarize_json_ld_item(schema)
            if summary:
                json_ld_items.append(summary)

        # Get unique schema types
        schema_types = sorted(set(schema_types))

        # Analyze Microdata
        microdata_types = []
        microdata_items = []
        for item in self.microdata_items:
            if item.get("type"):
                microdata_types.append(item["type"])
            microdata_items.append({
                "type": item.get("type", ""),
                "id": item.get("id", ""),
                "itemprop": item.get("itemprop", ""),
                "props": item.get("props", {})
            })

        microdata_types = sorted(set(microdata_types))

        rdfa_types = sorted(set(
            value
            for entry in self.rdfa_data
            for value in (
                entry.get("typeof", "").split()
                if isinstance(entry.get("typeof"), str) and entry.get("typeof")
                else []
            )
            if value
        ))

        # Count structured data
        total_schema = len(schema_types) + len(microdata_types) + len(self.rdfa_data)

        # Unique tracking tools
        tracking = list(set(self.tracking_scripts))

        # Full text for word count
        full_text = self.get_full_text()
        word_count = len(full_text.split())

        # Collect all link hrefs for URL verification
        link_hrefs = [link.get("href", "") for link in self.links if link.get("href")]

        return {
            "seo": {
                "title": self.title.strip(),
                "title_length": len(self.title.strip()),
                "title_ok": 30 <= len(self.title.strip()) <= 60,
                "meta_description": self.meta_description,
                "meta_description_length": len(self.meta_description),
                "meta_description_ok": 120 <= len(self.meta_description) <= 160,
                "canonical": self._canonical,
                "robots_meta": self._robots_meta,
                "has_viewport": self._has_viewport,
                "og_tags": self.og_tags,
                "twitter_tags": self.twitter_tags,
                "hreflang_tags": self._hreflang_tags,
                "headings": {k: v for k, v in self.headings.items() if v},
                "headings_with_context": self._headings_with_context,
                "heading_issues": heading_issues,
                "h1_count": len(self.headings["h1"]),
                "h1_text": self.headings["h1"][:3],  # First 3 H1s
                "images_total": len(self.images),
                "images_without_alt": images_without_alt,
                "images_with_lazy_loading": images_with_lazy
            },
            "links_found": link_hrefs,
            "content": {
                "word_count": word_count,
                "headings_count": sum(len(v) for v in self.headings.values()),
                "h1": self.headings["h1"],
                "h2": self.headings["h2"]
            },
            "conversion": {
                "ctas": self.ctas[:20],
                "cta_count": len(self.ctas),
                "forms": self.forms,
                "form_count": len(self.forms),
                "buttons": self.buttons[:20]
            },
            "trust": {
                "social_links": self.social_links,
                "social_link_count": len(self.social_links)
            },
            "tracking": {
                "tools_detected": tracking,
                "tools_count": len(tracking),
                "json_ld_schema_types": schema_types,
                "json_ld_count": len(schema_types),
                "json_ld_items": json_ld_items,
                "microdata_types": microdata_types,
                "microdata_count": len(microdata_types),
                "microdata_items": microdata_items,
                "rdfa_types": rdfa_types,
                "rdfa_items": self.rdfa_data,
                "rdfa_count": len(self.rdfa_data),
                "schema_summary": {
                    "json_ld_types": schema_types,
                    "microdata_types": microdata_types,
                    "rdfa_types": rdfa_types
                },
                "total_schema_count": total_schema
            },
            "technical": {
                "total_links": len(self.links),
                "internal_links": 0,  # Filled after URL analysis
                "external_links": 0,
                "scripts_count": len(self.scripts)
            }
        }


def check_redirects(url):
    """Check if URL redirects and track redirect chain."""
    redirect_chain = []
    final_url = url

    try:
        ctx = ssl.create_default_context()

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=10, context=ctx)

        # Track redirects
        if hasattr(response, 'url'):
            final_url = response.url
        if hasattr(response, 'redirects'):  # Not always available
            redirect_chain = response.redirects

        # Check for www vs non-www
        parsed_orig = urlparse(url)
        parsed_final = urlparse(final_url)

        www_status = {
            "original": parsed_orig.netloc,
            "final": parsed_final.netloc,
            "redirected": final_url != url,
            "www_differs": ("www." in parsed_orig.netloc) != ("www." in parsed_final.netloc)
        }

        return {
            "final_url": final_url,
            "redirect_chain": redirect_chain,
            "www_status": www_status
        }

    except Exception as e:
        return {
            "final_url": url,
            "error": str(e),
            "www_status": {"original": url, "final": url, "redirected": False}
        }


def fetch_page(url):
    """Fetch a webpage and return its HTML content."""
    ctx = ssl.create_default_context()

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(req, timeout=15, context=ctx)
        return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError:
        return None
    except (urllib.error.URLError, ssl.SSLError, TimeoutError):
        return None


def fetch_robots_txt(url):
    """Fetch and parse robots.txt."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    content = fetch_page(robots_url)
    if content:
        has_sitemap = "sitemap:" in content.lower()
        sitemap_urls = re.findall(r'sitemap:\s*(https?://[^\s]+)', content, re.IGNORECASE)
        return {
            "exists": True,
            "has_sitemap_reference": has_sitemap,
            "sitemap_urls": sitemap_urls,
            "content_preview": content[:500]
        }
    return {"exists": False}


def fetch_sitemap(url):
    """Check if sitemap.xml exists."""
    parsed = urlparse(url)
    sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(sitemap_url, headers={"User-Agent": "MarketingBot/1.0"})
        response = urllib.request.urlopen(req, timeout=10, context=ctx)
        content = response.read().decode("utf-8", errors="replace")
        # Count URLs in sitemap
        url_count = content.lower().count("<url>") or content.lower().count("<loc>")
        # Check for sitemap index
        has_sitemap_index = "<sitemapindex" in content.lower()
        return {"exists": True, "url_count": url_count, "is_index": has_sitemap_index}
    except (urllib.error.HTTPError, urllib.error.URLError, ssl.SSLError, TimeoutError):
        return {"exists": False, "url_count": 0}


def analyze(url):
    """Run full marketing analysis on a URL."""
    results = {"url": url, "status": "success"}

    # Check redirects first
    redirect_info = check_redirects(url)
    results["redirect_info"] = redirect_info

    # Use the final URL after redirects for analysis
    final_url = redirect_info.get("final_url", url)

    # Fetch and parse main page
    html = fetch_page(final_url)
    if not html:
        return {"url": url, "status": "error", "message": "Could not fetch page"}

    parser = ImprovedMarketingParser()
    try:
        parser.feed(html)
    except Exception as e:
        return {"url": url, "status": "error", "message": f"Parse error: {str(e)}"}

    page_results = parser.get_results()

    # Count internal vs external links
    parsed_url = urlparse(final_url)
    domain = parsed_url.netloc
    # Normalize domain (remove www for comparison)
    domain_norm = domain.replace("www.", "")

    internal = 0
    external = 0
    for link in parser.links:
        href = link.get("href", "")
        if not href or href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        # Check if internal
        link_domain = urlparse(href).netloc
        link_domain_norm = link_domain.replace("www.", "")
        if href.startswith("/") or link_domain_norm == domain_norm or link_domain == domain:
            internal += 1
        elif href.startswith("http"):
            external += 1

    page_results["technical"]["internal_links"] = internal
    page_results["technical"]["external_links"] = external

    # Check robots.txt and sitemap
    page_results["robots"] = fetch_robots_txt(final_url)
    page_results["sitemap"] = fetch_sitemap(final_url)

    # Add URL analysis
    page_results["url_analysis"] = {
        "original_url": url,
        "final_url": final_url,
        "uses_https": final_url.startswith("https://"),
        "has_www": "www." in parsed_url.netloc,
        "redirected": final_url != url
    }

    # Generate marketing scores
    scores = {}

    # SEO Score
    seo_score = 10
    seo = page_results["seo"]
    if not seo["title"]:
        seo_score -= 3
    elif not seo["title_ok"]:
        seo_score -= 1
    if not seo["meta_description"]:
        seo_score -= 3
    elif not seo["meta_description_ok"]:
        seo_score -= 1
    if not seo["headings"].get("h1"):
        seo_score -= 2
    if seo["images_without_alt"] > 0:
        seo_score -= min(2, seo["images_without_alt"])
    if seo["heading_issues"]:
        seo_score -= 1
    if not seo["has_viewport"]:
        seo_score -= 1
    scores["seo"] = max(0, seo_score)

    # CTA Score
    cta_score = 5
    conv = page_results["conversion"]
    if conv["cta_count"] == 0:
        cta_score = 1
    elif conv["cta_count"] >= 2:
        cta_score = 7
    if conv["cta_count"] >= 4:
        cta_score = 8
    # Check for value-driven CTAs
    value_ctas = [c for c in conv["ctas"] if len(c.get("text", "")) > 10]
    if value_ctas:
        cta_score = min(10, cta_score + 1)
    scores["cta"] = cta_score

    # Trust Score
    trust_score = 5
    if page_results["trust"]["social_link_count"] >= 3:
        trust_score += 2
    elif page_results["trust"]["social_link_count"] >= 1:
        trust_score += 1
    if page_results["tracking"]["total_schema_count"] > 0:
        trust_score += 1
    scores["trust"] = min(10, trust_score)

    # Tracking Score
    track_score = 3
    if page_results["tracking"]["tools_count"] >= 3:
        track_score = 9
    elif page_results["tracking"]["tools_count"] >= 2:
        track_score = 7
    elif page_results["tracking"]["tools_count"] >= 1:
        track_score = 5
    scores["tracking"] = track_score

    page_results["scores"] = scores
    page_results["overall_score"] = round(sum(scores.values()) / len(scores), 1)

    results["analysis"] = page_results
    return results


def main():
    if len(sys.argv) < 2:
        # Demo mode
        print(json.dumps({
            "usage": "uv run python scripts/analyze_page.py <url>",
            "example": "uv run python scripts/analyze_page.py https://flightscope.com",
            "description": "Analyzes a webpage for marketing effectiveness with accurate HTML parsing"
        }, indent=2))
        return

    url = sys.argv[1]
    if not url.startswith("http"):
        url = "https://" + url

    results = analyze(url)
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
