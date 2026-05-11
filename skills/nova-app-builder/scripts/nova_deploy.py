#!/usr/bin/env python3
"""
nova_deploy.py — Create, build, and deploy a Nova Platform app from a Git repo.

Usage:
    python3 scripts/nova_deploy.py \
        --repo https://github.com/you/my-app \
        --name "My App" \
        --port 8000 \
        --api-key <nova-api-key> \
        [--git-ref main] \
        [--version 1.0.0] \
        [--directory /] \
        [--onchain] \
        [--no-onchain] \
        [--dry-run] \
        [--poll-interval 15] \
        [--timeout 900]

Nova API key:  sparsity.cloud → Account → API Keys → Create
API docs:      https://sparsity.cloud/api/docs

Workflow:
    1. POST /api/apps                         — create app
    2. POST /api/apps/{sqid}/builds           — trigger build from Git
    3. Poll build until success
    4. POST /api/apps/{sqid}/deployments      — deploy the build
    5. Poll deployment until running
    6. (optional, prompted) On-chain registration:
       a. POST /api/apps/{sqid}/create-onchain
       b. POST /api/apps/{sqid}/builds/{id}/enroll
       c. POST /api/zkproof/generate
       d. POST /api/zkproof/onchain/register
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any

import urllib.request
import urllib.error

NOVA_API_BASE = "https://sparsity.cloud/api"


def make_advanced_config(
    port: int,
    directory: str = "/",
    enable_kms: bool = False,
    enable_s3: bool = False,
    enable_wallet: bool = False,
    enable_helios: bool = False,
    helios_chains: list | None = None,
) -> dict:
    return {
        "directory": directory,
        "app_listening_port": port,
        "egress_allow": ["**"],
        "enable_decentralized_kms": enable_kms,
        "enable_persistent_storage": enable_s3,
        "enable_s3_storage": enable_s3,
        "enable_s3_kms_encryption": enable_kms and enable_s3,
        "enable_ipfs_storage": False,
        "enable_walrus_storage": False,
        "enable_app_wallet": enable_wallet,
        "enable_helios_rpc": enable_helios,
        "helios_chains": helios_chains or [
            {"chain_id": "1", "kind": "ethereum", "network": "mainnet",
             "execution_rpc": "", "local_rpc_port": 18545}
        ],
    }


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _request(method: str, path: str, api_key: str, body: dict | None = None) -> dict:
    url = f"{NOVA_API_BASE}{path}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {e.code} {e.reason} → {url}\n{body_text}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error → {url}: {e.reason}") from e


def _post(path: str, api_key: str, body: dict | None = None) -> dict:
    return _request("POST", path, api_key, body)


def _get(path: str, api_key: str) -> dict:
    return _request("GET", path, api_key)


# ── URL extraction ────────────────────────────────────────────────────────────

def _normalize_url(url: str) -> str:
    """Ensure URL has https:// prefix and no trailing slash."""
    if not url:
        return ""
    if not url.startswith("http"):
        url = f"https://{url}"
    return url.rstrip("/")


def get_app_url(sqid: str, api_key: str) -> str:
    """Read the live URL from GET /apps/{sqid}/detail.
    Priority: deployments[0].enclave_info.instance_url
           → deployments[0].hostname
           → app.enclave_info.instance_url
           → app.hostname
    """
    detail = _get(f"/apps/{sqid}/detail", api_key)
    # Try deployments list first (most accurate for running instance)
    for d in detail.get("deployments", []):
        url = d.get("enclave_info", {}).get("instance_url", "")
        if url:
            return _normalize_url(url)
        h = d.get("hostname", "")
        if h:
            return _normalize_url(h)
    # Fall back to top-level app fields
    app = detail.get("app", {})
    url = app.get("enclave_info", {}).get("instance_url", "")
    if url:
        return _normalize_url(url)
    h = app.get("hostname", "")
    if h:
        return _normalize_url(h)
    return ""


# ── Steps 1–5 ─────────────────────────────────────────────────────────────────

def create_app(name: str, repo_url: str, port: int, directory: str, api_key: str) -> str:
    print(f"[1/4] 📝 Creating app '{name}' ...")
    result = _post("/apps", api_key, {
        "name": name,
        "repo_url": repo_url,
        "advanced": make_advanced_config(port, directory=directory),
    })
    sqid = result.get("sqid")
    if not sqid:
        raise RuntimeError(f"No sqid in create response: {result}")
    print(f"      ✓ App sqid: {sqid}")
    return sqid


def trigger_build(sqid: str, git_ref: str, version: str, api_key: str) -> int:
    print(f"[2/4] 🔨 Triggering build (ref={git_ref}, version={version}) ...")
    result = _post(f"/apps/{sqid}/builds", api_key, {"git_ref": git_ref, "version": version})
    build_id = result.get("id")
    if not build_id:
        raise RuntimeError(f"No build id in response: {result}")
    print(f"      ✓ Build ID: {build_id}")
    return build_id


