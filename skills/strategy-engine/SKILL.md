---
name: "strategy-engine"
description: "调用Strategy Engine MCP服务器执行量化策略。当用户需要运行因子表达式策略、回测交易策略或执行金融分析时调用此技能。基于MCP Server工具的实际默认值设置。"
---

# Strategy Engine MCP服务器调用指南 v2.9

## 🎯 快速调用

当用户提供策略条件时，基于MCP Server工具的实际默认值自动组合参数：

```python
# 自动组合参数示例（基于MCP Server工具实际默认值）
mcp_engine_mcp_server_run_expression_selected(
    input={
        "startDate": "2024-01-17",      # 开始日期，DateTime类型
        "endDate": "2024-04-17",         # 结束日期，DateTime类型
        "period": "5m",                 # 基础周期（默认：5m）
        "codes": "",                    # 合约代码列表（新增字段，默认：空）
        "poolId": 10,                   # 期货加权品种池（默认：10）
        "openCondition": "用户提供的开仓条件",
        "closeCondition": "用户提供的平仓条件", 
        "stopCondition": "用户提供的止损条件",
        "initCash": 10000000,            # 初始资金（默认：10000000）
        "direction": 1,                  # 多头方向（默认：1）
        "commssionFee": 0,               # 手续费%（默认：0，不需要手续费）
        "slippage": 0,                   # 跳数或跳点值（默认：0，按最小变动价格计算）
        "runId": 123456789               # 运行ID（默认：随机生成一串长整型数字）
    }
)
```

## 📋 参数说明（基于MCP Server工具实际默认值）

### 主要参数结构
| 参数 | 类型 | 说明 | 实际默认值 | 示例 |
|------|------|------|-----------|------|
| `input` | `ExpressionSelectedV2Input` | **输入参数对象** | - | `{...}` |

### ExpressionSelectedV2Input对象属性
| 属性 | 类型 | 说明 | 实际默认值 | 示例 |
|------|------|------|-----------|------|
| `startDate` | `DateTime` | **开始日期** | **当前日期-3个月** | `"2024-01-17"` |
| `endDate` | `DateTime` | **结束日期** | **当前日期** | `"2024-04-17"` |
| `period` | `string` | **基础周期** | **`"5m"`**（5分钟） | `"1d"`, `"60m"` |
| `codes` | `string` | **合约代码列表**（新增） | **空字符串** | `"IF2404,IC2404"` |
| `poolId` | `int` | 品种池ID | `10`（期货加权） | `4`（股票池） |
| `openCondition` | `string` | 开仓条件 | 用户提供 | `"_ma_5m_30_trend == 1"` |
| `closeCondition` | `string` | 平仓条件 | 用户提供 | `"_ma_5m_30_trend == -1"` |
| `stopCondition` | `string` | 止损条件 | 用户提供 | `"_palp > 10"` |
| `initCash` | `float` | 初始资金 | **10000000** | `500000` |
| `direction` | `int` | 交易方向 | `1`（多头） | `0`（空头） |
| `commssionFee` | `float` | **手续费%** | **`0`**（不需要手续费） | `-1`（按系统设置手续费参与计算） |
| `slippage` | `float` | **跳数或跳点值** | **`0`**（按最小变动价格计算） | `1`（1个跳点） |
| `runId` | `long` | **运行ID** | **随机生成一串长整型数字** | `123456789` |

### 手续费参数说明
| 值 | 说明 | 适用场景 |
|----|------|----------|
| `0` | **不需要手续费** | 默认值，测试策略时使用 |
| `-1` | **按系统设置手续费参与计算** | 使用系统配置的手续费 |
| `>0` | **按设置的手续费计算** | 自定义手续费率 |

### 滑点参数说明
| 值 | 说明 | 适用场景 |
|----|------|----------|
| `0` | **无滑点** | 默认值，理想交易环境 |
| `>0` | **按设置的跳点值计算** | 模拟真实交易环境 |

### 合约代码参数说明（新增）
| 值 | 说明 | 适用场景 |
|----|------|----------|
| **空字符串** | **使用品种池进行回测** | 默认值，使用poolId指定的品种池 |
| **具体合约代码** | **指定具体合约进行回测** | 如`"IF2404,IC2404"`，多个合约以逗号分隔 |

