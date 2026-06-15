#!/bin/bash
# Team Dispatch 一键安装脚本
# 用法:
#   bash ~/skills/team-dispatch/scripts/setup.sh
#   bash ~/skills/team-dispatch/scripts/setup.sh --baseline-models
#
# 本脚本自动完成所有配置，无需手动操作：
#   1. 创建软连接
#   2. 创建任务目录 + 复制模板
#   3. 生成用户配置（team-dispatch.json）
#   4. 为每个子 Agent 创建独立 agentDir（~/.openclaw/agents/<id>），包含完整 workspace 模板
#   5. 将 7 个子 Agent 写入 openclaw.json（含 workspace/identity/model）
#   6. 重启 Gateway 使配置生效

set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OPENCLAW_JSON="$HOME/.openclaw/openclaw.json"

BASELINE_MODELS=0
NO_WATCH=0

for arg in "$@"; do
  case "$arg" in
    --baseline-models) BASELINE_MODELS=1 ;;
    --no-watch) NO_WATCH=1 ;;
  esac
done

TD_VERSION=$(node -e "const fs=require('fs');try{const j=JSON.parse(fs.readFileSync('$SKILL_DIR/config.json','utf8'));process.stdout.write(String(j.version||''));}catch(e){process.stdout.write('');}")
echo "🚀 Team Dispatch v${TD_VERSION:-unknown} — 一键安装开始"
echo "   Args: ${*:-<none>}"
echo ""

# ─── Backup (for uninstall/restore) ───
TS="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="$HOME/.openclaw/backups/team-dispatch"
BACKUP_DIR="$BACKUP_ROOT/$TS"
mkdir -p "$BACKUP_DIR"
if [ -f "$OPENCLAW_JSON" ]; then
  cp "$OPENCLAW_JSON" "$BACKUP_DIR/openclaw.json.bak"
fi
if [ -f "$HOME/.openclaw/configs/team-dispatch.json" ]; then
  cp "$HOME/.openclaw/configs/team-dispatch.json" "$BACKUP_DIR/team-dispatch.json.bak"
fi
# record latest
echo "$BACKUP_DIR" > "$BACKUP_ROOT/latest"


# ─── 前置检查 ───
if ! command -v openclaw &> /dev/null; then
    echo "❌ 未找到 openclaw，请先安装"
    exit 1
fi
echo "✅ OpenClaw 已安装: $(openclaw --version 2>/dev/null || echo 'unknown')"

if ! command -v node &> /dev/null; then
    echo "❌ 未找到 node，请先安装 Node.js"
    exit 1
fi

# ─── Step 1: 软连接 ───
echo ""
echo "🔗 Step 1: 软连接..."
mkdir -p ~/.openclaw/skills
if [ ! -L ~/.openclaw/skills/team-dispatch ]; then
    ln -s "$SKILL_DIR" ~/.openclaw/skills/team-dispatch
    echo "   ✅ 软连接已创建"
else
    echo "   ⏭️  软连接已存在"
fi

# ─── Step 2: 任务目录 + 模板 ───
echo ""
echo "📁 Step 2: 任务目录 + 模板..."
mkdir -p ~/.openclaw/workspace/tasks/{active,done,templates}
cp "$SKILL_DIR/assets/templates/project.json" ~/.openclaw/workspace/tasks/templates/
echo "   ✅ tasks/{active,done,templates}/ + project.json 模板"

