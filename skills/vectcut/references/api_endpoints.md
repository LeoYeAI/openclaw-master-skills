## VectCut 主要端点与鉴权

基础信息：

- Base URL: `http://open.vectcut.com/cut_jianying`
- 统一鉴权：`Authorization: Bearer $VECTCUT_API_KEY`

如需查看每个端点的入参、字段含义与默认值，请参考同目录下的：

- `endpoint_params.md`

核心端点分组：

- 草稿：
  - `POST /create_draft`
  - `POST /query_script`
  - `POST /generate_draft_url`
  - `POST /copy_draft`
- 媒体与时间线：
  - `POST /add_video`
  - `POST /add_image`
  - `POST /add_audio`
  - `POST /add_text`
  - `POST /add_subtitle`
  - `POST /add_sticker`
  - `POST /add_preset`
  - `POST /add_effect`
  - `POST /add_filter`
  - `POST /add_video_keyframe`
- 高级能力：
  - `POST /generate_image`
  - `POST /generate_ai_video`
  - `POST /generate_speech`
  - `POST /remove_bg`
- 渲染：
  - `POST /generate_video`
  - `POST /task_status`
- 枚举与工具：
  - `GET /get_transition_types`
  - `GET /get_mask_types`
  - `GET /get_intro_animation_types`
  - `GET /get_outro_animation_types`
  - `GET /get_combo_animation_types`
  - `GET /get_text_intro_types`
  - `GET /get_text_outro_types`
  - `GET /get_text_loop_anim_types`
  - `GET /get_video_scene_effect_types`
  - `GET /get_video_character_effect_types`
  - `GET /get_filter_types`
  - `GET /get_font_types`
  - `GET /get_audio_effect_types`
  - `POST /get_duration`
  - `POST /search_sticker`
