# Eval: blog-url-collection (WITHOUT skill)

## 执行计划摘要
- 工具：web_fetch → write → read/edit
- 路径：workspace/collections/2026-03-09-paul-graham-writes.md
- 格式：Markdown，带简单元数据头（非 YAML frontmatter）
- 提取：标题、全文、URL、时间、标签、用户备注
- 索引：有，index.md 表格形式

## Assertion 评分

| ID | Assertion | Pass | Evidence |
|---|---|---|---|
| correct-directory | 文件保存到 collections/articles/ | ❌ | 放在 collections/ 根目录，没有 articles/ 子分类 |
| yaml-frontmatter | 完整 YAML frontmatter | ❌ | 用 markdown 列表，不是 YAML frontmatter |
| content-extraction | 提取核心观点(≥3个) | ❌ | 只提取全文，没有核心观点/要点摘录结构 |
| index-update | 更新 index.md | ✅ | 有 index.md 表格 |
| tags-reasonable | 标签合理且包含写作相关 | ✅ | #写作 #Paul-Graham |
| supadata-or-fetch | 使用 supadata 或 web_fetch | ✅ | 用了 web_fetch（但不知道 supadata） |

**Pass rate: 3/6 (50%)**
