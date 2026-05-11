#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2026 Anima-AIOS Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Anima AIOS v6.0 - Memory Watcher

监听 OpenClaw workspace/memory/ 目录变化，自动同步到 Anima L2 情景记忆。
解决 FB-008：Anima 与 OpenClaw 记忆写入没打通。

基于 watchdog 库，自动识别运行环境：
- Linux → inotify（秒级响应）
- macOS → FSEvents（秒级响应）  
- Windows → ReadDirectoryChangesW（秒级响应）
- 其他 → polling fallback

Author: 清禾
Date: 2026-03-23
Version: 6.0.0
"""

import os
import sys
import json
import time
import hashlib
import logging
from pathlib import Path
try:
    from ..config.path_config import get_config
except ImportError:
    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.insert(0, str(_Path(__file__).parent.parent / 'config'))
    from path_config import get_config
from datetime import datetime
from typing import Dict, List, Optional, Set

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [MemoryWatcher] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class MemoryFileHandler(FileSystemEventHandler):
    """
    文件系统事件处理器
    
    监听 .md 文件的创建和修改事件，提取新增内容并同步到 Anima。
    """
    
    def __init__(self, watcher: 'MemoryWatcher'):
        super().__init__()
        self.watcher = watcher
    
    def on_modified(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith('.md'):
            return
        self.watcher.handle_file_change(event.src_path)
    
    def on_created(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith('.md'):
            return
        self.watcher.handle_file_change(event.src_path)


class MemoryWatcher:
    """
    OpenClaw 记忆文件监听器
    
    监听 workspace/memory/ 目录，检测到新内容时：
    1. 提取新增行（diff）
    2. 写入 L2 情景记忆（facts/episodic/）
    3. 更新 EXP
    4. 检查每日任务完成
    5. 记录最后写入时间（供宫殿分类调度器使用）
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化 MemoryWatcher
        
        Args:
            config: 配置字典，可选。不传则从默认路径加载。
        """
        self.config = config or self._load_config()
        
        # 路径配置
        self.facts_base = Path(os.getenv(
            "ANIMA_FACTS_BASE",
            self.config.get("facts_base") or str(get_config().facts_base)
        ))
        self.agent_name = self._detect_agent_name()
        self.agent_dir = self.facts_base / self.agent_name
        self.watch_dir = self._detect_watch_dir()
        
        # 状态追踪
        self._file_hashes: Dict[str, str] = {}  # 文件路径 → 内容哈希
        self._file_lines: Dict[str, int] = {}   # 文件路径 → 已处理行数
        self._last_write_time: float = 0         # 最后一次知识写入时间戳
        self._synced_count: int = 0              # 本次运行同步的记忆数
        
        # 初始化：记录现有文件状态（避免启动时重复处理）
        self._init_file_state()
        
        logger.info(f"MemoryWatcher 初始化完成")
        logger.info(f"  Agent: {self.agent_name}")
        logger.info(f"  监听目录: {self.watch_dir}")
        logger.info(f"  Facts 目录: {self.agent_dir}")
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        config_paths = [
            Path(os.getenv("ANIMA_CONFIG", "")),
            Path.home() / ".anima" / "config" / "anima_config.json",
            Path("/root/.openclaw/skills/anima-aios/config/anima_config.json"),
        ]
        
        for path in config_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception:
                    continue
        
        return {}
    
    def _detect_agent_name(self) -> str:
        """自动检测当前 Agent 名称（委托给公共模块）"""
        # 优先：配置文件中的 agent_name
        name = self.config.get("agent_name", "")
        if name and name != "auto":
            return name
        # 委托给统一的 agent_resolver
        try:
            from .agent_resolver import resolve_agent_name
        except ImportError:
            from agent_resolver import resolve_agent_name
        return resolve_agent_name()
    def _detect_watch_dir(self) -> Path:
        """自动检测要监听的 memory 目录"""
        # 优先级：环境变量 > 配置文件 > 自动扫描
        watch_path = os.getenv("ANIMA_WATCH_DIR", "")
        if watch_path:
            return Path(watch_path)
        
        watch_path = self.config.get("watch_dir", "")
        if watch_path and watch_path != "auto":
            return Path(watch_path)
        
        # 自动扫描
        openclaw_dir = Path.home() / ".openclaw"
        for ws in openclaw_dir.glob("workspace-*/memory"):
            return ws
        
        # 默认
        return openclaw_dir / "workspace" / "memory"
    
    def _init_file_state(self):
        """初始化现有文件状态，避免启动时重复处理"""
        if not self.watch_dir.exists():
            self.watch_dir.mkdir(parents=True, exist_ok=True)
            return
        
        for md_file in self.watch_dir.glob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                self._file_hashes[str(md_file)] = hashlib.md5(content.encode()).hexdigest()
                self._file_lines[str(md_file)] = len(content.splitlines())
            except Exception as e:
                logger.warning(f"初始化文件状态失败 {md_file}: {e}")
    
    def handle_file_change(self, filepath: str):
        """
        处理文件变更事件
        
        提取新增内容，同步到 Anima L2。
        """
        filepath = str(filepath)
        
        try:
            content = Path(filepath).read_text(encoding='utf-8')
        except Exception as e:
            logger.warning(f"读取文件失败 {filepath}: {e}")
            return
        
        # 计算新哈希
        new_hash = hashlib.md5(content.encode()).hexdigest()
        old_hash = self._file_hashes.get(filepath, "")
        
        if new_hash == old_hash:
            return  # 内容没变
        
        # 提取新增行
        lines = content.splitlines()
        old_line_count = self._file_lines.get(filepath, 0)
        new_lines = lines[old_line_count:]
        
        if not new_lines:
            # 可能是修改了已有内容，取最后修改的部分
            new_lines = lines[-5:] if lines else []
        
        # 过滤空行和纯标记行
        meaningful_lines = [
            line.strip() for line in new_lines
            if line.strip() and not line.strip().startswith('#') and len(line.strip()) > 5
        ]
        
        if meaningful_lines:
            # 合并为一条记忆内容
            memory_content = '\n'.join(meaningful_lines)
            
            # 同步到 L2
            self._sync_to_l2(memory_content, filepath)
            
            # 更新 EXP
            self._update_exp(memory_content)
            
            # 检查任务完成
            self._check_quest_completion(memory_content)
            
            # 记录最后写入时间（供宫殿分类调度器使用）
            self._last_write_time = time.time()
            
            self._synced_count += 1
            logger.info(f"同步完成 #{self._synced_count}: {len(meaningful_lines)} 行 → L2")
        
        # 更新状态
        self._file_hashes[filepath] = new_hash
        self._file_lines[filepath] = len(lines)
    
    def _sync_to_l2(self, content: str, source_file: str):
        """
        将内容写入 L2 情景记忆（facts/episodic/）
        
        Args:
            content: 记忆内容
            source_file: 来源文件路径
        """
        episodic_dir = self.agent_dir / "facts" / "episodic"
        episodic_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        filename = f"episodic_{timestamp}_{content_hash}.md"
        
        # 构建 fact 文件
        source_name = Path(source_file).name
        fact_content = f"""---
