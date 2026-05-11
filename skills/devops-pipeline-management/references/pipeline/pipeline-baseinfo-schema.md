# 流水线基础信息数据结构文档

> 本文档定义了流水线基础信息的完整数据结构、校验规则和字段联动逻辑
> 适用于：创建流水线、编辑流水线、创建流水线模板

---

## 一、核心数据模型

### 1.1 基础信息 (PipelineBaseInfo)

```typescript
interface PipelineBaseInfo {
  // === 基础信息 ===
  name: string;                    // 流水线名称
  aliasId: string;                 // 别名 ID（16位随机字符串）
  pipelineKey: string;             // 流水线 Key
  buildNumber: string;             // 执行序号
  pipelineVer?: string;            // 版本（可选）
  label: ILabel[];                 // 标签列表
  timeoutDuration: string;         // 超时时间
  buildMachineMode: string;        // 构建执行机模式
  executeMachineId?: number;       // 执行机 ID（自定义模式时必填）
  buildPlatform: string;           // 构建环境类型

  // === 触发设置 ===
  timeExecution?: ITimeExecution | null;  // 定时执行配置
  webhookUrl?: string;                    // Webhook 链接

  // === 参数设置 ===
  customParameters: ICustomParameter[];   // 自定义参数列表

  // === 并发策略 ===
  concurrencySwitch?: boolean;     // 并发开关
  concurrencyNum?: number;         // 并发数
  concurrencyStrategy?: string;    // 并发策略
}
```

### 1.2 完整字段定义表

| 字段路径 | 类型 | 必填 | 默认值 | 说明 | 校验规则 |
|----------|------|------|--------|------|----------|
| `name` | string | ✅ | - | 流水线名称 | 不能为空、不能有空格、不能重复、最大200字符 |
| `aliasId` | string | ✅ | 自动生成 | 别名ID | 16位随机字符串，格式：`[a-z0-9]{16}` |
| `pipelineKey` | string | ✅ | 从name生成 | 流水线Key | 字母数字下划线连字符、最大30字符、编辑时不可改 |
| `buildNumber` | string | ✅ | `"1"` | 执行序号 | ≥1的整数、最大15字符 |
| `pipelineVer` | string | ❌ | `""` | 版本 | 最大20字符、仅数字字母横线下划线和点 |
| `label` | ILabel[] | ❌ | `[]` | 标签列表 | 最多5个标签 |
| `timeoutDuration` | string | ✅ | `"12H"` | 超时时间 | 枚举：`1H`~`12H`, `24H` |
| `buildMachineMode` | string | ✅ | `"default"` | 执行机模式 | 枚举：`default`/`custom` |
| `executeMachineId` | number | 条件 | - | 执行机ID | `buildMachineMode=custom`时必填 |
| `buildPlatform` | string | ✅ | `"linux"` | 构建环境 | 枚举：`linux`/`windows` |
| `timeExecution` | object | ❌ | `null` | 定时配置 | 开关开启时必填 |
| `webhookUrl` | string | ❌ | `""` | Webhook | 开关开启时系统自动生成 |
| `customParameters` | array | ❌ | `[]` | 自定义参数 | 参数名称不可重复 |
| `concurrencySwitch` | boolean | ❌ | `false` | 并发开关 | - |
| `concurrencyNum` | number | 条件 | `5` | 并发数 | 开关开启时必填，范围1-10 |
| `concurrencyStrategy` | string | 条件 | `"wait"` | 并发策略 | 开关开启时必填：`wait`/`reject` |

---

## 二、子数据结构

### 2.1 标签 (ILabel)

```typescript
interface ILabel {
  id: string;        // 标签唯一标识，示例："label_001"
  labelName: string; // 标签名称，示例："前端项目"
  color: string;     // 标签颜色：primary(蓝) | success(绿) | danger(红)
}
```

**标签颜色枚举：**

| 颜色值 | 色值 | 用途建议 |
|--------|------|----------|
| `primary` | #436ff6 | 通用/默认 |
| `success` | #57bc66 | 生产环境/重要 |
| `danger` | #ed4543 | 紧急/高风险 |

### 2.2 定时执行配置 (ITimeExecution)

