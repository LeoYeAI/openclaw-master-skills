#!/usr/bin/env python3
"""
multi-agent-workshop Orchestrator (Plan B Lite)

阶段机 + 门禁 + SQLite 持久化。替代 Markdown grep 校验，
硬性阻塞不满足前置条件的阶段跳转。

用法:
  python3 orchestrator.py init <session_id> [--deliverable-type TYPE]
  python3 orchestrator.py status <session_id>
  python3 orchestrator.py advance <session_id>          # 推进到下一阶段（检查门禁）
  python3 orchestrator.py set-phase <session_id> <phase> # 跳转（检查门禁）
  python3 orchestrator.py gate <session_id> [phase]      # 检查某阶段门禁是否通过
  python3 orchestrator.py set <session_id> <field> <value>  # 设置字段
  python3 orchestrator.py history <session_id>           # 阶段变更历史
  python3 orchestrator.py list                           # 列出所有 session
  python3 orchestrator.py import <session_id>            # 从现有 workshops/<id>/state.md 导入
  python3 orchestrator.py validate <session_id>          # 全量校验
  python3 orchestrator.py cleanup                        # 清理 OpenClaw 残留 subagent
  python3 orchestrator.py sync <session_id>              # 将 DB 状态回写到 state.md

依赖: Python 3.8+, 无第三方包
"""

import argparse
import json
import os
import re
import shutil
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORKSPACE_ROOT = SKILL_DIR.parent.parent
WORKSHOPS_DIR = WORKSPACE_ROOT / "workshops"
DB_PATH = SKILL_DIR / "data" / "orchestrator.db"

# ─── Phase definitions ───────────────────────────────────────────────

PHASES = [
    "phase_0_intake",
    "phase_1_understanding",
    "phase_2_roles",
    "phase_3_role_cards",
    "phase_4_discussion",
    "phase_5_plan",
    "awaiting_approval",
    "phase_6_execution",
]

PHASE_LABELS = {
    "phase_0_intake": "0 任务澄清",
    "phase_1_understanding": "1 任务理解",
    "phase_2_roles": "2 角色拆解",
    "phase_3_role_cards": "3 角色创建",
    "phase_4_discussion": "4 任务讨论",
    "phase_5_plan": "5 plan 起草",
    "awaiting_approval": "5+ 待批准",
    "phase_6_execution": "6 plan 执行",
}

PHASE_FROM_NUM = {
    "0": "phase_0_intake",
    "1": "phase_1_understanding",
    "2": "phase_2_roles",
    "3": "phase_3_role_cards",
    "4": "phase_4_discussion",
    "5": "phase_5_plan",
    "6": "phase_6_execution",
    "awaiting": "awaiting_approval",
    "wait": "awaiting_approval",
    "approval": "awaiting_approval",
}

DELIVERABLE_TYPES = ["methodology", "artifact", "outline_sample", "review", "mixed"]

SESSION_STATUSES = ["open", "completed", "stopped", "cancelled"]

# ─── Gate definitions ────────────────────────────────────────────────
# Each gate checks required fields before allowing entry to target phase.
# Returns (passed: bool, reason: str)

def _gate_to_phase1(db, sid):
    s = _get_session(db, sid)
    if not s["deliverable_type"]:
        return False, "阶段 0 未完成：缺少 deliverable_type（期望交付物类型）"
    if not s["success_criteria"]:
        return False, "阶段 0 未完成：缺少 success_criteria（成功标准）"
    return True, "OK"

def _gate_to_phase2(db, sid):
    s = _get_session(db, sid)
    if not s["raw_requirement"]:
        return False, "阶段 1 未完成：缺少 raw_requirement（原始需求）"
    return True, "OK"

def _gate_to_phase3(db, sid):
    s = _get_session(db, sid)
    if not s["task_type_tag"]:
        return False, "阶段 2 未完成：缺少 task_type_tag（任务类型标签）"
    if not s["role_rationale"]:
        return False, "阶段 2 未完成：缺少 role_rationale（选角理由）"
    roles = _get_roles(db, sid)
    if len(roles) < 1:
        return False, "阶段 2 未完成：至少需要 1 个角色（用 set-role 添加）"
    return True, "OK"

