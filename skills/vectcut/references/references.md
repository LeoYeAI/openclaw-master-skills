# References Index

## Endpoint Docs
- `endpoint_params.md`：端点总索引
- `endpoints/filter.md`：滤镜端点明细
- `endpoints/effect.md`：特效端点明细
- `endpoints/material.md`：素材感知端点明细（get_duration/get_resolution/video_detail）
- `endpoints/draft.md`：草稿管理端点明细（create_draft/modify_draft/remove_draft/query_script）
- `endpoints/asr.md`：语音识别端点明细（asr_basic/asr_nlp/asr_llm）
- `endpoints/generate_video.md`：云渲染端点明细（generate_video/task_status）
- `endpoints/generate_speech.md`：语音合成端点明细（generate_speech/fish_clone/voice_assets）
- `endpoints/generate_ai_image.md`：AI 图片生成端点明细（generate_image）
- `endpoints/generate_ai_video.md`：AI 视频生成端点明细（generate_ai_video/ai_video_task_status）
- `endpoints/digital_human.md`：数字人端点明细（create_digital_human/digital_human_task_status）
- `endpoints/video.md`：视频端点明细（add_video/modify_video/remove_video）
- `endpoints/image.md`：图片端点明细（add_image/modify_image/remove_image）
- `endpoints/text.md`：文本端点明细（add_text/modify_text/remove_text）
- `endpoints/keyframe.md`：关键帧端点明细（add_video_keyframe）
- `endpoints/process.md`：预处理端点明细（extract_audio/split_video）

## Enums
- `enums/filter_types.json`：滤镜枚举
- `enums/character_effect_types.json`：人物特效枚举
- `enums/scene_effect_types.json`：场景特效枚举
- `enums/minimax_voiceids.json`：Minimax 音色枚举
- `enums/azure_voiceids.json`：Azure 音色枚举
- `enums/volc_voiceids.json`：Volc 音色枚举
- `enums/fish_voiceids.json`：Fish 音色枚举
- `enums/font_types.json`：字体枚举
- `enums/text_intro_anims.json`：文字入场动画枚举
- `enums/text_outro_anims.json`：文字出场动画枚举
- `enums/text_loop_anims.json`：文字循环动画枚举

## Draft Query 解析
- `draft_query_notes.md`：`query_script` 返回 `output` 的结构解读（总体配置、materials、ID 关联、轨道、关键帧）
- `draft_info.json`：真实样例草稿结构（用于对照字段）

## ASR 回包解析
- `asr_basic.json`：asr_basic 真实样例
- `asr_nlp.json`：asr_nlp 真实样例
- `asr_llm.json`：asr_llm 真实样例
- `asr_basic_notes.md`：asr_basic 回包结构解读
- `asr_nlp_notes.md`：asr_nlp 回包结构解读
- `asr_llm_notes.md`：asr_llm 回包结构解读


## 约定
- 明细写在 `endpoints/`，总览写在 `endpoint_params.md`。
- 枚举统一放在 `enums/`，端点文档只做引用。
