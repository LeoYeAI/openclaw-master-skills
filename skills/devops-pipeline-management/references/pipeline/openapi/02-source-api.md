# 代码源 API

本文档定义代码源相关的 OpenAPI 接口。

---

## 添加代码源

### 请求

```
POST /rest/openapi/pipeline/source/save
```

### 代码源 - 最小请求体

```json
{
  "pipelineId": "pipe-001",
  "sourceType": "code",
  "repoType": "GITEE",
  "repoUrl": "https://code.iflytek.com/demo/my-app",
  "branch": "master",
  "workPath": "my-app_abc1"
}
```

### 制品源 - 最小请求体

```json
{
  "pipelineId": "pipe-001",
  "sourceType": "package",
  "repoType": "IPACKAGE",
  "packageType": "docker",
  "firstDir": "my-project",
  "imageName": "my-image",
  "defaultTag": "latest",
  "workPath": "my-image_xyz2"
}
```

---

## 字段说明

### 公共字段

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `pipelineId` | string | 是 | 流水线ID |
| `id` | string | 否 | 更新时必填 |
| `name` | string | 是 | 源名称（仓库名/镜像名） |
| `sourceType` | string | 是 | `code` 或 `package` |
| `repoType` | string | 是 | 仓库类型 |
| `workPath` | string | 是 | 工作目录 |

### sourceType 枚举

| 值 | 说明 |
|---|------|
| `code` | 代码源（Git仓库） |
| `package` | 制品源 |

### repoType 枚举

| 值 | sourceType | 说明 |
|---|------------|------|
| `GITEE` | code | Gitee 平台 |
| `GITLAB` | code | GitLab 平台 |
| `FLYCODE` | code | 质效Code平台 |
| `IPACKAGE` | package | iPackage 制品仓库 |

---

## 代码源完整字段

```json
{
  "id": "source-001",
  "name": "my-app",
  "nodeType": "custom-source-node",
  "defaultBranch": "master",
  "data": {
    "workPath": "my-app_abc1",
    "repoType": "GITEE",
    "refsType": "BRANCH",
    "sourceType": "code",
    "repoUrl": "https://code.iflytek.com/demo/my-app",
    "branch": "master",
    "commitId": "",
    "credentialsId": "",
    "webhook": {
      "enable": false,
      "event": ["pushEvents"],
      "branchEnable": false,
      "branch": "",
      "tagEnable": false,
      "tag": ""
    }
  }
}
```

### 代码源字段详情

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|-------|------|
| `refsType` | string | 否 | `BRANCH` | `BRANCH` / `TAG` / `COMMIT` |
| `repoUrl` | string | 是 | - | 仓库HTTP地址 |
| `branch` | string | 是 | - | 默认分支 |
| `commitId` | string | 否 | `""` | 指定提交ID |
| `credentialsId` | string | 否 | `""` | 凭证ID |

### Webhook 配置

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `webhook.enable` | boolean | 否 | 是否启用触发 |
| `webhook.event` | string[] | 条件 | 触发事件 |
| `webhook.branchEnable` | boolean | 否 | 分支过滤开关 |
| `webhook.branch` | string | 条件 | 分支正则 |
| `webhook.tagEnable` | boolean | 否 | 标签过滤开关 |
| `webhook.tag` | string | 条件 | 标签正则 |

### 触发事件枚举 (webhook.event)

**GITEE:**
| 值 | 说明 |
|---|------|
| `pushEvents` | 代码推送 |
| `createBranch` | 创建分支 |
| `createTag` | 创建标签 |
| `pullRequestMerge` | PR合并 |
| `pullRequestOpen` | PR开启 |

**GITLAB:**
| 值 | 说明 |
|---|------|
| `pushEvents` | 代码推送 |
| `createTag` | 创建标签 |
| `mergeRequest` | MR事件 |

---

## 制品源完整字段

```json
{
  "id": "source-001",
  "name": "my-image:latest",
  "nodeType": "custom-source-node",
  "data": {
    "workPath": "my-image_xyz2",
    "sourceType": "package",
    "repoType": "IPACKAGE",
    "packageName": "Artifactory",
    "packageType": "docker",
    "firstDir": "my-project",
    "imageName": "my-image",
    "normalArtifactName": "",
    "imageAddress": "registry.iflytek.com/my-project/my-image",
    "normalAddress": "",
    "ipackagePath": "my-project/docker/my-image",
    "defaultTag": "latest"
  }
}
```

### 制品源字段详情

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| `packageType` | string | 是 | `docker` / `normal` |
| `firstDir` | string | 是 | 一级目录 |
| `imageName` | string | 条件 | 镜像名（docker必填） |
| `normalArtifactName` | string | 条件 | 制品名（normal必填） |
| `defaultTag` | string | 是 | 默认版本 |

---

## 删除代码源

### 请求

```
DELETE /rest/openapi/pipeline/source/delete?sourceId={sourceId}&pipelineId={pipelineId}
```

### 响应

```json
{
  "code": "200",
  "message": "success"
}
```

---

## 响应格式

### 添加成功

```json
{
  "code": "200",
  "data": {
    "sourceId": "source-001",
    "workPath": "my-app_abc1"
  }
}
```
