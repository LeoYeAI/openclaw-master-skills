#!/usr/bin/env python3
"""
OpenClaw ↔ n8n Integration Validator (v2)

Validates:
  1. Network connectivity (n8n + Gateway health)
  2. Webhook authentication
  3. OpenClaw skill directory structure
  4. YAML frontmatter correctness
  5. Security Manifest presence in scripts
  6. Shell injection vulnerability scanning
  7. set -euo pipefail enforcement

Usage:
    python validate_integration.py --mode connectivity \
        --n8n-url http://localhost:5678 \
        --gateway-url http://localhost:18789

    python validate_integration.py --mode skill \
        --skill-dir ./openclaw-slack-send-message

    python validate_integration.py --mode all \
        --skill-dir ./openclaw-slack-send-message \
        --n8n-url http://localhost:5678
"""

# SECURITY MANIFEST:
# Environment variables accessed: N8N_URL, GATEWAY_URL, WEBHOOK_SECRET, OPENCLAW_GATEWAY_TOKEN (only)
# External endpoints called: ${N8N_URL}/healthz, ${GATEWAY_URL}/health, webhook endpoints (only)
# Local files read: SKILL.md, scripts/* within specified skill directory (only)
# Local files written: none

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def ok(msg): print(f"  {Colors.GREEN}✓{Colors.RESET} {msg}")
def fail(msg): print(f"  {Colors.RED}✗{Colors.RESET} {msg}")
def warn(msg): print(f"  {Colors.YELLOW}⚠{Colors.RESET} {msg}")
def info(msg): print(f"  {Colors.BLUE}ℹ{Colors.RESET} {msg}")
def section(title):
    print(f"\n{Colors.BOLD}{title}{Colors.RESET}")
    print("─" * 50)


def http_request(url, method="GET", headers=None, data=None, timeout=10):
    headers = headers or {}
    try:
        if data:
            data = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body, None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return e.code, body, str(e)
    except urllib.error.URLError as e:
        return None, None, str(e.reason)
    except Exception as e:
        return None, None, str(e)


# ─── Connectivity Checks ───

def check_n8n_health(n8n_url):
    section("n8n Instance Health")
    status, body, err = http_request(f"{n8n_url}/healthz")
    if status and 200 <= status < 300:
        ok(f"n8n reachable at {n8n_url}")
        return True
    elif status:
        warn(f"n8n returned HTTP {status} (may require authentication)")
        return True
    else:
        fail(f"Cannot reach n8n at {n8n_url}: {err}")
        return False


def check_gateway_health(gateway_url):
    section("OpenClaw Gateway Health")
    status, body, err = http_request(f"{gateway_url}/health")
    if status and 200 <= status < 300:
        ok(f"Gateway reachable at {gateway_url}")
        return True
    elif status:
        warn(f"Gateway returned HTTP {status}")
        return True
    else:
        fail(f"Cannot reach Gateway at {gateway_url}: {err}")
        return False


def check_webhook(n8n_url, path, secret):
    section("Webhook Authentication")
    url = f"{n8n_url}/webhook/{path}"
    headers = {"Content-Type": "application/json", "x-webhook-secret": secret}
    payload = {"action": "health_check", "payload": {"test": True}}
    status, body, err = http_request(url, "POST", headers, payload)
    if status and 200 <= status < 300:
        ok(f"Webhook {path} accepts authenticated requests")
        return True
    elif status in (401, 403):
        fail(f"Webhook authentication failed (HTTP {status})")
        return False
    elif status == 404:
        fail(f"Webhook path not found: {path} (is the workflow active?)")
        return False
    else:
        fail(f"Webhook error: HTTP {status} — {err}")
        return False


# ─── Skill Directory Validation ───

def validate_skill_directory(skill_dir):
    section("Skill Directory Structure")
    skill_path = Path(skill_dir)
    results = []

    # Check directory exists
    if not skill_path.is_dir():
        fail(f"Not a directory: {skill_dir}")
        return [False]

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        ok("SKILL.md found")
        results.append(True)
    else:
        fail("SKILL.md not found — required for OpenClaw skills")
        results.append(False)
        return results

    # Parse and validate YAML frontmatter
    results.extend(validate_yaml_frontmatter(skill_md))

    # Check for mandatory Markdown body sections
    results.extend(validate_markdown_body(skill_md))

    # Check scripts directory
    scripts_dir = skill_path / "scripts"
    if scripts_dir.is_dir():
        ok("scripts/ directory found")
        for script in scripts_dir.iterdir():
            if script.is_file():
                results.extend(validate_script(script))
    else:
        info("No scripts/ directory (skill uses inline execution only)")

    # Check for dangerous files
    results.extend(check_dangerous_files(skill_path))

    return results


