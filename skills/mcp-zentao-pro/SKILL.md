---
name: zentao
description: 禅道(ZenTao) MCP大模型能力扩展包。提供跨项目的数据聚合视图、一句话生成任务、无缝报工(Log Effort)、自动状态流转等四组原生能力。
metadata: {"openclaw":{"emoji":"🚀","install":[{"id":"node","kind":"node","package":"@chenish/zentao-mcp-agent","bins":["zentao-mcp","zentao-cli"],"label":"Install ZenTao AI Assistant"}]}}
---

# ZenTao AI Assistant (zentao-mcp-agent)

## When to use this skill
当你（大语言模型）需要代替用户在禅道中查阅待办、分配任务、填报工时或操作任务状态机时，请**必须**启用此扩展包提供的 Tool 集合。依托我们的 MVC+RESTful 混动底层架构，你可以基于用户授权，越过繁杂的分页与项目界面，进行事项的统筹处理。

## 💡 AI 最佳实践指引 (For LLM AI)

作为 AI Assistant，当用户提出下述意图时，请严格按照指引调用底层提供的 4 大 Tool 工具：

### 1. 全视界地盘拉取 (Global Dashboard)
- **触发意图**：用户询问**“看看张三手头有什么活”**、**“最近哪些线上 Bug 延期了”**。
- **调用动作**：调用 `getDashboard`。
- **参数指南**：通过 `type`（task/bug/story）切换类型，通过 `status`（doing, wait, done）过滤状态。
  - ✅ `my tasks / my bugs / my stories`：查询当前登录用户的待办，完全可用。
  - ✅ `--assign <他人>`：支持跨人员查看官方指派视角，适合主管查岗或交叉核对。
  - ✅ `manage --users <成员列表>`：管理视角聚合查询，适合主管查看单人或团队当前任务池。

### 1.1 管理聚合视角补充规则 (Management Dashboard)
- **触发意图**：用户说**“帮我看张三今天要盯哪些任务”**、**“把我们组这几个人的任务、需求、Bug 汇总出来”**。
- **调用动作**：优先调用 `manage` 对应的管理聚合能力。
- **参数指南**：
  - `--users` 支持账号、中文名、多人逗号分隔。
  - `--type` 支持 `tasks/stories/bugs/all`。
  - 默认口径为 **当前未完成项 + 当日完成/关闭项**；若用户指定时间窗口，再追加 `--date-from` 与 `--date-to`。
  - `--status` 支持逗号分隔，如 `doing,wait`。
  - `--deadline-from`、`--deadline-to` 可用于筛选临期任务；`--overdue-only` 可用于只看已延期项。
  - 管理视角中的状态是跨类型语义映射，不是简单字面匹配：例如 `doing,wait,done` 会自动覆盖任务、需求、Bug 各自对应的待处理/已完成状态。
  - `--team-name <团队名>` 可直接复用本地缓存的团队成员列表，适合固定小组的日常巡检。
  - 输出中的“总计”会严格跟随当前 `--type` 查询口径，并额外展示过滤条件，避免将定向查询误读为全量统计。
  - `my tasks --assign <账号>` 与 `manage --users <成员>` 不可混为一谈：前者是官方指派地盘，后者是管理汇总视角。
  - 输出展示优先使用中文友好字段，方便用户直接阅读，也便于大模型后续做晨报、周报和催办摘要。

### 2. 对话式任务派发 (Chat-to-Task)
- **触发意图**：用户说**“把网关排查的活儿发给李四，给半天时间”**，但未指明具体项目或迭代时。
- **调用动作**：组合调用 `getProjects` -> `getActiveExecutions` -> (若无当期迭代则调用 `createExecution`) -> 最后发起 `createTask`。
- **参数指南**：务必先明确当前的迭代/执行 `execId`。如不确定，先查询项目列表及其下挂载的近期执行。如有必要跨月，可智能创建一个当月的新冲刺。派单时，可以直接传入真实的中文 `name`、`assignee` 和工时 `estimate`（默认2小时）。底层已内置自动修补禅道必填项和账号映射转换。若是“从需求拆分任务”，可直接传 `storyId + projectId`；CLI 会优先复用当月执行，若不存在则复制上个执行配置后自动创建。
- **补充约定**：创建任务时可直接传 `pri` 和 `desc`；若未传 `pri`，默认按 `3` 级优先级创建。

### 3. 一句话快捷报工 (Seamless Effort Logging)
- **触发意图**：用户说**“给 10452 任务登记 2 个小时的内容撰写工时”**。
- **调用动作**：调用 `addEstimate`。
- **参数指南**：必须带有精确的 `taskId`、耗时 `consumed` 以及备注 `work`。本接口底座已修复了禅道坑爹的报工幽灵丢失漏洞，直接确保工时准确入库！

