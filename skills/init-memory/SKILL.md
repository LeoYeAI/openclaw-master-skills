---
name: init-memory
description: 为任意项目初始化 Claude 持久化记忆系统（v3.0 搜索引擎模型）。自动扫描项目结构、技术栈、代码规范，生成完整的记忆文件和 CLAUDE.md 指令。
---

# 🧠 Claude 持久化记忆系统初始化 Skill

> 记忆系统 v3.0 — "搜索引擎"模型：启动只读摘要，详情按需检索
>
> **核心理念**: Claude 不需要"记住一切"，只需要"知道去哪找"。

## 参数处理

用户输入参数: $ARGUMENTS

解析参数:
- `--force`: 覆盖已有的记忆文件（默认跳过已存在的文件）
- `--minimal`: 只创建核心文件（SUMMARY.md, architecture.json, conventions.json, semantic-index.json, changelog.json）
- `--lang zh`: 注释和描述使用中文（默认）
- `--lang en`: 注释和描述使用英文

如果 `.claude/memory/SUMMARY.md` 已存在且没有 `--force` 参数，**停止执行**并提示用户:
> ⚠️ 记忆系统已存在。使用 `--force` 覆盖，或手动删除 `.claude/memory/` 目录后重试。

---

## Step 1: 扫描项目

### 1.1 项目结构扫描

```
Glob "**/{package.json,tsconfig.json,Cargo.toml,go.mod,pyproject.toml,setup.py,requirements.txt,pom.xml,build.gradle,Gemfile,composer.json,CMakeLists.txt,Makefile,.csproj,pubspec.yaml,mix.exs,deno.json}" (忽略 node_modules、vendor、target、dist、build、.git)
```

读取找到的配置文件，提取:
- 项目名称（优先: package.json name > Cargo.toml name > go.mod module > 目录名）
- 技术栈（语言、框架、构建工具、运行时）
- 依赖列表（核心依赖，不含 devDependencies 细节）
- 脚本/命令（build/test/dev/start）
- 是否为 monorepo（workspaces / 多个子 package.json）

### 1.2 目录布局
```bash
find . -maxdepth 3 -type d \
  ! -path '*/node_modules/*' ! -path '*/.git/*' ! -path '*/dist/*' \
  ! -path '*/build/*' ! -path '*/.next/*' ! -path '*/target/*' \
  ! -path '*/vendor/*' ! -path '*/__pycache__/*' ! -path '*/.claude/*' \
  ! -path '*/.venv/*' ! -path '*/venv/*' ! -path '*/.tox/*' \
  | head -80 | sort
```

### 1.3 核心模块识别

根据项目语言类型选择合适的扫描模式:

**TypeScript/JavaScript 项目:**
```
Grep "^export (class|function|const|interface|type|enum)" --type ts,tsx,js,jsx
```

**Python 项目:**
```
Grep "^(class |def )" --type py
```

**Go 项目:**
```
Grep "^(func |type .* struct)" --type go
```

**Rust 项目:**
```
Grep "^(pub fn |pub struct |pub enum |pub trait )" --type rs
```

**Java/Kotlin 项目:**
```
Grep "^(public class|public interface|public enum|class |fun )" --type java,kt
```

取前 100 个结果，识别核心模块和它们的位置。

### 1.4 大文件识别（热点文件）
```bash
find . \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' \
  -o -name '*.py' -o -name '*.go' -o -name '*.rs' -o -name '*.java' \
  -o -name '*.kt' -o -name '*.vue' -o -name '*.svelte' -o -name '*.rb' \
  -o -name '*.ex' -o -name '*.exs' -o -name '*.dart' -o -name '*.swift' \
  -o -name '*.cpp' -o -name '*.c' -o -name '*.h' \) \
  ! -path '*/node_modules/*' ! -path '*/dist/*' ! -path '*/build/*' \
  ! -path '*/target/*' ! -path '*/vendor/*' ! -path '*/.git/*' \
  -exec wc -l {} + 2>/dev/null | sort -rn | head -20
```

对超过 500 行的文件进行逻辑分区扫描（扫描 function/class/section 定义及其行号）。
如果项目源文件较少，可降低阈值到 300 行。

