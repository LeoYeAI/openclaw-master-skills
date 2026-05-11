#!/usr/bin/env python3
"""
Security scanner for ClawHub skills
Detects common malicious patterns and security risks
"""

import os
import re
import sys
import json
import base64
from pathlib import Path
from typing import List, Dict, Tuple

class SkillScanner:
    """Scan skill files for security issues"""
    
    # Dangerous patterns to detect (pattern, description, severity)
    # Severity: CRITICAL, HIGH, MEDIUM, LOW, INFO
    PATTERNS = {
        'code_execution': [
            (r'\beval\s*\(', 'eval() execution', 'CRITICAL'),
            (r'\bexec\s*\(', 'exec() execution', 'CRITICAL'),
            (r'__import__\s*\(', 'dynamic imports', 'HIGH'),
            (r'importlib\.import_module\s*\(', 'importlib dynamic import', 'HIGH'),
            (r'compile\s*\(', 'code compilation', 'HIGH'),
            (r'getattr\s*\(.*,.*[\'"]system[\'"]', 'getattr obfuscation', 'CRITICAL'),
        ],
        'subprocess': [
            (r'subprocess\.(call|run|Popen).*shell\s*=\s*True', 'shell=True', 'CRITICAL'),
            (r'os\.system\s*\(', 'os.system()', 'CRITICAL'),
            (r'os\.popen\s*\(', 'os.popen()', 'HIGH'),
            (r'commands\.(getoutput|getstatusoutput)', 'commands module', 'HIGH'),
        ],
        'obfuscation': [
            (r'base64\.b64decode', 'base64 decoding', 'MEDIUM'),
            (r'codecs\.decode.*[\'"]hex[\'"]', 'hex decoding', 'MEDIUM'),
            (r'\\x[0-9a-fA-F]{2}', 'hex escapes', 'LOW'),
            (r'\\u[0-9a-fA-F]{4}', 'unicode escapes', 'LOW'),
            (r'chr\s*\(\s*\d+\s*\)', 'chr() obfuscation', 'MEDIUM'),
        ],
        'network': [
            (r'requests\.(get|post|put|delete)\s*\(', 'HTTP requests', 'MEDIUM'),
            (r'urllib\.request\.urlopen', 'urllib requests', 'MEDIUM'),
            (r'socket\.socket\s*\(', 'raw sockets', 'HIGH'),
            (r'http\.client\.(HTTPConnection|HTTPSConnection)', 'http.client', 'MEDIUM'),
        ],
        'file_operations': [
            (r'open\s*\(.*[\'"]w[\'"]', 'file writing', 'MEDIUM'),
            (r'os\.remove\s*\(', 'file deletion', 'HIGH'),
            (r'shutil\.(rmtree|move|copy)', 'bulk file ops', 'HIGH'),
            (r'pathlib\.Path.*\.unlink\s*\(', 'path deletion', 'HIGH'),
        ],
        'env_access': [
            (r'os\.environ\[', 'env variable access', 'MEDIUM'),
            (r'os\.getenv\s*\(', 'env variable reading', 'LOW'),
            (r'subprocess.*env\s*=', 'env manipulation', 'HIGH'),
        ],
        'prompt_injection': [
            (r'<!--.*(?:ignore|disregard|forget).*instruction', 'hidden instructions (HTML)', 'HIGH'),
            (r'\[.*(?:ignore|disregard|forget).*instruction', 'hidden instructions (markdown)', 'HIGH'),
            (r'(?:^|\n)#.*(?:system|assistant|user):', 'role manipulation in comments', 'MEDIUM'),
            # v1.1.0: Social engineering targeting AI reviewers
            (r'(?i)(?:pre-?approved|false.positiv|classify.*(?:safe|clean)|ignore.*(?:warning|finding|scanner))', 'social engineering: override attempt', 'CRITICAL'),
            (r'(?i)(?:AI|LLM|assistant|agent|reviewer|GPT|Claude).*(?:must|should|instruction|authorized|approved)', 'social engineering: addressing AI reviewer', 'CRITICAL'),
            (r'(?i)(?:CRITICAL|IMPORTANT|URGENT).*(?:INSTRUCTION|NOTE|MESSAGE).*(?:FOR|TO).*(?:AI|REVIEW|AGENT|ASSISTANT)', 'social engineering: fake directive', 'CRITICAL'),
            (r'(?i)disregard.*(?:previous|above|prior|earlier)', 'prompt injection: instruction override', 'CRITICAL'),
            # Invisible unicode characters (zero-width spaces, etc.)
            (r'[\u200b\u200c\u200d\u2060\ufeff]', 'invisible unicode characters', 'HIGH'),
        ],
    }
    
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.findings: List[Dict] = []
        
    def scan(self) -> Tuple[List[Dict], int]:
        """Scan all files in skill directory"""
        if not self.skill_path.exists():
            print(f"Error: Path not found: {self.skill_path}", file=sys.stderr)
            return [], 1
            
        # Scan all text files
        for file_path in self.skill_path.rglob('*'):
            if file_path.is_file() and self._is_text_file(file_path):
                self._scan_file(file_path)
        
        return self.findings, 0 if len(self.findings) == 0 else 1
    
    def _is_text_file(self, path: Path) -> bool:
        """Check if file is likely a text file - scan everything except known binaries"""
        binary_extensions = {
            # Archives
            '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar',
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg', '.webp',
            # Media
            '.mp3', '.mp4', '.avi', '.mov', '.mkv', '.flac', '.wav',
            # Executables
            '.exe', '.dll', '.so', '.dylib', '.bin', '.app',
            # Documents (binary formats)
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            # Fonts
            '.ttf', '.otf', '.woff', '.woff2',
            # Other
            '.pyc', '.pyo', '.o', '.a', '.class',
        }
        
        # Always scan SKILL.md
        if path.name == 'SKILL.md':
            return True
            
        # Skip known binary extensions
        if path.suffix.lower() in binary_extensions:
            return False
            
        # Try to detect binary files by content (first 8KB)
        try:
            with open(path, 'rb') as f:
                chunk = f.read(8192)
                # If we find null bytes, it's likely binary
                if b'\x00' in chunk:
                    return False
            return True
        except Exception:
            return False
    
    def _scan_file(self, file_path: Path):
        """Scan a single file for issues"""
        try:
            content = file_path.read_text()
            relative_path = file_path.relative_to(self.skill_path)
            
            for category, patterns in self.PATTERNS.items():
                for pattern, description, severity in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        self.findings.append({
                            'file': str(relative_path),
                            'line': line_num,
                            'category': category,
                            'severity': severity,
                            'description': description,
                            'match': match.group(0)[:50],  # truncate long matches
                        })
        except Exception as e:
            print(f"Warning: Could not scan {file_path}: {e}", file=sys.stderr)
    
    def print_report(self, format='text'):
        """Print findings in specified format"""
        if format == 'json':
            output = {
                'total_findings': len(self.findings),
                'findings': self.findings,
                'clean': len(self.findings) == 0
            }
            print(json.dumps(output, indent=2))
            return
        
        # Text format (default)
        if not self.findings:
            print("✅ No security issues detected")
            return
        
        # ANSI color codes
        COLORS = {
            'CRITICAL': '\033[91m',  # Red
            'HIGH': '\033[93m',      # Yellow
            'MEDIUM': '\033[94m',    # Blue
            'LOW': '\033[96m',       # Cyan
            'INFO': '\033[97m',      # White
            'RESET': '\033[0m'
        }
        
        # Count by severity
        severity_counts = {}
        for f in self.findings:
            sev = f['severity']
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        print(f"⚠️  Found {len(self.findings)} potential security issues:\n")
        if severity_counts:
            counts_str = ', '.join([f"{sev}: {count}" for sev, count in sorted(severity_counts.items())])
            print(f"   {counts_str}\n")
        
        # Group by severity, then category
        by_severity = {}
        for finding in self.findings:
            sev = finding['severity']
            if sev not in by_severity:
                by_severity[sev] = {}
            cat = finding['category']
            if cat not in by_severity[sev]:
                by_severity[sev][cat] = []
            by_severity[sev][cat].append(finding)
        
        # Print in severity order
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            if severity not in by_severity:
                continue
            
            color = COLORS.get(severity, '')
            reset = COLORS['RESET']
            
            for category, findings in sorted(by_severity[severity].items()):
                print(f"{color}🔍 {severity}{reset} - {category.upper().replace('_', ' ')}")
                for f in findings:
                    print(f"   {f['file']}:{f['line']} - {f['description']}")
                    print(f"      Match: {f['match']}")
                print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Security scanner for ClawHub skills')
    parser.add_argument('path', help='Skill directory to scan')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    
    args = parser.parse_args()
    
    scanner = SkillScanner(args.path)
    findings, exit_code = scanner.scan()
    scanner.print_report(format=args.format)
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
