# Marketing Report Generator (Markdown Format)

## Skill Purpose
Generate a comprehensive, professionally formatted marketing report in Markdown. This skill compiles data from all previous audit and analysis results into a single, client-ready document with scores, findings, recommendations, and a prioritized action plan with revenue impact estimates.

## When to Use
- User wants a full marketing report for a client or their own business
- User has completed one or more audit skills and wants a compiled report
- User asks for a marketing assessment, scorecard, or analysis document
- Triggered by `/market report` or `/market report <domain>`

## How to Execute

### Step 1: Collect All Available Data
Before generating the report, check for any existing audit data from previous skill runs. Look for these files in the project directory:

**Possible data sources:**
- `MARKETING-AUDIT.md` -- from `/market audit`
- `LANDING-CRO.md` -- from `/market landing`
- `SEO_AUDIT.md` -- from `/market seo`
- `BRAND-VOICE.md` -- from `/market brand`
- `COMPETITOR-REPORT.md` -- from `/market competitors`
- `FUNNEL-ANALYSIS.md` -- from `/market funnel`
- `AD-CAMPAIGNS.md` -- from `/market ads`
- `SOCIAL-CALENDAR.md` -- from `/market social`
- `EMAIL-SEQUENCES.md` -- from `/market emails`
- `COPY-SUGGESTIONS.md` -- from `/market copy`

If no previous data exists, inform the user and offer to:
1. Run a quick audit first (recommended)
2. Generate a report based on available information (website URL, user-provided data)
3. Create a report template they can fill in

### Step 2: Calculate the Marketing Scorecard

Use the same 6-category scoring model as `/market audit`. If `MARKETING-AUDIT.md` exists, treat its category scores as the source of truth and preserve them in the compiled report. Only calculate fallback scores manually when `MARKETING-AUDIT.md` is not available.

#### Category 1: Content & Messaging (Weight: 25%)
Evaluate based on homepage copy, landing page messaging, value proposition clarity, brand voice, and content quality.

| Factor | Points Available | Criteria |
|---|---|---|
| Headline clarity | 20 | Specific and audience-targeted = 20, understandable but generic = 12, vague = 5, missing = 0 |
| Value proposition strength | 25 | Clear differentiation and benefits = 25, partially clear = 15, weak = 7, missing = 0 |
| Body copy persuasion | 20 | Benefits-first and objection-aware = 20, adequate = 12, feature-dump = 5, weak = 0 |
| Social proof quality | 15 | Specific and credible = 15, some proof = 10, minimal = 5, none = 0 |
| Content depth and authority | 20 | Expert and substantive = 20, solid = 13, thin = 6, poor = 0 |

#### Category 2: Conversion Optimization (Weight: 20%)
Evaluate based on CTA quality, form friction, visual hierarchy, trust signals, and funnel flow.

| Factor | Points Available | Criteria |
|---|---|---|
| CTA effectiveness | 25 | Specific, visible, repeated = 25, adequate = 15, weak = 7, poor = 0 |
| Form friction | 20 | Minimal friction = 20, acceptable = 12, high friction = 5, severe = 0 |
| Visual hierarchy | 20 | Clear eye path to conversion = 20, decent = 12, cluttered = 5, poor = 0 |
| Trust near conversion | 20 | Proof and reassurance near CTAs = 20, some = 12, weak = 5, none = 0 |
| Funnel flow and mobile UX | 15 | Smooth and mobile-friendly = 15, mostly solid = 10, weak = 5, broken = 0 |

#### Category 3: SEO & Discoverability (Weight: 20%)
Evaluate based on technical SEO, on-page optimization, internal linking, and structured data.

