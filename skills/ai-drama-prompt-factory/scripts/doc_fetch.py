#!/usr/bin/env python3
"""
doc_fetch.py - 精准内容获取器
根据索引，定点获取文档的特定章节或行范围

用法：
    python3 doc_fetch.py --index doc_index.json --section "章节名"
    python3 doc_fetch.py --index doc_index.json --file "文件名" --lines 50-100
    python3 doc_fetch.py --index doc_index.json --file "文件名" --all
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


def load_index(index_path: str) -> Dict[str, Any]:
    """加载索引文件"""
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_file_in_index(index: Dict[str, Any], filename: str) -> Optional[Dict[str, Any]]:
    """在索引中查找文件"""
    files = index.get('files', [])
    
    # 精确匹配
    for f in files:
        if f['filename'] == filename or f['filepath'] == filename:
            return f
    
    # 模糊匹配
    for f in files:
        if filename.lower() in f['filename'].lower() or filename.lower() in f['filepath'].lower():
            return f
    
    return None


def find_section_in_file(file_info: Dict[str, Any], section_name: str) -> Optional[Dict[str, Any]]:
    """在文件索引中查找章节"""
    sections = file_info.get('sections', [])
    
    # 精确匹配
    for s in sections:
        if s.get('title', '').lower() == section_name.lower():
            return s
    
    # 模糊匹配
    for s in sections:
        if section_name.lower() in s.get('title', '').lower():
            return s
    
    return None


def parse_line_range(line_range: str) -> Tuple[int, int]:
    """解析行范围，如 '50-100' 或 '50'"""
    if '-' in line_range:
        start, end = line_range.split('-')
        return int(start), int(end)
    else:
        line = int(line_range)
        return line, line + 50  # 默认获取 50 行


def fetch_lines(filepath: str, start: int, end: int) -> str:
    """获取文件的指定行范围"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # 调整为 0-based 索引
        start_idx = max(0, start - 1)
        end_idx = min(len(lines), end)
        
        result_lines = lines[start_idx:end_idx]
        
        # 添加行号
        numbered_lines = []
        for i, line in enumerate(result_lines, start=start_idx + 1):
            numbered_lines.append(f'{i:4d} | {line.rstrip()}')
        
        return '\n'.join(numbered_lines)
    except Exception as e:
        return f'❌ 读取失败: {e}'


def fetch_section(filepath: str, section: Dict[str, Any], context_lines: int = 0) -> str:
    """获取指定章节的内容"""
    start = section.get('start_line', 1)
    end = section.get('end_line', start + 100)
    
    # 添加上下文
    if context_lines > 0:
        start = max(1, start - context_lines)
        end = end + context_lines
    
    return fetch_lines(filepath, start, end)


def fetch_all(filepath: str, max_lines: int = 500) -> str:
    """获取文件全部内容（有限制）"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        if len(lines) > max_lines:
            # 获取开头和结尾
            head = lines[:max_lines // 2]
            tail = lines[-(max_lines // 2):]
            
            result = []
            for i, line in enumerate(head, start=1):
                result.append(f'{i:4d} | {line.rstrip()}')
            
            result.append(f'\n... 省略 {len(lines) - max_lines} 行 ...\n')
            
            tail_start = len(lines) - len(tail) + 1
            for i, line in enumerate(tail, start=tail_start):
                result.append(f'{i:4d} | {line.rstrip()}')
            
            return '\n'.join(result)
        else:
            result = []
            for i, line in enumerate(lines, start=1):
                result.append(f'{i:4d} | {line.rstrip()}')
            return '\n'.join(result)
    except Exception as e:
        return f'❌ 读取失败: {e}'


def list_sections(file_info: Dict[str, Any]) -> str:
    """列出文件的所有章节"""
    sections = file_info.get('sections', [])
    
    if not sections:
        return '该文件没有可识别的章节结构'
    
    result = [f'📑 章节列表 ({len(sections)} 个):\n']
    
    for i, s in enumerate(sections, 1):
        title = s.get('title', '未命名')
        level = s.get('level', 0)
        start = s.get('start_line', '?')
        end = s.get('end_line', '?')
        indent = '  ' * (level - 1) if level > 0 else ''
        
        result.append(f'{indent}{i}. {title} (行 {start}-{end})')
    
    return '\n'.join(result)


def main():
    parser = argparse.ArgumentParser(description='精准内容获取器')
    parser.add_argument('--index', '-i', required=True, help='索引文件路径')
    parser.add_argument('--file', '-f', help='目标文件名（可模糊匹配）')
    parser.add_argument('--section', '-s', help='章节名（可模糊匹配）')
    parser.add_argument('--lines', '-l', help='行范围，如 50-100')
    parser.add_argument('--all', '-a', action='store_true', help='获取全部内容')
    parser.add_argument('--list', action='store_true', help='列出所有章节')
    parser.add_argument('--context', '-c', type=int, default=0, help='章节上下文行数')
    parser.add_argument('--max-lines', type=int, default=500, help='全文获取的最大行数')
    
    args = parser.parse_args()
    
    # 加载索引
    try:
        index = load_index(args.index)
    except Exception as e:
        print(f'❌ 无法加载索引: {e}')
        return 1
    
    files = index.get('files', [])
    
    # 如果只有一个文件，自动选择
    if len(files) == 1 and not args.file:
        file_info = files[0]
    elif args.file:
        file_info = find_file_in_index(index, args.file)
        if not file_info:
            print(f'❌ 未找到文件: {args.file}')
            print(f'可用文件: {", ".join(f["filename"] for f in files)}')
            return 1
    else:
        print('请指定文件 (--file)，或使用以下文件之一:')
        for f in files[:20]:
            print(f'  - {f["filename"]}')
        return 1
    
    filepath = file_info['filepath']
    print(f'📄 文件: {file_info["filename"]}')
    print(f'📍 路径: {filepath}')
    print(f'📝 总行数: {file_info.get("total_lines", "?")}')
    print('=' * 60)
    
    # 列出章节
    if args.list:
        print(list_sections(file_info))
        return 0
    
    # 获取章节
    if args.section:
        section = find_section_in_file(file_info, args.section)
        if not section:
            print(f'❌ 未找到章节: {args.section}')
            print(list_sections(file_info))
            return 1
        
        print(f'📑 章节: {section.get("title")}')
        print(f'📍 位置: 行 {section.get("start_line")}-{section.get("end_line")}')
        print('-' * 60)
        print(fetch_section(filepath, section, args.context))
        return 0
    
    # 获取行范围
    if args.lines:
        start, end = parse_line_range(args.lines)
        print(f'📍 行范围: {start}-{end}')
        print('-' * 60)
        print(fetch_lines(filepath, start, end))
        return 0
    
    # 获取全部
    if args.all:
        print(f'📄 全文内容 (最多 {args.max_lines} 行):')
        print('-' * 60)
        print(fetch_all(filepath, args.max_lines))
        return 0
    
    # 默认：显示章节列表
    print(list_sections(file_info))
    print('\n💡 使用 --section "章节名" 获取特定章节')
    print('   使用 --lines 50-100 获取指定行')
    print('   使用 --all 获取全部内容')
    
    return 0


if __name__ == '__main__':
    exit(main())
