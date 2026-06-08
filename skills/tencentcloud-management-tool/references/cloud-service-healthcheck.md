# 云服务健康度诊断

你对腾讯云监控指标、标签 API 的参数可能已过时。
**执行前请先用 `tccli <服务> <操作> --help` 确认最新参数。**

> 对用户的云服务进行**深度健康度诊断**，通过监控指标（CPU/内存/磁盘/连接数/延迟等）分析服务性能，输出健康度评分和完整巡检报告。
> **全程只读操作，不执行任何变更。默认不做全量扫描，需用户明确巡检范围（用户明确要求全量巡检除外）。**

### ⚠️ 与「资源状态巡检」的区别

| auto-check-resource.md（资源状态巡检） | 本文档（服务健康度诊断） |
|---------------------------------------|------------------------|
| 检查域名/证书是否到期、实例是否运行 | 深度诊断 CPU/内存/磁盘/连接数/延迟等监控指标 |
| 无评分体系，仅输出状态列表 | 有健康度评分（0-100）和完整巡检报告 |
| 直接按场景执行 | 必须先让用户选择巡检方式（方式一/二/三） |

**如果用户要求的是：**
- 「域名到期」「证书过期」「实例是否在运行」「资源状态」→ ⛔ **不使用本文档**，请使用 `auto-check-resource.md`
- 「服务巡检」「健康度检查」「诊断服务」「性能检查」「监控指标」→ ✅ **使用本文档**

---

## 执行规则

### 🔒 安全红线（全局强制）

> ⛔ **绝对禁止任何写操作**。整个巡检流程**只允许读取/查询操作**（Describe*、Get*），
> **严禁执行任何创建、修改、删除、重启、停止等写入类操作**（Create*、Modify*、Delete*、Start*、Stop*、Reboot*、Reset* 等）。
> 巡检的目的是诊断和发现问题，修复建议仅以文字形式提出，**不得代替用户执行**。

> ⛔ **默认禁止全量巡检**。不得在未经用户明确指定巡检范围的情况下，自动扫描账户下所有资源。
> 巡检范围必须由用户通过「方式一（标签发现）」或「方式二（手动指定）」明确确定。
> **例外**：当用户明确要求全量巡检（如"帮我巡检所有资源"、"全量扫描"、"检查账户下所有实例"）时，
> 可执行全量巡检，走「方式三（全量扫描）」流程。

### 完整巡检（触发词：帮我巡检服务、检查服务健康度、服务巡检、诊断服务状态、云服务健康检查、服务是否正常）

当用户请求服务巡检时，**必须严格遵守以下规则**：

1. **先确定巡检方式**：必须让用户明确选择使用「方式一（标签发现）」、「方式二（手动指定）」或「方式三（全量扫描）」，**不得跳过此步骤，不得自行决定**
2. **先确定巡检范围**：通过 Phase 0 明确要巡检的资源列表，不得跳过
3. **按顺序执行全部阶段**：Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4
4. **空结果也要执行**：某类资源未发现时，在报告中标注"未发现该类型资源"
5. **生成完整报告**：所有阶段执行完毕后，必须按本文档末尾的「巡检报告模板」输出完整报告
6. **状态标注**：对每个检查项明确标注状态（✅ 正常 / ⚠️ 警告 / ❌ 异常）
7. **只读操作**：全程只使用 Describe* / Get* 等查询类 API，绝不执行任何变更操作

### 单项检查

当用户仅请求某个特定检查（如"检查 Redis 健康度"、"看下数据库状态"），可只对指定资源类型执行 Phase 1 + Phase 2，无需执行全部阶段。但仍需用户提供明确的资源 ID，不得自行扫描全量资源。

---

## Phase 0: 确定巡检范围

### 步骤 1: 确定地域

询问用户目标地域。如果用户未指定，默认使用 `ap-guangzhou`，并告知用户。

### 步骤 2: 让用户选择资源关联方式

有三种方式确定巡检范围。**必须向用户展示可选方式并让用户明确选择**，不得自动跳过或替用户决定：

