#!/usr/bin/env python3
"""
SurrealDB Knowledge Graph Memory CLI

Commands:
  store     - Store a new fact
  search    - Semantic search for facts
  get       - Get a fact with context
  relate    - Create relationship between facts
  decay     - Apply time decay to all facts
  prune     - Remove low-confidence stale facts
  consolidate - Merge near-duplicate facts
  maintain  - Run full maintenance cycle
  stats     - Show database statistics
"""

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import yaml

try:
    from surrealdb import Surreal
except ImportError:
    print("ERROR: surrealdb package not installed. Run: pip install surrealdb")
    sys.exit(1)

try:
    import openai
except ImportError:
    openai = None

# ============================================
# Configuration
# ============================================

DEFAULT_CONFIG = {
    "connection": "ws://localhost:8000/rpc",
    "namespace": "openclaw",
    "database": "memory",
    "user": "root",
    "password": "root",
    "embedding": {
        "provider": "openai",
        "model": "text-embedding-3-small",
        "dimensions": 1536,
    },
    "confidence": {
        "initial_explicit": 0.9,
        "initial_inferred": 0.6,
        "support_threshold": 0.7,
        "support_transfer": 0.15,
        "support_max_boost": 0.2,
        "contradict_threshold": 0.7,
        "contradict_drain": 0.20,
        "entity_boost": 0.02,
        "entity_threshold": 0.8,
        "decay_rate": 0.05,
    },
    "maintenance": {
        "prune_after_days": 30,
        "min_confidence": 0.2,
        "consolidate_similarity": 0.95,
    },
}


def load_config() -> dict:
    """Load configuration from file or use defaults."""
    config_paths = [
        Path.home() / ".openclaw" / "surrealdb-memory.yaml",
        Path.home() / ".config" / "openclaw" / "surrealdb-memory.yaml",
        Path("surrealdb-memory.yaml"),
    ]
    
    for path in config_paths:
        if path.exists():
            with open(path) as f:
                user_config = yaml.safe_load(f)
                # Merge with defaults
                config = DEFAULT_CONFIG.copy()
                if user_config:
                    for key, value in user_config.items():
                        if isinstance(value, dict) and key in config:
                            config[key].update(value)
                        else:
                            config[key] = value
                return config
    
    return DEFAULT_CONFIG


CONFIG = load_config()

# ============================================
# Embedding
# ============================================

def get_embedding(text: str) -> list[float]:
    """Generate embedding for text using configured provider."""
    provider = CONFIG["embedding"]["provider"]
    model = CONFIG["embedding"]["model"]
    
    if provider == "openai":
        if openai is None:
            raise RuntimeError("openai package not installed")
        
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable not set")
        
        client = openai.OpenAI(api_key=api_key)
        response = client.embeddings.create(input=text, model=model)
        return response.data[0].embedding
    
    else:
        raise RuntimeError(f"Unknown embedding provider: {provider}")


# ============================================
# Entity Extraction (Simple)
# ============================================

def extract_entities(text: str) -> list[dict]:
    """Extract entities from text using simple patterns."""
    entities = []
    
    # Capitalized words (potential names/proper nouns)
    # Skip common words and sentence starters
    skip_words = {"the", "a", "an", "this", "that", "it", "i", "we", "they", "he", "she"}
    words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text)
    
    for word in words:
        if word.lower() not in skip_words:
            entities.append({
                "name": word,
                "type": "unknown",  # Could enhance with NER
            })
    
    # Project patterns (word-word, CamelCase)
    projects = re.findall(r'\b([a-z]+-[a-z]+|[A-Z][a-z]+[A-Z][a-z]+)\b', text)
    for project in projects:
        entities.append({
            "name": project,
            "type": "project",
        })
    
    # Deduplicate
    seen = set()
    unique = []
    for e in entities:
        key = e["name"].lower()
        if key not in seen:
            seen.add(key)
            unique.append(e)
    
    return unique


# ============================================
# Contradiction Detection
# ============================================

