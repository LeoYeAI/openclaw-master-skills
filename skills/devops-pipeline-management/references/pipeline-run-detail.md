---
name: pipeline-run-detail
description: 查询流水线执行详情。当用户需要查看执行日志、获取执行结果时使用此功能。

触发关键词："执行详情"、"执行日志"、"查看执行结果"、"运行记录"
---

# 流水线执行详情

> ⚠️ **大模型执行约束（必须严格遵守）**
>
> **执行铁律**：
> 1. **API调用规范**：任何发生 API 调用的，**必须实际调用 Python 脚本的 API 功能**，禁止模拟或跳过
> 2. **失败自动分析**：当流水线执行失败时，**必须自动调用日志接口并分析原因**，向用户提供解决方案

## 功能描述

根据执行记录ID查询流水线执行详情，包括执行状态、日志、耗时等。

## 使用方式

```bash
python -m scripts/main run-detail <pipeline_log_id>
```

## 执行流程（重要）

```
1. 调用 getPipelineWorkById 获取执行详情
       ↓
2. 检查 pipelineStatus 状态码
       ↓
   ┌───────────────────────────────────────┐
   │  100004 (成功) → 直接返回执行结果        │
   │  100005 (失败) → 进入失败分析流程        │
   │  100006 (取消) → 返回取消信息           │
   │  100002 (执行中) → 返回执行中状态        │
   └───────────────────────────────────────┘
       ↓
3. 失败分析流程 (pipelineStatus = 100005):
   a. 调用 getJenkinsConsoleLog 获取控制台日志
   b. 分析日志内容，识别错误类型
   c. 提供可能的原因和解决方案
   d. 返回给用户完整的分析报告
```

## 失败分析处理规范

当 `pipelineStatus = "100005"` (失败) 时，**必须**执行以下步骤：

### 步骤1：获取控制台日志

```bash
python -m scripts/main console-log <pipeline_log_id>
```

**API接口**: GET `/rest/openapi/pipeline/getJenkinsConsoleLog?pipelineLogId={pipelineLogId}`

### 步骤2：分析日志内容

大模型需要根据日志内容分析以下常见错误类型：

| 错误类型 | 关键字特征 | 可能原因 | 建议解决方案 |
|---------|-----------|---------|-------------|
| 编译错误 | `compilation failure`、`cannot find symbol`、`语法错误` | 代码语法问题、依赖缺失 | 检查代码语法、确认依赖版本 |
| 单元测试失败 | `Tests run:`、`FAILURES!`、`AssertionError` | 测试用例未通过 | 查看失败测试用例、修复业务逻辑 |
| 依赖下载失败 | `Could not resolve dependencies`、`connection refused`、`timeout` | 网络问题、仓库不可达 | 检查网络、更换镜像源、重试 |
| Docker构建失败 | `Docker build failed`、`COPY failed`、`no such file` | Dockerfile配置错误 | 检查Dockerfile路径和指令 |
| 代码扫描失败 | `SonarQube`、`quality gate`、`code smell` | 代码质量问题 | 修复扫描发现的代码问题 |
| 部署失败 | `deploy failed`、`resource insufficient`、`timeout` | 资源不足、配置错误 | 检查资源配置、扩容或重试 |
| 权限问题 | `Permission denied`、`Access denied`、`403` | 账号权限不足 | 检查账号权限配置 |
| 超时问题 | `timeout`、`timed out`、`exceeded` | 执行时间过长 | 优化构建过程或增加超时时间 |

### 步骤3：生成分析报告

返回给用户的报告应包含：

```markdown
## 流水线执行失败分析报告

### 基本信息
- 流水线名称: {pipelineName}
- 执行记录ID: {id}
- 执行时间: {createTime}
- 持续时长: {duration}秒

### 失败原因分析
{根据日志内容分析的具体失败原因}

### 关键错误日志
```
{截取的关键错误日志片段}
```

### 建议解决方案
1. {解决方案1}
2. {解决方案2}
3. {如有需要，建议联系相关人员}

### 后续操作建议
- [ ] 修复上述问题
- [ ] 重新执行流水线
```

## API接口

- **路径**: GET /rest/openapi/pipeline/getPipelineWorkById
- **方法**: GET

## 请求参数

### Query 参数

| 字段名 | 类型 | 必填 | 描述 | 示例值 |
|--------|------|------|------|--------|
| pipelineLogId | Long | 是 | 执行记录ID | `10001` |

## 响应示例

**成功响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 10001,
    "spaceId": 1001,
    "runTimes": 10,
    "pipelineId": "pipe-abc123",
    "pipelineName": "订单服务构建流水线",
    "pipelineStatus": "100004",
    "pipelineStatusName": "成功",
    "pipelineStageInfo": "[{\"stage\": \"build\", \"status\": \"success\"}]",
    "jenkinsJobId": "job-001",
    "jenkinsJobName": "order-service-build",
    "jenkinsJobUrl": "http://jenkins.example.com/job/order-service-build/10/",
    "runSources": "[{\"sourceId\": \"src-001\", \"branch\": \"master\"}]",
    "runRemark": "日常构建",
    "endTime": "2025-01-15T10:30:00",
    "duration": 300,
    "pipelineParams": "{}",
    "triggerMode": 0,
    "triggerModeName": "手动触发",
    "triggerUser": "zhangsan",
    "triggerParams": "{}",
    "createTime": "2025-01-15T10:25:00",
    "creator": "zhangsan",
    "creatorName": "张三",
    "taskStatusParam": "{}",
    "reRunFlag": 0,
    "fromPipelineLogId": null,
    "runFromPipelineLogId": null
  },
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

## PipelineWorkVO 字段说明

