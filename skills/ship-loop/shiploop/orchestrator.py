from __future__ import annotations

import asyncio
import fcntl
import glob
import logging
import os
import shutil
import signal
import time
import uuid
from pathlib import Path

from .budget import BudgetTracker
from .config import (
    SegmentConfig,
    SegmentStatus,
    ShipLoopConfig,
    load_config,
    save_config,
)
from .db import Database, get_db
from .deploy import verify_deployment
from .git_ops import get_diff, get_diff_stat, get_touched_paths
from .learnings import LearningsEngine
from .loops.meta import run_meta_loop
from .loops.optimize import run_optimization_loop
from .loops.repair import run_repair_loop
from .loops.ship import ShipResult, run_ship_loop
from .preflight import run_preflight
from .reporting import Reporter, SegmentReport
from .router import Action, Verdict, VerdictRouter

logger = logging.getLogger("shiploop.orchestrator")


class Orchestrator:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = load_config(config_path)
        self.repo = Path(self.config.repo)

        # SQLite database — primary state store in v5.0
        self.db: Database = get_db(self.repo)
        self.run_id: str = str(uuid.uuid4())

        metrics_dir = self.repo / ".shiploop"
        self.budget = BudgetTracker(
            self.config.budget, metrics_dir,
            db=self.db, run_id=self.run_id,
        )

        # LearningsEngine uses DB backend
        learnings_path = self.repo / "learnings.yml"
        self.learnings = LearningsEngine(learnings_path, db=self.db)

        self.reporter = Reporter(self.config)
        self.router = VerdictRouter.from_config(self.config.router or {})

        self._optimization_tasks: list[asyncio.Task] = []
        self._lock_file = None
        self._active_processes: list[asyncio.subprocess.Process] = []

    def _checkpoint(self) -> None:
        """Legacy YAML checkpoint — kept for backward compat with external tooling.
        Runtime state is now in SQLite; config is source of truth for segments definition.
        """
        save_config(self.config, self.config_path)

    def _set_segment_status(self, segment: SegmentConfig, status: SegmentStatus) -> None:
        segment.status = status
        self._checkpoint()
        # Also persist to DB
        self.db.update_segment_status(self.run_id, segment.name, status.value)

    def _find_eligible_segments(self) -> list[int]:
        shipped = {s.name for s in self.config.segments if s.status == SegmentStatus.SHIPPED}
        eligible: list[int] = []

        for i, seg in enumerate(self.config.segments):
            if seg.status != SegmentStatus.PENDING:
                continue
            deps_met = all(dep in shipped for dep in seg.depends_on)
            if deps_met:
                eligible.append(i)

        return eligible

    def _recover_crashed_segments(self) -> list[str]:
        recovered: list[str] = []
        for seg in self.config.segments:
            if seg.status in SegmentStatus.active_states():
                logger.warning("Crash recovery: segment '%s' was in state '%s', marking failed", seg.name, seg.status.value)
                self._set_segment_status(seg, SegmentStatus.FAILED)
                recovered.append(seg.name)
        return recovered

    async def _recover_verifying_segments(self) -> list[str]:
        re_verified: list[str] = []
        for seg in self.config.segments:
            if seg.status == SegmentStatus.FAILED and seg.commit:
                try:
                    verify_result = await verify_deployment(
                        self.config.deploy, seg.commit, self.config.site,
                    )
                    if verify_result.success:
                        seg.deploy_url = verify_result.deploy_url or ""
                        self._set_segment_status(seg, SegmentStatus.SHIPPED)
                        re_verified.append(seg.name)
                        logger.info("Re-verification succeeded for '%s'", seg.name)
                except Exception as e:
                    logger.warning("Re-verification failed for '%s': %s", seg.name, e)
        return re_verified

    def _acquire_lock(self) -> None:
        lock_path = self.repo / ".shiploop.lock"
        self._lock_file = open(lock_path, "w")
        try:
            fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self._lock_file.close()
            self._lock_file = None
            raise RuntimeError(
                "Another shiploop run is already active (could not acquire .shiploop.lock)"
            )

    def _release_lock(self) -> None:
        if self._lock_file:
            try:
                fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_UN)
                self._lock_file.close()
            except OSError:
                pass
            self._lock_file = None

    def _cleanup_orphaned_worktrees(self) -> None:
        for path in glob.glob("/tmp/shiploop-exp-*"):
            try:
                shutil.rmtree(path)
                logger.info("Cleaned orphaned worktree: %s", path)
            except OSError as e:
                logger.warning("Failed to remove orphaned worktree %s: %s", path, e)
        for path in glob.glob("/tmp/shiploop-opt-*"):
            try:
                shutil.rmtree(path)
                logger.info("Cleaned orphaned worktree: %s", path)
            except OSError as e:
                logger.warning("Failed to remove orphaned worktree %s: %s", path, e)

    def _install_signal_handlers(self) -> None:
        loop = asyncio.get_event_loop()

        def _handle_signal(sig: int) -> None:
            logger.warning("Received signal %s, shutting down...", signal.Signals(sig).name)
            for proc in self._active_processes:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
            self._release_lock()
            raise SystemExit(1)

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, _handle_signal, sig)

    def register_process(self, proc: asyncio.subprocess.Process) -> None:
        self._active_processes.append(proc)

    def unregister_process(self, proc: asyncio.subprocess.Process) -> None:
        try:
            self._active_processes.remove(proc)
        except ValueError:
            pass

    async def run(self, dry_run: bool = False) -> bool:
        self._acquire_lock()
        try:
            self._install_signal_handlers()
            self._cleanup_orphaned_worktrees()
            return await self._run_pipeline(dry_run)
        finally:
            self._release_lock()

    async def _run_pipeline(self, dry_run: bool = False) -> bool:
        # Create DB run record
        self.db.create_run(self.run_id, self.config.project)
        # Seed segment records
        for seg in self.config.segments:
            self.db.upsert_segment(
                run_id=self.run_id,
                name=seg.name,
                status=seg.status.value,
                prompt=seg.prompt,
                depends_on=seg.depends_on,
            )

        self.reporter.pipeline_start()

        recovered = self._recover_crashed_segments()
        if recovered:
            for name in recovered:
                self.reporter._print(f"⚠️  Crash recovery: '{name}' was in-progress, marked failed")

        if dry_run:
            result = self._dry_run()
            self.db.finish_run(self.run_id, "success" if result else "failed")
            return result

        all_success = True

        while True:
            eligible = self._find_eligible_segments()
            if not eligible:
                break

            for seg_index in eligible:
                segment = self.config.segments[seg_index]
                success = await self._run_segment(seg_index, segment)
                if not success:
                    all_success = False

        if self._optimization_tasks:
            await asyncio.gather(*self._optimization_tasks, return_exceptions=True)

        # Post-pipeline: auto-reflect if enabled
        if self.config.reflection.enabled and self.config.reflection.auto_run:
            await self._auto_reflect()

        total_cost = self.budget.get_run_cost()
        self.db.finish_run(self.run_id, "success" if all_success else "failed", total_cost)

        self.reporter.pipeline_complete()
        return all_success

    def _dry_run(self) -> bool:
        self.reporter._print("\n🏜️  DRY RUN — no changes will be made\n")
        while True:
            eligible = self._find_eligible_segments()
            if not eligible:
                break
            for seg_index in eligible:
                segment = self.config.segments[seg_index]
                total = len(self.config.segments)
                self.reporter._print(f"  Segment {seg_index + 1}/{total}: {segment.name}")
                self.reporter._print(f"    → Would run agent: {self.config.agent_command}")
                self.reporter._print(f"    → Would run preflight: build={self.config.preflight.build}, lint={self.config.preflight.lint}, test={self.config.preflight.test}")
                self.reporter._print(f"    → Would commit, push, and tag")
                self.reporter._print(f"    → Would verify deploy via {self.config.deploy.provider}")
                segment.status = SegmentStatus.SHIPPED
        self.reporter._print("\n🏜️  Dry run complete.")
        return True

    async def _run_segment(self, index: int, segment: SegmentConfig) -> bool:
        self.reporter.segment_start(index, segment)

        # Cross-segment convergence: warn if prior segments touched same files
        await self._inject_file_overlap_warning(segment)

        # Phase 1: Ship loop (code → preflight → ship → verify)
        self._set_segment_status(segment, SegmentStatus.CODING)
        self.db.emit_event(self.run_id, segment.name, "agent_started")

        ship_result = await run_ship_loop(
            self.config, segment, index,
            self.reporter, self.budget, self.learnings,
        )

        verdict = self._assess_ship_verdict(ship_result)
        action = self.router.route(verdict)
        self.db.emit_event(self.run_id, segment.name, "preflight_passed" if ship_result.success else "preflight_failed",
                           {"verdict": verdict.value, "action": action.value})

        if action == Action.SHIP and ship_result.success:
            # Record touched paths to DB after shipping
            await self._record_touched_paths(segment)
            self.db.emit_event(self.run_id, segment.name, "segment_shipped")
            return self._mark_shipped(index, segment, ship_result)

        if action == Action.FAIL:
            self.db.emit_event(self.run_id, segment.name, "segment_failed", {"reason": verdict.value})
            return self._mark_failed(index, segment, ship_result)

        if action == Action.PAUSE_AND_ALERT:
            self.learnings.record_decision_gap(
                segment=segment.name,
                context=f"Unexpected verdict: {verdict.value}",
                verdict=verdict.value,
                run_id=self.run_id,
            )
            self.db.emit_event(self.run_id, segment.name, "segment_failed", {"reason": "pause_and_alert"})
            return self._mark_failed(index, segment, ship_result)

        # Phase 2: Repair loop (preflight failed or converged)
        self._set_segment_status(segment, SegmentStatus.REPAIRING)
        self.reporter._print("   ❌ Preflight FAILED — entering repair loop")

        preflight_result = ship_result.preflight_result
        repair_result = await run_repair_loop(
            self.config, segment.name, preflight_result,
            self.reporter, self.budget, self.learnings,
            run_id=self.run_id,
        )

        if repair_result.success:
            self.db.emit_event(self.run_id, segment.name, "repair_done", {"attempts": repair_result.attempts_used})

            repair_diff = await get_diff(Path(self.config.repo))
            repair_diff_stat = await get_diff_stat(Path(self.config.repo))
            repair_diff_lines = len(repair_diff_stat.strip().splitlines()) if repair_diff_stat.strip() else 0

            self._set_segment_status(segment, SegmentStatus.SHIPPING)
            ship_result = await self._ship_and_verify(segment)
            if ship_result.success:
                await self._record_touched_paths(segment)
                self.db.emit_event(self.run_id, segment.name, "segment_shipped")
                result = self._mark_shipped(index, segment, ship_result)

                task = asyncio.create_task(self._run_optimization(
                    segment, preflight_result.combined_output,
                    repair_diff, repair_result.attempts_used, repair_diff_lines,
                ))
                self._optimization_tasks.append(task)

                return result

            self.db.emit_event(self.run_id, segment.name, "deploy_failed")
            return self._mark_failed(index, segment, ship_result)

        # Check if converged — route through verdict router
        if repair_result.converged:
            repair_verdict = Verdict.CONVERGED
        else:
            repair_verdict = Verdict.REPAIR_EXHAUSTED

        repair_action = self.router.route(repair_verdict)
        self.db.emit_event(self.run_id, segment.name, "repair_failed",
                           {"verdict": repair_verdict.value, "action": repair_action.value})

        if repair_action == Action.FAIL:
            return self._mark_failed(index, segment, ship_result)

        # Phase 3: Meta loop (repair exhausted / converged)
        self._set_segment_status(segment, SegmentStatus.EXPERIMENTING)
        all_errors = [preflight_result.combined_output]

        meta_result = await run_meta_loop(
            self.config, segment.name, segment.prompt,
            all_errors, self.reporter, self.budget, self.learnings,
        )

        if meta_result.success:
            self.db.emit_event(self.run_id, segment.name, "meta_done",
                               {"winner": meta_result.winner_experiment})
            self._set_segment_status(segment, SegmentStatus.SHIPPING)
            ship_result = await self._ship_and_verify(segment)
            if ship_result.success:
                await self._record_touched_paths(segment)
                self.db.emit_event(self.run_id, segment.name, "segment_shipped")
                return self._mark_shipped(index, segment, ship_result)
            self.db.emit_event(self.run_id, segment.name, "deploy_failed")
            return self._mark_failed(index, segment, ship_result)

        self.db.emit_event(self.run_id, segment.name, "segment_failed", {"reason": "all_loops_exhausted"})
        return self._mark_failed(index, segment, ShipResult(success=False, report=SegmentReport(
            name=segment.name, status="failed",
            repair_attempts=repair_result.attempts_used,
            meta_experiments=meta_result.experiments_tried,
            errors=["All loops exhausted"],
        )))

    def _assess_ship_verdict(self, ship_result: ShipResult) -> Verdict:
        """Translate ShipResult into a Verdict for routing."""
        if ship_result.success:
            return Verdict.SUCCESS

        report = ship_result.report
        if report and report.errors:
            first_error = report.errors[0]
            if "Agent failed" in first_error:
                return Verdict.AGENT_FAIL
            if "no file changes" in first_error.lower():
                return Verdict.NO_CHANGES
            if "Budget exceeded" in first_error:
                return Verdict.BUDGET_EXCEEDED

        # Preflight failure — repair loop territory
        if ship_result.preflight_result and not ship_result.preflight_result.passed:
            return Verdict.PREFLIGHT_FAIL

        return Verdict.UNKNOWN

    async def _inject_file_overlap_warning(self, segment: SegmentConfig) -> None:
        """Check if any shipped segments touched the same files and inject a warning."""
        shipped_paths = self.db.get_all_shipped_touched_paths(self.run_id)
        if not shipped_paths:
            return

        # We don't have touched_paths for this segment yet (it hasn't run), but we
        # can check if any prior touched paths seem relevant based on segment name.
        # The actual injection happens inside run_ship_loop via the augmented prompt.
        # Here we just log warnings and store them for the agent to see.
        overlapping: dict[str, list[str]] = {}
        for other_name, paths in shipped_paths.items():
            if other_name != segment.name and paths:
                overlapping[other_name] = paths

        if overlapping:
            # Store overlap warning as an event — run_ship_loop can pick it up
            self.db.emit_event(
                self.run_id, segment.name, "file_overlap_warning",
                {"overlapping_segments": {k: v[:10] for k, v in overlapping.items()}},
            )
            logger.debug(
                "Segment '%s' may overlap with: %s",
                segment.name, list(overlapping.keys()),
            )

    async def _record_touched_paths(self, segment: SegmentConfig) -> None:
        """Record files touched by the latest commit into the DB."""
        try:
            touched = await get_touched_paths(self.repo)
            self.db.update_segment_ship_info(
                run_id=self.run_id,
                name=segment.name,
                commit_sha=segment.commit or "",
                tag=segment.tag or "",
                deploy_url=segment.deploy_url or "",
                touched_paths=touched,
            )
        except Exception as e:
            logger.warning("Failed to record touched paths for '%s': %s", segment.name, e)

    async def _ship_and_verify(self, segment: SegmentConfig) -> ShipResult:
        from .ship_utils import ship_and_verify

        repo = Path(self.config.repo)
        sv_result = await ship_and_verify(self.config, segment, repo, self.reporter)

        if sv_result.success:
            return ShipResult(
                success=True, commit_sha=sv_result.commit_sha, tag=sv_result.tag,
                deploy_url=sv_result.deploy_url,
                report=SegmentReport(
                    name=segment.name, status="shipped",
                    commit=sv_result.commit_sha, tag=sv_result.tag,
                    deploy_url=sv_result.deploy_url,
                ),
            )

        return ShipResult(success=False, commit_sha=sv_result.commit_sha, tag=sv_result.tag, report=SegmentReport(
            name=segment.name, status="failed",
            errors=[sv_result.error or "Ship and verify failed"],
        ))

    def _mark_shipped(self, index: int, segment: SegmentConfig, result: ShipResult) -> bool:
        segment.commit = result.commit_sha
        segment.tag = result.tag
        segment.deploy_url = result.deploy_url
        self._set_segment_status(segment, SegmentStatus.SHIPPED)

        report = result.report or SegmentReport(
            name=segment.name, status="shipped",
            commit=result.commit_sha, tag=result.tag,
            cost_usd=self.budget.get_segment_cost(segment.name),
        )
        report.cost_usd = self.budget.get_segment_cost(segment.name)
        self.reporter.segment_shipped(index, report)
        return True

    def _mark_failed(self, index: int, segment: SegmentConfig, result: ShipResult) -> bool:
        self._set_segment_status(segment, SegmentStatus.FAILED)

        report = result.report or SegmentReport(name=segment.name, status="failed")
        self.reporter.segment_failed(index, report)
        return False

    async def _run_optimization(
        self,
        segment: SegmentConfig,
        preflight_error: str,
        repair_diff: str,
        repair_attempts: int,
        repair_diff_lines: int,
    ) -> None:
        try:
            await run_optimization_loop(
                self.config,
                segment.name,
                segment.prompt,
                preflight_error,
                repair_diff,
                repair_attempts,
                repair_diff_lines,
                self.reporter,
                self.budget,
                self.learnings,
            )
        except Exception as e:
            logger.error("Optimization for '%s' failed: %s", segment.name, e)

    async def _auto_reflect(self) -> None:
        """Run the meta-reflection loop if auto_run is enabled."""
        try:
            from .loops.reflect import run_reflect_loop
            depth = self.config.reflection.history_depth
            report = await run_reflect_loop(self.db, depth=depth)
            if report.recommendations:
                self.reporter._print("\n🪞 Reflection complete — recommendations generated")
        except Exception as e:
            logger.warning("Auto-reflect failed: %s", e)

    def get_status(self) -> list[dict]:
        return [
            {
                "name": seg.name,
                "status": seg.status.value,
                "commit": seg.commit,
                "tag": seg.tag,
                "deploy_url": seg.deploy_url,
                "depends_on": seg.depends_on,
            }
            for seg in self.config.segments
        ]

    def reset_segment(self, segment_name: str) -> bool:
        for seg in self.config.segments:
            if seg.name == segment_name:
                seg.status = SegmentStatus.PENDING
                seg.commit = None
                seg.tag = None
                seg.deploy_url = None
                self._checkpoint()
                return True
        return False
