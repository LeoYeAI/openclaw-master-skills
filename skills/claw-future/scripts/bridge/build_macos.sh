#!/usr/bin/env bash
# ============================================================
# build_macos.sh  --  编译 libctp_bridge.dylib (macOS)
# 依赖: Xcode Command Line Tools  (xcode-select --install)
# SDK: TraderAPI 6.7.7 + MdUserAPI 6.7.7
#
# 输出到 scripts/ 目录：
#   libctp_bridge.dylib        <- 桥接库
#   thosttraderapi_se           <- CTP TraderAPI dylib
#   thostmduserapi_se           <- CTP MdUserAPI dylib
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# ---------- SDK 路径 ----------
MAC_API="$REPO_ROOT/api/macos"
TD_FW="$MAC_API/thosttraderapi_se.framework"
MD_FW="$MAC_API/thostmduserapi_se.framework"
TD_INC="$TD_FW/Versions/A/Headers"
MD_INC="$MD_FW/Versions/A/Headers"
TD_DYLIB="$TD_FW/Versions/A/thosttraderapi_se"
MD_DYLIB="$MD_FW/Versions/A/thostmduserapi_se"

# ---------- 检查依赖 ----------
if [ ! -f "$TD_DYLIB" ]; then
    echo "[ERROR] TraderAPI dylib 未找到: $TD_DYLIB"
    exit 1
fi
if [ ! -f "$MD_DYLIB" ]; then
    echo "[ERROR] MdUserAPI dylib 未找到: $MD_DYLIB"
    exit 1
fi

# ---------- 输出目录（scripts/）----------
OUT_DIR="$SCRIPT_DIR/../"

echo "[INFO] 编译 libctp_bridge.dylib ..."

# -liconv: macOS 上 iconv 需要显式链接
clang++ \
    -shared -fPIC -fvisibility=hidden \
    -std=c++17 -O2 \
    -DCTPBRIDGE_EXPORTS \
    -I"$TD_INC" -I"$MD_INC" \
    "$SCRIPT_DIR/ctp_bridge.cpp" \
    "$TD_DYLIB" "$MD_DYLIB" \
    -liconv \
    -install_name @rpath/libctp_bridge.dylib \
    -Wl,-rpath,@loader_path \
    -o "${OUT_DIR}libctp_bridge.dylib"

# ---------- 拷贝 CTP dylib 到 scripts/ ----------
cp -f "$TD_DYLIB" "${OUT_DIR}thosttraderapi_se"
cp -f "$MD_DYLIB" "${OUT_DIR}thostmduserapi_se"
install_name_tool -id "@rpath/thosttraderapi_se" "${OUT_DIR}thosttraderapi_se"
install_name_tool -id "@rpath/thostmduserapi_se" "${OUT_DIR}thostmduserapi_se"

echo ""
echo "[OK] 编译成功，输出文件（均在 scripts/ 目录）："
echo "     ${OUT_DIR}libctp_bridge.dylib"
echo "     ${OUT_DIR}thosttraderapi_se"
echo "     ${OUT_DIR}thostmduserapi_se"
echo ""
echo "[提示] 三个文件须在同一目录，运行时无需设置 DYLD_FRAMEWORK_PATH。"
