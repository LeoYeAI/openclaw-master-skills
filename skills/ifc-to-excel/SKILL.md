---
name: "ifc-to-excel"
description: "Convert IFC files (2x3, 4x1, 4x3) to Excel databases using IfcExporter CLI. Extract BIM data, properties, and geometry without proprietary software."
---

# IFC to Excel Conversion

## Business Case

### Problem Statement
IFC (Industry Foundation Classes) is the open BIM standard, but:
- Reading IFC requires specialized software
- Property extraction needs programming knowledge
- Batch processing is manual and time-consuming
- Integration with analytics tools is complex

### Solution
IfcExporter.exe converts IFC files to structured Excel databases, making BIM data accessible for analysis, validation, and reporting.

### Business Value
- **Open standard** - Process any IFC file (2x3, 4x, 4.3)
- **No licenses** - Works offline without BIM software
- **Data extraction** - All properties, quantities, materials
- **3D geometry** - Export to Collada DAE format
- **Pipeline ready** - Integrate with ETL workflows

## Technical Implementation

### CLI Syntax
```bash
IfcExporter.exe <input_ifc> [options]
```

### Supported IFC Versions
| Version | Schema | Description |
|---------|--------|-------------|
| IFC2x3 | MVD | Most common exchange format |
| IFC4 | ADD1 | Enhanced properties |
| IFC4x1 | Alignment | Infrastructure support |
| IFC4x3 | Latest | Full infrastructure |

### Output Formats
| Output | Description |
|--------|-------------|
| `.xlsx` | Excel database with elements and properties |
| `.dae` | Collada 3D geometry with matching IDs |

### Options
| Option | Description |
|--------|-------------|
| `bbox` | Include element bounding boxes |
| `-no-xlsx` | Skip Excel export |
| `-no-collada` | Skip 3D geometry export |

### Examples

```bash
# Basic conversion (XLSX + DAE)
IfcExporter.exe "C:\Models\Building.ifc"

# With bounding boxes
IfcExporter.exe "C:\Models\Building.ifc" bbox

# Excel only (no 3D geometry)
IfcExporter.exe "C:\Models\Building.ifc" -no-collada

# Batch processing
for /R "C:\IFC_Models" %f in (*.ifc) do IfcExporter.exe "%f" bbox
```

### Python Integration

