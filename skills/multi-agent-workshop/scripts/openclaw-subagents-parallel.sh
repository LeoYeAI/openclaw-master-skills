#!/usr/bin/env bash
# 调整 OpenClaw openclaw.json 中 agents.defaults.subagents.maxConcurrent
# 「关闭」= 设为 1（禁止并行 subagent，一次只跑一个；不删 subagents 块，避免未知兼容问题）
#
# 用法（可chmod +x 后执行）:
#   bash openclaw-subagents-parallel.sh status
#   bash openclaw-subagents-parallel.sh off          # maxConcurrent -> 1
#   bash openclaw-subagents-parallel.sh on [N]      # 恢复并行，默认 N=8
#   OPENCLAW_JSON=/path/to/openclaw.json bash ... off
#
# 依赖: python3
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_ROOT="$(cd "$SKILL_DIR/../.." && pwd)"
DEFAULT_JSON="$(cd "$WORKSPACE_ROOT/.." && pwd)/openclaw.json"
OPENCLAW_JSON="${OPENCLAW_JSON:-$DEFAULT_JSON}"

die() { echo "openclaw-subagents-parallel.sh: $*" >&2; exit 1; }

cmd="${1:-status}"
val_on="${2:-8}"

[[ -f "$OPENCLAW_JSON" ]] || die "找不到配置文件: $OPENCLAW_JSON（可设置环境变量 OPENCLAW_JSON）"

backup() {
  local ts
  ts="$(date +%Y%m%d-%H%M%S)"
  cp -a "$OPENCLAW_JSON" "${OPENCLAW_JSON}.bak.${ts}"
  echo "已备份 -> ${OPENCLAW_JSON}.bak.${ts}"
}

read_current() {
  python3 - <<PY
import json
p = r"""$OPENCLAW_JSON"""
with open(p, encoding="utf-8") as f:
    d = json.load(f)
sub = d.get("agents", {}).get("defaults", {}).get("subagents", {})
print(sub.get("maxConcurrent", "(未设置 subagents.maxConcurrent)"))
PY
}

case "$cmd" in
  status)
    echo "文件: $OPENCLAW_JSON"
    echo -n "subagents.maxConcurrent = "
    read_current
    ;;
  off|disable)
    backup
    python3 - <<PY
import json
path = r"""$OPENCLAW_JSON"""
with open(path, encoding="utf-8") as f:
    d = json.load(f)
agents = d.setdefault("agents", {}).setdefault("defaults", {})
sub = agents.setdefault("subagents", {})
old = sub.get("maxConcurrent")
sub["maxConcurrent"] = 1
with open(path, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"已关闭并行: subagents.maxConcurrent {old!r} -> 1")
PY
    echo "请重启 OpenClaw 或重载配置使生效（若客户端会缓存配置）。"
    ;;
  on|enable)
    backup
    python3 - <<PY
import json, sys
path = r"""$OPENCLAW_JSON"""
n = int(r"""$val_on""")
if n < 1:
    raise SystemExit("N 须 >= 1")
with open(path, encoding="utf-8") as f:
    d = json.load(f)
agents = d.setdefault("agents", {}).setdefault("defaults", {})
sub = agents.setdefault("subagents", {})
old = sub.get("maxConcurrent")
sub["maxConcurrent"] = n
with open(path, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"已恢复并行: subagents.maxConcurrent {old!r} -> {n}")
PY
    echo "请重启 OpenClaw 或重载配置使生效（若客户端会缓存配置）。"
    ;;
  help|-h|--help)
    sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
    ;;
  *)
    die "用法: $0 status | off | on [N] | help"
    ;;
esac
