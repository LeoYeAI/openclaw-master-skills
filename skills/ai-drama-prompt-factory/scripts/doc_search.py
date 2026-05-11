#!/usr/bin/env python3
"""
doc_search.py - 文档搜索器
在已索引的文档中搜索关键词，返回匹配的上下文

用法：
    python3 doc_search.py --index doc_index.json --query "关键词"
    python3 doc_search.py --index doc_index.json --query "关键词1 关键词2" --context 3
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple


def load_index(index_path: str) -> Dict[str, Any]:
    """加载索引文件"""
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def search_in_file(filepath: str, keywords: List[str], context_lines: int = 2, 
                   max_matches: int = 10) -> List[Dict[str, Any]]:
    """在文件中搜索关键词"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        return [{'error': str(e)}]
    
    matches = []
    
    # 构建正则表达式（大小写不敏感）
    patterns = [re.compile(re.escape(kw), re.IGNORECASE) for kw in keywords]
    
    for i, line in enumerate(lines):
        # 检查是否匹配任一关键词
        matched_keywords = []
        for kw, pattern in zip(keywords, patterns):
            if pattern.search(line):
                matched_keywords.append(kw)
        
        if matched_keywords:
            # 获取上下文
            start_idx = max(0, i - context_lines)
            end_idx = min(len(lines), i + context_lines + 1)
            
            context = []
            for j in range(start_idx, end_idx):
                prefix = '>>>' if j == i else '   '
                context.append(f'{j+1:4d} {prefix} {lines[j].rstrip()}')
            
            matches.append({
                'line_number': i + 1,
                'matched_keywords': matched_keywords,
                'line': line.strip(),
                'context': '\n'.join(context),
            })
            
            if len(matches) >= max_matches:
                break
    
    return matches


def search_in_index(index: Dict[str, Any], keywords: List[str], 
                    context_lines: int = 2, max_matches_per_file: int = 5) -> Dict[str, Any]:
    """在整个索引中搜索"""
    files = index.get('files', [])
    results = []
    total_matches = 0
    
    for file_info in files:
        filepath = file_info['filepath']
        filename = file_info['filename']
        
        # 先检查索引中的关键词
        file_keywords = set(file_info.get('keywords', []))
        keyword_hits = sum(1 for kw in keywords if kw.lower() in 
                         (k.lower() for k in file_keywords))
        
        # 在文件中搜索
        matches = search_in_file(filepath, keywords, context_lines, max_matches_per_file)
        
        if matches and 'error' not in matches[0]:
            results.append({
                'filename': filename,
                'filepath': filepath,
                'keyword_relevance': keyword_hits / len(keywords) if keywords else 0,
                'matches': matches,
                'match_count': len(matches),
            })
            total_matches += len(matches)
    
    # 按相关性排序
    results.sort(key=lambda x: (x['match_count'], x['keyword_relevance']), reverse=True)
    
    return {
        'query': keywords,
        'total_files_searched': len(files),
        'files_with_matches': len(results),
        'total_matches': total_matches,
        'results': results,
    }


def highlight_keywords(text: str, keywords: List[str]) -> str:
    """高亮关键词（用 ** 包裹）"""
    for kw in keywords:
        pattern = re.compile(f'({re.escape(kw)})', re.IGNORECASE)
        text = pattern.sub(r'**\1**', text)
    return text


def format_results(search_results: Dict[str, Any], show_context: bool = True) -> str:
    """格式化搜索结果"""
    output = []
    
    query = ' '.join(search_results['query'])
    output.append(f'🔍 搜索: "{query}"')
    output.append(f'📁 搜索文件数: {search_results["total_files_searched"]}')
    output.append(f'✅ 匹配文件数: {search_results["files_with_matches"]}')
    output.append(f'📍 总匹配数: {search_results["total_matches"]}')
    output.append('=' * 60)
    
    if not search_results['results']:
        output.append('\n❌ 未找到匹配结果')
        return '\n'.join(output)
    
    for file_result in search_results['results']:
        output.append(f'\n📄 {file_result["filename"]}')
        output.append(f'   路径: {file_result["filepath"]}')
        output.append(f'   匹配数: {file_result["match_count"]}')
        output.append('-' * 40)
        
        for match in file_result['matches']:
            output.append(f'\n   📍 行 {match["line_number"]}: {highlight_keywords(match["line"], search_results["query"])}')
            
            if show_context:
                output.append('   上下文:')
                for ctx_line in match['context'].split('\n'):
                    output.append(f'      {ctx_line}')
    
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='文档搜索器')
    parser.add_argument('--index', '-i', required=True, help='索引文件路径')
    parser.add_argument('--query', '-q', required=True, help='搜索关键词（空格分隔多个）')
    parser.add_argument('--context', '-c', type=int, default=2, help='上下文行数')
    parser.add_argument('--max-matches', '-m', type=int, default=5, help='每个文件最大匹配数')
    parser.add_argument('--no-context', action='store_true', help='不显示上下文')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    # 加载索引
    try:
        index = load_index(args.index)
    except Exception as e:
        print(f'❌ 无法加载索引: {e}')
        return 1
    
    # 解析关键词
    keywords = args.query.split()
    
    if not keywords:
        print('❌ 请提供搜索关键词')
        return 1
    
    # 执行搜索
    results = search_in_index(index, keywords, args.context, args.max_matches)
    
    # 输出结果
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(format_results(results, show_context=not args.no_context))
    
    return 0 if results['total_matches'] > 0 else 1


if __name__ == '__main__':
    exit(main())
