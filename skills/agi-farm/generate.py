#!/usr/bin/env python3
"""
generate.py — Template renderer for agi-farm skill.

Reads team.json, renders all templates in templates/ with {{VARIABLE}} substitution,
writes output files to the workspace.

Usage:
  python3 generate.py --team-json /path/to/team.json --output /path/to/workspace/ --all-agents --shared
  python3 generate.py --team-json /path/to/team.json --output /path/to/workspace/ --agent main
  python3 generate.py --team-json /path/to/team.json --output /path/to/workspace/ --bundle
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).parent
TEMPLATES_DIR = SKILL_DIR / "templates"


AGENT_WORKSPACES = {
    "main":       ".",
    "researcher": "researcher",
    "builder":    "builder",
    "qa":         "qa",
    "content":    "content",
    "sage":       "solution-architect",
    "forge":      "implementation-engineer",
    "pixel":      "debugger",
    "vista":      "business-analyst",
    "cipher":     "knowledge-curator",
    "vigil":      "quality-assurance",
    "anchor":     "content-specialist",
    "lens":       "multimodal-specialist",
    "evolve":     "process-improvement",
    "nova":       "r-and-d",
}


def load_team(team_json_path: str) -> dict:
    return json.loads(Path(team_json_path).read_text())


def render(template_text: str, vars: dict) -> str:
    """Replace {{KEY}} with vars[KEY] in template_text."""
    result = template_text
    for key, value in vars.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


def make_vars(team: dict, agent: dict = None, workspace_root: Path = None) -> dict:
    """Build substitution variables for a given team + optional agent."""
    frameworks = team.get("frameworks", [])
    framework_str = ", ".join(frameworks) if frameworks else "none"

    agents_table = "\n".join(
        f"| {a['id']} | {a['name']} | {a['emoji']} | {a.get('model', '')} | {a['role']} |"
        for a in team.get("agents", [])
    )

    agents_dashboard_table = "\n".join(
        f"| {a['name']} {a['emoji']} | available | — | — |"
        for a in team.get("agents", [])
    )

    workspace_str = str(workspace_root) if workspace_root else str(Path.home() / ".openclaw" / "workspace")

    vars = {
        "TEAM_NAME":              team.get("team_name", "MyTeam"),
        "TEAM_NAME_LOWER":        team.get("team_name", "myteam").lower().replace(" ", "-"),
        "ORCHESTRATOR_NAME":      team.get("orchestrator_name", "Cooper"),
        "FRAMEWORKS":             framework_str,
        "AGENTS_TABLE":           agents_table,
        "AGENTS_DASHBOARD_TABLE": agents_dashboard_table,
        "DATE":                   datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "PRESET":                 str(team.get("preset", "9")),
        "WORKSPACE":              workspace_str,
    }

    if agent:
        vars.update({
            "AGENT_ID":    agent.get("id", ""),
            "AGENT_NAME":  agent.get("name", ""),
            "AGENT_EMOJI": agent.get("emoji", ""),
            "AGENT_ROLE":  agent.get("role", ""),
            "AGENT_GOAL":  agent.get("goal", ""),
            "AGENT_MODEL": agent.get("model", ""),
        })

    return vars


def render_template(template_name: str, vars: dict) -> str:
    """Load and render a template file."""
    path = TEMPLATES_DIR / template_name
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return render(path.read_text(encoding="utf-8"), vars)


def write_agent_files(team: dict, agent: dict, workspace_root: Path, no_overwrite: bool = False):
    """Write all 7 workspace files for one agent."""
    agent_id = agent["id"]
    subdir = AGENT_WORKSPACES.get(agent_id, agent_id)

    if subdir == ".":
        agent_dir = workspace_root
    else:
        agent_dir = workspace_root / "agents-workspaces" / subdir

    agent_dir.mkdir(parents=True, exist_ok=True)

    vars = make_vars(team, agent, workspace_root)

    # Pick SOUL.md template: agent-specific if it exists, else generic
    soul_template = f"SOUL.md.{agent_id}" if (TEMPLATES_DIR / f"SOUL.md.{agent_id}").exists() else "SOUL.md.generic"

    files = {
        "SOUL.md":      render_template(soul_template, vars),
        "IDENTITY.md":  render_template("IDENTITY.md.template", vars),
        "AGENTS.md":    render_template("AGENTS.md.template", vars),
        "USER.md":      render_template("USER.md.template", vars),
        "HEARTBEAT.md": render_template("HEARTBEAT.md.template", vars),
        "BOOTSTRAP.md": render_template("BOOTSTRAP.md.template", vars),
        "TOOLS.md":     render_template("TOOLS.md.template", vars),
    }

    for filename, content in files.items():
        dest = agent_dir / filename
        if no_overwrite and dest.exists():
            print(f"  skipped (exists) {dest}")
            continue
        dest.write_text(content, encoding="utf-8")
        print(f"  wrote {dest}")


def write_shared_files(team: dict, workspace_root: Path, no_overwrite: bool = False):
    """Write team-wide files: CLAUDE.md, MEMORY.md, comms infrastructure."""
    vars = make_vars(team, workspace_root=workspace_root)

    shared = {
        "CLAUDE.md": render_template("CLAUDE.md.template", vars),
        "MEMORY.md": render_template("MEMORY.md.template", vars),
    }
    for filename, content in shared.items():
        dest = workspace_root / filename
        if no_overwrite and dest.exists():
            print(f"  skipped (exists) {dest}")
            continue
        dest.write_text(content, encoding="utf-8")
        print(f"  wrote {dest}")

    # Comms infrastructure
    for agent in team["agents"]:
        aid = agent["id"]
        (workspace_root / "comms" / "inboxes").mkdir(parents=True, exist_ok=True)
        (workspace_root / "comms" / "outboxes").mkdir(parents=True, exist_ok=True)
        for subdir, fname, body in [
            ("inboxes",  f"{aid}.md", f"# {agent['name']} Inbox\n\n_No messages._\n"),
            ("outboxes", f"{aid}.md", f"# {agent['name']} Outbox\n\n_No messages._\n"),
        ]:
            dest = workspace_root / "comms" / subdir / fname
            if no_overwrite and dest.exists():
                continue
            dest.write_text(body, encoding="utf-8")
    bc = workspace_root / "comms" / "broadcast.md"
    if not (no_overwrite and bc.exists()):
        bc.write_text(f"# {team['team_name']} Broadcast\n\n_No broadcasts._\n", encoding="utf-8")
    print(f"  wrote comms/ infrastructure ({len(team['agents'])} agents)")


def write_bundle(team: dict, workspace_root: Path):
    """Write the portable bundle to workspace/agi-farm-bundle/."""
    bundle_dir = workspace_root / "agi-farm-bundle"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    vars = make_vars(team, workspace_root=workspace_root)

    # team.json
    (bundle_dir / "team.json").write_text(
        json.dumps(team, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # install.sh
    install_sh = render_template("install.sh.template", vars)
    install_path = bundle_dir / "install.sh"
    install_path.write_text(install_sh, encoding="utf-8")
    install_path.chmod(0o755)

    # README.md
    readme = render_template("README.md.bundle.template", vars)
    (bundle_dir / "README.md").write_text(readme, encoding="utf-8")

    print(f"  wrote bundle to {bundle_dir}")


def write_infrastructure_files(team: dict, workspace_root: Path):
    """Write team-wide infrastructure files: PROCESSES.json, TASKS.json, standards/, etc.

    Skips any file that already exists (never overwrites).
    """
    vars = make_vars(team, workspace_root=workspace_root)

    # Flat files at workspace root
    flat_files = [
        ("PROCESSES.json",           "PROCESSES.json.template"),
        ("SHARED_KNOWLEDGE.json",    "SHARED_KNOWLEDGE.json.template"),
        ("FAILURES.md",              "FAILURES.md.template"),
        ("DECISIONS.md",             "DECISIONS.md.template"),
        ("DASHBOARD.md",             "DASHBOARD.md.template"),
        ("IMPROVEMENT_BACKLOG.json", "IMPROVEMENT_BACKLOG.json.template"),
        ("EXPERIMENTS.json",         "EXPERIMENTS.json.template"),
        ("TASKS.json",               "TASKS.json.template"),
    ]

    for filename, template_name in flat_files:
        dest = workspace_root / filename
        if dest.exists():
            print(f"  skipped (exists) {dest}")
            continue
        content = render_template(template_name, vars)
        dest.write_text(content, encoding="utf-8")
        print(f"  wrote {dest}")

    # Standards files in standards/
    standards_dir = workspace_root / "standards"
    standards_dir.mkdir(parents=True, exist_ok=True)

    standards_files = [
        ("coding.md",        "standards/coding.md.template"),
        ("research.md",      "standards/research.md.template"),
        ("quality.md",       "standards/quality.md.template"),
        ("documentation.md", "standards/documentation.md.template"),
    ]

    for filename, template_name in standards_files:
        dest = standards_dir / filename
        if dest.exists():
            print(f"  skipped (exists) {dest}")
            continue
        content = render_template(template_name, vars)
        dest.write_text(content, encoding="utf-8")
        print(f"  wrote {dest}")


def parse_args():
    p = argparse.ArgumentParser(description="agi-farm template renderer")
    p.add_argument("--team-json", required=True, dest="team_json")
    p.add_argument("--output", required=True)
    p.add_argument("--agent", help="Render files for one agent ID")
    p.add_argument("--all-agents", action="store_true", dest="all_agents",
                   help="Render files for all agents in team.json")
    p.add_argument("--shared", action="store_true",
                   help="Write shared team files (CLAUDE.md, MEMORY.md, comms/)")
    p.add_argument("--bundle", action="store_true",
                   help="Write portable bundle (install.sh, README.md, team.json copy)")
    p.add_argument("--infrastructure", action="store_true",
                   help="Write team infrastructure files (PROCESSES.json, TASKS.json, DASHBOARD.md, standards/, etc.)")
    p.add_argument("--no-overwrite", action="store_true", dest="no_overwrite",
                   help="Skip files that already exist (safe re-render preserving manual edits)")
    return p.parse_args()


def main():
    args = parse_args()
    team = load_team(args.team_json)
    workspace_root = Path(args.output).expanduser().resolve()


    workspace_root.mkdir(parents=True, exist_ok=True)

    agent_map = {a["id"]: a for a in team.get("agents", [])}

    no_overwrite = args.no_overwrite

    if args.agent:
        agent = agent_map.get(args.agent)
        if not agent:
            print(f"Error: agent '{args.agent}' not in team.json", file=sys.stderr)
            sys.exit(1)
        print(f"Rendering files for agent: {args.agent}")
        write_agent_files(team, agent, workspace_root, no_overwrite)

    if args.all_agents:
        for agent in team["agents"]:
            print(f"Rendering files for agent: {agent['id']}")
            write_agent_files(team, agent, workspace_root, no_overwrite)

    if args.shared:
        print("Rendering shared team files...")
        write_shared_files(team, workspace_root, no_overwrite)
        print("Rendering infrastructure files (--shared implies --infrastructure)...")
        write_infrastructure_files(team, workspace_root)

    if args.infrastructure and not args.shared:
        print("Rendering infrastructure files...")
        write_infrastructure_files(team, workspace_root)

    if args.bundle:
        print("Writing portable bundle...")
        write_bundle(team, workspace_root)

    print("Done.")


if __name__ == "__main__":
    main()
