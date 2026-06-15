---
name: code-security-auditor
description: Comprehensive code security audit with AI-powered vulnerability detection. Covers OWASP Top 10, dependency scanning, secret detection, SAST, and provides actionable fix recommendations. Use when security review, penetration testing, or compliance audit is needed.
---

# Code Security Auditor

综合代码安全审计工具，结合 AI 推理能力与专业安全扫描工具，提供高可信度漏洞发现、可执行修复方案和持续学习优化。

## 🎯 核心能力

| 能力 | 说明 | 对标 Codex Security |
|------|------|---------------------|
| **OWASP Top 10 检测** | SQL 注入、XSS、CSRF、SSRF 等 | ✅ |
| **依赖漏洞扫描** | npm/pip/cargo/maven 依赖安全检查 | ✅ |
| **密钥泄露检测** | API Key、密码、Token 硬编码检测 | ✅ |
| **SAST 静态分析** | 代码流分析、污点追踪 | ✅ |
| **配置安全审计** | CORS、CSP、SSL/TLS 配置检查 | ✅ |
| **修复方案生成** | 提供可执行的安全修复代码 | ✅ |
| **误报率优化** | AI 上下文理解降低误报 | ✅ |

---

## 🚀 快速开始

```bash
# 完整安全审计
code-security-auditor audit <project_path>

# 快速扫描（仅高危漏洞）
code-security-auditor quick <project_path>

# 针对特定漏洞类型
code-security-auditor scan --type sql-injection <project_path>
code-security-auditor scan --type xss <project_path>
code-security-auditor scan --type ssrf <project_path>

# 生成修复建议
code-security-auditor fix <vulnerability_id>

# 与基线对比
code-security-auditor compare --baseline .security-baseline.json
```

---

## 📋 审计阶段（8 阶段深度审计）

### Phase 1: 依赖安全扫描

扫描项目依赖中的已知漏洞。

```bash
# Python
pip-audit
safety check
pipx run pip-audit --format json

# Node.js
npm audit --json
npx audit-ci --config audit-ci.jsonc

# Rust
cargo audit --json

# Java/Maven
mvn org.owasp:dependency-check-maven:check -Dformat=JSON
```

**输出示例**：
```json
{
  "phase": "dependency_scan",
  "verdict": "WARN",
  "findings": [
    {
      "id": "DEP-001",
      "severity": "HIGH",
      "package": "requests",
      "version": "2.28.0",
      "vulnerability": "CVE-2023-32681",
      "description": "信息泄露风险",
      "fix": "升级到 2.31.0+",
      "cvss": 7.5
    }
  ]
}
```

---

### Phase 2: 密钥泄露检测

检测硬编码的敏感信息。

**检测模式**：
```python
# API Keys
r'(api[_-]?key|apikey)\s*[:=]\s*["\'][a-zA-Z0-9]{20,}["\']'

# Passwords
r'(password|passwd|pwd)\s*[:=]\s*["\'].+["\']'

# Tokens
r'(token|secret|auth)\s*[:=]\s*["\'][a-zA-Z0-9_-]{20,}["\']'

# Private Keys
r'-----BEGIN (RSA |EC )?PRIVATE KEY-----'

# Cloud Credentials
r'AKIA[0-9A-Z]{16}'  # AWS Access Key
r'ghp_[a-zA-Z0-9]{36}'  # GitHub Token
```

**工具集成**：
```bash
# truffleHog
trufflehog filesystem <path> --json

# gitleaks
gitleaks detect --source <path> --report-format json

# detect-secrets
detect-secrets scan --all-files > .secrets.baseline
```

---

### Phase 3: OWASP Top 10 漏洞扫描

#### 3.1 SQL 注入检测

**检测模式**：
```python
# 危险模式
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")  # ❌
cursor.execute("SELECT * FROM users WHERE id = " + user_id)  # ❌

# 安全模式
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))  # ✅
```

**扫描规则**：
- 字符串拼接 SQL 语句
- 未使用参数化查询
- 用户输入直接进入查询
- ORM 的 raw query 未转义

---

#### 3.2 XSS（跨站脚本）检测

**检测模式**：
```python
# 危险模式
return f"<div>{user_input}</div>"  # ❌
html = "<span>" + request.args.get('name') + "</span>"  # ❌

# 安全模式
from markupsafe import escape
return f"<div>{escape(user_input)}</div>"  # ✅
```

**扫描规则**：
- 用户输入直接渲染到 HTML
- 未使用模板引擎的自动转义
- innerHTML 直接赋值
- dangerouslySetInnerHTML 使用

---

#### 3.3 SSRF（服务器端请求伪造）检测

**检测模式**：
```python
# 危险模式
requests.get(user_url)  # ❌ 无 URL 验证
urllib.request.urlopen(user_input)  # ❌

# 安全模式
def safe_request(url: str) -> Response:
    parsed = urlparse(url)
    if not is_safe_url(parsed):
        raise ValueError("Unsafe URL")
    return requests.get(url)
```

