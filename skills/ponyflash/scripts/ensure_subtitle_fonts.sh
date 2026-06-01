#!/usr/bin/env bash
# SECURITY MANIFEST:
#   Environment variables accessed: HOME, PONYFLASH_FONT_DIR, PONYFLASH_NOTO_FONT_URL
#   External endpoints called:
#     - https://mirrors.aliyun.com/CTAN/fonts/notocjksc/NotoSansCJKsc-Regular.otf
#     - https://cdn.jsdelivr.net/gh/notofonts/noto-cjk@main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf
#   Local files read: downloaded font cache paths under the selected font directory
#   Local files written: downloaded font cache paths under the selected font directory
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ensure_subtitle_fonts.sh [--font-dir <dir>] [--quiet] [--help]

Options:
  --font-dir <dir>  Override the download/cache directory.
  --quiet           Print only the resolved font path.
  --help            Show this help message.
EOF
}

font_dir="${PONYFLASH_FONT_DIR:-$HOME/.cache/ponyflash/fonts}"
quiet=0
font_filename="NotoSansCJKsc-Regular.otf"
primary_url="${PONYFLASH_NOTO_FONT_URL:-https://mirrors.aliyun.com/CTAN/fonts/notocjksc/NotoSansCJKsc-Regular.otf}"
fallback_url="https://cdn.jsdelivr.net/gh/notofonts/noto-cjk@main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --font-dir)
      font_dir="${2:-}"
      [[ -n "$font_dir" ]] || { echo "Missing value for --font-dir" >&2; exit 2; }
      shift 2
      ;;
    --quiet)
      quiet=1
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

font_dir="${font_dir/#\~/$HOME}"
font_path="$font_dir/$font_filename"

download_font() {
  local url="$1"
  local tmp_path="$font_path.tmp"

  if command -v curl >/dev/null 2>&1; then
    curl --fail --location --silent --show-error "$url" --output "$tmp_path"
  elif command -v wget >/dev/null 2>&1; then
    wget -q -O "$tmp_path" "$url"
  else
    echo "Missing downloader: need curl or wget to fetch subtitle fonts." >&2
    return 2
  fi

  mv "$tmp_path" "$font_path"
}

mkdir -p "$font_dir"

if [[ ! -s "$font_path" ]]; then
  rm -f "$font_path.tmp"
  if ! download_font "$primary_url"; then
    rm -f "$font_path.tmp"
    download_font "$fallback_url"
  fi
fi

if [[ ! -s "$font_path" ]]; then
  echo "Failed to prepare subtitle font: $font_path" >&2
  exit 1
fi

if [[ $quiet -eq 1 ]]; then
  printf '%s\n' "$font_path"
else
  echo "font_name=Noto Sans CJK SC"
  echo "font_dir=$font_dir"
  echo "font_file=$font_path"
fi
