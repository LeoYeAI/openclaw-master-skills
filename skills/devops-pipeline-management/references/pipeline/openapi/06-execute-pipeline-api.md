# 流水线执行 API

本文档定义流水线执行相关的 OpenAPI 接口，用于 Skill 训练场景。

> **更新日期**: 2026-03-15

---

## 接口概览

| 序号 | 接口名称 | 请求方法 | 接口路径 |
|------|----------|----------|----------|
| 1 | 手动执行流水线 | POST | /runByManual |
| 2 | 取消流水线 | POST | /cancel |
| 3 | 分页查询流水线执行记录 | GET | /queryPipelineWorkPage |
| 4 | 查询流水线执行记录详情 | GET | /getPipelineWorkById |
| 5 | 查询最近流水线执行记录 | POST | /queryLastestSelectedValueByField |
| 6 | 查询流水线控制台日志 | GET | /getJenkinsConsoleLog |

---

## 1. 执行流水线（手动触发）

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/runByManual` |
| 请求方法 | POST |
| 接口描述 | 触发流水线手动执行（OpenAPI触发类型为6） |

### 请求头

| 请求头 | 必填 | 描述 |
|--------|------|------|
| CP-GW-SUB | 条件 | 当前用户域账号（优先获取） |
| X-User-Account | 条件 | 当前用户域账号（CP-GW-SUB为空时备选） |

### 最小请求体

```json
{
  "pipelineId": "pipe-001"
}
```

### 完整请求体

```json
{
  "pipelineId": "pipe-001",
  "runRemark": "手动执行说明",
  "autoFillRunConfig": true,
  "reRunFlag": 0,
  "fromPipelineLogId": 10001,
  "runFromPipelineLogId": 10001,
  "versionId": "v1.0.0",
  "planId": 1001,
  "runSources": [
    {
      "id": "source-001",
      "name": "前端代码库",
      "shortName": "前端代码库",
      "refsType": "BRANCH",
      "refsTypeValue": "master",
      "data": {
        "sourceType": "code",
        "repoType": "GITEE",
        "refsType": "BRANCH",
        "repoUrl": "https://code.iflytek.com/team/frontend-app",
        "branch": "master",
        "workPath": "frontend-app_abc1",
        "commitId": "abc123",
        "commitMessage": "feat: add new feature"
      }
    },
    {
      "id": "source-002",
      "name": "Docker镜像",
      "shortName": "Docker镜像",
      "data": {
        "sourceType": "package",
        "repoType": "IPACKAGE",
        "packageType": "DOCKER",
        "workPath": "my-image_xyz2",
        "imageName": "my-image",
        "defaultTag": "latest",
        "imageAddress": "registry.iflytek.com/project/my-image:latest"
      }
    }
  ],
  "customParameterRuns": [],
  "taskDataList": []
}
```

### 响应

```json
{
  "code": 0,
  "message": "success",
  "data": 10001,
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**data 字段**: 流水线执行记录ID (Long)

---

## 顶层字段说明

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `pipelineId` | string | 是 | 流水线ID |
| `runRemark` | string | 否 | 执行备注说明 |
| `autoFillRunConfig` | boolean | 否 | 是否自动填充配置（使用上次执行记录） |
| `reRunFlag` | integer | 否 | 重新执行流水线（0-否/1-重新部署） |
| `fromPipelineLogId` | Long | 否 | 历史流水线执行记录信息 |
| `runFromPipelineLogId` | Long | 否 | 重新执行的触发流水线记录ID |
| `versionId` | String | 否 | 产研平台发布版本号 |
| `planId` | Long | 否 | 产研平台提测版本号 |
| `runSources` | array | 否 | 源配置列表（代码源+制品源） |
| `customParameterRuns` | array | 否 | 自定义运行参数 |
| `downloadDependInfo` | object | 否 | 下载依赖前置信息 |
| `taskDataList` | array | 否 | 指定执行的任务列表 |

---

## customParameterRuns 结构

### PipelineCustomParameterRunDto

```json
{
  "customParameterId": 1001,
  "name": "ENVIRONMENT",
  "type": "string",
  "defaultValue": "production",
  "enumValue": "dev,test,prod",
  "privateKey": false,
  "runSet": true,
  "description": "部署环境",
  "reSet": false
}
```

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `customParameterId` | Long | 否 | 自定义参数ID |
| `name` | String | 是 | 自定义参数名称 |
| `type` | String | 否 | 参数类型（string/auto/enum） |
| `defaultValue` | String | 否 | 默认值 |
| `enumValue` | String | 否 | 枚举选项 |
| `privateKey` | Boolean | 否 | 是否私密参数 |
| `runSet` | Boolean | 否 | 执行时设置 |
| `description` | String | 否 | 描述 |
| `reSet` | Boolean | 否 | 是否重置 |

---

## 2. 取消流水线

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/cancel` |
| 请求方法 | POST |
| 接口描述 | 取消正在执行的流水线 |

### 请求体

```json
{
  "pipelineLogId": 10001
}
```

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

## 3. 分页查询流水线执行记录

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/queryPipelineWorkPage` |
| 请求方法 | GET |
| 接口描述 | 分页查询流水线执行记录 |

### Query 参数

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| pipelineId | String | 是 | 流水线ID |
| type | String | 否 | 搜索数据类型 |
| keyword | String | 否 | 搜索关键字 |
| pageNum | Integer | 否 | 页码 |
| pageSize | Integer | 否 | 每页大小 |

### 请求示例

```
GET /rest/openapi/pipeline/queryPipelineWorkPage?pipelineId=pipe-abc123&pageNum=1&pageSize=10
```

### 响应 PipelineWorkVO 列表

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
        "id": 10001,
        "spaceId": 1001,
        "runTimes": 10,
        "pipelineId": "pipe-abc123",
        "pipelineName": "订单服务构建流水线",
        "pipelineStatus": "100004",
        "pipelineStatusName": "成功",
        "runRemark": "日常构建",
        "endTime": "2025-01-15T10:30:00",
        "duration": 300,
        "triggerMode": 0,
        "triggerModeName": "手动触发",
        "triggerUser": "zhangsan",
        "createTime": "2025-01-15T10:25:00",
        "creator": "zhangsan",
        "creatorName": "张三",
        "reRunFlag": 0
      }
    ]
  }
}
```

---

## 4. 查询流水线执行记录详情

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/getPipelineWorkById` |
| 请求方法 | GET |
| 接口描述 | 根据执行记录ID查询流水线执行详情 |

