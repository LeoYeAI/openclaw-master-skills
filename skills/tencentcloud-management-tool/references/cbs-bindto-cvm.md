# 购买云硬盘（CBS）并挂载到云服务器

你对腾讯云 CBS、CVM 挂载、TAT 远程执行相关 API 的参数可能已过时。
**执行前请先用 `tccli <服务> <操作> --help` 确认最新参数。**

> 适用场景：为已有的 CVM 云服务器或 Lighthouse 轻量应用服务器购买新的云硬盘（CBS），并完成挂载、分区、格式化及自动挂载配置。
> 全程通过 tccli 命令行完成，无需登录控制台。

---

## 前置条件

### 所需权限

| 权限 | 说明 |
|------|------|
| `QcloudCBSFullAccess` | 创建/管理云硬盘 |
| `QcloudCVMFullAccess` | 管理云服务器（CVM 场景） |
| `QcloudLighthouseFullAccess` | 管理轻量应用服务器（Lighthouse 场景） |
| `QcloudTATFullAccess` | TAT 自动化助手（远程执行磁盘初始化命令） |

> 子账号需在 CAM 控制台授予以上策略。

### 关键约束

- **可用区一致**：云硬盘必须与目标云服务器在**同一可用区**（如都在 `ap-beijing-3`），否则无法挂载
- **挂载上限**：每台 CVM 最多挂载 20 块云硬盘；Lighthouse 最多挂载 5 块云硬盘
- **计费方式**：需确认云硬盘的计费方式与实例是否匹配（包年包月/按量计费）

---

## 场景一：为 CVM 云服务器购买并挂载云硬盘

### 任务描述

为一台已有的 CVM 云服务器购买一块新的云硬盘（CBS），并将其挂载到该服务器上。

### 执行步骤

#### 步骤 1：查询目标 CVM 实例信息

首先确认目标实例的可用区、当前挂载的云硬盘数量等信息：

```bash
tccli cvm DescribeInstances --region <region> --InstanceIds '["<instance-id>"]'
```

关注以下字段：
- `Placement.Zone`：实例所在可用区（后续创建云硬盘必须指定相同可用区）
- `InstanceId`：实例 ID
- `InstanceName`：实例名称
- `InstanceState`：实例状态（应为 `RUNNING` 或 `STOPPED`）
- `DataDisks`：当前已挂载的数据盘列表

> ⚠️ 如果用户只提供了实例名称而非 ID，需使用 Filters 按名称查询：
> ```bash
> tccli cvm DescribeInstances --region <region> --Filters '[{"Name":"instance-name","Values":["<name>"]}]'
> ```

#### 步骤 2：查询云硬盘可用类型和价格

```bash
# 查询指定可用区支持的云硬盘类型
tccli cbs DescribeDiskConfigQuota --region <region> --InquiryType INQUIRY_CBS_CONFIG --DiskZones '["<zone>"]'
```

常见云硬盘类型：
| 类型 | DiskType | 说明 |
|------|----------|------|
| 高性能云硬盘 | `CLOUD_PREMIUM` | 适用于大部分 I/O 场景 |
| SSD 云硬盘 | `CLOUD_SSD` | 适用于中小型数据库 |
| 增强型 SSD 云硬盘 | `CLOUD_HSSD` | 适用于高性能数据库和核心业务 |
| 极速型 SSD 云硬盘 | `CLOUD_TSSD` | 适用于大型数据库和高 IOPS 场景 |

可选：查询云硬盘价格：

```bash
tccli cbs InquirePriceCreateDisks --region <region> \
  --DiskType "<disk-type>" \
  --DiskSize <size-in-gb> \
  --DiskCount 1 \
  --DiskChargeType "PREPAID" \
  --DiskChargePrepaid '{"Period":<months>,"RenewFlag":"NOTIFY_AND_MANUAL_RENEW"}'
```

#### 步骤 3：创建云硬盘

**包年包月云硬盘**（适配包年包月实例）：

```bash
tccli cbs CreateDisks --region <region> \
  --DiskType "<disk-type>" \
  --DiskSize <size-in-gb> \
  --DiskCount 1 \
  --DiskName "<disk-name>" \
  --DiskChargeType "PREPAID" \
  --DiskChargePrepaid '{"Period":<months>,"RenewFlag":"NOTIFY_AND_MANUAL_RENEW"}' \
  --Placement '{"Zone":"<zone>"}'
```

