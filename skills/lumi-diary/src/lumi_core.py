"""
Lumi Diary v0.2.0 — Core Engine (lumi_core.py)

Platform-agnostic business logic for the Lumi memory guardian.
All I/O is sandboxed to the vault directory resolved from the
``LUMI_VAULT_PATH`` environment variable (default: ``./Lumi_Vault``).

Data-flow philosophy:
  Fragment (主记录) ➡️ Annotation (同伴批注) ➡️ Canvas (交互画卷)

Storage layout:
  Solo/Daily/        — personal monthly journals
  Solo/Projects/     — serious personal material
  Circles/           — long-term group archives (monthly rotation)
  Events/            — temporary event groups (start → stop lifecycle)
  Assets/<xx>/       — media (Git-style 2-char hash sharding)
  Brain/             — Portraits, Keepsakes, indices, exports
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import threading
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

_LUMI_VERSION = "0.2.0"

# ---------------------------------------------------------------------------
# Vault root — configurable via environment variable
# ---------------------------------------------------------------------------

def _resolve_vault_root() -> Path:
    env = os.environ.get("LUMI_VAULT_PATH")
    return Path(env) if env else Path("Lumi_Vault")

VAULT_ROOT = _resolve_vault_root()

VAULT_DIRS = (
    "Solo/Daily", "Solo/Projects", "Circles", "Events",
    "Assets", "Brain", "Brain/exports",
)
CONTEXT_TYPES = ("solo", "circle", "event")

# ---------------------------------------------------------------------------
# Media extension registries
# ---------------------------------------------------------------------------

IMAGE_EXTS = frozenset({".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".heic"})
VIDEO_EXTS = frozenset({".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".3gp", ".flv"})
AUDIO_EXTS = frozenset({".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac", ".opus"})
MEDIA_EXTS = IMAGE_EXTS | VIDEO_EXTS | AUDIO_EXTS

# ---------------------------------------------------------------------------
# Threading
# ---------------------------------------------------------------------------

_file_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Path safety
# ---------------------------------------------------------------------------

_SAFE_FILENAME_RE = re.compile(r"[^\w\- ]")


def sanitize_path_component(name: str) -> str:
    """Strip traversal sequences and special chars from a single path component.

    Raises ``ValueError`` if the sanitized result is empty.
    """
    cleaned = name.replace("..", "").replace("/", "_").replace("\\", "_").replace("\x00", "")
    cleaned = _SAFE_FILENAME_RE.sub("_", cleaned).strip("_. ")
    if not cleaned:
        raise ValueError(f"Path component is empty after sanitization: {name!r}")
    return cleaned


def validate_within_vault(path: Path) -> Path:
    """Assert that *path* resolves inside ``VAULT_ROOT``."""
    vault_resolved = VAULT_ROOT.resolve()
    target_resolved = path.resolve()
    if not str(target_resolved).startswith(str(vault_resolved) + "/") and target_resolved != vault_resolved:
        raise ValueError(f"Path escapes vault boundary: {path}")
    return path


_SENSITIVE_PREFIXES = (
    "/etc", "/var", "/sys", "/proc", "/dev",
    "/private/etc", "/private/var",
    "/Library", "/System",
    "C:\\Windows", "C:\\Program Files",
)


def validate_media_source(src: Path) -> None:
    """Reject non-media files and files from sensitive system directories."""
    ext = src.suffix.lower()
    if ext not in MEDIA_EXTS:
        raise ValueError(f"Rejected non-media file: {src.name} (extension '{ext}')")
    resolved = str(src.resolve())
    for prefix in _SENSITIVE_PREFIXES:
        if resolved.startswith(prefix + "/") or resolved.startswith(prefix + "\\") or resolved == prefix:
            raise ValueError(f"Rejected file from sensitive path: {resolved}")


# ---------------------------------------------------------------------------
# Vault bootstrap
# ---------------------------------------------------------------------------

def ensure_vault() -> Path:
    """Create the vault directory tree on first access and return the root."""
    for sub in VAULT_DIRS:
        (VAULT_ROOT / sub).mkdir(parents=True, exist_ok=True)
    return VAULT_ROOT


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def month_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


# ---------------------------------------------------------------------------
# i18n
# ---------------------------------------------------------------------------

SUPPORTED_LOCALES = ("en", "zh")

_I18N: dict[str, dict[str, str]] = {
    "scroll_subtitle": {
        "en": "Lumi Memory Scroll",
        "zh": "Lumi 记忆画卷",
    },
    "title_suffix": {
        "en": "Lumi Scroll",
        "zh": "Lumi 画卷",
    },
    "stat_fragments": {
        "en": "fragments",
        "zh": "条碎片",
    },
    "stat_story_nodes": {
        "en": "story nodes",
        "zh": "个故事节点",
    },
    "keepsakes_gallery_title": {
        "en": "🃏 Keepsakes Gallery",
        "zh": "🃏 典藏瞬间",
    },
    "cta_heading": {
        "en": "✨ This is a static snapshot — the real scroll is interactive!",
        "zh": "✨ 这是一张静态快照——真正的画卷是可交互的！",
    },
    "cta_body": {
        "en": (
            "Want to flip the annotation cards and see the other side of the story? "
            "Install <strong>Lumi</strong> and import the <code>.lumi</code> capsule "
            "to unlock the full interactive scroll on your own device."
        ),
        "zh": (
            "想翻转批注卡片看另一面的吐槽吗？安装 <strong>Lumi 小精灵</strong>，"
            "导入 <code>.lumi</code> 记忆胶囊，即可在你的设备上展开交互画卷！"
        ),
    },
    "cta_badge": {
        "en": "🧚 Get Lumi — Your Memory Guardian",
        "zh": "🧚 获取 Lumi —— 你的记忆守护精灵",
    },
    "footer_rendered_by": {
        "en": "Rendered by",
        "zh": "由",
    },
    "footer_rendered_suffix": {
        "en": "",
        "zh": " 渲染",
    },
    "annotation_label": {
        "en": "🎭 {n} perspectives{extra} — click to flip",
        "zh": "🎭 {n} 个视角{extra} —— 点击翻转",
    },
    "annotation_extra": {
        "en": " (+{n} more)",
        "zh": " (还有 {n} 个)",
    },
    "flip_hint": {
        "en": "👆 tap to see the other side",
        "zh": "👆 点击查看另一面",
    },
    "canvas_prefix_solo": {
        "en": "Solo",
        "zh": "独白",
    },
    "canvas_prefix_circle": {
        "en": "Circle",
        "zh": "圈子",
    },
    "canvas_prefix_today": {
        "en": "Today",
        "zh": "今天",
    },
    "no_data_found": {
        "en": "No data found for '{target}'.",
        "zh": "未找到 '{target}' 的数据。",
    },
    "no_fragments_yet": {
        "en": "'{target}' has no fragments yet.",
        "zh": "'{target}' 还没有碎片记录。",
    },
}


def t(key: str, locale: str = "en", **kwargs: Any) -> str:
    """Translated string lookup with optional format kwargs."""
    entry = _I18N.get(key, {})
    text = entry.get(locale, entry.get("en", key))
    if kwargs:
        text = text.format(**kwargs)
    return text


# ---------------------------------------------------------------------------
# JSON helpers (atomic read / write with lock)
# ---------------------------------------------------------------------------

def read_json(path: Path, *, default: Any = None) -> Any:
    """Thread-safe JSON read. Returns *default* if absent or corrupt."""
    with _file_lock:
        if not path.exists():
            return default if default is not None else {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            backup = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, backup)
            return default if default is not None else {}


def write_json(path: Path, data: Any) -> None:
    """Thread-safe atomic JSON write."""
    with _file_lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------

def append_md(path: Path, block: str) -> None:
    """Append a markdown block, creating the file with a header if needed."""
    with _file_lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            header = f"# 📅 {path.stem}\n\n"
            path.write_text(header, encoding="utf-8")
        with path.open("a", encoding="utf-8") as fh:
            fh.write(block)


def insert_md_after_pattern(path: Path, pattern: str, block: str) -> bool:
    """Insert *block* after the fragment matching *pattern*.

    Returns True on successful insertion, False if pattern not found.
    """
    with _file_lock:
        if not path.exists():
            return False
        text = path.read_text(encoding="utf-8")
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            sep = re.search(r"\n---\n", text[match.end():])
            insert_pos = match.end() + sep.end() if sep else len(text)
            text = text[:insert_pos] + block + text[insert_pos:]
            path.write_text(text, encoding="utf-8")
            return True
        with path.open("a", encoding="utf-8") as fh:
            fh.write(block)
        return False


# ---------------------------------------------------------------------------
# Media storage — Git-style 2-char hash sharding
# ---------------------------------------------------------------------------

def md5_of_file(path: Path) -> str:
    """Hex MD5 digest of a file, read in 8 KiB chunks."""
    h = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _sharded_asset_path(digest: str, suffix: str) -> Path:
    """Compute the 2-char sharded path: ``Assets/<xx>/<full_hash><ext>``."""
    shard = digest[:2]
    return VAULT_ROOT / "Assets" / shard / f"{digest}{suffix}"


def store_media(src: Path) -> tuple[Path, bool]:
    """Copy *src* into the sharded ``Assets/`` tree.

    Returns ``(dest_path, already_existed)``.
    The destination uses Git-style 2-char hash prefix sharding.
    """
    validate_media_source(src)
    digest = md5_of_file(src)
    dest = _sharded_asset_path(digest, src.suffix.lower())
    if dest.exists():
        return dest, True
    with _file_lock:
        if dest.exists():
            return dest, True
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".tmp")
        shutil.copy2(src, tmp)
        tmp.replace(dest)
    return dest, False


def migrate_legacy_assets() -> int:
    """Move flat ``Assets/<hash><ext>`` files into ``Assets/<xx>/<hash><ext>``.

    Returns the number of files migrated. Safe to call repeatedly.
    """
    assets_dir = VAULT_ROOT / "Assets"
    if not assets_dir.exists():
        return 0
    migrated = 0
    for f in assets_dir.iterdir():
        if f.is_file() and not f.name.startswith("."):
            stem = f.stem
            if len(stem) >= 2 and all(c in "0123456789abcdef" for c in stem):
                shard_dir = assets_dir / stem[:2]
                shard_dir.mkdir(exist_ok=True)
                dest = shard_dir / f.name
                if not dest.exists():
                    with _file_lock:
                        if not dest.exists():
                            shutil.move(str(f), str(dest))
                            migrated += 1
    return migrated


def media_md_tag(path_str: str) -> str:
    """Markdown embed tag for a media file based on extension."""
    ext = Path(path_str).suffix.lower()
    name = Path(path_str).name
    if ext in VIDEO_EXTS:
        return f"- **Media:** 🎬 [video: {name}]({path_str})"
    if ext in AUDIO_EXTS:
        return f"- **Media:** 🎙 [audio: {name}]({path_str})"
    return f"- **Media:** ![image]({path_str})"


# ---------------------------------------------------------------------------
# Three-context routing helpers
# ---------------------------------------------------------------------------

def event_filename(event_name: str, group_id: str | None = None) -> str:
    """Deterministic filename for event files."""
    prefix = month_tag()
    safe_name = sanitize_path_component(event_name)
    if group_id:
        safe_gid = sanitize_path_component(group_id)
        return f"{prefix}-{safe_name}_g{safe_gid}.md"
    return f"{prefix}-{safe_name}.md"


def circle_filename(group_id: str) -> str:
    """Monthly archive filename for a circle."""
    safe_name = sanitize_path_component(group_id)
    return f"{safe_name}_{month_tag()}.md"


def resolve_target(
    context_type: str,
    *,
    event_name: str | None = None,
    group_id: str | None = None,
) -> Path:
    """Central router: map context to a vault file path.

    All user-supplied names are sanitized against path traversal.
    """
    if context_type == "solo":
        if event_name:
            safe = sanitize_path_component(event_name)
            target = VAULT_ROOT / "Solo" / "Projects" / f"{safe}.md"
            return validate_within_vault(target)
        return VAULT_ROOT / "Solo" / "Daily" / f"{month_tag()}.md"

    if context_type == "circle":
        gid = group_id or "default_circle"
        target = VAULT_ROOT / "Circles" / circle_filename(gid)
        return validate_within_vault(target)

    ename = event_name or "unnamed"
    target = VAULT_ROOT / "Events" / event_filename(ename, group_id)
    return validate_within_vault(target)


# ---------------------------------------------------------------------------
# Brain file constants
# ---------------------------------------------------------------------------

PORTRAITS_FILE = "Portraits.json"
KEEPSAKES_FILE = "Keepsakes.json"
FRAGMENT_INDEX_FILE = "fragment_index.json"
EVENTS_REGISTRY_FILE = "events_registry.json"

# Legacy filenames for migration
_LEGACY_IDENTITY_FILE = "identity.json"
_LEGACY_CIRCLE_DICT_FILE = "Circle_Dictionary.json"
_LEGACY_MEME_VAULT_FILE = "Meme_Vault.json"


def _brain_path(filename: str) -> Path:
    return VAULT_ROOT / "Brain" / filename


# ---------------------------------------------------------------------------
# Fragment dedup — merge by story_node_id + sender
# ---------------------------------------------------------------------------

_FRAGMENT_HEADER_RE = re.compile(
    r"### 🧩 Fragment `(?P<fid>[^`]+)` — (?P<ts>[^\n]+)\n"
    r"- \*\*From:\*\* (?P<sender>[^\n]+)\n"
    r"- \*\*Emotion:\*\* (?P<emotion>[^\n]+)\n"
    r"- \*\*Story Node:\*\* `(?P<node>[^`]+)`",
    re.MULTILINE,
)


def try_merge_fragment(
    target: Path,
    sender_name: str,
    story_node_id: str,
    new_emotion: str,
    new_content: str,
    new_media_line: str | None,
) -> dict[str, Any] | None:
    """If *target* already has a fragment with matching node+sender, merge into it.

    Returns a result dict on merge, or ``None`` when no duplicate found.
    """
    with _file_lock:
        if not target.exists():
            return None
        text = target.read_text(encoding="utf-8")

    for m in _FRAGMENT_HEADER_RE.finditer(text):
        if m.group("node") == story_node_id and m.group("sender") == sender_name:
            old_emotion_line = f"- **Emotion:** {m.group('emotion')}"
            merged_emotion = new_emotion
            if m.group("emotion") != new_emotion:
                merged_emotion = f"{m.group('emotion')} → {new_emotion}"
            new_emotion_line = f"- **Emotion:** {merged_emotion}"

            updated = text.replace(old_emotion_line, new_emotion_line, 1)

            frag_end_match = re.search(r"\n---\n", text[m.end():])
            if frag_end_match:
                block_end = m.end() + frag_end_match.start()
            else:
                block_end = len(text)
            block_text = text[m.start():block_end]

            if new_content not in block_text:
                quote_line = f"\n> ↩ _{now_iso()}_ — {new_content}"
                sep_in_updated = re.search(r"\n---\n", updated[m.start():])
                if sep_in_updated:
                    ins = m.start() + sep_in_updated.start()
                    updated = updated[:ins] + quote_line + updated[ins:]

            if new_media_line:
                sep2 = re.search(r"\n---\n", updated[m.start():])
                if sep2 and new_media_line not in updated:
                    ins2 = m.start() + sep2.start()
                    updated = updated[:ins2] + "\n" + new_media_line + updated[ins2:]

            with _file_lock:
                target.write_text(updated, encoding="utf-8")

            return {
                "status": "ok",
                "action": "merged",
                "fragment_id": m.group("fid"),
                "written_to": str(target),
                "emotion_updated": merged_emotion,
            }

    return None


# ---------------------------------------------------------------------------
# Event hint sniffing
# ---------------------------------------------------------------------------

_EVENT_HINT_RE = re.compile(
    r"(旅[行游]|出[发差]|到达|机场|候机|酒店|加班|开[会工]|"
    r"聚[餐会]|生日|毕业|搬家|travel|trip|flight|meeting)",
    re.IGNORECASE,
)


# ===========================================================================
# CORE TOOL 1: record_fragment
# ===========================================================================

def record_fragment(
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
    resolve_sender: Any | None = None,
) -> dict[str, Any]:
    """Record a life fragment into the local vault.

    ``resolve_sender`` is an optional callable ``(name, id) -> display_name``
    injected by the adapter layer (e.g. identity lookup). If ``None``, the
    raw ``sender_name`` is used as-is.
    """
    ensure_vault()

    if context_type not in CONTEXT_TYPES:
        return {"status": "error", "message": f"Unknown context_type '{context_type}'. Use: {CONTEXT_TYPES}"}

    if resolve_sender is not None:
        sender_name = resolve_sender(sender_name)

    ts = now_iso()
    emotion = emotion_tag or "🫧 neutral"

    # ── Sharded media storage ─────────────────────────────────────────
    stored_media: str | None = None
    media_reused = False
    if media_path:
        src = Path(media_path)
        if src.exists():
            try:
                dest, media_reused = store_media(src)
                stored_media = str(dest)
            except ValueError as e:
                return {"status": "error", "message": str(e)}
        else:
            stored_media = media_path

    media_md_line = media_md_tag(stored_media) if stored_media else None

    # ── Three-context routing ────────────────────────────────────────
    target = resolve_target(context_type, event_name=event_name, group_id=group_id)

    # ── Node dedup: try merge before creating new block ──────────────
    merge_result = try_merge_fragment(
        target, sender_name, story_node_id, emotion, content, media_md_line,
    )
    if merge_result is not None:
        merge_result["context_type"] = context_type
        if media_reused:
            merge_result["media_reused"] = True
        return merge_result

    # ── Build new markdown fragment ──────────────────────────────────
    frag_id = str(uuid.uuid4())[:8]
    lines = [
        f"\n### 🧩 Fragment `{frag_id}` — {ts}\n",
        f"- **From:** {sender_name}\n",
        f"- **Emotion:** {emotion}\n",
        f"- **Story Node:** `{story_node_id}` ({interaction_type})\n",
    ]
    if media_md_line:
        lines.append(media_md_line + "\n")
    lines.append(f"\n> {content}\n\n---\n")
    md_block = "".join(lines)

    # ── Annotation stitching (circle & event modes) ──────────────────
    inserted = False
    if interaction_type in ("reaction", "complement") and target.exists():
        sibling_pattern = rf"Story Node.*`{re.escape(story_node_id)}`"
        inserted = insert_md_after_pattern(target, sibling_pattern, md_block)

    if not inserted:
        append_md(target, md_block)

    # ── Auto-sniff potential new events ──────────────────────────────
    event_hint: str | None = None
    if context_type != "event" and not event_name and _EVENT_HINT_RE.search(content):
        event_hint = _EVENT_HINT_RE.search(content).group(0)  # type: ignore[union-attr]

    # ── Persist fragment index ───────────────────────────────────────
    index_path = _brain_path(FRAGMENT_INDEX_FILE)
    index: list[dict[str, Any]] = read_json(index_path, default=[])
    index.append({
        "id": frag_id,
        "ts": ts,
        "sender": sender_name,
        "story_node_id": story_node_id,
        "interaction_type": interaction_type,
        "context_type": context_type,
        "emotion": emotion,
        "event": event_name,
        "group_id": group_id,
        "media": stored_media,
        "file": str(target),
    })
    write_json(index_path, index)

    result: dict[str, Any] = {
        "status": "ok",
        "context_type": context_type,
        "fragment_id": frag_id,
        "written_to": str(target),
        "annotation_stitched": inserted,
    }
    if media_reused:
        result["media_reused"] = True
    if event_hint:
        result["event_hint"] = event_hint
        result["suggestion"] = (
            f"Lumi detected a '{event_hint}' vibe ✨ "
            f"Want me to start a dedicated Story Scroll for this?"
        )
    return result


# ===========================================================================
# CORE TOOL 2: manage_event
# ===========================================================================

def manage_event(
    action: str,
    event_name: str,
    *,
    group_id: str | None = None,
) -> dict[str, Any]:
    """Start, stop, or query a long-running story event."""
    ensure_vault()

    if action not in ("start", "stop", "query"):
        return {"status": "error", "message": f"Unknown action '{action}'. Use start / stop / query."}

    registry_path = VAULT_ROOT / "Events" / EVENTS_REGISTRY_FILE
    registry: dict[str, Any] = read_json(registry_path, default={})

    fname = event_filename(event_name, group_id)
    registry_key = fname.removesuffix(".md")
    event_file = VAULT_ROOT / "Events" / fname

    if action == "start":
        if registry_key in registry and registry[registry_key].get("active"):
            return {"status": "noop", "message": f"Event '{event_name}' is already active."}

        registry[registry_key] = {
            "event_name": event_name,
            "group_id": group_id,
            "started_at": now_iso(),
            "ended_at": None,
            "active": True,
        }
        write_json(registry_path, registry)

        group_line = f"  \n> Group: `{group_id}`\n" if group_id else ""
        header = (
            f"# 🚩 {event_name}\n\n"
            f"> Created by Lumi on {now_iso()}\n"
            f"{group_line}\n---\n"
        )
        with _file_lock:
            event_file.parent.mkdir(parents=True, exist_ok=True)
            event_file.write_text(header, encoding="utf-8")

        return {
            "status": "ok",
            "action": "started",
            "event": event_name,
            "registry_key": registry_key,
            "file": str(event_file),
        }

    if action == "stop":
        if registry_key not in registry or not registry[registry_key].get("active"):
            return {"status": "error", "message": f"Event '{event_name}' is not currently active."}

        registry[registry_key]["ended_at"] = now_iso()
        registry[registry_key]["active"] = False
        write_json(registry_path, registry)

        closing = (
            f"\n---\n\n## 🔒 Scroll Sealed\n\n"
            f"> '{event_name}' was sealed by Lumi on {now_iso()}.\n"
            f"> Precious memories safely locked in the vault ✨\n"
        )
        append_md(event_file, closing)

        return {"status": "ok", "action": "stopped", "event": event_name, "registry_key": registry_key}

    # query
    meta = registry.get(registry_key)
    if meta is None:
        return {"status": "not_found", "message": f"No event named '{event_name}' (key={registry_key})."}

    fragment_count = 0
    if event_file.exists():
        text = event_file.read_text(encoding="utf-8")
        fragment_count = len(re.findall(r"### 🧩 Fragment", text))

    return {
        "status": "ok",
        "event": event_name,
        "registry_key": registry_key,
        "group_id": meta.get("group_id"),
        "active": meta.get("active", False),
        "started_at": meta.get("started_at"),
        "ended_at": meta.get("ended_at"),
        "fragment_count": fragment_count,
    }


# ===========================================================================
# CORE TOOL 3: manage_fragment (CRUD)
# ===========================================================================

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
    """Full CRUD on fragments: search / get / update / delete."""
    ensure_vault()

    if action not in ("search", "get", "update", "delete"):
        return {"status": "error", "message": f"Unknown action '{action}'. Use search / get / update / delete."}

    index_path = _brain_path(FRAGMENT_INDEX_FILE)
    index: list[dict[str, Any]] = read_json(index_path, default=[])

    # ── SEARCH ───────────────────────────────────────────────────────
    if action == "search":
        results = index
        if sender:
            results = [f for f in results if f.get("sender") == sender]
        if context_type:
            results = [f for f in results if f.get("context_type") == context_type]
        if group_id:
            results = [f for f in results if f.get("group_id") == group_id]
        if event_name:
            results = [f for f in results if f.get("event") == event_name]
        if story_node_id:
            results = [f for f in results if f.get("story_node_id") == story_node_id]
        if date_from:
            results = [f for f in results if f.get("ts", "") >= date_from]
        if date_to:
            results = [f for f in results if f.get("ts", "") <= date_to]
        if keyword:
            kw = keyword.lower()
            filtered = []
            for f in results:
                if kw in f.get("sender", "").lower() or kw in f.get("emotion", "").lower():
                    filtered.append(f)
                    continue
                md_file = Path(f.get("file", ""))
                if md_file.exists():
                    fid = f.get("id", "")
                    text = md_file.read_text(encoding="utf-8")
                    frag_match = re.search(rf"Fragment `{re.escape(fid)}`.*?\n---\n", text, re.DOTALL)
                    if frag_match and kw in frag_match.group(0).lower():
                        filtered.append(f)
            results = filtered

        total = len(results)
        results = results[-limit:]
        return {"status": "ok", "action": "search", "total": total, "returned": len(results), "fragments": results}

    # ── GET ───────────────────────────────────────────────────────────
    if action == "get":
        if not fragment_id:
            return {"status": "error", "message": "fragment_id is required for 'get'."}
        entry = next((f for f in index if f["id"] == fragment_id), None)
        if not entry:
            return {"status": "not_found", "message": f"No fragment with id '{fragment_id}'."}
        md_file = Path(entry["file"])
        md_block: str | None = None
        if md_file.exists():
            text = md_file.read_text(encoding="utf-8")
            match = re.search(rf"### 🧩 Fragment `{re.escape(fragment_id)}`.*?\n---\n", text, re.DOTALL)
            if match:
                md_block = match.group(0)
        return {"status": "ok", "action": "get", "index_entry": entry, "markdown": md_block}

    # ── UPDATE ───────────────────────────────────────────────────────
    if action == "update":
        if not fragment_id:
            return {"status": "error", "message": "fragment_id is required for 'update'."}
        if not new_content and not new_emotion:
            return {"status": "error", "message": "Provide new_content and/or new_emotion."}

        entry_idx = next((i for i, f in enumerate(index) if f["id"] == fragment_id), None)
        if entry_idx is None:
            return {"status": "not_found", "message": f"No fragment with id '{fragment_id}'."}

        entry = index[entry_idx]
        md_file = Path(entry["file"])
        changes: list[str] = []

        if md_file.exists():
            with _file_lock:
                text = md_file.read_text(encoding="utf-8")

            match = re.search(
                rf"(### 🧩 Fragment `{re.escape(fragment_id)}`.*?\n)(---\n)",
                text, re.DOTALL,
            )
            if match:
                block = match.group(1)
                updated_block = block

                if new_emotion:
                    old_emo = re.search(r"- \*\*Emotion:\*\* (.+)\n", block)
                    if old_emo:
                        updated_block = updated_block.replace(old_emo.group(0), f"- **Emotion:** {new_emotion}\n", 1)
                    entry["emotion"] = new_emotion
                    changes.append("emotion")

                if new_content:
                    old_quotes = re.findall(r"^> .+$", block, re.MULTILINE)
                    if old_quotes:
                        last_quote = old_quotes[-1]
                        pos = updated_block.rfind(last_quote)
                        insert_after = pos + len(last_quote)
                        updated_block = (
                            updated_block[:insert_after]
                            + f"\n> ✏ _{now_iso()}_ — {new_content}"
                            + updated_block[insert_after:]
                        )
                    else:
                        updated_block = updated_block.rstrip() + f"\n> ✏ _{now_iso()}_ — {new_content}\n"
                    changes.append("content")

                text = text[:match.start()] + updated_block + match.group(2) + text[match.end():]
                with _file_lock:
                    md_file.write_text(text, encoding="utf-8")

        index[entry_idx] = entry
        write_json(index_path, index)
        return {"status": "ok", "action": "updated", "fragment_id": fragment_id, "changes": changes, "file": str(md_file)}

    # ── DELETE ───────────────────────────────────────────────────────
    if not fragment_id:
        return {"status": "error", "message": "fragment_id is required for 'delete'."}

    entry_idx = next((i for i, f in enumerate(index) if f["id"] == fragment_id), None)
    if entry_idx is None:
        return {"status": "not_found", "message": f"No fragment with id '{fragment_id}'."}

    entry = index.pop(entry_idx)
    md_file = Path(entry["file"])

    if md_file.exists():
        with _file_lock:
            text = md_file.read_text(encoding="utf-8")
        cleaned = re.sub(
            rf"\n### 🧩 Fragment `{re.escape(fragment_id)}`.*?\n---\n",
            "\n", text, count=1, flags=re.DOTALL,
        )
        with _file_lock:
            md_file.write_text(cleaned, encoding="utf-8")

    write_json(index_path, index)
    return {"status": "ok", "action": "deleted", "fragment_id": fragment_id, "file": str(md_file)}


# ===========================================================================
# PORTRAITS SYSTEM — consolidated identity + circle dictionary
# ===========================================================================

def _load_portraits() -> dict[str, Any]:
    """Load ``Portraits.json``, migrating legacy files on first call.

    Schema::

        {
          "owner": { "account_id", "display_name", "set_at" },
          "entities": {
            "<name_or_id>": {
              "display_name": str,
              "original_name": str | None,
              "first_seen": str,
              "milestones": [ { "label", "date", "note?" } ],
              "evolving_impressions": [ { "ts", "impression" } ],
              "traits": [ str ]
            }
          }
        }
    """
    path = _brain_path(PORTRAITS_FILE)

    if path.exists():
        return read_json(path, default={"owner": None, "entities": {}})

    portraits: dict[str, Any] = {"owner": None, "entities": {}}

    # Migrate legacy identity.json
    id_path = _brain_path(_LEGACY_IDENTITY_FILE)
    if id_path.exists():
        old_id = read_json(id_path, default={})
        if old_id.get("owner"):
            portraits["owner"] = old_id["owner"]
        for cid, cdata in old_id.get("contacts", {}).items():
            portraits["entities"][cid] = {
                "display_name": cdata.get("display_name", cid),
                "original_name": cdata.get("original_name"),
                "first_seen": cdata.get("set_at", now_iso()),
                "milestones": [],
                "evolving_impressions": [],
                "traits": [],
            }

    # Migrate legacy Circle_Dictionary.json
    cd_path = _brain_path(_LEGACY_CIRCLE_DICT_FILE)
    if cd_path.exists():
        old_cd = read_json(cd_path, default={})
        for user, info in old_cd.items():
            ent = portraits["entities"].setdefault(user, {
                "display_name": user,
                "original_name": None,
                "first_seen": info.get("first_seen", now_iso()),
                "milestones": [],
                "evolving_impressions": [],
                "traits": [],
            })
            for trait in info.get("traits", []):
                if trait not in ent["traits"]:
                    ent["traits"].append(trait)

    write_json(path, portraits)
    return portraits


def _save_portraits(data: dict[str, Any]) -> None:
    write_json(_brain_path(PORTRAITS_FILE), data)


# ---------------------------------------------------------------------------
# Identity management (formerly manage_identity)
# ---------------------------------------------------------------------------

def resolve_display_name(sender_name: str, sender_id: str | None = None) -> str:
    """Best display name for a sender, auto-registering unknown contacts."""
    if not sender_id:
        return sender_name

    portraits = _load_portraits()
    entities = portraits.setdefault("entities", {})

    if sender_id in entities:
        return entities[sender_id]["display_name"]

    owner = portraits.get("owner")
    if owner and owner.get("account_id") == sender_id:
        return owner["display_name"]

    entities[sender_id] = {
        "display_name": sender_name,
        "original_name": sender_name,
        "first_seen": now_iso(),
        "milestones": [],
        "evolving_impressions": [],
        "traits": [],
    }
    _save_portraits(portraits)
    return sender_name


def manage_identity(
    action: str,
    *,
    display_name: str | None = None,
    account_id: str | None = None,
    original_name: str | None = None,
) -> dict[str, Any]:
    """Manage the identity registry (init_owner / get_owner / rename / lookup / list_contacts)."""
    ensure_vault()
    portraits = _load_portraits()

    if action == "init_owner":
        if not display_name:
            return {"status": "error", "message": "display_name is required to set up the owner."}
        if portraits.get("owner"):
            return {
                "status": "already_set",
                "message": f"Owner is already '{portraits['owner']['display_name']}'. Use 'rename' to change.",
                "owner": portraits["owner"],
            }
        owner_id = account_id or f"owner_{uuid.uuid4().hex[:8]}"
        portraits["owner"] = {
            "account_id": owner_id,
            "display_name": display_name,
            "set_at": now_iso(),
        }
        _save_portraits(portraits)
        return {"status": "ok", "action": "owner_initialized", "owner": portraits["owner"]}

    if action == "get_owner":
        owner = portraits.get("owner")
        if not owner:
            return {"status": "no_owner", "message": "No owner set yet. Please ask the user for their name."}
        return {"status": "ok", "action": "get_owner", "owner": owner}

    if action == "rename":
        if not display_name:
            return {"status": "error", "message": "display_name is required for rename."}
        owner = portraits.get("owner")
        entities = portraits.setdefault("entities", {})

        if not account_id or (owner and owner.get("account_id") == account_id):
            if not owner:
                return {"status": "error", "message": "No owner to rename. Use 'init_owner' first."}
            old_name = owner["display_name"]
            owner["display_name"] = display_name
            owner["set_at"] = now_iso()
            _save_portraits(portraits)
            return {"status": "ok", "action": "owner_renamed", "old_name": old_name, "new_name": display_name}

        if account_id in entities:
            old_name = entities[account_id]["display_name"]
            entities[account_id]["display_name"] = display_name
            _save_portraits(portraits)
            return {"status": "ok", "action": "contact_renamed", "account_id": account_id, "old_name": old_name, "new_name": display_name}

        entities[account_id] = {
            "display_name": display_name,
            "original_name": original_name or display_name,
            "first_seen": now_iso(),
            "milestones": [],
            "evolving_impressions": [],
            "traits": [],
        }
        _save_portraits(portraits)
        return {"status": "ok", "action": "contact_registered", "account_id": account_id, "display_name": display_name}

    if action == "lookup":
        if not account_id:
            return {"status": "error", "message": "account_id is required for lookup."}
        owner = portraits.get("owner")
        if owner and owner.get("account_id") == account_id:
            return {"status": "ok", "action": "lookup", "type": "owner", "profile": owner}
        entities = portraits.get("entities", {})
        if account_id in entities:
            return {"status": "ok", "action": "lookup", "type": "contact", "profile": entities[account_id]}
        return {"status": "not_found", "message": f"No identity found for '{account_id}'."}

    if action == "list_contacts":
        entities = portraits.get("entities", {})
        return {
            "status": "ok", "action": "list_contacts",
            "owner": portraits.get("owner"),
            "total_contacts": len(entities),
            "contacts": entities,
        }

    return {"status": "error", "message": f"Unknown action '{action}'. Use: init_owner, get_owner, rename, lookup, list_contacts."}


# ---------------------------------------------------------------------------
# update_portrait — dynamic personality/milestone updates
# ---------------------------------------------------------------------------

def update_portrait(
    entity_name: str,
    *,
    new_impression: str | None = None,
    date: str | None = None,
    is_milestone: bool = False,
    milestone_label: str | None = None,
    traits: list[str] | None = None,
) -> dict[str, Any]:
    """Dynamically update a portrait entry.

    Called by the LLM when it notices new personality traits, preferences,
    or important dates during conversation.
    """
    ensure_vault()
    portraits = _load_portraits()
    entities = portraits.setdefault("entities", {})

    ent = entities.setdefault(entity_name, {
        "display_name": entity_name,
        "original_name": None,
        "first_seen": now_iso(),
        "milestones": [],
        "evolving_impressions": [],
        "traits": [],
    })

    changes: list[str] = []
    ts = date or today_tag()

    if new_impression:
        ent["evolving_impressions"].append({"ts": ts, "impression": new_impression})
        changes.append("impression")

    if is_milestone and milestone_label:
        ent["milestones"].append({"label": milestone_label, "date": ts, "note": new_impression or ""})
        changes.append("milestone")

    if traits:
        existing = set(ent["traits"])
        new_traits = [t_item for t_item in traits if t_item not in existing]
        ent["traits"].extend(new_traits)
        if new_traits:
            changes.append("traits")

    _save_portraits(portraits)

    return {
        "status": "ok",
        "entity": entity_name,
        "changes": changes,
        "total_milestones": len(ent["milestones"]),
        "total_impressions": len(ent["evolving_impressions"]),
        "total_traits": len(ent["traits"]),
    }


# ---------------------------------------------------------------------------
# check_time_echoes — milestone detection for the "Time Echoes" mechanism
# ---------------------------------------------------------------------------

def check_time_echoes(*, reference_date: str | None = None) -> dict[str, Any]:
    """Scan all portraits for milestones whose date matches today (MM-DD).

    Returns a list of triggered echoes for Lumi to weave into conversation.
    """
    ensure_vault()
    portraits = _load_portraits()

    check_date = reference_date or today_tag()
    mm_dd = check_date[5:]  # "MM-DD"

    echoes: list[dict[str, Any]] = []

    for name, ent in portraits.get("entities", {}).items():
        for ms in ent.get("milestones", []):
            ms_date = ms.get("date", "")
            if len(ms_date) >= 10 and ms_date[5:] == mm_dd:
                echoes.append({
                    "entity": name,
                    "display_name": ent.get("display_name", name),
                    "milestone": ms["label"],
                    "original_date": ms_date,
                    "note": ms.get("note", ""),
                })

    owner = portraits.get("owner")

    return {
        "status": "ok",
        "checked_date": check_date,
        "echoes": echoes,
        "owner": owner.get("display_name") if owner else None,
    }


# ===========================================================================
# CORE TOOL 4: save_keepsake (formerly save_meme)
# ===========================================================================

def save_keepsake(
    title: str,
    context_tags: list[str],
    *,
    media_path: str | None = None,
) -> dict[str, Any]:
    """Archive a legendary moment into Keepsakes for future recalls."""
    ensure_vault()

    ks_path = _brain_path(KEEPSAKES_FILE)
    keepsakes: list[dict[str, Any]] = read_json(ks_path, default=[])

    ks_id = str(uuid.uuid4())[:8]
    entry: dict[str, Any] = {
        "id": ks_id,
        "title": title,
        "context_tags": context_tags,
        "saved_at": now_iso(),
        "recall_count": 0,
    }

    media_reused = False
    if media_path:
        src = Path(media_path)
        if src.exists():
            try:
                dest, media_reused = store_media(src)
                entry["media"] = str(dest)
            except ValueError as e:
                return {"status": "error", "message": str(e)}
        else:
            entry["media"] = media_path
            entry["media_note"] = "original file not found at save time"

    keepsakes.append(entry)
    write_json(ks_path, keepsakes)

    result: dict[str, Any] = {
        "status": "ok",
        "keepsake_id": ks_id,
        "title": title,
        "tags": context_tags,
        "stored_in": str(ks_path),
    }
    if media_reused:
        result["media_reused"] = True
    return result


# ===========================================================================
# CORE TOOL 5: render_lumi_canvas
# ===========================================================================

_EMOTION_PALETTE: dict[str, str] = {
    "happy": "#FFD93D", "excited": "#FFCB77", "joy": "#FFE066",
    "proud": "#F7B731", "love": "#FF6B81", "grateful": "#F8A5C2",
    "hopeful": "#A3D9A5", "relieved": "#A8D8EA", "inspired": "#C9B1FF",
    "amused": "#FEE440", "determined": "#FF9F43", "confident": "#FFA502",
    "calm": "#B8E6CF", "peaceful": "#D4F1F4", "nostalgic": "#DDA0DD",
    "reflective": "#B0C4DE", "contemplative": "#B0C4DE", "neutral": "#E2E2E2",
    "noted": "#D5DBDB", "analytical": "#85C1E9",
    "sad": "#8093F1", "melancholy": "#7B68EE", "lonely": "#9B9BCC",
    "tired": "#A0A0B8", "exhausted": "#8E8EA0", "anxious": "#E8A87C",
    "nervous": "#DDA0DD", "frustrated": "#E57373", "angry": "#FF6B6B",
    "annoyed": "#FF8A80", "jealous": "#81C784",
    "shocked": "#FF4757", "terrified": "#D63031", "traumatized": "#C0392B",
    "embarrassed": "#FF9FF3", "cringe": "#FD79A8", "chaotic": "#A29BFE",
    "sarcastic": "#778BEB", "savage": "#E056A0",
    "breathtaking": "#54A0FF", "amazed": "#48DBFB", "mindblown": "#0ABDE3",
    "beautiful": "#55EFC4", "aesthetic": "#81ECEC",
    "hungry": "#FF6348", "thrifty": "#BADC58", "cozy": "#FDCB6E",
    "adventurous": "#F39C12", "overconfident": "#E17055",
}

_VIBE_THEMES: dict[str, dict[str, str]] = {
    "dark gaming": {
        "bg": "#0a0a1a", "surface": "#14142b", "text": "#e0e0ff",
        "accent": "#7c4dff", "accent2": "#448aff", "muted": "#555580",
    },
    "cottagecore": {
        "bg": "#fdf6ec", "surface": "#fff8f0", "text": "#5d4037",
        "accent": "#a1887f", "accent2": "#81c784", "muted": "#bcaaa4",
    },
    "zine aesthetic": {
        "bg": "#1a1a2e", "surface": "#16213e", "text": "#eaeaea",
        "accent": "#e94560", "accent2": "#0f3460", "muted": "#533483",
    },
    "desert stargazing": {
        "bg": "#0d1117", "surface": "#161b22", "text": "#c9d1d9",
        "accent": "#f0883e", "accent2": "#58a6ff", "muted": "#484f58",
    },
}
_DEFAULT_THEME: dict[str, str] = {
    "bg": "#fafafa", "surface": "#ffffff", "text": "#2d3436",
    "accent": "#6c5ce7", "accent2": "#00b894", "muted": "#b2bec3",
}


def _html_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _luminance_from_hex(h: str) -> float:
    h = h.lstrip("#")
    if len(h) != 6:
        return 0.9
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def _sender_color(name: str) -> str:
    return f"hsl({hash(name) % 360}, 55%, 50%)"


def parse_fragments_from_md(path: Path) -> list[dict[str, Any]]:
    """Extract structured fragment data from a Lumi markdown file."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    fragments: list[dict[str, Any]] = []
    for m in _FRAGMENT_HEADER_RE.finditer(text):
        frag_end = re.search(r"\n---\n", text[m.end():])
        block_end = m.end() + frag_end.start() if frag_end else len(text)
        body = text[m.end():block_end].strip()

        media_match = re.search(
            r"(?:!\[image\]\(([^)]+)\)"
            r"|\[video: [^\]]*\]\(([^)]+)\)"
            r"|\[audio: [^\]]*\]\(([^)]+)\))",
            body,
        )
        quotes = re.findall(r"^>\s*(.+)$", body, re.MULTILINE)

        emotion_raw = m.group("emotion").split("\u2192")[-1].strip()
        color = _EMOTION_PALETTE.get("neutral", "#E2E2E2")
        for key, val in _EMOTION_PALETTE.items():
            if key in emotion_raw.lower():
                color = val
                break

        fragments.append({
            "fragment_id": m.group("fid"),
            "timestamp": m.group("ts"),
            "sender": m.group("sender"),
            "emotion": m.group("emotion"),
            "emotion_color": color,
            "story_node_id": m.group("node"),
            "media": next((g for g in media_match.groups() if g), None) if media_match else None,
            "quotes": quotes,
        })
    return fragments


