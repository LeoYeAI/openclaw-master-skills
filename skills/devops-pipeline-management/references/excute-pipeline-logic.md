# ExcutePipeline 执行配置逻辑

## 概述

`ExcutePipeline.vue` 是流水线执行配置弹窗组件，负责：
1. 加载代码源和制品源的分支/标签/版本列表
2. 回填最近一次执行的配置
3. 组装执行参数并提交流水线执行

## 数据源结构

### 流水线配置数据来源

```
props.flowData?.pipeline?.sources
```

### 源类型

| 类型 | sourceType | 说明 |
|------|------------|------|
| 代码源 | `code` | Git 仓库（GitLab/GitHub/Gitee/Git/SVN） |
| 制品源 | `package` | Docker 镜像 / 普通制品 |

### 数据结构

```typescript
interface ISource {
  id: string
  name: string
  data: {
    sourceType: 'code' | 'package'
    // 代码源字段
    repoType: string      // 仓库类型: GITLAB/GITHUB/GITEE/GIT/SVN
    refsType: string      // 引用类型: BRANCH/TAG
    repoUrl: string       // 仓库地址
    branch: string        // 分支/标签名
    workPath: string      // 工作路径
    // 制品源字段
    packageType: 'DOCKER' | 'NORMAL'
    imageName: string     // 镜像名
    defaultTag: string    // 标签/版本
    fullPath: string      // 完整路径
    normalAddress: string // 普通制品地址
  }
}
```

## 代码源初始化流程

### 入口函数：`openDialog`

```typescript
const openDialog = async (params) => {
  const { useIn = 'edit' } = params || {}
  showDialog.value = true
  useInRef.value = useIn

  // 加载上次执行配置
  runConfig.value.autoFillRunConfig = JSON.parse(
    props.flowData?.pipeline?.latestPipWorkVO?.pipelineParams || '{}'
  )?.pipeline?.autoFillRunConfig

  // 初始化分支/标签列表
  await doGetRepoBranchList({
    currentPage: 1,
    pageSize: 20
  })
}
```

### 核心函数：`doGetRepoBranchList`

#### 1. 构建查询参数 (`getBranchVersion`)

```typescript
const getBranchVersion = () => {
  // 筛选代码源
  const sources = props.flowData?.pipeline?.sources
    ?.filter((item) => item.data.sourceType === 'code')

  // 筛选制品源
  const packages = props.flowData?.pipeline?.sources
    ?.filter((item) => item.data.sourceType === 'package')

  // 构建代码源参数
  const sourceParams = sources?.map((source: ISource) => {
    const { repoType, refsType, repoUrl, workPath } = source.data || {}
    return {
      sourceType: 'code',
      refsType,
      repoType,
      repoUrl,
      workPath
    }
  })

  // 构建制品源参数
  const packageParams = packages?.map((item: any) => {
    const { repoType, imageName, workPath, packageType, normalAddress, normalArtifactName } = item.data || {}
    return {
      sourceType: 'package',
      repoType,
      imageName,
      workPath,
      packageType,
      normalAddress,
      normalArtifactName
    }
  })

  return {
    pipelineId: props.flowData?.pipeline?.pipelineId,
    codeSourceParams: sourceParams,
    artifactParams: packageParams,
    sources  // 仅返回代码源
  }
}
```

#### 2. 获取最近执行配置

```typescript
// 调用 API 获取最近一次执行的分支/标签/版本
// 前端函数: queryLastestSelectedValueByField
// API路径: POST /rest/openapi/pipeline/queryLastestSelectedValueByField
const resVersion = await queryLastestSelectedValueByField({
  pipelineId,
  codeSourceParams,
  artifactParams
})
```

#### 3. 回填制品源数据

```typescript
if (resVersion.code === '200' && resVersion.data) {
  props.flowData?.pipeline?.sources.forEach((source: any) => {
    if (source?.data?.sourceType === 'package') {
      // 查找对应制品源
      const artifactResultItem = resVersion.data?.artifactResult?.find(
        (item: any) => item.artifactParam.workPath === source.data?.workPath
      )

      if (artifactResultItem && artifactResultItem?.lastestArtifactVersion) {
        // 回填版本号
        source.data.defaultTag = artifactResultItem?.lastestArtifactVersion

        // NORMAL 类型制品需要替换路径中的版本号
        if (source.data.packageType === PACKAGE_TYPE_ENUM.NORMAL) {
          getChangeFullPath(source.data, 'fullPath', source.data.defaultTag)
          getChangeFullPath(source.data, 'normalAddress', source.data.defaultTag)
          getChangeFullPath(source.data, 'ipackagePath', source.data.defaultTag)
        }
      }
    }
  })
}
```

