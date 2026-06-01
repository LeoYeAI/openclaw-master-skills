#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/../../assets"
LIB_DIR="$ASSETS_DIR/libs"
WHL_FILE="python_serverless-1.0.3.4.1-py3-none-any.whl"
LOCAL_WHL_PATH="$LIB_DIR/$WHL_FILE"

# 下载源配置
PUBLIC_URL="https://emr-serverless.tos-cn-beijing.volces.com/sdk/python/$WHL_FILE"
INTERNAL_URL="https://emr-serverless.tos-cn-beijing.ivolces.com/sdk/python/$WHL_FILE"

# 创建libs目录
mkdir -p "$LIB_DIR"

# 检查本地文件是否存在
if [[ -f "$LOCAL_WHL_PATH" ]]; then
    echo "使用本地安装包: $LOCAL_WHL_PATH"
    pip install "$LOCAL_WHL_PATH"
    exit 0
fi

echo "本地安装包不存在，开始下载..."

# 下载函数
download_file() {
    local url=$1
    local name=$2
    echo "尝试从$name下载: $url"

    # 使用wget下载，设置超时和重试
    if wget --timeout=30 --tries=3 -O "$LOCAL_WHL_PATH" "$url" 2>/dev/null; then
        echo "从$name下载成功"
        return 0
    else
        echo "从$name下载失败"
        rm -f "$LOCAL_WHL_PATH" 2>/dev/null
        return 1
    fi
}

# 先尝试公网下载
if download_file "$PUBLIC_URL" "公网"; then
    pip install "$LOCAL_WHL_PATH"
    exit 0
fi

# 公网失败后尝试内网下载
if download_file "$INTERNAL_URL" "火山内网"; then
    pip install "$LOCAL_WHL_PATH"
    exit 0
fi

echo "错误: 所有下载源都失败，无法安装serverless SDK"
echo "请检查网络连接或手动下载安装包到: $LOCAL_WHL_PATH"
exit 1