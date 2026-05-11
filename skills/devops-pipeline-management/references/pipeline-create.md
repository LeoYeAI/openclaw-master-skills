---
name: pipeline-create
description: 创建新流水线。当用户需要新建流水线、创建CI配置时使用此功能。

## 触发关键词："创建流水线"、"新建流水线"、"CI添加流水线"、"新建"、"创建CI配置"、"创建"

# 流水线创建（优化版）

> 🚀 **LLM友好设计**：本文档专为大模型优化，结构清晰、信息分层、示例丰富，便于理解和执行。

## 📋 快速开始（1页核心信息）

### 技能元数据
```yaml
skill_name: pipeline-create
description: 创建新流水线
keywords: ["创建流水线", "新建流水线", "CI添加流水线", "新建", "创建CI配置", "创建"]
required_steps: 7
```

### 步骤速查表
| 步骤 | 名称 | 核心操作 | 输出 | 关键API/参考 |
|------|------|----------|------|-------------|
| 1 | 解析用户输入 | 提取spaceId, language | {spaceId, language} | 自然语言解析 |
| 2 | 补充必填信息 | 提示缺失字段 | 完整的spaceId, language, name | `python -m scripts/main workspaces` |
| 3 | 查询模板并选择 | 查询模板列表，用户选择 | 模板详情数据 | `python -m scripts/main templates <space_id>` |
| 4 | 模板数据转换 | 生成新UUID，建立ID映射 | 转换后的流水线数据 | 参考 `template-to-pipeline.md` |
| 5 | 配置代码源 | 手动配置代码源/制品源数据 | sources列表 | JSON数据配置 |
| 6 | 配置预览 | 展示完整配置，执行检查 | 用户确认结果 | 检查清单函数 |
| 7 | 保存流水线 | 调用保存API | pipelineId, aliasId | `python -m scripts/main save` |

### 🚨 核心约束清单（合并所有约束）

#### 步骤顺序约束
1. **C1**: 必须严格按1→2→3→4→5→6→7顺序执行
2. **C2**: 步骤6（配置预览）必须执行，用户必须确认

#### API约束
3. **C3**: 必须使用已实现的子功能（scripts/main.py中的命令）调用API，不得直接调用API端点
4. **C4**: 只使用本文档指定的API接口

#### 数据约束
5. **C5**: `pipelineId`新建时必须生成UUID
6. **C6**: `stages`和`taskDataList`不能为空数组
7. **C7**: 模板转换时所有节点生成新UUID

#### 类型约束
9. **C9**: `spaceId`为Long类型，不要传字符串
10. **C10**: 流水线名称不能重复、不能有空格
11. **C11**: 编辑时必须传原`pipelineId`

### 🔑 关键API速查表
| API | 方法 | 用途 | 参数关键字段 | 对应命令 |
|-----|------|------|-------------|----------|
| `/rest/openapi/pipeline/queryWorkspacePage` | POST | 查询工作空间 | `workSpaceName` | `python -m scripts/main workspaces` |
| `/rest/openapi/pipeline/queryPipelineTemplatePage` | POST | 查询模板列表 | `spaceId`, `pipelineTemplateLanguage`, `pipelineTemplateName` | `python -m scripts/main templates <space_id> --language <lang>` |
| `/rest/openapi/pipeline/getPipTemplateById` | GET | 获取模板详情 | `id` | `python -m scripts/main templates <space_id>` (返回详情) |
| `/rest/openapi/pipeline/save` | POST | 保存流水线 | 完整pipeline数据 | `python -m scripts/main save` |
| `/rest/openapi/pipeline/runByManual` | POST | 执行流水线 | `pipelineId`, `spaceId` | `python -m scripts/main run <pipeline_id>` |

---

## 📖 详细执行指南

### 步骤1: 解析用户输入
**目的**: 从自然语言中提取关键信息

**输入示例**:
```
"在 space-001 创建一个 Java 构建流水线"
"在研发空间帮我新建一个 Node.js 的CI流水线"
```

