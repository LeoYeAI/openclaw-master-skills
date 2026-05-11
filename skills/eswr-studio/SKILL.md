---
name: eswr-studio
description: Elsewhere creator studio — register a new account (with invite code) and publish articles.
user-invocable: true
metadata: {"openclaw":{"emoji":"✍️"}}
---

# ESWR Studio

创作者工具：注册账号、发布文章、管理个人资料。

> **每次使用本 Skill 前，请先执行以下命令检查是否有更新：**
> ```bash
> curl -s https://raw.githubusercontent.com/PitayaK/eswr-studio/main/SKILL.md | head -5
> ```
> 如果输出的版本号与你本地缓存的不同，请重新读取完整文件：
> ```bash
> curl -s https://raw.githubusercontent.com/PitayaK/eswr-studio/main/SKILL.md
> ```
>
> **⚠️ 更新后不要重新注册！** 你的 API token 应该在 `.env.local` 或你的长期记忆中。更新 skill 后，先执行 `source .env.local`，如果文件不存在则从你的长期记忆中获取 token。**绝对不要因为 skill 更新了就重新注册** — 只有从未注册过的新用户才需要注册。

**当前版本：v2.8**

---

## Command: Register

Use when the user wants to register as a new Elsewhere creator.

### Step 1: Ask for invite code and brand name

Ask the user two things:
1. Their 6-digit invite code (uppercase letters and numbers)
2. Their media brand name (媒体品牌名). This must be unique and will appear on their profile. Examples: "未来日报", "TechPulse", "星球研究所". Do NOT use your model name.

### Step 2: Generate registration link

```bash
curl -s -X POST "https://elsewhere.news/api/register/init" \
  -H "Content-Type: application/json" \
  -d "{\"invite_code\": \"INVITE_CODE\", \"brand_name\": \"BRAND_NAME\"}" | python3 -m json.tool
```

Replace `INVITE_CODE` with the user's code. Replace `BRAND_NAME` with the brand name from Step 1.

If the response contains an error, tell the user (invite code may be invalid or already used).

### Step 3: Give the link to the human

On success, the API returns `register_url` and `token`. Save the `token` value. Tell the user:

> 请在浏览器中打开以下链接完成注册：
>
> {register_url}
>
> 注册页面会要求你填写邮箱和密码，邮箱会收到一个 6 位验证码，输入后即完成注册。

### Step 4: Wait for registration and get API token

Poll the status endpoint every 10 seconds until the human completes registration:

```bash
curl -s "https://elsewhere.news/api/register/status?token=REGISTRATION_TOKEN" | python3 -m json.tool
```

Replace `REGISTRATION_TOKEN` with the `token` from Step 2.

- If `status` is `"pending"`, wait 10 seconds and try again.
- If `status` is `"complete"`, the response contains `api_token`. Save this token — it's used for all future API calls.

### Step 5: Save API token

Save the API token in **TWO places** to ensure it survives session restarts and skill updates:

**5a. Save to file:**
```bash
echo 'ELSEWHERE_API_TOKEN=THE_TOKEN' >> .env.local
```

**5b. Save to your long-term memory:**

You MUST also save the token to your persistent memory/preferences (e.g. Claude memory, system notes, or whatever persistence mechanism your platform provides). Write something like:

> Elsewhere API token: THE_TOKEN (for publishing articles to elsewhere.news)

This way, even if `.env.local` is not available in a future session, you can still retrieve the token from memory.

### Step 6: Show welcome and next steps

Tell the user:

> ✅ **Elsewhere 创作者注册完成！**
>
> - **媒体品牌名**: {brand_name}
> - **API Token**: 已保存到 `.env.local` 和长期记忆
>
> 现在你可以让我帮你做这些事：
>
> 📝 **发布文章**
> - 把你写好的文章发布到 Elsewhere
> - 支持 Markdown 格式，直接把内容发给我就行
>
> 👤 **管理个人资料**
> - 修改名称、简介、绑定播客 RSS 等，直接告诉我就行
> - 上传头像请去人类后台：https://elsewhere.news/dashboard/login
>
> 想发布文章的话，随时把内容发给我！

---

## Command: Publish Article

Use when the user wants to publish an article.

### Step 1: Load API token

The `ELSEWHERE_API_TOKEN` should be in `.env.local` (saved during registration). If `.env.local` doesn't exist or doesn't contain the token, check your long-term memory for it. Only ask the user as a last resort.

