---
name: pipeline-run
description: 执行流水线。当用户需要运行流水线、触发构建、启动流水线时使用此功能。

触发关键词："执行流水线"、"运行流水线"、"启动流水线"、"触发构建"

**重要**: 执行流水线时必须参考以下文档：
- **[pipeline/openapi/06-execute-pipeline-api.md](pipeline/openapi/06-execute-pipeline-api.md)** - API 接口规范（**必须参考**）
---

# 流水线执行

> ⚠️ **大模型执行约束（必须严格遵守）**
>
> **执行铁律**：
> 1. **步骤顺序固定**：必须按本文档定义的流程执行，不可跳过或调换
> 2. **API调用规范**：任何发生 API 调用的，**必须实际调用 Python 脚本的 API 功能**，禁止模拟或跳过
> 3. **taskDataList 约束**：`taskDataList` **不能为空、不能为空数组**，必须包含有效的任务数据
> 4. **runSources 转换**：必须按照 `06-execute-pipeline-api.md` 中的转换逻辑进行转换
> 5. **API 调用**：只使用 `POST /rest/openapi/pipeline/runByManual` 接口

---

## 执行流程概览

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           流水线执行完整流程                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  步骤1: 获取流水线详情                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ API: GET /rest/openapi/pipeline/edit?pipelineId={pipelineId}            │    │
│  │ 返回: sources, stages, taskDataList                                      │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤2: 交互式选择分支/标签                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 遍历 sources:                                                            │    │
│  │ - 代码源 → 获取分支/标签列表 → 用户选择                                     │    │
│  │ - 制品源 → 获取版本列表 → 用户选择                                         │    │
│  │ 组装 runSources                                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤3: 交互式选择任务节点                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 展示流水线结构 (阶段→步骤→任务)                                            │    │
│  │ 用户选择要执行的任务 (可多选/全选)                                          │    │
│  │ 组装 taskDataList                                                        │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤4: 执行流水线                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ API: POST /rest/openapi/pipeline/runByManual                             │    │
│  │ 返回: pipelineLogId (执行记录ID)                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤5: 输出执行结果                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 按照输出格式展示：流水线名称、分支、执行阶段、详情链接                        │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 步骤1: 获取流水线详情

**API调用**：

```
GET /rest/openapi/pipeline/edit?pipelineId={pipelineId}
```

**响应关键字段**：

```json
{
  "code": 0,
  "data": {
    "pipeline": {
      "pipelineId": "xxx",
      "name": "流水线名称",
      "spaceId": 133,
      "sources": [...],      // 代码源/制品源列表
      "stages": [...]        // 阶段→步骤→任务 结构
    },
    "taskDataList": [...]    // 任务配置数据
  }
}
```

**提取关键信息**：

| 字段 | 用途 |
|------|------|
| `pipeline.spaceId` | 构建详情链接 |
| `pipeline.name` | 输出显示 |
| `pipeline.sources` | 步骤2 选择分支/版本 |
| `pipeline.stages` | 步骤3 选择任务节点 |
| `taskDataList` | 步骤3 组装执行数据 |

---

## 步骤2: 交互式选择分支/标签

### 2.1 遍历代码源

对于每个 `sourceType === 'code'` 的源：

**获取分支/标签列表 API**：

```
POST /rest/openapi/pipeline/getRepoBranchAndTagList
```

**请求体**：

```json
[
  {
    "refsType": "BRANCH",
    "repoType": "GITEE",
    "repoUrl": "https://gitee.com/team/repo",
    "currentPage": 1,
    "pageSize": 20
  }
]
```

**响应**：

```json
{
  "code": "200",
  "data": [
    {
      "branchListVO": {
        "branchVOPage": {
          "data": [
            { "name": "master", "commitId": "abc123" },
            { "name": "develop", "commitId": "def456" }
          ]
        }
      },
      "tagListVO": {
        "tagVOPage": {
          "data": [
            { "name": "v1.0.0", "commitId": "xyz789" }
          ]
        }
      }
    }
  ]
}
```

### 2.2 交互式选择界面

