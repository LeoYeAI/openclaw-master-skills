# Deeplake Managed Service -- Format Classes

Format classes normalize domain-specific dataset layouts into column-oriented batches for `Client.ingest()`. All format classes inherit from the `Format` abstract base class.

Both Python and Node.js implement the same Format interface.

## Format Base Class

### Python

```python
from deeplake.managed.formats import Format

class Format(ABC):
    @abstractmethod
    def normalize(self) -> Iterator[Dict[str, List[Any]]]:
        """Yield column-oriented batches: {col_name: [values...]}."""
        ...

    def schema(self) -> Dict[str, str]:
        """Return {col: deeplake_type} hints. Override to declare types."""
        return {}

    def pg_schema(self) -> Dict[str, str]:
        """Return {col: pg_domain_type} overrides. Override for domain types."""
        return {}

    def image_columns(self) -> List[str]:
        """Return column names containing IMAGE data (for thumbnail generation).
        Default: auto-detect from pg_schema() -- columns with type "IMAGE".
        """
        return [col for col, t in self.pg_schema().items() if t == "IMAGE"]
```

### Node.js / TypeScript

```typescript
import type { Format, Batch, SchemaMap } from 'deeplake';

interface Format {
    normalize(): Iterable<Batch> | AsyncIterable<Batch>;
    schema?(): SchemaMap;               // { col: deeplake_type }
    pg_schema?(): Record<string, string>; // { col: pg_domain_type }
    image_columns?(): string[];          // columns for thumbnail generation
}
```

### Method Summary

| Method            | Required | Purpose                                           |
| ----------------- | -------- | ------------------------------------------------- |
| `normalize()`     | Yes      | Yield `dict[str, list]` batches                   |
| `schema()`        | No       | Declare deeplake storage types (e.g. `"BINARY"`)  |
| `pg_schema()`     | No       | Declare PG domain types (e.g. `"IMAGE"`)          |
| `image_columns()` | No       | List IMAGE columns for thumbnail auto-generation  |

---

## Type Inference

Column types are inferred automatically from Python/JS values when no schema hint is provided:

| Python type   | JS/TS type          | Inferred schema type |
| ------------- | ------------------- | -------------------- |
| `bool`        | `boolean`           | BOOL                 |
| `int`         | `number` (integer)  | INT64                |
| `float`       | `number` (decimal)  | FLOAT64              |
| `str`         | `string`            | TEXT                 |
| `bytes`       | `Buffer/Uint8Array` | BINARY               |
| `list[float]` | `number[]`          | EMBEDDING            |

---

## Minimal Example -- CSV with Linked Images

```python
from deeplake.managed.formats import Format

class CsvWithImages(Format):
    """Format for a CSV file where one column contains image file paths."""

    def __init__(self, csv_path, images_dir):
        self.csv_path = Path(csv_path)
        self.images_dir = Path(images_dir)

    def schema(self):
        return {"image": "BINARY"}

    def pg_schema(self):
        return {"image": "IMAGE"}

    def normalize(self):
        import csv

        with open(self.csv_path) as f:
            rows = list(csv.DictReader(f))

        batch = []
        for row in rows:
            img_path = self.images_dir / row["image_file"]
            if not img_path.exists():
                continue
            batch.append({
                "image": img_path.read_bytes(),        # bytes -> IMAGE (via pg_schema())
                "label": row["label"],                 # str -> TEXT
                "confidence": float(row["confidence"]), # float -> FLOAT64
            })
            if len(batch) >= 100:
                yield {k: [d[k] for d in batch] for k in batch[0]}
                batch = []
        if batch:
            yield {k: [d[k] for d in batch] for k in batch[0]}

# Usage
client.ingest("labeled_images", format=CsvWithImages(
    csv_path="annotations.csv",
    images_dir="images/",
))
# Thumbnails auto-generated for "image" column (declared as IMAGE in pg_schema)
```

---

## Key Rules for `normalize()`

1. **Yield `dict[str, list]`** -- each dict maps column names to equal-length lists (one entry per row)
2. **Use consistent column names** across all yielded batches
3. **Use native Python types** -- `int`, `float`, `str`, `bytes`, `bool`, `list[float]` for embeddings. Types are inferred from the first batch
4. **Batch for memory** -- don't load entire dataset into one dict; yield batches of ~100-1000 rows
5. **Validate in `normalize()`** -- raise `FileNotFoundError` or `ValueError` early for missing files or bad data
6. **Skip bad rows with logging** -- use `logger.warning()` and `continue` for recoverable issues (missing files, etc.)

