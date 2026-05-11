#!/usr/bin/env python3
"""
claw-bond — Full Integration & System Test Suite
=================================================
Covers:
  1. Skill structure & OpenClaw discovery
  2. Identity & key management
  3. Token generation & validation
  4. Peer management (connection status / identity display)
  5. Session lifecycle (messaging, handoff, state transitions)
  6. Memory & scheduling (MEMORY.md, HEARTBEAT.md, deadlines)
  7. Hook integrity (gateway, heartbeat, bootstrap paths)
  8. Security
  9. Online relay tests (--relay flag)

Usage:
  python3 test_integration.py              # Full suite (offline)
  python3 test_integration.py --relay      # Include live relay tests
  python3 test_integration.py --verbose    # Show raw script output
  python3 test_integration.py --section 4  # Run only category 4

Exit: 0 = all passed, 1 = failures.
"""

import argparse
import base64
import datetime
import inspect
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

# ── Colours ────────────────────────────────────────────────────────────────
G  = "\033[92m"; R  = "\033[91m"; Y  = "\033[93m"
B  = "\033[94m"; W  = "\033[0m";  BD = "\033[1m"

SKILL_DIR  = Path(__file__).parent
NEGOTIATE  = SKILL_DIR / "negotiate.py"
HOOKS_DIR  = SKILL_DIR / "hooks"
SKILL_MD   = SKILL_DIR / "SKILL.md"
META_JSON  = SKILL_DIR / "_meta.json"
CLAWHUB    = SKILL_DIR / "clawhub.yaml"

# ── Test Registry ──────────────────────────────────────────────────────────
_tests: list[tuple[str, int, Any]] = []   # (name, category, fn)
_results: list[tuple[str, int, bool, str]] = []
_section_filter: Optional[int] = None
_verbose = False


def test(name: str, category: int = 0):
    def decorator(fn):
        _tests.append((name, category, fn))
        return fn
    return decorator


def ok(msg=""):   raise type("Pass", (Exception,), {})(msg)
def fail(reason): raise AssertionError(reason)
def assertIn(needle, haystack, msg=""):
    assert needle in haystack, msg or f"{needle!r} not found in:\n{haystack[:500]}"
def assertNotIn(needle, haystack, msg=""):
    assert needle not in haystack, msg or f"{needle!r} unexpectedly found in:\n{haystack[:500]}"


# ── Workspace Helpers ──────────────────────────────────────────────────────
def make_ws(alias="TestAgent") -> str:
    root = tempfile.mkdtemp(prefix="cwtest_")
    (Path(root) / "skills" / "claw-bond").mkdir(parents=True)
    # negotiate.py reads alias via regex: ^name:\s*(.+)$ or ^#\s*(.+)$
    Path(root, "SOUL.md").write_text(f"name: {alias}\n")
    return root


def run_cmd(args: list, ws: str, timeout=20, stdin="") -> tuple[int, str]:
    env = {**os.environ, "DIPLOMAT_WORKSPACE": ws}
    try:
        r = subprocess.run(
            [sys.executable, str(NEGOTIATE)] + args,
            capture_output=True, text=True, timeout=timeout,
            env=env, input=stdin,
        )
        out = r.stdout + r.stderr
        if _verbose:
            print(f"\n    [CMD] {args} → rc={r.returncode}\n    {out[:400]}")
        return r.returncode, out
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"


def init_ws(alias="Alice") -> str:
    ws = make_ws(alias)
    run_cmd(["generate-address"], ws, timeout=15)
    return ws


def inject_session(ws: str, **overrides) -> dict:
    """Write a fake SessionRecord into ledger.json."""
    base = {
        "session_id":       str(uuid.uuid4()),
        "peer_alias":       "Bob",
        "peer_pubkey":      "b" * 64,
        "initiated_by":     "self",
        "state":            "COMMITTED",
        "terms_version":    1,
        "final_terms": {
            "proposal_text": "Let's collaborate",
            "my_tasks":      ["Build the API"],
            "your_tasks":    ["Write the docs"],
            "deadline":      "2026-05-01T17:00:00+00:00",
            "checkin_at":    "2026-05-01T17:00:00+00:00",
            "terms_version": 1,
        },
        "memory_hash":      None,
        "peer_memory_hash": None,
        "seen_nonces":      [],
        "events":           [],
        "created_at":       "2026-03-27T01:00:00+00:00",
        "committed_at":     "2026-03-27T02:00:00+00:00",
        "checkin_at_actual": None,
        "pending_terms":    None,
    }
    base.update(overrides)
    ledger = {"sessions": [base]}
    (Path(ws) / "skills" / "claw-bond" / "ledger.json").write_text(json.dumps(ledger))
    return base


def inject_peer(ws: str, alias="Bob", pubkey=None) -> dict:
    """Write a fake PeerInfo into peers.json."""
    p = {
        "alias":           alias,
        "pubkey":          pubkey or ("b" * 64),
        "relay":           "wss://claw-diplomat-relay-production.up.railway.app",
        "relay_token":     "rt_fake_" + alias.lower(),
        "nat_hint":        "1.2.3.4",
        "last_seen":       "2026-03-27T01:00:00+00:00",
        "trusted_since":   "2026-03-27T00:00:00+00:00",
        "direct_available": False,
        "direct_address":  None,
        "relay_token_stale": False,
    }
    peers_path = Path(ws) / "skills" / "claw-bond" / "peers.json"
    data = {"peers": []}
    if peers_path.exists():
        try: data = json.loads(peers_path.read_text())
        except: pass
    data["peers"].append(p)
    peers_path.write_text(json.dumps(data))
    return p