def render_media_embed(media_path: str) -> str:
    """HTML embed tag for a media file. Only vault-internal paths are embedded."""
    if media_path.startswith(("file://", "http://", "https://", "/")):
        return f'<div class="card-media">📎 {_html_escape(Path(media_path).name)}</div>'

    p = Path(media_path)
    ext = p.suffix.lower()

    if str(VAULT_ROOT) in media_path:
        try:
            validate_within_vault(p)
        except ValueError:
            return f'<div class="card-media">📎 {_html_escape(p.name)}</div>'
        rel = Path("..") / p.relative_to(VAULT_ROOT)
    else:
        if ".." in str(p):
            return f'<div class="card-media">📎 {_html_escape(p.name)}</div>'
        rel = p

    escaped = _html_escape(str(rel))
    name = _html_escape(p.name)

    if ext in IMAGE_EXTS:
        return f'<div class="card-media"><img src="{escaped}" alt="{name}" loading="lazy"></div>'
    if ext in VIDEO_EXTS:
        return (
            f'<div class="card-media"><video src="{escaped}" controls preload="metadata"></video>'
            f'<span class="media-label">🎬 {name}</span></div>'
        )
    if ext in AUDIO_EXTS:
        return (
            f'<div class="card-media"><audio src="{escaped}" controls preload="metadata"></audio>'
            f'<span class="media-label">🎙 {name}</span></div>'
        )
    return f'<div class="card-media">📎 <a href="{escaped}">{name}</a></div>'