def validate_yaml_frontmatter(skill_md):
    section("YAML Frontmatter Validation")
    results = []
    content = skill_md.read_text(encoding="utf-8")

    # Check frontmatter exists
    if not content.startswith("---"):
        fail("SKILL.md does not start with YAML frontmatter (---)")
        return [False]

    parts = content.split("---", 2)
    if len(parts) < 3:
        fail("YAML frontmatter not properly closed (missing second ---)")
        return [False]

    frontmatter = parts[1].strip()
    ok("YAML frontmatter delimiters present")

    # Check required fields
    required = ["name", "description"]
    for field in required:
        if re.search(rf"^{field}:", frontmatter, re.MULTILINE):
            ok(f"'{field}' field present")
            results.append(True)
        else:
            fail(f"Missing required field: '{field}'")
            results.append(False)

    # Check for correct namespace
    if "metadata.openclaw" in frontmatter or "metadata:\n  openclaw:" in frontmatter:
        fail("Uses legacy 'metadata.openclaw' namespace — use 'metadata.clawdbot' instead")
        results.append(False)

    # Check for plural envs anti-pattern
    if "requires:\n" in frontmatter or "requires:" in frontmatter:
        if "envs:" in frontmatter:
            fail("Uses 'envs' (plural) — must be 'env' (singular)")
            results.append(False)
        elif "env:" in frontmatter:
            ok("'requires.env' uses correct singular form")
            results.append(True)

    # Check files declaration
    if "files:" in frontmatter:
        ok("'files' field declared (scripts won't trigger security flag)")
        results.append(True)
    elif (skill_md.parent / "scripts").is_dir():
        fail("Has scripts/ directory but 'files' not declared in frontmatter — ClawHub will flag as suspicious")
        results.append(False)

    # Check for multi-line strings
    if "|" in frontmatter and re.search(r":\s*\|", frontmatter):
        warn("Possible YAML block scalar detected — parser expects single-line values")
    if ">" in frontmatter and re.search(r":\s*>", frontmatter):
        warn("Possible YAML folded scalar detected — parser expects single-line values")

    return results


def validate_markdown_body(skill_md):
    section("Markdown Body Transparency Sections")
    results = []
    content = skill_md.read_text(encoding="utf-8")

    # Split off frontmatter
    parts = content.split("---", 2)
    body = parts[2] if len(parts) >= 3 else ""

    mandatory_sections = [
        ("External Endpoints", "## External Endpoints"),
        ("Security & Privacy", "## Security & Privacy"),
        ("Model Invocation Note", "## Model Invocation Note"),
        ("Trust Statement", "## Trust Statement"),
    ]

    for name, marker in mandatory_sections:
        if marker.lower() in body.lower():
            ok(f"'{name}' section present")
            results.append(True)
        else:
            fail(f"Missing mandatory section: '{name}' — required for ClawHub publishing")
            results.append(False)

    # Check for Trust Statement verbatim pattern
    if "by using this skill, data is sent to" in body.lower():
        ok("Trust Statement follows required pattern")
        results.append(True)
    elif "trust statement" in body.lower():
        warn("Trust Statement section exists but may not follow verbatim pattern")

    return results


