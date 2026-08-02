#!/usr/bin/env bash
# FlowSwarm Setup Script v2.0
# Installs RuFlo, registers MCP server, initializes projects, verifies everything.
#
# Usage:
#   ./setup-flow-swarm.sh                        # Install RuFlo + register MCP
#   ./setup-flow-swarm.sh /path/to/repo          # Install + init project + start daemon
#   ./setup-flow-swarm.sh --init-only /path/to/repo  # Skip install, just init project
#   ./setup-flow-swarm.sh --verify /path/to/repo     # Health check everything
#   ./setup-flow-swarm.sh --targets /path/to/repo    # Find best swarm targets

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${CYAN}[flowswarm]${NC} $*"; }
ok()    { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
fail()  { echo -e "${RED}[✗]${NC} $*"; exit 1; }

INIT_ONLY=false
VERIFY_ONLY=false
TARGETS_ONLY=false
PROJECT_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --init-only) INIT_ONLY=true; shift ;;
    --verify) VERIFY_ONLY=true; shift ;;
    --targets) TARGETS_ONLY=true; shift ;;
    --help|-h)
      echo "Usage: setup-flow-swarm.sh [OPTIONS] [/path/to/project]"
      echo ""
      echo "Options:"
      echo "  (no flags)       Install RuFlo + register MCP server"
      echo "  --init-only      Skip global install, just init project"
      echo "  --verify         Health check all components"
      echo "  --targets        Find best swarm targets in project"
      echo ""
      echo "Examples:"
      echo "  setup-flow-swarm.sh ~/Dev/my-project     # Full setup"
      echo "  setup-flow-swarm.sh --verify ~/Dev/my-project"
      echo "  setup-flow-swarm.sh --targets ~/Dev/my-project"
      exit 0
      ;;
    *) PROJECT_DIR="$1"; shift ;;
  esac
done

