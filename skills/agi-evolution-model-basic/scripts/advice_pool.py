#!/usr/bin/env python3
"""
建议池模块（Advice Pool）

功能：
- 存储软调节建议
- 查询软调节建议（由主循环调用）
- 记录采纳情况（由主循环调用）
- 清理过期建议
- 基于人格的个性化排序

设计原则：
- 超然存在：外环写入，主循环读取（单向流）
- 不强制执行：主循环自主决定是否采纳
- 时效性约束：过期建议自动清理
- 个性化排序：基于人格特质和采纳历史

数据结构：
- 建议：{id, content, priority, confidence, valid_until, vertex, based_on_intentionality, adoption_stats}
- 按顶点分类：drive, math, iteration
- 采纳统计：presented, adopted, effectiveness_sum
"""

import argparse
import json
import sys
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


class AdvicePool:
    """建议池"""
    
    def __init__(self, memory_dir: str = "./agi_memory"):
        self.memory_dir = memory_dir
        self.pool_file = f"{memory_dir}/advice_pool.json"
        
        # 建议池结构
        self.pool = {
            "drive": [],      # 针对得不到顶点的建议
            "math": [],       # 针对数学顶点的建议
            "iteration": []   # 针对自我迭代顶点的建议
        }
        
        # 元数据
        self.metadata = {
            "last_updated": None,
            "total_suggestions": 0,
            "active_suggestions": 0
        }
        
        # 加载现有建议池
        self._load()
    
    def add_suggestion(self, vertex: str, suggestion: Dict[str, Any]) -> str:
        """
        添加软调节建议
        
        Args:
            vertex: 目标顶点（drive/math/iteration）
            suggestion: 建议内容
                - content: 建议内容
                - priority: 优先级（0.0-1.0）
                - confidence: 置信度（0.0-1.0）
                - based_on_intentionality: 基于的意向性数据
                
        Returns:
            建议ID
        """
        if vertex not in self.pool:
            raise ValueError(f"Invalid vertex: {vertex}. Must be one of: drive, math, iteration")
        
        suggestion_with_metadata = {
            "id": str(uuid.uuid4()),
            "generation_time": datetime.now().isoformat(),
            "valid_until": (datetime.now() + timedelta(minutes=30)).isoformat(),
            "vertex": vertex,
            "content": suggestion.get('content', ''),
            "priority": suggestion.get('priority', 0.5),
            "confidence": suggestion.get('confidence', 0.5),
            "based_on_intentionality": suggestion.get('based_on_intentionality', {}),
            "adoption_stats": {
                "presented": 0,
                "adopted": 0,
                "effectiveness_sum": 0.0
            }
        }
        
        self.pool[vertex].append(suggestion_with_metadata)
        
        # 清理过期建议
        self._cleanup_expired()
        
        # 更新元数据
        self._update_metadata()
        
        # 保存
        self._save()
        
        return suggestion_with_metadata['id']
    
    def query_suggestions(self, vertex: str, context: Dict[str, Any] = None,
                          personality: Dict[str, Any] = None, 
                          limit: int = 3) -> List[Dict[str, Any]]:
        """
        查询软调节建议（由主循环调用）
        
        Args:
            vertex: 目标顶点（drive/math/iteration）
            context: 上下文信息
            personality: 人格数据
            limit: 返回建议数量限制
            
        Returns:
            建议列表（已排序）
        """
        # 1. 清理过期建议
        self._cleanup_expired()
        
        # 2. 过滤顶点
        vertex_suggestions = self.pool.get(vertex, [])
        
        if not vertex_suggestions:
            return []
        
        # 3. 过滤相关性
        relevant_suggestions = [
            s for s in vertex_suggestions
            if self._check_relevance(s, context) > 0.5
        ]
        
        if not relevant_suggestions:
            return []
        
        # 4. 基于人格排序
        if personality:
            scored_suggestions = [
                {
                    **s,
                    "personalized_score": self._calculate_personalized_score(
                        s,
                        personality
                    )
                }
                for s in relevant_suggestions
            ]
        else:
            scored_suggestions = [
                {
                    **s,
                    "personalized_score": s['priority'] * s['confidence']
                }
                for s in relevant_suggestions
            ]
        
        # 按个性化得分排序
        scored_suggestions.sort(
            key=lambda x: x['personalized_score'],
            reverse=True
        )
        
        # 5. 返回Top N
        top_suggestions = scored_suggestions[:limit]
        
        # 6. 更新呈现次数
        for s in top_suggestions:
            s['adoption_stats']['presented'] += 1
        
        # 保存更新
        self._save()
        
        return top_suggestions
    
    def record_adoption(self, suggestion_id: str, adopted: bool,
                        effectiveness: Optional[float] = None) -> bool:
        """
        记录采纳情况（由主循环调用）
        
        Args:
            suggestion_id: 建议ID
            adopted: 是否采纳
            effectiveness: 有效性评分（0.0-1.0，可选）
            
        Returns:
            是否成功记录
        """
        # 在所有顶点中查找建议
        found = False
        
        for vertex, suggestions in self.pool.items():
            for suggestion in suggestions:
                if suggestion['id'] == suggestion_id:
                    found = True
                    
                    if adopted:
                        suggestion['adoption_stats']['adopted'] += 1
                        if effectiveness is not None:
                            suggestion['adoption_stats']['effectiveness_sum'] += effectiveness
                    
                    break
            
            if found:
                break
        
        if found:
            self._update_metadata()
            self._save()
        
        return found
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取建议池统计信息
        
        Returns:
            统计信息
        """
        stats = {
            "metadata": self.metadata,
            "by_vertex": {}
        }
        
        for vertex, suggestions in self.pool.items():
            if suggestions:
                total_presented = sum(s['adoption_stats']['presented'] for s in suggestions)
                total_adopted = sum(s['adoption_stats']['adopted'] for s in suggestions)
                total_effectiveness = sum(s['adoption_stats']['effectiveness_sum'] for s in suggestions)
                
                adoption_rate = total_adopted / max(total_presented, 1)
                avg_effectiveness = total_effectiveness / max(total_adopted, 1)
                
                stats["by_vertex"][vertex] = {
                    "active_suggestions": len(suggestions),
                    "total_presented": total_presented,
                    "total_adopted": total_adopted,
                    "adoption_rate": adoption_rate,
                    "avg_effectiveness": avg_effectiveness
                }
        
        return stats
    
    def clear_expired(self) -> int:
        """
        清理所有过期建议
        
        Returns:
            清理的建议数量
        """
        before_count = sum(len(suggestions) for suggestions in self.pool.values())
        self._cleanup_expired()
        self._save()
        after_count = sum(len(suggestions) for suggestions in self.pool.values())
        
        return before_count - after_count
    
    def _load(self):
        """从文件加载建议池"""
        try:
            with open(self.pool_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.pool = data.get("pool", self.pool)
                self.metadata = data.get("metadata", self.metadata)
        except (FileNotFoundError, json.JSONDecodeError):
            # 文件不存在或格式错误，使用默认值
            pass
    
    def _save(self):
        """保存建议池到文件"""
        data = {
            "pool": self.pool,
            "metadata": self.metadata
        }
        
        with open(self.pool_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _cleanup_expired(self):
        """清理过期建议"""
        current_time = datetime.now()
        
        for vertex, suggestions in self.pool.items():
            self.pool[vertex] = [
                s for s in suggestions
                if datetime.fromisoformat(s['valid_until']) > current_time
            ]
    
    def _update_metadata(self):
        """更新元数据"""
        self.metadata['last_updated'] = datetime.now().isoformat()
        self.metadata['total_suggestions'] = sum(
            len(suggestions) for suggestions in self.pool.values()
        )
        self.metadata['active_suggestions'] = sum(
            len(suggestions) for suggestions in self.pool.values()
        )
    
    def _check_relevance(self, suggestion: Dict[str, Any],
                         context: Dict[str, Any] = None) -> float:
        """
        检查建议与上下文的相关性
        
        Args:
            suggestion: 建议
            context: 上下文
            
        Returns:
            相关性得分（0.0-1.0）
        """
        if not context:
            return 0.5
        
        based_on = suggestion.get('based_on_intentionality', {})
        context_intentionality = context.get('intentionality', {})
        
        if not based_on or not context_intentionality:
            return 0.5
        
        # 计算匹配度
        match_score = 0.0
        dimensions = ['agent', 'direction', 'content']
        
        for dimension in dimensions:
            if based_on.get(dimension) == context_intentionality.get(dimension):
                match_score += 1.0 / len(dimensions)
        
        return match_score
    
    def _calculate_personalized_score(self, suggestion: Dict[str, Any],
                                       personality: Dict[str, Any]) -> float:
        """
        计算基于人格的个性化得分
        
        Args:
            suggestion: 建议
            personality: 人格数据
            
        Returns:
            个性化得分
        """
        base_score = suggestion['priority'] * suggestion['confidence']
        
        # 基于采纳历史调整
        adoption_rate = suggestion['adoption_stats']['adopted'] / max(
            suggestion['adoption_stats']['presented'],
            1
        )
        
        # 基于人格特质调整
        conscientiousness = personality.get('conscientiousness', 0.5)
        openness = personality.get('openness', 0.5)
        
        # 谨慎性越高，越倾向于采纳历史成功的建议
        personality_factor = conscientiousness * 0.3 + openness * 0.2
        
        personalized_score = base_score * (1 + adoption_rate) * (1 + personality_factor)
        
        return personalized_score


def main():
    parser = argparse.ArgumentParser(description="建议池模块")
    parser.add_argument("--memory-dir", default="./agi_memory", help="记忆目录")
    parser.add_argument("--action", choices=["add", "query", "record", "stats", "clear"], 
                        required=True, help="操作类型")
    parser.add_argument("--vertex", choices=["drive", "math", "iteration"], 
                        help="目标顶点")
    parser.add_argument("--suggestion", help="建议内容（JSON）")
    parser.add_argument("--suggestion-id", help="建议ID")
    parser.add_argument("--adopted", type=bool, help="是否采纳")
    parser.add_argument("--effectiveness", type=float, help="有效性评分")
    parser.add_argument("--context", help="上下文（JSON）")
    parser.add_argument("--personality", help="人格数据（JSON文件）")
    parser.add_argument("--limit", type=int, default=3, help="返回建议数量限制")
    parser.add_argument("--output", help="输出文件")
    
    args = parser.parse_args()
    
    # 创建建议池
    pool = AdvicePool(memory_dir=args.memory_dir)
    
    if args.action == "add":
        # 添加建议
        if not args.vertex or not args.suggestion:
            print("Error: --vertex and --suggestion are required for add action")
            sys.exit(1)
        
        suggestion = json.loads(args.suggestion)
        suggestion_id = pool.add_suggestion(args.vertex, suggestion)
        
        result = {
            "success": True,
            "suggestion_id": suggestion_id,
            "message": "建议已添加到建议池"
        }
    
    elif args.action == "query":
        # 查询建议
        if not args.vertex:
            print("Error: --vertex is required for query action")
            sys.exit(1)
        
        context = json.loads(args.context) if args.context else None
        
        personality = None
        if args.personality:
            with open(args.personality, 'r', encoding='utf-8') as f:
                personality = json.load(f)
        
        suggestions = pool.query_suggestions(
            args.vertex,
            context,
            personality,
            args.limit
        )
        
        result = {
            "success": True,
            "vertex": args.vertex,
            "count": len(suggestions),
            "suggestions": suggestions
        }
    
    elif args.action == "record":
        # 记录采纳情况
        if not args.suggestion_id or args.adopted is None:
            print("Error: --suggestion-id and --adopted are required for record action")
            sys.exit(1)
        
        success = pool.record_adoption(
            args.suggestion_id,
            args.adopted,
            args.effectiveness
        )
        
        result = {
            "success": success,
            "message": "采纳情况已记录" if success else "建议ID不存在"
        }
    
    elif args.action == "stats":
        # 获取统计信息
        result = {
            "success": True,
            "stats": pool.get_stats()
        }
    
    elif args.action == "clear":
        # 清理过期建议
        cleared_count = pool.clear_expired()
        
        result = {
            "success": True,
            "cleared_count": cleared_count,
            "message": f"已清理 {cleared_count} 条过期建议"
        }
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    sys.exit(0)


if __name__ == "__main__":
    main()
