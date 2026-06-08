#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查文档中的同一段落重复引用问题

功能：扫描整个文档，找出同一段落中重复出现的引用组合

用法：
  python check_duplicate_citations.py <输入文件.md>
"""

import re
import sys

def normalize_citation(citation_text):
    """标准化引用组合，用于比较"""
    numbers = re.findall(r'\d+', citation_text)
    return tuple(sorted(numbers))

def find_paragraphs(text):
    """将文本分割成段落"""
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]

def check_paragraph(paragraph, para_index):
    """检查单个段落中的重复引用"""
    citation_pattern = re.compile(r'\[(\d+(?:,\d+)*(?:-\d+)?)\]')
    citations = list(citation_pattern.finditer(paragraph))
    
    if not citations:
        return []
    
    # 统计每个引用组合出现的次数和位置
    citation_stats = {}
    for match in citations:
        citation_key = normalize_citation(match.group(1))
        original_text = match.group(0)
        
        if citation_key not in citation_stats:
            citation_stats[citation_key] = {
                'count': 0,
                'original': original_text,
                'positions': []
            }
        citation_stats[citation_key]['count'] += 1
        citation_stats[citation_key]['positions'].append((match.start(), match.end()))
    
    # 找出重复的引用
    duplicates = []
    for key, stats in citation_stats.items():
        if stats['count'] > 1:
            duplicates.append({
                'citation': stats['original'],
                'count': stats['count'],
                'positions': stats['positions']
            })
    
    return duplicates

def main():
    if len(sys.argv) < 2:
        print("用法: python check_duplicate_citations.py <输入文件.md>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取文件失败 - {e}")
        sys.exit(1)
    
    print(f"正在检查: {input_file}")
    print("=" * 60)
    
    # 分离正文和参考文献部分
    ref_section_match = re.search(r'\n## 参考文献\s*\n', content)
    if ref_section_match:
        main_text = content[:ref_section_match.start()]
    else:
        main_text = content
    
    # 按段落分割
    paragraphs = find_paragraphs(main_text)
    
    # 检查每个段落
    total_duplicates = 0
    paragraphs_with_duplicates = 0
    
    for i, para in enumerate(paragraphs):
        duplicates = check_paragraph(para, i)
        
        if duplicates:
            paragraphs_with_duplicates += 1
            total_duplicates += len(duplicates)
            
            print(f"\n[段落 {i+1}] 发现重复引用:")
            # 显示段落前100字符作为上下文
            context = para[:100].replace('\n', ' ')
            if len(para) > 100:
                context += "..."
            print(f"   上下文: {context}")
            
            for dup in duplicates:
                print(f"   - 引用 {dup['citation']} 出现 {dup['count']} 次")
                # 提取每个位置的上下文
                for start, end in dup['positions']:
                    # 获取引用前后的文本
                    before = para[max(0, start-30):start]
                    after = para[end:min(len(para), end+30)]
                    print(f"      位置: ...{before}{dup['citation']}{after}...")
    
    print("\n" + "=" * 60)
    print("[检查统计]")
    print(f"   总段落数: {len(paragraphs)}")
    print(f"   有重复引用的段落: {paragraphs_with_duplicates}")
    print(f"   重复引用组合数: {total_duplicates}")
    
    if total_duplicates == 0:
        print("\n[OK] 未发现同一段落中的重复引用问题！")
    else:
        print(f"\n[WARNING] 发现 {total_duplicates} 处重复引用需要处理")
        print("   建议运行: python merge_duplicate_citations_in_paragraphs.py")

if __name__ == '__main__':
    main()
