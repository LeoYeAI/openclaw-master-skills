# Data Sync 仓库注册表

本文件记录所有需要同步的仓库信息。添加新仓库时只需在表格中追加一行。

## 仓库列表

| 仓库ID | 内容描述 | 本机路径 | 服务器 bare repo 路径 | GitHub 仓库 | 分支 |
|--------|---------|---------|---------------------|-------------|------|
| claude-config | .claude 配置（skills, hooks, windtunnel） | `~/.claude` | `/root/git-relay/claude-config.git` | `mwangxiang/claude-config` | master |
| knowledge-base | 记忆库、skill-factory、蒸馏文档、SOP | `<项目根>/VScode辅助工作学习` | `/root/git-relay/claude-knowledge-base.git` | `mwangxiang/wangxiang-study-lab` | master |

## 服务器信息

| 项目 | 值 |
|------|-----|
| IP | `129.211.0.193` |
| 用户 | `root` |
| 认证 | SSH 密钥 |
| relay 目录 | `/root/git-relay/` |

## Remote 命名规范

| Remote 名 | 指向 | 用途 |
|-----------|------|------|
| `relay` | 服务器 bare repo | 日常同步（高频） |
| `origin` 或 `github` | GitHub 仓库 | 大版本归档（低频） |

## 路径适配说明

`本机路径` 列中：
- `~/.claude` 自动展开为当前用户目录下的 `.claude`
- `<项目根>` 需在新电脑上首次 init 时填入实际路径

**添加新仓库时**，需同步执行：
1. 在服务器上 `git init --bare /root/git-relay/<新仓库名>.git`
2. 在本机 `git remote add relay root@129.211.0.193:/root/git-relay/<新仓库名>.git`
3. 在此文件追加一行
4. （可选）在 GitHub 创建对应私有仓库，在服务器 bare repo 中 `git remote add github <url>`
