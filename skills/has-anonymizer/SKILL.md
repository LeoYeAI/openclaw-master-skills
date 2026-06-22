---
name: has-anonymizer
description: "HaS (Hide and Seek) on-device text and image anonymization. Text: 8 languages (zh/en/fr/de/es/pt/ja/ko), open-set entity types. Image: 21 privacy categories (face, fingerprint, ID card, passport, license plate, etc.). Use when: (1) anonymizing text before sending to cloud LLMs then restoring the response, (2) anonymizing documents, code, emails, or messages before sharing, (3) scanning text or images for sensitive content, (4) anonymizing logs before handing to ops/support, (5) masking faces/IDs/plates in photos before publishing or sharing."
metadata:
  {
    "openclaw":
      {
        "emoji": "🔒",
        "requires": {
          "bins": ["llama-server", "uv"],
          "env": {
            "HAS_TEXT_MODEL_PATH": {
              "description": "Absolute path to the HaS text GGUF model (default: ~/.openclaw/tools/has-anonymizer/models/has_text_model.gguf)",
              "required": false
            },
            "HAS_IMAGE_MODEL": {
              "description": "Absolute path to the HaS image YOLO model (default: ~/.openclaw/tools/has-anonymizer/models/sensitive_seg_best.pt)",
              "required": false
            },
            "HAS_TEXT_MAX_PARALLEL_REQUESTS": {
              "description": "Maximum parallel inference requests for scan/hide/restore batch operations (default: 4, max: 4)",
              "required": false
            }
          }
        },
        "install":
          [
            {
              "id": "brew-uv",
              "kind": "brew",
              "os": ["darwin"],
              "formula": "uv",
              "bins": ["uv"],
              "label": "Install uv (brew)",
            },
            {
              "id": "brew-llama",
              "kind": "brew",
              "os": ["darwin"],
              "formula": "llama.cpp",
              "bins": ["llama-server"],
              "label": "Install llama.cpp (brew)",
            },
            {
              "id": "download-model",
              "kind": "download",
              "url": "https://huggingface.co/xuanwulab/HaS_Text_0209_0.6B_Q8/resolve/main/has_text_model.gguf",
              "targetDir": "models",
              "label": "Download HaS text model Q8 (639 MB)",
            },
            {
              "id": "download-image-model",
              "kind": "download",
              "url": "https://huggingface.co/xuanwulab/HaS_Image_0209_FP32/resolve/main/sensitive_seg_best.pt",
              "targetDir": "models",
              "label": "Download HaS image model FP32 (119 MB)",
            },
          ],
      },
  }
---

# HaS Privacy

HaS exposes a single umbrella CLI:

- `has text ...` for text anonymization, restoration, and scanning
- `has image ...` for image scanning, masking, and category discovery

Use it when you need to remove private data locally before sending content elsewhere, inspect a directory for privacy risks, or mask visual privacy targets in photos and screenshots.

## Agent Decision Guidelines

- Prefer `has text` for plaintext and `has image` for raster images. For mixed directories, run both and combine the results into one report.
- For PDFs, Word documents, or scanned pages, extract text first and then use `has text`. For screenshots/photos where the goal is simply to hide visible carriers such as faces, screens, paper, labels, or QR codes, use `has image`. If the goal is to reason about the text content inside an image, run OCR first and then use `has text`.
- Do not overwrite or delete the original files. Text commands can restore later, image masking is irreversible.
- Proactively mention configurable knobs when the user intent is clear: `has text` uses repeated `--type`; `has image` uses repeated `--type`, plus `--method` and `--strength`.
- If the user intent is ambiguous, start with `scan` before `hide`.
- After batch scans, summarize text file count, image file count, findings by type/category, high-risk items, and the suggested next step.
- If timing matters to the user, add `--timing` and report the elapsed result in plain language afterward.
- For `qr_code` and `barcode`, the default mosaic strength is automatically raised based on the detection size to ensure the encoding is destroyed. The agent does not need to manually increase `--strength` for these categories. If a detection output includes `effective_strength`, report it to the user.

## Shared CLI Contract

The current CLI contract is designed for agents first:

- Success returns compact JSON.
- Failure also returns compact JSON with `error.code` and `error.message`.
- Returned path fields are absolute.
  - This includes `file`, `output`, `mapping_output`, and `skipped[].file`.
