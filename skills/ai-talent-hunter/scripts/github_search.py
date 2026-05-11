#!/usr/bin/env python3
"""
GitHub Talent Hunter — Repo Search + User Search 双搜索引擎

评分算法 V3（100 分制）：
1. 领域匹配度（35分）  2. 可触达性（25分）  3. 代码影响力（20分）
4. 有效活跃度（12分）  5. 开源生态位（8分）

Usage:
    # 首次搜索
    python github_search.py --queries "language:c++ rocksdb pushed:>2025-01-01" \\
      --jd-keywords "rocksdb,lsm-tree" --jd-language "C++" \\
      --location "shenzhen" --target 20 -o results.json

    # 继续搜索
    python github_search.py --resume SEARCH_ID --target 20 -o results.json
"""

import os
import re
import sys
import json
import math
import time
import uuid
import argparse
import requests
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime

# 支持从 scripts/ 目录或项目根目录运行
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from location_data import LocationTarget, resolve_location, match_location, build_user_search_locations


class GitHubTalentHunterV3:
    """GitHub 人才猎手 V3 - 专业排序算法"""

    # Rate limiting 配置
    REQUEST_INTERVAL = 0.5  # 每次请求间隔（秒）
    RATE_LIMIT_WARNING_THRESHOLD = 200  # 剩余配额低于此值时警告

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("缺少 GITHUB_TOKEN 环境变量")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.endpoint = "https://api.github.com/graphql"
        self._last_request_time = 0.0

    MAX_RETRIES = 2  # 502/503 重试次数

    def _graphql_request(self, query: str, variables: Optional[Dict] = None, timeout: int = 30) -> Optional[Dict]:
        """
        通用 GraphQL 请求，内置 rate limiting、重试和错误处理。

        Returns:
            响应的 data 字段，如果出错返回 None
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        for attempt in range(1 + self.MAX_RETRIES):
            # Rate limiting
            elapsed = time.time() - self._last_request_time
            if elapsed < self.REQUEST_INTERVAL:
                time.sleep(self.REQUEST_INTERVAL - elapsed)

            try:
                response = requests.post(
                    self.endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=timeout
                )
                self._last_request_time = time.time()

                # 502/503 可重试
                if response.status_code in (502, 503) and attempt < self.MAX_RETRIES:
                    wait = 2 ** attempt  # 指数退避: 1s, 2s
                    print(f"[WARN] {response.status_code}，{wait}s 后重试 ({attempt+1}/{self.MAX_RETRIES})", file=sys.stderr)
                    time.sleep(wait)
                    continue

                response.raise_for_status()

                # 检查 rate limit
                remaining = response.headers.get("X-RateLimit-Remaining")
                if remaining and int(remaining) < self.RATE_LIMIT_WARNING_THRESHOLD:
                    reset_time = response.headers.get("X-RateLimit-Reset", "?")
                    print(f"[WARN] GitHub API 配额剩余: {remaining}，重置时间: {reset_time}", file=sys.stderr)

                data = response.json()
                if "errors" in data:
                    print(f"[ERROR] GraphQL 错误: {data['errors']}", file=sys.stderr)
                    return None

                return data.get("data")

            except requests.exceptions.Timeout:
                if attempt < self.MAX_RETRIES:
                    print(f"[WARN] 请求超时，重试 ({attempt+1}/{self.MAX_RETRIES})", file=sys.stderr)
                    continue
                print(f"[ERROR] GraphQL 请求超时 ({timeout}s)", file=sys.stderr)
                return None
            except requests.exceptions.RequestException as e:
                if attempt < self.MAX_RETRIES and "502" in str(e):
                    print(f"[WARN] {e}，重试 ({attempt+1}/{self.MAX_RETRIES})", file=sys.stderr)
                    time.sleep(2 ** attempt)
                    continue
                print(f"[ERROR] 请求失败: {e}", file=sys.stderr)
                return None

        return None
    
    def search_repos_page(self, query: str, cursor: Optional[str] = None, per_page: int = 50) -> tuple:
        """
        搜索单页仓库（支持分页）

        Returns:
            (repos, next_cursor, has_next_page)
        """
        graphql_query = """
        query SearchRepos($query: String!, $perPage: Int!, $cursor: String) {
          search(query: $query, type: REPOSITORY, first: $perPage, after: $cursor) {
            pageInfo {
              hasNextPage
              endCursor
            }
            nodes {
              ... on Repository {
                name
                description
                stargazerCount
                forkCount
                primaryLanguage { name }
                url
                owner {
                  login
                  ... on User {
                    name
                    bio
                    location
                    company
                    email
                    websiteUrl
                    twitterUsername
                    createdAt
                    followers { totalCount }
                    socialAccounts(first: 10) {
                      nodes {
                        provider
                        url
                      }
                    }
                  }
                }
                defaultBranchRef {
                  target {
                    ... on Commit {
                      history(first: 10) {
                        nodes {
                          author {
                            user {
                              login
                              name
                              bio
                              location
                              company
                              email
                              websiteUrl
                              twitterUsername
                              createdAt
                              followers { totalCount }
                              socialAccounts(first: 10) {
                                nodes {
                                  provider
                                  url
                                }
                              }
                            }
                          }
                          committedDate
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """

        cursor_info = f" (cursor: {cursor[:20]}...)" if cursor else " (第1页)"
        print(f"[DEBUG] 搜索仓库{cursor_info}: {query}", file=sys.stderr)

        variables = {
            "query": query,
            "perPage": per_page,
            "cursor": cursor
        }

        data = self._graphql_request(graphql_query, variables)
        if not data:
            return [], None, False

        search_result = data.get("search", {})
        repos = search_result.get("nodes", [])
        page_info = search_result.get("pageInfo", {})

        next_cursor = page_info.get("endCursor")
        has_next_page = page_info.get("hasNextPage", False)

        print(f"[INFO] 找到 {len(repos)} 个仓库，hasNextPage={has_next_page}", file=sys.stderr)
        return repos, next_cursor, has_next_page

    def fetch_user_repos_batch(self, logins: List[str], batch_size: int = 10) -> Dict[str, List]:
        """
        批量查询多个用户的仓库列表（Top 10 by stars）。
        用 GraphQL alias 一次查询多个用户，大幅减少 API 调用。

        Args:
            logins: GitHub 用户名列表
            batch_size: 每批查询的用户数（默认 10）

        Returns:
            {login: [repos]} 的字典
        """
        results = {}
        repo_fragment = """
            repositories(first: 10, orderBy: {field: STARGAZERS, direction: DESC}) {
              nodes {
                name
                stargazerCount
                forkCount
                description
                primaryLanguage { name }
              }
            }
        """

        for i in range(0, len(logins), batch_size):
            batch = logins[i:i + batch_size]
            # 构建批量查询，每个用户用 alias 区分
            user_queries = []
            for j, login in enumerate(batch):
                # GraphQL alias 不支持特殊字符，用 user_N 作为 alias
                user_queries.append(f'  user_{j}: user(login: "{login}") {{ {repo_fragment} }}')

            query = "query BatchUserRepos {\n" + "\n".join(user_queries) + "\n}"

            print(f"[INFO] 批量查询用户仓库 [{i+1}-{i+len(batch)}/{len(logins)}]", file=sys.stderr)
            data = self._graphql_request(query, timeout=30)

            if not data:
                # 批量失败时，逐个降级查询
                print(f"[WARN] 批量查询失败，降级为逐个查询", file=sys.stderr)
                for login in batch:
                    results[login] = self._fetch_single_user_repos(login)
                continue

            for j, login in enumerate(batch):
                user_data = data.get(f"user_{j}")
                if user_data:
                    repos = user_data.get("repositories", {}).get("nodes", [])
                    results[login] = repos
                else:
                    results[login] = []

        return results

    def _fetch_single_user_repos(self, login: str) -> List[Dict]:
        """单个用户仓库查询（批量查询的降级方案）"""
        graphql_query = """
        query GetUserRepos($login: String!) {
          user(login: $login) {
            repositories(first: 10, orderBy: {field: STARGAZERS, direction: DESC}) {
              nodes {
                name
                stargazerCount
                forkCount
                description
                primaryLanguage { name }
              }
            }
          }
        }
        """
        data = self._graphql_request(graphql_query, {"login": login}, timeout=10)
        if not data:
            return []

        user_data = data.get("user")
        if not user_data:
            return []

        return user_data.get("repositories", {}).get("nodes", [])

    def search_users_page(self, query: str, cursor: Optional[str] = None, per_page: int = 50) -> tuple:
        """
        GitHub User Search (type: USER)。
        直接搜人，支持 location:, followers:, language: 参数。
        返回的用户已包含 repositories，不需要二次查询。

        Returns:
            (users, next_cursor, has_next_page)
        """
        graphql_query = """
        query SearchUsers($query: String!, $perPage: Int!, $cursor: String) {
          search(query: $query, type: USER, first: $perPage, after: $cursor) {
            pageInfo {
              hasNextPage
              endCursor
            }
            nodes {
              ... on User {
                login
                name
                bio
                location
                company
                email
                websiteUrl
                twitterUsername
                createdAt
                isHireable
                status { message emoji }
                followers { totalCount }
                socialAccounts(first: 10) {
                  nodes {
                    provider
                    url
                    displayName
                  }
                }
                repositories(first: 10, orderBy: {field: STARGAZERS, direction: DESC}) {
                  nodes {
                    name
                    stargazerCount
                    forkCount
                    description
                    primaryLanguage { name }
                    pushedAt
                  }
                }
              }
            }
          }
        }
        """

        cursor_info = f" (cursor: {cursor[:20]}...)" if cursor else " (第1页)"
        print(f"[DEBUG] User Search{cursor_info}: {query}", file=sys.stderr)

        data = self._graphql_request(graphql_query, {
            "query": query,
            "perPage": per_page,
            "cursor": cursor
        })
        if not data:
            return [], None, False

        search_result = data.get("search", {})
        users = search_result.get("nodes", [])
        page_info = search_result.get("pageInfo", {})

        next_cursor = page_info.get("endCursor")
        has_next_page = page_info.get("hasNextPage", False)

        # 标记来源，User Search 已包含 repositories，跳过后续 batch fetch
        for user in users:
            if isinstance(user, dict) and "login" in user:
                user["_source"] = "user_search"

        print(f"[INFO] User Search 找到 {len(users)} 个用户，hasNextPage={has_next_page}", file=sys.stderr)
        return users, next_cursor, has_next_page

    def enrich_user_details_batch(self, users: List[Dict], batch_size: int = 5) -> None:
        """
        批量补充重量级字段（去重+过滤后调用）。
        直接修改 user dict，添加 contributionsCollection、pinnedItems、repositoryTopics。

        这些字段太重无法放在搜索查询中（会导致 RESOURCE_LIMITS_EXCEEDED），
        所以在搜索完成后单独批量查询。
        """
        logins = [u.get('login') for u in users if u.get('login')]
        if not logins:
            return

        enrich_fragment = """
            contributionsCollection {
              totalCommitContributions
              totalPullRequestContributions
              totalIssueContributions
              contributionCalendar { totalContributions }
            }
            pinnedItems(first: 6) {
              nodes {
                ... on Repository {
                  name description stargazerCount primaryLanguage { name }
                }
              }
            }
            repositories(first: 10, orderBy: {field: STARGAZERS, direction: DESC}) {
              nodes {
                name
                repositoryTopics(first: 10) { nodes { topic { name } } }
              }
            }
        """

        # login → user dict 的映射
        user_map = {u['login']: u for u in users if u.get('login')}
        enriched = 0

        for i in range(0, len(logins), batch_size):
            batch = logins[i:i + batch_size]
            user_queries = []
            for j, login in enumerate(batch):
                user_queries.append(f'  user_{j}: user(login: "{login}") {{ {enrich_fragment} }}')

            query = "{\n" + "\n".join(user_queries) + "\n}"

            print(f"[INFO] 补充候选人详情 [{i+1}-{i+len(batch)}/{len(logins)}]", file=sys.stderr)
            data = self._graphql_request(query, timeout=30)

            if not data:
                continue

            for j, login in enumerate(batch):
                user_data = data.get(f"user_{j}")
                if not user_data or login not in user_map:
                    continue

                u = user_map[login]

                # contributionsCollection
                cc = user_data.get("contributionsCollection", {})
                u["contributionsCollection"] = cc

                # pinnedItems
                pinned = user_data.get("pinnedItems", {}).get("nodes", [])
                u["pinnedItems"] = pinned

                # repositoryTopics → 合并到已有 repos
                enriched_repos = user_data.get("repositories", {}).get("nodes", [])
                existing_repos = u.get("repositories", {}).get("nodes", [])
                for er in enriched_repos:
                    for existing in existing_repos:
                        if existing.get("name") == er.get("name"):
                            topics = [t["topic"]["name"] for t in er.get("repositoryTopics", {}).get("nodes", [])]
                            existing["topics"] = topics
                            break

                enriched += 1

        print(f"[INFO] 已补充 {enriched}/{len(logins)} 个候选人的详细信息", file=sys.stderr)

    def extract_users_from_repos(self, repos: List[Dict]) -> List[Dict]:
        """从仓库列表中提取所有候选人（Owner + Contributors）"""
        all_users = []

        for repo in repos:
            # 提取 repo 最新 commit 时间（用于 Owner 活跃度）
            latest_commit_date = None
            branch_ref = repo.get("defaultBranchRef")
            if branch_ref:
                target = branch_ref.get("target")
                if target:
                    commits = target.get("history", {}).get("nodes") or []
                    if commits:
                        latest_commit_date = commits[0].get("committedDate")

            # 1. 提取仓库所有者（Owner）
            owner = repo.get("owner")
            if owner and isinstance(owner, dict) and "login" in owner:
                owner['is_owner'] = True
                owner['repo_stars'] = repo.get("stargazerCount", 0)
                owner['repo_forks'] = repo.get("forkCount", 0)
                # Owner 也获取活跃度数据（取 repo 最新 commit 时间）
                if latest_commit_date:
                    owner['last_commit_date'] = latest_commit_date
                all_users.append(owner)

            # 2. 提取最近的贡献者（Contributors from Commits）
            if branch_ref and branch_ref.get("target"):
                commits = branch_ref["target"].get("history", {}).get("nodes") or []
                for commit in commits:
                    author_user = commit.get("author", {}).get("user")
                    if author_user and isinstance(author_user, dict) and "login" in author_user:
                        author_user['is_owner'] = False
                        author_user['last_commit_date'] = commit.get("committedDate")
                        all_users.append(author_user)

        return all_users
    
    def deduplicate_users(self, users: List[Dict]) -> List[Dict]:
        """去重用户（基于 login），合并多次出现的数据"""
        unique_users = {}

        for user in users:
            login = user.get("login")
            if not login:
                continue

            if login in unique_users:
                existing = unique_users[login]
                # 合并 is_owner 标记（任一出现则为 True）
                if user.get('is_owner'):
                    existing['is_owner'] = True
                # 合并 repo_stars / repo_forks（取最大值）
                if user.get('repo_stars', 0) > existing.get('repo_stars', 0):
                    existing['repo_stars'] = user['repo_stars']
                if user.get('repo_forks', 0) > existing.get('repo_forks', 0):
                    existing['repo_forks'] = user['repo_forks']
                # 合并 last_commit_date（取最新的）
                new_date = user.get('last_commit_date')
                old_date = existing.get('last_commit_date')
                if new_date and (not old_date or new_date > old_date):
                    existing['last_commit_date'] = new_date
                # 补充缺失的 profile 字段
                for key in ['email', 'bio', 'location', 'company', 'name', 'websiteUrl', 'twitterUsername']:
                    if user.get(key) and not existing.get(key):
                        existing[key] = user[key]
                # 合并 socialAccounts
                if user.get('socialAccounts') and not existing.get('socialAccounts'):
                    existing['socialAccounts'] = user['socialAccounts']
            else:
                unique_users[login] = user

        print(f"[INFO] 去重后剩余 {len(unique_users)} 个用户", file=sys.stderr)
        return list(unique_users.values())
    
    # filter_by_email 已移除 — 邮箱现在是评分维度，不再做硬性过滤
    
    def filter_by_location_legacy(self, users: List[Dict], location_filter: str) -> List[Dict]:
        """
        地理位置过滤（AND 逻辑 - 必须满足）
        
        雯姐的新规则:
        1. Remote 自动通过（不受地理位置限制）
        2. 中文判断：GitHub 有中文 → 判定为中国
        3. 扩展城市关键词（14个城市 + 港澳台）
        
        Args:
            users: 候选人列表
            location_filter: 地理位置关键词（如 china, beijing, usa）
        
        Returns:
            过滤后的候选人列表
        """
        location_keywords = location_filter.lower().split(',')
        
        # 扩展中国相关关键词（省会城市 + 主要城市 + 港澳台）
        if 'china' in location_keywords:
            location_keywords.extend([
                '中国', 'chinese', 'cn', 'prc',
                
                # 直辖市
                'beijing', '北京', 'bj',
                'shanghai', '上海', 'sh',
                'tianjin', '天津', 'tj',
                'chongqing', '重庆', 'cq',
                
                # 省会 + 新一线城市
                'hangzhou', '杭州', 'hz',
                'chengdu', '成都', 'cd',
                'nanjing', '南京', 'nj',
                'wuhan', '武汉', 'wh',
                'xian', "xi'an", '西安',
                'suzhou', '苏州', 'sz',  # 注意：sz 也可能是深圳
                'shenzhen', '深圳',
                'guangzhou', '广州', 'gz',
                'xiamen', '厦门', 'xm',
                'qingdao', '青岛', 'qd',
                
                # 其他省会城市
                'zhengzhou', '郑州',
                'changsha', '长沙',
                'fuzhou', '福州',
                'hefei', '合肥',
                'nanchang', '南昌',
                'jinan', '济南',
                'taiyuan', '太原',
                'shijiazhuang', '石家庄',
                'harbin', '哈尔滨',
                'changchun', '长春',
                'shenyang', '沈阳',
                'hohhot', '呼和浩特',
                'urumqi', '乌鲁木齐',
                'lanzhou', '兰州',
                'yinchuan', '银川',
                'xining', '西宁',
                'lhasa', '拉萨',
                'kunming', '昆明',
                'guiyang', '贵阳',
                'nanning', '南宁',
                'haikou', '海口',
                
                # 主要二线城市
                'dongguan', '东莞',
                'foshan', '佛山',
                'ningbo', '宁波', 'nb',
                'wuxi', '无锡', 'wx',
                'changzhou', '常州',
                'dalian', '大连', 'dl',
                'zhuhai', '珠海',
                'wenzhou', '温州', 'wz',
                'shaoxing', '绍兴',
                'jiaxing', '嘉兴',
                'huzhou', '湖州',
                'jinhua', '金华',
                'taizhou', '台州',
                'quzhou', '衢州',
                'zhoushan', '舟山',
                'lishui', '丽水',
                
                # 港澳台
                'hong kong', 'hongkong', 'hk', '香港',
                'taiwan', 'taipei', 'tw', '台湾', '台北',
                'kaohsiung', '高雄',
                'taichung', '台中',
                'tainan', '台南',
                'macau', 'macao', '澳门',
                
                # 省份名（有些人只填省份）
                'guangdong', '广东',
                'jiangsu', '江苏',
                'zhejiang', '浙江',
                'shandong', '山东',
                'henan', '河南',
                'sichuan', '四川',
                'hubei', '湖北',
                'hunan', '湖南',
                'fujian', '福建',
                'anhui', '安徽',
                'hebei', '河北',
                'shaanxi', '陕西',
                'liaoning', '辽宁',
                'jilin', '吉林',
                'heilongjiang', '黑龙江',
            ])
        
        # 扩展新加坡相关关键词
        if 'singapore' in location_keywords:
            location_keywords.extend([
                'sg',  # 常用缩写
                'sgp',
                'singaporean',
                '新加坡',
            ])
        
        # 分离短缩写和长关键词，短缩写用词边界匹配避免误判
        short_keywords = [kw for kw in location_keywords if len(kw) <= 3 and kw.isascii()]
        long_keywords = [kw for kw in location_keywords if len(kw) > 3 or not kw.isascii()]

        # 预编译短缩写的正则（词边界匹配）
        short_patterns = [re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE) for kw in short_keywords] if short_keywords else []

        def has_chinese(text):
            return bool(re.search(r'[\u4e00-\u9fff]', text))

        filtered = []
        for user in users:
            location = (user.get('location') or '').lower()
            name = user.get('name') or ''
            bio = user.get('bio') or ''

            # 规则1: Remote 自动通过
            if 'remote' in location:
                filtered.append(user)
                continue

            # 规则2: location 包含目标关键词
            # 长关键词（>=4字符或中文）用 in 匹配
            if any(keyword in location for keyword in long_keywords):
                filtered.append(user)
                continue
            # 短缩写用词边界匹配，避免 "Graz" 匹配 "gz" 等误判
            if any(pattern.search(location) for pattern in short_patterns):
                filtered.append(user)
                continue

            # 规则3: 中文判断（name 或 bio 包含中文）
            if 'china' in location_keywords and (has_chinese(name) or has_chinese(bio)):
                filtered.append(user)
                continue

        return filtered
    
    def filter_by_location(self, users: List[Dict], target: LocationTarget, strict: bool = False) -> List[Dict]:
        """
        地理位置过滤。

        strict=False（默认）: 层级回落 city → province → country → 中文启发式
        strict=True: 仅匹配指定城市/省份，不回落到国家。Remote 仍通过。
        """
        mode = "严格" if strict else "宽松"
        filtered = []
        for user in users:
            user_loc = user.get('location') or ''
            user_name = user.get('name') or ''
            user_bio = user.get('bio') or ''
            matched, reason = match_location(user_loc, user_name, user_bio, target, strict=strict)
            if matched:
                user['_location_match_reason'] = reason
                filtered.append(user)
        print(f"[INFO] 地理位置过滤（{mode}）: {len(users)} → {len(filtered)} 人", file=sys.stderr)
        return filtered

    def _get_follower_count(self, user: Dict) -> int:
        """安全提取 follower 数量"""
        followers = user.get('followers', {})
        if isinstance(followers, dict):
            return followers.get('totalCount', 0)
        return followers or 0

    def calculate_score(self, user: Dict, jd_keywords: List[str], jd_language: str) -> Dict:
        """
        候选人综合评分算法 V3（100 分制）

        设计原则（猎头视角）：
        - 领域匹配是前提：找错人一切白费
        - 可触达性决定转化率：联系不上的大牛不如联系得上的牛人
        - 影响力体现技术深度：但不应被 star 通胀稀释
        - 活跃度预测响应概率：活跃的人更可能回复
        - 生态位是锦上添花：区分 leader vs follower

        维度与权重：
        1. 领域匹配度（Relevance）  — 35 分  最重要，错了后面都白搭
        2. 可触达性（Reachability）  — 25 分  能联系上才有意义
        3. 代码影响力（Impact）      — 20 分  技术深度的代理指标
        4. 有效活跃度（Activity）    — 12 分  活跃度越高越可能回复
        5. 开源生态位（Ecosystem）   —  8 分  区分度最低的维度
        """
        scores = {
            "relevance": 0.0,      # 领域匹配度（35分）
            "reachability": 0.0,   # 可触达性（25分）
            "impact": 0.0,         # 代码影响力（20分）
            "activity": 0.0,       # 有效活跃度（12分）
            "contribution": 0.0,   # 开源生态位（8分）
            "total": 0.0
        }

        repos = user.get('repositories', {}).get('nodes', [])

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 1. 领域匹配度（Relevance — 35 分）
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        # 1A. 主语言匹配（15 分）：Top 5 仓库中有目标语言即可
        for repo in repos[:5]:
            lang = repo.get('primaryLanguage') or {}
            if lang and lang.get('name', '').lower() == jd_language.lower():
                scores['relevance'] += 15
                break

        # 1B. 生态关键词匹配（20 分）：按命中数分级
        #   匹配源：repo name + description + repositoryTopics（标签匹配更精准）
        #   命中 3+ 个关键词 → 20 分（深度匹配）
        #   命中 2 个 → 15 分
        #   命中 1 个 → 10 分
        matched_keywords = set()
        for repo in repos[:5]:
            desc = (repo.get('description') or '').lower()
            repo_name = repo.get('name', '').lower()
            # 提取 topics 标签
            topics = [t.lower() for t in repo.get('topics', [])]
            text = f"{desc} {repo_name} {' '.join(topics)}"
            for keyword in jd_keywords:
                if keyword.lower() in text:
                    matched_keywords.add(keyword.lower())

        kw_count = len(matched_keywords)
        if kw_count >= 3:
            scores['relevance'] += 20
        elif kw_count == 2:
            scores['relevance'] += 15
        elif kw_count == 1:
            scores['relevance'] += 10

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 2. 可触达性（Reachability — 25 分）
        #    分级计分，多渠道可叠加，上限 25 分
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        reachability_raw = 0.0

        # 2A. 公开邮箱（+10）— 最直接的触达方式
        if user.get('email'):
            reachability_raw += 10

        # 2B. 个人网站/博客（+6）— 可以找到更多联系方式，也是破冰素材
        if user.get('websiteUrl'):
            reachability_raw += 6

        # 2C. Twitter/X（+5）— DM 是有效触达渠道
        if user.get('twitterUsername'):
            reachability_raw += 5

        # 2D. 其他社交账号（每个 +3，上限 +6）— LinkedIn、知乎等
        social_nodes = user.get("socialAccounts", {}).get("nodes", [])
        other_social_count = 0
        for account in social_nodes:
            provider = (account.get("provider") or "").lower()
            # 排除已单独计分的 twitter
            if provider and provider not in ("twitter", "x"):
                other_social_count += 1
        reachability_raw += min(other_social_count * 3, 6)

        # 2E. Profile 完整度（+3）— bio 不为空说明愿意被人了解
        if user.get('bio'):
            reachability_raw += 3

        # 2F. isHireable（+5）— 候选人主动标记"可被雇佣"，回复概率极高
        if user.get('isHireable'):
            reachability_raw += 5

        scores['reachability'] = min(reachability_raw, 25)

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 3. 代码影响力（Impact — 20 分）
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        total_stars = sum(r.get('stargazerCount', 0) for r in repos)
        total_forks = sum(r.get('forkCount', 0) for r in repos)
        follower_count = self._get_follower_count(user)

        # 3A. Star 影响力（上限 12 分）— 用 log 曲线避免被 star 通胀稀释
        #   10 stars → 3 分, 100 → 6 分, 1000 → 9 分, 5000+ → 12 分
        import math
        if total_stars > 0:
            star_score = min(math.log10(total_stars) * 3, 12)
            scores['impact'] += round(star_score, 1)

        # 3B. Fork 复用度（上限 4 分）
        if total_forks > 0:
            fork_score = min(math.log10(total_forks) * 2, 4)
            scores['impact'] += round(fork_score, 1)

        # 3C. 社区关注度（上限 4 分）
        if follower_count > 0:
            follower_score = min(math.log10(follower_count) * 2, 4)
            scores['impact'] += round(follower_score, 1)

        scores['impact'] = min(scores['impact'], 20)

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 4. 有效活跃度（Activity — 12 分）
        #    综合三个信号：last_commit_date + pushedAt + totalContributions
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        # 信号 A: 最近活跃时间（last_commit_date 或 repo pushedAt）
        recency_score = 0
        best_date = user.get('last_commit_date') or ''
        # 也检查 repos 的 pushedAt（User Search 用户没有 last_commit_date）
        for repo in repos[:5]:
            pushed = repo.get('pushedAt', '')
            if pushed and pushed > best_date:
                best_date = pushed

        if best_date:
            try:
                dt = datetime.fromisoformat(best_date.replace('Z', '+00:00'))
                days_ago = (datetime.now(dt.tzinfo) - dt).days
                if days_ago < 30:
                    recency_score = 8
                elif days_ago < 90:
                    recency_score = 5
                elif days_ago < 180:
                    recency_score = 3
            except Exception:
                pass

        # 信号 B: 贡献量（来自 contributionsCollection）
        volume_score = 0
        cc = user.get('contributionsCollection', {})
        total_contributions = cc.get('contributionCalendar', {}).get('totalContributions', 0)
        if total_contributions >= 1000:
            volume_score = 4    # 年贡献 1000+ = 非常活跃
        elif total_contributions >= 300:
            volume_score = 3
        elif total_contributions >= 100:
            volume_score = 2
        elif total_contributions > 0:
            volume_score = 1

        scores['activity'] = min(recency_score + volume_score, 12)

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 5. 开源生态位（Ecosystem — 8 分）
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        if user.get('is_owner') and repos:
            max_stars = max((r.get('stargazerCount', 0) for r in repos), default=0)
            if max_stars > 500:
                scores['contribution'] = 8    # 顶级 Owner
            elif max_stars > 100:
                scores['contribution'] = 5    # 有影响力的 Owner
            elif max_stars > 20:
                scores['contribution'] = 3    # 活跃 Owner

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 总分（100 分制）
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        scores['total'] = round(
            scores['relevance'] + scores['reachability'] + scores['impact'] +
            scores['activity'] + scores['contribution'], 1
        )

        return scores
    
    def build_candidate_profile(self, user: Dict, scores: Dict) -> Dict:
        """构建候选人完整画像"""
        username = user.get("login", "")

        # 提取社交账号
        social_accounts = {}
        social_nodes = user.get("socialAccounts", {}).get("nodes", [])
        for account in social_nodes:
            provider = account.get("provider", "").lower()
            url = account.get("url", "")
            if provider and url:
                social_accounts[provider] = url

        follower_count = self._get_follower_count(user)

        # 计算开发年限
        created_at = user.get("createdAt") or ""
        dev_years = 0
        if created_at:
            try:
                created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                dev_years = max(0, (datetime.now(created.tzinfo) - created).days // 365)
            except Exception:
                pass

        # 提取代表作：优先 pinnedItems（候选人自选），兜底 Top Star 仓库
        pinned_items = user.get('pinnedItems', [])
        repos = user.get('repositories', {}).get('nodes', [])

        # pinnedItems 作为代表作（如果有）
        pinned_repos = []
        if pinned_items:
            for item in pinned_items[:3]:
                if isinstance(item, dict) and item.get('name'):
                    primary_lang = item.get('primaryLanguage') or {}
                    pinned_repos.append({
                        "name": item.get('name'),
                        "stars": item.get('stargazerCount', 0),
                        "language": primary_lang.get('name', '') if isinstance(primary_lang, dict) else '',
                        "description": item.get('description', ''),
                        "pinned": True
                    })

        # Top Star 仓库（兜底或补充）
        top_repos = []
        for repo in repos[:3]:
            primary_lang = repo.get('primaryLanguage') or {}
            top_repos.append({
                "name": repo.get('name'),
                "stars": repo.get('stargazerCount', 0),
                "forks": repo.get('forkCount', 0),
                "language": primary_lang.get('name', '') if isinstance(primary_lang, dict) else '',
                "description": repo.get('description', ''),
                "topics": repo.get('topics', []),
                "pushed_at": repo.get('pushedAt', ''),
            })

        # 代表作 = pinnedItems 优先，没有则用 top_repos
        showcase_repos = pinned_repos if pinned_repos else top_repos
        
        # 活跃状态
        activity_label = "⚪ 不活跃"
        if scores.get("activity", 0) >= 10:
            activity_label = "🟢 活跃"
        elif scores.get("activity", 0) >= 6:
            activity_label = "🟡 近期活跃"
        elif scores.get("activity", 0) > 0:
            activity_label = "🔵 半年内活跃"

        # 匹配度标签
        total = scores.get("total", 0)
        if total >= 80:
            match_label = "🔥 极度匹配"
        elif total >= 65:
            match_label = "⭐ 高度匹配"
        elif total >= 50:
            match_label = "👍 匹配"
        else:
            match_label = "📋 参考"

        # 联系渠道图标
        contact_icons = []
        if user.get("email"):
            contact_icons.append("📧")
        if user.get("websiteUrl"):
            contact_icons.append("🌐")
        if user.get("twitterUsername"):
            contact_icons.append("🐦")
        if social_nodes:
            for acc in social_nodes:
                p = (acc.get("provider") or "").lower()
                if p and p not in ("twitter", "x"):
                    contact_icons.append("🔗")
                    break

        # 贡献统计
        cc = user.get("contributionsCollection", {})
        contributions = {
            "total": cc.get("contributionCalendar", {}).get("totalContributions", 0),
            "commits": cc.get("totalCommitContributions", 0),
            "pull_requests": cc.get("totalPullRequestContributions", 0),
            "issues": cc.get("totalIssueContributions", 0),
        }

        # isHireable
        is_hireable = user.get("isHireable", False)

        # 用户状态
        user_status = user.get("status") or {}
        status_message = user_status.get("message", "")

        # isHireable 标记
        if is_hireable:
            activity_label = activity_label + " | 🟢 求职中"

        return {
            "github_id": username,
            "name": user.get("name") or username,
            "bio": user.get("bio") or "",
            "location": user.get("location") or "未知",
            "company": user.get("company") or "",
            "blog": user.get("websiteUrl") or "",
            "email": user.get("email") or "",
            "twitter": user.get("twitterUsername") or "",
            "followers": follower_count,
            "created_at": created_at,
            "dev_years": dev_years,
            "is_hireable": is_hireable,
            "user_status": status_message,
            "profile_url": f"https://github.com/{username}",
            "social_accounts": social_accounts,
            "showcase_repos": showcase_repos,
            "top_repos": top_repos,
            "contributions": contributions,
            "last_commit_date": user.get("last_commit_date") or "",
            "is_owner": user.get("is_owner", False),
            "scores": scores,
            "total_score": scores['total'],
            "match_label": match_label,
            "activity_label": activity_label,
            "contact_icons": " ".join(contact_icons),
            "status": "pending"
        }
    
    def deep_search(
        self,
        queries: List[str],
        jd_keywords: List[str],
        jd_language: str,
        location_filter=None,
        pages: int = 3,
        start_page: int = 1,
        seen_github_ids: Set[str] = None
    ) -> Dict:
        """深度搜索 + 雯姐的专业排序（支持多轮）"""
        if seen_github_ids is None:
            seen_github_ids = set()
        
        print(f"\n[INFO] ===== 开始深度搜索 =====", file=sys.stderr)
        print(f"[INFO] 页数范围: 第 {start_page} 页 ~ 第 {start_page + pages - 1} 页", file=sys.stderr)
        print(f"[INFO] 每页仓库数: 30 个", file=sys.stderr)
        print(f"[INFO] JD 关键词: {jd_keywords}", file=sys.stderr)
        print(f"[INFO] JD 语言: {jd_language}", file=sys.stderr)
        if location_filter:
            print(f"[INFO] 地理位置过滤: {location_filter}", file=sys.stderr)
        if seen_github_ids:
            print(f"[INFO] 已出现过的候选人: {len(seen_github_ids)} 个（将自动过滤）", file=sys.stderr)
        
        all_raw_users = []
        
        for query in queries:
            print(f"\n[INFO] 查询: {query}", file=sys.stderr)
            
            # 跳过前面的页（如果 start_page > 1）
            cursor = None
            current_page = 1
            
            # 先跳到 start_page
            while current_page < start_page:
                _, cursor, has_next_page = self.search_repos_page(query, cursor=cursor, per_page=30)
                if not has_next_page:
                    print(f"[WARN] 已到最后一页（第 {current_page} 页），无法跳到第 {start_page} 页", file=sys.stderr)
                    break
                current_page += 1
                print(f"[DEBUG] 跳过第 {current_page-1} 页（cursor 前进）", file=sys.stderr)
            
            # 开始实际搜索
            for i in range(pages):
                page_number = start_page + i
                repos, next_cursor, has_next_page = self.search_repos_page(query, cursor=cursor, per_page=30)
                
                if not repos:
                    print(f"[WARN] 第 {page_number} 页没有找到仓库，停止搜索", file=sys.stderr)
                    break
                
                users = self.extract_users_from_repos(repos)
                all_raw_users.extend(users)
                
                print(f"[INFO] 第 {page_number} 页提取到 {len(users)} 个用户", file=sys.stderr)
                
                # 更新 cursor 用于下一页
                cursor = next_cursor
                
                # 如果没有下一页了，停止
                if not has_next_page:
                    print(f"[INFO] 已到最后一页（第 {page_number} 页），停止搜索", file=sys.stderr)
                    break
        
        print(f"\n[INFO] ===== 数据处理 =====", file=sys.stderr)
        raw_count = len(all_raw_users)
        print(f"[INFO] 原始用户数: {raw_count}", file=sys.stderr)
        
        # Step 1: 去重
        unique_users = self.deduplicate_users(all_raw_users)
        unique_count = len(unique_users)
        
        # Step 2: 过滤已出现过的候选人（多轮去重）
        if seen_github_ids:
            before_count = len(unique_users)
            unique_users = [u for u in unique_users if u.get('login') not in seen_github_ids]
            print(f"[INFO] 多轮去重: {before_count} → {len(unique_users)} 人（过滤掉 {before_count - len(unique_users)} 个已出现的）", file=sys.stderr)
            unique_count = len(unique_users)
        
        # Step 3: 地理位置过滤（如果指定了 location_filter）
        # 雯姐规则：Remote 自动通过 + 中文判断
        filtered_users = unique_users
        location_filtered_count = unique_count  # 默认等于去重后的数量
        if location_filter:
            before_count = len(filtered_users)
            # 支持 str 或 LocationTarget
            if isinstance(location_filter, str):
                loc_target = resolve_location(location_filter)
            else:
                loc_target = location_filter
            if loc_target:
                filtered_users = self.filter_by_location(filtered_users, loc_target)
            location_filtered_count = len(filtered_users)
            print(f"[INFO] 地理位置过滤: {before_count} → {location_filtered_count} 人", file=sys.stderr)
        
        # Step 4: 批量查询每个候选人的仓库列表
        print(f"\n[INFO] ===== 批量查询候选人仓库（{len(filtered_users)} 人）=====", file=sys.stderr)
        logins = [u.get("login") for u in filtered_users if u.get("login")]
        repos_map = self.fetch_user_repos_batch(logins)
        for user in filtered_users:
            login = user.get("login")
            user['repositories'] = {'nodes': repos_map.get(login, [])}
        
        # Step 5: 评分
        scored_candidates = []
        for user in filtered_users:
            scores = self.calculate_score(user, jd_keywords, jd_language)
            candidate = self.build_candidate_profile(user, scores)
            scored_candidates.append(candidate)
        
        # Step 6: 排序（按总分从高到低）
        sorted_candidates = sorted(scored_candidates, key=lambda x: x['total_score'], reverse=True)
        
        print(f"\n[INFO] ===== 搜索完成 =====", file=sys.stderr)
        print(f"[SUCCESS] 共找到 {len(sorted_candidates)} 个符合条件的候选人", file=sys.stderr)
        
        return {
            "candidates": sorted_candidates,
            "total": len(sorted_candidates),
            "pages_searched": pages,
            "queries": queries,
            "jd_keywords": jd_keywords,
            "jd_language": jd_language,
            # 数据漏斗（雯姐要求：展示过滤过程）
            "raw_count": raw_count,
            "unique_count": unique_count,
            "location_filtered": location_filtered_count
        }


def main():
    parser = argparse.ArgumentParser(description="GitHub Talent Hunter — Repo + User 双搜索引擎")
    parser.add_argument("--queries", nargs="+", help="Repo Search 查询列表（来自 JD Parser）")
    parser.add_argument("--jd-keywords", help="JD 核心关键词（逗号分隔）")
    parser.add_argument("--jd-language", help="JD 主语言（如 C++, Python）")
    parser.add_argument("--jd-title", help="职位名称（用于记录）")
    parser.add_argument("--location", help="地理位置（如 shenzhen, china, singapore）")
    parser.add_argument("--location-strict", action="store_true", help="严格位置匹配（不回落到国家级，仅匹配城市/省份）")
    parser.add_argument("--target", type=int, default=20, help="目标候选人数（默认20）")
    parser.add_argument("--resume", help="继续搜索（传入 search_id）")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--token", help="GitHub Personal Access Token")

    args = parser.parse_args()

    from candidate_manager import CandidateManager
    manager = CandidateManager()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 参数初始化
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    if args.resume:
        # 继续搜索模式
        print(f"[INFO] 继续搜索 (search_id={args.resume})", file=sys.stderr)
        prev = manager.get_search_result(args.resume)
        if not prev:
            print(f"[ERROR] 未找到搜索记录: {args.resume}", file=sys.stderr)
            sys.exit(1)

        search_id = args.resume
        search_params = prev.get("search_params", {})
        repo_queries = search_params.get("repo_queries", prev.get("queries", []))
        jd_keywords = search_params.get("jd_keywords", prev.get("jd_keywords", []))
        jd_language = search_params.get("jd_language", prev.get("jd_language", ""))
        jd_title = prev.get("jd_title", "")
        location_raw = search_params.get("location_raw", prev.get("location_filter"))
        seen_github_ids = set(prev.get("seen_github_ids", []))
        repo_page_offsets = prev.get("repo_page_offsets", {})
        user_page_offsets = prev.get("user_page_offsets", {})
        rounds_searched = prev.get("rounds_searched", 0)

        # 加载已有候选人
        all_candidates = {c["github_id"]: c for c in prev.get("candidates", [])}
        if not seen_github_ids:
            seen_github_ids = set(all_candidates.keys())

        print(f"[INFO] 已有 {len(all_candidates)} 个候选人，{len(seen_github_ids)} 个 seen_ids", file=sys.stderr)
    else:
        # 新搜索
        if not all([args.queries, args.jd_keywords, args.jd_language]):
            print("[ERROR] 新搜索需要 --queries, --jd-keywords, --jd-language", file=sys.stderr)
            sys.exit(1)

        search_id = str(uuid.uuid4())
        repo_queries = args.queries
        jd_keywords = [kw.strip() for kw in args.jd_keywords.split(",")]
        jd_language = args.jd_language
        jd_title = args.jd_title or f"{jd_language} 工程师"
        location_raw = args.location
        seen_github_ids = set()
        repo_page_offsets = {}
        user_page_offsets = {}
        rounds_searched = 0
        all_candidates = {}

        print(f"[INFO] 新搜索 (search_id={search_id})", file=sys.stderr)

    # 解析 location
    location_target = resolve_location(location_raw) if location_raw else None
    location_strict = getattr(args, 'location_strict', False)

    # 自动构建 User Search queries
    user_queries = []
    if location_target:
        locs = build_user_search_locations(location_target)
        lang = jd_language.lower()
        user_queries = [f"language:{lang} location:{loc} followers:>3" for loc in locs[:4]]
        print(f"[INFO] User Search queries: {user_queries}", file=sys.stderr)

    # 初始化搜索引擎
    try:
        hunter = GitHubTalentHunterV3(token=args.token)
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 搜索循环
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    PAGES_PER_ROUND = 3       # 每轮每条 query 搜 3 页 × 100 条 = 300 条
    USER_PAGES_PER_ROUND = 2  # User Search 每轮 2 页
    target = args.target
    zero_rounds = 0
    status = "in_progress"

    # 漏斗统计
    funnel = {
        "raw_from_repos": 0,
        "raw_from_users": 0,
        "after_dedup": 0,
        "after_location_filter": 0,
        "final_scored": 0,
    }

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"🔍 搜索目标: {target} 人 | 语言: {jd_language} | 位置: {location_raw or '不限'}", file=sys.stderr)
    print(f"   Repo queries: {len(repo_queries)} 条 | User queries: {len(user_queries)} 条", file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr)

    while True:
        rounds_searched += 1
        new_raw_users = []
        any_has_more = False

        print(f"\n{'─'*50}", file=sys.stderr)
        print(f"📍 Round {rounds_searched}", file=sys.stderr)
        print(f"{'─'*50}", file=sys.stderr)

        # ── Repo Search ──
        for query in repo_queries:
            start_offset = repo_page_offsets.get(query, 0)
            if start_offset >= 20:  # 20 页 × 50 = 1000（GitHub 硬限制）
                continue

            cursor = None
            # 快进到上次位置
            for skip_i in range(start_offset):
                _, cursor, has_next = hunter.search_repos_page(query, cursor)
                if not has_next:
                    break

            pages_fetched = 0
            for page_i in range(PAGES_PER_ROUND):
                page_num = start_offset + page_i + 1
                if page_num > 20:  # 硬限制 20页×50=1000
                    break
                repos, cursor, has_next = hunter.search_repos_page(query, cursor)
                if not repos:
                    break

                users = hunter.extract_users_from_repos(repos)
                new_raw_users.extend(users)
                funnel["raw_from_repos"] += len(users)
                pages_fetched += 1

                if has_next:
                    any_has_more = True
                if not has_next:
                    break

            repo_page_offsets[query] = start_offset + pages_fetched

        # ── User Search ──
        for query in user_queries:
            start_offset = user_page_offsets.get(query, 0)
            if start_offset >= 10:
                continue

            cursor = None
            for skip_i in range(start_offset):
                _, cursor, has_next = hunter.search_users_page(query, cursor)
                if not has_next:
                    break

            pages_fetched = 0
            for page_i in range(USER_PAGES_PER_ROUND):
                page_num = start_offset + page_i + 1
                if page_num > 10:
                    break
                users, cursor, has_next = hunter.search_users_page(query, cursor)
                if not users:
                    break

                new_raw_users.extend(users)
                funnel["raw_from_users"] += len(users)
                pages_fetched += 1

                if has_next:
                    any_has_more = True
                if not has_next:
                    break

            user_page_offsets[query] = start_offset + pages_fetched

        # ── 去重 + 过滤 + 评分 ──
        deduped = hunter.deduplicate_users(new_raw_users)
        funnel["after_dedup"] += len(deduped)

        # 排除已 seen
        new_only = [u for u in deduped if u.get('login') not in seen_github_ids]
        print(f"[INFO] 新增（排除 seen）: {len(new_only)} 人", file=sys.stderr)

        # Location 过滤
        if location_target:
            before = len(new_only)
            new_only = hunter.filter_by_location(new_only, location_target, strict=location_strict)
            funnel["after_location_filter"] += len(new_only)
        else:
            funnel["after_location_filter"] += len(new_only)

        # 批量查仓库（仅对 Repo Search 来的用户，User Search 已包含）
        needs_repos = [u for u in new_only if u.get('_source') != 'user_search']
        if needs_repos:
            logins = [u['login'] for u in needs_repos if u.get('login')]
            repos_map = hunter.fetch_user_repos_batch(logins)
            for u in needs_repos:
                u['repositories'] = {'nodes': repos_map.get(u.get('login', ''), [])}

        # 批量补充重量级字段（contributionsCollection、pinnedItems、repositoryTopics）
        if new_only:
            hunter.enrich_user_details_batch(new_only)

        # 评分 + 构建 profile
        new_scored = 0
        for u in new_only:
            login = u.get('login')
            if not login:
                continue
            scores = hunter.calculate_score(u, jd_keywords, jd_language)
            candidate = hunter.build_candidate_profile(u, scores)
            if u.get('_location_match_reason'):
                candidate['location_match'] = u['_location_match_reason']
            all_candidates[login] = candidate
            seen_github_ids.add(login)
            new_scored += 1

        funnel["final_scored"] = len(all_candidates)

        print(f"\n📊 本轮新增: {new_scored} 人 | 累计: {len(all_candidates)} / {target}", file=sys.stderr)

        # ── 停止条件 ──
        if len(all_candidates) >= target:
            status = "threshold_reached"
            print(f"\n✅ 达到目标 {len(all_candidates)}/{target}", file=sys.stderr)
            break

        if not any_has_more:
            status = "exhausted"
            print(f"\n⚠️ 搜索结果耗尽，共 {len(all_candidates)} 人", file=sys.stderr)
            break

        if new_scored == 0:
            zero_rounds += 1
            if zero_rounds >= 2:
                status = "zero_yield"
                print(f"\n⚠️ 连续 {zero_rounds} 轮无新增，停止搜索", file=sys.stderr)
                break
        else:
            zero_rounds = 0

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 输出
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    sorted_candidates = sorted(all_candidates.values(), key=lambda x: x.get('total_score', 0), reverse=True)

    result = {
        "search_id": search_id,
        "jd_title": jd_title,
        "status": status,
        "candidates": sorted_candidates,
        "total": len(sorted_candidates),
        "target": target,
        "has_more": any_has_more,
        "rounds_searched": rounds_searched,
        "funnel": funnel,
        "search_params": {
            "repo_queries": repo_queries,
            "user_queries": user_queries,
            "jd_keywords": jd_keywords,
            "jd_language": jd_language,
            "location_raw": location_raw,
        },
    }

    # 保存到 candidate_manager
    manager.save_search_result(
        search_id=search_id,
        jd_title=jd_title,
        queries=repo_queries,
        location_filter=location_raw,
        candidates=sorted_candidates,
        search_params=result["search_params"],
        seen_github_ids=list(seen_github_ids),
        repo_page_offsets=repo_page_offsets,
        user_page_offsets=user_page_offsets,
        rounds_searched=rounds_searched,
        status=status,
    )

    # 输出 JSON
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n📁 结果已保存: {args.output}", file=sys.stderr)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # 打印漏斗摘要
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"📊 搜索漏斗", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    print(f"  Repo Search 原始: {funnel['raw_from_repos']} 人", file=sys.stderr)
    print(f"  User Search 原始: {funnel['raw_from_users']} 人", file=sys.stderr)
    print(f"  去重后: {funnel['after_dedup']} 人", file=sys.stderr)
    print(f"  Location 过滤后: {funnel['after_location_filter']} 人", file=sys.stderr)
    print(f"  最终结果: {funnel['final_scored']} 人", file=sys.stderr)
    print(f"  状态: {status}", file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr)


if __name__ == "__main__":
    main()
