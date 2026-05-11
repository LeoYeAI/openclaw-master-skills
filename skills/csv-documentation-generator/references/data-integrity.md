# ALCOA+ 数据完整性原则 / ALCOA+ Data Integrity Principles

## 什么是 ALCOA+? / What is ALCOA+?

ALCOA+ 是一个用于确保数据完整性的原则框架，最初由 FDA 提出，后被行业广泛采用。

ALCOA+ is a framework for ensuring data integrity, originally developed by FDA and widely adopted by the industry.

## ALCOA+ 原则 / ALCOA+ Principles

```
┌────────────────────────────────────────────────────────────┐
│                      ALCOA+ 原则                           │
└────────────────────────────────────────────────────────────┘

    A - Attributable    可归属
    L - Legible         可读
    C - Contemporaneous 同步
    O - Original        原始
    A - Accurate        准确
    
    + - Complete        完整
    + - Consistent      一致
    + - Enduring       持久
```

## 原则详解 / Principle Details

### A - Attributable (可归属)

**定义**: 所有记录和数据必须能够追溯到创建或修改该数据的人。

**Requirement**: All records and data must be traceable to the person who created or modified the data.

**实施要点**:
- 用户必须唯一标识
- 所有操作必须记录操作者
- 电子签名必须唯一对应个人

**实施检查**:
- [ ] 用户唯一标识
- [ ] 审计追踪记录操作者
- [ ] 电子签名唯一

---

### L - Legible (可读)

**定义**: 数据必须清晰、可读，能够被人类理解和解释。

**Requirement**: Data must be clear, readable, and understandable by humans.

**实施要点**:
- 使用标准格式
- 避免数据截断
- 确保长期可读性

**实施检查**:
- [ ] 数据格式标准化
- [ ] 存储格式可读
- [ ] 备份数据可恢复

---

### C - Contemporaneous (同步)

**定义**: 数据必须在事件发生时实时记录，而不是事后补记。

**Requirement**: Data must be recorded at the time the event occurs, not later.

**实施要点**:
- 自动记录而非手动
- 时间戳准确
- 禁止回填数据

**实施检查**:
- [ ] 自动数据捕获
- [ ] 时间同步
- [ ] 禁止手动补录

---

### O - Original (原始)

**定义**: 必须保留原始记录或认证的真实副本。

**Requirement**: Must retain original records or certified true copies.

**实施要点**:
- 保留原始数据
- 防止数据覆盖
- 保留元数据

**实施检查**:
- [ ] 原始数据保留
- [ ] 防止覆盖机制
- [ ] 副本认证

---

### A - Accurate (准确)

**定义**: 数据必须准确反映实际发生的事件。

**Requirement**: Data must accurately reflect the actual events that occurred.

**实施要点**:
- 数据验证
- 质量控制
- 偏差调查

**实施检查**:
- [ ] 数据验证规则
- [ ] 准确性检查
- [ ] 偏差处理流程

---

### +C - Complete (完整)

**定义**: 所有数据必须完整，没有遗漏。

**Requirement**: All data must be complete, without omission.

**实施要点**:
- 记录所有数据
- 保留所有版本
- 包含所有测试数据

**实施检查**:
- [ ] 无数据删除
- [ ] 完整审计追踪
- [ ] 保留所有副本

---

### +C - Consistent (一致)

**定义**: 数据应该一致，无矛盾。

**Requirement**: Data should be consistent, without contradictions.

**实施要点**:
- 系统间数据同步
- 避免数据冲突
- 版本控制

**实施检查**:
- [ ] 数据同步机制
- [ ] 版本控制
- [ ] 一致性验证

---

### +E - Enduring (持久)

**定义**: 记录必须持久保存，符合法规要求的保存期限。

**Requirement**: Records must be retained persistently, meeting regulatory retention requirements.

**实施要点**:
- 长期存储介质
- 定期迁移策略
- 法规合规

**实施检查**:
- [ ] 存储介质可靠
- [ ] 保留期限合规
- [ ] 迁移计划
