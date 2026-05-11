# Context Restore Skill

## Overview

The **Context Restore** skill provides utilities for restoring and presenting compressed context information from OpenClaw sessions. It reads compressed context files and generates formatted reports at various detail levels.

## Features

- **Multi-format Support**: Handles both JSON and plain text compressed context files
- **Three Report Levels**: `minimal`, `normal`, and `detailed` output formats
- **Automatic Extraction**: Parses metadata, projects, tasks, and operations
- **Compression Analysis**: Calculates and displays compression ratios
- **Flexible Output**: Display to stdout or save to file

## Directory Structure

```
skills/context-restore/
├── README.md                 # This documentation
├── SKILL.md                  # Skill metadata (if needed)
└── scripts/
    ├── restore_context.py    # Main script
    └── test_results.md       # Test execution results
```

## Installation

No additional installation required. The script uses only Python standard library modules:

- `argparse` - Command-line argument parsing
- `json` - JSON format handling
- `re` - Regular expression parsing
- `sys` - System utilities
- `pathlib` - File path operations

## Usage

### Basic Usage

```bash
# Run with default settings (normal level)
python3 skills/context-restore/scripts/restore_context.py
```

### Report Levels

```bash
# Minimal - Brief summary with counts only
python3 skills/context-restore/scripts/restore_context.py --level minimal

# Normal - Full details with descriptions (default)
python3 skills/context-restore/scripts/restore_context.py --level normal

# Detailed - Complete dump with raw content preview
python3 skills/context-restore/scripts/restore_context.py --level detailed
```

### Custom File Path

```bash
# Use a specific compressed context file
python3 skills/context-restore/scripts/restore_context.py --file /path/to/context.json

# Combine with level and output options
python3 skills/context-restore/scripts/restore_context.py \
    --file ./custom_context.json \
    --level detailed \
    --output report.md
```

### Output to File

```bash
# Save report to Markdown file
python3 skills/context-restore/scripts/restore_context.py --output context_report.md
```

### Get Help

```bash
python3 skills/context-restore/scripts/restore_context.py --help
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--file PATH` | Path to compressed context file | `./compressed_context/latest_compressed.json` |
| `--level LEVEL` | Report detail level | `normal` |
| `--output PATH` | Output file path (optional) | None (stdout) |
| `--help` | Show help message | - |
| `--version` | Show version | - |

### Level Options

| Level | Description | Contents |
|-------|-------------|----------|
| `minimal` | Brief summary | Message counts, project names, task names |
| `normal` | Full details | Metadata, operations, descriptions, status, highlights |
| `detailed` | Complete dump | All data + raw content preview (JSON format) |

## Output Format

### Minimal Report Example

```
============================================================
CONTEXT RESTORE REPORT (Minimal)
============================================================

📊 Context Status:
   Messages: 45 → 12

🚀 Key Projects (3)
   • Hermes Plan
   • Akasha Plan
   • Morning Brief

📋 Ongoing Tasks (3)
   • Isolated Sessions
   • Cron Tasks
   • Main Session

============================================================
```

### Normal Report Example

```
============================================================
CONTEXT RESTORE REPORT (Normal)
============================================================

📊 Context Compression Info:
   Original messages: 45
   Compressed messages: 12
   Timestamp: 2026-02-06T23:30:00.000
   Compression ratio: 26.7%

🔄 Recent Operations (4)
   • Context restoration performed
   • 11 cron tasks converted to isolated mode
   ...

🚀 Key Projects

   📁 Hermes Plan
      Description: Data analysis assistant for Excel, documents, and reports
      Status: Active

...

============================================================
```

## API Reference

### Main Functions

#### `restore_context(filepath: str, level: str = 'normal') -> str`

Restore context from compressed file and generate a formatted report.

**Parameters:**
- `filepath` (str): Path to the compressed context file
- `level` (str): Report detail level (`minimal`, `normal`, `detailed`)

**Returns:**
- `str`: Formatted report string

**Raises:**
- `ValueError`: If an invalid level is provided

**Example:**
```python
from restore_context import restore_context

report = restore_context('./compressed_context/latest.json', level='normal')
print(report)
```

### Helper Functions

#### `load_compressed_context(filepath: str) -> Optional[Any]`

Load compressed context from file.

**Parameters:**
- `filepath` (str): Path to the file

**Returns:**
- `dict` or `str` or `None`: JSON object if valid JSON, raw string otherwise, None on error

#### `parse_metadata(content: str) -> dict`

Extract metadata from plain text content.

**Parameters:**
- `content` (str): Raw text content

**Returns:**
- `dict`: Metadata with keys: `original_count`, `compressed_count`, `timestamp`

#### `extract_key_projects(content: str) -> list[dict]`

Extract key projects from context.

**Parameters:**
- `content` (str): Raw text content

**Returns:**
- `list[dict]`: List of projects with keys: `name`, `description`, `status`, `location`

#### `extract_ongoing_tasks(content: str) -> list[dict]`

Extract ongoing tasks from context.

**Parameters:**
- `content` (str): Raw text content

**Returns:**
- `list[dict]`: List of tasks with keys: `task`, `status`, `detail`

#### `extract_recent_operations(content: str) -> list[str]`

Extract recent operations from context.

**Parameters:**
- `content` (str): Raw text content

**Returns:**
- `list[str]`: List of operation descriptions

#### `calculate_compression_ratio(original: Optional[int], compressed: Optional[int]) -> Optional[float]`

Calculate compression ratio as percentage.

**Parameters:**
- `original` (int or None): Original message count
- `compressed` (int or None): Compressed message count

**Returns:**
- `float` or `None`: Compression percentage, or None if invalid

## Error Handling

The script includes comprehensive error handling for:

- **File Not Found**: Displays error message and returns exit code 1
- **Permission Denied**: Displays error message and returns exit code 1
- **Invalid JSON**: Falls back to plain text parsing
- **Invalid Arguments**: Shows help and returns exit code 1
- **Unexpected Errors**: Displays error details and returns exit code 1

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Error (file not found, invalid input, etc.) |

## Integration with OpenClaw

This skill is designed to work with OpenClaw's context compression system:

1. **Context Compression**: When sessions reach token limits, OpenClaw compresses context
2. **Storage**: Compressed context is saved to `compressed_context/latest_compressed.json`
3. **Restoration**: This script reads and presents the compressed context
4. **Analysis**: Helps identify session state and active components

## Supported Context Formats

### JSON Format
```json
{
  "content": "...",
  "metadata": {
    "original_count": 100,
    "compressed_count": 25
  }
}
```

### Plain Text Format
```
**上下文压缩于 2026-02-06T23:30:00.000**

原始消息数: 45  压缩后消息数: 12

**user:** 继续之前的工作...

**assistant:** ✅ 上下文已恢复
...
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "File not found" error | Check the file path with `--file` option |
| Empty output | Verify the compressed context file has content |
| Incorrect parsing | Try `--level detailed` to see raw content |
| Permission denied | Check file/directory permissions |

### Debug Mode

For debugging, use the detailed level to see raw content:

```bash
python3 restore_context.py --level detailed --output debug.md
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-06 | Initial release |

## License

Part of the OpenClaw project.