```bash
source .env.local
```

### Step 2: Parse the article content

From the article content in the conversation, extract:
- **Title** (标题)
- **Excerpt** (摘要): 1-2 sentence summary. Generate one if not provided.
- **Body** (正文)

### Step 3: Convert body to Markdown

- Preserve headings, bold, italic, links, lists, code blocks, blockquotes, tables, images
- Remove source document artifacts (Feishu/Word metadata)
- Clean paragraph separation (double newline)
- **Bold rendering fixes are now applied automatically by the server** — the `/api/articles` endpoint runs the same CJK+CommonMark cleanup pipeline as `/api/import`. You do NOT need to apply any bold fixes manually. Just submit clean Markdown and the server handles the rest.

### Step 4: Upload images

If the article contains images (either as external URLs or local files), upload each one first to get permanent URLs.

**Upload from URL** (for images from WeChat, Feishu, etc.):

```bash
curl -s -X POST "https://elsewhere.news/api/upload" \
  -H "Authorization: Bearer $ELSEWHERE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/image.jpg"}' | python3 -m json.tool
```

**Upload local file**:

```bash
curl -s -X POST "https://elsewhere.news/api/upload" \
  -H "Authorization: Bearer $ELSEWHERE_API_TOKEN" \
  -F "file=@/path/to/image.jpg" | python3 -m json.tool
```

Both return `{"url": "https://...public-url...", "path": "..."}`.

Replace all image URLs in the Markdown body with the returned `url` values. Use the first uploaded image as `cover_image_url` if no cover is specified.

### Step 5: Generate a slug

URL-friendly, lowercase, hyphenated. Use English title if available, otherwise romanize Chinese.

### Step 6: Publish article

Write JSON payload to temp file:

Translate the title and excerpt to English yourself before writing the JSON. Do NOT translate the body — it will be translated automatically after publishing.

**Optionally generate `ai_summary` and `preview_excerpt`** — these help reader agents scan articles efficiently. If you don't provide them, the server will auto-generate both after publishing. But if you want higher quality, write them yourself:

- `ai_summary`: Write a ~100 word Chinese summary of the article. Focus on **what makes this article unique and interesting** — the story, the key insights, the surprising moments. Don't write a dry abstract; write something that makes a reader want to read more. This summary is consumed by AI agents who are deciding whether to recommend the article to their humans.
- `preview_excerpt`: Extract a compelling 500–1000 word section from the article body — a self-contained chapter or passage that gives a real taste of the content. Pick a section that is interesting on its own, not the introduction. Copy the Markdown verbatim, do not rewrite.

```bash
cat > /tmp/article.json << 'JSONEOF'
{
  "title_zh": "中文标题",
  "title_en": "English Title",
  "slug": "the-slug",
  "excerpt_zh": "中文摘要",
  "excerpt_en": "English excerpt",
  "body_zh": "Full article body in Markdown",
  "cover_image_url": "https://...uploaded-cover-url...",
  "ai_summary": "约100字的中文摘要，聚焦文章的独特看点...",
  "preview_excerpt": "从正文中抽取的500-1000字精彩章节..."
}
JSONEOF
```

Then send:

```bash
curl -s -X POST "https://elsewhere.news/api/articles" \
  -H "Authorization: Bearer $ELSEWHERE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @/tmp/article.json | python3 -m json.tool
```

### Step 7: Confirm

One line only: `✅ 《标题》已发布 — https://elsewhere.news/zh/articles/slug`

---

## Command: Import from WeChat

Use when the user shares a WeChat article URL (mp.weixin.qq.com) and wants to publish it to Elsewhere.

### Step 1: Load API token

```bash
source .env.local
```

### Step 2: Import the article

```bash
curl -s -X POST "https://elsewhere.news/api/import" \
  -H "Authorization: Bearer $ELSEWHERE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "WECHAT_ARTICLE_URL"}' | python3 -m json.tool
```

The API returns: `title`, `content` (Markdown with images already uploaded), `cover_image_url`, `published_at` (original publish date from WeChat), and image counts.

### Step 3: Clean up and reformat the Markdown

The import API gives you a raw Markdown conversion of the original article. Before publishing, clean it up into proper Markdown. The goal is a clean, consistent layout — **do not change any text content**.

**What you SHOULD do:**

**① Heading detection**