def wait_for_build(build_id: int, api_key: str, poll_interval: int, timeout: int) -> None:
    print(f"      ⏳ Building ...")
    deadline = time.time() + timeout
    dots = 0
    while time.time() < deadline:
        try:
            data = _get(f"/builds/{build_id}/status", api_key)
        except RuntimeError as exc:
            print(f"\n      [warn] {exc} — retrying ...")
            time.sleep(poll_interval)
            continue
        status = (data.get("status") or "unknown").lower()
        print(f"  [{('.' * (dots % 20)):.<20}] build={status}", end="\r")
        dots += 1
        if status == "success":
            print()
            print("      ✓ Build succeeded")
            return
        if status == "failed":
            print()
            err = data.get("error_message", "")
            hint = ""
            if "dockerfile" in err.lower():
                hint = "\n  Hint: Ensure Dockerfile exists at the repo root (or set --directory)"
            elif "port" in err.lower():
                hint = "\n  Hint: Check EXPOSE in Dockerfile matches --port"
            raise RuntimeError(f"Build failed: {err}{hint}")
        time.sleep(poll_interval)
    raise TimeoutError(f"Build {build_id} timed out after {timeout}s.")


def create_deployment(sqid: str, build_id: int, api_key: str) -> int:
    print(f"[3/4] 🚀 Deploying build {build_id} ...")
    result = _post(f"/apps/{sqid}/deployments", api_key, {"build_id": build_id})
    deploy_id = result.get("id")
    if not deploy_id:
        raise RuntimeError(f"No deployment id in response: {result}")
    print(f"      ✓ Deployment ID: {deploy_id}")
    return deploy_id


def wait_for_deployment(deploy_id: int, sqid: str, api_key: str, poll_interval: int, timeout: int) -> str:
    print(f"      ⏳ Waiting for running ...")
    deadline = time.time() + timeout
    last_state = ""
    while time.time() < deadline:
        try:
            data = _get(f"/deployments/{deploy_id}/status", api_key)
        except RuntimeError as exc:
            print(f"\n      [warn] {exc} — retrying ...")
            time.sleep(poll_interval)
            continue
        state = (data.get("deployment_state") or "unknown").lower()
        if state != last_state:
            print(f"\n      → {state}", end="", flush=True)
            last_state = state
        else:
            print(".", end="", flush=True)
        if state == "running":
            print()
            try:
                return get_app_url(sqid, api_key)
            except Exception:
                return ""
        if state in ("failed", "error"):
            print()
            msg = data.get("deployment_message", "")
            hint = ""
            if "port" in msg.lower():
                hint = "\n  Hint: Port mismatch — ensure app listens on --port and Dockerfile EXPOSEs same port"
            raise RuntimeError(f"Deployment failed (state={state}): {msg}{hint}")
        time.sleep(poll_interval)
    raise TimeoutError(f"Deployment timed out after {timeout}s.")


# ── Step 6: On-Chain Registration ─────────────────────────────────────────────

def register_onchain(sqid: str, build_id: int, deploy_id: int, api_key: str, poll_interval: int, timeout: int) -> None:
    print("\n[6a] ⛓️  Creating app on-chain ...")
    _post(f"/apps/{sqid}/create-onchain", api_key)
    deadline = time.time() + timeout
    while time.time() < deadline:
        data = _get(f"/apps/{sqid}/status", api_key)
        onchain_app_id = data.get("onchain_app_id")
        print(f"      onchain_app_id={onchain_app_id}", end="\r")
        if onchain_app_id:
            explorer_url = f"https://sparsity.cloud/explore/{onchain_app_id}"
            print(f"\n      ✓ On-chain app ID: {onchain_app_id}")
            print(f"        Explorer: {explorer_url}")
            break
        time.sleep(poll_interval)
    else:
        raise TimeoutError("create-onchain timed out.")

    print("\n[6b] ⛓️  Enrolling build version on-chain ...")
    _post(f"/apps/{sqid}/builds/{build_id}/enroll", api_key)
    deadline = time.time() + timeout
    while time.time() < deadline:
        data = _get(f"/builds/{build_id}/status", api_key)
        enrolled = data.get("is_enrolled")
        print(f"      is_enrolled={enrolled}", end="\r")
        if str(enrolled).lower() == "true":
            print("\n      ✓ Build enrolled")
            break
        time.sleep(poll_interval)
    else:
        raise TimeoutError("Enroll timed out.")

    print("\n[6c] ⛓️  Generating ZK proof ...")
    _post("/zkproof/generate", api_key, {"deployment_id": deploy_id})
    deadline = time.time() + timeout
    while time.time() < deadline:
        data = _get(f"/deployments/{deploy_id}/status", api_key)
        proof = (data.get("proof_status") or "").lower()
        print(f"      proof_status={proof}", end="\r")
        if proof == "proved":
            print("\n      ✓ ZK proof generated")
            break
        if proof == "failed":
            print()
            raise RuntimeError(
                "ZK proof generation failed.\n"
                f"  Check status at: {NOVA_API_BASE}/zkproof/status/{deploy_id}"
            )
        time.sleep(poll_interval)
    else:
        raise TimeoutError("ZK proof timed out.")

    print("\n[6d] ⛓️  Registering instance on-chain ...")
    _post("/zkproof/onchain/register", api_key, {"deployment_id": deploy_id})
    deadline = time.time() + timeout
    while time.time() < deadline:
        data = _get(f"/deployments/{deploy_id}/status", api_key)
        instance_id = data.get("onchain_instance_id")
        print(f"      onchain_instance_id={instance_id}", end="\r")
        if instance_id:
            print(f"\n      ✓ On-chain instance ID: {instance_id}")
            return
        time.sleep(poll_interval)
    raise TimeoutError("On-chain registration timed out.")


