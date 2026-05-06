---
name: "data-type-classifier"
description: "Classify construction data by type (structured, unstructured, semi-structured). Analyze data sources and recommend appropriate storage/processing methods"
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🏷️", "os": ["win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"], "anyBins": ["tesseract", "ifcopenshell"]}}}
---
# Data Type Classifier

## Overview

Based on DDC methodology (Chapter 2.1), this skill classifies construction data by type, analyzes data sources, and recommends appropriate storage, processing, and integration methods.

**Book Reference:** "Типы данных в строительстве" / "Data Types in Construction"

## Quick Start

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import json
import re
import mimetypes

class DataStructure(Enum):
    """Data structure classification"""
    STRUCTURED = "structured"           # Tables, databases, spreadsheets
    SEMI_STRUCTURED = "semi_structured" # JSON, XML, IFC
    UNSTRUCTURED = "unstructured"       # Documents, images, videos
    GEOMETRIC = "geometric"             # CAD, BIM geometry
    TEMPORAL = "temporal"               # Time-series, schedules
    SPATIAL = "spatial"                 # GIS, coordinates

class DataFormat(Enum):
    """Common construction data formats"""
    # Structured
    CSV = "csv"
    EXCEL = "excel"
    SQL = "sql"
    PARQUET = "parquet"

    # Semi-structured
    JSON = "json"
    XML = "xml"
    IFC = "ifc"
    BCF = "bcf"

    # Unstructured
    PDF = "pdf"
    DOCX = "docx"
    IMAGE = "image"
    VIDEO = "video"

    # Geometric
    DWG = "dwg"
    DXF = "dxf"
    RVT = "rvt"
    NWD = "nwd"
    OBJ = "obj"
    STL = "stl"

    # Schedule
    MPP = "mpp"
    P6 = "p6"
    XER = "xer"

class StorageRecommendation(Enum):
    """Storage system recommendations"""
    RELATIONAL_DB = "relational_database"
    DOCUMENT_DB = "document_database"
    OBJECT_STORAGE = "object_storage"
    GRAPH_DB = "graph_database"
    TIME_SERIES_DB = "time_series_database"
    VECTOR_DB = "vector_database"
    FILE_SYSTEM = "file_system"
    DATA_LAKE = "data_lake"

@dataclass
class DataCharacteristics:
    """Characteristics of a data source"""
    has_schema: bool
    has_relationships: bool
    is_queryable: bool
    is_binary: bool
    has_geometry: bool
    has_temporal: bool
    has_text_content: bool
    avg_record_size: Optional[int] = None  # bytes
    estimated_volume: Optional[str] = None  # small/medium/large/huge
    update_frequency: Optional[str] = None

@dataclass
class DataClassification:
    """Classification result for a data source"""
    source_name: str
    source_type: str
    detected_format: DataFormat
    structure: DataStructure
    characteristics: DataCharacteristics
    storage_recommendation: StorageRecommendation
    processing_tools: List[str]
    integration_options: List[str]
    quality_considerations: List[str]
    confidence: float

@dataclass
class ClassificationReport:
    """Complete classification report"""
    total_sources: int
    classifications: List[DataClassification]
    summary_by_structure: Dict[str, int]
    summary_by_format: Dict[str, int]
    storage_recommendations: Dict[str, List[str]]
    integration_strategy: Dict[str, str]


