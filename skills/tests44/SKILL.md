---
name: cicd-pipeline-automation
description: 适用于在前进平台为**已部署工作负载**创建持续更新流水线（代码克隆 → 构建 → 镜像构建 → 镜像更新部署）。生成 Jenkinsfile 前必须完整阅读本 SKILL 内「流水线骨架」节模板，禁止凭记忆默写。
---

# 适用场景

- **前提：** 工作负载（Deployment / StatefulSet / DaemonSet 等）已在前进平台完成初始部署。
- **目标：** 在前进平台创建一条 **持续更新流水线**，实现 **代码克隆 → 依赖安装与代码构建 → 镜像构建 → 镜像更新部署** 的全流程自动化，每次触发后自动将新镜像滚动更新到已有工作负载。
- **不适用于：** 首次创建工作负载、基础设施初始化等场景。

---

# **过程中禁止自动推进需要用户确认的步骤**

# 前置条件

##  使用`auth_login`获取前进平台Token

- **何时调用 `auth_login`（仅此几种，禁止「每调一个工具就登录一次」）**
  - 当前对话/任务中 **尚无任何有效 token**（尚未登录过）。
  - 调用需鉴权工具时出现 **鉴权失败**：HTTP 401、返回体明示 token 无效/过期、或工具返回与登录态相关的失败（如「未授权」「token 过期」）。
  - 用户 **主动要求重新登录** 或 **更换前进平台账号**。
- **何时禁止再次调用 `auth_login`**
  - 同一会话内 **已成功取得 token** 且后续工具调用 **未出现** 上述鉴权失败时：**一律复用已有 token**，连续调用 `auth_list_projects`、`caas_registry_*`、`cicd_*`、`olympus_core_*` 等时 **不要** 在中间穿插 `auth_login`。
  - **禁止**以「保险起见」「每个阶段刷新一下」为由重复登录。
- 从 `auth_login` 返回中取 **访问 token**，仅在 **后续 MCP 工具入参** 中使用；**禁止**将 token 写入仓库、Jenkinsfile、可提交的文档或 **用户可见的回复正文**。
- 用户 **拒绝提供登录信息** 时：**不要** 调用需鉴权的创建类工具，说明无法代建。
- 用户输入信息不正常，重复3次向用户获取正确用户名/密码
- 禁止推测
- 禁止尝试使用git凭证登录

## 在前进平台已部署工作负载，目前目标是创建持续更新流水线

--- 

# 流水线创建过程，按顺序，不可跳步(强制)

## 确定租户：`auth_list_tenants`

- 调用 **`auth_list_tenants`** 列出可访问租户。
- **有多个租户禁止默认选择最相关租户**
- **多个租户** 必须展示获取信息并且用户确认后采用,**不得猜测**。

## 确定项目：`auth_list_projects`

- 在已选租户下调用 **`auth_list_projects`**（`tenantId` 等从租户选中项取值）。
- **多个项目** 时必须由用户明确选中，**不得猜测**。
- 必须展示获取信息并且用户确认后采用。

## **Jenkinsfile 占位符收集**（与 **代码克隆 → 依赖安装与代码构建 → 镜像构建 → 镜像部署** 四步对应；严格按此顺序执行）

### 分步停顿与用户确认（强制，全阶段适用）

- **每完成当前小步后必须停止**，等待用户**明确回复确认**后再进入下一步；不得在同一轮对话里自问自答式「代用户选定」或连续推进多步。
- 不得一次性和用户确认太多的信息
- **禁止**在用户尚未确认当前步时，把后续阶段的大段候选项**一次性堆叠**成「总表 / 长模板」让用户批量填写（例如：未选定 `${BUILD_LANG}` 就同时列出镜像仓库、命名空间、部署参数等）。
- **依赖安装与代码构建** 必须严格按 **Step 1 → 停等确认 → Step 2 → 停等确认 → Step 3 → 停等确认** 执行；**镜像构建**、**镜像部署** 各子步同理，**上一步未确认不得进入下一步**。
- 若用户希望加快：仍须**逐步展示当前步选项**并得到确认，**禁止**用「请一次性填完下面所有项」替代分步确认。

1. **代码克隆**：向用户收集信息，获取git地址，git用户名和密码，以及代码目录。禁止推测，用输入的值替换**`${GIT_URL}`**、**`${GIT_USERNAME}`**、**`${GIT_PASSWORD}`**、**`${GIT_BRANCH}`**；**`${REPO_SUBPATH}`** 见参数表。**信息经用户确认后**，再进入第 2 点。
2.  **依赖安装与代码构建**
### Step 1：获取构建语言

- 调用 **`cicd_list_code_build_languages`** 获取支持语言列表
- **必须展示完整列表，并由用户明确选择**
- **选定后停止**，待用户确认无误后，再进入 Step 2（**禁止**在未确认语言时展示构建工具或构建命令）