def _render_single_card(frag: dict[str, Any], side: str, idx: int) -> str:
    sender = _html_escape(frag["sender"])
    initial = sender[0].upper()
    ts_short = frag["timestamp"][5:16].replace("T", " ")
    emotion = _html_escape(frag["emotion"])
    color = frag["emotion_color"]
    avatar_bg = _sender_color(frag["sender"])

    quotes_html = ""
    for q in frag.get("quotes", []):
        quotes_html += f"<blockquote>{_html_escape(q)}</blockquote>"

    media_html = render_media_embed(frag["media"]) if frag.get("media") else ""

    return f"""<div class="tl-node {side}" style="animation-delay:{idx * 0.08}s">
  <div class="card" style="border-left-color:{color}">
    <div class="card-header">
      <div class="avatar" style="background:{avatar_bg}">{initial}</div>
      <span class="sender">{sender}</span>
      <span class="timestamp">{ts_short}</span>
    </div>
    <span class="emotion-badge" style="background:{color}">{emotion}</span>
    <div class="card-body">{quotes_html}</div>
    {media_html}
  </div>
</div>"""


def _render_flip_card(frags: list[dict[str, Any]], side: str, idx: int, locale: str = "en") -> str:
    front = frags[0]
    back = frags[1] if len(frags) > 1 else frags[0]

    def _card_inner(f: dict[str, Any]) -> str:
        sender = _html_escape(f["sender"])
        initial = sender[0].upper()
        ts_short = f["timestamp"][5:16].replace("T", " ")
        emotion = _html_escape(f["emotion"])
        color = f["emotion_color"]
        avatar_bg = _sender_color(f["sender"])
        quotes = "".join(f"<blockquote>{_html_escape(q)}</blockquote>" for q in f.get("quotes", []))
        media = render_media_embed(f["media"]) if f.get("media") else ""
        return (
            f'<div class="card" style="border-left-color:{color}">'
            f'<div class="card-header">'
            f'<div class="avatar" style="background:{avatar_bg}">{initial}</div>'
            f'<span class="sender">{sender}</span>'
            f'<span class="timestamp">{ts_short}</span>'
            f'</div>'
            f'<span class="emotion-badge" style="background:{color}">{emotion}</span>'
            f'<div class="card-body">{quotes}</div>'
            f'{media}</div>'
        )

    extra_count = len(frags) - 2
    extra_note = t("annotation_extra", locale, n=extra_count) if extra_count > 0 else ""
    flip_label = t("annotation_label", locale, n=len(frags), extra=extra_note)
    flip_hint = t("flip_hint", locale)

    return f"""<div class="tl-node {side}" style="animation-delay:{idx * 0.08}s">
  <div class="flip-label">{flip_label}</div>
  <div class="flip-container">
    <div class="flipper">
      <div class="flip-front">{_card_inner(front)}</div>
      <div class="flip-back">{_card_inner(back)}</div>
    </div>
  </div>
  <div class="flip-hint">{flip_hint}</div>
</div>"""


