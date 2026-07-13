#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从搜索结果页直接联系供应商

重要：在搜索结果页，每张卡片右下角有旺旺图标
- class="J_WangWang" 或 class="ww-light"
- class="ww-link"
- 文本包含"旺旺在线"

使用方法:
    python search_and_contact.py --keyword "棒球帽" --message "询价消息" --num 10
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import argparse
import time
import urllib.parse

def safe_print(text):
    try:
        print(text)
    except:
        print(str(text).encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

def search_and_contact(keyword, message, num_results=10):
    """
    搜索产品并直接联系供应商（从搜索结果页点击旺旺图标）
    
    工作流程:
    1. 搜索关键词
    2. 在搜索结果页找到所有旺旺图标
    3. 逐一点击旺旺图标打开聊天
    4. 发送询价消息
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
            # 获取页面
            page = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    if "1688.com" in pg.url:
                        page = pg
                        break
                if page:
                    break
            
            if not page:
                safe_print("Error: No page found")
                browser.close()
                return 0
            
            # Step 1: 搜索关键词
            safe_print(f"Searching: {keyword}")
            page.goto("https://s.1688.com/selloffer/offer_search.htm", wait_until="domcontentloaded")
            time.sleep(2)
            
            # 输入关键词
            search_box = page.query_selector('input[name="keywords"]')
            if search_box:
                search_box.fill("")
                search_box.fill(keyword)
                time.sleep(0.5)
                search_box.press("Enter")
                safe_print(f"Submitted search: {keyword}")
                time.sleep(5)
            
            safe_print(f"Search results loaded: {page.url[:80]}")
            
            # Step 2: 找到所有旺旺图标
            safe_print("Looking for Wangwang icons on search results page...")
            
            # 旺旺图标选择器（按优先级）
            wangwang_selectors = [
                '.J_WangWang',           # 主要class
                '.ww-light',             # 旺旺灯
                '.ww-link',              # 旺旺链接
                'a[href*="air.1688.com"][href*="im"]',  # 聊天链接
                'a:has-text("旺旺在线")', # 文本包含旺旺在线
                '[data-spm-anchor-id*="offerlist"]',  # 商品列表中的旺旺
            ]
            
            # 获取所有旺旺按钮
            wangwang_buttons = []
            for selector in wangwang_selectors:
                try:
                    buttons = page.query_selector_all(selector)
                    safe_print(f"  Selector '{selector}': found {len(buttons)} elements")
                    for btn in buttons:
                        if btn not in wangwang_buttons:
                            wangwang_buttons.append(btn)
                except:
                    pass
            
            safe_print(f"Total unique Wangwang buttons: {len(wangwang_buttons)}")
            
            if len(wangwang_buttons) == 0:
                safe_print("Warning: No Wangwang buttons found")
                browser.close()
                return 0
            
            # Step 3: 逐一联系供应商
            safe_print(f"\nStarting to contact {min(len(wangwang_buttons), num_results)} suppliers...")
            
            for i, btn in enumerate(wangwang_buttons[:num_results], 1):
                safe_print(f"\n[{i}/{min(len(wangwang_buttons), num_results)}] Contacting supplier...")
                
                try:
                    # 获取供应商名称（如果有）
                    try:
                        # 尝试从父元素获取供应商名
                        parent = btn
                        for _ in range(5):
                            parent = parent.query_selector('..')
                            if parent:
                                text = parent.inner_text() or ''
                                if len(text) > 5 and len(text) < 100:
                                    safe_print(f"  Supplier: {text[:50]}")
                                    break
                    except:
                        pass
                    
                    # 点击旺旺图标
                    btn.click()
                    safe_print(f"  Clicked Wangwang icon")
                    time.sleep(3)
                    
                    # 查找新打开的聊天页面
                    chat_page = None
                    for ctx in browser.contexts:
                        for pg in ctx.pages:
                            if "air.1688.com" in pg.url and "def_cbu_web_im" in pg.url:
                                # 检查是否是新页面
                                chat_page = pg
                                break
                        if chat_page:
                            break
                    
                    if chat_page:
                        chat_page.bring_to_front()
                        time.sleep(2)
                        
                        # 发送消息
                        message_sent = False
                        for frame in chat_page.frames:
                            try:
                                inp = frame.locator('pre[contenteditable="true"]').first
                                if inp.is_visible():
                                    inp.click()
                                    inp.fill(message)
                                    time.sleep(0.5)
                                    
                                    send_btn = frame.locator('button:has-text("发送")').first
                                    if send_btn.is_visible():
                                        send_btn.click()
                                        safe_print(f"  ✓ Message sent!")
                                        message_sent = True
                                        contacted += 1
                                        time.sleep(2)
                                        break
                            except:
                                continue
                        
                        if not message_sent:
                            safe_print(f"  ✗ Could not send message")
                    else:
                        safe_print(f"  ✗ No chat page opened")
                    
                    # 回到搜索结果页
                    page.bring_to_front()
                    time.sleep(2)
                    
                except Exception as e:
                    safe_print(f"  ✗ Error: {e}")
                    continue
                
                # 间隔
                if i < min(len(wangwang_buttons), num_results):
                    safe_print(f"  Waiting 5 seconds...")
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
        description='从搜索结果页直接联系供应商',
        epilog='''
示例:
  python search_and_contact.py --keyword "棒球帽" --message "询价内容" --num 10
  python search_and_contact.py -k "帽子" -m "我要定制1000顶" -n 5

说明:
  此脚本会在搜索结果页直接点击每张卡片右下角的旺旺图标
  自动打开聊天窗口并发送消息
        '''
    )
    parser.add_argument('--keyword', '-k', required=True, help='搜索关键词')
    parser.add_argument('--message', '-m', required=True, help='询价消息')
    parser.add_argument('--num', '-n', type=int, default=10, help='联系供应商数量（默认10）')
    args = parser.parse_args()
    
    safe_print("="*60)
    safe_print("搜索并联系供应商（搜索结果页旺旺图标）")
    safe_print("="*60)
    safe_print(f"Keyword: {args.keyword}")
    safe_print(f"Message: {args.message}")
    safe_print(f"Max suppliers: {args.num}")
    safe_print("="*60)
    
    count = search_and_contact(args.keyword, args.message, args.num)
    
    safe_print("\n" + "="*60)
    safe_print(f"Completed: {count} suppliers contacted")
    safe_print("="*60)

if __name__ == "__main__":
    main()
