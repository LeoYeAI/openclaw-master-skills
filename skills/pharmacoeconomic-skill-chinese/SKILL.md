---
name: 药物经济学评价
description: 该技能包提供进行药物经济学评价的综合指导与工具，涵盖成本 - 效果分析、成本 - 效用分析、成本 - 效益分析、预算影响分析、敏感性分析及模型构建。当您需要进行以下工作时，请使用此技能：对医疗保健干预措施进行经济学评价；分析治疗成本与产出结果；构建决策分析模型（如马尔可夫模型、决策树模型、离散事件模拟模型）；依据中国指南撰写药物经济学报告。本技能包适用于从事卫生技术评估（HTA）项目的研究人员、卫生经济学家及医药行业专业人士。
---

# 药物经济学评价技能

## Overview

此技能提供全面的药物经济学评价指导，包括成本-效果分析、成本-效用分析、成本-效益分析、预算影响分析、敏感性分析和模型构建。遵循中国药物经济学评价指南（2023版），为医疗卫生干预措施的经济评价提供完整的工作流程、计算工具和参考文献。

## 评价类型选择

根据研究目的和数据特点选择合适的评价类型：

- **成本-效果分析 (CEA)**：干预效果可用单一临床指标（如生命年、生存率）衡量时使用
- **成本-效用分析 (CUA)**：需要同时考虑生存质量和生存时间时使用，效果指标为QALYs
- **成本-效益分析 (CBA)**：干预效果可以用货币单位衡量时使用
- **成本-最小化分析 (CMA)**：两种干预方案效果证实时使用，仅比较成本
- **预算影响分析 (BIA)**：评估新药或新技术对医保基金的财务影响时使用

## 核心工作流程

### 步骤 1：确定研究框架

1. 定义研究问题
   - 明确目标疾病和目标人群
   - 确定评价的干预措施和对照
   - 设定研究视角（推荐：全社会视角）

2. 选择评价类型
   - 根据效果指标性质选择 CEA、CUA、CBA 或 CMA
   - 长期研究考虑贴现（成本和效果均需贴现）
   - 中国推荐贴现率：4.5%

3. 确定分析时间范围
   - 慢性疾病：通常采用终身或足够长的时间范围
   - 急性疾病：短期随访（1-3年）
   - 预算影响分析：通常为3-5年

### 步骤 2：收集和识别成本

遵循中国药物经济学评价指南识别成本：

**直接医疗成本**
- 药品费用
- 门诊费用
- 住院费用
- 检查检验费用
- 手术治疗费用
- 不良事件治疗费用

**直接非医疗成本**
- 交通费用
- 住宿费用
- 营养支持费用
- 非专业护理费用

**间接成本**
- 生产力损失（早亡或病假）
- 陪护损失

**无形成本**
- 疼痛、焦虑、生活质量下降等不纳入货币成本，在效用分析中考虑

成本数据来源：
- 医院信息系统
- 医保数据库
- 流行病学研究
- 文献综述
- 问卷调查

### 步骤 3：测量效果/效用

**效果指标选择**
- 生存指标：生命年 (LY)、生存率
- 疾病特异性指标：无事件生存时间、症状改善
- 其他：并发症发生率、住院次数

**效用测量（推荐使用间接测量法）**
- EQ-5D（欧洲五维健康量表）
- SF-6D（基于SF-36）
- QWB（健康质量指数）

效用值来源优先级：
1. 基于目标人群的原始研究数据（最佳）
2. 已发表的中国人群效用值
3. 其他国家的数据（需调整）

### 步骤 4：构建决策分析模型

根据研究特点选择合适的模型类型：

#### 决策树模型
- **适用场景**：短期、单次决策、事件顺序明确
- **优点**：直观、易于理解、适合分析决策过程
- **步骤**：
  1. 定义决策节点、机会节点、终端节点
  2. 为每个机会节点分配概率（概率和为1）
  3. 为每个终端节点分配成本和效果
  4. 折回计算期望值
  5. 比较决策选项

#### 马尔可夫模型
- **适用场景**：慢性疾病、长期随访、需要处理循环事件
- **优点**：可处理疾病状态的周期性转移、结构清晰
- **步骤**：
  1. 定义健康状态（如：健康、轻度、中度、重度、死亡）
  2. 构建转移矩阵（描述状态间转移概率）
  3. 估计转移概率（从发生率、生存曲线或文献）
  4. 为每个状态分配周期成本和效用
  5. 设定周期长度（通常为1年）和模型时限
  6. 进行马尔可夫模拟