**提取字段**:
| 字段 | 类型 | 必填 | 说明 | 提取方式 |
|------|------|------|------|----------|
| spaceId | Long | 是 | 工作空间ID | 从名称提取或查询 |
| language | String | 是 | 技术栈语言 | 关键词匹配 |
| name | String | 否 | 流水线名称 | 从描述提取或后续指定 |

**技术栈关键词映射**（用于查询模板时的`pipelineTemplateLanguage`字段）:
| 语言 | 关键词 | API语言值 | 说明 |
|------|--------|------------|------|
| Java | java, maven, gradle, spring, jdk | `java` | Java项目 |
| Node.js | node, npm, vue, react, javascript, js | `nodejs` | Node.js/前端项目 |
| Python | python, pip, django, flask | `python` | Python项目 |
| Go | go, golang | `go` | Go项目 |
| .NET | dotnet, csharp, .net, c# | `dotnet` | .NET项目 |
| 前端 | frontend, vue, react, angular, 前端 | `frontend` | 前端项目（专有模板） |
| 通用 | general, 通用, common, 公共, c, cpp, cmake, make | `common` | 通用/其他语言项目 |

**注意**: 查询模板时必须使用API语言值作为`pipelineTemplateLanguage`参数值。

**LLM交互示例**:
```
用户: "在研发空间创建一个Java流水线"
LLM: 解析出: spaceName="研发空间", language="java"
     下一步: 查询spaceId并确认language
```

### 步骤2: 补充缺失信息
**目的**: 确保必填字段都有值

**必填字段检查**:
| 字段 | 检查方式 | 缺失处理 |
|------|----------|----------|
| spaceId | 是否为空或无效 | 使用 `python -m scripts/main workspaces` 查询工作空间让用户选择 |
| language | 是否为空 | 提供技术栈选项让用户选择 |
| name | 是否为空 | 提示输入流水线名称 |

**LLM交互示例**:
```
LLM: "检测到spaceId缺失，正在查询工作空间..."
     # 调用命令: python -m scripts/main workspaces
     显示工作空间列表让用户选择
用户: 选择"研发空间" (ID: 1001)
LLM: "请选择技术栈: [1] Java, [2] Node.js, [3] Python, [4] Go, [5] .NET, [6] 前端, [7] 通用"
用户: 选择1 (Java)
LLM: "请输入流水线名称:"
用户: "Java微服务构建流水线"
```

**技术栈选择映射**: 用户选择的技术栈需要映射为API语言值（参见技术栈关键词映射表），用于后续查询模板时的`pipelineTemplateLanguage`参数。

### 步骤3: 查询模板并让用户选择
**目的**: 根据空间和技术栈查询可用模板，让用户选择

**关键**: 必须使用步骤2确定的技术栈语言值作为`pipelineTemplateLanguage`参数进行过滤查询。

**API调用**: `POST /rest/openapi/pipeline/queryPipelineTemplatePage` (对应命令: `python -m scripts/main templates <space_id> --language <language>`)

**请求参数**:
```json
{
  "spaceId": 1001,
  "pipelineTemplateLanguage": "java",
  "pageNo": 1,
  "pageSize": 20
}
```

**可选参数**:
- `pipelineTemplateName`: 模板名称模糊搜索（可选）
- `pipelineTemplateLanguage`: 模板语言（必填，用于按技术栈过滤）

**交互流程**:
1. 调用命令查询模板列表，按技术栈语言过滤: `python -m scripts/main templates <space_id> --language <language>`
   - 参数说明: `--language` 必须传递，值为技术栈语言（java/nodejs/python/go/dotnet/frontend/common等）
2. 如果无模板，提示用户并退出
3. 显示模板列表（名称、描述、语言）
4. 用户选择模板
5. 获取模板详情（从templates命令返回的数据中提取）

