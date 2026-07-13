#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688 Slider CAPTCHA Solver - 滑块验证码解决工具

IMPORTANT: 反爬虫解决办法！！重要！！
=====================================
当1688检测到异常流量时，会显示滑块验证码。
使用此脚本模拟人类拖动行为解决验证码。

使用方法:
    python slider_captcha.py --target "滑块selector" --distance 260

示例:
    python slider_captcha.py --selector "#nc_1_n1z" --distance 260 --duration 1.5

常见滑块选择器:
    - #nc_1_n1z
    - .nc_iconfont.btn_slide
    - span[aria-label="滑块"]
    - [data-spm-anchor-id*="slide"]

注意:
    - 真正的反爬虫页面会显示: "Sorry, we have detected unusual traffic from your network."
    - URL包含 "_____tmd_____" 不一定是反爬虫
    - 解决验证码后页面会恢复正常
"""

import sys
import io

# Force UTF-8 - 必须使用UTF-8，否则输出会产生乱码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import argparse
import time
import random

def safe_print(text):
    """安全打印，处理编码问题"""
    try:
        print(text)
    except:
        print(str(text).encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

def solve_slider_captcha(selector, distance=260, duration=1.5):
    """
    模拟人类拖动滑块解决验证码
    
    工作原理:
    1. 定位滑块元素
    2. 计算起始和目标位置
    3. 分段拖动（模拟人类行为）
       - 使用缓动函数（smoothstep）模拟自然加速/减速
       - 添加随机抖动，更像人类操作
    4. 验证滑块是否消失
    
    参数:
        selector: 滑块元素的CSS选择器
        distance: 需要拖动的距离（像素）
        duration: 拖动持续时间（秒）
    
    返回:
        True: 成功解决验证码
        False: 解决失败
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
            # Get page
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
            
            # Check if this is actually an anti-bot page
            page_content = page.content()
            if "Sorry, we have detected unusual traffic" in page_content:
                safe_print("WARNING: Anti-bot page detected!")
            elif "_____tmd_____" in page.url:
                safe_print("WARNING: URL contains suspicious pattern, may be anti-bot")
            
            # Find slider element
            slider = page.query_selector(selector)
            if not slider:
                safe_print(f"Error: Could not find slider with selector: {selector}")
                safe_print("Trying alternative selectors...")
                
                # Try alternative selectors
                alt_selectors = [
                    ".nc_iconfont.btn_slide",
                    "span[aria-label='滑块']",
                    "[data-spm-anchor-id*='slide']",
                    ".btn_slide"
                ]
                
                for alt_sel in alt_selectors:
                    slider = page.query_selector(alt_sel)
                    if slider:
                        safe_print(f"Found slider with alternative selector: {alt_sel}")
                        break
                
                if not slider:
                    browser.close()
                    return False
            
            safe_print(f"Found slider element")
            
            # Get slider position
            box = slider.bounding_box()
            if not box:
                safe_print("Error: Could not get slider position")
                browser.close()
                return False
            
            safe_print(f"Slider position: x={box['x']}, y={box['y']}, width={box['width']}, height={box['height']}")
            
            # Calculate start and end positions
            start_x = box['x'] + box['width'] / 2
            start_y = box['y'] + box['height'] / 2
            end_x = start_x + distance
            end_y = start_y + random.randint(-5, 5)  # 添加一点随机Y轴偏移，更像人类
            
            safe_print(f"Dragging from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            
            # 方法2: 使用mouse事件（更像人类）
            page.mouse.move(start_x, start_y)
            time.sleep(0.2)
            page.mouse.down()
            time.sleep(0.1)
            
            # 模拟人类拖动：分段移动，速度不均匀
            steps = int(duration * 20)  # 每50ms一步
            current_x = start_x
            current_y = start_y
            
            for i in range(steps):
                progress = (i + 1) / steps
                # 使用缓动函数模拟人类拖动
                # smoothstep: progress * progress * (3 - 2 * progress)
                ease_progress = progress * progress * (3 - 2 * progress)
                
                target_x = start_x + (end_x - start_x) * ease_progress
                target_y = start_y + (end_y - start_y) * ease_progress
                
                # 添加随机抖动，更像人类操作
                jitter_x = random.randint(-2, 2)
                jitter_y = random.randint(-1, 1)
                
                page.mouse.move(target_x + jitter_x, target_y + jitter_y)
                time.sleep(duration / steps)
            
            # 最后精确位置
            page.mouse.move(end_x, end_y)
            time.sleep(0.1)
            page.mouse.up()
            
            safe_print("Drag completed")
            
            # 等待验证结果
            time.sleep(2)
            
            # 检查是否验证成功
            # 通常成功后页面会跳转或滑块消失
            new_slider = page.query_selector(selector)
            if new_slider:
                safe_print("Slider still exists, may need to retry")
                browser.close()
                return False
            else:
                safe_print("Slider disappeared, verification likely successful")
                browser.close()
                return True
            
        except Exception as e:
            safe_print(f"Error: {e}")
            browser.close()
            return False

def main():
    parser = argparse.ArgumentParser(
        description='1688 Slider CAPTCHA Solver - 滑块验证码解决工具',
        epilog='''
示例:
  python slider_captcha.py --selector "#nc_1_n1z" --distance 260 --duration 1.5
  python slider_captcha.py -s ".nc_iconfont.btn_slide" -d 260 -t 2.0

重要提示:
  - 真正的反爬虫页面会显示: "Sorry, we have detected unusual traffic from your network."
  - URL包含 "_____tmd_____" 不一定是反爬虫
  - 解决验证码后页面会恢复正常
        '''
    )
    parser.add_argument('--selector', '-s', default='#nc_1_n1z', 
                        help='Slider element CSS selector (default: #nc_1_n1z)')
    parser.add_argument('--distance', '-d', type=int, default=260, 
                        help='Drag distance in pixels (default: 260)')
    parser.add_argument('--duration', '-t', type=float, default=1.5, 
                        help='Drag duration in seconds (default: 1.5)')
    args = parser.parse_args()
    
    safe_print("="*50)
    safe_print("1688 Slider CAPTCHA Solver")
    safe_print("="*50)
    safe_print(f"Selector: {args.selector}")
    safe_print(f"Distance: {args.distance}px")
    safe_print(f"Duration: {args.duration}s")
    safe_print("="*50)
    
    success = solve_slider_captcha(args.selector, args.distance, args.duration)
    
    if success:
        safe_print("\n✓ CAPTCHA solved successfully")
        safe_print("You can now continue with your search or other operations.")
        return 0
    else:
        safe_print("\n✗ Failed to solve CAPTCHA")
        safe_print("Tips:")
        safe_print("  1. Check if the selector is correct")
        safe_print("  2. Try increasing --distance value")
        safe_print("  3. Try increasing --duration for slower drag")
        safe_print("  4. Make sure the page is fully loaded")
        return 1

if __name__ == "__main__":
    sys.exit(main())
