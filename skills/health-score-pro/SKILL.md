---
name: health-management
version: 1.1.0
description: Comprehensive health management system integrating 10 best-selling health books' consensus principles. Use when users discuss nutrition, supplements, fitness, diet, anti-aging, anti-inflammation, longevity, or request diet tracking/analysis. Supports (1) Daily diet recording with 3-dimension scoring (Greger's Daily Dozen, Li's 5×5×5, consensus checklist), (2) Weekly/monthly/yearly analysis with trend identification, (3) Food defense system identification (angiogenesis, regeneration, microbiome, DNA protection, immunity), (4) Personalized improvement recommendations based on data patterns.
manifest: manifest.json
author: longerian
metadata:
  openclaw:
    thinking: "medium"
  security:
    permissions_declared: true
    scripts_auditable: true
    data_local_only: true
    optional_dependencies: []

---

# Health Management Skill

A data-driven health management system based on the maximum consensus from 10 best-selling health books, featuring three-dimensional diet tracking and automated analysis.

## 🚨 CRITICAL: 多语言支持规范（最高优先级！）

**⚠️ 所有输出必须使用用户配置的语言！这不是可选项！**

### 强制执行规则

**AI 在每次回复前必须执行以下检查**：

```
1. ✅ 读取用户语言配置
   - 文件：memory/health-users/{username}/profile.md
   - 字段：**Language**: {language-code}
   - 默认：zh-CN（中文）

2. ✅ 使用用户语言输出所有内容
   - 饮食/运动/睡眠记录反馈
   - 健康建议和改进方案
   - 周报/月报/年报
   - 错误提示和引导信息
   - 评分解读和数据分析

3. ✅ 验证语言一致性
   - 所有标题使用用户语言
   - 所有建议使用用户语言
   - 所有数字格式符合语言习惯
```

**❌ 绝对禁止**：
- ❌ 忽略用户语言配置，使用默认语言
- ❌ 部分内容使用用户语言，部分使用其他语言
- ❌ 不读取 profile.md 中的 Language 字段

**✅ 正确示例**：
```
用户语言：en (English)

AI 回复：
📊 Today's Score: 23.5/30 (78%) ⭐⭐⭐ Good

✅ Highlights:
1. Complete defense system coverage (5/5)
2. High supplement-goal alignment

💡 Suggestions:
1. Add leafy greens: Suggest a spinach salad (100g)
```

**❌ 错误示例**（绝对禁止）：
```
用户语言：en (English)

AI 回复：
📊 今日评分：23.5/30 (78%) ⭐⭐⭐ 良好  ❌ 使用了中文

✅ 亮点：
1. 防御系统覆盖全面（5/5）  ❌ 使用了中文
```

---

## ⏰ 时区与日期规范（CRITICAL）

**所有日期和时间必须使用用户配置的时区**

### 时区配置

**首次使用时**：
- 系统会引导用户设置时区（第3步）
- 时区信息保存在 `memory/health-users/{username}/profile.md` 中
- 默认时区：`Asia/Shanghai`（北京时间，UTC+8）

---

## 🚨🚨🚨 CRITICAL: 格式规范强制执行（最高优先级！）

**⚠️ 每次记录健康数据时，必须严格遵守以下格式规范！这不是可选项！**

### 强制执行规则

**每次记录前必须执行以下检查**：

```
1. ✅ 检查历史记录格式
   - 读取前1-2天的记录文件
   - 确认表格、图表、评分格式
   - 严格按照相同格式记录

2. ✅ 睡眠记录必须包含：
   - 📊 客观数据表格（入睡时间、醒来时间、睡眠时长、清醒时间、深度睡眠、核心睡眠、REM睡眠）
   - 进度条图表（睡眠阶段分布）
   - 生理指标表格（心率、呼吸频率、手腕温度）
   - 💭 主观感受（入睡情况、睡眠质量、醒来状态）
   - 📈 睡眠综合评分表格（睡眠时长、睡眠结构、主观感受、总分）
   - 💡 改进建议（优点、可优化点、明日目标）

3. ✅ 饮食记录必须包含：
   - 📊 量化评估表格（维度一、维度二、维度三）
   - 防御系统覆盖评估表格
   - 三维度评分总览表格
   - 💡 改进建议（亮点、改进空间、午餐/晚餐建议）
   - 餐后运动建议

4. ✅ 日报总结必须包含：
   - 🎯 三餐综合评分表格
   - 📈 每日十二清单累计表格
   - 🎯 明日改进重点
   - 记录时间和数据来源
```

### ❌ 绝对禁止

- ❌ 使用简略格式，缺少表格
- ❌ 缺少进度条图表
- ❌ 缺少量化评估
- ❌ 缺少评分表格
- ❌ 说"格式太长，简化一下"
- ❌ 不参考历史记录格式

### ✅ 正确示例

**睡眠记录格式**（参考2026-03-14.md、2026-03-15.md）：
```markdown
## 😴 睡眠记录

### 📊 客观数据（智能手表）

| 指标 | 数值 | 评价 |
|------|------|------|
| **入睡时间** | 23:30（2026-03-15） | ✅ 正常 |
| **醒来时间** | 07:00（2026-03-16） | ✅ 正常 |
| **睡眠时长** | 7小时30分钟 | ✅ 充足（目标：7-9小时） |
...

**睡眠阶段分布**：
```
清醒时间：█░░░░░░░░░ 5-7%
深度睡眠：████░░░░░░ 20%
核心睡眠：██████████ 53%
REM睡眠： █████░░░░░ 27%
```

**生理指标**：
| 指标 | 数值 | 评价 |
|------|------|------|
| **心率** | 48-65 bpm | ✅ 正常偏低 |
...

### 📈 睡眠综合评分

| 维度 | 得分 | 说明 |
|------|------|------|
| **睡眠时长** | 9/10 | 7小时30分钟，达标 |
| **睡眠结构** | 8/10 | 深度睡眠20%正常 |
| **主观感受** | 8/10 | 睡得深实踏实 |
| **总分** | **25/30** | **83%** ⭐⭐⭐⭐ 很好 |
```

**饮食记录格式**（参考2026-03-14.md、2026-03-15.md）：
```markdown
### 📊 早餐量化评估

#### 维度一：每日十二清单（早餐贡献）

| 项目 | 早餐摄入 | 目标量 | 完成度 | 状态 |
|------|---------|--------|--------|------|
| 🥦 十字花科蔬菜 | 0克 | 80克 | 0% | ❌ **未达标**（需补充80克） |
| 🥬 绿叶菜 | 0克 | 160克 | 0% | ❌ **未达标**（需补充160克） |
...

#### 维度二：5×5×5方法（早餐贡献）

**防御系统覆盖评估**：

| 防御系统 | 早餐食物 | 摄入量 | 覆盖度 | 状态 |
|---------|---------|--------|--------|------|
| ✅ **血管生成(A)** | 坚果 + 橄榄油 | 35克 | 充分 | ✅ 充分覆盖 |
...

### 📊 三维度评分总览（早餐）

| 维度 | 得分 | 评价 | 说明 |
|------|------|------|------|
| **维度一：每日十二** | 2.5/10 | ⭐⭐ | 3/12项达标 |
| **维度二：5×5×5** | 6.0/10 | ⭐⭐⭐ | 5/5防御系统全覆盖 |
| **维度三：共识清单** | 7.3/10 | ⭐⭐⭐⭐ | 健康食物良好 |
| **总分** | **15.8/30** | **53%** | **⭐⭐⭐** 及格 |
```

### 🔧 AI 自检流程（每次记录前必须执行）

**步骤1：读取历史记录**
```bash
# 读取前1-2天的记录文件
read memory/health-users/{username}/daily/YYYY-MM-DD.md
```

**步骤2：检查格式**
```
✅ 是否有详细表格？
✅ 是否有进度条图表？
✅ 是否有量化评估？
✅ 是否有评分表格？
✅ 是否有改进建议？
```

**步骤3：按照相同格式记录**
```
✅ 使用相同的表格结构
✅ 使用相同的评分格式
✅ 使用相同的评价符号
✅ 使用相同的改进建议格式
```

**步骤4：备份前再次检查**
```
✅ 格式是否完整？
✅ 数据是否准确？
✅ 评分是否正确？
✅ 建议是否具体？
```

---

### 💡 为什么必须严格遵守格式？

1. **数据一致性**：便于对比分析，识别趋势
2. **可读性**：表格和图表更直观
3. **专业性**：符合健康管理系统的标准
4. **可追溯性**：便于回顾历史记录
5. **用户信任**：保持高质量的输出

---

**⚠️ 如果AI偷懒，用户可以说**：
- "格式不对，参考昨天的格式"
- "缺少表格，补上"
- "格式太简略，详细一点"
- "按照之前的格式重新记录"

**AI 必须立即修正，不得辩解！**

---

**支持的时区格式**：
- 时区名称：`Asia/Shanghai`, `America/New_York`, `Europe/London` 等
- 时区偏移：`UTC+8`, `UTC-5`, `UTC+0` 等

**常见时区示例**：
```bash
# 中国大陆
TIMEZONE="Asia/Shanghai"

# 美国东部
TIMEZONE="America/New_York"

# 美国西部
TIMEZONE="America/Los_Angeles"

# 欧洲
TIMEZONE="Europe/London"
TIMEZONE="Europe/Paris"

# 日本
TIMEZONE="Asia/Tokyo"
```

---

## 🌐 语言国际化支持（CRITICAL）

**所有输出必须使用用户配置的语言**

### ⚠️ 重要：AI 输出语言规范（CRITICAL）

**AI 在回复用户时，必须遵循以下规则**：

1. **首次交互时**：
   - 读取 `memory/health-users/{username}/profile.md` 中的 `Language` 字段
   - 如果未配置，使用默认语言：`zh-CN`（中文）

