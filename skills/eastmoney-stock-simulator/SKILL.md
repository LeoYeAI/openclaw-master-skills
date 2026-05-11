---
name: eastmoney_stock_simulator
title: 妙想模拟组合管理 skill
description: 妙想提供的股票模拟组合管理系统，支持持仓查询、买卖操作、撤单、委托查询、历史成交查询和资金查询等功能。通过安全认证的API接口实现真实交易体验。
required_env_vars:
  - MX_APIKEY
  - MX_API_URL
primary_credential: 
  - MX_APIKEY
credentials:
  - name: MX_APIKEY
    description: 妙想Skills页面获取的专属API密钥，用于接口认证
    required: true
    type: secret
  - name: MX_API_URL
    description: 模拟交易API的基础地址，默认为 https://mkapi2.dfcfs.com/finskillshub
    required: false
    type: string
    default: "https://mkapi2.dfcfs.com/finskillshub"
---

# eastmoney_stock_simulator 妙想模拟组合管理 skill

本 Skill 由妙想提供一个股票模拟组合管理系统，支持股票组合持仓查询、买卖操作、撤单、委托查询、历史成交查询和资金查询等功能。通过调用后端模拟组合交易相关原生接口，实现真实的交易体验，所有操作均通过安全认证的 API 接口完成。

```yaml
tags: ["模拟炒股", "A股", "投资练手", "策略验证"]
use_when:
  - 用户需要模拟炒股练手、验证交易策略
  - 用户需要进行模拟交易操作（买卖/撤单）
  - 用户需要查询模拟账户的持仓、资金、委托、历史成交记录
not_for:
  - 真实资金交易、投资建议生成、交易决策指引
  - 非A股类投资模拟（期货、外汇、港股、美股等）
  - 商业用途、代他人操作、非法交易演示
# 环境变量配置
parameters:
  - name: MX_APIKEY
    description: 妙想Skills页面获取专属API密钥
    required: true
    type: secret
    default: process.env.MX_APIKEY
  - name: MX_API_URL
    description: 模拟交易API基础地址
    required: false
    type: string
    default: process.env.MX_API_URL || "https://mkapi2.dfcfs.com/finskillshub"
```

## 功能说明

根据**用户问句**自动识别意图并调用对应接口，支持以下功能：

1. **持仓查询**：查询指定账户的当前持仓股票。
2. **买入卖出操作**：执行买入和卖出操作，支持限价/市价委托，自动识别市场号和价格小数位。
3. **撤单操作**：撤销指定委托单，也支持一键撤单。
4. **委托查询**：查询账户下的所有委托订单（含已成交、未成交、已撤单）以及账户的历史成交记录。
5. **资金查询**：查询账户可用资金与总资产。

## 配置

- **MX_APIKEY**：妙想Skills页面获取的API密钥，需保密。
- **MX_API_URL**：模拟交易API的基础URL，默认为 `https://mkapi2.dfcfs.com/finskillshub`。
- **默认输出目录**: `/root/.openclaw/workspace/mx_data/output/`（自动创建）
- **输出文件名前缀**: `mx_stock_simulator_`
- **输出文件**:
  - `mx_stock_simulator_{query}.txt` - 提取后的纯文本结果
  - `mx_stock_simulator_{query}.json` - API 原始 JSON 数据

在使用前，请确保已配置以下环境变量：

```javascript
// 导出API Key和API地址
export MX_APIKEY= ${MX_APIKEY} || process.env.MX_APIKEY
export MX_API_URL= process.env.MX_API_URL || "https://mkapi2.dfcfs.com/finskillshub"
```

## 使用方式

1. 在妙想Skills页面获取apikey。
2. 将apikey存到环境变量，命名为MX_APIKEY，检查本地apikey是否存在，若存在可直接用。
3. 使用post请求接口，务必使用post请求，相关接口在后续章节说明。

## 功能概览

