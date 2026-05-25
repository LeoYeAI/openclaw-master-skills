#!/usr/bin/env python3
"""
WeChat MP 用户管理：黑名单（获取 / 拉黑 / 取消拉黑）、关注者列表、用户基本信息等。

API 参考：
- POST /cgi-bin/tags/members/getblacklist — 黑名单列表（分页）
- POST /cgi-bin/tags/members/batchblacklist — 拉黑（每次最多 20 个 openid）
- POST /cgi-bin/tags/members/batchunblacklist — 取消拉黑（每次最多 20 个）
  https://developers.weixin.qq.com/doc/subscription/api/usermanage/userinfo/api_batchunblacklist.html
- GET  /cgi-bin/user/info — 用户基本信息
- POST /cgi-bin/user/get — 关注者 openid 列表（分页）
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


def _normalize_local_path(user_path: str, field: str) -> Dict[str, Any]:
    """
    限制本地路径：只允许当前工作目录及子目录中的相对路径。
    禁止绝对路径与目录穿越（..），避免被 @file 读到无关敏感文件。
    """
    if not user_path:
        return {"error": "invalid_param", "message": "field '%s' is empty" % field}
    if os.path.isabs(user_path):
        return {"error": "invalid_path", "message": "Absolute path is not allowed for '%s'" % field}
    norm = os.path.normpath(user_path)
    if norm == ".." or norm.startswith(".."):
        return {"error": "invalid_path", "message": "Path traversal is not allowed for '%s'" % field}
    base = os.getcwd()
    full = os.path.join(base, norm)
    return {"error": None, "path": full, "relative": norm}


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
        data = resp.json()
    except Exception:
        return None, "invalid_json: %s" % (resp.text[:400] if resp.text else "")
    if data.get("errcode") not in (0, None):
        return None, "api_error: %s %s" % (data.get("errcode"), data.get("errmsg"))
    return data, None


def _wechat_get(path: str, access_token: str, params: Dict[str, str]) -> Tuple[Optional[dict], Optional[str]]:
    q = dict(params)
    q["access_token"] = access_token
    url = WECHAT_API_BASE + path
    try:
        resp = requests.get(url, params=q, timeout=30)
    except Exception as e:
        return None, "request_failed: %s" % e
    try:
        data = resp.json()
    except Exception:
        return None, "invalid_json: %s" % (resp.text[:400] if resp.text else "")
    if data.get("errcode") not in (0, None):
        return None, "api_error: %s %s" % (data.get("errcode"), data.get("errmsg"))
    return data, None


def _require_openid_list(req: Dict[str, Any], key: str = "openid_list") -> Tuple[Optional[List[str]], Optional[str]]:
    v = req.get(key)
    if not isinstance(v, list) or not v:
        return None, "missing_param or empty: %s (expect JSON array of openid)" % key
    ids = [str(x).strip() for x in v if str(x).strip()]
    if not ids:
        return None, "openid_list has no valid openids"
    if len(ids) > 20:
        return None, "openid_list: WeChat allows at most 20 openids per request"
    return ids, None


def _cmd_blacklist_get(access_token: str, req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    """POST /cgi-bin/tags/members/getblacklist"""
    begin = str(req.get("begin_openid") or "")
    payload = {"begin_openid": begin}
    return _wechat_post_json("/cgi-bin/tags/members/getblacklist", access_token, payload)


def _cmd_blacklist_add(access_token: str, req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    """POST /cgi-bin/tags/members/batchblacklist"""
    ids, err = _require_openid_list(req, "openid_list")
    if err:
        return None, err
    return _wechat_post_json("/cgi-bin/tags/members/batchblacklist", access_token, {"openid_list": ids})


def _cmd_blacklist_remove(access_token: str, req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    """POST /cgi-bin/tags/members/batchunblacklist"""
    ids, err = _require_openid_list(req, "openid_list")
    if err:
        return None, err
    return _wechat_post_json("/cgi-bin/tags/members/batchunblacklist", access_token, {"openid_list": ids})


def _cmd_user_info(access_token: str, req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    """GET /cgi-bin/user/info"""
    oid = str(req.get("openid") or "").strip()
    if not oid:
        return None, "missing_param: openid"
    lang = str(req.get("lang") or "zh_CN").strip() or "zh_CN"
    return _wechat_get("/cgi-bin/user/info", access_token, {"openid": oid, "lang": lang})


def _cmd_user_list(access_token: str, req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    """POST /cgi-bin/user/get"""
    nxt = str(req.get("next_openid") or "")
    return _wechat_post_json("/cgi-bin/user/get", access_token, {"next_openid": nxt})


def _read_req_json() -> Dict[str, Any]:
    raw = sys.argv[2] if len(sys.argv) >= 3 else ""
    if isinstance(raw, str):
        rs = raw.strip()
        if rs == "-":
            raw = sys.stdin.read()
        elif rs.startswith("@") and len(rs) > 1:
            p = rs[1:].strip()
            safe = _normalize_local_path(p, "request_file")
            if safe["error"]:
                print("Invalid request file path: %s" % safe["message"], file=sys.stderr)
                sys.exit(1)
            try:
                with open(safe["path"], "r", encoding="utf-8") as f:
                    raw = f.read()
            except Exception as e:
                print("Failed to read json file '%s': %s" % (safe["relative"], e), file=sys.stderr)
                sys.exit(1)
    try:
        req = json.loads(raw) if raw.strip() else {}
    except Exception as e:
        print("JSON parse error: %s" % e, file=sys.stderr)
        sys.exit(1)
    if not isinstance(req, dict):
        print("Error: JSON body must be an object.", file=sys.stderr)
        sys.exit(1)
    return req


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  users.py blacklist_get '{\"begin_openid\":\"\"}'\n"
            "  users.py blacklist_add '{\"openid_list\":[\"oXXX\",\"oYYY\"]}'\n"
            "  users.py blacklist_remove '{\"openid_list\":[\"oXXX\"]}'\n"
            "  users.py user_info '{\"openid\":\"oXXX\",\"lang\":\"zh_CN\"}'\n"
            "  users.py user_list '{\"next_openid\":\"\"}'\n"
            "PowerShell 建议: users.py blacklist_remove @out\\req.json\n",
            file=sys.stderr,
        )
        sys.exit(1)

    cmd = sys.argv[1].strip().lower()
    req = _read_req_json()

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

        if cmd == "blacklist_get":
            data, err = _cmd_blacklist_get(token, req)
        elif cmd == "blacklist_add":
            data, err = _cmd_blacklist_add(token, req)
        elif cmd in ("blacklist_remove", "batch_unblacklist"):
            data, err = _cmd_blacklist_remove(token, req)
        elif cmd == "user_info":
            data, err = _cmd_user_info(token, req)
        elif cmd == "user_list":
            data, err = _cmd_user_list(token, req)
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
