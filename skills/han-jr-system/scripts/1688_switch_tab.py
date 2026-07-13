#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
切换 Chrome 里的 1688 聊天 tab（不弹新视窗）。
依赖: pip install playwright，Chrome --remote-debugging-port=9222

用法:
  python 1688_switch_tab.py              # 列出所有 1688 相关 tab
  python 1688_switch_tab.py 970171587332 # 切到 URL 含该 offerId 的 tab（杭菲那家）
  python 1688_switch_tab.py 杭菲         # 切到 URL 含「杭菲」的 tab
  python 1688_switch_tab.py baiyuanlong168
"""
import sys

def safe_print(*a, **k):
    def to_safe(s):
        return "".join(c if ord(c) < 128 else "?" for c in str(s))
    try:
        print(*a, **k)
    except (UnicodeEncodeError, UnicodeDecodeError):
        print(*[to_safe(x) for x in a], **k)

def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Need: pip install playwright")
        sys.exit(1)

    argv = sys.argv[1:]
    keyword = argv[0] if argv else None

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception:
            safe_print("Cannot connect to Chrome. Start with --remote-debugging-port=9222")
            sys.exit(1)
        try:
            pages = []
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    pages.append(pg)

            if not keyword:
                safe_print("1688-related tabs:")
                for i, pg in enumerate(pages):
                    u = pg.url or ""
                    if "1688.com" in u:
                        title = pg.title() or ""
                        safe_print(f"  [{i}] {u[:80]}...")
                        if title:
                            safe_print(f"      title: {title[:50]}")
                safe_print("Run: python 1688_switch_tab.py <offerId or keyword> to switch.")
                browser.close()
                return

            # 找 URL 或 title 包含 keyword 的 tab
            for pg in pages:
                u = pg.url or ""
                t = pg.title() or ""
                if "1688.com" in u and (keyword in u or keyword in t):
                    pg.bring_to_front()
                    safe_print("Switched to tab:", u[:70] + "...")
                    browser.close()
                    return

            safe_print(f"No tab matching '{keyword}' found.")
        finally:
            try:
                browser.close()
            except Exception:
                pass

if __name__ == "__main__":
    main()
