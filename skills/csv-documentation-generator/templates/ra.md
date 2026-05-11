# 风险评估 / Risk Assessment

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

## 1.5 变更说明 / Change Description

{CHANGE_DESCRIPTION}

> **AI填充指引**: 
> - 如果是变更项目，描述变更内容
> - 如果是新项目，此章节可留空
> - 变更风险应追溯到VP中的变更描述

## 2. 范围 / Scope

### 2.1 评估范围 / Assessment Scope

| 类别 | 范围 | 优先级 |
|------|------|--------|
| {CATEGORY_NAME} | {SCOPE_DESCRIPTION} | [{必须}/{应该}] |

### 2.2 关键功能 / Critical Functions

> **GAMP 5 M12批判性思维**: 关键功能识别应基于GxP影响和业务关键性。

| 功能 | 关键程度 | 原因 | 追溯URS |
|------|---------|------|--------|
| {FUNCTION_NAME} | [{高}/{中}/{低}] | {REASON} | {URS_IDS} |

### 2.3 评估方法 / Assessment Method

{ASSESSMENT_METHOD}

> **AI填充指引**: 默认使用FMEA方法，结合GAMP 5 QRM最佳实践。

### 2.4 参考文档 / Reference Documents

| 文档 | 文档编号 | 版本 |
|------|---------|------|
| {DOC_NAME} | {DOC_ID} | {VERSION} |

## 3. 风险评估标准 / Risk Assessment Criteria

### 3.1 严重性等级 / Severity Levels

| 等级 | 评分 | 描述 | 影响 |
|------|------|------|------|
| 严重 / Critical | 5 | {DESCRIPTION} | {IMPACT} |
| 高 / High | 4 | {DESCRIPTION} | {IMPACT} |
| 中 / Medium | 3 | {DESCRIPTION} | {IMPACT} |
| 低 / Low | 2 | {DESCRIPTION} | {IMPACT} |
| 可忽略 / Negligible | 1 | {DESCRIPTION} | {IMPACT} |

### 3.2 可能性等级 / Likelihood Levels

| 等级 | 评分 | 描述 | 发生频率 |
|------|------|------|---------|
| 频繁 / Frequent | 5 | {DESCRIPTION} | {FREQUENCY} |
| 可能 / Probable | 4 | {DESCRIPTION} | {FREQUENCY} |
| 偶尔 / Occasional | 3 | {DESCRIPTION} | {FREQUENCY} |
| 罕见 / Remote | 2 | {DESCRIPTION} | {FREQUENCY} |
| 不可能 / Improbable | 1 | {DESCRIPTION} | {FREQUENCY} |

### 3.3 可检测性等级 / Detectability Levels

| 等级 | 评分 | 描述 |
|------|------|------|
| 几乎不可能 / Almost Impossible | 5 | {DESCRIPTION} |
| 困难 / Difficult | 4 | {DESCRIPTION} |
| 一般 / Moderate | 3 | {DESCRIPTION} |
| 容易 / Easy | 2 | {DESCRIPTION} |
| 几乎肯定 / Almost Certain | 1 | {DESCRIPTION} |

### 3.4 风险优先级 / Risk Priority Number (RPN)

**RPN = 严重性 × 可能性 × 可检测性**

| RPN 范围 | 风险等级 | 颜色标识 | 行动要求 |
|----------|---------|---------|---------|
| 1-25 | 低风险 / Low | 绿色 | 接受，可不采取行动 |
| 26-50 | 中风险 / Medium | 黄色 | 需要关注，制定缓解措施 |
| 51-75 | 高风险 / High | 橙色 | 必须采取缓解措施 |
| 76-125 | 严重风险 / Critical | 红色 | 立即采取行动，暂停上线 |

## 4. 风险评估 / Risk Assessment

> **GAMP 5 M12层级风险规则**: 子功能风险不得高于父功能风险。

### 4.1 {CATEGORY_NAME} / {Category Name}

| ID | 风险描述 | 严重性 | 可能性 | 可检测性 | RPN | 风险等级 | 缓解措施 | 状态 |
|----|---------|--------|--------|----------|-----|----------|---------|------|
| {RA-ID} | {RISK_DESCRIPTION} | {S} | {L} | {D} | {RPN} | {RISK_LEVEL} | {MITIGATION} | [{已实施}/{待实施}] |

### 4.2 {CATEGORY_NAME} / {Category Name}

