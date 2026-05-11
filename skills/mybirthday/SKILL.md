---
name: member-manager
description: "管理組織成員（家人、同事、親戚等）的個人資料、農曆/新曆生日及紀念日，並用 OpenClaw cron 設置自動提醒。Use when: (1) 添加/編輯成員資料, (2) 設置生日或紀念日提醒, (3) 更新農曆對應的新曆日期, (4) 查看即將到來的重要日子, (5) 管理多個組織的成員。NOT for: 一般日程安排（用 calendar skill）。"
version: 1.0.1
license: MIT-0
env:
  OPENCLAW_SESSION_KEY:
    description: "當前用戶的 session 標識符（如 Telegram user ID）。用於多用戶數據隔離。"
    required: false
    default: "default"
paths:
  config:
    - "~/.openclaw/session.json"
  data:
    - "~/.openclaw/workspace/users/{SESSION_KEY}/members.json"
    - "~/.openclaw/workspace/users/{SESSION_KEY}/reminders.json"
dependencies:
  python:
    - name: lunardate
      version: ">=0.2.2"
      license: GPL-3.0
      required_for: "農曆日期轉換"
tools:
  - mcp__scheduled-tasks__create_scheduled_task
  - mcp__scheduled-tasks__list_scheduled_tasks
  - mcp__scheduled-tasks__update_scheduled_task
---

# member-manager — 成員資料與生日紀念日管理

管理多個組織（家庭、同事、親戚等）中成員的個人資料、農曆/新曆生日及各類紀念日，並透過 OpenClaw scheduled-tasks 自動發送提醒。

---

## 核心原則

1. **先讀後寫**：任何修改操作前，先讀取現有 JSON 檔案內容
2. **原子寫入**：每次寫入完整 JSON，不做部分更新
3. **用戶確認**：添加/刪除成員前向用戶確認資訊是否正確
4. **農曆自動轉換**：用戶提供農曆日期時，自動計算當年新曆日期
5. **提醒同步**：刪除成員時同步清理提醒；修改生日時同步更新提醒

---

## 多用戶數據隔離

此 skill 支持多用戶共享同一個 OpenClaw（例如 Telegram bot 場景）。每個用戶的數據存放在以**用戶 session key 命名的獨立目錄**，互不干擾。

### 數據路徑規則

```
~/.openclaw/workspace/users/{SESSION_KEY}/members.json
~/.openclaw/workspace/users/{SESSION_KEY}/reminders.json
```

`{SESSION_KEY}` 是 OpenClaw 的當前 session 標識符（Telegram DM 場景即為 Telegram user ID）。

**在使用任何成員數據前，必須先確定當前用戶的路徑。**

### 如何確定當前用戶的數據目錄

讀取環境變數或 session context 取得用戶 ID，**必須先清洗以防止目錄遍歷攻擊**，然後初始化數據目錄：

```python
import os, json, re

def sanitize_session_key(raw_key: str) -> str:
    """清洗 session key，只允許字母數字、連字號和底線，防止目錄遍歷"""
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', raw_key)
    if not sanitized:
        raise ValueError(f"Invalid session key: {raw_key!r}")
    return sanitized

# 方法 1：從環境變數取得
raw_id = os.environ.get("OPENCLAW_SESSION_KEY", "default")

# 方法 2：如果是在 Telegram bot 場景，嘗試讀取 session 檔案
session_file = os.path.expanduser("~/.openclaw/session.json")
if os.path.exists(session_file):
    with open(session_file) as f:
        session = json.load(f)
    raw_id = session.get("user_id", session.get("session_key", "default"))

user_id = sanitize_session_key(str(raw_id))

WORKSPACE_ROOT = os.path.expanduser("~/.openclaw/workspace/users")
base_dir = os.path.join(WORKSPACE_ROOT, user_id)

# 二次驗證：確保解析後的路徑仍在 workspace 目錄內
real_base = os.path.realpath(base_dir)
real_root = os.path.realpath(WORKSPACE_ROOT)
if not real_base.startswith(real_root + os.sep):
    raise ValueError(f"Path traversal detected: {base_dir}")

members_path = os.path.join(base_dir, "members.json")
reminders_path = os.path.join(base_dir, "reminders.json")

# 初始化新用戶
os.makedirs(base_dir, exist_ok=True)
if not os.path.exists(members_path):
    with open(members_path, "w") as f:
        json.dump([], f)
if not os.path.exists(reminders_path):
    with open(reminders_path, "w") as f:
        json.dump([], f)
```

