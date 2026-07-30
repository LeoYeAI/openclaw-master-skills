#!/usr/bin/env bash
set -euo pipefail

CONTACT=""
TYPE=""
NAME=""
SECURITY="CONTACT"
LANGUAGE="ENG"
DATA=""
REDIRECT=""
INTERNAL_ID=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --contact) CONTACT="$2"; shift 2 ;;
    --type) TYPE="$2"; shift 2 ;;
    --name) NAME="$2"; shift 2 ;;
    --security) SECURITY="$2"; shift 2 ;;
    --language) LANGUAGE="$2"; shift 2 ;;
    --data) DATA="$2"; shift 2 ;;
    --redirect) REDIRECT="$2"; shift 2 ;;
    --internal-id) INTERNAL_ID="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$CONTACT" || -z "$TYPE" || -z "$NAME" ]]; then
  echo '{"error": "Missing required arguments: --contact, --type, --name"}' >&2
  exit 1
fi

if [[ ! "$TYPE" =~ ^(document|form|json|consent)$ ]]; then
  echo '{"error": "Invalid --type. Must be: document, form, json, or consent"}' >&2
  exit 1
fi

source "$(dirname "$0")/sign-request.sh"

TYPE_UPPER=$(printf '%s' "$TYPE" | tr '[:lower:]' '[:upper:]')
RAW_DATA_JSON="${DATA:-null}"

if [[ "$TYPE_UPPER" == "FORM" ]]; then
  echo '{"error":"FORM is not supported as inline credential data. Use an existing form resource ID (resourcesIds/groupIds) instead."}' >&2
  exit 1
fi

DATA_ARRAY=$(jq -cn \
  --arg type "$TYPE_UPPER" \
  --arg name "$NAME" \
  --argjson raw "${RAW_DATA_JSON}" '
  def ensure_array:
    if . == null then []
    elif (type == "array") then .
    else [.] end;

  def with_hidden_default:
    map(if (has("hidden")) then . else . + {hidden:false} end);

  if $type == "CONSENT" then
    (
      if $raw == null then
        [{label:"text", type:"string", value:("I consent to " + $name), hidden:false}]
      elif ($raw | type) == "string" then
        [{label:"text", type:"string", value:$raw, hidden:false}]
      elif ($raw | type) == "object" and ($raw | has("text")) then
        [{label:"text", type:"string", value:$raw.text, hidden:false}]
      else
        ($raw | ensure_array | with_hidden_default)
      end
    )
    | if any(.[]; .label == "text" and ((.type|ascii_downcase) == "string") and (.hidden == false) and ((.value|tostring|length) > 0))
      then .
      else error("CONSENT requires at least one field: {\"label\":\"text\",\"type\":\"string\",\"value\":\"...\",\"hidden\":false}")
      end
  elif $type == "DOCUMENT" then
    (
      ($raw | ensure_array | with_hidden_default)
      | if any(.[]; .label == "pdf" and ((.type|ascii_downcase) == "pdf") and (.hidden == false) and ((.value|tostring|length) > 0))
        then .
        else error("DOCUMENT requires at least one field: {\"label\":\"pdf\",\"type\":\"pdf\",\"value\":\"<base64>\",\"hidden\":false}")
        end
    )
  else
    (
      if $raw == null then
        [{label:"text", type:"string", value:$name, hidden:false}]
      else
        ($raw | ensure_array | with_hidden_default)
      end
    )
  end
')

CREDENTIALS=$(jq -cn \
  --arg type "$TYPE_UPPER" \
  --arg name "$NAME" \
  --argjson data "$DATA_ARRAY" \
  '[{
    "type": $type,
    "name": $name,
    "required": true,
    "data": $data
  }]')

BODY=$(jq -cn \
  --arg contact "$CONTACT" \
  --argjson credentials "$CREDENTIALS" \
  --arg security "$SECURITY" \
  --arg language "$LANGUAGE" \
  --arg redirect "$REDIRECT" \
  --arg internalId "$INTERNAL_ID" \
  '{
    "contacts": [$contact],
    "securityLevel": $security,
    "credentials": $credentials,
    "language": $language
  }
  | if $redirect != "" then . + {"redirectUrl": $redirect} else . end
  | if $internalId != "" then . + {"internalId": $internalId} else . end')

via_curl POST /v1/request "$BODY"
