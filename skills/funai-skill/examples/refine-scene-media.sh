#!/bin/bash

set -euo pipefail

if [ -z "${BASH_VERSION:-}" ]; then
  echo "错误: examples/refine-scene-media.sh 需要使用 bash 运行。" >&2
  echo "示例: bash examples/refine-scene-media.sh <project_id> image \"新的sceneDescription\" \"新的prompt\"" >&2
  echo "示例: bash examples/refine-scene-media.sh <project_id> video \"新的动作\" \"新的运镜\"" >&2
  return 1 2>/dev/null || exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../scripts/api-client.sh"

PROJECT_ID="${1:-}"
MODE="${2:-}"
TEXT_A="${3:-}"
TEXT_B="${4:-}"
CHAPTER_NUM="${5:-1}"
SCENE_INDEX="${6:-0}"

if [ -z "$PROJECT_ID" ] || [ -z "$MODE" ] || [ -z "$TEXT_A" ] || [ -z "$TEXT_B" ]; then
  echo "用法: $0 <project_id> <image|video> <textA> <textB> [chapter_num] [scene_index]" >&2
  echo "  image 模式: textA=新的 sceneDescription, textB=新的 prompt" >&2
  echo "  video 模式: textA=新的动作 prompt, textB=新的运镜 cameraPrompt" >&2
  exit 1
fi

require_jq
require_setup_ready
load_config
check_auth

project_json=$(ensure_chapter_scenes_step "$PROJECT_ID" "$CHAPTER_NUM")
preset_resource_id=$(printf '%s' "$project_json" | jq -r '.data.presetResourceId')
wait_for_preset_chapter_status "$preset_resource_id" "$CHAPTER_NUM" "sceneTaskStatus" "SUCCESS" 120 3 >/dev/null
storyboard_id=$(resolve_storyboard_id "$preset_resource_id" "$CHAPTER_NUM")
scene_json=$(get_storyboard_scene "$storyboard_id" "$SCENE_INDEX")
scene_id=$(printf '%s' "$scene_json" | jq -r '.id')
prompt_detail=$(get_scene_prompt_detail "$scene_id")

printf '项目ID: %s\n' "$PROJECT_ID"
printf '项目链接: %s\n' "$(project_link "$PROJECT_ID")"
printf 'Storyboard ID: %s\n' "$storyboard_id"
printf 'Scene ID: %s\n' "$scene_id"
printf '场景名称: %s\n' "$(printf '%s' "$scene_json" | jq -r '.scene.scene_name // "未命名场景"')"
printf '当前分镜图: %s\n' "$(printf '%s' "$scene_json" | jq -r '.image // "暂无分镜图"')"
printf '\n当前 prompt/detail:\n'
printf '%s\n' "$prompt_detail" | jq '{image: .data.image.imagePromptInfo, video: ((.data.video // {}) | del(.url))}'

case "$MODE" in
  image)
    printf '\n开始重生图...\n'
    result=$(refine_scene_image "$PROJECT_ID" "$scene_id" "$TEXT_A" "$TEXT_B" "$CHAPTER_NUM")
    ;;
  video)
    printf '\n开始图转视频...\n'
    result=$(refine_scene_video "$PROJECT_ID" "$scene_id" "$TEXT_A" "$TEXT_B" "$CHAPTER_NUM" "-1" "720p" "")
    ;;
  *)
    echo "错误: mode 只能是 image 或 video" >&2
    exit 1
    ;;
esac

printf '\n结果:\n'
printf '%s\n' "$result" | jq '.'

if [ "$MODE" = "video" ]; then
  printf '对外返回 videoPlayUrl: %s\n' "$(printf '%s' "$result" | jq -r '.videoPlayUrl // empty')"
fi
