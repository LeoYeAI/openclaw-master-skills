---

name: pipeline-task-delete
description: 删除流水线中的任务节点。当用户需要从流水线中移除构建任务、部署任务、扫描任务等时使用此功能。

触发关键词："删除任务"、"移除任务"、"删除节点"、"流水线删除任务"
---

# 删除任务节点

> ⚠️ **大模型执行约束（必须严格遵守）**
>
> **继承全局约束**：本功能同时遵守 [SKILL.md](../SKILL.md) 中定义的全局执行约束。
>
> **本功能特定约束**：删除任务是流水线更新流程的一部分，删除操作由 [pipeline-update.md](./pipeline-update.md) 统一管理。

## 执行铁律

| 约束编号 | 约束类型 | 约束说明 | 违反后果 |
|---------|---------|---------|---------|
| D1 | 前置确认 | 删除前必须确认用户意图，防止误删 | 误删重要任务 |
| D2 | 双重移除 | 必须同时从 stages 和 taskDataList 中移除 | 数据不一致 |
| D3 | 依赖检查 | 检查是否有其他任务依赖此任务 | 关联任务执行失败 |
| D4 | 返回配置 | 删除后返回更新后的 pipeline 配置，由外部流程统一保存 | 配置丢失 |

---

## 功能描述

从已有流水线中删除任务节点。删除任务需要：
1. 确认要删除的任务
2. 检查任务依赖关系
3. 从 stages 和 taskDataList 中同时移除

---

## 删除任务流程

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           删除任务节点完整流程                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  步骤1: 解析用户输入                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 输入: "删除流水线pipe-001的Maven构建任务"                                  │    │
│  │ 输出: { pipelineId, taskName }                                           │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤2: 获取流水线详情                                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ API: GET /rest/openapi/pipeline/edit                                    │    │
│  │ 目的: 找到需要删除的任务                                                  │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤3: 确认删除任务                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 展示任务信息 → 用户确认 → 检查依赖关系                                     │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤4: 执行删除                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 从 stages.tasks 和 taskDataList 中移除任务                              │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                          │
│                                      ▼                                          │
│  步骤5: 返回更新后的配置                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ 返回更新后的 pipeline 配置                                              │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 详细步骤说明

### 步骤1: 解析用户输入

**输入示例**:
```
"删除流水线 pipe-001 的 Maven 构建任务"
"移除 pipeline-abc 中的部署任务"
"删除构建阶段的单元测试任务"
```

**需要提取的信息**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| pipelineId | string | 是 | 流水线ID |
| taskName | string | 否 | 任务名称（可选，不指定则显示列表让用户选择） |

---

### 步骤2: 获取流水线详情

**API**: `GET /rest/openapi/pipeline/edit?pipelineId={pipelineId}`

遍历 stages 找到目标任务：

```python
def find_task_in_pipeline(pipeline, task_name):
    """在流水线中查找任务"""
    for stage in pipeline.get("stages", []):
        for step in stage.get("steps", []):
            for task in step.get("tasks", []):
                if task.get("name") == task_name:
                    return {
                        "stage_id": stage.get("id"),
                        "stage_name": stage.get("name"),
                        "step_id": step.get("id"),
                        "step_name": step.get("name"),
                        "task_id": task.get("id"),
                        "task_name": task.get("name")
                    }
    return None
```

---

### 步骤3: 确认删除任务

#### 3.1 展示任务信息

```
⚠️ 确认删除任务
========================================
任务名称: Maven构建
任务ID: task-001
所属阶段: 构建阶段
所属步骤: Maven构建
----------------------------------------
⚠️ 确定要删除此任务吗？
```

#### 3.2 检查依赖关系