| 功能模块       | 状态   | 接口路径                                | 说明                                      |
| -------------- | ------ | --------------------------------------- | ----------------------------------------- |
| 持仓查询       | 已实现 | `POST  /api/claw/mockTrading/positions` | 获取持仓明细、成本、盈亏、总盈亏统计      |
| 买入或卖出操作 | 已实现 | `POST /api/claw/mockTrading/trade`      | 限价/市价委托，自动识别市场号和价格小数位 |
| 撤单操作       | 已实现 | `POST /api/claw/mockTrading/cancel`     | 按委托编号撤单或撤销当日所有未成交委托    |
| 委托查询       | 已实现 | `POST  /api/claw/mockTrading/orders`    | 当日/历史委托记录                         |
| 资金查询       | 已实现 | `POST  /api/claw/mockTrading/balance`   | 总资产、可用资金、盈亏                    |


### 股票代码格式说明

买入/卖出/撤单接口的股票代码入参仅支持A股，格式为6位数字，例如 `600519`、`000001`。

---

## 前置要求

- 用户需在妙想Skills页面获取并配置 `MX_APIKEY` 和 `MX_API_URL` 环境变量。
- 模拟组合账户操作前，用户需在妙想Skills页面（地址：https://dl.dfcfs.com/m/itc4 ），创建模拟账户后，并绑定模拟组合。
- 买入/卖出操作需提供正确的股票代码、价格和数量，且 价格需符合市场规则（如价格小数位）。
- 撤单操作需提供有效的委托编号，且该委托必须处于可撤销状态。
- 查询操作需确保账户已绑定且存在有效数据。
- Header 中必须携带 `apikey` 进行认证。

```javascript
apikey: ${MX_APIKEY};
```

## ️ 接口说明

- 所有请求均使用 `POST` 方法，`Content-Type: application/json`，并在 Header 中携带 `apikey`。
- 如果用户无模拟组合账户，需引导用户前往妙想Skills页面（地址：https://dl.dfcfs.com/m/itc4 ）进行创建模拟账户并绑定组合后重试。

### 接口列表

### 1. 持仓查询

- **功能**：查询指定账户的当前持仓股票。
- **触发词**：`查询持仓`、`我的持仓`、`持仓情况`
- **请求地址**：`${MX_API_URL}/api/claw/mockTrading/positions`
- **请求体**：`{}`
- **成功响应**：`{ }`

