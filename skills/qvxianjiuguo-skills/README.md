# 曲线救国 (qvxianjiuguo-skills)

机票模糊搜索 Skills，基于 Python CDP 浏览器自动化引擎。

支持 [OpenClaw](https://github.com/anthropics/openclaw) 及所有兼容 `SKILL.md` 格式的 AI Agent 平台（如 Claude Code）。

## ⚠️ 重要免责声明

**使用本工具前请务必阅读并理解以下声明：**

### 1. 项目性质与功能范围
- 本项目**仅供技术学习和研究使用**，展示浏览器自动化技术的应用
- **严禁用于任何商业用途**，包括但不限于：付费服务、数据分析出售、商业爬虫等
- 本项目不提供任何形式的担保，也不保证持续可用

### 2. 功能限制声明
- 本项目**不提供跨平台比价服务**，不支持多平台价格对比
- 本项目**不提供任何购票服务**，无法完成机票预订、支付等操作
- 本项目仅提供模糊搜索功能和单一平台（去哪儿）的价格查询
- 实际购票请通过官方 APP 或网站完成

### 3. 账号安全风险
- **强烈建议使用小号登录**，避免使用主账号
- 使用自动化工具登录可能导致账号被封禁、限制或永久禁用
- 各平台对自动化行为有检测机制，存在封号风险
- 请自行承担账号安全风险，本工具不对任何账号损失负责

### 4. 购票安全建议
- **建议在手机官方APP上完成购票**，更加安全可靠
- 本工具仅用于价格查询，**不建议直接通过自动化方式购票**
- 支付、改签、退票等敏感操作请在官方渠道完成
- 如遇账号异常，请立即停止使用并联系平台客服

### 5. 法律免责
- 使用者需自行遵守各平台的服务条款、用户协议及相关法律法规
- 使用者需自行承担因使用本工具产生的一切法律责任和后果
- 本工具开发者**不对任何因使用本工具导致的法律纠纷、经济损失、数据泄露等负责**
- 本工具不对使用者的行为承担任何连带责任

### 6. 魔改免责声明
- 任何人对本项目进行修改、增删功能、二次开发等行为，均与原作者无关
- 修改后的版本所产生的一切问题和后果，由修改者自行承担
- 原作者不对任何衍生版本、分支版本负责

### 7. 项目来源
- 本项目基于 [xiaohongshu-skills](https://github.com/Auto-Claw-CC/xiaohongshu-skills) 改造
- 核心自动化引擎继承自该项目
- 若有关于自动化引擎的问题，可向原作者反馈

### 8. 数据准确性
- 搜索结果仅供参考，实际价格以平台官方显示为准
- 航班信息可能存在延迟、错误或不准确的情况
- 请在购票前通过官方渠道核实所有信息

### 9. 知识产权声明
- 本项目未获得任何机票平台的授权或认可
- 各平台名称（去哪儿、携程、飞猪、同程等）及相关商标归各自公司所有
- 本项目与上述平台无任何关联

### 10. 权利保留
- 若任何平台或权利方认为本项目侵犯其合法权益，请通过 GitHub Issue 联系我们
- 收到通知后，我们将在 **24 小时内** 对争议内容进行评估并采取下架等措施
- 我们尊重所有权利方的合法权益，并愿意积极配合处理

**继续使用本工具即表示您已阅读、理解并同意以上全部内容。如有异议，请立即停止使用。**

---

## 功能概览

### 核心功能：模糊搜索低价机票

**搜索出发地和目的地 0-500km（可调）范围内所有机场之间的低价机票**

系统会自动：
1. 根据出发城市，查找周边范围内的所有机场
2. 根据目的地城市，查找周边范围内的所有机场
3. 搜索这些机场之间的所有航线组合
4. 按价格排序，找到最便宜的方案

```
例如：成都 → 上海

出发地 300km 范围内机场：成都双流(CTU)、成都天府(TFU)、绵阳(MIG)、重庆江北(CKG)...
目的地 300km 范围内机场：上海浦东(PVG)、上海虹桥(SHA)、杭州萧山(HGH)、南京禄口(NKG)...

搜索组合：CTU→PVG、CTU→SHA、CTU→HGH、TFU→PVG、TFU→SHA...（最多50个组合）

结果：找到最便宜的航班，可能降落在附近机场，需地面交通接驳
```

### 搜索范围设置

| 范围 | 说明 |
|------|------|
| **0km** | 仅搜索城市内机场，不扩展 |
| **200km** | 小范围扩展，搜索附近城市机场 |
| **300km** | **默认推荐**，平衡搜索范围和速度 |
| **350km** | 较大范围，可能找到更多低价 |
| **500km** | 最大范围，搜索时间较长 |

### 功能列表

| 功能 | 说明 |
|------|------|
| **机场查询** | 根据城市名查询机场信息 |
| **附近机场** | 查询指定机场周围一定范围内的其他机场 |
| **机票搜索** | 支持去哪儿、携程、飞猪、同程四个平台 |
| **地面交通** | 当降落在附近机场时，提示地面交通方式 |
| **智能规划** | 结合地面交通成本，规划最优出行方案 |

### 核心特点：曲线救国

通过模糊搜索（搜索周围机场组合），找到更便宜的机票：

> 例如：重庆 → 秦皇岛 直飞 ¥850
> 
> 但：重庆 → 唐山（附近机场）直飞 ¥520，再转大巴到秦皇岛 ¥50
> 
> 总共 ¥570，节省 ¥280！

## 安装

### 前置条件

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) 包管理器
- Google Chrome 浏览器

### 方法一：下载 ZIP 安装（推荐）

1. 在 GitHub 仓库页面点击 **Code → Download ZIP**，下载项目压缩包。
2. 解压到你的 Agent 的 skills 目录下：

```
# OpenClaw 示例
<openclaw-project>/skills/qvxianjiuguo-skills/

# Claude Code 示例
<your-project>/.claude/skills/qvxianjiuguo-skills/
```

3. 安装 Python 依赖：

```bash
cd qvxianjiuguo-skills
uv sync
```

### 方法二：Git Clone

```bash
cd <your-agent-project>/skills/
git clone https://github.com/Xiaoyiyebuaijianghua/qvxianjiuguo-skills.git
cd qvxianjiuguo-skills
uv sync
```

## 使用方式

### 作为 AI Agent 技能使用（推荐）

安装到 skills 目录后，直接用自然语言与 Agent 对话即可：

> "帮我查2月15日重庆到秦皇岛的机票，去哪儿搜"

> "查一下北京附近300公里内有哪些机场"

> "我想从上海去成都，帮我找最便宜的方案"

### 作为 CLI 工具使用

#### 1. 启动 Chrome

```bash
python -m qvxianjiuguo.chrome_launcher
```

#### 2. 查询机场信息

```bash
# 根据城市查询机场
python -m qvxianjiuguo.cli flight-lookup --city "重庆"

# 查询附近机场
python -m qvxianjiuguo.cli flight-nearby --airport "CKG" --range 300
```

#### 3. 登录（Cookie 方式）

**推荐使用 Cookie 方式登录，更安全可靠：**

```bash
# 1. 启动 Chrome
python -m qvxianjiuguo.chrome_launcher

# 2. 在 Chrome 中手动登录去哪儿（建议使用小号）

# 3. 保存 Cookie
python -m qvxianjiuguo.cli flight-save-cookie --platform qunar

# 4. 检查登录状态
python -m qvxianjiuguo.cli flight-check-login --platform qunar
```

#### 4. 搜索机票

```bash
python -m qvxianjiuguo.cli flight-search \
  --departure "重庆" \
  --destination "北京" \
  --date "2026-03-01" \
  --platform qunar \
  --departure-range 300 \
  --destination-range 300
```

## CLI 命令参考

| 子命令 | 说明 |
|--------|------|
| `flight-lookup --city` | 根据城市查询机场信息 |
| `flight-nearby --airport --range` | 查询附近机场 |
| `flight-search` | 执行机票模糊搜索 |
| `flight-check-login --platform` | 检查平台登录状态 |
| `flight-save-cookie --platform` | 保存 Cookie 到本地（推荐） |
| `flight-load-cookie --platform` | 从本地加载 Cookie 到浏览器 |

## 支持的平台

| 平台 | 代码 | 登录支持 | 搜索支持 | 说明 |
|------|------|----------|----------|------|
| 去哪儿 | qunar | ✅ Cookie 方式 | ✅ 完整支持 | **推荐**，持续维护 |
| 携程 | ctrip | ✅ Cookie 方式 | ⚠️ 基础支持 | 不保证持续适配 |
| 飞猪 | fliggy | ✅ Cookie 方式 | ⚠️ 基础支持 | 不保证持续适配 |
| 同程 | ly | ✅ Cookie 方式 | ⚠️ 基础支持 | 不保证持续适配 |

> **重要说明**：
> - **去哪儿**是主要支持平台，会持续维护和适配
> - **携程、飞猪、同程**仅提供基础支持，**不保证持续适配**
> - 如遇其他平台搜索失败，建议切换到去哪儿平台

## 项目结构

```
qvxianjiuguo-skills/
├── src/qvxianjiuguo/           # Python CDP 自动化引擎
│   ├── flight/                 # 机票搜索模块
│   │   ├── search.py           # 模糊搜索核心
│   │   ├── types.py            # 数据类型
│   │   ├── ground_transport.py # 地面交通计算
│   │   └── platforms/          # 平台处理器
│   │       ├── qunar.py        # 去哪儿
│   │       ├── ctrip.py        # 携程
│   │       ├── fliggy.py       # 飞猪
│   │       └── ly.py           # 同程
│   ├── cli.py                  # 统一 CLI 入口
│   └── chrome_launcher.py      # Chrome 进程管理
├── data/                       # 数据文件
│   ├── airports/               # 机场数据
│   │   ├── airports.json       # 全国机场信息
│   │   └── nearby-airports-*km.json  # 附近机场数据
│   └── flight-matrix/          # 航班连接矩阵
├── skills/                     # Skills 定义
│   └── qvxian-flight-search/   # 机票搜索技能
├── SKILL.md                    # 技能入口
├── pyproject.toml              # uv 项目配置
└── README.md
```

## 技术架构

```
用户 ──→ AI Agent ──→ SKILL.md ──→ CLI ──→ CDP 引擎 ──→ Chrome ──→ 机票平台
```

## 开发

```bash
uv sync                    # 安装依赖
uv run ruff check .        # Lint 检查
uv run ruff format .       # 代码格式化
uv run pytest              # 运行测试
```

## 致谢

本项目基于 [xiaohongshu-skills](https://github.com/Auto-Claw-CC/xiaohongshu-skills) 改造，保留了核心的 CDP 自动化引擎。

## License

MIT

Copyright (c) 2026 Auto-Claw-CC
Copyright (c) 2026 Xiaoyiyebuaijianghua
