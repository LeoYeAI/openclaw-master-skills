# -*- coding: utf-8 -*-
"""
筛选参考文献,删除指定的普通期刊
用法: python filter_references.py <your_review.md>
"""

import re
import sys
import os

if len(sys.argv) < 2:
    print("用法: python filter_references.py <your_review.md>")
    sys.exit(1)

input_file = sys.argv[1]

# 读取markdown文件
with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 需要删除的期刊
journals_to_remove = [
    '森林与人类',
    '中南林业调查规划',
    '河南林业',
    '云南林业'
]

# 提取所有参考文献
ref_pattern = r'\[(\d+)\]\s+(.*?)(?=\n\[|\n\n|$)'
matches = re.findall(ref_pattern, content, re.DOTALL)

# 存储保留的参考文献和旧编号映射
kept_refs = []
old_to_new_mapping = {}

for num, ref_text in matches:
    num = int(num)
    ref_text = ref_text.strip()

    # 检查是否包含需要删除的期刊
    should_remove = False
    for journal in journals_to_remove:
        if journal in ref_text:
            print(f"删除 [{num}]: 包含期刊 '{journal}'")
            try:
                print(f"    内容: {ref_text[:80]}...")
            except UnicodeEncodeError:
                print(f"    内容: (包含特殊字符)")
            should_remove = True
            break

    if not should_remove:
        print(f"保留 [{num}]")
        kept_refs.append((num, ref_text))

# 生成旧编号到新编号的映射
new_num = 1
for old_num, ref_text in kept_refs:
    old_to_new_mapping[old_num] = new_num
    new_num += 1

print(f"\n保留 {len(kept_refs)} 篇文献")
print(f"删除 {len(matches) - len(kept_refs)} 篇文献")

# 更新正文中的引用编号
print("\n更新正文中的引用编号...")

# 找到正文部分(参考文献之前)
ref_section_start = content.find('\n\n## 参考文献')
if ref_section_start == -1:
    ref_section_start = content.find('\n\n### 参考文献')
    if ref_section_start == -1:
        ref_section_start = len(content)

main_text = content[:ref_section_start]

# 替换引用编号 [数字] 为新编号
def replace_reference(match):
    old_num = int(match.group(1))
    if old_num in old_to_new_mapping:
        return f"[{old_to_new_mapping[old_num]}]"
    return match.group(0)

new_main_text = re.sub(r'\[(\d+)\]', replace_reference, main_text)

# 统计替换次数
replacement_count = 0
for old_num in old_to_new_mapping:
    count = main_text.count(f"[{old_num}]")
    if count > 0:
        replacement_count += count
        print(f"  [{old_num}] -> [{old_to_new_mapping[old_num]}] (出现{count}次)")

print(f"\n共替换了 {replacement_count} 处引用编号")

# 生成新的参考文献部分
print("\n生成新的参考文献列表...")
new_refs_section = "\n\n## 参考文献\n\n"
for old_num, ref_text in kept_refs:
    new_num = old_to_new_mapping[old_num]
    new_refs_section += f"[{new_num}] {ref_text}\n"

# 组合新内容
new_content = new_main_text + new_refs_section

base_name = os.path.splitext(input_file)[0]
output_filtered = f'{base_name}_筛选后.md'

# 写入新文件
with open(output_filtered, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("\n[完成]!")
print(f"新文件: {output_filtered}")
print(f"参考文献数量: {len(kept_refs)} 篇")