#### 4. 回填代码源数据

```typescript
sources.forEach((source: any) => {
  if (source?.data?.sourceType === 'code') {
    // 查找对应代码源
    const codeSourceResultItem = resVersion.data?.codeSourceResult?.find((item: any) =>
      item.codeSourceParam.repoType === source.data.repoType &&
      item.codeSourceParam.refsType === source.data.refsType &&
      item.codeSourceParam.repoUrl === source.data.repoUrl &&
      item.codeSourceParam.workPath === source.data.workPath
    )

    if (codeSourceResultItem && codeSourceResultItem?.branchOrTag) {
      // 回填分支/标签
      source.data.branch = codeSourceResultItem?.branchOrTag
    }
    if (codeSourceResultItem && codeSourceResultItem?.lastestCodeSourceParam?.refsType) {
      // 回填引用类型
      source.data.refsType = codeSourceResultItem?.lastestCodeSourceParam?.refsType
    }
  }
})
```

#### 5. 获取分支/标签列表

```typescript
// 构建查询参数列表
const dataList = sources.map((source: ISource) => {
  const { repoType, refsType, repoUrl, branch } = source.data || {}
  return {
    refsType,
    repoType,
    repoUrl,
    search: branch,  // 用于搜索
    currentPage,
    pageSize
  }
})

// 批量获取分支和标签列表
// 前端函数: getRepoBranchAndTagList
// API路径: POST /rest/openapi/pipeline/getRepoBranchAndTagList
const res = await getRepoBranchAndTagList(dataList)
```

#### 6. 处理每个源的分支信息

```typescript
const promises = res.data?.map(async (item: any, index: number) => {
  const sourceItem = sources[index]
  if (!sourceItem) return null

  const { refsType, repoType, repoUrl, branch: refsTypeValue } = sourceItem.data || {}

  // 获取提交信息（标签类型）
  // 前端函数: queryCommitDetail
  // API路径: POST /rest/openapi/pipeline/queryCommitDetail
  if (refsType === 'TAG') {
    const commitId = item.tagListVO.tagVOPage.data.find(
      (it) => it.name === refsTypeValue
    )?.commitId
    const res = await queryCommitDetail({ repoType, repoUrl, commitId })
    // 处理提交详情...
  } else {
    // 分支类型
    // 前端函数: queryRepoCommitList
    // API路径: POST /rest/openapi/pipeline/queryRepoCommitList
    const commitDesc = await queryRepoCommitList({ repoType, repoUrl, refsTypeValue })
  }

  // 验证分支/标签是否存在
  const optionList = item[refsTypeOptName.value[refsType]]?.[
    refsTypeSubOptName.value[refsType]
  ]?.data

  if (optionList?.length > 0) {
    const option = optionList.find((option: any) => option.name === sourceItem?.data?.branch)
    if (!option && sourceItem?.data?.branch) {
      ElMessage.warning(`${refsType === 'BRANCH' ? '分支' : '标签'}${sourceItem?.data?.branch}不存在, 请重新选择`)
    }
  } else {
    sourceItem.data.branch = ''
    error = `${refsType === 'BRANCH' ? '分支' : '标签'}不能为空`
  }

  return {
    ...item,
    ...sourceItem,
    refsTypeValue: sourceItem?.data?.branch,
    desc,
    error
  }
})

const results = await Promise.all(promises)
```

#### 7. 过滤有效数据

```typescript
// 获取所有任务的工作路径
const workPaths = props.flowData?.taskDataList?.map((item) => item.data?.workPath) || []

// 只保留在工作路径中的源
runConfig.value.runSourcesValues = results.filter(
  (item) => item && workPaths.includes(item.data?.workPath)
)
```

## 制品源初始化流程

### 计算属性：`packageSourceList`

```typescript
const packageSourceList = computed(() => {
  // 筛选制品源
  const packageSources = props.flowData?.pipeline?.sources?.filter(
    (item) => item?.data?.sourceType === 'package'
  )

  packageSources.forEach((item) => {
    item.data.tagSearchOptions = []

    // DOCKER 类型制品
    if (!item?.data?.packageType || item?.data?.packageType === PACKAGE_TYPE_ENUM.DOCKER) {
      return
    }

    // NORMAL 类型制品 - 设置 imageName
    item.data.imageName = item.data.fullPath
  })

  return cloneDeep(packageSources)
})
```

### 制品类型

| 类型 | packageType | 字段特点 |
|------|-------------|----------|
| Docker 镜像 | `DOCKER` | 使用 imageName、imageAddress、packageName |
| 普通制品 | `NORMAL` | 使用 normalArtifactName、fullPath、normalAddress |

## 执行提交数据转换

