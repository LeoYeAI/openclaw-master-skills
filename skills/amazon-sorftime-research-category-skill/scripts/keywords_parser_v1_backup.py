#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sorftime 类目关键词解析器
处理 category_keywords 返回的 SSE 响应
"""

import re
import json
import codecs
import sys
import os


def fix_mojibake(obj):
    """
    修复 UTF-8/Latin-1 双重编码问题 (Mojibake)

    当 UTF-8 字节被错误地解释为 Latin-1 时会产生乱码:
    解决方法: encode('latin-1') → decode('utf-8')
    """
    if isinstance(obj, dict):
        return {fix_mojibake(k): fix_mojibake(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [fix_mojibake(item) for item in obj]
    elif isinstance(obj, str):
        # 检查是否包含典型 Mojibake 模式
        mojibake_patterns = ['æ ', 'é¢', 'å ', 'ä»£', 'åç', 'å³']
        if any(p in obj for p in mojibake_patterns):
            try:
                return obj.encode('latin-1').decode('utf-8')
            except:
                return obj
        return obj
    else:
        return obj


def decode_keywords_response(file_path: str) -> list:
    """
    解码 category_keywords SSE 响应文件

    Args:
        file_path: SSE 响应文件路径

    Returns:
        list: 关键词数据列表
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 方法 1: 查找 SSE data 行
    for line in content.split('\n'):
        if line.startswith('data: '):
            json_text = line[6:]
            try:
                data = json.loads(json_text)
                result_text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                if result_text and ('关键词' in result_text or 'keyword' in result_text.lower()):
                    # 解码 Unicode 转义
                    decoded = codecs.decode(result_text, 'unicode-escape')

                    # 提取 JSON 数组 - 支持多种格式
                    # 格式 1: [{"关键词": 或格式 2: [{"keyword":
                    start = decoded.find('[{"关键词"')
                    if start == -1:
                        start = decoded.find('[{"keyword"')
                    if start == -1:
                        start = decoded.find('[{')

                    if start != -1:
                        # 找到匹配的结束括号
                        bracket_count = 0
                        in_string = False
                        escape_next = False
                        end = -1

                        for i in range(start, len(decoded)):
                            c = decoded[i]

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
                            json_str = decoded[start:end]
                            result = json.loads(json_str)
                            # 修复可能的编码问题
                            return fix_mojibake(result)
            except Exception as e:
                print(f"方法1解析失败: {e}")
                continue

    # 方法 2: 备用方法 - 直接从原始内容提取
    # 查找包含关键词的 JSON 数组片段
    bracket_count = 0
    in_array = False
    start = -1
    end = -1

    for i, c in enumerate(content):
        if c == '[':
            if not in_array:
                # 检查这是否是关键词数组的开始
                lookahead = content[i:i+200]
                if ('关键词' in lookahead or 'keyword' in lookahead.lower()):
                    in_array = True
                    start = i
            bracket_count += 1
        elif c == ']':
            bracket_count -= 1
            if in_array and bracket_count == 0:
                end = i + 1
                break

    if start != -1 and end != -1:
        raw_json = content[start:end]
        try:
            # 清理并解码
            decoded = codecs.decode(raw_json, 'unicode-escape')
            result = json.loads(decoded)
            return fix_mojibake(result)
        except Exception as e:
            print(f"方法2解析失败: {e}")

    # 方法 3: 使用正则表达式提取关键词数组
    try:
        # 查找 [{...}] 模式
        array_pattern = r'\[\{[^\]]*?"关键词"[^\]]*?\}'
        matches = re.findall(array_pattern, content, re.DOTALL)
        for match in matches:
            try:
                decoded = codecs.decode(match, 'unicode-escape')
                result = json.loads(decoded)
                if isinstance(result, list) and len(result) > 0:
                    return fix_mojibake(result)
            except:
                continue
    except Exception as e:
        print(f"方法3解析失败: {e}")

    raise ValueError("无法解析关键词数据 - 请检查文件格式是否正确")


def format_keyword_data(kw: dict) -> dict:
    """格式化单个关键词数据"""
    return {
        '关键词': kw.get('关键词', ''),
        '周搜索排名': kw.get('周搜索排名', '0'),
        '周搜索量': kw.get('周搜索量', '0'),
        '月搜索量': kw.get('月搜索量', '0'),
        'CPC竞价': kw.get('cpc精准竞价', '0'),
        '搜索结果数': kw.get('搜索结果数', '0'),
        '新品占比': kw.get('搜索结果前3页产品中上线3个月内产品数量占比', '0'),
    }


def print_keywords_table(keywords: list, limit: int = 20):
    """打印关键词表格"""
    print("\n" + "=" * 90)
    print(f"类目核心关键词 Top {min(len(keywords), limit)}")
    print("=" * 90)
    print(f"{'排名':<6}{'关键词':<25}{'月搜索量':<15}{'周排名':<10}{'CPC竞价':<10}{'新品占比':<10}")
    print("-" * 90)

    for i, kw in enumerate(keywords[:limit], 1):
        keyword = kw.get('关键词', 'N/A')
        monthly = kw.get('月搜索量', '0')
        rank = kw.get('周搜索排名', '0')
        cpc = kw.get('CPC竞价', '0')
        new_pct = kw.get('新品占比', '0')

        # 格式化数字
        try:
            monthly = f"{int(float(monthly)):,}"
        except:
            pass

        try:
            cpc = f"${float(cpc):.2f}"
        except:
            cpc = f"${cpc}"

        try:
            new_pct = f"{new_pct}%"
        except:
            pass

        print(f"{i:<6}{keyword:<25}{monthly:<15}{rank:<10}{cpc:<10}{new_pct:<10}")


def save_keywords(keywords: list, output_file: str):
    """保存关键词到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("类目核心关键词\n")
        f.write("=" * 90 + "\n")
        f.write(f"{'排名':<6}{'关键词':<25}{'月搜索量':<15}{'周排名':<10}{'CPC竞价':<10}{'新品占比':<10}\n")
        f.write("-" * 90 + "\n")

        for i, kw in enumerate(keywords, 1):
            keyword = kw.get('关键词', 'N/A')
            monthly = kw.get('月搜索量', '0')
            rank = kw.get('周搜索排名', '0')
            cpc = kw.get('CPC竞价', '0')
            new_pct = kw.get('新品占比', '0')

            try:
                monthly = f"{int(float(monthly)):,}"
            except:
                pass
            try:
                cpc = f"${float(cpc):.2f}"
            except:
                pass
            try:
                new_pct = f"{new_pct}%"
            except:
                pass

            f.write(f"{i:<6}{keyword:<25}{monthly:<15}{rank:<10}{cpc:<10}{new_pct:<10}\n")


def main():
    if len(sys.argv) < 2:
        print("用法: python keywords_parser.py <SSE响应文件> [输出目录] [显示数量]")
        print("\n示例:")
        print("  python keywords_parser.py keywords_response.txt")
        print("  python keywords_parser.py keywords_response.txt ./output 50")
        sys.exit(1)

    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    limit = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 20

    try:
        # 解码关键词响应
        keywords_raw = decode_keywords_response(file_path)

        # 格式化数据
        keywords = [format_keyword_data(kw) for kw in keywords_raw]

        # 打印表格
        print_keywords_table(keywords, limit)

        # 保存到文件
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'keywords.txt')
        save_keywords(keywords, output_file)
        print(f"\n关键词已保存到: {output_file}")

        # 保存 JSON 格式
        json_file = os.path.join(output_dir, 'keywords.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(keywords, f, ensure_ascii=False, indent=2)
        print(f"JSON 格式已保存到: {json_file}")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
