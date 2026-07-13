#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品类选品分析主工作流脚本 v4.0
一键执行完整的品类分析流程

主要改进 (v4.0):
1. ✅ 从 .mcp.json 自动读取 API Key（无需设置环境变量）
2. ✅ 修复 JSON 字符串值中未转义的控制字符（\n, \r, \t）
3. ✅ 改进类目搜索策略（支持模糊匹配和关键词变体）
4. ✅ 增强错误处理和调试信息
5. ✅ 更详细的执行状态跟踪
6. ✅ 支持继续执行（部分数据获取失败不影响整体流程）

主要改进 (v3.1):
1. 修复 Mojibake 编码问题
2. 改进 JSON 解析（支持 Python dict 格式）
3. 更详细的错误调试信息
4. 新增括号匹配算法
"""

import os
import sys
import json
import subprocess
import re
import codecs
from datetime import datetime
from collections import Counter

# ============================================================================
# API 配置 - 多源支持
# ============================================================================

def get_project_root_early():
    """早期获取项目根目录（在 PROJECT_ROOT 全局变量定义之前）"""
    path = os.path.abspath(__file__)
    while path != os.path.dirname(path):
        if os.path.basename(path) == '.claude':
            return os.path.dirname(path)
        path = os.path.dirname(path)
    return os.getcwd()

def get_api_key():
    """
    获取 Sorftime API Key
    优先级: 环境变量 > .mcp.json 配置文件
    """
    # 1. 尝试环境变量
    api_key = os.environ.get('SORFTIME_API_KEY', '')
    if api_key:
        return api_key

    # 2. 尝试从 .mcp.json 读取
    project_root = get_project_root_early()
    mcp_config_path = os.path.join(project_root, '.mcp.json')

    if os.path.exists(mcp_config_path):
        try:
            with open(mcp_config_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            config = json.loads(content)

            # 从 URL 中提取 API key: https://mcp.sorftime.com?key=XXX
            sorftime_url = config.get('mcpServers', {}).get('sorftime', {}).get('url', '')
            if 'key=' in sorftime_url:
                api_key = sorftime_url.split('key=')[-1]
                if api_key:
                    print(f"  ✓ 从 .mcp.json 读取 API Key")
                    return api_key
        except Exception as e:
            print(f"  ⚠ 读取 .mcp.json 失败: {e}")

    return ''


API_KEY = get_api_key()
API_URL = f'https://mcp.sorftime.com?key={API_KEY}'

# 项目路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_project_root():
    """获取项目根目录（.claude 的父目录）"""
    path = os.path.abspath(__file__)
    # 从脚本位置向上查找 .claude 目录
    while path != os.path.dirname(path):
        if os.path.basename(path) == '.claude':
            return os.path.dirname(path)
        path = os.path.dirname(path)
    # 如果找不到，使用当前工作目录
    return os.getcwd()

PROJECT_ROOT = get_project_root()


# ============================================================================
# 数据处理工具函数
# ============================================================================

def safe_int(value, default=0):
    """安全转换为整数"""
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        # 移除常见的非数字字符
        cleaned = re.sub(r'[^\d.-]', '', value)
        try:
            return int(float(cleaned)) if cleaned else default
        except ValueError:
            return default
    return default


def safe_float(value, default=0.0):
    """安全转换为浮点数"""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = re.sub(r'[^\d.-]', '', value)
        try:
            return float(cleaned) if cleaned else default
        except ValueError:
            return default
    return default


def fix_mojibake(text):
    """
    修复 Mojibake 编码问题 (UTF-8/Latin-1 双重编码)

    问题: UTF-8 字节被错误解释为 Latin-1
    解决: 将错误编码的字符串重新编码为 Latin-1，然后用 UTF-8 解码
    """
    if isinstance(text, str):
        try:
            return text.encode('latin-1').decode('utf-8')
        except:
            return text
    elif isinstance(text, dict):
        return {fix_mojibake(k): fix_mojibake(v) for k, v in text.items()}
    elif isinstance(text, list):
        return [fix_mojibake(item) for item in text]
    return text


def escape_control_chars_in_json_strings(json_str):
    """
    转义 JSON 字符串值中的控制字符

    问题: API 返回的 JSON 字符串值中包含原始的换行符、制表符等控制字符
    解决: 在保持 JSON 结构不变的情况下，只转义字符串值内的控制字符

    Args:
        json_str: 可能包含未转义控制字符的 JSON 字符串

    Returns:
        修复后的 JSON 字符串
    """
    result = []
    i = 0
    in_string = False
    escape_next = False

    while i < len(json_str):
        c = json_str[i]

        if escape_next:
            # 已转义，直接添加
            result.append(c)
            escape_next = False
            i += 1
            continue

        if c == '\\':
            result.append(c)
            escape_next = True
            i += 1
            continue

        if c == '"':
            in_string = not in_string
            result.append(c)
            i += 1
            continue

        # 在字符串值内部，转义控制字符
        if in_string:
            if c == '\n':
                result.append('\\n')
            elif c == '\r':
                result.append('\\r')
            elif c == '\t':
                result.append('\\t')
            elif ord(c) < 32:
                # 其他控制字符 - 替换为空格或删除
                result.append(' ')
            else:
                result.append(c)
        else:
            # 字符串外部，保持不变
            result.append(c)

        i += 1

    return ''.join(result)


def clean_json_string(s):
    """清理 JSON 字符串中的控制字符"""
    # 转义字符串值内的控制字符
    s = escape_control_chars_in_json_strings(s)

    # 移除所有剩余的控制字符（保留必要的空白）
    s = ''.join(c for c in s if c == '\n' or c == '\t' or c == '\r' or c >= ' ')

    # 替换转义序列
    s = s.replace('\\r\\n', ' ').replace('\\n', ' ').replace('\\t', ' ')
    return s


def python_dict_to_json(text):
    """将 Python dict 格式（单引号）转换为 JSON 格式（双引号）"""
    # 先替换 Python 字面量
    text = text.replace('True', 'true')
    text = text.replace('False', 'false')
    text = text.replace('None', 'null')

    # 转换单引号为双引号（注意不要处理字符串内的单引号）
    result = []
    i = 0
    in_string = False
    escape_next = False

    while i < len(text):
        c = text[i]

        if escape_next:
            result.append(c)
            escape_next = False
            i += 1
            continue

        if c == '\\':
            result.append(c)
            escape_next = True
            i += 1
            continue

        if c == '"':
            in_string = not in_string
            result.append(c)
            i += 1
            continue

        # 只在非字符串内的单引号转换为双引号
        if c == "'" and not in_string:
            result.append('"')
            i += 1
            continue

        result.append(c)
        i += 1

    return ''.join(result)


# ============================================================================
# 评分和分析函数
# ============================================================================

def calculate_hhi(products):
    """计算赫芬达尔-赫希曼指数 (HHI)"""
    if not products:
        return 0

    total_sales = sum(safe_int(p.get('月销量', 0)) for p in products)
    if total_sales == 0:
        return 0

    hhi = sum((safe_int(p.get('月销量', 0)) / total_sales) ** 2 for p in products)
    return round(hhi * 10000, 2)


def calculate_cr(products, n=3):
    """计算前 N 大品牌集中度 (CR)"""
    if not products:
        return 0

    total_sales = sum(safe_int(p.get('月销量', 0)) for p in products)
    if total_sales == 0:
        return 0

    brand_sales = {}
    for p in products:
        brand = p.get('品牌', 'Unknown')
        brand_sales[brand] = brand_sales.get(brand, 0) + safe_int(p.get('月销量', 0))

    top_brands = sorted(brand_sales.values(), reverse=True)[:n]
    cr = sum(top_brands) / total_sales * 100
    return round(cr, 2)


def analyze_brand_distribution(products):
    """分析品牌分布"""
    brand_data = {}
    for p in products:
        brand = p.get('品牌', 'Unknown')
        if brand not in brand_data:
            brand_data[brand] = {'count': 0, 'sales': 0, 'revenue': 0}
        brand_data[brand]['count'] += 1
        brand_data[brand]['sales'] += safe_int(p.get('月销量', 0))
        brand_data[brand]['revenue'] += safe_float(p.get('月销额', 0))

    sorted_brands = sorted(brand_data.items(), key=lambda x: x[1]['sales'], reverse=True)
    return sorted_brands


def analyze_seller_source(products):
    """分析卖家来源"""
    seller_stats = {'Amazon': 0, '美国': 0, '中国': 0, '其他': 0}
    for p in products:
        source = p.get('卖家来源', p.get('卖家', '其他'))
        if 'Amazon' in str(source):
            seller_stats['Amazon'] += 1
        elif '美国' in str(source):
            seller_stats['美国'] += 1
        elif '中国' in str(source) or 'CN' in str(source) or '中国香港' in str(source):
            seller_stats['中国'] += 1
        else:
            seller_stats['其他'] += 1

    total = len(products)
    return {k: round(v / total * 100, 1) if total > 0 else 0 for k, v in seller_stats.items()}


def calculate_five_dimension_score(data):
    """
    计算五维评分 (标准版本 - 与需求文档一致)

    评分标准:
    - 市场规模 (20分): >$10M=20, >$5M=17, >$1M=14, 其他=10
    - 增长潜力 (25分): 低评论产品占比>40%=22, >20%=18, 其他=14
    - 竞争烈度 (20分): Top3品牌占比<30%=18, <50%=14, 其他=8
    - 进入壁垒 (20分): Amazon占比<20%且新品>40%=20, 其他组合6-18分
    - 利润空间 (15分): 均价>$300=12, >$150=10, >$50=7, 其他=4
    """
    products = data.get('Top100产品', [])
    # 支持两种键名
    stats = data.get('类目统计报告', data.get('统计数据', {}))

    scores = {}

    # 1. 市场规模 (20分) - 基于类目月销额
    monthly_revenue = safe_float(stats.get('top100产品月销额', stats.get('类目月销额', 0)))
    if monthly_revenue > 10000000:
        scores['市场规模'] = 20
    elif monthly_revenue > 5000000:
        scores['市场规模'] = 17
    elif monthly_revenue > 1000000:
        scores['市场规模'] = 14
    else:
        scores['市场规模'] = 10

    # 2. 增长潜力 (25分) - 基于低评论产品占比 (评论数<100)
    low_review_products = sum(1 for p in products if safe_int(p.get('评论数', 0)) < 100)
    low_review_ratio = low_review_products / len(products) * 100 if products else 0

    if low_review_ratio > 40:
        scores['增长潜力'] = 22
    elif low_review_ratio > 20:
        scores['增长潜力'] = 18
    else:
        scores['增长潜力'] = 14

    # 3. 竞争烈度 (20分) - 基于 Top3 品牌占比 (CR3)
    cr3 = calculate_cr(products, 3)
    if cr3 < 30:
        scores['竞争烈度'] = 18
    elif cr3 < 50:
        scores['竞争烈度'] = 14
    else:
        scores['竞争烈度'] = 8

    # 4. 进入壁垒 (20分) - Amazon 占比 + 新品机会
    amazon_count = sum(1 for p in products if p.get('卖家') == 'Amazon' or 'Amazon' in str(p.get('卖家', '')))
    amazon_ratio = amazon_count / len(products) * 100 if products else 0

    # Amazon 占比评分 (0-10分): 占比越低，壁垒越小
    if amazon_ratio < 20:
        amazon_score = 10
    elif amazon_ratio < 40:
        amazon_score = 6
    else:
        amazon_score = 3

    # 新品机会评分 (0-10分): 新品越多，壁垒越小
    if low_review_ratio > 40:
        new_product_score = 10
    elif low_review_ratio > 20:
        new_product_score = 6
    else:
        new_product_score = 3

    scores['进入壁垒'] = amazon_score + new_product_score

    # 5. 利润空间 (15分) - 基于平均价格
    avg_price = sum(safe_float(p.get('价格', 0)) for p in products) / len(products) if products else 0
    if avg_price > 300:
        scores['利润空间'] = 12
    elif avg_price > 150:
        scores['利润空间'] = 10
    elif avg_price > 50:
        scores['利润空间'] = 7
    else:
        scores['利润空间'] = 4

    total_score = sum(scores.values())
    return scores, total_score


def get_rating(total_score):
    """获取评级"""
    if total_score >= 80:
        return "优秀", "强烈推荐进入"
    elif total_score >= 70:
        return "良好", "可以考虑进入"
    elif total_score >= 50:
        return "一般", "谨慎进入"
    else:
        return "较差", "不建议进入"


def generate_markdown_report(data, scores, total_score, category_name, site):
    """生成 Markdown 报告"""
    products = data.get('Top100产品', [])
    stats = data.get('类目统计报告', data.get('统计数据', {}))

    hhi = calculate_hhi(products)
    cr3 = calculate_cr(products, 3)
    brand_distribution = analyze_brand_distribution(products)
    seller_source = analyze_seller_source(products)

    rating, recommendation = get_rating(total_score)
    top10 = products[:10]

    avg_price = sum(safe_float(p.get('价格', 0)) for p in products) / len(products) if products else 0
    monthly_revenue = safe_float(stats.get('top100产品月销额', stats.get('类目月销额', 0)))
    monthly_sales = sum(safe_int(p.get('月销量', 0)) for p in products)
    avg_reviews = sum(safe_int(p.get('评论数', 0)) for p in products) / len(products) if products else 0
    avg_rating = sum(safe_float(p.get('星级', 0)) for p in products) / len(products) if products else 0

    # Amazon 占比
    amazon_count = sum(1 for p in products if p.get('卖家') == 'Amazon' or 'Amazon' in str(p.get('卖家', '')))
    amazon_ratio = amazon_count / len(products) * 100 if products else 0

    # 低评论产品占比
    low_review_products = sum(1 for p in products if safe_int(p.get('评论数', 0)) < 100)
    low_review_ratio = low_review_products / len(products) * 100 if products else 0

    report = f"""# {category_name} ({site}) 品类选品分析报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 数据来源: Sorftime Amazon 数据服务

