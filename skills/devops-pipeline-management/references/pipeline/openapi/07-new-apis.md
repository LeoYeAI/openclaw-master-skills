# 新增 API 汇总

本文档汇总了 2026-03-15 更新的新增 OpenAPI 接口。

---

## 新增接口列表

| 序号 | 接口名称 | 请求方法 | 接口路径 | 说明 |
|------|----------|----------|----------|------|
| 1 | 查询流水线控制台日志 | GET | /getJenkinsConsoleLog | 查询流水线执行日志 |
| 2 | 查询单个流水线模板 | GET | /getPipTemplateById | 获取模板详情 |
| 3 | 保存流水线模板 | POST | /savePipTemplate | 创建/编辑模板 |
| 4 | 查询仓库token配置状态 | POST | /checkRepoTokenByRepoTypeList | 检查token是否配置 |
| 5 | 查询流水线基本信息 | GET | /queryPipelineById | 获取流水线基本信息 |
| 6 | 获取镜像tag列表 | GET | /imageTags | 分页获取镜像标签 |
| 7 | 获取包版本列表 | GET | /packageVersions | 获取制品版本 |

---

## 1. 查询流水线控制台日志

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/getJenkinsConsoleLog` |
| 请求方法 | GET |
| 接口描述 | 根据执行记录ID查询流水线的控制台日志 |

### 使用场景

- 查看流水线执行过程的日志输出
- 调试流水线执行问题
- 监控长时间运行的流水线

### 请求参数

| 字段名 | 类型 | 必填 | 描述 | 示例值 |
|--------|------|------|------|--------|
| pipelineLogId | Long | 是 | 执行记录ID | `10001` |

### 请求示例

```
GET /rest/openapi/pipeline/getJenkinsConsoleLog?pipelineLogId=10001
```

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "logContent": "[INFO] Build started at 2025-01-15 10:00:00\n[INFO] Compiling source code...\n[INFO] Build successful!",
    "hasMore": false,
    "nextStart": 0,
    "isCompleted": true
  },
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

### PipelineJenkinsLogVO 字段说明

| 字段名 | 类型 | 描述 |
|--------|------|------|
| logContent | String | 日志内容 |
| hasMore | Boolean | 是否有更多日志 |
| nextStart | Integer | 下次读取的起始位置（用于分页读取长日志） |
| isCompleted | Boolean | 流水线是否已完成 |

### Python 调用示例

```python
def get_console_log(self, pipeline_log_id: int) -> dict:
    """获取流水线控制台日志"""
    params = {'pipelineLogId': pipeline_log_id}
    return self._request('GET', '/api/ai-bff/rest/openapi/pipeline/getJenkinsConsoleLog', params=params)

# 使用示例
result = client.get_console_log(10001)
if result['code'] == 0:
    log_data = result['data']
    print(log_data['logContent'])
    if log_data['hasMore']:
        print("还有更多日志...")
```

---

## 2. 查询单个流水线模板

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/getPipTemplateById` |
| 请求方法 | GET |
| 接口描述 | 根据ID查询单个流水线模板详情 |

### 使用场景

- 获取模板完整配置
- 基于模板创建流水线
- 编辑模板前获取当前配置

### 请求参数

| 字段名 | 类型 | 必填 | 描述 | 示例值 |
|--------|------|------|------|--------|
| id | String | 是 | 流水线模板ID | `template_123456` |

### 请求示例

```
GET /rest/openapi/pipeline/getPipTemplateById?id=template_123456
```

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "template_123456",
    "templateName": "Java构建模板",
    "templateType": "java",
    "description": "Java项目标准构建模板",
    "stages": [
      {
        "name": "构建",
        "steps": [
          {
            "name": "Maven构建",
            "type": "maven",
            "command": "mvn clean package"
          }
        ]
      }
    ],
    "createTime": "2025-01-10T08:00:00",
    "updateTime": "2025-01-15T10:00:00"
  },
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Python 调用示例

```python
def get_pipeline_template(self, template_id: str) -> dict:
    """查询单个流水线模板"""
    params = {'id': template_id}
    return self._request('GET', '/api/ai-bff/rest/openapi/pipeline/getPipTemplateById', params=params)

# 使用示例
result = client.get_pipeline_template("template_123456")
if result['code'] == 0:
    template = result['data']
    print(f"模板名称: {template['templateName']}")
    print(f"阶段数量: {len(template.get('stages', []))}")
```

---

