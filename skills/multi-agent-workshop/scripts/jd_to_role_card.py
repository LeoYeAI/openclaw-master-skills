#!/usr/bin/env python3
"""
从招聘平台 JD 生成角色卡草稿

用法：
    # 搜索并生成角色卡草稿
    python3 jd_to_role_card.py --role "内容运营" --industry "短视频"

    # 指定任务绑定
    python3 jd_to_role_card.py --role "合规法务" --industry "互联网" --task "评审用户协议改版方案"

    # 输出到文件
    python3 jd_to_role_card.py --role "数据分析师" --industry "电商" -o workshops/2026-03-26_demo/roles_data_analyst.md

依赖：仅标准库 + SERPER_API_KEY（从 ~/.openclaw/.env 读取）
"""

import argparse
import json
import os
import ssl
import sys
import urllib.request
from pathlib import Path


def load_env():
    env_file = Path.home() / ".openclaw" / ".env"
    if not env_file.exists():
        return
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if key and key not in os.environ:
                os.environ[key] = value


def search_jd(role: str, industry: str = "", platforms: str = "") -> dict:
    """通过 Serper API 搜索招聘 JD"""
    api_key = os.environ.get("SERPER_API_KEY")
    if not api_key:
        print("❌ 未找到 SERPER_API_KEY，请检查 ~/.openclaw/.env")
        sys.exit(1)

    platform_hint = platforms or "BOSS直聘 OR 猎聘 OR 拉勾"
    query = f'"{role}" {industry} 岗位职责 任职要求 ({platform_hint})'

    data = json.dumps({"q": query, "num": 8, "gl": "cn", "hl": "zh-cn"}).encode()
    req = urllib.request.Request(
        "https://google.serper.dev/search",
        data=data,
        headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        method="POST",
    )

    try:
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl._create_unverified_context()

    with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
        return json.loads(resp.read().decode())


def extract_snippets(results: dict) -> list[str]:
    """从搜索结果中提取摘要片段"""
    snippets = []
    for item in results.get("organic", []):
        snippet = item.get("snippet", "")
        if snippet and any(kw in snippet for kw in ["职责", "要求", "负责", "熟悉", "经验"]):
            snippets.append(snippet)
    if results.get("knowledgeGraph", {}).get("description"):
        snippets.insert(0, results["knowledgeGraph"]["description"])
    return snippets


def build_draft(role: str, industry: str, task: str, snippets: list[str]) -> str:
    """根据搜索片段组装角色卡草稿"""
    snippet_block = "\n".join(f"- {s}" for s in snippets[:6])

    task_line = task if task else "〈待填写——请在阶段 3 绑定具体任务〉"

    return f"""# 角色：{role}（针对任务：{task_line}）

> **数据来源**：从招聘平台 JD 搜索 "{role} {industry}" 提炼，以下为草稿，需根据任务裁剪。

## JD 摘要（原始素材，定稿后可删）

{snippet_block}

## 立场
- 关注：**〈从 JD 职责中提炼该角色最坚持的 1～2 个核心关切〉**
- 默认怀疑：〈从 JD 的协作对象 / KPI 冲突推断，该角色天然怀疑谁的什么〉

## 发言要求
1. 〈从 JD 核心技能要求转化——发言时必须体现的专业能力〉
2. 〈从 JD 考核指标转化——用什么维度评判方案好坏〉
3. 〈从 JD 协作要求转化——与其他角色互动时的行为约束〉

## 禁止
- 〈从 JD 岗位边界 / 汇报线推断——不得越权的领域〉
- 〈从 JD "不负责"暗示推断——不替其他角色做决策〉
"""


def main():
    load_env()

    parser = argparse.ArgumentParser(description="从招聘 JD 生成角色卡草稿")
    parser.add_argument("--role", required=True, help="角色名称（如：内容运营、数据分析师）")
    parser.add_argument("--industry", default="", help="行业/领域（如：短视频、电商、SaaS）")
    parser.add_argument("--task", default="", help="当前工作坊任务（绑定到角色卡首行）")
    parser.add_argument("--platforms", default="", help="限定平台（默认搜 BOSS/猎聘/拉勾）")
    parser.add_argument("-o", "--output", help="输出文件路径（默认打印到终端）")

    args = parser.parse_args()

    print(f"🔍 搜索: {args.role} {args.industry} ...")
    results = search_jd(args.role, args.industry, args.platforms)
    snippets = extract_snippets(results)

    if not snippets:
        print("⚠️  未搜到有效 JD 片段，请调整关键词重试")
        sys.exit(1)

    print(f"📋 提取到 {len(snippets)} 条 JD 片段")
    draft = build_draft(args.role, args.industry, args.task, snippets)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(draft, encoding="utf-8")
        print(f"✅ 角色卡草稿已写入: {out_path}")
    else:
        print("\n" + "=" * 60)
        print(draft)
        print("=" * 60)
        print("\n💡 这是草稿，需要人工/导演将 〈占位符〉 替换为具体内容")


if __name__ == "__main__":
    main()
