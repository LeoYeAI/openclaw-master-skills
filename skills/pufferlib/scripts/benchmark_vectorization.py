#!/usr/bin/env python3
"""Bounded synthetic vectorization benchmark with no PufferLib import."""

from __future__ import annotations

import argparse
import multiprocessing as mp
import os
import platform
import statistics
import time
from typing import Any

try:
    from ._common import UserInputError, bounded_int, emit_json
    from .env_template import SyntheticGymEnv
except ImportError:  # Direct script execution.
    from _common import UserInputError, bounded_int, emit_json
    from env_template import SyntheticGymEnv


def _run_partition(payload: tuple[int, int, int, int, int]) -> dict[str, Any]:
    """Run an allowlisted synthetic partition in one process."""
    start_index, num_envs, steps_per_env, seed, max_steps = payload
    agent_steps = 0
    checksum = 0.0
    resets = 0
    for offset in range(num_envs):
        env_index = start_index + offset
        env = SyntheticGymEnv(max_steps=max_steps)
        env.reset(seed=seed + env_index)
        env_resets = 0
        for step_index in range(steps_per_env):
            action = (seed + 17 * env_index + step_index) % env.action_space.n
            observation, reward, terminated, truncated, _ = env.step(action)
            checksum += reward + observation[0] * 1e-6
            agent_steps += 1
            if terminated or truncated:
                env_resets += 1
                resets += 1
                env.reset(seed=seed + env_index + env_resets * 1_000_003)
        env.close()
    return {"agent_steps": agent_steps, "checksum": checksum, "resets": resets}


def _partitions(
    *,
    num_envs: int,
    workers: int,
    steps_per_env: int,
    seed: int,
    max_steps: int,
) -> list[tuple[int, int, int, int, int]]:
    parts: list[tuple[int, int, int, int, int]] = []
    base, remainder = divmod(num_envs, workers)
    start = 0
    for worker_index in range(workers):
        count = base + int(worker_index < remainder)
        if count:
            parts.append((start, count, steps_per_env, seed, max_steps))
            start += count
    return parts


def _summarize(samples: list[float]) -> dict[str, float]:
    ordered = sorted(samples)

    def percentile(fraction: float) -> float:
        index = round((len(ordered) - 1) * fraction)
        return ordered[index]

    return {
        "maximum": max(samples),
        "median": statistics.median(samples),
        "minimum": min(samples),
        "p10": percentile(0.10),
        "p90": percentile(0.90),
    }


def benchmark(
    *,
    backend: str,
    num_envs: int,
    workers: int,
    steps_per_env: int,
    repeats: int,
    warmup_steps: int,
    seed: int,
    max_steps: int,
    start_method: str,
) -> dict[str, Any]:
    """Measure a fixed synthetic workload; never claim upstream PufferLib SPS."""
    workers = min(workers, num_envs)
    payloads = _partitions(
        num_envs=num_envs,
        workers=workers,
        steps_per_env=steps_per_env,
        seed=seed,
        max_steps=max_steps,
    )
    warmup_payloads = _partitions(
        num_envs=num_envs,
        workers=workers,
        steps_per_env=warmup_steps,
        seed=seed,
        max_steps=max_steps,
    )

    elapsed_samples: list[float] = []
    throughput_samples: list[float] = []
    checksums: list[float] = []
    observed_steps: list[int] = []

    pool: Any = None
    try:
        if backend == "multiprocessing":
            context = mp.get_context(start_method)
            pool = context.Pool(processes=workers)
            if warmup_steps:
                pool.map(_run_partition, warmup_payloads)
        elif warmup_steps:
            for payload in warmup_payloads:
                _run_partition(payload)

        for repeat_index in range(repeats):
            adjusted = [
                (start, count, steps, run_seed + repeat_index, limit)
                for start, count, steps, run_seed, limit in payloads
            ]
            started = time.perf_counter()
            if backend == "multiprocessing":
                results = pool.map(_run_partition, adjusted)
            else:
                results = [_run_partition(payload) for payload in adjusted]
            elapsed = time.perf_counter() - started
            agent_steps = sum(int(item["agent_steps"]) for item in results)
            checksum = sum(float(item["checksum"]) for item in results)
            elapsed_samples.append(elapsed)
            throughput_samples.append(agent_steps / elapsed)
            observed_steps.append(agent_steps)
            checksums.append(checksum)
    finally:
        if pool is not None:
            pool.close()
            pool.join()

    return {
        "backend": backend,
        "benchmark": "bundled-synthetic-harness",
        "checksums": checksums,
        "elapsed_seconds": _summarize(elapsed_samples),
        "environment_construction_in_timed_region": True,
        "hardware": {
            "logical_cpus": os.cpu_count(),
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
        "network_used": False,
        "parameters": {
            "max_steps": max_steps,
            "num_envs": num_envs,
            "repeats": repeats,
            "seed": seed,
            "start_method": start_method if backend == "multiprocessing" else None,
            "steps_per_env": steps_per_env,
            "warmup_steps": warmup_steps,
            "workers": workers,
        },
        "steps_per_second": _summarize(throughput_samples),
        "total_agent_steps_per_repeat": observed_steps,
        "warning": (
            "This measures the bundled synthetic harness, not PufferLib, an Ocean "
            "environment, training throughput, or cross-machine performance."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    safe_methods = [method for method in ("spawn", "forkserver") if method in mp.get_all_start_methods()]
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark only the built-in synthetic environment. Defaults are CPU-only, "
            "network-free, and intentionally small."
        )
    )
    parser.add_argument(
        "--backend", choices=["serial", "multiprocessing"], default="serial"
    )
    parser.add_argument("--envs", type=int, default=4, help="1..128")
    parser.add_argument("--workers", type=int, default=2, help="1..32")
    parser.add_argument("--steps-per-env", type=int, default=1_000, help="1..100000")
    parser.add_argument("--repeats", type=int, default=3, help="1..7")
    parser.add_argument("--warmup-steps", type=int, default=32, help="0..1000")
    parser.add_argument("--max-steps", type=int, default=32, help="1..10000")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--start-method",
        choices=safe_methods,
        default="spawn" if "spawn" in safe_methods else safe_methods[0],
        help="fork is intentionally unavailable",
    )
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        num_envs = bounded_int(args.envs, name="envs", minimum=1, maximum=128)
        workers = bounded_int(args.workers, name="workers", minimum=1, maximum=32)
        steps = bounded_int(
            args.steps_per_env,
            name="steps_per_env",
            minimum=1,
            maximum=100_000,
        )
        repeats = bounded_int(args.repeats, name="repeats", minimum=1, maximum=7)
        warmup = bounded_int(
            args.warmup_steps, name="warmup_steps", minimum=0, maximum=1_000
        )
        max_steps = bounded_int(
            args.max_steps, name="max_steps", minimum=1, maximum=10_000
        )
        report = benchmark(
            backend=args.backend,
            num_envs=num_envs,
            workers=workers,
            steps_per_env=steps,
            repeats=repeats,
            warmup_steps=warmup,
            seed=args.seed,
            max_steps=max_steps,
            start_method=args.start_method,
        )
    except (UserInputError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    emit_json(report, pretty=not args.compact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
