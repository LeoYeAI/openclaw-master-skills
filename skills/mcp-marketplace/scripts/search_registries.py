#!/usr/bin/env python3
"""Search MCP server registries: curated list + ClawHub bundle lookup + npm fallback."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


def load_known_servers(base_dir: str) -> list[dict]:
    path = Path(base_dir) / "assets" / "known_servers.json"
    try:
        with open(path) as f:
            return json.load(f)["servers"]
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, KeyError):
        return []


def load_clawhub_bundles(base_dir: str) -> dict:
    path = Path(base_dir) / "assets" / "clawhub_bundles.json"
    try:
        with open(path) as f:
            return json.load(f)["bundles"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return {}


def normalize_query(query: str) -> str:
    q = query.lower().strip()
    for suffix in ["mcp-server", "mcp server", "mcp", "server"]:
        if q.endswith(suffix) and len(q) > len(suffix):
            q = q[: -len(suffix)].strip().rstrip("-").strip()
    for prefix in ["mcp-server-", "mcp server ", "mcp-", "mcp "]:
        if q.startswith(prefix) and len(q) > len(prefix):
            q = q[len(prefix) :].strip()
    return q


def score_server(server: dict, query: str) -> int:
    q = normalize_query(query)
    score = 0

    if q == server["id"]:
        score = max(score, 100)
    if q in server["displayName"].lower():
        score = max(score, 80)
    if q in server.get("tags", []):
        score = max(score, 60)
    else:
        for tag in server.get("tags", []):
            if tag.startswith(q):
                score = max(score, 50)
                break
    if q in server["description"].lower():
        score = max(score, 40)

    return score


def search_curated(
    servers: list[dict], query: str, category: str | None = None
) -> list[dict]:
    results = []
    for server in servers:
        if category and category not in server.get("categories", []):
            continue
        s = score_server(server, query)
        if s > 0:
            results.append((s, server.get("popularity", 0), server))

    results.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [r[2] for r in results]


def check_clawhub(bundles: dict, query: str) -> dict | None:
    q = normalize_query(query)
    if q in bundles:
        return bundles[q]
    return None


def search_clawhub_api(query: str) -> dict | None:
    """Search ClawHub API for a matching bundle. Falls back to None on failure."""
    q = normalize_query(query)
    url = f"https://clawhub.openclaw.dev/api/search?q={quote_plus(q)}&type=mcp-bundle"
    try:
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        bundles = data.get("results", [])
        if bundles:
            b = bundles[0]
            return {
                "bundleId": b.get("id", ""),
                "displayName": b.get("displayName", ""),
                "description": b.get("description", ""),
                "skillCount": b.get("skillCount", 0),
            }
        return None
    except Exception:
        return None


def search_smithery(query: str, limit: int = 10) -> list[dict]:
    """Search Smithery.ai registry for MCP servers. No auth required."""
    q = normalize_query(query)
    url = f"https://registry.smithery.ai/servers?q={quote_plus(q)}&pageSize={limit}"
    try:
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        return [format_smithery_result(s) for s in data.get("servers", [])[:limit]]
    except Exception:
        return []


def format_smithery_result(server: dict) -> dict:
    """Convert a Smithery API result to the standard result format."""
    qualified = server.get("qualifiedName", server.get("name", ""))
    display = server.get("displayName", server.get("name", qualified))
    return {
        "id": qualified,
        "displayName": display,
        "description": server.get("description", ""),
        "transport": server.get("transport", "stdio"),
        "installMethod": _infer_install_method(server),
        "package": qualified,
        "requiredEnv": [],
        "verified": False,
        "source": "smithery",
    }


def _infer_install_method(server: dict) -> str:
    """Infer install method from Smithery server metadata."""
    name = server.get("qualifiedName", "")
    if name.startswith("@") or "/" in name:
        return "npx"
    repo = server.get("repository", "")
    if "pypi" in repo or server.get("runtime") == "python":
        return "uvx"
    return "npx"


def search_npm(query: str, limit: int = 10) -> list[dict]:
    """Search npm registry for MCP server packages. Fallback when curated list has no match."""
    q = normalize_query(query)
    strategies = [
        f"@modelcontextprotocol/{q}",
        f"mcp-server-{q}",
        f"{q} mcp server",
    ]
    seen: set[str] = set()
    results: list[dict] = []

    for text in strategies:
        if len(results) >= limit:
            break
        url = f"https://registry.npmjs.org/-/v1/search?text={quote_plus(text)}&size={limit}"
        try:
            req = Request(url, headers={"Accept": "application/json"})
            with urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
            for obj in data.get("objects", []):
                pkg_name = obj.get("package", {}).get("name", "")
                if pkg_name and pkg_name not in seen:
                    seen.add(pkg_name)
                    results.append(format_npm_result(obj))
        except Exception:
            continue

        if results:
            break

    return results[:limit]


def format_npm_result(npm_package: dict) -> dict:
    """Convert an npm registry search result to the standard result format."""
    pkg = npm_package["package"]
    name = pkg["name"]
    server_id = name.split("/")[-1]
    for prefix in ("server-", "mcp-server-", "mcp-"):
        if server_id.startswith(prefix):
            server_id = server_id[len(prefix):]
            break
    return {
        "id": server_id,
        "displayName": name,
        "description": pkg.get("description", ""),
        "transport": "stdio",
        "installMethod": "npx",
        "package": name,
        "requiredEnv": [],
        "verified": False,
        "source": "npm",
    }


def format_result(server: dict) -> dict:
    return {
        "id": server["id"],
        "displayName": server["displayName"],
        "description": server["description"],
        "transport": server["transport"],
        "installMethod": server["installMethod"],
        "package": server["package"],
        "requiredEnv": server["requiredEnv"],
        "verified": server["verified"],
        "source": "curated",
    }


def enrich_with_live_stats(results: list[dict]) -> list[dict]:
    """Add live download/popularity stats from npm registry."""
    from urllib.request import urlopen
    from urllib.error import URLError

    for result in results:
        package = result.get("package", "")
        install_method = result.get("installMethod", "")

        if install_method in ("npx", "npm") and package:
            try:
                # Get weekly downloads
                url = f"https://api.npmjs.org/downloads/point/last-week/{package}"
                with urlopen(url, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    downloads = data.get("downloads", 0)

                # Get publish date
                pkg_url = f"https://registry.npmjs.org/{package}/latest"
                with urlopen(pkg_url, timeout=5) as response:
                    pkg_data = json.loads(response.read().decode())
                    version = pkg_data.get("version", "unknown")

                result["liveStats"] = {
                    "weeklyDownloads": downloads,
                    "latestVersion": version,
                }
            except (URLError, json.JSONDecodeError, OSError, KeyError):
                result["liveStats"] = None
        else:
            result["liveStats"] = None

    return results


def main():
    parser = argparse.ArgumentParser(description="Search MCP server registries")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--category", default=None, help="Filter by category")
    parser.add_argument("--limit", type=int, default=10, help="Max results")
    parser.add_argument("--enrich", action="store_true", help="Enrich results with live popularity data (slower)")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    servers = load_known_servers(str(base_dir))
    bundles = load_clawhub_bundles(str(base_dir))

    if not servers:
        json.dump(
            {"error": "Catalog file not found or empty", "path": str(base_dir / "assets" / "known_servers.json")},
            sys.stdout,
            indent=2,
        )
        sys.exit(1)

    # ClawHub: try live API first, fall back to hardcoded lookup
    clawhub_match = search_clawhub_api(args.query)
    if clawhub_match is None:
        clawhub_match = check_clawhub(bundles, args.query)

    curated_results = search_curated(servers, args.query, args.category)[: args.limit]

    # Tiered fallback: curated -> npm -> smithery
    npm_results: list[dict] = []
    smithery_results: list[dict] = []
    if not curated_results:
        npm_results = search_npm(args.query, args.limit)
    if not curated_results and not npm_results:
        smithery_results = search_smithery(args.query, args.limit)

    all_results = (
        [format_result(r) for r in curated_results]
        + npm_results
        + smithery_results
    )
    sources_used = ["curated"]
    if npm_results:
        sources_used.append("npm")
    if smithery_results:
        sources_used.append("smithery")

    output = {
        "query": args.query,
        "resultsCount": len(all_results),
        "clawHubMatch": clawhub_match,
        "sources": sources_used,
        "results": all_results[: args.limit],
    }
    if args.enrich:
        all_results = output.get("results", [])
        output["results"] = enrich_with_live_stats(all_results)
        output["enriched"] = True
    else:
        output["enriched"] = False
    json.dump(output, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
