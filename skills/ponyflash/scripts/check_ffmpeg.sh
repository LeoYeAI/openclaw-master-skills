#!/usr/bin/env bash
# SECURITY MANIFEST:
#   Environment variables accessed: PATH
#   External endpoints called: none
#   Local files read: none
#   Local files written: none
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  check_ffmpeg.sh [--quiet] [--profile basic|full] [--require-basic-editing] [--require-subtitle-support] [--require-subtitles-filter] [--require-drawtext-filter] [--help]

Options:
  --quiet                     Only print failure messages.
  --profile <name>            Capability profile: basic or full.
  --require-basic-editing     Fail unless ffprobe, libx264, and aac encoding are available.
  --require-subtitle-support  Fail unless subtitles or drawtext is available.
  --require-subtitles-filter  Fail unless the subtitles filter is available.
  --require-drawtext-filter   Fail unless the drawtext filter is available.
  --help                      Show this help message.
EOF
}

has_filter() {
  local ffmpeg_path="$1"
  local filter_name="$2"

  "$ffmpeg_path" -hide_banner -filters 2>/dev/null | awk -v name="$filter_name" '
    $2 == name { found=1 }
    END { exit(found ? 0 : 1) }
  '
}

has_encoder() {
  local ffmpeg_path="$1"
  local encoder_name="$2"

  "$ffmpeg_path" -hide_banner -encoders 2>/dev/null | awk -v name="$encoder_name" '
    $2 == name { found=1 }
    END { exit(found ? 0 : 1) }
  '
}

quiet=0
require_basic_editing=0
require_subtitle_support=0
require_subtitles_filter=0
require_drawtext_filter=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --quiet)
      quiet=1
      shift
      ;;
    --profile)
      case "${2:-}" in
        basic)
          require_basic_editing=1
          ;;
        full)
          require_basic_editing=1
          require_subtitles_filter=1
          ;;
        *)
          echo "Unsupported profile: ${2:-}" >&2
          usage >&2
          exit 2
          ;;
      esac
      shift 2
      ;;
    --require-basic-editing)
      require_basic_editing=1
      shift
      ;;
    --require-subtitle-support)
      require_subtitle_support=1
      shift
      ;;
    --require-subtitles-filter)
      require_subtitles_filter=1
      shift
      ;;
    --require-drawtext-filter)
      require_drawtext_filter=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

os_name="$(uname -s 2>/dev/null | tr '[:upper:]' '[:lower:]')"
ffmpeg_bin="$(command -v ffmpeg || true)"
ffprobe_bin="$(command -v ffprobe || true)"

if [[ $quiet -eq 0 ]]; then
  echo "platform=${os_name:-unknown}"
  echo "path=$PATH"
fi

missing=0
capability_missing=0
subtitles_filter="missing"
drawtext_filter="missing"
subtitle_support="missing"
libx264_encoder="missing"
aac_encoder="missing"
basic_editing_support="missing"

if [[ -n "$ffmpeg_bin" ]]; then
  if has_encoder "$ffmpeg_bin" "libx264"; then
    libx264_encoder="available"
  fi

  if has_encoder "$ffmpeg_bin" "aac"; then
    aac_encoder="available"
  fi

  if [[ "$libx264_encoder" == "available" && "$aac_encoder" == "available" ]]; then
    basic_editing_support="available"
  fi

  if has_filter "$ffmpeg_bin" "subtitles"; then
    subtitles_filter="available"
  fi

  if has_filter "$ffmpeg_bin" "drawtext"; then
    drawtext_filter="available"
  fi

  if [[ "$subtitles_filter" == "available" && "$drawtext_filter" == "available" ]]; then
    subtitle_support="full"
  elif [[ "$subtitles_filter" == "available" ]]; then
    subtitle_support="subtitles_only"
  elif [[ "$drawtext_filter" == "available" ]]; then
    subtitle_support="drawtext_only"
  fi

  if [[ $quiet -eq 0 ]]; then
    ffmpeg_version="$("$ffmpeg_bin" -version 2>/dev/null | awk 'NR==1 { print $0 }')"
    echo "ffmpeg=installed"
    echo "ffmpeg_path=$ffmpeg_bin"
    echo "ffmpeg_version=${ffmpeg_version:-unknown}"
    echo "libx264_encoder=$libx264_encoder"
    echo "aac_encoder=$aac_encoder"
    echo "basic_editing_support=$basic_editing_support"
    echo "subtitles_filter=$subtitles_filter"
    echo "drawtext_filter=$drawtext_filter"
    echo "subtitle_support=$subtitle_support"
  fi
else
  echo "ffmpeg=missing"
  missing=1
fi

if [[ -n "$ffprobe_bin" ]]; then
  if [[ $quiet -eq 0 ]]; then
    ffprobe_version="$("$ffprobe_bin" -version 2>/dev/null | awk 'NR==1 { print $0 }')"
    echo "ffprobe=installed"
    echo "ffprobe_path=$ffprobe_bin"
    echo "ffprobe_version=${ffprobe_version:-unknown}"
  fi
else
  echo "ffprobe=missing"
  missing=1
fi

if [[ $missing -eq 0 ]]; then
  if [[ $require_basic_editing -eq 1 && "$basic_editing_support" != "available" ]]; then
    echo "Missing capability: basic editing support requires libx264 and aac encoders." >&2
    capability_missing=1
  fi

  if [[ $require_subtitle_support -eq 1 && "$subtitle_support" == "missing" ]]; then
    echo "Missing capability: subtitles or drawtext filter is required." >&2
    capability_missing=1
  fi

  if [[ $require_subtitles_filter -eq 1 && "$subtitles_filter" != "available" ]]; then
    echo "Missing capability: subtitles filter is required." >&2
    capability_missing=1
  fi

  if [[ $require_drawtext_filter -eq 1 && "$drawtext_filter" != "available" ]]; then
    echo "Missing capability: drawtext filter is required." >&2
    capability_missing=1
  fi
fi

if [[ $missing -ne 0 ]]; then
  [[ $quiet -eq 0 ]] && echo "status=missing_dependencies"
  exit 1
fi

if [[ $capability_missing -ne 0 ]]; then
  [[ $quiet -eq 0 ]] && echo "status=missing_capabilities"
  exit 3
fi

[[ $quiet -eq 0 ]] && echo "status=ready"
exit 0