def _assets_dir() -> Path:
    """Resolve the static assets directory (sibling of src/)."""
    return Path(__file__).resolve().parent.parent / "assets"


def generate_html_canvas(payload: dict[str, Any], locale: str = "en") -> Path:
    """Render a self-contained HTML memory scroll and save it to the vault."""
    title = _html_escape(payload["canvas_title"])
    vibe = payload.get("vibe", "warm default")
    lang = locale if locale in SUPPORTED_LOCALES else "en"
    theme = _DEFAULT_THEME.copy()
    for key, val in _VIBE_THEMES.items():
        if key in vibe.lower():
            theme = val
            break
    is_dark = _luminance_from_hex(theme["bg"]) < 0.4

    cards = payload.get("annotation_cards", [])
    keepsakes = payload.get("keepsakes", [])

    timeline_html_parts: list[str] = []
    for i, card in enumerate(cards):
        frags = card["fragments"]
        multi = card["is_multi_perspective"]
        side = "left" if i % 2 == 0 else "right"
        if multi:
            timeline_html_parts.append(_render_flip_card(frags, side, i, locale=lang))
        else:
            timeline_html_parts.append(_render_single_card(frags[0], side, i))

    timeline_html = "\n".join(timeline_html_parts)

    keepsake_html = ""
    if keepsakes:
        ks_items = []
        for m in keepsakes:
            tags = ", ".join(m.get("context_tags", []))
            ks_media = render_media_embed(m["media"]) if m.get("media") else ""
            ks_items.append(
                f'<div class="meme-item">'
                f'<div class="meme-info">'
                f'<span class="meme-icon">🃏</span>'
                f'<strong>{_html_escape(m["title"])}</strong>'
                f'<span class="meme-tags">{_html_escape(tags)}</span>'
                f'</div>{ks_media}</div>'
            )
        keepsake_html = (
            '<section class="meme-gallery">'
            f'<h2>{t("keepsakes_gallery_title", lang)}</h2>'
            + "\n".join(ks_items)
            + "</section>"
        )

    stats = (
        f'<div class="stats">'
        f'<span>📝 {payload["total_fragments"]} {t("stat_fragments", lang)}</span>'
        f'<span>🧩 {payload["total_nodes"]} {t("stat_story_nodes", lang)}</span>'
        f'<span>🎨 {_html_escape(vibe)}</span>'
        f'</div>'
    )

    tpl_path = _assets_dir() / "canvas_template.html"
    tpl = tpl_path.read_text(encoding="utf-8")

    html = tpl.format(
        html_lang="zh-CN" if lang == "zh" else "en",
        title=title,
        title_suffix=t("title_suffix", lang),
        theme_bg=theme["bg"],
        theme_surface=theme["surface"],
        theme_text=theme["text"],
        theme_accent=theme["accent"],
        theme_accent2=theme["accent2"],
        theme_muted=theme["muted"],
        shadow_card=0.25 if is_dark else 0.08,
        shadow_card_hover=0.35 if is_dark else 0.12,
        shadow_meme=0.2 if is_dark else 0.06,
        stats=stats,
        timeline_html=timeline_html,
        meme_html=keepsake_html,
        scroll_subtitle=t("scroll_subtitle", lang),
        cta_heading=t("cta_heading", lang),
        cta_body=t("cta_body", lang),
        cta_badge=t("cta_badge", lang),
        footer_rendered_by=t("footer_rendered_by", lang),
        footer_rendered_suffix=t("footer_rendered_suffix", lang),
        render_date=now_iso()[:10],
    )

    safe_title = sanitize_path_component(payload["canvas_title"])
    html_file = VAULT_ROOT / "Brain" / f"canvas_{safe_title}.html"
    validate_within_vault(html_file)
    html_file.parent.mkdir(parents=True, exist_ok=True)
    with _file_lock:
        html_file.write_text(html, encoding="utf-8")
    return html_file


