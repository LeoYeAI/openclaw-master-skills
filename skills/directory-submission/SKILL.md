---
name: directory-submission
description: When the user wants to submit a product to directories, launch platforms, curated lists, or app stores. Reads project-context.md when present and generates ready-to-paste submission content per platform. Also use when the user mentions "directory submission," "get listed," "app store listing," "submit to directories," "curated list," "best tools list," "Taaft," "Product Hunt," "directory ads," "newsletter feature," "directory campaign," "product info for directory," "tailor description per platform," "Shopify App Store," "Chrome Web Store," "submit to directory," "launch on Product Hunt," "navigation site," or "product directory."
metadata:
  version: 1.1.0
---

# Channels: Directory Submission

Guides submitting products, tools, or apps to directories and launch platforms.

**On each invocation**: On **first use** in the conversation, output the complete response (Introduction, Importance, Methods, Collaboration Channels, Rules, Avoid, Action). On **subsequent use** or when the user asks to skip (e.g., "just do it", "skip intro", "I already know"), go directly to Action.

Directory submission is a core channel for cold start—see **cold-start-strategy** for full launch planning. Directories offer more than listings: free/paid listings, ad placements, newsletter features, social promotion, and marketing campaigns. Platform types: AI tools (e.g. Taaft), product launch (e.g. Product Hunt), review platforms (e.g. G2), app stores, niche directories.

## Why Directory Submission Matters

*Platform examples are illustrative only. No affiliation, partnership, or endorsement implied.*

| Benefit | Description |
|---------|--------------|
| **Backlinks** | Quality directories pass link equity; improve domain authority and rankings. Focus on high-authority directories (DA 50+); avoid low-quality link farms. |
| **Real traffic & conversion** | Referral traffic from directories converts. ~42% of businesses report increased referral traffic after submission; referral conversion ~1.8% (B2C), 1.1% (B2B), 1.3% (SaaS). Use UTM to track; proper attribution can improve measured conversion by ~23%. |
| **Social proof for brand search** | When users search your brand name, directory listings (e.g. Product Hunt, G2, Taaft) often dominate SERP. Third-party presence signals legitimacy; consumers check 5-7 sources before deciding. Verified badges and consistent NAP across directories boost trust. See **serp-features** for SERP feature types. |

## Current Best Practices

**Quality over quantity.** Mass submission to hundreds of low-quality directories can harm rankings; strategic placement in 10-15 high-quality directories typically yields 15-25% improvement in indexing speed and branded search visibility.

| Practice | Why |
|----------|-----|
| **Prioritize DA/DR 50+** | High-authority directories pass link equity; low-quality link farms risk penalties |
| **Editorial review preferred** | Human-curated directories (vs. automated) carry more weight; Google's Helpful Content Update favors editorially-curated listings |
| **Niche over generic** | Industry-specific directories deliver faster results (30-60 days) and better topical relevance than generic sites (60-120 days) |
| **NAP consistency** | Name, Address, Phone identical across all listings--critical for local SEO |
| **Track submissions** | Document where you submitted, approval status, canonical topics |

**Budget reference**: Small businesses $300-500/mo; enterprises $1,500-3,000/mo for comprehensive programs. Results typically 30-60 days from high-authority directories.

## Initial Assessment

**Read project context first:** If `.claude/project-context.md` or `.cursor/project-context.md` exists, read it. Use sections 1-4, 5, 6, 8, 9 to generate submission content directly--no need to ask the user for info already in the context.

| Context section | Maps to directory fields |
|-----------------|---------------------------|
| 1. Product Overview | Name, one-line, category, pricing model |
| 2. Positioning Statement | Tagline, long description |
| 3. Value Proposition | Key messages, proof points -> Pros |
| 4. Target Audience | Description tone, use cases |
| 5. Existing Website | URL, key pages |
| 6. Keywords | Tags, negative keywords, Primary Task |
| 8. Brand & Voice | Tone, avoid terms, preferred wording — see **branding** for full brand strategy |
| 9. Product Documentation | Features, capabilities -> Other features |

**When context exists**: Generate ready-to-paste submission copy (tagline, short/long description, pros/cons, tags) tailored per platform. Output copy the user can paste into Taaft, Product Hunt, etc.

**When context is missing**: Gather from user's site; **search the web** for pricing, features, competitors, reviews, and any gaps. Then generate.