---

## 數據結構

### members.json

```json
[
  {
    "id": "uuid-v4",
    "name": "張三",
    "group": "家庭",
    "relationship": "父親",
    "phone": "0912345678",
    "birthday_solar": "1955-03-15",
    "birthday_lunar": {
      "month": 2,
      "day": 13,
      "is_leap_month": false
    },
    "birthday_lunar_solar_this_year": "2025-03-12",
    "anniversaries": [
      {
        "id": "uuid-v4",
        "label": "結婚紀念日",
        "date_solar": "1980-06-20",
        "recurring": true
      }
    ],
    "notes": "喜歡喝普洱茶",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
]
```

欄位說明：
- `id`：UUID v4，成員唯一標識
- `name`：姓名（必填）
- `group`：組別/組織名稱，如「家庭」「公司」「大學同學」（必填）
- `relationship`：與用戶的關係，如「父親」「主管」「同學」
- `phone`：電話號碼
- `birthday_solar`：新曆生日，格式 `YYYY-MM-DD`
- `birthday_lunar`：農曆生日，含 month/day/is_leap_month
- `birthday_lunar_solar_this_year`：農曆生日在**當年**對應的新曆日期（每年需更新）
- `anniversaries`：紀念日列表，每個紀念日有獨立 id
- `notes`：備註
- `created_at` / `updated_at`：時間戳

### reminders.json

```json
[
  {
    "id": "uuid-v4",
    "member_id": "對應 member 的 id",
    "type": "birthday_solar",
    "label": "張三 新曆生日",
    "advance_days": 3,
    "scheduled_task_id": "member-birthday-張三-solar",
    "enabled": true
  }
]
```

欄位說明：
- `type`：`birthday_solar` | `birthday_lunar` | `anniversary`
- `advance_days`：提前幾天提醒（默認 3 天）
- `scheduled_task_id`：對應 OpenClaw scheduled-task 的 ID
- `enabled`：是否啟用

---

## 農曆處理

農曆轉新曆每年都會變，因此需要**每年更新**農曆生日對應的新曆日期。

### 農曆轉新曆

```python
# pip install lunardate
from lunardate import LunarDate
from datetime import date, timedelta

def lunar_to_solar(year: int, lunar_month: int, lunar_day: int, is_leap: bool = False) -> date:
    """將農曆日期轉換為新曆日期"""
    try:
        lunar = LunarDate(year, lunar_month, lunar_day, is_leap)
        return lunar.toSolarDate()
    except ValueError:
        # 若該年無此農曆日期（例如閏月不存在），嘗試非閏月
        if is_leap:
            lunar = LunarDate(year, lunar_month, lunar_day, False)
            return lunar.toSolarDate()
        raise
```

### 計算提醒日期（正確處理跨月）

```python
def calculate_reminder_date(target_date: date, advance_days: int) -> date:
    """計算提前提醒的日期，正確處理跨月情況"""
    return target_date - timedelta(days=advance_days)
```

### 年度更新所有農曆生日

```python
def update_all_lunar_birthdays(base_dir: str, year: int):
    """更新所有成員農曆生日在指定年份的新曆日期"""
    members_path = os.path.join(base_dir, "members.json")
    with open(members_path) as f:
        members = json.load(f)

    updated = []
    for m in members:
        lunar = m.get("birthday_lunar")
        if lunar:
            try:
                solar = lunar_to_solar(
                    year, lunar["month"], lunar["day"],
                    lunar.get("is_leap_month", False)
                )
                m["birthday_lunar_solar_this_year"] = str(solar)
                updated.append(m["name"])
            except ValueError as e:
                # 記錄錯誤但繼續處理其他成員
                pass
        m["updated_at"] = datetime.utcnow().isoformat() + "Z"

    with open(members_path, "w") as f:
        json.dump(members, f, ensure_ascii=False, indent=2)

    return updated
```

