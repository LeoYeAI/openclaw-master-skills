---
name: devops-pipeline-management
description: |
  Expert for DevOps pipeline management, handling the complete lifecycle of pipelines on the quality and efficiency platform. Core capabilities:
  1) Workspace management - Query workspace lists with filtering
  2) Pipeline management - Create, query, update, and delete pipelines
  3) Execution management - Execute and cancel pipelines, query execution records and details
  4) Template management - Query pipeline templates and create pipelines from templates

  Trigger scenarios:
  - Users need to search for workspaces or pipelines
  - Users need to execute or run pipelines
  - Users need to check pipeline execution status or logs
  - Users need to create, update, or delete pipelines
  - Users need to query pipeline templates
---

# DevOps Pipeline Management Skill

## 概述

此 Skill 是 DevOps 质效平台的流水线管理专家，通过 OpenAPI 接口实现流水线的全生命周期管理。

**核心能力**：
- **工作空间管理**：查询工作空间列表，支持按名称、组织、产品线筛选
- **流水线管理**：创建、查询、更新、删除流水线，支持基于模板快速创建
- **执行管理**：执行流水线（支持交互式/非交互式模式）、取消执行、查询执行记录和详情
- **模板管理**：查询流水线模板列表，支持按名称、类型、语言筛选，用于快速创建流水线

**技术栈**：Python 3.8+、Requests、RESTful API

---

# ⚠️ 全局执行约束（强制执行）

> **执行任何子功能时，必须严格参考对应子功能文档。子功能文档即执行规范，禁止跳过、合并或自行发挥。**

## 核心原则

**子功能文档 = 执行规范 = 法律效力**

| 阶段 | 要求 |
|------|------|
| **执行前** | 必须先阅读对应子功能文档 |
| **执行中** | 必须按文档定义的步骤顺序执行 |
| **执行后** | 必须满足文档中的约束条件 |

**严格禁止的行为**：
- ✗ 不读文档直接执行
- ✗ 跳过或调换步骤执行
- ✗ 合并多个步骤为一步
- ✗ 自行实现功能而不调用对应Skill

## 全局约束清单

| 约束类型 | 约束说明 | 违反后果 |
|---------|---------|---------|
| **文档强制参考** | 执行子功能前必须阅读对应子功能文档 | 流程错误、操作失效 |
| **步骤顺序** | 子功能文档中定义的步骤必须按顺序执行，不得跳过、调换或合并 | 数据不完整、执行失败 |
| **配置预览** | 步骤中明确要求"预览"或"确认"的，必须执行该步骤后再继续 | 配置错误、无法追溯 |
| **必填校验** | 必填字段（文档中标记 ✅ 或"必填"）不能为空或空数组 | API调用失败 |
| **ID生成** | 新建实体时必须生成新的UUID，禁止复用已有ID | 数据冲突、覆盖问题 |
| **API调用** | 必须使用文档中指定的API接口，禁止自行调用其他接口 | 权限错误、功能异常 |
| **跨Skill调用** | 需要执行其他Skill功能时（如执行流水线），必须调用对应Skill | 流程中断、功能缺失 |

## 子功能文档（强制参考）

> **每个子功能都有专属文档，执行时必须严格参考对应文档**

### 流水线核心操作
| 子功能 | 文档路径 | 核心约束 |
|--------|---------|---------|
| 创建流水线 | [references/pipeline-create.md](references/pipeline-create.md) | **9步骤顺序**、配置预览(C7)必执行、调用pipeline-run skill |
| 更新流水线 | [references/pipeline-update.md](references/pipeline-update.md) | **6步骤顺序**、保留原pipelineId、ID保留 |
| 执行流水线 | [references/pipeline-run.md](references/pipeline-run.md) | taskDataList非空、参数组装、交互式/非交互式模式 |

### 任务节点管理
| 子功能 | 文档路径 | 核心约束 |
|--------|---------|---------|
| 添加任务节点 | [references/pipeline-task-add.md](references/pipeline-task-add.md) | 前置检查、ID生成、统一保存 |
| 更新任务节点 | [references/pipeline-task-update.md](references/pipeline-task-update.md) | 先查询、保留ID、字段合并 |
| 删除任务节点 | [references/pipeline-task-delete.md](references/pipeline-task-delete.md) | 前置确认、双重移除、依赖检查 |