NEGATION_PATTERNS = [
    (r"(.+) is (.+)", r"\1 is not \2"),
    (r"(.+) is not (.+)", r"\1 is \2"),
    (r"(.+) prefers (.+)", r"\1 dislikes \2"),
    (r"(.+) likes (.+)", r"\1 dislikes \2"),
    (r"(.+) always (.+)", r"\1 never \2"),
    (r"(.+) never (.+)", r"\1 always \2"),
]


def check_contradiction(fact1: str, fact2: str) -> float:
    """Check if two facts contradict. Returns contradiction strength (0-1)."""
    f1_lower = fact1.lower().strip()
    f2_lower = fact2.lower().strip()
    
    # Direct negation check
    for pattern, negated in NEGATION_PATTERNS:
        match1 = re.match(pattern, f1_lower)
        if match1:
            negated_form = re.sub(pattern, negated, f1_lower)
            if negated_form in f2_lower or f2_lower in negated_form:
                return 0.8
    
    # Check for opposing sentiment words
    positive = {"likes", "prefers", "enjoys", "loves", "wants", "always", "good", "yes"}
    negative = {"dislikes", "hates", "avoids", "never", "bad", "no", "not"}
    
    f1_words = set(f1_lower.split())
    f2_words = set(f2_lower.split())
    
    # Same subject but opposite sentiment
    common = f1_words & f2_words
    if len(common) >= 2:  # Share subject
        f1_pos = f1_words & positive
        f1_neg = f1_words & negative
        f2_pos = f2_words & positive
        f2_neg = f2_words & negative
        
        if (f1_pos and f2_neg) or (f1_neg and f2_pos):
            return 0.6
    
    return 0.0


# ============================================
# Database Operations
# ============================================

