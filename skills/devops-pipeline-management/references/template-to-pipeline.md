# 模板转流水线数据转换（仅转换组装）

本文档说明如何从模板数据转换组装成流水线数据，**只进行模板详情读取 → 数据转换组装 → 打印输出**，不进行校验和保存流水线。

---

## 概述

当用户基于模板创建流水线时，如果只需要将模板数据转换为流水线数据结构（用于预览、调试或后续处理），可以执行以下核心步骤：

1. **获取模板详情** - 调用 API 获取模板配置
2. **生成新 ID** - 为所有 stages、steps、tasks 生成新 UUID
3. **ID 映射追踪** - 记录原始任务 ID 到 `idInTemplate`
4. **补全任务数据字段** - 根据任务类型，结合 schema 自动补全缺失的必填字段和默认值
5. **组装流水线数据** - 合并转换后的模板和任务数据
6. **打印输出** - 输出转换后的流水线数据

**注意**：此流程不包含数据校验和保存到数据库的步骤，仅用于数据转换和展示。

---

## API 调用流程

```
1. GET /devops/api/ai-bff/rest/openapi/pipeline/getPipTemplateById
   ↓
2. 本地转换：
   - 生成新ID、建立映射
   - 补全任务数据字段（根据schema）
   - 组装流水线数据结构
   ↓
3. 打印转换后的流水线数据
```

---

## Step 1: 获取模板详情

### 请求

```http
GET /devops/api/ai-bff/rest/openapi/pipeline/getPipTemplateById?id={templateId}
```

### 响应

```json
{
  "code": "200",
  "data": {
    "pipelineTemplate": {
      "spaceId": 133,
      "pipelineTemplateVisibleRangeType": "group",
      "stages": [
        {
          "name": "新阶段",
          "id": "33d0805b-eda3-468e-9988-1c9fc45db48a",
          "nodeType": "custom-stage-node",
          "steps": [
            {
              "driven": 0,
              "name": "新步骤",
              "id": "5fcb4d78-4794-44d2-8dfa-a00c269e8867",
              "idx": 0,
              "nodeType": "custom-step-node",
              "tasks": [
                {
                  "name": "Node.js构建",
                  "id": "12c79673aa254bd497a5d841d5ff83c2",
                  "idx": 0,
                  "nodeType": "custom-task-node"
                }
              ]
            }
          ]
        }
      ],
      "description": "",
      "customParameters": [],
      "divisionId": "",
      "id": "640584d7-0cf4-4411-b265-c88e01bb2cc0",
      "pipelineTemplateType": 1,
      "pipelineTemplateName": "前端模板-2026-03-15-13-37-49",
      "pipelineTemplateLanguage": "Node.js",
      "status": 1
    },
    "taskDataList": [
      {
        "data": {
          "sourceId": "",
          "allHosts": false,
          "ignoreCoverageFailure": false,
          "uploadArtifact": true,
          "workPath": "",
          "artifactSuffix": "tar.gz",
          "shareType": 0,
          "enableSelfDefinedValues": false,
          "idInTemplate": "",
          "codeCoverGate": false,
          "compressType": "TAR(.tgz)",
          "jobType": "NpmBuild",
          "packagedName": "Artifacts_${PIPELINE_LOG_ID}",
          "enableCusArfUpDir": false,
          "stageId": "33d0805b-eda3-468e-9988-1c9fc45db48a",
          "createSharePubLink": 0,
          "artifactCompress": true,
          "nodeVersion": "v20.19.1",
          "nodeCustomVersion": "",
          "script": "#如需指定某个模块进行单独构建，可以通过 cd命令 进入目标模块所在路径，再执行构建命令，例如\n#cd devops-base/ai-base-service\nnpm set registry https://depend.iflytek.com/artifactory/api/npm/npm-repo\nnpm install\nnpm run build",
          "buildImageModel": "default",
          "dependencies": [],
          "skipExecution": false,
          "name": "Node.js构建",
          "shareIndate": 0,
          "artifactPath": [
            "dist/"
          ],
          "sysDefault": "default",
          "taskCategory": "Build"
        },
        "id": "12c79673aa254bd497a5d841d5ff83c2"
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

### Python 示例

```python
import uuid
import copy

