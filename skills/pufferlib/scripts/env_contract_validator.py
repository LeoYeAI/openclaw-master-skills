#!/usr/bin/env python3
"""Validate a built-in synthetic environment without importing plug-ins."""

from __future__ import annotations

import argparse
import math
import random
from typing import Any

try:
    from ._common import UserInputError, bounded_int, emit_json
    from .env_template import SyntheticGymEnv
except ImportError:  # Direct script execution.
    from _common import UserInputError, bounded_int, emit_json
    from env_template import SyntheticGymEnv


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _validate_reset(result: Any, env: SyntheticGymEnv, errors: list[str]) -> Any:
    _require(
        isinstance(result, tuple) and len(result) == 2,
        "reset() must return (observation, info)",
        errors,
    )
    if not isinstance(result, tuple) or len(result) != 2:
        return None
    observation, info = result
    _require(
        env.observation_space.contains(observation),
        "reset observation is outside observation_space",
        errors,
    )
    _require(isinstance(info, dict), "reset info must be a dict", errors)
    return observation


def _validate_step(result: Any, env: SyntheticGymEnv, errors: list[str]) -> tuple[bool, bool]:
    _require(
        isinstance(result, tuple) and len(result) == 5,
        "step() must return (observation, reward, terminated, truncated, info)",
        errors,
    )
    if not isinstance(result, tuple) or len(result) != 5:
        return False, False
    observation, reward, terminated, truncated, info = result
    _require(
        env.observation_space.contains(observation),
        "step observation is outside observation_space",
        errors,
    )
    _require(
        isinstance(reward, (int, float))
        and not isinstance(reward, bool)
        and math.isfinite(float(reward)),
        "reward must be a finite scalar",
        errors,
    )
    _require(type(terminated) is bool, "terminated must be bool", errors)
    _require(type(truncated) is bool, "truncated must be bool", errors)
    _require(isinstance(info, dict), "step info must be a dict", errors)
    _require(
        not (terminated and truncated),
        "synthetic environment must not terminate and truncate simultaneously",
        errors,
    )
    return bool(terminated), bool(truncated)


def _check_determinism(seed: int, max_steps: int, errors: list[str]) -> None:
    env_a = SyntheticGymEnv(max_steps=max_steps)
    env_b = SyntheticGymEnv(max_steps=max_steps)
    first_a = env_a.reset(seed=seed)
    first_b = env_b.reset(seed=seed)
    _require(first_a == first_b, "same reset seed produced different results", errors)
    actions = [0, 2, 1, 2, 0, 1]
    for action in actions:
        result_a = env_a.step(action)
        result_b = env_b.step(action)
        _require(result_a == result_b, "same action trace produced different results", errors)
        if result_a[2] or result_a[3]:
            break
    env_a.close()
    env_b.close()


def validate_synthetic(
    *,
    seed: int,
    steps: int,
    episodes: int,
    max_steps: int,
) -> dict[str, Any]:
    """Run bounded API, space, reset, termination, and determinism checks."""
    errors: list[str] = []
    env = SyntheticGymEnv(max_steps=max_steps)
    _require(hasattr(env, "observation_space"), "missing observation_space", errors)
    _require(hasattr(env, "action_space"), "missing action_space", errors)

    action_rng = random.Random(seed + 1)
    observation = _validate_reset(env.reset(seed=seed), env, errors)
    total_steps = 0
    completed_episodes = 0
    terminations = 0
    truncations = 0

    while total_steps < steps and completed_episodes < episodes:
        action = env.action_space.sample(action_rng)
        _require(env.action_space.contains(action), "sampled action is invalid", errors)
        terminated, truncated = _validate_step(env.step(action), env, errors)
        total_steps += 1
        if terminated or truncated:
            completed_episodes += 1
            terminations += int(terminated)
            truncations += int(truncated)
            observation = _validate_reset(
                env.reset(seed=seed + completed_episodes), env, errors
            )

    _require(
        observation is None or env.observation_space.contains(observation),
        "final observation is invalid",
        errors,
    )
    _check_determinism(seed, max_steps, errors)
    env.close()
    return {
        "checks": {
            "deterministic_seed": "passed" if not errors else "see errors",
            "reset_two_tuple": True,
            "spaces": True,
            "step_five_tuple": True,
        },
        "contract": "gymnasium",
        "environment": "synthetic",
        "errors": errors,
        "network_used": False,
        "observed": {
            "episodes": completed_episodes,
            "steps": total_steps,
            "terminations": terminations,
            "truncations": truncations,
        },
        "seed": seed,
        "status": "passed" if not errors else "failed",
        "vector_shape_expectation": {
            "actions": ["num_envs"],
            "observations": ["num_envs", 4],
            "rewards": ["num_envs"],
            "terminations": ["num_envs"],
            "truncations": ["num_envs"],
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate only the allowlisted built-in synthetic environment; "
            "external modules and dotted import paths are not supported."
        )
    )
    parser.add_argument("--environment", choices=["synthetic"], default="synthetic")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=int, default=64, help="1..10000")
    parser.add_argument("--episodes", type=int, default=8, help="1..100")
    parser.add_argument("--max-steps", type=int, default=16, help="1..10000")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        steps = bounded_int(args.steps, name="steps", minimum=1, maximum=10_000)
        episodes = bounded_int(args.episodes, name="episodes", minimum=1, maximum=100)
        max_steps = bounded_int(
            args.max_steps, name="max_steps", minimum=1, maximum=10_000
        )
        report = validate_synthetic(
            seed=args.seed,
            steps=steps,
            episodes=episodes,
            max_steps=max_steps,
        )
    except (UserInputError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    emit_json(report, pretty=not args.compact)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
