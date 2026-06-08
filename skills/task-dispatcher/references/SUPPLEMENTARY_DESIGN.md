# Task Dispatcher - 补充设计文档

## 概述

本文档是 task-dispatcher SKILL.md 的补充设计，针对 Critic 和 Reviewer 提出的问题提供详细的设计方案。

---

## 问题 1：澄清确认环节与现有「阶段3」关系

### 当前状态

现有 SKILL.md 已包含：
- **阶段 3：确认后再执行** - 任务列表展示给用户等待确认
- **6 项检查清单** - 任务目标、约束条件、复杂度、疑问点、资源需求、风险点

### 设计决策

**澄清确认环节是「阶段3」的增强，而非新增独立环节**

```
阶段 3：确认后再执行
├── 3.1 展示任务列表 (原有)
├── 3.2 6项检查清单 (原有)
├── 3.3 风险分类确认 (原有)
└── 3.4 ⚡ 澄清确认 (新增增强)
```

### 3.4 澄清确认的实现方式

**触发条件**：当识别到以下情况时，必须进入澄清确认：

| 情况 | 示例 | 处理方式 |
|------|------|----------|
| 信息不足 | 目标模糊、范围不清 | 暂停，询问用户 |
| 存在歧义 | 可多种理解 | 列出选项，确认 |
| 约束冲突 | 时间紧 + 质量高 | 告知权衡，确认优先级 |
| 依赖风险 | 外部依赖不可控 | 说明风险，确认是否继续 |

**实现流程**：

```
[任务分析]
    ↓
[检测疑问点] → 有疑问 → [生成澄清问题] → [等待用户确认] → [继续/调整]
    ↓ 无疑问
[6项检查清单]
    ↓
[风险分类] → HIGH/CRITICAL → [增强确认] → [等待用户授权]
    ↓
[执行分发]
```

**澄清确认的输出格式**：

```
## ⚡ 澄清确认

### 需要确认的问题

1. **目标明确性**: [具体问题]
   - 选项 A: [...]
   - 选项 B: [...]

2. **优先级权衡**: [冲突描述]
   - 优先质量 → 时间延长
   - 优先时间 → 质量折中

请回复您的选择，或补充更多信息 ✓
```

---

## 问题 2：YAML 配置边界定义

### 设计原则

| 存放位置 | 内容 | 理由 |
|----------|------|------|
| **SKILL.md** | 核心逻辑、角色定义、流程编排、原则性规则 | 稳定，需要 LLM 理解执行 |
| **YAML** | 管道配置、agent 映射、阈值参数、业务规则 | 灵活，需要经常调整 |

### YAML 配置文件结构