| Factor | Points Available | Criteria |
|---|---|---|
| Title/meta optimization | 15 | Strong = 15, present with issues = 10, weak = 5, missing = 0 |
| Heading hierarchy | 15 | Logical and keyword-aligned = 15, mostly good = 10, weak = 5, broken = 0 |
| Technical SEO | 20 | Strong foundation = 20, minor issues = 13, major issues = 7, critical = 0 |
| Internal linking | 15 | Strategic = 15, present = 10, minimal = 5, poor = 0 |
| Structured data | 15 | Comprehensive = 15, partial = 10, minimal = 5, none = 0 |
| Content quality / E-E-A-T | 20 | Strong = 20, good = 13, average = 7, weak = 0 |

#### Category 4: Competitive Positioning (Weight: 15%)
Evaluate based on differentiation, alternatives awareness, pricing context, and market positioning.

| Factor | Points Available | Criteria |
|---|---|---|
| Positioning clarity | 30 | Distinct and targeted = 30, somewhat clear = 18, generic = 8, weak = 0 |
| Alternatives awareness | 20 | Comparison content exists = 20, partial = 12, weak = 5, none = 0 |
| Pricing clarity | 20 | Clear and contextualized = 20, partial = 12, weak = 5, absent = 0 |
| Feature differentiation | 15 | Clear proof of superiority = 15, some differentiation = 10, weak = 4, none = 0 |
| Market authority signals | 15 | Strong = 15, adequate = 10, weak = 4, none = 0 |

#### Category 5: Brand & Trust (Weight: 10%)
Evaluate based on trust signals, design credibility, contact transparency, and proof of legitimacy.

| Factor | Points Available | Criteria |
|---|---|---|
| Trust signals | 35 | Multiple strong signals = 35, some = 22, weak = 10, none = 0 |
| Design quality | 25 | Professional and consistent = 25, adequate = 15, dated = 7, poor = 0 |
| Contact transparency | 20 | Clear and complete = 20, partial = 12, weak = 5, missing = 0 |
| Authority signals | 20 | Strong credentials/proof = 20, some = 12, weak = 5, none = 0 |

#### Category 6: Growth & Strategy (Weight: 10%)
Evaluate based on pricing logic, acquisition channels, lifecycle marketing, and retention/growth systems.

| Factor | Points Available | Criteria |
|---|---|---|
| Pricing strategy | 25 | Clear and compelling = 25, decent = 15, weak = 7, poor = 0 |
| Acquisition diversity | 25 | Multiple active channels = 25, some = 15, limited = 7, none = 0 |
| Lifecycle systems | 20 | Email/referral/retention systems present = 20, partial = 12, weak = 5, none = 0 |
| Content and growth loops | 15 | Clear compounding channels = 15, some = 10, weak = 4, none = 0 |
| Measurement and iteration | 15 | Evidence of tracking/optimization = 15, partial = 10, weak = 4, none = 0 |

#### Overall Score Calculation
```
Overall Score = (Content & Messaging * 0.25) + (Conversion Optimization * 0.20) + (SEO & Discoverability * 0.20) + (Competitive Positioning * 0.15) + (Brand & Trust * 0.10) + (Growth & Strategy * 0.10)
```

**Score Interpretation:**
| Score Range | Rating | Meaning |
|---|---|---|
| 85-100 | Excellent | Marketing is a competitive advantage. Optimize and scale. |
| 70-84 | Good | Solid foundation with clear improvement opportunities. |
| 55-69 | Average | Functional but leaving significant growth on the table. |
| 40-54 | Below Average | Multiple areas need attention. Significant opportunity cost. |
| 0-39 | Critical | Marketing is actively hurting growth. Immediate action required. |

### Step 3: Write Category Deep-Dives

For each of the 6 categories, provide:

1. **Score and Rating** -- X/100 with interpretation
2. **Key Findings** -- 3-5 specific observations with evidence
3. **What's Working** -- Positive elements to preserve and build on
4. **Gaps and Issues** -- Problems identified with severity ratings
5. **Recommendations** -- Specific, actionable improvements ranked by impact
6. **Revenue Impact Estimate** -- Estimated financial impact of implementing recommendations

