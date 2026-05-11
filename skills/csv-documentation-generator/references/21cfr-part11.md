# 21 CFR Part 11 快速参考 / 21 CFR Part 11 Quick Reference

## 什么是 Part 11? / What is Part 11?

21 CFR Part 11 是美国 FDA (Food and Drug Administration) 发布的联邦法规，规定了电子记录和电子签名的使用要求。

21 CFR Part 11 is an FDA regulation that defines the requirements for electronic records and electronic signatures.

## 适用范围 / Scope

Part 11 适用于:

- 需要根据 FDA 法规保存的记录
- 以电子形式创建、修改、维护、存档、检索或传输的记录
- 电子签名

Part 11 applies to:

- Records required to be maintained under FDA regulations
- Records created, modified, maintained, archived, retrieved, or transmitted electronically
- Electronic signatures

## 核心要求 / Core Requirements

### 1. 审计追踪 / Audit Trail

| 要求 | 描述 |
|------|------|
| 记录创建 | 记录所有创建电子记录的操作 |
| 记录修改 | 记录所有修改电子记录的操作 |
| 记录删除 | 记录删除操作 |
| 时间戳 | 记录操作的日期和时间 |
| 不可修改 | 审计追踪本身不可被修改或删除 |

### 2. 电子签名 / Electronic Signatures

| 要求 | 描述 |
|------|------|
| 唯一性 | 电子签名必须唯一对应到个人 |
| 不可重用 | 电子签名不能被复用或共享 |
| 签名含义 | 签名必须包含签名含义 |
| 日期时间 | 签名必须包含日期和时间 |

### 3. 系统安全 / System Security

| 要求 | 描述 |
|------|------|
| 访问控制 | 只有授权人员才能访问系统 |
| 权限管理 | 基于角色的访问控制 |
| 密码策略 | 强密码要求 |
| 会话管理 | 自动登出机制 |

### 4. 验证要求 / Validation Requirements

- 系统必须经过验证
- 验证文档需要保持
- 系统变更需要受控

## 合规检查清单 / Compliance Checklist

### 审计追踪

- [ ] 审计追踪功能已启用
- [ ] 记录所有创建操作
- [ ] 记录所有修改操作
- [ ] 记录所有删除操作
- [ ] 时间戳准确
- [ ] 审计追踪不可被修改

### 电子签名

- [ ] 电子签名唯一对应个人
- [ ] 电子签名不可共享
- [ ] 签名包含含义
- [ ] 签名包含日期时间

### 访问控制

- [ ] 用户身份验证机制
- [ ] 基于角色的权限控制
- [ ] 密码复杂度要求
- [ ] 账户锁定机制
- [ ] 会话超时

### 系统验证

- [ ] 系统已验证
- [ ] 验证文档完整
- [ ] 变更控制流程
- [ ] 培训记录

## 常见违规 / Common Violations

1. **审计追踪缺失** - 未启用或未配置审计追踪
2. **电子签名不合规** - 电子签名可被共享或复用
3. **访问控制不足** - 弱密码或共享账户
4. **验证不充分** - 验证文档不完整或缺失
5. **变更失控** - 系统变更未受控

## EU Annex 11 关系 / Relationship with EU Annex 11

Part 11 与 EU Annex 11 有很多相似之处，两者都强调:

- 审计追踪
- 访问控制
- 电子签名
- 系统验证
- 变更控制

两者主要区别:

- Part 11 是美国法规
- Annex 11 是欧盟指南
- 具体要求可能略有不同

## 实施建议 / Implementation Recommendations

1. **风险评估** - 评估系统对产品质量和患者安全的影响
2. **供应商评估** - 评估供应商的 Part 11 合规性
3. **系统验证** - 验证系统的 Part 11 功能
4. **流程定义** - 定义操作流程和培训要求
5. **持续监控** - 持续监控合规状态