- Invalid combinations fail fast instead of silently falling back.
- Directory mode is non-recursive. Only immediate children are processed.
- Batch results can include `skipped` and `skipped_count`.
  - Treat `skipped` entries as unprocessed files, not as clean files.

Shared command layout:

```bash
{baseDir}/scripts/has.sh <text|image> <command> [options]
```

Shared options can be placed before or after the subcommand.

---

# Part 1: `has text`

`has text` is the plaintext namespace. It supports:

- `scan`
- `hide`
- `restore`

It runs entirely on-device and uses a local `llama-server` plus the HaS text model when model inference is required.

## Core Text Concepts

### Semantic tags

Anonymized text uses semantic tags such as:

```text
<EntityType[ID].Category.Attribute>
```

This preserves structure better than a flat `[REDACTED]` token and is the reason restored downstream LLM output can remain usable.

### Open-set types

Repeated `--type` flags are open-set. They are not limited to a fixed catalog. Natural language type names such as `"person name"`, `"address"`, `"phone number"`, or `"numeric values (transaction amounts)"` are valid.

### Public/private distinction

Type wording matters. For example, `"personal location"` is usually safer than `"location"` if you want to preserve public places but hide private addresses. Public/private person-name distinctions remain less stable and should not be trusted without verification.

### Multilingual support

The text model supports Chinese, English, French, German, Spanish, Portuguese, Japanese, and Korean, including mixed-language text.

### Type name language

Match the `--type` language to the source text language:

- **Chinese text** → use Chinese type names: `--type "人名" --type "电话号码" --type "地址"`
- **Non-Chinese text** (English, French, German, etc.) → use English type names: `--type "person name" --type "phone number" --type "address"`

## Text Runtime Prerequisites

`has text` auto-starts a local `llama-server` when needed.

- Default model path: `~/.openclaw/tools/has-anonymizer/models/has_text_model.gguf`
- Override model path: `HAS_TEXT_MODEL_PATH=/abs/path/to/has_text_model.gguf`
- Override parallel cap: `HAS_TEXT_MAX_PARALLEL_REQUESTS`
- If HuggingFace downloads fail, see **Model Download Mirrors** below.

## Text Usage

```bash
{baseDir}/scripts/has.sh text [--timing] [--verbose] <scan|hide|restore> [options]
```

Namespace options:

| Option | Description |
|--------|-------------|
| `--timing` | Include `elapsed_ms` in the JSON output |
| `--verbose` | Emit runtime status and progress messages to stderr |

Input methods:

| Method | Description |
|--------|-------------|
| `--text '<text>'` | Pass text directly |
| `--file <path>` | Read text from a file |
| `--dir <path>` | Process immediate plaintext files in a directory |
| stdin | For single-text mode when no `--text`, `--file`, or `--dir` is provided |

Rules:

- `--text`, `--file`, and `--dir` are mutually exclusive.
- Empty `--type` values are rejected.
- Directory mode only accepts batch output flags.
- Single-file `hide` requires `--mapping-output`.
- Single-file `restore` requires `--mapping`.
- In text directory mode, `skipped` can include unprocessed files (binary, encoding, or read errors).

## `has text scan`

Finds sensitive entities without replacing them.

```bash
{baseDir}/scripts/has.sh text scan --type "person name" --type "phone number" --file report.txt
{baseDir}/scripts/has.sh text scan --type "person name" --type "phone number" --dir ./reports/
```