2. **所有输出都必须使用用户配置的语言**：
   - ✅ 饮食记录反馈
   - ✅ 运动记录反馈
   - ✅ 补剂记录反馈
   - ✅ 睡眠记录反馈
   - ✅ 评分分析
   - ✅ 健康建议
   - ✅ 周报/月报/年报
   - ✅ 错误提示
   - ✅ 引导信息

3. **语言切换规则**：
   - 用户随时可以说"切换到英文"或"switch to English"
   - AI 应更新 profile.md 中的 Language 字段
   - 后续所有输出使用新语言

---

### 语言配置

**首次使用时**：
- 系统会引导用户设置语言（第2步）
- 语言信息保存在 `memory/health-users/{username}/profile.md` 中
- 默认语言：`zh-CN`（中文简体）

**支持的语言**：
```bash
# 中文（简体）- 默认
LANGUAGE="zh-CN"

# English
LANGUAGE="en"

# 日本語
LANGUAGE="ja"

# 한국어
LANGUAGE="ko"

# Français
LANGUAGE="fr"

# Deutsch
LANGUAGE="de"

# Español
LANGUAGE="es"
```

---

### 📝 多语言输出示例（CRITICAL）

**AI 必须根据用户语言输出对应语言的反馈和报告**

#### 示例1：饮食记录反馈

**中文（zh-CN）**：
```
📊 今日评分：23.5/30 (78%) ⭐⭐⭐ 良好

✅ 亮点：
1. 防御系统覆盖全面（5/5）
2. 补剂选择与目标匹配度高
3. 饮食顺序执行良好

⚠️ 改进建议：
1. 补充绿叶菜：建议加一份凉拌菠菜（100克）
2. 补充十字花科：建议加一份西兰花（100克）
```

**英文**：
```
📊 Today's Score: 23.5/30 (78%) ⭐⭐⭐ Good

✅ Highlights:
1. Complete defense system coverage (5/5)
2. High supplement-goal alignment
3. Good meal sequence execution

⚠️ Improvements:
1. Add leafy greens: Suggest a spinach salad (100g)
2. Add cruciferous vegetables: Suggest steamed broccoli (100g)
```

**日文**：
```
📊 本日のスコア：23.5/30 (78%) ⭐⭐⭐ 良好

✅ ハイライト：
1. 防御システムの完全カバー（5/5）
2. サプリメントと目標の高い一致
3. 良好な食事順序の実行

⚠️ 改善提案：
1. 葉物野菜を追加：ほうれん草のサラダ（100g）を提案
2. アブラナ科野菜を追加：蒸しブロッコリー（100g）を提案
```

---

#### 示例2：周报模板

**中文（zh-CN）**：
```
📊 本周健康总结（2026-W10）

🎯 总体评分：78/100
📈 趋势：上升 ↑

✅ 成就：
- 连续7天记录饮食
- 防御系统覆盖率提升15%
- 补剂依从性100%

💡 下周重点：
1. 增加绿叶菜摄入（目标：160克/天）
2. 优化运动时间（目标：30分钟/天）
```

**英文**：
```
📊 Weekly Health Summary (2026-W10)

🎯 Overall Score: 78/100
📈 Trend: Rising ↑

✅ Achievements:
- 7-day consecutive diet tracking
- Defense system coverage increased by 15%
- 100% supplement adherence

💡 Next Week Focus:
1. Increase leafy greens intake (Goal: 160g/day)
2. Optimize exercise time (Goal: 30min/day)
```

---

#### 示例3：健康建议

**中文（zh-CN）**：
```
💡 根据你的目标（控制血糖），建议：

1. 饮食调整：
   - 增加膳食纤维（豆类、全谷物）
   - 控制精制碳水（白米、白面）
   - 优化进食顺序（蔬菜→蛋白质→碳水）

2. 补剂优化：
   - α-硫辛酸：300-600mg/天（空腹）
   - 铬：200-400mcg/天（随餐）
   - 镁：400-500mg/天（睡前）
```

**英文**：
```
💡 Based on your goals (Blood Sugar Control), suggestions:

1. Dietary Adjustments:
   - Increase dietary fiber (beans, whole grains)
   - Limit refined carbs (white rice, white flour)
   - Optimize meal sequence (veggies → protein → carbs)

2. Supplement Optimization:
   - Alpha-lipoic acid: 300-600mg/day (empty stomach)
   - Chromium: 200-400mcg/day (with meals)
   - Magnesium: 400-500mg/day (before bed)
```

---

### 🔧 AI 输出语言规则（CRITICAL）

**每次回复用户时，AI 必须执行以下步骤**：

```bash
1. 读取用户语言配置
   language=$(grep -E "^\s*-\s*\*\*Language\*\*:" profile.md | sed 's/.*\*\*Language\*\*:\s*//')

2. 根据语言选择输出模板
   case "$language" in
       zh-CN) # 使用中文模板
       en)    # 使用英文模板
       ja)    # 使用日文模板
       ...
   esac

3. 输出对应语言的内容
   - 所有标题、说明、建议、报告
   - 所有数据解读和分析
   - 所有错误提示和引导信息
```

---

### 多语言工具函数示例
```bash
# 读取用户语言
language=$(get_user_language "$username")

# 获取本地化文本
success_msg=$(get_localized_text "backup.success" "$language")

# 中文输出：✅ 数据已安全备份到 GitHub！
# 英文输出：✅ Data successfully backed up to GitHub!
```

### 日期格式标准

**文件命名**：
- 日报：`YYYY-MM-DD.md`（例如：`2026-03-06.md`）
- 周报：`YYYY-WXX.md`（例如：`2026-W10.md`）
- 月报：`YYYY-MM.md`（例如：`2026-03.md`）

**文件内容**：
```markdown
# 📅 2026-03-06 健康记录

> 创建时间：2026-03-06 20:46 (用户时区)
> 用户：your_username
```

**获取当前时间**：
- 使用 `session_status` 工具获取当前时间
- 或使用系统时间 + 用户时区
- **必须根据用户配置的时区转换**

**示例**：
```
✅ 正确：2026-03-06 20:46 (根据用户时区显示)
✅ 正确：2026-03-06 07:46 (UTC)
❌ 错误：使用固定时区，不考虑用户配置
```

---

## ⚠️ IMPORTANT: 备份功能说明

**🔒 隐私优先：备份功能需要用户配置，用户完全控制数据**

### 备份策略

**数据存储**：
- ✅ 所有数据存储在本地（`memory/health-users/{username}/`）
- ✅ 备份到 GitHub 需要**用户主动配置**
- ✅ **强烈建议使用私有仓库**
- ✅ 用户可随时禁用备份

**备份触发条件**（必须全部满足）：
1. ✅ 用户在 onboarding 时选择启用备份
2. ✅ 用户提供了 GitHub 仓库 URL
3. ✅ `backup_config.json` 中 `enabled: true`
4. ✅ 用户刚记录了健康数据（饮食/补剂/运动/睡眠）

**❌ 任何条件不满足时**：
- ❌ 不执行备份
- ✅ 数据仅保存在本地

### 备份触发条件

**仅在以下情况触发备份**：
1. ✅ 用户已明确配置 GitHub 备份（在 profile.md 中设置）
2. ✅ 用户主动请求数据更新
3. ✅ 用户手动触发备份命令

**❌ 不会自动触发备份**：
- ❌ 不会在后台自动执行
- ❌ 不会在用户未配置时执行
- ❌ 不会在用户明确禁用时执行

### 启用备份（可选）

**用户想启用备份时**：
```
用户：我想启用 GitHub 备份
AI：
1. 询问 GitHub 仓库 URL
2. 提醒使用私有仓库（重要！）
3. 配置 backup_config.json
4. 测试备份连接
5. 询问是否启用自动备份（可选）
```

### 备份流程（仅当用户启用时）

**当用户已启用备份并记录健康数据后**：
```
1. ✅ 更新每日记录文件（memory/health-users/{username}/daily/YYYY-MM-DD.md）
2. ⚠️ 检查备份是否启用（读取 backup_config.json）
3. ✅ 如果启用：执行备份脚本（bash scripts/backup_health_data.sh）
4. ✅ 验证推送结果（使用 gh repo view 验证）
5. ✅ 向用户反馈备份状态（显示提交哈希、推送状态）
```

**❌ 绝对禁止**：
- ❌ 在用户未配置时自动执行备份
- ❌ 使用公开仓库而不警告用户
- ❌ 跳过备份状态反馈
- ❌ 在用户明确禁用后仍执行备份

**✅ 正确示例**：
```
用户：早餐吃了西兰花、核桃、燕麦...
AI：
  ✅ 1. 更新每日记录文件
  ✅ 2. 执行备份脚本
  ✅ 3. 验证推送结果
  ✅ 4. 反馈：数据已备份！提交哈希：abc1234
```

**❌ 错误示例**（绝对禁止）：
```
用户：早餐吃了西兰花、核桃、燕麦...
AI：
  ✅ 1. 更新每日记录文件
  ❌ 2. （没有执行备份）
  ❌ 3. （没有反馈备份结果）
```

---

## 🚨 Multi-User Support Architecture

**CRITICAL: This skill supports multiple users with personalized tracking.**

### User Identification

**Primary identifier**: User's `label` or `name` from conversation metadata
- **Discord**: Use `username` or `label` field
- **Other platforms**: Use platform-specific user identifier
- **Fallback**: Use name provided in message

**Example identifiers**:
- Discord: `john_doe`, `jane_doe`
- Telegram: `@username` or user ID
- General: Name from conversation context

### Data Storage Structure

