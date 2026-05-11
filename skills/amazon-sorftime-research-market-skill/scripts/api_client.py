#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sorftime API 客户端 - 统一的数据采集接口

v2.2 - 修复大文件 JSON 解析问题

为 product-research Skill 提供简洁的 API 调用方法:
- 自动从 .mcp.json 读取 API Key
- SSE 响应解析
- Mojibake 编码修复
- 控制字符转义（在 Unicode 解码后执行）
- 返回干净的 Python dict

使用示例:
    from scripts.api_client import SorftimeClient

    client = SorftimeClient()

    # 获取类目 Top100
    top100 = client.get_category_report(site="US", node_id=12345)

    # 获取关键词详情
    keyword = client.get_keyword_detail(site="US", keyword="your keyword")

    # 获取产品详情
    product = client.get_product_detail(site="US", asin="B0XXXXXXXX")

    # 获取产品评论
    reviews = client.get_product_reviews(site="US", asin="B0XXXXXXXX", review_type="Negative")
"""

import os
import json
import re
import codecs
import subprocess
import sys
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path


# ============================================================================
# API 配置
# ============================================================================

def get_project_root():
    """获取项目根目录（.claude 的父目录）"""
    path = os.path.abspath(__file__)
    while path != os.path.dirname(path):
        if os.path.basename(path) == '.claude':
            return os.path.dirname(path)
        path = os.path.dirname(path)
    return os.getcwd()


def get_api_key():
    """
    从 .mcp.json 读取 Sorftime API Key

    Returns:
        str: API Key
    """
    project_root = get_project_root()
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
                    return api_key
        except Exception as e:
            print(f"⚠ 读取 .mcp.json 失败: {e}")

    # 尝试环境变量
    api_key = os.environ.get('SORFTIME_API_KEY', '')
    if api_key:
        return api_key

    raise ValueError(
        "API Key 未找到。请确保:\n"
        "1. .mcp.json 文件存在并包含 sorftime 配置，或\n"
        "2. 设置环境变量 SORFTIME_API_KEY"
    )


# ============================================================================
# 数据处理工具函数
# ============================================================================

def safe_int(value, default=0):
    """安全转换为整数"""
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
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
    """
    result = []
    i = 0
    in_string = False
    escape_next = False

    while i < len(json_str):
        c = json_str[i]

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

        if in_string:
            if c == '\n':
                result.append('\\n')
            elif c == '\r':
                result.append('\\r')
            elif c == '\t':
                result.append('\\t')
            elif ord(c) < 32:
                result.append(' ')
            else:
                result.append(c)
        else:
            result.append(c)
        i += 1

    return ''.join(result)


def extract_json_object(text):
    """
    从文本中提取完整的 JSON 对象

    使用括号匹配算法，支持嵌套结构
    """
    stack = []
    start_idx = None

    for i, char in enumerate(text):
        if char in '{[':
            if not stack:
                start_idx = i
            stack.append(char)
        elif char in '}]':
            if stack:
                expected = '}' if char == '}' else ']'
                opening = '{' if expected == '}' else '['
                if stack[-1] == opening:
                    stack.pop()
                    if not stack:
                        json_str = text[start_idx:i+1]
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            continue

    return None


def decode_sse_response(content):
    """
    解码 Sorftime SSE 响应

    处理流程:
    1. 清理控制字符
    2. 解析 SSE 格式 (event: message, data: {...})
    3. Unicode 解码
    4. Mojibake 修复
    5. 提取 JSON 对象

    Args:
        content: SSE 响应内容（字符串）

    Returns:
        dict: 解码后的数据
    """
    # 清理控制字符
    content = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', content)

    for line in content.split('\n'):
        if line.startswith('data: '):
            json_text = line[6:]  # 去掉 'data: ' 前缀
            try:
                data = json.loads(json_text)
                result_text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                if result_text:
                    # Unicode 解码
                    decoded = codecs.decode(result_text, 'unicode-escape')

                    # Mojibake 修复
                    decoded = fix_mojibake(decoded)

                    # 转义 JSON 字符串值内的控制字符（关键步骤！）
                    decoded = escape_control_chars_in_json_strings(decoded)

                    # 清理剩余的控制字符
                    decoded = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', decoded)

                    # 提取 JSON
                    json_obj = extract_json_object(decoded)
                    if json_obj:
                        return json_obj
            except Exception:
                continue

    # 如果 SSE 解析失败，尝试直接解析
    try:
        return json.loads(content)
    except:
        pass

    return None


