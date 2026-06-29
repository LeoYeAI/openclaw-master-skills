#!/usr/bin/env bash
# ============================================================
# build_linux.sh  --  编译 libctp_bridge.so (Linux x64)
# 依赖: g++ 9+ (sudo apt install g++)
# SDK: TraderAPI 6.7.11 (20250617) + MdUserAPI 6.7.11 (20250617)
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# ---------- SDK 路径 ----------
LINUX_SDK="$REPO_ROOT/api/linux"

# ---------- 检查依赖 ----------
if [ ! -f "$LINUX_SDK/thosttraderapi_se.so" ]; then
    echo "[ERROR] TraderAPI .so 未找到: $LINUX_SDK/thosttraderapi_se.so"
    exit 1
fi
if [ ! -f "$LINUX_SDK/thostmduserapi_se.so" ]; then
    echo "[ERROR] MdUserAPI .so 未找到: $LINUX_SDK/thostmduserapi_se.so"
    exit 1
fi

# ---------- 输出目录 ----------
OUT_DIR="$SCRIPT_DIR/../"

echo "[INFO] 编译 libctp_bridge.so ..."

g++ \
    -shared -fPIC -fvisibility=hidden \
    -std=c++17 -O2 \
    -DCTPBRIDGE_EXPORTS \
    -I"$LINUX_SDK" \
    "$SCRIPT_DIR/ctp_bridge.cpp" \
    -L"$LINUX_SDK" \
    -lthosttraderapi_se \
    -lthostmduserapi_se \
    -Wl,-rpath,'$ORIGIN' \
    -o "${OUT_DIR}libctp_bridge.so"

# 拷贝 CTP .so 到输出目录（运行时需要与 libctp_bridge.so 同目录）
cp -f "$LINUX_SDK/thosttraderapi_se.so"  "$OUT_DIR"
cp -f "$LINUX_SDK/thostmduserapi_se.so"  "$OUT_DIR"

echo ""
echo "[OK] 编译成功，输出文件："
echo "     ${OUT_DIR}libctp_bridge.so"
echo "     ${OUT_DIR}thosttraderapi_se.so"
echo "     ${OUT_DIR}thostmduserapi_se.so"
