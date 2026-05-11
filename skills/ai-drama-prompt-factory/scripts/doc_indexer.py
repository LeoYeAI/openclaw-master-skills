#!/usr/bin/env python3
"""
doc_indexer.py - 文档索引器
借鉴 Claude Code 读取代码的逻辑：快速扫描文档结构，建立索引

用法：
    python3 doc_indexer.py <文档路径或目录> [--output index.json] [--update]
"""

import argparse
import json
import os
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 支持的文件扩展名及其解析器类型
SUPPORTED_EXTENSIONS = {
    '.md': 'markdown',
    '.txt': 'text',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.jsx': 'javascript',
    '.tsx': 'typescript',
    '.html': 'html',
    '.htm': 'html',
    '.css': 'css',
    '.xml': 'xml',
    '.csv': 'csv',
    '.sql': 'sql',
    '.sh': 'shell',
    '.bash': 'shell',
}

def get_file_hash(filepath: str) -> str:
    """计算文件的 MD5 哈希值"""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def extract_keywords(text: str, max_keywords: int = 20) -> List[str]:
    """从文本中提取关键词"""
    # 移除标点，转小写
    words = re.findall(r'\b[\w\u4e00-\u9fff]+\b', text.lower())
    # 过滤停用词和短词
    stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 
                 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                 'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                 'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
                 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
                 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'up', 'out',
                 'this', 'that', 'these', 'those', 'it', 'its', '的', '是', '在',
                 '了', '和', '与', '或', '但', '如果', '那么', '这', '那'}
    filtered = [w for w in words if w not in stopwords and len(w) > 1]
    # 统计词频
    freq = {}
    for w in filtered:
        freq[w] = freq.get(w, 0) + 1
    # 返回高频词
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:max_keywords]]


class MarkdownParser:
    """Markdown 文档解析器"""
    
    @staticmethod
    def parse(content: str, filepath: str) -> Dict[str, Any]:
        lines = content.split('\n')
        sections = []
        current_section = None
        
        for i, line in enumerate(lines):
            # 检测标题
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                
                if current_section:
                    current_section['end_line'] = i
                    current_section['content_preview'] = '\n'.join(
                        lines[current_section['start_line']:min(current_section['start_line']+5, i)]
                    )
                    sections.append(current_section)
                
                current_section = {
                    'title': title,
                    'level': level,
                    'start_line': i + 1,
                    'end_line': None,
                }
        
        # 处理最后一个章节
        if current_section:
            current_section['end_line'] = len(lines)
            current_section['content_preview'] = '\n'.join(
                lines[current_section['start_line']:min(current_section['start_line']+5, len(lines))]
            )
            sections.append(current_section)
        
        return {
            'type': 'markdown',
            'total_lines': len(lines),
            'sections': sections,
            'keywords': extract_keywords(content),
        }


class PythonParser:
    """Python 代码解析器"""
    
    @staticmethod
    def parse(content: str, filepath: str) -> Dict[str, Any]:
        lines = content.split('\n')
        sections = []
        
        # 匹配类和函数定义
        patterns = [
            (r'^class\s+(\w+)', 'class'),
            (r'^def\s+(\w+)', 'function'),
            (r'^async\s+def\s+(\w+)', 'async_function'),
        ]
        
        for i, line in enumerate(lines):
            for pattern, section_type in patterns:
                match = re.match(pattern, line)
                if match:
                    # 获取文档字符串预览
                    docstring = ''
                    if i + 1 < len(lines):
                        next_lines = lines[i+1:i+6]
                        for nl in next_lines:
                            if '"""' in nl or "'''" in nl:
                                docstring = nl.strip().strip('"""').strip("'''")
                                break
                    
                    sections.append({
                        'title': match.group(1),
                        'type': section_type,
                        'start_line': i + 1,
                        'docstring': docstring,
                    })
        
        return {
            'type': 'python',
            'total_lines': len(lines),
            'sections': sections,
            'keywords': extract_keywords(content),
        }