Parameters:

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--type` | yes | Entity type to scan for; repeat to add more |
| `--text` / `--file` / `--dir` | one input | Input source |
| `--max-chunk-tokens` | | Max tokens per chunk, default `5000` |
| `--max-parallel-requests` | | Max scan chunks in parallel, default `4` |

Output:

- Single-text mode returns `{"entities": ...}`
- Directory mode returns `{"results":[...],"count":N,"summary":{...}}`
- Batch output may include `skipped` and `skipped_count`

## `has text hide`

Replaces sensitive entities with semantic tags.

```bash
{baseDir}/scripts/has.sh text hide --type "person name" --type "address" --text "John lives in Brooklyn" --mapping-output ./mapping.json
{baseDir}/scripts/has.sh text hide --type "person name" --file note.txt --output ./note.anonymized.txt --mapping-output ./note.mapping.json
{baseDir}/scripts/has.sh text hide --type "person name" --dir ./docs/
```

Parameters:

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--type` | yes | Entity type to anonymize; repeat to add more |
| `--text` / `--file` / `--dir` | one input | Input source |
| `--mapping-output` | single-file: yes | Output path for generated mapping JSON |
| `--output` | single-file | Output path for anonymized text |
| `--mapping` | single-file | Existing mapping JSON file for incremental anonymization |
| `--output-dir` | batch | Output directory for anonymized files (default: `<dir>/.has/anonymized/`) |
| `--mapping-dir` | batch | Output directory for per-file mapping JSON files (default: `<output-dir>/mappings/`) |
| `--max-chunk-tokens` | | Max tokens per chunk, default `3000` |
| `--max-parallel-requests` | | Max files in parallel for `--dir`, default `4` |
| `--no-tool-pair` | | Disable diff-based pair extraction; always use Model-Pair (slower but more robust) |

Behavior:

- Single-file mode never emits the mapping table inline.
- Single-file mode returns either:
  - `{"text":"...","mapping_output":"/abs/path/to/map.json"}`
  - `{"output":"/abs/path/to/out.txt","mapping_output":"/abs/path/to/map.json"}`
- Batch mode does not accept shared `--mapping`.
- Mapping files are sensitive assets. Protect them.

## `has text restore`

Restores anonymized text using mapping JSON.

```bash
{baseDir}/scripts/has.sh text restore --mapping mapping.json --text "<person name[1].personal.name> lives in ..."
{baseDir}/scripts/has.sh text restore --mapping mapping.json --file anonymized.txt --output restored.txt
{baseDir}/scripts/has.sh text restore --dir ./.has/anonymized/ --output-dir ./.has/restored/
```

Parameters:

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--mapping` | single-file: yes | Mapping JSON file path |
| `--text` / `--file` / `--dir` | one input | Input source |
| `--output` | single-file | Output path for restored text |
| `--mapping-dir` | batch | Per-file mapping directory (default: `<dir>/mappings/`) |
| `--output-dir` | batch | Output directory for restored files (default: sibling `restored/` under `.has/`, or `<dir>/.has/restored/`) |
| `--max-chunk-tokens` | | Max tokens per chunk when model restore is needed, default `3000` |
| `--max-parallel-requests` | | Max model-backed restore chunks in parallel |

Behavior:

- Single-file mode returns inline `text` unless `--output` is provided.
- `restore --dir` uses per-file mapping JSON files. It does not accept a shared `--mapping`.
- `restore --dir` expects mapping files at `<mapping-dir>/<filename>.mapping.json` (matching the naming convention produced by `hide --dir`).

## Typical Text Workflow

Anonymize text before sending it to a cloud LLM, then restore the answer:

1. `hide` to produce anonymized text plus mapping
2. send anonymized text to the cloud model **with a tag-format explanation** (see below)
3. `restore` the model response with the mapping

For multi-line text, prefer file-based intermediates over shell variables.

### Prompting the cloud LLM with anonymized text

When forwarding anonymized text to a cloud LLM, the agent **must** prepend a brief explanation of the tag format so the model understands and preserves the tags. Include wording equivalent to the following (adjust language to match the conversation):

> The text below has been anonymized. Sensitive entities are replaced by tags in the format `<EntityType[ID].Category.Attribute>`:
>
> - **EntityType** — the kind of entity (matches the `--type` value, e.g. `person name`, `address`, `phone number`).
> - **[ID]** — a numeric identifier. The same type + same ID always refers to the **same** real-world entity (e.g. every `<person name[1]>` is the same person; `<person name[2]>` is a different person).
> - **.Category.Attribute** — additional semantic classification of the entity.
>
> **Rules:**
> 1. Preserve every tag exactly as-is in your response — do not modify, translate, paraphrase, omit, or expand any tag.
> 2. When referring to an anonymized entity, reuse the original tag with the correct ID.
> 3. Do not attempt to guess the real values behind the tags.

Omitting this explanation may cause the cloud model to strip, rewrite, or misinterpret the tags, which will break the `restore` step.

## Model Download Mirrors

If HuggingFace downloads fail, use these ModelScope mirrors:

- text model: `https://modelscope.cn/models/TencentXuanwu/HaS_Text_0209_0.6B_Q8`
- image model: `https://modelscope.cn/models/TencentXuanwu/HaS_Image_0209_FP32`

