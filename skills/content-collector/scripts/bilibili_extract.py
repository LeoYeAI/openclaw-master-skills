#!/usr/bin/env python3
"""Extract video info and comments from Bilibili via public API.

Usage:
    python3 bilibili_extract.py <bvid_or_url> [--comments N] [--cookie-file PATH]

Output: JSON to stdout with video metadata + top comments.
"""

import sys
import re
import json
import urllib.request
import urllib.error
import os
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com/",
}

COOKIE = ""

def fetch_json(url, extra_headers=None):
    headers = {**HEADERS, "Cookie": COOKIE}
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def extract_bvid(input_str):
    m = re.search(r"(BV[a-zA-Z0-9]+)", input_str)
    return m.group(1) if m else input_str

def get_video_info(bvid):
    data = fetch_json(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}")
    if data["code"] != 0:
        raise Exception(f"API error: {data['message']}")
    v = data["data"]
    return {
        "bvid": v["bvid"],
        "aid": v["aid"],
        "title": v["title"],
        "description": v.get("desc", ""),
        "author": v["owner"]["name"],
        "author_mid": v["owner"]["mid"],
        "duration_seconds": v["duration"],
        "duration_display": f"{v['duration']//60}:{v['duration']%60:02d}",
        "publish_date": datetime.fromtimestamp(v["pubdate"]).strftime("%Y-%m-%d"),
        "cover": v["pic"],
        "tags_from_page": [],
        "cid": v["cid"],
        "stats": {
            "views": v["stat"]["view"],
            "danmaku": v["stat"]["danmaku"],
            "comments": v["stat"]["reply"],
            "favorites": v["stat"]["favorite"],
            "coins": v["stat"]["coin"],
            "shares": v["stat"]["share"],
            "likes": v["stat"]["like"],
        },
    }

def get_video_tags(bvid):
    try:
        data = fetch_json(f"https://api.bilibili.com/x/tag/archive/tags?bvid={bvid}")
        if data["code"] == 0 and data.get("data"):
            return [t["tag_name"] for t in data["data"]]
    except Exception:
        pass
    return []

def get_comments(aid, max_comments=30, cookie_sessdata=None):
    """Fetch comments. With cookie_sessdata, can paginate up to 20 pages (400 comments)."""
    comments = []
    seen = set()

    max_pages = 20 if cookie_sessdata else 5
    extra_headers = {"Cookie": f"SESSDATA={cookie_sessdata}"} if cookie_sessdata else None

    for pn in range(1, max_pages + 1):
        try:
            data = fetch_json(
                f"https://api.bilibili.com/x/v2/reply?type=1&oid={aid}&sort=2&pn={pn}&ps=20",
                extra_headers=extra_headers,
            )
            if data["code"] != 0:
                break

            # top replies (only on page 1)
            if pn == 1:
                for r in (data.get("data", {}).get("top_replies") or []):
                    c = _parse_comment(r)
                    if c and c["message"] not in seen:
                        seen.add(c["message"])
                        c["is_top"] = True
                        comments.append(c)

            replies = data.get("data", {}).get("replies") or []
            if not replies:
                break

            for r in replies:
                c = _parse_comment(r)
                if c and c["message"] not in seen:
                    seen.add(c["message"])
                    comments.append(c)

            if len(comments) >= max_comments:
                break
        except Exception as e:
            print(f"Warning: error fetching comments page {pn}: {e}", file=sys.stderr)
            break

    # sort by likes descending
    comments.sort(key=lambda x: x.get("likes", 0), reverse=True)
    return comments[:max_comments]

def _parse_comment(r):
    member = r.get("member", {})
    content = r.get("content", {})
    msg = content.get("message", "")
    if not msg:
        return None
    comment = {
        "user": member.get("uname", ""),
        "likes": r.get("like", 0),
        "reply_count": r.get("rcount", 0),
        "message": msg,
        "is_top": False,
        "sub_replies": [],
    }
    for sr in (r.get("replies") or [])[:3]:
        sm = sr.get("member", {})
        sc = sr.get("content", {})
        comment["sub_replies"].append({
            "user": sm.get("uname", ""),
            "likes": sr.get("like", 0),
            "message": sc.get("message", ""),
        })
    return comment

def get_subtitle(bvid, cid):
    """Try to get subtitle/CC if available."""
    try:
        data = fetch_json(
            f"https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}"
        )
        subtitles = data.get("data", {}).get("subtitle", {}).get("subtitles", [])
        if subtitles:
            sub_url = subtitles[0].get("subtitle_url", "")
            if sub_url:
                if sub_url.startswith("//"):
                    sub_url = "https:" + sub_url
                sub_data = fetch_json(sub_url)
                lines = sub_data.get("body", [])
                return [{"from": l["from"], "to": l["to"], "content": l["content"]} for l in lines]
    except Exception:
        pass
    return []

def _extract_sessdata(text):
    """Extract SESSDATA value from cookie text (e.g. 'SESSDATA=abc123' or full cookie string)."""
    m = re.search(r"SESSDATA=([^\s;]+)", text)
    return m.group(1) if m else None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 bilibili_extract.py <bvid_or_url> [--comments N] [--cookie-file PATH]", file=sys.stderr)
        sys.exit(1)

    global COOKIE

    bvid = extract_bvid(sys.argv[1])
    max_comments = 30
    cookie_sessdata = None

    if "--comments" in sys.argv:
        idx = sys.argv.index("--comments")
        if idx + 1 < len(sys.argv):
            max_comments = int(sys.argv[idx + 1])

    if "--cookie-file" in sys.argv:
        idx = sys.argv.index("--cookie-file")
        if idx + 1 < len(sys.argv):
            with open(sys.argv[idx + 1], "r") as f:
                cookie_text = f.read().strip()
            COOKIE = cookie_text
            cookie_sessdata = _extract_sessdata(cookie_text)

    # Also check env
    if not COOKIE:
        env_cookie = os.environ.get("BILIBILI_COOKIE", "")
        if env_cookie:
            COOKIE = env_cookie
            cookie_sessdata = _extract_sessdata(env_cookie)

    info = get_video_info(bvid)
    info["tags_from_page"] = get_video_tags(bvid)
    info["comments"] = get_comments(info["aid"], max_comments, cookie_sessdata=cookie_sessdata)
    info["subtitle"] = get_subtitle(bvid, info["cid"])
    info["has_subtitle"] = len(info["subtitle"]) > 0
    info["comment_count_fetched"] = len(info["comments"])

    json.dump(info, sys.stdout, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
