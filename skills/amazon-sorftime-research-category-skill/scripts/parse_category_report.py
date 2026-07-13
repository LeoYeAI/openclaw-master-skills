#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sorftime category_report 完整解析脚本
一键提取统计数据、产品列表、计算评分
"""

import re
import sys
import json
import codecs
from typing import Dict, List, Optional


class CategoryReportParser:
    """类目报告解析器"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = None
        self.statistics = {}
        self.products = []
        self.scores = {}

    def load(self) -> bool:
        """加载文件"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            return True
        except Exception as e:
            print(f"错误: 无法读取文件 - {e}")
            return False

    def extract_statistics(self) -> Dict[str, str]:
        """提取统计数据"""
        if not self.content:
            return {}

        # 先解码 Unicode 转义
        decoded_content = self._decode_unicode_escapes(self.content)

        # 使用 Unicode 转义格式的键名（如 \u0022\u6807\u9898\u0022 = "标题"）
        # 以及普通格式的键名
        patterns = [
            # Unicode 转义格式
            (r'\\u0022top100\u4ea7\u54c1\u6708\u9500\u91cf\\u0022:\\u0022?(\d+)\\u0022?', '总销量'),
            (r'\\u0022top100\u4ea7\u54c1\u6708\u9500\u989d\\u0022:\\u0022?([\d.]+)\\u0022?', '总销额'),
            (r'\\u0022average_price\\u0022:\\u0022?([\d.]+)\\u0022?', '平均价格'),
            (r'\\u0022median_price\\u0022:\\u0022?([\d.]+)\\u0022?', '中位数价格'),
            (r'\\u0022top3_brands_sales_volume_share\\u0022:\\u0022?([\d.]+%?)\\u0022?', 'Top3品牌占比'),
            (r'\\u0022amazonOwned_sales_volume_share\\u0022:\\u0022?([\d.]+%?)\\u0022?', 'Amazon自营占比'),
            (r'\\u0022low_reviews_sales_volume_share\\u0022:\\u0022?([\d.]+%?)\\u0022?', '低评论占比'),
            # 普通格式（如果已解码）
            (r'"top100产品月销量":"?(\d+)"?', '总销量'),
            (r'"top100产品月销额":"?([\d.]+)"?', '总销额'),
            (r'"average_price":"?([\d.]+)"?', '平均价格'),
            (r'"top3_brands_sales_volume_share":"?([\d.]+%?)"?', 'Top3品牌占比'),
            (r'"amazonOwned_sales_volume_share":"?([\d.]+%?)"?', 'Amazon自营占比'),
            (r'"low_reviews_sales_volume_share":"?([\d.]+%?)"?', '低评论占比'),
        ]

        results = {}
        for pattern, name in patterns:
            match = re.search(pattern, decoded_content)
            if match:
                results[name] = match.group(1)
            elif name not in results:  # 只在第一次尝试未找到时记录
                results[name] = "未找到"

        self.statistics = results
        return results

    def _decode_unicode_escapes(self, text: str) -> str:
        """解码 Unicode 转义字符"""
        # 处理 SSE 格式
        decoded = text
        for line in decoded.split('\n'):
            if line.startswith('data: '):
                json_text = line[6:]
                try:
                    data = json.loads(json_text)
                    result_text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                    if result_text:
                        # 解码 Unicode 转义
                        return codecs.decode(result_text, 'unicode-escape')
                except:
                    pass
        return decoded

    def extract_products(self, limit: int = 100) -> List[Dict]:
        """提取 Top N 产品"""
        if not self.content:
            return []

        # 先解码 Unicode 转义
        decoded_content = self._decode_unicode_escapes(self.content)

        products = []

        # Unicode 转义格式的键名
        # \u0022ASIN\u0022 = "ASIN", \u0022\u6807\u9898\u0022 = "标题", etc.
        # 匹配完整的产品对象
        product_pattern = r'\{\\u0022ASIN\\u0022:\\u0022([A-Z0-9]{10})\\u0022[^\}]*?\\u0022\u6708\u9500\u91cf\\u0022:\\u0022?(\d+)\\u0022?[^\}]*?\\u0022\u6807\u9898\\u0022:\\u0022([^\\u0022]{30,150})\\u0022[^\}]*?\\u0022\u4ef7\u683c\\u0022:([\d.]+)[^\}]*?\\u0022\u661f\u7ea7\\u0022:\\u0022?([\d.]+)\\u0022?[^\}]*?\\u0022\u54c1\u724c\\u0022:\\u0022([^\\u0022]+?)\\u0022[^\}]*?\}'

        for match in re.finditer(product_pattern, decoded_content):
            asin, sales, title, price, rating, brand = match.groups()

            products.append({
                'ASIN': asin,
                '标题': title,
                '价格': float(price),
                '月销量': int(sales),
                '评分': float(rating),
                '品牌': brand
            })

            if len(products) >= limit:
                break

        # 如果 Unicode 格式没找到，尝试普通格式
        if len(products) < limit:
            product_pattern2 = r'\{"ASIN":"([A-Z0-9]{10})"[^\}]*?"月销量":"?(\d+)"?[^\}]*?"标题":"([^"]{30,150})"[^\}]*?"价格":"?([\d.]+)"?[^\}]*?"星级":"?([\d.]+)"?[^\}]*?"品牌":"([^"]+?)"[^\}]*?\}'
            for match in re.finditer(product_pattern2, decoded_content):
                asin, sales, title, price, rating, brand = match.groups()
                # 避免重复添加
                if not any(p['ASIN'] == asin for p in products):
                    products.append({
                        'ASIN': asin,
                        '标题': title,
                        '价格': float(price),
                        '月销量': int(sales),
                        '评分': float(rating),
                        '品牌': brand
                    })
                    if len(products) >= limit:
                        break

        self.products = products
        return products

    def calculate_scores(self) -> Dict[str, float]:
        """计算五维评分"""
        if not self.statistics:
            return {}

        def safe_float(value, default=0):
            try:
                return float(str(value).replace('%', '').replace(',', ''))
            except:
                return default

        revenue = safe_float(self.statistics.get('总销额', 0))
        top3_share = safe_float(self.statistics.get('Top3品牌占比', 0))
        amazon_share = safe_float(self.statistics.get('Amazon自营占比', 0))
        low_review_share = safe_float(self.statistics.get('低评论占比', 0))
        avg_price = safe_float(self.statistics.get('平均价格', 0))

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

        self.scores = scores
        return scores

    def parse(self, limit: int = 100) -> Dict:
        """完整解析"""
        if not self.load():
            return {'error': '无法加载文件'}

        self.extract_statistics()
        self.extract_products(limit)
        self.calculate_scores()

        return {
            'statistics': self.statistics,
            'products': self.products,
            'scores': self.scores
        }

    def print_report(self):
        """打印报告"""
        print("=" * 70)
        print("类目选品分析报告")
        print("=" * 70)

        # 统计数据
        if self.statistics:
            print("\n【统计数据】")
            for name, value in self.statistics.items():
                print(f"  {name}: {value}")

        # 评分
        if self.scores:
            print("\n【五维评分】")
            for key, value in self.scores.items():
                if key not in ['总分', '评级']:
                    print(f"  {key}: {value}")
            print(f"\n  总分: {self.scores.get('总分', 0)}/100")
            print(f"  评级: {self.scores.get('评级', '未知')}")

        # 产品列表
        if self.products:
            print(f"\n【Top {len(self.products)} 产品】")
            print("-" * 100)
            for i, p in enumerate(self.products, 1):
                print(f"{i}. {p.get('ASIN')} | {p.get('品牌')} | "
                      f"${p.get('价格', 0):.2f} | {p.get('月销量', 0):,}销量 | "
                      f"{p.get('评分', 0):.1f}★")
                title = p.get('标题', '')[:60]
                print(f"   {title}...")
            print("-" * 100)


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python parse_category_report.py <响应文件路径> [产品数量]")
        print("\n示例:")
        print("  python parse_category_report.py temp_response.txt 100")
        print("\n选项:")
        print("  --json    输出 JSON 格式")
        print("  --save    保存为 JSON 文件")
        sys.exit(1)

    file_path = sys.argv[1]
    limit = 100

    # 解析参数
    for arg in sys.argv[2:]:
        if arg.isdigit():
            limit = int(arg)

    # 解析报告
    parser = CategoryReportParser(file_path)
    result = parser.parse(limit)

    if 'error' in result:
        print(f"错误: {result['error']}")
        sys.exit(1)

    # 打印报告
    parser.print_report()

    # JSON 输出
    if '--json' in sys.argv:
        print("\n" + "=" * 70)
        print("JSON 格式输出")
        print("=" * 70)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # 保存文件
    if '--save' in sys.argv:
        output_file = file_path.replace('.txt', '_parsed.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n已保存到: {output_file}")


if __name__ == "__main__":
    main()
