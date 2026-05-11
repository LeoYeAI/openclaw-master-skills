# 蝴蝶技能 createToken / buyTokens / sellTokens — ABI 与调用示例

**合约地址**：`0x482970490d06fc3a480bfd0e9e58141667cffedc`。  
**USDT（BSC）**：`0x55d398326f99059fF775485246999027B3197955`。

---

## createToken 函数 ABI（创建 V5 代币）

```json
[
  {
    "inputs": [
      { "internalType": "string", "name": "_name", "type": "string" },
      { "internalType": "string", "name": "_symbol", "type": "string" },
      { "internalType": "string", "name": "_meta", "type": "string" },
      { "internalType": "address", "name": "_feeTo", "type": "address" },
      { "internalType": "bytes32", "name": "_salt", "type": "bytes32" },
      { "internalType": "uint16", "name": "_taxRate", "type": "uint16" },
      { "internalType": "uint16", "name": "_mktBps", "type": "uint16" },
      { "internalType": "uint16", "name": "_dividendBps", "type": "uint16" },
      { "internalType": "uint16", "name": "_deflationBps", "type": "uint16" },
      { "internalType": "uint16", "name": "_lpBps", "type": "uint16" },
      { "internalType": "uint256", "name": "_minimumShareBalance", "type": "uint256" }
    ],
    "name": "createToken",
    "outputs": [{ "internalType": "address", "name": "token", "type": "address" }],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]
```

**调用**：直接 `write_contract`，`functionName`: `"createToken"`，`args`: `[name, symbol, meta, feeTo, salt, taxRate, mktBps, dividendBps, deflationBps, lpBps, minimumShareBalance]`。**0 税代币**：taxRate=0，mktBps/dividendBps/deflationBps/lpBps/minimumShareBalance 均填 0；salt 须用尾号 8888（`find-vanity-salt.js 8888`）。**税收代币**：taxRate 1–1000（100=1%，300=3%）；mktBps、dividendBps、deflationBps、lpBps 四者之和须为 10000；salt 须用尾号 7777（全营销用 7777，四档用 7777 v2）；启用分红时 minimumShareBalance ≥ 10_000 ether（如 `"10000000000000000000000"`），否则 0。salt 为 bytes32（0x+64 位十六进制）。详见 Flap [Portal](https://docs.flap.sh/flap/developers/token-launcher-developers/launch-token-through-portal)、[部署地址](https://docs.flap.sh/flap/developers/token-launcher-developers/deployed-contract-addresses)。

---

## buyTokens 函数 ABI

```json
[
  {
    "inputs": [
      { "internalType": "address", "name": "_token", "type": "address" },
      { "internalType": "uint256", "name": "_usdtAmount", "type": "uint256" }
    ],
    "name": "buyTokens",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]
```

**调用**：先 `approve_token_spending`（token=USDT，spender=FlapSkill，amount=本次 USDT）；再 `write_contract`，`functionName`: `"buyTokens"`，`args`: `[目标代币地址, usdtAmount最小单位]`。例：10 USDT = `"10000000000000000000"`。

---

## sellTokens 函数 ABI

```json
[
  {
    "inputs": [
      { "internalType": "address", "name": "_token", "type": "address" },
      { "internalType": "uint256", "name": "_tokenAmount", "type": "uint256" }
    ],
    "name": "sellTokens",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]
```

**调用**：先 `approve_token_spending`（token=要卖出的代币，spender=FlapSkill，amount=本次卖出数量）；再 `write_contract`，`functionName`: `"sellTokens"`，`args`: `[代币地址, tokenAmount最小单位]`。`_tokenAmount` 须按该代币 decimals 换算（如 18 位小数，1 个 = `"1000000000000000000"`）。无滑点保护。USDT 直接转给调用者，无返回值。用于**按具体数量**卖出。

---

## sellTokensByPercent 函数 ABI（按仓位比例卖出）

```json
[
  {
    "inputs": [
      { "internalType": "address", "name": "_token", "type": "address" },
      { "internalType": "uint256", "name": "_percentBps", "type": "uint256" }
    ],
    "name": "sellTokensByPercent",
    "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]
```

**调用**：先 `approve_token_spending`（token=要卖出的代币，spender=FlapSkill，amount 建议≥比例对应数量或全部仓位）；再 `write_contract`，`functionName`: `"sellTokensByPercent"`，`args`: `[代币地址, percentBps]`。`_percentBps` 为基点：10000=100%，5000=50%，1000=10%。合约按用户当前持仓 × percentBps/10000 计算卖出数量。无滑点保护。用于**按仓位比例/百分比**卖出。

---

## buyForCaller 函数 ABI（做市/刷量：用 funder 的 USDT 买入，代币给调用者）

```json
[
  {
    "inputs": [
      { "internalType": "address", "name": "_token", "type": "address" },
      { "internalType": "uint256", "name": "_usdtAmount", "type": "uint256" },
      { "internalType": "address", "name": "_funder", "type": "address" }
    ],
    "name": "buyForCaller",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]
```

**调用**：仅当 `allowedCallers[_funder][_token][msg.sender] == true` 时可调用（funder 须已对该 token 调用 `setAllowedCallers` 登记调用地址）。`_funder` 须已对 FlapSkill approve USDT。用于区分「小明对 0x0123 刷量」「小红对 0x456 刷量」等不同会话。

---

## sellForCaller 函数 ABI（做市/刷量：调用者交出代币卖出，USDT 给 funder）

```json
[
  {
    "inputs": [
      { "internalType": "address", "name": "_token", "type": "address" },
      { "internalType": "uint256", "name": "_tokenAmount", "type": "uint256" },
      { "internalType": "address", "name": "_funder", "type": "address" }
    ],
    "name": "sellForCaller",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]
```

**调用**：仅当 `allowedCallers[_funder][_token][msg.sender] == true` 时可调用。调用者须先对 FlapSkill approve 代币。所得 USDT 转给 `_funder`。

---

## setAllowedCallers 函数 ABI（做市：登记该 token 下允许调用 buyForCaller/sellForCaller 的地址）

```json
[
  {
    "inputs": [
      { "internalType": "address", "name": "_token", "type": "address" },
      { "internalType": "address[]", "name": "_callers", "type": "address[]" }
    ],
    "name": "setAllowedCallers",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]
```

**调用**：由 **funder（资金方）** 调用，`msg.sender` 即 funder。登记对该 `_token` 允许调用 buyForCaller/sellForCaller 的地址列表（做市脚本使用的 PRIVATE_KEYS 对应地址）。小明对 0x0123 刷量前，小明钱包调用 `setAllowedCallers(0x0123, [小明用的 worker 地址...])`；小红对 0x456 刷量前，小红钱包调用 `setAllowedCallers(0x456, [小红用的 worker 地址...])`，从而区分不同人、不同代币的会话。

---

## removeAllowedCallers 函数 ABI（取消某 token 下部分地址的调用权限）

```json
[
  {
    "inputs": [
      { "internalType": "address", "name": "_token", "type": "address" },
      { "internalType": "address[]", "name": "_callers", "type": "address[]" }
    ],
    "name": "removeAllowedCallers",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]
```

**调用**：由 funder 调用，取消上述地址对该 token 的调用权限。