def _resolve_card_path(sid, card_path):
    """Try to locate the card file relative to workshop, workspace, or skill dir."""
    for base in (WORKSHOPS_DIR / sid, WORKSPACE_ROOT, SKILL_DIR):
        candidate = base / card_path
        if candidate.exists():
            return candidate
    return None


def _validate_card_content(text, role_name):
    """Check card content for required task-binding marker."""
    if "针对任务" not in text[:500]:
        return (
            f"角色「{role_name}」角色卡缺少「针对任务：…」绑定"
            f"（首 500 字未出现；见 references/role-card-skeleton.md）"
        )
    return None


def _gate_to_phase4(db, sid):
    roles = _get_roles(db, sid)
    for r in roles:
        if not r["card_path"] and not r["card_inline"]:
            return False, f"阶段 3 未完成：角色「{r['name']}」缺少角色卡（card_path 或 card_inline）"
        content = None
        if r["card_path"]:
            resolved = _resolve_card_path(sid, r["card_path"])
            if not resolved:
                return False, f"阶段 3 未完成：角色「{r['name']}」的 card_path 文件不存在：{r['card_path']}"
            content = resolved.read_text(encoding="utf-8")
        elif r["card_inline"]:
            content = r["card_inline"]
        if content is not None:
            err = _validate_card_content(content, r["name"])
            if err:
                return False, f"阶段 3 未完成：{err}"
    return True, "OK"

def _gate_to_phase5(db, sid):
    msgs = _get_messages(db, sid, phase="phase_4_discussion")
    if len(msgs) < 1:
        return False, "阶段 4 未完成：无讨论记录（至少需要 1 条 phase_4 消息）"
    return True, "OK"

def _gate_to_awaiting(db, sid):
    s = _get_session(db, sid)
    plan_path = WORKSHOPS_DIR / sid / "plan.md"
    if not plan_path.exists() and not s.get("plan_version"):
        return False, "阶段 5 未完成：plan.md 不存在且 plan_version 未设置"
    return True, "OK"

def _gate_to_phase6(db, sid):
    s = _get_session(db, sid)
    if s["current_phase"] != "awaiting_approval":
        return False, "须先经过 awaiting_approval（用户确认后才能进入阶段 6）"
    if not s["approved_at"]:
        return False, "用户尚未确认 plan（缺少 approved_at）"
    return True, "OK"

GATES = {
    "phase_1_understanding": _gate_to_phase1,
    "phase_2_roles": _gate_to_phase2,
    "phase_3_role_cards": _gate_to_phase3,
    "phase_4_discussion": _gate_to_phase4,
    "phase_5_plan": _gate_to_phase5,
    "awaiting_approval": _gate_to_awaiting,
    "phase_6_execution": _gate_to_phase6,
}

# ─── Database ────────────────────────────────────────────────────────

def _init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript("""
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        current_phase TEXT NOT NULL DEFAULT 'phase_0_intake',
        session_status TEXT NOT NULL DEFAULT 'open',
        deliverable_type TEXT,
        non_goals TEXT,
        success_criteria TEXT,
        raw_requirement TEXT,
        task_type_tag TEXT,
        role_rationale TEXT,
        forcing_questions_note TEXT,
        plan_version INTEGER,
        plan_template TEXT,
        approved_at TEXT,
        approved_by TEXT,
        mode TEXT,
        compression_note TEXT,
        ended_at TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL REFERENCES sessions(id),
        name TEXT NOT NULL,
        responsibility TEXT,
        tension_point TEXT,
        card_path TEXT,
        card_inline TEXT,
        UNIQUE(session_id, name)
    );
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL REFERENCES sessions(id),
        phase TEXT NOT NULL,
        role TEXT,
        round TEXT,
        content TEXT,
        summary TEXT,
        completed TEXT DEFAULT 'unknown',
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS phase_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL REFERENCES sessions(id),
        from_phase TEXT,
        to_phase TEXT NOT NULL,
        gate_result TEXT,
        created_at TEXT NOT NULL
    );
    """)
    return db


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _get_session(db, sid):
    row = db.execute("SELECT * FROM sessions WHERE id = ?", (sid,)).fetchone()
    if not row:
        _die(f"Session 不存在: {sid}")
    return dict(row)


