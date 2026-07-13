# Eval: blog-url-collection (WITH skill)

## 执行计划摘要
- 工具：supadata_fetch.py（优先）→ web_fetch（降级）
- 路径：collections/articles/2026-03-09-paul-graham-writes.md
- 格式：Markdown + 完整 YAML frontmatter
- 提取：标题、作者、日期、标签、摘要、核心观点(3-7个)、要点摘录(blockquote)、我的笔记、原文摘要
- 索引：index.md（按月份倒序）+ tags.md（按标签聚合）
- 额外：关联项目自动匹配（读 projects.md），用户情感保留到"我的笔记"

## Assertion 评分

| ID | Assertion | Pass | Evidence |
|---|---|---|---|
| correct-directory | 文件保存到 collections/articles/ | ✅ | 明确指定 articles/ 子目录 |
| yaml-frontmatter | 完整 YAML frontmatter | ✅ | 包含 title/source/url/author/tags/category/summary/related_projects |
| content-extraction | 提取核心观点(≥3个) | ✅ | 明确说"3-7个核心观点" |
| index-update | 更新 index.md | ✅ | 详细描述了 index.md 和 tags.md 的更新步骤 |
| tags-reasonable | 标签合理且包含写作相关 | ✅ | [写作, writing, Paul Graham, 思维模型, 创作, AI] |
| supadata-or-fetch | 使用 supadata 或 web_fetch | ✅ | 优先 supadata，降级 web_fetch |

**Pass rate: 6/6 (100%)**