```python
import subprocess
import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import json


class IFCVersion(Enum):
    """IFC schema versions."""
    IFC2X3 = "IFC2X3"
    IFC4 = "IFC4"
    IFC4X1 = "IFC4X1"
    IFC4X3 = "IFC4X3"


class IFCEntityType(Enum):
    """Common IFC entity types."""
    IFCWALL = "IfcWall"
    IFCWALLSTANDARDCASE = "IfcWallStandardCase"
    IFCSLAB = "IfcSlab"
    IFCCOLUMN = "IfcColumn"
    IFCBEAM = "IfcBeam"
    IFCDOOR = "IfcDoor"
    IFCWINDOW = "IfcWindow"
    IFCROOF = "IfcRoof"
    IFCSTAIR = "IfcStair"
    IFCRAILING = "IfcRailing"
    IFCFURNISHINGELEMENT = "IfcFurnishingElement"
    IFCSPACE = "IfcSpace"
    IFCBUILDINGSTOREY = "IfcBuildingStorey"
    IFCBUILDING = "IfcBuilding"
    IFCSITE = "IfcSite"


@dataclass
class IFCElement:
    """Represents an IFC element."""
    global_id: str
    ifc_type: str
    name: str
    description: Optional[str]
    object_type: Optional[str]
    level: Optional[str]

    # Quantities
    area: Optional[float] = None
    volume: Optional[float] = None
    length: Optional[float] = None
    height: Optional[float] = None
    width: Optional[float] = None

    # Bounding box (if exported)
    bbox_min_x: Optional[float] = None
    bbox_min_y: Optional[float] = None
    bbox_min_z: Optional[float] = None
    bbox_max_x: Optional[float] = None
    bbox_max_y: Optional[float] = None
    bbox_max_z: Optional[float] = None

    # Properties
    properties: Dict[str, Any] = field(default_factory=dict)
    materials: List[str] = field(default_factory=list)


@dataclass
class IFCProperty:
    """Represents an IFC property."""
    pset_name: str
    property_name: str
    value: Any
    value_type: str


@dataclass
class IFCMaterial:
    """Represents an IFC material."""
    name: str
    category: Optional[str]
    thickness: Optional[float]
    layer_position: Optional[int]


class IFCExporter:
    """IFC to Excel converter using DDC IfcExporter CLI."""

    def __init__(self, exporter_path: str = "IfcExporter.exe"):
        self.exporter = Path(exporter_path)
        if not self.exporter.exists():
            raise FileNotFoundError(f"IfcExporter not found: {exporter_path}")

    def convert(self, ifc_file: str,
                include_bbox: bool = True,
                export_xlsx: bool = True,
                export_collada: bool = True) -> Path:
        """Convert IFC file to Excel."""
        ifc_path = Path(ifc_file)
        if not ifc_path.exists():
            raise FileNotFoundError(f"IFC file not found: {ifc_file}")

        cmd = [str(self.exporter), str(ifc_path)]

        if include_bbox:
            cmd.append("bbox")
        if not export_xlsx:
            cmd.append("-no-xlsx")
        if not export_collada:
            cmd.append("-no-collada")

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Export failed: {result.stderr}")

        return ifc_path.with_suffix('.xlsx')

    def batch_convert(self, folder: str,
                      include_subfolders: bool = True,
                      include_bbox: bool = True) -> List[Dict[str, Any]]:
        """Convert all IFC files in folder."""
        folder_path = Path(folder)
        pattern = "**/*.ifc" if include_subfolders else "*.ifc"

        results = []
        for ifc_file in folder_path.glob(pattern):
            try:
                output = self.convert(str(ifc_file), include_bbox)
                results.append({
                    'input': str(ifc_file),
                    'output': str(output),
                    'status': 'success'
                })
                print(f"✓ Converted: {ifc_file.name}")
            except Exception as e:
                results.append({
                    'input': str(ifc_file),
                    'output': None,
                    'status': 'failed',
                    'error': str(e)
                })
                print(f"✗ Failed: {ifc_file.name} - {e}")

        return results

    def read_elements(self, xlsx_file: str) -> pd.DataFrame:
        """Read converted Excel as DataFrame."""
        return pd.read_excel(xlsx_file, sheet_name="Elements")

    def get_element_types(self, xlsx_file: str) -> pd.DataFrame:
        """Get element type summary."""
        df = self.read_elements(xlsx_file)

        if 'IfcType' not in df.columns:
            raise ValueError("IfcType column not found")

        summary = df.groupby('IfcType').agg({
            'GlobalId': 'count',
            'Volume': 'sum' if 'Volume' in df.columns else 'count',
            'Area': 'sum' if 'Area' in df.columns else 'count'
        }).reset_index()

        summary.columns = ['IFC_Type', 'Count', 'Total_Volume', 'Total_Area']
        return summary.sort_values('Count', ascending=False)

    def get_levels(self, xlsx_file: str) -> pd.DataFrame:
        """Get building level summary."""
        df = self.read_elements(xlsx_file)

        level_col = None
        for col in ['Level', 'BuildingStorey', 'IfcBuildingStorey']:
            if col in df.columns:
                level_col = col
                break

        if level_col is None:
            return pd.DataFrame(columns=['Level', 'Element_Count'])

        summary = df.groupby(level_col).agg({
            'GlobalId': 'count'
        }).reset_index()
        summary.columns = ['Level', 'Element_Count']
        return summary

    def get_materials(self, xlsx_file: str) -> pd.DataFrame:
        """Get material summary."""
        df = self.read_elements(xlsx_file)

        if 'Material' not in df.columns:
            return pd.DataFrame(columns=['Material', 'Count'])

        summary = df.groupby('Material').agg({
            'GlobalId': 'count'
        }).reset_index()
        summary.columns = ['Material', 'Element_Count']
        return summary.sort_values('Element_Count', ascending=False)

    def get_quantities(self, xlsx_file: str,
                       group_by: str = 'IfcType') -> pd.DataFrame:
        """Get quantity takeoff summary."""
        df = self.read_elements(xlsx_file)

        if group_by not in df.columns:
            raise ValueError(f"Column {group_by} not found")

        agg_dict = {'GlobalId': 'count'}

        # Add numeric columns for aggregation
        numeric_cols = ['Volume', 'Area', 'Length', 'Width', 'Height']
        for col in numeric_cols:
            if col in df.columns:
                agg_dict[col] = 'sum'

        summary = df.groupby(group_by).agg(agg_dict).reset_index()
        return summary

    def filter_by_type(self, xlsx_file: str,
                       ifc_types: List[str]) -> pd.DataFrame:
        """Filter elements by IFC type."""
        df = self.read_elements(xlsx_file)
        return df[df['IfcType'].isin(ifc_types)]

    def get_properties(self, xlsx_file: str,
                       element_id: str) -> Dict[str, Any]:
        """Get all properties for specific element."""
        df = self.read_elements(xlsx_file)
        element = df[df['GlobalId'] == element_id]

        if element.empty:
            return {}

        # Convert row to dictionary, excluding NaN values
        props = element.iloc[0].dropna().to_dict()
        return props

    def validate_ifc_data(self, xlsx_file: str) -> Dict[str, Any]:
        """Validate IFC data quality."""
        df = self.read_elements(xlsx_file)

        validation = {
            'total_elements': len(df),
            'issues': []
        }

        # Check for missing GlobalIds
        if 'GlobalId' in df.columns:
            missing_ids = df['GlobalId'].isna().sum()
            if missing_ids > 0:
                validation['issues'].append(f"{missing_ids} elements missing GlobalId")

        # Check for missing names
        if 'Name' in df.columns:
            missing_names = df['Name'].isna().sum()
            if missing_names > 0:
                validation['issues'].append(f"{missing_names} elements missing Name")

        # Check for zero quantities
        for col in ['Volume', 'Area']:
            if col in df.columns:
                zero_qty = (df[col] == 0).sum()
                if zero_qty > 0:
                    validation['issues'].append(f"{zero_qty} elements with zero {col}")

        # Check for duplicate GlobalIds
        if 'GlobalId' in df.columns:
            duplicates = df['GlobalId'].duplicated().sum()
            if duplicates > 0:
                validation['issues'].append(f"{duplicates} duplicate GlobalIds")

        validation['is_valid'] = len(validation['issues']) == 0
        return validation


class IFCQuantityTakeoff:
    """Quantity takeoff from IFC data."""

    def __init__(self, exporter: IFCExporter):
        self.exporter = exporter

    def generate_qto(self, ifc_file: str) -> Dict[str, pd.DataFrame]:
        """Generate complete quantity takeoff."""
        xlsx = self.exporter.convert(ifc_file, include_bbox=True)
        df = self.exporter.read_elements(str(xlsx))

        qto = {}

        # Walls
        walls = df[df['IfcType'].str.contains('Wall', case=False, na=False)]
        if not walls.empty:
            qto['Walls'] = self._summarize_elements(walls, 'Type Name')

        # Slabs
        slabs = df[df['IfcType'].str.contains('Slab', case=False, na=False)]
        if not slabs.empty:
            qto['Slabs'] = self._summarize_elements(slabs, 'Type Name')

        # Columns
        columns = df[df['IfcType'].str.contains('Column', case=False, na=False)]
        if not columns.empty:
            qto['Columns'] = self._summarize_elements(columns, 'Type Name')

        # Beams
        beams = df[df['IfcType'].str.contains('Beam', case=False, na=False)]
        if not beams.empty:
            qto['Beams'] = self._summarize_elements(beams, 'Type Name')

        # Doors
        doors = df[df['IfcType'].str.contains('Door', case=False, na=False)]
        if not doors.empty:
            qto['Doors'] = self._summarize_elements(doors, 'Type Name')

        # Windows
        windows = df[df['IfcType'].str.contains('Window', case=False, na=False)]
        if not windows.empty:
            qto['Windows'] = self._summarize_elements(windows, 'Type Name')

        return qto

    def _summarize_elements(self, df: pd.DataFrame,
                            group_col: str) -> pd.DataFrame:
        """Summarize elements by grouping column."""
        if group_col not in df.columns:
            group_col = 'IfcType'

        agg_dict = {'GlobalId': 'count'}
        for col in ['Volume', 'Area', 'Length']:
            if col in df.columns:
                agg_dict[col] = 'sum'

        summary = df.groupby(group_col).agg(agg_dict).reset_index()
        summary.rename(columns={'GlobalId': 'Count'}, inplace=True)
        return summary

    def export_to_excel(self, qto: Dict[str, pd.DataFrame],
                        output_file: str):
        """Export QTO to multi-sheet Excel."""
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            for sheet_name, df in qto.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)


# Convenience functions
def convert_ifc_to_excel(ifc_file: str,
                         exporter_path: str = "IfcExporter.exe") -> str:
    """Quick conversion of IFC to Excel."""
    exporter = IFCExporter(exporter_path)
    output = exporter.convert(ifc_file)
    return str(output)


def get_ifc_summary(xlsx_file: str) -> Dict[str, Any]:
    """Get summary of converted IFC data."""
    df = pd.read_excel(xlsx_file, sheet_name="Elements")

    return {
        'total_elements': len(df),
        'ifc_types': df['IfcType'].nunique() if 'IfcType' in df.columns else 0,
        'levels': df['Level'].nunique() if 'Level' in df.columns else 0,
        'total_volume': df['Volume'].sum() if 'Volume' in df.columns else 0,
        'total_area': df['Area'].sum() if 'Area' in df.columns else 0
    }
```