```typescript
interface ITimeExecution {
  executeType: string;      // 定时周期：day/week/custom
  executeWeeks?: string[];  // 执行日，executeType=week时必填
  executeTime?: string;     // 执行时间，executeType!=custom时必填，格式：HH:mm:ss
  executeCron?: string;     // Cron表达式，executeType=custom时必填
}
```

**executeWeeks 枚举值：**

| 显示值 | 存储值 |
|--------|--------|
| 周一 | Monday |
| 周二 | Tuesday |
| 周三 | Wednesday |
| 周四 | Thursday |
| 周五 | Friday |
| 周六 | Saturday |
| 周日 | Sunday |

### 2.3 自定义参数 (ICustomParameter)

```typescript
interface ICustomParameter {
  name: string;           // 参数名称
  type: string;           // 类型：string/auto/enum
  defaultValue: string;   // 默认值
  enumValue?: string[];   // 枚举值列表，type=enum时必填
  privateKey: boolean;    // 是否私密参数
  runSet: boolean;        // 是否执行时设置
  description?: string;   // 描述
  pipelineId?: string;    // 流水线ID（编辑时填充）
  customParameterId?: string; // 参数ID（编辑时存在）
}
```

**参数类型定义：**

| 类型值 | 显示名 | 默认值校验 | 特殊限制 |
|--------|--------|------------|----------|
| `string` | 字符串 | 非空，支持中文、字母、数字及`- _ , / . $ { } [ ] : ; < > = ? \| ^ @ +` | 可设为私密参数 |
| `auto` | 自增长 | 非空，≥0的整数 | 不可设为私密参数 |
| `enum` | 枚举 | 必须从枚举值中选择 | 不可设为私密参数 |

---

## 三、字段联动规则

### 3.1 流水线Key自动生成

```
输入：流水线名称
处理：
  1. 中文字符 → 取拼音首字母小写
  2. 英文字符 → 转小写
  3. 数字 → 保留
  4. 其他字符 → 忽略
  5. 结果截取前30字符
输出：pipelineKey

示例：
  "前端构建流水线" → "qdgl"
  "Java后端服务" → "javahdfw"
  "Test_Project-123" → "test_project-123"
```

### 3.2 执行机模式联动

```
buildMachineMode 变化时：

if (buildMachineMode === "default") {
  buildPlatform = "linux";           // 固定为linux
  executeMachineId = undefined;      // 清空执行机选择
} else if (buildMachineMode === "custom") {
  buildPlatform = "";                // 等待选择执行机后自动填充
  // 用户选择 executeMachineId 后：
  buildPlatform = selectedMachine.machineType;
}
```

### 3.3 参数类型联动

```
type 变化时：

if (type === "enum" || type === "auto") {
  privateKey = false;                // 强制设为false
  privateKey.disabled = true;        // 禁用私密参数开关
}

privateKey 变化时：

if (privateKey === true) {
  runSet = false;                    // 私密参数不支持执行时设置
}
```

### 3.4 触发设置联动

```
timeExecutionSwitch 开启时：
  - executeType 必填（默认day）
  - 根据 executeType 决定其他必填字段

timeExecutionSwitch 关闭时：
  - timeExecution = null

webhookSwitch 开启时：
  - 系统自动生成 webhookUrl（不可手动输入）

webhookSwitch 关闭时：
  - webhookUrl = ""
```

---

## 四、校验规则汇总

### 4.1 正则表达式速查表

| 字段 | 正则表达式 | 说明 |
|------|------------|------|
| name | `^[^\s]*$` | 不能包含空格 |
| pipelineKey | `^[a-zA-Z0-9_-]+$` | 仅字母数字下划线连字符 |
| buildNumber | `^[1-9]\d*$` | 大于等于1的整数 |
| pipelineVer | `^[0-9a-zA-Z_\-\.]*$` | 数字字母横线下划线点 |
| parameter.name | `^[A-Za-z][A-Za-z0-9_-]*$` | 字母开头，支持字母数字下划线连字符 |
| auto默认值 | `^(0\|[1-9]\d*)$` | 大于等于0的整数 |

### 4.2 长度限制表

