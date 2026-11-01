#!/usr/bin/env python3
"""Generate a non-executable, hardware-blocked simulation plan as JSON."""

from __future__ import annotations

import argparse
from typing import Any, Sequence

if __package__:
  from ._common import (
      PYLABROBOT_VERSION,
      ValidationError,
      emit_error,
      emit_json,
      geometry_report,
      load_csv,
      load_json,
      plan_transfers,
      validate_manifest,
      validate_transfers,
  )
else:
  from _common import (
      PYLABROBOT_VERSION,
      ValidationError,
      emit_error,
      emit_json,
      geometry_report,
      load_csv,
      load_json,
      plan_transfers,
      validate_manifest,
      validate_transfers,
  )


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
      description=(
          "Generate a deterministic JSON plan for offline review. The output is data, "
          "not executable Python; this command cannot select or connect to live hardware."
      )
  )
  parser.add_argument("--manifest", required=True, help="Local UTF-8 .json manifest")
  parser.add_argument("--transfers", required=True, help="Local UTF-8 .csv transfer table")
  return parser


def _steps(operations: list[dict[str, Any]]) -> list[dict[str, Any]]:
  steps: list[dict[str, Any]] = []
  for operation in operations:
    common = {
        "transfer_id": operation["transfer_id"],
        "channel": operation["channel"],
    }
    steps.extend(
        [
            {
                **common,
                "action": "pick_up_tip",
                "tip": operation["assigned_tip"],
                "tip_type": operation["tip_type"],
            },
            {
                **common,
                "action": "aspirate",
                "resource": operation["source"],
                "volume_uL": operation["volume_uL"],
                "height_mm": operation["aspiration_height_mm"],
                "rate_uL_s": operation["aspiration_rate_uL_s"],
                "liquid_class_review_label": operation["liquid_class"],
            },
            {
                **common,
                "action": "dispense",
                "resource": operation["destination"],
                "volume_uL": operation["volume_uL"],
                "height_mm": operation["dispense_height_mm"],
                "rate_uL_s": operation["dispense_rate_uL_s"],
                "liquid_class_review_label": operation["liquid_class"],
            },
            {
                **common,
                "action": "drop_tip",
                "resource": operation["drop_tip_at"],
            },
        ]
    )
  return steps


def main(argv: Sequence[str] | None = None) -> int:
  args = build_parser().parse_args(argv)
  try:
    manifest = validate_manifest(load_json(args.manifest))
    geometry = geometry_report(manifest)
    if not geometry["ok"]:
      raise ValidationError("deck geometry must pass before a simulation plan is generated")
    transfers = validate_transfers(load_csv(args.transfers))
    transfer_plan = plan_transfers(manifest, transfers)
  except (OSError, ValidationError) as error:
    return emit_error(error)

  emit_json(
      {
          "ok": True,
          "plan_kind": "offline_review_only",
          "protocol_id": manifest["protocol_id"],
          "pylabrobot_target": PYLABROBOT_VERSION,
          "backend": (
              "pylabrobot.liquid_handling.backends.chatterbox."
              "LiquidHandlerChatterboxBackend"
          ),
          "backend_setup_permitted": True,
          "live_backend_permitted": False,
          "connection_attempted": False,
          "serial_usb_network_access": False,
          "geometry": geometry,
          "steps": _steps(transfer_plan["operations"]),
          "final_volume_ledger": transfer_plan["final_volume_ledger"],
          "tip_summary": transfer_plan["tip_summary"],
          "mandatory_human_review": [
              "physically reconcile deck and labware identities with this manifest",
              "verify calibration, collision envelopes, coordinates, channels, and units",
              "verify source volumes, dead volumes, destination capacity, and physical liquid",
              "verify tips, contamination controls, heights, rates, and vendor liquid classes",
              "confirm guards and emergency stop are ready before any separately authorized live run",
          ],
          "limitations": [
              "the chatterbox backend reports planned commands but does not model robot physics",
              "the visualizer renders tracker state but does not perform simulation logic",
              "bookkeeping cannot detect physical liquid, tips, seals, lids, tubing, or obstacles",
          ],
      }
  )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
