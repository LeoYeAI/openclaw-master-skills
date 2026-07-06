#!/usr/bin/env python3
"""
云比赛网数据查询工具 - 带性能跟踪
支持：比赛列表、分组信息、对阵数据、排名计算
"""

import requests
import json
import time
import sys
import html
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PerfTimer:
    """性能计时器"""
    name: str
    start_time: float = field(default_factory=time.perf_counter)
    end_time: Optional[float] = None
    
    def stop(self) -> float:
        """停止计时并返回耗时（秒）"""
        self.end_time = time.perf_counter()
        return self.elapsed()
    
    def elapsed(self) -> float:
        """获取已耗时（秒）"""
        end = self.end_time or time.perf_counter()
        return end - self.start_time


@dataclass
class PerfReport:
    """性能报告"""
    timers: List[PerfTimer] = field(default_factory=list)
    total_start: float = field(default_factory=time.perf_counter)
    
    def start(self, name: str) -> PerfTimer:
        """开始一个新的计时器"""
        timer = PerfTimer(name)
        self.timers.append(timer)
        return timer
    
    def summary(self) -> str:
        """生成性能报告摘要"""
        total_elapsed = time.perf_counter() - self.total_start
        step_total = sum(t.elapsed() for t in self.timers)
        
        lines = [
            "\n" + "=" * 50,
            "⏱️  性能计时报告",
            "=" * 50,
        ]
        
        for timer in self.timers:
            elapsed = timer.elapsed()
            percentage = (elapsed / total_elapsed * 100) if total_elapsed > 0 else 0
            lines.append(f"  {timer.name:25} : {elapsed:8.3f}s ({percentage:5.1f}%)")
        
        lines.extend([
            "-" * 50,
            f"  {'步骤累计':25} : {step_total:8.3f}s",
            f"  {'总耗时':25} : {total_elapsed:8.3f}s",
            "=" * 50,
        ])
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """转为字典格式"""
        total_elapsed = time.perf_counter() - self.total_start
        return {
            "total_seconds": round(total_elapsed, 3),
            "steps": [
                {"name": t.name, "seconds": round(t.elapsed(), 3)}
                for t in self.timers
            ]
        }


