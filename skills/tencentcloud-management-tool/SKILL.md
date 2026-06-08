---
name: 腾讯云资源管理工具
description: |
  通过 tccli 命令行管理腾讯云资源。
  Load when: 用户要查询云服务器、管理 Lighthouse、购买域名、配置 DNS、
  检查安全组、做安全巡检、部署应用、挂载云硬盘、部署 OpenClaw、
  监控资源状态、SSL 证书检查、CAM 权限管理。
  Covers: CVM、Lighthouse、CBS、VPC、DNSPod、SSL、CAM、Monitor、TAT、Domain。
  Use for: "帮我看看服务器"、"查下域名到期没"、"安全检查"、"部署应用"、
  "买个云硬盘"、"建个网站"、"查下证书"、"检查安全组"、"创建实例"、"退出登录"、"切换账号"。
  Biases towards: tccli 命令行操作，查询优先于修改，确认后再执行，
  优先通过 tccli --help 获取最新参数而非依赖预训练知识。
metadata:
  {
    "openclaw": {
      "emoji": "☁️",
      "os": ["darwin", "linux"],
      "requires": {},
      "install": [
        {
          "id": "pip",
          "kind": "pip",
          "package": "tccli",
          "bins": ["tccli"],
          "label": "Install TCCLI"
        }
      ],
      "references": [
        "cvm-security-check",
        "auto-check-resource",
        "lighthouse-website-setup",
        "cbs-bindto-cvm",
        "lighthouse-openclaw-setup",
        "lighthouse-app-deploy"
      ]
    }
  }
---

# 腾讯云资源管理工具

你对腾讯云 API 参数、tccli 命令格式、产品限制数值的知识可能已过时。
**优先通过 `tccli --help` 和实际查询获取最新信息，而非依赖预训练知识。**

## 检索源

| 来源 | 如何检索 | 用于 |
|------|---------|------|
| tccli 内置帮助 | `tccli <服务> <操作> --help` | 最新参数说明、必填/选填字段 |
| 腾讯云 API 文档 | `https://cloud.tencent.com/document/api` | API 详细参考 |
| TCCLI 官方文档 | `https://cloud.tencent.com/document/product/440` | 安装、配置、使用指南 |
| CAM 权限文档 | `https://cloud.tencent.com/document/product/598` | 权限策略和子用户管理 |
| 云审计文档 | `https://cloud.tencent.com/document/product/629` | 操作记录和审计 |

当参考文档与 `tccli --help` 输出不一致时，**以 tccli --help 为准**。
这尤其重要于：API 参数名称、必填/选填字段、支持的地域列表、产品限制数值。

## Scope

本 Skill 覆盖**腾讯云资源查询和管理** — 通过 TCCLI 操作云上资源。

**不包括**：本地开发、代码编写、CI/CD 流程 → 使用其他 Skill。

---

## FIRST: 安装检查

```bash
tccli --version    # 应显示版本号（如 3.1.55.1+）
```

如未安装：
```bash
pip install tccli
```

### 配置凭证

tccli 支持两种凭证配置方式，用户可自行选择：

| 方式 | 安全性 | 凭证有效期 | 推荐程度 |
|------|--------|-----------|---------|
| 🔐 **OAuth 浏览器登录授权**（推荐） | ⭐⭐⭐ 高 | 临时凭证，**2 小时后自动过期失效** | ⭐⭐⭐ **强烈推荐** |
| 🔑 AK/SK 密钥配置 | ⭐ 低 | **永久有效**，除非主动吊销/删除 AK/SK | 仅在特殊场景使用 |

> 💡 **强烈建议使用 OAuth 登录授权**：OAuth 方式使用的是临时凭证（2 小时后自动过期失效），即使凭证泄露影响也极为有限。
> 而 AK/SK 为永久凭证，一旦泄露且未及时吊销，攻击者可长期访问你的云资源，风险极高。
>
> 当用户未明确选择方式时，**默认引导使用 OAuth 登录授权**。
>
> ⛔ **你（Agent）不需要打开浏览器！** 打开浏览器、登录、查看验证码，全部是**用户自己**完成的。你只负责终端操作。
>
> ⛔ **绝对不要自行拼接 OAuth 授权链接！** 授权链接必须且只能通过 `python3 scripts/tccli-oauth-helper.py --get-url` 生成。自行拼接的 URL 会因缺少 `app_id`、`redirect_url` 错误等原因导致授权失败。

