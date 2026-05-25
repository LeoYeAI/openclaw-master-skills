#!/usr/bin/env python3
"""
Fetch WeChat mp.weixin.qq.com article page and extract正文。

特点：
- **只输出 `id="js_content"` 正文**
- 如果页面里没有 `js_content`，会直接报错

用法（PowerShell）：
  python skill/wechatmp/fetch_article.py get '{"url":"https://mp.weixin.qq.com/s/xxx","out_content":"out/article.html"}'

带 Cookie（可提高成功率/完整性）：
  $env:WECHAT_MP_COOKIE="你的Cookie"
  python skill/wechatmp/fetch_article.py get '{"url":"https://mp.weixin.qq.com/s/xxx","out_html":"out/page.html","out_content":"out/article.html"}'

可选：输出封面（og:image）
  python skill/wechatmp/fetch_article.py get '{"url":"https://mp.weixin.qq.com/s/xxx","out_content":"out/article.html","out_cover_url":"out/og_image_url.txt"}'
"""

import json
import os
import re
import sys
from typing import Any, Dict, Optional, Tuple

import requests


def _json_out(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _normalize_local_path(user_path: str, field: str) -> Dict[str, Any]:
    if not user_path:
        return {"error": "invalid_param", "message": "field '%s' is empty" % field}
    if os.path.isabs(user_path):
        return {"error": "invalid_path", "message": "Absolute path is not allowed for '%s'" % field}
    norm = os.path.normpath(user_path)
    if norm.startswith("..") or norm == "..":
        return {"error": "invalid_path", "message": "Path traversal is not allowed for '%s'" % field}
    base = os.getcwd()
    full = os.path.join(base, norm)
    return {"error": None, "path": full, "relative": norm}


def _write_text_if_needed(path_rel: str, text: str, field: str) -> Optional[str]:
    if not path_rel:
        return None
    safe = _normalize_local_path(path_rel, field)
    if safe["error"]:
        return safe["message"]
    os.makedirs(os.path.dirname(safe["path"]) or ".", exist_ok=True)
    try:
        with open(safe["path"], "w", encoding="utf-8") as f:
            f.write(text)
        return None
    except Exception as e:
        return "Failed to write %s: %s" % (field, e)


_JS_CONTENT_DIV_RE = re.compile(
    r'<div[^>]*\bid\s*=\s*(["\'])js_content\1[^>]*>(?P<html>[\s\S]*?)</div>',
    re.IGNORECASE,
)


def _extract_js_content_div(page_html: str) -> Optional[str]:
    m = _JS_CONTENT_DIV_RE.search(page_html or "")
    if not m:
        return None
    return (m.group("html") or "").strip()


def _extract_meta_og_image(html_text: str) -> Optional[str]:
    m = re.search(
        r'<meta[^>]+property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
        html_text or "",
        flags=re.IGNORECASE,
    )
    if not m:
        return None
    return (m.group(1) or "").strip() or None


def _fetch(url: str, cookie: str, timeout: int = 25) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://mp.weixin.qq.com/",
        "Upgrade-Insecure-Requests": "1",
    }
    if cookie:
        headers["Cookie"] = cookie
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
    except Exception as e:
        return None, "request_failed: %s" % e, None
    # mp.weixin.qq.com 页面一般是 utf-8；requests 的 r.text 可能因猜测编码导致“整页错码”。
    try:
        text = (r.content or b"").decode("utf-8", errors="replace")
    except Exception:
        text = ""
    return text, None, r.status_code


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: fetch_article.py get '{\"url\":\"https://mp.weixin.qq.com/s/xxx\"}'", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1].strip().lower()
    raw = sys.argv[2] if len(sys.argv) >= 3 else ""
    if isinstance(raw, str) and raw.strip() == "-":
        raw = sys.stdin.read()
    try:
        req = json.loads(raw) if raw.strip() else {}
    except Exception as e:
        print("JSON parse error: %s" % e, file=sys.stderr)
        sys.exit(1)
    if not isinstance(req, dict):
        print("Error: JSON body must be an object.", file=sys.stderr)
        sys.exit(1)

    if cmd != "get":
        _json_out({"error": "unknown_command", "supported": ["get"]})
        sys.exit(1)

    url = str(req.get("url") or "").strip()
    page_html_path = str(req.get("page_html_path") or "").strip()
    if not url and not page_html_path:
        _json_out({"error": "missing_param", "message": "url or page_html_path is required"})
        sys.exit(1)

    cookie = str(req.get("cookie") or os.environ.get("WECHAT_MP_COOKIE", "")).strip()
    out_html = str(req.get("out_html") or "").strip()
    out_content = str(req.get("out_content") or "").strip()
    out_cover_url = str(req.get("out_cover_url") or "").strip()

    status: Optional[int] = None
    if page_html_path:
        safe = _normalize_local_path(page_html_path, "page_html_path")
        if safe["error"]:
            _json_out({"error": "invalid_path", "message": safe["message"]})
            sys.exit(1)
        try:
            with open(safe["path"], "r", encoding="utf-8") as f:
                page_html = f.read()
        except Exception as e:
            _json_out({"error": "read_failed", "message": "Failed to read page_html_path: %s" % e})
            sys.exit(1)
    else:
        page_html, err, status = _fetch(url, cookie)
        if err:
            _json_out({"error": "fetch_failed", "message": err})
            sys.exit(1)

    if out_html:
        werr = _write_text_if_needed(out_html, page_html or "", "out_html")
        if werr:
            _json_out({"error": "write_failed", "message": werr})
            sys.exit(1)

    if out_cover_url:
        og_image_url = _extract_meta_og_image(page_html or "")
        if not og_image_url:
            print("WARN: og:image not found in page.", file=sys.stderr)
        else:
            werr = _write_text_if_needed(out_cover_url, og_image_url, "out_cover_url")
            if werr:
                print("WARN: failed to write out_cover_url: %s" % werr, file=sys.stderr)

    # 只取 js_content（不回退）
    js_content = _extract_js_content_div(page_html or "")
    if not js_content:
        _json_out(
            {
                "error": "not_found",
                "message": "js_content not found in page. Try providing Cookie via WECHAT_MP_COOKIE / 'cookie'.",
                "status_code": status,
                "url": url,
            }
        )
        sys.exit(1)

    if out_content:
        werr = _write_text_if_needed(out_content, js_content, "out_content")
        if werr:
            _json_out({"error": "write_failed", "message": werr})
            sys.exit(1)

    # 按你要求：只输出 js_content 本体（不输出其它元信息）
    # Windows 控制台可能是 gbk，直接 write(str) 会因字符无法编码而报错；统一用 UTF-8 bytes 输出。
    sys.stdout.buffer.write(js_content.encode("utf-8"))


if __name__ == "__main__":
    main()

