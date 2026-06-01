"""
Lumi Diary v0.2.0 — MCP Server Adapter

Wraps ``lumi_core`` functions as MCP tools for any MCP-compatible client
(Claude Desktop, Cursor, VS Code Copilot, etc.).

Run with:
    fastmcp run src/mcp_server.py
    # or
    python -m src.mcp_server
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from src import lumi_core

PERSONA_PATH = Path(__file__).resolve().parent.parent / "SKILL.md"

mcp = FastMCP(
    "Lumi Diary",
    instructions=(
        "You are Lumi, a local-first memory guardian and cyber bestie. "
        "Use the provided tools to record life fragments, manage events, "
        "render interactive memory scrolls, and more. All data stays in "
        "the user's local Lumi_Vault/ directory."
    ),
)


def _json_result(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Prompt: full Lumi persona
# ---------------------------------------------------------------------------

@mcp.prompt()
def lumi_persona() -> str:
    """Full Lumi persona and behavioral protocol. Attach this to activate Lumi's personality."""
    if PERSONA_PATH.exists():
        raw = PERSONA_PATH.read_text(encoding="utf-8")
        parts = raw.split("system_prompt: |", 1)
        if len(parts) > 1:
            prompt_section = parts[1].split("\ntools:", 1)[0]
            lines = prompt_section.split("\n")
            return "\n".join(line[2:] if line.startswith("  ") else line for line in lines)
    return "You are Lumi, a local-first memory guardian."


# ---------------------------------------------------------------------------
# Tools — all delegate to lumi_core
# ---------------------------------------------------------------------------

@mcp.tool()
def tool_record_fragment(
    sender_name: str,
    content: str,
    story_node_id: str,
    interaction_type: str,
    context_type: str = "solo",
    media_path: str | None = None,
    event_name: str | None = None,
    emotion_tag: str | None = None,
    group_id: str | None = None,
    sender_id: str | None = None,
) -> str:
    """Record a life fragment into the local vault.

    Routes to Solo/Circles/Events based on context_type.
    Supports media attachments, emotion tags, and annotation stitching.
    """
    def _resolver(name: str) -> str:
        return lumi_core.resolve_display_name(name, sender_id)

    return _json_result(lumi_core.record_fragment(
        sender_name, content, story_node_id, interaction_type,
        context_type=context_type, media_path=media_path,
        event_name=event_name, emotion_tag=emotion_tag,
        group_id=group_id, resolve_sender=_resolver,
    ))


@mcp.tool()
def tool_manage_identity(
    action: str,
    display_name: str | None = None,
    account_id: str | None = None,
    original_name: str | None = None,
) -> str:
    """Manage owner profile and contacts in the Portraits registry.

    Actions: init_owner, get_owner, rename, lookup, list_contacts.
    """
    return _json_result(lumi_core.manage_identity(
        action, display_name=display_name,
        account_id=account_id, original_name=original_name,
    ))


@mcp.tool()
def tool_manage_event(
    action: str,
    event_name: str,
    group_id: str | None = None,
) -> str:
    """Start, stop, or query an event scroll.

    Actions: start, stop, query.
    """
    return _json_result(lumi_core.manage_event(
        action, event_name, group_id=group_id,
    ))


@mcp.tool()
def tool_update_portrait(
    entity_name: str,
    new_impression: str | None = None,
    date: str | None = None,
    is_milestone: bool = False,
    milestone_label: str | None = None,
    traits: list[str] | None = None,
) -> str:
    """Update a portrait entry with impressions, milestones, or traits.

    Called when Lumi notices new personality traits or important dates.
    """
    return _json_result(lumi_core.update_portrait(
        entity_name, new_impression=new_impression,
        date=date, is_milestone=is_milestone,
        milestone_label=milestone_label, traits=traits,
    ))


@mcp.tool()
def tool_save_keepsake(
    title: str,
    context_tags: list[str],
    media_path: str | None = None,
) -> str:
    """Archive a legendary moment into Keepsakes for future callbacks.

    Media files are deduplicated via content-addressed MD5 hashing.
    """
    return _json_result(lumi_core.save_keepsake(
        title, context_tags, media_path=media_path,
    ))


@mcp.tool()
def tool_render_canvas(
    target_event: str,
    context_type: str = "event",
    vibe_override: str | None = None,
    group_id: str | None = None,
    locale: str = "en",
) -> str:
    """Render an interactive HTML memory scroll.

    Use target_event="today" or "this_month" for daily/monthly views.
    Locale: "en" (default) or "zh" for Chinese UI.
    """
    return _json_result(lumi_core.render_lumi_canvas(
        target_event, context_type=context_type,
        vibe_override=vibe_override, group_id=group_id, locale=locale,
    ))


@mcp.tool()
def tool_manage_fragment(
    action: str,
    fragment_id: str | None = None,
    keyword: str | None = None,
    sender: str | None = None,
    context_type: str | None = None,
    group_id: str | None = None,
    event_name: str | None = None,
    story_node_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 20,
    new_content: str | None = None,
    new_emotion: str | None = None,
) -> str:
    """Search, view, update, or delete recorded fragments.

    Actions: search, get, update, delete.
    """
    return _json_result(lumi_core.manage_fragment(
        action, fragment_id=fragment_id, keyword=keyword,
        sender=sender, context_type=context_type, group_id=group_id,
        event_name=event_name, story_node_id=story_node_id,
        date_from=date_from, date_to=date_to, limit=limit,
        new_content=new_content, new_emotion=new_emotion,
    ))


@mcp.tool()
def tool_export_capsule(
    target_event: str,
    context_type: str = "event",
    vibe_override: str | None = None,
    group_id: str | None = None,
    locale: str = "en",
) -> str:
    """Export a memory capsule (.lumi ZIP) for social sharing.

    Produces HTML scroll + .lumi capsule + optional PNG screenshot.
    """
    return _json_result(lumi_core.export_capsule(
        target_event, context_type=context_type,
        vibe_override=vibe_override, group_id=group_id, locale=locale,
    ))


@mcp.tool()
def tool_import_capsule(file_path: str) -> str:
    """Import a .lumi capsule and merge its memories into the local vault.

    Existing fragments are preserved; only new annotations are added.
    """
    return _json_result(lumi_core.import_capsule(file_path))


@mcp.tool()
def tool_check_time_echoes() -> str:
    """Check for milestone dates that match today (birthday, anniversary, etc.).

    Returns triggered echoes for Lumi to weave into conversation.
    """
    return _json_result(lumi_core.check_time_echoes())


if __name__ == "__main__":
    mcp.run()
