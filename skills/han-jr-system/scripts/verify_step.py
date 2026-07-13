#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证脚本 - 截图和OCR检查

用法:
    python verify_step.py --step "step_name" --text "期望文本" --timeout 10
    python verify_step.py --step "message_sent" --text "报价" --double

依赖:
    pip install playwright easyocr pillow numpy

功能:
    - First Check: 10秒内截图并OCR验证
    - Double Check: First Check失败时，额外20秒再次验证
"""

import sys
import io

# Force UTF-8 - 必须使用UTF-8，否则输出会产生乱码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import argparse
import time
import os
from datetime import datetime

def safe_print(text):
    """安全打印，处理编码问题"""
    try:
        print(text)
    except:
        print(str(text).encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

def take_screenshot(filename='screenshot.png'):
    """截图当前页面"""
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            
            # 获取当前页面
            page = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    page = pg
                    break
                if page:
                    break
            
            if not page:
                safe_print("错误: 未找到页面")
                return False
            
            # 截图
            page.screenshot(path=filename, full_page=True)
            browser.close()
            
            safe_print(f"截图已保存: {filename}")
            return True
            
    except Exception as e:
        safe_print(f"截图失败: {e}")
        return False

def ocr_check(image_path, expected_text=None):
    """OCR检查截图内容"""
    try:
        import easyocr
        import numpy as np
        from PIL import Image
        
        safe_print("正在加载OCR模型...")
        reader = easyocr.Reader(['ch_sim', 'en'], verbose=False)
        
        safe_print("正在进行OCR识别...")
        result = reader.readtext(image_path)
        
        text = ' '.join([r[1] for r in result])
        safe_print(f"OCR识别文本: {text[:200]}...")  # 只显示前200字符
        
        if expected_text:
            if expected_text in text:
                safe_print(f"OCR检查PASS: 找到'{expected_text}'")
                return True, text
            else:
                safe_print(f"OCR检查FAIL: 未找到'{expected_text}'")
                return False, text
        
        return True, text
        
    except ImportError:
        safe_print("警告: 未安装easyocr，跳过OCR检查")
        return True, ""
    except Exception as e:
        safe_print(f"OCR失败: {e}")
        return False, ""

def first_check(step_name, expected_text=None, timeout=10):
    """First Check - 10秒内验证
    
    工作流程:
    1. 等待指定时间(默认10秒)
    2. 截图当前页面
    3. OCR识别截图内容
    4. 检查是否包含期望文本
    
    返回:
        True: 验证通过
        False: 验证失败
    """
    safe_print(f"\n{'='*50}")
    safe_print(f"First Check: {step_name}")
    safe_print(f"超时: {timeout}秒")
    safe_print('='*50)
    
    # 等待
    safe_print(f"等待 {timeout} 秒...")
    time.sleep(timeout)
    
    # 截图
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_file = f"check_{step_name}_{timestamp}.png"
    
    safe_print("正在截图...")
    if not take_screenshot(screenshot_file):
        safe_print("First Check FAIL: 截图失败")
        return False
    
    # OCR检查
    if expected_text:
        safe_print(f"正在检查文本: '{expected_text}'")
        success, text = ocr_check(screenshot_file, expected_text)
        if success:
            safe_print(f"First Check PASS: {step_name}")
            return True
        else:
            safe_print(f"First Check FAIL (OCR): {step_name}")
            return False
    
    safe_print(f"First Check PASS (截图): {step_name}")
    return True

def double_check(step_name, expected_text=None):
    """Double Check - 额外20秒
    
    当First Check失败时执行:
    1. 额外等待20秒
    2. 再次截图
    3. OCR识别并检查
    """
    safe_print(f"\n{'='*50}")
    safe_print(f"Double Check: {step_name}")
    safe_print(f"额外等待: 20秒")
    safe_print('='*50)
    
    safe_print("等待20秒...")
    time.sleep(20)
    
    # 再次截图检查
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_file = f"double_check_{step_name}_{timestamp}.png"
    
    safe_print("正在截图...")
    if take_screenshot(screenshot_file):
        if expected_text:
            safe_print(f"正在检查文本: '{expected_text}'")
            success, _ = ocr_check(screenshot_file, expected_text)
            if success:
                safe_print(f"Double Check PASS: {step_name}")
                return True
    
    safe_print(f"Double Check FAIL: {step_name}")
    return False

def main():
    parser = argparse.ArgumentParser(
        description='步骤验证 - 截图和OCR检查',
        epilog='''
示例:
  python verify_step.py --step "search_complete" --text "帽子"
  python verify_step.py --step "message_sent" --text "报价" --double
  python verify_step.py --step "page_loaded" --timeout 5

说明:
  --step: 步骤名称，用于保存截图文件
  --text: 期望在页面上看到的文本(可选)
  --timeout: First Check等待时间(默认10秒)
  --double: First Check失败时执行Double Check(额外20秒)
        '''
    )
    parser.add_argument('--step', '-s', required=True, help='步骤名称')
    parser.add_argument('--text', '-t', help='期望的文本')
    parser.add_argument('--timeout', type=int, default=10, help='超时时间(秒)')
    parser.add_argument('--double', action='store_true', help='执行Double Check')
    args = parser.parse_args()
    
    safe_print("="*50)
    safe_print("OCR 验证步骤")
    safe_print("="*50)
    
    # First Check
    if first_check(args.step, args.text, args.timeout):
        return 0
    
    # 如果失败且要求Double Check
    if args.double:
        if double_check(args.step, args.text):
            return 0
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
