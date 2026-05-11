#!/bin/bash

set -euo pipefail

if [ -z "${BASH_VERSION:-}" ]; then
  echo "错误: examples/batch-scene-review.sh 需要使用 bash 运行。" >&2
  echo "示例: bash examples/batch-scene-review.sh <project_id> <output_dir> [chapter_num]" >&2
  return 1 2>/dev/null || exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../scripts/api-client.sh"

PROJECT_ID="${1:-}"
OUTPUT_DIR="${2:-}"
CHAPTER_NUM="${3:-1}"

if [ -z "$PROJECT_ID" ] || [ -z "$OUTPUT_DIR" ]; then
  echo "用法: $0 <project_id> <output_dir> [chapter_num]" >&2
  exit 1
fi

require_jq
require_setup_ready
load_config
check_auth

project_json=$(get_project "$PROJECT_ID")
preset_resource_id=$(printf '%s' "$project_json" | jq -r '.data.presetResourceId')
storyboard_id=$(resolve_storyboard_id "$preset_resource_id" "$CHAPTER_NUM")

printf '项目ID: %s\n' "$PROJECT_ID"
printf '项目链接: %s\n' "$(project_link "$PROJECT_ID")"
printf 'Storyboard ID: %s\n' "$storyboard_id"

printf '\n=== Scene 摘要 ===\n'
build_storyboard_scene_summaries "$storyboard_id" | jq '.'

printf '\n=== Prompt / Detail 摘要 ===\n'
build_scene_review_manifest "$storyboard_id" | jq '[.[] | {sceneIndex, sceneId, sceneName, imagePromptInfo, videoPromptInfo}]'

printf '\n=== 下载代表图到本地 ===\n'
download_storyboard_scene_images "$storyboard_id" "$OUTPUT_DIR" | jq '[.[] | {sceneIndex, sceneId, sceneName, downloadedImagePath, imageUrl: (.selectedImage.url // .storyboardImage)}]'

printf '\n建议：现在可以把这些本地图片交给具备多模态能力的模型先审图，再决定批量修改哪些 scene。\n'