class DataTypeClassifier:
    """
    Classify construction data by type and recommend processing methods.
    Based on DDC methodology Chapter 2.1.
    """

    def __init__(self):
        self.format_signatures = self._define_format_signatures()
        self.structure_mapping = self._define_structure_mapping()
        self.storage_mapping = self._define_storage_mapping()
        self.processing_tools = self._define_processing_tools()

    def _define_format_signatures(self) -> Dict[str, Dict]:
        """Define format detection signatures"""
        return {
            # File extensions
            ".csv": {"format": DataFormat.CSV, "structure": DataStructure.STRUCTURED},
            ".xlsx": {"format": DataFormat.EXCEL, "structure": DataStructure.STRUCTURED},
            ".xls": {"format": DataFormat.EXCEL, "structure": DataStructure.STRUCTURED},
            ".json": {"format": DataFormat.JSON, "structure": DataStructure.SEMI_STRUCTURED},
            ".xml": {"format": DataFormat.XML, "structure": DataStructure.SEMI_STRUCTURED},
            ".ifc": {"format": DataFormat.IFC, "structure": DataStructure.SEMI_STRUCTURED},
            ".bcf": {"format": DataFormat.BCF, "structure": DataStructure.SEMI_STRUCTURED},
            ".pdf": {"format": DataFormat.PDF, "structure": DataStructure.UNSTRUCTURED},
            ".docx": {"format": DataFormat.DOCX, "structure": DataStructure.UNSTRUCTURED},
            ".dwg": {"format": DataFormat.DWG, "structure": DataStructure.GEOMETRIC},
            ".dxf": {"format": DataFormat.DXF, "structure": DataStructure.GEOMETRIC},
            ".rvt": {"format": DataFormat.RVT, "structure": DataStructure.GEOMETRIC},
            ".nwd": {"format": DataFormat.NWD, "structure": DataStructure.GEOMETRIC},
            ".mpp": {"format": DataFormat.MPP, "structure": DataStructure.TEMPORAL},
            ".xer": {"format": DataFormat.XER, "structure": DataStructure.TEMPORAL},
            ".parquet": {"format": DataFormat.PARQUET, "structure": DataStructure.STRUCTURED},
            ".jpg": {"format": DataFormat.IMAGE, "structure": DataStructure.UNSTRUCTURED},
            ".png": {"format": DataFormat.IMAGE, "structure": DataStructure.UNSTRUCTURED},
            ".mp4": {"format": DataFormat.VIDEO, "structure": DataStructure.UNSTRUCTURED}
        }

    def _define_structure_mapping(self) -> Dict[DataStructure, Dict]:
        """Define characteristics for each structure type"""
        return {
            DataStructure.STRUCTURED: {
                "description": "Tabular data with fixed schema",
                "examples": ["Cost databases", "Material lists", "Vendor records"],
                "query_support": True,
                "schema_required": True
            },
            DataStructure.SEMI_STRUCTURED: {
                "description": "Hierarchical data with flexible schema",
                "examples": ["BIM models (IFC)", "API responses", "Configuration files"],
                "query_support": True,
                "schema_required": False
            },
            DataStructure.UNSTRUCTURED: {
                "description": "No predefined schema or format",
                "examples": ["Contracts", "Photos", "Emails", "Meeting notes"],
                "query_support": False,
                "schema_required": False
            },
            DataStructure.GEOMETRIC: {
                "description": "3D/2D geometric and spatial data",
                "examples": ["CAD drawings", "BIM geometry", "Point clouds"],
                "query_support": True,
                "schema_required": True
            },
            DataStructure.TEMPORAL: {
                "description": "Time-based sequential data",
                "examples": ["Schedules", "Progress data", "Sensor readings"],
                "query_support": True,
                "schema_required": True
            },
            DataStructure.SPATIAL: {
                "description": "Geographic and location data",
                "examples": ["Site maps", "GPS tracks", "GIS layers"],
                "query_support": True,
                "schema_required": True
            }
        }

    def _define_storage_mapping(self) -> Dict[DataStructure, StorageRecommendation]:
        """Map data structures to storage recommendations"""
        return {
            DataStructure.STRUCTURED: StorageRecommendation.RELATIONAL_DB,
            DataStructure.SEMI_STRUCTURED: StorageRecommendation.DOCUMENT_DB,
            DataStructure.UNSTRUCTURED: StorageRecommendation.OBJECT_STORAGE,
            DataStructure.GEOMETRIC: StorageRecommendation.FILE_SYSTEM,
            DataStructure.TEMPORAL: StorageRecommendation.TIME_SERIES_DB,
            DataStructure.SPATIAL: StorageRecommendation.RELATIONAL_DB
        }

    def _define_processing_tools(self) -> Dict[DataFormat, List[str]]:
        """Define processing tools for each format"""
        return {
            DataFormat.CSV: ["pandas", "polars", "duckdb"],
            DataFormat.EXCEL: ["pandas", "openpyxl", "xlrd"],
            DataFormat.JSON: ["json", "pandas", "jq"],
            DataFormat.XML: ["lxml", "ElementTree", "BeautifulSoup"],
            DataFormat.IFC: ["ifcopenshell", "IfcOpenShell", "xBIM"],
            DataFormat.BCF: ["bcfpython", "ifcopenshell"],
            DataFormat.PDF: ["pdfplumber", "PyPDF2", "pdf2image"],
            DataFormat.DOCX: ["python-docx", "mammoth"],
            DataFormat.DWG: ["ezdxf", "Teigha", "ODA SDK"],
            DataFormat.DXF: ["ezdxf", "dxfgrabber"],
            DataFormat.RVT: ["Revit API", "pyRevit", "Dynamo"],
            DataFormat.NWD: ["Navisworks API", "NW API"],
            DataFormat.MPP: ["mpxj", "Project API"],
            DataFormat.XER: ["xerparser", "P6 API"],
            DataFormat.PARQUET: ["pandas", "pyarrow", "polars"],
            DataFormat.IMAGE: ["PIL", "opencv", "scikit-image"],
            DataFormat.VIDEO: ["opencv", "ffmpeg", "moviepy"]
        }

    def classify_source(
        self,
        source_name: str,
        source_type: str,
        file_extension: Optional[str] = None,
        sample_data: Optional[Any] = None,
        metadata: Optional[Dict] = None
    ) -> DataClassification:
        """
        Classify a single data source.

        Args:
            source_name: Name of the data source
            source_type: Type (file, database, api, etc.)
            file_extension: File extension if applicable
            sample_data: Sample of the data for analysis
            metadata: Additional metadata

        Returns:
            Classification result
        """
        # Detect format
        detected_format, structure = self._detect_format(
            file_extension, source_type, sample_data
        )

        # Analyze characteristics
        characteristics = self._analyze_characteristics(
            detected_format, structure, sample_data, metadata
        )

        # Determine storage recommendation
        storage = self._recommend_storage(structure, characteristics)

        # Get processing tools
        tools = self.processing_tools.get(detected_format, [])

        # Determine integration options
        integration = self._get_integration_options(detected_format, structure)

        # Quality considerations
        quality = self._get_quality_considerations(detected_format, structure)

        # Calculate confidence
        confidence = self._calculate_confidence(
            file_extension, sample_data, metadata
        )

        return DataClassification(
            source_name=source_name,
            source_type=source_type,
            detected_format=detected_format,
            structure=structure,
            characteristics=characteristics,
            storage_recommendation=storage,
            processing_tools=tools,
            integration_options=integration,
            quality_considerations=quality,
            confidence=confidence
        )

    def _detect_format(
        self,
        extension: Optional[str],
        source_type: str,
        sample: Optional[Any]
    ) -> Tuple[DataFormat, DataStructure]:
        """Detect data format and structure"""
        # Check file extension
        if extension:
            ext = extension.lower() if extension.startswith('.') else f".{extension.lower()}"
            if ext in self.format_signatures:
                sig = self.format_signatures[ext]
                return sig["format"], sig["structure"]

        # Check source type
        if source_type == "database":
            return DataFormat.SQL, DataStructure.STRUCTURED
        elif source_type == "api":
            return DataFormat.JSON, DataStructure.SEMI_STRUCTURED

        # Analyze sample data
        if sample:
            if isinstance(sample, dict):
                return DataFormat.JSON, DataStructure.SEMI_STRUCTURED
            elif isinstance(sample, list) and all(isinstance(x, dict) for x in sample):
                return DataFormat.JSON, DataStructure.STRUCTURED
            elif isinstance(sample, str):
                if sample.strip().startswith('<'):
                    return DataFormat.XML, DataStructure.SEMI_STRUCTURED
                elif sample.strip().startswith('{'):
                    return DataFormat.JSON, DataStructure.SEMI_STRUCTURED

        # Default
        return DataFormat.JSON, DataStructure.SEMI_STRUCTURED

    def _analyze_characteristics(
        self,
        format: DataFormat,
        structure: DataStructure,
        sample: Optional[Any],
        metadata: Optional[Dict]
    ) -> DataCharacteristics:
        """Analyze data characteristics"""
        return DataCharacteristics(
            has_schema=structure in [DataStructure.STRUCTURED, DataStructure.TEMPORAL],
            has_relationships=format in [DataFormat.IFC, DataFormat.SQL],
            is_queryable=structure != DataStructure.UNSTRUCTURED,
            is_binary=format in [
                DataFormat.DWG, DataFormat.RVT, DataFormat.NWD,
                DataFormat.IMAGE, DataFormat.VIDEO, DataFormat.PDF
            ],
            has_geometry=structure == DataStructure.GEOMETRIC or format == DataFormat.IFC,
            has_temporal=structure == DataStructure.TEMPORAL,
            has_text_content=format in [
                DataFormat.PDF, DataFormat.DOCX, DataFormat.CSV
            ],
            estimated_volume=metadata.get("volume") if metadata else None,
            update_frequency=metadata.get("update_frequency") if metadata else None
        )

    def _recommend_storage(
        self,
        structure: DataStructure,
        characteristics: DataCharacteristics
    ) -> StorageRecommendation:
        """Recommend storage solution"""
        # Special cases
        if characteristics.has_text_content and not characteristics.has_schema:
            return StorageRecommendation.VECTOR_DB

        if characteristics.is_binary and characteristics.estimated_volume == "huge":
            return StorageRecommendation.OBJECT_STORAGE

        if characteristics.has_relationships:
            return StorageRecommendation.GRAPH_DB

        # Default mapping
        return self.storage_mapping.get(structure, StorageRecommendation.FILE_SYSTEM)

    def _get_integration_options(
        self,
        format: DataFormat,
        structure: DataStructure
    ) -> List[str]:
        """Get integration options for the data"""
        options = []

        if structure == DataStructure.STRUCTURED:
            options.extend(["Direct SQL queries", "ETL pipelines", "API export"])
        elif structure == DataStructure.SEMI_STRUCTURED:
            options.extend(["JSON/XML parsing", "Schema validation", "API integration"])
        elif structure == DataStructure.UNSTRUCTURED:
            options.extend(["OCR extraction", "NLP processing", "ML classification"])
        elif structure == DataStructure.GEOMETRIC:
            options.extend(["IFC export", "Geometry extraction", "Clash detection"])

        # Format-specific options
        if format == DataFormat.IFC:
            options.append("IFC import/export via IfcOpenShell")
        elif format == DataFormat.EXCEL:
            options.append("Pandas DataFrame conversion")
        elif format == DataFormat.PDF:
            options.append("PDF text/table extraction")

        return options

    def _get_quality_considerations(
        self,
        format: DataFormat,
        structure: DataStructure
    ) -> List[str]:
        """Get quality considerations"""
        considerations = []

        if structure == DataStructure.STRUCTURED:
            considerations.extend([
                "Validate schema consistency",
                "Check for null/missing values",
                "Verify data types"
            ])
        elif structure == DataStructure.UNSTRUCTURED:
            considerations.extend([
                "OCR accuracy verification",
                "Text encoding issues",
                "Content extraction completeness"
            ])
        elif structure == DataStructure.GEOMETRIC:
            considerations.extend([
                "Model validity (closed solids)",
                "Coordinate system consistency",
                "Unit verification"
            ])

        # Format-specific
        if format == DataFormat.IFC:
            considerations.append("IFC schema version compatibility")
        elif format == DataFormat.EXCEL:
            considerations.append("Formula vs value extraction")

        return considerations

    def _calculate_confidence(
        self,
        extension: Optional[str],
        sample: Optional[Any],
        metadata: Optional[Dict]
    ) -> float:
        """Calculate classification confidence"""
        confidence = 0.5  # Base confidence

        if extension:
            confidence += 0.3  # Extension provides good hint
        if sample:
            confidence += 0.15  # Sample data helps
        if metadata:
            confidence += 0.05  # Metadata adds context

        return min(1.0, confidence)

    def classify_multiple(
        self,
        sources: List[Dict]
    ) -> ClassificationReport:
        """
        Classify multiple data sources.

        Args:
            sources: List of source definitions

        Returns:
            Complete classification report
        """
        classifications = []

        for source in sources:
            classification = self.classify_source(
                source_name=source["name"],
                source_type=source.get("type", "file"),
                file_extension=source.get("extension"),
                sample_data=source.get("sample"),
                metadata=source.get("metadata")
            )
            classifications.append(classification)

        # Generate summaries
        summary_structure = {}
        summary_format = {}
        storage_recs = {}

        for c in classifications:
            # Structure summary
            struct = c.structure.value
            summary_structure[struct] = summary_structure.get(struct, 0) + 1

            # Format summary
            fmt = c.detected_format.value
            summary_format[fmt] = summary_format.get(fmt, 0) + 1

            # Storage recommendations
            storage = c.storage_recommendation.value
            if storage not in storage_recs:
                storage_recs[storage] = []
            storage_recs[storage].append(c.source_name)

        # Integration strategy
        strategy = self._generate_integration_strategy(classifications)

        return ClassificationReport(
            total_sources=len(sources),
            classifications=classifications,
            summary_by_structure=summary_structure,
            summary_by_format=summary_format,
            storage_recommendations=storage_recs,
            integration_strategy=strategy
        )

    def _generate_integration_strategy(
        self,
        classifications: List[DataClassification]
    ) -> Dict[str, str]:
        """Generate integration strategy"""
        strategy = {}

        # Group by structure
        structured = [c for c in classifications if c.structure == DataStructure.STRUCTURED]
        semi = [c for c in classifications if c.structure == DataStructure.SEMI_STRUCTURED]
        unstructured = [c for c in classifications if c.structure == DataStructure.UNSTRUCTURED]
        geometric = [c for c in classifications if c.structure == DataStructure.GEOMETRIC]

        if structured:
            strategy["structured_data"] = (
                "Use ETL pipeline to consolidate into central data warehouse. "
                "Implement SQL-based querying and reporting."
            )

        if semi:
            strategy["semi_structured_data"] = (
                "Use document database for flexible storage. "
                "Implement schema validation at ingestion."
            )

        if unstructured:
            strategy["unstructured_data"] = (
                "Extract text content using OCR/NLP. "
                "Store in vector database for semantic search."
            )

        if geometric:
            strategy["geometric_data"] = (
                "Standardize on IFC format for exchange. "
                "Maintain native formats for editing."
            )

        return strategy

    def generate_report(self, report: ClassificationReport) -> str:
        """Generate classification report"""
        output = f"""
# Data Classification Report

**Total Sources Analyzed:** {report.total_sources}

## Summary by Structure

"""
        for struct, count in report.summary_by_structure.items():
            output += f"- **{struct.title()}**: {count} sources\n"

        output += "\n## Summary by Format\n\n"
        for fmt, count in report.summary_by_format.items():
            output += f"- **{fmt.upper()}**: {count} sources\n"

        output += "\n## Storage Recommendations\n\n"
        for storage, sources in report.storage_recommendations.items():
            output += f"### {storage.replace('_', ' ').title()}\n"
            for src in sources:
                output += f"- {src}\n"
            output += "\n"

        output += "## Integration Strategy\n\n"
        for category, strategy in report.integration_strategy.items():
            output += f"### {category.replace('_', ' ').title()}\n{strategy}\n\n"

        output += "## Detailed Classifications\n\n"
        for c in report.classifications[:10]:
            output += f"""
### {c.source_name}
- **Format:** {c.detected_format.value}
- **Structure:** {c.structure.value}
- **Storage:** {c.storage_recommendation.value}
- **Tools:** {', '.join(c.processing_tools[:3])}
- **Confidence:** {c.confidence:.0%}
"""

        return output