---

## 功能操作指南

### 1. 添加成員

當用戶要求添加成員時：
1. 解析用戶提供的信息（姓名、組別、關係、生日等）
2. 如果用戶提供農曆生日，自動轉換為當年新曆日期
3. 向用戶確認信息後寫入

```python
import json, os, uuid
from datetime import datetime

def add_member(base_dir, name, group, relationship="", birthday_solar=None,
               birthday_lunar=None, phone="", notes=""):
    path = os.path.join(base_dir, "members.json")
    with open(path) as f:
        members = json.load(f)

    # 檢查是否已有同名同組成員
    for existing in members:
        if existing["name"] == name and existing["group"] == group:
            return None, f"已存在同名成員：{name}（{group}）"

    now = datetime.utcnow().isoformat() + "Z"
    member = {
        "id": str(uuid.uuid4()),
        "name": name,
        "group": group,
        "relationship": relationship,
        "phone": phone,
        "birthday_solar": birthday_solar,
        "birthday_lunar": birthday_lunar,
        "birthday_lunar_solar_this_year": None,
        "anniversaries": [],
        "notes": notes,
        "created_at": now,
        "updated_at": now
    }

    # 如果有農曆生日，計算當年新曆日期
    if birthday_lunar:
        from lunardate import LunarDate
        from datetime import date
        try:
            solar = lunar_to_solar(
                date.today().year,
                birthday_lunar["month"],
                birthday_lunar["day"],
                birthday_lunar.get("is_leap_month", False)
            )
            member["birthday_lunar_solar_this_year"] = str(solar)
        except ValueError:
            pass

    members.append(member)
    with open(path, "w") as f:
        json.dump(members, f, ensure_ascii=False, indent=2)

    return member, None
```

### 2. 編輯成員

```python
def update_member(base_dir, member_id, **updates):
    """更新成員資料。支持更新任意欄位。"""
    path = os.path.join(base_dir, "members.json")
    with open(path) as f:
        members = json.load(f)

    for m in members:
        if m["id"] == member_id:
            for key, value in updates.items():
                if key in m and key not in ("id", "created_at"):
                    m[key] = value
            m["updated_at"] = datetime.utcnow().isoformat() + "Z"

            # 如果更新了農曆生日，重新計算新曆日期
            if "birthday_lunar" in updates and updates["birthday_lunar"]:
                from datetime import date
                try:
                    lunar = updates["birthday_lunar"]
                    solar = lunar_to_solar(
                        date.today().year,
                        lunar["month"], lunar["day"],
                        lunar.get("is_leap_month", False)
                    )
                    m["birthday_lunar_solar_this_year"] = str(solar)
                except ValueError:
                    pass

            with open(path, "w") as f:
                json.dump(members, f, ensure_ascii=False, indent=2)
            return m
    return None
```

### 3. 刪除成員

刪除成員時**必須同步清理提醒**：

```python
def delete_member(base_dir, member_id):
    """刪除成員及其所有提醒"""
    # 刪除成員
    members_path = os.path.join(base_dir, "members.json")
    with open(members_path) as f:
        members = json.load(f)

    member = None
    new_members = []
    for m in members:
        if m["id"] == member_id:
            member = m
        else:
            new_members.append(m)

    if not member:
        return None, []

    with open(members_path, "w") as f:
        json.dump(new_members, f, ensure_ascii=False, indent=2)

    # 清理該成員的所有提醒
    reminders_path = os.path.join(base_dir, "reminders.json")
    with open(reminders_path) as f:
        reminders = json.load(f)

    removed_task_ids = []
    new_reminders = []
    for r in reminders:
        if r["member_id"] == member_id:
            removed_task_ids.append(r.get("scheduled_task_id"))
        else:
            new_reminders.append(r)

    with open(reminders_path, "w") as f:
        json.dump(new_reminders, f, ensure_ascii=False, indent=2)

    return member, removed_task_ids
```