#### 方式一：OAuth 浏览器登录授权（⭐ 推荐）

> 💡 **核心思路**：使用本技能提供的 `tccli-oauth-helper.py` 辅助脚本，将授权流程分为两个非阻塞步骤：
> 1. **生成授权链接** — 执行 `--get-url`，输出链接给用户
> 2. **使用验证码登录** — 用户登录后发回验证码，执行 `--code "验证码"` 完成登录
>
> **为什么用辅助工具？** 原生的 `tccli auth login --browser no` 使用交互式 `input()` 等待用户输入验证码，在非交互式环境（如 Agent 子进程）中会因 EOF 而失败。辅助工具将验证码作为命令行参数传入，完美支持非交互式环境。

**第一步：检查当前凭证是否有效**
```bash
python3 scripts/tccli-oauth-helper.py --status
```

如果返回 `✅ 凭证有效`，说明凭证正常，可跳过授权。如果显示凭证不存在或已过期，执行以下授权流程。

也可以用 tccli 命令验证凭证是否可用：

```bash
tccli cvm DescribeRegions
```

> ⚠️ **注意**：不要使用 `tccli sts GetCallerIdentity` 验证凭证，该接口不支持 OAuth 临时凭证，会报 `InvalidParameter.AccessKeyNotSupport` 错误。

**第二步：生成授权链接**

执行辅助工具生成授权链接（此命令**不会阻塞**）：

```bash
python3 scripts/tccli-oauth-helper.py --get-url
```

输出示例：
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔐 腾讯云 OAuth 授权登录
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

请在浏览器中打开以下链接完成登录：

https://cloud.tencent.com/open/authorize?scope=login&redirect_url=...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
登录后，页面会显示一串 base64 编码的验证码。
请复制该验证码，然后运行以下命令完成登录：

  python3 tccli-oauth-helper.py --code "验证码"

或发送给 AI 助手，让它帮你完成登录。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 State: xxxxxxxxxx (10分钟内有效)
```

**第三步：展示授权链接给用户**

将上一步生成的授权链接展示给用户：

```
请在您的浏览器中打开以下链接，完成腾讯云账号登录：

👉 <完整的授权链接>

登录成功后，页面上会显示一个验证码（一串 base64 编码的字符串），请完整复制后发给我。
```

> ⚠️ **关于验证码的正确认知**：
> - ✅ 验证码是浏览器登录成功后页面上显示的一串 **base64 编码字符串**（如 `eyJhY2Nlc3NUb2tlbi...`），通常很长
> - ✅ 这个 base64 字符串是 OAuth 授权码，辅助工具会用它去换取临时密钥
> - ❌ **不是** URL 中的参数（如 `state=xxx`）
> - ❌ **不是**短数字验证码
>
> ⛔ **你不需要打开浏览器** — 浏览器操作由用户完成，和你的运行环境无关。

**第四步：使用验证码完成登录**

用户在浏览器完成登录后，会将页面上显示的 base64 验证码发给你。

收到验证码后，执行以下命令完成登录（此命令**不会阻塞**）：

```bash
python3 scripts/tccli-oauth-helper.py --code "用户发来的完整base64验证码"
```

成功输出示例：
```
🔄 正在获取临时凭证...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ OAuth 登录成功!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 配置文件: default
📌 凭证路径: /root/.tccli/default.credential
📌 过期时间: 2026-03-21 16:43:20
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

现在可以使用 tccli 了，例如：
  tccli cvm DescribeInstances --region ap-guangzhou
