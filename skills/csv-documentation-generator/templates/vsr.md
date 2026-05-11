# 验证总结报告 / Validation Summary Report (VSR)

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

## 1. 执行摘要 / Executive Summary

### 1.1 项目概述 / Project Overview

{PROJECT_OVERVIEW}

> **AI填充指引**: 描述项目背景、验证周期和关键里程碑。

### 1.2 验证目标 / Validation Objectives

| 目标 / Objective | 完成情况 |
|----------------|---------|
| {OBJECTIVE} | [{是}/{否}] |

### 1.3 验证结果摘要 / Validation Results Summary

| 验证阶段 | 状态 | 测试用例 | 通过 | 失败 | 通过率 |
|---------|------|---------|------|------|-------|
| IQ | {STATUS} | {COUNT} | {PASS} | {FAIL} | {RATE}% |
| OQ | {STATUS} | {COUNT} | {PASS} | {FAIL} | {RATE}% |
| PQ | {STATUS} | {COUNT} | {PASS} | {FAIL} | {RATE}% |
| **总计** | | {TOTAL} | {TOTAL_PASS} | {TOTAL_FAIL} | {TOTAL_RATE}% |

**最终结论: [{通过}/{有条件通过}/{失败}]**

## 2. 系统概述 / System Overview

### 2.1 系统描述 / System Description

| 项目 | 内容 |
|------|------|
| {PROPERTY} | {VALUE} |

### 2.2 系统架构 / System Architecture

{SYSTEM_ARCHITECTURE_DESCRIPTION}

### 2.3 验证范围 / Validation Scope

| 阶段 | 文档编号 | 版本 | 状态 |
|------|---------|------|------|
| {PHASE} | {DOC_ID} | {VERSION} | [{完成}/{待完成}] |

## 3. 验证执行摘要 / Validation Execution Summary

### 3.1 验证周期 / Validation Timeline

| 阶段 | 开始日期 | 结束日期 | 持续时间(天) |
|------|---------|---------|------------|
| {PHASE} | {START} | {END} | {DURATION} |

### 3.2 验证资源 / Validation Resources

| 角色 | 人数 | 总工时 |
|------|------|-------|
| {ROLE} | {COUNT} | {HOURS} |

### 3.3 验证活动 / Validation Activities

| 活动 | 交付物 | 完成日期 | 状态 |
|------|-------|---------|------|
| {ACTIVITY} | {DELIVERABLE} | {DATE} | {STATUS} |

## 4. 验证结果汇总 / Validation Results Summary

### 4.1 {PHASE_NAME} 结果 / {Phase Name} Results

#### 4.1.1 测试结果统计 / Test Results Summary

| 项目 | 总数 | 通过 | 失败 | 通过率 |
|------|------|------|------|-------|
| {CATEGORY} | {TOTAL} | {PASS} | {FAIL} | {RATE}% |

#### 4.1.2 偏差汇总 / Deviations

| 偏差ID | 描述 | 严重程度 | 状态 |
|--------|------|---------|------|
| {DEV-ID} | {DESCRIPTION} | {SEVERITY} | [{已关闭}/{开放}] |

**{PHASE}结论**: [{通过}/{有条件通过}/{失败}]

### 4.2 {PHASE_NAME} 结果 / {Phase Name} Results

{...类似结构...}

### 4.3 {PHASE_NAME} 结果 / {Phase Name} Results

{...类似结构...}

## 5. 需求可追溯性 / Requirements Traceability

### 5.1 URS 需求验证状态 / URS Requirements Verification Status

{TRACEABILITY_TABLE}

> **AI填充指引**: RTM矩阵自动生成，包含URS→FS→测试用例的完整追溯链。

### 5.2 需求覆盖率 / Requirements Coverage

{COVERAGE_SUMMARY}

## 6. 风险评估回顾 / Risk Assessment Review

### 6.1 初始风险 / Initial Risks

| 风险ID | 风险描述 | 严重性 | 可能性 | RPN | 状态 |
|--------|---------|--------|--------|-----|------|
| {RA-ID} | {DESCRIPTION} | {S} | {L} | {RPN} | {STATUS} |

### 6.2 缓解措施 / Mitigation Measures

| 风险ID | 缓解措施 | 实施状态 | 残余风险 |
|--------|---------|---------|---------|
| {RA-ID} | {MITIGATION} | {STATUS} | {RESIDUAL} |

### 6.3 残余风险 / Residual Risks

| 风险ID | 残余风险描述 | RPN | 接受决定 |
|--------|-------------|-----|---------|
| {RA-ID} | {DESCRIPTION} | {RPN} | {DECISION} |

## 7. 偏差汇总 / Deviation Summary

### 7.1 偏差趋势 / Deviation Trend

| 阶段 | 偏差数 | 已关闭 | 开放 | 关闭率 |
|------|-------|-------|------|-------|
| {PHASE} | {COUNT} | {CLOSED} | {OPEN} | {RATE}% |

### 7.2 未关闭偏差 / Open Deviations

