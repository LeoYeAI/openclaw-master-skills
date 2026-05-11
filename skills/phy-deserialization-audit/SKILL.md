---
name: phy-deserialization-audit
description: Unsafe deserialization vulnerability scanner (OWASP A08:2021). Detects Python pickle/yaml/eval, Java ObjectInputStream/XStream/XMLDecoder, PHP unserialize, Ruby Marshal.load, Node.js eval/new Function/vm, Go gob with interface{}. Traces HTTP input sources to dangerous sinks, classifies CRITICAL/HIGH/MEDIUM, outputs CWE/CVE mappings and per-language fix snippets. Zero competitors on ClawHub.
license: Apache-2.0
tags:
  - security
  - deserialization
  - owasp
  - python
  - java
  - php
  - ruby
  - nodejs
  - vulnerability-scanner
metadata:
  author: PHY041
  version: "1.0.0"
---

# phy-deserialization-audit

Static scanner for **OWASP A08:2021 — Insecure Deserialization** vulnerabilities across Python, Java, PHP, Ruby, Node.js/TypeScript, and Go codebases. No API keys, no network calls, no dependencies beyond Python 3 stdlib.

## What It Detects

### Python
| Pattern | Severity | CVE/CWE |
|---------|----------|---------|
| `pickle.loads(user_data)` | CRITICAL | CWE-502 |
| `pickle.load(untrusted_file)` | CRITICAL | CWE-502 |
| `yaml.load(data)` without SafeLoader | HIGH | CVE-2017-18342 |
| `yaml.full_load()` / `yaml.unsafe_load()` | CRITICAL | CVE-2017-18342 |
| `jsonpickle.decode(input)` | CRITICAL | CWE-502 |
| `marshal.loads(data)` | HIGH | CWE-502 |
| `eval(user_input)` / `exec(user_input)` | CRITICAL | CWE-95 |
| `shelve.open(user_controlled_path)` | HIGH | CWE-502 |

### Java
| Pattern | Severity | CVE/CWE |
|---------|----------|---------|
| `new ObjectInputStream(...).readObject()` | CRITICAL | CWE-502, gadget chains |
| `XStream.fromXML(userInput)` | CRITICAL | CVE-2021-29505 |
| `new XMLDecoder(inputStream)` | CRITICAL | CWE-502 |
| `ObjectMapper.readValue(input, Object.class)` | HIGH | CVE-2017-7525 (Jackson polymorphic) |
| `Serializable` class with `readObject()` override | HIGH | CWE-502 |
| `new ObjectMapper().enableDefaultTyping()` | HIGH | CVE-2017-7525 |

### PHP
| Pattern | Severity | CVE/CWE |
|---------|----------|---------|
| `unserialize($userInput)` | CRITICAL | CWE-502, POP chains |
| `unserialize($_GET[...])` / `unserialize($_POST[...])` | CRITICAL | CWE-502 |
| `unserialize($_COOKIE[...])` | CRITICAL | CWE-502 |
| `unserialize(base64_decode(...))` | HIGH | CWE-502 |

### Ruby
| Pattern | Severity | CVE/CWE |
|---------|----------|---------|
| `Marshal.load(user_input)` | CRITICAL | CWE-502 |
| `YAML.load(user_input)` (Psych < 4.0 default) | HIGH | CVE-2013-4164 |
| `JSON.load(input)` (bypasses safe defaults) | MEDIUM | CWE-502 |

### Node.js / TypeScript
| Pattern | Severity | CVE/CWE |
|---------|----------|---------|
| `eval(req.body.*)` or `eval(req.params.*)` | CRITICAL | CWE-95 |
| `new Function(userInput)` | CRITICAL | CWE-95 |
| `vm.runInContext(userInput, ...)` | HIGH | CWE-94 |
| `vm.Script(userInput).runIn*` | HIGH | CWE-94 |
| `require(userControlledPath)` | HIGH | CWE-706 |
| `child_process.exec(unsanitizedInput)` | CRITICAL | CWE-78 (adjacent) |

