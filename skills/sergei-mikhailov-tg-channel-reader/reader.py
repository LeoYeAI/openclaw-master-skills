#!/usr/bin/env python3
"""
tg-channel-reader — Telegram channel reader skill for OpenClaw
Reads posts from public/private Telegram channels via MTProto (Pyrogram)
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    from pyrogram import Client
    from pyrogram.errors import (
        FloodWait,
        ChannelInvalid,
        ChannelPrivate,
        ChannelBanned,
        ChatForbidden,
        ChatInvalid,
        ChatRestricted,
        PeerIdInvalid,
        UsernameNotOccupied,
        UserBannedInChannel,
        InviteHashExpired,
        InviteHashInvalid,
    )
except ImportError:
    print(json.dumps({"error": "pyrogram not installed. Run: pip install pyrogram tgcrypto"}))
    sys.exit(1)


def _channel_error(channel: str, error_type: str, message: str, action: str) -> dict:
    """Build a structured channel error dict for the agent."""
    return {
        "error": message,
        "error_type": error_type,
        "channel": channel,
        "action": action,
    }


# Use Pyrogram's default device identity (Python MTProto client).
# Spoofing a mobile client causes Telegram to terminate sessions — the
# behaviour doesn't match and it's detected server-side.
_DEVICE: dict = {}


# ── Session helpers ──────────────────────────────────────────────────────────

_SESSION_NAMES = [
    ".tg-reader-session.session",
    ".telethon-reader.session",
    "tg-reader-session.session",
    "telethon-reader.session",
]


def _find_session_files() -> list:
    """Find tg-reader session files in home directory and current working directory.

    Only looks for known tg-reader session names — does not scan for
    arbitrary *.session files to avoid exposing unrelated session paths.
    """
    found = []
    seen: set = set()
    dirs_checked: set = set()
    for d in [Path.home(), Path.cwd()]:
        d = d.resolve()
        if d in dirs_checked:
            continue
        dirs_checked.add(d)
        for name in _SESSION_NAMES:
            f = d / name
            if f.exists():
                resolved = f.resolve()
                if resolved in seen:
                    continue
                seen.add(resolved)
                found.append(f)
    found.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return found


def _validate_session(session_name: str) -> None:
    """Verify the session file exists; exit with a JSON error and hints if not.

    Both Pyrogram and Telethon store sessions as ``{name}.session``.
    This check prevents a silent re-auth prompt when the file is missing.
    """
    session_file = Path(f"{session_name}.session")
    if session_file.exists():
        return

    found = _find_session_files()
    error: dict = {
        "error": f"Session file not found: {session_file}",
        "expected_path": str(session_file),
        "fix": [
            "Run 'tg-reader auth' to create a new session",
            "Or set TG_SESSION=/path/to/existing-session (without .session suffix)",
            "Or add {\"session\": \"/path/to/session\"} to ~/.tg-reader.json",
            "Or pass --session-file /path/to/session (without .session suffix)",
        ],
    }
    if found:
        error["found_sessions"] = [str(f) for f in found[:10]]
        suggestion = str(found[0]).removesuffix(".session")
        error["suggestion"] = f"Likely fix: use --session-file {suggestion}"

    print(json.dumps(error, indent=2))
    sys.exit(1)


# ── Config ──────────────────────────────────────────────────────────────────

def get_config(config_file=None, session_file=None):
    """Load credentials from env or config file (env takes priority).

    Args:
        config_file: Explicit path to config JSON (overrides ~/.tg-reader.json)
        session_file: Explicit path to session file (overrides default and config value)
    """
    api_id = os.environ.get("TG_API_ID")
    api_hash = os.environ.get("TG_API_HASH")
    session_name = os.environ.get("TG_SESSION", str(Path.home() / ".tg-reader-session"))

    if not api_id or not api_hash:
        config_path = Path(config_file) if config_file else Path.home() / ".tg-reader.json"
        if config_path.exists():
            with open(config_path) as f:
                cfg = json.load(f)
                api_id = api_id or cfg.get("api_id")
                api_hash = api_hash or cfg.get("api_hash")
                session_name = cfg.get("session", session_name)

    # Explicit --session-file overrides everything
    if session_file:
        session_name = session_file

    if not api_id or not api_hash:
        print(json.dumps({
            "error": "Missing credentials. Set TG_API_ID and TG_API_HASH env vars, "
                     "or create ~/.tg-reader.json with {\"api_id\": ..., \"api_hash\": \"...\"}. "
                     "For isolated agents, pass --config-file /path/to/tg-reader.json"
        }))
        sys.exit(1)

    # Normalize: strip .session suffix if user passed full filename
    if session_name.endswith(".session"):
        session_name = session_name[: -len(".session")]

    return int(api_id), api_hash, session_name


# ── Core ─────────────────────────────────────────────────────────────────────

def parse_since(since: str) -> datetime:
    """Parse --since flag: '24h', '7d', '2026-02-01', etc."""
    since = since.strip()
    now = datetime.now(timezone.utc)
    if since.endswith("h"):
        return now - timedelta(hours=int(since[:-1]))
    if since.endswith("d"):
        return now - timedelta(days=int(since[:-1]))
    if since.endswith("w"):
        return now - timedelta(weeks=int(since[:-1]))
    # Try ISO date
    try:
        dt = datetime.fromisoformat(since)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        raise ValueError(f"Cannot parse --since value: {since!r}. Use '24h', '7d', or 'YYYY-MM-DD'.")


async def _check_discussion_group(app, channel: str) -> bool:
    """Check whether the channel has a linked discussion group (comments)."""
    try:
        chat = await app.get_chat(channel)
        return chat.linked_chat is not None
    except Exception:
        return False


async def _fetch_comments(app, channel: str, message_id: int, comment_limit: int) -> list:
    """Fetch discussion replies (comments) for a single channel post.

    Returns a list of comment dicts. Skips media-only comments (no text).
    Re-raises FloodWait so the caller can handle retries.
    """
    comments = []
    try:
        async for reply in app.get_discussion_replies(channel, message_id, limit=comment_limit):
            text = ""
            if reply.text:
                text = reply.text
            elif reply.caption:
                text = reply.caption
            if not text:
                continue
            from_user = None
            if reply.from_user:
                from_user = reply.from_user.username or str(reply.from_user.id)
            reply_date = reply.date if reply.date.tzinfo else reply.date.replace(tzinfo=timezone.utc)
            comments.append({
                "id": reply.id,
                "date": reply_date.isoformat(),
                "text": text,
                "from_user": from_user,
            })
    except FloodWait:
        raise  # let caller handle retry
    except Exception:
        pass  # comments unavailable for this post
    return comments


async def _fetch_channel(app, channel: str, since: datetime, limit: int, text_only: bool,
                         comments: bool = False, comment_limit: int = 10, comment_delay: float = 3,
                         min_id: int = 0):
    """Fetch messages from a single channel using an existing Client session."""
    # Check discussion group availability once (only when comments requested)
    has_discussion = False
    if comments:
        has_discussion = await _check_discussion_group(app, channel)

    messages = []
    try:
        msg_index = 0
        async for msg in app.get_chat_history(channel, limit=limit):
            msg_date = msg.date if msg.date.tzinfo else msg.date.replace(tzinfo=timezone.utc)
            if msg_date < since:
                break
            # Break if we've reached already-read messages
            if min_id and msg.id <= min_id:
                break
            # Pyrogram: text for plain messages, caption for media messages
            text = ""
            if msg.text:
                text = msg.text
            elif msg.caption:
                text = msg.caption

            # --text-only: skip posts that have no text at all
            if text_only and not text:
                continue

            entry = {
                "id": msg.id,
                "date": msg_date.isoformat(),
                "text": text,
                "views": msg.views,
                "forwards": msg.forwards,
                "link": f"https://t.me/{channel.lstrip('@')}/{msg.id}",
                "has_media": msg.media is not None,
            }
            if msg.media:
                entry["media_type"] = str(msg.media)

            # Fetch comments for this post
            if comments and has_discussion:
                if msg_index > 0:
                    await asyncio.sleep(comment_delay)
                try:
                    post_comments = await _fetch_comments(app, channel, msg.id, comment_limit)
                    entry["comment_count"] = len(post_comments)
                    entry["comments"] = post_comments
                except FloodWait as e:
                    if e.value <= _FLOOD_WAIT_MAX:
                        await asyncio.sleep(e.value)
                        try:
                            post_comments = await _fetch_comments(app, channel, msg.id, comment_limit)
                            entry["comment_count"] = len(post_comments)
                            entry["comments"] = post_comments
                        except Exception:
                            entry["comment_count"] = 0
                            entry["comments"] = []
                    else:
                        entry["comment_count"] = 0
                        entry["comments"] = []
                        entry["comments_error"] = f"Rate limited: retry after {e.value}s"

            messages.append(entry)
            msg_index += 1
    except (ChannelPrivate, ChatForbidden, ChatRestricted) as e:
        return _channel_error(
            channel, "access_denied",
            f"Channel is private or access denied: {e}",
            "remove_from_list_or_rejoin",
        )
    except (ChannelBanned, UserBannedInChannel) as e:
        return _channel_error(
            channel, "banned",
            f"Banned from channel: {e}",
            "remove_from_list",
        )
    except (ChannelInvalid, ChatInvalid, PeerIdInvalid, UsernameNotOccupied) as e:
        return _channel_error(
            channel, "not_found",
            f"Channel not found or username is incorrect: {e}",
            "check_username",
        )
    except KeyError as e:
        # Pyrogram raises KeyError from resolve_peer / get_peer_by_username
        # when the username doesn't exist in Telegram's database
        return _channel_error(
            channel, "not_found",
            f"Username not found: {e}",
            "check_username",
        )
    except (InviteHashExpired, InviteHashInvalid) as e:
        return _channel_error(
            channel, "invite_expired",
            f"Invite link expired or invalid: {e}",
            "request_new_invite",
        )
    except FloodWait as e:
        return _channel_error(
            channel, "flood_wait",
            f"Rate limited: retry after {e.value}s",
            f"wait_{e.value}s",
        )
    except Exception as e:
        return _channel_error(
            channel, "unexpected",
            f"Unexpected error: {e}",
            "report_to_user",
        )

    result = {
        "channel": channel,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "since": since.isoformat(),
        "count": len(messages),
        "messages": messages,
    }
    if comments:
        result["comments_enabled"] = True
        result["comments_available"] = has_discussion
    return result


_FLOOD_WAIT_MAX = 60  # auto-retry only if wait is <= this many seconds


async def fetch_messages(channel: str, since: datetime, limit: int, text_only: bool,
                         config_file=None, session_file=None,
                         comments: bool = False, comment_limit: int = 10, comment_delay: float = 3,
                         min_id: int = 0):
    api_id, api_hash, session_name = get_config(config_file, session_file)
    _validate_session(session_name)
    async with Client(session_name, api_id=api_id, api_hash=api_hash, **_DEVICE) as app:
        return await _fetch_channel(app, channel, since, limit, text_only,
                                    comments=comments, comment_limit=comment_limit,
                                    comment_delay=comment_delay, min_id=min_id)


async def fetch_multiple(channels: list, since: datetime, limit: int, text_only: bool,
                         config_file=None, session_file=None, delay: float = 10,
                         min_ids: dict = None):
    """Fetch messages from multiple channels sequentially with delays.

    Channels are fetched one at a time to avoid Telegram FloodWait.
    If a FloodWait <= 60s is hit, the request is retried once automatically.
    """
    api_id, api_hash, session_name = get_config(config_file, session_file)
    _validate_session(session_name)

    results = []
    async with Client(session_name, api_id=api_id, api_hash=api_hash, **_DEVICE) as app:
        for i, channel in enumerate(channels):
            channel_min_id = (min_ids or {}).get(channel, 0)
            result = await _fetch_channel(app, channel, since, limit, text_only,
                                          min_id=channel_min_id)

            # Auto-retry on FloodWait if wait is reasonable
            if (isinstance(result, dict) and result.get("error_type") == "flood_wait"):
                wait_action = result.get("action", "")
                try:
                    wait_seconds = int(wait_action.replace("wait_", "").replace("s", ""))
                except (ValueError, AttributeError):
                    wait_seconds = 0
                if 0 < wait_seconds <= _FLOOD_WAIT_MAX:
                    await asyncio.sleep(wait_seconds)
                    result = await _fetch_channel(app, channel, since, limit, text_only,
                                                  min_id=channel_min_id)

            results.append(result)

            # Delay between channels (skip after the last one)
            if i < len(channels) - 1:
                await asyncio.sleep(delay)

    return results


# ── Channel info ─────────────────────────────────────────────────────────────

async def fetch_info(channel: str, config_file=None, session_file=None):
    api_id, api_hash, session_name = get_config(config_file, session_file)
    _validate_session(session_name)
    async with Client(session_name, api_id=api_id, api_hash=api_hash) as app:
        try:
            chat = await app.get_chat(channel)
            return {
                "id": chat.id,
                "title": chat.title,
                "username": chat.username,
                "description": chat.description,
                "members_count": chat.members_count,
                "link": f"https://t.me/{chat.username}" if chat.username else None,
            }
        except (ChannelPrivate, ChatForbidden, ChatRestricted) as e:
            return _channel_error(
                channel, "access_denied",
                f"Channel is private or access denied: {e}",
                "remove_from_list_or_rejoin",
            )
        except (ChannelBanned, UserBannedInChannel) as e:
            return _channel_error(
                channel, "banned",
                f"Banned from channel: {e}",
                "remove_from_list",
            )
        except (ChannelInvalid, ChatInvalid, PeerIdInvalid, UsernameNotOccupied) as e:
            return _channel_error(
                channel, "not_found",
                f"Channel not found or username is incorrect: {e}",
                "check_username",
            )
        except KeyError as e:
            return _channel_error(
                channel, "not_found",
                f"Username not found: {e}",
                "check_username",
            )
        except Exception as e:
            return _channel_error(
                channel, "unexpected",
                f"Unexpected error: {e}",
                "report_to_user",
            )


# ── Auth setup ───────────────────────────────────────────────────────────────

async def setup_auth(config_file=None, session_file=None):
    """Interactive first-time auth — creates session file."""
    api_id, api_hash, session_name = get_config(config_file, session_file)
    print(f"Starting auth for session: {session_name}")
    print("You will receive a code in Telegram. Enter it when prompted.")
    async with Client(session_name, api_id=api_id, api_hash=api_hash, **_DEVICE) as app:
        me = await app.get_me()
        print(json.dumps({"status": "authenticated", "user": me.username or str(me.id)}))


# ── Output helpers ────────────────────────────────────────────────────────────

def _print_text(result, since_label):
    """Print human-readable text output to stdout."""
    items = result if isinstance(result, list) else [result]
    for ch_result in items:
        if "error" in ch_result:
            print(f"[ERROR] {ch_result['channel']}: {ch_result['error']}")
            continue
        print(f"\n=== {ch_result['channel']} ({ch_result['count']} posts since {since_label}) ===")
        for msg in ch_result["messages"]:
            print(f"\n[{msg['date']}] {msg['link']}")
            print(msg["text"][:500] + ("..." if len(msg["text"]) > 500 else ""))
            if "comments" in msg and msg["comments"]:
                print(f"  [{msg['comment_count']} comments]")
                for c in msg["comments"]:
                    user = c.get("from_user") or "anonymous"
                    print(f"    @{user}: {c['text'][:200]}")


def _write_output(result, output_path, fmt, since_label):
    """Write output to a file and print a short confirmation to stdout."""
    output_path = os.path.abspath(output_path)
    with open(output_path, "w", encoding="utf-8") as f:
        if fmt == "json":
            json.dump(result, f, ensure_ascii=False, indent=2)
            f.write("\n")
        else:
            import io, contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                _print_text(result, since_label)
            f.write(buf.getvalue())

    if isinstance(result, list):
        count = sum(r.get("count", 0) for r in result if "error" not in r)
    else:
        count = result.get("count", 0) if "error" not in result else 0
    print(json.dumps({"status": "ok", "output_file": output_path, "count": count}, ensure_ascii=False))


# ── CLI helpers ──────────────────────────────────────────────────────────────

# Common flags hallucinated by LLM agents instead of --since
_FLAG_TYPOS = {
    "--hours": "--since (e.g. --since 24h)",
    "--days": "--since (e.g. --since 7d)",
    "--weeks": "--since (e.g. --since 2w)",
    "--time": "--since (e.g. --since 24h)",
    "--period": "--since (e.g. --since 24h)",
    "--after": "--since (e.g. --since 24h)",
    "--from": "--since (e.g. --since 24h or --since 2026-01-01)",
    "--media": "--text-only (inverted: use --text-only to exclude media-only posts)",
}


def _check_flag_typos():
    """Catch common parameter hallucinations from LLM agents and exit with a helpful JSON error."""
    for arg in sys.argv[1:]:
        if arg in _FLAG_TYPOS:
            print(json.dumps({
                "error": f"Unknown flag: {arg}. Did you mean {_FLAG_TYPOS[arg]}?",
                "action": "fix_command",
            }))
            sys.exit(1)


class _JsonArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that outputs errors as JSON instead of plain text."""

    def error(self, message):
        # Check for flag typos in the error message
        for typo, fix in _FLAG_TYPOS.items():
            if typo in message:
                print(json.dumps({
                    "error": f"Unknown flag: {typo}. Did you mean {fix}?",
                    "action": "fix_command",
                }))
                sys.exit(1)
        print(json.dumps({"error": f"Invalid command: {message}", "action": "fix_command"}))
        sys.exit(1)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    _check_flag_typos()

    parser = _JsonArgumentParser(
        prog="tg-reader",
        description="Read Telegram channel posts for OpenClaw agent"
    )
    # Global options (available to all subcommands)
    parser.add_argument("--config-file", default=None,
                        help="Path to config JSON (overrides ~/.tg-reader.json)")
    parser.add_argument("--session-file", default=None,
                        help="Path to session file (overrides default session path)")

    sub = parser.add_subparsers(dest="cmd", required=True)

    # fetch
    fetch_p = sub.add_parser("fetch", help="Fetch posts from one or more channels")
    fetch_p.add_argument("channels", nargs="+", help="Channel usernames e.g. @durov")
    fetch_p.add_argument("--since", default="24h", help="Time window: 24h, 7d, 2w, or YYYY-MM-DD")
    fetch_p.add_argument("--limit", type=int, default=100, help="Max posts per channel (default 100)")
    fetch_p.add_argument("--text-only", action="store_true",
                        help="Skip posts that have no text (media-only without caption)")
    fetch_p.add_argument("--delay", type=float, default=10,
                        help="Seconds to wait between channels (default 10)")
    fetch_p.add_argument("--comments", action="store_true",
                        help="Fetch comments for each post (single channel only)")
    fetch_p.add_argument("--comment-limit", type=int, default=10,
                        help="Max comments per post (default 10)")
    fetch_p.add_argument("--comment-delay", type=float, default=3,
                        help="Seconds between comment fetches per post (default 3)")
    fetch_p.add_argument("--format", choices=["json", "text"], default="json")
    fetch_p.add_argument("--output", nargs="?", const="tg-output.json", default=None,
                        help="Write output to file instead of stdout (default: tg-output.json)")
    fetch_p.add_argument("--all", action="store_true", dest="fetch_all",
                        help="Ignore read tracking and fetch all matching posts")
    fetch_p.add_argument("--state-file", default=None,
                        help="Path to state file for read tracking (overrides config)")

    # info
    info_p = sub.add_parser("info", help="Get channel title, description and subscriber count")
    info_p.add_argument("channel", help="Channel username e.g. @durov")

    # auth
    sub.add_parser("auth", help="Authenticate with Telegram (first-time setup)")

    args = parser.parse_args()
    cf = args.config_file
    sf = args.session_file

    if args.cmd == "info":
        result = asyncio.run(fetch_info(args.channel, cf, sf))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.cmd == "auth":
        asyncio.run(setup_auth(cf, sf))
        return

    if args.cmd == "fetch":
        try:
            since_dt = parse_since(args.since)
        except ValueError as e:
            print(json.dumps({"error": str(e)}))
            sys.exit(1)

        # Validate --comments constraints
        if args.comments:
            if len(args.channels) > 1:
                print(json.dumps({
                    "error": "--comments can only be used with a single channel",
                    "action": "remove_extra_channels_or_drop_comments",
                }))
                sys.exit(1)

        # Lower default limit when fetching comments (token economy)
        limit = args.limit
        if args.comments and limit == 100:
            limit = 30

        # Read tracking (read_unread mode)
        from tg_state import load_tracking_config, load_state, get_last_read_id, update_state, save_state

        read_unread, state_file_path = load_tracking_config(cf)
        if args.state_file:
            state_file_path = args.state_file

        use_tracking = read_unread and not args.fetch_all
        state = None
        min_id = 0
        min_ids = {}

        if use_tracking:
            state = load_state(state_file_path)
            if len(args.channels) == 1:
                min_id = get_last_read_id(state, args.channels[0])
            else:
                min_ids = {ch: get_last_read_id(state, ch) for ch in args.channels}

            # When tracking has state, --since is not needed — fetch all unread.
            # On first run (no state, min_id=0), --since still applies (default 24h).
            has_state = min_id > 0 or any(v > 0 for v in min_ids.values())
            if has_state:
                since_dt = datetime(2000, 1, 1, tzinfo=timezone.utc)

        if len(args.channels) == 1:
            result = asyncio.run(fetch_messages(
                args.channels[0], since_dt, limit, args.text_only, cf, sf,
                comments=args.comments, comment_limit=args.comment_limit,
                comment_delay=args.comment_delay, min_id=min_id))
        else:
            result = asyncio.run(fetch_multiple(args.channels, since_dt, limit, args.text_only, cf, sf,
                                                delay=args.delay, min_ids=min_ids))

        # Update tracking state after successful fetch
        if use_tracking and state is not None:
            if isinstance(result, list):
                for ch_result in result:
                    if "error" not in ch_result and ch_result.get("messages"):
                        newest_id = max(m["id"] for m in ch_result["messages"])
                        update_state(state, ch_result["channel"], newest_id)
            elif "error" not in result and result.get("messages"):
                newest_id = max(m["id"] for m in result["messages"])
                update_state(state, result["channel"], newest_id)
            save_state(state, state_file_path)

        # Add tracking metadata to output
        if read_unread:
            tracking_meta = {"enabled": True}
            if args.fetch_all:
                tracking_meta["overridden"] = True
            if isinstance(result, list):
                for ch_result in result:
                    if "error" not in ch_result:
                        ch_result["read_unread"] = tracking_meta.copy()
            elif "error" not in result:
                result["read_unread"] = tracking_meta

        if args.output:
            _write_output(result, args.output, args.format, args.since)
        elif args.format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            _print_text(result, args.since)


if __name__ == "__main__":
    main()