**按量计费云硬盘**（适配按量计费实例）：

```bash
tccli cbs CreateDisks --region <region> \
  --DiskType "<disk-type>" \
  --DiskSize <size-in-gb> \
  --DiskCount 1 \
  --DiskName "<disk-name>" \
  --DiskChargeType "POSTPAID_BY_HOUR" \
  --Placement '{"Zone":"<zone>"}'
```

> ⚠️ 创建云硬盘属于**中危操作**，执行前需向用户确认：
> - 云硬盘类型和大小
> - 计费方式和费用
> - 目标可用区

记录返回的 `DiskId`。

#### 步骤 4：等待云硬盘就绪

```bash
tccli cbs DescribeDisks --region <region> --DiskIds '["<disk-id>"]'
```

状态流转：`CREATING` → `UNATTACHED`（约 10–30 秒）

`DiskState` 变为 `UNATTACHED` 后方可进行挂载操作。

#### 步骤 5：挂载云硬盘到 CVM

```bash
tccli cbs AttachDisks --region <region> \
  --DiskIds '["<disk-id>"]' \
  --InstanceId "<instance-id>"
```

> ⚠️ 实例必须处于 `RUNNING` 或 `STOPPED` 状态才能挂载。

#### 步骤 6：确认挂载成功

```bash
tccli cbs DescribeDisks --region <region> --DiskIds '["<disk-id>"]'
```

确认以下字段：
- `DiskState`：应变为 `ATTACHED`
- `InstanceId`：应为目标实例 ID
- `Attached`：应为 `true`

#### 步骤 7：在实例内初始化磁盘（通过 TAT 远程执行）

挂载成功后，云硬盘在操作系统中表现为一块未格式化的裸盘，需要分区、格式化并挂载到文件系统。

**7a. 查看新磁盘设备名**

```bash
# 通过 TAT 执行命令
tccli tat RunCommand --region <region> \
  --InstanceIds '["<instance-id>"]' \
  --Content "$(echo 'lsblk' | base64)" \
  --CommandType "SHELL" \
  --Username "root" \
  --Timeout 30
```

等待几秒后查询执行结果：

```bash
tccli tat DescribeInvocationTasks --region <region> \
  --Filters '[{"Name":"invocation-id","Values":["<invocation-id>"]}]'
```

> 返回结果中的 `Output` 字段为 Base64 编码，需解码查看。新磁盘通常显示为 `vdb`（或 `vdc`、`vdd` 等，取决于已有磁盘数量），无分区和挂载点。

**7b. 分区、格式化并挂载**

```bash
# 通过 TAT 执行一键初始化脚本
tccli tat RunCommand --region <region> \
  --InstanceIds '["<instance-id>"]' \
  --Content "$(echo 'DISK=/dev/vdb
MOUNT_POINT=/data

# 创建分区
parted -s ${DISK} mklabel gpt
parted -s ${DISK} mkpart primary ext4 0% 100%
partprobe ${DISK}
sleep 2

# 格式化
mkfs.ext4 ${DISK}1

# 创建挂载点并挂载
mkdir -p ${MOUNT_POINT}
mount ${DISK}1 ${MOUNT_POINT}

# 配置开机自动挂载（使用 UUID，更可靠）
UUID=$(blkid -s UUID -o value ${DISK}1)
echo "UUID=${UUID} ${MOUNT_POINT} ext4 defaults 0 2" >> /etc/fstab

# 验证
df -h ${MOUNT_POINT}
cat /etc/fstab | grep ${MOUNT_POINT}' | base64)" \
  --CommandType "SHELL" \
  --Username "root" \
  --Timeout 60
```

> ⚠️ **重要提示**：
> - `DISK` 变量需替换为步骤 7a 中确认的实际设备名（如 `/dev/vdb`）
> - `MOUNT_POINT` 可按用户需求自定义（常见：`/data`、`/mnt/data`）
> - 如果是 CentOS 8+ / Ubuntu 20+，推荐使用 `xfs` 文件系统替代 `ext4`
> - 此操作会**清除磁盘上的所有数据**，仅用于全新云硬盘