# --- Targets Mode ---
if [[ "$TARGETS_ONLY" == true ]]; then
  [[ -n "$PROJECT_DIR" ]] || fail "Provide a project path: --targets /path/to/project"
  [[ -d "$PROJECT_DIR" ]] || fail "Directory not found: $PROJECT_DIR"
  cd "$PROJECT_DIR"

  echo -e "${BOLD}FlowSwarm Target Analysis${NC}"
  echo ""

  # Detect language
  if [[ -f "mix.exs" ]]; then
    LANG="elixir"
    SRC_DIR="lib"
    TEST_DIR="test"
    SRC_EXT="ex"
    TEST_SUFFIX="_test.exs"
  elif [[ -f "package.json" ]]; then
    LANG="javascript"
    SRC_DIR="src"
    TEST_DIR="test"
    SRC_EXT="ts"
    TEST_SUFFIX=".test.ts"
  else
    LANG="unknown"
    SRC_DIR="src"
    TEST_DIR="test"
    SRC_EXT="*"
    TEST_SUFFIX="_test.*"
  fi

  info "Detected: $LANG project"
  echo ""

  echo -e "${BOLD}Untested modules (best targets):${NC}"
  FOUND=0
  for f in $(find "$SRC_DIR" -name "*.${SRC_EXT}" 2>/dev/null | sort); do
    base=$(basename "$f" ".${SRC_EXT}")
    count=$(find "$TEST_DIR" -name "${base}${TEST_SUFFIX}" 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$count" == "0" ]]; then
      lines=$(wc -l < "$f" | tr -d ' ')
      if [[ "$lines" -gt 50 ]]; then
        # Classify module type
        TYPE="data"
        if grep -q "use GenServer\|use Agent\|use GenStage" "$f" 2>/dev/null; then
          TYPE="genserver"
        elif grep -q "Tesla\|HTTPoison\|Req\.\|Finch\." "$f" 2>/dev/null; then
          TYPE="http"
        elif grep -q "defstruct" "$f" 2>/dev/null; then
          TYPE="struct"
        fi
        printf "  %5sL  %-10s %s\n" "$lines" "[$TYPE]" "$f"
        FOUND=$((FOUND + 1))
      fi
    fi
  done | sort -rn

  if [[ "$FOUND" == "0" ]]; then
    ok "All modules have test files!"
  fi

  echo ""
  echo -e "${BOLD}Thin coverage (test LOC < 33% of source):${NC}"
  for f in $(find "$SRC_DIR" -name "*.${SRC_EXT}" 2>/dev/null | sort); do
    base=$(basename "$f" ".${SRC_EXT}")
    test_file=$(find "$TEST_DIR" -name "${base}${TEST_SUFFIX}" 2>/dev/null | head -1)
    if [[ -n "$test_file" ]]; then
      src=$(wc -l < "$f" | tr -d ' ')
      tst=$(wc -l < "$test_file" | tr -d ' ')
      if [[ "$src" -gt 0 ]]; then
        ratio=$((tst * 100 / src))
        if [[ "$ratio" -lt 33 ]]; then
          printf "  %3s%% coverage  %5sL src / %4sL test  %s\n" "$ratio" "$src" "$tst" "$f"
        fi
      fi
    fi
  done | sort -n

  exit 0
fi

# --- Verify Mode ---
if [[ "$VERIFY_ONLY" == true ]]; then
  echo -e "${BOLD}FlowSwarm Health Check${NC}"
  echo ""
  PASS=0; TOTAL=0

  # Global checks
  TOTAL=$((TOTAL + 1))
  if command -v ruflo >/dev/null 2>&1; then
    ok "RuFlo installed: $(ruflo --version 2>/dev/null || echo 'unknown')"
    PASS=$((PASS + 1))
  else
    echo -e "${RED}[✗]${NC} RuFlo not installed (npm install -g ruflo@latest)"
  fi

  TOTAL=$((TOTAL + 1))
  if command -v claude >/dev/null 2>&1; then
    ok "Claude Code installed"
    PASS=$((PASS + 1))
  else
    echo -e "${RED}[✗]${NC} Claude Code not installed"
  fi

  TOTAL=$((TOTAL + 1))
  # MCP check: grep for ruflo in claude mcp list output (handle timing/header issues)
  MCP_RAW=$(claude mcp list 2>/dev/null || true)
  if echo "$MCP_RAW" | grep -qi "ruflo\|claude.flow\|claude-flow"; then
    ok "RuFlo MCP server registered"
    PASS=$((PASS + 1))
  else
    echo -e "${RED}[✗]${NC} RuFlo MCP not registered (claude mcp add ruflo -- npx -y ruflo@latest mcp start)"
  fi

  # Project checks
  if [[ -n "$PROJECT_DIR" ]] && [[ -d "$PROJECT_DIR" ]]; then
    echo ""
    info "Project: $PROJECT_DIR"

    TOTAL=$((TOTAL + 1))
    if [[ -f "$PROJECT_DIR/.claude/settings.json" ]]; then
      if grep -q "hook-handler\|claude-flow\|ruflo" "$PROJECT_DIR/.claude/settings.json" 2>/dev/null; then
        ok "Claude hooks configured"
        PASS=$((PASS + 1))
      else
        warn "settings.json exists but no hooks found"
      fi
    else
      echo -e "${RED}[✗]${NC} .claude/settings.json missing (ruflo init)"
    fi

    TOTAL=$((TOTAL + 1))
    if [[ -f "$PROJECT_DIR/.swarm/memory.db" ]] || [[ -f "$PROJECT_DIR/.claude/memory.db" ]]; then
      ok "Memory database exists"
      PASS=$((PASS + 1))
    else
      echo -e "${RED}[✗]${NC} Memory not initialized (ruflo memory init)"
    fi

    TOTAL=$((TOTAL + 1))
    if [[ -f "$PROJECT_DIR/.mcp.json" ]]; then
      ok "MCP project config exists"
      PASS=$((PASS + 1))
    else
      echo -e "${RED}[✗]${NC} .mcp.json missing"
    fi

    TOTAL=$((TOTAL + 1))
    AGENT_COUNT=$(find "$PROJECT_DIR/.claude/agents/" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$AGENT_COUNT" -gt 0 ]]; then
      ok "Agent definitions: $AGENT_COUNT"
      PASS=$((PASS + 1))
    else
      echo -e "${RED}[✗]${NC} No agents in .claude/agents/"
    fi

    TOTAL=$((TOTAL + 1))
    if grep -q '"autoStart": true' "$PROJECT_DIR/.mcp.json" 2>/dev/null; then
      ok "MCP autoStart: true (150+ tools enabled)"
      PASS=$((PASS + 1))
    else
      echo -e "${RED}[✗]${NC} MCP autoStart is false — swarm tools DISABLED during Claude Code runs"
      echo "      Fix: python3 -c \"import json; d=json.load(open('.mcp.json')); d['mcpServers']['claude-flow']['autoStart']=True; json.dump(d,open('.mcp.json','w'),indent=2)\""
    fi

    TOTAL=$((TOTAL + 1))
    cd "$PROJECT_DIR"
    DAEMON_OUT=$(ruflo daemon status 2>&1 || true)
    if echo "$DAEMON_OUT" | grep -qiE "RUNNING|running|PID:"; then
      ok "Daemon running"
      PASS=$((PASS + 1))
    else
      warn "Daemon not running (ruflo daemon start)"
    fi
  fi

  echo ""
  if [[ "$PASS" -eq "$TOTAL" ]]; then
    echo -e "${GREEN}${BOLD}All checks passed ($PASS/$TOTAL)${NC}"
  else
    echo -e "${YELLOW}${BOLD}$PASS/$TOTAL checks passed${NC}"
  fi
  exit 0
fi

# --- Step 1: Prerequisites ---
info "Checking prerequisites..."

command -v node >/dev/null 2>&1 || fail "Node.js required (https://nodejs.org)"
NODE_VER=$(node -v | sed 's/v//' | cut -d. -f1)
[[ "$NODE_VER" -ge 20 ]] || fail "Node.js 20+ required (found v${NODE_VER})"
ok "Node.js $(node -v)"

command -v npm >/dev/null 2>&1 || fail "npm required"
ok "npm $(npm -v)"

command -v claude >/dev/null 2>&1 || fail "Claude Code CLI required"
ok "Claude Code installed"

command -v git >/dev/null 2>&1 || fail "git required"
ok "git $(git --version | awk '{print $3}')"

# --- Step 2: Install RuFlo ---
if [[ "$INIT_ONLY" == false ]]; then
  info "Installing RuFlo globally..."
  if command -v ruflo >/dev/null 2>&1; then
    CURRENT=$(ruflo --version 2>/dev/null || echo "unknown")
    ok "RuFlo already installed ($CURRENT), updating..."
  fi
  npm install -g ruflo@latest 2>&1 | tail -3
  ok "RuFlo $(ruflo --version 2>/dev/null)"

  # --- Step 3: Register MCP ---
  info "Registering RuFlo MCP server..."
  MCP_CHECK=$(claude mcp list 2>/dev/null || true)
  if echo "$MCP_CHECK" | grep -qi "ruflo\|claude-flow"; then
    ok "RuFlo MCP already registered"
  else
    claude mcp add ruflo -- npx -y ruflo@latest mcp start 2>&1
    ok "RuFlo MCP registered"
  fi
fi

# --- Step 4: Initialize project ---
if [[ -n "$PROJECT_DIR" ]]; then
  [[ -d "$PROJECT_DIR" ]] || fail "Directory not found: $PROJECT_DIR"
  info "Initializing RuFlo in $PROJECT_DIR..."
  cd "$PROJECT_DIR"

  if [[ -f ".claude/settings.json" ]] && grep -q "hook-handler\|claude-flow\|ruflo" ".claude/settings.json" 2>/dev/null; then
    warn "RuFlo already initialized. Skipping init."
  else
    ruflo init 2>&1 | tail -5
    ok "RuFlo initialized"
  fi

  # CRITICAL: Fix autoStart (ruflo init defaults to false, which disables ALL MCP tools)
  if [[ -f ".mcp.json" ]]; then
    if grep -q '"autoStart": false' ".mcp.json" 2>/dev/null; then
      python3 -c "
import json
with open('.mcp.json') as f: d = json.load(f)
for srv in d.get('mcpServers', {}).values():
    if srv.get('autoStart') == False:
        srv['autoStart'] = True
with open('.mcp.json', 'w') as f: json.dump(d, f, indent=2)
" 2>/dev/null && ok "Fixed autoStart: false → true (enables 150+ MCP tools)" || warn "Could not fix autoStart"
    else
      ok "MCP autoStart already enabled"
    fi
  fi

  # Memory
  info "Initializing memory..."
  if [[ -f ".swarm/memory.db" ]] || [[ -f ".claude/memory.db" ]]; then
    ok "Memory already exists"
  else
    timeout 30 ruflo memory init 2>&1 | tail -3 || warn "Memory init timed out (run manually: ruflo memory init)"
    ok "Memory initialized"
  fi

  # Daemon
  info "Starting daemon..."
  DAEMON_CHECK=$(ruflo daemon status 2>&1 || true)
  if echo "$DAEMON_CHECK" | grep -qiE "RUNNING|running"; then
    ok "Daemon already running"
  else
    ruflo daemon start 2>&1 | tail -3
    ok "Daemon started"
  fi
  echo ""
fi

ok "FlowSwarm setup complete!"
echo ""
info "Next steps:"
[[ -n "$PROJECT_DIR" ]] && echo "  $0 --verify $PROJECT_DIR"
[[ -n "$PROJECT_DIR" ]] && echo "  $0 --targets $PROJECT_DIR"
echo "  claude --print 'SWARM MODE: hierarchical, 4 agents. TASK: ...'"
