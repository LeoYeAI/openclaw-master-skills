---
name: ai-talent-hunter
description: 从 GitHub 找到最匹配的技术人才，生成个性化触达话术。适用于招聘工程师、寻找技术合伙人、猎头交付候选人等场景。
permissions:
  filesystem:
    read:
      - prompts/jd_parser_prompt.md  # Step 0: JD parsing prompt template for translating job requirements to GitHub search queries
      - prompts/pitch_writer_prompt.md  # Step 3: outreach message generation prompt template for personalized candidate engagement
      - data/candidates.jsonl  # Cross-search deduplication: avoid recommending previously selected candidates
    write:
      - data/candidates.jsonl  # Persist search results and candidate selection status
  env:
    - GITHUB_TOKEN  # Required: GitHub Personal Access Token for public API access (user-provided, stored in local .env)
config:
  reads:
    - prompts/jd_parser_prompt.md
    - prompts/pitch_writer_prompt.md
    - data/candidates.jsonl
  writes:
    - data/candidates.jsonl
  env:
    - GITHUB_TOKEN
---

# GitHub 人才猎手 (GitHub Talent Hunter)

**从 GitHub 真实代码里找技术人才** — 不看简历看代码，不靠吹嘘靠项目。为 HR、猎头、技术管理者和创业者设计的智能招聘工具。

---

## 🔒 安全声明

**OpenClaw 安全扫描可能会提示 "Suspicious"，这是正常的**，原因如下：

1. **需要 GitHub Token**：本 skill 使用 GitHub 公开 API 搜索开发者，需要用户自行配置 Token（详见"安全配置"章节）
2. **包含 Prompt 模板**：`prompts/` 文件夹包含 JD 解析和话术生成的 Prompt 模板，这是功能需要，不是恶意 prompt injection
3. **不自动发送消息**：本 skill **不会自动发送任何邮件或消息**，所有触达话术仅作草稿，需人工审核后手动发送

**合规保证**：
- ✅ 仅使用 GitHub 公开 API 和公开数据
- ✅ Human-in-the-Loop：用户逐一确认候选人，不批量骚扰
- ✅ Token 存储在本地 `.env` 文件（不上传到 git）
- ✅ 生成的触达话术需人工审核，不自动执行
- ❌ 不购买/爬取私密数据
- ❌ 不绕过任何反爬机制

---

## 核心能力

1. **基于真实代码搜人**：直接从 GitHub 代码仓库搜索——找到的是候选人真正做过的项目，不是简历上可以美化的内容，而是实打实写过的代码。传统招聘平台搜不到的技术关键词（如 RocksDB、LangChain、vLLM），在这里能精准命中
2. **智能排序**：按技术匹配度、活跃度、可联系性等维度自动排序，优先展示最值得联系的人
3. **全球定位**：支持按国家、省份、城市筛选候选人，也可不限地区搜索远程人才
4. **人工筛选**：候选人列表由你逐一确认，避免大撒网式骚扰
5. **个性化触达**：根据候选人真实项目经历生成定制话术，让对方感到"你真的了解我"

---

## 触发场景

**用户可能这样说**：

- HR："帮我找几个做 RAG 的 Python 工程师，深圳的"
- CEO："想找个 Rust 大牛来当技术合伙人"
- 猎头："客户要招 Next.js 前端，北京，给我 5 个候选人"
- CTO："帮我搜一下做分布式存储的 C++ 工程师，要最近半年活跃的"
- 创业者："我们在做 AI Agent，想找几个有 LangChain 经验的人聊聊"

**Skill 自动执行**：
1. 理解招聘需求 → 生成搜索条件（Step 0）
2. 从 GitHub 搜索候选人 → 构建画像并排序（Step 1）
3. 展示候选人列表 → 你来选人（Step 1.5）
4. 展示选中候选人的完整信息 → 最终确认（Step 2）
5. 为确认的候选人生成个性化触达话术（Step 3）

---

## 执行流程

### Step 0: 智能解析（JD Parser）

**目标**：将用户的口语化需求转译为 GitHub 搜索参数。

