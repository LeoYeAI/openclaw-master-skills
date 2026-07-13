#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688 站内信/联系卖家：用现有 Chrome 标签页给指定卖家发消息，不弹新视窗。

聊天页 URL 格式：https://air.1688.com/app/ocms-fusion-components-1688/def_cbu_web_im/index.html?touid=cnalichnbaiyuanlong168&siteid=cnalichn&...

依赖: pip install playwright，Chrome 带 --remote-debugging-port=9222
用法:
  # 在当前已打开的聊天页发送消息（不切换聊天对象）
  python 1688_send_message.py --current "您好，请问这款支持混批吗？"
  python 1688_send_message.py "您好，想咨询一下"
  # 按卖家名搜索并打开该卖家聊天页再发消息（会切换聊天对象）
  python 1688_send_message.py "正欣硅塑胶" "您好，想咨询滴胶玩具的起订量和价格"
  # 直接打开聊天页 URL 并发消息
  python 1688_send_message.py --url "https://air.1688.com/...?touid=..." "您的消息"
  python 1688_send_message.py --touid baiyuanlong168 "您的消息"
  # 从商品详情页点击「客服」打开对话再发消息
  python 1688_send_message.py --offer 998521626969 "您的消息"
"""
import urllib.parse
import sys

def safe_print(*a, **k):
    def to_safe(s):
        return "".join(c if ord(c) < 128 else "?" for c in str(s))
    try:
        print(*a, **k)
    except (UnicodeEncodeError, UnicodeDecodeError):
        print(*[to_safe(x) for x in a], **k)

SEARCH_BASE = "https://s.1688.com/selloffer/offer_search.htm"
CHAT_BASE = "https://air.1688.com/app/ocms-fusion-components-1688/def_cbu_web_im/index.html"
OFFER_DETAIL_BASE = "https://detail.1688.com/offer/"


def get_page(browser):
    page = None
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if "1688.com" in (pg.url or ""):
                page = pg
                break
            if (pg.url or "").startswith("http") and not page:
                page = pg
        if page:
            break
    return page


def get_chat_tab(browser):
    """返回已经是 1688 旺旺聊天页的 tab（air.1688.com/.../def_cbu_web_im）"""
    for ctx in browser.contexts:
        for pg in ctx.pages:
            u = pg.url or ""
            if "air.1688.com" in u and "def_cbu_web_im" in u:
                return pg
    return None


def get_chat_frame(page):
    """返回包含聊天输入框和发送按钮的 frame（优先 iframe 内的核心聊天区）。"""
    # 先找主页面上的输入框
    for frame in [page] + list(page.frames):
        try:
            inp = frame.locator("pre[contenteditable='true']").first
            inp.wait_for(state="attached", timeout=1500)
            # 同一 frame 内最好也有「发送」
            send_btn = frame.locator("button:has-text('发送'), a:has-text('发送'), span:has-text('发送')").first
            send_btn.wait_for(state="attached", timeout=1000)
            return frame
        except Exception:
            continue
    # 退而求其次：只要有 contenteditable 的 frame
    for frame in [page] + list(page.frames):
        try:
            inp = frame.locator("pre[contenteditable='true']").first
            inp.wait_for(state="attached", timeout=1500)
            return frame
        except Exception:
            continue
    return None


def send_message_on_chat_page(page, message: str) -> bool:
    """在当前聊天页发送自定义消息：在聊天 iframe 内定位输入框、填入内容、点击发送。不切换聊天对象。"""
    page.set_default_timeout(12000)
    chat_frame = get_chat_frame(page)
    if not chat_frame:
        return False

    input_selectors = [
        "pre[contenteditable='true']",
        "pre.edit[contenteditable='true']",
        "[contenteditable='true']",
    ]
    send_selectors = [
        "button:has-text('发送')",
        "a:has-text('发送')",
        "span:has-text('发送')",
        "[class*='send']",
    ]

    inp = None
    for sel in input_selectors:
        try:
            inp = chat_frame.locator(sel).first
            inp.wait_for(state="visible", timeout=2000)
            break
        except Exception:
            continue
    if not inp:
        return False

    # 将输入框滚动到可见
    try:
        inp.evaluate("el => el.scrollIntoView({ block: 'nearest', behavior: 'instant' })")
        page.wait_for_timeout(200)
    except Exception:
        pass

    # 点击聚焦
    try:
        inp.click()
        page.wait_for_timeout(300)
    except Exception:
        pass

    # 清空后填入内容：contenteditable 用 JS 设置文本更可靠
    try:
        chat_frame.evaluate("""(o) => {
            const el = document.querySelector(o.sel);
            if (!el) return;
            el.focus();
            el.innerText = o.text;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        }""", {"sel": "pre[contenteditable='true']", "text": message})
        page.wait_for_timeout(400)
    except Exception:
        try:
            # 备用：剪贴板粘贴
            page.evaluate("t => navigator.clipboard.writeText(t)", message)
            page.wait_for_timeout(100)
            inp.press("Control+v")
            page.wait_for_timeout(400)
        except Exception:
            try:
                page.keyboard.type(message, delay=25)
                page.wait_for_timeout(400)
            except Exception:
                return False

    # 发送按钮滚动到可见并点击
    send_btn = None
    for sel in send_selectors:
        try:
            send_btn = chat_frame.locator(sel).first
            send_btn.wait_for(state="visible", timeout=1500)
            break
        except Exception:
            continue
    if not send_btn:
        try:
            page.keyboard.press("Enter")
        except Exception:
            pass
        page.wait_for_timeout(500)
        return True

    try:
        send_btn.evaluate("el => el.scrollIntoView({ block: 'nearest', behavior: 'instant' })")
        page.wait_for_timeout(200)
    except Exception:
        pass
    try:
        send_btn.click()
    except Exception:
        page.keyboard.press("Enter")
    page.wait_for_timeout(600)
    return True


def run_with_current_chat(message: str) -> None:
    """仅在当前已打开的聊天页发送消息，不切换标签页、不跳转 URL。"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Need: pip install playwright")
        sys.exit(1)
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception:
            safe_print("Cannot connect to Chrome. Start Chrome with: --remote-debugging-port=9222")
            sys.exit(1)
        try:
            page = get_chat_tab(browser) or get_page(browser)
            if not page:
                safe_print("No tab found.")
                browser.close()
                sys.exit(1)
            if "air.1688.com" not in (page.url or "") or "def_cbu_web_im" not in (page.url or ""):
                safe_print("Current tab is not a 1688 chat page. Open the chat page first.")
                browser.close()
                sys.exit(1)
            page.bring_to_front()
            page.wait_for_timeout(500)
            if send_message_on_chat_page(page, message):
                safe_print("Message sent on current chat page.")
            else:
                safe_print("Could not find chat input. Type manually:")
                safe_print(message)
        finally:
            try:
                browser.close()
            except Exception:
                pass