```yaml
# task-dispatcher-config.yaml

# ===========================================
# 1. 管道配置 (Pipeline Config)
# ===========================================
pipelines:
  # 默认任务管道
  default:
    stages:
      - name: analyze
        agent: self  # task-dispatcher 自己执行
      - name: review
        agents: [critic, reviewer]
        mode: parallel  # or sequential
      - name: execute
        agent: ~dynamic  # 根据任务类型动态选择
      - name: verify
        agent: tester
    
    # 阶段间的确认规则
    confirm_after:
      - analyze  # 分析完成后确认
      - review   # 审核完成后确认 (针对 HIGH/CRITICAL 风险)
    
    # 失败传播规则
    fail_strategy:
      stop_on_critical: true
      retry_before_stop: 2

  # 快速任务管道 (跳过审核)
  fast:
    stages:
      - name: execute
        agents: [coder]
    confirm_after: []

  # 复杂任务管道 (多轮审核)
  complex:
    stages:
      - name: analyze
      - name: design_review
        agents: [architect, critic]
        mode: sequential
      - name: implement
      - name: test_review
        agents: [reviewer, tester]
        mode: parallel
      - name: deploy_review
        agents: [devops, critic]
        mode: sequential

# ===========================================
# 2. Agent 映射 (Agent Mapping)
# ===========================================
agent_mappings:
  # 任务类型 → Agent 映射
  task_types:
    code: coder
    research: researcher
    document: docs_writer
    test: tester
    review: reviewer
    architecture: architect
    deployment: devops
  
  # 技能标签 → Agent 映射
  skill_tags:
    security: [critic, security_specialist]
    performance: [reviewer, performance_expert]
    docs: [docs_writer]

# ===========================================
# 3. 阈值参数 (Thresholds)
# ===========================================
thresholds:
  # 复杂度判断
  complexity:
    simple_max_steps: 1
    normal_max_steps: 3
    complex_min_steps: 4
  
  # 风险判断
  risk:
    low_cost_threshold: 10      # $10
    medium_cost_threshold: 50  # $50
    high_cost_threshold: 100    # $100
  
  # 防死循环
  deadlock_prevention:
    max_token_per_task: 100000
    max_time_minutes: 30
    max_retries: 2
    progress_check_interval: 5  # 每5分钟检查一次进度
  
  # 审核汇总
  review:
    parallel_timeout: 10  # minutes
    sequential_timeout: 30  # minutes

# ===========================================
# 4. 业务规则 (Business Rules)
# ===========================================
business_rules:
  # 审核模式选择
  review_modes:
    # 并行审核适用场景
    parallel:
      - code + docs + test  # 独立产出
      - multiple_features   # 多功能并行
      - research + analysis # 调研+分析
    
    # 串联审核适用场景
    sequential:
      - architecture + implementation  # 架构影响实现
      - security + any                  # 安全优先
      - design + code                   # 设计决定代码
  
  # 确认要求
  confirm_requirements:
    auto_execute: [LOW]
    brief_confirm: [MEDIUM]
    detailed_confirm: [HIGH]
    explicit_authorization: [CRITICAL]
  
  # 审核汇总规则
  summary_rules:
    default_mode: majority  # majority | unanimous | veto
    veto_allowed_roles: [critic]  # 可一票否决的角色

# ===========================================
# 5. 模板 (Templates)
# ===========================================
templates:
  task_list: |
    ## 📋 任务分发计划
    
    **原始任务**: {task_description}
    **复杂度**: {complexity}
    **风险等级**: {risk_level}
    
    ### 任务列表
    | # | 任务 | Agent | 依赖 | 状态 |
    |---|------|-------|------|------|
    {task_rows}
    
    ### 确认
    {confirm_prompt}
  
  review_summary: |
    ## 🔍 审核汇总
    
    ### 审核结果
    {review_results}
    
    ### 汇总决定
    - **汇总方式**: {summary_mode}
    - **最终决定**: {final_decision}
    
    {next_action}
```

### 配置加载时机

| 时机 | 优点 | 缺点 |
|------|------|------|
| **任务分发时** (推荐) | 灵活应对任务变化，支持动态配置 | 每次加载有轻微延迟 |
| 启动时 | 预加载，无运行时延迟 | 修改需重启，不灵活 |

**推荐：任务分发时加载**

```python
# 伪代码
def dispatch_task(task):
    # 加载配置
    config = load_config("task-dispatcher-config.yaml")
    
    # 根据任务选择管道
    pipeline = select_pipeline(task, config.pipelines)
    
    # 根据任务类型选择 agent
    agent = select_agent(task, config.agent_mappings)
    
    # 执行
    execute_pipeline(pipeline, agent, config.thresholds)
```

---

## 问题 3：防死循环度量标准

### 三大度量维度

#### 3.1 成本度量 (Token 消耗)

```yaml
thresholds:
  deadlock_prevention:
    # 单任务最大 token 消耗
    max_token_per_task: 100000
    
    # 任务类型系数 (不同类型任务消耗不同)
    token_multipliers:
      code: 1.0
      research: 1.5  # 搜索+分析更耗 token
      review: 0.8
      test: 1.2
```

**计算公式**：

```
实际阈值 = 基础阈值 × 任务类型系数 × 复杂度系数
```

| 复杂度 | 系数 |
|--------|------|
| 简单 | 0.5 |
| 一般 | 1.0 |
| 复杂 | 1.5 |

#### 3.2 时间度量 (超时控制)

```yaml
thresholds:
  deadlock_prevention:
    # 基础超时时间 (分钟)
    base_timeout: 30
    
    # 任务类型时间系数
    time_multipliers:
      simple: 0.5    # 15 min
      normal: 1.0    # 30 min
      complex: 2.0   # 60 min
    
    # 动态调整策略
    dynamic_adjustment:
      enabled: true
      # 每次重试后增加 50% 时间
      retry_multiplier: 1.5
      # 最大超时上限
      max_timeout: 120  # 2 小时
```

**超时处理流程**：

```
[超时检测]
    ↓
[检查进度] → 有进展 → [延长 timeout，继续]
    ↓ 无进展
[重试] → 剩余重试次数 > 0 → [重新分发]
    ↓
[标记失败] → [进入兜底处理]
```

