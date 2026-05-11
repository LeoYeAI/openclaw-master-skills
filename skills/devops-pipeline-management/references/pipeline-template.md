---
name: pipeline-template
description: 分页查询流水线模板列表。当用户需要查看可用模板、搜索模板、创建流水线时选择模板使用此功能。

触发关键词："流水线模板"、"模板列表"、"查询模板"、"templates"
---

# 流水线模板列表查询

> ⚠️ **大模型执行约束（必须严格遵守）**
>
> **执行铁律**：
> 1. **API调用规范**：任何发生 API 调用的，**必须实际调用 Python 脚本的 API 功能**，禁止模拟或跳过

## 功能描述

分页查询工作空间下的流水线模板列表，支持按名称、类型筛选。模板是预定义的流水线配置，可用于快速创建新的流水线。

## 使用方式

```bash
python -m scripts/main templates <space_id> [options]
```

## API接口

- **路径**: POST /rest/openapi/pipeline/queryPipelineTemplatePage
- **方法**: POST

## 请求参数

### Body 参数 (JSON)

| 字段名 | 类型 | 必填 | 描述 | 示例值 |
|--------|------|------|------|--------|
| spaceId | Long | ✅ | 工作空间ID | `1001` |
| pipelineTemplateName | String | 否 | 模板名称（模糊搜索） | `Java` |
| pipelineTemplateType | String | 否 | 模板类型 | `1` |
| pipelineTemplateLanguage | String | 否 | 模板语言（java/python/nodejs/go/dotnet/frontend/common） | `java` |
| account | String | 否 | 当前登录账号 | `zhangsan` |
| pageNo | Integer | 否 | 页码（默认1） | `1` |
| pageSize | Integer | 否 | 每页大小（默认10） | `10` |

### 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| space_id | 工作空间ID（必填） | `133` |
| --name | 模板名称（模糊搜索） | `--name Java` |
| --type | 模板类型 | `--type 1` |
| --language | 模板语言（java/python/nodejs/go/dotnet/frontend/common） | `--language java` |
| --account | 当前登录账号 | `--account zhangsan` |
| --page | 页码 | `--page 1` |
| --size | 每页大小 | `--size 20` |

## 请求示例

**命令行 - 基础查询**:
```bash
python -m scripts/main templates 133
```

**命令行 - 按名称搜索**:
```bash
python -m scripts/main templates 133 --name Java
```

**命令行 - 按类型筛选**:
```bash
python -m scripts/main templates 133 --type 1
```

**命令行 - 分页查询**:
```bash
python -m scripts/main templates 133 --page 1 --size 20
```

**API请求体示例**:
```json
{
  "spaceId": 1001,
  "pipelineTemplateName": "Java",
  "pipelineTemplateType": null,
  "pageNo": 1,
  "pageSize": 10
}
```

## 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 25,
    "size": 10,
    "current": 1,
    "pages": 3,
    "records": [
      {
        "id": "tpl-abc123",
        "pipelineTemplateName": "Java微服务模板",
        "pipelineTemplateLanguage": "java",
        "pipelineTemplateParams": "{\"stages\":[{\"name\":\"构建\",\"tasks\":[]}]}",
        "pipelineTemplateType": 1,
        "status": 1,
        "statusName": "启用",
        "spaceId": 1001,
        "description": "Java微服务流水线模板，包含构建、测试、部署阶段",
        "createTime": "2025-01-15T10:00:00",
        "updateTime": "2025-01-15T10:00:00",
        "creator": "zhangsan",
        "creatorName": "张三"
      },
      {
        "id": "tpl-def456",
        "pipelineTemplateName": "Java Maven构建模板",
        "pipelineTemplateLanguage": "java",
        "pipelineTemplateParams": "{\"stages\":[{\"name\":\"Maven构建\",\"tasks\":[]}]}",
        "pipelineTemplateType": 1,
        "status": 1,
        "statusName": "启用",
        "spaceId": 1001,
        "description": "标准Maven项目构建模板",
        "createTime": "2025-01-14T09:00:00",
        "updateTime": "2025-01-14T09:00:00",
        "creator": "lisi",
        "creatorName": "李四"
      }
    ]
  },
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Page<PipTemplateVO> 字段说明

