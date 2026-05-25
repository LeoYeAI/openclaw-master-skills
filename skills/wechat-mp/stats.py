#!/usr/bin/env python3
"""
WeChat MP analytics/statistics.
数据统计（datacube）：图文群发、阅读、分享、用户增减等。
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


def _require_str(req: Dict[str, Any], key: str) -> Tuple[Optional[str], Optional[str]]:
    val = req.get(key)
    if val in (None, ""):
        return None, "missing_param: %s" % key
    return str(val), None


def _require_dates(req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    begin_date, err = _require_str(req, "begin_date")
    if err:
        return None, err
    end_date, err = _require_str(req, "end_date")
    if err:
        return None, err
    if len(begin_date) != 10 or len(end_date) != 10:
        return None, "invalid_param: begin_date/end_date must be 'YYYY-MM-DD'"
    return {"begin_date": begin_date, "end_date": end_date}, None


def _call_datacube(access_token: str, endpoint: str, req: Dict[str, Any]) -> Tuple[Optional[dict], Optional[str]]:
    payload, err = _require_dates(req)
    if err:
        return None, err
    return _wechat_post_json("/datacube/" + endpoint, access_token, payload)


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  stats.py articlesummary '{\"begin_date\":\"2026-03-01\",\"end_date\":\"2026-03-01\"}'\n"
            "  stats.py articletotal   '{\"begin_date\":\"2026-03-01\",\"end_date\":\"2026-03-01\"}'\n"
            "  stats.py userread       '{\"begin_date\":\"2026-03-01\",\"end_date\":\"2026-03-07\"}'\n"
            "  stats.py usershare      '{\"begin_date\":\"2026-03-01\",\"end_date\":\"2026-03-07\"}'\n"
            "  stats.py usercumulate   '{\"begin_date\":\"2026-03-01\",\"end_date\":\"2026-03-07\"}'\n",
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

    mapping = {
        "articlesummary": "getarticlesummary",
        "articletotal": "getarticletotal",
        "userread": "getuserread",
        "usershare": "getusershare",
        "usercumulate": "getusercumulate",
    }
    endpoint = mapping.get(cmd)
    if not endpoint:
        _json_out(
            {
                "error": "unknown_command",
                "message": "unknown command: %s" % cmd,
                "supported": sorted(mapping.keys()),
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

        data, err = _call_datacube(token, endpoint, req)
        if err:
            results.append({"account": name, "error": "api_call_failed", "message": err})
        else:
            results.append({"account": name, "ok": True, "result": data})
        time.sleep(0.2)

    _json_out({"ok": True, "command": cmd, "endpoint": endpoint, "accounts": results})


if __name__ == "__main__":
    main()