### 参数

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `pipelineLogId` | Long | 是 | 执行记录ID |

### 请求示例

```
GET /rest/openapi/pipeline/getPipelineWorkById?pipelineLogId=10001
```

### 响应 PipelineWorkVO

```json
{
  "code": 0,
  "data": {
    "id": 10001,
    "spaceId": 1001,
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
    "triggerMode": 0,
    "triggerModeName": "手动触发",
    "triggerUser": "zhangsan",
    "createTime": "2025-01-15T10:25:00",
    "creator": "zhangsan",
    "creatorName": "张三",
    "reRunFlag": 0,
    "fromPipelineLogId": null,
    "runFromPipelineLogId": null
  }
}
```

---

## 5. 查询流水线控制台日志

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

### 字段说明

| 字段 | 类型 | 说明 |
|-----|------|------|
| `logContent` | String | 日志内容 |
| `hasMore` | Boolean | 是否有更多日志 |
| `nextStart` | Integer | 下次读取的起始位置 |
| `isCompleted` | Boolean | 是否已完成 |

---

## PipelineWorkVO 字段说明

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | Long | 主键ID |
| spaceId | Long | 空间ID |
| runTimes | Long | 流水线运行次数 |
| pipelineId | String | 流水线ID |
| pipelineName | String | 流水线名称 |
| pipelineStatus | String | 流水线状态编码 |
| pipelineStatusName | String | 流水线状态名称 |
| pipelineStageInfo | String | 流水线阶段信息和状态（JSON字符串） |
| jenkinsJobId | String | 构建任务ID |
| jenkinsJobName | String | 构建任务名称 |
| jenkinsJobUrl | String | 构建任务URL |
| runSources | String | 执行时选择的代码源（JSON字符串） |
| runRemark | String | 执行备注 |
| endTime | LocalDateTime | 运行结束时间 |
| duration | Long | 持续时间（秒） |
| pipelineParams | String | 流水线参数（JSON字符串） |
| triggerMode | Integer | 触发执行方式（0手动/1定时/6 OpenAPI） |
| triggerModeName | String | 触发方式名称 |
| triggerUser | String | 触发人 |
| triggerParams | String | 触发参数 |
| createTime | LocalDateTime | 创建时间 |
| creator | String | 创建人（域账号） |
| creatorName | String | 创建人（中文姓名） |
| taskStatusParam | String | 流水线任务状态信息 |
| reRunFlag | Integer | 重新执行标志 |
| fromPipelineLogId | Long | 历史流水线执行源记录信息 |
| runFromPipelineLogId | Long | 重新执行的触发流水线ID |