### 4. 极简状态流转 (State Machine Control)
- **触发意图**：用户说**“那个 Bug 修完了，状态转给测试组长张三”**。
- **调用动作**：按实体类型调用 `updateTask`、`updateStory`、`updateBug` 工具组合。
- **检索补充**：若用户只给了任务名称而没有给 `taskId`，可先调用 `findTasksByName` 在当前账号、指定成员或团队范围内检索任务，拿到准确 ID 后再继续状态流转或报工。

### 5. 智能链接提取 (Smart Link Resolver)
- **触发意图**：用户在群聊或对话中甩出一条任意掺杂着链接的文本（如 **“帮我看看这个任务什么情况：http://zentao.yourcompany.com/task-view-123.html”**）。
- **调用动作**：提取包含网址在内的整段内容传给底层解析封装。你可以依此瞬间掌握该链接指向的任务/缺陷/需求等一切核心骨干状态。

### 6. 派发前负荷参考雷达 (Workload Radar)
- **触发意图**：用户在派发新任务前问**"李四目前有多少任务在手上，还有多少工时要做？"**，或者**"帮我看看张三和李四谁比较空"**。
- **调用动作**：调用底层 `getMemberLoad`，传入一个或多个成员账号/中文名，并发拉取其处理中任务与剩余工时后统一汇报。
- **重要原则**：这是纯参考数据，**不应自动阻断或拒绝** 派单操作。应将数据呈现给用户，由用户决定是否继续分派。
- **团队缓存补充**：若用户已保存团队别名，可优先使用 `--team-name` 复用团队成员列表。
- **口径补充**：该能力已复用管理视角底座，输出会显式标明是任务还是 Bug。
- **展示补充**：输出中应包含 `P1` 未完成任务数量、任务平均进度，以及每条任务的单项进度百分比，帮助用户快速判断团队负荷质量。

### 7. 停滞单据排查 (Stagnant Tasks Patrol)
- **触发意图**：用户询问**"张三有什么任务一直没动"** 或 **"帮我看看团队里有没有什么任务超过一周没人管"**。
- **调用动作**：提取目标成员列表与停滞天数阈值（默认3天），调用 `getStagnantTasks` 返回按停滞时长排序的停滞单据清单。

### 8. 晨会综合沙盘 (Morning Standup Radar)
- **触发意图**：用户说**"帮我出今天的晨会通报"** 或 **"看看今天团队有哪些紧急的事项"**，并提供团队成员列表。
- **调用动作**：调用 `getMorningCheck`，传入团队成员列表，返回三类清单：`overdue`（已超期）、`dueSoon`（今明到期）、`highPriority`（高优悬空）。
- **输出要求**：请将三类数据以清晰简明的格式呈现，使用 emoji 区分风险等级（🔴超期 / 🟡临期 / 🟠高优），方便用户直接转发晨会通报。
- **团队缓存补充**：固定团队可先通过 `team save` 建立别名，后续晨会直接使用 `--team-name`。
- **口径补充**：该能力已复用管理视角底座，预警清单中会显式区分任务、需求、Bug。
- **过滤补充**：无截止日期的需求默认不纳入晨会预警，避免将弱时效事项误判为晨会风险。
- **参数补充**：支持通过 `--pri-max` 调整晨会关注的高优阈值，例如传 `1` 时仅保留 `P1` 事项；输出中同时展示粗粒度进度百分比，便于快速判断推进程度。

### 9. 自动化周报摘要 (Weekly Synthesis)
- **触发意图**：用户说**"帮我出本周周报素材"**、**"汇总团队这周交付了哪些重点事项"**，并提供团队成员列表或团队名。
- **调用动作**：调用 `getWeeklySynthesis`，传入团队成员列表与时间窗，返回两类核心清单：`stories`（高优需求交付）与 `bugs`（重大缺陷修复），同时附带成员维度交付汇总。
- **输出要求**：优先展示统计范围、本周截止窗口、`总交付 / 高优交付 / 本周待完成任务` 与成员交付汇总；仅在用户明确需要逐条清单时，再补充任务、需求、Bug 详情。
- **团队缓存补充**：固定团队优先通过 `team save` 建立别名，周报直接复用 `--team-name`。
- **参数补充**：支持 `--date-from`、`--date-to` 自定义统计窗口，支持 `--pri-max` 收敛到更高价值的交付事项；Bug 严重程度默认跟随该阈值，`--severity-max` 仅保留为兼容补充参数。
- **视图补充**：支持 `--view summary|full`，默认使用 `summary`。当用户只需要给大模型投喂底稿时，直接走默认值；当用户明确需要逐条清单时，再切换为 `full`。
- **周窗口补充**：周报会按自然周自动识别周一到周日；即使在周四、周五、周六查询，也会自动纳入本周周末截止但尚未完成的任务。

