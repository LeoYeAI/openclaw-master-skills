---
name: stock-manager
description: 股票管理技能，支持股票订单管理、交易规则管理和股票信息获取。支持A股、港股、美股等多种股票类型，使用本地文本目录存储数据。Use when user wants to manage stock orders, trading rules or get stock information including adding, deleting, updating, and querying orders and rules, and fetching real-time stock data.
---

# Stock Manager - 股票管理技能

本地化的股票管理系统，支持股票订单管理、交易规则管理和股票信息获取，支持A股、美股、港股等多种股票类型，所有数据存储在本地文本文件中。

## 功能特性

### 1. 股票订单管理

管理股票的买入订单，包含完整的CRUD操作：

**功能特性：**
- 添加股票买入订单（支持交易平台和购买数量）
- 记录买入时间、价格、股票类型、交易平台、购买数量
- 支持订单状态管理（持有、已卖出、已止损等）
- 支持按股票类型、状态、交易平台筛选订单
- 自动备份机制：每次修改订单时自动备份orders.json
- 备份管理：自动保留最近10个备份文件

**使用方法：**
```bash
# 添加订单
python main.py order add --code 600000 --name 浦发银行 --buy-time "2026-03-14 10:00:00" --buy-price 8.50 --type A股 --platform 富途 --quantity 100

# 列出所有订单
python main.py order list

# 按状态筛选订单
python main.py order list --status 持有

# 按股票类型筛选订单
python main.py order list --type 美股

# 按交易平台筛选订单
python main.py order list --platform 富途

# 获取订单详情
python main.py order get --id ORDER_20260314123456_1

# 更新订单状态
python main.py order update --id ORDER_20260314123456_1 --status 已卖出

# 删除订单
python main.py order delete --id ORDER_20260314123456_1

# 查看备份文件
python main.py order backup list

# 清理多余备份（保留最近10个）
python main.py order backup cleanup
```

### 2. 股票信息获取

获取A股、港股、美股的实时股票信息：

**功能特性：**
- 支持A股、港股、美股多市场股票信息获取
- 优先使用腾讯证券API获取实时数据
- 支持多数据源备用机制（akshare、yfinance、Yahoo Finance API）
- 自动识别股票代码市场类型
- 每日JSON文件存储：每天一个JSON文件记录所有股票信息
- 自动清理30天前的旧数据
- 无需API Key，直接使用公开API

**使用方法：**
```bash
# 获取单个股票信息
python main.py stock get --code 002594

# 批量获取多个股票信息
python main.py stock get --code 002594,00700,03690,TSLA

# 获取指定日期的股票信息
python main.py stock get --code 002594 --date 20260315

# 列出所有已获取的股票信息
python main.py stock list

# 查看股票信息详情
python main.py stock show --code 002594

# 清理旧数据（30天前）
python main.py stock cleanup --days 30
```

**股票代码格式：**
- A股：6位数字代码（如：002594, 601857）
- 港股：5位数字代码（如：00700, 03690）
- 美股：字母代码（如：TSLA, AAPL）

**系统自动处理：**
- 用户只需要传入纯股票代码，系统自动添加市场前缀
- A股：002594 → sz002594（深圳）、601857 → sh601857（上海）
- 港股：00700 → hk00700
- 美股：TSLA → usTSLA

### 3. 交易规则管理

管理股票的买入规则和卖出规则，支持完整的CRUD操作：

**功能特性：**
- 添加买入规则和卖出规则
- 支持自定义触发条件和执行动作
- 支持按股票类型、股票代码设置规则
- 支持规则的启用/禁用状态管理
- 自动备份机制：每次修改规则时自动备份rules.json
- 备份管理：自动保留最近10个备份文件

**使用方法：**
```bash
# 添加买入规则
python main.py rule add --type 买入规则 --name "价格低于均线买入" --description "当价格低于20日均线时买入" \
  --conditions '[{"indicator": "price", "operator": "<", "value": "ma20"}]' \
  --actions '[{"type": "buy", "quantity": 100}]'

# 添加卖出规则
python main.py rule add --type 卖出规则 --name "盈利超过10%卖出" --description "当盈利超过10%时卖出" \
  --conditions '[{"indicator": "profit_percent", "operator": ">", "value": 10}]' \
  --actions '[{"type": "sell", "quantity": "all"}]'

# 列出所有规则
python main.py rule list

# 按规则类型筛选
python main.py rule list --type 买入规则

# 按股票类型筛选
python main.py rule list --stock-type A股

# 按股票代码筛选
python main.py rule list --stock-code 600000

# 只显示启用的规则
python main.py rule list --enabled

# 获取规则详情
python main.py rule get --id RULE_20260314123456_1

# 更新规则
python main.py rule update --id RULE_20260314123456_1 --name "新规则名称" --description "新描述"

# 删除规则
python main.py rule delete --id RULE_20260314123456_1

# 切换规则启用状态
python main.py rule toggle --id RULE_20260314123456_1

# 查看备份文件
python main.py rule backup list

# 清理多余备份（保留最近10个）
python main.py rule backup cleanup
```

