#!/usr/bin/env python3
"""
Knowledge Extraction from Memory Files

Reads MEMORY.md and memory/*.md, uses LLM to extract structured facts,
compares with existing knowledge graph, and updates accordingly.

Usage:
    python3 extract-knowledge.py extract              # Extract from changed files
    python3 extract-knowledge.py extract --full       # Full extraction (all files)
    python3 extract-knowledge.py status               # Show extraction status
    python3 extract-knowledge.py reconcile            # Deep reconciliation (prune stale)
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ============================================
# Configuration
# ============================================

WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
STATE_FILE = Path.home() / ".openclaw" / "memory" / "extraction-state.json"
SESSION_CACHE_FILE = Path.home() / ".openclaw" / "memory" / "session-cache.json"
PROGRESS_FILE = Path.home() / ".openclaw" / "memory" / "extraction-progress.json"

SURREAL_CONFIG = {
    "connection": "http://localhost:8000",
    "namespace": "openclaw",
    "database": "memory",
    "user": "root",
    "password": "root",
}

# Chunking for extraction (larger than embedding chunks)
EXTRACTION_CHUNK_SIZE = 2000  # chars
EXTRACTION_CHUNK_OVERLAP = 200

try:
    from surrealdb import Surreal
    SURREALDB_AVAILABLE = True
except ImportError:
    SURREALDB_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# ============================================
# State Management
# ============================================

def load_state() -> dict:
    """Load extraction state from disk."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except:
            pass
    return {
        "last_extraction": None,
        "file_hashes": {},
        "extraction_count": 0,
        "facts_extracted": 0,
    }

def save_state(state: dict):
    """Save extraction state to disk."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ============================================
# Progress Tracking
# ============================================

def write_progress(phase: str, current: int, total: int, message: str, detail: str = ""):
    """Write progress to file for UI polling."""
    progress = {
        "phase": phase,
        "current": current,
        "total": total,
        "percent": round(current / total * 100) if total > 0 else 0,
        "message": message,
        "detail": detail,
        "timestamp": datetime.now().isoformat(),
    }
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(json.dumps(progress))
    # Also print for log output
    print(f"[{progress['percent']}%] {message}" + (f" - {detail}" if detail else ""))

def clear_progress():
    """Clear progress file when done."""
    if PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()


# ============================================
# File Discovery
# ============================================

def list_memory_files(workspace: Path) -> list[Path]:
    """List all memory files in workspace."""
    files = []
    
    # MEMORY.md
    memory_file = workspace / "MEMORY.md"
    if memory_file.exists():
        files.append(memory_file)
    
    # memory.md (alternative)
    alt_memory = workspace / "memory.md"
    if alt_memory.exists() and alt_memory not in files:
        files.append(alt_memory)
    
    # memory/*.md
    memory_dir = workspace / "memory"
    if memory_dir.exists():
        for f in memory_dir.rglob("*.md"):
            if f.is_file():
                files.append(f)
    
    return files

def hash_file(path: Path) -> str:
    """Get hash of file content."""
    content = path.read_text(encoding="utf-8", errors="ignore")
    return hashlib.sha256(content.encode()).hexdigest()[:16]

def get_changed_files(files: list[Path], state: dict) -> list[Path]:
    """Filter to files that changed since last extraction."""
    changed = []
    for f in files:
        current_hash = hash_file(f)
        stored_hash = state.get("file_hashes", {}).get(str(f))
        if stored_hash != current_hash:
            changed.append(f)
    return changed


# ============================================
# Content Chunking
# ============================================

def chunk_content(content: str, chunk_size: int = EXTRACTION_CHUNK_SIZE, 
                  overlap: int = EXTRACTION_CHUNK_OVERLAP) -> list[dict]:
    """Split content into chunks for extraction."""
    lines = content.split("\n")
    chunks = []
    current_lines = []
    current_size = 0
    start_line = 1
    
    for i, line in enumerate(lines, 1):
        line_size = len(line) + 1
        
        if current_size + line_size > chunk_size and current_lines:
            # Flush current chunk
            chunks.append({
                "text": "\n".join(current_lines),
                "start_line": start_line,
                "end_line": i - 1,
            })
            
            # Overlap: keep some lines
            overlap_lines = []
            overlap_size = 0
            for prev_line in reversed(current_lines):
                if overlap_size + len(prev_line) > overlap:
                    break
                overlap_lines.insert(0, prev_line)
                overlap_size += len(prev_line) + 1
            
            current_lines = overlap_lines
            current_size = overlap_size
            start_line = i - len(overlap_lines)
        
        current_lines.append(line)
        current_size += line_size
    
    # Final chunk
    if current_lines:
        chunks.append({
            "text": "\n".join(current_lines),
            "start_line": start_line,
            "end_line": len(lines),
        })
    
    return chunks


# ============================================
# LLM Extraction
# ============================================

EXTRACTION_PROMPT = """You are extracting structured knowledge from personal notes/memory files.