| 字段名 | 类型 | 描述 | 示例值 |
|--------|------|------|--------|
| id | Long | 主键ID | `10001` |
| spaceId | Long | 空间ID | `1001` |
| runTimes | Long | 流水线运行次数 | `10` |
| pipelineId | String | 流水线ID | `pipe-abc123` |
| pipelineName | String | 流水线名称 | `订单服务构建流水线` |
| pipelineStatus | String | 流水线状态编码 | `100004` |
| pipelineStatusName | String | 流水线状态名称 | `成功` |
| pipelineStageInfo | String | 流水线阶段信息和状态 | JSON字符串 |
| jenkinsJobId | String | 构建任务ID | `job-001` |
| jenkinsJobName | String | 构建任务名称 | `order-service-build` |
| jenkinsJobUrl | String | 构建任务URL | `http://jenkins/job/...` |
| runSources | String | 执行时选择的代码源 | JSON字符串 |
| runRemark | String | 执行备注 | `日常构建` |
| endTime | LocalDateTime | 运行结束时间 | `2025-01-15T10:30:00` |
| duration | Long | 持续时间（秒） | `300` |
| pipelineParams | String | 流水线参数 | JSON字符串 |
| triggerMode | Integer | 触发执行方式（0手动/1定时） | `0` |
| triggerModeName | String | 触发方式名称 | `手动触发` |
| triggerUser | String | 触发人 | `zhangsan` |
| triggerParams | String | 触发参数 | JSON字符串 |
| createTime | LocalDateTime | 创建时间 | `2025-01-15T10:25:00` |
| creator | String | 创建人（域账号） | `zhangsan` |
| creatorName | String | 创建人（中文姓名） | `张三` |
| taskStatusParam | String | 流水线任务状态信息 | JSON字符串 |
| reRunFlag | Integer | 重新执行标志 | `0` |
| fromPipelineLogId | Long | 历史流水线执行源记录信息 | `null` |
| runFromPipelineLogId | Long | 重新执行的触发流水线ID | `null` |

## 流水线状态说明

| 状态编码 | 状态名称 | 说明 |
|----------|----------|------|
| 100000 | 未执行 | 初始状态 |
| 100001 | 等待中 | 等待执行 |
| 100002 | 执行中 | 正在运行 |
| 100004 | 成功 | 执行成功 |
| 100005 | 失败 | 执行失败 |
| 100006 | 已取消 | 用户取消 |

## 错误码

| 错误码 | 说明 |
|-------|------|
| 0 | 成功 |
| -1 | 通用失败（具体信息见message） |
| 401 | 无API访问权限 |
| 404 | 流水线或执行记录不存在 |
| 429 | 请求过于频繁（触发限流） |

## 业务场景示例

**场景: 查看构建详情**
```bash
curl -X GET "https://api.example.com/rest/openapi/pipeline/getPipelineWorkById?pipelineLogId=10001" \
  -H "X-User-Account: your_domain_account"
```

## 注意事项

1. 参数使用的是 **pipelineLogId**（执行记录ID），而非pipelineId
2. pipelineLogId为Long类型
3. 部分字段（如pipelineStageInfo、runSources）为JSON字符串，需要解析后使用
4. **当流水线执行失败（pipelineStatus=100005）时，必须自动调用日志接口分析原因**

## 完整失败分析示例

### 示例场景：流水线执行失败分析

**1. 查询执行详情**

```bash
python -m scripts/main run-detail 10086
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "id": 10086,
    "pipelineName": "用户服务构建流水线",
    "pipelineStatus": "100005",
    "pipelineStatusName": "失败",
    "duration": 120,
    "createTime": "2026-03-15T14:30:00",
    "triggerUser": "lisi"
  }
}
```

**2. 检测到失败，自动获取日志**

```bash
python -m scripts/main console-log 10086
```

**日志响应**:
```json
{
  "code": 0,
  "data": {
    "logContent": "[INFO] Building project...\n[ERROR] COMPILATION ERROR : \n[ERROR] /src/main/java/com/example/UserService.java:[25,9] cannot find symbol\n[ERROR]   symbol:   class UserDTO\n[ERROR]   location: class UserService\n[ERROR] -> [Help 1]\n[ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.8.1:compile",
    "isCompleted": true
  }
}
```

**3. 大模型分析后返回给用户的报告**

```markdown
## 流水线执行失败分析报告

### 基本信息
- 流水线名称: 用户服务构建流水线
- 执行记录ID: 10086
- 执行时间: 2026-03-15T14:30:00
- 持续时长: 120秒
- 触发人: lisi

### 失败原因分析
**编译错误**：在 `UserService.java` 第25行找不到 `UserDTO` 类的符号定义。

### 关键错误日志
```
[ERROR] /src/main/java/com/example/UserService.java:[25,9] cannot find symbol
[ERROR]   symbol:   class UserDTO
[ERROR]   location: class UserService
```

### 建议解决方案
1. **检查 import 语句**：确认 `UserDTO` 类是否已正确导入
2. **检查类定义**：确认 `UserDTO` 类是否存在，或是否在正确的包路径下
3. **检查依赖**：如果 `UserDTO` 来自外部依赖，确认 pom.xml 中是否已添加对应依赖

### 后续操作建议
- [ ] 检查 UserService.java 中的 import 语句
- [ ] 确认 UserDTO 类的位置和包名
- [ ] 修复后重新执行流水线
```

## 相关文档

- [流水线执行 API](./pipeline/openapi/06-execute-pipeline-api.md) - 包含 getJenkinsConsoleLog 接口详情
- [流水线取消](./pipeline-cancel.md) - 取消正在执行的流水线
