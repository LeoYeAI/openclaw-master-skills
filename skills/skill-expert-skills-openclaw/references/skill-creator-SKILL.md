---
name: skill-creator
description: 创建高效 Skill 的指南。当用户想要创建新 Skill（或更新现有 Skill）以通过专业知识、工作流或工具集成扩展 Claude 的能力时，应使用此 Skill。
license: 完整条款见 LICENSE.txt
---

# Skill 创建者

本 Skill 为创建高效 Skill 提供指导。

## 关于 Skill

Skill 是模块化的、自包含的包，通过提供专业知识、工作流和工具来扩展 Claude 的能力。可以将它们视为特定领域或任务的“入职指南”——它们将 Claude 从一个通用助手转变为配备了程序化知识的专业助手，而任何模型都无法完全具备这些知识。

### Skill 提供的内容

1. 专业工作流 - 针对特定领域的多步流程
2. 工具集成 - 处理特定文件格式或 API 的指令
3. 领域专家知识 - 公司特定的知识、Schema、业务逻辑
4. 绑定的资源 - 用于复杂和重复任务的脚本、参考资料和素材

## 核心原则

### 简洁是关键

上下文窗口是一种公共资源。Skill 与 Claude 所需的其他所有内容（系统提示词、对话历史、其他 Skill 的元数据以及实际的用户请求）共享上下文窗口。

**默认假设：Claude 已经非常聪明。** 只添加 Claude 尚未掌握的上下文。质疑每一条信息：“Claude 真的需要这个解释吗？”以及“这一段话值得它消耗的 token 成本吗？”

优先使用简练的示例，而非冗长的解释。

### 设置适当的自由度

根据任务的脆弱性和多变性匹配特定程度：

**高自由度（基于文本的指令）**：当多种方法都有效、决策取决于具体语境或启发式方法引导流程时使用。

**中自由度（带有参数的伪代码或脚本）**：当存在首选模式、允许某些变化或配置影响行为时使用。

**低自由度（特定的脚本，极少参数）**：当操作脆弱且易错、一致性至关重要或必须遵循特定顺序时使用。

将 Claude 想象成在路径上探索：狭窄的独木桥和悬崖需要特定的护栏（低自由度），而开阔的田野则允许许多路线（高自由度）。

### Skill 的剖析

每个 Skill 由一个必需的 SKILL.md 文件和可选的绑定资源组成：

```
skill-name/
├── SKILL.md (必需)
│   ├── YAML frontmatter 元数据 (必需)
│   │   ├── name: (必需)
│   │   └── description: (必需)
│   └── Markdown 指令 (必需)
└── 绑定的资源 (可选)
    ├── scripts/          - 可执行代码 (Python/Bash 等)
    ├── references/       - 旨在根据需要加载到上下文中的文档
    └── assets/           - 用于输出的文件 (模板、图标、字体等)
```

#### SKILL.md (必需)

每个 SKILL.md 由以下部分组成：

- **Frontmatter** (YAML)：包含 `name` 和 `description` 字段。这是 Claude 读取以决定何时使用该 Skill 的唯一字段，因此在描述该 Skill 是什么以及何时应使用它时，清晰且全面非常重要。
- **Body** (Markdown)：使用该 Skill 的指令和指导。仅在 Skill 触发后（如果触发）才加载。

#### 绑定的资源 (可选)

##### 脚本 (`scripts/`)

用于需要确定性可靠性或被反复重写的任务的可执行代码 (Python/Bash 等)。

- **何时包含**：当同一段代码被反复重写，或需要确定性的可靠性时。
- **示例**：用于 PDF 旋转任务的 `scripts/rotate_pdf.py`。
- **优点**：节省 Token、确定性、无需加载到上下文中即可执行。
- **注意**：脚本可能仍需要被 Claude 读取以进行补丁修改或特定环境的调整。

##### 参考资料 (`references/`)

旨在根据需要加载到上下文中，以辅助 Claude 的流程和思考的文档和参考材料。

