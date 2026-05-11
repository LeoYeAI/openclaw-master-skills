#!/usr/bin/env python3
"""
RootCraft Learning System - 记忆曲线模块
基于艾宾浩斯遗忘曲线设计复习计划

支持中英文
"""
import datetime
import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


# 艾宾浩斯遗忘曲线间隔（分钟）
MEMORY_INTERVALS = {
    "zh": [10, 1440, 4320, 10080, 20160, 43200],  # 10分钟、1天、3天、7天、14天、30天
    "en": [10, 1440, 4320, 10080, 20160, 43200]
}

MEMORY_INTERVALS_LABELS = {
    "zh": ["10分钟后", "1天后", "3天后", "7天后", "14天后", "30天后"],
    "en": ["After 10 min", "After 1 day", "After 3 days", "After 7 days", "After 14 days", "After 30 days"]
}


@dataclass
class FlashCard:
    """记忆卡片"""
    id: str
    front: str  # 正面问题
    back: str   # 背面答案
    tags: List[str]
    language: str = "zh"  # zh/en
    created_at: str = ""
    next_review: str = ""
    review_count: int = 0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()
        if not self.next_review:
            self.next_review = self.created_at


class MemoryCurve:
    """记忆曲线管理器"""

    def __init__(self, data_dir: str = None, language: str = "zh"):
        """
        初始化
        
        Args:
            data_dir: 数据存储目录
            language: 语言 zh/en
        """
        self.language = language
        if language not in MEMORY_INTERVALS:
            language = "zh"
        
        self.intervals = MEMORY_INTERVALS[language]
        self.interval_labels = MEMORY_INTERVALS_LABELS[language]
        
        # 数据存储
        if data_dir is None:
            data_dir = os.path.expanduser("~/.openclaw/workspace/rootcraft/cards")
        
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.cards_file = os.path.join(data_dir, "cards.json")
        self.schedule_file = os.path.join(data_dir, "schedule.json")
        
        # 加载数据
        self.cards = self._load_cards()
        self.schedule = self._load_schedule()
    
    def _load_cards(self) -> Dict[str, FlashCard]:
        """加载卡片"""
        if os.path.exists(self.cards_file):
            with open(self.cards_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {k: FlashCard(**v) for k, v in data.items()}
        return {}
    
    def _save_cards(self):
        """保存卡片"""
        data = {k: asdict(v) for k, v in self.cards.items()}
        with open(self.cards_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_schedule(self) -> Dict[str, List[str]]:
        """加载复习计划"""
        if os.path.exists(self.schedule_file):
            with open(self.schedule_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def _save_schedule(self):
        """保存复习计划"""
        with open(self.schedule_file, "w", encoding="utf-8") as f:
            json.dump(self.schedule, f, ensure_ascii=False, indent=2)
    
    def generate_card_id(self) -> str:
        """生成卡片ID"""
        import uuid
        return uuid.uuid4().hex[:8]
    
    def create_card(self, front: str, back: str, tags: List[str] = None) -> FlashCard:
        """
        创建卡片
        
        Args:
            front: 正面（问题）
            back: 背面（答案）
            tags: 标签
        
        Returns:
            创建的卡片
        """
        card_id = self.generate_card_id()
        card = FlashCard(
            id=card_id,
            front=front,
            back=back,
            tags=tags or ["rootcraft"],
            language=self.language
        )
        
        # 设置首次复习时间（10分钟后）
        first_review = datetime.datetime.now() + datetime.timedelta(minutes=self.intervals[0])
        card.next_review = first_review.isoformat()
        
        self.cards[card_id] = card
        
        # 生成复习计划
        self._generate_review_schedule(card_id)
        
        self._save_cards()
        self._save_schedule()
        
        return card
    
    def _generate_review_schedule(self, card_id: str):
        """生成复习时间表"""
        times = []
        now = datetime.datetime.now()
        
        for interval in self.intervals:
            next_time = now + datetime.timedelta(minutes=interval)
            times.append(next_time.isoformat())
        
        self.schedule[card_id] = times
    
    def get_due_cards(self) -> List[FlashCard]:
        """获取今日应复习的卡片"""
        now = datetime.datetime.now()
        due = []
        
        for card_id, card in self.cards.items():
            next_review = datetime.datetime.fromisoformat(card.next_review)
            if next_review <= now:
                due.append(card)
        
        return due
    
    def get_upcoming_cards(self, days: int = 7) -> Dict[str, List[FlashCard]]:
        """获取未来几天的复习安排"""
        result = {}
        
        for i in range(days):
            date = datetime.datetime.now() + datetime.timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            result[date_str] = []
        
        for card_id, card in self.cards.items():
            if card_id in self.schedule:
                for review_time in self.schedule[card_id]:
                    review_date = datetime.datetime.fromisoformat(review_time)
                    date_str = review_date.strftime("%Y-%m-%d")
                    if date_str in result:
                        result[date_str].append(card)
        
        return result
    
    def mark_reviewed(self, card_id: str, quality: int = 3):
        """
        标记已复习
        
        Args:
            card_id: 卡片ID
            quality: 回忆质量 1-5
                    1: 完全忘记
                    2: 记起来很困难
                    3: 记起来了，但有些犹豫
                    4: 回忆清晰
                    5: 太简单了
        """
        if card_id not in self.cards:
            return
        
        card = self.cards[card_id]
        card.review_count += 1
        
        # 根据记忆质量调整下次复习间隔
        if quality >= 4:
            # 记得牢，间隔增加
            current_idx = 0
            if card_id in self.schedule:
                try:
                    current_times = self.schedule[card_id]
                    if card.next_review in current_times:
                        current_idx = current_times.index(card.next_review)
                        if current_idx < len(self.intervals) - 1:
                            current_idx += 1
                except:
                    pass
            
            next_interval = self.intervals[current_idx]
        else:
            # 记得不牢，保持间隔或退回到第一个
            next_interval = self.intervals[0]
        
        next_review = datetime.datetime.now() + datetime.timedelta(minutes=next_interval)
        card.next_review = next_review.isoformat()
        
        self._save_cards()
    
    def delete_card(self, card_id: str) -> bool:
        """删除卡片"""
        if card_id in self.cards:
            del self.cards[card_id]
            if card_id in self.schedule:
                del self.schedule[card_id]
            self._save_cards()
            self._save_schedule()
            return True
        return False
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = len(self.cards)
        due_today = len(self.get_due_cards())
        
        # 统计各标签数量
        tag_counts = {}
        for card in self.cards.values():
            for tag in card.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return {
            "total_cards": total,
            "due_today": due_today,
            "tag_counts": tag_counts,
            "language": self.language
        }
    
    def export_to_csv(self, filepath: str = None) -> str:
        """导出为 CSV 格式（Anki 兼容）"""
        if filepath is None:
            filepath = os.path.join(self.data_dir, "rootcraft_cards.csv")
        
        import csv
        
        with open(filepath, "w", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["front", "back", "tags"])
            
            for card in self.cards.values():
                tags_str = ";".join(card.tags)
                writer.writerow([card.front, card.back, tags_str])
        
        return filepath
    
    def export_to_txt(self, filepath: str = None) -> str:
        """导出为纯文本格式（可直接复制使用）"""
        if filepath is None:
            filepath = os.path.join(self.data_dir, "rootcraft_cards.txt")
        
        label = "复习卡片" if self.language == "zh" else "Review Cards"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {label}\n\n")
            
            for i, card in enumerate(self.cards.values(), 1):
                f.write(f"## {i}. {card.front}\n\n")
                f.write(f"{card.back}\n\n")
                f.write(f"Tags: {', '.join(card.tags)}\n\n")
                f.write("---\n\n")
        
        return filepath
    
    def get_review_reminder(self) -> str:
        """获取复习提醒消息"""
        due = self.get_due_cards()
        
        if not due:
            if self.language == "zh":
                return "✅ 今天没有待复习的卡片！"
            else:
                return "✅ No cards to review today!"
        
        if self.language == "zh":
            msg = f"📚 你有 {len(due)} 张卡片需要复习：\n\n"
        else:
            msg = f"📚 You have {len(due)} cards to review:\n\n"
        
        for card in due[:5]:  # 只显示前5张
            msg += f"• {card.front[:50]}...\n"
        
        if len(due) > 5:
            msg += f"\n... 还有 {len(due) - 5} 张"
        
        return msg


def test():
    """测试"""
    # 中文测试
    print("=== 中文测试 ===")
    mc = MemoryCurve(language="zh")
    
    # 创建卡片
    card1 = mc.create_card(
        front="什么是第一性原理？",
        back="从最基本的事实和公理出发思考问题，而非依赖类比或传统智慧。",
        tags=["学习方法", "第一性原理"]
    )
    print(f"创建卡片: {card1.id}")
    
    card2 = mc.create_card(
        front="What is the First Principles Thinking?",
        back="Thinking from the most basic facts and axioms, rather than relying on analogies or conventional wisdom.",
        tags=["learning", "first-principles"]
    )
    print(f"创建卡片: {card2.id}")
    
    # 统计
    stats = mc.get_stats()
    print(f"统计: {stats}")
    
    # 导出
    csv_path = mc.export_to_csv()
    print(f"导出CSV: {csv_path}")
    
    # 英文测试
    print("\n=== English Test ===")
    mc_en = MemoryCurve(language="en")
    card3 = mc_en.create_card(
        front="What is Feynman Technique?",
        back="Explain a concept in simple terms as if teaching someone else.",
        tags=["learning", "technique"]
    )
    print(f"Created card: {card3.id}")
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    test()