```

**第五步：验证授权结果**

登录成功后，执行以下命令验证：

```bash
tccli cvm DescribeRegions
```

返回地域列表即表示授权成功。

> ⚠️ **注意**：不要使用 `tccli sts GetCallerIdentity` 验证，该接口不支持 OAuth 凭证。

#### 辅助工具命令参考

| 命令 | 说明 |
|------|------|
| `python3 scripts/tccli-oauth-helper.py --get-url` | 生成 OAuth 授权链接 |
| `python3 scripts/tccli-oauth-helper.py --code "验证码"` | 使用验证码完成登录 |
| `python3 scripts/tccli-oauth-helper.py --status` | 检查当前凭证状态 |
| `python3 scripts/tccli-oauth-helper.py --status --profile myprofile` | 检查指定配置文件的凭证状态 |
| `tccli auth logout` | 退出登录，清除本地凭证 |

授权成功后凭证会保存在 `~/.tccli/default.credential`，后续命令无需重复登录。tccli 会自动刷新 OAuth 凭证，无需手动维护。

#### 退出登录

当用户需要退出当前登录、切换账号或清除本地凭证时，可使用以下命令：

```bash
tccli auth logout
```

该命令会清除本地保存的凭证信息（包括 OAuth 临时凭证和 AK/SK 配置）。

> 💡 **退出后**：需要重新执行 OAuth 登录授权或配置 AK/SK 才能继续使用 tccli。

**常见退出场景**：
- 需要切换到其他腾讯云账号
- 凭证出现异常需要重新登录
- 出于安全考虑需要清除本地凭证
- 共享设备使用完毕后清除登录状态

#### 方式二：AK/SK 密钥配置

> ⚠️ **安全提示**：AK/SK 为**永久凭证**，除非你主动在腾讯云控制台吊销或删除，否则将一直有效。一旦泄露，攻击者可持续访问你的云资源。建议优先使用上方的 OAuth 登录授权方式。

如果用户选择使用 AK/SK 方式，或**主动**提供了 SecretId 和 SecretKey，可通过 tccli 命令配置：

```bash
tccli configure set secretId <用户提供的SecretId>
tccli configure set secretKey <用户提供的SecretKey>
tccli configure set region ap-guangzhou
```

配置完成后可通过以下命令验证：

```bash
tccli cvm DescribeRegions
```

> 💡 **提示**：当用户未明确选择凭证方式时，不要主动索要 AK/SK，应优先引导使用 OAuth 登录授权。
> 如遇授权问题，建议先尝试 OAuth 方式解决。


---

## 速查表

| 任务 | 命令 |
|------|------|
| 查看 CVM 实例 | `tccli cvm DescribeInstances --region ap-beijing` |
| 查看 Lighthouse 实例 | `tccli lighthouse DescribeInstances --region ap-beijing` |
| 查看云硬盘 | `tccli cbs DescribeDisks --region ap-beijing` |
| 查看安全组 | `tccli vpc DescribeSecurityGroups --region ap-beijing` |
| 查看 VPC | `tccli vpc DescribeVpcs --region ap-beijing` |
| 查看 DNS 记录 | `tccli dnspod DescribeRecordList --Domain <domain>` |
| 查看 SSL 证书 | `tccli ssl DescribeCertificates` |
| 查看域名列表 | `tccli domain DescribeDomainNameList` |
| 查看子用户 | `tccli cam ListUsers` |
| 查看告警策略 | `tccli monitor DescribeAlarmPolicies --Module monitor` |
| 查看可用地域 | `tccli cvm DescribeRegions` |
| 查看所有服务 | `tccli --help` |
| 查看操作参数 | `tccli <服务> <操作> --help` |
| 退出登录 | `tccli auth logout` |

---

## 场景决策

用户想做什么？
```
├─ 查询/了解资源状态 → 使用上方速查表中的命令
├─ 退出登录/切换账号/清除凭证 → tccli auth logout
├─ 安全检查/安全审计/安全巡检 → 读取 references/cvm-security-check.md
├─ 资源巡检/域名到期/证书检查 → 读取 references/auto-check-resource.md
├─ 服务健康度巡检/诊断服务/监控指标异常排查/性能诊断 → 读取 references/cloud-service-healthcheck.md（⚠️ 深度监控诊断，含 CPU/内存/磁盘/连接数等指标分析和健康度评分）
├─ 建站/搭网站/WordPress/宝塔/购买域名 → 读取 references/lighthouse-website-setup.md
├─ 部署应用(Go/Node/Python/Docker) → 读取 references/lighthouse-app-deploy.md
├─ 部署 OpenClaw/clawdbot → 读取 references/lighthouse-openclaw-setup.md
├─ 购买/挂载/扩容云硬盘 → 读取 references/cbs-bindto-cvm.md
└─ 其他云资源操作 → tccli <服务> --help 探索
```

当用户请求涉及以上场景时，**必须先读取对应的参考文档**，然后严格按照文档中的指引执行。

---

## 端到端示例：查询并管理 CVM 实例

```bash
# 1. 查看北京地区所有 CVM 实例
tccli cvm DescribeInstances --region ap-beijing