---

### Step 2：确认构建工具

根据用户选择的语言，**必须与用户确认**：

- node → `npm`
- java → `maven` / `gradle`（必须用户选择，禁止默认）
- go → `''`

填入：**`${BUILD_TOOL}`**。**确认后停止**，再进入 Step 3。

---

### Step 3：确认构建命令

- 构建命令来源：用户提供或确认
- 支持多行 shell
- **最终必须将完整命令写入 Jenkinsfile，禁止保留 `${BUILD_COMMANDS}`**
- **命令经用户确认后**，再进入第 3 点「镜像构建」。

---
3. **镜像构建**：
### Step 1：从前进平台获取制品仓库

- 调用 **`caas_registry_list_project_registries`**,
- **必须展示完整列表，并由用户选择**
- **强制格式（必须原样遵守）：** 选定后必须拼接并写入 `${DOCKER_SERVER}=registryId|服务地址`（示例：`f404d83fb8484e40|10.1.112.238:8443`）
- **强制校验：** `|` 左侧必须是 `registryId`，右侧必须是完整 `host:port`；**禁止**只填 `registryId`、只填地址、漏端口、交换左右顺序、加入空格或其他分隔符
- **唯一值处理：** 列表仅 1 个时可默认采用该项，但仍需在回复中明确展示最终 `${DOCKER_SERVER}` 完整值后再继续下一步
### Step 2：获取镜像仓库

- 调用 **`caas_registry_list_project_repo_projects`**
- **必须展示仓库列表，并由用户选择**
### Step 3：确认基础参数

必须逐项与用户确认：

- `${DOCKERFILE_PATH}`（dockerfile地址）
- `${PRODUCT_NAME}`（镜像名称，可建议默认值，但必须确认）
- `${IMAGE_TAG}`（默认 `latest`，但必须确认）


4. **镜像部署**
### Step 1：获取项目下集群与命名空间

- 调用 **`olympus_core_list_namespaces_group_by_cluster`**
- **必须展示 cluster + namespace 列表，并由用户选择**
- 填入格式：${DEPLOY_CLUSTER_NS} = 集群名:命名空间
### Step 2：确认部署参数

必须逐项与用户确认：

- `${DEPLOY_TYPE}`（deployment / statefulset / daemonset 等）
- `${DEPLOY_APP_NAME}`

按需与用户确认，主要和客户确认是否使用默认值，用户有需要再进行修改
- `${DEPLOY_CONTAINER_NAME}`（更新的具体容器名称，可以默认值，第一个）
- `${IMAGE_SOURCE}` （镜像来源默认是1来自上游构建步骤，可选2，来自用户提供）
- `${IMAGE_URL}`（根据需要提供）

- 禁止自动推断应用名或容器名
- 禁止自动选择 cluster 或 namespace


## 平台侧元数据收集

在完成上面的 Jenkinsfile 占位符收集后，在已选租户/项目下使用 `cicd_list_environments`（资源池 `envId`）、`cicd_list_tags`（标签）、`cicd_get_job_id`（`jobId`）等工具获取平台创建参数。

## 创建流水线

当 Jenkinsfile 占位符与平台元数据均确认完成后，将完整 Jenkinsfile 文本与「平台侧元数据收集」得到的 `envId`、标签 `labels`、`jobId`、`jobName` 一并传入 `cicd_create_pipeline`（字段以工具 schema 为准）。

## 约束（强制）

- **构建收集与后续占位符收集**：遵守上文 **「分步停顿与用户确认」**；**禁止**跳过中间确认、禁止用「一次性填表」代替逐步停等。
- **禁止**猜测须由用户确认的信息（租户、项目、制品、镜像仓库、部署目标等）。
- **鉴权与会话**：遵守上文 **「获取 Token 与 Token 复用」**；**对用户表述**：遵守 **「对用户可见输出」**。
- **不要去项目中找凭据，token 失效或鉴权失败时再请用户提供前进平台账号密码并重新 `auth_login`**
- **禁止**仅凭对话记忆、片段回忆、「默写」Jenkinsfile
- **用户没有提供完整的信息，不能开始创建Jenkinsfile**
- 用户信息不完整时，禁止生成 Jenkinsfile
- **禁止**仅凭对话记忆、片段回忆、「默写」Jenkinsfile
- **禁止**骨架中的前进封装步骤。
- **禁止**修改 `${env.xxx}` 变量
- **禁止**修改agent中的内容
- **原则：** MCP工具 能列出候选的须 **展示并由用户选定**；未确认项保留 **`${XXX}`** 或继续追问。占位符含义见 **「参数替换规则」** 表
- **Jenkinsfile 交付形态（强制）：** 业务占位符（`${GIT_URL}`、`${BUILD_LANG}`、`${DOCKER_SERVER}` 等）必须在 **`easyGitClone`、`containerCodeBuild`、`easyImageBuild`、`workloadImageUpdate` 各步骤的参数字段** 做 **直接值替换**（字面量或 Git 密码的凭据引用）。**禁止**用 `environment { }`、`parameters { }` 或 `"${params.XXX}"` 再包一层转发；骨架里的 `"${GIT_…}"` 仅表示 **生成前** 的占位，**不得**把最终文件写成「先 env 再引用同名变量」的形式。
- **禁止**过程中猜测
- **禁止**本地clone代码
- **禁止**对骨架进行修改，只需要根据用户输入信息修改占位符参数