```
请选择巡检的资源关联方式：

方式一（标签发现）：通过腾讯云标签（Tag）自动发现与某个服务关联的所有资源。
  适用于：已为云资源打上了统一的服务标签（如 Service=order-system）。

方式二（手动指定）：由您手动提供要巡检的资源类型和实例 ID。
  适用于：未配置标签，或只想巡检特定的几个资源。

方式三（全量扫描）：扫描当前地域下所有已知类型的云资源并逐一巡检。
  ⚠️ 资源数量较多时耗时较长，仅在您确认需要全量检查时使用。

请输入 1、2 或 3 选择方式：
```

> ⛔ **禁止在用户未明确选择方式的情况下开始巡检。**
> 如果用户的请求中没有包含标签信息也没有包含资源 ID、也没有明确要求全量，必须先向用户展示上述选择提示。
> 如果用户的请求中已经包含了标签信息（如"巡检 Service=xxx 的资源"），可视为已选择方式一。
> 如果用户的请求中已经包含了具体资源 ID（如"巡检 ins-xxx 和 cdb-xxx"），可视为已选择方式二。
> 如果用户的请求中明确要求全量（如"帮我巡检所有资源"、"全量扫描"、"检查所有实例"），可视为已选择方式三。

#### 方式一：基于标签（Tag）自动发现（⭐ 推荐）

用户通过统一标签将同一业务的不同云资源关联在一起。约定标签键如 `Service`，值为业务名如 `order-system`。

**操作步骤**：

1. 先询问用户服务名称或标签信息
2. 如果用户不确定有哪些标签，先查询现有标签：

```bash
# 查询账户下所有标签键
tccli tag DescribeTagKeys --region ap-guangzhou

# 查询某个标签键下的所有标签值
tccli tag DescribeTagValues --TagKeys '["Service"]' --region ap-guangzhou
```

3. 通过标签查询关联的所有资源：

```bash
tccli tag DescribeResourcesByTags --TagFilters '[{"TagKey":"Service","TagValue":["order-system"]}]' --region ap-guangzhou
```

4. 从返回结果中按 `ServiceType` 字段分类汇总资源。**不限于特定资源类型**，所有被标签关联的资源均纳入巡检范围。

已知资源类型映射（有精细化诊断方案）：

| ServiceType | 产品名称 | Monitor Namespace | Dimension Key |
|-------------|---------|-------------------|---------------|
| `cvm` | CVM 云服务器 | `QCE/CVM` | `InstanceId` |
| `cdb` | CDB MySQL | `QCE/CDB` | `InstanceId` |
| `redis` | Redis 缓存 | `QCE/REDIS_MEM` | `instanceid`（小写） |
| `ckafka` | CKafka 消息队列 | `QCE/CKAFKA` | `instanceId` |
| `lighthouse` | 轻量应用服务器 | `QCE/LIGHTHOUSE` | `InstanceId` |
| `cynosdb` | TDSQL-C MySQL | `QCE/CYNOSDB_MYSQL` | `InstanceId` |
| `mariadb` | MariaDB | `QCE/MARIADB` | `InstanceId` |
| `postgres` | PostgreSQL | `QCE/POSTGRES` | `resourceId` |
| `mongodb` | MongoDB | `QCE/CMONGO` | `target` |
| `clb` | 负载均衡 | `QCE/LB_PUBLIC` / `QCE/LB_PRIVATE` | `vip` |
| `nat` | NAT 网关 | `QCE/NAT_GATEWAY` | `natId` |
| `es` | Elasticsearch | `QCE/CES` | `uInstanceId` |

**如果遇到上表未列出的 ServiceType**，该资源归为「未知类型」，走通用诊断流程（见 Phase 1 和 Phase 2 的通用诊断部分）。

> ⚠️ **注意**：如果标签查询未返回任何资源，说明用户可能未配置标签，应引导用户使用方式二。

#### 方式二：用户手动指定资源 ID

当用户未配置标签或标签查询无结果时，引导用户手动提供资源列表：

```
请告诉我您要巡检的服务包含哪些云资源？
请提供资源类型和实例 ID，例如：
- CVM: ins-xxxx
- CDB: cdb-xxxx
- Redis: crs-xxxx
- CKafka: ckafka-xxxx
- CLB: lb-xxxx
- MongoDB: cmgo-xxxx
- 其他资源: 请说明产品类型和实例 ID

也可以直接提供 tccli 服务名和实例 ID 的组合，如 "postgres pg-xxxx"。
```