**操作**：
1. 读取 `prompts/jd_parser_prompt.md`
2. 将用户输入代入 Prompt，生成标准化 JSON
3. 输出格式：
   ```json
   {
     "search_queries": [
       "language:c++ rocksdb pushed:>2025-01-01",
       "language:c++ leveldb lsm-tree pushed:>2025-01-01"
     ],
     "target_languages": ["C++"],
     "ecosystem_keywords": ["rocksdb", "leveldb", "lsm-tree"],
     "location": "china",
     "reasoning": "将'RocksDB 相关'转译为 rocksdb + leveldb + lsm-tree 生态"
   }
   ```

**约束规则**：详见 `prompts/jd_parser_prompt.md`（包含查询生成、活跃度过滤、地理位置处理、负向排除等规则）。

---

### Step 1: 搜索（GitHub Search）

**目标**：从 GitHub 搜索候选人，构建完整画像并全局排序。

**操作**：
```bash
cd ~/.openclaw/workspace/skills/ai-talent-hunter

# 首次搜索（宽松位置匹配，默认）
python scripts/github_search.py \
  --queries "language:c++ rocksdb pushed:>2025-01-01" "language:c++ leveldb lsm-tree pushed:>2025-01-01" \
  --jd-keywords "rocksdb,lsm-tree,storage" \
  --jd-language "C++" \
  --location "shenzhen" \
  --target 20 \
  -o results.json

# 首次搜索（严格位置匹配 — 仅匹配指定城市/省份）
python scripts/github_search.py \
  --queries "..." \
  --jd-keywords "..." \
  --jd-language "C++" \
  --location "beijing" \
  --location-strict \
  --target 20 \
  -o results.json

# 继续搜索（当已有结果全部展示完，需要搜更多时）
python scripts/github_search.py --resume SEARCH_ID --target 20 -o results.json
```

**需要环境变量**：
```bash
export GITHUB_TOKEN=ghp_xxxxx  # GitHub Personal Access Token
```

**地理位置匹配模式**（⚠️ OpenClaw 必须根据用户措辞判断使用哪种模式）：

| 用户措辞 | 模式 | CLI 参数 | 行为 |
|---------|------|---------|------|
| "Base 深圳"、"最好在北京"、"深圳优先" | **宽松**（默认） | `--location "shenzhen"` | 城市→省份→国家→中文启发式 层级回落 |
| "**必须是**北京"、"**只要**北京的"、"**限制**北京" | **严格** | `--location "beijing" --location-strict` | 仅匹配城市/省份，不回落到国家级，**Remote 也不通过** |
| "不限地区"、"远程"、不提位置 | **不过滤** | 不加 `--location` | 不做任何位置过滤 |

**注意**：宽松模式下 Remote 用户自动通过；严格模式下 Remote 不通过（用户说"必须是北京"就不想看其他城市的人，包括 Remote）。

**搜索引擎说明**：
- 同时搜索**仓库**（技术关键词维度）和**用户**（地理位置维度），合并去重
- 自动循环直到达到目标人数或触发停止条件（结果耗尽 / 连续 2 轮零新增）
- 多条 query 之间是 OR 逻辑（覆盖不同技术维度）
- 无邮箱的候选人不过滤，仅在排序中降权
- 输出包含漏斗数据（`funnel` 字段）和停止状态（`status` 字段）

**搜索结果不佳时的优化建议**（⚠️ OpenClaw 必须根据漏斗数据自动判断并给出建议）：

搜索脚本输出 `funnel` 字段（漏斗数据）和 `status` 字段。当 `status` 不是 `threshold_reached` 时，OpenClaw 根据以下规则生成优化建议：

| 漏斗瓶颈 | 判断条件 | 建议 |
|----------|---------|------|
| **技术太冷门** | `raw_from_repos < 50` | "当前技术方向搜索结果很少，建议扩展到相邻技术栈。" 并给出具体扩展建议（如 VisionOS → 加入 ARKit、SceneKit） |
| **地理位置太严格** | `after_dedup > 100` 但 `after_location_filter < 10` | "技术匹配的候选人不少，但目标城市的人很少。建议放宽到省份/全国，或使用宽松模式。" |
| **活跃度过滤过严** | `after_location_filter > 50` 但高分候选人 < 5 | "候选人数量足够但质量不高（多数不活跃或匹配度低）。建议放宽 pushed 时间范围（如 2024 年）。" |
| **搜索结果耗尽** | `status = "exhausted"` | "已搜索全部可用结果。建议调整搜索关键词或放宽条件。" |