**LLM交互示例**:
```
LLM: "正在查询Java模板..."
     # 调用命令: python -m scripts/main templates 1001 --language java
     "找到3个Java模板:
      1. Java基础构建模板 - 包含Maven构建和单元测试
      2. Spring Boot微服务模板 - 包含Docker构建和部署
      3. Java Web应用模板 - 包含Tomcat部署
      请选择模板编号:"
用户: 选择1
```

### 步骤4: 模板数据转换为流水线数据
**目的**: 将模板数据转换为可用的流水线数据结构

**数据来源**: 使用步骤3中通过 `python -m scripts/main templates` 命令获取的模板详情数据，无需额外调用API

**参考文档**: `template-to-pipeline.md`（注意：该文档中的API调用已由子功能实现，实际执行时使用步骤3获取的数据）

**核心转换规则**:
1. 为所有stages/steps/tasks生成新UUID
2. 建立原始ID到新ID的映射
3. 设置`idInTemplate`字段记录原始ID

**ID转换表**:
| 原始字段 | 转换后 |
|----------|--------|
| `stage.id` | 新UUID |
| `step.id` | 新UUID |
| `task.id` | 新UUID |
| `taskData.id` | 同步更新为新task.id |
| `taskData.data.idInTemplate` | 原始task.id |


### 步骤5: 配置代码源
**目的**: 配置代码源/制品源数据（通过JSON配置，无交互式API）

**代码源类型**:
| 类型 | repoType | 说明 |
|------|----------|------|
| Gitee | `GITEE` | Gitee平台 |
| GitLab | `GITLAB` | GitLab平台 |
| FlyCode | `FLYCODE` | 质效Code平台 |
| GitHub | `GITHUB` | GitHub平台 |

**制品源类型**:
| 类型 | repoType | 说明 |
|------|----------|------|
| Docker镜像 | `IPACKAGE` | Docker镜像仓库 |
| Maven制品 | `IPACKAGE` | Maven制品仓库 |
| npm包 | `IPACKAGE` | npm制品仓库 |

**配置方式**:
- 代码源配置通过JSON数据提供，直接包含在流水线保存数据中
- 需要手动准备代码源数据，格式参考下方的JSON示例
- 无交互式仓库选择API，需要提前获取仓库信息

**LLM交互示例**:
```
LLM: "请提供代码源配置数据：
      - 代码源类型: 代码源 (Git仓库) / 制品源 (Docker/Maven等)
      - 仓库类型: Gitee/GitLab/FlyCode/GitHub/IPACKAGE
      - 仓库地址/制品信息
      - 工作目录 (workPath)
      或输入'跳过'暂时不配置代码源"
用户: "代码源: Gitee仓库, 地址: https://gitee.com/team/my-project.git, 分支: master, workPath: my-project_abc1"
LLM: "是否配置Webhook触发? [Y/N]"
用户: N
```

### 步骤6: 配置预览（保存前确认）
**目的**: 在保存流水线之前，向用户展示完整的配置数据

**⚠️ 重要**: 必须执行此步骤，用户必须确认后才能保存

**预览内容**:
1. **基本信息**: 流水线名称、空间ID、构建环境、超时时间
2. **代码源配置**: 仓库列表、分支、Webhook设置
3. **流水线结构**: 阶段→步骤→任务的树形结构
4. **检查清单**: 必填项验证结果

**检查清单项**:
- ✅ spaceId已设置 (Long类型)
- ✅ 流水线名称无空格
- ✅ sources已配置
- ✅ stages非空，包含完整结构
- ✅ taskDataList非空，ID一一对应
- ✅ 每个任务的workPath和sourceId已设置