#### 离散事件模拟 (DES)
- **适用场景**：个体差异大、事件时间不规律、需要处理资源限制
- **优点**：最灵活、可模拟个体路径、精确建模时间依赖关系
- **步骤**：
  1. 定义实体（患者）及其属性
  2. 定义可能的事件类型
  3. 建立事件调度机制
  4. 执行模拟
  5. 汇总分析结果

#### 分区生存模型 (PSM)
- **适用场景**：肿瘤学研究、基于生存曲线
- **优点**：直接基于生存数据、外推合理
- **步骤**：
  1. 获取PFS和OS生存曲线
  2. 使用参数化分布拟合曲线（指数、威布尔等）
  3. 外推到模型时限
  4. 计算各分区的人数分布
  5. 累积成本和效用

**详细建模方法参考**：`references/model_methods.md`

### 步骤 5：计算核心指标

使用 `scripts/` 中的计算工具：

#### 增量成本-效果比 (ICER)
使用 `scripts/cost_effectiveness_analysis.py` 中的 `calculate_icere()` 函数：

```python
from cost_effectiveness_analysis import calculate_icere

result = calculate_icere(
    cost_intervention,  # 干预组成本
    effect_intervention,  # 干预组效果（如QALYs）
    cost_control,  # 对照组成本
    effect_control,  # 对照组效果
    threshold=100000  # 支付阈值（中国参考：1-3倍人均GDP/QALY）
)
```

ICER计算公式：
\[ ICER = \frac{C_A - C_B}{E_A - E_B} = \frac{\Delta C}{\Delta E} \]

#### 质量调整生命年 (QALYs)
使用 `scripts/cost_effectiveness_analysis.py` 中的 `calculate_qaly()` 函数：

```python
from cost_effectiveness_analysis import calculate_qaly

qalys = calculate_qaly(
    life_years=10,  # 生命年
    utility_scores=np.array([...]),  # 各时期效用分数
    discount_rate=0.45  # 贴现率
)
```

QALY计算公式：
\[ QALY = \sum_{t=1}^{T} U_t \times \frac{1}{(1+r)^{t-1}} \]

#### 净收益 (Net Benefit)
\[ NB = \lambda \times E - C \]

其中：
- NB = 净收益
- λ = 支付阈值
- E = 效果
- C = 成本

#### 预算影响分析
使用 `scripts/budget_impact_analysis.py` 中的 `BudgetImpactModel` 类：

```python
from budget_impact_analysis import BudgetImpactModel

model = BudgetImpactModel(
    target_population=100000,  # 目标人群数量
    treatment_cost_new=15000,  # 新疗法人均成本
    treatment_cost_old=10000,  # 旧疗法人均成本
    horizon_years=5,  # 分析周期
    uptake_rate=0.2,  # 采用率
    discount_rate=0.45  # 贴现率
)

# 计算多情境预算影响
scenarios = {
    "基准情境": [0.2, 0.3, 0.4, 0.5, 0.6],
    "乐观情境": [0.3, 0.5, 0.7, 0.8, 0.9],
    "保守情境": [0.1, 0.15, 0.2, 0.25, 0.3]
}

results = model.compare_scenarios(
    scenarios,
    population_growth_rate=0.02,
    treatment_cost_inflation=0.01
)
```

### 步骤 6：进行敏感性分析

#### 单因素敏感性分析
使用 `scripts/cost_effectiveness_analysis.py` 中的 `deterministic_sensitivity_analysis()` 函数：

```python
from cost_effectiveness_analysis import deterministic_sensitivity_analysis

# 定义参数范围
param_ranges = {
    'drug_cost': (10000, 20000),
    'hospital_cost': (5000, 15000),
    'effectiveness': (0.8, 1.2)
}

# 执行敏感性分析
results_df = deterministic_sensitivity_analysis(
    base_params=base_parameters,
    param_ranges=param_ranges,
    outcome_func=outcome_function
)
```

**龙卷风图数据准备**：使用 `tornado_plot_data()` 函数

#### 概率敏感性分析 (PSA)
使用 `scripts/monte_carlo_simulation.py` 中的 `MonteCarloSimulator` 类：