#### 3.3 进度度量 (无进展检测)

```yaml
thresholds:
  deadlock_prevention:
    # 进度检查间隔 (分钟)
    progress_check_interval: 5
    
    # 无进展定义
    no_progress_definition:
      # 连续 N 次检查无状态变化
      consecutive_checks: 3  # 15 分钟无变化
      
      # 或：产出物未更新
      output_stale_minutes: 20
    
    # 进度追踪方式
    tracking:
      - agent_status_changes  # 状态变化
      - output_file_updates   # 文件更新
      - message_count         # 消息数量
```

**进展判定规则**：

| 指标 | 有进展 | 无进展 |
|------|--------|--------|
| 状态 | pending → running → completed | 连续 3 次 running |
| 输出 | 文件新增/修改 | 无变化 |
| 消息 | 有新消息 | 无消息 |

### 完整防死循环流程

```
[任务分发]
    ↓
[启动计时器]
    ↓
每 [progress_check_interval] 分钟:
    ├── [检查 token 消耗] → 超过 80% 阈值 → [警告用户]
    ├── [检查时间] → 超过 timeout → [进入无进展检测]
    └── [检查进度] → 无进展 → [进入重试流程]
    
[重试流程]
    ├── 增加 timeout (×1.5)
    ├── 减少 token 阈值 (×0.8)
    └── 重试次数 -1
    
[最终失败]
    ├── 记录详细日志
    ├── 通知用户
    └── 进入兜底处理
```

---

## 问题 4：并行/串联审核适用场景

### 场景分类矩阵

| 场景类型 | 适用模式 | 示例 | 理由 |
|----------|----------|------|------|
| **独立产出** | 并行 | 代码 + 文档 + 测试 | 各产出独立，无依赖 |
| **多功能开发** | 并行 | 多个独立 feature | 并行加速 |
| **调研+分析** | 并行 | 研究 + 总结 | 可流水线 |
| **依赖性强** | 串联 | 架构 + 实现 | 设计决定实现 |
| **安全相关** | 串联 | 安全审查 + 任何 | 安全优先 |
| **高风险** | 串联 | 关键决策 + 执行 | 谨慎行事 |

### YAML 配置示例

```yaml
business_rules:
  review_modes:
    # 并行审核配置
    parallel:
      conditions:
        - tasks_are_independent: true
        - no_shared_resources: true
        - different_agents: true
      
      examples:
        - "代码 + 文档 + 测试"
        - "前端 + 后端 (独立模块)"
        - "调研 + 分析"
      
      # 并行超时
      timeout: 10  # minutes
      
      # 并行数量限制
      max_parallel: 3

    # 串联审核配置
    sequential:
      conditions:
        - later_task_depends_on_earlier: true
        - security_or_safety_critical: true
        - high_risk_decision: true
      
      examples:
        - "架构设计 → 代码实现"
        - "安全审查 → 任何任务"
        - "设计评审 → 开发"
      
      # 串联超时 (每个阶段)
      timeout_per_stage: 30  # minutes
```

### 自动选择逻辑

```
[审核模式选择]

    ↓
[分析任务依赖关系]
    ├── 有依赖 → 串联
    └── 无依赖 → 并行
    
    ↓
[检查风险等级]
    ├── HIGH/CRITICAL → 串联 (即使独立)
    └── LOW/MEDIUM → 继续
    
    ↓
[检查资源冲突]
    ├── 共享资源 → 串联
    └── 独立资源 → 并行
    
    ↓
[最终决定]
```

---

## 问题 5：审核通过后的确认边界

### 风险等级确认矩阵

| 风险等级 | 审核通过后 | 示例 |
|----------|------------|------|
| 🟢 LOW | **自动执行** | 查天气、简单查询 |
| 🟡 MEDIUM | **简要确认** | 写一般代码、发送普通邮件 |
| 🔴 HIGH | **详细确认** | 修改配置、发布到测试环境 |
| ⚫ CRITICAL | **明确授权** | 删除数据、发布到生产、权限变更 |

### 确认边界规则

