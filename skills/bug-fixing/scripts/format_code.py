#!/usr/bin/env python3
"""
Code Formatting Script - Auto-format code files after modification.

Features:
- Supports Python (ruff/black), TypeScript/JavaScript (prettier), Go, Rust
- Auto-detects and suggests missing formatters
- Parallel processing for multiple files
- JSON output for CI/CD integration
- Respects project config files (.prettierrc, pyproject.toml, etc.)

Usage:
    python format_code.py <file_path> [--check-only] [--json]
    python format_code.py <file1> <file2> ...       # Multiple files (parallel)
    python format_code.py --dir <directory>         # Format directory
    python format_code.py --check-deps              # Check dependencies

Exit codes:
    0 - Success (formatted or already formatted)
    1 - Formatting failed or file not found
    2 - Formatter not available (install required)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import os
import json as json_module
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, asdict
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


@dataclass
class FormatResult:
    """Result of formatting a single file"""
    file_path: str
    success: bool
    changed: bool
    message: str
    formatter_used: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DependencyStatus:
    """Status of a formatter dependency"""
    name: str
    available: bool
    version: Optional[str] = None
    install_cmd: Optional[str] = None


class CodeFormatter:
    """Multi-language code formatter with fallback support"""
    
    # File extension to language mapping
    EXTENSION_MAP = {
        # Python
        '.py': 'python', '.pyw': 'python', '.pyi': 'python',
        # JavaScript/TypeScript
        '.ts': 'typescript', '.tsx': 'typescript',
        '.js': 'javascript', '.jsx': 'javascript',
        '.mjs': 'javascript', '.cjs': 'javascript',
        # Web
        '.json': 'json', '.css': 'css', '.scss': 'scss', '.less': 'less',
        '.html': 'html', '.vue': 'vue', '.svelte': 'svelte',
        '.yaml': 'yaml', '.yml': 'yaml', '.md': 'markdown',
        # Other languages
        '.go': 'go', '.rs': 'rust', '.sql': 'sql',
    }
    
    # Formatter install commands
    INSTALL_COMMANDS = {
        'ruff': 'pip install ruff',
        'black': 'pip install black',
        'prettier': 'npm install -g prettier',
        'gofmt': 'Included with Go installation',
        'rustfmt': 'rustup component add rustfmt',
    }
    
    def __init__(self, verbose: bool = False, max_workers: int = 4):
        self.verbose = verbose
        self.max_workers = max_workers
        self._formatter_cache: Dict[str, bool] = {}
        self._version_cache: Dict[str, str] = {}
        self._cache_lock = threading.Lock()
    
    def _log(self, message: str) -> None:
        if self.verbose:
            print(f"[FORMAT] {message}", file=sys.stderr)
    
    def _check_command(self, cmd: str) -> bool:
        """Check if a command is available (thread-safe)"""
        with self._cache_lock:
            if cmd in self._formatter_cache:
                return self._formatter_cache[cmd]
        
        try:
            check_cmd = 'where' if sys.platform == 'win32' else 'which'
            result = subprocess.run(
                [check_cmd, cmd],
                capture_output=True,
                text=True,
                timeout=5
            )
            available = result.returncode == 0
        except Exception:
            available = False
        
        with self._cache_lock:
            self._formatter_cache[cmd] = available
        return available
    
    def _get_version(self, cmd: str, version_flag: str = '--version') -> Optional[str]:
        """Get version of a command"""
        with self._cache_lock:
            if cmd in self._version_cache:
                return self._version_cache[cmd]
        
        try:
            result = subprocess.run(
                [cmd, version_flag],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                with self._cache_lock:
                    self._version_cache[cmd] = version
                return version
        except Exception:
            pass
        return None
    
    def check_dependencies(self) -> List[DependencyStatus]:
        """Check all formatter dependencies"""
        deps = []
        
        # Python formatters
        for name in ['ruff', 'black']:
            available = self._check_command(name)
            deps.append(DependencyStatus(
                name=name,
                available=available,
                version=self._get_version(name) if available else None,
                install_cmd=self.INSTALL_COMMANDS.get(name)
            ))
        
        # Node.js formatters
        for name in ['prettier']:
            # Check both global and npx
            available = self._check_command(name) or self._check_command('npx')
            deps.append(DependencyStatus(
                name=name,
                available=available,
                version=self._get_version('prettier') if self._check_command('prettier') else 'via npx',
                install_cmd=self.INSTALL_COMMANDS.get(name)
            ))
        
        # Go formatter
        available = self._check_command('gofmt')
        deps.append(DependencyStatus(
            name='gofmt',
            available=available,
            version=self._get_version('go', 'version') if available else None,
            install_cmd=self.INSTALL_COMMANDS.get('gofmt')
        ))
        
        # Rust formatter
        available = self._check_command('rustfmt')
        deps.append(DependencyStatus(
            name='rustfmt',
            available=available,
            version=self._get_version('rustfmt') if available else None,
            install_cmd=self.INSTALL_COMMANDS.get('rustfmt')
        ))
        
        return deps
    
    def _run_formatter(self, cmd: List[str], file_path: str, timeout: int = 30) -> Tuple[bool, str]:
        """Run a formatter command and return (success, message)"""
        try:
            self._log(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout,
                cwd=Path(file_path).parent  # Run in file's directory for config detection
            )
            if result.returncode == 0:
                return True, "Formatted successfully"
            else:
                error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                # Truncate long error messages
                if len(error_msg) > 200:
                    error_msg = error_msg[:200] + "..."
                return False, f"Formatter error: {error_msg}"
        except subprocess.TimeoutExpired:
            return False, f"Formatter timeout ({timeout}s)"
        except Exception as e:
            return False, f"Failed to run formatter: {e}"
    
    def _format_python(self, file_path: str, check_only: bool = False) -> FormatResult:
        """Format Python file using ruff (preferred) or black"""
        path = Path(file_path).resolve()
        
        # Try ruff first (faster, more features)
        if self._check_command('ruff'):
            cmd = ['ruff', 'format']
            if check_only:
                cmd.append('--check')
            cmd.append(str(path))
            
            success, message = self._run_formatter(cmd, file_path)
            return FormatResult(
                file_path=str(path),
                success=success,
                changed=success and not check_only,
                message=message,
                formatter_used='ruff'
            )
        
        # Fall back to black
        if self._check_command('black'):
            cmd = ['black']
            if check_only:
                cmd.append('--check')
            cmd.append(str(path))
            
            success, message = self._run_formatter(cmd, file_path)
            return FormatResult(
                file_path=str(path),
                success=success,
                changed=success and not check_only,
                message=message,
                formatter_used='black'
            )
        
        return FormatResult(
            file_path=str(path),
            success=False,
            changed=False,
            message="No Python formatter available. Install: pip install ruff"
        )
    
    def _format_js_ts(self, file_path: str, check_only: bool = False) -> FormatResult:
        """Format JavaScript/TypeScript using prettier"""
        path = Path(file_path).resolve()
        
        prettier_cmd = None
        if self._check_command('prettier'):
            prettier_cmd = ['prettier']
        elif self._check_command('npx'):
            prettier_cmd = ['npx', '--yes', 'prettier']
        
        if prettier_cmd:
            cmd = prettier_cmd.copy()
            if check_only:
                cmd.append('--check')
            else:
                cmd.append('--write')
            cmd.append(str(path))
            
            success, message = self._run_formatter(cmd, file_path)
            return FormatResult(
                file_path=str(path),
                success=success,
                changed=success and not check_only,
                message=message,
                formatter_used='prettier'
            )
        
        return FormatResult(
            file_path=str(path),
            success=False,
            changed=False,
            message="No JS/TS formatter available. Install: npm install -g prettier"
        )
    
    def _format_go(self, file_path: str, check_only: bool = False) -> FormatResult:
        """Format Go file using gofmt"""
        path = Path(file_path).resolve()
        
        if self._check_command('gofmt'):
            if check_only:
                # gofmt -d returns diff, non-empty means needs formatting
                cmd = ['gofmt', '-d', str(path)]
                success, message = self._run_formatter(cmd, file_path)
                return FormatResult(
                    file_path=str(path),
                    success=True,
                    changed=bool(message and 'diff' not in message.lower()),
                    message="Check completed",
                    formatter_used='gofmt'
                )
            else:
                cmd = ['gofmt', '-w', str(path)]
                success, message = self._run_formatter(cmd, file_path)
                return FormatResult(
                    file_path=str(path),
                    success=success,
                    changed=success,
                    message=message,
                    formatter_used='gofmt'
                )
        
        return FormatResult(
            file_path=str(path),
            success=False,
            changed=False,
            message="gofmt not available. Install Go from https://golang.org/"
        )
    
    def _format_rust(self, file_path: str, check_only: bool = False) -> FormatResult:
        """Format Rust file using rustfmt"""
        path = Path(file_path).resolve()
        
        if self._check_command('rustfmt'):
            cmd = ['rustfmt']
            if check_only:
                cmd.append('--check')
            cmd.append(str(path))
            
            success, message = self._run_formatter(cmd, file_path)
            return FormatResult(
                file_path=str(path),
                success=success,
                changed=success and not check_only,
                message=message,
                formatter_used='rustfmt'
            )
        
        return FormatResult(
            file_path=str(path),
            success=False,
            changed=False,
            message="rustfmt not available. Install: rustup component add rustfmt"
        )
    
    def _format_json(self, file_path: str, check_only: bool = False) -> FormatResult:
        """Format JSON using prettier or Python json module"""
        path = Path(file_path).resolve()
        
        # Try prettier first
        prettier_result = self._format_js_ts(file_path, check_only)
        if prettier_result.success:
            return prettier_result
        
        # Fall back to Python json module
        try:
            content = path.read_text(encoding='utf-8')
            parsed = json_module.loads(content)
            formatted = json_module.dumps(parsed, indent=2, ensure_ascii=False) + '\n'
            
            if check_only:
                changed = content != formatted
                return FormatResult(
                    file_path=str(path),
                    success=True,
                    changed=changed,
                    message="Check passed" if not changed else "File needs formatting",
                    formatter_used='python-json'
                )
            
            if content != formatted:
                path.write_text(formatted, encoding='utf-8')
                return FormatResult(
                    file_path=str(path),
                    success=True,
                    changed=True,
                    message="Formatted successfully",
                    formatter_used='python-json'
                )
            
            return FormatResult(
                file_path=str(path),
                success=True,
                changed=False,
                message="Already formatted",
                formatter_used='python-json'
            )
        except Exception as e:
            return FormatResult(
                file_path=str(path),
                success=False,
                changed=False,
                message=f"JSON format error: {e}"
            )
    
    def format_file(self, file_path: str, check_only: bool = False) -> FormatResult:
        """Format a single file based on its extension"""
        path = Path(file_path)
        
        if not path.exists():
            return FormatResult(
                file_path=str(path),
                success=False,
                changed=False,
                message=f"File not found: {file_path}"
            )
        
        ext = path.suffix.lower()
        language = self.EXTENSION_MAP.get(ext)
        
        if language == 'python':
            return self._format_python(file_path, check_only)
        elif language in ('typescript', 'javascript', 'css', 'scss', 'less', 
                          'markdown', 'html', 'vue', 'svelte', 'yaml'):
            return self._format_js_ts(file_path, check_only)
        elif language == 'json':
            return self._format_json(file_path, check_only)
        elif language == 'go':
            return self._format_go(file_path, check_only)
        elif language == 'rust':
            return self._format_rust(file_path, check_only)
        elif language == 'sql':
            # SQL formatting via prettier-plugin-sql (if available)
            return self._format_js_ts(file_path, check_only)
        else:
            return FormatResult(
                file_path=str(path),
                success=True,
                changed=False,
                message=f"No formatter configured for extension: {ext}"
            )
    
    def format_files(self, file_paths: List[str], check_only: bool = False) -> List[FormatResult]:
        """Format multiple files (parallel processing)"""
        if len(file_paths) == 1:
            return [self.format_file(file_paths[0], check_only)]
        
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {
                executor.submit(self.format_file, path, check_only): path 
                for path in file_paths
            }
            for future in as_completed(future_to_path):
                result = future.result()
                results.append(result)
                self._log(f"{result.file_path}: {result.message}")
        
        # Sort by original order
        path_order = {path: i for i, path in enumerate(file_paths)}
        results.sort(key=lambda r: path_order.get(r.file_path, 999))
        return results
    
    def format_directory(self, dir_path: str, check_only: bool = False,
                        extensions: Optional[List[str]] = None) -> List[FormatResult]:
        """Format all supported files in a directory"""
        path = Path(dir_path)
        if not path.exists():
            return [FormatResult(
                file_path=str(path),
                success=False,
                changed=False,
                message=f"Directory not found: {dir_path}"
            )]
        
        if extensions is None:
            extensions = list(self.EXTENSION_MAP.keys())
        
        files = []
        for ext in extensions:
            files.extend(path.rglob(f'*{ext}'))
        
        # Filter out common exclusions
        exclude_patterns = [
            'node_modules', '__pycache__', '.git', 'dist', 'build', 
            'venv', '.venv', 'target', '.next', '.nuxt', 'coverage'
        ]
        files = [f for f in files if not any(p in str(f) for p in exclude_patterns)]
        
        return self.format_files([str(f) for f in files], check_only)


def print_dependencies(deps: List[DependencyStatus]) -> None:
    """Print dependency status"""
    print("\n" + "=" * 60)
    print("🔧 FORMATTER DEPENDENCIES")
    print("=" * 60)
    
    for dep in deps:
        status = "✅" if dep.available else "❌"
        version = f" ({dep.version})" if dep.version else ""
        print(f"  {status} {dep.name}{version}")
        if not dep.available and dep.install_cmd:
            print(f"      Install: {dep.install_cmd}")
    
    print("=" * 60)


def print_summary(results: List[FormatResult], json_output: bool = False) -> None:
    """Print a summary of formatting results"""
    if json_output:
        output = {
            'results': [r.to_dict() for r in results],
            'summary': {
                'total': len(results),
                'success': sum(1 for r in results if r.success),
                'changed': sum(1 for r in results if r.changed),
                'failed': sum(1 for r in results if not r.success)
            }
        }
        print(json_module.dumps(output, indent=2, ensure_ascii=False))
        return
    
    print("\n" + "=" * 60)
    print("📋 FORMATTING SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r.success)
    changed_count = sum(1 for r in results if r.changed)
    failed_count = len(results) - success_count
    
    for result in results:
        status = "✅" if result.success else "❌"
        change = "(changed)" if result.changed else ""
        formatter = f"[{result.formatter_used}]" if result.formatter_used else ""
        print(f"  {status} {result.file_path} {formatter} {change}")
        if not result.success:
            print(f"      → {result.message}")
    
    print("-" * 60)
    print(f"Total: {len(results)} | ✅ Success: {success_count} | 🔄 Changed: {changed_count} | ❌ Failed: {failed_count}")
    print("=" * 60)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Format code files (Python, TypeScript, JavaScript, Go, Rust, etc.)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python format_code.py src/app.py                    # Format single file
  python format_code.py src/app.py src/utils.ts       # Format multiple files (parallel)
  python format_code.py --dir src/                    # Format directory
  python format_code.py src/app.py --check-only       # Check without modifying
  python format_code.py --check-deps                  # Check formatter dependencies
  python format_code.py src/app.py --json             # JSON output for CI/CD
        """
    )
    parser.add_argument('files', nargs='*', help='Files to format')
    parser.add_argument('--dir', '-d', help='Format all supported files in directory')
    parser.add_argument('--check-only', '-c', action='store_true', help='Check if files need formatting without modifying')
    parser.add_argument('--check-deps', action='store_true', help='Check formatter dependencies')
    parser.add_argument('--json', '-j', action='store_true', help='Output results as JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    parser.add_argument('--ext', action='append', help='File extensions to format (can specify multiple)')
    parser.add_argument('--workers', '-w', type=int, default=4, help='Number of parallel workers (default: 4)')
    
    args = parser.parse_args()
    
    formatter = CodeFormatter(verbose=args.verbose, max_workers=args.workers)
    
    # Check dependencies mode
    if args.check_deps:
        deps = formatter.check_dependencies()
        if args.json:
            print(json_module.dumps([asdict(d) for d in deps], indent=2))
        else:
            print_dependencies(deps)
        return 0 if all(d.available for d in deps) else 2
    
    if not args.files and not args.dir:
        parser.print_help()
        return 1
    
    if args.dir:
        results = formatter.format_directory(args.dir, check_only=args.check_only, extensions=args.ext)
    else:
        results = formatter.format_files(args.files, check_only=args.check_only)
    
    print_summary(results, json_output=args.json)
    
    # Return appropriate exit code
    if all(r.success for r in results):
        return 0
    elif any("not available" in (r.message or "") for r in results):
        return 2
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