```

## Common Use Cases

### Classify Single Data Source

```python
classifier = DataTypeClassifier()

# Classify a BIM model
classification = classifier.classify_source(
    source_name="Building Model",
    source_type="file",
    file_extension=".ifc",
    metadata={"volume": "large"}
)

print(f"Format: {classification.detected_format.value}")
print(f"Structure: {classification.structure.value}")
print(f"Storage: {classification.storage_recommendation.value}")
print(f"Tools: {classification.processing_tools}")
```

### Classify Multiple Sources

```python
sources = [
    {"name": "Cost Database", "type": "database", "extension": ".sql"},
    {"name": "Building Model", "type": "file", "extension": ".ifc"},
    {"name": "Contract PDFs", "type": "file", "extension": ".pdf"},
    {"name": "Site Photos", "type": "file", "extension": ".jpg"},
    {"name": "Schedule", "type": "file", "extension": ".mpp"}
]

report = classifier.classify_multiple(sources)

print(f"Total: {report.total_sources}")
print(f"By structure: {report.summary_by_structure}")
```

### Generate Classification Report

```python
report_text = classifier.generate_report(report)
print(report_text)

# Save to file
with open("classification_report.md", "w") as f:
    f.write(report_text)
```

## Quick Reference

| Component | Purpose |
|-----------|---------|
| `DataTypeClassifier` | Main classification engine |
| `DataStructure` | Structure types (structured, semi, unstructured) |
| `DataFormat` | File format detection |
| `StorageRecommendation` | Storage system recommendations |
| `DataClassification` | Classification result |
| `ClassificationReport` | Multi-source report |

## Resources

- **Book**: "Data-Driven Construction" by Artem Boiko, Chapter 2.1
- **Website**: https://datadrivenconstruction.io

## Next Steps

- Use [sql-query-builder](../sql-query-builder/SKILL.md) for structured data queries
- Use [pdf-to-structured](../../Chapter-2.4/pdf-to-structured/SKILL.md) for unstructured data
- Use [data-model-designer](../../Chapter-2.5/data-model-designer/SKILL.md) for schema design