class MemoryDB:
    def __init__(self):
        self.db: Optional[Surreal] = None
    
    async def connect(self):
        """Connect to SurrealDB."""
        # Newer SDK versions use http:// URL and connect in constructor
        url = CONFIG["connection"]
        if url.startswith("ws://"):
            url = url.replace("ws://", "http://").replace("/rpc", "")
        self.db = Surreal(url)
        self.db.signin({"username": CONFIG["user"], "password": CONFIG["password"]})
        self.db.use(CONFIG["namespace"], CONFIG["database"])
    
    async def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()
    
    async def store_fact(
        self,
        content: str,
        source: str = "inferred",
        confidence: Optional[float] = None,
        tags: Optional[list[str]] = None,
    ) -> dict:
        """Store a new fact with embedding and entity extraction."""
        
        # Set confidence based on source
        if confidence is None:
            if source == "explicit":
                confidence = CONFIG["confidence"]["initial_explicit"]
            else:
                confidence = CONFIG["confidence"]["initial_inferred"]
        
        # Generate embedding
        embedding = get_embedding(content)
        
        # Check for similar/contradicting facts
        similar = await self.search(content, max_results=5, min_score=0.85)
        
        # Create the fact
        result = await self.db.create("fact", {
            "content": content,
            "embedding": embedding,
            "source": source,
            "confidence": confidence,
            "tags": tags or [],
        })
        
        fact_id = result[0]["id"] if isinstance(result, list) else result["id"]
        
        # Check for contradictions and create edges
        for sim_fact in similar:
            contradiction_strength = check_contradiction(content, sim_fact["content"])
            if contradiction_strength > 0.5:
                await self.db.query("""
                    RELATE $new->relates_to->$old SET 
                        relationship = "contradicts",
                        strength = $strength,
                        detection_method = "pattern"
                """, {
                    "new": fact_id,
                    "old": sim_fact["id"],
                    "strength": contradiction_strength,
                })
                print(f"  ⚠️  Contradicts: {sim_fact['content'][:50]}...")
        
        # Extract and link entities
        entities = extract_entities(content)
        for entity in entities:
            # Find or create entity
            existing = await self.db.query(
                "SELECT * FROM entity WHERE name = $name",
                {"name": entity["name"]}
            )
            
            if existing and existing[0]:
                entity_id = existing[0][0]["id"]
            else:
                entity_embedding = get_embedding(entity["name"])
                entity_result = await self.db.create("entity", {
                    "name": entity["name"],
                    "type": entity["type"],
                    "embedding": entity_embedding,
                    "confidence": 0.5,
                })
                entity_id = entity_result[0]["id"] if isinstance(entity_result, list) else entity_result["id"]
            
            # Create mention edge
            await self.db.query("""
                RELATE $fact->mentions->$entity SET role = "subject"
            """, {"fact": fact_id, "entity": entity_id})
        
        return {"id": fact_id, "content": content, "confidence": confidence}
    
    async def search(
        self,
        query: str,
        max_results: int = 10,
        min_score: float = 0.5,
    ) -> list[dict]:
        """Semantic search for facts."""
        embedding = get_embedding(query)
        
        results = await self.db.query("""
            SELECT 
                *,
                vector::similarity::cosine(embedding, $embedding) AS similarity,
                fn::effective_confidence(id) AS effective_confidence,
                (vector::similarity::cosine(embedding, $embedding) * fn::effective_confidence(id)) AS weighted_score
            FROM fact
            WHERE archived = false
                AND vector::similarity::cosine(embedding, $embedding) > $min_score
            ORDER BY weighted_score DESC
            LIMIT $limit
        """, {
            "embedding": embedding,
            "min_score": min_score,
            "limit": max_results,
        })
        
        return results[0] if results else []
    
    async def get_fact_context(self, fact_id: str) -> dict:
        """Get a fact with full context."""
        results = await self.db.query(
            "RETURN fn::get_fact_context($fact_id)",
            {"fact_id": fact_id}
        )
        return results[0][0] if results and results[0] else None
    
    async def apply_decay(self) -> int:
        """Apply time decay to all facts."""
        # Get facts that haven't been accessed in over 30 days
        results = await self.db.query("""
            UPDATE fact SET 
                confidence = confidence * 0.95
            WHERE last_accessed < time::now() - 30d
            RETURN BEFORE
        """)
        
        count = len(results[0]) if results and results[0] else 0
        return count
    
    async def prune(self) -> dict:
        """Remove low-confidence stale facts."""
        days = CONFIG["maintenance"]["prune_after_days"]
        min_conf = CONFIG["maintenance"]["min_confidence"]
        
        # Archive heavily contradicted facts
        archived = await self.db.query(f"""
            UPDATE fact SET archived = true
            WHERE fn::effective_confidence(id) < 0.3
                AND fn::contradiction_drain(id) > 0.3
            RETURN BEFORE
        """)
        
        # Delete low-confidence stale facts
        deleted = await self.db.query(f"""
            DELETE FROM fact 
            WHERE fn::effective_confidence(id) < {min_conf}
                AND last_confirmed < time::now() - {days}d
            RETURN BEFORE
        """)
        
        # Cleanup orphaned edges
        await self.db.query("""
            DELETE FROM relates_to WHERE in.archived = true OR out.archived = true;
            DELETE FROM mentions WHERE in.archived = true;
        """)
        
        # Cleanup orphaned entities
        await self.db.query(f"""
            DELETE FROM entity 
            WHERE count(<-mentions) = 0 
                AND created_at < time::now() - {days}d
        """)
        
        return {
            "archived": len(archived[0]) if archived and archived[0] else 0,
            "deleted": len(deleted[0]) if deleted and deleted[0] else 0,
        }
    
    async def consolidate(self) -> int:
        """Merge near-duplicate facts."""
        threshold = CONFIG["maintenance"]["consolidate_similarity"]
        
        # Find potential duplicates
        facts = await self.db.query("SELECT * FROM fact WHERE archived = false")
        if not facts or not facts[0]:
            return 0
        
        merged = 0
        facts = facts[0]
        
        for i, fact in enumerate(facts):
            for other in facts[i+1:]:
                # Calculate similarity
                sim_result = await self.db.query("""
                    RETURN vector::similarity::cosine($e1, $e2)
                """, {"e1": fact["embedding"], "e2": other["embedding"]})
                
                similarity = sim_result[0][0] if sim_result and sim_result[0] else 0
                
                if similarity >= threshold:
                    # Keep the one with higher confidence
                    if fact["confidence"] >= other["confidence"]:
                        keep, remove = fact, other
                    else:
                        keep, remove = other, fact
                    
                    # Boost kept fact's confidence slightly
                    await self.db.query("""
                        UPDATE $id SET 
                            confidence = math::min(1.0, confidence + 0.05),
                            last_confirmed = time::now()
                    """, {"id": keep["id"]})
                    
                    # Archive the duplicate
                    await self.db.query("""
                        UPDATE $id SET archived = true
                    """, {"id": remove["id"]})
                    
                    merged += 1
        
        return merged
    
    async def get_stats(self) -> dict:
        """Get database statistics."""
        facts = await self.db.query("SELECT count() FROM fact WHERE archived = false GROUP ALL")
        entities = await self.db.query("SELECT count() FROM entity GROUP ALL")
        edges = await self.db.query("SELECT count() FROM relates_to GROUP ALL")
        
        avg_conf = await self.db.query("""
            SELECT math::mean(confidence) AS avg FROM fact WHERE archived = false GROUP ALL
        """)
        
        return {
            "facts": facts[0][0]["count"] if facts and facts[0] else 0,
            "entities": entities[0][0]["count"] if entities and entities[0] else 0,
            "relationships": edges[0][0]["count"] if edges and edges[0] else 0,
            "avg_confidence": round(avg_conf[0][0]["avg"], 3) if avg_conf and avg_conf[0] else 0,
        }


