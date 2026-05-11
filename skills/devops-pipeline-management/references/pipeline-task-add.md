---

name: pipeline-task-add
description: 添加任务节点到流水线。当用户需要在已有流水线中添加构建任务、部署任务、扫描任务等时使用此功能。

触发关键词："添加任务"、"新增任务"、"添加节点"、"流水线添加任务"、"添加构建任务"、"添加部署任务"
---

# 添加任务节点

> ⚠️ **大模型执行约束（必须严格遵守）**
>
> **继承全局约束**：本功能同时遵守 [SKILL.md](../SKILL.md) 中定义的全局执行约束。
>
> **本功能特定约束**：每次添加任务时，**必须严格按照本文档定义的步骤执行**，大模型不得自定义流程。

## 执行铁律

| 约束编号 | 约束类型 | 约束说明 | 违反后果 |
|---------|---------|---------|---------|
| T1 | 前置检查 | 必须先获取流水线详情，确认 stage 和 step 存在 | 任务添加到错误位置 |
| T2 | ID生成 | 添加新任务时必须生成 UUID 作为任务ID | 数据冲突 |
| T3 | 必填项 | taskData 的 jobType、name、taskCategory 必须填写 | 保存失败 |
| T4 | 统一保存 | 任务配置添加到流水线后，必须通过流水线保存API统一保存 | 任务丢失 |
| T5 | sourceId | 如果任务需要代码源，必须提供 sourceId | 构建失败 |

## 功能描述

向已有流水线添加任务节点。流水线结构为：**阶段(Stage) → 步骤(Step) → 任务(Task)**

## 流水线层级结构

```
Pipeline (流水线)
└── Stages (阶段列表)
    └── Steps (步骤列表)
        └── Tasks (任务列表)
```

| 层级 | 说明 |
|------|------|
| Stage | 阶段，如"构建阶段"、"部署阶段" |
| Step | 步骤（可并行/串行），如"Maven构建"、"Docker构建" |
| Task | 任务节点，具体执行单元 |

---

## 交互式添加任务流程

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           添加任务节点完整流程                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  步骤1: 解析用户输入                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 输入: "在流水线pipe-001的构建阶段添加一个Maven构建任务"                      │    │
│  │ 输出: { pipelineId, stageName, jobType }                                  │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤2: 获取流水线详情                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ API: GET /rest/openapi/pipeline/edit                                    │    │
│  │ 获取: pipelineId, sources, stages 结构                                   │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤3: 确定目标位置                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 展示现有 stages → 用户选择阶段 → 选择步骤                                 │    │
│  │ 如果阶段/步骤不存在，需要先创建                                           │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤4: 选择任务类型                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 展示任务类型列表 → 用户选择 jobType                                      │    │
│  │ 或根据关键词自动匹配                                                      │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤5: 生成任务ID                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ API: GET /rest/openapi/pipeline/task/createTaskId                       │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤6: 配置任务参数                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 根据 jobType 显示对应字段 → 用户填写/确认                                 │    │
│  │ 必填: name, jobType, taskCategory                                      │    │
│  │ 条件: workPath, sourceId                                               │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤7: 保存任务                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 将任务配置添加到 pipeline.stages + taskDataList                        │    │
│  │ 注意：此步骤是流水线创建/更新流程的一部分，由 pipeline-create.md        │    │
│  │ 或 pipeline-update.md 中的保存步骤统一保存                              │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤8: 配置预览                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 展示任务配置 → 用户确认 → 完成                                            │    │
│  └─────────���───────────────────────────────────────────────────────────────┘    │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 详细步骤说明

### 步骤1: 解析用户输入

**输入示例**:
```
"在流水线 pipe-001 添加一个 Maven 构建任务"
"给 pipeline-abc 添加部署任务到测试环境"
"在构建阶段添加 SonarQube 扫描"
```

**需要提取的信息**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pipelineId | string | 是 | 流水线ID（从输入中提取或让用户选择） |
| stageName | string | 否 | 阶段名称（可选，默认选择第一个阶段） |
| stepName | string | 否 | 步骤名称（可选） |
| jobType | string | 否 | 任务类型（可从语言/工具推断） |

