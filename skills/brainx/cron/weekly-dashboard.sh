#!/bin/bash
set -euo pipefail

ROOT="/home/clawd/.openclaw/skills/brainx-v5"
cd "$ROOT"

load_env() {
  for env_file in "$ROOT/.env" "/home/clawd/.openclaw/.env" "/home/clawd/.env"; do
    if [ -f "$env_file" ]; then
      set -a
      # shellcheck disable=SC1090
      source "$env_file"
      set +a
    fi
  done
  export DOTENV_CONFIG_QUIET="${DOTENV_CONFIG_QUIET:-true}"
}

detect_cli() {
  for candidate in "$ROOT/brainx" "$ROOT/brainx-v5" "$ROOT/brainx-v5-cli"; do
    if [ -x "$candidate" ]; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

load_env

if ! BRAINX_CLI="$(detect_cli)"; then
  echo "ERROR: BrainX CLI not found (checked: brainx, brainx-v5, brainx-v5-cli)"
  exit 1
fi

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL not set"
  exit 1
fi

METRICS_7D=$("$BRAINX_CLI" metrics --days 7 --json)

# 1) Auto-Harvester Stats
AUTO_HARVESTED=$(psql "$DATABASE_URL" -t -A -c "
SELECT count(*) as auto_harvested FROM brainx_memories
WHERE tags::text LIKE '%auto-harvested%'
AND created_at > NOW() - INTERVAL '7 days';
" 2>/dev/null || echo "0")

# 2) Cross-Agent Activity (top agentes)
CROSS_AGENT=$(psql "$DATABASE_URL" -t -A -F '|' -c "
SELECT context, count(*) as memories, avg(importance)::numeric(3,1) as avg_importance
FROM brainx_memories
WHERE created_at > NOW() - INTERVAL '7 days' AND superseded_by IS NULL
GROUP BY context ORDER BY count(*) DESC LIMIT 5;
" 2>/dev/null || true)

# 3) Dedup Effectiveness
DEDUP_COUNT=$(psql "$DATABASE_URL" -t -A -c "
SELECT count(*) as superseded FROM brainx_memories
WHERE superseded_by IS NOT NULL
AND updated_at > NOW() - INTERVAL '7 days';
" 2>/dev/null || echo "0")

# 4) Quality Distribution (por tier)
TIER_DIST=$(psql "$DATABASE_URL" -t -A -F '|' -c "
SELECT tier, count(*) FROM brainx_memories
WHERE superseded_by IS NULL GROUP BY tier ORDER BY count(*) DESC;
" 2>/dev/null || true)

TREND=$(psql "$DATABASE_URL" -t -A -F '|' -c "
SELECT to_char(date_trunc('day', created_at), 'YYYY-MM-DD') AS day,
       query_kind,
       ROUND(AVG(COALESCE(duration_ms,0))::numeric,2) AS avg_ms,
       COUNT(*) AS calls
FROM brainx_query_log
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY 1,2
ORDER BY 1 DESC,2;
" 2>/dev/null || true)

echo "🧠 BrainX Weekly Dashboard (7 días)"
echo ""
echo "📊 Estado General:"
echo "- cli: $(basename "$BRAINX_CLI")"
echo "- metrics: $(echo "$METRICS_7D" | jq -r '.ok')"
echo "- auto-harvested: $AUTO_HARVESTED memorias creadas"
echo "- dedup fusionadas: $DEDUP_COUNT memorias"
echo ""
echo "🔥 Top Patrones (recurrence):"
echo "$METRICS_7D" | jq -r '.top_recurring_patterns[0:5][]? | "  - \(.pattern_key // "(sin-key)"): \(.recurrence_count)x"' || echo "  - sin datos"
echo ""
echo "🤖 Cross-Agent Activity (top 5):"
if [ -z "$CROSS_AGENT" ]; then
  echo "  - sin datos"
else
  while IFS='|' read -r ctx mems avg_imp; do
    [ -z "$ctx" ] && continue
    echo "  - $ctx: $mems memorias (avg imp: $avg_imp)"
  done <<< "$CROSS_AGENT"
fi
echo ""
echo "📦 Quality Distribution (por tier):"
if [ -z "$TIER_DIST" ]; then
  echo "  - sin datos"
else
  while IFS='|' read -r tier count; do
    [ -z "$tier" ] && continue
    echo "  - $tier: $count"
  done <<< "$TIER_DIST"
fi
echo ""
echo "⚡ Performance Query (promedio 7d):"
PERF=$(echo "$METRICS_7D" | jq -r '.query_performance[]?' 2>/dev/null || true)
if [ -z "$PERF" ] || [ "$PERF" = "null" ]; then
  echo "  - sin datos"
else
  echo "$METRICS_7D" | jq -r '.query_performance[]? | "  - \(.query_kind): \(.calls) calls"' || echo "  - sin datos"
fi
echo ""
echo "📈 Tendencia Diaria:"
if [ -z "$TREND" ]; then
  echo "  - sin datos"
else
  while IFS='|' read -r day kind avg calls; do
    [ -z "$day" ] && continue
    echo "  - ${day} ${kind}: ${calls} calls, ${avg}ms"
  done <<< "$TREND"
fi
