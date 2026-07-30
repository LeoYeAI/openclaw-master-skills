---
name: "dgn-to-excel"
description: "Convert DGN files (v7-v8) to Excel databases. Extract elements, levels, and properties from infrastructure CAD files."
---

# DGN to Excel Conversion

## Business Case

### Problem Statement
DGN files are common in infrastructure and civil engineering:
- Transportation and highway design
- Bridge and tunnel projects
- Utility networks
- Rail infrastructure

Extracting structured data from DGN files for analysis and reporting can be challenging.

### Solution
Convert DGN files to structured Excel databases, supporting both v7 and v8 formats.

### Business Value
- **Infrastructure support** - Civil engineering focused
- **Legacy format support** - V7 and V8 DGN files
- **Data extraction** - Levels, cells, text, geometry
- **Batch processing** - Process multiple files
- **Structured output** - Excel format for analysis

## Technical Implementation

### CLI Syntax
```bash
DgnExporter.exe <input_dgn>
```

### Supported Versions
| Version | Description |
|---------|-------------|
| V7 DGN | Legacy MicroStation format (pre-V8) |
| V8 DGN | Modern MicroStation format |
| V8i DGN | MicroStation V8i format |

### Output Format
| Output | Description |
|--------|-------------|
| `.xlsx` | Excel database with all elements |

### Examples

```bash
# Basic conversion
DgnExporter.exe "C:\Projects\Bridge.dgn"

# Batch processing
for /R "C:\Infrastructure" %f in (*.dgn) do DgnExporter.exe "%f"

# PowerShell batch
Get-ChildItem "C:\Projects\*.dgn" -Recurse | ForEach-Object {
    & "C:\DDC\DgnExporter.exe" $_.FullName
}
```

### Python Integration