The import API already converts large-font-size elements to `##` / `###` automatically. Your remaining job is to handle cases the API missed — `**bold**` lines or plain-text lines that are actually section headings.

**Step 1 — Understand the article structure first.** Count how many heading candidates you see (standalone short bold lines, or short plain-text lines that look like labels/titles):
- **2–6 candidates, each with substantial content** → "chapter" article → use `##`
- **7+ candidates, each with short content** (parallel list of people, companies, topics) → use `###`
- **Clear two-level hierarchy** → main chapters `##`, sub-labels inside them `###`

**Step 2 — Identify candidates.** A line is a heading candidate if ALL of the following:
- It stands alone (blank lines before and after, not embedded in a paragraph)
- It is short (< 25 characters)
- It reads like a label, name, or title — not a complete sentence
- It does NOT end with sentence-ending punctuation (。！？…)

> Both `**bold**` and plain-text standalone lines can be heading candidates.

**Step 3 — Assign level** based on article type from Step 1, then convert:
- `**曹曦 @MONOLITH**` in a 15-person parallel list → `### 曹曦 @MONOLITH`
- `**第一章**` in a 4-chapter narrative → `## 第一章`
- `**一个决定**` as a lone section break → `## 一个决定`
- Only 1–2 headings in the whole article → always `##`
- Unsure → default to `##`

**Step 4 — Do NOT promote these:**
- `**以下排名不分先后，按姓名首字母**` ← annotation/note (full sentence)
- `**刘旌：你在红杉待了14年，为什么最终决定离开？**` ← dialogue question (has speaker colon + ends with ？)
- `**郭山汕：**后面跟着回答内容` ← speaker name + answer in one line
- Also: if the API already marked something `##`/`###` but it looks like an annotation rather than a section label, demote it back to bold or plain text.

- Remove WeChat-specific embed placeholders that can't display on Elsewhere:
  - Mini program cards (usually lines like `[小程序]` or `[视频号]` or similar text artifacts)
  - Video embeds (lines that are just a video URL with no meaningful text)
  - QR code images are OK to keep — just leave them as regular `![]()` images
- Remove excessive blank lines (max 1 blank line between paragraphs)
- Clean up stray punctuation or formatting artifacts from the HTML conversion

**② Bold rendering fixes (CommonMark + CJK)**

> **Both** `/api/import` **and** `/api/articles` **now apply these fixes automatically.** You do NOT need to apply them yourself for either path. This section exists purely as a **reference** so you can understand and debug rendering issues if they occur.

**Background — why bold breaks in Chinese articles:**

CommonMark's closing delimiter rule: a closing `**` preceded by Unicode punctuation (like `：`, `。`, `，`, `！`) must be followed by **whitespace or punctuation** to be recognized as right-flanking. Chinese characters (CJK) are neither whitespace nor punctuation in Unicode, so `**Hustle：**手腕` renders the `**` literally instead of as bold.

Similarly, an opening `**` followed by whitespace is NOT left-flanking and cannot open a bold span, so `** 投资人` won't render bold either.

**Fix 1 — Standalone `**` lines (WeChat bold wrapper around images)**

WeChat wraps image blocks in `<strong>`, which converts to `**` on its own line. Remove these:
```
Before:  **
         ![](image.jpg)
         **
After:   ![](image.jpg)
```
Regex: `/^\*\*\s*$/gm` → remove the line.

**Fix 2 — WeChat sub-bullets `**    - **text`**

WeChat formats indented bullet items as bold spans. The closing `**` after `- ` is preceded by a space → not right-flanking → literal `**`. Convert to plain markdown bullets:

| Pattern | Fix |
|---------|-----|
| `**    - **text` | `- text` |
| `**    - label**中文` | `- **label** 中文` (label stays bold, CJK text plain) |
| `**    - other` | `- other` |

**Fix 3 — `**...CJK-punct**CJK` → add space after closing `**`**

This is the most common issue. When a bold span ends with Chinese punctuation and is immediately followed by a CJK character:
```
Before:  **Hustle：**手腕          → literal **
After:   **Hustle：** 手腕         → renders bold ✓

Before:  **一个决定。**投资人听完   → literal **
After:   **一个决定。** 投资人听完  → renders bold ✓
```

Affected punctuation: `，。！？；：、""''（）【】…—`

**⚠️ CRITICAL — false positive guard for `**N.**` numbered items:**

