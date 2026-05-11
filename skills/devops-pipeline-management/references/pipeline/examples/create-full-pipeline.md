# 创建完整流水线示例

本文档展示如何通过 OpenAPI 创建一个完整的 Java Maven 构建流水线。

---

## 场景描述

创建一个包含以下步骤的流水线：
1. 代码源：Gitee 仓库
2. 构建：Maven 构建
3. 扫描：SonarQube 代码扫描
4. 部署：Docker 镜像构建

---

## 完整流程

### Step 1: 创建流水线

**请求**
```http
POST /devops/api/pipeline/save
Content-Type: application/json
Authorization: Bearer {token}

{
  "name": "Java应用构建流水线",
  "spaceId": "space-001",
  "aliasId": "java-build-pipeline",
  "label": ["Java", "Maven", "Backend"]
}
```

**响应**
```json
{
  "code": "200",
  "data": {
    "pipelineId": "pipe-123456"
  }
}
```

---

### Step 2: 添加代码源

**请求**
```http
POST /devops/api/pipeline/source/save
Content-Type: application/json

{
  "pipelineId": "pipe-123456",
  "sourceType": "code",
  "repoType": "GITEE",
  "repoUrl": "https://code.iflytek.com/myteam/my-java-app",
  "branch": "master",
  "workPath": "my-java-app_a1b2",
  "webhook": {
    "enable": true,
    "event": ["pushEvents"],
    "branchEnable": true,
    "branch": "master|develop"
  }
}
```

**响应**
```json
{
  "code": "200",
  "data": {
    "sourceId": "source-001",
    "workPath": "my-java-app_a1b2"
  }
}
```

---

### Step 3: 创建 Stage 结构

**请求**
```http
POST /devops/api/pipeline/stage/save
Content-Type: application/json

{
  "pipelineId": "pipe-123456",
  "stage": {
    "id": "stage-build",
    "name": "构建阶段",
    "nodeType": "custom-stage-node",
    "steps": [
      {
        "id": "step-build",
        "name": "构建步骤",
        "nodeType": "custom-step-node",
        "idx": 0,
        "driven": 0,
        "tasks": []
      }
    ]
  }
}
```

---

### Step 4: 获取任务ID（Maven构建）

**请求**
```http
GET /devops/api/pipeline/task/createTaskId?pipelineId=pipe-123456
```

**响应**
```json
{
  "code": "200",
  "data": "task-maven-001"
}
```

---

### Step 5: 添加 Maven 构建任务

**请求**
```http
POST /devops/api/pipeline/task/save
Content-Type: application/json

{
  "id": "task-maven-001",
  "pipelineId": "pipe-123456",
  "stageId": "stage-build",
  "taskData": {
    "taskCategory": "Build",
    "jobType": "MavenBuild",
    "name": "Maven构建",
    "workPath": "my-java-app_a1b2",
    "sourceId": "source-001",
    "jdkVersion": "JDK17",
    "mavenVersion": "Maven3.8.x",
    "script": "mvn -B clean package -Dmaven.test.skip=true",
    "uploadArtifact": true,
    "artifactPath": ["target/"],
    "artifactSuffix": ["jar"],
    "artifactCompress": true,
    "compressType": "TAR(.tgz)",
    "packagedName": "App_${PIPELINE_LOG_ID}"
  }
}
```

---

### Step 6: 添加 SonarQube 扫描任务

**获取任务ID**
```http
GET /devops/api/pipeline/task/createTaskId?pipelineId=pipe-123456
```

**添加任务**
```http
POST /devops/api/pipeline/task/save
Content-Type: application/json

{
  "id": "task-sonar-001",
  "pipelineId": "pipe-123456",
  "stageId": "stage-build",
  "taskData": {
    "taskCategory": "CodeScanner",
    "jobType": "SonarQube",
    "name": "代码扫描",
    "workPath": "my-java-app_a1b2",
    "sourceId": "source-001",
    "sonarProjectKey": "myteam-my-java-app",
    "qualityGate": true
  }
}
```

---

### Step 7: 创建部署阶段

**请求**
```http
POST /devops/api/pipeline/stage/save
Content-Type: application/json

{
  "pipelineId": "pipe-123456",
  "stage": {
    "id": "stage-deploy",
    "name": "部署阶段",
    "nodeType": "custom-stage-node",
    "steps": [
      {
        "id": "step-deploy",
        "name": "部署步骤",
        "nodeType": "custom-step-node",
        "idx": 0,
        "driven": 0,
        "tasks": []
      }
    ]
  }
}
```

