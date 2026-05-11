---
name: media-generation
description: Generate images, edit existing images, create short videos, run inpainting/outpainting and object-focused edits, use reference images as provider inputs, batch related media jobs from a manifest, and fetch returned media from URLs/HTML/JSON/data URLs/base64. Use when working on AI image generation, AI image editing, mask-based inpainting, outpainting, reference-image workflows, short AI video generation, product-shot variations, or reusable media-production pipelines.
---

# Media Generation

Handle image generation, image editing, and short video generation through one workflow: choose the right modality, pass caller intent through to the provider, save outputs under `tmp/images/` or `tmp/videos/`, and prefer the bundled helpers over ad-hoc one-off API calls.

## Workflow decision

- If the user wants a brand-new still image, use an image-generation model.
- If the user supplies an image or wants a specific existing image changed, use an image-edit workflow.
- If the user wants motion / a clip / a short video, use a video-generation model.
- If the request includes one or more reference images, use the helper that supports reference-image transport.

## Standard workflow

1. Determine whether the task is image generation, image editing, or video generation.
2. Clarify only when required to execute the request correctly.
3. Prefer `scripts/generate_image.py` for still-image generation.
4. Prefer `scripts/edit_image.py` for direct image edits.
5. Prefer `scripts/mask_inpaint.py` for localized edits with masks or generated regions.
6. Prefer `scripts/outpaint_image.py` for canvas expansion / outpainting.
7. Prefer `scripts/generate_consistent_media.py` when reference images need to be passed through.
8. Prefer `scripts/generate_video.py` for video generation, especially when the provider may return async job payloads.
9. Prefer `scripts/generate_batch_media.py` for repeatable batch jobs, templated variations, or auditable manifests.
10. Prefer `scripts/object_select_edit.py` for simple object-vs-background edits on transparent assets or clean backdrops.
11. If the provider returns a URL, path, HTML snippet, markdown snippet, `data:` URL, or `b64_json`, use `scripts/fetch_generated_media.py`.
12. Save outputs under:
    - images → `tmp/images/`
    - videos → `tmp/videos/`
13. If the user wants files sent in chat, prefer sending the local downloaded file.
14. Keep the original remote reference as fallback when local retrieval fails.

## Prompt handling

Default to **prompt pass-through**.

- Pass the caller's prompt through unchanged.
- Use optional request fields only when the caller provides them.
- Keep prompt semantics under caller control.

Use the scripts mainly as functional helpers:
- normalize arguments
- map fields to provider-specific JSON
- upload files
- poll async jobs
- download returned media
- save outputs under `tmp/images/` or `tmp/videos/`

## Delivery rules

- Save generated or edited images in `tmp/images/`.
- Save generated videos in `tmp/videos/`.
- Never scatter generated files in the workspace root.
- If message delivery blocks remote URLs, download locally first and then send the local file.
- If a remote file cannot be fetched locally but the raw link may still help, provide the original link clearly.

## Image generation helper

Use `scripts/generate_image.py` for direct still-image generation.

Example:

```bash
python3 skills/media-generation/scripts/generate_image.py \
  --prompt 'person' \
  --size '1024x1024' \
  --out-dir 'tmp/images' \
  --prefix 'generated'
```

The helper:
- reads provider credentials from OpenClaw config (`~/.openclaw/openclaw.json` by default, or `--config` / `$OPENCLAW_CONFIG`)
- calls `/images/generations` by default
- supports `size`, `quality`, `style`, `background`, `n`, `seed`, `extra-json`, and `extra-json-file`
- downloads the returned image into `tmp/images/` by default
- handles providers that reply with URL/path, `data:` URL, or `b64_json`

## Image edit helper

Use `scripts/edit_image.py` for direct image-edit calls.

Example:

```bash
python3 skills/media-generation/scripts/edit_image.py \
  --image 'tmp/images/source.jpg' \
  --prompt 'replace the background' \
  --out-dir 'tmp/images' \
  --prefix 'edited'
```

