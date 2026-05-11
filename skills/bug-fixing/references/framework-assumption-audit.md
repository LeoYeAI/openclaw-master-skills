# Framework Assumption Audit Protocol

> **Iron Rule 12**: When a fix involves third-party framework behavior, you MUST verify the actual semantics before implementing the fix.

## Table of Contents

- [Trigger Conditions](#trigger-conditions)
- [Audit Process](#audit-process)
- [Common Pitfall Pattern Library](#common-pitfall-pattern-library)
- [Quick Verification Techniques](#quick-verification-techniques)
- [Output Template](#output-template)
- [Real Cases](#real-cases)

---

## Trigger Conditions

When the fix meets **any** of the following conditions, a framework assumption audit is MANDATORY:

| Condition | Example |
|-----------|---------|
| Fix depends on framework/library loading, ordering, or priority behavior | env file load order, middleware execution order |
| Fix involves framework-internal merge/override logic | dict.update(), deepmerge, config override |
| Fix involves framework async/event loop behavior | asyncio event loop policy, subprocess support |
| Fix depends on ORM query/lazy loading/transaction semantics | SQLAlchemy lazy loading, session scope |
| Fix involves serialization/deserialization field handling | Pydantic model_dump(exclude_unset=True), JSON serialization order |
| Code comment claims framework behavior is X without citing source code evidence | "First file has highest priority" etc. without source reference |

---

## Audit Process

### Step 1: Identify Assumptions

List all assumptions about third-party framework behavior in the fix:

```markdown
## Framework Assumption List

| # | Assumption | Framework/Library | Verification Status |
|---|-----------|-------------------|---------------------|
| 1 | env files load in list order, first has priority | pydantic-settings | ☐ |
| 2 | asyncio supports subprocess on Windows | Python asyncio | ☐ |
```

### Step 2: Verify by Reading Source Code

For each assumption, find the actual implementation in the framework source:

1. **Locate source code**: Find relevant module in `venv/Lib/site-packages/` or `node_modules/`
2. **Trace call chain**: From the API entry point you use, trace to the actual behavior
3. **Document findings**: Note the source file path and line numbers

```markdown
## Verification Results

| # | Assumption | Actual Behavior | Source Evidence | Conclusion |
|---|-----------|----------------|-----------------|------------|
| 1 | First file has priority | dict.update() = last file wins | dotenv.py:97-103 | ❌ Assumption wrong |
| 2 | Windows supports subprocess | Needs ProactorEventLoop | base_events.py:528 | ⚠️ Conditional |
```

### Step 3: Document in Code Comments

Add verified semantics to the fix code:

```python
# NOTE: pydantic-settings uses dict.update() when iterating env files,
# so the **last** file in the tuple has the **highest** priority.
# Verified: pydantic_settings/sources/providers/dotenv.py:97-103
```

---

## Common Pitfall Pattern Library

### 1. Config File Load Order

| Framework | Common Assumption | Actual Behavior |
|-----------|-------------------|-----------------|
| **pydantic-settings** | First env file has priority | `dict.update()` → last file wins |
| **dotenv (Node.js)** | Later loads override earlier | By default, does NOT override existing vars |
| **Spring Boot** | application.yml has priority | profile-specific overrides default |
| **Vite** | .env has priority | .env.local > .env.mode > .env |

### 2. ORM Query Behavior

| Framework | Common Assumption | Actual Behavior |
|-----------|-------------------|-----------------|
| **SQLAlchemy** | Relationships auto-load | Default is lazy loading, can cause N+1 |
| **SQLAlchemy** | session.commit() refreshes objects | Need session.refresh() to get latest values |
| **Django ORM** | filter() returns a copy | Returns new QuerySet, lazily evaluated |

### 3. Async/Event Loop

| Framework | Common Assumption | Actual Behavior |
|-----------|-------------------|-----------------|
| **asyncio (Windows)** | subprocess supported on all platforms | SelectorEventLoop doesn't support it, need ProactorEventLoop |
| **uvicorn --reload** | Uses default event loop | May switch event loop policy |
| **aiohttp** | Session can be shared across threads | Bound to the event loop that created it |

### 4. Serialization/Deserialization

| Framework | Common Assumption | Actual Behavior |
|-----------|-------------------|-----------------|
| **Pydantic** | model_dump() includes all fields | exclude_unset=True only includes explicitly set fields |
| **JSON.parse** | Preserves key order | ES2015+ preserves insertion order, but numeric keys first |
| **msgpack** | Preserves dict order | Depends on version and config |

---

## Quick Verification Techniques

### Technique 1: grep Framework Source

```bash
# Search for key implementation in venv
grep -n "def _read_env_files" venv/Lib/site-packages/pydantic_settings/**/*.py
grep -n "dict.update\|\.update(" venv/Lib/site-packages/pydantic_settings/**/*.py
```

### Technique 2: Write a Minimal Test Script

```python
# test_env_priority.py - Verify env file load priority
import tempfile, os
from pathlib import Path

# Create two temp env files
with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f1:
    f1.write("MY_VAR=from_file_1\n")
    file1 = f1.name

with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f2:
    f2.write("MY_VAR=from_file_2\n")
    file2 = f2.name

from pydantic_settings import BaseSettings, SettingsConfigDict

class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(file1, file2))
    MY_VAR: str = ""

s = TestSettings()
print(f"Result: {s.MY_VAR}")  # See if it's file_1 or file_2
os.unlink(file1)
os.unlink(file2)
```

### Technique 3: Read Framework Source in IDE

In your IDE, Ctrl+Click to jump to the framework function definition and read the implementation line by line.
Focus on loops, merging, and override-related code patterns.

---

## Output Template

After every framework assumption audit, MUST output the following:

```markdown
## Framework Assumption Audit Results

**Framework/Library**: [name + version]

### Assumption Verification

| # | Assumption | Verification Method | Actual Behavior | Conclusion |
|---|-----------|--------------------|-----------------|-----------| 
| 1 | [assumption content] | [source reading/test script] | [actual behavior] | ✅/❌ |

### Impact on Fix
- [Adjustments to fix approach based on verification results]
```

---

## Real Cases

### Case 1: pydantic-settings env File Priority (BUG-014)

**Assumption**: In `env_file=("file_a", "file_b")`, `file_a` has highest priority
**Actual**: `DotEnvSettingsSource._read_env_files()` uses `dict.update()`, last file overrides previous ones
**Consequence**: env file priority was reversed, causing P1 regression (inconsistent encryption key)
**Lesson**: Cannot assume priority direction by "intuition", must read framework source to verify

### Case 2: Windows asyncio subprocess Support (BUG-017)

**Assumption**: `asyncio.create_subprocess_exec()` available on all platforms
**Actual**: SelectorEventLoop on Windows doesn't support subprocess, raises NotImplementedError
**Consequence**: Playwright initialization failure, producing noise logs
**Lesson**: For cross-platform async operations, must check event loop policy compatibility