**重要**：刪除成員後，需要用 `mcp__scheduled-tasks__update_scheduled_task` 停用對應的 scheduled tasks（將 `removed_task_ids` 中的 task 設為 disabled）。

### 4. 添加紀念日

```python
def add_anniversary(base_dir, member_id, label, date_solar, recurring=True):
    """為成員添加紀念日"""
    path = os.path.join(base_dir, "members.json")
    with open(path) as f:
        members = json.load(f)

    for m in members:
        if m["id"] == member_id:
            anniversary = {
                "id": str(uuid.uuid4()),
                "label": label,
                "date_solar": date_solar,
                "recurring": recurring
            }
            m["anniversaries"].append(anniversary)
            m["updated_at"] = datetime.utcnow().isoformat() + "Z"

            with open(path, "w") as f:
                json.dump(members, f, ensure_ascii=False, indent=2)
            return anniversary
    return None
```

### 5. 刪除紀念日

```python
def remove_anniversary(base_dir, member_id, anniversary_id):
    """刪除成員的某個紀念日"""
    path = os.path.join(base_dir, "members.json")
    with open(path) as f:
        members = json.load(f)

    for m in members:
        if m["id"] == member_id:
            m["anniversaries"] = [
                a for a in m["anniversaries"] if a["id"] != anniversary_id
            ]
            m["updated_at"] = datetime.utcnow().isoformat() + "Z"

            with open(path, "w") as f:
                json.dump(members, f, ensure_ascii=False, indent=2)
            return True
    return False
```

### 6. 查看即將到來的重要日子

```python
from datetime import date, timedelta
import calendar

def _safe_replace_year(d: date, year: int) -> date:
    """安全替換年份，處理 2/29 在非閏年的情況（fallback 到 2/28）"""
    if d.month == 2 and d.day == 29 and not calendar.isleap(year):
        return date(year, 2, 28)
    return d.replace(year=year)

def upcoming_events(base_dir, days_ahead=30):
    """查詢未來 N 天內的生日和紀念日"""
    path = os.path.join(base_dir, "members.json")
    with open(path) as f:
        members = json.load(f)

    today = date.today()
    end_date = today + timedelta(days=days_ahead)
    events = []

    for m in members:
        # 新曆生日
        if m.get("birthday_solar"):
            bday = date.fromisoformat(m["birthday_solar"])
            this_year = _safe_replace_year(bday, today.year)
            # 處理跨年情況
            if this_year < today:
                this_year = _safe_replace_year(bday, today.year + 1)
            if today <= this_year <= end_date:
                age = this_year.year - bday.year
                events.append({
                    "date": str(this_year),
                    "name": m["name"],
                    "group": m["group"],
                    "type": "新曆生日",
                    "label": f"{m['name']} 的生日（{age} 歲）",
                    "member_id": m["id"]
                })

        # 農曆生日（使用預計算的當年新曆日期）
        if m.get("birthday_lunar_solar_this_year"):
            lunar_solar = date.fromisoformat(m["birthday_lunar_solar_this_year"])
            if today <= lunar_solar <= end_date:
                events.append({
                    "date": str(lunar_solar),
                    "name": m["name"],
                    "group": m["group"],
                    "type": "農曆生日",
                    "label": f"{m['name']} 的農曆生日（農曆{m['birthday_lunar']['month']}月{m['birthday_lunar']['day']}日）",
                    "member_id": m["id"]
                })

        # 紀念日
        for ann in m.get("anniversaries", []):
            if ann.get("recurring") and ann.get("date_solar"):
                aday = date.fromisoformat(ann["date_solar"])
                this_year = _safe_replace_year(aday, today.year)
                if this_year < today:
                    this_year = _safe_replace_year(aday, today.year + 1)
                if today <= this_year <= end_date:
                    years = this_year.year - aday.year
                    events.append({
                        "date": str(this_year),
                        "name": m["name"],
                        "group": m["group"],
                        "type": "紀念日",
                        "label": f"{m['name']} — {ann['label']}（第 {years} 年）",
                        "member_id": m["id"]
                    })

    return sorted(events, key=lambda e: e["date"])
```