**技术栈/工具关键词映射**:

| jobType | 关键词 |
|---------|--------|
| `MavenBuild` | maven, mvn, java |
| `GradleBuild` | gradle |
| `NpmBuild` | npm, node, vue, react |
| `PythonBuild` | python, pip |
| `GoBuild` | go, golang |
| `DockerBuildAndUpload` | docker, 镜像 |
| `HostDeploy` | 部署, deploy |
| `SaeImageUpdate` | SAE, 阿里云 |
| `SonarQube` | sonar, 代码质量 |
| `ScaCodeScan` | 源码扫描, SCA |

---

### 步骤2: 获取流水线详情

**API**: `GET /rest/openapi/pipeline/edit?pipelineId={pipelineId}`

**目的**: 获取流水线的 stages 结构，确定任务添加位置

**响应中的关键字段**:
```json
{
  "data": {
    "pipelineId": "pipe-001",
    "sources": [...],
    "stages": [
      {
        "id": "stage-001",
        "name": "构建阶段",
        "steps": [
          {
            "id": "step-001",
            "name": "Maven构建",
            "tasks": [
              { "id": "task-001", "name": "编译" }
            ]
          }
        ]
      },
      {
        "id": "stage-002",
        "name": "部署阶段",
        "steps": [...]
      }
    ]
  }
}
```

---

### 步骤3: 确定目标位置

如果用户指定了阶段名称，在 stages 中查找匹配的 stage：
- 找到 → 获取 stageId
- 未找到 → 提示用户或创建新阶段

如果用户指定了步骤名称，在步骤中查找匹配的 step：
- 找到 → 获取 stepId
- 未找到 → 创建新步骤

**添加步骤到已有阶段**:
```json
{
  "id": "step-new-001",
  "name": "新步骤名称",
  "nodeType": "custom-step-node",
  "idx": 0,
  "driven": 0,
  "tasks": []
}
```

---

### 步骤4: 选择任务类型

从以下分类中选择合适的 jobType：

### Build (编译构建)

| jobType | 名称 | 说明 |
|---------|------|------|
| `OrderAction` | 执行命令 | 通用Shell命令执行任务 |
| `MavenBuild` | Maven构建 | Java Maven项目构建 |
| `GradleBuild` | Gradle构建 | Gradle项目构建 |
| `NpmBuild` | Node.js构建 | Node.js项目构建 |
| `PythonBuild` | Python构建 | Python项目构建 |
| `GoBuild` | Go构建 | Go项目构建 |
| `CppBuild` | C++构建 | C++项目构建 |
| `ChannelBuild` | 渠道构建 | Android多渠道包批量构建 |

### DockerBuild (镜像构建)

| jobType | 名称 | 说明 |
|---------|------|------|
| `DockerBuildAndUpload` | Docker构建上传 | 构建Docker镜像并上传到仓库 |
| `MavenDockerBuild` | Maven镜像构建 | Maven + Docker组合构建 |
| `NpmDockerBuild` | Node.js镜像构建 | Node.js + Docker组合构建 |
| `PythonDockerBuild` | Python镜像构建 | Python + Docker组合构建 |
| `GoDockerBuild` | Go镜像构建 | Go + Docker组合构建 |

### Deploy (部署)

| jobType | 名称 | 说明 |
|---------|------|------|
| `HostDeploy` | 主机部署 | 传统主机部署 |
| `HostDockerDeploy` | Docker部署 | 主机Docker部署 |
| `Sae` | SAE应用发布 | SAE首次创建应用 |
| `SaeImageUpdate` | SAE镜像更新 | SAE容器镜像更新部署 |
| `SaeHelm` | SAE Helm | SAE Helm Chart部署 |
| `YamlDeploy` | Yaml部署 | 通用YAML部署 |
| `CloudHelmDeploy` | Helm部署 | 云端Helm部署 |

### CodeScanner (代码扫描)

