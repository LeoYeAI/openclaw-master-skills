#!/usr/bin/env python3
"""
build_push.py — Build the Nova app Docker image and push it to a registry.

Usage:
    python3 scripts/build_push.py \
        --name my-app \
        --registry docker.io/alice \
        [--tag latest] \
        [--dockerfile ./my-app/Dockerfile] \
        [--context ./my-app]

Requirements:
    - Docker daemon must be running
    - `docker login` must have been run for the target registry

Output:
    Full image reference printed at the end, e.g.:
        docker.io/alice/my-app:latest
    Use this in nova_deploy.py --image
"""

import argparse
import subprocess
import sys


def run(cmd: list[str], step: str) -> None:
    """Run a shell command, stream output, and exit on failure."""
    print(f"\n[{step}] $ {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\n[error] Step '{step}' failed (exit {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)


def build_and_push(name: str, registry: str, tag: str, dockerfile: str, context: str) -> str:
    # Normalise registry: strip trailing slash
    registry = registry.rstrip("/")
    full_image = f"{registry}/{name}:{tag}"

    # ── Build ──────────────────────────────────────────────────────────────────
    run(
        ["docker", "build", "-t", full_image, "-f", dockerfile, context],
        step="docker build",
    )

    # ── Push ───────────────────────────────────────────────────────────────────
    run(["docker", "push", full_image], step="docker push")

    print(f"\n[OK] Image pushed: {full_image}")
    print(f"\n  Use in nova_deploy.py:\n  --image {full_image}\n")

    return full_image


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and push Nova app Docker image")
    parser.add_argument("--name", required=True, help="App name (used as image repo name)")
    parser.add_argument(
        "--registry",
        required=True,
        help="Docker registry prefix, e.g. docker.io/alice or ghcr.io/org",
    )
    parser.add_argument("--tag", default="latest", help="Image tag (default: latest)")
    parser.add_argument(
        "--dockerfile",
        default=None,
        help="Path to Dockerfile (default: <name>/Dockerfile)",
    )
    parser.add_argument(
        "--context",
        default=None,
        help="Docker build context directory (default: <name>/)",
    )
    args = parser.parse_args()

    dockerfile = args.dockerfile or f"{args.name}/Dockerfile"
    context = args.context or args.name

    build_and_push(
        name=args.name,
        registry=args.registry,
        tag=args.tag,
        dockerfile=dockerfile,
        context=context,
    )


if __name__ == "__main__":
    main()
