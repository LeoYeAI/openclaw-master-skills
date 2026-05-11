---
name: instruments-profiling
description: Use when profiling native macOS or iOS apps with Instruments/xctrace. Covers correct binary selection, CLI arguments, exports, and common gotchas.
metadata:
  short-description: Instruments profiling for macOS/iOS apps
---

# Instruments Profiling (macOS/iOS)

Use this skill when the user wants performance profiling or stack analysis for native apps.
Focus: Time Profiler, `xctrace` CLI, and picking the correct binary/app instance.

## Quick Start (CLI)

- List templates: `xcrun xctrace list templates`
- Record Time Profiler (launch):
  - `xcrun xctrace record --template 'Time Profiler' --time-limit 60s --output /tmp/App.trace --launch -- /path/To/App.app`
- Record Time Profiler (attach):
  - Launch app yourself, get PID, then:
  - `xcrun xctrace record --template 'Time Profiler' --time-limit 60s --output /tmp/App.trace --attach <pid>`
- Open trace in Instruments:
  - `open -a Instruments /tmp/App.trace`

Note: `xcrun xctrace --help` is not a valid subcommand. Use `xcrun xctrace help record`.

## Picking the Correct Binary (Critical)

**Gotcha: Instruments may profile the wrong app** (e.g., one in `/Applications`) if LaunchServices resolves a different bundle.
Use these rules:

- Prefer direct binary path for deterministic launch:
  - `xcrun xctrace record ... --launch -- /path/App.app/Contents/MacOS/App`
- If launching `.app`, ensure it’s the intended bundle:
  - `open -n /path/App.app`
  - Verify with `ps -p <pid> -o comm= -o command=`
- If both `/Applications/App.app` and a local build exist, explicitly target the local build path.
- After launch, confirm the process path before trusting the trace.

## Command Arguments (xctrace)

- `--template 'Time Profiler'`: template name from `xctrace list templates`.
- `--launch -- <cmd>`: everything after `--` is the target command (binary or app bundle).
- `--attach <pid|name>`: attach to running process.
- `--output <path>`: `.trace` output. If omitted, file saved in CWD.
- `--time-limit 60s|5m`: set capture duration.
- `--device <name|UDID>`: required for iOS device runs.
- `--target-stdout -`: stream launched process stdout to terminal (useful for CLI tools).

## Exporting Stacks (CLI)

- Inspect trace tables:
  - `xcrun xctrace export --input /tmp/App.trace --toc`
- Export raw time-profile samples:
  - `xcrun xctrace export --input /tmp/App.trace --xpath '/trace-toc/run[@number="1"]/data/table[@schema="time-profile"]' --output /tmp/time-profile.xml`
- Post-process in a script (Python/Rust) to aggregate stacks.

## Instruments UI Workflow

- Template: Time Profiler
- Use “Record” and capture the slow path (startup vs steady-state)
- Call Tree tips:
  - Hide System Libraries
  - Invert Call Tree
  - Separate by Thread
  - Focus on hot frames and call counts

## Gotchas & Fixes

- **Wrong app profiled**: LaunchServices resolves installed app instead of local build.
  - Fix: use direct binary path or `--attach` with known PID.
- **No samples / empty trace**: App exits quickly or never hits work.
  - Fix: longer capture, trigger workload during recording.
- **Privacy prompts**: `xctrace` may need Developer Tools permission.
  - Fix: System Settings → Privacy & Security → Developer Tools → allow Terminal/Xcode.
- **Large XML exports**: `time-profile` exports are huge.
  - Fix: filter with XPath and aggregate offline; don’t print to terminal.

## iOS Specific Notes

- Device: use `xcrun xctrace list devices` and `--device <UDID>`.
- Launch via Xcode if needed; attach with `xctrace --attach`.
- Ensure debug symbols for meaningful stacks.

## Verification Checklist

- Confirm trace process path matches target build.
- Confirm stacks show expected app frames.
- Capture covers the slow operation (startup/refresh). 
- Export stacks for automated diffing if optimizing.
