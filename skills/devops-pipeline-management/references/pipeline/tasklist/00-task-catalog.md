# 流水线任务原子能力目录

本文档汇总了质效平台4.0中所有流水线任务原子能力的配置信息。

> ⚠️ **注意**：各任务类型的详细配置字段请参考 [../schemas/all-tasks/](../schemas/all-tasks/) 目录下的 Schema 文件。

## 快速导航

| 场景 | 推荐文档 |
|------|---------|
| 配置校验规则 | [03-validate-rules.md](./03-validate-rules.md) |
| 通用字段说明 | [03-common-fields.md](./03-common-fields.md) |

---

## 任务类型索引

### 构建类任务

| 任务类型 | jobType | 说明 |
|---------|---------|------|
| 执行命令 | `OrderAction` | 通用Shell命令执行任务 |
| Maven构建 | `MavenBuild` | Java Maven项目构建 |
| Gradle构建 | `GradleBuild` | Gradle项目构建 |
| Node.js构建 | `NpmBuild` | Node.js项目构建 |
| Python构建 | `PythonBuild` | Python项目构建 |
| Go构建 | `GoBuild` | Go项目构建 |
| C++构建 | `CppBuild` | C++项目构建 |
| 渠道构建 | `ChannelBuild` | Android多渠道包批量构建 |

### Docker/镜像构建类任务

| 任务类型 | jobType | 说明 |
|---------|---------|------|
| Docker构建并上传 | `DockerBuildAndUpload` | 构建Docker镜像并上传到仓库 |
| Maven镜像构建 | `MavenDockerBuild` | Maven + Docker组合构建 |
| Node.js镜像构建 | `NpmDockerBuild` | Node.js + Docker组合构建 |
| Python镜像构建 | `PythonDockerBuild` | Python + Docker组合构建 |
| Go镜像构建 | `GoDockerBuild` | Go + Docker组合构建 |
| Gradle镜像构建 | `GradleDockerBuild` | Gradle + Docker组合构建 |
| C++镜像构建 | `CppDockerBuild` | C++ + Docker组合构建 |

### 部署类任务

| 任务类型 | jobType | 说明 |
|---------|---------|------|
| 主机部署 | `HostDeploy` | 传统主机部署 |
| Docker部署 | `HostDockerDeploy` | 主机Docker部署 |
| SAE应用发布 | `Sae` | SAE首次创建应用 |
| SAE镜像更新 | `SaeImageUpdate` | SAE容器镜像更新部署 |
| SAE Helm应用更新 | `SaeHelm` | SAE Helm Chart部署 |
| Yaml部署 | `YamlDeploy` | 通用YAML部署 |
| Helm应用部署 | `CloudHelmDeploy` | 云端Helm部署 |

### 代码扫描类任务

| 任务类型 | jobType | 说明 |
|---------|---------|------|
| SonarQube扫描 | `SonarQube` | SonarQube代码质量扫描 |
| 源码扫描 | `ScaCodeScan` | SCA组件依赖漏洞扫描 |
| 代码安全扫描 | `SecCodeScan` | 源代码安全扫描 |
| 二进制扫描 | `ScaBinaryScan` | 二进制制品安全扫描 |

### 代码操作类任务

| 任务类型 | jobType | 说明 |
|---------|---------|------|
| 创建Git标签 | `CreateGitTag` | 创建Git版本标签 |
| 发起合并请求 | `GitMerge` | 创建代码合并请求 |

### 测试/覆盖率类任务

| 任务类型 | jobType | 说明 |
|---------|---------|------|
| 代码覆盖度插桩 | `CodeCoverInst` | Jacoco插桩 |
| 代码覆盖度收集 | `CodeCoverCollect` | 覆盖率数据收集 |
| 执行计划 | `ExcutePlan` | 触发执行计划 |

### 通用/分发类任务

| 任务类型 | jobType | 说明 |
|---------|---------|------|
| 人工审核 | `ManualReview` | 人工审批确认任务 |
| 制品分发 | `ProductDistribution` | 镜像分发到多个仓库 |
| 制作Helm Chart上传 | `UploadChart` | Helm Chart制品上传 |
| 制品晋级 | `ArtifactPromotion` | 制品从build库晋级到release库 |

