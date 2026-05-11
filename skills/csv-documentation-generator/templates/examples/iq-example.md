# IQ 填充示例 / IQ Fill Example

> 本文件为IQ模板的完整填充示例，供AI Agent参考填充样式。
> 模板文件(iq.md)仅包含结构，占位符由AI根据业务场景填充。

---

## 3. 环境信息 / Environment Information

### 3.1 硬件环境 / Hardware Environment

#### 3.1.1 服务器清单 / Server Inventory

| 序号 | 主机名 / Hostname | IP地址 | 角色 | 硬件配置 | 厂商 | 序列号 |
|------|-----------------|--------|------|---------|------|-------|
| 1 | app-server-01 | 192.168.1.10 | 应用服务器 | CPU: 8核, 内存: 32GB, 磁盘: 500GB SSD | Dell R740 | ABC123 |
| 2 | db-server-01 | 192.168.1.11 | 数据库服务器 | CPU: 16核, 内存: 64GB, 磁盘: 1TB SSD | Dell R740 | ABC124 |
| 3 | cache-server-01 | 192.168.1.12 | 缓存服务器 | CPU: 4核, 内存: 16GB, 磁盘: 100GB SSD | Dell R640 | ABC125 |

### 3.2 软件环境 / Software Environment

#### 3.2.1 操作系统 / Operating Systems

| 序号 | 主机名 | 操作系统 | 版本 | 内核版本 | 安装日期 |
|------|--------|---------|------|---------|---------|
| 1 | app-server-01 | Ubuntu | 22.04 LTS | 5.15.0 | 2024-01-15 |
| 2 | db-server-01 | Ubuntu | 22.04 LTS | 5.15.0 | 2024-01-15 |
| 3 | cache-server-01 | Ubuntu | 22.04 LTS | 5.15.0 | 2024-01-15 |

#### 3.2.2 中间件 / Middleware

| 序号 | 中间件类型 | 软件名称 | 版本 | 端口 | 状态 |
|------|-----------|---------|------|------|------|
| 1 | Web服务器 | Nginx | 1.24 | 80,443 | 运行中 |
| 2 | 数据库 | PostgreSQL | 15.4 | 5432 | 运行中 |
| 3 | 缓存 | Redis | 7.2 | 6379 | 运行中 |

---

## 4. IQ 确认检查项 / IQ Check Items

### 4.1 硬件确认 / Hardware Qualification

#### 4.1.1 服务器硬件检查 / Server Hardware Check

| 序号 | 检查项目 | 预期结果 | 实际结果 | 状态 | 备注 |
|------|---------|---------|---------|------|------|
| IQ-HW-001 | 服务器型号/品牌 | Dell R740 | Dell R740 | Pass | |
| IQ-HW-002 | CPU规格 | 8核 | 8核 | Pass | |
| IQ-HW-003 | 内存容量 | ≥ 32GB | 32GB | Pass | |
| IQ-HW-004 | 系统盘容量 | ≥ 100GB | 500GB SSD | Pass | |

### 4.2 应用程序确认 / Application Qualification

| 序号 | 检查项目 | 预期结果 | 实际结果 | 状态 | 备注 |
|------|---------|---------|---------|------|------|
| IQ-APP-001 | 应用名称 | CTMS | CTMS | Pass | |
| IQ-APP-002 | 应用版本 | v2.0 | v2.0 | Pass | |
| IQ-APP-003 | 安装路径 | /opt/ctms | /opt/ctms | Pass | |
| IQ-APP-004 | 应用服务状态 | Running | Running | Pass | |

---

## IQ检查项ID编号规则

| 前缀 | 类别 |
|------|------|
| HW | 硬件 / Hardware |
| ST | 存储 / Storage |
| OS | 操作系统 / OS |
| DB | 数据库 / Database |
| CA | 缓存 / Cache |
| WEB | Web服务器 / Web Server |
| APP | 应用程序 / Application |
| NET | 网络 / Network |
| FW | 防火墙 / Firewall |
| SEC | 安全 / Security |
| BAK | 备份 / Backup |
| MON | 监控 / Monitoring |

## IQ检查原则

### GAMP 5 M12批判性思维应用

1. **基于风险的IQ范围**: 根据系统GAMP Category和RA中识别的风险，确定IQ检查范围
2. **配置项vs定制项**: COTS配置验证在IQ中，定制功能测试在OQ中
3. **供应商文档利用**: 利用供应商IQ检查表，减少重复工作