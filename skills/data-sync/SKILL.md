---
name: data-sync
description: "重要数据同步工具。通过云服务器中转站在多台电脑间同步 Claude Code 关键配置（skills、hooks、记忆库、skill-factory），GitHub 作为大版本归档。支持 init/pull/push/backup/status 五个子命令。"
---

# 重要数据同步 Skill（data-sync）

通过云服务器 bare repo 中转，在多台电脑之间增量同步 Claude Code 的关键数据资产，GitHub 作为大版本归档备份。

## 架构

```
电脑A ←──(pull/push)──→ 服务器 relay (最新最全) ←──(pull/push)──→ 电脑B
                              │
                        (backup: 大版本归档)
                              ↓
                           GitHub (私有仓库)
```

- **服务器是唯一中间节点**——两台电脑不直接通信，所有同步经过服务器
- **GitHub 是归档层**——不参与日常同步，只在大版本时接收推送
- **本机数据永远安全**——所有操作只增不删，不使用任何破坏性 git 命令

---

## 配置

仓库注册表和服务器信息存放在独立文件中，添加/修改仓库无需编辑本 SKILL.md：

**配置文件**：[sync-registry.md](sync-registry.md)（与本文件同目录）

读取方式：执行前先读取 `sync-registry.md`，解析仓库列表和服务器信息。如果配置文件不存在或格式异常，报错并提示用户检查。

---

## 使用触发词

用户说以下任一触发词时启动本 skill：

- `/data-sync`
- "同步数据" / "拉取同步" / "推送同步" / "数据备份" / "同步状态"

---

## 子命令路由

启动后，首先判断用户意图，路由到对应子命令：

```
用户请求进来
│
├─ "init" / "初始化" / "新电脑配置"
│   → Init 子命令（新电脑首次配置）
│
├─ "pull" / "拉取" / "同步到本机" / 未指定（默认）
│   → Pull 子命令
│
├─ "push" / "推送" / "上传"
│   → Push 子命令
│
├─ "backup" / "归档" / "大版本" / "推到GitHub"
│   → Backup 子命令
│
└─ "status" / "状态" / "检查"
    → Status 子命令
```

如果用户意图不明确，展示子命令菜单让用户选择。

---

## 子命令零：Init（新电脑初始化）

**场景**：新电脑首次使用，需要从服务器克隆全部仓库并配置环境。

### 执行流程

**步骤 1：检查前置条件**

```bash
# 检查 git 是否安装
git --version

# 检查 SSH 连接
ssh -o ConnectTimeout=5 root@<服务器IP> "echo ok"
```

- 如果 git 未安装，提示安装方法
- 如果 SSH 连接失败，引导用户配置 SSH 密钥：
  ```bash
  ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519
  # 然后手动将公钥添加到服务器 ~/.ssh/authorized_keys
  # 或从旧电脑上 scp 已有密钥对
  ```

**步骤 2：询问本机路径**

询问用户两个路径：
- `.claude` 配置目录（默认 `~/.claude`，通常不需要改）
- 学习工作库目录（用户指定项目根路径）

**步骤 3：克隆仓库**

按 `sync-registry.md` 中的仓库列表逐个克隆：

```bash
git clone root@<服务器IP>:/root/git-relay/claude-config.git <.claude路径>
git clone root@<服务器IP>:/root/git-relay/claude-knowledge-base.git <学习工作库路径>
```

每个克隆完成后验证：
```bash
git -C <路径> log -1 --format="%h %s (%ci)"
```

**步骤 4：重命名 remote**

克隆默认创建 `origin` remote，重命名为 `relay`（与 skill 规范一致）：
```bash
git -C <路径> remote rename origin relay
```

**步骤 5：路径适配**

自动检测并提示需要修改的绝对路径：

1. 读取 `<.claude路径>/CLAUDE.md`，列出其中所有硬编码路径
2. 提示用户将旧路径替换为新电脑的实际路径
3. 检查 `settings.json` 中的代理端口是否需要更新

**步骤 6：验证**

