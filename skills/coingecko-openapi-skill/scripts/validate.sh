#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SKILL_DIR="${ROOT_DIR}/skills/coingecko-openapi-skill"
SKILL_FILE="${SKILL_DIR}/SKILL.md"
OPENAI_FILE="${SKILL_DIR}/agents/openai.yaml"
USAGE_FILE="${SKILL_DIR}/references/usage-patterns.md"
SCHEMA_FILE="${SKILL_DIR}/references/coingecko-market.openapi.json"

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
jq -e '.paths["/simple/price"] and .paths["/onchain/networks"]' "${SCHEMA_FILE}" >/dev/null 2>&1 || fail 'OpenAPI schema missing expected CoinGecko or GeckoTerminal paths'

rg -q '^name:\s*coingecko-openapi-skill\s*$' "${SKILL_FILE}" || fail 'invalid skill name'
rg -q '^description:\s*.+' "${SKILL_FILE}" || fail 'missing description'

rg -q 'command -v coingecko-openapi-cli' "${SKILL_FILE}" || fail 'missing link-first command check'
rg -q 'uxc link coingecko-openapi-cli https://api.coingecko.com/api/v3 --schema-url ' "${SKILL_FILE}" || fail 'missing fixed link create command with schema-url'
rg -q 'coingecko-openapi-cli -h' "${SKILL_FILE}" || fail 'missing help-first host discovery example'
rg -q 'coingecko-openapi-cli get:/simple/price -h' "${SKILL_FILE}" || fail 'missing operation-level help example'
rg -q -- '--api-key-header x-cg-demo-api-key' "${SKILL_FILE}" || fail 'missing demo api key setup'
rg -q 'uxc auth binding match https://api.coingecko.com/api/v3' "${SKILL_FILE}" || fail 'missing binding match check'
rg -q 'x-cg-pro-api-key' "${SKILL_FILE}" || fail 'missing pro override guidance'
rg -q 'pro-api.coingecko.com' "${SKILL_FILE}" "${USAGE_FILE}" || fail 'missing pro host binding guidance'
rg -q 'read-only' "${SKILL_FILE}" || fail 'missing read-only guardrail'

if rg -q -- "--args\\s+'\\{" "${SKILL_FILE}" "${USAGE_FILE}"; then
  fail 'found banned legacy JSON argument pattern'
fi

rg -q '^\s*display_name:\s*"CoinGecko And GeckoTerminal"\s*$' "${OPENAI_FILE}" || fail 'missing display_name'
rg -q '^\s*short_description:\s*".+"\s*$' "${OPENAI_FILE}" || fail 'missing short_description'
rg -q '^\s*default_prompt:\s*".*\$coingecko-openapi-skill.*"\s*$' "${OPENAI_FILE}" || fail 'default_prompt must mention $coingecko-openapi-skill'

echo "skills/coingecko-openapi-skill validation passed"
