#!/usr/bin/env python3
"""
RootCraft Learning System - Anki 卡片生成器
从学习内容自动生成记忆卡片

支持中英文
"""
import os
import json
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class AnkiCard:
    """Anki 卡片"""
    front: str
    back: str
    tags: List[str]


class AnkiCardGenerator:
    """Anki 卡片生成器"""
    
    def __init__(self, language: str = "zh"):
        """
        初始化
        
        Args:
            language: 语言 zh/en
        """
        self.language = language
        self.cards = []
        
        # 语言相关的提示文本
        self.labels = {
            "zh": {
                "concept": "概念",
                "definition": "定义",
                "example": "例子",
                "analogy": "类比",
                "thinking": "思考题",
                "feynman": "费曼练习",
                "summary": "总结",
                "tip": "提示"
            },
            "en": {
                "concept": "Concept",
                "definition": "Definition",
                "example": "Example",
                "analogy": "Analogy",
                "thinking": "Thinking Question",
                "feynman": "Feynman Practice",
                "summary": "Summary",
                "tip": "Tip"
            }
        }
    
    def _t(self, key: str) -> str:
        """获取翻译"""
        return self.labels.get(self.language, self.labels["zh"]).get(key, key)
    
    def generate_from_concept(self, 
                               concept: str, 
                               definition: str = "",
                               examples: List[str] = None,
                               analogy: str = "",
                               key_points: List[str] = None) -> List[AnkiCard]:
        """
        从概念生成卡片组
        
        Args:
            concept: 概念名称
            definition: 定义/解释
            examples: 生活例子列表
            analogy: 类比
            key_points: 关键要点
        
        Returns:
            卡片列表
        """
        cards = []
        examples = examples or []
        key_points = key_points or []
        
        # 卡片1: 概念定义
        if definition:
            cards.append(AnkiCard(
                front=f"{self._t('concept')}: {concept}",
                back=definition,
                tags=["rootcraft", "concept", self.language]
            ))
        
        # 卡片2: 费曼练习 - 用简单语言解释
        cards.append(AnkiCard(
            front=f"{self._t('feynman')}: {concept}",
            back=f"📝 {self._t('tip')}: {self._get_feynman_tip()}",
            tags=["rootcraft", "feynman", self.language]
        ))
        
        # 卡片3: 生活例子
        for i, example in enumerate(examples[:2]):
            cards.append(AnkiCard(
                front=f"{concept} - {self._t('example')} {i+1}",
                back=example,
                tags=["rootcraft", "example", self.language]
            ))
        
        # 卡片4: 类比
        if analogy:
            cards.append(AnkiCard(
                front=f"{concept} - {self._t('analogy')}",
                back=analogy,
                tags=["rootcraft", "analogy", self.language]
            ))
        
        # 卡片5: 关键要点
        for i, point in enumerate(key_points[:3]):
            cards.append(AnkiCard(
                front=f"{concept} - {self._t('key_points')} {i+1}",
                back=point,
                tags=["rootcraft", "keypoint", self.language]
            ))
        
        # 卡片6: 逆向思考题
        cards.append(AnkiCard(
            front=f"{self._t('thinking')}: {concept}",
            back=self._get_thinking_question(concept),
            tags=["rootcraft", "thinking", self.language]
        ))
        
        self.cards.extend(cards)
        return cards
    
    def _get_feynman_tip(self) -> str:
        """获取费曼技巧提示"""
        if self.language == "zh":
            return "试着用一句话向非专业人士解释这个概念，不要使用专业术语。"
        else:
            return "Try to explain this concept in one sentence to a non-expert without using jargon."
    
    def _get_thinking_question(self, concept: str) -> str:
        """获取思考问题"""
        if self.language == "zh":
            return f"如果没有{concept}，世界会怎样？为什么它很重要？"
        else:
            return f"What would happen without {concept}? Why is it important?"
    
    def generate_from_aha_moment(self, 
                                  topic: str, 
                                  insight: str,
                                  related_concepts: List[str] = None) -> List[AnkiCard]:
        """
        从"啊哈时刻"生成卡片
        
        Args:
            topic: 主题
            insight: 领悟内容
            related_concepts: 相关概念
        """
        cards = []
        
        # 卡片：啊哈时刻记录
        cards.append(AnkiCard(
            front=f"💡 {topic} - 啊哈时刻",
            back=insight,
            tags=["rootcraft", "aha", self.language]
        ))
        
        # 卡片：相关概念
        if related_concepts:
            cards.append(AnkiCard(
                front=f"与「{topic}」相关的概念",
                back="、".join(related_concepts),
                tags=["rootcraft", "related", self.language]
            ))
        
        self.cards.extend(cards)
        return cards
    
    def generate_from_taxonomy(self,
                                topic: str,
                                categories: Dict[str, List[str]]) -> List[AnkiCard]:
        """
        从分类学结构生成卡片
        
        Args:
            topic: 主题
            categories: 分类字典 {"分类名": ["子项1", "子项2"]}
        
        Example:
            topic="Python数据结构"
            categories={
                "序列": ["list", "tuple", "str"],
                "映射": ["dict"],
                "集合": ["set", "frozenset"]
            }
        """
        cards = []
        
        # 卡片1: 分类概览
        overview = "\n".join([f"- {cat}: {', '.join(items)}" 
                             for cat, items in categories.items()])
        cards.append(AnkiCard(
            front=f"{topic} - 分类结构",
            back=overview,
            tags=["rootcraft", "taxonomy", self.language]
        ))
        
        # 卡片2: 每个分类
        for category, items in categories.items():
            cards.append(AnkiCard(
                front=f"{topic} - {category}",
                back="、".join(items),
                tags=["rootcraft", "taxonomy", self.language]
            ))
        
        # 卡片3: MECE 检查
        cards.append(AnkiCard(
            front=f"{topic} 的 MECE 分析",
            back=self._get_meceReminder(topic, categories),
            tags=["rootcraft", "mece", self.language]
        ))
        
        self.cards.extend(cards)
        return cards
    
    def _get_meceReminder(self, topic: str, categories: Dict) -> str:
        """获取 MECE 检查提示"""
        if self.language == "zh":
            count = len(categories)
            total_items = sum(len(items) for items in categories.values())
            return f"共{count}个分类，{total_items}个项目。检查：是否全面？是否不重复？"
        else:
            count = len(categories)
            total_items = sum(len(items) for items in categories.values())
            return f"{count} categories, {total_items} items total. Check: Complete? Non-overlapping?"
    
    def export_to_csv(self, filepath: str = None) -> str:
        """导出为 CSV（Anki 兼容格式）"""
        import csv
        
        if filepath is None:
            filepath = os.path.expanduser("~/.openclaw/workspace/rootcraft/cards.csv")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["front", "back", "tags"])
            
            for card in self.cards:
                tags_str = ";".join(card.tags)
                writer.writerow([card.front, card.back, tags_str])
        
        return filepath
    
    def export_to_anki_package(self, filepath: str = None) -> str:
        """
        导出为 Anki 包（需要 genanki 库）
        
        如果没有 genanki 库，则回退到 CSV
        """
        try:
            import genanki
            
            # 创建卡组
            deck = genanki.Deck(
                2059400110,  # 随机ID
                "RootCraft Cards"
            )
            
            # 创建卡片模板
            model = genanki.Model(
                2059400111,
                "RootCraft Model",
                fields=[
                    {"name": "Front"},
                    {"name": "Back"},
                    {"name": "Tags"}
                ],
                templates=[
                    {
                        "name": "Card 1",
                        "qfmt": "<div class='front'>{{Front}}</div>",
                        "afmt": "<div class='back'>{{Back}}</div>"
                    }
                ]
            )
            
            # 添加卡片到卡组
            for card in self.cards:
                note = genanki.Note(
                    model=model,
                    fields=[card.front, card.back, ",".join(card.tags)]
                )
                deck.add_note(note)
            
            # 保存
            if filepath is None:
                filepath = os.path.expanduser("~/.openclaw/workspace/rootcraft/cards.apkg")
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            package = genanki.Package(deck)
            package.write_to_file(filepath)
            
            return filepath
            
        except ImportError:
            # 没有 genanki，回退到 CSV
            return self.export_to_csv()
    
    def get_summary(self) -> str:
        """获取卡片生成摘要"""
        if self.language == "zh":
            msg = f"📝 已生成 {len(self.cards)} 张 Anki 卡片\n\n"
            msg += "标签统计：\n"
        else:
            msg = f"📝 Generated {len(self.cards)} Anki cards\n\n"
            msg += "Tag summary:\n"
        
        # 统计标签
        tag_counts = {}
        for card in self.cards:
            for tag in card.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        for tag, count in tag_counts.items():
            msg += f"• {tag}: {count}\n"
        
        return msg


