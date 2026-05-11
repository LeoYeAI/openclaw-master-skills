---
name: phy-path-traversal-audit
description: Path traversal and Local File Inclusion (LFI) vulnerability scanner (OWASP A01:2021). Detects user-controlled paths passed to file system sinks in Python/Java/PHP/Node.js/Go/Ruby without containment checks. Identifies missing os.path.abspath+startswith, realpath validation, basename stripping, and PHP include/require with user input. Outputs CWE-22/CWE-23 findings with HTTP taint analysis and per-language safe-path-handling code snippets. Zero competitors on ClawHub.
license: Apache-2.0
tags:
  - security
  - path-traversal
  - lfi
  - owasp
  - python
  - java
  - php
  - nodejs
  - go
  - ruby
metadata:
  author: PHY041
  version: "1.0.0"
---

# phy-path-traversal-audit

Static scanner for **OWASP A01:2021 — Broken Access Control / Path Traversal** (CWE-22) and **Local File Inclusion** (CWE-98). Finds file system sinks that accept user-controlled paths, checks for missing containment guards, and flags PHP `include`/`require` patterns that allow template injection. Zero external API calls, zero dependencies beyond Python 3 stdlib.

## What Is Path Traversal?

An attacker passes `../../etc/passwd` or `..%2F..%2Fetc%2Fshadow` as a filename parameter. Without validation, your code reads arbitrary files outside the intended base directory. With PHP `include`, it can lead to Remote Code Execution.

**Classic exploit:**
```
GET /api/files?path=../../etc/passwd HTTP/1.1
```
If your handler does `open("uploads/" + request.args["path"])`, attacker reads `/etc/passwd`.

## What It Detects

### Python
| Pattern | Severity | Notes |
|---------|----------|-------|
| `open(user_path)` | CRITICAL | Direct file read with user path |
| `open(os.path.join(base, user_input))` without `abspath`+`startswith` | HIGH | Join doesn't sanitize `../` |
| `pathlib.Path(user_path).read_text()` | CRITICAL | pathlib doesn't sanitize traversal |
| `Path(base).joinpath(user_input)` without `.resolve().is_relative_to(base)` | HIGH | |
| `os.listdir(user_path)` | HIGH | Directory listing disclosure |
| `os.open(user_path, os.O_RDONLY)` | CRITICAL | Low-level file open |
| `shutil.copy/move(user_src, ...)` | HIGH | File operation with user src |
| `tarfile.open(user_path)` | HIGH | Zip/tar slip (CVE-class) |
| `zipfile.ZipFile(user_path)` | HIGH | Zip slip attack |

### Java
| Pattern | Severity | Notes |
|---------|----------|-------|
| `new File(baseDir + userInput)` | CRITICAL | String concat without normalization |
| `new FileInputStream(userInput)` | CRITICAL | Direct file read |
| `Paths.get(userInput)` | HIGH | Path construction without validation |
| `Files.readAllBytes(Path.of(userInput))` | CRITICAL | File read |
| `Files.newBufferedReader(Paths.get(userInput))` | CRITICAL | File read |
| `new File(request.getServletContext().getRealPath(userInput))` | CRITICAL | Servlet path traversal |
| `response.setHeader("Content-Disposition", "..."+userInput)` | MEDIUM | Filename injection |

### PHP
| Pattern | Severity | Notes |
|---------|----------|-------|
| `include($_GET['page'])` / `include($_POST['file'])` | CRITICAL | LFI → RCE via log poisoning |
| `require($_GET['file'])` | CRITICAL | LFI |
| `include_once($_GET[...])` / `require_once($_GET[...])` | CRITICAL | LFI |
| `readfile($_GET['file'])` | CRITICAL | File disclosure |
| `file_get_contents($_GET['path'])` | HIGH | File/URL read |
| `fopen($_GET['file'], 'r')` | CRITICAL | File open |
| `file($_GET['path'])` | HIGH | Read file into array |
| `highlight_file($_GET['file'])` | CRITICAL | PHP source disclosure |
| `include("pages/" . $_GET['page'] . ".php")` | HIGH | Partial mitigation (extension added) but still exploitable via null byte on older PHP |