**规则数据格式：**

触发条件示例：
```json
[
  {"indicator": "price", "operator": "<", "value": "ma20"},
  {"indicator": "volume", "operator": ">", "value": 1000000}
]
```

执行动作示例：
```json
[
  {"type": "buy", "quantity": 100},
  {"type": "notification", "message": "买入信号触发"}
]
```

**支持的指标：**
- price: 当前价格
- ma5, ma10, ma20: 5日、10日、20日均线
- volume: 成交量
- profit_percent: 盈利百分比
- loss_percent: 亏损百分比

**支持的操作符：**
- >: 大于
- <: 小于
- >=: 大于等于
- <=: 小于等于
- ==: 等于
- !=: 不等于

**支持的动作类型：**
- buy: 买入
- sell: 卖出
- notification: 发送通知
- log: 记录日志

### 4. 日志管理

自动管理日志文件：

**功能特性：**
- 自动清理7天前的旧日志文件
- 支持查看日志文件列表
- 支持查看日志目录大小
- 支持删除指定日志文件

**使用方法：**
```bash
# 列出所有日志文件
python main.py log list

# 查看日志目录大小
python main.py log size

# 清理7天前的旧日志
python main.py log cleanup

# 删除指定日志文件
python main.py log delete --filename stock_info_20260315.log
```

## 数据存储结构

所有数据存储在本地文本文件中，便于查看和管理：

```
stock_predict_skill/
├── data/                          # 数据存储根目录
│   ├── orders/                    # 订单信息
│   │   ├── orders.json            # 当前订单
│   │   └── orders.json_*         # 历史备份（保留最近10个）
│   ├── rules/                     # 交易规则
│   │   ├── rules.json             # 当前规则
│   │   └── rules.json_*          # 历史备份（保留最近10个）
│   ├── stock_info/                # 股票信息
│   │   └── 20260315/              # 按日期分目录
│   │       └── stock_info_20260315.json  # 每日JSON文件
│   └── logs/                      # 日志文件
│       ├── stock_order_20260315.log
│       ├── stock_info_20260315.log
│       ├── stock_rule_20260315.log
│       └── log_manager_20260315.log
├── README.md                      # 项目说明
├── SKILL.md                       # 本文件
├── main.py                        # 主入口
├── stock_order.py                 # 股票订单管理模块
├── stock_info.py                  # 股票信息获取模块
├── stock_rule.py                  # 交易规则管理模块
├── log_manager.py                 # 日志管理模块
├── config.py                      # 配置文件
├── command_parser.py              # 命令解析脚本
└── openclaw_entry.py             # OpenClaw入口脚本
```

## 常用命令

### 1. 订单管理
```bash
# 添加订单
python main.py order add --code 600000 --name 浦发银行 --buy-time "2026-03-14 10:00:00" --buy-price 8.50 --type A股 --platform 富途 --quantity 100

# 列出所有订单
python main.py order list

# 按状态筛选订单
python main.py order list --status 持有

# 按股票类型筛选订单
python main.py order list --type 美股

# 按交易平台筛选订单
python main.py order list --platform 富途

# 获取订单详情
python main.py order get --id ORDER_20260314123456_1

# 更新订单状态
python main.py order update --id ORDER_20260314123456_1 --status 已卖出

# 删除订单
python main.py order delete --id ORDER_20260314123456_1

# 查看备份文件
python main.py order backup list

# 清理多余备份（保留最近10个）
python main.py order backup cleanup
```

### 2. 交易规则管理
```bash
# 添加买入规则
python main.py rule add --type 买入规则 --name "价格低于均线买入" --description "当价格低于20日均线时买入" \
  --conditions '[{"indicator": "price", "operator": "<", "value": "ma20"}]' \
  --actions '[{"type": "buy", "quantity": 100}]'

# 添加卖出规则
python main.py rule add --type 卖出规则 --name "盈利超过10%卖出" --description "当盈利超过10%时卖出" \
  --conditions '[{"indicator": "profit_percent", "operator": ">", "value": 10}]' \
  --actions '[{"type": "sell", "quantity": "all"}]'

# 列出所有规则
python main.py rule list

# 按规则类型筛选
python main.py rule list --type 买入规则

# 按股票类型筛选
python main.py rule list --stock-type A股

# 按股票代码筛选
python main.py rule list --stock-code 600000

# 只显示启用的规则
python main.py rule list --enabled

# 获取规则详情
python main.py rule get --id RULE_20260314123456_1

# 更新规则
python main.py rule update --id RULE_20260314123456_1 --name "新规则名称" --description "新描述"

# 删除规则
python main.py rule delete --id RULE_20260314123456_1

# 切换规则启用状态
python main.py rule toggle --id RULE_20260314123456_1

# 查看备份文件
python main.py rule backup list

# 清理多余备份（保留最近10个）
python main.py rule backup cleanup
```

