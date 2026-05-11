#!/usr/bin/env python3
"""
Nova App Builder — Full Deployment Pipeline

Usage:
    python3 deploy.py \
        --app-dir /path/to/my-app \
        --app-name my-oracle \
        --description "My ETH price oracle" \
        --github-token ghp_xxxx \
        --github-user myusername \
        --nova-key nv_xxxx \
        --port 8000 \
        --version 1.0.0 \
        [--egress "api.binance.com,api.coinbase.com"] \
        [--region us-west-1]

Pipeline:
    1. Create public GitHub repo + push app code
    2. POST /api/apps  →  get app_sqid
    3. POST /api/apps/{sqid}/builds  →  trigger transparent build
    4. Poll build until status=success (2-5 min)
    5. POST /api/apps/{sqid}/deployments  →  launch enclave
    6. Poll deployment until state=running
    7. Print live HTTPS URL
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
import urllib.error
import shutil

NOVA_BASE = "https://sparsity.cloud"
GITHUB_API = "https://api.github.com"
BUILD_POLL_INTERVAL = 15   # seconds
DEPLOY_POLL_INTERVAL = 20  # seconds
BUILD_TIMEOUT = 600        # 10 minutes
DEPLOY_TIMEOUT = 300       # 5 minutes


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def nova_request(method, path, nova_key, body=None):
    url = f"{NOVA_BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("X-API-Key", nova_key)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[nova] {method} {path} → HTTP {e.code}: {body}", file=sys.stderr)
        raise


def github_request(method, path, token, body=None):
    url = f"{GITHUB_API}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[github] {method} {path} → HTTP {e.code}: {body}", file=sys.stderr)
        raise


# ── Step 1: GitHub repo ───────────────────────────────────────────────────────

def create_github_repo(name, description, token):
    """Create a new public GitHub repo. Returns clone URL."""
    print(f"[1/6] Creating GitHub repo: {name} ...")
    try:
        repo = github_request("POST", "/user/repos", token, {
            "name": name,
            "description": description or "",
            "private": False,
            "auto_init": False,
        })
        print(f"      ✓ Created: {repo['html_url']}")
        return repo["clone_url"], repo["html_url"]
    except urllib.error.HTTPError as e:
        if e.code == 422:
            # Repo already exists — get it
            me = github_request("GET", "/user", token)
            username = me["login"]
            repo = github_request("GET", f"/repos/{username}/{name}", token)
            print(f"      ↺ Already exists: {repo['html_url']}")
            return repo["clone_url"], repo["html_url"]
        raise


def push_code_to_github(app_dir, clone_url, token, branch="main"):
    """Init git repo in app_dir and push to GitHub."""
    print(f"[2/6] Pushing code to GitHub ...")

    # Embed token in URL
    auth_url = clone_url.replace("https://", f"https://{token}@")

    with tempfile.TemporaryDirectory() as tmp:
        # Copy app dir contents to tmp
        src = app_dir.rstrip("/")
        dest = tmp

        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dest, item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

        def git(*args):
            result = subprocess.run(
                ["git"] + list(args),
                cwd=dest,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(f"git {' '.join(args)} failed:\n{result.stderr}")
            return result.stdout.strip()

        git("init", "-b", branch)
        git("config", "user.email", "nova-builder@openclaw.ai")
        git("config", "user.name", "Nova App Builder")
        git("add", ".")
        git("commit", "-m", "Initial commit via Nova App Builder")
        git("remote", "add", "origin", auth_url)
        git("push", "-u", "origin", branch)

    print(f"      ✓ Code pushed to {branch}")


# ── Step 2: Create Nova app ───────────────────────────────────────────────────

def create_nova_app(name, description, repo_url, port, egress_hosts, nova_key):
    print(f"[3/6] Creating Nova app: {name} ...")
    payload = {
        "name": name,
        "description": description or "",
        "repo_url": repo_url,
        "enclaver": {
            "ingress_port": port,
            "api_port": 18000,
            "aux_api_port": 18001,
            "memory_mb": 1500,
            "egress_allow": egress_hosts or [],
        },
    }
    app = nova_request("POST", "/api/apps", nova_key, payload)
    sqid = app["sqid"]
    print(f"      ✓ App sqid: {sqid}")
    return sqid


# ── Step 3: Trigger build ─────────────────────────────────────────────────────

def trigger_build(sqid, git_ref, version, nova_key):
    print(f"[4/6] Triggering build (ref={git_ref}, version={version}) ...")
    build = nova_request("POST", f"/api/apps/{sqid}/builds", nova_key, {
        "git_ref": git_ref,
        "version": version,
    })
    build_id = build["id"]
    run_id = build.get("github_run_id")
    if run_id:
        print(f"      ✓ Build #{build_id} — GitHub Actions: "
              f"https://github.com/sparsity-xyz/sparsity-nova-app-hub/actions/runs/{run_id}")
    else:
        print(f"      ✓ Build #{build_id} started (status: {build['status']})")
    return build_id


def poll_build(sqid, build_id, nova_key):
    print(f"[5/6] Waiting for build to complete ...")
    deadline = time.time() + BUILD_TIMEOUT
    while time.time() < deadline:
        build = nova_request("GET", f"/api/apps/{sqid}/builds/{build_id}", nova_key)
        status = build["status"]
        print(f"      … build status: {status}")
        if status == "success":
            print(f"      ✓ Build succeeded!")
            return build
        if status in ("failed", "cancelled", "error"):
            err = build.get("error_message", "")
            run_id = build.get("github_run_id")
            log_url = (f"https://github.com/sparsity-xyz/sparsity-nova-app-hub/"
                       f"actions/runs/{run_id}") if run_id else "N/A"
            raise RuntimeError(f"Build {status}: {err}\nBuild log: {log_url}")
        time.sleep(BUILD_POLL_INTERVAL)
    raise TimeoutError(f"Build did not complete within {BUILD_TIMEOUT}s")


# ── Step 4: Create + poll deployment ─────────────────────────────────────────

def create_deployment(sqid, build_id, region, cpu, ram_mib, nova_key):
    print(f"[6/6] Creating deployment (region={region}) ...")
    dep = nova_request("POST", f"/api/apps/{sqid}/deployments", nova_key, {
        "build_id": build_id,
        "region": region,
        "cpu": cpu,
        "ram_mib": ram_mib,
    })
    dep_id = dep["id"]
    print(f"      ✓ Deployment #{dep_id} queued (state: {dep['state']})")
    return dep_id


def poll_deployment(sqid, dep_id, nova_key):
    print(f"      Waiting for enclave to start ...")
    deadline = time.time() + DEPLOY_TIMEOUT
    while time.time() < deadline:
        detail = nova_request("GET", f"/api/apps/{sqid}/detail", nova_key)
        deployments = detail.get("deployments", [])
        dep = next((d for d in deployments if d["id"] == dep_id), None)
        if not dep:
            time.sleep(DEPLOY_POLL_INTERVAL)
            continue
        state = dep["state"]
        print(f"      … deployment state: {state}")
        if state == "running":
            return dep
        if state in ("failed", "stopped", "error", "cancelled"):
            msg = dep.get("message", "")
            raise RuntimeError(f"Deployment {state}: {msg}")
        time.sleep(DEPLOY_POLL_INTERVAL)
    raise TimeoutError(f"Deployment did not start within {DEPLOY_TIMEOUT}s")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Deploy a Nova TEE app end-to-end.\n\n"
                    "Credentials can be supplied via flags or environment variables:\n"
                    "  GITHUB_TOKEN  — GitHub personal access token (repo scope)\n"
                    "  GITHUB_USER   — GitHub username\n"
                    "  NOVA_API_KEY  — Nova Platform API key (sparsity.cloud → Account → API Keys)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--app-dir", required=True, help="Path to app source directory")
    parser.add_argument("--app-name", required=True, help="App name (also used as GitHub repo name)")
    parser.add_argument("--description", default="", help="App description")
    parser.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN"),
                        help="GitHub personal access token (repo scope) [env: GITHUB_TOKEN]")
    parser.add_argument("--github-user", default=os.environ.get("GITHUB_USER"),
                        help="GitHub username [env: GITHUB_USER]")
    parser.add_argument("--nova-key", default=os.environ.get("NOVA_API_KEY"),
                        help="Nova Platform API key [env: NOVA_API_KEY]")
    parser.add_argument("--port", type=int, default=8000, help="App listening port (default: 8000)")
    parser.add_argument("--version", default="1.0.0", help="Build version (semver, default: 1.0.0)")
    parser.add_argument("--git-ref", default="main", help="Git branch/tag (default: main)")
    parser.add_argument("--egress", default="", help="Comma-separated egress hostnames")
    parser.add_argument("--region", default="us-west-1", help="Deployment region (default: us-west-1)")
    parser.add_argument("--cpu", type=int, default=2, help="CPU cores (default: 2)")
    parser.add_argument("--ram-mib", type=int, default=4096, help="RAM in MiB (default: 4096)")
    parser.add_argument("--skip-github", action="store_true", help="Skip GitHub step (repo already exists)")
    parser.add_argument("--repo-url", help="Use existing repo URL (requires --skip-github)")
    args = parser.parse_args()

    # Validate required credentials
    missing = []
    if not args.skip_github:
        if not args.github_token:
            missing.append("--github-token / GITHUB_TOKEN (GitHub personal access token, repo scope)")
        if not args.github_user:
            missing.append("--github-user / GITHUB_USER (GitHub username)")
    if not args.nova_key:
        missing.append("--nova-key / NOVA_API_KEY (Nova Platform API key from sparsity.cloud → Account → API Keys)")
    if missing:
        print("Error: Missing required credentials:", file=sys.stderr)
        for m in missing:
            print(f"  • {m}", file=sys.stderr)
        sys.exit(1)

    egress_hosts = [h.strip() for h in args.egress.split(",") if h.strip()]

    # Step 1 & 2: GitHub
    if args.skip_github:
        if not args.repo_url:
            parser.error("--repo-url is required when using --skip-github")
        repo_url = args.repo_url
        repo_html = repo_url
        print(f"[1/6] Skipping GitHub — using: {repo_url}")
        print(f"[2/6] Skipping push — using existing repo")
    else:
        clone_url, repo_html = create_github_repo(
            args.app_name, args.description, args.github_token
        )
        repo_url = f"https://github.com/{args.github_user}/{args.app_name}"
        push_code_to_github(args.app_dir, clone_url, args.github_token, args.git_ref)

    # Step 3: Create Nova app
    sqid = create_nova_app(
        args.app_name, args.description, repo_url,
        args.port, egress_hosts, args.nova_key
    )

    # Step 4: Trigger build
    build_id = trigger_build(sqid, args.git_ref, args.version, args.nova_key)

    # Step 5: Poll build
    build = poll_build(sqid, build_id, args.nova_key)

    # Step 6: Create deployment
    dep_id = create_deployment(sqid, build_id, args.region, args.cpu, args.ram_mib, args.nova_key)

    # Step 7: Poll deployment
    dep = poll_deployment(sqid, dep_id, args.nova_key)

    # Done
    endpoint = dep.get("endpoint") or dep.get("url") or dep.get("subdomain") or "check sparsity.cloud dashboard"
    print()
    print("=" * 60)
    print("🎉 Deployment complete!")
    print(f"   App sqid   : {sqid}")
    print(f"   Build #    : {build_id}")
    print(f"   Deployment : #{dep_id}")
    print(f"   Endpoint   : {endpoint}")
    print(f"   Dashboard  : https://sparsity.cloud/app/{sqid}")
    print(f"   GitHub     : {repo_html}")
    print("=" * 60)


if __name__ == "__main__":
    main()
