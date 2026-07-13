#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证小翰系统各项功能
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from playwright.sync_api import sync_playwright
import json
import os

def check_chrome_connection():
    """验证 Chrome CDP 连接"""
    print('='*50)
    print('1. 验证 Chrome CDP 连接')
    print('='*50)
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp('http://localhost:9222')
            print('✓ Chrome CDP connection successful')
            print(f'  Contexts: {len(browser.contexts)}')
            pages = 0
            for ctx in browser.contexts:
                pages += len(ctx.pages)
            print(f'  Total pages: {pages}')
            browser.close()
            return True
    except Exception as e:
        print(f'✗ Error: {e}')
        return False

def check_current_page():
    """验证当前页面状态"""
    print()
    print('='*50)
    print('2. 验证当前页面状态')
    print('='*50)
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp('http://localhost:9222')
            page = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    page = pg
                    break
                if page:
                    break
            
            if page:
                print(f'URL: {page.url[:80]}')
                print(f'Title: {page.title()}')
                
                # 检查是否有搜索框
                search_box = page.query_selector('input[name="keywords"]')
                if search_box:
                    print('✓ 搜索框: 存在')
                else:
                    print('✗ 搜索框: 不存在')
                
                # 检查是否有滑块验证码
                slider = page.query_selector('#nc_1_n1z')
                if slider:
                    print('⚠ 滑块验证码: 存在')
                else:
                    print('✓ 滑块验证码: 不存在')
                
                # 检查是否有产品
                price_elems = page.query_selector_all('[class*="price"]')
                if len(price_elems) > 0:
                    print(f'✓ 产品价格元素: {len(price_elems)} 个')
                else:
                    print('✗ 产品价格元素: 未找到')
            else:
                print('✗ 没有找到页面')
            
            browser.close()
            return True
    except Exception as e:
        print(f'✗ Error: {e}')
        return False

def check_search_results():
    """验证搜索结果文件"""
    print()
    print('='*50)
    print('3. 验证搜索结果文件')
    print('='*50)
    
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    if not os.path.exists(results_dir):
        print(f'✗ 结果目录不存在: {results_dir}')
        return False
    
    files = [f for f in os.listdir(results_dir) if f.endswith('.json') and not f.startswith('show')]
    print(f'找到 {len(files)} 个结果文件:')
    
    total_records = 0
    for f in sorted(files):
        try:
            filepath = os.path.join(results_dir, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                total_records += len(data)
                print(f'  ✓ {f}: {len(data)} 条记录')
        except Exception as e:
            print(f'  ✗ {f}: 错误 - {e}')
    
    print(f'\n总计: {len(files)} 个文件, {total_records} 条记录')
    return True

def check_scripts():
    """验证核心脚本是否存在"""
    print()
    print('='*50)
    print('4. 验证核心脚本')
    print('='*50)
    
    scripts_dir = os.path.dirname(__file__)
    required_scripts = [
        'chrome_launch.py',
        'search_box_v2.py',
        'slider_captcha.py',
        '1688_send_message.py',
        'verify_step.py',
        'batch_search.py',
    ]
    
    for script in required_scripts:
        filepath = os.path.join(scripts_dir, script)
        if os.path.exists(filepath):
            print(f'  ✓ {script}')
        else:
            print(f'  ✗ {script} (缺失)')
    
    return True

def main():
    print('='*50)
    print('小翰系统功能验证')
    print('='*50)
    
    check_chrome_connection()
    check_current_page()
    check_search_results()
    check_scripts()
    
    print()
    print('='*50)
    print('验证完成')
    print('='*50)

if __name__ == '__main__':
    main()