| jobType | 名称 | 说明 |
|---------|------|------|
| `SonarQube` | SonarQube扫描 | SonarQube代码质量扫描 |
| `ScaCodeScan` | 源码扫描 | SCA组件依赖漏洞扫描 |
| `SecCodeScan` | 代码安全扫描 | 源代码安全扫描 |
| `ScaBinaryScan` | 二进制扫描 | 二进制制品安全扫描 |

### Normal (通用)

| jobType | 名称 | 说明 |
|---------|------|------|
| `ManualReview` | 人工审核 | 人工审批确认任务 |
| `ProductDistribution` | 制品分发 | 镜像分发到多个仓库 |

---

### 步骤5: 生成任务ID

生成一个新的 UUID 作为任务ID：

```python
import uuid
task_id = str(uuid.uuid4())
# 例如: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

---

### 步骤6: 配置任务参数

根据选择的 jobType 配置 taskData。

#### 通用字段 (所有 jobType 必需)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 任务名称 |
| jobType | string | 是 | 任务类型标识 |
| taskCategory | string | 是 | 任务分类 |
| workPath | string | 条件 | 工作目录（代码源根目录） |
| sourceId | string | 条件 | 代码源ID |

#### taskCategory 枚举

| 值 | 说明 |
|----|------|
| `Build` | 编译构建 |
| `DockerBuild` | 镜像构建 |
| `Deploy` | 部署 |
| `CodeScanner` | 代码扫描 |
| `CodeCover` | 测试/覆盖率 |
| `Code` | 代码操作 |
| `Normal` | 通用 |

#### jobType 与 taskCategory 映射

| jobType | taskCategory |
|---------|-------------|
| `MavenBuild` | Build |
| `DockerBuildAndUpload` | DockerBuild |
| `HostDeploy` | Deploy |
| `SonarQube` | CodeScanner |
| `ManualReview` | Normal |

---

### 各任务类型详细字段

> ⚠️ **详细字段配置请参考**：[schemas/all-tasks/](./pipeline/schemas/all-tasks/) 目录下的 Schema 文件

示例 - MavenBuild 任务配置:
```json
{
  "taskData": {
    "name": "Maven构建",
    "jobType": "MavenBuild",
    "taskCategory": "Build",
    "workPath": "my-app",
    "sourceId": "source-001",
    "jdkVersion": "JDK17",
    "mavenSettings": "default",
    "goals": "clean package",
    "options": "-DskipTests"
  }
}
```

示例 - DockerBuildAndUpload 任务配置:
```json
{
  "taskData": {
    "name": "Docker构建",
    "jobType": "DockerBuildAndUpload",
    "taskCategory": "DockerBuild",
    "workPath": "my-app",
    "sourceId": "source-001",
    "dockerfile": "./Dockerfile",
    "imageName": "my-app",
    "imageTag": "latest",
    "registryUrl": "registry.example.com"
  }
}
```

---

### 步骤7: 保存任务

将任务配置添加到流水线的 stages 结构中，等待流水线创建/更新流程统一保存。

> ⚠️ **重要**：添加任务是流水线创建/更新流程的一部分，保存操作由以下流程统一处理：
> - **创建流水线时**：由 [pipeline-create.md](./pipeline-create.md) 中的保存步骤统一保存
> - **更新流水线时**：由 [pipeline-update.md](./pipeline-update.md) 中的保存步骤统一保存

**任务配置结构**:
```json
{
  "pipeline": {
    "stages": [
      {
        "id": "stage-001",
        "name": "构建阶段",
        "steps": [
          {
            "id": "step-001",
            "name": "Maven构建",
            "tasks": [
              {
                "id": "task-new-001",
                "name": "Maven构建"
              }
            ]
          }
        ]
      }
    ]
  },
  "taskDataList": [
    {
      "id": "task-new-001",
      "data": {
        "name": "Maven构建",
        "jobType": "MavenBuild",
        "taskCategory": "Build",
        "workPath": "my-app",
        "sourceId": "source-001"
      }
    }
  ]
}
```

**关键点**:
- `pipeline.stages[].steps[].tasks[]` - 添加任务的基本信息（id, name）
- `taskDataList[]` - 添加任务的详细配置（id, data）
- 两者通过 `id` 关联

---

### 步骤8: 配置预览

保存成功后，展示任务配置摘要：
```
✅ 任务添加成功！

