#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
步骤验证工具（增强版）

功能：
1. 验证录制脚本中的步骤是否全部转换到测试用例中
2. 检查相邻步骤是否使用了相同的元素
3. 检查特殊逻辑（三层判断）是否保留
4. 检查页面跳转是否都有等待
"""

import re
import argparse
from pathlib import Path


def extract_steps_from_recording(script_path):
    """从录制脚本提取步骤"""
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取所有 step 标记
    step_pattern = r'mark_step_start\("step_(\d+)"\)'
    steps = re.findall(step_pattern, content)
    
    return sorted(set(steps), key=int)


def extract_steps_from_test(test_path):
    """从测试用例提取步骤注释"""
    with open(test_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取所有 step 注释
    step_pattern = r'step_(\d+)'
    steps = re.findall(step_pattern, content)
    
    return sorted(set(steps), key=int)


def check_adjacent_steps(test_path):
    """检查相邻步骤是否使用了相同的元素"""
    with open(test_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取所有的 tap() 调用
    tap_pattern = r'self\.tap\(self\.(\w+)\)'
    taps = re.findall(tap_pattern, content)
    
    warnings = []
    for i in range(len(taps) - 1):
        if taps[i] == taps[i + 1]:
            warnings.append(f"⚠️ 相邻的 tap() 使用了相同的元素：{taps[i]}")
    
    return warnings


def check_special_logic(recording_path, test_path):
    """检查特殊逻辑是否保留"""
    with open(recording_path, 'r', encoding='utf-8') as f:
        recording_content = f.read()
    
    with open(test_path, 'r', encoding='utf-8') as f:
        test_content = f.read()
    
    issues = []
    
    # 检查三层判断
    if recording_content.count('element_is_exists') > 10:  # 录制脚本有三层判断
        if test_content.count('element_is_exists') < 5:  # 测试用例中太少
            issues.append("⚠️ 录制脚本有三层判断，但测试用例中可能简化了")
    
    # 检查 else 判断
    recording_else_count = recording_content.count('else:')
    test_else_count = test_content.count('else:')
    if recording_else_count > 5 and test_else_count < recording_else_count / 2:
        issues.append(f"⚠️ 录制脚本有{recording_else_count}个 else 判断，但测试用例中只有{test_else_count}个")
    
    return issues


def check_page_wait(test_path):
    """检查页面跳转是否都有等待"""
    with open(test_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # 检查是否有 wait_for_page_success 调用
    if 'wait_for_page_success' not in content:
        issues.append("⚠️ 测试用例中没有使用 wait_for_page_success() 方法")
    
    # 检查页面跳转后是否有等待（简单检查）
    # 这个需要更复杂的逻辑，暂时简化
    
    return issues


def validate(recording_path, test_path):
    """验证步骤完整性"""
    recording_steps = extract_steps_from_recording(recording_path)
    test_steps = extract_steps_from_test(test_path)
    
    print(f"\n{'='*60}")
    print(f"步骤验证报告")
    print(f"{'='*60}\n")
    
    print(f"录制脚本：{recording_path}")
    print(f"测试用例：{test_path}\n")
    
    print(f"录制脚本步骤数：{len(recording_steps)}")
    print(f"测试用例步骤数：{len(test_steps)}\n")
    
    # 1. 检查步骤完整性
    missing_steps = set(recording_steps) - set(test_steps)
    
    if missing_steps:
        print(f"❌ 缺失的步骤：{sorted(missing_steps, key=int)}")
        print(f"\n缺失步骤详情:")
        for step in sorted(missing_steps, key=int):
            print(f"  - step_{step}")
        success = False
    else:
        print(f"✅ 所有步骤都已转换（{len(recording_steps)} 步，一个不漏）")
        success = True
    
    print(f"\n{'='*60}")
    print(f"详细检查")
    print(f"{'='*60}\n")
    
    # 2. 检查相邻步骤
    print(f"2. 相邻步骤检查:")
    adjacent_warnings = check_adjacent_steps(test_path)
    if adjacent_warnings:
        for warning in adjacent_warnings:
            print(f"  {warning}")
    else:
        print(f"  ✅ 相邻步骤元素检查通过")
    
    # 3. 检查特殊逻辑
    print(f"\n3. 特殊逻辑检查:")
    special_issues = check_special_logic(recording_path, test_path)
    if special_issues:
        for issue in special_issues:
            print(f"  {issue}")
    else:
        print(f"  ✅ 特殊逻辑检查通过")
    
    # 4. 检查页面跳转等待
    print(f"\n4. 页面跳转等待检查:")
    wait_issues = check_page_wait(test_path)
    if wait_issues:
        for issue in wait_issues:
            print(f"  {issue}")
    else:
        print(f"  ✅ 页面跳转等待检查通过")
    
    # 总结
    print(f"\n{'='*60}")
    print(f"验证总结")
    print(f"{'='*60}\n")
    
    all_issues = missing_steps or adjacent_warnings or special_issues or wait_issues
    if all_issues:
        print(f"❌ 验证失败，发现 {len(all_issues)} 个问题")
        return False
    else:
        print(f"✅ 验证通过，所有检查项都符合要求")
        return True


def main():
    parser = argparse.ArgumentParser(description='步骤验证工具（增强版）')
    parser.add_argument('--input', required=True, help='录制脚本路径')
    parser.add_argument('--test', required=True, help='测试用例路径')
    parser.add_argument('--report', help='生成验证报告路径')
    
    args = parser.parse_args()
    
    success = validate(args.input, args.test)
    
    if args.report:
        # 生成报告
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(f"验证结果：{'通过' if success else '失败'}\n")
            f.write(f"录制脚本步骤数：{len(extract_steps_from_recording(args.input))}\n")
            f.write(f"测试用例步骤数：{len(extract_steps_from_test(args.test))}\n")
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(0 if main() else 1)
