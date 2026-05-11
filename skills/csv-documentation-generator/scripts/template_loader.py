"""Template loader for CSV documentation generator"""

import os
import re
from typing import Dict, Any, Optional
from pathlib import Path


class TemplateLoader:
    """Load and process document templates"""

    def __init__(self, templates_dir: Optional[str] = None):
        if templates_dir is None:
            # Default to templates directory relative to this file
            self.templates_dir = Path(__file__).parent.parent / "templates"
        else:
            self.templates_dir = Path(templates_dir)

    def load_template(self, doc_type: str) -> str:
        """Load template content by document type"""
        template_file = self.templates_dir / f"{doc_type}.md"

        if not template_file.exists():
            # Check if it's an Excel template
            xlsx_file = self.templates_dir / f"{doc_type}.xlsx"
            if xlsx_file.exists():
                return str(xlsx_file)
            raise FileNotFoundError(f"Template not found: {doc_type}")

        with open(template_file, "r", encoding="utf-8") as f:
            return f.read()

    def load_excel_template(self, doc_type: str) -> str:
        """Load Excel template path"""
        template_file = self.templates_dir / f"{doc_type}.xlsx"

        if not template_file.exists():
            raise FileNotFoundError(f"Excel template not found: {doc_type}")

        return str(template_file)

    def process_template(self, content: str, variables: Dict[str, str]) -> str:
        """Replace template variables with actual values"""
        result = content

        for key, value in variables.items():
            # Replace {VARIABLE} format
            result = result.replace(f"{{{key}}}", value)

            # Also replace $VARIABLE format
            result = result.replace(f"${key}", value)

        return result

    def get_available_templates(self) -> list:
        """Get list of available template types"""
        templates = []

        if not self.templates_dir.exists():
            return templates

        for file in self.templates_dir.iterdir():
            if file.suffix in [".md", ".xlsx"]:
                templates.append(file.stem)

        return sorted(templates)


def process_markdown_table_bilingual(
    content: str, bilingual: bool = True, language: str = "zh"
) -> str:
    """
    Process bilingual markdown tables based on bilingual and language settings.

    Args:
        content: Markdown content
        bilingual: If True, headers remain bilingual; content follows language
                  If False, all content is single language based on --language
        language: Primary language for content ('zh' or 'en')

    Bilingual format expected: "中文 / English" or "English / 中文"
    - First part is Chinese
    - Second part is English
    """
    lines = content.split("\n")
    result = []

    in_table = False
    is_header_row = True

    for line in lines:
        # Check if line is a table separator
        if re.match(r"^\|[\s\-:|]+\|$", line):
            result.append(line)
            is_header_row = False
            continue

        # Table start
        if "|" in line and not in_table:
            in_table = True
            is_header_row = True

        # Process table content
        if in_table and "|" in line:
            cells = line.split("|")
            processed_cells = []

            for i, cell in enumerate(cells):
                cell = cell.strip()

                # Check if cell contains bilingual content (has / separator)
                if "/" in cell and not cell.startswith("-"):
                    parts = [p.strip() for p in cell.split("/") if p.strip()]

                    if len(parts) >= 2:
                        # Determine which is Chinese and which is English
                        # Chinese typically has Chinese characters
                        chinese_part = None
                        english_part = None

                        for p in parts:
                            if re.search(r"[\u4e00-\u9fff]", p):
                                chinese_part = p
                            else:
                                english_part = p

                        if bilingual:
                            if is_header_row:
                                # Headers stay bilingual: "中文 / English"
                                cell = f"{chinese_part or parts[0]} / {english_part or parts[-1]}"
                            else:
                                # Content follows language setting
                                cell = (
                                    chinese_part if language == "zh" else english_part
                                )
                                if cell is None:
                                    cell = parts[0]
                        else:
                            # Not bilingual mode - single language only
                            cell = chinese_part if language == "zh" else english_part
                            if cell is None:
                                cell = parts[0]

                processed_cells.append(cell)

            line = "|".join(processed_cells)
            result.append(line)
            is_header_row = False
        else:
            # Non-table content
            if in_table:
                in_table = False
            result.append(line)

    return "\n".join(result)
