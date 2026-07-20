from __future__ import annotations

import hashlib
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel

logger = logging.getLogger("shiploop.learnings")

STOP_WORDS = frozenset(
    "a an the is are was were to from in on of for with by at and or but not "
    "this that it be have has had do does did will would should could may can".split()
)


class Learning(BaseModel):
    id: str
    date: str
    segment: str
    error_signature: str = ""
    failure: str
    root_cause: str
    fix: str
    tags: list[str] = []
    learning_type: str = "failure"
    improvement_type: str = ""
    prompt_delta: str = ""
    score: float = 1.0


class LearningsEngine:
    """SQLite-backed learnings engine with effectiveness scoring.

    Falls back gracefully to YAML if no DB is provided (backward compat).
    Score semantics:
      - Start at 1.0
      - +0.1 when injected into a prompt and segment succeeds first-try
      - -0.2 when injected and segment fails the same way
      - Learnings with score < 0.3 are flagged as "stale"
    """

    def __init__(self, learnings_path: Path, db: "Database | None" = None):
        self.path = learnings_path
        self.db = db
        self.learnings: list[Learning] = []

        if self.db is not None:
            self._load_from_db()
        else:
            # Legacy YAML path for backward compatibility
            self._load_from_yaml()

    def _load_from_db(self) -> None:
        assert self.db is not None
        rows = self.db.get_all_learnings()
        self.learnings = [
            Learning(
                id=r["id"],
                date=r["date"],
                segment=r["segment"],
                error_signature=r.get("error_signature", ""),
                failure=r["failure"],
                root_cause=r["root_cause"],
                fix=r["fix"],
                tags=r.get("tags", []),
                learning_type=r.get("learning_type", "failure"),
                improvement_type=r.get("improvement_type", ""),
                prompt_delta=r.get("prompt_delta", ""),
                score=r.get("score", 1.0),
            )
            for r in rows
        ]

    def _load_from_yaml(self) -> None:
        if not self.path.exists():
            self.learnings = []
            return
        try:
            import yaml
            raw = yaml.safe_load(self.path.read_text())
            if isinstance(raw, list):
                self.learnings = [Learning.model_validate(item) for item in raw]
            else:
                self.learnings = []
        except Exception as e:
            logger.warning("Failed to load learnings from YAML: %s", e)
            self.learnings = []

    def _save(self) -> None:
        """Persist learnings. Uses DB if available, falls back to YAML."""
        if self.db is not None:
            # DB is the source of truth; in-memory list is kept in sync
            return
        self._save_yaml()

    def _save_yaml(self) -> None:
        import os
        import yaml
        data = [learning.model_dump() for learning in self.learnings]
        content = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(".yml.tmp")
        tmp_path.write_text(content)
        os.replace(str(tmp_path), str(self.path))

    def record(
        self,
        segment: str,
        failure: str,
        root_cause: str,
        fix: str,
        tags: list[str] | None = None,
        learning_type: str = "failure",
        improvement_type: str = "",
        prompt_delta: str = "",
    ) -> Learning:
        next_id = f"L{len(self.learnings) + 1:03d}"
        error_sig = _compute_error_signature(failure)
        auto_tags = _extract_tags(failure + " " + root_cause + " " + fix)
        all_tags = sorted(set((tags or []) + auto_tags))

        learning = Learning(
            id=next_id,
            date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            segment=segment,
            error_signature=error_sig,
            failure=failure[:500],
            root_cause=root_cause[:500],
            fix=fix[:500],
            tags=all_tags,
            learning_type=learning_type,
            improvement_type=improvement_type,
            prompt_delta=prompt_delta,
            score=1.0,
        )
        self.learnings.append(learning)

        if self.db is not None:
            self.db.save_learning(
                learning_id=learning.id,
                date=learning.date,
                segment=learning.segment,
                error_signature=learning.error_signature,
                failure=learning.failure,
                root_cause=learning.root_cause,
                fix=learning.fix,
                tags=learning.tags,
                learning_type=learning.learning_type,
                improvement_type=learning.improvement_type,
                prompt_delta=learning.prompt_delta,
                score=learning.score,
            )
        else:
            self._save_yaml()

        logger.info("Recorded learning %s for segment %s", next_id, segment)
        return learning

    def bump_score(self, learning_id: str, delta: float) -> None:
        """Adjust effectiveness score for a learning."""
        for learning in self.learnings:
            if learning.id == learning_id:
                learning.score = max(0.0, learning.score + delta)
                if self.db is not None:
                    self.db.update_learning_score(learning_id, delta)
                break

    def on_segment_success(self, injected_ids: list[str]) -> None:
        """Call after a segment succeeds on first try with injected learnings."""
        for lid in injected_ids:
            self.bump_score(lid, +0.1)

    def on_segment_failure(self, injected_ids: list[str]) -> None:
        """Call when segment fails the same way despite injected learnings."""
        for lid in injected_ids:
            self.bump_score(lid, -0.2)

    def get_stale(self, threshold: float = 0.3) -> list[Learning]:
        return [l for l in self.learnings if l.score < threshold]

    def record_decision_gap(
        self,
        segment: str,
        context: str,
        verdict: str,
        run_id: str | None = None,
    ) -> None:
        """Log a situation the system didn't know how to handle."""
        if self.db is not None:
            self.db.record_decision_gap(
                run_id=run_id,
                segment=segment,
                context=context[:1000],
                verdict_taken=verdict,
            )
        else:
            logger.warning(
                "MISSING_DECISION_BRANCH in segment '%s': verdict=%s context=%s",
                segment, verdict, context[:200],
            )

    def search(self, query: str, max_results: int = 3) -> list[Learning]:
        if not self.learnings:
            return []

        query_keywords = _extract_keywords(query)
        if not query_keywords:
            # Return highest-scored learnings
            sorted_learnings = sorted(self.learnings, key=lambda l: l.score, reverse=True)
            return sorted_learnings[:max_results]

        scored: list[tuple[float, Learning]] = []
        for learning in self.learnings:
            kw_score = _keyword_score(query_keywords, learning)
            if kw_score > 0:
                # Weight by both keyword relevance and effectiveness score
                combined = kw_score * (0.5 + learning.score * 0.5)
                scored.append((combined, learning))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [learning for _, learning in scored[:max_results]]

    def format_for_prompt(self, learnings: list[Learning]) -> str:
        if not learnings:
            return ""

        failure_learnings = [l for l in learnings if l.learning_type != "optimization"]
        optimization_learnings = [l for l in learnings if l.learning_type == "optimization"]

        lines = ["## Relevant Lessons from Past Runs", ""]

        if failure_learnings:
            for learning in failure_learnings:
                lines.append(f"### {learning.id}: {learning.segment}")
                lines.append(f"- **Failure:** {learning.failure}")
                lines.append(f"- **Root cause:** {learning.root_cause}")
                lines.append(f"- **Fix:** {learning.fix}")
                lines.append("")
            lines.append("Use these lessons to avoid repeating the same mistakes.")
            lines.append("")

        if optimization_learnings:
            lines.append("## Optimized Instructions from Past Runs")
            lines.append("")
            for learning in optimization_learnings:
                lines.append(f"### {learning.id}: {learning.segment} ({learning.improvement_type})")
                lines.append(f"- **For best results:** {learning.prompt_delta}")
                lines.append("")

        return "\n".join(lines)


def _compute_error_signature(error_text: str) -> str:
    first_lines = "\n".join(error_text.strip().splitlines()[:5])
    return hashlib.sha256(first_lines.encode()).hexdigest()[:12]


def _extract_keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", text.lower())
    return {w for w in words if len(w) >= 3 and w not in STOP_WORDS}


def _extract_tags(text: str) -> list[str]:
    keywords = _extract_keywords(text)
    tag_indicators = {
        "import", "module", "build", "error", "component", "test", "lint",
        "type", "typescript", "config", "route", "api", "auth", "deploy",
        "missing", "undefined", "null", "timeout", "permission", "syntax",
    }
    return sorted(keywords & tag_indicators)


def _keyword_score(query_keywords: set[str], learning: Learning) -> float:
    learning_text = " ".join([
        learning.failure, learning.root_cause, learning.fix,
        learning.segment, " ".join(learning.tags),
    ]).lower()
    learning_keywords = _extract_keywords(learning_text)
    overlap = query_keywords & learning_keywords
    if not overlap:
        return 0.0
    tag_overlap = query_keywords & set(learning.tags)
    return len(overlap) + len(tag_overlap) * 0.5


# Avoid circular import — imported lazily
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .db import Database
