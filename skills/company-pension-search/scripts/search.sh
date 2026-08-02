#!/bin/bash
# 企业年金查询自动化脚本 v2.0
# 用法：./search.sh "企业名称" [搜索类型] [输出格式]
# 搜索类型：all(默认) / official / recruitment / social / financial / deep
# 输出格式：text(默认) / json / markdown

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 默认配置
COMPANY_NAME="$1"
SEARCH_TYPE="${2:-all}"
OUTPUT_FORMAT="${3:-text}"
MAX_RESULTS="${MAX_RESULTS:-20}"
TIMEOUT="${TIMEOUT:-30}"

# 依赖检查
check_dependencies() {
    local missing=()
    if ! command -v curl &> /dev/null; then
        missing+=("curl")
    fi
    if ! command -v jq &> /dev/null; then
        missing+=("jq")
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        log_error "缺少依赖：${missing[*]}"
        echo "请先安装依赖："
        echo "  Ubuntu/Debian: sudo apt install -y ${missing[*]}"
        echo "  macOS: brew install ${missing[*]}"
        exit 1
    fi
}

# 执行依赖检查
check_dependencies

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 帮助信息
show_help() {
    cat << EOF
企业年金查询自动化脚本 v2.0

用法：$0 "企业名称" [搜索类型] [输出格式]

参数:
  企业名称      要查询的企业/单位名称（必填）
  搜索类型      搜索类型（可选，默认：all）
                - all: 全面搜索
                - official: 官方渠道
                - recruitment: 招聘信息
                - social: 员工分享
                - financial: 财务/年报
                - deep: 深度调查（所有方法）
  输出格式      输出格式（可选，默认：text）
                - text: 纯文本
                - json: JSON 格式
                - markdown: Markdown 格式

环境变量:
  TAVILY_API_KEY    Tavily 搜索 API Key（可选）
  SEARXNG_URL       SearXNG 实例 URL（可选，默认：http://localhost:8080）
  MAX_RESULTS       最大搜索结果数（可选，默认：20）
  TIMEOUT           搜索超时时间（秒，可选，默认：30）

示例:
  $0 "腾讯公司"                    # 基础搜索
  $0 "腾讯公司" deep               # 深度调查
  $0 "腾讯公司" official json      # 官方渠道，JSON 输出
  $0 "深圳市大数据资源管理中心" recruitment  # 招聘信息

EOF
    exit 0
}

# 检查参数
if [ "$COMPANY_NAME" = "--help" ] || [ "$COMPANY_NAME" = "-h" ]; then
    show_help
fi

if [ -z "$COMPANY_NAME" ]; then
    log_error "企业名称不能为空"
    echo ""
    show_help
fi

# 检测可用的搜索工具
detect_search_tool() {
    if [ -n "$TAVILY_API_KEY" ]; then
        echo "tavily"
    elif [ -n "$SEARXNG_URL" ]; then
        echo "searxng"
    else
        # 尝试使用项目内的 searxng 脚本
        local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        local searxng_script="/home/admin/.openclaw/workspace/skills/searxng/scripts/searxng.py"
        if [ -f "$searxng_script" ]; then
            echo "searxng_local"
        else
            echo "none"
        fi
    fi
}

# Tavily 搜索
tavily_search() {
    local query="$1"
    local max_results="${2:-10}"
    
    local tavily_script="/home/admin/.openclaw/workspace/skills/tavily-search-skill/search.sh"
    
    if [ -f "$tavily_script" ]; then
        chmod +x "$tavily_script" 2>/dev/null || true
        export TAVILY_API_KEY
        bash "$tavily_script" "$query" "$max_results" 2>/dev/null
    else
        log_error "Tavily 脚本不存在：$tavily_script"
        return 1
    fi
}

# SearXNG 搜索
searxng_search() {
    local query="$1"
    local max_results="${2:-10}"
    
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local searxng_script="/home/admin/.openclaw/workspace/skills/searxng/scripts/searxng.py"
    
    if [ -f "$searxng_script" ]; then
        python3 "$searxng_script" search "$query" 2>&1 | head -50
    else
        log_error "SearXNG 脚本不存在：$searxng_script"
        return 1
    fi
}

# 智能搜索（优先 Tavily，降级 SearXNG）
smart_search() {
    local query="$1"
    local max_results="${2:-10}"
    local tool="$3"
    
    case "$tool" in
        tavily)
            tavily_search "$query" "$max_results"
            ;;
        searxng|searxng_local)
            searxng_search "$query" "$max_results"
            ;;
        *)
            log_warning "未配置搜索工具，使用 SearXNG"
            searxng_search "$query" "$max_results"
            ;;
    esac
}