---

## 流水线状态码

| 状态编码 | 状态名称 | 说明 |
|----------|----------|------|
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

## taskDataList 结构（指定执行节点）

当需要指定执行流水线中的部分任务时使用。taskDataList不能为空数组。

### 任务节点结构

```json
{
  "id": "task-001",
  "name": "Maven构建",
  "data": {
    "jobType": "MavenBuild",
    "taskCategory": "Build"
  }
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `id` | string | 是 | 任务ID |
| `name` | string | 是 | 任务名称 |
| `data` | object | 否 | 任务配置数据 |
| `data.jobType` | string | 否 | 任务类型 |
| `data.taskCategory` | string | 否 | 任务分类 |

---

### 完整请求示例（指定执行节点）

```json
{
  "pipelineId": "pipe-001",
  "runSources": [...],
  "taskDataList": [
    {
      "id": "task-maven-001",
      "name": "Maven构建",
      "data": {
        "jobType": "MavenBuild",
        "taskCategory": "Build"
      }
    },
    {
      "id": "task-sonar-001",
      "name": "代码扫描",
      "data": {
        "jobType": "SonarQube",
        "taskCategory": "CodeScanner"
      }
    }
  ]
}
```

---

### 获取可选任务列表

从流水线配置中获取所有可执行的任务节点：

```python
def get_executable_tasks(pipeline_data):
    """获取流水线中所有可执行的任务"""
    tasks = []

    for stage in pipeline_data.get('stages', []):
        stage_name = stage.get('name', '')

        for step in stage.get('steps', []):
            step_name = step.get('name', '')
            driven = step.get('driven', 0)  # 0: 串行, 1: 并行

            for task in step.get('tasks', []):
                # 跳过"添加任务"按钮节点
                if task.get('nodeType') == 'custom-add-task-node':
                    continue

                tasks.append({
                    'id': task.get('id'),
                    'name': task.get('name'),
                    'stage': stage_name,
                    'step': step_name,
                    'driven': driven,
                    'nodeType': task.get('nodeType')
                })

    return tasks
```

### 流水线结构参考

```
pipeline.stages[]
├── id: "stage-001"
├── name: "构建阶段"
└── steps[]
    ├── id: "step-001"
    ├── name: "构建步骤"
    ├── driven: 0  # 串行
    └── tasks[]
        ├── id: "task-001"
        ├── name: "Maven构建"
        └── nodeType: "custom-task-node"