### 入口函数：`doRun`

```typescript
const doRun = async () => {
  const { pipelineId, triggerInfo } = props.flowData.pipeline
  const { runRemark, autoFillRunConfig } = runConfig.value
  let hasError = false
  // ...
}
```

### 1. 代码源数据转换

```typescript
const runSources = runConfig.value.runSourcesValues.map((item: any) => {
  const { refsType, refsTypeValue, data, id, name } = item

  // 执行时更新分支信息
  data.branch = item.refsTypeValue
  data.refsType = refsType

  // 校验
  if (!refsTypeValue) {
    item.error = `${refsType === 'TAG' ? '标签' : '分支'}不能为空`
    hasError = true
  } else {
    item.error = ''
  }

  // 获取 commit 信息
  const selectOption = item[refsTypeOptName.value?.[refsType]]?.[
    refsTypeSubOptName.value?.[refsType]
  ]?.data?.find((option: any) => {
    return option.name === refsTypeValue
  })

  const { commitId, commitMessage } = selectOption || {}

  return {
    refsType,
    refsTypeValue,
    id,
    name,
    shortName: name,
    data: {
      ...data,
      commitId,
      commitMessage
    }
  }
})
```

### 2. 制品源数据转换

```typescript
const packageSources = packageSourceList.value?.map((item: any) => {
  return {
    id: item.id,
    name: item.data.packageType === PACKAGE_TYPE_ENUM.NORMAL
      ? item.data.normalArtifactName
      : item.data.imageName,
    shortName: item.data.packageType === PACKAGE_TYPE_ENUM.NORMAL
      ? item.data.normalArtifactName
      : item.data.imageName,
    data: {
      packageType: item.data.packageType || PACKAGE_TYPE_ENUM.DOCKER,
      normalArtifactName: item.data.normalArtifactName,
      fullPath: item.data.fullPath,
      sourceType: item.data.sourceType,
      repoType: item.data.repoType,
      workPath: item.data.workPath,
      packageName: item.data.packageType === PACKAGE_TYPE_ENUM.NORMAL ? '' : item.data.packageName,
      firstDir: item.data.firstDir,
      imageName: item.data.packageType === PACKAGE_TYPE_ENUM.NORMAL ? '' : item.data.imageName,
      defaultTag: item.data.defaultTag,
      imageAddress: item.data.packageType === PACKAGE_TYPE_ENUM.NORMAL ? '' : item.data.imageAddress,
      normalAddress: item.data.normalAddress,
      ipackagePath: item.data.ipackagePath
    }
  }
})
```

### 3. 调整数据顺序

```typescript
const handleRunSource = (runSources: any[]) => {
  const sources = props.flowData?.pipeline?.sources
  if (!sources || !runSources) {
    return runSources
  }

  // 创建 workPath 到 runSource 的映射
  const runSourceMap = new Map()
  runSources.forEach((source: any) => {
    const workPath = source.data?.workPath
    if (workPath) {
      runSourceMap.set(workPath, source)
    }
  })

  // 按照 sources 的原始顺序重新排列
  const orderedRunSources: any = []
  sources.forEach((source) => {
    const workPath = source.data?.workPath
    if (workPath && runSourceMap.has(workPath)) {
      orderedRunSources.push(runSourceMap.get(workPath))
    }
  })

  return orderedRunSources
}
```

### 4. 提交执行

```typescript
// 前端函数: runByManual
// API路径: POST /rest/openapi/pipeline/runByManual
runByManual({
  pipelineId,
  triggerInfo,
  runRemark,
  autoFillRunConfig: isNoFirstRun.value ? autoFillRunConfig : false,
  runSources: handleRunSource([...runSources, ...packageSources]),
  customParameterRuns: customParameterRuns,
  taskDataList: taskTreeRef.value.getCheckedTaskDataList(),
  ...otherParams
})
```

