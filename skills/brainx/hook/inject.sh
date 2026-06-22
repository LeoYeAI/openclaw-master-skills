#!/bin/bash
# ⚠️ DEPRECATED — Use handler.js (OpenClaw internal hook). This script is kept for reference only.
#
# Known bugs (not fixed since deprecated):
#   - Variables $decisions_raw and $gotchas_raw are used in the Highlights section
#     but are never defined. The generate_topic() calls assign their counts to
#     DECISION_COUNT/GOTCHA_COUNT but the raw output is captured locally and lost.
#     Result: the Highlights section is always empty.
#   - If MEMORY.md contains BRAINX:START/END markers in instructional text (e.g.
#     "do not edit the <!-- BRAINX:START --> markers"), sed/awk would match the
#     first occurrence instead of the last, causing duplicate block injection.
#     Fixed in handler.js by using lastIndexOf(). Not fixed here (deprecated).
#
# The canonical hook is handler.js, deployed via:
#   cp hook/{HOOK.md,handler.js,package.json} ~/.openclaw/hooks/brainx-auto-inject/
#   openclaw hooks enable brainx-auto-inject
#
# ─────────────────────────────────────────────────────────────
# Original description (preserved for reference):
# BrainX V5 Smart Inject Hook — v2 (Topic Files + Compact Index)
# Runs on agent:bootstrap event
#
# Generates:
#   BRAINX_CONTEXT.md          — Compact index (~50 lines), always loaded
#   brainx-topics/facts.md     — Full infrastructure facts
#   brainx-topics/decisions.md — Recent decisions
#   brainx-topics/gotchas.md   — Known traps and errors
#   brainx-topics/learnings.md — Learnings and insights
#   brainx-topics/team.md      — High-importance cross-agent memories
#   brainx-topics/own.md       — Agent-specific memories (full)
#
# Agents read the index always; topic files on-demand when needed.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRAINX_DIR="$(dirname "$SCRIPT_DIR")"
WORKSPACE_DIR="${1:-${WORKSPACE_DIR:-.}}"
AGENT_NAME="${OPENCLAW_AGENT:-unknown}"

OUTPUT_FILE="$WORKSPACE_DIR/BRAINX_CONTEXT.md"
TOPICS_DIR="$WORKSPACE_DIR/brainx-topics"
BRAINX_CLI="$BRAINX_DIR/brainx-v5"
TIMESTAMP="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"

# Load environment
if [ -f "$BRAINX_DIR/.env" ]; then
    export $(grep -v '^#' "$BRAINX_DIR/.env" | xargs) 2>/dev/null || true
fi

# If brainx CLI not available, write fallback and exit cleanly
if [ ! -f "$BRAINX_CLI" ] && [ ! -L "$BRAINX_CLI" ]; then
    cat > "$OUTPUT_FILE" << EOF
# 🧠 BrainX V5 Context (Auto-Injected)

**Agent:** $AGENT_NAME | **Updated:** $TIMESTAMP

*BrainX CLI not available — skipped*
EOF
    echo "[brainx-inject] CLI not found, skipped" >&2
    exit 0
fi

mkdir -p "$WORKSPACE_DIR" "$TOPICS_DIR" 2>/dev/null || true

# ═══════════════════════════════════════════════════
# TOPIC FILES — Full content, loaded on-demand
# ═══════════════════════════════════════════════════

FACT_COUNT=0
DECISION_COUNT=0
GOTCHA_COUNT=0
LEARNING_COUNT=0
TEAM_COUNT=0
OWN_COUNT=0