### 查询与监控
| 子功能 | 文档路径 | 核心约束 |
|--------|---------|---------|
| 查询工作空间 | [references/workspace-list.md](references/workspace-list.md) | 分页参数、筛选条件 |
| 查询流水线列表 | [references/pipeline-page.md](references/pipeline-page.md) | 分页参数、排序规则 |
| 查询模板 | [references/pipeline-template.md](references/pipeline-template.md) | 语言筛选、类型筛选 |
| 查询执行记录 | [references/pipeline-list.md](references/pipeline-list.md) | 分页查询、状态筛选 |
| 查询执行详情 | [references/pipeline-run-detail.md](references/pipeline-run-detail.md) | 日志ID校验 |
| 流水线详情查询 | [references/pipeline-detail.md](references/pipeline-detail.md) | pipelineId校验 |

### 其他操作
| 子功能 | 文档路径 | 核心约束 |
|--------|---------|---------|
| 删除流水线 | [references/pipeline-delete.md](references/pipeline-delete.md) | 删除确认、不可恢复 |
| 取消执行 | [references/pipeline-cancel.md](references/pipeline-cancel.md) | 仅限执行中状态 |

## 约束示例

### ✅ 正确做法
- 执行"创建流水线" → **先阅读** [pipeline-create.md](references/pipeline-create.md) → **按9步骤执行**
- 执行"执行流水线" → **先阅读** [pipeline-run.md](references/pipeline-run.md) → **组装taskDataList**
- 步骤要求预览 → **展示预览**后再继续
- 需要执行流水线 → **调用** `pipeline-run` skill

### ❌ 错误做法（禁止）
- 不读文档直接执行
- 跳过配置预览步骤
- 自行实现 pipeline-run 功能而不调用 skill
- 合并多个步骤为一步
- 使用空数组作为 taskDataList
- 跳过必填字段校验

# DevOps Pipeline Management Skill

## 概述

此 Skill 是 DevOps 质效平台的流水线管理专家，通过 OpenAPI 接口实现流水线的全生命周期管理。

**核心能力**：
- **工作空间管理**：查询工作空间列表，支持按名称、组织、产品线筛选
- **流水线管理**：创建、查询、更新、删除流水线，支持基于模板快速创建
- **执行管理**：执行流水线（支持交互式/非交互式模式）、取消执行、查询执行记录和详情
- **模板管理**：查询流水线模板列表，支持按名称、类型、语言筛选，用于快速创建流水线

**技术栈**：Python 3.8+、Requests、RESTful API

## 环境准备

### 1. 系统要求

- Python 3.8+
- 网络可访问 DevOps 平台 API

### 2. 依赖安装

```bash
pip install requests
```

或使用 requirements.txt：

```bash
pip install -r requirements.txt
```

### 3. 获取 API 凭证

联系平台管理员获取以下凭证：

| 凭证 | 说明 |
|------|------|
| Domain Account | 域账号，用于权限校验和审计 |

## 环境变量配置

### 环境变量说明

| 变量名 | 必填 | 说明 |
|-------|-----|------|
| DEVOPS_DOMAIN_ACCOUNT | 是 | 域账号，用于权限校验和审计 |
| DEVOPS_BFF_URL | 是 | BFF 服务地址 |
| INTERACTIVE_MODE | 否 | 交互模式开关（默认：true）。true 时执行流水线会询问是否交互式选择分支/标签/版本 |

### 必填环境变量

```bash
# 域账号（必填）
export DEVOPS_DOMAIN_ACCOUNT="your_domain_account"

# BFF 服务地址（必填）
export DEVOPS_BFF_URL="https://one-dev.iflytek.com/devops"
```

### 可选环境变量

```bash
# 交互模式开关（默认：true）
# true: 执行流水线时询问是否交互式选择分支/标签/版本
# false: 自动使用最近执行记录填充，不询问
export INTERACTIVE_MODE="true"
```

### 持久化配置

将环境变量添加到 shell 配置文件（如 `~/.zshrc` 或 `~/.bashrc`）：

```bash
# DevOps Pipeline Skill 配置
export DEVOPS_DOMAIN_ACCOUNT="your_domain_account"
export DEVOPS_BFF_URL="https://one-dev.iflytek.com/devops"
export INTERACTIVE_MODE="true"  # 启用交互式选择功能
```

然后执行：

```bash
source ~/.zshrc  # 或 source ~/.bashrc
```

## 安装

### 方式一：直接使用

```bash
cd devops-skills/pipeline-management
python -m scripts/main --help
```