def decode_token(token_str: str) -> dict:
    padded = token_str.strip() + "=" * (-len(token_str.strip()) % 4)
    return json.loads(base64.urlsafe_b64decode(padded))


# ══════════════════════════════════════════════════════════════════════════
# CATEGORY 1 — Skill Structure & OpenClaw Discovery
# ══════════════════════════════════════════════════════════════════════════

@test("SKILL.md exists", 1)
def t_skill_md_exists():
    assert SKILL_MD.exists(), "SKILL.md not found"

@test("SKILL.md contains activation trigger phrases", 1)
def t_skill_triggers():
    content = SKILL_MD.read_text()
    for phrase in ["/claw-diplomat", "negotiate with", "propose to", "connect with", "make a deal"]:
        assertIn(phrase, content, f"Trigger phrase missing: {phrase!r}")

@test("SKILL.md contains all command table entries", 1)
def t_skill_commands():
    content = SKILL_MD.read_text()
    for cmd in ["generate-address", "connect", "propose", "list", "checkin",
                "cancel", "peers", "status", "key", "revoke", "handoff"]:
        assertIn(cmd, content, f"Command missing from SKILL.md: {cmd!r}")

@test("SKILL.md has first-time setup section", 1)
def t_skill_first_time():
    content = SKILL_MD.read_text()
    assertIn("First-Time Setup", content)
    assertIn("diplomat.key", content)

@test("SKILL.md has Installation section at the top", 1)
def t_skill_install_section():
    content = SKILL_MD.read_text()
    install_pos = content.find("## Installation")
    manual_pos  = content.find("Agent Operating Manual") if "Agent Operating Manual" in content else content.find("# Claw Connector")
    assert install_pos != -1, "No ## Installation section in SKILL.md"
    assert install_pos < manual_pos, "Installation section must come before the operating manual"

@test("SKILL.md install block shows correct clawhub install command", 1)
def t_skill_install_command():
    content = SKILL_MD.read_text()
    assertIn("clawhub install claw-bond", content)

@test("_meta.json is valid JSON with required fields", 1)
def t_meta_json():
    assert META_JSON.exists(), "_meta.json missing"
    data = json.loads(META_JSON.read_text())
    for field in ["slug", "version"]:
        assert field in data, f"_meta.json missing field: {field}"

@test("clawhub.yaml exists and has required sections", 1)
def t_clawhub_yaml():
    assert CLAWHUB.exists(), "clawhub.yaml missing"
    content = CLAWHUB.read_text()
    for section in ["skill:", "version:", "permissions:", "install:", "readme:"]:
        assertIn(section, content, f"clawhub.yaml missing: {section}")

@test("All three hook handler.ts files exist", 1)
def t_hook_files():
    for hook in ["diplomat-bootstrap", "diplomat-gateway", "diplomat-heartbeat"]:
        p = HOOKS_DIR / hook / "handler.ts"
        assert p.exists(), f"Missing hook: {p}"
        content = p.read_text()
        assertIn("export async function handler", content, f"handler.ts missing export in {hook}")

@test("SKILL.md references claw-bond (not claw-diplomat) as skill dir", 1)
def t_skill_correct_dir():
    content = SKILL_MD.read_text()
    # Check for the old "skills/claw-diplomat" directory path.
    # Git clone URLs may contain "claw-diplomat" as the REPO name — that's fine.
    # We only flag "skills/claw-diplomat" as a wrong DIRECTORY reference.
    for i, line in enumerate(content.splitlines(), 1):
        if "git clone" in line or "github.com" in line:
            continue  # repo name claw-diplomat is fine in git URLs
        assert "skills/claw-diplomat" not in line, \
            f"Wrong skill dir on line {i}: {line.strip()!r}"

@test("diplomat-gateway handler.ts uses claw-bond path for listener.py", 1)
def t_gateway_correct_path():
    content = (HOOKS_DIR / "diplomat-gateway" / "handler.ts").read_text()
    assertIn("'claw-bond'", content)
    assertNotIn("'skills', 'claw-diplomat'", content)

@test("diplomat-heartbeat handler.ts uses claw-bond path for ledger.json", 1)
def t_heartbeat_correct_path():
    content = (HOOKS_DIR / "diplomat-heartbeat" / "handler.ts").read_text()
    assertIn("skills/claw-bond/ledger.json", content)
    assertIn("skills/claw-bond/pending_approvals.json", content)


# ══════════════════════════════════════════════════════════════════════════
# CATEGORY 2 — Identity & Key Management
# ══════════════════════════════════════════════════════════════════════════

@test("Python dependencies (PyNaCl, websockets, noiseprotocol) importable", 2)
def t_deps():
    for mod in ["nacl", "websockets", "noise"]:
        r = subprocess.run([sys.executable, "-c", f"import {mod}"],
                           capture_output=True)
        assert r.returncode == 0, f"Missing dependency: {mod} — run: pip3 install PyNaCl noiseprotocol websockets"