def render_lumi_canvas(
    target_event: str,
    *,
    context_type: str = "event",
    vibe_override: str | None = None,
    group_id: str | None = None,
    locale: str = "en",
) -> dict[str, Any]:
    """Read vault data and render a Canvas (HTML scroll).

    Returns a structured payload with annotation cards and an HTML file path.
    """
    ensure_vault()
    lang = locale if locale in SUPPORTED_LOCALES else "en"

    solo_prefix = t("canvas_prefix_solo", lang)
    circle_prefix = t("canvas_prefix_circle", lang)
    today_prefix = t("canvas_prefix_today", lang)

    if target_event == "this_month" and context_type == "solo":
        source = resolve_target("solo")
        canvas_title = f"{solo_prefix} — {month_tag()}"
    elif context_type == "circle":
        source = resolve_target("circle", group_id=group_id)
        canvas_title = f"{circle_prefix} — {group_id or 'default'} ({month_tag()})"
    else:
        event_name = None if target_event == "today" else target_event
        if target_event == "today":
            source = resolve_target("solo")
            canvas_title = f"{today_prefix} — {today_tag()}"
        else:
            source = resolve_target(context_type, event_name=event_name, group_id=group_id)
            canvas_title = target_event

    if not source.exists():
        return {"status": "error", "message": t("no_data_found", lang, target=target_event)}

    fragments = parse_fragments_from_md(source)
    if not fragments:
        return {"status": "empty", "message": t("no_fragments_yet", lang, target=target_event)}

    node_groups: dict[str, list[dict[str, Any]]] = {}
    for frag in fragments:
        node_groups.setdefault(frag["story_node_id"], []).append(frag)

    annotation_cards: list[dict[str, Any]] = []
    for node_id, group in node_groups.items():
        annotation_cards.append({
            "story_node_id": node_id,
            "perspectives": len(group),
            "is_multi_perspective": len(group) > 1,
            "fragments": group,
        })

    keepsakes_list: list[dict[str, Any]] = read_json(_brain_path(KEEPSAKES_FILE), default=[])
    search_tags = {target_event.lower()}
    if group_id:
        search_tags.add(group_id.lower())
    relevant_keepsakes = [
        k for k in keepsakes_list
        if search_tags & {tg.lower() for tg in k.get("context_tags", [])}
    ]

    portraits = _load_portraits()
    group_traits = portraits.get("entities", {}).get("group_vibe", {}).get("traits", [])
    vibe = vibe_override or ("warm default" if not group_traits else group_traits[0])

    payload: dict[str, Any] = {
        "status": "ok",
        "context_type": context_type,
        "canvas_title": canvas_title,
        "source_file": str(source),
        "vibe": vibe,
        "total_fragments": len(fragments),
        "total_nodes": len(annotation_cards),
        "annotation_cards": annotation_cards,
        "keepsakes": relevant_keepsakes,
        "timeline": [
            {"ts": f["timestamp"], "sender": f["sender"], "emotion_color": f["emotion_color"]}
            for f in fragments
        ],
    }

    html_path = generate_html_canvas(payload, locale=lang)
    payload["html_file"] = str(html_path)

    return payload