**扫描规则**：
- requests/urllib 直接使用用户输入
- 未验证 URL 协议（http/https only）
- 未检查内网 IP（169.254.169.254 等）
- 未限制重定向

---

#### 3.4 其他 OWASP Top 10

| 漏洞类型 | 检测重点 |
|---------|---------|
| **A01 权限控制失效** | 未授权访问、IDOR、水平/垂直越权 |
| **A02 加密失败** | 弱加密算法、硬编码密钥、明文存储 |
| **A03 注入** | SQL、NoSQL、命令注入、LDAP 注入 |
| **A04 不安全设计** | 缺少速率限制、无审计日志 |
| **A05 配置错误** | 默认配置、详细错误信息、开放端口 |
| **A06 脆弱组件** | 过期依赖、已知漏洞 |
| **A07 认证失败** | 弱密码、无 MFA、会话固定 |
| **A08 数据完整性** | 无签名验证、反序列化漏洞 |
| **A09 日志失败** | 敏感信息入日志、无审计追踪 |
| **A10 SSRF** | 见上方详细检测 |

---

### Phase 4: 代码流分析（污点追踪）

追踪用户输入从源头到敏感操作的路径。

```python
# 污点源（Source）
user_input = request.args.get('id')  # tainted

# 污点传播
data = process(user_input)  # still tainted
query = build_query(data)  # still tainted

# 污点汇（Sink）
cursor.execute(query)  # VULNERABLE!
```

**AI 增强分析**：
- 跨函数污点追踪
- 识别净化函数（sanitizer）
- 上下文敏感分析
- 降低误报率

---

### Phase 5: 配置安全审计

#### 5.1 Web 服务器配置

```yaml
# CORS 检查
cors:
  allowed_origins: ["*"]  # ❌ 生产环境禁止
  allowed_methods: ["GET", "POST"]
  credentials: true  # ⚠️ 与 * 冲突

# CSP 检查
content_security_policy:
  default_src: ["'self'"]  # ✅
  script_src: ["'self'", "'unsafe-inline'"]  # ⚠️ 避免 unsafe-inline
```

#### 5.2 SSL/TLS 配置

```yaml
ssl:
  min_version: "TLSv1.2"  # ✅ 禁止 TLSv1.0/1.1
  ciphers:  # ✅ 使用强加密套件
    - ECDHE-RSA-AES256-GCM-SHA384
    - ECDHE-RSA-AES128-GCM-SHA256
  hsts: true  # ✅ 启用 HSTS
```

#### 5.3 文件权限

```bash
# 检查敏感文件权限
chmod 600 .env          # ✅
chmod 644 config.yaml   # ✅
chmod 755 scripts/      # ✅
chmod 777 anything      # ❌ 禁止
```

---

### Phase 6: 认证与会话安全

**检查项**：

| 检查点 | 要求 |
|--------|------|
| 密码存储 | bcrypt/argon2，禁止明文/MD5/SHA1 |
| 会话管理 | HttpOnly + Secure + SameSite |
| Token 安全 | JWT 签名验证、合理过期时间 |
| MFA 支持 | 关键操作要求多因素认证 |
| 速率限制 | 登录/注册接口防暴力破解 |
| 账户锁定 | 多次失败后临时锁定 |

---

### Phase 7: 安全日志与监控

**检查项**：

```python
# ✅ 正确的日志
logger.info(f"User {user_id} logged in from {ip}")

# ❌ 错误的日志（泄露敏感信息）
logger.info(f"Login attempt: user={username}, password={password}")
```

**要求**：
- 敏感信息不入日志
- 安全事件完整记录
- 日志完整性保护
- 告警阈值配置

---

### Phase 8: AI 驱动漏洞验证

使用 AI 模型验证潜在漏洞的真实性，降低误报。

```python
# AI 验证流程
def ai_verify_vulnerability(finding: Finding) -> VerificationResult:
    # 1. 分析代码上下文
    context = extract_context(finding.location)
    
    # 2. 检查是否有防护措施
    has_sanitizer = check_sanitizer(context)
    has_validation = check_input_validation(context)
    
    # 3. 生成利用路径
    exploit_path = generate_exploit_path(finding)
    
    # 4. 评估真实风险
    if has_sanitizer and not exploit_path:
        return VerificationResult.FALSE_POSITIVE
    
    return VerificationResult.CONFIRMED
```

**效果**（对标 Codex Security）：
- 误报率 ↓ 50%
- 噪声 ↓ 84%
- 真实漏洞检出率 ↑

---

## 📊 风险评级系统

### CVSS 3.1 评分

