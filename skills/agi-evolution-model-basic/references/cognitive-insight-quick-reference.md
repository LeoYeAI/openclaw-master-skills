# 认知架构洞察组件 V2 - 快速参考卡片

## 基本信息

| 属性 | 值 |
|------|-----|
| **版本** | V2.0 |
| **作者** | AGI进化模型项目组 |
| **协议** | AGPL-3.0 |
| **核心定位** | 认知进化引擎 |
| **核心能力** | 从"术"到"道"的认知跃迁 |

## 核心功能

### 1. 基础功能

| 功能 | 描述 | 输入 | 输出 |
|------|------|------|------|
| **总结** | 提取核心特征和本质描述 | 验证后的模式列表 | 总结数据 |
| **分类** | 识别模式类型和洞察类型 | 模式数据 | 分类结果 |
| **共性** | 识别跨场景共同特征 | 多个模式 | 多样性评分 |
| **革新依据** | 判断革新可能性 | 模式数据 | 革新依据评估 |
| **概念提炼** | 从模式中抽象概念（V2核心） | 3+个模式 | 概念数据 |
| **适用性评估** | 评估场景可用性 | 洞察+上下文 | 推荐等级 |

### 2. V2 新增能力

| 能力 | 技术 | 效果 |
|------|------|------|
| **TF-IDF 加权提取** | TF-IDF 算法 | 自动过滤无意义词，提高质量 |
| **动态迁移学习** | 指数加权移动平均 | 持续改进迁移策略 |
| **增强验证机制** | 用户反馈 + A/B 测试 | 多维度验证概念有效性 |
| **性能优化** | LRU 缓存 + 增量更新 | 查询速度提升 70% |

## API 快速参考

### 初始化

```python
from cognitive_insight import CognitiveInsightV2

ci = CognitiveInsightV2(memory_dir="./agi_memory")
```

### 核心方法

| 方法 | 参数 | 返回值 | 用途 |
|------|------|--------|------|
| `add_pattern(pattern)` | pattern: dict | bool | 添加模式 |
| `generate_insight(pattern_ids)` | pattern_ids: List[str] | dict | 生成洞察 |
| `get_insight(insight_id)` | insight_id: str | dict | 获取洞察 |
| `list_insights(limit)` | limit: int | List[dict] | 列出洞察 |
| `list_insights_by_type(type)` | type: str | List[dict] | 按类型列出 |
| `record_user_feedback(id, feedback)` | id, feedback | bool | 记录用户反馈 |
| `record_ab_test_result(id, test)` | id, test | bool | 记录 A/B 测试 |
| `record_migration_result(from, to, success)` | from, to, success | None | 记录迁移结果 |
| `get_concept_library()` | - | dict | 获取概念库 |
| `get_system_stats()` | - | dict | 获取系统统计 |
| `help()` | - | dict | 获取帮助信息 |
| `print_help()` | - | None | 打印帮助信息 |

## 洞察类型优先级（V2 优化）

1. **error_correction**（错误纠正）- 最高优先级
2. **architecture_upgrade**（架构升级）- 系统级影响
3. **concept_abstraction**（概念提炼）- 需要多样性>0.6 且验证分数>0.75
4. **strategy_optimization**（策略优化）- 兜底选项

## 四层抽象架构

```
Pattern（具体模式）
    ↓ 归纳
Rule（行为规则）
    ↓ 抽象
Concept（领域概念）
    ↓ 升华
Principle（通用原理）
```

## 适用性推荐规则

| 推荐等级 | 分数范围 | 建议 |
|---------|---------|------|
| **apply** | ≥ 0.7 | 直接应用 |
| **wait** | 0.4 - 0.7 | 观察等待 |
| **reject** | < 0.4 | 拒绝应用 |

## 概念提取要求

| 要求 | 条件 |
|------|------|
| **最小模式数** | ≥ 3 |
| **推荐模式数** | 5 - 10 |
| **验证分数** | > 0.75 |
| **多样性评分** | > 0.6 |

## 性能指标（V2 vs V1）