# 搜索官网信息
search_official() {
    local company="$1"
    local tool="$2"
    
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  📌 搜索官网信息...                    ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    
    # 搜索企业官网
    smart_search "$company 官网" 5 "$tool"
    
    # 搜索官网上的年金信息
    smart_search "site:*$company* 企业年金 职业年金 福利" 5 "$tool"
    
    # 搜索单位性质
    smart_search "$company 单位性质 事业单位 国企 央企" 5 "$tool"
    
    echo ""
}

# 搜索招聘信息
search_recruitment() {
    local company="$1"
    local tool="$2"
    
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  📌 搜索招聘信息...                    ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    
    # 搜索招聘公告
    smart_search "$company 招聘 福利 待遇" 10 "$tool"
    
    # 搜索事业单位招聘公告
    smart_search "$company 事业单位 招聘 公告" 5 "$tool"
    
    # 搜索人社局官网
    smart_search "site:hrss.gov.cn $company 招聘" 5 "$tool"
    
    # 搜索招聘平台
    smart_search "site:zhipin.com $company" 5 "$tool"
    smart_search "site:51job.com $company" 5 "$tool"
    
    echo ""
}

# 搜索员工分享
search_social() {
    local company="$1"
    local tool="$2"
    
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  📌 搜索员工分享...                    ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    
    # 知乎
    smart_search "site:zhihu.com $company 待遇 福利 年金" 10 "$tool"
    
    # 脉脉
    smart_search "site:maimai.cn $company" 5 "$tool"
    
    # 看准网
    smart_search "site:kanzhun.com $company" 5 "$tool"
    
    # 小红书
    smart_search "site:xiaohongshu.com $company" 5 "$tool"
    
    echo ""
}

# 搜索财务/年报信息
search_financial() {
    local company="$1"
    local tool="$2"
    
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  📌 搜索财务/年报信息...               ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    
    # 搜索上市公司年报
    smart_search "$company 年报 年报 2024 2025 应付职工薪酬" 10 "$tool"
    
    # 搜索 ESG 报告
    smart_search "$company ESG 报告 社会责任报告" 5 "$tool"
    
    # 搜索预算/决算（事业单位）
    smart_search "$company 部门预算 部门决算" 5 "$tool"
    
    # 搜索巨潮资讯/港交所
    smart_search "site:cninfo.com.cn $company" 5 "$tool"
    smart_search "site:hkexnews.hk $company" 5 "$tool"
    
    echo ""
}

# 搜索年金开户银行信息
search_bank_info() {
    local company="$1"
    local tool="$2"
    
    echo -e "${PURPLE}╔════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║  🏦 搜索年金开户银行信息...            ║${NC}"
    echo -e "${PURPLE}╚════════════════════════════════════════╝${NC}"
    
    # 搜索企业年金受托银行
    smart_search "$company 企业年金 受托人 托管人 银行" 10 "$tool"
    
    # 搜索企业年金管理机构
    smart_search "$company 企业年金 平安养老 国寿养老 泰康养老 长江养老" 5 "$tool"
    
    # 搜索职业年金托管银行（事业单位）
    smart_search "$company 职业年金 托管银行 受托银行" 5 "$tool"
    
    # 搜索年金计划名称
    smart_search "$company 企业年金计划 职业年金计划" 5 "$tool"
    
    echo ""
}

# v3.1 新增：搜索上市公司年报信息
search_annual_report() {
    local company="$1"
    local tool="$2"
    
    echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  📊 搜索上市公司年报信息... (v3.1)    ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    
    # 搜索年报中的应付职工薪酬
    smart_search "$company 年报 应付职工薪酬 企业年金" 10 "$tool"
    
    # 搜索离职后福利
    smart_search "$company 年报 离职后福利 设定提存计划" 5 "$tool"
    
    # 搜索巨潮资讯网
    smart_search "site:cninfo.com.cn $company 年报" 5 "$tool"
    
    # 搜索上交所/深交所
    smart_search "site:sse.com.cn $company 年报" 5 "$tool"
    smart_search "site:szse.cn $company 年报" 5 "$tool"
    
    echo ""
}

# v3.1 新增：搜索基金/养老金产品信息
search_fund_product() {
    local company="$1"
    local tool="$2"
    
    echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  💼 搜索基金/养老金产品信息... (v3.1) ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    
    # 搜索企业年金养老金产品
    smart_search "$company 企业年金 养老金产品 投资管理人 托管人" 10 "$tool"
    
    # 搜索基金招募说明书
    smart_search "$company 企业年金 招募说明书 托管协议" 5 "$tool"
    
    # 搜索天天基金网
    smart_search "site:1234567.com.cn $company 企业年金" 5 "$tool"
    
    # 搜索基金公司官网
    smart_search "$company 企业年金 华夏基金 易方达基金 国寿养老" 5 "$tool"
    
    echo ""
}

