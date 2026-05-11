# 首次使用引导流程

## 触发条件

**当用户首次使用健康记录功能时，自动执行以下流程**：

1. 检测用户是否已有 profile.md
2. 如果没有，启动首次使用引导
3. 自动执行 Git 环境检查
4. 根据检查结果，提供不同的引导路径

---

## 第0步：Git 环境检查（自动执行）

**自动执行**：
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

**根据检查结果，显示不同的提示**：

---

## 欢迎语

```
好的！我来帮你建立健康管理系统 🦞🏥

让我先检查一下环境配置...

✅ 环境检查完成！

---

这个系统会帮你：
✅ 建立个性化健康档案
✅ 三维度饮食评分（每日十二 + 5×5×5 + 共识清单）
✅ 追踪补剂、运动、睡眠
✅ 生成周报、月报、年报
✅ 自动备份到 GitHub（可选，安全可靠）

让我一步步引导你完成设置！
```

---

## 第1步：基本信息

**提示词**：
```
📋 **第1步：基本信息**

请告诉我：
1. 你想设置哪些健康目标？（可以多选）
   - 控制血糖
   - 抗衰老
   - 抗炎
   - 增肌
   - 改善睡眠
   - 减重
   - 其他（请说明）

2. 有没有食物过敏或禁忌？

示例回答：
- 健康目标：控制血糖、抗衰老、抗炎
- 禁忌：无
```

**数据收集**：
- health_goals: [目标1, 目标2, 目标3, ...]
- allergies: [过敏1, 过敏2, ...]
- restrictions: [禁忌1, 禁忌2, ...]

---

## 第2步：语言设置

**提示词**：
```
🌐 **第2步：语言设置**

请选择你希望使用的输出语言：

**支持的语言**：
1. 🇨🇳 中文（简体）- Chinese Simplified
2. 🇺🇸 English - 英语
3. 🇯🇵 日本語 - 日语
4. 🇰🇷 한국어 - 韩语
5. 🇫🇷 Français - 法语
6. 🇩🇪 Deutsch - 德语
7. 🇪🇸 Español - 西班牙语

**请选择**：
- 回复数字（1-7）快速选择
- 或直接输入语言代码（例如：zh-CN, en, ja）

示例回答：
- 1（中文）
- en（English）
- ja（日本語）

💡 提示：默认使用中文。选择后可随时在 profile.md 中修改。
```

**数据收集**：
- language: {语言代码}

**语言映射**：
```bash
1) zh-CN  # 中文简体（默认）
2) en     # English
3) ja     # 日本語
4) ko     # 한국어
5) fr     # Français
6) de     # Deutsch
7) es     # Español
```

**保存到 profile.md**：
```markdown
## 👤 Basic Info
- **Language**: {language}
```

**后续使用**：
- 所有输出根据用户选择的语言显示
- 默认：中文（zh-CN）
- 可随时修改：编辑 profile.md 中的 Language 字段

---

## 第3步：时区设置

**提示词**：
```
🌍 **第2步：时区设置**

为了确保所有时间记录准确，请设置你的时区。

**常见时区**：
1. 🇨🇳 中国大陆：Asia/Shanghai (UTC+8)
2. 🇺🇸 美国东部：America/New_York (UTC-5)
3. 🇺🇸 美国西部：America/Los_Angeles (UTC-8)
4. 🇬🇧 英国：Europe/London (UTC+0/+1)
5. 🇯🇵 日本：Asia/Tokyo (UTC+9)
6. 🇦🇺 澳大利亚：Australia/Sydney (UTC+10/+11)
7. 其他（请提供时区名称）

**请选择**：
- 回复数字（1-7）快速选择
- 或直接输入时区名称（例如：Asia/Shanghai）
- 或回复"UTC"使用通用时区

示例回答：
- 1（中国大陆）
- America/New_York
- UTC
```

**数据收集**：
- timezone: {时区名称}

**时区映射**：
```bash
1) Asia/Shanghai
2) America/New_York
3) America/Los_Angeles
4) Europe/London
5) Asia/Tokyo
6) Australia/Sydney
7) 用户自定义
```

**保存到 profile.md**：
```markdown
## 👤 Basic Info
- **Timezone**: {timezone}
```

---

## 第3步：个性化配置

**提示词**：
```
🎯 **第2步：个性化配置**

请告诉我你的偏好：

1. **饮食偏好**：
   - 素食/纯素/杂食
   - 口味偏好（清淡/重口味）

2. **补剂情况**：
   - 是否服用补剂？（是/否）
   - 如果有，请列出常服用的补剂

3. **运动习惯**：
   - 运动频率（每天/每周3-5次/偶尔）
   - 主要运动类型（有氧/力量/瑜伽等）

示例回答：
- 饮食：杂食，偏好清淡
- 补剂：鱼油、维生素D3、镁
- 运动：每周3-4次力量训练
```

