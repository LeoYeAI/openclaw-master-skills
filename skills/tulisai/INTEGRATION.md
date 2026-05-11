# BangunAI Blog Manager - Integration Guide

Complete integration guide untuk skill dengan BangunAI Blog (Digital Garden + Obsidian-like features).

## 🌿 Content Structure

```
src/content/
├── writing/     11 posts (notes, essays)
├── articles/    4 posts (technical tutorials)
├── read/        8 items (curated readings)
├── daily/       1 note (growing daily)
├── about.mdx    Single static page
├── now.mdx      Single dynamic page
└── index.ts     Auto-import loader
```

## 📝 Frontmatter Formats

### A. Standard (writing, articles, daily)
- **Required:** title, slug, summary, type, category, tags, date, readingTime
- **Type:** `note` | `essay` | `article`
- **Category:** `Tech` | `Refleksi` | `Produktivitas` | `Linux` | `Coding` | `Life`
- **Date:** ISO with time (`YYYY-MM-DDTHH:mm:ss`)

### B. Read Items (read/)
- **Required:** title, slug, snippet, source, url, tags, date
- **Body:** Optional (for personal notes)

### C. Special (about, now)
- **Required:** title only
- **Content:** Full MDX support

## 🧩 Obsidian-Like Features

| Feature | Implementation | Component |
|---------|----------------|-----------|
| Callouts | 14 types | `<Callout type="..." title="...">` |
| Mermaid | 9+ diagram types | ` ```mermaid ... ``` ` |
| LaTeX | Inline & block | `$...$` or `$$...$$` |
| WikiLinks | Internal linking | `<WikiLink to="slug" />` |
| Backlinks | Auto-generated | Auto in ArticleDetail |
| Graph View | Interactive | `/graph` route |
| TOC | Sticky + mobile | Auto-generated |
| Syntax Highlight | Shiki + copy | ` ```lang ... ``` ` |
| GFM | Tables, tasks | Standard Markdown |

## 🔧 8 Workflows

1. **daily** - Create daily note with rollover tasks
2. **fetch_last** - Style reference (supports about/now)
3. **write** - New content (multi-format frontmatter)
4. **log** - Append timestamped log
5. **read** - Smart search by keyword
6. **update_about** - Update about.mdx
7. **update_now** - Update now.mdx (auto-date)
8. **verify_index** - Content statistics

## 🎨 Design System

### Color Tokens (HSL)
- Dark Mode: Navy (#1A1A2E) + Cream (#F5E6D3)
- Light Mode: Cream + Navy
- Primary: Gold/amber accents

### Font Stack
- **Space Grotesk** - Headings
- **Source Serif 4** - Body
- **Inter** - UI elements
- **JetBrains Mono** - Code

### Glass Morphism
```tsx
<div className="glass glass-hover">...</div>
```

## 🚀 Auto-Import System

`src/content/index.ts` uses `import.meta.glob`:

```typescript
const writingModules = import.meta.glob("./writing/*.mdx", { eager: true });
```

**Result:** Create file → Auto-detected → Available immediately

## ✅ Best Practices

### Frontmatter
- Use ISO timestamps with time
- Tags: lowercase, kebab-case
- Category: exact match from list
- Type: note/essay/article

### File Naming
- kebab-case.mdx
- Descriptive names
- No spaces, no uppercase

### Content Structure
```mdx
## Introduction (H2)
### Subsection (H3)
<Callout>...</Callout>
## Conclusion (H2)
```

### Git Operations
```bash
git mv old.mdx new.mdx    # Preserve history
git rm unwanted.mdx        # Track deletion
```

## 📊 Current Statistics

```
Writing: 11 posts
Articles: 4 posts
Read: 8 items
Daily: 1 note
Special: 2 pages (about, now)
Total: 26 content files
```

## 🔗 Key URLs

- **Repo:** https://github.com/dwirx/BangunAI-Blog
- **Local:** http://localhost:8080
- **Routes:** `/`, `/writing`, `/artikel`, `/read`, `/tags`, `/graph`, `/now`, `/about`

## 📚 Documentation

- `SKILL.md` - Complete workflow guide (600+ lines)
- `README.md` - Quick reference
- `EXAMPLES.md` - Copy-paste examples
- `INTEGRATION.md` - This file

## 🎯 Migration Notes

### From Obsidian (ObsBlog)

**Changes:**
- ✅ Path: `/home/hades/ObsBlog` → `/home/hades/BangunAI-Blog`
- ✅ Format: `.md` → `.mdx`
- ✅ Frontmatter: Obsidian → BangunAI (more structured)
- ✅ Components: Obsidian callouts → React MDX components
- ✅ Features: Full Obsidian-like support (callouts, mermaid, LaTeX, wikilinks, backlinks, graph)

**Preserved:**
- ✅ Daily workflow (rollover tasks)
- ✅ Fetch style workflow
- ✅ Write workflow
- ✅ Log workflow
- ✅ Read workflow

**New:**
- ✅ 3 additional workflows (update_about, update_now, verify_index)
- ✅ MDX components (Callout, Mermaid, WikiLink, YouTube, etc.)
- ✅ Auto-import system
- ✅ Design system tokens
- ✅ Multiple content types (note/essay/article)
- ✅ 6 category options

## 🔍 Troubleshooting

### Content not showing
- Check frontmatter required fields
- Verify file in correct directory
- Restart dev server

### Mermaid not rendering
- Validate Mermaid syntax
- Check diagram type supported
- Browser console for errors

### WikiLink strikethrough
- Target slug not found
- Verify spelling
- Check target frontmatter

### LaTeX not rendering
- Validate LaTeX syntax
- Proper delimiters `$` or `$$`
- Escape special characters

## 🎉 Status

✅ **Fully integrated** with BangunAI Blog
✅ **8 workflows** production-ready
✅ **3 frontmatter formats** supported
✅ **14 callout types** available
✅ **9+ diagram types** via Mermaid
✅ **LaTeX math** via KaTeX
✅ **Auto-import** via import.meta.glob
✅ **Design system** documented
✅ **Best practices** established

**Ready for production use!** 🚀