def _get_roles(db, sid):
    rows = db.execute("SELECT * FROM roles WHERE session_id = ? ORDER BY id", (sid,)).fetchall()
    return [dict(r) for r in rows]


def _get_messages(db, sid, phase=None):
    if phase:
        rows = db.execute(
            "SELECT * FROM messages WHERE session_id = ? AND phase = ? ORDER BY id",
            (sid, phase)
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM messages WHERE session_id = ? ORDER BY id",
            (sid,)
        ).fetchall()
    return [dict(r) for r in rows]

# ─── Helpers ─────────────────────────────────────────────────────────

def _die(msg):
    print(f"✗ {msg}", file=sys.stderr)
    sys.exit(1)


def _check_gate(db, sid, target_phase):
    gate_fn = GATES.get(target_phase)
    if not gate_fn:
        return True, "无门禁"
    return gate_fn(db, sid)


def _patch_state_md(path: Path, sid: str, deliverable_type: Optional[str] = None):
    """Replace placeholders in a freshly copied state.md template."""
    text = path.read_text(encoding="utf-8")
    text = text.replace("〈标题〉", sid, 1)
    text = re.sub(
        r"(- \*\*Session ID\*\*:\s*)YYYY-MM-DD_〈简写〉",
        r"\g<1>" + sid,
        text, count=1,
    )
    if deliverable_type:
        text = re.sub(
            r"\[ \]\s*\*\*`" + re.escape(deliverable_type) + r"`\*\*",
            f"[x] **`{deliverable_type}`**",
            text, count=1,
        )
    path.write_text(text, encoding="utf-8")


def _record_transition(db, sid, from_phase, to_phase, gate_result):
    db.execute(
        "INSERT INTO phase_history (session_id, from_phase, to_phase, gate_result, created_at) VALUES (?,?,?,?,?)",
        (sid, from_phase, to_phase, gate_result, _now())
    )

# ─── Commands ────────────────────────────────────────────────────────

def cmd_init(args):
    db = _init_db()
    sid = args.session_id
    existing = db.execute("SELECT id FROM sessions WHERE id = ?", (sid,)).fetchone()
    if existing:
        _die(f"Session 已存在: {sid}")

    now = _now()
    db.execute(
        "INSERT INTO sessions (id, deliverable_type, created_at, updated_at) VALUES (?,?,?,?)",
        (sid, args.deliverable_type, now, now)
    )
    _record_transition(db, sid, None, "phase_0_intake", "初始化")
    db.commit()

    ws_dir = WORKSHOPS_DIR / sid
    ws_dir.mkdir(parents=True, exist_ok=True)
    (ws_dir / "deliverables").mkdir(exist_ok=True)

    state_tpl = SKILL_DIR / "templates" / "state.example.md"
    transcript_tpl = SKILL_DIR / "templates" / "transcript.example.md"
    state_dst = ws_dir / "state.md"
    if state_tpl.exists():
        shutil.copy2(str(state_tpl), str(state_dst))
        _patch_state_md(state_dst, sid, args.deliverable_type)
    if transcript_tpl.exists():
        txt = transcript_tpl.read_text(encoding="utf-8")
        txt = txt.replace("〈Session ID〉", sid, 1)
        (ws_dir / "transcript.md").write_text(txt, encoding="utf-8")

    print(f"✓ Session 已创建: {sid}")
    print(f"  目录: {ws_dir}")
    print(f"  当前阶段: phase_0_intake")
    if args.deliverable_type:
        print(f"  交付物类型: {args.deliverable_type}")
    print(f"  下一步: orchestrator.py set {sid} success_criteria \"...\"")


