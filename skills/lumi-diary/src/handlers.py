"""
Lumi Diary Skill — handlers.py
Local-first tool handlers for the Lumi memory guardian agent.

Three-Context Architecture (三态空间):

  Solo/Daily/        — personal monthly journals
  Solo/Projects/     — serious personal material
  Circles/           — long-term group archives (monthly rotation)
  Events/            — temporary event groups (start → stop lifecycle)
  Assets/            — media attachments (content-addressed / MD5)
  Brain/             — circle dictionary & meme vault (shared across all)
"""

from __future__ import annotations

import base64
import hashlib
import json
import mimetypes
import re
import shutil
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants & Vault bootstrap
# ---------------------------------------------------------------------------

VAULT_ROOT = Path("Lumi_Vault")
_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
VAULT_DIRS = ("Solo/Daily", "Solo/Projects", "Circles", "Events", "Assets", "Brain", "Brain/exports")
CONTEXT_TYPES = ("solo", "circle", "event")

_IMAGE_EXTS = frozenset({".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg", ".heic"})
_VIDEO_EXTS = frozenset({".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".3gp", ".flv"})
_AUDIO_EXTS = frozenset({".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac", ".opus"})

_file_lock = threading.Lock()

_SAFE_FILENAME_RE = re.compile(r"[^\w\- ]")


def _sanitize_path_component(name: str) -> str:
    """Strip directory separators, traversal sequences, and special chars.

    Ensures the result is a single, flat filename component that cannot
    escape the intended parent directory.  Raises ``ValueError`` if the
    sanitized result is empty.
    """
    cleaned = name.replace("..", "").replace("/", "_").replace("\\", "_").replace("\x00", "")
    cleaned = _SAFE_FILENAME_RE.sub("_", cleaned).strip("_. ")
    if not cleaned:
        raise ValueError(f"Path component is empty after sanitization: {name!r}")
    return cleaned


def _validate_within_vault(path: Path) -> Path:
    """Resolve *path* and assert it falls within ``VAULT_ROOT``.

    Raises ``ValueError`` on attempted traversal outside the vault.
    """
    vault_resolved = VAULT_ROOT.resolve()
    target_resolved = path.resolve()
    if not str(target_resolved).startswith(str(vault_resolved) + "/") and target_resolved != vault_resolved:
        raise ValueError(f"Path escapes vault boundary: {path}")
    return path


def _ensure_vault() -> Path:
    """Lazily create the vault tree on first access and return the root."""
    for sub in VAULT_DIRS:
        (VAULT_ROOT / sub).mkdir(parents=True, exist_ok=True)
    return VAULT_ROOT


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _month_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


# ---------------------------------------------------------------------------
# i18n — locale string maps
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
    "meme_gallery_title": {
        "en": "🃏 Meme Vault Matches",
        "zh": "🃏 表情包宝库",
    },
    "cta_heading": {
        "en": "✨ This is a static snapshot — the real scroll is interactive!",
        "zh": "✨ 这是一张静态快照——真正的画卷是可交互的！",
    },
    "cta_body": {
        "en": (
            "Want to flip the Rashomon cards and see the other side of the story? "
            "Install <strong>Lumi</strong> and import the <code>.lumi</code> seed file "
            "to unlock the full interactive scroll on your own device."
        ),
        "zh": (
            "想翻转罗生门卡片看另一面的吐槽吗？安装 <strong>Lumi 小精灵</strong>，"
            "导入 <code>.lumi</code> 记忆种子，即可在你的设备上展开交互画卷！"
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
    "rashomon_label": {
        "en": "🎭 Rashomon · {n} perspectives{extra} — click to flip",
        "zh": "🎭 罗生门 · {n} 个视角{extra} —— 点击翻转",
    },
    "rashomon_extra": {
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


def _t(key: str, locale: str = "en", **kwargs: Any) -> str:
    """Look up a translated string by key and locale, with format kwargs."""
    entry = _I18N.get(key, {})
    text = entry.get(locale, entry.get("en", key))
    if kwargs:
        text = text.format(**kwargs)
    return text


# ---------------------------------------------------------------------------
# JSON helpers (atomic read / write with lock)
# ---------------------------------------------------------------------------

def _read_json(path: Path, *, default: Any = None) -> Any:
    """Thread-safe JSON read. Returns *default* if the file is absent or corrupt."""
    with _file_lock:
        if not path.exists():
            return default if default is not None else {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            backup = path.with_suffix(path.suffix + ".bak")
            shutil.copy2(path, backup)
            return default if default is not None else {}


def _write_json(path: Path, data: Any) -> None:
    """Thread-safe JSON write with pretty-printing."""
    with _file_lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------

def _append_md(path: Path, block: str) -> None:
    """Append a markdown block to *path*, creating the file with a header if needed."""
    with _file_lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            header = f"# 📅 {path.stem}\n\n"
            path.write_text(header, encoding="utf-8")
        with path.open("a", encoding="utf-8") as fh:
            fh.write(block)


def _insert_md_after_pattern(path: Path, pattern: str, block: str) -> bool:
    """Insert *block* after the complete fragment that contains *pattern*.

    A "complete fragment" ends at the next ``---`` separator.
    Returns ``True`` if insertion succeeded, ``False`` if pattern was not found
    (in which case the block is appended instead).
    """
    with _file_lock:
        if not path.exists():
            return False
        text = path.read_text(encoding="utf-8")
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            sep = re.search(r"\n---\n", text[match.end():])
            if sep:
                insert_pos = match.end() + sep.end()
            else:
                insert_pos = len(text)
            text = text[:insert_pos] + block + text[insert_pos:]
            path.write_text(text, encoding="utf-8")
            return True
        with path.open("a", encoding="utf-8") as fh:
            fh.write(block)
        return False


# ---------------------------------------------------------------------------
# Media helpers — content-addressed (MD5) storage
# ---------------------------------------------------------------------------

_ALLOWED_MEDIA_EXTS = _IMAGE_EXTS | _VIDEO_EXTS | _AUDIO_EXTS


def _validate_media_source(src: Path) -> None:
    """Ensure *src* is a recognized media file, not a sensitive system file.

    Raises ``ValueError`` if the file extension is not a known media type
    or the path points to a sensitive system location.
    """
    ext = src.suffix.lower()
    if ext not in _ALLOWED_MEDIA_EXTS:
        raise ValueError(
            f"Rejected non-media file: {src.name} (extension '{ext}' is not a recognized media type)"
        )
    resolved = str(src.resolve())
    sensitive_prefixes = (
        "/etc", "/var", "/sys", "/proc", "/dev",
        "/private/etc", "/private/var",
        "/Library", "/System",
        "C:\\Windows", "C:\\Program Files",
    )
    for prefix in sensitive_prefixes:
        if resolved.startswith(prefix + "/") or resolved.startswith(prefix + "\\") or resolved == prefix:
            raise ValueError(f"Rejected file from sensitive path: {resolved}")


def _md5_of_file(path: Path) -> str:
    """Return the hex MD5 digest of a file, reading in 8 KiB chunks."""
    h = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _store_media_by_hash(src: Path) -> tuple[Path, bool]:
    """Copy *src* into ``Assets/`` using its MD5 hash as filename.

    Returns ``(dest_path, already_existed)``.  If a file with the same hash
    is already present the copy is skipped — true content-addressed dedup.

    Only recognized media files (images, videos, audio) are accepted.
    Files from sensitive system directories are rejected.
    """
    _validate_media_source(src)
    digest = _md5_of_file(src)
    dest = VAULT_ROOT / "Assets" / f"{digest}{src.suffix.lower()}"
    if dest.exists():
        return dest, True
    with _file_lock:
        if dest.exists():
            return dest, True
        tmp = dest.with_suffix(dest.suffix + ".tmp")
        shutil.copy2(src, tmp)
        tmp.replace(dest)
    return dest, False


def _media_md_tag(path_str: str) -> str:
    """Return the appropriate markdown tag for a media file based on its extension."""
    ext = Path(path_str).suffix.lower()
    name = Path(path_str).name
    if ext in _VIDEO_EXTS:
        return f"- **Media:** 🎬 [video: {name}]({path_str})"
    if ext in _AUDIO_EXTS:
        return f"- **Media:** 🎙 [audio: {name}]({path_str})"
    return f"- **Media:** ![image]({path_str})"


# ---------------------------------------------------------------------------
# Fragment dedup helpers — merge by story_node_id + sender
# ---------------------------------------------------------------------------

_FRAGMENT_HEADER_RE = re.compile(
    r"### 🧩 Fragment `(?P<fid>[^`]+)` — (?P<ts>[^\n]+)\n"
    r"- \*\*From:\*\* (?P<sender>[^\n]+)\n"
    r"- \*\*Emotion:\*\* (?P<emotion>[^\n]+)\n"
    r"- \*\*Story Node:\*\* `(?P<node>[^`]+)`",
    re.MULTILINE,
)


def _try_merge_fragment(
    target: Path,
    sender_name: str,
    story_node_id: str,
    new_emotion: str,
    new_content: str,
    new_media_line: str | None,
) -> dict[str, Any] | None:
    """If *target* already has a fragment with matching node+sender, update it.

    Returns a result dict on merge, or ``None`` to signal "no duplicate found".
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
                quote_line = f"\n> ↩ _{_now_iso()}_ — {new_content}"
                insert_at = m.end() + (frag_end_match.start() if frag_end_match else 0)
                updated_at_pos = updated.find(block_text) + len(block_text) if block_text in updated else insert_at
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
# Three-context routing helpers
# ---------------------------------------------------------------------------

def _event_filename(event_name: str, group_id: str | None = None) -> str:
    """Deterministic, collision-free filename for a temporary event.

    ``{YYYY-MM}-{event_name}.md``  or  ``{YYYY-MM}-{event_name}_g{group_id}.md``
    """
    prefix = _month_tag()
    safe_name = _sanitize_path_component(event_name)
    if group_id:
        safe_gid = _sanitize_path_component(group_id)
        return f"{prefix}-{safe_name}_g{safe_gid}.md"
    return f"{prefix}-{safe_name}.md"


def _circle_filename(group_id: str) -> str:
    """Monthly archive filename for a long-term circle.

    ``{group_name}_{YYYY-MM}.md``
    """
    safe_name = _sanitize_path_component(group_id)
    return f"{safe_name}_{_month_tag()}.md"


def _resolve_target(
    context_type: str,
    *,
    event_name: str | None = None,
    group_id: str | None = None,
) -> Path:
    """Central router: map ``(context_type, event_name, group_id)`` to a file path.

    All user-supplied names are sanitized to prevent path traversal.

    ============  ========================================================
    context_type  Target file
    ============  ========================================================
    solo          ``Solo/Projects/{event_name}.md``  if event_name given,
                  ``Solo/Daily/{YYYY-MM}.md``        otherwise.
    circle        ``Circles/{group_id}_{YYYY-MM}.md``
    event         ``Events/{YYYY-MM}-{event_name}[_g{group_id}].md``
    ============  ========================================================
    """
    if context_type == "solo":
        if event_name:
            safe = _sanitize_path_component(event_name)
            target = VAULT_ROOT / "Solo" / "Projects" / f"{safe}.md"
            return _validate_within_vault(target)
        return VAULT_ROOT / "Solo" / "Daily" / f"{_month_tag()}.md"

    if context_type == "circle":
        gid = group_id or "default_circle"
        target = VAULT_ROOT / "Circles" / _circle_filename(gid)
        return _validate_within_vault(target)

    # event (default fallback)
    ename = event_name or "unnamed"
    target = VAULT_ROOT / "Events" / _event_filename(ename, group_id)
    return _validate_within_vault(target)


# ---------------------------------------------------------------------------
# 1. record_group_fragment
# ---------------------------------------------------------------------------

_EVENT_HINT_RE = re.compile(
    r"(旅[行游]|出[发差]|到达|机场|候机|酒店|加班|开[会工]|"
    r"聚[餐会]|生日|毕业|搬家|travel|trip|flight|meeting)",
    re.IGNORECASE,
)


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
    """Record a life fragment (碎片) into the local vault.

    Three-context routing
    ---------------------
    ``context_type`` determines which physical folder receives the data:

    - **solo**   → ``Solo/Daily/{YYYY-MM}.md`` (journal) or
                    ``Solo/Projects/{event_name}.md`` (serious material).
    - **circle** → ``Circles/{group_id}_{YYYY-MM}.md`` (monthly archive).
    - **event**  → ``Events/{YYYY-MM}-{event_name}[_g{group_id}].md``.

    ``sender_id`` (optional) — unique account identifier from the IM platform.
    When provided, the display name is resolved from the local identity
    registry (auto-registering unknown contacts on first encounter).

    Anti-collision guarantees carry over from all contexts:
    node dedup, MD5 media hashing, and group namespace isolation.
    """
    _ensure_vault()

    if context_type not in CONTEXT_TYPES:
        return {"status": "error", "message": f"Unknown context_type '{context_type}'. Use: {CONTEXT_TYPES}"}

    sender_name = _resolve_display_name(sender_name, sender_id)

    ts = _now_iso()
    emotion = emotion_tag or "🫧 neutral"

    # ── Hash-based media storage ─────────────────────────────────────────
    stored_media: str | None = None
    media_reused = False
    if media_path:
        src = Path(media_path)
        if src.exists():
            try:
                dest, media_reused = _store_media_by_hash(src)
                stored_media = str(dest)
            except ValueError as e:
                return {"status": "error", "message": str(e)}
        else:
            stored_media = media_path

    media_md_line = _media_md_tag(stored_media) if stored_media else None

    # ── Three-context routing ────────────────────────────────────────────
    target = _resolve_target(context_type, event_name=event_name, group_id=group_id)

    # ── Node dedup: try merge before creating a new block ────────────────
    merge_result = _try_merge_fragment(
        target, sender_name, story_node_id, emotion, content, media_md_line,
    )
    if merge_result is not None:
        merge_result["context_type"] = context_type
        if media_reused:
            merge_result["media_reused"] = True
        return merge_result

    # ── Build the new markdown fragment ──────────────────────────────────
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

    # ── Rashomon stitching (circle & event modes) ────────────────────────
    inserted = False
    if interaction_type in ("reaction", "complement") and target.exists():
        sibling_pattern = rf"Story Node.*`{re.escape(story_node_id)}`"
        inserted = _insert_md_after_pattern(target, sibling_pattern, md_block)

    if not inserted:
        _append_md(target, md_block)

    # ── Auto-sniff potential new events (solo & circle only) ─────────────
    event_hint: str | None = None
    if context_type != "event" and not event_name and _EVENT_HINT_RE.search(content):
        event_hint = _EVENT_HINT_RE.search(content).group(0)  # type: ignore[union-attr]

    # ── Persist fragment index ───────────────────────────────────────────
    index_path = VAULT_ROOT / "Brain" / "fragment_index.json"
    index: list[dict[str, Any]] = _read_json(index_path, default=[])
    index.append(
        {
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
        }
    )
    _write_json(index_path, index)

    result: dict[str, Any] = {
        "status": "ok",
        "context_type": context_type,
        "fragment_id": frag_id,
        "written_to": str(target),
        "rashomon_stitched": inserted,
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


# ---------------------------------------------------------------------------
# 1b. manage_identity — user identity registry
# ---------------------------------------------------------------------------

_IDENTITY_FILE = "identity.json"


def _load_identity() -> dict[str, Any]:
    """Load the identity registry from the vault."""
    return _read_json(VAULT_ROOT / "Brain" / _IDENTITY_FILE, default={"owner": None, "contacts": {}})


def _save_identity(data: dict[str, Any]) -> None:
    _write_json(VAULT_ROOT / "Brain" / _IDENTITY_FILE, data)


def _resolve_display_name(
    sender_name: str,
    sender_id: str | None = None,
) -> str:
    """Return the best display name for a sender.

    Priority: bound display_name (by sender_id) > sender_name argument.
    If sender_id is provided and not yet registered, auto-register with
    the given sender_name as the initial display_name.
    """
    if not sender_id:
        return sender_name

    identity = _load_identity()
    contacts = identity.setdefault("contacts", {})

    if sender_id in contacts:
        return contacts[sender_id]["display_name"]

    # Check if this sender_id matches the owner
    owner = identity.get("owner")
    if owner and owner.get("account_id") == sender_id:
        return owner["display_name"]

    # Auto-register new contact
    contacts[sender_id] = {
        "original_name": sender_name,
        "display_name": sender_name,
        "set_at": _now_iso(),
    }
    _save_identity(identity)
    return sender_name


def manage_identity(
    action: str,
    *,
    display_name: str | None = None,
    account_id: str | None = None,
    original_name: str | None = None,
) -> dict[str, Any]:
    """Manage the local identity registry (owner profile & contacts).

    Actions
    -------
    init_owner
        Set up the vault owner's profile. Called once during the first solo
        conversation when Lumi asks "How should I call you?".
        Requires ``display_name``; ``account_id`` is optional (auto-generated
        if omitted).

    get_owner
        Return the current owner profile, or indicate that no owner has been
        set yet (triggers the greeting protocol).

    rename
        Change the display name for a contact (by ``account_id``) or the
        owner (if ``account_id`` matches the owner or is omitted).
        Requires ``display_name``.

    lookup
        Look up a contact by ``account_id``. Returns the display name and
        original name.

    list_contacts
        Return all known contacts.
    """
    _ensure_vault()
    identity = _load_identity()

    # ── INIT_OWNER ────────────────────────────────────────────────────
    if action == "init_owner":
        if not display_name:
            return {"status": "error", "message": "display_name is required to set up the owner."}
        if identity.get("owner"):
            return {
                "status": "already_set",
                "message": f"Owner is already '{identity['owner']['display_name']}'. Use 'rename' to change.",
                "owner": identity["owner"],
            }
        owner_id = account_id or f"owner_{uuid.uuid4().hex[:8]}"
        identity["owner"] = {
            "account_id": owner_id,
            "display_name": display_name,
            "set_at": _now_iso(),
        }
        _save_identity(identity)
        return {"status": "ok", "action": "owner_initialized", "owner": identity["owner"]}

    # ── GET_OWNER ─────────────────────────────────────────────────────
    if action == "get_owner":
        owner = identity.get("owner")
        if not owner:
            return {"status": "no_owner", "message": "No owner set yet. Please ask the user for their name."}
        return {"status": "ok", "action": "get_owner", "owner": owner}

    # ── RENAME ────────────────────────────────────────────────────────
    if action == "rename":
        if not display_name:
            return {"status": "error", "message": "display_name is required for rename."}
        owner = identity.get("owner")
        contacts = identity.setdefault("contacts", {})

        if not account_id or (owner and owner.get("account_id") == account_id):
            if not owner:
                return {"status": "error", "message": "No owner to rename. Use 'init_owner' first."}
            old_name = owner["display_name"]
            owner["display_name"] = display_name
            owner["set_at"] = _now_iso()
            _save_identity(identity)
            return {
                "status": "ok", "action": "owner_renamed",
                "old_name": old_name, "new_name": display_name,
            }

        if account_id in contacts:
            old_name = contacts[account_id]["display_name"]
            contacts[account_id]["display_name"] = display_name
            contacts[account_id]["set_at"] = _now_iso()
            _save_identity(identity)
            return {
                "status": "ok", "action": "contact_renamed",
                "account_id": account_id,
                "old_name": old_name, "new_name": display_name,
            }

        # Register new contact with the requested name
        contacts[account_id] = {
            "original_name": original_name or display_name,
            "display_name": display_name,
            "set_at": _now_iso(),
        }
        _save_identity(identity)
        return {
            "status": "ok", "action": "contact_registered",
            "account_id": account_id, "display_name": display_name,
        }

    # ── LOOKUP ────────────────────────────────────────────────────────
    if action == "lookup":
        if not account_id:
            return {"status": "error", "message": "account_id is required for lookup."}
        owner = identity.get("owner")
        if owner and owner.get("account_id") == account_id:
            return {"status": "ok", "action": "lookup", "type": "owner", "profile": owner}
        contacts = identity.get("contacts", {})
        if account_id in contacts:
            return {"status": "ok", "action": "lookup", "type": "contact", "profile": contacts[account_id]}
        return {"status": "not_found", "message": f"No identity found for '{account_id}'."}

    # ── LIST_CONTACTS ─────────────────────────────────────────────────
    if action == "list_contacts":
        contacts = identity.get("contacts", {})
        return {
            "status": "ok", "action": "list_contacts",
            "owner": identity.get("owner"),
            "total_contacts": len(contacts),
            "contacts": contacts,
        }

    return {"status": "error", "message": f"Unknown action '{action}'. Use: init_owner, get_owner, rename, lookup, list_contacts."}


# ---------------------------------------------------------------------------
# 2. manage_event
# ---------------------------------------------------------------------------

_EVENTS_REGISTRY = "events_registry.json"


def manage_event(
    action: str,
    event_name: str,
    *,
    group_id: str | None = None,
) -> dict[str, Any]:
    """Start, stop, or query a long-running story event.

    When *group_id* is supplied the event file is namespaced with a
    ``_g{group_id}`` suffix so that identically-named events from different
    groups never collide.

    Actions
    -------
    start  — create a new event markdown file and register it.
    stop   — mark the event as finished (adds a closing section).
    query  — return metadata and fragment count for the event.
    """
    _ensure_vault()

    if action not in ("start", "stop", "query"):
        return {"status": "error", "message": f"Unknown action '{action}'. Use start / stop / query."}

    registry_path = VAULT_ROOT / "Events" / _EVENTS_REGISTRY
    registry: dict[str, Any] = _read_json(registry_path, default={})

    fname = _event_filename(event_name, group_id)
    registry_key = fname.removesuffix(".md")
    event_file = VAULT_ROOT / "Events" / fname

    # ── START ────────────────────────────────────────────────────────────
    if action == "start":
        if registry_key in registry and registry[registry_key].get("active"):
            return {"status": "noop", "message": f"Event '{event_name}' is already active."}

        registry[registry_key] = {
            "event_name": event_name,
            "group_id": group_id,
            "started_at": _now_iso(),
            "ended_at": None,
            "active": True,
        }
        _write_json(registry_path, registry)

        group_line = f"  \n> Group: `{group_id}`\n" if group_id else ""
        header = (
            f"# 🚩 {event_name}\n\n"
            f"> Created by Lumi on {_now_iso()}\n"
            f"{group_line}\n---\n"
        )
        with _file_lock:
            event_file.write_text(header, encoding="utf-8")

        return {
            "status": "ok",
            "action": "started",
            "event": event_name,
            "registry_key": registry_key,
            "file": str(event_file),
        }

    # ── STOP ─────────────────────────────────────────────────────────────
    if action == "stop":
        if registry_key not in registry or not registry[registry_key].get("active"):
            return {"status": "error", "message": f"Event '{event_name}' is not currently active."}

        registry[registry_key]["ended_at"] = _now_iso()
        registry[registry_key]["active"] = False
        _write_json(registry_path, registry)

        closing = (
            f"\n---\n\n## 🔒 Scroll Sealed\n\n"
            f"> '{event_name}' was sealed by Lumi on {_now_iso()}.\n"
            f"> Precious memories safely locked in the vault ✨\n"
        )
        _append_md(event_file, closing)

        return {"status": "ok", "action": "stopped", "event": event_name, "registry_key": registry_key}

    # ── QUERY ────────────────────────────────────────────────────────────
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


# ---------------------------------------------------------------------------
# 3. update_circle_dictionary
# ---------------------------------------------------------------------------

_CIRCLE_DICT_FILE = "Circle_Dictionary.json"


def update_circle_dictionary(
    target_user: str,
    traits: list[str],
) -> dict[str, Any]:
    """Append newly-discovered traits, slang, or taboos to the circle dictionary.

    If *target_user* is ``"group_vibe"`` the traits describe the overall group
    atmosphere; otherwise they are tied to a specific person.
    """
    _ensure_vault()

    dict_path = VAULT_ROOT / "Brain" / _CIRCLE_DICT_FILE
    dictionary: dict[str, Any] = _read_json(dict_path, default={})

    entry = dictionary.setdefault(target_user, {
        "first_seen": _now_iso(),
        "traits": [],
    })

    existing: set[str] = set(entry["traits"])
    new_traits = [t for t in traits if t not in existing]
    entry["traits"].extend(new_traits)
    entry["last_updated"] = _now_iso()

    _write_json(dict_path, dictionary)

    # Also maintain a human-readable markdown mirror
    _sync_circle_md(dictionary)

    return {
        "status": "ok",
        "target_user": target_user,
        "added_traits": new_traits,
        "total_traits": len(entry["traits"]),
    }


def _sync_circle_md(dictionary: dict[str, Any]) -> None:
    """Render the circle dictionary into a readable markdown file."""
    md_path = VAULT_ROOT / "Brain" / "Circle_Dictionary.md"
    lines = ["# 🧠 Circle Dictionary\n\n"]
    for user, info in dictionary.items():
        emoji = "🌐" if user == "group_vibe" else "👤"
        lines.append(f"## {emoji} {user}\n\n")
        for trait in info.get("traits", []):
            lines.append(f"- {trait}\n")
        lines.append(f"\n_Last updated: {info.get('last_updated', 'N/A')}_\n\n---\n\n")

    with _file_lock:
        md_path.write_text("".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# 4. save_meme
# ---------------------------------------------------------------------------

_MEME_VAULT_FILE = "Meme_Vault.json"


def save_meme(
    meme_title: str,
    context_tags: list[str],
    *,
    media_path: str | None = None,
) -> dict[str, Any]:
    """Archive a legendary moment into the meme vault for future lethal recalls.

    Media files are stored content-addressed (MD5 hash filename) so that
    identical images are never duplicated on disk.
    """
    _ensure_vault()

    vault_path = VAULT_ROOT / "Brain" / _MEME_VAULT_FILE
    vault: list[dict[str, Any]] = _read_json(vault_path, default=[])

    meme_id = str(uuid.uuid4())[:8]
    entry: dict[str, Any] = {
        "id": meme_id,
        "title": meme_title,
        "context_tags": context_tags,
        "saved_at": _now_iso(),
        "recall_count": 0,
    }

    media_reused = False
    if media_path:
        src = Path(media_path)
        if src.exists():
            try:
                dest, media_reused = _store_media_by_hash(src)
                entry["media"] = str(dest)
            except ValueError as e:
                return {"status": "error", "message": str(e)}
        else:
            entry["media"] = media_path
            entry["media_note"] = "original file not found at save time"

    vault.append(entry)
    _write_json(vault_path, vault)

    result: dict[str, Any] = {
        "status": "ok",
        "meme_id": meme_id,
        "title": meme_title,
        "tags": context_tags,
        "stored_in": str(vault_path),
    }
    if media_reused:
        result["media_reused"] = True
    return result


# ---------------------------------------------------------------------------
# 5. render_lumi_canvas
# ---------------------------------------------------------------------------

_EMOTION_PALETTE: dict[str, str] = {
    # positive / warm
    "happy":        "#FFD93D",
    "excited":      "#FFCB77",
    "joy":          "#FFE066",
    "proud":        "#F7B731",
    "love":         "#FF6B81",
    "grateful":     "#F8A5C2",
    "hopeful":      "#A3D9A5",
    "relieved":     "#A8D8EA",
    "inspired":     "#C9B1FF",
    "amused":       "#FEE440",
    "determined":   "#FF9F43",
    "confident":    "#FFA502",
    # calm / reflective
    "calm":         "#B8E6CF",
    "peaceful":     "#D4F1F4",
    "nostalgic":    "#DDA0DD",
    "reflective":   "#B0C4DE",
    "contemplative":"#B0C4DE",
    "neutral":      "#E2E2E2",
    "noted":        "#D5DBDB",
    "analytical":   "#85C1E9",
    # negative / cool
    "sad":          "#8093F1",
    "melancholy":   "#7B68EE",
    "lonely":       "#9B9BCC",
    "tired":        "#A0A0B8",
    "exhausted":    "#8E8EA0",
    "anxious":      "#E8A87C",
    "nervous":      "#DDA0DD",
    "frustrated":   "#E57373",
    "angry":        "#FF6B6B",
    "annoyed":      "#FF8A80",
    "jealous":      "#81C784",
    # intense / dramatic
    "shocked":      "#FF4757",
    "terrified":    "#D63031",
    "traumatized":  "#C0392B",
    "embarrassed":  "#FF9FF3",
    "cringe":       "#FD79A8",
    "chaotic":      "#A29BFE",
    "sarcastic":    "#778BEB",
    "savage":       "#E056A0",
    # awe / wonder
    "breathtaking": "#54A0FF",
    "amazed":       "#48DBFB",
    "mindblown":    "#0ABDE3",
    "beautiful":    "#55EFC4",
    "aesthetic":    "#81ECEC",
    # food / niche
    "hungry":       "#FF6348",
    "thrifty":      "#BADC58",
    "cozy":         "#FDCB6E",
    "adventurous":  "#F39C12",
    "overconfident":"#E17055",
}


def _parse_fragments_from_md(path: Path) -> list[dict[str, Any]]:
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

        emotion_raw = m.group("emotion").split("→")[-1].strip()
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
    """Minimal HTML escaping."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _generate_html_canvas(payload: dict[str, Any], locale: str = "en") -> Path:
    """Render a self-contained HTML memory scroll and save it to the vault.

    The HTML structure lives in ``assets/canvas_template.html``; this function
    pre-computes all dynamic values and fills the template with ``.format()``.
    """
    title = _html_escape(payload["canvas_title"])
    vibe = payload.get("vibe", "warm default")
    lang = locale if locale in SUPPORTED_LOCALES else "en"
    theme = _DEFAULT_THEME.copy()
    for key, val in _VIBE_THEMES.items():
        if key in vibe.lower():
            theme = val
            break
    is_dark = _luminance_from_hex(theme["bg"]) < 0.4

    cards = payload.get("rashomon_cards", [])
    memes = payload.get("memes", [])

    # Build timeline + card HTML
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

    # Meme gallery
    meme_html = ""
    if memes:
        meme_items = []
        for m in memes:
            tags = ", ".join(m.get("context_tags", []))
            meme_media = ""
            if m.get("media"):
                meme_media = _render_media_embed(m["media"])
            meme_items.append(
                f'<div class="meme-item">'
                f'<div class="meme-info">'
                f'<span class="meme-icon">🃏</span>'
                f'<strong>{_html_escape(m["title"])}</strong>'
                f'<span class="meme-tags">{_html_escape(tags)}</span>'
                f'</div>'
                f'{meme_media}'
                f'</div>'
            )
        meme_html = (
            '<section class="meme-gallery">'
            f'<h2>{_t("meme_gallery_title", lang)}</h2>'
            + "\n".join(meme_items)
            + '</section>'
        )

    # Stats bar
    stats = (
        f'<div class="stats">'
        f'<span>📝 {payload["total_fragments"]} {_t("stat_fragments", lang)}</span>'
        f'<span>🧩 {payload["total_nodes"]} {_t("stat_story_nodes", lang)}</span>'
        f'<span>🎨 {_html_escape(vibe)}</span>'
        f'</div>'
    )

    # Load template from assets/ and fill in all dynamic values
    tpl_path = _ASSETS_DIR / "canvas_template.html"
    tpl = tpl_path.read_text(encoding="utf-8")

    html = tpl.format(
        html_lang="zh-CN" if lang == "zh" else "en",
        title=title,
        title_suffix=_t("title_suffix", lang),
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
        meme_html=meme_html,
        scroll_subtitle=_t("scroll_subtitle", lang),
        cta_heading=_t("cta_heading", lang),
        cta_body=_t("cta_body", lang),
        cta_badge=_t("cta_badge", lang),
        footer_rendered_by=_t("footer_rendered_by", lang),
        footer_rendered_suffix=_t("footer_rendered_suffix", lang),
        render_date=_now_iso()[:10],
    )

    safe_title = _sanitize_path_component(payload["canvas_title"])
    html_file = VAULT_ROOT / "Brain" / f"canvas_{safe_title}.html"
    _validate_within_vault(html_file)
    html_file.parent.mkdir(parents=True, exist_ok=True)
    with _file_lock:
        html_file.write_text(html, encoding="utf-8")
    return html_file


def _luminance_from_hex(h: str) -> float:
    """Rough perceived luminance from a hex color string."""
    h = h.lstrip("#")
    if len(h) != 6:
        return 0.9
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def _sender_color(name: str) -> str:
    """Deterministic color for a sender based on their name hash."""
    hue = hash(name) % 360
    return f"hsl({hue}, 55%, 50%)"


def _render_media_embed(media_path: str) -> str:
    """Return an HTML embed tag for a media file (img/video/audio).

    Paths stored in the index are relative to the project root (e.g.
    ``Lumi_Vault/Assets/abc123.jpg``).  HTML files live in
    ``Lumi_Vault/Brain/``, so we compute a ``../`` relative path.

    Only vault-internal paths are embedded; external or absolute paths
    are rendered as safe text labels to prevent local file disclosure.
    """
    if media_path.startswith(("file://", "http://", "https://", "/")):
        return f'<div class="card-media">📎 {_html_escape(Path(media_path).name)}</div>'

    p = Path(media_path)
    ext = p.suffix.lower()

    if str(VAULT_ROOT) in media_path:
        try:
            _validate_within_vault(p)
        except ValueError:
            return f'<div class="card-media">📎 {_html_escape(p.name)}</div>'
        rel = Path("..") / p.relative_to(VAULT_ROOT)
    else:
        if ".." in str(p):
            return f'<div class="card-media">📎 {_html_escape(p.name)}</div>'
        rel = p

    escaped = _html_escape(str(rel))
    name = _html_escape(p.name)

    if ext in _IMAGE_EXTS:
        return (
            f'<div class="card-media">'
            f'<img src="{escaped}" alt="{name}" loading="lazy">'
            f'</div>'
        )
    if ext in _VIDEO_EXTS:
        return (
            f'<div class="card-media">'
            f'<video src="{escaped}" controls preload="metadata"></video>'
            f'<span class="media-label">🎬 {name}</span>'
            f'</div>'
        )
    if ext in _AUDIO_EXTS:
        return (
            f'<div class="card-media">'
            f'<audio src="{escaped}" controls preload="metadata"></audio>'
            f'<span class="media-label">🎙 {name}</span>'
            f'</div>'
        )
    return f'<div class="card-media">📎 <a href="{escaped}">{name}</a></div>'


def _render_single_card(frag: dict[str, Any], side: str, idx: int) -> str:
    """Render a single-perspective timeline card."""
    sender = _html_escape(frag["sender"])
    initial = sender[0].upper()
    ts_short = frag["timestamp"][5:16].replace("T", " ")
    emotion = _html_escape(frag["emotion"])
    color = frag["emotion_color"]
    avatar_bg = _sender_color(frag["sender"])

    quotes_html = ""
    for q in frag.get("quotes", []):
        quotes_html += f"<blockquote>{_html_escape(q)}</blockquote>"

    media_html = _render_media_embed(frag["media"]) if frag.get("media") else ""

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
    """Render a Rashomon flip card with front/back perspectives."""
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
        media = _render_media_embed(f["media"]) if f.get("media") else ""
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
    extra_note = _t("rashomon_extra", locale, n=extra_count) if extra_count > 0 else ""
    flip_label = _t("rashomon_label", locale, n=len(frags), extra=extra_note)
    flip_hint = _t("flip_hint", locale)

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


def render_lumi_canvas(
    target_event: str,
    *,
    context_type: str = "event",
    vibe_override: str | None = None,
    group_id: str | None = None,
    locale: str = "en",
) -> dict[str, Any]:
    """Read vault data and return a structured payload for Live Canvas rendering.

    Supports all three context types:

    - ``context_type="solo"``   + ``target_event="this_month"`` → Solo/Daily
    - ``context_type="solo"``   + ``target_event="{project}"``  → Solo/Projects
    - ``context_type="circle"`` + ``group_id``                  → Circles
    - ``context_type="event"``  + ``target_event``              → Events

    ``locale`` controls UI language: ``"en"`` (default) or ``"zh"``.
    """
    _ensure_vault()
    lang = locale if locale in SUPPORTED_LOCALES else "en"

    # ── Resolve source file via the central router ───────────────────────
    solo_prefix = _t("canvas_prefix_solo", lang)
    circle_prefix = _t("canvas_prefix_circle", lang)
    today_prefix = _t("canvas_prefix_today", lang)

    if target_event == "this_month" and context_type == "solo":
        source = _resolve_target("solo")
        canvas_title = f"{solo_prefix} — {_month_tag()}"
    elif context_type == "circle":
        source = _resolve_target("circle", group_id=group_id)
        canvas_title = f"{circle_prefix} — {group_id or 'default'} ({_month_tag()})"
    else:
        event_name = None if target_event == "today" else target_event
        if target_event == "today":
            source = _resolve_target("solo")
            canvas_title = f"{today_prefix} — {_today_tag()}"
        else:
            source = _resolve_target(context_type, event_name=event_name, group_id=group_id)
            canvas_title = target_event

    if not source.exists():
        return {"status": "error", "message": _t("no_data_found", lang, target=target_event)}

    # ── Parse fragments ──────────────────────────────────────────────────
    fragments = _parse_fragments_from_md(source)
    if not fragments:
        return {"status": "empty", "message": _t("no_fragments_yet", lang, target=target_event)}

    # ── Group by story_node_id for Rashomon card pairs ───────────────────
    node_groups: dict[str, list[dict[str, Any]]] = {}
    for frag in fragments:
        node_groups.setdefault(frag["story_node_id"], []).append(frag)

    rashomon_cards: list[dict[str, Any]] = []
    for node_id, group in node_groups.items():
        rashomon_cards.append({
            "story_node_id": node_id,
            "perspectives": len(group),
            "is_multi_perspective": len(group) > 1,
            "fragments": group,
        })

    # ── Collect meme references ──────────────────────────────────────────
    meme_vault: list[dict[str, Any]] = _read_json(
        VAULT_ROOT / "Brain" / _MEME_VAULT_FILE, default=[]
    )
    search_tags = {target_event.lower()}
    if group_id:
        search_tags.add(group_id.lower())
    relevant_memes = [
        m for m in meme_vault
        if search_tags & {t.lower() for t in m.get("context_tags", [])}
    ]

    # ── Determine vibe / theme ───────────────────────────────────────────
    circle_dict: dict[str, Any] = _read_json(
        VAULT_ROOT / "Brain" / _CIRCLE_DICT_FILE, default={}
    )
    group_vibe_traits = circle_dict.get("group_vibe", {}).get("traits", [])

    vibe = vibe_override or ("warm default" if not group_vibe_traits else group_vibe_traits[0])

    payload: dict[str, Any] = {
        "status": "ok",
        "context_type": context_type,
        "canvas_title": canvas_title,
        "source_file": str(source),
        "vibe": vibe,
        "total_fragments": len(fragments),
        "total_nodes": len(rashomon_cards),
        "rashomon_cards": rashomon_cards,
        "memes": relevant_memes,
        "timeline": [
            {"ts": f["timestamp"], "sender": f["sender"], "emotion_color": f["emotion_color"]}
            for f in fragments
        ],
    }

    # ── Generate self-contained HTML scroll ───────────────────────────
    html_path = _generate_html_canvas(payload, locale=lang)
    payload["html_file"] = str(html_path)

    return payload


# ---------------------------------------------------------------------------
# 6. manage_fragment — conversational CRUD
# ---------------------------------------------------------------------------

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
    """Full CRUD on fragments, enabling conversational queries and edits.

    Actions
    -------
    search  — return matching fragments from the index (filter by any combo
              of sender / keyword / context_type / group_id / event_name /
              story_node_id / date range).
    get     — return the full detail for a single fragment by ``fragment_id``.
    update  — modify ``content`` and/or ``emotion`` of an existing fragment
              (both in the markdown file and the index).
    delete  — remove a fragment from both the markdown file and the index.
    """
    _ensure_vault()

    if action not in ("search", "get", "update", "delete"):
        return {"status": "error", "message": f"Unknown action '{action}'. Use search / get / update / delete."}

    index_path = VAULT_ROOT / "Brain" / "fragment_index.json"
    index: list[dict[str, Any]] = _read_json(index_path, default=[])

    # ── SEARCH ───────────────────────────────────────────────────────────
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

        return {
            "status": "ok",
            "action": "search",
            "total": total,
            "returned": len(results),
            "fragments": results,
        }

    # ── GET ───────────────────────────────────────────────────────────────
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
            match = re.search(
                rf"### 🧩 Fragment `{re.escape(fragment_id)}`.*?\n---\n",
                text, re.DOTALL,
            )
            if match:
                md_block = match.group(0)

        return {
            "status": "ok",
            "action": "get",
            "index_entry": entry,
            "markdown": md_block,
        }

    # ── UPDATE ────────────────────────────────────────────────────────────
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
                        updated_block = updated_block.replace(
                            old_emo.group(0),
                            f"- **Emotion:** {new_emotion}\n", 1,
                        )
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
                            + f"\n> ✏ _{_now_iso()}_ — {new_content}"
                            + updated_block[insert_after:]
                        )
                    else:
                        updated_block = updated_block.rstrip() + f"\n> ✏ _{_now_iso()}_ — {new_content}\n"
                    changes.append("content")

                text = text[:match.start()] + updated_block + match.group(2) + text[match.end():]
                with _file_lock:
                    md_file.write_text(text, encoding="utf-8")

        index[entry_idx] = entry
        _write_json(index_path, index)

        return {
            "status": "ok",
            "action": "updated",
            "fragment_id": fragment_id,
            "changes": changes,
            "file": str(md_file),
        }

    # ── DELETE ────────────────────────────────────────────────────────────
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

    _write_json(index_path, index)

    return {
        "status": "ok",
        "action": "deleted",
        "fragment_id": fragment_id,
        "file": str(md_file),
    }


# ---------------------------------------------------------------------------
# 7. export_lumi_scroll — share pipeline
# ---------------------------------------------------------------------------

_LUMI_VERSION = "0.1.5"


def _embed_media_base64(media_path: str | None) -> dict[str, Any] | None:
    """Read a media file and return a dict with base64-encoded data.

    Only files residing within the vault are embedded; external paths are
    silently skipped to prevent arbitrary file exfiltration.
    """
    if not media_path:
        return None
    p = Path(media_path)
    if not p.exists():
        return None
    try:
        _validate_within_vault(p)
    except ValueError:
        return None
    mime, _ = mimetypes.guess_type(str(p))
    if not mime:
        ext = p.suffix.lower()
        if ext in _IMAGE_EXTS:
            mime = f"image/{ext.lstrip('.')}"
        elif ext in _VIDEO_EXTS:
            mime = f"video/{ext.lstrip('.')}"
        elif ext in _AUDIO_EXTS:
            mime = f"audio/{ext.lstrip('.')}"
        else:
            mime = "application/octet-stream"
    data = p.read_bytes()
    return {
        "filename": p.name,
        "mime": mime,
        "size_bytes": len(data),
        "data": base64.b64encode(data).decode("ascii"),
    }


def _generate_lumi_seed(payload: dict[str, Any]) -> Path:
    """Package the canvas payload into a self-contained .lumi seed file."""
    cards = payload.get("rashomon_cards", [])
    fragments_out: list[dict[str, Any]] = []
    for card in cards:
        for frag in card["fragments"]:
            entry = {**frag}
            entry["media_embedded"] = _embed_media_base64(frag.get("media"))
            fragments_out.append(entry)

    memes_out: list[dict[str, Any]] = []
    for m in payload.get("memes", []):
        meme_entry = {**m}
        meme_entry["media_embedded"] = _embed_media_base64(m.get("media"))
        memes_out.append(meme_entry)

    seed: dict[str, Any] = {
        "lumi_version": _LUMI_VERSION,
        "exported_at": _now_iso(),
        "canvas_title": payload.get("canvas_title", "Untitled"),
        "context_type": payload.get("context_type", "event"),
        "vibe": payload.get("vibe", "warm default"),
        "total_fragments": payload.get("total_fragments", 0),
        "total_nodes": payload.get("total_nodes", 0),
        "fragments": fragments_out,
        "rashomon_cards": [
            {
                "story_node_id": c["story_node_id"],
                "perspectives": c["perspectives"],
                "is_multi_perspective": c["is_multi_perspective"],
            }
            for c in cards
        ],
        "memes": memes_out,
        "timeline": payload.get("timeline", []),
    }

    safe_title = _sanitize_path_component(payload["canvas_title"])
    seed_path = VAULT_ROOT / "Brain" / "exports" / f"{safe_title}.lumi"
    _validate_within_vault(seed_path)
    seed_path.parent.mkdir(parents=True, exist_ok=True)
    with _file_lock:
        tmp = seed_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(seed, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(seed_path)
    return seed_path


def _screenshot_html(html_path: Path, png_path: Path) -> str | None:
    """Use Playwright to screenshot the HTML scroll into a vertical long PNG.

    Returns the path string on success, or ``None`` if Playwright is unavailable.

    The browser context is sandboxed: JavaScript is disabled and navigation
    is restricted to ``file://`` URLs within the vault directory to prevent
    generated HTML from leaking local files or making network requests.
    """
    try:
        from playwright.sync_api import sync_playwright  # type: ignore[import-untyped]
    except ImportError:
        return None

    try:
        _validate_within_vault(html_path)
    except ValueError:
        return None

    try:
        png_path.parent.mkdir(parents=True, exist_ok=True)
        vault_prefix = f"file://{VAULT_ROOT.resolve()}"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 800, "height": 600},
                java_script_enabled=False,
            )
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


def export_lumi_scroll(
    target_event: str,
    *,
    context_type: str = "event",
    vibe_override: str | None = None,
    group_id: str | None = None,
    locale: str = "en",
) -> dict[str, Any]:
    """Export a memory scroll for social sharing.

    Produces three artifacts:

    1. **HTML scroll** — interactive page (from ``render_lumi_canvas``).
    2. **.lumi seed file** — self-contained JSON with base64-embedded media,
       importable on any device running Lumi.
    3. **Long PNG image** — vertical screenshot via Playwright headless browser,
       ready to drop into any IM chat.

    If Playwright is not installed the function still succeeds; the screenshot
    field will be ``None`` with an explanatory note.

    ``locale`` controls UI language: ``"en"`` (default) or ``"zh"``.
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

    # ── .lumi seed ────────────────────────────────────────────────────
    seed_path = _generate_lumi_seed(canvas_result)

    # ── Playwright screenshot ─────────────────────────────────────────
    html_path = Path(canvas_result["html_file"])
    safe_title = _sanitize_path_component(canvas_result["canvas_title"])
    png_path = VAULT_ROOT / "Brain" / "exports" / f"{safe_title}.png"
    _validate_within_vault(png_path)

    screenshot = _screenshot_html(html_path, png_path)

    result: dict[str, Any] = {
        "status": "ok",
        "canvas_title": canvas_result["canvas_title"],
        "context_type": canvas_result["context_type"],
        "html_file": canvas_result["html_file"],
        "lumi_seed": str(seed_path),
        "screenshot": screenshot,
    }

    if screenshot is None:
        result["screenshot_note"] = (
            "Install Playwright for PNG export: "
            "pip install playwright && playwright install chromium"
        )

    return result
