#!/usr/bin/env python3
"""Check bounded static deck geometry without importing PyLabRobot."""

from __future__ import annotations

import argparse
from typing import Sequence

if __package__:
  from ._common import (
      ValidationError,
      emit_error,
      emit_json,
      geometry_report,
      load_json,
      validate_manifest,
  )
else:
  from _common import (
      ValidationError,
      emit_error,
      emit_json,
      geometry_report,
      load_json,
      validate_manifest,
  )


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
      description=(
          "Check resource bounds and static axis-aligned collisions in an offline "
          "manifest. No hardware, serial, USB, or network access occurs."
      )
  )
  parser.add_argument("--input", required=True, help="Local UTF-8 .json manifest")
  return parser


def main(argv: Sequence[str] | None = None) -> int:
  args = build_parser().parse_args(argv)
  try:
    manifest = validate_manifest(load_json(args.input))
    report = geometry_report(manifest)
  except (OSError, ValidationError) as error:
    return emit_error(error)
  emit_json({"protocol_id": manifest["protocol_id"], **report})
  return 0 if report["ok"] else 3


if __name__ == "__main__":
  raise SystemExit(main())
