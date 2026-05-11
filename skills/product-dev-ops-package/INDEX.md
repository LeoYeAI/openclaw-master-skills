# Product DevOps Team Skill

> 产品研发运营协作体系 v3.2 - 四角色协作框架

## 快速导航

### 核心文档

| 文档 | 说明 |
|------|------|
| [SKILL.md](./SKILL.md) | Skill 主文档：角色识别规则、状态机、命令速查 |
| [README.md](./README.md) | 项目说明和使用指南 |

### 四角色 Agents（⭐ v3.2 新增，解决角色不一致）

| 角色 | 人设文件 | 核心职责 |
|------|---------|---------|
| 产品经理（王校长）| [agents/product-manager.md](./agents/product-manager.md) | 守护 Why，主持研讨，版本归档 |
| 架构师 | [agents/architect.md](./agents/architect.md) | API 先行，技术方案，契约检查 |
| 开发助手 | [agents/dev-assistant.md](./agents/dev-assistant.md) | 自治开发，自测，文档同步 |
| 运营经理 | [agents/ops-manager.md](./agents/ops-manager.md) | 早期介入，权限设计，上线计划 |

### 指令 Commands

| 指令 | 文档 | 说明 |
|------|------|------|
| `/开工 [项目名]` | [commands/start.md](./commands/start.md) | 启动项目 + 结构化访谈 |
| `/研讨` | [commands/workshop.md](./commands/workshop.md) | 四角色对齐研讨会 |
| `/冻结` | [commands/freeze.md](./commands/freeze.md) | Why 冻结，开发自治启动 |
| `/继续` | [commands/resume.md](./commands/resume.md) | 继续上次中断 |
| `/状态` | [commands/status.md](./commands/status.md) | 项目状态快照 |
| `/模式` | [commands/mode.md](./commands/mode.md) | 查看/切换协作模式 |
| `/归档 [版本]` | [commands/archive.md](./commands/archive.md) | 版本归档 |

### 模板 Templates

| 类别 | 路径 | 用途 |
|------|------|------|
| PRD | [templates/prd/](./templates/prd/) | 产品需求文档、功能规格、CHANGELOG |
| API | [templates/api/](./templates/api/) | OpenAPI、ADR |
| 研讨会 | [templates/workshop/](./templates/workshop/) | 研讨会记录、外部访谈 |
| 开发 | [templates/development/](./templates/development/) | 站会记录 |
| 测试 | [templates/test/](./templates/test/) | 测试用例 |
| Review | [templates/review/](./templates/review/) | 评审模板 |

---

## 目录结构

```
product-dev-ops-team/
├── SKILL.md                          # 技能主文档（角色规则、状态机）
├── INDEX.md                          # 本文件（快速导航）
├── README.md                         # 使用说明
├── agents/                           # ⭐ 角色人设和行为规则（v3.2 新增）
│   ├── product-manager.md
│   ├── architect.md
│   ├── dev-assistant.md
│   └── ops-manager.md
├── commands/                         # 指令定义
│   ├── start.md                      # /开工
│   ├── workshop.md                   # /研讨
│   ├── freeze.md                     # /冻结
│   ├── resume.md                     # /继续
│   ├── status.md                     # /状态
│   ├── mode.md                       # /模式
│   └── archive.md                    # /归档
└── templates/                        # 文档模板
    ├── prd/
    ├── api/
    ├── workshop/
    ├── development/
    ├── test/
    └── review/
```

---

## v3.2 更新说明

| 变更 | 说明 |
|------|------|
| ✅ 新增 `agents/` 目录 | 四个角色文件，定义人设、说话风格、行为规则、禁止事项 |
| ✅ 新增 `/开工` 命令文件 | 完整的6步访谈流程 + 目录初始化 |
| ✅ 新增 `/模式` 命令文件 | 标准/完整模式切换说明 |
| ✅ 新增 `/归档` 命令文件 | 归档前检查 + 发布说明 + 文档整理流程 |
| ✅ 优化 SKILL.md | 加入角色识别规则、发言格式规范、项目状态机 |

---

## 扩展技能

**strategy-consultant**（战略顾问技能，可选）：
- 适用于新业务方向、融资、高竞争市场
- 与本技能集成，为 `/研讨` 提供外部洞察输入
- 详见 SKILL.md 中的"与战略顾问的集成"章节

## 版本

v3.2.0 - 四角色行为规则定义，解决角色不一致问题