### 1.5 代码规范推断

读取 3-5 个核心源文件的前 50 行，推断:
- 缩进风格（tab vs space，几个空格）
- 引号风格（单引号 vs 双引号）
- 分号使用
- 命名约定（camelCase / snake_case / PascalCase）
- 导入风格和顺序
- 注释语言（中文/英文/混合）

同时检查是否存在以下配置文件:
`.eslintrc*`, `.prettierrc*`, `rustfmt.toml`, `.editorconfig`, `pyproject.toml [tool.black]`, `setup.cfg [flake8]`, `.rubocop.yml`, `biome.json`

### 1.6 项目特有规则扫描

检查是否已有:
- `CLAUDE.md` — 已有的 Claude 指令
- `.claude/` 目录 — 已有的 Claude 配置
- `CONTRIBUTING.md` — 贡献指南中的规范
- `.github/` — CI/CD 配置中的约束

---

## Step 2: 创建记忆文件

创建 `.claude/memory/` 目录，然后基于 Step 1 的扫描结果创建以下文件。

**重要规则**:
- 所有 JSON 文件中的 `$schema` 字段使用实际项目名称（从配置文件推断），不要硬编码
- 所有内容必须来自实际扫描，不得使用占位模板
- JSON 使用 2 空格缩进
- 日期格式统一 YYYY-MM-DD
- 文件使用 UTF-8 编码

### 2.1 architecture.json — 项目架构概览
```json
{
  "$schema": "<项目名> Architecture",
  "$version": "1.0.0",
  "$updated": "<今天日期>",
  "$description": "项目架构概览",

  "project": {
    "name": "<项目名>",
    "description": "<从配置文件推断的项目描述>",
    "monorepo": false,
    "packageManager": "<npm|yarn|pnpm|pip|cargo|go modules|...>"
  },

  "techStack": {
    "language": "<主要语言及版本>",
    "framework": "<主要框架及版本>",
    "buildTool": "<构建工具>",
    "runtime": "<运行时环境>",
    "uiLibrary": "<UI 库（如适用）>",
    "testFramework": "<测试框架>"
  },

  "packages": {
    "<包名>": {
      "path": "<路径>",
      "role": "<职责描述>",
      "entry": "<入口文件>",
      "format": "<ESM|CJS|mixed>"
    }
  },

  "mainModules": {
    "<模块名>": {
      "file": "<文件路径>",
      "lines": "<行数>",
      "role": "<职责描述>",
      "warning": "<注意事项（可选）>",
      "keyDataStructures": ["<核心数据结构>"]
    }
  },

  "keyDependencies": [
    { "name": "<包名>", "version": "<版本>", "purpose": "<用途>" }
  ]
}
```

**monorepo 项目**: `packages` 字段列出所有子包及其角色。
**单包项目**: `packages` 只有一个条目或省略。

### 2.2 conventions.json — 代码规范
```json
{
  "$schema": "<项目名> Code Conventions",
  "$version": "1.0.0",
  "$updated": "<今天日期>",
  "$description": "代码规范和约定。新增代码必须遵守这些规范",

  "codeStyle": {
    "language": "<TypeScript (strict)|Python 3.x|Go|...>",
    "indent": "<2 spaces|4 spaces|tabs>",
    "quotes": "<single|double>",
    "semicolons": "<true|false|N/A>",
    "trailingComma": "<none|es5|all|N/A>",
    "formatter": "<Prettier|Black|gofmt|rustfmt|...>",
    "linter": "<ESLint|Ruff|golint|clippy|...>"
  },

  "namingConventions": {
    "files": { "<类型>": "<命名规则>" },
    "code": {
      "classes": "<PascalCase>",
      "interfaces": "<规则>",
      "functions": "<camelCase|snake_case>",
      "constants": "<UPPER_SNAKE_CASE>",
      "variables": "<camelCase|snake_case>"
    }
  },

  "patterns": {
    "<模式名>": {
      "description": "<描述>",
      "template": "<代码模板（可选）>",
      "steps": ["<步骤>"]
    }
  },

  "commitMessageStyle": {
    "language": "<项目注释语言>",
    "prefix": "feat:/fix:/refactor:/chore:/docs:/test:",
    "examples": ["<示例>"]
  },

  "importOrder": ["<导入分组规则>"],

  "criticalRules": [
    "<从代码和配置中推断出的关键规则>"
  ]
}
```