# ============================================
# CLI Commands
# ============================================

async def cmd_store(args):
    """Store a new fact."""
    db = MemoryDB()
    await db.connect()
    
    try:
        tags = args.tags.split(",") if args.tags else None
        result = await db.store_fact(
            content=args.content,
            source=args.source,
            confidence=args.confidence,
            tags=tags,
        )
        print(f"✓ Stored fact: {result['id']}")
        print(f"  Content: {result['content']}")
        print(f"  Confidence: {result['confidence']}")
    finally:
        await db.close()


async def cmd_search(args):
    """Search for facts."""
    db = MemoryDB()
    await db.connect()
    
    try:
        results = await db.search(
            query=args.query,
            max_results=args.limit,
            min_score=args.min_score,
        )
        
        if not results:
            print("No results found.")
            return
        
        print(f"Found {len(results)} results:\n")
        for i, fact in enumerate(results, 1):
            eff_conf = fact.get("effective_confidence", fact.get("confidence", 0))
            sim = fact.get("similarity", 0)
            print(f"{i}. [{fact['id']}]")
            print(f"   {fact['content']}")
            print(f"   Confidence: {eff_conf:.2f} | Similarity: {sim:.2f}")
            print()
    finally:
        await db.close()


async def cmd_get(args):
    """Get a fact with context."""
    db = MemoryDB()
    await db.connect()
    
    try:
        result = await db.get_fact_context(args.fact_id)
        
        if not result:
            print(f"Fact not found: {args.fact_id}")
            return
        
        print(json.dumps(result, indent=2, default=str))
    finally:
        await db.close()


async def cmd_relate(args):
    """Create a relationship between two facts."""
    db = MemoryDB()
    await db.connect()
    
    try:
        valid_relationships = ["supports", "contradicts", "updates", "elaborates"]
        if args.relationship not in valid_relationships:
            print(f"Invalid relationship. Choose from: {', '.join(valid_relationships)}")
            return
        
        # Ensure fact IDs have proper format
        fact1 = args.fact1 if args.fact1.startswith("fact:") else f"fact:{args.fact1}"
        fact2 = args.fact2 if args.fact2.startswith("fact:") else f"fact:{args.fact2}"
        
        result = await db.db.query("""
            RELATE $from->relates_to->$to SET 
                relationship = $rel,
                strength = $strength,
                detection_method = "manual"
        """, {
            "from": fact1,
            "to": fact2,
            "rel": args.relationship,
            "strength": args.strength,
        })
        
        print(f"✓ Created relationship: {fact1} --[{args.relationship}]--> {fact2}")
    finally:
        await db.close()


async def cmd_decay(args):
    """Apply time decay."""
    db = MemoryDB()
    await db.connect()
    
    try:
        count = await db.apply_decay()
        print(f"✓ Applied decay to {count} facts")
    finally:
        await db.close()


