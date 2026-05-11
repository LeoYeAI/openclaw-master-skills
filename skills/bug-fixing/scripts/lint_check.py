#!/usr/bin/env python3
"""
Lint Check Script - Detect and categorize code warnings/errors after modification.

Features:
- Supports Python (ruff/pylint/mypy), TypeScript/JavaScript (eslint/tsc)
- Smart priority classification with rule-based and pattern-based detection
- Parallel processing for multiple files
- JSON output for CI/CD integration
- Auto-fix support for compatible linters
- Dependency checking with install suggestions

Usage:
    python lint_check.py <file_path>                    # Check single file
    python lint_check.py <file1> <file2>                # Check multiple files (parallel)
    python lint_check.py --dir <directory>              # Check directory
    python lint_check.py <file_path> --fix              # Auto-fix if possible
    python lint_check.py --check-deps                   # Check linter dependencies
    python lint_check.py <file_path> --json             # JSON output for CI/CD

Exit codes:
    0 - No errors found (may have warnings)
    1 - P0/P1 errors found (must fix)
    2 - P2 warnings found (should fix)
    3 - Linter not available
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import os
import re
import json
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


# Configure stdout/stderr encoding for Windows
def _configure_stdio() -> None:
    """Ensure UTF-8 encoding for stdout/stderr on Windows"""
    if sys.platform == 'win32':
        os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

_configure_stdio()


class Priority(Enum):
    """Error priority levels"""
    P0 = 0  # Must fix immediately (syntax, critical type errors)
    P1 = 1  # Must fix before commit (imports, declarations)
    P2 = 2  # Should fix (linting warnings)
    P3 = 3  # Optional (style nits)
    
    def __str__(self) -> str:
        return self.name


@dataclass
class DependencyStatus:
    """Status of a linter dependency"""
    name: str
    available: bool
    version: Optional[str] = None
    install_cmd: Optional[str] = None


@dataclass
class LintIssue:
    """Single lint issue"""
    file_path: str
    line: int
    column: int
    message: str
    rule_id: str
    priority: Priority
    category: str
    suggestion: Optional[str] = None
    fixable: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d['priority'] = str(self.priority)
        return d


@dataclass
class LintResult:
    """Lint result for a file"""
    file_path: str
    success: bool
    issues: List[LintIssue] = field(default_factory=list)
    linter_used: Optional[str] = None
    error_message: Optional[str] = None
    
    @property
    def p0_count(self) -> int:
        return sum(1 for i in self.issues if i.priority == Priority.P0)
    
    @property
    def p1_count(self) -> int:
        return sum(1 for i in self.issues if i.priority == Priority.P1)
    
    @property
    def p2_count(self) -> int:
        return sum(1 for i in self.issues if i.priority == Priority.P2)
    
    @property
    def p3_count(self) -> int:
        return sum(1 for i in self.issues if i.priority == Priority.P3)
    
    @property
    def has_blocking_issues(self) -> bool:
        return self.p0_count > 0 or self.p1_count > 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'file_path': self.file_path,
            'success': self.success,
            'issues': [i.to_dict() for i in self.issues],
            'linter_used': self.linter_used,
            'error_message': self.error_message,
            'counts': {
                'p0': self.p0_count,
                'p1': self.p1_count,
                'p2': self.p2_count,
                'p3': self.p3_count,
                'total': len(self.issues)
            }
        }


class PriorityClassifier:
    """Smart priority classification for lint issues"""
    
    # Rule ID prefixes that indicate specific priorities
    RULE_PRIORITY_MAP = {
        # Python - Ruff
        Priority.P0: {
            'E999',  # Syntax error
            'E902',  # IO error
            'F401',  # Imported but unused (can cause issues)
            'F821',  # Undefined name
            'F822',  # Undefined name in __all__
            'F823',  # Local variable referenced before assignment
        },
        Priority.P1: {
            'E',     # Error prefix
            'F',     # Pyflakes
            'PLE',   # Pylint errors
            'I001',  # Import sorting
        },
        Priority.P2: {
            'W',     # Warning prefix
            'PLW',   # Pylint warnings
            'C',     # Convention
            'N',     # Naming
            'D',     # Docstring
        },
        # TypeScript/ESLint
        'error': Priority.P1,
        'warn': Priority.P2,
        'warning': Priority.P2,
    }
    
    # Pattern-based classification (regex patterns)
    PATTERN_PRIORITY = {
        Priority.P0: [
            r'syntax\s*error', r'invalid\s*syntax', r'unexpected\s*token',
            r'cannot\s*parse', r'parse\s*error', r'SyntaxError',
            r'unterminated', r'unexpected\s*end', r'unexpected\s*EOF',
            r'missing.*semicolon', r'missing.*bracket', r'missing.*brace',
            r'illegal', r'invalid\s*character',
        ],
        Priority.P1: [
            r'undefined', r'not\s*defined', r'cannot\s*find', r'no\s*such',
            r'import.*error', r'module.*not\s*found', r'cannot\s*resolve',
            r'type.*mismatch', r'incompatible\s*type', r'not\s*assignable',
            r'missing.*import', r'unresolved.*reference', r'does\s*not\s*exist',
            r'has\s*no\s*attribute', r'has\s*no\s*member', r'is\s*not\s*a\s*function',
            r'expected.*argument', r'too\s*(many|few)\s*arguments',
            r'cannot\s*call', r'not\s*callable', r'return\s*type.*mismatch',
        ],
        Priority.P2: [
            r'unused', r'never\s*used', r'is\s*defined\s*but\s*never',
            r'deprecated', r'complexity', r'too\s*many', r'too\s*long',
            r'line\s*too\s*long', r'missing\s*docstring', r'missing\s*type',
            r'could\s*be', r'consider', r'prefer', r'should\s*be',
            r'shadowing', r'redefinition', r'reassigned',
        ],
    }
    
    # Fix suggestions based on patterns
    SUGGESTIONS = {
        r'undefined|not\s*defined': "Add import statement or define the variable/function",
        r'unused|never\s*used': "Remove unused code or add usage",
        r'import': "Check import path and module name",
        r'type.*mismatch|not\s*assignable': "Check type annotations and ensure compatibility",
        r'missing': "Add required syntax element or import",
        r'deprecated': "Update to use recommended API",
        r'cannot\s*find\s*module': "Install package or check import path",
        r'no\s*attribute|no\s*member': "Check spelling or add required method/property",
        r'argument': "Check function signature and argument count",
    }
    
    def __init__(self):
        # Compile patterns for efficiency
        self._compiled_patterns = {
            priority: [re.compile(p, re.IGNORECASE) for p in patterns]
            for priority, patterns in self.PATTERN_PRIORITY.items()
        }
        self._suggestion_patterns = [
            (re.compile(p, re.IGNORECASE), suggestion)
            for p, suggestion in self.SUGGESTIONS.items()
        ]
    
    def classify(self, message: str, rule_id: str, severity: Optional[str] = None) -> Priority:
        """Classify issue priority based on rule ID, message, and severity"""
        rule_upper = rule_id.upper()
        
        # 1. Check exact rule ID match
        for priority, rules in self.RULE_PRIORITY_MAP.items():
            if isinstance(rules, set) and rule_upper in rules:
                return priority
        
        # 2. Check rule ID prefix
        for priority, rules in self.RULE_PRIORITY_MAP.items():
            if isinstance(rules, set):
                for rule_prefix in rules:
                    if len(rule_prefix) <= 3 and rule_upper.startswith(rule_prefix):
                        return priority
        
        # 3. Check severity string
        if severity:
            severity_lower = severity.lower()
            if 'error' in severity_lower:
                return Priority.P1
            elif 'warn' in severity_lower:
                return Priority.P2
        
        # 4. Check message patterns
        for priority, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(message):
                    return priority
        
        # 5. Default based on rule prefix conventions
        if rule_upper.startswith('E') or rule_id.startswith('TS'):
            return Priority.P1
        elif rule_upper.startswith('W'):
            return Priority.P2
        
        return Priority.P3
    
    def get_suggestion(self, message: str) -> Optional[str]:
        """Get fix suggestion based on message"""
        for pattern, suggestion in self._suggestion_patterns:
            if pattern.search(message):
                return suggestion
        return None


class LintChecker:
    """Multi-language lint checker with parallel processing"""
    
    EXTENSION_MAP = {
        '.py': 'python', '.pyw': 'python', '.pyi': 'python',
        '.ts': 'typescript', '.tsx': 'typescript',
        '.js': 'javascript', '.jsx': 'javascript',
        '.mjs': 'javascript', '.cjs': 'javascript',
        '.vue': 'vue', '.go': 'go', '.rs': 'rust',
    }
    
    INSTALL_COMMANDS = {
        'ruff': 'pip install ruff',
        'pylint': 'pip install pylint',
        'mypy': 'pip install mypy',
        'eslint': 'npm install -g eslint',
        'tsc': 'npm install -g typescript',
    }
    
    def __init__(self, verbose: bool = False, max_workers: int = 4):
        self.verbose = verbose
        self.max_workers = max_workers
        self.classifier = PriorityClassifier()
        self._linter_cache: Dict[str, bool] = {}
        self._cache_lock = threading.Lock()
    
    def _log(self, message: str) -> None:
        if self.verbose:
            print(f"[LINT] {message}", file=sys.stderr)
    
    def _check_command(self, cmd: str) -> bool:
        """Check if a command is available (thread-safe)"""
        with self._cache_lock:
            if cmd in self._linter_cache:
                return self._linter_cache[cmd]
        
        try:
            check_cmd = 'where' if sys.platform == 'win32' else 'which'
            result = subprocess.run([check_cmd, cmd], capture_output=True, text=True, timeout=5)
            available = result.returncode == 0
        except Exception:
            available = False
        
        with self._cache_lock:
            self._linter_cache[cmd] = available
        return available
    
    def _get_version(self, cmd: str) -> Optional[str]:
        """Get version of a command"""
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except Exception:
            pass
        return None
    
    def check_dependencies(self) -> List[DependencyStatus]:
        """Check all linter dependencies"""
        deps = []
        for name in ['ruff', 'pylint', 'mypy', 'eslint', 'tsc']:
            # For eslint/tsc, also check npx
            if name in ('eslint', 'tsc'):
                available = self._check_command(name) or self._check_command('npx')
            else:
                available = self._check_command(name)
            
            deps.append(DependencyStatus(
                name=name,
                available=available,
                version=self._get_version(name) if available else None,
                install_cmd=self.INSTALL_COMMANDS.get(name)
            ))
        return deps
    
    def _parse_ruff_output(self, output: str, file_path: str) -> List[LintIssue]:
        """Parse ruff linter output"""
        issues = []
        # Ruff format: file:line:col: CODE message
        pattern = r'^(.+?):(\d+):(\d+):\s*(\w+)\s+(.+)$'
        
        for line in output.strip().split('\n'):
            if not line.strip():
                continue
            match = re.match(pattern, line)
            if match:
                _, line_num, col, rule_id, message = match.groups()
                priority = self.classifier.classify(message, rule_id)
                issues.append(LintIssue(
                    file_path=file_path,
                    line=int(line_num),
                    column=int(col),
                    message=message.strip(),
                    rule_id=rule_id,
                    priority=priority,
                    category='ruff',
                    suggestion=self.classifier.get_suggestion(message),
                    fixable=rule_id not in ('E999', 'E902')
                ))
        return issues
    
    def _parse_mypy_output(self, output: str, file_path: str) -> List[LintIssue]:
        """Parse mypy type checker output"""
        issues = []
        # mypy format: file:line: error: message  [error-code]
        pattern = r'^(.+?):(\d+):\s*(error|warning|note):\s*(.+?)(?:\s*\[([^\]]+)\])?$'
        
        for line in output.strip().split('\n'):
            if not line.strip():
                continue
            match = re.match(pattern, line)
            if match:
                _, line_num, severity, message, error_code = match.groups()
                rule_id = error_code or f'mypy-{severity}'
                priority = self.classifier.classify(message, rule_id, severity)
                
                # Mypy errors are typically P1
                if severity == 'error' and priority == Priority.P3:
                    priority = Priority.P1
                
                issues.append(LintIssue(
                    file_path=file_path,
                    line=int(line_num),
                    column=0,
                    message=message.strip(),
                    rule_id=rule_id,
                    priority=priority,
                    category='mypy',
                    suggestion=self.classifier.get_suggestion(message),
                    fixable=False
                ))
        return issues
    
    def _parse_eslint_output(self, output: str, file_path: str) -> List[LintIssue]:
        """Parse ESLint JSON output"""
        issues = []
        try:
            data = json.loads(output)
            for file_result in data:
                for msg in file_result.get('messages', []):
                    rule_id = msg.get('ruleId') or 'eslint'
                    message = msg.get('message', '')
                    severity = 'error' if msg.get('severity', 1) == 2 else 'warning'
                    priority = self.classifier.classify(message, rule_id, severity)
                    
                    issues.append(LintIssue(
                        file_path=file_path,
                        line=msg.get('line', 0),
                        column=msg.get('column', 0),
                        message=message.strip(),
                        rule_id=rule_id,
                        priority=priority,
                        category='eslint',
                        suggestion=self.classifier.get_suggestion(message),
                        fixable=msg.get('fix') is not None
                    ))
        except json.JSONDecodeError:
            pass
        return issues
    
    def _parse_tsc_output(self, output: str, file_path: str) -> List[LintIssue]:
        """Parse TypeScript compiler output"""
        issues = []
        # TSC format: file(line,col): error TSXXXX: message
        pattern = r'^(.+?)\((\d+),(\d+)\):\s*(error|warning)\s+(TS\d+):\s*(.+)$'
        
        for line in output.strip().split('\n'):
            match = re.match(pattern, line)
            if match:
                _, line_num, col, severity, code, message = match.groups()
                priority = self.classifier.classify(message, code, severity)
                issues.append(LintIssue(
                    file_path=file_path,
                    line=int(line_num),
                    column=int(col),
                    message=message.strip(),
                    rule_id=code,
                    priority=priority,
                    category='tsc',
                    suggestion=self.classifier.get_suggestion(message),
                    fixable=False
                ))
        return issues
    
    def _check_python(self, file_path: str, auto_fix: bool = False) -> LintResult:
        """Check Python file using ruff and optionally mypy"""
        path = Path(file_path).resolve()
        issues = []
        linters_used = []
        
        # Run ruff
        if self._check_command('ruff'):
            cmd = ['ruff', 'check']
            if auto_fix:
                cmd.append('--fix')
            cmd.append(str(path))
            
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True,
                    encoding='utf-8', errors='replace', timeout=30
                )
                ruff_issues = self._parse_ruff_output(result.stdout + result.stderr, str(path))
                issues.extend(ruff_issues)
                linters_used.append('ruff')
            except Exception as e:
                self._log(f"ruff error: {e}")
        
        # Run mypy for type checking
        if self._check_command('mypy'):
            cmd = ['mypy', '--no-error-summary', str(path)]
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True,
                    encoding='utf-8', errors='replace', timeout=60
                )
                mypy_issues = self._parse_mypy_output(result.stdout + result.stderr, str(path))
                # Deduplicate with ruff issues
                existing_locations = {(i.line, i.message[:50]) for i in issues}
                for issue in mypy_issues:
                    if (issue.line, issue.message[:50]) not in existing_locations:
                        issues.append(issue)
                linters_used.append('mypy')
            except Exception as e:
                self._log(f"mypy error: {e}")
        
        if not linters_used:
            return LintResult(
                file_path=str(path),
                success=False,
                error_message="No Python linter available. Install: pip install ruff mypy"
            )
        
        return LintResult(
            file_path=str(path),
            success=True,
            issues=issues,
            linter_used='+'.join(linters_used)
        )
    
    def _check_js_ts(self, file_path: str, auto_fix: bool = False) -> LintResult:
        """Check JavaScript/TypeScript file"""
        path = Path(file_path).resolve()
        issues = []
        linters_used = []
        
        # Run ESLint
        eslint_cmd = None
        if self._check_command('eslint'):
            eslint_cmd = ['eslint']
        elif self._check_command('npx'):
            eslint_cmd = ['npx', '--yes', 'eslint']
        
        if eslint_cmd:
            cmd = eslint_cmd + ['--format=json']
            if auto_fix:
                cmd.append('--fix')
            cmd.append(str(path))
            
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True,
                    encoding='utf-8', errors='replace', timeout=30
                )
                eslint_issues = self._parse_eslint_output(result.stdout, str(path))
                issues.extend(eslint_issues)
                linters_used.append('eslint')
            except Exception as e:
                self._log(f"eslint error: {e}")
        
        # Run TypeScript compiler for type checking
        if str(path).endswith(('.ts', '.tsx')):
            tsc_cmd = None
            if self._check_command('tsc'):
                tsc_cmd = ['tsc']
            elif self._check_command('npx'):
                tsc_cmd = ['npx', '--yes', 'tsc']
            
            if tsc_cmd:
                cmd = tsc_cmd + ['--noEmit', '--pretty', 'false', str(path)]
                try:
                    result = subprocess.run(
                        cmd, capture_output=True, text=True,
                        encoding='utf-8', errors='replace', timeout=60
                    )
                    tsc_issues = self._parse_tsc_output(result.stdout + result.stderr, str(path))
                    issues.extend(tsc_issues)
                    if 'tsc' not in linters_used:
                        linters_used.append('tsc')
                except Exception as e:
                    self._log(f"tsc error: {e}")
        
        if not linters_used:
            return LintResult(
                file_path=str(path),
                success=False,
                error_message="No JS/TS linter available. Install: npm install -g eslint typescript"
            )
        
        return LintResult(
            file_path=str(path),
            success=True,
            issues=issues,
            linter_used='+'.join(linters_used)
        )
    
    def check_file(self, file_path: str, auto_fix: bool = False) -> LintResult:
        """Check a single file for lint issues"""
        path = Path(file_path)
        
        if not path.exists():
            return LintResult(
                file_path=str(path),
                success=False,
                error_message=f"File not found: {file_path}"
            )
        
        ext = path.suffix.lower()
        language = self.EXTENSION_MAP.get(ext)
        
        if language == 'python':
            return self._check_python(str(path), auto_fix)
        elif language in ('typescript', 'javascript', 'vue'):
            return self._check_js_ts(str(path), auto_fix)
        else:
            return LintResult(
                file_path=str(path),
                success=True,
                issues=[],
                error_message=f"No linter configured for extension: {ext}"
            )
    
    def check_files(self, file_paths: List[str], auto_fix: bool = False) -> List[LintResult]:
        """Check multiple files (parallel processing)"""
        if len(file_paths) == 1:
            return [self.check_file(file_paths[0], auto_fix)]
        
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {
                executor.submit(self.check_file, path, auto_fix): path
                for path in file_paths
            }
            for future in as_completed(future_to_path):
                results.append(future.result())
        
        # Sort by original order
        path_order = {path: i for i, path in enumerate(file_paths)}
        results.sort(key=lambda r: path_order.get(r.file_path, 999))
        return results
    
    def check_directory(self, dir_path: str, auto_fix: bool = False,
                       extensions: Optional[List[str]] = None) -> List[LintResult]:
        """Check all supported files in a directory"""
        path = Path(dir_path)
        if not path.exists():
            return [LintResult(
                file_path=str(path),
                success=False,
                error_message=f"Directory not found: {dir_path}"
            )]
        
        if extensions is None:
            extensions = list(self.EXTENSION_MAP.keys())
        
        files = []
        for ext in extensions:
            files.extend(path.rglob(f'*{ext}'))
        
        exclude_patterns = [
            'node_modules', '__pycache__', '.git', 'dist', 'build',
            'venv', '.venv', 'target', '.next', '.nuxt', 'coverage'
        ]
        files = [f for f in files if not any(p in str(f) for p in exclude_patterns)]
        
        return self.check_files([str(f) for f in files], auto_fix)


def print_dependencies(deps: List[DependencyStatus]) -> None:
    """Print dependency status"""
    print("\n" + "=" * 60)
    print("🔧 LINTER DEPENDENCIES")
    print("=" * 60)
    
    for dep in deps:
        status = "✅" if dep.available else "❌"
        version = f" ({dep.version})" if dep.version else ""
        print(f"  {status} {dep.name}{version}")
        if not dep.available and dep.install_cmd:
            print(f"      Install: {dep.install_cmd}")
    
    print("=" * 60)


def print_issues(results: List[LintResult], summary_only: bool = False, 
                 json_output: bool = False) -> None:
    """Print lint issues with formatting"""
    if json_output:
        output = {
            'results': [r.to_dict() for r in results],
            'summary': {
                'total_files': len(results),
                'p0': sum(r.p0_count for r in results),
                'p1': sum(r.p1_count for r in results),
                'p2': sum(r.p2_count for r in results),
                'p3': sum(r.p3_count for r in results),
                'blocking': any(r.has_blocking_issues for r in results)
            }
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return
    
    print("\n" + "=" * 70)
    print("🔍 LINT CHECK RESULTS")
    print("=" * 70)
    
    total_p0 = sum(r.p0_count for r in results)
    total_p1 = sum(r.p1_count for r in results)
    total_p2 = sum(r.p2_count for r in results)
    total_p3 = sum(r.p3_count for r in results)
    
    if not summary_only:
        for result in results:
            if result.error_message and not result.success:
                print(f"\n❌ {result.file_path}")
                print(f"   Error: {result.error_message}")
                continue
            
            if not result.issues:
                print(f"\n✅ {result.file_path} - No issues [{result.linter_used}]")
                continue
            
            print(f"\n📄 {result.file_path} [{result.linter_used}]")
            
            priority_emoji = {
                Priority.P0: "🔴 P0 (CRITICAL)",
                Priority.P1: "🟠 P1 (ERROR)",
                Priority.P2: "🟡 P2 (WARNING)",
                Priority.P3: "⚪ P3 (INFO)"
            }
            
            for priority in Priority:
                priority_issues = [i for i in result.issues if i.priority == priority]
                if not priority_issues:
                    continue
                
                print(f"\n   {priority_emoji[priority]}:")
                for issue in priority_issues[:10]:  # Limit to 10 per priority
                    fix_indicator = "🔧" if issue.fixable else ""
                    print(f"      L{issue.line}:{issue.column} [{issue.rule_id}] {issue.message} {fix_indicator}")
                    if issue.suggestion:
                        print(f"         💡 {issue.suggestion}")
                
                if len(priority_issues) > 10:
                    print(f"      ... and {len(priority_issues) - 10} more")
    
    # Summary
    print("\n" + "-" * 70)
    print("📊 SUMMARY")
    print("-" * 70)
    print(f"   🔴 P0 (Critical):  {total_p0}")
    print(f"   🟠 P1 (Error):     {total_p1}")
    print(f"   🟡 P2 (Warning):   {total_p2}")
    print(f"   ⚪ P3 (Info):      {total_p3}")
    print(f"   ─────────────────────")
    print(f"   Total Issues:      {total_p0 + total_p1 + total_p2 + total_p3}")
    
    if total_p0 + total_p1 > 0:
        print("\n   ❌ STATUS: BLOCKING - Must fix P0/P1 issues before commit")
    elif total_p2 > 0:
        print("\n   ⚠️  STATUS: WARNING - Should fix P2 issues")
    else:
        print("\n   ✅ STATUS: PASS - No blocking issues")
    
    print("=" * 70)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check code files for lint errors and warnings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python lint_check.py src/app.py                    # Check single file
  python lint_check.py src/app.py src/utils.ts       # Check multiple files (parallel)
  python lint_check.py --dir src/                    # Check directory
  python lint_check.py src/app.py --fix              # Auto-fix if possible
  python lint_check.py --check-deps                  # Check linter dependencies
  python lint_check.py src/app.py --json             # JSON output for CI/CD
        """
    )
    parser.add_argument('files', nargs='*', help='Files to check')
    parser.add_argument('--dir', '-d', help='Check all supported files in directory')
    parser.add_argument('--fix', '-f', action='store_true', help='Attempt to auto-fix issues')
    parser.add_argument('--check-deps', action='store_true', help='Check linter dependencies')
    parser.add_argument('--summary-only', '-s', action='store_true', help='Only show summary')
    parser.add_argument('--json', '-j', action='store_true', help='Output results as JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    parser.add_argument('--ext', action='append', help='File extensions to check')
    parser.add_argument('--workers', '-w', type=int, default=4, help='Number of parallel workers')
    
    args = parser.parse_args()
    
    checker = LintChecker(verbose=args.verbose, max_workers=args.workers)
    
    # Check dependencies mode
    if args.check_deps:
        deps = checker.check_dependencies()
        if args.json:
            print(json.dumps([asdict(d) for d in deps], indent=2))
        else:
            print_dependencies(deps)
        return 0 if all(d.available for d in deps) else 3
    
    if not args.files and not args.dir:
        parser.print_help()
        return 1
    
    if args.dir:
        results = checker.check_directory(args.dir, auto_fix=args.fix, extensions=args.ext)
    else:
        results = checker.check_files(args.files, auto_fix=args.fix)
    
    print_issues(results, summary_only=args.summary_only, json_output=args.json)
    
    # Determine exit code
    total_p0 = sum(r.p0_count for r in results)
    total_p1 = sum(r.p1_count for r in results)
    total_p2 = sum(r.p2_count for r in results)
    
    if not all(r.success for r in results):
        if any("not available" in (r.error_message or "") for r in results):
            return 3
    
    if total_p0 + total_p1 > 0:
        return 1
    elif total_p2 > 0:
        return 2
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
