from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from common import abs_path, dump_json, run, slugify


DEFAULT_TOPICS = ["chrome-extension", "chrome-web-store"]
DEFAULT_TAGS = ["chrome-extension", "chrome-web-store", "openclaw"]
PUBLIC_SITE_BASE_ENV = "CWS_PUBLIC_SITE_BASE"


def parse_github_owner(repo_root: Path) -> str | None:
    result = run(["git", "remote", "get-url", "origin"], cwd=repo_root, timeout=10)
    if result.returncode != 0:
        return None
    remote = (result.stdout or "").strip()
    if remote.startswith("git@github.com:"):
        owner_repo = remote.split(":", 1)[1]
    elif "github.com/" in remote:
        owner_repo = remote.split("github.com/", 1)[1]
    else:
        return None
    owner = owner_repo.split("/", 1)[0]
    return owner or None


def read_extension_manifest(repo_root: Path, extension_manifest: str | None) -> dict:
    manifest_path = abs_path(extension_manifest) if extension_manifest else repo_root / "extension" / "manifest.json"
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def resolve_public_site_base(explicit_base: str | None) -> str | None:
    raw_value = (explicit_base or os.environ.get(PUBLIC_SITE_BASE_ENV, "")).strip()
    if not raw_value:
        return None
    return raw_value.rstrip("/") + "/"


def detect_reviewer_gate(repo_root: Path) -> dict[str, str | bool]:
    script_path = repo_root / "scripts" / "reviewer_gate.py"
    hook_path = repo_root / ".githooks" / "pre-push"
    return {
        "detected": script_path.exists() or hook_path.exists(),
        "script": "scripts/reviewer_gate.py" if script_path.exists() else "",
        "pre_push_hook": ".githooks/pre-push" if hook_path.exists() else "",
    }


def build_launch_manifest(
    repo_root: Path,
    *,
    owner: str | None,
    extension_manifest: str | None,
    clawhub_slug: str | None,
    clawhub_name: str | None,
    github_description: str | None,
    github_homepage: str | None,
    public_site_base: str | None,
    topics: list[str] | None,
    tags: list[str] | None,
) -> dict:
    manifest = read_extension_manifest(repo_root, extension_manifest)
    repo_name = repo_root.name
    extension_name = manifest["name"]
    repo_owner = owner or parse_github_owner(repo_root) or "example-org"
    repo_url = f"https://github.com/{repo_owner}/{repo_name}"
    public_base = resolve_public_site_base(public_site_base)
    support_url = f"{public_base}support/" if public_base else f"{repo_url}/issues"
    privacy_policy_url = (
        f"{public_base}privacy/" if public_base else f"{repo_url}/blob/main/docs/privacy-policy.md"
    )
    test_instructions_url = (
        f"{public_base}support/#reviewer-checklist"
        if public_base
        else f"{repo_url}/blob/main/docs/test-instructions.md"
    )
    payload = {
        "repo_owner": repo_owner,
        "repo_name": repo_name,
        "repo_url": repo_url,
        "github_description": github_description
        or f"Package, scan, and release {extension_name} for the Chrome Web Store.",
        "github_homepage": github_homepage or repo_url,
        "support_url": support_url,
        "privacy_policy_url": privacy_policy_url,
        "test_instructions_url": test_instructions_url,
        "github_topics": topics or DEFAULT_TOPICS,
        "reviewer_gate": detect_reviewer_gate(repo_root),
        "extension": {
            "name": extension_name,
            "version": manifest["version"],
            "summary": manifest["description"],
            "category": "Tools",
            "chrome_min_version": manifest.get("minimum_chrome_version", ""),
        },
        "release": {
            "tag": f"v{manifest['version']}",
            "title": f"Release {extension_name} v{manifest['version']}",
        },
        "project_slug": slugify(extension_name),
    }
    if clawhub_slug:
        payload["clawhub"] = {
            "slug": clawhub_slug,
            "name": clawhub_name or extension_name,
            "version": manifest["version"],
            "description": f"Release helper and metadata surface for {extension_name}.",
            "tags": tags or DEFAULT_TAGS,
        }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate GitHub and optional ClawHub release metadata from an extension manifest.")
    parser.add_argument("--repo-root", default=".", help="Project root.")
    parser.add_argument("--owner", help="GitHub owner or org. Defaults to the origin remote owner when available.")
    parser.add_argument("--extension-manifest", help="Path to the target extension manifest. Defaults to <repo>/extension/manifest.json.")
    parser.add_argument("--clawhub-slug", help="Optional ClawHub slug for the target public skill.")
    parser.add_argument("--clawhub-name", help="Optional ClawHub display name.")
    parser.add_argument("--github-description", help="Optional GitHub repo description override.")
    parser.add_argument("--github-homepage", help="Optional GitHub homepage override.")
    parser.add_argument(
        "--public-site-base",
        help=(
            "Optional public site base URL for reviewer-facing support/privacy pages. "
            f"Defaults to ${PUBLIC_SITE_BASE_ENV} when set."
        ),
    )
    parser.add_argument("--topic", action="append", dest="topics", help="Repeatable GitHub topic. Defaults to chrome-extension and chrome-web-store.")
    parser.add_argument("--tag", action="append", dest="tags", help="Repeatable ClawHub tag. Defaults to chrome-extension, chrome-web-store, and openclaw.")
    parser.add_argument("--out", required=True, help="Output JSON path.")
    args = parser.parse_args()

    repo_root = abs_path(args.repo_root)
    payload = build_launch_manifest(
        repo_root,
        owner=args.owner,
        extension_manifest=args.extension_manifest,
        clawhub_slug=args.clawhub_slug,
        clawhub_name=args.clawhub_name,
        github_description=args.github_description,
        github_homepage=args.github_homepage,
        public_site_base=args.public_site_base,
        topics=args.topics,
        tags=args.tags,
    )
    dump_json(args.out, payload)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
