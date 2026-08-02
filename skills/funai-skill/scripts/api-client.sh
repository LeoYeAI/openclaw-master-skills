#!/bin/bash

set -euo pipefail

if [ -z "${BASH_VERSION:-}" ]; then
  echo "错误: scripts/api-client.sh 需要在 bash 中运行或被 bash source。" >&2
  echo "正确示例:" >&2
  echo "  bash scripts/api-client.sh check" >&2
  echo "  bash -lc 'source scripts/api-client.sh && require_jq && load_config && create_project_with_defaults \"项目名\"'" >&2
  return 1 2>/dev/null || exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$SKILL_DIR/config/.env"
VERSION_FILE="$SKILL_DIR/VERSION"
BASE_URL="https://ai.fun.tv/service/workflow"
PROJECT_LINK_PREFIX="https://ai.fun.tv/#/comic/multiple?projectId="
SETUP_SKILL_URL="https://neirong.funshion.net/skills/setup-skill.md"

SETUP_STATUS_JSON=""
SETUP_STATUS_EXIT_CODE=""
SETUP_STATUS_PRINTED=""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

require_jq() {
  if ! command -v jq >/dev/null 2>&1; then
    echo -e "${RED}错误: 需要 jq 才能解析 API 响应${NC}" >&2
    echo "请先安装 jq，然后重试。" >&2
    exit 1
  fi
}

require_python3() {
  if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}错误: setup/version 检查需要 python3${NC}" >&2
    echo "请先安装 python3，然后重试。" >&2
    exit 1
  fi
}

load_config() {
  if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}错误: 配置文件不存在${NC}" >&2
    echo "请执行以下步骤：" >&2
    echo "  1. cp $SKILL_DIR/config/.env.example $CONFIG_FILE" >&2
    echo "  2. 编辑 $CONFIG_FILE 填入您的 Token" >&2
    exit 1
  fi

  if python3 - "$CONFIG_FILE" <<'PY'
from pathlib import Path
import re
import sys

text = Path(sys.argv[1]).read_text(encoding='utf-8', errors='ignore')
pattern = re.compile(r'^\s*AIFUN_TOKEN\s*=\s*["\']?[Bb]earer\s+.+$', re.MULTILINE)
raise SystemExit(0 if pattern.search(text) else 1)
PY
  then
    echo -e "${RED}错误: 配置文件里的 AIFUN_TOKEN 不能写成 Bearer 前缀形式${NC}" >&2
    echo "正确写法: AIFUN_TOKEN=eyJ..." >&2
    echo "错误写法: AIFUN_TOKEN=Bearer eyJ..." >&2
    echo "橙星梦工厂接口要求的请求头格式是: authorization: <token>" >&2
    exit 1
  fi

  # shellcheck source=/dev/null
  source "$CONFIG_FILE"

  if [ -z "${AIFUN_TOKEN:-}" ] || [ "$AIFUN_TOKEN" = "your_token_here" ]; then
    echo -e "${RED}错误: 请在配置文件中设置 AIFUN_TOKEN${NC}" >&2
    echo "配置文件路径: $CONFIG_FILE" >&2
    exit 1
  fi

  if [[ "$AIFUN_TOKEN" =~ ^[[:space:]]*[Bb]earer[[:space:]]+ ]]; then
    echo -e "${RED}错误: AIFUN_TOKEN 不能包含 Bearer 前缀${NC}" >&2
    echo "橙星梦工厂接口要求的请求头格式是: authorization: <token>" >&2
    echo "请在 $CONFIG_FILE 中只保留原始 token，本身不要写成 'Bearer xxx'。" >&2
    exit 1
  fi
}

project_link() {
  local project_id="$1"
  echo "${PROJECT_LINK_PREFIX}${project_id}"
}

to_video_play_url() {
  local raw_url="$1"

  if [ -z "$raw_url" ]; then
    printf '\n'
    return 0
  fi

  RAW_VIDEO_URL="$raw_url" python3 - <<'PY'
import os
import urllib.parse

raw = os.environ.get("RAW_VIDEO_URL", "")
if not raw:
    print("")
else:
    print("https://ai.fun.tv/static/videoPreview.html?url=" + urllib.parse.quote(raw, safe=""))
PY
}

