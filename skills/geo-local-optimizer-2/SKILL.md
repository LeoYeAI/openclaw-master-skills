---
name: geo-local-optimizer
description: >
  Local business-focused GEO optimization orchestrator for AI-powered local search. Use this skill
  whenever the user mentions local shops, clinics, restaurants, service providers, offline stores,
  franchise locations, or service areas and wants to rank better in AI answers or map-style results
  for queries like "near me", city/area + service, or landmark-based searches. Always consider this
  skill when the request combines GEO, local SEO, maps/listings, store pages, reviews, or service
  areas, even if the user does not explicitly say "GEO" or "local SEO".
---

# GEO Local Optimizer

A workflow skill for **local-business GEO optimization**, focusing specifically on **AI-powered local
search** scenarios.

The goal is to take the user from “I have / plan a local business presence” to a **structured local GEO
plan** that:

- Makes each location and service area **easy for AI models to understand and safely cite**
- Aligns **web pages + map/listing profiles + reviews + Q&A + local content** into one coherent entity
- Works for both **classical search + map packs** and **ChatGPT / Perplexity / Gemini / Claude** style
  local answers

This skill focuses on **strategy, structure, and workflows**. It should **coordinate** with other GEO
skills rather than replace them.

---

## When to use this skill

Invoke this skill **whenever**:

- The user runs or supports a **local business**, for example:
  - Food & beverage: cafes, restaurants, bakeries, bubble tea shops, snack bars
  - Everyday services: gyms, salons, laundries, pet stores, repair shops, home services
  - Medical & professional services: clinics, dentists, counseling centers, law firms, training centers
  - Retail stores: convenience stores, boutiques, electronics stores, bookstores
- The user’s goal explicitly or implicitly involves **local discovery**, such as:
  - “near me” style queries
  - city / district / neighborhood + service (e.g. "Downtown Toronto dentist", "Brooklyn personal trainer")
  - landmark-based searches (e.g. "coffee near Shibuya station", "gym near Central Park")
- The conversation touches on:
  - **store / location pages**, store detail pages, store finders, location landing pages
  - **map / listing / review / food delivery / local directory** presence
  - **local reviews, Q&A, UGC, and reputation**
  - how to make **AI answers for local queries more likely to mention this business**

Do **not** limit triggering only to explicit “local SEO” wording. If the user:

- Describes one or more locations with clear geography, **and**
- Wants local customers to find them more easily in search or AI answers,

then this skill should be strongly considered.

---

## Relationship to other GEO skills

When available, this skill should **coordinate** with:

- `geo-site-audit`: for overall technical + content GEO readiness of the website
- `geo-studio`: for higher-level GEO strategy and prioritization across regions or markets
- `geo-schema-gen`: to generate local-business-oriented schemas
- `geo-llms-txt`: to expose local pages and location hubs to AI crawlers
- `geo-multimodal-tagger`: to optimize store photos, menu images, environment shots, etc.
- `high-repeat-small-goods-ops`: for fast-moving local retail or F&B with high repeat purchase
- `high-ticket-trust-conversion`: for high-ticket, trust-sensitive local services (medical, education,
  home renovation, etc.)

If some skills are not present, still follow the same **workflow shape** and clearly explain what would
be done, providing concrete, copy-pastable outputs.

---

## Local AI search mindset

Before starting the workflow, briefly reason about the **local AI search context**:

- Typical queries combine **intent + geography + constraints**, for example:
  - “brunch cafe near [landmark], kid-friendly, outdoor seating if possible”
  - “[city/area] dentist that opens late after work”
- AI answers need:
  - Clear **entity definitions** (business type, brand, locations)
  - Stable **name / address / phone / hours / service area / price level / who it is for**
  - Rich but structured **factual descriptions** and **typical scenarios**
- Map / listing systems care about:
  - NAP consistency (Name, Address, Phone)
  - Categories, tags, photos, review volume and freshness
  - Citations and mentions across the web

Keep in mind: the goal is to **make it easy and safe for models to “recommend” this place to others**, not
just to stuff keywords.

---

## High-level workflow

When this skill is used, follow this **8-step workflow** unless the user explicitly asks for only a
subset.

### 1. Capture business and locality context

Clarify the minimal but sufficient context for local optimization:

- **Business basics**:
  - Category / industry (e.g. "specialty coffee shop", "community grocery", "dental clinic",
    "personal training studio")
  - Single location vs. multi-location / franchise
- **Geography and service area**:
  - Full address for each location (city / district / neighborhood / street / building, plus landmarks)
  - Service area: walkable radius, drive-time radius, or named areas / zip codes
  - Whether on-site, on-premise, or remote / at-home services are offered
- **Target customers and languages**:
  - Core audiences (commuters, families with kids, students, seniors, expats, etc.)
  - Languages supported (e.g. local language + English)
- **Key offers & positioning**:
  - Core services / hero products / packages
  - Price band (budget / mid-range / premium)
  - Differentiators (ambience, expertise, speed, convenience, family-friendliness, etc.)
