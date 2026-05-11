# Remove Background Module

Remove the background from a product image. This is typically the first step in the Product Avatar workflow — the output `bgRemovedImageFileId` feeds directly into `product_avatar.py --product-image-no-bg`.

## When to Use

- When you need a transparent/background-removed product image before placing it into an avatar scene.
- As step 1 of the Product Avatar V3 flow: **remove background → replace product image**.

## Subcommands

| Subcommand | When to use | Polls? |
|------------|-------------|--------|
| `run` | **Default.** New request, start to finish | Yes — waits until done |
| `submit` | Batch: fire multiple tasks without waiting | No — exits immediately |
| `query` | Recovery: resume polling a known `taskId` | Yes — waits until done |

## Usage

```bash
python {baseDir}/scripts/remove_bg.py <subcommand> [options]
```

## Examples

### `run` — Full Flow (DEFAULT)

```bash
python {baseDir}/scripts/remove_bg.py run --image product.png
```

Download result image:

```bash
python {baseDir}/scripts/remove_bg.py run --image product.png --output product_nobg.png
```

### Product Avatar Workflow (2-step)

```bash
# Step 1: Remove background — note the bgRemovedImageFileId in output
python {baseDir}/scripts/remove_bg.py run --image product.png --json

# Step 2: Use the fileId with product_avatar
python {baseDir}/scripts/product_avatar.py run \
  --product-image-no-bg <bgRemovedImageFileId> \
  --avatar-id <avatarId>
```

### `query` — Recovery

```bash
python {baseDir}/scripts/remove_bg.py query --task-id <taskId> --timeout 600
```

## Options

### `run` and `submit`

| Option | Description |
|--------|-------------|
| `--image` | Product image fileId or local path (required) |
| `--notice-url URL` | Webhook URL for completion notification |

### Polling (`run` and `query`)

| Option | Description |
|--------|-------------|
| `--timeout SECS` | Max polling time in seconds (default: 300) |
| `--interval SECS` | Polling interval in seconds (default: 3) |

### Global

| Option | Description |
|--------|-------------|
| `--output FILE` | Download result image to this local path |
| `--json` | Output full JSON response (not used by default; only when the user explicitly requests raw JSON output) |
| `-q, --quiet` | Suppress status messages on stderr |

## Output Fields

| Field | Description |
|-------|-------------|
| `bgRemovedImageFileId` | FileId of the background-removed image — pass to `product_avatar.py --product-image-no-bg` |
| `bgRemovedImagePath` | URL of the background-removed image |
| `bgRemovedImageWidth/Height` | Dimensions of the result |
| `maskImageFileId` | FileId of the mask image |
| `maskImagePath` | URL of the mask image |
| `costCredit` | Credits consumed |

## Task Statuses

`init` → `running` → `success` or `fail`
