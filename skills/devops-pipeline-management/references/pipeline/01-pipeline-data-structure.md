# 流水线数据结构

本文档详细定义了质效平台 4.0 流水线的完整数据结构。

## 核心数据结构概览

```
IFlowData
├── pipeline: IPipeline          # 流水线主体配置
└── taskDataList: ITaskData[]    # 任务配置数据列表
```

## IFlowData - 流水线完整数据

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `pipeline` | `IPipeline` | 是 | 流水线主体信息 |
| `taskDataList` | `ITaskData[]` | 否 | 任务详细配置数据列�� |
| `taskDataParamList` | `ITaskData[]` | 否 | 任务参数配置列表 |

### TypeScript 定义

```typescript
export interface IFlowData {
  pipeline: IPipeline
  taskDataList: Array<ITaskData>
  taskDataParamList?: Array<ITaskData>
}
```

## IPipeline - 流水线主体

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `pipelineId` | `string \| number \| null` | 否 | 流水线唯一标识（新建时为 null） |
| `spaceId` | `number \| string \| null` | 否 | 空间 ID |
| `name` | `string \| null` | 是 | 流水线名称 |
| `aliasId` | `string \| null` | 否 | 流水线别名 ID |
| `store` | `number` | 否 | 收藏状态：0-未收藏，1-已收藏 |
| `runTimes` | `string \| number` | 否 | 运行次数 |
| `pipelineStatus` | `string` | 否 | 流水线状态码 |
| `pipelineStatusName` | `string` | 否 | 流水线状态名称 |
| `pipelineStageInfo` | `string` | 否 | 阶段信息（序列化字符串） |
| `duration` | `string` | 否 | 执行时长 |
| `endTime` | `string` | 否 | 结束时间 |
| `runRemark` | `string` | 否 | 运行备注 |
| `createTime` | `string` | 否 | 创建时间 |
| `creator` | `string` | 否 | 创建者 |
| `triggerMode` | `string` | 否 | 触发方式代码 |
| `triggerModeName` | `string` | 否 | 触发方式名称 |
| `triggerUser` | `string` | 否 | 触发用户 |
| `label` | `Array<string>` | 否 | 标签列表 |
| `triggerInfo` | `ITriggerInfo` | 否 | 触发信息 |
| `timeExecution` | `ITimeExecution \| null` | 否 | 定时执行配置 |
| `webhookUrl` | `string` | 否 | Webhook 触发地址 |
| `sources` | `Array<ISource>` | 是 | 流水线源列表 |
| `stages` | `Array<IStage>` | 是 | 阶段列表 |

### TypeScript 定义

```typescript
export interface IPipeline {
  pipelineId: string | number | null
  spaceId: number | string | null
  name: string | null
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
  sources: Array<ISource>
  stages: Array<IStage>
}
```

## ISource - 流水线源

流水线源定义了代码仓库或制品的来源信息。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | `string` | 是 | 源唯一标识 |
| `name` | `string` | 是 | 源名称 |
| `nodeType` | `string` | 是 | 节点类型：`custom-source-node` |
| `defaultBranch` | `string` | 否 | 默认分支 |
| `data` | `ISourceData` | 是 | 源详细配置 |

### ISourceData - 源数据详情

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `workPath` | `string` | 是 | 工作目录路径 |
| `repoType` | `string` | 是 | 仓库类型：`GITEE` 等 |
| `refsType` | `string` | 是 | 引用类型：`BRANCH`、`TAG`、`COMMIT` |
| `sourceType` | `string` | 是 | 源类型：`code`、`package`、`pipeline` |
| `repoUrl` | `string` | 是 | 仓库地址 |
| `language` | `string` | 否 | 编程语言 |
| `branch` | `string` | 是 | 分支名称 |
| `commitId` | `string` | 否 | 提交 ID |
| `credentialsId` | `string` | 否 | 凭证 ID |

### TypeScript 定义

```typescript
export interface ISource {
  id: string
  name: string
  nodeType: string
  defaultBranch?: string
  data: {
    workPath: string
    repoType: string
    refsType: string
    sourceType: string      // 'code' | 'package' | 'pipeline'
    repoUrl: string
    language?: string
    branch: string
    commitId: string
    credentialsId: string
  }
}
```

### 默认值

```typescript
const DEFAULT_NEW_SOURCE = {
  id: uuid(),
  name: '',
  nodeType: 'custom-source-node',
  data: {
    repoType: 'GITEE',
    refsType: 'BRANCH',
    sourceType: 'code',
    repoUrl: '',
    branch: 'master',
    commitId: '',
    workPath: '',
    credentialsId: ''
  }
}
```

