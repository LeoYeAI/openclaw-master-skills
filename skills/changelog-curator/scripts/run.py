#!/usr/bin/env python3
import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parents[1]
SPEC_PATH = BASE_DIR / "resources" / "spec.json"
TEMPLATE_PATH = BASE_DIR / "resources" / "template.md"

def fail(message: str, code: int = 2) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return code

def load_spec() -> dict:
    try:
        return json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(fail(f"Missing spec file: {SPEC_PATH}"))
    except json.JSONDecodeError as exc:
        raise SystemExit(fail(f"Invalid JSON in {SPEC_PATH}: {exc}"))

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")

def list_text_files(root: Path, limit: int = 50):
    results = []
    for path in root.rglob("*"):
        if len(results) >= limit:
            break
        if path.is_file():
            if path.suffix.lower() in {".md",".txt",".json",".yaml",".yml",".py",".js",".ts",".csv",".tsv",".sh"}:
                results.append(path)
    return results

def make_structured_report(spec: dict, input_text: str) -> str:
    title = spec["title"]
    summary = spec["summary"]
    sections = spec["sections"]
    bullets = [line.strip("- ").strip() for line in input_text.splitlines() if line.strip()]
    bullets = bullets[:18]
    out = [f"# {title} 结果", "", f"> 模式：{spec['mode']}", f"> 摘要：{summary}", ""]
    for idx, section in enumerate(sections):
        out.append(f"## {section}")
        if bullets:
            selected = bullets[idx::max(1, len(sections))][:3]
            for item in selected:
                out.append(f"- {item}")
        else:
            out.append("- 输入材料不足，请补充更具体的原始信息。")
        out.append("")
    out.append("## 待确认项")
    out.append(f"- 请补充：{spec.get('inputHint', '更完整的输入材料')}")
    out.append("")
    out.append("## 下一步")
    out.append("- 先审阅上述结构，再决定是否进入执行、发送、发布或系统变更。")
    return "\n".join(out).strip() + "\n"

def directory_report(spec: dict, root: Path, limit: int) -> str:
    files = list_text_files(root, limit=limit)
    ext_counter = Counter(p.suffix.lower() or "<none>" for p in files)
    headings = []
    for p in files[: min(10, len(files))]:
        if p.suffix.lower() == ".md":
            text = read_text(p)
            for line in text.splitlines():
                if line.startswith("#"):
                    headings.append((p.name, line.strip()))
                    if len(headings) >= 12:
                        break
        if len(headings) >= 12:
            break
    out = [f"# {spec['title']} 扫描报告", "", f"扫描目录：`{root}`", f"文本文件样本数：{len(files)}", ""]
    out.append("## 目录概览")
    for p in files[:15]:
        out.append(f"- {p.relative_to(root)}")
    out.append("")
    out.append("## 扩展名分布")
    for ext, cnt in ext_counter.most_common():
        out.append(f"- {ext}: {cnt}")
    out.append("")
    out.append("## 标题样本")
    if headings:
        for fname, heading in headings:
            out.append(f"- {fname}: {heading}")
    else:
        out.append("- 未发现 Markdown 标题。")
    out.append("")
    for section in spec["sections"]:
        out.append(f"## {section}")
        out.append(f"- 基于目录和文件样本，围绕“{section}”给出人工审阅意见。")
        out.append("")
    return "\n".join(out).strip() + "\n"

def csv_report(spec: dict, path: Path, limit: int) -> str:
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    rows = []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        for idx, row in enumerate(reader):
            rows.append(row)
            if idx + 1 >= limit:
                break
    if not rows:
        return make_structured_report(spec, "未读取到数据行。")
    fieldnames = list(rows[0].keys())
    out = [f"# {spec['title']} 数据报告", "", f"文件：`{path}`", f"采样行数：{len(rows)}", ""]
    out.append("## 字段概览")
    for field in fieldnames:
        values = [r.get(field, "") for r in rows]
        non_empty = [v for v in values if str(v).strip()]
        unique = len(set(non_empty))
        out.append(f"- {field}: 非空 {len(non_empty)}/{len(rows)}，唯一值约 {unique}")
    out.append("")
    for section in spec["sections"]:
        out.append(f"## {section}")
        out.append(f"- 结合字段概览与样本，围绕“{section}”补充判断。")
        out.append("")
    return "\n".join(out).strip() + "\n"

PATTERNS = {
    "curl_pipe_bash": r"curl\s+[^|]+\|\s*(bash|sh)",
    "dangerous_rm": r"\brm\s+-rf\s+(/|\*|~|\.{1,2})",
    "base64_exec": r"base64\s+(-d|--decode).+\|\s*(bash|sh|python)",
    "secret_like": r"(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{8,}",
    "private_url": r"https?://[^/\s]+/(admin|internal|private|secret)",
}

