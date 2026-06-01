# Models API Reference

## Methods

### `pony_flash.models.list(**kwargs) -> SyncPage[ModelInfo]`

List available models. Supports pagination and filtering by type.

### `pony_flash.models.get(model_id: str) -> ModelDetail`

Get detailed information about a specific model.

## list() Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `cursor` | `str` | No | — | Pagination cursor |
| `limit` | `int` | No | — | Max items per page |
| `type` | `str` | No | — | Filter by type (e.g. `"image"`, `"video"`, `"speech"`, `"music"`) |

## Return types

### ModelInfo

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Model identifier |
| `type` | `str` | Model type |
| `input` | `List[str]` | Supported input types |
| `output` | `List[str]` | Supported output types |
| `supported_sizes` | `List[str]` | Available output sizes |
| `supported_durations` | `List[int]` | Available durations |
| `supported_qualities` | `List[str]` | Quality options |
| `supported_output_formats` | `List[str]` | Output format options |
| `pricing` | `ModelPricing \| None` | Pricing info |

### ModelDetail (extends ModelInfo)

Additional fields:

| Field | Type | Description |
|---|---|---|
| `name` | `str \| None` | Display name |
| `description` | `str \| None` | Model description |
| `supported_modes` | `List[SupportedMode]` | Available generation modes |
| `limits` | `ModelLimits \| None` | Input constraints |

### SupportedMode

| Field | Type | Description |
|---|---|---|
| `name` | `str` | Mode name |
| `description` | `str \| None` | Mode description |
| `required_fields` | `List[str]` | Required parameters for this mode |
| `optional_fields` | `List[str]` | Optional parameters for this mode |

### ModelLimits

| Field | Type |
|---|---|
| `max_prompt_length` | `int \| None` |
| `max_images` | `int \| None` |
| `max_file_size_mb` | `int \| None` |

### ModelPricing

| Field | Type |
|---|---|
| `unit` | `str` |
| `credits` | `int` |

## SyncPage

| Field | Type | Description |
|---|---|---|
| `items` | `List[T]` | Current page items |
| `has_more` | `bool` | More pages available |
| `next_cursor` | `str \| None` | Cursor for next page |

Iterable: `for model in page.items:`.

## Example

```python
page = pony_flash.models.list(type="video")
for m in page.items:
    print(f"{m.id}: sizes={m.supported_sizes}, durations={m.supported_durations}")

detail = pony_flash.models.get("omnihuman-1.5")
for mode in detail.supported_modes:
    print(f"  {mode.name}: required={mode.required_fields}")
```
