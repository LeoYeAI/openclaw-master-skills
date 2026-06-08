---
name: "image-to-data"
description: "Extract data from construction images using AI Vision. Analyze site photos, scanned documents, drawings."
---

# Image To Data

## Overview

Based on DDC methodology (Chapter 2.4), this skill extracts structured data from construction images using computer vision, OCR, and AI models to analyze site photos, scanned documents, and drawings.

**Book Reference:** "Преобразование данных в структурированную форму" / "Data Transformation to Structured Form"

## Quick Start

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import json
import base64

class ImageType(Enum):
    """Types of construction images"""
    SITE_PHOTO = "site_photo"
    SCANNED_DOCUMENT = "scanned_document"
    FLOOR_PLAN = "floor_plan"
    ELEVATION = "elevation"
    DETAIL_DRAWING = "detail_drawing"
    PROGRESS_PHOTO = "progress_photo"
    SAFETY_PHOTO = "safety_photo"
    DEFECT_PHOTO = "defect_photo"
    MATERIAL_PHOTO = "material_photo"
    EQUIPMENT_PHOTO = "equipment_photo"

class ExtractionType(Enum):
    """Types of data extraction"""
    OCR_TEXT = "ocr_text"
    TABLE = "table"
    OBJECT_DETECTION = "object_detection"
    MEASUREMENT = "measurement"
    CLASSIFICATION = "classification"
    PROGRESS = "progress"

@dataclass
class BoundingBox:
    """Bounding box for detected region"""
    x: int
    y: int
    width: int
    height: int
    confidence: float = 1.0

@dataclass
class TextRegion:
    """Extracted text region from image"""
    text: str
    bbox: BoundingBox
    confidence: float
    language: str = "en"

@dataclass
class DetectedObject:
    """Detected object in image"""
    label: str
    bbox: BoundingBox
    confidence: float
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExtractedTable:
    """Extracted table from image"""
    headers: List[str]
    rows: List[List[str]]
    bbox: BoundingBox
    confidence: float

@dataclass
class ProgressMeasurement:
    """Progress measurement from image"""
    element_type: str
    total_count: int
    completed_count: int
    percent_complete: float
    area_sqft: Optional[float] = None
    volume_cuft: Optional[float] = None

@dataclass
class ImageAnalysisResult:
    """Complete image analysis result"""
    image_id: str
    image_type: ImageType
    text_regions: List[TextRegion]
    detected_objects: List[DetectedObject]
    tables: List[ExtractedTable]
    progress: Optional[ProgressMeasurement] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0


class OCREngine:
    """OCR engine for text extraction"""

    def __init__(self, engine: str = "tesseract"):
        self.engine = engine
        self.supported_languages = ["en", "ru", "de", "fr", "es"]

    def extract_text(
        self,
        image_data: bytes,
        language: str = "en"
    ) -> List[TextRegion]:
        """Extract text from image"""
        # Simulated OCR extraction (use actual OCR library in production)
        # In production: pytesseract, EasyOCR, or cloud OCR services

        regions = []

        # Simulate detecting title block in drawing
        regions.append(TextRegion(
            text="PROJECT: OFFICE BUILDING",
            bbox=BoundingBox(x=100, y=50, width=300, height=30, confidence=0.95),
            confidence=0.95,
            language=language
        ))

        regions.append(TextRegion(
            text="DRAWING: A-101",
            bbox=BoundingBox(x=100, y=90, width=200, height=25, confidence=0.92),
            confidence=0.92,
            language=language
        ))

        regions.append(TextRegion(
            text="SCALE: 1:100",
            bbox=BoundingBox(x=100, y=120, width=150, height=20, confidence=0.88),
            confidence=0.88,
            language=language
        ))

        return regions

    def extract_structured_text(
        self,
        image_data: bytes,
        template: Optional[Dict] = None
    ) -> Dict[str, str]:
        """Extract structured text using template matching"""
        # Extract text regions
        regions = self.extract_text(image_data)

        # Match to template fields
        structured = {}

        if template:
            for field_name, field_config in template.items():
                # Find matching region
                for region in regions:
                    if field_config.get("keyword") in region.text.lower():
                        structured[field_name] = region.text
                        break
        else:
            # Default extraction
            for region in regions:
                if "PROJECT:" in region.text:
                    structured["project_name"] = region.text.split(":")[-1].strip()
                elif "DRAWING:" in region.text:
                    structured["drawing_number"] = region.text.split(":")[-1].strip()
                elif "SCALE:" in region.text:
                    structured["scale"] = region.text.split(":")[-1].strip()

        return structured


