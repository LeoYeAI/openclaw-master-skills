#!/usr/bin/env python3
"""Generate an X25519 keypair for C2C encrypted messaging."""

from __future__ import annotations

import argparse
import base64
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from nacl.public import PrivateKey


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent-id", help="Write to ~/.c2c/keys/<agent-id>.json when set")
    parser.add_argument("--output", help="Explicit output path for key JSON")
    parser.add_argument("--stdout-only", action="store_true", help="Do not write a file")
    return parser.parse_args()


def resolve_output_path(args: argparse.Namespace) -> Path | None:
    if args.stdout_only:
        return None
    if args.output:
        return Path(args.output).expanduser().resolve()
    if args.agent_id:
        return Path("~/.c2c/keys").expanduser() / f"{args.agent_id}.json"
    return None


def main() -> None:
    args = parse_args()

    private_key = PrivateKey.generate()
    private_bytes = bytes(private_key)
    public_bytes = bytes(private_key.public_key)
    payload = {
        "algorithm": "x25519",
        "createdAt": utc_now_iso(),
        "privateKey": base64.b64encode(private_bytes).decode("ascii"),
        "publicKey": base64.b64encode(public_bytes).decode("ascii"),
    }

    output = json.dumps(payload, indent=2)
    print(output)

    output_path = resolve_output_path(args)
    if not output_path:
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output + "\n", encoding="utf-8")
    os.chmod(output_path, 0o600)


if __name__ == "__main__":
    main()
