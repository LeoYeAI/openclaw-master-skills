# ☁️ TSA — 腾讯云智能顾问助手

> Tencent Cloud Smart Advisor (TSA) Skill for CodeBuddy / OpenClaw

通过 **AK/SK 鉴权**调用腾讯云智能顾问 API，以对话式交互管理云架构图、查询风险评估项、生成控制台免密登录链接。

## 功能概览

- **云架构管理** — 查询目录树、架构列表、架构详情
- **风险评估** — 获取评估项列表，支持按产品/分组/风险等级筛选
- **架构评估** — 获取 Well-Architected 评估结果（总分、各维度得分、治理建议）
- **免密登录** — 自动生成腾讯云控制台直达链接，点击即可免登录跳转
- **环境自检** — 一键检测 Python 版本、密钥配置、角色状态、Skill 版本更新

## 快速开始

### 1. 配置腾讯云密钥

在 [API 密钥管理](https://console.cloud.tencent.com/cam/capi) 获取密钥，写入 shell 配置文件：

```bash
echo 'export TENCENTCLOUD_SECRET_ID="your-secret-id"' >> ~/.zshrc
echo 'export TENCENTCLOUD_SECRET_KEY="your-secret-key"' >> ~/.zshrc
source ~/.zshrc
```

### 2. 安装 Skill

**通过 ClawHub 安装（推荐）：**

在 CodeBuddy 或 OpenClaw 的 Skill 市场搜索 `tsa` 并安装。

**手动安装：**

```bash
git clone git@git.woa.com:tsa/tsa-skills.git ~/.codebuddy/skills/tsa
```

### 3. 开始使用

在 CodeBuddy 中直接对话即可：

```
> 帮我检查一下腾讯云智能顾问的环境是否配置好了
> 查看我的云架构目录
> 列出所有架构图
> 查看风险评估项
> 帮我查看待整理目录下有哪些架构图
```

## 项目结构

```
tsa/
├── SKILL.md                  # Skill 指令文档（AI 加载的核心文件）
├── _meta.json                # 元信息（slug、版本号）
├── check_env.py              # 环境检测脚本（只读，不修改任何配置）
├── scripts/
│   ├── tcloud_api.py         # 腾讯云 API 统一调用（TC3-HMAC-SHA256 签名）
│   ├── create_role.py        # CAM 角色创建（需用户明确同意）
│   ├── setup_role.py         # 角色配置向导（交互式）
│   ├── login_url.py          # 免密登录链接生成
│   └── cleanup.py            # 配置清理（本地 + 云端）
├── references/               # API 接口文档（6 个接口）
│   ├── DescribeArch.md
│   ├── DescribeArchList.md
│   ├── DescribeLastEvaluation.md
│   ├── DescribeStrategies.md
│   ├── ListDirectoryV2.md
│   └── ListUnorganizedDirectory.md
├── tests/
│   ├── run.sh                # 测试框架（离线 + E2E）
│   └── cases/                # E2E 测试用例
├── publish.sh                # ClawHub 发布脚本
├── CONTRIBUTING.md           # 贡献指南
└── README.md
```

## API 接口

共 6 个接口，统一通过 `scripts/tcloud_api.py` 调用，服务域名 `advisor.tencentcloudapi.com`。

| 接口 | 说明 | 详细文档 |
|------|------|----------|
| `DescribeArchList` | 分页获取云架构图列表 | `references/api/DescribeArchList.md` |
| `DescribeArch` | 获取指定架构图详情 | `references/api/DescribeArch.md` |
| `ListDirectoryV2` | 查询架构目录树 | `references/api/ListDirectoryV2.md` |
| `ListUnorganizedDirectory` | 查询待整理目录 | `references/api/ListUnorganizedDirectory.md` |
| `DescribeStrategies` | 获取风险评估项列表 | `references/api/DescribeStrategies.md` |
| `DescribeLastEvaluation` | 获取架构评估结果 | `references/api/DescribeLastEvaluation.md` |

调用示例：

```bash
python3 scripts/tcloud_api.py advisor advisor.tencentcloudapi.com DescribeArchList 2020-07-21 '{"PageNumber":1,"PageSize":10}'
```

## 测试

测试框架包含 **离线测试**（39 项）和 **E2E 对话式测试**（7 个用例），共 56 项断言。

### 前置条件

- Python 3.7+
- CodeBuddy CLI（`codebuddy`）或 OpenClaw CLI（`openclaw`）
- 环境变量 `TENCENTCLOUD_SECRET_ID` 和 `TENCENTCLOUD_SECRET_KEY` 已配置

### 运行测试

```bash
# 运行全部测试（离线 + E2E）
bash tests/run.sh

# 仅运行离线测试（不需要 CLI 和网络）
bash tests/run.sh --offline

# 运行指定 E2E 用例
bash tests/run.sh --case 01

# 指定 CLI 工具
bash tests/run.sh --cli codebuddy
bash tests/run.sh --cli openclaw
```

### E2E 用例

| 用例 | 说明 |
|------|------|
| `01_env_check` | 环境检测 |
| `02_list_directory` | 查询架构目录 |
| `03_list_arch` | 查询架构列表 |
| `04_strategies` | 查询风险评估项 |
| `05_unorganized` | 查询待整理目录 |
| `06_login_url` | 免密登录链接生成 |
| `07_json_format` | API 输出 JSON 格式校验 |

E2E 测试会自动将每个用例的输入（prompt）和输出保存到 `tests/output/` 目录。

## 发布

通过 `publish.sh` 将 Skill 发布到 ClawHub 平台：

```bash
# 设置 ClawHub Token
export CLAWHUB_TOKEN="your-api-token"

# 发布（需提供 changelog）
./publish.sh "修复版本检查逻辑"

# 或直接传入 token
./publish.sh "修复版本检查逻辑" "your-api-token"
```

发布时会自动排除 `tests/`、`__pycache__/`、`.git/`、`publish.sh`、`CONTRIBUTING.md` 等非发布文件。版本号从 `_meta.json` 中读取。

## 安全说明

- **密钥安全** — AK/SK 仅通过环境变量读取，不会写入文件、日志或网络传输
- **角色创建** — CAM 角色创建为独立脚本，必须用户明确同意后才会执行
- **临时凭证** — STS 临时凭证仅在内存中使用，不持久化存储
- **配置文件** — `~/.tencent-cloudq/config.json` 仅保存角色 ARN，不保存密钥
- **网络访问** — 仅连接腾讯云官方域名（`*.tencentcloudapi.com`、`cloud.tencent.com`）

## 许可证

内部项目，仅限腾讯内部使用。
