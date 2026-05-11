#!/usr/bin/env python3
"""
TickTick 国际版 一次性 OAuth 授权脚本
（中国版用户请使用 dida-cli：npm install -g @suibiji/dida-cli && dida auth login）

使用方式：
  python3 ticktick_auth.py

授权完成后 token 保存到 ~/.config/timebox/ticktick.json
"""

import http.server, webbrowser, json, urllib.parse, urllib.request, base64, threading
from pathlib import Path

CLIENT_ID     = "在这里填入你的 client_id"
CLIENT_SECRET = "在这里填入你的 client_secret"
REDIRECT_URI  = "http://localhost:8765/callback"
TOKEN_FILE    = Path.home() / ".config" / "timebox" / "ticktick.json"
PORT          = 8765
AUTH_URL      = "https://ticktick.com/oauth/authorize"
TOKEN_URL     = "https://ticktick.com/oauth/token"

received_code = None


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global received_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if "code" in params:
            received_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h2 style='font-family:sans-serif;padding:40px'>✅ 授权成功！可以关闭此页面。</h2>".encode())
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Bad request")
        threading.Thread(target=self.server.shutdown).start()

    def log_message(self, *args): pass


def main():
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)

    server = http.server.HTTPServer(("localhost", PORT), CallbackHandler)

    auth_params = urllib.parse.urlencode({
        "client_id":     CLIENT_ID,
        "response_type": "code",
        "redirect_uri":  REDIRECT_URI,
        "scope":         "tasks:write tasks:read",
    })
    auth_url = f"{AUTH_URL}?{auth_params}"
    print(f"\n正在打开浏览器授权页...")
    print(f"如未自动打开，请手动访问：\n{auth_url}\n")
    webbrowser.open(auth_url)

    print("等待授权完成（在浏览器中点击同意）...")
    server.serve_forever()

    if not received_code:
        print("❌ 未收到授权码，请重试")
        return

    print("✓ 收到授权码，正在换取 Token...")

    credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    token_data = urllib.parse.urlencode({
        "grant_type":   "authorization_code",
        "code":         received_code,
        "redirect_uri": REDIRECT_URI,
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=token_data, method="POST")
    req.add_header("Authorization", f"Basic {credentials}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req) as resp:
            token = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"❌ Token 换取失败：HTTP {e.code}\n{e.read().decode()}")
        return

    TOKEN_FILE.write_text(json.dumps(token, indent=2, ensure_ascii=False))
    print(f"\n✅ 授权成功！Token 已保存到：{TOKEN_FILE}")
    print(f"   token_type  : {token.get('token_type', '?')}")
    print(f"   expires_in  : {token.get('expires_in', '?')} 秒")
    print(f"   scope       : {token.get('scope', '?')}")


if __name__ == "__main__":
    main()
