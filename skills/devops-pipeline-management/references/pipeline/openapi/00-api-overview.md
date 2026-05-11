# OpenAPI 总览

本文档为流水线 OpenAPI 的总览，用于 Skill 训练和外部系统集成。

## 基础信息

| 属性 | 值 |
|-----|-----|
| Base URL | `/rest/openapi/pipeline` |
| 认证方式 | Bearer Token (Header: `Authorization: Bearer {token}`) |
| Content-Type | `application/json` |

## API 端点总览

### 流水线管理

| 端点 | Method | 说明 |
|-----|--------|------|
| `/pipeline/save` | POST | 创建/更新流水线 |
| `/pipeline/detail` | GET | 获取流水线详情 |
| `/pipeline/delete` | DELETE | 删除流水线 |
| `/pipeline/list` | POST | 获取流水线列表 |
| `/pipeline/runByManual` | POST | 执行流水线（手动触发） |
| `/pipeline/queryLastestSelectedValueByField` | POST | 获取最近执行的分支/版本 |
| `/pipeline/getRepoBranchAndTagList` | POST | 获取分支/标签列表 |

### 代码源管理

| 端点 | Method | 说明 |
|-----|--------|------|
| `/pipeline/source/save` | POST | 添加/更新代码源 |
| `/pipeline/source/delete` | DELETE | 删除代码源 |

### 任务管理

| 端点 | Method | 说明 |
|-----|--------|------|
| `/pipeline/task/save` | POST | 添加/更新任务 |
| `/pipeline/task/delete` | DELETE | 删除任务 |
| `/pipeline/task/createTaskId` | GET | 生成任务ID |

### 流水线模板

| 端点 | Method | 说明 |
|-----|--------|------|
| `/pipeline/template/savePipTemplate` | POST | 保存模板 |
| `/pipeline/template/getPipTemplateById` | GET | 获取模板详情 |
| `/pipeline/template/queryNormalPipTemplatePage` | POST | 查询模板列表 |
| `/pipeline/template/delPipTemplate` | DELETE | 删除模板 |

---

## 通用响应格式

### 成功响应

```json
{
  "code": "200",
  "message": "success",
  "data": { ... }
}
```

### 错误响应

```json
{
  "code": "400",
  "message": "错误描述",
  "data": null
}
```

## 通用错误码

| 错误码 | 说明 |
|-------|------|
| `200` | 成功 |
| `400` | 请求参数错误 |
| `401` | 未授权/Token失效 |
| `403` | 无权限 |
| `404` | 资源不存在 |
| `500` | 服务器内部错误 |

---

## 核心操作流程

### 创建完整流水线的步骤

```
1. 创建流水线 → 获取 pipelineId
       ↓
2. 添加代码源 → 获取 sourceId
       ↓
3. 创建 Stage → 获取 stageId
       ↓
4. 添加任务 → 关联 sourceId, stageId
       ↓
5. 执行流水线
```

### 详细流程见

- [流水线 API](./01-pipeline-api.md) - 流水线创建、执行
- [代码源 API](./02-source-api.md) - 代码源配置
- [任务 API](./03-task-api.md) - 任务节点配置
- [模板 API](./04-template-api.md) - 模板管理
- [执行流水线 API](./06-execute-pipeline-api.md) - 流水线执行、分支/版本选择

---

## 快速开始示例

### 最小化创建流水线

```bash
# 1. 创建流水线
curl -X POST /rest/openapi/pipeline/save \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-pipeline",
    "spaceId": "space-001"
  }'

# 响应: { "code": "200", "data": { "pipelineId": "pipe-001" } }
```

### 完整示例

参见 [../examples/create-full-pipeline.md](../examples/create-full-pipeline.md)