def run_with_chat_url(chat_url: str, message: str) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Need: pip install playwright")
        sys.exit(1)
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception:
            safe_print("Cannot connect to Chrome. Start Chrome with: --remote-debugging-port=9222")
            sys.exit(1)
        try:
            # 取一个 tab，并确保打开的是目标 chat_url（否则会发错人）
            page = get_chat_tab(browser) or get_page(browser)
            if not page:
                safe_print("No tab found.")
                browser.close()
                sys.exit(1)
            # 若当前页不是目标聊天（URL 不含同一 offerId/touid），则跳转
            cur = (page.url or "")
            if chat_url not in cur and "offerId=" in chat_url:
                offer_id = None
                if "offerId=" in chat_url:
                    for part in chat_url.split("&"):
                        if part.startswith("offerId="):
                            offer_id = part.split("=", 1)[1].split("&")[0]
                            break
                if not offer_id or offer_id not in cur:
                    page.goto(chat_url, wait_until="domcontentloaded")
                    page.wait_for_timeout(3500)
            elif chat_url not in cur:
                page.goto(chat_url, wait_until="domcontentloaded")
                page.wait_for_timeout(3500)
            else:
                page.bring_to_front()
                page.wait_for_timeout(500)
            if send_message_on_chat_page(page, message):
                safe_print("Message sent on chat page.")
            else:
                safe_print("Could not find chat input. Type manually:")
                safe_print(message)
            if sys.stdin.isatty():
                input("Press Enter to close connection...")
        finally:
            try:
                browser.close()
            except Exception:
                pass


