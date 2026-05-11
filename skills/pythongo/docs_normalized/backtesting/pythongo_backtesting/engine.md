# pythongo.backtesting.engine

## `run()`

回测运行主函数

参数：

| 参数名 | 类型 | 描述 | 默认值 |
|---|---|---|---|
| `config` | `Config` | 回测配置 | 必填 |
| `strategy_cls` | `BaseStrategy` | 实例化策略 | 必填 |
| `strategy_params` | `BaseParams` | 实例化参数映射模型 | 必填 |
| `start_date` | `str` | 回测开始日期 | 必填 |
| `end_date` | `str` | 回测结束日期（不包括） | 必填 |
| `initial_capital` | `int | float` | 回测初始资金 | 1000000 |