```python
import subprocess
import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class DGNElementType(Enum):
    """DGN element types."""
    CELL_HEADER = 2
    LINE = 3
    LINE_STRING = 4
    SHAPE = 6
    TEXT_NODE = 7
    CURVE = 11
    COMPLEX_CHAIN = 12
    COMPLEX_SHAPE = 14
    ELLIPSE = 15
    ARC = 16
    TEXT = 17
    SURFACE = 18
    SOLID = 19
    BSPLINE_CURVE = 21
    POINT_STRING = 22
    DIMENSION = 33
    SHARED_CELL = 35


@dataclass
class DGNElement:
    """Represents a DGN element."""
    element_id: int
    element_type: int
    type_name: str
    level: int
    color: int
    weight: int
    style: int

    # Geometry
    range_low_x: Optional[float] = None
    range_low_y: Optional[float] = None
    range_low_z: Optional[float] = None
    range_high_x: Optional[float] = None
    range_high_y: Optional[float] = None
    range_high_z: Optional[float] = None

    # Cell/Text specific
    cell_name: Optional[str] = None
    text_content: Optional[str] = None


@dataclass
class DGNLevel:
    """Represents a DGN level."""
    number: int
    name: str
    is_displayed: bool
    is_frozen: bool
    element_count: int


class DGNExporter:
    """DGN to Excel converter using DDC DgnExporter CLI."""

    def __init__(self, exporter_path: str = "DgnExporter.exe"):
        self.exporter = Path(exporter_path)
        if not self.exporter.exists():
            raise FileNotFoundError(f"DgnExporter not found: {exporter_path}")

    def convert(self, dgn_file: str) -> Path:
        """Convert DGN file to Excel."""
        dgn_path = Path(dgn_file)
        if not dgn_path.exists():
            raise FileNotFoundError(f"DGN file not found: {dgn_file}")

        cmd = [str(self.exporter), str(dgn_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Export failed: {result.stderr}")

        return dgn_path.with_suffix('.xlsx')

    def batch_convert(self, folder: str,
                      include_subfolders: bool = True) -> List[Dict[str, Any]]:
        """Convert all DGN files in folder."""
        folder_path = Path(folder)
        pattern = "**/*.dgn" if include_subfolders else "*.dgn"

        results = []
        for dgn_file in folder_path.glob(pattern):
            try:
                output = self.convert(str(dgn_file))
                results.append({
                    'input': str(dgn_file),
                    'output': str(output),
                    'status': 'success'
                })
                print(f"✓ Converted: {dgn_file.name}")
            except Exception as e:
                results.append({
                    'input': str(dgn_file),
                    'output': None,
                    'status': 'failed',
                    'error': str(e)
                })
                print(f"✗ Failed: {dgn_file.name} - {e}")

        return results

    def read_elements(self, xlsx_file: str) -> pd.DataFrame:
        """Read converted Excel as DataFrame."""
        return pd.read_excel(xlsx_file, sheet_name="Elements")

    def get_levels(self, xlsx_file: str) -> pd.DataFrame:
        """Get level summary."""
        df = self.read_elements(xlsx_file)

        if 'Level' not in df.columns:
            raise ValueError("Level column not found")

        summary = df.groupby('Level').agg({
            'ElementId': 'count'
        }).reset_index()
        summary.columns = ['Level', 'Element_Count']
        return summary.sort_values('Level')

    def get_element_types(self, xlsx_file: str) -> pd.DataFrame:
        """Get element type statistics."""
        df = self.read_elements(xlsx_file)

        type_col = 'ElementType' if 'ElementType' in df.columns else 'Type'
        if type_col not in df.columns:
            return pd.DataFrame()

        summary = df.groupby(type_col).agg({
            'ElementId': 'count'
        }).reset_index()
        summary.columns = ['Element_Type', 'Count']
        return summary.sort_values('Count', ascending=False)

    def get_cells(self, xlsx_file: str) -> pd.DataFrame:
        """Get cell references (similar to blocks in DWG)."""
        df = self.read_elements(xlsx_file)

        # Filter to cell elements
        cells = df[df['ElementType'].isin([2, 35])]  # CELL_HEADER, SHARED_CELL

        if cells.empty or 'CellName' not in cells.columns:
            return pd.DataFrame(columns=['Cell_Name', 'Count'])

        summary = cells.groupby('CellName').agg({
            'ElementId': 'count'
        }).reset_index()
        summary.columns = ['Cell_Name', 'Count']
        return summary.sort_values('Count', ascending=False)

    def get_text_content(self, xlsx_file: str) -> pd.DataFrame:
        """Extract all text from DGN."""
        df = self.read_elements(xlsx_file)

        # Filter to text elements
        text_types = [7, 17]  # TEXT_NODE, TEXT
        texts = df[df['ElementType'].isin(text_types)]

        if 'TextContent' in texts.columns:
            return texts[['ElementId', 'Level', 'TextContent']].copy()
        return texts[['ElementId', 'Level']].copy()

    def get_statistics(self, xlsx_file: str) -> Dict[str, Any]:
        """Get comprehensive DGN statistics."""
        df = self.read_elements(xlsx_file)

        stats = {
            'total_elements': len(df),
            'levels_used': df['Level'].nunique() if 'Level' in df.columns else 0,
            'element_types': df['ElementType'].nunique() if 'ElementType' in df.columns else 0
        }

        # Calculate extents
        for coord in ['X', 'Y', 'Z']:
            low_col = f'RangeLow{coord}'
            high_col = f'RangeHigh{coord}'
            if low_col in df.columns and high_col in df.columns:
                stats[f'min_{coord.lower()}'] = df[low_col].min()
                stats[f'max_{coord.lower()}'] = df[high_col].max()

        return stats


class DGNAnalyzer:
    """Advanced DGN analysis for infrastructure projects."""

    def __init__(self, exporter: DGNExporter):
        self.exporter = exporter

    def analyze_infrastructure(self, dgn_file: str) -> Dict[str, Any]:
        """Analyze DGN for infrastructure elements."""
        xlsx = self.exporter.convert(dgn_file)
        df = self.exporter.read_elements(str(xlsx))

        analysis = {
            'file': dgn_file,
            'statistics': self.exporter.get_statistics(str(xlsx)),
            'levels': self.exporter.get_levels(str(xlsx)).to_dict('records'),
            'element_types': self.exporter.get_element_types(str(xlsx)).to_dict('records'),
            'cells': self.exporter.get_cells(str(xlsx)).to_dict('records')
        }

        # Identify infrastructure-specific elements
        if 'ElementType' in df.columns:
            # Lines and shapes (often roads, boundaries)
            lines = df[df['ElementType'].isin([3, 4, 6, 14])].shape[0]
            analysis['linear_elements'] = lines

            # Complex elements (often structures)
            complex_elements = df[df['ElementType'].isin([12, 14, 18, 19])].shape[0]
            analysis['complex_elements'] = complex_elements

            # Annotation elements
            annotations = df[df['ElementType'].isin([7, 17, 33])].shape[0]
            analysis['annotations'] = annotations

        return analysis

    def compare_revisions(self, dgn1: str, dgn2: str) -> Dict[str, Any]:
        """Compare two DGN revisions."""
        xlsx1 = self.exporter.convert(dgn1)
        xlsx2 = self.exporter.convert(dgn2)

        df1 = self.exporter.read_elements(str(xlsx1))
        df2 = self.exporter.read_elements(str(xlsx2))

        levels1 = set(df1['Level'].unique()) if 'Level' in df1.columns else set()
        levels2 = set(df2['Level'].unique()) if 'Level' in df2.columns else set()

        return {
            'revision1': dgn1,
            'revision2': dgn2,
            'element_count_diff': len(df2) - len(df1),
            'levels_added': list(levels2 - levels1),
            'levels_removed': list(levels1 - levels2),
            'common_levels': len(levels1 & levels2)
        }

    def extract_coordinates(self, xlsx_file: str) -> pd.DataFrame:
        """Extract element coordinates for GIS integration."""
        df = self.exporter.read_elements(xlsx_file)

        coord_cols = ['ElementId', 'Level', 'ElementType']
        for col in ['RangeLowX', 'RangeLowY', 'RangeLowZ',
                    'RangeHighX', 'RangeHighY', 'RangeHighZ',
                    'CenterX', 'CenterY', 'CenterZ']:
            if col in df.columns:
                coord_cols.append(col)

        return df[coord_cols].copy()


class DGNLevelManager:
    """Manage DGN level structures."""

    def __init__(self, exporter: DGNExporter):
        self.exporter = exporter

    def get_level_map(self, xlsx_file: str) -> Dict[int, str]:
        """Create level number to name mapping."""
        df = self.exporter.read_elements(xlsx_file)

        if 'Level' not in df.columns:
            return {}

        # MicroStation levels are typically numbered 1-63 (V7) or unlimited (V8)
        level_map = {}
        for level in df['Level'].unique():
            level_map[int(level)] = f"Level_{level}"

        return level_map

    def filter_by_levels(self, xlsx_file: str,
                         levels: List[int]) -> pd.DataFrame:
        """Filter elements by level numbers."""
        df = self.exporter.read_elements(xlsx_file)
        return df[df['Level'].isin(levels)]

    def get_level_usage_report(self, xlsx_file: str) -> pd.DataFrame:
        """Generate level usage report."""
        df = self.exporter.read_elements(xlsx_file)

        if 'Level' not in df.columns or 'ElementType' not in df.columns:
            return pd.DataFrame()

        # Cross-tabulate levels and element types
        report = pd.crosstab(df['Level'], df['ElementType'], margins=True)
        return report


# Convenience functions
def convert_dgn_to_excel(dgn_file: str,
                         exporter_path: str = "DgnExporter.exe") -> str:
    """Quick conversion of DGN to Excel."""
    exporter = DGNExporter(exporter_path)
    output = exporter.convert(dgn_file)
    return str(output)


def analyze_dgn(dgn_file: str,
                exporter_path: str = "DgnExporter.exe") -> Dict[str, Any]:
    """Analyze DGN file and return summary."""
    exporter = DGNExporter(exporter_path)
    analyzer = DGNAnalyzer(exporter)
    return analyzer.analyze_infrastructure(dgn_file)
```

