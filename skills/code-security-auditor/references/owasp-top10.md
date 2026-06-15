# Code Security Auditor - 参考文档

## 已集成的安全审计能力

本技能综合了以下开源安全工具/技能的核心能力：

### 1. security-auditor (ClawHub)
- **来源**: jgarrison929
- **核心能力**: OWASP Top 10 检测、认证流程、CORS/CSP 配置
- **已集成**: SQL 注入、XSS、CSRF、SSRF 检测规则

### 2. security-audit-toolkit (ClawHub)
- **来源**: gitgoodordietrying
- **核心能力**: 依赖漏洞扫描、密钥检测、SSL/TLS 审计
- **已集成**: pip-audit、npm audit、truffleHog 集成

### 3. pentest/security-reviewer (ClawHub)
- **来源**: Veeramanikandanr48
- **核心能力**: SAST 扫描、渗透测试、DevSecOps
- **已集成**: 代码流分析、污点追踪

### 4. OpenAI Codex Security (参考)
- **来源**: OpenAI
- **核心能力**: AI 驱动漏洞验证、修复方案生成
- **已集成**: AI 误报优化、可执行修复代码

### 5. code-qc (本地已有)
- **来源**: 本地技能
- **核心能力**: 代码质量审计、静态分析
- **已集成**: 项目结构、执行流程

---

## OWASP Top 10 2021 详细检测规则

### A01:2021 权限控制失效

**检测点**:
- 未授权访问敏感接口
- IDOR (Insecure Direct Object Reference)
- 水平/垂直越权

**示例代码**:
```python
# ❌ 危险：未检查权限
def get_user_data(user_id):
    return db.query(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ 安全：检查当前用户权限
def get_user_data(current_user, requested_user_id):
    if current_user.id != requested_user_id and not current_user.is_admin:
        raise PermissionError("Access denied")
    return db.query("SELECT * FROM users WHERE id = %s", (requested_user_id,))
```

---

### A02:2021 加密失败

**检测点**:
- 弱加密算法 (MD5, SHA1, DES)
- 硬编码加密密钥
- 敏感数据明文存储

**示例代码**:
```python
# ❌ 危险：弱加密
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()

# ✅ 安全：使用 bcrypt
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

---

### A03:2021 注入

**检测点**:
- SQL 注入
- NoSQL 注入
- 命令注入
- LDAP 注入

**示例代码**:
```python
# ❌ 危险：命令注入
os.system(f"ping {user_input}")

# ✅ 安全：使用 subprocess + 参数化
subprocess.run(['ping', user_input], check=True)
```

---

### A04:2021 不安全设计

**检测点**:
- 缺少速率限制
- 无审计日志
- 不安全的业务逻辑

**示例代码**:
```python
# ❌ 危险：无限重试
def login(username, password):
    return authenticate(username, password)

# ✅ 安全：速率限制 + 账户锁定
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=5, period=60)
def login(username, password):
    if check_failed_attempts(username) > 5:
        lock_account(username)
        raise AccountLockedException()
    return authenticate(username, password)
```

---

### A05:2021 配置错误

**检测点**:
- 默认配置未修改
- 详细错误信息泄露
- 不必要的开放端口

**检查清单**:
- [ ] 生产环境关闭 DEBUG 模式
- [ ] 移除默认账户/密码
- [ ] 禁用目录列表
- [ ] 配置安全头 (CSP, HSTS, X-Frame-Options)

---

### A06:2021 脆弱组件

**检测点**:
- 过期依赖
- 已知漏洞组件
- 不再维护的库

**工具集成**:
- Python: pip-audit, safety
- Node.js: npm audit, audit-ci
- Rust: cargo-audit
- Java: OWASP Dependency-Check

---

### A07:2021 认证失败

**检测点**:
- 弱密码策略
- 无 MFA
- 会话固定
- 凭证泄露

**最佳实践**:
```python
# 密码策略
def validate_password(password):
    if len(password) < 12:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*]', password):
        return False
    return True

# 会话管理
from flask_session import Session
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

---

### A08:2021 数据完整性

**检测点**:
- 无签名验证
- 反序列化漏洞
- 数据篡改

**示例代码**:
```python
# ❌ 危险：无签名验证
import pickle
data = pickle.loads(user_input)

# ✅ 安全：使用签名
import hmac
signature = hmac.new(secret_key, data, hashlib.sha256).digest()
# 验证签名后再使用数据
```

---

### A09:2021 日志失败

**检测点**:
- 敏感信息入日志
- 无审计追踪
- 日志可篡改

**示例代码**:
```python
# ❌ 危险：记录敏感信息
logger.info(f"Login: user={username}, password={password}")

# ✅ 安全：脱敏记录
logger.info(f"Login attempt: user={username}, ip={request.remote_addr}, success={success}")
```

---

### A10:2021 SSRF

**检测点**:
- 用户输入直接进入 URL
- 未验证协议
- 未检查内网 IP

