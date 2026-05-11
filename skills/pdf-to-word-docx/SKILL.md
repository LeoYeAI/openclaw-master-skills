---
name: pdf-to-word-docx
version: 1.0.0
description: PDF conversion toolkit featuring AI layout analysis and OCR. Converts PDFs to Word/Docx, Markdown, JSON, PPT, CSV, HTML, and XML for seamless LLM data processing.
homepage: https://www.compdf.com
metadata:
  clawdbot:
    emoji: "📑"
    requires:
      env: []
    files: ["scripts/*"]
compatibility: Requires Windows or macOS. Python with ComPDFKitConversion package (pip install ComPDFKitConversion). AI model (~525MB) auto-downloaded on first run.
---

# pdf to word

## Purpose
- Wraps the `ComPDFKitConversion` Python SDK into a reusable local conversion workflow, supporting PDF / image to Word, PPT, Excel, HTML, RTF, Image, TXT, JSON, Markdown, and CSV (10 output formats in total).

## Agent Skills Standard Compatibility
- This Skill uses an Anthropic Agent Skills-compatible directory structure: `pdf-to-word-docx/`.
- The entry point is `SKILL.md`; helper scripts are placed in `scripts/`.
- The document uses `$ARGUMENTS` and `${CLAUDE_SKILL_DIR}` conventions for distribution and execution in Claude Code / Agent Skills-compatible environments.

## Input / Output
- Input: The target format (`word`/`excel`/`ppt`/`html`/`rtf`/`image`/`txt`/`json`/`markdown`/`csv`), the PDF or image path, and the output path are passed via Skill arguments or the command line. An optional PDF password and conversion parameters may also be provided.
- Supported input file types:
  - PDF files (`.pdf`)
  - Image files (`.jpg`/`.jpeg`/`.png`/`.bmp`/`.tif`/`.tiff`/`.webp`/`.jp2`/`.gif`/`.tga`)
- Output: A file in the corresponding format (`.docx`, `.pptx`, `.xlsx`, `.html`, `.rtf`, image, `.txt`, `.json`, `.md`, `.csv`), or a clear error message.

## Prerequisites
- Supports Windows and macOS.
- The conversion SDK must be installed first:
  ```bash
  pip install ComPDFKitConversion
  ```
- On first run, the script automatically downloads `license.xml` from the ComPDF server and caches it in the `scripts/` directory:
  ```text
  https://download.compdf.com/skills/license/license.xml
  ```
- The script reads the `<key>...</key>` field from `license.xml` and uses that key for `LibraryManager.license_verify(...)` authentication — it does not pass the XML file path directly to the SDK.
- To use a custom license, place your own `license.xml` in the `scripts/` directory; the script will use it directly without downloading.
- During SDK initialization, the `resource` directory is always set to the directory containing `pdf-to-word-docx.py`, i.e., the `scripts/` directory itself.
- When `--enable-ocr` or `--enable-ai-layout` (enabled by default) is used, the Skill also requires `scripts/documentai.model`. If the file does not exist, the script will automatically download it from:
  ```text
  https://download.compdf.com/skills/model/documentai.model
  ```
- To reuse an existing model file, you can override the default model path via an environment variable:
  ```bash
  export COMPDF_DOCUMENT_AI_MODEL="/path/to/documentai.model"
  ```

## Workflow
1. Confirm the Python package is installed:
   ```bash
   python -m pip show ComPDFKitConversion
   ```
2. The script automatically downloads `license.xml` on first run; the `scripts/` directory is used directly as the SDK `resource` path.
3. In Agent Skills / Claude Code environments, prefer using the Skill's built-in script path variable:
   ```bash
   python "${CLAUDE_SKILL_DIR}/scripts/pdf-to-word-docx.py" word input.pdf output.docx
   python "${CLAUDE_SKILL_DIR}/scripts/pdf-to-word-docx.py" ppt input.pdf output.pptx
   python "${CLAUDE_SKILL_DIR}/scripts/pdf-to-word-docx.py" excel input.pdf output.xlsx
   ```
