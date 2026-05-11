from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Iterable


def abs_path(value: str | Path) -> Path:
    return Path(value).expanduser().resolve()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_json(path: str | Path) -> dict:
    return json.loads(abs_path(path).read_text(encoding="utf-8"))


def dump_json(path: str | Path, payload: object) -> None:
    out = abs_path(path)
    ensure_parent(out)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def dump_text(path: str | Path, text: str) -> None:
    out = abs_path(path)
    ensure_parent(out)
    out.write_text(text.rstrip() + "\n", encoding="utf-8")


def run(
    cmd: list[str],
    *,
    cwd: str | Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int | None = None,
) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    return lowered.strip("-")


def markdown_table(headers: list[str], rows: Iterable[Iterable[str]]) -> str:
    header_line = "| " + " | ".join(headers) + " |"
    divider = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_line, divider, *body])


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Project root. Defaults to cwd.",
    )
    return parser
