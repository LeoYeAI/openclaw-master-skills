#!/usr/bin/env python3
"""Decrypt a C2C encrypted payload."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

from nacl.public import Box, PrivateKey, PublicKey


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)

    recipient = parser.add_mutually_exclusive_group(required=True)
    recipient.add_argument("--recipient-private-key", help="Recipient private key (base64)")
    recipient.add_argument("--recipient-private-key-file", help="Path to recipient private key file or key JSON")

    sender = parser.add_mutually_exclusive_group(required=True)
    sender.add_argument("--sender-public-key", help="Sender public key (base64)")
    sender.add_argument("--sender-public-key-file", help="Path to sender public key file or key JSON")

    cipher = parser.add_mutually_exclusive_group(required=True)
    cipher.add_argument("--encrypted-payload", help="Encrypted payload (base64)")
    cipher.add_argument("--encrypted-file", help="Path to encrypted payload file")

    parser.add_argument("--raw", action="store_true", help="Print raw text instead of JSON formatting")
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


def main() -> None:
    args = parse_args()

    recipient_private_b64 = read_key(args.recipient_private_key, args.recipient_private_key_file, "privateKey")
    sender_public_b64 = read_key(args.sender_public_key, args.sender_public_key_file, "publicKey")

    if args.encrypted_payload:
        encrypted_b64 = args.encrypted_payload.strip()
    else:
        encrypted_b64 = read_text(args.encrypted_file)

    recipient_private = PrivateKey(base64.b64decode(recipient_private_b64))
    sender_public = PublicKey(base64.b64decode(sender_public_b64))

    box = Box(recipient_private, sender_public)
    plaintext = box.decrypt(base64.b64decode(encrypted_b64)).decode("utf-8")

    if args.raw:
        print(plaintext)
        return

    try:
        print(json.dumps(json.loads(plaintext), indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print(plaintext)


if __name__ == "__main__":
    main()