---

## 一、执行摘要

| 评估维度 | 得分 | 满分 |
|---------|------|------|
| **市场规模** | {scores.get('市场规模', 0)}/20 | 20 |
| **增长潜力** | {scores.get('增长潜力', 0)}/25 | 25 |
| **竞争烈度** | {scores.get('竞争烈度', 0)}/20 | 20 |
| **进入壁垒** | {scores.get('进入壁垒', 0)}/20 | 20 |
| **利润空间** | {scores.get('利润空间', 0)}/15 | 15 |
| **总分** | **{total_score}/100** | 100 |

**评级**: {rating}
**选品建议**: {recommendation}

---

## 二、市场概况

### 2.1 类目基本信息
- **类目名称**: {category_name}
- **Amazon 站点**: {site}

### 2.2 关键指标

| 指标 | 数值 |
|------|------|
| 类目月销量 | {monthly_sales:,} |
| 类目月销额 | ${monthly_revenue:,.2f} |
| 分析产品数量 | {len(products)} |
| 平均价格 | ${avg_price:.2f} |
| 平均评论数 | {avg_reviews:.0f} |
| 平均星级 | {avg_rating:.2f} |

### 2.3 市场集中度
- **HHI 指数**: {hhi} ({'低集中度' if hhi < 1500 else '中等集中度' if hhi < 2500 else '高集中度'})
- **CR3 (前三品牌集中度)**: {cr3}%
- **Amazon 自营占比**: {amazon_ratio:.1f}%
- **低评论产品占比** (评论数<100): {low_review_ratio:.1f}%