class JSONParser:
    """JSON 文档解析器"""
    
    @staticmethod
    def parse(content: str, filepath: str) -> Dict[str, Any]:
        try:
            data = json.loads(content)
            return {
                'type': 'json',
                'total_lines': len(content.split('\n')),
                'structure': JSONParser._extract_structure(data),
                'keywords': extract_keywords(content),
            }
        except json.JSONDecodeError:
            return {
                'type': 'json',
                'total_lines': len(content.split('\n')),
                'structure': {'error': 'Invalid JSON'},
                'keywords': [],
            }
    
    @staticmethod
    def _extract_structure(data, depth=0, max_depth=3) -> Dict[str, Any]:
        if depth >= max_depth:
            return {'type': type(data).__name__, 'truncated': True}
        
        if isinstance(data, dict):
            return {
                'type': 'object',
                'keys': list(data.keys())[:20],
                'children': {k: JSONParser._extract_structure(v, depth+1, max_depth) 
                            for k, v in list(data.items())[:10]}
            }
        elif isinstance(data, list):
            return {
                'type': 'array',
                'length': len(data),
                'sample': JSONParser._extract_structure(data[0], depth+1, max_depth) if data else None
            }
        else:
            return {'type': type(data).__name__}


class TextParser:
    """纯文本解析器 - 按段落分割"""
    
    @staticmethod
    def parse(content: str, filepath: str) -> Dict[str, Any]:
        lines = content.split('\n')
        paragraphs = []
        current_para = {'start_line': 1, 'text': ''}
        
        for i, line in enumerate(lines):
            if line.strip() == '':
                if current_para['text'].strip():
                    current_para['end_line'] = i
                    current_para['preview'] = current_para['text'][:200]
                    paragraphs.append(current_para)
                current_para = {'start_line': i + 2, 'text': ''}
            else:
                current_para['text'] += line + '\n'
        
        # 最后一段
        if current_para['text'].strip():
            current_para['end_line'] = len(lines)
            current_para['preview'] = current_para['text'][:200]
            paragraphs.append(current_para)
        
        return {
            'type': 'text',
            'total_lines': len(lines),
            'paragraphs': len(paragraphs),
            'sections': [{'title': f'段落 {i+1}', 'start_line': p['start_line'], 
                         'end_line': p['end_line'], 'preview': p['preview']} 
                        for i, p in enumerate(paragraphs[:50])],
            'keywords': extract_keywords(content),
        }


class HTMLParser:
    """HTML 文档解析器"""
    
    @staticmethod
    def parse(content: str, filepath: str) -> Dict[str, Any]:
        lines = content.split('\n')
        sections = []
        
        # 匹配主要的结构标签
        for i, line in enumerate(lines):
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'section', 'article', 'header', 'footer', 'main', 'nav']:
                pattern = rf'<{tag}[^>]*>([^<]*)</{tag}>'
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    sections.append({
                        'title': match.group(1).strip() or f'<{tag}>',
                        'type': tag,
                        'start_line': i + 1,
                    })
        
        return {
            'type': 'html',
            'total_lines': len(lines),
            'sections': sections,
            'keywords': extract_keywords(re.sub(r'<[^>]+>', '', content)),  # 移除HTML标签后提取关键词
        }


class GenericCodeParser:
    """通用代码解析器"""
    
    @staticmethod
    def parse(content: str, filepath: str) -> Dict[str, Any]:
        lines = content.split('\n')
        sections = []
        
        # 通用函数/类匹配模式
        patterns = [
            (r'^\s*(function|def|async\s+function|async\s+def)\s+(\w+)', 'function'),
            (r'^\s*(class)\s+(\w+)', 'class'),
            (r'^\s*(const|let|var)\s+(\w+)\s*=\s*(async\s+)?\(', 'arrow_function'),
            (r'^\s*export\s+(default\s+)?(function|class|const)\s+(\w+)', 'export'),
        ]
        
        for i, line in enumerate(lines):
            for pattern, section_type in patterns:
                match = re.match(pattern, line)
                if match:
                    name = match.groups()[-1] if match.groups() else 'unknown'
                    sections.append({
                        'title': name,
                        'type': section_type,
                        'start_line': i + 1,
                    })
        
        return {
            'type': 'code',
            'total_lines': len(lines),
            'sections': sections,
            'keywords': extract_keywords(content),
        }


