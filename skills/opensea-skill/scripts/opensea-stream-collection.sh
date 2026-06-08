#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: opensea-stream-collection.sh <collection_slug|*>" >&2
  exit 1
fi

slug="$1"
key="${OPENSEA_API_KEY:-}"

if [ -z "$key" ]; then
  echo "OPENSEA_API_KEY is required" >&2
  exit 1
fi

url="wss://stream.openseabeta.com/socket/websocket?token=${key}"
join="{\"topic\":\"collection:${slug}\",\"event\":\"phx_join\",\"payload\":{},\"ref\":1}"
heartbeat="{\"topic\":\"phoenix\",\"event\":\"heartbeat\",\"payload\":{},\"ref\":0}"

if command -v websocat >/dev/null 2>&1; then
  {
    printf '%s\n' "$join"
    while sleep 30; do
      printf '%s\n' "$heartbeat"
    done
  } | websocat -t "$url"
  exit 0
fi

if command -v wscat >/dev/null 2>&1; then
  cat <<INFO
wscat is installed, but it does not auto-send join/heartbeat.
Run: wscat -c "$url"
Then send:
$join
And every ~30s:
$heartbeat
INFO
  exit 0
fi

echo "Install websocat (preferred) or wscat to use the Stream API." >&2
exit 1