- **何时包含**：对于 Claude 在工作时应参考的文档。
- **示例**：用于财务 Schema 的 `references/finance.md`，用于公司 NDA 模板的 `references/mnda.md`，用于公司政策的 `references/policies.md`，用于 API 规范的 `references/api_docs.md`。
- **用例**：数据库 Schema、API 文档、领域知识、公司政策、详细的工作流指南。
- **优点**：保持 SKILL.md 精简，仅在 Claude 确定需要时才加载。
- **最佳实践**：如果文件很大（>10k 字），请在 SKILL.md 中包含 grep 搜索模式。
- **避免重复**：信息应存在于 SKILL.md 或参考文件中，而不是两者都有。除非确实是 Skill 的核心，否则优先将详细信息放在参考文件中——这既保持了 SKILL.md 的精简，又使信息在不占用上下文窗口的情况下可被发现。在 SKILL.md 中仅保留必要的程序性指令和工作流指导；将详细的参考材料、Schema 和示例移动到参考文件中。

##### 素材 (`assets/`)

不旨在加载到上下文中，而是用于 Claude 产生的输出文件。

- **何时包含**：当 Skill 需要用于最终输出的文件时。
- **示例**：用于品牌素材的 `assets/logo.png`，用于 PowerPoint 模板的 `assets/slides.pptx`，用于 HTML/React 样板的 `assets/frontend-template/`，用于排版的 `assets/font.ttf`。
- **用例**：模板、图像、图标、样板代码、字体、被复制或修改的样本文档。
- **优点**：将输出资源与文档分离，使 Claude 能够使用文件而无需将其加载到上下文中。

#### Skill 中不应包含的内容

一个 Skill 应仅包含直接支持其功能的必要文件。不要创建无关的文档或辅助文件，包括：

- README.md
- INSTALLATION_GUIDE.md (安装指南)
- QUICK_REFERENCE.md (快速参考)
- CHANGELOG.md (变更日志)
- 等等。

Skill 应仅包含 AI 助手完成手头工作所需的信息。它不应包含关于创建过程的辅助背景、设置和测试程序、面向用户的文档等。创建额外的文档文件只会增加杂乱和混乱。

### 渐进式披露设计原则 (Progressive Disclosure)

Skill 使用三层加载系统来高效管理上下文：

1. **元数据 (name + description)** - 始终在上下文中 (~100 字)
2. **SKILL.md 正文** - 在 Skill 触发时 (<5k 字)
3. **绑定的资源** - 根据 Claude 的需要 (无限制，因为脚本可以在不读取到上下文窗口的情况下执行)

#### 渐进式披露模式

保持 SKILL.md 正文精简，并控制在 500 行以内，以最小化上下文膨胀。在接近此限制时，将内容拆分为单独的文件。在将内容拆分到其他文件时，务必在 SKILL.md 中引用它们，并清晰描述何时读取它们，以确保 Skill 的阅读者知道它们的存在以及何时使用。

**核心原则：** 当一个 Skill 支持多种变体、框架或选项时，在 SKILL.md 中仅保留核心工作流和选择指导。将特定变体的详细信息（模式、示例、配置）移动到单独的参考文件中。

**模式 1：带有参考资料的高阶指南**

```markdown
# PDF 处理

## 快速开始

使用 pdfplumber 提取文本：
[代码示例]

## 高级功能

- **表单填充**：完整指南见 [FORMS.md](FORMS.md)
- **API 参考**：所有方法见 [REFERENCE.md](REFERENCE.md)
- **示例**：常见模式见 [EXAMPLES.md](EXAMPLES.md)
```

Claude 仅在需要时加载 FORMS.md、REFERENCE.md 或 EXAMPLES.md。

**模式 2：按领域组织**

对于拥有多个领域的 Skill，按领域组织内容以避免加载无关上下文：

```
bigquery-skill/
├── SKILL.md (概览与导航)
└── reference/
    ├── finance.md (收入、账单指标)
    ├── sales.md (机会、流水)
    ├── product.md (API 使用、功能)
    └── marketing.md (活动、归因)
```

当用户询问销售指标时，Claude 仅读取 sales.md。

同样，对于支持多个框架或变体的 Skill，按变体组织：

```
cloud-deploy/
├── SKILL.md (工作流 + 服务商选择)
└── references/
    ├── aws.md (AWS 部署模式)
    ├── gcp.md (GCP 部署模式)
    └── azure.md (Azure 部署模式)
```

当用户选择 AWS 时，Claude 仅读取 aws.md。

