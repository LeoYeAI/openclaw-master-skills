---
name: "ifc-data-extraction"
description: "Extract structured data from IFC (Industry Foundation Classes) files using IfcOpenShell. Parse BIM models, extract quantities, properties, spatial relationships, and export to various formats."
---

# IFC Data Extraction

## Overview

This skill provides comprehensive IFC file parsing and data extraction using IfcOpenShell. Extract element data, quantities, properties, and relationships from BIM models for analysis and reporting.

**Based on Open BIM Standards** - Working with vendor-neutral IFC format for maximum interoperability.

> "IFC является открытым стандартом для обмена BIM-данными, позволяющим извлекать информацию независимо от программного обеспечения."
> — DDC Methodology

## Quick Start

```python
import ifcopenshell
import ifcopenshell.util.element as element_util
import pandas as pd

# Open IFC file
ifc = ifcopenshell.open("model.ifc")

# Get project info
project = ifc.by_type("IfcProject")[0]
print(f"Project: {project.Name}")

# Extract all walls
walls = ifc.by_type("IfcWall")
print(f"Total walls: {len(walls)}")

# Get wall data
wall_data = []
for wall in walls:
    psets = element_util.get_psets(wall)
    wall_data.append({
        'GlobalId': wall.GlobalId,
        'Name': wall.Name,
        'Type': wall.is_a(),
        'Level': get_level(wall),
        'Properties': psets
    })

df = pd.DataFrame(wall_data)
print(df.head())
```

## Core Extraction Functions

### Element Extractor Class

```python
import ifcopenshell
import ifcopenshell.util.element as element_util
import ifcopenshell.util.placement as placement_util
import ifcopenshell.geom
import pandas as pd
from typing import List, Dict, Optional, Any

class IFCExtractor:
    """Extract data from IFC files"""

    def __init__(self, ifc_path: str):
        self.model = ifcopenshell.open(ifc_path)
        self.settings = ifcopenshell.geom.settings()

    def get_project_info(self) -> Dict:
        """Extract project metadata"""
        project = self.model.by_type("IfcProject")[0]
        site = self.model.by_type("IfcSite")
        building = self.model.by_type("IfcBuilding")

        return {
            'project_id': project.GlobalId,
            'project_name': project.Name,
            'description': project.Description,
            'site_count': len(site),
            'building_count': len(building),
            'schema': self.model.schema
        }

    def get_all_elements(self, element_types: List[str] = None) -> pd.DataFrame:
        """Extract all elements of specified types"""
        if element_types is None:
            element_types = [
                'IfcWall', 'IfcSlab', 'IfcColumn', 'IfcBeam',
                'IfcDoor', 'IfcWindow', 'IfcStair', 'IfcRoof'
            ]

        all_elements = []

        for ifc_type in element_types:
            elements = self.model.by_type(ifc_type)

            for elem in elements:
                data = self._extract_element_data(elem)
                data['IFC_Type'] = ifc_type
                all_elements.append(data)

        return pd.DataFrame(all_elements)

    def _extract_element_data(self, element) -> Dict:
        """Extract data from single element"""
        # Basic info
        data = {
            'GlobalId': element.GlobalId,
            'Name': element.Name,
            'Description': element.Description,
            'ObjectType': element.ObjectType if hasattr(element, 'ObjectType') else None
        }

        # Get level/storey
        data['Level'] = self._get_element_level(element)

        # Get material
        data['Material'] = self._get_element_material(element)

        # Get type
        data['TypeName'] = self._get_element_type(element)

        # Get all property sets
        psets = element_util.get_psets(element)
        data['PropertySets'] = psets

        # Extract common quantities
        base_quantities = psets.get('BaseQuantities', {})
        data.update({
            'Length': base_quantities.get('Length'),
            'Width': base_quantities.get('Width'),
            'Height': base_quantities.get('Height'),
            'Area': base_quantities.get('NetSideArea') or base_quantities.get('GrossArea'),
            'Volume': base_quantities.get('NetVolume') or base_quantities.get('GrossVolume')
        })

        return data

    def _get_element_level(self, element) -> Optional[str]:
        """Get the building storey for an element"""
        if hasattr(element, 'ContainedInStructure'):
            for rel in element.ContainedInStructure or []:
                if rel.RelatingStructure.is_a('IfcBuildingStorey'):
                    return rel.RelatingStructure.Name
        return None

    def _get_element_material(self, element) -> Optional[str]:
        """Get material name for element"""
        if hasattr(element, 'HasAssociations'):
            for rel in element.HasAssociations or []:
                if rel.is_a('IfcRelAssociatesMaterial'):
                    material = rel.RelatingMaterial
                    if hasattr(material, 'Name'):
                        return material.Name
                    elif hasattr(material, 'ForLayerSet'):
                        layers = material.ForLayerSet.MaterialLayers
                        if layers:
                            return layers[0].Material.Name
        return None

    def _get_element_type(self, element) -> Optional[str]:
        """Get element type name"""
        if hasattr(element, 'IsTypedBy'):
            for rel in element.IsTypedBy or []:
                return rel.RelatingType.Name
        return None

    def extract_quantities(self) -> pd.DataFrame:
        """Extract quantities for all elements"""
        elements = self.get_all_elements()

        # Group by category and level
        quantities = elements.groupby(['IFC_Type', 'Level']).agg({
            'GlobalId': 'count',
            'Volume': 'sum',
            'Area': 'sum',
            'Length': 'sum'
        }).rename(columns={'GlobalId': 'Count'}).reset_index()

        return quantities

    def extract_levels(self) -> pd.DataFrame:
        """Extract building levels/storeys"""
        storeys = self.model.by_type("IfcBuildingStorey")

        level_data = []
        for storey in storeys:
            level_data.append({
                'GlobalId': storey.GlobalId,
                'Name': storey.Name,
                'Elevation': storey.Elevation,
                'Description': storey.Description
            })

        return pd.DataFrame(level_data).sort_values('Elevation')

    def extract_spaces(self) -> pd.DataFrame:
        """Extract spaces/rooms"""
        spaces = self.model.by_type("IfcSpace")

        space_data = []
        for space in spaces:
            psets = element_util.get_psets(space)
            base_qty = psets.get('BaseQuantities', {})

            space_data.append({
                'GlobalId': space.GlobalId,
                'Name': space.Name,
                'LongName': space.LongName,
                'Level': self._get_element_level(space),
                'Area': base_qty.get('NetFloorArea'),
                'Volume': base_qty.get('NetVolume'),
                'Height': base_qty.get('Height')
            })

        return pd.DataFrame(space_data)

    def extract_materials(self) -> pd.DataFrame:
        """Extract material summary"""
        materials = {}

        for elem in self.model.by_type("IfcProduct"):
            material = self._get_element_material(elem)
            if material:
                if material not in materials:
                    materials[material] = {'count': 0, 'volume': 0}

                materials[material]['count'] += 1

                psets = element_util.get_psets(elem)
                volume = psets.get('BaseQuantities', {}).get('NetVolume', 0)
                if volume:
                    materials[material]['volume'] += volume

        return pd.DataFrame.from_dict(materials, orient='index').reset_index()

    def extract_relationships(self) -> pd.DataFrame:
        """Extract element relationships"""
        relationships = []

        # Spatial containment
        for rel in self.model.by_type("IfcRelContainedInSpatialStructure"):
            for elem in rel.RelatedElements:
                relationships.append({
                    'Element': elem.GlobalId,
                    'Element_Type': elem.is_a(),
                    'Relationship': 'ContainedIn',
                    'Related_To': rel.RelatingStructure.GlobalId,
                    'Related_Type': rel.RelatingStructure.is_a()
                })

        # Aggregation
        for rel in self.model.by_type("IfcRelAggregates"):
            for part in rel.RelatedObjects:
                relationships.append({
                    'Element': part.GlobalId,
                    'Element_Type': part.is_a(),
                    'Relationship': 'PartOf',
                    'Related_To': rel.RelatingObject.GlobalId,
                    'Related_Type': rel.RelatingObject.is_a()
                })

        return pd.DataFrame(relationships)
```

