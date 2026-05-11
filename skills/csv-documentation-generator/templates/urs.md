# 用户需求规格 / User Requirements Specification

| 属性 / Attribute | 内容 / Content |
|-----------------|----------------|
| 文档编号 / Document ID | {DOC_ID} |
| 版本 / Version | {VERSION} |
| 日期 / Date | {DATE} |
| 作者 / Author | {AUTHOR} |
| 审核 / Reviewer | {REVIEWER} |
| 批准 / Approver | {APPROVER} |
| 系统名称 / System Name | {SYSTEM_NAME} |
| 系统版本 / System Version | {SYSTEM_VERSION} |
| GAMP 分类 / GAMP Category | Category {GAMP_CATEGORY} |

---

## 1. 目的 / Purpose

{PURPOSE_TEXT}

> **AI填充指引**: 本章节应描述系统的业务背景和验证目标。
> - 如果是**新系统**: 描述系统的业务目标和预期用途
> - 如果是**变更项目**: 描述变更内容及变更原因

## 2. 范围 / Scope

### 2.1 系统概述 / System Overview

{SYSTEM_OVERVIEW}

> **AI填充指引**: 描述系统用途、主要业务目标和用户群体。

### 2.2 纳入的功能 / Included Functions

| 模块 / Module | 描述 / Description | 优先级 / Priority |
|-------------|-------------------|------------------|
| {MODULE_NAME} | {MODULE_DESCRIPTION} | [{必须}/{应该}/{可以}] |

> **AI填充指引**: 
> - 根据业务调研识别系统模块
> - 优先级基于GxP关键性和业务重要性判断

### 2.3 排除的功能 / Excluded Functions

| 功能 / Function | 排除原因 / Reason for Exclusion |
|----------------|--------------------------------|
| {EXCLUDED_FUNCTION} | {REASON} |

> **AI填充指引**: 明确哪些功能不在本验证范围内及原因。

### 2.4 用户群体 / User Groups

| 用户群体 / User Group | 描述 / Description | 使用频率 / Frequency |
|----------------------|-------------------|---------------------|
| {USER_GROUP} | {DESCRIPTION} | {FREQUENCY} |

> **AI填充指引**: 识别所有使用系统的用户群体及其使用场景。

## 3. 法规与标准要求 / Regulatory and Standards Requirements

### 3.1 数据完整性 - ALCOA+ / Data Integrity - ALCOA+

> **AI填充指引**: ALCOA+原则为GxP系统通用要求，可直接保留此框架。

| 要求 / Requirement | 描述 / Description | 优先级 / Priority |
|-------------------|-------------------|------------------|
| Attributable / 可归属 | {DESCRIPTION} | [必须] |
| Legible / 可读 | {DESCRIPTION} | [必须] |
| Contemporaneous / 同步 | {DESCRIPTION} | [必须] |
| Original / 原始 | {DESCRIPTION} | [必须] |
| Accurate / 准确 | {DESCRIPTION} | [必须] |
| Complete / 完整 | {DESCRIPTION} | [应该] |
| Consistent / 一致 | {DESCRIPTION} | [应该] |
| Enduring / 持久 | {DESCRIPTION} | [必须] |

### 3.2 电子记录与签名 / Electronic Records and Signatures

> **AI填充指引**: 根据系统是否涉及电子记录和签名，选择性填充。

| 要求 / Requirement | 描述 / Description | 优先级 / Priority |
|-------------------|-------------------|------------------|
| 审计追踪 / Audit Trail | {根据GxP记录识别填充} | [{必须}/{应该}] |
| 电子签名 / Electronic Signature | {如适用则填写} | [{必须}/{应该}] |
| 访问控制 / Access Control | {DESCRIPTION} | [必须] |
| 权限管理 / Role-based Access | {DESCRIPTION} | [必须] |
| 密码策略 / Password Policy | {DESCRIPTION} | [必须] |
| 会话管理 / Session Management | {DESCRIPTION} | [应该] |
| 权限分离 / Segregation of Duties | {DESCRIPTION} | [必须] |

### 3.3 GxP记录识别 / GxP Records Identification

> **GAMP 5 M12 Critical Thinking要求**: AI Agent必须识别哪些数据是GxP受监管记录，避免"全部审计"的过度做法。

{GXP_RECORDS_SECTION}

> **AI填充指引**: 
> 1. 列出系统中所有GxP受监管记录
> 2. 明确哪些记录需要审计追踪
> 3. 区分需要审计追踪的记录和不需要的记录

### 3.4 其他法规要求 / Other Regulatory Requirements