---
## 💻 安全与环境依赖说明 (Environment & Security)

> **⚠️ 运行须知：** 
> 这是一个受限的主流大模型端桥接应用。为保障您的操作合规，本扩展不会在未授权状态下进行任何风险调优或系统篡改。

### 1. 安装与依赖引入

如果您需要在本地命令行使用或验证此工具，可以进行全局安装或扩展装载：
```bash
# 全局安装 CLI 工具
npm install -g @chenish/zentao-mcp-agent

# 或者通过 npx 挂载大模型工具 (如平台需要)
npx skills add @chenish/zentao-mcp-agent
```

作为环境依赖底座，首次使用必须执行授权鉴权：
```bash
zentao-cli login --url "https://xxxxx.com/zentao" --account "<账号>" --pwd "<密码>"
```

### 2. 命令行全量调用实例

本插件已将极其复杂的禅道 API 与路由封装为极简的指令集，可用作日常 CLI：

**🔥 地盘全视界 (My Dashboard)**
```bash
# 基础：默认拉取指派给我的待办任务
zentao-cli my tasks
# 分类：拉取指派给我的缺陷清单
zentao-cli my bugs
# 分类：拉取指派给我的需求清单 (聚合：一键获取我名下的业务需求)
zentao-cli my stories
# 管理视角：跨权限查看张三地盘上的所有任务 (查岗：跨项目查阅张三的任务列表)
zentao-cli my tasks --assign 张三
# 精准过滤：查看张三目前正在进行中的任务 (过滤：精确提取张三进行中的代办)
zentao-cli my tasks --assign 张三 --status doing
# 管理聚合视角：汇总张三当前相关的任务、需求、缺陷
zentao-cli manage --users 张三
# 管理聚合视角：只看团队成员当前任务池
zentao-cli manage --users 张三,李四 --type tasks
# 管理聚合视角：只看单人的缺陷
zentao-cli manage --users 张三 --type bugs
# 管理聚合视角：只看进行中的任务
zentao-cli manage --users 张三 --type tasks --status doing
# 管理聚合视角：同时看进行中与待开始任务
zentao-cli manage --users 张三 --type tasks --status doing,wait
# 团队缓存视角：直接按团队名查询
zentao-cli manage --team-name "规划组"
# 时间窗管理视角：补入指定日期内完成/关闭的任务
zentao-cli manage --users 张三,李四 --date-from 2026-03-12 --date-to 2026-03-12
# 临期任务视角：筛出周末前到期任务
zentao-cli manage --users 张三,李四 --type tasks --deadline-to 2026-03-16
# 风险视角：只看已延期任务
zentao-cli manage --users 张三,李四 --type tasks --overdue-only
# 团队缓存管理
zentao-cli team save --name "规划组" --users "张三,李四,王五"
zentao-cli team list
zentao-cli team show --name "规划组"
zentao-cli team delete --name "规划组"
# 团队缓存晨会：只看 P1 高优事项
zentao-cli morning-check --team-name "规划组" --pri-max 1
# 团队缓存负荷：查看 P1 数量与任务进度
zentao-cli load --team-name "规划组"
# 团队缓存周报：输出本周高优需求与重大缺陷修复
zentao-cli weekly-synthesis --team-name "规划组"
# 自定义时间窗周报
zentao-cli weekly-synthesis --team-name "规划组" --date-from 2026-03-09 --date-to 2026-03-13 --pri-max 1
# 摘要模式周报：仅输出统计与重点摘要
zentao-cli weekly-synthesis --team-name "规划组" --view summary
# 详情模式周报：输出完整任务、需求、Bug 清单
zentao-cli weekly-synthesis --team-name "规划组" --view full
```