### 2.3 semantic-index.json — 语义索引
```json
{
  "$schema": "<项目名> Semantic Index",
  "$version": "1.0.0",
  "$updated": "<今天日期>",
  "$description": "关键词索引——从功能域/关键词到相关文件的映射",

  "index": {
    "<关键词|别名|同义词>": {
      "description": "<功能域描述>",
      "files": [
        { "path": "<文件路径>", "sections": ["<逻辑区域>"], "lineRange": [0, 0] }
      ],
      "quickRules": ["<该领域的快速提示/规则>"]
    }
  }
}
```

基于 Step 1.3 的扫描结果填充。将相关的导出按功能域分组。
每个索引条目可以有多个关键词别名（用 `|` 分隔）。

### 2.4 hotspot-map.json — 热点文件分区图
```json
{
  "$schema": "<项目名> Hotspot Map",
  "$version": "1.0.0",
  "$updated": "<今天日期>",
  "$description": "热点文件的逻辑分区图。修改大文件前先查此文件定位行号范围",

  "files": {
    "<文件名>": {
      "path": "<完整相对路径>",
      "totalLines": 0,
      "touchFrequency": 0,
      "sections": [
        {
          "name": "<逻辑分区名>",
          "lineRange": [0, 0],
          "description": "<该分区的功能描述>",
          "keySymbols": ["<重要函数/类名>"],
          "touchCount": 0,
          "subSections": []
        }
      ]
    }
  }
}
```

仅包含超过 500 行（小项目 300 行）的文件。每个文件最多 15 个分区。

### 2.5 task-context.json — 任务上下文
```json
{
  "$schema": "<项目名> Task Context",
  "$version": "1.0.0",
  "$updated": "<今天日期>",
  "$description": "当前任务上下文。帮助 Claude 理解未完成的工作",

  "currentTasks": [],
  "recentCompleted": [],
  "pendingIssues": [],
  "completedTasks": [],
  "knownLimitations": []
}
```

### 2.6 changelog.json — 变更日志
```json
{
  "$schema": "<项目名> Session Changelog",
  "$version": "1.0.0",
  "$updated": "<今天日期>",
  "$description": "增量变更日志。每次会话修改代码后追加记录",

  "sessions": [
    {
      "id": "SESSION-001",
      "date": "<今天日期>",
      "summary": "初始化 Claude 记忆系统",
      "changes": [
        {
          "action": "create",
          "files": [".claude/memory/*", "CLAUDE.md"],
          "reason": "建立持久化记忆系统，实现跨会话知识保持"
        }
      ],
      "decisions": ["采用 v3.0 搜索引擎模型：启动只读 SUMMARY.md，详情按需 Grep 检索"],
      "lessonsLearned": [],
      "ripples": { "description": "纯新增文件，无代码影响", "affectedModules": [], "sideEffects": [] },
      "rejectedAlternatives": []
    }
  ]
}
```

### 2.7 bugs-and-fixes.json — Bug 记录
```json
{
  "$schema": "<项目名> Bug & Fix Registry",
  "$version": "1.0.0",
  "$updated": "<今天日期>",
  "$description": "已知 Bug 和修复记录。避免相同问题重复犯错",

  "bugs": [],
  "commonMistakes": [],
  "predictions": []
}
```

### 2.8 causality-graph.json — 因果图谱
```json
{
  "$schema": "<项目名> Causality Graph",
  "$version": "1.0.0",
  "$updated": "<今天日期>",
  "$description": "因果图谱——记录 Bug 的完整因果链。新 Bug 出现时沿已知链反向推导",

  "chains": [],
  "chainIndex": {}
}
```

**如果使用了 `--minimal` 参数**，跳过: hotspot-map.json, task-context.json, bugs-and-fixes.json, causality-graph.json