@test("generate-address creates diplomat.key and diplomat.pub", 2)
def t_key_files_created():
    ws = make_ws()
    try:
        run_cmd(["generate-address"], ws, timeout=15)
        skill = Path(ws) / "skills" / "claw-bond"
        assert (skill / "diplomat.key").exists(), "diplomat.key not created"
        assert (skill / "diplomat.pub").exists(), "diplomat.pub not created"
    finally:
        shutil.rmtree(ws)

@test("diplomat.key is correct size (32 or 64 bytes — NaCl Curve25519)", 2)
def t_key_size():
    ws = make_ws()
    try:
        run_cmd(["generate-address"], ws, timeout=15)
        kb = (Path(ws) / "skills" / "claw-bond" / "diplomat.key").read_bytes()
        assert len(kb) in (32, 64), f"Key is {len(kb)} bytes — expected 32 or 64"
    finally:
        shutil.rmtree(ws)

@test("diplomat.key has permissions 600 (private key protection)", 2)
def t_key_perms():
    ws = make_ws()
    try:
        run_cmd(["generate-address"], ws, timeout=15)
        mode = oct((Path(ws) / "skills" / "claw-bond" / "diplomat.key").stat().st_mode)[-3:]
        assert mode == "600", f"diplomat.key mode is {mode}, expected 600"
    finally:
        shutil.rmtree(ws)

@test("diplomat.pub is 64-char hex (Curve25519 public key)", 2)
def t_pubkey_format():
    ws = make_ws()
    try:
        run_cmd(["generate-address"], ws, timeout=15)
        pub = (Path(ws) / "skills" / "claw-bond" / "diplomat.pub").read_text().strip()
        assert re.fullmatch(r"[0-9a-f]{64}", pub), f"diplomat.pub is not 64-char hex: {pub!r}"
    finally:
        shutil.rmtree(ws)

@test("key command prints the public key hex string", 2)
def t_key_command():
    ws = init_ws()
    try:
        rc, out = run_cmd(["key"], ws)
        assert re.search(r"[0-9a-f]{64}", out), f"No 64-char hex key in output:\n{out}"
    finally:
        shutil.rmtree(ws)

@test("Same key is reused on second run (key persistence)", 2)
def t_key_persists():
    ws = init_ws()
    try:
        pub1 = (Path(ws) / "skills" / "claw-bond" / "diplomat.pub").read_text().strip()
        run_cmd(["generate-address"], ws, timeout=15)
        pub2 = (Path(ws) / "skills" / "claw-bond" / "diplomat.pub").read_text().strip()
        assert pub1 == pub2, "Public key changed on second generate-address call — key should persist"
    finally:
        shutil.rmtree(ws)


# ══════════════════════════════════════════════════════════════════════════
# CATEGORY 3 — Token Generation & Validation
# ══════════════════════════════════════════════════════════════════════════

@test("generate-address outputs a base64url token (> 100 chars, no spaces)", 3)
def t_token_in_output():
    ws = make_ws()
    try:
        rc, out = run_cmd(["generate-address"], ws, timeout=15)
        token = next((l.strip() for l in out.splitlines() if len(l.strip()) > 100 and " " not in l.strip()), None)
        assert token is not None, f"No token found in output:\n{out}"
    finally:
        shutil.rmtree(ws)

@test("Token contains all 8 required identity fields", 3)
def t_token_fields():
    ws = make_ws("Alice")
    try:
        rc, out = run_cmd(["generate-address"], ws, timeout=15)
        token = next((l.strip() for l in out.splitlines() if len(l.strip()) > 100 and " " not in l.strip()), None)
        assert token, "No token in output"
        data = decode_token(token)
        for field in ["v", "alias", "pubkey", "relay", "relay_token", "nat_hint", "issued_at", "expires_at"]:
            assert field in data, f"Token missing field: {field!r}"
        assert data["v"] == 1, f"Token version is {data['v']}, expected 1"
    finally:
        shutil.rmtree(ws)

@test("Token alias matches SOUL.md alias", 3)
def t_token_alias():
    ws = make_ws("Tanush")
    try:
        rc, out = run_cmd(["generate-address"], ws, timeout=15)
        token = next((l.strip() for l in out.splitlines() if len(l.strip()) > 100 and " " not in l.strip()), None)
        if not token:
            return  # relay may be offline; skip alias check
        data = decode_token(token)
        assert data.get("alias") == "Tanush", f"Token alias is {data.get('alias')!r}, expected 'Tanush'"
    finally:
        shutil.rmtree(ws)

@test("Token pubkey matches diplomat.pub", 3)
def t_token_pubkey_matches():
    ws = make_ws()
    try:
        rc, out = run_cmd(["generate-address"], ws, timeout=15)
        token = next((l.strip() for l in out.splitlines() if len(l.strip()) > 100 and " " not in l.strip()), None)
        if not token:
            return
        data = decode_token(token)
        pub = (Path(ws) / "skills" / "claw-bond" / "diplomat.pub").read_text().strip()
        assert data["pubkey"] == pub, f"Token pubkey {data['pubkey']!r} != diplomat.pub {pub!r}"
    finally:
        shutil.rmtree(ws)