### 7. 搜索與篩選成員

```python
def search_members(base_dir, query=None, group=None):
    """搜索成員。支持按名字模糊搜索和按組別篩選。"""
    path = os.path.join(base_dir, "members.json")
    with open(path) as f:
        members = json.load(f)

    results = members
    if group:
        results = [m for m in results if m["group"] == group]
    if query:
        query_lower = query.lower()
        results = [m for m in results if
                   query_lower in m["name"].lower() or
                   query_lower in m.get("relationship", "").lower() or
                   query_lower in m.get("notes", "").lower()]
    return results

def list_groups(base_dir):
    """列出所有組別及成員數量"""
    path = os.path.join(base_dir, "members.json")
    with open(path) as f:
        members = json.load(f)

    groups = {}
    for m in members:
        g = m["group"]
        groups[g] = groups.get(g, 0) + 1
    return groups
```

---

## 設置提醒（OpenClaw Scheduled Tasks）

提醒使用 OpenClaw 的 `mcp__scheduled-tasks__create_scheduled_task` 工具來創建持久化的定時任務。

### 設置生日提醒

為成員設置生日提醒時，需要計算提醒日期並創建 scheduled task：

```
步驟：
1. 確定生日日期（新曆或農曆轉新曆）
2. 計算提醒日期 = 生日日期 - advance_days
3. 使用 mcp__scheduled-tasks__create_scheduled_task 創建任務
4. 將提醒信息寫入 reminders.json
```

#### Scheduled Task 參數範例

**新曆生日提醒**（每年固定日期）：
```
taskId: "member-birthday-{member_name}-solar"
cronExpression: "0 9 {remind_day} {remind_month} *"
prompt: "🎂 提醒：{member_name} 的生日在 {advance_days} 天後（{birthday_month}/{birthday_day}）！請準備祝福！\n\n成員資料：\n- 關係：{relationship}\n- 組別：{group}\n- 備註：{notes}"
description: "{member_name} 生日提醒（提前 {advance_days} 天）"
```

**農曆生日提醒**（日期每年變化，需配合年度更新）：
```
taskId: "member-birthday-{member_name}-lunar"
cronExpression: "0 9 {remind_day} {remind_month} *"
prompt: "🎂 提醒：{member_name} 的農曆生日在 {advance_days} 天後（農曆{lunar_month}月{lunar_day}日，今年新曆{solar_date}）！\n\n成員資料：\n- 關係：{relationship}\n- 組別：{group}\n- 備註：{notes}"
description: "{member_name} 農曆生日提醒（提前 {advance_days} 天）"
```

**紀念日提醒**：
```
taskId: "member-anniversary-{member_name}-{anniversary_label}"
cronExpression: "0 9 {remind_day} {remind_month} *"
prompt: "💝 提醒：{member_name} 的{anniversary_label}在 {advance_days} 天後（{date}）！\n\n成員資料：\n- 關係：{relationship}\n- 備註：{notes}"
description: "{member_name} {anniversary_label}提醒"
```

### 提醒日期計算（跨月處理）

**重要**：不能簡單用 `day - advance_days`，必須用日期運算處理跨月情況：

