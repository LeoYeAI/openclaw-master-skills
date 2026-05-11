#!/usr/bin/env python3
"""
SurrealDB Memory v2 Migration Script

Applies schema v2 changes idempotently - safe to run multiple times.
Handles "already exists" errors gracefully.

Usage:
    python3 migrate-v2.py [--url URL] [--user USER] [--pass PASS]
"""

import argparse
import os
import sys

# Configuration
SURREAL_CONFIG = {
    "connection": os.environ.get("SURREAL_URL", "http://localhost:8000"),
    "namespace": "openclaw",
    "database": "memory",
    "user": os.environ.get("SURREAL_USER", "root"),
    "password": os.environ.get("SURREAL_PASS", "root"),
}

try:
    from surrealdb import Surreal
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False
    print("ERROR: surrealdb package not installed")
    print("Run: pip install surrealdb")
    sys.exit(1)


def get_db():
    """Get database connection."""
    db = Surreal(SURREAL_CONFIG["connection"])
    db.signin({"username": SURREAL_CONFIG["user"], "password": SURREAL_CONFIG["password"]})
    db.use(SURREAL_CONFIG["namespace"], SURREAL_CONFIG["database"])
    return db


STATEMENTS = [
    # Episode table
    ("DEFINE TABLE episode SCHEMAFULL", "episode table"),
    ("DEFINE FIELD task ON TABLE episode TYPE string", "episode.task"),
    ("DEFINE FIELD goal ON TABLE episode TYPE string", "episode.goal"),
    ("DEFINE FIELD started_at ON TABLE episode TYPE option<datetime>", "episode.started_at"),
    ("DEFINE FIELD completed_at ON TABLE episode TYPE option<datetime>", "episode.completed_at"),
    ("DEFINE FIELD outcome ON TABLE episode TYPE string DEFAULT 'in_progress'", "episode.outcome"),
    ("DEFINE FIELD duration_hours ON TABLE episode TYPE option<float>", "episode.duration_hours"),
    ("DEFINE FIELD steps_taken ON TABLE episode TYPE int DEFAULT 0", "episode.steps_taken"),
    ("DEFINE FIELD decisions ON TABLE episode TYPE array DEFAULT []", "episode.decisions"),
    ("DEFINE FIELD problems ON TABLE episode TYPE array DEFAULT []", "episode.problems"),
    ("DEFINE FIELD solutions ON TABLE episode TYPE array DEFAULT []", "episode.solutions"),
    ("DEFINE FIELD key_learnings ON TABLE episode TYPE array DEFAULT []", "episode.key_learnings"),
    ("DEFINE FIELD facts_used ON TABLE episode TYPE array DEFAULT []", "episode.facts_used"),
    ("DEFINE FIELD facts_created ON TABLE episode TYPE array DEFAULT []", "episode.facts_created"),
    ("DEFINE FIELD embedding ON TABLE episode TYPE option<array<float>>", "episode.embedding"),
    ("DEFINE FIELD metadata ON TABLE episode TYPE option<object>", "episode.metadata"),
    ("DEFINE FIELD session_key ON TABLE episode TYPE option<string>", "episode.session_key"),
    ("DEFINE FIELD agent_id ON TABLE episode TYPE string DEFAULT 'main'", "episode.agent_id"),
    ("DEFINE INDEX IF NOT EXISTS episode_embedding_idx ON episode FIELDS embedding MTREE DIMENSION 1536 DIST COSINE", "episode embedding index"),
    ("DEFINE INDEX IF NOT EXISTS episode_outcome_idx ON episode FIELDS outcome", "episode outcome index"),
    ("DEFINE INDEX IF NOT EXISTS episode_agent_idx ON episode FIELDS agent_id", "episode agent index"),
    
    # Working memory table
    ("DEFINE TABLE working_memory SCHEMAFULL", "working_memory table"),
    ("DEFINE FIELD session_key ON TABLE working_memory TYPE string", "wm.session_key"),
    ("DEFINE FIELD agent_id ON TABLE working_memory TYPE string DEFAULT 'main'", "wm.agent_id"),
    ("DEFINE FIELD goal ON TABLE working_memory TYPE string", "wm.goal"),
    ("DEFINE FIELD plan ON TABLE working_memory TYPE array DEFAULT []", "wm.plan"),
    ("DEFINE FIELD decisions_made ON TABLE working_memory TYPE array DEFAULT []", "wm.decisions_made"),
    ("DEFINE FIELD blocked_on ON TABLE working_memory TYPE option<string>", "wm.blocked_on"),
    ("DEFINE FIELD confidence ON TABLE working_memory TYPE float DEFAULT 0.5", "wm.confidence"),
    ("DEFINE FIELD iteration ON TABLE working_memory TYPE int DEFAULT 0", "wm.iteration"),
    ("DEFINE FIELD created_at ON TABLE working_memory TYPE datetime DEFAULT time::now()", "wm.created_at"),
    ("DEFINE FIELD updated_at ON TABLE working_memory TYPE datetime DEFAULT time::now()", "wm.updated_at"),
    ("DEFINE FIELD metadata ON TABLE working_memory TYPE option<object>", "wm.metadata"),
    ("DEFINE INDEX IF NOT EXISTS wm_session_idx ON working_memory FIELDS session_key", "wm session index"),
    ("DEFINE INDEX IF NOT EXISTS wm_agent_idx ON working_memory FIELDS agent_id", "wm agent index"),
    
    # Fact table upgrades
    ("DEFINE FIELD scope ON TABLE fact TYPE string DEFAULT 'agent'", "fact.scope"),
    ("DEFINE FIELD client_id ON TABLE fact TYPE option<string>", "fact.client_id"),
    ("DEFINE FIELD agent_id ON TABLE fact TYPE string DEFAULT 'main'", "fact.agent_id"),
    ("DEFINE FIELD success_count ON TABLE fact TYPE int DEFAULT 0", "fact.success_count"),
    ("DEFINE FIELD failure_count ON TABLE fact TYPE int DEFAULT 0", "fact.failure_count"),
    ("DEFINE FIELD last_outcome ON TABLE fact TYPE option<string>", "fact.last_outcome"),
    ("DEFINE INDEX IF NOT EXISTS fact_scope_idx ON fact FIELDS scope", "fact scope index"),
    ("DEFINE INDEX IF NOT EXISTS fact_agent_idx ON fact FIELDS agent_id", "fact agent index"),
    
    # Entity upgrades
    ("DEFINE FIELD scope ON TABLE entity TYPE string DEFAULT 'agent'", "entity.scope"),
    ("DEFINE FIELD client_id ON TABLE entity TYPE option<string>", "entity.client_id"),
    ("DEFINE FIELD agent_id ON TABLE entity TYPE string DEFAULT 'main'", "entity.agent_id"),
]


