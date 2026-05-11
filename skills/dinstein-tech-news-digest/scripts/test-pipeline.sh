#!/bin/bash
# Pipeline smoke test — runs fetch steps with filtering, validates outputs
# Usage:
#   ./test-pipeline.sh                          # run all sources
#   ./test-pipeline.sh --only twitter,rss       # only these source types
#   ./test-pipeline.sh --skip web               # skip web search
#   ./test-pipeline.sh --topics crypto           # only sources with these topics
#   ./test-pipeline.sh --ids sama-twitter,openai-rss  # specific source IDs
#   ./test-pipeline.sh --hours 12               # custom time window
#   ./test-pipeline.sh --keep                   # keep output dir after test
#   ./test-pipeline.sh --twitter-backend twitterapiio  # force twitter backend
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULTS="$SCRIPT_DIR/../config/defaults"
OUTDIR=$(mktemp -d /tmp/tech-digest-test-XXXXXX)
PASSED=0
SKIPPED=0
FAILED=0
HOURS=24
KEEP=false
ONLY=""
SKIP=""
TOPICS=""
IDS=""
TWITTER_BACKEND=""
VERBOSE=""
CONFIG=""

# ── Parse args ──
while [[ $# -gt 0 ]]; do
    case "$1" in
        --only)       ONLY="$2"; shift 2 ;;
        --skip)       SKIP="$2"; shift 2 ;;
        --topics)     TOPICS="$2"; shift 2 ;;
        --ids)        IDS="$2"; shift 2 ;;
        --hours)      HOURS="$2"; shift 2 ;;
        --keep)       KEEP=true; shift ;;
        --twitter-backend|--backend) TWITTER_BACKEND="$2"; shift 2 ;;
        --config)     CONFIG="$2"; shift 2 ;;
        --verbose|-v) VERBOSE="--verbose"; shift ;;
        --help|-h)
            cat <<'HELP'
Pipeline smoke test — runs fetch steps with filtering, merges, and validates outputs.

USAGE:
  ./test-pipeline.sh [OPTIONS]

OPTIONS:
  --only TYPES      Only run these source types (comma-separated)
                    Values: rss, twitter, github, reddit, web
                    Example: --only twitter,rss

  --skip TYPES      Skip these source types (comma-separated)
                    Values: rss, twitter, github, reddit, web
                    Example: --skip web,reddit

  --topics TOPICS   Only include sources matching these topics (comma-separated)
                    Values: llm, ai-agent, frontier-tech, crypto
                    Example: --topics crypto,llm

  --ids IDS         Only include specific source IDs (comma-separated)
                    IDs are defined in config/defaults/sources.json
                    Example: --ids sama-twitter,openai-rss,vitalik-twitter

  --hours N         Time window for fetching articles (default: 24)
                    Example: --hours 48

  --twitter-backend NAME
                    Force a specific Twitter API backend
                    Values: official, twitterapiio, auto
                    official     = X API v2 (needs X_BEARER_TOKEN)
                    twitterapiio = twitterapi.io (needs TWITTERAPI_IO_KEY)
                    auto         = try twitterapiio first, fallback to official

  --config DIR      User config overlay directory (optional)
                    Example: --config workspace/config

  --verbose, -v     Enable verbose logging for fetch scripts

  --keep            Keep output directory after test (default: clean up on success)

  --help, -h        Show this help message

EXAMPLES:
  ./test-pipeline.sh                                    # full pipeline, all sources
  ./test-pipeline.sh --only twitter --twitter-backend twitterapiio  # twitter only via twitterapi.io
  ./test-pipeline.sh --topics crypto --hours 48 --keep  # crypto sources, 48h window
  ./test-pipeline.sh --skip web,reddit -v               # skip web+reddit, verbose
  ./test-pipeline.sh --ids sama-twitter,karpathy-twitter --only twitter

ENVIRONMENT:
  X_BEARER_TOKEN      Official X API v2 bearer token (for --backend official)
  TWITTERAPI_IO_KEY   twitterapi.io API key (for --backend twitterapiio)
  TWITTER_API_BACKEND Default twitter backend if --backend not given (official|twitterapiio|auto)
  BRAVE_API_KEY       Brave Search API key (for web fetch)
  GITHUB_TOKEN        GitHub token (optional, increases GitHub API rate limits)