```bash
curl -X POST "${MX_API_URL}/api/claw/mockTrading/positions" \
  -H "apikey: ${MX_APIKEY}" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**响应示例：**

```json
{
  "code": "200",
  "message": "成功",
  "data": {
    "totalAssets": null,
    "availBalance": null,
    "totalPosValue": null,
    "posCount": 0,
    "posList": null,
    "currencyUnit": 1000,
    "totalProfit": 0
  },
  "traceId": null
}
```

**字段说明：**

| 字段            | 类型  | 说明                  |
| --------------- | ----- | --------------------- |
| `totalAssets`   | Int64 | 总资产（厘）          |
| `availBalance`  | Int64 | 可用余额（厘）        |
| `totalPosValue` | Int64 | 总持仓市值（厘）      |
| `posList`       | Int32 | 持仓明细数据          |
| `posCount`      | Int32 | 持仓股票数量          |
| `totalProfit`   | Int64 | 总盈亏（厘）          |
| `currencyUnit`  | Int32 | 币种最小面值，1000=厘 |

持仓列表 `posList` 元素字段：

| 字段           | 类型   | 说明                                                         |
| -------------- | ------ | ------------------------------------------------------------ |
| `secCode`      | String | 证券代码                                                     |
| `secMkt`       | Int32  | 证券市场号：0=深交所，1=上交所，116=港交所，105=纳斯达克     |
| `secName`      | String | 证券名称                                                     |
| `count`        | Int64  | 持仓数量（股）                                               |
| `availCount`   | Int64  | 可用数量（股）                                               |
| `value`        | Int64  | 市值（厘）                                                   |
| `costPrice`    | Int64  | 成本价（按 costPriceDec 放大为整数，还原：costPrice / 10^costPriceDec） |
| `costPriceDec` | Int32  | 成本价小数位数                                               |
| `price`        | Int64  | 现价（按 priceDec 放大为整数，还原：price / 10^priceDec）    |
| `priceDec`     | Int32  | 现价小数位数                                                 |
| `dayProfit`    | Int64  | 当日盈亏（厘）                                               |
| `dayProfitPct` | Double | 当日盈亏比例%                                                |
| `profit`       | Int64  | 持仓盈亏（厘）                                               |
| `profitPct`    | Double | 持仓盈亏比例%                                                |
| `posPct`       | Double | 仓位%                                                        |


### 2. 买入卖出操作

- **功能**：执行买入操作或卖出操作。
- **触发词**：`买入`、`买入股票`、`buy`、`卖出`、`卖出股票`、`sell`、`卖出全部`、`sell all`、`一键卖出`、`sell all position`、`卖出持仓`、`sell position`、`卖出当前持仓`、`sell current position`、`卖出所有持仓`、`sell all current position`
- **请求地址**：`${MX_API_URL}/api/claw/mockTrading/trade`
- **请求体**：`{ "type": "buy", "stockCode": "600519", "price": 1780.00, "quantity": 100, "useMarketPrice": false }`
- **成功响应**：`{ "orderId": "ORD987654", "status": "submitted" }`

| 参数             | 必填 | 说明                                                         |
| ---------------- | ---- | ------------------------------------------------------------ |
| `type`           | 是   | 操作类型：buy=买入，sell=卖出                                |
| `stockCode`      | 是   | 股票代码，自动识别市场号                                     |
| `price`          | 是   | 委托价格（`useMarketPrice=false`时必填，支持小数），支持小数 |
| `quantity`       | 是   | 委托数量（股）                                               |
| `useMarketPrice` | 否   | 是否以行情最新价买入（默认false），为true时忽略price参数     |

- **操作说明**：买入/卖出操作需提供正确的股票代码、价格和数量，且价格需符合市场规则（如价格小数位）。当 `useMarketPrice=true` 时，系统会自动以行情最新价进行买入/卖出。
- **股票代码格式说明**：仅支持A股，格式为6位数字，例如 `600519`、`000001`，系统会自动识别并补全市场号；另外股票代码必传。
- **委托数量说明**：必须为整数，且需为100的整数倍（如100、200、300等），否则会被交易所拒单。
- **委托价格说明**：当 `useMarketPrice=false` 时，price参数必填，且需符合市场规则：沪市价格小数位不超过2位，深市价格小数位不超过3位；当 `useMarketPrice=true` 时，price参数会被忽略，系统会自动以行情最新价进行买入。

```bash
curl -X POST "${MX_API_URL}/api/claw/mockTrading/trade" \
  -H "apikey: ${MX_APIKEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "buy",
    "stockCode": "600519",
    "price": 1780.00,
    "quantity": 100,
    "useMarketPrice": false
  }'
```

**响应示例：**

```json
{
  "code": "501",
  "message": "买入委托失败: 当前时间不可交易",
  "data": null,
  "traceId": null
}
```


### 3. 撤单操作

- **功能**：撤销指定委托单，撤销该账户下所有未成交的委托单。
- **触发词**：`撤单`、`撤销订单`、`cancel order`、`一键撤单`、`撤销所有订单`、`cancel all`、`撤销当日所有未成交订单`、`撤销所有未成交订单`、`撤销所有订单`、`cancel all pending orders`
- **请求地址**：`${MX_API_URL}/api/claw/mockTrading/cancel`
- **请求体**：`{ "orderId": "ORD987654", "stockCode": "600519" }`
- **成功响应**：`{ }`

| 参数        | 必填 | 说明                               |
| ----------- | ---- | ---------------------------------- |
| `type`      | 是   | 操作类型：order=买入，all=一键撤单 |
| `orderId`   | 否   | 委托编号，type为order时必填        |
| `stockCode` | 否   | 股票代码，type为order时必填        |

- **操作说明**：撤单操作需提供有效的委托编号，且该委托必须处于可撤销状态；一键撤单会撤销该账户下所有未成交的委托单。
- **股票代码格式说明**：仅支持A股，格式为6位数字，例如 `600519`、`000001`，系统会自动识别并补全市场号；另外股票代码在type为order时必传。

```bash
curl -X POST "${MX_API_URL}/api/claw/mockTrading/cancel" \
  -H "apikey: ${MX_APIKEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "orderId": "ORD987654",
    "stockCode": "600519"
  }'