# 2. 按名称过滤特定实例
tccli cvm DescribeInstances --region ap-beijing \
  --Filters '[{"Name":"instance-name","Values":["my-server"]}]'

# 3. 查看该实例关联的安全组规则
tccli vpc DescribeSecurityGroupPolicies --region ap-beijing \
  --SecurityGroupId <sg-id>

# 4. 查看该实例的监控数据（CPU 使用率）
tccli monitor GetMonitorData --region ap-beijing \
  --Namespace QCE/CVM \
  --MetricName CpuUsage \
  --Instances '[{"Dimensions":[{"Name":"InstanceId","Value":"<instance-id>"}]}]' \
  --Period 300 \
  --StartTime "2026-03-24T00:00:00+08:00" \
  --EndTime "2026-03-24T12:00:00+08:00"
```

---

## 写操作和高危操作

### 操作分级

| 风险等级 | 操作类型 | 确认要求 |
|---------|---------|---------|
| ❌ 高危 | 删除实例/云硬盘/VPC/DNS/数据库、修改安全组入站规则 | **二次确认**，明确写出不可撤销性 |
| ⚠️ 中危 | 创建/修改资源、启动/停止实例、修改 DNS、续费 | 单次确认 |
| ✅ 低危 | 查询、列表、获取帮助 | 无需确认，直接执行 |

### 确认流程

1. 清楚说明将要执行的操作
2. 说明影响范围和后果
3. 等待用户明确输入"确认"或"是"
4. 收到确认后才执行

直接执行高危操作会导致 **数据永久丢失**、**服务不可恢复中断**、**计费资源无法找回**。

### 示例

```
用户：删除实例 i-xxxxx
Agent：
⚠️ 警告：即将删除实例 i-xxxxx
- 实例名称：test-server
- 地域：ap-beijing
- 状态：运行中