> 💡 Agent 收到用户提供的资源信息后，应根据实例 ID 前缀或用户说明，自动识别资源类型并映射到对应的 tccli 服务名。如果无法识别，向用户确认产品类型。

#### 方式三：全量扫描（仅限用户明确要求）

> ⚠️ 此方式**仅在用户主动明确要求全量巡检时使用**（如"帮我巡检所有资源"、"全量扫描"、"检查所有实例"）。
> Agent 不得主动建议或自动触发此方式。

**操作步骤**：

1. 向用户确认地域和要扫描的产品类型范围：

```
您要求全量扫描，请确认：
- 地域：ap-guangzhou（如需其他地域请说明）
- 扫描范围：默认扫描以下产品类型的所有实例：
  CVM、CDB、Redis、CKafka、Lighthouse、CLB、MongoDB、PostgreSQL、MariaDB、TDSQL-C、NAT 网关、Elasticsearch
- 如需增减产品类型，请说明

确认后开始扫描。
```

2. 用户确认后，逐一查询各产品的实例列表：

```bash
# 按产品类型逐一查询（仅 Describe 查询，只读操作）
tccli cvm DescribeInstances --region ap-guangzhou
tccli cdb DescribeDBInstances --region ap-guangzhou
tccli redis DescribeInstances --region ap-guangzhou
tccli ckafka DescribeInstances --region ap-guangzhou
tccli lighthouse DescribeInstances --region ap-guangzhou
# ... 其他产品类似
```

3. 汇总所有发现的实例，构建资源清单后进入步骤 3。

> 💡 全量扫描可能涉及大量资源和 API 调用，如资源数量过多（超过 50 个），建议分批巡检或缩小范围。

### 步骤 3: 构建资源清单

无论使用哪种方式，最终构建出一份资源清单表格展示给用户确认：

```
已发现以下资源，即将开始巡检：

| 序号 | 资源类型 | 资源 ID | 名称 | 地域 | 诊断模式 |
|------|---------|---------|------|------|---------|
| 1    | CVM     | ins-xxx | web-01 | ap-guangzhou | 精细化 |
| 2    | CDB     | cdb-xxx | mysql-01 | ap-guangzhou | 精细化 |
| 3    | Redis   | crs-xxx | cache-01 | ap-guangzhou | 精细化 |
| 4    | CKafka  | ckafka-x | mq-01 | ap-guangzhou | 精细化 |
| 5    | CLB     | lb-xxx  | slb-01 | ap-guangzhou | 通用 |
```

> 💡 「精细化」模式使用预设的核心指标和专用阈值；「通用」模式通过 `DescribeBaseMetrics` 动态探测指标，使用通用阈值。

---

## Phase 1: 资源状态检查

对资源清单中的每个资源，检查基本运行状态。

### CVM 实例状态

```bash
tccli cvm DescribeInstances --region ap-guangzhou \
  --InstanceIds '["ins-xxxxx"]'
```

关注字段：
- `InstanceState`：应为 `RUNNING`（非 `STOPPED` / `SHUTDOWN` / `TERMINATING`）
- `ExpiredTime`：检查是否即将到期（30 天内）
- `RestrictState`：是否被隔离（`PROTECTIVELY_ISOLATED`）

### CDB MySQL 实例状态

```bash
tccli cdb DescribeDBInstances --region ap-guangzhou \
  --InstanceIds '["cdb-xxxxx"]'
```

关注字段：
- `Status`：应为 `1`（运行中）
- `DeadlineTime`：检查是否即将到期
- `TaskStatus`：应为 `0`（无任务）

### Redis 实例状态

```bash
tccli redis DescribeInstances --region ap-guangzhou \
  --InstanceId crs-xxxxx
```

关注字段：
- `Status`：应为 `2`（运行中）
- `DeadlineTime`：检查是否即将到期

### CKafka 实例状态

```bash
tccli ckafka DescribeInstances --region ap-guangzhou \
  --InstanceId ckafka-xxxxx
```

关注字段：
- `Status`：应为 `1`（运行中）
- `ExpireTime`：检查是否即将到期

### 其他/未知类型资源的通用状态检查

对于不在上述已知列表中的资源类型，执行以下通用探测流程：

**步骤 1：确定 tccli 服务名和查询接口**

