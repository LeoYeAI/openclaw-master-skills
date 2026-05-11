#!/usr/bin/env python3
"""
OpenClaw Prediction Stack — Monitor Server
Serves system status API + static React frontend.
Ships with the prediction stack for end users.
Usage: python3 server.py [--port 3333] [--skills-dir ~/skills]
"""

import json
import os
import subprocess
import sys
import argparse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from datetime import datetime

# Default skill directories — user can override via --skills-dir
SKILLS_DIR = None
PROMPT_LAB = None

SKILL_NAMES = [
    ("kalshalyst", "Kalshalyst", "Contrarian edge scanner"),
    ("kalshi-command-center", "Kalshi Command Center", "Trade execution & portfolio"),
    ("xpulse", "Xpulse", "Social signal scanner"),
    ("polymarket-command-center", "Polymarket Command Center", "Cross-platform odds"),
    ("prediction-market-arbiter", "Prediction Market Arbiter", "Cross-platform arbitrage"),
    ("portfolio-drift-monitor", "Portfolio Drift Monitor", "Position drift alerts"),
    ("market-morning-brief", "Market Morning Brief", "Daily intelligence digest"),
    ("personality-engine", "Personality Engine", "Agent voice & behavior"),
    ("prediction-stack-setup", "Prediction Stack Setup", "Setup wizard"),
    ("prediction-stack-orchestrator", "Prediction Stack Orchestrator", "3-agent pipeline"),
]


def get_skills_status():
    """Check all 10 skills and their install/health status."""
    skills = []
    for dirname, name, desc in SKILL_NAMES:
        skill_dir = SKILLS_DIR / dirname
        skill_md = skill_dir / "SKILL.md"
        exists = skill_dir.exists()
        has_skill_md = skill_md.exists() if exists else False
        line_count = 0
        if has_skill_md:
            try:
                line_count = len(skill_md.read_text().splitlines())
            except Exception:
                pass

        scripts_dir = skill_dir / "scripts"
        script_count = 0
        if scripts_dir.exists():
            script_count = len(list(scripts_dir.glob("*.py"))) + len(list(scripts_dir.glob("*.sh")))

        skills.append({
            "id": dirname,
            "name": name,
            "description": desc,
            "installed": exists,
            "has_skill_md": has_skill_md,
            "lines": line_count,
            "scripts": script_count,
            "status": "active" if exists and has_skill_md else "missing",
        })
    return skills


def get_processes():
    """Check for running eval, autoresearch, and claude processes."""
    processes = []
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            if any(kw in line for kw in ["eval_xpulse", "eval.py", "autoresearch", "claude -p", "kalshalyst"]):
                if "grep" in line or "server.py" in line:
                    continue
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    ptype = "unknown"
                    cmd = parts[10][:120]
                    if "autoresearch" in cmd:
                        ptype = "autoresearch"
                    elif "eval_xpulse" in cmd:
                        ptype = "eval_xpulse"
                    elif "eval.py" in cmd:
                        ptype = "eval_kalshalyst"
                    elif "claude -p" in cmd:
                        ptype = "claude_cli"
                    elif "kalshalyst" in cmd:
                        ptype = "kalshalyst"

                    processes.append({
                        "pid": parts[1],
                        "type": ptype,
                        "cpu": parts[2],
                        "mem": parts[3],
                        "started": parts[8],
                        "command": cmd,
                    })
    except Exception as e:
        processes.append({"error": str(e)})
    return processes


