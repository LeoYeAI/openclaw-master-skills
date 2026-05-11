---

name: pipeline-update
description: 更新/编辑流水线配置。当用户需要修改流水线配置、更新CI配置、编辑流水线时使用此功能。支持命令行更新和交互式更新两种方式。

触发关键词："编辑流水线"、"修改流水线"、"更新流水线"、"流水线配置修改"、"调整流水线"
---

# 流水线更新（编辑）

> ⚠️ **大模型执行约束（必须严格遵守）**
>
> **继承全局约束**：本功能同时遵守 [SKILL.md](../SKILL.md) 中定义的全局执行约束。
>
> **本功能特定约束**：每次更新流水线时，**必须严格按照本文档定义的步骤执行**，大模型不得自定义流程、不得跳过步骤、不得调换顺序。

## 执行铁律

| 约束编号 | 约束类型 | 约束说明 | 违反后果 |
|---------|---------|---------|---------|
| U1 | 步骤顺序 | 必须按 1→2→3→4→5→6 顺序执行 | 数据不完整、流程中断 |
| U2 | 配置预览 | 步骤5（配置预览）**必须执行** | 用户无法确认配置、保存后无法追溯 |
| U3 | API调用 | **必须实际调用** API 功能 | 功能失效、结果不可预期 |
| U4 | 接口限定 | 只使用本文档指定的 API 接口 | 权限错误、接口不存在 |
| U5 | pipelineId | 更新时**必须保留原 pipelineId** | 创建重复流水线 |
| U6 | 必填项 | `taskDataList` **不能为空数组** | 执行失败、任务丢失 |
| U7 | ID保留 | 阶段/步骤/任务的 ID **必须保留原值** | 节点关联错误 |

## 功能描述

更新已有流水线的配置。与创建流程的主要区别：
- **必须先获取原流水线配置**（调用 edit API）
- **保留原 pipelineId**
- **更新是全量更新**，传入的配置会完全覆盖原有配置

支持两种更新方式（默认使用交互式更新）：

1. **交互式更新** - 通过交互式向导逐步更新（默认方式，功能更完整）
2. **命令行方式** - 通过命令行参数直接更新（快速更新）


---

## 交互式更新流程概览

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           交互式更新流水线完整流程                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  步骤1: 解析用户输入                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 输入: "编辑流水线pipe-001，添加一个部署任务"                                 │    │
│  │ 输出: { pipelineId, updateType }                                         │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤2: 获取流水线详情                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ API: GET /rest/openapi/pipeline/edit                                    │    │
│  │ 获取: pipelineId, name, sources, stages, taskDataList                    │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤3: 打开交互模式，更新代码源                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 展示当前代码源 → 修改/添加/删除                                           │    │
│  │ 可修改: 分支、标签、Webhook触发                                            │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤4: 打开交互模式，更新任务节点                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 展示当前流水线结构 (阶段→步骤→任务)                                        │    │
│  │                                                                         │    │
│  │ 操作菜单:                                                                │    │
│  │ 1. 添加任务 → 选择阶段 → 选择步骤 → 配置任务                              │    │
│  │ 2. 修改任务 → 选择任务 → 修改参数                                        │    │
│  │ 3. 删除任务 → 选择任务 → 确认删除                                        │    │
│  │ 4. 添加步骤 → 选择阶段 → 创建新步骤                                      │    │
│  │ 5. 添加阶段 → 创建新阶段                                                 │    │
│  │ 0. 完成配置                                                              │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤5: 配置预览（保存前确认）                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 展示更新后的配置数据 → 执行检查清单 → 用户确认 → 保存                       │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤6: 保存流水线                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ API: POST /rest/openapi/pipeline/save                                   │    │
│  │ 返回: pipelineId (与原ID相同)                                            │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 与创建流程的对比

| 对比项 | 创建流程 (pipeline-create) | 更新流程 (pipeline-update) |
|-------|---------------------------|--------------------------|
| pipelineId | 新生成 UUID | 保留原值 |
| 数据来源 | 从模板获取 | 从 edit API 获取现有配置 |
| 步骤数量 | 9步 | 6步 |
| 步骤1 | 解析用户输入(spaceId, language) | 解析用户输入(pipelineId, updateType) |
| 步骤2 | 补充必填信息 | 获取流水线详情(edit API) |
| 步骤3 | 查询模板并选择 | 更新代码源 |
| 步骤4 | 模板数据转换 | 更新任务节点 |
| 步骤5 | 配置代码源 | 配置预览 |
| 步骤6 | 配置任务节点 | 保存流水线 |
| 步骤7 | 配置预览 | - |
| 步骤8 | 保存流水线 | - |
| 步骤9 | 执行流水线 | - |

