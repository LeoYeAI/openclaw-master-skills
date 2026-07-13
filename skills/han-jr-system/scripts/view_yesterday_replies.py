#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看昨天供应商的回复

从昨天的搜索结果中重新打开旺旺链接，查看供应商回复
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
import time
from pathlib import Path

def safe_print(text):
    try:
        print(text)
    except:
        print(str(text).encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

def view_supplier_replies():
    """查看供应商回复"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        safe_print("Error: pip install playwright")
        return
    
    # 昨天的搜索结果文件
    result_files = [
        'results/棒球帽.json',
        'results/棒球帽定制.json', 
        'results/鸭舌帽刺绣.json'
    ]
    
    all_suppliers = []
    for file in result_files:
        path = Path(file)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_suppliers.extend(data)
    
    if not all_suppliers:
        safe_print("没有找到昨天的搜索结果")
        return
    
    safe_print(f"找到 {len(all_suppliers)} 家昨天联系的供应商")
    safe_print("="*60)
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            safe_print(f"Error: 无法连接Chrome: {e}")
            return
        
        try:
            # 只查看前5家的回复
            for i, supplier in enumerate(all_suppliers[:5], 1):
                name = supplier.get('name', 'Unknown')[:30]
                link = supplier.get('link', '')
                
                if not link or 'similar_search' in link:
                    continue
                
                safe_print(f"\n[{i}/5] 查看供应商: {name}")
                
                # 获取旺旺链接
                search_page = browser.contexts[0].new_page()
                
                try:
                    # 访问店铺页面获取旺旺链接
                    search_page.goto(link, wait_until="domcontentloaded", timeout=10000)
                    time.sleep(3)
                    
                    # 获取旺旺链接
                    ww_href = search_page.evaluate('''() => {
                        const link = document.querySelector('a[href*="air.1688.com"][href*="im"]');
                        return link ? link.href : null;
                    }''')
                    
                    if ww_href:
                        safe_print(f"  打开旺旺聊天...")
                        
                        # 打开旺旺聊天
                        chat_page = browser.contexts[0].new_page()
                        chat_page.goto(ww_href, wait_until="domcontentloaded")
                        time.sleep(4)
                        
                        chat_page.bring_to_front()
                        time.sleep(2)
                        
                        # 截图查看聊天记录
                        screenshot_file = f"reply_{i}_{name.replace(' ', '_')[:20]}.png"
                        chat_page.screenshot(path=screenshot_file, full_page=False)
                        safe_print(f"  ✓ 截图已保存: {screenshot_file}")
                        
                        # 尝试获取聊天记录
                        messages = []
                        for frame in chat_page.frames:
                            try:
                                msg_elements = frame.query_selector_all('.message-item, .msg-item, [class*="message"]')
                                for msg in msg_elements[-5:]:  # 最近5条
                                    text = msg.inner_text() or ""
                                    if text.strip():
                                        messages.append(text[:80])
                            except:
                                pass
                        
                        if messages:
                            safe_print(f"  最近消息:")
                            for msg in messages:
                                safe_print(f"    - {msg}")
                        else:
                            safe_print(f"  暂无新消息或需要滚动查看")
                        
                        chat_page.close()
                    else:
                        safe_print(f"  ✗ 未找到旺旺链接")
                    
                    search_page.close()
                    
                except Exception as e:
                    safe_print(f"  ✗ 错误: {e}")
                    try:
                        search_page.close()
                    except:
                        pass
                
                # 间隔
                if i < 5:
                    safe_print("  等待3秒...")
                    time.sleep(3)
            
            safe_print("\n" + "="*60)
            safe_print("查看完成")
            safe_print("="*60)
            
        finally:
            browser.close()

if __name__ == "__main__":
    view_supplier_replies()