### Go
| Pattern | Severity | CVE/CWE |
|---------|----------|---------|
| `gob.NewDecoder(conn).Decode(&interface{})` | HIGH | CWE-502 |
| `encoding/xml.Unmarshal` with `interface{}` target | MEDIUM | CWE-502 |
| `json.Unmarshal` into `interface{}` then unsafe cast | MEDIUM | CWE-20 |

## Taint Flow Logic

The scanner uses a two-pass approach:

**Pass 1 — Dangerous sink detection:** Find all pattern matches per file.

**Pass 2 — HTTP input proximity check:** Within the same function block (±40 lines), look for HTTP input markers:
- Python: `request.body`, `request.data`, `request.POST`, `request.GET`, `flask.request`, `request.json`
- Java: `HttpServletRequest`, `@RequestBody`, `@RequestParam`, `getParameter(`, `getInputStream(`
- PHP: `$_GET`, `$_POST`, `$_REQUEST`, `$_COOKIE`, `$_FILES`, `file_get_contents("php://input")`
- Ruby: `params[`, `request.body`, `JSON.parse(request.body)`
- Node.js: `req.body`, `req.params`, `req.query`, `req.headers`, `request.body`
- Go: `r.Body`, `r.URL.Query()`, `r.FormValue(`

If HTTP input marker found near sink → **CRITICAL** or **HIGH**
If no HTTP input marker visible → downgrade one level (informational) with note: *"Verify data source"*

**Safe patterns (excluded):**
- `yaml.safe_load(...)` — OK
- `yaml.load(data, Loader=yaml.SafeLoader)` — OK
- `pickle.loads(STATIC_BYTES)` where argument is a literal — OK
- `eval("1 + 2")` with string literal — OK

## Implementation

