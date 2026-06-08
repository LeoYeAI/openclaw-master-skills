# -*- coding: utf-8 -*-
"""
完整修复参考文献问题 - 使用最严谨的方法
用法: python extract_and_fix_references.py <your_review.md>
"""

import re
import sys
import os

if len(sys.argv) < 2:
    print("用法: python extract_and_fix_references.py <your_review.md>")
    sys.exit(1)

input_file = sys.argv[1]

# 读取原始文件
with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 需要删除的普通期刊
journals_to_remove = [
    '森林与人类',
    '中南林业调查规划',
    '河南林业',
    '云南林业'
]

# 分离正文和参考文献
ref_start = content.find('\n\n## 参考文献')
if ref_start == -1:
    ref_start = content.find('\n\n### 参考文献')

main_text = content[:ref_start]
refs_text = content[ref_start + len('\n\n## 参考文献'):]

# 提取参考文献,保留完整内容
ref_lines = refs_text.strip().split('\n')
refs = []
for line in ref_lines:
    if line.strip():
        match = re.match(r'\[(\d+)\]\s+(.*)', line.strip())
        if match:
            num = int(match.group(1))
            text = match.group(2).strip()
            refs.append((num, text))

print(f"提取到参考文献: {len(refs)} 条")

# 标记需要删除的文献
deleted_indices = set()
for i, (num, text) in enumerate(refs):
    for journal in journals_to_remove:
        if journal in text:
            deleted_indices.add(i)
            print(f"标记删除 [{num}]: {text[:60]}...")
            break

# 保留的文献
kept_refs = [(num, text) for i, (num, text) in enumerate(refs) if i not in deleted_indices]
print(f"\n保留文献: {len(kept_refs)} 条")

# 重新编号
new_num_mapping = {}  # 旧编号 -> 新编号列表(因为同一旧编号可能对应多条文献)
refs_by_old_num = {}
for i, (old_num, text) in enumerate(kept_refs):
    if old_num not in refs_by_old_num:
        refs_by_old_num[old_num] = []
    refs_by_old_num[old_num].append((i, text))

# 为每条保留的文献分配新编号
final_refs = []  # (新编号, 文本)
old_to_new = {}  # 旧编号 -> 新编号(取第一条)

new_num = 1
for old_num in sorted(refs_by_old_num.keys()):
    refs_for_old_num = refs_by_old_num[old_num]
    for idx, text in refs_for_old_num:
        final_refs.append((new_num, text))
        if old_num not in old_to_new:
            old_to_new[old_num] = new_num
        new_num += 1

print(f"新编号范围: 1 - {new_num - 1}")

# 替换正文中的引用
def replace_citation(match):
    old_num = int(match.group(1))

    # 删除[99]和[107]
    if old_num in [99, 107]:
        print(f"删除无效引用 [{old_num}]")
        return ''

    # 查找新编号
    if old_num in old_to_new:
        return f"[{old_to_new[old_num]}]"

    # 如果找不到,保持原样
    return match.group(0)

new_main_text = re.sub(r'\[(\d+)\]', replace_citation, main_text)

# 生成新的参考文献部分
new_refs_section = "\n\n## 参考文献\n\n"
for new_num, text in final_refs:
    new_refs_section += f"[{new_num}] {text}\n\n"

# 组合
final_content = new_main_text + new_refs_section

# 保存
base_name = os.path.splitext(input_file)[0]
output_file = f'{base_name}_最终修复.md'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(final_content)

print(f"\n完成! 输出文件: {output_file}")
