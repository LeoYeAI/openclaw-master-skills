# 数据字段说明

## 股票数据（ftshare-market-data）

| 字段 | 说明 | 示例 |
|------|------|------|
| name | 股票名称 | 朗科科技 |
| symbol_id | 股票代码 | 300042 |
| change_rate | 涨跌幅（小数）| 0.20 → 展示为 +20.0% |
| turnover | 成交额（元）| 1511903038 → 展示为 15.1亿 |
| latest | 最新价 | 45.6 |
| trading_status | LIMIT_UP / LIMIT_DOWN / NORMAL | LIMIT_UP |
| close | 收盘价（指数用此字段，latest 可能为 null） | 4084.79 |
| prev_close | 昨收价 | 4095.45 |
| symbol_status.base | 股票基本状态 | NORMAL |
| symbol_status.extra | 盘中/收盘状态：TRADING / CALL_AUCTION / CLOSED | CLOSED |

## 涨跌幅数据处理规范

- `change_rate` 乘以 100 得百分比，正数加 `+`
- `turnover` 除以 1e8 保留1位小数得"亿"
- 跌幅榜过滤：`change_rate != null AND latest != null AND change_rate < 0`
- 展示颜色：涨 → RED(255,65,65)，跌 → GREEN(45,210,100)

## 新闻数据（newsnow-reader）

```bash
python3 newsnow-reader/scripts/fetch_news.py wallstreetcn 8
```
返回 JSON 列表，每项包含 `title`、`url`、`extra.info`

## 大盘指数

通过 `stock-security-info --symbol` 获取：
- 收盘场景：使用 `close` 字段（`latest` 可能为 null）
- 盘中场景：使用 `latest` 字段（实时价格），`close` 此时为昨收

| 指数 | 代码 | 取值字段 |
|------|------|---------|
| 上证指数 | 000001.SH | close + change_rate |
| 深证成指 | 399001.SZ | close + change_rate |
| 创业板指 | 399006.SZ | close + change_rate |

## 市场状态判断

通过任意股票的 `symbol_status.extra` 字段判断：

| 值 | 含义 | 对应场景 |
|----|------|---------|
| `CLOSED` | 已收盘 | 收盘复盘 |
| `NOT_OPEN` | 未开盘（非交易时段） | 收盘复盘（数据为最近交易日） |
| `TRADING` | 交易中 | 盘中快报，需标注时间 |
| `CALL_AUCTION` | 集合竞价中 | 盘中快报 |
