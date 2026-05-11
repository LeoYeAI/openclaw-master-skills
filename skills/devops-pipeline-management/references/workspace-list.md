---
name: workspace-list
description: 分页查询���作空间列表。当用户需要查看工作空间、查找空间ID、按组织/产品线筛选空间时使用此功能。

触发关键词："工作空间列表"、"空间列表"、"查询空间"、"workspace"
---

# 工作空间列表查询

> ⚠️ **大模型执行约束（必须严格遵守）**
>
> **执行铁律**：
> 1. **API调用规范**：任何发生 API 调用的，**必须实际调用 Python 脚本的 API 功能**，禁止模拟或跳过

## 功能描述

分页查询工作空间列表，支持按名称、组织、产品线等条件筛选。工作���间是流水线管理的基础单元，每个流水线都属于一个工作空间。

## 使用方式

```bash
python -m scripts/main workspaces [options]
```

## API接口

- **路径**: POST /rest/openapi/pipeline/queryWorkspacePage
- **方法**: POST

## 请求参数

### Body 参数 (JSON)

| 字段名 | 类型 | 必填 | 描述 | 示例值 |
|--------|------|------|------|--------|
| workSpaceName | String | 否 | 工作空间名称（模糊搜索） | `devops` |
| pompProjectCode | String | 否 | 项目编码 | `PROJ001` |
| divisionName | String | 否 | 一级组织名称 | `研发中心` |
| teamName | String | 否 | 产品线名称 | `DevOps平台` |
| divisionIdList | List<String> | 否 | 一级组织ID集合 | `["div001", "div002"]` |
| currentPage | Integer | 否 | 页码（默认1） | `1` |
| pageSize | Integer | 否 | 每页大小（默认10） | `10` |

## 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| --name | 工作空间名称（模糊搜索） | `--name devops` |
| --division | 一级组织名称 | `--division "研发中心"` |
| --team | 产品线名称 | `--team "DevOps平台"` |
| --project-code | 项目编码 | `--project-code PROJ001` |
| --page | 页码 | `--page 1` |
| --size | 每页大小 | `--size 20` |

## 请求示例

**基础查询**:
```bash
python -m scripts/main workspaces
```

**按名称搜索**:
```bash
python -m scripts/main workspaces --name devops
```

**按组织筛选**:
```bash
python -m scripts/main workspaces --division "研发中心"
```

**按产品线筛选**:
```bash
python -m scripts/main workspaces --team "DevOps平台"
```

**分页查询**:
```bash
python -m scripts/main workspaces --page 2 --size 20
```

**组合条件查询**:
```bash
python -m scripts/main workspaces --name devops --division "研发中心" --page 1 --size 10
```

**API请求体示例**:
```json
{
  "workSpaceName": "devops",
  "divisionName": "研发中心",
  "teamName": "DevOps平台",
  "currentPage": 1,
  "pageSize": 10
}
```

## 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 50,
    "currentPage": 1,
    "pageSize": 10,
    "data": [
      {
        "id": 1001,
        "workSpaceName": "DevOps研发空间",
        "workSpaceKey": "devops-space",
        "workSpaceVer": "v1.0",
        "divisionId": "div001",
        "divisionKey": "rd-center",
        "divisionName": "研发中心",
        "teamId": "team001",
        "teamKey": "devops-platform",
        "teamName": "DevOps平台",
        "customProductPath": "/artifacts/devops",
        "customImagePath": "/images/devops",
        "deleted": 0,
        "updateTime": "2025-01-15T10:00:00",
        "createTime": "2025-01-10T08:00:00",
        "workSpaceAdminUserList": [
          {
            "userId": 1001,
            "userName": "张三",
            "userAccount": "zhangsan",
            "roleId": 1,
            "roleName": "管理员"
          }
        ],
        "workSpaceNormalUserList": [
          {
            "userId": 1002,
            "userName": "李四",
            "userAccount": "lisi",
            "roleId": 2,
            "roleName": "开发者"
          }
        ],
        "workSpaceProjectList": [
          {
            "projectId": 1001,
            "projectName": "DevOps平台项目",
            "projectCode": "DEVOPS"
          }
        ],
        "workSpaceHelmRepoList": [
          {
            "repoId": 1001,
            "repoName": "helm-repo",
            "repoUrl": "https://helm.example.com"
          }
        ]
      }
    ]
  },
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

