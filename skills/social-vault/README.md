# SocialVault

社交平台账号凭证管理器 — 为 OpenClaw Agent 提供登录态获取、加密存储、健康监测和自动续期能力。

## 功能概览

- **多方式登录态获取**：Cookie 粘贴（3 种格式自动识别）、API Token、扫码登录
- **加密存储**：AES-256-GCM 加密，随机 IV，密钥权限 600
- **健康监测**：每 6 小时自动检查，失效告警 + 过期预警
- **自动续期**：Cookie 浏览器活跃续期 + API Token 自动刷新
- **浏览器指纹**：首次导入时记录环境参数，操作时自动还原
- **可插拔架构**：Platform Adapter 纯 Markdown 格式，支持用户自建

## 内置平台

| 平台 | 认证方式 | Cookie 有效期 |
|------|----------|---------------|
| 小红书 | Cookie / 扫码登录 | ~7 天 |
| 哔哩哔哩 | Cookie / 扫码登录 | ~30 天 |
| 知乎 | Cookie | ~30 天 |
| 百度贴吧 | Cookie | ~180 天 |

## 快速开始

```
# 添加 B站 账号
socialvault add bilibili

# 查看所有账号
socialvault list

# 检查账号状态
socialvault check

# 使用账号凭证
socialvault use bilibili-main
```

## 安全性

- 所有凭证使用 AES-256-GCM 加密存储在本地
- 密钥文件权限设为 600（仅 owner 可读写）
- 明文凭证在内存中使用后立即清除
- 密码仅用于 Token 交换，不做持久化
- 日志中不输出任何凭证内容
- vault/ 目录不入版本控制

## 目录结构

```
socialvault/
├── SKILL.md          # 主 Skill 定义
├── clawhub.json      # ClawHub 发布清单
├── scripts/          # TypeScript 辅助脚本
│   ├── types.ts
│   ├── vault-crypto.ts
│   ├── cookie-parser.ts
│   ├── health-check.ts
│   ├── fingerprint-manager.ts
│   ├── adapter-generator.ts
│   └── qrcode-server.ts
├── adapters/         # 平台适配器
│   ├── _spec.md
│   ├── _template.md
│   ├── xiaohongshu.md
│   ├── bilibili.md
│   ├── zhihu.md
│   ├── tieba.md
│   └── custom/       # 用户自建适配器
├── guides/           # 用户教程
│   ├── cookie-export-xiaohongshu.md
│   ├── cookie-export-bilibili.md
│   ├── cookie-export-zhihu.md
│   └── cookie-export-tieba.md
├── tests/            # 测试文件
│   ├── test-crypto.ts
│   ├── test-cookie-parser.ts
│   └── test-health-check.ts
└── vault/            # 运行时数据（不入版本控制）
    ├── vault.enc
    ├── vault-key
    ├── accounts.json
    └── fingerprints/
```

## 测试

```bash
npm test
```

覆盖 48 个测试用例：加密/解密、Cookie 解析、健康检查。

## 命令列表

| 命令 | 说明 |
|------|------|
| `socialvault add <platform>` | 添加账号 |
| `socialvault list` | 列出所有账号 |
| `socialvault check [account-id]` | 检查健康状态 |
| `socialvault use <account-id>` | 加载凭证到 browser |
| `socialvault update <account-id>` | 更新凭证 |
| `socialvault remove <account-id>` | 删除账号 |
| `socialvault status` | 整体状态概览 |
| `socialvault adapter list` | 列出适配器 |
| `socialvault adapter create <platform>` | 创建自定义适配器 |
| `socialvault rotate-key` | 密钥轮换 |
| `socialvault token <account-id>` | 获取 API Token |
| `socialvault release <account-id>` | 回收凭证 |

## 许可证

MIT