def example_usage():
    """使用示例"""
    # 中文示例
    print("=== 中文示例 ===")
    gen = AnkiCardGenerator(language="zh")
    
    # 从概念生成卡片
    gen.generate_from_concept(
        concept="第一性原理",
        definition="从最基本的事实和公理出发思考问题，而非依赖类比或传统智慧。",
        examples=[
            "马斯克思考电池成本：原材料是什么？每个原材料多少钱？能优化吗？",
            "孩子问：为什么要上學？ → 教育的本质是什么？"
        ],
        analogy="就像剥洋葱，一层层剥开，直到找到最核心的那一层",
        key_points=[
            "追问为什么直到不能再问",
            "不接受未经检验的假设",
            "从基本原则重新推导"
        ]
    )
    
    # 从啊哈时刻生成
    gen.generate_from_aha_moment(
        topic="学习",
        insight="学习的本质是建立联系，而不是存储信息",
        related_concepts=["记忆", "理解", "应用"]
    )
    
    # 从分类学生成
    gen.generate_from_taxonomy(
        topic="Python数据类型",
        categories={
            "数值": ["int", "float", "complex"],
            "序列": ["str", "list", "tuple", "bytes"],
            "映射": ["dict"],
            "集合": ["set", "frozenset"]
        }
    )
    
    print(gen.get_summary())
    
    # 导出
    csv_path = gen.export_to_csv()
    print(f"导出到: {csv_path}")
    
    # 英文示例
    print("\n=== English Example ===")
    gen_en = AnkiCardGenerator(language="en")
    gen_en.generate_from_concept(
        concept="First Principles Thinking",
        definition="Thinking from the most basic facts and axioms, rather than relying on analogies or conventional wisdom.",
        examples=[
            "Musk on battery costs: What are the raw materials? What's each material's price? Can we optimize?",
            "Child asks: Why go to school? → What's the essence of education?"
        ],
        analogy="Like peeling an onion, layer by layer, until you find the core"
    )
    
    print(gen_en.get_summary())


if __name__ == "__main__":
    example_usage()