任务名称: Maven构建
任务类型: MavenBuild
所属阶段: 构建阶段
所属步骤: Maven构建
工作目录: my-app
代码源: order-service (source-001)
```

---

## 命令行方式

```bash
# 添加 Maven 构建任务
python -m scripts/main task-add \
  --pipeline-id pipe-001 \
  --stage-id stage-001 \
  --step-id step-001 \
  --job-type MavenBuild \
  --name "Maven构建" \
  --work-path my-app \
  --source-id source-001

# 添加 Docker 构建任务
python -m scripts/main task-add \
  --pipeline-id pipe-001 \
  --stage-id stage-002 \
  --step-id step-new \
  --job-type DockerBuildAndUpload \
  --name "Docker构建" \
  --dockerfile ./Dockerfile \
  --image-name my-app
```

---

## 常见场景

### 场景1: 添加构建任务

```python
import uuid

# 1. 获取当前流水线配置（由 pipeline-create/pipeline-update 流程提供）
pipeline = get_pipeline_edit(pipeline_id)

# 2. 生成任务ID
task_id = str(uuid.uuid4())

# 3. 构建任务数据
task_data = {
    "name": "Maven构建",
    "jobType": "MavenBuild",
    "taskCategory": "Build",
    "workPath": "my-app",
    "sourceId": source_id,
    "jdkVersion": "JDK17",
    "goals": "clean package"
}

# 4. 将任务添加到 stages 结构中
for stage in pipeline["stages"]:
    if stage["name"] == "构建阶段":
        for step in stage["steps"]:
            if step["name"] == "构建":
                step["tasks"].append({
                    "id": task_id,
                    "name": "Maven构建"
                })

# 5. 添加到 taskDataList
task_data_list = pipeline.get("taskDataList", [])
task_data_list.append({
    "id": task_id,
    "data": task_data
})

# 6. 返回更新后的 pipeline 配置，由外部流程统一保存
# pipeline-create.md 或 pipeline-update.md 会在适当时候调用保存
return pipeline, task_data_list
```

### 场景2: 添加部署任务

```python
# 任务配置
task_data = {
    "name": "部署到测试环境",
    "jobType": "HostDeploy",
    "taskCategory": "Deploy",
    "hostGroupId": 1001,
    "allHosts": True,
    "workPath": "/opt/app"
}

# 添加到对应的 stage.step.tasks 和 taskDataList
# 由外部流程统一保存
```

### 场景3: 添加代码扫描任务

```python
task_data = {
    "name": "代码质量扫描",
    "jobType": "SonarQube",
    "taskCategory": "CodeScanner",
    "sourceId": source_id,
    "sonarProjectKey": "my-app",
    "sonarUrl": "https://sonar.example.com"
}

# 添加到对应的 stage.step.tasks 和 taskDataList
# 由外部流程统一保存
```

---

## 错误处理

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 400 | 参数错误 | 检查必填字段是否填写 |
| 404 | 流水线/阶段/步骤不存在 | 确认 pipelineId、stageId 正确 |
| 500 | 服务端错误 | 重试或联系管理员 |

---

## 注意事项

1. **任务需要添加到两个地方**：
   - `pipeline.stages[].steps[].tasks[]` - 任务基本信息
   - `taskDataList[]` - 任务详细配置
2. **统一保存**：添加/更新任务是流水线创建/更新流程的一部分，由 [pipeline-create.md](./pipeline-create.md) 或 [pipeline-update.md](./pipeline-update.md) 统一保存
3. **sourceId 关联**：如果任务需要读取代码，必须提供正确的 sourceId
4. **工作目录**：workPath 是相对于代码源根目录的路径
5. **任务依赖**：如果任务有依赖关系，需要设置 dependencies 字段
