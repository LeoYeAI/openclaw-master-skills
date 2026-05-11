from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

from common import abs_path


SKIP_DIRS = {"__pycache__", ".DS_Store"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Chrome extension ZIP archive.")
    parser.add_argument("--extension-dir", required=True, help="Extension source directory.")
    parser.add_argument("--out", required=True, help="ZIP output path.")
    args = parser.parse_args()

    extension_dir = abs_path(args.extension_dir)
    out_path = abs_path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(extension_dir.rglob("*")):
            if path.name in SKIP_DIRS:
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.is_file():
                archive.write(path, path.relative_to(extension_dir))

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