## 3. 保存流水线模板

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/savePipTemplate` |
| 请求方法 | POST |
| 接口描述 | 保存新建或编辑的流水线模板配置 |

### 使用场景

- 创建新的流水线模板
- 编辑现有模板
- 保存主机部署配置

### 请求体

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| id | String | 否 | 模板ID（为空则新建） |
| templateName | String | 是 | 模板名称 |
| templateType | String | 是 | 模板类型 |
| description | String | 否 | 模板描述 |
| stages | List | 是 | 阶段配置列表 |
| taskDataList | List | 否 | 任务参数列表（用于主机部署配置） |

### TaskData 字段说明（主机部署）

| 字段名 | 类型 | 描述 |
|--------|------|------|
| jobType | String | 任务类型：`HostDeploy` 或 `HostDockerDeploy` |
| hostGroupId | Long | 主机组ID |
| allHosts | Boolean | 是否选择全部主机 |
| hostIds | List<Long> | 主机ID列表（allHosts为false时必填） |

### 新建模板请求示例

```json
{
  "templateName": "Java构建模板",
  "templateType": "java",
  "description": "Java项目标准构建模板",
  "stages": [
    {
      "name": "构建",
      "steps": [
        {
          "name": "Maven构建",
          "type": "maven",
          "command": "mvn clean package"
        }
      ]
    }
  ],
  "taskDataList": [
    {
      "data": {
        "jobType": "HostDeploy",
        "hostGroupId": 1001,
        "allHosts": false,
        "hostIds": [1001, 1002]
      }
    }
  ]
}
```

### 编辑模板请求示例

```json
{
  "id": "template_123456",
  "templateName": "Java构建模板V2",
  "templateType": "java",
  "description": "更新后的Java项目构建模板",
  "stages": [
    {
      "name": "构建",
      "steps": [
        {
          "name": "Maven构建",
          "type": "maven",
          "command": "mvn clean package -DskipTests"
        }
      ]
    }
  ]
}
```

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": "template_123456",
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Python 调用示例

```python
def save_pipeline_template(
    self,
    template_name: str,
    template_type: str,
    stages: list,
    template_id: str = None,
    description: str = None,
    task_data_list: list = None
) -> dict:
    """保存流水线模板"""
    data = {
        'templateName': template_name,
        'templateType': template_type,
        'stages': stages
    }
    if template_id:
        data['id'] = template_id
    if description:
        data['description'] = description
    if task_data_list:
        data['taskDataList'] = task_data_list
    return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/savePipTemplate', data=data)

# 使用示例 - 新建模板
result = client.save_pipeline_template(
    template_name="Python构建模板",
    template_type="python",
    stages=[{"name": "构建", "steps": []}],
    description="Python项目标准构建模板"
)
print(f"创建的模板ID: {result['data']}")
```

---

## 4. 查询仓库token配置状态

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/checkRepoTokenByRepoTypeList` |
| 请求方法 | POST |
| 接口描述 | 根据仓库类型查询是否配置token |

### 使用场景

- 检查代码仓库是否已授权
- 创建流水线前验证仓库配置
- 显示可用仓库类型

### 请求体

```json
{
  "repoTypeList": ["gitlab", "github", "gitee"]
}
```

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "gitlab": true,
    "github": false,
    "gitee": true
  },
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Python 调用示例

```python
def check_repo_token(self, repo_type_list: list) -> dict:
    """查询仓库token配置状态"""
    data = {'repoTypeList': repo_type_list}
    return self._request('POST', '/api/ai-bff/rest/openapi/pipeline/checkRepoTokenByRepoTypeList', data=data)

# 使用示例
result = client.check_repo_token(["gitlab", "github", "gitee"])
if result['code'] == 0:
    for repo_type, configured in result['data'].items():
        status = "已配置" if configured else "未配置"
        print(f"{repo_type}: {status}")
```

---

## 5. 查询流水线基本信息

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/queryPipelineById` |
| 请求方法 | GET |
| 接口描述 | 根据流水线ID查询单条流水线的基本信息 |

### 使用场景

- 获取流水线元数据（不包含完整配置）
- 显示流水线详情页面头部信息
- 检查流水线权限

### 与 /edit 接口的区别

| 接口 | 用途 | 返回内容 |
|------|------|----------|
| /queryPipelineById | 获取基本信息 | 基本信息 + 权限 + 最近执行记录 |
| /edit | 编辑时获取配置 | 完整的 sources + stages 配置 |

### 请求参数

| 字段名 | 类型 | 必填 | 描述 | 示例值 |
|--------|------|------|------|--------|
| pipelineId | String | 是 | 流水线ID | `pipe-abc123` |

### 响应 PipelineTemplateVO

```json
{
  "code": 0,
  "data": {
    "id": "pipe-abc123",
    "pipelineName": "订单服务构建流水线",
    "pipelineKey": "order-service",
    "pipelineAliasId": "PIPE001",
    "label": ["Java", "Microservice"],
    "spaceId": 1001,
    "createTime": "2025-01-15T10:00:00",
    "updateTime": "2025-01-15T10:00:00",
    "creator": "zhangsan",
    "creatorName": "张三",
    "store": 0,
    "permissionList": ["edit", "delete", "run"],
    "pipelineOwner": "zhangsan",
    "pipelineOwnerName": "张三",
    "buildNumber": 10,
    "buildNumberHasUsed": false,
    "latestPipWorkVO": {}
  }
}
```

### Python 调用示例

```python
def get_pipeline_by_id(self, pipeline_id: str) -> dict:
    """查询流水线基本信息"""
    params = {'pipelineId': pipeline_id}
    return self._request('GET', '/api/ai-bff/rest/openapi/pipeline/queryPipelineById', params=params)