---

## 详细步骤说明

### 步骤1: 解析用户输入

**目的**: 从自然语言中提取关键信息

**输入示例**:

```
"编辑流水线 pipe-001"
"把流水线 pipeline-abc 的 JDK 版本改成 11"
"在流水线 test-pipe 添加一个部署任务"
"更新流水线的分支为 feature-branch"
```

**需要提取的信息**:


| 字段       | 类型     | 必填  | 说明     | 提取方式                           |
| -------- | ------ | --- | ------ | ------------------------------ |
| pipelineId | String | 是   | 流水线ID | 从输入中提取或让用户选择              |
| updateType | String | 否   | 更新类型  | 添加任务/修改任务/修改代码源/全量更新 |


**更新类型关键词映射**:


| 更新类型   | 关键词                                   | 说明 |
| ------- | ------------------------------------- | ---- |
| 添加任务   | 添加任务、新增任务、添加节点              | 在现有阶段添加新任务 |
| 修改任务   | 修改任务、更新任务、修改参数              | 修改已有任务的配置 |
| 删除任务   | 删除任务、移除任务                       | 删除已有任务 |
| 修改代码源 | 修改分支、更新分支、换分支               | 修改代码源配置 |
| 全量更新   | 编辑、编辑流水线、全面更新                | 打开交互式向导 |



---

### 步骤2: 获取流水线详情

**目的**: 获取原流水线配置，作为更新的基础

**API**: `GET /rest/openapi/pipeline/edit?pipelineId={pipelineId}`

**响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| pipelineId | String | 流水线ID |
| name | String | 流水线名称 |
| spaceId | Long | 空间ID |
| sources | Array | 代码源列表 |
| stages | Array | 阶段列表（含步骤和任务） |
| taskDataList | Array | 任务配置详情列表 |
| triggerInfo | Object | 触发配置 |
| timeoutDuration | String | 超时时间 |
| buildPlatform | String | 构建平台 |

**响应示例**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "pipelineId": "pipe-001",
    "name": "订单服务构建流水线",
    "spaceId": 1001,
    "sources": [
      {
        "id": "src-001",
        "name": "order-service",
        "refsType": "branch",
        "refsTypeValue": "master"
      }
    ],
    "stages": [
      {
        "id": "stage-001",
        "name": "构建阶段",
        "steps": [
          {
            "id": "step-001",
            "name": "Maven构建",
            "tasks": [
              { "id": "task-001", "name": "编译打包" }
            ]
          }
        ]
      }
    ],
    "taskDataList": [
      {
        "id": "task-001",
        "data": {
          "name": "编译打包",
          "jobType": "MavenBuild",
          "jdkVersion": "JDK17"
        }
      }
    ]
  }
}
```

---

### 步骤3: 更新代码源

展示当前代码源列表，支持以下操作：

#### 3.1 查看当前代码源

```
📦 代码源列表:
├── 📦 order-service (src-001)
│   ├── 类型: GitLab
│   ├── 分支: master
│   └── 工作目录: ./
└── [添加代码源]
```

#### 3.2 修改代码源

| 操作 | 说明 |
|------|------|
| 修改分支 | 更新 refsTypeValue |
| 添加Webhook | 配置触发器 |
| 删除代码源 | 从 sources 数组中移除 |

**更新代码源示例**:
```python
# 获取当前配置
pipeline = get_pipeline_edit(pipeline_id)

# 修改分支
for source in pipeline["sources"]:
    if source["id"] == "src-001":
        source["refsTypeValue"] = "feature-new-branch"
        source["data"]["branch"] = "feature-new-branch"