# 解析器映射
PARSERS = {
    'markdown': MarkdownParser,
    'python': PythonParser,
    'json': JSONParser,
    'yaml': JSONParser,  # YAML 也用 JSON 解析器（简化）
    'text': TextParser,
    'html': HTMLParser,
    'javascript': GenericCodeParser,
    'typescript': GenericCodeParser,
    'css': GenericCodeParser,
    'xml': HTMLParser,
    'csv': TextParser,
    'sql': GenericCodeParser,
    'shell': GenericCodeParser,
}


def index_file(filepath: str) -> Optional[Dict[str, Any]]:
    """索引单个文件"""
    path = Path(filepath)
    
    if not path.exists():
        return None
    
    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return {'error': str(e), 'filepath': filepath}
    
    parser_type = SUPPORTED_EXTENSIONS[ext]
    parser = PARSERS.get(parser_type, TextParser)
    
    result = parser.parse(content, filepath)
    result.update({
        'filepath': str(path.absolute()),
        'filename': path.name,
        'extension': ext,
        'size_bytes': path.stat().st_size,
        'modified_time': datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
        'hash': get_file_hash(filepath),
    })
    
    return result


def index_directory(dirpath: str, recursive: bool = True) -> Dict[str, Any]:
    """索引整个目录"""
    path = Path(dirpath)
    
    if not path.exists() or not path.is_dir():
        return {'error': f'目录不存在: {dirpath}'}
    
    files = []
    if recursive:
        for ext in SUPPORTED_EXTENSIONS.keys():
            files.extend(path.rglob(f'*{ext}'))
    else:
        for ext in SUPPORTED_EXTENSIONS.keys():
            files.extend(path.glob(f'*{ext}'))
    
    indexed_files = []
    total_lines = 0
    all_keywords = []
    
    for f in files:
        # 跳过隐藏文件和常见忽略目录
        if any(part.startswith('.') or part in ['node_modules', '__pycache__', 'venv', '.git'] 
               for part in f.parts):
            continue
        
        result = index_file(str(f))
        if result and 'error' not in result:
            indexed_files.append(result)
            total_lines += result.get('total_lines', 0)
            all_keywords.extend(result.get('keywords', []))
    
    # 汇总关键词
    keyword_freq = {}
    for kw in all_keywords:
        keyword_freq[kw] = keyword_freq.get(kw, 0) + 1
    top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:50]
    
    return {
        'type': 'directory',
        'path': str(path.absolute()),
        'total_files': len(indexed_files),
        'total_lines': total_lines,
        'files': indexed_files,
        'top_keywords': [kw for kw, _ in top_keywords],
        'indexed_at': datetime.now().isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description='文档索引器 - 快速扫描文档结构')
    parser.add_argument('path', help='文档路径或目录')
    parser.add_argument('--output', '-o', default='doc_index.json', help='输出索引文件路径')
    parser.add_argument('--update', '-u', action='store_true', help='增量更新现有索引')
    parser.add_argument('--no-recursive', action='store_true', help='不递归扫描子目录')
    
    args = parser.parse_args()
    path = Path(args.path)
    
    if not path.exists():
        print(f'❌ 路径不存在: {args.path}')
        return 1
    
    print(f'📚 正在索引: {args.path}')
    
    if path.is_file():
        result = index_file(str(path))
        if result:
            result = {'type': 'single_file', 'files': [result], 'indexed_at': datetime.now().isoformat()}
    else:
        result = index_directory(str(path), recursive=not args.no_recursive)
    
    if 'error' in result:
        print(f'❌ 索引失败: {result["error"]}')
        return 1
    
    # 保存索引
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    if result['type'] == 'directory':
        print(f'✅ 索引完成!')
        print(f'   📁 文件数: {result["total_files"]}')
        print(f'   📝 总行数: {result["total_lines"]}')
        print(f'   🔑 关键词: {", ".join(result["top_keywords"][:10])}')
    else:
        file_info = result['files'][0]
        print(f'✅ 索引完成!')
        print(f'   📄 文件: {file_info["filename"]}')
        print(f'   📝 行数: {file_info["total_lines"]}')
        if 'sections' in file_info:
            print(f'   📑 章节数: {len(file_info["sections"])}')
    
    print(f'   💾 索引保存至: {output_path}')
    
    return 0


if __name__ == '__main__':
    exit(main())