对每个仓库执行 status 检查，确认一切正常：
```bash
git -C <路径> remote -v         # 确认 relay remote
git -C <路径> log -1 --oneline  # 确认有内容
git -C <路径> status --short    # 确认干净状态
```

**步骤 7：生成 Init 报告**

```
=== Data Sync Init 报告 ===

环境:
  Git: v2.43.7
  SSH: root@129.211.0.193 连接正常

仓库:
  claude-config:
    路径: C:\Users\新用户\.claude
    Remote: relay → 129.211.0.193:/root/git-relay/claude-config.git
    最新提交: 6955b12 "migration: full state backup" (2026-02-23)
    状态: 就绪

  knowledge-base:
    路径: D:\项目\VScode辅助工作学习
    Remote: relay → 129.211.0.193:/root/git-relay/claude-knowledge-base.git
    最新提交: 857b757 "migration: full knowledge base backup" (2026-02-23)
    状态: 就绪

待办:
  → 请检查 CLAUDE.md 中的路径引用是否正确
  → 请确认 settings.json 中的代理端口

初始化完成。可以开始使用 /data-sync pull 和 push 了。
```

---

## 子命令一：Pull（拉取同步）

**场景**：切换到另一台电脑开始工作前，拉取最新内容。

### 执行流程

**步骤 1：环境检测**

对 `sync-registry.md` 中的每个仓库：
1. 检查本机路径是否存在（不存在 → 提示用户先执行 `init`）
2. 检查是否有 `relay` remote 配置（没有 → 报错并提示配置命令）
3. 检查 SSH 连接到服务器是否正常（失败 → 见"错误处理"章节）
4. 如有异常，报告并询问用户是否继续

**步骤 2：检查本地状态**

对每个仓库执行：
```bash
git -C <本机路径> status --short
```

- 如果有未提交的本地修改，**警告用户**并提供选项：
  - (a) 先执行 Push 子命令提交本地修改（推荐）
  - (b) `git stash` 暂存后再 pull，pull 完后 `git stash pop`
  - (c) 忽略警告，直接 pull（可能产生冲突）

**步骤 3：先检查是否有更新**

```bash
git -C <本机路径> fetch relay <分支>
git -C <本机路径> log HEAD..relay/<分支> --oneline
```

- 如果没有新提交，报告"已是最新"并跳过
- 如果有新提交，展示变更概览后继续

**步骤 4：执行拉取**

```bash
git -C <本机路径> pull relay <分支> --ff-only
```

- 使用 `--ff-only` 防止意外合并冲突
- 如果 fast-forward 失败（有分叉），报告给用户并提供选项：
  - (a) `git pull relay <分支> --rebase`（推荐，保持线性历史）
  - (b) `git pull relay <分支>`（允许合并提交）
  - (c) 跳过此仓库

**步骤 5：生成报告**

```
=== Data Sync Pull 报告 ===

claude-config:
  状态: 已更新
  更新: 3 files changed (+45, -12)
  最新提交: abc1234 "sync: skill迭代" (2026-02-23)

knowledge-base:
  状态: 已是最新（无更新）

建议下一步: 本机已同步到最新，可以开始工作。工作完毕后执行 /data-sync push。
```

---

## 子命令二：Push（推送同步 + 版本对比）

**场景**：在当前电脑完成工作后，推送变更到服务器。

### 执行流程

**步骤 1：检测变更**

对每个仓库执行：
```bash
git -C <本机路径> status --short
git -C <本机路径> diff --stat
```

- 列出所有修改、新增、删除的文件
- 如果没有变更，跳过该仓库并报告"无变更"

**步骤 2：检查服务器是否领先**

```bash
git -C <本机路径> fetch relay <分支>
git -C <本机路径> log HEAD..relay/<分支> --oneline
```

- 如果服务器有本机没有的提交（另一台电脑推过），**中止 push**：
  > "服务器有更新（来自另一台电脑），请先执行 /data-sync pull 再 push。"
- 这是"先 pull 后 push"规则的强制执行

**步骤 3：展示变更摘要**

```
claude-config 变更:
  修改: skills/ai-auto-dev/skill.md
  新增: skills/data-sync/SKILL.md
  共 2 个文件

knowledge-base 变更:
  修改: Claude Code辅助学习记忆库.md
  修改: 思维蒸馏.md
  共 2 个文件
```

