#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在已打开的旺旺聊天页面发送消息

使用方法:
    python send_chat_message.py --message "消息内容"
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

def send_chat_message(message):
    """
    在已打开的旺旺聊天页面发送消息
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
            # 找到聊天页面
            chat_page = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    if "air.1688.com" in pg.url and "def_cbu_web_im" in pg.url:
                        chat_page = pg
                        safe_print(f"Found chat page: {pg.url[:80]}...")
                        break
                if chat_page:
                    break
            
            if not chat_page:
                safe_print("Error: No chat page found. Please click Wangwang icon first.")
                browser.close()
                return False
            
            # 切换到聊天页面
            chat_page.bring_to_front()
            time.sleep(2)
            
            # 截图聊天页面
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            chat_screenshot = f"chat_before_{timestamp}.png"
            chat_page.screenshot(path=chat_screenshot, full_page=False)
            safe_print(f"Chat screenshot saved: {chat_screenshot}")
            
            # 查找输入框 - 在iframe中
            safe_print("Looking for chat input...")
            
            # 先尝试在主页面查找
            input_selectors = [
                'pre[contenteditable="true"]',
                '[contenteditable="true"]',
                'textarea',
                'input[type="text"]',
                '.edit',
            ]
            
            input_found = False
            
            # 在所有frames中查找
            for frame in chat_page.frames:
                for sel in input_selectors:
                    try:
                        element = frame.locator(sel).first
                        if element.is_visible():
                            safe_print(f"Found input in frame: {sel}")
                            
                            # 点击输入框
                            element.click()
                            time.sleep(0.5)
                            
                            # 输入消息
                            element.fill(message)
                            safe_print(f"Message entered: {message}")
                            time.sleep(1)
                            
                            # 查找发送按钮
                            send_selectors = [
                                'button:has-text("发送")',
                                'text=发送',
                                '[class*="send"]',
                                'button.send',
                            ]
                            
                            for send_sel in send_selectors:
                                try:
                                    send_btn = frame.locator(send_sel).first
                                    if send_btn.is_visible():
                                        safe_print(f"Found send button: {send_sel}")
                                        send_btn.click()
                                        safe_print("✓ Message sent!")
                                        input_found = True
                                        time.sleep(2)
                                        break
                                except:
                                    continue
                            
                            if not input_found:
                                # 尝试按Enter发送
                                element.press("Enter")
                                safe_print("✓ Message sent (Enter key)")
                                input_found = True
                                time.sleep(2)
                            
                            break
                    except Exception as e:
                        continue
                
                if input_found:
                    break
            
            if not input_found:
                safe_print("Warning: Could not find chat input")
                # 尝试使用JavaScript
                try:
                    safe_print("Trying JavaScript method...")
                    chat_page.evaluate(f'''
                        () => {{
                            const inputs = document.querySelectorAll('pre[contenteditable="true"], [contenteditable="true"], textarea');
                            if (inputs.length > 0) {{
                                const input = inputs[0];
                                input.focus();
                                input.innerText = "{message}";
                                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                
                                // 查找发送按钮
                                const sendBtns = document.querySelectorAll('button');
                                for (const btn of sendBtns) {{
                                    if (btn.textContent.includes('发送')) {{
                                        btn.click();
                                        return true;
                                    }}
                                }}
                                return false;
                            }}
                            return false;
                        }}
                    ''')
                    safe_print("JavaScript method executed")
                    time.sleep(2)
                except Exception as e:
                    safe_print(f"JavaScript method failed: {e}")
            
            # 截图发送后的页面
            after_screenshot = f"chat_after_{timestamp}.png"
            chat_page.screenshot(path=after_screenshot, full_page=False)
            safe_print(f"After screenshot saved: {after_screenshot}")
            
            browser.close()
            return input_found
            
        except Exception as e:
            safe_print(f"Error: {e}")
            import traceback
            safe_print(traceback.format_exc())
            browser.close()
            return False

def main():
    parser = argparse.ArgumentParser(description='在旺旺聊天页面发送消息')
    parser.add_argument('--message', '-m', required=True, help='要发送的消息')
    args = parser.parse_args()
    
    safe_print("="*60)
    safe_print("发送旺旺消息")
    safe_print("="*60)
    safe_print(f"消息: {args.message}")
    safe_print("="*60)
    
    success = send_chat_message(args.message)
    
    if success:
        safe_print("\n✓ 消息发送成功")
        return 0
    else:
        safe_print("\n✗ 消息发送失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
