#!/bin/bash

set -euo pipefail

if [ -z "${BASH_VERSION:-}" ]; then
  echo "错误: examples/create-comic.sh 需要使用 bash 运行。" >&2
  echo "正确示例: bash examples/create-comic.sh" >&2
  return 1 2>/dev/null || exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../scripts/api-client.sh"

AUTO_CONFIRM="${AUTO_CONFIRM:-}"

NOVEL_CONTENT='清晨，城市公园的林荫道上还带着尚未散尽的薄雾，年轻人林舟沿着青石板路缓缓慢跑。阳光穿过高大的树冠，在路面上投下细碎而温暖的光影，周围的一切都显得安静而清新。

他刚想加快脚步，一只金毛犬忽然从花坛边的灌木后窜了出来，几乎撞上他的膝盖。林舟下意识停住脚步，呼吸一乱，目光顺着牵引绳的方向望去。

不远处，一个扎着马尾的女孩正快步跑来。她一边努力稳住手里的牵引绳，一边朝林舟露出有些抱歉的笑意。清晨原本平稳的节奏，就这样被一场意外的相遇轻轻打断。'

print_section() {
  local title="$1"
  echo ""
  echo -e "${GREEN}=== ${title} ===${NC}"
}

confirm_or_exit() {
  local checkpoint_name="$1"
  local modify_hint="$2"
  local answer

  echo ""
  echo -e "${YELLOW}--- ${checkpoint_name}确认 ---${NC}"
  echo "$modify_hint"

  if [ "$AUTO_CONFIRM" = "YES" ]; then
    echo "AUTO_CONFIRM=YES，自动确认继续。"
    return 0
  fi

  read -r -p "是否确认继续下一步？输入 yes 继续，其它任意输入将停止脚本: " answer
  case "$answer" in
    yes|YES|y|Y)
      echo "已确认，继续下一步。"
      ;;
    *)
      echo "已按用户确认点停止。请根据当前结果修改后重新运行脚本或在项目页面继续处理。"
      exit 0
      ;;
  esac
}

show_novel_checkpoint() {
  local project_id="$1"

  print_section "小说 / 剧本确认"
  echo "项目链接: $(project_link "$project_id")"
  echo "以下是本次自检已提交并写入项目的剧本内容："
  echo "注意：这是 automation/self-check 脚本。为了验证整条链路，本脚本会先提交再展示确认；真实面向用户的 Agent 流程仍应先展示并等待用户确认，再提交或继续。"
  echo "----------------------------------------"
  printf '%s\n' "$NOVEL_CONTENT"
  echo "----------------------------------------"
  confirm_or_exit "小说 / 剧本" "如需修改，请先调整剧本内容后重新运行；确认无误后再继续角色与分镜流程。"
}

show_roles_checkpoint() {
  local project_id="$1"
  local roles_json="$2"

  print_section "角色确认"
  echo "项目链接: $(project_link "$project_id")"
  echo "以下是当前角色形象结果。当前已支持在“角色与配音”步骤修改角色形象；但本自检脚本默认不自动修改。"
  echo "如果你要测试改角色形象，请在这一步停止，并改用 examples/modify-role-image.sh 或 source 后调用 modify_role_image。"
  echo "----------------------------------------"
  printf '%s\n' "$roles_json" | jq -r '
    .data.roles[]?
    | "角色名: \(.realName // "未命名角色")\n角色图片: \(.imgUrl // "暂无图片")\n状态: \(.taskStatus // "UNKNOWN")\n----------------------------------------"
  '
  confirm_or_exit "角色" "如需修改角色形象，请停留在本步骤执行修改；确认无误后再继续进入场景 / 分镜步骤。"
}