## IStage - 阶段

阶段是流水线的第一级组织单元，包含多个步骤。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | `string` | 是 | 阶段唯一标识 |
| `name` | `string` | 是 | 阶段名称 |
| `nodeType` | `string` | 是 | 节点类型：`custom-stage-node` |
| `bizType` | `string` | 否 | 业务类型：`STAGE_NODE`、`RIGHT_ADD_STAGE_NODE` |
| `steps` | `Array<IStep>` | 是 | 步骤列表 |

### TypeScript 定义

```typescript
export interface IStage {
  id: string
  name: string
  nodeType: string
  bizType?: string
  steps: Array<IStep>
}
```

### 默认值

```typescript
// 带有"新增任务"按钮的阶段
const DEFAULT_NEW_STAGE = {
  id: uuid(),
  name: '新阶段',
  bizType: 'RIGHT_ADD_STAGE_NODE',
  nodeType: 'custom-stage-node',
  steps: [
    {
      id: uuid(),
      name: '新步骤',
      nodeType: 'custom-step-node',
      idx: 0,
      driven: 1,
      tasks: [
        {
          id: uuid(),
          nodeType: 'custom-add-task-node',
          name: '新增任务',
          idx: 0
        }
      ]
    }
  ]
}

// 空阶段
const DEFAULT_STAGE_DATA = {
  id: uuid(),
  name: '新阶段',
  nodeType: 'custom-stage-node',
  steps: [
    {
      id: uuid(),
      name: '新步骤',
      nodeType: 'custom-step-node',
      idx: 0,
      driven: 0,
      tasks: []
    }
  ]
}
```

## IStep - 步骤

步骤是阶段的二级组织单元，控制任务的执行方式（串行/并行）。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | `string` | 是 | 步骤唯一标识 |
| `name` | `string` | 是 | 步骤名称 |
| `nodeType` | `string` | 是 | 节点类型：`custom-step-node` |
| `driven` | `number` | 是 | 驱动方式：0-串行，1-并行 |
| `idx` | `number` | 是 | 步骤索引 |
| `tasks` | `Array<ITask>` | 是 | 任务列表 |

### TypeScript 定义

```typescript
export interface IStep {
  id: string
  name: string
  nodeType: string
  driven: number       // 0: 串行执行, 1: 并行执行
  idx: number
  tasks: Array<ITask>
}
```

### 默认值

```typescript
const DEFAULT_NEW_STEP = {
  id: uuid(),
  name: '新步骤',
  nodeType: 'custom-step-node',
  idx: 0,
  driven: 0,
  tasks: []
}
```

## ITask - 任务节点

任务是流水线的最小执行单元，对应画布上的任务节点。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | `string` | 是 | 任务唯一标识 |
| `name` | `string` | 是 | 任务名称 |
| `nodeType` | `string` | 是 | 节点类型：`custom-task-node`、`custom-add-task-node` |
| `idx` | `number` | 否 | 任务索引 |
| `data` | `ITaskNodeData` | 否 | 运行时状态数据（执行时填充） |
| `position` | `{x, y}` | 否 | 画布位置（分组流水线用） |
| `width` | `number` | 否 | 节点宽度 |
| `height` | `number` | 否 | 节点高度 |

### TypeScript 定义

```typescript
export interface ITask {
  id: string
  name: string
  nodeType: string
  idx?: number
  data?: ITaskNodeData
  position?: {
    x: number
    y: number
  }
  width?: number
  height?: number
}

export interface ITaskNodeData {
  duration?: string        // 执行时长
  taskStatus?: string      // 任务状态码
  taskStatusName?: string  // 任务状态名称
  endTime?: string         // 结束时间
  startTime?: string       // 开始时间
}
```

### 默认值

```typescript
const DEFAULT_NEW_TASK = {
  id: uuid(),
  nodeType: 'custom-task-node',
  name: '新任务',
  idx: 0
}
```

## ITaskData - 任务配置数据

`taskDataList` 存储每个任务的详细配置信息。

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | `string` | 是 | 任务 ID（对应 ITask.id） |
| `data` | `object` | 是 | 任务详细配置数据 |

### TypeScript 定义

```typescript
export interface ITaskData {
  id: string
  data: string | number | boolean | Array<any> | object
}
```

## 辅助数据结构

### ITriggerInfo - 触发信息

```typescript
export interface ITriggerInfo {
  triggerType: number      // 触发类型
  triggerParams: any       // 触发参数
}
```

### ITimeExecution - 定时执行配置

