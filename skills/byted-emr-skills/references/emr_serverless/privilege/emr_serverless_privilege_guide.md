# EMR Serverless 队列权限操作指南

## 概述

EMR Serverless 提供全托管的 Serverless 形态大数据服务，主要面向作业提交和资源队列管理。队列权限是 Serverless 环境中资源队列的访问控制机制，用于限制用户对队列的操作权限。

## 说明

本文档提供 Serverless Spark 中 **队列权限** 相关的 OpenAPI。

**OpenAPI 调用方式**

- **API Version** 统一为 **2024-03-25**
- **Service**： emr_serverless

## 核心调用方法

所有 EMR Serverless 队列管理操作均通过 `scripts/serverless/emr_serverless_manager.py` 中的 `manage_emr_serverless` 方法实现。

# 队列权限管理操作
### 1. 数据队列获权方列表 (ListAuthorizedPrincipalsForQueue)

**接口描述**  
根据指定的队列，获取具有其权限的用户/用户组列表。

**请求方式**： `GET`  
**Action**： `ListAuthorizedPrincipalsForQueue`

**请求参数**

| 参数 | 类型 | 是否必须 | 描述 |
|------|------|----------|------|
| QueueName | String | Y | 队列名 |
| IdentityName | String | N | 过滤项：用户/组名关键词搜索，精确匹配 |
| IdentityType | String | N | 过滤项：用户类型，可选项为：`User`/`Group`/`GroupDataLeap`。如果多选，则逗号分隔，如 `xxx,yyy` |
| Role | String | N | 过滤项：角色，可选项为：`Admin`/`Viewer`。如果多选，则逗号分隔，如 `xxx,yyy` |
| Limit | Integer | Y | 每页能够显示的最大数量 |
| Offset | Integer | Y | 最小值为1，代表页数 |

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action ListAuthorizedPrincipalsForQueue \
  --method GET \
  --query '{
    "QueueName": "my-queue",
    "IdentityName": "admin",
    "IdentityType": "User",
    "Role": "Admin",
    "Limit": 10,
    "Offset": 1
  }'
```

**返回参数**

| 参数 | 类型 | 描述 |
|------|------|------|
| AccountId | String | 用户所属租户的 AccountID |
| IdentityId | String | 用户/组 ID |
| IdentityName | String | 用户/组 名称 |
| IdentityType | String | 用户类型：`User`/`Group` |
| ResourceId | String | 资源ID，队列权限中为队列ID |
| Role | String | 角色：`Admin`/`Viewer` |
| AuthorizedSource | String | 授权来源：由 xxx 授予、源自继承 |
| IsInherit | Boolean | true/false，true 表示源自继承，无法修改&删除 |
| ExpiredTime | String | 到期时间：`2021-12-30 23:23:23`，-1 表示"永久授权"。对于 UDF/Resource/Queue，此项为空。 |
| ExpiredDays | Int | 到期天数：20，-1 表示"永久授权" |

**返回示例**

```json
{
    "ResponseMetadata": {
        "RequestId": "20260314144521DB63174CB8DF6B2D186F",
        "Action": "ListAuthorizedPrincipalsForQueue",
        "Version": "2024-03-25",
        "Service": "emr_serverless",
        "Region": "cn-beijing",
        "Error": null
    },
    "Result": {
        "Data": [
            {
                "AuthorizedSource": "由lixiaoyu.2sre@bytedance.com授予",
                "ResourceId": "1238543785583968256",
                "Role": "Developer",
                "IdentityType": "User",
                "ExpiredDays": -1,
                "IsInherit": false,
                "ExpiredTime": "",
                "QueueName": "公共队列",
                "AccountId": "emr_serverless_2100005493",
                "IdentityId": "58658394",
                "IdentityName": "emr_backend_user"
            },
            {
                "AuthorizedSource": "由liuzhaoxing授予",
                "ResourceId": "1238543785583968256",
                "Role": "Admin",
                "IdentityType": "User",
                "ExpiredDays": -1,
                "IsInherit": false,
                "ExpiredTime": "",
                "QueueName": "公共队列",
                "AccountId": "emr_serverless_2100005493",
                "IdentityId": "5608315",
                "IdentityName": "shenyihong.zzz@bytedance.com"
            }
        ],
        "Limit": 10,
        "Offset": 1,
        "Total": 7
    }
}
```

**参数说明**

- **IdentityType 枚举值**：
  - `User`：用户
  - `Group`：用户组
  - `GroupDataLeap`：DataLeap 用户组

- **Role 枚举值**：
  - `Admin`：管理员权限，可管理队列和作业
  - `Viewer`：查看权限，只能查看队列和作业信息

- **ExpiredTime 特殊值**：
  - `-1`：表示永久授权

- **IsInherit 含义**：
  - `true`：权限源自继承，无法修改和删除
  - `false`：权限为直接授予，可以修改和删除
  

### 2. 用户名模糊查询&判断用户是否已经具有指定队列的权限 (ListIAMUsersWithQueueRole)

**接口描述**  
根据用户名模糊查询用户列表，同时判断用户是否已经具有指定队列的权限。

**请求方式**： `GET`  
**Action**： `ListIAMUsersWithQueueRole`

**请求参数**

| 参数 | 是否必须 | 描述 |
|------|----------|------|
| IdentityName | Y | 用户名，支持模糊查询 |
| QueueName | Y | 队列名 |
| Limit | Y | 每页能够显示的最大数量 |
| Offset | Y | 最小值为1，代表页数 |

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action ListIAMUsersWithQueueRole \
  --method GET \
  --query '{
    "IdentityName": "admin",
    "QueueName": "my-queue",
    "Limit": 10,
    "Offset": 1
  }'
```