# ===========================================================================
# CAPSULE — .lumi ZIP export / import
# ===========================================================================

import mimetypes
import base64
import tempfile


def _embed_media_base64(media_path: str | None) -> dict[str, Any] | None:
    """Base64-encode a vault-local media file for seed compatibility."""
    if not media_path:
        return None
    p = Path(media_path)
    if not p.exists():
        return None
    try:
        validate_within_vault(p)
    except ValueError:
        return None
    mime, _ = mimetypes.guess_type(str(p))
    if not mime:
        ext = p.suffix.lower()
        if ext in IMAGE_EXTS:
            mime = f"image/{ext.lstrip('.')}"
        elif ext in VIDEO_EXTS:
            mime = f"video/{ext.lstrip('.')}"
        elif ext in AUDIO_EXTS:
            mime = f"audio/{ext.lstrip('.')}"
        else:
            mime = "application/octet-stream"
    data = p.read_bytes()
    return {"filename": p.name, "mime": mime, "size_bytes": len(data), "data": base64.b64encode(data).decode("ascii")}


def _screenshot_html(html_path: Path, png_path: Path) -> str | None:
    """Screenshot the HTML scroll via Playwright (sandbox: JS disabled, net blocked)."""
    try:
        from playwright.sync_api import sync_playwright  # type: ignore[import-untyped]
    except ImportError:
        return None
    try:
        validate_within_vault(html_path)
    except ValueError:
        return None
    try:
        png_path.parent.mkdir(parents=True, exist_ok=True)
        vault_prefix = f"file://{VAULT_ROOT.resolve()}"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 800, "height": 600}, java_script_enabled=False)
            page = context.new_page()

            def _block_external(route):
                url = route.request.url
                if url.startswith(vault_prefix) or url.startswith("data:"):
                    route.continue_()
                else:
                    route.abort("blockedbyclient")

            page.route("**/*", _block_external)
            page.goto(f"file://{html_path.resolve()}")
            page.wait_for_load_state("networkidle")
            page.screenshot(path=str(png_path), full_page=True)
            context.close()
            browser.close()
        return str(png_path)
    except Exception:
        return None