**模式 3：条件性详情**

显示基础内容，链接到高级内容：

```markdown
# DOCX 处理

## 创建文档

使用 docx-js 创建新文档。见 [DOCX-JS.md](DOCX-JS.md)。

## 编辑文档

对于简单的编辑，直接修改 XML。

**对于修订跟踪**：见 [REDLINING.md](REDLINING.md)
**对于 OOXML 详情**：见 [OOXML.md](OOXML.md)
```

Claude 仅在用户需要这些功能时读取 REDLINING.md 或 OOXML.md。

**重要准则：**

- **避免深层嵌套引用** - 保持参考资料距离 SKILL.md 只有一层。所有参考文件都应直接链接自 SKILL.md。
- **结构化较长的参考文件** - 对于超过 100 行的文件，请在顶部包含目录，以便 Claude 在预览时能看到全文范围。

## Skill 创建流程

Skill 创建涉及以下步骤：

1. 通过具体示例理解 Skill
2. 规划可复用的 Skill 内容（脚本、参考资料、素材）
3. 初始化 Skill（运行 init_skill.py）
4. 编辑 Skill（实施资源并编写 SKILL.md）
5. 打包 Skill（运行 package_skill.py）
6. 基于实际使用进行迭代

按顺序遵循这些步骤，仅在有明确理由说明其不适用时才跳过。

### 步骤 1：通过具体示例理解 Skill

只有在 Skill 的使用模式已经清晰理解时，才跳过此步骤。即使在处理现有 Skill 时，它仍然具有价值。

要创建一个高效的 Skill，请清晰地理解如何使用该 Skill 的具体示例。这种理解可以来自直接的用户示例，也可以来自经用户反馈验证的生成示例。

例如，在构建 image-editor Skill 时，相关问题包括：

- “image-editor Skill 应支持哪些功能？编辑、旋转，还有别的吗？”
- “你能举一些如何使用此 Skill 的示例吗？”
- “我可以想象用户会问‘帮我去除这张照片的红眼’或‘旋转这张照片’。你还想象了其他使用此 Skill 的方式吗？”
- “用户会说什么话来触发这个 Skill？”

为了避免让用户感到负担，避免在一个消息中询问过多问题。从最重要的问题开始，并根据需要进行跟进以提高效率。

当对 Skill 应支持的功能有了清晰的认识时，结束此步骤。

### 步骤 2：规划可复用的 Skill 内容

要将具体示例转化为高效的 Skill，请通过以下方式分析每个示例：

1. 考虑如何从头开始执行示例
2. 识别在重复执行这些工作流时，哪些脚本、参考资料和素材会有所帮助

示例：在构建 `pdf-editor` Skill 以处理“帮我旋转这个 PDF”之类的查询时，分析表明：

1. 旋转 PDF 每次都需要重写相同的代码
2. 在 Skill 中存储一个 `scripts/rotate_pdf.py` 脚本会很有帮助

示例：在为“帮我做一个待办事项应用”或“帮我做一个仪表盘来跟踪我的步数”之类的查询设计 `frontend-webapp-builder` Skill 时，分析表明：

1. 编写前端 Web 应用每次都需要相同的 HTML/React 样板
2. 在 Skill 中存储一个包含样板 HTML/React 项目文件的 `assets/hello-world/` 模板会很有帮助

示例：在构建 `big-query` Skill 以处理“今天有多少用户登录？”之类的查询时，分析表明：

1. 查询 BigQuery 每次都需要重新发现表 Schema 和关系
2. 在 Skill 中存储一个记录表 Schema 的 `references/schema.md` 文件会很有帮助

要确立 Skill 的内容，请分析每个具体示例，列出要包含的可复用资源清单：脚本、参考资料和素材。

### 步骤 3：初始化 Skill

此时，是时候实际创建 Skill 了。

仅当正在开发的 Skill 已经存在，并且需要迭代或打包时，才跳过此步骤。在这种情况下，继续下一步。

当从头开始创建新 Skill 时，始终运行 `init_skill.py` 脚本。该脚本可以方便地生成一个新的模板 Skill 目录，自动包含 Skill 所需的一切，使 Skill 创建流程更加高效和可靠。

用法：

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

该脚本：