type: episodic
source: openclaw_memory_watcher
source_file: {source_name}
agent: {self.agent_name}
created_at: {datetime.now().isoformat()}
quality: pending
tags: [auto-sync, openclaw-memory]
---

{content}
"""
        
        fact_path = episodic_dir / filename
        fact_path.write_text(fact_content, encoding='utf-8')
        logger.debug(f"写入 L2: {filename}")
    
    def _update_exp(self, content: str):
        """
        更新 EXP（记忆写入 +1 EXP）
        
        Args:
            content: 记忆内容
        """
        try:
            exp_file = self.agent_dir / "exp_history.jsonl"
            exp_file.parent.mkdir(parents=True, exist_ok=True)
            
            exp_record = {
                "timestamp": datetime.now().isoformat(),
                "action": "memory_watcher_sync",
                "exp": 1,
                "dimension": "understanding",
                "quality_multiplier": 1.0,
                "source": "memory_watcher"
            }
            
            with open(exp_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(exp_record, ensure_ascii=False) + '\n')
            
            logger.debug(f"EXP +1 (memory_watcher_sync)")
        except Exception as e:
            logger.warning(f"更新 EXP 失败: {e}")
    
    def _check_quest_completion(self, content: str):
        """
        检查每日任务完成情况（解决 FB-006）
        
        Args:
            content: 记忆内容
        """
        try:
            daily_exp_file = self.agent_dir / "daily_exp.json"
            if not daily_exp_file.exists():
                return
            
            with open(daily_exp_file, 'r', encoding='utf-8') as f:
                daily_data = json.load(f)
            
            quests = daily_data.get("quests", [])
            updated = False
            
            for quest in quests:
                if quest.get("completed", False):
                    continue
                
                title = quest.get("title", "").lower()
                
                # 自动检测任务完成
                if "写一条记忆" in title or "写记忆" in title:
                    quest["completed"] = True
                    quest["completed_at"] = datetime.now().isoformat()
                    updated = True
                    logger.info(f"任务自动完成: {quest['title']}")
                elif "写工作日志" in title or "日志" in title:
                    quest["completed"] = True
                    quest["completed_at"] = datetime.now().isoformat()
                    updated = True
                    logger.info(f"任务自动完成: {quest['title']}")
            
            if updated:
                with open(daily_exp_file, 'w', encoding='utf-8') as f:
                    json.dump(daily_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.debug(f"检查任务完成失败: {e}")
    
    @property
    def last_write_time(self) -> float:
        """最后一次知识写入的时间戳（供宫殿分类调度器使用）"""
        return self._last_write_time
    
    def get_status(self) -> Dict:
        """获取 watcher 运行状态"""
        return {
            "agent": self.agent_name,
            "watch_dir": str(self.watch_dir),
            "facts_dir": str(self.agent_dir),
            "synced_count": self._synced_count,
            "tracked_files": len(self._file_hashes),
            "last_write_time": datetime.fromtimestamp(self._last_write_time).isoformat() if self._last_write_time else None,
            "running": True
        }
    
    def start(self, blocking: bool = True):
        """
        启动文件监听
        
        Args:
            blocking: 是否阻塞运行（默认 True）
        """
        if not self.watch_dir.exists():
            self.watch_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建监听目录: {self.watch_dir}")
        
        handler = MemoryFileHandler(self)
        observer = Observer()
        observer.schedule(handler, str(self.watch_dir), recursive=False)
        observer.start()
        
        logger.info(f"🔍 MemoryWatcher 启动，监听: {self.watch_dir}")
        logger.info(f"   后端: {observer.__class__.__name__}")
        
        if blocking:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
                logger.info("MemoryWatcher 停止")
            observer.join()
        else:
            return observer


def main():
    """启动 MemoryWatcher"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Anima Memory Watcher - 监听 OpenClaw 记忆文件变化')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--status', action='store_true', help='显示状态')
    parser.add_argument('--once', action='store_true', help='扫描一次后退出（不持续监听）')
    args = parser.parse_args()
    
    config = None
    if args.config:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    watcher = MemoryWatcher(config)
    
    if args.status:
        status = watcher.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return
    
    if args.once:
        # 单次扫描模式：检查所有文件的变化
        logger.info("单次扫描模式")
        for md_file in watcher.watch_dir.glob("*.md"):
            watcher.handle_file_change(str(md_file))
        status = watcher.get_status()
        logger.info(f"扫描完成，同步 {status['synced_count']} 条记忆")
        return
    
    # 持续监听模式
    watcher.start(blocking=True)


if __name__ == '__main__':
    main()