HELP
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ── Helpers ──
should_run() {
    local type="$1"
    # Check --only filter
    if [ -n "$ONLY" ]; then
        echo ",$ONLY," | grep -qi ",$type," || return 1
    fi
    # Check --skip filter
    if [ -n "$SKIP" ]; then
        echo ",$SKIP," | grep -qi ",$type," && return 1
    fi
    return 0
}

run_step() {
    local name="$1"; shift
    local start=$(date +%s)
    if "$@" 2>&1; then
        local elapsed=$(( $(date +%s) - start ))
        echo "✅ $name (${elapsed}s)"
        PASSED=$((PASSED + 1))
    else
        local code=$?
        local elapsed=$(( $(date +%s) - start ))
        echo "❌ $name (exit $code, ${elapsed}s)"
        FAILED=$((FAILED + 1))
    fi
}

validate_json() {
    local file="$1" name="$2"
    if [ -f "$file" ] && python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
# Print summary stats
if 'sources' in d and isinstance(d['sources'], list):
    ok = sum(1 for s in d['sources'] if s.get('status') == 'ok')
    total = len(d['sources'])
    articles = sum(s.get('count', len(s.get('articles', []))) for s in d['sources'])
    print(f'   📊 {ok}/{total} sources ok, {articles} articles')
elif 'topics' in d:
    topics = d['topics']
    if isinstance(topics, dict):
        total = sum(len(t.get('articles', [])) for t in topics.values())
        print(f'   📊 {len(topics)} topics, {total} articles')
    elif isinstance(topics, list):
        total = sum(len(t.get('articles', [])) for t in topics)
        print(f'   📊 {len(topics)} topics, {total} articles')
" "$file" 2>/dev/null; then
        echo "✅ $name JSON valid"
        PASSED=$((PASSED + 1))
    else
        echo "❌ $name JSON invalid or missing"
        FAILED=$((FAILED + 1))
    fi
}

# ── Generate filtered sources if --topics or --ids specified ──
EXTRA_ARGS=()
if [ -n "$TOPICS" ] || [ -n "$IDS" ]; then
    FILTER_CONFIG="$OUTDIR/filter-config"
    mkdir -p "$FILTER_CONFIG"
    python3 -c "
import json, sys
topics_filter = '${TOPICS}'.split(',') if '${TOPICS}' else []
ids_filter = '${IDS}'.split(',') if '${IDS}' else []

d = json.load(open('${DEFAULTS}/sources.json'))
filtered = []
for s in d['sources']:
    if ids_filter and s['id'] not in ids_filter:
        continue
    if topics_filter and not any(t in s.get('topics', []) for t in topics_filter):
        continue
    filtered.append(s)

d['sources'] = filtered
print(f'Filtered: {len(filtered)} sources', file=sys.stderr)
json.dump(d, open('${FILTER_CONFIG}/sources.json', 'w'), indent=2)
" 2>&1
    DEFAULTS="$FILTER_CONFIG"
fi

if [ -n "$CONFIG" ]; then
    EXTRA_ARGS+=("--config" "$CONFIG")
fi
if [ -n "$VERBOSE" ]; then
    EXTRA_ARGS+=("$VERBOSE")
fi

echo "🧪 Pipeline Test (hours=$HOURS, outdir=$OUTDIR)"
echo "   Sources: $(python3 -c "import json; d=json.load(open('${DEFAULTS}/sources.json')); types={}
for s in d['sources']: t=s['type']; types[t]=types.get(t,0)+1
print(' | '.join(f'{t}:{n}' for t,n in sorted(types.items())))" 2>/dev/null)"
echo ""

# ── Fetch steps ──

# RSS
if should_run "rss"; then
    run_step "fetch-rss" python3 "$SCRIPT_DIR/fetch-rss.py" --defaults "$DEFAULTS" --hours "$HOURS" --output "$OUTDIR/rss.json" --force "${EXTRA_ARGS[@]}"
    validate_json "$OUTDIR/rss.json" "rss"
else
    echo "⏭  fetch-rss (skipped)"
    SKIPPED=$((SKIPPED + 1))
fi

# GitHub
if should_run "github"; then
    run_step "fetch-github" python3 "$SCRIPT_DIR/fetch-github.py" --defaults "$DEFAULTS" --hours "$HOURS" --output "$OUTDIR/github.json" --force "${EXTRA_ARGS[@]}"
    validate_json "$OUTDIR/github.json" "github"
else
    echo "⏭  fetch-github (skipped)"
    SKIPPED=$((SKIPPED + 1))
fi

