#!/usr/bin/env python3
"""
Migrate existing OpenClaw SQLite memory to SurrealDB knowledge graph.

Usage:
    python3 migrate-sqlite.py [--source ~/.openclaw/memory/main.sqlite] [--dry-run]
"""

import argparse
import asyncio
import json
import os
import sqlite3
import sys
from pathlib import Path

try:
    from surrealdb import Surreal
except ImportError:
    print("ERROR: surrealdb package not installed. Run: pip install surrealdb")
    sys.exit(1)

try:
    import yaml
except ImportError:
    yaml = None

# Import config from memory-cli
sys.path.insert(0, str(Path(__file__).parent))
from importlib import import_module

# Load config
DEFAULT_CONFIG = {
    "connection": "ws://localhost:8000/rpc",
    "namespace": "openclaw",
    "database": "memory",
    "user": "root",
    "password": "root",
}


def load_config() -> dict:
    """Load configuration."""
    config_paths = [
        Path.home() / ".openclaw" / "surrealdb-memory.yaml",
        Path("surrealdb-memory.yaml"),
    ]
    
    for path in config_paths:
        if path.exists() and yaml:
            with open(path) as f:
                user_config = yaml.safe_load(f)
                config = DEFAULT_CONFIG.copy()
                if user_config:
                    config.update(user_config)
                return config
    
    return DEFAULT_CONFIG


CONFIG = load_config()


def find_sqlite_databases() -> list[Path]:
    """Find existing OpenClaw SQLite memory databases."""
    memory_dir = Path.home() / ".openclaw" / "memory"
    if not memory_dir.exists():
        return []
    
    return list(memory_dir.glob("*.sqlite"))


def read_sqlite_chunks(db_path: Path) -> list[dict]:
    """Read chunks from SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, path, source, start_line, end_line, text, embedding, updated_at
            FROM chunks
        """)
        
        rows = cursor.fetchall()
        chunks = []
        
        for row in rows:
            embedding = json.loads(row["embedding"]) if row["embedding"] else None
            chunks.append({
                "id": row["id"],
                "path": row["path"],
                "source": row["source"],
                "start_line": row["start_line"],
                "end_line": row["end_line"],
                "text": row["text"],
                "embedding": embedding,
                "updated_at": row["updated_at"],
            })
        
        return chunks
    finally:
        conn.close()


async def migrate_chunks(chunks: list[dict], db: Surreal, dry_run: bool = False) -> dict:
    """Migrate chunks to SurrealDB facts."""
    stats = {"migrated": 0, "skipped": 0, "errors": 0}
    
    for chunk in chunks:
        try:
            # Skip if no embedding
            if not chunk["embedding"]:
                print(f"  SKIP (no embedding): {chunk['path']}:{chunk['start_line']}")
                stats["skipped"] += 1
                continue
            
            # Determine source type
            source = "migrated"
            if "MEMORY.md" in chunk["path"]:
                source = "explicit"
            
            # Initial confidence based on source file
            confidence = 0.7 if "MEMORY.md" in chunk["path"] else 0.5
            
            if dry_run:
                print(f"  [DRY-RUN] Would migrate: {chunk['path']}:{chunk['start_line']}-{chunk['end_line']}")
                print(f"            Text: {chunk['text'][:80]}...")
                stats["migrated"] += 1
                continue
            
            # Check for existing fact with same content
            existing = await db.query("""
                SELECT * FROM fact WHERE content = $content
            """, {"content": chunk["text"]})
            
            if existing and existing[0]:
                print(f"  SKIP (exists): {chunk['path']}:{chunk['start_line']}")
                stats["skipped"] += 1
                continue
            
            # Create fact
            result = await db.create("fact", {
                "content": chunk["text"],
                "embedding": chunk["embedding"],
                "source": source,
                "confidence": confidence,
                "tags": [chunk["path"]],
                "metadata": {
                    "migrated_from": str(chunk["id"]),
                    "original_path": chunk["path"],
                    "original_lines": f"{chunk['start_line']}-{chunk['end_line']}",
                },
            })
            
            print(f"  ✓ Migrated: {chunk['path']}:{chunk['start_line']}-{chunk['end_line']}")
            stats["migrated"] += 1
            
        except Exception as e:
            print(f"  ERROR: {chunk['path']}:{chunk['start_line']} - {e}")
            stats["errors"] += 1
    
    return stats


async def main():
    parser = argparse.ArgumentParser(description="Migrate SQLite memory to SurrealDB")
    parser.add_argument("--source", type=Path, help="Source SQLite database")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated")
    parser.add_argument("--all", action="store_true", help="Migrate all found databases")
    args = parser.parse_args()
    
    # Find databases to migrate
    if args.source:
        databases = [args.source]
    elif args.all:
        databases = find_sqlite_databases()
    else:
        databases = find_sqlite_databases()
        if not databases:
            print("No SQLite databases found in ~/.openclaw/memory/")
            return
        
        print("Found databases:")
        for i, db in enumerate(databases, 1):
            print(f"  {i}. {db.name}")
        
        choice = input("\nMigrate which? [1/all/none]: ").strip().lower()
        if choice == "none":
            return
        elif choice == "all":
            pass
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(databases):
                databases = [databases[idx]]
            else:
                print("Invalid choice")
                return
        else:
            databases = [databases[0]]
    
    if not databases:
        print("No databases selected.")
        return
    
    # Connect to SurrealDB
    print("\nConnecting to SurrealDB...")
    db = Surreal(CONFIG["connection"])
    await db.connect()
    await db.signin({"user": CONFIG["user"], "pass": CONFIG["password"]})
    await db.use(CONFIG["namespace"], CONFIG["database"])
    
    try:
        total_stats = {"migrated": 0, "skipped": 0, "errors": 0}
        
        for db_path in databases:
            print(f"\n=== Migrating: {db_path.name} ===")
            
            # Read chunks
            chunks = read_sqlite_chunks(db_path)
            print(f"Found {len(chunks)} chunks")
            
            if not chunks:
                continue
            
            # Migrate
            stats = await migrate_chunks(chunks, db, args.dry_run)
            
            for key in total_stats:
                total_stats[key] += stats[key]
        
        print("\n=== Migration Complete ===")
        print(f"Migrated: {total_stats['migrated']}")
        print(f"Skipped: {total_stats['skipped']}")
        print(f"Errors: {total_stats['errors']}")
        
        if args.dry_run:
            print("\n(This was a dry run. No changes were made.)")
    
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
