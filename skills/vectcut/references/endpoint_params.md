# Endpoint Params

本文件作为总索引，不再承载完整端点细节。

## 按能力域拆分
- `endpoints/filter.md`：滤镜相关端点（add_filter/modify_filter/remove_filter）
- `endpoints/effect.md`：特效相关端点（add_effect/modify_effect/remove_effect）
- `endpoints/material.md`：素材感知端点（get_duration/get_resolution/video_detail）
- `endpoints/draft.md`：草稿管理端点（create_draft/modify_draft/remove_draft/query_script）
- `endpoints/asr.md`：语音识别端点（asr_basic/asr_nlp/asr_llm）
- `endpoints/generate_video.md`：云渲染端点（generate_video/task_status）
- `endpoints/generate_speech.md`：语音合成端点（generate_speech/fish_clone/voice_assets）
- `endpoints/generate_ai_image.md`：AI 图片生成端点（generate_image）
- `endpoints/generate_ai_video.md`：AI 视频生成端点（generate_ai_video/ai_video_task_status）
- `endpoints/digital_human.md`：数字人端点（create_digital_human/digital_human_task_status）
- `endpoints/video.md`：视频端点（add_video/modify_video/remove_video）
- `endpoints/image.md`：图片端点（add_image/modify_image/remove_image）
- `endpoints/text.md`：文本端点（add_text/modify_text/remove_text）
- `endpoints/keyframe.md`：关键帧端点（add_video_keyframe）
- `endpoints/process.md`：预处理端点（extract_audio/split_video）

## 枚举文件
- `enums/filter_types.json`：`filter_type` 可选值
- `enums/character_effect_types.json`：`effect_category` 为 `character` 时的 `effect_type` 可选值
- `enums/scene_effect_types.json`：`effect_category` 为 `scene` 时的 `effect_type` 可选值
- `enums/minimax_voiceids.json`：`provider=minimax` 的 `voice_id` 可选值
- `enums/azure_voiceids.json`：`provider=azure` 的 `voice_id` 可选值
- `enums/volc_voiceids.json`：`provider=volc` 的 `voice_id` 可选值
- `enums/fish_voiceids.json`：`provider=fish` 的 `voice_id` 可选值
- `enums/font_types.json`：`add_text.font` 可选值
- `enums/text_intro_anims.json`：`add_text.intro_animation` 可选值
- `enums/text_outro_anims.json`：`add_text.outro_animation` 可选值
- `enums/text_loop_anims.json`：`add_text.loop_animation` 可选值

## Query Script 输出解析
- `query_script` 的 `output` 为草稿结构体解析入口。
- 结构解读文档：`draft_query_notes.md`（建议与 `endpoints/draft.md` 配套阅读）。
- 样例数据：`draft_info.json`（用于字段对照与校验规则落地）。

## ASR 输出解析
- `asr_basic`：重点解析 `result.raw.result.utterances`，结构说明见 `asr_basic_notes.md`。
- `asr_nlp`：重点解析 `segments`（含 `phrase/words`），结构说明见 `asr_nlp_notes.md`。
- `asr_llm`：重点解析 `segments`（含 `keywords/en/words`），结构说明见 `asr_llm_notes.md`。

## 维护规则
- 新端点优先写入对应能力域文件。
- 涉及复杂返回结构的端点，需在 `references/` 增加专用解读文档并在本文件登记入口。
- 本文件仅维护目录结构与跳转入口。