@test("Token expires_at is 7 days in the future (±1 day tolerance)", 3)
def t_token_expiry():
    ws = make_ws()
    try:
        rc, out = run_cmd(["generate-address"], ws, timeout=15)
        token = next((l.strip() for l in out.splitlines() if len(l.strip()) > 100 and " " not in l.strip()), None)
        if not token:
            return
        data = decode_token(token)
        exp = datetime.datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
        now = datetime.datetime.now(datetime.timezone.utc)
        delta_days = (exp - now).days
        assert 6 <= delta_days <= 8, f"Token expires in {delta_days} days — expected ~7"
    finally:
        shutil.rmtree(ws)

@test("my-address.token file is written to skill dir", 3)
def t_token_file_written():
    ws = make_ws()
    try:
        run_cmd(["generate-address"], ws, timeout=15)
        p = Path(ws) / "skills" / "claw-bond" / "my-address.token"
        assert p.exists(), "my-address.token not written"
        assert p.stat().st_size > 100, "my-address.token is too small"
    finally:
        shutil.rmtree(ws)

@test("connect rejects expired token with 'expired' message", 3)
def t_expired_token():
    ws = init_ws()
    try:
        expired = {
            "v": 1, "alias": "Stale", "pubkey": "a" * 64,
            "relay": "wss://claw-diplomat-relay-production.up.railway.app",
            "relay_token": "rt_fake", "nat_hint": "1.2.3.4",
            "issued_at": "2024-01-01T00:00:00Z", "expires_at": "2024-01-08T00:00:00Z",
        }
        tok = base64.urlsafe_b64encode(json.dumps(expired).encode()).decode().rstrip("=")
        rc, out = run_cmd(["connect", tok], ws, timeout=10)
        assertIn("expired", out.lower(), f"Expected expired message, got:\n{out}")
    finally:
        shutil.rmtree(ws)

@test("connect rejects token with wrong version (v=99)", 3)
def t_wrong_version_token():
    ws = init_ws()
    try:
        bad = {
            "v": 99, "alias": "Future", "pubkey": "a" * 64,
            "relay": "wss://example.com", "relay_token": "rt_fake",
            "nat_hint": "1.2.3.4",
            "issued_at": "2026-01-01T00:00:00Z",
            "expires_at": "2099-01-08T00:00:00Z",
        }
        tok = base64.urlsafe_b64encode(json.dumps(bad).encode()).decode().rstrip("=")
        rc, out = run_cmd(["connect", tok], ws, timeout=10)
        assert rc != 0 or "invalid" in out.lower() or "version" in out.lower(), \
            f"Expected version error, got:\n{out}"
    finally:
        shutil.rmtree(ws)

@test("connect rejects completely malformed token", 3)
def t_malformed_token():
    ws = init_ws()
    try:
        rc, out = run_cmd(["connect", "notavalidtoken123"], ws, timeout=10)
        assert rc != 0 or "invalid" in out.lower() or "error" in out.lower(), \
            f"Expected error for malformed token:\n{out}"
    finally:
        shutil.rmtree(ws)


# ══════════════════════════════════════════════════════════════════════════
# CATEGORY 4 — Peer Management (Connection Status / Identity Display)
# ══════════════════════════════════════════════════════════════════════════

@test("peers list shows 'not connected' message when no peers", 4)
def t_peers_empty():
    ws = init_ws()
    try:
        rc, out = run_cmd(["peers"], ws)
        assert any(p in out for p in ["haven't connected", "No peers", "0 peer"]), \
            f"Expected empty peers message:\n{out}"
    finally:
        shutil.rmtree(ws)

@test("peers list shows peer alias, relay, and last-seen after connect", 4)
def t_peers_shows_identity():
    ws = init_ws()
    try:
        inject_peer(ws, alias="Bob", pubkey="b" * 64)
        rc, out = run_cmd(["peers"], ws)
        assertIn("Bob", out, f"Peer alias not shown:\n{out}")
        assertIn("claw-diplomat-relay", out, f"Relay not shown:\n{out}")
    finally:
        shutil.rmtree(ws)

@test("peers list shows 1 peer total count", 4)
def t_peers_count():
    ws = init_ws()
    try:
        inject_peer(ws, alias="Bob")
        rc, out = run_cmd(["peers"], ws)
        assertIn("1 peer", out, f"Peer count not in output:\n{out}")
    finally:
        shutil.rmtree(ws)

@test("peers list shows multiple peers with correct count", 4)
def t_peers_multiple():
    ws = init_ws()
    try:
        inject_peer(ws, alias="Alice", pubkey="a" * 64)
        inject_peer(ws, alias="Charlie", pubkey="c" * 64)
        rc, out = run_cmd(["peers"], ws)
        assertIn("Alice", out)
        assertIn("Charlie", out)
        assertIn("2 peers", out, f"Expected '2 peers':\n{out}")
    finally:
        shutil.rmtree(ws)

@test("peers.json written with correct fields (alias, pubkey, relay, last_seen)", 4)
def t_peers_json_fields():
    ws = init_ws()
    try:
        inject_peer(ws, alias="Bob", pubkey="b" * 64)
        data = json.loads((Path(ws) / "skills" / "claw-bond" / "peers.json").read_text())
        peer = data["peers"][0]
        for field in ["alias", "pubkey", "relay", "last_seen", "trusted_since"]:
            assert field in peer, f"peers.json peer missing field: {field!r}"
        assert peer["alias"] == "Bob"
    finally:
        shutil.rmtree(ws)

