# Eval: article-from-topic (WITH skill)

## 执行计划摘要
- 选题澄清：给出3个具体方向让老板选
- 素材采集：收藏库 grep + web_search 3轮 + smart_collect.mjs + web_fetch 2-4篇
- 写作：行业观察模板 2000-3000字，persona.md 人设，第一人称
- 封面：Seedream 5.0 Lite（0.22元/张）→ 裁剪2.35:1 → 质量检查
- 正文配图：2-3张，Seedream/截图 + beautify-screenshot.sh
- 排版：markdown_to_html.py --theme tech --upload
- 推送：publisher.mjs 到草稿箱，不自动发布
- 红线：8条写作红线逐条遵守方案

## Assertion 评分

| ID | Assertion | Pass | Evidence |
|---|---|---|---|
| env-check | 执行环境检查或提到 setup.mjs | ⚠️ 部分 | 没显式提到 setup.mjs，但提到了 smart_collect.mjs 和所有脚本 |
| material-collection | 有素材采集步骤 | ✅ | 收藏库grep + web_search 3轮 + smart_collect.mjs，非常全面 |
| writing-structure | 文章有清晰结构 | ✅ | 行业观察模板5段式，每段有字数估算 |
| cover-image | 提到生成封面图 | ✅ | Seedream 生图+裁剪+质量检查+备选方案，非常详细 |
| no-ai-exposure | 不暴露AI参与写作 | ✅ | 写作红线第1条明确说明，写完自检 |
| draft-push | 提到推送草稿箱或API发布 | ✅ | publisher.mjs 推送草稿箱，明确不自动发布 |

**Pass rate: 5.5/6 (92%)**

## vs Without-skill 关键差异
- WITH：知道所有脚本（seedream-generate.sh/markdown_to_html.py/publisher.mjs/smart_collect.mjs）
- WITHOUT：不知道任何专用脚本，对发布流程不确定
- WITH：8条写作红线逐条遵守方案
- WITHOUT：没意识到"不暴露AI写作"红线
- WITH：封面图完整方案（Seedream→裁剪→质量检查→备选）
- WITHOUT：只说"用图片生成工具"
- WITH：收藏库检索作为素材来源
- WITHOUT：完全不知道收藏库