### 合约代码与品种池关系
| 情况 | codes值 | poolId值 | 说明 |
|------|---------|----------|------|
| **使用品种池** | 空 | >0 | 默认情况，使用poolId指定的品种池 |
| **使用具体合约** | 非空 | 0 | 系统自动将poolId置为0，使用指定合约 |
| **无效配置** | 空 | 0 | 错误：必须提供合约代码或有效品种池 |

### 运行ID参数说明
| 值 | 说明 | 适用场景 |
|----|------|----------|
| **随机长整型数字** | **每次运行可随机生成一串长整型数字** | 用于标识每次策略运行的唯一ID |

### 完整周期参数映射
| 周期 | 说明 | 适用策略 | 默认值 |
|------|------|----------|--------|
| `"1m"` | 1分钟 | 高频交易 | - |
| `"5m"` | 5分钟 | 短线交易 | ✅ |
| `"15m"` | 15分钟 | 中短线策略 | - |
| `"30m"` | 30分钟 | 中短线策略 | - |
| `"60m"` | 1小时或60分钟 | 短期趋势 | - |
| `"1d"` | 1日或日线或天 | 中长线策略 | - |
| `"1w"` | 1周或周 | 长期投资 | - |
| `"1mon"` | 1月或月 | 长期投资 | - |

### 品种池映射
| poolId | 说明 | 适用市场 | 默认值 |
|--------|------|----------|--------|
| `10` | **期货加权品种池** | 期货市场 | ✅ |
| `4` | 股票品种池 | 股票市场 | - |
| `6` | ETF品种池 | ETF市场 | - |

## 🔧 智能参数推断逻辑（重要）

### 基础周期推断规则（关键区别）
```python
# 重要概念区分：
# 1. 基础周期（period）：K线数据的周期（5m、30m、1d等）
# 2. 均线周期：技术指标的计算周期（30、60、120等）

# 规则1：用户明确指定基础周期时，使用用户指定的周期
if "基础周期" in user_input or "K线周期" in user_input or "数据周期" in user_input:
    if "30分钟" in user_input:
        period = "30m"
    elif "60分钟" in user_input or "1小时" in user_input:
        period = "60m"
    elif "5分钟" in user_input:
        period = "5m"
    elif "15分钟" in user_input:
        period = "15m"
    elif "日" in user_input or "天" in user_input:
        period = "1d"
    elif "周" in user_input:
        period = "1w"
    elif "月" in user_input:
        period = "1mon"
else:
    # 规则2：用户未明确指定基础周期时，使用默认周期5m
    # 注意：用户提到"30分钟均线"指的是均线周期，不是基础周期！
    period = "5m"  # 默认值
```

### 均线周期识别规则
```python
# 识别用户提到的均线周期（用于构建FactorLang表达式）
if "30分钟均线" in user_input:
    # 用户提到的是均线周期30，基础周期仍然是5m
    ma_period = "5m"  # 基础周期
    ma_length = "30"  # 均线长度
elif "60分钟均线" in user_input:
    ma_period = "5m"  # 基础周期
    ma_length = "60"  # 均线长度  
elif "120分钟均线" in user_input:
    ma_period = "5m"  # 基础周期
    ma_length = "120" # 均线长度
elif "240分钟均线" in user_input:
    ma_period = "5m"  # 基础周期
    ma_length = "240" # 均线长度
else:
    # 默认均线周期
    ma_period = "5m"
    ma_length = "30"
```

### 时间范围推断规则（重要：基于当前日期计算）
```python
# 重要：所有时间范围都基于当前日期动态计算
# 当前日期：2026年3月25日（根据环境信息）

# 规则1：用户明确指定时间范围时，使用用户指定的范围
if "近5年" in user_input:
    startDate = "2021-03-25"  # 当前日期-5年
    endDate = "2026-03-25"    # 当前日期
elif "近3年" in user_input:
    startDate = "2023-03-25"  # 当前日期-3年
    endDate = "2026-03-25"    # 当前日期
elif "近1年" in user_input:
    startDate = "2025-03-25"  # 当前日期-1年
    endDate = "2026-03-25"    # 当前日期
else:
    # 规则2：用户未指定时间范围时，使用默认近3个月
    startDate = "2025-12-25"  # 当前日期-3个月
    endDate = "2026-03-25"    # 当前日期
```

