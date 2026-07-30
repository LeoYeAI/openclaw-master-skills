#!/usr/bin/env python3
"""Recommend MCP servers based on project type detection."""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from pathlib import Path


def load_templates(base_dir: str) -> dict:
    path = Path(base_dir) / "assets" / "project_templates.json"
    try:
        with open(path) as f:
            return json.load(f)["templates"]
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


def scan_project(project_dir: str, templates: dict) -> list[dict]:
    """Score each template against the project directory."""
    project_path = Path(project_dir)
    scores = []

    for name, template in templates.items():
        score = 0
        matched_files = []
        matched_patterns = []

        # Check detection files
        for f in template.get("detectionFiles", []):
            target = project_path / f
            if target.exists() or target.is_dir():
                score += 2
                matched_files.append(f)

        # Check detection patterns in common files
        content_files = ["package.json", "requirements.txt", "pyproject.toml", "Pipfile", "Gemfile"]
        combined_content = ""
        for cf in content_files:
            cf_path = project_path / cf
            if cf_path.exists():
                try:
                    combined_content += cf_path.read_text(errors="ignore").lower()
                except OSError:
                    continue

        for pattern in template.get("detectionPatterns", []):
            if pattern.lower() in combined_content:
                score += 1
                matched_patterns.append(pattern)

        if score > 0:
            scores.append({
                "templateName": name,
                "displayName": template["displayName"],
                "description": template["description"],
                "score": score,
                "matchedFiles": matched_files,
                "matchedPatterns": matched_patterns,
                "recommendedServers": template["recommendedServers"],
                "optionalServers": template["optionalServers"],
            })

    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores


def main():
    parser = argparse.ArgumentParser(description="Recommend MCP servers based on project type")
    parser.add_argument("--project-dir", default=str(Path.cwd()), help="Project directory to scan (default: cwd)")
    parser.add_argument("--template", default=None, help="Force a specific template instead of auto-detecting")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    templates = load_templates(str(base_dir))
    known = load_known_servers(str(base_dir))
    configured = _find_configured_servers()

    if args.template:
        if args.template not in templates:
            json.dump({"error": f"Template '{args.template}' not found. Available: {', '.join(templates.keys())}"}, sys.stdout, indent=2)
            print()
            sys.exit(1)
        t = templates[args.template]
        matches = [{
            "templateName": args.template,
            "displayName": t["displayName"],
            "description": t["description"],
            "score": 100,
            "matchedFiles": [],
            "matchedPatterns": [],
            "recommendedServers": t["recommendedServers"],
            "optionalServers": t["optionalServers"],
        }]
    else:
        matches = scan_project(args.project_dir, templates)

    if not matches:
        json.dump({
            "action": "recommend",
            "detected": False,
            "note": "Could not detect project type. Available templates: " + ", ".join(templates.keys()),
        }, sys.stdout, indent=2)
        print()
        return

    best = matches[0]
    all_servers = best["recommendedServers"] + best["optionalServers"]

    recommendations = []
    for sid in all_servers:
        server = known.get(sid)
        entry = {
            "serverId": sid,
            "displayName": server["displayName"] if server else sid,
            "category": "recommended" if sid in best["recommendedServers"] else "optional",
            "alreadyConfigured": sid in configured,
        }
        if server:
            entry["requiredEnv"] = server.get("requiredEnv", [])
            entry["installMethod"] = server.get("installMethod", "unknown")
        recommendations.append(entry)

    new_recommendations = [r for r in recommendations if not r["alreadyConfigured"]]
    already_configured = [r for r in recommendations if r["alreadyConfigured"]]

    output = {
        "action": "recommend",
        "detected": True,
        "projectDir": args.project_dir,
        "template": {
            "name": best["templateName"],
            "displayName": best["displayName"],
            "description": best["description"],
            "confidence": "high" if best["score"] >= 4 else "medium" if best["score"] >= 2 else "low",
        },
        "matchedFiles": best["matchedFiles"],
        "matchedPatterns": best["matchedPatterns"],
        "recommendations": new_recommendations,
        "alreadyConfigured": already_configured,
        "alternativeTemplates": [{"name": m["templateName"], "displayName": m["displayName"], "score": m["score"]} for m in matches[1:3]],
    }
    json.dump(output, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
