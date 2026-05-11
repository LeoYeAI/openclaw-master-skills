#!/usr/bin/env python3
"""
Simple knowledge graph tool for direct CLI usage.
Usage: knowledge-tool.py <command> [args]

Commands:
  search <query> [--limit N]
  recall <fact_id|query>
  store <content> [--confidence N]
  stats
"""

import argparse
import json
import os
import sys

# Configuration
SURREAL_CONFIG = {
    "connection": "http://localhost:8000",
    "namespace": "openclaw",
    "database": "memory",
    "user": "root",
    "password": "root",
}

def get_db():
    from surrealdb import Surreal
    db = Surreal(SURREAL_CONFIG["connection"])
    db.signin({"username": SURREAL_CONFIG["user"], "password": SURREAL_CONFIG["password"]})
    db.use(SURREAL_CONFIG["namespace"], SURREAL_CONFIG["database"])
    return db

def get_embedding(text):
    import openai
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    client = openai.OpenAI(api_key=api_key)
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding

def cmd_search(args):
    db = get_db()
    embedding = get_embedding(args.query)
    
    if embedding:
        results = db.query("""
            SELECT id, content, confidence, source,
                vector::similarity::cosine(embedding, $embedding) AS similarity
            FROM fact
            WHERE archived = false
            ORDER BY similarity DESC
            LIMIT $limit
        """, {"embedding": embedding, "limit": args.limit})
    else:
        results = db.query("""
            SELECT id, content, confidence, source
            FROM fact
            WHERE archived = false AND content CONTAINS $query
            ORDER BY confidence DESC
            LIMIT $limit
        """, {"query": args.query, "limit": args.limit})
    
    output = {
        "query": args.query,
        "count": len(results) if results else 0,
        "facts": [
            {
                "id": str(f.get("id", "")),
                "content": f.get("content", ""),
                "confidence": round(f.get("confidence", 0), 3),
                "similarity": round(f.get("similarity", 0), 3) if f.get("similarity") else None,
            }
            for f in (results or [])
        ]
    }
    print(json.dumps(output, indent=2))

def cmd_recall(args):
    db = get_db()
    
    # If it looks like an ID, use it directly
    if args.target.startswith("fact:"):
        fact_id = args.target
    else:
        # Search for it
        embedding = get_embedding(args.target)
        if embedding:
            results = db.query("""
                SELECT id, vector::similarity::cosine(embedding, $embedding) AS sim
                FROM fact
                WHERE archived = false
                ORDER BY sim DESC
                LIMIT 1
            """, {"embedding": embedding})
        else:
            results = db.query("""
                SELECT id FROM fact WHERE content CONTAINS $query LIMIT 1
            """, {"query": args.target})
        
        if not results:
            print(json.dumps({"error": "No matching fact found"}))
            return
        fact_id = results[0]["id"]
    
    # Get fact
    fact = db.query("SELECT * FROM $id", {"id": fact_id})
    if not fact:
        print(json.dumps({"error": f"Fact not found: {fact_id}"}))
        return
    
    fact = fact[0]
    
    # Get relations
    supporting = db.query("""
        SELECT in.content AS content, in.confidence AS confidence, strength
        FROM relates_to WHERE out = $id AND relationship = "supports"
    """, {"id": fact_id}) or []
    
    contradicting = db.query("""
        SELECT in.content AS content, in.confidence AS confidence, strength
        FROM relates_to WHERE out = $id AND relationship = "contradicts"
    """, {"id": fact_id}) or []
    
    entities = db.query("""
        SELECT out.name AS name, out.type AS type, role
        FROM mentions WHERE in = $id
    """, {"id": fact_id}) or []
    
    output = {
        "fact": {
            "id": str(fact.get("id", "")),
            "content": fact.get("content", ""),
            "confidence": fact.get("confidence", 0),
            "source": fact.get("source", ""),
            "tags": fact.get("tags", []),
        },
        "supporting": supporting,
        "contradicting": contradicting,
        "entities": entities,
    }
    print(json.dumps(output, indent=2))

def cmd_store(args):
    db = get_db()
    embedding = get_embedding(args.content)
    
    result = db.create("fact", {
        "content": args.content,
        "embedding": embedding or [],
        "source": "explicit",
        "confidence": args.confidence,
        "tags": [],
    })
    
    fact_id = result[0]["id"] if isinstance(result, list) else result.get("id")
    print(json.dumps({
        "success": True,
        "fact_id": str(fact_id),
        "content": args.content,
    }, indent=2))

def cmd_stats(args):
    db = get_db()
    
    facts = db.query("SELECT count() FROM fact WHERE archived = false GROUP ALL")
    entities = db.query("SELECT count() FROM entity GROUP ALL")
    relations = db.query("SELECT count() FROM relates_to GROUP ALL")
    avg_conf = db.query("SELECT math::mean(confidence) AS avg FROM fact WHERE archived = false GROUP ALL")
    
    output = {
        "facts": facts[0].get("count", 0) if facts else 0,
        "entities": entities[0].get("count", 0) if entities else 0,
        "relations": relations[0].get("count", 0) if relations else 0,
        "avg_confidence": round(avg_conf[0].get("avg", 0), 3) if avg_conf else 0,
    }
    print(json.dumps(output, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Knowledge Graph Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # search
    p_search = subparsers.add_parser("search", help="Search for facts")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", type=int, default=10, help="Max results")
    p_search.set_defaults(func=cmd_search)
    
    # recall
    p_recall = subparsers.add_parser("recall", help="Recall a fact with context")
    p_recall.add_argument("target", help="Fact ID or search query")
    p_recall.set_defaults(func=cmd_recall)
    
    # store
    p_store = subparsers.add_parser("store", help="Store a new fact")
    p_store.add_argument("content", help="Fact content")
    p_store.add_argument("--confidence", type=float, default=0.9, help="Confidence 0-1")
    p_store.set_defaults(func=cmd_store)
    
    # stats
    p_stats = subparsers.add_parser("stats", help="Get statistics")
    p_stats.set_defaults(func=cmd_stats)
    
    args = parser.parse_args()
    
    try:
        args.func(args)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