class ObjectDetector:
    """Object detection for construction images"""

    def __init__(self, model: str = "yolov8"):
        self.model = model
        self.construction_classes = self._load_construction_classes()

    def _load_construction_classes(self) -> Dict[str, Dict]:
        """Load construction-specific object classes"""
        return {
            # Equipment
            "excavator": {"category": "equipment", "safety_zone": 20},
            "crane": {"category": "equipment", "safety_zone": 30},
            "forklift": {"category": "equipment", "safety_zone": 10},
            "concrete_mixer": {"category": "equipment", "safety_zone": 5},
            "scaffolding": {"category": "equipment", "safety_zone": 5},

            # Safety
            "hard_hat": {"category": "ppe", "required": True},
            "safety_vest": {"category": "ppe", "required": True},
            "safety_glasses": {"category": "ppe", "required": False},
            "harness": {"category": "ppe", "required": False},

            # Materials
            "rebar_bundle": {"category": "material", "unit": "bundle"},
            "concrete_block": {"category": "material", "unit": "pallet"},
            "lumber_stack": {"category": "material", "unit": "bundle"},
            "pipe_stack": {"category": "material", "unit": "bundle"},

            # Workers
            "worker": {"category": "person", "track": True},

            # Building elements
            "column": {"category": "structure"},
            "beam": {"category": "structure"},
            "slab": {"category": "structure"},
            "wall": {"category": "structure"},
        }

    def detect(
        self,
        image_data: bytes,
        confidence_threshold: float = 0.5
    ) -> List[DetectedObject]:
        """Detect objects in image"""
        # Simulated detection (use actual model in production)
        # In production: YOLO, Faster R-CNN, etc.

        detected = []

        # Simulate detected objects
        sample_detections = [
            ("worker", 0.92, BoundingBox(200, 300, 80, 180, 0.92)),
            ("hard_hat", 0.88, BoundingBox(210, 300, 30, 25, 0.88)),
            ("safety_vest", 0.85, BoundingBox(210, 340, 60, 80, 0.85)),
            ("scaffolding", 0.78, BoundingBox(400, 100, 200, 400, 0.78)),
            ("concrete_block", 0.72, BoundingBox(50, 450, 100, 50, 0.72)),
        ]

        for label, conf, bbox in sample_detections:
            if conf >= confidence_threshold:
                class_info = self.construction_classes.get(label, {})
                detected.append(DetectedObject(
                    label=label,
                    bbox=bbox,
                    confidence=conf,
                    attributes=class_info
                ))

        return detected

    def detect_safety_compliance(
        self,
        image_data: bytes
    ) -> Dict:
        """Detect safety compliance in image"""
        objects = self.detect(image_data)

        workers = [o for o in objects if o.label == "worker"]
        hard_hats = [o for o in objects if o.label == "hard_hat"]
        vests = [o for o in objects if o.label == "safety_vest"]

        compliance = {
            "workers_detected": len(workers),
            "hard_hats_detected": len(hard_hats),
            "vests_detected": len(vests),
            "hard_hat_compliance": len(hard_hats) / len(workers) if workers else 1.0,
            "vest_compliance": len(vests) / len(workers) if workers else 1.0,
            "overall_compliance": "compliant" if len(hard_hats) >= len(workers) else "non-compliant",
            "violations": []
        }

        if len(hard_hats) < len(workers):
            compliance["violations"].append({
                "type": "missing_hard_hat",
                "count": len(workers) - len(hard_hats)
            })

        return compliance


