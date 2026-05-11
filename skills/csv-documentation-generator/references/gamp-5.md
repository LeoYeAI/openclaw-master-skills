# GAMP 5 快速参考指南 / GAMP 5 Quick Reference Guide

## 什么是 GAMP? / What is GAMP?

GAMP (Good Automated Manufacturing Practice) 是一套用于计算机化系统验证的指南，由 ISPE (International Society for Pharmaceutical Engineering) 开发和维护。

GAMP is a set of guidelines for computerized system validation, developed and maintained by ISPE.

## GAMP 5 核心原则 / GAMP 5 Core Principles

1. **基于风险 / Risk-Based**: 验证工作应与风险级别相适应
2. **生命周期方法 / Lifecycle Approach**: 贯穿整个系统生命周期
3. **充分性 / Scalable**: 验证活动应根据系统复杂性调整
4. **知识管理 / Knowledge-Based**: 基于供应商和用户双方的知识

## 系统分类 / System Categories

| 分类 | 描述 | 验证要求 |
|------|------|----------|
| Category 1 | 基础设施软件 (操作系统, 数据库等) | 简化验证 |
| Category 2 | 固件 | 简化验证 |
| Category 3 | 商用现货软件 (非配置型) | 基于风险的验证 |
| Category 4 | 配置型 COTS 软件 | 基于风险的验证 |
| Category 5 | 定制/关键应用软件 | 完整生命周期验证 |

## 验证生命周期 / Validation Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                    验证生命周期                          │
│                  Validation Lifecycle                    │
└─────────────────────────────────────────────────────────┘

    ┌──────────┐
    │   计划    │
    │ Planning │
    └────┬─────┘
         │
    ┌────▼─────┐
    │ 规格定义  │──────┐
    │ Spec     │      │
    └────┬─────┘      │
         │        ┌───▼───┐
    ┌────▼─────┐ │ URS   │
    │   设计   │ │ FS    │
    │ Design  │ │ TS    │
    └────┬─────┘ └───┬───┘
         │        ┌──▼────┐
    ┌────▼─────┐ │ Risk  │
    │   构建   │ │Assess │
    │ Build   │ └───┬────┘
    └────┬─────┘      │
         │        ┌───▼────┐
    ┌────▼─────┐ │ IQ     │
    │   测试   │ │ OQ     │
    │ Testing │ │ PQ     │
    └────┬─────┘ └───┬────┘
         │        ┌──▼────┐
    ┌────▼─────┐ │ VSR   │
    │   发布   │ │       │
    │ Release │ └───┬────┘
    └────┬─────┘      │
         │        ┌───▼────┐
    ┌────▼─────┐ │ 操作    │
    │ 持续验证 │ │ Ops    │
    │ Ongoing │ │       │
    └─────────┘ └────────┘
```

## 关键文件 / Key Documents

| 文件 | 缩写 | 目的 |
|------|------|------|
| 验证计划 | VP | 定义验证范围、方法、时间表 |
| 用户需求规格 | URS | 定义用户需求 |
| 功能规格 | FS | 定义系统功能 |
| 技术规格 | TS | 定义技术实现 |
| 风险评估 | RA | 识别和评估风险 |
| 安装确认 | IQ | 验证正确安装 |
| 操作确认 | OQ | 验证正确操作 |
| 性能确认 | PQ | 验证性能要求 |
| 追溯矩阵 | RTM | 链接需求到测试 |
| 验证总结报告 | VSR | 总结验证结果 |

## 验证方法 / Validation Approach

### Category 1-2: 简化方法

- 供应商评估
- 安装确认
- 基本操作确认

### Category 3: 风险基础方法

- 风险评估
- 配置验证
- 部分功能测试

### Category 4: 风险基础方法

- 完整风险评估
- 配置测试
- 功能测试

### Category 5: 完整生命周期

- 详细规格
- 设计审核
- 完整测试

## 常见活动 / Common Activities

### 计划阶段

- [ ] 制定验证计划
- [ ] 定义角色和职责
- [ ] 制定时间表
- [ ] 定义交付物

### 规格阶段

- [ ] 编写 URS
- [ ] 编写 FS/TS
- [ ] 风险评估

### 实施阶段

- [ ] 开发/配置系统
- [ ] 编写测试用例

### 确认阶段

- [ ] IQ 测试
- [ ] OQ 测试
- [ ] PQ 测试

### 报告阶段

- [ ] 编写验证报告
- [ ] 审核和批准

## 质量要求 / Quality Requirements

- 所有文档需要审核和批准
- 变更需要受控
- 审计追踪需要启用
- 培训需要完成记录