4. For more control, append common parameters:
   ```bash
   python "${CLAUDE_SKILL_DIR}/scripts/pdf-to-word-docx.py" excel input.pdf output.xlsx --page-ranges "1-3,5" --excel-all-content --excel-worksheet-option for-page
   python "${CLAUDE_SKILL_DIR}/scripts/pdf-to-word-docx.py" word input.pdf output.docx --enable-ocr --page-layout-mode flow
   ```
5. On startup, the script ensures `scripts/license.xml` exists (downloading it automatically from the ComPDF server if missing), reads the `<key>` field for SDK authentication, and uses the `scripts/` directory as the `resource` path.
6. If `--enable-ocr` or `--enable-ai-layout` (enabled by default) is active, the script checks whether `scripts/documentai.model` exists; if not, it downloads the file automatically before initializing the Document AI model.
7. Check the return code; if it is not `SUCCESS`, handle license, password, resource, model, or input file issues according to the error name.

## documentai.model Download Optimization
- The script preferentially uses the model file pointed to by `COMPDF_DOCUMENT_AI_MODEL`.
- The default model path is `scripts/documentai.model`.
- During automatic download, the file is first written to `documentai.model.part` and then atomically renamed to the final file upon success, preventing partial file corruption.
- On download failure, the script retries automatically with back-off intervals of `2s / 5s / 10s`.

## Invoking Directly as a Skill
- In environments that support Agent Skills, the Skill can be called directly:
  ```text
  /pdf-to-word-docx word input.pdf output.docx
  /pdf-to-word-docx excel input.pdf output.xlsx --excel-worksheet-option for-page
  ```
- When the Skill receives arguments, it passes them through to the script as-is:
  ```bash
  python "${CLAUDE_SKILL_DIR}/scripts/pdf-to-word-docx.py" $ARGUMENTS
  ```
- If the environment does not support direct Skill invocation, fall back to a regular command-line call.

## Supported Output Formats
- `word` → calls `CPDFConversion.start_pdf_to_word`
- `excel` → calls `CPDFConversion.start_pdf_to_excel`
- `ppt` → calls `CPDFConversion.start_pdf_to_ppt`
- `html` → calls `CPDFConversion.start_pdf_to_html`
- `rtf` → calls `CPDFConversion.start_pdf_to_rtf`
- `image` → calls `CPDFConversion.start_pdf_to_image`
- `txt` → calls `CPDFConversion.start_pdf_to_txt`
- `json` → calls `CPDFConversion.start_pdf_to_json`
- `markdown` → calls `CPDFConversion.start_pdf_to_markdown`
- `csv` → reuses `CPDFConversion.start_pdf_to_excel` with table/Excel parameters to produce CSV-friendly output

## Input Source Types
- The script supports **PDF and image** as input sources. The SDK's `start_pdf_to_*` interfaces natively accept image files with no pre-processing required.
- By default, the script auto-detects the input type from the file extension:
  - `.pdf` → `pdf`
  - `.png/.jpg/.jpeg/.bmp/.tif/.tiff/.gif/.webp/.tga` → `image`
- You can also specify the source type explicitly:
  ```bash
  python "${CLAUDE_SKILL_DIR}/scripts/pdf-to-word-docx.py" word input.png output.docx --source-type image
  ```
- `image -> *` and `pdf -> *` share the same set of `CPDFConversion.start_pdf_to_*` interfaces; only the input file type differs.

## Smart Defaults
The script automatically adjusts certain parameters based on the input source and output format to reduce manual configuration:

| Trigger | Automatic Behavior | User-Overridable | Description |
|----------|----------|-------------|------|
| Input source is an **image** (auto-detected or explicit `--source-type image`) | Automatically enables `--enable-ocr` | No (`--enable-ocr` uses `store_true`; there is no `--no-enable-ocr`) | Text in images must be extracted via OCR; without OCR, output will contain only images and no text |
| Output format is **HTML** (`format = html`) | Automatically sets `--page-layout-mode` to `box` (box layout) | Yes — passing `--page-layout-mode flow` explicitly overrides this | Box layout better preserves the original formatting in HTML; specify `flow` explicitly if flow layout is needed |

