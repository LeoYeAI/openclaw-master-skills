#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的GitCode评论检查脚本
"""

import json
import subprocess
import sys
from datetime import datetime

# 配置
TOKEN = "5_EtXLq3jGyQvb6tWwrN3byz"
API_BASE = "https://api.gitcode.com/api/v5"
USER = "newstarzj"
REPOS = [
    "cann/runtime",
    "cann/oam-tools",
    "cann/oam-tools-diag"
]

def log(msg):
    """带时间戳的日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {msg}")

def api_get(url):
    """调用 GitCode API"""
    sep = '&' if '?' in url else '?'
    cmd = f'curl -s "{url}{sep}access_token={TOKEN}&per_page=100"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except:
        return None

def check_mentions():
    """检查所有仓库的@评论"""
    log("========== 开始检查@评论 ==========")
    
    all_mentions = []
    
    for repo in REPOS:
        log(f"检查仓库 {repo} 中的@评论...")
        
        # 获取开放的PR
        prs_data = api_get(f"{API_BASE}/repos/{repo}/pulls?state=open&per_page=10")
        if not prs_data or not isinstance(prs_data, list):
            log(f"仓库 {repo} 没有开放的PR或获取失败")
            continue
        
        # 检查每个PR的评论
        for pr in prs_data:
            pr_num = pr['number']
            pr_title = pr.get('title', 'N/A')
            
            # 获取PR评论
            comments = api_get(f"{API_BASE}/repos/{repo}/pulls/{pr_num}/comments")
            if not comments or not isinstance(comments, list):
                continue
            
            # 检查评论中是否@了用户
            for comment in comments:
                body = comment.get('body', '')
                
                # 检查@提及
                if f'@{USER}' in body:
                    comment_id = comment.get('id')
                    comment_user = comment.get('user', {}).get('name', 'Unknown')
                    comment_time = comment.get('created_at', 'N/A')
                    comment_body = body[:100] + '...' if len(body) > 100 else body
                    
                    mention = {
                        'repo': repo,
                        'pr_num': pr_num,
                        'pr_title': pr_title,
                        'comment_id': comment_id,
                        'comment_user': comment_user,
                        'comment_time': comment_time,
                        'comment_body': comment_body,
                        'url': f"https://gitcode.com/{repo}/pull/{pr_num}"
                    }
                    all_mentions.append(mention)
                    log(f"发现@评论: PR #{pr_num}, 评论者: {comment_user}")
    
    # 输出结果
    if all_mentions:
        log(f"发现 {len(all_mentions)} 个需要审查的PR")
        print("\n=== MENTIONS_JSON ===")
        print(json.dumps(all_mentions, ensure_ascii=False))
        print("=== END_MENTIONS_JSON ===\n")
    else:
        log("没有发现新的@评论")
    
    log("========== 检查完成 ==========")
    return all_mentions

if __name__ == "__main__":
    mentions = check_mentions()
    sys.exit(0 if mentions else 0)