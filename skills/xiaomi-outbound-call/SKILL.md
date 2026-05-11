---
name: xiaomi-outbound-bot
description: 触发阿里云晓蜜外呼机器人任务，自动批量拨打电话。适用于批量外呼、客户回访、满意度调查、简历筛查约面试等场景。可从前置工具或节点获取外呼名单。
---

# 阿里云晓蜜外呼机器人

自动化外呼机器人技能，用于批量电话外呼。

## 快速开始

### 方式 1: 使用 JSON 文件（推荐）⭐

创建 `taskInput.json` 文件：

```json
{
  "phoneNumbers": ["13800138000", "13900139000"],
  "scenarioDescription": "春季新品推广，了解客户购买意向",
  "taskName": "春季促销活动"
}
```

执行：

```bash
node scripts/bundle.js taskInput.json
```

### 方式 2: 使用环境变量

```bash
ARGUMENTS='{"phoneNumbers":["13800138000"],"scenarioDescription":"测试外呼"}' \
node scripts/bundle.js
```

## Agent 最佳实践 🎯

### 关键原则：充分利用场景信息 + 执行前确认

当用户提供外呼需求时，**不要**只提取电话号码和简单描述，而应该：

1. **深度分析场景** - 理解用户的真实意图和具体需求
2. **提取所有细节** - 时间、地点、条件、要求等
3. **构建完整配置** - 生成详细的 `agentProfile`，包含所有 11 个字段
4. **设计对话流程** - 在 `workflow` 中体现具体的沟通步骤
5. **执行前必须确认** ⚠️ - 向用户展示场景信息和外呼名单，等待明确确认

### 示例对比

❌ **不好的做法**（信息丢失）：
```json
{
  "phoneNumbers": ["15611207961"],
  "scenarioDescription": "建议反馈",
  "taskName": "建议外呼"
}
```
问题：丢失了"面试邀约"、"后天晚上八点"、"备选时间"等关键信息

✅ **好的做法**（充分利用信息）：
```json
{
  "phoneNumbers": ["15611207961"],
  "scenarioDescription": "Java 开发岗位面试邀约 - 优秀候选人",
  "taskName": "面试邀约",
  "agentProfile": {
    "role": "招聘专员",
    "background": "Java 开发岗位招聘，候选人简历优秀",
    "goals": "确认后天晚上八点面试时间，不方便则协商大后天",
    "workflow": "自我介绍 -> 说明来意 -> 确认后天晚上八点 -> 备选时间 -> 记录反馈",
    "openingPrompt": "您好，我是XX公司招聘专员，看到您的简历非常优秀"
  }
}
```

## 何时使用此技能

当用户提到以下场景时使用此技能：

- 需要批量打电话给客户（包括从前置节点获取的名单）
- 外呼任务、电话营销、客户回访
- 满意度调查、产品推广
- **简历筛查后约面试** - 从简历筛查工具获取候选人电话
- 通知提醒、信息确认
- 提到"晓蜜"、"外呼机器人"、"自动拨号"、"约面试"、"打电话"

**⚠️ 重要提示**：使用此技能时，请务必：
1. **仔细分析用户场景** - 提取所有有用信息
2. **构建完整的 agentProfile** - 不要只提供最基本的字段
3. **设计合理的对话流程** - 在 workflow 中体现用户的具体需求
4. **执行前必须确认** - 向用户展示场景信息和外呼名单，等待明确确认后才执行

## 前置条件

### 1. 配置阿里云凭证

需要在环境变量中配置阿里云 AK/SK：

```bash
export ALIYUN_OUTBOUND_BOT_ACCESS_KEY_ID="your-access-key-id"
export ALIYUN_OUTBOUND_BOT_ACCESS_KEY_SECRET="your-access-key-secret"
```

详细配置说明请参考 `references/config.md`

### 2. 绑定外呼号码 ⚠️ 重要

**必须在阿里云晓蜜控制台申请并绑定外呼号码，否则无法进行外呼。**