| ID | 风险描述 | 严重性 | 可能性 | 可检测性 | RPN | 风险等级 | 缓解措施 | 状态 |
|----|---------|--------|--------|----------|-----|----------|---------|------|
| {RA-ID} | {RISK_DESCRIPTION} | {S} | {L} | {D} | {RPN} | {RISK_LEVEL} | {MITIGATION} | [{已实施}/{待实施}] |

> **AI填充指引**: 
> - ID格式: RA-{CategoryPrefix}-{SEQ}
> - 子类别风险不得高于父类别风险
> - 追溯到URS需求ID

## 5. 风险评估汇总 / Risk Assessment Summary

### 5.1 风险统计 / Risk Statistics

| 风险类别 | 总风险数 | 高风险 | 中风险 | 低风险 |
|---------|---------|--------|--------|--------|
| {CATEGORY} | {COUNT} | {HIGH} | {MEDIUM} | {LOW} |
| **总计** | {TOTAL} | {HIGH_TOTAL} | {MEDIUM_TOTAL} | {LOW_TOTAL} |

### 5.2 风险分布 / Risk Distribution

| RPN范围 | 数量 | 占比 | 颜色 |
|---------|------|------|------|
| 76-125 (严重) | {COUNT} | {PERCENTAGE} | 红 |
| 51-75 (高) | {COUNT} | {PERCENTAGE} | 橙 |
| 26-50 (中) | {COUNT} | {PERCENTAGE} | 黄 |
| 1-25 (低) | {COUNT} | {PERCENTAGE} | 绿 |

## 6. 风险缓解措施 / Risk Mitigation

### 6.1 已采取的措施 / Implemented Mitigations

| 风险ID | 缓解措施 | 实施日期 | 责任部门 | 验证方法 |
|--------|---------|---------|---------|---------|
| {RA-ID} | {MITIGATION} | {DATE} | {OWNER} | {METHOD} |

### 6.2 残余风险 / Residual Risks

| 风险ID | 残余风险描述 | 初始RPN | 残余RPN | 接受决定 | 批准人 |
|--------|-------------|---------|--------|---------|-------|
| {RA-ID} | {DESCRIPTION} | {INITIAL_RPN} | {RESIDUAL_RPN} | {DECISION} | {APPROVER} |

### 6.3 风险接受 / Risk Acceptance

| 风险ID | 风险描述 | 接受理由 | 批准人 | 批准日期 |
|--------|---------|---------|-------|---------|
| {RA-ID} | {DESCRIPTION} | {JUSTIFICATION} | {APPROVER} | {DATE} |

## 7. 风险监控 / Risk Monitoring

### 7.1 监控指标 / Monitoring Metrics

| 风险ID | 监控指标 | 监控频率 | 告警阈值 | 责任人 |
|--------|---------|---------|---------|-------|
| {RA-ID} | {METRIC} | {FREQUENCY} | {THRESHOLD} | {OWNER} |

### 7.2 定期审查 / Periodic Review

| 审查内容 | 审查频率 | 负责团队 |
|---------|---------|---------|
| {REVIEW_ITEM} | {FREQUENCY} | {TEAM} |

## 8. 风险评估结论 / Risk Assessment Conclusion

### 8.1 总体评估 / Overall Assessment

| 评估项 | 结论 |
|--------|------|
| 风险识别完整性 | [{充分}/{部分}] |
| 缓解措施有效性 | [{有效}/{待改进}] |
| 残余风险可接受性 | [{可接受}/{需关注}] |
| 上线建议 | [{可以上线}/{有条件上线}/{暂不上线}] |

### 8.2 后续行动 / Next Actions

| 行动项 | 负责方 | 完成日期 |
|--------|-------|---------|
| {ACTION} | {OWNER} | {DATE} |

## 9. 批准 / Approval

| 角色 / Role | 签名 / Signature | 日期 / Date |
|-------------|-----------------|-------------|
| 系统负责人 / System Owner | | |
| IT 负责人 / IT Lead | | |
| QA 负责人 / QA Lead | | |
| 质量总监 / Quality Director | | |
| 安全负责人 / Security Lead | | |

---

## 附录 / Appendices

### 附录 A: 风险评估方法说明 / Appendix A: Risk Assessment Methodology

#### A.1 FMEA 方法

{ FMEA_METHOD_DESCRIPTION }

#### A.2 评分标准

详见第3节风险评估标准。

### 附录 B: 参考文献 / Appendix B: References

1. GAMP 5 Second Edition - Good Automated Manufacturing Practice
2. 21 CFR Part 11 - Electronic Records and Signatures
3. EU Annex 11 - Computerised Systems
4. ISPE Risk-Based Validation
5. ICH Q9 - Quality Risk Management