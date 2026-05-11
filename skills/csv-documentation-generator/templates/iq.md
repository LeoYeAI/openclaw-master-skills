# 安装确认 / Installation Qualification (IQ)

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

> **AI填充指引**: 描述IQ验证的目的和范围。

## 2. 范围 / Scope

### 2.1 IQ 确认范围 / IQ Scope

> **GAMP 5 M12批判性思维**: 根据系统风险等级和GAMP Category确定IQ范围。

| 类别 / Category | 项目 / Items | 优先级 / Priority |
|---------------|-------------|------------------|
| {CATEGORY_NAME} | {ITEMS} | [{必须}/{应该}] |

### 2.2 排除范围 / Excluded Scope

- [ ] {EXCLUDED_ITEM}

### 2.3 参考文档 / Reference Documents

| 文档 / Document | 文档编号 / Document ID | 版本 / Version |
|---------------|---------------------|---------------|
| {DOC_NAME} | {DOC_ID} | {VERSION} |

## 3. 环境信息 / Environment Information

### 3.1 硬件环境 / Hardware Environment

#### 3.1.1 服务器清单 / Server Inventory

| 序号 | 主机名 / Hostname | IP地址 | 角色 | 硬件配置 | 厂商 | 序列号 |
|------|-----------------|--------|------|---------|------|-------|
| {SEQ} | {HOSTNAME} | {IP} | {ROLE} | CPU: {CPU}, 内存: {RAM}, 磁盘: {STORAGE} | {VENDOR} | {SERIAL} |

#### 3.1.2 网络设备 / Network Equipment

| 序号 | 设备类型 | 型号 | IP地址 | 端口 | 用途 |
|------|---------|------|--------|------|------|
| {SEQ} | {TYPE} | {MODEL} | {IP} | {PORTS} | {PURPOSE} |

### 3.2 软件环境 / Software Environment

#### 3.2.1 操作系统 / Operating Systems

| 序号 | 主机名 | 操作系统 | 版本 | 内核版本 | 安装日期 |
|------|--------|---------|------|---------|---------|
| {SEQ} | {HOSTNAME} | {OS} | {VERSION} | {KERNEL} | {DATE} |

#### 3.2.2 中间件 / Middleware

| 序号 | 中间件类型 | 软件名称 | 版本 | 端口 | 状态 |
|------|-----------|---------|------|------|------|
| {SEQ} | {TYPE} | {SOFTWARE} | {VERSION} | {PORT} | {STATUS} |

#### 3.2.3 应用程序 / Application Software

| 序号 | 应用名称 | 版本 | 安装路径 | 端口 | 状态 |
|------|---------|------|---------|------|------|
| {SEQ} | {APP_NAME} | {VERSION} | {PATH} | {PORT} | {STATUS} |

## 4. IQ 确认检查项 / IQ Check Items

### 4.1 {CATEGORY_NAME} / {Category Name}

| 序号 | 检查项目 | 预期结果 | 实际结果 | 状态 | 备注 |
|------|---------|---------|---------|------|------|
| {IQ-ID} | {CHECK_ITEM} | {EXPECTED} | {ACTUAL} | [{Pass}/{Fail}] | {NOTES} |

### 4.2 {CATEGORY_NAME} / {Category Name}

| 序号 | 检查项目 | 预期结果 | 实际结果 | 状态 | 备注 |
|------|---------|---------|---------|------|------|
| {IQ-ID} | {CHECK_ITEM} | {EXPECTED} | {ACTUAL} | [{Pass}/{Fail}] | {NOTES} |

> **AI填充指引**: 
> - ID格式: IQ-{CategoryPrefix}-{SEQ}
> - 根据TS和RA确定具体检查项
> - 预期结果应与TS规格一致

## 5. IQ 总结 / IQ Summary

### 5.1 测试结果统计 / Test Results Summary

| 项目 / Item | 总数 / Total | 通过 / Pass | 失败 / Fail | 通过率 / Pass Rate |
|------------|-------------|------------|------------|-------------------|
| {CATEGORY} | {TOTAL} | {PASS} | {FAIL} | {RATE}% |
| **总计 / Total** | {GRAND_TOTAL} | {TOTAL_PASS} | {TOTAL_FAIL} | {GRAND_RATE}% |

### 5.2 偏差记录 / Deviation Records

| 偏差编号 | 检查项 | 描述 | 影响评估 | 纠正措施 | 状态 | 关闭日期 |
|---------|--------|------|---------|---------|------|---------|
| {DEV-ID} | {CHECK_ITEM} | {DESCRIPTION} | {IMPACT} | {CORRECTION} | [{Open}/{Closed}] | {DATE} |

## 6. 结论 / Conclusion

### 6.1 IQ 结论 / IQ Conclusion

| 项目 / Item | 结果 / Result |
|------------|-------------|
| IQ 测试完成日期 | {DATE} |
| IQ 测试结果 | [{Pass}/{Fail}/{Conditional Pass}] |
| 总检查项数 | {TOTAL} |
| 通过项数 | {PASS} |
| 失败项数 | {FAIL} |
| 通过率 | {RATE}% |

### 6.2 后续行动 / Next Actions

| 行动 / Action | 负责方 / Owner | 计划日期 / Planned Date |
|--------------|---------------|------------------------|
| {ACTION} | {OWNER} | {DATE} |

### 6.3 最终结论 / Final Conclusion

- [ ] 系统安装符合技术规格要求
- [ ] 所有关键组件已正确安装和配置
- [ ] 网络和安全配置已验证
- [ ] 环境满足进入OQ测试的前置条件

**结论: 系统 [可以/不可以] 进入 OQ 阶段**

## 7. 批准 / Approval

| 角色 / Role | 签名 / Signature | 日期 / Date |
|-------------|-----------------|-------------|
| 测试工程师 / Test Engineer | | |
| IT 负责人 / IT Lead | | |
| 系统负责人 / System Owner | | |
| QA 审核员 / QA Reviewer | | |
| QA 批准人 / QA Approver | | |