### 方式二：添加到 PATH（可选）

```bash
# 添加软链接（可选：使用 devops-pipeline 作为命令名）
sudo ln -s $(pwd)/scripts/main.py /usr/local/bin/devops-pipeline

# 使用
devops-pipeline --help      # 需要创建符号链接
```

> **说明**：文档中的命令示例统一使用 `python -m scripts/main` 作为入口命令。如需简化命令，可创建符号链接。

## 快速开始

### 1. 验证配置

```bash
python -m scripts/main
```

### 2. 查询工作空间

```bash
python -m scripts/main workspaces --name devops
```

### 3. 查询流水线列表

```bash
python -m scripts/main pipelines <space_id>
```

### 4. 执行流水线

```bash
python -m scripts/main run <pipeline_id>
```

## 典型工作流程

### 流程一：查找并执行流水线

```
1. workspaces          → 获取工作空间列表，找到目标空间ID
2. pipelines <spaceId> → 获取空间下的流水线列表，找到目标流水线ID
3. run <pipelineId>    → 执行流水线
4. list <pipelineId>   → 查看执行记录
5. run-detail <id>     → 查看执行详情
```

### 流程二：基于模板创建流水线（9步骤规范）

> **执行约束**：创建流水线必须严格按照 [pipeline-create.md](references/pipeline-create.md) 定义的9步骤顺序执行，不得跳过、调换或合并步骤。保存流水线操作通过 `save` 命令实现。

```
1. 解析用户输入 → 从自然语言提取 spaceId、流水线名称、技术栈等信息
2. 补充必填信息 → 交互式补充缺失的 spaceId、流水线名称等
3. 查询模板并选择 → 查询模板列表，交互式选择适合的模板
4. 模板数据转换 → 将模板数据转换为流水线数据，生成新UUID
5. 配置代码源 → 交互式配置代码仓库、分支等源代码信息
6. 配置任务节点 → 交互式配置任务参数、执行路径等
7. 配置预览 → 展示完整配置供用户确认
8. 保存流水线 → 调用 `save` 命令保存流水线配置
9. 执行流水线 → 调用 `run` 命令执行新创建的流水线
```

**关键约束**：
- **步骤顺序**：必须按 1→2→3→4→5→6→7→8→9 顺序执行，不得跳过、调换或合并
- **配置预览**：步骤7（配置预览）**必须执行**，用户确认后才能保存
- **命令调用**：步骤8使用 `save` 命令保存，步骤9使用 `run` 命令执行
- **ID生成**：`pipelineId` 新建时必须生成 UUID；模板转换时所有节点必须生成新 UUID
- **必填项**：`stages` 和 `taskDataList` 不能为空数组，否则保存/执行失败
- **API限定**：只能使用文档中指定的 API 接口

**说明**：
- 创建流水线通过 `save` 命令实现，需遵循上述9步骤流程
- 模板查询支持按名称模糊搜索、按类型筛选、按编程语言筛选
- 支持的模板语言：java, python, nodejs, go, dotnet, frontend, common

### 流程三：监控执行状态

```
1. list <pipelineId>       → 查看执行记录列表
2. run-detail <logId>      → 查看具体执行详情
3. cancel <logId>          → 如需取消正在执行的流水线
```

## 命令参考

所有命令均通过 `python -m scripts/main <command>` 调用。

### 工作空间与模板管理

| 命令 | 说明 | 用法 |
|------|------|------|
| `workspaces` | 查询工作空间列表 | `main.py workspaces [--name NAME] [--division NAME] [--team NAME] [--project-code CODE] [--page N] [--size N]` |
| `templates` | 查询流水线模板列表 | `main.py templates <space_id> [--name NAME] [--type TYPE] [--language LANG] [--account ACCOUNT] [--page N] [--size N]` |
| `pipelines` | 查询流水线列表 | `main.py pipelines <space_id> [--name NAME] [--page N] [--size N]` |

### 流水线配置管理

| 命令 | 说明 | 用法 |
|------|------|------|
| `detail` | 查询流水线详情 | `main.py detail <pipeline_id>` |
| `save` | 保存流水线（创建或更新） | `main.py save [--config JSON] [--file FILE] [--task-data JSON] [--task-data-file FILE]` |
| `delete` | 删除流水线 | `main.py delete <pipeline_id>` |

