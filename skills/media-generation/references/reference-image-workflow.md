# Reference-Image Workflow

Use this reference for reference-image transport behavior and provider compatibility.

## Purpose

Pass one or more reference images through to a provider without changing caller prompt text.

## Helper

Primary helper:
- `scripts/generate_consistent_media.py`

This helper:
- accepts one or more `--reference-image` inputs
- can encode them as data URLs
- can attach them under a configurable JSON field
- can delegate execution to `generate_image.py` or `generate_video.py`
- can retry without provider-json reference payloads when transport mode is `auto`

## Core arguments

- `--reference-image` repeatable reference image path
- `--reference-key` JSON field name for encoded reference images
- `--transport auto|none|provider-json`
- `--mode image|video`
- `--video-reference-mode reference|animate`

## Transport modes

### `provider-json`
- Encode reference images
- Attach them in request JSON under `reference_key`
- Use when provider schema accepts encoded reference-image fields

### `auto`
- Try provider-json transport first
- If that request fails, retry without provider-json references

### `none`
- Do not attach provider-json reference payloads
- Still allow the delegated script to receive a direct `--image` argument when applicable

## Video path behavior

When `--mode video` and at least one reference image is present:
- the first reference image is passed to `generate_video.py` via `--image`
- `--video-reference-mode` is forwarded as the video request mode
- `--image-transport data-url` is used for the delegated video request
- if `video-reference-mode=reference` and `reference_key` matches a known image field, that field name is forwarded to `generate_video.py`

## Common compatibility issues

Check these first:
- provider rejects large encoded payloads
- provider expects a different reference-image field name
- provider accepts direct image fields but not `reference_images`
- provider accepts video image input only in one specific field

## Data handling notes

- Reference images are read from local paths.
- Encoded payloads may be written to a temporary JSON file when the inline JSON would be too large.
- Temporary JSON files are deleted after execution.