**示例代码**:
```python
import socket
import ipaddress
from urllib.parse import urlparse

def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    
    # 只允许 http/https
    if parsed.scheme not in ['http', 'https']:
        return False
    
    try:
        ip = socket.gethostbyname(parsed.hostname)
        ip_obj = ipaddress.ip_address(ip)
        
        # 禁止私有 IP
        if ip_obj.is_private:
            return False
        if ip_obj.is_loopback:
            return False
        if ip_obj.is_link_local:
            return False
        
        # 禁止云元数据
        if str(ip_obj) == '169.254.169.254':
            return False
        
        return True
    except:
        return False

# 使用
if is_safe_url(user_url):
    requests.get(user_url)
else:
    raise ValueError("Unsafe URL")
```

---

## 密钥检测正则表达式

```python
SECRET_PATTERNS = [
    # API Keys
    (r'(?:api[_-]?key|apikey)\s*[:=]\s*["\'][a-zA-Z0-9_-]{20,}["\']', 'API Key'),
    
    # Passwords
    (r'(?:password|passwd|pwd)\s*[:=]\s*["\'].+["\']', 'Hardcoded Password'),
    
    # Tokens
    (r'(?:secret|token)\s*[:=]\s*["\'][a-zA-Z0-9_-]{20,}["\']', 'Secret/Token'),
    
    # Private Keys
    (r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----', 'Private Key'),
    
    # AWS
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
    (r'aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40}', 'AWS Secret Key'),
    
    # GitHub
    (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Personal Token'),
    (r'gho_[a-zA-Z0-9]{36}', 'GitHub OAuth Token'),
    (r'ghu_[a-zA-Z0-9]{36}', 'GitHub User Token'),
    
    # OpenAI
    (r'sk-[a-zA-Z0-9]{48}', 'OpenAI API Key'),
    
    # Google
    (r'AIza[0-9A-Za-z_-]{35}', 'Google API Key'),
    
    # Slack
    (r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}', 'Slack Token'),
    
    # JWT
    (r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*', 'JWT Token'),
]
```

---

## 修复代码模板库

### SQL 注入修复

**Python (sqlite3)**:
```python
# Before
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# After
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

**Python (MySQL)**:
```python
# Before
cursor.execute(f"SELECT * FROM users WHERE name = '{name}'")

# After
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
```

**Python (Django)**:
```python
# Before
User.objects.raw(f"SELECT * FROM users WHERE id = {user_id}")

# After
User.objects.filter(id=user_id)
```

**Node.js (mysql)**:
```javascript
// Before
connection.query(`SELECT * FROM users WHERE id = ${userId}`);

// After
connection.query('SELECT * FROM users WHERE id = ?', [userId]);
```

---

### XSS 修复

**Python (Flask)**:
```python
from markupsafe import escape

# Before
return f"<div>{user_input}</div>"

# After
return f"<div>{escape(user_input)}</div>"
```

**Python (Django)**:
```python
from django.utils.html import escape

# Before
return format_html("<div>{}</div>", user_input)

# After
return format_html("<div>{}</div>", escape(user_input))
```

**JavaScript (React)**:
```jsx
// Before
<div dangerouslySetInnerHTML={{__html: userContent}} />

// After
<div>{userContent}</div>  // React 默认转义
```

---

### SSRF 修复

**Python (通用)**:
```python
import socket
import ipaddress
from urllib.parse import urlparse

def is_safe_url(url: str, allowed_schemes=['http', 'https']) -> bool:
    try:
        parsed = urlparse(url)
        
        # 检查协议
        if parsed.scheme not in allowed_schemes:
            return False
        
        # 解析 IP
        ip = socket.gethostbyname(parsed.hostname)
        ip_obj = ipaddress.ip_address(ip)
        
        # 检查 IP 类型
        if ip_obj.is_private:
            return False
        if ip_obj.is_loopback:
            return False
        if ip_obj.is_link_local:
            return False
        if ip_obj.is_multicast:
            return False
        
        # 检查云元数据 IP
        cloud_metadata_ips = [
            '169.254.169.254',  # AWS
            '100.100.100.200',  # Alibaba
            '168.63.129.16',    # Azure
        ]
        if str(ip_obj) in cloud_metadata_ips:
            return False
        
        return True
    except Exception:
        return False

def safe_get(url: str, **kwargs):
    if not is_safe_url(url):
        raise ValueError(f"Unsafe URL: {url}")
    return requests.get(url, allow_redirects=False, **kwargs)
```

---

## CI/CD 集成模板

### GitHub Actions
```yaml
name: Security Audit

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  security-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install security auditor
        run: |
          pip install pip-audit safety
          npm install -g npm-audit
      
      - name: Run Security Audit
        run: |
          python auditor.py audit . \
            --format sarif \
            --output security-results.sarif \
            --fail-on high
      
      - name: Upload to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: security-results.sarif
```

### GitLab CI
```yaml
security-audit:
  stage: test
  image: python:3.11
  before_script:
    - pip install pip-audit safety
  script:
    - python auditor.py audit . --fail-on high
  artifacts:
    reports:
      sast: security-results.sarif
    paths:
      - security-results.sarif
```

---

## 参考资料

- [OWASP Top 10 2021](https://owasp.org/www-project-top-ten/)
- [CWE - Common Weakness Enumeration](https://cwe.mitre.org/)
- [CVSS Calculator](https://www.first.org/cvss/calculator/3.1)
- [SARIF Specification](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning)