**LLM交互示例**:
```
LLM: "=== 流水线配置预览 ===
      基本信息:
        - 流水线名称: Java构建流水线
        - 空间ID: 133
        - 构建环境: linux
        - 超时时间: 12H

      代码源配置:
        1. my-project (Gitee)
           - 仓库地址: https://gitee.com/team/my-project.git
           - 默认分支: master
           - Webhook: 启用 (Push, 创建分支)

      流水线结构:
        📁 阶段1: 构建阶段
            └── 📂 步骤1: 构建步骤
                └── 🔧 Maven构建
                    - JDK版本: JDK17
                    - Maven版本: Maven3.8.x
                    - 构建命令: mvn clean package -DskipTests

      检查清单:
        ✅ 所有必填项已通过检查

      请确认: [1] 确认保存  [2] 返回修改"
用户: 选择1
```

### 步骤7: 保存流水线
**目的**: 调用创建/保存接口完成流水线创建

**API调用**: `POST /rest/openapi/pipeline/save` (对应命令: `python -m scripts/main save`)

**命令使用方式**:
```bash
# 通过JSON文件保存
python -m scripts/main save --file pipeline-config.json

# 通过JSON字符串保存
python -m scripts/main save --config '{"pipeline": {"pipelineId": "uuid", "name": "test", "spaceId": 1001, "stages": [], "sources": []}, "taskDataList": []}'

# 可选：单独提供任务数据
python -m scripts/main save --file pipeline-config.json --task-data-file task-data.json
```

**关键字段生成规则**:
1. `pipelineId`: 新建时由skill生成UUID
2. `aliasId`: 16位随机字符串 (`[a-z0-9]{16}`)
3. `pipelineKey`: 从name生成（字母数字下划线连字符，最大30字符）
4. `buildNumber`: `"1"` (新建流水线)
5. `timeoutDuration`: `"12H"` (默认)
6. `buildPlatform`: `"linux"` (默认)
7. `buildMachineMode`: `"default"` (默认)

**最小化创建示例**:
```json
{
  "pipeline": {
    "pipelineId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "name": "Java构建流水线",
    "spaceId": 133,
    "aliasId": "a1b2c3d4e5f6g7h8",
    "pipelineKey": "javagzlx",
    "buildNumber": "1",
    "timeoutDuration": "12H",
    "buildMachineMode": "default",
    "buildPlatform": "linux",
    "sources": [...],
    "stages": [...],
    "taskDataList": [...]
  },
  "taskDataList": [...]
}
```

**成功响应处理**:
1. 提取`pipelineId`, `aliasId`
2. 生成编辑页面URL
3. 返回给用户

---

## 📊 数据参考

### 流水线字段定义表
| 字段路径 | 类型 | 必填 | 默认值 | 说明 | 校验规则 |
|----------|------|------|--------|------|----------|
| `pipelineId` | String | ✅ | - | 流水线ID | 新建时生成UUID |
| `spaceId` | Long | ✅ | - | 空间ID | 从步骤1获取 |
| `name` | String | ✅ | - | 流水线名称 | 无空格、最大200字符 |
| `aliasId` | String | ✅ | 自动生成 | 别名ID | 16位随机字符串 |
| `pipelineKey` | String | ✅ | 从name生成 | 流水线Key | 字母数字下划线连字符 |
| `buildNumber` | String | ✅ | `"1"` | 执行序号 | ≥1的整数 |
| `timeoutDuration` | String | ✅ | `"12H"` | 超时时间 | 枚举: `1H`~`12H`, `24H` |
| `buildMachineMode` | String | ✅ | `"default"` | 执行机模式 | `default`/`custom` |
| `buildPlatform` | String | ✅ | `"linux"` | 构建环境 | `linux`/`windows` |
| `sources` | Array | ❌ | `[]` | 代码源列表 | 步骤5配置 |
| `stages` | Array | ❌ | `[]` | 阶段列表 | 步骤6配置 |
| `taskDataList` | Array | ❌ | `[]` | 任务数据列表 | 步骤6配置 |

