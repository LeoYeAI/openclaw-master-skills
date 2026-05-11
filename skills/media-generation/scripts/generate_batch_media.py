#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def parse_args():
    p = argparse.ArgumentParser(description="Run a batch media manifest through the media-generation helpers.")
    p.add_argument("--manifest", required=True, help="Path to a JSON or JSONL manifest")
    p.add_argument("--vars-json", help="Shared JSON object used for string templating")
    p.add_argument("--vars-file", help="Path to a shared JSON object used for string templating")
    p.add_argument("--summary-out", help="Optional JSON file to write the full batch summary")
    p.add_argument("--continue-on-error", action="store_true", help="Continue processing later items after a failure")
    p.add_argument("--dry-run", action="store_true", help="Print the resolved commands without executing them")
    p.add_argument("--print-json", action="store_true", help="Print structured JSON output")
    return p.parse_args()


def load_json_object(text, label):
    obj = json.loads(text)
    if not isinstance(obj, dict):
        raise SystemExit(f"{label} must decode to a JSON object")
    return obj


def load_manifest(path: Path):
    text = path.read_text(encoding="utf-8")
    stripped = text.strip()
    if not stripped:
        return []
    if stripped.startswith("["):
        items = json.loads(stripped)
        if not isinstance(items, list):
            raise SystemExit("JSON manifest must be an array")
        return items
    items = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as e:
            raise SystemExit(f"invalid JSONL at line {idx}: {e}")
        items.append(item)
    return items


def load_shared_vars(args):
    shared = {}
    if args.vars_json:
        shared.update(load_json_object(args.vars_json, "--vars-json"))
    if args.vars_file:
        shared.update(load_json_object(Path(args.vars_file).read_text(encoding="utf-8"), "--vars-file"))
    return shared


def render_value(value, vars_map):
    if isinstance(value, str):
        return value.format_map(SafeDict(vars_map))
    if isinstance(value, list):
        return [render_value(v, vars_map) for v in value]
    if isinstance(value, dict):
        return {k: render_value(v, vars_map) for k, v in value.items() if k != "vars"}
    return value


def render_item(item, shared_vars, index):
    local_vars = item.get("vars") or {}
    if local_vars and not isinstance(local_vars, dict):
        raise SystemExit("manifest item field 'vars' must be an object when present")
    vars_map = dict(shared_vars)
    vars_map.update(local_vars)
    vars_map.setdefault("index", index)
    vars_map.setdefault("mode", item.get("mode", "image"))
    rendered = render_value(item, vars_map)
    rendered["vars"] = vars_map
    return rendered


def choose_script(item):
    mode = item.get("mode", "image")
    if item.get("consistent") or item.get("reference_image") or item.get("reference_images"):
        return SCRIPT_DIR / "generate_consistent_media.py"
    if mode == "video":
        return SCRIPT_DIR / "generate_video.py"
    if mode == "image":
        return SCRIPT_DIR / "generate_image.py"
    raise SystemExit(f"unsupported mode in manifest item: {mode}")


def add_repeatable(cmd, flag, value):
    if value is None:
        return
    if isinstance(value, list):
        for item in value:
            cmd.extend([flag, str(item)])
    else:
        cmd.extend([flag, str(value)])


def item_to_command(item):
    script = choose_script(item)
    prompt = item.get("prompt")
    if not prompt:
        raise SystemExit("manifest item missing required field: prompt")

    cmd = [sys.executable, str(script), "--prompt", str(prompt)]

    if script.name == "generate_consistent_media.py":
        cmd.extend(["--mode", str(item.get("mode", "image"))])
        add_repeatable(cmd, "--reference-image", item.get("reference_images") or item.get("reference_image"))
        if item.get("reference_key"):
            cmd.extend(["--reference-key", str(item["reference_key"])])
        if item.get("transport"):
            cmd.extend(["--transport", str(item["transport"])])

    simple_flags = [
        "provider", "model", "endpoint", "out_dir", "prefix", "size", "quality", "style", "background",
        "n", "seed", "duration", "seconds", "fps", "config", "status_endpoint_template", "image",
        "extra_json", "extra_json_file", "timeout", "poll_interval", "max_polls",
    ]
    for key in simple_flags:
        if key in item and item[key] is not None:
            cmd.extend(["--" + key.replace("_", "-"), str(item[key])])

    if item.get("download") is False:
        cmd.append("--no-download")
    if item.get("print_json"):
        cmd.append("--print-json")
    return cmd


def maybe_write_summary(path, summary):
    if not path:
        return
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    args = parse_args()
    items = load_manifest(Path(args.manifest))
    shared_vars = load_shared_vars(args)
    results = []
    overall_ok = True

    for index, raw_item in enumerate(items, start=1):
        item = render_item(raw_item, shared_vars, index)
        cmd = item_to_command(item)
        record = {"index": index, "item": item, "cmd": cmd, "ok": None, "stdout": None, "stderr": None}
        if args.dry_run:
            record["ok"] = True
            results.append(record)
            continue
        proc = subprocess.run(cmd, text=True, capture_output=True)
        record["ok"] = proc.returncode == 0
        record["stdout"] = proc.stdout.strip()
        record["stderr"] = proc.stderr.strip()
        results.append(record)
        if proc.returncode != 0:
            overall_ok = False
            if not args.continue_on_error:
                break

    summary = {
        "ok": overall_ok,
        "count": len(items),
        "manifest": args.manifest,
        "summary_out": args.summary_out,
        "results": results,
    }
    maybe_write_summary(args.summary_out, summary)
    if args.print_json or args.dry_run:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        for item in results:
            print(json.dumps(item, ensure_ascii=False))
    if not overall_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