```
┌─────────────────────────────────────────────────────────────┐
│  选择代码源分支/标签                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  代码源: my-project (Gitee)                                 │
│                                                             │
│  选择类型:                                                   │
│  ○ 分支 (BRANCH)                                            │
│  ○ 标签 (TAG)                                               │
│                                                             │
│  可选项:                                                     │
│  ○ master (默认)                                            │
│  ○ develop                                                  │
│  ○ feature/new-feature                                      │
│  ○ release/v1.0                                             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  [取消]                                    [确认]            │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 遍历制品源

对于每个 `sourceType === 'package'` 的源：

**获取镜像标签列表 API**：

```
GET /rest/openapi/pipeline/imageTags?imageName={imageName}&repoType=IPACKAGE
```

**获取普通制品版本列表 API**：

```
GET /rest/openapi/pipeline/packageVersions?artifactName={artifactName}&repoType=IPACKAGE
```

### 2.4 组装 runSources

**代码源 runSource 结构**：

```json
{
  "id": "source-001",
  "name": "my-project",
  "shortName": "my-project",
  "refsType": "BRANCH",
  "refsTypeValue": "master",
  "data": {
    "sourceType": "code",
    "repoType": "GITEE",
    "repoUrl": "https://gitee.com/team/repo",
    "branch": "master",
    "refsType": "BRANCH",
    "workPath": "my-project_src1"
  }
}
```

**Docker 制品源 runSource 结构**：

```json
{
  "id": "source-002",
  "name": "my-image",
  "shortName": "my-image",
  "data": {
    "sourceType": "package",
    "packageType": "DOCKER",
    "repoType": "IPACKAGE",
    "workPath": "my-image_xyz2",
    "imageName": "my-image",
    "defaultTag": "v1.0.0",
    "imageAddress": "registry.iflytek.com/project/my-image:v1.0.0"
  }
}
```

---

## 步骤3: 交互式选择任务节点

### 3.1 从流水线配置获取可执行任务

**任务层级结构**：

```
流水线 (Pipeline)
└── 阶段列表 (Stages)
    └── 阶段 (Stage)
        └── 步骤列表 (Steps)
            └── 步骤 (Step)
                └── 任务列表 (Tasks)
                    └── 任务 (Task) ← 可执行单元
```

**解析可执行任务**：

```python
def get_executable_tasks(pipeline_data):
    """从流水线配置中获取所有可执行的任务"""
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

                tasks.append({
                    'id': task.get('id'),
                    'name': task.get('name'),
                    'stageName': stage_name,
                    'stepName': step_name,
                    'driven': driven
                })

    return tasks
```

### 3.2 交互式选择界面

```
┌─────────────────────────────────────────────────────────────┐
│  选择执行任务节点                                             │
├─────────────────────────────────────────────────────────────┤
│  ☑ 全选                                                      │
│                                                             │
│  ▼ 构建阶段                                                  │
│    ☑ Maven构建 (MavenBuild)                    [串行]       │
│    ☑ Docker镜像构建 (DockerBuild)              [并行]       │
│                                                             │
│  ▼ 测试阶段                                                  │
│    ☐ 单元测试 (JUnit)                         [串行]       │
│    ☐ 代码扫描 (SonarQube)                     [串行]       │
│                                                             │
│  ▼ 部署阶段                                                  │
│    ☐ K8s部署 (K8sDeploy)                      [串行]       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  [取消]                                    [开始执行]        │
└─────────────────────────────────────────────────────────────┘

已选择: 2 个任务
```

### 3.3 组装 taskDataList

> ⚠️ **重要约束**：`taskDataList` **不能为空、不能为空数组**

**根据用户选择组装**：

```python
def build_task_data_list(selected_task_ids, pipeline_data):
    """根据用户选择的任务ID构建 taskDataList"""
    task_data_list = []
    all_task_data = pipeline_data.get('taskDataList', [])

    for td in all_task_data:
        if td.get('id') in selected_task_ids:
            task_data_list.append({
                'id': td.get('id'),
                'name': td.get('name', ''),
                'data': {
                    'jobType': td.get('data', {}).get('jobType', ''),
                    'taskCategory': td.get('data', {}).get('taskCategory', '')
                }
            })

    return task_data_list
