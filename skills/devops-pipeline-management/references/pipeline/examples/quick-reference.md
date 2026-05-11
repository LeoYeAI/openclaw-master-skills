# Skill 场景快速参考

本文档提供 Skill 开发中常见场景的快速参考。

---

## 场景1: 创建流水线

### 最小请求
```json
POST /devops/api/pipeline/save
{
  "name": "流水线名称",
  "spaceId": "空间ID"
}
```

### 响应
```json
{
  "code": "200",
  "data": { "pipelineId": "xxx" }
}
```

---

## 场景2: 添加代码源

### 最小请求（代码源）
```json
POST /devops/api/pipeline/source/save
{
  "pipelineId": "流水线ID",
  "sourceType": "code",
  "repoType": "GITEE",
  "repoUrl": "https://code.iflytek.com/team/repo",
  "branch": "master",
  "workPath": "repo_abc1"
}
```

### 最小请求（制品源）
```json
POST /devops/api/pipeline/source/save
{
  "pipelineId": "流水线ID",
  "sourceType": "package",
  "repoType": "IPACKAGE",
  "packageType": "docker",
  "firstDir": "project",
  "imageName": "my-image",
  "defaultTag": "latest",
  "workPath": "image_xyz2"
}
```

---

## 场景3: 添加任务

### Step 1: 获取任务ID
```http
GET /devops/api/pipeline/task/createTaskId?pipelineId={pipelineId}
```

### Step 2: 添加任务

#### Maven 构建
```json
POST /devops/api/pipeline/task/save
{
  "id": "任务ID",
  "pipelineId": "流水线ID",
  "stageId": "阶段ID",
  "taskData": {
    "taskCategory": "Build",
    "jobType": "MavenBuild",
    "name": "Maven构建",
    "workPath": "工作目录",
    "sourceId": "代码源ID",
    "jdkVersion": "JDK17",
    "mavenVersion": "Maven3.8.x"
  }
}
```

#### Node.js 构建
```json
{
  "taskCategory": "Build",
  "jobType": "NpmBuild",
  "name": "Node.js构建",
  "workPath": "工作目录",
  "sourceId": "代码源ID",
  "nodeVersion": "Node18"
}
```

#### Docker 构建
```json
{
  "taskCategory": "DockerBuild",
  "jobType": "DockerBuildAndUpload",
  "name": "镜像构建",
  "workPath": "工作目录",
  "sourceId": "代码源ID",
  "dockerfilePath": "Dockerfile",
  "imageName": "${PIPELINE_NAME}",
  "tag": "${BUILD_NUMBER}"
}
```

#### 主机部署
```json
{
  "taskCategory": "Deploy",
  "jobType": "HostDeploy",
  "name": "主机部署",
  "workPath": "工作目录",
  "sourceId": "代码源ID",
  "hostGroupId": "主机组ID",
  "targetPath": "/app"
}
```

#### 执行命令
```json
{
  "taskCategory": "Build",
  "jobType": "OrderAction",
  "name": "执行命令",
  "workPath": "工作目录",
  "sourceId": "代码源ID",
  "script": "echo hello"
}
```

---

## 场景4: 执行流水线

### 请求格式（taskDataList 必填）
```json
POST /devops/api/pipeline/runByManual
{
  "pipelineId": "流水线ID",
  "runSources": [...],
  "taskDataList": [
    {
      "id": "task-001",
      "name": "任务名称"
    }
  ]
}
```

**注意**: `taskDataList` 为必填项，至少需要选择一个任务。

### 指定分支执行
```json
POST /devops/api/pipeline/runByManual
{
  "pipelineId": "流水线ID",
  "runSources": [
    {
      "id": "source-001",
      "name": "代码库",
      "shortName": "代码库",
      "refsType": "BRANCH",
      "refsTypeValue": "develop",
      "data": {
        "sourceType": "code",
        "repoType": "GITEE",
        "refsType": "BRANCH",
        "repoUrl": "https://code.iflytek.com/team/repo",
        "branch": "develop",
        "workPath": "repo_abc1"
      }
    }
  ]
}
```

### 指定制品版本执行
```json
POST /devops/api/pipeline/runByManual
{
  "pipelineId": "流水线ID",
  "runSources": [
    {
      "id": "source-002",
      "name": "Docker镜像",
      "shortName": "Docker镜像",
      "data": {
        "sourceType": "package",
        "repoType": "IPACKAGE",
        "packageType": "DOCKER",
        "workPath": "image_xyz2",
        "imageName": "my-image",
        "defaultTag": "v2.0.0",
        "imageAddress": "registry.iflytek.com/project/my-image:v2.0.0"
      }
    }
  ]
}
```

### 响应
```json
{
  "code": "200",
  "data": {
    "buildNumber": "15",
    "buildLogId": "log-001"
  }
}
```

---

## 场景5: 获取分支/版本列表

