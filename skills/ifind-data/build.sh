#!/usr/bin/env bash
# ═══════════════════════════════════════════════════
# ifind-api 构建 / 部署管理脚本
# ═══════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="${SCRIPT_DIR}/scripts/ifind-api"
DIST_DIR="${SCRIPT_DIR}/dist"
BINARY_NAME="ifind-api"

NAS_HOST="nas-ubuntu"
NAS_PATH="~/.openclaw/skills/ifind-data/scripts"

# 平台列表: OS/ARCH
PLATFORMS=(
  "linux/amd64"
  "darwin/arm64"
  "windows/amd64"
)

build_one() {
  local os_arch="$1"
  local goos="${os_arch%%/*}"
  local goarch="${os_arch##*/}"
  local output="${DIST_DIR}/${BINARY_NAME}-${goos}-${goarch}"
  if [ "$goos" = "windows" ]; then
    output="${output}.exe"
  fi

  echo "  Building ${goos}/${goarch} ..."
  (cd "$SRC_DIR" && GOOS="$goos" GOARCH="$goarch" go build \
    -ldflags="-s -w" \
    -o "$output" \
    .)
  echo "  → $(basename "$output")"
}

cmd_build() {
  local filter="${1:-}"
  mkdir -p "$DIST_DIR"

  # go mod tidy
  (cd "$SRC_DIR" && go mod tidy)

  for platform in "${PLATFORMS[@]}"; do
    local goos="${platform%%/*}"
    if [ -n "$filter" ] && [ "$filter" != "$goos" ]; then
      continue
    fi
    build_one "$platform"
  done

  echo ""
  echo "Build complete:"
  ls -lh "$DIST_DIR"/
}

cmd_deploy() {
  echo "=== Building linux/amd64 ==="
  mkdir -p "$DIST_DIR"
  (cd "$SRC_DIR" && go mod tidy)
  build_one "linux/amd64"

  local binary="${DIST_DIR}/${BINARY_NAME}-linux-amd64"

  echo ""
  echo "=== Deploying to ${NAS_HOST} ==="
  scp "$binary" "${NAS_HOST}:${NAS_PATH}/${BINARY_NAME}"
  ssh "$NAS_HOST" "chmod +x ${NAS_PATH}/${BINARY_NAME}"
  ssh "$NAS_HOST" "rm -f ${NAS_PATH}/ifind-api.sh"

  echo ""
  echo "Deploy complete. Old .sh removed."
}

cmd_clean() {
  echo "Cleaning dist/ ..."
  rm -rf "$DIST_DIR"
  echo "Done."
}

# ─── 入口 ───
case "${1:-}" in
  deploy)
    cmd_deploy
    ;;
  clean)
    cmd_clean
    ;;
  linux|darwin|windows)
    cmd_build "$1"
    ;;
  ""|all)
    cmd_build ""
    ;;
  *)
    echo "用法: ./build.sh [linux|darwin|windows|deploy|clean]"
    echo ""
    echo "  (无参数)   编译全部 3 个平台"
    echo "  linux      只编译 linux/amd64"
    echo "  darwin     只编译 darwin/arm64"
    echo "  windows    只编译 windows/amd64"
    echo "  deploy     编译 linux + scp 部署到 NAS"
    echo "  clean      清理 dist/"
    exit 1
    ;;
esac
