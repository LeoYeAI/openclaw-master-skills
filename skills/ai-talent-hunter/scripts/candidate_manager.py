#!/usr/bin/env python3
"""
候选人状态管理器

功能：
1. 保存所有搜索到的候选人
2. 记录候选人状态（pending / selected / passed）
3. 防止重复推荐
4. 支持查询历史记录
5. 搜索记录支持 resume（search_params / page offsets / seen ids）
6. 批量更新候选人状态
7. 跨搜索查询候选人出现记录

数据结构：
{
  "search_id": "uuid",
  "jd_title": "AI 原生应用开发工程师",
  "search_date": "2026-03-25",
  "queries": [...],
  "location_filter": "shenzhen",
  "search_params": { ... },
  "seen_github_ids": ["user1", "user2"],
  "repo_page_offsets": {"query1": 3, "query2": 5},
  "user_page_offsets": {"query1": 2},
  "status": "in_progress",
  "rounds_searched": 1,
  "candidates": [
    {
      "github_id": "zhangsan",
      "name": "Zhang San",
      "score": 210.5,
      "status": "pending",  // pending / selected / passed
      "selected_at": null,
      "passed_at": null,
      "pass_reason": null,
      ...
    }
  ]
}
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional


class CandidateManager:
    """候选人状态管理器"""

    def __init__(self, db_path: str = "~/.openclaw/workspace/skills/ai-talent-hunter/data/candidates.jsonl"):
        self.db_path = os.path.expanduser(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _load_records(self) -> List[Dict]:
        """从 JSONL 文件加载所有记录"""
        records: List[Dict] = []
        if not os.path.exists(self.db_path):
            return records
        with open(self.db_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        return records

    def _save_records(self, records: List[Dict]) -> None:
        """将所有记录写回 JSONL 文件"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')

    def save_search_result(
        self,
        search_id: Optional[str],
        jd_title: str,
        queries: List[str],
        location_filter: Optional[str],
        candidates: List[Dict],
        # 新增参数：支持搜索 resume 与状态追踪
        search_params: Optional[Dict] = None,
        seen_github_ids: Optional[List[str]] = None,
        repo_page_offsets: Optional[Dict] = None,
        user_page_offsets: Optional[Dict] = None,
        rounds_searched: int = 1,
        status: str = "in_progress",
    ) -> str:
        """
        保存搜索结果

        Args:
            search_id: 搜索记录 ID（如果为 None，自动生成）
            jd_title: 职位名称
            queries: 搜索查询
            location_filter: 地理位置过滤
            candidates: 候选人列表
            search_params: 完整搜索参数，用于 resume
            seen_github_ids: 已出现的 github_id 列表
            repo_page_offsets: query → 已搜到第几页（Repo Search）
            user_page_offsets: query → 已搜到第几页（User Search）
            rounds_searched: 已搜索轮数
            status: 搜索状态 ("in_progress" / "completed" / "abandoned")

        Returns:
            search_id: 搜索记录 ID
        """
        if search_id is None:
            search_id = str(uuid.uuid4())
        search_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record: Dict = {
            "search_id": search_id,
            "jd_title": jd_title,
            "search_date": search_date,
            "queries": queries,
            "location_filter": location_filter,
            "search_params": search_params,
            "seen_github_ids": seen_github_ids or [],
            "repo_page_offsets": repo_page_offsets or {},
            "user_page_offsets": user_page_offsets or {},
            "status": status,
            "rounds_searched": rounds_searched,
            "candidates": candidates,
            "total": len(candidates),
        }

        # 读取已有记录，查找是否存在相同 search_id
        records = self._load_records()
        existing_index = -1
        for i, r in enumerate(records):
            if r["search_id"] == search_id:
                existing_index = i
                break

        if existing_index >= 0:
            # 合并候选人列表：以新的覆盖旧的（基于 github_id 去重）
            old_record = records[existing_index]
            old_candidates_map = {c["github_id"]: c for c in old_record["candidates"]}
            for c in candidates:
                old_candidates_map[c["github_id"]] = c
            merged_candidates = list(old_candidates_map.values())
            record["candidates"] = merged_candidates
            record["total"] = len(merged_candidates)
            records[existing_index] = record
            print(f"[INFO] 搜索记录已更新（合并候选人）: search_id={search_id}")
        else:
            records.append(record)
            print(f"[INFO] 搜索记录已保存: search_id={search_id}")

        self._save_records(records)
        return search_id

    def update_candidate_status(
        self,
        search_id: str,
        github_id: str,
        status: str,
        reason: Optional[str] = None
    ):
        """
        更新候选人状态

        Args:
            search_id: 搜索记录 ID
            github_id: GitHub ID
            status: 状态（selected / passed / pending）
            reason: Pass 原因（可选）
        """
        if not os.path.exists(self.db_path):
            print(f"[ERROR] 数据文件不存在: {self.db_path}")
            return

        records = self._load_records()

        # 更新目标记录
        updated = False
        for record in records:
            if record["search_id"] == search_id:
                for candidate in record["candidates"]:
                    if candidate["github_id"] == github_id:
                        candidate["status"] = status
                        if status == "selected":
                            candidate["selected_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        elif status == "passed":
                            candidate["passed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            candidate["pass_reason"] = reason
                        updated = True
                        break
                if updated:
                    break

        if not updated:
            print(f"[WARN] 未找到记录: search_id={search_id}, github_id={github_id}")
            return

        self._save_records(records)
        print(f"[INFO] 已更新候选人状态: {github_id} → {status}")

    def get_search_result(self, search_id: str) -> Optional[Dict]:
        """
        获取搜索结果

        Args:
            search_id: 搜索记录 ID

        Returns:
            搜索记录（包含候选人列表）
        """
        if not os.path.exists(self.db_path):
            return None

        with open(self.db_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    if record["search_id"] == search_id:
                        return record
        return None

    def is_candidate_already_selected(self, github_id: str) -> bool:
        """
        检查候选人是否已被选中过（跨搜索）

        Args:
            github_id: GitHub ID

        Returns:
            True 如果已被选中
        """
        if not os.path.exists(self.db_path):
            return False

        with open(self.db_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    for candidate in record["candidates"]:
                        if candidate["github_id"] == github_id and candidate["status"] == "selected":
                            return True
        return False

    def list_all_searches(self) -> List[Dict]:
        """
        列出所有搜索记录

        Returns:
            搜索记录列表（不含候选人详情）
        """
        if not os.path.exists(self.db_path):
            return []

        searches = []
        with open(self.db_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    searches.append({
                        "search_id": record["search_id"],
                        "jd_title": record["jd_title"],
                        "search_date": record["search_date"],
                        "total": record["total"],
                        "status": record.get("status", "unknown"),
                        "rounds_searched": record.get("rounds_searched", 0),
                        "selected_count": sum(1 for c in record["candidates"] if c.get("status") == "selected"),
                        "passed_count": sum(1 for c in record["candidates"] if c.get("status") == "passed"),
                    })
        return searches

    def get_candidate_appearances(self, github_id: str) -> Dict:
        """
        查询单个候选人在所有搜索中的出现记录

        Args:
            github_id: GitHub ID

        Returns:
            包含 appearances 列表和 latest_profile 的字典
        """
        records = self._load_records()
        appearances: List[Dict] = []
        latest_profile: Optional[Dict] = None
        latest_date = ""

        for record in records:
            for candidate in record["candidates"]:
                if candidate["github_id"] == github_id:
                    appearances.append({
                        "search_id": record["search_id"],
                        "jd_title": record["jd_title"],
                        "search_date": record["search_date"],
                        "score": candidate.get("score"),
                        "status": candidate.get("status", "pending"),
                    })
                    # reason: 按 search_date 取最新的完整 profile
                    if record["search_date"] > latest_date:
                        latest_date = record["search_date"]
                        latest_profile = candidate
                    break

        return {
            "github_id": github_id,
            "appearances": appearances,
            "latest_profile": latest_profile,
        }

    def get_selected_candidates(self, search_id: str) -> List[Dict]:
        """
        获取某次搜索中所有 selected 的候选人

        Args:
            search_id: 搜索记录 ID

        Returns:
            selected 候选人的完整列表
        """
        record = self.get_search_result(search_id)
        if record is None:
            return []
        return [c for c in record["candidates"] if c.get("status") == "selected"]

    def set_search_status(self, search_id: str, status: str) -> bool:
        """
        设置搜索记录的状态

        Args:
            search_id: 搜索记录 ID
            status: 新状态 ("in_progress" / "completed" / "abandoned")

        Returns:
            是否更新成功
        """
        records = self._load_records()
        for record in records:
            if record["search_id"] == search_id:
                record["status"] = status
                self._save_records(records)
                print(f"[INFO] 搜索状态已更新: search_id={search_id} → {status}")
                return True
        print(f"[WARN] 未找到搜索记录: search_id={search_id}")
        return False


def main():
    """命令行测试"""
    import argparse

    parser = argparse.ArgumentParser(description="候选人状态管理器")
    parser.add_argument(
        "--action",
        choices=[
            "list", "get", "update",
            "get-candidate", "batch-update", "get-selected", "set-status",
        ],
        required=True,
    )
    parser.add_argument("--search-id", help="搜索记录 ID")
    parser.add_argument("--github-id", help="GitHub ID")
    parser.add_argument("--status", help="新状态")
    parser.add_argument("--reason", help="Pass 原因")
    # batch-update 参数
    parser.add_argument("--selected", help="逗号分隔的 selected GitHub ID 列表")
    parser.add_argument("--passed", help="逗号分隔的 passed GitHub ID 列表")
    parser.add_argument("--pending", help="逗号分隔的 pending GitHub ID 列表")

    args = parser.parse_args()

    manager = CandidateManager()

    if args.action == "list":
        searches = manager.list_all_searches()
        print(json.dumps(searches, ensure_ascii=False, indent=2))

    elif args.action == "get":
        if not args.search_id:
            print("[ERROR] 缺少 --search-id 参数")
            return
        result = manager.get_search_result(args.search_id)
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"[ERROR] 未找到搜索记录: {args.search_id}")

    elif args.action == "update":
        if not all([args.search_id, args.github_id, args.status]):
            print("[ERROR] 缺少必需参数: --search-id, --github-id, --status")
            return
        manager.update_candidate_status(
            args.search_id,
            args.github_id,
            args.status,
            args.reason,
        )

    elif args.action == "get-candidate":
        if not args.github_id:
            print("[ERROR] 缺少 --github-id 参数")
            return
        result = manager.get_candidate_appearances(args.github_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "batch-update":
        if not args.search_id:
            print("[ERROR] 缺少 --search-id 参数")
            return
        count = 0
        for status_name, id_list_str in [("selected", args.selected), ("passed", args.passed), ("pending", args.pending)]:
            if not id_list_str:
                continue
            for gid in id_list_str.split(","):
                gid = gid.strip()
                if gid:
                    manager.update_candidate_status(args.search_id, gid, status_name)
                    count += 1
        print(f"[INFO] 批量更新完成，共 {count} 条")

    elif args.action == "get-selected":
        if not args.search_id:
            print("[ERROR] 缺少 --search-id 参数")
            return
        selected = manager.get_selected_candidates(args.search_id)
        print(json.dumps(selected, ensure_ascii=False, indent=2))

    elif args.action == "set-status":
        if not args.search_id or not args.status:
            print("[ERROR] 缺少必需参数: --search-id, --status")
            return
        manager.set_search_status(args.search_id, args.status)


if __name__ == "__main__":
    main()