### 获取最近执行的配置
```json
POST /devops/api/pipeline/queryLastestSelectedValueByField
{
  "pipelineId": "流水线ID",
  "codeSourceParams": [
    {
      "sourceType": "code",
      "refsType": "BRANCH",
      "repoType": "GITEE",
      "repoUrl": "https://code.iflytek.com/team/repo",
      "workPath": "repo_abc1"
    }
  ],
  "artifactParams": []
}
```

### 获取分支列表
```json
POST /devops/api/pipeline/getRepoBranchAndTagList
[
  {
    "refsType": "BRANCH",
    "repoType": "GITEE",
    "repoUrl": "https://code.iflytek.com/team/repo",
    "search": "",
    "currentPage": 1,
    "pageSize": 20
  }
]
```

### 获取镜像标签列表
```http
GET /devops/api/pipeline/imageTags?imageName={imageName}&repoType=IPACKAGE
```

---

## 场景6: 创建模板

### 最小请求
```json
POST /devops/api/pipeline/template/savePipTemplate
{
  "pipelineTemplateName": "模板名称",
  "pipelineTemplateLanguage": "java",
  "pipelineTemplateVisibleRangeType": "personal",
  "pipelineConfig": {
    "name": "流水线名称",
    "sources": [],
    "stages": [...]
  },
  "taskDataList": [...]
}
```

---

## 常用 jobType 速查

| 分类 | jobType | 说明 |
|-----|---------|------|
| Build | `MavenBuild` | Maven构建 |
| Build | `NpmBuild` | Node.js构建 |
| Build | `PythonBuild` | Python构建 |
| Build | `GoBuild` | Go构建 |
| Build | `OrderAction` | 执行命令 |
| DockerBuild | `DockerBuildAndUpload` | Docker构建 |
| DockerBuild | `MavenDockerBuild` | Maven镜像构建 |
| DockerBuild | `NpmDockerBuild` | Node.js镜像构建 |
| Deploy | `HostDeploy` | 主机部署 |
| Deploy | `HostDockerDeploy` | Docker部署 |
| Deploy | `SaeImageUpdate` | SAE部署 |
| CodeScanner | `SonarQube` | 代码扫描 |
| Normal | `ManualReview` | 人工审核 |

---

## 条件必填规则

### 模板 vs 流水线

| 字段 | 模板 | 流水线 |
|-----|------|--------|
| `workPath` | 可空 | 必填 |
| `sourceId` | 可空 | 必填 |
| `jdkVersion` | 可选 | 必填 |
| `nodeVersion` | 可选 | 必填 |

### 制品上传

| 条件 | 必填字段 |
|-----|---------|
| `uploadArtifact=true` | `artifactPath`, `artifactSuffix` |
| `artifactCompress=true` | `compressType`, `packagedName` |

### 自定义镜像

| 条件 | 必填字段 |
|-----|---------|
| `buildImageModel=custom` | `executeImageId` |

---

## 错误处理

### 常见错误码

| 错误码 | 说明 | 解决方案 |
|-------|------|---------|
| `400` | 参数错误 | 检查必填字段 |
| `401` | 未授权 | 检查 Token |
| `404` | 资源不存在 | 检查 ID 是否正确 |
| `500` | 服务器错误 | 联系管理员 |

### 执行流水线常见错误

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `分支不存在` | 指定的分支在仓库中不存在 | 检查分支名是否正确 |
| `制品版本不存在` | 指定的版本在制品库中不存在 | 检查版本号是否正确 |
| `流水线正在执行中` | 同一流水线已有运行中的任务 | 等待执行完成或取消 |
| `sourceId不匹配` | runSources 中的 id 与流水线配置不一致 | 检查 sources 配置 |

---

## runSources 数据结构速查

### 代码源 (sourceType: code)

```json
{
  "id": "source-001",
  "name": "代码库名称",
  "shortName": "代码库名称",
  "refsType": "BRANCH",
  "refsTypeValue": "master",
  "data": {
    "sourceType": "code",
    "repoType": "GITEE",
    "refsType": "BRANCH",
    "repoUrl": "仓库地址",
    "branch": "分支名",
    "workPath": "工作目录"
  }
}
```

### Docker 制品源 (sourceType: package, packageType: DOCKER)

```json
{
  "id": "source-002",
  "name": "镜像名称",
  "shortName": "镜像名称",
  "data": {
    "sourceType": "package",
    "repoType": "IPACKAGE",
    "packageType": "DOCKER",
    "workPath": "工作目录",
    "imageName": "镜像名",
    "defaultTag": "标签",
    "imageAddress": "完整镜像地址"
  }
}
```

### 普通制品源 (sourceType: package, packageType: NORMAL)

```json
{
  "id": "source-003",
  "name": "制品名称",
  "shortName": "制品名称",
  "data": {
    "sourceType": "package",
    "repoType": "IPACKAGE",
    "packageType": "NORMAL",
    "workPath": "工作目录",
    "normalArtifactName": "制品名",
    "fullPath": "完整路径",
    "defaultTag": "版本"
  }
}
```
