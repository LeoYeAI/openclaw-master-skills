#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
URL_INPUT="${1:-https://example.com/demo.mp4}"
CONTENT_INPUT="${2:-}"

[[ -z "${VECTCUT_API_KEY:-}" ]] && echo "ERROR: VECTCUT_API_KEY is required" && exit 1

if [[ -n "$CONTENT_INPUT" ]]; then
  PAYLOAD="{\"url\":\"${URL_INPUT}\",\"content\":\"${CONTENT_INPUT}\"}"
else
  PAYLOAD="{\"url\":\"${URL_INPUT}\"}"
fi

echo "=== CURL DEMO: asr_llm (segments/keywords/en) ==="
RES_LLM="$("${ROOT}/scripts/asr_ops.sh" asr_llm "${PAYLOAD}")"
echo "asr_llm => ${RES_LLM}"

echo "=== CURL DEMO: asr_nlp (segments/phrase/words) ==="
RES_NLP="$("${ROOT}/scripts/asr_ops.sh" asr_nlp "${PAYLOAD}")"
echo "asr_nlp => ${RES_NLP}"

echo "=== CURL DEMO: asr_basic (result.raw.result.utterances) ==="
RES_BASIC="$("${ROOT}/scripts/asr_ops.sh" asr_basic "${PAYLOAD}")"
echo "asr_basic => ${RES_BASIC}"

echo "=== DONE ==="