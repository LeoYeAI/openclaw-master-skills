# 流水线 API

本文档定义流水线相关的 OpenAPI 接口。

> **更新日期**: 2026-03-15
> **接口数量**: 23
> **控制器路径**: `/rest/openapi/pipeline`

---

## 接口概览

| 序号 | 接口名称 | 请求方法 | 接口路径 |
|------|----------|----------|----------|
| 1 | 保存流水线 | POST | /save |
| 2 | 手动执行流水线 | POST | /runByManual |
| 3 | 获取流水线参数 | GET | /edit |
| 4 | ���消流水线 | POST | /cancel |
| 5 | 分页查询流水线执行记录 | GET | /queryPipelineWorkPage |
| 6 | 查询流水线执行记录详情 | GET | /getPipelineWorkById |
| 7 | 删除流水线 | POST | /delete |
| 8 | 分页查询流水线 | POST | /queryPipelinePage |
| 9 | 分页查询流水线模板 | POST | /queryPipelineTemplatePage |
| 10 | 查询最近流水线执行记录 | POST | /queryLastestSelectedValueByField |
| 11 | 查询流水线基本信息 | GET | /queryPipelineById |
| 12 | 分页获取分支/标签列表 | POST | /getRepoBranchAndTagList |
| 13 | 分页获取commit列表 | POST | /queryRepoCommitList |
| 14 | 查询代码提交详情 | POST | /queryCommitDetail |
| 15 | 获取镜像tag列表 | GET | /imageTags |
| 16 | 获取包版本列表 | GET | /packageVersions |
| 17 | 分页查询工作空间 | POST | /queryWorkspacePage |
| 18 | 分页查询代码仓库 | POST | /queryRepoList |
| 19 | 分页获取分支列表 | POST | /queryRepoBranchList |
| 20 | 查询流水线控制台日志 | GET | /getJenkinsConsoleLog |
| 21 | 查询单个流水线模板 | GET | /getPipTemplateById |
| 22 | 保存流水线模板 | POST | /savePipTemplate |
| 23 | 查询仓库token配置状态 | POST | /checkRepoTokenByRepoTypeList |

---

## 通用响应格式

| 字段名 | 类型 | 描述 |
|--------|------|------|
| code | Integer | 响应码：0=成功, -1=失败 |
| message | String | 响应消息描述 |
| data | Object | 响应数据（类型视接口而定） |
| requestId | String | 请求唯一标识（UUID） |

---