---

## 三、品牌分析

### 3.1 Top 品牌 (按销量)

| 排名 | 品牌 | 产品数 | 月销量 | 月销额 |
|------|------|--------|--------|--------|
"""

    for i, (brand, info) in enumerate(brand_distribution[:10], 1):
        report += f"| {i} | {brand} | {info['count']} | {info['sales']:,} | ${info['revenue']:,.2f} |\n"

    report += f"""

### 3.2 卖家来源分布

| 来源 | 占比 |
|------|------|
| Amazon 自营 | {seller_source['Amazon']}% |
| 美国卖家 | {seller_source['美国']}% |
| 中国卖家 | {seller_source['中国']}% |
| 其他/未知 | {seller_source['其他']}% |

---

## 四、Top 10 热销产品

| 排名 | ASIN | 产品标题 | 价格 | 月销量 | 月销额 | 评论数 | 星级 | 品牌 |
|------|------|----------|------|--------|--------|--------|------|------|
"""

    for i, p in enumerate(top10, 1):
        title = p.get('标题', 'N/A')[:60] + '...' if len(p.get('标题', '')) > 60 else p.get('标题', 'N/A')
        price = safe_float(p.get('价格', 0))
        sales = safe_int(p.get('月销量', 0))
        revenue = safe_float(p.get('月销额', 0))
        reviews = safe_int(p.get('评论数', 0))
        rating = safe_float(p.get('星级', 0))
        asin = p.get('ASIN', 'N/A')
        report += f"| {i} | [{asin}](https://www.amazon.com/dp/{asin}) | {title} | ${price:.2f} | {sales:,} | ${revenue:,.2f} | {reviews:,} | {rating:.1f} | {p.get('品牌', 'N/A')} |\n"

    report += f"""