**`save` 命令参数说明**：
- `--config <json_string>`：流水线配置JSON字符串
- `--file <json_file_path>`：流水线配置JSON文件路径
- `--task-data <json_string>`：任务数据JSON字符串（可选）
- `--task-data-file <json_file_path>`：任务数据JSON文件路径（可选）

> **注意**：`save` 命令既可用于保存新流水线（需生成新pipelineId），也可用于更新现有流水线（保留原pipelineId）。创建流水线时应遵循 [pipeline-create.md](references/pipeline-create.md) 的9步骤规范，更新流水线时应遵循 [pipeline-update.md](references/pipeline-update.md) 的6步骤规范。

### 流水线执行与监控

| 命令 | 说明 | 用法 |
|------|------|------|
| `run` | 执行流水线 | `main.py run <pipeline_id> [--branch BRANCH] [--tasks TASKS] [--sources JSON] [--params JSON] [--auto-fill] [--re-run] [--remark TEXT] [--interactive] [--non-interactive]` |
| `list` | 查询执行记录 | `main.py list <pipeline_id> [--page-num N] [--page-size N]` |
| `run-detail` | 查询执行详情 | `main.py run-detail <pipeline_log_id>` |
| `cancel` | 取消流水线执行 | `main.py cancel <pipeline_log_id>` |

### 任务节点管理（流水线更新流程的一部分）

任务节点的添加、更新、删除操作是流水线更新流程的一部分，通过修改流水线配置并调用 `save` 命令实现。详细操作请参考：
- 添加任务节点：[pipeline-task-add.md](references/pipeline-task-add.md)
- 更新任务节点：[pipeline-task-update.md](references/pipeline-task-update.md)
- 删除任务节点：[pipeline-task-delete.md](references/pipeline-task-delete.md)

所有任务操作完成后，必须通过 `save` 命令统一保存流水线配置。

## 使用示例

### 查询工作空间列表

```bash
# 查询所有工作空间
python -m scripts/main workspaces

# 按名称搜索
python -m scripts/main workspaces --name devops

# 按组织筛选
python -m scripts/main workspaces --division "研发中心"

# 按产品线筛选
python -m scripts/main workspaces --team "DevOps平台"

# 分页查询
python -m scripts/main workspaces --page 2 --size 20
```

### 查询流水线列表

```bash
# 查询空间 133 的流水线列表
python -m scripts/main pipelines 133

# 按名称搜索
python -m scripts/main pipelines 133 --name 构建

# 分页查询
python -m scripts/main pipelines 133 --page-num 2 --page-size 20
```

### 查询流水线模板

```bash
# 查询空间 133 的模板列表
python -m scripts/main templates 133

# 按名称搜索
python -m scripts/main templates 133 --name Java

# 按类型筛选
python -m scripts/main templates 133 --type 1

# 按编程语言筛选
python -m scripts/main templates 133 --language java

# 分页查询
python -m scripts/main templates 133 --page 1 --size 20
```

### 基于模板创建流水线

**完整9步骤交互式创建**：
创建流水线需遵循 [pipeline-create.md](references/pipeline-create.md) 定义的9步骤规范。以下是完整流程：

```bash
# 1. 查询工作空间获取 space_id（可选，用于确认空间）
python -m scripts/main workspaces --name devops

# 2. 查询可用模板（可选，用于了解可用模板）
python -m scripts/main templates 133 --name "Java微服务"

# 3. 创建流水线配置（遵循9步骤规范）
#    步骤1-7：交互式收集配置信息
#    步骤8：使用 save 命令保存流水线配置
python -m scripts/main save --config '{"pipelineId": "新生成的UUID", "name": "我的Java流水线", "spaceId": 133, ...}'

# 4. 执行流水线（步骤9）
python -m scripts/main run <新创建的pipeline_id>
```
> **注意**：创建流水线必须严格遵循9步骤规范，包括：模板选择、代码源配置、任务节点配置、配置预览、保存和执行。

**分步创建（高级用法）**：
```bash
# 仅创建配置，不执行（步骤1-8）
# 遵循9步骤规范的前8步，生成流水线配置后使用 save 命令保存
python -m scripts/main save --file pipeline-config.json

# 更新已创建的流水线配置（遵循6步骤规范）
# 遵循 [pipeline-update.md](references/pipeline-update.md) 的6步骤规范
python -m scripts/main save --config '{"pipelineId": "现有pipelineId", "name": "更新后的名称", ...}'

# 执行已创建的流水线
python -m scripts/main run <pipeline_id>
```