## Output Structure

### Excel Sheets
| Sheet | Content |
|-------|---------|
| Elements | All DGN elements with properties |
| Levels | Level definitions |
| Cells | Cell library |

### Element Columns
| Column | Type | Description |
|--------|------|-------------|
| ElementId | int | Unique element ID |
| ElementType | int | Type code (3=Line, 17=Text, etc.) |
| Level | int | Level number |
| Color | int | Color index |
| Weight | int | Line weight |
| Style | int | Line style |
| RangeLowX/Y/Z | float | Bounding box minimum |
| RangeHighX/Y/Z | float | Bounding box maximum |
| CellName | string | Cell name (for cell elements) |
| TextContent | string | Text content (for text elements) |

## Quick Start

```python
# Initialize exporter
exporter = DGNExporter("C:/DDC/DgnExporter.exe")

# Convert DGN to Excel
xlsx = exporter.convert("C:/Projects/Highway.dgn")
print(f"Output: {xlsx}")

# Read elements
df = exporter.read_elements(str(xlsx))
print(f"Total elements: {len(df)}")

# Get level statistics
levels = exporter.get_levels(str(xlsx))
print(levels)

# Get element types
types = exporter.get_element_types(str(xlsx))
print(types)
```

## Common Use Cases

### 1. Infrastructure Analysis
```python
exporter = DGNExporter()
analyzer = DGNAnalyzer(exporter)

analysis = analyzer.analyze_infrastructure("highway.dgn")
print(f"Total elements: {analysis['statistics']['total_elements']}")
print(f"Linear elements: {analysis['linear_elements']}")
print(f"Annotations: {analysis['annotations']}")
```