**数据收集**：
- diet_preference: {素食/纯素/杂食}
- taste_preference: {清淡/重口味}
- supplements: [补剂1, 补剂2, ...]
- exercise_frequency: {每天/每周3-5次/偶尔}
- exercise_type: [类型1, 类型2, ...]

---

## 第4步：备份配置（可选）

**提示词**：
```
💾 **第4步：备份配置（可选）**

为了数据安全，建议启用自动备份到 GitHub。

**备份好处**：
- ✅ 防止数据丢失
- ✅ 版本控制，可回溯历史
- ✅ 多设备同步
- ✅ 完全私密（私有仓库）

**是否启用备份？**

1. ✅ 启用备份（推荐）
2. ❌ 暂不启用（稍后可手动配置）

请选择 1 或 2。
```

**用户选择**：
- **选择 1（启用备份）** → 进入第 4.1 步（配置仓库）
- **选择 2（暂不启用）** → 跳过备份配置，进入第 5 步

---

### 第 4.1 步：配置备份仓库（仅在选择启用时显示）

**提示词**：
```
💾 **第4.1步：配置备份仓库**

太好了！现在配置你的 GitHub 备份仓库。

**前置要求**：
- ✅ GitHub 账号
- ✅ SSH 密钥已配置（已在第0步检查）
- ✅ 创建一个**私有仓库**（推荐）

**请提供**：
1. GitHub 仓库 URL（SSH 格式）
   
   示例：git@github.com:yourname/health-backup.git

2. 备份分支（默认：main）

**提示**：
- 强烈建议使用**私有仓库**
- 仓库名可以是任意名称（如：my-health-data）
- 分支通常使用 main 或 master

**你的仓库地址**：
```

**用户输入**：
```bash
BACKUP_REPO_URL=git@github.com:yourname/health-backup.git
BACKUP_BRANCH=main
```

**AI 验证**：
1. ✅ 检查 URL 格式（必须是 SSH）
2. ✅ 测试 Git 连接
3. ✅ 提醒用户使用私有仓库

**验证成功后**：
```bash
# 保存到 backup_config.json
{
  "enabled": true,
  "repo_url": "git@github.com:yourname/health-backup.git",
  "branch": "main",
  "auto_backup": true,
  "created_at": "2026-03-16T09:30:00+08:00"
}
```

**反馈用户**：
```
✅ **备份配置成功！**

- 仓库地址：git@github.com:yourname/health-backup.git
- 备份分支：main
- 自动备份：已启用

你的健康数据将在每次记录后自动备份到 GitHub。

⚠️ **重要提醒**：
请确保仓库设置为**私有**，以保护你的健康数据隐私。

进入下一步...
```

---

## 第5步：确认和保存

**提示词**：
```
✅ **最后一步：确认和保存**

让我确认一下你的信息：

---

## 📊 你的健康档案

**健康目标**（优先级排序）：
1. {目标1} ⭐⭐⭐⭐⭐⭐
2. {目标2} ⭐⭐⭐⭐⭐
3. {目标3} ⭐⭐⭐⭐

**饮食偏好**：
- 饮食类型：{类型}
- 口味偏好：{口味}

**补剂情况**：
- {补剂1}
- {补剂2}

**运动习惯**：
- 频率：{频率}
- 类型：{类型}

**食物禁忌**：
- {禁忌1}
- {禁忌2}

---

**三维度评分权重**（根据你的目标自动计算）：
- 维度一（每日十二）：{权重}
- 维度二（5×5×5）：{权重}
- 维度三（共识清单）：{权重}

---

**确认无误？**（回复"确认"保存，或告诉我需要修改的地方）
```

---

## 第6步：保存档案

**用户确认后执行**：

1. **创建用户目录**：
```bash
mkdir -p ~/.openclaw/workspace/memory/health-users/{username}/{daily,weekly,monthly}
```

2. **生成 profile.md**：
- 使用模板 `templates/profile-template.md`
- 填充用户信息
- 保存到 `memory/health-users/{username}/profile.md`

3. **生成补剂数据库**（如果有补剂）：
- 创建 `supplement-database.md`
- 引导用户补全补剂详细信息

4. **执行备份**（如果已配置）：
```bash
bash scripts/backup_health_data.sh
```

---

## 第7步：完成引导

**反馈用户**：

```
✅ **健康档案已创建！**

📁 文件已保存：
- 用户档案：profile.md
- 补剂数据库：supplement-database.md

---

🎉 **恭喜！你的健康管理系统已就绪！**

现在你可以：
1. 🍽️ 记录饮食：健康助手 早餐吃了...
2. 💊 记录补剂：健康助手 今天吃了鱼油、维生素D3
3. 🏃 记录运动：健康助手 今天跑了5公里
4. 😴 记录睡眠：健康助手 昨晚睡了7小时
5. 📊 查看总结：健康助手 总结今日表现
6. 📈 周报月报：健康助手 周报/月报

💡 **配置备份（推荐）**：
健康助手 配置健康数据备份

有任何问题随时问我！🦞
```