---

## 五、选品建议

### 5.1 市场机会
- 该品类市场规模{'较大' if scores.get('市场规模', 0) >= 17 else '中等' if scores.get('市场规模', 0) >= 14 else '较小'}
- 竞争{'相对温和' if cr3 < 40 else '较为激烈'}
- {'存在' if seller_source['中国'] > 20 else '较少'}中国卖家机会
- 低评论产品占比 {low_review_ratio:.1f}%，{'新品机会较大' if low_review_ratio > 30 else '新品有一定机会' if low_review_ratio > 15 else '新品机会较少'}

### 5.2 进入策略
- 建议定价范围: ${avg_price * 0.7:.2f} - ${avg_price * 1.3:.2f}
- 关注差异化产品和细分市场
- 重视产品质量以获取好评
- {'Amazon 占比较高，需注意价格竞争' if amazon_ratio > 30 else 'Amazon 占比较低，第三方卖家机会较大'}

### 5.3 风险提示
- {'Amazon 自营占比较高，需注意价格竞争' if amazon_ratio > 30 else 'Amazon 自营占比较低'}
- 头部品牌已建立一定优势（CR3 = {cr3}%）
- 新产品需要投入营销获取初期销量
- 平均评论数 {avg_reviews:.0f}，{'评论门槛较高' if avg_reviews > 500 else '评论门槛适中' if avg_reviews > 100 else '评论门槛较低'}

