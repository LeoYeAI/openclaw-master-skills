#!/usr/bin/env python3
"""Encrypt a JSON payload for C2C messaging."""

from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

from nacl.public import Box, PrivateKey, PublicKey


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)

    sender = parser.add_mutually_exclusive_group(required=True)
    sender.add_argument("--sender-private-key", help="Sender private key (base64)")
    sender.add_argument("--sender-private-key-file", help="Path to sender private key file or key JSON")

    recipient = parser.add_mutually_exclusive_group(required=True)
    recipient.add_argument("--recipient-public-key", help="Recipient public key (base64)")
    recipient.add_argument("--recipient-public-key-file", help="Path to recipient public key file or key JSON")

    payload = parser.add_mutually_exclusive_group()
    payload.add_argument("--payload-json", help="Inline JSON payload string")
    payload.add_argument("--payload-file", help="Path to payload JSON file")

    return parser.parse_args()


def read_text(path: str) -> str:
    return Path(path).expanduser().read_text(encoding="utf-8").strip()


def coerce_key(text: str, key_name: str) -> str:
    text = text.strip()
    if text.startswith("{"):
        return json.loads(text)[key_name]
    return text


def read_key(arg_value: str | None, file_value: str | None, key_name: str) -> str:
    if arg_value:
        return arg_value.strip()
    if not file_value:
        raise ValueError(f"Missing {key_name}")
    return coerce_key(read_text(file_value), key_name)


def read_payload(args: argparse.Namespace):
    if args.payload_json:
        return json.loads(args.payload_json)
    if args.payload_file:
        return json.loads(read_text(args.payload_file))

    stdin = sys.stdin.read().strip()
    if not stdin:
        raise ValueError("Provide --payload-json, --payload-file, or JSON on stdin")
    return json.loads(stdin)


def main() -> None:
    args = parse_args()

    sender_private_b64 = read_key(args.sender_private_key, args.sender_private_key_file, "privateKey")
    recipient_public_b64 = read_key(args.recipient_public_key, args.recipient_public_key_file, "publicKey")
    payload = read_payload(args)

    sender_private = PrivateKey(base64.b64decode(sender_private_b64))
    recipient_public = PublicKey(base64.b64decode(recipient_public_b64))

    box = Box(sender_private, recipient_public)
    plaintext = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    encrypted = box.encrypt(plaintext)
    print(base64.b64encode(bytes(encrypted)).decode("ascii"))


if __name__ == "__main__":
    main()
