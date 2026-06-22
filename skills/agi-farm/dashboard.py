#!/usr/bin/env python3
"""
CooperCorp AGI Team Dashboard Server — File-Watcher Edition
Usage: python3 dashboard.py [--port 8080] [--workspace /path/to/workspace] [--no-browser]

Live updates via watchdog: pushes SSE events immediately on any workspace file change.
Fallback: full refresh every 60s + keepalive ping every 25s (proxy-safe).
"""

import argparse
import json
import os
import queue
import re
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# ── watchdog ─────────────────────────────────────────────────────────────────
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_OK = True
except ImportError:
    WATCHDOG_OK = False
    print("⚠  watchdog not installed — falling back to 5s polling.")
    print("   Install with: pip3 install watchdog --break-system-packages")


# ── Constants ─────────────────────────────────────────────────────────────────
WATCHED_EXTENSIONS = {".json", ".md"}
DEBOUNCE_SECONDS   = 0.25   # coalesce rapid writes into one push
KEEPALIVE_SECONDS  = 25     # SSE comment to prevent proxy timeout
FALLBACK_SECONDS   = 60     # full re-push even if no file change
POLL_FALLBACK_SEC  = 5      # interval when watchdog unavailable


# ═══════════════════════════════════════════════════════════════════════════════
#  DATA LAYER
# ═══════════════════════════════════════════════════════════════════════════════

