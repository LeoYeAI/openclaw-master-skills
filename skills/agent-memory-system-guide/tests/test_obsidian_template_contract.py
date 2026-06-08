from pathlib import Path


def test_obsidian_template_exists():
    repo_root = Path(__file__).resolve().parents[1]
    assert (repo_root / 'templates' / 'OBSIDIAN-NOTE.md').exists()
