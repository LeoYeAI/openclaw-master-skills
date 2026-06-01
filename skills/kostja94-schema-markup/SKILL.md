---
name: schema-markup
description: When the user wants to add or optimize structured data (Schema.org, JSON-LD). Also use when the user mentions "schema," "structured data," "JSON-LD," "rich results," "rich snippets," "Google rich snippets," "featured snippet schema," "add schema to page," "missing structured data," "schema validation error," "Schema Markup Validator," "Google Rich Results Test," "FAQ schema," "Article schema," "Organization schema," "JobPosting," "HowTo," "Event," "SoftwareApplication," "BreadcrumbList," "WebSite," "Recipe," "Product," "Dataset," or "GEO."
metadata:
  version: 1.3.0
---

# SEO On-Page: Schema / Structured Data

Guides implementation of Schema.org structured data (JSON-LD) for rich snippets, enhanced search results, and Generative Engine Optimization (GEO).

**When invoking**: On **first use**, if helpful, open with 1–2 sentences on what this skill covers and why it matters, then provide the main output. On **subsequent use** or when the user asks to skip, go directly to the main output.

## Scope (On-Page SEO)

- **Schema markup**: Schema.org types for rich results, AI search visibility, and machine-readable content
- **Schema.org vs. search engines**: Schema.org defines 800+ types; each search engine supports only a subset for rich results

## Schema.org vs. Search Engine Support

**Schema.org and Google Structured Data are not fully aligned.** Schema.org is an open vocabulary (800+ types); Google, Bing, and other engines each support only a curated subset for rich results.

| Engine | Support | Notes |
|--------|---------|-------|
| **Google** | Subset only | Only types in [Google's search gallery](https://developers.google.com/search/docs/guides/search-gallery) generate rich results. Valid Schema.org markup not in Google's list won't produce enhanced snippets—even if technically correct. |
| **Bing** | Subset; different | Supports JSON-LD, Microdata, RDFa, Open Graph. Some types (e.g., Product, Offer) have format-specific support. Check [Bing Webmaster docs](https://www.bing.com/webmasters/help/marking-up-your-site-with-structured-data-3a93e731). |
| **Other engines** | Varies | Yandex, DuckDuckGo, AI search tools (Perplexity, etc.) may use Schema.org for understanding even when they don't display rich results. |

**Practical implication**: Implement Schema.org markup for your content type. If Google doesn't show rich results for that type, Bing or AI systems may still use it. Always verify against [Google's developer docs](https://developers.google.com/search/docs) for Google-specific rich result eligibility.

## Rich Results: Google Support (2025)

**High-impact types**: Product, Review snippets, HowTo (desktop), Article/News, Video, Recipe, LocalBusiness, Event, Breadcrumb, Sitelinks searchbox, JobPosting.

**Limited or context-dependent**: HowTo (mobile), FAQ (government/health sites for many queries), Education Q&A, Course, SoftwareApplication, Speakable (news), DiscussionForumPosting.

**Deprecated**: COVID data panels, some AMP-only formats, data-vocabulary.org.

**Implementation**: JSON-LD preferred; include `@context`, `@type`, stable `@id`; ISO 8601 dates; match structured data to visible content. Validate with [Rich Results Test](https://search.google.com/test/rich-results). Rich results can increase CTR up to ~35% and improve AI citation. [AISO Hub](https://aiso-hub.com/insights/google-rich-results-types/), [Digital Applied](https://www.digitalapplied.com/blog/structured-data-seo-2026-rich-results-guide)

## Schema ↔ SERP Features ↔ Rich Results (Strongly Related)

**Schema, SERP features, and rich results are strongly related.** Schema is the **necessary condition** for most rich results. When targeting a SERP feature, implement the corresponding schema type. See **serp-features** for the full SERP feature list and optimization.

### Rich Results vs Featured Snippets

- **Rich results**: Schema-powered enhancements to standard listings (stars, breadcrumbs, FAQ dropdowns, product info). Appear within organic positions; do not require top-10 rank.
- **Featured snippets**: Google-extracted answer boxes at position zero. No schema required; content structure matters. Schema (FAQPage, HowTo, Article) can support extraction.

| Schema Type | SERP Feature / Rich Result | Notes |
|-------------|----------------------------|-------|
| **FAQPage** | PAA, Featured Snippet | FAQ dropdown; Q&A-style snippet. Eligibility restricted for many sites (e.g. government/health) |
| **BreadcrumbList** | Breadcrumbs | Path display in result |
| **AggregateRating, Review** | Reviews / Stars | Star ratings |
| **HowTo** | Featured Snippet (list) | Step-based snippet; desktop support; mobile may be limited |
| **Article** | In-Depth Articles, Snippet | Article rich result |
| **VideoObject** | Video | Video thumbnail; see **video-optimization** |
| **Product, Offer** | Shopping, Product | Product/shopping results |
| **Recipe** | Recipe | Recipe rich result |
| **JobPosting** | Google Jobs | Job listings |
| **Event** | Event | Event rich result |
| **WebSite + SearchAction** | Sitelinks searchbox | Site links for brand queries |
| **Organization, Person** | Knowledge Panel | Entity info; see **entity-seo** |

**Workflow**: 1) Use **serp-features** to identify target SERP feature; 2) Look up schema type in this table; 3) Implement and validate with Rich Results Test.

