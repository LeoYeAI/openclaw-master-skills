#!/bin/bash
# archive.sh - 将 cloudq skill 相关文件打包为 cloudq.zip
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

OUTPUT="cloudq.zip"

# 删除旧的压缩包
rm -f "$OUTPUT"

# 使用 git ls-files 获取被跟踪的文件（排除 .gitignore 中的内容）
# 若文件尚未提交，则回退到 find 方式
if git rev-parse --is-inside-work-tree >/dev/null 2>&1 && git log --oneline -1 >/dev/null 2>&1; then
    git archive --format=zip --output="$OUTPUT" HEAD
else
    # 回退：用 find 排除缓存和输出目录
    find . \
        -path './.git' -prune -o \
        -path './__pycache__' -prune -o \
        -path './scripts/__pycache__' -prune -o \
        -path './references/plugins/tsa-risk/scripts/__pycache__' -prune -o \
        -path './references/plugins/tsa-risk/output' -prune -o \
        -path './tests' -prune -o \
        -path './output' -prune -o \
        -name '*.pyc' -prune -o \
        -name '*.pyo' -prune -o \
        -name '.DS_Store' -prune -o \
        -name '*.zip' -prune -o \
        -name '*.tar.gz' -prune -o \
        -name '*.log' -prune -o \
        -name 'archive.sh' -prune -o \
        -type f -print \
    | zip "$OUTPUT" -@
fi

echo "已打包: $OUTPUT ($(du -h "$OUTPUT" | cut -f1))"