# ── Topic 1: Facts ──
project_facts=""
if [ -n "$DATABASE_URL" ]; then
    project_facts=$(psql "$DATABASE_URL" -t -A -F '|' -c "
        SELECT content, tier, importance, context, tags::text
        FROM brainx_memories
        WHERE type = 'fact'
          AND superseded_by IS NULL
          AND tier IN ('hot', 'warm')
        ORDER BY importance DESC, last_seen DESC NULLS LAST
        LIMIT 25;
    " 2>/dev/null) || true

    if [ -n "$project_facts" ]; then
        {
            echo "# 📌 Project Facts (Infrastructure)"
            echo ""
            echo "**Updated:** $TIMESTAMP"
            echo ""
            while IFS='|' read -r content tier imp ctx tags; do
                [ -z "$content" ] && continue
                FACT_COUNT=$((FACT_COUNT + 1))
                echo "- **[$tier/imp:$imp]** $content"
            done <<< "$project_facts"
        } > "$TOPICS_DIR/facts.md"
    else
        echo "# 📌 Project Facts — Empty" > "$TOPICS_DIR/facts.md"
    fi
fi

# Helper: generate a topic file from brainx inject output
generate_topic() {
    local title="$1"
    local query="$2"
    local outfile="$3"
    local limit="${4:-8}"
    local min_imp="${5:-5}"
    local tier_flag="$6"
    
    local inject_args=(inject --query "$query" --limit "$limit" --minImportance "$min_imp")
    [ -n "$tier_flag" ] && inject_args+=(--tier "$tier_flag")
    
    local raw
    raw=$("$BRAINX_CLI" "${inject_args[@]}" 2>/dev/null) || true
    
    local count=0
    if [ -n "$raw" ]; then
        count=$(echo "$raw" | grep -c '^\[sim:' 2>/dev/null || echo "0")
    fi
    
    if [ "$count" -gt 0 ]; then
        {
            echo "# $title"
            echo ""
            echo "**Updated:** $TIMESTAMP"
            echo ""
            echo "$raw"
        } > "$outfile"
    else
        echo "# $title — None found" > "$outfile"
    fi
    
    echo "$count"
}

DECISION_COUNT=$(generate_topic "🎯 Decisions" \
    "decisions architecture choices configuration" \
    "$TOPICS_DIR/decisions.md" 8 5 hot)

GOTCHA_COUNT=$(generate_topic "⚠️ Gotchas & Traps" \
    "gotchas traps errors bugs workarounds warnings" \
    "$TOPICS_DIR/gotchas.md" 8 5)

LEARNING_COUNT=$(generate_topic "💡 Learnings & Insights" \
    "learnings discoveries insights knowledge" \
    "$TOPICS_DIR/learnings.md" 8 5)

TEAM_COUNT=$(generate_topic "🔥 Team Knowledge (High Importance)" \
    "critical decisions infrastructure team configuration" \
    "$TOPICS_DIR/team.md" 8 7)

# ── Agent-specific (own memories) → topic file ──
own_raw=$("$BRAINX_CLI" inject \
    --query "recent work decisions gotchas by agent $AGENT_NAME" \
    --context "agent:$AGENT_NAME" \
    --limit 5 \
    --minImportance 5 2>/dev/null) || true

if [ -n "$own_raw" ]; then
    OWN_COUNT=$(echo "$own_raw" | grep -c '^\[sim:' 2>/dev/null || echo "0")
    if [ "$OWN_COUNT" -gt 0 ]; then
        {
            echo "# 🤖 Agent: $AGENT_NAME — My Memories"
            echo ""
            echo "**Updated:** $TIMESTAMP"
            echo ""
            echo "$own_raw"
        } > "$TOPICS_DIR/own.md"
    else
        echo "# 🤖 Agent: $AGENT_NAME — No memories" > "$TOPICS_DIR/own.md"
        OWN_COUNT=0
    fi
else
    echo "# 🤖 Agent: $AGENT_NAME — No memories" > "$TOPICS_DIR/own.md"
    OWN_COUNT=0
fi

# ═══════════════════════════════════════════════════
# COMPACT INDEX — Always loaded (target: ~50 lines)
# ═══════════════════════════════════════════════════

# Helper: extract first content line from each memory block in inject output
# Skips [sim:...] headers, --- separators, and empty lines
# Returns clean one-liner summaries truncated to maxlen
extract_content_lines() {
    local raw="$1"
    local max="${2:-3}"
    local maxlen="${3:-120}"
    local count=0
    local in_header=0
    
    while IFS= read -r line; do
        # Skip metadata headers
        [[ "$line" =~ ^\[sim: ]] && { in_header=1; continue; }
        # Skip separators and empty
        [[ "$line" == "---" ]] && continue
        [[ -z "$line" ]] && continue
        # Skip lines that are just ] or short fragments
        [[ ${#line} -lt 5 ]] && continue
        
        # This is a content line
        if [ ${#line} -gt "$maxlen" ]; then
            line="${line:0:$((maxlen - 3))}..."
        fi
        echo "  - $line"
        count=$((count + 1))
        in_header=0
        [ "$count" -ge "$max" ] && return
    done <<< "$raw"
}

# Top fact summaries for index
fact_summaries=""
if [ -n "$project_facts" ]; then
    fact_summaries=$(echo "$project_facts" | head -5 | while IFS='|' read -r content tier imp ctx tags; do
        [ -z "$content" ] && continue
        [ ${#content} -gt 100 ] && content="${content:0:97}..."
        echo "  - [$tier] $content"
    done)
fi

# Own memory summaries for index
own_summaries=""
if [ "$OWN_COUNT" -gt 0 ] 2>/dev/null; then
    own_summaries=$(extract_content_lines "$own_raw" 3 100)
fi

{
    echo "# 🧠 BrainX V5 Context (Auto-Injected)"
    echo ""
    echo "**Agent:** $AGENT_NAME | **Updated:** $TIMESTAMP"
    echo "**Mode:** Compact index — lee topic files con \`cat brainx-topics/<file>.md\` cuando necesites detalle"
    echo ""

    # ── Facts summary ──
    echo "## 📌 Facts ($FACT_COUNT) → \`brainx-topics/facts.md\`"
    [ -n "$fact_summaries" ] && echo "$fact_summaries" || echo "  *Empty*"
    echo ""

    # ── Own memories summary ──
    echo "## 🤖 Mis memorias ($OWN_COUNT) → \`brainx-topics/own.md\`"
    [ -n "$own_summaries" ] && echo "$own_summaries" || echo "  *Sin memorias propias*"
    echo ""

    # ── Topic directory ──
    echo "## 📂 Topics disponibles"
    echo ""
    echo "| Topic | Items | Archivo |"
    echo "|-------|-------|---------|"
    echo "| 🎯 Decisions | $DECISION_COUNT | \`brainx-topics/decisions.md\` |"
    echo "| ⚠️ Gotchas | $GOTCHA_COUNT | \`brainx-topics/gotchas.md\` |"
    echo "| 💡 Learnings | $LEARNING_COUNT | \`brainx-topics/learnings.md\` |"
    echo "| 🔥 Team | $TEAM_COUNT | \`brainx-topics/team.md\` |"
    echo "| 📌 Facts | $FACT_COUNT | \`brainx-topics/facts.md\` |"
    echo "| 🤖 Own | $OWN_COUNT | \`brainx-topics/own.md\` |"
    echo ""

    # ── Highlights ──
    has_highlights=0
    
    decision_lines=""
    [ "$DECISION_COUNT" -gt 0 ] 2>/dev/null && decision_lines=$(extract_content_lines "$decisions_raw" 3 100) && [ -n "$decision_lines" ] && has_highlights=1
    
    gotcha_lines=""
    [ "$GOTCHA_COUNT" -gt 0 ] 2>/dev/null && gotcha_lines=$(extract_content_lines "$gotchas_raw" 3 100) && [ -n "$gotcha_lines" ] && has_highlights=1

    if [ "$has_highlights" -eq 1 ]; then
        echo "## ⚡ Highlights"
        echo ""
        [ -n "$decision_lines" ] && echo "**Decisions:**" && echo "$decision_lines" && echo ""
        [ -n "$gotcha_lines" ] && echo "**Gotchas:**" && echo "$gotcha_lines" && echo ""
    fi

    echo "---"
    echo "**Guardar fact:** \`brainx add --type fact --tier hot --importance 8 --context \"project:NAME\" --content \"...\"\`"

} > "$OUTPUT_FILE"

# ═══════════════════════════════════════════════════
# TELEMETRY
# ═══════════════════════════════════════════════════

INDEX_CHARS=$(wc -c < "$OUTPUT_FILE" 2>/dev/null || echo "0")
TOPICS_CHARS=0
for tf in "$TOPICS_DIR"/*.md; do
    [ -f "$tf" ] && TOPICS_CHARS=$((TOPICS_CHARS + $(wc -c < "$tf" 2>/dev/null || echo 0)))
done

echo "[brainx-inject] agent=$AGENT_NAME facts=$FACT_COUNT decisions=$DECISION_COUNT gotchas=$GOTCHA_COUNT learnings=$LEARNING_COUNT team=$TEAM_COUNT own=$OWN_COUNT index=${INDEX_CHARS}ch topics=${TOPICS_CHARS}ch" >&2

if [ -n "$DATABASE_URL" ] && command -v psql &>/dev/null; then
    psql "$DATABASE_URL" -c "
        INSERT INTO brainx_pilot_log (agent, own_memories, team_memories, total_chars, injected_at)
        VALUES ('$AGENT_NAME', $OWN_COUNT, $TEAM_COUNT, $INDEX_CHARS, NOW())
    " 2>/dev/null || true
fi

exit 0