**返回参数**

通用操作响应 `OperateResponse` 结构：

| 参数 | 类型 | 描述 |
|------|------|------|
| Success | boolean | 是否操作成功 |

通用列表实体 `DataList<T>` 结构：

| 参数 | 类型 | 描述 |
|------|------|------|
| Items | Array<T> | 数据列表 |
| TotalCount | Integer | 总记录数 |
| PageSize | Integer | 每页大小 |
| PageNum | Integer | 当前页码 |

`IAMUserWithRole` 对象字段说明：

| 参数 | 类型 | 描述 |
|------|------|------|
| AccountId | String | 用户所属租户的 AccountID |
| IdentityId | String | 用户/组 ID |
| IdentityName | String | 用户/组 名称 |
| IdentityType | String | 用户类型：User/Group |
| Role | String | 角色：Admin/Viewer，如果没有 Role，则为空。多个以 , 分隔 |

**返回示例**

```json
{
    "ResponseMetadata": {
        "RequestId": "20260314153756D5CDE8AAE1996E6CB36C",
        "Action": "ListIAMUsersWithQueueRole",
        "Version": "2024-03-25",
        "Service": "emr_serverless",
        "Region": "cn-beijing",
        "Error": null
    },
    "Result": {
        "Data": [
            {
                "Role": "",
                "IdentityType": "User",
                "AccountId": "emr_serverless_2100005493",
                "IdentityId": "76058391",
                "IdentityName": "changailing"
            },
            {
                "Role": "",
                "IdentityType": "User",
                "AccountId": "emr_serverless_2100005493",
                "IdentityId": "75959369",
                "IdentityName": "chenxiaoya.cxy"
            }
        ],
        "Limit": 1000,
        "Offset": 0,
        "Total": 199
    }
}
```

### 3. 权限授予 (GrantQueuePrivilege)

**接口描述**  
为用户授予指定数据对象的权限。

**请求方式**： `POST`  
**Action**： `GrantQueuePrivilege`

**请求参数**

