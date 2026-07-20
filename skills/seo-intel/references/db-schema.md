# SEO Intel — Database Schema Reference

SQLite database. Created automatically on first run from `db/schema.sql`.

## Tables

### domains
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| domain | TEXT UNIQUE | e.g. "carbium.io" |
| project | TEXT | Project name |
| role | TEXT | "target" or "competitor" |
| first_seen | INTEGER | Epoch ms |
| last_crawled | INTEGER | Epoch ms |

### pages
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| domain_id | INTEGER FK → domains | |
| url | TEXT UNIQUE | Full URL |
| crawled_at | INTEGER | Epoch ms |
| status_code | INTEGER | HTTP status |
| word_count | INTEGER | Body text words |
| load_ms | INTEGER | Page load time |
| is_indexable | INTEGER | 1 = yes |
| click_depth | INTEGER | BFS depth from homepage (0 = homepage) |
| published_date | TEXT | ISO date or null |
| modified_date | TEXT | ISO date or null |
| content_hash | TEXT | SHA-256 for incremental crawling |

### extractions (Solo tier)
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| page_id | INTEGER FK → pages | |
| title | TEXT | Extracted title |
| meta_desc | TEXT | Meta description |
| h1 | TEXT | Primary heading |
| product_type | TEXT | |
| pricing_tier | TEXT | free/freemium/paid/enterprise/none |
| cta_primary | TEXT | |
| tech_stack | TEXT | JSON array |
| schema_types | TEXT | JSON array |
| search_intent | TEXT | Informational/Navigational/Commercial/Transactional |
| primary_entities | TEXT | JSON array of 3-7 concept strings |

### headings
| Column | Type | Notes |
|---|---|---|
| page_id | INTEGER FK → pages | |
| level | INTEGER | 1-6 |
| text | TEXT | Heading content |

### keywords
| Column | Type | Notes |
|---|---|---|
| page_id | INTEGER FK → pages | |
| keyword | TEXT | |
| location | TEXT | title/h1/h2/meta/body |

### links
| Column | Type | Notes |
|---|---|---|
| source_id | INTEGER FK → pages | |
| target_url | TEXT | |
| anchor_text | TEXT | |
| is_internal | INTEGER | 1 = same domain |

### technical
| Column | Type | Notes |
|---|---|---|
| page_id | INTEGER FK → pages | |
| has_canonical | INTEGER | 0/1 |
| has_og_tags | INTEGER | 0/1 |
| has_schema | INTEGER | 0/1 |
| has_sitemap | INTEGER | 0/1 |
| has_robots | INTEGER | 0/1 |

### page_schemas
| Column | Type | Notes |
|---|---|---|
| page_id | INTEGER FK → pages | |
| schema_type | TEXT | @type: Organization, Product, FAQ, etc. |
| name | TEXT | |
| description | TEXT | |
| rating | REAL | aggregateRating value |
| price | TEXT | |
| raw_json | TEXT | Full JSON-LD object |

### analyses (Solo tier)
| Column | Type | Notes |
|---|---|---|
| project | TEXT | |
| generated_at | INTEGER | |
| model | TEXT | Which AI model |
| keyword_gaps | TEXT | JSON array |
| content_gaps | TEXT | JSON array |
| quick_wins | TEXT | JSON array |
| new_pages | TEXT | JSON array |
| positioning | TEXT | Strategic positioning text |
| raw | TEXT | Full model response |

## Key Relationships
- `domains.id` → `pages.domain_id`
- `pages.id` → `extractions.page_id`, `headings.page_id`, `keywords.page_id`, `links.source_id`, `technical.page_id`, `page_schemas.page_id`
- Filter by project: `WHERE domains.project = ?`
- Filter by role: `WHERE domains.role = 'target'` or `'competitor'`
