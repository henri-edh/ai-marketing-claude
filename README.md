<p align="center">
  <img src="banner.svg" alt="AI Marketing Suite for Claude Code" width="100%">
</p>

# AI Marketing Suite for Claude Code

A comprehensive marketing analysis and automation skill system for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Audit any website's marketing, generate copy, build email sequences, create content calendars, analyze competitors, and produce client-ready PDF reports — all from your terminal.

**Built for entrepreneurs, agency builders, and solopreneurs who want to sell marketing services powered by AI.**

---

## What This Does

Type a command in Claude Code and get instant, actionable marketing analysis:

```
> /market audit https://calendly.com

Launching 5 parallel agents...
✓ Content & Messaging Analysis     — Score: 72/100
✓ Conversion Optimization          — Score: 58/100
✓ SEO & Discoverability            — Score: 81/100
✓ Competitive Positioning          — Score: 64/100
✓ Brand & Trust                    — Score: 76/100
✓ Growth & Strategy                — Score: 61/100

Overall Marketing Score: 69/100

Full report saved to MARKETING-AUDIT.md
```

---

## Installation

### One-Command Install

```bash
curl -fsSL https://raw.githubusercontent.com/zubair-trabzada/ai-marketing-claude/main/install.sh | bash
```

### Manual Install

```bash
git clone https://github.com/zubair-trabzada/ai-marketing-claude.git
cd ai-marketing-claude
./install.sh
```

### What Gets Installed

- **UV** (Python package manager) — automatically installed if not present
- **Python 3.13** virtual environment — managed by UV
- **All 15 marketing skills** — installed under `~/.claude/skills/`
- **5 parallel analysis agents** — installed to `~/.claude/agents/`
- **7 Python utility scripts** — including the full SEO evidence and rendered-verification pipeline
- **6 marketing templates** — email sequences, proposals, calendars
- **Shared accuracy guardrails** — installed for analytical skills and agents

### Optional: Browserless for Rendered SEO Verification

`/market seo` now defaults to Browserless-backed rendered verification when you run the verification script directly. Add a token to your shell or `.env`:

```bash
export BROWSERLESS_TOKEN=your_token_here
```

If Browserless is unavailable, you can fall back to the bundled Playwright wrapper:

```bash
uv run python scripts/verify_rendered_seo.py seo_evidence.json rendered_verification.json --provider local-playwright-cli
```

### Optional: PDF Report Support

The installer will attempt to install `reportlab` automatically. To enable PDF reports manually:

```bash
# After installation, use the UV Python environment
uv pip install reportlab --python ~/.claude/skills/market/.venv/bin/python
```

---

## Commands

| Command | What It Does |
|---------|-------------|
| `/market audit <url>` | Full marketing audit with 5 parallel agents |
| `/market quick <url>` | 60-second marketing snapshot |
| `/market copy <url>` | Generate optimized copy with before/after examples |
| `/market emails <topic>` | Generate complete email sequences |
| `/market social <topic>` | 30-day social media content calendar |
| `/market ads <url>` | Ad creative and copy for all platforms |
| `/market funnel <url>` | Sales funnel analysis and optimization |
| `/market competitors <url>` | Competitive intelligence report |
| `/market landing <url>` | Landing page CRO analysis |
| `/market launch <product>` | Product launch playbook |
| `/market proposal <client>` | Client proposal generator |
| `/market report <url>` | Full marketing report (Markdown) |
| `/market report-pdf <url>` | Professional marketing report (PDF) |
| `/market seo <url>` | SEO content audit with improved accuracy |
| `/market brand <url>` | Brand voice analysis and guidelines |

---

## Architecture