```bash
# 尝试用 tccli 查看该服务支持的操作
tccli <服务名> --help
```

大多数腾讯云产品遵循 `Describe*Instances` 或 `Describe*` 模式查询实例信息。

**步骤 2：查询实例详情**

```bash
# 尝试常见的查询模式
tccli <服务名> DescribeInstances --help
# 或
tccli <服务名> Describe<资源类型>s --help
```

**步骤 3：从返回结果中提取关键状态字段**

通用关注字段（大多数产品具备）：
- `Status` / `InstanceState` / `State`：运行状态
- `ExpiredTime` / `DeadlineTime` / `ExpireTime`：到期时间
- `InstanceId` / 资源 ID：用于后续监控查询

> 💡 **提示**：如果无法通过 tccli 查询到实例详情（如该产品不支持 DescribeInstances），则跳过状态检查，直接进入 Phase 2 尝试拉取监控数据。

### 状态检查结果标注

| 状态 | 标注 |
|------|------|
| 运行中 | ✅ 正常 |
| 已停止但未隔离 | ⚠️ 警告 |
| 被隔离/欠费 | ❌ 异常 |
| 30 天内到期 | ⚠️ 即将到期 |

---

## Phase 2: 监控指标诊断

通过 `tccli monitor GetMonitorData` 拉取各资源的核心监控指标，对比阈值判断是否异常。

### 时间范围

默认拉取**最近 1 小时**的数据，粒度 300 秒（5 分钟）。时间范围可根据用户需求调整。

```
StartTime: 当前时间 - 1小时（ISO 8601 格式）
EndTime: 当前时间（ISO 8601 格式）
Period: 300
```

### CVM 监控指标

| 指标 | MetricName | 正常范围 | 警告阈值 | 危险阈值 |
|------|-----------|---------|---------|---------|
| CPU 使用率 | `CpuUsage` | < 70% | ≥ 70% | ≥ 90% |
| 内存使用率 | `MemUsage` | < 70% | ≥ 70% | ≥ 90% |
| 基础 CPU 使用率 | `BaseCpuUsage` | < 70% | ≥ 70% | ≥ 85% |
| TCP 连接数 | `TcpCurrEstab` | 稳定 | 持续增长 | 突增 50%+ |
| 内网出带宽 | `LanOuttraffic` | < 60% | ≥ 60% | ≥ 80% |

```bash
# CVM CPU 使用率
tccli monitor GetMonitorData --region ap-guangzhou \
  --Namespace QCE/CVM \
  --MetricName CpuUsage \
  --Instances '[{"Dimensions":[{"Name":"InstanceId","Value":"ins-xxxxx"}]}]' \
  --Period 300 \
  --StartTime "2026-03-26T08:00:00+08:00" \
  --EndTime "2026-03-26T09:00:00+08:00"
```

> 💡 CVM 的其他指标（MemUsage、BaseCpuUsage 等）替换 `--MetricName` 即可，Namespace 和 Dimensions 格式不变。

### CDB MySQL 监控指标

| 指标 | MetricName | 正常范围 | 警告阈值 | 危险阈值 |
|------|-----------|---------|---------|---------|
| CPU 使用率 | `CpuUseRate` | < 60% | ≥ 60% | ≥ 80% |
| 内存使用率 | `MemoryUseRate` | < 70% | ≥ 70% | ≥ 85% |
| 磁盘使用率 | `VolumeRate` | < 70% | ≥ 70% | ≥ 85% |
| 主从延迟 | `SlaveDelay` | 0s | ≥ 5s | ≥ 10s |
| 连接使用率 | `ConnectionUseRate` | < 60% | ≥ 60% | ≥ 80% |
| 慢查询数 | `SlowQueries` | 0 | > 0 | > 10/min |

```bash
# CDB MySQL CPU 使用率
tccli monitor GetMonitorData --region ap-guangzhou \
  --Namespace QCE/CDB \
  --MetricName CpuUseRate \
  --Instances '[{"Dimensions":[{"Name":"InstanceId","Value":"cdb-xxxxx"}]}]' \
  --Period 300 \
  --StartTime "2026-03-26T08:00:00+08:00" \
  --EndTime "2026-03-26T09:00:00+08:00"
```

### Redis 监控指标

