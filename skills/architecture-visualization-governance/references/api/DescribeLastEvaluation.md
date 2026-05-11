# DescribeLastEvaluation — 获取架构图最近一次评估结果

获取指定架构图最近一次的 Well-Architected 评估结果，包括总分、各支柱维度得分以及治理建议。

## 参数

| 参数 | 必选 | 类型 | 描述 |
|------|------|------|------|
| ArchId | 是 | String | 云架构 ID，如 `arch-gvqocc25` |

## 调用示例

```bash
python3 {baseDir}/scripts/tcloud_api.py \
  advisor \
  advisor.tencentcloudapi.com \
  DescribeLastEvaluation \
  2020-07-21 \
  '{"ArchId":"arch-gvqocc25"}'
```

## 返回示例

```json
{
  "success": true,
  "action": "DescribeLastEvaluation",
  "data": {
    "UpdateTime": "2024-07-12 09:12:34",
    "NeedReEvaluation": false,
    "WellArchScore": {
      "TotalScore": 68,
      "PillarScore": [
        {"Category": "安全", "Value": 34},
        {"Category": "可靠", "Value": 34},
        {"Category": "性能", "Value": 34},
        {"Category": "成本", "Value": 34},
        {"Category": "服务限制", "Value": 34},
        {"Category": "卓越运营", "Value": 34}
      ]
    },
    "GovernanceAdvices": [
      {
        "AdviceCategory": "推荐治理",
        "Layer": [
          {
            "LayerCategory": "资源层",
            "Advices": [
              {
                "StrategyName": "strategy-xxx",
                "Title": "云数据库（MySQL）root 账号安全风险",
                "Pillar": "安全",
                "Explain": "检查root 账号安全风险",
                "Problems": [
                  {
                    "Title": "MySQL实例只设置了root账号",
                    "ImpactInstances": 4,
                    "Callback": {"Type": "Plugin", "Value": "PluginName", "Param": "测试参数"}
                  }
                ]
              }
            ]
          },
          {
            "LayerCategory": "架构层",
            "Advices": []
          }
        ]
      }
    ]
  },
  "requestId": "xxx-xxx-xx"
}
```

## 返回字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `UpdateTime` | String | 最近一次评估时间 |
| `NeedReEvaluation` | Boolean | 是否需要重新评估（架构图有变更时为 `true`） |
| `WellArchScore.TotalScore` | Integer | 总评分（满分 100） |
| `WellArchScore.PillarScore[]` | Array | 各支柱维度得分 |
| `PillarScore[].Category` | String | 维度名称：安全 / 可靠 / 性能 / 成本 / 服务限制 / 卓越运营 |
| `PillarScore[].Value` | Integer | 该维度得分 |
| `GovernanceAdvices[]` | Array | 治理建议分组 |
| `GovernanceAdvices[].AdviceCategory` | String | 建议分类：推荐治理 / 安全 / 可靠 / 性能 / 成本 / 服务限制 / 卓越运营 |
| `GovernanceAdvices[].Layer[]` | Array | 按层级分组的建议 |
| `Layer[].LayerCategory` | String | 层级分类：资源层 / 架构层 |
| `Layer[].Advices[]` | Array | 具体建议列表 |
| `Advices[].StrategyName` | String | 策略标识 |
| `Advices[].Title` | String | 建议标题 |
| `Advices[].Pillar` | String | 所属支柱维度 |
| `Advices[].Explain` | String | 检查说明 |
| `Advices[].Problems[]` | Array | 发现的问题列表 |
| `Problems[].Title` | String | 问题描述 |
| `Problems[].ImpactInstances` | Integer | 影响的实例数量 |
| `Problems[].Callback` | Object | 回调信息（可选） |
| `Callback.Type` | String | 回调类型：`URL`（跳转链接）/ `Plugin`（插件） |
| `Callback.Value` | String | 回调值（URL 地址或插件名称） |
| `Callback.Param` | String | 回调参数 |

## 展示格式

向用户展示评估结果时，先展示总分和各维度得分，再按建议分类展示治理建议：

```
📊 架构评估结果（arch-gvqocc25）
评估时间：2024-07-12 09:12:34
总分：68 / 100

各维度得分：
  安全：34  |  可靠：34  |  性能：34
  成本：34  |  服务限制：34  |  卓越运营：34

【推荐治理】
  ▸ 资源层
    ⚠️ 云数据库（MySQL）root 账号安全风险（安全）
       MySQL实例只设置了root账号，影响 4 个实例

  ▸ 架构层
    （无建议）

【安全】
  ▸ 资源层
    ⚠️ 云数据库（MySQL）root 账号安全风险（安全）
       MySQL实例只设置了root账号，影响 4 个实例
```

当 `NeedReEvaluation` 为 `true` 时，应在输出中提示用户：`⚠️ 架构图已变更，建议重新评估`。

当 `Callback.Type` 为 `URL` 时，可将 `Callback.Value` 作为问题详情链接展示。

## 典型用法

- "查看架构图 arch-xxx 的评估结果" → 调用接口，展示总分和各维度得分
- "这个架构图有哪些安全问题" → 调用接口，筛选 `AdviceCategory=安全` 或 `Pillar=安全` 的建议
- "架构图需要治理什么" → 调用接口，筛选 `AdviceCategory=推荐治理` 的建议