```
ai-marketing-claude/
├── market/SKILL.md                     # Main orchestrator (routes all /market commands)
│
├── skills/                             # 14 sub-skills
│   ├── market-audit/SKILL.md           # Full audit orchestration
│   ├── market-copy/SKILL.md            # Copywriting analysis & generation
│   ├── market-emails/SKILL.md          # Email sequence generation
│   ├── market-social/SKILL.md          # Social media content calendar
│   ├── market-ads/SKILL.md             # Ad creative & copy
│   ├── market-funnel/SKILL.md          # Funnel analysis & optimization
│   ├── market-competitors/SKILL.md     # Competitive intelligence
│   ├── market-landing/SKILL.md         # Landing page CRO
│   ├── market-launch/SKILL.md          # Launch playbook generation
│   ├── market-proposal/SKILL.md        # Client proposal generator
│   ├── market-report/SKILL.md          # Marketing report (Markdown)
│   ├── market-report-pdf/SKILL.md      # Marketing report (PDF)
│   ├── market-seo/SKILL.md             # SEO content audit (improved accuracy)
│   └── market-brand/SKILL.md           # Brand voice analysis
│
├── agents/                             # 5 parallel subagents
│   ├── market-content.md               # Content & messaging analysis
│   ├── market-conversion.md            # CRO & funnel optimization
│   ├── market-competitive.md           # Competitive positioning
│   ├── market-technical.md             # Technical SEO & tracking
│   └── market-strategy.md              # Brand, pricing & growth strategy
│
├── skills/ACCURACY-GUARDRAILS.md       # Shared accuracy rules for all analytical skills
│
├── scripts/                            # Python utility scripts
│   ├── analyze_page.py                 # Webpage marketing analysis (improved parser)
│   ├── collect_seo_evidence.py         # Representative page-set collector for SEO audits
│   ├── verify_rendered_seo.py          # Browser-rendered verification for critical SEO findings
│   ├── generate_seo_audit_report.py    # Deterministic SEO_AUDIT.md generator from evidence artifacts
│   ├── competitor_scanner.py           # Competitor website scanner (SSL-verified)
│   ├── social_calendar.py              # Social content calendar generator (validated input)
│   └── generate_pdf_report.py          # PDF report generator (data-driven weights)
│
├── templates/                          # Marketing templates
│   ├── email-welcome.md                # Welcome email sequence (5 emails)
│   ├── email-nurture.md                # Lead nurture sequence (6 emails)
│   ├── email-launch.md                 # Product launch sequence (8 emails)
│   ├── proposal-template.md            # Client proposal template
│   ├── content-calendar.md             # 30-day content calendar
│   └── launch-checklist.md             # Launch checklist
│
├── install.sh                          # One-command installer (UV-enabled)
├── uninstall.sh                        # Clean uninstaller
├── requirements.txt                    # Python dependencies
├── pyproject.toml                      # Python project configuration
├── .python-version                     # Python version specification
└── LICENSE                             # MIT License
```

---

## Scoring Methodology

The full marketing audit scores websites across 6 dimensions:

| Category | Weight | What It Measures |
|----------|--------|------------------|
| Content & Messaging | 25% | Copy quality, value props, headlines, CTAs |
| Conversion Optimization | 20% | Funnels, forms, social proof, friction, urgency |
| SEO & Discoverability | 20% | On-page SEO, technical SEO, content structure |
| Competitive Positioning | 15% | Differentiation, market awareness, alternatives |
| Brand & Trust | 10% | Design quality, trust signals, authority |
| Growth & Strategy | 10% | Pricing, acquisition channels, retention |

**Overall Marketing Score** = Weighted average of all categories (0-100)

---

## How It Works

1. **You type a command** — e.g., `/market audit https://example.com`
2. **Claude reads the skill files** — they tell Claude exactly how to analyze the site
3. **5 subagents launch in parallel** — each one analyzes a different dimension
4. **Python scripts run** — automated page analysis with accurate HTML parsing
5. **Results are compiled** — into a scored, prioritized, actionable report
6. **Output is saved** — as a Markdown file or professional PDF

### Accuracy Guardrails

All analytical skills follow mandatory accuracy rules to prevent false findings:

- **Never fabricate URLs** — only reference pages actually fetched or found in links
- **JavaScript-rendering awareness** — flags when content may be dynamically loaded
- **Confidence levels** — every finding tagged as Confirmed, Likely, or Needs Verification
- **Scraper limitation transparency** — reports always disclose methodology limitations
- **Design choices vs failures** — distinguishes intentional design decisions from actual problems
- **Verification checklists** — built into every analytical skill's output process

### Improved SEO Analysis

The SEO analysis script includes:

- **Accurate title tag extraction** — only from `<head>`, ignoring SVG elements
- **Heading context tracking** — distinguishes nav/footer headings from content headings
- **Multiple structured data formats** — JSON-LD, Microdata, and RDFa detection
- **Redirect analysis** — tracks www vs non-www, redirect chains
- **Section-aware analysis** — understands semantic HTML5 sections (main, nav, header, footer, aside)

### Scoring Calibration

All 5 audit subagents include concrete scoring examples (what a 2/10, 5/10, and 9/10 looks like) to ensure consistent, reproducible scores across different analyses.

### Cross-Skill Integration

Skills automatically detect and use output from other skills:

| Skill Writes | Other Skills Read It |
|---|---|
| `MARKETING-AUDIT.md` | copy, emails, funnel, report, report-pdf, proposal |
| `COMPETITOR-REPORT.md` | copy, ads, funnel, social, report, report-pdf |
| `BRAND-VOICE.md` | copy, social, emails, report, report-pdf |
| `COPY-SUGGESTIONS.md` | ads, funnel, emails, social, competitors |
| `SEO_AUDIT.md` | report, report-pdf, proposal |
| `FUNNEL-ANALYSIS.md` | ads, emails, competitors, report |
| `EMAIL-SEQUENCES.md` | funnel, social, report |
| `AD-CAMPAIGNS.md` | report, report-pdf |
| `SOCIAL-CALENDAR.md` | ads, report, report-pdf |
| `LANDING-CRO.md` | report, report-pdf, proposal |

---

SEO audits are generated as standalone fresh runs. Other skills may read `SEO_AUDIT.md` as an output artifact, but `/market seo` should not consume prior audit markdown as an input unless the user explicitly asks for a comparison.

---

## Use Cases

### For Agency Builders
- Run `/market audit` on a prospect's website before a sales call
- Generate `/market proposal` with specific findings and pricing
- Deliver `/market report-pdf` as a professional client deliverable

### For Solopreneurs
- Use `/market copy` to optimize your own landing pages
- Generate `/market emails` for your product launches
- Build `/market social` calendars for consistent posting

### For Content Creators
- Research competitors with `/market competitors`
- Plan launches with `/market launch`
- Analyze your funnel with `/market funnel`

---

## Python Environment

This project uses **UV** for fast, reliable Python package management:

- Virtual environment: `~/.claude/skills/market/.venv`
- Python helper script: `~/.claude/skills/market/python-env.sh`
- All Python scripts should run through the UV-managed environment

To run Python scripts manually:

```bash
uv run python scripts/analyze_page.py <url>
uv run python scripts/collect_seo_evidence.py <url> seo_evidence.json --profile deep
export BROWSERLESS_TOKEN=your_token_here
uv run python scripts/verify_rendered_seo.py seo_evidence.json rendered_verification.json
```

Local fallback if you explicitly want the bundled Playwright CLI instead:

```bash
uv run python scripts/verify_rendered_seo.py seo_evidence.json rendered_verification.json --provider local-playwright-cli
```

---

## Uninstall

```bash
./uninstall.sh
```

Or manually:
```bash
rm -rf ~/.claude/skills/market*
rm -f ~/.claude/agents/market-*.md
```

---

## Learn More

Want to learn how to build a marketing agency powered by AI tools like this?

**[Join the AI Workshop Community](https://www.skool.com/aiworkshop)** — Learn AI automations, vibe coding, and how to build AI-powered services for clients.

---

## Recent Improvements

### v2.1 — Accuracy & Reliability Update

**Accuracy Guardrails (Critical)**
- Added shared `ACCURACY-GUARDRAILS.md` with 8 mandatory rules for all analytical skills
- Ported guardrails to market-landing, market-copy, market-funnel, market-competitors, and market-brand
- Added verification checklists to prevent hallucinated findings (fabricated URLs, misquoted copy)
- All 5 audit subagents now include scoring calibration examples for consistent scoring

**Security & Stability Fixes**
- `competitor_scanner.py`: Re-enabled SSL certificate verification (was disabled — MITM risk)
- `competitor_scanner.py`: Replaced bare `except:` blocks with proper error handling and logging
- `social_calendar.py`: Added input validation (platform names, day bounds 1-90, error messages)

**Cross-Skill Integration Fixes**
- Fixed 5 incorrect file references in report and report-pdf skills (e.g., `COMPETITOR-ANALYSIS.md` → `COMPETITOR-REPORT.md`)
- All skills now reference correct output filenames for seamless cross-skill data sharing

**Feature Additions**
- `market-emails`: Comprehensive deliverability checklist (CAN-SPAM, GDPR, spam triggers, sender reputation)
- `market-ads`: Platform policy compliance checks for Meta, Google, and LinkedIn
- `market-launch`: Launch size parameter (Minimal/Standard/Full) to scope output appropriately
- `market-funnel`: Revenue estimates now labeled with `[ESTIMATE]` tags and "Data Needed" section
- `market-proposal`: Auto-population table mapping 7 prior audit files to proposal sections
- `generate_pdf_report.py`: Weights now read from JSON data; intelligent label abbreviation
- `social_calendar.py`: Hook formulas expanded from 6 to 15 per platform
- `competitor_scanner.py`: Pricing page detection expanded from 3 to 7 URL paths

---

## License

MIT License — see [LICENSE](LICENSE) for details.