OpenClaw 给出建议时，必须提供**具体的操作指引**（如"去掉 --location-strict"、"关键词加入 XX"），而非泛泛而谈。

---

**排序算法 V3（总分 100 分）**：

**设计原则**（猎头视角）：
- 领域匹配是前提：找错人一切白费
- 可触达性决定转化率：联系不上的大牛不如联系得上的牛人
- 影响力体现技术深度：但用 log 曲线避免 star 通胀
- 活跃度预测响应概率：活跃的人更可能回复
- 生态位是锦上添花：区分 leader vs follower

| 维度 | 得分规则 | 权重 |
|------|----------|------|
| **1. 领域匹配度** | 主语言匹配(15) + 生态关键词分级(10/15/20) | 35 分 |
| **2. 可触达性** | 邮箱(10) + 博客(6) + Twitter(5) + 社交(6) + bio(3) + isHireable(5)，可叠加，上限25 | 25 分 |
| **3. 代码影响力** | log₁₀(Star)×3(12) + log₁₀(Fork)×2(4) + log₁₀(Followers)×2(4) | 20 分 |
| **4. 有效活跃度** | 30天(12) / 90天(8) / 180天(4) | 12 分 |
| **5. 开源生态位** | 顶级Owner>500★(8) / 中等>100★(5) / 活跃>20★(3) | 8 分 |

**详细评分逻辑**：

**1. 领域匹配度（Relevance - 35分）**
- **规则 A**（主语言匹配）：Top 5 仓库的主语言与 JD 匹配 → +15 分
- **规则 B**（生态关键词）：Top 5 仓库的名称/描述命中 JD 关键词，按命中数分级：
  匹配源包含 repo 名称、描述和 **repositoryTopics 标签**（标签匹配比文本匹配更精准）
  - 命中 3+ 个 → +20 分（深度匹配）
  - 命中 2 个 → +15 分
  - 命中 1 个 → +10 分

**2. 可触达性（Reachability - 25分）**
- **多渠道叠加，上限 25 分**：
  - 公开邮箱 → +10 分（最直接的触达方式）
  - 个人网站/博客 → +6 分（可找到更多联系方式，也是破冰素材）
  - Twitter/X → +5 分（DM 是有效触达渠道）
  - 其他社交账号 → 每个 +3 分，上限 +6 分（LinkedIn、知乎等）
  - 有 bio → +3 分（愿意被人了解的信号）
  - isHireable = true → +5 分（候选人主动标记"可被雇佣"，回复概率极高）
- **说明**：不过滤无联系方式的候选人，仅影响排序。大牛无邮箱仍会出现，但排序靠后。HR 可通过 GitHub Issue/PR 评论等方式联系。

**3. 代码影响力（Impact - 20分）**
- **规则 A**（Star 影响力）：log₁₀(Star总数) × 3，封顶 12 分
  - 10★ → 3分, 100★ → 6分, 1000★ → 9分, 5000+★ → 12分
- **规则 B**（Fork 复用度）：log₁₀(Fork总数) × 2，封顶 4 分
- **规则 C**（社区关注度）：log₁₀(Followers) × 2，封顶 4 分
- **设计理由**：用 log 曲线而非线性，避免 star 通胀稀释区分度

**4. 有效活跃度（Activity - 12分）**
- 综合两个信号：
  - 信号 A — 最近活跃时间：30天内(8) / 90天内(5) / 180天内(3)
  - 信号 B — 年度贡献量：1000+(4) / 300+(3) / 100+(2) / >0(1)
- 两个信号相加，上限 12 分

**5. 开源生态位（Ecosystem - 8分）**
- 是 Owner 且最高星仓库 > 500★ → 8 分（顶级 Owner）
- 是 Owner 且最高星仓库 > 100★ → 5 分（有影响力的 Owner）
- 是 Owner 且最高星仓库 > 20★ → 3 分（活跃 Owner）

**档位划分**：
- 🔥 **极度匹配**：≥80 分（强烈推荐）
- ⭐ **高度匹配**：65-79 分（推荐）
- 👍 **匹配**：50-64 分（可考虑）
- 📋 **参考**：<50 分（需人工判断）

**输出**：`results.json`（完整候选人列表，已排序，含漏斗数据和停止状态）

---