## Geometry Extraction

### Extract Geometry Data

```python
import numpy as np

class IFCGeometryExtractor:
    """Extract geometry data from IFC elements"""

    def __init__(self, ifc_path: str):
        self.model = ifcopenshell.open(ifc_path)
        self.settings = ifcopenshell.geom.settings()
        self.settings.set(self.settings.USE_WORLD_COORDS, True)

    def get_element_geometry(self, element) -> Dict:
        """Extract geometry for single element"""
        try:
            shape = ifcopenshell.geom.create_shape(self.settings, element)

            verts = shape.geometry.verts
            faces = shape.geometry.faces

            # Calculate bounding box
            vertices = np.array(verts).reshape(-1, 3)
            min_coords = vertices.min(axis=0)
            max_coords = vertices.max(axis=0)
            dimensions = max_coords - min_coords

            return {
                'GlobalId': element.GlobalId,
                'vertices_count': len(vertices),
                'faces_count': len(faces) // 3,
                'min_x': min_coords[0],
                'min_y': min_coords[1],
                'min_z': min_coords[2],
                'max_x': max_coords[0],
                'max_y': max_coords[1],
                'max_z': max_coords[2],
                'length': dimensions[0],
                'width': dimensions[1],
                'height': dimensions[2],
                'center_x': (min_coords[0] + max_coords[0]) / 2,
                'center_y': (min_coords[1] + max_coords[1]) / 2,
                'center_z': (min_coords[2] + max_coords[2]) / 2
            }
        except:
            return {'GlobalId': element.GlobalId, 'error': 'Geometry extraction failed'}

    def get_bounding_boxes(self, element_type: str) -> pd.DataFrame:
        """Get bounding boxes for all elements of type"""
        elements = self.model.by_type(element_type)
        boxes = [self.get_element_geometry(e) for e in elements]
        return pd.DataFrame(boxes)

    def calculate_volumes(self, element_type: str) -> pd.DataFrame:
        """Calculate volumes using geometry"""
        elements = self.model.by_type(element_type)
        volumes = []

        for elem in elements:
            try:
                shape = ifcopenshell.geom.create_shape(self.settings, elem)
                # Calculate volume from mesh (simplified)
                verts = np.array(shape.geometry.verts).reshape(-1, 3)
                bbox_volume = np.prod(verts.max(axis=0) - verts.min(axis=0))

                volumes.append({
                    'GlobalId': elem.GlobalId,
                    'Name': elem.Name,
                    'BBox_Volume': bbox_volume
                })
            except:
                pass

        return pd.DataFrame(volumes)
```

