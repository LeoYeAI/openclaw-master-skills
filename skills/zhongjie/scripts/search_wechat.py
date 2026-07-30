#!/usr/bin/env python3
"""
微信公众号文章搜索工具

通过搜狗微信搜索（weixin.sogou.com）获取微信公众号文章。
支持 --fetch-content 使用 Playwright 无头浏览器抓取文章正文。

Usage:
    python3 search_wechat.py --keyword "效率工具"
    python3 search_wechat.py --keyword "AI工具推荐" --limit 20
    python3 search_wechat.py --keyword "独立开发" --resolve-url
    python3 search_wechat.py --keyword "独立开发" --resolve-url --fetch-content
    python3 search_wechat.py --keywords "效率工具" "AI产品" --limit 10
    python3 search_wechat.py --fetch-content --url "https://mp.weixin.qq.com/s/xxx"

依赖（仅 --fetch-content 需要）：
    pip install playwright && python -m playwright install chromium
"""

import argparse
import asyncio
import gzip
import html
import html.parser
import json
import os
import random
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
import zlib
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import SEARCH_RESULTS_DIR, ensure_dirs

RESULT_FILE = os.path.join(SEARCH_RESULTS_DIR, "wechat_results.txt")

DEFAULT_KEYWORDS = ["效率工具推荐", "独立开发 产品", "AI工具 推荐"]

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/123.0.0.0 Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
]

BASE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Host": "weixin.sogou.com",
    "Referer": "https://weixin.sogou.com/",
}

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


def _random_ua():
    return random.choice(USER_AGENTS)


def _decompress(data, encoding):
    """解压 HTTP 响应体。"""
    if not encoding:
        return data
    enc = encoding.lower()
    try:
        if "gzip" in enc:
            return gzip.decompress(data)
        if "deflate" in enc:
            return zlib.decompress(data)
        if "br" in enc:
            import brotli  # type: ignore
            return brotli.decompress(data)
    except Exception:
        pass
    return data


def _http_get(url, extra_headers=None, timeout=30, retries=1):
    """通用 GET 请求，返回 (status, headers, body_bytes)。"""
    headers = {**BASE_HEADERS, "User-Agent": _random_ua()}
    if extra_headers:
        headers.update(extra_headers)

    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout, context=_ssl_ctx) as resp:
                raw = resp.read()
                body = _decompress(raw, resp.headers.get("Content-Encoding", ""))
                return resp.status, dict(resp.headers), body
        except Exception as e:
            if attempt >= retries:
                raise
            time.sleep(0.3 + attempt * 0.3)
    raise RuntimeError(f"Request failed: {url}")


def _http_get_text(url, extra_headers=None, timeout=30, retries=1):
    """GET 请求返回文本。"""
    status, headers, body = _http_get(url, extra_headers, timeout, retries)
    return body.decode("utf-8", errors="replace")


# ── Cookie 获取 ──────────────────────────────────────────────

def _extract_cookies(resp_headers):
    """从响应头提取 Set-Cookie。"""
    cookies = []
    for key, val in resp_headers.items():
        if key.lower() == "set-cookie":
            cookie_val = val.split(";")[0]
            if cookie_val:
                cookies.append(cookie_val)
    return "; ".join(cookies)


def get_sogou_cookie():
    """从搜狗视频页获取 cookie，用于后续请求。"""
    try:
        req = urllib.request.Request(
            "https://v.sogou.com/v?ie=utf8&query=&p=40030600",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "User-Agent": _random_ua(),
            },
        )
        with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
            cookie_str = _extract_cookies(dict(resp.headers))
            cookie_obj = {}
            for part in cookie_str.split("; "):
                if "=" in part:
                    k, _, v = part.partition("=")
                    cookie_obj[k.strip()] = v.strip()
            return cookie_str, cookie_obj
    except Exception:
        return "", {}


# ── HTML 解析 ────────────────────────────────────────────────

def _unescape(text):
    """HTML 实体解码 + 去除多余空白。"""
    return html.unescape(text).strip()