### Step 1.5: 候选人展示与筛选（Human-in-the-Loop）

**目标**：让用户快速扫描候选人，标记状态（selected / passed / pending）。

**为什么需要这一步？**
- ❌ 不能直接批量生成触达话术（垃圾邮件制造机）
- ✅ 用户必须先筛选候选人，确认要触达的人

---

#### 展示格式（Markdown 表格，飞书兼容）

**每批展示数量**：最多 15 人。不足 15 人时展示全部。

**表头固定格式**：

```markdown
# 🎯 [职位名] — 候选人列表
搜索范围: [语言] + [关键词] | [位置] | 共 N 人，展示 Top 15

| # | 匹配 | 候选人 | 简介 | 公司 | 经验 | 📍 | 联系 | 状态 | 代表作 |
|---|------|--------|------|------|------|-----|------|------|--------|
| 1 | 🔥 | 张三 (@zhangsan) | ... | 字节跳动 | 8年 | 深圳 | 📧🌐🐦 | 🟢 | mutative (2.0K) |
| 2 | ⭐ | 李四 (@lisi) | ... | 阿里巴巴 | 5年 | 杭州 | 📧 | 🟢 | ssr (2.7K) |
...

---
回复数字选择：`1,3` = 选中 | `pass 2` = 跳过 | 「继续」查看下一批
```

---

#### 各列填写规范

| 列名 | 数据来源 | 填写规则 |
|------|----------|----------|
| **#** | 序号 | 当前批次内的序号（1-15） |
| **匹配** | `match_label` 字段 | 🔥 极度匹配(≥80) / ⭐ 高度匹配(65-79) / 👍 匹配(50-64) / 📋 参考(<50) |
| **候选人** | `name` + `github_id` | 格式：`真实姓名 (@github_id)`。如果 name 等于 github_id 则只写一个 |
| **简介** | **OpenClaw 根据 bio + 代表作 + 公司综合生成** | 见下方「简介生成规则」 |
| **公司** | `company` 字段 | 去掉 `@` 前缀。为空时写「独立开发者」。超过 12 字截断加 `..` |
| **经验** | `dev_years` 字段 | 格式：`N年`（基于 GitHub 账号创建时间推算，注意是"GitHub 活跃年限"不是"工作经验"） |
| **📍** | `location` 字段 | 翻译为中文城市名。超过 6 字截断。目标城市加 🎯 标记 |
| **联系** | `contact_icons` 字段 | 图标组合：📧=邮箱 🌐=博客/网站 🐦=Twitter 🔗=其他社交。**不展示具体值**（Step 2 才展示） |
| **状态** | `activity_label` 字段 | 🟢=30天内活跃 🟡=90天内 🔵=半年内 ⚪=不活跃。如果 isHireable=true，activity_label 后面会带 "| 🟢 求职中" |
| **代表作** | 优先 `showcase_repos`（候选人自选置顶项目），无置顶时用 `top_repos[0]` | 格式：`项目名 (星数)`。星数 ≥1000 用 K 表示。置顶项目加 📌 标记 |

---

#### 简介生成规则（⚠️ 重要：这一列由 OpenClaw 生成，不是原始数据）

**目的**：让不懂技术的 HR/猎头 一眼理解这个人是做什么的、为什么值得联系。

**生成规则**：
1. **长度**：一句话，15-30 个中文字
2. **内容优先级**（按顺序取最有价值的信息）：
   - 如果有知名公司经历 → 提及公司 + 角色（如："字节跳动 AI 工作流框架核心开发者"）
   - 如果代表作 star 数高 → 提及影响力（如："11K+ 开发者使用的 React 文档框架作者"）
   - 如果 bio 有明确方向 → 提炼方向（如："专注 RAG 和知识图谱的 AI 研究员"）
   - 兜底 → 根据代表作描述概括（如："用 Next.js 构建全栈电商项目"）
3. **技术术语规则**：可以使用 JD 中出现过的技术词（如 React、Next.js），但不引入 JD 以外的技术术语
4. **禁止**：
   - ❌ 不要照搬英文 bio（要翻译/提炼为中文）
   - ❌ 不要写"该候选人..."这种第三人称废话
   - ❌ 不要重复代表作列已有的信息