```python
from monte_carlo_simulation import MonteCarloSimulator

# 创建模拟器
simulator = MonteCarloSimulator(n_simulations=10000, seed=42)

# 定义参数分布
parameters = {
    'cost': {
        'distribution': 'gamma',
        'params': (2, 15000),  # shape, scale
        'min_value': 0
    },
    'effect': {
        'distribution': 'beta',
        'params': (5, 3),  # alpha, beta
        'min_value': 0,
        'max_value': 10
    }
}

# 执行PSA
results_df = simulator.probabilistic_sensitivity_analysis(
    parameters=parameters,
    outcome_func=outcome_function,
    threshold=120000
)
```

**生成成本-效果可接受曲线 (CEAC)**：使用 `generate_ceac()` 函数

**价值信息分析 (VOI)**：使用 `value_of_information_analysis()` 函数

### 步骤 7：结果解释与报告

#### 支付阈值（中国参考）
- 1倍人均GDP/QALY：约 100,000元
- 2倍人均GDP/QALY：约 200,000元
- 3倍人均GDP/QALY：约 300,000元

#### 结果解释
- **ICER ≤ 支付阈值**：具有成本效果
- **ICER > 支付阈值**：不具有成本效果
- **严格优势**：成本更低且效果更好
- **严格劣势**：成本更高且效果更差

#### 报告要求
遵循 CHEERS 2022 声明和中国药物经济学评价指南：
1. 清晰描述研究设计和方法
2. 报告基线分析结果
3. 提供敏感性分析结果（单因素和概率敏感性）
4. 报告结果的置信区间
5. 讨论研究局限性和推广性
6. 明确声明资助来源和潜在利益冲突

**详细指南参考**：`references/china_guidelines.md`

## Scripts 使用指南

### cost_effectiveness_analysis.py
核心功能：成本-效果分析、ICER计算、QALY计算、确定性敏感性分析

主要函数：
- `calculate_icere()`：计算ICER
- `calculate_qaly()`：计算QALYs
- `calculate_ceac()`：计算成本-效果可接受曲线
- `deterministic_sensitivity_analysis()`：单因素敏感性分析
- `tornado_plot_data()`：准备龙卷风图数据
- `markov_model_transition()`：马尔可夫模型模拟
- `discount_costs()`：成本贴现

### budget_impact_analysis.py
核心功能：预算影响分析模型

主要类和方法：
- `BudgetImpactModel`：预算影响分析模型
  - `calculate_budget_impact_scenario()`：计算单情境预算影响
  - `compare_scenarios()`：比较多个情境
  - `sensitivity_analysis()`：敏感性分析
  - `generate_summary()`：生成分析摘要
- `calculate_incremental_budget_impact()`：计算增量预算影响
- `budget_impact_report()`：生成预算影响报告

### monte_carlo_simulation.py
核心功能：蒙特卡洛模拟、概率敏感性分析、价值信息分析

主要类和方法：
- `MonteCarloSimulator`：蒙特卡洛模拟器
  - `generate_samples()`：从指定分布生成样本
  - `probabilistic_sensitivity_analysis()`：执行PSA
  - `generate_ceac()`：生成CEAC
  - `value_of_information_analysis()`：VOI分析
  - `scatter_plot_data()`：准备成本-效果散点图数据

## References 使用指南

### china_guidelines.md
中国药物经济学评价指南（2025版）关键内容摘要，包含：
- 评价框架和视角
- 成本识别与测量
- 效果/效用测量
- 模型构建方法
- 贴现原则
- 敏感性分析要求
- 结果表达和报告标准
- 常用计算公式

**使用场景**：查询中国药物经济学评价的具体要求、标准和方法

### model_methods.md
详细的决策分析模型构建方法，包含：
- 马尔可夫模型（基础概念、转移矩阵、概率估计）
- 决策树模型（结构、概率分配、折回计算）
- 离散事件模拟（核心要素、优缺点）
- 分区生存模型（生存曲线拟合）
- 模型比较和选择
- 建模最佳实践

**使用场景**：学习具体的建模方法、构建决策分析模型

## 常见任务场景

### 场景 1：开展新药的成本-效果分析
1. 确定研究视角（全社会视角）
2. 识别直接医疗成本和直接非医疗成本
3. 收集临床试验数据获取效果指标（生存、QALYs）
4. 构建马尔可夫模型模拟疾病进展
5. 计算ICER并与支付阈值比较
6. 进行单因素和概率敏感性分析
7. 按照CHEERS标准撰写报告