def _read_json(path):
    """Read a JSON file, return None on failure."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def get_eval_results():
    """Read eval results from prompt-lab if available."""
    results = {"xpulse": {"status": "no_results"}, "kalshalyst": {"status": "no_results"}}

    if not PROMPT_LAB:
        return results

    # Xpulse
    xp = _read_json(PROMPT_LAB / "xpulse-results.json")
    if xp:
        xp["last_updated"] = datetime.fromtimestamp(
            (PROMPT_LAB / "xpulse-results.json").stat().st_mtime
        ).isoformat()
        results["xpulse"] = xp

    # Kalshalyst — check multiple sources
    for fname in ["results.json", "results_latest_best.json"]:
        kal = _read_json(PROMPT_LAB / fname)
        if kal and "trading_score" in kal:
            kal["last_updated"] = datetime.fromtimestamp(
                (PROMPT_LAB / fname).stat().st_mtime
            ).isoformat()
            results["kalshalyst"] = kal
            break

    return results


def get_configs():
    """Read Kelly, ensemble, and market filter configs."""
    configs = {}

    search_paths = [PROMPT_LAB, Path.home()] if PROMPT_LAB else [Path.home()]

    for base in search_paths:
        if not base:
            continue
        kp = base / "kelly_config.json"
        if kp.exists() and "kelly" not in configs:
            data = _read_json(kp)
            if data:
                configs["kelly"] = data

    if PROMPT_LAB:
        ew = _read_json(PROMPT_LAB / "ensemble_weights.json")
        if ew:
            configs["ensemble"] = ew

        mf = _read_json(PROMPT_LAB / "market_filter.json")
        if mf:
            configs["market_filter"] = mf

    return configs


def get_autoresearch_status():
    """Check if any autoresearch loops are running."""
    status = {
        "xpulse": {"running": False, "iteration": 0, "best_score": 0, "last_action": ""},
        "kalshalyst": {"running": False, "best_score": 0},
    }

    if not PROMPT_LAB:
        return status

    # Xpulse best score
    xp_best = PROMPT_LAB / "xpulse_best_score.txt"
    if xp_best.exists():
        try:
            status["xpulse"]["best_score"] = float(xp_best.read_text().strip().split(":")[0])
        except Exception:
            pass

    # Xpulse log parsing
    xp_log = PROMPT_LAB / "autoresearch_xpulse_nohup.out"
    if xp_log.exists():
        try:
            lines = xp_log.read_text().splitlines()
            for line in reversed(lines):
                if "ITERATION" in line and status["xpulse"]["iteration"] == 0:
                    try:
                        status["xpulse"]["iteration"] = int(line.split("ITERATION")[1].strip().split()[0])
                    except Exception:
                        pass
                if ("ACCEPT" in line or "REJECT" in line or "Failed" in line) and not status["xpulse"]["last_action"]:
                    status["xpulse"]["last_action"] = line.strip()[-80:]
                if status["xpulse"]["iteration"] > 0 and status["xpulse"]["last_action"]:
                    break
        except Exception:
            pass

    # Process checks
    for name, pattern in [("xpulse", "autoresearch_xpulse"), ("kalshalyst", "autoresearch.sh")]:
        try:
            result = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True, timeout=5)
            status[name]["running"] = result.returncode == 0
        except Exception:
            pass

    # Kalshalyst best score
    kal_best = PROMPT_LAB / "best_score.txt"
    if kal_best.exists():
        try:
            status["kalshalyst"]["best_score"] = float(kal_best.read_text().strip().split(":")[0])
        except Exception:
            pass

    return status


def get_recent_logs(n=30):
    """Get recent log lines from autoresearch loops."""
    logs = {}
    if not PROMPT_LAB:
        return logs

    for key, fname in [("xpulse", "autoresearch_xpulse_nohup.out"), ("kalshalyst", "autoresearch_log.txt")]:
        log_path = PROMPT_LAB / fname
        if log_path.exists():
            try:
                lines = log_path.read_text().splitlines()
                logs[key] = lines[-n:]
            except Exception:
                logs[key] = []
    return logs


def build_full_status():
    """Aggregate all status into one payload."""
    return {
        "timestamp": datetime.now().isoformat(),
        "skills": get_skills_status(),
        "processes": get_processes(),
        "eval": get_eval_results(),
        "autoresearch": get_autoresearch_status(),
        "configs": get_configs(),
        "logs": get_recent_logs(),
    }


class DashboardHandler(SimpleHTTPRequestHandler):
    """Serve API + static files."""

    def do_GET(self):
        if self.path == "/api/status":
            self.send_json(build_full_status())
        elif self.path == "/api/skills":
            self.send_json(get_skills_status())
        elif self.path == "/api/processes":
            self.send_json(get_processes())
        elif self.path == "/api/configs":
            self.send_json(get_configs())
        elif self.path == "/" or self.path == "/index.html":
            self.path = "/index.html"
            super().do_GET()
        else:
            super().do_GET()

    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def log_message(self, format, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description="OpenClaw Prediction Stack Monitor")
    parser.add_argument("--port", type=int, default=3333, help="Port (default: 3333)")
    parser.add_argument("--skills-dir", type=str, default=None,
                        help="Path to skills directory (default: ~/skills)")
    parser.add_argument("--prompt-lab", type=str, default=None,
                        help="Path to prompt-lab directory (default: ~/prompt-lab)")
    args = parser.parse_args()

    global SKILLS_DIR, PROMPT_LAB
    SKILLS_DIR = Path(args.skills_dir).expanduser() if args.skills_dir else Path.home() / "skills"
    if args.prompt_lab:
        PROMPT_LAB = Path(args.prompt_lab).expanduser()
    else:
        default_pl = Path.home() / "prompt-lab"
        PROMPT_LAB = default_pl if default_pl.exists() else None

    os.chdir(Path(__file__).parent)

    server = HTTPServer(("0.0.0.0", args.port), DashboardHandler)
    print(f"\n  ┌──────────────────────────────────────────────┐")
    print(f"  │  OPENCLAW PREDICTION STACK MONITOR v1.0      │")
    print(f"  │  http://localhost:{args.port}                      │")
    print(f"  │  Skills: {SKILLS_DIR}")
    print(f"  │  Prompt Lab: {PROMPT_LAB or 'not found'}")
    print(f"  └──────────────────────────────────────────────┘\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Monitor stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
