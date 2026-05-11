#!/usr/bin/env python3
"""
Unified data collection pipeline for tech-news-digest.

Runs all 6 fetch steps (RSS, Twitter, GitHub, GitHub Trending, Reddit, Web) in parallel,
then merges + deduplicates + scores into a single output JSON.

Replaces the agent's sequential 6-step tool-call loop with one command,
eliminating ~60-120s of LLM round-trip overhead.

Usage:
    python3 run-pipeline.py \
      --defaults <SKILL_DIR>/config/defaults \
      --config <WORKSPACE>/config \
      --hours 48 --freshness pd \
      --archive-dir <WORKSPACE>/archive/tech-news-digest/ \
      --output /tmp/td-merged.json \
      --verbose
"""

import json
import sys
import os
import subprocess
import time
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any

SCRIPTS_DIR = Path(__file__).parent
DEFAULT_TIMEOUT = 180  # per-step timeout in seconds


def setup_logging(verbose: bool) -> logging.Logger:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger(__name__)


def run_step(
    name: str,
    script: str,
    args_list: list,
    output_path: Path,
    timeout: int = DEFAULT_TIMEOUT,
    force: bool = False,
) -> Dict[str, Any]:
    """Run a fetch script as a subprocess, return result metadata."""
    t0 = time.time()
    cmd = [sys.executable, str(SCRIPTS_DIR / script)] + args_list + [
        "--output", str(output_path),
    ]
    if force:
        cmd.append("--force")

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=timeout,
            env=os.environ,
        )
        elapsed = time.time() - t0
        ok = result.returncode == 0

        # Try to read output stats
        count = 0
        if ok and output_path.exists():
            try:
                with open(output_path) as f:
                    data = json.load(f)
                count = (
                    data.get("total_articles")
                    or data.get("total_posts")
                    or data.get("total_releases")
                    or data.get("total_results")
                    or data.get("total")
                    or 0
                )
            except (json.JSONDecodeError, OSError):
                pass

        return {
            "name": name,
            "status": "ok" if ok else "error",
            "elapsed_s": round(elapsed, 1),
            "count": count,
            "stderr_tail": (result.stderr or "").strip().split("\n")[-3:] if not ok else [],
        }

    except subprocess.TimeoutExpired:
        elapsed = time.time() - t0
        return {
            "name": name,
            "status": "timeout",
            "elapsed_s": round(elapsed, 1),
            "count": 0,
            "stderr_tail": [f"Killed after {timeout}s"],
        }
    except Exception as e:
        elapsed = time.time() - t0
        return {
            "name": name,
            "status": "error",
            "elapsed_s": round(elapsed, 1),
            "count": 0,
            "stderr_tail": [str(e)],
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the full tech-news-digest data pipeline in one shot.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--defaults", type=Path, required=True, help="Skill defaults config dir")
    parser.add_argument("--config", type=Path, default=None, help="User config overlay dir")
    parser.add_argument("--hours", type=int, default=48, help="Time window in hours")
    parser.add_argument("--freshness", type=str, default="pd", help="Web search freshness (pd/pw/pm)")
    parser.add_argument("--archive-dir", type=Path, default=None, help="Archive dir for dedup penalty")
    parser.add_argument("--output", "-o", type=Path, default=Path("/tmp/td-merged.json"), help="Final merged output")
    parser.add_argument("--step-timeout", type=int, default=DEFAULT_TIMEOUT, help="Per-step timeout (seconds)")
    parser.add_argument("--twitter-backend", choices=["official", "twitterapiio", "auto"], default=None, help="Twitter API backend to use")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--force", action="store_true", help="Force re-fetch ignoring caches")
    parser.add_argument("--enrich", action="store_true", help="Enable full-text enrichment for top articles")
    parser.add_argument("--skip", type=str, default="", help="Comma-separated list of steps to skip (rss,twitter,github,reddit,web)")
    parser.add_argument("--reuse-dir", type=Path, default=None, help="Reuse existing intermediate directory instead of creating new one")

    args = parser.parse_args()
    logger = setup_logging(args.verbose)

    # Parse --skip into a set
    skip_steps = set(s.strip().lower() for s in args.skip.split(',') if s.strip())

    # Intermediate output paths
    import tempfile
    if args.reuse_dir:
        _run_dir = str(args.reuse_dir)
        os.makedirs(_run_dir, exist_ok=True)
    else:
        _run_dir = tempfile.mkdtemp(prefix="td-pipeline-")
    tmp_rss = Path(_run_dir) / "rss.json"
    tmp_twitter = Path(_run_dir) / "twitter.json"
    tmp_github = Path(_run_dir) / "github.json"
    tmp_trending = Path(_run_dir) / "trending.json"
    tmp_reddit = Path(_run_dir) / "reddit.json"
    tmp_web = Path(_run_dir) / "web.json"
    logger.info(f"📁 Run directory: {_run_dir}")

    # Common args for all fetch scripts
    common = ["--defaults", str(args.defaults)]
    if args.config:
        common += ["--config", str(args.config)]
    common += ["--hours", str(args.hours)]
    verbose_flag = ["--verbose"] if args.verbose else []

    # Define the 5 parallel fetch steps
    steps = [
        ("RSS", "fetch-rss.py", common + verbose_flag, tmp_rss),
        ("Twitter", "fetch-twitter.py", common + verbose_flag + (["--backend", args.twitter_backend] if args.twitter_backend else []), tmp_twitter),
        ("GitHub", "fetch-github.py", common + verbose_flag, tmp_github),
        ("GitHub Trending", "fetch-github.py", ["--trending", "--hours", str(args.hours)] + verbose_flag, tmp_trending),
        ("Reddit", "fetch-reddit.py", common + verbose_flag, tmp_reddit),
        ("Web", "fetch-web.py",
         ["--defaults", str(args.defaults)]
         + (["--config", str(args.config)] if args.config else [])
         + ["--freshness", args.freshness]
         + verbose_flag,
         tmp_web),
    ]

    # Filter steps by --skip and --reuse-dir
    active_steps = []
    for name, script, step_args, out_path in steps:
        step_key = name.lower()
        if step_key in skip_steps:
            logger.info(f"  ⏭️  {name}: skipped (--skip)")
            continue
        if args.reuse_dir and out_path.exists() and not args.force:
            logger.info(f"  ♻️  {name}: reusing existing {out_path}")
            continue
        active_steps.append((name, script, step_args, out_path))

    logger.info(f"🚀 Starting pipeline: {len(active_steps)}/{len(steps)} sources, {args.hours}h window, freshness={args.freshness}")
    t_start = time.time()

    # Phase 1: Parallel fetch
    step_results = []
    if active_steps:
        with ThreadPoolExecutor(max_workers=len(active_steps)) as pool:
            futures = {}
            for name, script, step_args, out_path in active_steps:
                f = pool.submit(run_step, name, script, step_args, out_path, args.step_timeout, args.force)
                futures[f] = name

            for future in as_completed(futures):
                res = future.result()
                step_results.append(res)
                status_icon = {"ok": "✅", "error": "❌", "timeout": "⏰"}.get(res["status"], "?")
                logger.info(f"  {status_icon} {res['name']}: {res['count']} items ({res['elapsed_s']}s)")
                if res["status"] != "ok" and res["stderr_tail"]:
                    for line in res["stderr_tail"]:
                        logger.debug(f"    {line}")

    fetch_elapsed = time.time() - t_start
    logger.info(f"📡 Fetch phase done in {fetch_elapsed:.1f}s")

    # Phase 2: Merge
    logger.info("🔀 Merging & scoring...")
    merge_args = ["--verbose"] if args.verbose else []
    for flag, path in [("--rss", tmp_rss), ("--twitter", tmp_twitter),
                       ("--github", tmp_github), ("--trending", tmp_trending), ("--reddit", tmp_reddit),
                       ("--web", tmp_web)]:
        if path.exists():
            merge_args += [flag, str(path)]
    if args.archive_dir:
        merge_args += ["--archive-dir", str(args.archive_dir)]
    merge_args += ["--output", str(args.output)]

    merge_result = run_step("Merge", "merge-sources.py", merge_args, args.output, timeout=60, force=False)

    # Phase 3: Enrich high-scoring articles with full text
    if merge_result["status"] == "ok" and args.enrich and "enrich" not in skip_steps:
        logger.info("📰 Enriching top articles with full text...")
        enrich_args = ["--input", str(args.output), "--output", str(args.output)]
        enrich_args += ["--verbose"] if args.verbose else []
        enrich_result = run_step("Enrich", "enrich-articles.py", enrich_args, args.output, timeout=120, force=False)
    else:
        enrich_result = {"name": "Enrich", "status": "skipped", "elapsed_s": 0, "count": 0, "stderr_tail": []}

    total_elapsed = time.time() - t_start

    # Summary
    logger.info(f"{'=' * 50}")
    logger.info(f"📊 Pipeline Summary ({total_elapsed:.1f}s total)")
    for r in step_results:
        logger.info(f"   {r['name']:10s} {r['status']:7s} {r['count']:4d} items  {r['elapsed_s']:5.1f}s")
    logger.info(f"   {'Merge':10s} {merge_result['status']:7s} {merge_result.get('count',0):4d} items  {merge_result['elapsed_s']:5.1f}s")
    logger.info(f"   Output: {args.output}")

    if merge_result["status"] != "ok":
        logger.error(f"❌ Merge failed: {merge_result['stderr_tail']}")
        return 1

    # Write pipeline metadata alongside output for agent consumption
    meta = {
        "pipeline_version": "1.0.0",
        "total_elapsed_s": round(total_elapsed, 1),
        "fetch_elapsed_s": round(fetch_elapsed, 1),
        "steps": step_results,
        "merge": merge_result,
        "output": str(args.output),
    }
    meta_path = args.output.with_suffix(".meta.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    if not args.reuse_dir:
        import shutil
        try:
            shutil.rmtree(_run_dir)
            logger.debug(f"Cleaned up {_run_dir}")
        except Exception:
            pass

    logger.info(f"✅ Done → {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
