# Document Parser

> OpenClaw Skill - High-precision document parsing

Extract structured data from PDF, images, and Word documents.

## Features

- ✅ **Multi-format Support**: PDF, Images (JPG/PNG), Word documents
- ✅ **Layout Analysis**: Automatically detect and structure document elements
- ✅ **Table Recognition**: Extract tables with HTML and Markdown outputs
- ✅ **OCR Support**: Recognize text in scanned documents and images
- ✅ **Seal Detection**: Detect stamps and seals in documents
- ✅ **TOC Extraction**: Extract table of contents from documents
- ✅ **Cross-page Merge**: Automatically merge content across pages

## Quick Start

### Installation

```bash
# Install via ClawHub
openclaw skills install document-parser

# Or manual installation (local development)
cd E:\skills\document-parser
pip install -r requirements.txt
```

### Configuration

**Option 1: Environment Variables (Recommended)**
```bash
# Windows PowerShell
$env:DOCUMENT_PARSER_API_KEY="your_api_key"
setx DOCUMENT_PARSER_API_KEY "your_api_key"

# Optional: Custom API endpoint
$env:DOCUMENT_PARSER_BASE_URL="http://your-server:8088/taidp/v1/idp/general_parse"
```

**Option 2: Configuration File**
```bash
cd E:\skills\document-parser
copy config.example.json config.json
# Edit config.json with your API Key
```

### Usage

#### Parse a Document
```bash
# Basic parsing
document-parser parse "C:\docs\report.pdf"

# Enable layout analysis and table recognition
document-parser parse "C:\docs\report.pdf" --layout --table

# Specify output format
document-parser parse "C:\docs\scan.jpg" --output markdown

# Specify page range
document-parser parse "C:\docs\book.pdf" --pages 1-5,10-15
```

#### Query Task Status
```bash
document-parser status <task_id>
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | string | Yes | PDF/Image/Word file path |
| --layout | flag | No | Enable layout analysis |
| --table | flag | No | Enable table recognition |
| --seal | flag | No | Enable seal recognition |
| --output | string | No | Output format: json/markdown/both |
| --pages | string | No | Page range, e.g., "1-5,8,10-12" |

## Output Format

Returns structured JSON containing:

```json
{
  "code": 10000,
  "message": "Success",
  "request_id": "xxx-xxx-xxx",
  "elapsed_time": 8.5,
  "pages": [
    {
      "page_no": 1,
      "height": 1654,
      "width": 1169,
      "elements": [...]
    }
  ],
  "markdown": "Parsed Markdown text"
}
```

## Supported Document Elements

| Type | Description |
|------|-------------|
| DocumentTitle | Document title |
| LevelTitle | Section heading |
| Paragraph | Text paragraph |
| Table | Table |
| Image | Image |
| PageHeader | Header |
| PageFooter | Footer |
| Seal | Seal/Stamp |
| Formula | Mathematical formula |
| TableOfContents | Table of contents |

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 10000 | Success | Parsing successful |
| 10001 | Missing parameter | Missing required parameter |
| 10002 | Invalid parameter | Invalid parameter value |
| 10003 | Invalid file | Unsupported file format |
| 10004 | Failed to recognize | Recognition failed |
| 10005 | Internal error | Internal server error |

## Examples

### Parse PDF and extract tables
```bash
document-parser parse "C:\docs\financial_report.pdf" --table --output markdown
```

### Parse scanned document with OCR
```bash
document-parser parse "C:\docs\scanned_contract.jpg" --layout
```

### Parse Word document
```bash
document-parser parse "C:\docs\manual.docx" --output json
```

## Dependencies

- Python 3.8+
- requests>=2.28.0
- python-docx>=0.8.11
- Pillow>=9.0.0

## License

MIT License

## Support

File an issue or contact the author for help.
