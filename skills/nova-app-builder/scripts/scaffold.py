#!/usr/bin/env python3
# scaffold.py — Nova app project generator

import argparse
import shutil
import sys
import textwrap
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = SKILL_DIR / "assets" / "app-template"


def scaffold(name: str, desc: str, port: int, out: Path) -> Path:
    dest = out / name
    if dest.exists():
        print(f"[warn] Directory already exists: {dest} — files will be overwritten")

    shutil.copytree(str(TEMPLATE_DIR), str(dest), dirs_exist_ok=True)

    # Rename Dockerfile.txt -> Dockerfile and replace port placeholder
    dockerfile_template = dest / "Dockerfile.txt"
    dockerfile = dest / "Dockerfile"
    text = dockerfile_template.read_text()
    text = text.replace("{{APP_PORT}}", str(port))
    dockerfile.write_text(text)
    dockerfile_template.unlink()

    # Patch enclave/main.py placeholders
    main_py = dest / "enclave" / "main.py"
    text = main_py.read_text()
    text = text.replace("{{APP_NAME}}", name)
    text = text.replace("{{APP_DESC}}", desc)
    text = text.replace("{{APP_PORT}}", str(port))
    main_py.write_text(text)

    print(f"\n[OK] Scaffolded Nova app -> {dest}\n")
    for f in sorted(dest.rglob("*")):
        if f.is_file():
            print(f"  {f.relative_to(dest)}")

    print(textwrap.dedent(f"""
    Next steps:
      1. Edit  {dest}/enclave/main.py          <- app logic
      2. Edit  {dest}/enclave/requirements.txt <- pip packages
      3. Test locally:
           cd {dest}/enclave
           IN_ENCLAVE=false uvicorn main:app --host 0.0.0.0 --port {port} --reload
      4. Push to a Git repo
      5. Deploy:
           python3 scripts/nova_deploy.py \\
             --repo https://github.com/you/{name} \\
             --name "{name}" \\
             --port {port} \\
             --api-key YOUR_NOVA_API_KEY
    """))
    return dest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True)
    p.add_argument("--desc", default="A Nova Platform app")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--out", default=".")
    args = p.parse_args()

    name = args.name.lower().replace(" ", "-")
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    if not TEMPLATE_DIR.exists():
        print(f"[error] Template not found: {TEMPLATE_DIR}", file=sys.stderr)
        sys.exit(1)

    scaffold(name, args.desc, args.port, out)


if __name__ == "__main__":
    main()
