# Flap Skills（蝴蝶技能）

基于 [BNB Chain MCP](https://docs.bnbchain.org/showcase/mcp/skills/) 的 AI 技能：**创建 V5 代币**（0 税或税收，四档分配）、**USDT 买入/卖出**（按数量或按比例）、**做市刷量**（每轮 5 买 5 卖，启动销毁 5 万枚，无 USDT 时卖回 funder 后继续，日志北京时间）。代币迁移后支持 PancakeSwap V2/V3。

**技能合约（BSC）**：`0x482970490d06fc3a480bfd0e9e58141667cffedc`  
**技能版本**：1.8.0

---

## 依赖

本技能依赖 **BNB Chain MCP**。使用前请先完成：

- **连接 BNB Chain MCP**：运行 `npx @bnb-chain/mcp@latest`
- **安装 BNB Chain 官方技能**（可选）：`npx skills add bnb-chain/bnbchain-skills`

详细说明见：[BNB Chain Skills 文档](https://docs.bnbchain.org/showcase/mcp/skills/)

---

## 安装

### Cursor / Claude

在当前项目中安装（仅当前项目可用）：

```bash
npx skills add flap-builder/flap-skills
```

全局安装（所有项目可用）：

```bash
npx skills add flap-builder/flap-skills -g
```

### OpenClaw

本技能已上架 [ClawHub](https://clawhub.ai)。先安装 ClawHub CLI，再安装本技能：

```bash
npm i -g clawhub
clawhub install flap-skills
```

安装后**新开一次 OpenClaw 会话**，技能才会被加载。使用方式与下方「如何使用」相同：在对话中说「**蝴蝶技能**」即可触发。OpenClaw 需已配置 [BNB Chain MCP](https://docs.bnbchain.org/showcase/mcp/skills/)（如通过官方文档页由 bot 自行拉取并配置），且环境中已设置 `PRIVATE_KEY` 才能发送链上交易。

---

## 如何使用

### 触发方式

在对话中说「**蝴蝶技能**」即可触发本技能。

### 前置条件

- 已安装并连接 [BNB Chain MCP](https://docs.bnbchain.org/showcase/mcp/skills/)
- 在 MCP 的 `env` 中已配置 `PRIVATE_KEY`，否则无法发送链上交易

### 支持的操作

| 操作 | 说明 |
|------|------|
| **创建代币** | **0 税**：只需「蝴蝶技能 创建代币 名称：… 符号：…」（可选官网、简介、图片），不需税点、税收地址。**有税**：需「税点：…% 税收地址：0x…」并可选四档分配、官网、简介、图片；Agent 按类型跑脚本生成 meta 与 salt（0 税 8888，有税 7777）并调用合约 |
| **买入** | 先授权 USDT，再按指定代币与 USDT 数量买入 |
| **卖出（按数量）** | 指定代币地址与卖出数量 |
| **卖出（按比例）** | 指定代币地址与比例（如 50%、100%） |
| **做市/刷量** | 每轮 5 买 5 卖；启动时销毁 5 万枚；无 USDT 时卖回 funder 后继续；资金归集地址必填。停止说「**停止做市刷量**」；归集说「**归集资金**」并指定代币与目标地址。见 [SKILL.md §6](SKILL.md#6-做市刷量与创建代币买卖一致用户说一句agent-自主执行) |

### 创建代币提示词示例

**0 税代币**（只说名称和符号即可）：

```
蝴蝶技能 创建代币
名称：My Token
符号：MTK
```

可选补充官网、简介、代币图片。不需要说税点、税收地址。

**税收代币**（需税点与税收地址）：

```
蝴蝶技能 创建代币
名称：My Token
符号：MTK
税点：3%
税收地址：0x...
官网：https://example.com
简介：这是一段代币简介
```

可选指定四档分配（四者之和 100%），例如：**营销税点：50% 持币分红税点：25% 回购销毁税点：15% LP回流税点：10%**；启用持币分红时可选「**最低持币数量：1 万**」。未指定分配时默认全部归营销。

（有官网、简介或图片时，Agent 会跑 `scripts/upload-token-meta.js` 等脚本完成 meta 与 salt。）

### 完整提示词示例（实测可直接用）

以下为实测可用的自然语言示例，复制后替换地址或参数即可使用。

**示例 1：创建 0 税代币**（只说名称、符号，可选官网与简介）

```
蝴蝶技能 创建代币
名称：0税
符号：0税
官网：https://github.com/flap-builder/flap-skills
简介：这是一个AI Agent使用蝴蝶技能创建的0税测试代币，CA：0xe139ca52ffd33d7cbb0dfeaf075f943c13937777
```

（附上代币图片即可；不写税点、税收地址。）

**示例 2：创建税收代币**（四档分配 + 持币门槛）

```
蝴蝶技能 创建代币
名称：TEST
符号：TEST
税点：10%
税收地址：0x62F5cCb8b1744A427b7511374F4eb33114217199
营销税点：80% 持币分红税点：10% 回购销毁税点：10%
最低持币数量：50000
```

（LP 回流未写即 0%，四档之和 80+10+10+0=100%。附代币图片可选。）

**示例 3：买入**

```
蝴蝶技能 用 0.01 U 买入 0x37be760e5fb95f9457137b6cb5b33b0be89a7777
```

**示例 4：卖出全部**

```
蝴蝶技能 卖出所有的 0x37be760e5fb95f9457137b6cb5b33b0be89a7777
```

其他说法：按数量「蝴蝶技能 卖出 100 个 0x…」、按比例「蝴蝶技能 卖出 50% 的 0x…」。

### 买入 / 卖出示例（简要）

- 「蝴蝶技能 用 0.01 U 买入 0x…」 / 「蝴蝶技能 用 10 USDT 买入 0x…」
- 「蝴蝶技能 卖出 100 个 0x…」
- 「蝴蝶技能 卖出 50% 的 0x…」 / 「蝴蝶技能 卖出所有的 0x…」

### 做市/刷量示例（资金归集地址必填）

```
使用蝴蝶技能对 0xe139ca52ffd33d7cbb0dfeaf075f943c13937777 进行做市刷量，随机范围：1-10U，资金归集地址：0x62F5cCb8b1744A427b7511374F4eb33114217199
```

Agent 将自动：生成 20 个 worker → **自主向每人转 0.001 BNB 作 Gas**（无需你手动转）→ **MCP 对技能合约授权 USDT、setAllowedCallers 登记 worker** → 启动做市脚本（**worker 调用合约** buyForCaller/sellForCaller 买卖）。**只有你说「停止做市刷量」或 Ctrl+C 会停止**，停止后剩余代币与 BNB 归集到上述地址。**做市过程中若某 worker Gas 不足**，Agent 会**自主**用 MCP 向该 worker 转 0.001 BNB 补 gas，**无需主人批准**。

**停止做市**：说「**停止做市刷量**」或「蝴蝶技能 停止做市刷量」，Agent 会停止做市脚本（本轮结束后执行归集）；或在运行 mm-bot 的终端按 **Ctrl+C**。

**归集资金**：说「**归集资金**」或「蝴蝶技能 归集资金」，并说明代币地址与归集目标地址（或指定上次做市用的 worker 文件），Agent 会执行 `mm-collect.js` 将各 worker 的剩余代币与 BNB 归集到目标地址。例：「蝴蝶技能 归集资金，代币 0xe139…37777，归集到 0x62F5…199，worker 文件 mm-workers-20260305-074301.json」。

更多合约接口与 ABI 见仓库内 [SKILL.md](./SKILL.md) 与 [references/contract-abi.md](./references/contract-abi.md)。

---

## 捐款

如本技能对你有帮助，欢迎捐赠：

**捐款地址**：`0x62F5cCb8b1744A427b7511374F4eb33114217199`

**CA**：`0xe139ca52ffd33d7cbb0dfeaf075f943c13937777`
