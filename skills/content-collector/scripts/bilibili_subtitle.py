#!/usr/bin/env python3
"""Extract AI-generated subtitles from Bilibili videos.

Usage:
    python3 bilibili_subtitle.py <bvid_or_url> [options]

Options:
    --cookie-file PATH   Path to file containing Bilibili cookie string
    --json               Output full JSON (metadata + subtitle list)
    --plain              Output plain text without timestamps
    --part N             Part number for multi-part videos (default: 1)

Cookie priority: --cookie-file > BILIBILI_COOKIE env > Chrome auto-extract (macOS)

Output: By default, each subtitle line with timestamp. Use --json or --plain to change.
"""

import sys
import re
import json
import os
import urllib.request
import urllib.error
import sqlite3
import subprocess
import struct
import hashlib
import tempfile
import shutil

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com/",
}

COOKIE = ""


def fetch_json(url):
    req = urllib.request.Request(url, headers={**HEADERS, "Cookie": COOKIE})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def extract_bvid(input_str):
    m = re.search(r"(BV[a-zA-Z0-9]+)", input_str)
    return m.group(1) if m else input_str


def format_time(seconds):
    """Format seconds to MM:SS or HH:MM:SS."""
    seconds = int(seconds)
    if seconds >= 3600:
        return f"{seconds // 3600}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


# ---------------------------------------------------------------------------
# Cookie extraction from Chrome (macOS)
# ---------------------------------------------------------------------------

def _chrome_decrypt_value(encrypted_value):
    """Decrypt Chrome cookie value on macOS using Keychain."""
    if not encrypted_value or len(encrypted_value) < 4:
        return None
    # v10 prefix means AES-128-CBC encrypted with Chrome Safe Storage key
    if encrypted_value[:3] != b"v10":
        # unencrypted
        return encrypted_value.decode("utf-8", errors="replace")

    try:
        # Get Chrome Safe Storage password from macOS Keychain
        proc = subprocess.run(
            ["security", "find-generic-password", "-s", "Chrome Safe Storage", "-w"],
            capture_output=True, text=True, timeout=5,
        )
        if proc.returncode != 0:
            return None
        password = proc.stdout.strip()

        # Derive key using PBKDF2 (iterations=1003, salt=b'saltysalt', keylen=16)
        import hashlib
        dk = hashlib.pbkdf2_hmac("sha1", password.encode("utf-8"), b"saltysalt", 1003, dklen=16)

        # AES-128-CBC decrypt, IV = 16 bytes of space (0x20)
        # Use openssl CLI to avoid requiring any third-party Python libs
        iv = b" " * 16  # 0x20
        ciphertext = encrypted_value[3:]  # strip v10 prefix

        proc = subprocess.run(
            ["openssl", "enc", "-aes-128-cbc", "-d", "-K", dk.hex(), "-iv", iv.hex()],
            input=ciphertext, capture_output=True, timeout=5,
        )
        if proc.returncode != 0:
            return None
        decrypted = proc.stdout
        # Strip PKCS7 padding
        if decrypted:
            pad_len = decrypted[-1]
            if 0 < pad_len <= 16 and all(b == pad_len for b in decrypted[-pad_len:]):
                decrypted = decrypted[:-pad_len]
        return decrypted.decode("utf-8", errors="replace")
    except Exception:
        return None


def extract_chrome_sessdata():
    """Try to extract SESSDATA from Chrome's cookie database on macOS."""
    if sys.platform != "darwin":
        return None

    cookie_db = os.path.expanduser(
        "~/Library/Application Support/Google/Chrome/Default/Cookies"
    )
    if not os.path.exists(cookie_db):
        return None

    # Copy DB to temp file to avoid SQLite lock issues
    tmp = None
    try:
        tmp = tempfile.mktemp(suffix=".db")
        shutil.copy2(cookie_db, tmp)

        conn = sqlite3.connect(tmp)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT encrypted_value, value FROM cookies "
            "WHERE host_key LIKE '%bilibili.com' AND name = 'SESSDATA' "
            "ORDER BY last_access_utc DESC LIMIT 1"
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        encrypted_value, plain_value = row
        if plain_value:
            return plain_value
        if encrypted_value:
            decrypted = _chrome_decrypt_value(encrypted_value)
            if decrypted:
                return decrypted
    except Exception as e:
        print(f"Warning: Chrome cookie extraction failed: {e}", file=sys.stderr)
    finally:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)
    return None


# ---------------------------------------------------------------------------
# Bilibili API calls
# ---------------------------------------------------------------------------

def get_video_info(bvid):
    """Get video metadata including aid and cid."""
    data = fetch_json(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}")
    if data["code"] != 0:
        raise Exception(f"API error: {data['message']}")
    return data["data"]


def get_subtitle_list(bvid, cid):
    """Fetch subtitle list from player/wbi/v2 endpoint."""
    url = f"https://api.bilibili.com/x/player/wbi/v2?bvid={bvid}&cid={cid}"
    data = fetch_json(url)
    if data["code"] != 0:
        raise Exception(f"Player API error (code {data['code']}): {data.get('message', 'unknown')}")
    subtitles = data.get("data", {}).get("subtitle", {}).get("subtitles", [])
    return subtitles


