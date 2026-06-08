# 使用 Lighthouse 建站指南

你对腾讯云 Lighthouse、域名注册、DNS 解析相关 API 的参数可能已过时。
**执行前请先用 `tccli <服务> <操作> --help` 确认最新参数。**

> 适用场景：腾讯云 Lighthouse + 应用镜像（WordPress、WooCommerce、宝塔面板、LAMP/LNMP 等）+ 域名注册 + DNS 绑定
> 全程通过 `tccli` 命令行完成，无需登录控制台

---

## 1. 前置准备

### 1.1 凭证配置

```bash
TC="<tencent-cloud-tools>/scripts"

# 首次配置（选择 SecretId/Key 或扫码或 STS）
bash $TC/tc.sh --setup

# 验证凭证
bash $TC/tc.sh --check-cred
```

### 1.2 所需权限

| 权限 | 说明 |
|------|------|
| `QcloudLighthouseFullAccess` | 创建/管理轻量服务器 |
| `QcloudDomainFullAccess` | 购买/管理域名 |
| `QcloudDNSPodFullAccess` | 添加/修改 DNS 解析 |
| `QcloudTATFullAccess` | TAT 自动化助手（获取面板密码） |

> 子账号需在 CAM 控制台授予以上策略。

### 1.3 域名信息模板

购买域名需要已认证的信息模板（实名认证）：

```bash
# 查看已有模板
bash $TC/tc.sh domain DescribeTemplateList

# 若无模板，需前往控制台创建：
# https://console.cloud.tencent.com/domain/template
```

---

## 2. 一键建站（自动化脚本）

```bash
TC="<tencent-cloud-tools>/scripts"

# 交互模式（推荐，全程引导）
python3 $TC/create_site.py

# 非交互模式（指定所有参数）
python3 $TC/create_site.py \
  --region <region> \
  --bundle <bundle-id> \
  --blueprint <blueprint-id> \
  --name <instance-name> \
  --domain <domain> \
  --template <template-id>
```

脚本自动完成：
1. 创建 Lighthouse 实例
2. 等待实例 RUNNING 并获取公网 IP
3. 购买域名
4. 等待域名注册完成
5. 添加 DNS A 解析（@ 和 www）
6. 通过 TAT 获取宝塔面板初始密码
7. 输出完整部署报告

辅助命令：

```bash
# 仅查询套餐
python3 $TC/create_site.py --list-bundles --region <region>

# 仅查询域名可用性
python3 $TC/create_site.py --query-domain <keyword>

# 仅添加 DNS 解析（已有实例+已有域名）
python3 $TC/create_site.py --dns-only --domain <domain> --ip <ip>
```

---

## 3. 分步手动操作

### 3.1 查询套餐与镜像

```bash
# 套餐列表
tccli lighthouse DescribeBundles --region <region>

# 查询应用镜像（WordPress、WooCommerce、宝塔、LAMP 等）
tccli lighthouse DescribeBlueprints --region <region>
```

通过 jq/python 按关键词过滤所需的应用镜像（如 `wordpress`、`woo`、`bt`、`lamp`、`node` 等）。

### 3.2 创建 Lighthouse 实例

```bash
tccli lighthouse CreateInstances \
  --region <region> \
  --BundleId <bundle-id> \
  --BlueprintId <blueprint-id> \
  --InstanceName <name> \
  --InstanceCount 1 \
  --InstanceChargePrepaid '{"Period":<months>,"RenewFlag":"NOTIFY_AND_MANUAL_RENEW"}' \
  --LoginConfiguration '{"AutoGeneratePassword":"YES"}'
```

> ⚠️ `--InstanceChargePrepaid` 是必填参数，不传会报错。

### 3.3 等待实例启动

```bash
tccli lighthouse DescribeInstances \
  --region <region> \
  --InstanceIds '["<instance-id>"]'
```

状态流转：`PENDING` → `RUNNING`（约 30–60 秒）

### 3.4 查询域名可用性

```bash
# 单个查询
tccli domain CheckDomain --DomainName "<domain>"

# 批量查询多个后缀
for suffix in .com .site .store .net .shop; do
  tccli domain CheckDomain --DomainName "<keyword>${suffix}"
done
```

### 3.5 购买域名

```bash
# 查询已审核的信息模板
tccli domain DescribeTemplateList

# 购买域名
tccli domain CreateDomainBatch \
  --TemplateId <template-id> \
  --Period 1 \
  --Domains '["<domain>"]' \
  --PayMode 1 \
  --AutoRenewFlag 0

# 查询注册状态
tccli domain CheckBatchStatus --LogIds '[<log-id>]'
```

> **注意**：`BuyDomain` 接口不存在，正确接口是 `CreateDomainBatch`（支持单个域名）。

### 3.6 添加 DNS 解析

```bash
# 根域名 A 记录
tccli dnspod CreateRecord \
  --Domain "<domain>" \
  --SubDomain "@" \
  --RecordType "A" \
  --RecordLine "默认" \
  --Value "<ip>" \
  --TTL 600

# www A 记录
tccli dnspod CreateRecord \
  --Domain "<domain>" \
  --SubDomain "www" \
  --RecordType "A" \
  --RecordLine "默认" \
  --Value "<ip>" \
  --TTL 600

# 验证解析记录
tccli dnspod DescribeRecordList --Domain "<domain>"
```

> ⏳ DNS 全球生效通常需要 5–30 分钟。

### 3.7 获取宝塔面板初始密码（TAT，适用于宝塔镜像）