```

---

### 步骤4: 更新任务节点

展示当前流水线结构，支持以下操作：

#### 4.1 查看当前任务结构

```
📋 流水线结构:
│
├── 📂 构建阶段 (stage-001)
│   └── 📂 Maven构建 (step-001) [串行]
│       ├── ✅ 编译打包 (task-001)
│       └── ➕ 添加任务
│
├── 📂 部署阶段 (stage-002)
│   └── 📂 主机部署 (step-001) [串行]
│       ├── ✅ 部署到测试 (task-002)
│       └── ➕ 添加任务
│
├── ➕ 添加阶段
└── ➕ 添加步骤
```

#### 4.2 操作菜单

| 菜单 | 操作 | 说明 |
|------|------|------|
| 1 | 添加任务 | 选择阶段 → 选择步骤 → 配置新任务（详见 pipeline-task-add.md） |
| 2 | 修改任务 | 选择任务 → 修改参数（详见 pipeline-task-update.md） |
| 3 | 删除任务 | 选择任务 → 确认删除（详见 pipeline-task-delete.md） |
| 4 | 添加步骤 | 选择阶段 → 创建新步骤 |
| 5 | 添加阶段 | 创建新阶段 |
| 0 | 完成配置 | 进入配置预览 |

#### 4.3 更新任务示例

**添加任务**:
```python
import uuid

# 生成新任务ID
task_id = str(uuid.uuid4())

# 构建任务配置
task_data = {
    "name": "部署到测试环境",
    "jobType": "HostDeploy",
    "taskCategory": "Deploy",
    "hostGroupId": 1001,
    "workPath": "/opt/app"
}

# 添加到 stages 结构
for stage in pipeline["stages"]:
    if stage["name"] == "部署阶段":
        for step in stage["steps"]:
            step["tasks"].append({
                "id": task_id,
                "name": "部署到测试环境"
            })

# 添加到 taskDataList
pipeline["taskDataList"].append({
    "id": task_id,
    "data": task_data
})
```

**修改任务**:
```python
# 修改任务配置
for td in pipeline["taskDataList"]:
    if td["id"] == "task-001":
        td["data"]["jdkVersion"] = "JDK11"
```

**删除任务**:
```python
# 从 stages 中移除
for stage in pipeline["stages"]:
    for step in stage["steps"]:
        step["tasks"] = [t for t in step["tasks"] if t["id"] != "task-to-delete"]

# 从 taskDataList 中移除
pipeline["taskDataList"] = [td for td in pipeline["taskDataList"] if td["id"] != "task-to-delete"]
```

> ⚠️ **任务操作详细说明**：
> - 添加任务 → [pipeline-task-add.md](./pipeline-task-add.md)
> - 修改任务 → [pipeline-task-update.md](./pipeline-task-update.md)
> - 删除任务 → [pipeline-task-delete.md](./pipeline-task-delete.md)

---

### 步骤5: 配置预览（保存前确认）

展示更新后的完整配置，执行检查清单。

#### 5.1 配置预览示例

```
📋 流水线配置预览:
│
├── 基本信息:
│   ├── 流水线ID: pipe-001
│   ├── 流水线名称: 订单服务构建流水线
│   └── 空间ID: 1001
│
├── 代码源 (1个):
│   └── order-service → feature-new-branch
│
├── 阶段结构:
│   ├── 📂 构建阶段
│   │   └── 📂 Maven构建 [串行]
│   │       ├── ✅ 编译打包
│   │       └── ✅ SonarQube扫描 (新增)
│   │
│   └── 📂 部署阶段
│       └── 📂 主机部署 [串行]
│           └── ✅ 部署到测试
│
└── 任务配置 (3个):
    ├── task-001: MavenBuild (JDK17)
    ├── task-002: SonarQube (新增)
    └── task-003: HostDeploy
```

#### 5.2 检查清单

> ⚠️ **保存前必须确认以下检查项**：

- [ ] pipelineId 与原ID一致
- [ ] stages 结构完整
- [ ] taskDataList 不为空（如果需要执行流水线）
- [ ] 所有 sourceId 引用有效
- [ ] 任务依赖关系正确

---

### 步骤6: 保存流水线

**API**: `POST /rest/openapi/pipeline/save`

**请求体结构**:

```json
{
  "pipeline": {
    "pipelineId": "pipe-001",
    "name": "订单服务构建流水线",
    "spaceId": 1001,
    "sources": [...],
    "stages": [...],
    "triggerInfo": {...},
    "timeoutDuration": "2H",
    "buildPlatform": "linux"
  },
  "taskDataList": [...]
}
```

**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": "pipe-001",
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

> ⚠️ **注意**：更新成功后返回的 pipelineId 与原 ID 相同

---

## 命令行方式

> ⚠️ **注意**：原有的 `update` 命令已移除，现在统一使用 `save` 命令进行流水线创建和更新。

```bash
# 通过JSON字符串更新流水线名称
python -m scripts/main save --config '{"pipelineId": "pipe-001", "name": "新名称", "spaceId": 1001}'