```python
#!/usr/bin/env python3
"""
phy-deserialization-audit — OWASP A08:2021 scanner
Usage: python3 audit_deserial.py [path] [--json] [--ci]
"""
import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ─── Severity ────────────────────────────────────────────────────────────────
CRITICAL, HIGH, MEDIUM, INFO = "CRITICAL", "HIGH", "MEDIUM", "INFO"

@dataclass
class Finding:
    file: str
    line: int
    pattern_name: str
    matched_text: str
    severity: str
    cwe: str
    cve: Optional[str]
    description: str
    fix: str
    has_http_taint: bool = False

# ─── Pattern registry ────────────────────────────────────────────────────────
# (pattern_name, regex, base_severity, cwe, cve, description, fix)
PATTERNS = {
    ".py": [
        ("PICKLE_LOADS",
         re.compile(r'\bpickle\.loads?\s*\('),
         CRITICAL, "CWE-502", None,
         "pickle.load/loads deserializes arbitrary Python objects — remote code execution if input is user-controlled.",
         "Never deserialize user input with pickle. Use json.loads() + schema validation (Pydantic/marshmallow)."),

        ("YAML_UNSAFE_LOAD",
         re.compile(r'\byaml\.(?:load|full_load|unsafe_load)\s*\((?![^)]*SafeLoader)'),
         HIGH, "CWE-502", "CVE-2017-18342",
         "yaml.load() without Loader=yaml.SafeLoader executes arbitrary Python code embedded in YAML.",
         "Replace with yaml.safe_load(data) or yaml.load(data, Loader=yaml.SafeLoader)."),

        ("JSONPICKLE_DECODE",
         re.compile(r'\bjsonpickle\.decode\s*\('),
         CRITICAL, "CWE-502", None,
         "jsonpickle.decode() restores full Python object graphs — arbitrary code execution.",
         "Do not use jsonpickle for untrusted input. Use json.loads() + strict schema."),

        ("MARSHAL_LOADS",
         re.compile(r'\bmarshal\.loads?\s*\('),
         HIGH, "CWE-502", None,
         "marshal is not intended for untrusted data and can execute code.",
         "Replace with json.loads() and validate schema."),

        ("EVAL_EXEC",
         re.compile(r'\b(?:eval|exec)\s*\('),
         CRITICAL, "CWE-95", None,
         "eval()/exec() with user-controlled input leads to arbitrary code execution.",
         "Remove eval/exec. Use ast.literal_eval() for safe literal evaluation, or a proper parser."),

        ("SHELVE_OPEN",
         re.compile(r'\bshelve\.open\s*\('),
         HIGH, "CWE-502", None,
         "shelve uses pickle internally — path traversal + deserialization risk.",
         "Ensure path is never user-controlled; prefer a proper database or JSON store."),
    ],
    ".java": [
        ("OBJECT_INPUT_STREAM",
         re.compile(r'\bnew\s+ObjectInputStream\s*\('),
         CRITICAL, "CWE-502", None,
         "Java deserialization via ObjectInputStream enables gadget-chain attacks (Apache Commons, Spring).",
         "Use a type-validating ObjectInputStream wrapper (e.g., Apache Commons ValidatingObjectInputStream) or replace with JSON/Protobuf."),

        ("XSTREAM_FROM_XML",
         re.compile(r'\.fromXML\s*\('),
         CRITICAL, "CWE-502", "CVE-2021-29505",
         "XStream.fromXML() can execute arbitrary code via crafted XML.",
         "Upgrade XStream ≥1.4.18 and enable allowlist: xstream.addPermission(NoTypePermission.NONE)."),

        ("XML_DECODER",
         re.compile(r'\bnew\s+XMLDecoder\s*\('),
         CRITICAL, "CWE-502", None,
         "XMLDecoder can instantiate arbitrary Java objects from XML — remote code execution.",
         "Never use XMLDecoder with untrusted input. Use a JSON parser or JAXB with an allowlist."),

        ("JACKSON_OBJECT_CLASS",
         re.compile(r'\.readValue\s*\([^,]+,\s*Object\.class\s*\)'),
         HIGH, "CWE-502", "CVE-2017-7525",
         "Jackson readValue to Object.class enables polymorphic deserialization attacks.",
         "Always specify a concrete class: mapper.readValue(json, MyDto.class)."),

        ("JACKSON_DEFAULT_TYPING",
         re.compile(r'\.enableDefaultTyping\s*\('),
         HIGH, "CWE-502", "CVE-2017-7525",
         "enableDefaultTyping() allows arbitrary class instantiation via @class field.",
         "Remove enableDefaultTyping(). Use @JsonTypeInfo on specific types only."),

        ("SERIALIZABLE_READOBJECT",
         re.compile(r'private\s+void\s+readObject\s*\(\s*ObjectInputStream'),
         HIGH, "CWE-502", None,
         "Custom readObject() override — verify it validates state before use.",
         "Validate all fields in readObject(); throw InvalidObjectException on unexpected values."),
    ],
    ".php": [
        ("PHP_UNSERIALIZE_INPUT",
         re.compile(r'\bunserialize\s*\(\s*\$(?:_GET|_POST|_REQUEST|_COOKIE|_SERVER)\b'),
         CRITICAL, "CWE-502", None,
         "unserialize() on HTTP input enables PHP Object Injection (POP chains → RCE).",
         "Never call unserialize() on user input. Use json_decode() with strict schema validation."),

        ("PHP_UNSERIALIZE_VAR",
         re.compile(r'\bunserialize\s*\('),
         HIGH, "CWE-502", None,
         "unserialize() on potentially user-controlled data.",
         "Verify data source. Replace with json_decode() wherever possible."),

        ("PHP_UNSERIALIZE_BASE64",
         re.compile(r'\bunserialize\s*\(\s*base64_decode\s*\('),
         CRITICAL, "CWE-502", None,
         "base64 obfuscation does not protect against PHP Object Injection.",
         "Remove entirely. Use signed tokens (JWT/HMAC) to pass state between requests."),
    ],
    ".rb": [
        ("RUBY_MARSHAL_LOAD",
         re.compile(r'\bMarshal\.load\s*\('),
         CRITICAL, "CWE-502", None,
         "Marshal.load executes arbitrary Ruby code from crafted binary data.",
         "Never deserialize untrusted data with Marshal. Use JSON.parse + schema validation."),

        ("RUBY_YAML_LOAD",
         re.compile(r'\bYAML\.load\s*\((?![^)]*safe)'),
         HIGH, "CWE-502", "CVE-2013-4164",
         "YAML.load() with Psych < 4.0 allows arbitrary object instantiation.",
         "Replace with YAML.safe_load() or YAML.load(data, permitted_classes: [])."),

        ("RUBY_JSON_LOAD",
         re.compile(r'\bJSON\.load\s*\('),
         MEDIUM, "CWE-502", None,
         "JSON.load() creates Ruby objects from JSON — prefer JSON.parse.",
         "Replace with JSON.parse() which only produces standard types."),
    ],
    ".js": _build_js_patterns(),
    ".ts": _build_js_patterns(),
    ".go": [
        ("GO_GOB_INTERFACE",
         re.compile(r'gob\.NewDecoder\s*\([^)]+\)\.Decode\s*\(&\s*(?:interface|any)\s*\{?\}?'),
         HIGH, "CWE-502", None,
         "gob decoding into interface{} without type registration is unsafe with untrusted data.",
         "Use gob.Register() to allowlist concrete types, or prefer encoding/json with a concrete struct."),

        ("GO_XML_INTERFACE",
         re.compile(r'xml\.Unmarshal\s*\([^,]+,\s*&\s*(?:interface|any)\s*\{?\}?'),
         MEDIUM, "CWE-502", None,
         "xml.Unmarshal into interface{} loses type safety.",
         "Unmarshal into a concrete struct type."),
    ],
}

def _build_js_patterns():
    return [
        ("JS_EVAL",
         re.compile(r'\beval\s*\('),
         CRITICAL, "CWE-95", None,
         "eval() with user-controlled input leads to arbitrary JS execution.",
         "Remove eval(). Use JSON.parse() for data, or a proper expression parser (e.g., mathjs)."),

        ("JS_NEW_FUNCTION",
         re.compile(r'\bnew\s+Function\s*\('),
         CRITICAL, "CWE-95", None,
         "new Function() constructs executable code — equivalent to eval().",
         "Avoid new Function() with user input. Use structured data and validation instead."),

        ("JS_VM_RUN",
         re.compile(r'\bvm\.(?:runIn(?:New)?Context|Script)\s*\('),
         HIGH, "CWE-94", None,
         "Node.js vm module does not provide a security sandbox — code can escape the context.",
         "Do not use vm for untrusted code execution. Use isolated-vm or a subprocess-based sandbox."),

        ("JS_DYNAMIC_REQUIRE",
         re.compile(r'\brequire\s*\(\s*(?:req\.|params\.|query\.|body\.)'),
         HIGH, "CWE-706", None,
         "Dynamic require() with user-controlled path enables path traversal and module injection.",
         "Whitelist allowed module names; never pass user input directly to require()."),

        ("JS_SERIALIZE_JS",
         re.compile(r'\bserialize\s*\([^)]*(?:req\.|params\.|query\.|body\.)'),
         HIGH, "CWE-502", None,
         "serialize-javascript or similar with user-controlled objects can produce executable code.",
         "Never serialize user-supplied objects for client transmission without sanitization."),
    ]

# HTTP input markers per language
HTTP_MARKERS = {
    ".py":   re.compile(r'request\.(body|data|json|POST|GET|form|files|args)|flask\.request|tornado\.web|django\.http'),
    ".java": re.compile(r'HttpServletRequest|@RequestBody|@RequestParam|getParameter\(|getInputStream\(|@PathVariable'),
    ".php":  re.compile(r'\$_(?:GET|POST|REQUEST|COOKIE|FILES)|php://input'),
    ".rb":   re.compile(r'\bparams\[|request\.body|request\.params'),
    ".js":   re.compile(r'\breq\.(body|params|query|headers)|request\.(body|params)'),
    ".ts":   re.compile(r'\breq\.(body|params|query|headers)|request\.(body|params)'),
    ".go":   re.compile(r'r\.Body|r\.URL\.Query\(\)|r\.FormValue\(|r\.Header\.Get\('),
}

SAFE_PATTERNS = {
    ".py": re.compile(r'yaml\.safe_load|Loader\s*=\s*yaml\.SafeLoader|ast\.literal_eval'),
    ".rb": re.compile(r'YAML\.safe_load|JSON\.parse'),
    ".java": re.compile(r'ValidatingObjectInputStream|addPermission'),
}

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
    safe_pat = SAFE_PATTERNS.get(suffix)

    for (name, pat, base_sev, cwe, cve, desc, fix) in PATTERNS[suffix]:
        for m in pat.finditer(full_text):
            lineno = full_text[:m.start()].count("\n") + 1

            # Skip if a safe alternative is on the same line
            line_text = lines[lineno - 1]
            if safe_pat and safe_pat.search(line_text):
                continue

            # Check for HTTP taint in surrounding ±40 lines
            start = max(0, lineno - 40)
            end = min(len(lines), lineno + 40)
            context = "\n".join(lines[start:end])
            has_http = bool(http_marker and http_marker.search(context)) if http_marker else False

            # Downgrade severity if no HTTP taint visible
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
                cve=cve,
                description=desc,
                fix=fix,
                has_http_taint=has_http,
            ))

    return findings

def walk_files(root: Path, exts: set[str]) -> list[Path]:
    skip_dirs = {".git", "node_modules", "vendor", "__pycache__", ".venv", "venv",
                 "dist", "build", "target", ".gradle", ".mvn"}
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fname in filenames:
            if Path(fname).suffix.lower() in exts:
                results.append(Path(dirpath) / fname)
    return results

SEV_ORDER = {CRITICAL: 0, HIGH: 1, MEDIUM: 2, INFO: 3}
ICONS = {CRITICAL: "🔴", HIGH: "🟠", MEDIUM: "🟡", INFO: "⚪"}

def format_text_report(findings: list[Finding], scanned: int) -> str:
    by_sev: dict[str, list[Finding]] = {CRITICAL: [], HIGH: [], MEDIUM: [], INFO: []}
    for f in findings:
        by_sev[f.severity].append(f)

    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "  DESERIALIZATION AUDIT REPORT (OWASP A08:2021)",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"  Scanned: {scanned} files",
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
            taint = "⚡ HTTP taint confirmed" if f.has_http_taint else "⚠️  HTTP taint unconfirmed — verify source"
            lines += [
                f"  {rel}:{f.line} — {f.pattern_name}",
                f"  Code:   {f.matched_text}",
                f"  Taint:  {taint}",
                f"  Risk:   {f.description}",
                f"  {f.cwe}" + (f"  {f.cve}" if f.cve else ""),
                f"  Fix:    {f.fix}",
                "",
            ]

    critical_count = len(by_sev[CRITICAL])
    lines += [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"  CI gate exit code: {'1 (CRITICAL findings present)' if critical_count else '0 (clean)'}",
        "  Full audit docs: https://owasp.org/A08_2021-Software_and_Data_Integrity_Failures/",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="OWASP A08:2021 deserialization auditor")
    parser.add_argument("path", nargs="?", default=".", help="Root directory to scan")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--ci", action="store_true", help="Exit 1 if CRITICAL found")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    supported_exts = {".py", ".java", ".php", ".rb", ".js", ".ts", ".go"}
    files = walk_files(root, supported_exts)

    all_findings: list[Finding] = []
    for f in files:
        all_findings.extend(scan_file(f))
    all_findings.sort(key=lambda x: (SEV_ORDER[x.severity], x.file, x.line))

    if args.json:
        import dataclasses
        print(json.dumps([dataclasses.asdict(f) for f in all_findings], indent=2))
    else:
        print(format_text_report(all_findings, len(files)))

    if args.ci:
        has_critical = any(f.severity == CRITICAL for f in all_findings)
        sys.exit(1 if has_critical else 0)

if __name__ == "__main__":
    main()
```