```

### 执行规则

| 场景 | taskDataList | 行为 |
|-----|-------------|------|
| 执行全部 | 包含所有任务 | 执行流水线中所有任务 |
| 执行部分 | 包含部分任务 | 只执行指定的任务及其依赖 |

### 注意事项

1. **依赖任务**：如果选择了中间的任务，其依赖的前置任务也会被执行
2. **顺序**：任务会按照流水线中的顺序执行（串行/并行由 step.driven 决定）
3. **Stage 级别**：也可以选择只执行某个 Stage 内的所有任务

---

## runSources 结构

### 代码源 (sourceType: code)

```json
{
  "id": "source-001",
  "name": "代码库名称",
  "shortName": "代码库名称",
  "refsType": "BRANCH",
  "refsTypeValue": "master",
  "data": {
    "sourceType": "code",
    "repoType": "GITEE",
    "refsType": "BRANCH",
    "repoUrl": "https://code.iflytek.com/team/repo",
    "branch": "master",
    "workPath": "repo_abc1",
    "commitId": "commit-sha",
    "commitMessage": "commit message"
  }
}
```

#### 代码源字段说明

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `id` | string | 是 | 源ID（来自流水线配置） |
| `name` | string | 是 | 源名称 |
| `shortName` | string | 是 | 简短名称（通常与name相同） |
| `refsType` | string | 是 | `BRANCH` 或 `TAG` |
| `refsTypeValue` | string | 是 | 分支名或标签名 |
| `data.sourceType` | string | 是 | 固定为 `code` |
| `data.repoType` | string | 是 | `GITEE` / `GITLAB` / `FLYCODE` |
| `data.repoUrl` | string | 是 | 仓库地址 |
| `data.branch` | string | 是 | 分支/标签名 |
| `data.workPath` | string | 是 | 工作目录 |
| `data.commitId` | string | 否 | 提交ID |
| `data.commitMessage` | string | 否 | 提交信息 |

---

### 制品源 (sourceType: package)

#### Docker 镜像

```json
{
  "id": "source-002",
  "name": "镜像名称",
  "shortName": "镜像名称",
  "data": {
    "sourceType": "package",
    "repoType": "IPACKAGE",
    "packageType": "DOCKER",
    "workPath": "image_xyz2",
    "packageName": "Artifactory",
    "firstDir": "project",
    "imageName": "my-image",
    "defaultTag": "v1.0.0",
    "imageAddress": "registry.iflytek.com/project/my-image:v1.0.0"
  }
}
```

#### 普通制品

```json
{
  "id": "source-003",
  "name": "制品名称",
  "shortName": "制品名称",
  "data": {
    "sourceType": "package",
    "repoType": "IPACKAGE",
    "packageType": "NORMAL",
    "workPath": "Artifact_xyz2",
    "normalArtifactName": "my-artifact",
    "fullPath": "project/normal/my-artifact/v1.0.0",
    "normalAddress": "registry.iflytek.com/project/normal/my-artifact/v1.0.0",
    "defaultTag": "v1.0.0"
  }
}
```

#### 制品源字段说明

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `data.sourceType` | string | 是 | 固定为 `package` |
| `data.packageType` | string | 是 | `DOCKER` 或 `NORMAL` |
| `data.workPath` | string | 是 | 工作目录 |
| `data.defaultTag` | string | 是 | 版本标签 |

**Docker 专用字段:**

| 字段 | 说明 |
|-----|------|
| `imageName` | 镜像名称 |
| `imageAddress` | 镜像完整地址 |
| `packageName` | 制品仓名称（通常为 Artifactory） |
| `firstDir` | 一级目录 |

**NORMAL 专用字段:**

| 字段 | 说明 |
|-----|------|
| `normalArtifactName` | 制品名称 |
| `fullPath` | 完整路径 |
| `normalAddress` | 制品地址 |

---

## runSources 数据转换逻辑

本节说明如何将流水线配置中的 `sources` 转换为执行时的 `runSources`。

### 输入数据（流水线配置）

```json
{
  "pipeline": {
    "sources": [
      {
        "id": "source-001",
        "name": "前端代码库",
        "nodeType": "custom-source-node",
        "data": {
          "sourceType": "code",
          "repoType": "GITEE",
          "refsType": "BRANCH",
          "repoUrl": "https://code.iflytek.com/team/frontend-app",
          "branch": "master",
          "workPath": "frontend-app_abc1"
        }
      },
      {
        "id": "source-002",
        "name": "Docker镜像",
        "nodeType": "custom-source-node",
        "data": {
          "sourceType": "package",
          "repoType": "IPACKAGE",
          "packageType": "DOCKER",
          "workPath": "my-image_xyz2",
          "imageName": "my-image",
          "defaultTag": "latest"
        }
      }
    ]
  },
  "taskDataList": [
    {
      "id": "task-001",
      "data": {
        "workPath": "frontend-app_abc1"
      }
    }
  ]
}
```

### 转换规则

#### 1. 过滤有效源

只保留在 `taskDataList` 中被引用的源：

```python
def filter_valid_sources(sources, task_data_list):
    """过滤出被任务引用的源"""
    used_work_paths = {task['data']['workPath'] for task in task_data_list}
    return [s for s in sources if s['data']['workPath'] in used_work_paths]
```

#### 2. 代码源转换

```python
def transform_code_source(source):
    """将代码源配置转换为 runSource 格式"""
    data = source['data']

    return {
        "id": source['id'],
        "name": source['name'],
        "shortName": source['name'],  # 通常与 name 相同
        "refsType": data['refsType'],      # BRANCH 或 TAG
        "refsTypeValue": data['branch'],   # 分支名或标签名
        "data": {
            "sourceType": "code",
            "repoType": data['repoType'],
            "refsType": data['refsType'],
            "repoUrl": data['repoUrl'],
            "branch": data['branch'],
            "workPath": data['workPath'],
            "commitId": data.get('commitId', ''),
            "commitMessage": data.get('commitMessage', '')
        }
    }