Identify:
1. **Product type**: AI tool, SaaS, app, Chrome extension, Shopify app
2. **Target directories**: AI tools, product launch, app stores, niche
3. **Readiness**: Landing page, screenshots, description, media kit

## Product / Website Info Required

**Source**: Project context (preferred) or user's site. Each directory needs different fields; prepare a base set, then adapt per platform.

### Standard Fields (Most Directories)

| Field | Typical Spec | Notes |
|-------|--------------|-------|
| **Product name** | 60-80 chars | Consistent spelling across all listings |
| **URL** | Working product/landing page | No redirect chains |
| **Tagline / one-liner** | <=60 chars (Taaft: max 12 words) | Catchy, benefit-focused |
| **Short description** | 150-300 chars | Used by many directories |
| **Long description** | 400-600 chars | For platforms that allow more |
| **Category / Task** | Platform-specific | Match taxonomy (Taaft: Primary + Secondary Tasks) |
| **Keywords / Tags** | 5-10 terms, comma-separated | Natural, no stuffing |
| **Contact** | Email, optional NAP | For verification |
| **Company name** | Legal entity | Some directories require |
| **Promo code** | If applicable | Product Hunt, deal platforms |
| **Other URLs** | Blog, Affiliate Program, FAQ | Optional but useful |
| **API availability** | Yes/No | AI/SaaS directories |
| **Demo video** | URL or file | Many platforms support |

**Platform-specific**: Taaft requires many more fields (icon, main image, demo video, features, models, built-with tools, modalities, pricing, legal URLs, pros/cons, socials, tracking links)--see Taaft section.

### Prepare Asset Tiers

Create multiple versions so you can match each directory's format without rewriting from scratch:

- **One-liner** (<=60 chars): Elevator pitch; "Remote Project Manager Pro" beats "Project Tool"
- **Short** (150-300 chars): Core value + one differentiator
- **Long** (400-600 chars): Problem -> solution story; features + benefits

### Rich Content Base (Build First, Use Everywhere)

Even if a directory form does not require it, build a full reference so you can tailor per platform and for SEO/GEO. **Search the web** when info is missing.

| Section | Content | Use For |
|---------|---------|---------|
| **Definition** | What the product is; category; one-sentence positioning | Intro text, GEO-friendly summaries |
| **Importance** | Why it matters for the target audience; key differentiator | Long descriptions, first comments |
| **Features** | Core capabilities; technical specs; integrations | Taaft, G2, comparison sites |
| **Use cases** | Who uses it; workflows; outcomes | Taaft tasks, niche directories |
| **Solutions** | Problems solved; before/after | Product Hunt, curated lists |
| **Competitors** | Alternatives (e.g. Competitor A, B); how this differs | Comparison sites, G2 |
| **Pricing** | Plans, credits, free tier | G2, Capterra, budget-focused lists |
| **Rules / Avoid** | What to emphasize; what to avoid per platform | Quality control |

### Multiple Versions for Differentiation (SEO & GEO)

**Do not submit identical copy to every directory.** Duplicate content hurts SEO and reduces GEO citation diversity. Generate **at least 2-3 distinct versions** per field (tagline, short, long) so:

- Different directories show different angles
- AI tools and search engines see varied, non-duplicate signals
- Users can pick the best fit per platform or A/B test

| Version | Angle | Best For |
|---------|-------|----------|
| **A** | Feature-led (capabilities, specs) | Taaft, technical directories |
| **B** | Benefit-led (outcomes, use cases) | Product Hunt, creator-focused |
| **C** | Comparison-led (vs. competitors) | AlternativeTo, G2 alternatives |
| **D** | Audience-led (who, workflow) | Niche directories, vertical lists |

## Tailor Per Platform (Different Expression, Different Emphasis)

**Do not copy-paste identical descriptions.** Each directory has a different audience and format; customizing per platform improves approval, visibility, and conversion.

