# Context Restore API 参考

本文档提供 Context Restore 所有公开 API 的详细参考，包括函数签名、参数说明、返回值和使用示例。

---

## 目录

- [核心函数](#核心函数)
- [变化检测函数](#变化检测函数)
- [自动恢复函数](#自动恢复函数)
- [Cron 集成函数](#cron-集成函数)
- [辅助函数](#辅助函数)
- [类型定义](#类型定义)

---

## 核心函数

### `load_compressed_context()`

加载压缩的上下文文件。

**签名：**
```python
def load_compressed_context(filepath: str) -> Any
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| filepath | str | 是 | 上下文文件路径 |

**返回值：**
| 类型 | 说明 |
|------|------|
| dict/list | 有效的 JSON 对象 |
| str | 非 JSON 格式的原始内容 |
| None | 文件无法加载 |

**异常：**
| 异常类型 | 触发条件 |
|----------|---------|
| ContextLoadError | 文件不存在、权限被拒、读取错误 |

**示例：**
```python
from restore_context import load_compressed_context

# 加载 JSON 文件
result = load_compressed_context('./compressed_context/latest_compressed.json')

if isinstance(result, dict):
    print(f"JSON format: {result.get('version')}")
else:
    print(f"Text format: {result[:100]}")
```

---

### `parse_metadata()`

从纯文本内容中提取元数据。

**签名：**
```python
def parse_metadata(content: str) -> dict
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | str | 是 | 原始文本内容 |

**返回值：**
```python
{
    "original_count": int,      # 原始消息数
    "compressed_count": int,    # 压缩后消息数
    "timestamp": str           # 压缩时间戳
}
```

**示例：**
```python
from restore_context import parse_metadata

content = """
上下文压缩于 2026-02-06 23:42:00
原始消息数: 150
压缩后消息数: 25
"""

metadata = parse_metadata(content)
print(metadata)
# {'original_count': 150, 'compressed_count': 25, 'timestamp': '2026-02-06'}
```

---

### `extract_recent_operations()`

提取最近操作记录。

**签名：**
```python
def extract_recent_operations(content: str, max_count: int = 5) -> list[str]
```

**参数：**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| content | str | 是 | - | 原始文本内容 |
| max_count | int | 否 | 5 | 最大返回操作数 |

**返回值：**
| 类型 | 说明 |
|------|------|
| list[str] | 操作描述列表 |

**示例：**
```python
from restore_context import extract_recent_operations

content = """
✅ 完成数据清洗模块
✅ 部署新功能到生产环境
✅ 添加 3 个新 cron 任务
"""

ops = extract_recent_operations(content, max_count=10)
print(ops)
# ['完成数据清洗模块', '部署新功能到生产环境', '添加 3 个新 cron 任务']
```

---

### `extract_key_projects()`

提取关键项目信息。

**签名：**
```python
def extract_key_projects(content: str) -> list[dict]
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | str | 是 | 原始文本内容 |

**返回值：**
```python
[
    {
        "name": str,           # 项目名称
        "description": str,    # 项目描述
        "status": str,         # 当前状态
        "location": str        # 文件系统路径
    }
]
```

**示例：**
```python
from restore_context import extract_key_projects

content = """
Hermes Plan 是数据分析助手
Akasha Plan 是自主新闻系统
"""

projects = extract_key_projects(content)
for p in projects:
    print(f"{p['name']}: {p['status']}")
```

---

### `extract_ongoing_tasks()`

提取进行中的任务。

**签名：**
```python
def extract_ongoing_tasks(content: str) -> list[dict]
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | str | 是 | 原始文本内容 |

**返回值：**
```python
[
    {
        "task": str,       # 任务名称
        "status": str,     # 任务状态
        "detail": str      # 详细信息
    }
]
```

**示例：**
```python
from restore_context import extract_ongoing_tasks

content = "3个活跃 Isolated Sessions"

tasks = extract_ongoing_tasks(content)
print(tasks)
# [{'task': 'Isolated Sessions', 'status': 'Active', 'detail': '3 sessions running in parallel'}]
```

---

### `extract_timeline()`

提取历史操作时间线。

**签名：**
```python
def extract_timeline(
    content: str,
    period: str = "daily",
    days: int = 30
) -> dict
```

**参数：**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| content | str | 是 | - | 原始文本内容 |
| period | str | 否 | "daily" | 聚合周期："daily" \| "weekly" \| "monthly" |
| days | int | 否 | 30 | 包含天数 |

**返回值：**
```python
{
    "period": str,              # 使用的聚合周期
    "total_days": int,          # 覆盖的总天数
    "total_operations": int,    # 总操作数
    "timeline": [
        {
            "period_label": str,      # 周期标签
            "date_range": str,         # 日期范围
            "operations": list[str],  # 操作列表
            "projects": list[str],    # 相关项目
            "operations_count": int,  # 操作数量
            "highlights": list[str]   # 重要亮点
        }
    ]
}
```

**异常：**
| 异常类型 | 触发条件 |
|----------|---------|
| ValueError | period 参数无效 |

**示例：**
```python
from restore_context import extract_timeline

# 按周提取
timeline = extract_timeline(content, period="weekly", days=30)

for week in timeline['timeline']:
    print(f"📅 {week['period_label']}")
    for op in week['operations']:
        print(f"  - {op}")
```

---

### `get_context_summary()`

获取结构化上下文摘要（JSON 输出）。

**签名：**
```python
def get_context_summary(
    filepath: str,
    period: str = "daily",
    days: int = 30
) -> dict
```

**参数：**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| filepath | str | 是 | - | 上下文文件路径 |
| period | str | 否 | "daily" | 时间线聚合周期 |
| days | int | 否 | 30 | 时间线覆盖天数 |

**返回值：**
```python
{
    "success": bool,                  # 是否成功
    "filepath": str,                  # 文件路径
    "metadata": {
        "original_count": int,
        "compressed_count": int,
        "timestamp": str,
        "compression_ratio": float
    },
    "operations": list[str],
    "projects": list[dict],
    "tasks": list[dict],
    "timeline": dict,                 # extract_timeline() 返回
    "memory_highlights": list[str],
    "project_progress": dict
}
```

**示例：**
```python
from restore_context import get_context_summary

# 获取摘要
summary = get_context_summary('./compressed_context/latest_compressed.json')

if summary['success']:
    print(f"压缩率: {summary['metadata']['compression_ratio']}%")
    print(f"项目数: {len(summary['projects'])}")
    print(f"任务数: {len(summary['tasks'])}")
    
    for project in summary['projects']:
        print(f"- {project['name']}: {project['status']}")
```

---

### `compare_contexts()`

比较两个版本的上下文差异。

**签名：**
```python
def compare_contexts(old: str, new: str) -> dict
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old | str | 是 | 旧版本文件路径 |
| new | str | 是 | 新版本文件路径 |

**返回值：**
```python
{
    "success": bool,
    "added_projects": list[dict],
    "removed_projects": list[dict],
    "modified_projects": list[dict],
    "added_tasks": list[dict],
    "removed_tasks": list[dict],
    "modified_tasks": list[dict],
    "operations_added": list[str],
    "operations_removed": list[str],
    "operations_change": {
        "added_count": int,
        "removed_count": int,
        "net_change": int,
        "total_old": int,
        "total_new": int
    },
    "time_diff_hours": float,
    "message_count_change": dict
}
```

**示例：**
```python
from restore_context import compare_contexts

diff = compare_contexts('context_yesterday.json', 'context_today.json')

if diff['success']:
    print(f"⏱️  时间差: {diff['time_diff_hours']:.1f} 小时")
    print(f"➕ 新增项目: {len(diff['added_projects'])}")
    print(f"➖ 移除项目: {len(diff['removed_projects'])}")
    print(f"🔄 修改项目: {len(diff['modified_projects'])}")
    print(f"📝 新增操作: {len(diff['operations_added'])}")
```

---

### `format_diff_report()`

生成格式化的差异报告。

**签名：**
```python
def format_diff_report(diff: dict, old_file: str, new_file: str) -> str
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| diff | dict | 是 | compare_contexts() 返回的差异字典 |
| old_file | str | 是 | 旧文件路径 |
| new_file | str | 是 | 新文件路径 |

**返回值：**
| 类型 | 说明 |
|------|------|
| str | 格式化的报告字符串 |

**示例：**
```python
from restore_context import compare_contexts, format_diff_report

diff = compare_contexts('old.json', 'new.json')
report = format_diff_report(diff, 'old.json', 'new.json')

print(report)

# 或输出到文件
with open('diff_report.txt', 'w') as f:
    f.write(report)
```

---

## 变化检测函数

### `hash_content()`

计算内容哈希值。

**签名：**
```python
def hash_content(content: str) -> str
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | str | 是 | 要计算哈希的内容 |

**返回值：**
| 类型 | 说明 |
|------|------|
| str | SHA256 哈希值（十六进制） |

**示例：**
```python
from restore_context import hash_content

content = "上下文内容..."
hash_value = hash_content(content)
print(f"Hash: {hash_value}")
# Hash: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

---

### `detect_context_changes()`

检测上下文是否发生变化。

**签名：**
```python
def detect_context_changes(current: str, previous: str) -> bool
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| current | str | 是 | 当前内容 |
| previous | str | 是 | 之前的内容 |

**返回值：**
| 类型 | 说明 |
|------|------|
| bool | True 表示有变化，False 表示无变化 |

**示例：**
```python
from restore_context import detect_context_changes, hash_content

old_content = "旧的上下文内容"
new_content = "新的上下文内容"

if detect_context_changes(new_content, old_content):
    print("上下文已变化!")
else:
    print("上下文无变化")
```

---

### `load_cached_hash()`

从缓存加载保存的哈希值。

**签名：**
```python
def load_cached_hash(cache_file: str = None) -> Optional[str]
```

**参数：**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| cache_file | str | 否 | 默认缓存路径 | 缓存文件路径 |

**返回值：**
| 类型 | 说明 |
|------|------|
| str | 缓存的哈希值 |
| None | 缓存不存在或无法读取 |

**示例：**
```python
from restore_context import load_cached_hash

cached_hash = load_cached_hash()
if cached_hash:
    print(f"Cached hash: {cached_hash}")
else:
    print("No cached hash found")
```

---

### `save_cached_hash()`

保存内容哈希到缓存。

**签名：**
```python
def save_cached_hash(
    content_hash: str,
    context_file: str,
    cache_file: str = None
) -> bool
```

**参数：**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| content_hash | str | 是 | - | 要保存的哈希值 |
| context_file | str | 是 | - | 关联的上下文文件 |
| cache_file | str | 否 | 默认路径 | 缓存文件路径 |

**返回值：**
| 类型 | 说明 |
|------|------|
| bool | True 表示成功，False 表示失败 |

**示例：**
```python
from restore_context import hash_content, save_cached_hash

content = "上下文内容..."
content_hash = hash_content(content)

success = save_cached_hash(
    content_hash,
    './compressed_context/latest_compressed.json'
)
print(f"Saved: {success}")
```

---

## 自动恢复函数

### `check_and_restore_context()`

检查并自动恢复上下文。

**签名：**
```python
def check_and_restore_context(
    context_file: str,
    auto_mode: bool = False,
    quiet: bool = False,
    level: str = 'normal'
) -> dict
```

**参数：**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| context_file | str | 是 | - | 上下文文件路径 |
| auto_mode | bool | 否 | False | 是否自动模式 |
| quiet | bool | 否 | False | 是否静默模式 |
| level | str | 否 | "normal" | 恢复级别 |

**返回值：**
```python
{
    "changed": bool,           # 是否检测到变化
    "restored": bool,          # 是否执行了恢复
    "report": str,             # 恢复报告内容
    "summary": dict            # 上下文摘要
}
```

**示例：**
```python
from restore_context import check_and_restore_context

# 自动检测并恢复
result = check_and_restore_context(
    context_file='./compressed_context/latest_compressed.json',
    auto_mode=True,
    quiet=False,
    level='normal'
)

if result['changed'] and result['restored']:
    print(result['report'])
```

---

### `send_context_change_notification()`

发送上下文变化通知。

**签名：**
```python
def send_context_change_notification(
    context_file: str,
    auto_mode: bool = False
) -> bool
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| context_file | str | 是 | 上下文文件路径 |
| auto_mode | bool | 是 | 是否为自动模式 |

**返回值：**
| 类型 | 说明 |
|------|------|
| bool | True 表示通知发送成功 |

**示例：**
```python
from restore_context import send_context_change_notification

success = send_context_change_notification(
    './compressed_context/latest_compressed.json',
    auto_mode=True
)
print(f"Notification sent: {success}")
```

---

## Cron 集成函数

### `generate_cron_script()`

生成 cron 监控脚本。

**签名：**
```python
def generate_cron_script() -> str
```

**返回值：**
| 类型 | 说明 |
|------|------|
| str | 可执行的 Bash 脚本内容 |

**示例：**
```python
from restore_context import generate_cron_script

script_content = generate_cron_script()

with open('context_monitor.sh', 'w') as f:
    f.write(script_content)

print("Cron script generated")
```

---

### `install_cron_job()`

安装 cron 定时任务。

**签名：**
```python
def install_cron_job(
    script_path: str = None,
    interval_minutes: int = 5
) -> bool
```

**参数：**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| script_path | str | 否 | 默认脚本 | 监控脚本路径 |
| interval_minutes | int | 否 | 5 | 检查间隔（分钟） |

**返回值：**
| 类型 | 说明 |
|------|------|
| bool | True 表示安装成功 |

**示例：**
```python
from restore_context import install_cron_job

# 安装默认 cron（每5分钟）
success = install_cron_job()

# 安装自定义间隔
success = install_cron_job(interval_minutes=10)
```

---

## 辅助函数

### `calculate_compression_ratio()`

计算压缩率。

**签名：**
```python
def calculate_compression_ratio(
    original: Optional[int],
    compressed: Optional[int]
) -> Optional[float]
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| original | int | 是 | 原始消息数 |
| compressed | int | 是 | 压缩后消息数 |

**返回值：**
| 类型 | 说明 |
|------|------|
| float | 压缩率（百分比） |
| None | 输入无效时返回 |

**示例：**
```python
from restore_context import calculate_compression_ratio

ratio = calculate_compression_ratio(150, 25)
print(f"压缩率: {ratio:.1f}%")
# 压缩率: 16.7%
```

---

### `filter_context()`

过滤上下文内容。

**签名：**
```python
def filter_context(content: str, filter_pattern: str) -> str
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | str | 是 | 原始内容 |
| filter_pattern | str | 是 | 过滤关键词 |

**返回值：**
| 类型 | 说明 |
|------|------|
| str | 过滤后的内容 |

**示例：**
```python
from restore_context import filter_context

filtered = filter_context(content, "Hermes Plan")
print(filtered)
# 只包含与 "Hermes Plan" 相关的内容
```

---

### `normalize_content()`

标准化文本内容（使用 LRU 缓存）。

**签名：**
```python
def normalize_content(content: str) -> str
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | str | 是 | 原始内容 |

**返回值：**
| 类型 | 说明 |
|------|------|
| str | 小写化后的内容 |

**注意：** 此函数使用 LRU 缓存，重复调用相同内容会更快。

---

### `split_for_telegram()`

分割长消息用于 Telegram 发送。

**签名：**
```python
def split_for_telegram(
    content: str,
    max_length: int = 4000
) -> list[str]
```

**参数：**
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| content | str | 是 | - | 要分割的内容 |
| max_length | int | 否 | 4000 | 每块最大长度 |

**返回值：**
| 类型 | 说明 |
|------|------|
| list[str] | 分割后的消息块列表 |

**示例：**
```python
from restore_context import split_for_telegram

long_content = "..."  # 很长的内容
chunks = split_for_telegram(long_content, max_length=3000)

for i, chunk in enumerate(chunks):
    print(f"[{i+1}/{len(chunks)}] {len(chunk)} chars")
```

---

## 类型定义

### ContextSummary

`get_context_summary()` 返回的摘要类型。

```python
{
    "success": bool,
    "filepath": str,
    "metadata": {
        "original_count": Optional[int],
        "compressed_count": Optional[int],
        "timestamp": Optional[str],
        "compression_ratio": Optional[float]
    },
    "operations": List[str],
    "projects": List[Project],
    "tasks": List[Task],
    "timeline": Timeline,
    "memory_highlights": List[str],
    "project_progress": Dict
}
```

### Project

项目信息类型。

```python
{
    "name": str,
    "description": str,
    "status": str,
    "location": Optional[str]
}
```

### Task

任务信息类型。

```python
{
    "task": str,
    "status": str,
    "detail": str
}
```

### Timeline

时间线类型。

```python
{
    "period": str,                    # "daily" | "weekly" | "monthly"
    "total_days": int,
    "total_operations": int,
    "timeline": List[TimelineEntry]
}

TimelineEntry = {
    "period_label": str,
    "date_range": Optional[str],
    "operations": List[str],
    "projects": List[str],
    "operations_count": int,
    "highlights": List[str]
}
```

### ContextDiff

上下文差异类型。

```python
{
    "success": bool,
    "added_projects": List[Project],
    "removed_projects": List[Project],
    "modified_projects": List[dict],
    "added_tasks": List[Task],
    "removed_tasks": List[Task],
    "modified_tasks": List[dict],
    "operations_added": List[str],
    "operations_removed": List[str],
    "operations_change": dict,
    "time_diff_hours": float,
    "message_count_change": dict,
    "old_summary": dict,
    "new_summary": dict
}
```

---