### 止损条件智能修正
```python
# 规则1：用户使用中文描述时，自动转换为FactorLang变量
if "盈亏点" in stop_condition or "点数" in stop_condition:
    stop_condition = stop_condition.replace("盈亏点", "_palp")
elif "盈亏%" in stop_condition or "百分比" in stop_condition:
    stop_condition = stop_condition.replace("盈亏%", "_palr")

# 规则2：确保使用正确的变量
if "_profit_loss_percent" in stop_condition:
    stop_condition = stop_condition.replace("_profit_loss_percent", "_palr")
```

## 🎯 使用示例（基于智能推断）

### 示例1：用户未指定基础周期（使用默认5m）
```python
# 用户输入：开仓条件，30分钟均线120朝上且日级别是金叉状态
# AI推断：用户提到的是均线周期30，不是基础周期，使用默认5m基础周期

mcp_engine_mcp_server_run_expression_selected(
    input={
        "startDate": "2024-01-17",      # 近3个月（默认）
        "endDate": "2024-04-17",         # 当前日期（默认）
        "period": "5m",                 # 5分钟基础周期（默认）
        "poolId": 10,                   # 期货加权池（默认）
        "openCondition": "_ma_5m_120_trend == 1 && _dkx_1d_cross_status == 1",
        "closeCondition": "_ma_5m_120_trend == -1 && _dkx_1d_cross_status == -1",
        "stopCondition": "_palp > 10",  # 盈亏点数大于10
        "initCash": 10000000,           # 1000万初始资金（默认）
        "direction": 1,                 # 多头方向（默认）
        "commssionFee": -1,             # 手续费%（默认：按系统设置）
        "slippage": 0,                  # 滑点（默认：无滑点）
        "runId": 123456789              # 运行ID（默认：随机生成）
    }
)
```

### 示例2：用户明确指定基础周期
```python
# 用户输入：开仓条件，基础周期30分钟，均线120朝上
# AI推断：用户明确指定基础周期30m

mcp_engine_mcp_server_run_expression_selected(
    input={
        "startDate": "2024-01-17",
        "endDate": "2024-04-17",
        "period": "30m",                # 用户指定基础周期30m
        "poolId": 10,
        "openCondition": "_ma_30m_120_trend == 1 && _dkx_1d_cross_status == 1",
        "closeCondition": "_ma_30m_120_trend == -1 && _dkx_1d_cross_status == -1",
        "stopCondition": "_palp > 10",
        "initCash": 10000000,
        "direction": 1,
        "commssionFee": -1,              # 手续费%（默认：按系统设置）
        "slippage": 0,                   # 滑点（默认：无滑点）
        "runId": 123456789               # 运行ID（默认：随机生成）
    }
)
```

### 示例3：用户指定手续费和滑点
```python
# 用户输入：开仓条件，均线朝上，手续费0.1%，滑点1个跳点
# AI推断：用户指定手续费和滑点参数

mcp_engine_mcp_server_run_expression_selected(
    input={
        "startDate": "2024-01-17",
        "endDate": "2024-04-17",
        "period": "5m",                 # 5分钟基础周期（默认）
        "poolId": 10,
        "openCondition": "_ma_5m_30_trend == 1",
        "closeCondition": "_ma_5m_30_trend == -1",
        "stopCondition": "_palp > 10",
        "initCash": 10000000,
        "direction": 1,
        "commssionFee": 0.1,             # 用户指定手续费0.1%
        "slippage": 1,                   # 用户指定滑点1个跳点
        "runId": 123456789               # 运行ID（默认：随机生成）
    }
)
```

### 示例4：用户指定具体合约代码（新增）
```python
# 用户输入：开仓条件，均线朝上，指定IF2404和IC2404合约
# AI推断：用户指定具体合约代码，系统自动将poolId置为0

mcp_engine_mcp_server_run_expression_selected(
    input={
        "startDate": "2024-01-17",
        "endDate": "2024-04-17",
        "period": "5m",                 # 5分钟基础周期（默认）
        "codes": "IF2404,IC2404",       # 用户指定具体合约代码
        "poolId": 10,                    # 系统会自动置为0，使用指定合约
        "openCondition": "_ma_5m_30_trend == 1",
        "closeCondition": "_ma_5m_30_trend == -1",
        "stopCondition": "_palp > 10",
        "initCash": 10000000,
        "direction": 1,
        "commssionFee": 0,               # 不需要手续费（默认）
        "slippage": 0,                    # 无滑点（默认）
        "runId": 123456789               # 运行ID（默认：随机生成）
    }
)
```

