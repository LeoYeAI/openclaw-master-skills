#!/usr/bin/env python3
"""
Code Security Auditor - 综合代码安全审计工具

集各家之所长：
- OWASP Top 10 检测 (security-auditor)
- 依赖漏洞扫描 (security-audit-toolkit)
- 密钥泄露检测 (truffleHog/gitleaks)
- SAST 静态分析 (pentest/security-reviewer)
- AI 驱动漏洞验证 (对标 Codex Security)
"""

import os
import sys
import json
import re
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# ============== 数据结构 ==============

class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class Verdict(Enum):
    PASS = "PASS"
    PASS_WITH_INFO = "PASS WITH INFO"
    WARN = "WARN"
    FAIL = "FAIL"

@dataclass
class Location:
    file: str
    line: int
    column: int = 0

@dataclass
class Finding:
    id: str
    type: str
    severity: str
    cvss: float
    location: Location
    description: str
    evidence: str
    remediation: Dict[str, str]
    references: List[str]
    ai_verified: bool = False
    false_positive_likelihood: float = 0.0

@dataclass
class AuditResult:
    timestamp: str
    project: str
    commit: str
    duration_seconds: float
    verdict: str
    summary: Dict[str, int]
    findings: List[Finding]

# ============== 检测规则 ==============

# OWASP Top 10 检测模式
SQL_INJECTION_PATTERNS = [
    # Python
    (r'execute\s*\(\s*f["\'].*\{.*\}.*["\']', 'f-string in SQL'),
    (r'execute\s*\([^)]*\+[^)]*\)', 'string concatenation in SQL'),
    (r'raw\s*\(\s*f["\']', 'Django raw f-string'),
    (r'\.raw\s*\([^)]*\+', 'Django raw concatenation'),
    # JavaScript
    (r'query\s*\(\s*`[^`]*\$\{', 'template literal in SQL'),
    (r'query\s*\([^)]*\+', 'concatenation in SQL'),
]

XSS_PATTERNS = [
    # Python
    (r'return\s*f["\'].*<[^>]*\{.*\}[^>]*>.*["\']', 'f-string HTML rendering'),
    (r'\.html\s*\([^)]*\+', 'string concat in HTML'),
    # JavaScript
    (r'innerHTML\s*=\s*[^"\']', 'direct innerHTML assignment'),
    (r'dangerouslySetInnerHTML', 'React dangerous HTML'),
    (r'\.html\s*\([^)]*\$\{', 'template literal in HTML'),
]

SSRF_PATTERNS = [
    (r'requests\.(get|post|put|delete)\s*\([^)]*\b(url|uri|endpoint|target)\b', 'user input in request'),
    (r'urllib\.request\.urlopen\s*\([^)]*\b(url|uri)\b', 'user input in urlopen'),
    (r'fetch\s*\([^)]*\b(url|uri|endpoint)\b', 'user input in fetch'),
    (r'axios\.(get|post)\s*\([^)]*\b(url|uri|endpoint)\b', 'user input in axios'),
]

