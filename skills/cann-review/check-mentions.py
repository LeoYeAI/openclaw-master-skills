#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 GitCode 仓库中@你的评论并自动审查相关PR
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 配置
TOKEN = "5_EtXLq3jGyQvb6tWwrN3byz"
API_BASE = "https://api.gitcode.com/api/v5"
USER = "newstarzj"
STATE_FILE = Path.home() / ".openclaw/workspace/skills/cann-review/.mention-state.json"
REPOS = [
    "cann/runtime",
    "cann/oam-tools",
    "cann/oam-tools-diag"
]

def log(msg):
    """带时间戳的日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {msg}")

def init_state():
    """初始化状态文件"""
    if not STATE_FILE.exists():
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        state = {"checked_comments": [], "last_check": ""}
        STATE_FILE.write_text(json.dumps(state, indent=2))
    return json.loads(STATE_FILE.read_text())

def save_state(state):
    """保存状态文件"""
    STATE_FILE.write_text(json.dumps(state, indent=2))

def api_get(url):
    """调用 GitCode API"""
    # 使用access_token参数而非Bearer token，因为Bearer方式会截断评论列表
    sep = '&' if '?' in url else '?'
    cmd = f'curl -s "{url}{sep}access_token={TOKEN}&per_page=100"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except:
        return None

def check_repo_mentions(repo, state):
    """检查仓库中的@评论"""
    log(f"检查仓库 {repo} 中的@评论...")
    
    # 获取开放的PR
    prs_data = api_get(f"{API_BASE}/repos/{repo}/pulls?state=open&per_page=50")
    if not prs_data or not isinstance(prs_data, list):
        log(f"仓库 {repo} 没有开放的PR或获取失败")
        return []
    
    new_mentions = []
    
    for pr in prs_data:
        pr_num = pr['number']
        
        # 获取PR评论
        comments = api_get(f"{API_BASE}/repos/{repo}/pulls/{pr_num}/comments")
        if not comments or not isinstance(comments, list):
            continue
        
        # 检查评论中是否@了用户（支持多种格式）
        for comment in comments:
            body = comment.get('body', '')
            
            # 检查多种@格式
            has_mention = False
            if f'@{USER}' in body:
                has_mention = True
            elif f'[@{USER}]' in body:
                has_mention = True
            elif f'@{USER}' in body:
                has_mention = True
            
            if has_mention:
                comment_id = comment.get('id')
                
                # 检查是否已经处理过
                if comment_id in state['checked_comments']:
                    continue
                
                # 记录新的@评论
                new_mentions.append({
                    'repo': repo,
                    'pr_num': pr_num,
                    'pr_title': pr.get('title', 'N/A'),
                    'comment_id': comment_id,
                    'comment_user': comment.get('user', {}).get('name', 'Unknown'),
                    'comment_time': comment.get('created_at', 'N/A'),
                    'comment_body': body[:100],
                    'url': f"https://gitcode.com/{repo}/pull/{pr_num}"
                })
                
                # 标记为已处理
                state['checked_comments'].append(comment_id)
                log(f"发现新的@评论: PR #{pr_num}, 评论者: {comment.get('user', {}).get('name', 'Unknown')}")
    
    log(f"仓库 {repo} 发现 {len(new_mentions)} 个新的@评论")
    return new_mentions

def main():
    """主函数"""
    log("========== 开始检查@评论 ==========")
    
    # 初始化状态
    state = init_state()
    
    # 检查所有仓库
    all_mentions = []
    for repo in REPOS:
        mentions = check_repo_mentions(repo, state)
        all_mentions.extend(mentions)
    
    # 更新状态
    state['last_check'] = datetime.now().isoformat()
    save_state(state)
    
    # 输出结果供后续处理
    if all_mentions:
        log(f"发现 {len(all_mentions)} 个需要审查的PR")
        # 输出JSON格式供 agent 解析
        print("\n=== MENTIONS_JSON ===")
        print(json.dumps(all_mentions, ensure_ascii=False))
        print("=== END_MENTIONS_JSON ===\n")
    else:
        log("没有发现新的@评论")
    
    log("========== 检查完成 ==========")
    
    return all_mentions

if __name__ == "__main__":
    mentions = main()
    sys.exit(0 if mentions else 0)