choose_storyboard_next_action() {
  local project_id="$1"
  local storyboard_json="$2"
  local answer

  print_section "场景 / 分镜确认" >&2
  echo "项目链接: $(project_link "$project_id")" >&2
  echo "以下是当前场景 / 分镜结果。分镜图已生成完成，请确认下一步要走哪条路径：" >&2
  echo "----------------------------------------" >&2
  printf '%s\n' "$storyboard_json" | jq -r '
    .data.data.scenes[]?
    | "场景编号: \(.scene.scene_id // "未编号")\n场景名称: \(.scene.scene_name // "未命名场景")\n场景描述: \(.scene.scene_description // .content // "暂无描述")\n分镜图: \(.image // "暂无分镜图")\n当前资源类型: \(.displayType // "unknown")\n----------------------------------------"
  ' >&2

  if [ "$AUTO_CONFIRM" = "YES" ]; then
    echo "AUTO_CONFIRM=YES，默认选择直接进入成片合成。" >&2
    printf 'compose\n'
    return 0
  fi

  echo "请选择下一步：" >&2
  echo "  1) 将分镜图继续转为视频" >&2
  echo "  2) 直接进入成片界面合成" >&2
  echo "  其它任意输入) 停止脚本，等待后续决定" >&2
  read -r -p "请输入 1 或 2: " answer

  case "$answer" in
    1)
      printf 'video\n'
      ;;
    2)
      printf 'compose\n'
      ;;
    *)
      printf 'stop\n'
      ;;
  esac
}

print_section "0. 检查 setup / 版本前置条件"
require_jq
require_setup_ready

print_section "0. 检查依赖与认证"
load_config
check_auth
echo -e "${GREEN}Token 有效，可开始自检${NC}"

echo "说明：examples/create-comic.sh 是自检/自动化脚本，不是面向真实用户交互的话术模板。"

print_section "1. 获取创建项目可选项"
options=$(get_select_options 1)
aspect=$(pick_default_option "$options" '.data.ratios')
img_gen_type=$(pick_default_option "$options" '.data.generateTypes')
model=$(pick_default_option "$options" '.data.models')
video_model=$(pick_default_option "$options" '.data.videoModels')
style=$(pick_default_option "$options" '.data.styles')
script_type=$(printf '%s' "$options" | jq -r '(.data.scriptTypes // []) | (map(select(.isDefault == true))[0] // .[0] // {value:"0"}).value')
echo "注意：本脚本是自检脚本，因此会使用 select-options 返回的实时默认值自动填充比例、风格、模型和剧本模式。"
echo "在真实用户交互中，aspect（画面比例）和 style（风格）必须先让用户明确选择，不能这样静默默认。"
echo "默认比例: $aspect"
echo "默认生图类型: $img_gen_type"
echo "默认生图模型: $model"
echo "默认视频模型: $video_model"
echo "默认风格: $style"
echo "默认剧本类型: $script_type"

print_section "2. 创建项目"
project_name="自检项目-$(date +%s)"
project_result=$(create_project "$project_name" "$aspect" "$img_gen_type" "$model" "$video_model" "$style" "$script_type")
project_id=$(printf '%s' "$project_result" | jq -r '.data.id')
project_detail=$(get_project "$project_id")
preset_resource_id=$(printf '%s' "$project_detail" | jq -r '.data.presetResourceId')
current_step=$(printf '%s' "$project_detail" | jq -r '.data.workflow.currentStep')
echo "项目ID: $project_id"
echo "当前步骤: $current_step"
echo "项目链接: $(project_link "$project_id")"

print_section "3. 提交剧本"
submit_result=$(submit_novel "$project_id" "$NOVEL_CONTENT" "$script_type" "0")
submit_task_id=$(extract_task_id "$submit_result")
echo "提交任务ID: $submit_task_id"
submit_poll=$(poll_task "$submit_task_id" 120 3)
submit_resource_id=$(printf '%s' "$submit_poll" | jq -r '.data.resourceId')
echo "剧本资源ID: $submit_resource_id"
show_novel_checkpoint "$project_id"

print_section "4. 智能分集"
novel_opt_result=$(next_step "$project_id" "novel_opt")
novel_opt_task_id=$(extract_task_id "$novel_opt_result")
echo "智能分集任务ID: $novel_opt_task_id"
poll_task "$novel_opt_task_id" 120 3 >/dev/null

print_section "5. 等待角色图完成并执行角色步骤"
roles_json=$(wait_for_roles_ready "$preset_resource_id" 120 3)
show_roles_checkpoint "$project_id" "$roles_json"
extract_roles_inputs=$(build_extract_roles_inputs "$preset_resource_id" 1)
extract_roles_result=$(next_step "$project_id" "novel_extract_roles" "$extract_roles_inputs")
printf '%s\n' "$extract_roles_result" | jq '.'