```
memory/
├── health-users/                     # Multi-user data directory
│   ├── {username1}/                  # User-specific directory
│   │   ├── profile.md                # Personal health goals
│   │   ├── daily/                    # Daily records (用户时区)
│   │   │   ├── 2026-03-06.md
│   │   │   ├── 2026-03-07.md
│   │   │   └── ...
│   │   ├── weekly/                   # Weekly analysis
│   │   │   ├── 2026-W10.md
│   │   │   └── ...
│   │   └── monthly/                  # Monthly summaries
│   │       ├── 2026-03.md
│   │       └── ...
│   ├── {username2}/
│   │   ├── profile.md
│   │   ├── daily/
│   │   └── ...
│   └── ...
```

### User Identification Workflow

**When receiving ANY health-related message:**

1. **Extract user identity**:
   ```json
   {
     "username": "john_doe",
     "name": "John Doe",
     "platform": "discord"
   }
   ```

2. **Check if user profile exists**:
   - Read: `memory/health-users/{username}/profile.md`
   - If NOT exists → Create new user profile

3. **Load user context**:
   - **Personal goals and priorities** ⭐
   - **Language preference** ⭐ (CRITICAL: 用于输出语言)
   - **Timezone** ⭐ (CRITICAL: 用于时间显示)
   - Recent records (last 7 days)
   - Active challenges/achievements

4. **Process message with user context**:
   - **Apply user's language** (CRITICAL: 所有输出使用用户语言)
   - **Apply user's timezone** (CRITICAL: 所有时间使用用户时区)
   - Apply personalized scoring weights
   - Reference user's specific goals
   - Compare against user's historical data

5. **Save records to user directory**:
   - Daily records: `memory/health-users/{username}/daily/YYYY-MM-DD.md`
   - Weekly analysis: `memory/health-users/{username}/weekly/YYYY-WXX.md`
   - Monthly summary: `memory/health-users/{username}/monthly/YYYY-MM.md`

### 🚨 CRITICAL: Language Output Checklist

**AI must verify BEFORE EVERY response**:

```
✅ 语言检查清单（每次回复前必须验证）：

1. ✅ 已读取用户语言配置
   - 从 profile.md 读取 Language 字段
   - 如果未配置，使用默认语言 zh-CN

2. ✅ 所有输出使用用户语言
   - 标题和说明
   - 数据解读和分析
   - 健康建议
   - 错误提示

3. ✅ 数字和日期格式符合语言习惯
   - 中文：2026年03月14日
   - 英文：March 14, 2026
   - 日文：2026年3月14日

4. ✅ 使用用户语言的术语
   - 中文：防御系统、每日十二清单
   - 英文：Defense Systems, Daily Dozen
   - 日文：防御システム、デイリードーズン
```

### User Profile Template

**File**: `memory/health-users/{username}/profile.md`

```markdown
# 🎯 {username}'s Health Profile

> Created: YYYY-MM-DD
> Last Updated: YYYY-MM-DD

## 👤 Basic Info
- **Name**: {name}
- **Username**: {username}
- **Platform**: {platform}
- **Created**: YYYY-MM-DD

## 🎯 Health Goals (Priority Order)
1. [Goal 1] - Priority: ⭐⭐⭐⭐⭐⭐
2. [Goal 2] - Priority: ⭐⭐⭐⭐⭐
...

## 📊 Personalized Scoring Weights
- Dimension 1: [weight]
- Dimension 2: [weight]
- Dimension 3: [weight]

## 📅 Tracking History
- First Record: YYYY-MM-DD
- Total Records: XX days
- Current Streak: XX days

## 🏆 Achievements
- [ ] Achievement 1
- [ ] Achievement 2
...
```

### Privacy & Isolation

**IMPORTANT**:
- Each user's data is **completely isolated**
- Never reference one user's data in another user's conversation
- Never share personal health information between users
- User profiles are confidential

### Default Behavior for New Users

**When encountering a new user:**

1. **Create profile**: Ask for health goals
2. **Set defaults**: Use standard scoring weights
3. **Provide onboarding**: Explain 3-dimension system
4. **Start tracking**: Begin with first record

**Template**: See [references/new-user-onboarding.md](references/new-user-onboarding.md)

---

## Core Framework

This skill integrates three complementary dietary frameworks:

1. **Dr. Greger's Daily Dozen** (12 items) - Plant-based nutrition checklist
2. **Dr. Li's 5×5×5 Method** - Five foods covering five defense systems, five times daily
3. **10-Book Consensus Checklist** - Evidence-based health principles from top longevity/nutrition books

## 🚨 CRITICAL: Multi-User Identification Required

**BEFORE processing ANY health-related message, you MUST:**

1. **Extract user identity** from conversation metadata:
   - Discord: Use `label` or `username` field
   - Telegram: Use `username` or `user_id`
   - Other platforms: Use platform-specific identifier

2. **Check user profile**:
   ```
   Read: memory/health-users/{username}/profile.md
   ```

3. **If profile NOT exists**:
   - Trigger new user onboarding
   - Create user directory: `memory/health-users/{username}/`
   - Create profile: `memory/health-users/{username}/profile.md`
   - See [references/new-user-onboarding.md](references/new-user-onboarding.md)

4. **If profile exists**:
   - Load user goals and personalized weights
   - Read recent records (last 7 days)
   - Apply user-specific context to analysis

5. **Save records to user directory**:
   ```
   Daily: memory/health-users/{username}/daily/YYYY-MM-DD.md
   Weekly: memory/health-users/{username}/weekly/YYYY-WXX.md
   Monthly: memory/health-users/{username}/monthly/YYYY-MM.md
   ```


---

## 🥢 Chinese Food Support & Dynamic Food Database

### Chinese Food Database

**IMPORTANT**: This skill includes a comprehensive Chinese food database.

**Reference**: [references/chinese-food-database.md](references/chinese-food-database.md)

**Coverage**:
- Chinese vegetables (大白菜、芥蓝、空心菜、茼蒿等)
- Chinese fruits (桑葚、杨梅、枇杷、龙眼等)
- Chinese proteins (豆腐、豆浆、各种鱼类、内脏等)
- Chinese grains (糙米、黑米、小米、燕麦等)
- Chinese spices & herbs (姜、蒜、葱、枸杞、红枣等)
- Chinese dishes (番茄炒蛋、清蒸鱼、蒜蓉西兰花等)

**Usage**: When user mentions Chinese foods, check both databases:
1. [references/food-database.md](references/food-database.md) - Western foods
2. [references/chinese-food-database.md](references/chinese-food-database.md) - Chinese foods

### Dynamic Food Search (CRITICAL)

**When food is NOT found in database:**

**Step 1: Identify unknown food**
```
User: "吃了马齿苋"
AI check: food-database.md + chinese-food-database.md → Not found
```

**Step 2: Search for food information (web_search)**

**Search Strategy**: Use web_search (Brave) for scientific research

```bash
# Search for food information
Search query: "{food_name} 营养成分 健康效益 scientific research"
Example: "马齿苋 营养成分 健康效益 研究"
```

**Step 3: Analyze search results**
Extract from search results:
- Main nutrients (主要营养成分)
- Bioactive compounds (生物活性物质)
- Health benefits (健康效益)
- Defense system mapping (防御系统对应)

**Step 4: Update database**
```markdown
Add to appropriate section in chinese-food-database.md:

| {food_name} | {defense_systems} | {key_nutrients} |

Example:
| 马齿苋 | M+A+I | Omega-3、抗氧化物、膳食纤维 |
```

**Step 5: Apply immediately**
```
"马齿苋 → 微生物组(M) + 血管生成(A) + 免疫(I)"
```

**Example workflow:**

```
User: "早餐吃了燕麦粥配马齿苋"

AI process:
1. 燕麦 → Found in database: M (microbiome)
2. 马齿苋 → NOT found

3. Search (web_search): "马齿苋 营养成分 健康效益"
   Results:
   - Rich in Omega-3 fatty acids
   - Antioxidants (flavonoids, vitamin C)
   - Anti-inflammatory properties
   - Supports gut health

4. Defense system mapping:
   - Omega-3 → Microbiome (M) + Angiogenesis (A)
   - Antioxidants → DNA Protection (D) + Immunity (I)
   - Anti-inflammatory → Immunity (I)
   
   Conclusion: M+A+I

5. Update database:
   Add to chinese-food-database.md under "绿叶蔬菜":
   | 马齿苋 | M+A+I | Omega-3、抗氧化物、膳食纤维 |

6. User response:
   "✅ 马齿苋 → 微生物组(M) + 血管生成(A) + 免疫(I)
   这是一个非常健康的野菜！富含Omega-3和抗氧化物。"
```

### Food Search Best Practices

**DO ✅**:
- Search in both English and Chinese if needed
- Look for scientific research on health benefits
- Focus on bioactive compounds and mechanisms
- Cross-reference multiple sources
- Add to database immediately after confirmation

**DON'T ❌**:
- Don't guess defense systems without research
- Don't skip the search step
- Don't forget to update the database
- Don't provide incomplete information

---

## Quick Start

### ⚠️ 重要说明：称呼适配

**本 skill 中的示例对话使用通用称呼（如"健康助手"、"AI"等）。**

**实际使用时**：
- 请根据你在 `IDENTITY.md` 中设置的 OpenClaw 称呼来交互
- 例如：如果你的 OpenClaw 名叫"小蟹"，则示例中的"健康助手"应替换为"@小蟹"
- 例如：如果你的 OpenClaw 名叫"Jarvis"，则示例中的"健康助手"应替换为"@Jarvis"

---

### 🚨 首次使用引导流程（CRITICAL）

**触发条件**：用户首次使用健康记录功能

**自动执行 Git 环境检查**：
```bash
bash scripts/check_git_config.sh
```

