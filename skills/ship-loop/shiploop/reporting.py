from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field
from typing import TextIO

from .config import SegmentConfig, SegmentStatus, ShipLoopConfig


@dataclass
class SegmentReport:
    name: str
    status: str
    commit: str | None = None
    tag: str | None = None
    deploy_url: str | None = None
    duration_seconds: float = 0.0
    cost_usd: float = 0.0
    repair_attempts: int = 0
    meta_experiments: int = 0
    errors: list[str] = field(default_factory=list)


class Reporter:
    def __init__(self, config: ShipLoopConfig, out: TextIO | None = None):
        self.config = config
        self.out = out or sys.stdout
        self.segment_reports: list[SegmentReport] = []
        self._start_time = time.monotonic()
        self._segment_start: float | None = None

    def pipeline_start(self) -> None:
        total = len(self.config.segments)
        self._print(f"\n🚢 Ship Loop: {self.config.project} ({total} segments)")
        self._print("━" * 50)

    def segment_start(self, index: int, segment: SegmentConfig) -> None:
        total = len(self.config.segments)
        self._segment_start = time.monotonic()
        self._print(f"\n🔄 Segment {index + 1}/{total}: {segment.name}")

    def segment_phase(self, segment_name: str, phase: str) -> None:
        elapsed = self._elapsed_segment()
        self._print(f"   {_phase_emoji(phase)} {phase}... ({elapsed})")

    def segment_shipped(self, index: int, report: SegmentReport) -> None:
        total = len(self.config.segments)
        cost_str = f", ${report.cost_usd:.2f}" if report.cost_usd > 0 else ""
        short_sha = (report.commit or "")[:7]
        elapsed = _format_duration(report.duration_seconds)
        self._print(
            f"✅ Segment {index + 1}/{total}: {report.name} — shipped "
            f"({short_sha}) [{elapsed}{cost_str}]"
        )
        self.segment_reports.append(report)

    def segment_failed(self, index: int, report: SegmentReport) -> None:
        total = len(self.config.segments)
        self._print(f"❌ Segment {index + 1}/{total}: {report.name} — FAILED")
        if report.repair_attempts > 0:
            self._print(f"   Repair: {report.repair_attempts} attempts failed")
        if report.meta_experiments > 0:
            self._print(f"   Meta: {report.meta_experiments} experiments failed")
        for error in report.errors[-3:]:
            self._print(f"   {error}")
        self.segment_reports.append(report)

    def repair_attempt(self, segment_name: str, attempt: int, max_attempts: int) -> None:
        self._print(f"   🔧 Repair attempt {attempt}/{max_attempts}")

    def repair_success(self, segment_name: str, attempt: int) -> None:
        self._print(f"   ✅ Preflight passed after repair attempt {attempt}")

    def repair_failure(self, segment_name: str, attempt: int, error_summary: str) -> None:
        self._print(f"   ❌ Repair {attempt} failed: {error_summary[:100]}")

    def meta_start(self) -> None:
        self._print("   🧪 Entering meta loop...")

    def meta_analysis(self) -> None:
        self._print("   🧠 Running meta-analysis...")

    def experiment_start(self, exp_num: int, total: int) -> None:
        self._print(f"   🧪 Experiment {exp_num}/{total}")

    def experiment_result(self, exp_num: int, passed: bool, diff_lines: int = 0) -> None:
        if passed:
            self._print(f"   ✅ Experiment {exp_num} passed (diff: {diff_lines} lines)")
        else:
            self._print(f"   ❌ Experiment {exp_num} failed")

    def experiment_winner(self, exp_num: int, branch: str) -> None:
        self._print(f"   🏆 Winner: experiment {exp_num} (branch: {branch})")

    def optimization_start(self, segment_name: str) -> None:
        self._print(f"   🔬 Background optimization for '{segment_name}'...")

    def optimization_result(self, segment_name: str, result: dict) -> None:
        if result.get("winner") is not None:
            self._print(f"   🎯 Optimization found: {result.get('improvement_type', '')} for '{segment_name}'")
        else:
            self._print(f"   ℹ️  No optimization found for '{segment_name}'")

    def optimization_skipped(self, segment_name: str, reason: str) -> None:
        self._print(f"   ⏭️  Optimization skipped for '{segment_name}': {reason}")

    def budget_warning(self, segment: str, cost: float, limit: float) -> None:
        self._print(f"⚠️  Budget alert: {segment} at ${cost:.2f} / ${limit:.2f}")

    def budget_halt(self, segment: str, cost: float, limit: float) -> None:
        self._print(f"🛑 Budget exceeded: {segment} at ${cost:.2f} (limit: ${limit:.2f}) — halting")

    def pipeline_complete(self) -> None:
        elapsed = time.monotonic() - self._start_time
        shipped = sum(1 for r in self.segment_reports if r.status == "shipped")
        total = len(self.config.segments)
        total_cost = sum(r.cost_usd for r in self.segment_reports)

        self._print("\n" + "━" * 50)
        if shipped == total:
            self._print(f"🏁 Ship loop complete! {shipped}/{total} segments shipped.")
        else:
            failed = total - shipped
            self._print(f"🏁 Ship loop finished. {shipped}/{total} shipped, {failed} failed.")
        self._print(f"   Total time: {_format_duration(elapsed)}")
        if total_cost > 0:
            self._print(f"   Total cost: ${total_cost:.2f}")
        self._print("━" * 50)

    def get_json_report(self) -> str:
        return json.dumps(
            {
                "project": self.config.project,
                "total_segments": len(self.config.segments),
                "shipped": sum(1 for r in self.segment_reports if r.status == "shipped"),
                "failed": sum(1 for r in self.segment_reports if r.status == "failed"),
                "total_cost_usd": sum(r.cost_usd for r in self.segment_reports),
                "total_duration_seconds": time.monotonic() - self._start_time,
                "segments": [
                    {
                        "name": r.name,
                        "status": r.status,
                        "commit": r.commit,
                        "tag": r.tag,
                        "cost_usd": r.cost_usd,
                        "duration_seconds": r.duration_seconds,
                        "repair_attempts": r.repair_attempts,
                    }
                    for r in self.segment_reports
                ],
            },
            indent=2,
        )

    def _elapsed_segment(self) -> str:
        if self._segment_start is None:
            return ""
        return _format_duration(time.monotonic() - self._segment_start)

    def _print(self, msg: str) -> None:
        print(msg, file=self.out, flush=True)


def _phase_emoji(phase: str) -> str:
    return {
        "coding": "🤖",
        "preflight": "🛫",
        "shipping": "📦",
        "verifying": "🔍",
        "repairing": "🔧",
        "experimenting": "🧪",
    }.get(phase, "▶")


def _format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"