## 流水线骨架

**agent 块强制约束（最高优先级）：** `agent { ... }` 块内的全部内容 **必须与下方骨架完全一致，一字不改**；**禁止**增删、替换、重排其中任何字段、镜像变量、资源配置或 volumeMounts/volumes 条目。

**占位符规则：** 只替换 **`${GIT_URL}`**、**`${IMAGE_TAG}`** 这类 **非 `env.`** 的 **`${XXX}`**；**不要**改动 **`${env.xxx}`**（Jenkins 运行时环境）。禁止在模板中提交真实密钥。

**生成结果写法：** 上述 **`${XXX}`** 仅在 **产出 Jenkinsfile 之前** 作为待填标记；写入平台的 Jenkinsfile 里应变为 **各步骤参数上的直接字面量**（与下文「完整案例」一致），**不要**增加 `environment` / `parameters` 块来承载这些业务配置。

```groovy
pipeline {
  agent {
    kubernetes {
      cloud "${env.runCluster}"
      defaultContainer 'maven'
      yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: jnlp
    image: ${env.inboundImage}
  - name: maven
    imagePullPolicy: Always
    image: ${env.agentImage}
    command:
    - sleep
    args:
    - 99d
    resources:
      requests:
        cpu: "100m"
        memory: "100Mi"
      limits:
        cpu: "4000m"
        memory: "8192Mi"
    volumeMounts:
      - mountPath: "/var/run/docker.sock"
        name: "volume-1"
        readOnly: false
      - mountPath: /root/.m2/settings.xml
        name: config
        subPath: settings.xml
  volumes:
    - name: "volume-1"
      hostPath:
        path: "/var/run/docker.sock"
    - name: config
      configMap:
        name: jenkins-agent-config
        items:
          - key: settings.xml
            path: settings.xml
    - name: buildah-conf
      configMap:
        name: buildah-conf
        items:
          - key: registries.conf
            path: registries.conf
'''
    }
  }
  stages {
    stage('代码克隆') {
      steps {
        easyGitClone(
          stepName: '代码克隆',
          gitUrl: "${GIT_URL}",
          gitUserName: "${GIT_USERNAME}",
          gitPassword: "${GIT_PASSWORD}",
          branch: "${GIT_BRANCH}",
          path: "${REPO_SUBPATH}"
        )
      }
    }
    stage('依赖安装与代码构建') {
      steps {
        containerCodeBuild(
          stepName: '依赖安装与代码构建',
          language: "${BUILD_LANG}",
          buildTool: "${BUILD_TOOL}",
          command: '''${BUILD_COMMANDS}''',
          file_setting: '',
          proxy: ''
        )
      }
    }
    stage('镜像构建') {
      steps {
        easyImageBuild(
          stepName: '镜像构建',
          dockerServer: "${DOCKER_SERVER}",
          dockerRepository: "${DOCKER_REPOSITORY}",
          imageSecret: '',
          dockerfile: "${DOCKERFILE_PATH}",
          productName: "${PRODUCT_NAME}",
          params_tag: "${IMAGE_TAG}"
        )
      }
    }
    stage('镜像部署') {
      steps {
        workloadImageUpdate(
          stepName: '容器应用镜像更新',
          clusterNamespace: "${DEPLOY_CLUSTER_NS}",
          type: "${DEPLOY_TYPE}",
          appName: "${DEPLOY_APP_NAME}",
          containerName: "${DEPLOY_CONTAINER_NAME}",
          imageSource: "${IMAGE_SOURCE}",
          imageUrl: "${IMAGE_URL}"
        )
      }
    }
  }
}
```

## 完整案例：Kubernetes Agent + Node 18 / npm（含 dist 与 `.dockerignore`）

与上文骨架 **阶段一致**（代码克隆 → 构建 → 镜像 → 部署）。以下为 **结构示例**：Git 凭据须用 Jenkins 凭据 ID 或平台约定方式管理，**禁止**在仓库中提交明文密码。