### Node.js / TypeScript
| Pattern | Severity | Notes |
|---------|----------|-------|
| `fs.readFile(req.params.path, ...)` | CRITICAL | Direct file read |
| `fs.readFileSync(req.query.file)` | CRITICAL | Sync file read |
| `fs.createReadStream(req.body.path)` | CRITICAL | Stream file read |
| `res.sendFile(req.params.filename)` | HIGH | Express static file serve |
| `res.download(req.query.file)` | HIGH | File download |
| `path.join(__dirname, req.params.file)` without `path.resolve`+`startsWith` check | HIGH | Join alone is insufficient |
| `require(req.params.module)` | CRITICAL | Path traversal + arbitrary code execution |
| `fs.readdirSync(req.query.dir)` | HIGH | Directory listing |

### Go
| Pattern | Severity | Notes |
|---------|----------|-------|
| `os.Open(r.FormValue("path"))` | CRITICAL | Direct file open |
| `os.ReadFile(r.URL.Query().Get("file"))` | CRITICAL | File read |
| `http.ServeFile(w, r, r.FormValue("path"))` | CRITICAL | File serve — `http.ServeFile` has some built-in protection but verify |
| `filepath.Join(base, r.FormValue("name"))` without `filepath.Clean`+containment | HIGH | |
| `os.Stat(r.FormValue("path"))` | MEDIUM | Path existence disclosure |

### Ruby
| Pattern | Severity | Notes |
|---------|----------|-------|
| `File.open(params[:path])` | CRITICAL | File open |
| `File.read(params[:file])` | CRITICAL | File read |
| `IO.read(params[:file])` | CRITICAL | File read |
| `send_file(params[:path])` | CRITICAL | Rails file serve |
| `send_data(File.read(params[:file]))` | CRITICAL | File read + serve |
| `render params[:template]` | CRITICAL | Template injection (+ path traversal) |
| `erb.result(binding) where erb from params` | CRITICAL | Template injection |

## Containment Guard Detection

After finding a sink, the scanner checks if a safe-path guard exists within ±40 lines. If found, the finding is downgraded or suppressed:

**Python safe guards:**
```python
# Correct: resolve to absolute, then check containment
safe_path = os.path.abspath(os.path.join(BASE_DIR, user_input))
if not safe_path.startswith(BASE_DIR):
    raise PermissionError("path traversal detected")

# Also safe: pathlib.resolve() + is_relative_to()
resolved = (Path(BASE_DIR) / user_input).resolve()
if not resolved.is_relative_to(BASE_DIR):
    raise ValueError("path traversal")
```

**Java safe guards:**
```java
// Correct: normalize and verify containment
Path safePath = Paths.get(baseDir).resolve(userInput).normalize().toAbsolutePath();
if (!safePath.startsWith(Paths.get(baseDir).toAbsolutePath())) {
    throw new SecurityException("Path traversal detected");
}
```

**Node.js safe guards:**
```javascript
// Correct: resolve and check startsWith
const safePath = path.resolve(BASE_DIR, userInput);
if (!safePath.startsWith(BASE_DIR + path.sep)) {
    throw new Error("Path traversal detected");
}
```

**PHP safe guards:**
```php
// Correct: realpath + containment check
$path = realpath(BASE_DIR . '/' . $userInput);
if ($path === false || strpos($path, BASE_DIR) !== 0) {
    http_response_code(403);
    exit('Forbidden');
}
// Also: basename() strips directory components (partial mitigation)
$filename = basename($_GET['file']); // removes ../
```

**Go safe guards:**
```go
// Correct: Clean + containment check
safePath := filepath.Join(baseDir, filepath.Clean("/"+r.FormValue("path")))
if !strings.HasPrefix(safePath, baseDir+string(os.PathSeparator)) {
    http.Error(w, "Forbidden", 403)
    return
}
```

## Zip Slip Detection

Tar/zip extraction without path validation enables a special case of path traversal where malicious archives overwrite files outside the extraction directory:

```python
# DANGEROUS — zip slip
with zipfile.ZipFile(archive) as zf:
    zf.extractall(extract_dir)  # member names not validated

# SAFE
import zipfile, os
with zipfile.ZipFile(archive) as zf:
    for member in zf.infolist():
        member_path = os.path.abspath(os.path.join(extract_dir, member.filename))
        if not member_path.startswith(os.path.abspath(extract_dir) + os.sep):
            raise ValueError(f"Zip slip: {member.filename}")
        zf.extract(member, extract_dir)
```

The scanner detects `zipfile.ZipFile.extractall()`, `tarfile.TarFile.extractall()`, `ZipInputStream` in Java, `net/http` archiver patterns in Go.

## Implementation

```python
#!/usr/bin/env python3
"""
phy-path-traversal-audit — OWASP A01:2021 path traversal scanner
Usage: python3 audit_path_traversal.py [path] [--json] [--ci]
"""
import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

CRITICAL, HIGH, MEDIUM, INFO = "CRITICAL", "HIGH", "MEDIUM", "INFO"
SEV_ORDER = {CRITICAL: 0, HIGH: 1, MEDIUM: 2, INFO: 3}
ICONS = {CRITICAL: "🔴", HIGH: "🟠", MEDIUM: "🟡", INFO: "⚪"}

@dataclass
class Finding:
    file: str
    line: int
    pattern_name: str
    matched_text: str
    severity: str
    cwe: str
    description: str
    fix: str
    has_http_taint: bool = False

PATTERNS = {
    ".py": [
        ("OPEN_DIRECT",
         re.compile(r'\bopen\s*\('),
         CRITICAL, "CWE-22",
         "open() with user-controlled path enables arbitrary file read/write.",
         "Resolve to absolute path, then verify it starts with the allowed base directory."),

        ("PATHLIB_READ",
         re.compile(r'\bPath\s*\([^)]+\)\.(?:read_text|read_bytes|open)\s*\('),
         CRITICAL, "CWE-22",
         "pathlib.Path().read_text/bytes with user path — Path() does not sanitize ../.",
         "Use (Path(BASE_DIR) / user_input).resolve().is_relative_to(BASE_DIR) before reading."),

        ("OS_PATH_JOIN_NO_ABSPATH",
         re.compile(r'\bos\.path\.join\s*\([^)]+\)'),
         HIGH, "CWE-22",
         "os.path.join() alone doesn't prevent traversal — '../' components are preserved.",
         "After join: safe = os.path.abspath(joined); assert safe.startswith(BASE_DIR)."),

        ("OS_LISTDIR",
         re.compile(r'\bos\.listdir\s*\('),
         HIGH, "CWE-22",
         "os.listdir() with user path exposes directory contents.",
         "Validate path against BASE_DIR allowlist before listing."),

        ("ZIP_EXTRACTALL",
         re.compile(r'\bextractall\s*\('),
         HIGH, "CWE-22",
         "extractall() without member path validation enables zip-slip attack.",
         "Validate each member path before extraction (see zip-slip safe pattern)."),

        ("TARFILE_EXTRACT",
         re.compile(r'\btarfile\.open\s*\(|\b\.extract\s*\('),
         HIGH, "CWE-22",
         "tarfile extract without member path validation enables tar-slip.",
         "Use tarfile.data_filter (Python 3.12+) or manually check member.name."),
    ],
    ".java": [
        ("NEW_FILE_CONCAT",
         re.compile(r'\bnew\s+File\s*\([^)]+\+\s*\w+\s*\)'),
         CRITICAL, "CWE-22",
         "new File(base + userInput) — string concatenation without path normalization.",
         "Use Paths.get(base).resolve(userInput).normalize() then check startsWith(base)."),

        ("NEW_FILE_INPUT_STREAM",
         re.compile(r'\bnew\s+FileInputStream\s*\('),
         CRITICAL, "CWE-22",
         "FileInputStream with user-controlled path enables arbitrary file read.",
         "Normalize and validate path before constructing FileInputStream."),

        ("FILES_READ",
         re.compile(r'\bFiles\.(readAllBytes|readString|newBufferedReader|newInputStream)\s*\('),
         CRITICAL, "CWE-22",
         "Files.readAllBytes/readString with user path enables path traversal.",
         "Validate path: Path.of(base).resolve(userInput).normalize().toAbsolutePath() starts with base."),

        ("PATHS_GET",
         re.compile(r'\bPaths\.get\s*\('),
         HIGH, "CWE-22",
         "Paths.get() with user input — check for subsequent normalize()+startsWith() guard.",
         "Always follow with .normalize().toAbsolutePath() and containment check."),

        ("SERVLET_REAL_PATH",
         re.compile(r'\.getRealPath\s*\('),
         CRITICAL, "CWE-22",
         "getRealPath() with user input translates to filesystem path — path traversal.",
         "Validate user input before passing to getRealPath(); prefer serving from classpath."),
    ],
    ".php": [
        ("PHP_INCLUDE_INPUT",
         re.compile(r'\b(?:include|require|include_once|require_once)\s*\(\s*\$(?:_GET|_POST|_REQUEST|_COOKIE)\b'),
         CRITICAL, "CWE-98",
         "PHP include/require with HTTP input — Local File Inclusion → potential RCE via log poisoning.",
         "NEVER use include/require with user input. Use a whitelist: $allowed = ['home', 'about']; "
         "if (!in_array($page, $allowed)) die('invalid');"),

        ("PHP_INCLUDE_VAR",
         re.compile(r'\b(?:include|require|include_once|require_once)\s*\([^)]*\$'),
         HIGH, "CWE-98",
         "PHP include/require with variable — verify variable is not user-controlled.",
         "Use a whitelist of allowed template names; never construct include path from user input."),

        ("PHP_READFILE_INPUT",
         re.compile(r'\b(?:readfile|highlight_file|show_source)\s*\(\s*\$(?:_GET|_POST|_REQUEST)\b'),
         CRITICAL, "CWE-22",
         "readfile/highlight_file with HTTP input — arbitrary file read/PHP source disclosure.",
         "Validate and sanitize filename; use basename() + allowlist; resolve + containment check."),

        ("PHP_FOPEN_INPUT",
         re.compile(r'\bfopen\s*\(\s*\$(?:_GET|_POST|_REQUEST|_COOKIE)\b'),
         CRITICAL, "CWE-22",
         "fopen() with HTTP input — arbitrary file open.",
         "Validate path with realpath(); check containment: strpos(realpath, BASE_DIR) === 0."),

        ("PHP_FILE_GET_CONTENTS",
         re.compile(r'\bfile(?:_get_contents|_put_contents|)\s*\(\s*\$(?:_GET|_POST|_REQUEST)\b'),
         CRITICAL, "CWE-22",
         "file_get_contents/file with HTTP input — arbitrary file read.",
         "Validate: $safe = realpath(BASE_DIR.'/'.basename($input)); if (!str_starts_with($safe, BASE_DIR)) { die(); }"),
    ],
    ".js": _build_js_path_patterns(),
    ".ts": _build_js_path_patterns(),
    ".go": [
        ("OS_OPEN_FORM",
         re.compile(r'\bos\.(?:Open|ReadFile|OpenFile|Create)\s*\(\s*r\.(?:FormValue|URL\.Query\(\)\.Get|Form\.Get)\s*\('),
         CRITICAL, "CWE-22",
         "os.Open/ReadFile with form value — direct path traversal.",
         "filepath.Clean(\"/\"+userInput) then filepath.Join(baseDir, cleaned); verify strings.HasPrefix(result, baseDir)."),

        ("FILEPATH_JOIN_NO_GUARD",
         re.compile(r'\bfilepath\.Join\s*\('),
         HIGH, "CWE-22",
         "filepath.Join with user input — Join alone doesn't prevent traversal.",
         "After join: safe := filepath.Clean(joined); if !strings.HasPrefix(safe, baseDir+sep) { error }"),

        ("HTTP_SERVE_FILE",
         re.compile(r'\bhttp\.ServeFile\s*\('),
         HIGH, "CWE-22",
         "http.ServeFile — Go's stdlib adds some protection but explicit validation is safer.",
         "Validate path against allowed directory before calling ServeFile."),
    ],
    ".rb": [
        ("FILE_OPEN_PARAMS",
         re.compile(r'\b(?:File\.open|File\.read|IO\.read|IO\.binread)\s*\(\s*params\['),
         CRITICAL, "CWE-22",
         "File.open/read with params — arbitrary file read.",
         "Validate: path = Rails.root.join('safe_dir', File.basename(params[:file]))\n"
         "raise unless path.to_s.start_with?(Rails.root.join('safe_dir').to_s)"),

        ("SEND_FILE_PARAMS",
         re.compile(r'\bsend_file\s*\(\s*params\['),
         CRITICAL, "CWE-22",
         "Rails send_file with params — arbitrary file download.",
         "Whitelist allowed filenames; never construct path from user input."),

        ("RENDER_PARAMS_TEMPLATE",
         re.compile(r'\brender\s+params\['),
         CRITICAL, "CWE-98",
         "Rails render with params — template injection + path traversal.",
         "Whitelist allowed template names: ALLOWED_TEMPLATES = ['home', 'about']\n"
         "render params[:page] if ALLOWED_TEMPLATES.include?(params[:page])"),
    ],
}

def _build_js_path_patterns():
    return [
        ("FS_READFILE_PARAM",
         re.compile(r'\bfs\.(?:readFile|readFileSync|createReadStream|readdirSync|stat|statSync)\s*\(\s*req\.[a-zA-Z.[\]'"]+'),
         CRITICAL, "CWE-22",
         "fs.readFile/readFileSync with request param — direct path traversal.",
         "const safe = path.resolve(BASE_DIR, req.params.file);\n"
         "if (!safe.startsWith(BASE_DIR + path.sep)) throw new Error('Forbidden');\n"
         "fs.readFile(safe, ...)"),

        ("RES_SENDFILE_PARAM",
         re.compile(r'\bres\.(?:sendFile|download)\s*\(\s*(?:path\.join\s*\([^)]+\)|req\.[a-zA-Z.[\]'"]+)'),
         HIGH, "CWE-22",
         "res.sendFile/download with request param — path traversal.",
         "Validate path before sending. res.sendFile only after containment check."),

        ("PATH_JOIN_NO_RESOLVE",
         re.compile(r'\bpath\.join\s*\([^)]*(?:req\.|__dirname)[^)]*\)'),
         HIGH, "CWE-22",
         "path.join() with request input — join preserves ../ components.",
         "After join: const safe = path.resolve(joined); assert safe.startsWith(BASE_DIR)."),

        ("REQUIRE_DYNAMIC",
         re.compile(r'\brequire\s*\(\s*(?:path\.join|req\.[a-zA-Z.[\]'"]+)'),
         CRITICAL, "CWE-22",
         "require() with user-controlled path — path traversal + arbitrary code execution.",
         "Never use require() with user input. Use a module whitelist."),

        ("FS_WRITE_PARAM",
         re.compile(r'\bfs\.(?:writeFile|writeFileSync|appendFile|appendFileSync)\s*\(\s*req\.[a-zA-Z.[\]'"]+'),
         CRITICAL, "CWE-22",
         "fs.writeFile with request param — arbitrary file write (can overwrite config/keys).",
         "Validate destination path against BASE_DIR; never allow writing outside allowed dirs."),
    ]

HTTP_MARKERS = {
    ".py":   re.compile(r'request\.(args|form|json|data|files|GET|POST|params)|flask\.request|starlette|fastapi|aiohttp\.web'),
    ".java": re.compile(r'HttpServletRequest|@RequestParam|@PathVariable|getParameter\(|request\.getParameter|@RequestBody'),
    ".php":  re.compile(r'\$_(?:GET|POST|REQUEST|COOKIE|FILES)'),
    ".rb":   re.compile(r'\bparams\[|request\.(body|params|query_string)'),
    ".js":   re.compile(r'\breq\.(body|params|query|headers)|ctx\.(query|body|params)'),
    ".ts":   re.compile(r'\breq\.(body|params|query|headers)|ctx\.(query|body|params)'),
    ".go":   re.compile(r'r\.(FormValue\(|URL\.Query\(\)\.Get|Form\.Get|Body|Header\.Get\()'),
}

GUARD_PATTERNS = {
    ".py":   re.compile(r'os\.path\.abspath|\.resolve\(\)|\.is_relative_to|startswith\s*\(.*BASE|startswith\s*\(.*base_dir'),
    ".java": re.compile(r'\.normalize\(\)|\.toAbsolutePath\(\)|startsWith\s*\('),
    ".php":  re.compile(r'\brealpath\s*\(|strpos\s*\(|str_starts_with|basename\s*\('),
    ".rb":   re.compile(r'start_with\?|File\.basename|realpath'),
    ".js":   re.compile(r'path\.resolve|\.startsWith\s*\(|realpathSync|path\.normalize'),
    ".ts":   re.compile(r'path\.resolve|\.startsWith\s*\(|realpathSync|path\.normalize'),
    ".go":   re.compile(r'filepath\.Clean|strings\.HasPrefix|strings\.Contains.*"\.\."'),
}

SKIP_DIRS = {".git", "node_modules", "vendor", "__pycache__", ".venv", "venv",
             "dist", "build", "target", "test", "tests", "__tests__", "spec", "fixtures"}

def scan_file(filepath: Path) -> list[Finding]:
    suffix = filepath.suffix.lower()
    if suffix not in PATTERNS:
        return []
    try:
        lines = filepath.read_text(encoding="utf-8", errors="replace").splitlines()
    except (OSError, PermissionError):
        return []

    full_text = "\n".join(lines)
    findings: list[Finding] = []
    http_marker = HTTP_MARKERS.get(suffix)
    guard_pat = GUARD_PATTERNS.get(suffix)

    for (name, pat, base_sev, cwe, desc, fix) in PATTERNS[suffix]:
        for m in pat.finditer(full_text):
            lineno = full_text[:m.start()].count("\n") + 1
            line_text = lines[lineno - 1]

            start = max(0, lineno - 40)
            end = min(len(lines), lineno + 40)
            context = "\n".join(lines[start:end])

            has_http = bool(http_marker and http_marker.search(context))
            guard_found = bool(guard_pat and guard_pat.search(context))

            if guard_found:
                continue  # Safe pattern present — skip

            sev = base_sev
            if not has_http:
                if sev == CRITICAL:
                    sev = HIGH
                elif sev == HIGH:
                    sev = MEDIUM

            findings.append(Finding(
                file=str(filepath),
                line=lineno,
                pattern_name=name,
                matched_text=line_text.strip()[:120],
                severity=sev,
                cwe=cwe,
                description=desc,
                fix=fix,
                has_http_taint=has_http,
            ))
    return findings

def walk_files(root: Path) -> list[Path]:
    exts = {".py", ".java", ".php", ".rb", ".js", ".ts", ".go"}
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if Path(fname).suffix.lower() in exts:
                results.append(Path(dirpath) / fname)
    return results

def format_report(findings: list[Finding], scanned: int) -> str:
    by_sev = {CRITICAL: [], HIGH: [], MEDIUM: [], INFO: []}
    for f in findings:
        by_sev[f.severity].append(f)

    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "  PATH TRAVERSAL AUDIT (OWASP A01:2021 — CWE-22/98)",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"  Scanned:  {scanned} files",
        f"  Findings: {len(by_sev[CRITICAL])} CRITICAL  {len(by_sev[HIGH])} HIGH  {len(by_sev[MEDIUM])} MEDIUM",
        "",
    ]

    for sev in [CRITICAL, HIGH, MEDIUM]:
        group = by_sev[sev]
        if not group:
            continue
        lines.append(f"{ICONS[sev]} {sev} ({len(group)} findings)")
        lines.append("")
        for f in sorted(group, key=lambda x: x.file):
            rel = os.path.relpath(f.file)
            taint_str = "⚡ HTTP taint confirmed" if f.has_http_taint else "⚠️  HTTP taint unconfirmed — verify source"
            lines += [
                f"  {rel}:{f.line} — {f.pattern_name}",
                f"  Code:  {f.matched_text}",
                f"  Taint: {taint_str}",
                f"  Risk:  {f.description}",
                f"  {f.cwe}",
                f"  Fix:   {f.fix}",
                "",
            ]

    critical_count = len(by_sev[CRITICAL])
    lines += [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"  CI gate: {'exit 1 — CRITICAL findings present' if critical_count else 'exit 0 — clean'}",
        "  OWASP: https://owasp.org/Top10/A01_2021-Broken_Access_Control/",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Path traversal / LFI scanner")
    parser.add_argument("path", nargs="?", default=".", help="Root directory to scan")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--ci", action="store_true", help="Exit 1 if CRITICAL found")
    args = parser.parse_args()

    files = walk_files(Path(args.path).resolve())
    all_findings: list[Finding] = []
    for f in files:
        all_findings.extend(scan_file(f))
    all_findings.sort(key=lambda x: (SEV_ORDER[x.severity], x.file, x.line))

    if args.json:
        import dataclasses
        print(json.dumps([dataclasses.asdict(f) for f in all_findings], indent=2))
    else:
        print(format_report(all_findings, len(files)))

    if args.ci:
        sys.exit(1 if any(f.severity == CRITICAL for f in all_findings) else 0)

if __name__ == "__main__":
    main()
```