此操作 **不可撤销**，实例及其数据将 **永久丢失**。
请输入"确认"继续，或"取消"放弃。
```

---

## 反模式与常见错误

### 自行拼接 OAuth 授权链接

授权链接包含 `app_id`、`redirect_url`、`state` 等关键参数，拼接错误会导致授权失败。

**Check**: 必须通过辅助脚本生成授权链接，不要自行拼接。

```bash
# ✅ 正确：用辅助脚本生成
python3 scripts/tccli-oauth-helper.py --get-url
```

```bash
# ❌ 错误：自行拼接 URL——会缺少 app_id 或 redirect_url 错误
# https://cloud.tencent.com/open/authorize?scope=login&redirect_url=...
```

### 用 CVM 命令操作 Lighthouse（或反过来）

Lighthouse 和 CVM 是**完全独立的产品**，API 互不相通。

**Check**: 不要用 `tccli cvm` 命令操作 Lighthouse 实例，反之亦然。

```bash
# ✅ 正确：查询 Lighthouse 用 lighthouse 服务
tccli lighthouse DescribeInstances --region ap-beijing
```

```bash
# ❌ 错误：用 cvm 服务查询 Lighthouse 实例——查不到
tccli cvm DescribeInstances --region ap-beijing
```

### 使用占位符假装执行成功

**Check**: 用户未提供 SecretId/SecretKey/InstanceId 等关键参数时，不使用占位符执行命令。

```bash
# ✅ 正确：向用户索取缺失参数
# "请提供目标实例的 InstanceId，可通过 tccli cvm DescribeInstances 查询"
```

```bash
# ❌ 错误：用占位符直接执行
tccli cvm StopInstances --InstanceIds '["<instance-id>"]'
# 这会导致 API 报错或操作错误的实例
```

### 跳过 --help 直接猜参数

**Check**: 对不确定的参数，先用 `--help` 确认。

```bash
# ✅ 正确：先查参数再执行
tccli lighthouse CreateInstances --help
```

```bash
# ❌ 错误：凭记忆拼参数——可能参数名已变更或格式不对
tccli lighthouse CreateInstances --BundleId xxx --ImageId yyy
# Lighthouse 用 BlueprintId 不是 ImageId
```

### 不区分查询和写操作

**Check**: 能先 `Describe` 的，不直接 `Create` / `Modify` / `Delete`。

```bash
# ✅ 正确：先查再改
tccli cbs DescribeDisks --region ap-beijing --DiskIds '["disk-xxx"]'
# 确认状态后再执行操作
```

```bash
# ❌ 错误：直接删除，不先查看当前状态
tccli cbs TerminateDisks --DiskIds '["disk-xxx"]'
# 可能删错盘，导致 **数据永久丢失**
```

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 如何查看操作历史？ | 启用云审计 `tccli cloudaudit LookUpEvents` |
| 如何查询特定标签的资源？ | `--Filters '[{"Name":"tag:Environment","Values":["production"]}]'` |
| 命令执行失败？ | 检查凭证有效性、地域是否正确、用 `--help` 确认参数 |
| 如何退出登录/切换账号？ | `tccli auth logout`，然后重新登录 |
| 如何查看可用地域？ | `tccli cvm DescribeRegions` |
| 如何批量操作？ | 使用 `--Filters` 过滤 + 循环遍历结果 |

---

## 关键词

Search: `DescribeInstances`, `DescribeSecurityGroups`, `DescribeSecurityGroupPolicies`,
`CreateInstances`, `DescribeBlueprints`, `DescribeBundles`, `CreateRecord`,
`DescribeRecordList`, `DescribeCertificates`, `DescribeDomainNameList`,
`RunCommand`, `AttachDisks`, `CreateDisks`, `DescribeDisks`,
`DescribeAlarmPolicies`, `ListUsers`, `ListAttachedUserAllPolicies`,
`tccli`, `Lighthouse`, `CVM`, `CBS`, `DNSPod`, `SSL`, `CAM`, `TAT`,
`openclaw`, `clawdbot`, `安全检查`, `安全巡检`, `资源巡检`, `建站`, `部署应用`,
`退出登录`, `logout`, `切换账号`, `清除凭证`

---

## Reference 文件

- [云服务器安全检查](references/cvm-security-check.md) — 安全组、公网暴露、登录方式、镜像、监控、CAM 权限
- [云资源巡检和监控](references/auto-check-resource.md) — 域名到期、SSL 证书、实例状态、云硬盘状态
- [云服务健康度诊断](references/cloud-service-healthcheck.md) — 服务级深度健康度诊断，含监控指标分析、健康度评分、巡检报告
- [使用 Lighthouse 建站指南](references/lighthouse-website-setup.md) — WordPress/宝塔 + 域名注册 + DNS
- [Lighthouse 应用部署指引](references/lighthouse-app-deploy.md) — Go/Node/Python/Docker 部署
- [在 Lighthouse 上部署 OpenClaw](references/lighthouse-openclaw-setup.md) — OpenClaw/clawdbot 实例部署
- [购买云硬盘并挂载到云服务器](references/cbs-bindto-cvm.md) — CBS 创建、挂载、分区、快照

---

**版本**：v1.2.0
**最后更新**：2026-03-27
