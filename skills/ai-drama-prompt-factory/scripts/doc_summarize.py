#!/usr/bin/env python3
"""
doc_summarize.py - 文档结构摘要器
基于索引生成文档的结构化概览

用法：
    python3 doc_summarize.py --index doc_index.json
    python3 doc_summarize.py --index doc_index.json --depth 3 --keywords
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Any


def load_index(index_path: str) -> Dict[str, Any]:
    """加载索引文件"""
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes < 1024:
        return f'{size_bytes} B'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    else:
        return f'{size_bytes / (1024 * 1024):.1f} MB'


def summarize_file(file_info: Dict[str, Any], depth: int = 2, show_keywords: bool = False) -> str:
    """生成单个文件的摘要"""
    output = []
    
    filename = file_info.get('filename', '未知文件')
    total_lines = file_info.get('total_lines', 0)
    file_type = file_info.get('type', 'unknown')
    size = file_info.get('size_bytes', 0)
    
    output.append(f'📄 {filename}')
    output.append(f'   类型: {file_type} | 行数: {total_lines} | 大小: {format_size(size)}')
    
    # 显示章节结构
    sections = file_info.get('sections', [])
    if sections:
        output.append(f'   📑 章节结构 ({len(sections)} 个):')
        
        shown_sections = 0
        for s in sections:
            level = s.get('level', 1)
            if level <= depth:
                title = s.get('title', '未命名')
                start = s.get('start_line', '?')
                end = s.get('end_line', '?')
                s_type = s.get('type', '')
                
                indent = '   ' * level
                type_tag = f' [{s_type}]' if s_type and s_type not in ['section'] else ''
                output.append(f'   {indent}• {title}{type_tag} (行 {start}-{end})')
                shown_sections += 1
                
                if shown_sections >= 20:
                    output.append(f'   ... 还有 {len(sections) - shown_sections} 个章节')
                    break
    
    # JSON 结构
    if 'structure' in file_info:
        structure = file_info['structure']
        if isinstance(structure, dict):
            if structure.get('type') == 'object':
                keys = structure.get('keys', [])
                output.append(f'   🔑 顶级键: {", ".join(keys[:15])}')
                if len(keys) > 15:
                    output.append(f'       ... 还有 {len(keys) - 15} 个键')
            elif structure.get('type') == 'array':
                output.append(f'   📦 数组长度: {structure.get("length", "?")}')
    
    # 关键词
    if show_keywords:
        keywords = file_info.get('keywords', [])
        if keywords:
            output.append(f'   🔑 关键词: {", ".join(keywords[:15])}')
    
    return '\n'.join(output)


def summarize_directory(index: Dict[str, Any], depth: int = 2, 
                        show_keywords: bool = False, max_files: int = 20) -> str:
    """生成目录索引的摘要"""
    output = []
    
    path = index.get('path', '未知目录')
    total_files = index.get('total_files', 0)
    total_lines = index.get('total_lines', 0)
    indexed_at = index.get('indexed_at', '?')
    
    output.append('=' * 60)
    output.append(f'📁 文档集索引摘要')
    output.append('=' * 60)
    output.append(f'📍 路径: {path}')
    output.append(f'📊 统计: {total_files} 个文件, {total_lines} 行')
    output.append(f'🕐 索引时间: {indexed_at}')
    
    # 全局关键词
    top_keywords = index.get('top_keywords', [])
    if top_keywords:
        output.append(f'🔑 热门关键词: {", ".join(top_keywords[:20])}')
    
    output.append('-' * 60)
    
    # 按类型分组
    files = index.get('files', [])
    by_type = {}
    for f in files:
        ftype = f.get('type', 'unknown')
        if ftype not in by_type:
            by_type[ftype] = []
        by_type[ftype].append(f)
    
    output.append(f'\n📊 文件类型分布:')
    for ftype, file_list in sorted(by_type.items(), key=lambda x: -len(x[1])):
        total_lines_in_type = sum(f.get('total_lines', 0) for f in file_list)
        output.append(f'   • {ftype}: {len(file_list)} 个文件, {total_lines_in_type} 行')
    
    output.append(f'\n📄 文件列表 (显示 {min(max_files, len(files))}/{len(files)}):')
    output.append('-' * 60)
    
    # 按行数排序，大文件优先
    sorted_files = sorted(files, key=lambda x: x.get('total_lines', 0), reverse=True)
    
    for i, file_info in enumerate(sorted_files[:max_files]):
        if i > 0:
            output.append('')
        output.append(summarize_file(file_info, depth, show_keywords))
    
    if len(files) > max_files:
        output.append(f'\n... 还有 {len(files) - max_files} 个文件未显示')
        output.append('   使用 --max-files 增加显示数量')
    
    return '\n'.join(output)


def summarize_single_file(index: Dict[str, Any], depth: int = 2, 
                          show_keywords: bool = False) -> str:
    """生成单文件索引的摘要"""
    files = index.get('files', [])
    if not files:
        return '❌ 索引中没有文件'
    
    file_info = files[0]
    output = []
    
    output.append('=' * 60)
    output.append(f'📄 文档摘要')
    output.append('=' * 60)
    output.append(summarize_file(file_info, depth, show_keywords))
    
    # 额外的详细信息
    sections = file_info.get('sections', [])
    if sections and len(sections) > 5:
        output.append('\n' + '=' * 60)
        output.append('📑 完整章节目录:')
        output.append('=' * 60)
        
        for i, s in enumerate(sections, 1):
            level = s.get('level', 1)
            title = s.get('title', '未命名')
            start = s.get('start_line', '?')
            end = s.get('end_line', '?')
            
            indent = '  ' * (level - 1)
            output.append(f'{i:3d}. {indent}{title} (行 {start}-{end})')
    
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='文档结构摘要器')
    parser.add_argument('--index', '-i', required=True, help='索引文件路径')
    parser.add_argument('--depth', '-d', type=int, default=2, help='显示的章节层级深度')
    parser.add_argument('--keywords', '-k', action='store_true', help='显示关键词')
    parser.add_argument('--max-files', '-m', type=int, default=20, help='最大显示文件数')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    # 加载索引
    try:
        index = load_index(args.index)
    except Exception as e:
        print(f'❌ 无法加载索引: {e}')
        return 1
    
    if args.json:
        # 输出精简的 JSON 摘要
        summary = {
            'type': index.get('type'),
            'path': index.get('path'),
            'total_files': index.get('total_files'),
            'total_lines': index.get('total_lines'),
            'top_keywords': index.get('top_keywords', [])[:20],
            'files': [
                {
                    'filename': f.get('filename'),
                    'type': f.get('type'),
                    'total_lines': f.get('total_lines'),
                    'sections_count': len(f.get('sections', [])),
                }
                for f in index.get('files', [])
            ]
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        # 生成文本摘要
        if index.get('type') == 'directory':
            print(summarize_directory(index, args.depth, args.keywords, args.max_files))
        else:
            print(summarize_single_file(index, args.depth, args.keywords))
    
    return 0


if __name__ == '__main__':
    exit(main())