def transform_template_data(template_response: dict) -> dict:
    """将模板数据转换为流水线数据（仅转换，不校验）"""
    # 深拷贝原始数据，避免修改原数据
    pipeline_template = copy.deepcopy(template_response["pipelineTemplate"])
    task_data_list = copy.deepcopy(template_response["taskDataList"])

    # 创建任务ID映射表：旧ID -> 新ID
    task_id_mapping = {}

    for stage in pipeline_template.get("stages", []):
        # 生成新的 stage ID
        stage["id"] = str(uuid.uuid4())

        for step in stage.get("steps", []):
            # 生成新的 step ID
            step["id"] = str(uuid.uuid4())

            for task in step.get("tasks", []):
                old_task_id = task["id"]
                new_task_id = str(uuid.uuid4())
                task_id_mapping[old_task_id] = new_task_id

                # 更新 task ID
                task["id"] = new_task_id

    # 更新 taskDataList 中的 ID 并添加 idInTemplate
    for task_data in task_data_list:
        old_id = task_data["id"]
        if old_id in task_id_mapping:
            new_id = task_id_mapping[old_id]
            # 记录原始 ID（用于追溯）
            if "data" not in task_data:
                task_data["data"] = {}
            task_data["data"]["idInTemplate"] = old_id
            # 同步更新 taskData ID
            task_data["id"] = new_id
        else:
            # 如果找不到映射，保持原ID但添加idInTemplate
            if "data" not in task_data:
                task_data["data"] = {}
            task_data["data"]["idInTemplate"] = old_id

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

## Step 3: 补全任务数据字段

### 核心逻辑

根据任务类型（`jobType` 字段），从 `devops-pipeline-management/references/pipeline/schemas/all-tasks/` 目录加载对应的 JSON Schema 文件，自动补全缺失的必填字段和默认值。

**补全规则**：
1. **必填字段补全**：检查 `required` 字段列表，如果字段缺失，则根据字段类型添加默认值：
   - `string` 类型：空字符串 `""`
   - `number` 类型：`0`
   - `boolean` 类型：`false`
   - `array` 类型：`[]`
   - `object` 类型：`{}`
2. **默认值补全**：检查 `properties` 中的 `default` 值，如果字段缺失，则添加默认值
3. **字段类型转换**：确保现有字段的值类型符合 schema 定义

**Schema 文件命名规则**：
- `jobType: "NpmBuild"` → `npm-build.schema.json`
- `jobType: "MavenBuild"` → `maven-build.schema.json`
- `jobType: "DockerBuild"` → `docker-build.schema.json`

**常见任务类型映射表**：

| jobType | schema 文件 |
|---------|-------------|
| NpmBuild | npm-build.schema.json |
| MavenBuild | maven-build.schema.json |
| GradleBuild | gradle-build.schema.json |
| GoBuild | go-build.schema.json |
| PythonBuild | python-build.schema.json |
| CppBuild | cpp-build.schema.json |
| NpmDockerBuild | npm-docker-build.schema.json |
| MavenDockerBuild | maven-docker-build.schema.json |
| DockerBuild | docker-build.schema.json |
| HostDeploy | host-deploy.schema.json |
| SAEDeploy | sae-deploy.schema.json |
| ManualReview | manual-review.schema.json |
| SonarQube | sonar-qube.schema.json |

完整列表请查看 `devops-pipeline-management/references/pipeline/schemas/all-tasks/` 目录。

### Python 示例

