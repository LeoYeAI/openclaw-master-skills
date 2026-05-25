#!/usr/bin/env python3
"""
WeChat MP (公众号) Markdown -> HTML -> 草稿箱发布工具（draft）。

初期仅实现：
- Markdown 转 HTML
- HTML 基础美化（支持传 css 字符串 / 读取本地 css / 从网页抓取 <style>）
- 使用用户指定封面图并上传为永久素材得到 thumb_media_id
- 创建草稿（draft/add）
- 支持多个公众号账号批量同步（多 AppID/AppSecret）

后续可扩展：留言管理、数据统计等（独立脚本）。
文档：https://developers.weixin.qq.com/doc/subscription/api/
"""

import base64
import json
import os
import re
import sys
import time
import html as _html_stdlib
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional, Tuple

import requests


WECHAT_API_BASE = "https://api.weixin.qq.com"


def _json_out(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _cjk_score(s: str) -> int:
    score = 0
    for ch in s:
        o = ord(ch)
        # 常用 CJK & 全角符号
        if 0x4E00 <= o <= 0x9FFF:
            score += 2
        elif 0x3400 <= o <= 0x4DBF:
            score += 2
        elif 0xF900 <= o <= 0xFAFF:
            score += 1
        elif 0x3000 <= o <= 0x303F:
            score += 1
        elif 0xFF00 <= o <= 0xFFEF:
            score += 1
    return score


def _repair_mojibake(s: str) -> str:
    """
    尝试修复“乱码字符串”（常见于一次错误解码导致的 mojibake），例如：
    - 'æµ‹è¯•' -> '测试'

    仅在启发式判断“更像中文”时才替换，避免误伤正常英文/emoji。
    """
    if not s:
        return s
    # 如果已经出现大量 '?'，通常是上游编码已丢字（不可逆）；直接返回，让上层给出告警
    if s.count("?") >= 2 and _cjk_score(s) == 0:
        return s
    # 快速判断：如果已经有较多中文，则无需修复
    if _cjk_score(s) >= 2:
        return s
    # 尝试：把当前字符串当作 latin1 还原成 bytes，再按常见编码解回
    try:
        raw = s.encode("latin1", errors="strict")
    except Exception:
        return s

    candidates: List[str] = []
    for enc in ("utf-8", "gb18030"):
        try:
            candidates.append(raw.decode(enc))
        except Exception:
            pass
    if not candidates:
        return s

    best = max(candidates, key=_cjk_score)
    if _cjk_score(best) > _cjk_score(s):
        return best
    return s

def _normalize_local_path(user_path: str, field: str) -> Dict[str, Any]:
    """
    规范化并限制本地文件路径，只允许在当前工作目录及其子目录内读取/写入。
    禁止绝对路径和目录穿越（包含 ..），避免被恶意提示利用读取任意系统文件。
    """
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


def _read_text_input(req: Dict[str, Any], *, field_path: str, field_content: str, allowed_ext: Tuple[str, ...]) -> Tuple[Optional[str], Optional[str]]:
    """
    从 content 或 path 读取文本。path 必须是相对路径且扩展名受限。
    返回 (text, error_message)。
    """
    content = req.get(field_content)
    if content is not None and str(content) != "":
        return str(content), None

    path_raw = req.get(field_path)
    if not path_raw:
        return None, "Either '%s' or '%s' is required" % (field_content, field_path)

    safe = _normalize_local_path(str(path_raw).strip(), field_path)
    if safe["error"]:
        return None, safe["message"]

    rel = safe["relative"]
    _, ext = os.path.splitext(rel)
    if ext.lower() not in allowed_ext:
        return None, "Unsupported extension: %s (allowed: %s)" % (ext, ", ".join(allowed_ext))

    if not os.path.isfile(safe["path"]):
        return None, "File not found: %s" % rel

    try:
        with open(safe["path"], "rb") as f:
            raw = f.read()
        # Windows 上很多 md/html/css 文件可能是 GBK/GB18030。
        # 为避免“按 UTF-8 强解码导致的不可逆乱码”，这里按常见编码做降级解码。
        for enc in ("utf-8", "utf-8-sig", "gb18030"):
            try:
                return raw.decode(enc), None
            except Exception:
                pass
        # 最后兜底：用替换策略返回，至少不中断流程，并提示用户检查文件编码
        print(
            "WARN: cannot decode '%s' as utf-8/utf-8-sig/gb18030; used utf-8(errors=replace). Please save the file as UTF-8."
            % rel,
            file=sys.stderr,
        )
        return raw.decode("utf-8", errors="replace"), None
    except Exception as e:
        return None, "Failed to read file: %s" % e


def _fetch_text_url(url: str, *, cookie: str = "", timeout: int = 25, max_bytes: int = 2_500_000) -> Tuple[Optional[str], Optional[str]]:
    """
    下载 URL 文本（HTML/CSS 等）。限制：
    - 仅允许 http/https
    - 最大响应体 max_bytes
    """
    u = (url or "").strip()
    if not u:
        return None, "url is empty"
    p = urlparse(u)
    if p.scheme not in ("http", "https"):
        return None, "unsupported scheme: %s" % (p.scheme or "")

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
        r = requests.get(u, headers=headers, timeout=timeout, stream=True)
    except Exception as e:
        return None, "request_failed: %s" % e

    # 限制下载大小
    chunks: List[bytes] = []
    total = 0
    try:
        for chunk in r.iter_content(chunk_size=65536):
            if not chunk:
                continue
            chunks.append(chunk)
            total += len(chunk)
            if total > max_bytes:
                return None, "response too large (> %d bytes)" % max_bytes
    finally:
        try:
            r.close()
        except Exception:
            pass

    raw = b"".join(chunks)
    # 按常见编码尝试解码
    for enc in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return raw.decode(enc), None
        except Exception:
            pass
    return raw.decode("utf-8", errors="replace"), None


def _fetch_image_url(
    url: str,
    *,
    cookie: str = "",
    timeout: int = 25,
    max_bytes: int = 5_000_000,
) -> Tuple[Optional[bytes], Optional[str], Optional[str]]:
    """
    下载 URL 图片并限制大小。
    返回 (image_bytes, error_message, content_type)
    """
    u = (url or "").strip()
    if not u:
        return None, "url is empty", None
    p = urlparse(u)
    if p.scheme not in ("http", "https"):
        return None, "unsupported scheme: %s" % (p.scheme or ""), None

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "image/*,*/*;q=0.8",
        "Referer": "https://mp.weixin.qq.com/",
    }
    if cookie:
        headers["Cookie"] = cookie

    try:
        r = requests.get(u, headers=headers, timeout=timeout, stream=True)
    except Exception as e:
        return None, "request_failed: %s" % e, None

    content_type = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
    chunks: List[bytes] = []
    total = 0
    try:
        for chunk in r.iter_content(chunk_size=65536):
            if not chunk:
                continue
            chunks.append(chunk)
            total += len(chunk)
            if total > max_bytes:
                return None, "response too large (> %d bytes)" % max_bytes, content_type
    finally:
        try:
            r.close()
        except Exception:
            pass

    return b"".join(chunks), None, content_type or None