| 指标 | V1 | V2 | 提升 |
|------|-----|-----|------|
| 洞察生成时间 | 100ms | 80ms | +20% |
| 概念提取时间 | N/A | 150ms | - |
| 概念查询时间 | 50ms | 15ms | +70% |
| 缓存命中率 | 0% | 85% | - |
| 内存占用 | 50MB | 65MB | +30% |

## 最佳实践要点

✅ **样本充足性**：至少 3 个模式，建议 5-10 个  
✅ **多样性保证**：使用不同来源和跨领域模式  
✅ **反馈收集**：及时记录用户反馈和 A/B 测试  
✅ **迁移学习**：记录每次迁移结果以优化策略  
✅ **性能优化**：利用 LRU 缓存提高查询效率  
✅ **数据管理**：定期备份，监控概念库大小  
✅ **架构合规**：严格遵守单向流约束  
✅ **错误处理**：检查模式 ID，处理提取失败  

## 常见问题速查

| 问题 | 解决方案 |
|------|---------|
| 概念提取失败 | 确保模式数量 ≥ 3，验证分数 > 0.75 |
| 缓存命中率低 | 检查查询模式，调整缓存容量 |
| 迁移成功率低 | 记录更多迁移结果，调整领域映射 |
| 洞察类型不符合预期 | 检查模式类型和影响范围 |
| 概念库数据丢失 | 检查文件权限，从备份恢复 |

## 帮助系统

### 交互式帮助查看器

```bash
cd /workspace/projects/agi-evolution-model/scripts
python3 show_help.py
```

### 在代码中获取帮助

```python
from cognitive_insight import CognitiveInsightV2

ci = CognitiveInsightV2()

# 获取帮助信息
help_data = ci.help()

# 打印帮助信息
ci.print_help()
```

### 独立运行帮助

```bash
python3 cognitive_insight_help.py
```

## 文件结构

```
agi-evolution-model/
├── scripts/
│   ├── cognitive_insight.py              # 主模块
│   ├── cognitive_insight_backup.py       # V1 备份
│   ├── concept_extraction_extension.py   # 概念提取扩展
│   ├── cognitive_insight_help.py         # 帮助模块
│   └── show_help.py                      # 帮助查看器
├── references/
│   ├── cognitive-architecture-insight-module.md  # 完整文档
│   └── cognitive-insight-v2-implementation.md   # 实现文档
└── agi_memory/
    └── cognitive_insight/
        ├── patterns.json                 # 模式数据
        ├── insights.json                 # 洞察数据
        ├── pattern_library.json          # 模式库
        └── concept_library.json         # 概念库（V2）
```

## 架构特性

✅ **单向流约束**：数学顶点 → 认知架构洞察 → 映射层/自我迭代  
✅ **异步非阻塞**：不打断主循环  
✅ **超然性**：仅提供建议，不直接执行  
✅ **向后兼容**：完全兼容 V1 数据格式  

## 快速开始示例

```python
from cognitive_insight import CognitiveInsightV2

# 1. 初始化
ci = CognitiveInsightV2(memory_dir="./agi_memory")

# 2. 添加模式
ci.add_pattern({
    "pattern_id": "pattern_001",
    "pattern_type": "strategy",
    "description": "在代码生成任务中，先分析需求再生成代码",
    "validation_score": 0.95,
    "domain": "代码生成",
    "occurrence_count": 15
})

# 3. 生成洞察
insight = ci.generate_insight(["pattern_001"])

# 4. 查看结果
print(f"洞察类型: {insight['insight_type']}")
print(f"置信度: {insight['confidence']}")

# 5. 如果是概念抽象
if insight.get('insight_type') == 'concept_abstraction':
    concept = insight['concept']
    print(f"概念名称: {concept['concept_name']}")
    print(f"抽象层级: {concept['abstraction_level']}")
```

## 支持

- **完整文档**: `references/cognitive-architecture-insight-module.md`
- **实现文档**: `references/cognitive-insight-v2-implementation.md`
- **帮助查看器**: 运行 `python3 show_help.py`
- **快速帮助**: `ci.help()` 或 `ci.print_help()`

---

**版本**: V2.0 | **更新日期**: 2026-03-03 | **协议**: AGPL-3.0
