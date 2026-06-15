---
name: website-monitor
description: >
  构建一个自定义网站监控系统，能够每5分钟检测目标网站的HTTP状态码和响应时延，
  并在每天早上9点自动生成一份基于监控数据的HTML网页报告。
  
  当用户提到以下场景时，请务必使用此 skill：
  - 想要监控某个或多个网站是否正常运行
  - 想要记录网站的响应时间、延迟、可用性
  - 想要定时检查 HTTP 状态码（200、404、500 等）
  - 想要生成网站健康状况报告或可视化图表
  - 提到"网站监控"、"可用性检测"、"uptime"、"健康检查"、"HTTP 探测"等关键词
  - 想要每日汇总、每天早上自动发报告等定时报告需求
---

# Website Monitor Skill

本 skill 帮助用户构建一套完整的**网站 HTTP 监控系统**，包括：

- 每 5 分钟一次的 HTTP 状态码 + 响应时延探测
- 数据持久化存储（SQLite 或 JSON 文件）
- 每天早上 9:00 自动生成 HTML 网页报告
- 报告包含：可用率、平均/最大/最小时延、状态码分布、时序图

---

## 第一步：收集用户需求

在开始生成代码前，先确认以下信息（如用户已提供可跳过）：

1. **监控目标**：需要监控哪些网站 URL？（可多个）
2. **告警需求**：是否需要在网站宕机时发送通知？（邮件/Webhook/忽略）
3. **运行环境**：在哪里运行？（本地 Python、Linux 服务器、Docker）
4. **报告存储**：报告保存到本地文件即可，还是需要托管到某个路径？
5. **数据保留**：监控数据保留多少天？（默认 90 天，最多 90 天）

---

## 第二步：生成完整的监控系统代码

### 项目结构

```
website-monitor/
├── monitor.py          # 核心监控脚本（探测 + 数据存储）
├── report.py           # 报告生成脚本（读取数据 → HTML）
├── scheduler.py        # 定时任务入口（整合 monitor + report）
├── config.json         # 用户配置文件（监控目标、参数）
├── data/
│   └── monitor.db      # SQLite 数据库（或 monitor.jsonl）
└── reports/
    └── report_YYYYMMDD.html   # 每日生成的报告
```

---

### config.json 模板

```json
{
  "targets": [
    {
      "name": "示例网站",
      "url": "https://example.com",
      "timeout": 10
    }
  ],
  "check_interval_minutes": 5,
  "report_time": "09:00",
  "data_retention_days": 90,
  "report_dir": "./reports",
  "data_dir": "./data"
}
```

---

### monitor.py — 核心探测逻辑

```python
"""
monitor.py
每次运行：对所有目标发起 HTTP GET，记录状态码 + 响应时延到 SQLite。
"""
import sqlite3, requests, time, json, os
from datetime import datetime

CONFIG_PATH = "config.json"
DB_PATH = "data/monitor.db"

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def init_db(db_path: str):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS checks (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            ts        TEXT NOT NULL,         -- ISO8601 时间戳
            name      TEXT NOT NULL,         -- 目标名称
            url       TEXT NOT NULL,
            status    INTEGER,               -- HTTP 状态码，NULL 表示请求失败
            latency   REAL,                  -- 响应时间（秒），NULL 表示超时/错误
            error     TEXT                   -- 错误信息（正常时为 NULL）
        )
    """)
    conn.commit()
    return conn

def check_target(target: dict) -> dict:
    """对单个目标发起探测，返回结果字典。"""
    url = target["url"]
    timeout = target.get("timeout", 10)
    ts = datetime.utcnow().isoformat()
    try:
        start = time.perf_counter()
        resp = requests.get(url, timeout=timeout, allow_redirects=True)
        latency = time.perf_counter() - start
        return {
            "ts": ts,
            "name": target["name"],
            "url": url,
            "status": resp.status_code,
            "latency": round(latency, 4),
            "error": None
        }
    except requests.exceptions.Timeout:
        return {"ts": ts, "name": target["name"], "url": url,
                "status": None, "latency": None, "error": "Timeout"}
    except Exception as e:
        return {"ts": ts, "name": target["name"], "url": url,
                "status": None, "latency": None, "error": str(e)}

def run_checks(config: dict, conn: sqlite3.Connection):
    for target in config["targets"]:
        result = check_target(target)
        conn.execute(
            "INSERT INTO checks (ts, name, url, status, latency, error) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (result["ts"], result["name"], result["url"],
             result["status"], result["latency"], result["error"])
        )
        status_str = str(result["status"]) if result["status"] else f"ERR({result['error']})"
        latency_str = f"{result['latency']*1000:.1f}ms" if result["latency"] else "N/A"
        print(f"[{result['ts']}] {result['name']} → {status_str}  {latency_str}")
    conn.commit()

MAX_RETENTION_DAYS = 90  # 硬上限，不允许超过 90 天

def purge_old_data(config: dict, conn: sqlite3.Connection):
    """删除超过保留期的数据，保留天数不超过 MAX_RETENTION_DAYS。"""
    days = min(int(config.get("data_retention_days", MAX_RETENTION_DAYS)), MAX_RETENTION_DAYS)
    conn.execute(
        "DELETE FROM checks WHERE ts < datetime('now', ? || ' days')",
        (f"-{days}",)
    )
    conn.commit()
    print(f"[清理] 已删除 {days} 天前的历史数据（上限 {MAX_RETENTION_DAYS} 天）")

if __name__ == "__main__":
    cfg = load_config()
    db = init_db(cfg.get("data_dir", "./data") + "/monitor.db")
    run_checks(cfg, db)
    purge_old_data(cfg, db)
    db.close()
```