```

#### 3. Docker 制品源转换

```python
def transform_docker_package_source(source):
    """将 Docker 制品源转换为 runSource 格式"""
    data = source['data']

    return {
        "id": source['id'],
        "name": data.get('imageName', source['name']),
        "shortName": data.get('imageName', source['name']),
        "data": {
            "sourceType": "package",
            "repoType": data['repoType'],
            "packageType": "DOCKER",
            "workPath": data['workPath'],
            "packageName": data.get('packageName', 'Artifactory'),
            "firstDir": data.get('firstDir', ''),
            "imageName": data.get('imageName', ''),
            "defaultTag": data['defaultTag'],
            "imageAddress": data.get('imageAddress', '')
        }
    }
```

#### 4. 普通制品源转换

```python
def transform_normal_package_source(source):
    """将普通制品源转换为 runSource 格式"""
    data = source['data']

    # 需要替换路径中的版本号
    version = data['defaultTag']
    full_path = replace_version_in_path(data.get('fullPath', ''), version)
    normal_address = replace_version_in_path(data.get('normalAddress', ''), version)

    return {
        "id": source['id'],
        "name": data.get('normalArtifactName', source['name']),
        "shortName": data.get('normalArtifactName', source['name']),
        "data": {
            "sourceType": "package",
            "repoType": data['repoType'],
            "packageType": "NORMAL",
            "workPath": data['workPath'],
            "normalArtifactName": data.get('normalArtifactName', ''),
            "fullPath": full_path,
            "normalAddress": normal_address,
            "ipackagePath": data.get('ipackagePath', ''),
            "defaultTag": version
        }
    }

def replace_version_in_path(path, version):
    """替换路径中的版本号"""
    # 路径格式: project/type/name/{version}
    # 将最后一个路径段替换为版本号
    if not path:
        return path
    parts = path.rstrip('/').split('/')
    if len(parts) > 0:
        parts[-1] = version
    return '/'.join(parts)
```

#### 5. 保持原始顺序

```python
def order_run_sources(run_sources, original_sources):
    """按照原始 sources 的顺序重排 runSources"""
    # 创建 workPath 到 runSource 的映射
    run_source_map = {
        rs['data']['workPath']: rs
        for rs in run_sources
    }

    # 按原始顺序重排
    ordered = []
    for source in original_sources:
        work_path = source['data']['workPath']
        if work_path in run_source_map:
            ordered.append(run_source_map[work_path])

    return ordered
```

### 完整转换函数

```python
def build_run_sources(pipeline_data, task_data_list):
    """
    构建执行流水线所需的 runSources

    Args:
        pipeline_data: 流水线配置 (包含 sources)
        task_data_list: 任务列表 (用于过滤有效源)

    Returns:
        list: runSources 列表
    """
    sources = pipeline_data.get('sources', [])
    run_sources = []

    # 1. 获取被引用的 workPath
    used_work_paths = {
        task['data'].get('workPath')
        for task in task_data_list
        if task['data'].get('workPath')
    }

    # 2. 转换每个源
    for source in sources:
        work_path = source['data'].get('workPath')

        # 过滤未被引用的源
        if work_path not in used_work_paths:
            continue

        source_type = source['data'].get('sourceType')

        if source_type == 'code':
            run_sources.append(transform_code_source(source))
        elif source_type == 'package':
            package_type = source['data'].get('packageType', 'DOCKER')
            if package_type == 'DOCKER':
                run_sources.append(transform_docker_package_source(source))
            else:
                run_sources.append(transform_normal_package_source(source))

    # 3. 保持原始顺序
    return order_run_sources(run_sources, sources)
```

### 转换结果示例

```json
{
  "pipelineId": "pipe-001",
  "runSources": [
    {
      "id": "source-001",
      "name": "前端代码库",
      "shortName": "前端代码库",
      "refsType": "BRANCH",
      "refsTypeValue": "master",
      "data": {
        "sourceType": "code",
        "repoType": "GITEE",
        "refsType": "BRANCH",
        "repoUrl": "https://code.iflytek.com/team/frontend-app",
        "branch": "master",
        "workPath": "frontend-app_abc1",
        "commitId": "",
        "commitMessage": ""
      }
    },
    {
      "id": "source-002",
      "name": "my-image",
      "shortName": "my-image",
      "data": {
        "sourceType": "package",
        "repoType": "IPACKAGE",
        "packageType": "DOCKER",
        "workPath": "my-image_xyz2",
        "packageName": "Artifactory",
        "firstDir": "",
        "imageName": "my-image",
        "defaultTag": "latest",
        "imageAddress": ""
      }
    }
  ]
}
```

### 更新分支/版本的转换

当用户选择不同的分支或版本时：

```python
def update_run_source_branch(run_source, new_branch, new_refs_type=None):
    """更新代码源的分支"""
    run_source['refsTypeValue'] = new_branch
    run_source['data']['branch'] = new_branch

    if new_refs_type:
        run_source['refsType'] = new_refs_type
        run_source['data']['refsType'] = new_refs_type

    # 清空 commit 信息（需要重新获取）
    run_source['data']['commitId'] = ''
    run_source['data']['commitMessage'] = ''

    return run_source

