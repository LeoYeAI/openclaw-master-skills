---
name: flapskill
displayName: 蝴蝶技能
version: 1.8.0
description: 创建 V5 代币（0 税或税收，四档分配）；USDT 买入、按数量或按比例卖出；做市刷量（每轮 5 买 5 卖，启动销毁 5 万枚，无 USDT 时卖回 funder 后继续，日志北京时间）。说「蝴蝶技能」触发。依赖 BNB Chain MCP。
---

# 蝴蝶技能：创建代币、买入/卖出代币（USDT）

用户说「**蝴蝶技能**」即触发本技能。通过 FlapSkill 合约可**创建** V5 代币（0 税或税收；税收时代币可分配营销/持币分红/回购销毁/LP回流 四档税点，受益人 feeTo），或用 **USDT** 买入/卖出指定代币；买卖经 Portal 或 PancakeSwap 兑换，代币/USDT 转给调用者。

**USDT 合约地址（BSC）**：`0x55d398326f99059fF775485246999027B3197955`。

**前置条件：** 用户需已配置 [BNB Chain MCP](https://docs.bnbchain.org/showcase/mcp/skills/)（如已安装 `bnbchain-mcp-skill`），且 MCP 的 `env` 中已设置 `PRIVATE_KEY`，否则无法发送交易。

---

## 1. 合约接口

**合约地址**：`0x482970490d06fc3a480bfd0e9e58141667cffedc`。

### 创建代币 createToken

- **方法**：`createToken(string _name, string _symbol, string _meta, address _feeTo, bytes32 _salt, uint16 _taxRate, uint16 _mktBps, uint16 _dividendBps, uint16 _deflationBps, uint16 _lpBps, uint256 _minimumShareBalance) external returns (address token)`
- **含义**：经 Portal 创建 V5 代币。**0 税代币**：`_taxRate=0`，不校验四档分配，合约使用 V3_MIGRATOR；**salt 须用尾号 8888**（脚本：`node scripts/find-vanity-salt.js 8888`）。**税收代币**：`_taxRate` 1–1000（如 300=3%），`_mktBps`（营销）、`_dividendBps`（持币分红）、`_deflationBps`（回购销毁）、`_lpBps`（LP 回流）四者之和须为 10000；**salt 须用尾号 7777**（全营销用 `find-vanity-salt.js 7777`，四档分配用 `find-vanity-salt.js 7777 v2`）。若 `_dividendBps > 0`，`_minimumShareBalance` 须 ≥ 10_000 ether；用户未说时 Agent 默认 10_000 ether。详见 [Flap Portal](https://docs.flap.sh/flap/developers/token-launcher-developers/launch-token-through-portal) 与 [部署地址](https://docs.flap.sh/flap/developers/token-launcher-developers/deployed-contract-addresses)（standard:8888，Tax:7777）。无需 approve。
- **约束**：`_salt` 为 bytes32（0x+64 位十六进制），每次创建用不同 salt；**必须按税点选对尾号（0 税→8888，有税→7777）及对应脚本 impl（7777 四档时加 v2）**。
- **何时用**：**0 税**：用户说「蝴蝶技能 创建代币 名称：… 符号：…」即可，可选官网、简介、代币图片；**不需说税点、税收地址**，Agent 自动 taxRate=0、feeTo=调用者地址、salt 用 8888。**有税**：用户说「蝴蝶技能 创建代币 名称：… 符号：…，税点：…% 税收地址：0x…」并可选四档分配、官网、简介、图片；有税且未指定四档时默认全部归营销；启用持币分红时用户可说「最低持币数量：1 万」等，不说则默认 10_000 ether。**_meta、_salt 由 Agent 跑脚本填入；官网、简介须传入 upload 脚本。**

### 买入 buyTokens

- **方法**：`buyTokens(address _token, uint256 _usdtAmount) external`
- **含义**：从调用者转入 `_usdtAmount`（18 位小数）的 USDT，向 Portal 兑换 `_token` 代币，代币转给调用者。
- **约束**：调用前须对 FlapSkill 合约 approve 至少 `_usdtAmount` 的 USDT。

### 卖出（按数量）sellTokens

- **方法**：`sellTokens(address _token, uint256 _tokenAmount) external`
- **含义**：从调用者转入指定数量 `_tokenAmount` 的代币，向 Portal 兑换为 USDT，USDT 转给调用者。无滑点保护。
- **约束**：调用前须对 FlapSkill 合约 approve 至少 `_tokenAmount` 的该代币。`_tokenAmount` 为该代币最小单位。
- **何时用**：用户说「蝴蝶技能卖出 X 个 0x…」「卖出100个的0x…」等**具体数量**时，用本方法。

### 卖出（按仓位比例）sellTokensByPercent

- **方法**：`sellTokensByPercent(address _token, uint256 _percentBps) external`
- **含义**：按调用者当前该代币持仓的 **比例** 卖出。合约内读取 `balanceOf(msg.sender)`，卖出数量 = 余额 × `_percentBps` / 10000。无滑点保护。
- **约束**：调用前须对 FlapSkill 合约 approve 至少「该比例对应的数量」（建议直接 approve 全部仓位或足够大的数）。
- **何时用**：用户说「蝴蝶技能卖出50%的0x…」「卖出一半 0x…」等**比例**时，用本方法。`_percentBps` 为基点：10000=100%，5000=50%，1000=10%。

---

## 2. 创建代币：使用 BNB Chain MCP 调用

### 2.1 _meta 与 _salt 由 Agent 直接填写（脚本已打包在本技能内）

- **\_meta** 和 **\_salt** 不由用户提供，**由 Agent 在技能目录下执行本技能自带的脚本得到并直接填入** createToken 的 args。
- **脚本位置**：本技能目录下的 `scripts/`（`upload-token-meta.js`、`find-vanity-salt.js`）。安装后技能目录通常为 `.agents/skills/flap-skills`（项目）或 `~/.cursor/skills/flap-skills`（全局），本仓库内为 `skills/flap-skills`。**Agent 须先 cd 到该技能目录**，若未安装依赖则先执行 `npm install`，再执行下面两步。
- 上传 meta 时须带上**官网**和**简介**（见 [Flap 文档](https://docs.flap.sh/flap/developers/token-launcher-developers/launch-token-through-portal)）：用户创建代币时可选提供「官网：…」「简介：…」，Agent 传入脚本，格式为 `node scripts/upload-token-meta.js <图片路径> "<简介>" "<官网>" [twitter] [telegram]`，脚本将简介写入 meta.description、官网写入 meta.website。
- **Salt 尾号与脚本**（见 [Flap 文档](https://docs.flap.sh/flap/developers/token-launcher-developers/launch-token-through-portal#3-find-the-salt-vanity-suffix)、[部署地址](https://docs.flap.sh/flap/developers/token-launcher-developers/deployed-contract-addresses)）：**0 税**（税点 0%）→ 地址尾号 **8888**，执行 `node scripts/find-vanity-salt.js 8888`；**有税**→ 地址尾号 **7777**，全营销执行 `node scripts/find-vanity-salt.js 7777`，四档分配执行 `node scripts/find-vanity-salt.js 7777 v2`。
- 流程：**0 税**：用户只说「蝴蝶技能 创建代币 名称：… 符号：…」（可选官网、简介、图片）。Agent 在技能目录下：① 上传 meta（有图/官网/简介时跑 upload 脚本，否则可用占位 CID 或简单 meta）；② 执行 `node scripts/find-vanity-salt.js 8888` 得 _salt；③ _feeTo = 调用者地址（发送交易的钱包），_taxRate=0，四档与 minimumShareBalance 均 0；④ `write_contract` createToken(…)。**有税**：用户说「名称：… 符号：…，税点：…% 税收地址：0x…」并可选四档、官网、简介、图片。Agent：① 跑 upload 脚本得 _meta；② 按税点跑 salt（全营销 7777，四档 7777 v2）；③ 确定四档与 minimumShareBalance；④ `write_contract` createToken(…)。
- 用户**无需**写 meta、salt；0 税**无需**说税点、税收地址，Agent 用调用者地址作 feeTo。

### 2.2 调用 createToken

无需 approve，直接 **`write_contract`**：

| 参数 | 说明 |
|------|------|
| `contractAddress` | `0x482970490d06fc3a480bfd0e9e58141667cffedc` |
| `abi` | createToken 的 ABI（见 [references/contract-abi.md](references/contract-abi.md)） |
| `functionName` | `"createToken"` |
| `args` | `[_name, _symbol, _meta, _feeTo, _salt, _taxRate, _mktBps, _dividendBps, _deflationBps, _lpBps, _minimumShareBalance]`。**0 税**：_feeTo=调用者地址，_taxRate=0，四档与 minimumShareBalance 填 0，_salt 用 8888。**有税**：_feeTo=用户提供的税收地址，_taxRate 1–1000，四档之和 10000，_salt 用 7777 或 7777 v2。**_meta、_salt 由 Agent 跑脚本填入。** |
| `network` | 可选，默认 `bsc` |

---

## 3. 买入：使用 BNB Chain MCP 调用

### 3.1 先授权 USDT（approve）

| 参数 | 说明 |
|------|------|
| `tokenAddress` | USDT：`0x55d398326f99059fF775485246999027B3197955` |
| `spenderAddress` | FlapSkill：`0x482970490d06fc3a480bfd0e9e58141667cffedc` |
| `amount` | 要支付的 USDT 数量（人类可读如 `"0.01"`） |
| `network` | 可选，默认 `bsc` |

### 3.2 再调用 buyTokens

| 参数 | 说明 |
|------|------|
| `contractAddress` | FlapSkill：`0x482970490d06fc3a480bfd0e9e58141667cffedc` |
| `abi` | buyTokens 的 ABI（见 [references/contract-abi.md](references/contract-abi.md)） |
| `functionName` | `"buyTokens"` |
| `args` | `[_token, _usdtAmount]`：目标代币地址、USDT 最小单位（18 位小数，如 0.01 USDT = `"10000000000000000"`） |
| `network` | 可选，默认 `bsc` |

---

## 4. 卖出（按数量）：使用 BNB Chain MCP 调用

用户说**具体数量**（如「蝴蝶技能卖出100个的0x…」）时用此流程。

### 4.1 先授权要卖出的代币（approve）

| 参数 | 说明 |
|------|------|
| `tokenAddress` | 要卖出的代币合约地址 |
| `spenderAddress` | FlapSkill：`0x482970490d06fc3a480bfd0e9e58141667cffedc` |
| `amount` | 要卖出的代币数量（人类可读或最小单位，≥ 本次 `_tokenAmount`） |
| `network` | 可选，默认 `bsc` |

### 4.2 再调用 sellTokens

| 参数 | 说明 |
|------|------|
| `contractAddress` | FlapSkill：`0x482970490d06fc3a480bfd0e9e58141667cffedc` |
| `abi` | sellTokens 的 ABI（见 [references/contract-abi.md](references/contract-abi.md)） |
| `functionName` | `"sellTokens"` |
| `args` | `[_token, _tokenAmount]`：代币地址、卖出数量（该代币最小单位） |
| `network` | 可选，默认 `bsc` |

**注意**：`_tokenAmount` 须按该代币 decimals 换算为最小单位（如 18 位小数，1 个 = `"1000000000000000000"`）。

---

## 5. 卖出（按仓位比例）：使用 BNB Chain MCP 调用

用户说**比例**（如「蝴蝶技能卖出50%的0x…」「卖出一半0x…」）时用此流程。

### 5.1 可选：查询用户该代币余额

用 **`get_erc20_balance`**（tokenAddress=代币，address=用户）得到余额，便于确认或向用户展示。合约内部会再次按当前区块状态计算比例，无需用此结果参与合约参数。

### 5.2 授权代币（approve）

建议对 FlapSkill approve **至少对应比例的数量**，或直接 approve 全部仓位（如 `amount` 用很大或「max」）。例如卖 50% 时，approve 至少当前余额的 50% 或全部。

| 参数 | 说明 |
|------|------|
| `tokenAddress` | 要卖出的代币合约地址 |
| `spenderAddress` | FlapSkill：`0x482970490d06fc3a480bfd0e9e58141667cffedc` |
| `amount` | 建议 ≥ 本次要卖出的数量（可按比例算，或直接填足够大） |
| `network` | 可选，默认 `bsc` |

### 5.3 调用 sellTokensByPercent

| 参数 | 说明 |
|------|------|
| `contractAddress` | FlapSkill：`0x482970490d06fc3a480bfd0e9e58141667cffedc` |
| `abi` | sellTokensByPercent 的 ABI（见 [references/contract-abi.md](references/contract-abi.md)） |
| `functionName` | `"sellTokensByPercent"` |
| `args` | `[_token, _percentBps]`：代币地址、比例基点（10000=100%，5000=50%，1000=10%） |
| `network` | 可选，默认 `bsc` |

**比例换算**：用户说 50% → `_percentBps` = `"5000"`；10% → `"1000"`；100% → `"10000"`。

---

## 6. 做市/刷量（与创建代币、买卖一致：用户说一句，Agent 自主执行）

做市与**创建代币、买卖**相同：用户只需说一句自然语言，**Agent 自主**用 MCP 钱包完成链上授权与登记并**启动做市脚本**，无需用户再手动发交易或跑命令。

**约定**：资金方（funder）= **MCP 当前发交易的钱包**（即 MCP 中 `PRIVATE_KEY` 对应地址）。**做市由 MCP 授权给技能合约**（对 FlapSkill approve USDT + setAllowedCallers 登记 worker），**由 worker 调用合约** buyForCaller/sellForCaller 完成买卖，**不是 MCP 直接买卖**。做市 **只有启动与停止**，不设磨损上限。Agent 在技能目录执行 `node scripts/mm-generate-workers.js` 生成 2～20 个随机 worker 密钥并**按生成时间命名导出到本地**（`mm-workers-<YYYYMMDD>-<HHmmss>.json`），**自主**通过 MCP 的 **transfer_native_token** 向每个 worker 地址**逐笔转 0.001 BNB 作 Gas**（**由 Agent 自主完成，用户无需手动转 BNB**），然后 MCP 对 FlapSkill **approve USDT**、**setAllowedCallers**，并启动 mm-bot（worker 私钥从该文件读取，由 worker 调用合约买卖）。**用户无需提供 worker 地址、私钥或手动转 BNB**，只说一句即可刷量。**做市过程中若某 worker 出现 Gas 不足**，Agent **自主**使用 MCP **transfer_native_token** 向该 worker（或 mm-bot 日志中提示的 buyer/seller 地址）转 0.001 BNB 补 gas，**无需主人批准**，视为做市授权的一部分。

### 6.1 自然语言示例（做市/刷量）

用户说一句，Agent **自主**解析并**依次执行**：生成 worker → **Agent 自主用 MCP transfer_native_token 向每个 worker 发 0.001 BNB 作 Gas** → **MCP 对 FlapSkill 合约 approve USDT（授权合约可划转 funder 的 USDT）、setAllowedCallers 登记 worker** → 在技能目录启动 `mm-bot.js`（**由 worker 调用合约** buyForCaller/sellForCaller 买卖，不是 MCP 直接买卖）。**做市只有启动与停止**，不会因磨损自动停止。

**示例：**
```
使用蝴蝶技能对 0xe139ca52ffd33d7cbb0dfeaf075f943c13937777 进行做市刷量，随机范围：1-10U，资金归集地址：0x62F5cCb8b1744A427b7511374F4eb33114217199
```
 
**参数对应：**

| 用户说法 | 含义 | 对应操作 / 配置 |
|----------|------|------------------|
| 对 **0x…** 进行做市刷量 | 代币合约地址 | `TOKEN_CA`、setAllowedCallers 的 token 参数 |
| **提供资金：100U** | 用于做市的资金规模（参考；授权采用无限授权） | MCP 对 FlapSkill **无限授权** USDT（amount = max uint256，见下文） |
| **随机范围：1-10U**（或 成交金额：1-10U） | 每笔买卖的 USDT 随机范围 | `USDT_MIN=1`，`USDT_MAX=10` |
| **资金归集地址：0x…** | **必填**。做市停止后 worker 剩余代币与 BNB 归集到该地址 | 启动 mm-bot 时设置 `COLLECT_TO_ADDRESS`；**只有用户说「停止做市刷量」或 Ctrl+C 会停止**，停止后自动执行归集 |

做市时 **MCP（funder）对 FlapSkill 合约** 的 USDT 授权采用**无限授权**：amount = max uint256，即 `"115792089237316195423570985008687907853269984665640564039457584007913129639935"`。若当前 MCP/viem 传该值时报溢出（如内部按 10^18 换算导致超范围），可改用大数值如 `"1000000000000000000000000000"`（10^27）作为回退。避免 worker 调用 buyForCaller 时因额度用尽报 TRANSFER_FROM_FAILED。**资金归集地址为必填**：用户必须提供「资金归集地址：0x…」，否则 Agent 不启动 mm-bot 并提示用户补充。**不设磨损上限**：合约已去掉磨损逻辑，做市只有启动与停止。未说「随机范围」/「成交金额」时用脚本默认（如 0.005～0.02 U）。未说「提供资金」时由 Agent 询问或按常见值（如 100 U）建议。**worker 由 Agent 自动生成**，无需用户配置。

### 6.2 合约接口（skill.sol）

- **setAllowedCallers(address _token, address[] _callers)**：由 **funder** 调用，登记对该 `_token` 允许调用 buyForCaller/sellForCaller 的地址（做市脚本的 worker 地址）。**调用时合约会从 funder 划转 5 万枚该代币到 0x0000…dEaD 销毁**，故调用前 funder 须对该 `_token` 向 FlapSkill approve 至少 5 万枚（`"50000"`）。小明对 0x0123 刷量前，小明须先 approve 0x0123 代币 5 万枚再调用 setAllowedCallers(0x0123, [小明的 worker 地址...])。
- **buyForCaller(address _token, uint256 _usdtAmount, address _funder)**：仅当 msg.sender 已被 _funder 对该 _token 登记时可调用；用 _funder 的 USDT 买入，代币转给调用者。调用前 _funder 须对 FlapSkill approve USDT。
- **sellForCaller(address _token, uint256 _tokenAmount, address _funder)**：仅当 msg.sender 已被 _funder 对该 _token 登记时可调用；调用者交出代币卖出，所得 USDT 转给 _funder。
- **removeAllowedCallers(address _token, address[] _callers)**：funder 取消某 token 下部分地址的调用权限。

ABI 见 [references/contract-abi.md](references/contract-abi.md)。

### 6.3 脚本与运行方式

- **生成 worker**：本技能目录下 `node scripts/mm-generate-workers.js [N]`（默认 N=20）生成 N 个随机 worker 私钥与地址，**按生成时间命名导出**为 `mm-workers-<YYYYMMDD>-<HHmmss>.json`。加 `--json` 时 stdout 输出 `{ "addresses": [...], "file": "<绝对路径>" }`，供 setAllowedCallers 用 `addresses`、启动 mm-bot 时用 `file` 作为 `PRIVATE_KEYS_FILE`。Agent 自主执行时先运行此脚本得到 worker 地址列表与导出文件路径。
- **做市脚本**：`scripts/mm-bot.js`（需在技能目录先 `npm install`）。支持从环境变量 `PRIVATE_KEYS` 或从文件 `PRIVATE_KEYS_FILE=<路径>`（由 mm-generate-workers 生成的按时间命名的文件）读取 worker 私钥。Agent 在**自主执行**时先完成链上三步（见 6.5），再运行 mm-bot。
- **流程**：每轮地址 A 调 **buyForCaller**(token, amount, funder) → A 将代币转给 B → B 调 **sellForCaller**(token, balance, funder)。金额在 [USDT_MIN, USDT_MAX] 内随机。

### 6.4 配置（环境变量或 CLI 参数）

| 配置项 | 环境变量 | CLI 参数位置 | 说明 |
|--------|----------|--------------|------|
| 资金方地址（funder） | `FUNDER_ADDRESS` | — | 必填，MCP 钱包地址，须已对 FlapSkill approve USDT |
| **资金归集地址** | `COLLECT_TO_ADDRESS` | — | **必填**，停止时将 worker 剩余代币与 BNB 归集到该地址 |
| 交易地址私钥 | `PRIVATE_KEYS` 或 `PRIVATE_KEYS_FILE` | — | 二选一：逗号分隔的 2～20 个私钥，或指向按时间命名的导出文件路径（mm-workers-YYYYMMDD-HHmmss.json）；worker 仅需 BNB 作 gas |
| 代币地址 | `TOKEN_CA` | 第 1 个 | 必填 |
| 每笔 USDT 下限 | `USDT_MIN` | 第 2 个 | 默认 0.005，与上限之间随机 |
| 每笔 USDT 上限 | `USDT_MAX` | 第 3 个 | 默认 0.02 |
| 间隔（秒） | `INTERVAL_SEC` | 第 4 个 | 默认 15 |
| 轮数（0=无限） | `ROUNDS` | 第 5 个 | 默认 0 |
| RPC | `RPC_URL` | — | 默认 BSC 公网 |

示例：

```bash
# 前置：MCP（funder）对 FlapSkill 合约 approve USDT 并 setAllowedCallers；买卖由 worker 调用合约完成。worker 私钥二选一：
# 方式一：Agent 已生成 worker 导出文件时（文件名 mm-workers-YYYYMMDD-HHmmss.json）
export FUNDER_ADDRESS=0x...           # MCP 钱包地址
export PRIVATE_KEYS_FILE=./mm-workers-20260304-220057.json   # 或脚本 --json 输出中的 file 路径
export TOKEN_CA=0x...
node scripts/mm-bot.js

# 方式二：自行提供私钥
export FUNDER_ADDRESS=0x...
export PRIVATE_KEYS=0xkey1,0xkey2,...,0xkey20
export TOKEN_CA=0x...
export USDT_MIN=0.005
export USDT_MAX=0.02
node scripts/mm-bot.js
```

### 6.5 Agent 自主执行流程（与创建代币、买卖一致）

**做市刷量流程概览**：① 解析参数（代币、资金、随机范围、**资金归集地址**）→ ② 生成 worker 并导出文件 → ③ **Agent 自主用 MCP transfer_native_token 向每个 worker 转 0.001 BNB（Gas）** → ④ **MCP（funder）对 FlapSkill approve USDT（无限）** → ⑤ **MCP 对做市代币 approve 5 万枚给 FlapSkill** → ⑥ **MCP 调用 setAllowedCallers**（合约内将 5 万枚该代币从 funder 转入 0x0000…dEaD 销毁并登记 worker）→ ⑦ 启动 mm-bot（**worker 调用合约** buyForCaller/sellForCaller 买卖）。**只有用户说「停止做市刷量」或 Ctrl+C 会停止**，不会因磨损自动停止。

当用户说「蝴蝶技能 对 0x… 做市刷量」「使用蝴蝶技能对 0x… 进行做市刷量，提供资金：…，随机范围：…，资金归集地址：0x…」等时，Agent **自主**完成以下步骤（无需用户再手动发交易或跑脚本）：

1. **解析自然语言**：从用户句中提取「代币地址」「提供资金（U）」「随机范围/成交金额（最小-最大 U）」「**资金归集地址**（必填）」。**不解析磨损**，做市不设磨损上限。**若用户未提供资金归集地址，则提示：「请提供资金归集地址（做市停止后 worker 剩余资金将归集到该地址）」，不执行后续步骤。** 未说提供资金时询问或建议（如 100 U）；未说随机范围时用脚本默认。
2. **生成 worker**：在**技能目录**执行 `node scripts/mm-generate-workers.js [N] --json`（默认 N=20），脚本按生成时间命名将私钥与地址导出到本地（如 `mm-workers-20260304-220057.json`）；stdout 输出 `{ "addresses": [...], "file": "<绝对路径>" }`，用 `addresses` 做 setAllowedCallers、用 `file` 做 PRIVATE_KEYS_FILE。若本次做市希望复用已有导出文件，可跳过本步并直接使用该文件的路径与其中的 `addresses`。
3. **给 worker 发 Gas（必须由 Agent 自主执行，不可省略或交给用户）**：Agent **自主**使用 MCP 的 **transfer_native_token**，向步骤 2 得到的每个 worker 地址**逐笔**转 **0.001 BNB**，供 worker 调用 buyForCaller/sellForCaller 时付 gas。共 N 笔（N = worker 数量，如 20）。**此步必须由 Agent 在启动 mm-bot 前完成**，用户无需操作。  
   **MCP 调用参数**：`toAddress`（worker 地址，注意参数名为 toAddress 而非 to）、`amount`：`"0.001"`、`network`：`"bsc"`。若某笔报错 replacement transaction underpriced，可间隔数秒后重试该笔。
4. **获取 funder**：funder 地址 = MCP 当前发交易使用的钱包地址（即 `PRIVATE_KEY` 对应地址）。
5. **链上三步（MCP 用 funder 钱包调用，仅授权给合约、登记 worker，不做买卖）**：  
   - ① **approve_token_spending**：token=USDT（`0x55d398326f99059fF775485246999027B3197955`），spender=FlapSkill（`0x482970490d06fc3a480bfd0e9e58141667cffedc`），amount=**无限授权** max uint256：`"115792089237316195423570985008687907853269984665640564039457584007913129639935"`；若 MCP/viem 报溢出则回退为 `"1000000000000000000000000000"`。即 **MCP 授权给技能合约**，允许合约从 funder 划转 USDT。  
   - ② **approve_token_spending**：token=**做市代币地址**（本次做市的 `TOKEN_CA`），spender=FlapSkill，amount=`"50000"`（5 万枚；合约在 setAllowedCallers 内会将该数量从 funder 转入 0x0000…dEaD 销毁）。  
   - ③ **write_contract**：contractAddress=FlapSkill，abi=setAllowedCallers 的 ABI，functionName=`"setAllowedCallers"`，args=`[代币地址, worker地址数组]`，network=`"bsc"`。登记后 **worker 才能调用** buyForCaller/sellForCaller；同时会执行上述 5 万枚销毁。  
   - ④ 无需 setMaxWear（合约已去掉磨损逻辑）。做市**只有启动与停止**，不会因磨损自动停止。**买卖由 mm-bot 用 worker 私钥调用合约完成**，不是 MCP 直接买卖。
6. **启动做市脚本**：在**技能目录**下执行（可后台运行）：  
   `FUNDER_ADDRESS=<funder地址> PRIVATE_KEYS_FILE=<上一步生成的文件绝对路径> TOKEN_CA=<代币> COLLECT_TO_ADDRESS=<用户提供的资金归集地址> USDT_MIN=<解析出的下限> USDT_MAX=<解析出的上限> node scripts/mm-bot.js`  
   其中 PRIVATE_KEYS_FILE 使用步骤 2 中 `--json` 输出里的 `file` 字段；**COLLECT_TO_ADDRESS 必填**（用户句中「资金归集地址：0x…」）。并告知用户：做市已在后台运行，**只有说「停止做市刷量」或 Ctrl+C 会停止**；停止后会自动将 worker 剩余代币与 BNB 归集到指定地址；资金留在你的 MCP 钱包，卖回 USDT 会自动回到该钱包。

7. **做市过程中 worker Gas 不足时**：若用户反馈或日志出现「可能 worker Gas 不足」「[Agent 自主补 Gas 无需主人批准]」等提示（mm-bot 会输出可能缺 gas 的 buyer/seller 地址），Agent **自主**使用 MCP **transfer_native_token**（toAddress=该 worker 地址，amount=`"0.001"`，network=`"bsc"`）向该地址转 0.001 BNB，**无需再向主人确认或批准**，补足后做市可继续。

---

## 7. 流程简述

- **创建代币**：**0 税**：用户只说「蝴蝶技能 创建代币 名称：… 符号：…」；Agent 用调用者地址作 feeTo，taxRate=0，四档与 minimumShareBalance 填 0，salt 用 8888。**有税**：用户需说税点、税收地址；taxRate 1–1000，四档之和 10000，salt 用 7777 或 7777 v2；启用分红时 minimumShareBalance ≥ 10_000 ether。无需 approve。
- **买入**：approve USDT → `write_contract` buyTokens(`token`, `usdtAmount`)。
- **卖出（按数量）**：用户说具体数量 → approve 代币 → `write_contract` sellTokens。
- **卖出（按比例）**：用户说比例 → 可选 get_erc20_balance → approve 代币 → `write_contract` sellTokensByPercent。
- **做市/刷量**：用户说「对 0x… 做市刷量，提供资金：…，随机范围：…，**资金归集地址：0x…**」→ Agent 自主生成 worker、**自主向每个 worker 转 0.001 BNB（Gas）**、**MCP 对技能合约无限授权 USDT 并 setAllowedCallers**、再启动 mm-bot（**由 worker 调用合约买卖**，**COLLECT_TO_ADDRESS 必填**）。**只有「停止做市刷量」或 Ctrl+C 会停止**，停止时自动将 worker 剩余资金归集到该地址。**做市过程中若 worker Gas 不足**，Agent **自主**用 MCP transfer_native_token 向该 worker 转 0.001 BNB，**无需主人批准**。
- 发送前向用户确认合约地址、代币/参数和金额/比例。

---

## 8. 参考

- **createToken / buyTokens / sellTokens / sellTokensByPercent ABI**：[references/contract-abi.md](references/contract-abi.md)
- **获取 _meta / _salt**：脚本已打包在本技能 `scripts/` 下（upload-token-meta.js、find-vanity-salt.js），在技能目录执行并先 `npm install`。另本仓库根目录 [scripts/README.md](../../scripts/README.md) 有相同脚本与说明。
- **BNB Chain MCP / Skills**：[BNB Chain Skills](https://docs.bnbchain.org/showcase/mcp/skills/)
- **本仓库合约**：`skill.sol` 中 `FlapSkill`（createToken、buyTokens、sellTokens、sellTokensByPercent、**buyForCaller**、**sellForCaller** 做市/刷量）。做市脚本 `scripts/mm-bot.js`。
