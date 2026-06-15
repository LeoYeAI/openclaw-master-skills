#!/bin/bash
# Team Dispatch verification suite (PASS/FAIL)
#
# Usage:
#   bash <SKILL_DIR>/scripts/verify.sh
#   SKIP_SETUP=1 bash <SKILL_DIR>/scripts/verify.sh
#   SKIP_CRON=1 bash <SKILL_DIR>/scripts/verify.sh
#   SKIP_WATCH_SIM=1 bash <SKILL_DIR>/scripts/verify.sh
#
# Notes:
# - Non-destructive by default.
# - It may create temporary files under ~/.openclaw/workspace/tasks/active/ and then removes them.

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TASKS_DIR="$HOME/.openclaw/workspace/tasks"
OPENCLAW_JSON="$HOME/.openclaw/openclaw.json"
TD_CFG="$HOME/.openclaw/configs/team-dispatch.json"

RED="\033[31m"; GREEN="\033[32m"; YELLOW="\033[33m"; NC="\033[0m"

pass() { echo -e "${GREEN}PASS${NC} $*"; }
warn() { echo -e "${YELLOW}WARN${NC} $*"; }
fail() { echo -e "${RED}FAIL${NC} $*"; exit 1; }

need_cmd() { command -v "$1" >/dev/null 2>&1 || fail "missing command: $1"; }

SKIP_SETUP="${SKIP_SETUP:-0}"
SKIP_CRON="${SKIP_CRON:-0}"
SKIP_WATCH_SIM="${SKIP_WATCH_SIM:-0}"

need_cmd openclaw
need_cmd node
need_cmd python3

echo "== Team Dispatch verify =="
echo "SKILL_DIR=$SKILL_DIR"

# 1) setup.sh idempotency
if [ "$SKIP_SETUP" = "1" ]; then
  warn "SKIP_SETUP=1 (skipping setup.sh run)"
else
  echo "\n[1] Running setup.sh (idempotent)"

# Required assets sanity-check (important for Clawhub packaging)
need_file() {
  local p="$1"
  if [ ! -f "$p" ]; then
    echo "${RED}FAIL${NC}: missing required file: $p"
    exit 1
  fi
}
need_file "$SKILL_DIR/assets/launchd/openclaw.team-dispatch.watch.plist.xml"
need_file "$SKILL_DIR/assets/windows/watch-install.ps1.txt"
  bash "$SKILL_DIR/scripts/setup.sh" >/tmp/team-dispatch.verify.setup.log 2>&1 || {
    tail -120 /tmp/team-dispatch.verify.setup.log >&2 || true
    fail "setup.sh failed (see /tmp/team-dispatch.verify.setup.log)"
  }
  pass "setup.sh ok"
fi

# 2) symlink
echo "\n[2] Skill symlink"
if [ -L "$HOME/.openclaw/skills/team-dispatch" ]; then
  TARGET="$(readlink "$HOME/.openclaw/skills/team-dispatch")"
  pass "symlink exists -> $TARGET"
else
  fail "missing symlink: ~/.openclaw/skills/team-dispatch"
fi

# 3) tasks dirs
echo "\n[3] tasks dirs + template"
for d in active done templates; do
  [ -d "$TASKS_DIR/$d" ] || fail "missing dir: $TASKS_DIR/$d"
  pass "$TASKS_DIR/$d"
done
[ -f "$TASKS_DIR/templates/project.json" ] || fail "missing template: $TASKS_DIR/templates/project.json"
pass "project.json template exists"

# 4) config
echo "\n[4] team-dispatch.json"
[ -f "$TD_CFG" ] || fail "missing config: $TD_CFG"
node -e "JSON.parse(require('fs').readFileSync('$TD_CFG','utf8'));" || fail "invalid JSON: $TD_CFG"
pass "config json valid"

# 5) openclaw.json main + workers
echo "\n[5] openclaw.json agents.list"
node - <<'NODE'
const fs=require('fs');
const p=process.env.HOME+'/.openclaw/openclaw.json';
const j=JSON.parse(fs.readFileSync(p,'utf8'));
const list=j.agents?.list||[];
// worker ids come from config (fallback to defaults)
let td={};
try{
  const up=process.env.HOME+'/.openclaw/configs/team-dispatch.json';
  const sp=process.env.HOME+'/.openclaw/skills/team-dispatch/config.json';
  const p=fs.existsSync(up)?up:sp;
  td=JSON.parse(fs.readFileSync(p,'utf8'));
}catch(e){}
const workerIds = Object.keys(td?.team?.agents||{});
const order=['coder','product','tester','research','trader','writer'];
const set=new Set(workerIds.length?workerIds:order);
const workers=order.filter(x=>set.has(x));
for(const k of workerIds) if(!workers.includes(k)) workers.push(k);

const ids=['main', ...workers];
const missing=ids.filter(id=>!list.find(x=>x.id===id));
if(missing.length){
  console.error('missing agents:', missing.join(', '));
  process.exit(2);
}
const main=list.find(x=>x.id==='main');
if(!main.subagents || !Array.isArray(main.subagents.allowAgents) || main.subagents.allowAgents.length===0){
  console.error('main.subagents.allowAgents missing');
  process.exit(3);
}
if(!main.subagents.allowAgents.includes('*')){
  console.error('main.subagents.allowAgents does not include *');
  process.exit(4);
}
console.log('ok');
NODE
pass "agents.list contains main+workers and main.allowAgents includes *"

