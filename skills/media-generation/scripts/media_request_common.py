#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path


def default_config_path():
    return Path(os.environ.get("OPENCLAW_CONFIG", Path.home() / ".openclaw" / "openclaw.json"))


def default_output_dir(kind: str):
    base = Path(os.environ.get("MEDIA_GENERATION_OUTPUT_ROOT", "tmp"))
    return base / kind


def default_mask_dir():
    return default_output_dir("images") / "masks"


def default_outpaint_work_dir():
    return default_output_dir("images") / "outpaint_inputs"


def load_config(config_path: Path):
    config_path = Path(config_path).expanduser()
    if not config_path.exists():
        raise SystemExit(
            "config not found: "
            f"{config_path}\n"
            "Pass --config explicitly or set the OPENCLAW_CONFIG env var. Expected an OpenClaw config with models.providers entries."
        )
    try:
        return json.loads(config_path.read_text()), config_path
    except json.JSONDecodeError as e:
        raise SystemExit(f"invalid JSON in config {config_path}: {e}")


def load_provider(config_path: Path, provider_name: str | None):
    data, resolved_config_path = load_config(config_path)
    providers = data.get("models", {}).get("providers")
    if not isinstance(providers, dict) or not providers:
        raise SystemExit(
            f"no providers found in config: {resolved_config_path}\n"
            "Expected config.models.providers to be a non-empty object."
        )
    if not provider_name:
        provider_name = sorted(providers.keys())[0]
    if provider_name not in providers:
        available = ", ".join(sorted(providers.keys()))
        raise SystemExit(
            f"provider not found: {provider_name}\n"
            f"Config: {resolved_config_path}\n"
            f"Available providers: {available}\n"
            "Pass --provider with one of the available names, or set the OPENCLAW_MEDIA_PROVIDER env var."
        )
    provider = providers[provider_name]
    if not isinstance(provider, dict):
        raise SystemExit(f"provider entry is not an object: {provider_name}")
    missing = [key for key in ("baseUrl", "apiKey") if not provider.get(key)]
    if missing:
        raise SystemExit(
            f"provider is missing required fields: {provider_name} -> {', '.join(missing)}\n"
            "Expected at least baseUrl and apiKey in config.models.providers.<provider>."
        )
    return provider["baseUrl"].rstrip("/"), provider["apiKey"], provider_name


def merge_extra_json(payload: dict, extra_json=None, extra_json_file=None):
    merged = dict(payload)
    if extra_json:
        try:
            extra = json.loads(extra_json)
        except json.JSONDecodeError as e:
            raise SystemExit(f"invalid --extra-json: {e}")
        if not isinstance(extra, dict):
            raise SystemExit("--extra-json must decode to a JSON object")
        merged.update(extra)
    if extra_json_file:
        extra_path = Path(extra_json_file)
        if not extra_path.exists():
            raise SystemExit(f"--extra-json-file not found: {extra_path}")
        try:
            extra = json.loads(extra_path.read_text())
        except json.JSONDecodeError as e:
            raise SystemExit(f"invalid JSON in --extra-json-file {extra_path}: {e}")
        if not isinstance(extra, dict):
            raise SystemExit("--extra-json-file must contain a JSON object")
        merged.update(extra)
    return merged


def extract_first_ref(payload):
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for key in ("url", "path", "b64_json"):
                        if item.get(key):
                            return item[key]
        for key in ("url", "path", "b64_json"):
            if payload.get(key):
                return payload[key]
    return None


def failure_hints(status_code, endpoint, modality):
    hints = []
    if status_code in (401, 403):
        hints.append("check apiKey / auth for the selected provider")
    if status_code == 404:
        hints.append(f"check whether the provider exposes {endpoint} for {modality}")
    if status_code == 400:
        hints.append("check provider-specific payload fields, model name, and extra-json contents")
    if status_code == 415:
        hints.append("check content type expectations for this endpoint")
    if status_code >= 500:
        hints.append("provider-side error; retry later or switch provider/model")
    return hints


def request_exception_hint(exc):
    return (
        f"request failed: {exc}\n"
        "Check baseUrl reachability, endpoint path, network connectivity, and TLS/proxy settings for the selected provider."
    )


def run_fetch_helper(script_dir: Path, response_text: str, out_dir: str, prefix: str, origin: str = None, headers=None):
    helper = script_dir / "fetch_generated_media.py"
    cmd = [
        sys.executable,
        str(helper),
        "--response-text",
        response_text,
        "--out-dir",
        out_dir,
        "--prefix",
        prefix,
    ]
    if origin:
        cmd.extend(["--origin", origin])
    for header in headers or []:
        cmd.extend(["--header", header])
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    lines = [line for line in result.stdout.strip().splitlines() if line.strip()]
    return lines[-1] if lines else None