**模板使用流程说明**：
1. **推荐使用完整交互式流程**：遵循9步骤规范创建流水线
2. **模板查询（可选）**：先通过 `templates` 命令查询可用模板，了解模板ID和配置
3. **交互式创建**：通过交互式向导收集配置信息，支持选择模板、配置代码源、配置任务节点
4. **配置预览**：创建过程中必须展示配置预览，供用户确认后再保存
5. **自动执行**：默认创建完成后自动执行流水线（步骤9），可根据需要跳过
6. **更新配置**：创建后如需修改，可遵循6步骤规范使用 `save` 命令更新配置

### 查询流水线详情

```bash
python -m scripts/main detail 4059831ef9ee41d3ad7d7c4c4be567b1
```

### 执行流水线

```bash
# 基本执行（使用默认配置）
python -m scripts/main run 4059831ef9ee41d3ad7d7c4c4be567b1

# 指定分支执行
python -m scripts/main run 4059831ef9ee41d3ad7d7c4c4be567b1 --branch feature/new-feature

# 指定执行的任务节点
python -m scripts/main run 4059831ef9ee41d3ad7d7c4c4be567b1 --tasks task-1,task-2

# 自动填充上次配置
python -m scripts/main run 4059831ef9ee41d3ad7d7c4c4be567b1 --auto-fill

# 非交互模式执行
python -m scripts/main run 4059831ef9ee41d3ad7d7c4c4be567b1 --non-interactive
```

### 查询执行记录

```bash
# 查询执行记录列表
python -m scripts/main list 4059831ef9ee41d3ad7d7c4c4be567b1

# 分页查询
python -m scripts/main list 4059831ef9ee41d3ad7d7c4c4be567b1 --page-num 1 --page-size 20

# 按状态搜索
python -m scripts/main list 4059831ef9ee41d3ad7d7c4c4be567b1 --type status --keyword success
```

### 查询执行详情

```bash
python -m scripts/main run-detail 22579
```

### 取消流水线

```bash
python -m scripts/main cancel 22579
```

### 创建流水线

```bash
# 创建流水线（遵循9步骤规范，使用 save 命令）
# 生成新的 pipelineId
python -m scripts/main save --config '{"pipelineId": "新生成的UUID", "name": "我的流水线", "spaceId": 133, "stages": [...], "sources": [...]}'

# 如果需要指定任务数据
python -m scripts/main save --config '{"pipelineId": "新生成的UUID", "name": "我的流水线", "spaceId": 133}' --task-data '[{"id": "task-001", "data": {...}}]'

# 从JSON文件创建
python -m scripts/main save --file pipeline-config.json
```

### 更新流水线

```bash
# 更新流水线（遵循6步骤规范，使用 save 命令）
# 保留原 pipelineId，更新需要修改的字段
python -m scripts/main save --config '{"pipelineId": "现有pipelineId", "name": "新名称", "spaceId": 133, ...}'

# 从JSON文件更新
python -m scripts/main save --file updated-pipeline-config.json

# 同时更新任务数据
python -m scripts/main save --config '{"pipelineId": "现有pipelineId", "name": "新名称", "spaceId": 133}' --task-data '[{"id": "task-001", "data": {...}}]'
```

### 删除流水线

```bash
python -m scripts/main delete 4059831ef9ee41d3ad7d7c4c4be567b1
```

## 请求头

| Header | 说明 | 示例 |
|--------|------|------|
| X-User-Account | 用户域账号 | `rfdai` |

## API 接口列表

**Base URL**: `/api/ai-bff/rest/openapi/pipeline`

| 序号 | 功能 | 接口路径 | 方法 |
|------|------|---------|------|
| 1 | 保存流水线 | /save | POST |
| 2 | 手动执行流水线 | /runByManual | POST |
| 3 | 获取流水线参数 | /edit | GET |
| 4 | 取消流水线 | /cancel | POST |
| 5 | 分页查询流水线执行记录 | /queryPipelineWorkPage | GET |
| 6 | 查询流水线执行记录详情 | /getPipelineWorkById | GET |
| 7 | 删除流水线 | /delete | POST |
| 8 | 分页查询流水线 | /queryPipelinePage | POST |
| 9 | 分页查询流水线模板 | /queryPipelineTemplatePage | POST |
| 10 | 查询最近流水线执行记录 | /queryLastestSelectedValueByField | POST |
| 11 | 查询流水线基本信息 | /queryPipelineById | GET |
| 12 | 分页获取分支/标签列表 | /getRepoBranchAndTagList | POST |
| 13 | 分页获取commit列表 | /queryRepoCommitList | POST |
| 14 | 查询代码提交详情 | /queryCommitDetail | POST |
| 15 | 获取镜像tag列表 | /imageTags | GET |
| 16 | 获取包版本列表 | /packageVersions | GET |
| 17 | 分页查询工作空间 | /queryWorkspacePage | POST |

