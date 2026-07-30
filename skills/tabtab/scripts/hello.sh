#!/bin/bash
_D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; [ -f "$_D/env" ] && source "$_D/env"
# 验证 API Key 连通性
#
# 用法：
#   bash hello.sh
#
# 环境变量：
#   TABTAB_API_KEY   必填  sk-… API Key
#   TABTAB_BASE_URL  可选  默认 https://tabtabai.com

set -e

BASE="${TABTAB_BASE_URL:-https://tabtabai.com}"
KEY="${TABTAB_API_KEY:?请设置 TABTAB_API_KEY}"

curl -s "$BASE/open/apis/v1/hello" \
    -H "Authorization: Bearer $KEY"