| 等级 | 分数范围 | 颜色 |
|------|---------|------|
| **严重 (Critical)** | 9.0 - 10.0 | 🔴 |
| **高危 (High)** | 7.0 - 8.9 | 🟠 |
| **中危 (Medium)** | 4.0 - 6.9 | 🟡 |
| **低危 (Low)** | 0.1 - 3.9 | 🟢 |
| **无风险 (None)** | 0.0 | ⚪ |

### 综合 verdict

```python
def calculate_verdict(findings: List[Finding]) -> str:
    critical_count = sum(1 for f in findings if f.severity == "CRITICAL")
    high_count = sum(1 for f in findings if f.severity == "HIGH")
    
    if critical_count > 0:
        return "FAIL - CRITICAL VULNERABILITIES FOUND"
    elif high_count > 0:
        return "FAIL - HIGH SEVERITY VULNERABILITIES FOUND"
    elif any(f.severity == "MEDIUM" for f in findings):
        return "WARN - MEDIUM SEVERITY ISSUES FOUND"
    elif findings:
        return "PASS WITH INFO - LOW SEVERITY ISSUES FOUND"
    else:
        return "PASS - NO SECURITY ISSUES FOUND"
```

---

## 🔧 修复方案生成

### 自动修复示例

#### SQL 注入修复

**修复前**：
```python
def get_user(user_id: str):
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    return cursor.execute(query)
```

**修复后**：
```python
def get_user(user_id: str):
    query = "SELECT * FROM users WHERE id = %s"
    return cursor.execute(query, (user_id,))
```

#### XSS 修复

**修复前**：
```python
@app.route('/greet')
def greet():
    name = request.args.get('name')
    return f"<h1>Hello, {name}!</h1>"
```

**修复后**：
```python
from markupsafe import escape

@app.route('/greet')
def greet():
    name = request.args.get('name')
    return f"<h1>Hello, {escape(name)}!</h1>"
```

#### SSRF 修复

**修复前**：
```python
def fetch_url(url: str):
    return requests.get(url)
```

**修复后**：
```python
import socket
from urllib.parse import urlparse
import ipaddress

def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ['http', 'https']:
        return False
    
    try:
        ip = socket.gethostbyname(parsed.hostname)
        ip_obj = ipaddress.ip_address(ip)
        # 禁止私有 IP、链路本地、云元数据
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
            return False
        if str(ip_obj) == '169.254.169.254':  # AWS metadata
            return False
        return True
    except:
        return False

def fetch_url(url: str):
    if not is_safe_url(url):
        raise ValueError("Unsafe URL detected")
    return requests.get(url, allow_redirects=False)
```

---

## 📁 配置文件 (.security-audit.yaml)

```yaml
# 项目安全审计配置

# 扫描范围
scope:
  include:
    - "src/**/*"
    - "app/**/*"
  exclude:
    - "**/test/**"
    - "**/vendor/**"
    - "**/node_modules/**"
    - "**/*.min.js"

# 风险阈值
thresholds:
  critical: 0    # 0 个严重漏洞
  high: 0        # 0 个高危漏洞
  medium: 10     # 最多 10 个中危
  low: 50        # 最多 50 个低危

# 规则配置
rules:
  sql_injection:
    enabled: true
    severity: CRITICAL
  xss:
    enabled: true
    severity: HIGH
  ssrf:
    enabled: true
    severity: CRITICAL
  hardcoded_secrets:
    enabled: true
    severity: CRITICAL
  dependency_vulnerabilities:
    enabled: true
    min_severity: HIGH  # 只报告高危以上

# 修复建议
fix_suggestions:
  enabled: true
  auto_fix: false  # 谨慎启用自动修复
  review_required: true

# 报告配置
reporting:
  formats:
    - markdown
    - json
    - sarif  # IDE 集成
  include_code_snippets: true
  include_fix_examples: true
```

---

## 📤 报告输出

### 终端摘要

```
🔒 Code Security Audit Report
═══════════════════════════════════════════════════
Project: my-app @ abc1234
Date: 2026-03-07 14:30:00
Duration: 45.2s

Verdict: ❌ FAIL - HIGH SEVERITY VULNERABILITIES FOUND

Summary:
┌─────────────┬───────┬──────────┐
│ Severity    │ Count │ Status   │
├─────────────┼───────┼──────────┤
│ 🔴 Critical │   2   │  FAIL    │
│ 🟠 High     │   5   │  FAIL    │
│ 🟡 Medium   │  12   │  WARN    │
│ 🟢 Low      │  23   │  INFO    │
└─────────────┴───────┴──────────┘

Top Issues:
1. [CRITICAL] SQL Injection in user_controller.py:45
   → Use parameterized queries
   
2. [CRITICAL] Hardcoded AWS Key in config.py:12
   → Move to environment variables
   
3. [HIGH] XSS in template.html:78
   → Escape user input

4. [HIGH] SSRF in webhook_handler.py:34
   → Validate URL before request

5. [HIGH] Outdated dependency: requests@2.28.0
   → Upgrade to 2.31.0+

Next Steps:
• Run: code-security-auditor fix --all
• Review: .security-audit/report.md
• Compare: code-security-auditor compare --baseline
```