def cmd_status(args):
    db = _init_db()
    s = _get_session(db, args.session_id)
    roles = _get_roles(db, args.session_id)
    msgs = _get_messages(db, args.session_id)

    phase_label = PHASE_LABELS.get(s["current_phase"], s["current_phase"])
    print(f"== {s['id']} ==")
    print(f"  阶段: {phase_label} ({s['current_phase']})")
    print(f"  Session 状态: {s['session_status']}")
    print(f"  交付物类型: {s['deliverable_type'] or '(未设)'}")
    print(f"  成功标准: {s['success_criteria'] or '(未设)'}")
    print(f"  原始需求: {(s['raw_requirement'] or '')[:80]}{'...' if s.get('raw_requirement') and len(s['raw_requirement']) > 80 else '' if not s.get('raw_requirement') else ''}")
    print(f"  任务类型: {s['task_type_tag'] or '(未设)'}")
    print(f"  选角理由: {s['role_rationale'] or '(未设)'}")
    print(f"  角色数: {len(roles)}")
    for r in roles:
        card = "✓" if (r["card_path"] or r["card_inline"]) else "✗"
        print(f"    - {r['name']}: {r['responsibility'] or ''} [卡:{card}]")
    print(f"  讨论消息数: {len(msgs)}")
    print(f"  plan_version: {s['plan_version'] or '(无)'}")
    print(f"  用户确认: {s['approved_at'] or '(未确认)'}")
    print(f"  创建: {s['created_at']}  更新: {s['updated_at']}")

    next_idx = PHASES.index(s["current_phase"]) + 1 if s["current_phase"] in PHASES else None
    if next_idx and next_idx < len(PHASES):
        next_phase = PHASES[next_idx]
        passed, reason = _check_gate(db, args.session_id, next_phase)
        marker = "✓" if passed else "✗"
        print(f"\n  下一阶段门禁 ({PHASE_LABELS.get(next_phase, next_phase)}): {marker} {reason}")


def cmd_advance(args):
    db = _init_db()
    s = _get_session(db, args.session_id)

    if s["session_status"] != "open":
        _die(f"Session 状态为 {s['session_status']}，无法推进")

    cur = s["current_phase"]
    if cur not in PHASES:
        _die(f"当前阶段 {cur} 不在已知阶段列表中")
    idx = PHASES.index(cur)
    if idx >= len(PHASES) - 1:
        _die("已在最后阶段，无法继续推进")

    target = PHASES[idx + 1]
    passed, reason = _check_gate(db, args.session_id, target)
    if not passed:
        print(f"✗ 门禁未通过 → {PHASE_LABELS.get(target, target)}")
        print(f"  原因: {reason}")
        sys.exit(1)

    db.execute(
        "UPDATE sessions SET current_phase = ?, updated_at = ? WHERE id = ?",
        (target, _now(), args.session_id)
    )
    _record_transition(db, args.session_id, cur, target, "passed")
    db.commit()

    print(f"✓ {PHASE_LABELS.get(cur, cur)} → {PHASE_LABELS.get(target, target)}")


def cmd_set_phase(args):
    db = _init_db()
    s = _get_session(db, args.session_id)

    target = PHASE_FROM_NUM.get(args.phase, args.phase)
    if target not in PHASES:
        _die(f"未知阶段: {args.phase}")

    if s["session_status"] != "open":
        _die(f"Session 状态为 {s['session_status']}，无法变更阶段")

    if not args.force:
        passed, reason = _check_gate(db, args.session_id, target)
        if not passed:
            print(f"✗ 门禁未通过 → {PHASE_LABELS.get(target, target)}")
            print(f"  原因: {reason}")
            print(f"  若确需跳过，使用 --force")
            sys.exit(1)

    old = s["current_phase"]
    db.execute(
        "UPDATE sessions SET current_phase = ?, updated_at = ? WHERE id = ?",
        (target, _now(), args.session_id)
    )
    gate_result = "forced" if args.force else "passed"
    _record_transition(db, args.session_id, old, target, gate_result)
    db.commit()

    forced_tag = " (forced)" if args.force else ""
    print(f"✓ {PHASE_LABELS.get(old, old)} → {PHASE_LABELS.get(target, target)}{forced_tag}")


