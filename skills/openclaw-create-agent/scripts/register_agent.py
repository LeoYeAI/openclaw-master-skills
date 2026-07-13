#!/usr/bin/env python3
"""
register_agent.py — 安全修改 openclaw.json，注册新 Agent

用法：
  python3 register_agent.py \
    --agent-id staff-ou_xxx \
    --workspace ~/.openclaw/agency-agents/staff-ou_xxx \
    --parent-id main \
    --also-allow feishu_get_user feishu_im_user_message ...

特性：
  - 注册前自动备份（带时间戳）
  - 双向绑定：agents.list + 父 Agent 的 allowAgents
  - 注册后执行 openclaw config validate
  - validate 失败自动回滚，不留残局
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

OPENCLAW_JSON = Path.home() / ".openclaw" / "openclaw.json"


def load_config():
    with open(OPENCLAW_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config):
    with open(OPENCLAW_JSON, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")


def backup_config():
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = str(OPENCLAW_JSON) + f".bak.{ts}"
    shutil.copy2(OPENCLAW_JSON, backup_path)
    print(f"✅ 已备份：{backup_path}")
    return backup_path


def rollback(backup_path):
    shutil.copy2(backup_path, OPENCLAW_JSON)
    print(f"🔄 已回滚至：{backup_path}")


def validate_config():
    result = subprocess.run(
        ["openclaw", "config", "validate"],
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout + result.stderr


def main():
    parser = argparse.ArgumentParser(description="注册新 Agent 到 openclaw.json")
    parser.add_argument("--agent-id", required=True, help="新 Agent 的 ID")
    parser.add_argument("--workspace", required=True, help="workspace 路径")
    parser.add_argument("--parent-id", required=True, help="父 Agent 的 ID（用于 allowAgents）")
    parser.add_argument("--also-allow", nargs="*", default=[], help="工具权限列表")
    parser.add_argument("--agent-dir", help="agentDir 路径（可选，不传则不写入此字段）")
    parser.add_argument("--dry-run", action="store_true",
                        help="预览将要对 openclaw.json 做的修改，不实际写入")
    args = parser.parse_args()

    agent_id = args.agent_id
    workspace = str(Path(args.workspace).expanduser())
    parent_id = args.parent_id
    also_allow = args.also_allow
    agent_dir = args.agent_dir  # None 时不写入 agentDir 字段
    dry_run = args.dry_run

    print(f"\n=== {'[DRY-RUN] ' if dry_run else ''}注册 Agent: {agent_id} ===")
    if dry_run:
        print("  ⚠️  DRY-RUN 模式：只预览变更，不写入任何文件")
    print(f"  workspace:  {workspace}")
    print(f"  agentDir:   {agent_dir or '(不写入)'}")
    print(f"  父 Agent:   {parent_id}")
    print(f"  工具权限:   {also_allow or '(无)'}")
    print()

    # Step 1: 备份（dry-run 模式跳过）
    backup_path = None
    if not dry_run:
        backup_path = backup_config()

    try:
        config = load_config()
        agents_section = config.get("agents", {})
        agents_list = agents_section.get("list", [])

        # Step 2: 检查是否已存在
        existing = next((a for a in agents_list if a.get("id") == agent_id), None)
        if existing:
            print(f"⚠️  Agent '{agent_id}' 已存在，将覆盖其定义。")

        # Step 3: 构建新 Agent 定义
        new_agent = {
            "id": agent_id,
            "workspace": workspace,
        }
        if agent_dir:
            new_agent["agentDir"] = agent_dir
        if also_allow:
            new_agent["tools"] = {"alsoAllow": also_allow}

        # Step 4: 写入 agents.list
        if existing:
            idx = next(i for i, a in enumerate(agents_list) if a.get("id") == agent_id)
            agents_list[idx] = new_agent
        else:
            agents_list.append(new_agent)

        agents_section["list"] = agents_list
        config["agents"] = agents_section

        # Step 5: 双向绑定 — 在父 Agent 的 allowAgents 里追加
        parent = next((a for a in agents_list if a.get("id") == parent_id), None)
        if parent is None:
            print(f"❌ 找不到父 Agent '{parent_id}'，请检查 agent id 是否正确")
            rollback(backup_path)
            sys.exit(1)

        subagents_config = parent.setdefault("subagents", {})
        allow_agents = subagents_config.get("allowAgents", [])
        if agent_id not in allow_agents:
            allow_agents.append(agent_id)
            subagents_config["allowAgents"] = allow_agents
            print(f"✅ 已将 '{agent_id}' 加入 '{parent_id}' 的 allowAgents")
        else:
            print(f"ℹ️  '{agent_id}' 已在 '{parent_id}' 的 allowAgents 中")

        # Step 6: 写入（dry-run 模式只打印 diff，不写入）
        if dry_run:
            import json as _json
            original = load_config()
            print("\n=== [DRY-RUN] 变更预览 ===")
            orig_agents = [a.get("id") for a in original.get("agents", {}).get("list", [])]
            new_agents  = [a.get("id") for a in agents_list]
            added = [i for i in new_agents if i not in orig_agents]
            updated = [i for i in new_agents if i in orig_agents and
                       next((a for a in original["agents"]["list"] if a["id"] == i), {}) !=
                       next((a for a in agents_list if a["id"] == i), {})]
            if added:
                print(f"  + agents.list 新增：{added}")
            if updated:
                print(f"  ~ agents.list 覆盖：{updated}")
            orig_parent = next((a for a in original.get("agents", {}).get("list", [])
                                if a.get("id") == parent_id), {})
            orig_allow = orig_parent.get("subagents", {}).get("allowAgents", [])
            new_allow = subagents_config.get("allowAgents", [])
            if agent_id not in orig_allow:
                print(f"  + {parent_id}.subagents.allowAgents 新增：{agent_id}")
            print("\n⚠️  DRY-RUN 完成，未写入任何文件。去掉 --dry-run 后执行实际注册。")
            return
        else:
            save_config(config)
            print("✅ openclaw.json 已更新")

        # Step 7: validate
        print("\n=== 执行 openclaw config validate ===")
        ok, output = validate_config()
        if ok:
            print("✅ validate 通过")
        else:
            print("❌ validate 失败，自动回滚")
            print(output)
            rollback(backup_path)
            print("\n📋 诊断建议：")
            print(f"  1. 查看备份与当前配置的差异：diff {backup_path} {OPENCLAW_JSON}")
            print(f"  2. 查看当前 agents 配置：openclaw config get agents")
            print(f"  3. 手动对比备份文件：{backup_path}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ 发生错误：{e}")
        if backup_path:
            rollback(backup_path)
        sys.exit(1)

    print(f"\n✅ Agent '{agent_id}' 注册完成")
    print("下一步：验证 workspace 完整性后重启 Gateway")
    print("  bash scripts/verify_workspace.sh <agentId> --type human|functional")
    print("  systemctl --user restart openclaw-gateway.service")
    print("  sleep 8  # 等待工具注册完成")


if __name__ == "__main__":
    main()
