# 通用字段说明

本文档描述了所有流水线任务原子能力的通用字段配置。

## 通用字段列表

### 基础信息字段

| 字段名 | 类型 | 默认值 | 说明 | 必填 | 备注 |
|-------|------|-------|------|------|------|
| `name` | string | - | 任务名称 | **是** | 最大长度100字符 |
| `identifier` | string | `''` | 任务标识 | 否 | 仅系统模板可用，用于API调用场景 |
| `jobType` | string | - | 任务类型标识 | **是** | 如 `OrderAction`, `MavenBuild` 等 |
| `taskCategory` | string | - | 任务分类 | **是** | 枚举: `Build`, `Deploy`, `CodeScanner`, `Normal` |
| `idInTemplate` | string | `''` | 模板中任务ID | 否 | 模板任务使用 |

### 构建环境字段

| 字段名 | 类型 | 默认值 | 说明 | 必填 | 备注 |
|-------|------|-------|------|------|------|
| `buildImageModel` | string | `'default'` | 构建环境类型 | **是** | `default`: 默认环境<br>`custom`: 自定义镜像 |
| `executeImageId` | string | `''` | 执行镜像ID | 条件必填 | 当 `buildImageModel` 为 `custom` 时必填 |

### 工作目录字段

| 字段名 | 类型 | 默认值 | 说明 | 必填 | 备注 |
|-------|------|-------|------|------|------|
| `workPath` | string | `''` | 工作目录 | 条件必填 | 非模板模式下必填，选择代码源 |
| `sourceId` | string | `''` | 代码源ID | 否 | 对应流水线源的ID |

### 依赖关系字段

| 字段名 | 类型 | 默认值 | 说明 | 必填 | 备注 |
|-------|------|-------|------|------|------|
| `dependencies` | array | `[]` | 前序任务依赖列表 | 否 | 数组元素包含: `taskId`, `valueTemplate`, `taskFeildPath`, `depType`, `priority` |

### 依赖关系结构

```typescript
interface Dependency {
  id?: string;              // 依赖ID
  taskId: string;           // 前序任务ID
  jobType?: string;         // 前序任务类型
  valueTemplate: string;   // 值模板，如 `${id}`
  taskFeildPath: string;    // 依赖字段路径
  parentPath?: string;      // 父路径
  depType: string;          // 依赖类型
  priority: boolean;        // 是否优先依赖
}
```

### 依赖类型 (depType)

| 值 | 说明 |
|---|------|
| `SELF` | 自身依赖 |
| `PACKAGE` | 制品依赖 |
| `OTHER` | 其他依赖 |

---

## 各任务类型通用配置示例

### 执行命令任务 (OrderAction)

```json
{
  "name": "执行命令",
  "taskCategory": "Normal",
  "jobType": "OrderAction",
  "buildImageModel": "default",
  "executeImageId": "",
  "script": "echo hello,world!",
  "workPath": "",
  "sourceId": "",
  "idInTemplate": "",
  "dependencies": [],
  "identifier": ""
}
```

### Maven构建任务 (MavenBuild)

```json
{
  "name": "Maven构建",
  "taskCategory": "Build",
  "jobType": "MavenBuild",
  "buildImageModel": "default",
  "executeImageId": "",
  "workPath": "",
  "sourceId": "",
  "jdkVersion": "JDK1.8",
  "mavenVersion": "Maven3.3.9",
  "selectedMavenRepos": [],
  "script": "mvn -B clean package -Dmaven.test.skip=true",
  "uploadArtifact": true,
  "artifactPath": ["target/"],
  "artifactSuffix": ["jar"],
  "artifactCompress": true,
  "compressType": "TAR(.tgz)",
  "packagedName": "Artifacts_${PIPELINE_LOG_ID}",
  "idInTemplate": "",
  "dependencies": []
}
```

---

## 构建环境配置 (BuildEnvironment)

构建环境是所有任务类型的通用配置组件。

### 配置项

| 字段名 | 类型 | 默认值 | 说明 | 必填 |
|-------|------|-------|------|------|
| `buildImageModel` | string | `'default'` | 构建环境类型 | **是** |
| `executeImageId` | string | `''` | 镜像ID | 条件 |

### 构建环境类型选项

| 值 | 说明 |
|---|------|
| `default` | 默认构建环境（平台提供） |
| `custom` | 自定义镜像（用户自行配置） |

### 默认构建环境

选择 `default` 时，无需选择具体镜像，平台会提供默认的执行环境。

### 自定义镜像

选择 `custom` 时，需要从下拉列表中选择一个已配置的自定义镜像。选择后，任务将使用该镜像执行。

---

## 工作目录配置

工作目录用于指定代码源文件下载后的根目录。

### 配置说明

- **非模板模式**: 必须选择工作目录，从已配置的代码源中选择
- **模板模式**: 无需配置工作目录，任务可在任意流水线中使用

### 工作目录选择

从流水线配置的代码源中选择，支持筛选 `sourceType === 'code'` 的源。

---

## 前序任务依赖配置

用于配置当前任务与前序任务之间的依赖关系，实现任务间的数据传递。

### 使用场景

1. **制品传递**: 当前任务需要使用前序任务生成的制品
2. **镜像引用**: 部署任务需要引用构建任务生成的镜像
3. **变量传递**: 任务间需要传递环境变量或配置

### 配置方式

通过 `YamlParamsSetting` 组件添加变量，支持:
- 前序任务制品地址
- 前序任务镜像地址
- 自定义参数