def _extract_meta_og_image(html_text: str) -> Optional[str]:
    m = re.search(
        r'<meta[^>]+property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
        html_text or "",
        flags=re.IGNORECASE,
    )
    if not m:
        return None
    return (m.group(1) or "").strip() or None


def _md_to_html(md: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        import markdown  # type: ignore
    except Exception:
        return None, "missing_dependency: pip install markdown"
    try:
        html = markdown.markdown(md, extensions=["extra", "tables", "fenced_code"])
        return html, None
    except Exception as e:
        return None, "markdown_error: %s" % e


_STYLE_TAG_RE = re.compile(r"<style[^>]*>(?P<css>[\s\S]*?)</style>", re.IGNORECASE)
_STYLE_TAG_BLOCK_RE = re.compile(r"<style[^>]*>[\s\S]*?</style>", re.IGNORECASE)

_BODY_RE = re.compile(r"<body[^>]*>(?P<body>[\s\S]*?)</body>", re.IGNORECASE)
_HTML_TAG_RE = re.compile(r"<html[^>]*>(?P<html>[\s\S]*?)</html>", re.IGNORECASE)
_HEAD_RE = re.compile(r"<head[^>]*>[\s\S]*?</head>", re.IGNORECASE)
_DOCTYPE_RE = re.compile(r"<!doctype[^>]*>", re.IGNORECASE)
_JS_CONTENT_DIV_RE = re.compile(
    r'<div[^>]*\bid\s*=\s*(["\'])js_content\1[^>]*>(?P<html>[\s\S]*?)</div>',
    re.IGNORECASE,
)


def _extract_body_if_full_html(html_text: str) -> str:
    """
    用户可能传入的是完整 HTML 文档（含 <html>/<head>/<body>）。
    微信上传 content 只需要 body 的内容；保留整页会引入额外标签，增加被清洗概率。
    """
    if not html_text:
        return ""
    m = _BODY_RE.search(html_text)
    if m:
        return m.group("body").strip()
    # 有些内容只有 <html> 没有 body，退化为去掉外层 html 标签
    m2 = _HTML_TAG_RE.search(html_text)
    if m2:
        s = m2.group("html")
    else:
        s = html_text

    # 尽量剔除 doctype / head（即使没有 body，也尽量只保留“正文”部分）
    s = _DOCTYPE_RE.sub("", s)
    s = _HEAD_RE.sub("", s)
    return s.strip()


def _extract_js_content_from_page(page_html: str) -> Optional[str]:
    m = _JS_CONTENT_DIV_RE.search(page_html or "")
    if not m:
        return None
    inner = (m.group("html") or "").strip()
    return inner or None


def _extract_inner_html_by_selector(html_text: str, selector: str) -> Optional[str]:
    """
    从 HTML 中按 CSS selector 精确提取“元素内部 HTML”（innerHTML）。

    返回 innerHTML 字符串；失败返回 None。
    说明：为了不强制引入依赖，这里仅在安装了 `beautifulsoup4` 时生效。
    """
    if not html_text or not selector:
        return None
    try:
        from bs4 import BeautifulSoup  # type: ignore
    except Exception:
        return None

    try:
        soup = BeautifulSoup(html_text, "html.parser")
        el = soup.select_one(selector)
        if not el:
            return None
        inner = el.decode_contents() if hasattr(el, "decode_contents") else str(el)
        inner = (inner or "").strip()
        return inner or None
    except Exception:
        return None


def _div_to_section(html_text: str) -> str:
    """
    公众号编辑器经常清洗/重排 div。为了减少“发布后 div 消失导致结构坍塌”，
    这里把多数 div 替换为语义更接近且相对更稳定的 section。
    注意：这不会保证 100% 保留，但能显著提升被保留的概率。
    """
    if not html_text:
        return ""
    # 仅处理标签名，不动属性
    html_text = re.sub(r"<\s*div(\s|>)", r"<section\1", html_text, flags=re.IGNORECASE)
    html_text = re.sub(r"</\s*div\s*>", r"</section>", html_text, flags=re.IGNORECASE)
    return html_text


_CLASS_ATTR_RE = re.compile(r'\bclass\s*=\s*(["\'])(?P<cls>[^"\']*)\1', re.IGNORECASE)


def _find_balanced_tag_block(s: str, *, tag: str, start_idx: int) -> Optional[Tuple[int, int]]:
    """
    从 start_idx 处的 `<tag ...>` 开始，按同名标签计数找到匹配的 `</tag>`。
    返回 (block_start, block_end_exclusive)。找不到则返回 None。
    """
    open_tag_re = re.compile(r"<\s*%s(\s|>)" % re.escape(tag), re.IGNORECASE)
    close_tag_re = re.compile(r"</\s*%s\s*>" % re.escape(tag), re.IGNORECASE)

    m0 = open_tag_re.search(s, start_idx)
    if not m0 or m0.start() != start_idx:
        return None

    i = start_idx
    depth = 0
    while i < len(s):
        mo = open_tag_re.search(s, i)
        mc = close_tag_re.search(s, i)
        if mc is None:
            return None
        if mo is not None and mo.start() < mc.start():
            depth += 1
            i = mo.end()
            continue
        depth -= 1
        i = mc.end()
        if depth == 0:
            return start_idx, i
    return None


def _extract_start_tag_and_inner(block: str, *, tag: str) -> Optional[Tuple[str, str]]:
    """
    给定完整块 `<tag ...> ... </tag>`，提取开始标签文本与 inner HTML。
    """
    start_m = re.match(r"<\s*%s\b(?P<attrs>[^>]*)>" % re.escape(tag), block, flags=re.IGNORECASE)
    if not start_m:
        return None
    start_tag_end = start_m.end()
    end_m = re.search(r"</\s*%s\s*>\s*$" % re.escape(tag), block, flags=re.IGNORECASE)
    if not end_m:
        return None
    inner = block[start_tag_end : end_m.start()]
    return block[:start_tag_end], inner


def _get_classes(start_tag: str) -> List[str]:
    m = _CLASS_ATTR_RE.search(start_tag)
    if not m:
        return []
    return [c for c in (m.group("cls") or "").split() if c]


def _looks_like_grid_container(classes: List[str]) -> bool:
    # 尽量通用：不写死业务名，只匹配常见 grid/row/col/card-list 等命名
    for c in classes:
        lc = c.lower()
        if lc == "grid" or "grid" in lc:
            return True
        if lc in ("card-grid", "cards", "cardlist", "grid-container"):
            return True
    return False


def _looks_like_card_item(classes: List[str]) -> bool:
    for c in classes:
        lc = c.lower()
        if lc == "card" or "card" in lc:
            return True
        if lc == "item" or "item" in lc:
            return True
        if lc in ("cell", "tile", "panel"):
            return True
    return False


def _sanitize_for_wechat(html_text: str) -> str:
    """
    尽量把 HTML 调整成公众号更能接受的形态。
    - 提取 body（若是整页 HTML）
    - 网格卡片结构降级为 table
    - div -> section（减少被清洗导致结构丢失）
    """
    s = _extract_body_if_full_html(html_text)
    s = _div_to_section(s)
    return s


def _extract_styles_from_url(style_url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    仅抓取网页中的 <style> 内联样式（不拉取外链 CSS），用于“拿过来样式”的轻量实现。
    """
    try:
        resp = requests.get(style_url, timeout=20, headers={"User-Agent": "OpenClaw-WeChatMP/1.0"})
    except Exception as e:
        return None, "request_failed: %s" % e
    if resp.status_code != 200:
        return None, "http_error: %s" % resp.status_code
    text = resp.text or ""
    css_list = [m.group("css").strip() for m in _STYLE_TAG_RE.finditer(text) if m.group("css").strip()]
    if not css_list:
        return "", None
    return "\n\n".join(css_list), None


def _wrap_wechat_html(body_html: str, *, extra_css: str) -> str:
    """
    仅做最小包裹，不注入默认 base_css（由调用方通过 extra_css 控制样式）。
    """
    css = (extra_css or "").strip()
    if css:
        return '<section class="wechatmp-article">' + "<style>\n" + css + "\n</style>\n" + body_html + "</section>"
    return '<section class="wechatmp-article">' + body_html + "</section>"


def _parse_css_declarations(block: str) -> Dict[str, str]:
    """
    解析 `a:1; b:2` 形式的 declarations，返回 {prop: value}。
    非严格实现：忽略空项、忽略无冒号项。
    """
    out: Dict[str, str] = {}
    for part in (block or "").split(";"):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            continue
        k, v = part.split(":", 1)
        k = k.strip().lower()
        v = v.strip()
        if not k or not v:
            continue
        out[k] = v
    return out


def _merge_style_attr(existing: str, add: Dict[str, str]) -> str:
    base = _parse_css_declarations(existing or "")
    # inline style 优先级更高：保留 existing，缺失的再补
    for k, v in add.items():
        if k not in base:
            base[k] = v
    return "; ".join([f"{k}: {v}" for k, v in base.items()]) + (";" if base else "")


_TAG_RE = re.compile(r"<(?P<tag>[a-zA-Z][a-zA-Z0-9]*)\b(?P<attrs>[^>]*)>", re.IGNORECASE)
_ATTR_CLASS_RE = re.compile(r'\bclass\s*=\s*(["\'])(?P<cls>[^"\']*)\1', re.IGNORECASE)
_ATTR_STYLE_RE = re.compile(r'\bstyle\s*=\s*(["\'])(?P<style>[^"\']*)\1', re.IGNORECASE)
_ATTR_CLASS_STRIP_RE = re.compile(r'\s+\bclass\s*=\s*(["\'])[^"\']*\1', re.IGNORECASE)


def _selector_matches(tag: str, attrs: str, selector: str) -> bool:
    """
    仅支持非常常见的 selector：
    - tag
    - .class
    - tag.class
    - 以及 `.wechatmp-article <simple>` 这类“根作用域限定”（会在进入本函数前做剥离）
    其它 selector 直接返回 False（避免误伤）。
    """
    selector = (selector or "").strip()
    if not selector:
        return False
    if selector.startswith("@"):
        return False
    if any(x in selector for x in (" ", ">", "+", "~", "[", ":", "#", "*")):
        return False

    tag_l = tag.lower()
    cls_m = _ATTR_CLASS_RE.search(attrs or "")
    classes = set((cls_m.group("cls") or "").split()) if cls_m else set()

    if selector.startswith("."):
        return selector[1:] in classes
    if "." in selector:
        t, c = selector.split(".", 1)
        tl = t.lower()
        # div -> section：我们会把 div 替换为 section，因此把 div 选择器视作也能命中 section
        if tl == tag_l and (c in classes):
            return True
        if tl == "div" and tag_l == "section" and (c in classes):
            return True
        return False
    sel_l = selector.lower()
    if sel_l == tag_l:
        return True
    # div -> section：同上，div 选择器也命中 section
    if sel_l == "div" and tag_l == "section":
        return True
    return False


def _normalize_selector_for_inlining(selector: str) -> Optional[str]:
    """
    将选择器规范化为可内联的“简单选择器”，并尽量支持我们自己注入的根作用域：
    - `.wechatmp-article p` -> `p`
    - `.wechatmp-article .date` -> `.date`
    - `.wechatmp-article h1` -> `h1`
    - `.wechatmp-article` -> `.wechatmp-article`（用于根节点本身）

    其它复杂选择器返回 None（跳过）。
    """
    sel = (selector or "").strip()
    if not sel:
        return None
    if sel.startswith("@"):
        return None

    # 支持根作用域限定：公众号内容都包在 .wechatmp-article 下，可以安全剥离
    root = ".wechatmp-article"
    if sel == root:
        return sel
    if sel.startswith(root + " "):
        sel = sel[len(root) :].strip()

    # 支持非常常见的“后代选择器”（仅 1 个空格）：A B
    if " " in sel:
        if any(x in sel for x in (">", "+", "~", "[", ":", "#", "*")):
            return None
        parts = [p for p in sel.split() if p]
        if len(parts) == 2:
            a, b = parts
            if any(x in a for x in (">", "+", "~", "[", ":", "#", "*")):
                return None
            if any(x in b for x in (">", "+", "~", "[", ":", "#", "*")):
                return None
            return a + " " + b
        return None

    # 剥离后如果还包含复杂结构就跳过（避免误伤）
    if any(x in sel for x in (">", "+", "~", "[", ":", "#", "*")):
        return None
    return sel or None


def _inline_descendant_rules(html_text: str, rules: List[Tuple[str, str, Dict[str, str]]]) -> str:
    """
    将后代选择器 A B 的规则内联：
    在匹配 A 的元素块内部，对匹配 B 的元素添加 inline style。
    仅支持两段式 selector（A 与 B 都是简单选择器：tag / .class / tag.class）。
    """
    if not html_text or not rules:
        return html_text

    # 找到所有标签起始位置，逐个尝试匹配 ancestor selector
    s = html_text
    i = 0
    while True:
        m = _TAG_RE.search(s, i)
        if not m:
            break
        tag = m.group("tag")
        attrs = m.group("attrs") or ""

        # 仅对能做配对提取的标签处理（避免单标签/自闭合带来的错配）
        if s[m.end() - 2 : m.end()] == "/>":
            i = m.end()
            continue

        matched_rules = [(a, b, d) for (a, b, d) in rules if _selector_matches(tag, attrs, a)]
        if not matched_rules:
            i = m.end()
            continue

        block_pos = _find_balanced_tag_block(s, tag=tag, start_idx=m.start())
        if not block_pos:
            i = m.end()
            continue
        b0, b1 = block_pos
        block = s[b0:b1]
        extracted = _extract_start_tag_and_inner(block, tag=tag)
        if not extracted:
            i = b1
            continue
        start_tag, inner = extracted

        # 在 inner 上应用 child selector 的简单内联
        def inner_repl(mm: re.Match) -> str:
            t2 = mm.group("tag")
            a2 = mm.group("attrs") or ""
            add: Dict[str, str] = {}
            for _, child_sel, decls in matched_rules:
                if _selector_matches(t2, a2, child_sel):
                    add.update(decls)
            if not add:
                return mm.group(0)
            sm = _ATTR_STYLE_RE.search(a2)
            if sm:
                merged = _merge_style_attr(sm.group("style") or "", add)
                new_attrs = a2[: sm.start()] + f' style="{merged}"' + a2[sm.end() :]
            else:
                new_attrs = a2 + f' style="{_merge_style_attr("", add)}"'
            return f"<{t2}{new_attrs}>"

        inner2 = _TAG_RE.sub(inner_repl, inner)
        block2 = start_tag + inner2 + (re.search(r"</\s*%s\s*>\s*$" % re.escape(tag), block, flags=re.IGNORECASE).group(0))  # type: ignore
        s = s[:b0] + block2 + s[b1:]
        i = b0 + len(block2)

    return s


def _inline_css_from_style_tags(html_text: str) -> str:
    """
    将 HTML 中所有 <style>...</style> 里的部分规则内联到元素 style="" 上，然后移除 <style>。
    为了健壮性与安全性，仅支持简单选择器（tag / .class / tag.class）。
    """
    if not html_text:
        return ""

    css_list = [m.group("css") for m in _STYLE_TAG_RE.finditer(html_text) if (m.group("css") or "").strip()]
    if not css_list:
        return html_text
    css = "\n".join(css_list)

    # 移除所有 style 标签（避免公众号丢失导致完全无样式）
    html_wo_style = _STYLE_TAG_BLOCK_RE.sub("", html_text)

    # 解析规则：selector { decls }
    rules_simple: List[Tuple[str, Dict[str, str]]] = []
    rules_desc: List[Tuple[str, str, Dict[str, str]]] = []
    # 去掉注释
    css = re.sub(r"/\*[\s\S]*?\*/", "", css)
    for chunk in css.split("}"):
        if "{" not in chunk:
            continue
        sel_part, decl_part = chunk.split("{", 1)
        decls = _parse_css_declarations(decl_part)
        if not decls:
            continue
        selectors = [s.strip() for s in sel_part.split(",") if s.strip()]
        for sel in selectors:
            nsel = _normalize_selector_for_inlining(sel)
            if nsel:
                if " " in nsel:
                    a, b = nsel.split(" ", 1)
                    rules_desc.append((a.strip(), b.strip(), decls))
                else:
                    rules_simple.append((nsel, decls))

    if not rules_simple and not rules_desc:
        return html_wo_style

    def repl(m: re.Match) -> str:
        tag = m.group("tag")
        attrs = m.group("attrs") or ""
        # 跳过 <style> 自身（已移除，但以防万一）
        if tag.lower() == "style":
            return m.group(0)

        add: Dict[str, str] = {}
        for sel, decls in rules_simple:
            if _selector_matches(tag, attrs, sel):
                # 后面的规则覆盖前面的（同优先级下按顺序）
                add.update(decls)
        if not add:
            return m.group(0)

        sm = _ATTR_STYLE_RE.search(attrs)
        if sm:
            merged = _merge_style_attr(sm.group("style") or "", add)
            new_attrs = attrs[: sm.start()] + f' style="{merged}"' + attrs[sm.end() :]
        else:
            new_attrs = attrs + f' style="{_merge_style_attr("", add)}"'
        return f"<{tag}{new_attrs}>"

    out = _TAG_RE.sub(repl, html_wo_style)
    # 再处理后代选择器（A B）
    if rules_desc:
        out = _inline_descendant_rules(out, rules_desc)
    return out


def _strip_class_attributes(html_text: str) -> str:
    """
    在 CSS 已经完成内联后，移除所有 class 属性，降低公众号对 class/结构的重排影响。
    """
    if not html_text:
        return ""

    def repl(m: re.Match) -> str:
        tag = m.group("tag")
        attrs = m.group("attrs") or ""
        attrs2 = _ATTR_CLASS_STRIP_RE.sub("", attrs)
        return f"<{tag}{attrs2}>"

    return _TAG_RE.sub(repl, html_text)


def _generate_cover_image(title: str, *, out_rel: str) -> Tuple[Optional[str], Optional[str]]:
    """
    自动生成一张简单封面图（PNG）。out_rel 为相对路径（限制在 cwd 下）。
    返回 (relative_path, error_message)
    """
    safe = _normalize_local_path(out_rel, "cover_out")
    if safe["error"]:
        return None, safe["message"]

    try:
        from PIL import Image, ImageDraw, ImageFont  # type: ignore
    except Exception:
        return None, "missing_dependency: pip install pillow"

    os.makedirs(os.path.dirname(safe["path"]) or ".", exist_ok=True)

    w, h = 900, 383  # 适配常见封面比例
    bg = (15, 23, 42)
    fg = (255, 255, 255)
    accent = (22, 119, 255)

    img = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(img)

    # 装饰条
    draw.rectangle([0, 0, 10, h], fill=accent)

    # 字体：尽量使用默认字体（跨平台）
    try:
        font_title = ImageFont.truetype("arial.ttf", 48)
        font_sub = ImageFont.truetype("arial.ttf", 22)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # 简单换行（按字符数粗略切）
    t = (title or "").strip()
    if not t:
        t = "公众号文章"
    max_len = 18
    lines: List[str] = []
    while t:
        lines.append(t[:max_len])
        t = t[max_len:]
        if len(lines) >= 3:
            break

    y = 90
    for line in lines:
        draw.text((60, y), line, font=font_title, fill=fg)
        y += 60

    draw.text((60, h - 55), "Generated by OpenClaw · WeChatMP", font=font_sub, fill=(180, 190, 210))

    try:
        img.save(safe["path"], format="PNG")
    except Exception as e:
        return None, "save_failed: %s" % e

    return safe["relative"], None


def _get_access_token(appid: str, secret: str) -> Tuple[Optional[str], Optional[str]]:
    url = WECHAT_API_BASE + "/cgi-bin/token"
    params = {"grant_type": "client_credential", "appid": appid, "secret": secret}
    try:
        resp = requests.get(url, params=params, timeout=20)
    except Exception as e:
        return None, "request_failed: %s" % e
    try:
        data = resp.json()
    except Exception:
        return None, "invalid_json: %s" % (resp.text[:300] if resp.text else "")
    if data.get("errcode"):
        return None, "api_error: %s %s" % (data.get("errcode"), data.get("errmsg"))
    token = data.get("access_token")
    if not token:
        return None, "api_error: no access_token"
    return str(token), None


def _wechat_post_json(url: str, payload: dict) -> Tuple[Optional[dict], Optional[str]]:
    try:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        resp = requests.post(
            url,
            data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=60,
        )
    except Exception as e:
        return None, "request_failed: %s" % e
    try:
        data = json.loads(resp.content.decode("utf-8"))
    except Exception:
        try:
            data = resp.json()
        except Exception:
            return None, "invalid_json: %s" % (resp.text[:400] if resp.text else "")
    if data.get("errcode") not in (0, None):
        return None, "api_error: %s %s" % (data.get("errcode"), data.get("errmsg"))
    return data, None


def _upload_cover_as_material(
    access_token: str,
    cover_rel_path: str,
    *,
    cover_mime: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str]]:
    safe = _normalize_local_path(cover_rel_path, "cover")
    if safe["error"]:
        return None, safe["message"]
    if not os.path.isfile(safe["path"]):
        return None, "File not found: %s" % safe["relative"]

    # WeChat 接口上传 image 时，mime 类型最好匹配实际文件格式。
    if not cover_mime:
        _, ext = os.path.splitext(safe["path"])
        ext = (ext or "").lower().strip(".")
        if ext == "png":
            cover_mime = "image/png"
        elif ext in ("jpg", "jpeg"):
            cover_mime = "image/jpeg"
        elif ext == "gif":
            cover_mime = "image/gif"
        else:
            cover_mime = "image/png"

    url = WECHAT_API_BASE + "/cgi-bin/material/add_material"
    params = {"access_token": access_token, "type": "image"}
    try:
        with open(safe["path"], "rb") as f:
            files = {"media": (os.path.basename(safe["path"]), f, cover_mime)}
            resp = requests.post(url, params=params, files=files, timeout=60)
    except Exception as e:
        return None, "request_failed: %s" % e

    try:
        data = resp.json()
    except Exception:
        return None, "invalid_json: %s" % (resp.text[:400] if resp.text else "")

    if data.get("errcode") not in (0, None) and data.get("errcode") is not None:
        return None, "api_error: %s %s" % (data.get("errcode"), data.get("errmsg"))

    media_id = data.get("media_id")
    if not media_id:
        return None, "api_error: no media_id"
    return str(media_id), None


def _draft_add(access_token: str, article: dict) -> Tuple[Optional[str], Optional[str], Optional[dict]]:
    url = WECHAT_API_BASE + "/cgi-bin/draft/add"
    url = url + "?access_token=" + access_token
    payload = {"articles": [article]}
    data, err = _wechat_post_json(url, payload)
    if err:
        return None, err, None
    media_id = data.get("media_id")
    if not media_id:
        return None, "api_error: no draft media_id", data
    return str(media_id), None, data


def _load_accounts() -> Tuple[Optional[List[dict]], Optional[str]]:
    """
    支持两种方式：
    1) 单账号：WECHAT_MP_APP_ID / WECHAT_MP_APP_SECRET
    2) 多账号：WECHAT_MP_ACCOUNTS='[{"name":"a","appid":"...","secret":"..."}, ...]'
    """
    raw = os.environ.get("WECHAT_MP_ACCOUNTS", "").strip()
    if raw:
        try:
            obj = json.loads(raw)
        except Exception as e:
            return None, "Invalid WECHAT_MP_ACCOUNTS JSON: %s" % e
        if not isinstance(obj, list) or not obj:
            return None, "WECHAT_MP_ACCOUNTS must be a non-empty JSON array"
        accounts = []
        for i, item in enumerate(obj):
            if not isinstance(item, dict):
                return None, "WECHAT_MP_ACCOUNTS[%d] must be an object" % i
            appid = str(item.get("appid") or "").strip()
            secret = str(item.get("secret") or "").strip()
            name = str(item.get("name") or ("account_%d" % (i + 1))).strip()
            if not appid or not secret:
                return None, "WECHAT_MP_ACCOUNTS[%d] missing appid/secret" % i
            accounts.append({"name": name, "appid": appid, "secret": secret})
        return accounts, None

    appid = os.environ.get("WECHAT_MP_APP_ID", "").strip()
    secret = os.environ.get("WECHAT_MP_APP_SECRET", "").strip()
    if not appid or not secret:
        return None, "Missing env: WECHAT_MP_APP_ID / WECHAT_MP_APP_SECRET (or WECHAT_MP_ACCOUNTS)"
    return [{"name": "default", "appid": appid, "secret": secret}], None


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  publish.py draft '{...json...}'\n\n"
            "Example:\n"
            "  publish.py draft '{\"title\":\"标题\",\"md_path\":\"article.md\",\"digest\":\"摘要\",\"style_url\":\"https://example.com\"}'",
            file=sys.stderr,
        )
        sys.exit(1)

    cmd = sys.argv[1].strip().lower()
    raw = sys.argv[2] if len(sys.argv) >= 3 else ""
    if isinstance(raw, str):
        raw_stripped = raw.strip()
        # 1) 从 stdin 读取 JSON：publish.py draft -
        if raw_stripped == "-":
            # 用 buffer 读取，尽量避免 PowerShell/控制台编码导致中文变 '????'
            b = sys.stdin.buffer.read()
            text = None
            for enc in ("utf-8", "utf-8-sig", "utf-16", "utf-16le", "gb18030"):
                try:
                    text = b.decode(enc)
                    break
                except Exception:
                    pass
            if text is None:
                # 兜底：尽量解出来（可能仍有替换字符）
                text = b.decode("utf-8", errors="replace")
            raw = text
        # 2) 从文件读取 JSON：publish.py draft @out/req.json（推荐，最稳）
        elif raw_stripped.startswith("@") and len(raw_stripped) > 1:
            p = raw_stripped[1:]
            safe = _normalize_local_path(p, "req_json_path")
            if safe["error"]:
                print(safe["message"], file=sys.stderr)
                sys.exit(1)
            try:
                with open(safe["path"], "rb") as f:
                    b = f.read()
                text = None
                for enc in ("utf-8", "utf-8-sig", "utf-16", "utf-16le", "gb18030"):
                    try:
                        text = b.decode(enc)
                        break
                    except Exception:
                        pass
                if text is None:
                    text = b.decode("utf-8", errors="replace")
                raw = text
            except Exception as e:
                print("Failed to read json file: %s" % e, file=sys.stderr)
                sys.exit(1)
    try:
        req = json.loads(raw) if raw.strip() else {}
    except Exception as e:
        print("JSON parse error: %s" % e, file=sys.stderr)
        sys.exit(1)
    if not isinstance(req, dict):
        print("Error: JSON body must be an object.", file=sys.stderr)
        sys.exit(1)

    if cmd not in ("draft", "draft_add"):
        print("Error: unknown command '%s'" % cmd, file=sys.stderr)
        sys.exit(1)

    title = str(req.get("title") or "").strip()
    # 默认尝试修复标题 mojibake；可传 repair_mojibake=0 关闭
    try:
        repair_mojibake = int(req.get("repair_mojibake", 1))
    except Exception:
        repair_mojibake = 1
    if repair_mojibake:
        title = _repair_mojibake(title)
    if not title:
        _json_out({"error": "missing_param", "message": "title is required"})
        sys.exit(1)

    digest = str(req.get("digest") or "").strip()
    author = str(req.get("author") or os.environ.get("WECHAT_MP_DEFAULT_AUTHOR", "")).strip()
    if repair_mojibake:
        digest = _repair_mojibake(digest)
        author = _repair_mojibake(author)
    # 如果仍然是 '????' 形态，给出明确提示（通常是 PowerShell/文件保存编码导致的不可逆丢字）
    if (title.count("?") >= 2 and _cjk_score(title) == 0) or (digest.count("?") >= 2 and _cjk_score(digest) == 0):
        print(
            "WARN: title/digest contains many '?' characters. This usually means the text was already lost before Python received it. "
            "Please pass request JSON via @file (UTF-8) instead of pipeline/console, e.g. `publish.py draft @out/req.json`.",
            file=sys.stderr,
        )
    content_source_url = str(req.get("content_source_url") or "").strip()

    # 内容：支持 md_path/md_content 或 html_path/html_content
    body_html = None
    input_html_css = ""
    html_text_full = None
    full_html_for_meta = None
    # 允许直接从网络 URL 拉取 HTML
    if req.get("html_url"):
        url = str(req.get("html_url") or "").strip()
        cookie = str(req.get("html_url_cookie") or os.environ.get("WECHAT_MP_COOKIE", "")).strip()
        try:
            max_bytes = int(req.get("html_url_max_bytes", 2_500_000))
        except Exception:
            max_bytes = 2_500_000
        # 给一个合理下限，避免误传极小值
        if max_bytes < 200_000:
            max_bytes = 200_000
        text, err = _fetch_text_url(url, cookie=cookie, max_bytes=max_bytes)
        if err:
            _json_out({"error": "fetch_failed", "message": err, "html_url": url})
            sys.exit(1)
        html_text_full = text or ""
        full_html_for_meta = html_text_full
    if html_text_full is not None:
        # 先从整份 HTML 里提取 head/style
        all_css = [m.group("css").strip() for m in _STYLE_TAG_RE.finditer(html_text_full) if (m.group("css") or "").strip()]
        input_html_css = "\n\n".join(all_css)
        html_url_lc = str(req.get("html_url") or "").strip().lower()
        # 针对 mp.weixin.qq.com 页面：固定提取 id="js_content" 正文。
        if "mp.weixin.qq.com/" in html_url_lc:
            js_content = _extract_js_content_from_page(html_text_full)
            body_html = js_content if js_content else _extract_body_if_full_html(html_text_full)
        else:
            body_html = _extract_body_if_full_html(html_text_full)
    elif req.get("html_path") or req.get("html_content"):
        html_text, err = _read_text_input(req, field_path="html_path", field_content="html_content", allowed_ext=(".html", ".htm"))
        if err:
            _json_out({"error": "invalid_param", "message": err})
            sys.exit(1)
        # HTML 输入可能是完整文档（含 html/head/body）。
        # 1) 先从“整份 HTML”中提取 <style>，避免只取 body 时把 head 里的 CSS 丢掉
        all_css = [m.group("css").strip() for m in _STYLE_TAG_RE.finditer(html_text or "") if (m.group("css") or "").strip()]
        input_html_css = "\n\n".join(all_css)
        # 2) 微信 content 只需要 body 部分
        body_html = _extract_body_if_full_html(html_text or "")
        full_html_for_meta = html_text or ""
    else:
        md_text, err = _read_text_input(req, field_path="md_path", field_content="md_content", allowed_ext=(".md", ".markdown", ".txt"))
        if err:
            _json_out({"error": "invalid_param", "message": err})
            sys.exit(1)
        html, err2 = _md_to_html(md_text or "")
        if err2:
            _json_out({"error": "convert_failed", "message": err2})
            sys.exit(1)
        body_html = html or ""

    # 精确提取正文（例如网易文章：div.post_body）
    # 规则：
    # - 若传了 content_selector：直接按该 selector 抽取 innerHTML
    # - 否则：auto_content_selector=1 时默认尝试 'div.post_body'
    try:
        content_selector = str(req.get("content_selector") or "").strip()
    except Exception:
        content_selector = ""
    try:
        auto_content_selector = int(req.get("auto_content_selector", 1))
    except Exception:
        auto_content_selector = 1
    if (not content_selector) and auto_content_selector:
        source_url = str(req.get("html_url") or "").strip().lower()
        # 常见站点默认正文 selector（可被 content_selector 覆盖）
        if "163.com" in source_url:
            content_selector = "div.post_body"
        elif "sina.com.cn" in source_url or "k.sina.com.cn" in source_url:
            content_selector = "div.article"
        elif "toutiao.com" in source_url:
            content_selector = "article"
        else:
            content_selector = "div.post_body"
    if content_selector:
        full_for_select = full_html_for_meta if full_html_for_meta is not None else html_text_full
        extracted = _extract_inner_html_by_selector(full_for_select or "", content_selector)
        if extracted:
            body_html = extracted

    # 公众号兼容：默认开启；可传 wechat_sanitize=0 关闭
    try:
        wechat_sanitize = int(req.get("wechat_sanitize", 1))
    except Exception:
        wechat_sanitize = 1
    if wechat_sanitize:
        body_html = _sanitize_for_wechat(body_html or "")

    # 样式：css / css_path / style_url 三选多可叠加
    extra_css = ""
    # 来自 html 输入（通常在 head/style 中）的样式，优先合并进来
    if input_html_css:
        extra_css += "\n\n" + input_html_css
    css_inline = req.get("css")
    if css_inline is not None and str(css_inline).strip():
        extra_css += "\n\n" + str(css_inline)

    css_path = req.get("css_path")
    if css_path:
        css_text, err = _read_text_input(req, field_path="css_path", field_content="_css_content_ignored", allowed_ext=(".css",))
        # _read_text_input 会优先读 content 字段；这里避免误用，直接读 path
        if err:
            _json_out({"error": "invalid_param", "message": err})
            sys.exit(1)
        extra_css += "\n\n" + (css_text or "")

    style_url = str(req.get("style_url") or "").strip()
    if style_url:
        css_from_url, err = _extract_styles_from_url(style_url)
        if err:
            _json_out({"error": "style_fetch_failed", "message": err, "style_url": style_url})
            sys.exit(1)
        extra_css += "\n\n" + (css_from_url or "")

    final_html = _wrap_wechat_html(body_html, extra_css=extra_css)
    # 默认内联 CSS，避免公众号发布时丢失 <style> 样式；可传 inline_css=0 关闭
    try:
        inline_css = int(req.get("inline_css", 1))
    except Exception:
        inline_css = 1
    if inline_css:
        final_html = _inline_css_from_style_tags(final_html)
    # 默认剥离 class 属性（依赖 inline_css 把样式落到 style=""）；可传 strip_class=0 关闭
    try:
        strip_class = int(req.get("strip_class", 1))
    except Exception:
        strip_class = 1
    if strip_class:
        final_html = _strip_class_attributes(final_html)

    # 可选：发布前限制 content 字节数，防止微信返回 45002（content size out of limit）。
    try:
        content_max_bytes = int(req.get("content_max_bytes", 0))
    except Exception:
        content_max_bytes = 0
    final_html_bytes = len(final_html.encode("utf-8"))
    if content_max_bytes > 0 and final_html_bytes > content_max_bytes:
        _json_out(
            {
                "error": "content_too_large",
                "message": "content bytes exceed content_max_bytes",
                "content_bytes": final_html_bytes,
                "content_max_bytes": content_max_bytes,
            }
        )
        sys.exit(1)

    # 调试：把最终上传的 HTML 落盘，便于确认 div/布局替换是否生效
    debug_out = str(req.get("debug_html_out") or "").strip()
    if debug_out:
        safe = _normalize_local_path(debug_out, "debug_html_out")
        if safe["error"]:
            _json_out({"error": "invalid_path", "message": safe["message"]})
            sys.exit(1)
        os.makedirs(os.path.dirname(safe["path"]) or ".", exist_ok=True)
        try:
            with open(safe["path"], "w", encoding="utf-8") as f:
                f.write(final_html)
        except Exception as e:
            _json_out({"error": "write_failed", "message": "Failed to write debug_html_out: %s" % e})
            sys.exit(1)

    # 干跑：只生成最终 HTML（可配合 debug_html_out 查看），不调用微信接口
    try:
        dry_run = int(req.get("dry_run", 0))
    except Exception:
        dry_run = 0
    if dry_run:
        _json_out(
            {
                "ok": True,
                "dry_run": True,
                "title": title,
                "wechat_sanitize": bool(wechat_sanitize),
                "debug_html_out": debug_out or None,
                "final_html_bytes": final_html_bytes,
            }
        )
        return

    # 封面：
    # - 优先使用用户显式提供：cover_path / cover_base64 / cover_url 三选一
    # - 若都未提供，可选自动使用页面 meta og:image（默认开启）
    # - 不再自动生成本地封面图
    cover_rel = None
    cover_mime_for_upload: Optional[str] = None
    og_image_url = _extract_meta_og_image(full_html_for_meta or "") if full_html_for_meta is not None else None
    try:
        auto_cover_from_og_image = int(req.get("auto_cover_from_og_image", 1))
    except Exception:
        auto_cover_from_og_image = 1
    if req.get("cover_path"):
        safe = _normalize_local_path(str(req.get("cover_path")).strip(), "cover_path")
        if safe["error"]:
            _json_out({"error": "invalid_path", "message": safe["message"]})
            sys.exit(1)
        cover_rel = safe["relative"]
    elif req.get("cover_base64"):
        # 将 base64 生成文件（限制到 cwd）
        out_rel = str(req.get("cover_out") or "out/wechatmp-cover.png")
        safe = _normalize_local_path(out_rel, "cover_out")
        if safe["error"]:
            _json_out({"error": "invalid_path", "message": safe["message"]})
            sys.exit(1)
        try:
            raw_bytes = base64.b64decode(str(req.get("cover_base64")), validate=False)
            os.makedirs(os.path.dirname(safe["path"]) or ".", exist_ok=True)
            with open(safe["path"], "wb") as f:
                f.write(raw_bytes)
            cover_rel = safe["relative"]
        except Exception as e:
            _json_out({"error": "invalid_param", "message": "cover_base64 decode failed: %s" % e})
            sys.exit(1)
    elif req.get("cover_url"):
        cover_url = str(req.get("cover_url") or "").strip()
        cookie = str(req.get("cover_url_cookie") or os.environ.get("WECHAT_MP_COOKIE", "")).strip()
        try:
            max_bytes = int(req.get("cover_url_max_bytes", 5_000_000))
        except Exception:
            max_bytes = 5_000_000
        out_rel = str(req.get("cover_out") or "out/wechatmp-cover.png")
        safe = _normalize_local_path(out_rel, "cover_out")
        if safe["error"]:
            _json_out({"error": "invalid_path", "message": safe["message"]})
            sys.exit(1)
        img_bytes, err_img, content_type = _fetch_image_url(
            cover_url,
            cookie=cookie,
            max_bytes=max_bytes,
        )
        if err_img:
            _json_out({"error": "cover_fetch_failed", "message": err_img, "cover_url": cover_url})
            sys.exit(1)
        try:
            os.makedirs(os.path.dirname(safe["path"]) or ".", exist_ok=True)
            with open(safe["path"], "wb") as f:
                f.write(img_bytes or b"")
        except Exception as e:
            _json_out({"error": "cover_write_failed", "message": "Failed to write cover_out: %s" % e})
            sys.exit(1)
        cover_rel = safe["relative"]
        cover_mime_for_upload = content_type
    elif auto_cover_from_og_image and og_image_url:
        cookie = str(req.get("cover_url_cookie") or os.environ.get("WECHAT_MP_COOKIE", "")).strip()
        try:
            max_bytes = int(req.get("cover_url_max_bytes", 5_000_000))
        except Exception:
            max_bytes = 5_000_000
        out_rel = str(req.get("cover_out") or "out/wechatmp-cover.png")
        safe = _normalize_local_path(out_rel, "cover_out")
        if safe["error"]:
            _json_out({"error": "invalid_path", "message": safe["message"]})
            sys.exit(1)
        img_bytes, err_img, content_type = _fetch_image_url(
            og_image_url,
            cookie=cookie,
            max_bytes=max_bytes,
        )
        if err_img:
            _json_out({"error": "cover_fetch_failed", "message": err_img, "cover_url": og_image_url})
            sys.exit(1)
        try:
            os.makedirs(os.path.dirname(safe["path"]) or ".", exist_ok=True)
            with open(safe["path"], "wb") as f:
                f.write(img_bytes or b"")
        except Exception as e:
            _json_out({"error": "cover_write_failed", "message": "Failed to write cover_out: %s" % e})
            sys.exit(1)
        cover_rel = safe["relative"]
        cover_mime_for_upload = content_type
    else:
        _json_out(
            {
                "error": "missing_param",
                "message": "cover is required: provide cover_path / cover_base64 / cover_url, or ensure page has og:image (auto_cover_from_og_image=1)",
            }
        )
        sys.exit(1)

    accounts, err = _load_accounts()
    if err:
        _json_out({"error": "missing_credential", "message": err})
        sys.exit(1)

    results = []
    for acc in accounts or []:
        name = acc["name"]
        token, err = _get_access_token(acc["appid"], acc["secret"])
        if err:
            results.append({"account": name, "error": "token_failed", "message": err})
            continue

        thumb_media_id, err = _upload_cover_as_material(token, cover_rel, cover_mime=cover_mime_for_upload)
        if err:
            results.append({"account": name, "error": "cover_upload_failed", "message": err, "cover": cover_rel})
            continue

        article = {
            "title": title,
            "author": author,
            "digest": digest,
            "content": final_html,
            "content_source_url": content_source_url,
            "thumb_media_id": thumb_media_id,
            "need_open_comment": int(req.get("need_open_comment", 0)),
            "only_fans_can_comment": int(req.get("only_fans_can_comment", 0)),
            "show_cover_pic": int(req.get("show_cover_pic", 1)),
        }

        draft_id, err, raw_resp = _draft_add(token, article)
        if err:
            results.append({"account": name, "error": "draft_add_failed", "message": err, "raw": raw_resp})
            continue
        results.append({"account": name, "ok": True, "draft_media_id": draft_id, "thumb_media_id": thumb_media_id})

        # 轻微 sleep，避免多账号瞬时打满
        time.sleep(0.2)

    _json_out(
        {
            "ok": True,
            "title": title,
            "cover": cover_rel,
            "accounts": results,
        }
    )


if __name__ == "__main__":
    main()

