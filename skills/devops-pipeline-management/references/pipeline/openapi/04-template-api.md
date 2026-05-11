# 模板 API

本文档定义流水线模板相关的 OpenAPI 接口。

---

## 保存模板

### 请求

```
POST /rest/openapi/pipeline/template/savePipTemplate
```

### 最小请求体

```json
{
  "pipelineTemplateName": "Java Maven 构建模板",
  "pipelineTemplateLanguage": "java",
  "pipelineTemplateVisibleRangeType": "personal",
  "pipelineConfig": {
    "name": "Maven构建流水线",
    "sources": [],
    "stages": []
  },
  "taskDataList": []
}
```

### 完整请求体

```json
{
  "pipelineTemplateId": null,
  "pipelineTemplateName": "Java Maven 构建模板",
  "pipelineTemplateLanguage": "java",
  "description": "适用于 Java Maven 项目的标准构建流程",
  "status": 1,
  "pipelineTemplateVisibleRangeType": "division",
  "divisionId": "org-001",
  "pipelineConfig": {
    "name": "Maven构建流水线",
    "aliasId": "",
    "label": ["Java", "Maven"],
    "sources": [],
    "stages": [
      {
        "id": "stage-build",
        "name": "构建",
        "nodeType": "custom-stage-node",
        "steps": [
          {
            "id": "step-001",
            "name": "构建步骤",
            "nodeType": "custom-step-node",
            "driven": 0,
            "idx": 0,
            "tasks": [
              {
                "id": "task-maven",
                "name": "Maven构建",
                "nodeType": "custom-task-node",
                "idx": 0
              }
            ]
          }
        ]
      }
    ]
  },
  "taskDataList": [
    {
      "id": "task-maven",
      "data": {
        "taskCategory": "Build",
        "jobType": "MavenBuild",
        "name": "Maven构建",
        "workPath": "",
        "sourceId": "",
        "jdkVersion": "JDK17",
        "mavenVersion": "Maven3.8.x",
        "script": "mvn clean package",
        "idInTemplate": "task-maven"
      }
    }
  ]
}
```

---

## 字段说明

### 模板基础信息

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `pipelineTemplateId` | string | 否 | 更新时必填 |
| `pipelineTemplateName` | string | 是 | 模板名称 |
| `pipelineTemplateLanguage` | string | 是 | 模板语言 |
| `description` | string | 否 | 描述 |
| `status` | number | 否 | 0-禁用, 1-启用 |
| `pipelineTemplateVisibleRangeType` | string | 是 | 可见范围 |
| `divisionId` | string | 条件 | 组织ID（division类型必填） |

### pipelineTemplateLanguage 枚举

| 值 | 说明 |
|---|------|
| `java` | Java |
| `nodejs` | Node.js |
| `python` | Python |
| `go` | Go |
| `cpp` | C++ |
| `general` | 通用 |

### pipelineTemplateVisibleRangeType 枚举

| 值 | 说明 |
|---|------|
| `personal` | 个人可见 |
| `division` | 部门可见 |
| `space` | 空间可见 |
| `system` | 系统模板 |

### status 枚举

| 值 | 说明 |
|---|------|
| `0` | 禁用 |
| `1` | 启用 |

---

## 获取模板详情

### 请求

```
GET /rest/openapi/pipeline/getPipTemplateById?pipelineTemplateId={id}
```

### 响应

```json
{
  "code": "200",
  "data": {
    "pipelineTemplateId": "template-001",
    "pipelineTemplateName": "Java Maven 构建模板",
    "pipelineTemplateLanguage": "java",
    "description": "...",
    "status": 1,
    "pipelineConfig": { ... },
    "taskDataList": [ ... ]
  }
}
```

---

## 查询模板列表

### 请求

```
POST /rest/openapi/pipeline/template/queryNormalPipTemplatePage
```

### 请求体

```json
{
  "pageNum": 1,
  "pageSize": 10,
  "pipelineTemplateName": "",
  "status": 1
}
```

### 响应

```json
{
  "code": "200",
  "data": {
    "list": [
      {
        "pipelineTemplateId": "template-001",
        "pipelineTemplateName": "Java Maven 构建模板",
        "pipelineTemplateLanguage": "java",
        "status": 1,
        "createTime": "2024-01-01 10:00:00",
        "creator": "admin"
      }
    ],
    "total": 100
  }
}
```

---

## 删除模板

### 请求

```
GET /rest/openapi/pipeline/template/delPipTemplate?pipelineTemplateId={id}
```

### 响应

```json
{
  "code": "200",
  "message": "success"
}
```

---

## 更新模板状态

### 请求

```
POST /rest/openapi/pipeline/template/updatePipTemplateStatus
```

### 请求体

```json
{
  "pipelineTemplateId": "template-001",
  "status": 0
}
```

---

## 复制模板

### 请求

```
POST /rest/openapi/pipeline/template/copyPipTemplate
```

### 请求体

```json
{
  "pipelineTemplateId": "template-001",
  "pipelineTemplateName": "复制的模板名称"
}
```

---

## 从模板创建流水线

从模板创建流水线的处理流程：

1. **获取模板详情**
2. **复制配置到新流水线**
3. **生成新的 ID**（pipelineId, stageId, taskId 等）
4. **清空模板特有字段**（idInTemplate, sourceId, workPath）
5. **用户配置代码源**

### 示例代码

```typescript
// 1. 获取模板
const template = await getTemplate(templateId)

// 2. 复制配置
const newPipeline = cloneDeep(template.pipelineConfig)

// 3. 生成新 ID
const taskIdMap = {}
newPipeline.stages.forEach(stage => {
  stage.id = uuid()
  stage.steps.forEach(step => {
    step.id = uuid()
    step.tasks.forEach(task => {
      taskIdMap[task.id] = uuid()
      task.id = taskIdMap[task.id]
    })
  })
})

// 4. 更新 taskDataList 中的 ID
const newTaskDataList = template.taskDataList.map(task => ({
  ...task,
  id: taskIdMap[task.id] || task.id,
  data: {
    ...task.data,
    idInTemplate: '',
    sourceId: '',
    workPath: ''
  }
}))

// 5. 创建流水线
await createPipeline({
  ...newPipeline,
  taskDataList: newTaskDataList
})
```
