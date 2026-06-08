# Reproducible Setup

Use this file when the goal is not just to make desktop automation work once, but to make it work again on another host.

## Goal

Standardize four things:

1. runtime location
2. dependency installation
3. platform prerequisites
4. smoke-test procedure

If these are stable, the same skill can be brought up on another Mac, Windows PC, or Linux machine with fewer surprises.

## Runtime convention

Keep the packaged skill directory clean.

Use an external runtime directory such as:

- workspace-local: `cache/desktop-agent-ops/venv`
- future shared host pattern: `$OPENCLAW_DESKTOP_AGENT_OPS_HOME/venv`

Recommended environment variable:

- `DESKTOP_AGENT_OPS_PYTHON`

Example:

- `DESKTOP_AGENT_OPS_PYTHON=/abs/path/to/venv/bin/python`

The helper scripts should always be runnable by explicitly pointing to the chosen interpreter.

## Preferred installer

Use `uv`, not ad hoc `pip`.

Reason:

- faster and more reproducible
- works cleanly with explicit interpreter targets
- easier to document cross-host

## Minimum Python dependencies

Current common runtime dependencies:

- `pillow`
- `pyautogui`
- `pygetwindow`
- `pytesseract`
- `opencv-python`
- `numpy`

Do not assume they exist in the system Python.

## Platform prerequisites

### macOS

Required:

- Screen Recording permission
- Accessibility permission
- Automation permission when app activation is needed
- `cliclick` available on PATH
- `tesseract` binary on PATH (for OCR-based targeting)

Nice to have:

- a dedicated external venv managed by `uv`

### Windows

Required later when implementation is tested there:

- Python runtime in external venv
- desktop control backend chosen explicitly
- screenshot backend chosen explicitly

### Linux

Required later when implementation is tested there:

- X11 or Wayland path documented separately
- screenshot backend chosen explicitly
- input backend chosen explicitly

## One-host bring-up checklist

1. probe platform
2. create external runtime
3. install dependencies
4. run permission bootstrap (`scripts/permission_bootstrap.py`, add `--open-settings` on macOS if prompts fail)
5. run doctor
6. run smoke test
7. only then start UI task testing

## Smoke test expectations

A host is considered ready only if all of these pass:

- frontmost app query
- full screenshot
- screen size
- mouse position readback
- move + readback consistency
- pixel color read

Recommended extended checks for precision-ready hosts:
- screenshot with visible cursor
- structured target report generation
- click-and-verify helper producing pre/post captures and candidate-point metadata

Optional but useful:

- focus-app
- click on a safe blank area
- type into a scratch app like Notes or a temporary text field

## Failure policy

If smoke test fails, do not continue to real UI tasks.

First classify the failure:

- missing dependency
- missing OS permission
- backend command unavailable
- coordinate mismatch
- verification mismatch

Then fix the class, not just the single symptom.

## Reproducibility target

The target form is:

- same skill package
- same documented external runtime layout
- same bring-up commands
- same doctor command
- same smoke test command
- same pass/fail criteria

That is what makes the skill portable across hosts instead of machine-specific.