# 6) workspace files
echo "\n[6] agent workspaces"
REQ_FILES=(AGENTS.md SOUL.md IDENTITY.md USER.md TOOLS.md)
for a in coder product tester research trader writer; do
  ws="$HOME/.openclaw/agents/$a/workspace"
  [ -d "$ws" ] || fail "$a workspace dir missing: $ws"
  missing=""
  for f in "${REQ_FILES[@]}"; do
    [ -f "$ws/$f" ] || missing="$missing $f"
  done
  if [ -n "$missing" ]; then
    fail "$a workspace missing:$missing"
  fi
  [ -d "$HOME/.openclaw/agents/$a/sessions" ] || warn "$a sessions missing (will be created at runtime)"
  pass "$a workspace ok"
done

# 7) cron watcher preferred
if [ "$SKIP_CRON" = "1" ]; then
  warn "SKIP_CRON=1 (skipping OpenClaw cron checks)"
else
  echo "\n[7] OpenClaw cron watcher"
  openclaw cron status >/dev/null 2>&1 || fail "openclaw cron status failed"
  pass "cron status ok"

  # find job
  JOB_JSON=$(openclaw cron list --json 2>/dev/null)
  JOB_ID=$(printf %s "$JOB_JSON" | node -e "
    let s='';process.stdin.on('data',d=>s+=d);process.stdin.on('end',()=>{
      const j=JSON.parse(s);const jobs=j.jobs||j;
      let td={};
      try{
        const fs2=require('fs');
        const up=process.env.HOME+'/.openclaw/configs/team-dispatch.json';
        const sp=process.env.HOME+'/.openclaw/skills/team-dispatch/config.json';
        const p=fs2.existsSync(up)?up:sp;
        td=JSON.parse(fs2.readFileSync(p,'utf8'));
      }catch(e){}
      const name=String(td.team?.watcher?.jobName||'Team Dispatch watcher');
      const hit=(jobs||[]).find(x=>x.name===name);
      process.stdout.write(hit?.jobId||hit?.id||'');
    });")

  if [ -z "$JOB_ID" ]; then
    # attempt install (auto)
    INTERVAL=300 GRACE=20 bash "$SKILL_DIR/scripts/watch-install.sh" --backend auto >/tmp/team-dispatch.verify.watch-install.log 2>&1 || true
    JOB_JSON=$(openclaw cron list --json 2>/dev/null)
    JOB_ID=$(printf %s "$JOB_JSON" | node -e "
      let s='';process.stdin.on('data',d=>s+=d);process.stdin.on('end',()=>{
        const j=JSON.parse(s);const jobs=j.jobs||j;
        let td={};
        try{
          const fs2=require('fs');
          const up=process.env.HOME+'/.openclaw/configs/team-dispatch.json';
          const sp=process.env.HOME+'/.openclaw/skills/team-dispatch/config.json';
          const p=fs2.existsSync(up)?up:sp;
          td=JSON.parse(fs2.readFileSync(p,'utf8'));
        }catch(e){}
        const name=String(td.team?.watcher?.jobName||'Team Dispatch watcher');
        const hit=(jobs||[]).find(x=>x.name===name);
        process.stdout.write(hit?.jobId||hit?.id||'');
      });")
  fi

  [ -n "$JOB_ID" ] || fail "cron job not found: Team Dispatch watcher"
  pass "cron watcher exists: $JOB_ID"
fi

# 8) simulate overdue reset pending
if [ "$SKIP_WATCH_SIM" = "1" ]; then
  warn "SKIP_WATCH_SIM=1 (skipping watch.py overdue simulation)"
else
  echo "\n[8] watch.py overdue simulation (reset to pending)"
  SIM="$TASKS_DIR/active/timeout-sim.json"
  python3 - <<'PY'
import json, os
from datetime import datetime, timezone, timedelta
TZ = timezone(timedelta(hours=8))
started = (datetime.now(TZ) - timedelta(hours=1)).isoformat(timespec='seconds')

data = {
  'project': 'timeout-sim',
  'goal': 'simulate overdue task reset to pending',
  'created': datetime.now(TZ).isoformat(timespec='seconds'),
  'status': 'active',
  'retryLimit': 1,
  'tasks': [
    {
      'id': 't1',
      'agentId': 'tester',
      'description': 'simulate a stuck in-progress task',
      'status': 'in-progress',
      'dependsOn': [],
      'timeoutSeconds': 1,
      'result': '',
      'error': '',
      'retries': 0,
      'startedAt': started,
      'completedAt': None,
      'sessionKey': 'fake-session-key'
    }
  ]
}

p = os.path.expanduser('~/.openclaw/workspace/tasks/active/timeout-sim.json')
os.makedirs(os.path.dirname(p), exist_ok=True)
with open(p, 'w', encoding='utf-8') as f:
  json.dump(data, f, ensure_ascii=False, indent=2)
print('wrote', p)
PY

  python3 "$HOME/.openclaw/skills/team-dispatch/scripts/watch.py" --once --tasks-dir "$TASKS_DIR" --grace 0 >/tmp/team-dispatch.verify.watch-sim.log 2>&1 || {
    cat /tmp/team-dispatch.verify.watch-sim.log >&2
    rm -f "$SIM" || true
    fail "watch.py simulation run failed"
  }

  python3 - <<'PY'
import json, os
p=os.path.expanduser('~/.openclaw/workspace/tasks/active/timeout-sim.json')
j=json.load(open(p,'r',encoding='utf-8'))
t=j['tasks'][0]
assert t['retries']==1, t
assert t['status']=='pending', t
assert t['startedAt'] is None, t
assert t['sessionKey'] is None, t
assert 'timeout' in (t.get('error') or ''), t
assert j.get('status')=='active', j
print('ok')
PY

  rm -f "$SIM" || true
  pass "watch.py resets overdue task to pending"
fi

echo "\n✅ ALL CHECKS PASSED"