5. **示例**：
   - ✅ "阿里 13 年老兵，ice.js 渐进式框架核心作者"
   - ✅ "腾讯前端，开发基于 Next.js 的边缘计算博客引擎"
   - ✅ "全栈工程师，专注 React 状态管理和性能优化"
   - ❌ "A passionate developer who loves open source"（照搬英文）
   - ❌ "该候选人是一名优秀的前端工程师"（废话）

---

#### 用户交互规则

| 用户说 | OpenClaw 行为 |
|--------|------------|
| `"1, 3, 5"` 或 `"选 1 3 5"` | 标记为 selected，调 `candidate_manager.py --action batch-update` |
| `"pass 2, 4"` 或 `"跳过 2 4"` | 标记为 passed |
| `"继续"` / `"下一批"` / `"搜更多"` / `"继续搜索"` / `"更多"` | **统一逻辑**：见下方「继续/搜更多的判断规则」 |
| `"修改要求"` 或 `"换个条件"` | 回到 Step 0 重新解析 JD |
| `"就这些了"` 或 `"完成"` | 进入 Step 2 二次确认 |
| `"看看 zhangsan"` | 调 `candidate_manager.py --action get-candidate --github-id zhangsan` 展示详情 |

**⚠️「继续/搜更多」的判断规则（重要！不要让用户区分这两个操作）**：

当用户说"继续"、"搜更多"、"下一批"、"继续搜索"或任何表达"想看更多人"的意思时，OpenClaw 按以下优先级自动判断：

```
1. 如果还有未展示的已有结果 → 直接翻页展示下一批 15 人（不调 API）
2. 如果已有结果全部展示完了 → 调 github_search.py --resume SEARCH_ID 搜索新页面
3. 如果搜索已耗尽（status=exhausted/zero_yield）→ 告知用户无更多结果 + 给出优化建议
```

**用户不需要知道"翻页"和"搜索"的区别。** 这是内部实现细节，OpenClaw 自动判断。

**翻页终止规则**：
- 如果下一批的最高分 < 50（📋 参考级别），在展示前提醒：「⚠️ 后续候选人匹配度较低，建议调整搜索条件」
- 如果已有结果全部展示完且搜索未耗尽，提示：「已展示全部 N 人，正在搜索更多候选人...」然后自动调 --resume

---

#### 状态管理

```bash
cd ~/.openclaw/workspace/skills/ai-talent-hunter

# 批量更新状态
python scripts/candidate_manager.py --action batch-update \
  --search-id UUID --selected "user1,user2" --passed "user3"

# 查看某人详细信息
python scripts/candidate_manager.py --action get-candidate --github-id "zhangsan"
```

**数据持久化**：
- 所有搜索记录保存到：`~/.openclaw/workspace/skills/ai-talent-hunter/data/candidates.jsonl`
- 格式：每行一个 JSON 对象（JSONL）
- 支持跨搜索查询（防止重复推荐已 selected 的候选人）

---

### Step 2: 二次确认（Selected Review）

**目标**：用非技术语言展示所有 selected 候选人的完整信息，让 HR/猎头/高管最终确认后再生成触达话术。

**⚠️ 核心原则**：用户可能不懂技术、无法访问 GitHub。所有信息必须翻译为商业语言。

**操作**：
```bash
cd ~/.openclaw/workspace/skills/ai-talent-hunter
python scripts/candidate_manager.py --action get-selected --search-id UUID
```

---

#### 每位候选人的展示模板

OpenClaw 按以下结构为每位 selected 候选人生成展示内容：

**1. 一句话推荐**（⚠️ 由 OpenClaw 生成）
- 用商业语言概括此人为什么值得联系
- 提及公司背景 + 核心成就 + 与岗位的关联
- 示例：
  - ✅ "RingCentral（美资通讯巨头）在职 9 年资深前端，独立开发的开源工具被全球 2000+ 开发团队使用，React 生态核心技术栈完全匹配"
  - ❌ "TypeScript 开发者，有 mutative 项目 2000 stars"（技术黑话，HR 看不懂）

**2. 基本信息**（表格）

| 项目 | 信息 |
|------|------|
| 真实姓名 | 从 `name` 字段取 |
| 当前公司 | 从 `company` 字段取，如果是知名公司则括号补充公司简介 |
| 所在城市 | 翻译为中文 |
| GitHub 活跃年限 | 从 `dev_years` 字段取，注意措辞为"GitHub 活跃 N 年"而非"工作经验 N 年" |
| 活跃状态 | 🟢/🟡/🔵/⚪ |
| 求职状态 | isHireable=true → "✅ 已标记接受新机会" / false → 不显示 |