**Revenue Impact Estimation Framework:**
```
Impact = (Estimated traffic change * Conversion rate change * Average deal value) * Confidence factor

Example:
- Current monthly traffic: 10,000
- Recommended SEO improvements could increase traffic 30%: +3,000 visits
- Current conversion rate: 2%, CRO could improve to 3%: +1% = +130 conversions
- Average deal value: $500
- Estimated monthly revenue impact: $65,000
- Confidence factor (conservative): 0.5
- Conservative estimate: $32,500/month additional revenue
```

### Step 4: Competitor Comparison Summary
If competitor data is available from `/market competitors`, include:

**Competitive Positioning Matrix:**
| Factor | Client | Competitor 1 | Competitor 2 | Competitor 3 |
|---|---|---|---|---|
| Website Quality | X/10 | X/10 | X/10 | X/10 |
| SEO Visibility | X/10 | X/10 | X/10 | X/10 |
| Content Quality | X/10 | X/10 | X/10 | X/10 |
| Social Presence | X/10 | X/10 | X/10 | X/10 |
| Overall Position | Xth/4 | Xth/4 | Xth/4 | Xth/4 |

**Competitive Advantages:** What the client does better
**Competitive Gaps:** Where competitors outperform the client
**Opportunities:** Spaces competitors are not addressing

### Step 5: Content Quality Assessment
Summarize content findings across all channels:

- **Website copy** -- Clarity, persuasiveness, brand alignment
- **Blog content** -- Depth, expertise, SEO optimization, publishing cadence
- **Social media content** -- Engagement quality, brand consistency, platform optimization
- **Email content** -- Subject line effectiveness, body copy quality, CTA strength
- **Ad creative** -- Messaging clarity, visual quality, offer presentation

### Step 6: Conversion Optimization Summary
Compile all conversion-related findings:

- **Primary conversion paths** -- How visitors become customers
- **Funnel leaks** -- Where potential customers drop off
- **CRO quick wins** -- Changes that can be implemented immediately
- **Testing opportunities** -- A/B tests recommended with hypotheses
- **Benchmark comparison** -- Current rates vs industry standards

### Step 7: SEO Snapshot
Summarize SEO health in a scannable format:

```
SEO Health Snapshot:
- Title Tags: [Optimized / Needs Work / Missing]
- Meta Descriptions: [Optimized / Needs Work / Missing]
- H1 Tags: [Proper / Issues / Missing]
- Image Alt Text: [Complete / Partial / Missing]
- Page Speed: [Fast / Moderate / Slow]
- Mobile-Friendly: [Yes / Partially / No]
- Schema Markup: [Present / Partial / Missing]
- Robots.txt: [Configured / Issues / Missing]
- Sitemap: [Present / Issues / Missing]
- HTTPS: [Yes / No]
- Core Web Vitals: [Pass / Needs Work / Fail]
```

### Step 8: Build the Prioritized Action Plan

Organize all recommendations into three tiers:

#### Quick Wins (Implement This Week)
High impact, low effort changes. These should be implementable within 1-5 business days.

Format each item as:
```
- [ ] [Action item]: [Specific description]
  - Impact: [HIGH/MEDIUM/LOW]
  - Effort: [1-5 hours]
  - Expected Result: [Specific outcome]
  - Revenue Impact: [$X/month estimated]
```

#### Medium-Term (Implement This Month)
Moderate impact, moderate effort. These require 1-4 weeks.

#### Strategic (Implement This Quarter)
High impact, high effort. These are foundational changes that require planning and sustained effort.

### Step 9: Build the 30-60-90 Day Roadmap

**Days 1-30: Foundation & Quick Wins**
- Week 1: Implement all quick wins from the action plan
- Week 2: Set up tracking and analytics baseline
- Week 3: Begin medium-term improvements
- Week 4: First performance review and adjustment

**Days 31-60: Growth & Optimization**
- Week 5-6: Launch core campaign improvements
- Week 7: A/B testing program begins
- Week 8: Content strategy implementation

