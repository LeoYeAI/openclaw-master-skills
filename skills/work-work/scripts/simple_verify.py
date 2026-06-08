# -*- coding: utf-8 -*-
"""
简化的验证脚本 - 只检查最关键的问题
用法: python simple_verify.py <your_review.md>
"""

import re
import sys
from collections import Counter

if len(sys.argv) < 2:
    print("用法: python simple_verify.py <your_review.md>")
    sys.exit(1)

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 80)
print("综述验证报告(简化版)")
print("=" * 80)

# 分离正文和参考文献
ref_start = content.find('\n\n## 参考文献')
main_text = content[:ref_start]
refs_text = content[ref_start + len('\n\n## 参考文献'):]

# 1. 检查正文中的引用
print("\n[1] 正文引用检查")
citations = re.findall(r'\[(\d+)\]', main_text)
citation_nums = [int(c) for c in citations]

if citation_nums:
    print(f"正文引用总数: {len(citation_nums)}")
    print(f"引用编号范围: {min(citation_nums)} - {max(citation_nums)}")

    # 超范围引用
    invalid = [n for n in citation_nums if n > 94]
    if invalid:
        print(f"警告: 发现超范围引用 {len(set(invalid))} 个: {sorted(set(invalid))}")
    else:
        print("OK: 所有引用编号都在范围内")

    # 未引用的文献
    all_cited = set(citation_nums)
    unused = [i for i in range(1, 95) if i not in all_cited]
    if unused:
        print(f"未引用的文献: {len(unused)} 篇")
    else:
        print("OK: 所有文献都有被引用")

# 2. 检查参考文献列表
print("\n[2] 参考文献列表检查")

# 更精确地提取参考文献
ref_lines = refs_text.strip().split('\n')
valid_refs = []
for line in ref_lines:
    if line.strip() and line.strip().startswith('['):
        valid_refs.append(line.strip())

print(f"参考文献数量: {len(valid_refs)}")

# 提取编号
ref_nums = []
for ref in valid_refs:
    match = re.match(r'\[(\d+)\]', ref)
    if match:
        ref_nums.append(int(match.group(1)))

if ref_nums:
    print(f"参考文献编号范围: {min(ref_nums)} - {max(ref_nums)}")

    # 检查是否连续
    if len(set(ref_nums)) == len(ref_nums) and max(ref_nums) - min(ref_nums) + 1 == len(ref_nums):
        print("OK: 参考文献编号连续且无重复")
    else:
        if len(set(ref_nums)) != len(ref_nums):
            print("警告: 参考文献编号有重复")
        else:
            print("警告: 参考文献编号不连续")

# 3. 检查章节结构
print("\n[3] 章节结构检查")
h1 = re.findall(r'^# (.+)$', content, re.MULTILINE)
h2 = re.findall(r'^## (.+)$', content, re.MULTILINE)

print(f"一级标题: {len(h1)} 个")
print(f"二级标题: {len(h2)} 个")

# 检查编号章节
numbered = re.findall(r'^## (一|二|三|四|五|六|七|八)、', content, re.MULTILINE)
print(f"编号章节: {len(numbered)} 个")

print("\n" + "=" * 80)
print("验证完成")
print("=" * 80)
