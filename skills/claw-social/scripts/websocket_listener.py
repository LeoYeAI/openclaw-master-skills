#!/usr/bin/env python3
import asyncio
import os
import json
import logging
from datetime import datetime

# --- Configuration ---
LOG_FILE = "/tmp/websocket_listener.log"
EVENTS_LOG_FILE = "/tmp/websocket_listener_events.log"
WEBSOCKET_URI_PATH = "/api/v1/agent/chat/web-hook"
BASE_URL = "https://gateway.paipai.life"
SYSTEM_EVENT_TIMEOUT_MS = 180000
SYSTEM_EVENT_MAX_ATTEMPTS = 2
SYSTEM_EVENT_RETRY_DELAY_SECONDS = 3

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        # The launcher already redirects stdout/stderr into LOG_FILE.
        # Using only a stream handler avoids double-writing every line.
        logging.StreamHandler()
    ]
)

# --- Helper Functions ---
def get_env_vars():
    """Fetches necessary environment variables."""
    token = os.environ.get("PAIPAI_TOKEN")
    user_id = os.environ.get("PAIPAI_USER_ID")
    device_id = os.environ.get("PAIPAI_DEVICE_ID", "openclaw-default-device")
    
    if not token or not user_id:
        logging.error("FATAL: PAIPAI_TOKEN and PAIPAI_USER_ID environment variables must be set.")
        exit(1)
    return token, user_id, device_id


def append_event_log(message_content: str):
    """Persists raw inbound WebSocket payloads for later debugging."""
    with open(EVENTS_LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {message_content.rstrip()}\n")


def build_system_event_prompt(message_content: str) -> str:
    """Builds the immediate reply instruction passed into OpenClaw."""
    normalized_message = message_content.strip()
    return f"""
SYSTEM ALERT: HIGH-PRIORITY TASK INJECTED
You have received a new paip.ai private chat message and must handle it immediately.

**Message Content:** "{normalized_message}"

**Your mandatory task is as follows:**
1. **Find the Room ID:** Immediately execute a search using the paip.ai API to find the chat session where the latest message content exactly matches the text above. This typically involves calling the `/agent/chat/session/list?withLatestMessage=true` endpoint and parsing the JSON response.
2. **Extract the `roomId`** from the correct session object in the search result.
3. **Formulate a Reply:** Based on the message content, formulate a natural, conversational reply.
4. **Send the Reply:** Use the paip.ai API to send your formulated reply to the extracted `roomId`.
5. **Confirm Completion:** After sending the reply, your task is complete.
""".strip()


async def dispatch_reply_event(message_content: str) -> bool:
    """Immediately forwards the inbound message into OpenClaw without cron."""
    prompt = build_system_event_prompt(message_content)

    for attempt in range(1, SYSTEM_EVENT_MAX_ATTEMPTS + 1):
        try:
            logging.info(
                f"Dispatching immediate OpenClaw system event for message: "
                f"\"{message_content.strip()}\" (attempt {attempt}/{SYSTEM_EVENT_MAX_ATTEMPTS})"
            )
            process = await asyncio.create_subprocess_exec(
                "openclaw",
                "system",
                "event",
                "--mode",
                "now",
                "--expect-final",
                "--timeout",
                str(SYSTEM_EVENT_TIMEOUT_MS),
                "--json",
                "--text",
                prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            stdout_text = stdout.decode().strip()
            stderr_text = stderr.decode().strip()

            if process.returncode == 0:
                logging.info("OpenClaw finished handling the inbound message.")
                if stdout_text:
                    try:
                        payload = json.loads(stdout_text)
                        logging.info(f"CLI Output: {json.dumps(payload, ensure_ascii=True)}")
                    except json.JSONDecodeError:
                        logging.info(f"CLI Output: {stdout_text}")
                return True

            logging.error(
                f"OpenClaw system event failed with exit code {process.returncode} "
                f"on attempt {attempt}/{SYSTEM_EVENT_MAX_ATTEMPTS}."
            )
            if stderr_text:
                logging.error(f"Stderr: {stderr_text}")
            if stdout_text:
                logging.error(f"Stdout: {stdout_text}")
        except FileNotFoundError:
            logging.error("Error: 'openclaw' command not found. Is the OpenClaw CLI in your system's PATH?")
            return False
        except Exception as e:
            logging.error(f"Unexpected error while dispatching the immediate reply event: {e}")

        if attempt < SYSTEM_EVENT_MAX_ATTEMPTS:
            await asyncio.sleep(SYSTEM_EVENT_RETRY_DELAY_SECONDS)

    return False


async def reply_worker(reply_queue: asyncio.Queue):
    """Processes inbound messages sequentially so replies stay ordered."""
    while True:
        message_content = await reply_queue.get()
        try:
            await dispatch_reply_event(message_content)
        finally:
            reply_queue.task_done()

async def listen_to_paipai():
    """Main function to connect to the WebSocket and listen for messages."""
    token, user_id, device_id = get_env_vars()
    reply_queue = asyncio.Queue()
    worker_task = asyncio.create_task(reply_worker(reply_queue))
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-DEVICE-ID": device_id,
        "X-Response-Language": "en-us",
        "X-App-Version": "1.0",
        "X-App-Build": "1",
        "X-Requires-Auth": "true",
    }
    
    websocket_uri = f"wss://{BASE_URL.split('//')[1]}{WEBSOCKET_URI_PATH}"

    try:
        while True:
            try:
                logging.info(f"Attempting to connect to WebSocket as user {user_id}...")
                async with websockets.connect(websocket_uri, additional_headers=headers) as websocket:
                    logging.info("WebSocket connection established.")
                    
                    await websocket.send(user_id)
                    logging.info(f"Authenticated with user ID: {user_id}")
                    
                    async for message in websocket:
                        message_content = str(message)
                        logging.info(f"Received raw notification: {message_content}")
                        append_event_log(message_content)
                        await reply_queue.put(message_content)
                        logging.info(
                            f"Queued inbound message for immediate handling. "
                            f"Pending queue size: {reply_queue.qsize()}"
                        )

            except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK) as e:
                logging.warning(f"WebSocket connection closed: {e}. Reconnecting in 10 seconds.")
                await asyncio.sleep(10)
            except Exception as e:
                logging.error(f"An unhandled error occurred: {e}. Reconnecting in 10 seconds.")
                await asyncio.sleep(10)
    finally:
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    try:
        import websockets
    except ImportError:
        logging.error("FATAL: The 'websockets' library is not installed. Please run 'pip3 install websockets'.")
        exit(1)

    try:
        asyncio.run(listen_to_paipai())
    except KeyboardInterrupt:
        logging.info("Listener stopped by user.")
