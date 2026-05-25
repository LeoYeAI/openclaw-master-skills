"""去哪儿登录自动化测试

测试去哪儿登录流程，包括：
1. 检查登录状态
2. 导航到登录页面
3. 分析页面结构
4. 测试手机号输入
5. 测试获取验证码按钮
"""

from __future__ import annotations

import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qvxianjiuguo.chrome_launcher import ensure_chrome, has_display
from qvxianjiuguo.xhs.cdp import Browser
from qvxianjiuguo.flight.platforms import get_platform_handler


def main():
    print("=" * 60)
    print("去哪儿登录自动化测试")
    print("=" * 60)
    
    # 1. 确保 Chrome 运行
    print("\n[1] 启动 Chrome...")
    if not ensure_chrome(port=9222, headless=not has_display()):
        print("❌ 无法启动 Chrome")
        return
    
    browser = Browser(host="127.0.0.1", port=9222)
    browser.connect()
    page = browser.get_or_create_page()
    
    # 2. 获取处理器
    print("\n[2] 获取去哪儿处理器...")
    handler = get_platform_handler("qunar")
    if not handler:
        print("❌ 无法获取处理器")
        return
    
    # 3. 导航到登录页面
    print(f"\n[3] 导航到登录页面: {handler.login_url}")
    page.navigate(handler.login_url)
    page.wait_for_load()
    time.sleep(5)  # 增加等待时间
    print("✓ 已到达登录页面")
    
    # 4. 获取页面原始 HTML
    print("\n[4] 获取页面内容...")
    html_content = page.evaluate("() => document.documentElement.outerHTML")
    print(f"页面 HTML 长度: {len(html_content) if html_content else 0}")
    
    if html_content and len(html_content) < 1000:
        print(f"页面内容: {html_content[:500]}")
    
    # 5. 分析页面结构
    print("\n[5] 分析页面结构...")
    
    page_info = page.evaluate("""
        () => {
            const info = {
                title: document.title,
                url: window.location.href,
                bodyText: document.body ? document.body.innerText.substring(0, 500) : '',
                inputs: [],
                buttons: [],
                allClickable: []
            };
            
            // 获取所有输入框
            document.querySelectorAll('input').forEach(el => {
                info.inputs.push({
                    type: el.type,
                    placeholder: el.placeholder,
                    name: el.name,
                    id: el.id,
                    className: el.className
                });
            });
            
            // 获取所有按钮
            document.querySelectorAll('button, a.btn, div[role="button"], span[role="button"]').forEach(el => {
                const text = el.innerText || el.value || '';
                if (text.trim()) {
                    info.buttons.push({
                        text: text.trim().substring(0, 50),
                        className: el.className,
                        id: el.id
                    });
                }
            });
            
            // 获取所有可点击元素
            document.querySelectorAll('a, button, div[onclick], span[onclick]').forEach(el => {
                const text = el.innerText || '';
                if (text.includes('登录') || text.includes('手机') || text.includes('验证码') || text.includes('获取')) {
                    info.allClickable.push({
                        tag: el.tagName,
                        text: text.trim().substring(0, 30),
                        className: el.className.substring(0, 50)
                    });
                }
            });
            
            return info;
        }
    """)
    
    print(f"\n页面标题: {page_info.get('title')}")
    print(f"当前URL: {page_info.get('url')}")
    print(f"\n页面文字内容预览:\n{page_info.get('bodyText')}")
    
    print(f"\n找到 {len(page_info.get('inputs', []))} 个输入框:")
    for i, inp in enumerate(page_info.get('inputs', [])[:10]):
        print(f"  [{i+1}] type={inp.get('type')}, placeholder={inp.get('placeholder')}")
    
    print(f"\n找到 {len(page_info.get('buttons', []))} 个按钮:")
    for i, btn in enumerate(page_info.get('buttons', [])[:15]):
        print(f"  [{i+1}] text={btn.get('text')}")
    
    print(f"\n找到 {len(page_info.get('allClickable', []))} 个相关可点击元素:")
    for i, el in enumerate(page_info.get('allClickable', [])):
        print(f"  [{i+1}] tag={el.get('tag')}, text={el.get('text')}")
    
    # 6. 尝试切换到手机登录
    print("\n[6] 尝试切换到手机登录...")
    result = handler.switch_to_phone_login(page)
    if result:
        print("✓ 已切换到手机登录")
    else:
        print("⚠️ 切换失败，可能默认就是手机登录")
    
    time.sleep(3)
    
    # 7. 再次分析页面
    print("\n[7] 切换后再次分析页面...")
    page_info2 = page.evaluate("""
        () => {
            const info = {
                inputs: [],
                buttons: []
            };
            
            document.querySelectorAll('input').forEach(el => {
                info.inputs.push({
                    type: el.type,
                    placeholder: el.placeholder,
                    name: el.name,
                    id: el.id,
                    className: el.className
                });
            });
            
            document.querySelectorAll('button, a, span, div').forEach(el => {
                const text = (el.innerText || el.value || '').trim();
                if (text.includes('获取') || text.includes('验证码') || text.includes('登录') || text.includes('发送')) {
                    info.buttons.push({
                        text: text.substring(0, 30),
                        tagName: el.tagName,
                        className: el.className.substring(0, 50)
                    });
                }
            });
            
            return info;
        }
    """)
    
    print(f"\n切换后找到 {len(page_info2.get('inputs', []))} 个输入框:")
    for i, inp in enumerate(page_info2.get('inputs', [])[:10]):
        print(f"  [{i+1}] type={inp.get('type')}, placeholder={inp.get('placeholder')}")
    
    print(f"\n切换后找到 {len(page_info2.get('buttons', []))} 个相关按钮:")
    for i, btn in enumerate(page_info2.get('buttons', [])):
        print(f"  [{i+1}] text={btn.get('text')}, tag={btn.get('tagName')}")
    
    print("\n" + "=" * 60)
    print("页面分析完成")
    print("=" * 60)
    
    browser.close_page(page)
    browser.close()


if __name__ == "__main__":
    main()