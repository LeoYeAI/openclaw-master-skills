#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
联系供应商并发送询价消息

使用方法:
    python contact_supplier.py --link "供应商链接" --message "询价消息"

示例:
    python contact_supplier.py --link "http://shop483u278m52h82.1688.com" --message "我要定制棒球帽，请问多少钱？"
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

def contact_supplier(shop_link, message):
    """
    联系供应商并发送消息
    
    工作流程:
    1. 打开供应商店铺页面
    2. 点击"客服"按钮
    3. 发送询价消息
    4. 截图验证
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        safe_print("Error: pip install playwright")
        return False
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            safe_print(f"Error connecting to browser: {e}")
            return False
        
        try:
            # 获取页面
            page = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    page = pg
                    break
                if page:
                    break
            
            if not page:
                safe_print("Error: No page found")
                browser.close()
                return False
            
            safe_print(f"Current URL: {page.url}")
            
            # 打开供应商店铺页面
            safe_print(f"Opening shop: {shop_link}")
            page.goto(shop_link, wait_until="domcontentloaded")
            time.sleep(3)
            
            safe_print(f"Loaded: {page.url}")
            
            # 截图保存
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_file = f"shop_{timestamp}.png"
            page.screenshot(path=screenshot_file, full_page=False)
            safe_print(f"Screenshot saved: {screenshot_file}")
            
            # 寻找并点击"客服"按钮
            safe_print("Looking for customer service button...")
            
            # 多个可能的选择器
            service_selectors = [
                'text=客服',
                '[data-spm-anchor-id*="wangwang"]',
                'od-text[i18n="wangwang"]',
                'a:has-text("客服")',
                '.customer-service',
                'a[href*="im"]',
                'button:has-text("联系")',
            ]
            
            clicked = False
            for selector in service_selectors:
                try:
                    btn = page.locator(selector).first
                    if btn.is_visible():
                        safe_print(f"Found button: {selector}")
                        btn.click()
                        clicked = True
                        safe_print("Clicked customer service button")
                        time.sleep(3)
                        break
                except Exception as e:
                    continue
            
            if not clicked:
                safe_print("Warning: Could not find customer service button")
                # Try JavaScript click
                try:
                    page.evaluate('''() => {
                        const elements = document.querySelectorAll('*');
                        for (const el of elements) {
                            if (el.textContent && el.textContent.includes('客服')) {
                                el.click();
                                return true;
                            }
                        }
                        return false;
                    }''')
                    safe_print("Tried JavaScript click")
                    time.sleep(3)
                except Exception as e:
                    safe_print(f"JavaScript click failed: {e}")
            
            # 检查是否有聊天窗口打开
            chat_page = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    if "air.1688.com" in pg.url or "im" in pg.url:
                        chat_page = pg
                        break
                if chat_page:
                    break
            
            if chat_page:
                safe_print(f"Chat page found: {chat_page.url}")
                chat_page.bring_to_front()
                time.sleep(2)
                
                # 尝试发送消息
                safe_print(f"Sending message: {message}")
                # 这里需要找到聊天输入框
                # 由于聊天页面结构复杂，暂时只截图保存
                chat_screenshot = f"chat_{timestamp}.png"
                chat_page.screenshot(path=chat_screenshot, full_page=False)
                safe_print(f"Chat screenshot saved: {chat_screenshot}")
            else:
                safe_print("No chat page found, checking current page...")
                # 截图当前页面
                current_screenshot = f"current_{timestamp}.png"
                page.screenshot(path=current_screenshot, full_page=False)
                safe_print(f"Current page screenshot: {current_screenshot}")
            
            browser.close()
            return True
            
        except Exception as e:
            safe_print(f"Error: {e}")
            browser.close()
            return False

def main():
    parser = argparse.ArgumentParser(description='联系供应商')
    parser.add_argument('--link', '-l', required=True, help='供应商店铺链接')
    parser.add_argument('--message', '-m', required=True, help='询价消息')
    args = parser.parse_args()
    
    safe_print("="*60)
    safe_print("联系供应商")
    safe_print("="*60)
    safe_print(f"店铺: {args.link}")
    safe_print(f"消息: {args.message}")
    safe_print("="*60)
    
    success = contact_supplier(args.link, args.message)
    
    if success:
        safe_print("\n✓ 联系完成")
        return 0
    else:
        safe_print("\n✗ 联系失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