def update_run_source_version(run_source, new_version):
    """更新制品源的版本"""
    run_source['data']['defaultTag'] = new_version

    # 更新相关地址
    if run_source['data']['packageType'] == 'DOCKER':
        # 更新镜像地址: registry/path/image:{tag}
        old_address = run_source['data'].get('imageAddress', '')
        if old_address and ':' in old_address:
            base = old_address.rsplit(':', 1)[0]
            run_source['data']['imageAddress'] = f"{base}:{new_version}"
    else:
        # 更新普通制品路径
        run_source['data']['fullPath'] = replace_version_in_path(
            run_source['data'].get('fullPath', ''), new_version
        )
        run_source['data']['normalAddress'] = replace_version_in_path(
            run_source['data'].get('normalAddress', ''), new_version
        )

    return run_source
```

---

## 辅助 API

### 获取最近执行的分支/版本

用于自动填充上次执行配置。

**请求**
```
POST /rest/openapi/pipeline/queryLastestSelectedValueByField
```

**请求体**
```json
{
  "pipelineId": "pipe-001",
  "codeSourceParams": [
    {
      "sourceType": "code",
      "refsType": "BRANCH",
      "repoType": "GITEE",
      "repoUrl": "https://code.iflytek.com/team/repo",
      "workPath": "repo_abc1"
    }
  ],
  "artifactParams": [
    {
      "sourceType": "package",
      "repoType": "IPACKAGE",
      "imageName": "my-image",
      "workPath": "image_xyz2",
      "packageType": "DOCKER"
    }
  ]
}
```

**响应**
```json
{
  "code": "200",
  "data": {
    "codeSourceResult": [
      {
        "codeSourceParam": {
          "repoType": "GITEE",
          "refsType": "BRANCH",
          "repoUrl": "https://code.iflytek.com/team/repo",
          "workPath": "repo_abc1"
        },
        "branchOrTag": "master",
        "lastestCodeSourceParam": {
          "refsType": "BRANCH"
        }
      }
    ],
    "artifactResult": [
      {
        "artifactParam": {
          "workPath": "image_xyz2"
        },
        "lastestArtifactVersion": "v1.0.0"
      }
    ]
  }
}
```

---

### 获取分支/标签列表

**请求**
```
POST /rest/openapi/pipeline/getRepoBranchAndTagList
```

**请求体**
```json
[
  {
    "refsType": "BRANCH",
    "repoType": "GITEE",
    "repoUrl": "https://code.iflytek.com/team/repo",
    "search": "master",
    "currentPage": 1,
    "pageSize": 20
  }
]
```

**响应**
```json
{
  "code": "200",
  "data": [
    {
      "branchListVO": {
        "branchVOPage": {
          "data": [
            {
              "name": "master",
              "commitId": "abc123"
            },
            {
              "name": "develop",
              "commitId": "def456"
            }
          ]
        }
      },
      "tagListVO": {
        "tagVOPage": {
          "data": []
        }
      }
    }
  ]
}
```

---

### 获取提交详情（标签）

**请求**
```
POST /rest/openapi/pipeline/queryCommitDetail
```

**请求体**
```json
{
  "repoType": "GITEE",
  "repoUrl": "https://code.iflytek.com/team/repo",
  "commitId": "abc123"
}
```

---

### 获取提交列表（分支）

**请求**
```
POST /rest/openapi/pipeline/queryRepoCommitList
```

**请求体**
```json
{
  "repoType": "GITEE",
  "repoUrl": "https://code.iflytek.com/team/repo",
  "refsTypeValue": "master"
}
```

---

### 获取镜像标签列表

**请求**
```
GET /rest/openapi/pipeline/imageTags?imageName={imageName}&repoType=IPACKAGE
```

---

### 获取普通制品版本列表

**请求**
```
GET /rest/openapi/pipeline/packageVersions?artifactName={artifactName}&repoType=IPACKAGE
```

---

## 执行流程

### 简化流程（推荐）

```
1. 获取流水线详情 → 得到 sources 配置
       ↓
