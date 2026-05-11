# 🎉 New User Onboarding Guide

> Use this guide when encountering a new user for the first time

---

## 📋 Onboarding Workflow

### Step 1: Welcome & Introduction (30 seconds)

**Agent says**:
```
欢迎来到健康管理计划！🎉

我会帮你建立一个基于科学的健康管理系统，整合了10本畅销健康书籍的最大共识。

这个系统可以：
✅ 自动识别食物对应的防御系统
✅ 三维度评分（满分192分）
✅ 每日/每周/每月自动分析
✅ 个性化改进建议

让我们先设定你的健康目标！
```

---

### Step 2: Collect Health Goals (1-2 minutes)

**Agent asks**:
```
请告诉我你的健康目标，按重要性排序：

常见目标：
1. 抗衰老
2. 抗炎
3. 控制血糖/预防糖尿病
4. 维持体重
5. 增加肌肉
6. 改善睡眠
7. 提高精力
8. 其他（请说明）

示例回答：
"我的目标是抗衰老、抗炎、维持体重、增加肌肉"
```

**User provides goals**:
```
例如："抗衰老、抗炎、维持体重、增加肌肉、控制血糖"
```

---

### Step 3: Create User Profile (Automatic)

**Agent creates**: `memory/health-users/{username}/profile.md`

**Profile structure**:
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

### 优先级1: {Goal 1} ⭐⭐⭐⭐⭐⭐
**重点关注**: [相关防御系统或指标]
**关键食物**: [推荐食物]
**关键行为**: [推荐行为]

### 优先级2: {Goal 2} ⭐⭐⭐⭐⭐
...

## 📊 Personalized Scoring Weights

### 维度一：《救命》每日十二清单
- 标准权重: 1.0
- 你的权重: 1.0

### 维度二：《吃出自愈力》5×5×5
- 标准权重: 1.0
- 你的权重: 1.5
- 重点防御系统: [根据目标调整]

### 维度三：共识清单
- 标准权重: 1.0
- 你的权重: 1.2-1.5
- 重点项目: [根据目标调整]

## 📅 Tracking History
- First Record: [待记录]
- Total Records: 0 days
- Current Streak: 0 days

## 🏆 Achievements
- [ ] 连续7天达标
- [ ] 连续30天达标
- [ ] 单月平均分>80%
...

## 📝 Notes
[用户特殊需求、过敏、偏好等]
```

---

### Step 4: Setup Supplement Database (Optional, 1-2 minutes)

**Agent asks**:
```
你有在服用补剂吗？（维生素、鱼油、蛋白粉等）

如果有，我可以帮你建立一个补剂数据库，这样以后你只需要说"和昨天一样的补剂"，我就能快速记录了！

如果有，请告诉我：
- 补剂名称（如：鱼油、维生素D3）
- 品牌（如：XX品牌）
- 每粒剂量（如：645mg）
- 有效成分（如：613mg EPA+DHA）

示例：
"鱼油，营养工厂，每粒645mg，含613mg EPA+DHA"
"维生素D3，Swisse，每粒1000 IU"

如果暂时没有或者不确定，可以跳过，之后再补充！
```

**User provides supplement info**:
```
例如："鱼油、维生素D3、镁"
```

**Agent action**:
1. If user provides supplements → Create `supplement-database.md`
2. If user skips → Note in profile, can setup later
3. Save to: `memory/health-users/{username}/supplement-database.md`
4. Backup to GitHub

**Supplement database template**:
```markdown
# 💊 补剂数据库

> 创建时间：YYYY-MM-DD
> 用户：{username}

## 📋 使用说明
[标准模板内容...]

## 💊 补剂清单

### 晨间补剂
| 补剂名称 | 品牌 | 每粒剂量 | 有效成分 | 服用时间 | 健康目标 | 状态 | 更新日期 |
|---------|------|---------|---------|---------|---------|------|---------|
| [补剂1] | [品牌] | [剂量] | [成分] | 晨间随餐 | [目标] | 启用 | [日期] |

### 晚间补剂
[同上格式]
```

---

### Step 5: Explain Core Concepts (1 minute)

**Agent explains**:
```
太好了！你的个人档案已创建。✅

让我简单解释一下三维度评分系统：

维度一：《救命》每日十二清单（满分12分）
- 每天追踪12项关键食物/行为
- 豆类、浆果、蔬菜、坚果、运动等

维度二：《吃出自愈力》5×5×5（满分10分）
- 选择5种食物，覆盖5大防御系统
- 血管生成、再生、微生物组、DNA保护、免疫

维度三：共识清单（满分170分）
- 健康食物（70分）
- 限制食物（50分）
- 生活方式（50分）

综合得分：满分192分
- 🌟🌟🌟🌟🌟 90-100%: 卓越
- 🌟🌟🌟🌟 80-89%: 优秀
- 🌟🌟🌟 70-79%: 良好
```

---

### Step 6: Guide First Recording (30 seconds)

**Agent says**:
```
准备好开始记录了吗？非常简单！

只需要告诉我你今天吃了什么，例如：

早餐：燕麦+蓝莓+亚麻籽
午餐：沙拉+鸡胸肉+西兰花
晚餐：三文鱼+糙米
零食：核桃一小把
运动：快走40分钟

我会自动帮你分析并记录！💪

