#!/bin/bash
# Generate a demo DAG project JSON under ~/.openclaw/workspace/tasks/active/
# This is a *local smoke test* for the Team Dispatch workflow (DAG file → dispatch → writeback → archive).
#
# Usage:
#   bash <SKILL_DIR>/scripts/demo-project.sh
#   PROJECT_ID=team-mvp-1 bash <SKILL_DIR>/scripts/demo-project.sh
#
# Output:
#   ~/.openclaw/workspace/tasks/active/<projectId>.json

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="$SKILL_DIR/assets/templates/project.json"
OUT_DIR="$HOME/.openclaw/workspace/tasks/active"

PROJECT_ID="${PROJECT_ID:-team-mvp-1}"
TS="$(date +%Y%m%d-%H%M%S)"
PROJECT_KEY="$PROJECT_ID-$TS"
OUT="$OUT_DIR/$PROJECT_KEY.json"

mkdir -p "$OUT_DIR"

TEMPLATE="$TEMPLATE" OUT="$OUT" PROJECT_KEY="$PROJECT_KEY" python3 - <<PY
import json, os, datetime

template_path = os.environ.get('TEMPLATE')
out_path = os.environ.get('OUT')
project_key = os.environ.get('PROJECT_KEY')

with open(template_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

def iso():
    # local time is fine here; watcher/parser uses fromisoformat
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()

data['project'] = project_key
data['goal'] = '协作开发测试：CLI Todo 工具（add/list/done + todos.json 持久化 + 测试 + 文档）'
data['created'] = iso()
data['language'] = 'zh'
data['retryLimit'] = 1

# DAG from product spec (T1→T2→T3; T3→T4,T5; T4&T5→T6)
tasks = [
  {
    'id': 't1-design',
    'agentId': 'product',
    'description': '需求澄清与接口设计：定义 CLI 命令（add/list/done/--help）与 todos.json schema，并列出关键边界行为。',
    'status': 'pending',
    'dependsOn': [],
    'onFailure': 'block',
    'timeoutSeconds': 600,
  },
  {
    'id': 't2-scaffold',
    'agentId': 'coder',
    'description': '初始化项目骨架：可运行的 CLI 入口与测试脚本；确保在干净环境可执行并输出 --help。',
    'status': 'pending',
    'dependsOn': ['t1-design'],
    'onFailure': 'block',
    'timeoutSeconds': 900,
  },
  {
    'id': 't3-core',
    'agentId': 'coder',
    'description': '实现核心功能：add/list/done + todos.json 持久化（文件不存在/存在都可用）；非法 id 返回非0并输出错误。',
    'status': 'pending',
    'dependsOn': ['t2-scaffold'],
    'onFailure': 'block',
    'timeoutSeconds': 1200,
  },
  {
    'id': 't4-tests',
    'agentId': 'tester',
    'description': '补齐单元测试：添加成功、完成成功/非法id、空文件初始化、list 输出包含新增项；测试不污染真实数据。',
    'status': 'pending',
    'dependsOn': ['t3-core'],
    'onFailure': 'block',
    'timeoutSeconds': 900,
  },
  {
    'id': 't5-docs',
    'agentId': 'writer',
    'description': '编写 README：安装、三条核心命令示例、todos.json 位置与格式、完整演示流程（add→list→done→list）。',
    'status': 'pending',
    'dependsOn': ['t3-core'],
    'onFailure': 'block',
    'timeoutSeconds': 600,
  },
  {
    'id': 't6-e2e',
    'agentId': 'tester',
    'description': '集成验收：删除 todos.json 从0跑通演示流程；npm/pnpm test 全绿；CLI 返回码符合成功/失败预期。',
    'status': 'pending',
    'dependsOn': ['t4-tests', 't5-docs'],
    'onFailure': 'block',
    'timeoutSeconds': 900,
  },
]

# Normalize task fields to match template schema
base = data['tasks'][0]
normalized = []
for t in tasks:
    nt = dict(base)
    nt.update(t)
    nt.setdefault('result', '')
    nt.setdefault('error', '')
    nt.setdefault('retries', 0)
    nt.setdefault('startedAt', None)
    nt.setdefault('completedAt', None)
    nt.setdefault('sessionKey', None)
    normalized.append(nt)

data['tasks'] = normalized

data['deliverables'] = [
  {'id': 'todos-cli', 'type': 'cli', 'path': '<repo>/'},
  {'id': 'readme', 'type': 'doc', 'path': '<repo>/README.md'},
  {'id': 'tests', 'type': 'test', 'path': '<repo>/'}
]

data['summary'] = ''
data['finalMessage'] = ''

with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(out_path)
PY

echo "✅ Demo project generated: $OUT"
echo "Next: ask main agent to run it (Team Dispatch dispatch/writeback/archive)."
