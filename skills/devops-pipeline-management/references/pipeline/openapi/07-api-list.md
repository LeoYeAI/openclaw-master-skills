# API 端点清单

本文档汇总 `docs/pipeline` 目录中所有使用的 API 端点（完整路径）。

**Base URL**: `/rest/openapi`

---

## API 统计

| 分类 | 数量 |
|-----|------|
| 流水线管理 | 6 |
| 代码源管理 | 2 |
| Stage 管理 | 1 |
| 任务管理 | 3 |
| 模板管理 | 6 |
| 辅助查询 | 6 |
| **总计** | **24** |

---

## 完整 API 列表

### 流水线管理

| Method | 完整路径 | 说明 |
|--------|----------|------|
| POST | `/rest/openapi/pipeline/save` | 创建/更新流水线 |
| GET | `/rest/openapi/pipeline/detail` | 获取流水线详情 |
| DELETE | `/rest/openapi/pipeline/delete` | 删除流水线 |
| POST | `/rest/openapi/pipeline/list` | 获取流水线列表 |
| POST | `/rest/openapi/pipeline/runByManual` | 执行流水线（手动触发） |

### 模板管理

| Method | 完整路径 | 说明 |
|--------|----------|------|
| POST | `/rest/openapi/pipeline/template/savePipTemplate` | 保存模板 |
| GET | `/rest/openapi/pipeline/template/getPipTemplateById` | 获取模板详情 |
| POST | `/rest/openapi/pipeline/template/queryNormalPipTemplatePage` | 查询模板列表 |
| DELETE | `/rest/openapi/pipeline/template/delPipTemplate` | 删除模板 |
| POST | `/rest/openapi/pipeline/template/copyPipTemplate` | 复制模板 |
| POST | `/rest/openapi/pipeline/template/updatePipTemplateStatus` | 更新模板状态 |

### 数据校验

| Method | 完整路径 | 说明 |
|--------|----------|------|
| POST | `/devops/api/pipeline/validatePipelineTaskData` | 校验任务数据合法性 |

### 辅助查询（执行流水线）

| Method | 完整路径 | 说明 |
|--------|----------|------|
| POST | `/rest/openapi/pipeline/queryLastestSelectedValueByField` | 获取最近执行的分支/版本 |
| POST | `/rest/openapi/pipeline/getRepoBranchAndTagList` | 获取分支/标签列表 |
| POST | `/rest/openapi/pipeline/queryCommitDetail` | 获取提交详情（标签） |
| POST | `/rest/openapi/pipeline/queryRepoCommitList` | 获取提交列表（分支） |
| GET | `/rest/openapi/pipeline/imageTags` | 获取镜像标签列表 |
| GET | `/rest/openapi/pipeline/packageVersions` | 获取普通制品版本列表 |

---

## 按 Skill 场景分类

### 场景1: 创建流水线

```
POST /rest/openapi/pipeline/save
POST /rest/openapi/pipeline/source/save
POST /rest/openapi/pipeline/stage/save
GET  /rest/openapi/pipeline/task/createTaskId
POST /rest/openapi/pipeline/task/save
```

### 场景2: 执行流水线

```
GET  /rest/openapi/pipeline/detail
POST /rest/openapi/pipeline/queryLastestSelectedValueByField
POST /rest/openapi/pipeline/getRepoBranchAndTagList
POST /rest/openapi/pipeline/runByManual
```

### 场景3: 管理模板

```
POST   /rest/openapi/pipeline/template/savePipTemplate
GET    /rest/openapi/pipeline/template/getPipTemplateById
POST   /rest/openapi/pipeline/template/queryNormalPipTemplatePage
POST   /rest/openapi/pipeline/template/copyPipTemplate
DELETE /rest/openapi/pipeline/template/delPipTemplate
```

### 场景4: 查询信息

```
GET  /rest/openapi/pipeline/detail
POST /rest/openapi/pipeline/list
POST /rest/openapi/pipeline/getRepoBranchAndTagList
GET  /rest/openapi/pipeline/imageTags
GET  /rest/openapi/pipeline/packageVersions
```

---

## 请求示例

### 创建流水线

```bash
curl -X POST /rest/openapi/pipeline/save \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"name": "my-pipeline", "spaceId": "space-001"}'
```

### 获取流水线详情

```bash
curl -X GET "/rest/openapi/pipeline/detail?pipelineId=pipe-001" \
  -H "Authorization: Bearer {token}"
```

### 执行流水线

```bash
curl -X POST /rest/openapi/pipeline/runByManual \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"pipelineId": "pipe-001"}'
```
