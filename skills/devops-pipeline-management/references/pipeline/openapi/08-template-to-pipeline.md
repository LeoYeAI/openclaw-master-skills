# 模板转流水线数据转换

本文档说明如何从模板数据创建流水线，包括 ID 映射、数据校验等关键步骤。

---

## 概述

当用户基于模板创建流水线时，需要完成以下核心步骤：

1. **获取模板详情** - 调用 API 获取模板配置
2. **生成新 ID** - 为所有 stages、steps、tasks 生成新 UUID
3. **ID 映射追踪** - 记录原始任务 ID 到 `idInTemplate`
4. **数据校验** - 调用校验 API 验证任务配置
5. **组装流水线** - 合并校验结果到最终数据

---

## API 调用流程

```
1. GET /devops/api/pipeline/template/getPipTemplateById
   ↓
2. POST /devops/api/pipeline/validatePipelineTaskData
   ↓
3. POST /devops/api/pipeline/save
```

---

## Step 1: 获取模板详情

### 请求

```http
GET /devops/api/pipeline/template/getPipTemplateById?id={templateId}
```

### 响应

```json
{
  "code": "200",
  "data": {
    "pipelineTemplate": {
      "spaceId": "space-001",
      "customParameters": [],
      "stages": [
        {
          "id": "stage-original-001",
          "name": "构建阶段",
          "steps": [
            {
              "id": "step-original-001",
              "name": "构建步骤",
              "tasks": [
                {
                  "id": "task-original-001",
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
        "id": "task-original-001",
        "data": {
          "name": "Maven构建",
          "taskCategory": "Build",
          "jobType": "MavenBuild",
          "jdkVersion": "JDK17",
          "mavenVersion": "Maven3.8.x"
        }
      }
    ]
  }
}
```

---

## Step 2: 生成新 ID 并建立映射

### 核心逻辑

模板中的所有 ID 都需要替换为新的 UUID，同时保留原始 ID 的映射关系。

**转换规则**：

| 原始字段 | 转换后 |
|---------|--------|
| `stage.id` | 新 UUID |
| `step.id` | 新 UUID |
| `task.id` | 新 UUID |
| `taskData.id` | 同步更新为新 task.id |
| `taskData.data.idInTemplate` | 原始 task.id |

### 伪代码

```
function transformTemplateToPipeline(templateResponse):
    pipelineTemplate = templateResponse.pipelineTemplate
    taskDataList = templateResponse.taskDataList

    for stage in pipelineTemplate.stages:
        stage.id = generateUUID()

        for step in stage.steps:
            step.id = generateUUID()

            for task in step.tasks:
                oldTaskId = task.id
                newTaskId = generateUUID()

                // 查找对应的 taskData
                taskData = findTaskDataById(taskDataList, oldTaskId)

                if taskData:
                    // 记录原始 ID
                    taskData.data.idInTemplate = oldTaskId
                    // 更新为新 ID
                    taskData.id = newTaskId

                // 更新 task.id
                task.id = newTaskId

    return { pipelineTemplate, taskDataList }
```

### Python 示例

```python
import uuid

def transform_template_data(template_response: dict) -> dict:
    """将模板数据转换为流水线数据"""
    pipeline_template = template_response["pipelineTemplate"]
    task_data_list = template_response["taskDataList"]

    for stage in pipeline_template.get("stages", []):
        # 生成新的 stage ID
        stage["id"] = str(uuid.uuid4())

        for step in stage.get("steps", []):
            # 生成新的 step ID
            step["id"] = str(uuid.uuid4())

            for task in step.get("tasks", []):
                old_task_id = task["id"]
                new_task_id = str(uuid.uuid4())

                # 查找并更新对应的 taskData
                for task_data in task_data_list:
                    if task_data["id"] == old_task_id:
                        # 记录原始 ID（用于追溯）
                        task_data["data"]["idInTemplate"] = old_task_id
                        # 同步更新 taskData ID
                        task_data["id"] = new_task_id
                        break

                # 更新 task ID
                task["id"] = new_task_id

    return {
        "pipelineTemplate": pipeline_template,
        "taskDataList": task_data_list
    }
```

### 转换前后对比

**转换前**（模板数据）：