# 通过JSON字符串更新代码源分支
python -m scripts/main save --config '{"pipelineId": "pipe-001", "sources": [{"id": "src-001", "name": "order-service", "refsType": "branch", "refsTypeValue": "feature-branch", "data": {"sourceType": "code", "repoType": "gitlab", "repoUrl": "https://gitlab.example.com/order/service.git", "branch": "feature-branch", "workPath": "./src"}}]}'

# 通过JSON文件更新流水线
python -m scripts/main save --file updated-pipeline-config.json

# 同时指定任务数据
python -m scripts/main save --config '{"pipelineId": "pipe-001", "name": "订单服务构建流水线", "spaceId": 1001, "stages": [...]}' --task-data '[{"id": "task-001", "data": {"name": "构建任务", "jobType": "MavenBuild"}}]'
```

**参数说明**：
- `--config <json_string>`：流水线配置JSON字符串
- `--file <json_file_path>`：流水线配置JSON文件路径
- `--task-data <json_string>`：任务数据JSON字符串（可选）
- `--task-data-file <json_file_path>`：任务数据JSON文件路径（可选）

**注意**：更新流水线时必须保留原 `pipelineId`，且必须包含必填字段：`pipelineId`, `name`, `spaceId`, `pipelineKey`, `aliasId`, `buildNumber`, `buildPlatform`, `timeoutDuration`。

---

## 请求示例

### 示例1: 更新流水线名称

```json
{
  "pipeline": {
    "pipelineId": "pipe-001",
    "name": "更新后的流水线名称",
    "spaceId": 1001
  }
}
```

### 示例2: 更新代码源分支

```json
{
  "pipeline": {
    "pipelineId": "pipe-001",
    "name": "订单服务构建流水线",
    "spaceId": 1001,
    "sources": [
      {
        "id": "src-001",
        "name": "order-service",
        "refsType": "branch",
        "refsTypeValue": "feature-new-branch",
        "data": {
          "sourceType": "code",
          "repoType": "gitlab",
          "repoUrl": "https://gitlab.example.com/order/service.git",
          "branch": "feature-new-branch",
          "workPath": "./src"
        }
      }
    ]
  }
}
```

### 示例3: 添加新任务

```json
{
  "pipeline": {
    "pipelineId": "pipe-001",
    "name": "订单服务构建流水线",
    "spaceId": 1001,
    "stages": [
      {
        "id": "stage-001",
        "name": "构建阶段",
        "steps": [
          {
            "id": "step-001",
            "name": "Maven构建",
            "tasks": [
              { "id": "task-001", "name": "编译打包" },
              { "id": "task-new-001", "name": "代码扫描" }
            ]
          }
        ]
      }
    ]
  },
  "taskDataList": [
    {
      "id": "task-001",
      "data": { "name": "编译打包", "jobType": "MavenBuild" }
    },
    {
      "id": "task-new-001",
      "data": {
        "name": "代码扫描",
        "jobType": "SonarQube",
        "taskCategory": "CodeScanner"
      }
    }
  ]
}
```

### 示例4: 更新触发方式

```json
{
  "pipeline": {
    "pipelineId": "pipe-001",
    "name": "订单服务构建流水线",
    "spaceId": 1001,
    "triggerInfo": {
      "triggerType": 1,
      "triggerParams": {
        "cron": "0 0 2 * * ?"
      }
    }
  }
}
```

---

## 响应示例

### 成功响应

```json
{
  "code": 0,
  "message": "success",
  "data": "pipe-001",
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 失败响应

```json
{
  "code": -1,
  "message": "更新流水线失败: 流水线不存在或已被删除",
  "data": null,
  "requestId": "550e8400-e29b-41d4-a716-446655440001"
}
```

---

## 错误码

| 错误码 | 说明 |
|-------|------|
| 0 | 成功 |
| -1 | 通用失败（具体信息见message） |
| 401 | 无API访问权限 |
| 429 | 请求过于频繁（触发限流） |

---

## 注意事项

1. **pipelineId 保持不变**：更新后 pipelineId 与原 ID 相同
2. **全量更新**：传入的配置会完全覆盖原有配置，不传的字段会被清空
3. **spaceId 为 Long 类型**：不要传字符串
4. **需要编辑权限**：确保有编辑该流水线的权限
5. **taskDataList 不能为空**：如果需要执行流水线，taskDataList 必须有值
6. **ID保留**：阶段/步骤/任务的 ID 必须保留原值，不能生成新的 UUID