class SlowDataCache:
    """
    Background thread that refreshes slow subprocess calls (openclaw agents list,
    openclaw cron list) every REFRESH_SEC seconds. build_workspace_snapshot reads
    from this cache instantly instead of blocking on subprocess calls per file change.
    """
    REFRESH_SEC = 30

    def __init__(self):
        self._lock          = threading.Lock()
        self._agent_statuses: dict = {}
        self._cron_statuses:  dict = {}
        self._last_refresh:   float = 0.0
        self._thread = threading.Thread(target=self._loop, daemon=True, name="slow-data-cache")
        self._thread.start()

    def _fetch_agents(self) -> dict:
        try:
            r = subprocess.run(["openclaw", "agents", "list", "--json"],
                                capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                return {a["id"]: a for a in json.loads(r.stdout)}
        except Exception:
            pass
        return {}

    def _fetch_crons(self) -> dict:
        statuses: dict = {}
        try:
            r = subprocess.run(["openclaw", "cron", "list"],
                                capture_output=True, text=True, timeout=10)
            for line in r.stdout.splitlines()[1:]:
                parts = line.split()
                if len(parts) < 8:
                    continue
                for i, part in enumerate(parts):
                    if part.lower() in ("running", "ok", "error", "idle") and i + 2 < len(parts):
                        cs       = part.lower()
                        agent_id = parts[-1].strip()
                        if cs == "running" and agent_id not in statuses:
                            statuses[agent_id] = "busy"
                        elif cs == "error" and statuses.get(agent_id) != "busy":
                            statuses[agent_id] = "error"
                        break
        except Exception:
            pass
        return statuses

    def _refresh(self):
        agents = self._fetch_agents()
        crons  = self._fetch_crons()
        with self._lock:
            self._agent_statuses = agents
            self._cron_statuses  = crons
            self._last_refresh   = time.time()

    def _loop(self):
        self._refresh()           # warm up immediately on start
        while True:
            time.sleep(self.REFRESH_SEC)
            self._refresh()

    def get_agent_statuses(self) -> dict:
        with self._lock:
            return dict(self._agent_statuses)

    def get_cron_statuses(self) -> dict:
        with self._lock:
            return dict(self._cron_statuses)

    def age_seconds(self) -> float:
        with self._lock:
            return time.time() - self._last_refresh if self._last_refresh else 999


# Global cache instance — started once, shared by all requests
_slow_cache = SlowDataCache()


def get_heartbeat_age(workspace: Path, ws_dir: str = "") -> int:
    """Minutes since last ISO timestamp found in HEARTBEAT.md."""
    paths = []
    if ws_dir:
        paths.append(workspace / "agents-workspaces" / ws_dir / "HEARTBEAT.md")
    paths.append(workspace / "HEARTBEAT.md")
    for p in paths:
        try:
            content = p.read_text(encoding="utf-8")
            matches = re.findall(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', content)
            if matches:
                last_ts = datetime.fromisoformat(matches[-1]).replace(tzinfo=timezone.utc)
                return int((datetime.now(timezone.utc) - last_ts).total_seconds() / 60)
        except Exception:
            pass
    return 999


def read_json(workspace: Path, rel: str) -> dict | list:
    try:
        return json.loads((workspace / rel).read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_md(workspace: Path, rel: str) -> str:
    try:
        return (workspace / rel).read_text(encoding="utf-8")
    except Exception:
        return ""


def count_inbox(workspace: Path, agent_id: str) -> int:
    try:
        content = (workspace / f"comms/inboxes/{agent_id}.md").read_text(encoding="utf-8")
        return len([l for l in content.splitlines() if l.startswith("##")])
    except Exception:
        return 0


def _load_crons() -> list:
    """Load all cron jobs from jobs.json with enriched state."""
    try:
        cron_file = Path.home() / ".openclaw/cron/jobs.json"
        raw = json.loads(cron_file.read_text())
        jobs = raw.get("jobs", [])
        now_ms = int(time.time() * 1000)
        for j in jobs:
            state = j.get("state", {})
            # Human-friendly next/last run
            nxt = state.get("nextRunAtMs")
            lst = state.get("lastRunAtMs")
            j["_next_run_sec"]  = round((nxt - now_ms) / 1000) if nxt else None
            j["_last_run_sec"]  = round((now_ms - lst) / 1000) if lst else None
            j["_status"]        = state.get("lastStatus", "idle")
            j["_consecutive_errors"] = state.get("consecutiveErrors", 0)
            j["_last_error"]    = state.get("lastError", "")
            j["_duration_ms"]   = state.get("lastDurationMs")
        return jobs
    except Exception:
        return []


def _load_comms(workspace: Path, agent_ids: list) -> dict:
    """Load inbox + outbox content for each agent."""
    comms = {}
    for aid in agent_ids:
        inbox_path  = workspace / f"comms/inboxes/{aid}.md"
        outbox_path = workspace / f"comms/outboxes/{aid}.md"
        comms[aid] = {
            "inbox":  inbox_path.read_text(encoding="utf-8")  if inbox_path.exists()  else "",
            "outbox": outbox_path.read_text(encoding="utf-8") if outbox_path.exists() else "",
        }
    return comms


def _build_alerts(tasks: list, agents: list, crons: list, sla_at_risk: list) -> list:
    """Derive actionable alerts from live system state."""
    alerts = []
    now = datetime.now(timezone.utc).isoformat()

    for t in tasks:
        if t.get("status") == "needs_human_decision":
            alerts.append({"id": f"hitl-{t['id']}", "type": "hitl", "severity": "critical",
                "title": f"HITL Required: {t.get('title','')}", "detail": t.get("hitl_reason",""),
                "ts": t.get("created_at", now), "task_id": t["id"], "resolved": False})

    for t in sla_at_risk:
        alerts.append({"id": f"sla-{t['id']}", "type": "sla_breach", "severity": "high",
            "title": f"SLA At Risk: {t.get('title','')}", "detail": f"Deadline: {t.get('sla',{}).get('deadline','')}",
            "ts": now, "task_id": t["id"], "resolved": False})

    for a in agents:
        if a.get("status") == "error":
            alerts.append({"id": f"agent-error-{a['id']}", "type": "agent_error", "severity": "high",
                "title": f"Agent Error: {a.get('name', a['id'])}", "detail": "Last cron run failed",
                "ts": now, "agent_id": a["id"], "resolved": False})

    for j in crons:
        if j.get("_consecutive_errors", 0) >= 3:
            alerts.append({"id": f"cron-{j['id']}", "type": "cron_error", "severity": "medium",
                "title": f"Cron Failing: {j.get('name','')} [{j.get('agentId','')}]",
                "detail": j.get("_last_error", "")[:120],
                "ts": now, "cron_id": j["id"], "resolved": False})

    # Sort: critical first, then by time
    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    alerts.sort(key=lambda a: sev_order.get(a["severity"], 9))
    return alerts


def enrich_projects(projects: list, tasks: list, workspace: Path) -> list:
    """Auto-calculate all derived project fields from live task data."""
    task_map = {t["id"]: t for t in tasks if isinstance(t, dict) and "id" in t}

    for p in projects:
        if not isinstance(p, dict):
            continue

        task_ids   = p.get("task_ids", [])
        proj_tasks = [task_map[tid] for tid in task_ids if tid in task_map]

        # ── task counts ──
        done    = [t for t in proj_tasks if t.get("status") == "complete"]
        failed  = [t for t in proj_tasks if t.get("status") == "failed"]
        blocked = [t for t in proj_tasks if t.get("status") == "blocked"]
        hitl    = [t for t in proj_tasks if t.get("status") == "needs_human_decision"]
        active  = [t for t in proj_tasks if t.get("status") == "in-progress"]
        pending = [t for t in proj_tasks if t.get("status") == "pending"]

        p["_task_counts"] = {
            "total":      len(proj_tasks),
            "done":       len(done),
            "active":     len(active),
            "pending":    len(pending),
            "blocked":    len(blocked),
            "failed":     len(failed),
            "hitl":       len(hitl),
        }

        # ── progress % (tasks-based) ──
        p["_progress_pct"] = (
            round(len(done) / len(proj_tasks) * 100) if proj_tasks else 0
        )

        # ── quality score (avg of completed tasks) ──
        qualities = []
        for t in done:
            q = t.get("quality_score") or t.get("output_quality")
            if q is not None:
                try: qualities.append(float(q))
                except: pass
        p["_quality_score"] = (
            round(sum(qualities) / len(qualities), 2) if qualities
            else p.get("quality_score")
        )

        # ── velocity (tasks/day since project start) ──
        try:
            created = datetime.fromisoformat(p["created_at"].replace("Z", "+00:00"))
            days = max(1, (datetime.now(timezone.utc) - created).days)
            p["_velocity"] = round(len(done) / days, 2)
        except Exception:
            p["_velocity"] = p.get("velocity", 0)

        # ── auto-detect risks from live task data ──
        now = datetime.now(timezone.utc)
        auto_risks = []

        for t in blocked:
            auto_risks.append({
                "id": f"auto-blocked-{t['id']}",
                "type": "blocked",
                "description": f"Task {t['id']} blocked: {t.get('title','')}",
                "detected_at": now.isoformat(),
                "detected_by": "dashboard",
                "severity": "high",
                "resolved": False,
            })
        for t in hitl:
            auto_risks.append({
                "id": f"auto-hitl-{t['id']}",
                "type": "hitl_pending",
                "description": f"HITL required on {t['id']}: {t.get('hitl_reason') or t.get('title','')}",
                "detected_at": now.isoformat(),
                "detected_by": "dashboard",
                "severity": "critical",
                "resolved": False,
            })
        for t in proj_tasks:
            sla = t.get("sla", {}) or {}
            dl  = sla.get("deadline") or sla.get("target")
            if dl and t.get("status") not in ("complete","failed"):
                try:
                    d = datetime.fromisoformat(dl.replace("Z", "+00:00"))
                    if d < now:
                        auto_risks.append({
                            "id": f"auto-overdue-{t['id']}",
                            "type": "overdue",
                            "description": f"Task {t['id']} past deadline: {t.get('title','')}",
                            "detected_at": now.isoformat(),
                            "detected_by": "dashboard",
                            "severity": "high",
                            "resolved": False,
                        })
                except: pass

        # Merge: auto risks + manually logged risks (agent-written ones)
        existing_ids = {r["id"] for r in p.get("risks", [])}
        merged = [r for r in p.get("risks", []) if not r.get("resolved", False)]
        for r in auto_risks:
            if r["id"] not in existing_ids:
                merged.append(r)
        p["_risks"] = merged

        # ── activity feed (chronological from task completions + decisions) ──
        activity = []
        for t in done:
            ca = t.get("completed_at")
            if ca:
                agent = t.get("assigned_to", "?")
                activity.append({
                    "ts": ca, "type": "task_complete",
                    "agent": agent,
                    "text": f"Completed {t['id']}: {t.get('title','')}",
                    "task_id": t["id"],
                })
        for t in failed:
            ca = t.get("updated_at") or t.get("created_at", "")
            activity.append({
                "ts": ca, "type": "task_failed",
                "agent": t.get("assigned_to","?"),
                "text": f"Failed {t['id']}: {t.get('title','')}",
                "task_id": t["id"],
            })
        for d in p.get("decisions", []):
            activity.append({
                "ts": d.get("decided_at",""),
                "type": "decision",
                "agent": d.get("decided_by","?"),
                "text": d.get("decision",""),
                "decision_id": d.get("id"),
            })
        for r in p.get("risks", []):
            activity.append({
                "ts": r.get("detected_at",""),
                "type": "risk",
                "agent": r.get("detected_by","?"),
                "text": r.get("description",""),
                "severity": r.get("severity"),
            })
        activity.sort(key=lambda x: x.get("ts",""), reverse=True)
        p["_activity"] = activity[:30]

        # ── auto-advance milestones ──
        for ms in p.get("milestones", []):
            if ms.get("auto_complete") and ms.get("status") != "complete":
                ms_tasks = ms.get("task_ids", [])
                if ms_tasks and all(task_map.get(tid, {}).get("status") == "complete" for tid in ms_tasks):
                    ms["status"] = "complete"
                    ms["completed_at"] = now.isoformat()

        # ── milestone counts ──
        mss = p.get("milestones", [])
        p["_milestone_counts"] = {
            "total":    len(mss),
            "done":     sum(1 for m in mss if m.get("status") == "complete"),
            "active":   sum(1 for m in mss if m.get("status") == "in-progress"),
            "pending":  sum(1 for m in mss if m.get("status") == "pending"),
            "blocked":  sum(1 for m in mss if m.get("status") == "blocked"),
        }

        # ── last activity timestamp ──
        ts_list = [a["ts"] for a in p["_activity"] if a.get("ts")]
        p["_last_activity"] = max(ts_list) if ts_list else p.get("updated_at","")

        # ── agent session traces (proc_ids from tasks) ──
        p["_sessions"] = [
            {"task_id": t["id"], "proc_id": t.get("proc_id"), "assigned_to": t.get("assigned_to"),
             "status": t.get("status"), "completed_at": t.get("completed_at")}
            for t in proj_tasks if t.get("proc_id")
        ]

    return projects



def _probe_gateway(timeout: float = 1.0) -> bool:
    """Return True if the OpenClaw gateway port is reachable."""
    try:
        cfg_path = Path.home() / ".openclaw" / "openclaw.json"
        port = 18789  # default
        if cfg_path.exists():
            cfg = json.loads(cfg_path.read_text())
            port = cfg.get("gateway", {}).get("port", port)
        with socket.create_connection(("127.0.0.1", port), timeout=timeout):
            return True
    except Exception:
        return False

def get_dashboard_data(workspace: Path) -> dict:
    now = datetime.now(timezone.utc)

    # ── core data files ──
    tasks_raw   = read_json(workspace, "TASKS.json")
    tasks       = tasks_raw.get("tasks", []) if isinstance(tasks_raw, dict) else (tasks_raw if isinstance(tasks_raw, list) else [])
    agent_status_raw = read_json(workspace, "AGENT_STATUS.json")
    agent_perf_raw   = read_json(workspace, "AGENT_PERFORMANCE.json")
    agent_perf       = agent_perf_raw.get("agents", {}) if isinstance(agent_perf_raw, dict) else {}
    okrs_raw    = read_json(workspace, "OKRs.json")
    velocity_raw= read_json(workspace, "VELOCITY.json")
    budget_raw  = read_json(workspace, "BUDGET.json")
    projects_raw= read_json(workspace, "PROJECTS.json")
    projects    = enrich_projects(
        projects_raw.get("projects", []) if isinstance(projects_raw, dict) else [],
        tasks, workspace
    )
    experiments_raw = read_json(workspace, "EXPERIMENTS.json")
    experiments = experiments_raw.get("experiments", []) if isinstance(experiments_raw, dict) else []
    backlog_raw = read_json(workspace, "IMPROVEMENT_BACKLOG.json")
    backlog     = backlog_raw.get("items", []) if isinstance(backlog_raw, dict) else []
    benchmarks_raw   = read_json(workspace, "MODEL_BENCHMARKS.json")
    shared_knowledge = read_json(workspace, "SHARED_KNOWLEDGE.json")
    sk_entries  = shared_knowledge.get("entries", []) if isinstance(shared_knowledge, dict) else []
    broadcast   = read_md(workspace, "comms/broadcast.md")

    # ── memory lines ──
    try:
        memory_lines = len((workspace / "MEMORY.md").read_text(encoding="utf-8").splitlines())
    except Exception:
        memory_lines = 0

    # ── task stats ──
    task_counts = {
        "pending": 0, "in-progress": 0, "complete": 0,
        "failed": 0, "blocked": 0, "needs_human_decision": 0,
    }
    sla_at_risk = []
    for t in tasks:
        if not isinstance(t, dict):
            continue
        status = t.get("status", "pending")
        if status in task_counts:
            task_counts[status] += 1
        sla = t.get("sla", {}) or {}
        deadline = sla.get("deadline") or sla.get("target")
        if deadline and status not in ("complete", "failed"):
            try:
                dl = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
                if (dl - now).total_seconds() < 7200:
                    sla_at_risk.append(t)
            except Exception:
                pass

    # ── live agent cards ──
    live_agents   = _slow_cache.get_agent_statuses()
    cron_statuses = _slow_cache.get_cron_statuses()

    agent_ids = (
        list(live_agents.keys()) if live_agents
        else (list(agent_status_raw.keys()) if isinstance(agent_status_raw, dict) else [])
    )

    agents = []
    for aid in agent_ids:
        live        = live_agents.get(aid, {})
        status_info = (agent_status_raw.get(aid, {}) if isinstance(agent_status_raw, dict) else {})
        if not isinstance(status_info, dict):
            status_info = {}
        perf        = agent_perf.get(aid, {}) if isinstance(agent_perf.get(aid), dict) else {}
        inbox_count = count_inbox(workspace, aid)

        agent_ws_path = live.get("workspace", "")
        ws_dir = Path(agent_ws_path).name if (agent_ws_path and agent_ws_path != str(workspace)) else ""
        hb_age = get_heartbeat_age(workspace, ws_dir)

        if cron_statuses.get(aid) == "busy":
            live_status = "busy"
        elif cron_statuses.get(aid) == "error":
            live_status = "error"
        elif hb_age < 6:
            live_status = "active"
        elif hb_age < 60:
            live_status = "available"
        else:
            live_status = status_info.get("status", "available")

        agents.append({
            "id":             aid,
            "name":           live.get("identityName") or live.get("name") or status_info.get("name", aid),
            "emoji":          live.get("identityEmoji") or status_info.get("emoji", "🤖"),
            "role":           status_info.get("role", ""),
            "model":          live.get("model", ""),
            "status":         live_status,
            "inbox_count":    inbox_count,
            "tasks_completed":perf.get("tasks_completed", 0),
            "tasks_failed":   perf.get("tasks_failed", 0),
            "avg_quality":    perf.get("avg_quality_score", 0),
            "credibility":    perf.get("credibility_score", 1.0),
            "specializations":perf.get("specialization_strengths", []),
        })

    velocity_daily   = velocity_raw.get("daily", [])   if isinstance(velocity_raw, dict) else []
    velocity_summary = velocity_raw.get("weekly_summary", {}) if isinstance(velocity_raw, dict) else {}

    # ── cron jobs ──
    crons = _load_crons()

    # ── dispatcher state ──
    dispatcher_raw = read_json(workspace, "DISPATCHER_STATE.json")

    # ── agent comms (inbox + outbox per agent) ──
    comms = _load_comms(workspace, [a["id"] for a in agents])

    # ── knowledge entries ──
    knowledge_entries = sk_entries

    # ── sprint ──
    sprint_raw = read_json(workspace, "SPRINT.json")

    # ── alerts (derived) ──
    alerts = _build_alerts(tasks, agents, crons, sla_at_risk)

    hitl_tasks = [t for t in tasks if t.get("status") == "needs_human_decision"]

    return {
        "timestamp":    now.isoformat(),
        "gateway_online": _probe_gateway(),
        "agents":       agents,
        "tasks":        tasks,
        "task_counts":  task_counts,
        "sla_at_risk":  sla_at_risk,
        "hitl_tasks":   hitl_tasks,
        "okrs":         okrs_raw if isinstance(okrs_raw, dict) else {},
        "velocity": {
            "daily":          velocity_daily,
            "weekly_summary": velocity_summary,
            "metrics":        velocity_raw.get("metrics", {}) if isinstance(velocity_raw, dict) else {},
        },
        "budget":          budget_raw if isinstance(budget_raw, dict) else {},
        "projects":        projects,
        "experiments":     experiments,
        "backlog":         backlog,
        "benchmarks":      benchmarks_raw if isinstance(benchmarks_raw, dict) else {},
        "knowledge":       knowledge_entries,
        "knowledge_count": len(sk_entries),
        "memory_lines":    memory_lines,
        "broadcast":       broadcast[-2000:],
        "crons":           crons,
        "dispatcher":      dispatcher_raw if isinstance(dispatcher_raw, dict) else {},
        "comms":           comms,
        "sprint":          sprint_raw if isinstance(sprint_raw, dict) else {},
        "alerts":          alerts,
        "cache_age_seconds": round(_slow_cache.age_seconds()),
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  BROADCASTER  (thread-safe fan-out hub)
# ═══════════════════════════════════════════════════════════════════════════════

class Broadcaster:
    """
    Hub that holds one queue per connected SSE client.
    Push a message → every client receives it.
    """

    def __init__(self):
        self._lock    = threading.Lock()
        self._clients: dict[int, queue.Queue] = {}
        self._counter = 0

    def subscribe(self) -> tuple[int, queue.Queue]:
        with self._lock:
            cid = self._counter
            self._counter += 1
            q: queue.Queue = queue.Queue(maxsize=8)
            self._clients[cid] = q
        return cid, q

    def unsubscribe(self, cid: int):
        with self._lock:
            self._clients.pop(cid, None)

    def push(self, payload: str):
        """Fan-out payload string to all connected clients (non-blocking)."""
        with self._lock:
            dead = []
            for cid, q in self._clients.items():
                try:
                    q.put_nowait(payload)
                except queue.Full:
                    dead.append(cid)
            for cid in dead:
                del self._clients[cid]

    def broadcast(self, data: dict):
        """Alias: serialize dict and push to all clients."""
        self.push(json.dumps(data, default=str))

    @property
    def client_count(self) -> int:
        with self._lock:
            return len(self._clients)


# ═══════════════════════════════════════════════════════════════════════════════
#  FILE WATCHER
# ═══════════════════════════════════════════════════════════════════════════════

class WorkspaceWatcher:
    """
    Wraps watchdog (or a polling thread if unavailable).
    Debounces rapid file events, then calls `on_change()`.
    """

    def __init__(self, workspace: Path, on_change, debounce: float = DEBOUNCE_SECONDS):
        self.workspace  = workspace
        self.on_change  = on_change
        self.debounce   = debounce
        self._timer: threading.Timer | None = None
        self._lock      = threading.Lock()
        self._observer  = None
        self._poll_thread: threading.Thread | None = None

    def start(self):
        if WATCHDOG_OK:
            self._start_watchdog()
        else:
            self._start_poll()

    def _start_watchdog(self):
        handler = _WatchdogHandler(self._schedule)
        observer = Observer()
        observer.schedule(handler, str(self.workspace), recursive=True)
        observer.start()
        self._observer = observer
        print(f"   👁  watchdog watching {self.workspace}")

    def _start_poll(self):
        def _loop():
            while True:
                time.sleep(POLL_FALLBACK_SEC)
                self.on_change()
        t = threading.Thread(target=_loop, daemon=True)
        t.start()
        self._poll_thread = t
        print(f"   ⏱  polling every {POLL_FALLBACK_SEC}s (watchdog unavailable)")

    def _schedule(self):
        """Debounce: reset timer on every event, fire once when quiet."""
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(self.debounce, self.on_change)
            self._timer.daemon = True
            self._timer.start()

    def stop(self):
        if self._observer:
            self._observer.stop()
            self._observer.join()


class _WatchdogHandler(FileSystemEventHandler if WATCHDOG_OK else object):
    def __init__(self, callback):
        if WATCHDOG_OK:
            super().__init__()
        self._cb = callback

    def on_any_event(self, event):
        # Only care about real files with relevant extensions
        if event.is_directory:
            return
        src = getattr(event, "src_path", "")
        if Path(src).suffix.lower() in WATCHED_EXTENSIONS:
            self._cb()


# ═══════════════════════════════════════════════════════════════════════════════
#  HTTP HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

SKILL_DIR = Path(__file__).parent


def make_handler(workspace: Path, broadcaster: Broadcaster):

    class DashboardHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, fmt, *args):
            pass  # suppress default access log noise

        def send_cors(self):
            self.send_header("Access-Control-Allow-Origin",  "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_cors()
            self.end_headers()

        def do_POST(self):
            path = self.path.split("?")[0]
            try:
                length = int(self.headers.get("Content-Length", 0))
                body   = json.loads(self.rfile.read(length)) if length else {}
            except Exception:
                body = {}

            def reply(data, status=200):
                b = json.dumps(data, default=str).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.send_header("Content-Length", str(len(b)))
                self.end_headers()
                self.wfile.write(b)

            # ── Cron trigger ──
            if path.startswith("/api/cron/") and path.endswith("/trigger"):
                cron_id = path.split("/")[3]
                try:
                    subprocess.Popen(["openclaw", "cron", "run", cron_id],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    reply({"ok": True, "cron_id": cron_id, "action": "triggered"})
                except Exception as e:
                    reply({"ok": False, "error": str(e)}, 500)

            # ── Cron toggle enable/disable ──
            elif path.startswith("/api/cron/") and path.endswith("/toggle"):
                cron_id = path.split("/")[3]
                try:
                    cron_file = Path.home() / ".openclaw/cron/jobs.json"
                    jobs_data = json.loads(cron_file.read_text())
                    for j in jobs_data.get("jobs", []):
                        if j["id"] == cron_id:
                            j["enabled"] = not j.get("enabled", True)
                            new_state    = j["enabled"]
                            break
                    cron_file.write_text(json.dumps(jobs_data, indent=2))
                    reply({"ok": True, "cron_id": cron_id, "enabled": new_state})
                    broadcaster.broadcast(get_dashboard_data(workspace))
                except Exception as e:
                    reply({"ok": False, "error": str(e)}, 500)

            # ── Task status update ──
            elif path.startswith("/api/task/") and path.endswith("/status"):
                task_id = path.split("/")[3]
                new_status = body.get("status")
                if not new_status:
                    reply({"ok": False, "error": "status required"}, 400)
                else:
                    try:
                        tasks_file = workspace / "TASKS.json"
                        tasks_data = json.loads(tasks_file.read_text())
                        task_list  = tasks_data.get("tasks", tasks_data if isinstance(tasks_data, list) else [])
                        for t in task_list:
                            if t.get("id") == task_id:
                                t["status"] = new_status
                                if new_status == "complete":
                                    t["completed_at"] = datetime.now(timezone.utc).isoformat()
                                break
                        if isinstance(tasks_data, dict):
                            tasks_data["tasks"] = task_list
                            tasks_file.write_text(json.dumps(tasks_data, indent=2))
                        else:
                            tasks_file.write_text(json.dumps(task_list, indent=2))
                        reply({"ok": True, "task_id": task_id, "status": new_status})
                    except Exception as e:
                        reply({"ok": False, "error": str(e)}, 500)

            # ── HITL approve ──
            elif path.startswith("/api/hitl/") and path.endswith("/approve"):
                task_id = path.split("/")[3]
                note    = body.get("note", "Approved via dashboard")
                try:
                    tasks_file = workspace / "TASKS.json"
                    tasks_data = json.loads(tasks_file.read_text())
                    task_list  = tasks_data.get("tasks", [])
                    for t in task_list:
                        if t.get("id") == task_id:
                            t["status"] = "in-progress"
                            t["hitl_resolved_at"] = datetime.now(timezone.utc).isoformat()
                            t["hitl_resolution"]  = f"APPROVED: {note}"
                            break
                    tasks_data["tasks"] = task_list
                    tasks_file.write_text(json.dumps(tasks_data, indent=2))
                    reply({"ok": True, "task_id": task_id, "action": "approved"})
                except Exception as e:
                    reply({"ok": False, "error": str(e)}, 500)

            # ── HITL reject ──
            elif path.startswith("/api/hitl/") and path.endswith("/reject"):
                task_id = path.split("/")[3]
                note    = body.get("note", "Rejected via dashboard")
                try:
                    tasks_file = workspace / "TASKS.json"
                    tasks_data = json.loads(tasks_file.read_text())
                    task_list  = tasks_data.get("tasks", [])
                    for t in task_list:
                        if t.get("id") == task_id:
                            t["status"] = "blocked"
                            t["hitl_resolved_at"] = datetime.now(timezone.utc).isoformat()
                            t["hitl_resolution"]  = f"REJECTED: {note}"
                            break
                    tasks_data["tasks"] = task_list
                    tasks_file.write_text(json.dumps(tasks_data, indent=2))
                    reply({"ok": True, "task_id": task_id, "action": "rejected"})
                except Exception as e:
                    reply({"ok": False, "error": str(e)}, 500)

            else:
                reply({"error": "not found"}, 404)

        def do_GET(self):
            path = self.path.split("?")[0]
            if path == "/" or path == "/index.html":
                self._serve_html()
            elif path == "/api/data":
                self._serve_json(workspace)
            elif path == "/api/stream":
                self._serve_sse()
            elif path.startswith("/assets/"):
                self._serve_asset(path)
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"Not found")

        # ── static HTML (React build preferred, legacy fallback) ──
        def _serve_html(self):
            react_build = SKILL_DIR / "dashboard-react/dist/index.html"
            html_path   = react_build if react_build.exists() else SKILL_DIR / "dashboard.html"
            try:
                content = html_path.read_text(encoding="utf-8")
                
                # Fetch initial data payload and inject into HTML
                data_snapshot = get_dashboard_data(workspace)
                payload_json = json.dumps(data_snapshot, default=str)
                injection = f'<script>window.INITIAL_DATA = {payload_json};</script>'
                
                # Insert right before </head>
                if "</head>" in content:
                    content = content.replace("</head>", f"{injection}\n</head>")
                    
                content_bytes = content.encode("utf-8")
                
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_cors()
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Content-Length", str(len(content_bytes)))
                self.end_headers()
                self.wfile.write(content_bytes)
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"dashboard not found")

        # ── static assets (React build chunks) ──
        def _serve_asset(self, path: str):
            asset_path = SKILL_DIR / "dashboard-react/dist" / path.lstrip("/")
            if not asset_path.exists():
                self.send_response(404)
                self.end_headers()
                return
            ext = asset_path.suffix.lower()
            ct  = {
                ".js":   "application/javascript",
                ".css":  "text/css",
                ".png":  "image/png",
                ".svg":  "image/svg+xml",
                ".ico":  "image/x-icon",
                ".woff2":"font/woff2",
            }.get(ext, "application/octet-stream")
            content = asset_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", ct)
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        # ── REST snapshot ──
        def _serve_json(self, ws: Path):
            try:
                data = get_dashboard_data(ws)
                body = json.dumps(data, default=str).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                err = json.dumps({"error": str(e)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_cors()
                self.end_headers()
                self.wfile.write(err)

        # ── SSE stream ──
        def _serve_sse(self):
            self.send_response(200)
            self.send_header("Content-Type",  "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection",    "keep-alive")
            self.send_header("X-Accel-Buffering", "no")  # nginx compat
            self.send_cors()
            self.end_headers()

            # Subscribe to broadcaster
            cid, q = broadcaster.subscribe()

            def _write(text: str) -> bool:
                """Returns False if client disconnected."""
                try:
                    self.wfile.write(text.encode("utf-8"))
                    self.wfile.flush()
                    return True
                except (BrokenPipeError, ConnectionResetError, OSError):
                    return False

            try:
                # ── send initial snapshot immediately ──
                data    = get_dashboard_data(workspace)
                payload = json.dumps(data, default=str)
                if not _write(f"data: {payload}\n\n"):
                    return

                last_fallback = time.monotonic()
                last_keepalive = time.monotonic()

                while True:
                    now = time.monotonic()

                    # ── forced full refresh every FALLBACK_SECONDS ──
                    if now - last_fallback >= FALLBACK_SECONDS:
                        data    = get_dashboard_data(workspace)
                        payload = json.dumps(data, default=str)
                        if not _write(f"data: {payload}\n\n"):
                            return
                        last_fallback  = now
                        last_keepalive = now
                        continue

                    # ── keepalive comment every KEEPALIVE_SECONDS ──
                    if now - last_keepalive >= KEEPALIVE_SECONDS:
                        if not _write(": keepalive\n\n"):
                            return
                        last_keepalive = now

                    # ── drain the queue (file-change events) ──
                    try:
                        # Block up to 1s so we don't busy-spin
                        msg = q.get(timeout=1.0)
                        if not _write(f"data: {msg}\n\n"):
                            return
                        last_fallback  = time.monotonic()
                        last_keepalive = time.monotonic()
                        # Drain any additional queued events (coalesced)
                        while True:
                            try:
                                q.get_nowait()  # discard duplicates — next push is fresh
                            except queue.Empty:
                                break
                    except queue.Empty:
                        pass  # timeout — loop back to check keepalive / fallback

            finally:
                broadcaster.unsubscribe(cid)

    return DashboardHandler


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="CooperCorp AGI Dashboard (file-watcher edition)")
    parser.add_argument("--port",      type=int, default=8080)
    parser.add_argument("--workspace", type=str,
                        default=str(Path.home() / ".openclaw" / "workspace"))
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    workspace = Path(os.path.expanduser(args.workspace))
    if not workspace.exists():
        print(f"⚠  Workspace not found: {workspace}", file=sys.stderr)

    # ── shared broadcaster ──
    broadcaster = Broadcaster()

    # ── workspace watcher → broadcast on change ──
    def _on_change():
        # Force a refresh of the slow cache in the background so
        # agent statuses are instantly up-to-date on files change.
        threading.Thread(target=_slow_cache._refresh, daemon=True).start()
        
        if broadcaster.client_count == 0:
            return  # no clients — skip the work
        try:
            data    = get_dashboard_data(workspace)
            payload = json.dumps(data, default=str)
            broadcaster.push(payload)
        except Exception as e:
            broadcaster.push(json.dumps({"error": str(e)}))

    watcher = WorkspaceWatcher(workspace, _on_change)
    watcher.start()

    # ── HTTP server ──
    handler = make_handler(workspace, broadcaster)
    server  = ThreadingHTTPServer(("", args.port), handler)

    url = f"http://localhost:{args.port}"
    print(f"\n🚀 CooperCorp AGI Dashboard — File-Watcher Edition")
    print(f"   URL:       {url}")
    print(f"   Workspace: {workspace}")
    print(f"   SSE:       {url}/api/stream  (instant on file change, {FALLBACK_SECONDS}s fallback)")
    print(f"   Debounce:  {int(DEBOUNCE_SECONDS * 1000)}ms")
    print(f"   Press Ctrl+C to stop\n")

    if not args.no_browser:
        def _open():
            time.sleep(0.9)
            webbrowser.open(url)
        threading.Thread(target=_open, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋  Dashboard stopped.")
        watcher.stop()
        server.shutdown()


if __name__ == "__main__":
    main()