print_section "6. 等待 sceneCaptionsTaskStatus，再执行智能分镜"
wait_for_preset_chapter_status "$preset_resource_id" 1 "sceneCaptionsTaskStatus" "SUCCESS" 120 3 >/dev/null
scene_caption_result=$(next_step "$project_id" "novel_scene_captions" '[{"type":"number","name":"chapterNum","value":1},{"name":"imgGenTypeRef","value":1}]')
dialog_task_id=$(extract_task_id "$scene_caption_result")
echo "智能分镜 dialogTaskId: $dialog_task_id"
poll_task "$dialog_task_id" 160 3 >/dev/null

print_section "7. 等待 sceneTaskStatus，再推进到成片"
wait_for_preset_chapter_status "$preset_resource_id" 1 "sceneTaskStatus" "SUCCESS" 160 3 >/dev/null
chapter_scenes_result=$(next_step "$project_id" "novel_chapter_scenes" '[{"type":"number","name":"chapterNum","value":1}]')
printf '%s\n' "$chapter_scenes_result" | jq '.'

print_section "8. 获取 storyboard 与场景"
storyboard_id=$(resolve_storyboard_id "$preset_resource_id" 1)
storyboard_json=$(get_resource "$storyboard_id")
scene_count=$(printf '%s' "$storyboard_json" | jq '.data.data.scenes | length')
first_scene_id=$(printf '%s' "$storyboard_json" | jq -r '.data.data.scenes[0].id')
echo "storyboardId: $storyboard_id"
echo "scene 数量: $scene_count"
echo "首个 sceneId: $first_scene_id"
next_action=$(choose_storyboard_next_action "$project_id" "$storyboard_json")

case "$next_action" in
  video)
    print_section "9. 检查批量转视频状态（只检查，不执行）"
    batch_check=$(check_batch_ai_video "$storyboard_id")
    printf '%s\n' "$batch_check" | jq '.'
    echo "你已选择“将分镜图转为视频”。本自检脚本默认不自动执行高消耗的批量转视频，请根据需要改用专门的视频生成流程。"
    exit 0
    ;;
  compose)
    ;;
  *)
    echo "已在分镜图确认点停止。请根据当前结果稍后再决定是转视频还是直接成片。"
    exit 0
    ;;
esac

print_section "9. 检查批量转视频状态（只检查，不执行）"
batch_check=$(check_batch_ai_video "$storyboard_id")
printf '%s\n' "$batch_check" | jq '.'

print_section "10. 配置成片并执行合成"
echo "当前进入的是成片设置与视频合成流程。"
echo "注意：进入 novel_chapter_video 只表示进入成片设置阶段，不代表最终成片已经生成。"
echo "只有等视频合成任务成功后，用户才能在项目页面看到最终成片。"
prepare_video_composite "$project_id" 1 >/dev/null
save_video_compose_config_from_project "$project_id" 1 >/dev/null
echo "成片设置已保存（封面 / 字幕 / 背景音乐等）。接下来将真正发起视频合成。"
compose_result=$(compose_video "$project_id" 1 "720p" "1")
compose_task_id=$(extract_task_id "$compose_result")
echo "视频合成任务ID: $compose_task_id"
compose_poll=$(poll_task "$compose_task_id" 240 5)
final_resource_id=$(printf '%s' "$compose_poll" | jq -r '.data.resourceId')
final_video_json=$(get_final_video_resource_info "$final_resource_id")
echo "最终视频资源ID: $final_resource_id"
echo "最终视频可播放链接: $(printf '%s' "$final_video_json" | jq -r '.videoPlayUrl // empty')"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}自检流程执行完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo "项目ID: $project_id"
echo "项目链接: $(project_link "$project_id")"
echo "Storyboard ID: $storyboard_id"
echo "最终视频资源ID: $final_resource_id"
echo "最终视频可播放链接: $(printf '%s' "$final_video_json" | jq -r '.videoPlayUrl // empty')"
echo "说明：如果 videoPlayUrl 非空，当前可以直接把这个链接返回给用户播放最终视频。"