### 2. Level Audit
```python
exporter = DGNExporter()
xlsx = exporter.convert("bridge.dgn")
levels = exporter.get_levels(str(xlsx))

# Check for unused standard levels
for idx, row in levels.iterrows():
    print(f"Level {row['Level']}: {row['Element_Count']} elements")
```

### 3. GIS Integration
```python
analyzer = DGNAnalyzer(exporter)
xlsx = exporter.convert("utilities.dgn")
coords = analyzer.extract_coordinates(str(xlsx))

# Export for GIS
coords.to_csv("coordinates.csv", index=False)
```

### 4. Revision Comparison
```python
analyzer = DGNAnalyzer(exporter)
diff = analyzer.compare_revisions("rev1.dgn", "rev2.dgn")
print(f"Elements changed: {diff['element_count_diff']}")
```

## Integration with DDC Pipeline

```python
# Infrastructure pipeline: DGN → Excel → Analysis
from dgn_exporter import DGNExporter, DGNAnalyzer

# 1. Convert DGN
exporter = DGNExporter("C:/DDC/DgnExporter.exe")
xlsx = exporter.convert("highway_project.dgn")

# 2. Analyze structure
stats = exporter.get_statistics(str(xlsx))
print(f"Elements: {stats['total_elements']}")
print(f"Levels: {stats['levels_used']}")

# 3. Extract for GIS
analyzer = DGNAnalyzer(exporter)
coords = analyzer.extract_coordinates(str(xlsx))
coords.to_csv("for_gis.csv", index=False)
```

## Best Practices

1. **Check version** - V7 and V8 have different capabilities
2. **Reference files** - Process all reference files separately
3. **Level mapping** - Document level standards for your organization
4. **Coordinate systems** - Verify units and coordinate systems
5. **Cell libraries** - Export cells separately if needed

## Resources

- **GitHub**: [cad2data Pipeline](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto)
- **DDC Book**: Chapter 2.4 - CAD Data Extraction
- **MicroStation**: Infrastructure-focused CAD software
