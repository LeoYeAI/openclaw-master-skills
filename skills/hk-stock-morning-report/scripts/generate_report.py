#!/usr/bin/env python3
"""
HK Stock Morning Report Generator
股市晨報生成器

Fetches index data from Tencent Finance API and generates
the morning report in the standard format.

Usage:
    python3 generate_report.py
"""

import json
import re
import urllib.request
from datetime import datetime, date
from typing import Optional

WORKDIR = "/root/.openclaw/workspace"
OUTPUT_FILE = f"{WORKDIR}/stock_morning_report.md"

# ─── Tencent Finance API ────────────────────────────────────────

def fetch_index(code: str) -> Optional[dict]:
    """
    Fetch HK index data from Tencent Finance API.
    code: r_hkHSI (恒生), r_hkHSTECH (恒科), r_hkHSTECH (國企)
    Returns dict with price, prev_close, change, change_pct
    """
    url = f"https://qt.gtimg.cn/q={code}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            raw = resp.read().decode("gbk")
        # Format: v_r_hkHSI="100,恒生指數,28645.88,28645.88,28555.71,28555.71,28555.71,28555.71,0,0,28645.88,28555.71,0,28645.88,28555.71,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
        # Field 1=code, 2=name, 3=price, 4=prev_close, 5=open, ...
        parts = raw.split("~")
        if len(parts) < 4:
            return None
        fields = parts[1].split(",")
        price = float(fields[3])
        prev_close = float(fields[4])
        change = price - prev_close
        change_pct = (change / prev_close) * 100
        sign = "+" if change >= 0 else ""
        return {
            "price": price,
            "prev_close": prev_close,
            "change": change,
            "change_pct": f"{sign}{change_pct:.2f}%",
            "sign": "+" if change >= 0 else ""
        }
    except Exception as e:
        print(f"[WARN] Failed to fetch {code}: {e}")
        return None


def get_last_trading_day() -> str:
    """Return the last trading day in YYYY-MM-DD format."""
    today = date.today()
    weekday = today.weekday()  # 0=Mon, 4=Fri
    days_ago = 1 if weekday >= 1 else (3 if weekday == 0 else 2)
    last = today - datetime.timedelta(days=days_ago)
    return last.strftime("%Y-%m-%d")


def get_date_header() -> str:
    """
    Determine the Section 1 header based on last trading day.
    Returns e.g. "昨日股市回顧" or "週X股市回顧"
    """
    today = date.today()
    weekday = today.weekday()  # 0=Mon
    days_ago = 1 if weekday >= 1 else (3 if weekday == 0 else 2)
    last = today - datetime.timedelta(days=days_ago)
    last_weekday = last.weekday()
    today_weekday = today.weekday()

    if (today - last).days == 1:
        return "昨日股市回顧"
    elif (today - last).days <= 5 and last_weekday >= 0 and last_weekday <= 4:
        # Same week
        weekday_names = ["一", "二", "三", "四", "五"]
        return f"週{weekday_names[last_weekday]}股市回顧"
    else:
        weekday_names = ["一", "二", "三", "四", "五"]
        return f"上週{weekday_names[last_weekday]}股市回顧"


# ─── Report Generation ──────────────────────────────────────────

def build_report(
    hsi_data: dict,
    hstech_data: dict,
    section1: str,
    section2: str,
    section3_items: list,  # [(title, content), ...]
    section4: tuple,       # (title, content)
    sources: str
) -> str:
    """Assemble the full report from components."""

    # Big title = 3 Section 3 titles joined by semicolons
    big_title = "; ".join([item[0] for item in section3_items[:3]])

    today_str = date.today().strftime("%-m.%-d")

    lines = [
        f"🔴股市晨報({today_str}) 🔵 | {big_title}",
        "",
        "「Xx內部文件 不得外傳 Internal Use only 」",
        "",
        f"📍一、{get_date_header()}",
        "",
        section1,
        "",
        "📍二、" + section2,
        "",
        "📍三、熱點資訊",
        ""
    ]

    for title, content in section3_items[:3]:
        lines.append(f"▶️ {title}")
        lines.append("")
        lines.append(content)
        lines.append("")

    if section4:
        title, content = section4
        lines.extend([
            "📍四、熱門港股",
            "",
            f"▶️ {title}",
            "",
            content,
            "",
        ])

    lines.extend([
        f"資料來源: {sources}",
        "",
        "「只供內部參考，不可外傳」"
    ])

    return "\n".join(lines)


def save_report(content: str) -> None:
    """Write report to OUTPUT_FILE."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Report saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    print("=== HK Stock Morning Report Generator ===")
    today = date.today().strftime("%Y-%m-%d")
    print(f"Date: {today}")
    print()

    # Fetch index data
    print("Fetching HSI...")
    hsi = fetch_index("r_hkHSI")
    if hsi:
        print(f"  HSI: {hsi['price']} ({hsi['sign']}{hsi['change']:.2f} / {hsi['change_pct']})")

    print("Fetching HSTECH...")
    hstech = fetch_index("r_hkHSTECH")
    if hstech:
        print(f"  HSTECH: {hstech['price']} ({hstech['sign']}{hstech['change']:.2f} / {hstech['change_pct']})")

    print()
    print(f"Last trading day: {get_last_trading_day()}")
    print(f"Section 1 header: {get_date_header()}")
    print()
    print("NOTE: Web search sections (market review, southbound capital,")
    print("      hot news, top stock) must be completed by the AI agent")
    print("      using Tavily web search per the SKILL.md workflow.")
    print()
    print("Generate report with the complete workflow from SKILL.md.")
