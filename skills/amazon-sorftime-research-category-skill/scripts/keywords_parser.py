#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sorftime 关键词 SSE 响应解析器 v3.0 - 稳定增强版

支持多种关键词数据格式:
1. 中文键名: [{"关键词": "...", "月搜索量": "..."}]
2. 英文键名: [{"keyword": "...", "monthlySearchVolume": "..."}]
3. 嵌套转义格式
4. 直接从 SSE data: 行提取

主要改进:
1. 更好的错误处理
2. 支持直接 JSON 格式
3. 自动格式标准化
"""

import re
import json
import codecs
import sys
import os


def safe_int(value, default=0):
    """安全地转换为整数"""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        # 移除非数字字符
        cleaned = re.sub(r'[^\d]', '', value)
        try:
            return int(cleaned) if cleaned else default
        except ValueError:
            return default
    return default


def parse_keywords_sse(file_path: str, verbose: bool = False) -> list:
    """
    解析关键词 SSE 响应文件

    Args:
        file_path: SSE 响应文件路径
        verbose: 是否显示调试信息

    Returns:
        list: 解析后的关键词列表
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if verbose:
        print(f"[DEBUG] 文件大小: {len(content)} 字节")
        print(f"[DEBUG] 文件前200字符: {content[:200]}")

    keywords = []

    # 策略 1: 标准 SSE 格式
    if verbose:
        print("\n[策略1] 尝试标准 SSE 格式...")

    for line in content.split('\n'):
        if line.startswith('data: '):
            json_text = line[6:]
            try:
                data = json.loads(json_text)
                result_text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                if result_text:
                    # 尝试直接解析
                    try:
                        keywords = json.loads(result_text)
                        if isinstance(keywords, list) and keywords:
                            if verbose:
                                print(f"[策略1] ✓ 成功，找到 {len(keywords)} 个关键词")
                            return keywords
                    except json.JSONDecodeError:
                        # 尝试 Unicode 解码
                        decoded = codecs.decode(result_text, 'unicode-escape')
                        keywords = json.loads(decoded)
                        if isinstance(keywords, list) and keywords:
                            if verbose:
                                print(f"[策略1] ✓ Unicode 解码成功，找到 {len(keywords)} 个关键词")
                            return keywords
            except Exception as e:
                if verbose:
                    print(f"[策略1] 失败: {e}")
                continue

    # 策略 2: 直接 JSON 解析（已解码的文件）
    if verbose:
        print("\n[策略2] 尝试直接 JSON 解析...")

    try:
        keywords = json.loads(content)
        if isinstance(keywords, list) and keywords:
            if verbose:
                print(f"[策略2] ✓ 成功，找到 {len(keywords)} 个关键词")
            return keywords
    except:
        pass

    # 策略 3: 直接 JSON 数组提取
    if verbose:
        print("\n[策略3] 尝试直接 JSON 数组提取...")

    # 查找数组开始
    patterns = [
        r'(\[{\"?关键词\"?)',
        r'(\[{\"?keyword\"?)',
        r'(\[.*\"?关键词\"?)',
    ]

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            # 找到数组开始位置
            start = match.start()
            # 手动解析括号匹配
            bracket_count = 0
            in_string = False
            escape_next = False
            end = -1

            for i in range(start, len(content)):
                c = content[i]

                if escape_next:
                    escape_next = False
                    continue

                if c == '\\':
                    escape_next = True
                    continue

                if c == '"' and not escape_next:
                    in_string = not in_string
                    continue

                if not in_string:
                    if c == '[':
                        bracket_count += 1
                    elif c == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end = i + 1
                            break

            if end != -1:
                raw_json = content[start:end]

                try:
                    keywords = json.loads(raw_json)
                    if isinstance(keywords, list) and keywords:
                        if verbose:
                            print(f"[策略3] ✓ 成功，找到 {len(keywords)} 个关键词")
                        return keywords
                except json.JSONDecodeError:
                    # 尝试 Unicode 解码
                    try:
                        decoded = codecs.decode(raw_json, 'unicode-escape')
                        keywords = json.loads(decoded)
                        if isinstance(keywords, list) and keywords:
                            if verbose:
                                print(f"[策略3] ✓ Unicode 解码成功，找到 {len(keywords)} 个关键词")
                            return keywords
                    except:
                        pass

    raise ValueError("无法解析关键词数据 - 所有策略均失败")


def normalize_keywords(keywords: list) -> list:
    """标准化关键词数据格式"""
    normalized = []

    for kw in keywords:
        if not isinstance(kw, dict):
            continue

        normalized_kw = {}

        # 标准化键名
        normalized_kw['关键词'] = kw.get('关键词') or kw.get('keyword', '')

        # 搜索量字段可能的键名
        for key in ['月搜索量', 'monthlySearchVolume', '月搜', 'monthlySearch']:
            if key in kw:
                normalized_kw['月搜索量'] = safe_int(kw[key])
                break
        if '月搜索量' not in normalized_kw:
            normalized_kw['月搜索量'] = 0

        # 周搜索量
        for key in ['周搜索量', 'weeklySearchVolume', '周搜', 'weeklySearch']:
            if key in kw:
                normalized_kw['周搜索量'] = safe_int(kw[key])
                break
        if '周搜索量' not in normalized_kw:
            normalized_kw['周搜索量'] = 0

        # 其他常用字段
        normalized_kw['周搜索排名'] = kw.get('周搜索排名', kw.get('weeklySearchRank', ''))
        normalized_kw['CPC竞价'] = kw.get('CPC竞价', kw.get('cpc精准竞价', kw.get('cpcBid', kw.get('cpc', ''))))

        normalized.append(normalized_kw)

    return normalized


def main():
    if len(sys.argv) < 2:
        print("用法: python keywords_parser.py <SSE响应文件> [输出目录] [产品数量] [--verbose]")
        print("\n示例:")
        print("  python keywords_parser.py keywords_raw.txt")
        print("  python keywords_parser.py keywords_raw.txt ./output 50")
        print("  python keywords_parser.py keywords_raw.txt ./output 20 --verbose")
        sys.exit(1)

    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    limit = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 50
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    try:
        print(f"\n正在解析关键词文件: {file_path}")

        # 解析关键词
        keywords = parse_keywords_sse(file_path, verbose=verbose)

        # 标准化格式
        normalized = normalize_keywords(keywords)

        print(f"\n✓ 成功解析 {len(normalized)} 个关键词")

        # 保存
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'keywords.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(normalized, f, ensure_ascii=False, indent=2)

        print(f"✓ 关键词已保存到: {output_file}")

        # 显示 Top 10
        display_count = min(10, len(normalized))
        print(f"\n【Top {display_count} 关键词】")
        print("-" * 80)
        for i, kw in enumerate(normalized[:display_count], 1):
            print(f"{i:2}. {kw['关键词']:<30} | 月搜索: {kw['月搜索量']:,} | 周搜索: {kw['周搜索量']:,}")
        print("-" * 80)

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