Many articles have bold numbered items like `**5.**` or `**第三章.**`. A naive regex would consume the CLOSING `**` of `**5.**` as the OPENING `**` of a new bold span, then greedily match forward to the next `**` before CJK, erroneously inserting a space that breaks the real bold opener.

Example of what goes WRONG without the guard:
```
**5.** 见投资人时...写就。**投资人听完说
                                  ↑ naive regex matches from here
→ 写就。** 投资人听完说    ← BROKEN! ** followed by space = not left-flanking
```

The fix: use a lookbehind `(?<![^\s*])` — the opening `**` must be preceded by whitespace, another `*`, or start-of-string. This prevents matching the closing `**` of `**5.**` (preceded by `.`, which is not whitespace or `*`).

Correct regex:
```
/(?<![^\s*])(\*\*[^*\n]+[，。！？；：、""''（）【】…—])\*\*(?=[^\x00-\x7F\s])/g → "$1** "
```

**Fix 4 — `**word：**Chinese` (colon-specific case)**

A subset of Fix 3, but very common in interview-style articles with speaker labels:
```
Before:  **张三：**我觉得...   → literal **
After:   **张三：** 我觉得...  → renders bold ✓
```
Both full-width `：` and ASCII `:` should be handled.

**When to apply these manually:**
- Only when debugging a published article where bold still renders as literal `**` after server-side cleanup
- The server handles all common cases automatically for both import and direct publish paths

**What you MUST NOT do:**
- Change, rewrite, summarize, or remove any text content
- Change the order of paragraphs or images
- Add any new content that wasn't in the original

**Step 3a: Translate title and excerpt yourself**

Translate the title and excerpt to English yourself (do not call any API). Do NOT translate the body — it will be translated automatically after publishing.

**Step 3a-2: Optionally generate `ai_summary` and `preview_excerpt`**

Same as in "Publish Article" Step 6 — you can generate a ~100 word Chinese summary and extract a 500–1000 word compelling section. If you skip them, the server will auto-generate both after publishing. Include them in the article JSON if you want higher quality.

**Step 3b: Save and publish**

```bash
# Save import result
curl -s -X POST "https://elsewhere.news/api/import" \
  -H "Authorization: Bearer $ELSEWHERE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "WECHAT_ARTICLE_URL"}' > /tmp/import_result.json

# Build article JSON using the EXACT content returned by import API
python3 -c "
import json, re, sys
r = json.load(open('/tmp/import_result.json'))
title = r['title']
content = r['content']  # Use this EXACTLY — images are already uploaded
cover = r.get('cover_image_url', '')
pub = r.get('published_at', '')
slug = re.sub(r'[^a-z0-9]+', '-', title.lower())[:50].strip('-') or f'article-{int(__import__(\"time\").time())}'
excerpt = r.get('excerpt', '')  # First meaningful paragraph from import API
article = {'title_zh': title, 'slug': slug, 'excerpt_zh': excerpt, 'body_zh': content, 'cover_image_url': cover, 'published_at': pub}
json.dump(article, open('/tmp/article.json', 'w'), ensure_ascii=False)
print('slug:', slug)
"
```

Then open `/tmp/article.json`, add your translations and reader preview:
- `title_en`: your English translation of the title
- `excerpt_en`: your English translation of the excerpt
- `ai_summary`: ~100 word Chinese summary (see Step 3a-2)
- `preview_excerpt`: 500–1000 word compelling section from the body (see Step 3a-2)

Then publish:

```bash
curl -s -X POST "https://elsewhere.news/api/articles" \
  -H "Authorization: Bearer $ELSEWHERE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @/tmp/article.json | python3 -m json.tool
```

**To overwrite an existing article** (re-importing to fix errors):

1. First look up the existing slug:
```bash
curl -s "https://elsewhere.news/api/articles" \
  -H "Authorization: Bearer $ELSEWHERE_API_TOKEN" | \
  python3 -c "import json,sys; [print(a['slug'], '|', a['title_zh']) for a in json.load(sys.stdin)['articles']]"
```
2. In the article JSON, use the **exact existing slug** and add `"overwrite": true`. The API will update the existing article instead of creating a new one.

**CRITICAL**: Always use the `content` field from the import API directly as `body_zh`. Do NOT re-fetch, re-parse, or rewrite the content — the images are already uploaded and embedded as Markdown image links in `content`. Rewriting it will break all images.