---

## Optional `schema()` and `pg_schema()` Methods

- `schema()` returns `dict[str, str]` mapping column names to deeplake storage type names (e.g. `{"image": "BINARY", "mask": "BINARY"}`)
- `pg_schema()` returns `dict[str, str]` mapping column names to PostgreSQL domain types (e.g. `{"image": "IMAGE", "mask": "SEGMENT_MASK"}`)
- These hints override type inference for columns where Python types are ambiguous (e.g. `bytes` could be `BINARY`, `IMAGE`, `SEGMENT_MASK`, etc.)
- User-supplied schema to `ingest()` takes precedence over format schema hints
- Available domain types: `IMAGE`, `SEGMENT_MASK`, `BINARY_MASK`, `BOUNDING_BOX`, `CLASS_LABEL`, `POLYGON`, `POINT`, `MESH`, `MEDICAL`, `VIDEO`

---

## Thumbnail Auto-Generation

When a format's `image_columns()` returns column names (default: columns with `pg_schema()` type `"IMAGE"`), the SDK automatically generates thumbnails after ingestion:

- **Sizes:** 32x32, 64x64, 128x128, 256x256 (aspect-preserving)
- **Format:** JPEG, quality 85
- **Storage:** Shared `thumbnails` dataset at `{root_path}/thumbnails` with columns: `file_id`, `column_name`, `dimension`, `content`
- **Requires:** Pillow (Python) or sharp (Node.js)

Override `image_columns()` to customize which columns get thumbnails:

```python
class MyFormat(Format):
    def pg_schema(self):
        return {"photo": "IMAGE", "icon": "IMAGE"}

    def image_columns(self):
        return ["photo"]  # Only generate thumbnails for "photo", not "icon"
```

---

## Multi-File Format with Embeddings

```python
class ImageFolderWithEmbeddings(Format):
    """Images in subfolders (subfolder name = label) + pre-computed embeddings."""

    def __init__(self, root_dir, embeddings_path):
        self.root_dir = Path(root_dir)
        self.embeddings_path = Path(embeddings_path)

    def normalize(self):
        import json

        with open(self.embeddings_path) as f:
            embeddings = json.load(f)

        batch = []
        for label_dir in sorted(self.root_dir.iterdir()):
            if not label_dir.is_dir():
                continue
            label = label_dir.name
            for img_path in sorted(label_dir.glob("*.jpg")):
                emb = embeddings.get(img_path.name)
                if emb is None:
                    continue
                batch.append({
                    "image": img_path.read_bytes(),
                    "label": label,
                    "embedding": emb,
                    "filename": img_path.name,
                })
                if len(batch) >= 100:
                    yield {k: [d[k] for d in batch] for k in batch[0]}
                    batch = []
        if batch:
            yield {k: [d[k] for d in batch] for k in batch[0]}

client.ingest("classified_images", format=ImageFolderWithEmbeddings(
    root_dir="imagenet/train",
    embeddings_path="embeddings.json",
))
```

---

## Built-in Formats

### CocoPanoptic

```python
# Python
from deeplake.managed.formats import CocoPanoptic

client.ingest("panoptic", format=CocoPanoptic(
    images_dir="coco/train2017",
    masks_dir="coco/panoptic_train2017",
    annotations="coco/annotations/panoptic_train2017.json",
    batch_size=100,  # optional, default 100
))
```

```typescript
// Node.js
import { CocoPanoptic } from 'deeplake';

await client.ingest("panoptic", null, {
    format: new CocoPanoptic({
        imagesDir: "coco/train2017",
        masksDir: "coco/panoptic_train2017",
        annotations: "coco/annotations/panoptic_train2017.json",
        batchSize: 100,  // optional, default 100
    }),
});
```

**Parameters:**
- `images_dir` / `imagesDir` -- Directory containing the images (e.g. `train2017/`)
- `masks_dir` / `masksDir` -- Directory containing panoptic segmentation masks (e.g. `panoptic_train2017/`)
- `annotations` -- Path to the panoptic annotations JSON file
- `batch_size` / `batchSize` -- Images per batch (default 100)

**Generated columns:**
| Column          | Type           | Description                    |
| --------------- | -------------- | ------------------------------ |
| `coco_image_id` | int            | COCO image ID                  |
| `image`         | IMAGE          | Image binary data              |
| `mask`          | SEGMENT_MASK   | Panoptic segmentation mask PNG |
| `width`         | int            | Image width in pixels          |
| `height`        | int            | Image height in pixels         |
| `filename`      | str            | Original image filename        |
| `mask_filename` | str            | Panoptic mask PNG filename     |
| `segments_info` | str (JSON)     | Per-segment category/area info |
| `categories`    | str (JSON)     | Category definitions           |