## Generative Engine Optimization (GEO)

**GEO** = optimizing content so AI systems (Google AI Overviews, Perplexity, ChatGPT, Gemini) choose, cite, and quote your content in generated answers. Structured data makes content machine-readable; AI engines extract and cite more accurately. Key schema types for GEO: Organization, Person/Author, WebSite, WebPage, FAQPage, HowTo, Article, Product, AggregateRating. See **generative-engine-optimization** for full GEO strategy.

## Initial Assessment

**Check for project context first:** If `.claude/project-context.md` or `.cursor/project-context.md` exists, read it for product type and content.

Identify:
1. **Page type**: Article, Product, FAQ, Organization, JobPosting, Event, etc.
2. **Content**: What entities to describe
3. **Goal**: Rich snippets, AI Overview visibility, Knowledge Panel

## Schema Type Classification

### Core Types (General Use)

| Type | Use case |
|------|----------|
| **Organization** | Site-wide; company info, logo, sameAs; see placement below |
| **WebSite** | Site-wide; search action, site name; pair with Organization on homepage |
| **Article** | Blog posts, news, tool intros |
| **BreadcrumbList** | Breadcrumb navigation |
| **FAQPage** | FAQ sections; triggers PAA-style results |
| **Person** | Author info; pairs with Article |
| **ImageObject** | Image metadata for rich results |
| **HowTo** | Tutorials, step-by-step guides. **Note**: Google may have deprecated HowTo rich results (2023–2024); Schema.org still supports it; Bing/AI may use it |

### Exclusive Types (Specific Scenarios)

| Type | Use case |
|------|----------|
| **JobPosting** | Recruitment sites, AI Job Matching |
| **Product** | E-commerce product pages |
| **Event** | Event pages, ticketing (not general blogs) |
| **SoftwareApplication** | App pages, tool pages |
| **LocalBusiness** | Local business pages |
| **Dataset** | Data platforms, datasets |
| **DiscussionForumPosting** | Forums, community posts |
| **Quiz** | Education, flashcards |
| **MathSolver** | Math tools |
| **CaseStudy** | Case study pages |
| **Recipe** | Recipes, meal plans, cooking instructions |

**Rule**: Use core types for most sites. Use exclusive types only when page content matches (e.g., don't use Event on a blog; don't use JobPosting on a product page).

### Organization & WebSite Schema Placement

| Where | Organization | WebSite | Notes |
|-------|--------------|---------|-------|
| **Homepage** | Minimum | Minimum | Add both Organization and WebSite to homepage at least. Organization describes the entity that owns the site; WebSite enables sitelinks searchbox and site identity. |
| **Root layout / global** | Optimal | Optimal | Place in site-wide layout (e.g. `layout.tsx`, `_document`, global header/footer) so schema appears on every page. Google uses the first instance found; one instance per site is sufficient. |
| **About page** | No | No | About page uses **AboutPage** schema (page-specific: headline, description, author, about). Organization is entity-level, not page-level—do not confine it to About. See **about-page-generator**. |

**Implementation**: JSON-LD in `<head>`; use `@id` (e.g. `https://example.com/#organization`) to link Organization ↔ WebSite ↔ WebPage for entity graph. See **entity-seo** for @id and Knowledge Panel.

## Action: Website/Product Type → Schema Mapping

**Use this table to recommend which exclusive schema types fit a site.** Match the site's content and product type to the most relevant schema. When in doubt, start with core types (Organization, WebSite, Article); add exclusive types only when content clearly matches.

