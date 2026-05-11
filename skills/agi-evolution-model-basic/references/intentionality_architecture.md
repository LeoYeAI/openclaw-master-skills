# 工程意向性分析模组架构文档（阴性后台）

## 目录
1. [概述](#概述)
2. [核心概念](#核心概念)
3. [模块组成](#模块组成)
4. [数据格式](#数据格式)
5. [接口规范](#接口规范)
6. [信息流](#信息流)
7. [使用示例](#使用示例)
8. [设计原则](#设计原则)

---

## 概述

### 设计目标
工程意向性分析模组是AGI进化模型的**阴性后台独立运行模组**，默默运行于主循环之外，采用"被动响应 + 时效性约束"设计模式。外圈持续收集、分类、分析意向性数据，生成软调节建议，但不主动干预主循环，仅在主循环查询时响应。

### 核心特性
- **独立性**：完全独立运行，不依赖主循环触发，有自己的生命周期
- **阴性属性**：被动、隐性、柔性，像影子一样默默伴随主循环
- **后台运行**：不阻塞主循环，在后台持续积累和分析数据
- **时效性**：软调节建议具有时间窗口约束，过期自动失效
- **超然性**：不参与主循环执行，保持独立性和客观性
- **软调节**：通过建议间接影响主循环，不强制执行
- **全局视角**：从全局角度观察和分析系统运行

### 运行模式

**主循环（阳性前台）**：
- 主动运行、直接执行
- 按需查询外圈获取软调节建议
- 显性参与用户交互

**外环（阴性后台）**：
- 默默运行、独立后台
- 持续收集、分类、分析意向性
- 被动响应主循环的查询
- 建议具有时效性约束

### 与主循环的关系
| 特性 | 主循环（阳性前台） | 外环（阴性后台） |
|------|-------------------|-------------------|
| 运行模式 | 前台主动运行 | 后台默默运行 |
| 参与方式 | 直接参与执行 | 不参与主循环 |
| 响应方式 | 实时响应 | 被动响应查询 |
| 视角 | 局部/实时 | 全局/长期 |
| 调节特性 | 硬性操作 | 软调节建议 |
| 时效性 | 即时执行 | 具有时效性约束 |
| 哲学属性 | 阳（主动、显性） | 阴（被动、隐性） |

---

## 核心概念

### 意向性（Intentionality）
意向性指意识"关于"（aboutness）或"指向"（directedness）某对象的根本属性，不是"意图"（intention），而是意识与世界建立意义关联的结构性条件。

### 分类维度

#### 1. 按主体分类
- **自身意向性**：主体对自身心理状态的直接指向与觉知
  - 特点：第一人称权威性、前反思自明性、自我指涉结构
- **他人意向性**：主体将意向状态归因于其他心智主体
  - 特点：推断性、社会规范性、可错性、交互建构性

#### 2. 按方向分类
- **主动意向性**：有意识、有目的地指向某对象
  - 特点：目标导向、注意资源分配、可报告性、责任归属
- **被动意向性**：被外部刺激或内部状态牵引
  - 特点：刺激驱动、前注意加工、身体优先性、适应性功能

#### 3. 按内容分类
- **知觉意向性**：关于感知和觉察
- **信念意向性**：关于相信和认为
- **欲望意向性**：关于想要和希望

#### 4. 按实现方式分类
- **内在意向性**：本质的、固有的意向性
- **派生意向性**：衍生、获得的意向性

---

## 模块组成

### 1. 意向性收集模块（intentionality_collector.py）

**功能**：
- 收集来自用户、系统内部、外部的意向性数据
- 预处理数据（格式转换、数据清洗、特征提取）
- 初步识别意向性类型和基本特征

**核心方法**：
```python
collect_from_user(user_input: str) -> Dict[str, Any]
collect_from_system(internal_state: Dict) -> Dict[str, Any]
collect_from_external(external_data: Dict) -> Dict[str, Any]
preprocess(data: Dict) -> Dict[str, Any]
preliminary_identify(data: Dict) -> Dict[str, Any]
```

**使用示例**：
```bash
# 收集用户输入
python3 scripts/intentionality_collector.py \
  --source user \
  --content "我想要学习Python编程" \
  --output collected.json
```

### 2. 意向性分类模块（intentionality_classifier.py）

**功能**：
- 按主体分类：自身 / 他人
- 按方向分类：主动 / 被动
- 按内容分类：知觉 / 信念 / 欲望
- 按实现方式分类：内在 / 派生
- 计算分类置信度

**核心方法**：
```python
classify_by_agent(data: Dict) -> Dict[str, Any]
classify_by_direction(data: Dict) -> Dict[str, Any]
classify_by_content(data: Dict) -> Dict[str, Any]
classify_by_realization(data: Dict) -> Dict[str, Any]
classify(data: Dict) -> Dict[str, Any]
```

**使用示例**：
```bash
# 完整分类
python3 scripts/intentionality_classifier.py \
  --input collected.json \
  --dimension all \
  --output classified.json
```

### 3. 意向性分析模块（intentionality_analyzer.py）

**功能**：
- 强度分析：评估意向性的显著性强弱
- 紧迫性分析：评估意向性的时间维度
- 优先级分析：基于人格和马斯洛需求评估优先级

**核心方法**：
```python
analyze_intensity(classification: Dict, data: Dict) -> Dict[str, Any]
analyze_urgency(classification: Dict, data: Dict) -> Dict[str, Any]
analyze_priority(analysis: Dict, personality: Dict = None) -> Dict[str, Any]
analyze(classification: Dict, data: Dict, personality: Dict = None) -> Dict[str, Any]
```

**使用示例**：
```bash
# 完整分析
python3 scripts/intentionality_analyzer.py \
  --classification classified.json \
  --data collected.json \
  --personality personality.json \
  --dimension all \
  --output analyzed.json
```

### 4. 意向性调节模块（intentionality_regulator.py）

**功能**：
- 基于历史经验生成最优解
- 生成软调节建议
- 提供给自我迭代顶点
- 收集反馈

**核心方法**：
```python
generate_optimal_solution(analysis: Dict, history: List = None) -> Dict[str, Any]
generate_soft_regulation(analysis: Dict, optimal_solution: Dict) -> Dict[str, Any]
collect_feedback(regulation_id: str, outcome: Dict) -> Dict[str, Any]
```

**使用示例**：
```bash
# 生成调节建议
python3 scripts/intentionality_regulator.py \
  --analysis analyzed.json \
  --history feedback_history.json \
  --output regulation.json
```

### 5. 超然性保持模块（transcendence_keeper.py）

**功能**：
- 客观评估机制
- 冲突避免策略
- 独立性保障机制

**核心方法**：
```python
objective_assess(regulation: Dict, system_state: Dict = None) -> Dict[str, Any]
detect_conflict(regulation: Dict, main_loop_state: Dict) -> Dict[str, Any]
ensure_independence(regulation: Dict) -> Dict[str, Any]
evaluate_transcendence(regulation: Dict, main_loop_state: Dict = None) -> Dict[str, Any]
```

**使用示例**：
```bash
# 综合评估
python3 scripts/transcendence_keeper.py \
  --regulation regulation.json \
  --main-loop-state main_loop.json \
  --component all \
  --output transcendence_check.json
```

---

## 数据格式

### 1. 意向性数据对象（IntentionalityData）
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-02-22T10:00:00Z",
  "source": "user",
  "raw_content": "我想要学习Python编程",
  "preprocessed": {
    "content": "我想要学习Python编程",
    "length": 11,
    "word_count": 6
  },
  "features": {
    "self_agent": [{"keyword": "我", "count": 2}],
    "active_direction": [{"keyword": "想要", "count": 1}],
    "desire_content": [{"keyword": "想要", "count": 1}],
    "sentence_count": 1,
    "emotion": []
  },
  "preliminary_identification": {
    "likely_agent": "self",
    "likely_direction": "active",
    "likely_content": "desire"
  }
}
```

### 2. 分类结果（ClassificationResult）
```json
{
  "agent": {
    "type": "self",
    "confidence": 0.85,
    "evidence": ["关键词'我'出现2次"],
    "all_scores": {"self": 2.3, "other": 0.0}
  },
  "direction": {
    "type": "active",
    "confidence": 0.78,
    "evidence": ["关键词'想要'出现1次"],
    "all_scores": {"active": 1.3, "passive": 0.0}
  },
  "content": {
    "type": "desire",
    "confidence": 0.72,
    "evidence": ["关键词'想要'出现1次"],
    "all_scores": {"perception": 0.0, "belief": 0.0, "desire": 1.3}
  },
  "realization": {
    "type": "derived",
    "confidence": 0.60,
    "evidence": ["无明确指示，默认为派生意向性"],
    "all_scores": {"intrinsic": 0.0, "derived": 0.0}
  },
  "overall_confidence": 0.74
}
```

### 3. 分析结果（AnalysisResult）
```json
{
  "timestamp": "2025-02-22T10:00:05Z",
  "intensity": {
    "score": 0.65,
    "level": "medium",
    "components": {
      "confidence": 0.22,
      "word_count": 0.04,
      "keyword_count": 0.12,
      "emotion_strength": 0.00
    },
    "thresholds": {"low": 0.3, "medium": 0.6, "high": 0.8}
  },
  "urgency": {
    "score": 0.45,
    "level": "medium",
    "components": {
      "time_indicators": 0.00,
      "urgency_keywords": 0.00,
      "active_direction": 0.10
    },
    "indicators_found": [],
    "thresholds": {"low": 0.3, "medium": 0.6, "high": 0.8}
  },
  "priority": {
    "score": 0.52,
    "level": "medium",
    "components": {
      "intensity": 0.20,
      "urgency": 0.14,
      "maslow_alignment": 0.10,
      "personality_match": 0.10
    },
    "aligned_with_maslow": "self_actualization",
    "thresholds": {"low": 0.3, "medium": 0.6, "high": 0.8}
  },
  "overall_score": 0.54
}
```

### 4. 软调节建议（SoftRegulation）
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2025-02-22T10:00:10Z",
  "target": "self_iteration_vertex",
  "type": "strategy_adjustment",
  "suggestion": [
    "建议调整处理策略以匹配当前意向性级别",
    "采用标准处理策略"
  ],
  "parameters": {
    "aggressiveness": 0.54,
    "complexity_level": "medium",
    "fallback_enabled": true
  },
  "expected_outcome": "调整处理策略，匹配当前意向性需求",
  "strength": "medium",
  "confidence": 0.54,
  "reasoning": "基于分析结果：强度=medium, 紧迫性=medium, 优先级=medium",
  "valid_until": "2025-02-22T10:05:10Z",  # 时效性：5分钟后失效
  "time_to_live": 300  # 存活时间（秒）
}
```

### 5. 超然性评估结果（TranscendenceCheck）
```json
{
  "allowed": true,
  "composite_score": 0.78,
  "objective_assessment": {
    "score": 0.82,
    "level": "high",
    "components": {
      "emotional_neutrality": 0.30,
      "fact_based": 0.24,
      "logical_consistency": 0.20,
      "bias_free": 0.18
    }
  },
  "conflict_detection": {
    "conflict_detected": false,
    "conflict_level": "low",
    "conflict_score": 0.35,
    "conflicts_detected": [],
    "conflict_components": {
      "direct_intervention": 0.2,
      "behavioral_override": 0.3,
      "state_modification": 0.2
    }
  },
  "independence_assessment": {
    "score": 0.80,
    "level": "high",
    "components": {
      "decision_autonomy": 0.40,
      "data_isolation": 0.30,
      "no_external_dependency": 0.30
    }
  },
  "timestamp": "2025-02-22T10:00:15Z"
}
```

---

## 接口规范

### 命令行接口
所有模块使用 `argparse` 处理命令行参数，支持 `--help` 查看使用说明。

### 数据交换格式
- 所有模块使用 JSON 格式进行数据交换
- 输出到 stdout，便于管道调用
- 支持 `--output` 参数指定输出文件

### 错误处理
- 使用 stderr 输出错误信息
- 使用非零退出码表示错误

---

## 信息流

### 完整流程（外环内部）
```
用户/系统输入（持续流入）
    ↓
意向性收集模块
    ↓
预处理 + 初步识别
    ↓
意向性分类模块（四维分类）
    ↓
意向性分析模块（三维分析）
    ↓
意向性调节模块（生成最优解 + 软调节建议，带时效性）
    ↓
超然性保持模块（客观评估 + 冲突检测 + 独立性保障）
    ↓
软调节建议（存储，等待主循环查询）
```

### 与主循环的交互
```
┌─────────────────────────────────────────┐
│         主循环（阳性前台）               │
│  ┌───────────────────────────────────┐  │
│  │  三角形三顶点（内圈）            │  │
│  │  • 得不到（动力）                 │  │
│  │  • 数学（秩序）+ 各分支           │  │
│  │  • 自我迭代（演化）               │  │
│  └───────────────────────────────────┘  │
│              ↑ ↓                         │
│         （按需查询/接收）                  │
└─────────────────────────────────────────┘
                    ↑ ↓
┌─────────────────────────────────────────┐
│      外环（阴性后台默默运行）           │
│  • 持续收集意向性数据                   │
│  • 实时分类和分析                       │
│  • 生成软调节建议（带时效性）            │
│  • 被动响应主循环查询                   │
└─────────────────────────────────────────┘
```

### 关键约束
1. **独立性**：外环不依赖主循环触发，拥有独立生命周期
2. **超然性**：外环不直接干预主循环，仅在被查询时响应
3. **时效性**：软调节建议具有时间窗口，过期自动失效
4. **被动性**：外环不主动发送建议，等待主循环查询
5. **不打断**：外环在后台默默运行，不阻塞主循环

### 时效性机制
- 软调节建议生成时自动添加时间戳和有效期
- 主循环查询时自动过滤已过期的建议
- 高优先级意向性建议具有更长的有效期

---

## 使用示例

### 完整流程示例
```bash
# 1. 收集意向性数据
python3 scripts/intentionality_collector.py \
  --source user \
  --content "我想要学习Python编程" \
  --output collected.json

# 2. 分类
python3 scripts/intentionality_classifier.py \
  --input collected.json \
  --output classified.json

# 3. 分析
python3 scripts/intentionality_analyzer.py \
  --classification classified.json \
  --data collected.json \
  --output analyzed.json

# 4. 生成调节建议
python3 scripts/intentionality_regulator.py \
  --analysis analyzed.json \
  --output regulation.json

# 5. 超然性检查
python3 scripts/transcendence_keeper.py \
  --regulation regulation.json \
  --output final_regulation.json

# 6. 提交给自我迭代顶点（在主循环中）
# final_regulation.json 包含 allowed 字段，只有为 true 时才执行
```

### 管道组合示例
```bash
python3 scripts/intentionality_collector.py --source user --content "我需要帮助" \
  | python3 scripts/intentionality_classifier.py \
  | python3 scripts/intentionality_analyzer.py \
  | python3 scripts/intentionality_regulator.py \
  | python3 scripts/transcendence_keeper.py
```

---

## 设计原则

### 1. 超然性原则
- 保持独立性和客观性
- 不直接参与主循环操作
- 通过软调节间接影响

### 2. 模块化设计
- 每个模块独立可测试
- 清晰的接口和数据格式
- 支持单独调用和组合调用

### 3. 确定性算法
- 基于规则和特征匹配
- 可复现的分类结果
- 明确的评分机制

### 4. 可扩展性
- 支持新增分类维度
- 支持自定义规则库
- 支持集成到现有架构

### 5. 信息流约束
- 外环独立运行，不依赖主循环触发
- 被动响应主循环查询
- 保持架构一致性

### 6. 时效性约束
- 软调节建议自动过期
- 支持优先级相关的有效期调整
- 确保建议的实时性

---

## 附录

### 相关文档
- [SKILL.md](../SKILL.md) - 主技能文档
- [references/architecture.md](architecture.md) - 整体架构
- [references/maslow_needs.md](maslow_needs.md) - 马斯洛需求层次

### 哲学基础
- 胡塞尔：意向性作为意识的根本属性
- 布伦塔诺：心理现象的意向性特征
- 塞尔：派生意向性理论
- 阴阳哲学：阴与阳的互补与平衡

### 技术实现
- 纯Python实现，无外部依赖
- 使用argparse处理命令行参数
- 使用json模块进行数据交换
- 支持管道调用
- 时效性管理基于时间戳和有效期

---

**文档版本**: 1.0
**最后更新**: 2025-02-22
**作者**: kiwifruit
**协议**: AGPL-3.0