#### 步骤 8：验证最终状态

```bash
# 通过 TAT 查看磁盘使用情况
tccli tat RunCommand --region <region> \
  --InstanceIds '["<instance-id>"]' \
  --Content "$(echo 'df -Th && echo "---" && lsblk && echo "---" && cat /etc/fstab' | base64)" \
  --CommandType "SHELL" \
  --Username "root" \
  --Timeout 30
```

确认：
- 新分区已挂载到指定目录
- 文件系统类型正确
- `/etc/fstab` 中已添加自动挂载配置

---

## 场景二：为 Lighthouse 轻量应用服务器购买并挂载云硬盘

### 任务描述

为一台已有的 Lighthouse 轻量应用服务器购买一块新的云硬盘，并完成挂载。

### 执行步骤

#### 步骤 1：查询目标 Lighthouse 实例信息

```bash
tccli lighthouse DescribeInstances --region <region> --InstanceIds '["<instance-id>"]'
```

关注以下字段：
- `Zone`：实例所在可用区
- `InstanceId`：实例 ID
- `InstanceName`：实例名称
- `InstanceState`：实例状态（应为 `RUNNING`）

#### 步骤 2：查询当前已挂载的云硬盘

```bash
tccli lighthouse DescribeDisks --region <region> \
  --Filters '[{"Name":"instance-id","Values":["<instance-id>"]}]'
```

> Lighthouse 单实例最多挂载 **5** 块数据盘，需确认未超出限制。

#### 步骤 3：查询可用的云硬盘配置

```bash
# 查询 Lighthouse 云硬盘套餐
tccli lighthouse DescribeDiskConfigs --region <region>
```

> 注意：Lighthouse 的云硬盘创建接口与 CVM 不同，使用 Lighthouse 专用接口。

#### 步骤 4：创建 Lighthouse 云硬盘

```bash
tccli lighthouse CreateDisks --region <region> \
  --Zone "<zone>" \
  --DiskSize <size-in-gb> \
  --DiskType "<disk-type>" \
  --DiskChargePrepaid '{"Period":<months>,"RenewFlag":"NOTIFY_AND_MANUAL_RENEW"}' \
  --DiskCount 1 \
  --DiskName "<disk-name>"
```

> ⚠️ Lighthouse 云硬盘仅支持**包年包月**计费方式。

记录返回的 `DiskId`。

#### 步骤 5：等待云硬盘就绪

```bash
tccli lighthouse DescribeDisks --region <region> \
  --DiskIds '["<disk-id>"]'
```

状态流转：`CREATING` → `UNATTACHED`

#### 步骤 6：挂载云硬盘到 Lighthouse 实例

```bash
tccli lighthouse AttachDisks --region <region> \
  --DiskIds '["<disk-id>"]' \
  --InstanceId "<instance-id>"
```

#### 步骤 7：确认挂载成功

```bash
tccli lighthouse DescribeDisks --region <region> --DiskIds '["<disk-id>"]'
```

确认 `DiskState` 变为 `ATTACHED`，`InstanceId` 为目标实例。

#### 步骤 8：在实例内初始化磁盘（通过 TAT 远程执行）

Lighthouse 同样支持 TAT 自动化助手，初始化步骤与 CVM 场景一致：

```bash
# 查看新磁盘设备名
tccli tat RunCommand --region <region> \
  --InstanceIds '["<instance-id>"]' \
  --Content "$(echo 'lsblk' | base64)" \
  --CommandType "SHELL" \
  --Username "root" \
  --Timeout 30
```

然后按照场景一步骤 7b 执行分区、格式化和挂载操作。

---

## 场景三：为云硬盘创建定期快照策略

### 任务描述

为新挂载的云硬盘配置定期快照策略，保障数据安全。

### 执行步骤

#### 步骤 1：创建定期快照策略

```bash
tccli cbs CreateAutoSnapshotPolicy --region <region> \
  --Policy '[{"DayOfWeek":[0,3],"Hour":[2]}]' \
  --AutoSnapshotPolicyName "<policy-name>" \
  --IsActivated true \
  --RetentionDays 7
```