def pattern_report(spec: dict, path: Path, limit: int) -> str:
    targets = [path] if path.is_file() else list_text_files(path, limit=limit)
    findings = []
    for target in targets:
        text = read_text(target)
        for name, pattern in PATTERNS.items():
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                snippet = match.group(0)
                if "secret_like" == name:
                    snippet = re.sub(r"([A-Za-z0-9_\-]{4})[A-Za-z0-9_\-]+", r"\1***", snippet)
                findings.append((str(target), name, snippet[:160]))
                if len(findings) >= limit:
                    break
            if len(findings) >= limit:
                break
        if len(findings) >= limit:
            break
    out = [f"# {spec['title']} 模式扫描", "", f"扫描目标：`{path}`", ""]
    out.append("## 发现结果")
    if findings:
        for target, name, snippet in findings:
            out.append(f"- [{name}] {target}: `{snippet}`")
    else:
        out.append("- 未命中内置高风险模式。")
    out.append("")
    for section in spec["sections"]:
        out.append(f"## {section}")
        out.append(f"- 围绕“{section}”给出人工复核和修复建议。")
        out.append("")
    return "\n".join(out).strip() + "\n"

def parse_frontmatter(path: Path):
    text = read_text(path)
    if not text.startswith("---\n"):
        return None, "SKILL.md 缺少前置 frontmatter"
    parts = text.split("\n---\n", 1)
    if len(parts) < 2:
        return None, "frontmatter 未正确闭合"
    front = parts[0].splitlines()[1:]
    data = {}
    for line in front:
        if not line.strip() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data, None

def skill_audit(spec: dict, path: Path, limit: int) -> str:
    required = [
        "SKILL.md",
        "README.md",
        "SELF_CHECK.md",
        "scripts/run.py",
        "resources/spec.json",
        "resources/template.md",
        "examples/example-input.md",
        "tests/smoke-test.md",
    ]
    out = [f"# {spec['title']} 规范检查", "", f"检查目标：`{path}`", ""]
    out.append("## 文件完整性")
    for rel in required:
        target = path / rel
        out.append(f"- {rel}: {'OK' if target.exists() else 'MISSING'}")
    out.append("")
    skill_md = path / "SKILL.md"
    if skill_md.exists():
        data, err = parse_frontmatter(skill_md)
        out.append("## Frontmatter")
        if err:
            out.append(f"- 错误：{err}")
        else:
            for key in ("name","description","version","metadata"):
                out.append(f"- {key}: {'OK' if key in data else 'MISSING'}")
            metadata_value = data.get("metadata", "")
            if metadata_value:
                try:
                    json.loads(metadata_value)
                    out.append("- metadata JSON: OK")
                except Exception as exc:
                    out.append(f"- metadata JSON: INVALID ({exc})")
    out.append("")
    for section in spec["sections"]:
        out.append(f"## {section}")
        out.append(f"- 围绕“{section}”给出修复建议或复检动作。")
        out.append("")
    return "\n".join(out).strip() + "\n"

def build_report(spec: dict, source: Path, limit: int) -> str:
    mode = spec["mode"]
    if mode == "structured_brief":
        text = read_text(source) if source.exists() and source.is_file() else str(source)
        return make_structured_report(spec, text)
    if mode == "directory_audit":
        if not source.exists() or not source.is_dir():
            return make_structured_report(spec, f"目录不存在：{source}")
        return directory_report(spec, source, limit)
    if mode == "csv_audit":
        if not source.exists() or not source.is_file():
            return make_structured_report(spec, f"文件不存在：{source}")
        return csv_report(spec, source, limit)
    if mode == "pattern_audit":
        if not source.exists():
            return make_structured_report(spec, f"目标不存在：{source}")
        return pattern_report(spec, source, limit)
    if mode == "skill_audit":
        if not source.exists() or not source.is_dir():
            return make_structured_report(spec, f"Skill 目录不存在：{source}")
        return skill_audit(spec, source, limit)
    return make_structured_report(spec, f"未知模式：{mode}")

def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local support script for this Skill.")
    parser.add_argument("--input", required=True, help="Input file, directory, or inline string.")
    parser.add_argument("--output", help="Write output to a file instead of stdout.")
    parser.add_argument("--format", choices=["markdown","json"], default="markdown", help="Output format.")
    parser.add_argument("--limit", type=int, default=50, help="Limit sample size or findings.")
    parser.add_argument("--dry-run", action="store_true", help="Analyze only and skip file writing.")
    args = parser.parse_args()

    spec = load_spec()
    source = Path(args.input).expanduser()

    if source.exists():
        report = build_report(spec, source, args.limit)
    else:
        if spec["mode"] in {"directory_audit","csv_audit","pattern_audit","skill_audit"}:
            return fail(f"Input path does not exist: {source}")
        report = build_report(spec, Path(args.input), args.limit)

    if args.format == "json":
        payload = {"skill": spec["slug"], "mode": spec["mode"], "report": report}
        rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    else:
        rendered = report

    if args.dry_run or not args.output:
        print(rendered)
        return 0

    output_path = Path(args.output).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    print(f"Wrote output to {output_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