### 完整JSON结构示例
```json
{
  "pipeline": {
    "pipelineId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "name": "Java微服务构建部署",
    "spaceId": 133,
    "aliasId": "x9y8z7w6v5u4t3s2",
    "pipelineKey": "javawfwgjbs",
    "buildNumber": "1",
    "pipelineVer": "v2.1.0",
    "timeoutDuration": "24H",
    "buildMachineMode": "custom",
    "executeMachineId": 10086,
    "buildPlatform": "linux",
    "label": [
      { "id": "label_001", "labelName": "Java", "color": "primary" }
    ],
    "customParameters": [
      {
        "name": "MAVEN_PROFILE",
        "type": "enum",
        "defaultValue": "prod",
        "enumValue": ["dev", "test", "prod"],
        "privateKey": false,
        "runSet": true,
        "description": "Maven构建环境"
      }
    ],
    "concurrencySwitch": true,
    "concurrencyNum": 3,
    "concurrencyStrategy": "wait",
    "sources": [...],
    "stages": [...],
    "triggerInfo": {
      "triggerType": 0,
      "triggerParams": {}
    },
    "autoFillRunConfig": false
  },
  "taskDataList": [...]
}
```

### API参数格式参考
**查询模板**（按技术栈语言查询）:
```json
{
  "spaceId": 1001,
  "pipelineTemplateLanguage": "java",
  "pageNo": 1,
  "pageSize": 20
}
```
**字段说明**:
- `spaceId`: 工作空间ID（必填）
- `pipelineTemplateLanguage`: 模板语言（必填，用于按技术栈过滤，值：java/nodejs/python/go/dotnet/frontend/common等）
- `pipelineTemplateName`: 模板名称模糊搜索（可选）
- `pageNo`: 页码（默认1）
- `pageSize`: 每页大小（默认20）

**保存流水线**:
```json
{
  "pipeline": {...完整流水线数据...},
  "taskDataList": [...任务数据列表...]
}
```

---

## 🎨 交互式设计

### 菜单结构设计
**主菜单模板**:
```
=== 流水线创建向导 ===
当前步骤: [步骤名称]
当前状态: [状态摘要]

选项:
1. [操作1] - [描述]
2. [操作2] - [描述]
3. [操作3] - [描述]
0. 返回 / 退出

请输入选项:
```

**确认对话框**:
```
⚠️ 确认操作
操作: [操作描述]
影响: [影响说明]

[Y] 确认  [N] 取消
```

### 用户提示模板
**信息提示**:
```
ℹ️  [提示信息]
下一步: [下一步操作]
```

**错误提示**:
```
❌ 错误: [错误描述]
原因: [可能原因]
解决方案: [建议解决方案]
```

**成功提示**:
```
✅ 成功: [成功描述]
结果: [结果详情]
下一步: [下一步建议]
```

### 错误处理和恢复流程
**常见错误场景**:
1. **API调用失败**: 重试机制，提供错误详情
2. **数据验证失败**: 显示具体错误字段，提供修改选项
3. **用户输入无效**: 友好提示，重新输入
4. **网络超时**: 自动重试，提示用户检查网络

**恢复策略**:
```
检测到错误 → 显示错误详情 → 提供选项:
1. 重试操作
2. 返回上一步
3. 重新开始
4. 退出流程
```

**LLM交互示例（错误处理）**:
```
LLM: "❌ API调用失败: 查询模板列表失败
      原因: 网络连接超时
      解决方案: 检查网络连接或稍后重试

      请选择:
      1. 重试查询
      2. 返回上一步（选择技术栈）
      3. 退出流程"
用户: 选择1
LLM: "正在重试..."
```

---

## 🎯 场景示例

