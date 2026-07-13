#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量联系供应商 - 简化版

使用方法:
    python batch_contact.py --input "results/棒球帽.json" --message "询价消息"
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import argparse
import json
import time

def safe_print(text):
    try:
        print(text)
    except:
        print(str(text).encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

def contact_supplier_simple(shop_link, message, index):
    """
    简化版联系供应商
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
                    if "1688.com" in pg.url:
                        page = pg
                        break
                if page:
                    break
            
            if not page:
                safe_print(f"[{index}] Error: No page found")
                browser.close()
                return False
            
            safe_print(f"[{index}] Opening: {shop_link}")
            
            # 打开店铺页面
            try:
                page.goto(shop_link, wait_until="domcontentloaded", timeout=15000)
                time.sleep(2)
            except Exception as e:
                safe_print(f"[{index}] Page load timeout, continuing...")
            
            safe_print(f"[{index}] URL: {page.url}")
            
            # 寻找并点击旺旺图标
            clicked = False
            
            # 尝试多种方式找旺旺图标
            selectors = [
                'img[src*="O1CN01is8OHl"]',
                'img[src*="wangwang"]',
                '[data-spm-anchor-id*="wangwang"]',
                '[class*="wangwang"]',
            ]
            
            for selector in selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible():
                        element.click()
                        clicked = True
                        safe_print(f"[{index}] Clicked Wangwang icon")
                        time.sleep(3)
                        break
                except:
                    continue
            
            if not clicked:
                # 尝试JavaScript点击
                try:
                    page.evaluate('''() => {
                        const imgs = document.querySelectorAll('img');
                        for (const img of imgs) {
                            const src = img.src || '';
                            if (src.includes('O1CN') || src.includes('wangwang')) {
                                img.click();
                                return true;
                            }
                        }
                        return false;
                    }''')
                    clicked = True
                    safe_print(f"[{index}] Clicked via JavaScript")
                    time.sleep(3)
                except:
                    pass
            
            if not clicked:
                safe_print(f"[{index}] Warning: Could not click Wangwang")
                browser.close()
                return False
            
            # 查找聊天页面
            chat_page = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    if "air.1688.com" in pg.url and "def_cbu_web_im" in pg.url:
                        chat_page = pg
                        break
                if chat_page:
                    break
            
            if chat_page:
                chat_page.bring_to_front()
                time.sleep(2)
                
                # 发送消息
                for frame in chat_page.frames:
                    try:
                        inp = frame.locator('pre[contenteditable="true"]').first
                        if inp.is_visible():
                            inp.click()
                            inp.fill(message)
                            time.sleep(0.5)
                            
                            # 点击发送
                            send_btn = frame.locator('button:has-text("发送")').first
                            if send_btn.is_visible():
                                send_btn.click()
                                safe_print(f"[{index}] ✓ Message sent!")
                                time.sleep(2)
                                browser.close()
                                return True
                    except:
                        continue
                
                safe_print(f"[{index}] Could not send message")
            else:
                safe_print(f"[{index}] No chat page found")
            
            browser.close()
            return False
            
        except Exception as e:
            safe_print(f"[{index}] Error: {e}")
            browser.close()
            return False

def main():
    parser = argparse.ArgumentParser(description='批量联系供应商')
    parser.add_argument('--input', '-i', required=True, help='供应商JSON文件')
    parser.add_argument('--message', '-m', required=True, help='询价消息')
    args = parser.parse_args()
    
    # 读取供应商列表
    with open(args.input, 'r', encoding='utf-8') as f:
        suppliers = json.load(f)
    
    safe_print("="*60)
    safe_print("批量联系供应商")
    safe_print("="*60)
    safe_print(f"Total suppliers: {len(suppliers)}")
    safe_print(f"Message: {args.message}")
    safe_print("="*60)
    
    success_count = 0
    
    for i, supplier in enumerate(suppliers, 1):
        link = supplier.get('link', '')
        if not link or 'similar_search' in link:
            # 尝试从其他字段获取链接
            name = supplier.get('name', '')
            safe_print(f"[{i}] Skipping (no valid link): {name}")
            continue
        
        safe_print(f"\n[{i}/{len(suppliers)}] Contacting...")
        
        if contact_supplier_simple(link, args.message, i):
            success_count += 1
        
        # 等待间隔
        if i < len(suppliers):
            safe_print(f"[{i}] Waiting 5 seconds...")
            time.sleep(5)
    
    safe_print("\n" + "="*60)
    safe_print(f"Completed: {success_count}/{len(suppliers)} suppliers contacted")
    safe_print("="*60)

if __name__ == "__main__":
    main()