class _SogouSearchParser(html.parser.HTMLParser):
    """从搜狗微信搜索结果页提取文章列表（纯标准库实现）。"""

    def __init__(self, max_results):
        super().__init__()
        self.max_results = max_results
        self.articles = []

        self._in_news_list = False
        self._in_li = False
        self._in_h3 = False
        self._in_h3_a = False
        self._in_txt_info = False
        self._in_s_p = False
        self._in_source_span = False
        self._in_s2 = False
        self._in_script = False

        self._current = {}
        self._h3_a_href = ""
        self._text_buf = []

    def handle_starttag(self, tag, attrs):
        if len(self.articles) >= self.max_results:
            return
        attr = dict(attrs)
        cls = attr.get("class", "")

        if tag == "ul" and "news-list" in cls:
            self._in_news_list = True
            return

        if not self._in_news_list:
            return

        if tag == "li":
            self._in_li = True
            self._current = {
                "title": "", "url": "", "summary": "",
                "datetime": "", "date_text": "", "date_description": "", "source": "",
            }

        if self._in_li:
            if tag == "h3":
                self._in_h3 = True
            if self._in_h3 and tag == "a":
                self._in_h3_a = True
                href = attr.get("href", "")
                if href.startswith("/"):
                    href = f"https://weixin.sogou.com{href}"
                self._h3_a_href = href
                self._text_buf = []

            if tag == "p" and "txt-info" in cls:
                self._in_txt_info = True
                self._text_buf = []

            if tag == "div" and "s-p" in cls:
                self._in_s_p = True

            if self._in_s_p:
                if tag == "span" and "all-time-y2" in cls:
                    self._in_source_span = True
                    self._text_buf = []
                if tag == "a" and "account" in cls:
                    self._in_source_span = True
                    self._text_buf = []
                if tag == "span" and "s2" in cls:
                    self._in_s2 = True
                    self._text_buf = []

            if tag == "script":
                self._in_script = True
                self._text_buf = []

    def handle_endtag(self, tag):
        if len(self.articles) >= self.max_results:
            return

        if tag == "ul" and self._in_news_list:
            self._in_news_list = False
            return

        if not self._in_news_list:
            return

        if tag == "a" and self._in_h3_a:
            self._in_h3_a = False
            self._current["title"] = _unescape("".join(self._text_buf))
            self._current["url"] = self._h3_a_href

        if tag == "h3" and self._in_h3:
            self._in_h3 = False

        if tag == "p" and self._in_txt_info:
            self._in_txt_info = False
            self._current["summary"] = _unescape("".join(self._text_buf))

        if tag == "span" and self._in_source_span:
            self._in_source_span = False
            text = _unescape("".join(self._text_buf))
            if text:
                self._current["source"] = text

        if tag == "span" and self._in_s2:
            self._in_s2 = False

        if tag == "script" and self._in_script and self._in_s_p:
            self._in_script = False
            script_text = "".join(self._text_buf)
            ts_match = re.search(r"(\d{10})", script_text)
            if ts_match:
                ts = int(ts_match.group(1))
                dt = datetime.fromtimestamp(ts)
                self._current["datetime"] = dt.strftime("%Y-%m-%d %H:%M:%S")
                self._current["date_text"] = dt.strftime("%Y年%m月%d日")
                diff = datetime.now() - dt
                if diff.days > 0:
                    self._current["date_description"] = f"{diff.days}天前"
                else:
                    hours = diff.seconds // 3600
                    if hours > 0:
                        self._current["date_description"] = f"{hours}小时前"
                    else:
                        mins = diff.seconds // 60
                        self._current["date_description"] = f"{mins}分钟前" if mins > 0 else "刚刚"

        if tag == "div" and self._in_s_p:
            self._in_s_p = False

        if tag == "li" and self._in_li:
            self._in_li = False
            if self._current.get("title"):
                self.articles.append(self._current)
            self._current = {}

    def handle_data(self, data):
        if self._in_h3_a or self._in_txt_info or self._in_source_span or self._in_script:
            self._text_buf.append(data)


