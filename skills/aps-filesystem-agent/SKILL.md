---
name: aps-filesystem-agent
description: >
  Use this skill whenever an APS (production scheduling) agent needs to interact
  with a local filesystem-based knowledge base. Triggers include: reading or
  searching APS rules, loading client memory or shop floor configurations,
  proposing new rules to the knowledge base, updating or deprecating existing
  knowledge, querying decision history, rebuilding the vector index, or any
  task involving the aps_knowledge_base/ directory structure. Also use when the
  agent needs to understand what knowledge is available before making scheduling
  decisions, or when it wants to persist something learned in a conversation.
  Always consult this skill before reading from or writing to any part of the
  APS knowledge base filesystem.
---

# APS Filesystem Agent Skill

This skill teaches an APS scheduling agent how to navigate, query, and maintain
a local filesystem-based knowledge base. The filesystem is the single source of
truth for all domain rules, client memory, and problem schemas. A vector index
sits on top for semantic retrieval, and Git tracks every change for auditability.

## Knowledge base layout

```
aps_knowledge_base/
├── .git/                     ← version history, never touch manually
├── domain_rules/             ← APS rules extracted from conversations
│   ├── _index.json           ← master rule registry (always update this)
│   ├── machine_rules/
│   ├── operator_rules/
│   └── material_rules/
├── client_memory/            ← persistent understanding of this customer
│   ├── _profile.json         ← shop floor + planning process + preferences
│   ├── shop_floor/
│   ├── planning_process/
│   └── decision_history/     ← one file per scheduling session
├── problem_schemas/          ← modeling templates by problem type
├── solver_configs/           ← solver parameters and routing thresholds
├── pending_review/           ← proposed knowledge awaiting human approval
└── logs/
    ├── decisions/            ← audit trail of scheduling decisions
    └── knowledge_changes/    ← audit trail of knowledge writes
```

Before doing anything, confirm the knowledge base root exists:
```bash
ls aps_knowledge_base/ 2>/dev/null || echo "Knowledge base not initialized"
```

If it doesn't exist yet, initialize it (see "Initializing a new knowledge base" below).

---

## Reading knowledge

### Load client profile

Always load the client profile first — it tells you the shop floor topology,
planning process, and output preferences that frame every other decision.

```python
import json, pathlib

kb = pathlib.Path("aps_knowledge_base")
profile = json.loads((kb / "client_memory/_profile.json").read_text())
shop = profile["shop_floor"]        # type, stages, machines_per_stage, etc.
prefs = profile["preferences"]      # primary_objective, output_format, etc.
```

### Semantic retrieval of rules (preferred method)

Use semantic search when you know *what you need* but not *which file has it*.
This requires the vector index to be built (see "Maintaining the vector index").

```python
import chromadb

client = chromadb.PersistentClient(path="aps_knowledge_base/.chromadb")
collection = client.get_collection("domain_rules")

results = collection.query(
    query_texts=["operator HSE certification machine maintenance"],
    n_results=5,
    where={"status": "active"}          # only retrieve active rules
)

# results["ids"], results["documents"], results["metadatas"]
for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"[{meta['rule_id']}] {meta['name']}: {doc}")
```

### Direct rule lookup by ID

When you already know the rule ID (e.g., from a decision log):

```python
rule_path = kb / f"domain_rules/{category}/{rule_id}.json"
rule = json.loads(rule_path.read_text())
```

### Load all active rules for a scheduling session

Inject the Top-K most relevant rules into the scheduling context:

```python
def get_relevant_rules(query: str, top_k: int = 5) -> list[dict]:
    collection = client.get_collection("domain_rules")
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where={"status": "active"}
    )
    rules = []
    for rule_id, meta in zip(results["ids"][0], results["metadatas"][0]):
        path = kb / meta["file_path"]
        rules.append(json.loads(path.read_text()))
    return rules
```

### Load a problem schema template

```python
problem_type = "flow_shop"   # or job_shop, rcpsp, re_entrant
schema = json.loads((kb / f"problem_schemas/{problem_type}.json").read_text())
```

### Read session decision history

```python
history_dir = kb / "client_memory/decision_history"
sessions = sorted(history_dir.glob("session_*.json"), reverse=True)
last_session = json.loads(sessions[0].read_text()) if sessions else {}
```

---

## Proposing new knowledge (write path)

**The agent NEVER writes directly to the main knowledge directories.**
All new knowledge goes to `pending_review/` first, then a human confirms.

### Propose a new APS rule

Call this whenever you extract a new constraint or rule from a conversation:

