#!/bin/bash

set -euo pipefail

if [ -z "${BASH_VERSION:-}" ]; then
  echo "错误: examples/modify-role-image.sh 需要使用 bash 运行。" >&2
  echo "正确示例: bash examples/modify-role-image.sh \"修改后的角色形象描述\" [角色名]" >&2
  return 1 2>/dev/null || exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../scripts/api-client.sh"

MODIFY_PROMPT="${1:-测试修改角色形象：更利落的短发，更强的电影感，更克制的表情。}"
TARGET_ROLE_NAME="${2:-}"

NOVEL_CONTENT='清晨，城市公园的林荫道上还带着尚未散尽的薄雾，年轻人林舟沿着青石板路缓缓慢跑。阳光穿过高大的树冠，在路面上投下细碎而温暖的光影，周围的一切都显得安静而清新。

他刚想加快脚步，一只金毛犬忽然从花坛边的灌木后窜了出来，几乎撞上他的膝盖。林舟下意识停住脚步，呼吸一乱，目光顺着牵引绳的方向望去。

不远处，一个扎着马尾的女孩正快步跑来。她一边努力稳住手里的牵引绳，一边朝林舟露出有些抱歉的笑意。清晨原本平稳的节奏，就这样被一场意外的相遇轻轻打断。'

print_section() {
  local title="$1"
  echo ""
  echo -e "${GREEN}=== ${title} ===${NC}"
}

print_section "0. 检查 setup / 认证"
require_jq
require_setup_ready
load_config
check_auth

print_section "1. 创建测试项目并推进到角色与配音步骤"
options=$(get_select_options 1)
aspect=$(pick_default_option "$options" '.data.ratios')
img_gen_type=$(pick_default_option "$options" '.data.generateTypes')
model=$(pick_default_option "$options" '.data.models')
video_model=$(pick_default_option "$options" '.data.videoModels')
style=$(pick_default_option "$options" '.data.styles')
script_type=$(printf '%s' "$options" | jq -r '(.data.scriptTypes // []) | (map(select(.isDefault == true))[0] // .[0] // {value:"0"}).value')

project_name="改角色形象自检-$(date +%s)"
project_result=$(create_project "$project_name" "$aspect" "$img_gen_type" "$model" "$video_model" "$style" "$script_type")
project_id=$(printf '%s' "$project_result" | jq -r '.data.id')
project_detail=$(get_project "$project_id")
preset_resource_id=$(printf '%s' "$project_detail" | jq -r '.data.presetResourceId')
echo "项目ID: $project_id"
echo "项目链接: $(project_link "$project_id")"

submit_result=$(submit_novel "$project_id" "$NOVEL_CONTENT" "$script_type" "0")
submit_task_id=$(extract_task_id "$submit_result")
poll_task "$submit_task_id" 120 3 >/dev/null

novel_opt_result=$(next_step "$project_id" "novel_opt")
novel_opt_task_id=$(extract_task_id "$novel_opt_result")
poll_task "$novel_opt_task_id" 120 3 >/dev/null

roles_json=$(wait_for_roles_ready "$preset_resource_id" 120 3)

if [ -n "$TARGET_ROLE_NAME" ]; then
  role_ref="$TARGET_ROLE_NAME"
else
  role_ref=$(printf '%s' "$roles_json" | jq -r '.data.roles[0].realName // empty')
fi

target_role_json=$(get_role_from_roles "$roles_json" "$role_ref")
echo "目标角色: $(printf '%s' "$target_role_json" | jq -r '.realName')"
echo "修改前图片: $(printf '%s' "$target_role_json" | jq -r '.imgUrl')"
echo "修改提示词: $MODIFY_PROMPT"

print_section "2. 执行角色形象修改"
modify_result=$(modify_role_image "$project_id" "$role_ref" "$MODIFY_PROMPT")
printf '%s\n' "$modify_result" | jq '.'

print_section "3. 修改结果"
echo "项目链接: $(project_link "$project_id")"
echo "角色名称: $(printf '%s' "$modify_result" | jq -r '.roleName')"
echo "新图资源ID: $(printf '%s' "$modify_result" | jq -r '.selectedImageResourceId')"
echo "新图URL: $(printf '%s' "$modify_result" | jq -r '.selectedImageUrl')"
echo "当前角色描述: $(printf '%s' "$modify_result" | jq -r '.appearance')"
echo "说明：角色形象修改只在角色与配音步骤执行；新图必须生成完成并被 apply 后，才算修改完成。"