**Days 61-90: Scale & Expand**
- Week 9-10: Scale what's working, cut what isn't
- Week 11: Expand to new channels or campaigns
- Week 12: Comprehensive review, update strategy for next quarter

### Step 10: Appendix

Include methodology notes so the client understands how scores were derived:

**Scoring Methodology:**
- How each category was evaluated
- Data sources used
- Benchmarks referenced
- Limitations and assumptions
- Date of analysis

**Tools Used:**
- List any tools or scripts used in the analysis
- Reference to scripts/analyze_page.py if used

**Glossary:**
- Define marketing terms that a non-marketer client may not know
- Keep it relevant to terms used in the report

## Output Format

Generate a file called `MARKETING-REPORT.md` with:

```markdown
# Marketing Report
## [Company/Domain Name]
### Prepared by: [Agent/Agency Name]
### Date: [Date]

---

## Executive Summary

### Overall Marketing Score: [X/100] -- [Rating]

[2-3 paragraph summary covering: current state assessment, top 3 findings, estimated revenue impact of implementing recommendations, and recommended first steps]

### Score Breakdown
| Category | Score | Rating |
|---|---|---|
| Content & Messaging | X/100 | [Rating] |
| Conversion Optimization | X/100 | [Rating] |
| SEO & Discoverability | X/100 | [Rating] |
| Competitive Positioning | X/100 | [Rating] |
| Brand & Trust | X/100 | [Rating] |
| Growth & Strategy | X/100 | [Rating] |
| **Overall** | **X/100** | **[Rating]** |

### Top 3 Priority Actions
1. [Most impactful recommendation with revenue estimate]
2. [Second most impactful recommendation]
3. [Third most impactful recommendation]

---

## Detailed Findings

### 1. Content & Messaging [X/100]
[Deep-dive analysis with findings, what's working, gaps, recommendations]

### 2. Conversion Optimization [X/100]
[Deep-dive analysis]

### 3. SEO & Discoverability [X/100]
[Deep-dive analysis]

### 4. Competitive Positioning [X/100]
[Deep-dive analysis]

### 5. Brand & Trust [X/100]
[Deep-dive analysis]

### 6. Growth & Strategy [X/100]
[Deep-dive analysis]

---

## Competitor Comparison
[Matrix and analysis]

---

## SEO Snapshot
[Health checklist]

---

## Conversion Optimization Summary
[Funnel analysis and CRO recommendations]

---

## Revenue Impact Summary
| Recommendation | Estimated Monthly Impact | Confidence | Priority |
|---|---|---|---|
| [Rec 1] | $X,XXX | High/Medium/Low | 1 |
| [Rec 2] | $X,XXX | High/Medium/Low | 2 |
| ... | ... | ... | ... |
| **Total Estimated Impact** | **$XX,XXX/month** | | |

---

## Prioritized Action Plan

### Quick Wins (This Week)
- [ ] [Action items with impact and effort]

### Medium-Term (This Month)
- [ ] [Action items]

### Strategic (This Quarter)
- [ ] [Action items]

---

## 30-60-90 Day Roadmap
[Week-by-week plan]

---

## Appendix
### Methodology
### Tools Used
### Glossary
### Data Sources
```

## Key Principles
- This report should be impressive enough to use as a sales tool. A well-crafted marketing report can open the door to a client engagement.
- Always lead with insights and opportunities, not criticism. Frame everything through the lens of growth potential.
- Quantify everything possible. "$32,000/month in unrealized revenue" is more compelling than "you're leaving money on the table."
- Make the action plan so specific that someone could hand it to a junior marketer and they could execute it.
- Use professional formatting: consistent headers, tables for data, checkboxes for action items, clear visual hierarchy.
- If data from previous skills is available, reference specific findings. If not, be transparent about what's based on analysis vs estimation.
- The report should tell a story: Here's where you are, here's where you could be, here's how to get there, and here's what it's worth.