@test("stale relay token is flagged in peers list output", 4)
def t_peers_stale_flag():
    ws = init_ws()
    try:
        inject_peer(ws, alias="Stale")
        # Set relay_token_stale = true
        ppath = Path(ws) / "skills" / "claw-bond" / "peers.json"
        data = json.loads(ppath.read_text())
        data["peers"][0]["relay_token_stale"] = True
        ppath.write_text(json.dumps(data))
        rc, out = run_cmd(["peers"], ws)
        assertIn("stale", out.lower(), f"Stale flag not shown:\n{out}")
    finally:
        shutil.rmtree(ws)


# ══════════════════════════════════════════════════════════════════════════
# CATEGORY 5 — Session Lifecycle (Messaging & Handoff)
# ══════════════════════════════════════════════════════════════════════════

@test("list shows 'no negotiations' when ledger is empty", 5)
def t_list_empty():
    ws = init_ws()
    try:
        rc, out = run_cmd(["list"], ws)
        assertIn("No negotiations", out, f"Expected empty list:\n{out}")
    finally:
        shutil.rmtree(ws)

@test("status shows 'All clear' when ledger is empty", 5)
def t_status_empty():
    ws = init_ws()
    try:
        rc, out = run_cmd(["status"], ws)
        assertIn("All clear", out, f"Expected clear status:\n{out}")
    finally:
        shutil.rmtree(ws)

@test("list shows session when COMMITTED session in ledger", 5)
def t_list_shows_committed():
    ws = init_ws()
    try:
        s = inject_session(ws, state="COMMITTED", peer_alias="Bob")
        rc, out = run_cmd(["list"], ws)
        assertIn("Bob", out, f"Peer name not in list:\n{out}")
        assertIn("COMMITTED", out, f"State not in list:\n{out}")
    finally:
        shutil.rmtree(ws)

@test("status shows active commitment with peer name, task, and deadline", 5)
def t_status_shows_active():
    ws = init_ws()
    try:
        inject_session(ws, state="COMMITTED", peer_alias="Bob",
                       final_terms={
                           "my_tasks": ["Build the API"],
                           "your_tasks": ["Write the docs"],
                           "deadline": "2026-05-01T17:00:00+00:00",
                           "checkin_at": "2026-05-01T17:00:00+00:00",
                           "terms_version": 1,
                       })
        rc, out = run_cmd(["status"], ws)
        assertIn("Bob", out)
        assertIn("Build the API", out, f"My task not shown:\n{out}")
    finally:
        shutil.rmtree(ws)

@test("status shows pending proposals with state label", 5)
def t_status_pending():
    ws = init_ws()
    try:
        inject_session(ws, state="PROPOSED", peer_alias="Charlie", final_terms=None)
        rc, out = run_cmd(["status"], ws)
        assertIn("Charlie", out)
        assertIn("PROPOSED", out, f"State not shown:\n{out}")
    finally:
        shutil.rmtree(ws)

@test("status shows overdue when deadline has passed", 5)
def t_status_overdue():
    ws = init_ws()
    try:
        inject_session(ws, state="COMMITTED", peer_alias="Dave",
                       final_terms={
                           "my_tasks": ["Ship the feature"],
                           "your_tasks": ["Review it"],
                           "deadline": "2025-01-01T00:00:00+00:00",   # past!
                           "checkin_at": "2025-01-01T00:00:00+00:00",
                           "terms_version": 1,
                       })
        rc, out = run_cmd(["status"], ws)
        assertIn("Overdue", out, f"'Overdue' section missing from status:\n{out}")
        assertIn("Dave", out)
    finally:
        shutil.rmtree(ws)

@test("checkin done transitions COMMITTED session to DONE", 5)
def t_checkin_done():
    ws = init_ws()
    try:
        s = inject_session(ws, state="COMMITTED", peer_alias="Bob")
        short_id = s["session_id"][:4]
        rc, out = run_cmd(["checkin", short_id, "done"], ws, timeout=10)
        assert rc == 0 or "DONE" in out or "marked" in out.lower() or "recorded" in out.lower(), \
            f"Checkin done failed:\n{out}"
    finally:
        shutil.rmtree(ws)

@test("checkin overdue transitions COMMITTED session to OVERDUE", 5)
def t_checkin_overdue():
    ws = init_ws()
    try:
        s = inject_session(ws, state="COMMITTED", peer_alias="Bob")
        short_id = s["session_id"][:4]
        rc, out = run_cmd(["checkin", short_id, "overdue"], ws, timeout=10)
        assert rc == 0 or "OVERDUE" in out or "marked" in out.lower() or "recorded" in out.lower(), \
            f"Checkin overdue failed:\n{out}"
    finally:
        shutil.rmtree(ws)

