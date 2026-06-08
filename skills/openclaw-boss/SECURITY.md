# 🔒 OpenClaw Boss 安全说明

## ⚠️ 安装前必读

本技能需要访问你的个人数据以生成评价报告。请在安装前仔细阅读以下说明。

---

## 📋 数据访问清单

### 读取的文件

| 文件路径 | 用途 | 必要性 |
|---------|------|--------|
| `/root/.openclaw/workspace/MEMORY.md` | 长期记忆分析 | ✅ 必需 |
| `/root/.openclaw/workspace/USER.md` | 用户信息分析 | ✅ 必需 |
| `/root/.openclaw/workspace/memory/*.md` | 日常记忆分析 | ✅ 必需 |
| `/root/.openclaw/workspace/db/memory.db` | 记忆数据库查询 | ✅ 必需 |
| OpenClaw 会话历史 | 对话内容分析 | ✅ 必需 |

### 执行的命令

| 命令 | 用途 | 风险等级 |
|------|------|---------|
| `sessions_list` | 获取会话列表 | 🟢 低风险（OpenClaw 内置） |
| `python3 analyze-user.py` | 运行分析脚本 | 🟡 中风险（本地脚本） |
| `crontab` / `/etc/cron.d/` | 配置定时任务 | 🟡 中风险（需要 root） |

---

## 🔍 代码审计指南

### 核心脚本位置

```bash
# 分析脚本
/root/.openclaw/workspace/skills/openclaw-boss/scripts/analyze-user.py

# 自动安装脚本
/root/.openclaw/workspace/skills/openclaw-boss/.onload
```

### 关键代码审查点

#### 1. 文件读取（analyze-user.py）

```python
# 第 45-60 行：读取记忆文件
memory_files = glob.glob(f"{workspace}/memory/*.md")
for file in memory_files:
    with open(file, 'r') as f:
        content = f.read()
```

**审查要点**: 只读取，不修改，不上传

#### 2. 会话历史访问（analyze-user.py）

```python
# 第 78-95 行：获取会话列表
result = subprocess.run(
    ['openclaw', 'sessions', 'list', '--limit', '100'],
    capture_output=True,
    text=True
)
```

**审查要点**: 使用 OpenClaw 官方 API，只读访问

#### 3. 定时任务配置（.onload）

```bash
# 第 25-35 行：创建 Cron 任务
cat > /etc/cron.d/openclaw-boss << EOF
0 22 * * 0 root python3 analyze-user.py --report-type weekly
0 9 1 * * root python3 analyze-user.py --report-type monthly
EOF
```

**审查要点**: 明确写入 cron 配置，可手动审查

---

## 🛡️ 安全建议

### 1. 沙箱测试（推荐）

在完全信任之前，先在测试环境运行：

```bash
# 创建测试工作空间
mkdir -p /tmp/openclaw-test
cd /tmp/openclaw-test

# 复制技能
cp -r /root/.openclaw/workspace/skills/openclaw-boss ./

# 修改配置指向测试目录
cd openclaw-boss/scripts
python3 analyze-user.py --workspace /tmp/openclaw-test
```

### 2. 权限限制

```bash
# 限制脚本执行权限
chmod 755 /root/.openclaw/workspace/skills/openclaw-boss/scripts/analyze-user.py

# 限制数据库访问
chmod 644 /root/.openclaw/workspace/db/memory.db
```

### 3. 禁用自动 Cron（可选）

如果不想自动配置定时任务：

```bash
# 安装后删除 cron 配置
sudo rm -f /etc/cron.d/openclaw-boss

# 或注释掉定时任务
sudo nano /etc/cron.d/openclaw-boss
# 在行首添加 #
```

### 4. 网络隔离（高级）

如果担心数据外泄：

```bash
# 使用防火墙限制出站连接
sudo ufw deny out to any port 80,443 except from 192.168.0.0/16

# 或使用容器运行
docker run --rm --network none ...
```

---

## 📊 数据流向说明

```
┌─────────────────────┐
│  用户文件系统        │
│  - MEMORY.md        │
│  - USER.md          │
│  - memory/*.md      │
│  - db/memory.db     │
└──────────┬──────────┘
           │ 读取（只读）
           ▼
┌─────────────────────┐
│  analyze-user.py    │
│  - 分析数据         │
│  - 生成报告         │
│  - 无网络调用       │
└──────────┬──────────┘
           │ 输出
           ▼
┌─────────────────────┐
│  本地报告文件       │
│  reports/*.md       │
│  （不自动上传）     │
└─────────────────────┘
```

**关键点**:
- ✅ 只读取本地文件
- ✅ 无网络外泄调用
- ✅ 报告保存在本地
- ✅ 不修改原始数据

---

## 🔐 隐私保护

### 数据处理原则

1. **本地处理**: 所有分析在本地完成，不上传到外部服务器
2. **只读访问**: 不修改用户的记忆文件
3. **最小权限**: 只访问必要的文件
4. **透明操作**: 所有操作记录到日志

### 敏感信息处理

脚本会检测并标记敏感信息，但不会自动删除或修改：

```python
# 检测敏感信息（示例）
sensitive_patterns = [
    r'ghp_[A-Za-z0-9]{36}',  # GitHub Token
    r'sk-[A-Za-z0-9]{32,}',  # API Key
    r'password.*',           # 密码
]

# 在报告中警告，但不修改原始文件
```

---

## ✅ 安全检查清单

安装前确认：

- [ ] 已阅读本安全文档
- [ ] 已审查 `analyze-user.py` 代码
- [ ] 已审查 `.onload` 自动安装脚本
- [ ] 了解脚本将访问的文件
- [ ] 了解定时任务的配置方式
- [ ] 同意在信任的环境中运行
- [ ] （可选）已在沙箱环境测试

---

## 🚨 报告安全问题

如果发现安全漏洞，请：

1. **不要**公开披露
2. 发送邮件至：yiweisibot@163.com
3. 或在 GitHub 提交私有 Issue

---

## 📝 更新日志

| 版本 | 日期 | 安全更新 |
|------|------|---------|
| v5.1.1 | 2026-03-06 | 添加 SECURITY.md 安全文档 |
| v5.1.0 | 2026-03-06 | 初始安全审计 |

---

_最后更新：2026-03-06_  
_版本：v5.1.1_