| 字段 | 最大长度 | 说明 |
|------|----------|------|
| name | 200 | 流水线名称 |
| pipelineKey | 30 | 流水线Key |
| buildNumber | 15 | 执行序号 |
| pipelineVer | 20 | 版本号 |
| label.labelName | 20 | 标签名称 |
| parameter.name | 100 | 参数名称 |
| parameter.defaultValue | 30000 | 默认值 |
| parameter.description | 500 | 参数描述 |

### 4.3 条件必填矩阵

| 字段 | 条件 | 必填 |
|------|------|------|
| executeMachineId | buildMachineMode === "custom" | ✅ |
| timeExecution | timeExecutionSwitch === true | ✅ |
| timeExecution.executeWeeks | executeType === "week" | ✅ |
| timeExecution.executeTime | executeType !== "custom" | ✅ |
| timeExecution.executeCron | executeType === "custom" | ✅ |
| webhookUrl | webhookSwitch === true | ✅ |
| concurrencyNum | concurrencySwitch === true | ✅ |
| concurrencyStrategy | concurrencySwitch === true | ✅ |
| enumValue | type === "enum" | ✅ |

---

## 五、完整JSON示例

### 5.1 最小化创建示例

```json
{
  "name": "前端构建流水线",
  "aliasId": "a1b2c3d4e5f6g7h8",
  "pipelineKey": "qdgl",
  "buildNumber": "1",
  "timeoutDuration": "12H",
  "buildMachineMode": "default",
  "buildPlatform": "linux",
  "label": [],
  "customParameters": []
}
```

### 5.2 完整配置示例

```json
{
  "name": "Java微服务构建部署",
  "aliasId": "x9y8z7w6v5u4t3s2",
  "pipelineKey": "javawfwgjbs",
  "buildNumber": "1",
  "pipelineVer": "v2.1.0",
  "timeoutDuration": "24H",
  "buildMachineMode": "custom",
  "executeMachineId": 10086,
  "buildPlatform": "linux",
  "label": [
    { "id": "label_001", "labelName": "Java", "color": "primary" },
    { "id": "label_002", "labelName": "生产环境", "color": "danger" }
  ],
  "timeExecution": {
    "executeType": "week",
    "executeWeeks": ["Monday", "Wednesday", "Friday"],
    "executeTime": "02:00:00"
  },
  "webhookUrl": "",
  "customParameters": [
    {
      "name": "MAVEN_PROFILE",
      "type": "enum",
      "defaultValue": "prod",
      "enumValue": ["dev", "test", "prod"],
      "privateKey": false,
      "runSet": true,
      "description": "Maven构建环境"
    },
    {
      "name": "BUILD_SEQ",
      "type": "auto",
      "defaultValue": "1000",
      "privateKey": false,
      "runSet": false,
      "description": "构建序号"
    },
    {
      "name": "NPM_REGISTRY",
      "type": "string",
      "defaultValue": "https://registry.npmmirror.com",
      "privateKey": false,
      "runSet": true,
      "description": "NPM镜像源"
    }
  ],
  "concurrencySwitch": true,
  "concurrencyNum": 3,
  "concurrencyStrategy": "wait"
}
```

### 5.3 编辑模式示例（注意只读字段）

```json
{
  "name": "已存在的流水线",
  "aliasId": "existing_alias_id",
  "pipelineKey": "existing_key",  // 只读，不可修改
  "buildNumber": "42",
  "timeoutDuration": "12H",
  "buildMachineMode": "default",
  "buildPlatform": "linux",
  "label": [],
  "customParameters": [
    {
      "name": "EXISTING_PARAM",
      "type": "string",
      "defaultValue": "value",
      "privateKey": false,
      "runSet": false,
      "pipelineId": "pipe_12345",
      "customParameterId": "param_67890"
    }
  ]
}
```

---

## 六、枚举值常量表

### 6.1 超时时间选项

```javascript
const timeoutOptions = [
  { label: "1小时", value: "1H" },
  { label: "2小时", value: "2H" },
  { label: "3小时", value: "3H" },
  { label: "4小时", value: "4H" },
  { label: "5小时", value: "5H" },
  { label: "6小时", value: "6H" },
  { label: "7小时", value: "7H" },
  { label: "8小时", value: "8H" },
  { label: "9小时", value: "9H" },
  { label: "10小时", value: "10H" },
  { label: "11小时", value: "11H" },
  { label: "12小时", value: "12H" },
  { label: "24小时", value: "24H" }
];
```