When triggered, the script prints a notice to `stderr`, for example:
```text
Auto-enabled OCR for image input.
Auto-set page layout mode to BOX for HTML output.
```

## All Parameters

### Positional Parameters
| Parameter | Description |
|------|------|
| `format` | Target format: `word`/`excel`/`ppt`/`html`/`rtf`/`image`/`txt`/`json`/`markdown`/`csv` |
| `input_pdf` | Input file path (PDF or image) |
| `output_path` | Output file path |

### General Parameters
| Parameter | Type | Default | Description |
|------|------|--------|------|
| `--source-type` | Option | `auto` | Input source type: `auto`/`pdf`/`image` |
| `--password` | String | `""` | PDF open password |
| `--page-ranges` | String | None | Page range, e.g. `1-3,5` |
| `--font-name` | String | `""` | Output font name |

### Layout Parameters
| Parameter | Type | Default | Description |
|------|------|--------|------|
| `--enable-ai-layout` | Boolean | **True** | AI layout analysis (disable with `--no-enable-ai-layout`) |
| `--page-layout-mode` | Option | SDK default `flow` (auto-switched to `box` for HTML output) | Page layout: `box` (box layout) / `flow` (flow layout) |

### Content Retention Parameters
| Parameter | Type | Default | Description |
|------|------|--------|------|
| `--contain-image` | Boolean | **True** | Retain images (disable with `--no-contain-image`) |
| `--contain-annotation` | Boolean | **True** | Retain annotations (disable with `--no-contain-annotation`) |
| `--contain-page-background-image` | Boolean | **True** | Retain page background images (disable with `--no-contain-page-background-image`) |
| `--formula-to-image` | Boolean | False | Convert formulas to image output |
| `--transparent-text` | Boolean | False | Preserve transparent text |

### Output Control Parameters
| Parameter | Type | Default | Description |
|------|------|--------|------|
| `--output-document-per-page` | Boolean | False | Split output into one document per page |
| `--auto-create-folder` | Boolean | **True** | Automatically create output directory (disable with `--no-auto-create-folder`) |

### OCR Parameters
| Parameter | Type | Default | Description |
|------|------|--------|------|
| `--enable-ocr` | Boolean | False (auto-enabled for image input) | Enable OCR |
| `--ocr-option` | Option | SDK default `all` | OCR scope: `invalid-character`/`scan-page`/`invalid-character-and-scan-page`/`all` |
| `--ocr-language` | Multi-select | `auto` | OCR language(s); multiple languages can be specified simultaneously. Options: `auto`/`chinese`/`chinese-tra`/`english`/`korean`/`japanese`/`latin`/`devanagari`/`cyrillic`/`arabic`/`tamil`/`telugu`/`kannada`/`thai`/`greek`/`eslav` |

### Excel-Specific Parameters
| Parameter | Type | Default | Description |
|------|------|--------|------|
| `--excel-all-content` | Boolean | False | Include all content in Excel output |
| `--excel-csv-format` | Boolean | False | Output Excel result in CSV format |
| `--excel-worksheet-option` | Option | SDK default `for-table` | Worksheet split strategy: `for-table`/`for-page`/`for-document` |

### JSON-Specific Parameters
| Parameter | Type | Default | Description |
|------|------|--------|------|
| `--json-contain-table` | Boolean | **True** | Include table data in JSON output (disable with `--no-json-contain-table`) |

### TXT-Specific Parameters
| Parameter | Type | Default | Description |
|------|------|--------|------|
| `--txt-table-format` | Boolean | **True** | Enable table formatting in TXT output (disable with `--no-txt-table-format`) |