**检查项**：
1. ✅ Git 是否已安装
2. ✅ Git 用户信息是否已配置（user.name、user.email）
3. ✅ SSH 密钥是否存在
4. ✅ GitHub CLI 是否已安装（可选）
5. ✅ Workspace 是否已初始化 Git 仓库
6. ✅ 健康数据目录是否存在

**根据检查结果，执行不同的引导流程**：

---

#### 情况A：Git 未安装

```
⚠️ 检测到 Git 未安装

虽然不影响使用健康记录功能，但建议安装 Git 以启用备份功能。

你可以：
1. 继续使用健康记录（不启用备份）
2. 安装 Git 后配置备份

安装 Git：
- macOS: brew install git
- Linux: sudo apt-get install git
- Windows: https://git-scm.com/download/win

配置备份：配置健康数据备份
```

**流程继续**，不阻塞使用 ✅

---

#### 情况B：Git 已安装，但未配置备份

```
✅ Git 环境检查完成！

检测到 Git 已安装，但尚未配置备份功能。

💾 **配置备份（可选但推荐）**

备份数据会自动推送到 GitHub，安全可靠。
你可以选择：
1. 现在配置备份（推荐）
2. 稍后配置

回复"配置备份"我将引导你完成配置，或回复"稍后配置"跳过。
```

**用户选择**：
- **"配置备份"** → 进入备份配置流程
- **"稍后配置"** 或 **"跳过"** → 完成引导，开始使用

---

#### 情况C：Git 和备份都已配置

```
✅ Git 环境检查完成！
✅ 备份功能已配置！

备份路径：{用户配置的路径}
远程仓库：{GitHub 仓库地址}

🎉 恢复使用！继续记录你的健康数据吧！
```

---

### 💊 Supplement Management (NEW!)

**Comprehensive supplement tracking and analysis system.**

**Reference**: [references/supplement-database.md](references/supplement-database.md)

#### 📦 Personal Supplement Database

**Location**: `memory/health-users/{username}/supplement-database.md`

**Purpose**: 集中管理个人补剂信息，避免每次翻历史记录

**Database Structure**:
```markdown
| 补剂名称 | 品牌 | 每粒剂量 | 有效成分 | 服用时间 | 健康目标 | 状态 | 更新日期 |
|---------|------|---------|---------|---------|---------|------|---------|
| 鱼油 | XX品牌 | 645mg | 613mg EPA+DHA (95%) | 晨间随餐 | 抗炎⭐⭐⭐⭐⭐ | 启用 | 2026-03-06 |
```

**Workflow**:

**⚠️ FIRST-TIME SETUP (NEW USER)**:

When a user first mentions supplements, **MUST guide them to create supplement database**:

```
User: "今天吃了鱼油、维生素D3、镁"

AI (if supplement-database.md NOT exists):
1. 🎯 检测到补剂记录，但数据库不存在
2. 💡 引导用户建立补剂仓库：
   "我发现你还没有建立补剂数据库。为了方便记录，我帮你创建一个补剂仓库吧！
   
   请告诉我以下信息：
   - 鱼油：品牌、每粒剂量、有效成分（如EPA+DHA含量）
   - 维生素D3：品牌、每粒剂量
   - 镁：品牌、每粒剂量、形式（柠檬酸镁/甘氨酸镁等）
   
   建立后，以后你说'和昨天一样的补剂'，我就能直接查数据库记录了！"

3. User provides information
4. Create `supplement-database.md` with full details
5. Backup to GitHub
6. Confirm to user: "✅ 补剂数据库已创建！"
```

**Rules for first-time setup**:
- ✅ **Must check** if `supplement-database.md` exists before recording supplements
- ✅ **Must guide user** to create database if not exists
- ✅ **Must collect** brand, dosage, active ingredients for each supplement
- ✅ **如果用户已启用备份**：执行备份脚本（参考"备份流程"章节）

1. **Recording supplements**:
   ```
   User: "今天吃了和昨天一样的补剂"

   AI:
   1. Query personal supplement database
   2. Extract: 鱼油 645mg, 维生素D3 2000 IU, 柠檬酸镁 400mg
   3. Record to daily file
   4. Backup to GitHub
   ```

2. **Updating database**:
   ```
   User: "我换了鱼油品牌，现在是XX品牌，每粒700mg"

   AI:
   1. Update supplement-database.md
   2. Change "品牌" and "每粒剂量" columns
   3. Update "更新日期" to current date
   4. Backup to GitHub
   5. Confirm to user
   ```

3. **Adding new supplement**:
   ```
   User: "今天开始吃辅酶Q10，每粒200mg"

   AI:
   1. Check if exists in database
   2. If not, ask for details (brand, timing, health goals)
   3. Add new row to database
   4. Record to daily file
   5. Backup to GitHub
   ```