**步骤 4：安全检查**

扫描变更文件，检查以下项目：

| 检查项 | 级别 | 处理 |
|--------|------|------|
| 文件内容匹配 `(api_key\|token\|password\|secret)\s*[:=]` | 阻断 | 必须确认或排除后才能继续 |
| `.env` 文件被 staged | 阻断 | 提示加入 `.gitignore` |
| 单个文件 > 5MB | 警告 | 展示文件名和大小，用户确认 |
| `node_modules/` 被 staged | 阻断 | 检查 `.gitignore` 是否缺失规则 |
| `.gitignore` 没有排除常见临时文件 | 警告 | 建议添加规则 |

**步骤 5：提交并推送**

用户确认后，对每个有变更的仓库执行：
```bash
git -C <本机路径> add -A
git -C <本机路径> commit -m "sync: <自动生成的变更摘要>"
git -C <本机路径> push relay <分支>
```

Commit message 格式：`sync: <日期> <变更文件数>个文件 (<主要变更简述>)`
示例：`sync: 2026-02-23 4 files (skill迭代+记忆库更新)`

**步骤 6：与 GitHub 大版本对比**

推送完成后，自动对比当前状态与 GitHub 最近 tag 之间的差距：

```bash
# 获取最近的 tag
git -C <本机路径> describe --tags --abbrev=0 2>/dev/null

# 如果有 tag，统计差距
git -C <本机路径> log <最近tag>..HEAD --oneline
git -C <本机路径> diff --stat <最近tag>..HEAD
```

**版本对比判定逻辑**：

```
获取最近 tag
│
├─ 无 tag
│   → 提示: "尚无大版本归档，建议执行 /data-sync backup 打 v1.0"
│
├─ 自上次 tag 以来 < 5 commits 且 < 10 files changed
│   → 提示: "变更较少，暂不需要归档"
│
├─ 自上次 tag 以来 5-15 commits 或 10-20 files changed
│   → 提示: "变更适中，可考虑归档"
│
└─ 自上次 tag 以来 > 15 commits 或 > 20 files changed
    → 强烈建议: "变更较多，建议尽快执行 /data-sync backup"
```

**步骤 7：生成推送报告**

```
=== Data Sync Push 报告 ===

claude-config:
  提交: abc1234 "sync: 2026-02-23 2 files (新增data-sync skill)"
  推送: relay/master 成功
  传输量: ~15 KB (增量)
  距上次大版本: +8 commits, 15 files changed → 建议归档

knowledge-base:
  提交: def5678 "sync: 2026-02-23 2 files (记忆库+蒸馏更新)"
  推送: relay/master 成功
  传输量: ~3 KB (增量)
  距上次大版本: 无 tag → 建议打 v1.0

建议下一步:
  → 两个仓库都有较多未归档变更，建议执行 /data-sync backup
  → 或继续工作，下次再归档
```

---

## 子命令三：Backup（大版本归档到 GitHub）

**场景**：累积了较多变更，或达到里程碑，需要完整归档到 GitHub。

### 执行流程

**步骤 1：确认归档范围**

展示各仓库自上次 tag 以来的完整变更：

```bash
# 每个仓库
git -C <本机路径> describe --tags --abbrev=0 2>/dev/null
git -C <本机路径> log <最近tag>..HEAD --oneline  # 或 git log --oneline（无tag时）
git -C <本机路径> diff --stat <最近tag>..HEAD
```

询问用户：
- 归档哪些仓库（全部 / 选择性）
- 版本号（自动建议下一个版本号，用户可修改）
- 版本说明（一句话概括本次归档的主要内容）

**版本号自动建议逻辑**：
```
获取最近 tag
│
├─ 无 tag → 建议 v1.0
├─ 最近 tag 是 vX.Y
│   ├─ 有新增 skill 或重大模块 → 建议 vX.(Y+1)
│   └─ 仅小改 → 建议 vX.(Y+1)
└─ 用户可手动指定任意版本号
```

