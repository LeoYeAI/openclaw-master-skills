# Files API Reference

## Methods

### `pony_flash.files.upload(file: FileInput) -> str`

Upload a file via presigned URL. Returns `file_id`.

Most users don't need to call this directly — `generate()` auto-uploads `FileInput` values.

### `pony_flash.files.presign(*, filename, content_type, size) -> PresignResponse`

Get a presigned upload URL. Low-level; prefer `upload()`.

### `pony_flash.files.resolve(inp: FileInput) -> dict`

Resolve a `FileInput` to API JSON (`{"type": "url", "url": ...}` or `{"type": "file_id", "file_id": ...}`). Auto-uploads if needed.

### `pony_flash.files.resolve_many(inputs: Sequence[FileInput]) -> list[dict]`

Resolve multiple `FileInput` values.

### `pony_flash.files.get(file_id: str) -> FileObject`

Get file metadata.

### `pony_flash.files.list() -> list[FileObject]`

List all uploaded files.

### `pony_flash.files.delete(file_id: str) -> None`

Delete a file.

### `pony_flash.files.cleanup(file_ids: Sequence[str]) -> None`

Best-effort delete of temporary files. Errors are logged, never raised.

## Return types

### PresignResponse

| Field | Type | Description |
|---|---|---|
| `file_id` | `str` | Assigned file ID |
| `upload_url` | `str` | Presigned PUT URL |
| `expires_at` | `str` | Expiration timestamp |
| `method` | `str` | HTTP method (default `"PUT"`) |
| `headers` | `Dict[str, str]` | Headers to include in upload |

### FileObject

| Field | Type | Description |
|---|---|---|
| `file_id` | `str` | File identifier |
| `filename` | `str` | Original filename |
| `content_type` | `str` | MIME type |
| `size` | `int` | File size in bytes |
| `status` | `str` | Upload status |
| `created_at` | `str` | Creation timestamp |
| `expires_at` | `str \| None` | Expiration timestamp |

## Example

```python
file_id = pony_flash.files.upload(open("photo.jpg", "rb"))
print(f"Uploaded: {file_id}")

files = pony_flash.files.list()
for f in files:
    print(f"{f.file_id}: {f.filename} ({f.size} bytes)")

pony_flash.files.delete(file_id)
```
