#!/usr/bin/env python3
import json
import sys
import subprocess

comment = sys.argv[1]
pr_url = sys.argv[2]

# 转义 JSON
json_body = json.dumps({"body": comment})

# 构建 curl 命令
cmd = [
    "curl", "-s", "-X", "POST",
    "-H", "Authorization: Bearer 5_EtXLq3jGyQvb6tWwrN3byz",
    "-H", "Content-Type: application/json",
    "-d", json_body,
    pr_url
]

result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)