## Export Functions

### Export to Various Formats

```python
class IFCExporter:
    """Export IFC data to various formats"""

    def __init__(self, extractor: IFCExtractor):
        self.extractor = extractor

    def to_excel(self, output_path: str, include_all: bool = True):
        """Export to Excel with multiple sheets"""
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Project info
            project_info = pd.DataFrame([self.extractor.get_project_info()])
            project_info.to_excel(writer, sheet_name='Project', index=False)

            # All elements
            if include_all:
                elements = self.extractor.get_all_elements()
                elements.to_excel(writer, sheet_name='Elements', index=False)

            # Quantities
            quantities = self.extractor.extract_quantities()
            quantities.to_excel(writer, sheet_name='Quantities', index=False)

            # Levels
            levels = self.extractor.extract_levels()
            levels.to_excel(writer, sheet_name='Levels', index=False)

            # Spaces
            spaces = self.extractor.extract_spaces()
            spaces.to_excel(writer, sheet_name='Spaces', index=False)

            # Materials
            materials = self.extractor.extract_materials()
            materials.to_excel(writer, sheet_name='Materials', index=False)

        return output_path

    def to_csv(self, output_dir: str):
        """Export to multiple CSV files"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        exports = {
            'elements.csv': self.extractor.get_all_elements(),
            'quantities.csv': self.extractor.extract_quantities(),
            'levels.csv': self.extractor.extract_levels(),
            'spaces.csv': self.extractor.extract_spaces(),
            'materials.csv': self.extractor.extract_materials()
        }

        for filename, df in exports.items():
            df.to_csv(os.path.join(output_dir, filename), index=False)

        return output_dir

    def to_json(self, output_path: str):
        """Export to JSON"""
        import json

        data = {
            'project': self.extractor.get_project_info(),
            'elements': self.extractor.get_all_elements().to_dict('records'),
            'quantities': self.extractor.extract_quantities().to_dict('records'),
            'levels': self.extractor.extract_levels().to_dict('records'),
            'materials': self.extractor.extract_materials().to_dict('records')
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

        return output_path

    def to_database(self, connection_string: str, table_prefix: str = 'ifc_'):
        """Export to SQL database"""
        from sqlalchemy import create_engine

        engine = create_engine(connection_string)

        tables = {
            f'{table_prefix}elements': self.extractor.get_all_elements(),
            f'{table_prefix}quantities': self.extractor.extract_quantities(),
            f'{table_prefix}levels': self.extractor.extract_levels(),
            f'{table_prefix}spaces': self.extractor.extract_spaces(),
            f'{table_prefix}materials': self.extractor.extract_materials()
        }

        for table_name, df in tables.items():
            # Remove complex columns for database storage
            simple_df = df.select_dtypes(exclude=['object']).copy()
            for col in df.columns:
                if df[col].dtype == 'object':
                    simple_df[col] = df[col].astype(str)

            simple_df.to_sql(table_name, engine, if_exists='replace', index=False)

        return list(tables.keys())
```

## Quick Reference

| Element Type | Common Properties | Quantities |
|-------------|-------------------|------------|
| IfcWall | IsExternal, FireRating | Length, Height, Area, Volume |
| IfcSlab | IsExternal, LoadBearing | Area, Volume, Perimeter |
| IfcColumn | LoadBearing | Height, CrossSectionArea |
| IfcBeam | LoadBearing | Length, CrossSectionArea |
| IfcDoor | FireRating, AcousticRating | Width, Height |
| IfcWindow | ThermalTransmittance | Width, Height, Area |

## Property Set Lookup

```python
# Common IFC Property Sets
PSETS = {
    'Pset_WallCommon': ['IsExternal', 'LoadBearing', 'FireRating'],
    'Pset_SlabCommon': ['IsExternal', 'LoadBearing', 'AcousticRating'],
    'Pset_ColumnCommon': ['IsExternal', 'LoadBearing'],
    'Pset_BeamCommon': ['LoadBearing', 'FireRating'],
    'Pset_DoorCommon': ['FireRating', 'AcousticRating', 'SecurityRating'],
    'Pset_WindowCommon': ['ThermalTransmittance', 'GlazingType'],
    'BaseQuantities': ['Length', 'Width', 'Height', 'Area', 'Volume']
}
```

## Resources

- **IfcOpenShell**: https://ifcopenshell.org
- **IFC Standard**: https://www.buildingsmart.org/standards/bsi-standards/industry-foundation-classes/
- **DDC Website**: https://datadrivenconstruction.io

## Next Steps

- See `bim-validation-pipeline` for validating extracted data
- See `qto-report` for quantity take-off reports
- See `4d-simulation` for linking to schedules