class TableExtractor:
    """Extract tables from images"""

    def extract_tables(
        self,
        image_data: bytes,
        detect_headers: bool = True
    ) -> List[ExtractedTable]:
        """Extract tables from image"""
        # Simulated table extraction
        # In production: Camelot, Tabula, or custom CNN

        tables = []

        # Simulate a schedule table
        tables.append(ExtractedTable(
            headers=["Activity", "Start", "End", "Duration"],
            rows=[
                ["Foundation", "2024-01-01", "2024-01-15", "14 days"],
                ["Framing", "2024-01-16", "2024-02-28", "44 days"],
                ["MEP Rough-in", "2024-03-01", "2024-03-31", "31 days"]
            ],
            bbox=BoundingBox(50, 200, 500, 200, 0.85),
            confidence=0.85
        ))

        return tables

    def table_to_dataframe(self, table: ExtractedTable) -> Dict:
        """Convert table to dictionary (DataFrame-like)"""
        return {
            "columns": table.headers,
            "data": table.rows,
            "records": [
                dict(zip(table.headers, row))
                for row in table.rows
            ]
        }


class ProgressAnalyzer:
    """Analyze construction progress from images"""

    def __init__(self):
        self.reference_models = {}

    def analyze_progress(
        self,
        current_image: bytes,
        reference_image: Optional[bytes] = None,
        element_type: str = "general"
    ) -> ProgressMeasurement:
        """Analyze progress by comparing images"""
        # Simulated progress analysis
        # In production: Use semantic segmentation + comparison

        # Simulate progress detection
        return ProgressMeasurement(
            element_type=element_type,
            total_count=100,
            completed_count=65,
            percent_complete=65.0,
            area_sqft=15000.0,
            volume_cuft=None
        )

    def compare_with_plan(
        self,
        site_photo: bytes,
        plan_image: bytes
    ) -> Dict:
        """Compare site photo with plan"""
        return {
            "match_score": 0.78,
            "deviations": [],
            "completion_estimate": 65.0,
            "areas_of_concern": []
        }


class ConstructionImageAnalyzer:
    """
    Main class for construction image analysis.
    Based on DDC methodology Chapter 2.4.
    """

    def __init__(self):
        self.ocr = OCREngine()
        self.detector = ObjectDetector()
        self.table_extractor = TableExtractor()
        self.progress_analyzer = ProgressAnalyzer()

    def analyze_image(
        self,
        image_data: bytes,
        image_type: ImageType,
        image_id: str = "img_001",
        extract_types: Optional[List[ExtractionType]] = None
    ) -> ImageAnalysisResult:
        """
        Analyze a construction image.

        Args:
            image_data: Image data as bytes
            image_type: Type of image
            image_id: Unique image identifier
            extract_types: Types of extraction to perform

        Returns:
            Complete analysis result
        """
        start_time = datetime.now()

        if extract_types is None:
            extract_types = [ExtractionType.OCR_TEXT, ExtractionType.OBJECT_DETECTION]

        text_regions = []
        detected_objects = []
        tables = []
        progress = None

        # OCR extraction
        if ExtractionType.OCR_TEXT in extract_types:
            text_regions = self.ocr.extract_text(image_data)

        # Object detection
        if ExtractionType.OBJECT_DETECTION in extract_types:
            detected_objects = self.detector.detect(image_data)

        # Table extraction
        if ExtractionType.TABLE in extract_types:
            tables = self.table_extractor.extract_tables(image_data)

        # Progress analysis
        if ExtractionType.PROGRESS in extract_types:
            progress = self.progress_analyzer.analyze_progress(image_data)

        processing_time = (datetime.now() - start_time).total_seconds()

        return ImageAnalysisResult(
            image_id=image_id,
            image_type=image_type,
            text_regions=text_regions,
            detected_objects=detected_objects,
            tables=tables,
            progress=progress,
            metadata={"extraction_types": [e.value for e in extract_types]},
            processing_time=processing_time
        )

    def analyze_site_photo(
        self,
        image_data: bytes,
        image_id: str = "site_001"
    ) -> Dict:
        """Analyze site photo for progress and safety"""
        result = self.analyze_image(
            image_data,
            ImageType.SITE_PHOTO,
            image_id,
            [ExtractionType.OBJECT_DETECTION, ExtractionType.PROGRESS]
        )

        safety = self.detector.detect_safety_compliance(image_data)

        return {
            "image_id": result.image_id,
            "objects_detected": len(result.detected_objects),
            "progress": result.progress,
            "safety_compliance": safety,
            "equipment": [o.label for o in result.detected_objects if o.attributes.get("category") == "equipment"],
            "materials": [o.label for o in result.detected_objects if o.attributes.get("category") == "material"]
        }

    def extract_drawing_data(
        self,
        image_data: bytes,
        image_id: str = "dwg_001"
    ) -> Dict:
        """Extract data from scanned drawing"""
        result = self.analyze_image(
            image_data,
            ImageType.FLOOR_PLAN,
            image_id,
            [ExtractionType.OCR_TEXT, ExtractionType.TABLE]
        )

        # Extract title block info
        title_block = self.ocr.extract_structured_text(image_data)

        return {
            "image_id": result.image_id,
            "title_block": title_block,
            "text_regions": len(result.text_regions),
            "tables": [
                self.table_extractor.table_to_dataframe(t)
                for t in result.tables
            ],
            "all_text": [r.text for r in result.text_regions]
        }

    def batch_analyze(
        self,
        images: List[Tuple[bytes, ImageType, str]]
    ) -> List[ImageAnalysisResult]:
        """Analyze multiple images"""
        results = []
        for image_data, image_type, image_id in images:
            result = self.analyze_image(image_data, image_type, image_id)
            results.append(result)
        return results

    def export_results(
        self,
        result: ImageAnalysisResult,
        format: str = "json"
    ) -> str:
        """Export analysis results"""
        data = {
            "image_id": result.image_id,
            "image_type": result.image_type.value,
            "text_count": len(result.text_regions),
            "object_count": len(result.detected_objects),
            "table_count": len(result.tables),
            "texts": [
                {"text": r.text, "confidence": r.confidence}
                for r in result.text_regions
            ],
            "objects": [
                {"label": o.label, "confidence": o.confidence}
                for o in result.detected_objects
            ],
            "processing_time": result.processing_time
        }

        if format == "json":
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
```

## Common Use Cases

### Analyze Site Photo

```python
analyzer = ConstructionImageAnalyzer()

