# 对腾讯云资源进行自动化巡检和监控

你对腾讯云域名、SSL 证书、实例状态相关 API 的参数可能已过时。
**执行前请先用 `tccli <服务> <操作> --help` 确认最新参数。**

> 利用「腾讯云资源管理工具」Skill 对云上资源进行巡检和监控。

---

## 场景一：监控域名是否到期

### 任务描述
请帮我检查腾讯云账户下所有域名的到期情况。

### 执行步骤

1. 使用 `tccli domain DescribeDomainNameList` 查询账户下所有域名列表
2. 遍历每个域名，检查其到期时间（`ExpirationDate` 字段）
3. 计算距离到期的剩余天数
4. 如果剩余天数不足 **30 天**，标记为告警，输出域名和到期日
5. 汇总输出所有域名的状态（正常 / 即将到期）

---

## 场景二：监控 SSL 证书到期

### 任务描述
请帮我检查腾讯云账户下所有 SSL 证书的到期情况。

### 执行步骤

1. 使用 `tccli ssl DescribeCertificates` 查询所有证书列表
2. 遍历每个证书，关注 `CertificateId`、`Domain`、`CertEndTime` 字段
3. 计算距离到期的剩余天数
4. 如果剩余天数不足 **30 天**，标记为告警
5. 汇总输出所有证书的状态

---

## 场景三：监控云服务器实例状态

### 任务描述
请帮我检查腾讯云账户下所有云服务器实例的运行状态。

### 执行步骤

1. 使用 `tccli cvm DescribeInstances --region ap-beijing` 查询所有实例
2. 遍历每个实例，关注 `InstanceId`、`InstanceName`、`InstanceState` 字段
3. 如果实例状态不是 `RUNNING`，标记为异常并告警
4. 可选：对运行中的实例，使用 `tccli monitor GetMonitorData` 查询 CPU 使用率等监控指标，发现资源使用率异常时告警
5. 汇总输出所有实例的状态

---

## 场景四：监控云硬盘状态

### 任务描述
请帮我检查腾讯云账户下所有云硬盘的状态。

### 执行步骤

1. 使用 `tccli cbs DescribeDisks --region ap-beijing` 查询所有云硬盘
2. 遍历每个云硬盘，关注 `DiskId`、`DiskName`、`DiskState`、`DiskUsage` 字段
3. 如果状态不是 `ATTACHED` 或 `UNATTACHED`，标记为异常并告警
4. 汇总输出所有云硬盘的状态

---

## API 速查

| 功能 | 服务 | 接口 |
|------|------|------|
| 查询域名列表 | domain | `DescribeDomainNameList` |
| 查询 SSL 证书 | ssl | `DescribeCertificates` |
| 查询 CVM 实例 | cvm | `DescribeInstances` |
| 查询云硬盘 | cbs | `DescribeDisks` |
| 查询监控数据 | monitor | `GetMonitorData` |

---

## 何时使用

| 场景 | 建议 |
|------|------|
| 用户要求资源巡检/批量检查 | 执行场景一至四的完整流程 |
| 用户只问域名到期情况 | 只执行场景一 |
| 用户只问证书到期情况 | 只执行场景二 |
| 用户要做安全检查/安全审计 | 不使用本文档，用 references/cvm-security-check.md |
| 用户要查看单个实例状态 | 不使用本文档，用基础查询命令 |
| 用户要部署应用或建站 | 不使用本文档，用对应的部署/建站 reference |