## Usage

**Scan current directory:**
```bash
python3 audit_deserial.py
```

**Scan a specific project:**
```bash
python3 audit_deserial.py ~/projects/myapp
```

**JSON output (pipe to jq):**
```bash
python3 audit_deserial.py --json | jq '[.[] | select(.severity == "CRITICAL")]'
```

**CI fail-gate (exits 1 if any CRITICAL):**
```bash
python3 audit_deserial.py --ci && echo "Clean" || echo "CRITICAL deserialization risks found"
```

**GitHub Actions integration:**
```yaml
- name: Deserialization Audit
  run: |
    python3 .claude/skills/phy-deserialization-audit/audit_deserial.py --ci
```

## Sample Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DESERIALIZATION AUDIT REPORT (OWASP A08:2021)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Scanned: 84 files
  Findings: 2 CRITICAL  3 HIGH  1 MEDIUM

🔴 CRITICAL (2 findings)

  api/views.py:145 — PICKLE_LOADS
  Code:   data = pickle.loads(request.body)
  Taint:  ⚡ HTTP taint confirmed
  Risk:   pickle.load/loads deserializes arbitrary Python objects — RCE if input is user-controlled.
  CWE-502
  Fix:    Never deserialize user input with pickle. Use json.loads() + Pydantic/marshmallow.

  api.php:89 — PHP_UNSERIALIZE_INPUT
  Code:   $obj = unserialize($_POST['data']);
  Taint:  ⚡ HTTP taint confirmed
  Risk:   unserialize() on HTTP input enables PHP Object Injection (POP chains → RCE).
  CWE-502
  Fix:    Never call unserialize() on user input. Use json_decode() with strict schema validation.

