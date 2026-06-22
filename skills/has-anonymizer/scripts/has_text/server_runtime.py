#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""On-demand llama-server management for has_text commands."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from typing import Optional
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

from .client import DEFAULT_SERVER, HaSClient

DEFAULT_MODEL_PATH = "~/.openclaw/tools/has-anonymizer/models/has_text_model.gguf"
DEFAULT_HEALTH_TIMEOUT_S = 30.0
DEFAULT_CONTEXT_PER_SLOT = 8192
MAX_AUTO_PARALLEL_SLOTS = 4
_LOCAL_HOSTS = {"127.0.0.1", "localhost", "0.0.0.0", "::1", "::"}
_PARALLEL_FLAG_RE = re.compile(r"(?:^|\s)(?:-np|--parallel)(?:=|\s+)(-?\d+)(?=\s|$)")
_CONTEXT_FLAG_RE = re.compile(r"(?:^|\s)(?:-c|--ctx-size)(?:=|\s+)(\d+)(?=\s|$)")


def _verbose_enabled() -> bool:
    return os.environ.get("HAS_TEXT_VERBOSE") == "1"


@dataclass(frozen=True)
class RunningServer:
    """Observed state for a local listener bound to the target port."""

    server_url: str
    port: int
    pid: Optional[int]
    command: Optional[str]
    healthy: bool
    matches_has_model: bool
    parallel_slots: Optional[int]
    context_tokens: Optional[int]


@dataclass
class ServerLease:
    """Lease for a reused or newly started llama-server process."""

    server_url: str
    started_pid: Optional[int] = None
    log_path: Optional[str] = None
    _process: Optional[subprocess.Popen] = field(default=None, repr=False)

    def create_client(self) -> HaSClient:
        return HaSClient(self.server_url)

    def close(self) -> None:
        if self._process is None or self.started_pid is None:
            return

        process = self._process
        if process.poll() is not None:
            return

        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)

    def __enter__(self) -> ServerLease:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def default_model_path() -> str:
    """Return the default local HaS model path."""
    return os.path.expanduser(os.environ.get("HAS_TEXT_MODEL_PATH", DEFAULT_MODEL_PATH))


def parse_parallel_slots(command: str) -> Optional[int]:
    """Extract the configured llama-server slot count from a command line."""
    match = _PARALLEL_FLAG_RE.search(command)
    if not match:
        return None
    return int(match.group(1))


def parse_context_size(command: str) -> Optional[int]:
    """Extract the configured llama-server context size from a command line."""
    match = _CONTEXT_FLAG_RE.search(command)
    if not match:
        return None
    return int(match.group(1))


def _is_loopback_host(host: Optional[str]) -> bool:
    return (host or "").lower() in _LOCAL_HOSTS


def _normalized_local_host(host: Optional[str]) -> str:
    normalized = (host or "").lower()
    if normalized in {"", "localhost", "0.0.0.0", "::1", "::"}:
        return "127.0.0.1"
    return normalized


def _parse_port(server_url: str) -> int:
    parsed = urlparse(server_url)
    if parsed.port is None:
        raise ValueError(f"Server URL must include an explicit port: {server_url}")
    return parsed.port


def _with_port(server_url: str, port: int) -> str:
    parsed = urlparse(server_url)
    host = _normalized_local_host(parsed.hostname)
    scheme = parsed.scheme or "http"
    return f"{scheme}://{host}:{port}"


def _healthcheck(server_url: str) -> bool:
    try:
        with urlopen(f"{server_url.rstrip('/')}/health", timeout=2) as response:
            return response.status == 200
    except URLError:
        return False
    except TimeoutError:
        return False


def _listening_pid(port: int) -> Optional[int]:
    if shutil.which("lsof") is None:
        return None

    result = subprocess.run(
        ["lsof", "-tiTCP:%d" % port, "-sTCP:LISTEN"],
        check=False,
        capture_output=True,
        text=True,
    )
    line = result.stdout.strip().splitlines()
    if not line:
        return None
    try:
        return int(line[0].strip())
    except ValueError:
        return None


def _read_process_command(pid: int) -> Optional[str]:
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "command="],
        check=False,
        capture_output=True,
        text=True,
    )
    command = result.stdout.strip()
    return command or None


def inspect_local_server(server_url: str, model_path: Optional[str] = None) -> RunningServer:
    """Inspect the local process currently bound to the target port."""
    resolved_model = os.path.basename(model_path or default_model_path())
    port = _parse_port(server_url)
    pid = _listening_pid(port)
    command = _read_process_command(pid) if pid is not None else None
    healthy = _healthcheck(server_url)
    matches_has_model = bool(
        command
        and "llama-server" in command
        and resolved_model in command
    )
    parallel_slots = parse_parallel_slots(command) if command else None
    context_tokens = parse_context_size(command) if command else None
    return RunningServer(
        server_url=server_url,
        port=port,
        pid=pid,
        command=command,
        healthy=healthy,
        matches_has_model=matches_has_model,
        parallel_slots=parallel_slots,
        context_tokens=context_tokens,
    )


