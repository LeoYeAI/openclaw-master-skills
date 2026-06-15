# Test file for Code Security Auditor
# 包含各种安全漏洞示例，用于测试检测能力

import os
import sqlite3
import requests
from flask import Flask, request

app = Flask(__name__)

# ============== 漏洞示例 ==============

# 🔴 CRITICAL: SQL 注入
def get_user_vulnerable(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # 危险：f-string 直接拼接 SQL
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchone()

# 🔴 CRITICAL: 硬编码 API Key
API_KEY = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"

# 🔴 CRITICAL: SSRF 漏洞
def fetch_url_vulnerable(url):
    # 危险：直接使用用户输入的 URL
    return requests.get(url)

# 🟠 HIGH: XSS 漏洞
@app.route('/greet')
def greet_vulnerable():
    name = request.args.get('name', '')
    # 危险：直接渲染用户输入到 HTML
    return f"<h1>Hello, {name}!</h1>"

# 🟠 HIGH: 命令注入
def ping_host(host):
    # 危险：os.system 直接执行用户输入
    os.system(f"ping -c 4 {host}")

# 🟠 HIGH: 弱加密
import hashlib
def hash_password_weak(password):
    # 危险：使用 MD5 哈希密码
    return hashlib.md5(password.encode()).hexdigest()

# 🟡 MEDIUM: 敏感信息入日志
import logging
logger = logging.getLogger(__name__)

def log_login(username, password):
    # 危险：记录密码到日志
    logger.info(f"Login attempt: user={username}, password={password}")

# ============== 安全示例 ==============

# ✅ 安全：参数化查询
def get_user_safe(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# ✅ 安全：使用环境变量
API_KEY_SAFE = os.environ.get('API_KEY')

# ✅ 安全：URL 验证
import socket
import ipaddress
from urllib.parse import urlparse

def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            return False
        ip = socket.gethostbyname(parsed.hostname)
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private or ip_obj.is_loopback:
            return False
        return True
    except:
        return False

def fetch_url_safe(url):
    if is_safe_url(url):
        return requests.get(url, allow_redirects=False)
    raise ValueError("Unsafe URL")

# ✅ 安全：XSS 防护
from markupsafe import escape

@app.route('/greet-safe')
def greet_safe():
    name = request.args.get('name', '')
    return f"<h1>Hello, {escape(name)}!</h1>"

# ✅ 安全：使用 subprocess
def ping_host_safe(host):
    import subprocess
    subprocess.run(['ping', '-c', '4', host], check=True)

# ✅ 安全：强加密
import bcrypt
def hash_password_safe(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# ✅ 安全：日志脱敏
def log_login_safe(username, success):
    logger.info(f"Login attempt: user={username}, success={success}")
