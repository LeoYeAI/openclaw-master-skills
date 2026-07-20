from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

logger = logging.getLogger("shiploop.loop.reflect")

if TYPE_CHECKING:
    from ..db import Database


@dataclass
class ReflectionReport:
    generated_at: str = ""
    runs_analyzed: int = 0
    recommendations: list[str] = field(default_factory=list)
    repeat_failures: list[dict] = field(default_factory=list)
    repair_heavy_segments: list[dict] = field(default_factory=list)
    stale_learnings: list[dict] = field(default_factory=list)
    decision_gaps: list[dict] = field(default_factory=list)
    efficiency: dict = field(default_factory=dict)


async def run_reflect_loop(db: Database, depth: int = 10) -> ReflectionReport:
    """Analyze recent run history and generate actionable recommendations.

    Checks:
    - Repeat failures (same error_signature across segments/runs)
    - Repair-heavy segments (>1 repair attempt, same error type)
    - Efficiency trends (cost per segment, time per segment)
    - Stale learnings (score < 0.3, never used effectively)
    - Decision gaps (MISSING_DECISION_BRANCH events)
    """
    report = ReflectionReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
    )

    recent_runs = db.get_recent_runs(limit=depth)
    report.runs_analyzed = len(recent_runs)

    if not recent_runs:
        report.recommendations.append("No runs recorded yet — run your first pipeline to start learning.")
        return report

    # 1. Repeat failures
    repeat_failures = db.get_repeat_failures()
    report.repeat_failures = repeat_failures
    for rf in repeat_failures:
        count = rf["count"]
        segments = rf.get("segments", "")
        report.recommendations.append(
            f"⚠️  Error signature {rf['error_signature'][:8]}… repeated {count}× "
            f"across segments: {segments}. Consider adding a learning or decomposing the task."
        )

    # 2. Repair-heavy segments
    repair_heavy = db.get_repair_heavy_segments()
    report.repair_heavy_segments = repair_heavy
    for rh in repair_heavy:
        if rh["repair_count"] >= 2:
            report.recommendations.append(
                f"🔧 Segment '{rh['segment']}' triggered {rh['repair_count']} repair loops. "
                "Review the task prompt — it may be under-specified or too broad."
            )

    # 3. Stale learnings
    stale = db.get_stale_learnings(threshold=0.3)
    report.stale_learnings = stale
    if stale:
        stale_ids = [s["id"] for s in stale]
        report.recommendations.append(
            f"📉 {len(stale)} stale learning(s) (score < 0.3): {', '.join(stale_ids[:5])}. "
            "These learnings haven't helped — consider removing or rewriting them."
        )

    # 4. Decision gaps
    gaps = db.get_decision_gaps(resolved=False)
    report.decision_gaps = gaps
    if gaps:
        report.recommendations.append(
            f"❓ {len(gaps)} unresolved decision gap(s) recorded. "
            "Review and add learnings or router overrides to handle these cases."
        )

    # 5. Efficiency analysis
    usage_records = db.get_usage_records()
    if usage_records:
        total_cost = sum(r["estimated_cost_usd"] for r in usage_records)
        segments_set = {r["segment"] for r in usage_records}
        avg_cost = total_cost / max(len(segments_set), 1)

        report.efficiency = {
            "total_cost_usd": round(total_cost, 4),
            "unique_segments": len(segments_set),
            "avg_cost_per_segment_usd": round(avg_cost, 4),
            "total_usage_records": len(usage_records),
        }

        if avg_cost > 5.0:
            report.recommendations.append(
                f"💰 Average cost per segment is ${avg_cost:.2f} — consider tightening prompts "
                "or using a cheaper model for repair loops."
            )

    # 6. Auto-create learnings from patterns (if warranted)
    _maybe_auto_learn(db, repeat_failures, report)

    if not report.recommendations:
        report.recommendations.append("✅ No issues detected in recent history. Pipeline looks healthy!")

    logger.info(
        "Reflection complete: %d runs, %d recommendations",
        report.runs_analyzed, len(report.recommendations),
    )
    return report


def _maybe_auto_learn(
    db: Database,
    repeat_failures: list[dict],
    report: ReflectionReport,
) -> None:
    """Auto-generate learnings from repeat failure patterns."""
    for rf in repeat_failures:
        if rf["count"] >= 3:
            # This pattern has failed 3+ times — record it as a learning
            sig = rf["error_signature"]
            segments = rf.get("segments", "unknown")
            learning_id = f"AUTO-{sig[:8]}"

            existing = db.get_all_learnings()
            existing_ids = {l["id"] for l in existing}

            if learning_id not in existing_ids:
                db.save_learning(
                    learning_id=learning_id,
                    date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    segment="*",
                    error_signature=sig,
                    failure=f"Pattern repeated {rf['count']} times across segments: {segments}",
                    root_cause="Recurrent failure not yet resolved",
                    fix="This task pattern needs human review or prompt restructuring",
                    tags=["auto-generated", "repeat-failure"],
                    learning_type="failure",
                    score=1.0,
                )
                report.recommendations.append(
                    f"🤖 Auto-created learning {learning_id} for repeat failure pattern {sig[:8]}…"
                )


def format_report(report: ReflectionReport) -> str:
    """Format a ReflectionReport as human-readable text."""
    lines = [
        "═" * 60,
        f"🪞  Ship Loop Reflection Report",
        f"   Generated: {report.generated_at}",
        f"   Runs analyzed: {report.runs_analyzed}",
        "═" * 60,
        "",
    ]

    if report.efficiency:
        e = report.efficiency
        lines += [
            "📊 Efficiency",
            f"   Total cost:     ${e.get('total_cost_usd', 0):.4f}",
            f"   Segments run:   {e.get('unique_segments', 0)}",
            f"   Avg/segment:    ${e.get('avg_cost_per_segment_usd', 0):.4f}",
            "",
        ]

    if report.repeat_failures:
        lines.append(f"🔁 Repeat Failures ({len(report.repeat_failures)})")
        for rf in report.repeat_failures[:5]:
            lines.append(f"   {rf['error_signature'][:12]}… × {rf['count']}")
        lines.append("")

    if report.repair_heavy_segments:
        lines.append(f"🔧 Repair-Heavy Segments ({len(report.repair_heavy_segments)})")
        for rh in report.repair_heavy_segments[:5]:
            lines.append(f"   {rh['segment']}: {rh['repair_count']} repairs")
        lines.append("")

    if report.stale_learnings:
        lines.append(f"📉 Stale Learnings ({len(report.stale_learnings)})")
        for sl in report.stale_learnings[:5]:
            lines.append(f"   {sl['id']} (score {sl['score']:.2f})")
        lines.append("")

    if report.decision_gaps:
        lines.append(f"❓ Unresolved Decision Gaps ({len(report.decision_gaps)})")
        for dg in report.decision_gaps[:5]:
            lines.append(f"   {dg['segment']}: {dg['verdict_taken']}")
        lines.append("")

    lines.append("💡 Recommendations")
    for rec in report.recommendations:
        lines.append(f"   {rec}")

    lines += ["", "═" * 60]
    return "\n".join(lines)
