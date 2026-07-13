#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整工作流 - 铅笔供应商联系

用法:
    python pencil_workflow.py
    
步骤:
    1. 启动Chrome
    2. 搜索"铅笔"供应商
    3. 联系第一家
    4. 验证每一步
"""

import subprocess
import sys
import time
import json

def run_step(script_name, args=None, description=""):
    """运行脚本步骤并验证"""
    print(f"\n{'='*60}")
    print(f"步骤: {description}")
    print(f"脚本: {script_name}")
    print('='*60)
    
    cmd = ['python', script_name]
    if args:
        cmd.extend(args)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(f"错误: {result.stderr}")
    
    return result.returncode == 0

def verify_step(step_name, expected_text=None):
    """验证步骤"""
    print(f"\n验证: {step_name}")
    
    cmd = ['python', 'verify_step.py', '--step', step_name]
    if expected_text:
        cmd.extend(['--text', expected_text])
    cmd.append('--double')  # 失败时自动Double Check
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    
    return result.returncode == 0

def main():
    print("="*60)
    print("小翰系统 - 铅笔供应商联系工作流")
    print("="*60)
    
    # Step 1: 启动Chrome
    if not run_step('chrome_launch.py', description="启动Chrome"):
        print("工作流失败: Chrome启动失败")
        return 1
    
    # 验证Chrome启动
    if not verify_step('chrome_start', 'Chrome'):
        print("工作流失败: Chrome验证失败")
        return 1
    
    # Step 2: 搜索供应商
    if not run_step('search_1688.py', ['--keyword', '铅笔', '--num', '5', '--output', 'pencil_suppliers.json'], 
                    description="搜索铅笔供应商"):
        print("工作流失败: 搜索失败")
        return 1
    
    # 验证搜索结果
    if not verify_step('search_results', '铅笔'):
        print("工作流失败: 搜索结果验证失败")
        return 1
    
    # Step 3: 联系第一家供应商
    # 读取供应商列表
    try:
        with open('pencil_suppliers.json', 'r', encoding='utf-8') as f:
            suppliers = json.load(f)
        
        if not suppliers:
            print("错误: 未找到供应商")
            return 1
        
        first_supplier = suppliers[0]
        print(f"\n联系第一家供应商: {first_supplier['name']}")
        
        # 发送消息
        if not run_step('1688_send_message.py', 
                       ['--offer', first_supplier['link'], '需要铅笔，请报价'],
                       description="发送询价消息"):
            print("工作流失败: 消息发送失败")
            return 1
        
        # 验证消息发送
        if not verify_step('message_sent', '报价'):
            print("工作流失败: 消息验证失败")
            return 1
        
        # 记录
        print(f"\n记录:")
        print(f"  供应商: {first_supplier['name']}")
        print(f"  链接: {first_supplier['link']}")
        print(f"  时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  内容: 需要铅笔，请报价")
        
    except Exception as e:
        print(f"读取供应商列表失败: {e}")
        return 1
    
    print("\n" + "="*60)
    print("工作流完成: 第一家供应商已联系，等待回复")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())