#!/usr/bin/env python3
"""将 TSA 打包为多个不同 slug/name 的 zip 压缩包"""
import json, os, re, shutil, tempfile, zipfile

os.chdir(os.path.dirname(os.path.abspath(__file__)))

TARGETS = [
    ("cloudq-aiops", "AIOps CloudQ"),
    ("cloudq-sre", "CloudQ SRE"),
    ("tencent-cloudq", "Tencent CloudQ"),
]

EXCLUDES = {
    "tests", "__pycache__", ".git", ".DS_Store",
    "publish.sh", "batch_publish.sh", "batch_publish.py",
    "CONTRIBUTING.md", "name_candidates.txt", ".workbuddy",
    "publish_log.json", "publish_log.json.example",
    "publish_output.log", "start_publish.sh",
    "clear_publish_log.py", "view_publish_log.py",
    "PUBLISH_GUIDE.md", "QUICK_START.md", "CODEBUDDY.md",
    "make_zips.py",
}

output_dir = os.path.dirname(os.path.abspath(__file__))  # 输出到 tsa 同级的 Downloads

for slug, name in TARGETS:
    tmp_dir = tempfile.mkdtemp(prefix=f"tsa_{slug}_")

    # 复制文件
    for item in os.listdir("."):
        if item in EXCLUDES or item.endswith((".pyc", ".pyo")):
            continue
        src = os.path.join(".", item)
        dst = os.path.join(tmp_dir, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", "*.pyo", ".DS_Store"))
        else:
            shutil.copy2(src, dst)

    # 修改 _meta.json 中的 slug
    meta_path = os.path.join(tmp_dir, "_meta.json")
    with open(meta_path, "r") as f:
        meta = json.load(f)
    meta["slug"] = slug
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    # 修改 SKILL.md 中的 name
    skill_path = os.path.join(tmp_dir, "SKILL.md")
    with open(skill_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(
        r"^name:\s*.*$", f"name: {slug}",
        content, count=1, flags=re.MULTILINE
    )
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(content)

    # 打成 zip
    zip_path = os.path.join(output_dir, f"{slug}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(tmp_dir):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for fn in files:
                if fn.endswith((".pyc", ".pyo")) or fn == ".DS_Store":
                    continue
                fp = os.path.join(root, fn)
                zf.write(fp, os.path.relpath(fp, tmp_dir))

    shutil.rmtree(tmp_dir, ignore_errors=True)
    print(f"✔ {zip_path}  (slug={slug}, name={name})")

print("\n✅ 全部完成！")
