# Tushare Pro 金融数据 Skill

[![Version](https://img.shields.io/badge/version-1.3.0-blue.svg)](https://tushare.pro)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE)
[![ClawHub](https://img.shields.io/badge/ClawHub-BossQuant-purple.svg)](https://clawhub.com)

Tushare Pro金融大数据平台，提供A股、指数、基金、期货、债券、宏观数据。

## ✨ 特性

- 👥 **300万+用户** - 国内最大的金融数据社区之一
- 🔌 **标准化API** - 统一的接口风格，简洁易用
- 📊 **全品种覆盖** - A股、指数、基金、期货、债券、宏观经济
- 🏆 **积分体系** - 按积分等级开放不同数据权限

## 📥 安装

```bash
pip install tushare --upgrade
```

## ⚙️ 配置

需注册 [Tushare Pro](https://tushare.pro) 获取 Token：

```python
import tushare as ts

# 方式一：直接设置
ts.set_token('YOUR_TUSHARE_TOKEN')

# 方式二：环境变量 TUSHARE_TOKEN
```

## 🚀 快速开始

```python
import tushare as ts

ts.set_token('YOUR_TUSHARE_TOKEN')
pro = ts.pro_api()

# 获取日线行情
df = pro.daily(ts_code='000001.SZ', start_date='20240101', end_date='20241231')
print(df.head())

# 获取股票列表
df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
print(df.head())
```

## 📊 支持的数据类型

| 类别 | 说明 | 示例接口 |
|------|------|----------|
| 股票行情 | 日线/周线/月线 | `pro.daily()` |
| 股票列表 | 基本信息 | `pro.stock_basic()` |
| 每日指标 | 市盈率/换手率等 | `pro.daily_basic()` |
| 财务数据 | 利润表/资产负债表 | `pro.income()` / `pro.balancesheet()` |
| 指数行情 | 指数日线 | `pro.index_daily()` |
| 基金行情 | 基金净值/行情 | `pro.fund_daily()` |
| 期货行情 | 期货日线 | `pro.fut_daily()` |
| 宏观经济 | GDP/CPI等 | `pro.cn_gdp()` |

## 📖 更多示例

```python
import tushare as ts

pro = ts.pro_api()

# 每日指标（市盈率、换手率等）
df = pro.daily_basic(ts_code='000001.SZ', trade_date='20241231')

# 利润表
df = pro.income(ts_code='000001.SZ', period='20240331')

# 指数日线
df = pro.index_daily(ts_code='000300.SH', start_date='20240101', end_date='20241231')
```

## 📄 许可证

Apache License 2.0

## 📊 更新日志

### v1.3.0 (2026-03-23)
- 🎉 增加更丰富的AI Agent演示和高阶使用指南
- 🔄 更新版本号并清理失效链接


### v1.2.0 (2026-03-15)
- 🎉 初始版本发布
- 📊 支持A股、指数、基金、期货、债券、宏观数据

---

## 🤝 社区与支持

- **维护者**：大佬量化 (Boss Quant)
- **主页**：https://tushare.pro
- **ClawHub**：https://clawhub.com
