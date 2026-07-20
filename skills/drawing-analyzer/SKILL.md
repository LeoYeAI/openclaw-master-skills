---
name: "drawing-analyzer"
description: "Analyze construction drawings to extract dimensions, annotations, symbols, and metadata. Support quantity takeoff and design review automation."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "📑", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Drawing Analyzer for Construction

## Overview

Analyze construction drawings (PDF, DWG) to extract dimensions, annotations, symbols, title block data, and support automated quantity takeoff and design review.

## Business Case

Drawing analysis automation enables:
- **Faster Takeoffs**: Extract quantities from drawings
- **Quality Control**: Verify drawing completeness
- **Data Extraction**: Pull metadata for project systems
- **Design Review**: Automated checking against standards

## Technical Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import re
import pdfplumber
from pathlib import Path

@dataclass
class TitleBlockData:
    project_name: str
    project_number: str
    sheet_number: str
    sheet_title: str
    discipline: str
    scale: str
    date: str
    revision: str
    drawn_by: str
    checked_by: str
    approved_by: str

@dataclass
class Dimension:
    value: float
    unit: str
    dimension_type: str  # linear, angular, radial
    location: Tuple[float, float]
    associated_text: str

@dataclass
class Annotation:
    text: str
    annotation_type: str  # note, callout, tag, keynote
    location: Tuple[float, float]
    references: List[str]

@dataclass
class Symbol:
    symbol_type: str  # door, window, equipment, etc.
    tag: str
    location: Tuple[float, float]
    properties: Dict[str, Any]

@dataclass
class DrawingAnalysisResult:
    file_name: str
    title_block: Optional[TitleBlockData]
    dimensions: List[Dimension]
    annotations: List[Annotation]
    symbols: List[Symbol]
    scale_factor: float
    drawing_area: Tuple[float, float]
    quality_issues: List[str]