#### 如何绑定号码：

1. 登录 [阿里云晓蜜控制台](https://outboundbot.console.aliyun.com/)
2. 进入"号码管理"页面
3. 申请外呼号码（需要审核）
4. 将号码绑定到租户

#### 检查机制：

技能会在执行外呼前自动检查：
- ✅ 如果租户有绑定号码 → 自动绑定到实例，继续执行
- ❌ 如果租户没有绑定号码 → **终止流程**，提示用户配置

#### 错误提示：

```
❌ 租户下无绑定号码，无法进行外呼。
请先在阿里云晓蜜控制台申请并绑定外呼号码。
```

### 3. 系统要求

**只需要 Node.js 环境**（版本 >= 18）即可运行。

## Agent 使用指南

当你（Agent）需要帮助用户执行外呼任务时，请遵循以下步骤：

### 步骤 1: 获取外呼名单

**场景 A: 从前置节点获取**（如简历筛查、客户查询等）

如果用户的请求是多步骤任务的一部分（例如："给昨天收集到的蓝领简历进行筛查并约面试"），你应该：

1. **先执行前置步骤** - 调用相应的工具获取数据（如简历筛查工具）
2. **提取电话号码** - 从前置工具的返回结果中提取电话号码列表
3. **推断场景描述** - 根据用户意图生成场景描述（如"面试邀约"、"简历筛查后约面试"）
4. **直接传递给此技能** - 无需再次询问用户

**场景 B: 用户直接提供**

如果用户直接提供电话号码或明确的外呼需求，收集以下信息：

- **电话号码列表**（必需）- 至少一个有效的中国大陆手机号（1开头的11位数字）
- **外呼场景描述**（必需）- 清晰描述外呼目的，例如"产品推广"、"客户回访"
- **任务名称**（可选）- 便于识别的任务名称

如果信息不完整，使用 `ask questions` 工具向用户询问。

### 步骤 2: 验证数据

- 检查电话号码格式（中国大陆手机号：1开头的11位数字）
- 确保场景描述清晰明确
- 确认用户已配置阿里云 AK/SK 环境变量

### 步骤 3: 向用户确认信息 ⚠️ 必须执行

**在执行外呼任务前，必须向用户展示并确认以下信息：**

1. **外呼场景** - 清晰描述外呼目的和内容
2. **外呼名单** - 展示将要拨打的电话号码列表和数量
3. **智能体配置** - 如果构建了 agentProfile，简要说明智能体的角色和目标

#### 确认方式示例

```
准备执行外呼任务，请确认以下信息：

📋 任务信息
- 任务名称: 面试邀约
- 外呼场景: Java 开发岗位面试邀约 - 优秀候选人
- 智能体角色: 招聘专员
- 外呼目标: 确认后天晚上八点面试时间，不方便则协商大后天

📞 外呼名单（共 1 人）
1. 15611207961

是否确认执行外呼？
```

**重要提示**：
- ✅ 必须等待用户明确确认后才能执行
- ✅ 如果用户不确认，询问需要修改什么
- ❌ 不要在用户未确认的情况下自动执行外呼

### 步骤 4: 准备输入文件

**主要方式：创建 `taskInput.json` 文件** ⭐

将收集到的信息格式化为 JSON 文件。**重要：请仔细分析用户场景，提取尽可能多的信息来构建智能体配置。**

#### 🎯 从场景中提取信息的指南

当用户提供外呼场景时，你应该：

1. **分析场景类型** - 识别是招聘、销售、客服、调查等哪种场景
2. **提取关键信息** - 从用户描述中提取：
   - 外呼目的（如"邀约面试"、"产品推广"）
   - 具体内容（如"后天晚上八点"、"Java 开发岗位"）
   - 候选条件（如"不方便则询问其他时间"）
   - 特殊要求（如"优秀的候选人"、"VIP 客户"）

3. **构建 agentProfile** - 根据场景自动生成：
   - `role`: 根据场景推断（如"招聘专员"、"销售顾问"）
   - `background`: 提取业务背景（如"Java 开发岗位面试邀约"）
   - `goals`: 明确外呼目标（如"确认候选人后天晚上八点是否方便参加面试"）
   - `workflow`: 设计对话流程（如"问候 -> 说明来意 -> 确认时间 -> 备选方案 -> 记录反馈"）
   - `openingPrompt`: 生成得体的开场白（如"您好，我是XX公司的招聘专员"）

#### 📝 示例：从场景到完整配置

**用户场景**：
```
给 15611207961 这个优秀的人邀约面试，后天晚上八点是否方便参加面试，如不方便则询问大后天任意时间
```

**应该生成的完整 JSON**：
```json
{
  "phoneNumbers": ["15611207961"],
  "scenarioDescription": "Java 开发岗位面试邀约 - 优秀候选人",
  "taskName": "面试邀约",
  "agentProfile": {
    "name": "李敏",
    "gender": "女",
    "age": 28,
    "role": "招聘专员",
    "communicationStyle": ["专业", "友好", "高效"],
    "background": "Java 开发岗位招聘，候选人简历优秀，需要邀约面试",
    "goals": "确认候选人后天（X月X日）晚上八点是否方便参加面试，如不方便则协商大后天的时间",
    "skills": "面试邀约、时间协调、候选人沟通",
    "workflow": "自我介绍 -> 说明来意（面试邀约）-> 确认后天晚上八点 -> 如不方便询问大后天时间 -> 记录反馈 -> 发送面试详情",
    "constraint": "保持专业、尊重候选人时间、提供灵活的时间选择",
    "openingPrompt": "您好，我是XX公司的招聘专员李敏，看到您的简历非常优秀"
  }
}
```

**❌ 不够好的示例**（信息提取不充分）：
```json
{
  "phoneNumbers": ["15611207961"],
  "scenarioDescription": "建议反馈",
  "taskName": "建议外呼",
  "type": "service"
}
```

技能支持多种输入格式，会自动识别并解析：

**格式 1: 标准格式**（推荐）：

```json
{
  "phoneNumbers": ["13800138000", "13900139000"],
  "scenarioDescription": "春季新品推广，了解客户购买意向",
  "taskName": "春季促销活动",
  "agentProfile": {
    "name": "小美",
    "gender": "女",
    "age": 25,
    "role": "销售顾问",
    "communicationStyle": ["热情", "专业", "亲切"],
    "background": "春季新品推广活动",
    "goals": "了解客户购买意向，促成交易",
    "skills": "产品介绍、需求挖掘、促成交易",
    "workflow": "问候 -> 了解需求 -> 介绍产品 -> 处理异议 -> 促成合作",
    "constraint": "保持礼貌、尊重对方意愿、不强制推销",
    "openingPrompt": "您好，我是小美，春季新品推广活动的销售顾问"
  }
}
```

**注意**: `agentProfile` 中的所有字段都是可选的。如果不提供，系统会根据 `scenarioDescription` 智能推断合适的配置。

**格式 2: 简化格式**：

```json
{
  "phones": "13800138000,13900139000",
  "scenario": "产品推广",
  "name": "春季促销"
}
```

**格式 3: 候选人/简历筛查格式**（前置节点）：

```json
{
  "candidates": [
    { "name": "张三", "phone": "13800138000", "score": 85 },
    { "name": "李四", "phone": "13900139000", "score": 90 }
  ],
  "scenarioDescription": "面试邀约 - 蓝领岗位简历筛查通过",
  "taskName": "蓝领简历筛查后约面试",
  "previousStep": "简历筛查"
}
```

**格式 4: CRM/外部工具格式**：

```json
{
  "data": {
    "contacts": [
      { "phone": "13800138000", "name": "张三" },
      { "phone": "13900139000", "name": "李四" }
    ],
    "purpose": "客户回访",
    "campaignName": "满意度调查"
  },
  "toolName": "CRM-System"
}
```

**格式 5: 通用列表格式**：

```json
[
  { "phone": "13800138000", "name": "张三" },
  { "phone": "13900139000", "name": "李四" }
]
```

注意：使用此格式时，scenarioDescription 会默认为"批量外呼"

### 智能体配置（强烈推荐）⭐

**虽然 `agentProfile` 是可选的，但强烈建议 Agent 根据用户场景主动构建完整的智能体配置。**

提供完整的 `agentProfile` 可以：
- ✅ 让外呼更加专业和得体
- ✅ 提高外呼成功率和用户体验
- ✅ 确保对话流程符合业务需求
- ✅ 避免通用话术导致的沟通不畅

技能支持自定义外呼智能体的人设和行为。可以通过 `agentProfile` 字段配置：

#### 配置字段说明

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `name` | string | 否 | 智能体名称 | "小美"、"小智" |
| `gender` | string | 否 | 性别 | "男"、"女" |
| `age` | number | 否 | 年龄 | 25 |
| `role` | string | 否 | 身份角色 | "销售顾问"、"招聘专员"、"客服专员" |
| `communicationStyle` | string[] | 否 | 沟通风格 | ["热情", "专业", "亲切"] |
| `background` | string | 否 | 业务背景 | "春季新品推广活动" |
| `goals` | string | 否 | 业务目标 | "了解客户购买意向，促成交易" |
| `skills` | string | 否 | 业务技能 | "产品介绍、需求挖掘、促成交易" |
| `workflow` | string | 否 | 工作流程 | "问候 -> 了解需求 -> 介绍产品 -> 促成合作" |
| `constraint` | string | 否 | 约束条件 | "保持礼貌、尊重对方意愿、不强制推销" |
| `openingPrompt` | string | 否 | 开场白 | "您好，我是小美" |

#### 智能推断

如果不提供 `agentProfile` 或部分字段，系统会根据 `scenarioDescription` 智能推断：

- **面试/招聘场景** → 招聘专员，专业友好的风格
- **保险/理财场景** → 保险顾问，专业耐心的风格
- **游戏推广场景** → 游戏推广员，热情活泼的风格
- **审计/调查场景** → 审计专员，专业严谨的风格
- **客服/回访场景** → 客服专员，亲切耐心的风格
- **销售/产品场景** → 销售顾问，热情专业的风格

#### 配置示例

**招聘场景**：
```json
{
  "phoneNumbers": ["13800138000"],
  "scenarioDescription": "面试邀约 - Java 开发工程师",
  "agentProfile": {
    "name": "李敏",
    "role": "招聘专员",
    "openingPrompt": "您好，我是李敏，XX公司的招聘专员"
  }
}
```

**保险场景**：
```json
{
  "phoneNumbers": ["13800138000"],
  "scenarioDescription": "重疾险产品推荐",
  "agentProfile": {
    "name": "王顾问",
    "role": "保险顾问",
    "communicationStyle": ["专业", "耐心", "诚恳"]
  }
}
```

## 输入格式完整说明

### 主要输入方式：taskInput.json 文件 ⭐

**这是推荐的主要输入方式**。创建一个 JSON 文件（通常命名为 `taskInput.json`），包含外呼任务的所有参数。

#### 完整格式示例

```json
{
  "phoneNumbers": ["13800138000", "13900139000"],
  "scenarioDescription": "春季新品推广，了解客户购买意向",
  "taskName": "春季促销活动",
  "agentProfile": {
    "name": "小美",
    "gender": "女",
    "age": 25,
    "role": "销售顾问",
    "communicationStyle": ["热情", "专业", "亲切"],
    "background": "春季新品推广活动",
    "goals": "了解客户购买意向，促成交易",
    "skills": "产品介绍、需求挖掘、促成交易",
    "workflow": "问候 -> 了解需求 -> 介绍产品 -> 处理异议 -> 促成合作",
    "constraint": "保持礼貌、尊重对方意愿、不强制推销",
    "openingPrompt": "您好，我是小美，春季新品推广活动的销售顾问"
  },
  "metadata": {
    "source": "manual",
    "campaign": "spring-2024"
  }
}
```

#### 最简格式

```json
{
  "phoneNumbers": ["13800138000"],
  "scenarioDescription": "测试外呼"
}
```

#### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `phoneNumbers` | string[] | ✅ 是 | 电话号码列表，中国大陆手机号（11位，1开头） |
| `scenarioDescription` | string | ✅ 是 | 外呼场景描述，用于生成话术和智能体配置 |
| `taskName` | string | 否 | 任务名称，便于识别 |
| `agentProfile` | object | 否 | 智能体配置，不提供则自动推断 |
| `metadata` | object | 否 | 额外元数据，可存储任何自定义信息 |

#### 执行方式

```bash
# 使用 JSON 文件
node scripts/bundle.js taskInput.json

# 或使用其他文件名
node scripts/bundle.js my-task.json
```

### 备用输入方式

#### 方式 2: $ARGUMENTS 环境变量

适用于 Cursor Agent 或需要通过环境变量传递参数的场景：

```bash
ARGUMENTS='{"phoneNumbers":["13800138000"],"scenarioDescription":"测试"}' \
node scripts/bundle.js
```

#### 方式 3: 交互式输入

如果不提供任何参数，技能会进入交互式模式，逐步询问：

```bash
node scripts/bundle.js

# 会提示输入：
# - 电话号码列表
# - 场景描述
# - 任务名称
```

### 输入优先级

技能会按以下顺序查找输入：

1. **命令行参数**（JSON 文件路径）- 最高优先级
2. **$ARGUMENTS 环境变量** - 次优先级
3. **交互式输入** - 兜底方案

### 步骤 5: 执行技能

**在用户确认后，执行外呼任务：**

**方式 A: 使用 JSON 文件（推荐）**

```bash
node scripts/bundle.js taskInput.json
```

**方式 B: 使用 $ARGUMENTS 环境变量**

```bash
ARGUMENTS='{"phoneNumbers":["13800138000"],"scenarioDescription":"测试"}' \
node scripts/bundle.js
```

**输入优先级**：
1. 命令行参数（JSON 文件路径）
2. `$ARGUMENTS` 环境变量
3. 交互式输入（如果以上都未提供）

### 步骤 6: 监控和反馈

- 监控命令输出，查看任务进度
- 等待任务完成（可能需要几分钟，取决于电话数量）
- 向用户报告结果：
  - 外呼任务已启动
  - 任务组 ID
  - 拨打的电话数量

## 常见使用场景

### 场景 1: 从前置节点获取数据（链式调用）⭐ 重点

**用户**: "给昨天收集到的蓝领简历进行筛查并约面试"

**Agent 操作流程**:

1. **执行前置步骤** - 调用简历筛查工具

   ```
   [简历筛查工具返回]
   {
     "candidates": [
       { "name": "张三", "phone": "13800138000", "score": 85 },
       { "name": "李四", "phone": "13900139000", "score": 90 }
     ]
   }
   ```

2. **提取电话号码** - 从筛查结果中提取

   ```javascript
   phoneNumbers = ["13800138000", "13900139000"];
   ```

3. **生成场景描述** - 根据用户意图自动生成

   ```javascript
   scenarioDescription = "面试邀约 - 蓝领岗位简历筛查通过";
   taskName = "蓝领简历筛查后约面试";
   ```

4. **创建 taskInput.json 文件**

   ```json
   {
     "phoneNumbers": ["13800138000", "13900139000"],
     "scenarioDescription": "面试邀约 - 蓝领岗位简历筛查通过",
     "taskName": "蓝领简历筛查后约面试",
     "agentProfile": {
       "role": "招聘专员",
       "openingPrompt": "您好，我是XX公司的招聘专员"
     },
     "metadata": {
       "source": "resume-screening",
       "previousStep": "简历筛查",
       "candidates": [
         { "name": "张三", "phone": "13800138000", "score": 85 },
         { "name": "李四", "phone": "13900139000", "score": 90 }
       ]
     }
   }
   ```

5. **执行外呼技能**

   ```bash
   node scripts/bundle.js taskInput.json
   ```

**关键点**:

- ✅ 无需用户再次提供电话号码
- ✅ 场景描述由 Agent 根据上下文自动生成
- ✅ 可以在 metadata 中保留前置节点的完整数据
- ✅ 整个流程对用户透明，一句话完成多步任务

### 场景 2: 用户直接提供号码

**用户**: "帮我给 13800138000 和 13900139000 打电话，做春季促销推广"

**Agent 操作**:

1. 提取电话号码: `["13800138000", "13900139000"]`
2. 提取场景: `"春季促销推广"`
3. 创建 `taskInput.json`:

```json
{
  "phoneNumbers": ["13800138000", "13900139000"],
  "scenarioDescription": "春季促销推广",
  "taskName": "春季促销"
}
```

4. 执行: `node scripts/bundle.js taskInput.json`

### 场景 3: 用户提供号码列表

**用户**: "我有个客户名单，帮我做满意度回访"

**Agent 操作**:

1. 使用 `ask questions` 工具询问号码列表
2. 读取并解析号码
3. 创建 `taskInput.json`:

```json
{
  "phoneNumbers": ["13800138000", "13900139000", "..."],
  "scenarioDescription": "客户满意度回访",
  "taskName": "满意度调查"
}
```

4. 执行: `node scripts/bundle.js taskInput.json`

### 场景 4: 从文件读取

**用户**: "用 customers.json 里的号码做产品推广"

**Agent 操作**:

1. 读取 `customers.json` 文件内容
2. 解析电话号码
3. 创建 `taskInput.json`:

```json
{
  "phoneNumbers": ["提取的号码列表"],
  "scenarioDescription": "产品推广",
  "taskName": "产品推广活动"
}
```

4. 执行: `node scripts/bundle.js taskInput.json`

## 工作流程

技能执行时会自动完成以下步骤：

```
1. 验证输入 - 检查电话号码格式和必需参数
   ↓
2. 创建实例 - 获取或创建阿里云晓蜜外呼实例
   ↓
3. 确认绑定号码 - 检查租户是否有绑定号码 ⚠️ 关键步骤
   ├─ 如果没有绑定号码 → 终止流程，提示用户配置
   └─ 如果有绑定号码 → 自动绑定到实例，继续执行
   ↓
4. 创建话术 - 根据场景描述生成外呼话术
   ↓
5. 创建任务组 - 在阿里云晓蜜平台创建外呼任务组
   ↓
6. 启动外呼 - 开始批量拨打电话
   ↓
7. 返回结果 - 输出任务组 ID 和执行状态
```

## 高级用法

### 使用 JSON 文件（推荐）⭐

**这是主要的输入方式**。创建 `taskInput.json` 文件：

```json
{
  "phoneNumbers": ["13800138000", "13900139000"],
  "scenarioDescription": "了解客户满意度",
  "taskName": "客户回访",
  "agentProfile": {
    "role": "客服专员",
    "openingPrompt": "您好，我是XX公司的客服专员"
  }
}
```

执行：

```bash
node scripts/bundle.js taskInput.json
```

### 使用 $ARGUMENTS 环境变量

适用于 Cursor Agent 或脚本调用：

```bash
ARGUMENTS='{"phoneNumbers":["13800138000"],"scenarioDescription":"测试"}' \
node scripts/bundle.js
```

### 命令行参数

```bash
# 指定 JSON 文件
node scripts/bundle.js taskInput.json

# 指定实例 ID 和脚本 ID（复用已有资源）
node scripts/bundle.js taskInput.json --instance-id xxx --script-id yyy
```

## 输出结果

技能执行完成后会输出：

```typescript
{
  taskInput: {
    phoneNumbers: string[];
    scenarioDescription: string;
    taskName?: string;
    metadata?: Record<string, any>;
  },
  jobGroupId: string;         // 任务组 ID
  instanceId: string;         // 外呼实例 ID
  scriptId: string;           // 话术脚本 ID
  totalPhones: number;        // 拨打的电话数量
}
```

## 常见问题

### 1. 租户没有绑定号码 ⚠️ 最常见

**错误**: 
```
❌ 租户下无绑定号码，无法进行外呼。
请先在阿里云晓蜜控制台申请并绑定外呼号码。
```

**原因**: 租户未在阿里云晓蜜控制台申请和绑定外呼号码

**解决**:
1. 登录 [阿里云晓蜜控制台](https://outboundbot.console.aliyun.com/)
2. 进入"号码管理"页面
3. 申请外呼号码（需要提交资质审核）
4. 审核通过后，将号码绑定到租户
5. 重新执行外呼任务

**注意**: 
- 号码申请需要企业资质
- 审核可能需要 1-3 个工作日
- 绑定号码后技能会自动检测并使用

### 2. 环境变量未配置

**错误**: "请配置阿里云 AK/SK 环境变量"

**解决**:

```bash
export ALIYUN_OUTBOUND_BOT_ACCESS_KEY_ID="your-key"
export ALIYUN_OUTBOUND_BOT_ACCESS_KEY_SECRET="your-secret"
```

### 3. 电话号码格式错误

**错误**: "电话号码格式不正确"

**解决**: 确保号码是中国大陆手机号（1开头的11位数字）

### 4. 任务创建失败

**错误**: "创建任务组失败"

**可能原因**:
- 实例状态异常
- 话术脚本未发布
- 账号权限不足
- 并发数超限

**解决**: 检查阿里云晓蜜控制台的实例和脚本状态

## 命令行参数

```bash
node scripts/bundle.js [options]

Options:
  --json <file>        从 JSON 文件读取任务配置
  --no-interactive     禁用交互式输入
  --instance-id <id>   指定外呼实例 ID
  --script-id <id>     指定话术脚本 ID
```

## 相关文档

- [配置说明](references/config.md) - 详细的环境变量配置指南
- [阿里云晓蜜文档](https://help.aliyun.com/product/outboundbot.html) - 官方产品文档

## 注意事项

1. **合规使用**: 确保外呼行为符合相关法律法规，获得用户同意
2. **号码隐私**: 妥善保管客户电话号码，避免泄露
3. **费用控制**: 外呼服务会产生费用，注意控制调用频率
4. **测试环境**: 建议先在测试环境验证，再用于生产
5. **错误处理**: 监控任务执行状态，及时处理失败情况

## 功能说明

### 核心功能

1. **批量外呼** - 支持同时向多个号码发起外呼
2. **场景定制** - 根据场景描述自动生成外呼话术
3. **自动创建** - 自动创建外呼实例和话术脚本
4. **号码检查** - 自动检查并绑定外呼号码
5. **任务管理** - 创建并启动外呼任务组

### 技能范围

本技能专注于**外呼任务的创建和启动**，包括：
- ✅ 验证电话号码
- ✅ 创建外呼实例
- ✅ 检查并绑定外呼号码
- ✅ 生成外呼话术
- ✅ 创建任务组
- ✅ 启动外呼任务

本技能**不包括**：
- ❌ 外呼结果分析
- ❌ 录音文件处理
- ❌ 会话内容总结
- ❌ 情感分析

如需查看外呼结果，请在阿里云晓蜜控制台查看。

## 参考链接

- [阿里云晓蜜控制台](https://outboundbot.console.aliyun.com/)
- [阿里云晓蜜文档](https://help.aliyun.com/product/outboundbot.html)