**3. 职业亮点**（⚠️ 由 OpenClaw 生成，列表形式）
- 将技术成就翻译为非技术人员能理解的描述
- 翻译规则：
  - Star 数 → "N 个开发者/团队关注使用"
  - 技术术语：**可以使用 JD 中出现过的技术词**（如 JD 提到 React 则可写"React 框架"），**但不引入 JD 以外的技术术语**（如 JD 没提 TypeScript 就不要写）
  - 不出现 GitHub 链接（用户可能打不开）
  - 项目描述要用一句话解释这个项目解决什么问题
- 示例（假设 JD 提到了 React/Next.js）：
  - ✅ "独立开发了高性能数据处理工具 mutative，被 2000+ 开发者关注使用，比同类方案快 2-6 倍"
  - ✅ "参与字节跳动 flowgram.ai 工作流平台核心开发，该项目被 7800+ 开发者关注"
  - ✅ "开发了 React 文档框架 fumadocs，被 11000+ 开发者使用"（JD 提到了 React，可以用）
  - ❌ "有一个 TypeScript 项目叫 mutative，2000 stars"（JD 没提 TypeScript，且用了 stars 原始术语）
- 贡献统计翻译规则：
  - contributions.total → "过去一年贡献了 N 次代码"
  - contributions.commits + contributions.pull_requests → "提交了 N 次代码修改，N 个代码改进请求"
  - pinnedItems → "候选人自选代表作：[列出置顶项目名]"

**4. 与岗位匹配度**
- 匹配标签（🔥/⭐/👍/📋）
- 逐条列出与 JD 需求的匹配点和不匹配点
- 示例：
  - ✅ React/Next.js 技术栈完全吻合
  - ✅ 有大型框架设计和开发经验
  - ⚠️ 目前在厦门，非目标城市北京

**5. 联系方式与建议**（表格）

| 渠道 | 信息 | 建议 |
|------|------|------|
| 📧 邮箱 | 具体邮箱地址 | ✅ 推荐，最直接 |
| 🌐 个人网站 | 具体网址 | 可参考了解更多 |
| 🐦 Twitter | 具体链接 | 可作为备选 |
| 🔗 其他社交 | 具体链接 | — |

- 如果无公开邮箱，给出替代建议："⚠️ 无公开邮箱，建议通过 Twitter 私信 或 GitHub 主页留言联系"

**6. 风险提示**
- ⚠️ 近期不活跃，可能已转型或离职
- ⚠️ 不在目标城市，需确认远程/搬迁意愿
- ⚠️ 无邮箱，联系难度较高
- ✅ isHireable=true → "此人已主动标记接受新机会，回复概率较高"
- ⚠️ isHireable=false + 知名大厂在职 → "未标记求职意向，可能需要更有竞争力的条件"
- ✅ 无明显风险（如果没有问题也要写）

---

#### 用户操作

| 用户说 | OpenClaw 行为 |
|--------|-------------|
| "确认全部" | 进入 Step 3（为所有 selected 生成触达话术） |
| "去掉 2 号" 或 "取消 XX" | 将其从 selected 改为 passed，不再生成话术 |
| "补人" 或 "回去再选" | 回到 Step 1.5 继续筛选 |

---

### Step 3: Pitch Writer（生成触达话术）

**目标**：为每位确认的候选人生成个性化触达消息。

**前置条件**：
- ⚠️ 只针对 Step 2 中最终确认的 selected 候选人
- ⚠️ 绝不批量生成（垃圾邮件制造机）

**⚠️ 前置信息收集（如果缺失，OpenClaw 必须先询问用户）**：

| 信息 | 为什么需要 | 示例 |
|------|----------|------|
| 发送人身份 | 决定语气（CTO≠HR≠CEO） | CTO / HR / 猎头 / CEO / 合伙人 |
| 发送人姓名 | 署名 | "李明" |
| 公司名称 | 让对方知道谁在联系 | "字节跳动" / "一家 A 轮 AI 创业公司" |
| 触达目的 | 决定话术方向 | 全职招聘 / 技术顾问 / 开源合作 |
| 触达渠道 | 决定长度和格式 | 邮件 / Twitter DM / 微信 |