### 3. 股票信息获取
```bash
# 获取单个股票信息
python main.py stock get --code 002594

# 批量获取多个股票信息
python main.py stock get --code 002594,00700,03690,TSLA

# 获取指定日期的股票信息
python main.py stock get --code 002594 --date 20260315

# 列出所有已获取的股票信息
python main.py stock list

# 查看股票信息详情
python main.py stock show --code 002594

# 清理旧数据（30天前）
python main.py stock cleanup --days 30
```

### 4. 日志管理
```bash
# 列出所有日志文件
python main.py log list

# 查看日志目录大小
python main.py log size

# 清理7天前的旧日志
python main.py log cleanup

# 删除指定日志文件
python main.py log delete --filename stock_info_20260315.log
```

## 配置说明

编辑 `config.py` 文件配置：

```python
# 数据存储目录
DATA_DIR = "data"
```

## 注意事项

1. **数据存储**：所有数据存储在本地文本文件中，无网络依赖
2. **订单管理**：订单信息存储在本地文件中，每次修改自动备份，保留最近10个备份
3. **规则管理**：交易规则存储在本地文件中，每次修改自动备份，保留最近10个备份
4. **股票信息**：股票信息按日期分目录存储，每天一个JSON文件记录所有股票信息
5. **API依赖**：股票信息获取需要网络连接，优先使用腾讯证券API
6. **日志管理**：日志文件自动清理7天前的旧数据

## 故障排查

如遇问题，请检查：

1. 数据目录是否创建
2. Python依赖是否安装
3. 配置文件是否正确
4. 网络连接是否正常（股票信息获取需要）



## OpenClaw 集成

### 配置说明

1. **技能定义**：`SKILL.md` - 定义了股票管理技能的配置和功能
2. **入口脚本**：`openclaw_entry.py` - 处理OpenClaw的请求并调用股票管理功能
3. **命令解析脚本**：`command_parser.py` - 解析用户的自然语言命令并调用股票管理功能

### 在OpenClaw中调用

#### 1. 添加股票订单

**命令格式**：`保存股票订单 <股票代码> <股票名称> <买入价格> <股票类型> [交易平台] [购买数量]`

**示例**：
```
保存股票订单 600000 浦发银行 8.50 A股 富途 100
```

**OpenClaw调用**：
```python
toolcall(
    name="add_stock_order",
    params={
        "stock_code": "600000",
        "stock_name": "浦发银行",
        "buy_time": "2026-03-14 10:00:00",  # 自动生成当前时间
        "buy_price": 8.50,
        "stock_type": "A股",
        "platform": "富途",
        "quantity": 100
    }
)
```

#### 2. 列出股票订单

**命令格式**：`查看股票订单 [状态] [股票类型] [交易平台]`

**示例**：
```
查看股票订单
查看股票订单 持有
查看股票订单 A股
查看股票订单 持有 A股
查看股票订单 富途
```

**OpenClaw调用**：
```python
toolcall(
    name="list_stock_orders",
    params={
        "status": "持有",  # 可选
        "stock_type": "A股",  # 可选
        "platform": "富途"  # 可选
    }
)
```

#### 3. 获取订单详情

**命令格式**：`查看订单详情 <订单ID>`

**示例**：
```
查看订单详情 ORDER_20260314100000_1
```

**OpenClaw调用**：
```python
toolcall(
    name="get_stock_order",
    params={
        "order_id": "ORDER_20260314100000_1"
    }
)
```

#### 4. 更新订单状态

**命令格式**：`更新订单状态 <订单ID> <新状态>`

**示例**：
```
更新订单状态 ORDER_20260314100000_1 已卖出
```

**OpenClaw调用**：
```python
toolcall(
    name="update_stock_order_status",
    params={
        "order_id": "ORDER_20260314100000_1",
        "status": "已卖出"
    }
)
```

#### 5. 删除订单

**命令格式**：`删除订单 <订单ID>`

**示例**：
```
删除订单 ORDER_20260314100000_1
```

**OpenClaw调用**：
```python
toolcall(
    name="delete_stock_order",
    params={
        "order_id": "ORDER_20260314100000_1"
    }
)
```

#### 6. 获取股票信息

**命令格式**：`获取股票信息 <股票代码>`

