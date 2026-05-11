#!/usr/bin/env python3
"""
认知架构洞察组件 V2 帮助模块（精简版）
专注于快速查询和问题解决
"""

from typing import Dict, List


class CognitiveInsightHelp:
    """认知架构洞察组件帮助类（精简版）"""
    
    def __init__(self):
        self.version = "2.0"
        self.author = "AGI进化模型项目组"
        self.license = "AGPL-3.0"
    
    def get_help(self) -> Dict:
        """获取帮助信息（精简版）"""
        return {
            'version': self.version,
            'author': self.author,
            'license': self.license,
            'description': self._get_description(),
            'api_reference': self._get_api_reference(),
            'faq': self._get_faq(),
            'troubleshooting': self._get_troubleshooting()
        }
    
    def _get_description(self) -> str:
        """获取组件描述"""
        return """
认知架构洞察组件 V2 (Cognitive Architecture Insight Module V2)
===========================================================

核心定位：AGI进化模型的"认知进化引擎"，负责从数学顶点输出的结构化模式中
提取深度洞察，实现从"术"（技巧）到"道"（原理）的认知跃迁。

主要能力：
- 模式总结与特征提取
- 智能分类（优化优先级）
- 跨场景共性识别
- 革新依据评估
- 概念提炼（V2核心）：四层抽象架构
- 适用性评估

架构特性：
- 单向流约束：严格遵循 数学顶点 → 认知架构洞察 → 映射层/自我迭代
- 异步非阻塞：不打断主循环
- 超然性：仅提供建议，不直接执行
- 向后兼容：完全兼容 V1 数据格式
"""
    
    def _get_api_reference(self) -> Dict:
        """获取API参考"""
        return {
            'CognitiveInsightV2': {
                '类名': 'CognitiveInsightV2',
                '初始化': {
                    '方法': '__init__(memory_dir: str = "./agi_memory")',
                    '参数': {
                        'memory_dir': 'str - 记忆存储目录路径，默认为 "./agi_memory"'
                    },
                    '返回': 'CognitiveInsightV2 实例'
                },
                '核心方法': [
                    {
                        '方法': 'add_pattern(pattern: dict) -> bool',
                        '描述': '添加数学顶点验证后的模式',
                        '参数': {
                            'pattern_id': 'str - 模式唯一标识',
                            'pattern_type': 'str - 模式类型',
                            'description': 'str - 模式描述',
                            'validation_score': 'float - 验证分数 (0.0-1.0)',
                            'domain': 'str - 所属领域',
                            'occurrence_count': 'int - 出现次数'
                        },
                        '返回': 'bool - 是否成功添加'
                    },
                    {
                        '方法': 'generate_insight(pattern_ids: List[str]) -> dict',
                        '描述': '生成洞察（V2支持概念提炼）',
                        '参数': {
                            'pattern_ids': 'List[str] - 模式ID列表'
                        },
                        '返回': 'dict - 洞察数据'
                    },
                    {
                        '方法': 'get_insight(insight_id: str) -> Optional[dict]',
                        '描述': '根据ID获取洞察',
                        '返回': 'dict or None - 洞察数据'
                    },
                    {
                        '方法': 'list_insights(limit: int = 10) -> List[dict]',
                        '描述': '列出最新洞察',
                        '返回': 'List[dict] - 洞察列表（按时间倒序）'
                    },
                    {
                        '方法': 'record_user_feedback(insight_id: str, feedback: dict) -> bool',
                        '描述': '记录用户反馈',
                        '参数': {
                            'insight_id': 'str - 洞察ID',
                            'rating': 'int - 评分（1-5）',
                            'comment': 'str - 评论内容',
                            'scenario': 'str - 应用场景'
                        },
                        '返回': 'bool - 是否成功记录'
                    },
                    {
                        '方法': 'get_concept_library() -> dict',
                        '描述': '获取概念库',
                        '返回': 'dict - 概念库数据'
                    },
                    {
                        '方法': 'get_system_stats() -> dict',
                        '描述': '获取系统统计信息',
                        '返回': 'dict - 系统统计'
                    },
                    {
                        '方法': 'help() -> dict',
                        '描述': '获取帮助信息',
                        '返回': 'dict - 帮助数据'
                    },
                    {
                        '方法': 'print_help()',
                        '描述': '打印帮助信息到控制台',
                        '返回': 'None'
                    }
                ]
            },
            'ConceptExtractionExtension': {
                '类名': 'ConceptExtractionExtension',
                '描述': '概念提取扩展模块（V2核心）',
                '核心方法': [
                    {
                        '方法': 'extract_concept(patterns: List[dict]) -> Optional[dict]',
                        '描述': '从模式中提取概念（使用TF-IDF）',
                        '参数': {'patterns': 'List[dict] - 模式列表（至少3个）'},
                        '返回': 'dict or None - 概念数据'
                    },
                    {
                        '方法': 'list_concepts_by_level(level: str) -> List[dict]',
                        '描述': '按抽象层级列出概念',
                        '参数': {'level': 'str - 抽象层级（rule/concept/principle）'},
                        '返回': 'List[dict] - 概念列表'
                    },
                    {
                        '方法': 'get_cache_stats() -> dict',
                        '描述': '获取缓存统计',
                        '返回': 'dict - 缓存统计'
                    },
                    {
                        '方法': 'get_learning_stats() -> dict',
                        '描述': '获取学习统计',
                        '返回': 'dict - 学习统计'
                    }
                ]
            }
        }
    
    def _get_faq(self) -> List[Dict]:
        """获取常见问题解答"""
        return [
            {
                '问题': 'Q1: V2 版本是否兼容 V1 的数据？',
                '回答': 'A: 是的，V2 完全兼容 V1 的数据格式。可以直接升级，无需迁移数据。'
            },
            {
                '问题': 'Q2: 概念提炼需要多少个模式？',
                '回答': 'A: 至少需要 3 个模式。建议使用 5-10 个模式以提高概念的质量和置信度。模式的验证分数应 > 0.75。'
            },
            {
                '问题': 'Q3: 如何提高概念提取的成功率？',
                '回答': 'A: 1) 使用更多高质量模式（> 0.75）；2) 增加模式来源的多样性；3) 使用跨领域模式；4) 提供清晰的描述。'
            },
            {
                '问题': 'Q4: 概念提取失败怎么办？',
                '回答': 'A: 1) 确保模式数量 ≥ 3；2) 检查模式验证分数 > 0.75；3) 增加模式来源的多样性；4) 系统会自动降级到策略优化。'
            },
            {
                '问题': 'Q5: 如何查看帮助信息？',
                '回答': 'A: 使用 ci.help() 获取结构化帮助数据，或 ci.print_help() 打印帮助信息。也可以运行 python3 scripts/show_help.py 使用交互式帮助查看器。'
            },
            {
                '问题': 'Q6: 适用性评估的推荐等级是如何确定的？',
                '回答': 'A: 基于加权总分：apply（≥0.7）、wait（0.4-0.7）、reject（<0.4）。对于概念类型，额外评估抽象层级匹配度。'
            },
            {
                '问题': 'Q7: V2 相比 V1 性能提升了多少？',
                '回答': 'A: 洞察生成速度提升约 20%；概念查询速度提升 70%；缓存命中率可达 85%。'
            },
            {
                '问题': 'Q8: 如何判断一个概念是否有效？',
                '回答': 'A: 通过多个维度判断：1) 验证计数；2) 用户反馈评分；3) A/B 测试结果；4) 迁移成功率；5) 适用性历史。'
            }
        ]
    
    def _get_troubleshooting(self) -> Dict:
        """获取故障排查指南"""
        return {
            '常见问题': [
                {
                    '问题': '概念提取失败',
                    '可能原因': [
                        '模式数量不足（少于 3 个）',
                        '模式多样性不足',
                        '验证分数过低'
                    ],
                    '解决方案': [
                        '确保至少添加 3 个模式',
                        '增加模式来源的多样性',
                        '提高模式的验证分数（> 0.75）'
                    ]
                },
                {
                    '问题': '缓存命中率低',
                    '可能原因': [
                        '查询的模式不重复',
                        '缓存容量太小',
                        '查询模式随机性高'
                    ],
                    '解决方案': [
                        '检查查询模式是否过于随机',
                        '调整缓存容量（默认 100）'
                    ]
                },
                {
                    '问题': '迁移成功率低',
                    '可能原因': [
                        '迁移路径选择不当',
                        '源领域和目标领域差异大',
                        '迁移历史数据不足'
                    ],
                    '解决方案': [
                        '记录更多迁移结果以供学习',
                        '调整领域映射表'
                    ]
                },
                {
                    '问题': '洞察类型不符合预期',
                    '可能原因': [
                        '分类逻辑优先级不匹配',
                        '影响范围判断错误',
                        '多样性评分计算异常'
                    ],
                    '解决方案': [
                        '检查模式类型和影响范围设置',
                        '调整多样性阈值（当前 0.6）'
                    ]
                }
            ]
        }
    
    def print_help(self):
        """打印帮助信息"""
        help_data = self.get_help()
        
        print("=" * 80)
        print("认知架构洞察组件 V2 帮助信息")
        print("=" * 80)
        print()
        
        print(f"版本: {help_data['version']}")
        print(f"作者: {help_data['author']}")
        print(f"协议: {help_data['license']}")
        print()
        
        print(help_data['description'])
        print()
        
        print("=" * 80)
        print("API 参考")
        print("=" * 80)
        print()
        for class_name, methods in help_data['api_reference'].items():
            print(f"【{class_name}】")
            if '核心方法' in methods:
                for method in methods['核心方法']:
                    print(f"  • {method['方法']}")
                    print(f"    {method['描述']}")
                print()
        
        print("=" * 80)
        print("常见问题 (FAQ)")
        print("=" * 80)
        print()
        for faq in help_data['faq']:
            print(faq['问题'])
            print(faq['回答'])
            print()


def show_help():
    """显示帮助信息"""
    helper = CognitiveInsightHelp()
    helper.print_help()


if __name__ == "__main__":
    show_help()
