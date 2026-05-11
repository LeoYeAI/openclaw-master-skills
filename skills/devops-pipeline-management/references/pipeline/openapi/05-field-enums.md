# 字段枚举值汇总

本文档汇总所有任务配置中的枚举字段可选值，方便 Skill 开发时参考。

---

## 通用枚举

### sourceType (源类型)

| 值 | 说明 |
|---|------|
| `code` | 代码源（Git仓库） |
| `package` | 制品源 |

### repoType (仓库类型)

| 值 | 适用 sourceType | 说明 |
|---|----------------|------|
| `GITEE` | code | Gitee 平台 |
| `GITLAB` | code | GitLab 平台 |
| `FLYCODE` | code | 质效Code平台 |
| `IPACKAGE` | package | iPackage 制品仓库 |

### refsType (引用类型)

| 值 | 说明 |
|---|------|
| `BRANCH` | 分支 |
| `TAG` | 标签 |
| `COMMIT` | 提交 |

### packageType (制品类型)

| 值 | 说明 |
|---|------|
| `docker` | 镜像制品 |
| `normal` | 普通制品 |

### taskCategory (任务分类)

| 值 | 说明 |
|---|------|
| `Build` | 编译构建 |
| `DockerBuild` | 镜像构建 |
| `Deploy` | 部署 |
| `CodeScanner` | 代码扫描 |
| `CodeCover` | 测试/覆盖率 |
| `Code` | 代码操作 |
| `Normal` | 通用 |

---

## 构建环境枚举

### buildImageModel (构建环境类型)

| 值 | 说明 |
|---|------|
| `default` | 默认环境 |
| `custom` | 自定义镜像 |

### JDK 版本

| 值 | 说明 |
|---|------|
| `JDK1.8` | JDK 8 |
| `JDK11` | JDK 11 |
| `JDK17` | JDK 17 (推荐) |
| `JDK21` | JDK 21 |

### Maven 版本

| 值 | 说明 |
|---|------|
| `Maven3.3.9` | Maven 3.3.9 |
| `Maven3.5.4` | Maven 3.5.4 |
| `Maven3.6.3` | Maven 3.6.3 |
| `Maven3.8.x` | Maven 3.8.x |

### Node.js 版本

| 值 | 说明 |
|---|------|
| `Node14` | Node.js 14 |
| `Node16` | Node.js 16 |
| `Node18` | Node.js 18 (推荐) |
| `Node20` | Node.js 20 |

### Python 版本

| 值 | 说明 |
|---|------|
| `Python3.8` | Python 3.8 |
| `Python3.9` | Python 3.9 |
| `Python3.10` | Python 3.10 |
| `Python3.11` | Python 3.11 |

### Go 版本

| 值 | 说明 |
|---|------|
| `Go1.18` | Go 1.18 |
| `Go1.19` | Go 1.19 |
| `Go1.20` | Go 1.20 |
| `Go1.21` | Go 1.21 |

---

## 制品相关枚举

### artifactSuffix (制品类型)

| 值 | 说明 |
|---|------|
| `jar` | Java 归档 |
| `war` | Web 归档 |
| `zip` | ZIP 压缩包 |
| `tar` | TAR 压缩包 |
| `tgz` | TAR.GZ 压缩包 |

### compressType (压缩格式)

| 值 | 说明 |
|---|------|
| `TAR(.tgz)` | TGZ 格式 |
| `TAR(.tar.gz)` | TAR.GZ 格式 |
| `ZIP` | ZIP 格式 |

---

## 部署相关枚举

### deployType (部署类型)

| 值 | 说明 |
|---|------|
| `artifact` | 制品部署 |
| `script` | 脚本部署 |

### multiPlatform (多平台构建)

| 值 | 说明 |
|---|------|
| `""` | 不启用多平台 |
| `linux/amd64` | AMD64 架构 |
| `linux/arm64` | ARM64 架构 |

---

## 模板相关枚举

### pipelineTemplateVisibleRangeType (可见范围)

| 值 | 说明 |
|---|------|
| `personal` | 个人可见 |
| `division` | 部门可见 |
| `space` | 空间可见 |
| `system` | 系统模板 |

### pipelineTemplateLanguage (模板语言)

| 值 | 说明 |
|---|------|
| `java` | Java |
| `nodejs` | Node.js |
| `python` | Python |
| `go` | Go |
| `cpp` | C++ |
| `general` | 通用 |

### status (状态)

| 值 | 说明 |
|---|------|
| `0` | 禁用 |
| `1` | 启用 |

---

## 触发事件枚举

### GITEE webhook.event

| 值 | 说明 |
|---|------|
| `pushEvents` | 代码推送 |
| `createBranch` | 创建分支 |
| `createTag` | 创建标签 |
| `pullRequestMerge` | PR 合并 |
| `pullRequestOpen` | PR 开启 |
| `pullRequestUpdate` | PR 更新 |

### GITLAB webhook.event

| 值 | 说明 |
|---|------|
| `pushEvents` | 代码推送 |
| `createTag` | 创建标签 |
| `mergeRequest` | MR 事件 |

---

## 画布状态枚举

### GRAPH_STATUS

| 值 | 说明 |
|---|------|
| `detail` | 详情模式 |
| `editing` | 编辑模式 |
| `onlyView` | 只读模式 |
| `running` | 运行中 |
| `pending` | 等待中 |
| `cancel` | 已取消 |

### driven (执行方式)

| 值 | 说明 |
|---|------|
| `0` | 串行执行 |
| `1` | 并行执行 |

---

## 动态参数

在任务配置中可使用以下动态参数：

| 参数 | 说明 |
|-----|------|
| `${PIPELINE_NAME}` | 流水线名称 |
| `${BUILD_NUMBER}` | 构建号 |
| `${PIPELINE_LOG_ID}` | 流水线执行日志ID |
| `${BRANCH}` | 当前分支 |
| `${COMMIT_ID}` | 提交ID |

**示例:**
```json
{
  "packagedName": "Artifacts_${PIPELINE_LOG_ID}",
  "imageName": "${PIPELINE_NAME}",
  "tag": "${BUILD_NUMBER}"
}
```
