# BangunAI Blog Manager - Examples

Contoh lengkap penggunaan semua workflows.

## 1. Daily Note Workflow

```bash
BLOG_ROOT="/home/hades/BangunAI-Blog"
DAILY_DIR="$BLOG_ROOT/src/content/daily"
mkdir -p "$DAILY_DIR"

TODAY=$(date +%Y-%m-%d)
FILE="$DAILY_DIR/$TODAY.mdx"
LAST_FILE=$(find "$DAILY_DIR" -name "????-??-??.mdx" ! -name "$TODAY.mdx" 2>/dev/null | sort | tail -n 1)

if [ ! -f "$FILE" ]; then
  cat > "$FILE" <<DAILYEOF
---
title: "Daily Note: $TODAY"
date: "$TODAY"
type: daily
tags: [daily]
---

# Daily Note: $TODAY

DAILYEOF

  if [ -n "$LAST_FILE" ]; then
    PENDING=$(grep "\- \[ \]" "$LAST_FILE" || true)
    if [ -n "$PENDING" ]; then
      echo "## Rollover Tasks" >> "$FILE"
      echo "" >> "$FILE"
      echo "$PENDING" >> "$FILE"
      echo "" >> "$FILE"
    fi
  fi
  
  cat >> "$FILE" <<DAILYEOF
## Tasks Today

- [ ] 

## Log

DAILYEOF
  echo "✅ Created: $FILE"
else
  echo "📂 Exists: $FILE"
fi
```

## 2. Fetch Style Reference

### Fetch Writing Post Style
```bash
CATEGORY="writing"
BLOG_ROOT="/home/hades/BangunAI-Blog"
DIR="$BLOG_ROOT/src/content/$CATEGORY"
LAST_FILE=$(ls -t "$DIR"/*.mdx 2>/dev/null | head -n 1)
echo "📄 REFERENSI GAYA ($LAST_FILE):"
head -n 40 "$LAST_FILE"
```

### Fetch Read Item Style
```bash
CATEGORY="read"
BLOG_ROOT="/home/hades/BangunAI-Blog"
DIR="$BLOG_ROOT/src/content/$CATEGORY"
LAST_FILE=$(ls -t "$DIR"/*.mdx 2>/dev/null | head -n 1)
echo "📄 REFERENSI GAYA ($LAST_FILE):"
head -n 15 "$LAST_FILE"
```

### Fetch About Page
```bash
CATEGORY="about"
BLOG_ROOT="/home/hades/BangunAI-Blog"
cat "$BLOG_ROOT/src/content/about.mdx"
```

## 3. Create New Content

### Create Writing Post
```bash
CATEGORY="writing"
FILENAME="my-new-article.mdx"
BLOG_ROOT="/home/hades/BangunAI-Blog"

cat > "$BLOG_ROOT/src/content/$CATEGORY/$FILENAME" <<'WRITINGEOF'
---
title: "Judul Artikel Baru"
slug: judul-artikel-baru
summary: "Ringkasan singkat tentang artikel ini."
type: note
category: Tech
tags: [react, typescript]
date: "2026-02-12T15:00:00"
readingTime: 5
---

## Introduction

Paragraf pembuka yang menarik perhatian pembaca.

## Section 1

### Subsection A

Content here...

```typescript
// Example code
function example() {
  return "Hello World";
}
```

## Conclusion

Kesimpulan artikel.
WRITINGEOF

echo "✅ Created: $BLOG_ROOT/src/content/$CATEGORY/$FILENAME"
```

### Create Read Item
```bash
CATEGORY="read"
FILENAME="interesting-article.mdx"
BLOG_ROOT="/home/hades/BangunAI-Blog"

cat > "$BLOG_ROOT/src/content/$CATEGORY/$FILENAME" <<'READEOF'
---
title: "Interesting Article Title"
slug: interesting-article
snippet: "A compelling quote or snippet from the article."
source: "website.com"
url: "https://website.com/article"
tags: [tech, programming]
date: "2026-02-12T15:00:00"
---

## Key Takeaways

- Point 1
- Point 2
- Point 3

## Personal Notes

Catatan personal tentang artikel ini...
READEOF

echo "✅ Created: $BLOG_ROOT/src/content/$CATEGORY/$FILENAME"
```

### Create Article
```bash
CATEGORY="articles"
FILENAME="deep-dive-topic.mdx"
BLOG_ROOT="/home/hades/BangunAI-Blog"

cat > "$BLOG_ROOT/src/content/$CATEGORY/$FILENAME" <<'ARTICLEOF'
---
title: "Deep Dive: Topik Menarik"
slug: deep-dive-topic
summary: "Eksplorasi mendalam tentang topik tertentu."
type: article
category: Tech
tags: [architecture, system-design]
date: "2026-02-12T15:00:00"
readingTime: 15
---

## Overview

Long-form content untuk artikel mendalam.

## Section 1: Background

Content...

## Section 2: Technical Details

Content...

## Conclusion

Summary dan takeaways.
ARTICLEOF

echo "✅ Created: $BLOG_ROOT/src/content/$CATEGORY/$FILENAME"
```

## 4. Append Log to Daily Note

```bash
CONTENT="Finished writing new blog post about TypeScript"
TODAY=$(date +%Y-%m-%d)
FILE="/home/hades/BangunAI-Blog/src/content/daily/$TODAY.mdx"

if [ ! -f "$FILE" ]; then 
  echo "❌ Run 'daily' workflow first!"
  exit 1
fi

echo "- $(date +%H:%M) $CONTENT" >> "$FILE"
echo "✅ Logged to: $FILE"
```

