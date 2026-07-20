# Productivity Automation Kit - 效率自动化工具箱

## 🚀 快速开始

```bash
# 进入scripts目录
cd scripts

# 数据自动化
python data_automation.py --input data.json --output result.json

# 日程规划
python schedule_planner.py --tasks tasks.json

# 任务提醒
bash task_reminder.sh
```

## 目录结构

```
productivity-automation-kit/
├── SKILL.md                    # 功能说明文档
├── README.md                   # 本文件
├── scripts/
│   ├── data_automation.py     # 数据自动化（ETL）
│   ├── schedule_planner.py     # 日程规划
│   └── task_reminder.sh        # 任务提醒脚本
├── references/
│   └── workflow-templates.md   # 工作流模板
└── schemas/
    └── task-schema.json       # 任务数据格式
```

## 主要模块

### data_automation.py
```bash
# 基本用法
python data_automation.py --input data.json --output cleaned.json

# 带配置
python data_automation.py --input data.csv --type csv --config config.json

# 指定指标
python data_automation.py --input data.json --metrics count sum average
```

### schedule_planner.py
```bash
# 生成日程
python schedule_planner.py --days 7 --output schedule.json

# 从任务列表生成
python schedule_planner.py --tasks tasks.json --output schedule.json
```

### task_reminder.sh
```bash
# 基本运行
bash task_reminder.sh

# 指定任务文件
TASK_FILE=tasks.json bash task_reminder.sh
```

## 工作流模板

参见 `references/workflow-templates.md`

## 依赖

- Python 3.7+
- Bash (Linux/macOS) 或 Git Bash (Windows)