---

### report.py — HTML 报告生成

```python
"""
report.py
读取 SQLite 数据，汇总昨天（或指定日期）的监控数据，生成一份独立 HTML 报告。
"""
import sqlite3, json, os, sys
from datetime import datetime, timedelta, timezone
from collections import defaultdict

CONFIG_PATH = "config.json"

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def fetch_day_data(conn, date_str: str):
    """取指定日期（YYYY-MM-DD）的全部记录。"""
    rows = conn.execute(
        "SELECT ts, name, url, status, latency, error FROM checks "
        "WHERE DATE(ts) = ? ORDER BY ts",
        (date_str,)
    ).fetchall()
    return rows

def compute_stats(rows):
    """按 name 分组，计算可用率、时延统计、状态码分布。"""
    groups = defaultdict(list)
    for r in rows:
        groups[r[1]].append(r)
    
    stats = {}
    for name, records in groups.items():
        total = len(records)
        ok = [r for r in records if r[3] and 200 <= r[3] < 400]
        latencies = [r[4] * 1000 for r in records if r[4] is not None]
        status_dist = defaultdict(int)
        for r in records:
            key = str(r[3]) if r[3] else f"Error"
            status_dist[key] += 1
        
        stats[name] = {
            "url": records[0][2],
            "total": total,
            "uptime_pct": round(len(ok) / total * 100, 2) if total else 0,
            "avg_ms": round(sum(latencies) / len(latencies), 1) if latencies else None,
            "min_ms": round(min(latencies), 1) if latencies else None,
            "max_ms": round(max(latencies), 1) if latencies else None,
            "p95_ms": round(sorted(latencies)[int(len(latencies)*0.95)-1], 1) if len(latencies) >= 20 else None,
            "status_dist": dict(status_dist),
            "timeline": [
                {"ts": r[0], "status": r[3], "latency_ms": round(r[4]*1000,1) if r[4] else None, "error": r[5]}
                for r in records
            ]
        }
    return stats

def render_html(date_str: str, stats: dict) -> str:
    """将统计数据渲染为独立 HTML 字符串（内嵌 CSS + JS + Chart.js）。"""
    
    # 生成每个目标的卡片和图表数据
    cards_html = ""
    chart_scripts = ""
    
    for i, (name, s) in enumerate(stats.items()):
        uptime_color = "#22c55e" if s["uptime_pct"] >= 99 else "#f59e0b" if s["uptime_pct"] >= 95 else "#ef4444"
        
        status_badges = " ".join(
            f'<span class="badge" style="background:{("#22c55e" if k.startswith("2") else "#f59e0b" if k.startswith("3") else "#ef4444") if k != "Error" else "#6b7280"}">'
            f'{k}: {v}</span>'
            for k, v in s["status_dist"].items()
        )
        
        # 时延折线图数据（最多取 288 个点）
        tl = s["timeline"][-288:]
        labels = [t["ts"][11:16] for t in tl]  # HH:MM
        latency_data = [t["latency_ms"] if t["latency_ms"] is not None else "null" for t in tl]
        status_colors = [
            '"#22c55e"' if t["status"] and 200 <= t["status"] < 400
            else '"#ef4444"'
            for t in tl
        ]
        
        chart_id = f"chart_{i}"
        
        cards_html += f"""
        <div class="card">
          <div class="card-header">
            <div>
              <h2>{name}</h2>
              <a href="{s['url']}" target="_blank" class="url">{s['url']}</a>
            </div>
            <div class="uptime-badge" style="background:{uptime_color}">
              {s['uptime_pct']}% 可用
            </div>
          </div>
          
          <div class="metrics">
            <div class="metric">
              <div class="metric-value">{s['avg_ms'] or 'N/A'}</div>
              <div class="metric-label">平均时延 (ms)</div>
            </div>
            <div class="metric">
              <div class="metric-value">{s['min_ms'] or 'N/A'}</div>
              <div class="metric-label">最小时延 (ms)</div>
            </div>
            <div class="metric">
              <div class="metric-value">{s['max_ms'] or 'N/A'}</div>
              <div class="metric-label">最大时延 (ms)</div>
            </div>
            <div class="metric">
              <div class="metric-value">{s['p95_ms'] or 'N/A'}</div>
              <div class="metric-label">P95 时延 (ms)</div>
            </div>
            <div class="metric">
              <div class="metric-value">{s['total']}</div>
              <div class="metric-label">检测次数</div>
            </div>
          </div>
          
          <div class="status-row">{status_badges}</div>
          
          <div class="chart-wrap">
            <canvas id="{chart_id}"></canvas>
          </div>
        </div>
        """
        
        chart_scripts += f"""
        new Chart(document.getElementById('{chart_id}'), {{
          type: 'line',
          data: {{
            labels: {json.dumps(labels)},
            datasets: [{{
              label: '响应时延 (ms)',
              data: {latency_data},
              borderColor: '#6366f1',
              backgroundColor: 'rgba(99,102,241,0.08)',
              borderWidth: 1.5,
              pointRadius: 2,
              pointBackgroundColor: [{",".join(status_colors)}],
              tension: 0.3,
              fill: true,
              spanGaps: false
            }}]
          }},
          options: {{
            responsive: true,
            plugins: {{ legend: {{ display: false }} }},
            scales: {{
              x: {{ ticks: {{ maxTicksLimit: 12, font: {{ size: 10 }} }}, grid: {{ display: false }} }},
              y: {{ beginAtZero: true, title: {{ display: true, text: 'ms' }} }}
            }}
          }}
        }});
        """
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>网站监控日报 · {date_str}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f1f5f9; color: #1e293b; padding: 2rem; }}
    .header {{ text-align: center; margin-bottom: 2rem; }}
    .header h1 {{ font-size: 1.8rem; font-weight: 700; color: #0f172a; }}
    .header p {{ color: #64748b; margin-top: .4rem; }}
    .card {{ background: #fff; border-radius: 12px; padding: 1.5rem;
             margin-bottom: 1.5rem; box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
    .card-header {{ display: flex; justify-content: space-between;
                    align-items: flex-start; margin-bottom: 1rem; }}
    .card-header h2 {{ font-size: 1.1rem; font-weight: 600; }}
    .url {{ font-size: .8rem; color: #6366f1; text-decoration: none; }}
    .uptime-badge {{ color: #fff; border-radius: 20px; padding: .3rem .9rem;
                     font-size: .85rem; font-weight: 700; white-space: nowrap; }}
    .metrics {{ display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1rem; }}
    .metric {{ background: #f8fafc; border-radius: 8px; padding: .7rem 1.2rem;
               text-align: center; flex: 1; min-width: 90px; }}
    .metric-value {{ font-size: 1.3rem; font-weight: 700; color: #0f172a; }}
    .metric-label {{ font-size: .7rem; color: #94a3b8; margin-top: .2rem; }}
    .status-row {{ display: flex; flex-wrap: wrap; gap: .4rem; margin-bottom: 1rem; }}
    .badge {{ color: #fff; border-radius: 4px; padding: .15rem .5rem; font-size: .75rem; }}
    .chart-wrap {{ position: relative; height: 180px; }}
    @media (max-width: 600px) {{ body {{ padding: 1rem; }} .metrics {{ gap: .5rem; }} }}
  </style>
</head>
<body>
  <div class="header">
    <h1>🌐 网站监控日报</h1>
    <p>统计日期：{date_str} &nbsp;·&nbsp; 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
  </div>
  {cards_html}
  <script>
    {chart_scripts}
  </script>
</body>
</html>"""

def generate_report(date_str: str = None):
    cfg = load_config()
    if not date_str:
        # 默认生成昨天的报告
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    db_path = os.path.join(cfg.get("data_dir", "./data"), "monitor.db")
    conn = sqlite3.connect(db_path)
    rows = fetch_day_data(conn, date_str)
    conn.close()
    
    if not rows:
        print(f"[报告] {date_str} 无监控数据，跳过生成。")
        return
    
    stats = compute_stats(rows)
    html = render_html(date_str, stats)
    
    report_dir = cfg.get("report_dir", "./reports")
    os.makedirs(report_dir, exist_ok=True)
    out_path = os.path.join(report_dir, f"report_{date_str}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[报告] 已生成 → {out_path}")
    return out_path

if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    generate_report(date_arg)
```