或者，如果你想先设定间歇性禁食时间，也可以告诉我你的作息时间。
```

---

## 🎯 Onboarding Checklist

**Agent must complete**:

- [ ] Welcome user
- [ ] Collect health goals (at least 1)
- [ ] Create user profile: `memory/health-users/{username}/profile.md`
- [ ] Setup supplement database (optional): `memory/health-users/{username}/supplement-database.md`
- [ ] Explain 3-dimension system briefly
- [ ] Guide first recording OR set fasting schedule
- [ ] Create user directory structure:
  ```
  memory/health-users/{username}/
  ├── profile.md
  ├── supplement-database.md (if applicable)
  ├── daily/
  ├── weekly/
  └── monthly/
  ```

---

## 🚨 Common Onboarding Scenarios

### Scenario 1: User provides incomplete goals

**User says**: "我想健康一点"

**Agent responds**:
```
好的！让我帮你明确目标。你最关心的是：

1. 长期健康（抗衰老、预防疾病）
2. 体重管理（减重/增肌/维持）
3. 精力提升（改善疲劳、提高专注力）
4. 特定健康问题（炎症、血糖、睡眠等）

请告诉我你的优先级！
```

---

### Scenario 2: User has specific health conditions

**User says**: "我有糖尿病前期"

**Agent responds**:
```
了解！那我们把**控制血糖、预防糖尿病**设为最高优先级目标。

这非常重要，因为：
- 血糖控制是代谢健康的基础
- 胰岛素抵抗影响所有其他健康目标
- 通过饮食和生活方式可以有效逆转

我会特别关注：
✅ 饮食顺序（蔬菜→蛋白质→碳水）
✅ 间歇性禁食（14-16小时）
✅ 餐后运动（10-15分钟散步）
✅ 严格避免精制糖和精制碳水

准备好了吗？我们开始记录第一餐！
```

**Agent action**: Set blood sugar control as Priority 1 with ⭐⭐⭐⭐⭐⭐

---

### Scenario 3: User wants to start immediately

**User says**: "早餐：燕麦+蓝莓" (without setting goals first)

**Agent responds**:
```
收到！让我先记录下来。

在分析之前，能快速告诉我你的健康目标吗？
例如：抗衰老、抗炎、增肌、减重、控制血糖等

这样我可以给你更个性化的建议！

如果你暂时不确定，我可以先用标准配置，之后再调整。
```

**Agent action**:
1. Record the meal temporarily
2. Ask for goals (don't block)
3. If user doesn't provide goals → Use default profile
4. Save record after profile is ready

---

### Scenario 4: User is returning after long break

**User says**: "我又回来了，好久没记录了"

**Agent responds**:
```
欢迎回来！🎉

让我先看看你的历史记录...
[读取用户档案]

你上次记录是在 [日期]，已经 [X天] 了。

你的目标是：
1. [Goal 1]
2. [Goal 2]
...

还想继续追踪这些目标吗？还是需要调整？

准备好后，告诉我今天吃了什么就可以开始了！
```

---

## 📊 Profile Update Triggers

**Automatically update user profile when**:

1. **Goals change**: User explicitly states new goals
2. **Priorities shift**: User focuses on different aspects
3. **Achievements unlocked**: Update achievements section
4. **Long-term trends**: Add notes about patterns
5. **Health improvements**: Record significant changes

**Update frequency**:
- Profile summary: Monthly
- Achievements: As unlocked
- Goals: When user requests

---

## 🔧 Technical Implementation

### User Directory Creation

**When creating new user**:

```bash
mkdir -p memory/health-users/{username}/daily
mkdir -p memory/health-users/{username}/weekly
mkdir -p memory/health-users/{username}/monthly
```

### Profile Reading Logic

**Every interaction**:

```python
# Pseudocode
username = extract_username(conversation_metadata)
profile_path = f"memory/health-users/{username}/profile.md"

if not exists(profile_path):
    # New user - trigger onboarding
    onboard_new_user(username)
else:
    # Existing user - load profile
    profile = read_file(profile_path)
    user_goals = profile.extract_goals()
    user_weights = profile.extract_weights()
    recent_records = read_recent_records(username, days=7)

# Process message with user context
response = analyze_with_context(message, user_goals, user_weights, recent_records)
```

### Record Saving Logic

**When saving daily record**:

```python
# Pseudocode
username = extract_username(conversation_metadata)
date = get_current_date()
record_path = f"memory/health-users/{username}/daily/{date}.md"

save_record(record_path, daily_data)

# Update profile tracking history
profile_path = f"memory/health-users/{username}/profile.md"
update_tracking_history(profile_path, date)
```

---

## 💡 Best Practices

### DO ✅

- Always identify user before processing
- Load user profile for every interaction
- Save records to user-specific directory
- Reference user's personal goals in analysis
- Celebrate user-specific achievements
- Keep user data completely isolated

### DON'T ❌

- Never mix data between users
- Never assume default goals without asking
- Never reference another user's data
- Never skip user identification step
- Never save to wrong user directory
- Never share personal health information

---

## 📚 Reference

- User profile template: See this document
- Directory structure: See [SKILL.md](../SKILL.md) Multi-User Support section
- Privacy guidelines: See [SKILL.md](../SKILL.md) Privacy & Isolation section

---

**Remember**: Every user is unique. Personalization is the key to success! 🎯