```python
import json
import os
import copy

def complete_task_data_with_schema(task_data_list: list, schema_base_path: str) -> list:
    """根据任务类型自动补全缺失字段和默认值"""
    completed_list = copy.deepcopy(task_data_list)

    for task_data in completed_list:
        if "data" not in task_data:
            task_data["data"] = {}

        data = task_data["data"]

        # 获取任务类型
        job_type = data.get("jobType")
        if not job_type:
            print(f"警告: 任务 {task_data.get('id', 'unknown')} 缺少 jobType 字段")
            continue

        # 构建 schema 文件路径
        # 将驼峰命名转换为短横线命名，如 "NpmBuild" -> "npm-build"
        import re
        schema_name = re.sub(r'(?<!^)(?=[A-Z])', '-', job_type).lower()
        schema_file = f"{schema_name}.schema.json"
        schema_path = os.path.join(schema_base_path, schema_file)

        # 加载 schema
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
        except FileNotFoundError:
            print(f"警告: 未找到 {job_type} 的 schema 文件: {schema_file}")
            continue
        except json.JSONDecodeError:
            print(f"错误: schema 文件格式无效: {schema_path}")
            continue

        # 补全必填字段
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in data:
                # 根据 schema 中的类型定义设置默认值
                field_schema = schema["properties"].get(field, {})
                field_type = field_schema.get("type", "string")

                if field_type == "string":
                    data[field] = ""
                elif field_type == "number":
                    data[field] = 0
                elif field_type == "boolean":
                    data[field] = False
                elif field_type == "array":
                    data[field] = []
                elif field_type == "object":
                    data[field] = {}
                else:
                    data[field] = ""

        # 补全默认值字段
        properties = schema.get("properties", {})
        for field_name, field_schema in properties.items():
            if "default" in field_schema and field_name not in data:
                data[field_name] = copy.deepcopy(field_schema["default"])

    return completed_list
```

### 补全前后对比

**补全前**（转换后的数据）：
```json
{
  "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "data": {
    "name": "Node.js构建",
    "jobType": "NpmBuild",
    "taskCategory": "Build",
    "idInTemplate": "task-original-001"
  }
}
```

**补全后**（根据 npm-build.schema.json）：
```json
{
  "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "data": {
    "name": "Node.js构建",
    "jobType": "NpmBuild",
    "taskCategory": "Build",
    "idInTemplate": "task-original-001",
    "workPath": "",
    "sourceId": "",
    "buildImageModel": "default",
    "executeImageId": "",
    "sysDefault": "default",
    "nodeVersion": "",
    "nodeCustomVersion": "",
    "script": "#如需指定某个模块进行单独构建，可以通过 cd命令 进入目标模块所在路径，再执行构建命令，例如\n#cd devops-base/ai-base-service\nnpm set registry https://depend.iflytek.com/artifactory/api/npm/npm-repo\nnpm install\nnpm run build",
    "uploadArtifact": true,
    "artifactPath": ["dist/"],
    "artifactSuffix": [],
    "artifactCompress": true,
    "compressType": "TAR(.tgz)",
    "packagedName": "Artifacts_${PIPELINE_LOG_ID}",
    "dependencies": []
  }
}
```

---

## Step 4: 组装流水线数据

### 数据结构组装

```python
import copy

def assemble_pipeline_data(
    transformed_data: dict,
    pipeline_name: str,
    pipeline_alias: str,
    space_id: str
) -> dict:
    """组装完整的流水线数据结构（仅组装，不保存）"""
    pipeline_template = transformed_data["pipelineTemplate"]
    task_data_list = transformed_data["taskDataList"]

    # 创建流水线对象，保留模板中的常见字段
    pipeline = {
        "pipelineId": "",  # 新建时为空
        "name": pipeline_name,
        "aliasId": pipeline_alias,
        "spaceId": space_id,
        "customParameters": copy.deepcopy(pipeline_template.get("customParameters", [])),
        "stages": copy.deepcopy(pipeline_template.get("stages", []))
    }

    # 可选：保留模板中的其他常见字段（如description等）
    # 注意：流水线可能不需要所有模板字段，这里只保留可能通用的字段
    optional_fields = ["description", "divisionId", "status"]
    for field in optional_fields:
        if field in pipeline_template and field not in pipeline:
            pipeline[field] = copy.deepcopy(pipeline_template[field])

    return {
        "pipeline": pipeline,
        "taskDataList": copy.deepcopy(task_data_list)
    }
```

