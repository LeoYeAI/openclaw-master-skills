#!/usr/bin/env python3
"""Test if Telethon session is authorized."""

import asyncio
import os
from telethon import TelegramClient

async def test_session():
    # Get credentials from environment variables
    api_id = os.environ.get("TG_API_ID")
    api_hash = os.environ.get("TG_API_HASH")
    
    if not api_id or not api_hash:
        print("Error: TG_API_ID and TG_API_HASH environment variables must be set")
        print("Example:")
        print("  export TG_API_ID=12345678")
        print("  export TG_API_HASH=your_api_hash_here")
        return
    
    session_name = os.path.expanduser("~/.telethon-reader")
    
    print(f"Testing session: {session_name}.session")
    print(f"API ID: {api_id}")
    print(f"API Hash: {'*' * len(api_hash)}")
    
    client = TelegramClient(session_name, int(api_id), api_hash)
    await client.connect()
    
    is_auth = await client.is_user_authorized()
    print(f"Is authorized: {is_auth}")
    
    if is_auth:
        me = await client.get_me()
        print(f"Logged in as: {me.username or me.id}")
    else:
        print("Session is not authorized!")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_session())