def cmd_gate(args):
    db = _init_db()
    s = _get_session(db, args.session_id)
    target = args.phase
    if target:
        target = PHASE_FROM_NUM.get(target, target)
    else:
        idx = PHASES.index(s["current_phase"]) + 1 if s["current_phase"] in PHASES else None
        if idx is None or idx >= len(PHASES):
            print("已在最后阶段，无后续门禁")
            return
        target = PHASES[idx]

    passed, reason = _check_gate(db, args.session_id, target)
    marker = "✓" if passed else "✗"
    print(f"{marker} 门禁 → {PHASE_LABELS.get(target, target)}: {reason}")
    if not passed:
        sys.exit(1)


def cmd_set(args):
    db = _init_db()
    s = _get_session(db, args.session_id)
    field = args.field
    value = args.value

    settable = [
        "deliverable_type", "non_goals", "success_criteria",
        "raw_requirement", "task_type_tag", "role_rationale",
        "forcing_questions_note", "plan_version", "plan_template",
        "approved_at", "approved_by", "mode", "compression_note",
        "session_status", "ended_at",
    ]
    if field not in settable:
        _die(f"不可设置的字段: {field}\n可用: {', '.join(settable)}")

    if field == "deliverable_type" and value not in DELIVERABLE_TYPES:
        _die(f"deliverable_type 须为: {', '.join(DELIVERABLE_TYPES)}")
    if field == "session_status" and value not in SESSION_STATUSES:
        _die(f"session_status 须为: {', '.join(SESSION_STATUSES)}")
    if field == "plan_version":
        value = int(value)

    db.execute(f"UPDATE sessions SET {field} = ?, updated_at = ? WHERE id = ?",
               (value, _now(), args.session_id))
    db.commit()
    print(f"✓ {args.session_id}.{field} = {value}")


def cmd_set_role(args):
    db = _init_db()
    _get_session(db, args.session_id)

    existing = db.execute(
        "SELECT id FROM roles WHERE session_id = ? AND name = ?",
        (args.session_id, args.name)
    ).fetchone()

    if existing:
        updates = []
        params = []
        if args.responsibility:
            updates.append("responsibility = ?")
            params.append(args.responsibility)
        if args.tension:
            updates.append("tension_point = ?")
            params.append(args.tension)
        if args.card_path:
            updates.append("card_path = ?")
            params.append(args.card_path)
        if args.card_inline:
            updates.append("card_inline = ?")
            params.append(args.card_inline)
        if updates:
            params.append(args.session_id)
            params.append(args.name)
            db.execute(f"UPDATE roles SET {', '.join(updates)} WHERE session_id = ? AND name = ?", params)
            db.commit()
        print(f"✓ 已更新角色: {args.name}")
    else:
        db.execute(
            "INSERT INTO roles (session_id, name, responsibility, tension_point, card_path, card_inline) VALUES (?,?,?,?,?,?)",
            (args.session_id, args.name, args.responsibility, args.tension, args.card_path, args.card_inline)
        )
        db.commit()
        print(f"✓ 已添加角色: {args.name}")


def cmd_add_message(args):
    db = _init_db()
    _get_session(db, args.session_id)
    db.execute(
        "INSERT INTO messages (session_id, phase, role, round, content, summary, completed, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (args.session_id, args.phase, args.role, args.round, args.content, args.summary, args.completed or "unknown", _now())
    )
    db.commit()
    print(f"✓ 已记录消息: phase={args.phase} role={args.role}")