The helper:
- reads provider credentials from OpenClaw config
- calls `/images/edits` by default
- supports optional `--mask` input for localized edits
- downloads the returned image into `tmp/images/` by default
- handles URL/path, `data:` URL, or `b64_json`

## Mask inpaint helper

Use `scripts/mask_inpaint.py` for localized repainting tasks.

Example:

```bash
python3 skills/media-generation/scripts/mask_inpaint.py \
  --image 'tmp/images/source.jpg' \
  --x 120 --y 80 --width 220 --height 180 \
  --prompt 'replace the masked area' \
  --out-dir 'tmp/images' \
  --prefix 'mask-result'
```

The helper:
- accepts either an existing `--mask` image or generated regions
- supports rectangle / ellipse regions and repeatable `--region` specs
- supports percentage-based regions like `rect-pct` / `ellipse-pct`
- supports `--expand` / `--shrink` before feathering
- supports `--mask-only` for local preparation / testing without a live API call
- forwards `--config`, `--provider`, `--model`, and `--endpoint` to `scripts/edit_image.py`
- reuses `scripts/edit_image.py` for the final edit call

## Outpaint helper

Use `scripts/outpaint_image.py` for extension / canvas expansion tasks.

Example:

```bash
python3 skills/media-generation/scripts/outpaint_image.py \
  --image 'tmp/images/source.jpg' \
  --left 512 --right 512 --top 128 --bottom 128 \
  --mode blur \
  --prompt 'extend outward' \
  --out-dir 'tmp/images' \
  --prefix 'outpaint-result'
```

The helper:
- expands the canvas locally before calling the model
- supports directional expansion on each side
- supports `transparent`, `blur`, and `solid` initialization modes
- forwards `--config`, `--provider`, `--model`, and `--endpoint` to `scripts/edit_image.py`
- reuses `scripts/edit_image.py` for the final edit call

## Reference-image helper

Use `scripts/generate_consistent_media.py` when one or more reference images need to be passed through to the provider.

Note: the script name is historical; its current role is reference-image transport and delegation.

Example:

```bash
python3 skills/media-generation/scripts/generate_consistent_media.py \
  --mode image \
  --reference-image 'tmp/images/reference.png' \
  --prompt 'character' \
  --size '1024x1024' \
  --out-dir 'tmp/images' \
  --prefix 'reference-output'
```

The helper:
- can pass encoded reference images in provider JSON (default key: `reference_images`)
- can retry without provider-json references when transport is `auto`
- delegates to `scripts/generate_image.py` or `scripts/generate_video.py`

## Batch generation helper

Use `scripts/generate_batch_media.py` when the user wants several related outputs, repeatable batch rendering, or a manifest-driven workflow.

Example:

```bash
python3 skills/media-generation/scripts/generate_batch_media.py \
  --manifest 'tmp/images/media-batch.jsonl' \
  --vars-json '{"subject":"item"}' \
  --summary-out 'tmp/images/media-batch-summary.json' \
  --continue-on-error \
  --print-json
```

The helper supports:
- JSON array or JSONL manifests
- image generation, video generation, and reference-image generation
- shared templating vars via `--vars-json` or `--vars-file`
- item-local `vars` objects for per-item string rendering such as `{index}`
- `--summary-out` to persist the resolved batch result JSON
- `--dry-run` to validate a manifest before spending live generation calls

## Object-select edit helper

Use `scripts/object_select_edit.py` when the source has a transparent background or a simple clean backdrop and the user wants a one-step object or background edit workflow.

Example:

```bash
python3 skills/media-generation/scripts/object_select_edit.py \
  --image 'tmp/images/product.png' \
  --selection-mode alpha \
  --edit-target background \
  --prompt 'replace the background' \
  --out-dir 'tmp/images' \
  --prefix 'product-bg-edit'
```

The helper:
- prepares an object/background mask with `prepare_object_mask.py`
- flips the mask automatically when editing the background instead of the object
- passes the prepared mask into `mask_inpaint.py`
- supports `--prepare-only` for local inspection/testing without a live edit call

