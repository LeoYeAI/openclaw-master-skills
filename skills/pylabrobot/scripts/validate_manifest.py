#!/usr/bin/env python3
"""Validate a strict offline PyLabRobot protocol manifest."""

from __future__ import annotations

import argparse
from typing import Sequence

if __package__:
  from ._common import ValidationError, emit_error, emit_json, load_json, validate_manifest
else:
  from _common import ValidationError, emit_error, emit_json, load_json, validate_manifest


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
      description=(
          "Validate protocol-manifest schema v1.0. This command is dependency-free "
          "and never imports PyLabRobot or accesses hardware/network interfaces."
      )
  )
  parser.add_argument("--input", required=True, help="Local UTF-8 .json manifest")
  return parser


def main(argv: Sequence[str] | None = None) -> int:
  args = build_parser().parse_args(argv)
  try:
    manifest = validate_manifest(load_json(args.input))
  except (OSError, ValidationError) as error:
    return emit_error(error)
  emit_json(
      {
          "ok": True,
          "protocol_id": manifest["protocol_id"],
          "schema_version": manifest["schema_version"],
          "mode": manifest["mode"],
          "resource_count": len(manifest["resources"]),
          "requires_human_confirmation": True,
          "hardware_access": False,
      }
  )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