| 指标 | MetricName | 正常范围 | 警告阈值 | 危险阈值 |
|------|-----------|---------|---------|---------|
| CPU 使用率 | `CpuUtil` | < 60% | ≥ 60% | ≥ 80% |
| 内存使用率 | `MemUtil` | < 60% | ≥ 60% | ≥ 80% |
| 连接数 | `Connections` | 稳定 | 接近上限 80% | 接近上限 95% |
| 命令执行错误 | `CmdErr` | 0 | > 0 | 持续 > 0 |
| 平均执行时延 | `AvgExecLatency` | < 5ms | ≥ 5ms | ≥ 10ms |

```bash
# Redis 内存使用率
tccli monitor GetMonitorData --region ap-guangzhou \
  --Namespace QCE/REDIS_MEM \
  --MetricName MemUtil \
  --Instances '[{"Dimensions":[{"Name":"instanceid","Value":"crs-xxxxx"}]}]' \
  --Period 300 \
  --StartTime "2026-03-26T08:00:00+08:00" \
  --EndTime "2026-03-26T09:00:00+08:00"
```

> ⚠️ **注意**：Redis 的 Namespace 是 `QCE/REDIS_MEM`（不是 `QCE/REDIS`），Dimension 名称是小写的 `instanceid`。

### CKafka 监控指标

| 指标 | MetricName | 正常范围 | 警告阈值 | 危险阈值 |
|------|-----------|---------|---------|---------|
| 消息堆积量 | `MsgHeap` | 稳定/下降 | 持续增长 | 急剧增长 |
| 生产速率 | `ProducerTps` | 稳定 | 下降 30%+ | 下降 50%+ |
| 消费速率 | `ConsumerTps` | 稳定 | 下降 30%+ | 下降 50%+ |
| 磁盘使用率 | `DiskUsage` | < 60% | ≥ 60% | ≥ 80% |

```bash
# CKafka 消息堆积量
tccli monitor GetMonitorData --region ap-guangzhou \
  --Namespace QCE/CKAFKA \
  --MetricName MsgHeap \
  --Instances '[{"Dimensions":[{"Name":"instanceId","Value":"ckafka-xxxxx"}]}]' \
  --Period 300 \
  --StartTime "2026-03-26T08:00:00+08:00" \
  --EndTime "2026-03-26T09:00:00+08:00"
```

### 其他/未知类型资源的通用监控诊断

对于不在上述已知产品列表中的资源，通过**动态探测**完成监控诊断。

**步骤 1：确定 Monitor Namespace**

先尝试根据 Phase 0 的已知映射表找到 Namespace。如果不在表中，使用以下命令查询所有支持监控的产品：

```bash
tccli monitor DescribeProductList --Module monitor
```

从返回结果中匹配该资源类型对应的 Namespace。

**步骤 2：动态获取可用指标列表**

```bash
# 查询该 Namespace 下支持的所有监控指标
tccli monitor DescribeBaseMetrics --Namespace <Namespace>
```

返回结果中每个指标包含：
- `MetricName`：指标英文名
- `MetricCName`：指标中文名
- `Dimensions`：所需维度
- `Unit`：单位（%、MB、Count、ms 等）
- `Periods`：支持的统计粒度

**步骤 3：从指标列表中筛选核心指标**

按以下优先级自动筛选需要拉取的指标（选取最多 6 个）：

| 优先级 | 指标关键词（匹配 MetricName 或 MetricCName） | 说明 |
|--------|----------------------------------------------|------|
| 🔴 P0 | `Cpu`、`CpuUsage`、`CpuUtil`、`CpuUseRate` | CPU 使用率 |
| 🔴 P0 | `Mem`、`Memory`、`MemUsage`、`MemUtil` | 内存使用率 |
| 🟠 P1 | `Disk`、`Volume`、`Storage`、`DiskUsage`、`VolumeRate` | 磁盘/存储使用率 |
| 🟠 P1 | `Connection`、`Conn`、`ActiveConn` | 连接数/连接使用率 |
| 🟡 P2 | `Latency`、`Delay`、`ResponseTime` | 延迟/响应时间 |
| 🟡 P2 | `Error`、`Fail`、`Reject` | 错误数/失败率 |
| 🔵 P3 | `Traffic`、`Bandwidth`、`InBandwidth`、`OutBandwidth` | 流量/带宽 |
| 🔵 P3 | `Qps`、`Tps`、`Requests` | 请求量/吞吐量 |