def validate_script(script_path):
    section(f"Script: {script_path.name}")
    results = []
    content = script_path.read_text(encoding="utf-8", errors="replace")

    # Check shebang
    if content.startswith("#!/"):
        ok(f"Shebang present: {content.splitlines()[0]}")
    else:
        warn("No shebang line — may not be executable")

    is_bash = "bash" in content.splitlines()[0] if content.startswith("#!") else script_path.suffix == ".sh"

    # Check set -euo pipefail (bash only)
    if is_bash:
        if "set -euo pipefail" in content:
            ok("set -euo pipefail present (strict error handling)")
            results.append(True)
        else:
            fail("Missing 'set -euo pipefail' — non-negotiable for LLM-driven execution")
            results.append(False)

    # Check Security Manifest Header
    if "SECURITY MANIFEST:" in content:
        ok("Security Manifest Header present")
        results.append(True)

        # Validate manifest fields
        manifest_fields = [
            "Environment variables accessed",
            "External endpoints called",
            "Local files read",
            "Local files written",
        ]
        for field in manifest_fields:
            if field in content:
                ok(f"  Manifest declares: {field}")
            else:
                fail(f"  Manifest missing: {field}")
                results.append(False)
    else:
        fail("Missing Security Manifest Header — required for ClawHub publishing")
        results.append(False)

    # Shell injection vulnerability scan
    injection_patterns = [
        (r'curl\s+"[^"]*\$\{[^}]+\}', "Possible shell injection: raw variable in curl URL"),
        (r'eval\s+"\$', "Dangerous: eval with variable expansion"),
        (r'echo\s+\$\{', "Possible expansion: use printf '%s' instead of echo ${}"),
    ]
    for pattern, message in injection_patterns:
        # Skip if the variable is a known safe env var
        matches = re.findall(pattern, content)
        for match in matches:
            if "N8N_WEBHOOK_URL" in match or "N8N_WEBHOOK_SECRET" in match:
                continue  # Env vars are safe (not user input)
            if "SAFE_" in match:
                continue  # Already sanitized
            warn(f"  {message}: {match[:60]}...")

    # Check for interactive prompts
    interactive_patterns = ["read -p", "read -r", "select ", "dialog "]
    for pattern in interactive_patterns:
        if pattern in content:
            fail(f"Interactive prompt detected: '{pattern}' — scripts must be headless")
            results.append(False)

    return results


def check_dangerous_files(skill_path):
    section("Dangerous File Check")
    results = []

    dangerous = [".env", ".git"]
    for name in dangerous:
        if (skill_path / name).exists():
            fail(f"'{name}' found — must be excluded from .skill package")
            results.append(False)

    # Check for symlinks
    for p in skill_path.rglob("*"):
        if p.is_symlink():
            fail(f"Symlink found: {p} — rejected by ClawHub packaging validator")
            results.append(False)

    if all(results) or not results:
        ok("No dangerous files or symlinks detected")
        results.append(True)

    return results


# ─── Main ───

def main():
    parser = argparse.ArgumentParser(description="OpenClaw ↔ n8n Integration Validator (v2)")
    parser.add_argument("--mode", choices=["connectivity", "skill", "all"], default="all")
    parser.add_argument("--n8n-url", default=os.environ.get("N8N_URL", "http://localhost:5678"))
    parser.add_argument("--gateway-url", default=os.environ.get("GATEWAY_URL", "http://localhost:18789"))
    parser.add_argument("--webhook-secret", default=os.environ.get("WEBHOOK_SECRET", ""))
    parser.add_argument("--webhook-path", default="openclaw-health-check")
    parser.add_argument("--gateway-token", default=os.environ.get("OPENCLAW_GATEWAY_TOKEN", ""))
    parser.add_argument("--skill-dir", help="Path to OpenClaw skill directory to validate")
    args = parser.parse_args()

    print(f"\n{Colors.BOLD}OpenClaw ↔ n8n Integration Validator v2{Colors.RESET}")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")

    results = []

    if args.mode in ("connectivity", "all"):
        results.append(("n8n Health", check_n8n_health(args.n8n_url)))
        if args.webhook_secret:
            results.append(("Webhook Auth", check_webhook(args.n8n_url, args.webhook_path, args.webhook_secret)))
        results.append(("Gateway Health", check_gateway_health(args.gateway_url)))

    if args.mode in ("skill", "all") and args.skill_dir:
        skill_results = validate_skill_directory(args.skill_dir)
        results.append(("Skill Structure", all(skill_results)))

    # Summary
    section("Summary")
    passed = sum(1 for _, r in results if r)
    total = len(results)
    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {status}  {name}")
    print(f"\n  {passed}/{total} checks passed")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All checks passed.{Colors.RESET}\n")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some checks failed — review above.{Colors.RESET}\n")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