### HTML-Specific Parameters
| Parameter | Type | Default | Description |
|------|------|--------|------|
| `--html-option` | Option | SDK default `single-page` | HTML output mode: `single-page`/`single-page-with-bookmark`/`multiple-page`/`multiple-page-with-bookmark` |

### Image-Specific Parameters
| Parameter | Type | Default | Description |
|------|------|--------|------|
| `--image-type` | Option | SDK default `jpg` | Image output format: `jpg`/`jpeg`/`jpeg2000`/`png`/`bmp`/`tiff`/`tga`/`gif`/`webp` |
| `--image-color-mode` | Option | SDK default `color` | Image color mode: `color`/`gray`/`binary` |
| `--image-scaling` | Float | `1.0` | Image scaling factor |
| `--image-path-enhance` | Boolean | False | Enable image path enhancement |

### Parameter Default Value Rules
- **Parameters that default to True** (`--enable-ai-layout`/`--contain-image`/`--contain-annotation`/`--contain-page-background-image`/`--auto-create-folder`/`--json-contain-table`/`--txt-table-format`) use `BooleanOptionalAction`; pass `--no-xxx` to disable.
- **Parameters that default to False** (`--enable-ocr`/`--formula-to-image`/`--transparent-text`/`--output-document-per-page`/`--excel-all-content`/`--excel-csv-format`/`--image-path-enhance`) use `store_true`; passing the flag enables them.
- **All CLI parameter defaults are fully consistent with the SDK's `ConvertOptions()` defaults** — omitting a parameter is equivalent to using the SDK's original default value.

## Recommended Command Examples

### PDF to Word (default parameters, AI layout analysis enabled)
```bash
python "${CLAUDE_SKILL_DIR}/scripts/pdf-to-word-docx.py" word input.pdf output.docx
```

### PDF to Word, box layout, no images, no AI layout analysis
```bash
python "${CLAUDE_SKILL_DIR}/scripts/pdf-to-word-docx.py" word input.pdf output.docx --no-enable-ai-layout --no-contain-image --page-layout-mode box
```

### PDF to Word, retain annotations and background images, one document per page
```bash
python "${CLAUDE_SKILL_DIR}/scripts/pdf-to-word-docx.py" word input.pdf output.docx --output-document-per-page
```

### PDF to Excel, include all content and split worksheets by page
```bash
python "${CLAUDE_SKILL_DIR}/scripts/pdf-to-word-docx.py" excel input.pdf output.xlsx --excel-all-content --excel-worksheet-option for-page
```

### PDF to TXT, with table formatting enabled
```bash
python "${CLAUDE_SKILL_DIR}/scripts/pdf-to-word-docx.py" txt input.pdf output.txt
```

### PDF to HTML, multi-page with bookmarks mode
```bash
python "${CLAUDE_SKILL_DIR}/scripts/pdf-to-word-docx.py" html input.pdf output_dir --html-option multiple-page-with-bookmark
```

### PDF to Image, PNG format, grayscale, 2x scaling
```bash
python "${CLAUDE_SKILL_DIR}/scripts/pdf-to-word-docx.py" image input.pdf output.png --image-type png --image-color-mode gray --image-scaling 2.0
```

### Image to Word (OCR auto-enabled, specify Chinese language)
```bash
python "${CLAUDE_SKILL_DIR}/scripts/pdf-to-word-docx.py" word input.png output.docx --ocr-language chinese
```
> Note: For image input, the script automatically enables OCR — there is no need to pass `--enable-ocr` manually. To specify an OCR language, `--ocr-language` can still be used.

### PDF with OCR enabled (multiple languages)
```bash
python "${CLAUDE_SKILL_DIR}/scripts/pdf-to-word-docx.py" word input.pdf output.docx --enable-ocr --ocr-language chinese english japanese
```

