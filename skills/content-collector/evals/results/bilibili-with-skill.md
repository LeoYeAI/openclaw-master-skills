# Eval: bilibili-video-collection (WITH skill)

## 执行计划摘要
- 工具链：bilibili_extract.py（元数据+评论）→ bilibili_transcribe.sh（转录）→ LLM 提炼
- 路径：collections/videos/2026-03-09-ai-agent-bilibili.md
- 格式：Markdown + 完整 YAML frontmatter（含视频专属字段）
- 内容结构：核心观点 + 要点摘录 + 热门评论精选 + 评论区观点摘要 + 我的笔记 + 原文摘要
- 关键决策："Supadata 不支持 B站" → 直接走本地流程，避免走弯路
- 后置：index.md + tags.md 双索引更新

## Assertion 评分

| ID | Assertion | Pass | Evidence |
|---|---|---|---|
| bilibili-detection | 识别B站链接并使用本地脚本 | ✅ | 明确跳过 Supadata，走本地 bilibili 专用流程 |
| correct-tools | 使用 bilibili_extract.py 和 bilibili_transcribe.sh | ✅ | 4步标准流程，两个脚本都明确提到 |
| video-directory | 文件保存到 collections/videos/ | ✅ | collections/videos/2026-03-09-ai-agent-bilibili.md |
| video-metadata | 包含视频专属字段 | ✅ | duration/platform/bvid/stats 全部包含 |

**Pass rate: 4/4 (100%)**