## 1. 保存流水线

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/save` |
| 请求方法 | POST |
| 接口描述 | 保存新建或编辑的流水线配置（新建/编辑） |

### 请求体

```json
{
  "pipeline": {
    "name": "订单服务构建流水线",
    "spaceId": 1001,
    "pipelineId": "",
    "sources": [...],
    "stages": [...]
  },
  "taskDataList": [...]
}
```

### PipelineParams 字段说明

| 字段名 | 类型 | 必填 | 描述 | 示例值 |
|--------|------|------|------|--------|
| pipelineId | String | 否 | 流水线ID（后端生成UUID，编辑时必填） | `pipe-abc123` |
| name | String | 是 | 流水线名称 | `订单服务构建流水线` |
| spaceId | Long | 是 | 空间ID | `1001` |
| aliasId | String | 否 | 流水线别名ID（页面显示） | `PIPE001` |
| pipelineKey | String | 否 | 流水线Key | `order-service-pipeline` |
| label | JSONArray | 否 | 流水线标签数组 | `["Java", "Microservice"]` |
| sources | List | 否 | 流水线代码源 | 详见 Source |
| stages | List | 否 | 阶段信息 | 详见 Stage |
| timeoutDuration | String | 否 | 超时时间（2D/2H/2M/2S） | `2H` |
| buildPlatform | String | 否 | 构建平台（windows/linux） | `linux` |
| buildMachineMode | String | 否 | 构建机器模式（default/custom） | `default` |
| autoFillRunConfig | Boolean | 否 | 自动填充上一次运行配置参数 | `false` |

### 响应

```json
{
  "code": 0,
  "message": "success",
  "data": "pipe-abc123",
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## 2. 获取流水线参数（编辑时）

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/edit` |
| 请求方法 | GET |
| 接口描述 | 编辑流水线时获取流水线配置参数 |

### 参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `pipelineId` | string | 是 | 流水线ID |

### 响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "pipelineId": "pipe-abc123",
    "name": "订单服务构建流水线",
    "spaceId": 1001,
    "sources": [...],
    "stages": [...],
    "triggerInfo": { "triggerType": 0 },
    "timeoutDuration": "2H",
    "buildPlatform": "linux"
  },
  "requestId": "uuid-string"
}
```

---

## 3. 删除流水线

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/delete` |
| 请求方法 | POST |
| 接口描述 | 删除指定的流水线及其关联的主机/主机组关系 |

### 参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `pipelineId` | string | 是 | 流水线ID（Query参数） |

### 响应

```json
{
  "code": 0,
  "message": "success",
  "data": true,
  "requestId": "uuid-string"
}
```

---

## 4. 查询流水线基本信息

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/queryPipelineById` |
| 请求方法 | GET |
| 接口描述 | 根据流水线ID查询单条流水线的基本信息 |

### 参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `pipelineId` | string | 是 | 流水线ID |

### 响应 PipelineTemplateVO

```json
{
  "code": 0,
  "data": {
    "id": "pipe-abc123",
    "pipelineName": "订单服务构建流水线",
    "pipelineKey": "order-service",
    "pipelineAliasId": "PIPE001",
    "pipelineLabel": "[\"Java\",\"Microservice\"]",
    "label": ["Java", "Microservice"],
    "spaceId": 1001,
    "createTime": "2025-01-15T10:00:00",
    "updateTime": "2025-01-15T10:00:00",
    "creator": "zhangsan",
    "creatorName": "张三",
    "store": 0,
    "permissionList": ["edit", "delete", "run"],
    "pipelineOwner": "zhangsan",
    "pipelineOwnerName": "张三",
    "buildNumber": 10,
    "buildNumberHasUsed": false,
    "latestPipWorkVO": {}
  }
}
```

---

## 5. 分页查询流水线

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/queryPipelinePage` |
| 请求方法 | POST |
| 接口描述 | 分页查询流水线列表 |

### 请求体

```json
{
  "spaceId": 1001,
  "pipelineName": "构建",
  "queryFlag": 0,
  "pageNum": 1,
  "pageSize": 10
}
```

### 字段说明

| 字段名 | 类型 | 必填 | 描述 | 示例值 |
|--------|------|------|------|--------|
| spaceId | Long | 是 | 工作空间ID | `1001` |
| pipelineName | String | 否 | 流水线名称（模糊搜索） | `构建` |
| queryFlag | Integer | 否 | 查询标识（0-全部/1-我收藏的/2-我创建的/3-最后一次由我执行的） | `0` |
| account | String | 否 | 当前登录账号 | `zhangsan` |
| flag | Boolean | 否 | 是否需要关联权限表查询 | `true` |
| pageNum | Integer | 否 | 页码 | `1` |
| pageSize | Integer | 否 | 每页大小 | `10` |

### 响应 PipelineTemplateVO 列表

```json
{
  "code": 0,
  "data": {
    "total": 100,
    "size": 10,
    "current": 1,
    "pages": 10,
    "records": [
      {
        "id": "pipe-abc123",
        "pipelineName": "订单服务构建流水线",
        "pipelineKey": "order-service",
        "spaceId": 1001,
        "creator": "zhangsan",
        "creatorName": "张三",
        "store": 0,
        "permissionList": ["edit", "delete", "run"]
      }
    ]
  }
}
```

---

## 6. 分页查询流水线模板

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/queryPipelineTemplatePage` |
| 请求方法 | POST |
| 接口描述 | 分页查询流水线模板列表 |

### 请求体

```json
{
  "spaceId": 1001,
  "pipelineTemplateName": "Java",
  "pipelineTemplateType": "1",
  "pipelineTemplateLanguage": "java",
  "pageNo": 1,
  "pageSize": 10
}
```

### 字段说明

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| spaceId | Long | 是 | 工作空间ID |
| pipelineTemplateName | String | 否 | 流水线模板名称（模糊搜索） |
| pipelineTemplateType | String | 否 | 流水线模板类型 |
| pipelineTemplateLanguage | String | 否 | 流水线模板语言 |
| account | String | 否 | 当前登录账号 |
| pageNo | Integer | 否 | 页码（默认1） |
| pageSize | Integer | 否 | 每页大小（默认10） |

### 响应 PipTemplateVO 列表

```json
{
  "code": 0,
  "data": {
    "total": 50,
    "records": [
      {
        "id": "tpl-abc123",
        "pipelineTemplateName": "Java微服务模板",
        "pipelineTemplateLanguage": "java",
        "pipelineTemplateParams": "{}",
        "pipelineTemplateType": 1,
        "status": 1,
        "statusName": "启用",
        "spaceId": 1001,
        "description": "Java微服务流水线模板",
        "stages": [],
        "pipelineTemplatePermission": ["edit", "delete"]
      }
    ]
  }
}
```

---

## 7. 查询单个流水线模板

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/getPipTemplateById` |
| 请求方法 | GET |
| 接口描述 | 根据ID查询单个流水线模板详情 |

### 参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `id` | string | 是 | 流水线模板ID |

### 响应

```json
{
  "code": 0,
  "data": {
    "id": "template_123456",
    "templateName": "Java构建模板",
    "templateType": "java",
    "description": "Java项目标准构建模板",
    "stages": [...],
    "createTime": "2025-01-10T08:00:00"
  }
}
```

---

## 8. 保存流水线模板

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/savePipTemplate` |
| 请求方法 | POST |
| 接口描述 | 保存新建或编辑的流水线模板配置 |

### 请求体

```json
{
  "id": null,
  "templateName": "Java构建模板",
  "templateType": "java",
  "description": "Java项目标准构建模板",
  "stages": [
    {
      "name": "构建",
      "steps": [{"name": "Maven构建", "command": "mvn clean package"}]
    }
  ],
  "taskDataList": [
    {
      "data": {
        "jobType": "HostDeploy",
        "hostGroupId": 1001,
        "allHosts": false,
        "hostIds": [1001, 1002]
      }
    }
  ]
}
```

### 字段说明

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| id | String | 否 | 模板ID（为空则新建） |
| templateName | String | 是 | 模板名称 |
| templateType | String | 是 | 模板类型 |
| description | String | 否 | 模板描述 |
| stages | List | 是 | 阶段配置列表 |
| taskDataList | List | 否 | 任务参数列表（用于主机部署配置） |

### 响应

```json
{
  "code": 0,
  "data": "template_123456"
}
```

---

## 9. 查询仓库token配置状态

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/checkRepoTokenByRepoTypeList` |
| 请求方法 | POST |
| 接口描述 | 根据仓库类型查询是否配置token |

### 请求体

```json
{
  "repoTypeList": ["gitlab", "github", "gitee"]
}
```

### 响应

```json
{
  "code": 0,
  "data": {
    "gitlab": true,
    "github": false,
    "gitee": true
  }
}
```

---

## 10. 查询流水线控制台日志

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/getJenkinsConsoleLog` |
| 请求方法 | GET |
| 接口描述 | 根据执行记录ID查询流水线的控制台日志 |

### 参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `pipelineLogId` | Long | 是 | 执行记录ID |

### 响应 PipelineJenkinsLogVO

```json
{
  "code": 0,
  "data": {
    "logContent": "[INFO] Build started...\n[INFO] Compiling...",
    "hasMore": false,
    "nextStart": 0,
    "isCompleted": true
  }
}
```

---

## 流水线数据结构

### IFlowData

```typescript
interface IFlowData {
  pipeline: IPipeline
  taskDataList: ITaskData[]
}
```

### IPipeline

```typescript
interface IPipeline {
  pipelineId: string | null
  spaceId: Long
  name: string
  aliasId?: string
  pipelineKey?: string
  label?: string[]
  sources: ISource[]
  stages: IStage[]
  timeoutDuration?: string    // 超时时间（2D/2H/2M/2S）
  buildPlatform?: string      // linux/windows
  buildMachineMode?: string   // default/custom
  autoFillRunConfig?: boolean
  triggerInfo?: TriggerInfo
}
```

### IStage

```typescript
interface IStage {
  id: string
  name: string
  nodeType: 'custom-stage-node'
  steps: IStep[]
}
```

### IStep

```typescript
interface IStep {
  id: string
  name: string
  nodeType: 'custom-step-node'
  idx: number
  driven: 0 | 1    // 0: 串行, 1: 并行
  tasks: ITask[]
}
```

### ITask

```typescript
interface ITask {
  id: string
  name: string
  nodeType: 'custom-task-node'
  idx?: number
}
```

### TriggerInfo

```typescript
interface TriggerInfo {
  triggerType: 0 | 1 | 2 | 6  // 0手动/1定时/2webhook/6OpenAPI
  triggerParams?: object
  triggerUser?: string
}
```

---

## 创建 Stage 的默认结构

添加任务前需要先创建 Stage 和 Step：

```json
{
  "id": "stage-001",
  "name": "构建阶段",
  "nodeType": "custom-stage-node",
  "steps": [
    {
      "id": "step-001",
      "name": "构建步骤",
      "nodeType": "custom-step-node",
      "idx": 0,
      "driven": 0,
      "tasks": []
    }
  ]
}
```

---

## 流水线状态码

| 状态码 | 状态名称 | 说明 |
|--------|----------|------|
| 100000 | 未执行 | 初始状态 |
| 100001 | 等待中 | 等待执行资源 |
| 100002 | 执行中 | 流水线正在运行 |
| 100004 | 成功 | 所有任务执行成功 |
| 100005 | 失败 | 至少一个任务失败 |
| 100006 | 已取消 | 用户手动取消 |

---

## 触发类型

| 类型值 | 类型名称 | 说明 |
|--------|----------|------|
| 0 | 手动触发 | 用户手动执行 |
| 1 | 定时触发 | 通过定时任务触发 |
| 2 | Webhook触发 | 通过外部Webhook接口触发 |
| 6 | OpenAPI触发 | 通过OpenAPI接口触发 |

---

## 相关文档

- [流水线执行 API](./06-execute-pipeline-api.md) - 执行、取消、查询执行记录
- [字段枚举汇总](./05-field-enums.md) - 所有枚举值