---

## 完整流程示例

### Python 完整示例（仅转换和打印）

```python
import uuid
import json
import requests

class TemplateToPipelineConverter:
    """模板转流水线转换器（仅转换，不校验不保存）"""

    SCHEMA_BASE_PATH = "devops-pipeline-management/references/pipeline/schemas/all-tasks"

    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def convert_template_to_pipeline(
        self,
        template_id: str,
        pipeline_name: str,
        pipeline_alias: str,
        space_id: str
    ) -> dict:
        """从模板转换流水线数据（仅转换，不保存）"""

        # Step 1: 获取模板详情
        template_data = self._get_template_detail(template_id)

        # Step 2: 转换 ID
        transformed = self._transform_ids(template_data)

        # Step 3: 补全任务数据字段
        completed = self._complete_task_data(transformed)

        # Step 4: 组装流水线数据
        pipeline_data = self._assemble_pipeline_data(
            completed, pipeline_name, pipeline_alias, space_id
        )

        # Step 5: 打印组装后的数据
        self._print_pipeline_data(pipeline_data)

        return pipeline_data

    def _get_template_detail(self, template_id: str) -> dict:
        """获取模板详情"""
        url = f"/devops/api/ai-bff/rest/openapi/pipeline/getPipTemplateById"
        resp = requests.get(url, params={"id": template_id}, headers=self.headers)
        return resp.json()["data"]

    def _transform_ids(self, template_response: dict) -> dict:
        """转换所有 ID"""
        import copy

        # 深拷贝原始数据，避免修改原数据
        pipeline_template = copy.deepcopy(template_response["pipelineTemplate"])
        task_data_list = copy.deepcopy(template_response["taskDataList"])

        # 创建任务ID映射表：旧ID -> 新ID
        task_id_mapping = {}

        for stage in pipeline_template.get("stages", []):
            stage["id"] = str(uuid.uuid4())

            for step in stage.get("steps", []):
                step["id"] = str(uuid.uuid4())

                for task in step.get("tasks", []):
                    old_id = task["id"]
                    new_id = str(uuid.uuid4())
                    task_id_mapping[old_id] = new_id
                    task["id"] = new_id

        # 更新 taskDataList 中的 ID 并添加 idInTemplate
        for task_data in task_data_list:
            old_id = task_data["id"]
            if old_id in task_id_mapping:
                new_id = task_id_mapping[old_id]
                # 确保data字段存在
                if "data" not in task_data:
                    task_data["data"] = {}
                # 记录原始 ID（用于追溯）
                task_data["data"]["idInTemplate"] = old_id
                # 同步更新 taskData ID
                task_data["id"] = new_id
            else:
                # 如果找不到映射，保持原ID但添加idInTemplate
                if "data" not in task_data:
                    task_data["data"] = {}
                task_data["data"]["idInTemplate"] = old_id

        return {
            "pipelineTemplate": pipeline_template,
            "taskDataList": task_data_list
        }

    def _complete_task_data(self, transformed_data: dict) -> dict:
        """根据任务类型自动补全缺失字段和默认值"""
        import json
        import os
        import copy
        import re

        pipeline_template = copy.deepcopy(transformed_data["pipelineTemplate"])
        task_data_list = copy.deepcopy(transformed_data["taskDataList"])

        for task_data in task_data_list:
            if "data" not in task_data:
                task_data["data"] = {}

            data = task_data["data"]

            # 获取任务类型
            job_type = data.get("jobType")
            if not job_type:
                print(f"警告: 任务 {task_data.get('id', 'unknown')} 缺少 jobType 字段")
                continue

            # 构建 schema 文件路径
            # 将驼峰命名转换为短横线命名，如 "NpmBuild" -> "npm-build"
            schema_name = re.sub(r'(?<!^)(?=[A-Z])', '-', job_type).lower()
            schema_file = f"{schema_name}.schema.json"
            schema_path = os.path.join(self.SCHEMA_BASE_PATH, schema_file)

            # 加载 schema
            try:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
            except FileNotFoundError:
                print(f"警告: 未找到 {job_type} 的 schema 文件: {schema_file}")
                continue
            except json.JSONDecodeError:
                print(f"错误: schema 文件格式无效: {schema_path}")
                continue

            # 补全必填字段
            required_fields = schema.get("required", [])
            for field in required_fields:
                if field not in data:
                    # 根据 schema 中的类型定义设置默认值
                    field_schema = schema["properties"].get(field, {})
                    field_type = field_schema.get("type", "string")

                    if field_type == "string":
                        data[field] = ""
                    elif field_type == "number":
                        data[field] = 0
                    elif field_type == "boolean":
                        data[field] = False
                    elif field_type == "array":
                        data[field] = []
                    elif field_type == "object":
                        data[field] = {}
                    else:
                        data[field] = ""

            # 补全默认值字段
            properties = schema.get("properties", {})
            for field_name, field_schema in properties.items():
                if "default" in field_schema and field_name not in data:
                    data[field_name] = copy.deepcopy(field_schema["default"])

        return {
            "pipelineTemplate": pipeline_template,
            "taskDataList": task_data_list
        }

    def _assemble_pipeline_data(
        self,
        transformed_data: dict,
        pipeline_name: str,
        pipeline_alias: str,
        space_id: str
    ) -> dict:
        """组装流水线数据"""
        import copy

        pipeline_template = transformed_data["pipelineTemplate"]
        task_data_list = transformed_data["taskDataList"]

        # 创建流水线对象，保留模板中的常见字段
        pipeline = {
            "pipelineId": "",
            "name": pipeline_name,
            "aliasId": pipeline_alias,
            "spaceId": space_id,
            "customParameters": copy.deepcopy(pipeline_template.get("customParameters", [])),
            "stages": copy.deepcopy(pipeline_template.get("stages", []))
        }

        # 可选：保留模板中的其他常见字段（如description等）
        # 注意：流水线可能不需要所有模板字段，这里只保留可能通用的字段
        optional_fields = ["description", "divisionId", "status"]
        for field in optional_fields:
            if field in pipeline_template and field not in pipeline:
                pipeline[field] = copy.deepcopy(pipeline_template[field])

        return {
            "pipeline": pipeline,
            "taskDataList": copy.deepcopy(task_data_list)
        }

    def _print_pipeline_data(self, pipeline_data: dict):
        """打印组装后的流水线数据"""
        print("=== 转换后的流水线数据 ===")
        print(json.dumps(pipeline_data, indent=2, ensure_ascii=False))
        print("==========================")


# 使用示例
if __name__ == "__main__":
    # 创建转换器实例
    converter = TemplateToPipelineConverter(token="your-token")

    # 执行转换并打印结果
    result = converter.convert_template_to_pipeline(
        template_id="template-001",
        pipeline_name="my-new-pipeline",
        pipeline_alias="my-pipeline",
        space_id="space-001"
    )

    # result 包含转换后的完整流水线数据
    print(f"转换完成！流水线数据已生成，共 {len(result['pipeline']['stages'])} 个阶段")
```

