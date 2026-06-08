from pathlib import Path


def test_gitignore_covers_skillup_artifacts():
    repo_root = Path(__file__).resolve().parents[1]
    gitignore_text = (repo_root / '.gitignore').read_text(encoding='utf-8')

    for token in [
        '.skillup-artifacts/',
        '.skillup-check.json',
        '.skillup-*-current.json',
        '.skillup-dryrun.json',
        '.skillup-publish.json',
        '.skillup-*-sync.json',
        '.skillup.local.toml',
        '.DS_Store',
    ]:
        assert token in gitignore_text