## Trial License and Usage Limits
- The `scripts/license.xml` auto-downloaded from the ComPDF server is a **Trial License**, allowing a maximum of **200 conversions**.
- The script uses a SHA-256 fingerprint to detect whether the current License is the default trial key; **no usage limit applies when using any other License**.
- After each successful conversion using the trial License, the script prints the current used/remaining count to `stderr`, for example:
  ```text
  Trial license: 5/200 conversions used, 195 remaining.
  ```
- When the trial limit is reached (200 conversions), the script refuses to convert and prompts the user to purchase a full License:
  ```text
  Error: Trial license usage limit reached (200 conversions). Please purchase a license at: https://www.compdf.com/contact-sales
  ```
- When the trial License has expired (SDK authentication fails), the error message also includes a purchase link.
- **After purchasing a full License**, place a custom `license.xml` containing the new `<key>` in `scripts/` (overwriting the auto-downloaded trial file) — no script modifications or counter file cleanup are required.

## Confirmed Facts
- `ComPDFKitConversion 3.9.0` has been successfully installed on the local machine.
- The installed package provides 10 conversion methods including `CPDFConversion.start_pdf_to_word/start_pdf_to_ppt/start_pdf_to_excel`.
- `LibraryManager` provides `initialize`, `license_verify`, `release`, `set_document_ai_model`, and `set_ocr_language`.
- Official documentation confirms support for PDF to Word / Excel / PPT / HTML / RTF / Image / TXT / JSON / Markdown.
- The SDK's `start_pdf_to_*` interfaces natively accept image file input (PNG → Word has been verified successfully).
- `enable_ai_layout` defaults to `True` in the SDK; `set_document_ai_model()` must be called first to load the model before use, otherwise a 0xC0000005 crash will occur.
- `--ocr-language` supports specifying multiple languages simultaneously (e.g. `--ocr-language chinese english`).

## Risks / Notes
- The official requirements page states Python `>=3.6`, while the demo page states `<3.11`, but PyPI currently provides a `cp314` wheel in practice; treat the locally installable wheel as the source of truth, but always verify installation in a new environment first.
- If the script cannot download `license.xml` from the server (network issue) and no manual file exists in `scripts/`, or the `<key>` field is empty, the script cannot complete SDK authentication and cannot perform any real conversions.
- `documentai.model` is a large file (approximately 525 MB); there will be a noticeable download delay the first time OCR / AI layout is enabled. Because `--enable-ai-layout` defaults to True, **the model download will be triggered on the very first run**.
- If the runtime environment cannot access `https://download.compdf.com/skills/model/documentai.model`, place `documentai.model` in the `scripts/` directory in advance.
- Do not directly apply the initialization patterns from ComPDF SDKs for other languages to the Python package; this Skill is based on the locally verified `LibraryManager` / `CPDFConversion` API.

## Resource Navigation
- License file: `License.txt`
- Script: `scripts/pdf-to-word-docx.py`
- SDK authentication file: `scripts/license.xml` (auto-downloaded from `https://download.compdf.com/skills/license/license.xml` if missing)
- SDK authentication source: the `<key>` field in `license.xml`
- SDK resource path: `scripts/`
- OCR / AI layout model: `scripts/documentai.model` (auto-downloaded if missing)
- Purchase a full License: `https://www.compdf.com/contact-sales`
- Official documentation:
  - `https://www.compdf.com/guides/conversion-sdk/python/overview`
  - `https://www.compdf.com/guides/conversion-sdk/python/pdf-to-word`
  - `https://www.compdf.com/guides/conversion-sdk/python/pdf-to-excel`
  - `https://www.compdf.com/guides/conversion-sdk/python/pdf-to-ppt`
  - `https://www.compdf.com/guides/conversion-sdk/python/apply-license`