## Video generation helper

Use `scripts/generate_video.py` for direct video-generation calls.

Example:

```bash
python3 skills/media-generation/scripts/generate_video.py \
  --prompt 'motion clip' \
  --size '720x1280' \
  --seconds 6 \
  --out-dir 'tmp/videos' \
  --prefix 'generated-video'
```

The helper:
- reads provider credentials from OpenClaw config
- calls `/videos` by default
- supports `size`, `seconds` / `duration`, `fps`, `seed`, optional input image, `extra-json`, and `extra-json-file`
- can resolve both immediate-result and async job responses by polling when the provider returns job metadata instead of the final media directly
- downloads the returned video into `tmp/videos/` by default

## Retrieval helper

Use `scripts/fetch_generated_media.py` for both images and videos.
It can extract downloadable refs from markdown / HTML / JSON, and can also persist `data:` URLs or `b64_json` payloads directly to local files.

## Quick compatibility checklist

Before blaming the skill, check these first:
- config exists and is valid JSON
- `config.models.providers.<provider>` exists
- the selected provider has both `baseUrl` and `apiKey`
- the chosen endpoint actually exists on that provider
- the chosen model name is valid for that endpoint
- any provider-specific fields passed through `--extra-json` or `--extra-json-file` match that provider's schema

Defaults used by the bundled scripts:
- config path: `~/.openclaw/openclaw.json` or `$OPENCLAW_CONFIG`
- default provider: `$OPENCLAW_MEDIA_PROVIDER`, otherwise the first provider found in config
- default model names: placeholders unless overridden by env vars or `--model`
  - image → `$OPENCLAW_MEDIA_IMAGE_MODEL` or `image-model`
  - edit → `$OPENCLAW_MEDIA_EDIT_MODEL` or `image-edit-model`
  - video → `$OPENCLAW_MEDIA_VIDEO_MODEL` or `video-model`
- output root: `tmp/` or `$MEDIA_GENERATION_OUTPUT_ROOT`
- output paths are resolved relative to the current working directory unless you pass an absolute `--out-dir`

## Quick troubleshooting

Common failure patterns:
- **`provider not found`** → pass `--provider` explicitly or set `$OPENCLAW_MEDIA_PROVIDER`
- **placeholder model warning (`image-model` / `image-edit-model` / `video-model`)** → pass `--model` explicitly or set the matching `$OPENCLAW_MEDIA_*_MODEL` env var
- **`config not found` / invalid JSON** → pass `--config` explicitly or fix the OpenClaw config file
- **HTTP 404** → check `--endpoint` and video polling paths
- **HTTP 400** → check model name and provider-specific payload fields in `--extra-json` / `--extra-json-file`
- **HTTP 401/403** → check the provider `apiKey`
- **request failed before HTTP response** → check base URL, proxy/TLS, or network reachability
- **video accepted then failed later** → check request payload, provider logs, or switch provider/model

Use `--print-json` when debugging so the response body, resolved endpoint, and failure hints stay visible.

## References

- Batch workflow reference: `references/batch-workflows.md`
- Model capability matrix: `references/model-capabilities.md`
- Reference-image workflow: `references/reference-image-workflow.md`
- Image generation helper: `scripts/generate_image.py`
- Reference-image helper: `scripts/generate_consistent_media.py`
- Image edit helper: `scripts/edit_image.py`
- Mask inpaint helper: `scripts/mask_inpaint.py`
- Outpaint helper: `scripts/outpaint_image.py`
- Video generation helper: `scripts/generate_video.py`
- Batch generation helper: `scripts/generate_batch_media.py`
- Object-select edit helper: `scripts/object_select_edit.py`
- Object mask prep helper: `scripts/prepare_object_mask.py`
- Shared request utility: `scripts/media_request_common.py`
- Smoke tests: `scripts/smoke_test.py`
- Unified fetch helper: `scripts/fetch_generated_media.py`