def _target_slots(required_slots: int) -> int:
    """Clamp local auto-managed slot counts to the supported safety ceiling."""
    return min(required_slots, MAX_AUTO_PARALLEL_SLOTS)


def _target_context_tokens(required_slots: int, context_per_slot: int = DEFAULT_CONTEXT_PER_SLOT) -> int:
    """Keep each local auto-managed slot at the requested context budget."""
    return context_per_slot * _target_slots(required_slots)


def _supports_required_slots(observed_slots: Optional[int], required_slots: int) -> bool:
    if observed_slots is None:
        return required_slots <= 1
    if observed_slots < 0:
        return required_slots <= 1
    return observed_slots >= required_slots


def _supports_required_context(
    observed_slots: Optional[int],
    observed_context_tokens: Optional[int],
    context_per_slot: int = DEFAULT_CONTEXT_PER_SLOT,
) -> bool:
    if observed_slots is None or observed_context_tokens is None:
        return False
    if observed_slots <= 0:
        return False
    return observed_context_tokens >= observed_slots * context_per_slot


def _find_free_port(host: str) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


def _start_server(
    server_url: str,
    required_slots: int,
    context_tokens: int,
    model_path: str,
) -> ServerLease:
    if shutil.which("llama-server") is None:
        raise RuntimeError("llama-server was not found in PATH")

    model_file = Path(model_path).expanduser()
    if not model_file.is_file():
        raise RuntimeError(
            f"HaS text model not found at {model_file}. "
            "Install has_text_model.gguf before running has-text."
        )

    parsed = urlparse(server_url)
    bind_host = _normalized_local_host(parsed.hostname)
    port = _parse_port(server_url)
    log_path = f"/tmp/llama-server-{port}.log"
    with open(log_path, "ab") as log_handle:
        process = subprocess.Popen(
            [
                "llama-server",
                "--host",
                bind_host,
                "-m",
                str(model_file),
                "-ngl",
                "999",
                "-c",
                str(context_tokens),
                "-np",
                str(required_slots),
                "-fa",
                "on",
                "-ctk",
                "q8_0",
                "-ctv",
                "q8_0",
                "--port",
                str(port),
            ],
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

    deadline = time.time() + DEFAULT_HEALTH_TIMEOUT_S
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError(
                f"llama-server exited before becoming ready. Check {log_path} for details."
            )
        if _healthcheck(server_url):
            if _verbose_enabled():
                print(
                    f"Started HaS llama-server at {server_url} with {required_slots} slot(s) "
                    f"and context {context_tokens}.",
                    file=sys.stderr,
                )
            return ServerLease(
                server_url=server_url,
                started_pid=process.pid,
                log_path=log_path,
                _process=process,
            )
        time.sleep(0.25)

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)

    raise RuntimeError(
        f"Timed out waiting for llama-server at {server_url}. Check {log_path} for details."
    )


def acquire_server(
    server_url: str = DEFAULT_SERVER,
    *,
    required_slots: int = 1,
    model_path: Optional[str] = None,
    context_per_slot: int = DEFAULT_CONTEXT_PER_SLOT,
) -> ServerLease:
    """Reuse or start a local HaS llama-server for the requested workload."""
    if required_slots < 1:
        raise ValueError("required_slots must be >= 1")

    parsed = urlparse(server_url)
    if not _is_loopback_host(parsed.hostname):
        raise RuntimeError(
            f"has-text only supports local loopback servers for on-device privacy. "
            f"Refusing to connect to non-local URL: {server_url}"
        )

    target_slots = _target_slots(required_slots)
    target_context_tokens = _target_context_tokens(required_slots, context_per_slot)
    target_url = _with_port(server_url, _parse_port(server_url))
    observed = inspect_local_server(target_url, model_path=model_path)
    if (
        observed.pid is not None
        and observed.healthy
        and observed.matches_has_model
        and _supports_required_slots(observed.parallel_slots, target_slots)
        and _supports_required_context(observed.parallel_slots, observed.context_tokens, context_per_slot)
    ):
        if _verbose_enabled():
            print(
                f"Reusing HaS llama-server at {target_url}.",
                file=sys.stderr,
            )
        return ServerLease(server_url=target_url)

    start_url = target_url
    bind_host = _normalized_local_host(parsed.hostname)
    if observed.pid is not None or _port_in_use(bind_host, observed.port):
        next_port = _find_free_port(bind_host)
        start_url = _with_port(target_url, next_port)

    return _start_server(
        start_url,
        required_slots=target_slots,
        context_tokens=target_context_tokens,
        model_path=model_path or default_model_path(),
    )