def export_capsule(
    target_event: str,
    *,
    context_type: str = "event",
    vibe_override: str | None = None,
    group_id: str | None = None,
    locale: str = "en",
) -> dict[str, Any]:
    """Export a memory capsule as a .lumi ZIP file.

    Contents of the ZIP::

        lumi.json          — v0.2.0 node-based schema
        index.html         — degraded Canvas HTML for offline browsing
        assets/            — copied media files

    Returns the absolute path to the generated ``.lumi`` file.
    """
    canvas_result = render_lumi_canvas(
        target_event,
        context_type=context_type,
        vibe_override=vibe_override,
        group_id=group_id,
        locale=locale,
    )
    if canvas_result.get("status") != "ok":
        return canvas_result

    cards = canvas_result.get("annotation_cards", [])
    keepsakes_matched = canvas_result.get("keepsakes", [])

    # Build v0.2.0 lumi.json: timeline of nodes
    nodes: list[dict[str, Any]] = []
    media_to_copy: list[tuple[str, str]] = []  # (vault_path, zip_internal_name)

    for card in cards:
        frags = card["fragments"]
        primary = frags[0]
        annotations = frags[1:] if len(frags) > 1 else []

        def _process_media(frag: dict) -> str | None:
            mp = frag.get("media")
            if not mp:
                return None
            p = Path(mp)
            if p.exists():
                arc_name = f"assets/{p.name}"
                media_to_copy.append((str(p), arc_name))
                return arc_name
            return None

        node: dict[str, Any] = {
            "node_id": card["story_node_id"],
            "fragment": {
                "fragment_id": primary["fragment_id"],
                "timestamp": primary["timestamp"],
                "sender": primary["sender"],
                "emotion": primary["emotion"],
                "content": " | ".join(primary.get("quotes", [])),
                "media": _process_media(primary),
            },
            "annotations": [
                {
                    "fragment_id": a["fragment_id"],
                    "timestamp": a["timestamp"],
                    "sender": a["sender"],
                    "emotion": a["emotion"],
                    "content": " | ".join(a.get("quotes", [])),
                    "media": _process_media(a),
                }
                for a in annotations
            ],
        }
        nodes.append(node)

    lumi_json: dict[str, Any] = {
        "lumi_version": _LUMI_VERSION,
        "exported_at": now_iso(),
        "canvas_title": canvas_result["canvas_title"],
        "context_type": canvas_result["context_type"],
        "vibe": canvas_result.get("vibe", "warm default"),
        "total_fragments": canvas_result["total_fragments"],
        "total_nodes": canvas_result["total_nodes"],
        "timeline": nodes,
        "keepsakes": [
            {"id": k["id"], "title": k["title"], "context_tags": k.get("context_tags", []), "media": _process_media_ks(k, media_to_copy)}
            for k in keepsakes_matched
        ],
    }

    safe_title = sanitize_path_component(canvas_result["canvas_title"])
    exports_dir = VAULT_ROOT / "Brain" / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)

    lumi_path = exports_dir / f"{safe_title}.lumi"
    validate_within_vault(lumi_path)

    with zipfile.ZipFile(str(lumi_path), "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("lumi.json", json.dumps(lumi_json, ensure_ascii=False, indent=2))

        html_file = Path(canvas_result["html_file"])
        if html_file.exists():
            zf.write(str(html_file), "index.html")

        added: set[str] = set()
        for vault_p, arc_name in media_to_copy:
            if arc_name not in added and Path(vault_p).exists():
                zf.write(vault_p, arc_name)
                added.add(arc_name)

    # Optional screenshot
    html_path = Path(canvas_result["html_file"])
    png_path = exports_dir / f"{safe_title}.png"
    screenshot = _screenshot_html(html_path, png_path)

    result: dict[str, Any] = {
        "status": "ok",
        "canvas_title": canvas_result["canvas_title"],
        "context_type": canvas_result["context_type"],
        "html_file": canvas_result["html_file"],
        "capsule_file": str(lumi_path.resolve()),
        "screenshot": screenshot,
    }
    if screenshot is None:
        result["screenshot_note"] = "Install Playwright for PNG export: pip install playwright && playwright install chromium"
    return result


def _process_media_ks(keepsake: dict, media_list: list) -> str | None:
    """Helper to process keepsake media for capsule export."""
    mp = keepsake.get("media")
    if not mp:
        return None
    p = Path(mp)
    if p.exists():
        arc_name = f"assets/{p.name}"
        media_list.append((str(p), arc_name))
        return arc_name
    return None


def import_capsule(file_path: str) -> dict[str, Any]:
    """Import a .lumi capsule ZIP and merge its data into the local vault.

    Merge rules:
    - If a local ``node_id`` already exists, the local ``fragment`` is kept
      and incoming ``annotations`` are appended (no duplicates by fragment_id).
    - Media files are copied into the sharded ``Assets/`` tree.
    - Fragment index is updated.
    """
    ensure_vault()
    capsule = Path(file_path)
    if not capsule.exists():
        return {"status": "error", "message": f"Capsule not found: {file_path}"}

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            with zipfile.ZipFile(str(capsule), "r") as zf:
                zf.extractall(tmpdir)
        except zipfile.BadZipFile:
            return {"status": "error", "message": "Invalid .lumi capsule (not a valid ZIP file)."}

        lumi_json_path = Path(tmpdir) / "lumi.json"
        if not lumi_json_path.exists():
            return {"status": "error", "message": "Capsule missing lumi.json manifest."}

        data = json.loads(lumi_json_path.read_text(encoding="utf-8"))

    incoming_nodes = data.get("timeline", [])
    capsule_title = data.get("canvas_title", "imported")
    context_type = data.get("context_type", "event")

    # Load existing fragment index
    index_path = _brain_path(FRAGMENT_INDEX_FILE)
    index: list[dict[str, Any]] = read_json(index_path, default=[])
    existing_fids = {f["id"] for f in index}

    nodes_imported = 0
    annotations_merged = 0
    media_imported = 0

    for node in incoming_nodes:
        node_id = node.get("node_id", "")
        frag = node.get("fragment", {})
        annotations = node.get("annotations", [])

        # Copy media from capsule temp dir into vault
        def _import_media(media_ref: str | None) -> str | None:
            nonlocal media_imported
            if not media_ref:
                return None
            src = Path(tmpdir) / media_ref
            if not src.exists():
                return None
            ext = src.suffix.lower()
            if ext not in MEDIA_EXTS:
                return None
            digest = md5_of_file(src)
            dest = _sharded_asset_path(digest, ext)
            if not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                with _file_lock:
                    if not dest.exists():
                        shutil.copy2(str(src), str(dest))
                        media_imported += 1
            return str(dest)

        frag_media = _import_media(frag.get("media"))

        # Check if this node's fragment already exists locally
        frag_id = frag.get("fragment_id", "")
        if frag_id not in existing_fids:
            index.append({
                "id": frag_id,
                "ts": frag.get("timestamp", now_iso()),
                "sender": frag.get("sender", "unknown"),
                "story_node_id": node_id,
                "interaction_type": "imported",
                "context_type": context_type,
                "emotion": frag.get("emotion", "neutral"),
                "event": capsule_title,
                "group_id": None,
                "media": frag_media,
                "file": f"imported:{capsule_title}",
            })
            existing_fids.add(frag_id)
            nodes_imported += 1

        for ann in annotations:
            ann_id = ann.get("fragment_id", "")
            ann_media = _import_media(ann.get("media"))
            if ann_id not in existing_fids:
                index.append({
                    "id": ann_id,
                    "ts": ann.get("timestamp", now_iso()),
                    "sender": ann.get("sender", "unknown"),
                    "story_node_id": node_id,
                    "interaction_type": "annotation",
                    "context_type": context_type,
                    "emotion": ann.get("emotion", "neutral"),
                    "event": capsule_title,
                    "group_id": None,
                    "media": ann_media,
                    "file": f"imported:{capsule_title}",
                })
                existing_fids.add(ann_id)
                annotations_merged += 1

    write_json(index_path, index)

    # Import keepsakes
    incoming_ks = data.get("keepsakes", [])
    if incoming_ks:
        ks_path = _brain_path(KEEPSAKES_FILE)
        local_ks: list[dict[str, Any]] = read_json(ks_path, default=[])
        local_ids = {k["id"] for k in local_ks}
        for ks in incoming_ks:
            if ks.get("id") not in local_ids:
                local_ks.append(ks)
        write_json(ks_path, local_ks)

    return {
        "status": "ok",
        "capsule_title": capsule_title,
        "nodes_imported": nodes_imported,
        "annotations_merged": annotations_merged,
        "media_imported": media_imported,
        "keepsakes_imported": len(incoming_ks),
    }
