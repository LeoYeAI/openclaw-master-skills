#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SKILL_DIR="${ROOT_DIR}/skills/moralis-openapi-skill"
SKILL_FILE="${SKILL_DIR}/SKILL.md"
OPENAI_FILE="${SKILL_DIR}/agents/openai.yaml"
USAGE_FILE="${SKILL_DIR}/references/usage-patterns.md"
SCHEMA_FILE="${SKILL_DIR}/references/moralis-evm.openapi.json"

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

jq -e '.openapi and .paths and .components' "${SCHEMA_FILE}" >/dev/null 2>&1 || fail 'invalid OpenAPI schema JSON or missing .openapi/.paths/.components'
jq -e '.paths["/{address}/balance"] and .paths["/erc20/{address}/price"]' "${SCHEMA_FILE}" >/dev/null 2>&1 || fail 'OpenAPI schema missing expected Moralis paths'

rg -q '^name:\s*moralis-openapi-skill\s*$' "${SKILL_FILE}" || fail 'invalid skill name'
rg -q '^description:\s*.+' "${SKILL_FILE}" || fail 'missing description'

rg -q 'command -v moralis-openapi-cli' "${SKILL_FILE}" || fail 'missing link-first command check'
rg -q 'uxc link moralis-openapi-cli https://deep-index.moralis.io/api/v2.2 --schema-url ' "${SKILL_FILE}" || fail 'missing fixed link create command with schema-url'
rg -F -q 'moralis-openapi-cli get:/{address}/balance -h' "${SKILL_FILE}" || fail 'missing operation-level help example'
rg -q -- '--api-key-header X-API-Key' "${SKILL_FILE}" || fail 'missing X-API-Key auth setup'
rg -q 'uxc auth binding match https://deep-index.moralis.io/api/v2.2' "${SKILL_FILE}" || fail 'missing binding match check'
rg -q 'read-only' "${SKILL_FILE}" || fail 'missing read-only guardrail'

if rg -q -- "--args\\s+'\\{" "${SKILL_FILE}" "${USAGE_FILE}"; then
  fail 'found banned legacy JSON argument pattern'
fi

rg -q '^\s*display_name:\s*"Moralis Web3 Data API"\s*$' "${OPENAI_FILE}" || fail 'missing display_name'
rg -q '^\s*short_description:\s*".+"\s*$' "${OPENAI_FILE}" || fail 'missing short_description'
rg -q '^\s*default_prompt:\s*".*\$moralis-openapi-skill.*"\s*$' "${OPENAI_FILE}" || fail 'default_prompt must mention $moralis-openapi-skill'

echo "skills/moralis-openapi-skill validation passed"