```json
{
  "stages": [
    {
      "id": "stage-001",
      "steps": [
        {
          "id": "step-001",
          "tasks": [
            { "id": "task-001", "name": "构建" }
          ]
        }
      ]
    }
  ],
  "taskDataList": [
    { "id": "task-001", "data": { "name": "构建" } }
  ]
}
```

**转换后**（流水线数据）：

```json
{
  "stages": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "steps": [
        {
          "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
          "tasks": [
            { "id": "c3d4e5f6-a7b8-9012-cdef-123456789012", "name": "构建" }
          ]
        }
      ]
    }
  ],
  "taskDataList": [
    {
      "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "data": {
        "name": "构建",
        "idInTemplate": "task-001"
      }
    }
  ]
}
```

---

## Step 3: 校验任务数据

### 请求

```http
POST /devops/api/pipeline/validatePipelineTaskData
Content-Type: application/json

{
  "taskDataList": [
    {
      "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "data": {
        "idInTemplate": "task-001",
        "name": "Maven构建",
        "taskCategory": "Build",
        "jobType": "MavenBuild",
        "jdkVersion": "JDK17",
        "mavenVersion": "Maven3.8.x",
        "workPath": "",
        "sourceId": ""
      }
    }
  ]
}
```

### 响应

```json
{
  "code": "200",
  "data": [
    {
      "taskParams": {
        "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
        "autoId": "auto-001",
        "data": {
          "name": "Maven构建",
          "taskCategory": "Build",
          "jobType": "MavenBuild",
          "jdkVersion": "JDK17",
          "mavenVersion": "Maven3.8.x",
          "taskParamList": [
            { "name": "GOAL", "value": "clean package" }
          ]
        }
      },
      "hasError": false
    }
  ]
}
```

### 校验结果处理

```python
def process_validation_result(validate_response: list, pipeline_id: str) -> list:
    """处理校验结果，组装最终的 taskDataList"""
    result = []

    for item in validate_response:
        task_params = item.get("taskParams", {})

        # 检查参数完整性
        has_error = False
        task_param_list = task_params.get("data", {}).get("taskParamList", [])
        for param in task_param_list:
            if not param.get("value") or not param.get("name"):
                has_error = True
                break

        result.append({
            "id": task_params["id"],
            "autoId": task_params.get("autoId"),
            "data": {
                **task_params["data"],
                "pipelineId": pipeline_id,
                "taskIsError": has_error or item.get("hasError", False)
            }
        })

    return result
```

---

## Step 4: 组装流水线数据

### 最终数据结构

```python
def assemble_pipeline_data(
    pipeline_template: dict,
    validated_task_list: list,
    pipeline_name: str,
    pipeline_alias: str,
    space_id: str
) -> dict:
    """组装完整的流水线数据"""
    return {
        "pipeline": {
            "pipelineId": "",  # 新建时为空
            "name": pipeline_name,
            "aliasId": pipeline_alias,
            "spaceId": space_id,
            "customParameters": pipeline_template.get("customParameters", []),
            "stages": pipeline_template["stages"]
        },
        "taskDataList": validated_task_list
    }
```

### 保存流水线

```http
POST /devops/api/pipeline/save
Content-Type: application/json

{
  "pipeline": {
    "name": "my-pipeline",
    "aliasId": "my-pipeline-alias",
    "spaceId": "space-001",
    "customParameters": [],
    "stages": [...]
  },
  "taskDataList": [...]
}
```

---

## 完整流程示例

### Python 完整示例

