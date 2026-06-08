#!/bin/bash
# 启动 Khoj 服务

set -e

# 配置
KHOJ_PORT="${KHOJ_PORT:-42110}"
KHOJ_URL="http://localhost:${KHOJ_PORT}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}启动 Khoj RAG 服务...${NC}"

# 检查是否已运行
if curl -s "${KHOJ_URL}/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Khoj 服务已在运行${NC}"
    echo "  地址: ${KHOJ_URL}"
    exit 0
fi

# 检查依赖
if ! command -v khoj &> /dev/null; then
    echo -e "${RED}✗ khoj 未安装${NC}"
    echo "  请运行: pip install khoj"
    exit 1
fi

# 启动服务（嵌入式 PostgreSQL 模式）
export USE_EMBEDDED_DB="true"

nohup khoj --anonymous-mode > /tmp/khoj.log 2>&1 &

# 等待启动
echo -n "  等待服务启动"
for i in {1..30}; do
    if curl -s "${KHOJ_URL}/api/health" > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓ Khoj 服务已启动${NC}"
        echo "  地址: ${KHOJ_URL}"
        echo "  日志: /tmp/khoj.log"
        exit 0
    fi
    echo -n "."
    sleep 1
done

echo ""
echo -e "${RED}✗ 服务启动超时${NC}"
echo "  查看日志: cat /tmp/khoj.log"
exit 1