## Output Structure

### Excel Sheets
| Sheet | Content |
|-------|---------|
| Elements | All IFC elements with properties |
| Types | Element types summary |
| Levels | Building storey data |
| Materials | Material assignments |
| PropertySets | IFC property sets |

### Element Columns
| Column | Type | Description |
|--------|------|-------------|
| GlobalId | string | IFC GUID |
| IfcType | string | IFC entity type |
| Name | string | Element name |
| Description | string | Element description |
| Level | string | Building storey |
| Material | string | Primary material |
| Volume | float | Volume (m³) |
| Area | float | Surface area (m²) |
| Length | float | Length (m) |
| Height | float | Height (m) |
| Width | float | Width (m) |

## Quick Start

```python
# Initialize exporter
exporter = IFCExporter("C:/DDC/IfcExporter.exe")

# Convert IFC to Excel
xlsx = exporter.convert("C:/Models/Building.ifc", include_bbox=True)

# Read elements
df = exporter.read_elements(str(xlsx))
print(f"Total elements: {len(df)}")

# Get element types
types = exporter.get_element_types(str(xlsx))
print(types)

# Get quantities by type
qto = exporter.get_quantities(str(xlsx), group_by='IfcType')
print(qto)
```

## Common Use Cases

### 1. Model Validation
```python
exporter = IFCExporter()
xlsx = exporter.convert("model.ifc")
validation = exporter.validate_ifc_data(str(xlsx))

if not validation['is_valid']:
    print("Issues found:")
    for issue in validation['issues']:
        print(f"  - {issue}")
```