### 输出示例

```
=== 转换后的流水线数据 ===
{
  "pipeline": {
    "pipelineId": "",
    "name": "my-new-pipeline",
    "aliasId": "my-pipeline",
    "spaceId": "space-001",
    "customParameters": [],
    "stages": [
      {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "name": "构建阶段",
        "steps": [
          {
            "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
            "name": "构建步骤",
            "tasks": [
              {
                "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
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
      "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "data": {
        "name": "Maven构建",
        "taskCategory": "Build",
        "jobType": "MavenBuild",
        "jdkVersion": "JDK17",  // 模板原始值
        "mavenVersion": "Maven3.8.x",  // 模板原始值
        "idInTemplate": "task-original-001",
        "workPath": "",  // 补全的必填字段
        "sourceId": "",  // 补全的必填字段
        "buildImageModel": "default",  // 补全的默认值字段
        "executeImageId": "",  // 补全的必填字段
        "selectedMavenRepos": [],  // 补全的默认值字段
        "selectedMavenSetting": "",
        "artifactPath": [],
        "artifactSuffix": [],
        "artifactCompress": true,
        "compressType": "TAR(.tgz)",
        "packagedName": "Artifacts_${PIPELINE_LOG_ID}",
        "dependencies": []
        // ... 其他根据 schema 补全的字段
      }
    }
  ]
}
==========================
转换完成！流水线数据已生成，共 1 个阶段，任务数据已根据 schema 补全
```