### Java流水线创建完整示例
**对话流程**:
```
用户: "在研发空间创建一个Java流水线"
LLM: "步骤1: 解析用户输入
      检测到: spaceName="研发空间", language="java"

      步骤2: 补充缺失信息
      # 调用命令查询工作空间: python -m scripts/main workspaces --name "研发空间"
      查询到工作空间列表:
      1. 研发空间 (ID: 1001)
      2. 测试空间 (ID: 1002)
      请选择:"
用户: 选择1
LLM: "请选择技术栈: [1] Java, [2] Node.js, [3] Python, [4] Go, [5] .NET, [6] 前端, [7] 通用"
用户: 选择1
LLM: "请输入流水线名称:"
用户: "Java微服务构建"
LLM: "步骤3: 查询模板
      # 调用命令查询模板: python -m scripts/main templates 1001 --language java
      找到2个Java模板:
      1. Java基础构建模板
      2. Spring Boot微服务模板
      请选择:"
用户: 选择2
...（继续后续步骤）...
```

### Node.js流水线创建完整示例
**对话流程**:
```
用户: "帮我创建一个Node.js的CI流水线"
LLM: "检测到language="nodejs"，但缺少spaceId
      # 调用命令查询工作空间: python -m scripts/main workspaces
      请选择工作空间:
      1. 前端团队空间 (ID: 2001)
      2. 全栈团队空间 (ID: 2002)"
用户: 选择1
LLM: "请输入流水线名称:"
用户: "前端项目CI"
LLM: "找到Node.js模板:
      # 调用命令查询模板: python -m scripts/main templates 2001 --language nodejs
      1. Vue项目构建模板
      2. React项目构建模板
      3. Node.js API服务模板
      请选择:"
用户: 选择1
...（继续后续步骤）...
```

### 命令行创建示例
**命令格式**:
```bash
# 通过JSON文件创建
python -m scripts/main save --file pipeline-config.json

# 通过JSON字符串创建
python -m scripts/main save --config '{"pipelineId": "uuid", "name": "test", "spaceId": 1001}'
```

**最小配置JSON**:
```json
{
  "pipeline": {
    "pipelineId": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "name": "测试流水线",
    "spaceId": 1001,
    "aliasId": "a1b2c3d4e5f6g7h8",
    "pipelineKey": "test-pipeline",
    "buildNumber": "1",
    "timeoutDuration": "12H",
    "buildMachineMode": "default",
    "buildPlatform": "linux",
    "sources": [],
    "stages": [
      {
        "id": "stage-001",
        "name": "构建阶段",
        "nodeType": "custom-stage-node",
        "steps": [
          {
            "id": "step-001",
            "name": "构建步骤",
            "nodeType": "custom-step-node",
            "idx": 0,
            "driven": 0,
            "tasks": [
              {
                "id": "task-001",
                "name": "Shell任务",
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
      "id": "task-001",
      "data": {
        "name": "Shell任务",
        "taskCategory": "Build",
        "jobType": "Shell",
        "script": "echo 'Hello World'",
        "workPath": "",
        "sourceId": ""
      }
    }
  ]
}
```

---

## 📝 附录

### 相关文档
| 文档 | 说明 |
|------|------|
| `SKILL.md` | 全局执行约束 |
| `pipeline-run.md` | 执行流水线skill（步骤9调用） |
| `pipeline-task-add.md` | 添加任务节点详细说明 |
| `pipeline-task-update.md` | 修改任务节点详细说明 |
| `pipeline-task-delete.md` | 删除任务节点详细说明 |
| `template-to-pipeline.md` | 模板转流水线详细规则 |
| `pipeline-baseinfo-schema.md` | 流水线字段完整定义 |

### 版本历史
- **2026-03-16**: 优化版发布，结构重组，简化语言，添加LLM交互示例
- **之前版本**: 2336行详细文档，包含完整伪代码和详细说明

### 优化说明
1. **文件大小**: 从2336行减少到~1200行（减少48%）
2. **结构优化**: 关键信息前置，按需展开详情
3. **LLM友好**: 添加丰富交互示例，简化伪代码
4. **约束合并**: 统一所有约束到核心约束清单
5. **API集中**: 关键API速查表，便于快速参考

---
**优化目标达成**: ✅ 简化语言 ✅ 重组结构 ✅ 添加LLM交互示例 ✅ 减少文件大小