```python
from datetime import date, timedelta
import calendar

def get_reminder_cron(target_month, target_day, advance_days):
    """計算提醒的 cron expression，正確處理跨月和跨年"""
    today = date.today()
    year = today.year
    m, d = int(target_month), int(target_day)

    # 處理 2/29 非閏年 fallback
    if m == 2 and d == 29 and not calendar.isleap(year):
        d = 28

    target = date(year, m, d)
    # 如果今年的目標日期已過，使用明年
    if target < today:
        year += 1
        if m == 2 and int(target_day) == 29 and not calendar.isleap(year):
            d = 28
        target = date(year, m, d)

    remind_date = target - timedelta(days=advance_days)
    # 返回 cron: 分 時 日 月 星期
    return f"0 9 {remind_date.day} {remind_date.month} *"
```

### 寫入 reminders.json

```python
def save_reminder(base_dir, member_id, reminder_type, label, advance_days, task_id):
    """保存提醒記錄"""
    path = os.path.join(base_dir, "reminders.json")
    with open(path) as f:
        reminders = json.load(f)

    reminder = {
        "id": str(uuid.uuid4()),
        "member_id": member_id,
        "type": reminder_type,
        "label": label,
        "advance_days": advance_days,
        "scheduled_task_id": task_id,
        "enabled": True
    }
    reminders.append(reminder)

    with open(path, "w") as f:
        json.dump(reminders, f, ensure_ascii=False, indent=2)
    return reminder
```

### 年度農曆更新任務

應設置一個每年 1 月 1 日執行的 scheduled task，自動更新所有農曆生日的新曆日期：

```
taskId: "member-lunar-annual-update"
cronExpression: "0 10 1 1 *"
prompt: "執行 member-manager 年度農曆更新：
1. 讀取 members.json 中所有有農曆生日的成員
2. 使用 lunardate 將每個農曆生日轉換為今年的新曆日期
3. 更新 birthday_lunar_solar_this_year 欄位
4. 更新所有農曆生日提醒的 cron expression（因為新曆日期變了）
5. 回報更新結果"
description: "每年自動更新農曆生日對應的新曆日期"
```

---

## 輸出格式

### 成員列表顯示格式

```
📋 {group} 成員列表（共 N 人）

1. {name}（{relationship}）
   🎂 生日：{birthday_solar}（新曆）/ 農曆{lunar_month}月{lunar_day}日
   📞 {phone}
   📝 {notes}

2. ...
```

### 即將到來的事件顯示格式

```
📅 未來 {days} 天的重要日子：

🎂 {date} — {name} 的生日（{age} 歲）
💝 {date} — {name} — {anniversary_label}（第 N 年）
...

共 N 個事件。
```

### 操作結果確認格式

```
✅ 已添加成員：{name}（{group} / {relationship}）
   生日：{birthday_info}
   已設置提醒：提前 {advance_days} 天

✅ 已刪除成員：{name}
   已清理 {N} 個相關提醒

✅ 已更新 {N} 位成員的農曆生日新曆日期
```

---

## 常用指令示例

以下是用戶可以對 AI 說的話，以及 skill 應如何回應：

| 用戶說 | AI 應執行 |
|--------|-----------|
| 幫我加一個成員：媽媽，農曆三月初五生日 | add_member（group 默認「家庭」） + lunar_to_solar + 存檔 + 詢問是否設置提醒 |
| 加同事小王，5月3號生日 | add_member（group「同事」）+ 存檔 |
| 查看這個月有哪些生日 | upcoming_events(days_ahead=30)，以表格顯示 |
| 幫我提前 3 天提醒張三的生日 | 計算提醒日期 + create_scheduled_task + save_reminder |
| 更新今年所有農曆生日的新曆日期 | update_all_lunar_birthdays + 更新相關提醒的 cron |
| 顯示家庭組的所有成員 | search_members(group="家庭")，以列表顯示 |
| 幫張三加一個結婚紀念日 6/20 | add_anniversary + 詢問是否設置提醒 |
| 刪除成員李四 | 確認後 delete_member + 清理提醒 + 停用 scheduled tasks |
| 修改張三的電話 | update_member(phone=...) |
| 列出所有組別 | list_groups 顯示組別及人數 |
| 查看所有提醒 | 讀取 reminders.json 並用 list_scheduled_tasks 顯示狀態 |
| 設置每年自動更新農曆 | 創建 member-lunar-annual-update scheduled task |

