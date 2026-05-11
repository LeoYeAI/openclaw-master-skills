#!/usr/bin/env python3
"""
Knowledge Store & Recall Tools for SurrealDB Memory

These tools provide the agent interface to the knowledge graph.
- knowledge_store: Store facts with confidence scoring
- knowledge_recall: Retrieve relevant knowledge with graph context

Usage:
    python3 knowledge-tools.py store "Charles prefers direct communication" --source explicit
    python3 knowledge-tools.py recall "communication preferences" --limit 5
    python3 knowledge-tools.py context <session_key>  # Get cached context for session
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Session cache for async prefetch results
SESSION_CACHE_FILE = Path.home() / ".openclaw" / "memory" / "session-cache.json"

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
# Configuration
# ============================================

CONFIG = {
    "connection": "http://localhost:8000",
    "namespace": "openclaw",
    "database": "memory",
    "user": "root",
    "password": "root",
    "embedding": {
        "model": "text-embedding-3-small",
        "dimensions": 1536,
    },
    "confidence": {
        "explicit": 0.9,
        "inferred": 0.6,
        "recalled": 0.7,
    },
}


# ============================================
# Embedding
# ============================================

def get_embedding(text: str) -> list[float]:
    """Generate embedding using OpenAI."""
    if not OPENAI_AVAILABLE:
        raise RuntimeError("openai package not installed")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    
    client = openai.OpenAI(api_key=api_key)
    response = client.embeddings.create(
        input=text,
        model=CONFIG["embedding"]["model"]
    )
    return response.data[0].embedding


# ============================================
# Entity Extraction
# ============================================

def extract_entities(text: str) -> list[dict]:
    """Extract entities from text using patterns."""
    entities = []
    
    skip_words = {"the", "a", "an", "this", "that", "it", "i", "we", "they", "he", "she", 
                  "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
                  "do", "does", "did", "will", "would", "could", "should", "may", "might",
                  "remember", "know", "think", "said", "says", "told"}
    
    words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text)
    for word in words:
        if word.lower() not in skip_words and len(word) > 1:
            entities.append({"name": word, "type": "unknown"})
    
    projects = re.findall(r'\b([a-z]+-[a-z]+(?:-[a-z]+)*)\b', text)
    for project in projects:
        if len(project) > 3:
            entities.append({"name": project, "type": "project"})
    
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

NEGATION_PAIRS = [
    ("is", "is not"), ("likes", "dislikes"), ("prefers", "avoids"),
    ("always", "never"), ("loves", "hates"), ("can", "cannot"),
    ("will", "won't"), ("good", "bad"), ("yes", "no"),
]

def check_contradiction(fact1: str, fact2: str) -> float:
    """Check if two facts contradict. Returns strength 0-1."""
    f1 = fact1.lower()
    f2 = fact2.lower()
    
    for pos, neg in NEGATION_PAIRS:
        if pos in f1 and neg in f2:
            return 0.8
        if neg in f1 and pos in f2:
            return 0.8
    
    f1_words = set(f1.split())
    f2_words = set(f2.split())
    common = f1_words & f2_words
    
    positive = {"likes", "prefers", "enjoys", "loves", "wants", "good", "yes", "always"}
    negative = {"dislikes", "hates", "avoids", "bad", "no", "never", "not"}
    
    if len(common) >= 2:
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

class KnowledgeDB:
    def __init__(self):
        self.db = None
    
    def connect(self):
        if not SURREALDB_AVAILABLE:
            raise RuntimeError("surrealdb package not installed")
        self.db = Surreal(CONFIG["connection"])
        self.db.signin({"username": CONFIG["user"], "password": CONFIG["password"]})
        self.db.use(CONFIG["namespace"], CONFIG["database"])
    
    def close(self):
        if self.db:
            try:
                self.db.close()
            except NotImplementedError:
                pass  # HTTP connections don't need explicit close
    
    def store(self, content: str, source: str = "explicit", confidence: float = None,
              tags: list = None) -> dict:
        """Store a fact with embedding and entity extraction."""
        
        if confidence is None:
            confidence = CONFIG["confidence"].get(source, 0.6)
        
        embedding = get_embedding(content)
        similar = self.search(content, limit=5, min_score=0.85)
        
        result = self.db.create("fact", {
            "content": content,
            "embedding": embedding,
            "source": source,
            "confidence": confidence,
            "tags": tags or [],
        })
        
        fact_id = result[0]["id"] if isinstance(result, list) else result["id"]
        
        contradictions = []
        for sim in similar:
            strength = check_contradiction(content, sim.get("content", ""))
            if strength > 0.5:
                self.db.query("""
                    RELATE $new->relates_to->$old SET 
                        relationship = "contradicts",
                        strength = $strength,
                        detection_method = "pattern"
                """, {"new": fact_id, "old": sim["id"], "strength": strength})
                contradictions.append(sim["content"][:50])
        
        entities = extract_entities(content)
        linked_entities = []
        for entity in entities:
            existing = self.db.query(
                "SELECT * FROM entity WHERE name = $name",
                {"name": entity["name"]}
            )
            
            entity_id = None
            if existing and existing[0]:
                result_list = existing[0] if isinstance(existing, list) else existing
                if isinstance(result_list, list) and len(result_list) > 0:
                    first = result_list[0]
                    if isinstance(first, dict) and "id" in first:
                        entity_id = first["id"]
            
            if not entity_id:
                entity_emb = get_embedding(entity["name"])
                ent_result = self.db.create("entity", {
                    "name": entity["name"],
                    "type": entity["type"],
                    "embedding": entity_emb,
                    "confidence": 0.5,
                })
                entity_id = ent_result[0]["id"] if isinstance(ent_result, list) else ent_result["id"]
            
            self.db.query(
                "RELATE $fact->mentions->$entity SET role = 'subject'",
                {"fact": fact_id, "entity": entity_id}
            )
            linked_entities.append(entity["name"])
        
        return {
            "id": str(fact_id),
            "content": content,
            "confidence": confidence,
            "entities": linked_entities,
            "contradictions": contradictions,
        }
    
    def search(self, query: str, limit: int = 10, min_score: float = 0.5) -> list:
        """Semantic search with confidence weighting."""
        embedding = get_embedding(query)
        
        results = self.db.query("""
            SELECT 
                id, content, confidence, source, tags,
                vector::similarity::cosine(embedding, $embedding) AS similarity,
                (vector::similarity::cosine(embedding, $embedding) * confidence) AS weighted_score
            FROM fact
            WHERE archived = false
                AND vector::similarity::cosine(embedding, $embedding) > $min_score
            ORDER BY weighted_score DESC
            LIMIT $limit
        """, {"embedding": embedding, "min_score": min_score, "limit": limit})
        
        # Results come directly as list of dicts (not nested)
        facts = results if isinstance(results, list) else []
        
        # Convert RecordID objects to strings
        for fact in facts:
            if isinstance(fact, dict) and "id" in fact and hasattr(fact["id"], "__str__"):
                fact["id"] = str(fact["id"])
        return facts
    
    def recall_with_context(self, query: str, limit: int = 5) -> dict:
        """Recall facts with graph context (related facts, entities)."""
        
        facts = self.search(query, limit=limit, min_score=0.4)
        
        if not facts:
            return {"facts": [], "entities": [], "context": ""}
        
        all_entities = set()
        related_facts = []
        
        for fact in facts:
            if not isinstance(fact, dict):
                continue
            fact_id = fact.get("id")
            if not fact_id:
                continue
            
            try:
                entities = self.db.query("""
                    SELECT out.name AS name, out.type AS type, role
                    FROM mentions WHERE in = type::thing($fact_id)
                """, {"fact_id": fact_id})
                
                # Results come directly as list
                if entities and isinstance(entities, list):
                    for e in entities:
                        if isinstance(e, dict) and "name" in e:
                            all_entities.add(e["name"])
                
                supporters = self.db.query("""
                    SELECT in.content AS content, in.confidence AS confidence
                    FROM relates_to 
                    WHERE out = type::thing($fact_id) AND relationship = "supports"
                    LIMIT 3
                """, {"fact_id": fact_id})
                
                if supporters and isinstance(supporters, list):
                    for s in supporters:
                        if isinstance(s, dict) and s.get("content") not in [f.get("content") for f in facts]:
                            related_facts.append(s)
                
                self.db.query("""
                    UPDATE type::thing($fact_id) SET 
                        access_count = access_count + 1,
                        last_accessed = time::now()
                """, {"fact_id": fact_id})
            except Exception:
                pass  # Skip errors in graph traversal
        
        context_lines = ["## Relevant Knowledge"]
        for fact in facts[:5]:
            conf = fact.get("confidence", 0)
            context_lines.append(f"- {fact['content']} (confidence: {conf:.1%})")
        
        if related_facts:
            context_lines.append("\n### Supporting Context")
            for rf in related_facts[:3]:
                context_lines.append(f"- {rf['content']}")
        
        if all_entities:
            context_lines.append(f"\n### Entities: {', '.join(list(all_entities)[:10])}")
        
        return {
            "facts": facts,
            "related": related_facts,
            "entities": list(all_entities),
            "context": "\n".join(context_lines),
        }


# ============================================
# Session Cache (for async prefetch)
# ============================================

def load_session_cache() -> dict:
    if SESSION_CACHE_FILE.exists():
        try:
            with open(SESSION_CACHE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {}

def save_session_cache(cache: dict):
    SESSION_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SESSION_CACHE_FILE, "w") as f:
        json.dump(cache, f)

def cache_context(session_key: str, context: str, query: str):
    cache = load_session_cache()
    cache[session_key] = {
        "context": context,
        "query": query,
        "timestamp": datetime.now().isoformat(),
    }
    if len(cache) > 100:
        sorted_keys = sorted(cache.keys(), key=lambda k: cache[k].get("timestamp", ""))
        for k in sorted_keys[:-100]:
            del cache[k]
    save_session_cache(cache)

def get_cached_context(session_key: str) -> str:
    cache = load_session_cache()
    entry = cache.get(session_key)
    if entry:
        return entry.get("context", "")
    return ""


# ============================================
# Health Check
# ============================================

def check_health() -> dict:
    health = {
        "surrealdb_available": SURREALDB_AVAILABLE,
        "openai_available": OPENAI_AVAILABLE,
        "api_key_set": bool(os.environ.get("OPENAI_API_KEY")),
        "server_reachable": False,
        "error": None,
    }
    
    if SURREALDB_AVAILABLE:
        try:
            db = KnowledgeDB()
            db.connect()
            db.close()
            health["server_reachable"] = True
        except Exception as e:
            health["error"] = str(e)
    
    return health


# ============================================
# CLI Commands
# ============================================

def cmd_store(args):
    """Store a fact."""
    try:
        db = KnowledgeDB()
        db.connect()
        try:
            result = db.store(
                content=args.content,
                source=args.source,
                confidence=args.confidence,
                tags=args.tags.split(",") if args.tags else None,
            )
            print(json.dumps(result, indent=2))
        finally:
            db.close()
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "error": str(e),
            "content": args.content,
            "fallback": "Fact not stored - knowledge graph unavailable",
        }, indent=2))
        sys.exit(0)

def cmd_recall(args):
    """Recall knowledge with context."""
    try:
        db = KnowledgeDB()
        db.connect()
        try:
            result = db.recall_with_context(args.query, limit=args.limit)
            
            if args.format == "context":
                print(result["context"])
            else:
                print(json.dumps(result, indent=2, default=str))
            
            if args.session:
                cache_context(args.session, result["context"], args.query)
        finally:
            db.close()
    except Exception as e:
        fallback = {
            "status": "degraded",
            "error": str(e),
            "facts": [],
            "related": [],
            "entities": [],
            "context": "# Knowledge graph unavailable",
            "fallback": "Proceeding without stored knowledge context",
        }
        if args.format == "context":
            print("# Knowledge graph unavailable")
        else:
            print(json.dumps(fallback, indent=2))
        sys.exit(0)

def cmd_prefetch(args):
    """Prefetch and cache knowledge for a session."""
    try:
        db = KnowledgeDB()
        db.connect()
        try:
            result = db.recall_with_context(args.query, limit=args.limit)
            facts_count = len(result.get('facts', []))
            cache_context(args.session, result["context"], args.query)
            print(json.dumps({
                "status": "success",
                "cached": facts_count,
                "session": args.session,
            }))
        finally:
            db.close()
    except Exception as e:
        print(json.dumps({
            "status": "skipped",
            "error": str(e),
            "session": args.session,
        }))
        sys.exit(0)

def cmd_context(args):
    """Get cached context for a session."""
    context = get_cached_context(args.session)
    if context:
        print(context)
    else:
        print("# No cached knowledge context")

def cmd_search(args):
    """Simple semantic search."""
    try:
        db = KnowledgeDB()
        db.connect()
        try:
            results = db.search(args.query, limit=args.limit, min_score=args.min_score)
            for i, fact in enumerate(results, 1):
                sim = fact.get("similarity", 0)
                conf = fact.get("confidence", 0)
                print(f"{i}. [{sim:.2f} sim, {conf:.1%} conf] {fact['content']}")
        finally:
            db.close()
    except Exception as e:
        print(f"Search unavailable: {e}")
        sys.exit(0)

def cmd_health(args):
    """Check system health."""
    health = check_health()
    print(json.dumps(health, indent=2))


# ============================================
# Main
# ============================================

def main():
    parser = argparse.ArgumentParser(description="Knowledge Store & Recall Tools")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # store
    store_p = subparsers.add_parser("store", help="Store a fact")
    store_p.add_argument("content", help="Fact content")
    store_p.add_argument("--source", default="explicit", choices=["explicit", "inferred"])
    store_p.add_argument("--confidence", type=float)
    store_p.add_argument("--tags", help="Comma-separated tags")
    store_p.set_defaults(func=cmd_store)
    
    # recall
    recall_p = subparsers.add_parser("recall", help="Recall knowledge with context")
    recall_p.add_argument("query", help="Query string")
    recall_p.add_argument("--limit", type=int, default=5)
    recall_p.add_argument("--session", help="Session key for caching")
    recall_p.add_argument("--format", choices=["json", "context"], default="json")
    recall_p.set_defaults(func=cmd_recall)
    
    # prefetch
    prefetch_p = subparsers.add_parser("prefetch", help="Prefetch and cache for session")
    prefetch_p.add_argument("query", help="Query string")
    prefetch_p.add_argument("session", help="Session key")
    prefetch_p.add_argument("--limit", type=int, default=5)
    prefetch_p.set_defaults(func=cmd_prefetch)
    
    # context
    context_p = subparsers.add_parser("context", help="Get cached context")
    context_p.add_argument("session", help="Session key")
    context_p.set_defaults(func=cmd_context)
    
    # search
    search_p = subparsers.add_parser("search", help="Simple semantic search")
    search_p.add_argument("query", help="Query string")
    search_p.add_argument("--limit", type=int, default=10)
    search_p.add_argument("--min-score", type=float, default=0.5)
    search_p.set_defaults(func=cmd_search)
    
    # health
    health_p = subparsers.add_parser("health", help="Check system health")
    health_p.set_defaults(func=cmd_health)
    
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