# 使用示例
result = client.get_pipeline_by_id("pipe-abc123")
if result['code'] == 0:
    pipeline = result['data']
    print(f"流水线名称: {pipeline['pipelineName']}")
    print(f"构建号: {pipeline['buildNumber']}")
    print(f"权限: {pipeline['permissionList']}")
```

---

## 6. 获取镜像tag列表

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/imageTags` |
| 请求方法 | GET |
| 接口描述 | 分页获取指定镜像的tag列表 |

### 使用场景

- 选择Docker镜像版本
- 执行流水线时选择制品版本
- 查看可用镜像标签

### 请求参数

| 字段名 | 类型 | 必填 | 描述 | 示例值 |
|--------|------|------|------|--------|
| imageName | String | 是 | 镜像名称 | `myapp` |
| tag | String | 否 | 标签名(过滤用) | `v1` |
| pageNo | Integer | 否 | 页码（默认1） | `1` |
| pageSize | Integer | 否 | 每页大小（默认10） | `10` |

### 请求示例

```
GET /rest/openapi/pipeline/imageTags?imageName=myapp&tag=v1&pageNo=1&pageSize=10
```

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 50,
    "currentPage": 1,
    "pageSize": 10,
    "records": [
      "v1.0.0",
      "v1.0.1",
      "v1.0.2",
      "v1.1.0",
      "latest"
    ]
  },
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Python 调用示例

```python
def get_image_tags(self, image_name: str, tag: str = None, page_no: int = 1, page_size: int = 10) -> dict:
    """获取镜像tag列表"""
    params = {'imageName': image_name, 'pageNo': page_no, 'pageSize': page_size}
    if tag:
        params['tag'] = tag
    return self._request('GET', '/api/ai-bff/rest/openapi/pipeline/imageTags', params=params)

# 使用示例
result = client.get_image_tags("myapp", tag="v1", page_size=20)
if result['code'] == 0:
    for tag in result['data']['records']:
        print(tag)
```

---

## 7. 获取包版本列表

### 接口说明

| 项目 | 说明 |
|------|------|
| 接口路径 | `/rest/openapi/pipeline/packageVersions` |
| 请求方法 | GET |
| 接口描述 | 获取指定包的所有版本列表 |

### 使用场景

- 选择普通制品版本
- 执行流水线时选择依赖版本

### 请求参数

| 字段名 | 类型 | 必填 | 描述 | 示例值 |
|--------|------|------|------|--------|
| repo | String | 是 | 仓库名称 | `myrepo` |
| packagePath | String | 是 | 包路径 | `com/example/myapp` |
| packageName | String | 是 | 包名称 | `myapp.jar` |

### 请求示例

```
GET /rest/openapi/pipeline/packageVersions?repo=myrepo&packagePath=com/example/myapp&packageName=myapp.jar
```

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": [
    "2.0.0",
    "1.1.0",
    "1.0.1",
    "1.0.0"
  ],
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Python 调用示例

```python
def get_package_versions(self, repo: str, package_path: str, package_name: str) -> dict:
    """获取包版本列表"""
    params = {
        'repo': repo,
        'packagePath': package_path,
        'packageName': package_name
    }
    return self._request('GET', '/api/ai-bff/rest/openapi/pipeline/packageVersions', params=params)

# 使用示例
result = client.get_package_versions("myrepo", "com/example/myapp", "myapp.jar")
if result['code'] == 0:
    for version in result['data']:
        print(version)
```

---

## 更新的执行流水线字段

`/runByManual` 接口新增了以下字段：

| 字段 | 类型 | 说明 |
|-----|------|------|
| reRunFlag | Integer | 重新执行流水线（0-否/1-重新部署） |
| fromPipelineLogId | Long | 历史流水线执行记录信息 |
| runFromPipelineLogId | Long | 重新执行的触发流水线记录ID |
| versionId | String | 产研平台发布版本号 |
| planId | Long | 产研平台提测版本号 |
| downloadDependInfo | Object | 下载依赖前置信息 |

### 重新执行流水线示例

```json
{
  "pipelineId": "pipe-abc123",
  "reRunFlag": 1,
  "fromPipelineLogId": 10001,
  "runRemark": "重新部署"
}
```

---

## 相关文档

- [流水线 API](./01-pipeline-api.md) - 基础 CRUD 接口
- [流水线执行 API](./06-execute-pipeline-api.md) - 执行相关接口
