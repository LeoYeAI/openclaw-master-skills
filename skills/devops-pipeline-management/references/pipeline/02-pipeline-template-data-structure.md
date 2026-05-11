# 流水线模板数据结构

本文档详细定义了质效平台 4.0 流水线模板的完整数据结构。

## 概述

流水线模板用于保存可复用的流水线配置，方便快速创建新的流水线。模板与流水线共享相似的数据结构，但有一些特定于模板的字段。

## 模板数据结构

### IFormFlowTemplate - 模板表单配置

| 字段 | ��型 | 必填 | 说明 |
|------|------|------|------|
| `pipelineTemplateName` | `string` | 是 | 模板名称 |
| `pipelineTemplateLanguage` | `string` | 是 | 模板语言标识 |
| `description` | `string` | 否 | 模板描述 |
| `status` | `number` | 否 | 模板状态：0-禁用，1-启用 |
| `pipelineTemplateVisibleRangeType` | `string` | 是 | 可见范围类型 |
| `divisionId` | `string` | 否 | 组织/部门 ID |

### TypeScript 定义

```typescript
export interface IFormFlowTemplate {
  pipelineTemplateName: string
  pipelineTemplateLanguage: string
  description: string
  status?: number
  pipelineTemplateVisibleRangeType: string
  divisionId: string
}
```

## 完整模板数据结构

模板保存时使用的数据结构，包含模板元信息和流水线配置。

```typescript
interface IPipelineTemplate {
  // 模板基本信息
  pipelineTemplateId: string | number
  pipelineTemplateName: string
  pipelineTemplateLanguage: string
  description: string
  status: number                              // 0: 禁用, 1: 启用
  pipelineTemplateVisibleRangeType: string    // 可见范围类型
  divisionId: string                          // 组织 ID
  creator: string                             // 创建者
  createTime: string                          // 创建时间
  updateTime: string                          // 更新时间

  // 流水线配置（继承自 IFlowData.pipeline）
  pipelineConfig: {
    name: string                              // 默认流水线名称
    aliasId: string                           // 别名
    label: string[]                           // 标签
    sources: ISource[]                        // 流水线源（模板中可能为空）
    stages: IStage[]                          // 阶段配置
  }

  // 任务配置列表
  taskDataList: ITaskData[]                   // 任务详细配置
}
```

## 模板完整数据示例

```json
{
  "pipelineTemplateId": "template-001",
  "pipelineTemplateName": "Java Maven 构建模板",
  "pipelineTemplateLanguage": "java",
  "description": "适用于 Java Maven 项目的标准构建流程模板",
  "status": 1,
  "pipelineTemplateVisibleRangeType": "division",
  "divisionId": "org-001",
  "creator": "admin",
  "createTime": "2024-01-01 10:00:00",
  "updateTime": "2024-01-15 14:30:00",

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
              },
              {
                "id": "task-sonar",
                "name": "代码扫描",
                "nodeType": "custom-task-node",
                "idx": 1
              }
            ]
          }
        ]
      },
      {
        "id": "stage-deploy",
        "name": "部署",
        "nodeType": "custom-stage-node",
        "steps": [
          {
            "id": "step-002",
            "name": "部署步骤",
            "nodeType": "custom-step-node",
            "driven": 0,
            "idx": 0,
            "tasks": [
              {
                "id": "task-docker",
                "name": "镜像构建",
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
        "script": "mvn -B clean package -Dmaven.test.skip=true",
        "workPath": "",
        "sourceId": "",
        "jdkVersion": "JDK1.8",
        "mavenVersion": "Maven3.3.9",
        "selectedMavenRepos": [],
        "uploadArtifact": true,
        "artifactPath": ["target/"],
        "artifactSuffix": "jar",
        "artifactCompress": true,
        "compressType": "TAR(.tgz)",
        "packagedName": "Artifacts_${PIPELINE_LOG_ID}",
        "idInTemplate": "task-maven",
        "dependencies": []
      }
    },
    {
      "id": "task-sonar",
      "data": {
        "taskCategory": "CodeScanner",
        "jobType": "SonarQube",
        "name": "代码扫描",
        "script": "",
        "workPath": "",
        "sourceId": "",
        "idInTemplate": "task-sonar",
        "dependencies": []
      }
    },
    {
      "id": "task-docker",
      "data": {
        "taskCategory": "DockerBuild",
        "jobType": "DockerBuildAndUpload",
        "name": "镜像构建",
        "workPath": "",
        "sourceId": "",
        "dockerfilePath": "Dockerfile",
        "imageName": "${PIPELINE_NAME}",
        "tag": "${BUILD_NUMBER}",
        "preDependTaskId": "",
        "idInTemplate": "task-docker",
        "dependencies": []
      }
    }
  ]
}
```