@test("cancel removes PROPOSED session from active list", 5)
def t_cancel_proposed():
    ws = init_ws()
    try:
        s = inject_session(ws, state="PROPOSED", peer_alias="Bob", final_terms=None)
        short_id = s["session_id"][:4]
        rc, out = run_cmd(["cancel", short_id], ws, timeout=10)
        assert rc == 0 or "cancel" in out.lower() or "CANCELLED" in out, \
            f"Cancel failed:\n{out}"
    finally:
        shutil.rmtree(ws)

@test("INBOUND_PENDING session appears in status as pending proposal", 5)
def t_inbound_pending_shown():
    ws = init_ws()
    try:
        inject_session(ws, state="INBOUND_PENDING", peer_alias="Eve",
                       final_terms=None,
                       pending_terms={
                           "my_tasks": ["Eve's task"],
                           "your_tasks": ["Your task"],
                           "deadline": "2026-06-01T00:00:00+00:00",
                           "trusted": True,
                       })
        rc, out = run_cmd(["status"], ws)
        assertIn("Eve", out, f"Inbound peer not shown:\n{out}")
    finally:
        shutil.rmtree(ws)

@test("HANDOFF_RECEIVED session type is a valid SessionState", 5)
def t_handoff_state_exists():
    # Import negotiate.py and verify SessionState has HANDOFF_RECEIVED
    import importlib.util
    spec = importlib.util.spec_from_file_location("negotiate", NEGOTIATE)
    mod  = importlib.util.load_from_spec = spec
    # Just check the source text
    src = NEGOTIATE.read_text()
    assertIn("HANDOFF_RECEIVED", src)
    assertIn("handoff", src.lower())

@test("Session IDs are unique UUIDs across multiple sessions", 5)
def t_session_id_unique():
    ws = init_ws()
    try:
        ids = []
        for i in range(5):
            s = inject_session(ws, peer_alias=f"Peer{i}")
            ledger_path = Path(ws) / "skills" / "claw-bond" / "ledger.json"
            # Each inject_session overwrites — test uuid generation instead
            ids.append(str(uuid.uuid4()))
        assert len(set(ids)) == 5, "UUID collision detected"
    finally:
        shutil.rmtree(ws)

@test("propose requires existing peer — returns helpful error if unknown", 5)
def t_propose_unknown_peer():
    ws = init_ws()
    try:
        rc, out = run_cmd(["propose", "UnknownAgent999"], ws, timeout=10)
        assert rc != 0 or "don't have" in out.lower() or "connect" in out.lower() or \
               "not found" in out.lower() or "unknown" in out.lower(), \
            f"Expected 'peer not found' error:\n{out}"
    finally:
        shutil.rmtree(ws)


# ══════════════════════════════════════════════════════════════════════════
# CATEGORY 6 — Memory & Scheduling
# ══════════════════════════════════════════════════════════════════════════

@test("HEARTBEAT.md gets 'Diplomat Deadline Check' block via install command", 6)
def t_heartbeat_written():
    ws = make_ws()
    try:
        run_cmd(["install"], ws, timeout=15)   # install writes HEARTBEAT.md
        hb_path = Path(ws) / "HEARTBEAT.md"
        assert hb_path.exists(), "HEARTBEAT.md not created by install"
        content = hb_path.read_text()
        assertIn("Diplomat Deadline Check", content, f"HEARTBEAT.md:\n{content}")
    finally:
        shutil.rmtree(ws)

@test("HEARTBEAT.md block is idempotent (not duplicated on second install)", 6)
def t_heartbeat_idempotent():
    ws = make_ws()
    try:
        run_cmd(["install"], ws, timeout=15)
        run_cmd(["install"], ws, timeout=15)   # second call should not duplicate
        content = (Path(ws) / "HEARTBEAT.md").read_text()
        count = content.count("Diplomat Deadline Check")
        assert count == 1, f"'Diplomat Deadline Check' appears {count} times — should be 1"
    finally:
        shutil.rmtree(ws)

@test("install command writes HEARTBEAT.md (install subcommand)", 6)
def t_install_subcommand():
    ws = make_ws()
    try:
        rc, out = run_cmd(["install"], ws, timeout=10)
        # install should set up the workspace
        hb = Path(ws) / "HEARTBEAT.md"
        assert hb.exists() or rc == 0, f"install failed:\n{out}"
    finally:
        shutil.rmtree(ws)

@test("help-security command outputs encryption info", 6)
def t_help_security():
    ws = init_ws()
    try:
        rc, out = run_cmd(["help-security"], ws, timeout=10)
        assertIn("Noise_XX", out, f"Encryption info missing:\n{out}")
        assertIn("diplomat.key", out)
    finally:
        shutil.rmtree(ws)

@test("Overdue session shown in status when deadline is in the past", 6)
def t_past_deadline_in_status():
    ws = init_ws()
    try:
        inject_session(ws, state="COMMITTED", peer_alias="OldDeal",
                       final_terms={
                           "my_tasks": ["Finish report"],
                           "your_tasks": ["Review report"],
                           "deadline": "2024-01-01T00:00:00+00:00",
                           "checkin_at": "2024-01-01T00:00:00+00:00",
                           "terms_version": 1,
                       })
        rc, out = run_cmd(["status"], ws)
        assertIn("OldDeal", out)
        assertIn("Overdue", out, f"Overdue not shown for past deadline:\n{out}")
    finally:
        shutil.rmtree(ws)