# Load image (in production, read from file)
with open("site_photo.jpg", "rb") as f:
    image_data = f.read()

result = analyzer.analyze_site_photo(image_data)

print(f"Objects detected: {result['objects_detected']}")
print(f"Safety compliance: {result['safety_compliance']['overall_compliance']}")
print(f"Progress: {result['progress'].percent_complete}%")
```

### Extract Drawing Data

```python
with open("floor_plan.png", "rb") as f:
    drawing_data = f.read()

data = analyzer.extract_drawing_data(drawing_data)

print(f"Drawing: {data['title_block'].get('drawing_number')}")
print(f"Project: {data['title_block'].get('project_name')}")
for table in data['tables']:
    print(f"Table with {len(table['records'])} rows")
```

### Detect Safety Violations

```python
detector = ObjectDetector()

with open("site_photo.jpg", "rb") as f:
    image_data = f.read()

safety = detector.detect_safety_compliance(image_data)

if safety['overall_compliance'] == 'non-compliant':
    for violation in safety['violations']:
        print(f"Violation: {violation['type']} - Count: {violation['count']}")
```

## Quick Reference

| Component | Purpose |
|-----------|---------|
| `ConstructionImageAnalyzer` | Main analysis engine |
| `OCREngine` | Text extraction |
| `ObjectDetector` | Object detection |
| `TableExtractor` | Table extraction |
| `ProgressAnalyzer` | Progress analysis |
| `ImageAnalysisResult` | Complete analysis result |

## Resources

- **Book**: "Data-Driven Construction" by Artem Boiko, Chapter 2.4
- **Website**: https://datadrivenconstruction.io

## Next Steps

- Use [cad-to-data](../cad-to-data/SKILL.md) for CAD/BIM extraction
- Use [defect-detection-ai](../../../DDC_Innovative/defect-detection-ai/SKILL.md) for defects
- Use [safety-compliance-checker](../../../DDC_Innovative/safety-compliance-checker/SKILL.md) for safety
