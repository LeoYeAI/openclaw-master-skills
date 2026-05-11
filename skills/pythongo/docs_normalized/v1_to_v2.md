# 迁移指南

本指南帮助你从老版本 PythonGO 更新到新版本 PythonGO，但并不是所有方法都有代替的方法，有些方法我们已经删除，所以只能大致的例举出一些需要改动的东西

建议阅读本迁移指南前先阅读所有的文档，对新版本框架有个大概的了解，当然，我们的建议还是按照文档重写你的策略，这才是最快捷方便的

* `CtaTemplate` -> `pythongo.base.BaseStrategy` 或者 `pythongo.ui.BaseStrategy`，[策略规范 - 导入父类](./styleguide/strategy_rules.mdx#import)

* `vtObject` -> `pythongo.classdef` 参考 「深入框架 - pythongo.classdef」

* `utils` -> `pythongo.utils` 参考 [深入框架 - pythongo.utils](./modules/pythongo_utils)

* `indicators` -> `pythongo.indicator`，参考 [深入框架 - pythongo.indicator](./modules/pythongo_indicator)

* 「参数映射表」`paramMap` 改为「参数映射模型」，参考 [教程 - 第一个策略 - 定义参数映射](./tutorial/first_strategy.mdx#def-params)

* 「状态映射表」`varMap` 改为「状态映射模型」，参考 [教程 - 第一个策略 - 定义状态映射](./tutorial/first_strategy.mdx#def-state)

* 回调函数使用下划线命名，参考 [风格指南 - 策略规范 - 回调函数](./styleguide/strategy_rules.mdx#callback)，或者 [深入框架 - pythongo.base - BaseStrategy](./modules/pythongo_base.mdx#basestrategy)

* `symbol` -> `instrument_id`，所有的「合约代码」变量名都统一为 `instrument_id`

* `instrument` -> `instrument_id`，要特别注意一些函数的入参的合约代码变量名也统一了

* 报单函数全部删除，改为 `send_order`，参考 [深入框架 - pythongo.base - BaseStrategy - send_order](./modules/pythongo_base#send_order)

* 删除 `regTimer` 定时器，请使用 `pythongo.utils.Scheduler` 模块，参考 [深入框架 - pythongo.utils - Scheduler](./modules/pythongo_utils#scheduler)

* 删除 `ArrayManager` 和 `BarManager`，合成 K 线请使用 `KLineGenerator`，参考 [深入框架 - pythongo.utils - KLineGenerator](./modules/pythongo_utils#kline-generator)

* 删除 `self.loadBar` 和 `self.loadDay`

* 分钟级 K 线合成器 `MinKLineGenerator` 改名为 `KLineGenerator`

* 秒级 K 线生成器 `KLineGenerator` 改名为 `KLineGeneratorSec`

* `self.get_contract` 改名为 `self.get_instrument_data`

* 所有的模块都在 `pythongo` 中，建议仔细阅读本文档的「深入框架」章节

注意，这里可能并没有罗列出所有需要更改的地方，因为新版 PythonGO 是完全重写的，所以我们的建议是按照全部文档来重写自己的策略。