**🔥 对话派单化与执行自治 (Projects & Chat-to-Task)**
```bash
# 列出活跃中的项目总库 (新增能力)
zentao-cli projects
# 获取某项目下活跃的冲刺/迭代 ID 列表 (历史意图示例，当前 CLI 参数请使用 --projectId)
zentao-cli executions --project 577
# 获取某项目下活跃的冲刺/迭代 ID 列表 (当前 CLI 参数)
zentao-cli executions --projectId 577
# 仅看进行中的迭代
zentao-cli executions --projectId 577 --status doing
# 当期无迭代时：自动新建一个默认7天的本月新冲刺阶段
zentao-cli execution create --projectId 577 --name "2026年3月常规迭代"
# 显式指定起止日期创建迭代
zentao-cli execution create --projectId 577 --name "2026年3月常规迭代" --begin "2026-03-17" --end "2026-03-24"
# 指定工作日天数
zentao-cli execution create --projectId 577 --name "2026年3月常规迭代" --days 6
# 瞬时派单：时间与工时全部由底层静默注入默认值
zentao-cli task create --execId 123 --name "网关熔断排查" --assign "张三"
# 带优先级与描述派单
zentao-cli task create --execId 123 --name "网关熔断排查" --assign "张三" --pri 2 --desc "补充任务描述"
# 精细派单：明确指定 8 小时预估工时和特定截止日期
zentao-cli task create --execId 123 --name "全量压测" --assign "李四" --estimate 8 --deadline "2026-03-20"
# 指定预估工时，截止日期走默认值
zentao-cli task create --execId 123 --name "接口联调" --assign "张三" --estimate 4
# 从需求拆分任务：自动复用当月执行，必要时复制上个执行后建任务
zentao-cli task create --storyId 12072 --projectId 281 --name "数据库改造脚本适配" --assign "张三" --estimate 8 --pri 2
# 从需求拆分任务：显式指定执行模板与新执行名称
zentao-cli task create --storyId 12072 --projectId 281 --templateExecId 5825 --executionName "2026年03月常规迭代" --name "数据库改造脚本适配" --assign "张三" --desc "从需求拆分的研发任务"
```

**🔥 单点状态机 (State Machine Control)**
```bash
# 状态扭转：仅将任务状态标记为已完成
zentao-cli task update --taskId 123 --status done
# 先按名称找任务 ID
zentao-cli task find --name "网关排查"
# 在指定成员范围内按名称找任务
zentao-cli task find --name "接口联调" --owner zhangsan,lisi
# 在团队缓存范围内按名称找任务
zentao-cli task find --name "接口联调" --team-name "规划组"
# 启动任务：切换为进行中
zentao-cli task update --taskId 123 --status doing --comment "开始处理"
# 关闭任务：验证完成后关闭
zentao-cli task update --taskId 123 --status closed --comment "验证通过，执行关闭"
# 任务转交：仅将任务丢给张三处理
zentao-cli task update --taskId 123 --assign 张三
# 复合协同：完成、转交、加备注一气呵成
zentao-cli task update --taskId 123 --status done --assign 张三 --comment "代码已提交，转交测试验证"
# 关闭需求：将需求直接关闭
zentao-cli story update --storyId 12072 --status closed --comment "需求已验收完成"
# 激活需求：将已关闭需求重新激活
zentao-cli story update --storyId 14526 --status active --comment "重新激活继续推进"
# 转交需求：将需求交给张三继续跟进
zentao-cli story update --storyId 12072 --assign 张三 --comment "转交继续跟进"
# 解决缺陷：将 Bug 标记为已解决
zentao-cli bug update --bugId 11071 --status done --comment "缺陷已修复完成"
# 关闭缺陷：验证通过后关闭 Bug
zentao-cli bug update --bugId 11071 --status closed --comment "验证通过，关闭缺陷"
# 重开缺陷：继续跟踪处理
zentao-cli bug update --bugId 11071 --status active --comment "重新激活继续跟踪"
# 转交缺陷：将 Bug 交给张三继续跟进
zentao-cli bug update --bugId 11071 --assign 张三 --comment "转交继续跟进"
```

**🔥 一句话报工作业 (Log Effort)**
```bash
# 极简报工：给 69704 任务快速登记 2 小时消耗
zentao-cli task effort --taskId 69704 --consumed 2
# 详尽报工：登记耗时并追加详细的研发日志
zentao-cli task effort --taskId 69704 --consumed 2.5 --desc "完成了核心业务逻辑的编写"
```

> 当前 `task effort` CLI 已稳定支持 `--taskId + --consumed`，可选 `--desc`；仅写说明不填耗时仍属于后续增强目标。

**当前已知限制**
- `task effort --taskId <id> --desc "..."` 这种仅写说明不填耗时的形态，在当前禅道环境中页面历史不会稳定落备注。
- `story update --storyId <id> --status active` 在当前禅道环境中尚未稳定生效，需求激活链路仍待后续排查。

---

## 🤝 欢迎提出需求与共建

如果你对本插件有任何新的期待，或者希望由社区帮你加入更多针对禅道系统的定制化、自动化功能接口，我们非常**愿意并且乐意为大家拓展功能**！
欢迎随时前往 [GitHub Repository](https://github.com/chenish/mcp-zentao-pro/issues) 提交你的 Issue 需求或者 Bug 报错。