def parse_articles_from_html(html_text, max_results):
    """解析搜狗微信搜索结果页 HTML，返回文章列表。"""
    parser = _SogouSearchParser(max_results)
    try:
        parser.feed(html_text)
    except Exception:
        pass
    return parser.articles


# ── URL 解析 ─────────────────────────────────────────────────

def _extract_redirect_url(html_text):
    """从搜狗跳转页提取真实微信文章 URL。"""
    m = re.search(
        r'<meta[^>]*http-equiv=["\']refresh["\'][^>]*content=["\']\\d+;\s*url=([^"\']+)["\']',
        html_text, re.IGNORECASE,
    )
    if m:
        return m.group(1)

    for pattern in [
        r'location\.href\s*=\s*["\']([^"\']+)["\']',
        r'location\s*=\s*["\']([^"\']+)["\']',
        r'window\.location\s*=\s*["\']([^"\']+)["\']',
    ]:
        m = re.search(pattern, html_text, re.IGNORECASE)
        if m:
            return m.group(1)

    parts = re.findall(r"url\s*\+=\s*'([^']*)'", html_text)
    parts += re.findall(r'url\s*\+=\s*"([^"]*)"', html_text)
    if parts:
        joined = "".join(parts)
        if "mp.weixin.qq.com" in joined:
            return joined

    return None


def _get_real_url(sogou_url, cookie_obj, retries=3):
    """解析搜狗跳转链接 → 真实微信文章 URL。"""
    if "weixin.sogou.com" not in sogou_url:
        return sogou_url, True

    base_cookies = "ABTEST=7|1716888919|v1; IPLOC=CN5101; ariaDefaultTheme=default; ariaFixed=true; ariaReadtype=1; ariaStatus=false"
    snuid = cookie_obj.get("SNUID", "")
    cookie_str = f"{base_cookies}; SNUID={snuid}" if snuid else base_cookies

    extra = {"Cookie": cookie_str, "Host": "weixin.sogou.com"}

    for attempt in range(retries):
        try:
            req = urllib.request.Request(sogou_url, headers={
                **extra,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "User-Agent": _random_ua(),
            })
            opener = urllib.request.build_opener(
                urllib.request.HTTPSHandler(context=_ssl_ctx),
                _NoRedirectHandler(),
            )
            resp = opener.open(req, timeout=5)
            status = resp.status
            headers = dict(resp.headers)
            body = resp.read()

            if 300 <= status < 400:
                loc = headers.get("Location", headers.get("location", ""))
                if loc and "mp.weixin.qq.com" in loc:
                    return loc, True
                return sogou_url, False

            if status == 200:
                text = body.decode("utf-8", errors="replace")
                redirect = _extract_redirect_url(text)
                if redirect and "mp.weixin.qq.com" in redirect:
                    return redirect, True
                return sogou_url, False

        except Exception:
            pass
        if attempt < retries - 1:
            time.sleep(1)

    return sogou_url, False


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """阻止自动跟随重定向，手动处理 Location。"""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

    def http_error_301(self, req, fp, code, msg, headers):
        return fp
    http_error_302 = http_error_303 = http_error_307 = http_error_308 = http_error_301


def resolve_real_urls(articles):
    """批量解析文章的真实微信 URL。"""
    _, cookie_obj = get_sogou_cookie()
    print(f"  开始解析 {len(articles)} 篇文章的真实URL...", file=sys.stderr, flush=True)

    success = 0
    for i, art in enumerate(articles):
        print(f"  [{i+1}/{len(articles)}] {art['title'][:30]}...", file=sys.stderr, flush=True)
        real_url, ok = _get_real_url(art["url"], cookie_obj)
        art["url"] = real_url
        art["url_resolved"] = ok
        if ok and "weixin.sogou.com" not in real_url:
            success += 1
        if i < len(articles) - 1:
            time.sleep(0.5 + random.random())

    print(f"  URL 解析完成: 成功 {success}, 失败 {len(articles) - success}", file=sys.stderr, flush=True)
    return articles