# 密钥泄露检测模式
SECRET_PATTERNS = [
    (r'(?:api[_-]?key|apikey)\s*[:=]\s*["\'][a-zA-Z0-9_-]{20,}["\']', 'API Key'),
    (r'(?:password|passwd|pwd)\s*[:=]\s*["\'].+["\']', 'Hardcoded Password'),
    (r'(?:secret|token)\s*[:=]\s*["\'][a-zA-Z0-9_-]{20,}["\']', 'Secret/Token'),
    (r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----', 'Private Key'),
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
    (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Token'),
    (r'sk-[a-zA-Z0-9]{48}', 'OpenAI API Key'),
    (r'Bearer\s+[a-zA-Z0-9_-]{20,}', 'Bearer Token'),
]

# ============== 工具集成 ==============

def run_command(cmd: List[str], cwd: str = None) -> Tuple[int, str, str]:
    """运行外部命令"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def scan_dependencies(project_path: str) -> List[Finding]:
    """Phase 1: 依赖漏洞扫描"""
    findings = []
    
    # Python 项目
    requirements_files = list(Path(project_path).rglob("requirements*.txt"))
    if requirements_files:
        code, out, err = run_command(['pip-audit', '--format', 'json'], cwd=project_path)
        if code == 0 and out:
            try:
                deps = json.loads(out)
                for dep, vulns in deps.items():
                    for vuln in vulns:
                        findings.append(Finding(
                            id=f"DEP-{len(findings)+1:03d}",
                            type="dependency_vulnerability",
                            severity="HIGH" if vuln.get('severity') in ['HIGH', 'CRITICAL'] else "MEDIUM",
                            cvss=float(vuln.get('cvss', 5.0)),
                            location=Location(file="requirements.txt", line=0),
                            description=f"{dep}: {vuln.get('description', 'Known vulnerability')}",
                            evidence=f"{dep}=={vuln.get('version', 'unknown')}",
                            remediation={
                                'description': f"Upgrade {dep} to safe version",
                                'code': f"pip install {dep}>={vuln.get('fixed_in', 'latest')}"
                            },
                            references=[vuln.get('id', 'CVE-unknown')]
                        ))
            except json.JSONDecodeError:
                pass
    
    # Node.js 项目
    package_json = Path(project_path) / "package.json"
    if package_json.exists():
        code, out, err = run_command(['npm', 'audit', '--json'], cwd=project_path)
        if code == 0 and out:
            try:
                data = json.loads(out)
                for vuln in data.get('vulnerabilities', {}).values():
                    findings.append(Finding(
                        id=f"DEP-{len(findings)+1:03d}",
                        type="dependency_vulnerability",
                        severity=vuln.get('severity', 'MEDIUM').upper(),
                        cvss=float(vuln.get('cvss', 5.0)),
                        location=Location(file="package.json", line=0),
                        description=f"{vuln.get('name', 'Unknown')}: {vuln.get('title', 'Vulnerability')}",
                        evidence=vuln.get('vulnerable_versions', 'unknown'),
                        remediation={
                            'description': vuln.get('recommendation', 'Upgrade package'),
                            'code': f"npm install {vuln.get('name', 'package')}@latest"
                        },
                        references=[vuln.get('url', '')]
                    ))
            except json.JSONDecodeError:
                pass
    
    return findings

def scan_secrets(project_path: str) -> List[Finding]:
    """Phase 2: 密钥泄露检测"""
    findings = []
    
    # 尝试使用 truffleHog
    code, out, err = run_command(['trufflehog', 'filesystem', project_path, '--json'], cwd=project_path)
    if code == 0 and out:
        for line in out.strip().split('\n'):
            if line:
                try:
                    data = json.loads(line)
                    findings.append(Finding(
                        id=f"SECRET-{len(findings)+1:03d}",
                        type="hardcoded_secret",
                        severity="CRITICAL",
                        cvss=9.0,
                        location=Location(
                            file=data.get('Source', {}).get('file', 'unknown'),
                            line=data.get('Source', {}).get('line', 0)
                        ),
                        description=f"Hardcoded secret detected: {data.get('DetectorType', 'Secret')}",
                        evidence=data.get('Raw', '****')[:50] + '...',
                        remediation={
                            'description': 'Move secret to environment variable',
                            'code': 'os.environ.get("SECRET_NAME")'
                        },
                        references=['https://owasp.org/www-project-top-ten/A07_2021-Identification_and_Authentication_Failures/']
                    ))
                except json.JSONDecodeError:
                    continue
        return findings
    
    # 备用：正则扫描
    for root, dirs, files in os.walk(project_path):
        # 跳过无关目录
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__', 'dist', 'build']]
        
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.yaml', '.yml', '.env', '.config')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for pattern, secret_type in SECRET_PATTERNS:
                            for match in re.finditer(pattern, content, re.IGNORECASE):
                                line_num = content[:match.start()].count('\n') + 1
                                rel_path = os.path.relpath(filepath, project_path)
                                findings.append(Finding(
                                    id=f"SECRET-{len(findings)+1:03d}",
                                    type="hardcoded_secret",
                                    severity="CRITICAL",
                                    cvss=9.0,
                                    location=Location(file=rel_path, line=line_num),
                                    description=f"Potential {secret_type} detected",
                                    evidence=match.group()[:50] + '...',
                                    remediation={
                                        'description': 'Move to environment variable or secrets manager',
                                        'code': 'os.environ.get("SECRET_NAME")'
                                    },
                                    references=['https://owasp.org/www-project-top-ten/A07_2021-Identification_and_Authentication_Failures/']
                                ))
                except Exception:
                    continue
    
    return findings

def scan_owasp(project_path: str) -> List[Finding]:
    """Phase 3: OWASP Top 10 漏洞扫描"""
    findings = []
    
    # 如果是单个文件，直接扫描
    if os.path.isfile(project_path):
        files_to_scan = [(os.path.dirname(project_path), os.path.basename(project_path))]
    else:
        # 否则遍历目录
        files_to_scan = []
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__', 'dist', 'build']]
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')):
                    files_to_scan.append((root, file))
    
    for root, file in files_to_scan:
        filepath = os.path.join(root, file)
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                content = ''.join(lines)
                rel_path = os.path.relpath(filepath, os.path.dirname(project_path)) if os.path.isdir(project_path) else os.path.basename(project_path)
                
                # SQL 注入 - 简化模式，直接检测 f-string 和拼接
                for i, line in enumerate(lines, 1):
                    # f-string SQL
                    if re.search(r'execute\s*\(\s*f["\']', line, re.IGNORECASE):
                        findings.append(Finding(
                            id=f"SQL-INJ-{len(findings)+1:03d}",
                            type="sql_injection",
                            severity="CRITICAL",
                            cvss=9.8,
                            location=Location(file=rel_path, line=i),
                            description="SQL Injection: f-string in execute()",
                            evidence=line.strip()[:80],
                            remediation={
                                'description': 'Use parameterized queries',
                                'code': 'cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))'
                            },
                            references=['https://owasp.org/www-community/attacks/SQL_Injection']
                        ))
                    # 字符串拼接 SQL
                    elif re.search(r'execute\s*\([^)]*\+', line, re.IGNORECASE) and 'select' in line.lower():
                        findings.append(Finding(
                            id=f"SQL-INJ-{len(findings)+1:03d}",
                            type="sql_injection",
                            severity="CRITICAL",
                            cvss=9.8,
                            location=Location(file=rel_path, line=i),
                            description="SQL Injection: string concatenation",
                            evidence=line.strip()[:80],
                            remediation={
                                'description': 'Use parameterized queries',
                                'code': 'cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))'
                            },
                            references=['https://owasp.org/www-community/attacks/SQL_Injection']
                        ))
                
                # XSS - 检测 f-string HTML 渲染
                for i, line in enumerate(lines, 1):
                    if re.search(r'return\s*f["\'].*<[^>]*\{', line, re.IGNORECASE):
                        findings.append(Finding(
                            id=f"XSS-{len(findings)+1:03d}",
                            type="xss",
                            severity="HIGH",
                            cvss=7.5,
                            location=Location(file=rel_path, line=i),
                            description="XSS Vulnerability: f-string HTML rendering",
                            evidence=line.strip()[:80],
                            remediation={
                                'description': 'Escape user input before rendering',
                                'code': 'from markupsafe import escape; escape(user_input)'
                            },
                            references=['https://owasp.org/www-community/attacks/xss/']
                        ))
                    elif 'innerHTML' in line and '=' in line and 'escape' not in line.lower():
                        findings.append(Finding(
                            id=f"XSS-{len(findings)+1:03d}",
                            type="xss",
                            severity="HIGH",
                            cvss=7.5,
                            location=Location(file=rel_path, line=i),
                            description="XSS Vulnerability: innerHTML assignment",
                            evidence=line.strip()[:80],
                            remediation={
                                'description': 'Use textContent or escape input',
                                'code': 'element.textContent = userInput'
                            },
                            references=['https://owasp.org/www-community/attacks/xss/']
                        ))
                
                # SSRF - 检测 requests.get 等直接使用变量
                for i, line in enumerate(lines, 1):
                    if re.search(r'requests\.(get|post|put|delete)\s*\(\s*\w+\s*\)', line) and 'http' not in line:
                        findings.append(Finding(
                            id=f"SSRF-{len(findings)+1:03d}",
                            type="ssrf",
                            severity="CRITICAL",
                            cvss=9.0,
                            location=Location(file=rel_path, line=i),
                            description="SSRF Vulnerability: user input in request",
                            evidence=line.strip()[:80],
                            remediation={
                                'description': 'Validate URL before making request',
                                'code': 'def is_safe_url(url): ... # Check protocol, IP, etc.'
                            },
                            references=['https://owasp.org/www-community/attacks/Server_Side_Request_Forgery']
                        ))
                
                # 命令注入
                for i, line in enumerate(lines, 1):
                    if re.search(r'os\.system\s*\(\s*f["\']', line) or re.search(r'os\.system\s*\([^)]*\+', line):
                        findings.append(Finding(
                            id=f"CMD-INJ-{len(findings)+1:03d}",
                            type="command_injection",
                            severity="CRITICAL",
                            cvss=9.5,
                            location=Location(file=rel_path, line=i),
                            description="Command Injection: os.system with user input",
                            evidence=line.strip()[:80],
                            remediation={
                                'description': 'Use subprocess with list arguments',
                                'code': 'subprocess.run(["command", "arg1", "arg2"], check=True)'
                            },
                            references=['https://owasp.org/www-community/attacks/Command_Injection']
                        ))
                
                # 硬编码密钥
                for i, line in enumerate(lines, 1):
                    for pattern, secret_type in SECRET_PATTERNS:
                        if re.search(pattern, line, re.IGNORECASE):
                            findings.append(Finding(
                                id=f"SECRET-{len(findings)+1:03d}",
                                type="hardcoded_secret",
                                severity="CRITICAL",
                                cvss=9.0,
                                location=Location(file=rel_path, line=i),
                                description=f"Hardcoded {secret_type} detected",
                                evidence=line.strip()[:80],
                                remediation={
                                    'description': 'Move to environment variable',
                                    'code': 'os.environ.get("SECRET_NAME")'
                                },
                                references=['https://owasp.org/www-project-top-ten/A07_2021-Identification_and_Authentication_Failures/']
                            ))
                            break
                
                # 弱加密
                for i, line in enumerate(lines, 1):
                    if 'hashlib.md5' in line.lower() or 'hashlib.sha1' in line.lower():
                        findings.append(Finding(
                            id=f"WEAK-CRYPTO-{len(findings)+1:03d}",
                            type="weak_cryptography",
                            severity="HIGH",
                            cvss=7.0,
                            location=Location(file=rel_path, line=i),
                            description="Weak cryptographic algorithm (MD5/SHA1)",
                            evidence=line.strip()[:80],
                            remediation={
                                'description': 'Use bcrypt or argon2 for passwords',
                                'code': 'import bcrypt; bcrypt.hashpw(password, bcrypt.gensalt())'
                            },
                            references=['https://owasp.org/www-project-top-ten/A02_2021-Cryptographic_Failures/']
                        ))
                
                # 敏感信息入日志
                for i, line in enumerate(lines, 1):
                    if 'logger' in line.lower() and 'password' in line.lower():
                        findings.append(Finding(
                            id=f"LOG-LEAK-{len(findings)+1:03d}",
                            type="sensitive_log",
                            severity="MEDIUM",
                            cvss=5.0,
                            location=Location(file=rel_path, line=i),
                            description="Sensitive information (password) in log",
                            evidence=line.strip()[:80],
                            remediation={
                                'description': 'Remove sensitive data from logs',
                                'code': 'logger.info(f"Login: user={username}, success={success}")'
                            },
                            references=['https://owasp.org/www-project-top-ten/A09_2021-Security_Logging_and_Monitoring_Failures/']
                        ))
                                
        except Exception as e:
            continue
    
    return findings

def ai_verify_finding(finding: Finding, project_path: str) -> Finding:
    """Phase 8: AI 驱动漏洞验证（增强版）
    
    使用多层启发式规则降低误报率：
    1. 上下文防护检测
    2. 跨文件引用分析
    3. 数据流追踪
    4. 测试代码识别
    """
    try:
        filepath = os.path.join(project_path, finding.location.file)
        if not os.path.exists(filepath):
            return finding
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            line_idx = finding.location.line - 1
            
            # 1. 检查上下文防护措施 (±20 行)
            context_start = max(0, line_idx - 20)
            context_end = min(len(lines), line_idx + 10)
            context = ''.join(lines[context_start:context_end])
            
            # 防护关键词 (增强版)
            protection_keywords = [
                'escape', 'sanitize', 'validate', 'filter', 'clean', 'safe',
                'parameterize', 'prepared', 'bound', 'htmlentit', 'urlencod',
                'csrf', 'xss_protec', 'sql_injec', 'whitelist', 'allowlist'
            ]
            has_protection = any(kw in context.lower() for kw in protection_keywords)
            
            # 2. 检查函数定义和参数类型注解
            func_context = ''.join(lines[max(0, line_idx-30):line_idx+5])
            has_type_annotation = any([
                '-> str' in func_context and finding.type == 'xss',
                ': str' in func_context and 'def ' in func_context,
                'Optional[' in func_context,
                'Union[' in func_context
            ])
            
            # 3. 检查是否是测试/示例代码
            is_test = any([
                'test' in finding.location.file.lower(),
                'mock' in finding.location.file.lower(),
                'example' in finding.location.file.lower(),
                'demo' in finding.location.file.lower(),
                '__test__' in context
            ])
            
            # 4. 检查变量来源 (数据流追踪 - 简化版)
            var_name_match = re.search(r'(\w+)\s*=', ''.join(lines[max(0, line_idx-50):line_idx]))
            if var_name_match:
                var_name = var_name_match.group(1)
                # 检查变量是否来自可信源
                trusted_sources = ['config', 'settings', 'constants', 'env.get', 'os.environ']
                is_trusted_source = any(src in context.lower() for src in trusted_sources)
            else:
                is_trusted_source = False
            
            # 5. 检查是否有 try-except 错误处理
            has_error_handling = 'try:' in context and 'except' in context
            
            # 综合评分
            risk_score = 0.0
            
            if has_protection:
                risk_score -= 0.4  # 有防护措施，风险降低
            if has_type_annotation:
                risk_score -= 0.1  # 有类型注解，风险略降
            if is_test:
                risk_score -= 0.3  # 测试代码，风险降低
            if is_trusted_source:
                risk_score -= 0.2  # 可信来源，风险降低
            if has_error_handling:
                risk_score -= 0.1  # 有错误处理，风险略降
            
            # 基础风险 (无防护 +0.3)
            if not has_protection and not is_test:
                risk_score += 0.3
            
            # 规范化到 0-1
            finding.false_positive_likelihood = max(0.0, min(1.0, 0.5 + risk_score))
            finding.ai_verified = True
            
            # 添加验证详情
            finding.remediation['verification_details'] = {
                'has_protection': has_protection,
                'has_type_annotation': has_type_annotation,
                'is_test': is_test,
                'is_trusted_source': is_trusted_source,
                'has_error_handling': has_error_handling,
                'risk_score': round(risk_score, 2)
            }
                
    except Exception as e:
        # 发生错误时保持原样
        pass
    
    return finding

# ============== 报告生成 ==============

def calculate_verdict(findings: List[Finding]) -> str:
    """计算最终 verdict"""
    severity_counts = {
        'CRITICAL': 0,
        'HIGH': 0,
        'MEDIUM': 0,
        'LOW': 0,
        'INFO': 0
    }
    
    for f in findings:
        severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1
    
    if severity_counts['CRITICAL'] > 0:
        return "FAIL - CRITICAL VULNERABILITIES FOUND"
    elif severity_counts['HIGH'] > 0:
        return "FAIL - HIGH SEVERITY VULNERABILITIES FOUND"
    elif severity_counts['MEDIUM'] > 0:
        return "WARN - MEDIUM SEVERITY ISSUES FOUND"
    elif severity_counts['LOW'] > 0 or severity_counts['INFO'] > 0:
        return "PASS WITH INFO - LOW SEVERITY ISSUES FOUND"
    else:
        return "PASS - NO SECURITY ISSUES FOUND"

def generate_terminal_report(result: AuditResult) -> str:
    """生成终端报告"""
    lines = [
        "🔒 Code Security Audit Report",
        "═" * 50,
        f"Project: {result.project}",
        f"Date: {result.timestamp}",
        f"Duration: {result.duration_seconds:.1f}s",
        "",
        f"Verdict: {'❌' if 'FAIL' in result.verdict else '⚠️' if 'WARN' in result.verdict else '✅'} {result.verdict}",
        "",
        "Summary:",
        "┌─────────────┬───────┬──────────┐",
        "│ Severity    │ Count │ Status   │",
        "├─────────────┼───────┼──────────┤",
    ]
    
    severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
    severity_icons = {
        'CRITICAL': '🔴',
        'HIGH': '🟠',
        'MEDIUM': '🟡',
        'LOW': '🟢',
        'INFO': '⚪'
    }
    
    for sev in severity_order:
        count = result.summary.get(sev, 0)
        status = "FAIL" if sev in ['CRITICAL', 'HIGH'] else "WARN" if sev == 'MEDIUM' else "INFO"
        icon = severity_icons.get(sev, '')
        lines.append(f"│ {icon} {sev:10}│ {count:5} │ {status:8} │")
    
    lines.extend([
        "└─────────────┴───────┴──────────┘",
        "",
        "Top Issues:",
    ])
    
    # 显示前 5 个最严重的问题
    sorted_findings = sorted(result.findings, key=lambda f: {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'INFO': 4}.get(f.severity, 5))
    for i, f in enumerate(sorted_findings[:5], 1):
        lines.append(f"{i}. [{f.severity}] {f.type} in {f.location.file}:{f.location.line}")
        lines.append(f"   → {f.remediation.get('description', 'Review and fix')}")
        lines.append("")
    
    lines.extend([
        "Next Steps:",
        "• Run: code-security-auditor fix --all",
        "• Review: .security-audit/report.md",
        "• Compare: code-security-auditor compare --baseline",
    ])
    
    return '\n'.join(lines)

def generate_json_report(result: AuditResult) -> str:
    """生成 JSON 报告"""
    return json.dumps({
        'meta': {
            'timestamp': result.timestamp,
            'project': result.project,
            'commit': result.commit,
            'tool_version': '1.0.0'
        },
        'verdict': result.verdict,
        'summary': result.summary,
        'findings': [asdict(f) for f in result.findings]
    }, indent=2, default=str)

def generate_markdown_report(result: AuditResult) -> str:
    """生成 Markdown 报告"""
    lines = [
        "# 🔒 Code Security Audit Report",
        "",
        f"**Project:** {result.project}",
        f"**Date:** {result.timestamp}",
        f"**Duration:** {result.duration_seconds:.1f}s",
        "",
        f"## Verdict: {'❌' if 'FAIL' in result.verdict else '⚠️' if 'WARN' in result.verdict else '✅'} {result.verdict}",
        "",
        "## Summary",
        "",
        "| Severity | Count |",
        "|----------|-------|",
    ]
    
    for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
        count = result.summary.get(sev, 0)
        lines.append(f"| {sev} | {count} |")
    
    lines.extend([
        "",
        "## Findings",
        "",
    ])
    
    # 按严重程度分组
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
        sev_findings = [f for f in result.findings if f.severity == severity]
        if sev_findings:
            lines.append(f"### {severity}")
            lines.append("")
            for f in sev_findings:
                lines.extend([
                    f"#### {f.id}: {f.type}",
                    "",
                    f"- **Location:** `{f.location.file}:{f.location.line}`",
                    f"- **CVSS:** {f.cvss}",
                    f"- **Description:** {f.description}",
                    f"- **Evidence:** `{f.evidence}`",
                    f"- **Fix:** {f.remediation.get('description', 'Review and fix')}",
                    "",
                    f"```python",
                    f.remediation.get('code', '# No code suggestion'),
                    "```",
                    "",
                ])
    
    return '\n'.join(lines)

# ============== 跨文件分析 ==============

def analyze_cross_file(project_path: str, findings: List[Finding]) -> List[Finding]:
    """跨文件污点追踪分析（增强版）
    
    检测数据从源头 (source) 到汇点 (sink) 的完整路径
    """
    enhanced_findings = []
    
    # 构建项目文件索引
    file_index = {}
    function_index = {}
    
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'venv', '__pycache__']]
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, project_path)
                file_index[rel_path] = filepath
                
                # 构建函数索引
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # 提取函数定义
                        for match in re.finditer(r'def\s+(\w+)\s*\(([^)]*)\)', content):
                            func_name = match.group(1)
                            params = match.group(2)
                            if rel_path not in function_index:
                                function_index[rel_path] = []
                            function_index[rel_path].append({
                                'name': func_name,
                                'params': params,
                                'pos': match.start()
                            })
                except:
                    pass
    
    # 对每个发现进行跨文件验证
    for finding in findings:
        # 检查是否有跨文件调用
        if finding.type in ['sql_injection', 'xss', 'ssrf', 'command_injection']:
            # 查找函数调用链
            calling_files = find_calling_functions(finding, file_index, function_index)
            if calling_files:
                finding.remediation['call_chain'] = calling_files
                # 如果调用链中有防护措施，降低风险
                if has_protection_in_chain(finding, calling_files, file_index):
                    finding.false_positive_likelihood = min(0.8, finding.false_positive_likelihood + 0.2)
        
        enhanced_findings.append(finding)
    
    return enhanced_findings


def find_calling_functions(finding: Finding, file_index: Dict, function_index: Dict) -> List[Dict]:
    """查找调用链"""
    call_chain = []
    
    try:
        filepath = os.path.join(os.path.dirname(list(file_index.values())[0]) if file_index else '', finding.location.file)
        if not os.path.exists(filepath):
            return call_chain
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            line_idx = finding.location.line - 1
            
            # 向上查找函数定义
            for i in range(line_idx, -1, -1):
                if 'def ' in lines[i]:
                    match = re.search(r'def\s+(\w+)', lines[i])
                    if match:
                        call_chain.append({
                            'file': finding.location.file,
                            'function': match.group(1),
                            'line': i + 1
                        })
                    break
        
        # 查找 import 关系
        for file_path, content_path in file_index.items():
            try:
                with open(content_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if finding.location.file.split('/')[-1] in content:
                        call_chain.append({
                            'file': file_path,
                            'type': 'imports',
                            'line': '?'
                        })
            except:
                pass
    except:
        pass
    
    return call_chain[:5]  # 最多返回 5 层


def has_protection_in_chain(finding: Finding, call_chain: List[Dict], file_index: Dict) -> bool:
    """检查调用链中是否有防护措施"""
    protection_keywords = ['validate', 'sanitize', 'escape', 'filter', 'check', 'verify']
    
    for call in call_chain:
        if 'file' in call:
            try:
                filepath = os.path.join(os.path.dirname(list(file_index.values())[0]) if file_index else '', call['file'])
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if any(kw in content.lower() for kw in protection_keywords):
                            return True
            except:
                pass
    
    return False


# ============== 主函数 ==============

def audit(project_path: str, quick: bool = False, output_format: str = 'terminal') -> AuditResult:
    """执行完整安全审计"""
    start_time = datetime.now()
    
    findings = []
    
    # Phase 1: 依赖扫描
    print("📦 Phase 1: Scanning dependencies...")
    findings.extend(scan_dependencies(project_path))
    
    # Phase 2: 密钥检测
    print("🔑 Phase 2: Detecting secrets...")
    findings.extend(scan_secrets(project_path))
    
    if not quick:
        # Phase 3: OWASP Top 10
        print("🛡️  Phase 3: Scanning OWASP Top 10...")
        findings.extend(scan_owasp(project_path))
        
        # Phase 4: 跨文件分析 (新增)
        print("🔗 Phase 4: Cross-file analysis...")
        findings = analyze_cross_file(project_path, findings)
        
        # Phase 8: AI 验证 (增强版)
        print("🤖 Phase 8: AI verification (enhanced)...")
        findings = [ai_verify_finding(f, project_path) for f in findings]
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # 计算摘要
    summary = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
    for f in findings:
        summary[f.severity] = summary.get(f.severity, 0) + 1
    
    # 获取 commit hash
    code, out, err = run_command(['git', 'rev-parse', '--short', 'HEAD'], cwd=project_path)
    commit = out.strip() if code == 0 else 'unknown'
    
    result = AuditResult(
        timestamp=start_time.isoformat(),
        project=os.path.basename(os.path.abspath(project_path)),
        commit=commit,
        duration_seconds=duration,
        verdict=calculate_verdict(findings),
        summary=summary,
        findings=findings
    )
    
    return result

def main():
    parser = argparse.ArgumentParser(description='Code Security Auditor')
    parser.add_argument('command', choices=['audit', 'quick', 'scan'], help='Command to run')
    parser.add_argument('path', nargs='?', default='.', help='Project path')
    parser.add_argument('--format', choices=['terminal', 'json', 'markdown', 'sarif'], default='terminal')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--type', choices=['sql-injection', 'xss', 'ssrf', 'secrets', 'dependencies'])
    parser.add_argument('--fail-on', choices=['critical', 'high', 'medium'], default='high')
    
    args = parser.parse_args()
    
    # 执行审计
    quick = args.command == 'quick'
    result = audit(args.path, quick=quick)
    
    # 生成报告
    if args.format == 'terminal':
        report = generate_terminal_report(result)
    elif args.format == 'json':
        report = generate_json_report(result)
    elif args.format == 'markdown':
        report = generate_markdown_report(result)
    else:
        report = generate_json_report(result)
    
    # 输出
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to {args.output}")
    else:
        print(report)
    
    # 根据 --fail-on 退出码
    if 'FAIL' in result.verdict:
        sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    main()
