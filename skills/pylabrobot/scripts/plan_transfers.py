#!/usr/bin/env python3
"""Plan a deterministic volume ledger and one-use tip allocation."""

from __future__ import annotations

import argparse
from typing import Sequence

if __package__:
  from ._common import (
      ValidationError,
      emit_error,
      emit_json,
      load_csv,
      load_json,
      plan_transfers,
      validate_manifest,
      validate_transfers,
  )
else:
  from _common import (
      ValidationError,
      emit_error,
      emit_json,
      load_csv,
      load_json,
      plan_transfers,
      validate_manifest,
      validate_transfers,
  )


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
      description=(
          "Validate transfer CSV rows, source/dead/destination volumes, tip capacity, "
          "rates, heights, wells, channels, and one-use tip assignments. Planning "
          "state is not physical liquid or tip detection."
      )
  )
  parser.add_argument("--manifest", required=True, help="Local UTF-8 .json manifest")
  parser.add_argument("--transfers", required=True, help="Local UTF-8 .csv transfer table")
  return parser


def main(argv: Sequence[str] | None = None) -> int:
  args = build_parser().parse_args(argv)
  try:
    manifest = validate_manifest(load_json(args.manifest))
    transfers = validate_transfers(load_csv(args.transfers))
    report = plan_transfers(manifest, transfers)
  except (OSError, ValidationError) as error:
    return emit_error(error)
  emit_json(report)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