完整 API 文档请参考: [pipeline_skill.md](docs/pipeline_skill.md)

## 流水线状态说明

| 状态码 | 状态名称 | 说明 |
|--------|----------|------|
| 100000 | 未执行 | 流水线初始状态 |
| 100001 | 等待中 | 等待执行资源 |
| 100002 | 执行中 | 正在执行 |
| 100004 | 成功 | 执行成功 |
| 100005 | 失败 | 执行失败 |
| 100006 | 已取消 | 用户取消 |

## 错误处理

### 常见错误

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 401 | 无API访问权限 | 联系管理员开通对应 API 权限 |
| 404 | 流水线不存在 | 检查流水线ID是否正确 |
| 429 | 请求过于频繁 | 降低请求频率 |

### 调试模式

执行时会打印详细的请求和响应信息：

```
============================================================
[Request] POST https://one-dev.iflytek.com/devops/api/ai-bff/rest/openapi/pipeline/runByManual
------------------------------------------------------------
Headers:
  X-User-Account: rfdai
------------------------------------------------------------
Body: {...}
============================================================

============================================================
[Response] Status: 200
------------------------------------------------------------
Response Body: {...}
============================================================
```

## 子功能文档

详细功能说明请参考 `references/` 目录：

### 流水线核心操作
| 功能 | 参考文档 |
|------|---------|
| 流水线创建 | [pipeline-create.md](references/pipeline-create.md) |
| 流水线更新 | [pipeline-update.md](references/pipeline-update.md) |
| 流水线执行 | [pipeline-run.md](references/pipeline-run.md) |

### 任务节点管理
| 功能 | 参考文档 |
|------|---------|
| 添加任务节点 | [pipeline-task-add.md](references/pipeline-task-add.md) |
| 更新任务节点 | [pipeline-task-update.md](references/pipeline-task-update.md) |
| 删除任务节点 | [pipeline-task-delete.md](references/pipeline-task-delete.md) |

### 查询与监控
| 功能 | 参考文档 |
|------|---------|
| 工作空间列表查询 | [workspace-list.md](references/workspace-list.md) |
| 流水线模板列表查询 | [pipeline-template.md](references/pipeline-template.md) |
| 流水线列表查询 | [pipeline-page.md](references/pipeline-page.md) |
| 流水线详情查询 | [pipeline-detail.md](references/pipeline-detail.md) |
| 流水线执行记录查询 | [pipeline-list.md](references/pipeline-list.md) |
| 流水线执行详情查询 | [pipeline-run-detail.md](references/pipeline-run-detail.md) |

### 其他操作
| 功能 | 参考文档 |
|------|---------|
| 流水线删除 | [pipeline-delete.md](references/pipeline-delete.md) |
| 流水线取消 | [pipeline-cancel.md](references/pipeline-cancel.md) |

## 注意事项

1. **环境变量必填**: 环境变量（DEVOPS_DOMAIN_ACCOUNT、DEVOPS_BFF_URL）均为必填，缺少任意一个将无法正常使用
2. **域账号必填**: `domain_account` 用于权限校验和操作审计
3. **删除不可恢复**: 删除操作不可恢复，请谨慎使用
4. **取消限制**: 取消操作只对正在执行的流水线有效（状态为 100001 或 100002）
5. **执行权限**: 执行流水线需要对应的 API 访问权限，无权限时返回 401
6. **环境变量持久化**: 建议将环境变量配置到 `~/.zshrc` 或 `~/.bashrc` 中，避免每次手动设置
7. **ID说明**:
   - `space_id` / `id`（WorkSpaceVO）：工作空间ID，用于查询流水线列表
   - `pipeline_id` / `pipelineId`：流水线ID，用于执行、查询详情等操作
   - `pipeline_log_id` / `id`（PipelineWorkVO）：执行记录ID，用于查看执行详情、取消执行

## 更新日志

### v1.2.0
- 移除 AppKey 签名认证，简化认证流程
- 仅需配置域账号和 BFF 服务地址