```python
def check_task_dependencies(pipeline, task_id):
    """检查是否有其他任务依赖此任务"""
    dependencies = []

    for td in pipeline.get("taskDataList", []):
        task_data = td.get("data", {})
        deps = task_data.get("dependencies", [])
        if task_id in deps:
            # 找到依赖此任务的其他任务
            for stage in pipeline.get("stages", []):
                for step in stage.get("steps", []):
                    for task in step.get("tasks", []):
                        if task.get("id") == td.get("id"):
                            dependencies.append({
                                "task_id": td.get("id"),
                                "task_name": task.get("name"),
                                "stage_name": stage.get("name"),
                                "step_name": step.get("name")
                            })

    return dependencies


# 检查示例
deps = check_task_dependencies(pipeline, "task-001")
if deps:
    print("⚠️ 警告: 以下任务依赖此任务:")
    for dep in deps:
        print(f"  - {dep['task_name']} ({dep['stage_name']} / {dep['step_name']})")
    print("删除后可能导致这些任务执行失败!")
```

---

### 步骤4: 执行删除

从两个位置同时移除任务：

```python
def delete_task(pipeline, task_id):
    """删除任务"""

    # 1. 从 stages 结构中移除
    for stage in pipeline.get("stages", []):
        for step in stage.get("steps", []):
            step["tasks"] = [
                t for t in step.get("tasks", [])
                if t.get("id") != task_id
            ]

    # 2. 从 taskDataList 中移除
    pipeline["taskDataList"] = [
        td for td in pipeline.get("taskDataList", [])
        if td.get("id") != task_id
    ]

    return pipeline
```

---

### 步骤5: 返回更新后的配置

删除完成后，返回更新后的 pipeline 配置：

```python
# 删除任务后返回更新后的配置
# 由 pipeline-update.md 统一保存
return pipeline
```

---

## 完整删除示例

### 示例: 删除 Maven 构建任务

```python
def delete_task_from_pipeline(pipeline_id: str, task_name: str = None):
    """从流水线中删除任务"""

    # 1. 获取流水线详情
    pipeline = get_pipeline_edit(pipeline_id)

    # 2. 如果未指定任务名称，显示任务列表让用户选择
    if not task_name:
        task_name = await select_task_from_list(pipeline)

    # 3. 查找任务
    task_info = find_task_in_pipeline(pipeline, task_name)
    if not task_info:
        print(f"❌ 未找到任务: {task_name}")
        return pipeline

    # 4. 确认删除
    print(f"\n⚠️ 确认删除任务:")
    print(f"   任务名称: {task_info['task_name']}")
    print(f"   所属阶段: {task_info['stage_name']}")
    print(f"   所属步骤: {task_info['step_name']}")

    confirm = await prompt_confirm("确定要删除此任务吗?")
    if not confirm:
        print("❌ 已取消删除")
        return pipeline

    # 5. 检查依赖
    deps = check_task_dependencies(pipeline, task_info["task_id"])
    if deps:
        force = await prompt_confirm(
            f"⚠️ 有 {len(deps)} 个任务依赖此任务，强制删除?",
            default=False
        )
        if not force:
            print("❌ 已取消删除")
            return pipeline

    # 6. 执行删除
    pipeline = delete_task(pipeline, task_info["task_id"])

    print(f"\n✅ 已删除任务: {task_name}")

    # 7. 返回更新后的配置（由 pipeline-update 保存）
    return pipeline


async def select_task_from_list(pipeline):
    """从任务列表中选择"""
    tasks = []
    for stage in pipeline.get("stages", []):
        for step in stage.get("steps", []):
            for task in step.get("tasks", []):
                tasks.append({
                    "label": f"{task['name']} ({stage['name']}/{step['name']})",
                    "value": task['name']
                })

    return await prompt_choice("请选择要删除的任务:", tasks)
```

---

## 命令行方式

```bash
# 删除指定任务
python -m scripts/main task-delete \
  --pipeline-id pipe-001 \
  --task-name "Maven构建"

# 删除任务（交互式选择）
python -m scripts/main task-delete \
  --pipeline-id pipe-001
```

---

## 注意事项

1. **双重移除**：必须同时从 `stages[].steps[].tasks[]` 和 `taskDataList[]` 中移除
2. **依赖检查**：删除前检查是否有其他任务依赖此任务
3. **确认删除**：删除前必须让用户确认，防止误删
4. **统一保存**：删除任务是流水线更新流程的一部分，由 [pipeline-update.md](./pipeline-update.md) 统一保存
5. **不可恢复**：删除操作不可逆，删除后任务配置将丢失