2. 直接使用默认分支/版本执行
       ↓
3. POST /runByManual
```

### 完整流程（交互式）

```
1. 获取流水线详情 → 得到 sources + stages 配置
       ↓
2. 获取上次执行配置（可选）
   POST /queryLastestSelectedValueByField
       ↓
3. 获取分支/标签列表（可选）
   POST /getRepoBranchAndTagList
       ↓
4. 用户选择分支/标签/版本
       ↓
5. 从流水线配置中解析可选任务节点列表
       ↓
6. 用户选择要执行的任务节点（可多选）
       ↓
7. 组装 runSources + taskDataList 数据
       ↓
8. POST /runByManual
```

#### 5.1 获取可选任务节点列表

从流水线详情中解析所有可执行的任务节点：

```python
def get_executable_tasks(pipeline_data):
    """
    从流水线配置中获取所有可执行的任务节点

    返回: [
      {
        "id": "task-001",
        "name": "Maven构建",
        "stageName": "构建阶段",
        "stepName": "构建步骤",
        "driven": "串行",
        "jobType": "MavenBuild"
      },
      ...
    ]
    """
    tasks = []

    for stage in pipeline_data.get('stages', []):
        stage_name = stage.get('name', '')

        for step in stage.get('steps', []):
            step_name = step.get('name', '')
            driven = '并行' if step.get('driven') == 1 else '串行'

            for task in step.get('tasks', []):
                # 跳过"添加任务"按钮节点
                if task.get('nodeType') == 'custom-add-task-node':
                    continue

                # 获取任务配置信息
                task_id = task.get('id')
                task_name = task.get('name')

                # 从 taskDataList 中查找对应的 jobType
                job_type = ''
                for td in pipeline_data.get('taskDataList', []):
                    if td.get('id') == task_id:
                        job_type = td.get('data', {}).get('jobType', '')
                        break

                tasks.append({
                    'id': task_id,
                    'name': task_name,
                    'stageName': stage_name,
                    'stepName': step_name,
                    'driven': driven,
                    'jobType': job_type
                })

    return tasks
```

#### 5.2 任务节点选择逻辑

用户可以选择执行全部任务或部分任务：

| 场景 | taskDataList | 行为 |
|-----|-------------|------|
| 执行全部 | 空数组 `[]` 或包含所有任务 | 执行流水线中所有任务 |
| 执行部分 | 包含用户选择的任务ID | 只执行指定任务及其依赖 |

**注意**：
- 如果选择了中间的任务，其依赖的前置任务也会自动被执行
- 任务会按照流水线中的顺序执行（串行/并行由 step.driven 决定）

#### 5.3 组装 taskDataList

根据用户选择的任务，组装 taskDataList：

```python
def build_task_data_list(selected_task_ids, pipeline_data):
    """
    根据用户选择的任务ID列表，构建 taskDataList

    Args:
        selected_task_ids: 用户选择的任务ID列表
        pipeline_data: 流水线完整配置

    Returns:
        list: taskDataList，用于请求体
    """
    task_data_list = []
    all_task_data = pipeline_data.get('taskDataList', [])

    # 找出所有被选中的任务及其依赖任务
    selected_set = set(selected_task_ids)
    dependent_tasks = set()

    # 简单的依赖处理：将被选中任务之前的所有任务也加入
    all_task_ids_order = []
    for stage in pipeline_data.get('stages', []):
        for step in stage.get('steps', []):
            for task in step.get('tasks', []):
                if task.get('nodeType') != 'custom-add-task-node':
                    all_task_ids_order.append(task.get('id'))

    # 找出依赖任务（被选中任务之前的所有任务）
    for task_id in selected_task_ids:
        if task_id in all_task_ids_order:
            idx = all_task_ids_order.index(task_id)
            dependent_tasks.update(all_task_ids_order[:idx])

    # 合并选择的任务和依赖任务
    final_task_ids = selected_set | dependent_tasks

    # 构建 taskDataList
    for td in all_task_data:
        if td.get('id') in final_task_ids:
            task_info = {
                'id': td.get('id'),
                'name': td.get('name', ''),
                'data': {
                    'jobType': td.get('data', {}).get('jobType', ''),
                    'taskCategory': td.get('data', {}).get('taskCategory', '')
                }
            }
            task_data_list.append(task_info)

    return task_data_list