def main():
    parser = argparse.ArgumentParser(description="Apply SurrealDB Memory v2 schema")
    parser.add_argument("--url", default=SURREAL_CONFIG["connection"], help="SurrealDB URL")
    parser.add_argument("--user", default=SURREAL_CONFIG["user"], help="Username")
    parser.add_argument("--password", "--pass", default=SURREAL_CONFIG["password"], help="Password")
    parser.add_argument("--force", action="store_true", help="Drop and recreate tables")
    args = parser.parse_args()
    
    SURREAL_CONFIG["connection"] = args.url
    SURREAL_CONFIG["user"] = args.user
    SURREAL_CONFIG["password"] = args.password
    
    print(f"=== SurrealDB Memory v2 Migration ===")
    print(f"URL: {SURREAL_CONFIG['connection']}")
    print(f"NS/DB: {SURREAL_CONFIG['namespace']}/{SURREAL_CONFIG['database']}")
    print()
    
    try:
        db = get_db()
    except Exception as e:
        print(f"ERROR: Could not connect to SurrealDB: {e}")
        print("Start it with: surreal start --user root --pass root file:~/.openclaw/memory/knowledge.db")
        sys.exit(1)
    
    if args.force:
        print("Force mode: dropping episode and working_memory tables...")
        try:
            db.query("REMOVE TABLE episode")
            db.query("REMOVE TABLE working_memory")
        except:
            pass
        print()
    
    success = 0
    skipped = 0
    errors = 0
    
    for stmt, desc in STATEMENTS:
        try:
            db.query(stmt)
            print(f"✓ {desc}")
            success += 1
        except Exception as e:
            err = str(e)
            if "already exists" in err.lower():
                print(f"○ {desc} (already exists)")
                skipped += 1
            else:
                print(f"✗ {desc}: {err[:60]}")
                errors += 1
    
    print()
    print(f"=== Migration Complete ===")
    print(f"Applied: {success}, Skipped: {skipped}, Errors: {errors}")
    
    if errors == 0:
        print()
        print("New capabilities:")
        print("  • Episodes table for task histories")
        print("  • Working memory snapshots")
        print("  • Scoped facts (global/client/agent)")
        print("  • Outcome-based confidence calibration")
        print()
        print("Next steps:")
        print("  1. Update MCP config to use mcp-server-v2.py")
        print("  2. Create .working-memory/ directory in workspace")
        print("  3. Start using episode_* and working_memory_* tools")


if __name__ == "__main__":
    main()