> 💡 **匹配逻辑**：对 `DescribeBaseMetrics` 返回的指标列表，按上述关键词进行大小写不敏感的部分匹配。每个优先级选取第一个匹配的指标。如果某优先级没有匹配项则跳过。

**步骤 4：拉取指标数据**

```bash
# 通用拉取模板（替换 Namespace、MetricName、Dimension）
tccli monitor GetMonitorData --region ap-guangzhou \
  --Namespace <Namespace> \
  --MetricName <MetricName> \
  --Instances '[{"Dimensions":[{"Name":"<DimensionKey>","Value":"<资源ID>"}]}]' \
  --Period 300 \
  --StartTime "<1小时前>" \
  --EndTime "<当前时间>"
```

> ⚠️ **Dimension 的 Name 值**从 `DescribeBaseMetrics` 返回的 `Dimensions` 字段获取，不要硬编码猜测。

**步骤 5：通用阈值判定**

对于没有预设阈值的指标，按以下通用规则判定：

| 指标类型 | 单位 | 正常范围 | 警告阈值 | 危险阈值 |
|---------|------|---------|---------|---------|
| 使用率类 | `%` | < 70% | ≥ 70% | ≥ 90% |
| 延迟类 | `ms` | < 100ms | ≥ 100ms | ≥ 500ms |
| 错误/失败类 | `Count` | 0 | > 0 | 持续 > 0 |
| 连接数类 | `Count` | 稳定不增 | 持续增长 | 突增 50%+ |
| 流量/吞吐类 | `MB`/`Count` | 稳定 | 异常波动 30%+ | 异常波动 50%+ |

> 💡 对于使用率类指标（单位为 %），阈值判断最可靠。其他类型指标缺乏绝对基准，应结合趋势判断（是否突增/突降）。在报告中标注这些是**通用阈值参考**，建议用户根据业务实际调整。

### 指标数据分析方法

拉取到监控数据后，按以下方式分析：

1. **计算平均值**：取时间窗口内所有数据点的平均值，与阈值对比
2. **计算最大值**：取时间窗口内的峰值，识别是否存在突增
3. **趋势判断**：对比前后数据点，判断指标是稳定、上升还是下降

---

## Phase 3: 告警策略覆盖检查

检查这些资源是否被 Monitor 告警策略覆盖。

根据资源清单中涉及的产品类型，逐一查询对应 Namespace 的告警策略：

```bash
# 按 Namespace 查询告警策略（替换为实际涉及的 Namespace）
tccli monitor DescribeAlarmPolicies --region ap-guangzhou --Module monitor --Namespace <Namespace>
```

常见产品告警策略查询示例：
```bash
tccli monitor DescribeAlarmPolicies --region ap-guangzhou --Module monitor --Namespace QCE/CVM
tccli monitor DescribeAlarmPolicies --region ap-guangzhou --Module monitor --Namespace QCE/CDB
tccli monitor DescribeAlarmPolicies --region ap-guangzhou --Module monitor --Namespace QCE/REDIS_MEM
tccli monitor DescribeAlarmPolicies --region ap-guangzhou --Module monitor --Namespace QCE/CKAFKA
```

> 💡 对于未知类型资源，使用 Phase 2 中确定的 Namespace 查询告警策略。如果无法确定 Namespace，则标注"无法检查告警覆盖"。

检查要点：
- 每个资源是否被至少一个告警策略覆盖
- 告警策略是否覆盖了核心指标（CPU、内存、磁盘等）
- 告警通知渠道是否已配置（短信、邮件、微信等）

标注规则：
- ✅ 有告警策略覆盖且涵盖核心指标
- ⚠️ 有告警策略但缺少关键指标覆盖
- ❌ 无任何告警策略覆盖

---

## Phase 4: 健康度评分与报告

### 单资源健康度评分

根据 Phase 1（状态）和 Phase 2（指标）的检查结果，对每个资源计算健康度分数：