**操作**：
1. OpenClaw 读取 `prompts/pitch_writer_prompt.md`
2. 结合候选人 profile + 上述前置信息
3. 为每位候选人生成定制话术

**核心规则**（详见 `prompts/pitch_writer_prompt.md`）：
- 语气匹配发送人身份（CTO 谈技术、CEO 谈愿景、HR 展现专业了解）
- 必须引用候选人的真实项目/背景（不是泛泛赞美）
- 绝不使用 HR 套话（"薪资丰厚"、"诚邀加入"、"我们是一家..."）
- 字数严格控制（邮件 ≤150 字、Twitter DM ≤80 字、微信 ≤100 字）
- 行动邀请低压力（"聊聊"而非"面试"）

---

## 合规红线（强制）

**✅ 允许的数据源**：
- GitHub 公开 API
- 个人博客公开文章
- Twitter/X 公开推文

**❌ 严禁的行为**：
- 购买/爬取私密数据
- 未经授权的批量邮件发送
- 绕过反爬机制的暴力抓取
- 任何形式的钓鱼/伪装

**🔒 Human-in-the-Loop 强制要求**：
- 生成的触达话术仅作草稿
- 必须由 HR/业务人员审核
- 手动通过邮件/Twitter 发送
- Skill 本身不执行发送

---

## 故障排查

### GitHub API 返回 403 Forbidden

**原因**：GitHub Token 权限不足或已过期。

**解决方案**：
```bash
# 重新生成 Token（需要 read:user 和 read:org 权限）
export GITHUB_TOKEN=ghp_新的token
```

---

## 依赖

- Python 3.8+
- requests
- GitHub Personal Access Token（需要 `read:user` 和 `read:org` 权限）

### ⚠️ 安全配置

**GitHub Token 获取**：
1. 访问 https://github.com/settings/tokens
2. 创建新 token，勾选 `read:user` 和 `read:org` 权限
3. 复制 token 到 `.env` 文件（**不要提交到 git！**）

**环境变量配置**：
```bash
# 创建 .env 文件（已在 .gitignore 中，不会被上传）
echo "GITHUB_TOKEN=your_token_here" > .env

# 或者临时使用（不持久化）
export GITHUB_TOKEN=ghp_your_token_here
```

**🔒 安全红线**：
- ❌ 绝对不要把真实 Token 提交到 git/GitHub
- ❌ 不要在公开的 SKILL.md 示例中使用真实 Token
- ✅ 使用 `.env` 文件（已加入 .gitignore）
- ✅ 示例中使用 `ghp_xxxxx` 占位符

---

## 示例用法

### 完整流程示例

```bash
# Step 0: JD 解析（在 OpenClaw 中执行）
# 输入："找 5 个深圳的 RocksDB C++ 工程师，要求最近 1 年内有活跃贡献"
# 输出：search_params.json

# Step 1: 搜索
cd ~/.openclaw/workspace/skills/ai-talent-hunter
export GITHUB_TOKEN=ghp_xxxxx

python scripts/github_search.py \
  --queries "language:c++ rocksdb pushed:>2025-01-01" \
  --jd-keywords "rocksdb,lsm-tree,storage" \
  --jd-language "C++" \
  --location "shenzhen" \
  --target 20 \
  -o results.json

# Step 1.5: 候选人展示与筛选（OpenClaw 展示，用户选择）
# 用户："1, 3, 5" → selected，"pass 2, 4" → passed

python scripts/candidate_manager.py --action batch-update \
  --search-id "uuid" --selected "zhangsan,wangwu" --passed "lisi"

# Step 2: 二次确认（展示 selected 候选人完整信息）
python scripts/candidate_manager.py --action get-selected --search-id "uuid"

# Step 3: 生成触达话术（只针对 selected 的人）
# OpenClaw 读取 prompts/pitch_writer_prompt.md 生成个性化触达消息
```

---

## 注意事项

1. **质量优先**：搜索结果可能有数百人，但只展示排序后的 Top 候选人。用户逐批确认，而非一次性倾倒所有结果。
2. **触达话术是草稿**：生成的消息需人工审核后再发送，Skill 本身不执行发送。

