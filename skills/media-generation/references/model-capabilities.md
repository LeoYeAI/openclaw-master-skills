# Model Capabilities

Use this reference for modality selection, parameter support, return shapes, and compatibility expectations.

## Modalities

### Still-image generation
Typical endpoint:
- `/images/generations`

Typical inputs:
- `prompt`
- optional `size`
- optional `quality`
- optional `style`
- optional `background`
- optional `n`
- optional `seed`

Typical return shapes:
- absolute `url`
- relative `path`
- `b64_json`
- direct media references embedded in JSON/text

### Image edit / inpaint / outpaint
Typical endpoint:
- `/images/edits`

Typical inputs:
- `image`
- `prompt`
- optional `mask`
- provider-specific multipart form fields

Typical return shapes:
- absolute `url`
- relative `path`
- `b64_json`

### Short video generation
Typical endpoint:
- `/videos`
- provider-specific video endpoints

Typical inputs:
- `prompt`
- optional `size`
- optional `seconds` / `duration`
- optional `fps`
- optional `seed`
- optional image input via `image`, `input_image`, `first_frame_image`, or `reference_images`

Typical return shapes:
- direct media `url`
- relative `path`
- HTML/JSON media reference
- async job payload with `id`, `status_url`, or equivalent polling metadata

## Input transport notes

### Text request
Use prompt-only requests when the provider endpoint accepts only textual input.

### Image request
Image inputs may need one of these forms depending on provider:
- local path
- data URL
- JSON array of encoded images

### Reference-image request
Reference-image workflows depend on provider schema. Common JSON field names:
- `reference_images`
- `image`
- `input_image`
- `first_frame_image`

## Helper selection

Use:
- `generate_image.py` for still-image generation
- `edit_image.py` for direct image edits
- `mask_inpaint.py` when a mask is required or should be generated locally
- `outpaint_image.py` when the canvas must be expanded locally before calling the edit endpoint
- `generate_video.py` for direct video requests and async polling
- `generate_consistent_media.py` when reference images need transport handling
- `fetch_generated_media.py` when the response contains downloadable media references

## Compatibility checks

Before execution, verify:
- config file exists and is valid JSON
- `config.models.providers.<provider>` exists
- provider has `baseUrl` and `apiKey`
- endpoint exists on that provider
- model name is valid for that endpoint
- provider-specific fields in `extra_json` / `extra_json_file` match schema

## Default environment values

- config path: `~/.openclaw/openclaw.json` or `$OPENCLAW_CONFIG`
- default provider: `$OPENCLAW_MEDIA_PROVIDER`, otherwise first provider in config
- default image model: `$OPENCLAW_MEDIA_IMAGE_MODEL` or `image-model`
- default edit model: `$OPENCLAW_MEDIA_EDIT_MODEL` or `image-edit-model`
- default video model: `$OPENCLAW_MEDIA_VIDEO_MODEL` or `video-model`
- output root: `tmp/` or `$MEDIA_GENERATION_OUTPUT_ROOT`

## Return-shape handling

Providers may return:
- direct absolute URL
- relative path requiring origin prefix
- `data:` URL
- `b64_json`
- HTML with media source tags
- async job metadata requiring polling

Use the bundled helpers so these return shapes are normalized consistently.