### JSON 报告（机器可读）

```json
{
  "meta": {
    "timestamp": "2026-03-07T14:30:00Z",
    "commit": "abc1234",
    "tool_version": "1.0.0"
  },
  "verdict": "FAIL",
  "summary": {
    "critical": 2,
    "high": 5,
    "medium": 12,
    "low": 23,
    "total": 42
  },
  "findings": [
    {
      "id": "SQL-INJ-001",
      "type": "sql_injection",
      "severity": "CRITICAL",
      "cvss": 9.8,
      "location": {
        "file": "src/controllers/user_controller.py",
        "line": 45,
        "column": 12
      },
      "description": "用户输入直接进入 SQL 查询",
      "evidence": "cursor.execute(f\"SELECT * FROM users WHERE id = '{user_id}'\")",
      "remediation": {
        "description": "使用参数化查询",
        "code": "cursor.execute(\"SELECT * FROM users WHERE id = %s\", (user_id,))"
      },
      "references": [
        "https://owasp.org/www-community/attacks/SQL_Injection",
        "https://cwe.mitre.org/data/definitions/89.html"
      ]
    }
  ]
}
```

### SARIF 格式（IDE 集成）

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Code Security Auditor",
          "version": "1.0.0"
        }
      },
      "results": [
        {
          "ruleId": "SQL-INJ",
          "level": "error",
          "message": {
            "text": "SQL Injection vulnerability detected"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "src/controllers/user_controller.py"
                },
                "region": {
                  "startLine": 45,
                  "startColumn": 12
                }
              }
            }
          ]
        }
      ]
    }
  ]
}
```

---

## 🔄 CI/CD 集成

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
      
      - name: Run Security Audit
        run: |
          code-security-auditor audit . \
            --format sarif \
            --output security-results.sarif \
            --fail-on high
      
      - name: Upload to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: security-results.sarif
      
      - name: Check Baseline
        run: |
          code-security-auditor compare \
            --baseline .security-baseline.json \
            --current security-results.json
```

### GitLab CI

```yaml
security-audit:
  stage: test
  image: python:3.11
  script:
    - pip install code-security-auditor
    - code-security-auditor audit . --fail-on high
  artifacts:
    reports:
      sast: security-results.sarif
```

---

## 📚 参考资源

### OWASP Top 10 2021
- https://owasp.org/www-project-top-ten/

### CWE 通用弱点
- https://cwe.mitre.org/

### 安全编码规范
- Python: https://docs.python.org/3/library/security.html
- Node.js: https://nodejs.org/en/docs/guides/security/

### 漏洞数据库
- NVD: https://nvd.nist.gov/
- CVE: https://cve.mitre.org/

---

## 🎯 与 OpenAI Codex Security 对比

| 能力 | Codex Security | Code Security Auditor |
|------|---------------|----------------------|
| **OWASP Top 10** | ✅ | ✅ |
| **依赖扫描** | ✅ | ✅ |
| **密钥检测** | ✅ | ✅ (truffleHog/gitleaks) |
| **SAST** | ✅ AI 驱动 | ✅ AI + 规则混合 |
| **误报优化** | ✅ ↓50% | ✅ AI 验证阶段 |
| **修复建议** | ✅ 可执行代码 | ✅ 可执行代码 |
| **本地运行** | ❌ 需上传 OpenAI | ✅ 完全本地 |
| **数据隐私** | ⚠️ 代码出境 | ✅ 代码不出境 |
| **费用** | 付费（首月免费） | ✅ 开源免费 |
| **可扩展** | ❌ 封闭 | ✅ 自定义规则 |

---

## ⚠️ 风险声明

1. **本工具不保证发现所有漏洞** — 安全审计应结合人工审查
2. **自动修复需谨慎** — 建议 review 后再应用
3. **生产环境前必须人工确认** — 自动化工具不能替代安全专家
4. **定期更新规则库** — 新漏洞不断出现，保持工具更新

---

## 📝 使用示例

```bash
# 开发阶段快速检查
code-security-auditor quick ./src

# 发布前完整审计
code-security-auditor audit . --output report.md

# 针对 PR 的变更审计
code-security-auditor audit . --changed-only

# 生成修复补丁
code-security-auditor fix --all --review

# 与基线对比（检测回归）
code-security-auditor compare --baseline last-release.json

# 导出 SARIF 供 IDE 使用
code-security-auditor audit . --format sarif --output results.sarif
```

---

_持续学习优化：每次审计结果可反馈到 AI 模型，持续降低误报率、提高检出率。_
