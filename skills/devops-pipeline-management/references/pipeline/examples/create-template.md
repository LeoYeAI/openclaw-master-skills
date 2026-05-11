# 创建流水线模板示例

本文档展示如何通过 OpenAPI 创建一个可复用的流水线模板。

---

## 场景描述

创建一个 Java Maven 构建模板，包含：
- Maven 构建
- SonarQube 扫描
- Docker 镜像构建

---

## 请求示例

```http
POST /devops/api/pipeline/template/savePipTemplate
Content-Type: application/json
Authorization: Bearer {token}

{
  "pipelineTemplateName": "Java Maven 标准构建模板",
  "pipelineTemplateLanguage": "java",
  "description": "适用于 Java Maven 项目的标准 CI/CD 流程",
  "status": 1,
  "pipelineTemplateVisibleRangeType": "division",
  "divisionId": "org-001",
  "pipelineConfig": {
    "name": "Maven构建流水线",
    "aliasId": "",
    "label": ["Java", "Maven"],
    "sources": [],
    "stages": [
      {
        "id": "stage-build",
        "name": "构建",
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
                "id": "task-maven",
                "name": "Maven构建",
                "nodeType": "custom-task-node",
                "idx": 0
              },
              {
                "id": "task-sonar",
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
        "name": "部署",
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
                "id": "task-docker",
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
      "id": "task-maven",
      "data": {
        "taskCategory": "Build",
        "jobType": "MavenBuild",
        "name": "Maven构建",
        "workPath": "",
        "sourceId": "",
        "jdkVersion": "JDK17",
        "mavenVersion": "Maven3.8.x",
        "selectedMavenRepos": [],
        "script": "mvn -B clean package -Dmaven.test.skip=true",
        "uploadArtifact": true,
        "artifactPath": ["target/"],
        "artifactSuffix": ["jar"],
        "artifactCompress": true,
        "compressType": "TAR(.tgz)",
        "packagedName": "Artifacts_${PIPELINE_LOG_ID}",
        "idInTemplate": "task-maven",
        "dependencies": []
      }
    },
    {
      "id": "task-sonar",
      "data": {
        "taskCategory": "CodeScanner",
        "jobType": "SonarQube",
        "name": "代码扫描",
        "workPath": "",
        "sourceId": "",
        "idInTemplate": "task-sonar",
        "dependencies": ["task-maven"]
      }
    },
    {
      "id": "task-docker",
      "data": {
        "taskCategory": "DockerBuild",
        "jobType": "DockerBuildAndUpload",
        "name": "镜像构建",
        "workPath": "",
        "sourceId": "",
        "dockerfilePath": "Dockerfile",
        "imageName": "${PIPELINE_NAME}",
        "tag": "${BUILD_NUMBER}",
        "preDependTaskId": "task-maven",
        "idInTemplate": "task-docker",
        "dependencies": []
      }
    }
  ]
}
```

---

## 响应

```json
{
  "code": "200",
  "data": {
    "pipelineTemplateId": "template-001"
  }
}
```

---

## 模板特点

### 与流水线的区别

| 字段 | 模板 | 流水线 |
|-----|------|--------|
| `sources` | 空 | 必须配置 |
| `workPath` | 空 | 必须填写 |
| `sourceId` | 空 | 必须关联 |
| `idInTemplate` | 有值 | 可能为空 |

### 使用模板创建流水线

1. 获取模板详情
2. 复制 `pipelineConfig` 和 `taskDataList`
3. 生成新的 ID（stageId, stepId, taskId）
4. 清空 `idInTemplate`、`sourceId`、`workPath`
5. 用户配置代码源
6. 保存为新流水线

---

## 最小模板示例（仅构建）

```json
{
  "pipelineTemplateName": "简单Maven构建",
  "pipelineTemplateLanguage": "java",
  "pipelineTemplateVisibleRangeType": "personal",
  "pipelineConfig": {
    "name": "Maven构建",
    "sources": [],
    "stages": [
      {
        "id": "stage-1",
        "name": "构建",
        "nodeType": "custom-stage-node",
        "steps": [
          {
            "id": "step-1",
            "name": "构建",
            "nodeType": "custom-step-node",
            "idx": 0,
            "driven": 0,
            "tasks": [
              {
                "id": "task-1",
                "name": "Maven构建",
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
      "id": "task-1",
      "data": {
        "taskCategory": "Build",
        "jobType": "MavenBuild",
        "name": "Maven构建",
        "idInTemplate": "task-1"
      }
    }
  ]
}
```