# ── Interactive prompt ────────────────────────────────────────────────────────

def ask_onchain() -> bool:
    print("\nOn-chain registration establishes verifiable trust:")
    print("  6a. Register app in Nova App Registry (Base Sepolia)")
    print("  6b. Record EIF PCR measurements on-chain")
    print("  6c. Generate ZK proof from enclave attestation")
    print("  6d. Link live instance to enrolled build on-chain")
    print()
    try:
        answer = input("Run on-chain registration? [y/N]: ").strip().lower()
        return answer in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create, build, and deploy a Nova Platform app from Git"
    )
    parser.add_argument("--repo", required=True, help="Git repo URL")
    parser.add_argument("--name", required=True, help="App display name")
    parser.add_argument("--port", type=int, default=8000, help="App listening port (default: 8000)")
    parser.add_argument("--git-ref", default="main", help="Branch, tag, or commit SHA (default: main)")
    parser.add_argument("--version", default="1.0.0", help="Semver version (default: 1.0.0)")
    parser.add_argument("--directory", default="/", help="Subdirectory with Dockerfile (default: /)")
    parser.add_argument("--api-key", required=True, help="Nova Platform API key")
    parser.add_argument("--onchain", action="store_true", help="Run on-chain registration (skip prompt)")
    parser.add_argument("--no-onchain", action="store_true", help="Skip on-chain registration (skip prompt)")
    parser.add_argument("--dry-run", action="store_true", help="Print config and exit without deploying")
    parser.add_argument("--poll-interval", type=int, default=15, help="Poll interval in seconds (default: 15)")
    parser.add_argument("--timeout", type=int, default=900, help="Total timeout in seconds (default: 900)")
    args = parser.parse_args()

    advanced = make_advanced_config(args.port, directory=args.directory)

    if args.dry_run:
        print("=== Dry Run — no changes will be made ===")
        print(f"  App name   : {args.name}")
        print(f"  Repo       : {args.repo}")
        print(f"  Git ref    : {args.git_ref}")
        print(f"  Version    : {args.version}")
        print(f"  Port       : {args.port}")
        print(f"  Directory  : {args.directory}")
        print(f"  On-chain   : {'yes' if args.onchain else 'no' if args.no_onchain else 'prompt'}")
        print(f"  Advanced   :")
        print(json.dumps(advanced, indent=4))
        return

    try:
        sqid = create_app(args.name, args.repo, args.port, args.directory, args.api_key)
        build_id = trigger_build(sqid, args.git_ref, args.version, args.api_key)
        wait_for_build(build_id, args.api_key, args.poll_interval, args.timeout)
        deploy_id = create_deployment(sqid, build_id, args.api_key)
        app_url = wait_for_deployment(deploy_id, sqid, args.api_key, args.poll_interval, args.timeout)

        print(f"""
╔══════════════════════════════════════════════════════════════╗
║  🎉 Nova App is LIVE                                         ║
╠══════════════════════════════════════════════════════════════╣
║  App sqid    : {sqid:<46}║
║  Build ID    : {str(build_id):<46}║
║  Deploy ID   : {str(deploy_id):<46}║
║  URL         : {app_url:<46}║
╚══════════════════════════════════════════════════════════════╝
""")

        if args.no_onchain:
            run_onchain = False
        elif args.onchain:
            run_onchain = True
        else:
            run_onchain = ask_onchain()

        if run_onchain:
            register_onchain(sqid, build_id, deploy_id, args.api_key, args.poll_interval, args.timeout)
            # Fetch final on-chain IDs for the summary
            try:
                status = _get(f"/apps/{sqid}/status", args.api_key)
                onchain_app_id = status.get("onchain_app_id", "")
                onchain_instance_id = status.get("latest_onchain_instance_id", "")
            except Exception:
                onchain_app_id = ""
                onchain_instance_id = ""
            print("\n✅  On-chain registration complete.")
            if onchain_app_id:
                print(f"    Explorer: https://sparsity.cloud/explore/{onchain_app_id}")
        else:
            print("Skipped on-chain registration.")

        if app_url:
            print(f"\nVerify:\n  curl {app_url}/\n  curl {app_url}/api/hello\n  curl -X POST {app_url}/.well-known/attestation\n")

    except (RuntimeError, TimeoutError) as exc:
        print(f"\n[error] {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[cancelled]")
        sys.exit(0)


if __name__ == "__main__":
    main()
