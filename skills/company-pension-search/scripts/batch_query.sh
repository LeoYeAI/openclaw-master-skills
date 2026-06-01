#!/bin/bash
# 企业年金批量查询脚本 v2.0
# 用法：./batch_query.sh [公司列表文件] [输出目录]

set -e

COMPANY_LIST_FILE="${1:-}"
OUTPUT_DIR="${2:-./batch_reports}"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 帮助信息
show_help() {
    cat << EOF
企业年金批量查询脚本 v2.0

用法：$0 [公司列表文件] [输出目录]

参数:
  公司列表文件    包含公司名称的文件，每行一个（必填）
  输出目录        报告输出目录（可选，默认：./batch_reports）

示例:
  $0 companies.txt
  $0 companies.txt ./output

公司列表文件格式:
  腾讯公司
  阿里巴巴
  字节跳动
  华为

EOF
    exit 0
}

# 检查参数
if [ -z "$COMPANY_LIST_FILE" ]; then
    log_error "公司列表文件不能为空"
    show_help
fi

if [ ! -f "$COMPANY_LIST_FILE" ]; then
    log_error "文件不存在：$COMPANY_LIST_FILE"
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 统计
TOTAL=0
SUCCESS=0
FAILED=0

log_info "开始批量查询"
log_info "公司列表：$COMPANY_LIST_FILE"
log_info "输出目录：$OUTPUT_DIR"
echo ""

# 读取公司列表并逐个查询
while IFS= read -r company || [ -n "$company" ]; do
    # 跳过空行和注释
    [[ -z "$company" || "$company" =~ ^# ]] && continue
    
    TOTAL=$((TOTAL + 1))
    
    echo "═══════════════════════════════════════════"
    echo "  🔍 调查 [$TOTAL]: $company"
    echo "═══════════════════════════════════════════"
    echo ""
    
    # 执行查询
    if bash "$SCRIPT_DIR/search.sh" "$company" deep > "$OUTPUT_DIR/${company}_search_log.txt" 2>&1; then
        log_success "✓ $company 调查完成"
        SUCCESS=$((SUCCESS + 1))
        
        # 生成报告
        bash "$SCRIPT_DIR/generate_report.sh" "$company" "" "$OUTPUT_DIR" 2>/dev/null || true
    else
        log_error "✗ $company 调查失败"
        FAILED=$((FAILED + 1))
    fi
    
    echo ""
done < "$COMPANY_LIST_FILE"

# 生成汇总报告
SUMMARY_FILE="$OUTPUT_DIR/批量查询汇总_$(date +"%Y-%m-%d_%H-%M-%S").md"

cat > "$SUMMARY_FILE" << EOF
# 企业年金批量查询汇总报告

**生成时间**：$(date +"%Y-%m-%d %H:%M")  
**公司列表**：$COMPANY_LIST_FILE  
**输出目录**：$OUTPUT_DIR

---

## 📊 查询统计

| 指标 | 数量 |
|------|------|
| 总公司数 | $TOTAL |
| 成功 | $SUCCESS |
| 失败 | $FAILED |
| 成功率 | $(awk "BEGIN {printf \"%.1f\", ($SUCCESS/$TOTAL)*100}")% |

---

## 📋 公司列表

### 成功查询
$(for i in $(seq 1 $SUCCESS); do echo "- [ ] 待填写"; done)

### 失败查询
$(for i in $(seq 1 $FAILED); do echo "- [ ] 待填写"; done)

---

## 📄 详细报告

详细报告文件位于：$OUTPUT_DIR/

---

**生成工具**：company-pension-search v2.0
EOF

log_success "批量查询完成！"
echo ""
echo "═══════════════════════════════════════════"
echo "  📊 统计结果："
echo "  总计：$TOTAL 家"
echo "  成功：$SUCCESS 家"
echo "  失败：$FAILED 家"
echo "  成功率：$(awk "BEGIN {printf \"%.1f\", ($SUCCESS/$TOTAL)*100}")%"
echo ""
echo "  📄 汇总报告：$SUMMARY_FILE"
echo "═══════════════════════════════════════════"
