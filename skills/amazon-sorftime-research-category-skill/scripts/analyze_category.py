#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品类选品一体化分析脚本
一个命令完成：API 调用 → 数据解析 → 报告生成
"""

import os
import sys
import json
import re
import codecs
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class CategoryAnalyzer:
    """品类选品一体化分析器"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化分析器"""
        self.api_key = api_key or self._load_api_key()
        self.base_url = "https://mcp.sorftime.com"
        self.request_id = 0
        self.category_name = None
        self.site = "US"
        self.limit = 100

    def _load_api_key(self) -> str:
        """从配置文件加载 API Key"""
        config_file = Path(".mcp.json")
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                url = config['mcpServers']['sorftime']['url']
                return url.split('key=')[-1]
        raise FileNotFoundError("找不到 .mcp.json 配置文件")

    def _get_next_id(self) -> int:
        """获取下一个请求 ID"""
        self.request_id += 1
        return self.request_id

    def _call_api(self, tool_name: str, arguments: Dict) -> Optional[Dict]:
        """调用 Sorftime MCP API"""
        url = f"{self.base_url}?key={self.api_key}"
        payload = {
            'jsonrpc': '2.0',
            'id': self._get_next_id(),
            'method': 'tools/call',
            'params': {
                'name': tool_name,
                'arguments': arguments
            }
        }

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=120,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code != 200:
                print(f"  ✗ HTTP {response.status_code}")
                return None

            # 解析 SSE 响应
            return self._parse_sse_response(response.text)

        except Exception as e:
            print(f"  ✗ 异常: {e}")
            return None

    def _parse_sse_response(self, raw_text: str):
        """解析 SSE 响应，支持对象和数组"""
        try:
            lines = raw_text.split('\n')
            for line in lines:
                if line.startswith('data: '):
                    json_data = line[6:]  # 去掉 'data: ' 前缀
                    data = json.loads(json_data)

                    if 'error' in data:
                        return None

                    if 'result' in data:
                        result = data['result']
                        if 'content' in result and len(result['content']) > 0:
                            content = result['content'][0]
                            if 'text' in content:
                                text = content['text']
                                if not text:
                                    continue

                                # JSON 已经自动解码了 Unicode 转义，不需要再用 codecs.decode
                                # 直接使用 text 即可
                                decoded = text

                                # 查找第一个完整的 JSON 对象（包含产品数据）
                                first_obj_start = decoded.find('{')
                                if first_obj_start != -1:
                                    depth = 0
                                    end = -1
                                    for i in range(first_obj_start, len(decoded)):
                                        if decoded[i] == '{':
                                            depth += 1
                                        elif decoded[i] == '}':
                                            depth -= 1
                                            if depth == 0:
                                                end = i + 1
                                                break

                                    if end != -1:
                                        json_str = decoded[first_obj_start:end]
                                        json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
                                        return json.loads(json_str)

                                # 如果没找到对象，尝试数组
                                first_arr_start = decoded.find('[')
                                if first_arr_start != -1:
                                    depth = 0
                                    end = -1
                                    for i in range(first_arr_start, len(decoded)):
                                        if decoded[i] == '[':
                                            depth += 1
                                        elif decoded[i] == ']':
                                            depth -= 1
                                            if depth == 0:
                                                end = i + 1
                                                break

                                    if end != -1:
                                        json_str = decoded[first_arr_start:end]
                                        json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
                                        return json.loads(json_str)

            return None

        except Exception as e:
            print(f"  ✗ SSE 解析异常: {e}")
            return None

    def _fix_chinese_keys(self, obj):
        """修复中文键名的编码问题"""
        if isinstance(obj, dict):
            new_dict = {}
            for key, value in obj.items():
                fixed_key = self._fix_key(key)
                new_dict[fixed_key] = self._fix_chinese_keys(value)
            return new_dict
        elif isinstance(obj, list):
            return [self._fix_chinese_keys(item) for item in obj]
        else:
            return obj

    def _fix_key(self, key: str) -> str:
        """修复单个键名的编码问题"""
        if not isinstance(key, str):
            return key

        # 检查是否包含高字节字符 (可能是编码问题)
        if not any(0x80 <= ord(c) <= 0xFF for c in key):
            return key

        # 方法1: 尝试 latin-1 -> utf-8
        try:
            return key.encode('latin-1').decode('utf-8')
        except:
            pass

        # 方法2: 尝试 ISO-8859-1 -> utf-8
        try:
            return key.encode('iso-8859-1').decode('utf-8')
        except:
            pass

        # 方法3: 尝试 cp1252 -> utf-8
        try:
            return key.encode('cp1252').decode('utf-8')
        except:
            pass

        # 都失败了，返回原键
        return key

    def search_category(self, category_name: str, site: str = "US") -> Optional[str]:
        """搜索品类获取 nodeId"""
        print(f"[1/6] 搜索类目: {category_name} ({site})")

        result = self._call_api('category_name_search', {
            'amzSite': site,
            'searchName': category_name
        })

        if not result:
            print(f"  ✗ 未找到类目: {category_name}")
            return None

        # 处理不同的返回格式
        categories = []
        if isinstance(result, list):
            categories = result
        elif isinstance(result, str):
            # 如果是字符串，尝试解析为 JSON
            try:
                categories = json.loads(result)
            except:
                print(f"  ✗ 无法解析类目数据")
                return None
        elif isinstance(result, dict):
            # 如果是字典，可能是单条结果
            categories = [result]

        if not categories:
            print(f"  ✗ 类目列表为空")
            return None

        # 选择第一个类目
        selected = categories[0]
        node_id = selected.get('NodeId') or selected.get('nodeId')
        name = selected.get('Name') or selected.get('name')

        # 保存品类名称
        self.category_name = name if name else category_name

        print(f"  ✓ 找到类目: {self.category_name} (nodeId: {node_id})")

        return node_id

    def get_category_report(self, node_id: str) -> Optional[Dict]:
        """获取类目报告"""
        print(f"[2/6] 获取类目报告...")

        result = self._call_api('category_report', {
            'amzSite': self.site,
            'nodeId': node_id
        })

        if not result:
            print(f"  ✗ 获取类目报告失败")
            return None

        result = self._fix_chinese_keys(result)

        # 统计信息
        stats = result.get('类目统计报告', {})
        products = result.get('Top100产品', [])

        print(f"  ✓ 类目报告获取成功")
        print(f"    - 产品数量: {len(products)}")

        return result

    def extract_and_analyze(self, report_data: Dict) -> Dict:
        """提取数据并分析"""
        print(f"[3/6] 提取和分析数据...")

        # 提取统计数据
        stats = report_data.get('类目统计报告', {})

        # 提取产品列表
        products = report_data.get('Top100产品', [])[:self.limit]

        # 计算评分
        scores = self._calculate_scores(stats)

        print(f"  ✓ 数据提取完成")
        print(f"    - 总销量: {stats.get('top100产品月销量', 'N/A')}")
        print(f"    - 平均价格: {stats.get('average_price', 'N/A')}")

        return {
            'category_name': self.category_name,
            'site': self.site,
            'limit': self.limit,
            'statistics': stats,
            'products': products,
            'scores': scores,
            'timestamp': datetime.now().isoformat()
        }

    def _calculate_scores(self, stats: Dict) -> Dict:
        """计算五维评分"""
        def safe_float(value, default=0):
            try:
                return float(str(value).replace('%', '').replace(',', ''))
            except:
                return default

        revenue = safe_float(stats.get('top100产品月销额', 0))
        top3_share = safe_float(stats.get('top3_brands_sales_volume_share', 0))
        amazon_share = safe_float(stats.get('amazonOwned_sales_volume_share', 0))
        low_review_share = safe_float(stats.get('low_reviews_sales_volume_share', 0))
        avg_price = safe_float(stats.get('average_price', 0))

        scores = {}

        # 市场规模
        if revenue > 10000000:
            scores['市场规模'] = 20
        elif revenue > 5000000:
            scores['市场规模'] = 17
        elif revenue > 1000000:
            scores['市场规模'] = 14
        else:
            scores['市场规模'] = 10

        # 增长潜力
        if low_review_share > 40:
            scores['增长潜力'] = 22
        elif low_review_share > 20:
            scores['增长潜力'] = 18
        else:
            scores['增长潜力'] = 14

        # 竞争烈度
        if top3_share < 30:
            scores['竞争烈度'] = 18
        elif top3_share < 50:
            scores['竞争烈度'] = 14
        else:
            scores['竞争烈度'] = 8

        # 进入壁垒
        barrier_score = 0
        if amazon_share < 20:
            barrier_score += 10
        elif amazon_share < 40:
            barrier_score += 6
        else:
            barrier_score += 3

        if low_review_share > 40:
            barrier_score += 10
        elif low_review_share > 20:
            barrier_score += 6
        else:
            barrier_score += 3

        scores['进入壁垒'] = barrier_score

        # 利润空间
        if avg_price > 300:
            scores['利润空间'] = 12
        elif avg_price > 150:
            scores['利润空间'] = 10
        elif avg_price > 50:
            scores['利润空间'] = 7
        else:
            scores['利润空间'] = 4

        scores['总分'] = sum(scores.values())

        if scores['总分'] >= 80:
            scores['评级'] = '优秀'
        elif scores['总分'] >= 70:
            scores['评级'] = '良好'
        elif scores['总分'] >= 50:
            scores['评级'] = '一般'
        else:
            scores['评级'] = '较差'

        return scores

    def generate_reports(self, data: Dict) -> Path:
        """生成所有格式的报告"""
        print(f"[4/6] 生成报告...")

        # 导入报告生成器
        try:
            from generate_reports import CategoryReportGenerator
        except ImportError:
            print("  ✗ 报告生成模块未找到")
            return None

        # 创建输出目录
        date_str = datetime.now().strftime('%Y/%m')
        safe_name = self._sanitize_filename(self.category_name)
        output_dir = Path('category-reports') / date_str / f"{safe_name}_{self.site}"

        # 生成报告
        generator = CategoryReportGenerator(data, str(output_dir))
        report_files = generator.generate_all()

        print(f"  ✓ 报告已保存到: {output_dir}")

        # 打印文件列表
        for format_type, path in report_files.items():
            print(f"    [{format_type.upper()}] {path}")

        return output_dir

    def _sanitize_filename(self, name: str) -> str:
        """清理文件名"""
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            name = name.replace(char, '_')
        name = name.replace(' ', '_')
        return name[:50]

    def analyze(self, category_name: str, site: str = "US", limit: int = 100) -> bool:
        """
        执行完整的品类分析

        Args:
            category_name: 品类名称
            site: 亚马逊站点
            limit: 分析产品数量

        Returns:
            是否成功
        """
        start_time = datetime.now()

        print("=" * 70)
        print(f"品类选品分析")
        print("=" * 70)
        print(f"品类: {category_name}")
        print(f"站点: {site}")
        print(f"分析数量: Top{limit}")
        print(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        self.site = site
        self.limit = limit

        # 步骤 1: 搜索品类
        node_id = self.search_category(category_name, site)
        if not node_id:
            return False

        # 步骤 2: 获取类目报告
        report_data = self.get_category_report(node_id)
        if not report_data:
            return False

        # 步骤 3: 提取和分析数据
        data = self.extract_and_analyze(report_data)

        # 步骤 4: 生成报告
        output_dir = self.generate_reports(data)

        # 完成
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "=" * 70)
        print("分析完成！")
        print("=" * 70)
        print(f"总耗时: {duration:.1f} 秒")
        print(f"输出目录: {output_dir}")
        print(f"数据时间: {data.get('timestamp', '')}")
        print(f"综合评级: {data['scores'].get('评级', 'N/A')} ({data['scores'].get('总分', 0)}/100)")
        print("=" * 70)

        return True


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python analyze_category.py <品类名称> [站点] [分析数量]")
        print("\n示例:")
        print("  python analyze_category.py \"Phone Cases\" US 20")
        print("  python analyze_category.py Sofas US 50")
        print("\n参数:")
        print("  品类名称  - 必填，要分析的品类名称")
        print("  站点       - 可选，默认 US")
        print("  分析数量   - 可选，默认 100")
        sys.exit(1)

    category_name = sys.argv[1]
    site = sys.argv[2] if len(sys.argv) > 2 else "US"
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 100

    # 执行分析
    analyzer = CategoryAnalyzer()
    success = analyzer.analyze(category_name, site, limit)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