```typescript
export interface ITimeExecution {
  executeType: string           // 执行类型
  executeWeeks?: Array<any>     // 执行周期（周几）
  executeTime?: string          // 执行时间
  executeCron?: string          // Cron 表达式
}
```

### IFormFlow - 表单配置

```typescript
export interface IFormFlow {
  buildNumber: string
  name: string
  pipelineVer: string
  aliasId: string
  pipelineKey: string
  label: Array<string>
  timeExecutionSwitch?: boolean
  timeExecution?: ITimeExecution | null
  webhookUrl?: string
  buildMachineMode?: string
  buildPlatform?: string
  executeMachineId?: number
}
```

## 状态枚举

### GRAPH_STATUS - 画布状态

| 值 | 说明 |
|------|------|
| `detail` | 详情模式 |
| `editing` | 编辑模式 |
| `onlyView` | 只读模式 |
| `running` | 运行中 |
| `pending` | 等待中 |
| `cancel` | 已取消 |

### PIPELINE_STATUS_MAP / EXECUTION_STATUS_ENUM - 执行状态

| 状态码 | 名称 | 说明 |
|--------|------|------|
| `100000` | 未执行 | NOTEXCUTE |
| `100001` | 等待中 | WAITING |
| `100002` | 执行中 | RUNNING |
| `100003` | 暂停/成功 | PAUSE（旧）/ SUCCESS（新） |
| `100004` | 成功 | SUCCESS |
| `100005` | 失败 | FAILURE |
| `100006` | 已取消 | CANCELLED |
| `100007` | 跳过执行 | SKIP_EXECUTION |

### NODE_BIZ_TYPE - 节点业务类型

| 值 | 说明 |
|------|------|
| `TASK_NODE` | 任务节点 |
| `STAGE_NODE` | 阶段节点 |
| `SOURCE_NODE` | 源节点 |
| `RIGHT_ADD_STAGE_NODE` | 添加阶段按钮节点 |

### TRIGGER_MODE_MAP - 触发方式

| 值 | 说明 |
|------|------|
| `0` | 手动触发 |
| `1` | 代码触发 |
| `3` | 定时触发 |
| `4` | 流水线触发 |
| `5` | Webhook触发 |

## 完整数据示例

```json
{
  "pipeline": {
    "pipelineId": "123456",
    "spaceId": "1",
    "name": "示例流水线",
    "aliasId": "demo-pipeline",
    "store": 0,
    "runTimes": "10",
    "pipelineStatus": "100003",
    "pipelineStatusName": "成功",
    "pipelineStageInfo": "",
    "runRemark": "",
    "triggerMode": "0",
    "triggerModeName": "手动触发",
    "triggerUser": "admin",
    "label": ["前端", "测试"],
    "triggerInfo": {
      "triggerType": 0,
      "triggerParams": {}
    },
    "timeExecution": null,
    "webhookUrl": "",
    "sources": [
      {
        "id": "source-001",
        "name": "前端代码库",
        "nodeType": "custom-source-node",
        "data": {
          "workPath": "frontend-app",
          "repoType": "GITEE",
          "refsType": "BRANCH",
          "sourceType": "code",
          "repoUrl": "https://code.iflytek.com/demo/frontend-app",
          "branch": "master",
          "commitId": "",
          "credentialsId": "cred-001"
        }
      }
    ],
    "stages": [
      {
        "id": "stage-001",
        "name": "构建阶段",
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
                "id": "task-001",
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
      "id": "task-001",
      "data": {
        "taskCategory": "Build",
        "jobType": "MavenBuild",
        "name": "Maven构建",
        "script": "mvn clean package",
        "workPath": "",
        "sourceId": "source-001",
        "jdkVersion": "JDK1.8",
        "mavenVersion": "Maven3.3.9",
        "uploadArtifact": true,
        "artifactPath": ["target/"],
        "artifactSuffix": "jar"
      }
    }
  ]
}
```

## 节点层级关系图

```
流水线 (IFlowData)
│
├── 流水线源 (sources: ISource[])
│   └── 源配置 (data: ISourceData)
│
└── 阶段 (stages: IStage[])
    └── 步骤 (steps: IStep[])
        └── 任务 (tasks: ITask[])
            │
            └── 任务配置 (taskDataList → ITaskData.data)
```

## 相关文件

- 类型定义：`src/utils/graph/type.ts`
- 常量定义：`src/utils/graph/constant.ts`
- Store 管理：`src/store/flow.ts`
- 默认值函数：`src/store/flow.ts` 中的 `getDefault*` 系列函数