### 2.9 SUMMARY.md（最后创建）

```markdown
# <项目名> — Claude 记忆摘要

> 记忆系统 v3.0 — 本文件是固定大小的"缓存"，详细数据在各 JSON 文件中

## 🏗️ 架构速览
- **技术栈**: <语言 + 框架 + 构建工具>
- **项目结构**: <简要描述目录布局>
- **核心模块**: <列出 3-5 个最重要的模块>

## 📊 热点文件
<列出行数最多的 3-5 个文件及其行数>

## 🔄 最近 3 次变更
1. SESSION-001: 初始化 Claude 记忆系统

## 📋 当前状态
- **进行中**: 无
- **待处理**: 无

## ⚠️ 高频陷阱（Top 5）
暂无记录

## 🔍 检索指南
| 需要什么 | 怎么查 |
|----------|--------|
| 功能域→文件映射 | `Grep "关键词" .claude/memory/semantic-index.json` |
| 大文件行号定位 | `Grep "section名" .claude/memory/hotspot-map.json` |
| Bug 因果链 | `Grep "症状" .claude/memory/causality-graph.json` |
| 已知 Bug/预判 | `Grep "症状" .claude/memory/bugs-and-fixes.json` |
| 历史决策 | `Grep "功能" .claude/memory/changelog.json` |
| 代码规范 | `Read .claude/memory/conventions.json` |
| 完整架构 | `Read .claude/memory/architecture.json` |
```

---

## Step 3: 生成/更新 CLAUDE.md

### 要注入的记忆系统指令块

以下内容用 `<!-- MEMORY-SYSTEM-START -->` 和 `<!-- MEMORY-SYSTEM-END -->` 标记包裹:

```markdown
<!-- MEMORY-SYSTEM-START -->
## 📖 启动时只读一个文件

\```
Read .claude/memory/SUMMARY.md
\```

**不要**在启动时读取其他记忆文件。SUMMARY.md 包含架构速览、当前状态、高频陷阱和检索指南。

## 🔍 按需检索（改代码/修 Bug 前查询）

需要详情时，用 Grep/Read **精准查询**对应文件，不要全量加载：

| 场景 | 做什么 |
|------|--------|
| **改代码前** — 定位文件和行号 | `Grep "关键词" .claude/memory/semantic-index.json` |
| **改核心文件** — 查逻辑分区行号 | `Grep "section名" .claude/memory/hotspot-map.json` |
| **修 Bug 前** — 匹配已知症状 | `Grep "症状关键词" .claude/memory/causality-graph.json` |
| **修 Bug 前** — 查是否已预判 | `Grep "症状" .claude/memory/bugs-and-fixes.json` |
| **查历史决策** — 为什么这样做 | `Grep "功能关键词" .claude/memory/changelog.json` |
| **查代码规范** — 命名/风格/模式 | `Read .claude/memory/conventions.json` |
| **查完整架构** — 模块/IPC/技术栈 | `Read .claude/memory/architecture.json` |

## ⚡ 关键规则

> 以下规则从项目扫描中自动生成，请根据实际情况补充

1. **热点文件** — 修改超过 500 行的文件前，必须先 Grep semantic-index + hotspot-map 定位
2. **修 Bug** — 先 Grep causality-graph 的 chainIndex 匹配症状
3. 提交信息推荐 `feat:/fix:/refactor:/chore:` 前缀

## 🔄 任务完成后必须更新

每次完成代码修改后，按需更新以下文件（只更新涉及到的）：

### 必更新
- **changelog.json** — 在 `sessions` 数组末尾追加：
  ```json
  {
    "id": "SESSION-xxx", "date": "YYYY-MM-DD", "summary": "...",
    "changes": [{ "action": "create|modify|delete", "files": [...], "reason": "..." }],
    "decisions": [...], "lessonsLearned": [...],
    "ripples": { "description": "...", "affectedModules": [...], "sideEffects": [...] },
    "rejectedAlternatives": [{ "option": "...", "reason": "..." }]
  }
  ```

### 按需更新
- **bugs-and-fixes.json** — 修了 Bug → 追加 bugs；发现易错模式 → 追加 commonMistakes；主动扫描 → 追加 predictions
- **task-context.json** — 更新 currentTasks / recentCompleted（只保留最近 5 条）/ pendingIssues
- **hotspot-map.json** — 改了核心文件 → touchCount +1, lastModified, lineRange 偏移
- **semantic-index.json** — 新增功能域 → 添加索引条目
- **causality-graph.json** — 发现新因果链 → 追加 chains + 更新 chainIndex
- **architecture.json** — 架构变化（新模块/IPC/页面）→ 同步更新

### 最后一步：重写 SUMMARY.md
从各详细文件中提取最新信息，**重写**（非追加）SUMMARY.md：
- `最近 3 次变更` ← changelog.json 最后 3 条的 summary
- `当前状态` ← task-context.json 的 currentTasks + pendingIssues
- `高频陷阱` ← bugs-and-fixes.json 的 commonMistakes（Top 5）
- 其他部分按需更新

> 💡 设计理念：SUMMARY.md 是固定大小的"缓存"，详细数据永远保留在原文件中。
> Claude 不需要"记住一切"，只需要"知道去哪找"。
<!-- MEMORY-SYSTEM-END -->
```

