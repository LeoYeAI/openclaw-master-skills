#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜索并联系供应商 - 修复版

重要规则:
1. 每次只打开一个旺旺聊天页面
2. 发送完消息后必须关闭聊天页面
3. 回到搜索结果页后再联系下一家

使用方法:
    python search_and_contact_fixed.py --keyword "棒球帽" --message "询价内容" --num 10
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import argparse
import time

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
            if 'air.1688.com' in pg.url and 'def_cbu_web_im' in pg.url:
                try:
                    pg.close()
                    closed += 1
                except:
                    pass
    return closed

def get_search_page(browser):
    """获取搜索结果页"""
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if 'selloffer' in pg.url or '1688.com' in pg.url:
                return pg
    return None

def get_chat_page(browser):
    """获取当前打开的聊天页面（只应该有一个）"""
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if 'air.1688.com' in pg.url and 'def_cbu_web_im' in pg.url:
                return pg
    return None

def send_message_in_chat(chat_page, message):
    """在聊天页面发送消息"""
    for frame in chat_page.frames:
        try:
            inp = frame.locator('pre[contenteditable="true"]').first
            if inp.is_visible():
                inp.click()
                time.sleep(0.3)
                inp.fill(message)
                time.sleep(0.5)
                
                send_btn = frame.locator('button:has-text("发送")').first
                if send_btn.is_visible():
                    send_btn.click()
                    return True
        except:
            continue
    return False

def search_and_contact_fixed(keyword, message, num_results=10):
    """
    搜索产品并联系供应商（修复版）
    
    规则:
    1. 每次只打开一个聊天页面
    2. 发送完消息后关闭聊天页面
    3. 回到搜索结果页后再联系下一家
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        safe_print("Error: pip install playwright")
        return 0
    
    contacted = 0
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            safe_print(f"Error connecting to browser: {e}")
            return 0
        
        try:
            # 步骤1: 清理所有现有的聊天页面
            safe_print("Closing existing chat pages...")
            closed = close_all_chat_pages(browser)
            safe_print(f"Closed {closed} chat pages")
            
            # 步骤2: 获取或创建搜索结果页
            search_page = get_search_page(browser)
            
            if not search_page:
                safe_print("Creating new search page...")
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
                safe_print(f"Submitted search: {keyword}")
                time.sleep(5)
            
            safe_print(f"Search results loaded")
            
            # 步骤4: 找到所有旺旺图标
            safe_print("\nLooking for Wangwang icons...")
            wangwang_buttons = search_page.query_selector_all('.J_WangWang, .ww-link')
            safe_print(f"Found {len(wangwang_buttons)} Wangwang buttons")
            
            if len(wangwang_buttons) == 0:
                safe_print("No Wangwang buttons found")
                browser.close()
                return 0
            
            # 步骤5: 逐一联系供应商
            safe_print(f"\nStarting to contact {min(len(wangwang_buttons), num_results)} suppliers...")
            
            for i in range(min(len(wangwang_buttons), num_results)):
                safe_print(f"\n{'='*60}")
                safe_print(f"[{i+1}/{min(len(wangwang_buttons), num_results)}] Contacting supplier...")
                safe_print('='*60)
                
                try:
                    # 确保在搜索结果页
                    search_page.bring_to_front()
                    time.sleep(1)
                    
                    # 重新获取按钮列表（因为页面可能刷新）
                    wangwang_buttons = search_page.query_selector_all('.J_WangWang, .ww-link')
                    if i >= len(wangwang_buttons):
                        safe_print("No more buttons available")
                        break
                    
                    btn = wangwang_buttons[i]
                    
                    # 点击旺旺图标
                    safe_print("Clicking Wangwang icon...")
                    btn.click()
                    time.sleep(4)
                    
                    # 获取新打开的聊天页面
                    chat_page = get_chat_page(browser)
                    
                    if not chat_page:
                        safe_print("✗ Chat page not opened")
                        continue
                    
                    safe_print(f"Chat page opened")
                    chat_page.bring_to_front()
                    time.sleep(2)
                    
                    # 发送消息
                    safe_print("Sending message...")
                    if send_message_in_chat(chat_page, message):
                        safe_print("✓ Message sent successfully!")
                        contacted += 1
                    else:
                        safe_print("✗ Failed to send message")
                    
                    time.sleep(2)
                    
                    # 关闭聊天页面
                    safe_print("Closing chat page...")
                    chat_page.close()
                    time.sleep(2)
                    
                    # 回到搜索结果页
                    search_page.bring_to_front()
                    safe_print("Back to search page")
                    
                except Exception as e:
                    safe_print(f"✗ Error: {e}")
                    # 确保关闭聊天页面
                    close_all_chat_pages(browser)
                    continue
                
                # 间隔
                if i < min(len(wangwang_buttons), num_results) - 1:
                    safe_print("Waiting 5 seconds...")
                    time.sleep(5)
            
            browser.close()
            return contacted
            
        except Exception as e:
            safe_print(f"Error: {e}")
            import traceback
            safe_print(traceback.format_exc())
            browser.close()
            return contacted

def main():
    parser = argparse.ArgumentParser(
        description='搜索并联系供应商（修复版）',
        epilog='''
重要规则:
  1. 每次只打开一个旺旺聊天页面
  2. 发送完消息后必须关闭聊天页面
  3. 回到搜索结果页后再联系下一家

示例:
  python search_and_contact_fixed.py --keyword "棒球帽" --message "询价内容" --num 10
        '''
    )
    parser.add_argument('--keyword', '-k', required=True, help='搜索关键词')
    parser.add_argument('--message', '-m', required=True, help='询价消息')
    parser.add_argument('--num', '-n', type=int, default=10, help='联系供应商数量（默认10）')
    args = parser.parse_args()
    
    safe_print("="*60)
    safe_print("搜索并联系供应商（修复版）")
    safe_print("="*60)
    safe_print(f"Keyword: {args.keyword}")
    safe_print(f"Message: {args.message}")
    safe_print(f"Max suppliers: {args.num}")
    safe_print("="*60)
    
    count = search_and_contact_fixed(args.keyword, args.message, args.num)
    
    safe_print("\n" + "="*60)
    safe_print(f"Completed: {count} suppliers contacted")
    safe_print("="*60)

if __name__ == "__main__":
    main()
