# qvxianjiuguo-skills (曲线救国)

机票模糊搜索工具，支持去哪儿、携程、飞猪、同程四个平台。

## 开发命令

```bash
uv sync                    # 安装依赖
uv run ruff check .        # Lint 检查
uv run ruff format .       # 代码格式化
```

## 架构

```
src/qvxianjiuguo/
├── __init__.py           # 包入口
├── cli.py                # CLI 命令行入口
├── chrome_launcher.py    # Chrome 进程管理
└── flight/
    ├── __init__.py
    ├── search.py         # 机票搜索核心逻辑
    ├── types.py          # 类型定义
    ├── ground_transport.py # 地面交通计算
    └── platforms/
        ├── __init__.py
        └── platforms.py  # 四个平台处理器

data/
├── airports/             # 机场数据
│   ├── airports.json
│   ├── nearby-airports-*.json
│   └── ...
└── flight-matrix/        # 航班矩阵数据
    ├── flight-matrix.json
    └── ...

skills/
└── qvxian-flight-search/
    └── SKILL.md          # AI Agent 技能定义
```

## CLI 子命令

| 子命令 | 说明 |
|--------|------|
| `flight-lookup --city <城市名>` | 查询机场信息 |
| `flight-nearby --airport <代码> --range <km>` | 查询附近机场 |
| `flight-search --departure <出发地> --destination <目的地> --date <日期> --platform <平台>` | 机票搜索 |
| `flight-check-login --platform <平台>` | 检查平台登录状态 |

## 调用方式

```bash
# 启动 Chrome
python -m qvxianjiuguo.chrome_launcher

# 查询机场
python -m qvxianjiuguo.cli flight-lookup --city "重庆"

# 查询附近机场
python -m qvxianjiuguo.cli flight-nearby --airport CKG --range 350

# 机票搜索
python -m qvxianjiuguo.cli flight-search \
  --departure "重庆" \
  --destination "秦皇岛" \
  --date "2026-02-15" \
  --platform qunar

# 检查登录状态
python -m qvxianjiuguo.cli flight-check-login --platform qunar
```

## 代码规范

- 行长度上限 100 字符
- 完整 type hints
- CLI exit code：0=成功，1=错误
- JSON 输出 `ensure_ascii=False`