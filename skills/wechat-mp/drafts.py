#!/usr/bin/env python3
"""
WeChat MP draft management.
草稿管理：批量获取、获取详情、删除草稿、提交发布。

API（参考官方文档）：
- POST /cgi-bin/draft/batchget
- POST /cgi-bin/draft/get
- POST /cgi-bin/draft/delete
- POST /cgi-bin/freepublish/submit（将草稿提交发布，接口英文名 freepublish_submit）
"""

import json
import os
import sys
import time
from urllib.parse import urlparse
from typing import Any, Dict, List, Optional, Tuple

import requests


WECHAT_API_BASE = "https://api.weixin.qq.com"


def _json_out(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _load_accounts() -> Tuple[Optional[List[dict]], Optional[str]]:
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


def _wechat_post_json(path: str, access_token: str, payload: dict) -> Tuple[Optional[dict], Optional[str]]:
    url = WECHAT_API_BASE + path
    sep = "&" if "?" in url else "?"
    url = url + sep + "access_token=" + access_token
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


def _require_str(req: Dict[str, Any], key: str) -> Tuple[Optional[str], Optional[str]]:
    val = req.get(key)
    if val in (None, ""):
        return None, "missing_param: %s" % key
    return str(val), None


def _require_int(req: Dict[str, Any], key: str) -> Tuple[Optional[int], Optional[str]]:
    if key not in req:
        return None, "missing_param: %s" % key
    try:
        return int(req.get(key)), None
    except Exception:
        return None, "invalid_param: %s must be integer" % key


def _fetch_image_url(
    url: str,
    *,
    cookie: str = "",
    timeout: int = 25,
    max_bytes: int = 5_000_000,
) -> Tuple[Optional[bytes], Optional[str], Optional[str]]:
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


def _upload_image_material_from_bytes(
    access_token: str,
    image_bytes: bytes,
    *,
    filename: str = "cover.jpg",
    content_type: str = "image/jpeg",
) -> Tuple[Optional[str], Optional[str]]:
    url = WECHAT_API_BASE + "/cgi-bin/material/add_material"
    params = {"access_token": access_token, "type": "image"}
    try:
        files = {"media": (filename, image_bytes, content_type)}
        resp = requests.post(url, params=params, files=files, timeout=60)
    except Exception as e:
        return None, "request_failed: %s" % e

    try:
        data = resp.json()
    except Exception:
        return None, "invalid_json: %s" % (resp.text[:400] if resp.text else "")
    if data.get("errcode") not in (0, None):
        return None, "api_error: %s %s" % (data.get("errcode"), data.get("errmsg"))
    media_id = data.get("media_id")
    if not media_id:
        return None, "api_error: no media_id"
    return str(media_id), None


def _cmd_clone(all_accounts: List[dict], req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    media_id, err = _require_str(req, "media_id")
    if err:
        return None, err

    source_name = str(req.get("source_account") or "").strip()
    targets_raw = req.get("target_accounts")
    if targets_raw is None:
        target_names: Optional[List[str]] = None
    elif isinstance(targets_raw, list):
        target_names = [str(x).strip() for x in targets_raw if str(x).strip()]
    else:
        return None, "invalid_param: target_accounts must be array of account names"

    by_name = {str(a["name"]): a for a in all_accounts}
    if source_name:
        source_acc = by_name.get(source_name)
        if not source_acc:
            return None, "invalid_param: source_account not found: %s" % source_name
    else:
        if len(all_accounts) == 1:
            source_acc = all_accounts[0]
        else:
            return None, "missing_param: source_account is required when WECHAT_MP_ACCOUNTS has multiple accounts"

    # 构造目标号列表：默认=除源号外全部
    if target_names is None:
        target_accs = [a for a in all_accounts if a["name"] != source_acc["name"]]
    else:
        target_accs = []
        for n in target_names:
            a = by_name.get(n)
            if not a:
                return None, "invalid_param: target account not found: %s" % n
            if a["name"] == source_acc["name"]:
                continue
            target_accs.append(a)
    if not target_accs:
        return None, "invalid_param: no target accounts"

    src_token, err = _get_access_token(source_acc["appid"], source_acc["secret"])
    if err:
        return None, "source_token_failed: %s" % err

    src_data, err = _cmd_get(src_token, {"media_id": media_id})
    if err:
        return None, "source_get_failed: %s" % err

    # draft/get 返回结构通常是 {"news_item":[...]}
    src_items = src_data.get("news_item")
    if not isinstance(src_items, list) or not src_items:
        return None, "source_get_failed: no news_item in draft/get response"

    cookie = str(req.get("cover_url_cookie") or os.environ.get("WECHAT_MP_COOKIE", "")).strip()
    try:
        cover_max_bytes = int(req.get("cover_url_max_bytes", 5_000_000))
    except Exception:
        cover_max_bytes = 5_000_000

    results = []
    for tgt in target_accs:
        name = tgt["name"]
        token, err = _get_access_token(tgt["appid"], tgt["secret"])
        if err:
            results.append({"account": name, "error": "token_failed", "message": err})
            continue

        cloned_articles = []
        clone_err = None
        for idx, it in enumerate(src_items):
            if not isinstance(it, dict):
                clone_err = "invalid source article at index %d" % idx
                break
            thumb_url = str(it.get("thumb_url") or req.get("cover_url") or "").strip()
            if not thumb_url:
                clone_err = "article[%d] missing thumb_url and no cover_url fallback provided" % idx
                break
            img_bytes, ferr, ctype = _fetch_image_url(thumb_url, cookie=cookie, max_bytes=cover_max_bytes)
            if ferr:
                clone_err = "cover_fetch_failed article[%d]: %s" % (idx, ferr)
                break
            ext = ".jpg"
            ct = ctype or "image/jpeg"
            if "png" in ct:
                ext = ".png"
            elif "gif" in ct:
                ext = ".gif"
            filename = "cover_%d%s" % (idx + 1, ext)
            thumb_media_id, uerr = _upload_image_material_from_bytes(token, img_bytes or b"", filename=filename, content_type=ct)
            if uerr:
                clone_err = "cover_upload_failed article[%d]: %s" % (idx, uerr)
                break

            cloned_articles.append(
                {
                    "title": str(it.get("title") or ""),
                    "author": str(it.get("author") or ""),
                    "digest": str(it.get("digest") or ""),
                    "content": str(it.get("content") or ""),
                    "content_source_url": str(it.get("content_source_url") or ""),
                    "thumb_media_id": thumb_media_id,
                    "show_cover_pic": int(it.get("show_cover_pic", 1)),
                    "need_open_comment": int(it.get("need_open_comment", 0)),
                    "only_fans_can_comment": int(it.get("only_fans_can_comment", 0)),
                }
            )

        if clone_err:
            results.append({"account": name, "error": "clone_failed", "message": clone_err})
            continue

        add_data, aerr = _wechat_post_json("/cgi-bin/draft/add", token, {"articles": cloned_articles})
        if aerr:
            results.append({"account": name, "error": "draft_add_failed", "message": aerr})
            continue
        results.append(
            {
                "account": name,
                "ok": True,
                "draft_media_id": add_data.get("media_id"),
                "article_count": len(cloned_articles),
            }
        )
        time.sleep(0.2)

    return {
        "ok": True,
        "command": "clone",
        "source_account": source_acc["name"],
        "source_media_id": media_id,
        "accounts": results,
    }, None


def _cmd_list(access_token: str, req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    """
    批量获取草稿 /cgi-bin/draft/batchget
    参数：
    - offset: 从 0 开始
    - count: 1-20
    - no_content: 0/1（不返回 content）
    """
    offset = int(req.get("offset", 0))
    count = int(req.get("count", 20))
    no_content = int(req.get("no_content", 1))
    payload = {"offset": offset, "count": count, "no_content": no_content}
    return _wechat_post_json("/cgi-bin/draft/batchget", access_token, payload)


def _cmd_get(access_token: str, req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    media_id, err = _require_str(req, "media_id")
    if err:
        return None, err
    payload = {"media_id": media_id}
    return _wechat_post_json("/cgi-bin/draft/get", access_token, payload)


def _cmd_delete(access_token: str, req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    media_id, err = _require_str(req, "media_id")
    if err:
        return None, err
    payload = {"media_id": media_id}
    return _wechat_post_json("/cgi-bin/draft/delete", access_token, payload)


def _cmd_freepublish_submit(access_token: str, req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    """
    发布草稿：POST /cgi-bin/freepublish/submit
    请求体：{"media_id": "草稿的 media_id"}
    成功时返回 publish_id、msg_data_id 等；仅表示提交成功，实际发布异步完成。
    文档：https://developers.weixin.qq.com/doc/subscription/api/public/api_freepublish_submit.html
    """
    media_id, err = _require_str(req, "media_id")
    if err:
        return None, err
    payload = {"media_id": media_id}
    return _wechat_post_json("/cgi-bin/freepublish/submit", access_token, payload)


def _cmd_switch_status(access_token: str) -> Tuple[Optional[dict], Optional[str]]:
    """
    查询草稿箱开关状态 /cgi-bin/draft/switch?checkonly=1
    返回 is_open: 0=关闭, 1=开启
    """
    url = WECHAT_API_BASE + "/cgi-bin/draft/switch?checkonly=1&access_token=" + access_token
    try:
        resp = requests.post(url, timeout=20)
    except Exception as e:
        return None, "request_failed: %s" % e
    try:
        data = resp.json()
    except Exception:
        return None, "invalid_json: %s" % (resp.text[:400] if resp.text else "")
    if data.get("errcode") not in (0, None):
        return None, "api_error: %s %s" % (data.get("errcode"), data.get("errmsg"))
    return data, None


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  drafts.py list '{\"offset\":0,\"count\":20,\"no_content\":1}'\n"
            "  drafts.py get '{\"media_id\":\"xxx\"}'\n"
            "  drafts.py delete '{\"media_id\":\"xxx\"}'\n"
            "  drafts.py clone '{\"media_id\":\"xxx\",\"source_account\":\"公众号A\",\"target_accounts\":[\"公众号B\"]}'\n"
            "  drafts.py publish '{\"media_id\":\"xxx\"}'\n"
            "  drafts.py switch_status\n",
            file=sys.stderr,
        )
        sys.exit(1)

    cmd = sys.argv[1].strip().lower()
    raw = sys.argv[2] if len(sys.argv) >= 3 else ""
    if isinstance(raw, str):
        rs = raw.strip()
        if rs == "-":
            raw = sys.stdin.read()
        elif rs.startswith("@") and len(rs) > 1:
            p = rs[1:]
            try:
                with open(p, "r", encoding="utf-8") as f:
                    raw = f.read()
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

    accounts, err = _load_accounts()
    if err:
        _json_out({"error": "missing_credential", "message": err})
        sys.exit(1)

    if cmd == "clone":
        data, err = _cmd_clone(accounts or [], req)
        if err:
            _json_out({"error": "clone_failed", "message": err})
            sys.exit(1)
        _json_out(data)
        return

    if cmd == "switch_status":
        results = []
        for acc in accounts or []:
            name = acc["name"]
            token, err = _get_access_token(acc["appid"], acc["secret"])
            if err:
                results.append({"account": name, "error": "token_failed", "message": err})
                continue
            data, err = _cmd_switch_status(token)
            if err:
                results.append({"account": name, "error": "api_call_failed", "message": err})
            else:
                is_open = data.get("is_open")
                results.append({"account": name, "ok": True, "is_open": is_open, "is_open_desc": "开启" if is_open == 1 else "关闭"})
            time.sleep(0.2)
        _json_out({"ok": True, "command": cmd, "accounts": results})
        return

    results = []
    for acc in accounts or []:
        name = acc["name"]
        token, err = _get_access_token(acc["appid"], acc["secret"])
        if err:
            results.append({"account": name, "error": "token_failed", "message": err})
            continue

        if cmd == "list":
            data, err = _cmd_list(token, req)
        elif cmd == "get":
            data, err = _cmd_get(token, req)
        elif cmd == "delete":
            data, err = _cmd_delete(token, req)
        elif cmd == "publish":
            data, err = _cmd_freepublish_submit(token, req)
        else:
            results.append({"account": name, "error": "unknown_command", "message": "unknown command: %s" % cmd})
            continue

        if err:
            results.append({"account": name, "error": "api_call_failed", "message": err})
        else:
            results.append({"account": name, "ok": True, "result": data})
        time.sleep(0.2)

    _json_out({"ok": True, "command": cmd, "accounts": results})


if __name__ == "__main__":
    main()

