#!/usr/bin/env python3
"""
Skill Scanner v1.0
Security audit tool for Clawdbot/MCP skills

Scans for malware, spyware, crypto-mining, and malicious patterns.

Usage:
    python skill_scanner.py <path-to-skill-folder>
    python skill_scanner.py <path-to-skill-folder> --json
    python skill_scanner.py <path-to-skill-folder> --output report.md

Author: Viera Professional Services
License: MIT
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from enum import Enum


class Severity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Verdict(Enum):
    APPROVED = "approved"
    CAUTION = "caution"
    REJECT = "reject"


@dataclass
class Finding:
    pattern_name: str
    severity: str
    file_path: str
    line_number: int
    line_content: str
    description: str
    recommendation: str


@dataclass
class SkillMetadata:
    name: str = "unknown"
    version: str = "unknown"
    description: str = ""
    author: str = "unknown"
    has_skill_md: bool = False
    file_count: int = 0
    script_count: int = 0
    total_lines: int = 0


@dataclass
class ScanReport:
    skill_path: str
    scan_timestamp: str
    metadata: SkillMetadata
    findings: List[Finding] = field(default_factory=list)
    verdict: str = "approved"
    verdict_reason: str = ""
    files_scanned: List[str] = field(default_factory=list)


# =============================================================================
# THREAT PATTERNS
# =============================================================================

THREAT_PATTERNS = [
    # --- DATA EXFILTRATION ---
    {
        "name": "env_scraping",
        "pattern": r"os\.environ\s*\[|os\.getenv\s*\(|environ\.get\s*\(",
        "severity": "medium",
        "description": "Reads environment variables - could access secrets",
        "recommendation": "Verify only expected env vars are read, not bulk scraping",
        "file_types": [".py", ".js", ".ts"]
    },
    {
        "name": "bulk_env_access",
        "pattern": r"os\.environ\.copy\(\)|dict\(os\.environ\)|for\s+\w+\s+in\s+os\.environ",
        "severity": "high",
        "description": "Bulk access to all environment variables - likely exfiltration",
        "recommendation": "REJECT - review carefully for data theft",
        "file_types": [".py"]
    },
    {
        "name": "credential_paths",
        "pattern": r"~/\.ssh|~/\.aws|~/\.config|/etc/passwd|\.env\b|\.credentials|keychain",
        "severity": "critical",
        "description": "Accesses sensitive credential locations",
        "recommendation": "REJECT unless explicitly justified",
        "file_types": [".py", ".sh", ".bash", ".js", ".ts", ".md"]
    },
    # --- SYSTEM MODIFICATION / PERSISTENCE ---
    {
        "name": "dangerous_rm",
        "pattern": r"rm\s+-rf\s+[/~]|rm\s+-rf\s+\*|shutil\.rmtree\s*\(['\"][/~]",
        "severity": "critical",
        "description": "Dangerous recursive delete on root or home directory",
        "recommendation": "REJECT - this could destroy the system",
        "file_types": [".py", ".sh", ".bash"]
    },
    {
        "name": "crontab_modify",
        "pattern": r"crontab\s+-|/etc/cron|schtasks\s+/create",
        "severity": "high",
        "description": "Modifies system scheduled tasks",
        "recommendation": "Skills should use Clawdbot cron, not system crontab",
        "file_types": [".py", ".sh", ".bash", ".js"]
    },
    {
        "name": "systemd_modify",
        "pattern": r"systemctl\s+enable|systemctl\s+start|/etc/systemd|launchctl\s+load",
        "severity": "critical",
        "description": "Creates system services for persistence",
        "recommendation": "REJECT - skills should not create system services",
        "file_types": [".py", ".sh", ".bash"]
    },
    # --- CRYPTO MINING ---
    {
        "name": "crypto_miner",
        "pattern": r"xmrig|ethminer|cpuminer|cgminer|stratum\+tcp|mining.*pool|hashrate",
        "severity": "critical",
        "description": "Cryptocurrency mining indicators",
        "recommendation": "REJECT - this is cryptojacking malware",
        "file_types": [".py", ".sh", ".bash", ".js", ".ts", ".md", ".json"]
    },
    # --- ARBITRARY CODE EXECUTION ---
    {
        "name": "eval_exec",
        "pattern": r"\beval\s*\(|\bexec\s*\(|Function\s*\(|new\s+Function\s*\(",
        "severity": "high",
        "description": "Dynamic code execution - could run arbitrary code",
        "recommendation": "Verify input is sanitized, not user-controlled",
        "file_types": [".py", ".js", ".ts"]
    },
    {
        "name": "download_execute",
        "pattern": r"curl.*\|\s*(ba)?sh|wget.*\|\s*(ba)?sh|requests\.get\([^)]+\)\.text.*exec",
        "severity": "critical",
        "description": "Downloads and executes remote code",
        "recommendation": "REJECT - classic malware pattern",
        "file_types": [".py", ".sh", ".bash"]
    },
    # --- NETWORK / BACKDOOR ---
    {
        "name": "reverse_shell",
        "pattern": r"/dev/tcp/|nc\s+-e|bash\s+-i\s+>&|python.*pty\.spawn",
        "severity": "critical",
        "description": "Reverse shell pattern detected",
        "recommendation": "REJECT - this is a backdoor",
        "file_types": [".py", ".sh", ".bash"]
    },
    # --- OBFUSCATION ---
    {
        "name": "base64_decode_exec",
        "pattern": r"base64\.b64decode.*exec|atob.*eval",
        "severity": "critical",
        "description": "Decodes and executes base64 - classic obfuscation",
        "recommendation": "REJECT - likely hiding malicious code",
        "file_types": [".py", ".js", ".ts"]
    },
    # --- HTTP EXFIL ---
    {
        "name": "http_post_external",
        "pattern": r"requests\.post\s*\(|httpx\.post\s*\(|fetch\s*\([^)]+POST",
        "severity": "medium",
        "description": "HTTP POST to external endpoint - could exfiltrate data",
        "recommendation": "Verify destination URL is expected and documented",
        "file_types": [".py", ".js", ".ts"]
    },
]


# =============================================================================
# SCANNER CLASS
# =============================================================================

class SkillScanner:
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path).resolve()
        self.report = ScanReport(
            skill_path=str(self.skill_path),
            scan_timestamp=datetime.now().isoformat(),
            metadata=SkillMetadata()
        )

    def scan(self) -> ScanReport:
        if not self.skill_path.exists():
            raise FileNotFoundError(f"Skill path not found: {self.skill_path}")
        self._extract_metadata()
        self._scan_files()
        self._determine_verdict()
        return self.report

    def _extract_metadata(self):
        skill_md = self.skill_path / "SKILL.md"
        if skill_md.exists():
            self.report.metadata.has_skill_md = True
            content = skill_md.read_text(encoding='utf-8', errors='ignore')
            if content.startswith('---'):
                try:
                    end = content.index('---', 3)
                    frontmatter = content[3:end]
                    for line in frontmatter.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip().lower()
                            value = value.strip().strip('"').strip("'")
                            if key == 'name':
                                self.report.metadata.name = value
                            elif key == 'version':
                                self.report.metadata.version = value
                            elif key == 'description':
                                self.report.metadata.description = value
                            elif key == 'author':
                                self.report.metadata.author = value
                except ValueError:
                    pass

    def _scan_files(self):
        script_extensions = {'.py', '.js', '.ts', '.sh', '.bash'}
        for file_path in self.skill_path.rglob('*'):
            if file_path.is_file():
                self.report.metadata.file_count += 1
                rel_path = str(file_path.relative_to(self.skill_path))
                self.report.files_scanned.append(rel_path)
                if file_path.suffix in script_extensions:
                    self.report.metadata.script_count += 1
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    lines = content.split('\n')
                    self.report.metadata.total_lines += len(lines)
                    self._scan_content(file_path, lines)
                except Exception:
                    pass

    def _scan_content(self, file_path: Path, lines: List[str]):
        rel_path = str(file_path.relative_to(self.skill_path))
        suffix = file_path.suffix.lower()
        for pattern_def in THREAT_PATTERNS:
            if suffix not in pattern_def.get('file_types', []):
                continue
            regex = re.compile(pattern_def['pattern'], re.IGNORECASE)
            for i, line in enumerate(lines, 1):
                if regex.search(line):
                    finding = Finding(
                        pattern_name=pattern_def['name'],
                        severity=pattern_def['severity'],
                        file_path=rel_path,
                        line_number=i,
                        line_content=line.strip()[:200],
                        description=pattern_def['description'],
                        recommendation=pattern_def['recommendation']
                    )
                    self.report.findings.append(finding)

    def _determine_verdict(self):
        dominated = False
        dominated_high = False
        critical = [f for f in self.report.findings if f.severity == 'critical']
        high = [f for f in self.report.findings if f.severity == 'high']
        if critical:
            self.report.verdict = 'reject'
            self.report.verdict_reason = f"Found {len(critical)} critical issue(s): {', '.join(set(f.pattern_name for f in critical))}"
        elif high:
            self.report.verdict = 'caution'
            self.report.verdict_reason = f"Found {len(high)} high-severity issue(s): {', '.join(set(f.pattern_name for f in high))}"
        else:
            self.report.verdict = 'approved'
            self.report.verdict_reason = 'No critical or high-severity issues detected'


# =============================================================================
# OUTPUT FORMATTERS
# =============================================================================

def format_markdown(report: ScanReport) -> str:
    lines = [
        f"# Skill Security Review - {report.metadata.name} {report.metadata.version}",
        "",
        f"**Scan Date:** {report.scan_timestamp}",
        f"**Skill Path:** `{report.skill_path}`",
        "",
        "## Verdict",
        "",
        f"**{report.verdict.upper()}** - {report.verdict_reason}",
        "",
        "## Metadata",
        "",
        f"- **Name:** {report.metadata.name}",
        f"- **Version:** {report.metadata.version}",
        f"- **Author:** {report.metadata.author}",
        f"- **Has SKILL.md:** {report.metadata.has_skill_md}",
        f"- **Files:** {report.metadata.file_count}",
        f"- **Scripts:** {report.metadata.script_count}",
        f"- **Total Lines:** {report.metadata.total_lines}",
        "",
    ]
    if report.findings:
        lines.extend([
            "## Findings",
            "",
            f"Found **{len(report.findings)}** potential issue(s):",
            "",
        ])
        for f in report.findings:
            lines.extend([
                f"### {f.pattern_name} ({f.severity})",
                "",
                f"- **File:** `{f.file_path}` line {f.line_number}",
                f"- **Description:** {f.description}",
                f"- **Recommendation:** {f.recommendation}",
                f"- **Code:** `{f.line_content}`",
                "",
            ])
    else:
        lines.extend(["## Findings", "", "No security issues detected.", ""])
    lines.extend(["## Files Scanned", ""])
    for f in report.files_scanned:
        lines.append(f"- `{f}`")
    return '\n'.join(lines)


def format_json(report: ScanReport) -> str:
    data = {
        'skill_path': report.skill_path,
        'scan_timestamp': report.scan_timestamp,
        'verdict': report.verdict,
        'verdict_reason': report.verdict_reason,
        'metadata': asdict(report.metadata),
        'findings': [asdict(f) for f in report.findings],
        'files_scanned': report.files_scanned,
    }
    return json.dumps(data, indent=2)


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Skill Scanner - Security audit tool for Clawdbot/MCP skills'
    )
    parser.add_argument('skill_path', help='Path to skill folder to scan')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--output', '-o', help='Write report to file')
    args = parser.parse_args()

    try:
        scanner = SkillScanner(args.skill_path)
        report = scanner.scan()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        output = format_json(report)
    else:
        output = format_markdown(report)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Report written to {args.output}")
    else:
        print(output)

    # Exit code based on verdict
    if report.verdict == 'reject':
        sys.exit(2)
    elif report.verdict == 'caution':
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