# ============================================================================
# Sorftime API 客户端
# ============================================================================

class SorftimeClient:
    """
    Sorftime API 客户端

    提供简洁的方法调用 Sorftime MCP API
    """

    # API 工具名称映射
    TOOLS = {
        # 类目相关
        'search_categories_broadly': 'search_categories_broadly',  # 多维度广泛搜索类目
        'category_name_search': 'category_name_search',  # 按类目名称搜索（使用 searchName 参数）
        'category_report': 'category_report',
        'category_trend': 'category_trend',
        'category_keywords': 'category_keywords',

        # 关键词相关
        'keyword_detail': 'keyword_detail',
        'keyword_search_results': 'keyword_search_results',
        'keyword_extends': 'keyword_extends',
        'keyword_trend': 'keyword_trend',

        # 产品相关
        'product_detail': 'product_detail',
        'product_reviews': 'product_reviews',
        'product_traffic_terms': 'product_traffic_terms',
        'product_trend': 'product_trend',
        'product_search': 'product_search',

        # 选品相关
        'potential_product': 'potential_product',
        'competitor_product_keywords': 'competitor_product_keywords',

        # 供应链
        'ali1688': 'ali1688_similar_product',
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端

        Args:
            api_key: Sorftime API Key，如果不提供则从 .mcp.json 读取
        """
        self.api_key = api_key or get_api_key()
        self.api_url = f'https://mcp.sorftime.com?key={self.api_key}'
        self.request_id = 0

    def _call(self, tool_name: str, arguments: Dict[str, Any]) -> tuple:
        """
        调用 Sorftime API

        Args:
            tool_name: API 工具名称
            arguments: API 参数

        Returns:
            tuple: (解析后的数据 dict, 原始响应 str)
        """
        self.request_id += 1

        payload = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        try:
            result = subprocess.run(
                ['curl', '-s', '-X', 'POST', self.api_url,
                 '-H', 'Content-Type: application/json',
                 '-H', 'Accept: application/json, text/event-stream',
                 '-d', json.dumps(payload)],
                capture_output=True,
                text=True,
                timeout=60,
                check=True
            )

            # 返回原始响应和解析后的数据
            raw_response = result.stdout
            data = decode_sse_response(raw_response)

            if data is None:
                # 即使解析失败，也返回原始响应供调试
                return None, raw_response

            return data, raw_response

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"API 调用失败: {e}")
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"API 调用超时")

    # ========================================================================
    # 类目相关 API
    # ========================================================================

    def search_category_by_product_name(
        self,
        site: str,
        product_name: str
    ) -> Dict[str, Any]:
        """
        按产品名称搜索类目

        Args:
            site: 站点 (US, GB, DE, FR, IT, ES, CA, JP, etc.)
            product_name: 产品名称

        Returns:
            dict: 搜索结果，包含类目列表
        """
        return self._call(
            self.TOOLS['category_name_search'],
            {"amzSite": site, "searchName": product_name}  # 注意: 参数是 searchName
        )

    def search_category_by_name(
        self,
        site: str,
        category_name: str
    ) -> Dict[str, Any]:
        """
        按类目名称搜索（别名方法，与 search_category_by_product_name 相同）

        Args:
            site: 站点
            category_name: 类目名称

        Returns:
            dict: 搜索结果
        """
        return self.search_category_by_product_name(site, category_name)

    def search_categories_broadly(
        self,
        site: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        多维度广泛搜索类目（新增 - 用于蓝海发现）

        Args:
            site: 站点 (US, GB, DE, FR, IT, ES, CA, JP, etc.)
            filters: 筛选条件（可选）
                - top3Product_sales_share: Top3 产品销量占比上限（如 0.4 表示<40%）
                - top3Brands_sales_share: Top3 品牌销量占比上限
                - newProductSalesAmountShare: 新品销量占比下限（如 0.15 表示>15%）
                - brandCount: 品牌数量下限（如 80 表示>80 个品牌）
                - priceRange_min: 价格范围下限
                - priceRange_max: 价格范围上限
                - monthlySales_min: 月销量下限
                - monthlySales_max: 月销量上限

        Returns:
            dict: 类目列表，包含：
                - categories: 类目列表
                - total: 总数
        """
        params = {"amzSite": site}
        if filters:
            params.update(filters)
        return self._call(
            self.TOOLS['search_categories_broadly'],
            params
        )

    def get_category_report(
        self,
        site: str,
        node_id: int
    ) -> Dict[str, Any]:
        """
        获取类目 Top100 报告

        Args:
            site: 站点
            node_id: 类目 Node ID

        Returns:
            dict: Top100 产品数据
        """
        return self._call(
            self.TOOLS['category_report'],
            {"amzSite": site, "nodeId": str(node_id)}
        )

    def get_category_trend(
        self,
        site: str,
        node_id: int,
        trend_index: str = "NewProductSalesAmountShare"
    ) -> Dict[str, Any]:
        """
        获取类目趋势数据

        Args:
            site: 站点
            node_id: 类目 Node ID
            trend_index: 趋势类型
                - NewProductSalesAmountShare: 新品销量占比
                - NewProductProductShare: 新品数量占比
                - etc.

        Returns:
            dict: 结构化趋势数据
                {
                    "trend_data": [
                        {"date": "2024-03", "value": 33.35},
                        ...
                    ],
                    "metric": "新品占比",
                    "node_id": "99530371011"
                }
        """
        raw_data, raw_response = self._call(
            self.TOOLS['category_trend'],
            {"amzSite": site, "nodeId": str(node_id), "trendIndex": trend_index}
        )

        # 转换原始格式为结构化格式
        # 原始格式: ["2024年03月=33.35", "2024年04月=27.94", ...]
        # 目标格式: {"trend_data": [{"date": "2024-03", "value": 33.35}, ...]}
        if isinstance(raw_data, list):
            trend_data = []
            for item in raw_data:
                if isinstance(item, str) and '=' in item:
                    # 解析 "2024年03月=33.35" 格式
                    date_str, value_str = item.split('=', 1)
                    # 转换日期格式: "2024年03月" -> "2024-03"
                    date_match = re.search(r'(\d{4})年(\d{2})月', date_str)
                    if date_match:
                        year, month = date_match.groups()
                        formatted_date = f"{year}-{month}"
                        try:
                            value = float(value_str)
                            trend_data.append({
                                "date": formatted_date,
                                "value": value
                            })
                        except ValueError:
                            continue

            # 指标名称映射
            metric_names = {
                "NewProductSalesAmountShare": "新品销量占比",
                "NewProductProductShare": "新品数量占比",
            }

            return {
                "trend_data": trend_data,
                "metric": metric_names.get(trend_index, trend_index),
                "node_id": str(node_id),
                "site": site
            }

        return raw_data

    def get_category_keywords(
        self,
        site: str,
        node_id: int,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        获取类目关键词

        Args:
            site: 站点
            node_id: 类目 Node ID
            page: 页码

        Returns:
            dict: 关键词数据
        """
        return self._call(
            self.TOOLS['category_keywords'],
            {"amzSite": site, "nodeId": str(node_id), "page": page}
        )

    # ========================================================================
    # 关键词相关 API
    # ========================================================================

    def get_keyword_detail(
        self,
        site: str,
        keyword: str
    ) -> Dict[str, Any]:
        """
        获取关键词详情

        Args:
            site: 站点
            keyword: 关键词

        Returns:
            dict: 关键词详情（搜索量、CPC、自然位产品等）
        """
        return self._call(
            self.TOOLS['keyword_detail'],
            {"amzSite": site, "keyword": keyword}
        )

    def get_keyword_search_results(
        self,
        site: str,
        keyword: str
    ) -> Dict[str, Any]:
        """
        获取关键词搜索结果（自然位产品）

        Args:
            site: 站点
            keyword: 关键词

        Returns:
            dict: 自然位产品列表
        """
        return self._call(
            self.TOOLS['keyword_search_results'],
            {"amzSite": site, "searchKeyword": keyword}
        )

    def get_keyword_extends(
        self,
        site: str,
        keyword: str
    ) -> Dict[str, Any]:
        """
        获取关键词延伸词

        Args:
            site: 站点
            keyword: 关键词

        Returns:
            dict: 延伸词列表
        """
        return self._call(
            self.TOOLS['keyword_extends'],
            {"amzSite": site, "keyword": keyword}
        )

    # ========================================================================
    # 产品相关 API
    # ========================================================================

    def get_product_detail(
        self,
        site: str,
        asin: str
    ) -> Dict[str, Any]:
        """
        获取产品详情

        Args:
            site: 站点
            asin: 产品 ASIN

        Returns:
            dict: 产品详情
        """
        return self._call(
            self.TOOLS['product_detail'],
            {"amzSite": site, "asin": asin}
        )

    def get_product_reviews(
        self,
        site: str,
        asin: str,
        review_type: str = "Both"
    ) -> Dict[str, Any]:
        """
        获取产品评论

        Args:
            site: 站点
            asin: 产品 ASIN
            review_type: 评论类型 (Both, Positive, Negative)

        Returns:
            dict: 评论列表
        """
        return self._call(
            self.TOOLS['product_reviews'],
            {"amzSite": site, "asin": asin, "reviewType": review_type}
        )

    def get_product_traffic_terms(
        self,
        site: str,
        asin: str
    ) -> Dict[str, Any]:
        """
        获取产品流量关键词（反查）

        Args:
            site: 站点
            asin: 产品 ASIN

        Returns:
            dict: 流量关键词列表
        """
        return self._call(
            self.TOOLS['product_traffic_terms'],
            {"amzSite": site, "asin": asin}
        )

    def get_product_trend(
        self,
        site: str,
        asin: str
    ) -> Dict[str, Any]:
        """
        获取产品趋势

        Args:
            site: 站点
            asin: 产品 ASIN

        Returns:
            dict: 趋势数据
        """
        return self._call(
            self.TOOLS['product_trend'],
            {"amzSite": site, "asin": asin}
        )

    def search_products(
        self,
        site: str,
        search_name: str,
        **filters
    ) -> Dict[str, Any]:
        """
        搜索产品

        Args:
            site: 站点
            search_name: 搜索关键词
            **filters: 筛选条件

        Returns:
            dict: 搜索结果
        """
        params = {"amzSite": site, "searchName": search_name}
        params.update(filters)
        return self._call(self.TOOLS['product_search'], params)

    # ========================================================================
    # 选品相关 API
    # ========================================================================

    def get_potential_products(
        self,
        site: str,
        search_name: str,
        **filters
    ) -> Dict[str, Any]:
        """
        获取潜力产品

        Args:
            site: 站点
            search_name: 搜索关键词
            **filters: 筛选条件

        Returns:
            dict: 潜力产品列表
        """
        params = {"amzSite": site, "searchName": search_name}
        params.update(filters)
        return self._call(self.TOOLS['potential_product'], params)

    def get_competitor_keywords(
        self,
        site: str,
        asin: str
    ) -> Dict[str, Any]:
        """
        获取竞品关键词布局

        Args:
            site: 站点
            asin: 产品 ASIN

        Returns:
            dict: 竞品关键词布局
        """
        return self._call(
            self.TOOLS['competitor_product_keywords'],
            {"amzSite": site, "asin": asin}
        )

    # ========================================================================
    # 供应链 API
    # ========================================================================

    def get_1688_products(
        self,
        search_name: str
    ) -> Dict[str, Any]:
        """
        获取 1688 相似产品

        Args:
            search_name: 搜索关键词

        Returns:
            dict: 1688 产品列表
        """
        return self._call(
            self.TOOLS['ali1688'],
            {"searchName": search_name}
        )


# ============================================================================
# 便捷函数
# ============================================================================

def create_client() -> SorftimeClient:
    """创建 Sorftime 客户端（便捷函数）"""
    return SorftimeClient()


# ============================================================================
# 命令行接口
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sorftime API 客户端")
    parser.add_argument("tool", choices=[
        "category_report", "keyword_detail", "product_detail",
        "product_reviews", "category_trend"
    ], help="API 工具名称")
    parser.add_argument("--site", default="US", help="站点")
    parser.add_argument("--node-id", type=int, help="类目 Node ID")
    parser.add_argument("--keyword", help="关键词")
    parser.add_argument("--asin", help="产品 ASIN")
    parser.add_argument("--output", "-o", help="输出文件路径")

    args = parser.parse_args()

    client = SorftimeClient()

    if args.tool == "category_report":
        if not args.node_id:
            parser.error("--node-id 是必需的")
        result = client.get_category_report(args.site, args.node_id)

    elif args.tool == "keyword_detail":
        if not args.keyword:
            parser.error("--keyword 是必需的")
        result = client.get_keyword_detail(args.site, args.keyword)

    elif args.tool == "product_detail":
        if not args.asin:
            parser.error("--asin 是必需的")
        result = client.get_product_detail(args.site, args.asin)

    elif args.tool == "product_reviews":
        if not args.asin:
            parser.error("--asin 是必需的")
        result = client.get_product_reviews(args.site, args.asin)

    elif args.tool == "category_trend":
        if not args.node_id:
            parser.error("--node-id 是必需的")
        result = client.get_category_trend(args.site, args.node_id)

    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✓ 结果已保存到: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
