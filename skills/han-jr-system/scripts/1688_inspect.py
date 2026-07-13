#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查当前 1688 页面中的图像与文本（inspect）。
连接 Chrome 后抓取当前 tab 的图片元素和可见文本，便于观测页面结构。
依赖: pip install playwright，Chrome --remote-debugging-port=9222
用法: python 1688_inspect.py [可选：关键词，用于定位要检查的 tab]
"""
import sys
import json

def safe_print(*a, **k):
    def to_safe(s):
        return "".join(c if ord(c) < 128 else "?" for c in str(s))
    try:
        print(*a, **k)
    except (UnicodeEncodeError, UnicodeDecodeError):
        print(*[to_safe(x) for x in a], **k)


def get_page(browser, keyword=None):
    for ctx in browser.contexts:
        for pg in ctx.pages:
            u = pg.url or ""
            if "1688.com" not in u:
                continue
            if keyword and keyword not in u and keyword not in (pg.title() or ""):
                continue
            return pg
    for ctx in browser.contexts:
        if ctx.pages:
            return ctx.pages[-1]
    return None


def inspect_page(page):
    """在页面内执行 JS，收集图片、文本及位置，便于看图像与文本之间的布局。"""
    data = page.evaluate("""
        () => {
            const out = { images: [], texts: [], items: [] };
            // 图片：src, alt, 尺寸 + 位置
            document.querySelectorAll('img[src]').forEach(img => {
                const src = img.src || '';
                if (src.startsWith('data:') && src.length > 100) return;
                const rect = img.getBoundingClientRect();
                if (rect.width < 2 || rect.height < 2) return;
                const item = {
                    src: src.substring(0, 120),
                    alt: (img.alt || '').substring(0, 80),
                    width: Math.round(rect.width),
                    height: Math.round(rect.height),
                    x: Math.round(rect.left),
                    y: Math.round(rect.top)
                };
                out.images.push(item);
                out.items.push({ type: 'image', ...item });
            });
            // 带位置的文本块：从有 innerText 且可见的元素取
            const textEls = document.body.querySelectorAll('p, div, span, a, li, h1, h2, h3, label, button');
            const seen = new Set();
            textEls.forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.width < 15 || rect.height < 10) return;
                const text = (el.innerText || '').trim();
                if (text.length < 2 || text.length > 300) return;
                const key = text.substring(0, 50);
                if (seen.has(key)) return;
                seen.add(key);
                out.texts.push(text);
                out.items.push({
                    type: 'text',
                    text: text.substring(0, 100),
                    x: Math.round(rect.left),
                    y: Math.round(rect.top),
                    width: Math.round(rect.width),
                    height: Math.round(rect.height)
                });
            });
            out.texts = out.texts.slice(0, 60);
            // 按 y 再 x 排序，得到从上到下、从左到右的「图像与文本」顺序
            out.items.sort((a, b) => (a.y - b.y) || (a.x - b.x));
            out.items = out.items.slice(0, 80);
            return out;
        }
    """)
    return data


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Need: pip install playwright")
        sys.exit(1)

    keyword = sys.argv[1] if len(sys.argv) > 1 else None
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception:
            safe_print("Cannot connect to Chrome. Start with --remote-debugging-port=9222")
            sys.exit(1)
        try:
            page = get_page(browser, keyword)
            if not page:
                safe_print("No 1688 tab found.")
                browser.close()
                sys.exit(1)
            page.set_default_timeout(8000)
            data = inspect_page(page)
            safe_print("=== IMAGES ===")
            for i, im in enumerate(data.get("images") or []):
                safe_print(f"  [{i+1}] {im.get('alt') or '(no alt)'} | {im.get('width')}x{im.get('height')} | {im.get('src', '')[:60]}...")
            safe_print("")
            safe_print("=== TEXTS (sample) ===")
            for i, t in enumerate((data.get("texts") or [])[:25]):
                line = (t or "").replace("\n", " ")[:100]
                safe_print(f"  [{i+1}] {line}")
            safe_print("")
            safe_print("=== LAYOUT (image vs text, top-left order) ===")
            for i, it in enumerate((data.get("items") or [])[:20]):
                typ = it.get("type", "")
                x, y = it.get("x", 0), it.get("y", 0)
                if typ == "image":
                    safe_print(f"  [{i+1}] image @ ({x},{y}) {it.get('width')}x{it.get('height')}")
                else:
                    txt = (it.get("text") or "").replace("\\n", " ")[:50]
                    safe_print(f"  [{i+1}] text  @ ({x},{y}) {txt}")
            # 可选：写入 JSON 便于程序用
            out_path = __file__.replace(".py", "_out.json")
            try:
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                safe_print("")
                safe_print("Full data saved to:", out_path)
            except Exception:
                pass
        finally:
            try:
                browser.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()