---

## 互動流程

### 添加成員的完整互動流程

```
用戶：幫我加一個成員，我媽媽，農曆三月初五生日

AI：
1. 解析信息：姓名=媽媽，關係=母親，農曆生日=三月初五
2. 計算今年新曆日期
3. 確認：
   「確認添加以下成員：
    - 姓名：媽媽
    - 組別：家庭
    - 關係：母親
    - 農曆生日：三月初五（今年新曆 {date}）
    是否正確？要設置生日提醒嗎？」
4. 用戶確認後存檔
5. 如果要提醒，詢問提前幾天（默認 3 天）
6. 創建 scheduled task + 保存 reminder
```

### 農曆日期的自然語言解析

用戶可能用多種方式表達農曆日期：
- 「農曆三月初五」→ month=3, day=5
- 「陰曆八月十五」→ month=8, day=15
- 「農曆閏四月初一」→ month=4, day=1, is_leap_month=true
- 「二月二」→ month=2, day=2

---

## 安全與隱私

### PII 數據保護

本 skill 存儲個人可識別信息（PII），包括姓名、電話、生日等。**所有數據以明文 JSON 存儲在本地磁碟**。

**必要的安全措施：**
1. **文件權限**：數據目錄應設置為僅用戶可讀（`chmod 700 ~/.openclaw/workspace/users/`）
2. **備份加密**：備份時應使用加密（如 `gpg` 或加密壓縮包）
3. **不要將數據目錄同步到雲端**（如 iCloud、Dropbox），除非雲端本身有加密

```python
# 初始化時設置目錄權限
import stat
os.makedirs(base_dir, exist_ok=True)
os.chmod(base_dir, stat.S_IRWXU)  # 700: 僅 owner 可讀寫執行
```

### Session Key 安全

Session key **必須經過清洗**才能用於構建文件路徑，防止目錄遍歷攻擊（如 `../../etc/passwd`）。參見上方 `sanitize_session_key()` 函數。

### Agent 自主存取控制

當此 skill 被 AI agent 自主調用時：
- **讀取操作**（查看成員、查詢事件）：可自動執行
- **寫入操作**（添加/編輯/刪除成員）：**必須先向用戶確認**
- **提醒設置**（創建 scheduled task）：**必須先向用戶確認**
- **刪除操作**（刪除成員及提醒）：**必須先向用戶確認，且明確列出將被刪除的內容**

### lunardate 依賴

推薦使用 `lunardate` 套件（PyPI: `lunardate`）：
- **維護者**：lidaobing
- **版本**：0.2.2（2023-12-07）
- **許可證**：GPLv3（注意：若 skill 本身使用 MIT-0，分發時需考慮 GPL 兼容性）
- **支持範圍**：1900–2099 年的農曆轉換
- **狀態**：Beta，無已知安全漏洞
- **安裝前**建議用 `pip-audit` 掃描確認

---

## 注意事項

1. **農曆閏月**：`birthday_lunar.is_leap_month` 標記是否為閏月，轉換時需傳入 `is_leap=True`。若該年無閏月，自動 fallback 到非閏月
2. **跨年生日查詢**：查詢即將到來的事件時，如果今年的日期已過，應查看明年的日期
3. **跨用戶隔離**：永遠不要在沒有 session key 的情況下讀寫成員數據
4. **Cron 管理**：刪除成員時，必須同步刪除 reminders.json 條目並停用 scheduled tasks
5. **重複檢查**：添加成員前檢查是否已存在同名同組成員
6. **lunardate 安裝**：首次使用農曆功能時，需確認 `lunardate` 已安裝（`pip install lunardate`），並用 `pip-audit` 掃描
7. **2 月 29 日處理**：使用 `_safe_replace_year()` 自動 fallback 到 2/28（非閏年）
8. **文件權限**：確保數據目錄權限為 700，防止其他用戶讀取 PII