## 5. Smart Read Content

```bash
# Search for file containing keyword
FILE="typescript"
RESULT=$(find "/home/hades/BangunAI-Blog/src/content" -name "*$FILE*.mdx" | head -n 1)

if [ -n "$RESULT" ]; then
  echo "📄 Found: $RESULT"
  cat "$RESULT"
else
  echo "❌ No file found matching: $FILE"
fi
```

## 6. Update About Page

```bash
FILE="/home/hades/BangunAI-Blog/src/content/about.mdx"

cat > "$FILE" <<'ABOUTEOF'
---
title: "About"
---

Hai, selamat datang di blog saya.

## Tentang Saya

Saya seorang developer yang passionate tentang...

## Tentang Blog Ini

Blog ini berisi...

## Kontak

Email: example@email.com
ABOUTEOF

echo "✅ Updated: $FILE"
```

## 7. Update Now Page

```bash
FILE="/home/hades/BangunAI-Blog/src/content/now.mdx"
CURRENT_DATE=$(date +"%B %Y")

cat > "$FILE" <<NOWEOF
---
title: "Now"
---

## Apa yang Sedang Saya Kerjakan

*Terakhir diperbarui: $CURRENT_DATE*

Halaman ini terinspirasi dari [nownownow.com](https://nownownow.com) — tempat saya mencatat apa yang sedang saya fokuskan saat ini.

---

### 🔨 Proyek

- Project 1
- Project 2

### 📚 Sedang Dibaca

- Book 1
- Book 2

### 🎯 Fokus Belajar

- Topic 1
- Topic 2

---

> *Halaman ini adalah snapshot dari kehidupan saya saat ini.*
NOWEOF

echo "✅ Updated: $FILE"
```

## 8. Verify Content Statistics

```bash
BLOG_ROOT="/home/hades/BangunAI-Blog"

echo "📊 Content Statistics:"
echo ""
echo "Writing posts: $(ls -1 "$BLOG_ROOT/src/content/writing"/*.mdx 2>/dev/null | wc -l)"
echo "Articles: $(ls -1 "$BLOG_ROOT/src/content/articles"/*.mdx 2>/dev/null | wc -l)"
echo "Read items: $(ls -1 "$BLOG_ROOT/src/content/read"/*.mdx 2>/dev/null | wc -l)"
echo "Daily notes: $(ls -1 "$BLOG_ROOT/src/content/daily"/*.mdx 2>/dev/null | wc -l)"
echo ""
echo "Special files:"
echo "- about.mdx: $(test -f "$BLOG_ROOT/src/content/about.mdx" && echo "✅" || echo "❌")"
echo "- now.mdx: $(test -f "$BLOG_ROOT/src/content/now.mdx" && echo "✅" || echo "❌")"
echo "- index.ts: $(test -f "$BLOG_ROOT/src/content/index.ts" && echo "✅" || echo "❌")"
```

## Common Tasks

### List All Posts by Category
```bash
echo "=== Writing Posts ==="
ls -lt /home/hades/BangunAI-Blog/src/content/writing/*.mdx | head -5

echo ""
echo "=== Articles ==="
ls -lt /home/hades/BangunAI-Blog/src/content/articles/*.mdx | head -5

echo ""
echo "=== Read Items ==="
ls -lt /home/hades/BangunAI-Blog/src/content/read/*.mdx | head -5
```

### Search for Keyword
```bash
KEYWORD="typescript"
echo "Searching for: $KEYWORD"
find /home/hades/BangunAI-Blog/src/content -name "*.mdx" -exec grep -l "$KEYWORD" {} \;
```

### Move/Rename Post
```bash
cd /home/hades/BangunAI-Blog
git mv src/content/writing/old-name.mdx src/content/writing/new-name.mdx
echo "✅ Renamed post (git tracked)"
```

### Delete Post
```bash
cd /home/hades/BangunAI-Blog
git rm src/content/writing/unwanted-post.mdx
echo "✅ Deleted post (git tracked)"
```

## Integration with index.ts

File `src/content/index.ts` **auto-detect** semua MDX files:

```typescript
// Auto-import all MDX files (no manual registration needed!)
const writingModules = import.meta.glob<MdxModule>("./writing/*.mdx", { eager: true });
const articleModules = import.meta.glob<MdxModule>("./articles/*.mdx", { eager: true });
const readModules = import.meta.glob<MdxModule>("./read/*.mdx", { eager: true });
const aboutModule = import.meta.glob<MdxModule>("./about.mdx", { eager: true });
const nowModule = import.meta.glob<MdxModule>("./now.mdx", { eager: true });
```

**Artinya:** Setiap kali kamu create file `.mdx` baru di folder yang tepat, file itu **otomatis ter-import** tanpa perlu edit `index.ts`!

## Tips & Best Practices

1. **Always use frontmatter** — Semua MDX file harus punya frontmatter minimal
2. **Consistent slugs** — Gunakan kebab-case, lowercase, no special chars
3. **ISO timestamps** — Format date: `"2026-02-12T15:00:00"`
4. **Git tracking** — Gunakan `git mv` dan `git rm` untuk preserve history
5. **Auto-import** — Tidak perlu edit `index.ts`, semua MDX auto-detected
6. **Reading time** — Estimasi ~200 kata/menit
7. **Tags lowercase** — Konsisten pakai lowercase untuk tags
8. **Category consistency** — Pilih dari: Tech, Life, Design, Business

