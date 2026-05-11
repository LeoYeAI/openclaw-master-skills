# 质效平台 4.0 流水线文档

本文档为流水线 OpenAPI 接口文档，用于 Skill 训练和外部系统集成。

## 文档目录

### OpenAPI 文档

| 文档 | 说明 |
|------|------|
| [流水线 API](./openapi/01-pipeline-api.md) | 流水线创建、执行、删除 |
| [任务 API](./openapi/03-task-api.md) | 任务节点配置、jobType 列表 |
| [模板 API](./openapi/04-template-api.md) | 模板管理 |
| [字段枚举汇总](./openapi/05-field-enums.md) | 所有枚举字段的可选值 |
| [执行流水线 API](./openapi/06-execute-pipeline-api.md) | 流水线执行、分支/版本选择 |

### JSON Schema

| 文档 | 说明 |
|------|------|
| [pipeline.schema.json](./schemas/pipeline.schema.json) | 流水线数据 Schema |
| [source.schema.json](./schemas/source.schema.json) | 代码源数据 Schema |
| [task-data.schema.json](./schemas/task-data.schema.json) | 任务配置通用 Schema |
| [run-pipeline.schema.json](./schemas/run-pipeline.schema.json) | 执行流水线请求 Schema |
| [all-tasks/](./schemas/all-tasks/) | 各任务类型专用 Schema（36个） |

### 参考文档

| 文档 | 说明 |
|------|------|
| [任务目录](./tasklist/00-task-catalog.md) | 所有任务类型索引 |
| [通用字段](./tasklist/03-common-fields.md) | 所有任务通用字段说明 |
| [校验规则](./tasklist/03-validate-rules.md) | 字段校验规则说明 |
| [数据结构](./01-pipeline-data-structure.md) | 完整数据结构定义 |

## 快速查找

| 场景 | 推荐文档 |
|------|---------|
| 创建流水线 | [流水线 API](./openapi/01-pipeline-api.md) |
| 添加任务 | [任务 API](./openapi/03-task-api.md) |
| 执行流水线 | [执行流水线 API](./openapi/06-execute-pipeline-api.md) |
| 查枚举值 | [字段枚举汇总](./openapi/05-field-enums.md) |
| 数据验证 | [schemas/](./schemas/) |

## 核心概念

| 概念 | 说明 |
|-----|------|
| `jobType` | 任务类型标识（如 `MavenBuild`, `DockerBuildAndUpload`） |
| `taskCategory` | 任务分类（`Build`, `DockerBuild`, `Deploy`, `CodeScanner`, `CodeCover`, `Code`, `Normal`） |
| `workPath` | 工作目录（代码源根目录） |
| `sourceId` | 代码源 ID |
| `runSources` | 执行时的源配置列表 |

## 动态参数

| 参数 | 说明 |
|-----|------|
| `${PIPELINE_NAME}` | 流水线名称 |
| `${BUILD_NUMBER}` | 构建号 |
| `${PIPELINE_LOG_ID}` | 流水线执行日志 ID |
| `${BRANCH}` | 当前分支 |
| `${COMMIT_ID}` | 提交 ID |