---

## 关键注意事项

### 1. ID 映射的重要性

`idInTemplate` 字段用于：
- 追溯任务来源
- 模板版本管理
- 任务配置对比

### 2. 仅转换不保存

此流程**包含**以下操作：
- 模板数据读取和转换
- ID 重新生成和映射
- 根据 schema 补全缺失字段和默认值
- 流水线数据结构组装

此流程**不包含**以下操作：
- 保存到数据库（`/pipeline/save`）
- 关联代码源（`workPath`、`sourceId` 等字段的实际值填充）

### 3. 字段保留说明

转换过程中会保留所有原始数据字段：

**必保留字段**：
- `pipelineTemplate.stages` 及其所有嵌套字段（`name`、`nodeType`、`idx`、`driven` 等）
- `pipelineTemplate.customParameters`
- `taskDataList` 中的所有任务数据字段

**ID 转换**：
- `stage.id`、`step.id`、`task.id` 替换为新 UUID
- `taskData.id` 同步更新为新 task.id
- `taskData.data.idInTemplate` 添加原始 task.id 记录

**可选保留字段**：
- `description`、`divisionId`、`status` 等模板元数据字段
- 其他 `pipelineTemplate` 中的自定义字段

**深拷贝保护**：使用 `copy.deepcopy()` 确保原始数据不被修改，所有字段完整保留。

### 4. Schema补全说明

根据任务类型自动补全缺失字段和默认值：

**补全规则**：
1. **必填字段补全**：检查 schema 中的 `required` 字段列表，如果字段缺失则根据字段类型添加默认值
2. **默认值补全**：检查 schema `properties` 中的 `default` 值，如果字段缺失则添加默认值
3. **字段保留**：已存在的字段值不会被覆盖，保持模板原始数据

**Schema文件查找**：
- 根据 `jobType` 字段确定 schema 文件（驼峰转短横线命名）
- 从 `devops-pipeline-management/references/pipeline/schemas/all-tasks/` 目录加载
- 如果找不到对应 schema 文件，跳过该任务的补全并输出警告

**注意事项**：
- `workPath`、`sourceId` 等流水线特定字段会补全为空字符串，需要用户后续填写
- 模板中的自定义字段会完整保留，不会因为 schema 中不存在而被移除
- 补全过程不影响 stages 和 pipelineTemplate 的其他结构

### 5. 使用场景

此转换流程适用于：
- 流水线数据预览
- 调试模板转换逻辑
- 数据迁移或导出
- 测试环境数据准备

### 6. 后续操作

转换后的流水线数据已包含所有必填字段和默认值，但还需要：
1. **填写实际值**：为 `workPath`、`sourceId` 等字段填写具体的流水线配置值
2. **调用保存 API**：使用 `/pipeline/save` 将流水线保存到数据库

---

## 相关 API

| API | 说明 |
|-----|------|
| `GET /devops/api/ai-bff/rest/openapi/pipeline/getPipTemplateById` | 获取模板详情（本流程唯一需要的 API）|

**注意**：本流程仅使用获取模板详情的 API，其他 API（如校验、保存）不在本流程范围内。