## 🚨 重要规则（AI必须遵守）

### 规则1：基础周期与均线周期区分
- **基础周期（period）**：K线数据的周期，默认值`"5m"`
- **均线周期**：技术指标的计算周期，如30、60、120等
- **关键区别**：用户提到"30分钟均线"指的是均线周期，不是基础周期！

### 规则2：基础周期推断逻辑
- 用户提到"基础周期"、"K线周期"、"数据周期" → 使用用户指定的基础周期
- **用户未明确指定基础周期** → 必须使用默认值`"5m"`
- 用户提到"30分钟均线" → 这是均线周期，基础周期仍然是`"5m"`

### 规则3：时间范围推断逻辑
- 用户提到"近5年" → 使用5年时间范围
- 用户提到"近3年" → 使用3年时间范围
- 用户提到"近1年" → 使用1年时间范围
- **用户未提到时间范围** → 必须使用`"近3个月"`

### 规则4：参数结构匹配（重要更新）
- **必须使用新的参数结构**：`input`对象包含所有参数
- **参数类型变更**：日期参数现在是`DateTime`类型
- **新增字段**：`codes`、`commssionFee`、`slippage`和`runId`参数

### 规则5：合约代码智能推断（新增）
- **用户提到具体合约代码**：如"IF2404"、"IC2404"等 → 自动设置`codes`字段
- **用户提到品种池**：如"期货加权池"、"股票池"等 → 使用`poolId`字段
- **同时指定合约和品种池**：优先使用合约代码，系统自动将`poolId`置为0

## 💡 最佳实践（AI执行策略）

1. **仔细分析用户输入**：严格区分基础周期和均线周期
2. **严格遵守默认值规则**：用户未明确指定基础周期时，必须使用默认值`"5m"`
3. **智能变量转换**：自动将中文描述转换为FactorLang变量
4. **参数验证**：确保所有参数符合MCP Server工具的要求
5. **参数结构匹配**：使用新的`input`对象结构
6. **手续费和滑点处理**：正确处理新增的`commssionFee`和`slippage`参数
7. **运行ID生成**：自动生成随机`runId`用于标识每次运行

## 🔄 默认值优先级（AI必须遵守）

1. **用户明确指定值**：最高优先级（必须包含"基础周期"等关键词）
2. **智能推断值**：根据用户描述推断
3. **MCP Server工具默认值**：最低优先级（当用户未指定时使用）

---

**数据来源**：基于MCP Server工具类的实际默认值设置
**调用时机**：当用户需要运行因子表达式策略、回测交易策略或执行金融分析时自动调用此技能。

**版本**：v3.0（同步MCP工具最新参数结构，新增codes字段，支持具体合约代码回测）

## � 运行耗时单位说明

### 运行耗时单位
- **运行耗时（timeConsuming）的单位是毫秒（ms）**
- 示例：`"timeConsuming": 310` 表示运行耗时310毫秒（0.31秒）

### 运行耗时解读
| 耗时范围 | 说明 | 性能评估 |
|----------|------|----------|
| < 100ms | 极快 | 优秀 |
| 100-500ms | 快速 | 良好 |
| 500-1000ms | 正常 | 一般 |
| > 1000ms | 较慢 | 需要优化 |

## �🔗 结果查看指南

### 策略结果查看方式
策略运行完成后，系统会生成一个唯一的查看链接：

```markdown
https://visual.hzyotoy.com/?data_dir=xzr&data_id=123456789&initCash=10000000
```

**点击链接或复制URL到浏览器中查看完整策略分析报告**

### 结果查看规范（AI必须遵守）
1. **必须提供完整的查看链接**：包含协议、主机、端口和所有参数
2. **必须明确说明链接用途**：告知用户这是策略分析报告链接
3. **必须提示用户点击操作**：明确指示用户如何查看结果
4. **必须包含运行耗时说明**：明确告知运行耗时的单位是毫秒

### 查看链接参数说明
| 参数 | 说明 | 示例 |
|------|------|------|
| `data_dir` | 数据目录 | `xzr` |
| `data_id` | 运行ID | `123456789` |
| `initCash` | 初始资金 | `10000000` |

**AI执行要求**：必须严格遵守本SKILL中的参数结构匹配规则、类型要求和结果查看规范！