Given this text, extract discrete facts. For each fact:
1. Write a concise, single-assertion statement
2. Identify entities mentioned (people, projects, concepts, places)
3. Assign confidence (0.0-1.0): 1.0 for definitive statements, lower for uncertain/inferred
4. Mark source: "explicit" if directly stated, "inferred" if derived

Rules:
- Extract only meaningful facts, not meta-commentary
- Keep facts atomic (one assertion per fact)
- Preserve important context in the fact statement
- Skip obvious/trivial information
- If no meaningful facts, return empty array

Text:
---
{content}
---

Return JSON array:
[
  {{
    "content": "fact statement",
    "entities": ["Entity1", "Entity2"],
    "confidence": 0.9,
    "source": "explicit"
  }}
]

Only return the JSON array, no other text."""

def extract_facts_from_chunk(chunk_text: str, file_path: str) -> list[dict]:
    """Use LLM to extract facts from a chunk."""
    if not OPENAI_AVAILABLE:
        return []
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return []
    
    client = openai.OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": EXTRACTION_PROMPT.format(content=chunk_text)}
            ],
            temperature=0.3,
            max_tokens=2000,
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON (handle markdown code blocks)
        if result_text.startswith("```"):
            result_text = re.sub(r"```(?:json)?\n?", "", result_text)
            result_text = result_text.strip()
        
        facts = json.loads(result_text)
        
        # Add file source to each fact
        for fact in facts:
            fact["file_source"] = str(file_path)
        
        return facts
    
    except Exception as e:
        print(f"  Warning: Extraction failed for chunk: {e}", file=sys.stderr)
        return []


# ============================================
# Database Operations
# ============================================

def get_embedding(text: str) -> list[float]:
    """Generate embedding for text."""
    if not OPENAI_AVAILABLE:
        return []
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return []
    
    client = openai.OpenAI(api_key=api_key)
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def find_similar_facts(db, content: str, threshold: float = 0.85) -> list[dict]:
    """Find existing facts similar to content."""
    embedding = get_embedding(content)
    if not embedding:
        return []
    
    # SurrealDB v2.x requires computed fields for ordering
    results = db.query("""
        SELECT id, content, confidence, source,
               vector::similarity::cosine(embedding, $embedding) AS similarity
        FROM fact
        WHERE archived = false
            AND vector::similarity::cosine(embedding, $embedding) > $threshold
        ORDER BY similarity DESC
        LIMIT 5
    """, {"embedding": embedding, "threshold": threshold})
    
    # Results come as flat list of dicts
    return results if isinstance(results, list) else []

def store_fact(db, fact: dict, agent_id: str = "main") -> str:
    """Store a new fact in the database, tagged with the source agent."""
    embedding = get_embedding(fact["content"])
    
    result = db.create("fact", {
        "content": fact["content"],
        "embedding": embedding,
        "source": fact.get("source", "extracted"),
        "confidence": fact.get("confidence", 0.7),
        "file_source": fact.get("file_source", ""),
        "extracted_at": datetime.now().isoformat(),
        "tags": [],
        "agent_id": agent_id,
        "scope": "agent",
    })
    
    fact_id = result[0]["id"] if isinstance(result, list) else result["id"]
    
    # Link entities
    for entity_name in fact.get("entities", []):
        # Find or create entity
        existing = db.query(
            "SELECT id FROM entity WHERE name = $name LIMIT 1",
            {"name": entity_name}
        )
        
        # Query returns flat list of dicts
        entity_id = None
        if existing and isinstance(existing, list) and len(existing) > 0:
            first = existing[0]
            if isinstance(first, dict) and "id" in first:
                entity_id = first["id"]
        
        if not entity_id:
            # Create new entity
            entity_emb = get_embedding(entity_name)
            ent_result = db.create("entity", {
                "name": entity_name,
                "type": "extracted",
                "embedding": entity_emb,
                "confidence": 0.6,
            })
            entity_id = ent_result[0]["id"] if isinstance(ent_result, list) else ent_result["id"]
        
        # Link fact to entity
        try:
            db.query(
                "RELATE $fact->mentions->$entity SET role = 'subject'",
                {"fact": fact_id, "entity": entity_id}
            )
        except Exception as e:
            print(f"  Warning: Could not link entity {entity_name}: {e}", file=sys.stderr)
    
    return str(fact_id)

def update_fact_confidence(db, fact_id: str, new_confidence: float):
    """Update confidence of existing fact."""
    db.query(
        "UPDATE $fact_id SET confidence = $confidence, last_confirmed = time::now()",
        {"fact_id": fact_id, "confidence": new_confidence}
    )


# ============================================
# Extraction Logic
# ============================================

def extract_from_file(db, file_path: Path, verbose: bool = False, 
                      file_idx: int = 0, total_files: int = 1, agent_id: str = "main") -> dict:
    """Extract knowledge from a single file, tagging facts with the source agent."""
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    chunks = chunk_content(content)
    
    stats = {"chunks": len(chunks), "facts_new": 0, "facts_updated": 0, "facts_skipped": 0}
    rel_path = str(file_path.relative_to(WORKSPACE_DIR)) if WORKSPACE_DIR in file_path.parents or file_path.parent == WORKSPACE_DIR else file_path.name
    
    if verbose:
        print(f"  Processing {len(chunks)} chunks...")
    
    for i, chunk in enumerate(chunks):
        # Update progress with chunk detail
        overall_progress = file_idx + (i / len(chunks)) if len(chunks) > 0 else file_idx
        write_progress(
            "extracting",
            int(overall_progress * 100),
            total_files * 100,
            f"File {file_idx + 1}/{total_files}: {rel_path}",
            f"Chunk {i + 1}/{len(chunks)}"
        )
        
        facts = extract_facts_from_chunk(chunk["text"], str(file_path))
        
        for fact in facts:
            # Check for similar existing facts
            similar = find_similar_facts(db, fact["content"])
            
            if similar and isinstance(similar, list) and len(similar) > 0:
                # Fact exists - update confidence if new one is higher
                existing = similar[0]
                if isinstance(existing, dict):
                    if fact.get("confidence", 0.7) > existing.get("confidence", 0):
                        update_fact_confidence(db, existing["id"], fact["confidence"])
                        stats["facts_updated"] += 1
                    else:
                        stats["facts_skipped"] += 1
                else:
                    # Unexpected structure, treat as new
                    store_fact(db, fact, agent_id=agent_id)
                    stats["facts_new"] += 1
            else:
                # New fact - store it
                store_fact(db, fact, agent_id=agent_id)
                stats["facts_new"] += 1
        
        if verbose and (i + 1) % 5 == 0:
            print(f"    Chunk {i + 1}/{len(chunks)} done")
    
    return stats


def run_extraction(full: bool = False, verbose: bool = False, agent_id: str = "main"):
    """Run knowledge extraction from memory files."""
    # Write immediate progress so UI doesn't show stale "Starting..."
    write_progress("init", 0, 1, "Working", "Scanning files...")
    
    if not SURREALDB_AVAILABLE:
        print("Error: surrealdb package not installed", file=sys.stderr)
        clear_progress()
        return {"success": False, "error": "surrealdb not available"}
    
    state = load_state()
    files = list_memory_files(WORKSPACE_DIR)
    
    if full:
        changed = files
    else:
        changed = get_changed_files(files, state)
    
    if not changed:
        print("No files changed since last extraction.")
        clear_progress()
        return {"success": True, "files_processed": 0, "message": "No changes"}
    
    write_progress("init", 0, len(changed), f"Starting extraction of {len(changed)} file(s)")
    print(f"Extracting from {len(changed)} file(s)...")
    
    # Connect to database
    try:
        db = Surreal(SURREAL_CONFIG["connection"])
        db.signin({"username": SURREAL_CONFIG["user"], "password": SURREAL_CONFIG["password"]})
        db.use(SURREAL_CONFIG["namespace"], SURREAL_CONFIG["database"])
    except Exception as e:
        print(f"Error: Could not connect to database: {e}", file=sys.stderr)
        return {"success": False, "error": str(e)}
    
    total_stats = {"files": 0, "facts_new": 0, "facts_updated": 0, "facts_skipped": 0}
    
    try:
        for file_idx, file_path in enumerate(changed):
            rel_path = str(file_path.relative_to(WORKSPACE_DIR))
            write_progress(
                "extracting",
                file_idx,
                len(changed),
                f"Processing file {file_idx + 1}/{len(changed)}",
                rel_path
            )
            print(f"\n📄 {rel_path}")
            stats = extract_from_file(db, file_path, verbose, file_idx, len(changed), agent_id=agent_id)
            
            # Update file hash
            state["file_hashes"][str(file_path)] = hash_file(file_path)
            
            total_stats["files"] += 1
            total_stats["facts_new"] += stats["facts_new"]
            total_stats["facts_updated"] += stats["facts_updated"]
            total_stats["facts_skipped"] += stats["facts_skipped"]
            
            print(f"   ✓ {stats['facts_new']} new, {stats['facts_updated']} updated, {stats['facts_skipped']} skipped")
    
    finally:
        try:
            db.close()
        except NotImplementedError:
            pass  # HTTP connections don't need explicit close
    
    # Update state
    state["last_extraction"] = datetime.now().isoformat()
    state["extraction_count"] = state.get("extraction_count", 0) + 1
    state["facts_extracted"] = state.get("facts_extracted", 0) + total_stats["facts_new"]
    save_state(state)
    
    write_progress("complete", len(changed), len(changed), "Extraction complete", 
                   f"{total_stats['facts_new']} new, {total_stats['facts_updated']} updated")
    
    print(f"\n✅ Extraction complete:")
    print(f"   Files: {total_stats['files']}")
    print(f"   New facts: {total_stats['facts_new']}")
    print(f"   Updated: {total_stats['facts_updated']}")
    print(f"   Skipped (duplicates): {total_stats['facts_skipped']}")
    
    # Clear progress after short delay so UI can see completion
    clear_progress()
    
    return {"success": True, **total_stats}


def run_single_file_extraction(file_path_str: str, verbose: bool = False, agent_id: str = "main"):
    """Extract knowledge from a single file, tagging facts with the given agent."""
    if not SURREALDB_AVAILABLE:
        print("Error: surrealdb package not installed", file=sys.stderr)
        return {"success": False, "error": "surrealdb not available"}
    
    # Resolve file path
    file_path = Path(file_path_str)
    if not file_path.is_absolute():
        file_path = WORKSPACE_DIR / file_path
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return {"success": False, "error": "file not found"}
    
    print(f"Extracting from: {file_path.relative_to(WORKSPACE_DIR)}")
    
    try:
        db = Surreal(SURREAL_CONFIG["connection"])
        db.signin({"username": SURREAL_CONFIG["user"], "password": SURREAL_CONFIG["password"]})
        db.use(SURREAL_CONFIG["namespace"], SURREAL_CONFIG["database"])
        
        stats = extract_from_file(db, file_path, verbose, agent_id=agent_id)
        
        print(f"✓ {stats['facts_new']} new, {stats['facts_updated']} updated, {stats['facts_skipped']} skipped")
        
        # Update state for this file
        state = load_state()
        file_rel = str(file_path.relative_to(WORKSPACE_DIR))
        if "file_hashes" not in state:
            state["file_hashes"] = {}
        state["file_hashes"][file_rel] = hash_file(file_path)
        state["facts_extracted"] = state.get("facts_extracted", 0) + stats["facts_new"]
        save_state(state)
        
        return {"success": True, **stats}
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}
    
    finally:
        try:
            db.close()
        except NotImplementedError:
            pass


def run_reconcile(verbose: bool = False):
    """Deep reconciliation - prune stale facts, clean orphans."""
    # Write immediate progress
    write_progress("reconcile", 0, 4, "Working", "Connecting to database...")
    
    if not SURREALDB_AVAILABLE:
        print("Error: surrealdb package not installed", file=sys.stderr)
        clear_progress()
        return {"success": False, "error": "surrealdb not available"}
    
    print("Running deep reconciliation...")
    
    try:
        db = Surreal(SURREAL_CONFIG["connection"])
        db.signin({"username": SURREAL_CONFIG["user"], "password": SURREAL_CONFIG["password"]})
        db.use(SURREAL_CONFIG["namespace"], SURREAL_CONFIG["database"])
    except Exception as e:
        print(f"Error: Could not connect to database: {e}", file=sys.stderr)
        return {"success": False, "error": str(e)}
    
    stats = {"decayed": 0, "pruned": 0, "orphans_cleaned": 0}
    
    try:
        # 1. Apply confidence decay to old facts
        write_progress("reconcile", 1, 4, "Applying confidence decay", "Reducing confidence of stale facts...")
        decay_result = db.query("""
            UPDATE fact SET confidence = confidence * 0.95 
            WHERE last_accessed < time::now() - 30d 
                AND archived = false
                AND confidence > 0.1
        """)
        stats["decayed"] = len(decay_result[0]) if decay_result and decay_result[0] else 0
        print(f"  📉 Decayed {stats['decayed']} stale facts")
        
        # 2. Prune very low confidence facts
        write_progress("reconcile", 2, 4, "Pruning low-confidence facts", "Removing facts below threshold...")
        prune_result = db.query("""
            DELETE FROM fact 
            WHERE confidence < 0.15 
                AND last_confirmed < time::now() - 30d
        """)
        stats["pruned"] = len(prune_result[0]) if prune_result and prune_result[0] else 0
        print(f"  🗑️  Pruned {stats['pruned']} low-confidence facts")
        
        # 3. Clean orphaned edges
        write_progress("reconcile", 3, 4, "Cleaning orphaned edges", "Removing broken relationships...")
        db.query("DELETE FROM relates_to WHERE in.archived = true OR out.archived = true")
        db.query("DELETE FROM mentions WHERE in.archived = true")
        
        # 4. Clean orphaned entities (no mentions for 30+ days)
        write_progress("reconcile", 4, 4, "Cleaning orphaned entities", "Removing unused entities...")
        orphan_result = db.query("""
            DELETE FROM entity 
            WHERE count(<-mentions) = 0 
                AND created_at < time::now() - 30d
        """)
        stats["orphans_cleaned"] = len(orphan_result[0]) if orphan_result and orphan_result[0] else 0
        print(f"  🧹 Cleaned {stats['orphans_cleaned']} orphaned entities")
    
    finally:
        try:
            db.close()
        except NotImplementedError:
            pass  # HTTP connections don't need explicit close
    
    # Update state
    state = load_state()
    state["last_reconciliation"] = datetime.now().isoformat()
    save_state(state)
    
    write_progress("complete", 4, 4, "Reconciliation complete",
                   f"Decayed: {stats['decayed']}, Pruned: {stats['pruned']}, Orphans: {stats['orphans_cleaned']}")
    clear_progress()
    
    print(f"\n✅ Reconciliation complete")
    return {"success": True, **stats}


def show_status():
    """Show extraction status."""
    state = load_state()
    
    print("📊 Knowledge Extraction Status")
    print("=" * 40)
    
    last = state.get("last_extraction")
    if last:
        print(f"Last extraction: {last}")
    else:
        print("Last extraction: Never")
    
    last_recon = state.get("last_reconciliation")
    if last_recon:
        print(f"Last reconciliation: {last_recon}")
    
    print(f"Total extractions: {state.get('extraction_count', 0)}")
    print(f"Total facts extracted: {state.get('facts_extracted', 0)}")
    print(f"Files tracked: {len(state.get('file_hashes', {}))}")
    
    # Check for pending changes
    files = list_memory_files(WORKSPACE_DIR)
    changed = get_changed_files(files, state)
    
    print()
    if changed:
        print(f"⚠️  {len(changed)} file(s) changed since last extraction:")
        for f in changed[:5]:
            print(f"   - {f.relative_to(WORKSPACE_DIR)}")
        if len(changed) > 5:
            print(f"   ... and {len(changed) - 5} more")
    else:
        print("✅ All files up to date")
    
    return state


def run_deduplicate(threshold: float = 0.95, dry_run: bool = False):
    """Find and remove duplicate facts based on semantic similarity."""
    if not SURREALDB_AVAILABLE:
        print("Error: surrealdb package not installed", file=sys.stderr)
        return {"success": False, "error": "surrealdb not available"}
    
    print(f"Finding duplicates (threshold: {threshold:.0%})...")
    
    try:
        db = Surreal(SURREAL_CONFIG["connection"])
        db.signin({"username": SURREAL_CONFIG["user"], "password": SURREAL_CONFIG["password"]})
        db.use(SURREAL_CONFIG["namespace"], SURREAL_CONFIG["database"])
        
        # Get all facts
        facts = db.query("SELECT id, content, embedding, confidence, created_at FROM fact WHERE archived = false")
        
        if not facts:
            print("No facts to deduplicate")
            return {"success": True, "duplicates": 0}
        
        print(f"Checking {len(facts)} facts for duplicates...")
        
        # Find duplicates using pairwise similarity
        duplicates = []
        seen_ids = set()
        
        for i, fact1 in enumerate(facts):
            if str(fact1["id"]) in seen_ids:
                continue
            
            emb1 = fact1.get("embedding", [])
            if not emb1:
                continue
            
            for fact2 in facts[i+1:]:
                if str(fact2["id"]) in seen_ids:
                    continue
                
                emb2 = fact2.get("embedding", [])
                if not emb2:
                    continue
                
                # Cosine similarity
                dot = sum(a * b for a, b in zip(emb1, emb2))
                norm1 = sum(a * a for a in emb1) ** 0.5
                norm2 = sum(b * b for b in emb2) ** 0.5
                similarity = dot / (norm1 * norm2) if norm1 and norm2 else 0
                
                if similarity >= threshold:
                    # Keep the one with higher confidence, or older if equal
                    keep, remove = (fact1, fact2) if fact1.get("confidence", 0) >= fact2.get("confidence", 0) else (fact2, fact1)
                    duplicates.append({
                        "keep": str(keep["id"]),
                        "remove": str(remove["id"]),
                        "similarity": similarity,
                        "keep_content": keep["content"][:60],
                        "remove_content": remove["content"][:60],
                    })
                    seen_ids.add(str(remove["id"]))
        
        print(f"Found {len(duplicates)} duplicate pairs")
        
        if duplicates and not dry_run:
            print("Removing duplicates...")
            for dup in duplicates:
                db.query("UPDATE type::thing($id) SET archived = true", {"id": dup["remove"]})
            print(f"Archived {len(duplicates)} duplicate facts")
        elif duplicates and dry_run:
            print("\nDry run - would remove:")
            for dup in duplicates[:10]:
                print(f"  [{dup['similarity']:.1%}] \"{dup['remove_content']}...\"")
            if len(duplicates) > 10:
                print(f"  ... and {len(duplicates) - 10} more")
        
        return {"success": True, "duplicates": len(duplicates), "dry_run": dry_run}
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}
    
    finally:
        try:
            db.close()
        except NotImplementedError:
            pass


def run_relation_discovery(batch_size: int = 20, verbose: bool = False):
    """Use AI to discover relationships between facts."""
    if not SURREALDB_AVAILABLE:
        print("Error: surrealdb package not installed", file=sys.stderr)
        return {"success": False, "error": "surrealdb not available"}
    
    if not OPENAI_AVAILABLE:
        print("Error: openai package not installed", file=sys.stderr)
        return {"success": False, "error": "openai not available"}
    
    write_progress("relations", 0, 100, "Starting relationship discovery", "Connecting to database...")
    print("Discovering relationships between facts...")
    
    try:
        db = Surreal(SURREAL_CONFIG["connection"])
        db.signin({"username": SURREAL_CONFIG["user"], "password": SURREAL_CONFIG["password"]})
        db.use(SURREAL_CONFIG["namespace"], SURREAL_CONFIG["database"])
    except Exception as e:
        print(f"Error: Could not connect to database: {e}", file=sys.stderr)
        clear_progress()
        return {"success": False, "error": str(e)}
    
    stats = {"analyzed": 0, "relations_found": 0, "supports": 0, "contradicts": 0, "relates_to": 0, "updates": 0}
    
    try:
        # Get facts without many relations (prioritize isolated facts)
        write_progress("relations", 5, 100, "Finding isolated facts", "Querying database...")
        facts = db.query("""
            SELECT id, content, confidence, source, created_at
            FROM fact
            WHERE archived = false
            ORDER BY created_at DESC
            LIMIT 100
        """)
        
        if not facts or len(facts) == 0:
            print("No facts to analyze")
            clear_progress()
            return {"success": True, "message": "No facts to analyze", **stats}
        
        print(f"Analyzing {len(facts)} facts for relationships...")
        
        # Process in batches
        for batch_start in range(0, len(facts), batch_size):
            batch = facts[batch_start:batch_start + batch_size]
            batch_num = batch_start // batch_size + 1
            total_batches = (len(facts) + batch_size - 1) // batch_size
            
            write_progress(
                "relations",
                10 + int(80 * batch_start / len(facts)),
                100,
                f"Analyzing batch {batch_num}/{total_batches}",
                f"Processing {len(batch)} facts..."
            )
            
            # Find relations for this batch
            relations = discover_relations_for_batch(db, batch, verbose)
            
            for rel in relations:
                try:
                    from_rec = rel["from_record"]
                    to_rec = rel["to_record"]
                    
                    # Check if relation already exists
                    existing = db.query("""
                        SELECT id FROM relates_to 
                        WHERE in = $from AND out = $to AND relationship = $relationship
                        LIMIT 1
                    """, {"from": from_rec, "to": to_rec, "relationship": rel["kind"]})
                    
                    if existing and len(existing) > 0:
                        continue  # Skip existing relation
                    
                    # Create the relation - pass RecordID objects, use schema field names
                    # Schema: relationship (string), strength (float), detected_at, detection_method
                    db.query("""
                        RELATE $from->relates_to->$to SET 
                            relationship = $relationship,
                            strength = $strength,
                            detection_method = 'ai_discovery'
                    """, {
                        "from": from_rec,
                        "to": to_rec,
                        "relationship": rel["kind"],
                        "strength": rel.get("confidence", 0.7),
                    })
                    
                    stats["relations_found"] += 1
                    stats[rel["kind"]] = stats.get(rel["kind"], 0) + 1
                    
                    if verbose:
                        print(f"  + {rel['kind']}: {rel.get('reason', '')[:50]}")
                
                except Exception as e:
                    if verbose:
                        print(f"  Warning: Could not create relation: {e}")
            
            stats["analyzed"] += len(batch)
        
        write_progress("relations", 95, 100, "Finalizing", "Updating statistics...")
        
    finally:
        try:
            db.close()
        except NotImplementedError:
            pass
    
    # Update state
    state = load_state()
    state["last_relation_discovery"] = datetime.now().isoformat()
    state["relations_discovered"] = state.get("relations_discovered", 0) + stats["relations_found"]
    save_state(state)
    
    write_progress("complete", 100, 100, "Relationship discovery complete",
                   f"Found {stats['relations_found']} new relations")
    clear_progress()
    
    print(f"\n✅ Relationship discovery complete:")
    print(f"   Facts analyzed: {stats['analyzed']}")
    print(f"   New relations: {stats['relations_found']}")
    print(f"   - supports: {stats['supports']}")
    print(f"   - contradicts: {stats['contradicts']}")
    print(f"   - relates_to: {stats['relates_to']}")
    print(f"   - updates: {stats['updates']}")
    
    return {"success": True, **stats}


RELATION_DISCOVERY_PROMPT = """Analyze these facts and identify meaningful relationships between them.

