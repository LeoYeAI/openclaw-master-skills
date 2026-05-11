# BangunAI Blog Manager Skill

Agent skill untuk mengelola content BangunAI Blog — Digital Garden & Knowledge Base dengan Obsidian-like features (React 18 + Vite + MDX + Mermaid + KaTeX + Shiki).

## Quick Start

```bash
# Test skill dari workspace
cd /home/hades/BangunAI-Blog/skill
cat SKILL.md
```

## Workflows Available

| Workflow | Command | Description |
|----------|---------|-------------|
| `daily` | Bash script | Create daily note dengan rollover tasks |
| `fetch_last` | Bash script | Fetch latest file untuk style reference (supports about/now) |
| `write` | Bash script | Write new content dengan frontmatter |
| `log` | Bash script | Append log ke daily note |
| `read` | Bash script | Smart read content by keyword |
| `update_about` | Bash script | Update about.mdx page |
| `update_now` | Bash script | Update now.mdx page with timestamp |
| `verify_index` | Bash script | Verify content auto-import statistics |

## Content Structure

```
src/content/
├── writing/     # Blog posts (notes, essays)
├── articles/    # Technical articles, tutorials
├── read/        # Reading notes (bookmarks, link sharing)
├── daily/       # Daily notes (tasks, logs)
├── about.mdx    # About page (single file, MDX)
├── now.mdx      # Now page (single file, MDX)
└── index.ts     # Content loader (auto-import via import.meta.glob)
```

## Obsidian-Like Features

- **14 Callout Types** — info, tip, warning, danger, success, note, example, bug, question, abstract, important, caution, quote, cite
- **Mermaid Diagrams** — flowchart, sequence, pie, class, state, ER, gantt, mindmap, timeline
- **LaTeX Math (KaTeX)** — Inline `$...$` and block `$$...$$`
- **WikiLinks** — Internal linking dengan auto-strikethrough untuk broken links
- **Backlinks** — Auto-generated backlinks di setiap artikel
- **Graph View** — Interactive force-directed knowledge graph
- **Syntax Highlighting** — Shiki-powered dengan copy button
- **GFM Support** — Tables, task lists, strikethrough
- **Table of Contents** — Sticky TOC dengan active heading tracking

## Frontmatter Templates

### Standard Posts (writing, articles, daily)

```yaml
---
title: "Your Title"
slug: your-slug
summary: "Brief compelling summary"
type: note              # note | essay | article
category: Tech          # Tech | Refleksi | Produktivitas | Linux | Coding | Life
tags: [tag1, tag2]
date: "2026-02-12T15:30:00"
readingTime: 5
featured: false         # optional
---
```

### Read Items (read/)

```yaml
---
title: "Article Title"
slug: article-slug
snippet: "Interesting quote or snippet"
source: "website.com"
url: "https://full-url.com"
tags: [tag1, tag2]
date: "2026-02-12T18:00:00"
---
```

### Special Pages (about, now)

```yaml
---
title: "About"
---
```

## Usage Examples

### Create Daily Note
```bash
BLOG_ROOT="/home/hades/BangunAI-Blog"
DAILY_DIR="$BLOG_ROOT/src/content/daily"
mkdir -p "$DAILY_DIR"
TODAY=$(date +%Y-%m-%d)
# ... (see SKILL.md for full script)
```

### Fetch Style Reference
```bash
CATEGORY="writing"
BLOG_ROOT="/home/hades/BangunAI-Blog"
DIR="$BLOG_ROOT/src/content/$CATEGORY"
ls -t "$DIR"/*.mdx | head -n 1 | xargs head -n 40
```

### Create New Post
```bash
CATEGORY="writing"
FILENAME="my-new-post.mdx"
BLOG_ROOT="/home/hades/BangunAI-Blog"
cat > "$BLOG_ROOT/src/content/$CATEGORY/$FILENAME" <<'MDXEOF'
---
title: "My New Post"
slug: my-new-post
summary: "This is a new blog post"
type: note
category: Tech
tags: [example]
date: "2026-02-12T10:00:00"
readingTime: 3
---

## Introduction

Content here...
MDXEOF
```

## Integration with OpenCode

This skill is automatically loaded when:
- User asks to create blog content
- User mentions "BangunAI Blog"
- User wants to write MDX articles
- User needs frontmatter conventions

## Development Commands

```bash
# Start dev server
bun run dev

# Build production
bun run build

# Run tests
bun run test

# Lint code
bun run lint
```

## Path Configuration

- Blog Root: `/home/hades/BangunAI-Blog`
- Content Root: `/home/hades/BangunAI-Blog/src/content`
- Skill Location: `/home/hades/BangunAI-Blog/skill/`

## Categories

- **Tech** — Teknologi, programming, tools, frameworks
- **Refleksi** — Personal reflection, thoughts, philosophy
- **Produktivitas** — Productivity tips, workflow, GTD
- **Linux** — Linux, terminal, system administration
- **Coding** — Coding practices, patterns, best practices
- **Life** — Lifestyle, personal experiences, stories

## Content Types

- **note** — Short blog posts, quick thoughts, snapshots
- **essay** — Long-form personal writing, explorative thoughts
- **article** — Technical tutorials, structured guides, how-tos
- **daily** — Daily notes with tasks and logs

## MDX Components

| Component | Usage |
|-----------|-------|
| Callout | `<Callout type="info" title="...">...</Callout>` (14 types) |
| Mermaid | ` ```mermaid ... ``` ` (9+ diagram types) |
| LaTeX | `$...$` or `$$...$$` (KaTeX) |
| WikiLink | `<WikiLink to="slug" label="..." />` |
| Highlight | `<Highlight>...</Highlight>` or `<mark>` |
| YouTube | `<YouTube url="..." title="..." />` |
| Code | ` ```lang ... ``` ` (Shiki + copy button) |

