#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688 Supplier Search - Search Box Input Version (Fixed)
Uses search box input and properly extracts product information

IMPORTANT NOTES - 重要说明:
============================
1. 搜索方式:
   - 必须通过搜索框输入关键词
   - 不要通过URL参数直接搜索
   - 搜索框输入更稳定，不易触发反爬虫

2. 编码问题:
   - 输出必须使用UTF-8编码
   - 文件保存必须使用UTF-8编码
   - 否则会产生乱码

3. 反爬虫检测:
   - 真正的反爬虫页面会显示: "Sorry, we have detected unusual traffic from your network."
   - URL包含 "_____tmd_____" 不一定是反爬虫
   - 如果遇到滑块验证码，使用 slider_captcha.py 解决

4. 解决反爬虫:
   - 运行: python slider_captcha.py --selector "#nc_1_n1z" --distance 260
   - 解决后继续搜索

工作流程:
=========
1. 访问1688搜索页面
2. 找到搜索框（通过多个selector尝试）
3. 清空并输入关键词
4. 按Enter提交搜索（不要构造URL）
5. 等待结果加载
6. 提取产品信息
7. 保存到JSON文件（UTF-8编码）
"""

import sys
import io

# Force UTF-8 - 必须使用UTF-8，否则输出会产生乱码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import argparse
import json
import time

def safe_print(text):
    """安全打印，处理编码问题"""
    try:
        print(text)
    except:
        print(str(text).encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

def check_antibot(page):
    """
    检查是否触发反爬虫机制
    
    真正的反爬虫页面会包含以下文字：
    - "Sorry, we have detected unusual traffic from your network."
    - "您的访问过于频繁"
    
    如果页面上没有这句话，大概率不是反爬虫
    
    参数:
        page: Playwright page对象
    
    返回:
        (is_antibot, marker): 是否反爬虫，检测到的标记
    """
    try:
        page_content = page.content()
        antibot_markers = [
            "Sorry, we have detected unusual traffic",
            "unusual traffic from your network",
            "您的访问过于频繁",  # 中文反爬虫提示
            "访问频率过高",
        ]
        for marker in antibot_markers:
            if marker in page_content:
                return True, marker
        
        # 检查URL是否包含可疑模式
        if "_____tmd_____" in page.url:
            safe_print(f"WARNING: URL contains suspicious pattern: _____tmd_____")
            safe_print("This may indicate anti-bot protection or other error.")
            safe_print("If you see a slider captcha, run: python slider_captcha.py --selector '#nc_1_n1z' --distance 260")
        
        return False, None
    except Exception as e:
        safe_print(f"Error checking antibot: {e}")
        return False, None

def search_1688(keyword, num_results=5):
    """
    通过搜索框输入搜索1688供应商
    
    重要：不要通过URL参数直接搜索，必须通过搜索框输入
    
    参数:
        keyword: 搜索关键词
        num_results: 返回结果数量
    
    返回:
        产品列表，每个产品包含name, price, location, link
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        safe_print("Error: pip install playwright")
        sys.exit(1)
    
    results = []
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception as e:
            safe_print(f"Error: {e}")
            sys.exit(1)
        
        try:
            # Get page
            page = None
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    if "1688.com" in (pg.url or ""):
                        page = pg
                        break
                if page:
                    break
            
            if not page:
                page = browser.contexts[0].new_page()
            
            page.set_default_timeout(30000)
            
            # Step 1: Go to 1688 search page
            safe_print(f"Search: {keyword}")
            page.goto("https://s.1688.com/selloffer/offer_search.htm", wait_until="domcontentloaded")
            time.sleep(3)
            
            safe_print(f"Loaded: {(page.url or '')[:60]}")
            
            # Check for anti-bot
            is_antibot, marker = check_antibot(page)
            if is_antibot:
                safe_print(f"="*50)
                safe_print(f"WARNING: Anti-bot detected!")
                safe_print(f"Marker: {marker}")
                safe_print(f"="*50)
                safe_print("Please run the following command to solve the captcha:")
                safe_print("  python slider_captcha.py --selector '#nc_1_n1z' --distance 260")
                safe_print("="*50)
                browser.close()
                sys.exit(1)
            
            # Step 2: Find and clear search box
            # 按优先级尝试多个selector
            search_selectors = [
                'input[placeholder*="搜索"]',
                'input[type="text"]',
                '.search-input input',
                '#search-input',
                'input[name="keywords"]'
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_box = page.query_selector(selector)
                    if search_box:
                        safe_print(f"Found search box: {selector}")
                        break
                except:
                    continue
            
            if not search_box:
                safe_print("Error: Could not find search box")
                # Take screenshot for debugging
                try:
                    page.screenshot(path=f"debug_{keyword}.png")
                    safe_print(f"Screenshot saved: debug_{keyword}.png")
                except:
                    pass
                browser.close()
                sys.exit(1)
            
            # Step 3: Clear and input keyword
            search_box.click()
            search_box.fill("")  # Clear first
            time.sleep(0.5)
            search_box.fill(keyword)
            safe_print(f"Input keyword: {keyword}")
            time.sleep(1)
            
            # Step 4: Submit search (press Enter)
            # 必须通过搜索框提交，不要构造URL
            search_box.press("Enter")
            safe_print("Submitted search")
            
            # Step 5: Wait for results to load
            time.sleep(5)
            
            safe_print(f"Result URL: {(page.url or '')[:80]}")
            
            # Check for anti-bot again
            is_antibot, marker = check_antibot(page)
            if is_antibot:
                safe_print(f"="*50)
                safe_print(f"WARNING: Anti-bot detected after search!")
                safe_print(f"Marker: {marker}")
                safe_print(f"="*50)
                safe_print("Please run the following command to solve the captcha:")
                safe_print("  python slider_captcha.py --selector '#nc_1_n1z' --distance 260")
                safe_print("="*50)
                browser.close()
                sys.exit(1)
            
            # Step 6: Extract product information using JavaScript
            products = page.evaluate("""() => {
                const results = [];
                
                // Find all elements that contain price info (likely product cards)
                const allElements = document.querySelectorAll('*');
                const productCards = [];
                
                for (const el of allElements) {
                    // Check if element has price-related class or content
                    const text = el.textContent || '';
                    const hasPrice = text.includes('¥') || text.includes('元') || /\\d+\\.\\d+/.test(text);
                    const className = el.className || '';
                    const isPriceElement = typeof className === 'string' && (className.includes('price') || className.includes('Price'));
                    
                    if (hasPrice && isPriceElement) {
                        // Find parent that might be a product card
                        let parent = el.parentElement;
                        for (let i = 0; i < 5 && parent; i++) {
                            const parentText = parent.textContent || '';
                            if (parentText.length > 50 && parentText.length < 500) {
                                // This might be a product card
                                if (!productCards.includes(parent)) {
                                    productCards.push(parent);
                                }
                                break;
                            }
                            parent = parent.parentElement;
                        }
                    }
                }
                
                // Extract info from each card
                for (const card of productCards.slice(0, 10)) {
                    const product = {};
                    
                    // Get all text
                    const fullText = card.textContent || '';
                    
                    // Find title (usually the longest text that's not price)
                    const textNodes = [];
                    const walk = (node) => {
                        if (node.nodeType === 3) { // Text node
                            const text = node.textContent.trim();
                            if (text.length > 5 && text.length < 100) {
                                textNodes.push(text);
                            }
                        }
                        for (const child of node.childNodes) {
                            walk(child);
                        }
                    };
                    walk(card);
                    
                    // Title is usually the longest non-price text
                    const nonPriceTexts = textNodes.filter(t => !t.includes('¥') && !/^\\d/.test(t));
                    if (nonPriceTexts.length > 0) {
                        product.title = nonPriceTexts.sort((a, b) => b.length - a.length)[0];
                    }
                    
                    // Find price
                    const priceMatch = fullText.match(/[¥￥]\\s*([\\d,]+(?:\\.\\d+)?)/);
                    if (priceMatch) {
                        product.price = '¥' + priceMatch[1];
                    }
                    
                    // Find link
                    const linkEl = card.querySelector('a[href]');
                    if (linkEl) {
                        product.link = linkEl.getAttribute('href');
                    }
                    
                    if (product.title) {
                        results.push(product);
                    }
                }
                
                return results;
            }""")
            
            safe_print(f"Found {len(products)} products")
            
            for i, p in enumerate(products[:num_results], 1):
                title = p.get('title', 'Unknown')
                price = p.get('price', 'Unknown')
                link = p.get('link', '')
                
                results.append({
                    'name': title.strip() if title else 'Unknown',
                    'price': price.strip() if price else 'Unknown',
                    'location': 'Unknown',
                    'link': link if link else f'https://detail.1688.com/offer/{i}.html'
                })
            
            browser.close()
            
        except Exception as e:
            safe_print(f"Error: {e}")
            browser.close()
            sys.exit(1)
    
    return results

def main():
    parser = argparse.ArgumentParser(
        description='1688 Supplier Search - Search Box Input Version',
        epilog='''
示例:
  python search_box_v2.py --keyword "帽子" --num 5 --output hat.json
  python search_box_v2.py -k "外套" -n 10 -o coat.json

重要提示:
  - 必须通过搜索框输入，不要通过URL参数搜索
  - 输出使用UTF-8编码，避免乱码
  - 如果遇到反爬虫，运行: python slider_captcha.py --selector "#nc_1_n1z" --distance 260
        '''
    )
    parser.add_argument('--keyword', '-k', required=True, help='Search keyword')
    parser.add_argument('--num', '-n', type=int, default=5, help='Number of results (default: 5)')
    parser.add_argument('--output', '-o', default='suppliers.json', help='Output JSON file')
    args = parser.parse_args()
    
    safe_print("="*50)
    safe_print(f"1688 Search (Search Box): {args.keyword}")
    safe_print("="*50)
    
    results = search_1688(args.keyword, args.num)
    
    if results:
        safe_print(f"\nResults: {len(results)}")
        for i, r in enumerate(results, 1):
            title = r['name'][:50] if r['name'] else 'Unknown'
            price = r['price'] if r['price'] else 'Unknown'
            safe_print(f"{i}. {title} - {price}")
        
        # 必须使用UTF-8编码保存，否则会产生乱码
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        safe_print(f"\nSaved: {args.output}")
        return 0
    else:
        safe_print("\nNo results")
        return 1

if __name__ == "__main__":
    sys.exit(main())