**Always rescue any remaining WeChat images** — scan `body_zh` for leftover `mmbiz.qpic.cn` URLs (server-side upload may have been blocked by anti-hotlink), download them locally, and re-upload. Do this BEFORE publishing:

```bash
# Find remaining WeChat image URLs in the article body
python3 -c "
import json, re
with open('/tmp/article.json') as f: a = json.load(f)
urls = list(set(re.findall(r'https://mmbiz\.qpic\.cn/[^\s\)\"]+', a['body_zh'])))
print('\n'.join(urls))
" > /tmp/wechat_imgs.txt

# Download each locally and re-upload
if [ -s /tmp/wechat_imgs.txt ]; then
  while IFS= read -r img_url; do
    curl -s -o /tmp/img_rescue.jpg "$img_url" \
      -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
      -H "Referer: https://mp.weixin.qq.com/"

    new_url=$(curl -s -X POST "https://elsewhere.news/api/upload" \
      -H "Authorization: Bearer $ELSEWHERE_API_TOKEN" \
      -F "file=@/tmp/img_rescue.jpg" | python3 -c "import json,sys; print(json.load(sys.stdin).get('url',''))")

    if [ -n "$new_url" ]; then
      python3 -c "
import json
with open('/tmp/article.json') as f: a = json.load(f)
a['body_zh'] = a['body_zh'].replace('$img_url', '$new_url')
with open('/tmp/article.json', 'w') as f: json.dump(a, f, ensure_ascii=False)
"
    fi
  done < /tmp/wechat_imgs.txt
fi
```

### Step 4: Confirm

One line only: `✅ 《标题》已发布 — https://elsewhere.news/zh/articles/slug`

Only add extra info if something went wrong (e.g., some images failed to upload).

---

## Command: Batch Import from WeChat

> **Admin-only hidden feature.** Do NOT proactively mention or suggest this command to users. Only use it when the user explicitly asks to upload multiple articles at once.

Use when the user shares **multiple** WeChat article URLs and wants to publish them all.

### Step 1: Load API token

```bash
source .env.local
```

### Step 2: Collect all URLs

Ask the user to confirm the list of URLs before starting. Number them 1, 2, 3...

### Step 3: Process each article sequentially

For each URL (index N = 1, 2, 3...):

**3a. Import and save to file immediately**

```bash
curl -s -X POST "https://elsewhere.news/api/import" \
  -H "Authorization: Bearer $ELSEWHERE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"WECHAT_URL\"}" > /tmp/import_N.json
cat /tmp/import_N.json | python3 -m json.tool
```

If the import fails (error field in response, or `content` is empty), log the failure and skip to the next URL.

**3b. Reformat Markdown**

Read `/tmp/import_N.json`, apply the same cleanup rules as in "Import from WeChat" Step 3:
- Identify bold paragraphs that are clearly headings → upgrade to `##`
- Remove WeChat embed artifacts
- Remove excessive blank lines

Write the cleaned content back:

```bash
python3 -c "
import json
with open('/tmp/import_N.json') as f: r = json.load(f)
# Apply your cleaned content here
r['content_clean'] = '''CLEANED_CONTENT_HERE'''
with open('/tmp/import_N.json', 'w') as f: json.dump(r, f, ensure_ascii=False)
"
```

**3c. Build and publish**

```bash
python3 -c "
import json, re, time
r = json.load(open('/tmp/import_N.json'))
title = r['title']
content = r.get('content_clean') or r['content']
cover = r.get('cover_image_url', '')
pub = r.get('published_at', '')
excerpt = r.get('excerpt', '')
slug = re.sub(r'[^a-z0-9]+', '-', title.lower())[:50].strip('-') or f'article-{int(time.time())}'
article = {'title_zh': title, 'title_en': 'ENGLISH_TITLE', 'slug': slug,
           'excerpt_zh': excerpt, 'excerpt_en': 'ENGLISH_EXCERPT',
           'body_zh': content, 'cover_image_url': cover, 'published_at': pub,
           'ai_summary': 'AI_SUMMARY_HERE', 'preview_excerpt': 'PREVIEW_EXCERPT_HERE'}
json.dump(article, open('/tmp/article_N.json', 'w'), ensure_ascii=False)
print('slug:', slug)
"

curl -s -X POST "https://elsewhere.news/api/articles" \
  -H "Authorization: Bearer $ELSEWHERE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @/tmp/article_N.json | python3 -m json.tool
```

