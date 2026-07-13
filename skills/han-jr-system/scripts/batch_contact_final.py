#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量联系供应商 - 完整版（使用正确的iframe方法）

使用方法:
    python batch_contact_final.py --keyword "棒球帽" --message "询价内容" --num 20

功能:
    1. 搜索关键词
    2. 获取所有旺旺链接
    3. 逐一打开聊天页面
    4. 在正确的frame中发送消息
    5. 关闭聊天页面，继续下一家
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import argparse
import time
from datetime import datetime

def safe_print(text):
    try:
        print(text)
    except:
        print(str(text).encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

def close_all_chat_pages(browser):
    """关闭所有旺旺聊天页面"""
    closed = 0
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if 'air.1688.com' in pg.url:
                try:
                    pg.close()
                    closed += 1
                except:
                    pass
    return closed

def send_message_in_chat(chat_page, message):
    """
    在聊天页面发送消息
    
    正确的做法：遍历所有frames，在Frame 1中找到输入框
    """
    for frame_idx, frame in enumerate(chat_page.frames):
        try:
            # 查找输入框
            inp = frame.locator("pre[contenteditable='true']").first
            if inp.is_visible():
                # 点击输入框
                inp.click()
                time.sleep(0.3)
                
                # 填入消息
                inp.fill(message)
                time.sleep(0.3)
                
                # 点击发送按钮
                btn = frame.locator("button:has-text('发送')").first
                if btn.is_visible():
                    btn.click()
                    return True, frame_idx
        except:
            continue
    return False, None

def batch_contact(keyword, message, num_results=20):
    """
    批量联系供应商
    
    流程:
    1. 搜索关键词
    2. 获取旺旺链接
    3. 逐一联系
    4. 记录结果
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        safe_print("Error: pip install playwright")
        return 0
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            safe_print(f"Error connecting to browser: {e}")
            return 0
        
        try:
            # 步骤1: 清理现有聊天页面
            safe_print("="*60)
            safe_print("批量联系供应商 - 完整版")
            safe_print("="*60)
            
            closed = close_all_chat_pages(browser)
            if closed > 0:
                safe_print(f"Closed {closed} existing chat pages")
            
            # 步骤2: 获取或创建搜索页
            search_page = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    if 'selloffer' in pg.url:
                        search_page = pg
                        break
                if search_page:
                    break
            
            if not search_page:
                search_page = browser.contexts[0].new_page()
            
            # 步骤3: 搜索关键词
            safe_print(f"\nSearching: {keyword}")
            search_page.goto("https://s.1688.com/selloffer/offer_search.htm", wait_until="domcontentloaded")
            time.sleep(2)
            
            search_box = search_page.query_selector('input[name="keywords"]')
            if search_box:
                search_box.fill("")
                search_box.fill(keyword)
                time.sleep(0.5)
                search_box.press("Enter")
                safe_print(f"Submitted search")
                time.sleep(5)
            
            # 步骤4: 获取旺旺链接
            ww_hrefs = search_page.evaluate('''() => {
                const links = document.querySelectorAll('a[href*="air.1688.com"][href*="im"]');
                return Array.from(links).map(a => a.href);
            }''')
            
            total = min(len(ww_hrefs), num_results)
            safe_print(f"Found {len(ww_hrefs)} wangwang links")
            safe_print(f"Will contact: {total} suppliers")
            safe_print("="*60)
            
            # 步骤5: 逐一联系
            success_count = 0
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for i in range(total):
                safe_print(f"\n[{i+1}/{total}] Contacting supplier...")
                
                try:
                    # 打开聊天页面
                    chat_page = browser.contexts[0].new_page()
                    chat_page.goto(ww_hrefs[i], wait_until="domcontentloaded")
                    time.sleep(4)
                    
                    chat_page.bring_to_front()
                    time.sleep(1)
                    
                    # 发送消息
                    sent, frame_idx = send_message_in_chat(chat_page, message)
                    
                    if sent:
                        safe_print(f"  ✓ Message sent (Frame {frame_idx})")
                        success_count += 1
                    else:
                        safe_print(f"  ✗ Failed to send")
                    
                    time.sleep(1)
                    
                    # 关闭聊天页面
                    chat_page.close()
                    time.sleep(2)
                    
                except Exception as e:
                    safe_print(f"  ✗ Error: {e}")
                    continue
                
                # 间隔
                if i < total - 1:
                    safe_print("  Waiting 3 seconds...")
                    time.sleep(3)
            
            # 完成报告
            safe_print("\n" + "="*60)
            safe_print(f"Completed: {success_count}/{total} suppliers contacted")
            safe_print(f"Success rate: {success_count/total*100:.1f}%")
            safe_print("="*60)
            
            browser.close()
            return success_count
            
        except Exception as e:
            safe_print(f"Error: {e}")
            import traceback
            safe_print(traceback.format_exc())
            browser.close()
            return 0

def main():
    parser = argparse.ArgumentParser(
        description='批量联系供应商 - 完整版',
        epilog='''
示例:
  python batch_contact_final.py --keyword "棒球帽" --message "询价内容" --num 20
  python batch_contact_final.py -k "帽子 定制" -m "我要定制1000顶" -n 15

说明:
  使用正确的iframe方法发送消息
  每次只打开一个聊天页面
  自动关闭聊天页面后继续下一家
        '''
    )
    parser.add_argument('--keyword', '-k', required=True, help='搜索关键词')
    parser.add_argument('--message', '-m', required=True, help='询价消息')
    parser.add_argument('--num', '-n', type=int, default=20, help='联系供应商数量（默认20）')
    args = parser.parse_args()
    
    batch_contact(args.keyword, args.message, args.num)

if __name__ == "__main__":
    main()