## 模板与流水线的差异

| 特性 | 模板 | 流水线 |
|------|------|--------|
| `sources` | 通常为空（使用时配置） | 必须配置 |
| `pipelineId` | 无 | 有 |
| `workPath` | 无需选择 | 必须选择 |
| `sourceId` | 为空 | 关联流水线源 |
| `idInTemplate` | 有（用于追踪） | 可能为空 |
| 运行状态 | 无 | 有 |
| 触发配置 | 可配置默认值 | 完整配置 |

## 模板可见范围类型

```typescript
enum TemplateVisibleRangeType {
  PERSONAL = 'personal',        // 个人可见
  DIVISION = 'division',        // 部门可见
  SPACE = 'space',              // 空间可见
  SYSTEM = 'system'             // 系统模板（管理员创建）
}
```

## 模板状态

| 状态值 | 说明 |
|--------|------|
| `0` | 禁用 |
| `1` | 启用 |

## 模板 API 接口

### 获取模板列表

```typescript
// 普通模板列表
POST /devops/api/pipeline/template/queryNormalPipTemplatePage
{
  "pageNum": 1,
  "pageSize": 10,
  "pipelineTemplateName": "",     // 搜索关键字
  "status": 1                     // 状态筛选
}

// 系统模板列表
POST /devops/api/pipeline/template/queryAdminPipTemplatePage
```

### 获取模板详情

```typescript
GET /devops/api/pipeline/template/getPipTemplateById?pipelineTemplateId={id}
```

### 保存模板

```typescript
POST /devops/api/pipeline/template/savePipTemplate
{
  "pipelineTemplateId": "",
  "pipelineTemplateName": "模板名称",
  "pipelineTemplateLanguage": "java",
  "description": "描述",
  "status": 1,
  "pipelineTemplateVisibleRangeType": "division",
  "divisionId": "org-001",
  "pipelineConfig": { ... },
  "taskDataList": [ ... ]
}
```

### 复制模板

```typescript
POST /devops/api/pipeline/template/copyPipTemplate
{
  "pipelineTemplateId": "template-001",
  "pipelineTemplateName": "复制的新模板名称"
}
```

### 删除模板

```typescript
GET /devops/api/pipeline/template/delPipTemplate?pipelineTemplateId={id}
```

### 更新模板状态

```typescript
POST /devops/api/pipeline/template/updatePipTemplateStatus
{
  "pipelineTemplateId": "template-001",
  "status": 0    // 0: 禁用, 1: 启用
}
```

### 校验模板名称

```typescript
POST /devops/api/pipeline/template/checkPipTemplateName
{
  "pipelineTemplateName": "模板名称",
  "pipelineTemplateId": ""    // 更新时传入
}
```

### 校验任务参数

```typescript
POST /devops/api/pipeline/template/taskParams/validate
{
  // 任务配置数据
}
```

## 从模板创建流水线

使用模板创建流水线时的处理流程：

1. **复制模板配置**
   ```typescript
   const newFlowData = cloneDeep(templateData.pipelineConfig)
   ```