---

*本报告由 Claude Code 自动生成 | 数据来源: Sorftime*
"""

    return report


# ============================================================================
# 主工作流类
# ============================================================================

class CategoryAnalysisWorkflow:
    """品类选品分析工作流 v4.0"""

    def __init__(self, category: str, site: str = 'US', limit: int = 20, node_id: str = None):
        self.category = category
        self.site = site.upper()
        self.limit = limit
        self.node_id = node_id
        self.output_dir = ''
        self.request_id = 0
        self.data = None  # 存储解析后的完整数据
        self.execution_log = []  # 执行日志

    def log(self, message: str, level: str = 'INFO'):
        """记录日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.execution_log.append(log_entry)
        print(f"  {message}")

    def check_api_key(self):
        """检查 API Key 是否可用"""
        if not API_KEY:
            self.log("❌ API Key 未设置", "ERROR")
            self.log("请设置 SORFTIME_API_KEY 环境变量，或在 .mcp.json 中配置", "ERROR")
            return False
        self.log(f"✓ API Key 已配置 (长度: {len(API_KEY)})")
        return True

    def _curl_request(self, tool_name: str, arguments: dict) -> dict:
        """执行 curl 请求，返回解析后的结果"""
        self.request_id += 1
        args_str = json.dumps(arguments, ensure_ascii=False)

        cmd = [
            'curl', '-s', '-X', 'POST', API_URL,
            '-H', 'Content-Type: application/json',
            '-d', f'{{"jsonrpc":"2.0","id":{self.request_id},"method":"tools/call","params":{{"name":"{tool_name}","arguments":{args_str}}}}}'
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, encoding='utf-8', errors='ignore')
            return self._parse_sse_response(result.stdout)
        except subprocess.TimeoutExpired:
            self.log(f"⏱ 请求超时 (tool: {tool_name})", "WARN")
            return {'text': '', 'error': 'Timeout', 'has_error': True}
        except Exception as e:
            self.log(f"✗ 请求失败: {e}", "ERROR")
            return {'text': '', 'error': str(e), 'has_error': True}

    def _parse_sse_response(self, response: str) -> dict:
        """解析 SSE 响应，返回文本内容"""
        result = {'text': '', 'error': None, 'has_error': False}

        for line in response.split('\n'):
            if line.startswith('data: '):
                json_text = line[6:]
                try:
                    data = json.loads(json_text)
                    result_text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                    if result_text:
                        # 解码 Unicode 转义
                        decoded = codecs.decode(result_text, 'unicode-escape')
                        # 修复 Mojibake
                        decoded = fix_mojibake(decoded)
                        result['text'] = decoded
                        return result
                except json.JSONDecodeError as e:
                    result['error'] = str(e)
                    result['has_error'] = True

        # 检查错误响应
        if 'error' in response.lower() or 'isError' in response or 'Authentication required' in response:
            result['has_error'] = True
            if 'Authentication required' in response:
                result['error'] = 'Authentication failed - Invalid API Key'

        return result

    def _parse_business_data(self, text_content: str) -> dict:
        """
        从 API 返回的文本内容中解析业务数据

        处理多种可能的格式:
        1. 纯 JSON 格式
        2. 带前缀的 JSON
        3. Python dict 格式（单引号）
        4. 需要清理控制字符的 JSON
        """
        # 1. 转义字符串值内的控制字符（关键修复）
        text_content = escape_control_chars_in_json_strings(text_content)

        # 2. 清理剩余控制字符
        text_content = clean_json_string(text_content)

        # 3. 找到 JSON 开始位置
        json_start = text_content.find('{')
        if json_start == -1:
            self.log("未找到 JSON 数据", "ERROR")
            return None

        # 4. 使用括号匹配提取完整的 JSON/Python dict
        json_str = self._extract_braced_content(text_content, json_start)
        if not json_str:
            self.log("无法提取完整的 JSON 数据", "ERROR")
            return None

        # 5. 转换 Python dict 格式为 JSON 格式
        json_str = python_dict_to_json(json_str)

        # 6. 尝试解析
        try:
            data = json.loads(json_str)
            # 修复所有字符串的编码
            data = fix_mojibake(data)
            return data
        except json.JSONDecodeError as e:
            self.log(f"⚠ JSON 解析失败: {e}", "ERROR")
            # 保存解析失败的文本用于调试
            debug_file = os.path.join(self.output_dir, 'parse_debug.txt')
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"Error: {e}\n")
                f.write(f"JSON start: {json_start}\n")
                f.write(f"JSON length: {len(json_str)}\n")
                f.write(f"First 500 chars:\n{json_str[:500]}\n")
            self.log(f"调试信息已保存: {debug_file}", "DEBUG")
            return None

    def _extract_braced_content(self, text: str, start: int) -> str:
        """使用括号匹配提取花括号内容"""
        if start >= len(text) or text[start] != '{':
            return None

        depth = 0
        in_string = False
        escape_next = False

        for i in range(start, len(text)):
            c = text[i]

            if escape_next:
                escape_next = False
                continue

            if c == '\\':
                escape_next = True
                continue

            if c == '"':
                in_string = not in_string
                continue

            if not in_string:
                if c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        return text[start:i+1]

        return None

    def step1_search_category(self):
        """步骤1: 搜索类目获取 nodeId"""
        print(f"\n{'='*70}")
        print(f"步骤1: 搜索类目 '{self.category}'")
        print('='*70)

        # 如果已提供 NodeID，跳过搜索
        if self.node_id:
            self.log(f"使用提供的 NodeId: {self.node_id}")
            return True

        result = self._curl_request('category_name_search', {
            'amzSite': self.site,
            'searchName': self.category
        })

        text = result.get('text', '')

        if 'Authentication required' in text or 'Authentication failed' in str(result.get('error', '')):
            self.log("认证失败，请检查 API Key", "ERROR")
            return False

        # 尝试多种搜索策略
        search_variants = [
            self.category,
            self.category.replace(' & ', ' '),
            self.category.split(' ')[0],  # 第一个词
            self.category.rstrip('s'),  # 移除复数
        ]

        for variant in search_variants:
            if variant == self.category:
                continue  # 已经尝试过

            if '未查询到对应类目' in text or not text:
                self.log(f"尝试搜索变体: '{variant}'")
                result = self._curl_request('category_name_search', {
                    'amzSite': self.site,
                    'searchName': variant
                })
                text = result.get('text', '')
                if text and '未查询到对应类目' not in text:
                    self.category = variant
                    self.log(f"找到匹配类目: {variant}")
                    break

        if '未查询到对应类目' in text or not text:
            self.log(f"未找到类目: {self.category}", "ERROR")
            return False

        # 提取 NodeID
        match = re.search(r'"NodeId":"?(\d+)"?', text)
        if match:
            self.node_id = match.group(1)
            self.log(f"找到类目 NodeId: {self.node_id}")
            return True

        # 检查是否返回了多个类目
        if '"Name"' in text and '"NodeId"' in text:
            self.log("API 返回了多个类目，请选择更具体的类目名称", "WARN")
            # 尝试提取第一个类目
            matches = re.findall(r'"Name":"([^"]+)","NodeId":"(\d+)"', text)
            if matches:
                self.log("找到以下类目选项:", "INFO")
                for i, (name, nid) in enumerate(matches[:5], 1):
                    self.log(f"  {i}. {name} (NodeID: {nid})")
                # 使用第一个
                self.node_id = matches[0][1]
                self.category = matches[0][0]
                self.log(f"使用第一个类目: {self.category}")
                return True

        self.log("未找到匹配的类目", "ERROR")
        return False

    def step2_get_category_report(self):
        """步骤2: 获取并解析类目报告"""
        print(f"\n{'='*70}")
        print("步骤2: 获取类目报告 (Top100 + 统计数据)")
        print('='*70)

        response = self._curl_request('category_report', {
            'amzSite': self.site,
            'nodeId': self.node_id
        })

        text = response.get('text', '')

        if 'Authentication required' in text:
            self.log("认证失败，请检查 API Key", "ERROR")
            return False

        if '没有相关数据' in text or not text:
            self.log(f"该类目暂无数据: {self.node_id}", "ERROR")
            return False

        # 保存原始响应（用于调试）
        temp_file = os.path.join(self.output_dir, 'category_report_raw.txt')
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write("event: message\n")
            f.write(f"data: {{\"result\":{{\"content\":[{{\"type\":\"text\",\"text\":\"{text}\"}}]}}}}\n")
        self.log(f"原始响应已保存: {temp_file}")

        # 解析业务数据
        self.log("正在解析业务数据...")
        self.data = self._parse_business_data(text)

        if not self.data:
            self.log("数据解析失败", "ERROR")
            return False

        products = self.data.get('Top100产品', [])
        stats = self.data.get('类目统计报告', self.data.get('统计数据', {}))

        self.log(f"✓ 解析成功")
        self.log(f"  - Top100产品数量: {len(products)}")
        monthly_revenue = safe_float(stats.get('top100产品月销额', stats.get('类目月销额', 0)))
        self.log(f"  - 类目月销额: ${monthly_revenue:,.2f}")

        return True

    def step3_generate_report(self):
        """步骤3: 生成分析报告"""
        print(f"\n{'='*70}")
        print("步骤3: 生成分析报告")
        print('='*70)

        if not self.data:
            self.log("没有可用的数据", "ERROR")
            return False

        # 计算五维评分
        scores, total_score = calculate_five_dimension_score(self.data)
        print(f"\n五维评分: {total_score}/100")
        for k, v in scores.items():
            print(f"  - {k}: {v}")

        # 生成 Markdown 报告
        report = generate_markdown_report(self.data, scores, total_score, self.category, self.site)
        report_file = os.path.join(self.output_dir, "report.md")

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        self.log(f"✓ 报告已生成: {report_file}")

        # 保存数据
        data_file = os.path.join(self.output_dir, "data.json")
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        self.log(f"✓ 数据已保存: {data_file}")

        # 保存评分
        scores_file = os.path.join(self.output_dir, "scores.json")
        with open(scores_file, 'w', encoding='utf-8') as f:
            json.dump({"scores": scores, "total_score": total_score}, f, ensure_ascii=False, indent=2)
        self.log(f"✓ 评分已保存: {scores_file}")

        # 保存 TopN 产品
        products = self.data.get('Top100产品', [])
        top_n = products[:self.limit]
        top_n_file = os.path.join(self.output_dir, "top_products.json")
        with open(top_n_file, 'w', encoding='utf-8') as f:
            json.dump(top_n, f, ensure_ascii=False, indent=2)
        self.log(f"✓ Top{self.limit} 产品已保存: {top_n_file}")

        return True

    def run(self):
        """执行完整工作流"""
        print("\n" + "="*70)
        print(f"品类选品分析: {self.category} ({self.site})")
        print("="*70)

        # 检查 API Key
        if not self.check_api_key():
            return False

        # 创建输出目录
        date_str = datetime.now().strftime('%Y%m%d')
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', self.category).replace(' ', '_')
        safe_name = safe_name[:50]
        self.output_dir = os.path.join(PROJECT_ROOT, 'category-reports', f'{safe_name}_{self.site}_{date_str}')
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"\n输出目录: {self.output_dir}")

        # 执行工作流
        success = True
        if not self.step1_search_category():
            self.log("类目搜索失败", "ERROR")
            success = False

        if success and not self.step2_get_category_report():
            self.log("获取类目报告失败", "ERROR")
            success = False

        if success and not self.step3_generate_report():
            self.log("报告生成失败", "ERROR")
            success = False

        # 保存执行日志
        log_file = os.path.join(self.output_dir, "execution.log")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.execution_log))

        # 打印总结
        print("\n" + "="*70)
        if success:
            print("✓ 分析完成!")
            print(f"报告位置: {self.output_dir}/report.md")
        else:
            print("✗ 分析失败，请查看错误信息")
        print("="*70)

        return success


# ============================================================================
# 命令行入口
# ============================================================================

def main():
    if len(sys.argv) < 3:
        print("用法: python workflow.py <品类名称|NodeID> <站点> [分析数量]")
        print("示例: python workflow.py \"Sofas\" US 20")
        print("示例: python workflow.py 679394011 US 20")
        sys.exit(1)

    # 解析参数
    category_or_nodeid = sys.argv[1]
    site = sys.argv[2] if len(sys.argv) > 2 else 'US'
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20

    # 判断是品类名称还是 NodeID
    node_id = None
    category = category_or_nodeid

    if category_or_nodeid.isdigit():
        node_id = category_or_nodeid
        category = f"NodeID_{category_or_nodeid}"

    # 运行工作流
    workflow = CategoryAnalysisWorkflow(category, site, limit, node_id)
    success = workflow.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