```python
import json, pathlib, datetime

def propose_rule(rule_content: dict, source_quote: str, session_id: str):
    kb = pathlib.Path("aps_knowledge_base")
    pending = kb / "pending_review"
    pending.mkdir(exist_ok=True)

    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    proposal = {
        **rule_content,
        "status": "proposed",
        "metadata": {
            **rule_content.get("metadata", {}),
            "created_at": datetime.datetime.utcnow().isoformat() + "Z",
            "created_by": "ai_agent",
            "confirmed_by": None,
            "source_session": session_id,
            "source_quote": source_quote,
            "use_count": 0,
            "confidence": 0.9
        }
    }

    out_path = pending / f"proposed_{rule_content['id']}_{ts}.json"
    out_path.write_text(json.dumps(proposal, ensure_ascii=False, indent=2))

    # Return the summary to show the user for confirmation
    return {
        "proposal_file": str(out_path),
        "rule_id": rule_content["id"],
        "name": rule_content["name"],
        "description": rule_content["description"]
    }
```

After calling this, **always present the proposal to the user** with a
confirmation prompt before moving on. Format it like this:

```
建议将以下内容加入知识库：

规则ID: {rule_id}
名称: {name}
描述: {description}
来源: "{source_quote}"

[确认入库] [修改后入库] [忽略本次]
```

Wait for explicit confirmation before proceeding to `confirm_proposal()`.

### Propose an update to client memory

```python
def propose_memory_update(memory_type: str, updates: dict, reason: str):
    """
    memory_type: 'shop_floor' | 'planning_process' | 'preferences'
    """
    pending = kb / "pending_review"
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    proposal = {
        "type": "client_memory_update",
        "memory_type": memory_type,
        "updates": updates,
        "reason": reason,
        "proposed_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    out_path = pending / f"proposed_memory_{memory_type}_{ts}.json"
    out_path.write_text(json.dumps(proposal, ensure_ascii=False, indent=2))
    return str(out_path)
```

---

## Confirming proposals (after human approval)

Only call these functions **after** the user has explicitly confirmed in chat.

```python
def confirm_proposal(proposal_file: str, confirmed_by: str):
    """Move a proposal from pending_review into the live knowledge base."""
    kb = pathlib.Path("aps_knowledge_base")
    proposal_path = pathlib.Path(proposal_file)
    proposal = json.loads(proposal_path.read_text())

    if proposal.get("type") == "client_memory_update":
        _apply_memory_update(proposal, confirmed_by)
    else:
        _apply_rule(proposal, confirmed_by)

    # Remove from pending
    proposal_path.unlink()

    # Update vector index and commit
    _update_vector_index(proposal)
    _git_commit(proposal, confirmed_by)


def _apply_rule(proposal: dict, confirmed_by: str):
    rule_type = proposal.get("type", "general")
    category_map = {
        "machine_constraint": "machine_rules",
        "operator_constraint": "operator_rules",
        "material_constraint": "material_rules",
    }
    subdir = category_map.get(rule_type, "machine_rules")
    dest = kb / f"domain_rules/{subdir}/{proposal['id']}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)

    proposal["status"] = "active"
    proposal["metadata"]["confirmed_by"] = confirmed_by
    proposal["metadata"]["confirmed_at"] = (
        datetime.datetime.utcnow().isoformat() + "Z"
    )
    dest.write_text(json.dumps(proposal, ensure_ascii=False, indent=2))

    # Refresh the index file
    _refresh_rule_index()


def _apply_memory_update(proposal: dict, confirmed_by: str):
    profile_path = kb / "client_memory/_profile.json"
    profile = json.loads(profile_path.read_text())
    memory_type = proposal["memory_type"]

    if memory_type not in profile:
        profile[memory_type] = {}
    profile[memory_type].update(proposal["updates"])
    profile["last_updated"] = datetime.datetime.utcnow().isoformat() + "Z"

    profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2))
```

---

## Maintaining the vector index

The vector index must stay in sync with the filesystem. Rebuild it whenever
rules are added, updated, or deprecated.

### Incremental update (after a single rule change)

```python
def _update_vector_index(rule: dict):
    import chromadb
    client = chromadb.PersistentClient(path="aps_knowledge_base/.chromadb")

    try:
        collection = client.get_or_create_collection("domain_rules")
    except Exception:
        collection = client.create_collection("domain_rules")

    text = f"{rule['name']} {rule['description']} {' '.join(rule.get('metadata', {}).get('tags', []))}"
    meta = {
        "rule_id": rule["id"],
        "name": rule["name"],
        "status": rule.get("status", "active"),
        "constraint_type": rule.get("constraint_type", "soft"),
        "file_path": f"domain_rules/{_infer_subdir(rule)}/{rule['id']}.json"
    }
    collection.upsert(ids=[rule["id"]], documents=[text], metadatas=[meta])
```

### Full rebuild (use after bulk changes or first setup)

```bash
python aps_knowledge_base/scripts/rebuild_index.py
```

See `references/scripts.md` for the full rebuild script content.

---

## Git version management

Every confirmed knowledge change gets a Git commit automatically.