def cmd_history(args):
    db = _init_db()
    rows = db.execute(
        "SELECT * FROM phase_history WHERE session_id = ? ORDER BY id",
        (args.session_id,)
    ).fetchall()
    if not rows:
        print("(无历史)")
        return
    for r in rows:
        fr = r["from_phase"] or "(init)"
        to = r["to_phase"]
        print(f"  {r['created_at']}  {PHASE_LABELS.get(fr, fr)} → {PHASE_LABELS.get(to, to)}  [{r['gate_result']}]")


def cmd_list(args):
    db = _init_db()
    rows = db.execute("SELECT id, current_phase, session_status, created_at FROM sessions ORDER BY created_at DESC").fetchall()
    if not rows:
        print("(无 session)")
        return
    for r in rows:
        phase_label = PHASE_LABELS.get(r["current_phase"], r["current_phase"])
        print(f"  {r['id']}  {phase_label}  [{r['session_status']}]  {r['created_at']}")


def cmd_validate(args):
    db = _init_db()
    s = _get_session(db, args.session_id)
    roles = _get_roles(db, args.session_id)
    sid = args.session_id
    errors = []
    warnings = []

    if not s["deliverable_type"]:
        errors.append("缺少 deliverable_type")
    if not s["success_criteria"]:
        warnings.append("缺少 success_criteria")
    if not s["raw_requirement"]:
        warnings.append("缺少 raw_requirement")
    if not s["task_type_tag"]:
        warnings.append("缺少 task_type_tag")
    if not s["role_rationale"]:
        warnings.append("缺少 role_rationale")
    if len(roles) < 1 and PHASES.index(s["current_phase"]) >= PHASES.index("phase_3_role_cards"):
        errors.append("已到阶段 3+ 但无角色")
    for r in roles:
        if not r["card_path"] and not r["card_inline"]:
            if PHASES.index(s["current_phase"]) >= PHASES.index("phase_4_discussion"):
                errors.append(f"角色「{r['name']}」缺角色卡（已到阶段 4+）")
        else:
            content = None
            if r["card_path"]:
                resolved = _resolve_card_path(sid, r["card_path"])
                if not resolved:
                    warnings.append(f"角色「{r['name']}」的 card_path 文件不存在：{r['card_path']}")
                else:
                    content = resolved.read_text(encoding="utf-8")
            elif r["card_inline"]:
                content = r["card_inline"]
            if content is not None:
                err = _validate_card_content(content, r["name"])
                if err:
                    warnings.append(err)

    plan_path = WORKSHOPS_DIR / sid / "plan.md"
    if PHASES.index(s["current_phase"]) >= PHASES.index("awaiting_approval"):
        if not plan_path.exists():
            errors.append("已到 awaiting_approval+ 但 plan.md 不存在")
    if s["current_phase"] == "phase_6_execution" and not s["approved_at"]:
        errors.append("已在阶段 6 但无 approved_at")
    if s["session_status"] in ("completed", "stopped") and not s["ended_at"]:
        warnings.append(f"Session 状态为 {s['session_status']} 但缺少 ended_at")

    print(f"== validate: {sid} ==")
    for e in errors:
        print(f"  ✗ {e}")
    for w in warnings:
        print(f"  ⚠ {w}")
    if not errors and not warnings:
        print("  ✓ 全部通过")
    elif not errors:
        print(f"  共 {len(warnings)} 个建议项，无阻塞错误")
    else:
        print(f"  共 {len(errors)} 个错误，{len(warnings)} 个建议")
        sys.exit(1)