---

### Step 8: 添加 Docker 构建任务

**获取任务ID**
```http
GET /devops/api/pipeline/task/createTaskId?pipelineId=pipe-123456
```

**添加任务**
```http
POST /devops/api/pipeline/task/save
Content-Type: application/json

{
  "id": "task-docker-001",
  "pipelineId": "pipe-123456",
  "stageId": "stage-deploy",
  "taskData": {
    "taskCategory": "DockerBuild",
    "jobType": "DockerBuildAndUpload",
    "name": "镜像构建",
    "workPath": "my-java-app_a1b2",
    "sourceId": "source-001",
    "dockerfilePath": "Dockerfile",
    "imageName": "${PIPELINE_NAME}",
    "tag": "${BUILD_NUMBER}",
    "preDependTaskId": "task-maven-001"
  }
}
```

---

### Step 9: 执行流水线

**请求**
```http
POST /devops/api/pipeline/run
Content-Type: application/json

{
  "pipelineId": "pipe-123456",
  "branch": "master"
}
```

**响应**
```json
{
  "code": "200",
  "data": {
    "buildNumber": "1",
    "buildLogId": "log-001"
  }
}
```

---

## 最终流水线结构

```
Java应用构建流水线
│
├── 代码源: my-java-app (Gitee)
│
├── 阶段1: 构建阶段
│   └── 步骤: 构建步骤 (串行)
│       ├── 任务1: Maven构建
│       └── 任务2: 代码扫描
│
└── 阶段2: 部署阶段
    └── 步骤: 部署步骤 (串行)
        └── 任务: 镜像构建
```

---

## 完整数据结构（最终保存）

```json
{
  "pipeline": {
    "pipelineId": "pipe-123456",
    "name": "Java应用构建流水线",
    "spaceId": "space-001",
    "sources": [
      {
        "id": "source-001",
        "name": "my-java-app",
        "nodeType": "custom-source-node",
        "data": {
          "workPath": "my-java-app_a1b2",
          "sourceType": "code",
          "repoType": "GITEE",
          "repoUrl": "https://code.iflytek.com/myteam/my-java-app",
          "branch": "master"
        }
      }
    ],
    "stages": [
      {
        "id": "stage-build",
        "name": "构建阶段",
        "nodeType": "custom-stage-node",
        "steps": [
          {
            "id": "step-build",
            "name": "构建步骤",
            "nodeType": "custom-step-node",
            "idx": 0,
            "driven": 0,
            "tasks": [
              {
                "id": "task-maven-001",
                "name": "Maven构建",
                "nodeType": "custom-task-node",
                "idx": 0
              },
              {
                "id": "task-sonar-001",
                "name": "代码扫描",
                "nodeType": "custom-task-node",
                "idx": 1
              }
            ]
          }
        ]
      },
      {
        "id": "stage-deploy",
        "name": "部署阶段",
        "nodeType": "custom-stage-node",
        "steps": [
          {
            "id": "step-deploy",
            "name": "部署步骤",
            "nodeType": "custom-step-node",
            "idx": 0,
            "driven": 0,
            "tasks": [
              {
                "id": "task-docker-001",
                "name": "镜像构建",
                "nodeType": "custom-task-node",
                "idx": 0
              }
            ]
          }
        ]
      }
    ]
  },
  "taskDataList": [
    {
      "id": "task-maven-001",
      "data": {
        "taskCategory": "Build",
        "jobType": "MavenBuild",
        "name": "Maven构建",
        "workPath": "my-java-app_a1b2",
        "sourceId": "source-001",
        "jdkVersion": "JDK17",
        "mavenVersion": "Maven3.8.x",
        "script": "mvn -B clean package -Dmaven.test.skip=true",
        "uploadArtifact": true,
        "artifactPath": ["target/"]
      }
    },
    {
      "id": "task-sonar-001",
      "data": {
        "taskCategory": "CodeScanner",
        "jobType": "SonarQube",
        "name": "代码扫描",
        "workPath": "my-java-app_a1b2",
        "sourceId": "source-001"
      }
    },
    {
      "id": "task-docker-001",
      "data": {
        "taskCategory": "DockerBuild",
        "jobType": "DockerBuildAndUpload",
        "name": "镜像构建",
        "workPath": "my-java-app_a1b2",
        "sourceId": "source-001",
        "dockerfilePath": "Dockerfile",
        "imageName": "${PIPELINE_NAME}",
        "tag": "${BUILD_NUMBER}",
        "preDependTaskId": "task-maven-001"
      }
    }
  ]
}
```