## PageResult<WorkSpaceVO> 字段说明

| 字段名 | 类型 | 描述 |
|--------|------|------|
| total | Long | 总记录数 |
| currentPage | Integer | 当前页码 |
| pageSize | Integer | 每页大小 |
| data | List<WorkSpaceVO> | 工作空间列表 |

## WorkSpaceVO 字段说明

| 字段名 | 类型 | 描述 | 示例值 |
|--------|------|------|--------|
| id | Long | 工作空间ID（用于查询流水线列表） | `1001` |
| workSpaceName | String | 工作空间名称 | `DevOps研发空间` |
| workSpaceKey | String | 工作空间Key | `devops-space` |
| workSpaceVer | String | 工作空间版本 | `v1.0` |
| divisionId | String | 一级组织ID | `div001` |
| divisionKey | String | 一级组织Key | `rd-center` |
| divisionName | String | 一级组织名称 | `研发中心` |
| teamId | String | 产品线ID | `team001` |
| teamKey | String | 产品线Key | `devops-platform` |
| teamName | String | 产品线名称 | `DevOps平台` |
| customProductPath | String | 自定义制品路径 | `/artifacts/devops` |
| customImagePath | String | 自定义镜像路径 | `/images/devops` |
| deleted | Integer | 是否删除（0-否，1-是） | `0` |
| updateTime | LocalDateTime | 更新时间 | `2025-01-15T10:00:00` |
| createTime | LocalDateTime | 创建时间 | `2025-01-10T08:00:00` |
| workSpaceAdminUserList | List | 工作空间管理员用户列表 | 详见 AiWorkSpaceUserRoleVO |
| workSpaceNormalUserList | List | 工作空间普通用户列表 | 详见 AiWorkSpaceUserRoleVO |
| workSpaceProjectList | List | 工作空间关联项目列表 | 详见 AiWorkSpaceProjectVO |
| workSpaceHelmRepoList | List | Helm仓库列表 | 详见 AiWorkSpaceHelmRepoVO |

## AiWorkSpaceUserRoleVO 字段说明

| 字段名 | 类型 | 描述 | 示例值 |
|--------|------|------|--------|
| userId | Long | 用户ID | `1001` |
| userName | String | 用户名 | `张三` |
| userAccount | String | 用户账号 | `zhangsan` |
| roleId | Long | 角色ID | `1` |
| roleName | String | 角色名称 | `管理员` |

## AiWorkSpaceProjectVO 字段说明

| 字段名 | 类型 | 描述 | 示例值 |
|--------|------|------|--------|
| projectId | Long | 项目ID | `1001` |
| projectName | String | 项目名称 | `DevOps平台项目` |
| projectCode | String | 项目编码 | `DEVOPS` |

## AiWorkSpaceHelmRepoVO 字段说明

| 字段名 | 类型 | 描述 | 示例值 |
|--------|------|------|--------|
| repoId | Long | 仓库ID | `1001` |
| repoName | String | 仓库名称 | `helm-repo` |
| repoUrl | String | 仓库地址 | `https://helm.example.com` |

## 错误码

| 错误码 | 说明 |
|-------|------|
| 0 | 成功 |
| -1 | 通用失败（具体信息见message） |
| 401 | 无API访问权限 |
| 429 | 请求过于频繁（触发限流） |

## 典型使用场景

### 1. 查找流水线所属空间ID

查询流水线列表需要提供空间ID (spaceId)，可通过此接口获取：

```bash
# 按名称搜索工作空间
python -m scripts/main workspaces --name "我的项目"

# 获取空间ID后查询流水线
python -m scripts/main pipelines 1001
```

### 2. 按组织筛选工作空间

```bash
# 查询研发中心下的所有工作空间
python -m scripts/main workspaces --division "研发中心"
```

### 3. 按产品线筛选工作空间

```bash
# 查询DevOps产品线下的所有工作空间
python -m scripts/main workspaces --team "DevOps平台"
```

## 注意事项

1. 所有筛选参数均为可选，不传参数则查询所有工作空间
2. workSpaceName 支持模糊搜索
3. 工作空间ID (id字段) 是后续查询流水线列表的关键参数
4. 默认分页大小为10，可根据需要调整
5. divisionIdList 参数需要传组织ID数组，通常配合组织树接口使用