| 评分区间 | 标记 | 判定条件 |
|---------|------|---------|
| 80-100 分 | ✅ 健康 | 资源运行中，所有核心指标在正常范围内 |
| 60-79 分 | ⚠️ 亚健康 | 资源运行中，存在 1-2 个指标达到警告阈值 |
| 0-59 分 | ❌ 异常 | 资源非运行状态，或存在指标达到危险阈值 |

**扣分规则**：
- 基础分 100 分
- 每个指标达到**警告阈值**：扣 10 分
- 每个指标达到**危险阈值**：扣 20 分
- 资源**非运行状态**：直接降至 40 分
- 资源**被隔离/欠费**：直接降至 20 分
- **无告警策略覆盖**：扣 5 分
- **通用诊断资源**（非精细化指标）：在报告中标注 `[通用诊断]`，提示用户阈值为参考值

### 服务整体健康度

```
服务健康度 = 所有资源健康度分数的最低值（木桶原理）

  ✅ 健康:   最低资源分数 ≥ 80
  ⚠️ 亚健康: 最低资源分数在 60-79
  ❌ 异常:   最低资源分数 < 60
```

> 采用木桶原理（取最低分），因为一个关键资源异常即可影响整个服务可用性。

---

## 巡检报告模板

执行完上述所有阶段后，**必须**输出以下格式的巡检报告：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏥 云服务健康度巡检报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 服务名称: <服务名或标签值>
📌 巡检时间: <当前时间>
📌 巡检地域: <地域>
📌 资源总数: <资源数量>

┌─────────────────────────────────────────────────┐
│ 📊 服务整体健康度: ✅/⚠️/❌ <状态> (<分数>/100)  │
└─────────────────────────────────────────────────┘

## 资源清单与状态

| 资源类型 | 资源ID | 名称 | 运行状态 | 健康度 |
|---------|--------|------|---------|--------|
| CVM     | ins-xxx | web-01  | ✅ RUNNING | 95/100 |
| CDB     | cdb-xxx | mysql-01 | ✅ 运行中 | 62/100 ⚠️ |
| Redis   | crs-xxx | cache-01 | ✅ 运行中 | 90/100 |
| CKafka  | ckafka-x| mq-01   | ✅ 运行中 | 85/100 |
| CLB     | lb-xxx  | slb-01  | ✅ 运行中 | 88/100 [通用诊断] |
| MongoDB | cmgo-xx | mongo-01 | ✅ 运行中 | 78/100 ⚠️ [通用诊断] |

## 异常/警告指标详情

（仅列出存在警告或异常的资源）

### ⚠️ CDB mysql-01 (cdb-xxx) — 健康度 62/100

| 指标 | 当前值(平均) | 峰值 | 阈值 | 状态 |
|------|------------|------|------|------|
| CPU使用率 | 82% | 91% | 警告≥60% 危险≥80% | ❌ 危险 |
| 内存使用率 | 72% | 78% | 警告≥70% 危险≥85% | ⚠️ 警告 |
| 磁盘使用率 | 87% | 89% | 警告≥70% 危险≥85% | ❌ 危险 |
| 主从延迟 | 0s | 0s | 警告≥5s 危险≥10s | ✅ 正常 |
| 连接使用率 | 45% | 52% | 警告≥60% 危险≥80% | ✅ 正常 |
| 慢查询数 | 23/5min | 45 | > 0 关注 | ⚠️ 关注 |

## 告警策略覆盖

| 资源 | 告警覆盖 | 说明 |
|------|---------|------|
| CVM ins-xxx | ✅ 已覆盖 | CPU/内存/磁盘告警已配置 |
| CDB cdb-xxx | ❌ 未覆盖 | 建议配置告警策略 |
| Redis crs-xxx | ✅ 已覆盖 | 内存/连接数告警已配置 |
| CKafka ckafka-x | ⚠️ 部分覆盖 | 缺少消息堆积告警 |

## 修复建议（按优先级）

> ⚠️ 以下为建议，**仅供参考，需用户确认后自行执行**。巡检过程不会自动执行任何修复操作。

1. 🔴 [紧急] <资源名> <具体问题>，建议 <修复方案>
2. 🟠 [高] <资源名> <具体问题>，建议 <修复方案>
3. 🟡 [中] <资源名> <具体问题>，建议 <修复方案>
4. 🔵 [低] <资源名> <具体问题>，建议 <修复方案>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## API 速查