```yaml
business_rules:
  confirm_after_review:
    # 审核通过后的自动执行规则
    auto_execute_when:
      risk_level: LOW
      and:
        - review_passed: true
        - no_blocking_issues: true
    
    # 需要简要确认
    brief_confirm_when:
      risk_level: MEDIUM
      or:
        - cost_exceeds_threshold: true
        - changes_production: false  # 非生产
    
    # 需要详细确认
    detailed_confirm_when:
      risk_level: HIGH
      or:
        - changes_config: true
        - affects_other_systems: true
        - requires_downtime: true
    
    # 需要明确授权
    explicit_auth_when:
      risk_level: CRITICAL
      or:
        - deletes_data: true
        - publishes_to_production: true
        - changes_permissions: true
        - irreversible: true
```

### 用户确认时的信息展示

```
## ⚠️ 执行确认

### 任务信息
- **任务**: [描述]
- **执行Agent**: [agent-name]
- **风险等级**: [🟢/🟡/🔴/⚫]

### 审核结果
- **审核状态**: ✅ 通过 / ⚠️ 有条件通过 / ❌ 需关注
- **审核意见**: [简要摘要]

### 确认内容
{根据风险等级显示不同内容}

请回复 [确认执行] 或提出修改意见
```

---

## 问题 6：智能汇总规则和冲突解决策略

### 6.1 智能汇总规则

```yaml
business_rules:
  summary_rules:
    # 默认汇总模式
    default_mode: majority
    
    # 汇总模式定义
    modes:
      # 多数同意 (默认)
      majority:
:         description超过半数审核者同意即可通过
        threshold: > 50%
        applicable_to: [LOW, MEDIUM]
      
      # 全票通过
      unanimous:
        description: 所有审核者都同意才能通过
        threshold: = 100%
        applicable_to: [HIGH, CRITICAL]
      
      # 一票否决
      veto:
        description: 任何审核者反对即不通过
        threshold: any reject
        applicable_to: [CRITICAL, security]
        veto_roles: [critic, security_specialist]
      
      # 一票通过 (快速通道)
      fast_track:
        description: 任何一个审核者通过即可
        threshold: >= 1 approve
        applicable_to: [LOW]
        conditions:
          - no_critic_involved: true
    
    # 特殊情况处理
    tie_breaking:
      # 平票时的处理
      on_tie:
        # 默认: 咨询更高层级
        action: escalate
        # 或: 默认拒绝
        # action: reject
```

### 汇总规则速查表

| 模式 | 条件 | 适用场景 | 示例 |
|------|------|----------|------|
| **多数同意** | >50% 同意 | 低风险任务 | 简单代码审查 |
| **全票通过** | 100% 同意 | 高风险任务 | 生产部署 |
| **一票否决** | 任何反对 | 安全相关 | 权限变更 |
| **一票通过** | 任何同意 | 快速任务 | 文档润色 |

### 6.2 冲突解决策略

```yaml
business_rules:
  conflict_resolution:
    # 冲突类型定义
    conflict_types:
      # 审核者之间的冲突
      reviewer_conflict:
        - critic vs reviewer
        - reviewer vs reviewer
        - critic vs critic
      
      # 审核结果与用户期望的冲突
      expectation_conflict:
        - user_wants_approve vs reviewer_rejects
        - user_wants_fast vs critic_wants_thorough
    
    # 解决策略
    strategies:
      # 1. 角色优先级 (当 critic 参与时)
      role_priority:
        enabled: true
        hierarchy:
          - critic        # 最高优先级
          - security      # 安全优先
          - architect    # 架构决策
          - reviewer     # 代码审查
          - tester       # 测试验证
          - docs_writer  # 文档
          - researcher   # 调研
      
      # 2. 第三方仲裁
      arbitration:
        enabled: true
        arbitrator: architect  # 架构师仲裁
        fallback: user         # 无法仲裁时用户决定
      
      # 3. 复审机制
      re_review:
        enabled: true
        trigger:
          - conflict_detected: true
          - confidence_below: 0.7
        reviewers: [original_reviewers + 1_new]
      
      # 4. 条件通过
      conditional_pass:
        enabled: true
        conditions:
          - address_critic_concerns: true
          - document_risks: true
          - get_user_acknowledgment: true

    # 冲突升级路径
    escalation:
      level_1: # 同角色协商
        description: 同一角色的多个审核者自行讨论
        timeout: 5min
        
      level_2: # 角色协调
        description: 由高优先级角色协调
        timeout: 10min
        
      level_3: # 仲裁者决定
        description: 仲裁者做最终决定
        timeout: 15min
        
      level_4: # 用户决定
        description: 无法达成一致，用户决定
        timeout: user_response
```