## Acceptance Checklist
- [ ] `python -m pip show ComPDFKitConversion` shows the installed package
- [ ] Running `python "${CLAUDE_SKILL_DIR}/scripts/pdf-to-word-docx.py" --help` or an equivalent local command produces normal output
- [ ] The script auto-downloads `scripts/license.xml` if missing, then extracts the license key from the `<key>` field for authentication
- [ ] The script uses the `scripts/` directory as the SDK resource path
- [ ] The script recognizes all 10 target formats: `word`/`excel`/`ppt`/`html`/`rtf`/`image`/`txt`/`json`/`markdown`/`csv`
- [ ] The script accepts both PDF and image files (`.png`/`.jpg`/`.jpeg`/`.bmp`/`.tif`/`.tiff`/`.gif`/`.webp`/`.tga`) as input
- [ ] When `--enable-ocr` or `--enable-ai-layout` (enabled by default) is active and `documentai.model` is missing, the script auto-downloads the model
- [ ] When `license.xml` cannot be obtained (download fails and no manual file exists) or authentication fails, a clear error is output rather than a silent failure
- [ ] The 7 parameters that default to True can be disabled with `--no-xxx`
- [ ] `--ocr-language` supports specifying multiple languages simultaneously
- [ ] After a conversion using the trial License, the usage count increments
- [ ] When the trial License reaches 200 conversions, the script refuses to convert and outputs a purchase link
- [ ] When using a non-trial License, no usage limit applies
- [ ] For image input, even if `--enable-ocr` is not passed, the script automatically enables OCR and prints a notice to `stderr`
- [ ] For HTML output, even if `--page-layout-mode` is not passed, the script automatically uses `box` (box layout) and prints a notice to `stderr`
- [ ] For HTML output, explicitly passing `--page-layout-mode flow` overrides the automatic box layout behavior

## Distribution Notes
- This Skill does not depend on any machine-specific absolute paths.
- When distributing to other users, the following directory structure is sufficient:
  ```text
  pdf-to-word-docx/
  ├── SKILL.md
  ├── License.txt
  └── scripts/
      └── pdf-to-word-docx.py
  ```
- Users place this directory under their own skills root directory and the Skill is ready to use.
- `license.xml` is auto-downloaded at runtime; no need to include it in the distribution package.

## Common Pitfalls
- `scripts/license.xml` is missing and cannot be auto-downloaded (network unavailable or server error): the script will error out before authentication. If you are in an offline environment, place `license.xml` manually in the `scripts/` directory.
- `scripts/license.xml` is missing the `<key>` field or its value is empty: the script will error out before authentication.
- SDK resource files required by the SDK are absent from the `scripts/` directory: conversion may fail after `LibraryManager.initialize()`.
- A password-protected PDF is provided without `--password`: this will trigger `PDF_PASSWORD_ERROR`.
- OCR / AI layout is enabled but `documentai.model` is not present locally and the network is unavailable: the model download will fail; place the file in the `scripts/` directory manually in advance.
- When the Excel output strategy is unclear, prefer passing `--excel-worksheet-option` explicitly to avoid unexpected result structures.
- When converting images to other formats, the script already enables OCR automatically; if the output still contains no text, check whether `documentai.model` is complete and whether the OCR language matches.
- Once the trial License usage limit is exhausted, a full License must be purchased to continue; purchase link: `https://www.compdf.com/contact-sales`.

## Copyright

This Skill is built on top of the [ComPDFKit Conversion SDK](https://www.compdf.com).

```
© 2014-2026 PDF Technologies, Inc., a KDAN Company. All Rights Reserved.
```

- **SDK Name**: ComPDFKitConversion
- **SDK Author**: PDF Technologies, Inc.
- **License Type**: Commercial License (Commercial / Proprietary) — non-exclusive, non-transferable, non-sublicensable, revocable
- **Official Website**: https://www.compdf.com
- **Contact**: support@compdf.com
- **Terms of Service**: https://www.compdf.com/terms-of-service
- **Privacy Policy**: https://www.compdf.com/privacy-policy

> **Important**: Under the ComPDFKit Terms of Service, distributing the documentation, sample code, or source code of the ComPDFKit Conversion SDK to third parties is prohibited. Please ensure you have obtained a valid ComPDFKit License before using this Skill.