def pick_chinese_subtitle(subtitles):
    """Pick Chinese subtitle from subtitle list, preferring AI-generated zh."""
    # Priority: ai-zh > zh-CN > zh-Hans > any zh
    for priority in ["ai-zh", "zh-CN", "zh-Hans", "zh"]:
        for s in subtitles:
            lan = s.get("lan", "")
            if lan == priority or lan.startswith(priority):
                return s
    # Fallback: any subtitle with zh in lan
    for s in subtitles:
        if "zh" in s.get("lan", ""):
            return s
    # Last resort: first subtitle
    if subtitles:
        return subtitles[0]
    return None


def download_subtitle(subtitle_url):
    """Download and parse subtitle JSON."""
    if subtitle_url.startswith("//"):
        subtitle_url = "https:" + subtitle_url
    data = fetch_json(subtitle_url)
    return data.get("body", [])


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(1)

    global COOKIE

    bvid = extract_bvid(sys.argv[1])
    output_json = "--json" in sys.argv
    output_plain = "--plain" in sys.argv
    part_num = 1

    # Parse --part
    if "--part" in sys.argv:
        idx = sys.argv.index("--part")
        if idx + 1 < len(sys.argv):
            part_num = int(sys.argv[idx + 1])

    # Cookie resolution: --cookie-file > env > Chrome
    if "--cookie-file" in sys.argv:
        idx = sys.argv.index("--cookie-file")
        if idx + 1 < len(sys.argv):
            with open(sys.argv[idx + 1], "r") as f:
                COOKIE = f.read().strip()

    if not COOKIE:
        COOKIE = os.environ.get("BILIBILI_COOKIE", "")

    if not COOKIE:
        sessdata = extract_chrome_sessdata()
        if sessdata:
            COOKIE = f"SESSDATA={sessdata}"
            print("Info: Using SESSDATA from Chrome cookies", file=sys.stderr)

    if not COOKIE:
        print("Error: No cookie available. AI subtitles require login.", file=sys.stderr)
        print("Provide cookie via one of:", file=sys.stderr)
        print("  1. --cookie-file <path>  (file with cookie string)", file=sys.stderr)
        print("  2. BILIBILI_COOKIE env   (cookie string)", file=sys.stderr)
        print("  3. Login to bilibili.com in Chrome (auto-extract on macOS)", file=sys.stderr)
        sys.exit(1)

    # Step 1: Get video info
    try:
        video = get_video_info(bvid)
    except Exception as e:
        print(f"Error: Failed to get video info for {bvid}: {e}", file=sys.stderr)
        sys.exit(1)

    title = video.get("title", "")
    aid = video.get("aid", 0)

    # Handle multi-part videos
    pages = video.get("pages", [])
    if part_num > 1 and part_num <= len(pages):
        cid = pages[part_num - 1]["cid"]
        part_title = pages[part_num - 1].get("part", "")
    else:
        cid = video.get("cid", 0)
        part_title = ""

    print(f"Info: {title}", file=sys.stderr)
    if part_title:
        print(f"Info: Part {part_num}: {part_title}", file=sys.stderr)

    # Step 2: Get subtitle list
    try:
        subtitles = get_subtitle_list(bvid, cid)
    except Exception as e:
        print(f"Error: Failed to get subtitles: {e}", file=sys.stderr)
        sys.exit(1)

    if not subtitles:
        print("Error: No subtitles available for this video.", file=sys.stderr)
        print("Possible reasons:", file=sys.stderr)
        print("  - Video has no AI-generated subtitles", file=sys.stderr)
        print("  - Cookie may be expired (re-login to bilibili.com)", file=sys.stderr)
        print("  - Video is too short or too new for AI subtitles", file=sys.stderr)
        sys.exit(1)

    # Step 3: Pick Chinese subtitle
    chosen = pick_chinese_subtitle(subtitles)
    sub_url = chosen.get("subtitle_url", "")
    lan = chosen.get("lan", "")
    lan_doc = chosen.get("lan_doc", "")

    print(f"Info: Found subtitle: {lan_doc} ({lan})", file=sys.stderr)

    if not sub_url:
        print("Error: Subtitle URL is empty.", file=sys.stderr)
        sys.exit(1)

    # Step 4: Download subtitle content
    try:
        body = download_subtitle(sub_url)
    except Exception as e:
        print(f"Error: Failed to download subtitle: {e}", file=sys.stderr)
        sys.exit(1)

    if not body:
        print("Error: Subtitle body is empty.", file=sys.stderr)
        sys.exit(1)

    print(f"Info: {len(body)} subtitle lines", file=sys.stderr)

    # Step 5: Output
    if output_json:
        result = {
            "bvid": bvid,
            "aid": aid,
            "cid": cid,
            "title": title,
            "part": part_title if part_title else None,
            "subtitle_lang": lan,
            "subtitle_lang_doc": lan_doc,
            "subtitle_count": len(body),
            "subtitles": [
                {
                    "from": item.get("from", 0),
                    "to": item.get("to", 0),
                    "content": item.get("content", ""),
                }
                for item in body
            ],
        }
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        print()
    elif output_plain:
        for item in body:
            print(item.get("content", ""))
    else:
        # Default: timestamped text
        for item in body:
            t = format_time(item.get("from", 0))
            content = item.get("content", "")
            print(f"[{t}] {content}")


if __name__ == "__main__":
    main()