2. **生成新的 ID**
   ```typescript
   newFlowData.stages.forEach(stage => {
     stage.id = uuid()
     stage.steps.forEach(step => {
       step.id = uuid()
       step.tasks.forEach(task => {
         task.id = uuid()
       })
     })
   })
   ```

3. **清空模板特有字段**
   ```typescript
   taskData.data.idInTemplate = ''
   taskData.data.sourceId = ''
   taskData.data.workPath = ''
   ```

4. **用户配置流水线源**
   - 创建流水线后，用户需要配置流水线源
   - 系统会自动关联 `workPath` 和 `sourceId`

## 模板中的任务依赖

模板中定义的任务可能存在依赖关系（如 `preDependTaskId`），复制时需要重新映射：

```typescript
// 复制时维护 ID 映射关系
const taskIdMapping = {}

oldTaskDataList.forEach(oldTask => {
  const newId = uuid()
  taskIdMapping[oldTask.id] = newId
})

// 更新依赖引用
newTaskDataList.forEach(newTask => {
  if (newTask.data.preDependTaskId) {
    newTask.data.preDependTaskId = taskIdMapping[newTask.data.preDependTaskId] || ''
  }
})
```

## 模板数据校验

### 必填字段校验

```typescript
const validateTemplate = (template: IPipelineTemplate) => {
  const errors = []

  if (!template.pipelineTemplateName) {
    errors.push('模板名称不能为空')
  }

  if (!template.pipelineTemplateLanguage) {
    errors.push('模板语言不能为空')
  }

  if (!template.pipelineTemplateVisibleRangeType) {
    errors.push('可见范围不能为空')
  }

  // 校验任务配置
  template.taskDataList.forEach(taskData => {
    if (!taskData.data.name) {
      errors.push(`任务 ${taskData.id} 名称不能为空`)
    }
    if (!taskData.data.jobType) {
      errors.push(`任务 ${taskData.id} 类型不能为空`)
    }
  })

  return errors
}
```

## 相关文件

- 类型定义：`src/utils/graph/type.ts` (`IFormFlowTemplate`)
- API 接口：`src/api/template.ts`
- 模板组件：`src/views/flowLine/` 相关页面

## 组装流水线模板（分组流水线）

组装流水线用于组合多个子流水线，具有不同的数据结构：

### ISpacePipeline - 空间流水线信息

```typescript
export interface ISpacePipeline {
  spacePipelineId: string
  spacePipelineKey: string
  timeoutDuration: string
  buildNumber: number
  spaceId: string
  name: string
  pipelineName: string
  pipelineOwnerName: string
  pipelineOwner: string
  aliasId: string | null
  store: number
  runTimes: string | number
  pipelineStatus: string
  pipelineStatusName: string
  pipelineStageInfo: string
  duration?: string
  endTime?: string
  runRemark: string
  createTime?: string
  creator?: string
  triggerMode: string
  triggerModeName: string
  triggerUser: string
  label: Array<string>
  triggerInfo: ITriggerInfo
  timeExecution?: ITimeExecution | null
  webhookUrl?: string
  permissionList: Array<string>
}
```

### IGroupFlowData - 分组流水线数据

```typescript
export interface IGroupFlowData {
  pipeline: ISpacePipeline
  nodeDataList: Array<ITaskData>    // 子流水线节点配置
  nodes: Array<ITask>               // 画布节点
  edges: Array<IEdge>               // 画布连线
}

export interface IEdge {
  id: string
  source: {
    cell: string
    port: string
  }
  target: {
    cell: string
    port: string
  }
  vertices: Array<{
    x: number
    y: number
  }>
}
```

### IGroupFormFlow - 分组流水线表单

```typescript
export interface IGroupFormFlow {
  buildNumber: string
  name: string
  aliasId: string
  spacePipelineKey: string
  label: Array<string>
  timeExecutionSwitch?: boolean
  timeExecution?: ITimeExecution | null
  webhookUrl?: string
  isExecuteMachine?: string
  executeMachine?: string
  buildEnvironmentType?: string
  timeoutDuration: string
}
```