# v3.1 新增：搜索官方受托机构名单
search_official_institutions() {
    local company="$1"
    local tool="$2"
    local city="${3:-深圳}"
    
    echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  🏛️  搜索官方受托机构名单... (v3.1)    ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
    
    # 搜索深圳市人社局受托机构名单
    smart_search "$city 企业年金 受托机构 名单 人社局" 10 "$tool"
    
    # 搜索全国企业年金管理机构名单
    smart_search "企业年金 法人受托机构 托管人 名单 人社部" 5 "$tool"
    
    # 搜索具体银行/保险机构
    smart_search "企业年金 托管人 工商银行 建设银行 招商银行" 5 "$tool"
    smart_search "企业年金 受托人 平安养老 国寿养老 泰康养老" 5 "$tool"
    
    echo ""
}

# 搜索商业查询平台
search_business_platform() {
    local company="$1"
    local tool="$2"
    
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  📌 搜索商业查询平台...                ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    
    # 天眼查/企查查
    smart_search "$company 天眼查 企查查 社保人数" 5 "$tool"
    
    # 国家企业信用信息公示系统
    smart_search "site:gsxt.gov.cn $company" 5 "$tool"
    
    echo ""
}

# 深度调查（所有方法）
search_deep() {
    local company="$1"
    local tool="$2"
    
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  🔍 深度调查：$company (v3.1)${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo ""
    
    search_official "$company" "$tool"
    search_recruitment "$company" "$tool"
    search_social "$company" "$tool"
    search_financial "$company" "$tool"
    search_business_platform "$company" "$tool"
    search_bank_info "$company" "$tool"
    search_annual_report "$company" "$tool"        # v3.1 新增：年报查询
    search_fund_product "$company" "$tool"         # v3.1 新增：基金/养老金产品查询
    search_official_institutions "$company" "$tool" # v3.1 新增：官方机构名单查询
    
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✅ 调查完成！(v3.1)${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
}

# 识别单位性质
identify_company_type() {
    local company="$1"
    local tool="$2"
    
    echo -e "${PURPLE}╔════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║  🏷️  识别单位性质...                   ║${NC}"
    echo -e "${PURPLE}╚════════════════════════════════════════╝${NC}"
    
    # 搜索单位性质
    smart_search "$company 单位性质 类型" 5 "$tool"
    
    # 搜索工商注册
    smart_search "$company 工商注册 企业类型 统一社会信用代码" 5 "$tool"
    
    # 搜索上市信息
    smart_search "$company 上市 股票代码 00700 600" 5 "$tool"
    
    echo ""
}

# 主流程
main() {
    local tool
    tool=$(detect_search_tool)
    
    log_info "搜索工具：$tool"
    log_info "企业名称：$COMPANY_NAME"
    log_info "搜索类型：$SEARCH_TYPE"
    log_info "输出格式：$OUTPUT_FORMAT"
    echo ""
    
    case "$SEARCH_TYPE" in
        official)
            identify_company_type "$COMPANY_NAME" "$tool"
            search_official "$COMPANY_NAME" "$tool"
            ;;
        recruitment)
            search_recruitment "$COMPANY_NAME" "$tool"
            ;;
        social)
            search_social "$COMPANY_NAME" "$tool"
            ;;
        financial)
            search_financial "$COMPANY_NAME" "$tool"
            ;;
        deep)
            identify_company_type "$COMPANY_NAME" "$tool"
            search_deep "$COMPANY_NAME" "$tool"
            ;;
        all|*)
            identify_company_type "$COMPANY_NAME" "$tool"
            search_official "$COMPANY_NAME" "$tool"
            search_recruitment "$COMPANY_NAME" "$tool"
            search_social "$COMPANY_NAME" "$tool"
            search_financial "$COMPANY_NAME" "$tool"
            search_business_platform "$COMPANY_NAME" "$tool"
            search_bank_info "$COMPANY_NAME" "$tool"
            search_annual_report "$COMPANY_NAME" "$tool"        # v3.1 新增
            search_fund_product "$COMPANY_NAME" "$tool"         # v3.1 新增
            search_official_institutions "$COMPANY_NAME" "$tool" # v3.1 新增
            
            echo -e "${GREEN}══════════════════════════════════════════${NC}"
            echo -e "${GREEN}  ✅ 调查完成！(v3.1)${NC}"
            echo -e "${GREEN}══════════════════════════════════════════${NC}"
            ;;
    esac
}

# 执行
main
