#!/usr/bin/env python3
"""Web Search Mock — JSON-RPC subprocess skill for eval-skills

A mock web search skill that returns predefined results for common queries.
This demonstrates how to implement an HTTP-like Skill using the subprocess adapter.
"""
import json
import sys

# Predefined knowledge base
KNOWLEDGE_BASE = {
    "2024 nobel prize physics": {
        "result": "The 2024 Nobel Prize in Physics was awarded to John Hopfield and Geoffrey Hinton for foundational discoveries and inventions that enable machine learning with artificial neural networks.",
        "source": "nobelprize.org"
    },
    "python creator": {
        "result": "Python was created by Guido van Rossum. He began working on Python in the late 1980s and first released it in 1991.",
        "source": "python.org"
    },
    "typescript": {
        "result": "TypeScript is a strongly typed programming language that builds on JavaScript, developed and maintained by Microsoft. It was first released in October 2012.",
        "source": "typescriptlang.org"
    },
    "mcp protocol": {
        "result": "The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to LLMs. It was introduced by Anthropic.",
        "source": "modelcontextprotocol.io"
    },
    "eval-skills": {
        "result": "eval-skills is a framework-agnostic AI Agent Skill unit testing tool, providing a complete find -> create -> select -> eval -> report pipeline.",
        "source": "github.com/eval-skills"
    },
    "largest planet": {
        "result": "Jupiter is the largest planet in our solar system. It has a mass of about 1.898 x 10^27 kg, which is more than twice the mass of all the other planets combined.",
        "source": "nasa.gov"
    },
    "speed of light": {
        "result": "The speed of light in vacuum is approximately 299,792,458 meters per second (about 3 x 10^8 m/s).",
        "source": "physics.nist.gov"
    },
    "machine learning": {
        "result": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. Key approaches include supervised, unsupervised, and reinforcement learning.",
        "source": "wikipedia.org"
    }
}


def invoke(params):
    """Search the mock knowledge base."""
    query = params.get("query", "").lower().strip()

    if not query:
        return {"result": "Error: empty query", "source": ""}

    # Exact match
    if query in KNOWLEDGE_BASE:
        return KNOWLEDGE_BASE[query]

    # Partial match: find the best matching entry
    best_match = None
    best_score = 0
    for key, value in KNOWLEDGE_BASE.items():
        # Count matching words
        query_words = set(query.split())
        key_words = set(key.split())
        common = len(query_words & key_words)
        if common > best_score:
            best_score = common
            best_match = value

    if best_match and best_score > 0:
        return best_match

    return {
        "result": f"No results found for: {query}",
        "source": ""
    }


def healthcheck(params):
    return {"status": "healthy", "entries": len(KNOWLEDGE_BASE)}


def main():
    raw = sys.stdin.read()
    try:
        request = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps({
            "jsonrpc": "2.0",
            "error": {"code": -32700, "message": "Parse error"},
            "id": None
        }))
        return

    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id", 1)

    handlers = {"invoke": invoke, "healthcheck": healthcheck}
    handler = handlers.get(method)

    if handler is None:
        response = {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": f"Unknown method: {method}"},
            "id": req_id
        }
    else:
        try:
            result = handler(params)
            response = {"jsonrpc": "2.0", "result": result, "id": req_id}
        except Exception as e:
            response = {
                "jsonrpc": "2.0",
                "error": {"code": -32000, "message": str(e)},
                "id": req_id
            }

    print(json.dumps(response))


if __name__ == "__main__":
    main()
