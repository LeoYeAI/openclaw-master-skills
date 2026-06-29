# Recipes Guide

Browse and use Medeo's pre-built video recipes (templates).

## List Available Recipes

```bash
python3 {baseDir}/scripts/medeo_video.py recipes
```

Returns a list of recipe objects with:
- `recipe_id` — use with `--recipe-id` in generation
- `name` — human-readable name
- `description` — what the recipe produces
- `thumbnail_url` — preview image

## Paginate Through Recipes

```bash
python3 {baseDir}/scripts/medeo_video.py recipes --cursor <cursor_value>
```

The `cursor` value comes from the previous response. Keep calling with the new cursor until no more results.

## Use a Recipe in Video Generation

```bash
python3 {baseDir}/scripts/medeo_video.py spawn-task \
  --message "your video description" \
  --recipe-id "recipe_01..."
```

The recipe provides a pre-built style/structure. Your `--message` customizes the content within that structure.
