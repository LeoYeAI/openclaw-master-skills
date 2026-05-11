# pythongo.ui

本模块包含了绘画 K 线图 UI 的代码，鉴于代码复杂且后续可能使用别的方式展示 K 线图，不过多介绍，有需求的话可以自行查阅代码，这里仅挑选部分类说明

> [!ERROR]
> 注意，如策略需要使用 K 线图 UI，则一定要使用本模块中的 `BaseStrategy`，详情查阅：[策略规范 - 导入父类](/styleguide/strategy_rules#import)

## `BaseStrategy`

带 UI 的基础策略模版

自动处理 UI 逻辑，比如启动显示，暂停隐藏等

### `widget`

| 类型 | 描述 |
|---|---|
| `KLWidget` | 实例化的 K 线组件 |

### `main_indicator_data`

注意：不能直接对该属性赋值，而应该自行定义该属性

| 类型 | 描述 |
|---|---|
| `dict[str | float |
| ` |
| 主 | 图 | 指 | 标 | 数 | 据 |

### `sub_indicator_data`

注意：不能直接对该属性赋值，而应该自行定义该属性

| 类型 | 描述 |
|---|---|
| `dict[str | float |
| ` |
| 副 | 图 | 指 | 标 | 数 | 据 |

> [!INFO]
> 具体关于指标数据的定义，请查阅 [策略规范 - 线图指标定义](/styleguide/strategy_rules#def-ui-indicator)

## `KLWidget`

K 线组件

### `recv_kline()`

收取 K 线、价格信号、指标数据，并将 K 线更新在线图上

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `data` | `dict[str | float | KLineData |
| ` |
| 数 | 据 | 容 | 器 |
| 必 | 填 |

data 包含 K 线数据、价格信号、指标数据

举例：`{"kline": kline_data, "signal_price": 0.0, "MA": 0.0}`

## 模块说明 [#modules-description]

### `crosshair.py`

该模块是十字光标模块，可以显示通过移动鼠标后到达的 K 线坐标对应的 K 线数据

### `drawer.py`

绘画 K 线图 UI 的主模块，使用 PyQt 构建了整个线图的 UI

### `widget.py`

连接策略与 `drawer.py` 的桥梁，其中包含了带 UI 功能的基础策略模版，还有 `KLWidget` 简化库，可以将 K 线数据传递给 UI，并更新绘图
