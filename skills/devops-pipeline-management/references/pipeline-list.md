---
name: pipeline-list
description: 分页查询流水线执行记录。当用户需要查看流水线执行记录列表、历史执行记录时使用此功能。

触发关键词："执行记录"、"历史记录"、"运行记录"、"查看执行"、"pipeline list"
---

# 流水线执行记录列表查询

> ⚠️ **大模型执行约束（必须严格遵守）**
>
> **执行铁律**：
> 1. **API调用规范**：任何发生 API 调用的，**必须实际调用 Python 脚本的 API 功能**，禁止模拟或跳过

## 功能描述

分页查询流水线执行记录，支持按状态、代码源等条件筛选。可查看流水线的历史执行情况，包括执行状态、触发人、执行时间等信息。

## 使用方式

```bash
python -m scripts/main list <pipeline_id> [options]
```

## API接口

- **路径**: GET /rest/openapi/pipeline/queryPipelineWorkPage
- **方法**: GET

## 请求参数

### Query 参数

| 字段名 | 类型 | 必填 | 描述 | 示例值 |
|--------|------|------|------|--------|
| pipelineId | String | 是 | 流水线ID | `pipe-abc123` |
| type | String | 否 | 搜索数据类型 | `status` |
| keyword | String | 否 | 搜索关键字 | `success` |
| codeSourceParams | List | 否 | 代码源参数 | JSON序列化字符串 |
| artifactParams | List | 否 | 制品参数 | JSON序列化字符串 |
| pageNum | Integer | 否 | 页码（默认1） | `1` |
| pageSize | Integer | 否 | 每页大小（默认10） | `10` |

### 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| pipeline_id | 流水线ID（必填） | `pipe-abc123` |
| --page-num | 页码 | `--page-num 1` |
| --page-size | 每页大小 | `--page-size 20` |
| --type | 搜索类型 | `--type status` |
| --keyword | 搜索关键字 | `--keyword success` |

### CodeSourceParam 字段说明

用于按代码源筛选执行记录。

| 字段名 | 类型 | 描述 | 示例值 |
|--------|------|------|--------|
| sourceType | String | 源类型 | `code` |
| repoType | String | 仓库类型 | `gitlab` |
| repoUrl | String | 仓库URL | `https://gitlab.example.com/repo.git` |
| refsType | String | 引用类型（branch/tag） | `branch` |
| workPath | String | 工作路径 | `./` |
| completeFilterFlag | Boolean | 完整过滤标志 | `false` |

### ArtifactParam 字段说明

用于按制品参数筛选执行记录。

| 字段名 | 类型 | 描述 | 示例值 |
|--------|------|------|--------|
| sourceType | String | 源类型 | `package` |
| repoType | String | 仓库类型 | `harbor` |
| normalAddress | String | 普通制品地址 | - |
| normalArtifactName | String | 普通制品名称 | - |
| packageType | String | 包类型 | `docker` |
| imageName | String | 镜像名称 | `myapp` |
| workPath | String | 工作路径 | `./` |
| completeFilterFlag | Boolean | 完整过滤标志 | `false` |

## 请求示例

**命令行 - 基础查询**:
```bash
python -m scripts/main list pipe-abc123
```

**命令行 - 分页查询**:
```bash
python -m scripts/main list pipe-abc123 --page-num 1 --page-size 20
```

**命令行 - 按状态搜索**:
```bash
python -m scripts/main list pipe-abc123 --type status --keyword success
```

**API - 基础查询**:
```
GET /rest/openapi/pipeline/queryPipelineWorkPage?pipelineId=pipe-abc123
```

**API - 分页查询**:
```
GET /rest/openapi/pipeline/queryPipelineWorkPage?pipelineId=pipe-abc123&pageNum=1&pageSize=20
```

**API - 带关键字搜索**:
```
GET /rest/openapi/pipeline/queryPipelineWorkPage?pipelineId=pipe-abc123&type=status&keyword=success
```

## 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 100,
    "size": 10,
    "current": 1,
    "pages": 10,
    "records": [
      {
        "id": 10001,
        "spaceId": 1001,
        "runTimes": 10,
        "pipelineId": "pipe-abc123",
        "pipelineName": "订单服务构建流水线",
        "pipelineStatus": "100004",
        "pipelineStatusName": "成功",
        "pipelineStageInfo": "[{\"stage\": \"build\", \"status\": \"success\"}]",
        "jenkinsJobId": "job-001",
        "jenkinsJobName": "order-service-build",
        "jenkinsJobUrl": "http://jenkins.example.com/job/order-service-build/10/",
        "runSources": "[{\"sourceId\": \"src-001\", \"branch\": \"master\"}]",
        "runRemark": "日常构建",
        "endTime": "2025-01-15T10:30:00",
        "duration": 300,
        "pipelineParams": "{}",
        "triggerMode": 0,
        "triggerModeName": "手动触发",
        "triggerUser": "zhangsan",
        "triggerParams": "{}",
        "createTime": "2025-01-15T10:25:00",
        "creator": "zhangsan",
        "creatorName": "张三",
        "taskStatusParam": "{}",
        "reRunFlag": 0,
        "fromPipelineLogId": null,
        "runFromPipelineLogId": null
      },
      {
        "id": 10002,
        "spaceId": 1001,
        "runTimes": 11,
        "pipelineId": "pipe-abc123",
        "pipelineName": "订单服务构建流水线",
        "pipelineStatus": "100005",
        "pipelineStatusName": "失败",
        "runRemark": "测试构建",
        "endTime": "2025-01-14T16:20:00",
        "duration": 120,
        "triggerMode": 0,
        "triggerModeName": "手动触发",
        "triggerUser": "lisi",
        "createTime": "2025-01-14T16:18:00",
        "creator": "lisi",
        "creatorName": "李四",
        "reRunFlag": 0
      }
    ]
  },
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Page<PipelineWorkVO> 字段说明