### 6.2 构建环境类型选项

```javascript
const buildEnvironmentTypeOptions = [
  { label: "Linux", value: "linux" },
  { label: "Windows", value: "windows" }
];
```

### 6.3 执行机模式选项

```javascript
const buildMachineModeOptions = [
  { label: "默认执行机", value: "default", description: "平台提供的执行机器" },
  { label: "自定义执行机", value: "custom", description: "空间级自有执行机" }
];
```

### 6.4 定时周期选项

```javascript
const executeTypeOptions = [
  { label: "每日定时执行", value: "day" },
  { label: "每周定时执行", value: "week" },
  { label: "自定义", value: "custom" }
];
```

### 6.5 并发策略选项

```javascript
const concurrencyStrategyOptions = [
  { label: "排队等待", value: "wait" },
  { label: "不允许触发新的执行", value: "reject" }
];
```

### 6.6 参数类型选项

```javascript
const parameterTypeOptions = [
  { label: "字符串", value: "string" },
  { label: "自增长", value: "auto" },
  { label: "枚举", value: "enum" }
];
```

---

## 七、OpenAPI Schema 片段

```yaml
components:
  schemas:
    PipelineBaseInfo:
      type: object
      required:
        - name
        - aliasId
        - pipelineKey
        - buildNumber
        - timeoutDuration
        - buildMachineMode
        - buildPlatform
      properties:
        name:
          type: string
          maxLength: 200
          pattern: "^[^\\s]*$"
          description: 流水线名称，不能包含空格
        aliasId:
          type: string
          pattern: "^[a-z0-9]{16}$"
          description: 16位随机字符串
        pipelineKey:
          type: string
          maxLength: 30
          pattern: "^[a-zA-Z0-9_-]+$"
          description: 流水线Key，编辑时不可修改
        buildNumber:
          type: string
          maxLength: 15
          pattern: "^[1-9]\\d*$"
          description: 执行序号，必须≥1的整数
        pipelineVer:
          type: string
          maxLength: 20
          pattern: "^[0-9a-zA-Z_\\-\\.]*$"
        timeoutDuration:
          type: string
          enum: ["1H","2H","3H","4H","5H","6H","7H","8H","9H","10H","11H","12H","24H"]
        buildMachineMode:
          type: string
          enum: ["default", "custom"]
        executeMachineId:
          type: number
        buildPlatform:
          type: string
          enum: ["linux", "windows"]
        label:
          type: array
          maxItems: 5
          items:
            $ref: "#/components/schemas/Label"
        timeExecution:
          $ref: "#/components/schemas/TimeExecution"
        webhookUrl:
          type: string
        customParameters:
          type: array
          items:
            $ref: "#/components/schemas/CustomParameter"
        concurrencySwitch:
          type: boolean
        concurrencyNum:
          type: number
          minimum: 1
          maximum: 10
        concurrencyStrategy:
          type: string
          enum: ["wait", "reject"]

    Label:
      type: object
      properties:
        id:
          type: string
        labelName:
          type: string
          maxLength: 20
        color:
          type: string
          enum: ["primary", "success", "danger"]

    TimeExecution:
      type: object
      required:
        - executeType
      properties:
        executeType:
          type: string
          enum: ["day", "week", "custom"]
        executeWeeks:
          type: array
          items:
            type: string
            enum: ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        executeTime:
          type: string
          pattern: "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$"
        executeCron:
          type: string

    CustomParameter:
      type: object
      required:
        - name
        - type
        - defaultValue
        - privateKey
        - runSet
      properties:
        name:
          type: string
          maxLength: 100
          pattern: "^[A-Za-z][A-Za-z0-9_-]*$"
        type:
          type: string
          enum: ["string", "auto", "enum"]
        defaultValue:
          type: string
          maxLength: 30000
        enumValue:
          type: array
          items:
            type: string
        privateKey:
          type: boolean
        runSet:
          type: boolean
        description:
          type: string
          maxLength: 500
```

---

*文档版本: 2.0*
*更新日期: 2026-03-13*