### 注入逻辑

1. **如果 CLAUDE.md 不存在**:
   创建新文件，内容为:
   ```markdown
   # <项目名> — Claude 工程指令

   > 记忆系统 v3.0 — "搜索引擎"模型：启动只读摘要，详情按需检索

   <记忆系统指令块>
   ```

2. **如果 CLAUDE.md 已存在**:
   - 如果已包含 `<!-- MEMORY-SYSTEM-START -->` 标记，替换标记之间的内容
   - 如果不包含标记，在文件**顶部第一个一级标题之后**插入记忆系统指令块
   - **保留 CLAUDE.md 中的所有其他内容不变**

---

## Step 4: 输出完成报告

扫描创建的所有文件，统计大小，输出如下格式的报告:

```
✅ Claude 记忆系统初始化完成！

📁 创建的文件:
  .claude/memory/SUMMARY.md          (xxx bytes)
  .claude/memory/architecture.json   (xxx bytes)
  .claude/memory/conventions.json    (xxx bytes)
  .claude/memory/semantic-index.json (xxx bytes)
  .claude/memory/hotspot-map.json    (xxx bytes)
  .claude/memory/task-context.json   (xxx bytes)
  .claude/memory/changelog.json      (xxx bytes)
  .claude/memory/bugs-and-fixes.json (xxx bytes)
  .claude/memory/causality-graph.json(xxx bytes)
  CLAUDE.md                          (已更新/已创建)

📊 项目分析摘要:
  - 技术栈: <语言> + <框架>
  - 核心模块: <数量>个
  - 热点文件(>500行): <数量>个
  - 语义索引域: <数量>个

🧠 记忆系统设计:
  - 启动加载: ~3KB（仅 SUMMARY.md）
  - 详情存储: 按需 Grep 检索
  - 增长模型: 启动负载永远 O(1)

💡 下一步建议:
  1. 审查 architecture.json 中的模块描述是否准确
  2. 检查 conventions.json 是否符合团队规范
  3. 在 task-context.json 中添加当前进行中的任务
  4. 将 .claude/memory/ 加入版本控制（推荐）
  5. 根据项目特点补充 CLAUDE.md 中的关键规则
```

---

## 注意事项

- 所有文件使用 UTF-8 编码
- JSON 文件使用 2 空格缩进
- 日期格式统一使用 YYYY-MM-DD
- **不要在任何文件中使用占位模板**——所有内容必须来自实际扫描
- 如果某个扫描步骤失败（比如没有 package.json），优雅降级，用目录名作为项目名
- 热点文件扫描如果源文件不多，可以降低阈值到 300 行
- 如果项目已有 CLAUDE.md 中的项目特有规则（如 IPC 规则、弹窗规则等），注入时保留这些规则
- 对于不同技术栈的项目，`关键规则` 部分应自适应生成（如 Go 项目不需要 IPC 规则）