### 2. Quantity Takeoff
```python
qto_generator = IFCQuantityTakeoff(exporter)
qto = qto_generator.generate_qto("building.ifc")

for category, data in qto.items():
    print(f"\n{category}:")
    print(data.to_string(index=False))
```

### 3. Material Schedule
```python
xlsx = exporter.convert("building.ifc")
materials = exporter.get_materials(str(xlsx))
print(materials)
```

## Integration with DDC Pipeline

```python
# Full pipeline: IFC → Excel → Validation → Cost Estimate
exporter = IFCExporter("C:/DDC/IfcExporter.exe")

# 1. Convert IFC
xlsx = exporter.convert("project.ifc", include_bbox=True)

# 2. Validate data
validation = exporter.validate_ifc_data(str(xlsx))
print(f"Valid: {validation['is_valid']}")

# 3. Generate QTO
qto = IFCQuantityTakeoff(exporter)
quantities = qto.generate_qto("project.ifc")

# 4. Export for cost estimation
qto.export_to_excel(quantities, "project_qto.xlsx")
```

## Resources

- **GitHub**: [cad2data Pipeline](https://github.com/datadrivenconstruction/cad2data-Revit-IFC-DWG-DGN-pipeline-with-conversion-validation-qto)
- **IFC Standard**: [buildingSMART](https://www.buildingsmart.org/standards/bsi-standards/industry-foundation-classes/)
- **DDC Book**: Chapter 2.4 - CAD/BIM Data Extraction
