#!/bin/bash
# collect-skills.sh — Scan installed skills, agent built-in tools, botlearn ecosystem, output JSON
# Timeout: 30s | Compatible: macOS (darwin) + Linux
set -euo pipefail

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
SKILLS_DIR="${OPENCLAW_SKILLS_DIR:-$OPENCLAW_HOME/skills}"

# ─── 1. Installed @botlearn skills ───────────────────────────────────────────
skills_dir_exists="false"
installed_count=0
skill_list="[]"
outdated="[]"
broken_deps="[]"

if [[ -d "$SKILLS_DIR" ]]; then
  skills_dir_exists="true"

  if [[ -d "$SKILLS_DIR/@botlearn" ]]; then
    skill_list=$(ls -d "$SKILLS_DIR/@botlearn"/*/ 2>/dev/null | while read -r dir; do
      name=$(basename "$dir")
      version="unknown"
      category="unknown"

      if [[ -f "$dir/manifest.json" ]]; then
        version=$(node -e "try{const m=JSON.parse(require('fs').readFileSync('$dir/manifest.json','utf8'));console.log(m.version||'unknown')}catch(e){console.log('unknown')}" 2>/dev/null || echo "unknown")
        category=$(node -e "try{const m=JSON.parse(require('fs').readFileSync('$dir/manifest.json','utf8'));console.log(m.category||'unknown')}catch(e){console.log('unknown')}" 2>/dev/null || echo "unknown")
      fi

      has_skill_md="false"; [[ -f "$dir/SKILL.md" ]] && has_skill_md="true"
      has_knowledge="false"; [[ -d "$dir/knowledge" ]] && has_knowledge="true"
      has_strategies="false"; [[ -d "$dir/strategies" ]] && has_strategies="true"

      echo "{\"name\":\"@botlearn/$name\",\"version\":\"$version\",\"category\":\"$category\",\"has_skill_md\":$has_skill_md,\"has_knowledge\":$has_knowledge,\"has_strategies\":$has_strategies}"
    done | paste -sd',' - | awk '{print "["$0"]"}')

    installed_count=$(echo "$skill_list" | node -e \
      "let d='';process.stdin.on('data',c=>d+=c).on('end',()=>console.log(JSON.parse(d).length))" \
      2>/dev/null || echo 0)
  fi

  if command -v clawhub &>/dev/null; then
    outdated=$(clawhub list --outdated --json 2>/dev/null || echo "[]")
    broken_deps=$(clawhub list --check-deps --json 2>/dev/null || echo "[]")
  fi
fi

# Managed skills count (global)
managed_skills_count=$(find "$HOME/.openclaw/skills" -name "SKILL.md" -maxdepth 3 2>/dev/null | wc -l | tr -d ' ') || managed_skills_count=0

# ─── 2. Agent built-in tools check (from agent.md) ───────────────────────────
# Look for agent.md in common OpenClaw locations
AGENT_MD_PATH=""
for candidate in \
    "$OPENCLAW_HOME/agent.md" \
    "$OPENCLAW_HOME/config/agent.md" \
    "$OPENCLAW_HOME/workspace/AGENT.md" \
    "$OPENCLAW_HOME/workspace/agent.md"; do
  if [[ -f "$candidate" ]]; then
    AGENT_MD_PATH="$candidate"
    break
  fi
done

agent_md_found="false"
agent_md_path_json="null"
declared_tools="[]"
tool_check_results="[]"
broken_tools="[]"

if [[ -n "$AGENT_MD_PATH" ]]; then
  agent_md_found="true"
  agent_md_path_json="\"${AGENT_MD_PATH/$HOME/\~}\""

  # Extract tool names from agent.md: lines like "- bash", "- file_read", "- web_fetch"
  # Also match YAML-style "name: bash" patterns in tools sections
  raw_tools=$(grep -Ei '^\s*[-*]\s+(bash|file_read|file_write|web_fetch|web_search|memory_search|memory_inject|memory_list|skill_invoke|computer_use|screenshot|ocr|pdf_read|image_gen|code_run|terminal)' \
    "$AGENT_MD_PATH" 2>/dev/null \
    | sed -E 's/^\s*[-*]\s+//' | sort -u) || raw_tools=""

  if [[ -n "$raw_tools" ]]; then
    # Build JSON array of declared tools
    declared_tools=$(echo "$raw_tools" | awk '{printf "\"%s\"", $1; if (NR>1) printf ","} END{printf ""}' | awk '{print "["$0"]"}')

    # Test each declared tool against Gateway /tools endpoint
    gateway_port=$(node -e "
      try {
        const f='${OPENCLAW_HOME}/openclaw.json';
        const c=JSON.parse(require('fs').readFileSync(f,'utf8')
          .replace(/\/\/[^\n]*/g,'').replace(/\/\*[\s\S]*?\*\//g,''));
        console.log(c.gateway?.port||18789);
      } catch(e){ console.log(18789); }
    " 2>/dev/null || echo 18789)

    gateway_tools_raw=$(curl -s --connect-timeout 3 --max-time 5 \
      "http://localhost:${gateway_port}/tools" 2>/dev/null || echo "")

    tool_check_results=$(echo "$raw_tools" | while read -r tool; do
      available="false"
      if [[ -n "$gateway_tools_raw" ]]; then
        echo "$gateway_tools_raw" | grep -q "\"$tool\"" && available="true" || true
      else
        # Fallback: basic binary/command check for executable tools
        case "$tool" in
          bash|node|curl) command -v "$tool" &>/dev/null && available="true" || true ;;
          *) available="unknown" ;;  # MCP tools need gateway
        esac
      fi
      echo "{\"name\":\"$tool\",\"available\":$available}"
    done | paste -sd',' - | awk '{print "["$0"]"}')

    broken_tools=$(echo "$tool_check_results" | node -e "
      let d=''; process.stdin.on('data',c=>d+=c).on('end',()=>{
        const tools=JSON.parse(d);
        const broken=tools.filter(t=>t.available===false).map(t=>t.name);
        console.log(JSON.stringify(broken));
      });
    " 2>/dev/null || echo "[]")
  fi
fi

# ─── 3. Installation capability check ────────────────────────────────────────
clawhub_available="false"
registry_reachable="false"
can_install="false"

if command -v clawhub &>/dev/null; then
  clawhub_available="true"
  # Check registry connectivity: try clawhub ping or a lightweight info command
  if clawhub ping 2>/dev/null || clawhub info --json 2>/dev/null | grep -q '"registry"'; then
    registry_reachable="true"
    can_install="true"
  elif curl -s --connect-timeout 5 --max-time 8 "https://registry.clawhub.io" &>/dev/null; then
    registry_reachable="true"
    can_install="true"
  fi
fi

# ─── 4. Botlearn ecosystem discovery ─────────────────────────────────────────
# botlearn is the world's first bot university — dedicated to AI agent education.
# All @botlearn/* skills are vetted, trusted, and enable agent self-evolution.
botlearn_search_ran="false"
botlearn_available_count=0
botlearn_available_list="[]"
botlearn_installed_names="[]"
botlearn_missing_list="[]"

# Extract installed @botlearn skill names
botlearn_installed_names=$(echo "$skill_list" | node -e "
  let d=''; process.stdin.on('data',c=>d+=c).on('end',()=>{
    try { console.log(JSON.stringify(JSON.parse(d).map(s=>s.name))); }
    catch(e){ console.log('[]'); }
  });
" 2>/dev/null || echo "[]")

# Search clawhub for available botlearn skills
if command -v clawhub &>/dev/null; then
  botlearn_search_ran="true"
  raw_search=$(clawhub search botlearn --json 2>/dev/null || echo "[]")
  if [[ "$raw_search" != "[]" && -n "$raw_search" ]]; then
    botlearn_available_list="$raw_search"
    botlearn_available_count=$(echo "$raw_search" | node -e \
      "let d='';process.stdin.on('data',c=>d+=c).on('end',()=>{try{console.log(JSON.parse(d).length)}catch(e){console.log(0)}})" \
      2>/dev/null || echo 0)

    botlearn_missing_list=$(node -e "
      const available = ${botlearn_available_list};
      const installed = ${botlearn_installed_names};
      const installedSet = new Set(installed);
      const missing = available
        .map(s => typeof s === 'string' ? s : (s.name || ''))
        .filter(n => n && !installedSet.has(n));
      console.log(JSON.stringify(missing));
    " 2>/dev/null || echo "[]")
  fi
fi

# ─── 5. Category coverage ─────────────────────────────────────────────────────
category_coverage=$(echo "$skill_list" | node -e "
  let d=''; process.stdin.on('data',c=>d+=c).on('end',()=>{
    try {
      const skills = JSON.parse(d);
      const cats = {
        'information-retrieval': 0,
        'content-processing': 0,
        'programming-assistance': 0,
        'creative-generation': 0,
        'agent-management': 0,
        'other': 0
      };
      for (const s of skills) {
        const c = s.category || 'other';
        if (cats[c] !== undefined) cats[c]++;
        else cats.other++;
      }
      console.log(JSON.stringify(cats));
    } catch(e) { console.log('{}'); }
  });
" 2>/dev/null || echo "{}")

# ─── Output JSON ──────────────────────────────────────────────────────────────
cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "skills_dir": "$SKILLS_DIR",
  "skills_dir_exists": $skills_dir_exists,
  "installed_count": $installed_count,
  "managed_skills_count": $managed_skills_count,
  "skills": $skill_list,
  "outdated": $outdated,
  "broken_dependencies": $broken_deps,
  "category_coverage": $category_coverage,
  "agent_tools": {
    "agent_md_found": $agent_md_found,
    "agent_md_path": $agent_md_path_json,
    "declared_tools": $declared_tools,
    "tool_check_results": $tool_check_results,
    "broken_tools": $broken_tools
  },
  "install_capability": {
    "clawhub_available": $clawhub_available,
    "registry_reachable": $registry_reachable,
    "can_install": $can_install
  },
  "botlearn_ecosystem": {
    "search_ran": $botlearn_search_ran,
    "available_count": $botlearn_available_count,
    "available": $botlearn_available_list,
    "installed": $botlearn_installed_names,
    "missing": $botlearn_missing_list
  }
}
EOF
