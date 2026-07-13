#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
联系供应商并发送询价消息 - 通过旺旺图标

重要：客服按钮是旺旺图标
<img src="//img.alicdn.com/imgextra/i2/O1CN01is8OHl1kFZwewJrMC_!!6000000004654-2-tps-28-28.png">

使用方法:
    python contact_supplier_wangwang.py --link "供应商链接" --message "询价消息"
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

def contact_supplier_wangwang(shop_link, message):
    """
    联系供应商并发送消息 - 通过旺旺图标
    
    工作流程:
    1. 打开供应商店铺页面
    2. 寻找旺旺图标并点击
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
            
            # 寻找旺旺图标 - 优先级顺序
            safe_print("Looking for Wangwang icon...")
            
            # 旺旺图标特征
            wangwang_selectors = [
                # 图片src包含旺旺图标
                'img[src*="O1CN01is8OHl"]',
                'img[src*="wangwang"]',
                'img[src*="ww"]',
                # data-spm-anchor-id包含wangwang
                '[data-spm-anchor-id*="wangwang"]',
                # 类名包含wangwang
                '[class*="wangwang"]',
                '[class*="ww"]',
                # 文本包含旺旺
                'text=旺旺',
                'text=联系旺旺',
                # 客服相关
                'text=客服',
                'a:has-text("客服")',
                'button:has-text("客服")',
            ]
            
            clicked = False
            for selector in wangwang_selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible():
                        safe_print(f"Found Wangwang icon: {selector}")
                        element.click()
                        clicked = True
                        safe_print("Clicked Wangwang icon")
                        time.sleep(4)
                        break
                except Exception as e:
                    continue
            
            if not clicked:
                safe_print("Warning: Could not find Wangwang icon by selectors")
                # 尝试通过图片查找
                try:
                    # 查找所有图片
                    images = page.query_selector_all('img')
                    safe_print(f"Found {len(images)} images on page")
                    
                    for img in images:
                        src = img.get_attribute('src') or ''
                        if 'wangwang' in src.lower() or 'ww' in src.lower() or 'O1CN' in src:
                            safe_print(f"Found potential Wangwang img: {src}")
                            img.click()
                            clicked = True
                            safe_print("Clicked image")
                            time.sleep(4)
                            break
                except Exception as e:
                    safe_print(f"Image search failed: {e}")
            
            if not clicked:
                safe_print("Warning: Could not find any Wangwang icon")
            
            # 检查是否有聊天窗口打开（新标签页）
            chat_page = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    url = pg.url or ""
                    safe_print(f"Checking page: {url[:80]}")
                    if "air.1688.com" in url or "im" in url or "wangwang" in url:
                        chat_page = pg
                        safe_print(f"Chat page found!")
                        break
                if chat_page:
                    break
            
            if chat_page:
                safe_print(f"Chat page URL: {chat_page.url}")
                chat_page.bring_to_front()
                time.sleep(2)
                
                # 截图聊天窗口
                chat_screenshot = f"chat_{timestamp}.png"
                chat_page.screenshot(path=chat_screenshot, full_page=False)
                safe_print(f"Chat screenshot saved: {chat_screenshot}")
                
                # 尝试发送消息
                safe_print(f"Attempting to send message: {message}")
                
                # 查找输入框
                input_selectors = [
                    'pre[contenteditable="true"]',
                    '[contenteditable="true"]',
                    'textarea',
                    'input[type="text"]',
                ]
                
                input_found = False
                for sel in input_selectors:
                    try:
                        inp = chat_page.locator(sel).first
                        if inp.is_visible():
                            safe_print(f"Found input: {sel}")
                            inp.fill(message)
                            time.sleep(1)
                            
                            # 查找发送按钮
                            send_selectors = [
                                'button:has-text("发送")',
                                'text=发送',
                                '[class*="send"]',
                            ]
                            
                            for send_sel in send_selectors:
                                try:
                                    send_btn = chat_page.locator(send_sel).first
                                    if send_btn.is_visible():
                                        safe_print(f"Found send button: {send_sel}")
                                        send_btn.click()
                                        safe_print("Message sent!")
                                        input_found = True
                                        time.sleep(2)
                                        break
                                except:
                                    continue
                            
                            if not input_found:
                                # 尝试按Enter发送
                                inp.press("Enter")
                                safe_print("Pressed Enter to send")
                                input_found = True
                                time.sleep(2)
                            
                            break
                    except Exception as e:
                        continue
                
                if not input_found:
                    safe_print("Could not find chat input")
                    
            else:
                safe_print("No chat page found")
                # 截图当前页面
                current_screenshot = f"current_{timestamp}.png"
                page.screenshot(path=current_screenshot, full_page=False)
                safe_print(f"Current page screenshot: {current_screenshot}")
            
            browser.close()
            return clicked
            
        except Exception as e:
            safe_print(f"Error: {e}")
            import traceback
            safe_print(traceback.format_exc())
            browser.close()
            return False

def main():
    parser = argparse.ArgumentParser(description='联系供应商 - 通过旺旺图标')
    parser.add_argument('--link', '-l', required=True, help='供应商店铺链接')
    parser.add_argument('--message', '-m', required=True, help='询价消息')
    args = parser.parse_args()
    
    safe_print("="*60)
    safe_print("联系供应商 - 旺旺图标方式")
    safe_print("="*60)
    safe_print(f"店铺: {args.link}")
    safe_print(f"消息: {args.message}")
    safe_print("="*60)
    
    success = contact_supplier_wangwang(args.link, args.message)
    
    if success:
        safe_print("\n✓ 联系完成")
        return 0
    else:
        safe_print("\n✗ 联系失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
