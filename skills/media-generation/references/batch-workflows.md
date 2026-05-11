# Batch Workflows

Use this reference for the manifest and execution model of `scripts/generate_batch_media.py`.

## Purpose

Run multiple media requests from one manifest and collect one summary file.

## Supported manifest formats

- JSON array
- JSONL (one JSON object per line)

## Supported item routing

The batch helper dispatches items by fields present in each item:

- image generation → `generate_image.py`
- video generation (`mode: video`) → `generate_video.py`
- reference-image workflow (`reference_image` / `reference_images` / `consistent`) → `generate_consistent_media.py`

## Shared templating

String fields support `{variable}` substitution.

Variable sources:
1. `--vars-json`
2. `--vars-file`
3. item-local `vars`
4. built-in values: `index`, `mode`

## Common item fields

Core:
- `mode`
- `prompt`
- `prefix`
- `provider`
- `model`
- `endpoint`
- `out_dir`

Image/video option passthrough:
- `size`
- `quality`
- `style`
- `background`
- `n`
- `seed`
- `duration`
- `seconds`
- `fps`
- `config`
- `status_endpoint_template`
- `image`
- `extra_json`
- `extra_json_file`
- `timeout`
- `poll_interval`
- `max_polls`

Reference-image workflow fields:
- `reference_image`
- `reference_images`
- `reference_key`
- `transport`

Execution controls:
- `download`
- `print_json`

## Output summary

Use `--summary-out` to persist a JSON summary.

Summary fields include:
- overall `ok`
- item `index`
- rendered `item`
- resolved `cmd`
- per-item `stdout`
- per-item `stderr`

## Validation / debugging

- Use `--dry-run` to inspect rendered commands without execution.
- Use `--continue-on-error` to process later items after a failure.
- If only reference-image items fail, check `reference_key`, `transport`, and provider schema compatibility.
- If only video items fail, check `endpoint` and `status_endpoint_template`.