### 冲突解决流程图

```
[检测到冲突]
    ↓
[判断冲突类型]
    ├── reviewer_conflict → [进入角色协调]
    └── expectation_conflict → [进入期望管理]
    
[角色协调]
    ├── 检查角色优先级
    ├── 高优先级决定
    └── 如需仲裁 → [仲裁流程]

[期望管理]
    ├── 展示冲突点
    ├── 提供选项
    └── 用户决定

[记录冲突]
    - 冲突内容
    - 解决方式
    - 最终决定
```

---

## 完整架构图 (更新版)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Task Dispatcher                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│  │  Stage 1    │     │  Stage 2    │     │  Stage 3    │              │
│  │  需求分析    │ ──→ │  任务拆解    │ ──→ │  确认执行    │              │
│  └─────────────┘     └─────────────┘     └─────────────┘              │
│        │                   │                   │                        │
│        ↓                   ↓                   ↓                        │
│  • 提取目标           • 生成任务列表        • 6项检查清单              │
│  • 约束条件           • 确定并行度          • 风险分类                 │
│  • 复杂度判断         • Agent分配           • ⚡澄清确认(增强)         │
│  • 疑问识别                                                    ↓         │
│                                                          ┌───────────┐ │
│                                                          │ 确认边界   │ │
│                                                          │ LOW→自动   │ │
│                                                          │ MEDIUM→简  │ │
│                                                          │ HIGH→详    │ │
│                                                          │ CRIT→授权  │ │
│                                                          └───────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         Pipeline Engine                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    YAML 配置加载 (task-dispatcher-config.yaml)   │   │
│  ├─────────────────┬─────────────────┬─────────────────────────────┤   │
│  │  Pipeline Config │ Agent Mappings  │  Thresholds & Rules          │   │
│  │  - default       │  - task_types   │  - complexity               │   │
│  │  - fast          │  - skill_tags   │  - risk                     │   │
│  │  - complex       │                 │  - deadlock_prevention      │   │
│  │                  │                 │  - review_modes             │   │
│  └────────┬────────┴────────┬────────┴──────────────┬──────────────┘   │
│           │                  │                        │                  │
│           ↓                  ↓                        ↓                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      审核模式选择                                │   │
│  │  ┌─────────────┐              ┌─────────────┐                  │   │
│  │  │   并行审核   │              │   串联审核   │                  │   │
│  │  │ (独立产出)  │              │ (依赖/安全)  │                  │   │
│  │  └─────────────┘              └─────────────┘                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ↓                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     审核汇总 & 冲突解决                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │   │
│  │  │ 多数同意模式  │  │ 全票通过模式  │  │ 一票否决模式  │        │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘        │   │
│  │                                                                  │   │
│  │  冲突解决: 角色优先级 → 仲裁 → 复审 → 条件通过 → 用户决定       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         防死循环机制                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│  │   成本度量   │     │   时间度量   │     │   进度度量   │              │
│  │  Token 消耗  │     │  超时控制   │     │  无进展检测  │              │
│  │  - 基础阈值  │     │  - 基础超时  │     │  - 状态变化  │              │
│  │  - 类型系数  │     │  - 动态调整  │     │  - 文件更新  │              │
│  │  - 复杂度    │     │  - 重试乘数  │     │  - 消息数量  │              │
│  └─────────────┘     └─────────────┘     └─────────────┘              │
│        │                   │                   │                        │
│        └───────────────────┴───────────────────┘                        │
│                            │                                            │
│                            ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                      处理流程                                   │    │
│  │  警告 → 延长/重试 → 兜底处理 → 记录日志 → 通知用户              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 总结

本文档提供了以下补充设计：

| # | 问题 | 解决方案 |
|---|------|----------|
| 1 | 澄清确认环节定位 | 作为「阶段3」的增强 (3.4)，触发条件明确 |
| 2 | YAML 配置边界 | SKILL.md = 核心逻辑；YAML = 配置/参数/规则 |
| 3 | 防死循环度量 | 成本/时间/进度三维度，阈值可配置 |
| 4 | 并行/串联审核 | 场景分类矩阵，自动选择逻辑 |
| 5 | 审核后确认边界 | 风险等级确认矩阵，4级确认要求 |
| 6 | 汇总规则 & 冲突解决 | 4种汇总模式 + 4级冲突升级 |