## 数据流向图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              执行配置弹窗                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐                                                       │
│  │  openDialog()    │                                                       │
│  └────────┬─────────┘                                                       │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────┐                    │
│  │              doGetRepoBranchList()                  │                    │
│  ├─────────────────────────────────────────────────────┤                    │
│  │  1. getBranchVersion()                              │                    │
│  │     - 筛选代码源 sources[]                          │                    │
│  │     - 筛选制品源 packages[]                         │                    │
│  │     - 构建 codeSourceParams                          │                    │
│  │     - 构建 artifactParams                            │                    │
│  └────────┬────────────────────────────────────────────┘                    │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────┐                    │
│  │  queryLastestSelectedValueByField()                 │                    │
│  │  API: POST /rest/openapi/pipeline/queryLastestSelectedValueByField       │
│  │     - 获取最近一次执行的分支/标签/版本                │                    │
│  └────────┬────────────────────────────────────────────┘                    │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────┐                    │
│  │  回填数据到 sources                                 │                    │
│  │     - 代码源: branch, refsType                      │                    │
│  │     - 制品源: defaultTag, 替换路径版本号            │                    │
│  └────────┬────────────────────────────────────────────┘                    │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────┐                    │
│  │  getRepoBranchAndTagList()                           │                    │
│  │  API: POST /rest/openapi/pipeline/getRepoBranchAndTagList               │
│  │     - 批量获取分支/标签列表                          │                    │
│  └────────┬────────────────────────────────────────────┘                    │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────┐                    │
│  │  Promise.all() 处理每个源                           │                    │
│  │     - 获取提交信息                                   │                    │
│  │     - 验证分支/标签存在性                            │                    │
│  └────────┬────────────────────────────────────────────┘                    │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────┐                    │
│  │  runConfig.runSourcesValues = results               │                    │
│  │     - 过滤有效数据（在工作路径中的源）               │                    │
│  └─────────────────────────────────────────────────────┘                    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐                                                       │
│  │  doRun()         │                                                       │
│  └────────┬─────────┘                                                       │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────┐                    │
│  │  runSources = runSourcesValues.map()               │                    │
│  │     - 转换代码源格式                                 │                    │
│  │     - 获取 commitId/commitMessage                   │                    │
│  └────────┬────────────────────────────────────────────┘                    │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────┐                    │
│  │  packageSources = packageSourceList.map()          │                    │
│  │     - 转换制品源格式                                 │                    │
│  └────────┬────────────────────────────────────────────┘                    │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────┐                    │
│  │  handleRunSource([...runSources, ...packageSources])│                   │
│  │     - 按原始顺序重排数据                             │                    │
│  └────────┬────────────────────────────────────────────┘                    │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────┐                    │
│  │  runByManual({ runSources, ... })                   │                    │
│  │  API: POST /rest/openapi/pipeline/runByManual       │                    │
│  │     - 提交执行                                       │                    │
│  └─────────────────────────────────────────────────────┘                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 关键 API 对照表

| 前端函数名称 | API 路径 | 请求方法 | Python 方法名 | 用途 |
|-------------|---------|---------|--------------|------|
| `queryLastestSelectedValueByField` | `/rest/openapi/pipeline/queryLastestSelectedValueByField` | POST | `query_latest_selected_value` | 获取最近一次执行的分支/标签/版本 |
| `getRepoBranchAndTagList` | `/rest/openapi/pipeline/getRepoBranchAndTagList` | POST | `get_repo_branch_and_tag_list` | 批量获取分支和标签列表 |
| `getRepoBranchAndTagList` | `/rest/openapi/pipeline/getRepoBranchAndTagList` | POST | `get_repo_branch_and_tag_list_batch` | 批量获取多个代码源的分支/标签 |
| `queryCommitDetail` | `/rest/openapi/pipeline/queryCommitDetail` | POST | `query_commit_detail` | 获取标签的提交详情 |
| `queryRepoCommitList` | `/rest/openapi/pipeline/queryRepoCommitList` | POST | `query_repo_commit_list` | 获取分支的提交列表 |
| `queryPkgTags` | `/rest/openapi/pipeline/imageTags` | GET | `query_image_tags` | 查询 Docker 镜像标签 |
| `queryPkgArtifactTags` | `/rest/openapi/pipeline/packageVersions` | GET | `query_package_versions` | 查询普通制品版本 |
| `runByManual` | `/rest/openapi/pipeline/runByManual` | POST | `run_pipeline` | 手动执行流水线 |
| `edit` | `/rest/openapi/pipeline/edit` | GET | `get_pipeline_detail` / `get_pipeline_for_run` | 获取流水线配置 |

## 交互式选择功能

当 `INTERACTIVE_MODE=true` 时，执行流水线会询问用户是否交互式选择分支/标签/版本。

### 交互式选择相关方法

| 方法名 | 用途 |
|-------|------|
| `_interactive_select_branch_tag` | 交互式选择代码源的分支/标签 |
| `_interactive_select_package_version` | 交互式选择制品源的版本 |
| `_interactive_assemble_run_sources` | 交互式组装 runSources 数据 |
| `_auto_fill_run_sources` | 自动填充 runSources（使用最近执行记录） |

## 关键数据流

1. **初始化加载**: `openDialog` → `doGetRepoBranchList` → 回填 → 展示
2. **用户选择**: 用户选择分支/标签 → 更新 `runSourcesValues`
3. **执行提交**: `doRun` → 转换数据 → `handleRunSource` 调整顺序 → `runByManual`
