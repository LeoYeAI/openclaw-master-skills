#!/usr/bin/env python3
import json
import os
import subprocess
import sys

TOKEN = os.environ.get("GITCODE_API_TOKEN", "")
if not TOKEN:
    sys.exit("GITCODE_API_TOKEN is not set. "
             "Export it before running: export GITCODE_API_TOKEN=<your token>")

comment = sys.argv[1]
pr_url = sys.argv[2]

# 转义 JSON
json_body = json.dumps({"body": comment})

# 构建 curl 命令
cmd = [
    "curl", "-s", "-X", "POST",
    "-H", f"Authorization: Bearer {TOKEN}",
    "-H", "Content-Type: application/json",
    "-d", json_body,
    pr_url
]

result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)