| Platform Type | Audience | Emphasis | Tone |
|---------------|----------|----------|------|
| **Product Hunt** | Indie makers, founders, early adopters | See **product-hunt-launch** for full workflow | Community, authentic, maker-friendly |
| **Taaft** | AI tool seekers, task/job-oriented | Tasks and jobs your tool solves; keyword-rich for AI use cases; "what can I do with this" | Functional, searchable, use-case driven |
| **G2 / Capterra** | Enterprise buyers, comparison shoppers | Features, integrations, pricing; review-oriented; social proof | Professional, comparison-ready |
| **AlternativeTo** | Users switching from competitors | "Alternative to X"; migration ease; differentiation | Comparison, migration, alternatives |
| **Niche directories** | Vertical (e.g., e-commerce, healthcare) | Industry keywords; vertical pain points; compliance if relevant | Vertical-specific, jargon-appropriate |
| **App stores** (Shopify, Chrome) | Merchants / extension users | Merchant value (Shopify); use case (Chrome); screenshots show workflow | Benefit-first, feature-clear |

### Consistency to Keep

While tailoring, keep **consistent** across all listings:

- Product name spelling and formatting
- Core positioning (who it's for, main benefit)
- Contact info format (NAP if applicable)

Inconsistent NAP or product names can hurt SEO and trust.

## Directory Offerings (Beyond Listing)

Directories typically offer multiple touchpoints--not just inclusion in the catalog:

| Offering | Description | Use When |
|----------|-------------|----------|
| **Listing** | Free or paid inclusion in directory catalog | Baseline visibility, backlinks, evergreen traffic |
| **Ad placements** | Sponsored slots, banners, featured placement | Need boosted visibility; budget for paid promotion |
| **Newsletter** | Featured in directory's email to subscribers | Product Hunt, Taaft; high-intent audience |
| **Social promotion** | Directory shares your product on X, LinkedIn, etc. | Launch day amplification; viral potential |
| **Marketing campaigns** | Bundled packages: listing + newsletter + ads + social | Full-funnel campaign; product launch or relaunch |

**Strategy**: Start with free listing for backlinks and baseline traffic. Layer paid options (ads, newsletter features, campaigns) when ROI justifies--especially for launches or when organic listing underperforms.

**dofollow vs nofollow**: dofollow passes link equity for SEO; nofollow does not. But the goal is conversion--if users click through and convert, the shorter path (direct traffic) can outweigh SEO benefit. Small, unknown directories have driven three-figure annual subscriptions from a single 10-minute submission.

### Collaboration Channels (Newsletter, Ads, Social, Campaigns)

**Include this section in output** when the user invokes this skill. Directories offer follow-on collaboration beyond listing:

| Channel | Platform Examples | Scale / Notes |
|---------|-------------------|---------------|
| **Newsletter** | Product Hunt, Taaft | High-intent; paid or bundled; best for launches |
| **Ad placements** | Taaft banners, Product Hunt Featured, G2/Capterra sponsored | Use UTM (e.g. utm_medium=paid); test after organic listing. See **directory-listing-ads** for Taaft, Shopify App Store, G2, Capterra paid campaign setup |
| **Social promotion** | Taaft, Product Hunt share on X, LinkedIn | Launch-day amplification; @ platform accounts when posting |
| **Marketing campaigns** | Taaft: listing + newsletter + ads + social | Full-funnel; product launch or relaunch; budget-dependent |

**Phased approach**: (1) Free listing first. (2) Newsletter features when launching. (3) Ads if organic underperforms. (4) Campaign packages for major launches.

**Budget reference**: Small teams $0-500/mo (listing + occasional newsletter); growth $300-500/mo; enterprise $1,500-3,000+/mo for full programs.

## Directory Types

| Type | Examples | Best For | Traffic / Benefit |
|------|----------|----------|-------------------|
| **AI tools** | Taaft (There's An AI For That) | AI products, SaaS | 4M+ monthly visitors; 700-10K+ visitors per listing |
| **Developer tools** | DevHunt | OSS, dev tools, APIs | Dev-focused; GitHub-verified; free; see **open-source-strategy** |
| **Product launch** | Product Hunt | New products, features | See **product-hunt-launch** for full PH workflow |
| **App stores** | Shopify App Store, Chrome Web Store | Apps, extensions | Merchant/developer discovery |
| **Niche directories** | Industry-specific lists | Vertical SaaS, tools | Targeted backlinks, SEO |
| **Review platforms** | G2, Capterra | B2B SaaS, commercial software | Rich snippets (reviews, ratings); higher-intent buyers; vendor verification required |
| **Curated lists** | Best-of roundups, Awesome lists, niche blog posts | Any product | Editorial backlinks; outreach to list authors; same prep as directories |

**Dimension diversity**: Your product has multiple dimensions--AI tool, productivity tool, SaaS, industry-specific. After AI directories, submit to vertical niches (e.g., e-commerce tools, marketing tools, cross-border commerce tools). Smaller traffic but higher intent and conversion.

**Feature vs solution directories**: Feature directories (text, image, video, audio by modality) suit AI enthusiasts who compare tools. Solution directories (workflow-oriented: SEO tools, EDM marketing, TikTok analytics) suit users seeking 10x productivity in a workflow--often higher conversion for B2B.

## Directory Lists (Curated Lists)

**Same principles as directories**--backlinks, traffic, discovery. Curated lists are editorial roundups (e.g., "Best AI tools 2025," "Top 10 SaaS for marketing") published on blogs, newsletters, or dedicated list sites.

| Type | Examples | How to get listed |
|------|----------|-------------------|
| **Best-of / Top N** | "Best SEO tools," "Top 10 AI writing tools" | Outreach to list authors; provide product info, use case, differentiator |
| **Awesome lists** | GitHub Awesome-*, Awesome Tools | Submit PR or contact maintainer; follow list format. See **github** for creating or optimizing awesome-style curated lists. |
| **Comparison / alternatives** | AlternativeTo, G2 alternatives | Submit as alternative to X; comparison-focused copy |
| **Niche roundups** | Industry blogs, newsletters | Pitch for inclusion; offer quote, case study, or exclusive angle |

**Preparation**: Same as directory submission--product info, tagline, short/long description, screenshots. Tailor pitch to list theme (e.g., "best for startups," "budget-friendly," "enterprise-ready").

**Tip**: One solid backlink from a curated list often beats many low-quality directory links. Prioritize lists with editorial oversight and real traffic.

## Key Platforms

### Taaft (There's An AI For That)

- **URL**: taaft.com/submit or theresanaiforthat.com/submit
- **Scale**: 46K+ AI tools, 4M+ monthly visitors, 2.8M+ newsletter subscribers
- **Listing**: 700-10K+ guaranteed targeted visitors per listing; early launch bonus (up to $300 PPC credits for launching on Taaft first)
- **Beyond listing**: Newsletter features (reach 2.8M+ subs), ad placements, social promotion, marketing campaigns
- **Free vs paid**: Submission fee varies; sometimes free listing is possible (e.g., early action, specific criteria)--check current pricing
- **Use when**: Product is AI-related; want AI-focused traffic, backlinks, and paid amplification options

**Taaft submission fields** (prepare before submitting; changes can take up to 24h to reflect):

| Category | Field | Spec / Notes |
|----------|-------|--------------|
| **Identity** | Name | Product/tool name |
| | Primary Task | Search and select from Taaft task taxonomy (e.g., Text to speech, Image generation) |
| | Secondary Tasks | Search and add; subject to approval, processed daily |
| | Tagline | Max 12 words; benefit-focused |
| | Description | Full product description; use-case driven, keyword-rich |
| | Country | Select from list |
| **Media** | Icon | SVG preferred; PNG/JPEG/WEBP <=500x500 px |
| | Main image | Product screenshot or hero visual |
| | Demo video | Optional; no captions (Taaft auto-generates for all languages) |
| **Features** | Supported features | Check: Agents, API, MCP, Run locally, Open source, No signup, Supports TAAFT code |
| | Other features | Ordered list by importance; add keywords (e.g., ai voice, text to voice, voice cloning) |
| **Tech** | Search models | Add AI models used (e.g., GPT-4, Claude) |
| | Built with | Select from platform options (e.g. Cursor, Lovable, v0.dev) |
| | Modalities | Supported Inputs/Outputs: Text, Image, Audio, Video, 3D, API, Code, etc. |
| **Pricing** | Pricing model | Freemium, Free trial, Paid, etc. |
| | Paid starting price (USD) | If paid |
| | Billing frequency | Monthly, Yearly, etc. |
| | Hard paywall | Does tool show paywall before letting users try? |
| **Legal** | Refund Policy | No Refunds / Custom text |
| | Refund Policy URL | Optional |
| | Privacy Policy URL | Required |
| | Terms & Conditions URL | Required |
| **Discovery** | Tags | Comma-separated; use for search and filtering |
| | Negative keywords | Comma-separated; exclude from irrelevant searches |
| **Tracking** | Tracking link | Custom UTM (default: ?ref=taaft&utm_source=taaft&utm_medium=referral) |
| | PPC tracking link | For PPC ads (default: ?ref=taaft_feat&utm_source=taaft_feat&utm_medium=referral) |
| **Socials** | Facebook, TikTok, Instagram, Telegram, Discord, X, YouTube, LinkedIn | URLs |
| **Pros / Cons** | Pros | Add multiple; feature and benefit bullets |
| | Cons | Add multiple; honest limitations (builds trust) |

**Tip**: Pros and cons help users compare; be honest--negative keywords and cons improve relevance and trust.

### Product Hunt

See **product-hunt-launch** for full preparation, launch day strategy, and post-launch. Product Hunt: producthunt.com/launch; free listing; community upvotes; Product Hunt Daily newsletter; paid featured placement. Use when launching new product or major feature.

### DevHunt (Developer Tools)

- **URL**: devhunt.org
- **Audience**: Developers, indie makers, open source maintainers
- **Content**: Developer tools, APIs, libraries, open source projects; GitHub-verified submissions; 50+ categories
- **Listing**: Free to submit; community-driven; alternative to Product Hunt for dev tools
- **Use when**: Open source or developer tool; want dev-focused discovery. See **open-source-strategy** for full OSS commercialization path.

### Shopify App Store

- **URL**: shopify.dev/docs/apps/launch/shopify-app-store
- **Listing**: App catalog; merchant discovery
- **Beyond listing**: Featured placement, app store ads, partner marketing programs
- **Requirements**: Partner account; session tokens (no third-party cookies); Shopify checkout; app icon 1200x1200; factual listing
- **Use when**: Building Shopify apps; need merchant discovery and optional paid promotion

### Review Platforms (G2, Capterra)

- **Type**: B2B software review platform (vendor-submitted, review-driven); rich snippets (stars, ratings) in SERP; see **serp-features**
- **vs directories**: More complex submission (domain email verification, more fields, features, FAQ); commercialized (membership, paid placement); lower risk than PH ranking--reviews drive priority; higher-paying B2B users
- **Use when**: B2B SaaS; want review-rich SERP presence and enterprise buyers

### Chrome Web Store

- **URL**: developer.chrome.com/docs/webstore
- **Listing**: Extension catalog; user discovery
- **Beyond listing**: Featured placement, promoted listings
- **Requirements**: Extension package; icons, screenshots, description; privacy policy
- **Use when**: Chrome extensions; need user discovery and optional paid promotion

## Submission Checklist

Before submitting to any directory:

- [ ] **Product / website info** gathered (name, URL, tagline, short + long descriptions, keywords)
- [ ] **Asset tiers** prepared (one-liner, short, long) for platform-specific adaptation
- [ ] **Landing page** live and optimized
- [ ] **Product description** clear, benefit-focused (no jargon)
- [ ] **Screenshots / demo** (Product Hunt: 1270x760 recommended)
- [ ] **Logo / icon** per platform specs
- [ ] **Category** selected correctly per directory taxonomy
- [ ] **URL** correct and working
- [ ] **Media kit** (for Product Hunt, press outreach) —see **media-kit-page-generator**
- [ ] **Platform-specific copy** drafted (do not reuse identical text across directories)
- [ ] **Taaft** (if applicable): Full field set--icon, main image, demo video, Primary/Secondary Tasks, features, models, built-with, modalities, pricing, legal URLs, pros/cons, socials, tracking links

## Best Practices

| Practice | Purpose |
|----------|---------|
| **Gather product info first** | Extract from user's site; prepare asset tiers before submitting |
| **Tailor per platform** | Different expression/emphasis per directory; no copy-paste identical text |
| **Prioritize quality** | Rejected or low-quality listings waste effort |
| **Match category** | Wrong category = poor visibility |
| **Unique descriptions** | Avoid duplicate content; improves approval and conversion |
| **Track with UTM** | **analytics-tracking** for attribution |
| **Batch submissions** | Prepare once, adapt copy per platform, submit to multiple directories |
| **Update listings** | Keep descriptions and screenshots current |
| **Submit small directories too** | Major directories get crawled by smaller ones; but small directories can still drive high-value conversions (e.g., three-figure annual subscription from one 10-min submission) |

## Output Format

**On each invocation**: On **first use**, output the complete response (Introduction, Importance, Methods, Collaboration Channels, Rules, Avoid, Action). On **subsequent use** or when the user asks to skip, go directly to Action. Search the web for missing product info.

### Required Output Structure (in order)

1. **Introduction** --What directory submission is: Taaft, Product Hunt, G2, curated lists, app stores; listings, ads, newsletter features, campaigns. Part of cold-start strategy—see **cold-start-strategy** for full launch plan.

2. **Importance** --Why directory submission matters: backlinks and domain authority; referral traffic and conversion (~42% report increased traffic); social proof for brand search (directory listings dominate SERP); third-party presence signals legitimacy.

3. **Methods** --How to submit:
   - **Taaft**: Full field set; Primary/Secondary Tasks; tailor for AI tool seekers
   - **Product Hunt**: See **product-hunt-launch** for full workflow
   - **G2/Capterra**: Features, pricing, verification; comparison-oriented
   - **Curated lists**: Outreach to list authors; pitch per theme

4. **Collaboration Channels (Beyond Listing)** --Newsletter, ads, social, campaigns. Include:
   - **Newsletter**: Taaft (2.8M+ subs), Product Hunt Daily, Future Tools--high-intent; paid or bundled
   - **Ad placements**: Taaft, Product Hunt Featured, G2/Capterra sponsored; use UTM
   - **Social promotion**: Directory shares on X, LinkedIn; launch-day amplification
   - **Campaigns**: Bundled listing + newsletter + ads + social; full-funnel for launches
   - **Phased approach**: Listing first -> Newsletter -> Ads -> Campaigns
   - **Budget reference**: Small $0-500/mo; growth $300-500/mo; enterprise $1,500-3,000+/mo

5. **Rules** --Tailor per platform; different expression per directory; multiple versions (A/B/C/D) to avoid duplicate content (SEO/GEO friendly); match category; prepare asset tiers (one-liner, short, long).

6. **Avoid** --Copy-paste identical copy across directories; generic descriptions; missing legal URLs; wrong category; low-quality link farms.

7. **Action** --Ready-to-paste submission content for the user's product:
   - **Rich content base** (features, use cases, solutions, competitors, pricing)--search web if missing
   - **Multiple versions** for tagline, short, long--each directory gets distinct copy
   - **Platform-specific** copy for Taaft, G2, AlternativeTo, etc.; Product Hunt → **product-hunt-launch**
   - **Readiness checklist**, **submission order**, **UTM templates**

## Bulk Submission

**Manual**: Prepare info once; submit to directories in priority order. Major directories first--smaller ones often crawl or republish.

**Outsourced**: Freelance platforms; use when budget allows and speed matters.

## Related Resources

- **project-context** (`.cursor/project-context.md` or `.claude/project-context.md`): Read when present; use to generate submission content directly. Template: `templates/project-context.md` in this repo.
- **Alignify directory guide**: [alignify.co/zh/insights/directory-submission-sites](https://alignify.co/zh/insights/directory-submission-sites) --Cold-start strategy, preparation checklist, review platforms, vertical directories, bulk submission.

## Related Skills

- **branding**: Brand strategy, voice, tone; Section 8 Brand & Voice in project-context
- **media-kit-page-generator**: Press kit, screenshots, assets for launch; required for Product Hunt and directory submissions
- **link-building**: Directory and curated list backlinks contribute to link profile; this skill handles the submission workflow—see **link-building** for broader outreach, guest posting, broken link building
- **github**: GitHub awesome lists as curated lists; create or submit to awesome-* repos
- **open-source-strategy**: Open source commercialization; DevHunt, GitHub, Awesome lists for OSS projects
- **grokipedia-recommendations**: Same output pattern--platform context first (Introduction, Importance, Methods, Rules, Avoid), then Action; high-authority placement for GEO; directories for human discovery--complementary
- **generative-engine-optimization**: GEO strategy; varied directory copy improves AI citation diversity; directory submission complements AI search visibility
- **affiliate-marketing**: Different channel; directories complement affiliate
- **cold-start-strategy**: Cold start orchestrates directory-submission, Product Hunt, Reddit, Indie Hackers; this skill handles directory submission workflow
- **indie-hacker-strategy**: Indie hacker Product Hunt, first 100 users; Build in Public
- **directory-listing-ads**: Paid promotions within Taaft, Shopify App Store, G2, Capterra; use after listing is live
- **community-forum**: Forum promotion (HN, Indie Hacker); community invitation; different from directory listing
- **analytics-tracking**: UTM for directory traffic attribution
- **serp-features**: SERP features; directory listings in brand search SERP