**步骤 2：确保 relay 是最新的**

归档前先同步到服务器：
```bash
git -C <本机路径> push relay <分支>
```

**步骤 3：打 Tag**

```bash
git -C <本机路径> tag -a <版本号> -m "<版本说明>"
git -C <本机路径> push relay <分支> --tags
```

Tag 命名规范：`v<主版本>.<次版本>`
- 新增重要内容（新 skill、新蒸馏主题）→ 次版本 +1
- 架构大调整 → 主版本 +1

**步骤 4：推送到 GitHub（自动选择路径）**

```
检测 GitHub 连通性
│
├─ 本机能连 GitHub（curl --max-time 5 https://api.github.com）
│   → 路径 A：本机直推
│   git -C <本机路径> push origin <分支> --tags
│   （如果没有 origin remote，自动添加）
│
└─ 本机不能连 GitHub（超时或拒绝）
    → 路径 B：服务器中转推
    ssh root@<服务器IP> "cd /root/git-relay/<仓库>.git && git push github --mirror"
    │
    ├─ 成功 → 继续
    └─ 失败（服务器未配置 GitHub credential）
        → 引导配置：
        ssh root@<服务器IP>
        cd /root/git-relay/<仓库>.git
        git remote set-url github https://<token>@github.com/mwangxiang/<仓库>.git
        # 或配置 credential helper
```

**服务器端 GitHub Credential 配置说明**：

首次通过服务器中转推送 GitHub 时，需要在服务器上配置认证：

```bash
# 方式一：URL 内嵌 token（简单但 token 明文存储）
ssh root@<服务器IP>
cd /root/git-relay/<仓库>.git
git remote set-url github https://mwangxiang:<GitHub_PAT>@github.com/mwangxiang/<仓库>.git

# 方式二：git credential store（token 存文件，稍安全）
ssh root@<服务器IP>
git config --global credential.helper store
# 首次 push 时输入用户名和 token，之后自动记住
```

获取 GitHub Personal Access Token：GitHub Settings → Developer settings → Personal access tokens → 创建，勾选 `repo` 权限。

**步骤 5：验证归档**

```bash
# 路径 A 验证（本机直推后）
git -C <本机路径> ls-remote origin --tags | grep <版本号>

# 路径 B 验证（服务器中转后）
ssh root@<服务器IP> "cd /root/git-relay/<仓库>.git && git log --oneline -1 && git tag -l | tail -3"
```

如果有 GitHub token 可用，额外通过 API 验证：
```bash
curl -s -H "Authorization: token <token>" \
  https://api.github.com/repos/mwangxiang/<仓库>/tags | head -20
```

**步骤 6：生成归档报告**

```
=== Data Sync Backup 报告 ===

claude-config:
  版本: v1.1
  Tag 说明: "新增 data-sync skill, windtunnel 更新"
  推送方式: 服务器中转 (路径 B)
  GitHub: mwangxiang/claude-config 验证通过
  变更统计: 15 files, +320 -45 (自 v1.0)
  归档大小: ~2.1 MB (git pack)

knowledge-base:
  版本: v1.0
  Tag 说明: "初始归档：记忆库+skill-factory+SOP"
  推送方式: 服务器中转 (路径 B)
  GitHub: mwangxiang/wangxiang-study-lab 验证通过
  变更统计: 272 files (首次归档)
  归档大小: ~8.5 MB (git pack)

归档历史:
  claude-config: v1.0 (02-20) → v1.1 (02-23) [本次]
  knowledge-base: v1.0 (02-23) [本次, 首次]

建议下一步: 归档完成，GitHub 已保存完整快照。下次累积较多变更后再 backup。
```

---

## 子命令四：Status（同步状态）

**场景**：快速查看各仓库在本机、服务器、GitHub 三个节点的同步状态。

### 执行流程

**步骤 1：收集信息**

对每个仓库，并行收集：