```groovy
pipeline {
  agent {
    kubernetes {
      cloud "${env.runCluster}"
      defaultContainer 'maven'
      yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: jnlp
    image: ${env.inboundImage}
  - name: maven
    imagePullPolicy: Always
    image: ${env.agentImage}
    command:
    - sleep
    args:
    - 99d
    resources:
      requests:
        cpu: "100m"
        memory: "100Mi"
      limits:
        cpu: "4000m"
        memory: "8192Mi"
    volumeMounts:
      - mountPath: "/var/run/docker.sock"
        name: "volume-1"
        readOnly: false
      - mountPath: /root/.m2/settings.xml
        name: config
        subPath: settings.xml
  volumes:
    - hostPath:
        path: "/var/run/docker.sock"
      name: "volume-1"
    - configMap:
        items:
        - key: settings.xml
          path: settings.xml
        name: jenkins-agent-config
      name: config
    - configMap:
        items:
        - key: registries.conf
          path: registries.conf
        name: buildah-conf
      name: buildah-conf
'''
    }

  }
  stages {
    stage('代码克隆') {
      steps {
        easyGitClone(stepName: '代码克隆', gitUrl: 'https://example.com/org/repo.git', gitUserName: 'example-user', gitPassword: '<Jenkins 凭据，勿明文提交>', branch: 'main', path: '')
      }
    }

    stage('依赖安装与代码构建') {
      steps {
        containerCodeBuild(stepName: '依赖安装与代码构建', language: 'node18', buildTool: 'npm', command: '''npm install & npm build
''', file_setting: '', proxy: '')
      }
    }

    stage('镜像构建') {
      steps {
        easyImageBuild(stepName: '镜像构建', dockerServer: 'registryId|10.0.0.1:8443', dockerRepository: 'your-library', imageSecret: '', dockerfile: 'Dockerfile', productName: 'your-product', params_tag: 'latest')
      }
    }

    stage('镜像部署') {
      steps {
        workloadImageUpdate(stepName: '容器应用镜像更新', clusterNamespace: 'cluster:namespace', type: 'deployment', appName: 'app-name', containerName: '', imageSource: '1', imageUrl: '')
      }
    }

  }
}
```

## 参数替换规则

| 参数 | Typical use |
|--------|----------------|
| `${GIT_URL}` | 仓库地址 |
| `${GIT_USERNAME}` | Git 用户名 |
| `${GIT_PASSWORD}` | Git 密码占位（生成时应改为凭据引用） |
| `${GIT_BRANCH}` | 分支 |
| `${REPO_SUBPATH}` | 克隆后相对子目录，空则填 `''` |
| `${BUILD_LANG}` | 使用cicd_list_code_build_languages工具获取支持的语言，展示value让用户选择，禁止猜测和进一步扩展 |
| `${BUILD_TOOL}` | 如 `npm` / `maven` / `gradle` |
| `${BUILD_COMMANDS}` | 构建命令 |
| `${DOCKER_SERVER}` | **强制值格式** `registryId|host:port`（示例：`f404d83fb8484e40|10.1.112.238:8443`）；必须通过 `caas_registry_list_project_registries` 获取并由用户确认；禁止只填一侧或改用其他分隔符 |
| `${DOCKER_REPOSITORY}` | 镜像仓库名称，使用caas_registry_list_project_repo_projects工具根据制品服务id获取镜像仓库名称 |
| `${DOCKERFILE_PATH}` | Dockerfile 路径 |
| `${PRODUCT_NAME}` | 镜像名称,默认可以用仓库名称或者流水线名称 |
| `${IMAGE_TAG}` | 镜像 tag ，默认latest|
| `${DEPLOY_CLUSTER_NS}` |使用olympus_core_list_namespaces_group_by_cluster获取集群和namespace集群，格式`cluster:namespace`|
| `${DEPLOY_TYPE}` | `deployment` / `statefulset` /  `daemonset`等 |
| `${DEPLOY_APP_NAME}` | 需要更新的工作负载名 |
| `${DEPLOY_CONTAINER_NAME}` | 可选，多容器时指定容器名，默认 `''` |
| `${IMAGE_SOURCE}` | `1`表示从构建步骤来，`2`表示需要提供镜像地址,默认`1` |
| `${IMAGE_URL}` | `IMAGE_SOURCE` 为2时需要填写，默认 `''` |

## `command` 与 `${BUILD_COMMANDS}`

Groovy 单引号三引号字符串 **不会** 对 `${BUILD_COMMANDS}` 做运行时插值。`${BUILD_COMMANDS}` 仅作为 **生成/填充前的标记**：自动化或人工应用本模板时，应把 **`${BUILD_COMMANDS}` 整段替换为最终多行 shell**，提交到 Jenkins 的 Jenkinsfile 里不应再保留字面量 `${BUILD_COMMANDS}`。