# Ensure projects root directory exists (real code space). Config-driven: paths.projectsRoot, default ~/work.
PROJECTS_ROOT=$(node -e "
  const fs=require('fs');
  const home=process.env.HOME;
  const up=home+'/.openclaw/configs/team-dispatch.json';
  const sp='$SKILL_DIR/config.json';
  let j={};
  try{ const p=fs.existsSync(up)?up:sp; j=JSON.parse(fs.readFileSync(p,'utf8')); }catch(e){}
  process.stdout.write(String(j.paths?.projectsRoot||'~/work'));
")
# Expand leading ~/ (do NOT rely on shell tilde expansion, because the value is quoted)
if [[ "$PROJECTS_ROOT" == \~/* ]]; then
  PROJECTS_ROOT="$HOME/${PROJECTS_ROOT#\~\/}"
fi
mkdir -p "$PROJECTS_ROOT"
echo "   ✅ projectsRoot: $PROJECTS_ROOT"

# ─── Step 3: 用户配置 ───
echo ""
echo "🧩 Step 3: 用户配置..."
bash "$SKILL_DIR/scripts/setup-config.sh" || true

# ─── Step 4: 子 Agent agentDir（完整模板复制） ───
echo ""
echo "🏠 Step 4: 子 Agent 独立 agentDir（~/.openclaw/agents/<id>）..."

# Agents roster comes from config when available; fallback to the default 6.
# NOTE: macOS ships bash 3.2 by default (no `mapfile`). Use a compatible read loop.
AGENTS=()
while IFS= read -r _agent; do
  [ -n "$_agent" ] && AGENTS+=("$_agent")
done < <(node -e "
  const fs=require('fs');
  const home=process.env.HOME;
  const userP=home+'/.openclaw/configs/team-dispatch.json';
  const skillP='$SKILL_DIR/config.json';
  let j={};
  // Prefer user override; else fall back to skill root config.json
  try{
    if (fs.existsSync(userP)) j=JSON.parse(fs.readFileSync(userP,'utf8'));
    else if (fs.existsSync(skillP)) j=JSON.parse(fs.readFileSync(skillP,'utf8'));
  }catch(e){ j={}; }

  const keys = Object.keys(j?.team?.agents||{});
  const order = ['coder','product','tester','research','trader','writer'];
  const set = new Set(keys.length?keys:order);
  const out = order.filter(x=>set.has(x));
  for (const k of keys) if (!out.includes(k)) out.push(k);
  process.stdout.write(out.join('\n'));
")

for agent in "${AGENTS[@]}"; do
    # 全新安装逻辑：cp -R assets/agents/<id> → ~/.openclaw/agents/<id>
    agent_dir="$HOME/.openclaw/agents/$agent"
    template_dir="$SKILL_DIR/assets/agents/$agent"
    template_ws="$template_dir/workspace"

    if [ -d "$template_ws" ]; then
        if [ ! -d "$agent_dir" ]; then
            mkdir -p "$HOME/.openclaw/agents"
            cp -R "$template_dir" "$agent_dir"
            mkdir -p "$agent_dir/sessions"  # 约定目录（运行时会写入）
            # marker file: safe for uninstall purge
            echo "managed-by=team-dispatch" > "$agent_dir/.team-dispatch-managed"
            echo "createdAt=$TS" >> "$agent_dir/.team-dispatch-managed"
            echo "   ✅ $agent → 已复制完整 agentDir 模板到 ~/.openclaw/agents/$agent"
        else
            # 已存在：只补齐 workspace 下缺失文件
            mkdir -p "$agent_dir/workspace"
            for f in "$template_ws"/*; do
                fname="$(basename "$f")"
                if [ ! -e "$agent_dir/workspace/$fname" ]; then
                    cp -R "$f" "$agent_dir/workspace/$fname"
                    echo "   🔧 $agent → 补齐 workspace/$fname"
                fi
            done
            if [ -d "$template_ws/.openclaw" ] && [ ! -d "$agent_dir/workspace/.openclaw" ]; then
                cp -R "$template_ws/.openclaw" "$agent_dir/workspace/.openclaw"
                echo "   🔧 $agent → 补齐 workspace/.openclaw/"
            fi
            mkdir -p "$agent_dir/sessions"
            echo "   ⏭️  $agent → agentDir 已存在，已补齐缺失文件"
        fi
    else
        # 回退：仅创建最小 workspace-coder 结构（旧兼容）
        ws="$HOME/.openclaw/workspace-$agent"
        mkdir -p "$ws"
        if [ ! -f "$ws/AGENTS.md" ] && [ -f "$SKILL_DIR/assets/agents/$agent.md" ]; then
            cp "$SKILL_DIR/assets/agents/$agent.md" "$ws/AGENTS.md"
            echo "   ✅ $agent → workspace + AGENTS.md（回退模式）"
        else
            echo "   ⏭️  $agent → 已存在（回退模式）"
        fi
    fi
done

# ─── Step 5: 写入 openclaw.json ───
echo ""
echo "👥 Step 5: 配置子 Agent 到 openclaw.json..."

node -e "
const fs = require('fs');
const path = '$OPENCLAW_JSON';
const tdUserPath = process.env.HOME + '/.openclaw/configs/team-dispatch.json';
const tdSkillPath = '$SKILL_DIR/config.json';

const config = JSON.parse(fs.readFileSync(path, 'utf8'));
const tdCfg = (() => {
  try {
    if (fs.existsSync(tdUserPath)) return JSON.parse(fs.readFileSync(tdUserPath, 'utf8'));
    if (fs.existsSync(tdSkillPath)) return JSON.parse(fs.readFileSync(tdSkillPath, 'utf8'));
  } catch (e) {}
  return {};
})();

if (!config.agents) config.agents = {};
if (!config.agents.list) config.agents.list = [];

const home = process.env.HOME;
const baseline = $BASELINE_MODELS;

const roster = tdCfg?.team?.agents || {};
const lang = tdCfg?.language || 'zh';

const getDisplayName = (id) => {
  const r = roster[id] || {};
  if (lang === 'zh') return r.displayNameCN || r.displayName || id;
  return r.displayName || r.displayNameCN || id;
};

const mainCfg = tdCfg?.team?.main || {};
const mainName = (lang === 'zh')
  ? (mainCfg.displayNameCN || mainCfg.displayName || 'main')
  : (mainCfg.displayName || mainCfg.displayNameCN || 'main');

const mainAgentPatch = {
  id: 'main',
  default: true,
  name: 'main',
  workspace: home + '/.openclaw/workspace',
  agentDir: home + '/.openclaw/agents/main/agent',
  model: mainCfg.model || 'openai-codex/gpt-5.4',
  identity: { name: mainName, emoji: mainCfg.emoji || '🎯' },
  subagents: { allowAgents: ['*'] },
};

// Ensure / patch main
{
  const idx = config.agents.list.findIndex(a => a.id === 'main');
  if (idx === -1) {
    config.agents.list.unshift(mainAgentPatch);
    console.log('   ✅ main → 新增（dispatcher/root）');
  } else {
    const existing = config.agents.list[idx];
    existing.subagents ??= {};
    if (!Array.isArray(existing.subagents.allowAgents) || existing.subagents.allowAgents.length === 0) {
      existing.subagents.allowAgents = ['*'];
      console.log('   🔧 main → 设置 subagents.allowAgents=["*"]');
    }
    if (!existing.workspace) { existing.workspace = mainAgentPatch.workspace; console.log('   🔧 main → 补齐 workspace'); }
    if (!existing.agentDir) { existing.agentDir = mainAgentPatch.agentDir; console.log('   🔧 main → 补齐 agentDir'); }
    if (baseline) {
      const before = (typeof existing.model === 'string') ? existing.model : (existing.model?.primary || '(unset)');
      existing.model = mainAgentPatch.model;
      console.log('   🔧 main → baseline model: ' + before + ' → ' + mainAgentPatch.model);
    } else {
      if (!existing.model) { existing.model = mainAgentPatch.model; console.log('   🔧 main → 补齐 model'); }
    }
    if (!existing.identity) { existing.identity = mainAgentPatch.identity; console.log('   🔧 main → 补齐 identity'); }
    if (!existing.name) { existing.name = mainAgentPatch.name; console.log('   🔧 main → 补齐 name'); }
    if (existing.default !== true) { existing.default = true; console.log('   🔧 main → 设置 default=true'); }
  }
}

const defaultOrder = ['coder','product','tester','research','trader','writer'];
const workerIds = (() => {
  const keys = Object.keys(roster || {});
  const set = new Set(keys.length ? keys : defaultOrder);
  const out = defaultOrder.filter(x => set.has(x));
  for (const k of keys) if (!out.includes(k)) out.push(k);
  return out;
})();

const defaultFallbacks = ['bailian/qwen3.5-plus','bailian/kimi-k2.5','zai/glm-4.7'];

const workers = workerIds.map((id) => {
  const r = roster[id] || {};
  const name = getDisplayName(id);
  const emoji = r.emoji || '🤖';
  const theme = r.theme || '';
  const toolsProfile = r.toolsProfile || 'full';

  // Baseline model policy:
  // - coder: openai-codex/gpt-5.3-codex
  // - others: openai-codex/gpt-5.4
  const baselinePrimary = id === 'coder' ? 'openai-codex/gpt-5.3-codex' : 'openai-codex/gpt-5.4';
  const primaryDefault = baselinePrimary;
  const primary = baseline ? baselinePrimary : (r.model || primaryDefault);

  return {
    id,
    name,
    model: { primary, fallbacks: defaultFallbacks },
    tools: { profile: toolsProfile },
    skills: [],
    workspace: home + '/.openclaw/agents/' + id + '/workspace',
    identity: { name, emoji, theme },
  };
});

let added = 0, updated = 0, skipped = 0;
for (const agent of workers) {
  const idx = config.agents.list.findIndex(a => a.id === agent.id);
  if (idx === -1) {
    config.agents.list.push(agent);
    console.log('   ✅ ' + agent.id + ' (' + agent.identity.name + ') → 新增');
    added++;
  } else {
    const existing = config.agents.list[idx];
    let changed = false;
    if (!existing.workspace) { existing.workspace = agent.workspace; changed = true; }
    if (!existing.identity) { existing.identity = agent.identity; changed = true; }
    if (!existing.name) { existing.name = agent.name; changed = true; }
    if (!existing.tools) { existing.tools = agent.tools; changed = true; }
    // Model patching policy:
    // - default: do not overwrite user-set model
    // - baseline mode (--baseline-models): force-set model.primary to the baseline
    if (baseline) {
      existing.model ??= {};
      if (typeof existing.model === 'string') {
        existing.model = { primary: existing.model, fallbacks: defaultFallbacks };
      }
      const before = (typeof existing.model === 'string') ? existing.model : existing.model?.primary;
      existing.model = { primary: agent.model.primary, fallbacks: defaultFallbacks };
      console.log('   🔧 ' + agent.id + ' → baseline model: ' + before + ' → ' + agent.model.primary);
      updated++;
    } else if (changed) {
      console.log('   🔧 ' + agent.id + ' → 补齐缺失字段');
      updated++;
    } else {
      console.log('   ⏭️  ' + agent.id + ' → 已完整，跳过');
      skipped++;
    }
  }
}

fs.writeFileSync(path, JSON.stringify(config, null, 2));
console.log('');
console.log('   新增: ' + added + ', 更新: ' + updated + ', 跳过: ' + skipped);
" || { echo "❌ 写入 openclaw.json 失败"; exit 1; }

# 验证 JSON 格式
node -e "JSON.parse(require('fs').readFileSync('$OPENCLAW_JSON','utf8'))" || { echo "❌ openclaw.json 格式错误"; exit 1; }

# ─── Step 6: 验证 + 重启 ───
echo ""
echo "🔍 Step 6: 验证安装..."
ERRORS=0

# 检查软连接
if [ -L ~/.openclaw/skills/team-dispatch ]; then
    echo "   ✅ 软连接: $(readlink ~/.openclaw/skills/team-dispatch)"
else
    echo "   ❌ 软连接缺失"; ERRORS=$((ERRORS + 1))
fi

# 检查任务目录
for dir in active done templates; do
    if [ -d ~/.openclaw/workspace/tasks/$dir ]; then
        echo "   ✅ tasks/$dir/"
    else
        echo "   ❌ tasks/$dir/ 缺失"; ERRORS=$((ERRORS + 1))
    fi
done

# 检查模板
if [ -f ~/.openclaw/workspace/tasks/templates/project.json ]; then
    echo "   ✅ project.json 模板"
else
    echo "   ❌ project.json 模板缺失"; ERRORS=$((ERRORS + 1))
fi

# 检查用户配置
if [ -f ~/.openclaw/configs/team-dispatch.json ]; then
    echo "   ✅ team-dispatch.json 用户配置"
else
    echo "   ❌ team-dispatch.json 缺失"; ERRORS=$((ERRORS + 1))
fi

# 检查子 Agent workspace 完整性
EXPECTED_FILES=("AGENTS.md" "SOUL.md" "IDENTITY.md" "USER.md" "TOOLS.md")
for agent in "${AGENTS[@]}"; do
    ws="$HOME/.openclaw/agents/$agent/workspace"
    if [ ! -d "$ws" ]; then
        echo "   ❌ $agent → workspace 缺失"; ERRORS=$((ERRORS + 1))
        continue
    fi
    missing=""
    for ef in "${EXPECTED_FILES[@]}"; do
        [ ! -f "$ws/$ef" ] && missing="$missing $ef"
    done
    if [ -z "$missing" ]; then
        echo "   ✅ $agent → workspace 完整"
    else
        echo "   ⚠️  $agent → 缺少:$missing"
    fi
    # sessions 目录
    if [ -d "$HOME/.openclaw/agents/$agent/sessions" ]; then
        echo "      ✅ sessions/"
    else
        echo "      ⚠️  sessions/ 缺失（会在运行时自动生成）"
    fi
done

# 检查 openclaw.json 中的 agents.list
node -e "
const fs = require('fs');
const config = JSON.parse(fs.readFileSync('$OPENCLAW_JSON', 'utf8'));
const list = config.agents?.list || [];

// main
const main = list.find(x => x.id === 'main');
if (!main) {
  console.log('   ❌ main → 未配置（必须存在，用于派发/调度）');
} else {
  const allow = main.subagents?.allowAgents;
  console.log('   ✅ main → workspace=' + (main.workspace||'(missing)') + ' subagents.allowAgents=' + JSON.stringify(allow||null));
}

// workers
const required = ['coder','product','tester','research','trader','writer'];
let ok = 0;
for (const id of required) {
  const a = list.find(x => x.id === id);
  if (a && a.workspace && a.identity) {
    const m = typeof a.model === 'string' ? a.model : a.model?.primary;
    console.log('   ✅ ' + id + ' (' + a.identity.name + ' ' + a.identity.emoji + ') → ' + m);
    ok++;
  } else if (a) {
    console.log('   ⚠️  ' + id + ' → 存在但缺少 workspace 或 identity');
  } else {
    console.log('   ❌ ' + id + ' → 未配置');
  }
}
" || true

echo ""

# ─── Step 7: 安装 watcher（跨平台，默认启用，可 --no-watch 关闭） ───
echo "🧭 Step 7: watcher（任务监控/超时重试兜底）..."
WATCH_ENABLED=$(node -e "
  const fs=require('fs');
  const home=process.env.HOME;
  const up=home+'/.openclaw/configs/team-dispatch.json';
  const sp='$SKILL_DIR/config.json';
  let u={}, s={};
  try{ if (fs.existsSync(up)) u=JSON.parse(fs.readFileSync(up,'utf8')); }catch(e){}
  try{ if (fs.existsSync(sp)) s=JSON.parse(fs.readFileSync(sp,'utf8')); }catch(e){}
  // Merge: skill defaults first, user overrides second (missing fields fall back to defaults)
  const merged={...s, ...u, team:{...(s.team||{}), ...(u.team||{}), watcher:{...((s.team||{}).watcher||{}), ...(((u.team||{}).watcher)||{})}}};
  const w=merged.team?.watcher||{};
  process.stdout.write(w.enabled===false?'0':'1');
")
WATCH_BACKEND=$(node -e "
  const fs=require('fs');
  const home=process.env.HOME;
  const up=home+'/.openclaw/configs/team-dispatch.json';
  const sp='$SKILL_DIR/config.json';
  let u={}, s={};
  try{ if (fs.existsSync(up)) u=JSON.parse(fs.readFileSync(up,'utf8')); }catch(e){}
  try{ if (fs.existsSync(sp)) s=JSON.parse(fs.readFileSync(sp,'utf8')); }catch(e){}
  const merged={...s, ...u, team:{...(s.team||{}), ...(u.team||{}), watcher:{...((s.team||{}).watcher||{}), ...(((u.team||{}).watcher)||{})}}};
  process.stdout.write(String(merged.team?.watcher?.backend||'auto'));
")
WATCH_INTERVAL=$(node -e "
  const fs=require('fs');
  const home=process.env.HOME;
  const up=home+'/.openclaw/configs/team-dispatch.json';
  const sp='$SKILL_DIR/config.json';
  let u={}, s={};
  try{ if (fs.existsSync(up)) u=JSON.parse(fs.readFileSync(up,'utf8')); }catch(e){}
  try{ if (fs.existsSync(sp)) s=JSON.parse(fs.readFileSync(sp,'utf8')); }catch(e){}
  const merged={...s, ...u, team:{...(s.team||{}), ...(u.team||{}), watcher:{...((s.team||{}).watcher||{}), ...(((u.team||{}).watcher)||{})}}};
  process.stdout.write(String(merged.team?.watcher?.interval||300));
")
WATCH_GRACE=$(node -e "
  const fs=require('fs');
  const home=process.env.HOME;
  const up=home+'/.openclaw/configs/team-dispatch.json';
  const sp='$SKILL_DIR/config.json';
  let u={}, s={};
  try{ if (fs.existsSync(up)) u=JSON.parse(fs.readFileSync(up,'utf8')); }catch(e){}
  try{ if (fs.existsSync(sp)) s=JSON.parse(fs.readFileSync(sp,'utf8')); }catch(e){}
  const merged={...s, ...u, team:{...(s.team||{}), ...(u.team||{}), watcher:{...((s.team||{}).watcher||{}), ...(((u.team||{}).watcher)||{})}}};
  process.stdout.write(String(merged.team?.watcher?.grace||20));
")

if [ "$NO_WATCH" -eq 1 ]; then
    echo "   ⏭️  已通过 --no-watch 禁用 watcher 安装"
elif [ "$WATCH_ENABLED" = "0" ]; then
    echo "   ⏭️  team-dispatch.json 中 watcher.enabled=false，跳过"
elif [ "$ERRORS" -ne 0 ]; then
    echo "   ⚠️  安装存在错误（$ERRORS），跳过 watcher 安装"
else
    echo "   ▶︎ backend=$WATCH_BACKEND interval=$WATCH_INTERVAL grace=$WATCH_GRACE"
    INTERVAL="$WATCH_INTERVAL" GRACE="$WATCH_GRACE" bash "$SKILL_DIR/scripts/watch-install.sh" --backend "$WATCH_BACKEND" \
      && echo "   ✅ watcher 已安装/启用" \
      || echo "   ⚠️  watcher 安装失败（不影响主功能）。可手动运行: bash $SKILL_DIR/scripts/watch-install.sh"
fi

# ─── Step 8: 安装每日总结任务（openclaw cron，默每天22点） ───
echo ""
echo "📅 Step 8: 每日总结任务（openclaw cron）..."

# 读取每日总结配置（类似 watcher 配置方式）
DAILY_SUMMARY_ENABLED=$(node -e "
  const fs=require('fs');
  const home=process.env.HOME;
  const up=home+'/.openclaw/configs/team-dispatch.json';
  const sp='$SKILL_DIR/config.json';
  let u={}, s={};
  try{ if (fs.existsSync(up)) u=JSON.parse(fs.readFileSync(up,'utf8')); }catch(e){}
  try{ if (fs.existsSync(sp)) s=JSON.parse(fs.readFileSync(up,'utf8')); }catch(e){}
  const merged={...s, ...u, team:{...(s.team||{}), ...(u.team||{}), dailySummary:{...((s.team||{}).dailySummary||{}), ...(((u.team||{}).dailySummary)||{})}}};
  const ds=merged.team?.dailySummary||{};
  process.stdout.write(ds.enabled===false?'0':'1');
")
DAILY_SUMMARY_CRON=$(node -e "
  const fs=require('fs');
  const home=process.env.HOME;
  const up=home+'/.openclaw/configs/team-dispatch.json';
  const sp='$SKILL_DIR/config.json';
  let u={}, s={};
  try{ if (fs.existsSync(up)) u=JSON.parse(fs.readFileSync(up,'utf8')); }catch(e){}
  try{ if (fs.existsSync(sp)) s=JSON.parse(fs.readFileSync(sp,'utf8')); }catch(e){}
  const merged={...s, ...u, team:{...(s.team||{}), ...(u.team||{}), dailySummary:{...((s.team||{}).dailySummary||{}), ...(((u.team||{}).dailySummary)||{})}}};
  process.stdout.write(String(merged.team?.dailySummary?.cron||'0 22 * * *'));
")
DAILY_SUMMARY_TZ=$(node -e "
  const fs=require('fs');
  const home=process.env.HOME;
  const up=home+'/.openclaw/configs/team-dispatch.json';
  const sp='$SKILL_DIR/config.json';
  let u={}, s={};
  try{ if (fs.existsSync(up)) u=JSON.parse(fs.readFileSync(up,'utf8')); }catch(e){}
  try{ if (fs.existsSync(sp)) s=JSON.parse(fs.readFileSync(sp,'utf8')); }catch(e){}
  const merged={...s, ...u, team:{...(s.team||{}), ...(u.team||{}), dailySummary:{...((s.team||{}).dailySummary||{}), ...(((u.team||{}).dailySummary)||{})}}};
  process.stdout.write(String(merged.team?.dailySummary?.timezone||''));
")
DAILY_SUMMARY_NAME=$(node -e "
  const fs=require('fs');
  const home=process.env.HOME;
  const up=home+'/.openclaw/configs/team-dispatch.json';
  const sp='$SKILL_DIR/config.json';
  let u={}, s={};
  try{ if (fs.existsSync(up)) u=JSON.parse(fs.readFileSync(up,'utf8')); }catch(e){}
  try{ if (fs.existsSync(sp)) s=JSON.parse(fs.readFileSync(sp,'utf8')); }catch(e){}
  const merged={...s, ...u, team:{...(s.team||{}), ...(u.team||{}), dailySummary:{...((s.team||{}).dailySummary||{}), ...(((u.team||{}).dailySummary)||{})}}};
  process.stdout.write(String(merged.team?.dailySummary?.jobName||'team-dispatch.daily-summary'));
")
DAILY_SUMMARY_DESC=$(node -e "
  const fs=require('fs');
  const home=process.env.HOME;
  const up=home+'/.openclaw/configs/team-dispatch.json';
  const sp='$SKILL_DIR/config.json';
  let u={}, s={};
  try{ if (fs.existsSync(up)) u=JSON.parse(fs.readFileSync(up,'utf8')); }catch(e){}
  try{ if (fs.existsSync(sp)) s=JSON.parse(fs.readFileSync(sp,'utf8')); }catch(e){}
  const merged={...s, ...u, team:{...(s.team||{}), ...(u.team||{}), dailySummary:{...((s.team||{}).dailySummary||{}), ...(((u.team||{}).dailySummary)||{})}}};
  process.stdout.write(String(merged.team?.dailySummary?.jobDescription||'Team Dispatch 每日总结：汇总当天完成的任务、进度和状态'));
")

install_daily_summary_job() {
  local SKILL_DIR="$1"
  local JOB_NAME="$2"
  local CRON_EXPR="$3"
  local TIMEZONE="$4"
  local DESC="$5"

  # 检查是否已存在
  local JOB_ID=$(openclaw cron list --json 2>/dev/null | node -e "
    const fs=require('fs');
    let s=''; process.stdin.on('data',d=>s+=d); process.stdin.on('end',()=>{
      try{const j=JSON.parse(s); const jobs=j.jobs||j; const hit=(jobs||[]).find(x=>x.name==='$JOB_NAME');
      process.stdout.write(hit?.jobId||hit?.id||'');}catch(e){process.stdout.write('');}
    });
  ")

  if [ -n "$JOB_ID" ]; then
    echo "   ⏭️  每日总结任务已存在: $JOB_ID"
    return 0
  fi

  # 构建时区参数
  local TZ_ARG=""
  if [ -n "$TIMEZONE" ]; then
    TZ_ARG="--tz $TIMEZONE"
  fi

  # 创建每日总结任务
  local MSG=$(cat <<'EOF'
请生成 Team Dispatch 的每日总结报告：

1. 扫描 ~/.openclaw/workspace/tasks/active/ 下的所有项目
2. 汇总今天完成的任务（根据 completedAt 判断）
3. 列出进行中的任务和当前状态
4. 识别任何失败或卡住的任务
5. 生成简洁的日报总结

格式：
📊 Team Dispatch 日报 (YYYY-MM-DD)
✅ 今日完成: X 个任务
🔄 进行中: X 个任务
⚠️  需关注: X 个问题
EOF
)

  JOB_ID=$(openclaw cron add \
    --name "$JOB_NAME" \
    --cron "$CRON_EXPR" \
    $TZ_ARG \
    --session isolated \
    --agent main \
    --message "$MSG" \
    --no-deliver \
    --description "$DESC" \
    --json 2>/dev/null | node -e "let s='';process.stdin.on('data',d=>s+=d);process.stdin.on('end',()=>{try{const j=JSON.parse(s);process.stdout.write(j.jobId||j.id||'');}catch(e){process.stdout.write('');}});")

  if [ -n "$JOB_ID" ]; then
    echo "   ✅ 每日总结任务已创建: $JOB_ID"
    echo "   ⏰ 执行计划: $CRON_EXPR"
    [ -n "$TIMEZONE" ] && echo "   🌍 时区: $TIMEZONE"
  else
    echo "   ⚠️  每日总结任务创建失败（不影响主功能）"
  fi
}

if [ "$ERRORS" -ne 0 ]; then
  echo "   ⏭️  安装存在错误，跳过每日总结任务"
elif ! command -v openclaw >/dev/null 2>&1; then
  echo "   ⏭️  未找到 openclaw，跳过每日总结任务"
elif [ "$DAILY_SUMMARY_ENABLED" = "0" ]; then
  echo "   ⏭️  config.json 中 dailySummary.enabled=false，跳过"
else
  echo "   ▶︎ cron='$DAILY_SUMMARY_CRON'${DAILY_SUMMARY_TZ:+ tz=$DAILY_SUMMARY_TZ}"
  install_daily_summary_job "$SKILL_DIR" "$DAILY_SUMMARY_NAME" "$DAILY_SUMMARY_CRON" "$DAILY_SUMMARY_TZ" "$DAILY_SUMMARY_DESC"
fi

echo ""
if [ "$ERRORS" -eq 0 ]; then
    echo "🎉 安装完成！Team Dispatch v${TD_VERSION:-unknown} 已就绪"
    echo ""
    echo "📋 已配置的团队："
    for agent in "${AGENTS[@]}"; do
        echo "   - $agent"
    done
    echo ""
    echo "🔄 正在重启 Gateway..."
    openclaw gateway restart 2>/dev/null || true
    echo ""
    echo "使用方式: 直接向主 Agent 提需求，系统会自动分析、拆解、派发"
else
    echo "⚠️  安装有 $ERRORS 个问题，请检查上方输出"
fi