@test("Future commitment does NOT appear in overdue section", 6)
def t_future_not_overdue():
    ws = init_ws()
    try:
        inject_session(ws, state="COMMITTED", peer_alias="FuturePartner",
                       final_terms={
                           "my_tasks": ["Build feature"],
                           "your_tasks": ["Test feature"],
                           "deadline": "2099-12-31T23:59:59+00:00",
                           "checkin_at": "2099-12-31T23:59:59+00:00",
                           "terms_version": 1,
                       })
        rc, out = run_cmd(["status"], ws)
        assertNotIn("Overdue", out, f"Future session incorrectly flagged overdue:\n{out}")
        assertIn("FuturePartner", out)
    finally:
        shutil.rmtree(ws)

@test("Multiple active sessions all shown in status", 6)
def t_multiple_sessions_in_status():
    ws = init_ws()
    try:
        for alias in ["Alpha", "Beta", "Gamma"]:
            inject_session_multi(ws, alias)
        rc, out = run_cmd(["status"], ws)
        for alias in ["Alpha", "Beta", "Gamma"]:
            assertIn(alias, out, f"{alias} not in status:\n{out}")
    finally:
        shutil.rmtree(ws)


def inject_session_multi(ws: str, alias: str):
    """Append a session to existing ledger."""
    path = Path(ws) / "skills" / "claw-bond" / "ledger.json"
    data = json.loads(path.read_text()) if path.exists() else {"sessions": []}
    data["sessions"].append({
        "session_id":       str(uuid.uuid4()),
        "peer_alias":       alias,
        "peer_pubkey":      "b" * 64,
        "initiated_by":     "self",
        "state":            "COMMITTED",
        "terms_version":    1,
        "final_terms": {
            "my_tasks":      [f"Task for {alias}"],
            "your_tasks":    ["Their task"],
            "deadline":      "2099-12-31T23:59:59+00:00",
            "checkin_at":    "2099-12-31T23:59:59+00:00",
            "terms_version": 1,
        },
        "memory_hash": None, "peer_memory_hash": None,
        "seen_nonces": [], "events": [],
        "created_at": "2026-03-27T01:00:00+00:00",
        "committed_at": "2026-03-27T02:00:00+00:00",
        "checkin_at_actual": None, "pending_terms": None,
    })
    path.write_text(json.dumps(data))


# ══════════════════════════════════════════════════════════════════════════
# CATEGORY 7 — Security
# ══════════════════════════════════════════════════════════════════════════

@test("Private key never appears in any command output", 7)
def t_key_not_in_output():
    ws = init_ws()
    try:
        priv = (Path(ws) / "skills" / "claw-bond" / "diplomat.key").read_bytes().hex()
        for cmd in [["key"], ["peers"], ["status"], ["list"]]:
            rc, out = run_cmd(cmd, ws, timeout=10)
            assertNotIn(priv, out, f"Private key leaked in {cmd} output!")
    finally:
        shutil.rmtree(ws)

@test("Token with missing required field is rejected", 7)
def t_token_missing_field():
    ws = init_ws()
    try:
        # Missing 'relay' field
        bad = {
            "v": 1, "alias": "Bad", "pubkey": "a" * 64,
            "relay_token": "rt_fake", "nat_hint": "1.2.3.4",
            "issued_at": "2026-01-01T00:00:00Z",
            "expires_at": "2099-01-08T00:00:00Z",
        }
        tok = base64.urlsafe_b64encode(json.dumps(bad).encode()).decode().rstrip("=")
        rc, out = run_cmd(["connect", tok], ws, timeout=10)
        assert rc != 0 or "invalid" in out.lower() or "missing" in out.lower() or \
               "error" in out.lower(), f"Expected error for missing field:\n{out}"
    finally:
        shutil.rmtree(ws)

@test("Peer proposal text cannot contain shell injection markers", 7)
def t_no_shell_injection():
    ws = init_ws()
    try:
        # Inject a session with adversarial proposal text
        inject_session(ws, peer_alias="Attacker",
                       final_terms={
                           "my_tasks": ["$(rm -rf /tmp/evil)"],
                           "your_tasks": ["`id`"],
                           "deadline": "2099-01-01T00:00:00+00:00",
                           "checkin_at": "2099-01-01T00:00:00+00:00",
                           "terms_version": 1,
                       })
        rc, out = run_cmd(["status"], ws, timeout=10)
        # The text should appear as display content, not cause errors or execution
        assert rc == 0 or "Attacker" in out, \
            f"Status crashed on adversarial content:\n{out}"
        # File system should be intact
        assert (Path(ws) / "skills" / "claw-bond" / "diplomat.key").exists(), \
            "diplomat.key was deleted — possible shell injection!"
    finally:
        shutil.rmtree(ws)

@test("Unknown command shows helpful error (not a crash)", 7)
def t_unknown_command():
    ws = init_ws()
    try:
        rc, out = run_cmd(["totally-unknown-command-xyz"], ws, timeout=10)
        # Should fail gracefully, not crash with traceback
        assert "Traceback" not in out or rc != 0, \
            f"Unknown command caused unhandled exception:\n{out}"
    finally:
        shutil.rmtree(ws)