```

#### 5.4 交互式选择示例 UI

```
┌─────────────────────────────────────────────────────────────┐
│  选择执行任务节点                                             │
├─────────────────────────────────────────────────────────────┤
│  ☐ 全选                                                      │
│                                                             │
│  ▼ 构建阶段                                                  │
│    ☑ Maven构建 (MavenBuild)                    [串行]       │
│    ☑ Docker镜像构建 (DockerBuild)             [并行]       │
│                                                             │
│  ▼ 测试阶段                                                  │
│    ☐ 单元测试 (OrderAction)                   [串行]       │
│    ☐ 集成测试 (OrderAction)                   [串行]       │
│                                                             │
│  ▼ 部署阶段                                                  │
│    ☐ SAE应用发布 (Sae)                      [串行]       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  [取消]                                    [开始执行]        │
└─────────────────────────────────────────────────────────────┘

已选择: 2 个任务（将执行: Maven构建 + Docker镜像构建 + 依赖任务）
```

---

### 请求体组装示例

根据选择的分支/版本和任务节点，完整组装请求体：

```json
{
  "pipelineId": "pipe-001",
  "runSources": [
    {
      "id": "source-001",
      "name": "代码库",
      "refsType": "BRANCH",
      "refsTypeValue": "develop",
      "data": {
        "sourceType": "code",
        "repoType": "GITEE",
        "branch": "develop",
        "workPath": "repo_abc1"
      }
    }
  ],
  "taskDataList": [
    {
      "id": "task-maven-001",
      "name": "Maven构建",
      "data": {
        "jobType": "MavenBuild",
        "taskCategory": "Build"
      }
    },
    {
      "id": "task-docker-001",
      "name": "Docker镜像构建",
      "data": {
        "jobType": "DockerBuildAndUpload",
        "taskCategory": "DockerBuild"
      }
    }
  ]
}
```

---

## 执行示例

### 示例1: 最简执行（使用默认配置）

```bash
curl -X POST /rest/openapi/pipeline/runByManual \
  -H "Content-Type: application/json" \
  -d '{
    "pipelineId": "pipe-001"
  }'
```

### 示例2: 指定分支执行

```bash
curl -X POST /rest/openapi/pipeline/runByManual \
  -H "Content-Type: application/json" \
  -d '{
    "pipelineId": "pipe-001",
    "runSources": [
      {
        "id": "source-001",
        "name": "代码库",
        "shortName": "代码库",
        "refsType": "BRANCH",
        "refsTypeValue": "develop",
        "data": {
          "sourceType": "code",
          "repoType": "GITEE",
          "refsType": "BRANCH",
          "repoUrl": "https://code.iflytek.com/team/repo",
          "branch": "develop",
          "workPath": "repo_abc1"
        }
      }
    ]
  }'
```

### 示例3: 指定制品版本执行

```bash
curl -X POST /rest/openapi/pipeline/runByManual \
  -H "Content-Type: application/json" \
  -d '{
    "pipelineId": "pipe-001",
    "runSources": [
      {
        "id": "source-002",
        "name": "Docker镜像",
        "shortName": "Docker镜像",
        "data": {
          "sourceType": "package",
          "repoType": "IPACKAGE",
          "packageType": "DOCKER",
          "workPath": "image_xyz2",
          "imageName": "my-image",
          "defaultTag": "v2.0.0",
          "imageAddress": "registry.iflytek.com/project/my-image:v2.0.0"
        }
      }
    ]
  }'
```

---

## 响应格式

### 成功响应

```json
{
  "code": "200",
  "message": "success",
  "data": {
    "buildNumber": "15",
    "buildLogId": "log-001",
    "pipelineRunId": "run-001"
  }
}
```

### 错误响应

```json
{
  "code": "400",
  "message": "分支不存在",
  "data": null
}
```

---

## 常见错误

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `分支不存在` | 指定的分支在仓库中不存在 | 检查分支名是否正确 |
| `制品版本不存在` | 指定的版本在制品库中不存在 | 检查版本号是否正确 |
| `流水线正在执行中` | 同一流水线已有运行中的任务 | 等待执行完成或取消 |
| `缺少必要参数` | pipelineId 等必填字段缺失 | 检查请求体 |

---

## 相关文档

- [流水线 API](./01-pipeline-api.md) - 创建/获取流水线
- [字段枚举汇总](./05-field-enums.md) - 所有枚举值