---

## 通用字段说明

所有任务类型都包含以下通用字段：

| 字段名 | 类型 | 说明 | 必填 |
|-------|------|------|------|
| `name` | string | 任务名称 | 是 |
| `buildImageModel` | string | 构建环境类型 (`default`/`custom`) | 是 |
| `executeImageId` | string | 执行镜像ID | 条件必填 |
| `workPath` | string | 工作目录（代码源根目录） | 条件必填 |
| `sourceId` | string | 代码源ID | 否 |
| `jobType` | string | 任务类型标识 | 是 |
| `taskCategory` | string | 任务分类 (`Build`/`Deploy`/`CodeScanner`/`Normal`) | 是 |
| `dependencies` | array | 前序任务依赖 | 否 |
| `idInTemplate` | string | 模板中任务ID | 否 |

详细说明请参考 [03-common-fields.md](./03-common-fields.md)

---

## 任务分类 (taskCategory)

| 值 | 说明 |
|---|------|
| `Build` | 编译构建类任务 |
| `DockerBuild` | 镜像构建类任务 |
| `Deploy` | 部署类任务 |
| `CodeScanner` | 代码扫描类任务 |
| `CodeCover` | 测试/覆盖率类任务 |
| `Code` | 代码操作类任务 |
| `Normal` | 通用类任务 |

---

## jobType 完整列表

| jobType | taskCategory | 说明 |
|---------|-------------|------|
| `OrderAction` | Build | 通用Shell命令执行任务 |
| `MavenBuild` | Build | Java Maven项目构建 |
| `GradleBuild` | Build | Gradle项目构建 |
| `NpmBuild` | Build | Node.js项目构建 |
| `PythonBuild` | Build | Python项目构建 |
| `GoBuild` | Build | Go项目构建 |
| `CppBuild` | Build | C++项目构建 |
| `ChannelBuild` | Build | Android多渠道包批量构建 |
| `DockerBuildAndUpload` | DockerBuild | 构建Docker镜像并上传到仓库 |
| `MavenDockerBuild` | DockerBuild | Maven + Docker组合构建 |
| `NpmDockerBuild` | DockerBuild | Node.js + Docker组合构建 |
| `PythonDockerBuild` | DockerBuild | Python + Docker组合构建 |
| `GoDockerBuild` | DockerBuild | Go + Docker组合构建 |
| `GradleDockerBuild` | DockerBuild | Gradle + Docker组合构建 |
| `CppDockerBuild` | DockerBuild | C++ + Docker组合构建 |
| `HostDeploy` | Deploy | 传统主机部署 |
| `HostDockerDeploy` | Deploy | 主机Docker部署 |
| `Sae` | Deploy | SAE首次创建应用 |
| `SaeImageUpdate` | Deploy | SAE容器镜像更新部署 |
| `SaeHelm` | Deploy | SAE Helm Chart部署 |
| `YamlDeploy` | Deploy | 通用YAML部署 |
| `CloudHelmDeploy` | Deploy | 云端Helm部署 |
| `SonarQube` | CodeScanner | SonarQube代码质量扫描 |
| `ScaCodeScan` | CodeScanner | SCA组件依赖漏洞扫描 |
| `SecCodeScan` | CodeScanner | 源代码安全扫描 |
| `ScaBinaryScan` | CodeScanner | 二进制制品安全扫描 |
| `CreateGitTag` | Code | 创建Git版本标签 |
| `GitMerge` | Code | 创建代码合并请求 |
| `CodeCoverInst` | CodeCover | Jacoco插桩 |
| `CodeCoverCollect` | CodeCover | 覆盖率数据收集 |
| `ExcutePlan` | CodeCover | 触发执行计划 |
| `ManualReview` | Normal | 人工审批确认任务 |
| `ProductDistribution` | Normal | 镜像分发到多个仓库 |
| `UploadChart` | Normal | Helm Chart制品上传 |
| `ArtifactPromotion` | Normal | 制品从build库晋级到release库 |