**Note:** No external dependencies for CocoPanoptic -- uses only stdlib/built-in JSON and file I/O.

### Coco (Detection/Captions)

```python
# Python (requires pycocotools, Pillow, numpy)
from deeplake.managed.formats import Coco

client.ingest("coco_train", format=Coco(
    images_dir="coco/train2017",
    annotations_dir="coco/annotations",
))
```

```typescript
// Node.js (no external deps -- pure JS mask rendering)
import { Coco } from 'deeplake';

await client.ingest("coco_train", null, {
    format: new Coco({
        imagesDir: "coco/train2017",
        annotationsDir: "coco/annotations",
    }),
});
```

**Parameters:**
- `images_dir` / `imagesDir` -- Directory containing images
- `annotations_dir` / `annotationsDir` -- Directory containing annotation JSONs (optional, defaults to `<images_dir>/../annotations`)
- `instances_json` / `instancesJson` -- Explicit instances JSON path (optional, auto-detected from split name)
- `captions_json` / `captionsJson` -- Explicit captions JSON path (optional, `False`/`false` to skip)
- `batch_size` / `batchSize` -- Images per batch (default 100)
- `max_images` / `maxImages` -- Limit number of images (optional)

**Generated columns:**
| Column          | Type           | Description                                       |
| --------------- | -------------- | ------------------------------------------------- |
| `coco_image_id` | int            | COCO image ID                                     |
| `image`         | IMAGE          | Source image file bytes                            |
| `mask`          | SEGMENT_MASK   | Combined segmentation mask PNG (category per pixel)|
| `width`         | int            | Image width in pixels                             |
| `height`        | int            | Image height in pixels                            |
| `filename`      | str            | Original image filename                           |
| `captions`      | str (JSON)     | JSON list of caption strings                      |
| `annotations`   | str (JSON)     | JSON list of annotation dicts (bbox, category_id, area, iscrowd) |
| `categories`    | str (JSON)     | Category definitions (same for all rows)          |
| `num_objects`   | int            | Number of object annotations for this image       |

### LeRobot (3-table design)

```python
# Python
from deeplake.managed.formats import LeRobotTasks, LeRobotFrames, LeRobotEpisodes

client.ingest("tasks", format=LeRobotTasks(dataset_dir="lerobot_data"))
client.ingest("frames", format=LeRobotFrames(dataset_dir="lerobot_data", chunk_start=0, chunk_end=10))
client.ingest("episodes", format=LeRobotEpisodes(dataset_dir="lerobot_data", chunk_start=0, chunk_end=10))
```

```typescript
// Node.js
import { LeRobotTasks, LeRobotFrames, LeRobotEpisodes } from 'deeplake';

await client.ingest("tasks", null, { format: new LeRobotTasks({ datasetDir: "lerobot_data" }) });
await client.ingest("frames", null, { format: new LeRobotFrames({ datasetDir: "lerobot_data", chunkStart: 0, chunkEnd: 10 }) });
await client.ingest("episodes", null, { format: new LeRobotEpisodes({ datasetDir: "lerobot_data", chunkStart: 0, chunkEnd: 10 }) });
```

**LeRobotTasks columns:**
| Column       | Type | Description              |
| ------------ | ---- | ------------------------ |
| `task_index` | int  | Task index               |
| `task`       | str  | Task description string  |

**LeRobotFrames columns:**
| Column          | Type  | Description                   |
| --------------- | ----- | ----------------------------- |
| `index`         | int   | Global frame index            |
| `episode_index` | int   | Episode this frame belongs to |
| `frame_index`   | int   | Frame index within episode    |
| `task_index`    | int   | Task index                    |
| `timestamp`     | float | Frame timestamp               |
| `state_x` .. `state_gripper` | float | 8 unpacked state scalars |
| `action_x` .. `action_gripper` | float | 7 unpacked action scalars |

**LeRobotEpisodes columns:**
| Column             | Type   | Description                  |
| ------------------ | ------ | ---------------------------- |
| `episode_index`    | int    | Episode index                |
| `task`             | str    | Task description             |
| `length`           | int    | Number of frames in episode  |
| `exterior_1_video` | VIDEO  | Exterior camera 1 MP4 bytes  |
| `exterior_2_video` | VIDEO  | Exterior camera 2 MP4 bytes  |
| `wrist_video`      | VIDEO  | Wrist camera MP4 bytes       |