| 字段名 | 类型 | 描述 |
|--------|------|------|
| total | Long | 总记录数 |
| size | Long | 每页大小 |
| current | Long | 当前页码 |
| pages | Long | 总页数 |
| records | List | 执行记录列表（PipelineWorkVO） |

## PipelineWorkVO 字段说明

| 字段名 | 类型 | 描述 | 示例值 |
|--------|------|------|--------|
| id | Long | 主键ID（执行记录ID，用于取消/查看详情） | `10001` |
| spaceId | Long | 空间ID | `1001` |
| runTimes | Long | 流水线运行次数 | `10` |
| pipelineId | String | 流水线ID | `pipe-abc123` |
| pipelineName | String | 流水线名称 | `订单服务构建流水线` |
| pipelineStatus | String | 流水线状态编码 | `100004` |
| pipelineStatusName | String | 流水线状态名称 | `成功` |
| pipelineStageInfo | String | 流水线阶段信息和状态 | JSON字符串 |
| jenkinsJobId | String | 构建任务ID | `job-001` |
| jenkinsJobName | String | 构建任务名称 | `order-service-build` |
| jenkinsJobUrl | String | 构建任务URL | `http://jenkins/job/...` |
| runSources | String | 执行时选择的代码源 | JSON字符串 |
| runRemark | String | 执行备注 | `日常构建` |
| endTime | LocalDateTime | 运行结束时间 | `2025-01-15T10:30:00` |
| duration | Long | 持续时间（秒） | `300` |
| pipelineParams | String | 流水线参数 | JSON字符串 |
| triggerMode | Integer | 触发执行方式（0手动/1定时） | `0` |
| triggerModeName | String | 触发方式名称 | `手动触发` |
| triggerUser | String | 触发人 | `zhangsan` |
| triggerParams | String | 触发参数 | JSON字符串 |
| createTime | LocalDateTime | 创建时间 | `2025-01-15T10:25:00` |
| creator | String | 创建人（域账号） | `zhangsan` |
| creatorName | String | 创建人（中文姓名） | `张三` |
| taskStatusParam | String | 流水线任务状态信息 | JSON字符串 |
| reRunFlag | Integer | 重新执行标志（0-否，1-是） | `0` |
| fromPipelineLogId | Long | 历史流水线执行源记录信息 | `null` |
| runFromPipelineLogId | Long | 重新执行的触发流水线ID | `null` |

## 流水线状态说明

| 状态编码 | 状态名称 | 说明 |
|----------|----------|------|
| 100000 | 未执行 | 初始状态 |
| 100001 | 等待中 | 等待执行资源 |
| 100002 | 执行中 | 流水线正在运行 |
| 100004 | 成功 | 所有任务执行成功 |
| 100005 | 失败 | 至少一个任务失败 |
| 100006 | 已取消 | 用户手动取消 |

## 触发方式说明

| 触发方式编码 | 触发方式名称 | 说明 |
|-------------|-------------|------|
| 0 | 手动触发 | 用户通过界面或API手动执行 |
| 1 | 定时触发 | 通过定时任务自动执行 |

## 错误码

| 错误码 | 说明 |
|-------|------|
| 0 | 成功 |
| -1 | 通用失败（具体信息见message） |
| 401 | 无API访问权限 |
| 404 | 流水线不存在 |
| 429 | 请求过于频繁（触发限流） |

## 典型使用场景

### 1. 查看流水线执行历史

```bash
# 查看最近10条执行记录
python -m scripts/main list pipe-abc123

# 查看更多记录
python -m scripts/main list pipe-abc123 --page-size 50
```

### 2. 查找失败的执行记录

```bash
# 按状态搜索失败记录
python -m scripts/main list pipe-abc123 --type status --keyword failed

# 或使用状态编码
python -m scripts/main list pipe-abc123 --type status --keyword 100005
```

### 3. 获取执行记录ID用于后续操作

```bash
# 查询执行记录列表，获取id字段
python -m scripts/main list pipe-abc123

# 使用返回的id查看执行详情
python -m scripts/main run-detail 10001

# 使用返回的id取消正在执行的流水线
python -m scripts/main cancel 10001
```

### 4. 分页浏览执行记录

```bash
# 查看第一页
python -m scripts/main list pipe-abc123 --page-num 1 --page-size 20

# 查看第二页
python -m scripts/main list pipe-abc123 --page-num 2 --page-size 20
```

## 注意事项

1. **pipelineId为必填参数**，可通过 `pipelines` 命令查询流水线列表获取
2. **id字段（执行记录ID）** 是后续操作的关键参数：
   - 用于 `run-detail` 命令查看执行详情
   - 用于 `cancel` 命令取消正在执行的流水线
   - 用于 `run` 命令的 `--re-run` 重新执行
3. **codeSourceParams和artifactParams** 需要JSON序列化后传递
4. **duration单位为秒**，可根据需要转换为分钟或小时展示
5. 默认分页大小为10，可根据需要调整 `--page-size` 参数
6. PipelineWorkVO详细字段说明参见 [pipeline-run-detail.md](pipeline-run-detail.md)
