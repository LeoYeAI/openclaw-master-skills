## scripts/

这里放“本地命令行辅助内容”，用于快速调用 VectCut 的 HTTP API。

推荐用法：

```bash
export VECTCUT_BASE_URL="http://open.vectcut.com/cut_jianying"

curl -X POST "$VECTCUT_BASE_URL/create_draft" \
  -H "Authorization: Bearer $VECTCUT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"demo"}'

curl -X GET "$VECTCUT_BASE_URL/get_transition_types" \
  -H "Authorization: Bearer $VECTCUT_API_KEY"
```

示例请求体可以参考：

- `assets/requests/create_draft_examples.json5`
- `assets/requests/add_audio_examples.json5`
- `assets/requests/add_text_and_image_examples.json5`
- `assets/requests/add_video_examples.json5`
- `assets/requests/add_subtitle_examples.json5`
- `assets/requests/add_video_keyframe_examples.json5`
- `assets/requests/add_sticker_examples.json5`
- `assets/requests/add_effect_examples.json5`
- `assets/requests/add_filter_examples.json5`
- `assets/requests/add_text_template_examples.json5`
- `assets/requests/generate_image_examples.json5`
- `assets/requests/generate_ai_video_examples.json5`
- `assets/requests/generate_speech_examples.json5`
- `assets/requests/remove_bg_examples.json5`
- `assets/requests/search_sticker_examples.json5`
- `assets/requests/get_audio_effect_types_examples.json5`
- `assets/requests/get_video_effect_types_examples.json5`
- `assets/requests/get_filter_types_examples.json5`
- `assets/requests/get_duration_examples.json5`
