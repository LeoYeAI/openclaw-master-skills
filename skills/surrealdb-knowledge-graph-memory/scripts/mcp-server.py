#!/usr/bin/env python3
"""
MCP Server for SurrealDB Knowledge Graph Memory

Exposes tools for knowledge recall, search, and storage.
Run with: python3 mcp-server.py
"""

import json
import sys
import os
from pathlib import Path

# Add the scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# Configuration
SURREAL_CONFIG = {
    "connection": "http://localhost:8000",
    "namespace": "openclaw", 
    "database": "memory",
    "user": "root",
    "password": "root",
}

try:
    from surrealdb import Surreal
    import openai
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False

# MCP Protocol helpers
def send_response(id, result=None, error=None):
    """Send JSON-RPC response."""
    response = {"jsonrpc": "2.0", "id": id}
    if error:
        response["error"] = error
    else:
        response["result"] = result
    print(json.dumps(response), flush=True)

def send_notification(method, params=None):
    """Send JSON-RPC notification."""
    notification = {"jsonrpc": "2.0", "method": method}
    if params:
        notification["params"] = params
    print(json.dumps(notification), flush=True)

# Database helpers
def get_db():
    """Get database connection."""
    if not DEPS_AVAILABLE:
        return None
    db = Surreal(SURREAL_CONFIG["connection"])
    db.signin({"username": SURREAL_CONFIG["user"], "password": SURREAL_CONFIG["password"]})
    db.use(SURREAL_CONFIG["namespace"], SURREAL_CONFIG["database"])
    return db

def close_db(db):
    """Safely close database connection."""
    if db:
        try:
            db.close()
        except (NotImplementedError, AttributeError):
            pass  # HTTP connections don't need explicit close

def get_embedding(text: str) -> list:
    """Generate embedding for text."""
    if not DEPS_AVAILABLE:
        return []
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return []
    client = openai.OpenAI(api_key=api_key)
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding

# Tool implementations
def knowledge_search(query: str, limit: int = 10, min_confidence: float = 0.3) -> dict:
    """Search for facts in the knowledge graph."""
    if not DEPS_AVAILABLE:
        return {"error": "Dependencies not available (surrealdb, openai)"}
    
    try:
        db = get_db()
        embedding = get_embedding(query)
        
        if not embedding:
            # Fallback to text search
            results = db.query("""
                SELECT id, content, confidence, source, tags
                FROM fact
                WHERE archived = false
                    AND content CONTAINS $query
                ORDER BY confidence DESC
                LIMIT $limit
            """, {"query": query, "limit": limit})
        else:
            results = db.query("""
                SELECT id, content, confidence, source, tags,
                    vector::similarity::cosine(embedding, $embedding) AS similarity
                FROM fact
                WHERE archived = false
                    AND confidence >= $min_conf
                ORDER BY similarity DESC
                LIMIT $limit
            """, {"embedding": embedding, "limit": limit, "min_conf": min_confidence})
        
        close_db(db)
        
        facts = results if isinstance(results, list) else []
        return {
            "query": query,
            "count": len(facts),
            "facts": [
                {
                    "id": str(f.get("id", "")),
                    "content": f.get("content", ""),
                    "confidence": f.get("confidence", 0),
                    "similarity": f.get("similarity", None),
                    "source": f.get("source", ""),
                }
                for f in facts
            ]
        }
    except Exception as e:
        return {"error": str(e)}

def knowledge_recall(fact_id: str = None, query: str = None) -> dict:
    """Recall a specific fact with its full context (related facts, entities)."""
    if not DEPS_AVAILABLE:
        return {"error": "Dependencies not available"}
    
    try:
        db = get_db()
        
        # If query provided, search first
        if query and not fact_id:
            search_result = knowledge_search(query, limit=1)
            if search_result.get("facts"):
                fact_id = search_result["facts"][0]["id"]
            else:
                return {"error": "No matching fact found", "query": query}
        
        if not fact_id:
            return {"error": "Either fact_id or query required"}
        
        # Get the fact - use select() method for record IDs
        fact_result = db.select(fact_id)
        if not fact_result:
            return {"error": f"Fact not found: {fact_id}"}
        
        # select() returns a dict directly for single records
        fact = fact_result if isinstance(fact_result, dict) else fact_result[0] if fact_result else {}
        
        # Get supporting facts
        supporting = db.query("""
            SELECT in.id AS id, in.content AS content, in.confidence AS confidence, strength
            FROM relates_to
            WHERE out = $fact_id AND relationship = "supports"
        """, {"fact_id": fact_id})
        
        # Get contradicting facts
        contradicting = db.query("""
            SELECT in.id AS id, in.content AS content, in.confidence AS confidence, strength
            FROM relates_to
            WHERE out = $fact_id AND relationship = "contradicts"
        """, {"fact_id": fact_id})
        
        # Get related entities
        entities = db.query("""
            SELECT out.id AS id, out.name AS name, out.type AS type, role
            FROM mentions
            WHERE in = $fact_id
        """, {"fact_id": fact_id})
        
        close_db(db)
        
        return {
            "fact": {
                "id": str(fact.get("id", "")),
                "content": fact.get("content", ""),
                "confidence": fact.get("confidence", 0),
                "source": fact.get("source", ""),
                "tags": fact.get("tags", []),
                "created_at": str(fact.get("created_at", "")),
            },
            "supporting_facts": supporting if isinstance(supporting, list) else [],
            "contradicting_facts": contradicting if isinstance(contradicting, list) else [],
            "entities": entities if isinstance(entities, list) else [],
        }
    except Exception as e:
        return {"error": str(e)}

