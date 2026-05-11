---

name: pipeline-task-update
description: 更新/编辑流水线中的任务节点配置。当用户需要修改已有任务的参数、调整任务配置时使用此功能。

触发关键词："修改任务"、"更新任务"、"编辑任务"、"调整任务配置"、"任务参数修改"
---

# 更新任务节点

> ⚠️ **大模型执行约束（必须严格遵守）**
>
> **继承全局约束**：本功能同时遵守 [SKILL.md](../SKILL.md) 中定义的全局执行约束。
>
> **本功能特定约束**：每次更新任务时，**必须先获取任务当前配置再进行修改**。

## 执行铁律

| 约束编号 | 约束类型 | 约束说明 | 违反后果 |
|---------|---------|---------|---------|
| U1 | 先查询 | 必须先获取任务当前配置 | 覆盖原有配置 |
| U2 | 保留ID | 更新时必须使用原任务ID | 创建重复任务 |
| U3 | 必填项 | 核心字段（name, jobType, taskCategory）不能为空 | 保存失败 |
| U4 | 字段合并 | 只需要传递需要更新的字段，其他字段保留原值 | 数据丢失 |

---

## 功能描述

更新已有流水线的任务节点配置。与添加任务不同，更新任务需要：
1. 先查询任务的当前配置
2. 修改需要变更的字段
3. 保留其他字段不变

---

## 更新任务流程

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           更新任务节点完整流程                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  步骤1: 解析用户输入                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 输入: "把流水线pipe-001的Maven构建任务改为JDK11"                           │    │
│  │ 输出: { pipelineId, taskName, updateFields }                             │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤2: 获取流水线详情                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ API: GET /rest/openapi/pipeline/edit                                    │    │
│  │ 目的: 找到需要修改的任务，获取 taskId                                     │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤3: 查询任务当前配置                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 从 pipeline.edit 响应中获取任务配置                                       │    │
│  │ 遍历 stages → steps → tasks 找到目标任务的 taskData                      │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤4: 修改任务参数                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 合并原配置与新配置 → 生成更新后的 taskData                               │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤5: 保存更新                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 更新 pipeline 中的 taskDataList 配置                                    │    │
│  │ 注意：此步骤是流水线更新流程的一部分，由 pipeline-update.md              │    │
│  │ 中的保存步骤统一保存                                                     │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤6: 确认更新结果                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 展示更新后的任务配置                                                     │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 详细步骤说明

### 步骤1: 解析用户输入

**输入示例**:
```
"把流水线 pipe-001 的 Maven 构建任务改成 JDK11"
"修改构建任务的 workPath 为 ./src"
"将部署任务的目标主机组改为 group-002"
"更新 SonarQube 扫描的 projectKey"
```

**需要提取的信息**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pipelineId | string | 是 | 流水线ID |
| taskName | string | 是 | 任务名称（用于定位任务） |
| updateFields | dict | 是 | 需要更新的字段和值 |

---

### 步骤2: 获取流水线详情

**API**: `GET /rest/openapi/pipeline/edit?pipelineId={pipelineId}`

遍历 stages 找到目标任务：
```python
for stage in stages:
    for step in stage.get('steps', []):
        for task in step.get('tasks', []):
            if task.get('name') == task_name:
                task_id = task.get('id')
                stage_id = stage.get('id')
                step_id = step.get('id')
                break
```

---

### 步骤3: 查询任务当前配置

从 `GET /rest/openapi/pipeline/edit` 响应中获取任务配置：

```python
# 从流水线详情中获取任务配置
pipeline = get_pipeline_edit(pipeline_id)

# 遍历找到目标任务
task_data = None
target_task_id = None

for stage in pipeline.get("stages", []):
    for step in stage.get("steps", []):
        for task in step.get("tasks", []):
            if task.get("name") == task_name:
                target_task_id = task.get("id")
                break

# 从 taskDataList 中获取详细配置
for td in pipeline.get("taskDataList", []):
    if td.get("id") == target_task_id:
        task_data = td.get("data")
        break
```

---

### 步骤4: 修改任务参数

#### 常见更新场景

**场景A: 修改 JDK 版本**
```python
# 原配置
original_task_data = {
    "name": "Maven构建",
    "jobType": "MavenBuild",
    "taskCategory": "Build",
    "jdkVersion": "JDK17",
    "goals": "clean package"
}

# 需要更新的字段
update_fields = {
    "jdkVersion": "JDK11"
}

# 合并配置
updated_task_data = {**original_task_data, **update_fields}
# 结果: jdkVersion 变为 JDK11，其他字段保留
```

**场景B: 修改工作目录**
```python
update_fields = {
    "workPath": "./new-path"
}
```

**场景C: 修改构建命令**
```python
update_fields = {
    "goals": "clean package -DskipTests"
}
```

**场景D: 添加/修改依赖任务**
```python
# 设置任务依赖（串行执行）
update_fields = {
    "dependencies": ["task-previous-001"]
}
```

