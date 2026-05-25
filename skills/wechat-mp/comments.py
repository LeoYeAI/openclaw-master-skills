#!/usr/bin/env python3
"""
WeChat MP comments management.
留言/评论管理：查询、精选/取消精选、开启/关闭评论、回复/删除等。
"""

import json
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import requests


WECHAT_API_BASE = "https://api.weixin.qq.com"


def _json_out(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


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
        data = resp.json()
    except Exception:
        return None, "invalid_json: %s" % (resp.text[:400] if resp.text else "")
    if data.get("errcode") not in (0, None):
        return None, "api_error: %s %s" % (data.get("errcode"), data.get("errmsg"))
    return data, None


def _require_int(req: Dict[str, Any], key: str) -> Tuple[Optional[int], Optional[str]]:
    if key not in req:
        return None, "missing_param: %s" % key
    try:
        return int(req.get(key)), None
    except Exception:
        return None, "invalid_param: %s must be integer" % key


def _require_str(req: Dict[str, Any], key: str) -> Tuple[Optional[str], Optional[str]]:
    val = req.get(key)
    if val in (None, ""):
        return None, "missing_param: %s" % key
    return str(val), None


def _cmd_list(access_token: str, req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    """
    查询评论列表 /cgi-bin/comment/list
    需要：msg_data_id, index, begin, count, type
    """
    msg_data_id, err = _require_int(req, "msg_data_id")
    if err:
        return None, err
    index, err = _require_int(req, "index")
    if err:
        return None, err
    begin, err = _require_int(req, "begin")
    if err:
        return None, err
    count, err = _require_int(req, "count")
    if err:
        return None, err
    ctype, err = _require_int(req, "type")
    if err:
        return None, err
    payload = {
        "msg_data_id": msg_data_id,
        "index": index,
        "begin": begin,
        "count": count,
        "type": ctype,
    }
    return _wechat_post_json("/cgi-bin/comment/list", access_token, payload)


def _cmd_open(access_token: str, req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    msg_data_id, err = _require_int(req, "msg_data_id")
    if err:
        return None, err
    index, err = _require_int(req, "index")
    if err:
        return None, err
    payload = {"msg_data_id": msg_data_id, "index": index}
    return _wechat_post_json("/cgi-bin/comment/open", access_token, payload)


def _cmd_close(access_token: str, req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    msg_data_id, err = _require_int(req, "msg_data_id")
    if err:
        return None, err
    index, err = _require_int(req, "index")
    if err:
        return None, err
    payload = {"msg_data_id": msg_data_id, "index": index}
    return _wechat_post_json("/cgi-bin/comment/close", access_token, payload)


def _cmd_mark(access_token: str, req: Dict[str, Any], elect: bool) -> Tuple[Optional[dict], Optional[str]]:
    """
    精选/取消精选：/cgi-bin/comment/markelect, /cgi-bin/comment/unmarkelect
    需要：msg_data_id, index, user_comment_id
    """
    msg_data_id, err = _require_int(req, "msg_data_id")
    if err:
        return None, err
    index, err = _require_int(req, "index")
    if err:
        return None, err
    user_comment_id, err = _require_int(req, "user_comment_id")
    if err:
        return None, err
    payload = {"msg_data_id": msg_data_id, "index": index, "user_comment_id": user_comment_id}
    path = "/cgi-bin/comment/markelect" if elect else "/cgi-bin/comment/unmarkelect"
    return _wechat_post_json(path, access_token, payload)


def _cmd_delete(access_token: str, req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    """
    删除评论 /cgi-bin/comment/delete
    需要：msg_data_id, index, user_comment_id
    """
    msg_data_id, err = _require_int(req, "msg_data_id")
    if err:
        return None, err
    index, err = _require_int(req, "index")
    if err:
        return None, err
    user_comment_id, err = _require_int(req, "user_comment_id")
    if err:
        return None, err
    payload = {"msg_data_id": msg_data_id, "index": index, "user_comment_id": user_comment_id}
    return _wechat_post_json("/cgi-bin/comment/delete", access_token, payload)


def _cmd_reply_add(access_token: str, req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    """
    回复评论 /cgi-bin/comment/reply/add
    需要：msg_data_id, index, user_comment_id, content
    """
    msg_data_id, err = _require_int(req, "msg_data_id")
    if err:
        return None, err
    index, err = _require_int(req, "index")
    if err:
        return None, err
    user_comment_id, err = _require_int(req, "user_comment_id")
    if err:
        return None, err
    content, err = _require_str(req, "content")
    if err:
        return None, err
    payload = {"msg_data_id": msg_data_id, "index": index, "user_comment_id": user_comment_id, "content": content}
    return _wechat_post_json("/cgi-bin/comment/reply/add", access_token, payload)


def _cmd_reply_delete(access_token: str, req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    """
    删除回复 /cgi-bin/comment/reply/delete
    需要：msg_data_id, index, user_comment_id
    """
    msg_data_id, err = _require_int(req, "msg_data_id")
    if err:
        return None, err
    index, err = _require_int(req, "index")
    if err:
        return None, err
    user_comment_id, err = _require_int(req, "user_comment_id")
    if err:
        return None, err
    payload = {"msg_data_id": msg_data_id, "index": index, "user_comment_id": user_comment_id}
    return _wechat_post_json("/cgi-bin/comment/reply/delete", access_token, payload)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  comments.py list '{\"msg_data_id\":123,\"index\":0,\"begin\":0,\"count\":20,\"type\":0}'\n"
            "  comments.py open '{\"msg_data_id\":123,\"index\":0}'\n"
            "  comments.py close '{\"msg_data_id\":123,\"index\":0}'\n"
            "  comments.py mark '{\"msg_data_id\":123,\"index\":0,\"user_comment_id\":1}'\n"
            "  comments.py unmark '{\"msg_data_id\":123,\"index\":0,\"user_comment_id\":1}'\n"
            "  comments.py delete '{\"msg_data_id\":123,\"index\":0,\"user_comment_id\":1}'\n"
            "  comments.py reply_add '{\"msg_data_id\":123,\"index\":0,\"user_comment_id\":1,\"content\":\"谢谢关注\"}'\n"
            "  comments.py reply_delete '{\"msg_data_id\":123,\"index\":0,\"user_comment_id\":1}'\n",
            file=sys.stderr,
        )
        sys.exit(1)

    cmd = sys.argv[1].strip().lower()
    raw = sys.argv[2] if len(sys.argv) >= 3 else ""
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

    results = []
    for acc in accounts or []:
        name = acc["name"]
        token, err = _get_access_token(acc["appid"], acc["secret"])
        if err:
            results.append({"account": name, "error": "token_failed", "message": err})
            continue

        if cmd == "list":
            data, err = _cmd_list(token, req)
        elif cmd == "open":
            data, err = _cmd_open(token, req)
        elif cmd == "close":
            data, err = _cmd_close(token, req)
        elif cmd == "mark":
            data, err = _cmd_mark(token, req, True)
        elif cmd == "unmark":
            data, err = _cmd_mark(token, req, False)
        elif cmd == "delete":
            data, err = _cmd_delete(token, req)
        elif cmd == "reply_add":
            data, err = _cmd_reply_add(token, req)
        elif cmd == "reply_delete":
            data, err = _cmd_reply_delete(token, req)
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