- **Existing digital assets**:
  - Website, landing pages, store finder, mini-apps, social channels, PDFs / decks
  - Existing map / review / delivery / directory listings (Google Maps, Apple Maps, Yelp,
    Tripadvisor, local review apps, food delivery platforms, etc.)

Output a `## Local Business Brief` section with 6–10 bullet points summarizing this.

### 2. Audit current local presence

Based on the information and URLs provided by the user:

- Check **NAP consistency**:
  - Brand / store naming conventions
  - Address, phone, website, hours across platforms
- Map / listing profiles:
  - Whether major platforms have claimed / verified listings
  - Accuracy of categories and attributes
  - Photo quality (storefront, interior, key products / services, atmosphere)
  - Presence of a concise, informative business description and highlights
- Website & store pages:
  - Whether each location has its **own landing page** (or a location finder + subpages)
  - Whether pages clearly display: name, address, phone, hours, service area, price level,
    directions / transport hints
  - Presence of local FAQs and scenario-based descriptions
- Reviews & Q&A:
  - Review volume, average ratings, recency
  - Common themes in questions (parking, wait times, booking, kid-friendly, etc.)

Output a `## Local Presence Snapshot` with:

- 1–2 short paragraphs on overall status
- A markdown table summarizing key surfaces, for example:

```markdown
| Surface / Platform | Status (Good/OK/Poor/Missing) | Key issues / notes                  |
|--------------------|-------------------------------|-------------------------------------|
| Website store page | OK                            | Has address but lacks detailed FAQ  |
| Google / Apple map | Good                          | Photos ok, but no English summary   |
| Local review app   | Poor                          | Few reviews, category mis-specified |
```

### 3. Design local entity and page strategy

Turn the brief + audit into a **concrete entity & page plan**:

- Decide what counts as a distinct **local entity**:
  - Single-store: each location is a separate local entity
  - Multi-location + service areas: locations plus city / area-level service pages
  - Person + organization: key practitioners or founders linked to the business
- Plan the **core local GEO pages**:
  - Brand / site-level hub pages (as canonical anchors and store finders)
  - Location pages (one landing page per store / location)
  - Service-area pages (e.g. "Downtown home appliance repair", "Midtown personal training")
  - Local FAQ / resource pages (e.g. "Family-friendly weekend guide for [area]" featuring the business)
- For each planned page, define:
  - **Primary intent** (what query / question it should answer)
  - **Target geography** (city / district / neighborhood / service area)
  - **Primary entity type** (LocalBusiness subtype / Organization / Person / Service)
  - **Canonical URL suggestion** (e.g. `/stores/downtown-cafe` or `/city/area/service`)

Output a `## Local Entity & Page Plan` section with:

- A table for core pages
- Brief bullets explaining how this plan helps AI answer local, scenario-based queries with this business.

### 4. Craft AI-local landing structures

For each key local page type, propose a **reusable structure**.

For **single store / location pages**, suggest a template like:

```markdown
# [Brand / Location Name] – [City / Area] [Clear category keyword]
## Summary
- 2–4 bullets: who you are, where you are, who it’s for, what makes it special.

## About the business
Explain the business type, main services / products, and positioning in a few short paragraphs.

## Who we serve
- Typical customer profiles (commuters, families, students, fitness enthusiasts, etc.)
- Typical visit / usage scenarios (weekday lunch, after-work training, weekend brunch, etc.)

## Where we are
- Full address + nearby landmarks
- How to get there by walking / public transport / driving

## Opening hours & booking
- Weekday / weekend / holiday hours
- Reservation / booking methods (phone, website form, app, messaging, etc.)

## Products & services
- Core offerings list (name + short description + who it’s best for)
- Optional: indicative price ranges or popular bundles

## FAQ
Q1: [common local question]
A1: [short but informative answer]

Q2: ...

## Tips
- Parking / waiting times / peak hours
- Kid / pet friendliness
- Any other local tips
```

For **service-area pages**, adapt the template to focus on coverage area and how on-site / remote
service works.

Output a `## Local Page Structures` section that:

- Includes at least one concrete template for location pages
- Optionally includes variants for:
  - Single-location vs. multi-location brands
  - High-repeat, low-ticket retail vs. high-ticket, trust-heavy services

### 5. Local structured data & listing alignment

Use or conceptually apply `geo-schema-gen` to design **structured data** for local entities and pages:

- Recommend appropriate `@type` selections:
  - `LocalBusiness` or specific subtypes such as `Restaurant`, `CafeOrCoffeeShop`, `Store`,
    `MedicalClinic`, `Dentist`, `HealthClub`, `EducationalOrganization`, etc.
  - `Service` for at-home / remote services
  - `Person` for key practitioners or experts when relevant
- For each key page type, specify required fields:
  - `name`, `image`, `url`, `telephone`
  - `address` (with postal address fields)
  - `geo` (latitude / longitude, if available)
  - `openingHoursSpecification`
  - `areaServed` / `serviceArea`
  - Industry-specific fields such as `servesCuisine`, `priceRange`, `amenityFeature`
  - `sameAs` linking to main map / listing profiles and strong social profiles

