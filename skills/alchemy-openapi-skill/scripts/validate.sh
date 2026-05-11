#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SKILL_DIR="${ROOT_DIR}/skills/alchemy-openapi-skill"
SKILL_FILE="${SKILL_DIR}/SKILL.md"
OPENAI_FILE="${SKILL_DIR}/agents/openai.yaml"
USAGE_FILE="${SKILL_DIR}/references/usage-patterns.md"
SCHEMA_FILE="${SKILL_DIR}/references/alchemy-prices.openapi.json"

fail() {
  printf '[validate] error: %s\n' "$*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "required command not found: $1"
}

need_cmd jq
need_cmd rg

for file in "${SKILL_FILE}" "${OPENAI_FILE}" "${USAGE_FILE}" "${SCHEMA_FILE}"; do
  [[ -f "${file}" ]] || fail "missing required file: ${file}"
done

jq -e '.openapi and .paths' "${SCHEMA_FILE}" >/dev/null 2>&1 || fail 'invalid OpenAPI schema JSON or missing .openapi/.paths'
jq -e '.paths["/tokens/by-symbol"] and .paths["/tokens/by-address"] and .paths["/tokens/historical"]' "${SCHEMA_FILE}" >/dev/null 2>&1 || fail 'OpenAPI schema missing expected Alchemy paths'
jq -e '.paths["/tokens/by-symbol"].get and .paths["/tokens/by-address"].post and .paths["/tokens/historical"].post' "${SCHEMA_FILE}" >/dev/null 2>&1 || fail 'OpenAPI schema must expose GET /tokens/by-symbol and POST /tokens/by-address,/tokens/historical'

rg -q '^name:\s*alchemy-openapi-skill\s*$' "${SKILL_FILE}" || fail 'invalid skill name'
rg -q '^description:\s*.+' "${SKILL_FILE}" || fail 'missing description'

rg -q 'command -v alchemy-openapi-cli' "${SKILL_FILE}" || fail 'missing link-first command check'
rg -q 'uxc link alchemy-openapi-cli https://api.g.alchemy.com --schema-url ' "${SKILL_FILE}" || fail 'missing fixed link create command with schema-url'
rg -F -q 'alchemy-openapi-cli get:/tokens/by-symbol -h' "${SKILL_FILE}" || fail 'missing operation-level help example'
rg -q -- '--path-prefix-template "/prices/v1/\{\{secret\}\}"' "${SKILL_FILE}" || fail 'missing path-prefix auth setup'
rg -q 'uxc auth binding match https://api.g.alchemy.com' "${SKILL_FILE}" || fail 'missing binding match check'
rg -q 'prices-only' "${SKILL_FILE}" || fail 'missing prices-only guardrail'
rg -q 'single `symbols=<TOKEN>` query' "${SKILL_FILE}" || fail 'missing by-symbol single-symbol guidance'

if rg -q -- "--args\\s+'\\{" "${SKILL_FILE}" "${USAGE_FILE}"; then
  fail 'found banned legacy JSON argument pattern'
fi

rg -q '^\s*display_name:\s*"Alchemy Prices API"\s*$' "${OPENAI_FILE}" || fail 'missing display_name'
rg -q '^\s*short_description:\s*".+"\s*$' "${OPENAI_FILE}" || fail 'missing short_description'
rg -q '^\s*default_prompt:\s*".*\$alchemy-openapi-skill.*"\s*$' "${OPENAI_FILE}" || fail 'default_prompt must mention $alchemy-openapi-skill'

echo "skills/alchemy-openapi-skill validation passed"