# ── Playwright 文章正文抓取 ───────────────────────────────────

WECHAT_STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
delete navigator.__proto__.webdriver;
Object.defineProperty(navigator, 'plugins', {
    get: () => {
        const p = [
            { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
            { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
            { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' },
        ];
        p.length = 3;
        return p;
    }
});
Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en-US', 'en'] });
Object.defineProperty(navigator, 'language', { get: () => 'zh-CN' });
Object.defineProperty(navigator, 'platform', { get: () => 'MacIntel' });
"""


async def _launch_wechat_browser():
    """启动用于抓取微信文章的 Playwright 浏览器实例。"""
    from playwright.async_api import async_playwright

    pw = await async_playwright().start()
    browser = await pw.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
        ],
    )
    context = await browser.new_context(
        viewport={"width": 1280, "height": 900},
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
    )
    await context.add_init_script(WECHAT_STEALTH_JS)
    return pw, browser, context


async def _extract_article_from_page(page):
    """从已加载的微信文章页面中提取标题、作者、发布时间和正文。"""
    title = await page.evaluate("""
        () => {
            const el = document.getElementById('activity-name')
                || document.querySelector('.rich_media_title');
            return el ? el.innerText.trim() : '';
        }
    """)
    author = await page.evaluate("""
        () => {
            const el = document.getElementById('js_author_name')
                || document.getElementById('js_name')
                || document.querySelector('.rich_media_meta_text');
            return el ? el.innerText.trim() : '';
        }
    """)
    publish_time = await page.evaluate("""
        () => {
            const el = document.getElementById('publish_time');
            return el ? el.innerText.trim() : '';
        }
    """)
    content = await page.evaluate("""
        () => {
            const el = document.getElementById('js_content');
            if (!el) return '';
            const clone = el.cloneNode(true);
            clone.querySelectorAll('script, style, noscript').forEach(n => n.remove());
            return clone.innerText.trim();
        }
    """)
    return title, author, publish_time, content


async def _fetch_single_article(context, url, timeout_ms=30000):
    """用已有的浏览器 context 抓取单篇微信文章正文。

    Args:
        url: mp.weixin.qq.com 文章直链
    """
    page = await context.new_page()
    try:
        await page.route(
            re.compile(r"\.(png|jpg|jpeg|gif|svg|mp4|webm|ico|woff2?)(\?|$)", re.I),
            lambda route: route.abort(),
        )

        await page.goto(url, wait_until="networkidle", timeout=timeout_ms)

        try:
            await page.wait_for_selector("#js_content", state="visible", timeout=8000)
        except Exception:
            pass

        title, author, publish_time, content = await _extract_article_from_page(page)

        if not content:
            return {"error": "正文区域为空（可能文章已删除或需要付费阅读）"}

        content = re.sub(r"\n{3,}", "\n\n", content)

        return {
            "title": title,
            "author": author,
            "publish_time": publish_time,
            "content": content,
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        await page.close()


async def _fetch_article_content_async(url, timeout_ms=30000):
    """用 Playwright 无头浏览器抓取单篇微信文章的正文。

    Args:
        url: 微信文章 URL（mp.weixin.qq.com）或搜狗跳转链接

    Returns:
        dict: {"title", "author", "publish_time", "content"} 或包含 "error" 的 dict
    """
    from playwright.async_api import async_playwright

    pw, browser, context = await _launch_wechat_browser()
    try:
        return await _fetch_single_article(context, url, timeout_ms)
    finally:
        await context.close()
        await browser.close()
        await pw.stop()


def fetch_article_content(url, timeout_ms=30000):
    """同步包装：用 Playwright 抓取单篇微信文章正文。"""
    return asyncio.run(_fetch_article_content_async(url, timeout_ms))


async def _fetch_articles_content_async(articles, delay_range=(2.0, 5.0)):
    """批量抓取文章正文。复用同一个浏览器实例，减少开销。

    仅处理 URL 已解析为 mp.weixin.qq.com 的文章。
    """
    targets = [
        a for a in articles
        if a.get("url_resolved") and "mp.weixin.qq.com" in a.get("url", "")
    ]

    if not targets:
        print("  ⚠️ 没有已解析的微信文章URL可供抓取正文", file=sys.stderr, flush=True)
        return articles

    print(
        f"  开始抓取 {len(targets)} 篇文章正文（Playwright 无头浏览器）...",
        file=sys.stderr, flush=True,
    )

    pw, browser, context = await _launch_wechat_browser()
    try:
        success = 0
        for i, art in enumerate(targets):
            title_short = art["title"][:30]
            print(f"  [{i+1}/{len(targets)}] {title_short}...", file=sys.stderr, flush=True)

            result = await _fetch_single_article(context, art["url"])
            if "error" in result:
                print(f"    ⚠️ 抓取失败: {result['error']}", file=sys.stderr, flush=True)
                art["content"] = ""
            else:
                art["content"] = result.get("content", "")
                if result.get("author"):
                    art["author"] = result["author"]
                if result.get("publish_time"):
                    art["publish_time"] = result["publish_time"]
                content_len = len(art["content"])
                print(f"    ✅ 正文 {content_len} 字符", file=sys.stderr, flush=True)
                success += 1

            if i < len(targets) - 1:
                delay = random.uniform(*delay_range)
                await asyncio.sleep(delay)

        print(
            f"  正文抓取完成: 成功 {success}, 失败 {len(targets) - success}",
            file=sys.stderr, flush=True,
        )
    finally:
        await context.close()
        await browser.close()
        await pw.stop()

    return articles


def fetch_articles_content(articles, delay_range=(2.0, 5.0)):
    """同步包装：批量抓取文章正文。"""
    return asyncio.run(_fetch_articles_content_async(articles, delay_range))


# ── 搜索主流程 ───────────────────────────────────────────────

def search_wechat(keyword, max_results=10, resolve_url=False, fetch_content=False):
    """搜索微信公众号文章。

    Args:
        keyword: 搜索关键词
        max_results: 最大返回数（上限 50）
        resolve_url: 是否解析真实微信文章 URL
        fetch_content: 是否用 Playwright 抓取文章正文
                       （Playwright 自动跟随重定向，无需先 resolve_url）

    Returns:
        list[dict]: 文章列表
    """
    max_results = min(max_results, 50)
    articles = []
    page = 1
    pages_needed = (max_results + 9) // 10

    while len(articles) < max_results and page <= pages_needed:
        try:
            cookie_str, _ = get_sogou_cookie()
            encoded = urllib.parse.quote(keyword)
            url = f"https://weixin.sogou.com/weixin?query={encoded}&s_from=input&_sug_=n&type=2&page={page}&ie=utf8"

            extra = {}
            if cookie_str:
                extra["Cookie"] = cookie_str

            text = _http_get_text(url, extra_headers=extra, timeout=30, retries=1)

            remaining = max_results - len(articles)
            parsed = parse_articles_from_html(text, remaining)
            if not parsed:
                break
            articles.extend(parsed)
            page += 1

            if page <= pages_needed:
                time.sleep(0.5 + random.random())
        except Exception as e:
            print(f"  ⚠️ 请求第{page}页失败: {e}", file=sys.stderr)
            break

    result = articles[:max_results]

    if fetch_content and result:
        result = resolve_real_urls(result)
        result = fetch_articles_content(result)
    elif resolve_url and result:
        result = resolve_real_urls(result)

    return result


# ── 输出格式 ─────────────────────────────────────────────────

def format_as_text(all_articles, keywords_used):
    """将文章列表格式化为纯文本。"""
    lines = [
        f"微信公众号文章搜索结果 — 关键词: {', '.join(keywords_used)}",
        "=" * 60,
        "",
    ]

    seen = set()
    unique = []
    for a in all_articles:
        key = a.get("title", "")
        if key and key not in seen:
            seen.add(key)
            unique.append(a)

    for i, a in enumerate(unique, 1):
        title = a.get("title", "(无标题)")
        source = a.get("source", "")
        summary = a.get("summary", "")
        content = a.get("content", "")
        dt = a.get("datetime", "")
        desc = a.get("date_description", "")
        url = a.get("url", "")

        lines.append(f"#{i} {title}")
        meta_parts = []
        if source:
            meta_parts.append(f"公众号: {source}")
        if a.get("author"):
            meta_parts.append(f"作者: {a['author']}")
        if a.get("publish_time"):
            meta_parts.append(f"发布时间: {a['publish_time']}")
        elif dt:
            meta_parts.append(f"日期: {dt}")
        if desc:
            meta_parts.append(f"({desc})")
        if meta_parts:
            lines.append(f"  {'  '.join(meta_parts)}")
        if content:
            lines.append(f"  --- 正文 ({len(content)} 字) ---")
            lines.append(f"  {content}")
            lines.append(f"  --- 正文结束 ---")
        elif summary:
            if len(summary) > 200:
                summary = summary[:200] + "..."
            lines.append(f"  {summary}")
        if url:
            lines.append(f"  {url}")
        lines.append("")

    lines.append(f"共 {len(unique)} 篇文章（已去重）")
    return "\n".join(lines)


# ── CLI ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="微信公众号文章搜索（通过搜狗微信）")
    parser.add_argument("--keyword", type=str, default=None, help="搜索关键词（单个）")
    parser.add_argument("--keywords", nargs="+", default=None, help="多个搜索关键词")
    parser.add_argument("--limit", type=int, default=10, help="每个关键词的最大结果数（默认 10，上限 50）")
    parser.add_argument("--resolve-url", action="store_true", help="解析真实微信文章 URL（会额外请求，较慢）")
    parser.add_argument("--fetch-content", action="store_true", help="用 Playwright 抓取文章正文（需安装 playwright）")
    parser.add_argument("--url", type=str, default=None, help="直接抓取单篇微信文章正文（需 mp.weixin.qq.com URL）")
    parser.add_argument("--output", type=str, default=None, help="输出文件路径")
    args = parser.parse_args()

    ensure_dirs()

    # 直接抓取单篇文章模式
    if args.url:
        if "mp.weixin.qq.com" not in args.url:
            print("❌ --url 需要 mp.weixin.qq.com 的文章链接", file=sys.stderr)
            sys.exit(1)
        print(f"📖 抓取文章正文: {args.url[:80]}...", file=sys.stderr, flush=True)
        result = fetch_article_content(args.url)
        if "error" in result:
            print(f"❌ 抓取失败: {result['error']}", file=sys.stderr)
            sys.exit(1)
        output = (
            f"标题: {result['title']}\n"
            f"作者: {result['author']}\n"
            f"发布时间: {result['publish_time']}\n"
            f"正文长度: {len(result['content'])} 字\n"
            f"{'=' * 60}\n"
            f"{result['content']}\n"
        )
        print(output)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"\n📄 结果已保存到 {args.output}", file=sys.stderr)
        return

    if args.keyword:
        keywords = [args.keyword]
    elif args.keywords:
        keywords = args.keywords
    else:
        keywords = DEFAULT_KEYWORDS

    all_articles = []
    for kw in keywords:
        print(f"🔍 搜索微信公众号: {kw}...", file=sys.stderr, flush=True)
        arts = search_wechat(
            kw,
            max_results=args.limit,
            resolve_url=args.resolve_url,
            fetch_content=args.fetch_content,
        )
        print(f"  → 获取 {len(arts)} 篇文章", file=sys.stderr, flush=True)
        all_articles.extend(arts)
        if len(keywords) > 1:
            time.sleep(1 + random.random())

    if not all_articles:
        print("❌ 未获取到任何文章（搜狗可能触发了反爬验证）", file=sys.stderr)
        print("💡 建议: 稍后重试，或减少请求频率", file=sys.stderr)
        sys.exit(1)

    text = format_as_text(all_articles, keywords)

    output_file = args.output or RESULT_FILE
    ensure_dirs()
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)

    print(text)
    print(f"\n📄 结果已保存到 {output_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