class DrawingAnalyzer:
    """Analyze construction drawings for data extraction."""

    # Common dimension patterns
    DIMENSION_PATTERNS = [
        r"(\d+'-\s*\d+(?:\s*\d+/\d+)?\"?)",  # Feet-inches: 10'-6", 10' - 6 1/2"
        r"(\d+(?:\.\d+)?)\s*(?:mm|cm|m|ft|in)",  # Metric/imperial with unit
        r"(\d+'-\d+\")",  # Compact feet-inches
        r"(\d+)\s*(?:SF|LF|CY|EA)",  # Quantity dimensions
    ]

    # Common annotation patterns
    ANNOTATION_PATTERNS = {
        'keynote': r'^\d{1,2}[A-Z]?$',  # 1A, 12, 5B
        'room_tag': r'^(?:RM|ROOM)\s*\d+',
        'door_tag': r'^[A-Z]?\d{2,3}[A-Z]?$',
        'grid_line': r'^[A-Z]$|^\d+$',
        'elevation': r'^(?:EL|ELEV)\.?\s*\d+',
        'detail_ref': r'^\d+/[A-Z]\d+',
    }

    # Scale patterns
    SCALE_PATTERNS = [
        r"SCALE:\s*(\d+(?:/\d+)?)\s*[\"']\s*=\s*(\d+)\s*['\-]",  # 1/4" = 1'-0"
        r"(\d+):(\d+)",  # 1:100
        r"NTS|NOT TO SCALE",
    ]

    def __init__(self):
        self.results: Dict[str, DrawingAnalysisResult] = {}

    def analyze_pdf_drawing(self, pdf_path: str) -> DrawingAnalysisResult:
        """Analyze a PDF drawing."""
        path = Path(pdf_path)

        all_text = ""
        dimensions = []
        annotations = []
        symbols = []
        quality_issues = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Extract text
                text = page.extract_text() or ""
                all_text += text + "\n"

                # Extract dimensions
                page_dims = self._extract_dimensions(text)
                dimensions.extend(page_dims)

                # Extract annotations
                page_annots = self._extract_annotations(text)
                annotations.extend(page_annots)

                # Extract from tables (often contain schedules)
                tables = page.extract_tables()
                for table in tables:
                    symbols.extend(self._parse_schedule_table(table))

        # Parse title block
        title_block = self._extract_title_block(all_text)

        # Determine scale
        scale_factor = self._determine_scale(all_text)

        # Quality checks
        quality_issues = self._check_drawing_quality(
            title_block, dimensions, annotations
        )

        result = DrawingAnalysisResult(
            file_name=path.name,
            title_block=title_block,
            dimensions=dimensions,
            annotations=annotations,
            symbols=symbols,
            scale_factor=scale_factor,
            drawing_area=(0, 0),  # Would need image analysis
            quality_issues=quality_issues
        )

        self.results[path.name] = result
        return result

    def _extract_dimensions(self, text: str) -> List[Dimension]:
        """Extract dimensions from text."""
        dimensions = []

        for pattern in self.DIMENSION_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                value, unit = self._parse_dimension_value(match)
                if value > 0:
                    dimensions.append(Dimension(
                        value=value,
                        unit=unit,
                        dimension_type='linear',
                        location=(0, 0),
                        associated_text=match
                    ))

        return dimensions

    def _parse_dimension_value(self, dim_text: str) -> Tuple[float, str]:
        """Parse dimension text to value and unit."""
        dim_text = dim_text.strip()

        # Feet and inches: 10'-6"
        ft_in_match = re.match(r"(\d+)'[-\s]*(\d+)?(?:\s*(\d+)/(\d+))?\"?", dim_text)
        if ft_in_match:
            feet = int(ft_in_match.group(1))
            inches = int(ft_in_match.group(2) or 0)
            if ft_in_match.group(3) and ft_in_match.group(4):
                inches += int(ft_in_match.group(3)) / int(ft_in_match.group(4))
            return feet * 12 + inches, 'in'

        # Metric with unit
        metric_match = re.match(r"(\d+(?:\.\d+)?)\s*(mm|cm|m)", dim_text)
        if metric_match:
            return float(metric_match.group(1)), metric_match.group(2)

        # Just a number
        num_match = re.match(r"(\d+(?:\.\d+)?)", dim_text)
        if num_match:
            return float(num_match.group(1)), ''

        return 0, ''

    def _extract_annotations(self, text: str) -> List[Annotation]:
        """Extract annotations from text."""
        annotations = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            for annot_type, pattern in self.ANNOTATION_PATTERNS.items():
                if re.match(pattern, line, re.IGNORECASE):
                    annotations.append(Annotation(
                        text=line,
                        annotation_type=annot_type,
                        location=(0, 0),
                        references=[]
                    ))
                    break

            # General notes
            if line.startswith(('NOTE:', 'SEE ', 'REFER TO', 'TYP', 'U.N.O.')):
                annotations.append(Annotation(
                    text=line,
                    annotation_type='note',
                    location=(0, 0),
                    references=[]
                ))

        return annotations

    def _extract_title_block(self, text: str) -> Optional[TitleBlockData]:
        """Extract title block information."""
        # Common title block patterns
        patterns = {
            'project_name': r'PROJECT(?:\s*NAME)?:\s*(.+?)(?:\n|$)',
            'project_number': r'(?:PROJECT\s*)?(?:NO|NUMBER|#)\.?:\s*(\S+)',
            'sheet_number': r'SHEET(?:\s*NO)?\.?:\s*([A-Z]?\d+(?:\.\d+)?)',
            'sheet_title': r'SHEET\s*TITLE:\s*(.+?)(?:\n|$)',
            'scale': r'SCALE:\s*(.+?)(?:\n|$)',
            'date': r'DATE:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'revision': r'REV(?:ISION)?\.?:\s*(\S+)',
            'drawn_by': r'(?:DRAWN|DRN)\s*(?:BY)?:\s*(\S+)',
            'checked_by': r'(?:CHECKED|CHK)\s*(?:BY)?:\s*(\S+)',
        }

        extracted = {}
        for field, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            extracted[field] = match.group(1).strip() if match else ''

        # Determine discipline from sheet number
        sheet_num = extracted.get('sheet_number', '')
        discipline = ''
        if sheet_num:
            prefix = sheet_num[0].upper() if sheet_num[0].isalpha() else ''
            discipline_map = {
                'A': 'Architectural', 'S': 'Structural', 'M': 'Mechanical',
                'E': 'Electrical', 'P': 'Plumbing', 'C': 'Civil',
                'L': 'Landscape', 'I': 'Interior', 'F': 'Fire Protection'
            }
            discipline = discipline_map.get(prefix, '')

        return TitleBlockData(
            project_name=extracted.get('project_name', ''),
            project_number=extracted.get('project_number', ''),
            sheet_number=sheet_num,
            sheet_title=extracted.get('sheet_title', ''),
            discipline=discipline,
            scale=extracted.get('scale', ''),
            date=extracted.get('date', ''),
            revision=extracted.get('revision', ''),
            drawn_by=extracted.get('drawn_by', ''),
            checked_by=extracted.get('checked_by', ''),
            approved_by=''
        )

    def _parse_schedule_table(self, table: List[List]) -> List[Symbol]:
        """Parse schedule table to extract symbols/elements."""
        symbols = []

        if not table or len(table) < 2:
            return symbols

        # First row is usually headers
        headers = [str(cell).lower() if cell else '' for cell in table[0]]

        # Find key columns
        tag_col = next((i for i, h in enumerate(headers) if 'tag' in h or 'mark' in h or 'no' in h), 0)
        type_col = next((i for i, h in enumerate(headers) if 'type' in h or 'size' in h), -1)

        for row in table[1:]:
            if len(row) > tag_col and row[tag_col]:
                tag = str(row[tag_col]).strip()
                symbol_type = str(row[type_col]).strip() if type_col >= 0 and len(row) > type_col else ''

                if tag:
                    props = {}
                    for i, header in enumerate(headers):
                        if i < len(row) and row[i]:
                            props[header] = str(row[i])

                    symbols.append(Symbol(
                        symbol_type=symbol_type or 'unknown',
                        tag=tag,
                        location=(0, 0),
                        properties=props
                    ))

        return symbols

    def _determine_scale(self, text: str) -> float:
        """Determine drawing scale factor."""
        for pattern in self.SCALE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'NTS' in match.group(0).upper():
                    return 0  # Not to scale

                if '=' in match.group(0):
                    # Imperial: 1/4" = 1'-0"
                    return self._parse_imperial_scale(match.group(0))
                else:
                    # Metric: 1:100
                    return 1 / float(match.group(2))

        return 1.0  # Default

    def _parse_imperial_scale(self, scale_text: str) -> float:
        """Parse imperial scale to factor."""
        match = re.search(r'(\d+)(?:/(\d+))?\s*["\']?\s*=\s*(\d+)', scale_text)
        if match:
            numerator = float(match.group(1))
            denominator = float(match.group(2)) if match.group(2) else 1
            feet = float(match.group(3))
            inches_per_foot = (numerator / denominator)
            return inches_per_foot / (feet * 12)
        return 1.0

    def _check_drawing_quality(self, title_block: TitleBlockData,
                                dimensions: List, annotations: List) -> List[str]:
        """Check drawing for quality issues."""
        issues = []

        if title_block:
            if not title_block.project_number:
                issues.append("Missing project number in title block")
            if not title_block.sheet_number:
                issues.append("Missing sheet number")
            if not title_block.scale:
                issues.append("Missing scale indication")
            if not title_block.date:
                issues.append("Missing date")

        if len(dimensions) == 0:
            issues.append("No dimensions found - verify drawing content")

        # Check for typical construction notes
        note_types = [a.annotation_type for a in annotations]
        if 'note' not in note_types:
            issues.append("No general notes found")

        return issues

    def generate_drawing_index(self, results: List[DrawingAnalysisResult]) -> str:
        """Generate drawing index from multiple analyzed drawings."""
        lines = ["# Drawing Index", ""]
        lines.append("| Sheet | Title | Discipline | Scale | Rev |")
        lines.append("|-------|-------|------------|-------|-----|")

        for result in sorted(results, key=lambda r: r.title_block.sheet_number if r.title_block else ''):
            if result.title_block:
                tb = result.title_block
                lines.append(f"| {tb.sheet_number} | {tb.sheet_title} | {tb.discipline} | {tb.scale} | {tb.revision} |")

        return "\n".join(lines)

    def generate_report(self, result: DrawingAnalysisResult) -> str:
        """Generate analysis report for a drawing."""
        lines = ["# Drawing Analysis Report", ""]
        lines.append(f"**File:** {result.file_name}")

        if result.title_block:
            tb = result.title_block
            lines.append("")
            lines.append("## Title Block")
            lines.append(f"- **Project:** {tb.project_name}")
            lines.append(f"- **Project No:** {tb.project_number}")
            lines.append(f"- **Sheet:** {tb.sheet_number}")
            lines.append(f"- **Title:** {tb.sheet_title}")
            lines.append(f"- **Discipline:** {tb.discipline}")
            lines.append(f"- **Scale:** {tb.scale}")
            lines.append(f"- **Date:** {tb.date}")
            lines.append(f"- **Revision:** {tb.revision}")

        lines.append("")
        lines.append("## Content Summary")
        lines.append(f"- **Dimensions Found:** {len(result.dimensions)}")
        lines.append(f"- **Annotations Found:** {len(result.annotations)}")
        lines.append(f"- **Symbols/Elements:** {len(result.symbols)}")

        if result.quality_issues:
            lines.append("")
            lines.append("## Quality Issues")
            for issue in result.quality_issues:
                lines.append(f"- ⚠️ {issue}")

        if result.symbols:
            lines.append("")
            lines.append("## Elements Found")
            for symbol in result.symbols[:20]:
                lines.append(f"- {symbol.tag}: {symbol.symbol_type}")

        return "\n".join(lines)
```

## Quick Start

```python
# Initialize analyzer
analyzer = DrawingAnalyzer()

# Analyze a drawing
result = analyzer.analyze_pdf_drawing("A101_Floor_Plan.pdf")

# Check title block
if result.title_block:
    print(f"Sheet: {result.title_block.sheet_number}")
    print(f"Title: {result.title_block.sheet_title}")
    print(f"Scale: {result.title_block.scale}")

# Review extracted data
print(f"Dimensions: {len(result.dimensions)}")
print(f"Annotations: {len(result.annotations)}")
print(f"Symbols: {len(result.symbols)}")

# Check quality
for issue in result.quality_issues:
    print(f"Issue: {issue}")

# Generate report
report = analyzer.generate_report(result)
print(report)
```

## Dependencies

```bash
pip install pdfplumber
```
