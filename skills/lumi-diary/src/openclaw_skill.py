"""
Lumi Diary v0.2.0 — OpenClaw Adapter Layer

Wraps ``lumi_core`` functions for the OpenClaw platform, handling
platform-specific concerns like file_id resolution and sandbox paths.

This module is the entry point referenced by SKILL.md ``tools:`` section.
"""

from __future__ import annotations

from typing import Any

from src import lumi_core


# ---------------------------------------------------------------------------
# OpenClaw-specific sender resolution
# ---------------------------------------------------------------------------

def _resolve_sender_openclaw(sender_name: str, sender_id: str | None = None) -> str:
    """Resolve display name using the Portraits registry.

    In OpenClaw, sender_id comes from the IM platform binding.
    """
    return lumi_core.resolve_display_name(sender_name, sender_id)


# ===========================================================================
# Tool wrappers — called by SKILL.md tool declarations
# ===========================================================================

def record_group_fragment(
    sender_name: str,
    content: str,
    story_node_id: str,
    interaction_type: str,
    *,
    context_type: str = "solo",
    media_path: str | None = None,
    event_name: str | None = None,
    emotion_tag: str | None = None,
    group_id: str | None = None,
    sender_id: str | None = None,
) -> dict[str, Any]:
    """OpenClaw wrapper for record_fragment.

    Resolves sender identity from the platform and delegates to core.
    """
    def _resolver(name: str) -> str:
        return _resolve_sender_openclaw(name, sender_id)

    return lumi_core.record_fragment(
        sender_name, content, story_node_id, interaction_type,
        context_type=context_type,
        media_path=media_path,
        event_name=event_name,
        emotion_tag=emotion_tag,
        group_id=group_id,
        resolve_sender=_resolver,
    )


def manage_identity(
    action: str,
    *,
    display_name: str | None = None,
    account_id: str | None = None,
    original_name: str | None = None,
) -> dict[str, Any]:
    return lumi_core.manage_identity(
        action, display_name=display_name,
        account_id=account_id, original_name=original_name,
    )


def manage_event(
    action: str,
    event_name: str,
    *,
    group_id: str | None = None,
) -> dict[str, Any]:
    return lumi_core.manage_event(action, event_name, group_id=group_id)


def update_portrait(
    entity_name: str,
    *,
    new_impression: str | None = None,
    date: str | None = None,
    is_milestone: bool = False,
    milestone_label: str | None = None,
    traits: list[str] | None = None,
) -> dict[str, Any]:
    return lumi_core.update_portrait(
        entity_name,
        new_impression=new_impression,
        date=date,
        is_milestone=is_milestone,
        milestone_label=milestone_label,
        traits=traits,
    )


def save_keepsake(
    title: str,
    context_tags: list[str],
    *,
    media_path: str | None = None,
) -> dict[str, Any]:
    return lumi_core.save_keepsake(title, context_tags, media_path=media_path)


def render_lumi_canvas(
    target_event: str,
    *,
    context_type: str = "event",
    vibe_override: str | None = None,
    group_id: str | None = None,
    locale: str = "en",
) -> dict[str, Any]:
    return lumi_core.render_lumi_canvas(
        target_event, context_type=context_type,
        vibe_override=vibe_override, group_id=group_id, locale=locale,
    )


def manage_fragment(
    action: str,
    *,
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
) -> dict[str, Any]:
    return lumi_core.manage_fragment(
        action, fragment_id=fragment_id, keyword=keyword,
        sender=sender, context_type=context_type, group_id=group_id,
        event_name=event_name, story_node_id=story_node_id,
        date_from=date_from, date_to=date_to, limit=limit,
        new_content=new_content, new_emotion=new_emotion,
    )


def export_capsule(
    target_event: str,
    *,
    context_type: str = "event",
    vibe_override: str | None = None,
    group_id: str | None = None,
    locale: str = "en",
) -> dict[str, Any]:
    return lumi_core.export_capsule(
        target_event, context_type=context_type,
        vibe_override=vibe_override, group_id=group_id, locale=locale,
    )


def import_capsule(file_path: str) -> dict[str, Any]:
    return lumi_core.import_capsule(file_path)


def check_time_echoes() -> dict[str, Any]:
    return lumi_core.check_time_echoes()
