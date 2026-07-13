#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旺旺聊天管理器 - 查看聊天记录、搜索联系人、回复消息

功能:
    1. 列出所有旺旺聊天页面
    2. 打开指定的旺旺聊天页面
    3. 在联系人列表中搜索
    4. 查看聊天记录和回复信息
    5. 继续回复消息

用法:
    python wangwang_chat_manager.py                    # 列出所有旺旺聊天页
    python wangwang_chat_manager.py --list             # 同上
    python wangwang_chat_manager.py --open 0           # 打开第1个旺旺页
    python wangwang_chat_manager.py --search "供应商"   # 搜索联系人
    python wangwang_chat_manager.py --reply "消息"      # 在当前页回复消息
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import argparse
import time
import json
from datetime import datetime
from pathlib import Path

def safe_print(text):
    try:
        print(text)
    except:
        print(str(text).encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

def get_all_chat_pages(browser):
    """获取所有旺旺聊天页面"""
    chat_pages = []
    for ctx_idx, ctx in enumerate(browser.contexts):
        for pg_idx, pg in enumerate(ctx.pages):
            url = pg.url or ""
            if "air.1688.com" in url and "def_cbu_web_im" in url:
                title = pg.title() or ""
                chat_pages.append({
                    'context': ctx_idx,
                    'page': pg_idx,
                    'url': url,
                    'title': title,
                    'page_obj': pg
                })
    return chat_pages

def list_chat_pages(browser):
    """列出所有旺旺聊天页面"""
    chat_pages = get_all_chat_pages(browser)
    
    safe_print("="*60)
    safe_print(f"找到 {len(chat_pages)} 个旺旺聊天页面")
    safe_print("="*60)
    
    for i, info in enumerate(chat_pages):
        safe_print(f"\n[{i}] {info['title'][:40]}")
        safe_print(f"    URL: {info['url'][:60]}...")
    
    if not chat_pages:
        safe_print("\n没有找到旺旺聊天页面")
        safe_print("提示: 先使用 batch_contact_final.py 联系供应商")
    
    return chat_pages

def open_chat_page(browser, index):
    """打开指定的旺旺聊天页面"""
    chat_pages = get_all_chat_pages(browser)
    
    if index < 0 or index >= len(chat_pages):
        safe_print(f"错误: 索引 {index} 超出范围 (0-{len(chat_pages)-1})")
        return None
    
    page_info = chat_pages[index]
    page = page_info['page_obj']
    
    safe_print(f"\n切换到: {page_info['title'][:40]}")
    page.bring_to_front()
    time.sleep(2)
    
    return page

def search_contacts(page, keyword):
    """在联系人列表中搜索"""
    safe_print(f"\n搜索联系人: '{keyword}'")
    
    found = []
    
    # 尝试在frames中查找联系人
    for frame_idx, frame in enumerate(page.frames):
        try:
            # 查找联系人元素
            contacts = frame.query_selector_all('.contact-item, .list-item, [class*="contact"]')
            
            for contact in contacts:
                try:
                    text = contact.inner_text() or ""
                    if keyword in text:
                        found.append({
                            'frame': frame_idx,
                            'text': text[:50],
                            'element': contact
                        })
                except:
                    pass
        except:
            pass
    
    safe_print(f"找到 {len(found)} 个匹配联系人")
    
    for i, info in enumerate(found[:10]):  # 只显示前10个
        safe_print(f"  [{i}] {info['text']}")
    
    return found

def get_chat_history(page):
    """获取聊天记录"""
    safe_print("\n获取聊天记录...")
    
    messages = []
    
    for frame_idx, frame in enumerate(page.frames):
        try:
            # 查找消息气泡
            msg_elements = frame.query_selector_all('.message-item, .msg-item, [class*="message"], [class*="msg"]')
            
            for msg in msg_elements:
                try:
                    text = msg.inner_text() or ""
                    if text.strip():
                        messages.append({
                            'frame': frame_idx,
                            'text': text[:100],
                            'element': msg
                        })
                except:
                    pass
        except:
            pass
    
    safe_print(f"找到 {len(messages)} 条消息")
    
    # 显示最近10条消息
    for msg in messages[-10:]:
        safe_print(f"  {msg['text']}")
    
    return messages

def reply_message(page, message):
    """在当前聊天页面回复消息"""
    safe_print(f"\n发送回复: {message}")
    
    sent = False
    
    # 在Frame 1中查找输入框（根据之前的经验）
    for frame_idx, frame in enumerate(page.frames):
        try:
            inp = frame.locator("pre[contenteditable='true']").first
            if inp.is_visible():
                inp.click()
                time.sleep(0.3)
                inp.fill(message)
                time.sleep(0.3)
                
                btn = frame.locator("button:has-text('发送')").first
                if btn.is_visible():
                    btn.click()
                    safe_print(f"✓ 消息已发送 (Frame {frame_idx})")
                    sent = True
                    time.sleep(1)
                    break
        except:
            continue
    
    if not sent:
        safe_print("✗ 发送失败")
    
    return sent

def save_last_chat_url(url):
    """保存最后访问的旺旺URL"""
    config_file = Path("last_chat_url.txt")
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(url)

def load_last_chat_url():
    """加载最后访问的旺旺URL"""
    config_file = Path("last_chat_url.txt")
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def main():
    parser = argparse.ArgumentParser(
        description='旺旺聊天管理器 - 查看聊天记录、搜索联系人、回复消息',
        epilog='''
示例:
  python wangwang_chat_manager.py                    # 列出所有旺旺聊天页
  python wangwang_chat_manager.py --open 0           # 打开第1个旺旺页
  python wangwang_chat_manager.py --search "供应商"   # 搜索联系人
  python wangwang_chat_manager.py --history          # 查看聊天记录
  python wangwang_chat_manager.py --reply "好的"      # 回复消息
  python wangwang_chat_manager.py --last             # 打开最后访问的旺旺页
        '''
    )
    parser.add_argument('--list', '-l', action='store_true', help='列出所有旺旺聊天页')
    parser.add_argument('--open', '-o', type=int, help='打开指定索引的旺旺页')
    parser.add_argument('--search', '-s', help='搜索联系人')
    parser.add_argument('--history', '-hi', action='store_true', help='查看聊天记录')
    parser.add_argument('--reply', '-r', help='回复消息')
    parser.add_argument('--last', action='store_true', help='打开最后访问的旺旺页')
    args = parser.parse_args()
    
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        safe_print("Error: pip install playwright")
        sys.exit(1)
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            safe_print(f"Error: 无法连接Chrome: {e}")
            safe_print("请先运行: python chrome_launch.py")
            sys.exit(1)
        
        try:
            # 默认列出所有聊天页
            if not any([args.list, args.open is not None, args.search, args.history, args.reply, args.last]):
                args.list = True
            
            # 列出所有聊天页
            if args.list:
                chat_pages = list_chat_pages(browser)
                browser.close()
                return
            
            # 打开最后访问的旺旺页
            if args.last:
                last_url = load_last_chat_url()
                if last_url:
                    safe_print(f"打开最后访问的旺旺页: {last_url[:60]}...")
                    page = browser.contexts[0].new_page()
                    page.goto(last_url, wait_until="domcontentloaded")
                    time.sleep(3)
                    page.bring_to_front()
                    
                    # 保存当前URL
                    save_last_chat_url(page.url)
                    
                    if args.reply:
                        reply_message(page, args.reply)
                    
                    browser.close()
                    return
                else:
                    safe_print("没有找到最后访问的旺旺页记录")
                    browser.close()
                    return
            
            # 打开指定的旺旺页
            if args.open is not None:
                page = open_chat_page(browser, args.open)
                if not page:
                    browser.close()
                    return
                
                # 保存当前URL
                save_last_chat_url(page.url)
                
                # 搜索联系人
                if args.search:
                    search_contacts(page, args.search)
                
                # 查看聊天记录
                if args.history:
                    get_chat_history(page)
                
                # 回复消息
                if args.reply:
                    reply_message(page, args.reply)
                
                browser.close()
                return
            
            # 如果没有指定打开页面，但有其他操作
            if args.search or args.history or args.reply:
                chat_pages = get_all_chat_pages(browser)
                if not chat_pages:
                    safe_print("错误: 没有打开的旺旺聊天页")
                    safe_print("请先使用 --open 打开一个聊天页")
                    browser.close()
                    return
                
                # 使用第一个聊天页
                page = chat_pages[0]['page_obj']
                page.bring_to_front()
                time.sleep(2)
                
                if args.search:
                    search_contacts(page, args.search)
                
                if args.history:
                    get_chat_history(page)
                
                if args.reply:
                    reply_message(page, args.reply)
                
                browser.close()
                return
            
        finally:
            try:
                browser.close()
            except:
                pass

if __name__ == "__main__":
    main()
