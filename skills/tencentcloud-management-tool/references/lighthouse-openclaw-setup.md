# 在腾讯云 Lighthouse 上部署 OpenClaw（clawdbot 镜像）

你对腾讯云 Lighthouse 实例创建、镜像查询、密码重置相关 API 的参数可能已过时。
**执行前请先用 `tccli lighthouse <操作> --help` 确认最新参数。**

> 通过 tccli 命令行在腾讯云轻量应用服务器（Lighthouse）上创建 OpenClaw 实例的完整流程。

---

## 前置条件

### 1. 安装 tccli

```bash
python3 -m pip install tccli
```

### 2. 配置腾讯云凭证

前往 [腾讯云 API 密钥控制台](https://console.cloud.tencent.com/cam/capi) 获取 SecretId 和 SecretKey。

```bash
tccli configure set secretId <SecretId>
tccli configure set secretKey <SecretKey>
tccli configure set region <region>
tccli configure set output json
```

验证凭证：

```bash
tccli sts GetCallerIdentity
```

---

## 第一步：查询 OpenClaw 镜像

```bash
tccli lighthouse DescribeBlueprints --region <region>
```

通过 python/jq 过滤包含 `openclaw`、`claw`、`clawdbot` 等关键词的镜像，获取 BlueprintId。

---

## 第二步：查询套餐

```bash
tccli lighthouse DescribeBundles --region <region>
```

按需筛选 CPU/内存规格（如 4c8g），获取 BundleId。

---

## 第三步：创建实例

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

> ⚠️ `--InstanceChargePrepaid` 为必填参数，缺少会直接报错。

---

## 第四步：等待实例就绪

轮询实例状态，直到变为 `RUNNING` 并获得公网 IP（通常约 30–60 秒）：

```bash
tccli lighthouse DescribeInstances \
  --region <region> \
  --InstanceIds '["<instance-id>"]'
```

状态流转：`PENDING` → `RUNNING`

---

## 第五步：设置 root 密码

`AutoGeneratePassword` 模式下无法直接获取初始密码，需主动设置：

```bash
tccli lighthouse ResetInstancesPassword \
  --region <region> \
  --InstanceIds '["<instance-id>"]' \
  --Password '<password>' \
  --UserName 'root'
```

---

## SSH 登录

```bash
ssh root@<ip>
```

> 💡 首次登录后建议立即修改 root 密码：`passwd root`

---

## 常用运维命令

```bash
# 查看实例状态
tccli lighthouse DescribeInstances --region <region> --InstanceIds '["<instance-id>"]'

# 重启
tccli lighthouse RebootInstances --region <region> --InstanceIds '["<instance-id>"]'

# 关机
tccli lighthouse StopInstances --region <region> --InstanceIds '["<instance-id>"]'

# 开机
tccli lighthouse StartInstances --region <region> --InstanceIds '["<instance-id>"]'

# 查看防火墙规则
tccli lighthouse DescribeFirewallRules --region <region> --InstanceId "<instance-id>"

# 续费
tccli lighthouse RenewInstances --region <region> --InstanceIds '["<instance-id>"]' \
  --InstanceChargePrepaid '{"Period":<months>,"RenewFlag":"NOTIFY_AND_MANUAL_RENEW"}'
```

---

## 注意事项

1. **凭证安全**：SecretKey 不要出现在日志或代码注释中，建议使用 `tencent-cloud-tools` 的 keystore 加密存储
2. **高危操作**：Stop/Terminate 等操作建议先用 `--dry-run` 预演
3. **密码修改**：首次 SSH 登录后立即修改 root 密码
4. **续费提醒**：注意实例到期时间，提前续费或设置自动续费

---

## 何时使用

| 场景 | 建议 |
|------|------|
| 用户要部署 OpenClaw / clawdbot | 按本文档完整流程执行 |
| 用户要在 Lighthouse 上部署其他应用 | 不使用本文档，用 references/lighthouse-app-deploy.md |
| 用户要建站（WordPress/宝塔） | 不使用本文档，用 references/lighthouse-website-setup.md |
| 用户要管理已有 Lighthouse 实例 | 参考本文档"常用运维命令"部分 |
| 用户要挂载云硬盘到实例 | 不使用本文档，用 references/cbs-bindto-cvm.md |