| 法规/标准 | 要求描述 | 适用条款 |
|----------|---------|---------|
| {REGULATION} | {DESCRIPTION} | {CLAUSE} |

> **AI填充指引**: 根据系统类型和目标市场，补充适用的法规要求。

## 4. 功能需求 / Functional Requirements

### 4.1 {MODULE_NAME} / {Module Name}

> **AI填充指引**: 
> - 每个功能模块单独一节
> - 按模块逐项填充需求
> - 使用统一ID格式: URS-{SEQ}

| ID | 需求描述 / Requirement Description | 优先级 / Priority | 验证方法 / Verification |
|----|-----------------------------------|------------------|----------------------|
| URS-{SEQ:001} | {REQUIREMENT_TEXT} | [{必须}/{应该}/{可以}] | [{测试}/{审查}] |

### 4.2 {MODULE_NAME} / {Module Name}

| ID | 需求描述 / Requirement Description | 优先级 / Priority | 验证方法 / Verification |
|----|-----------------------------------|------------------|----------------------|
| URS-{SEQ:XXX} | {REQUIREMENT_TEXT} | [{必须}/{应该}/{可以}] | [{测试}/{审查}] |

### 4.3 {MODULE_NAME} / {Module Name}

| ID | 需求描述 / Requirement Description | 优先级 / Priority | 验证方法 / Verification |
|----|-----------------------------------|------------------|----------------------|
| URS-{SEQ:XXX} | {REQUIREMENT_TEXT} | [{必须}/{应该}/{可以}] | [{测试}/{审查}] |

> **AI填充指引**: 
> - ID编号必须连续
> - 需求描述格式: "系统应[功能动词]+[具体对象]+[条件/标准]"
> - 高风险需求（安全、合规）优先标记[必须]
> - 追溯到后续FS/TS文档

## 5. 非功能需求 / Non-Functional Requirements

### 5.1 性能要求 / Performance Requirements

| 指标 / Metric | 要求 / Requirement | 测试阈值 / Test Threshold |
|--------------|-------------------|--------------------------|
| {METRIC} | {REQUIREMENT} | {THRESHOLD} |

> **AI填充指引**: 根据业务需求和用户规模确定性能指标。

### 5.2 安全要求 / Security Requirements

| 要求 / Requirement | 标准 / Standard | 验证方法 |
|-------------------|----------------|---------|
| {SECURITY_REQUIREMENT} | {STANDARD} | [{测试}/{审查}] |

### 5.3 可用性要求 / Availability Requirements

| 指标 / Metric | 要求 / Requirement |
|--------------|-------------------|
| {METRIC} | {REQUIREMENT} |

### 5.4 兼容性要求 / Compatibility Requirements

| 类型 / Type | 要求 / Requirements |
|------------|-------------------|
| {TYPE} | {REQUIREMENT} |

### 5.5 可维护性要求 / Maintainability Requirements

| 要求 / Requirement | 描述 / Description |
|-------------------|-------------------|
| {REQUIREMENT} | {DESCRIPTION} |

## 6. 验收标准 / Acceptance Criteria

### 6.1 功能验收 / Functional Acceptance

| # | 验收条件 / Acceptance Condition | 优先级 / Priority | 验证方法 |
|---|--------------------------------|------------------|---------|
| {SEQ:1} | {ACCEPTANCE_CONDITION} | [{必须}/{应该}] | [{测试}/{审查}] |

### 6.2 性能验收 / Performance Acceptance

| # | 验收条件 / Acceptance Condition | 目标值 | 验证方法 |
|---|--------------------------------|-------|---------|
| {SEQ:1} | {ACCEPTANCE_CONDITION} | {TARGET} | {METHOD} |

### 6.3 安全验收 / Security Acceptance

| # | 验收条件 / Acceptance Condition | 验证方法 |
|---|--------------------------------|---------|
| {SEQ:1} | {ACCEPTANCE_CONDITION} | {METHOD} |

### 6.4 文档验收 / Documentation Acceptance

| 验收项 | 状态 |
|--------|------|
| 验证文档完整且经过审核批准 | [ ] |
| 用户操作手册已编写 | [ ] |
| 管理员操作手册已编写 | [ ] |
| 培训记录已保存 | [ ] |

## 7. 术语表 / Glossary

| 术语 / Term | 定义 / Definition |
|------------|------------------|
| {TERM} | {DEFINITION} |

## 8. 批准 / Approval

| 角色 / Role | 签名 / Signature | 日期 / Date |
|-------------|-----------------|-------------|
| 系统负责人 / System Owner | | |
| QA 负责人 / QA Lead | | |
| 业务负责人 / Business Owner | | |
| IT 负责人 / IT Lead | | |