| 功能 | 服务 | 接口 |
|------|------|------|
| 查询标签键 | tag | `DescribeTagKeys` |
| 查询标签值 | tag | `DescribeTagValues` |
| 按标签查资源 | tag | `DescribeResourcesByTags` |
| 查询 CVM 实例 | cvm | `DescribeInstances` |
| 查询 CDB 实例 | cdb | `DescribeDBInstances` |
| 查询 Redis 实例 | redis | `DescribeInstances` |
| 查询 CKafka 实例 | ckafka | `DescribeInstances` |
| 查询监控数据 | monitor | `GetMonitorData` |
| 查询告警策略 | monitor | `DescribeAlarmPolicies` |
| 查询产品支持的指标 | monitor | `DescribeBaseMetrics` |
| 查询监控产品列表 | monitor | `DescribeProductList` |

---

## 监控 Namespace 与 Dimension 速查

### 已知产品速查

| 云产品 | ServiceType | Namespace | Dimension Key |
|--------|-------------|-----------|---------------|
| CVM | `cvm` | `QCE/CVM` | `InstanceId` |
| CDB MySQL | `cdb` | `QCE/CDB` | `InstanceId` |
| Redis | `redis` | `QCE/REDIS_MEM` | `instanceid`（小写） |
| CKafka | `ckafka` | `QCE/CKAFKA` | `instanceId` |
| Lighthouse | `lighthouse` | `QCE/LIGHTHOUSE` | `InstanceId` |
| TDSQL-C MySQL | `cynosdb` | `QCE/CYNOSDB_MYSQL` | `InstanceId` |
| MariaDB | `mariadb` | `QCE/MARIADB` | `InstanceId` |
| PostgreSQL | `postgres` | `QCE/POSTGRES` | `resourceId` |
| MongoDB | `mongodb` | `QCE/CMONGO` | `target` |
| CLB（公网） | `clb` | `QCE/LB_PUBLIC` | `vip` |
| NAT 网关 | `nat` | `QCE/NAT_GATEWAY` | `natId` |
| Elasticsearch | `es` | `QCE/CES` | `uInstanceId` |

> ⚠️ 特别注意：
> - Redis 的 Namespace 是 `QCE/REDIS_MEM`，Dimension key 是**小写**的 `instanceid`
> - PostgreSQL 的 Dimension key 是 `resourceId`（不是 InstanceId）
> - MongoDB 的 Dimension key 是 `target`

### 未知产品的 Namespace 探测

如果产品不在上表中，通过以下步骤确定 Namespace 和 Dimension：

```bash
# 1. 查询所有支持监控的产品列表
tccli monitor DescribeProductList --Module monitor

# 2. 找到匹配的 Namespace 后，查询该 Namespace 下的指标和维度
tccli monitor DescribeBaseMetrics --Namespace <Namespace>
```

`DescribeBaseMetrics` 返回的每个指标中的 `Dimensions` 字段即为该产品需要的维度信息。

---

## 何时使用

| 场景 | 建议 |
|------|------|
| 用户说「服务巡检」「健康度检查」「诊断服务」 | ✅ 先让用户选择方式一、方式二或方式三，再执行 Phase 0-4 完整流程 |
| 用户说「看看 CPU/内存使用率」「监控指标异常」「性能检查」 | ✅ 需用户提供资源 ID，只执行 Phase 2 的对应产品部分 |
| 用户说"帮我查查所有服务器"但未明确全量 | ⛔ 不执行全量扫描，引导用户通过标签或手动指定范围 |
| 用户明确要求"全量巡检/扫描所有资源" | ✅ 确认地域和产品范围后，走方式三全量扫描 |
| 用户说「域名到期」「证书过期」「资源是否到期」 | ⛔ **不使用本文档**，用 references/auto-check-resource.md |
| 用户说「检查实例状态」「实例是否在运行」「云硬盘状态」 | ⛔ **不使用本文档**，用 references/auto-check-resource.md |
| 用户说「资源巡检」「批量检查资源状态」 | ⛔ **不使用本文档**，用 references/auto-check-resource.md |
| 用户要做安全检查/安全审计 | ⛔ 不使用本文档，用 references/cvm-security-check.md |
| 用户要部署应用或建站 | ⛔ 不使用本文档，用对应的部署/建站 reference |
