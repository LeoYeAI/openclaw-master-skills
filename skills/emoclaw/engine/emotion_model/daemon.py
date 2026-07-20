"""Emotion model daemon — persistent process with Unix socket interface.

Loads the model once and listens for inference requests, avoiding
the ~2s sentence-transformer load time on every message.

Run as:  python -m emotion_model.daemon
Or via:  systemctl start <agent>-emotion
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import traceback

from . import config
from .inference import EmotionEngine


def run_daemon(config_path: str | None = None) -> None:
    """Start the emotion daemon.

    Args:
        config_path: Optional path to emoclaw.yaml override.
                     If provided, sets EMOCLAW_CONFIG env var so
                     config reloads from that path on next import.
    """
    if config_path:
        os.environ["EMOCLAW_CONFIG"] = config_path

    model_path = config.CHECKPOINT_DIR / "best_model.pt"
    socket_path = config.SOCKET_PATH

    print(f"[{config.AGENT_NAME}] Loading emotion engine (model: {model_path})...")
    engine = EmotionEngine(
        model_path=str(model_path) if model_path.exists() else None,
        state_path=config.STATE_PATH,
    )
    print(f"[{config.AGENT_NAME}] Engine loaded. Listening on {socket_path}")

    # Clean up stale socket
    if os.path.exists(socket_path):
        os.unlink(socket_path)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(socket_path)
    server.listen(1)
    os.chmod(socket_path, 0o660)

    try:
        while True:
            conn, _ = server.accept()
            try:
                data = b""
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    data += chunk

                request = json.loads(data.decode("utf-8"))

                # Handle special commands
                if request.get("command") == "ping":
                    response = {"status": "ok", "message": "emotion engine alive"}
                elif request.get("command") == "state":
                    response = {
                        "emotion_vector": engine.state.emotion_vector,
                        "message_count": engine.state.message_count,
                        "last_updated": engine.state.last_updated,
                    }
                else:
                    # Standard inference — defaults come from config
                    block = engine.process_message(
                        message_text=request["text"],
                        sender=request.get("sender"),
                        channel=request.get("channel"),
                        recent_context=request.get("context"),
                    )
                    response = {"state_block": block}

                conn.sendall(json.dumps(response).encode("utf-8"))

            except Exception as e:
                error_msg = json.dumps({"error": str(e)})
                try:
                    conn.sendall(error_msg.encode("utf-8"))
                except Exception:
                    pass
                traceback.print_exc()
            finally:
                conn.close()

    except KeyboardInterrupt:
        print(f"\n[{config.AGENT_NAME}] Shutting down emotion daemon.")
    finally:
        server.close()
        if os.path.exists(socket_path):
            os.unlink(socket_path)


def main() -> None:
    """CLI entry point with --config argument."""
    parser = argparse.ArgumentParser(
        description="Emotion model daemon — persistent inference server"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to emoclaw.yaml config file",
    )
    args = parser.parse_args()
    run_daemon(config_path=args.config)


if __name__ == "__main__":
    main()
