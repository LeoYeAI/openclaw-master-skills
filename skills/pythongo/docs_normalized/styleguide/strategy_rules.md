# 策略规范

过去我们的框架没有一个统一的代码规范，导致每个人的代码都长得不一样，现在新版本不仅规范了框架代码，还需要规范策略代码。

## 导入父类 [#import]

通过把 K 线图相关代码拆分出去，我们得到了两个基础策略模版类：

* `pythongo.base.BaseStrategy`

* `pythongo.ui.BaseStrategy`

### `pythongo.base`

本模块定义了完整的策略模版，也封装了从无限易取数据的方法

当我们的策略完全不需要用到 K 线图的时候则导入本模块中的 `BaseStrategy`，并继承该类

```python {1}
from pythongo.base import BaseStrategy

class Demo(BaseStrategy):
    ...
```

### `pythongo.ui`

本模块继承自上面 `pythongo.base` 中的 `BaseStrategy`，但额外包含了所有的 K 线图代码以及处理逻辑

当我们的策略需要使用到 K 线图的时候则导入本模块中的  `BaseStrategy`，并继承该类

```python {1}
from pythongo.ui import BaseStrategy

class Demo(BaseStrategy):
    ...
```

该类会自动处理 K 线图初始化等相关操作，使得所有的策略代码不再需要手动处理线图的启动、显示、关闭等操作

## 初始化 [#init]

### 自定义变量 [#custom-var]

很多时候我们需要定义一些自定义变量，用来实现策略更复杂的操作，这些变量就是实例变量，我们和正常写代码一样，直接定义在 `self.__init__` 中，对于默认值为 `None{:py}` 或者为对象的变量，应该写上类型注释

```python copy {6-8}
class Demo(BaseStrategy):
    def __init__(self) -> None:
        super().__init__()

        # 自定义变量
        self.global_var_name: str | None = None
        self.global_var_int = 1
        self.test_string = ""
```

## 线图指标定义 [#def-ui-indicator]

当我们使用 K 线图组件时，需要定义线图上显示的指标，现在我们有了更方便的定义方法

`@property{:py}` 装饰器可以把一个类方法装饰成类属性，在我们定义线图显示指标的时候，使用这个装饰器再合适不过了，因为每次调用这个属性，都会去使用最新的指标数据，而不需要自己对这个属性做任何赋值操作

下面定义的两个属性，是以方法来定义的，但可以当做属性调用，所以我们可以实现更进阶的操作

### 主图指标 [#main-indicator]

主图指标使用属性名 `main_indicator_data` 定义

```python copy {7-8,10-16}
from pythongo.ui import BaseStrategy

class Demo(BaseStrategy):
    def __init__(self) -> None:
        super().__init__()

        self.fast_ma = 0.0
        self.slow_ma = 0.0

    @property
    def main_indicator_data(self) -> dict[str, float]:
        """主图指标"""
        return {
            "MA0": self.fast_ma,
            "MA1": self.slow_ma,
        }
```

### 副图指标 [#sub-indicator]

副图指标使用属性名 `sub_indicator_data` 定义

```python copy {7-9,11-18}
from pythongo.ui import BaseStrategy

class Demo(BaseStrategy):
    def __init__(self) -> None:
        super().__init__()

        self.k = 0.0
        self.d = 0.0
        self.j = 0.0

    @property
    def sub_indicator_data(self) -> dict[str, float]:
        """副图指标"""
        return {
            "K": self.k,
            "D": self.d,
            "J": self.j,
        }
```

### 进阶操作 [#high-level-code]

在上面定义指标的例子中，`KDJ` 指标还好，如果是 `MA` 指标，我们软件一般都会显示为 `MA10`、 `MA20` 这种带周期的名称，但是在策略中，我们已经把指标名称定义为 `MA0` 和 `MA1`，且不会再更改了

这就导致即使我们更改了指标的周期，线图上显示的指标名字还是不会变，我们不能很清楚的知道现在显示的是什么周期的指标

这个时候装饰器就起作用了，还记得我们之前说的：「装饰器可以把一个类方法装饰成类属性」吗？既然我们定义的不是属性，而是方法，那就可以在方法里实现更新指标名称的操作了

```python copy {7-8,14,16-17,23-24}
from pythongo.base import BaseParams, Field
from pythongo.ui import BaseStrategy

class Params(BaseParams):
    """参数映射模型"""
    fast_period: int = Field(default=5, title="快均线周期", ge=2)
    slow_period: int = Field(default=20, title="慢均线周期")

class Demo(BaseStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.params_map = Params()

        self.fast_ma = 0.0
        self.slow_ma = 0.0

    @property
    def main_indicator_data(self) -> dict[str, float]:
        """主图指标"""
        return {
            f"MA{self.params_map.fast_period}": self.fast_ma,
            f"MA{self.params_map.slow_period}": self.slow_ma,
        }
```

这样，从 PythonGO 窗口传进来的快均线周期和慢均线周期就会在 `self.main_indicator_data` 调用后转成一个新的字典：

```json
{
    "MA5": 0.0,
    "MA20": 0.0
}
```

其中 `5` 和 `20` 是取的参数映射模型中 `self.params_map.fast_period` 和 `self.params_map.slow_period` 的值，我们通过 `f-string` 配合 `@property{:py}` 装饰器，实现了在更改指标周期后，线图上显示的指标名是 `MA` + 更改后的指标周期

## 回调函数 [#callback]

在自己编写策略的时候，回调函数应该按照以下顺序定义，使用不到的回调函数允许不定义

```python
from pythongo.base import BaseStrategy

class Demo(BaseStrategy):
    def __init__(self) -> None:
        super().__init__()

    def on_init(self, ...) -> None:
        super().on_init(...)

    def on_start(self, ...) -> None:
        super().on_start(...)

    def on_stop(self, ...) -> None:
        super().on_stop(...)

    def on_tick(self, ...) -> None:
        super().on_tick(...)

    def on_contract_status(self, ...) -> None:
        super().on_contract_status(...)

    def on_order(self, ...) -> None:
        super().on_order(...)

    def on_cancel(self, ...) -> None:
        super().on_cancel(...)

    def on_order_trade(self, ...) -> None:
        super().on_order_trade(...)

    def on_trade(self, ...) -> None:
        super().on_trade(...)

    def on_error(self, ...) -> None:
        super().on_error(...)
```

注意：所有回调函数，一定要使用 `super()` 来调用父类的回调函数

## 函数调用 [#call-function]

调用函数时，如果函数的参数超过两个，则需要在入参的时候填写参数名，这点在[代码规范](./style_rules.mdx)中已经强调了

```python
def foo(a: int, b: int, c: int) -> int:
    return a + b + c

# 正确
foo(a=1, b=2, c=3)

# 错误
foo(1, 2, 3)
```