---

### 步骤5: 保存更新

将更新后的任务配置同步到 `taskDataList` 中，等待流水线更新流程统一保存。

> ⚠️ **重要**：更新任务是流水线更新流程的一部分，保存操作由 [pipeline-update.md](./pipeline-update.md) 中的保存步骤统一处理。

**关键点**:
- 更新 `taskDataList` 中对应 taskId 的 `data` 字段
- 保持 `pipeline.stages` 中的任务基本信息不变（只更新 data）

---

### 步骤6: 确认更新结果

更新成功后，展示变更摘要：
```
✅ 任务更新成功！

任务名称: Maven构建
任务ID: task-001

变更内容:
├── jdkVersion: JDK17 → JDK11
└── goals: clean package → clean package -DskipTests
```

---

## 命令行方式

```bash
# 更新 JDK 版本
python -m scripts/main task-update \
  --pipeline-id pipe-001 \
  --task-id task-001 \
  --field jdkVersion=JDK11

# 更新多个字段
python -m scripts/main task-update \
  --pipeline-id pipe-001 \
  --task-id task-001 \
  --field workPath=./new-path \
  --field goals="clean package -DskipTests"
```

---

## 常用更新字段参考

### 构建类任务 (Build)

| jobType | 可更新字段 |
|---------|-----------|
| `MavenBuild` | jdkVersion, goals, options, mavenSettings |
| `GradleBuild` | jdkVersion, gradleVersion, tasks |
| `NpmBuild` | npmCommand, nodeVersion |
| `PythonBuild` | pythonVersion, command |
| `GoBuild` | goVersion, command |

### Docker 构建类任务

| jobType | 可更新字段 |
|---------|-----------|
| `DockerBuildAndUpload` | dockerfile, imageName, imageTag, registryUrl |
| `MavenDockerBuild` | dockerfile, imageName, mavenGoals |
| `NpmDockerBuild` | dockerfile, imageName, npmCommand |

### 部署类任务

| jobType | 可更新字段 |
|---------|-----------|
| `HostDeploy` | hostGroupId, allHosts, hostIds, workPath |
| `HostDockerDeploy` | hostGroupId, allHosts, hostIds, containerName |
| `SaeImageUpdate` | appId, imageTag |
| `YamlDeploy` | yamlPath, namespace |

### 代码扫描类任务

| jobType | 可更新字段 |
|---------|-----------|
| `SonarQube` | sonarProjectKey, sonarUrl, qualityGate |
| `ScaCodeScan` | scanType, threshold |
| `SecCodeScan` | scanScope |

---

## 完整更新示例

### 示例1: 修改 Maven 构建任务的 JDK 版本

```python
def update_task_jdk_version(pipeline, task_id: str, new_jdk: str):
    """更新任务的 JDK 版本"""
    # 1. 在 taskDataList 中找到并更新任务配置
    for td in pipeline.get("taskDataList", []):
        if td.get("id") == task_id:
            task_data = td.get("data", {})
            # 更新 JDK 版本
            task_data["jdkVersion"] = new_jdk
            break

    # 2. 返回更新后的配置，由外部流程统一保存
    return pipeline

# 使用（由 pipeline-update 流程调用）
pipeline = get_pipeline_edit(pipeline_id)
pipeline = update_task_jdk_version(pipeline, "task-001", "JDK11")
# 由 pipeline-update.md 统一保存
```

### 示例2: 修改部署任务的目标主机

```python
def update_deploy_hosts(pipeline, task_id: str, host_group_id: int, host_ids: list):
    """更新部署任务的目标主机"""
    # 更新任务配置
    for td in pipeline.get("taskDataList", []):
        if td.get("id") == task_id:
            task_data = td.get("data", {})
            task_data["hostGroupId"] = host_group_id
            task_data["allHosts"] = False
            task_data["hostIds"] = host_ids
            break

    # 返回更新后的配置
    return pipeline
```

### 示例3: 添加任务依赖

```python
def add_task_dependency(pipeline, task_id: str, dependency_task_id: str):
    """添加任务依赖"""
    # 添加依赖
    for td in pipeline.get("taskDataList", []):
        if td.get("id") == task_id:
            task_data = td.get("data", {})
            deps = task_data.get("dependencies", [])
            deps.append(dependency_task_id)
            task_data["dependencies"] = deps
            break

    # 返回更新后的配置
    return pipeline
```

---

## 注意事项

1. **统一保存**：更新任务是流水线更新流程的一部分，由 [pipeline-update.md](./pipeline-update.md) 统一保存
2. **不要修改 jobType**：jobType 决定任务类型，更改会导致任务不可用
3. **保留必填字段**：name、taskCategory 等字段即使不修改也要保留
4. **sourceId 变更**：如果修改了 sourceId，需要确保新代码源存在
5. **工作目录**：修改 workPath 后要确认路径正确
6. **依赖任务**：dependencies 中的任务必须在同一阶段之前的步骤中