| 字段名 | 类型 | 描述 |
|--------|------|------|
| total | Long | 总记录数 |
| size | Long | 每页大小 |
| current | Long | 当前页码 |
| pages | Long | 总页数 |
| records | List | 流水线模板列表（PipTemplateVO） |

## PipTemplateVO 字段说明

| 字段名 | 类型 | 描述 | 示例值 |
|--------|------|------|--------|
| id | String | 模板ID | `tpl-abc123` |
| pipelineTemplateName | String | 模板名称 | `Java微服务模板` |
| pipelineTemplateLanguage | String | 模板语言 | `java` |
| pipelineTemplateParams | String | 模板参数配置（JSON字符串） | `{"stages":[]}` |
| pipelineTemplateType | Integer | 模板类型 | `1` |
| status | Integer | 状态（1-启用/0-禁用） | `1` |
| statusName | String | 状态名称 | `启用` |
| spaceId | Long | 空间ID | `1001` |
| description | String | 模板描述 | `Java微服务流水线模板` |
| createTime | LocalDateTime | 创建时间 | `2025-01-15T10:00:00` |
| updateTime | LocalDateTime | 更新时间 | `2025-01-15T10:00:00` |
| pipelineStageInfo | String | 流水线阶段信息（JSON字符串） | `{"stages":[]}` |
| creator | String | 创建人（域账号） | `zhangsan` |
| updater | String | 更新人（域账号） | `lisi` |
| deleted | Byte | 删除标志 | `0` |
| creatorName | String | 创建人（中文姓名） | `张三` |
| updaterName | String | 更新人（中文姓名） | `李四` |
| stages | List&lt;Stage&gt; | 阶段列表 | 详见 Stage 结构 |
| pipelineTemplatePermission | List&lt;String&gt; | 模板操作权限列表 | `["edit", "delete"]` |

## 模板语言类型

| 语言 | 标识 |
|------|------|
| Java | `java` |
| Python | `python` |
| Node.js | `nodejs` |
| Go | `go` |
| .NET | `dotnet` |
| 前端 | `frontend` |
| 通用 | `common` |

## 错误码

| 错误码 | 说明 |
|-------|------|
| 0 | 成功 |
| -1 | 通用失败（具体信息见message） |
| 401 | 无API访问权限 |
| 429 | 请求过于频繁（触发限流） |

## 典型使用场景

### 1. 查看可用模板列表

```bash
# 查询工作空间下的所有模板
python -m scripts/main templates 133
```

### 2. 按技术栈搜索模板

```bash
# 搜索Java相关模板
python -m scripts/main templates 133 --name Java

# 搜索Python相关模板
python -m scripts/main templates 133 --name Python
```

### 3. 创建流水线前选择模板

```bash
# 1. 先查询工作空间获取space_id
python -m scripts/main workspaces --name devops

# 2. 查询可用模板
python -m scripts/main templates 133 --name Java

# 3. 选择模板创建流水线
python -m scripts/main create "我的Java流水线" 133
```

### 4. 分页浏览模板

```bash
# 查看第一页
python -m scripts/main templates 133 --page 1 --size 20

# 查看第二页
python -m scripts/main templates 133 --page 2 --size 20
```

## 与流水线列表的区别

| 功能 | 命令 | 说明 |
|------|------|------|
| 流水线模板列表 | `templates <space_id>` | 查询可用的模板配置，用于创建新流水线 |
| 流水线列表 | `pipelines <space_id>` | 查询已创建的流水线，用于执行和管理 |

## 模板使用流程

```
1. 查询模板列表 → templates <space_id>
2. 选择合适的模板 → 记录模板ID或配置
3. 创建流水线 → create <name> <space_id>
4. 配置流水线 → update <pipeline_id>
5. 执行流水线 → run <pipeline_id>
```

## 注意事项

1. **spaceId为必填参数**，可通过 `workspaces` 命令查询获取
2. **pipelineTemplateName 支持模糊搜索**，输入关键字即可匹配
3. **pipelineTemplateParams** 是JSON字符串格式，包含完整的流水线配置模板
4. **status=1** 的模板才可正常使用，禁用状态的模板不会出现在创建流程中
5. 默认分页大小为10，可根据需要调整 `--size` 参数
6. 模板列表只展示当前工作空间下可用的模板