**Rules**:
- ✅ **Must query database first** before recording supplements
- ✅ **Must update database** when user reports brand/dosage changes
- ✅ **如果用户已启用备份**：执行备份脚本（参考"备份流程"章节）
- ✅ Keep historical data (don't delete, just mark "状态" as "停用")

**Key features**:
- 200+ supplements with dosage, timing, and health benefits
- Defense system mapping for each supplement
- Personalized recommendations based on user's 5 health goals
- Daily/weekly/monthly tracking templates
- Automatic optimization suggestions

**Usage**:

**User records supplements**:
```
User: "今天吃了维生素D3 4000IU、鱼油2g、肌酸5g"

AI:
1. Identify supplements from database
2. Map to defense systems:
   - 维生素D3 → DNA保护(D) + 免疫(I)
   - 鱼油 → 血管生成(A) + 微生物组(M) + 免疫(I)
   - 肌酸 → 再生(R)

3. Match to user's goals:
   - 控制血糖⭐⭐⭐⭐⭐⭐: 维生素D3 ✅, 鱼油 ✅
   - 抗衰老⭐⭐⭐⭐⭐: 维生素D3 ✅, 肌酸 ✅
   - 抗炎⭐⭐⭐⭐⭐: 鱼油 ✅
   - 增肌⭐⭐⭐⭐: 肌酸 ✅

4. Provide feedback:
   ✅ 补剂选择很好！覆盖了你的核心目标
   💡 建议：增加α-硫辛酸（血糖控制）和镁（睡眠）
```

**User asks for recommendations**:
```
User: "根据我的目标，推荐补剂"

AI:
根据你的5个目标，推荐核心补剂：

【控制血糖⭐⭐⭐⭐⭐⭐】最高优先级
基础补剂：
- α-硫辛酸 300-600mg/天（空腹）
- 铬 200-400mcg/天（随餐）
- 镁 400-500mg/天（睡前）
- 维生素D3 2000-4000 IU/天（随餐）
- Omega-3 2-3g/天（随餐）

进阶补剂（可选）：
- 肉桂提取物
- 益生菌
- 小檗碱（需医嘱）

【抗衰老⭐⭐⭐⭐⭐】
...
```

**Templates**:
- Daily tracking: [assets/supplement-tracking-template.md](assets/supplement-tracking-template.md)

---

### Recording Daily Diet

**User input format:**
```
Breakfast: [foods]
Lunch: [foods]
Dinner: [foods]
Snacks: [optional]
Exercise: [type + duration]
Fasting: [hours]
```

**Automatic analysis includes:**
- Food categorization → Defense system mapping
- Three-dimension scoring (Daily Dozen + 5×5×5 + Consensus)
- Missing items identification
- Personalized recommendations

### Example Workflow

**User:** "Today I ate oatmeal with blueberries and flaxseed for breakfast, salad with broccoli and salmon for lunch, tomatoes with garlic and olive oil for dinner."

**Agent response:**
```
📊 Today's Analysis

✅ Defense Systems Covered:
- Angiogenesis (A): 7 foods ⭐⭐⭐⭐⭐
- Microbiome (M): 3 foods ⭐⭐⭐
- DNA Protection (D): 4 foods ⭐⭐⭐⭐
- Immunity (I): 2 foods ⭐⭐
- Regeneration (R): 0 foods ⚠️

📈 Scores:
- Daily Dozen: 8/12 (67%)
- 5×5×5: 6/10 (60%)
- Consensus: 125/170 (74%)
- Overall: 139/192 (72%)

💡 Missing Items:
- Regeneration foods: Add coffee, dark chocolate, walnuts, or turmeric
- Berries: Only 1 serving (goal: 1+ daily) ✅
- Cruciferous vegetables: Only 1 serving (goal: 1+ daily) ✅

🎯 Tomorrow's Plan:
1. Add coffee or green tea after breakfast (covers Regeneration)
2. Include walnuts as snack
3. Consider adding turmeric to dinner
```

## 🚨🚨🚨 CRITICAL: 量化评估规则（最高优先级！）

**⚠️ 必须根据实际摄入量评估，不能简单认为"吃了什么就达标"！**

### 核心原则

**❌ 错误评估方式**（绝对禁止）：
```
用户：吃了2个猪肉白菜饺子
AI：✅ 十字花科蔬菜达标！（错误！）
```

**✅ 正确评估方式**（强制执行）：
```
用户：吃了2个猪肉白菜饺子
AI：
1. 估算实际摄入量：2个饺子中白菜约10-15克
2. 对比目标：十字花科蔬菜目标1份（80克）
3. 计算完成度：10-15克 / 80克 = 13%-19%
4. 评估结果：❌ 未达标（仅完成13%-19%）
```

### 量化评估标准

#### 维度一：每日十二清单（必须量化）

| 项目 | 目标量 | 达标标准 | 未达标标准 |
|------|--------|---------|-----------|
| 🫘 豆类 | 3份（240克） | ≥200克（83%） | <200克 |
| 🫐 浆果 | 1份（80克） | ≥60克（75%） | <60克 |
| 🍎 其他水果 | 3份（240克） | ≥200克（83%） | <200克 |
| 🥦 十字花科蔬菜 | 1份（80克） | ≥60克（75%） | <60克 |
| 🥬 绿叶菜 | 2份（160克） | ≥120克（75%） | <120克 |
| 🥕 其他蔬菜 | 2份（160克） | ≥120克（75%） | <120克 |
| 🌱 亚麻籽 | 1份（1汤匙） | ≥1汤匙 | <1汤匙 |
| 🥜 坚果 | 1份（30克） | ≥25克（83%） | <25克 |
| 🌿 香料 | 1份（含姜黄） | 包含姜黄 | 不含姜黄 |
| 🌾 全谷物 | 3份（240克） | ≥200克（83%） | <200克 |
| 💧 饮品 | 5份（2.5升） | ≥2升（80%） | <2升 |
| 🏃 运动 | 1次（30分钟） | ≥30分钟 | <30分钟 |

**评分规则**：
- ✅ 达标：完成度 ≥75%
- ⚠️ 部分达标：完成度 50%-74%
- ❌ 未达标：完成度 <50%

**示例**：
```markdown
用户：晚餐吃了韭菜鸡蛋饺子5个、素三鲜饺子5个

AI评估：
1. 绿叶菜（韭菜）：
   - 估算摄入量：5个韭菜饺子 + 5个素三鲜饺子 ≈ 30-40克韭菜
   - 目标：160克
   - 完成度：30-40克 / 160克 = 19%-25%
   - 结果：❌ 未达标（仅完成19%-25%）

2. 优质蛋白质（鸡蛋）：
   - 估算摄入量：10个饺子中鸡蛋 ≈ 50-60克
   - 目标：100克/餐
   - 完成度：50-60克 / 100克 = 50%-60%
   - 结果：⚠️ 部分达标（完成50%-60%）

结论：绿叶菜严重不足，蛋白质部分达标
```

#### 维度二：5×5×5（量化覆盖度）

**防御系统覆盖标准**：
- ✅ **充分覆盖**：食物分量 ≥50克 或 2种以上食物
- ⚠️ **部分覆盖**：食物分量 20-50克 或 1种食物
- ❌ **未覆盖**：食物分量 <20克 或 无相关食物

**示例**：
```markdown
用户：晚餐吃了韭菜鸡蛋饺子

AI评估：
1. 血管生成(A) - 韭菜：
   - 摄入量：30-40克
   - 结果：⚠️ 部分覆盖（<50克）

2. 再生(R) - 鸡蛋：
   - 摄入量：50-60克
   - 结果：✅ 充分覆盖（≥50克）

结论：5个防御系统中，1个充分覆盖，4个未覆盖
```

#### 维度三：共识清单（量化健康习惯）

**健康食物评分标准**：
- ✅ **满分（10分）**：达到推荐量的80%以上
- ⚠️ **部分分（5-9分）**：达到推荐量的50%-79%
- ❌ **低分（0-4分）**：达到推荐量的50%以下

**限制食物惩罚标准**：
- 每次消费精制糖：-2分
- 每次消费精制碳水：-2分
- 每次消费加工食品：-2分
- 每次消费油炸食品：-2分

**生活方式评分标准**：
- ✅ **满分（10分）**：严格执行
- ⚠️ **部分分（5-9分）**：部分执行
- ❌ **低分（0-4分）**：未执行或执行很差

### 强制执行流程

**当用户记录饮食时，AI必须执行以下流程**：

1. **✅ 估算实际摄入量**（克数、份数）
2. **✅ 对比目标量**（每日十二清单目标）
3. **✅ 计算完成度百分比**
4. **✅ 根据完成度评估**（达标/部分达标/未达标）
5. **✅ 明确标注未达标项**
6. **✅ 提供具体改进建议**（需要补充多少克）

**❌ 绝对禁止**：
- ❌ 简单说"吃了XX就达标"
- ❌ 不估算实际摄入量
- ❌ 不计算完成度百分比
- ❌ 隐瞒未达标项

**✅ 正确示例**：
```
用户：晚餐吃了17个饺子（5个韭菜鸡蛋、5个素三鲜、5个猪肉笋丁、2个猪肉白菜）

AI评估：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 绿叶菜评估（目标：160克）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 韭菜：30-40克（10个饺子馅）
• 白菜：10-15克（2个饺子馅）
• 总计：40-55克
• 完成度：40-55克 / 160克 = 25%-34%
• 结果：❌ 未达标（仅完成25%-34%）
• 需补充：105-120克绿叶菜

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 十字花科蔬菜评估（目标：80克）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 白菜：10-15克（2个饺子馅）
• 完成度：10-15克 / 80克 = 13%-19%
• 结果：❌ 未达标（仅完成13%-19%）
• 需补充：65-70克十字花科蔬菜

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 优质蛋白质评估（目标：100克/餐）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 鸡蛋：50-60克（10个饺子）
• 猪肉：30-40克（7个饺子）
• 虾仁：10-15克（5个饺子）
• 总计：90-115克
• 完成度：90-115克 / 100克 = 90%-115%
• 结果：✅ 达标（完成90%-115%）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 改进建议
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 补充绿叶菜：建议加一份凉拌菠菜（100克）
2. 补充十字花科：建议加一份西兰花（100克）
```

---

## Three-Dimension Scoring System (统一10分制)

**重要改进**：所有三个维度统一归一化到10分制，便于直观比较和综合评估。

**总分**：30分（10+10+10）

---

### 维度一：每日十二清单 (10分)

**原始评分**：12项，每项1分，满分12分
**归一化公式**：`(实际得分/12) × 10`，四舍五入到1位小数

**⚠️ 必须量化评估（见上方规则）**

**清单项目**：
- 🫘 豆类 ×3
- 🫐 浆果 ×1
- 🍎 其他水果 ×3
- 🥦 十字花科蔬菜 ×1
- 🥬 绿叶菜 ×2
- 🥕 其他蔬菜 ×2
- 🌱 亚麻籽 ×1
- 🥜 坚果 ×1
- 🌿 香料 ×1（必须包含姜黄）
- 🌾 全谷物 ×3
- 💧 饮品 ×5
- 🏃 运动 ×1

**评分示例**：
- 完成12项 → 12/12 × 10 = **10.0分** ⭐⭐⭐⭐⭐
- 完成9项 → 9/12 × 10 = **7.5分** ⭐⭐⭐
- 完成6项 → 6/12 × 10 = **5.0分** ⭐⭐

---

### 维度二：5×5×5方法 (10分)

**原始评分**：5个防御系统（5分）+ 5次进食分布（5分）= 10分
**归一化**：已经是10分制，无需转换

**第一步：覆盖5个防御系统**（5分）
| 防御系统 | 关键食物 | 得分 |
|---------|---------|------|
| 血管生成 (A) | 番茄、浆果、绿茶、西兰花 | 1分 |
| 再生 (R) | 咖啡、黑巧克力、核桃、姜黄 | 1分 |
| 微生物组 (M) | 酸奶、燕麦、洋葱、豆类 | 1分 |
| DNA保护 (D) | 蓝莓、绿叶菜、坚果 | 1分 |
| 免疫 (I) | 大蒜、生姜、蘑菇、柑橘 | 1分 |

**第二步：分布在5次进食**（5分）
- 早餐 → 1分
- 午餐 → 1分
- 晚餐 → 1分
- 加餐 → 1分
- 饮品/甜点 → 1分

**多功能食物**（覆盖3+系统）：
- 蓝莓：A+D+I
- 西兰花：A+D+I
- 亚麻籽：M+D+A
- 绿茶：A+M+I
- 核桃：R+D+A
- 黑巧克力：A+R+M
- 大蒜：A+I+M

**评分示例**：
- 覆盖5个系统 + 5次进食 → **10.0分** ⭐⭐⭐⭐⭐
- 覆盖3个系统 + 3次进食 → 6/10 × 10 = **6.0分** ⭐⭐⭐

---

### 维度三：共识清单 (10分)

**原始评分**：170分（健康食物70分 + 限制食物50分 + 生活方式50分）
**归一化公式**：`(实际得分/170) × 10`，四舍五入到1位小数

#### 健康食物（原始70分）

**评分标准**：每项0-10分
- 十字花科蔬菜
- 深色绿叶菜
- 浆果
- 健康脂肪
- 发酵食物
- 豆类
- 鱼类（如适用）

**小计**：7项 × 10分 = 70分

#### 限制食物（原始50分）

**评分标准**：完全避免10分，每次消费-2分
- 精制糖
- 精制碳水
- 加工食品
- 反式脂肪
- 果糖/果汁

**小计**：5项 × 10分 = 50分

#### 生活方式（原始50分）

**评分标准**：每项0-10分
- 间歇性禁食（12-16小时）
- 饮食顺序（蔬菜→蛋白质→碳水）
- 有氧运动（≥30分钟）
- 力量训练（2-3次/周）
- 睡眠质量（7-9小时）

**小计**：5项 × 10分 = 50分

**总分**：70 + 50 + 50 = 170分

**归一化示例**：
- 153分 → 153/170 × 10 = **9.0分** ⭐⭐⭐⭐⭐
- 136分 → 136/170 × 10 = **8.0分** ⭐⭐⭐⭐
- 119分 → 119/170 × 10 = **7.0分** ⭐⭐⭐
- 85分 → 85/170 × 10 = **5.0分** ⭐⭐

---

### 综合评分（30分制）

**计算公式**：`维度一得分 + 维度二得分 + 维度三得分`

**评级标准**（百分比制）：
- 🌟🌟🌟🌟🌟 90-100% (27-30分): 优秀
- 🌟🌟🌟🌟 80-89% (24-26.9分): 很好
- 🌟🌟🌟 70-79% (21-23.9分): 良好
- 🌟🌟 60-69% (18-20.9分): 及格
- 🌟 <60% (<18分): 需要改进

**示例评分**：
```
维度一：9/12项 → 9/12 × 10 = 7.5分
维度二：8/10分 → 8.0分
维度三：136/170分 → 136/170 × 10 = 8.0分

总分：7.5 + 8.0 + 8.0 = 23.5/30 (78%) ⭐⭐⭐ 良好
```

---

### 补剂加分系统（可选）

**补剂对综合评分的积极影响**：

| 贡献项 | 加分 | 说明 |
|--------|------|------|
| 防御系统覆盖率提升 | +0.5-1.0分 | 从<50%提升到>80% |
| 目标匹配补剂到位 | +0.5-1.0分 | 核心补剂组合完整 |
| 剂量优化 | +0.3-0.5分 | 剂量在推荐范围内 |

**最高加分**：+2.5分

**最终得分上限**：32.5/30（可超过100%）

**示例**：
```
基础得分：23.5/30 (78%)
补剂加分：+1.5分（防御系统覆盖率提升+目标匹配）

最终得分：25.0/30 (83%) ⭐⭐⭐⭐ 很好
```

## Analysis & Reporting

### 🚨 Summary文件生成规则（CRITICAL）

**⚠️ 每次生成总结报告时，必须创建单独的summary文件！这不是可选项！**

#### 强制执行规则

**当用户要求总结时（"总结今日表现"、"给我总结下"等），必须执行以下流程**：

```
1. ✅ 生成单独的summary文件
2. ✅ 文件路径：memory/health-users/{username}/daily/YYYY-MM-DD-summary.md
3. ✅ 文件内容包含完整的分析报告（评分、亮点、改进建议等）
4. ✅ 立即执行备份脚本（bash scripts/backup_health_data.sh）
5. ✅ 向用户反馈文件生成和备份状态
```

#### Summary文件模板

**文件命名**：`YYYY-MM-DD-summary.md`

**文件结构**：
```markdown
# 📊 YYYY-MM-DD 健康管理总结报告

> 生成时间：YYYY-MM-DD HH:MM (用户时区)
> 用户：{username}

---

## 🌟 今日总评：{评级}

**综合评分**：**XX.X/30 (XX%)** 🎉

**评级**：{优秀/良好/及格/需要改进}

**进步**：相比上次提升了 X.X分！

---

## 📊 三维度评分总览

### 维度一：每日十二清单（X.X/10）
...

### 维度二：5×5×5（X.X/10）
...

### 维度三：共识清单（X.X/10）
...

---

## 😴 睡眠质量
...

## 🍽️ 饮食记录
...

## 🏃 运动记录
...

## 💊 补剂记录
...

## 🎯 目标匹配度评估
...

## 📈 今日亮点
...

## 💡 明日改进建议
...

---

**报告生成时间**：YYYY-MM-DD HH:MM (用户时区)
**数据来源**：Apple Health + 用户自述
**备份状态**：已备份到 GitHub（提交哈希：xxxxxxx）
```

#### ❌ 绝对禁止

- ❌ 只在对话中回复总结，不生成文件
- ❌ 生成文件后不执行备份
- ❌ 说"稍后生成文件"或"等会再备份"
- ❌ 不向用户反馈文件生成和备份状态

#### ✅ 正确示例

**用户**："给我总结下今日表现"

**AI**：
1. ✅ 读取每日记录文件
2. ✅ 生成 `2026-03-11-summary.md`
3. ✅ 执行备份脚本
4. ✅ 反馈：
```
✅ 已生成总结文件！
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 文件：2026-03-11-summary.md
• 提交哈希：ab6da30
• 推送状态：成功
```

#### 📁 文件结构示例

```
daily/
├── 2026-03-06.md
├── 2026-03-06-summary.md ⭐
├── 2026-03-07.md
├── 2026-03-07-summary.md ⭐
├── 2026-03-08.md
├── 2026-03-08-summary.md ⭐
├── ...
```

#### 💡 为什么必须生成单独的summary文件？

1. **便于GitHub查看**：用户可以在GitHub上直接查看历史总结
2. **便于历史追溯**：独立的summary文件便于快速查找和对比
3. **与weekly/monthly保持一致**：周报、月报都是独立文件，日报也应该如此
4. **便于分享**：独立的summary文件便于分享给医生或营养师

---

### Daily Analysis

Automatic calculation of:
- Three-dimension scores
- Defense system coverage
- Missing critical items
- Next-day action items

**⚠️ 重要**：Daily Analysis不是总结报告！只是每日记录文件中的数据分析部分。当用户要求"总结"时，必须生成单独的summary文件！

### Weekly Analysis (request: "weekly analysis")

Read the past 7 days' records and generate:
- Average scores per dimension
- Trend identification (improving/declining/stable)
- Top 3 achievements
- Top 3 challenges
- Specific improvement recommendations

**Template:** See [assets/weekly-analysis-template.md](assets/weekly-analysis-template.md)

### Monthly Analysis (request: "monthly analysis")

Generate comprehensive report including:
- Week-by-week trends
- Weight/waist circumference changes
- Achievement unlocks (7-day streak, 30-day streak, etc.)
- Habit formation assessment
- Next month goals

**Template:** See [assets/monthly-summary-template.md](assets/monthly-summary-template.md)

### Yearly Summary (request: "yearly analysis")

Long-term trend analysis:
- Monthly progression charts
- Major health improvements
- Sustainable habits formed
- Next year focus areas

## Food Defense System Database

For complete food-to-defense-system mapping, see [references/food-database.md](references/food-database.md)

**Quick reference - Top multi-functional foods:**
1. Blueberries → A+D+I
2. Broccoli → A+D+I
3. Flaxseeds → M+D+A
4. Green tea → A+M+I
5. Walnuts → R+D+A
6. Dark chocolate → A+R+M
7. Garlic → A+I+M

**Usage:** When user mentions a food, automatically identify which defense system(s) it supports.

## Recording Templates

### Quick Daily Log
For simple daily tracking, use [assets/quick-log.md](assets/quick-log.md)

### Comprehensive Tracking
For detailed recording including reflections, use [assets/daily-tracking-template.md](assets/daily-tracking-template.md)

## Health Principles Reference

For the complete consensus principles from 10 health books, see [references/principles.md](references/principles.md)

**Core principles (all 10 books agree):**
1. Eat plenty of vegetables (especially cruciferous)
2. Avoid processed foods
3. Control blood sugar/insulin
4. Include healthy fats
5. Practice intermittent fasting

## Analysis Methodology

For detailed analysis guidance and pattern recognition, see [references/analysis-guide.md](references/analysis-guide.md)

## Usage Patterns

### Pattern 1: Daily Recording（每日记录）
**完整流程（备份为可选）**：
1. User provides food intake（用户提供饮食信息）
2. Agent analyzes and scores（AI 分析并评分）
3. **Agent updates daily record file（AI 更新每日记录文件）**
4. **⚠️ 如果用户已启用备份：Agent executes backup script（AI 执行备份脚本）** 
5. Agent provides feedback and recommendations（AI 提供反馈和建议）
6. **⚠️ 如果执行了备份：Agent reports backup status to user（AI 向用户报告备份状态）**

**注意**：备份仅在用户配置并启用时执行（检查 backup_config.json）

### Pattern 2: Periodic Review（定期回顾）
User requests "weekly/monthly/yearly analysis" → Agent reads records → Generates comprehensive report with trends and insights

### Pattern 3: Food Inquiry（食物查询）
User asks about specific food → Agent identifies defense system(s) and nutritional benefits

### Pattern 4: Goal Setting（目标设定）
User specifies health goals (anti-aging, weight loss, muscle gain) → Agent customizes recommendations and prioritizes relevant metrics

### Pattern 5: Sleep Recording（睡眠记录）
**完整流程（备份为可选）**：
1. User provides sleep data（用户提供睡眠数据）
2. **Agent updates daily record file（AI 更新每日记录文件）**
3. **⚠️ 如果用户已启用备份：Agent executes backup script（AI 执行备份脚本）**
4. Agent provides sleep analysis and recommendations（AI 提供睡眠分析和建议）
5. **⚠️ 如果执行了备份：Agent reports backup status to user（AI 向用户报告备份状态）**

## Important Notes

### ⚠️ IMPORTANT: 备份是可选的，默认关闭

- **🔒 默认行为：所有数据仅存储在本地，不上传到任何服务器**
- **✅ 用户可选择启用 GitHub 备份（需显式配置）**
- **⚠️ 如果用户启用了备份，备份脚本会在数据更新后执行**
- **✅ 必须向用户反馈备份状态（提交哈希、推送结果）**
- **❌ 如果备份失败，必须如实告知用户**
- **❌ 如果用户未启用备份，不要执行备份脚本**

### 其他重要事项

- **Personalization:** Adapt recommendations based on user's specific goals, allergies, and preferences
- **Progressive improvement:** Focus on 1-3 changes at a time rather than overwhelming overhaul
- **80/20 rule:** Aim for 80% compliance, allow 20% flexibility
- **Data-driven:** Base recommendations on actual recorded data, not assumptions
- **Positive reinforcement:** Celebrate achievements and streaks to maintain motivation

## Quick Commands

- "Today's analysis" - Analyze today's food intake
- "Weekly analysis" - Generate weekly report
- "Monthly analysis" - Generate monthly summary
- "Backup data" - Manually trigger backup to GitHub（手动触发备份）

---

## 🔄 数据备份到 GitHub（可选功能）

### ⚠️ IMPORTANT: 备份是可选的，默认关闭

**🔒 隐私优先：默认所有数据仅存储在本地，不上传到任何服务器**

**用户可选择启用 GitHub 备份**（需显式配置）

#### ✅ 备份启用条件（必须同时满足）

**备份仅在以下条件全部满足时执行**：
1. ✅ **用户已配置 GitHub 仓库**（在 `backup_config.json` 中设置）
2. ✅ **用户已显式启用备份**（`backup_config.json` 中 `enabled: true`）
3. ✅ **用户刚记录了健康数据**（饮食/补剂/运动/睡眠）
4. ✅ **备份脚本可执行**（`scripts/backup_health_data.sh` 存在且有执行权限）

**❌ 任何条件不满足时**：
- ❌ **不执行备份脚本**
- ❌ **不向 GitHub 推送数据**
- ✅ **数据仅保存在本地**

#### 📋 备份执行流程（仅当启用时）

**当所有启用条件满足时，AI 应执行以下流程**：

1. ✅ **检查备份是否启用**（读取 `backup_config.json`）
   ```bash
   # 如果 backup_config.json 不存在或 enabled: false
   # → 跳过备份，数据仅保存本地
   ```

2. ✅ **如果启用：更新每日记录文件**（`memory/health-users/{username}/daily/YYYY-MM-DD.md`）

3. ✅ **如果启用：执行备份脚本**（`bash scripts/backup_health_data.sh`）

4. ✅ **如果启用：验证推送结果**（使用 `gh repo view` 验证）

5. ✅ **如果启用：向用户反馈备份状态**（显示提交哈希、推送状态）

**❌ 绝对禁止**：
- ❌ 在用户未配置时自动执行备份
- ❌ 在用户明确禁用后仍执行备份
- ❌ 使用公开仓库而不警告用户
- ❌ 不向用户反馈备份结果

**✅ 正确示例（用户已启用备份）**：
```
用户：早餐吃了西兰花、核桃、燕麦...
AI：
1. 检查 backup_config.json → enabled: true ✅
2. 更新每日记录文件 ✅
3. 执行备份脚本 ✅
4. 验证推送结果 ✅
5. 反馈：✅ 数据已备份！提交哈希：abc1234
```

**✅ 正确示例（用户未启用备份）**：
```
用户：早餐吃了西兰花、核桃、燕麦...
AI：
1. 检查 backup_config.json → 不存在或 enabled: false ✅
2. 更新每日记录文件 ✅
3. 跳过备份（用户未启用）✅
4. 反馈：✅ 已记录！数据保存在本地
```

**❌ 错误示例（绝对禁止）**：
```
用户：早餐吃了西兰花、核桃、燕麦...
AI：
1. 更新每日记录文件 ✅
2. （未检查 backup_config.json 就执行备份）❌
3. （在用户未启用时推送数据）❌
```

### 备份流程（仅当用户启用时）

**自动触发条件**（必须全部满足）：
1. ✅ 用户已配置并启用 GitHub 备份
2. ✅ 用户记录了饮食/补剂/运动/睡眠
3. ✅ AI 检查并确认备份已启用

**执行步骤**（仅在启用时）：
1. ✅ 用户记录饮食/补剂/运动/睡眠
2. ✅ AI 检查备份是否启用
3. ✅ **如果启用：AI 更新每日记录文件**
4. ✅ **如果启用：AI 执行备份脚本**
5. ✅ **如果启用：AI 提交到本地 Git 仓库**
6. ✅ **如果启用：AI 推送到 GitHub 远程仓库**
7. ✅ **如果启用：AI 验证推送结果**
7. ✅ **反馈备份状态给用户**（必须！）

**备份脚本位置**：
```
~/.openclaw/workspace/skills/health-management/scripts/backup_health_data.sh
```

**备份仓库位置**：
```
~/Documents/health-backup/
├── .git/                      # Git 仓库
├── .gitignore                 # Git 忽略规则
├── README.md                  # 仓库说明文档
└── health-users/              # 健康数据（从 workspace 自动同步）
    ├── john_doe/              # 用户 john_doe 的数据
    │   ├── profile.md         # 个人健康档案
    │   ├── daily/             # 每日记录
    │   ├── weekly/            # 每周分析
    │   └── monthly/           # 每月总结
    └── ou_xxx/                # 其他用户数据
```

**GitHub 远程仓库**：
- 🔒 仓库类型：Private（私有仓库）
- 📦 仓库地址：https://github.com/YOUR_USERNAME/YOUR_REPO_NAME
- 🔄 自动同步：每次记录健康数据后自动推送

### 备份范围

**源数据目录**：
```
~/.openclaw/workspace/memory/health-users/
├── john_doe/
│   ├── profile.md              # 个人健康档案
│   ├── daily/                  # 每日记录
│   ├── weekly/                 # 每周分析
│   └── monthly/                # 每月总结
└── jane_doe/                   # 其他用户数据
```

**备份内容**：
- ✅ 所有用户的健康档案
- ✅ 所有每日记录
- ✅ 所有周报/月报
- ✅ 所有历史数据

### 备份规范

**参考标准**：充电管理技能 (charging-ledger) 的备份逻辑

**Git 操作**：
```bash
# 1. 检查是否有变更
git diff-index --quiet HEAD -- memory/health-users/

# 2. 添加健康数据目录
git add memory/health-users/

# 3. 创建提交
git commit -m "🏥 健康数据备份 - YYYY年MM月DD日 HH:MM:SS CST

变更文件：X 个
新增行数：Y
删除行数：Z"

# 4. 推送到 GitHub
git push origin main

# 5. 验证推送
gh repo view --json updatedAt,homepageUrl
```

**提交信息格式**：
```
🏥 健康数据备份 - 2026年03月06日 22:00:00 CST

变更文件：2 个
新增行数：150
删除行数：20
```

### 备份验证

**使用 gh 命令验证**：
```bash
gh repo view --json updatedAt,homepageUrl --jq '最后更新: \(.updatedAt) | 仓库地址: \(.homepageUrl)'
```

**验证内容**：
- ✅ 最后更新时间
- ✅ 仓库地址
- ✅ 提交哈希值

### 备份反馈

**成功反馈**：
```
🔄 数据同步
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 提交哈希：abc1234
• 推送状态：成功
• 仓库地址：https://github.com/YOUR_USERNAME/YOUR_REPO_NAME
• 最后更新：2026-03-06T14:00:00Z

✅ 健康数据已安全备份到 GitHub！
```

**失败反馈**：
```
❌ 备份未完成

🔄 数据同步失败
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 推送状态：失败
• 错误信息：[具体错误信息]

💡 建议：
• 检查网络连接
• 检查 Git 配置
• 手动执行：./scripts/backup_health_data.sh
```

### 手动备份

**命令**：
```bash
cd ~/.openclaw/workspace
./skills/health-management/scripts/backup_health_data.sh
```

**适用场景**：
- 自动备份失败时
- 需要立即备份时
- 批量数据导入后

### GitHub 仓库配置

**首次配置**：
```bash
# 1. 确保 workspace 已初始化 Git
cd ~/.openclaw/workspace
git init

# 2. 添加远程仓库（如果未配置）
git remote add origin https://github.com/YOUR_USERNAME/openclaw-workspace.git

# 3. 推送到 GitHub
git push -u origin main
```

**推荐配置**：
- 🔒 设置为 Private 仓库（隐私保护）
- 🔑 配置 SSH 密钥（免密推送）
- 📅 定期检查备份状态

### 时区要求

⚠️ **重要：所有时间操作必须使用用户配置的时区**

**时区配置位置**：
- 用户配置：`memory/health-users/{username}/profile.md`
- 默认时区：`Asia/Shanghai`（北京时间，UTC+8）

**时间格式化示例**：
```bash
# 读取用户时区
timezone=$(get_user_timezone "$username")

# 使用用户时区格式化时间
TZ="$timezone" date '+%Y年%m月%d日 %H:%M:%S %Z'
```

### 错误处理

**常见错误**：

1. **没有变更需要备份**
   - 状态：正常，无需操作
   - 反馈：`ℹ️ 没有需要备份的更改`

2. **推送失败**
   - 原因：网络问题、权限问题
   - 处理：如实反馈错误信息，建议手动备份

3. **gh 命令验证失败**
   - 原因：gh 未安装或未认证
   - 处理：跳过验证，提供仓库链接

**错误反馈原则**：
- ✅ 如实反馈错误信息
- ❌ 不编造推送结果
- ❌ 不隐瞒错误
- ✅ 提供解决建议

### 备份安全

**数据隐私**：
- 🔒 GitHub 仓库设置为 Private
- 🔐 只有你能访问自己的数据
- 🚫 不公开分享健康数据

**数据完整性**：
- ✅ Git 版本控制
- ✅ 完整历史记录
- ✅ 可随时回滚

**数据隔离**：
- ✅ 不同用户数据完全隔离
- ✅ 每个用户独立目录
- ✅ 互不干扰

### 🚨 文件操作安全（CRITICAL）

**⚠️ 绝对禁止的危险操作**：

**❌ 禁止：文件追加到自身**
```bash
# ❌ 错误示例 - 会导致无限循环，文件爆炸式增长
cat file.md >> file.md
echo "内容" >> file.md >> file.md
```

**原因**：
- `cat file >> file` 会导致文件**无限循环复制自身**
- 文件会从几百KB → 几GB → 几十GB → 填满磁盘
- **真实案例**：2026-03-10，68GB备份文件就是因此产生

**✅ 正确的文件操作方法**：

**方法1：使用 edit 工具（推荐）**
```markdown
1. 先 read 文件
2. 使用 edit 工具追加内容
3. 精确控制，不会出错
```

**方法2：使用临时文件**
```bash
# ✅ 正确 - 使用临时文件
cat file.md > temp.md
echo "新内容" >> temp.md
mv temp.md file.md
```

**方法3：使用 write 工具（完全重写）**
```markdown
1. read 原文件
2. 构造新内容（原内容 + 新内容）
3. write 完整内容
```

**⚠️ 强制检查清单**：
- ✅ 追加文件前，确认源文件 ≠ 目标文件
- ✅ 使用 edit 工具而不是 cat >>
- ✅ 文件大小超过 1MB 时，立即停止并警告
- ✅ 定期检查 `.backup`、`.append` 等临时文件

**🚨 紧急处理流程**：
如果发现异常大文件（>10MB）：
1. ✅ 立即删除异常文件
2. ✅ 检查 .gitignore 是否正确配置
3. ✅ 清理 Git 历史（`git gc --prune=now`）
4. ✅ 更新 .gitignore 防止再次提交

- "What does [food] support?" - Identify defense system(s)
- "Am I missing anything?" - Check for gaps in today's intake

---

## 📋 输出格式规范

⚠️ **重要：所有健康报告必须遵循固定格式，确保输出一致性**

### 🎯 核心原则

1. **打分规则简要说明**：每次输出必须包含一句话解释
2. **防御系统显示**：必须显示中文名称，不能只显示字母
3. **固定格式**：严格按照模板输出，确保一致性

---

### 📊 评分规则简要说明（每次必须包含）

**标准模板**：
```
📋 评分说明：总分30分（3个维度各10分）
• 维度一（每日十二）：营养多样性，需全天覆盖
• 维度二（5×5×5）：防御系统，单餐可满分
• 维度三（共识清单）：健康习惯，需全天+生活方式
```

**简短版（单餐输出）**：
```
📋 评分说明：总分30分（3维度×10分）| 维度二（防御系统）单餐可满分
```

---

### 🛡️ 防御系统显示规范

**必须格式**：`中文名称 (字母)`

**标准列表**：
- ✅ **血管生成 (A)**：番茄、浆果、绿茶、西兰花
- ✅ **再生 (R)**：咖啡、黑巧克力、核桃、姜黄
- ✅ **微生物组 (M)**：酸奶、燕麦、洋葱、豆类
- ✅ **DNA保护 (D)**：蓝莓、绿叶菜、坚果
- ✅ **免疫 (I)**：大蒜、生姜、蘑菇、柑橘

**错误示例** ❌：
- A（血管生成）
- A: 血管生成
- 血管生成A

**正确示例** ✅：
- 血管生成 (A)
- 再生 (R)
- 微生物组 (M)

---

### 📝 单餐记录输出模板

```markdown
## 🍽️ [餐次]记录 ([日期])

### 📊 评分总览

📋 评分说明：总分30分（3维度×10分）| 维度二（防御系统）单餐可满分

| 维度 | 得分 | 评价 |
|------|------|------|
| **维度一：每日十二** | X.X/10 | ⭐ 评价 |
| **维度二：5×5×5** | X.X/10 | ⭐⭐⭐ 评价 |
| **维度三：共识清单** | X.X/10 | ⭐⭐⭐ 评价 |
| **总分** | **XX.X/30** | **XX%** ⭐⭐ |

---

### 🥗 食物清单

| 食物 | 分量 | 防御系统 | 营养亮点 |
|------|------|---------|---------|
| 食物1 | 中份 | 系统名称 (字母) | 亮点 |
| 食物2 | 中份 | 系统名称 (字母) | 亮点 |

---

### 🛡️ 防御系统覆盖（维度二）

**已覆盖系统**（X/5）：
- ✅ **血管生成 (A)**：食物列表
- ✅ **再生 (R)**：食物列表
- ✅ **微生物组 (M)**：食物列表
- ✅ **DNA保护 (D)**：食物列表
- ✅ **免疫 (I)**：食物列表

**未覆盖系统**：
- ❌ 系统名称 (字母)：建议食物

**防御系统得分**：X/5分

---

### 📋 每日十二清单（维度一）

| 项目 | 本次包含 | 今日累计 | 目标 |
|------|---------|---------|------|
| 🫘 豆类 | ✅/❌ | X/3 | 3 |
| 🫐 浆果 | ✅/❌ | X/1 | 1 |
| 🍎 其他水果 | ✅/❌ | X/3 | 3 |
| 🥦 十字花科 | ✅/❌ | X/1 | 1 |
| 🥬 绿叶菜 | ✅/❌ | X/2 | 2 |
| 🥕 其他蔬菜 | ✅/❌ | X/2 | 2 |
| 🌱 亚麻籽 | ✅/❌ | X/1 | 1 |
| 🥜 坚果 | ✅/❌ | X/1 | 1 |
| 🌿 香料 | ✅/❌ | X/1 | 1 |
| 🌾 全谷物 | ✅/❌ | X/3 | 3 |
| 💧 饮品 | ✅/❌ | X/5 | 5 |
| 🏃 运动 | ✅/❌ | X/1 | 1 |

**得分**：X/12 → X.X/10

---

### ✅ 健康习惯（维度三）

#### 健康食物
- ✅ 十字花科蔬菜：评价
- ✅ 健康脂肪：评价
- ⚠️ 缺少：建议

#### 限制食物
- ✅ 避免精制糖：评价
- ✅ 避免加工食品：评价

#### 生活方式
- ✅ 饮食顺序：评价
- ⚠️ 运动：建议
- ⚠️ 睡眠：建议

---

### 🌟 亮点与改进

**✅ 亮点**：
1. 亮点1
2. 亮点2

**⚠️ 改进建议**：
1. 建议1
2. 建议2

---

### 🎯 今日目标进度

| 目标 | 状态 | 备注 |
|------|------|------|
| ✅ 目标1 | 已完成 | 备注 |
| ⏳ 目标2 | 进行中 | 备注 |
| ❌ 目标3 | 未完成 | 备注 |

---

### 📈 与上次对比

| 指标 | 上次 | 本次 | 变化 |
|------|------|------|------|
| 总分 | X.X/30 | X.X/30 | +X.X |
| 防御系统 | X/5 | X/5 | +X |

---

### 💡 下一步建议

**午餐/晚餐建议**：
- 建议1
- 建议2

**今日重点**：
- 重点1
- 重点2
```

---

### 📊 每日总结输出模板

```markdown
## 📅 [日期]健康总结

### 📊 三维度评分总览

📋 评分说明：总分30分（3维度×10分）| 全天数据更准确

| 维度 | 得分 | 评价 | 说明 |
|------|------|------|------|
| **维度一：每日十二** | X.X/10 | ⭐⭐⭐ | 营养多样性 |
| **维度二：5×5×5** | X.X/10 | ⭐⭐⭐ | 防御系统覆盖 |
| **维度三：共识清单** | X.X/10 | ⭐⭐⭐ | 健康习惯 |
| **总分** | **XX.X/30** | **XX%** | **综合评价** |

---

### 🍽️ 全天饮食回顾

**早餐**：X.X/10 ⭐⭐⭐
- 食物列表
- 防御系统覆盖：X/5

**午餐**：X.X/10 ⭐⭐⭐
- 食物列表
- 防御系统覆盖：X/5

**晚餐**：X.X/10 ⭐⭐⭐
- 食物列表
- 防御系统覆盖：X/5

**加餐/饮品**：
- 食物列表

---

### 🛡️ 防御系统全天覆盖

**累计覆盖**：
- ✅ **血管生成 (A)**：X次 | 食物列表
- ✅ **再生 (R)**：X次 | 食物列表
- ✅ **微生物组 (M)**：X次 | 食物列表
- ✅ **DNA保护 (D)**：X次 | 食物列表
- ✅ **免疫 (I)**：X次 | 食物列表

**进食分布得分**：X/5分

---

### 📋 每日十二完成度

| 项目 | 完成度 | 状态 |
|------|--------|------|
| 🫘 豆类 (3) | X/3 | ✅/⚠️/❌ |
| 🫐 浆果 (1) | X/1 | ✅/⚠️/❌ |
| ... | ... | ... |

**完成度**：X/12项 → X.X/10分

---

### ✅ 健康习惯评估

#### 健康食物 (X/70分)
- 评估详情

#### 限制食物 (X/50分)
- 评估详情

#### 生活方式 (X/50分)
- 评估详情

---

### 🌟 今日成就

1. ✅ 成就1
2. ✅ 成就2
3. ✅ 成就3

---

### ⚠️ 改进空间

1. 改进点1
2. 改进点2
3. 改进点3

---

### 🎯 明日计划

1. 计划1
2. 计划2
3. 计划3

---

### 📈 趋势分析

| 指标 | 昨日 | 今日 | 变化 | 趋势 |
|------|------|------|------|------|
| 总分 | X.X | X.X | +X.X | 📈/📉/➡️ |
| 防御系统 | X/5 | X/5 | +X | 📈/📉/➡️ |
```

---

### ⚠️ 输出一致性检查清单

**每次输出前必须检查**：

1. ✅ **评分说明**：是否包含一句话解释？
2. ✅ **防御系统**：是否显示中文名称 (字母) 格式？
3. ✅ **表格格式**：是否使用标准表格？
4. ✅ **评价符号**：是否使用星级 ⭐⭐⭐？
5. ✅ **完成状态**：是否使用 ✅/⚠️/❌？
6. ✅ **变化趋势**：是否使用 📈/📉/➡️？
7. ✅ **总分计算**：是否准确计算30分制？
8. ✅ **百分比**：是否计算百分比？
9. ✅ **对比数据**：是否包含与上次对比？
10. ✅ **改进建议**：是否包含具体建议？

---

### 🔍 质量保证

**输出前自检**：
- [ ] 评分规则是否简要说明？
- [ ] 防御系统是否显示中文名称？
- [ ] 格式是否符合模板？
- [ ] 数据是否准确？
- [ ] 建议是否具体可行？

**错误处理**：
- ❌ 不编造数据
- ❌ 不遗漏维度
- ❌ 不省略评价
- ✅ 如实反馈缺失信息

---

**最后更新**：2026-03-07
**版本**：v1.1
- "How can I improve [dimension]?" - Get specific improvement suggestions
