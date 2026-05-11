#!/usr/bin/env python3
"""
SurrealDB Memory - Web Management UI

A standalone web interface for managing the knowledge graph memory.
Includes installation, health checks, stats, and maintenance operations.

Usage:
    python3 web-ui.py [--port 8765]
    
Then open http://localhost:8765
"""

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
from urllib.parse import parse_qs, urlparse

# Try imports
try:
    from surrealdb import Surreal
    SURREALDB_AVAILABLE = True
except ImportError:
    SURREALDB_AVAILABLE = False

# ============================================
# Configuration
# ============================================

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = Path.home() / ".openclaw" / "memory"
DB_FILE = DATA_DIR / "knowledge.db"

CONFIG = {
    "connection": "ws://localhost:8000/rpc",
    "namespace": "openclaw",
    "database": "memory",
    "user": "root",
    "password": "root",
}

# ============================================
# Health & Status Checks
# ============================================

def check_surrealdb_installed() -> dict:
    """Check if SurrealDB binary is installed."""
    surreal_path = shutil.which("surreal")
    if surreal_path:
        try:
            result = subprocess.run(
                ["surreal", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version = result.stdout.strip().split("\n")[0] if result.stdout else "unknown"
            return {"installed": True, "path": surreal_path, "version": version}
        except Exception as e:
            return {"installed": True, "path": surreal_path, "version": f"error: {e}"}
    return {"installed": False, "path": None, "version": None}


def check_surrealdb_running() -> dict:
    """Check if SurrealDB server is running."""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        return {"running": result == 0, "port": 8000}
    except Exception as e:
        return {"running": False, "port": 8000, "error": str(e)}


def check_schema_initialized() -> dict:
    """Check if schema is initialized (requires running server)."""
    if not SURREALDB_AVAILABLE:
        return {"initialized": False, "error": "surrealdb package not installed"}
    
    async def check():
        try:
            db = Surreal(CONFIG["connection"])
            await db.connect()
            await db.signin({"user": CONFIG["user"], "pass": CONFIG["password"]})
            await db.use(CONFIG["namespace"], CONFIG["database"])
            
            # Check if fact table exists
            result = await db.query("INFO FOR DB")
            await db.close()
            
            tables = result[0] if result else {}
            has_fact = "fact" in str(tables)
            return {"initialized": has_fact, "tables": tables}
        except Exception as e:
            return {"initialized": False, "error": str(e)}
    
    return asyncio.run(check())


def check_python_deps() -> dict:
    """Check Python dependencies."""
    deps = {
        "surrealdb": SURREALDB_AVAILABLE,
        "openai": False,
        "yaml": False,
    }
    try:
        import openai
        deps["openai"] = True
    except ImportError:
        pass
    try:
        import yaml
        deps["yaml"] = True
    except ImportError:
        pass
    
    all_ok = all(deps.values())
    return {"ok": all_ok, "dependencies": deps}


def get_full_health() -> dict:
    """Get complete health status."""
    return {
        "timestamp": datetime.now().isoformat(),
        "surrealdb_binary": check_surrealdb_installed(),
        "surrealdb_server": check_surrealdb_running(),
        "schema": check_schema_initialized(),
        "python_deps": check_python_deps(),
        "data_dir": {
            "path": str(DATA_DIR),
            "exists": DATA_DIR.exists(),
        }
    }


# ============================================
# Database Operations
# ============================================

async def get_stats() -> dict:
    """Get database statistics."""
    if not SURREALDB_AVAILABLE:
        return {"error": "surrealdb package not installed"}
    
    try:
        db = Surreal(CONFIG["connection"])
        await db.connect()
        await db.signin({"user": CONFIG["user"], "pass": CONFIG["password"]})
        await db.use(CONFIG["namespace"], CONFIG["database"])
        
        facts = await db.query("SELECT count() FROM fact WHERE archived = false GROUP ALL")
        entities = await db.query("SELECT count() FROM entity GROUP ALL")
        edges = await db.query("SELECT count() FROM relates_to GROUP ALL")
        archived = await db.query("SELECT count() FROM fact WHERE archived = true GROUP ALL")
        
        avg_conf = await db.query("""
            SELECT math::mean(confidence) AS avg FROM fact WHERE archived = false GROUP ALL
        """)
        
        by_source = await db.query("""
            SELECT source, count() AS count FROM fact WHERE archived = false GROUP BY source
        """)
        
        await db.close()
        
        return {
            "facts": facts[0][0]["count"] if facts and facts[0] else 0,
            "entities": entities[0][0]["count"] if entities and entities[0] else 0,
            "relationships": edges[0][0]["count"] if edges and edges[0] else 0,
            "archived": archived[0][0]["count"] if archived and archived[0] else 0,
            "avg_confidence": round(avg_conf[0][0]["avg"], 3) if avg_conf and avg_conf[0] and avg_conf[0][0].get("avg") else 0,
            "by_source": by_source[0] if by_source else [],
        }
    except Exception as e:
        return {"error": str(e)}


async def run_maintenance(operation: str) -> dict:
    """Run maintenance operation."""
    if not SURREALDB_AVAILABLE:
        return {"error": "surrealdb package not installed"}
    
    try:
        db = Surreal(CONFIG["connection"])
        await db.connect()
        await db.signin({"user": CONFIG["user"], "pass": CONFIG["password"]})
        await db.use(CONFIG["namespace"], CONFIG["database"])
        
        result = {"operation": operation}
        
        if operation == "decay":
            res = await db.query("""
                UPDATE fact SET confidence = confidence * 0.95
                WHERE last_accessed < time::now() - 30d AND archived = false
                RETURN BEFORE
            """)
            result["affected"] = len(res[0]) if res and res[0] else 0
            
        elif operation == "prune":
            # Archive contradicted
            archived = await db.query("""
                UPDATE fact SET archived = true
                WHERE confidence < 0.3 AND archived = false
                RETURN BEFORE
            """)
            # Delete very low confidence
            deleted = await db.query("""
                DELETE FROM fact WHERE confidence < 0.2 AND last_confirmed < time::now() - 30d
                RETURN BEFORE
            """)
            result["archived"] = len(archived[0]) if archived and archived[0] else 0
            result["deleted"] = len(deleted[0]) if deleted and deleted[0] else 0
            
        elif operation == "consolidate":
            # This would require more complex logic - just report for now
            result["message"] = "Consolidation requires embedding comparison - run via CLI"
            
        elif operation == "full":
            # Run all
            decay = await db.query("""
                UPDATE fact SET confidence = confidence * 0.95
                WHERE last_accessed < time::now() - 30d AND archived = false
                RETURN BEFORE
            """)
            prune = await db.query("""
                DELETE FROM fact WHERE confidence < 0.2 AND last_confirmed < time::now() - 30d
                RETURN BEFORE
            """)
            result["decay_affected"] = len(decay[0]) if decay and decay[0] else 0
            result["pruned"] = len(prune[0]) if prune and prune[0] else 0
        
        await db.close()
        result["success"] = True
        return result
        
    except Exception as e:
        return {"error": str(e), "success": False}


# ============================================
# Installation / Repair
# ============================================

def install_surrealdb() -> dict:
    """Install SurrealDB binary."""
    try:
        # Detect platform
        import platform
        system = platform.system().lower()
        
        if system == "darwin":
            # macOS - try homebrew first
            if shutil.which("brew"):
                result = subprocess.run(
                    ["brew", "install", "surrealdb/tap/surreal"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            else:
                result = subprocess.run(
                    ["sh", "-c", "curl -sSf https://install.surrealdb.com | sh"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
        elif system == "linux":
            result = subprocess.run(
                ["sh", "-c", "curl -sSf https://install.surrealdb.com | sh"],
                capture_output=True,
                text=True,
                timeout=300
            )
        else:
            return {"success": False, "error": f"Unsupported platform: {system}"}
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def install_python_deps() -> dict:
    """Install Python dependencies."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "surrealdb", "openai", "pyyaml"],
            capture_output=True,
            text=True,
            timeout=120
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def start_surrealdb() -> dict:
    """Start SurrealDB server."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Start in background
        process = subprocess.Popen(
            ["surreal", "start", "--user", "root", "--pass", "root", f"file:{DB_FILE}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )
        
        # Wait a moment for startup
        import time
        time.sleep(2)
        
        # Check if running
        if process.poll() is None:
            return {"success": True, "pid": process.pid}
        else:
            stdout, stderr = process.communicate(timeout=5)
            return {
                "success": False,
                "error": stderr.decode() if stderr else "Process exited",
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def init_schema() -> dict:
    """Initialize database schema."""
    try:
        schema_file = SCRIPT_DIR / "schema.sql"
        if not schema_file.exists():
            return {"success": False, "error": "schema.sql not found"}
        
        result = subprocess.run(
            [
                "surreal", "import",
                "--conn", "http://localhost:8000",
                "--user", "root",
                "--pass", "root",
                "--ns", "openclaw",
                "--db", "memory",
                str(schema_file)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def auto_repair() -> dict:
    """Attempt to automatically repair/setup the system."""
    steps = []
    
    # 1. Check/install binary
    binary = check_surrealdb_installed()
    if not binary["installed"]:
        steps.append({"step": "install_binary", "result": install_surrealdb()})
        binary = check_surrealdb_installed()
    else:
        steps.append({"step": "install_binary", "result": {"skipped": True, "reason": "already installed"}})
    
    # 2. Check/install Python deps
    deps = check_python_deps()
    if not deps["ok"]:
        steps.append({"step": "install_python", "result": install_python_deps()})
    else:
        steps.append({"step": "install_python", "result": {"skipped": True, "reason": "all deps installed"}})
    
    # 3. Check/start server
    server = check_surrealdb_running()
    if not server["running"]:
        steps.append({"step": "start_server", "result": start_surrealdb()})
        import time
        time.sleep(2)
    else:
        steps.append({"step": "start_server", "result": {"skipped": True, "reason": "already running"}})
    
    # 4. Check/init schema
    schema = check_schema_initialized()
    if not schema.get("initialized"):
        steps.append({"step": "init_schema", "result": init_schema()})
    else:
        steps.append({"step": "init_schema", "result": {"skipped": True, "reason": "already initialized"}})
    
    # Final health check
    final_health = get_full_health()
    
    return {
        "steps": steps,
        "final_health": final_health,
        "success": (
            final_health["surrealdb_binary"]["installed"] and
            final_health["surrealdb_server"]["running"] and
            final_health["schema"].get("initialized", False)
        )
    }


# ============================================
# Web Server
# ============================================

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SurrealDB Memory - Management UI</title>
    <style>
        :root {
            --bg: #0d1117;
            --bg-secondary: #161b22;
            --border: #30363d;
            --text: #c9d1d9;
            --text-muted: #8b949e;
            --primary: #58a6ff;
            --success: #3fb950;
            --warning: #d29922;
            --danger: #f85149;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 { color: var(--primary); margin-bottom: 8px; }
        h2 { color: var(--text); margin: 24px 0 12px; font-size: 18px; }
        .subtitle { color: var(--text-muted); margin-bottom: 24px; }
        .card {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 16px;
        }
        .card-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 12px;
        }
        .row { display: flex; gap: 16px; flex-wrap: wrap; }
        .col { flex: 1; min-width: 280px; }
        .stat {
            text-align: center;
            padding: 16px;
            background: var(--bg);
            border-radius: 6px;
        }
        .stat-value { font-size: 32px; font-weight: 700; color: var(--primary); }
        .stat-label { color: var(--text-muted); font-size: 13px; }
        .status {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 500;
        }
        .status-ok { background: rgba(63, 185, 80, 0.15); color: var(--success); }
        .status-warn { background: rgba(210, 153, 34, 0.15); color: var(--warning); }
        .status-error { background: rgba(248, 81, 73, 0.15); color: var(--danger); }
        .status::before { content: ''; width: 8px; height: 8px; border-radius: 50%; background: currentColor; }
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: var(--bg-secondary);
            color: var(--text);
            font-size: 14px;
            cursor: pointer;
            transition: all 0.15s;
        }
        .btn:hover { border-color: var(--primary); color: var(--primary); }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .btn-primary { background: var(--primary); border-color: var(--primary); color: #fff; }
        .btn-primary:hover { background: #4c9aed; }
        .btn-danger { border-color: var(--danger); color: var(--danger); }
        .btn-danger:hover { background: var(--danger); color: #fff; }
        .health-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid var(--border);
        }
        .health-item:last-child { border-bottom: none; }
        .log {
            background: var(--bg);
            border-radius: 4px;
            padding: 12px;
            font-family: monospace;
            font-size: 12px;
            max-height: 200px;
            overflow-y: auto;
            white-space: pre-wrap;
            color: var(--text-muted);
        }
        .actions { display: flex; gap: 8px; margin-top: 16px; flex-wrap: wrap; }
        #toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 6px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            display: none;
            z-index: 1000;
        }
        #toast.show { display: block; animation: slideIn 0.3s ease; }
        @keyframes slideIn { from { transform: translateY(20px); opacity: 0; } }
        .spinner { animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <h1>🧠 SurrealDB Memory</h1>
    <p class="subtitle">Knowledge Graph Management UI</p>

    <div class="row">
        <div class="col">
            <div class="card">
                <div class="card-title">📊 Statistics</div>
                <div class="row" id="stats">
                    <div class="stat col"><div class="stat-value" id="stat-facts">-</div><div class="stat-label">Facts</div></div>
                    <div class="stat col"><div class="stat-value" id="stat-entities">-</div><div class="stat-label">Entities</div></div>
                    <div class="stat col"><div class="stat-value" id="stat-relations">-</div><div class="stat-label">Relations</div></div>
                    <div class="stat col"><div class="stat-value" id="stat-confidence">-</div><div class="stat-label">Avg Confidence</div></div>
                </div>
                <div class="actions">
                    <button class="btn" onclick="loadStats()">↻ Refresh</button>
                </div>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col">
            <div class="card">
                <div class="card-title">🏥 Health Status</div>
                <div id="health">
                    <div class="health-item">
                        <span>SurrealDB Binary</span>
                        <span class="status status-warn" id="health-binary">Checking...</span>
                    </div>
                    <div class="health-item">
                        <span>Database Server</span>
                        <span class="status status-warn" id="health-server">Checking...</span>
                    </div>
                    <div class="health-item">
                        <span>Schema Initialized</span>
                        <span class="status status-warn" id="health-schema">Checking...</span>
                    </div>
                    <div class="health-item">
                        <span>Python Dependencies</span>
                        <span class="status status-warn" id="health-python">Checking...</span>
                    </div>
                </div>
                <div class="actions">
                    <button class="btn" onclick="loadHealth()">↻ Check Health</button>
                    <button class="btn btn-primary" onclick="autoRepair()">🔧 Auto-Repair</button>
                </div>
            </div>
        </div>

        <div class="col">
            <div class="card">
                <div class="card-title">🔧 Maintenance</div>
                <p style="color: var(--text-muted); margin-bottom: 16px; font-size: 14px;">
                    Run maintenance operations to keep the knowledge graph healthy.
                </p>
                <div class="actions">
                    <button class="btn" onclick="runMaintenance('decay')">📉 Apply Decay</button>
                    <button class="btn" onclick="runMaintenance('prune')">🗑️ Prune Stale</button>
                    <button class="btn btn-primary" onclick="runMaintenance('full')">🔄 Full Maintenance</button>
                </div>
                <div id="maintenance-log" class="log" style="margin-top: 12px; display: none;"></div>
            </div>
        </div>
    </div>

    <div class="card">
        <div class="card-title">🛠️ Installation</div>
        <div class="row">
            <div class="col">
                <h3 style="font-size: 14px; margin-bottom: 8px;">Manual Steps</h3>
                <div class="actions">
                    <button class="btn" onclick="installBinary()">Install SurrealDB</button>
                    <button class="btn" onclick="installPython()">Install Python Deps</button>
                    <button class="btn" onclick="startServer()">Start Server</button>
                    <button class="btn" onclick="initSchema()">Init Schema</button>
                </div>
            </div>
        </div>
        <div id="install-log" class="log" style="margin-top: 12px; display: none;"></div>
    </div>

    <div id="toast"></div>

    <script>
        const API = '';
        
        function toast(message, type = 'info') {
            const el = document.getElementById('toast');
            el.textContent = message;
            el.className = 'show';
            el.style.borderColor = type === 'error' ? 'var(--danger)' : type === 'success' ? 'var(--success)' : 'var(--border)';
            setTimeout(() => el.className = '', 3000);
        }
        
        async function api(endpoint, method = 'GET') {
            try {
                const res = await fetch(API + '/api/' + endpoint, { method });
                return await res.json();
            } catch (e) {
                toast('API Error: ' + e.message, 'error');
                return { error: e.message };
            }
        }
        
        function setStatus(id, ok, text) {
            const el = document.getElementById(id);
            el.className = 'status ' + (ok ? 'status-ok' : 'status-error');
            el.textContent = text || (ok ? 'OK' : 'Error');
        }
        
        async function loadHealth() {
            const data = await api('health');
            if (data.error) return;
            
            const b = data.surrealdb_binary;
            setStatus('health-binary', b.installed, b.installed ? b.version : 'Not installed');
            
            const s = data.surrealdb_server;
            setStatus('health-server', s.running, s.running ? 'Running on :8000' : 'Not running');
            
            const sc = data.schema;
            setStatus('health-schema', sc.initialized, sc.initialized ? 'Initialized' : sc.error || 'Not initialized');
            
            const p = data.python_deps;
            setStatus('health-python', p.ok, p.ok ? 'All installed' : 'Missing deps');
        }
        
        async function loadStats() {
            const data = await api('stats');
            if (data.error) {
                document.getElementById('stat-facts').textContent = '!';
                return;
            }
            document.getElementById('stat-facts').textContent = data.facts || 0;
            document.getElementById('stat-entities').textContent = data.entities || 0;
            document.getElementById('stat-relations').textContent = data.relationships || 0;
            document.getElementById('stat-confidence').textContent = data.avg_confidence || '-';
        }
        
        async function runMaintenance(op) {
            const log = document.getElementById('maintenance-log');
            log.style.display = 'block';
            log.textContent = 'Running ' + op + '...';
            
            const data = await api('maintenance/' + op, 'POST');
            log.textContent = JSON.stringify(data, null, 2);
            
            if (data.success) {
                toast('Maintenance complete', 'success');
                loadStats();
            } else {
                toast('Maintenance failed: ' + (data.error || 'unknown'), 'error');
            }
        }
        
        async function autoRepair() {
            toast('Running auto-repair...');
            const log = document.getElementById('install-log');
            log.style.display = 'block';
            log.textContent = 'Starting auto-repair...\\n';
            
            const data = await api('repair', 'POST');
            log.textContent = JSON.stringify(data, null, 2);
            
            if (data.success) {
                toast('System repaired successfully!', 'success');
            } else {
                toast('Some issues remain - check log', 'error');
            }
            loadHealth();
            loadStats();
        }
        
        async function installBinary() {
            toast('Installing SurrealDB...');
            const data = await api('install/binary', 'POST');
            showInstallLog(data);
            loadHealth();
        }
        
        async function installPython() {
            toast('Installing Python deps...');
            const data = await api('install/python', 'POST');
            showInstallLog(data);
            loadHealth();
        }
        
        async function startServer() {
            toast('Starting server...');
            const data = await api('install/start', 'POST');
            showInstallLog(data);
            loadHealth();
        }
        
        async function initSchema() {
            toast('Initializing schema...');
            const data = await api('install/schema', 'POST');
            showInstallLog(data);
            loadHealth();
            loadStats();
        }
        
        function showInstallLog(data) {
            const log = document.getElementById('install-log');
            log.style.display = 'block';
            log.textContent = JSON.stringify(data, null, 2);
            if (data.success) toast('Success!', 'success');
            else toast('Failed - check log', 'error');
        }
        
        // Initial load
        loadHealth();
        loadStats();
    </script>
</body>
</html>
"""


class MemoryUIHandler(SimpleHTTPRequestHandler):
    """HTTP handler for the memory UI."""
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
    
    def send_json(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/' or path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
            
        elif path == '/api/health':
            self.send_json(get_full_health())
            
        elif path == '/api/stats':
            self.send_json(asyncio.run(get_stats()))
            
        else:
            self.send_error(404)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/api/repair':
            self.send_json(auto_repair())
            
        elif path == '/api/install/binary':
            self.send_json(install_surrealdb())
            
        elif path == '/api/install/python':
            self.send_json(install_python_deps())
            
        elif path == '/api/install/start':
            self.send_json(start_surrealdb())
            
        elif path == '/api/install/schema':
            self.send_json(init_schema())
            
        elif path.startswith('/api/maintenance/'):
            op = path.split('/')[-1]
            self.send_json(asyncio.run(run_maintenance(op)))
            
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def main():
    parser = argparse.ArgumentParser(description="SurrealDB Memory Web UI")
    parser.add_argument("--port", type=int, default=8765, help="Port to serve on")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    args = parser.parse_args()
    
    server = HTTPServer((args.host, args.port), MemoryUIHandler)
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           SurrealDB Memory - Management UI                  ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   Open in browser:  http://{args.host}:{args.port}               ║
║                                                              ║
║   Features:                                                  ║
║     • Health monitoring                                      ║
║     • One-click installation                                 ║
║     • Auto-repair                                            ║
║     • Maintenance operations                                 ║
║     • Statistics dashboard                                   ║
║                                                              ║
║   Press Ctrl+C to stop                                       ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