def knowledge_store(content: str, source: str = "explicit", confidence: float = 0.9, tags: list = None) -> dict:
    """Store a new fact in the knowledge graph."""
    if not DEPS_AVAILABLE:
        return {"error": "Dependencies not available"}
    
    try:
        db = get_db()
        embedding = get_embedding(content)
        
        result = db.create("fact", {
            "content": content,
            "embedding": embedding,
            "source": source,
            "confidence": confidence,
            "tags": tags or [],
        })
        
        fact_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        close_db(db)
        
        return {
            "success": True,
            "fact_id": str(fact_id),
            "content": content,
            "confidence": confidence,
        }
    except Exception as e:
        return {"error": str(e)}

def knowledge_stats() -> dict:
    """Get knowledge graph statistics."""
    if not DEPS_AVAILABLE:
        return {"error": "Dependencies not available"}
    
    try:
        db = get_db()
        
        facts = db.query("SELECT count() FROM fact WHERE archived = false GROUP ALL")
        entities = db.query("SELECT count() FROM entity GROUP ALL")
        relations = db.query("SELECT count() FROM relates_to GROUP ALL")
        avg_conf = db.query("SELECT math::mean(confidence) AS avg FROM fact WHERE archived = false GROUP ALL")
        
        close_db(db)
        
        return {
            "facts": facts[0].get("count", 0) if facts else 0,
            "entities": entities[0].get("count", 0) if entities else 0,
            "relations": relations[0].get("count", 0) if relations else 0,
            "avg_confidence": avg_conf[0].get("avg", 0) if avg_conf else 0,
        }
    except Exception as e:
        return {"error": str(e)}

# MCP Tool definitions
TOOLS = [
    {
        "name": "knowledge_search",
        "description": "Search the knowledge graph for facts matching a query. Returns semantically similar facts ranked by relevance and confidence.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query - natural language description of what you're looking for"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 10)",
                    "default": 10
                },
                "min_confidence": {
                    "type": "number",
                    "description": "Minimum confidence threshold 0-1 (default: 0.3)",
                    "default": 0.3
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "knowledge_recall",
        "description": "Recall a specific fact with its full context including supporting facts, contradicting facts, and related entities.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "fact_id": {
                    "type": "string",
                    "description": "The ID of the fact to recall (e.g., 'fact:abc123')"
                },
                "query": {
                    "type": "string",
                    "description": "Alternative: search query to find the fact"
                }
            }
        }
    },
    {
        "name": "knowledge_store",
        "description": "Store a new fact in the knowledge graph. Use for important information that should be remembered.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The fact content - a clear, single assertion"
                },
                "source": {
                    "type": "string",
                    "description": "Source type: 'explicit' (user stated), 'inferred' (derived)",
                    "default": "explicit"
                },
                "confidence": {
                    "type": "number",
                    "description": "Confidence level 0-1 (default: 0.9 for explicit)",
                    "default": 0.9
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional tags for categorization"
                }
            },
            "required": ["content"]
        }
    },
    {
        "name": "knowledge_stats",
        "description": "Get statistics about the knowledge graph (fact count, entity count, relationships, average confidence).",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

# Request handlers
def handle_initialize(id, params):
    """Handle initialize request."""
    send_response(id, {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {}
        },
        "serverInfo": {
            "name": "surrealdb-memory",
            "version": "1.1.0"
        }
    })

def handle_tools_list(id, params):
    """Handle tools/list request."""
    send_response(id, {"tools": TOOLS})

def handle_tools_call(id, params):
    """Handle tools/call request."""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    if tool_name == "knowledge_search":
        result = knowledge_search(
            query=arguments.get("query", ""),
            limit=arguments.get("limit", 10),
            min_confidence=arguments.get("min_confidence", 0.3)
        )
    elif tool_name == "knowledge_recall":
        result = knowledge_recall(
            fact_id=arguments.get("fact_id"),
            query=arguments.get("query")
        )
    elif tool_name == "knowledge_store":
        result = knowledge_store(
            content=arguments.get("content", ""),
            source=arguments.get("source", "explicit"),
            confidence=arguments.get("confidence", 0.9),
            tags=arguments.get("tags")
        )
    elif tool_name == "knowledge_stats":
        result = knowledge_stats()
    else:
        send_response(id, error={"code": -32601, "message": f"Unknown tool: {tool_name}"})
        return
    
    send_response(id, {
        "content": [
            {"type": "text", "text": json.dumps(result, indent=2)}
        ]
    })

def main():
    """Main MCP server loop."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue
        
        method = request.get("method")
        id = request.get("id")
        params = request.get("params", {})
        
        if method == "initialize":
            handle_initialize(id, params)
        elif method == "tools/list":
            handle_tools_list(id, params)
        elif method == "tools/call":
            handle_tools_call(id, params)
        elif method == "notifications/initialized":
            pass  # Acknowledgment, no response needed
        else:
            if id is not None:
                send_response(id, error={"code": -32601, "message": f"Unknown method: {method}"})

if __name__ == "__main__":
    main()