---

## Git 配置失败处理（可选）

**如果第0步检查失败，提供手动配置指导**：

```
⚠️ **Git 配置检查失败**

让我帮你一步步配置 Git...

---

### 📋 配置步骤

#### 1️⃣ 安装 Git（如果未安装）

**macOS**：
```bash
brew install git
```

**Linux**：
```bash
sudo apt-get install git
```

**Windows**：
下载：https://git-scm.com/download/win

---

#### 2️⃣ 配置 Git 用户信息

```bash
git config --global user.name "your_name"
git config --global user.email "your_email@example.com"
```

**示例**：
```bash
git config --global user.name "John Doe"
git config --global user.email "john.doe@example.com"
```

---

#### 3️⃣ 生成 SSH 密钥

```bash
ssh-keygen -t ed25519 -C "你的邮箱"
```

**按 Enter 使用默认设置**，然后查看公钥：
```bash
cat ~/.ssh/id_ed25519.pub
```

---

#### 4️⃣ 添加 SSH 密钥到 GitHub

1. 复制公钥内容
2. 访问：https://github.com/settings/keys
3. 点击：**New SSH key**
4. 标题：OpenClaw Health Management
5. 粘贴公钥内容
6. 点击：**Add SSH key**

---

**完成配置后，回复"继续"，我会继续引导你完成健康档案设置。**
```

---

## 引导流程完成

用户完成引导后，可以开始使用所有功能：
- ✅ 每日饮食记录
- ✅ 补剂管理
- ✅ 运动记录
- ✅ 睡眠记录
- ✅ 三维度评分
- ✅ 周报/月报/年报
- ✅ 自动备份（如果已配置）

---

## 不阻塞使用的设计

### 关键原则

1. **首次使用不强制配置备份**
   - 用户可以跳过备份配置
   - 先使用健康记录功能
   - 稍后配置备份

2. **备份失败不阻塞使用**
   - 如果未配置备份，跳过备份步骤
   - 显示友好提示，但不报错
   - 用户可以随时配置

3. **允许后续补充配置**
   - 用户随时可以说：`健康助手 配置健康数据备份`
   - 系统会引导完成配置
   - 不影响已有数据

4. **灵活的仓库位置**
   - 用户可以选择任意路径
   - 可以修改备份路径
   - 可以暂停/恢复备份

---

## 备份管理命令

**查看备份配置**：
```
用户：健康助手 查看备份配置

AI：
💾 **备份配置**

- 备份路径：{路径}
- 远程仓库：{SSH 地址}
- 自动备份：{启用/暂停}
- 最后备份：{时间}

**操作**：
- 修改路径：健康助手 修改备份路径
- 暂停备份：健康助手 暂停自动备份
- 恢复备份：健康助手 恢复自动备份
- 立即备份：健康助手 立即备份健康数据
```

**修改备份路径**：
```
用户：健康助手 修改备份路径

AI：
💾 **修改备份路径**

当前路径：{旧路径}

请告诉我新的备份路径，或回复"取消"。

示例：~/Documents/new-backup
```

**暂停/恢复备份**：
```
用户：健康助手 暂停自动备份

AI：
✅ **自动备份已暂停**

数据将不再自动备份到 GitHub。

恢复备份：健康助手 恢复自动备份
```

---

## 配置文件格式

**文件路径**：`memory/health-users/.backup_config`

**内容**：
```bash
# 健康数据备份配置
# 创建时间：2026-03-13 21:00 (用户时区)

# 备份仓库路径（本地）
BACKUP_REPO_PATH=/home/yourname/Documents/health-backup

# GitHub 远程仓库地址（SSH）
BACKUP_REMOTE_URL=git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git

# 是否启用自动备份（true/false）
BACKUP_ENABLED=true

# 最后备份时间
LAST_BACKUP_TIME=2026-03-13 21:00:00
```

---

**用户，优化完成！**

**核心改进**：
1. ✅ 动态检测 Git 环境（check_git_config.sh）
2. ✅ 可选的备份配置流程（configure_backup.sh）
3. ✅ 灵活的备份管理（manage_backup.sh）
4. ✅ 支持动态备份路径（backup_health_data.sh）
5. ✅ 首次使用引导流程（onboarding-flow.md）
6. ✅ 不阻塞使用（可跳过备份配置）

**使用流程**：
1. 首次使用 → 自动检查 Git 环境
2. 创建健康档案 → 可选择配置备份
3. 备份配置 → 可选任意路径
4. 后续管理 → 可随时修改/暂停/恢复

要测试一下吗？🦞