```python
import uuid
import requests

class TemplateToPipelineConverter:
    """模板转流水线转换器"""

    BASE_URL = "/devops/api"

    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def create_pipeline_from_template(
        self,
        template_id: str,
        pipeline_name: str,
        pipeline_alias: str,
        space_id: str
    ) -> dict:
        """从模板创建流水线"""

        # Step 1: 获取模板详情
        template_data = self._get_template_detail(template_id)

        # Step 2: 转换 ID
        transformed = self._transform_ids(template_data)

        # Step 3: 校验任务数据
        validated = self._validate_task_data(transformed["taskDataList"])

        # Step 4: 处理校验结果
        task_list = self._process_validation(validated, "")

        # Step 5: 组装并保存
        pipeline_data = {
            "pipeline": {
                "pipelineId": "",
                "name": pipeline_name,
                "aliasId": pipeline_alias,
                "spaceId": space_id,
                "customParameters": transformed["pipelineTemplate"].get("customParameters", []),
                "stages": transformed["pipelineTemplate"]["stages"]
            },
            "taskDataList": task_list
        }

        return self._save_pipeline(pipeline_data)

    def _get_template_detail(self, template_id: str) -> dict:
        """获取模板详情"""
        url = f"{self.BASE_URL}/pipeline/template/getPipTemplateById"
        resp = requests.get(url, params={"id": template_id}, headers=self.headers)
        return resp.json()["data"]

    def _transform_ids(self, template_response: dict) -> dict:
        """转换所有 ID"""
        pipeline_template = template_response["pipelineTemplate"]
        task_data_list = template_response["taskDataList"]

        for stage in pipeline_template.get("stages", []):
            stage["id"] = str(uuid.uuid4())

            for step in stage.get("steps", []):
                step["id"] = str(uuid.uuid4())

                for task in step.get("tasks", []):
                    old_id = task["id"]
                    new_id = str(uuid.uuid4())

                    for td in task_data_list:
                        if td["id"] == old_id:
                            td["data"]["idInTemplate"] = old_id
                            td["id"] = new_id
                            break

                    task["id"] = new_id

        return {
            "pipelineTemplate": pipeline_template,
            "taskDataList": task_data_list
        }

    def _validate_task_data(self, task_data_list: list) -> list:
        """校验任务数据"""
        url = f"{self.BASE_URL}/pipeline/validatePipelineTaskData"
        resp = requests.post(url, json={"taskDataList": task_data_list}, headers=self.headers)
        return resp.json()["data"]

    def _process_validation(self, validate_result: list, pipeline_id: str) -> list:
        """处理校验结果"""
        result = []
        for item in validate_result:
            tp = item.get("taskParams", {})

            has_error = item.get("hasError", False)
            for param in tp.get("data", {}).get("taskParamList", []):
                if not param.get("value") or not param.get("name"):
                    has_error = True
                    break

            result.append({
                "id": tp["id"],
                "autoId": tp.get("autoId"),
                "data": {
                    **tp["data"],
                    "pipelineId": pipeline_id,
                    "taskIsError": has_error
                }
            })
        return result

    def _save_pipeline(self, pipeline_data: dict) -> dict:
        """保存流水线"""
        url = f"{self.BASE_URL}/pipeline/save"
        resp = requests.post(url, json=pipeline_data, headers=self.headers)
        return resp.json()


# 使用示例
converter = TemplateToPipelineConverter(token="your-token")
result = converter.create_pipeline_from_template(
    template_id="template-001",
    pipeline_name="my-new-pipeline",
    pipeline_alias="my-pipeline",
    space_id="space-001"
)
print(result)
```

---

## 关键注意事项

### 1. ID 映射的重要性

`idInTemplate` 字段用于：
- 追溯任务来源
- 模板版本管理
- 任务配置对比

### 2. 模板与流水线的区别

| 特性 | 模板 | 流水线 |
|-----|------|--------|
| `workPath` | 可空 | 必须填写 |
| `sourceId` | 可空 | 必须关联代码源 |
| `pipelineId` | 不存在 | 必须存在 |
| 任务参数 | 可能不完整 | 必须完整 |

### 3. 校验错误处理

当 `taskIsError: true` 时：
- 表示任务配置不完整
- 需要用户补充必填参数
- 通常是 `workPath`、`sourceId` 等字段

### 4. 必填字段补充

创建流水线后，通常需要补充：
- `workPath` - 工作目录
- `sourceId` - 关联的代码源 ID
- 其他 jobType 特定字段

---

## 相关 API

| API | 说明 |
|-----|------|
| `GET /pipeline/template/getPipTemplateById` | 获取模板详情 |
| `POST /pipeline/validatePipelineTaskData` | 校验任务数据 |
| `POST /pipeline/save` | 保存流水线 |
| `POST /pipeline/source/save` | 添加代码源 |
| `POST /pipeline/task/save` | 更新任务配置 |
