#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并同一段落中的重复引用组合

功能：在同一段落中，如果相同的引用编号组合多次出现，
      只保留最后一个出现的引用组合，删除前面重复的。

例如：
  原文：...非人灵长类动物之一[34,37]。某物种体长...15-17 kg[34,36]。
       其毛色较为单调...黑色毛冠[34,36]。
  合并后：...非人灵长类动物之一[34,37]。某物种体长...15-17 kg[34,36]。
       其毛色较为单调...黑色毛冠。

用法：
  python merge_duplicate_citations_in_paragraphs.py <输入文件.md> [输出文件.md]
  
  如果不指定输出文件，默认生成：<原文件名>_merged.md
"""

import re
import sys
from collections import OrderedDict

def find_paragraphs(text):
    """
    将文本分割成段落
    段落以空行分隔
    """
    # 按空行分割段落
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]

def normalize_citation(citation_text):
    """
    标准化引用组合，用于比较
    例如：[34,36] 和 [34,36] 是相同的
          [36,34] 和 [34,36] 也是相同的（排序后比较）
    """
    # 提取所有数字
    numbers = re.findall(r'\d+', citation_text)
    # 排序后组成元组作为唯一标识
    return tuple(sorted(numbers))

def merge_citations_in_paragraph(paragraph):
    """
    在单个段落内合并重复的引用组合
    保留每个引用组合最后一次出现的位置，删除前面的重复
    
    处理场景：
    - 单个引用：[34]
    - 组合引用：[34,36] 或 [34-36] 或 [34,35,36]
    
    示例：
    原文：...kg[34,36]。其毛色...[34,36]。
    结果：...kg[34,36]。其毛色...。
    （保留最后一个[34,36]，删除前面的）
    """
    # 匹配引用标记，包括组合引用 [34,36] 或范围 [34-36]
    citation_pattern = re.compile(r'\[(\d+(?:,\d+)*(?:-\d+)?)\]')
    
    # 找出所有引用及其位置
    citations = list(citation_pattern.finditer(paragraph))
    
    if not citations:
        return paragraph
    
    # 记录每个引用组合最后出现的位置
    last_occurrence = {}
    for i, match in enumerate(citations):
        citation_key = normalize_citation(match.group(1))
        last_occurrence[citation_key] = (match.start(), match.end())
    
    # 确定要删除的引用位置（非最后一次出现的）
    to_remove = []
    for match in citations:
        citation_key = normalize_citation(match.group(1))
        # 如果当前位置不是最后出现的位置，则删除
        if (match.start(), match.end()) != last_occurrence[citation_key]:
            to_remove.append((match.start(), match.end()))
    
    if not to_remove:
        return paragraph  # 没有重复引用
    
    # 从后向前删除，避免位置偏移问题
    result = paragraph
    for start, end in sorted(to_remove, reverse=True):
        result = result[:start] + result[end:]
    
    return result

def process_document(content):
    """
    处理整个文档，合并各段落中的重复引用
    """
    # 分离正文和参考文献部分
    ref_section_match = re.search(r'\n## 参考文献\s*\n', content)
    
    if ref_section_match:
        main_text = content[:ref_section_match.start()]
        ref_section = content[ref_section_match.start():]
    else:
        main_text = content
        ref_section = ""
    
    # 处理正文部分
    # 按段落分割并处理
    paragraphs = find_paragraphs(main_text)
    
    merged_count = 0
    processed_paragraphs = []
    
    for para in paragraphs:
        original_para = para
        processed_para = merge_citations_in_paragraph(para)
        
        if original_para != processed_para:
            # 统计合并的引用数
            original_citations = re.findall(r'\[\d+(?:,\d+)*(?:-\d+)?\]', original_para)
            processed_citations = re.findall(r'\[\d+(?:,\d+)*(?:-\d+)?\]', processed_para)
            merged_count += len(original_citations) - len(processed_citations)
        
        processed_paragraphs.append(processed_para)
    
    # 重新组合正文
    processed_main_text = '\n\n'.join(processed_paragraphs)
    
    # 组合完整文档
    result = processed_main_text + ref_section
    
    return result, merged_count

def main():
    if len(sys.argv) < 2:
        print("用法: python merge_duplicate_citations_in_paragraphs.py <输入文件.md> [输出文件.md]")
        print("\n功能：合并同一段落中的重复引用，只保留最后一次出现")
        print("\n示例：")
        print('  原文：研究显示[34]有显著效果[36]，进一步分析[34]表明...')
        print('  合并后：研究显示[34]有显著效果[36]，进一步分析表明...')
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        # 自动生成输出文件名
        if input_file.endswith('.md'):
            output_file = input_file[:-3] + '_merged.md'
        else:
            output_file = input_file + '_merged.md'
    
    # 读取输入文件
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取文件失败 - {e}")
        sys.exit(1)
    
    print(f"正在处理: {input_file}")
    
    # 处理文档
    result, merged_count = process_document(content)
    
    # 写入输出文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
    except Exception as e:
        print(f"错误: 写入文件失败 - {e}")
        sys.exit(1)
    
    # 输出结果
    print(f"\n处理完成!")
    print(f"  输出文件: {output_file}")
    print(f"  合并重复引用: {merged_count} 处")
    
    if merged_count > 0:
        print(f"\n✓ 已删除同一段落中的重复引用，保留最后一次出现")
    else:
        print(f"\n✓ 未发现需要合并的重复引用")

if __name__ == '__main__':
    main()