normalize_endpoint() {
  local endpoint="$1"

  if [[ "$endpoint" == http* ]]; then
    echo "$endpoint"
  elif [[ "$endpoint" == /service/workflow* ]]; then
    echo "$BASE_URL${endpoint#/service/workflow}"
  elif [[ "$endpoint" == /* ]]; then
    echo "$BASE_URL$endpoint"
  else
    echo "$BASE_URL/$endpoint"
  fi
}

api_request() {
  local method="$1"
  local endpoint="$2"
  local data="${3:-}"
  local response
  local http_code
  local body
  local url

  url="$(normalize_endpoint "$endpoint")"

  if [ "$method" = "GET" ]; then
    response=$(curl -sS -w "\n%{http_code}" \
      "$url" \
      -H "authorization: $AIFUN_TOKEN")
  else
    response=$(curl -sS -w "\n%{http_code}" \
      -X POST "$url" \
      -H "Content-Type: application/json" \
      -H "authorization: $AIFUN_TOKEN" \
      -d "$data")
  fi

  http_code=$(printf '%s\n' "$response" | tail -1)
  body=$(printf '%s\n' "$response" | sed '$d')

  if [ "$http_code" = "401" ]; then
    echo -e "${RED}Token 已过期或无效！${NC}" >&2
    if [[ "$AIFUN_TOKEN" =~ ^[[:space:]]*[Bb]earer[[:space:]]+ ]]; then
      echo "检测到当前 token 带有 Bearer 前缀；橙星梦工厂接口不接受这种格式。" >&2
      echo "请改成原始 token，并使用请求头: authorization: <token>" >&2
    fi
    echo "请访问 https://ai.fun.tv/#/openclaw 重新获取Token" >&2
    echo "然后更新到: $CONFIG_FILE" >&2
    return 1
  fi

  printf '%s\n' "$body"
}

api_request_checked() {
  local method="$1"
  local endpoint="$2"
  local data="${3:-}"
  local body
  local code
  local msg

  body=$(api_request "$method" "$endpoint" "$data") || return 1
  code=$(printf '%s' "$body" | jq -r '.code // empty')

  if [ "$code" != "200" ]; then
    msg=$(printf '%s' "$body" | jq -r '.msg // "未知错误"')
    echo -e "${RED}API 调用失败: ${msg}${NC}" >&2
    printf '%s\n' "$body" | jq '.' >&2 || printf '%s\n' "$body" >&2
    return 1
  fi

  printf '%s\n' "$body"
}

extract_task_id() {
  local body="$1"
  printf '%s' "$body" | jq -r '.data.dialogTaskId // .data.resultId // empty'
}

step_rank() {
  case "$1" in
    novel_input) printf '10\n' ;;
    novel_opt) printf '20\n' ;;
    novel_extract_roles) printf '30\n' ;;
    novel_scene_captions) printf '40\n' ;;
    novel_chapter_scenes) printf '50\n' ;;
    novel_chapter_video) printf '60\n' ;;
    *) printf '0\n' ;;
  esac
}

guard_step_not_already_passed() {
  local project_id="$1"
  local target_step="$2"
  local project_json
  local current_step
  local current_rank
  local target_rank

  project_json=$(get_project "$project_id") || return 1
  current_step=$(printf '%s' "$project_json" | jq -r '.data.workflow.currentStep // empty')

  if [ "$current_step" = "$target_step" ]; then
    printf '%s\n' "$project_json"
    return 0
  fi

  current_rank=$(step_rank "$current_step")
  target_rank=$(step_rank "$target_step")

  if [ "$current_rank" -gt 0 ] && [ "$target_rank" -gt 0 ] && [ "$current_rank" -gt "$target_rank" ]; then
    echo -e "${RED}错误: 当前步骤 ${current_step} 已经过了目标步骤 ${target_step}，不要重复调用 next_step${NC}" >&2
    echo "请先读取当前项目状态，并根据当前步骤继续，而不是重放旧步骤。" >&2
    return 1
  fi

  printf '%s\n' "$project_json"
}

get_task() {
  local task_id="$1"
  api_request_checked GET "/task/$task_id"
}

poll_task() {
  local task_id="$1"
  local max_attempts="${2:-60}"
  local interval="${3:-3}"
  local i
  local result
  local status
  local message

  for i in $(seq 1 "$max_attempts"); do
    result=$(get_task "$task_id") || return 1
    status=$(printf '%s' "$result" | jq -r '.data.status // empty')
    message=$(printf '%s' "$result" | jq -r '.data.message // empty')

    if [ "$status" = "SUCCESS" ]; then
      printf '%s\n' "$result"
      return 0
    fi

    if [ "$status" = "FAILED" ] || [ "$status" = "CANCELED" ]; then
      echo -e "${RED}任务结束: ${status}${NC}" >&2
      printf '%s\n' "$result" | jq '.' >&2
      return 1
    fi

    if [ -n "$message" ]; then
      echo -e "[$i/$max_attempts] 状态: ${YELLOW}${status}${NC} - ${message}" >&2
    else
      echo -e "[$i/$max_attempts] 状态: ${YELLOW}${status}${NC}" >&2
    fi

    sleep "$interval"
  done

  echo -e "${RED}任务超时${NC}" >&2
  return 1
}

check_auth() {
  api_request_checked POST "/project/story/select-options" '{"appCode":"ai-story","generateType":"1"}' >/dev/null
}

load_local_skill_version() {
  local version

  if [ ! -f "$VERSION_FILE" ]; then
    echo -e "${RED}错误: 未找到本地版本文件${NC}" >&2
    echo "请确认以下文件存在并包含当前 Skill 版本: $VERSION_FILE" >&2
    return 1
  fi

  require_python3
  version=$(python3 - "$VERSION_FILE" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8", errors="ignore")
for line in text.splitlines():
    value = line.strip()
    if value and not value.startswith("#"):
        print(value)
        break
else:
    raise SystemExit(1)
PY
)

  if [ -z "$version" ]; then
    echo -e "${RED}错误: 本地版本文件为空或格式无效${NC}" >&2
    echo "请在 $VERSION_FILE 中写入类似 1.0.1 的版本号。" >&2
    return 1
  fi

  printf '%s\n' "$version"
}

fetch_setup_metadata_json() {
  local markdown

  require_python3

  if ! markdown=$(curl -fsSL "$SETUP_SKILL_URL"); then
    echo -e "${RED}错误: 无法读取 setup 入口${NC}" >&2
    echo "读取失败地址: $SETUP_SKILL_URL" >&2
    return 1
  fi

  SETUP_MARKDOWN="$markdown" python3 - <<'PY'
import json
import os
import re

text = os.environ.get("SETUP_MARKDOWN", "")
match = re.search(r"```yaml\s*(.*?)```", text, re.IGNORECASE | re.DOTALL)
if not match:
    raise SystemExit("missing yaml block in setup skill")

data = {}
for raw_line in match.group(1).splitlines():
    line = raw_line.strip()
    if not line or line.startswith("#") or ":" not in line:
        continue
    key, value = line.split(":", 1)
    data[key.strip()] = value.strip().strip('"').strip("'")

required = ["latest_version", "minimum_required_version", "force_update", "skill_package_url"]
missing = [key for key in required if not data.get(key)]
if missing:
    raise SystemExit(f"missing setup fields: {', '.join(missing)}")

print(json.dumps(data, ensure_ascii=False))
PY
}

evaluate_setup_compatibility() {
  local local_version="$1"
  local metadata_json="$2"

  require_python3

  SETUP_METADATA_JSON="$metadata_json" python3 - "$local_version" <<'PY'
import json
import os
import re
import sys

local_version = sys.argv[1]
data = json.loads(os.environ.get("SETUP_METADATA_JSON", "{}"))
latest_version = data.get("latest_version", "0.0.0")
minimum_required_version = data.get("minimum_required_version", "0.0.0")
force_update = str(data.get("force_update", "false")).strip().lower() == "true"


def parse_version(version: str):
    parts = []
    for chunk in version.split("."):
        match = re.match(r"(\d+)", chunk.strip())
        parts.append(int(match.group(1)) if match else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


local_parts = parse_version(local_version)
latest_parts = parse_version(latest_version)
minimum_parts = parse_version(minimum_required_version)

status = "ok"
reason = "up_to_date"
exit_code = 0

if local_parts < minimum_parts:
    status = "blocked"
    reason = "below_minimum"
    exit_code = 2
elif force_update and local_parts < latest_parts:
    status = "blocked"
    reason = "force_update"
    exit_code = 2
elif local_parts < latest_parts:
    status = "warn"
    reason = "outdated"
elif local_parts > latest_parts:
    status = "warn"
    reason = "ahead_of_remote"

print(json.dumps({
    "status": status,
    "reason": reason,
    "local_version": local_version,
    "latest_version": latest_version,
    "minimum_required_version": minimum_required_version,
    "force_update": force_update,
    "skill_package_url": data.get("skill_package_url", ""),
}))
raise SystemExit(exit_code)
PY
}

get_setup_status_json() {
  local local_version
  local metadata_json
  local status_json
  local rc

  if [ -n "$SETUP_STATUS_JSON" ]; then
    printf '%s\n' "$SETUP_STATUS_JSON"
    return "${SETUP_STATUS_EXIT_CODE:-0}"
  fi

  local_version=$(load_local_skill_version) || return 1
  metadata_json=$(fetch_setup_metadata_json) || return 1

  if status_json=$(evaluate_setup_compatibility "$local_version" "$metadata_json"); then
    rc=0
  else
    rc=$?
  fi

  SETUP_STATUS_JSON="$status_json"
  SETUP_STATUS_EXIT_CODE="$rc"

  printf '%s\n' "$SETUP_STATUS_JSON"
  return "$rc"
}

print_setup_status() {
  local status_json
  local rc
  local status
  local reason
  local local_version
  local latest_version
  local minimum_required_version
  local force_update
  local skill_package_url

  if status_json=$(get_setup_status_json); then
    rc=0
  else
    rc=$?
  fi

  if [ -z "$status_json" ]; then
    return "$rc"
  fi

  status=$(printf '%s' "$status_json" | jq -r '.status')
  reason=$(printf '%s' "$status_json" | jq -r '.reason')
  local_version=$(printf '%s' "$status_json" | jq -r '.local_version')
  latest_version=$(printf '%s' "$status_json" | jq -r '.latest_version')
  minimum_required_version=$(printf '%s' "$status_json" | jq -r '.minimum_required_version')
  force_update=$(printf '%s' "$status_json" | jq -r '.force_update')
  skill_package_url=$(printf '%s' "$status_json" | jq -r '.skill_package_url')

  echo "setup 入口: $SETUP_SKILL_URL"
  echo "本地版本: $local_version"
  echo "远端 latest_version: $latest_version"
  echo "远端 minimum_required_version: $minimum_required_version"
  echo "远端 force_update: $force_update"
  echo "技能包地址: $skill_package_url"

  case "$status:$reason" in
    ok:up_to_date)
      echo -e "${GREEN}setup/version 检查通过：本地版本与远端要求一致${NC}"
      ;;
    warn:outdated)
      echo -e "${YELLOW}提示：本地版本低于远端 latest_version，但未触发强制升级。建议先同步本地 Skill 再继续。${NC}"
      ;;
    warn:ahead_of_remote)
      echo -e "${YELLOW}提示：本地版本高于当前远端 setup 元数据；当前按本地开发版本继续。${NC}"
      ;;
    blocked:below_minimum)
      echo -e "${RED}错误：本地版本低于远端 minimum_required_version，不能继续执行创建/推进类操作。${NC}"
      echo "这是开发仓库内的 verify-or-stop 保护：脚本会停止，不会自动覆盖当前 working tree。" >&2
      ;;
    blocked:force_update)
      echo -e "${RED}错误：远端要求 force_update，当前本地版本不能继续执行创建/推进类操作。${NC}"
      echo "这是开发仓库内的 verify-or-stop 保护：脚本会停止，不会自动覆盖当前 working tree。" >&2
      ;;
    *)
      echo -e "${RED}错误：未识别的 setup/version 状态${NC}" >&2
      ;;
  esac

  return "$rc"
}

require_setup_ready() {
  local status_json
  local rc
  local status
  local reason

  if status_json=$(get_setup_status_json); then
    rc=0
  else
    rc=$?
  fi

  if [ -z "$status_json" ]; then
    return "$rc"
  fi

  status=$(printf '%s' "$status_json" | jq -r '.status')
  reason=$(printf '%s' "$status_json" | jq -r '.reason')

  if [ "$status" = "blocked" ]; then
    if [ -z "$SETUP_STATUS_PRINTED" ]; then
      print_setup_status >&2 || true
      SETUP_STATUS_PRINTED=1
    fi
    return 1
  fi

  if [ -z "$SETUP_STATUS_PRINTED" ]; then
    case "$reason" in
      up_to_date)
        echo -e "${GREEN}setup/version 检查通过${NC}" >&2
        ;;
      outdated)
        echo -e "${YELLOW}setup/version 检查通过：本地版本低于远端 latest_version，但当前未被阻断${NC}" >&2
        ;;
      ahead_of_remote)
        echo -e "${YELLOW}setup/version 检查通过：本地版本高于当前远端 setup 元数据${NC}" >&2
        ;;
    esac
    SETUP_STATUS_PRINTED=1
  fi

  return "$rc"
}

pick_default_option() {
  local body="$1"
  local path="$2"

  printf '%s' "$body" | jq -r "${path} | (map(select(.isDefault == true))[0] // .[0]).value"
}

get_select_options() {
  local generate_type="${1:-1}"
  local payload

  payload=$(jq -cn --arg generateType "$generate_type" '{appCode:"ai-story", generateType:$generateType}')
  api_request_checked POST "/project/story/select-options" "$payload"
}

create_project() {
  local name="$1"
  local aspect="$2"
  local img_gen_type="$3"
  local model="$4"
  local video_model="$5"
  local style="$6"
  local script_type="${7:-0}"
  local payload

  if [ -z "$name" ] || [ -z "$aspect" ] || [ -z "$img_gen_type" ] || [ -z "$model" ] || [ -z "$video_model" ] || [ -z "$style" ]; then
    echo -e "${RED}错误: create_project 需要 name/aspect/img_gen_type/model/video_model/style${NC}" >&2
    return 1
  fi

  require_setup_ready || return 1

  payload=$(jq -cn \
    --arg workflowId "695f25b74c510d48b10c4345" \
    --arg name "$name" \
    --arg aspect "$aspect" \
    --arg imgGenType "$img_gen_type" \
    --arg model "$model" \
    --arg videoModel "$video_model" \
    --arg style "$style" \
    --arg scriptType "$script_type" \
    '{
      workflowId: $workflowId,
      name: $name,
      extras: {
        aspect: $aspect,
        imgGenType: $imgGenType,
        model: $model,
        videoModel: $videoModel,
        style: $style,
        content: "",
        workflowTemplate: 0,
        scriptType: $scriptType
      }
    }')

  api_request_checked POST "/project/create" "$payload"
}

create_project_with_defaults() {
  local name="$1"
  local generate_type="${2:-1}"
  local options
  local aspect
  local img_gen_type
  local model
  local video_model
  local style
  local script_type

  options=$(get_select_options "$generate_type")
  aspect=$(pick_default_option "$options" '.data.ratios')
  img_gen_type=$(pick_default_option "$options" '.data.generateTypes')
  model=$(pick_default_option "$options" '.data.models')
  video_model=$(pick_default_option "$options" '.data.videoModels')
  style=$(pick_default_option "$options" '.data.styles')
  script_type=$(printf '%s' "$options" | jq -r '(.data.scriptTypes // []) | (map(select(.isDefault == true))[0] // .[0] // {value:"0"}).value')

  create_project "$name" "$aspect" "$img_gen_type" "$model" "$video_model" "$style" "$script_type"
}

submit_novel() {
  local project_id="$1"
  local content="$2"
  local script_type="${3:-0}"
  local is_split="${4:-0}"
  local payload

  require_setup_ready || return 1

  payload=$(jq -cn \
    --arg userProjectId "$project_id" \
    --arg content "$content" \
    --arg scriptType "$script_type" \
    --arg isSplit "$is_split" \
    '{
      userProjectId: $userProjectId,
      step: "novel_input",
      inputs: [
        {name:"content", type:"text", value:$content},
        {name:"scriptType", type:"text", value:$scriptType},
        {name:"isSplit", type:"text", value:$isSplit}
      ]
    }')

  api_request_checked POST "/project/step/next" "$payload"
}

next_step() {
  local project_id="$1"
  local step="$2"
  local inputs_json="${3:-[]}"
  local payload

  require_setup_ready || return 1
  guard_step_not_already_passed "$project_id" "$step" >/dev/null || return 1

  printf '%s' "$inputs_json" | jq -e '.' >/dev/null
  payload=$(jq -cn \
    --arg userProjectId "$project_id" \
    --arg step "$step" \
    --argjson inputs "$inputs_json" \
    '{userProjectId:$userProjectId, step:$step, inputs:$inputs}')

  api_request_checked POST "/project/step/next" "$payload"
}

get_project() {
  local project_id="$1"
  api_request_checked GET "/project/$project_id"
}

get_roles() {
  local preset_resource_id="$1"
  api_request_checked GET "/comic/roles/$preset_resource_id"
}

get_role_resources() {
  local role_resource_id="$1"
  api_request_checked GET "/comic/role/${role_resource_id}/resources"
}

map_role_gender_code() {
  case "$1" in
    1|male|Male|MALE|男|男性)
      printf '1\n'
      ;;
    2|female|Female|FEMALE|女|女性)
      printf '2\n'
      ;;
    *)
      echo -e "${RED}错误: 无法识别角色性别：$1${NC}" >&2
      return 1
      ;;
  esac
}

map_role_age_code() {
  case "$1" in
    1|儿童)
      printf '1\n'
      ;;
    2|少年)
      printf '2\n'
      ;;
    3|青年)
      printf '3\n'
      ;;
    4|中年)
      printf '4\n'
      ;;
    5|老年)
      printf '5\n'
      ;;
    *)
      echo -e "${RED}错误: 无法识别角色年龄段：$1${NC}" >&2
      return 1
      ;;
  esac
}

ensure_role_voice_step() {
  local project_id="$1"
  local project_json
  local current_step

  project_json=$(get_project "$project_id") || return 1
  current_step=$(printf '%s' "$project_json" | jq -r '.data.workflow.currentStep // empty')

  if [ "$current_step" != "novel_extract_roles" ]; then
    echo -e "${RED}错误: 当前步骤为 ${current_step:-<empty>}，只有在 角色与配音（novel_extract_roles）步骤才能修改角色形象${NC}" >&2
    return 1
  fi

  printf '%s\n' "$project_json"
}

get_role_from_roles() {
  local roles_json="$1"
  local role_ref="$2"
  local role_json

  role_json=$(printf '%s' "$roles_json" | jq -c --arg roleRef "$role_ref" '
    first(.data.roles[]? | select((.resourceId // "") == $roleRef or (.realName // "") == $roleRef)) // empty
  ')

  if [ -z "$role_json" ] || [ "$role_json" = "null" ]; then
    echo -e "${RED}错误: 未找到目标角色：$role_ref${NC}" >&2
    return 1
  fi

  printf '%s\n' "$role_json"
}

build_generate_role_image_payload() {
  local project_json="$1"
  local role_json="$2"
  local description="$3"
  local name
  local age_label
  local age_code
  local style_id
  local model
  local project_id
  local role_resource_id
  local ip_role_id

  name=$(printf '%s' "$role_json" | jq -r '.realName // empty')
  age_label=$(printf '%s' "$role_json" | jq -r '.age // empty')
  age_code=$(map_role_age_code "$age_label") || return 1
  style_id=$(printf '%s' "$role_json" | jq -r '.styleId // empty')
  model=$(printf '%s' "$project_json" | jq -r '.data.extras.model // empty')
  project_id=$(printf '%s' "$project_json" | jq -r '.data.id // empty')
  role_resource_id=$(printf '%s' "$role_json" | jq -r '.resourceId // empty')
  ip_role_id=$(printf '%s' "$role_json" | jq -r '.ipRoleId // empty')

  if [ -z "$name" ] || [ -z "$style_id" ] || [ -z "$model" ] || [ -z "$project_id" ] || [ -z "$role_resource_id" ] || [ -z "$ip_role_id" ]; then
    echo -e "${RED}错误: 构造角色改图请求时缺少必要字段${NC}" >&2
    return 1
  fi

  jq -cn \
    --arg name "$name" \
    --argjson age "$age_code" \
    --arg description "$description" \
    --argjson styleId "$style_id" \
    --arg model "$model" \
    --arg projectId "$project_id" \
    --arg roleId "$role_resource_id" \
    --argjson id "$ip_role_id" \
    '{
      name: $name,
      age: $age,
      description: $description,
      styleId: $styleId,
      model: $model,
      projectId: $projectId,
      roleId: $roleId,
      id: $id
    }'
}

generate_role_image() {
  local project_json="$1"
  local role_json="$2"
  local description="$3"
  local payload

  require_setup_ready || return 1
  payload=$(build_generate_role_image_payload "$project_json" "$role_json" "$description") || return 1
  api_request_checked POST "/ipRole/generateIpRole" "$payload"
}

wait_for_new_role_image_ready() {
  local role_resource_id="$1"
  local existing_ids_json="$2"
  local max_attempts="${3:-60}"
  local interval="${4:-3}"
  local i
  local resources_json
  local failed_candidate
  local ready_candidate
  local pending_desc

  for i in $(seq 1 "$max_attempts"); do
    resources_json=$(get_role_resources "$role_resource_id") || return 1

    failed_candidate=$(printf '%s' "$resources_json" | jq -c --argjson existingIds "$existing_ids_json" '
      [.data[]? | select((.resourceId as $id | $existingIds | index($id) | not) and .taskStatus == "FAILED")][0] // empty
    ')
    if [ -n "$failed_candidate" ] && [ "$failed_candidate" != "null" ]; then
      echo -e "${RED}错误: 新角色图生成失败${NC}" >&2
      printf '%s\n' "$failed_candidate" | jq '.' >&2
      return 1
    fi

    ready_candidate=$(printf '%s' "$resources_json" | jq -c --argjson existingIds "$existing_ids_json" '
      [.data[]? | select((.resourceId as $id | $existingIds | index($id) | not) and .taskStatus == "SUCCESS" and ((.imgUrl // "") != ""))][0] // empty
    ')
    if [ -n "$ready_candidate" ] && [ "$ready_candidate" != "null" ]; then
      printf '%s\n' "$ready_candidate"
      return 0
    fi

    pending_desc=$(printf '%s' "$resources_json" | jq -r --argjson existingIds "$existing_ids_json" '
      [.data[]? | select((.resourceId as $id | $existingIds | index($id) | not))
       | "\(.resourceId):\(.taskStatus // \"UNKNOWN\")"] | join(", ")
    ')

    if [ -n "$pending_desc" ]; then
      echo -e "[$i/$max_attempts] 等待新角色图生成完成: ${YELLOW}${pending_desc}${NC}" >&2
    else
      echo -e "[$i/$max_attempts] 等待新角色图资源出现..." >&2
    fi
    sleep "$interval"
  done

  echo -e "${RED}等待新角色图生成完成超时${NC}" >&2
  return 1
}

build_apply_role_image_payload() {
  local project_id="$1"
  local role_json="$2"
  local image_resource_id="$3"
  local name
  local age_label
  local age_code
  local gender_label
  local gender_code
  local role_resource_id

  name=$(printf '%s' "$role_json" | jq -r '.realName // empty')
  age_label=$(printf '%s' "$role_json" | jq -r '.age // empty')
  age_code=$(map_role_age_code "$age_label") || return 1
  gender_label=$(printf '%s' "$role_json" | jq -r '.gender // empty')
  gender_code=$(map_role_gender_code "$gender_label") || return 1
  role_resource_id=$(printf '%s' "$role_json" | jq -r '.resourceId // empty')

  if [ -z "$name" ] || [ -z "$role_resource_id" ] || [ -z "$image_resource_id" ]; then
    echo -e "${RED}错误: 构造角色应用新图请求时缺少必要字段${NC}" >&2
    return 1
  fi

  jq -cn \
    --arg name "$name" \
    --argjson age "$age_code" \
    --argjson gender "$gender_code" \
    --arg imageResourceId "$image_resource_id" \
    --arg userProject "$project_id" \
    --arg roleId "$role_resource_id" \
    '{
      name: $name,
      age: $age,
      gender: $gender,
      imageResourceId: $imageResourceId,
      isPublic: 1,
      userProject: $userProject,
      roleId: $roleId
    }'
}

apply_role_image() {
  local project_id="$1"
  local role_json="$2"
  local image_resource_id="$3"
  local payload

  require_setup_ready || return 1
  payload=$(build_apply_role_image_payload "$project_id" "$role_json" "$image_resource_id") || return 1
  api_request_checked POST "/ipRole/applyImage" "$payload"
}

wait_for_applied_role_image() {
  local preset_resource_id="$1"
  local role_ref="$2"
  local expected_image_resource_id="$3"
  local max_attempts="${4:-30}"
  local interval="${5:-2}"
  local i
  local roles_json
  local role_json
  local current_image_resource_id
  local current_img_url

  for i in $(seq 1 "$max_attempts"); do
    roles_json=$(get_roles "$preset_resource_id") || return 1
    role_json=$(get_role_from_roles "$roles_json" "$role_ref") || return 1
    current_image_resource_id=$(printf '%s' "$role_json" | jq -r '.imageResourceId // empty')
    current_img_url=$(printf '%s' "$role_json" | jq -r '.imgUrl // empty')

    if [ "$current_image_resource_id" = "$expected_image_resource_id" ] && [ -n "$current_img_url" ]; then
      printf '%s\n' "$role_json"
      return 0
    fi

    echo -e "[$i/$max_attempts] 等待角色主图切换到新图片资源: ${YELLOW}${current_image_resource_id:-<empty>}${NC}" >&2
    sleep "$interval"
  done

  echo -e "${RED}等待角色主图切换超时${NC}" >&2
  return 1
}

modify_role_image() {
  local project_id="$1"
  local role_ref="$2"
  local description="$3"
  local project_json
  local preset_resource_id
  local roles_json
  local role_json
  local role_resource_id
  local before_resources_json
  local existing_ids_json
  local generate_result
  local task_id
  local generated_candidate_json
  local generated_image_resource_id
  local generated_image_url
  local updated_role_json
  local role_name
  local selected_image_resource_id
  local selected_image_url
  local updated_appearance

  if [ -z "$project_id" ] || [ -z "$role_ref" ] || [ -z "$description" ]; then
    echo -e "${RED}错误: modify_role_image 需要 project_id / role_ref / description${NC}" >&2
    return 1
  fi

  require_setup_ready || return 1
  project_json=$(ensure_role_voice_step "$project_id") || return 1
  preset_resource_id=$(printf '%s' "$project_json" | jq -r '.data.presetResourceId // empty')
  roles_json=$(get_roles "$preset_resource_id") || return 1
  role_json=$(get_role_from_roles "$roles_json" "$role_ref") || return 1
  role_resource_id=$(printf '%s' "$role_json" | jq -r '.resourceId // empty')
  role_name=$(printf '%s' "$role_json" | jq -r '.realName // empty')

  before_resources_json=$(get_role_resources "$role_resource_id") || return 1
  existing_ids_json=$(printf '%s' "$before_resources_json" | jq -c '[.data[]?.resourceId]')

  generate_result=$(generate_role_image "$project_json" "$role_json" "$description") || return 1
  task_id=$(printf '%s' "$generate_result" | jq -r '.data.taskId // empty')
  if [ -n "$task_id" ]; then
    poll_task "$task_id" 120 3 >/dev/null
  fi

  generated_candidate_json=$(wait_for_new_role_image_ready "$role_resource_id" "$existing_ids_json" 40 2) || return 1
  generated_image_resource_id=$(printf '%s' "$generated_candidate_json" | jq -r '.resourceId // empty')
  generated_image_url=$(printf '%s' "$generated_candidate_json" | jq -r '.imgUrl // empty')

  apply_role_image "$project_id" "$role_json" "$generated_image_resource_id" >/dev/null || return 1
  updated_role_json=$(wait_for_applied_role_image "$preset_resource_id" "$role_resource_id" "$generated_image_resource_id" 30 2) || return 1
  selected_image_resource_id=$(printf '%s' "$updated_role_json" | jq -r '.imageResourceId // empty')
  selected_image_url=$(printf '%s' "$updated_role_json" | jq -r '.imgUrl // empty')
  updated_appearance=$(printf '%s' "$updated_role_json" | jq -r '.appearance // empty')

  jq -cn \
    --arg projectId "$project_id" \
    --arg presetResourceId "$preset_resource_id" \
    --arg roleResourceId "$role_resource_id" \
    --arg roleName "$role_name" \
    --arg taskId "$task_id" \
    --arg generatedImageResourceId "$generated_image_resource_id" \
    --arg generatedImageUrl "$generated_image_url" \
    --arg selectedImageResourceId "$selected_image_resource_id" \
    --arg selectedImageUrl "$selected_image_url" \
    --arg appearance "$updated_appearance" \
    '{
      projectId: $projectId,
      presetResourceId: $presetResourceId,
      roleResourceId: $roleResourceId,
      roleName: $roleName,
      generateTaskId: $taskId,
      generatedImageResourceId: $generatedImageResourceId,
      generatedImageUrl: $generatedImageUrl,
      selectedImageResourceId: $selectedImageResourceId,
      selectedImageUrl: $selectedImageUrl,
      appearance: $appearance
    }'
}

get_preset() {
  local preset_resource_id="$1"
  api_request_checked GET "/resource/comicPreset/$preset_resource_id"
}

get_resource() {
  local resource_id="$1"
  api_request_checked GET "/resource/$resource_id"
}

prev_step() {
  local project_id="$1"
  local step="$2"
  local chapter_num="${3:-1}"
  local payload

  require_setup_ready || return 1

  payload=$(jq -cn \
    --arg userProjectId "$project_id" \
    --arg step "$step" \
    --argjson chapterNum "$chapter_num" \
    '{userProjectId:$userProjectId, step:$step, chapterNum:$chapterNum}')

  api_request_checked POST "/project/step/prev" "$payload"
}

ensure_chapter_scenes_step() {
  local project_id="$1"
  local chapter_num="${2:-1}"
  local project_json
  local current_step

  project_json=$(get_project "$project_id") || return 1
  current_step=$(printf '%s' "$project_json" | jq -r '.data.workflow.currentStep // empty')

  if [ "$current_step" = "novel_chapter_scenes" ]; then
    printf '%s\n' "$project_json"
    return 0
  fi

  if [ "$current_step" = "novel_chapter_video" ]; then
    prev_step "$project_id" "novel_chapter_video" "$chapter_num" >/dev/null
    get_project "$project_id"
    return 0
  fi

  echo -e "${RED}错误: 当前步骤为 ${current_step:-<empty>}，无法直接进入分镜图步骤${NC}" >&2
  return 1
}

ensure_scene_task_ready() {
  local project_id="$1"
  local chapter_num="${2:-1}"
  local project_json
  local preset_resource_id

  project_json=$(ensure_chapter_scenes_step "$project_id" "$chapter_num") || return 1
  preset_resource_id=$(printf '%s' "$project_json" | jq -r '.data.presetResourceId // empty')

  if [ -z "$preset_resource_id" ]; then
    echo -e "${RED}错误: 未找到 presetResourceId，无法确认 sceneTaskStatus${NC}" >&2
    return 1
  fi

  wait_for_preset_chapter_status "$preset_resource_id" "$chapter_num" "sceneTaskStatus" "SUCCESS" 120 3 >/dev/null || return 1
  printf '%s\n' "$project_json"
}

wait_for_roles_ready() {
  local preset_resource_id="$1"
  local max_attempts="${2:-60}"
  local interval="${3:-3}"
  local i
  local roles_json
  local pending_count
  local pending_desc

  for i in $(seq 1 "$max_attempts"); do
    roles_json=$(get_roles "$preset_resource_id") || return 1
    pending_count=$(printf '%s' "$roles_json" | jq '[.data.roles[]? | select(.taskStatus != "SUCCESS" or ((.imgUrl // "") == ""))] | length')

    if [ "$pending_count" = "0" ]; then
      printf '%s\n' "$roles_json"
      return 0
    fi

    pending_desc=$(printf '%s' "$roles_json" | jq -r '[.data.roles[]? | select(.taskStatus != "SUCCESS" or ((.imgUrl // "") == "")) | "\(.realName):\(.taskStatus // "UNKNOWN")"] | join(", ")')
    echo -e "[$i/$max_attempts] 等待角色图完成: ${YELLOW}${pending_desc}${NC}" >&2
    sleep "$interval"
  done

  echo -e "${RED}等待角色图完成超时${NC}" >&2
  return 1
}

build_extract_roles_inputs() {
  local preset_resource_id="$1"
  local chapter_num="${2:-1}"
  local roles_json

  roles_json=$(get_roles "$preset_resource_id") || return 1
  printf '%s' "$roles_json" | jq -c --argjson chapterNum "$chapter_num" '
    def normalize_voice:
      if .value != null and (.value | type) == "string" and (.value | test("^[0-9]+$"))
      then .value = (.value | tonumber)
      else .
      end;

    ((.data.voiceInputs[0] // .data.roles[0].inputs[0]) | normalize_voice) as $voice
    | [
        {type:"number", name:"chapterNum", value:$chapterNum},
        $voice
      ]
  '
}

wait_for_preset_chapter_status() {
  local preset_resource_id="$1"
  local chapter_num="$2"
  local field_name="$3"
  local expected_value="${4:-SUCCESS}"
  local max_attempts="${5:-60}"
  local interval="${6:-3}"
  local i
  local preset_json
  local current_value

  for i in $(seq 1 "$max_attempts"); do
    preset_json=$(get_preset "$preset_resource_id") || return 1
    current_value=$(printf '%s' "$preset_json" | jq -r --argjson chapterNum "$chapter_num" --arg field "$field_name" '
      (.data.data.chapters // [])
      | map(select(.num == $chapterNum))[0][$field] // empty
    ')

    if [ "$current_value" = "$expected_value" ]; then
      printf '%s\n' "$preset_json"
      return 0
    fi

    echo -e "[$i/$max_attempts] 等待章节字段 ${BLUE}${field_name}${NC} = ${YELLOW}${expected_value}${NC}，当前为: ${current_value:-<empty>}" >&2
    sleep "$interval"
  done

  echo -e "${RED}等待章节字段 ${field_name} 超时${NC}" >&2
  return 1
}

resolve_storyboard_id() {
  local preset_resource_id="$1"
  local chapter_num="${2:-1}"
  local preset_json
  local scene_task_id
  local task_json

  preset_json=$(get_preset "$preset_resource_id") || return 1
  scene_task_id=$(printf '%s' "$preset_json" | jq -r --argjson chapterNum "$chapter_num" '
    (.data.data.chapters // [])
    | map(select(.num == $chapterNum))[0].sceneTaskId // empty
  ')

  if [ -z "$scene_task_id" ]; then
    echo -e "${RED}错误: 未找到 sceneTaskId${NC}" >&2
    return 1
  fi

  task_json=$(get_task "$scene_task_id") || return 1
  printf '%s' "$task_json" | jq -r '.data.resourceId // empty'
}

get_storyboard_scene() {
  local storyboard_id="$1"
  local scene_index="${2:-0}"
  local storyboard_json

  storyboard_json=$(get_resource "$storyboard_id") || return 1
  printf '%s' "$storyboard_json" | jq -c --argjson sceneIndex "$scene_index" '.data.data.scenes[$sceneIndex]'
}

get_storyboard_scenes() {
  local storyboard_id="$1"
  local storyboard_json

  storyboard_json=$(get_resource "$storyboard_id") || return 1
  printf '%s' "$storyboard_json" | jq -c '.data.data.scenes // []'
}

build_storyboard_scene_summaries() {
  local storyboard_id="$1"
  local storyboard_json

  storyboard_json=$(get_resource "$storyboard_id") || return 1
  printf '%s' "$storyboard_json" | jq -c '
    [(.data.data.scenes // []) | to_entries[]
      | {
          sceneIndex: .key,
          sceneId: .value.id,
          sceneUuid: (.value.scene.scene_id // ""),
          sceneName: (.value.scene.scene_name // ""),
          sceneDescription: (.value.scene.scene_description // .value.content // ""),
          imageUrl: (.value.image // ""),
          imageResourceId: (.value.imageResourceId // ""),
          displayType: (.value.displayType // ""),
          videoPlayUrl: (if (.value.videoPlayUrl // "") != "" then .value.videoPlayUrl else (if (.value.video // "") != "" then ("https://ai.fun.tv/static/videoPreview.html?url=" + ((.value.video // "")|@uri)) else "" end) end)
        }
    ]
  '
}

build_scene_review_manifest() {
  local storyboard_id="$1"
  local scenes_json
  local result='[]'
  local scene_row
  local scene_id
  local scene_index
  local prompt_json
  local resources_json
  local selected_image
  local selected_video

  scenes_json=$(get_storyboard_scenes "$storyboard_id") || return 1
  while IFS= read -r scene_row; do
    scene_index=$(printf '%s' "$scene_row" | jq -r '.key')
    scene_id=$(printf '%s' "$scene_row" | jq -r '.value.id')
    prompt_json=$(get_scene_prompt_detail "$scene_id") || return 1
    resources_json=$(get_scene_resources "$scene_id") || return 1
    selected_image=$(printf '%s' "$resources_json" | jq -c '[.data[]? | select(.type == "image" and .selected == true)][0] // null')
    selected_video=$(printf '%s' "$resources_json" | jq -c '[.data[]? | select(.type == "video" and .selected == true)][0] // null | if . == null then null else {resourceId, videoPlayUrl: (.videoPlayUrl // (if (.url // "") != "" then ("https://ai.fun.tv/static/videoPreview.html?url=" + ((.url // "")|@uri)) else "" end)), videoCover, duration, taskStatus, selected} end')

    result=$(printf '%s' "$result" | jq -c \
      --argjson scene "$scene_row" \
      --argjson sceneIndex "$scene_index" \
      --argjson promptDetail "$prompt_json" \
      --argjson selectedImage "$selected_image" \
      --argjson selectedVideo "$selected_video" '
        . + [{
          sceneIndex: $sceneIndex,
          sceneId: $scene.value.id,
          sceneName: ($scene.value.scene.scene_name // ""),
          sceneDescription: ($scene.value.scene.scene_description // $scene.value.content // ""),
          storyboardImage: ($scene.value.image // ""),
        imagePromptInfo: ($promptDetail.data.image.imagePromptInfo // {}),
        videoPromptInfo: (($promptDetail.data.video // {}) | del(.url)),
        selectedImage: $selectedImage,
        selectedVideo: $selectedVideo
      }]
      ')
  done < <(printf '%s' "$scenes_json" | jq -c 'to_entries[]')

  printf '%s\n' "$result"
}

batch_get_scene_prompt_details() {
  local storyboard_id="$1"
  build_scene_review_manifest "$storyboard_id" | jq '[.[] | {sceneIndex, sceneId, sceneName, imagePromptInfo, videoPromptInfo}]'
}

download_storyboard_scene_images() {
  local storyboard_id="$1"
  local output_dir="$2"
  local manifest_json

  if [ -z "$output_dir" ]; then
    echo -e "${RED}错误: download_storyboard_scene_images 需要 output_dir${NC}" >&2
    return 1
  fi

  manifest_json=$(build_scene_review_manifest "$storyboard_id") || return 1
  mkdir -p "$output_dir"

  MANIFEST_JSON="$manifest_json" OUTPUT_DIR="$output_dir" python3 - <<'PY'
import json
import os
import re
import urllib.request
from pathlib import Path

manifest = json.loads(os.environ["MANIFEST_JSON"])
output_dir = Path(os.environ["OUTPUT_DIR"])
result = []

def safe_slug(text: str) -> str:
    text = re.sub(r"[^\w\-\u4e00-\u9fff]+", "-", text).strip("-")
    return text or "scene"

for item in manifest:
    selected_image = item.get("selectedImage") or {}
    image_url = selected_image.get("url") or item.get("storyboardImage") or ""
    local_path = ""
    if image_url:
        name = f"scene-{item.get('sceneIndex', 0)}-{safe_slug(item.get('sceneName') or item.get('sceneId') or '')}.png"
        path = output_dir / name
        urllib.request.urlretrieve(image_url, path)
        local_path = str(path)
    enriched = dict(item)
    enriched["downloadedImagePath"] = local_path
    result.append(enriched)

print(json.dumps(result, ensure_ascii=False))
PY
}

batch_refine_scene_images_from_file() {
  local project_id="$1"
  local spec_file="$2"
  local chapter_num="${3:-1}"
  local result='[]'
  local item
  local scene_id
  local scene_description
  local prompt
  local old_image_json
  local refine_result

  if [ ! -f "$spec_file" ]; then
    echo -e "${RED}错误: spec_file 不存在: $spec_file${NC}" >&2
    return 1
  fi

  jq -e '.' "$spec_file" >/dev/null
  while IFS= read -r item; do
    scene_id=$(printf '%s' "$item" | jq -r '.sceneId // empty')
    scene_description=$(printf '%s' "$item" | jq -r '.sceneDescription // empty')
    prompt=$(printf '%s' "$item" | jq -r '.prompt // empty')

    if [ -z "$scene_id" ] || [ -z "$scene_description" ] || [ -z "$prompt" ]; then
      echo -e "${RED}错误: spec item 缺少 sceneId / sceneDescription / prompt${NC}" >&2
      return 1
    fi

    old_image_json=$(get_scene_image_resource "$scene_id") || return 1
    refine_result=$(refine_scene_image "$project_id" "$scene_id" "$scene_description" "$prompt" "$chapter_num") || return 1
    result=$(printf '%s' "$result" | jq -c \
      --argjson item "$item" \
      --arg oldImageUrl "$(printf '%s' "$old_image_json" | jq -r '.url // empty')" \
      --argjson refine "$refine_result" '
        . + [{
          sceneId: ($item.sceneId // ""),
          oldImageUrl: $oldImageUrl,
          taskId: ($refine.taskId // ""),
          newImageUrl: ($refine.selectedImageUrl // ""),
          sceneDescription: ($refine.sceneDescription // ""),
          prompt: ($refine.prompt // "")
        }]
      ')
  done < <(jq -c '.[]' "$spec_file")

  printf '%s\n' "$result"
}

get_scene_resources() {
  local scene_id="$1"
  api_request_checked GET "/storyboard/scene/${scene_id}/resources"
}

get_scene_prompt_detail() {
  local scene_id="$1"
  api_request_checked GET "/storyboard/scene/${scene_id}/prompt/detail?sceneId=${scene_id}"
}

build_scene_image_payload() {
  local scene_id="$1"
  local screen_description="${2:-}"
  local subject_description="${3:-}"
  local prompt_json

  prompt_json=$(get_scene_prompt_detail "$scene_id") || return 1
  validate_scene_image_prompt_refs "$prompt_json" "$subject_description" || return 1

  printf '%s' "$prompt_json" | jq -c \
    --arg sceneId "$scene_id" \
    --arg screenDescription "$screen_description" \
    --arg subjectDescription "$subject_description" '
      .data.image as $image
      | ($image.imagePromptInfo // {}) as $promptInfo
      | ($image.roles // []) as $roles
      | {
          sceneId: $sceneId,
          roles: $roles,
          imgGenType: ($image.imgGenType // "1"),
          promptV2: {
            screen_description: (if $screenDescription != "" then $screenDescription else ($promptInfo.screen_description // "") end),
            subject_description: (if $subjectDescription != "" then $subjectDescription else ($promptInfo.subject_description // "") end)
          },
          model: ($image.model // "doubao-seedream-3.0")
        }
    '
}

validate_scene_image_prompt_refs() {
  local prompt_json="$1"
  local subject_description="$2"

  if [ -z "$subject_description" ]; then
    return 0
  fi

  SUBJECT_DESCRIPTION="$subject_description" PROMPT_JSON="$prompt_json" python3 - <<'PY'
import json
import os
import re
import sys

subject = os.environ.get("SUBJECT_DESCRIPTION", "")
prompt_json = os.environ.get("PROMPT_JSON", "{}")
data = json.loads(prompt_json)
roles = (((data.get("data") or {}).get("image") or {}).get("roles") or [])
allowed = {str(role.get("id")): role.get("realName") or role.get("label") or "" for role in roles if role.get("id") is not None}
refs = re.findall(r"@\[[^\]]+\]\(id:(\d+)\)", subject)
invalid = [ref for ref in refs if ref not in allowed]

if invalid:
    allowed_text = ", ".join(f"{rid}:{name}" if name else rid for rid, name in allowed.items()) or "<empty>"
    sys.stderr.write(f"错误: prompt 中引用了当前 scene 不存在的角色 id: {', '.join(invalid)}\n")
    sys.stderr.write(f"当前 scene 允许的角色引用: {allowed_text}\n")
    raise SystemExit(1)
PY
}

validate_scene_video_text_prompts() {
  local prompt="$1"
  local camera_prompt="$2"

  if [[ "$prompt" == *"@["* ]] || [[ "$camera_prompt" == *"@["* ]]; then
    echo -e "${RED}错误: scene 视频提示词不应包含 @人物(id:xxxx) 引用，请把动作/运镜改成纯文本描述${NC}" >&2
    return 1
  fi
}

extract_task_id_from_array_result() {
  local body="$1"
  printf '%s' "$body" | jq -r '
    if (.data | type) == "array" then
      (.data[0].taskId // empty)
    else
      (.data.taskId // .data.resultId // empty)
    end
  '
}

wait_for_new_scene_resource_ready() {
  local scene_id="$1"
  local resource_type="$2"
  local existing_ids_json="$3"
  local max_attempts="${4:-60}"
  local interval="${5:-3}"
  local i
  local resources_json
  local failed_candidate
  local ready_candidate
  local pending_desc

  for i in $(seq 1 "$max_attempts"); do
    resources_json=$(get_scene_resources "$scene_id") || return 1

    failed_candidate=$(printf '%s' "$resources_json" | jq -c --arg type "$resource_type" --argjson existingIds "$existing_ids_json" '
      [.data[]? | select(.type == $type and (.resourceId as $id | $existingIds | index($id) | not) and .taskStatus == "FAILED")][0] // empty
    ')
    if [ -n "$failed_candidate" ] && [ "$failed_candidate" != "null" ]; then
      echo -e "${RED}错误: 新 ${resource_type} 资源生成失败${NC}" >&2
      printf '%s\n' "$failed_candidate" | jq '.' >&2
      return 1
    fi

    ready_candidate=$(printf '%s' "$resources_json" | jq -c --arg type "$resource_type" --argjson existingIds "$existing_ids_json" '
      [.data[]? | select(.type == $type and (.resourceId as $id | $existingIds | index($id) | not) and .taskStatus == "SUCCESS" and (if $type == "video" then (((.videoPlayUrl // "") != "") or ((.url // "") != "")) else ((.url // "") != "") end))][0] // empty
    ')
    if [ -n "$ready_candidate" ] && [ "$ready_candidate" != "null" ]; then
      printf '%s\n' "$ready_candidate"
      return 0
    fi

    pending_desc=$(printf '%s' "$resources_json" | jq -r --arg type "$resource_type" --argjson existingIds "$existing_ids_json" '
      [.data[]? | select(.type == $type and (.resourceId as $id | $existingIds | index($id) | not))
       | "\(.resourceId):\(.taskStatus // "UNKNOWN")"] | join(", ")
    ')

    if [ -n "$pending_desc" ]; then
      echo -e "[$i/$max_attempts] 等待新 ${resource_type} 资源完成: ${YELLOW}${pending_desc}${NC}" >&2
    else
      echo -e "[$i/$max_attempts] 等待新的 ${resource_type} 资源出现..." >&2
    fi
    sleep "$interval"
  done

  echo -e "${RED}等待新的 ${resource_type} 资源完成超时${NC}" >&2
  return 1
}

wait_for_selected_scene_resource() {
  local scene_id="$1"
  local resource_id="$2"
  local resource_type="$3"
  local max_attempts="${4:-40}"
  local interval="${5:-3}"
  local i
  local resources_json
  local matched_resource

  for i in $(seq 1 "$max_attempts"); do
    resources_json=$(get_scene_resources "$scene_id") || return 1
    matched_resource=$(printf '%s' "$resources_json" | jq -c --arg resourceId "$resource_id" --arg type "$resource_type" '
      [.data[]? | select(.resourceId == $resourceId and .type == $type and .taskStatus == "SUCCESS" and (.selected == true))][0] // empty
    ')

    if [ -n "$matched_resource" ] && [ "$matched_resource" != "null" ]; then
      printf '%s\n' "$matched_resource"
      return 0
    fi

    echo -e "[$i/$max_attempts] 等待 ${resource_type} 资源切换为 selected=true: ${YELLOW}${resource_id}${NC}" >&2
    sleep "$interval"
  done

  echo -e "${RED}等待 ${resource_type} 资源切换为当前选中超时${NC}" >&2
  return 1
}

generate_scene_image() {
  local project_id="$1"
  local scene_id="$2"
  local screen_description="${3:-}"
  local subject_description="${4:-}"
  local chapter_num="${5:-1}"
  local payload

  require_setup_ready || return 1
  ensure_scene_task_ready "$project_id" "$chapter_num" >/dev/null || return 1
  payload=$(build_scene_image_payload "$scene_id" "$screen_description" "$subject_description") || return 1
  api_request_checked POST "/storyboard/scene/ai/image" "$payload"
}

refine_scene_image() {
  local project_id="$1"
  local scene_id="$2"
  local screen_description="$3"
  local subject_description="$4"
  local chapter_num="${5:-1}"
  local before_resources_json
  local existing_ids_json
  local result
  local task_id
  local selected_resource_json
  local prompt_json

  if [ -z "$project_id" ] || [ -z "$scene_id" ] || [ -z "$screen_description" ] || [ -z "$subject_description" ]; then
    echo -e "${RED}错误: refine_scene_image 需要 project_id / scene_id / sceneDescription / prompt${NC}" >&2
    return 1
  fi

  before_resources_json=$(get_scene_resources "$scene_id") || return 1
  existing_ids_json=$(printf '%s' "$before_resources_json" | jq -c '[.data[]? | select(.type == "image") | .resourceId]')

  result=$(generate_scene_image "$project_id" "$scene_id" "$screen_description" "$subject_description" "$chapter_num") || return 1
  task_id=$(extract_task_id_from_array_result "$result")
  if [ -n "$task_id" ]; then
    poll_task "$task_id" 120 3 >/dev/null
  fi

  selected_resource_json=$(wait_for_new_scene_resource_ready "$scene_id" "image" "$existing_ids_json" 60 2) || return 1
  selected_resource_json=$(wait_for_selected_scene_resource "$scene_id" "$(printf '%s' "$selected_resource_json" | jq -r '.resourceId')" "image" 30 2) || return 1
  prompt_json=$(get_scene_prompt_detail "$scene_id") || return 1

  printf '%s\n%s' "$selected_resource_json" "$prompt_json" | jq -sc --arg taskId "$task_id" '
    .[0] as $resource
    | .[1].data as $detail
    | {
        taskId: $taskId,
        sceneId: ($detail.image.sceneId // $resource.sceneId // ""),
        selectedImageResourceId: ($resource.resourceId // ""),
        selectedImageUrl: ($resource.url // ""),
        sceneDescription: ($detail.image.imagePromptInfo.screen_description // ""),
        prompt: ($detail.image.imagePromptInfo.subject_description // ""),
        model: ($detail.image.model // ""),
        imgGenType: ($detail.image.imgGenType // "")
      }
  '
}

get_scene_image_resource() {
  local scene_id="$1"
  local preferred_image_id="${2:-}"
  local strict_preferred="${3:-0}"
  local resources_json
  local matched_image

  resources_json=$(get_scene_resources "$scene_id") || return 1

  if [ "$strict_preferred" = "1" ] && [ -n "$preferred_image_id" ]; then
    matched_image=$(printf '%s' "$resources_json" | jq -c --arg preferredImageId "$preferred_image_id" '
      (.data // []) | map(select(.type == "image" and .resourceId == $preferredImageId))[0] // empty
    ')

    if [ -z "$matched_image" ] || [ "$matched_image" = "null" ]; then
      echo -e "${RED}错误: 未找到与 prompt/detail.video.imageId 对应的 scene 基准图资源，已停止图转视频${NC}" >&2
      echo "不要用 selected=true 或其他 image 资源替代当前 video.imageId 对应项。" >&2
      return 1
    fi

    printf '%s\n' "$matched_image"
    return 0
  fi

  matched_image=$(printf '%s' "$resources_json" | jq -c --arg preferredImageId "$preferred_image_id" '
    (.data // []) as $items
    | if ($preferredImageId != "") then
        ($items | map(select(.type == "image" and .resourceId == $preferredImageId))[0])
      else
        null
      end
      // ($items | map(select(.type == "image" and .selected == true))[0])
      // empty
  ')

  if [ -z "$matched_image" ] || [ "$matched_image" = "null" ]; then
    echo -e "${RED}错误: 当前 scene 没有可用的基准分镜图资源，不能发起图转视频${NC}" >&2
    return 1
  fi

  printf '%s\n' "$matched_image"
}

build_scene_video_payload() {
  local scene_id="$1"
  local duration="${2:--1}"
  local clarity="${3:-720p}"
  local tail_image="${4:-}"
  local prompt_override="${5:-}"
  local camera_prompt_override="${6:-}"
  local model_override="${7:-}"
  local prompt_json
  local image_json
  local preferred_image_id

  prompt_json=$(get_scene_prompt_detail "$scene_id") || return 1
  preferred_image_id=$(printf '%s' "$prompt_json" | jq -r '.data.video.imageId // empty')

  if [ -z "$preferred_image_id" ]; then
    echo -e "${RED}错误: prompt/detail 未提供 video.imageId，无法安全确定图转视频基准图${NC}" >&2
    return 1
  fi

  image_json=$(get_scene_image_resource "$scene_id" "$preferred_image_id" "1") || return 1

  printf '%s\n%s' "$prompt_json" "$image_json" | jq -sc \
    --arg duration "$duration" \
    --arg clarity "$clarity" \
    --arg tailImage "$tail_image" \
    --arg promptOverride "$prompt_override" \
    --arg cameraPromptOverride "$camera_prompt_override" \
    --arg modelOverride "$model_override" '
    .[0].data.video as $video
    | .[1] as $image
    | {
        sceneId: $video.sceneId,
        prompt: (if $promptOverride != "" then $promptOverride else ($video.prompt // "") end),
        cameraPrompt: (if $cameraPromptOverride != "" then $cameraPromptOverride else ($video.cameraPrompt // "") end),
        model: (if $modelOverride != "" then $modelOverride else ($video.model // "doubao-pro") end),
        duration: $duration,
        firstImage: ($image.url // ""),
        tailImage: $tailImage,
        clarity: $clarity,
        imageId: ($image.resourceId // "")
      }
  '
}

generate_scene_video() {
  local project_id="$1"
  local scene_id="$2"
  local duration="${3:--1}"
  local clarity="${4:-720p}"
  local tail_image="${5:-}"
  local chapter_num="${6:-1}"
  local prompt_override="${7:-}"
  local camera_prompt_override="${8:-}"
  local model_override="${9:-}"
  local payload

  require_setup_ready || return 1
  ensure_scene_task_ready "$project_id" "$chapter_num" >/dev/null || return 1

  payload=$(build_scene_video_payload "$scene_id" "$duration" "$clarity" "$tail_image" "$prompt_override" "$camera_prompt_override" "$model_override") || return 1
  api_request_checked POST "/storyboard/scene/ai/video" "$payload"
}

refine_scene_video() {
  local project_id="$1"
  local scene_id="$2"
  local prompt_override="$3"
  local camera_prompt_override="$4"
  local chapter_num="${5:-1}"
  local duration="${6:--1}"
  local clarity="${7:-720p}"
  local tail_image="${8:-}"
  local model_override="${9:-}"
  local before_resources_json
  local existing_ids_json
  local result
  local task_id
  local selected_resource_json
  local prompt_json

  if [ -z "$project_id" ] || [ -z "$scene_id" ] || [ -z "$prompt_override" ] || [ -z "$camera_prompt_override" ]; then
    echo -e "${RED}错误: refine_scene_video 需要 project_id / scene_id / prompt / cameraPrompt${NC}" >&2
    return 1
  fi

  validate_scene_video_text_prompts "$prompt_override" "$camera_prompt_override" || return 1

  before_resources_json=$(get_scene_resources "$scene_id") || return 1
  existing_ids_json=$(printf '%s' "$before_resources_json" | jq -c '[.data[]? | select(.type == "video") | .resourceId]')

  result=$(generate_scene_video "$project_id" "$scene_id" "$duration" "$clarity" "$tail_image" "$chapter_num" "$prompt_override" "$camera_prompt_override" "$model_override") || return 1
  task_id=$(extract_task_id_from_array_result "$result")
  if [ -n "$task_id" ]; then
    poll_task "$task_id" 180 5 >/dev/null
  fi

  selected_resource_json=$(wait_for_new_scene_resource_ready "$scene_id" "video" "$existing_ids_json" 80 3) || return 1
  selected_resource_json=$(wait_for_selected_scene_resource "$scene_id" "$(printf '%s' "$selected_resource_json" | jq -r '.resourceId')" "video" 40 3) || return 1
  prompt_json=$(get_scene_prompt_detail "$scene_id") || return 1

  printf '%s\n%s' "$selected_resource_json" "$prompt_json" | jq -sc --arg taskId "$task_id" '
    .[0] as $resource
    | .[1].data as $detail
    | {
        taskId: $taskId,
        sceneId: ($detail.video.sceneId // $resource.sceneId // ""),
        selectedVideoResourceId: ($resource.resourceId // ""),
        videoPlayUrl: ($resource.videoPlayUrl // (if ($resource.url // "") != "" then ("https://ai.fun.tv/static/videoPreview.html?url=" + (($resource.url // "")|@uri)) else "" end)),
        videoCover: ($resource.videoCover // ""),
        prompt: ($detail.video.prompt // ""),
        cameraPrompt: ($detail.video.cameraPrompt // ""),
        model: ($detail.video.model // ""),
        imageId: ($detail.video.imageId // "")
      }
  '
}

get_final_video_resource_info() {
  local resource_id="$1"
  local resource_json

  resource_json=$(get_resource "$resource_id") || return 1
  printf '%s' "$resource_json" | jq -c '
    .data as $res
    | {
        resourceId: ($res.id // ""),
        category: ($res.category // ""),
        type: ($res.type // ""),
        cover: ($res.data.cover // ""),
        videoPlayUrl: ($res.data.videoPlayUrl // (if ($res.data.url // "") != "" then ("https://ai.fun.tv/static/videoPreview.html?url=" + (($res.data.url // "")|@uri)) else "" end)),
        duration: ($res.data.duration // ""),
        fileType: ($res.data.fileType // "")
      }
  '
}

prepare_video_composite() {
  local project_id="$1"
  local chapter_num="${2:-1}"
  local payload

  require_setup_ready || return 1

  payload=$(jq -cn --arg projectId "$project_id" --argjson chapterNum "$chapter_num" '{projectId:$projectId, chapterNum:$chapterNum}')
  api_request_checked POST "/storyboard/prepareVideoComposite" "$payload"
}

get_video_setting() {
  local project_id="$1"
  local chapter_num="${2:-1}"
  api_request_checked GET "/storyboard/getVideoSetting?userProjectId=${project_id}&type=2&chapterNum=${chapter_num}"
}

save_video_compose_config_from_project() {
  local project_id="$1"
  local chapter_num="${2:-1}"
  local settings_json
  local payload

  require_setup_ready || return 1

  settings_json=$(get_video_setting "$project_id" "$chapter_num") || return 1
  payload=$(printf '%s' "$settings_json" | jq -c --arg projectId "$project_id" --argjson chapterNum "$chapter_num" '
    .data as $data
    | ($data.coverList // []) as $coverList
    | ($data.selectCover // ($coverList[0].coverId // empty)) as $selectCover
    | ($data.selectCoverUrl // ($coverList[]? | select(.coverId == $selectCover) | .coverUrl) // ($coverList[0].coverUrl // "")) as $selectCoverUrl
    | {
        selectCover: $selectCover,
        coverList: $coverList,
        selectMusicId: ($data.selectMusicId // "prepared-001"),
        selectTitleFont: ($data.selectTitleFont // "font0"),
        selectSubtitleFont: ($data.selectSubtitleFont // "font1"),
        title: ($data.title // "AI漫剧"),
        bgmVolume: ($data.bgmVolume // 0.15),
        type: 2,
        chapterNum: $chapterNum,
        userProjectId: $projectId,
        selectCoverUrl: $selectCoverUrl
      }
  ')

  api_request_checked POST "/storyboard/saveVideoComposeConfig" "$payload"
}

check_batch_ai_video() {
  local storyboard_id="$1"
  local payload

  payload=$(jq -cn --arg storyBoardId "$storyboard_id" '{storyBoardId:$storyBoardId}')
  api_request_checked POST "/storyboard/check/batchAiVideo" "$payload"
}

compose_video() {
  local project_id="$1"
  local chapter_num="${2:-1}"
  local clarity="${3:-720p}"
  local need_ai_watermark="${4:-1}"
  local payload

  require_setup_ready || return 1

  payload=$(jq -cn \
    --arg projectId "$project_id" \
    --argjson chapterNum "$chapter_num" \
    --arg clarity "$clarity" \
    --arg watermark "$need_ai_watermark" \
    '{
      userProjectId: $projectId,
      step: "novel_chapter_video",
      inputs: [
        {type:"number", name:"chapterNum", value:$chapterNum},
        {type:"text", name:"needAiWatermark", value:$watermark},
        {type:"text", name:"clarity", value:$clarity}
      ]
    }')

  api_request_checked POST "/project/step/action" "$payload"
}

main() {
  require_jq
  load_config

  case "${1:-}" in
    check)
      check_auth && echo -e "${GREEN}Token 有效${NC}"
      ;;
    setup-check)
      print_setup_status
      ;;
    get)
      shift
      api_request_checked GET "$@"
      ;;
    post)
      shift
      if [ "${ALLOW_UNSAFE_RAW_POST:-}" != "YES" ]; then
        echo -e "${RED}错误: 原始 post 命令已标记为 debug-only，默认禁用${NC}" >&2
        echo "请优先使用 create_project / next_step / modify_role_image / compose_video 等高层 helper。" >&2
        echo "如需调试底层接口，请显式设置: ALLOW_UNSAFE_RAW_POST=YES" >&2
        exit 1
      fi
      echo -e "${YELLOW}警告: 你正在使用未受高层业务护栏约束的原始 POST 调试入口${NC}" >&2
      api_request_checked POST "$1" "${2:-}"
      ;;
    poll)
      poll_task "$2" "${3:-60}" "${4:-3}"
      ;;
    select-options)
      get_select_options "${2:-1}"
      ;;
    project-link)
      project_link "$2"
      ;;
    prev-step)
      prev_step "$2" "$3" "${4:-1}"
      ;;
    ensure-scenes-step)
      ensure_chapter_scenes_step "$2" "${3:-1}"
      ;;
    scene-resources)
      get_scene_resources "$2"
      ;;
    role-resources)
      get_role_resources "$2"
      ;;
    current-step)
      get_project "$2" | jq -r '.data.workflow.currentStep // empty'
      ;;
    video-play-url)
      to_video_play_url "$2"
      ;;
    storyboard-scenes)
      build_storyboard_scene_summaries "$2"
      ;;
    batch-scene-prompt-details)
      build_scene_review_manifest "$2" | jq '[.[] | {sceneIndex, sceneId, sceneName, imagePromptInfo, videoPromptInfo}]'
      ;;
    download-scene-images)
      download_storyboard_scene_images "$2" "$3"
      ;;
    batch-refine-scene-images)
      batch_refine_scene_images_from_file "$2" "$3" "${4:-1}"
      ;;
    modify-role-image)
      modify_role_image "$2" "$3" "$4"
      ;;
    scene-prompt-detail)
      get_scene_prompt_detail "$2"
      ;;
    scene-image-payload)
      build_scene_image_payload "$2" "${3:-}" "${4:-}"
      ;;
    scene-image)
      refine_scene_image "$2" "$3" "$4" "$5" "${6:-1}"
      ;;
    scene-video-payload)
      build_scene_video_payload "$2" "${3:--1}" "${4:-720p}" "${5:-}" "${6:-}" "${7:-}" "${8:-}"
      ;;
    scene-video)
      refine_scene_video "$2" "$3" "$4" "$5" "${6:-1}" "${7:--1}" "${8:-720p}" "${9:-}" "${10:-}"
      ;;
    final-video-resource)
      get_final_video_resource_info "$2"
      ;;
    *)
      cat <<EOF
用法: $0 <command> [args]

 命令:
   check                        检查 Token 是否有效
   setup-check                  检查 setup/version 前置条件
   get <endpoint>               发送 GET 请求（要求 code=200）
   post <endpoint> <json>       debug-only：发送原始 POST 请求（默认禁用）
  poll <task_id> [n] [sec]     轮询任务状态
  select-options [type]        获取创建项目可选项，默认 type=1
  project-link <project_id>    输出项目链接
  prev-step <project> <step> [chapter]
                              执行步骤回退
   ensure-scenes-step <project> [chapter]
                               若项目在成片步骤，则自动回退到分镜图步骤
    role-resources <role_id>     获取单个角色的候选图片资源列表
    current-step <project_id>    输出项目当前 workflow.currentStep
    video-play-url <raw_url>     将原始视频 url 规范化为可直接播放的 videoPlayUrl
    storyboard-scenes <storyboard_id>
                               输出 storyboard 下所有 scene 的摘要（视频只给 videoPlayUrl）
    batch-scene-prompt-details <storyboard_id>
                               批量读取 storyboard 下各 scene 的 prompt/detail 摘要
    download-scene-images <storyboard_id> <output_dir>
                               批量下载各 scene 当前代表性图片，便于 AI 审图
    batch-refine-scene-images <project> <spec_file> [chapter]
                               读取 JSON 文件批量重生图，并汇总旧图/新图/任务ID
    modify-role-image <project> <role_id|name> <description>
                               在角色与配音步骤修改角色形象，等待新图完成并应用
    scene-resources <scene_id>   获取场景资源列表
    scene-image-payload <scene_id> [sceneDescription] [prompt]
                               构造单场景重生图 payload（sceneDescription + prompt）
    scene-image <project> <scene_id> <sceneDescription> <prompt> [chapter]
                               在分镜图步骤重生单场景图片，并返回最终选中的图片
   scene-prompt-detail <scene_id>
                               获取场景 prompt / 视频配置详情
   scene-video-payload <scene_id> [duration] [clarity] [tail] [prompt] [cameraPrompt] [model]
                               使用当前 scene 的基准分镜图构造图转视频 payload
   scene-video <project> <scene_id> <prompt> <cameraPrompt> [chapter] [duration] [clarity] [tail] [model]
                               在分镜图步骤重生单场景视频，并返回最终选中的视频
   final-video-resource <resource_id>
                               读取最终成片视频资源摘要（含 videoPlayUrl）

内置函数（供 source scripts/api-client.sh 后复用）:
  - get_select_options
  - create_project / create_project_with_defaults
  - submit_novel
  - next_step
  - get_project / get_roles / get_preset / get_resource / get_task
  - get_role_resources / modify_role_image
  - wait_for_roles_ready
  - build_extract_roles_inputs
  - wait_for_preset_chapter_status
  - resolve_storyboard_id
  - prev_step / ensure_chapter_scenes_step
  - guard_step_not_already_passed
  - get_storyboard_scene / get_storyboard_scenes / build_storyboard_scene_summaries
  - get_scene_resources / get_scene_prompt_detail / get_scene_image_resource
  - build_scene_review_manifest / download_storyboard_scene_images / batch_refine_scene_images_from_file
  - build_scene_image_payload / refine_scene_image
  - build_scene_video_payload / refine_scene_video / get_final_video_resource_info
  - prepare_video_composite / get_video_setting / save_video_compose_config_from_project
  - check_batch_ai_video
  - compose_video

 注意:
   0. setup-check 会读取远端 setup-skill.md，并校验本地 VERSION 是否满足要求。
   0.5. 如果是 `source scripts/api-client.sh` 后复用内置函数，必须先显式调用 `load_config`（必要时也先调用 `require_jq`）。
   0.6. 原始 `post` 调试入口不会自动补上高层业务护栏；默认禁用，仅限显式设置 `ALLOW_UNSAFE_RAW_POST=YES` 时使用。
   1. 创建项目必须先调 select-options，再使用接口返回值。
   2. 不要把 scene-list 返回的 sceneUuid 当作 sceneId。
   3. 不要只看 workflow.currentStep，还要检查 comicPreset.data.chapters[] 中的隐藏任务状态。
   3.5. 调用 next_step 前，helper 会先检查项目是否已经自动前进到目标步骤之后；如果已经越过，就不要重放旧步骤。
   4. scene/ai/video 必须使用 scene 当前基准分镜图资源（优先 video.imageId 对应 image），而不是角色图。
   5. 角色形象修改只允许在 novel_extract_roles（角色与配音）步骤执行；生成成功后还必须 apply 新图才算完成。
   6. scene/ai/image 的真实提示词由 sceneDescription + prompt 共同组成；其中 prompt 可以包含 @人物(id:xxxx) 保持一致性。
   7. scene/ai/video 的 prompt / cameraPrompt 分别对应动作 / 运镜；这里不要再使用 @人物插入，直接写纯文本动作和镜头描述。
   8. scene 视频和最终成片对外统一只返回 videoPlayUrl；不要在高层 helper / 示例输出里暴露原始视频 url。
EOF
      ;;
  esac
}

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
  main "$@"
fi