---

# Part 2: `has image`

`has image` is the image namespace. It supports:

- `scan`
- `hide`
- `categories`

It loads the YOLO segmentation model directly and does not require `llama-server`.

## Image Usage

```bash
{baseDir}/scripts/has.sh image [--timing] [--model MODEL] <scan|hide|categories> [options]
```

Namespace options:

| Option | Applies to | Description |
|--------|------------|-------------|
| `--timing` | all image commands | Include `elapsed_ms` in the JSON output |
| `--model PATH` | `scan`, `hide` | Override the image model path |


## Image Privacy Categories

Common categories include `biometric_face`, `id_card`, `passport`, `license_plate`, `qr_code`, `mobile_screen`, and `paper`.

Use `has image categories` when you need the full catalog of 21 supported classes.

`--type` accepts:

- English names
- Chinese names
- numeric IDs
- unique partial matches such as `face`

Rules:

- Empty `--type` values are rejected.
- Ambiguous partial matches fail fast.
- Omit `--type` to scan or mask all supported categories.
- In image directory mode, `skipped` can include unprocessed files.

## `has image scan`

Finds privacy regions without modifying the image.

```bash
{baseDir}/scripts/has.sh image scan --image photo.jpg --type face --type id_card
{baseDir}/scripts/has.sh image scan --dir ./photos/ --type face
```

Parameters:

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--image` / `--dir` | one input | Single image or batch directory |
| `--type` | | Category filter; repeat to add more |
| `--conf` | | Confidence threshold, default `0.25` |
| `--model` | | Override image model path |

Output:

- Single-image mode returns `detections` and `summary`
- Directory mode returns `results`, `count`, `summary`, and optional `skipped`

## `has image hide`

Detects and masks privacy regions in images.

```bash
{baseDir}/scripts/has.sh image hide --image photo.jpg --type face --method blur --strength 25
{baseDir}/scripts/has.sh image hide --dir ./photos/
```

Parameters:

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `--image` / `--dir` | one input | Single image or batch directory |
| `--output` | single-image | Output image path |
| `--output-dir` | batch | Output directory |
| `--type` | | Category filter; repeat to add more |
| `--method` | | `mosaic`, `blur`, or `fill`; default `mosaic` |
| `--strength` | | Mosaic block size or blur radius; default `15` |
| `--fill-color` | | Fill color for `fill`; default `#000000` |
| `--conf` | | Confidence threshold; default `0.25` |
| `--model` | | Override image model path |

Behavior:

- Refuses to overwrite the source image.
- Directory mode accepts `--output-dir`, not `--output`.
- For `qr_code` and `barcode` detections with `--method mosaic`, the block size is automatically raised to `max(strength, bbox_short_side // 10, 20)` to prevent the encoding from surviving pixelation. After masking, a lightweight verification confirms the code is no longer machine-readable; if it is, the strength is escalated further (up to a fill fallback). Each affected detection includes an `effective_strength` field in the output.
- A cv2-based fallback supplements YOLO detection for QR codes and barcodes. When YOLO misses a code (e.g. large codes on plain backgrounds), `cv2.QRCodeDetector` and `cv2.barcode.BarcodeDetector` provide additional coverage. When YOLO misclassifies a code region as a different category (e.g. `monitor_screen`), cv2 corrects the category before `--type` filtering, so `--type qr_code` catches all QR codes regardless of YOLO's label. Corrected detections include a `"corrected_from"` field; new detections include `"cv2_fallback": true`.

## `has image categories`

Lists all supported image privacy categories.

```bash
{baseDir}/scripts/has.sh image categories
{baseDir}/scripts/has.sh image categories --timing
```

Behavior:

- Returns `{"categories":[...]}`
- Supports `--timing`

## Suggested Combined Scan

For a mixed workspace:

1. run `has text scan ... --dir <dir>` for plaintext
2. run `has image scan --dir <dir>` for images
3. merge the two JSON results into one privacy report

If the user wants masking after that, use `hide` on the specific files or directories you already identified.
