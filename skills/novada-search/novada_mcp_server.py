#!/usr/bin/env python3
"""Novada Search MCP Server (stdio JSON-RPC)."""

import json
import sys
from novada_search import NovadaSearch, NovadaSearchError


def handle_initialize(_params):
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "novada-search", "version": "1.0.8"},
    }


def handle_tools_list():
    return {
        "tools": [
            {
                "name": "novada_search",
                "description": "Multi-engine web search for AI agents. Supports Google, Bing, and more. Use scene='news' for latest headlines, scene='academic' for research papers, scene='jobs' for job listings, scene='video' for tutorials. Use mode='auto' to detect intent, mode='multi' for parallel multi-engine search with dedup. Returns structured JSON with unified_results ranked by relevance and cross-engine agreement.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "scene": {"type": "string", "enum": ["shopping", "local", "jobs", "academic", "video", "news", "travel", "finance", "images"]},
                        "mode": {"type": "string", "enum": ["auto", "multi"]},
                        "max_results": {"type": "integer", "default": 10},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "novada_extract",
                "description": "Extract clean content from URL.",
                "inputSchema": {
                    "type": "object",
                    "properties": {"url": {"type": "string"}},
                    "required": ["url"],
                },
            },
            {
                "name": "novada_research",
                "description": "Deep research: search the web then extract full content from top results. Note: this feature is in beta and may not return extracted content for all URLs. Returns search results plus attempted extraction from top sources.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Research query"},
                        "max_sources": {"type": "integer", "default": 5, "description": "Sources to extract (1-10)"},
                        "scene": {"type": "string", "enum": ["shopping", "local", "jobs", "academic", "video", "news", "travel", "finance", "images"]}
                    },
                    "required": ["query"]
                }
            },
        ]
    }


def handle_tool_call(name, arguments):
    client = NovadaSearch()
    if name == "novada_search":
        result = client.search(
            query=arguments["query"],
            scene=arguments.get("scene"),
            mode=arguments.get("mode"),
            max_results=arguments.get("max_results", 10),
            format="agent-json",
        )
        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
    if name == "novada_extract":
        result = client.extract(url=arguments["url"])
        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
    if name == "novada_research":
        result = client.research(
            query=arguments["query"],
            max_sources=arguments.get("max_sources", 5),
            scene=arguments.get("scene"),
        )
        return [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}]
    raise ValueError(f"Unknown tool: {name}")


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = request.get("method", "")
        params = request.get("params", {})
        req_id = request.get("id")

        try:
            if method == "initialize":
                result = handle_initialize(params)
            elif method == "notifications/initialized":
                continue
            elif method == "tools/list":
                result = handle_tools_list()
            elif method == "tools/call":
                content = handle_tool_call(params.get("name", ""), params.get("arguments", {}))
                result = {"content": content}
            else:
                result = {}
            response = {"jsonrpc": "2.0", "id": req_id, "result": result}
        except NovadaSearchError as e:
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": f"Novada Search error: {e}"}], "isError": True},
            }
        except Exception as e:
            response = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}}

        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