| Website / Product type | Recommended exclusive schema | Why |
|------------------------|------------------------------|-----|
| **AI meal planner, recipe site, food blog, cooking app** | **Recipe** | Ingredients, instructions, cook time, servings—highly relevant for food/meal content. Google supports Recipe rich results. |
| **Job board, recruitment site, careers page** | **JobPosting** | Title, company, location, salary, employment type. Required for Google Jobs. |
| **Event platform, ticketing, webinar, conference** | **Event** | Date, location, price. Use only on actual event pages. |
| **SaaS, app, Chrome extension, tool, software product page** | **SoftwareApplication** | App name, category, rating, price, OS. Fits product/feature pages. |
| **E-commerce product page** | **Product** | Price, availability, brand, reviews. Use with Offer, AggregateRating. |
| **Forum, community, Reddit-style, Q&A** | **DiscussionForumPosting** | Post content, author, comments. For user-generated discussion. |
| **Data platform, dataset repository, Scale AI / Surge AI** | **Dataset** | Dataset name, creator, license, distribution format. For data catalog pages. |
| **Education site, flashcards, Quizlet-style** | **Quiz** | Question-answer pairs. For educational Q&A content. |
| **Math solver, calculator, equation tool** | **MathSolver** | Math problem input, solution output. For math tools. |
| **Restaurant, local service, store locator** | **LocalBusiness** | Address, hours, NAP. For local SEO. |
| **Case study, customer story page** | **CaseStudy** | Client, outcome, methodology. For B2B case studies. |
| **FAQ page, product FAQ, support FAQ** | **FAQPage** | Question + acceptedAnswer pairs. Triggers PAA-style results. |
| **Tutorial, how-to guide, step-by-step** | **HowTo** | Steps, tools, time. Note: Google may have deprecated rich results; Bing/AI may still use. |
| **News article, press release** | **NewsArticle** | Use instead of Article for news. |
| **Video page, podcast episode** | **VideoObject** / **PodcastEpisode** | For video/audio content. See **video-optimization** for VideoObject, thumbnail, key moments. |

**Examples:**
- **AI meal planner** (e.g., generates weekly meal plans with recipes) → Add **Recipe** schema to each recipe/meal page; **Article** or **WebPage** for landing pages
- **AI writing tool** → **SoftwareApplication** on product page; **Article** on blog
- **Recruitment SaaS** → **JobPosting** on job listing pages; **SoftwareApplication** on product page
- **Recipe blog** → **Recipe** on each recipe post; **Article** for non-recipe posts

**Output**: When recommending schema, state: (1) which exclusive types fit the site/product, (2) which page types get which schema, (3) core types to add site-wide (Organization, WebSite, BreadcrumbList).

### Article / BlogPosting / NewsArticle: Type Selection & Implementation

Choose the **most specific** type that matches content:

| Type | Use case |
|------|----------|
| **BlogPosting** | Informal blog posts; individual authors; regularly updated |
| **Article** | Formal, evergreen content; tool intros; encyclopedic |
| **NewsArticle** | Time-sensitive news; recognized publishers |

**Required properties**: headline (max 110 chars), image (min 1200px wide; absolute URL), datePublished (ISO 8601), author (Person or Organization), publisher (Organization with logo).

**Recommended**: dateModified, description, mainEntityOfPage (canonical URL).

**Date display for CTR**: Google recommends showing **only one date** on the page. If both datePublished and dateModified are visible, Google may pick the wrong date for SERP display—Search Engine Land saw ~22% CTR drop. Best practice: show dateModified if it exists, otherwise datePublished. Keep both in JSON-LD; the rule applies to **visible** date only.

**JSON-LD example** (BlogPosting):

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "The Ultimate SEO Checklist for 2025",
  "description": "A complete guide to optimizing blog posts for search and AI.",
  "image": "https://example.com/image.jpg",
  "datePublished": "2025-01-15T09:00:00Z",
  "dateModified": "2025-02-01T14:30:00Z",
  "author": { "@type": "Person", "name": "Jane Doe", "url": "https://example.com/author/jane" },
  "publisher": { "@type": "Organization", "name": "Example", "logo": { "@type": "ImageObject", "url": "https://example.com/logo.png" } }
}
```

Place in `<head>` via `<script type="application/ld+json">`. For article pages, use `og:type: article` with og:article:published_time, og:article:modified_time, og:article:author. See **article-page-generator**, **open-graph**.

### BreadcrumbList

For breadcrumb navigation. Schema must match visible breadcrumbs exactly. See **breadcrumb-generator** for UI, placement, and semantic HTML.

| Requirement | Guideline |
|-------------|-----------|
| **Format** | JSON-LD in `<script type="application/ld+json">` |
| **URLs** | Absolute URLs with https:// for each item |
| **Position** | Sequential integers starting from 1 |
| **Match** | Schema must match visible breadcrumbs exactly |

**JSON-LD example**:

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/" },
    { "@type": "ListItem", "position": 2, "name": "Category", "item": "https://example.com/category/" },
    { "@type": "ListItem", "position": 3, "name": "Current Page", "item": "https://example.com/category/current-page/" }
  ]
}
```

