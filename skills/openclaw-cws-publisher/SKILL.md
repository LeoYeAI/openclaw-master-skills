---
name: openclaw-cws-publisher
description: OpenClaw CWS Publisher is a public ClawHub Chrome Web Store publisher skill. Use it when the user says "chrome web store publisher", "extension release publisher", "CWS publisher", or wants to package and harden a Chrome extension with CWS package, listing, design, local E2E, latest Chrome, competitor, leak, GitHub, and ClawHub gates.
version: 0.3.2
homepage: https://github.com/zack-dev-cm/openclaw-cws-publisher
license: MIT
user-invocable: true
metadata: {"openclaw":{"homepage":"https://github.com/zack-dev-cm/openclaw-cws-publisher","skillKey":"openclaw-cws-publisher","requires":{"bins":["git","gh","npx"],"anyBins":["python3","python"]},"install":[{"kind":"brew","label":"Install GitHub CLI","formula":"gh","bins":["gh"]}]}}
---

# OpenClaw CWS Publisher

Search intent: `chrome web store publisher`, `extension release publisher`, `cws publisher`, `chrome extension publish`

## Goal

Prepare a Chrome extension repo for release with less metadata drift:

- package the extension
- validate the exact ZIP intended for upload against source manifest and CWS listing copy
- scan tracked and untracked non-ignored files for obvious leak risks
- run local reviewer/E2E gates
- enforce design, UI, screenshot, and claim-alignment score gates
- check current Chrome Stable release data before declaring E2E coverage fresh
- run a lightweight competitor and positioning differentiation check
- detect repo-local reviewer gates
- generate GitHub metadata
- generate optional ClawHub metadata and explicit tags
- render reproducible publish commands

## Use This Skill When

- the user wants a Chrome extension repo prepared for GitHub release
- the user wants CWS ZIP/listing/privacy/design/E2E readiness checked before dashboard submission
- the user wants ClawHub tags and GitHub topics kept in sync
- the user wants a leakage check before public release
- the user already has a specific repo path to release

## Operating Order

1. Build the extension ZIP intended for upload.
   - `python3 {baseDir}/scripts/build_extension_zip.py --extension-dir <repo>/extension --out <zip>`
2. Validate the exact ZIP, source manifest, and listing contract.
   - `python3 {baseDir}/scripts/validate_cws_package.py --zip <zip> --source-manifest <repo>/extension/manifest.json --listing-json <repo>/docs/cws/listing.json`
   - Default posture blocks stale ZIPs, Manifest V2, `tabs`, `debugger`, `<all_urls>`, persistent host permissions, declarative content scripts, remote script/eval patterns, missing permission justifications, privacy-practice drift, and no-host ZIPs whose listing still carries host-permission copy.
   - If a product genuinely needs host permissions, use `--allow-host-permissions` only after the listing and reviewer instructions explain the shipped user-facing need.
3. Scan tracked and untracked non-ignored files for obvious publish leaks.
   - `python3 {baseDir}/scripts/scan_publish_surface.py --root <repo> --json-out <json> --markdown-out <md>`
4. Run local reviewer/E2E gates.
   - `python3 {baseDir}/scripts/run_local_e2e_gates.py --repo-root <repo> --json-out <json> --markdown-out <md>`
   - The script discovers `check:cws`, `check:public`, `check:public:visual`, `test:e2e:reviewer`, `test:e2e`, and `scripts/reviewer_gate.py` when present.
5. Enforce the design/UI/UX evidence gate.
   - `python3 {baseDir}/scripts/check_design_gate.py --design-report <repo>/docs/design-gate.json --screenshot-metadata <repo>/assets/listing/screenshot-1.png.source.json`
   - Every changed public page, popup, CWS screenshot, promo tile, hero, and media asset must score at least `8/10` for product clarity, visual trust, evidence integrity, responsive polish, accessibility, and claim alignment.
6. Check current Chrome Stable release data.
   - `python3 {baseDir}/scripts/check_chrome_release.py --tested-chrome-version <local chrome version> --json-out <json> --markdown-out <md>`
   - Source: Chrome for Testing last-known-good Stable feed, cross-checked with ChromiumDash, Chrome Releases, and Chrome for Developers release notes when making decisions.
7. Run a competitor/differentiation check.
   - `python3 {baseDir}/scripts/check_competitors.py --listing-json <repo>/docs/cws/listing.json --competitors-json <repo>/docs/cws/competitors.json --min-competitors 3 --markdown-out <md>`
   - Record at least three comparable products or explicit substitutes; flag risky claims like `#1`, `best`, `official`, and close-copy positioning.
8. Generate launch metadata.
   - `python3 {baseDir}/scripts/generate_launch_manifest.py --repo-root <repo> --owner <github-owner> --public-site-base <https://public-site.example/> --out <json>`
   - If you already export `CWS_PUBLIC_SITE_BASE`, you can omit `--public-site-base` and the script will reuse that public reviewer-facing base.
9. Render publish commands.
   - `python3 {baseDir}/scripts/render_publish_commands.py --manifest <json> --out <md>`

## Rules

- Operate on the repo path the user named, not on arbitrary sibling directories.
- Inspect the ZIP intended for upload, not only the source tree, before calling a Chrome Web Store package ready.
- Prefer `activeTab` plus `scripting` after an explicit user gesture over persistent host permissions.
- Do not publish when the leak scan has unresolved findings.
- Do not publish when the target repo has a reviewer gate and it fails.
- Do not publish when package/listing/privacy claims disagree with the ZIP manifest.
- Do not publish when the design/UI gate is missing or any score is below `8/10`.
- Do not publish when local E2E was only run on an older Chrome milestone without recording the current Stable release check.
- Do not publish listing copy that claims official affiliation, best-in-class status, background crawling, server sync, or broad permissions unless the shipped product and public evidence prove it.
- Keep GitHub topics and ClawHub tags explicit in the generated manifest.
- Use a dedicated public site base for support, privacy-policy, and reviewer-instructions links when the extension has one.
- If a Chrome Web Store draft is already pending review, do not recommend canceling or replacing it unless a verified acceptance blocker exists.
- Do not assume generated artifacts should be committed.

## Current Policy Anchors

- Chrome Web Store Program Policies: https://developer.chrome.com/docs/webstore/program-policies/policies
- Manifest V3 remote-code requirements: https://developer.chrome.com/docs/webstore/program-policies/mv3-requirements
- `activeTab` plus `scripting` model: https://developer.chrome.com/docs/extensions/develop/concepts/activeTab
- Permission warnings and host permission warnings: https://developer.chrome.com/docs/extensions/develop/concepts/declare-permissions
- Chrome release notes: https://developer.chrome.com/release-notes/
- Chrome release feed: https://chromiumdash.appspot.com/fetch_releases

## Bundled Scripts

- `scripts/build_extension_zip.py`
- `scripts/validate_cws_package.py`
- `scripts/scan_publish_surface.py`
- `scripts/run_local_e2e_gates.py`
- `scripts/check_design_gate.py`
- `scripts/check_chrome_release.py`
- `scripts/check_competitors.py`
- `scripts/generate_launch_manifest.py`
- `scripts/render_publish_commands.py`
