# Anima AIOS v6.2.1 发布说明

**发布日期：** 2026-03-26  
**类型：** 安全与隐私补丁  
**上一版本：** v6.2.0 (2026-03-25)

---

## 🔒 安全修复（P0）

### 1. 版本号统一
- **问题：** `__init__.py` 版本号为 6.1.2，与 _meta.json 的 6.2.0 不一致
- **修复：** 统一更新为 6.2.1
- **文件：** `__init__.py`

### 2. 隐私默认保护
- **问题：** `team_mode` 默认为 true，会扫描其他 Agent 的认知画像
- **修复：** 默认改为 false，保护多 Agent 环境隐私
- **文件：** `_meta.json`

---

## 📝 文档改进（P1）

### 3. 修改误导性文案
- **问题：** SKILL.md 宣称"零侵入/安装即生效"，但实际有后台 watcher
- **修复：** 改为"低侵入/可选后台监听"
- **文件：** `SKILL.md`

### 4. 新增后台行为说明章节
- **内容：** 明确说明 memory_watcher、每日进化、团队排行的触发条件和关闭方法
- **位置：** SKILL.md 安装章节下方
- **文件：** `SKILL.md`

### 5. 配置隐私提示
- **内容：** 在配置章节添加 team_mode 说明和隐私提示
- **位置：** SKILL.md 配置章节
- **文件：** `SKILL.md`

---

## ⚙️ 安装优化（P2）

### 6. post-install.sh 提示
- **内容：** 安装完成后提示 team_mode 默认关闭，以及如何启用
- **位置：** post-install.sh 结尾
- **文件：** `post-install.sh`

### 7. 版本历史更新
- **内容：** 在 SKILL.md 添加 v6.2.1 变更说明
- **位置：** SKILL.md v6.2.0 章节之前
- **文件：** `SKILL.md`

---

## ✅ Z 的测试验证（2026-03-26）

**测试者：** Z (始量工作室)  
**测试结果：** 8/8 通过 🎉  
**总评：** 9.0/10

### 验证通过的功能
- ✅ v6.2 原生记忆导入（131 条记忆 + 140.6 EXP）
- ✅ 三层记忆同步机制
- ✅ 五维认知画像生成
- ✅ 知识宫殿 + 金字塔引擎
- ✅ Ebbinghaus 记忆衰减
- ✅ 健康系统 5 模块

### 待优化项（非阻塞）
- 🔍 五维归一化分数趋同（混合归一化模式的预期行为，但需文档说明）
- 📝 金字塔提炼触发条件需明确（≥3 条同主题实例）
- 📊 大量 sessions 导入时添加进度条（体验优化）

---

## 📊 影响评估

| 项目 | 影响 | 说明 |
|------|------|------|
| **现有用户升级** | 低 | team_mode 变为 false，需手动开启团队排行 |
| **新用户** | 正面 | 默认更安全，隐私保护更好 |
| **团队排行功能** | 中 | 需要用户手动配置 `team_mode: true` |
| **ClawHub 审核** | 正面 | 解决 OpenClaw 安全审计指出的所有问题 |

---

## 🧪 测试建议

### 安装测试
```bash
# 全新安装
clawhub install anima-aios

# 检查版本
python3 -c "import anima; print(anima.__version__)"  # 应输出 6.2.1

# 检查配置
cat ~/.anima/config/anima_config.json | grep team_mode  # 应为 false
```

### 功能测试
```bash
# 运行自检
python3 anima_doctor.py

# 运行集成测试
python3 tests/test_integration_v6.py
```

---

## 📋 变更文件清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `__init__.py` | 修改 | 版本号 6.1.2 → 6.2.1 |
| `_meta.json` | 修改 | team_mode.default: true → false |
| `config/anima_config.template.json` | 修改 | version: 6.0.0 → 6.2.1 |
| `SKILL.md` | 修改 | 文案优化 + 新增章节 |
| `post-install.sh` | 修改 | 添加隐私提示 |

---

## 🔗 相关链接

- GitHub: https://github.com/anima-aios/anima
- ClawHub: `clawhub install anima-aios`
- 安全文档：SECURITY.md

---

_架构只能演进，不能退化。—— 立文铁律_