---

### scheduler.py — 定时任务调度器

```python
"""
scheduler.py
主入口：启动后台调度器。
  - 每 5 分钟执行一次 monitor.py 的 run_checks()
  - 每天 09:00 执行一次 report.py 的 generate_report()

依赖：pip install schedule requests
"""
import schedule, time, sqlite3, os, json
from datetime import datetime
import monitor, report

def load_config():
    with open("config.json") as f:
        return json.load(f)

def job_check():
    cfg = load_config()
    db_path = os.path.join(cfg.get("data_dir", "./data"), "monitor.db")
    conn = monitor.init_db(db_path)
    monitor.run_checks(cfg, conn)
    monitor.purge_old_data(cfg, conn)
    conn.close()

def job_report():
    report.generate_report()  # 默认生成昨天的报告

if __name__ == "__main__":
    cfg = load_config()
    interval = cfg.get("check_interval_minutes", 5)
    report_time = cfg.get("report_time", "09:00")
    
    print(f"🚀 监控调度器启动")
    print(f"   探测间隔：每 {interval} 分钟")
    print(f"   日报时间：每天 {report_time}")
    print(f"   监控目标：{[t['name'] for t in cfg['targets']]}")
    print()
    
    # 立即执行一次检测
    job_check()
    
    # 注册定时任务
    schedule.every(interval).minutes.do(job_check)
    schedule.every().day.at(report_time).do(job_report)
    
    while True:
        schedule.run_pending()
        time.sleep(30)
```

