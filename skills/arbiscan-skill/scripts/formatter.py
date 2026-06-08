"""输出格式化 — table / json / markdown"""

import json
from tabulate import tabulate


def format_table(rows: list, headers: list) -> str:
    """格式化为终端表格"""
    return tabulate(rows, headers=headers, tablefmt="simple", floatfmt=".4f")


def format_markdown(rows: list, headers: list) -> str:
    """格式化为 Markdown 表格"""
    return tabulate(rows, headers=headers, tablefmt="github", floatfmt=".4f")


def format_json(rows: list, headers: list) -> str:
    """格式化为 JSON"""
    data = [dict(zip(headers, row)) for row in rows]
    return json.dumps(data, indent=2, ensure_ascii=False)


def format_output(rows: list, headers: list, fmt: str = "table") -> str:
    """统一格式化入口"""
    if not rows:
        return "No opportunities found."
    formatters = {
        "table": format_table,
        "markdown": format_markdown,
        "json": format_json,
    }
    formatter = formatters.get(fmt, format_table)
    return formatter(rows, headers)


def risk_level(apy: float, symbol: str) -> str:
    """根据年化和币种评估风险等级
    HIGH: APY > 50% 或 (非主流币 且 APY > 20%)
    MEDIUM: APY 10-50% 或 非主流币
    LOW: 主流币 且 APY < 10%
    """
    major_coins = {"BTC", "ETH", "BNB", "SOL", "XRP"}
    is_major = symbol in major_coins
    if apy > 50:
        return "HIGH"
    if not is_major and apy > 20:
        return "HIGH"
    if apy > 10 or not is_major:
        return "MEDIUM"
    return "LOW"