**Multiple paths**: Google supports multiple BreadcrumbList objects on the same page when a page is reachable via multiple paths (e.g., product in multiple categories). Use an array of BreadcrumbList objects.

## Best Practices

| Principle | Guideline |
|-----------|-----------|
| **Accuracy** | Data must match visible page content; never add invisible or misleading data |
| **Completeness** | Include all required properties per type |
| **Most specific type** | Use NewsArticle over Article when applicable |
| **JSON-LD** | Preferred format; place in `<script type="application/ld+json">` |
| **@id for entities** | Use @id for Organization, Person to enable entity linking; see **entity-seo** |
| **Phased implementation** | Add required properties first; then optional for optimization |
| **Validation** | Test with Rich Results Test and Schema Markup Validator |
| **inLanguage (multilingual)** | Add `"inLanguage": "en-US"` (IETF BCP 47) to match hreflang; localize names, descriptions, FAQs for rich snippets per locale |

### Multilingual Schema (inLanguage)

For multilingual sites, add `inLanguage` to JSON-LD to reinforce language targeting. Align with hreflang values (e.g. `"inLanguage": "zh-CN"` with `hreflang="zh-CN"`).

**Localize schema data**: Translate structured data fields (name, description, FAQ acceptedAnswer, etc.) for each locale to improve rich snippet CTR in that language.

**Types that support inLanguage**: Article, BlogPosting, WebApplication, FAQPage, HowTo, Product, Organization.

## Implementation Workflow

1. **Analyze** page type and content; choose matching Schema type
2. **Select format** — JSON-LD recommended (Google, Bing, AI tools support it)
3. **Write** structured data; start with required properties
4. **Validate** with [Rich Results Test](https://search.google.com/test/rich-results), [Schema Markup Validator](https://validator.schema.org/)
5. **Deploy and monitor** via Search Console enhanced reports

## Common Errors and Fixes

| Error | Fix |
|-------|-----|
| **Data doesn't match visible content** | Schema must describe only what users see |
| **Missing required properties** | Check Google/Schema.org docs for each type |
| **Wrong type for page** | Don't use Event on non-event pages; don't use JobPosting on product pages |
| **Format/syntax errors** | Validate JSON-LD; check quotes, brackets, commas |
| **Over-markup** | Mark only relevant content; avoid stuffing unrelated types |

## Implementation

### Next.js (metadata)

```tsx
export const metadata = {
  other: {
    'script:ld+json': JSON.stringify({
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "...",
      "description": "...",
      "inLanguage": "en-US",
      "image": "https://example.com/image.jpg",
      "datePublished": "2024-01-01T00:00:00Z",
      "dateModified": "2024-01-15T00:00:00Z",
      "author": { "@type": "Person", "name": "..." },
      "publisher": { "@type": "Organization", "name": "...", "logo": { "@type": "ImageObject", "url": "..." } }
    }),
  },
};
```

### HTML (generic)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "...",
  "description": "...",
  "inLanguage": "en-US",
  "author": { "@type": "Person", "name": "..." },
  "publisher": { "@type": "Organization", "name": "...", "logo": { "@type": "ImageObject", "url": "..." } }
}
</script>
```

## Validation Tools

| Tool | Purpose |
|------|---------|
| [Google Rich Results Test](https://search.google.com/test/rich-results) | Check if Google can generate rich results |
| [Schema Markup Validator](https://validator.schema.org/) | Validate against Schema.org spec |
| Search Console | Enhanced reports; monitor validity over time |

## Output Format

- **Action first**: Use the Website/Product Type → Schema Mapping table to recommend which exclusive schema fits the site (e.g., AI meal planner → Recipe; SaaS tool → SoftwareApplication)
- **Schema type** recommendation (core vs. exclusive)
- **Page-level mapping**: Which pages get which schema
- **JSON-LD** structure with required properties
- **Validation** steps
- **References**: [Schema.org](https://schema.org/), [Google Structured Data](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data), [Bing Markup](https://www.bing.com/webmasters/help/marking-up-your-site-with-structured-data-3a93e731)

## Related Skills

- **article-page-generator**: Article structure; Article/BlogPosting/NewsArticle schema; date display
- **serp-features**: **Strongly related**—schema maps to SERP features; see mapping table above
- **faq-page-generator**: FAQPage schema; FAQ content structure
- **breadcrumb-generator**: BreadcrumbList schema implementation
- **featured-snippet**: FAQPage, HowTo for snippets
- **video-optimization**: VideoObject, video sitemap, thumbnail, key moments
- **entity-seo**: Organization, Person for entity recognition; @id; Knowledge Panel
- **homepage-generator**: Organization + WebSite schema on homepage or root layout
- **indexing**: Google Indexing API for JobPosting, BroadcastEvent