> 上例表示每周日和周三凌晨 2 点自动创建快照，保留 7 天。

记录返回的 `AutoSnapshotPolicyId`。

#### 步骤 2：将云硬盘绑定到快照策略

```bash
tccli cbs BindAutoSnapshotPolicy --region <region> \
  --AutoSnapshotPolicyId "<policy-id>" \
  --DiskIds '["<disk-id>"]'
```

#### 步骤 3：验证绑定结果

```bash
tccli cbs DescribeAutoSnapshotPolicies --region <region> \
  --AutoSnapshotPolicyIds '["<policy-id>"]'
```

确认 `DiskIdSet` 中包含目标云硬盘 ID。

---

## 常见问题

| 问题 | 原因与解决 |
|------|-----------|
| 创建云硬盘报错"可用区不支持" | 确认使用的 `DiskType` 在目标可用区可用，用 `DescribeDiskConfigQuota` 查询 |
| 挂载报错"可用区不一致" | 云硬盘和实例必须在同一可用区，无法跨可用区挂载 |
| 挂载后系统中看不到新磁盘 | Linux 执行 `lsblk` 或 `fdisk -l` 查看；Windows 在「磁盘管理」中初始化 |
| 分区后 `df -h` 看不到 | 需要先 `mount` 挂载到目录才能在 `df` 中显示 |
| 重启后磁盘未自动挂载 | 检查 `/etc/fstab` 配置是否正确，建议使用 UUID 而非设备名 |
| Lighthouse 创建云硬盘报错 | Lighthouse 使用专用接口 `lighthouse CreateDisks`，不能用 CBS 的 `CreateDisks` |
| 挂载数量超限 | CVM 最多 20 块，Lighthouse 最多 5 块，需先卸载不用的盘 |

---

## API 速查

### CBS（云硬盘 - 适用于 CVM）

| 功能 | 服务 | 接口 |
|------|------|------|
| 查询云硬盘 | cbs | `DescribeDisks` |
| 查询云硬盘配置 | cbs | `DescribeDiskConfigQuota` |
| 查询价格 | cbs | `InquirePriceCreateDisks` |
| 创建云硬盘 | cbs | `CreateDisks` |
| 挂载云硬盘 | cbs | `AttachDisks` |
| 卸载云硬盘 | cbs | `DetachDisks` |
| 创建快照 | cbs | `CreateSnapshot` |
| 创建定期快照策略 | cbs | `CreateAutoSnapshotPolicy` |
| 绑定快照策略 | cbs | `BindAutoSnapshotPolicy` |
| 查询快照策略 | cbs | `DescribeAutoSnapshotPolicies` |
| 扩容云硬盘 | cbs | `ResizeDisk` |
| 退还云硬盘 | cbs | `TerminateDisks` |

### Lighthouse（轻量应用服务器云硬盘）

| 功能 | 服务 | 接口 |
|------|------|------|
| 查询云硬盘 | lighthouse | `DescribeDisks` |
| 查询云硬盘配置 | lighthouse | `DescribeDiskConfigs` |
| 创建云硬盘 | lighthouse | `CreateDisks` |
| 挂载云硬盘 | lighthouse | `AttachDisks` |
| 卸载云硬盘 | lighthouse | `DetachDisks` |
| 续费云硬盘 | lighthouse | `RenewDisks` |
| 退还云硬盘 | lighthouse | `TerminateDisks` |

### 通用

| 功能 | 服务 | 接口 |
|------|------|------|
| 查询 CVM 实例 | cvm | `DescribeInstances` |
| 查询 Lighthouse 实例 | lighthouse | `DescribeInstances` |
| 远程执行命令 | tat | `RunCommand` |
| 查询执行结果 | tat | `DescribeInvocationTasks` |

---

## 何时使用

| 场景 | 建议 |
|------|------|
| 用户要购买/创建/挂载云硬盘 | 按本文档场景一或场景二执行 |
| 用户要配置定期快照 | 参考本文档场景三 |
| 用户只查看云硬盘状态 | 不使用本文档，用 `tccli cbs DescribeDisks` |
| 用户要做安全检查 | 不使用本文档，用 references/cvm-security-check.md |
| 用户要部署应用或建站 | 不使用本文档，用对应的部署/建站 reference |