def run_from_offer_page(offer_url_or_id: str, message: str) -> None:
    """从商品详情页打开，点击「客服」开启与工厂对话，再发消息。"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Need: pip install playwright")
        sys.exit(1)
    offer_url = offer_url_or_id if offer_url_or_id.startswith("http") else f"{OFFER_DETAIL_BASE}{offer_url_or_id}.html"
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception:
            safe_print("Cannot connect to Chrome. Start Chrome with: --remote-debugging-port=9222")
            sys.exit(1)
        try:
            page = get_page(browser)
            if not page:
                safe_print("No tab found.")
                browser.close()
                sys.exit(1)
            page.set_default_timeout(12000)
            page.goto(offer_url, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            # 点击「客服」链接：<a class="action-link customer-service" data-click="咨询客服"><od-text i18n="wangwang">客服</od-text></a>
            clicked = False
            for sel in [
                "a.action-link.customer-service",
                "a[data-click='咨询客服']",
                "a:has-text('客服')",
                ".customer-service",
            ]:
                try:
                    page.locator(sel).first.click(timeout=3000)
                    clicked = True
                    break
                except Exception:
                    continue
            if not clicked:
                safe_print("Could not find 客服 link on offer page.")
                browser.close()
                sys.exit(1)
            page.wait_for_timeout(4000)
            # 聊天可能在新 tab 或本页侧栏/iframe
            chat_page = get_chat_tab(browser)
            if chat_page:
                chat_page.bring_to_front()
                page.wait_for_timeout(1500)
                if send_message_on_chat_page(chat_page, message):
                    safe_print("Message sent after opening chat from offer page.")
                else:
                    safe_print("Chat opened but could not send. Type manually:")
                    safe_print(message)
            else:
                if send_message_on_chat_page(page, message):
                    safe_print("Message sent (chat in same page).")
                else:
                    safe_print("Chat may have opened in panel. Type manually:")
                    safe_print(message)
            if sys.stdin.isatty():
                input("Press Enter to close connection...")
        finally:
            try:
                browser.close()
            except Exception:
                pass


def run(seller_name: str, message: str) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Need: pip install playwright")
        sys.exit(1)

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception:
            safe_print("Cannot connect to Chrome. Start Chrome with: --remote-debugging-port=9222")
            sys.exit(1)

        try:
            page = get_page(browser)
            if not page:
                safe_print("No tab found. Open Chrome with a tab and run again.")
                browser.close()
                sys.exit(1)

            page.set_default_timeout(12000)
            # 搜索卖家名（店铺/公司名）
            kw = urllib.parse.quote(seller_name)
            search_url = f"{SEARCH_BASE}?keywords={kw}"
            page.goto(search_url, wait_until="domcontentloaded")
            page.wait_for_timeout(4000)

            # 点第一个商品或店铺链接进入（便于出现「联系卖家」）
            try:
                link = page.locator(
                    "a[href*='offer'], a[href*='detail'], a[href*='shop']"
                ).first
                link.wait_for(state="visible", timeout=5000)
                link.click()
                page.wait_for_timeout(3000)
            except Exception:
                pass

            # 找「联系卖家」「联系」「旺旺」「发消息」并点击
            contact_clicked = False
            for sel in [
                "a:has-text('联系卖家')",
                "a:has-text('联系')",
                "span:has-text('联系卖家')",
                "span:has-text('联系')",
                "button:has-text('联系')",
                "[class*='contact']",
                "[class*='wangwang']",
                "a[href*='im']",
            ]:
                try:
                    btn = page.locator(sel).first
                    btn.click(timeout=3000)
                    contact_clicked = True
                    page.wait_for_timeout(2500)
                    break
                except Exception:
                    continue

            if not contact_clicked:
                safe_print("Could not find contact button. You may need to click it manually in the 1688 tab.")
                safe_print("Then run again, or type your message in the chat that opened.")

            # 若当前已是聊天页 (air.1688.com)，直接发消息
            if "air.1688.com" in (page.url or "") and "def_cbu_web_im" in (page.url or ""):
                if send_message_on_chat_page(page, message):
                    safe_print("Message sent on chat page.")
                else:
                    safe_print("Type manually:")
                    safe_print(message)
                if sys.stdin.isatty():
                    input("Press Enter to close connection...")
                return

            # 找聊天输入框并填写、发送（网页版旺旺/站内信）
            try:
                inp = page.locator(
                    "textarea[placeholder*='输入'], textarea[placeholder*='消息'], "
                    "input[placeholder*='输入'], .message-input textarea, [contenteditable='true']"
                ).first
                inp.wait_for(state="visible", timeout=5000)
                inp.fill(message)
                page.wait_for_timeout(500)
                send_btn = page.locator(
                    "button:has-text('发送'), button:has-text('Send'), "
                    ".send-btn, [class*='send']"
                ).first
                try:
                    send_btn.click(timeout=2000)
                    safe_print("Message sent (or sent button clicked). Check the 1688 chat.")
                except Exception:
                    inp.press("Enter")
                    safe_print("Message entered and Enter pressed. Check the 1688 chat.")
            except Exception:
                safe_print("Chat input not found. Please type your message in the 1688 chat window:")
                safe_print(message)

            if sys.stdin.isatty():
                input("Press Enter to close connection...")
        finally:
            try:
                browser.close()
            except Exception:
                pass


def main():
    argv = sys.argv[1:]
    if len(argv) >= 1 and argv[0] == "--current":
        message = " ".join(argv[1:]) if len(argv) > 1 else input("Message: ").strip() or "您好，想咨询一下产品。"
        run_with_current_chat(message)
        return
    if len(argv) >= 2 and argv[0] == "--url":
        chat_url = argv[1]
        message = " ".join(argv[2:]) if len(argv) > 2 else input("Message: ").strip() or "您好，想咨询一下产品。"
        run_with_chat_url(chat_url, message)
        return
    if len(argv) >= 2 and argv[0] == "--touid":
        touid = argv[1]
        message = " ".join(argv[2:]) if len(argv) > 2 else input("Message: ").strip() or "您好，想咨询一下产品。"
        chat_url = f"{CHAT_BASE}?touid=cnalichn{touid}&siteid=cnalichn&status=1&portalId=&gid=&itemsId="
        run_with_chat_url(chat_url, message)
        return
    if len(argv) >= 2 and argv[0] == "--offer":
        offer = argv[1]
        message = " ".join(argv[2:]) if len(argv) > 2 else input("Message: ").strip() or "您好，想咨询一下产品。"
        run_from_offer_page(offer, message)
        return
    args = [a for a in argv if not a.startswith("--")]
    # 仅一条消息且无 --url/--touid/--offer：在当前聊天页发送，不切换对象
    if len(args) == 1:
        run_with_current_chat(args[0])
        return
    if len(args) < 2:
        safe_print("Usage: python 1688_send_message.py --current \"message\"   # send in current chat (no switch)")
        safe_print("       python 1688_send_message.py \"message\"             # same as --current")
        safe_print("       python 1688_send_message.py <seller_name> [message]")
        safe_print("       python 1688_send_message.py --url <chat_page_url> [message]")
        safe_print("       python 1688_send_message.py --touid <seller_id> [message]")
        safe_print("       python 1688_send_message.py --offer <detail_url_or_offer_id> [message]")
        safe_print('Example: python 1688_send_message.py "您好，请问支持混批吗？"')
        sys.exit(1)
    seller_name = args[0]
    message = " ".join(args[1:])
    run(seller_name, message)


if __name__ == "__main__":
    main()
