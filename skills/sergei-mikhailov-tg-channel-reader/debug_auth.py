#!/usr/bin/env python3
"""
Debug auth script — verbose MTProto logging.
Run: python3 debug_auth.py
"""
import logging
import asyncio
import json
import os
from pathlib import Path

# Enable full Pyrogram debug output
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
# Silence noisy asyncio internals
logging.getLogger("asyncio").setLevel(logging.WARNING)

from pyrogram import Client

def get_config():
    api_id = os.environ.get("TG_API_ID")
    api_hash = os.environ.get("TG_API_HASH")
    session_name = os.environ.get("TG_SESSION", str(Path.home() / ".tg-reader-session"))

    if not api_id or not api_hash:
        config_path = Path.home() / ".tg-reader.json"
        if config_path.exists():
            with open(config_path) as f:
                cfg = json.load(f)
                api_id = api_id or cfg.get("api_id")
                api_hash = api_hash or cfg.get("api_hash")
                session_name = cfg.get("session", session_name)

    if not api_id or not api_hash:
        print("ERROR: Set TG_API_ID and TG_API_HASH, or create ~/.tg-reader.json")
        raise SystemExit(1)

    print(f"api_id   = {api_id}")
    print(f"api_hash = {api_hash[:4]}{'*' * (len(str(api_hash)) - 4)}")
    print(f"session  = {session_name}")
    return int(api_id), api_hash, session_name


async def main():
    api_id, api_hash, session_name = get_config()

    # Warn before deleting existing session files
    existing = [Path(session_name + ext) for ext in (".session", ".session-journal")
                if Path(session_name + ext).exists()]
    if existing:
        print("\n⚠️  The following session files will be DELETED for a clean re-auth:")
        for p in existing:
            print(f"   {p}")
        answer = input("\nProceed? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print("Aborted.")
            return
        for p in existing:
            print(f"Removing: {p}")
            p.unlink()

    print("\n--- Connecting to Telegram ---\n")
    async with Client(
        session_name,
        api_id=api_id,
        api_hash=api_hash,
    ) as app:
        me = await app.get_me()
        print(f"\n--- Auth OK: {me.username or me.id} ---")


asyncio.run(main())