Output a `## Local Structured Data Package` section with:

- 1–2 example JSON-LD blocks for typical local scenarios (e.g. a single cafe + a city-level service page)
- A table mapping `Page URL pattern → Schema types → Key fields to fill`

Also align **map / listing profiles**:

- For each major platform (Google Maps, Apple Maps, local map apps, review sites, food delivery apps):
  - Suggest category and attribute choices
  - Suggest cover / hero photos and supporting images
  - Suggest a short, consistent description and key highlights, aligned with the website copy

### 6. Reviews, Q&A, and local UGC engine

Design a **sustainable local reputation engine** so search engines and AI models keep receiving fresh,
high-quality signals:

- Reviews:
  - Provide simple, natural review invitation scripts (offline and online)
  - Provide a “high-information review” template that gently encourages:
    - Visit / usage context (when they came, with whom)
    - Specific services / products used
    - Perceived value and who this is good for
  - Provide a response structure for negative reviews: empathize → explain (if needed) → offer a
    constructive resolution.
- Q&A:
  - List 5–15 of the most common questions for this type of business and location
  - Provide “standard answer” drafts suitable for map / listing Q&A and website FAQ pages, using
    clear, factual language that local search can understand
- UGC & social:
  - Suggest 3–5 local content themes for short videos / posts (e.g. “day in the life”, “neighborhood
    guide”, “behind the scenes”)
  - Suggest photo / content angles that strongly tie the business to the local area and typical use cases

Output a `## Local Reputation & Q&A Plan` section with:

- Review invitation scripts
- Example “good review” patterns
- Top FAQs + standard answer drafts

### 7. AI & crawler signaling for local content

Focus on how new or improved local content gets **discovered and trusted** by search engines and AI:

- Sitemaps:
  - Recommend including store pages, service-area pages, and local hubs in XML sitemaps
  - For multi-city or multi-language sites, suggest a clean sitemap structure
- `llms.txt` and AI index pages:
  - Use or conceptually apply `geo-llms-txt` to:
    - Add sections such as “Local / Locations / Stores / Clinics”
    - Point to key local hub pages and representative location pages
  - If no `llms.txt` exists, propose a minimal starter structure
- Internal linking:
  - Recommend internal links from:
    - About / story pages
    - Product or service descriptions
    - Local guides / blog posts
  - Ensure anchor text combines **geography + scenario + category** wherever reasonable
- External citations:
  - Suggest priority local citation sources: local directories, industry associations, local media,
    partner sites, community organizations, etc.

Output a `## Local AI & Crawler Signaling Plan` section with:

- A concise checklist of recommended actions
- A small table mapping `URL → Sitemaps / llms.txt / Internal links / External citations`

### 8. Measurement and iteration loop

Define what **success** means for local GEO in the age of AI, and how to iterate:

- Potential metrics:
  - Impressions and clicks for local queries in search tools (if the user has access)
  - Navigation / directions requests to locations
  - Calls, bookings, inquiries attributed to organic / local discovery
  - Orders, visits, or signups from local customers (including repeat visits)
  - Frequency of brand / location mentions in AI answers for relevant queries (if sampled manually
    or via tools)
- Iteration rhythm:
  - Recommend a light “local GEO review” every 1–3 months
  - Check: business info changes, review volume & quality, FAQ relevance, new photos or content needs

Output a `## Measurement & Iteration` section that:

- Lists 5–10 actionable metrics
- Suggests a simple review cadence and division of responsibilities (e.g. store managers vs. HQ team)

---

## Output format

Unless the user explicitly requests a different format, structure your answer as:

1. `## Local Business Brief`
2. `## Local Presence Snapshot`
3. `## Local Entity & Page Plan`
4. `## Local Page Structures`
5. `## Local Structured Data Package`
6. `## Local Reputation & Q&A Plan`
7. `## Local AI & Crawler Signaling Plan`
8. `## Measurement & Iteration`

Use:

- **Markdown headings and tables** for structure
- Bulleted lists instead of dense paragraphs
- Short, actionable sentences that local owners or operators can copy into task trackers or docs

If the user only asks for a **subset** (e.g., “just the store page structure and review scripts”), still
keep the headings but clearly mark skipped sections (e.g., “Not in scope for this request”).

---

## Example triggering prompts (for reference)

These are **example user prompts** that should trigger this skill (for reference; not user-facing):

- “I run three coffee shops in one city and want ChatGPT and Perplexity to be more likely to recommend
  us when people ask for good work-friendly cafes near our neighborhoods. Help me design a local GEO
  plan across our website, map listings, and reviews.”
- “We’re a small dental clinic that relies on local search. Please help us restructure our site,
  location pages, and Google Maps profile so that AI assistants and search engines can clearly
  understand who we serve, where we are, and when we’re open.”
- “I offer personal training in two districts and also do at-home sessions. I want a clear plan for
  local landing pages, service-area content, structured data, and reviews so that AI tools can
  confidently recommend me when users ask for trainers in my area.”

You do **not** need to surface this list directly to the user; it exists only to clarify intent.

