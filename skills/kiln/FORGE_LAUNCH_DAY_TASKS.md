# Forge Launch Day Tasks

When Adam says "go", follow this checklist to merge Forge into Kiln. Everything lands behind `KILN_ENABLE_FORGE=1` — zero impact on existing Kiln users until the flag is flipped.

**Estimated time: ~2.5 hours**

---

## Pre-Flight (10 min)

- [ ] `git checkout main && git pull` on Kiln repo
- [ ] `cd kiln && python3 -m pytest tests/ -x -q` — baseline passes
- [ ] `cd .forge && python3 -m pytest tests/ -x -q` — Forge tests pass (4,078+)
- [ ] Verify advance work is in place:
  - [ ] `_error_dict()` / `_success_dict()` helpers aligned in `.forge/src/forge/server.py`
  - [ ] `register_forge_tools()` function exists in `.forge/src/forge/server.py`
  - [ ] `register_forge_commands()` function exists in `.forge/src/forge/cli.py`
  - [ ] `_FORGE_ENABLED` flag exists in both files

---

## Step 1: Create directory structure (2 min)

```bash
mkdir -p kiln/src/kiln/forge/{devices,safety,data,fulfillment,marketplaces,generation,gateway,payments}
mkdir -p kiln/tests/forge
```

---

## Step 2: Copy source files (5 min)

```bash
# Core modules
cp .forge/src/forge/*.py kiln/src/kiln/forge/

# Subdirectories
cp .forge/src/forge/devices/*.py kiln/src/kiln/forge/devices/
cp .forge/src/forge/safety/*.py kiln/src/kiln/forge/safety/
cp .forge/src/forge/data/*.json kiln/src/kiln/forge/data/
cp .forge/src/forge/fulfillment/*.py kiln/src/kiln/forge/fulfillment/
cp .forge/src/forge/marketplaces/*.py kiln/src/kiln/forge/marketplaces/
cp .forge/src/forge/generation/*.py kiln/src/kiln/forge/generation/
cp .forge/src/forge/gateway/*.py kiln/src/kiln/forge/gateway/
cp .forge/src/forge/payments/*.py kiln/src/kiln/forge/payments/

# Tests
cp .forge/tests/*.py kiln/tests/forge/
cp .forge/tests/conftest.py kiln/tests/forge/conftest.py
```

---

## Step 3: Rewrite imports (10 min)

```bash
# Source files
find kiln/src/kiln/forge/ -name "*.py" -exec sed -i '' 's/from forge\./from kiln.forge./g' {} +
find kiln/src/kiln/forge/ -name "*.py" -exec sed -i '' 's/import forge\./import kiln.forge./g' {} +

# Test files
find kiln/tests/forge/ -name "*.py" -exec sed -i '' 's/from forge\./from kiln.forge./g' {} +
find kiln/tests/forge/ -name "*.py" -exec sed -i '' 's/import forge\./import kiln.forge./g' {} +
find kiln/tests/forge/ -name "*.py" -exec sed -i '' 's/import forge$/import kiln.forge/g' {} +
```

Reference: `.forge/IMPORT_REWRITE_MAP.md` for the full list of imports.

---

## Step 4: Wire server.py (15 min)

Add to `kiln/src/kiln/server.py` before `if __name__` / end of file:

```python
# ---------------------------------------------------------------------------
# Forge multi-device tools (gated behind KILN_ENABLE_FORGE=1)
# ---------------------------------------------------------------------------
_FORGE_ENABLED = os.environ.get("KILN_ENABLE_FORGE", "").lower() in ("1", "true", "yes")
if _FORGE_ENABLED:
    try:
        from kiln.forge.server import register_forge_tools
        _forge_count = register_forge_tools(mcp)
        logger.info("Forge multi-device tools enabled (%d tools)", _forge_count)
    except ImportError:
        logger.warning("KILN_ENABLE_FORGE=1 but kiln.forge package not found")
```

Then update Forge's `server.py` to remove its own `mcp = FastMCP(...)` line and use the one passed via `register_forge_tools()`.

---

## Step 5: Wire CLI (5 min)

Add to `kiln/src/kiln/cli/main.py` after existing command registrations:

```python
_FORGE_ENABLED = os.environ.get("KILN_ENABLE_FORGE", "").lower() in ("1", "true", "yes")
if _FORGE_ENABLED:
    try:
        from kiln.forge.cli import register_forge_commands
        register_forge_commands(cli)
    except ImportError:
        pass
```

All Forge commands become available as `kiln forge <command>`.

---

## Step 6: Persistence schema merge (10 min)

Add to `kiln/src/kiln/persistence.py` inside `KilnDB._ensure_schema()`:

```python
# Forge multi-device tables (schema always present, populated when FORGE enabled)
cur.executescript("""
    CREATE TABLE IF NOT EXISTS device_jobs (
        job_id TEXT PRIMARY KEY,
        file_name TEXT NOT NULL,
        device_name TEXT,
        device_type TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'queued',
        submitted_by TEXT,
        priority INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        started_at TEXT,
        completed_at TEXT,
        error TEXT,
        metadata_json TEXT DEFAULT '{}',
        config_json TEXT DEFAULT '{}'
    );
    CREATE TABLE IF NOT EXISTS device_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT NOT NULL,
        device_name TEXT,
        device_type TEXT,
        timestamp TEXT NOT NULL,
        data_json TEXT DEFAULT '{}',
        source TEXT
    );
    CREATE TABLE IF NOT EXISTS device_job_outcomes (
        outcome_id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT UNIQUE,
        device_name TEXT,
        device_type TEXT,
        file_name TEXT,
        file_hash TEXT,
        material_type TEXT,
        outcome TEXT NOT NULL,
        quality_grade TEXT,
        failure_mode TEXT,
        settings_json TEXT DEFAULT '{}',
        environment_json TEXT DEFAULT '{}',
        notes TEXT,
        agent_id TEXT,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS material_inventory (
        material_id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_type TEXT NOT NULL,
        name TEXT NOT NULL,
        quantity_remaining REAL,
        unit TEXT,
        cost_per_unit REAL,
        expiry_date TEXT,
        added_at TEXT NOT NULL,
        last_used_at TEXT
    );
    CREATE TABLE IF NOT EXISTS forge_agent_memory (
        key TEXT NOT NULL,
        device_type TEXT NOT NULL,
        value_json TEXT DEFAULT '{}',
        created_at TEXT NOT NULL,
        updated_at TEXT,
        PRIMARY KEY (key, device_type)
    );
    CREATE TABLE IF NOT EXISTS device_maintenance (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_name TEXT NOT NULL,
        device_type TEXT NOT NULL,
        maintenance_type TEXT NOT NULL,
        description TEXT,
        performed_at TEXT NOT NULL,
        next_due_at TEXT,
        performed_by TEXT
    );
    CREATE TABLE IF NOT EXISTS job_annotations (
        annotation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT NOT NULL,
        note TEXT NOT NULL,
        tags_json TEXT DEFAULT '[]',
        created_at TEXT NOT NULL
    );
""")
```

**Critical**: Forge's `agent_memory` is renamed to `forge_agent_memory` to avoid collision with Kiln's existing `agent_memory` table (different schema). Update the table name reference in `kiln/src/kiln/forge/persistence.py` to match.

Also add the indexes from `.forge/src/forge/persistence.py` (lines 199-237).

---

## Step 7: pyproject.toml (2 min)

In `kiln/pyproject.toml`, update package-data:

```toml
[tool.setuptools.package-data]
kiln = ["data/*.json", "forge/data/*.json", "py.typed"]
```

No new external dependencies needed — Forge's only dependency is `kiln3d` (the host package).

---

## Step 8: Compile check (5 min)

```bash
find kiln/src/kiln/forge/ -name "*.py" | xargs -I{} python3 -m py_compile {}
```

Fix any import errors from the namespace change.

---

## Step 9: Test — Forge OFF (10 min)

```bash
cd kiln && python3 -m pytest tests/ -x -q --ignore=tests/forge
```

All existing Kiln tests must pass. Zero Forge impact.

---

## Step 10: Test — Forge ON (15 min)

```bash
cd kiln && KILN_ENABLE_FORGE=1 python3 -m pytest tests/ -x -q
cd kiln && KILN_ENABLE_FORGE=1 python3 -m pytest tests/forge/ -x -q
```

All 4,078+ Forge tests + all Kiln tests must pass together.

---

## Step 11: Lint (5 min)

```bash
cd kiln && ruff check src/kiln/forge/ --fix
cd kiln && ruff format src/kiln/forge/
```

---

## Step 12: Smoke test (5 min)

- [ ] `kiln serve` starts normally — no Forge tools visible
- [ ] `KILN_ENABLE_FORGE=1 kiln serve` starts — 185 + 193 = 378 tools
- [ ] `KILN_ENABLE_FORGE=1 kiln forge --help` shows all Forge commands
- [ ] `kiln forge --help` without flag shows error or "Forge not enabled"

---

## Step 13: Documentation (20 min)

- [ ] **README.md**: Add back "Beyond 3D Printing" section (was scrubbed for stealth). Add feature flag instructions.
- [ ] **docs/WHITEPAPER.md**: Restore section 11 (Physical Fabrication Generalization). Add adapter hierarchy details.
- [ ] **docs/PROJECT_DOCS.md**: Restore DeviceType/DeviceAdapter descriptions. Add Forge module catalog, adapter list, safety docs.
- [ ] **docs/LITEPAPER.md**: Add multi-device vision paragraph.
- [ ] **.dev/COMPLETED_TASKS.md**: Append "Forge multi-device manufacturing merged into Kiln"
- [ ] **.dev/TASKS.md**: Remove Forge merge task if listed

---

## Step 14: Commit + push (5 min)

```bash
git add -A
git commit -m "Merge Forge multi-device manufacturing into Kiln

Adds SLA, laser, and CNC device support as kiln.forge subpackage.
193 new MCP tools + 32 CLI commands, gated behind KILN_ENABLE_FORGE=1.
12 new device adapters: FormLabs, Prusa SL, Chitubox, Glowforge,
LightBurn, xTool, GRBL, LinuxCNC, Carbide Motion + simulators.
7 new persistence tables for device jobs, events, outcomes, materials,
maintenance, and annotations.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"

git push
```

---

## Phase 2: Consolidate Infrastructure (later, separate sprint)

- [ ] Merge `ForgePersistence` methods into `KilnDB` (unified DB)
- [ ] Merge `DeviceQueue` into Kiln's queue (add `device_type` column)
- [ ] Merge `DeviceRegistry` into Kiln's registry (accept any adapter type)
- [ ] Merge event types, schedulers, webhooks, auth into single implementations
- [ ] Factor out `_error_dict()`/`_success_dict()` into shared `kiln/_response.py`

## Phase 3: Delete the Seam (later)

- [ ] Remove `KILN_ENABLE_FORGE` flag — all tools become first-class
- [ ] Flatten CLI: `kiln forge status` → `kiln status` shows all device types
- [ ] Update FastMCP instructions to include multi-device guidance
- [ ] Remove "Forge" branding from all user-facing docs — it's just Kiln
- [ ] Archive `forge-internal` repo
