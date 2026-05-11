---
name: technical-seo-checker
description: 'Use when the user asks to "technical SEO audit", "check page speed", "crawl issues", "Core Web Vitals", "site indexing problems", "my site is slow", "Google cannot crawl my site", "mobile issues", or "indexing problems". Performs technical SEO audits covering site speed, crawlability, indexability, mobile-friendliness, security, and structured data. Identifies technical issues preventing optimal search performance. For content and heading element issues, see on-page-seo-auditor. For link architecture, see internal-linking-optimizer.'
license: Apache-2.0
metadata:
  author: aaron-he-zhu
  version: "2.0.0"
  geo-relevance: "low"
  tags:
    - seo
    - technical seo
    - page speed
    - core web vitals
    - crawlability
    - indexability
    - mobile-friendly
    - site speed
    - security audit
  triggers:
    - "technical SEO audit"
    - "check page speed"
    - "crawl issues"
    - "Core Web Vitals"
    - "site indexing problems"
    - "mobile-friendly check"
    - "site speed"
    - "my site is slow"
    - "Google can't crawl my site"
    - "mobile issues"
    - "indexing problems"
---

# Technical SEO Checker


> **[SEO & GEO Skills Library](https://skills.sh/aaron-he-zhu/seo-geo-claude-skills)** · 20 skills for SEO + GEO · Install all: `npx skills add aaron-he-zhu/seo-geo-claude-skills`

<details>
<summary>Browse all 20 skills</summary>

**Research** · [keyword-research](../../research/keyword-research/) · [competitor-analysis](../../research/competitor-analysis/) · [serp-analysis](../../research/serp-analysis/) · [content-gap-analysis](../../research/content-gap-analysis/)

**Build** · [seo-content-writer](../../build/seo-content-writer/) · [geo-content-optimizer](../../build/geo-content-optimizer/) · [meta-tags-optimizer](../../build/meta-tags-optimizer/) · [schema-markup-generator](../../build/schema-markup-generator/)

**Optimize** · [on-page-seo-auditor](../on-page-seo-auditor/) · **technical-seo-checker** · [internal-linking-optimizer](../internal-linking-optimizer/) · [content-refresher](../content-refresher/)

**Monitor** · [rank-tracker](../../monitor/rank-tracker/) · [backlink-analyzer](../../monitor/backlink-analyzer/) · [performance-reporter](../../monitor/performance-reporter/) · [alert-manager](../../monitor/alert-manager/)

**Cross-cutting** · [content-quality-auditor](../../cross-cutting/content-quality-auditor/) · [domain-authority-auditor](../../cross-cutting/domain-authority-auditor/) · [entity-optimizer](../../cross-cutting/entity-optimizer/) · [memory-management](../../cross-cutting/memory-management/)

</details>

This skill performs comprehensive technical SEO audits to identify issues that may prevent search engines from properly crawling, indexing, and ranking your site.

## When to Use This Skill

- Launching a new website
- Diagnosing ranking drops
- Pre-migration SEO audits
- Regular technical health checks
- Identifying crawl and index issues
- Improving site performance
- Fixing Core Web Vitals issues

## What This Skill Does

1. **Crawlability Audit**: Checks robots.txt, sitemaps, crawl issues
2. **Indexability Review**: Analyzes index status and blockers
3. **Site Speed Analysis**: Evaluates Core Web Vitals and performance
4. **Mobile-Friendliness**: Checks mobile optimization
5. **Security Check**: Reviews HTTPS and security headers
6. **Structured Data Audit**: Validates schema markup
7. **URL Structure Analysis**: Reviews URL patterns and redirects
8. **International SEO**: Checks hreflang and localization

## How to Use

### Full Technical Audit

```
Perform a technical SEO audit for [URL/domain]
```

### Specific Issue Check

```
Check Core Web Vitals for [URL]
```

```
Audit crawlability and indexability for [domain]
```

### Pre-Migration Audit

```
Technical SEO checklist for migrating [old domain] to [new domain]
```

## Data Sources

> See [CONNECTORS.md](../../CONNECTORS.md) for tool category placeholders.

**With ~~web crawler + ~~page speed tool + ~~CDN connected:**
Claude can automatically crawl the entire site structure via ~~web crawler, pull Core Web Vitals and performance metrics from ~~page speed tool, analyze caching headers from ~~CDN, and fetch mobile-friendliness data. This enables comprehensive automated technical audits.

**With manual data only:**
Ask the user to provide:
1. Site URL(s) to audit
2. PageSpeed Insights screenshots or reports
3. robots.txt file content
4. sitemap.xml URL or file

Proceed with the full audit using provided data. Note in the output which findings are from automated crawl vs. manual review.

## Instructions

When a user requests a technical SEO audit:

1. **Audit Crawlability**

   ```markdown
   ## Crawlability Analysis
   
   ### Robots.txt Review
   
   **URL**: [domain]/robots.txt
   **Status**: [Found/Not Found/Error]
   
   **Current Content**:
   ```
   [robots.txt content]
   ```
   
   | Check | Status | Notes |
   |-------|--------|-------|
   | File exists | ✅/❌ | [notes] |
   | Valid syntax | ✅/⚠️/❌ | [errors found] |
   | Sitemap declared | ✅/❌ | [sitemap URL] |
   | Important pages blocked | ✅/⚠️/❌ | [blocked paths] |
   | Assets blocked | ✅/⚠️/❌ | [CSS/JS blocked?] |
   | Correct user-agents | ✅/⚠️/❌ | [notes] |
   
   **Issues Found**:
   - [Issue 1]
   - [Issue 2]
   
   **Recommended robots.txt**:
   ```
   User-agent: *
   Allow: /
   Disallow: /admin/
   Disallow: /private/
   
   Sitemap: https://example.com/sitemap.xml
   ```
   
   ---
   
   ### XML Sitemap Review
   
   **Sitemap URL**: [URL]
   **Status**: [Found/Not Found/Error]
   
   | Check | Status | Notes |
   |-------|--------|-------|
   | Sitemap exists | ✅/❌ | [notes] |
   | Valid XML format | ✅/⚠️/❌ | [errors] |
   | In robots.txt | ✅/❌ | [notes] |
   | Submitted to ~~search console | ✅/⚠️/❌ | [notes] |
   | URLs count | [X] | [appropriate?] |
   | Only indexable URLs | ✅/⚠️/❌ | [notes] |
   | Includes priority | ✅/⚠️ | [notes] |
   | Includes lastmod | ✅/⚠️ | [accurate?] |
   
   **Issues Found**:
   - [Issue 1]
   
   ---
   
   ### Crawl Budget Analysis
   
   | Factor | Status | Impact |
   |--------|--------|--------|
   | Crawl errors | [X] errors | [Low/Med/High] |
   | Duplicate content | [X] pages | [Low/Med/High] |
   | Thin content | [X] pages | [Low/Med/High] |
   | Redirect chains | [X] found | [Low/Med/High] |
   | Orphan pages | [X] found | [Low/Med/High] |
   
   **Crawlability Score**: [X]/10
   ```

2. **Audit Indexability**

   ```markdown
   ## Indexability Analysis
   
   ### Index Status Overview
   
   | Metric | Count | Notes |
   |--------|-------|-------|
   | Pages in sitemap | [X] | |
   | Pages indexed | [X] | [source: site: search] |
   | Index coverage ratio | [X]% | [good if >90%] |
   
   ### Index Blockers Check
   
   | Blocker Type | Found | Pages Affected |
   |--------------|-------|----------------|
   | noindex meta tag | [X] | [list or "none"] |
   | noindex X-Robots | [X] | [list or "none"] |
   | Robots.txt blocked | [X] | [list or "none"] |
   | Canonical to other | [X] | [list or "none"] |
   | 4xx/5xx errors | [X] | [list or "none"] |
   | Redirect loops | [X] | [list or "none"] |
   
   ### Canonical Tags Audit
   
   | Check | Status | Notes |
   |-------|--------|-------|
   | Canonicals present | ✅/⚠️/❌ | [X]% of pages |
   | Self-referencing | ✅/⚠️/❌ | [notes] |
   | Consistent (HTTP/HTTPS) | ✅/⚠️/❌ | [notes] |
   | Consistent (www/non-www) | ✅/⚠️/❌ | [notes] |
   | No conflicting signals | ✅/⚠️/❌ | [notes] |
   
   ### Duplicate Content Issues
   
   | Issue Type | Count | Examples |
   |------------|-------|----------|
   | Exact duplicates | [X] | [URLs] |
   | Near duplicates | [X] | [URLs] |
   | Parameter duplicates | [X] | [URLs] |
   | WWW/non-WWW | [X] | [notes] |
   | HTTP/HTTPS | [X] | [notes] |
   
   **Indexability Score**: [X]/10
   ```

3. **Audit Site Speed & Core Web Vitals**

   ```markdown
   ## Performance Analysis
   
   ### Core Web Vitals
   
   | Metric | Mobile | Desktop | Target | Status |
   |--------|--------|---------|--------|--------|
   | LCP (Largest Contentful Paint) | [X]s | [X]s | <2.5s | ✅/⚠️/❌ |
   | FID (First Input Delay) | [X]ms | [X]ms | <100ms | ✅/⚠️/❌ |
   | CLS (Cumulative Layout Shift) | [X] | [X] | <0.1 | ✅/⚠️/❌ |
   | INP (Interaction to Next Paint) | [X]ms | [X]ms | <200ms | ✅/⚠️/❌ |
   
   ### Additional Performance Metrics
   
   | Metric | Value | Status |
   |--------|-------|--------|
   | Time to First Byte (TTFB) | [X]ms | ✅/⚠️/❌ |
   | First Contentful Paint (FCP) | [X]s | ✅/⚠️/❌ |
   | Speed Index | [X] | ✅/⚠️/❌ |
   | Total Blocking Time | [X]ms | ✅/⚠️/❌ |
   | Page Size | [X]MB | ✅/⚠️/❌ |
   | Requests | [X] | ✅/⚠️/❌ |
   
   ### Performance Issues
   
   **LCP Issues**:
   - [Issue]: [Impact] - [Solution]
   - [Issue]: [Impact] - [Solution]
   
   **CLS Issues**:
   - [Issue]: [Impact] - [Solution]
   
   **Resource Loading**:
   | Resource Type | Count | Size | Issues |
   |---------------|-------|------|--------|
   | Images | [X] | [X]MB | [notes] |
   | JavaScript | [X] | [X]MB | [notes] |
   | CSS | [X] | [X]KB | [notes] |
   | Fonts | [X] | [X]KB | [notes] |
   
   ### Optimization Recommendations
   
   **High Impact**:
   1. [Recommendation] - Est. improvement: [X]s
   2. [Recommendation] - Est. improvement: [X]s
   
   **Medium Impact**:
   1. [Recommendation]
   2. [Recommendation]
   
   **Performance Score**: [X]/10
   ```

4. **Audit Mobile-Friendliness**

   ```markdown
   ## Mobile Optimization Analysis
   
   ### Mobile-Friendly Test
   
   | Check | Status | Notes |
   |-------|--------|-------|
   | Mobile-friendly overall | ✅/❌ | [notes] |
   | Viewport configured | ✅/❌ | [viewport tag] |
   | Text readable | ✅/⚠️/❌ | Font size: [X]px |
   | Tap targets sized | ✅/⚠️/❌ | [notes] |
   | Content fits viewport | ✅/❌ | [notes] |
   | No horizontal scroll | ✅/❌ | [notes] |
   
   ### Responsive Design Check
   
   | Element | Desktop | Mobile | Issues |
   |---------|---------|--------|--------|
   | Navigation | [status] | [status] | [notes] |
   | Images | [status] | [status] | [notes] |
   | Forms | [status] | [status] | [notes] |
   | Tables | [status] | [status] | [notes] |
   | Videos | [status] | [status] | [notes] |
   
   ### Mobile-First Indexing
   
   | Check | Status | Notes |
   |-------|--------|-------|
   | Mobile version has all content | ✅/⚠️/❌ | [notes] |
   | Mobile has same structured data | ✅/⚠️/❌ | [notes] |
   | Mobile has same meta tags | ✅/⚠️/❌ | [notes] |
   | Mobile images have alt text | ✅/⚠️/❌ | [notes] |
   
   **Mobile Score**: [X]/10
   ```

5. **Audit Security & HTTPS**

   ```markdown
   ## Security Analysis
   
   ### HTTPS Status
   
   | Check | Status | Notes |
   |-------|--------|-------|
   | SSL certificate valid | ✅/❌ | Expires: [date] |
   | HTTPS enforced | ✅/❌ | [redirects properly?] |
   | Mixed content | ✅/⚠️/❌ | [X] issues |
   | HSTS enabled | ✅/⚠️ | [notes] |
   | Certificate chain | ✅/⚠️/❌ | [notes] |
   
   ### Security Headers
   
   | Header | Present | Value | Recommended |
   |--------|---------|-------|-------------|
   | Content-Security-Policy | ✅/❌ | [value] | [recommendation] |
   | X-Frame-Options | ✅/❌ | [value] | DENY or SAMEORIGIN |
   | X-Content-Type-Options | ✅/❌ | [value] | nosniff |
   | X-XSS-Protection | ✅/❌ | [value] | 1; mode=block |
   | Referrer-Policy | ✅/❌ | [value] | [recommendation] |
   
   **Security Score**: [X]/10
   ```

6. **Audit URL Structure**

   ```markdown
   ## URL Structure Analysis
   
   ### URL Pattern Review
   
   | Check | Status | Notes |
   |-------|--------|-------|
   | HTTPS URLs | ✅/⚠️/❌ | [X]% HTTPS |
   | Lowercase URLs | ✅/⚠️/❌ | [notes] |
   | No special characters | ✅/⚠️/❌ | [notes] |
   | Readable/descriptive | ✅/⚠️/❌ | [notes] |
   | Appropriate length | ✅/⚠️/❌ | Avg: [X] chars |
   | Keywords in URLs | ✅/⚠️/❌ | [notes] |
   | Consistent structure | ✅/⚠️/❌ | [notes] |
   
   ### URL Issues Found
   
   | Issue Type | Count | Examples |
   |------------|-------|----------|
   | Dynamic parameters | [X] | [URLs] |
   | Session IDs in URLs | [X] | [URLs] |
   | Uppercase characters | [X] | [URLs] |
   | Special characters | [X] | [URLs] |
   | Very long URLs (>100) | [X] | [URLs] |
   
   ### Redirect Analysis
   
   | Check | Status | Notes |
   |-------|--------|-------|
   | Redirect chains | [X] found | [max chain length] |
   | Redirect loops | [X] found | [URLs] |
   | 302 → 301 needed | [X] found | [URLs] |
   | Broken redirects | [X] found | [URLs] |
   
   **URL Score**: [X]/10
   ```

7. **Audit Structured Data**

   > **CORE-EEAT alignment**: Schema markup quality maps to O05 (Schema Markup) in the CORE-EEAT benchmark. See [content-quality-auditor](../../cross-cutting/content-quality-auditor/) for full content quality audit.

   ```markdown
   ## Structured Data Analysis
   
   ### Schema Markup Found
   
   | Schema Type | Pages | Valid | Errors |
   |-------------|-------|-------|--------|
   | [Type 1] | [X] | ✅/❌ | [errors] |
   | [Type 2] | [X] | ✅/❌ | [errors] |
   
   ### Validation Results
   
   **Errors**:
   - [Error 1]: [affected pages] - [solution]
   - [Error 2]: [affected pages] - [solution]
   
   **Warnings**:
   - [Warning 1]: [notes]
   
   ### Missing Schema Opportunities
   
   | Page Type | Current Schema | Recommended |
   |-----------|----------------|-------------|
   | Blog posts | [current] | Article + FAQ |
   | Products | [current] | Product + Review |
   | Homepage | [current] | Organization |
   
   **Structured Data Score**: [X]/10
   ```

8. **Audit International SEO (if applicable)**

   ```markdown
   ## International SEO Analysis
   
   ### Hreflang Implementation
   
   | Check | Status | Notes |
   |-------|--------|-------|
   | Hreflang tags present | ✅/❌ | [notes] |
   | Self-referencing | ✅/⚠️/❌ | [notes] |
   | Return tags present | ✅/⚠️/❌ | [notes] |
   | Valid language codes | ✅/⚠️/❌ | [notes] |
   | x-default tag | ✅/⚠️ | [notes] |
   
   ### Language/Region Targeting
   
   | Language | URL | Hreflang | Status |
   |----------|-----|----------|--------|
   | [en-US] | [URL] | [tag] | ✅/⚠️/❌ |
   | [es-ES] | [URL] | [tag] | ✅/⚠️/❌ |
   
   **International Score**: [X]/10
   ```

9. **Generate Technical Audit Summary**

   ```markdown
   # Technical SEO Audit Report
   
   **Domain**: [domain]
   **Audit Date**: [date]
   **Pages Analyzed**: [X]
   
   ## Overall Technical Health: [X]/100
   
   ```
   Score Breakdown:
   ████████░░ Crawlability: 8/10
   ███████░░░ Indexability: 7/10
   █████░░░░░ Performance: 5/10
   ████████░░ Mobile: 8/10
   █████████░ Security: 9/10
   ██████░░░░ URL Structure: 6/10
   █████░░░░░ Structured Data: 5/10
   ```
   
   ## Critical Issues (Fix Immediately)
   
   1. **[Issue]**: [Impact] 
      - Affected: [pages/scope]
      - Solution: [specific fix]
      - Priority: 🔴 Critical
   
   2. **[Issue]**: [Impact]
      - Affected: [pages/scope]
      - Solution: [specific fix]
      - Priority: 🔴 Critical
   
   ## High Priority Issues
   
   1. **[Issue]**: [Solution]
   2. **[Issue]**: [Solution]
   
   ## Medium Priority Issues
   
   1. **[Issue]**: [Solution]
   2. **[Issue]**: [Solution]
   
   ## Quick Wins
   
   These can be fixed quickly for immediate improvement:
   
   1. [Quick fix 1]
   2. [Quick fix 2]
   3. [Quick fix 3]
   
   ## Implementation Roadmap
   
   ### Week 1: Critical Fixes
   - [ ] [Task 1]
   - [ ] [Task 2]
   
   ### Week 2-3: High Priority
   - [ ] [Task 1]
   - [ ] [Task 2]
   
   ### Week 4+: Optimization
   - [ ] [Task 1]
   - [ ] [Task 2]
   
   ## Monitoring Recommendations

   Set up alerts for:
   - Core Web Vitals drops
   - Crawl error spikes
   - Index coverage changes
   - Security issues
   ```

## Validation Checkpoints

### Input Validation
- [ ] Site URL or domain clearly specified
- [ ] Access to technical data (robots.txt, sitemap, or crawl results)
- [ ] Performance metrics available (via ~~page speed tool or screenshots)

### Output Validation
- [ ] Every recommendation cites specific data points (not generic advice)
- [ ] All issues include affected URLs or page counts
- [ ] Performance metrics include actual numbers with units (seconds, KB, etc.)
- [ ] Source of each data point clearly stated (~~web crawler data, ~~page speed tool, user-provided, or estimated)

## Example

**User**: "Check the technical SEO of cloudhosting.com"

**Output**:

```markdown
# Technical SEO Audit Report

**Domain**: cloudhosting.com
**Audit Date**: 2024-09-15
**Pages Analyzed**: 312

## Crawlability Analysis

### Robots.txt Review

**URL**: cloudhosting.com/robots.txt
**Status**: Found

| Check | Status | Notes |
|-------|--------|-------|
| File exists | ✅ | 200 response |
| Valid syntax | ⚠️ | Wildcard pattern `Disallow: /*?` too aggressive — blocks faceted pages |
| Sitemap declared | ❌ | No Sitemap directive in robots.txt |
| Important pages blocked | ⚠️ | /pricing/ blocked by `Disallow: /pricing` rule |
| Assets blocked | ✅ | CSS/JS accessible |

**Issues Found**:
- Sitemap URL not declared in robots.txt
- `/pricing/` inadvertently blocked — high-value commercial page

### XML Sitemap Review

**Sitemap URL**: cloudhosting.com/sitemap.xml
**Status**: Found (not referenced in robots.txt)

| Check | Status | Notes |
|-------|--------|-------|
| Sitemap exists | ✅ | Valid XML, 287 URLs |
| Only indexable URLs | ❌ | 23 noindex URLs included |
| Includes lastmod | ⚠️ | All dates set to 2023-01-01 — not accurate |

**Crawlability Score**: 5/10

## Performance Analysis

### Core Web Vitals

| Metric | Mobile | Desktop | Target | Status |
|--------|--------|---------|--------|--------|
| LCP (Largest Contentful Paint) | 4.8s | 2.1s | <2.5s | ❌ Mobile / ✅ Desktop |
| FID (First Input Delay) | 45ms | 12ms | <100ms | ✅ / ✅ |
| CLS (Cumulative Layout Shift) | 0.24 | 0.08 | <0.1 | ❌ Mobile / ✅ Desktop |
| INP (Interaction to Next Paint) | 380ms | 140ms | <200ms | ❌ Mobile / ✅ Desktop |

### Additional Performance Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Time to First Byte (TTFB) | 1,240ms | ❌ |
| Page Size | 3.8MB | ❌ |
| Requests | 94 | ⚠️ |

**LCP Issues**:
- Uncompressed hero image (2.4MB PNG): Convert to WebP, est. save 1.9MB
- No CDN detected: TTFB 1,240ms from origin server

**CLS Issues**:
- Ad banner at top of page injects without reserved height (0.18 shift contribution)

**Performance Score**: 3/10

## Security Analysis

### HTTPS Status

| Check | Status | Notes |
|-------|--------|-------|
| SSL certificate valid | ✅ | Expires: 2025-03-22 |
| HTTPS enforced | ⚠️ | http://cloudhosting.com returns 200 instead of 301 redirect |
| Mixed content | ❌ | 7 images loaded over HTTP on /features/ page |
| HSTS enabled | ❌ | Header not present |

**Security Score**: 5/10

## Structured Data Analysis

### Schema Markup Found

| Schema Type | Pages | Valid | Errors |
|-------------|-------|-------|--------|
| Organization | 1 (homepage) | ✅ | None |
| Article | 0 | — | Missing on 48 blog posts |
| Product | 0 | — | Missing on 5 plan pages |
| FAQ | 0 | — | Missing on 12 pages with FAQ content |

**Structured Data Score**: 3/10

## Overall Technical Health: 42/100

```
Score Breakdown:
█████░░░░░ Crawlability: 5/10
██████░░░░ Indexability: 6/10
███░░░░░░░ Performance: 3/10
██████░░░░ Mobile: 6/10
█████░░░░░ Security: 5/10
██████░░░░ URL Structure: 6/10
███░░░░░░░ Structured Data: 3/10
```

## Priority Issues

### 🔴 Critical (Fix Immediately)
1. **Mobile LCP 4.8s (target <2.5s)** — Compress hero image to WebP (est. save 1.9MB) and implement a CDN to reduce TTFB from 1,240ms to <400ms.

### 🟡 Important (Fix Soon)
2. **HTTP not redirecting to HTTPS** — Add 301 redirect from http:// to https:// and enable HSTS header. 7 mixed-content images on /features/ need URL updates.

### 🟢 Minor (Optimize)
3. **No Article/FAQ schema on blog posts** — Add Article schema to 48 blog posts and FAQ schema to 12 FAQ pages for rich result eligibility.
```

## Technical SEO Checklist

```markdown
### Crawlability
- [ ] robots.txt is valid and not blocking important content
- [ ] XML sitemap exists and is submitted to ~~search console
- [ ] No crawl errors in ~~search console
- [ ] No redirect chains or loops

### Indexability  
- [ ] Important pages are indexable
- [ ] Canonical tags are correct
- [ ] No duplicate content issues
- [ ] Pagination is handled correctly

### Performance
- [ ] Core Web Vitals pass
- [ ] Page speed under 3 seconds
- [ ] Images are optimized
- [ ] JS/CSS are minified

### Mobile
- [ ] Mobile-friendly test passes
- [ ] Viewport is configured
- [ ] Touch elements are properly sized

### Security
- [ ] HTTPS is enforced
- [ ] SSL certificate is valid
- [ ] No mixed content
- [ ] Security headers present

### Structure
- [ ] URLs are clean and descriptive
- [ ] Site architecture is logical
- [ ] Internal linking is strong
```

## Tips for Success

1. **Prioritize by impact** - Fix critical issues first
2. **Monitor continuously** - Use ~~search console alerts
3. **Test changes** - Verify fixes work before deploying widely
4. **Document everything** - Track changes for troubleshooting
5. **Regular audits** - Schedule quarterly technical reviews

## Technical SEO Severity Framework

### Issue Classification

| Severity | Impact Description | Examples | Response Time |
|----------|-------------------|---------|---------------|
| **Critical** | Prevents indexation or causes site-wide issues | Robots.txt blocking site, noindex on key pages, site-wide 500 errors | Same day |
| **High** | Significantly impacts rankings or user experience | Slow page speed, missing hreflang, duplicate content, redirect chains | Within 1 week |
| **Medium** | Affects specific pages or has moderate impact | Missing schema, suboptimal canonicals, thin content pages | Within 1 month |
| **Low** | Minor optimization opportunities | Image compression, minor CLS issues, non-essential schema missing | Next quarter |

### Technical Debt Prioritization Matrix

| Factor | Weight | Assessment |
|--------|--------|-----------|
| Pages affected | 30% | Site-wide > Section > Single page |
| Revenue impact | 25% | Revenue pages > Blog > Utility pages |
| Fix difficulty | 20% | Config change < Template change < Code rewrite |
| Competitive impact | 15% | Competitors passing you > parity > you ahead |
| Crawl budget waste | 10% | High waste > Moderate > Minimal |

## Core Web Vitals Optimization Quick Reference

### LCP (Largest Contentful Paint) Optimization

| Root Cause | Detection | Fix |
|-----------|-----------|-----|
| Large hero image | PageSpeed Insights | Serve WebP, resize to container, add loading="lazy" |
| Render-blocking CSS/JS | DevTools Coverage | Defer non-critical, inline critical CSS |
| Slow server response | TTFB >800ms | CDN, server-side caching, upgrade hosting |
| Third-party scripts | DevTools Network | Defer/async, use facade pattern |

### CLS (Cumulative Layout Shift) Optimization

| Root Cause | Detection | Fix |
|-----------|-----------|-----|
| Images without dimensions | DevTools | Add explicit width/height attributes |
| Ads/embeds without reserved space | Visual inspection | Set min-height on containers |
| Web fonts causing FOUT | DevTools | font-display: swap + preload fonts |
| Dynamic content injection | Visual inspection | Reserve space with CSS |

### INP (Interaction to Next Paint) Optimization

| Root Cause | Detection | Fix |
|-----------|-----------|-----|
| Long JavaScript tasks | DevTools Performance | Break into smaller tasks, use requestIdleCallback |
| Heavy event handlers | DevTools | Debounce/throttle, use passive listeners |
| Main thread blocking | DevTools | Web workers for heavy computation |

## Reference Materials

- [robots.txt Reference](./references/robots-txt-reference.md) - Syntax guide, templates, common configurations
- [HTTP Status Codes](./references/http-status-codes.md) - SEO impact of each status code, redirect best practices

## Related Skills

- [on-page-seo-auditor](../on-page-seo-auditor/) — On-page SEO audit
- [schema-markup-generator](../../build/schema-markup-generator/) — Fix schema issues
- [performance-reporter](../../monitor/performance-reporter/) — Monitor improvements
- [internal-linking-optimizer](../internal-linking-optimizer/) — Fix link issues
- [alert-manager](../../monitor/alert-manager/) — Set up alerts for technical issues found
- [content-quality-auditor](../../cross-cutting/content-quality-auditor/) — Full 80-item CORE-EEAT audit