class YunbisaiClient:
    """云比赛网 API 客户端（带性能跟踪）"""
    
    BASE_URL = "https://data-center.yunbisai.com/api"
    OPEN_URL = "https://open.yunbisai.com/api"
    API_URL = "https://api.yunbisai.com"
    
    def __init__(self, verbose: bool = True):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.yunbisai.com/"
        })
        self.verbose = verbose
        self.perf = PerfReport()
    
    def _log(self, msg: str):
        """打印日志"""
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    def _request(self, url: str, params: Dict = None) -> Dict:
        """发送请求并返回JSON"""
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def get_events(self, area: str = "广东省", month: int = 1, 
                   event_type: int = 2, page_size: int = 100, 
                   keyword: str = None, search_all: bool = True) -> Tuple[List[Dict], Dict]:
        """
        获取比赛列表
        
        Args:
            area: 地区名称
            month: 最近多少个月
            event_type: 赛事类型 (2=围棋)
            page_size: 每页数量 (默认100，最大200)
            keyword: 关键词过滤 (在标题/城市中搜索)
            search_all: 是否搜索所有页 (默认True)
        
        Returns:
            (events_list, perf_info)
        """
        timer = self.perf.start("获取比赛列表")
        keyword_hint = f", keyword={keyword}" if keyword else ""
        self._log(f"正在获取比赛列表: area={area}, month={month}{keyword_hint}")
        
        all_events = []
        matched_events = []
        page = 1
        total_pages = 1
        api_calls = 0
        
        while page <= total_pages:
            url = f"{self.BASE_URL}/lswl-events"
            params = {
                "page": page,
                "eventType": event_type,
                "month": month,
                "areaNum": area,
                "PageSize": min(page_size, 200)  # API限制最大200
            }
            
            try:
                data = self._request(url, params)
                api_calls += 1
                # 处理两种返回格式：带areaNum时返回{rows: []}，不带时返回{datArr: {rows: []}}
                if data.get("error") == 0 or "datArr" in data or "rows" in data:
                    rows = data.get("datArr", {}).get("rows") if "datArr" in data else data.get("rows", [])
                    all_events.extend(rows)
                    
                    # 如果有关键词，实时过滤并检查是否可以提前退出
                    if keyword:
                        for row in rows:
                            title = row.get('title', '')
                            city = row.get('city_name', '')
                            if keyword in title or keyword in city:
                                matched_events.append(row)
                        
                        # 如果找到了匹配项且不需要全部数据，可以提前退出
                        if matched_events and not search_all:
                            self._log(f"  ✓ 第 {page} 页找到匹配项，提前结束搜索")
                            break
                    
                    # 处理两种返回格式
                    total_pages = data.get("datArr", {}).get("TotalPage", 1) if "datArr" in data else data.get("TotalPage", 1)
                    progress = f" ({len(matched_events)} 匹配)" if keyword and matched_events else ""
                    self._log(f"  获取第 {page}/{total_pages} 页，本页 {len(rows)} 条数据{progress}")
                    
                    if page >= total_pages:
                        break
                    page += 1
                else:
                    break
            except Exception as e:
                self._log(f"  请求失败: {e}")
                break
        
        elapsed = timer.stop()
        result_events = matched_events if keyword else all_events
        search_info = f" (搜索了 {api_calls} 页)" if api_calls > 1 else ""
        self._log(f"✓ 共获取 {len(result_events)} 场比赛{search_info}，耗时 {elapsed:.3f}s")
        
        return result_events, {"count": len(result_events), "seconds": round(elapsed, 3), "api_calls": api_calls}
    
    def get_groups_from_html(self, event_id: int) -> List[Dict]:
        """
        从 HTML 页面解析分组信息（API 403 时的备用方案）
        
        Returns:
            groups_list
        """
        url = f"https://www.yunbisai.com/tpl/eventFeatures/eventDetail-{event_id}.html"
        self._log(f"  尝试从 HTML 解析分组: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            content = response.text
            
            # 解析 HTML 中的分组数据
            # 格式1: <li data-groupname="..."><a ... data-groupid="...">
            # 格式2: <a ... data-groupname="..." data-groupid="...">
            import re
            groups = []
            
            # 查找所有分组条目（支持两种格式）
            # 格式1: li 标签上有 groupname，a 标签上有 groupid
            # 注意：正则返回 (groupname, groupid)
            pattern1 = r'<li[^>]*data-groupname="([^"]+)"[^>]*>[^<]*<a[^>]*data-groupid="(\d+)"'
            matches1 = re.findall(pattern1, content, re.DOTALL)
            
            # 格式2: a 标签上同时有 groupname 和 groupid
            pattern2 = r'<a[^>]*data-groupname="([^"]+)"[^>]*data-groupid="(\d+)"'
            matches2 = re.findall(pattern2, content, re.DOTALL)
            
            matches = matches1 + matches2
            
            # 去重（可能会有重复）
            seen = set()
            for group_name, group_id in matches:
                if group_id not in seen:
                    seen.add(group_id)
                    groups.append({
                        "group_id": int(group_id),
                        "groupname": group_name.strip(),
                        "event_id": event_id
                    })
            
            if groups:
                self._log(f"  ✓ 从 HTML 解析到 {len(groups)} 个分组")
                return groups
            else:
                self._log(f"  未从 HTML 中找到分组数据")
                return []
        except Exception as e:
            self._log(f"  HTML 解析失败: {e}")
            return []
    
    def get_groups(self, event_id: int) -> Tuple[List[Dict], Dict]:
        """
        获取比赛分组信息（支持 API 和 HTML 双模式）
        
        Returns:
            (groups_list, perf_info)
        """
        timer = self.perf.start("获取分组信息")
        self._log(f"正在获取比赛分组: event_id={event_id}")
        
        url = f"{self.OPEN_URL}/event/feel/list"
        params = {
            "event_id": event_id,
            "page": 1,
            "pagesize": 500
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            # 如果返回 403，尝试从 HTML 解析
            if response.status_code == 403:
                self._log(f"  API 返回 403，尝试从 HTML 页面解析...")
                groups = self.get_groups_from_html(event_id)
                elapsed = timer.stop()
                return groups, {"count": len(groups), "seconds": round(elapsed, 3), "source": "html"}
            
            response.raise_for_status()
            data = response.json()
            
            if data.get("error") == 0:
                rows = data.get("datArr", {}).get("rows", [])
                elapsed = timer.stop()
                self._log(f"✓ 共获取 {len(rows)} 个分组，耗时 {elapsed:.3f}s")
                return rows, {"count": len(rows), "seconds": round(elapsed, 3), "source": "api"}
        except Exception as e:
            self._log(f"  API 请求失败: {e}")
            # API 失败，尝试 HTML
            self._log(f"  尝试从 HTML 页面解析...")
            groups = self.get_groups_from_html(event_id)
            elapsed = timer.stop()
            return groups, {"count": len(groups), "seconds": round(elapsed, 3), "source": "html"}
        
        elapsed = timer.stop()
        return [], {"count": 0, "seconds": round(elapsed, 3)}
    
    def get_group_players(self, event_id: int, group_id: int) -> Tuple[List[Dict], Dict]:
        """
        获取分组选手列表
        
        Returns:
            (players_list, perf_info)
        """
        timer = self.perf.start("获取分组选手")
        self._log(f"正在获取分组选手: event_id={event_id}, group_id={group_id}")
        
        url = f"{self.OPEN_URL}/event/feel/list"
        params = {
            "event_id": event_id,
            "group_id": group_id,
            "page": 1,
            "pagesize": 200
        }
        
        try:
            data = self._request(url, params)
            if data.get("error") == 0:
                rows = data.get("datArr", {}).get("rows", [])
                elapsed = timer.stop()
                self._log(f"✓ 共获取 {len(rows)} 名选手，耗时 {elapsed:.3f}s")
                return rows, {"count": len(rows), "seconds": round(elapsed, 3)}
        except Exception as e:
            self._log(f"  请求失败: {e}")
        
        elapsed = timer.stop()
        return [], {"count": 0, "seconds": round(elapsed, 3)}
    
    def get_against_plan(self, group_id: int, bout: int) -> Tuple[Optional[Dict], Dict]:
        """
        获取某轮对阵表
        
        Returns:
            (match_data, perf_info)
        """
        timer = self.perf.start(f"获取第{bout}轮对阵")
        
        url = f"{self.API_URL}/request/Group/Againstplan"
        params = {"groupid": group_id, "bout": bout}
        
        try:
            data = self._request(url, params)
            if data.get("error") == 0:
                timer.stop()
                return data.get("datArr", {}), {"seconds": round(timer.elapsed(), 3)}
        except Exception as e:
            self._log(f"  请求失败: {e}")
        
        timer.stop()
        return None, {"seconds": round(timer.elapsed(), 3)}
    
    def get_all_rounds(self, group_id: int) -> Tuple[List[Dict], int, Dict]:
        """
        获取分组所有轮次对阵
        
        Returns:
            (all_matches, total_bouts, perf_info)
        """
        timer = self.perf.start("获取所有轮次对阵")
        self._log(f"正在获取分组所有轮次对阵: group_id={group_id}")
        
        all_matches = []
        
        # 先获取第1轮，得到总轮数
        first_round, _ = self.get_against_plan(group_id, 1)
        if not first_round:
            elapsed = timer.stop()
            return [], 0, {"count": 0, "seconds": round(elapsed, 3)}
        
        total_bouts = int(first_round.get("total_bout", 0) or 0)
        # 为第1轮的对局添加轮次信息
        first_rows = first_round.get("rows", [])
        for row in first_rows:
            row['bout'] = 1
        all_matches.extend(first_rows)
        
        self._log(f"  总轮数: {total_bouts}")
        
        # 获取剩余轮次
        completed_rounds = 1  # 第1轮已添加
        for bout in range(2, total_bouts + 1):
            round_data, _ = self.get_against_plan(group_id, bout)
            if not round_data:
                break
            
            rows = round_data.get("rows", [])
            
            # 检查该轮是否已经完成（不是所有对局的 p1_score 和 p2_score 都是 0.0）
            is_round_completed = any(
                float(m.get('p1_score') or 0) != 0.0 or float(m.get('p2_score') or 0) != 0.0
                for m in rows
            )
            
            if not is_round_completed:
                self._log(f"  第 {bout} 轮尚未完成，停止获取")
                break
            
            # 为该轮的对局添加轮次信息
            for row in rows:
                row['bout'] = bout
            all_matches.extend(rows)
            completed_rounds += 1
        
        elapsed = timer.stop()
        self._log(f"✓ 共获取 {len(all_matches)} 场对局（{completed_rounds}/{total_bouts}轮），耗时 {elapsed:.3f}s")
        
        return all_matches, completed_rounds, {"count": len(all_matches), "rounds": completed_rounds, "total_rounds": total_bouts, "seconds": round(elapsed, 3)}
    
    def calculate_ranking(self, matches: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        根据对阵数据计算排名
        
        Returns:
            (rankings, perf_info)
        """
        timer = self.perf.start("计算排名")
        self._log("正在计算排名...")
        
        players = {}
        
        # 初始化选手
        for match in matches:
            for key, name_key, team_key in [
                ('p1id', 'p1', 'p1_teamname'),
                ('p2id', 'p2', 'p2_teamname')
            ]:
                pid = match.get(key)
                name = match.get(name_key)
                team = match.get(team_key) or ''
                if pid and name and pid not in players:
                    players[pid] = {
                        'id': pid,
                        'name': name,
                        'team': team,
                        'wins': 0,
                        'losses': 0,
                        'draws': 0,
                        'score': 0,
                        'opponents': [],
                        'progressive': [],
                        'games': []  # 存储每轮对局详情
                    }
        
        # 逐轮解析
        for match in matches:
            p1_id = match.get('p1id')
            p2_id = match.get('p2id')
            p1_name = match.get('p1', '')
            p2_name = match.get('p2', '')
            p1_score = float(match.get('p1_score') or 0)
            p2_score = float(match.get('p2_score') or 0)
            bout = match.get('bout', 0)  # 轮次
            
            # 处理p1
            if p1_id and p1_id in players:
                if p2_id and p2_name and p2_id in players:
                    players[p1_id]['opponents'].append(p2_id)
                if p1_score == 2.0:
                    players[p1_id]['wins'] += 1
                    result = '胜'
                elif p1_score == 0.0:
                    players[p1_id]['losses'] += 1
                    result = '负'
                else:
                    players[p1_id]['draws'] += 1
                    result = '和'
                players[p1_id]['score'] += p1_score
                players[p1_id]['progressive'].append(players[p1_id]['score'])
                # 记录对局详情
                players[p1_id]['games'].append({
                    'round': bout,
                    'opponent': p2_name or '轮空',
                    'result': result,
                    'score': p1_score
                })
            
            # 处理p2
            if p2_id and p2_id in players:
                if p1_id and p1_name and p1_id in players:
                    players[p2_id]['opponents'].append(p1_id)
                if p2_score == 2.0:
                    players[p2_id]['wins'] += 1
                    result = '胜'
                elif p2_score == 0.0:
                    players[p2_id]['losses'] += 1
                    result = '负'
                else:
                    players[p2_id]['draws'] += 1
                    result = '和'
                players[p2_id]['score'] += p2_score
                players[p2_id]['progressive'].append(players[p2_id]['score'])
                # 记录对局详情
                players[p2_id]['games'].append({
                    'round': bout,
                    'opponent': p1_name or '轮空',
                    'result': result,
                    'score': p2_score
                })
        
        # 计算对手分和累进分
        for pid, p in players.items():
            p['opponent_score'] = sum(
                players[oid]['score'] for oid in p['opponents'] if oid in players
            )
            p['progressive_score'] = sum(p['progressive'])
        
        # 排序：个人积分 > 对手分 > 累进分
        sorted_players = sorted(
            players.values(),
            key=lambda x: (x['score'], x['opponent_score'], x['progressive_score']),
            reverse=True
        )
        
        elapsed = timer.stop()
        self._log(f"✓ 排名计算完成（{len(sorted_players)}名选手），耗时 {elapsed:.3f}s")
        
        return sorted_players, {"count": len(sorted_players), "seconds": round(elapsed, 3)}
    
    def print_ranking(self, rankings: List[Dict], top_n: int = None, output_file: str = None):
        """打印排名表 - 智能格式：≤10行用单行格式，>10行输出HTML文件+显示前10名预览"""
        rankings_to_print = rankings[:top_n] if top_n else rankings
        total = len(rankings_to_print)
        
        if total <= 10:
            # 单行 Markdown 格式
            print("\n📋 排名列表\n")
            for i, p in enumerate(rankings_to_print, 1):
                record = f"{p['wins']}胜{p['losses']}负"
                if p['draws'] > 0:
                    record += f"{p['draws']}和"
                print(f"{i}. **{p['name']}** | 积分: {int(p['score'])} | 对手分: {int(p['opponent_score'])} | 累进分: {int(p['progressive_score'])} | {record}")
            print()
        else:
            # HTML 格式输出到文件（手机端优化）
            html_path = output_file or f"/tmp/ranking_{int(time.time())}.html"
            html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>排名表</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background: #f5f5f5; line-height: 1.6; }}
        .container {{ max-width: 100%; margin: 0 auto; background: white; min-height: 100vh; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px 16px; text-align: center; }}
        .header h1 {{ font-size: 22px; margin-bottom: 8px; font-weight: 600; }}
        .header .subtitle {{ font-size: 14px; opacity: 0.9; }}
        .stats {{ display: flex; justify-content: center; gap: 30px; padding: 15px; background: #f8f9fa; border-bottom: 1px solid #eee; }}
        .stat {{ text-align: center; }}
        .stat-value {{ font-size: 20px; font-weight: bold; color: #667eea; }}
        .stat-label {{ font-size: 12px; color: #666; margin-top: 2px; }}
        .list {{ padding: 0; }}
        .item {{ display: flex; align-items: center; padding: 12px 16px; border-bottom: 1px solid #f0f0f0; background: white; }}
        .item:nth-child(even) {{ background: #fafafa; }}
        .rank {{ width: 44px; text-align: center; font-size: 14px; font-weight: bold; color: #999; flex-shrink: 0; }}
        .rank.gold {{ color: #d4af37; font-size: 13px; }}
        .rank.silver {{ color: #c0c0c0; font-size: 13px; }}
        .rank.bronze {{ color: #cd7f32; font-size: 13px; }}
        .info {{ flex: 1; margin-left: 12px; min-width: 0; }}
        .name {{ font-size: 16px; font-weight: 600; color: #333; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .details {{ font-size: 13px; color: #666; display: flex; gap: 12px; flex-wrap: wrap; }}
        .score {{ font-weight: bold; color: #e74c3c; }}
        .item {{ cursor: pointer; }}
        .item:active {{ background: #f0f0f0; }}
        .games-detail {{ display: none; padding: 10px 16px; background: #f8f9fa; border-bottom: 1px solid #e0e0e0; }}
        .games-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        .games-table th {{ background: #667eea; color: white; padding: 6px; text-align: center; }}
        .games-table td {{ padding: 6px; border-bottom: 1px solid #eee; text-align: center; }}
        .games-table tr:nth-child(even) {{ background: #f0f0f0; }}
        @media (max-width: 375px) {{
            .header h1 {{ font-size: 20px; }}
            .name {{ font-size: 15px; }}
            .details {{ font-size: 12px; gap: 8px; }}
            .rank {{ width: 35px; font-size: 15px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏆 比赛排名</h1>
            <div class="subtitle">5段及以上组</div>
        </div>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{total}</div>
                <div class="stat-label">参赛人数</div>
            </div>
            <div class="stat">
                <div class="stat-value">8</div>
                <div class="stat-label">比赛轮次</div>
            </div>
        </div>
        <div class="list">
'''
            for i, p in enumerate(rankings_to_print, 1):
                record = f"{p['wins']}胜{p['losses']}负"
                if p['draws'] > 0:
                    record += f"{p['draws']}和"
                rank_class = 'rank'
                if i == 1:
                    rank_class += ' gold'
                    rank_text = '🥇'
                elif i == 2:
                    rank_class += ' silver'
                    rank_text = '🥈'
                elif i == 3:
                    rank_class += ' bronze'
                    rank_text = '🥉'
                else:
                    rank_text = str(i)
                
                # 构建对局详情HTML
                games_html = '<div class="games-detail" id="games-' + str(i) + '">'
                games_html += '<table class="games-table">'
                games_html += '<tr><th>轮次</th><th>对手</th><th>结果</th></tr>'
                for game in sorted(p.get('games', []), key=lambda x: x.get('round', 0)):
                    games_html += f"<tr><td>第{game.get('round', '-')}轮</td><td>{html.escape(str(game.get('opponent', '-')))}</td><td>{game.get('result', '-')}</td></tr>"
                games_html += '</table></div>'
                
                html_content += f'''            <div class="item" onclick="toggleGames({i})">
                <div class="{rank_class}">{rank_text}</div>
                <div class="info">
                    <div class="name">{html.escape(str(p['name']))}</div>
                    <div class="details">
                        <span class="score">积分 {int(p['score'])}</span>
                        <span>对手分 {int(p['opponent_score'])}</span>
                        <span>累进分 {int(p['progressive_score'])}</span>
                        <span>{html.escape(record)}</span>
                    </div>
                </div>
            </div>
            {games_html}
'''
            html_content += '''        </div>
    </div>
    <script>
        function toggleGames(idx) {
            var detail = document.getElementById('games-' + idx);
            if (detail.style.display === 'block') {
                detail.style.display = 'none';
            } else {
                // 先关闭所有其他详情
                var allDetails = document.querySelectorAll('.games-detail');
                allDetails.forEach(function(d) { d.style.display = 'none'; });
                detail.style.display = 'block';
            }
        }
    </script>
</body>
</html>'''
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"\n📊 排名数据已导出到 HTML 文件: {html_path}")
            print(f"   共 {total} 条记录\n")
            
            # 显示前10名预览
            print("📋 前10名预览:\n")
            for i, p in enumerate(rankings_to_print[:10], 1):
                record = f"{p['wins']}胜{p['losses']}负"
                if p['draws'] > 0:
                    record += f"{p['draws']}和"
                print(f"{i}. **{p['name']}** | 积分: {int(p['score'])} | 对手分: {int(p['opponent_score'])} | 累进分: {int(p['progressive_score'])} | {record}")
            print(f"\n... 还有 {total - 10} 名选手\n")
    
    def print_perf_report(self):
        """打印性能报告"""
        print(self.perf.summary())
    
    def get_perf_dict(self) -> Dict:
        """获取性能数据字典"""
        return self.perf.to_dict()


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='云比赛网数据查询工具')
    parser.add_argument('--event-id', '-e', type=int, help='比赛ID')
    parser.add_argument('--group-id', '-g', type=int, help='分组ID')
    parser.add_argument('--area', '-a', default='广东省', help='地区（默认：广东省）')
    parser.add_argument('--month', '-m', type=int, default=1, help='最近多少个月（默认：1）')
    parser.add_argument('--keyword', '-k', help='关键词过滤（在标题/城市中搜索）')
    parser.add_argument('--page-size', '-p', type=int, default=100, help='每页数量（默认：100，最大200）')
    parser.add_argument('--limit', '-l', type=int, help='限制显示条数（≤15时用单行格式）')
    parser.add_argument('--ranking', '-r', action='store_true', help='计算排名')
    parser.add_argument('--matchups', '-u', type=int, help='查询第N轮对阵表')
    parser.add_argument('--json', '-j', action='store_true', help='输出JSON格式')
    parser.add_argument('--quiet', '-q', action='store_true', help='静默模式（减少输出）')
    
    args = parser.parse_args()
    
    client = YunbisaiClient(verbose=not args.quiet)
    result = {"status": "ok", "data": {}}
    
    try:
        # 查询比赛列表
        if not args.event_id:
            events, perf = client.get_events(
                area=args.area, 
                month=args.month,
                page_size=args.page_size,
                keyword=args.keyword
            )
            result["data"]["events"] = events
            result["data"]["_perf"] = perf
            
            if not args.json:
                total_events = len(events)
                display_events = events[:args.limit] if args.limit else events
                display_count = len(display_events)
                
                if display_count <= 10:
                    # 单行 Markdown 格式
                    limit_hint = f" (前{display_count}场)" if args.limit and total_events > display_count else ""
                    print(f"\n📋 找到 {total_events} 场比赛{limit_hint}\n")
                    for e in display_events:
                        event_id = e.get('event_id')
                        title = e.get('title')
                        city = e.get('city_name')
                        date = e.get('max_time', '')[:10]
                        print(f"• [{event_id}] **{title}** | 城市: {city} | 日期: {date}")
                    if args.limit and total_events > display_count:
                        print(f"\n... 还有 {total_events - display_count} 场")
                    print()
                else:
                    # HTML 格式输出到文件（手机端优化）
                    html_path = f"/tmp/events_{int(time.time())}.html"
                    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>比赛列表</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background: #f5f5f5; line-height: 1.6; }}
        .container {{ max-width: 100%; margin: 0 auto; background: white; min-height: 100vh; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px 16px; text-align: center; position: sticky; top: 0; z-index: 100; }}
        .header h1 {{ font-size: 22px; margin-bottom: 8px; font-weight: 600; }}
        .header .subtitle {{ font-size: 14px; opacity: 0.9; }}
        .list {{ padding: 0; }}
        .item {{ display: block; padding: 16px; border-bottom: 1px solid #f0f0f0; background: white; text-decoration: none; color: inherit; }}
        .item:active {{ background: #f5f5f5; }}
        .title {{ font-size: 16px; font-weight: 600; color: #333; margin-bottom: 8px; line-height: 1.4; }}
        .meta {{ display: flex; gap: 16px; font-size: 13px; color: #666; flex-wrap: wrap; }}
        .meta span {{ display: flex; align-items: center; gap: 4px; }}
        .city {{ color: #667eea; font-weight: 500; }}
        .date {{ color: #27ae60; }}
        .id {{ color: #999; font-family: monospace; font-size: 12px; }}
        .empty {{ text-align: center; padding: 60px 20px; color: #999; }}
        @media (max-width: 375px) {{
            .header h1 {{ font-size: 20px; }}
            .title {{ font-size: 15px; }}
            .meta {{ gap: 12px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏆 围棋比赛列表</h1>
            <div class="subtitle">共 {total_events} 场比赛</div>
        </div>
        <div class="list">
'''
                    for e in events:
                        event_id = e.get('event_id')
                        title = html.escape(str(e.get('title', '')))
                        city = html.escape(str(e.get('city_name', '')))
                        date = html.escape(str(e.get('max_time', ''))[:10])
                        players = e.get('play_num') or '-'
                        html_content += f'''            <div class="item">
                <div class="title">{title}</div>
                <div class="meta">
                    <span class="city">📍 {city}</span>
                    <span class="date">📅 {date}</span>
                    <span class="id">ID: {event_id}</span>
                </div>
            </div>
'''
                    html_content += '''        </div>
    </div>
</body>
</html>'''
                    
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    print(f"\n📊 比赛列表已导出到 HTML 文件: {html_path}")
                    print(f"   共 {total_events} 场比赛\n")
                    
                    # 显示前10条预览
                    print("📋 前10场预览:\n")
                    for e in events[:10]:
                        event_id = e.get('event_id')
                        title = e.get('title')
                        city = e.get('city_name')
                        date = e.get('max_time', '')[:10]
                        print(f"• [{event_id}] **{title}** | 城市: {city} | 日期: {date}")
                    print(f"\n... 还有 {total_events - 10} 场比赛\n")
        
        # 查询分组
        elif args.event_id and not args.group_id:
            groups, perf = client.get_groups(args.event_id)
            result["data"]["groups"] = groups
            result["data"]["_perf"] = perf
            
            if not args.json:
                total_groups = len(groups)
                if total_groups <= 10:
                    # 单行 Markdown 格式
                    print(f"\n📋 比赛 {args.event_id} 共有 {total_groups} 个分组\n")
                    for g in groups:
                        group_id = g.get('group_id')
                        group_name = g.get('groupname')
                        print(f"• [{group_id}] **{group_name}**")
                    print()
                else:
                    # 尝试从第一轮对阵表计算人数
                    group_counts = {}
                    for g in groups:
                        gid = g.get('group_id')
                        try:
                            match_data, _ = client.get_against_plan(gid, 1)
                            if match_data:
                                rows = match_data.get('rows', [])
                                # 计算实际参赛人数（处理轮空情况）
                                count = 0
                                for m in rows:
                                    if m.get('p1'):
                                        count += 1
                                    if m.get('p2'):
                                        count += 1
                                group_counts[gid] = count
                        except:
                            pass
                    
                    # HTML 格式输出到文件（手机端优化）
                    html_path = f"/tmp/groups_{int(time.time())}.html"
                    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>分组列表</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background: #f5f5f5; line-height: 1.6; }}
        .container {{ max-width: 100%; margin: 0 auto; background: white; min-height: 100vh; }}
        .header {{ background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); color: white; padding: 20px 16px; text-align: center; position: sticky; top: 0; z-index: 100; }}
        .header h1 {{ font-size: 22px; margin-bottom: 8px; font-weight: 600; }}
        .header .subtitle {{ font-size: 14px; opacity: 0.9; }}
        .list {{ padding: 0; }}
        .item {{ display: flex; align-items: center; padding: 14px 16px; border-bottom: 1px solid #f0f0f0; background: white; }}
        .item:nth-child(even) {{ background: #fafafa; }}
        .group-num {{ width: 32px; height: 32px; background: #e8f5e9; color: #27ae60; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 13px; flex-shrink: 0; }}
        .info {{ flex: 1; margin-left: 12px; min-width: 0; }}
        .group-name {{ font-size: 15px; font-weight: 500; color: #333; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 2px; }}
        .meta {{ font-size: 12px; color: #999; display: flex; gap: 12px; }}
        .count {{ color: #27ae60; font-weight: 500; }}
        @media (max-width: 375px) {{
            .header h1 {{ font-size: 20px; }}
            .group-name {{ font-size: 15px; }}
            .group-num {{ width: 36px; height: 36px; font-size: 13px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 比赛分组</h1>
            <div class="subtitle">共 {total_groups} 个分组</div>
        </div>
        <div class="list">
'''
                    for i, g in enumerate(groups, 1):
                        group_id = g.get('group_id')
                        group_name = html.escape(str(g.get('groupname', '')))
                        # 优先使用从对阵表计算的人数
                        players_count = group_counts.get(group_id, g.get('playernum') or g.get('participant_count') or '-')
                        html_content += f'''            <div class="item">
                <div class="group-num">{i}</div>
                <div class="info">
                    <div class="group-name">{group_name}</div>
                    <div class="meta">
                        <span>ID: {group_id}</span>
                        <span class="count">👥 {players_count}人</span>
                    </div>
                </div>
            </div>
'''
                    html_content += '''        </div>
    </div>
</body>
</html>'''
                    
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    print(f"\n📊 分组列表已导出到 HTML 文件: {html_path}")
                    print(f"   共 {total_groups} 个分组\n")
                    
                    # 显示前10条预览
                    print("📋 前10个分组预览:\n")
                    for g in groups[:10]:
                        group_id = g.get('group_id')
                        group_name = g.get('groupname')
                        print(f"• [{group_id}] **{group_name}**")
                    print(f"\n... 还有 {total_groups - 10} 个分组\n")
        
        # 查询对阵并计算排名
        elif args.group_id:
            if args.matchups:
                # 查询指定轮次对阵表
                match_data, perf = client.get_against_plan(args.group_id, args.matchups)
                result["data"]["matchups"] = match_data
                result["data"]["_perf"] = perf
                
                if not args.json and match_data:
                    rows = match_data.get('rows', [])
                    total_bouts = match_data.get('total_bout', 0)
                    total_matches = len(rows)
                    
                    if total_matches <= 10:
                        # 单行 Markdown 格式
                        print(f"\n📋 第{args.matchups}轮对阵表 (共{total_matches}台)\n")
                        for m in rows:
                            p1 = m.get('p1') or '轮空'
                            p2 = m.get('p2') or '轮空'
                            seat = m.get('seatnum')
                            print(f"台{seat}: {p1} vs {p2}")
                        print()
                    else:
                        # HTML 格式输出到文件（手机端优化）
                        html_path = f"/tmp/matchups_{int(time.time())}.html"
                        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>第{args.matchups}轮对阵表</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background: #f5f5f5; line-height: 1.6; }}
        .container {{ max-width: 100%; margin: 0 auto; background: white; min-height: 100vh; }}
        .header {{ background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%); color: white; padding: 20px 16px; text-align: center; position: sticky; top: 0; z-index: 100; }}
        .header h1 {{ font-size: 22px; margin-bottom: 8px; font-weight: 600; }}
        .header .subtitle {{ font-size: 14px; opacity: 0.9; }}
        .stats {{ display: flex; justify-content: center; gap: 30px; padding: 15px; background: #f8f9fa; border-bottom: 1px solid #eee; }}
        .stat {{ text-align: center; }}
        .stat-value {{ font-size: 20px; font-weight: bold; color: #ff6b6b; }}
        .stat-label {{ font-size: 12px; color: #666; margin-top: 2px; }}
        .list {{ padding: 0; }}
        .item {{ display: flex; align-items: center; padding: 14px 16px; border-bottom: 1px solid #f0f0f0; background: white; }}
        .item:nth-child(even) {{ background: #fafafa; }}
        .table-num {{ width: 44px; text-align: center; font-size: 13px; color: #999; flex-shrink: 0; }}
        .table-num .num {{ font-size: 18px; font-weight: bold; color: #ff6b6b; }}
        .match {{ flex: 1; margin: 0 12px; min-width: 0; }}
        .player {{ font-size: 15px; font-weight: 500; color: #333; padding: 4px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .player.black::before {{ content: "⚫ "; }}
        .player.white::before {{ content: "⚪ "; }}
        .vs {{ font-size: 12px; color: #ccc; text-align: center; padding: 2px 0; }}
        .result {{ width: 50px; text-align: center; font-size: 14px; font-weight: bold; flex-shrink: 0; }}
        .result.win {{ color: #27ae60; }}
        .result.loss {{ color: #e74c3c; }}
        .result.pending {{ color: #999; }}
        @media (max-width: 375px) {{
            .header h1 {{ font-size: 20px; }}
            .player {{ font-size: 14px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚔️ 第{args.matchups}轮对阵表</h1>
            <div class="subtitle">分组ID: {args.group_id}</div>
        </div>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{total_matches}</div>
                <div class="stat-label">对局数</div>
            </div>
            <div class="stat">
                <div class="stat-value">{total_bouts}</div>
                <div class="stat-label">总轮次</div>
            </div>
        </div>
        <div class="list">
'''
                        for m in rows:
                            seat = m.get('seatnum')
                            p1 = html.escape(str(m.get('p1') or '轮空'))
                            p2 = html.escape(str(m.get('p2') or '轮空'))
                            score1 = m.get('p1_score')
                            score2 = m.get('p2_score')

                            if score1 is None or score2 is None:
                                result_text = '未开始'
                                result_class = 'pending'
                            else:
                                s1 = int(float(score1))
                                s2 = int(float(score2))
                                if s1 > s2:
                                    result_text = '黑胜'
                                    result_class = 'win'
                                elif s2 > s1:
                                    result_text = '白胜'
                                    result_class = 'loss'
                                else:
                                    result_text = '平局'
                                    result_class = 'pending'

                            html_content += f'''            <div class="item">
                <div class="table-num"><div class="num">{seat}</div>台</div>
                <div class="match">
                    <div class="player black">{p1}</div>
                    <div class="vs">VS</div>
                    <div class="player white">{p2}</div>
                </div>
                <div class="result {result_class}">{result_text}</div>
            </div>
'''
                        html_content += '''        </div>
    </div>
</body>
</html>'''
                        
                        with open(html_path, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        
                        print(f"\n📊 对阵表已导出到 HTML 文件: {html_path}")
                        print(f"   共 {total_matches} 台对局\n")
                        
                        # 显示前10条预览
                        print(f"📋 第{args.matchups}轮对阵预览:\n")
                        for m in rows[:10]:
                            p1 = m.get('p1') or '轮空'
                            p2 = m.get('p2') or '轮空'
                            seat = m.get('seatnum')
                            print(f"台{seat}: {p1} vs {p2}")
                        if total_matches > 10:
                            print(f"\n... 还有 {total_matches - 10} 台对局\n")
            
            elif args.ranking:
                matches, total_bouts, perf_matches = client.get_all_rounds(args.group_id)
                rankings, perf_ranking = client.calculate_ranking(matches)
                
                result["data"]["rankings"] = rankings
                result["data"]["total_bouts"] = total_bouts
                result["data"]["_perf"] = {
                    "matches": perf_matches,
                    "ranking": perf_ranking
                }
                
                if not args.json:
                    client.print_ranking(rankings)
            else:
                players, perf = client.get_group_players(args.event_id, args.group_id)
                result["data"]["players"] = players
                result["data"]["_perf"] = perf
                
                if not args.json:
                    total_players = len(players)
                    if total_players <= 10:
                        # 单行 Markdown 格式
                        print(f"\n📋 分组 {args.group_id} 共有 {total_players} 名选手\n")
                        for p in players:
                            name = p.get('participantname')
                            rank = p.get('rank_num')
                            score = p.get('integral')
                            print(f"• **{name}** | 排名: {rank} | 积分: {score}")
                        print()
                    else:
                        # HTML 格式输出到文件（手机端优化）
                        html_path = f"/tmp/players_{int(time.time())}.html"
                        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>选手列表</title>
    <style>
                        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background: #f5f5f5; line-height: 1.6; }}
                        .container {{ max-width: 100%; margin: 0 auto; background: white; min-height: 100vh; }}
                        .header {{ background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); color: white; padding: 20px 16px; text-align: center; position: sticky; top: 0; z-index: 100; }}
                        .header h1 {{ font-size: 22px; margin-bottom: 8px; font-weight: 600; }}
                        .header .subtitle {{ font-size: 14px; opacity: 0.9; }}
                        .list {{ padding: 0; }}
                        .item {{ display: flex; align-items: center; padding: 14px 16px; border-bottom: 1px solid #f0f0f0; background: white; }}
                        .item:nth-child(even) {{ background: #fafafa; }}
                        .rank {{ width: 36px; height: 36px; background: #f3e5f5; color: #9b59b6; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; flex-shrink: 0; }}
                        .rank.top3 {{ background: #ffebee; color: #e74c3c; }}
                        .info {{ flex: 1; margin-left: 12px; display: flex; justify-content: space-between; align-items: center; }}
                        .name {{ font-size: 16px; font-weight: 500; color: #333; }}
                        .score {{ font-size: 18px; font-weight: bold; color: #e74c3c; }}
                        @media (max-width: 375px) {{
                            .header h1 {{ font-size: 20px; }}
                            .name {{ font-size: 15px; }}
                            .score {{ font-size: 16px; }}
                        }}
                    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👥 选手列表</h1>
            <div class="subtitle">共 {total_players} 名选手</div>
        </div>
        <div class="list">
'''
                        for i, p in enumerate(players, 1):
                            rank = p.get('rank_num')
                            name = html.escape(str(p.get('participantname', '')))
                            score = p.get('integral')
                            rank_class = 'rank'
                            if rank and int(rank) <= 3:
                                rank_class += ' top3'
                            html_content += f'''            <div class="item">
                <div class="{rank_class}">{rank}</div>
                <div class="info">
                    <div class="name">{name}</div>
                    <div class="score">{score}分</div>
                </div>
            </div>
'''
                        html_content += '''        </div>
    </div>
</body>
</html>'''
                        
                        with open(html_path, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        
                        print(f"\n📊 选手列表已导出到 HTML 文件: {html_path}")
                        print(f"   共 {total_players} 名选手\n")
                        
                        # 显示前10条预览
                        print("📋 前10名选手预览:\n")
                        for p in players[:10]:
                            name = p.get('participantname')
                            rank = p.get('rank_num')
                            score = p.get('integral')
                            print(f"• **{name}** | 排名: {rank} | 积分: {score}")
                        print(f"\n... 还有 {total_players - 10} 名选手\n")
        
        # 输出性能报告
        if not args.json and not args.quiet:
            client.print_perf_report()
        
        # JSON输出
        if args.json:
            result["_perf_summary"] = client.get_perf_dict()
            print(json.dumps(result, ensure_ascii=False, indent=2))
    
    except Exception as e:
        result = {"status": "error", "message": str(e)}
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
