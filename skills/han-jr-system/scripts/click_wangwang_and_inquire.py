#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从1688搜索结果页点击供应商旺旺图标并询价

Usage:
    python click_wangwang_and_inquire.py --index 1 --message "2000支2B铅笔黑色的多少钱？要开票"
    
Args:
    --index: 供应商序号（1=第一个，2=第二个，以此类推）
    --message: 询价消息
"""

import argparse
import sys
import time
import re
from datetime import datetime
from pathlib import Path

def safe_print(*a, **k):
    def to_safe(s):
        return "".join(c if ord(c) < 128 else "?" for c in str(s))
    try:
        print(*a, **k)
    except (UnicodeEncodeError, UnicodeDecodeError):
        print(*[to_safe(x) for x in a], **k)


# 旺旺按钮选择器（正确的旺旺在线按钮）
WANGWANG_SELECTORS = [
    "span.J_WangWang a",  # 最准确的：class包含J_WangWang的span下的a标签
    "a:has-text('旺旺在线')",  # 包含"旺旺在线"文本
    "a.ww-link",  # class为ww-link
    "a[href*='def_cbu_web_im']",  # href包含def_cbu_web_im
    "a[data-spm-anchor-id*='offerlist']",  # data-spm-anchor-id包含offerlist
    "a:has(od-text[i18n='wangwang'])",
    "a[data-spm-anchor-id*='wangwang']",
    "[class*='wangwang']",
]


def get_page(browser):
    """获取1688页面"""
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if "1688.com" in (pg.url or ""):
                return pg
    return None


def get_chat_tab(browser):
    """获取旺旺聊天页"""
    for ctx in browser.contexts:
        for pg in ctx.pages:
            u = pg.url or ""
            if "air.1688.com" in u and "def_cbu_web_im" in u:
                return pg
    return None


def click_wangwang_on_search_page(page, index=1):
    """
    在搜索结果页点击第index个供应商的旺旺图标
    正确的旺旺按钮特征：class包含J_WangWang，或包含"旺旺在线"文本
    """
    safe_print(f"Looking for supplier #{index} wangwang button...")
    
    # 方法1：直接找所有旺旺按钮（span.J_WangWang a）
    clicked = False
    
    # 优先使用最准确的选择器
    primary_selectors = [
        "span.J_WangWang a",  # 最准确
        "a:has-text('旺旺在线')",
        "a.ww-link",
    ]
    
    for sel in primary_selectors:
        try:
            buttons = page.locator(sel).all()
            safe_print(f"Found {len(buttons)} buttons with selector: {sel}")
            if len(buttons) >= index:
                btn = buttons[index - 1]
                btn.scroll_into_view_if_needed()
                page.wait_for_timeout(800)
                btn.click()
                clicked = True
                safe_print(f"Clicked wangwang button #{index} ({sel})")
                break
        except Exception as e:
            safe_print(f"Selector {sel} failed: {e}")
            continue
    
    if not clicked:
        # 方法2：先找供应商卡片，再在卡片内找旺旺按钮
        safe_print("Trying card-based approach...")
        card_selectors = [
            "[data-offer-id]",
            ".sm-offer-item",
            ".offer-item",
        ]
        
        cards = []
        for sel in card_selectors:
            try:
                elements = page.locator(sel).all()
                if elements:
                    cards = elements
                    safe_print(f"Found {len(cards)} supplier cards")
                    break
            except:
                continue
        
        if cards and len(cards) >= index:
            target_card = cards[index - 1]
            
            # 在卡片内找旺旺按钮
            for sel in WANGWANG_SELECTORS:
                try:
                    wangwang_btn = target_card.locator(sel).first
                    if wangwang_btn.count() > 0:
                        wangwang_btn.scroll_into_view_if_needed()
                        page.wait_for_timeout(800)
                        wangwang_btn.click()
                        clicked = True
                        safe_print(f"Clicked card wangwang button ({sel})")
                        break
                except:
                    continue
    
    return clicked


def send_message_in_chat(page, message):
    """
    在聊天窗口发送消息
    """
    safe_print(f"Sending message: {message}")
    
    # 找聊天输入框
    input_selectors = [
        "pre[contenteditable='true']",
        "[contenteditable='true']",
        "textarea",
    ]
    
    chat_frame = None
    for frame in [page] + list(page.frames):
        for sel in input_selectors:
            try:
                inp = frame.locator(sel).first
                inp.wait_for(state="visible", timeout=2000)
                chat_frame = frame
                break
            except:
                continue
        if chat_frame:
            break
    
    if not chat_frame:
        safe_print("Error: Could not find chat input")
        return False
    
    try:
        # 点击输入框
        inp = chat_frame.locator(input_selectors[0]).first
        inp.click()
        page.wait_for_timeout(300)
        
        # 填入消息
        inp.fill(message)
        page.wait_for_timeout(400)
        
        # 点击发送或按Enter
        send_selectors = [
            "button:has-text('发送')",
            "a:has-text('发送')",
            "span:has-text('发送')",
        ]
        
        sent = False
        for sel in send_selectors:
            try:
                btn = chat_frame.locator(sel).first
                btn.click()
                sent = True
                break
            except:
                continue
        
        if not sent:
            inp.press("Enter")
        
        page.wait_for_timeout(600)
        safe_print("Message sent")
        return True
        
    except Exception as e:
        safe_print(f"Error sending message: {e}")
        return False


def record_inquiry(supplier_name, message, timestamp):
    """
    记录询价信息
    """
    record_file = Path("inquiry_records.txt")
    with open(record_file, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"Time: {timestamp}\n")
        f.write(f"Supplier: {supplier_name}\n")
        f.write(f"Message: {message}\n")
        f.write(f"{'='*50}\n")
    safe_print(f"Recorded to: {record_file}")


def main():
    parser = argparse.ArgumentParser(description='Click wangwang and inquire from 1688 search results')
    parser.add_argument('--index', '-i', type=int, default=1, help='Supplier index (1=first)')
    parser.add_argument('--message', '-m', default="2000支2B铅笔黑色的多少钱？要开票", help='Inquiry message')
    args = parser.parse_args()
    
    safe_print("="*60)
    safe_print("1688 Wangwang Click and Inquire")
    safe_print("="*60)
    
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        safe_print("Error: playwright required")
        safe_print("Run: pip install playwright")
        sys.exit(1)
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            safe_print(f"Error: Cannot connect to Chrome: {e}")
            safe_print("Please run: python chrome_launch.py")
            sys.exit(1)
        
        try:
            # Step 1: Find 1688 search page
            page = get_page(browser)
            if not page:
                safe_print("Error: No 1688 page found")
                browser.close()
                sys.exit(1)
            
            page.bring_to_front()
            safe_print(f"Current page: {(page.url or '')[:60]}")
            
            # Step 2: Click wangwang button
            safe_print(f"\nStep 1: Clicking wangwang button for supplier #{args.index}")
            if not click_wangwang_on_search_page(page, args.index):
                safe_print("Error: Could not click wangwang button")
                browser.close()
                sys.exit(1)
            
            # Wait for chat window to open
            safe_print("Waiting for chat window...")
            page.wait_for_timeout(6000)
            
            # Check if new tab opened
            all_pages = []
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    all_pages.append(pg.url or "")
            safe_print(f"All tabs: {len(all_pages)}")
            for i, url in enumerate(all_pages, 1):
                safe_print(f"  {i}. {url[:60]}")
            
            # Step 3: Find chat tab
            chat_page = get_chat_tab(browser)
            if not chat_page:
                # Maybe chat opened in same tab
                page.wait_for_timeout(3000)
                if "air.1688.com" in (page.url or ""):
                    chat_page = page
                    safe_print("Chat opened in same tab")
                else:
                    safe_print("Error: Chat window did not open")
                    safe_print("Please check if 1688 requires login")
                    browser.close()
                    sys.exit(1)
            
            chat_page.bring_to_front()
            safe_print("Waiting for chat page to fully load...")
            chat_page.wait_for_timeout(4000)  # Increased wait time
            
            # Get supplier name from URL
            supplier_name = "Unknown"
            try:
                url = chat_page.url or ""
                match = re.search(r"touid=([^&#]+)", url)
                if match:
                    supplier_name = match.group(1)
            except:
                pass
            
            safe_print(f"\nStep 2: Chat opened with: {supplier_name}")
            
            # Step 4: Send message
            safe_print(f"\nStep 3: Sending inquiry message")
            if send_message_in_chat(chat_page, args.message):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                record_inquiry(supplier_name, args.message, timestamp)
                
                # Step 5: Wait for reply and screenshot
                safe_print("\nStep 4: Waiting for reply (8 seconds)...")
                chat_page.wait_for_timeout(8000)
                
                # Screenshot
                screenshot_file = f"chat_reply_{supplier_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                try:
                    chat_page.screenshot(path=screenshot_file, full_page=True)
                    safe_print(f"Screenshot saved: {screenshot_file}")
                except Exception as e:
                    safe_print(f"Screenshot failed: {e}")
                
                safe_print("\n" + "="*60)
                safe_print("Inquiry completed successfully!")
                safe_print(f"Supplier: {supplier_name}")
                safe_print(f"Message: {args.message}")
                safe_print("="*60)
                
                # Close chat tab to avoid confusion with next supplier
                safe_print("\nClosing chat tab...")
                try:
                    chat_page.close()
                    safe_print("Chat tab closed")
                except Exception as e:
                    safe_print(f"Warning: Could not close chat tab: {e}")
                
                browser.close()
                return 0
            else:
                safe_print("Error: Failed to send message")
                browser.close()
                return 1
                
        except Exception as e:
            safe_print(f"Error: {e}")
            browser.close()
            sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())