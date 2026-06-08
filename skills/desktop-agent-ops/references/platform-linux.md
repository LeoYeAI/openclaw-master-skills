# Linux Path

This file defines the intended Linux branch for the skill.

## First branch

Always detect whether Linux is:

- X11
- Wayland

Use `scripts/platform_probe.py` before assuming available tools.

## Preferred direction

For Linux helper logic, tool families include:

- X11: `xdotool`, `wmctrl`, screenshot tools
- Wayland: compositor-specific screenshot and input tools, with stricter limits

If X11 tools are missing, report which dependency is absent and suggest installation.

## MVP rule

Linux helpers are now **best-effort** via `xdotool`/`wmctrl` for frontmost/list/focus/bounds. If tools are missing (or under Wayland), commands return structured errors. Be explicit about dependency requirements when failures occur.

## Behavior rule

Keep the skill workflow identical where possible; only the helper implementation should branch.