---

## 第三步：安装与运行

### 安装依赖

```bash
pip install requests schedule
```

### 启动监控

```bash
python scheduler.py
```

### 手动生成今天/指定日期的报告

```bash
python report.py                    # 生成昨天的报告
python report.py 2024-01-15         # 生成指定日期的报告
```

### 使用 systemd 开机自启（Linux 服务器）

```ini
# /etc/systemd/system/website-monitor.service
[Unit]
Description=Website Monitor
After=network.target

[Service]
WorkingDirectory=/opt/website-monitor
ExecStart=/usr/bin/python3 scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable website-monitor
sudo systemctl start website-monitor
```

### Docker 运行（可选）

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install requests schedule
CMD ["python", "scheduler.py"]
```

---

## 第四步：报告示例说明

每份 HTML 报告包含以下内容（每个监控目标一张卡片）：

| 指标 | 说明 |
|------|------|
| 可用率 | 状态码 2xx/3xx 的比例，绿色 ≥99%，黄色 ≥95%，红色 <95% |
| 平均时延 | 全天响应时间均值（ms） |
| 最小/最大时延 | 全天最快/最慢响应 |
| P95 时延 | 95th 百分位数（需 ≥20 条数据才显示）|
| 检测次数 | 当天实际探测次数（288 次 = 全天无中断）|
| 状态码分布 | 各 HTTP 状态码出现次数 |
| 时延折线图 | 全天时延趋势，失败点标红 |

---

## 注意事项 / 常见问题

**Q：程序崩溃重启后数据会丢失吗？**  
A：不会，数据持久化在 SQLite，重启后继续写入。

**Q：如何新增监控目标？**  
A：编辑 `config.json` 的 `targets` 数组，重启 `scheduler.py` 即可。

**Q：想要宕机告警怎么办？**  
A：在 `monitor.py` 的 `run_checks()` 里，若 `result["status"]` 为 None 或 ≥500，可调用钉钉/飞书/Slack Webhook 发送告警消息。

**Q：能监控 HTTPS 证书过期吗？**  
A：可以扩展 `check_target()`，使用 `ssl` + `socket` 检测证书有效期并写入额外字段。
