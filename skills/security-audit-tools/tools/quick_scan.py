#!/usr/bin/env python3
"""
Quick Security Scanner - 5分钟扫描所有代码
仅检测明显恶意模式，非深度审查
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

class QuickSecurityScanner:
    def __init__(self, target_dir):
        self.target_dir = Path(target_dir)
        self.findings = defaultdict(list)
        self.stats = {
            'files_scanned': 0,
            'lines_scanned': 0,
            'total_findings': 0
        }
    
    def scan_all(self):
        """扫描所有文件"""
        for ext in ['*.ts', '*.js', '*.tsx', '*.jsx']:
            for file in self.target_dir.rglob(ext):
                if 'node_modules' in str(file) or '__tests__' in str(file):
                    continue
                self.scan_file(file)
        
        return self.generate_report()
    
    def scan_file(self, file_path):
        """扫描单个文件"""
        self.stats['files_scanned'] += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                self.stats['lines_scanned'] += len(lines)
                
                for line_num, line in enumerate(lines, 1):
                    self.check_patterns(file_path, line_num, line)
        except Exception as e:
            self.findings['errors'].append(f"{file_path}: {str(e)}")
    
    def check_patterns(self, file_path, line_num, line):
        """检查恶意模式"""
        
        # 1. 动态代码执行
        if re.search(r'\beval\s*\(|new\s+Function\s*\(', line):
            self.add_finding('CRITICAL', 'Dynamic Code Execution', file_path, line_num, line.strip())
        
        # 2. 进程创建
        if re.search(r'child_process|\.exec\s*\(|\.spawn\s*\(|execSync|spawnSync', line):
            self.add_finding('HIGH', 'Process Creation', file_path, line_num, line.strip())
        
        # 3. 文件系统操作
        if re.search(r'fs\.read|fs\.write|readFile|writeFile|unlink|rmdir', line):
            self.add_finding('MEDIUM', 'File Operation', file_path, line_num, line.strip())
        
        # 4. 网络请求（可疑域名）
        if re.search(r'https?://', line):
            if not re.search(r'polymarket|github|example|localhost|127\.0\.0\.1|polygon-rpc|etherscan|goldsky', line):
                self.add_finding('HIGH', 'Suspicious Network Request', file_path, line_num, line.strip())
        
        # 5. 硬编码私钥
        if re.search(r'private[_-]?key\s*[=:]\s*["\']0x[a-f0-9]{64}["\']', line, re.I):
            self.add_finding('CRITICAL', 'Hardcoded Private Key', file_path, line_num, line.strip())
        
        # 6. 硬编码密钥
        if re.search(r'(api[_-]?key|secret|token)\s*[=:]\s*["\'][a-zA-Z0-9]{20,}["\']', line, re.I):
            if 'process.env' not in line:
                self.add_finding('HIGH', 'Hardcoded Secret', file_path, line_num, line.strip())
        
        # 7. 混淆代码
        if re.search(r'\\x[0-9a-f]{2}{10,}|atob\(|btoa\(|Buffer.*from.*base64', line):
            self.add_finding('MEDIUM', 'Obfuscation Detected', file_path, line_num, line.strip())
        
        # 8. 数据外泄模式
        if re.search(r'(fetch|axios|http\.get|http\.post).*\+.*private', line, re.I):
            self.add_finding('CRITICAL', 'Potential Data Exfiltration', file_path, line_num, line.strip())
        
        # 9. 命令注入
        if re.search(r'\$\s*\{.*\}.*exec|`.*`.*exec', line):
            self.add_finding('CRITICAL', 'Command Injection', file_path, line_num, line.strip())
        
        # 10. 危险的npm包
        if re.search(r'require\s*\(\s*["\'](?:shelljs|node-pty|sudo)', line):
            self.add_finding('HIGH', 'Dangerous Package', file_path, line_num, line.strip())
    
    def add_finding(self, severity, category, file_path, line_num, line):
        """添加发现"""
        self.findings[severity].append({
            'category': category,
            'file': str(file_path.relative_to(self.target_dir)),
            'line': line_num,
            'code': line[:100]  # 截断
        })
        self.stats['total_findings'] += 1
    
    def generate_report(self):
        """生成报告"""
        report = {
            'stats': self.stats,
            'findings': dict(self.findings),
            'risk_score': self.calculate_risk_score()
        }
        return report
    
    def calculate_risk_score(self):
        """计算风险分数（0-100）"""
        score = 0
        score += len(self.findings.get('CRITICAL', [])) * 30
        score += len(self.findings.get('HIGH', [])) * 15
        score += len(self.findings.get('MEDIUM', [])) * 5
        score += len(self.findings.get('LOW', [])) * 1
        return min(100, score)

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python quick_security_scan.py <target_directory>")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    print(f"=== Quick Security Scan ===")
    print(f"Target: {target_dir}")
    print(f"Scanning all code...\n")
    
    scanner = QuickSecurityScanner(target_dir)
    report = scanner.scan_all()
    
    # 打印统计
    print(f"Files scanned: {report['stats']['files_scanned']}")
    print(f"Lines scanned: {report['stats']['lines_scanned']:,}")
    print(f"Total findings: {report['stats']['total_findings']}")
    print(f"Risk score: {report['risk_score']}/100\n")
    
    # 打印发现
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        if severity in report['findings'] and report['findings'][severity]:
            print(f"\n{severity}:")
            for finding in report['findings'][severity][:10]:  # 只显示前10个
                print(f"  [{finding['category']}] {finding['file']}:{finding['line']}")
                print(f"    {finding['code']}")
    
    # 保存完整报告
    with open('/tmp/security_scan_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nFull report saved to: /tmp/security_scan_report.json")
    
    # 返回风险等级
    if report['risk_score'] >= 70:
        print("\n❌ HIGH RISK - Do not install")
        sys.exit(1)
    elif report['risk_score'] >= 40:
        print("\n⚠️  MEDIUM RISK - Manual review required")
        sys.exit(0)
    else:
        print("\n✅ LOW RISK - Safe to install")
        sys.exit(0)

if __name__ == '__main__':
    main()
