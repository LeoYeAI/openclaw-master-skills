#!/usr/bin/env python3
"""Dependency-free synthetic Gymnasium-style environment template.

This module is intentionally local and synthetic. It does not import PufferLib,
Gymnasium, environment plug-ins, native extensions, or ROMs. Port the contract
to a separately reviewed Gymnasium or PufferLib environment only after the
validator passes.
"""

from __future__ import annotations

import argparse
import math
import random
from dataclasses import dataclass
from typing import Any

try:
    from ._common import UserInputError, bounded_int, emit_json
except ImportError:  # Direct script execution.
    from _common import UserInputError, bounded_int, emit_json


@dataclass(frozen=True)
class DiscreteSpace:
    """Minimal stand-in for a discrete action space."""

    n: int

    @property
    def shape(self) -> tuple[int, ...]:
        return ()

    def contains(self, value: Any) -> bool:
        return isinstance(value, int) and not isinstance(value, bool) and 0 <= value < self.n

    def sample(self, rng: random.Random) -> int:
        return rng.randrange(self.n)


@dataclass(frozen=True)
class BoxSpace:
    """Minimal one-dimensional finite box used by the synthetic environment."""

    low: float
    high: float
    shape: tuple[int, ...]
    dtype: str = "float32"

    def contains(self, value: Any) -> bool:
        if len(self.shape) != 1 or not isinstance(value, (list, tuple)):
            return False
        if len(value) != self.shape[0]:
            return False
        for item in value:
            if isinstance(item, bool) or not isinstance(item, (int, float)):
                return False
            if not math.isfinite(float(item)) or not self.low <= float(item) <= self.high:
                return False
        return True


class SyntheticGymEnv:
    """Small deterministic environment implementing Gymnasium's five-tuple API."""

    metadata = {"render_modes": []}

    def __init__(self, *, max_steps: int = 16) -> None:
        if not 1 <= max_steps <= 10_000:
            raise UserInputError("max_steps must be between 1 and 10000")
        self.max_steps = max_steps
        self.observation_space = BoxSpace(-1.0, 1.0, (4,))
        self.action_space = DiscreteSpace(3)
        self._rng = random.Random()
        self._initialized = False
        self._done = False
        self._position = 0.0
        self._target = 0.75
        self._step_count = 0
        self._last_action = 0.0

    def _observation(self) -> list[float]:
        return [
            float(self._position),
            float(self._target),
            float(self._step_count / self.max_steps),
            float(self._last_action),
        ]

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[list[float], dict[str, Any]]:
        """Reset state and return ``(observation, info)``."""
        if seed is not None:
            self._rng.seed(seed)
        if options is not None and set(options) - {"position", "target"}:
            raise UserInputError("reset options may contain only position and target")

        self._position = self._rng.uniform(-0.5, 0.5)
        self._target = self._rng.choice((-0.75, 0.75))
        if options:
            self._position = float(options.get("position", self._position))
            self._target = float(options.get("target", self._target))
        if not -1.0 <= self._position <= 1.0 or not -1.0 <= self._target <= 1.0:
            raise UserInputError("position and target options must be within [-1, 1]")

        self._step_count = 0
        self._last_action = 0.0
        self._initialized = True
        self._done = False
        observation = self._observation()
        return observation, {"seed": seed, "synthetic": True}

    def step(
        self, action: int
    ) -> tuple[list[float], float, bool, bool, dict[str, Any]]:
        """Advance one step and return the Gymnasium five-tuple."""
        if not self._initialized:
            raise RuntimeError("reset() must be called before step()")
        if self._done:
            raise RuntimeError("reset() must be called after termination or truncation")
        if not self.action_space.contains(action):
            raise ValueError(f"action {action!r} is outside the action space")

        movement = (-0.125, 0.0, 0.125)[action]
        self._position = max(-1.0, min(1.0, self._position + movement))
        self._last_action = movement / 0.125
        self._step_count += 1

        distance = abs(self._target - self._position)
        terminated = distance <= 0.0625
        truncated = self._step_count >= self.max_steps and not terminated
        reward = 1.0 if terminated else -distance
        self._done = terminated or truncated
        info = {
            "distance": float(distance),
            "episode_step": self._step_count,
        }
        return self._observation(), float(reward), terminated, truncated, info

    def close(self) -> None:
        self._initialized = False
        self._done = True


def run_demo(*, seed: int, steps: int, max_steps: int) -> dict[str, Any]:
    """Run a bounded deterministic rollout for documentation and smoke tests."""
    env = SyntheticGymEnv(max_steps=max_steps)
    action_rng = random.Random(seed + 1)
    observation, _ = env.reset(seed=seed)
    total_reward = 0.0
    resets = 0
    terminated_count = 0
    truncated_count = 0

    for index in range(steps):
        action = env.action_space.sample(action_rng)
        observation, reward, terminated, truncated, _ = env.step(action)
        total_reward += reward
        terminated_count += int(terminated)
        truncated_count += int(truncated)
        if terminated or truncated:
            resets += 1
            observation, _ = env.reset(seed=seed + resets + index + 1)

    env.close()
    return {
        "environment": "synthetic",
        "last_observation": observation,
        "network_used": False,
        "resets": resets,
        "seed": seed,
        "steps": steps,
        "terminated": terminated_count,
        "total_reward": total_reward,
        "truncated": truncated_count,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the dependency-free synthetic environment template."
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=int, default=16, help="1..10000")
    parser.add_argument("--max-steps", type=int, default=16, help="1..10000")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        steps = bounded_int(args.steps, name="steps", minimum=1, maximum=10_000)
        max_steps = bounded_int(
            args.max_steps, name="max_steps", minimum=1, maximum=10_000
        )
        result = run_demo(seed=args.seed, steps=steps, max_steps=max_steps)
    except (UserInputError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    emit_json(result, pretty=not args.compact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