| 偏差ID | 阶段 | 描述 | 影响评估 | 计划关闭日期 |
|--------|------|------|---------|-------------|
| {DEV-ID} | {PHASE} | {DESCRIPTION} | {IMPACT} | {DATE} |

## 8. 变更控制 / Change Control

| 变更编号 | 描述 | 变更类型 | 审批日期 | 影响评估 |
|----------|------|---------|---------|---------|
| {CHANGE-ID} | {DESCRIPTION} | {TYPE} | {DATE} | {IMPACT} |

## 9. 培训记录 / Training Records

| 培训项目 | 培训日期 | 参加人数 | 培训结果 | 备注 |
|---------|---------|---------|---------|------|
| {TRAINING} | {DATE} | {COUNT} | {RESULT} | {NOTES} |

## 10. 验证结论 / Validation Conclusion

### 10.1 功能符合性 / Functional Compliance

| 检查项 | 状态 | 备注 |
|--------|------|------|
| {CHECK_ITEM} | [{通过}/{待改进}] | {NOTES} |

### 10.2 质量符合性 / Quality Compliance

| 检查项 | 状态 | 备注 |
|--------|------|------|
| {CHECK_ITEM} | [{通过}/{待改进}] | {NOTES} |

### 10.3 法规符合性 / Regulatory Compliance

| 检查项 | 状态 | 备注 |
|--------|------|------|
| {CHECK_ITEM} | [{通过}/{待改进}] | {NOTES} |

### 10.4 最终结论 / Final Conclusion

- [ ] {CONCLUSION_ITEM}

**验证结论: [{通过 (PASS)}/{有条件通过 (CONDITIONAL PASS)}/{失败 (FAIL)}]**

## 11. 后续建议 / Recommendations

### 11.1 运营建议 / Operational Recommendations

| 建议 | 优先级 | 负责方 |
|------|--------|-------|
| {RECOMMENDATION} | [{高}/{中}/{低}] | {OWNER} |

### 11.2 维护建议 / Maintenance Recommendations

| 建议 | 优先级 | 负责方 |
|------|--------|-------|
| {RECOMMENDATION} | [{高}/{中}/{低}] | {OWNER} |

## 12. 经验教训 / Lessons Learned

> **GAMP 5 M12 Critical Thinking要求**: 验证总结应包含对验证方法有效性的评估。

### 12.1 成功实践 / What Went Well

| 领域 | 实践描述 | 复用建议 |
|------|---------|---------|
| {AREA} | {DESCRIPTION} | {SUGGESTION} |

### 12.2 改进机会 / What Could Be Improved

| 领域 | 问题描述 | 改进建议 |
|------|---------|---------|
| {AREA} | {DESCRIPTION} | {SUGGESTION} |

### 12.3 下次项目建议 / Recommendations for Future Projects

| 建议类别 | 具体建议 | 优先级 |
|---------|---------|--------|
| {CATEGORY} | {SUGGESTION} | [{高}/{中}/{低}] |

## 13. 持续合规计划 / Ongoing Compliance Plan

> **GAMP 5 O8 Periodic Review要求**: 系统需要定期评审以确保持续符合法规要求。

### 13.1 周期性评审计划 / Periodic Review Schedule

| 评审类型 | 评审内容 | 频率 | 负责团队 | 上次日期 | 下次日期 |
|---------|---------|------|---------|---------|---------|
| {REVIEW_TYPE} | {CONTENT} | {FREQUENCY} | {TEAM} | {LAST_DATE} | {NEXT_DATE} |

### 13.2 持续监控方法 / Continuous Monitoring Approach

> **GAMP 5 M11要求**: 从"固定时间点确认"转向"持续控制监控"方法。

| 监控项 | 监控方法 | 工具/系统 | 阈值 | 告警方式 |
|--------|---------|-----------|------|---------|
| {MONITORING_ITEM} | {METHOD} | {TOOL} | {THRESHOLD} | {ALERT} |

### 13.3 变更影响评估 / Change Impact Assessment

| 变更类型 | 触发条件 | 评估范围 | 审批要求 |
|---------|---------|---------|---------|
| {CHANGE_TYPE} | {TRIGGER} | {SCOPE} | {REQUIREMENT} |

## 14. 批准 / Approval

| 角色 / Role | 签名 / Signature | 日期 / Date |
|-------------|-----------------|-------------|
| {ROLE} | | |

---

## 附录 / Appendices

### 附录 A: 验证交付物清单 / Appendix A: Validation Deliverables Checklist

| # | 交付物 | 文档编号 | 版本 | 状态 | 日期 |
|---|-------|---------|------|------|------|
| {SEQ} | {DELIVERABLE} | {DOC_ID} | {VERSION} | {STATUS} | {DATE} |

### 附录 B: 缩写与术语 / Appendix B: Abbreviations and Terms

| 缩写 | 全称 | 中文 |
|------|------|------|
| {ABBREVIATION} | {FULL_NAME} | {CHINESE} |

### 附录 C: 参考文档 / Appendix C: Reference Documents

| 文档名称 | 文档编号 | 版本 |
|---------|---------|------|
| {DOC_NAME} | {DOC_ID} | {VERSION} |