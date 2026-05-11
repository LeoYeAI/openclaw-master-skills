# DescribeStrategies — 获取智能顾问支持的风险评估项列表

查询智能顾问**平台支持**的所有风险评估项（巡检项），涵盖安全、可靠、费用、性能、服务限制等维度，覆盖 COS、CVM、MySQL、Redis、CBS、CAM、CLB、VPC 等云产品。该接口返回的是智能顾问平台定义的评估规则列表，**不是**某个架构图的风险评估结果。

## 参数

无必填参数，直接调用即可。

## 调用示例

```bash
python3 {baseDir}/scripts/tcloud_api.py \
  advisor \
  advisor.tencentcloudapi.com \
  DescribeStrategies \
  2020-07-21 \
  '{}'
```

## 返回示例

```json
{
  "success": true,
  "action": "DescribeStrategies",
  "data": {
    "Strategies": [
      {
        "StrategyId": 131,
        "Name": "云数据库（Redis）跨可用区部署",
        "Desc": "检查 Redis 实例是否跨可用区部署...",
        "Product": "redis",
        "ProductDesc": "云数据库（Redis）",
        "Repair": "建议采用跨可用区部署方案...",
        "GroupId": 2,
        "GroupName": "可靠",
        "IsSupportCustom": false,
        "Conditions": [
          {
            "ConditionId": 178,
            "Level": 2,
            "LevelDesc": "中风险",
            "Desc": "Redis 实例未跨可用区部署"
          }
        ]
      }
    ]
  },
  "requestId": "xxxxxxxx-..."
}
```

## 返回字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `StrategyId` | Integer | 评估项唯一 ID |
| `Name` | String | 评估项名称（用于拼接控制台链接） |
| `Desc` | String | 评估项描述 |
| `Product` | String | 产品标识（cos / cvm / mysql / redis / cbs / cam 等） |
| `ProductDesc` | String | 产品中文名 |
| `Repair` | String | 修复建议 |
| `GroupName` | String | 分组：安全 / 可靠 / 费用 / 性能 / 服务限制 |
| `Conditions[].Level` | Integer | 风险等级：3=高危 / 2=中危 / 1=低危 |
| `Conditions[].LevelDesc` | String | 等级描述 |
| `Conditions[].Desc` | String | 条件描述 |

## 筛选方式

该接口无服务端筛选参数，返回全量评估项。需在返回结果中按以下维度进行客户端筛选：

1. **按产品筛选**：用 `Product` 字段匹配（如 `cos`、`cvm`、`mysql`、`redis`）
2. **按分组筛选**：用 `GroupName` 字段匹配（`安全`、`可靠`、`费用`、`性能`、`服务限制`）
3. **按风险等级筛选**：遍历 `Conditions[]`，`Level` 为 3=高危、2=中危、1=低危

## 常见 Product 值

| Product | ProductDesc |
|---------|-------------|
| cos | 对象存储（COS） |
| cvm | 云服务器（CVM） |
| mysql | 云数据库（MySQL） |
| redis | 云数据库（Redis） |
| cbs | 云硬盘（CBS） |
| cam | 访问管理（CAM） |
| clb | 负载均衡（CLB） |
| vpc | 私有网络（VPC） |
| lighthouse | 轻量应用服务器（LH） |
| mongodb | 云数据库（MongoDB） |

## 控制台直达链接

每个评估项可通过 `Name` 字段拼接控制台跳转 URL（无需免密登录，直接展示即可）：

```
https://console.cloud.tencent.com/advisor/assess?strategyName={URL编码后的Name}
```

## 展示格式

向用户展示评估项时，按产品分组，每条包含风险等级、名称、分组和控制台链接：

```
【云数据库（Redis）】
  🔴 高危  Redis 实例未开启密码认证
  分组：安全  |  StrategyId：132
  控制台：https://console.cloud.tencent.com/advisor/assess?strategyName=Redis%20...

  🟡 中危  云数据库（Redis）跨可用区部署
  分组：可靠  |  StrategyId：131
  控制台：https://console.cloud.tencent.com/advisor/assess?strategyName=...
```

等级图标：🔴 高危（Level=3）、🟡 中危（Level=2）、🟢 低危（Level=1）

## 典型用法

- "查看 COS 的所有风险项" → 筛选 `Product=cos`，输出带控制台链接的列表
- "有哪些高危的安全风险" → 筛选 `GroupName=安全` + `Level=3`
- "智能顾问有哪些巡检项" → 直接输出全量列表（按 ProductDesc 分组）
- "给我 Redis 的巡检链接" → 筛选 `Product=redis`，每条附上控制台 URL