## Usage

```bash
# Scan current project
python3 audit_path_traversal.py

# Scan with CI fail-gate
python3 audit_path_traversal.py --ci

# JSON output
python3 audit_path_traversal.py --json | jq '[.[] | select(.severity == "CRITICAL")]'

# GitHub Actions
- name: Path Traversal Audit
  run: python3 .claude/skills/phy-path-traversal-audit/audit_path_traversal.py --ci
```

## Sample Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PATH TRAVERSAL AUDIT (OWASP A01:2021 — CWE-22/98)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Scanned:  54 files
  Findings: 3 CRITICAL  2 HIGH  0 MEDIUM

🔴 CRITICAL (3 findings)

  api/files.py:67 — OPEN_DIRECT
  Code:  return open(os.path.join("uploads", request.args["path"])).read()
  Taint: ⚡ HTTP taint confirmed
  Risk:  open() with user-controlled path enables arbitrary file read/write.
  CWE-22
  Fix:   safe = os.path.abspath(os.path.join("uploads", user_input))
         assert safe.startswith(os.path.abspath("uploads"))

  pages/api.php:34 — PHP_INCLUDE_INPUT
  Code:  include($_GET['page'] . '.php');
  Taint: ⚡ HTTP taint confirmed
  Risk:  PHP include with HTTP input — LFI → potential RCE via log poisoning.
  CWE-98
  Fix:   Use whitelist: $allowed = ['home', 'about'];
         if (!in_array($_GET['page'], $allowed)) die('invalid');

  src/routes/download.js:91 — FS_READFILE_PARAM
  Code:  fs.createReadStream(req.query.file)
  Taint: ⚡ HTTP taint confirmed
  Risk:  fs.createReadStream with request param — direct path traversal.
  CWE-22
  Fix:   const safe = path.resolve(BASE_DIR, req.query.file);
         if (!safe.startsWith(BASE_DIR + path.sep)) throw new Error('Forbidden');
         fs.createReadStream(safe)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CI gate: exit 1 — CRITICAL findings present
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Companion Skills

| Skill | Use Together For |
|-------|-----------------|
| `phy-ssrf-audit` | Complete input → file/URL access security sweep |
| `phy-deserialization-audit` | OWASP A08 + A01 — full untrusted input chain |
| `phy-cors-audit` | Network boundary + filesystem boundary protection |
| `phy-jwt-auth-audit` | Auth controls that should gate file access |
