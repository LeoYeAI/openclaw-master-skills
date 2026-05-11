"""Weiyun login module - supports QR code login and cookies login."""

import io
import json
import time
import argparse
import requests

try:
    import qrcode
except ImportError:
    qrcode = None

from weiyun_skills.utils import (
    parse_cookies_str,
    cookies_dict_to_str,
    get_timestamp,
    build_response,
)

# Weiyun QR code login endpoints
XLOGIN_URL = "https://xui.ptlogin2.qq.com/cgi-bin/xlogin"
PTQRSHOW_URL = "https://ssl.ptlogin2.qq.com/ptqrshow"
PTQRLOGIN_URL = "https://ssl.ptlogin2.qq.com/ptqrlogin"
CHECK_URL = "https://www.weiyun.com/disk"

DEFAULT_COOKIES_PATH = "cookies.json"


def _save_cookies(cookies_data: dict, save_path: str) -> None:
    """Save cookies data to a JSON file.

    Args:
        cookies_data: Cookies data to save.
        save_path: File path to save cookies.
    """
    cookies_data["update_time"] = get_timestamp()
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(cookies_data, f, ensure_ascii=False, indent=2)


def load_cookies(save_path: str = DEFAULT_COOKIES_PATH) -> dict:
    """Load cookies from a JSON file.

    Args:
        save_path: Path to cookies file.

    Returns:
        Cookies data dict, or empty dict if file not found.
    """
    try:
        with open(save_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _display_qr_terminal(img_bytes: bytes) -> None:
    """Display QR code image in terminal using ASCII art.

    Args:
        img_bytes: QR code image bytes.
    """
    if qrcode is None:
        print("[ERROR] qrcode package not installed. Run: pip install qrcode[pil]")
        return

    try:
        from PIL import Image
        img = Image.open(io.BytesIO(img_bytes))
        # Convert image to ASCII QR code for terminal display
        img = img.convert("L")
        width, height = img.size
        # Scale down for terminal
        scale = max(1, width // 40)
        for y in range(0, height, scale * 2):
            line = ""
            for x in range(0, width, scale):
                pixel = img.getpixel((min(x, width - 1), min(y, height - 1)))
                line += "██" if pixel < 128 else "  "
            print(line)
    except ImportError:
        print("[ERROR] Pillow package not installed. Run: pip install Pillow")


def qrcode_login(save_path: str = DEFAULT_COOKIES_PATH) -> dict:
    """Login to Weiyun via QR code scanning.

    Displays a QR code in terminal for the user to scan with WeChat/QQ.
    After successful login, cookies are saved to the specified file.

    Args:
        save_path: Path to save cookies file.

    Returns:
        Response dict with login result.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.weiyun.com/",
    })

    # Step 1: Visit xlogin page to get initial cookies
    print("[*] Initializing QR code login...")
    try:
        xlogin_params = {
            "appid": "527020901",
            "daid": "372",
            "style": "33",
            "login_text": "登录",
            "hide_title_bar": "1",
            "hide_border": "1",
            "target": "self",
            "s_url": "https://www.weiyun.com/web/callback/common_qq_login_ok.html",
            "pt_3rd_aid": "0",
            "pt_feedback_link": "https://support.qq.com/",
        }
        session.get(XLOGIN_URL, params=xlogin_params, timeout=10)
    except requests.RequestException as e:
        return build_response(False, message=f"Failed to init login: {e}",
                              error_code="NETWORK_ERROR")

    # Step 2: Get QR code image
    print("[*] Fetching QR code...")
    try:
        qr_params = {
            "appid": "527020901",
            "e": "2",
            "l": "M",
            "s": "3",
            "d": "72",
            "v": "4",
            "t": str(time.time()),
            "daid": "372",
            "pt_3rd_aid": "0",
        }
        qr_resp = session.get(PTQRSHOW_URL, params=qr_params, timeout=10)
        if qr_resp.status_code != 200:
            return build_response(False, message="Failed to get QR code",
                                  error_code="NETWORK_ERROR")

        # Get qrsig cookie for polling
        qrsig = session.cookies.get("qrsig", "")
        if not qrsig:
            return build_response(False, message="Failed to get qrsig cookie",
                                  error_code="AUTH_FAILED")

    except requests.RequestException as e:
        return build_response(False, message=f"Failed to fetch QR code: {e}",
                              error_code="NETWORK_ERROR")

    # Step 3: Display QR code in terminal
    print("\n" + "=" * 50)
    print("  Scan the QR code below with WeChat/QQ")
    print("=" * 50 + "\n")
    _display_qr_terminal(qr_resp.content)
    print("\n" + "=" * 50)
    print("  Waiting for scan...")
    print("=" * 50 + "\n")

    # Step 4: Poll for login result
    def _hash33(t: str) -> int:
        """Hash function for ptqrtoken."""
        e = 0
        for c in t:
            e += (e << 5) + ord(c)
        return e & 0x7FFFFFFF

    ptqrtoken = _hash33(qrsig)
    max_attempts = 60  # Wait up to ~120 seconds
    for attempt in range(max_attempts):
        try:
            poll_params = {
                "u1": "https://www.weiyun.com/web/callback/common_qq_login_ok.html",
                "ptqrtoken": str(ptqrtoken),
                "ptredirect": "0",
                "h": "1",
                "t": "1",
                "g": "1",
                "from_ui": "1",
                "ptlang": "2052",
                "action": f"0-0-{int(time.time() * 1000)}",
                "js_ver": "24012815",
                "js_type": "1",
                "login_sig": session.cookies.get("pt_login_sig", ""),
                "pt_uistyle": "40",
                "aid": "527020901",
                "daid": "372",
                "pt_3rd_aid": "0",
                "o1vId": "",
            }
            poll_resp = session.get(PTQRLOGIN_URL, params=poll_params, timeout=10)
            resp_text = poll_resp.text

            if "登录成功" in resp_text or "登陆成功" in resp_text:
                print("[✓] Login successful!")

                # Extract redirect URL and follow it to get final cookies
                import re
                url_match = re.search(r"'(https?://[^']+)'", resp_text)
                if url_match:
                    redirect_url = url_match.group(1)
                    session.get(redirect_url, timeout=10, allow_redirects=True)

                # Collect all cookies
                all_cookies = {}
                for cookie in session.cookies:
                    all_cookies[cookie.name] = cookie.value

                cookies_str = cookies_dict_to_str(all_cookies)
                cookies_data = {
                    "cookies_str": cookies_str,
                    "cookies_dict": all_cookies,
                    "uin": all_cookies.get("uin", ""),
                }

                _save_cookies(cookies_data, save_path)

                return build_response(True, data={
                    "uin": all_cookies.get("uin", ""),
                    "nickname": "",
                    "cookies_str": cookies_str,
                    "save_path": save_path,
                })

            elif "二维码未失效" in resp_text:
                pass  # QR code still valid, keep waiting
            elif "二维码认证中" in resp_text or "已扫描" in resp_text:
                print("[*] QR code scanned, waiting for confirmation...")
            elif "二维码已失效" in resp_text:
                print("[✗] QR code expired!")
                return build_response(False, message="QR code expired",
                                      error_code="QR_EXPIRED")
            elif "本次登录已被拒绝" in resp_text:
                print("[✗] Login cancelled by user!")
                return build_response(False, message="Login cancelled",
                                      error_code="QR_CANCELLED")

        except requests.RequestException:
            pass

        time.sleep(2)

    return build_response(False, message="Login timeout", error_code="QR_EXPIRED")


def cookies_login(cookies_str: str,
                  save_path: str = DEFAULT_COOKIES_PATH) -> dict:
    """Login to Weiyun using cookies copied from browser.

    Args:
        cookies_str: Cookie string from browser DevTools.
        save_path: Path to save cookies file.

    Returns:
        Response dict with login result.
    """
    if not cookies_str or not cookies_str.strip():
        return build_response(False, message="Cookies string is empty",
                              error_code="INVALID_PARAM")

    cookies_dict = parse_cookies_str(cookies_str)

    # Verify cookies by making a test request
    print("[*] Verifying cookies...")
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.weiyun.com/",
    })
    session.cookies.update(cookies_dict)

    try:
        resp = session.get("https://www.weiyun.com/disk", timeout=10,
                           allow_redirects=False)
        # If we get redirected to login page, cookies are invalid
        if resp.status_code in (301, 302):
            location = resp.headers.get("Location", "")
            if "login" in location.lower() or "xui.ptlogin2" in location:
                return build_response(False,
                                      message="Cookies are invalid or expired",
                                      error_code="AUTH_EXPIRED")
    except requests.RequestException as e:
        return build_response(False, message=f"Verification failed: {e}",
                              error_code="NETWORK_ERROR")

    print("[✓] Cookies verified successfully!")

    # Save cookies
    cookies_data = {
        "cookies_str": cookies_str.strip(),
        "cookies_dict": cookies_dict,
        "uin": cookies_dict.get("uin", ""),
    }
    _save_cookies(cookies_data, save_path)

    return build_response(True, data={
        "uin": cookies_dict.get("uin", ""),
        "nickname": "",
        "save_path": save_path,
    })


def main():
    """CLI entry point for login."""
    parser = argparse.ArgumentParser(description="Weiyun Login Tool")
    parser.add_argument(
        "--method", choices=["qrcode", "cookies"], default="qrcode",
        help="Login method: qrcode (scan QR code) or cookies (paste cookies)"
    )
    parser.add_argument(
        "--cookies", type=str, default="",
        help="Cookie string from browser (required for cookies method)"
    )
    parser.add_argument(
        "--save-path", type=str, default=DEFAULT_COOKIES_PATH,
        help=f"Path to save cookies file (default: {DEFAULT_COOKIES_PATH})"
    )
    args = parser.parse_args()

    if args.method == "qrcode":
        result = qrcode_login(save_path=args.save_path)
    elif args.method == "cookies":
        if not args.cookies:
            print("[ERROR] --cookies argument is required for cookies method")
            print("Usage: python login.py --method cookies --cookies \"your_cookies\"")
            return
        result = cookies_login(args.cookies, save_path=args.save_path)
    else:
        print(f"[ERROR] Unknown method: {args.method}")
        return

    if result["success"]:
        print(f"\n[✓] Login successful! Cookies saved to: {result['data']['save_path']}")
    else:
        print(f"\n[✗] Login failed: {result['message']}")


if __name__ == "__main__":
    main()