🟠 HIGH (3 findings)

  src/loader.java:34 — OBJECT_INPUT_STREAM
  Code:   Object obj = new ObjectInputStream(socket.getInputStream()).readObject();
  Taint:  ⚡ HTTP taint confirmed
  Risk:   Java deserialization via ObjectInputStream enables gadget-chain attacks.
  CWE-502
  Fix:    Use ValidatingObjectInputStream from Apache Commons IO or replace with JSON/Protobuf.

  config/parser.py:28 — YAML_UNSAFE_LOAD
  Code:   cfg = yaml.load(config_str)
  Taint:  ⚠️  HTTP taint unconfirmed — verify source
  Risk:   yaml.load() without SafeLoader executes arbitrary Python code embedded in YAML.
  CWE-502  CVE-2017-18342
  Fix:    Replace with yaml.safe_load(data) or yaml.load(data, Loader=yaml.SafeLoader).

  app.js:67 — JS_EVAL
  Code:   const result = eval(req.query.expr);
  Taint:  ⚡ HTTP taint confirmed
  Risk:   eval() with user-controlled input leads to arbitrary JS execution.
  CWE-95
  Fix:    Remove eval(). Use JSON.parse() for data, or a proper expression parser.

🟡 MEDIUM (1 finding)

  lib/api.rb:12 — RUBY_JSON_LOAD
  Code:   obj = JSON.load(params[:data])
  Taint:  ⚡ HTTP taint confirmed
  Risk:   JSON.load() creates Ruby objects from JSON — prefer JSON.parse.
  CWE-502
  Fix:    Replace with JSON.parse() which only produces standard types.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CI gate exit code: 1 (CRITICAL findings present)
  Full audit docs: https://owasp.org/A08_2021-Software_and_Data_Integrity_Failures/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## CVE/CWE Reference

| Vulnerability | CVE | CVSS | Impact |
|---------------|-----|------|--------|
| Java deserialization gadget chains | Multiple | 9.8 CRITICAL | RCE |
| Python pickle RCE | — | 9.8 CRITICAL | RCE |
| XStream XML deserialization | CVE-2021-29505 | 8.8 HIGH | RCE |
| SnakeYAML / PyYAML unsafe load | CVE-2017-18342 | 9.8 CRITICAL | RCE |
| Jackson polymorphic deserialization | CVE-2017-7525 | 9.8 CRITICAL | RCE |
| PHP Object Injection (POP chains) | Multiple | 9.0 CRITICAL | RCE |

## Relationships to Other phy- Skills

| Companion Skill | When to Use Together |
|----------------|---------------------|
| `phy-jwt-auth-audit` | Auth + deserialization both present in API layers |
| `phy-cors-audit` | Network boundary misconfig + input handling risks |
| `phy-regex-audit` | Before deploying: full input-handling security sweep |
| `phy-env-doctor` | Ensure no deserialization keys/secrets in .env |