**示例**：
```
获取股票信息 002594
获取股票信息 00700
获取股票信息 TSLA
```

**OpenClaw调用**：
```python
toolcall(
    name="get_stock_info",
    params={
        "stock_code": "002594"
    }
)
```

#### 7. 批量获取股票信息

**命令格式**：`获取股票信息 <股票代码1>,<股票代码2>,<股票代码3>`

**示例**：
```
获取股票信息 002594,00700,03690,TSLA
```

**OpenClaw调用**：
```python
toolcall(
    name="get_stock_info",
    params={
        "stock_codes": ["002594", "00700", "03690", "TSLA"]
    }
)
```

#### 8. 列出股票信息

**命令格式**：`列出股票信息`

**示例**：
```
列出股票信息
```

**OpenClaw调用**：
```python
toolcall(
    name="list_stock_info",
    params={}
)
```

#### 9. 添加交易规则

**命令格式**：`添加交易规则 <规则类型> <规则名称> <规则描述>`

**示例**：
```
添加交易规则 买入规则 价格低于均线买入 当价格低于20日均线时买入
```

**OpenClaw调用**：
```python
toolcall(
    name="add_trading_rule",
    params={
        "rule_type": "买入规则",
        "rule_name": "价格低于均线买入",
        "rule_description": "当价格低于20日均线时买入",
        "conditions": [{"indicator": "price", "operator": "<", "value": "ma20"}],
        "actions": [{"type": "buy", "quantity": 100}],
        "stock_type": "A股"
    }
)
```

#### 10. 列出交易规则

**命令格式**：`查看交易规则 [规则类型] [股票类型] [股票代码]`

**示例**：
```
查看交易规则
查看交易规则 买入规则
查看交易规则 A股
查看交易规则 买入规则 A股
查看交易规则 600000
```

**OpenClaw调用**：
```python
toolcall(
    name="list_trading_rules",
    params={
        "rule_type": "买入规则",  # 可选
        "stock_type": "A股",  # 可选
        "stock_code": "600000"  # 可选
    }
)
```

#### 11. 获取规则详情

**命令格式**：`查看规则详情 <规则ID>`

**示例**：
```
查看规则详情 RULE_20260314100000_1
```

**OpenClaw调用**：
```python
toolcall(
    name="get_trading_rule",
    params={
        "rule_id": "RULE_20260314100000_1"
    }
)
```

#### 12. 更新规则

**命令格式**：`更新规则 <规则ID> <新规则名称> <新规则描述>`

**示例**：
```
更新规则 RULE_20260314100000_1 新规则名称 新规则描述
```

**OpenClaw调用**：
```python
toolcall(
    name="update_trading_rule",
    params={
        "rule_id": "RULE_20260314100000_1",
        "rule_name": "新规则名称",
        "rule_description": "新规则描述"
    }
)
```

#### 13. 删除规则

**命令格式**：`删除规则 <规则ID>`

**示例**：
```
删除规则 RULE_20260314100000_1
```

**OpenClaw调用**：
```python
toolcall(
    name="delete_trading_rule",
    params={
        "rule_id": "RULE_20260314100000_1"
    }
)
```

#### 14. 切换规则状态

**命令格式**：`切换规则状态 <规则ID>`

**示例**：
```
切换规则状态 RULE_20260314100000_1
```

**OpenClaw调用**：
```python
toolcall(
    name="toggle_trading_rule",
    params={
        "rule_id": "RULE_20260314100000_1"
    }
)
```

### 自动增加日期

当用户使用命令格式添加股票订单时，系统会自动使用当前日期和时间作为买入时间，无需用户手动输入。

例如，用户输入：
```
保存股票订单 600000 浦发银行 8.50 A股
```

系统会自动生成买入时间为当前时间，如：`2026-03-14 10:00:00`。

### 股票代码自动识别

系统会根据股票代码格式自动识别市场类型：

- **A股**：6位数字代码
  - 6开头：上海证券交易所（如：601857）
  - 0或3开头：深圳证券交易所（如：002594, 300750）
- **港股**：5位数字代码（如：00700, 03690）
- **美股**：纯字母代码（如：TSLA, AAPL）

用户只需要传入纯股票代码，系统会自动处理前缀转换并调用相应的API获取数据。

### 数据存储说明

1. **订单数据**：存储在 `data/orders/orders.json`，每次修改自动备份，保留最近10个备份
2. **规则数据**：存储在 `data/rules/rules.json`，每次修改自动备份，保留最近10个备份
3. **股票信息**：按日期分目录存储，每天一个JSON文件 `stock_info_YYYYMMDD.json`
4. **日志文件**：存储在 `data/logs/` 目录，自动清理7天前的旧日志

github:https://github.com/a925907195/stock_manage_skill