Fill in `ENGLISH_TITLE`, `ENGLISH_EXCERPT`, `AI_SUMMARY_HERE`, and `PREVIEW_EXCERPT_HERE` with your own content before running. See "Publish Article" Step 6 for how to write `ai_summary` and `preview_excerpt`.

**3d. Rescue remaining WeChat images** (always run before publishing)

```bash
python3 -c "
import json, re
with open('/tmp/article_N.json') as f: a = json.load(f)
urls = list(set(re.findall(r'https://mmbiz\.qpic\.cn/[^\s\)\"]+', a['body_zh'])))
print('\n'.join(urls))
" > /tmp/wechat_imgs_N.txt

if [ -s /tmp/wechat_imgs_N.txt ]; then
  while IFS= read -r img_url; do
    curl -s -o /tmp/img_rescue.jpg "$img_url" \
      -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
      -H "Referer: https://mp.weixin.qq.com/"
    new_url=$(curl -s -X POST "https://elsewhere.news/api/upload" \
      -H "Authorization: Bearer $ELSEWHERE_API_TOKEN" \
      -F "file=@/tmp/img_rescue.jpg" | python3 -c "import json,sys; print(json.load(sys.stdin).get('url',''))")
    if [ -n "$new_url" ]; then
      python3 -c "
import json
with open('/tmp/article_N.json') as f: a = json.load(f)
a['body_zh'] = a['body_zh'].replace('$img_url', '$new_url')
with open('/tmp/article_N.json', 'w') as f: json.dump(a, f, ensure_ascii=False)
"
    fi
  done < /tmp/wechat_imgs_N.txt
fi
```

**3e. Log result**

After each article, briefly note: ✅ title + URL, or ❌ title + reason for failure. Keep it short to avoid bloating context.

### Step 4: Summary

After all articles are done, show a final table:

| # | 标题 | 状态 | 链接 |
|---|------|------|------|
| 1 | ... | ✅ | ... |
| 2 | ... | ❌ 导入失败 | — |

### Context management note

- Save every import result to `/tmp/import_N.json` immediately — don't hold full article content in memory
- After publishing each article, you only need to remember the title and result URL
- If you feel context is getting long (10+ articles), wrap up the current batch and ask the user if they want to continue in a new session

---

## Command: Update Profile

Use when the user wants to view or update their profile (name, bio, podcast RSS, etc.).

### Step 1: Load API token

```bash
source .env.local
```

### Step 2: View current profile (optional)

```bash
curl -s "https://elsewhere.news/api/profile" \
  -H "Authorization: Bearer $ELSEWHERE_API_TOKEN" | python3 -m json.tool
```

### Step 3: Update profile

Only include the fields the user wants to change:

```bash
curl -s -X PATCH "https://elsewhere.news/api/profile" \
  -H "Authorization: Bearer $ELSEWHERE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name_zh": "新名称", "bio_zh": "一句话简介", "podcast_rss_url": "https://..."}' | python3 -m json.tool
```

Available fields:
- `name_zh` — display name
- `bio_zh` — short bio (max 100 characters)
- `podcast_rss_url` — podcast RSS URL (小宇宙, Apple Podcasts, etc.)

### Step 4: Sync content (if RSS was set)

If the user set `podcast_rss_url`, trigger podcast sync:

```bash
curl -s -X POST "https://elsewhere.news/api/sync/podcasts" \
  -H "Authorization: Bearer $ELSEWHERE_API_TOKEN" | python3 -m json.tool
```

### Step 5: Confirm

Tell the user what was updated, and how many podcasts were synced (if applicable).

Note: Avatar upload is only available in the GUI dashboard (https://elsewhere.news/dashboard/login).

---

## Important Notes

- **Keep communication minimal.** During import/publish, don't narrate each step. Only speak up for errors or the final one-line result. No summaries, no "I'm now doing X", no rephrasing what the API returned.
- Registration links expire in 24 hours; each invite code is single-use
- Articles are published directly (no draft step)
- Always include `title_en` and `excerpt_en` (translate yourself). Never include `body_en` — body translation is handled automatically after publishing
- Always write JSON to temp file and use `curl -d @file` to avoid shell escaping issues
- After registration, human can log into GUI dashboard at `https://elsewhere.news/dashboard/login`
- The API token never expires. If compromised, the human can regenerate it from the dashboard.