| 参数 | 是否必须 | 描述 |
|------|----------|------|
| AccountID | N | 用户 AccountID，默认为当前用户 AccountID |
| IdentityId | Y | 用户/组 ID |
| IdentityType | Y | 用户类型：`User`/`Group` |
| QueueName | Y | 队列名 |
| Role | Y | 角色（对数据对象的操作权限），可选项为：`Admin`/`Viewer` |

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action GrantQueuePrivilege \
  --method POST \
  --body '{
    "IdentityId": "user-123",
    "IdentityType": "User",
    "QueueName": "my-queue",
    "Role": "Admin"
  }'
```

**请求参数示例**（JSON）

```json
{
    "IdentityId": "user-123",
    "IdentityType": "User",
    "QueueName": "my-queue",
    "Role": "Admin"
}
```

**返回参数**

通用操作响应 `OperateResponse` 结构：

| 参数 | 类型 | 描述 |
|------|------|------|
| Success | boolean | 是否操作成功 |

**返回示例**

```json
{
    "ResponseMetadata": {
        "RequestId": "202603141538454C8E24E0A6DA5D2C6D38",
        "Action": "GrantQueuePrivilege",
        "Version": "2024-03-25",
        "Service": "emr_serverless",
        "Region": "cn-beijing",
        "Error": null
    },
    "Result": {
        "Success": true
    }
}
```

### 4. 修改权限 (AlterQueuePrivilege)

**接口描述**  
修改用户对指定队列的权限。实际效果可以简单理解为：先对老的权限 RevokeQueuePrivilege，然后再对新的权限 GrantQueuePrivilege。

**请求方式**： `POST`  
**Action**： `AlterQueuePrivilege`

**请求参数**

| 参数 | 是否必须 | 描述 |
|------|----------|------|
| AccountID | N | 用户 AccountID，默认为当前用户 AccountID |
| IdentityId | Y | 用户/组 ID |
| IdentityType | Y | 用户类型：`User`/`Group` |
| QueueName | Y | 队列名 |
| OldRole | Y | 老角色（对数据对象的操作权限），可选项为：`Admin`/`Viewer` |
| Role | Y | 角色（对数据对象的操作权限），可选项为：`Admin`/`Viewer` |

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action AlterQueuePrivilege \
  --method POST \
  --body '{
    "IdentityId": "user-123",
    "IdentityType": "User",
    "QueueName": "my-queue",
    "OldRole": "Viewer",
    "Role": "Admin"
  }'
```

**请求参数示例**（JSON）

```json
{
    "IdentityId": "user-123",
    "IdentityType": "User",
    "QueueName": "my-queue",
    "OldRole": "Viewer",
    "Role": "Admin"
}
```

**返回参数**

通用操作响应 `OperateResponse` 结构：

| 参数 | 类型 | 描述 |
|------|------|------|
| Success | boolean | 是否操作成功 |

**返回示例**

```json
{
    "ResponseMetadata": {
        "RequestId": "202603141543178C958A4205A46B2BB5AD",
        "Action": "AlterQueuePrivilege",
        "Version": "2024-03-25",
        "Service": "emr_serverless",
        "Region": "cn-beijing",
        "Error": null
    },
    "Result": {
        "Success": true
    }
}
```

**参数说明**

- **IdentityType 枚举值**：
  - `User`：用户
  - `Group`：用户组

- **Role 枚举值**：
  - `Admin`：管理员权限，可管理队列和作业
  - `Viewer`：查看权限，只能查看队列和作业信息

**使用场景**

- **权限升级**：将用户的权限从 Viewer 升级为 Admin
- **权限降级**：将用户的权限从 Admin 降级为 Viewer
- **权限调整**：调整用户组的权限级别

**注意事项**

1. **原子操作**：该操作是原子性的，确保权限修改的一致性
2. **权限验证**：修改前会验证 OldRole 是否与当前权限一致，避免误操作
3. **权限继承**：如果权限源自继承，修改操作可能会失败或需要特殊处理
4. **权限冲突**：确保修改后的权限不会与其他权限来源产生冲突