- 在指定路径创建 Skill 目录
- 生成带有正确 frontmatter 和 TODO 占位符的 SKILL.md 模板
- 创建示例资源目录：`scripts/`、`references/` 和 `assets/`
- 在每个目录中添加可以自定义或删除的示例文件

初始化后，根据需要自定义或删除生成的 SKILL.md 和示例文件。

### 步骤 4：编辑 Skill

在编辑（新生成的或现有的）Skill 时，请记住该 Skill 是为了让另一个 Claude 实例使用而创建的。包含对 Claude 有益且非显而易见的信息。考虑哪些程序化知识、领域特定细节或可复用素材将帮助另一个 Claude 实例更有效地执行这些任务。

#### 学习成熟的设计模式

根据你的 Skill 需求咨询这些有用的指南：

- **多步流程**：参见 references/workflows.md，了解顺序工作流和条件逻辑
- **特定输出格式或质量标准**：参见 references/output-patterns.md，了解模板和示例模式

这些文件包含了高效 Skill 设计的既定最佳实践。

#### 从可复用的 Skill 内容开始

要开始实施，请从上面识别出的可复用资源开始：`scripts/`、`references/` 和 `assets/` 文件。请注意，此步骤可能需要用户输入。例如，在实施 `brand-guidelines` Skill 时，用户可能需要提供要存储在 `assets/` 中的品牌素材或模板，或者要存储在 `references/` 中的文档。

添加的脚本必须通过实际运行来进行测试，以确保没有错误且输出符合预期。如果有很多类似的脚本，只需测试一个具有代表性的样本，以在平衡完成时间的同时确保所有脚本都能正常工作的信心。

删除任何 Skill 不需要示例文件和目录。初始化脚本在 `scripts/`、`references/` 和 `assets/` 中创建示例文件以演示结构，但大多数 Skill 不会全部需要它们。

#### 更新 SKILL.md

**写作指南**：始终使用命令式/不定式形式。

##### Frontmatter

使用 `name` 和 `description` 编写 YAML frontmatter：

- `name`: Skill 名称
- `description`: 这是 Skill 的主要触发机制，帮助 Claude 理解何时使用它。
  - 包含 Skill 的功能以及使用它的特定触发因素/背景。
  - 在这里包含所有的“何时使用”信息 - 而不是在正文里。正文仅在触发后才加载，因此正文中的“何时使用此 Skill”部分对 Claude 没有帮助。
  - `docx` Skill 的描述示例：“全面的文档创建、编辑和分析，支持修订跟踪、批注、格式保留和文本提取。当 Claude 需要处理专业文档 (.docx 文件) 以用于：(1) 创建新文档、(2) 修改或编辑内容、(3) 处理修订跟踪、(4) 添加批注或任何其他文档任务时使用。”

不要在 YAML frontmatter 中包含任何其他字段。

##### 正文 (Body)

编写使用该 Skill 及其绑定资源的指令。

### 步骤 5：打包 Skill

一旦 Skill 开发完成，必须将其打包成可分发的 .skill 文件并分享给用户。打包流程会自动先验证 Skill，以确保其符合所有要求：

```bash
scripts/package_skill.py <path/to/skill-folder>
```

可选的输出目录规范：

```bash
scripts/package_skill.py <path/to/skill-folder> ./dist
```

打包脚本将：

1. **自动验证** Skill，检查：

   - YAML frontmatter 格式和必需字段
   - Skill 命名约定和目录结构
   - 描述的完整性和质量
   - 文件组织和资源引用

2. 如果验证通过，则**打包** Skill，创建一个以 Skill 命名的 .skill 文件（例如，`my-skill.skill`），其中包含所有文件并保持正确的目录结构以便分发。.skill 文件是一个扩展名为 .skill 的 zip 文件。

如果验证失败，脚本将报告错误并退出，而不创建包。修复任何验证错误并再次运行打包命令。

### 步骤 6：迭代

在测试 Skill 后，用户可能会请求改进。通常这发生在刚使用完 Skill 之后，此时对 Skill 的表现还有新鲜的印象。

**迭代工作流：**

1. 在实际任务中使用 Skill
2. 注意遇到的困难或低效之处
3. 识别应如何更新 SKILL.md 或绑定的资源
4. 实施更改并再次测试
