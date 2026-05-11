# Command: /workshop (产品研讨会)

## 功能

启动产品研讨会，五角色（产品经理、战略顾问、架构师、开发助手、运营经理）对齐 Why、Scope、Timeline。

## 触发时机

- 外部客户访谈完成后
- Why 冻结前
- 战略顾问已准备好所有输入材料

## 前置条件

1. 结构化访谈已完成（王校长）
2. 外部客户访谈已完成（战略顾问）
3. 战略分析材料已准备：
   - insights.md（外部洞察汇总）
   - benchmark-report.md（行业Benchmark）
   - business-model-canvas.md（商业模式画布）
   - financial-summary.md（财务预测摘要）
   - strategic-recommendations.md（战略建议）

## 研讨会议程

```
Phase 1: Why 陈述 + 外部洞察（15分钟）
├── 王校长陈述 Why
├── 战略顾问呈现外部洞察
└── 五角色提问澄清

Phase 2: 需求澄清（15分钟）
├── 开发提问技术细节
├── 运营提问业务流程
├── 架构提问技术约束
└── 战略提问商业逻辑

Phase 3: 方案讨论（20分钟）
├── 架构师：技术方案
├── 开发助手：实现难度
├── 运营经理：运营策略
├── 战略顾问：商业建议
└── 王校长：优先级排序

Phase 4: 决策对齐（10分钟）
├── 确认 Why
├── 确认 Scope（MVP范围）
├── 确认 Timeline
└── 确认 Next Step
```

## 输出

- `00-work/interview/workshop/YYYY-MM-DD-workshop-summary.md`
- `00-work/interview/workshop/YYYY-MM-DD-scope-agreement.md`
- `00-work/interview/workshop/YYYY-MM-DD-action-items.md`
- `00-work/interview/workshop/decisions.md`（累计决策）

## 后续流程

研讨会结束 → 五角色确认 → `/freeze` → Why 冻结 → 开发自治启动

## 指令别名

- `/研讨`
- `/workshop`