async def cmd_prune(args):
    """Prune low-confidence facts."""
    db = MemoryDB()
    await db.connect()
    
    try:
        result = await db.prune()
        print(f"✓ Pruning complete:")
        print(f"  Archived: {result['archived']} facts")
        print(f"  Deleted: {result['deleted']} facts")
    finally:
        await db.close()


async def cmd_consolidate(args):
    """Consolidate duplicate facts."""
    db = MemoryDB()
    await db.connect()
    
    try:
        count = await db.consolidate()
        print(f"✓ Consolidated {count} duplicate facts")
    finally:
        await db.close()


async def cmd_maintain(args):
    """Run full maintenance cycle."""
    db = MemoryDB()
    await db.connect()
    
    try:
        print("Running maintenance cycle...")
        
        print("\n1. Applying time decay...")
        decay_count = await db.apply_decay()
        print(f"   Decayed: {decay_count} facts")
        
        print("\n2. Pruning stale facts...")
        prune_result = await db.prune()
        print(f"   Archived: {prune_result['archived']}")
        print(f"   Deleted: {prune_result['deleted']}")
        
        print("\n3. Consolidating duplicates...")
        consolidate_count = await db.consolidate()
        print(f"   Merged: {consolidate_count} facts")
        
        print("\n✓ Maintenance complete!")
    finally:
        await db.close()


async def cmd_stats(args):
    """Show database statistics."""
    db = MemoryDB()
    await db.connect()
    
    try:
        stats = await db.get_stats()
        print("=== Knowledge Graph Statistics ===")
        print(f"Facts: {stats['facts']}")
        print(f"Entities: {stats['entities']}")
        print(f"Relationships: {stats['relationships']}")
        print(f"Avg Confidence: {stats['avg_confidence']}")
    finally:
        await db.close()


# ============================================
# Main
# ============================================

def main():
    parser = argparse.ArgumentParser(
        description="SurrealDB Knowledge Graph Memory CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # store
    store_parser = subparsers.add_parser("store", help="Store a new fact")
    store_parser.add_argument("content", help="The fact content")
    store_parser.add_argument("--source", default="explicit", choices=["explicit", "inferred"])
    store_parser.add_argument("--confidence", type=float, help="Initial confidence (0-1)")
    store_parser.add_argument("--tags", help="Comma-separated tags")
    store_parser.set_defaults(func=cmd_store)
    
    # search
    search_parser = subparsers.add_parser("search", help="Search for facts")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=10)
    search_parser.add_argument("--min-score", type=float, default=0.5)
    search_parser.set_defaults(func=cmd_search)
    
    # get
    get_parser = subparsers.add_parser("get", help="Get fact with context")
    get_parser.add_argument("fact_id", help="Fact ID (e.g., fact:abc123)")
    get_parser.set_defaults(func=cmd_get)
    
    # relate
    relate_parser = subparsers.add_parser("relate", help="Create relationship between facts")
    relate_parser.add_argument("fact1", help="Source fact ID")
    relate_parser.add_argument("relationship", choices=["supports", "contradicts", "updates", "elaborates"],
                               help="Relationship type")
    relate_parser.add_argument("fact2", help="Target fact ID")
    relate_parser.add_argument("--strength", type=float, default=0.5, help="Relationship strength (0-1)")
    relate_parser.set_defaults(func=cmd_relate)
    
    # decay
    decay_parser = subparsers.add_parser("decay", help="Apply time decay")
    decay_parser.set_defaults(func=cmd_decay)
    
    # prune
    prune_parser = subparsers.add_parser("prune", help="Prune stale facts")
    prune_parser.set_defaults(func=cmd_prune)
    
    # consolidate
    consolidate_parser = subparsers.add_parser("consolidate", help="Merge duplicates")
    consolidate_parser.set_defaults(func=cmd_consolidate)
    
    # maintain
    maintain_parser = subparsers.add_parser("maintain", help="Full maintenance")
    maintain_parser.set_defaults(func=cmd_maintain)
    
    # stats
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.set_defaults(func=cmd_stats)
    
    args = parser.parse_args()
    asyncio.run(args.func(args))


if __name__ == "__main__":
    main()
