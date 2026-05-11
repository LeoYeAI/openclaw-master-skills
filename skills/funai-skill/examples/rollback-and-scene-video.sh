#!/bin/bash

set -euo pipefail

if [ -z "${BASH_VERSION:-}" ]; then
  echo "错误: examples/rollback-and-scene-video.sh 需要使用 bash 运行。" >&2
  echo "正确示例: bash examples/rollback-and-scene-video.sh <project_id>" >&2
  return 1 2>/dev/null || exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../scripts/api-client.sh"

PROJECT_ID="${1:-}"
CHAPTER_NUM="${2:-1}"
SCENE_INDEX="${3:-0}"
CONFIRM_CONSUME="${CONFIRM_CONSUME:-}"
AUTO_CONFIRM="${AUTO_CONFIRM:-}"

if [ -z "$PROJECT_ID" ]; then
  printf '用法: %s <project_id> [chapter_num] [scene_index]\n' "$0" >&2
  printf '执行真实图转视频会消耗梦想值。若确认执行，请使用: CONFIRM_CONSUME=YES %s <project_id>\n' "$0" >&2
  exit 1
fi

require_jq
require_setup_ready
load_config
check_auth

printf '说明：本脚本会先做 setup/version 前置检查；默认仅做 dry-run，不会直接消耗梦想值。\n'

project_json=$(ensure_chapter_scenes_step "$PROJECT_ID" "$CHAPTER_NUM")
preset_resource_id=$(printf '%s' "$project_json" | jq -r '.data.presetResourceId')
wait_for_preset_chapter_status "$preset_resource_id" "$CHAPTER_NUM" "sceneTaskStatus" "SUCCESS" 120 3 >/dev/null

storyboard_id=$(resolve_storyboard_id "$preset_resource_id" "$CHAPTER_NUM")
scene_json=$(get_storyboard_scene "$storyboard_id" "$SCENE_INDEX")
scene_id=$(printf '%s' "$scene_json" | jq -r '.id')
payload=$(build_scene_video_payload "$scene_id" "-1" "720p" "")
scene_name=$(printf '%s' "$scene_json" | jq -r '.scene.scene_name // "未命名场景"')
scene_desc=$(printf '%s' "$scene_json" | jq -r '.scene.scene_description // .content // "暂无描述"')
scene_image=$(printf '%s' "$scene_json" | jq -r '.image // "暂无分镜图"')

printf '项目ID: %s\n' "$PROJECT_ID"
printf '章节: %s\n' "$CHAPTER_NUM"
printf 'Storyboard ID: %s\n' "$storyboard_id"
printf 'Scene ID: %s\n' "$scene_id"
printf '项目链接: %s\n' "$(project_link "$PROJECT_ID")"
printf '场景名称: %s\n' "$scene_name"
printf '场景描述: %s\n' "$scene_desc"
printf '当前分镜图: %s\n' "$scene_image"
printf '\n当前分镜图已准备完成。下一步有两种选择：\n'
printf '  1) 将这张分镜图继续转为视频（会消耗梦想值）\n'
printf '  2) 不转视频，直接回到项目页面继续走成片合成\n'
printf '\n本脚本仅负责图转视频路径；如果你要直接成片，请停止脚本并回到项目页面或成片流程。\n'
printf '\n将使用以下 payload 发起单场景图转视频：\n'
printf '%s\n' "$payload" | jq '.'

if [ "$CONFIRM_CONSUME" != "YES" ]; then
  printf '\n未设置 CONFIRM_CONSUME=YES，当前保持在 dry-run。\n' >&2
  printf '若你决定继续转视频，请重新执行：\n' >&2
  printf '  CONFIRM_CONSUME=YES bash %s %s %s %s\n' "$0" "$PROJECT_ID" "$CHAPTER_NUM" "$SCENE_INDEX" >&2
  printf '若你决定直接成片，请不要继续这个脚本，改走成片流程。\n' >&2
  exit 0
fi

if [ "$AUTO_CONFIRM" = "YES" ]; then
  printf '\nAUTO_CONFIRM=YES，自动按“继续转视频”路径执行。\n' >&2
fi

current_prompt=$(printf '%s' "$payload" | jq -r '.prompt // empty')
current_camera_prompt=$(printf '%s' "$payload" | jq -r '.cameraPrompt // empty')
video_result=$(refine_scene_video "$PROJECT_ID" "$scene_id" "$current_prompt" "$current_camera_prompt" "$CHAPTER_NUM" "-1" "720p" "")
task_id=$(printf '%s' "$video_result" | jq -r '.taskId // empty')
printf '\n图转视频任务已提交，taskId: %s\n' "$task_id"
printf '%s\n' "$video_result" | jq '.'
printf '对外返回 videoPlayUrl: %s\n' "$(printf '%s' "$video_result" | jq -r '.videoPlayUrl // empty')"
