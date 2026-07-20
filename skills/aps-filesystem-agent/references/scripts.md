# APS Knowledge Base — Utility Scripts

## rebuild_index.py

Full source for the vector index rebuild script.
Place at `aps_knowledge_base/scripts/rebuild_index.py`.

```python
#!/usr/bin/env python3
"""
Rebuilds the ChromaDB vector index from scratch by scanning all JSON files
in the domain_rules/ directory. Run this after bulk imports or to fix drift.

Usage:
    python aps_knowledge_base/scripts/rebuild_index.py
    python aps_knowledge_base/scripts/rebuild_index.py --kb-path /path/to/kb
"""

import argparse
import json
import pathlib
import sys

def rebuild(kb_path: str = "aps_knowledge_base"):
    try:
        import chromadb
    except ImportError:
        print("chromadb not installed. Run: pip install chromadb")
        sys.exit(1)

    kb = pathlib.Path(kb_path)
    if not kb.exists():
        print(f"Knowledge base not found at {kb_path}")
        sys.exit(1)

    client = chromadb.PersistentClient(path=str(kb / ".chromadb"))

    # Delete and recreate for a clean rebuild
    try:
        client.delete_collection("domain_rules")
    except Exception:
        pass
    collection = client.create_collection(
        "domain_rules",
        metadata={"hnsw:space": "cosine"}
    )

    ids, documents, metadatas = [], [], []

    for rule_file in sorted((kb / "domain_rules").rglob("*.json")):
        if rule_file.name.startswith("_"):
            continue
        try:
            rule = json.loads(rule_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  SKIP (JSON error): {rule_file} — {e}")
            continue

        rule_id = rule.get("id")
        if not rule_id:
            print(f"  SKIP (no id): {rule_file}")
            continue

        tags = rule.get("metadata", {}).get("tags", [])
        text = " ".join(filter(None, [
            rule.get("name", ""),
            rule.get("description", ""),
            " ".join(tags)
        ]))

        meta = {
            "rule_id": rule_id,
            "name": rule.get("name", ""),
            "status": rule.get("status", "active"),
            "constraint_type": rule.get("constraint_type", "soft"),
            "rule_type": rule.get("type", ""),
            "file_path": str(rule_file.relative_to(kb)),
            "use_count": int(rule.get("metadata", {}).get("use_count", 0)),
            "confidence": float(rule.get("metadata", {}).get("confidence", 0.9))
        }

        ids.append(rule_id)
        documents.append(text)
        metadatas.append(meta)

    if ids:
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        print(f"Indexed {len(ids)} rules into domain_rules collection.")
    else:
        print("No rules found to index.")

    # Rebuild the _index.json as well
    _rebuild_index_json(kb)
    print("Done.")


def _rebuild_index_json(kb: pathlib.Path):
    import datetime
    entries = []
    for rule_file in sorted((kb / "domain_rules").rglob("*.json")):
        if rule_file.name.startswith("_"):
            continue
        try:
            rule = json.loads(rule_file.read_text(encoding="utf-8"))
            entries.append({
                "id": rule.get("id"),
                "name": rule.get("name", ""),
                "type": rule.get("type", ""),
                "status": rule.get("status", "active"),
                "file_path": str(rule_file.relative_to(kb)),
                "tags": rule.get("metadata", {}).get("tags", []),
                "use_count": rule.get("metadata", {}).get("use_count", 0)
            })
        except Exception:
            pass

    index = {
        "last_rebuilt": datetime.datetime.utcnow().isoformat() + "Z",
        "total_active": sum(1 for e in entries if e["status"] == "active"),
        "rules": entries
    }
    (kb / "domain_rules/_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--kb-path", default="aps_knowledge_base")
    args = parser.parse_args()
    rebuild(args.kb_path)
```

---

## refresh_rule_index.py (inline helper)

Used inside `confirm_proposal()` and `deprecate_rule()` to keep `_index.json`
current without a full rebuild. Paste this helper into your agent code:

```python
def _refresh_rule_index():
    import datetime
    entries = []
    for rule_file in sorted((kb / "domain_rules").rglob("*.json")):
        if rule_file.name.startswith("_"):
            continue
        try:
            rule = json.loads(rule_file.read_text(encoding="utf-8"))
            entries.append({
                "id": rule.get("id"),
                "name": rule.get("name", ""),
                "type": rule.get("type", ""),
                "status": rule.get("status", "active"),
                "file_path": str(rule_file.relative_to(kb)),
                "tags": rule.get("metadata", {}).get("tags", []),
                "use_count": rule.get("metadata", {}).get("use_count", 0)
            })
        except Exception:
            pass

    index = {
        "last_rebuilt": datetime.datetime.utcnow().isoformat() + "Z",
        "total_active": sum(1 for e in entries if e["status"] == "active"),
        "rules": entries
    }
    (kb / "domain_rules/_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2)
    )
```

---

## increment_use_count.py (inline helper)

Called after each scheduling session to track rule usage frequency:

```python
def _increment_use_count(rule_id: str):
    import datetime
    for rule_file in (kb / "domain_rules").rglob(f"{rule_id}.json"):
        rule = json.loads(rule_file.read_text(encoding="utf-8"))
        rule["metadata"]["use_count"] = rule["metadata"].get("use_count", 0) + 1
        rule["metadata"]["last_used_at"] = datetime.datetime.utcnow().isoformat() + "Z"
        rule_file.write_text(json.dumps(rule, ensure_ascii=False, indent=2))

        # also update chromadb metadata
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(kb / ".chromadb"))
            col = client.get_collection("domain_rules")
            existing = col.get(ids=[rule_id])["metadatas"]
            if existing:
                updated_meta = {**existing[0], "use_count": rule["metadata"]["use_count"]}
                col.update(ids=[rule_id], metadatas=[updated_meta])
        except Exception:
            pass
        break
```
