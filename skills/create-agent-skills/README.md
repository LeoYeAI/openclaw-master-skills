# Skill Designer Agent Skills

A comprehensive skill for creating effective [Agent Skills](https://agentskills.io/) - includes validation, initialization, and packaging tools that comply with the official Agent Skills specification.

## Features

- **`init_skill.py`**: Initialize new skills from a template with proper structure
- **`quick_validate.py`**: Validate skills against the official Agent Skills specification
- **`package_skill.py`**: Package skills into distributable `.skill` files

## Quick Start

### Creating a New Skill

```bash
python scripts/init_skill.py my-new-skill --path ./skills
```

### Validating a Skill

```bash
python scripts/quick_validate.py path/to/skill-folder
```

### Packaging a Skill

```bash
python scripts/package_skill.py path/to/skill-folder
```

## Requirements

- Python 3.11+
- PyYAML (`pip install pyyaml`)

## Creating Releases

This repository uses GitHub Actions to automatically create releases when you push a version tag.

### Automatic Release on Tag Push

1. Create and push a version tag:
   ```bash
   git tag -a v1.0.0 -m "Initial release"
   git push origin v1.0.0
   ```

2. GitHub Actions will automatically:
   - Validate the skill
   - Package it into a `.skill` file
   - Create a GitHub release with the packaged file attached

### Manual Release

You can also trigger a release manually from the GitHub Actions tab:
1. Go to **Actions** → **Create Release**
2. Click **Run workflow**
3. The workflow will create a release with a timestamp-based version

## License

Apache License 2.0 - See [LICENSE.txt](LICENSE.txt) for details.