```bash
# 本机
git -C <本机路径> log -1 --format="%h %s (%ci)"
git -C <本机路径> status --short | wc -l
git -C <本机路径> describe --tags --abbrev=0 2>/dev/null
git -C <本机路径> rev-list --count HEAD 2>/dev/null

# 服务器
ssh -o ConnectTimeout=5 root@<服务器IP> \
  "cd /root/git-relay/<仓库>.git && git log -1 --format='%h %s (%ci)'"

# 对比 hash
LOCAL_HASH=$(git -C <本机路径> log -1 --format="%H")
SERVER_HASH=$(ssh root@<服务器IP> "cd /root/git-relay/<仓库>.git && git log -1 --format='%H'")
```

**步骤 2：判定同步状态**

```
比较 LOCAL_HASH 和 SERVER_HASH
│
├─ 相同 → "已同步"
├─ 本机领先（本机有服务器没有的 commit） → "本机有未推送的变更"
├─ 服务器领先（服务器有本机没有的 commit） → "服务器有更新，需要 pull"
└─ 双方都有对方没有的 commit → "已分叉，需要手动处理"
```

**步骤 3：展示报告**

```
=== Data Sync Status ===

claude-config:
  本机:    abc1234 "sync: 更新skill" (2026-02-23 20:00)
  服务器:  abc1234 "sync: 更新skill" (2026-02-23 20:00)
  同步状态: 已同步
  未提交修改: 0 个文件
  最近 tag: v1.1 (距今 3 commits)

knowledge-base:
  本机:    def5678 "sync: 记忆库" (2026-02-23 19:30)
  服务器:  aaa9999 "sync: 另一台电脑推送" (2026-02-23 21:00)
  同步状态: 服务器有更新，需要 pull
  未提交修改: 2 个文件
  最近 tag: v1.0 (距今 5 commits)

建议下一步:
  → knowledge-base: 先 pull 最新，再处理本地修改
  → 可执行 /data-sync pull 自动处理
```

---

## 核心规则

### 1. 绝不删除本地文件
- 所有 git 操作使用安全模式（`--ff-only`、不使用 `--force`）
- pull 冲突时报告给用户，不自动覆盖
- **禁止的命令**：`git reset --hard`、`git clean -f`、`git checkout .`、`git push --force`

### 2. 增量优先
- git 天然增量传输，日常同步通常 < 1 MB
- 不重复推送未变更的内容
- `.gitignore` 排除 node_modules、telemetry、debug 等大体积临时文件

### 3. 服务器是最新最全
- 两台电脑都推到服务器，服务器永远保留最完整的版本
- GitHub 只在大版本时接收推送，可以落后于服务器

### 4. 先 pull 后 push
- Push 前自动 `fetch` 检查服务器是否领先
- 如果服务器有本机没有的提交，中止 push 并要求先 pull
- 避免分叉和不必要的合并提交

### 5. 确认后再执行
- Push 和 Backup 操作展示变更摘要后，等待用户确认
- Pull 如有本地修改，先警告用户
- 大版本 Tag 需要用户确认版本号和说明

### 6. 敏感信息保护
- 推送前扫描 API key、token、password（正则：`(api_key|token|password|secret)\s*[:=]`）
- `settings.json` 中的代理地址可以推送（不含密钥）
- `tech-library.md`（含 API key）已在 `.gitignore` 中排除
- GitHub token 不写入任何 tracked 文件

---

## 错误处理

### SSH 连接失败

```
SSH 连接服务器失败
│
├─ Connection refused（端口未开放或 sshd 未运行）
│   → 提示: "服务器 SSH 端口不可达，请检查服务器状态或防火墙规则"
│   → 如果只是暂时性故障，可以先做本地 commit，稍后再 push
│
├─ Connection timed out（网络不通）
│   → 提示: "网络连接超时，请检查网络或 VPN"
│   → 建议稍后重试
│
├─ Permission denied（密钥认证失败）
│   → 提示: "SSH 认证失败，请检查 ~/.ssh/ 密钥配置"
│   → 引导: ssh-keygen + 将公钥添加到服务器
│
└─ Host key verification failed（首次连接或 IP 变更）
    → 提示: "服务器指纹变更，如确认安全请执行:"
    → ssh-keygen -R <服务器IP>
```

### Git Push 失败

