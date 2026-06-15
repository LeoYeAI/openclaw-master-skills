# HuggingFace Cache Monitoring

Pattern for tracking model download progress and cache size in workflows that use HuggingFace models.

## The Problem

HuggingFace caches model files in a specific directory structure:
```
~/.cache/huggingface/hub/
└── models--org--model-name/
    ├── blobs/          # Actual model files (large)
    ├── snapshots/      # Symlinks to blobs (organized by commit hash)
    └── refs/           # Branch pointers
```

A common mistake is scanning only `blobs/` and missing the `snapshots/` directory, or double-counting by not skipping symlinks.

## Correct Pattern

```python
@app.get("/download_progress")
async def download_progress(model_name: str = ""):
    """Check download progress by polling HuggingFace cache."""
    # Get cache location (respects HF_HOME, TRANSFORMERS_CACHE env vars)
    try:
        from huggingface_hub.constants import HF_HUB_CACHE
        cache_base = str(HF_HUB_CACHE)
    except Exception:
        cache_base = os.path.expanduser("~/.cache/huggingface/hub")
    
    if model_name:
        safe_name = model_name.replace("/", "--")
        model_dir = os.path.join(cache_base, f"models--{safe_name}")
        # ⚠️ Scan BOTH blobs and snapshots directories
        scan_dirs = [
            os.path.join(model_dir, "blobs"),
            os.path.join(model_dir, "snapshots"),
        ]
    else:
        model_dir = cache_base
        scan_dirs = [cache_base]
    
    result = {
        "downloading": False,
        "total_size": 0,
        "incomplete_count": 0,
        "model_name": model_name,
        "cache_path": model_dir,
        "cache_exists": os.path.exists(model_dir),  # Useful for debugging
    }
    
    for scan_dir in scan_dirs:
        if not os.path.exists(scan_dir):
            continue
        for root, dirs, files in os.walk(scan_dir):
            for f in files:
                try:
                    fpath = os.path.join(root, f)
                    # ⚠️ Skip symlinks to avoid double-counting!
                    # snapshots/ contains symlinks to blobs/
                    if os.path.islink(fpath):
                        continue
                    size = os.path.getsize(fpath)
                    result["total_size"] += size
                    # .incomplete files indicate active download
                    if f.endswith('.incomplete'):
                        result["downloading"] = True
                        result["incomplete_count"] += 1
                except OSError:
                    pass
    
    result["total_mb"] = round(result["total_size"] / 1024 / 1024, 1)
    return result
```

## Key Points

1. **Scan both `blobs/` and `snapshots/`** — Models may be accessed via either path
2. **Skip symlinks** — `snapshots/` contains symlinks to `blobs/`, counting both would double the size
3. **Check for `.incomplete` files** — HuggingFace creates these during active downloads
4. **Respect HF environment vars** — Use `HF_HUB_CACHE` if available, fallback to default
5. **Include `cache_exists` flag** — Helps debug when cache path doesn't exist

## Frontend Polling

```tsx
// Poll every 5 seconds while monitoring is enabled
useEffect(() => {
  if (!connected || !monitorDownloads) {
    if (!monitorDownloads) setDownloadProgress(null);
    return;
  }
  
  const pollDownload = async () => {
    try {
      const res = await fetch(`${serverUrl}/download_progress?model_name=${encodeURIComponent(selectedModel)}`);
      if (res.ok) {
        const data = await res.json();
        setDownloadProgress({
          total_mb: data.total_mb,
          downloading: data.downloading,
          cache_path: data.cache_path,
        });
      }
    } catch {}
  };
  
  pollDownload();  // Initial check
  const interval = setInterval(pollDownload, 5000);
  return () => clearInterval(interval);
}, [connected, serverUrl, selectedModel, monitorDownloads]);
```

## Workflows Using This Pattern

- `RAG` — Embed and generation models
- `MusicGen` — Audio generation models
- `LocalChat` — LLM models
- `STT` — Speech-to-text models
- `VoiceAgent` — Router and voice models
- `SDXLGenerator` — Image generation models
- `ImageToText` — Vision models

All follow the same pattern with workflow-specific variations (different model name formats, additional state like `is_loading`).