```python
import subprocess

def _git_commit(item: dict, confirmed_by: str):
    kb_path = "aps_knowledge_base"
    item_id = item.get("id", item.get("memory_type", "unknown"))
    item_type = item.get("type", "update")

    action = "add" if item.get("status") == "active" else "update"
    msg = f"{action}: {item_id} {item_type} ({confirmed_by})"

    subprocess.run(["git", "-C", kb_path, "add", "-A"], check=True)
    subprocess.run(["git", "-C", kb_path, "commit", "-m", msg], check=True)
```

Commit message conventions:
```
add: rule_003 operator_constraint (big_boss)
update: client_memory shop_floor topology (plant_manager)
deprecate: rule_002 machine_a3 calibration - operator left (admin)
restore: rule_002 machine_a3 calibration (admin)
```

To view history for a specific rule:
```bash
git -C aps_knowledge_base log --oneline -- domain_rules/operator_rules/rule_003.json
```

---

## Updating knowledge status

### Deprecate a rule (soft disable — keeps the record)

```python
def deprecate_rule(rule_id: str, reason: str, deprecated_by: str):
    # find the file
    for f in (kb / "domain_rules").rglob(f"{rule_id}.json"):
        rule = json.loads(f.read_text())
        rule["status"] = "deprecated"
        rule["metadata"]["deprecated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
        rule["metadata"]["deprecation_reason"] = reason
        f.write_text(json.dumps(rule, ensure_ascii=False, indent=2))

        # remove from vector index so it won't be retrieved
        client = chromadb.PersistentClient(path="aps_knowledge_base/.chromadb")
        col = client.get_collection("domain_rules")
        col.update(ids=[rule_id], metadatas=[{**col.get(ids=[rule_id])["metadatas"][0], "status": "deprecated"}])

        _git_commit({"id": rule_id, "type": "deprecation"}, deprecated_by)
        _refresh_rule_index()
        return True
    return False
```

### Record a scheduling decision (audit log)

After every scheduling session, persist the decision for future reference:

```python
def log_decision(session_id: str, decision: dict, rules_used: list[str]):
    log_entry = {
        "session_id": session_id,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "decision_summary": decision,
        "triggered_by_rules": rules_used,
        "human_confirmed": True
    }
    log_path = kb / f"client_memory/decision_history/{session_id}.json"
    log_path.write_text(json.dumps(log_entry, ensure_ascii=False, indent=2))

    # Also bump use_count on every rule that was triggered
    for rule_id in rules_used:
        _increment_use_count(rule_id)
```

---

## Knowledge health checks

Run these checks periodically or before a major scheduling session.

```python
def check_knowledge_health() -> dict:
    issues = []
    profile = json.loads((kb / "client_memory/_profile.json").read_text())

    # Check for rules referencing people/machines that no longer exist
    known_operators = profile.get("operators", {}).get("active", [])
    for f in (kb / "domain_rules").rglob("*.json"):
        rule = json.loads(f.read_text())
        if rule.get("status") != "active":
            continue
        for op in rule.get("scope", {}).get("operators", []):
            if op not in known_operators:
                issues.append({
                    "rule_id": rule["id"],
                    "issue": f"references operator '{op}' not in active roster"
                })

    # Flag rules unused for 180+ days
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=180)
    for f in (kb / "domain_rules").rglob("*.json"):
        rule = json.loads(f.read_text())
        if rule.get("status") != "active":
            continue
        last_used = rule.get("metadata", {}).get("last_used_at")
        if last_used and datetime.datetime.fromisoformat(last_used[:-1]) < cutoff:
            issues.append({
                "rule_id": rule["id"],
                "issue": "not used in 180+ days — consider deprecating"
            })

    return {"issues": issues, "checked_at": datetime.datetime.utcnow().isoformat()}
```

---

## Initializing a new knowledge base

If `aps_knowledge_base/` does not exist, bootstrap it:

```bash
mkdir -p aps_knowledge_base/{domain_rules/{machine_rules,operator_rules,material_rules},client_memory/{shop_floor,planning_process,decision_history},problem_schemas,solver_configs,pending_review,logs/{decisions,knowledge_changes},.chromadb}

cd aps_knowledge_base && git init && git commit --allow-empty -m "init: knowledge base"
```

Then create `client_memory/_profile.json` with the shell structure and fill it
in from the conversation (use `propose_memory_update` + confirmation flow).

See `references/schemas.md` for the full JSON schemas for every file type.

---

## Decision checklist before every scheduling session

1. Load `client_memory/_profile.json` — confirm shop floor topology is current
2. Retrieve Top-5 relevant rules via semantic search using the order batch description
3. Check `pending_review/` — if any proposals await, surface them to the user
4. Load the matching `problem_schemas/<type>.json` template
5. After solving, call `log_decision()` with the rules that were triggered
6. If new constraints emerged in conversation, call `propose_rule()` and await confirmation

---

## Reference files

For detailed schemas and the rebuild script, read these when needed:

- `references/schemas.md` — full JSON schemas for rules, client memory, proposals
- `references/scripts.md` — `rebuild_index.py` full source code
