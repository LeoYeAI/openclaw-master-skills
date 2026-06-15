#!/usr/bin/env bash
# _curl-retry.sh — Shared retry wrapper for curl calls
# Source this file: source "$SCRIPT_DIR/_curl-retry.sh"
#
# Provides: curl_retry [curl-args...]
# Retries up to 3 times with exponential backoff (2s, 4s) on curl failure.
# Transparent drop-in for curl: same args, same output.

curl_retry() {
  local max_retries="${CURL_MAX_RETRIES:-3}"
  local delay=2
  local attempt=0
  local output exit_code

  while [ $attempt -lt $max_retries ]; do
    exit_code=0
    output=$(curl "$@" 2>/dev/null) || exit_code=$?
    if [ $exit_code -eq 0 ]; then
      printf '%s' "$output"
      return 0
    fi
    attempt=$((attempt + 1))
    if [ $attempt -lt $max_retries ]; then
      sleep $delay
      delay=$((delay * 2))
    fi
  done

  # Final attempt failed — return whatever we got
  printf '%s' "$output"
  return $exit_code
}