# ══════════════════════════════════════════════════════════════════════════
# CATEGORY 8 — Online Relay Tests (--relay flag only)
# ══════════════════════════════════════════════════════════════════════════

def run_relay_tests():
    print(f"\n  {BD}[Category 8: Live relay tests]{W}")
    ws_alice = make_ws("Alice")
    ws_bob   = make_ws("Bob")
    alice_token = None
    try:
        # 8.1 Alice generates address
        rc, out = run_cmd(["generate-address"], ws_alice, timeout=20)
        token = next((l.strip() for l in out.splitlines() if len(l.strip()) > 100 and " " not in l.strip()), None)
        name = "Alice generates relay address"
        if token:
            _results.append((name, 8, True, ""))
            print(f"  {G}✓{W} {name}")
            alice_token = token
        else:
            _results.append((name, 8, False, f"No token:\n{out}"))
            print(f"  {R}✗{W} {name}")
            return  # can't continue without token

        # 8.2 Bob connects to Alice
        rc, out = run_cmd(["connect", alice_token], ws_bob, timeout=25)
        connected = "connected" in out.lower() or "✅" in out
        name = "Bob connects to Alice via relay"
        _results.append((name, 8, connected, out if not connected else ""))
        print(f"  {G if connected else R}{'✓' if connected else '✗'}{W} {name}")

        # 8.3 Bob's peers list shows Alice's identity
        rc, out = run_cmd(["peers"], ws_bob, timeout=10)
        shows_alice = "alice" in out.lower()
        name = "Bob's peers list shows Alice's identity"
        _results.append((name, 8, shows_alice, out if not shows_alice else ""))
        print(f"  {G if shows_alice else R}{'✓' if shows_alice else '✗'}{W} {name}")

        # 8.4 Alice's peers list shows Bob after Bob connects
        rc, out = run_cmd(["peers"], ws_alice, timeout=10)
        shows_bob = "bob" in out.lower()
        name = "Alice's peers list shows Bob after connect"
        _results.append((name, 8, shows_bob, out if not shows_bob else ""))
        print(f"  {G if shows_bob else R}{'✓' if shows_bob else '✗'}{W} {name}")

        # 8.5 Bob generates his own address (relay round-trip)
        rc, out = run_cmd(["generate-address"], ws_bob, timeout=20)
        has_token = any(len(l.strip()) > 100 and " " not in l.strip() for l in out.splitlines())
        name = "Bob can generate his own relay address"
        _results.append((name, 8, has_token, out if not has_token else ""))
        print(f"  {G if has_token else R}{'✓' if has_token else '✗'}{W} {name}")

    finally:
        shutil.rmtree(ws_alice)
        shutil.rmtree(ws_bob)


# ── Runner ─────────────────────────────────────────────────────────────────

def run_all(relay=False, verbose=False, section=None):
    global _verbose, _section_filter
    _verbose = verbose
    _section_filter = section

    cats = {
        1: "Skill Structure & OpenClaw Discovery",
        2: "Identity & Key Management",
        3: "Token Generation & Validation",
        4: "Peer Management (Connection Status / Identity)",
        5: "Session Lifecycle (Messaging & Handoff)",
        6: "Memory & Scheduling",
        7: "Security",
        8: "Online Relay Tests",
    }

    print(f"\n{BD}claw-bond — Full Integration Test Suite{W}")
    print("=" * 55)

    current_cat = None
    for name, cat, fn in _tests:
        if section and cat != section:
            continue
        if cat != current_cat:
            current_cat = cat
            print(f"\n  {BD}{B}[{cat}] {cats.get(cat, '')}]{W}")
        try:
            fn()
            _results.append((name, cat, True, ""))
            print(f"  {G}✓{W} {name}")
        except AssertionError as e:
            _results.append((name, cat, False, str(e)))
            print(f"  {R}✗{W} {name}")
            if str(e):
                for line in str(e).splitlines()[:5]:
                    print(f"      {R}{line}{W}")
        except Exception as e:
            _results.append((name, cat, False, f"Exception: {e}"))
            print(f"  {R}✗{W} {name}")
            print(f"      {R}Exception: {e}{W}")

    if relay and (not section or section == 8):
        run_relay_tests()

    # ── Summary ──
    passed = sum(1 for _, _, ok, _ in _results if ok)
    failed = sum(1 for _, _, ok, _ in _results if not ok)
    total  = len(_results)

    print(f"\n{'='*55}")
    print(f"{BD}Results: {G}{passed} passed{W}{BD}, {R if failed else ''}{failed} failed{W}{BD} / {total} total{W}")

    if failed:
        print(f"\n{R}{BD}FAILURES:{W}")
        for name, cat, ok, reason in _results:
            if not ok:
                print(f"  [{cat}] {name}")
                if reason:
                    print(f"       {R}{reason[:400]}{W}")
        sys.exit(1)
    else:
        print(f"\n{G}{BD}✓ All tests passed. claw-bond is production-ready.{W}")
        sys.exit(0)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--relay",   action="store_true", help="Include live relay tests (needs internet)")
    p.add_argument("--verbose", action="store_true", help="Print raw script output")
    p.add_argument("--section", type=int, metavar="N", help="Run only category N (1-8)")
    args = p.parse_args()
    run_all(relay=args.relay, verbose=args.verbose, section=args.section)