def cmd_import(args):
    """从现有 workshops/<id>/state.md 导入基础字段到 DB"""
    db = _init_db()
    sid = args.session_id
    state_path = WORKSHOPS_DIR / sid / "state.md"
    if not state_path.exists():
        _die(f"找不到 {state_path}")

    existing = db.execute("SELECT id FROM sessions WHERE id = ?", (sid,)).fetchone()
    if existing:
        _die(f"Session 已存在于 DB: {sid}（若需重新导入，先手动删除 DB 记录）")

    text = state_path.read_text(encoding="utf-8")
    now = _now()

    phase_match = re.search(r"phase key\*\*:\s*`([^`]+)`", text)
    current_phase = phase_match.group(1) if phase_match else "phase_0_intake"
    if current_phase not in PHASES:
        current_phase = "phase_0_intake"

    tag_match = re.search(r"任务类型标签[^`]*`([^`]+)`", text)
    task_type_tag = tag_match.group(1) if tag_match else None

    dt_match = re.search(r"\[x\]\s*\*\*`(\w+)`\*\*", text)
    deliverable_type = dt_match.group(1) if dt_match and dt_match.group(1) in DELIVERABLE_TYPES else None

    req_match = re.search(r"原始需求[））\s]*[：:]\s*(.*?)(?:\n##|\n---|\Z)", text, re.DOTALL)
    raw_req = req_match.group(1).strip()[:500] if req_match else None

    sc_match = re.search(r"成功标准[^：:]*[：:]\s*(.*?)$", text, re.MULTILINE)
    success_criteria = sc_match.group(1).strip()[:300] if sc_match and sc_match.group(1).strip() else None

    rr_match = re.search(r"\*\*选角理由\*\*[^：:]*[：:]\s*(.*?)(?:\n\*\*|\n\||\n---|\Z)", text, re.DOTALL)
    role_rationale = rr_match.group(1).strip()[:500] if rr_match and rr_match.group(1).strip() else None

    db.execute(
        """INSERT INTO sessions
        (id, current_phase, task_type_tag, raw_requirement, deliverable_type, success_criteria, role_rationale, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (sid, current_phase, task_type_tag, raw_req, deliverable_type, success_criteria, role_rationale, now, now)
    )
    _record_transition(db, sid, None, current_phase, "imported")

    role_pattern = re.compile(r"\|\s*\*\*(.+?)\*\*\s*\|(.+?)\|(.+?)\|")
    for m in role_pattern.finditer(text):
        name = m.group(1).strip()
        resp = m.group(2).strip()
        tension = m.group(3).strip()
        if name and name != "角色":
            db.execute(
                "INSERT OR IGNORE INTO roles (session_id, name, responsibility, tension_point) VALUES (?,?,?,?)",
                (sid, name, resp, tension)
            )

    db.commit()
    roles = _get_roles(db, sid)
    print(f"✓ 已导入: {sid}")
    print(f"  阶段: {current_phase}")
    print(f"  角色: {len(roles)} 个")
    print(f"  提示: 用 set 命令补充缺失字段（deliverable_type, success_criteria 等）")


def cmd_sync(args):
    """将 DB 状态回写到 state.md 的基本信息区"""
    db = _init_db()
    s = _get_session(db, args.session_id)
    state_path = WORKSHOPS_DIR / args.session_id / "state.md"
    if not state_path.exists():
        _die(f"找不到 {state_path}")

    text = state_path.read_text(encoding="utf-8")
    changed = False

    phase_pat = r"(\*\*当前阶段 phase key\*\*:\s*`)[^`]+(`)"
    text, n = re.subn(phase_pat, lambda m: m.group(1) + s["current_phase"] + m.group(2), text, count=1)
    if n == 0:
        print("⚠ state.md 中未找到 phase key 行，跳过同步")
    else:
        changed = True
        print(f"✓ state.md 已同步: phase key → {s['current_phase']}")

    sess_status_pat = r"^(- \*\*Session 状态\*\*[^：:]*[：:]\s*`)([^`]+)(`)(.*)$"
    text, n2 = re.subn(
        sess_status_pat,
        lambda m: m.group(1) + s["session_status"] + m.group(3) + m.group(4),
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if n2 > 0:
        changed = True
        print(f"✓ state.md 已同步: Session 状态 → {s['session_status']}")
    elif s["session_status"]:
        print("⚠ state.md 中未匹配到「- **Session 状态**…：`…`」行，跳过 Session 状态同步（请检查模板格式）")

    if changed:
        state_path.write_text(text, encoding="utf-8")


def cmd_cleanup(args):
    """清理 OpenClaw sessions.json 残留 subagent"""
    openclaw_root = WORKSPACE_ROOT.parent
    sessions_json = openclaw_root / "agents" / "main" / "sessions" / "sessions.json"
    if not sessions_json.exists():
        _die(f"找不到 {sessions_json}")

    ts = time.strftime("%Y%m%d-%H%M%S")
    bak = f"{sessions_json}.bak.{ts}"
    shutil.copy2(str(sessions_json), bak)
    print(f"已备份: {bak}")

    with open(sessions_json, encoding="utf-8") as f:
        data = json.load(f)

    sub_keys = [k for k in data if "subagent" in k.lower()]
    if not sub_keys:
        print("无残留 subagent 条目。")
        return

    print(f"找到 {len(sub_keys)} 个 subagent 条目：")
    for k in sub_keys:
        label = data[k].get("label", "(无)") if isinstance(data[k], dict) else ""
        print(f"  - {k}  label={label}")
        del data[k]

    with open(sessions_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"已删除 {len(sub_keys)} 个。请重启 Gateway。")


# ─── CLI ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="multi-agent-workshop Orchestrator (Plan B Lite)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="创建 session")
    p_init.add_argument("session_id")
    p_init.add_argument("--deliverable-type", "-d", choices=DELIVERABLE_TYPES)

    p_status = sub.add_parser("status", help="查看 session 状态")
    p_status.add_argument("session_id")

    p_advance = sub.add_parser("advance", help="推进到下一阶段（检查门禁）")
    p_advance.add_argument("session_id")

    p_sp = sub.add_parser("set-phase", help="跳转阶段（检查门禁）")
    p_sp.add_argument("session_id")
    p_sp.add_argument("phase")
    p_sp.add_argument("--force", "-f", action="store_true", help="跳过门禁检查")

    p_gate = sub.add_parser("gate", help="检查门禁")
    p_gate.add_argument("session_id")
    p_gate.add_argument("phase", nargs="?")

    p_set = sub.add_parser("set", help="设置字段")
    p_set.add_argument("session_id")
    p_set.add_argument("field")
    p_set.add_argument("value")

    p_role = sub.add_parser("set-role", help="添加/更新角色")
    p_role.add_argument("session_id")
    p_role.add_argument("name")
    p_role.add_argument("--responsibility", "-r")
    p_role.add_argument("--tension", "-t")
    p_role.add_argument("--card-path")
    p_role.add_argument("--card-inline")

    p_msg = sub.add_parser("add-message", help="记录讨论消息")
    p_msg.add_argument("session_id")
    p_msg.add_argument("--phase", required=True)
    p_msg.add_argument("--role")
    p_msg.add_argument("--round")
    p_msg.add_argument("--content")
    p_msg.add_argument("--summary")
    p_msg.add_argument("--completed", choices=["complete", "partial", "blocked", "unknown"])

    p_hist = sub.add_parser("history", help="阶段变更历史")
    p_hist.add_argument("session_id")

    sub.add_parser("list", help="列出所有 session")

    p_val = sub.add_parser("validate", help="全量校验")
    p_val.add_argument("session_id")

    p_imp = sub.add_parser("import", help="从现有 state.md 导入")
    p_imp.add_argument("session_id")

    p_sync = sub.add_parser("sync", help="DB 状态回写 state.md")
    p_sync.add_argument("session_id")

    sub.add_parser("cleanup", help="清理 OpenClaw 残留 subagent")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmd_map = {
        "init": cmd_init,
        "status": cmd_status,
        "advance": cmd_advance,
        "set-phase": cmd_set_phase,
        "gate": cmd_gate,
        "set": cmd_set,
        "set-role": cmd_set_role,
        "add-message": cmd_add_message,
        "history": cmd_history,
        "list": cmd_list,
        "validate": cmd_validate,
        "import": cmd_import,
        "sync": cmd_sync,
        "cleanup": cmd_cleanup,
    }
    cmd_map[args.command](args)


if __name__ == "__main__":
    main()