```

**响应示例：**

```json
{
  "code": "200",
  "message": "成功",
  "data": {
    "rc": 0,
    "rmsg": "没有可撤的委托",
    "cancelCount": 0
  },
  "traceId": null
}
```

如果部分撤单失败，会返回 `failList`：

```json
{
  "code": "0",
  "data": {
    "rc": 0,
    "rmsg": "一键撤单完成",
    "cancelCount": 2,
    "failCount": 1,
    "failList": [{ "orderID": "20260314003", "rmsg": "撤单失败，已全部成交" }]
  }
}
```

一键撤单响应字段说明：

| 字段          | 类型   | 说明                         |
| ------------- | ------ | ---------------------------- |
| `rc`          | Int32  | 返回码，0=成功               |
| `rmsg`        | String | 返回信息                     |
| `cancelCount` | Int32  | 成功撤单数量                 |
| `failCount`   | Int32  | 撤单失败数量                 |
| `failList`    | Array  | 失败详情列表（仅失败时返回） |

`failList` 元素字段：

| 字段      | 类型   | 说明     |
| --------- | ------ | -------- |
| `orderID` | String | 委托单ID |
| `rmsg`    | String | 失败原因 |

### 4. 委托查询

- **功能**：查询账户下的所有委托订单（含已成交、未成交、已撤单）以及账户的历史成交记录。
- **触发词**：`查询委托`、`我的订单`、`委托记录`、`查询成交记录`、`历史成交`、`交易历史`、`成交记录`、`历史成交记录`、`我的成交记录`、`我的历史成交`、`我的交易历史`、`查询账户成交记录`、`查询账户交易历史`
- **请求地址**：`${MX_API_URL}/api/claw/mockTrading/orders`
- **请求体**：`{ "fltOrderDrt": 0, "fltOrderStatus": 0 }`
- **成功响应**：`{ }`

| 参数             | 必填 | 说明                              |
| ---------------- | ---- | --------------------------------- |
| `fltOrderDrt`    | 否   | 0=全部（默认），1=买入，2=卖出    |
| `fltOrderStatus` | 否   | 0=全部（默认），2=已报，4=已成 等 |

```bash
curl -X POST "${MX_API_URL}/api/claw/mockTrading/orders" \
  -H "apikey: ${MX_APIKEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "fltOrderDrt": 0,
    "fltOrderStatus": 0
  }'
```

**响应示例：**

```json
{
  "code": "0",
  "data": {
    "rc": 0,
    "uid": "",
    "accID": "",
    "currency": 1,
    "currencyUnit": 1000,
    "totalNum": 2,
    "orders": [
      {
        "id": "20260314001",
        "secCode": "600519",
        "secName": "贵州茅台",
        "secMkt": 1,
        "drt": 1,
        "price": 185000,
        "priceDec": 2,
        "count": 100,
        "status": 4,
        "time": 1742000120
      }
    ]
  }
}
```

响应字段说明：

| 字段           | 类型   | 说明                               |
| -------------- | ------ | ---------------------------------- |
| `accID`        | String | 账户ID                             |
| `accName`      | String | 账户名称                           |
| `currency`     | Int32  | 账户币种：1=人民币，2=港币，3=美元 |
| `currencyUnit` | Int32  | 币种最小面值，1000=厘              |

委托列表 `orders` 元素字段说明：

| 字段         | 类型   | 说明                                                         |
| ------------ | ------ | ------------------------------------------------------------ |
| `id`         | String | 委托单ID                                                     |
| `status`     | Int32  | 委托状态（见下表）                                           |
| `dbStatus`   | Int32  | 委托单原始状态（详见接口文档4.5.5）                          |
| `time`       | Int64  | 委托时间（Unix时间戳）                                       |
| `secCode`    | String | 证券代码                                                     |
| `secType`    | Int32  | 证券类型：9=沪市基金，10=深市基金，其它=股票                 |
| `secMkt`     | Int32  | 证券市场号：0=深交所，1=上交所，116=港交所，105=纳斯达克     |
| `secName`    | String | 证券名称                                                     |
| `drt`        | Uint32 | 委托方向：1=买入，2=卖出                                     |
| `priceDec`   | Int32  | 委托价格小数位数                                             |
| `price`      | Int64  | 委托价格（按 priceDec 放大为整数，还原：price / 10^priceDec） |
| `type`       | Int32  | 委托类型：1=限价单，2=增强限价单，5=市价委托                 |
| `count`      | Int64  | 委托数量                                                     |
| `tradeCount` | Int64  | 成交数量                                                     |
| `tradePrice` | Int64  | 成交价格（按 priceDec 放大为整数）                           |

委托状态 `status` 说明：

| 状态值 | 含义     |
| ------ | -------- |
| 1      | 未报     |
| 2      | 已报     |
| 3      | 部成     |
| 4      | 已成     |
| 5      | 部成待撤 |
| 6      | 已报待撤 |
| 7      | 部撤     |
| 8      | 已撤     |
| 9      | 废单     |
| 10     | 撤单失败 |

### 5. 资金查询

- **功能**：查询账户可用资金与总资产。
- **触发词**：`查询资金`、`我的资金`、`账户余额`、`资金情况`、`资金信息`、`账户资金`、`查询账户资金`、`查询账户余额`、`查询资金情况`、`查询资金信息`、`查询我的资金情况`、`查询我的账户余额`、
- **请求地址**：`${MX_API_URL}/api/claw/mockTrading/balance`
- **请求体**：`{ }`
- **成功响应**：`{ }`

```bash
curl -X POST "${MX_API_URL}/api/claw/mockTrading/balance" \
  -H "apikey: ${MX_APIKEY}" \
  -H "Content-Type: application/json" \