Facts (with IDs):
{facts_list}

For each relationship you find, specify:
- from_id: The source fact ID
- to_id: The target fact ID  
- kind: One of "supports", "contradicts", "relates_to", or "updates"
- confidence: 0.0-1.0 how certain you are
- reason: Brief explanation

Relationship types:
- supports: Fact A provides evidence or reinforcement for Fact B
- contradicts: Fact A conflicts with or negates Fact B
- relates_to: Facts share a topic, entity, or concept
- updates: Fact A is a newer/corrected version of Fact B

Rules:
- Only include strong, meaningful relationships
- Don't relate every fact - quality over quantity
- Consider semantic meaning, not just keyword overlap
- If facts share an entity but aren't meaningfully related, skip them

Return JSON array (or empty array if no strong relationships):
[
  {{"from_id": "fact:xxx", "to_id": "fact:yyy", "kind": "supports", "confidence": 0.8, "reason": "Both describe X's preference for Y"}}
]

Only return the JSON array."""


def discover_relations_for_batch(db, batch_facts: list, verbose: bool = False) -> list[dict]:
    """Use LLM to find relationships in a batch of facts."""
    if len(batch_facts) < 2:
        return []
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return []
    
    # Build a lookup from string ID to RecordID object
    id_lookup = {}
    for f in batch_facts:
        # The id is a RecordID object, str() gives "fact:xxx"
        id_str = str(f['id'])
        id_lookup[id_str] = f['id']
    
    # Format facts for prompt
    facts_list = "\n".join([
        f"[{f['id']}] {f['content']}" 
        for f in batch_facts
    ])
    
    client = openai.OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": RELATION_DISCOVERY_PROMPT.format(facts_list=facts_list)}
            ],
            temperature=0.3,
            max_tokens=2000,
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON
        if result_text.startswith("```"):
            result_text = re.sub(r"```(?:json)?\n?", "", result_text)
            result_text = result_text.strip()
        
        relations = json.loads(result_text)
        
        # Validate and transform
        valid_relations = []
        for rel in relations:
            if all(k in rel for k in ["from_id", "to_id", "kind"]):
                from_id_str = rel["from_id"]
                to_id_str = rel["to_id"]
                
                # Look up the RecordID objects
                from_record = id_lookup.get(from_id_str)
                to_record = id_lookup.get(to_id_str)
                
                if from_record and to_record and rel["kind"] in ["supports", "contradicts", "relates_to", "updates"]:
                    valid_relations.append({
                        "from": from_id_str,
                        "to": to_id_str,
                        "from_record": from_record,
                        "to_record": to_record,
                        "kind": rel["kind"],
                        "confidence": rel.get("confidence", 0.7),
                        "reason": rel.get("reason", ""),
                    })
        
        return valid_relations
    
    except Exception as e:
        if verbose:
            print(f"  Warning: Relation discovery failed: {e}")
        return []


def run_rebuild_links():
    """Rebuild entity links for all facts by re-extracting entities."""
    if not SURREALDB_AVAILABLE:
        print("Error: surrealdb package not installed", file=sys.stderr)
        return {"success": False, "error": "surrealdb not available"}
    
    print("Rebuilding entity links...")
    
    try:
        db = Surreal(SURREAL_CONFIG["connection"])
        db.signin({"username": SURREAL_CONFIG["user"], "password": SURREAL_CONFIG["password"]})
        db.use(SURREAL_CONFIG["namespace"], SURREAL_CONFIG["database"])
        
        # Get all facts
        facts = db.query("SELECT id, content FROM fact WHERE archived = false")
        
        if not facts:
            print("No facts to process")
            return {"success": True, "links_created": 0}
        
        print(f"Processing {len(facts)} facts...")
        links_created = 0
        
        for i, fact in enumerate(facts):
            fact_id = fact["id"]
            content = fact["content"]
            
            # Extract entities from content
            entities = extract_entities_simple(content)
            
            for entity_name in entities:
                # Find or create entity
                existing = db.query(
                    "SELECT id FROM entity WHERE name = $name LIMIT 1",
                    {"name": entity_name}
                )
                
                entity_id = None
                if existing and len(existing) > 0 and isinstance(existing[0], dict):
                    entity_id = existing[0]["id"]
                
                if not entity_id:
                    # Create entity
                    entity_emb = get_embedding(entity_name)
                    ent_result = db.create("entity", {
                        "name": entity_name,
                        "type": "extracted",
                        "embedding": entity_emb,
                        "confidence": 0.6,
                    })
                    entity_id = ent_result[0]["id"] if isinstance(ent_result, list) else ent_result["id"]
                
                # Create link (ignore if exists)
                try:
                    db.query(
                        "RELATE $fact->mentions->$entity SET role = 'subject'",
                        {"fact": fact_id, "entity": entity_id}
                    )
                    links_created += 1
                except Exception:
                    pass  # Link may already exist
            
            if (i + 1) % 20 == 0:
                print(f"  Processed {i + 1}/{len(facts)} facts...")
        
        print(f"\n✅ Created {links_created} entity links")
        return {"success": True, "links_created": links_created}
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}
    
    finally:
        try:
            db.close()
        except NotImplementedError:
            pass


def extract_entities_simple(text: str) -> list[str]:
    """Simple entity extraction using regex patterns."""
    import re
    
    entities = set()
    
    # Skip common words
    skip_words = {"the", "a", "an", "this", "that", "it", "i", "we", "they", "he", "she", 
                  "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
                  "do", "does", "did", "will", "would", "could", "should", "may", "might",
                  "remember", "know", "think", "said", "says", "told", "new", "use", "using"}
    
    # Capitalized words/phrases (names, projects)
    for match in re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text):
        if match.lower() not in skip_words and len(match) > 1:
            entities.add(match)
    
    # Kebab-case identifiers (project names)
    for match in re.findall(r'\b([a-z]+-[a-z]+(?:-[a-z]+)*)\b', text):
        if len(match) > 3:
            entities.add(match)
    
    return list(entities)


# ============================================
# CLI
# ============================================

def main():
    parser = argparse.ArgumentParser(description="Knowledge Extraction from Memory Files")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Global --agent-id option (usable with any subcommand)
    parser.add_argument("--agent-id", default="main", help="Agent ID to tag extracted facts with (default: main)")

    # extract
    extract_p = subparsers.add_parser("extract", help="Extract knowledge from memory files")
    extract_p.add_argument("--full", action="store_true", help="Process all files, not just changed")
    extract_p.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    extract_p.add_argument("--file", "-f", help="Extract from single file only")
    
    # status
    subparsers.add_parser("status", help="Show extraction status")
    
    # reconcile
    reconcile_p = subparsers.add_parser("reconcile", help="Deep reconciliation (prune, decay, clean)")
    reconcile_p.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    # check (for heartbeat - returns exit code)
    check_p = subparsers.add_parser("check", help="Check if extraction needed (for heartbeat)")
    
    # dedupe
    dedupe_p = subparsers.add_parser("dedupe", help="Find and remove duplicate facts")
    dedupe_p.add_argument("--threshold", "-t", type=float, default=0.95, help="Similarity threshold (default: 0.95)")
    dedupe_p.add_argument("--dry-run", action="store_true", help="Show duplicates without removing")
    
    # discover-relations
    relations_p = subparsers.add_parser("discover-relations", help="Use AI to find relationships between facts")
    relations_p.add_argument("--batch-size", "-b", type=int, default=20, help="Facts per batch (default: 20)")
    relations_p.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    # rebuild-links
    rebuild_p = subparsers.add_parser("rebuild-links", help="Rebuild entity links for existing facts")
    
    args = parser.parse_args()
    
    agent_id = getattr(args, "agent_id", "main") or "main"

    if args.command == "extract":
        if args.file:
            result = run_single_file_extraction(args.file, verbose=args.verbose, agent_id=agent_id)
        else:
            result = run_extraction(full=args.full, verbose=args.verbose, agent_id=agent_id)
        sys.exit(0 if result.get("success") else 1)
    
    elif args.command == "status":
        show_status()
    
    elif args.command == "reconcile":
        result = run_reconcile(verbose=args.verbose)
        sys.exit(0 if result.get("success") else 1)
    
    elif args.command == "check":
        state = load_state()
        files = list_memory_files(WORKSPACE_DIR)
        changed = get_changed_files(files, state)
        if changed:
            print(f"EXTRACTION_NEEDED:{len(changed)}")
            sys.exit(1)  # Extraction needed
        else:
            print("UP_TO_DATE")
            sys.exit(0)  # No extraction needed
    
    elif args.command == "dedupe":
        result = run_deduplicate(threshold=args.threshold, dry_run=args.dry_run)
        sys.exit(0 if result.get("success") else 1)
    
    elif args.command == "rebuild-links":
        result = run_rebuild_links()
        sys.exit(0 if result.get("success") else 1)
    
    elif args.command == "discover-relations":
        result = run_relation_discovery(batch_size=args.batch_size, verbose=args.verbose)
        sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