```

**taskDataList 结构**：

```json
[
  {
    "id": "task-001",
    "name": "Maven构建",
    "data": {
      "jobType": "MavenBuild",
      "taskCategory": "Build"
    }
  },
  {
    "id": "task-002",
    "name": "Docker镜像构建",
    "data": {
      "jobType": "DockerBuildAndUpload",
      "taskCategory": "DockerBuild"
    }
  }
]
```

---

## 步骤4: 执行流水线

### API 调用

```
POST /rest/openapi/pipeline/runByManual
```

### 完整请求体

```json
{
  "pipelineId": "25aa4b5ff23045fba4b6f2b7c162eda7",
  "runRemark": "手动触发执行",
  "runSources": [
    {
      "id": "source-001",
      "name": "my-project",
      "shortName": "my-project",
      "refsType": "BRANCH",
      "refsTypeValue": "master",
      "data": {
        "sourceType": "code",
        "repoType": "GITEE",
        "repoUrl": "https://gitee.com/team/repo",
        "branch": "master",
        "refsType": "BRANCH",
        "workPath": "my-project_src1"
      }
    }
  ],
  "taskDataList": [
    {
      "id": "task-001",
      "name": "Maven构建",
      "data": {
        "jobType": "MavenBuild",
        "taskCategory": "Build"
      }
    }
  ]
}
```

### 响应

```json
{
  "code": 0,
  "message": "success",
  "data": 22613,
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**data 字段**: 流水线执行记录ID (pipelineLogId)

---

## 步骤5: 输出执行结果

### 输出模板

```markdown
流水线启动成功！

| 项目 | 信息 |
|------|------|
| 流水线名称 | {pipelineName} |
| 分支 | {branch} |
| 代码仓库 | {repoName} |

**执行阶段：**
{stages列表}

**查看执行详情：** https://one-dev.iflytek.com/cloud-work/devops/web-devops-application/flow/detail?pipelineId={pipelineId}&pipelineLogId={pipelineLogId}&spaceId={spaceId}
```

### 输出规范

| 规范项 | 说明 |
|--------|------|
| 不显示执行记录ID | pipelineLogId 仅用于构建链接 |
| 提供可点击链接 | 格式固定，参数从响应和配置中获取 |
| 展示基本信息 | 流水线名称、分支、代码仓库 |
| 列出执行阶段 | 从 stages 中提取任务名称 |

### 示例输出

```markdown
流水线启动成功！

| 项目 | 信息 |
|------|------|
| 流水线名称 | Node.js构建流水线 |
| 分支 | release_20250515 |
| 代码仓库 | ylyan9/yyltest-nodejs02 |

**执行阶段：**
1. Node.js构建 (v18.20.8)
2. Node.js镜像构建

**查看执行详情：** https://one-dev.iflytek.com/cloud-work/devops/web-devops-application/flow/detail?pipelineId=25aa4b5ff23045fba4b6f2b7c162eda7&pipelineLogId=22613&spaceId=133
```

---

## API 接口汇总

| 步骤 | API | 方法 | 说明 |
|------|-----|------|------|
| 1 | `/rest/openapi/pipeline/edit` | GET | 获取流水线详情 |
| 2 | `/rest/openapi/pipeline/getRepoBranchAndTagList` | POST | 获取分支/标签列表 |
| 2 | `/rest/openapi/pipeline/imageTags` | GET | 获取镜像标签列表 |
| 2 | `/rest/openapi/pipeline/packageVersions` | GET | 获取制品版本列表 |
| 4 | `/rest/openapi/pipeline/runByManual` | POST | 执行流水线 |

---

## 注意事项

### 大模型执行约束

| 约束项 | 说明 | 违反后果 |
|--------|------|----------|
| 步骤顺序 | 必须按 1→2→3→4→5 顺序执行 | 流程混乱、数据缺失 |
| taskDataList | **不能为空、不能为空数组** | 执行失败 |
| runSources | 必须按转换逻辑生成 | 数据格式错误 |
| pipelineId | 必填 | 接口报错 |

### 执行前检查清单

- [ ] 已获取流水线详情（包含 sources、stages、taskDataList）
- [ ] taskDataList 非空、非空数组，包含有效的任务数据
- [ ] runSources 已按转换逻辑正确组装
- [ ] 每个代码源的 branch/refsTypeValue 已设置

### 其他注意事项

1. OpenAPI触发类型自动设置为2
2. pipelineLogId 为 Long 类型，返回的是执行记录ID
3. 重新执行时需要传 reRunFlag=1 和 fromPipelineLogId
4. **taskDataList 不能为空或空数组** - 这是执行流水线的关键约束

---

## 相关文档

| 文档 | 说明 |
|------|------|
| `pipeline/openapi/06-execute-pipeline-api.md` | 执行 API 详细规范（**必须参考**） |
| `excute-pipeline-logic.md` | runSources 数据转换详细逻辑 |