### 场景 2：预算影响分析
1. 确定目标人群规模
2. 获取新药和对照治疗方案的成本
3. 设定采用率情景（基准、乐观、保守）
4. 使用 `BudgetImpactModel` 计算各情景的预算影响
5. 进行敏感性分析
6. 生成预算影响报告

### 场景 3：模型构建与验证
1. 根据疾病特点选择模型类型
2. 使用 `references/model_methods.md` 学习建模方法
3. 从文献或临床试验估计模型参数
4. 进行模型验证（内部验证和外部验证）
5. 使用模型进行基线分析
6. 进行敏感性分析验证模型稳定性

### 场景 4：概率敏感性分析
1. 为每个关键参数指定概率分布
2. 使用 `MonteCarloSimulator` 进行10,000次以上模拟
3. 生成成本-效果散点图
4. 生成成本-效果可接受曲线（CEAC）
5. 进行价值信息分析（VOI）
6. 报告成本效果概率和置信区间

## 参数管理最佳实践

### 参数整齐排列原则
在进行药物经济学评价时，所有参数应整齐排列并标明来源。以下是最佳实践：

#### 1. 参数分类组织
将参数按照以下分类整齐排列：
- **研究框架参数**：研究视角、时间范围、贴现率、支付阈值等
- **模型结构参数**：健康状态、初始分布等
- **转移概率参数**：各状态间的转移概率
- **成本参数**：各状态的年度成本明细
- **效用值参数**：各状态的效用值
- **敏感性分析参数**：参数范围和概率分布
- **模拟参数**：模拟次数、随机种子等

#### 2. 参数来源标注
每个参数值都必须标注明确的数据来源：
- **文献引用**：注明文献作者、期刊、年份、页码
- **数据库**：注明数据库名称、版本、访问时间
- **指南/标准**：注明指南名称、版本号、发布机构
- **专家意见**：注明专家来源和判断依据
- **研究假设**：说明假设的理由和依据

#### 3. 参数格式规范
```python
# ========== 参数分类标题 ==========
PARAMETER_NAME = {
    'parameter_key': value,  # 来源: 详细说明数据来源
    'another_key': value,    # 来源: 参考文献 [作者, 期刊, 年份]
}
```

#### 4. 示例代码
参见 `scripts/example.py` 文件，其中展示了如何整齐排列所有参数并标明来源。该文件包含：
- 完整的参数分类组织
- 详细的数据来源标注
- 参考文献列表
- 参数使用示例

#### 5. 参数来源模板
- 临床试验：`来源: LIFE研究结果,缬沙坦组无事件率,Dahlöf B et al. Lancet. 2002;359:995-1003`
- 流行病学研究：`来源: 中国人口统计年鉴(2024),40-49岁年龄别死亡率`
- 医疗费用：`来源: 缬沙坦80mg片剂,5元/天×365天,中国医疗保障局药品目录价格(2024)`
- 指南推荐：`来源: 中国药物经济学评价指南(2025版),推荐4.5%贴现率`
- 研究假设：`来源: 假设新确诊患者,100%初始无并发症`

## 重要注意事项

1. **遵循中国指南**：确保研究方法符合中国药物经济学评价指南（2025版）的要求

2. **透明度**：清晰描述所有假设、数据来源和计算方法

3. **参数来源标注**：所有参数值必须注明来源，便于追溯和验证

4. **贴现**：成本和效果均需贴现，中国推荐贴现率4.5%

5. **敏感性分析**：必须进行充分的敏感性分析以评估不确定性

6. **模型验证**：对模型进行内部验证，如可能进行外部验证

7. **报告标准**：遵循 CHEERS 2022 报告标准

8. **支付阈值**：明确说明使用的支付阈值及其依据（中国参考：1-3倍人均GDP/QALY）

9. **时间范围**：选择足够长的时间范围以捕捉所有相关成本和效果

10. **成本测量**：避免使用支付价格（报销后价格），使用实际费用或标准化收费

11. **效用测量**：优先使用中国人群的效用值，使用时注意测量工具的适用性

12. **参数整齐排列**：参考 `scripts/example.py` 中的格式，整齐排列所有参数并详细标注来源

---

**资源说明**：
- `scripts/`：包含 Python 计算脚本，可直接执行以进行药物经济学计算
- `references/`：包含详细的方法指南和参考文献，在需要时加载到上下文
- `assets/`：暂未包含模板文件，可根据需要添加