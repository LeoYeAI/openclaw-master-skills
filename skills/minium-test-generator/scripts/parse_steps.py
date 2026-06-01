#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
录制脚本解析器

功能：解析 Minium 录制脚本，提取步骤信息，生成步骤清单和对照表模板
"""

import re
import argparse
from pathlib import Path
from datetime import datetime


def parse_steps(script_path):
    """解析录制脚本，提取步骤信息"""
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取所有步骤标记
    step_pattern = r'self\.mark_step_start\("step_(\d+)"\)'
    step_matches = list(re.finditer(step_pattern, content))
    
    steps = []
    for i, match in enumerate(step_matches):
        step_num = match.group(1)
        start_pos = match.end()
        
        # 获取下一个步骤的开始位置
        if i + 1 < len(step_matches):
            end_pos = step_matches[i + 1].start()
        else:
            end_pos = len(content)
        
        # 提取步骤代码
        step_code = content[start_pos:end_pos].strip()
        
        # 分析步骤类型
        step_type = analyze_step_type(step_code)
        
        # 提取 XPath（如果有）
        xpaths = extract_xpaths(step_code)
        
        steps.append({
            'step_num': step_num,
            'step_type': step_type,
            'xpaths': xpaths,
            'code': step_code[:200]  # 只保留前 200 字符
        })
    
    return steps


def analyze_step_type(step_code):
    """分析步骤类型"""
    
    # 检查是否有三层判断
    if 'element_is_exists' in step_code and step_code.count('if') >= 2:
        return '⚠️ 三层判断'
    
    # 检查是否有 else 判断
    if 'element_is_exists' in step_code and 'else' in step_code:
        return '⚠️ else 判断'
    
    # 检查是否是滚动
    if 'scroll_to' in step_code:
        return '🔄 滚动'
    
    # 检查是否是输入
    if 'element.input' in step_code:
        return '📝 输入'
    
    # 检查是否是页面跳转验证
    if 'wait_for_page' in step_code:
        return '🔗 页面跳转'
    
    # 默认
    return '✅ 普通'


def extract_xpaths(step_code):
    """提取步骤中的所有 XPath"""
    
    xpaths = []
    
    # 提取 get_element_by_xpath 的参数
    xpath_pattern = r'get_element_by_xpath\("""(.*?)"""'
    matches = re.findall(xpath_pattern, step_code)
    xpaths.extend(matches)
    
    # 提取 element_is_exists 的 xpath 参数
    exists_xpath_pattern = r'element_is_exists\(xpath="""(.*?)"""'
    matches = re.findall(exists_xpath_pattern, step_code)
    xpaths.extend(matches)
    
    return xpaths


def generate_checklist(steps, output_path):
    """生成步骤对照表模板"""
    
    checklist = f"""# 步骤对照表

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**录制脚本**: {Path(output_path).parent.name}
**总步骤数**: {len(steps)}

---

## 📊 步骤统计

| 类型 | 数量 |
|------|------|
| 普通步骤 | {sum(1 for s in steps if s['step_type'] == '✅ 普通')} |
| ⚠️ 特殊逻辑步骤 | {sum(1 for s in steps if '⚠️' in s['step_type'])} |
| 🔄 循环步骤 | {sum(1 for s in steps if '🔄' in s['step_type'])} |

---

## 📋 步骤清单

"""
    
    # 普通步骤
    normal_steps = [s for s in steps if s['step_type'] == '✅ 普通']
    if normal_steps:
        checklist += "### 普通步骤\n\n"
        for step in normal_steps:
            checklist += f"- step_{step['step_num']}: [待补充说明]\n"
        checklist += "\n"
    
    # 特殊逻辑步骤
    special_steps = [s for s in steps if '⚠️' in s['step_type']]
    if special_steps:
        checklist += "### ⚠️ 特殊逻辑步骤\n\n"
        for step in special_steps:
            xpath_count = len(step['xpaths'])
            checklist += f"- step_{step['step_num']}: {step['step_type']} 【XPath 数量：{xpath_count}】\n"
            if xpath_count > 1:
                checklist += f"  - 注意：该步骤有多个 XPath，需要逐个对照\n"
        checklist += "\n"
    
    # 循环步骤
    loop_steps = [s for s in steps if '🔄' in s['step_type']]
    if loop_steps:
        checklist += "### 🔄 循环步骤\n\n"
        # 分组连续的滚动步骤
        groups = []
        current_group = []
        for step in loop_steps:
            if not current_group or int(step['step_num']) == int(current_group[-1]['step_num']) + 1:
                current_group.append(step)
            else:
                groups.append(current_group)
                current_group = [step]
        if current_group:
            groups.append(current_group)
        
        for i, group in enumerate(groups):
            start = group[0]['step_num']
            end = group[-1]['step_num']
            count = len(group)
            checklist += f"- step_{start}-{end}: 滚动页面 ({count}次)\n"
        checklist += "\n"
    
    # 步骤对照表
    checklist += """## 📝 步骤对照表

| 步骤 | 录制脚本 XPath | 测试用例方法 | 元素是否相同 | 特殊逻辑 | 验证 |
|------|--------------|------------|------------|---------|------|
"""
    
    for step in steps:
        xpath_str = ', '.join(step['xpaths'][:2])  # 只显示前 2 个 XPath
        if len(step['xpaths']) > 2:
            xpath_str += f'... (共{len(step["xpaths"])})'
        
        checklist += f"| step_{step['step_num']} | `{xpath_str}` | `待填写` | - | {step['step_type']} | ☐ |\n"
    
    # 相邻步骤检查
    checklist += """
## 🔍 相邻步骤检查

**规则**: 如果连续步骤在同一个方法中，必须验证元素 XPath 是否不同

"""
    
    for i in range(len(steps) - 1):
        step1 = steps[i]
        step2 = steps[i + 1]
        checklist += f"- [ ] step_{step1['step_num']} 和 step_{step2['step_num']} 的元素 XPath 是否不同？ → 待验证 ☐\n"
    
    # 页面跳转检查
    jump_steps = [s for s in steps if '🔗' in s['step_type']]
    if jump_steps:
        checklist += """
## 🔗 页面跳转检查

**规则**: 每个页面跳转后都必须添加 `wait_for_page_success()`

"""
        for step in jump_steps:
            checklist += f"- [ ] step_{step['step_num']} 跳转后是否添加了等待？ → 待验证 ☐\n"
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(checklist)
    
    print(f"[OK] 步骤对照表已生成：{output_path}")


def main():
    parser = argparse.ArgumentParser(description='录制脚本解析器')
    parser.add_argument('--input', required=True, help='录制脚本路径')
    parser.add_argument('--output', required=True, help='步骤对照表输出路径')
    
    args = parser.parse_args()
    
    print(f"[INFO] 解析录制脚本：{args.input}")
    steps = parse_steps(args.input)
    print(f"[INFO] 共解析 {len(steps)} 个步骤")
    
    print(f"[INFO] 生成步骤对照表：{args.output}")
    generate_checklist(steps, args.output)
    
    print(f"\n[OK] 解析完成！")
    print(f"[INFO] 普通步骤：{sum(1 for s in steps if s['step_type'] == '✅ 普通')}")
    print(f"[INFO] 特殊逻辑步骤：{sum(1 for s in steps if '⚠️' in s['step_type'])}")
    print(f"[INFO] 循环步骤：{sum(1 for s in steps if '🔄' in s['step_type'])}")


if __name__ == '__main__':
    main()