```
Push 失败
│
├─ rejected (non-fast-forward)
│   → 原因: 服务器有本机没有的提交（另一台电脑推过）
│   → 处理: 先 pull 再 push（强制执行"先pull后push"规则）
│
├─ remote: Repository not found
│   → 原因: bare repo 路径错误或已被删除
│   → 处理: 检查 sync-registry.md 中的路径是否正确
│   → 恢复: ssh 到服务器确认 /root/git-relay/ 下的仓库列表
│
└─ fatal: unable to access (GitHub push)
    → 原因: GitHub 不可达或认证失败
    → 处理: 自动切换到服务器中转推送（路径 B）
```

### Git Pull 冲突

```
Pull 产生冲突
│
├─ 仅 markdown 文件冲突
│   → 展示冲突内容（<<<< ==== >>>>标记），建议用户手动选择保留哪个版本
│   → markdown 冲突通常是两端同时编辑了同一段落
│   → 解决后: git add <文件> && git commit
│
├─ 配置文件冲突（settings.json、.claude/settings.local.json）
│   → 展示两个版本的差异
│   → 建议保留当前电脑的配置（配置通常是机器特定的）
│   → 保留本机版: git checkout --ours <文件> && git add <文件>
│
└─ 其他文件冲突
    → 报告冲突文件列表和冲突行数
    → 不自动解决，逐个展示差异，交给用户处理
```

### 磁盘空间不足

```bash
# Push 前检查服务器剩余空间
ssh root@<服务器IP> "df -h /root/git-relay/ | tail -1"
```

- 如果服务器剩余 < 500 MB，发出警告
- 如果服务器剩余 < 100 MB，阻断 push 并建议清理

### 网络中断恢复

如果 push 过程中网络中断：
- git push 是原子操作，中断不会破坏远端仓库
- 重新执行相同的 push 命令即可恢复
- 提示用户: "推送被中断，请检查网络后重新执行 /data-sync push"

---

## 版本标签规范

| 场景 | Tag 格式 | 示例 |
|------|---------|------|
| 首次归档 | `v1.0` | `v1.0` |
| 常规积累归档 | `v<主>.<次+1>` | `v1.1`, `v1.2` |
| 架构变更 / 新增重要模块 | `v<主+1>.0` | `v2.0` |
| 紧急修复（可选） | `v<主>.<次>-hotfix` | `v1.1-hotfix` |

**打 tag 的时机建议**：
- 累积 10+ commits 或 20+ files changed
- 新增了重要 skill
- 记忆库有重大更新
- 电脑迁移前（确保完整备份）

---

## 扩展：添加新仓库

1. 在服务器上创建 bare repo：
   ```bash
   ssh root@129.211.0.193 "cd /root/git-relay && git init --bare <新仓库名>.git"
   ```

2. 在本机添加 relay remote：
   ```bash
   cd <本机项目路径>
   git remote add relay root@129.211.0.193:/root/git-relay/<新仓库名>.git
   git push relay <分支>
   ```

3. 在 `sync-registry.md` 仓库列表中追加一行

4. （可选）在 GitHub 创建对应的私有仓库，在服务器 bare repo 中：
   ```bash
   ssh root@129.211.0.193
   cd /root/git-relay/<新仓库名>.git
   git remote add github https://github.com/mwangxiang/<仓库名>.git
   ```

---

## 与其他 Skill 的配合

- **dev-log**：大版本归档时，可先用 `/dev-log` 生成详细的版本文档，再用 `/data-sync backup` 推送
- **distill**：蒸馏完新知识后，用 `/data-sync push` 同步到服务器
- **ai-auto-dev**：Codex 完成开发后，用 `/data-sync push` 保存成果
- **skill-factory**：新 skill 交付部署后，用 `/data-sync push` 同步到所有设备

---

## 快速参考卡

```
/data-sync init     ← 新电脑首次配置（克隆+路径适配）
/data-sync pull     ← 换电脑时，拉取最新
/data-sync push     ← 工作完毕，推送变更（自动对比大版本）
/data-sync backup   ← 里程碑时，归档到 GitHub（打 tag）
/data-sync status   ← 随时查看同步状态
```