# Twitter
if should_run "twitter"; then
    TWITTER_ARGS=("--defaults" "$DEFAULTS" "--hours" "$HOURS" "--output" "$OUTDIR/twitter.json" "--force" "${EXTRA_ARGS[@]}")
    [ -n "$TWITTER_BACKEND" ] && TWITTER_ARGS+=("--backend" "$TWITTER_BACKEND")

    if [ -n "$X_BEARER_TOKEN" ] || [ -n "$TWITTERAPI_IO_KEY" ]; then
        run_step "fetch-twitter" python3 "$SCRIPT_DIR/fetch-twitter.py" "${TWITTER_ARGS[@]}"
        validate_json "$OUTDIR/twitter.json" "twitter"
    else
        echo "⏭  fetch-twitter (no X_BEARER_TOKEN or TWITTERAPI_IO_KEY)"
        SKIPPED=$((SKIPPED + 1))
    fi
else
    echo "⏭  fetch-twitter (skipped)"
    SKIPPED=$((SKIPPED + 1))
fi

# Reddit
if should_run "reddit"; then
    if [ -f "$SCRIPT_DIR/fetch-reddit.py" ]; then
        run_step "fetch-reddit" python3 "$SCRIPT_DIR/fetch-reddit.py" --defaults "$DEFAULTS" --hours "$HOURS" --output "$OUTDIR/reddit.json" --force "${EXTRA_ARGS[@]}"
        validate_json "$OUTDIR/reddit.json" "reddit"
    else
        echo "⏭  fetch-reddit (script not found)"
        SKIPPED=$((SKIPPED + 1))
    fi
else
    echo "⏭  fetch-reddit (skipped)"
    SKIPPED=$((SKIPPED + 1))
fi

# Web search
if should_run "web"; then
    if [ -n "$BRAVE_API_KEY" ]; then
        run_step "fetch-web" python3 "$SCRIPT_DIR/fetch-web.py" --defaults "$DEFAULTS" --freshness pd --output "$OUTDIR/web.json" --force "${EXTRA_ARGS[@]}"
        validate_json "$OUTDIR/web.json" "web"
    else
        echo "⏭  fetch-web (no BRAVE_API_KEY)"
        SKIPPED=$((SKIPPED + 1))
    fi
else
    echo "⏭  fetch-web (skipped)"
    SKIPPED=$((SKIPPED + 1))
fi

# ── Merge ──
MERGE_ARGS=("--output" "$OUTDIR/merged.json")
[ -f "$OUTDIR/rss.json" ]     && MERGE_ARGS+=("--rss" "$OUTDIR/rss.json")
[ -f "$OUTDIR/twitter.json" ] && MERGE_ARGS+=("--twitter" "$OUTDIR/twitter.json")
[ -f "$OUTDIR/web.json" ]     && MERGE_ARGS+=("--web" "$OUTDIR/web.json")
[ -f "$OUTDIR/github.json" ]  && MERGE_ARGS+=("--github" "$OUTDIR/github.json")
[ -f "$OUTDIR/reddit.json" ]  && MERGE_ARGS+=("--reddit" "$OUTDIR/reddit.json")

if [ ${#MERGE_ARGS[@]} -gt 2 ]; then
    run_step "merge-sources" python3 "$SCRIPT_DIR/merge-sources.py" "${MERGE_ARGS[@]}"
    validate_json "$OUTDIR/merged.json" "merged"

    # Validate merged structure
    if python3 -c "
import json, sys
d = json.load(open(sys.argv[1]))
assert 'topics' in d and 'output_stats' in d
stats = d['output_stats']
print(f'   📊 Merged: {stats.get(\"total_articles\", \"?\")} articles across {len(d[\"topics\"])} topics')
" "$OUTDIR/merged.json" 2>/dev/null; then
        echo "✅ merged structure valid"
        PASSED=$((PASSED + 1))
    else
        echo "❌ merged structure invalid"
        FAILED=$((FAILED + 1))
    fi
else
    echo "⏭  merge (no source files to merge)"
    SKIPPED=$((SKIPPED + 1))
fi

# ── Summary ──
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Results: $PASSED passed, $FAILED failed, $SKIPPED skipped"
echo "   Output:  $OUTDIR"
if [ "$KEEP" = false ] && [ "$FAILED" -eq 0 ]; then
    rm -rf "$OUTDIR"
    echo "   (cleaned up — use --keep to preserve)"
fi
[ "$FAILED" -eq 0 ] && exit 0 || exit 1
