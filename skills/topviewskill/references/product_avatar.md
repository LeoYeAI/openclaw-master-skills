# Product Avatar Module

Replace product images in digital human (avatar) scenes — put your product into a model's hands automatically.

## When to Use

When you need to place a product into a digital human / model scene — e.g., making a model hold, wear, or display a product.

## Subcommands

| Subcommand | When to use | Polls? |
|------------|-------------|--------|
| `run` | **Default.** New request, start to finish | Yes — waits until done |
| `submit` | Batch: fire multiple tasks without waiting | No — exits immediately |
| `query` | Recovery: resume polling a known `taskId` | Yes — waits until done |
| `list-categories` | List avatar categories (for filtering `list-avatars`) | No |
| `list-avatars` | Browse public avatar templates | No |

## Usage

```bash
python {baseDir}/scripts/product_avatar.py <subcommand> [options]
```

## Full Workflow (Remove Background → Replace)

The recommended Product Avatar V3 flow:

```
Step 1: productImage → remove_bg.py → bgRemovedImageFileId
Step 2: bgRemovedImageFileId + avatarId → product_avatar.py → resultImage
```

```bash
# Step 1 — Remove product background
python {baseDir}/scripts/remove_bg.py run --image product.png --json
# Note the bgRemovedImageFileId from output

# Step 2 — Browse available avatars and pick one
python {baseDir}/scripts/product_avatar.py list-avatars --gender female

# Step 3 — Replace product into avatar scene
python {baseDir}/scripts/product_avatar.py run \
  --product-image-no-bg <bgRemovedImageFileId> \
  --avatar-id <avatarId>
```

If you already have a background-removed product image or a custom template image, you can skip step 1 and go directly to step 2/3.

## Browsing Templates

### List Categories

```bash
python {baseDir}/scripts/product_avatar.py list-categories
```

### Browse Avatars

```bash
# All avatars
python {baseDir}/scripts/product_avatar.py list-avatars

# Filter by gender
python {baseDir}/scripts/product_avatar.py list-avatars --gender female

# Filter by category
python {baseDir}/scripts/product_avatar.py list-avatars --category-ids <id1>,<id2>

# Sort by newest
python {baseDir}/scripts/product_avatar.py list-avatars --sort Newest
```

### `list-avatars` Options

| Option | Description |
|--------|-------------|
| `--gender` | `male` or `female` |
| `--category-ids` | Category IDs, comma-separated (from `list-categories`) |
| `--ethnicity-ids` | Ethnicity IDs, comma-separated |
| `--sort` | `Popularity` (default) or `Newest` |
| `--page` | Page number (default: 1) |
| `--size` | Items per page (default: 20) |

## Examples

### Auto Mode (Model-Priority)

```bash
python {baseDir}/scripts/product_avatar.py run \
  --product-image product.png \
  --template-image template.png \
  --mode auto \
  --keep-target model
```

### Auto Mode (Product-Priority)

```bash
python {baseDir}/scripts/product_avatar.py run \
  --product-image product.png \
  --template-image template.png \
  --mode auto \
  --keep-target product
```

### Manual Mode with V4 (banana_pro)

```bash
python {baseDir}/scripts/product_avatar.py run \
  --product-image product.png \
  --template-image template.png \
  --mode manual \
  --version v4 \
  --location '[[10.5, 20.0], [30.5, 40.0]]'
```

### With Background-Removed Product (from remove_bg.py)

```bash
python {baseDir}/scripts/product_avatar.py run \
  --product-image-no-bg <bgRemovedImageFileId> \
  --avatar-id <avatarId>
```

### With Public Avatar (from list-avatars)

```bash
python {baseDir}/scripts/product_avatar.py run \
  --product-image product.png \
  --avatar-id <avatarId>
```

## Options

### `run` and `submit`

| Option | Description |
|--------|-------------|
| `--product-image` | Product image fileId or local path |
| `--product-image-no-bg` | Product image (background removed) fileId or local path |
| `--template-image` | Template/model image fileId or local path |
| `--avatar-id` | Avatar ID (public or private digital human) |
| `--face-image` | User face image fileId or local path |
| `--prompt` | Image edit prompt text |
| `--mode` | `auto` (automatic) or `manual` (coordinate-based) |
| `--keep-target` | `model` (default) or `product`; only for auto mode |
| `--version` | `v3` (default) or `v4` (banana_pro, supports manual) |
| `--location` | Product coordinates as JSON 2D array |
| `--product-size` | Product size (enum value) |
| `--project-id` | Project ID |
| `--board-id` | Board ID |
| `--notice-url` | Webhook URL |

### Polling / Global

| Option | Description |
|--------|-------------|
| `--timeout SECS` | Max polling time (default: 600) |
| `--interval SECS` | Polling interval (default: 5) |
| `--output FILE` | Download result to local path |
| `--json` | Full JSON response |
| `-q, --quiet` | Suppress status messages |

## Mode Comparison

| Mode | Version | Description |
|------|---------|-------------|
| `auto` + `model` | v3/v4 | Automatic placement, preserves model pose (default) |
| `auto` + `product` | v3/v4 | Automatic placement, preserves product appearance |
| `manual` | v4 only | Manual coordinate-based placement (banana_pro) |

## Cost

Fixed: **0.5 credits** per task. Failed tasks are refunded.
