# 🔒 Code Security Auditor

> 集各家之所长的综合代码安全审计工具
> 
> 对标 OpenAI Codex Security，完全本地运行，数据不出境

---

## 🎯 能力概览

| 能力 | 说明 | 来源 |
|------|------|------|
| **OWASP Top 10 检测** | SQL 注入、XSS、CSRF、SSRF 等 | security-auditor |
| **依赖漏洞扫描** | npm/pip/cargo/maven 依赖安全检查 | security-audit-toolkit |
| **密钥泄露检测** | API Key、密码、Token 硬编码检测 | truffleHog/gitleaks |
| **SAST 静态分析** | 代码流分析、污点追踪 | pentest/security-reviewer |
| **配置安全审计** | CORS、CSP、SSL/TLS 配置检查 | 综合 |
| **AI 漏洞验证** | 降低误报率、提供修复方案 | Codex Security 参考 |
| **修复代码生成** | 可执行的安全修复代码 | Codex Security 参考 |

---

## 📦 安装

本技能已创建在本地：

```
~/.openclaw/workspace/skills/code-security-auditor/
```

无需额外安装，直接使用即可。

### 依赖工具（可选，增强扫描能力）

```bash
# Python 依赖扫描
pip install pip-audit safety

# Node.js 依赖扫描
npm install -g npm-audit

# 密钥扫描
pip install truffleHog
# 或
go install github.com/zricethezav/gitleaks/v8@latest
```

---

## 🚀 快速开始

```bash
# 完整安全审计
python auditor.py audit /path/to/project

# 快速扫描（仅高危漏洞）
python auditor.py quick /path/to/project

# 生成 JSON 报告
python auditor.py audit . --format json --output report.json

# 生成 Markdown 报告
python auditor.py audit . --format markdown --output report.md

# CI/CD 模式（高危漏洞时失败）
python auditor.py audit . --fail-on high
```

---

## 📋 审计阶段

### Phase 1: 依赖安全扫描
- 扫描 `requirements.txt`、`package.json` 等
- 检测已知 CVE 漏洞
- 提供升级建议

### Phase 2: 密钥泄露检测
- API Keys、Passwords、Tokens
- Private Keys、Cloud Credentials
- 支持 truffleHog/gitleaks 集成

### Phase 3: OWASP Top 10 扫描
- SQL 注入
- XSS（跨站脚本）
- SSRF（服务器端请求伪造）
- 权限控制失效
- 加密失败
- 注入攻击
- 不安全设计
- 配置错误
- 脆弱组件
- 认证失败
- 数据完整性
- 日志失败

### Phase 8: AI 驱动漏洞验证
- 上下文分析
- 防护措施检测
- 误报率优化（目标 ↓50%）

---

## 📊 报告示例

```
🔒 Code Security Audit Report
═══════════════════════════════════════════════════
Project: my-app
Date: 2026-03-07T14:30:00
Duration: 45.2s

Verdict: ❌ FAIL - HIGH SEVERITY VULNERABILITIES FOUND

Summary:
┌─────────────┬───────┬──────────┐
│ Severity    │ Count │ Status   │
├─────────────┼───────┼──────────┤
│ 🔴 CRITICAL │     2 │ FAIL     │
│ 🟠 HIGH     │     5 │ FAIL     │
│ 🟡 MEDIUM   │    12 │ WARN     │
│ 🟢 LOW      │    23 │ INFO     │
└─────────────┴───────┴──────────┘

Top Issues:
1. [CRITICAL] SQL Injection in user_controller.py:45
   → Use parameterized queries

2. [CRITICAL] Hardcoded AWS Key in config.py:12
   → Move to environment variables

3. [HIGH] XSS in template.html:78
   → Escape user input
```

---

## 🔧 修复示例

### SQL 注入修复

**修复前**:
```python
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

**修复后**:
```python
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### XSS 修复

**修复前**:
```python
return f"<div>{user_input}</div>"
```

**修复后**:
```python
from markupsafe import escape
return f"<div>{escape(user_input)}</div>"
```

### SSRF 修复

**修复前**:
```python
requests.get(user_url)
```

**修复后**:
```python
def is_safe_url(url: str) -> bool:
    # 验证协议、IP、云元数据等
    ...

if is_safe_url(user_url):
    requests.get(user_url)
```

---

## 🆚 与 OpenAI Codex Security 对比

| 维度 | Codex Security | Code Security Auditor |
|------|---------------|----------------------|
| **OWASP Top 10** | ✅ | ✅ |
| **依赖扫描** | ✅ | ✅ |
| **密钥检测** | ✅ | ✅ |
| **SAST** | ✅ AI 驱动 | ✅ AI + 规则混合 |
| **误报优化** | ✅ ↓50% | ✅ AI 验证阶段 |
| **修复建议** | ✅ 可执行代码 | ✅ 可执行代码 |
| **本地运行** | ❌ 需上传 OpenAI | ✅ 完全本地 |
| **数据隐私** | ⚠️ 代码出境 | ✅ 代码不出境 |
| **费用** | 付费 | ✅ 免费 |
| **可扩展** | ❌ 封闭 | ✅ 自定义规则 |

---

## ⚠️ 风险声明

1. **本工具不保证发现所有漏洞** — 安全审计应结合人工审查
2. **自动修复需谨慎** — 建议 review 后再应用
3. **生产环境前必须人工确认** — 自动化工具不能替代安全专家
4. **定期更新规则库** — 新漏洞不断出现，保持工具更新

---

## 📚 参考资料

- [OWASP Top 10 2021](https://owasp.org/www-project-top-ten/)
- [CWE - Common Weakness Enumeration](https://cwe.mitre.org/)
- [CVSS Calculator](https://www.first.org/cvss/calculator/3.1)

---

## 🤝 贡献

本技能综合了以下开源项目的能力：

- [security-auditor](https://clawhub.com) - OWASP Top 10 检测
- [security-audit-toolkit](https://clawhub.com) - 依赖/密钥扫描
- [pentest/security-reviewer](https://clawhub.com) - SAST 分析
- [OpenAI Codex Security](https://openai.com) - AI 驱动漏洞验证（参考）

---

_版本：1.0.0 | 创建日期：2026-03-07 | 作者：AI Assistant_
