#!/usr/bin/env python3
"""Recommend complementary MCP servers based on what's already installed."""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from pathlib import Path


def load_affinities(base_dir: str) -> dict:
    path = Path(base_dir) / "assets" / "server_affinities.json"
    try:
        with open(path) as f:
            return json.load(f)["affinities"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return {}


def load_known_servers(base_dir: str) -> dict:
    path = Path(base_dir) / "assets" / "known_servers.json"
    try:
        with open(path) as f:
            data = json.load(f)
        return {s["id"]: s for s in data["servers"]}
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return {}


def load_installed_state() -> set:
    state_file = Path.home() / ".openclaw" / "mcp-marketplace" / "installed_servers.json"
    if not state_file.exists():
        return set()
    try:
        with open(state_file) as f:
            return set(json.load(f).get("servers", {}).keys())
    except (json.JSONDecodeError, KeyError):
        return set()


def _find_configured_servers() -> set:
    configured = set()
    paths = [
        Path.cwd() / ".mcp.json",
        Path.cwd() / ".cursor" / "mcp.json",
    ]
    if platform.system() == "Darwin":
        paths.append(Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json")
    elif platform.system() == "Windows":
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            paths.append(Path(appdata) / "Claude" / "claude_desktop_config.json")
    else:
        paths.append(Path.home() / ".config" / "claude" / "claude_desktop_config.json")

    for p in paths:
        if p.exists():
            try:
                with open(p) as f:
                    config = json.load(f)
                configured.update(config.get("mcpServers", {}).keys())
            except (json.JSONDecodeError, OSError):
                continue
    return configured


def compute_recommendations(
    installed: set, affinities: dict, known: dict, max_results: int = 5
) -> list[dict]:
    """Score candidate servers by affinity to installed servers."""
    candidates: dict[str, dict] = {}

    for installed_id in installed:
        server_affinities = affinities.get(installed_id, {})
        for candidate_id, score in server_affinities.items():
            if candidate_id in installed:
                continue  # Already installed
            if candidate_id not in known:
                continue  # Not in catalog

            if candidate_id not in candidates:
                candidates[candidate_id] = {
                    "serverId": candidate_id,
                    "totalScore": 0.0,
                    "reasons": [],
                }

            candidates[candidate_id]["totalScore"] += score
            candidates[candidate_id]["reasons"].append(
                f"Complements {known.get(installed_id, {}).get('displayName', installed_id)} (affinity: {score})"
            )

    # Sort by total score descending
    ranked = sorted(candidates.values(), key=lambda x: x["totalScore"], reverse=True)

    # Enrich with server details
    results = []
    for entry in ranked[:max_results]:
        server = known.get(entry["serverId"], {})
        results.append({
            "serverId": entry["serverId"],
            "displayName": server.get("displayName", entry["serverId"]),
            "description": server.get("description", ""),
            "score": round(entry["totalScore"], 2),
            "reasons": entry["reasons"],
            "installMethod": server.get("installMethod", "unknown"),
            "requiredEnv": server.get("requiredEnv", []),
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="Recommend complementary MCP servers")
    parser.add_argument("--max-results", type=int, default=5, help="Maximum recommendations to return")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    affinities = load_affinities(str(base_dir))
    known = load_known_servers(str(base_dir))

    installed = load_installed_state() | _find_configured_servers()

    if not installed:
        json.dump({
            "action": "smart-recommend",
            "recommendations": [],
            "note": "No servers installed or configured. Try 'install the standard dev toolkit' or 'recommend servers for this project' first.",
        }, sys.stdout, indent=2)
        print()
        return

    recommendations = compute_recommendations(installed, affinities, known, args.max_results)

    output = {
        "action": "smart-recommend",
        "basedOn": sorted(installed),
        "recommendationCount": len(recommendations),
        "recommendations": recommendations,
    }
    json.dump(output, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