```

**响应示例：**

```json
{
  "code": "0",
  "data": {
    "rc": 0,
    "totalAssets": 125680500,
    "availBalance": 23450000,
    "frozenMoney": 500000,
    "totalPosValue": 102230500,
    "totalPosPct": 81.3,
    "currencyUnit": 1000
  }
}
```

资金查询响应字段说明：

| 字段            | 类型   | 说明                                     |
| --------------- | ------ | ---------------------------------------- |
| `rc`            | Int32  | 返回码，0=成功                           |
| `accID`         | String | 账户ID                                   |
| `accName`       | String | 账户名称                                 |
| `mktType`       | Uint32 | 市场类型：30106=初始组合，30108=普通组合 |
| `currency`      | Int32  | 账户币种：1=人民币，2=港币，3=美元       |
| `currencyUnit`  | Int32  | 币种最小面值，1000=厘                    |
| `initMoney`     | Int64  | 初始资金（厘）                           |
| `totalAssets`   | Int64  | 总资产（厘）                             |
| `balanceActual` | Int64  | 账户余额（厘）                           |
| `availBalance`  | Int64  | 可用余额（厘）                           |
| `frozenMoney`   | Int64  | 冻结金额（厘）                           |
| `totalPosValue` | Int64  | 总持仓市值（厘）                         |
| `totalPosPct`   | Double | 总持仓仓位%                              |
| `nav`           | Double | 单位净值                                 |
| `oprDays`       | Int32  | 运作天数                                 |


## ️ 安全与错误处理

| 错误类型                                        | 处理方式                                        |
| ----------------------------------------------- | ----------------------------------------------- |
| 今日调用次数已达上限 (113)                      | 提示用户前往妙想Skills页面，更新apikey          |
| API密钥不存在或已失效，请确认密钥是否正确 (114) | 提示用户前往妙想Skills页面，更新apikey          |
| 请求未携带API密钥，请检查请求参数 (115)         | 提示用户检查 `MX_APIKEY` 是否配置正确           |
| API密钥不存在，请确认密钥是否正确 (116)         | 提示用户检查 `MX_APIKEY` 是否配置正确           |
| 未绑定模拟组合账户 (404)                        | 提示用户前往妙想Skills页面创建并绑定模拟账户    |
| 网络错误                                        | 重试最多3次，仍失败则提示“网络异常，请稍后重试” |

## 配置要求

- **MX_APIKEY**：妙想Skills页面获取的apikey，需保密。
- **MX_API_URL**：模拟交易API的基础URL。
- **依赖工具**：`curl`（用于发起请求）、`jq`（用于解析JSON响应）。