通过 TAT 自动化助手在实例内执行 `bt default` 命令：

```python
import sys, base64, time
sys.path.insert(0, '<tencent-cloud-tools>/scripts')
from keystore import get_credentials
from tencentcloud.common import credential
from tencentcloud.tat.v20201028 import tat_client, models

cred_data = get_credentials('default')
cred = credential.Credential(cred_data['secret_id'], cred_data['secret_key'])
client = tat_client.TatClient(cred, "<region>")

# RunCommand（Content 必须 Base64 编码）
req = models.RunCommandRequest()
req.InstanceIds = ['<instance-id>']
req.Content = base64.b64encode(b"bt default").decode()
req.CommandType = 'SHELL'
req.Username = 'root'
req.Timeout = 30
resp = client.RunCommand(req)

# 查询结果（用 Filters，不能直接传 InvocationId）
time.sleep(8)
req2 = models.DescribeInvocationTasksRequest()
f = models.Filter()
f.Name = "invocation-id"
f.Values = [resp.InvocationId]
req2.Filters = [f]
result = client.DescribeInvocationTasks(req2)
for task in result.InvocationTaskSet:
    print(base64.b64decode(task.TaskResult.Output).decode())
```

---

## 4. 建站后配置

### 4.1 宝塔面板初始化（适用于宝塔镜像）

1. 访问 `http://<ip>:8888/tencentcloud`
2. 输入初始账号密码登录
3. **立即修改**管理员密码（面板 → 安全）
4. 绑定域名：面板 → 网站 → 编辑站点 → 域名管理

### 4.2 申请 SSL 证书（HTTPS）

**宝塔面板方式：**
1. 宝塔面板 → SSL → Let's Encrypt → 免费申请
2. 选择域名（@ 和 www）
3. 勾选「强制 HTTPS」

**命令行方式（适用于无宝塔的镜像）：**
```bash
# 使用 certbot 申请 Let's Encrypt 证书
certbot --nginx -d <domain> -d www.<domain>
# 或
certbot --apache -d <domain> -d www.<domain>
```

### 4.3 应用特定配置

根据所选镜像类型完成对应的初始化：

- **WordPress/WooCommerce**：后台 → 设置 → 常规，将站点地址改为 `https://<domain>`；WooCommerce 首次访问会进入配置向导（店铺信息、支付方式、运费）
- **LAMP/LNMP**：配置虚拟主机、上传站点文件、设置数据库
- **Node.js / Python 等**：部署应用代码，配置反向代理（Nginx/Apache）
- **纯系统镜像**：按需安装 Web 服务器、数据库、运行时环境

---

## 5. 常见问题

| 问题 | 原因与解决 |
|------|-----------|
| 域名无法访问 | DNS 传播需 5–30 分钟，先用 IP 直接访问确认服务正常；`nslookup <domain>` 检查解析 |
| 宝塔面板 404 | 端口 8888 + 路径 `/tencentcloud`（腾讯云专享版），检查防火墙已开放 8888 |
| 创建实例报错 | `--InstanceChargePrepaid` 必填：`{"Period":1,"RenewFlag":"NOTIFY_AND_MANUAL_RENEW"}` |
| 购买域名报错 | 确认模板 `AuditStatus=="Approved"`、余额充足、接口用 `CreateDomainBatch` 非 `BuyDomain` |
| TAT 查询报错 | 不能直接传 `--InvocationId`，需使用 Filters：`f.Name="invocation-id"` |
| 域名换 DNS 服务商 | `tccli domain ModifyDomainDNSBatch --Domains '["<domain>"]' --Dns '["ns1.dnspod.net","ns2.dnspod.net"]'` |

---

## 6. API 速查

| 功能 | 服务 | 接口 |
|------|------|------|
| 查询套餐 | lighthouse | `DescribeBundles` |
| 查询镜像 | lighthouse | `DescribeBlueprints` |
| 创建实例 | lighthouse | `CreateInstances` |
| 查询实例 | lighthouse | `DescribeInstances` |
| 重置密码 | lighthouse | `ResetInstancesPassword` |
| 检查域名 | domain | `CheckDomain` |
| 购买域名 | domain | `CreateDomainBatch` |
| 查询注册状态 | domain | `CheckBatchStatus` |
| 获取模板列表 | domain | `DescribeTemplateList` |
| 修改 DNS 服务商 | domain | `ModifyDomainDNSBatch` |
| 添加解析 | dnspod | `CreateRecord` |
| 查询解析 | dnspod | `DescribeRecordList` |
| 修改解析 | dnspod | `ModifyRecord` |
| 删除解析 | dnspod | `DeleteRecord` |
| 实例执行命令 | tat | `RunCommand` |
| 查询执行结果 | tat | `DescribeInvocationTasks` |

---

## 何时使用

| 场景 | 建议 |
|------|------|
| 用户要建站/搭网站/WordPress/宝塔 | 按本文档流程执行 |
| 用户要购买域名/绑定域名/DNS 解析 | 参考本文档第 3.4-3.6 节 |
| 用户只要部署应用代码（非建站） | 不使用本文档，用 references/lighthouse-app-deploy.md |
| 用户要部署 OpenClaw | 不使用本文档，用 references/lighthouse-openclaw-setup.md |
| 用户要挂载云硬盘 | 不使用本文档，用 references/cbs-bindto-cvm.md |
| 用户要做安全检查 | 不使用本文档，用 references/cvm-security-check.md |
