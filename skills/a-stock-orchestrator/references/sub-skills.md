# 子 Skill 快速参考

## akshare-stock - 常用 API

```python
import akshare as ak

# 实时行情
ak.stock_zh_a_spot_em()

# 个股历史K线
ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20250101", end_date="20251231", adjust="qfq")

# 财务指标
ak.stock_financial_analysis_indicator(symbol="000001")

# 板块列表（行业）
ak.stock_board_industry_name_em()

# 板块列表（概念）
ak.stock_board_concept_name_em()

# 板块成分股
ak.stock_board_industry_cons_em(symbol="半导体")

# 个股资金流向
ak.stock_individual_fund_flow(stock="000001", market="sh")

# 龙虎榜
ak.stock_lhb_detail_em(date="20250321")
```

## a-stock-trading-assistant - 脚本调用

```bash
# 个股实时行情
python3 skills/a-stock-trading-assistant/scripts/fetch_stock.py --code 600519

# 大盘指数
python3 skills/a-stock-trading-assistant/scripts/fetch_stock.py --index

# 热点板块
python3 skills/a-stock-trading-assistant/scripts/fetch_stock.py --hot-sectors
```

## a-stock-portfolio-monitor - 脚本调用

```bash
# 添加持仓
python3 skills/a-stock-portfolio-monitor/scripts/portfolio.py add 600519 --cost 1800 --qty 100 --name 贵州茅台

# 查看持仓
python3 skills/a-stock-portfolio-monitor/scripts/portfolio.py show

# 持仓分析
python3 skills/a-stock-portfolio-monitor/scripts/portfolio.py analyze

# 更新持仓
python3 skills/a-stock-portfolio-monitor/scripts/portfolio.py update 600519 --cost 1750

# 删除持仓
python3 skills/a-stock-portfolio-monitor/scripts/portfolio.py remove 600519
```

## tradingagents-analysis - API 调用

```bash
# 提交分析（需要 TRADINGAGENTS_TOKEN）
curl -X POST "https://api.510168.xyz/v1/analyze" \
  -H "Authorization: Bearer $TRADINGAGENTS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "贵州茅台"}'

# 查询任务状态
curl "https://api.510168.xyz/v1/jobs/{job_id}" \
  -H "Authorization: Bearer $TRADINGAGENTS_TOKEN"

# 获取结果
curl "https://api.510168.xyz/v1/jobs/{job_id}/result" \
  -H "Authorization: Bearer $TRADINGAGENTS_TOKEN"
```

## 其他 Skill（规则型，无脚本）

- **a-stock-fundamental-screening**: 读取 SKILL.md 获取筛选规则，用 LLM 对数据做判断
- **a-stock-leader-identification**: 读取 SKILL.md 获取龙头识别规则，用 LLM 对板块数据做判断
- **a-stock-volume-price**: 读取 SKILL.md 获取量价规则，用 LLM 对行情数据做判断
- **stock-research-engine**: 读取 SKILL.md + references/analysis-framework.md，按框架执行 6 步分析
