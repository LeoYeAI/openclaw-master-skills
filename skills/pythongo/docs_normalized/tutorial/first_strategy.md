# 第一个策略

## 准备工作 [#preparation]

工欲善其事，必先利其器，我们前面铺垫了这么多，终于来到编写策略代码的环节了，但是别急，我们还需要一个趁手的代码编辑器，编辑器可以帮我们检查在代码编写阶段出现的 BUG，可以帮我们统一代码的风格，还可以帮我们快速补全代码，让写代码效率更上一层楼。

我们推荐的编辑器是：Visual Studio Code [点击下载](https://code.visualstudio.com/Download)

安装完成之后，我们还需要下载以下扩展：

* 简体中文 [点击下载](https://marketplace.visualstudio.com/items?itemName=MS-CEINTL.vscode-language-pack-zh-hans) （汉化编辑器）

* Python [点击下载](https://marketplace.visualstudio.com/items?itemName=ms-python.python) 

* Pylance [点击下载](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)

* isort [点击下载](https://marketplace.visualstudio.com/items?itemName=ms-python.isort)

依次点击下载链接后，会打开对应的下载页面，我们看到「右侧侧边栏」，找到 「Resources」，点击 「Download Extension」，会开始下载扩展，扩展的文件后缀名是 `.vsix`

当我们把扩展下载好之后，会得到四个扩展文件，现在打开编辑器，点击左侧侧边栏「扩展」按钮，再点击「三个点」按钮，在菜单中选择「Install From VISX...」，中文则是「从 VISX 中安装...」，选择我们刚下载的四个扩展文件后点击「Install」，等待安装完成即可

![image](https://infinitrader-file.quantdo.com.cn/pythongo/img/v2/20240115114101.png)

注意：如果你打不开下载页面，或者觉得操作困难，可以跳过安装扩展的步骤，这些扩展只是让编辑器更好的支持 Python 语言，但不是必须的。

## 编写策略 [#develop-strategy]

我们知道如何加载策略后，也大体了解了一下运行原理，编辑器也准备好了，现在终于开始编写我们第一个策略了。

### 工作目录 [#work-directory]

我们首先需要用编辑器打开工作目录：

![image](https://infinitrader-file.quantdo.com.cn/pythongo/img/v2/20240322100514.png)

点击「策略管理」按钮后点击「文件夹」按钮打开策略路径，此时是位于 `self_strategy` 目录（策略路径）下，我们需要往上**两级**，按住 `Alt` + `上方向键` 两次，进入以 `InfiniTrader` 开头的目录，比如：`InfiniTrader_Simulation`，此时进入了无限易的主目录，我们可以在这个目录下看到 `pyStrategy` 文件夹，这是 PythonGO 整体的工作目录，**右键该目录**：

* 如果是 Windows 10：在弹出的菜单中点击「通过 Code 打开」

* 如果是 Windows 11：在弹出的菜单中点击「显示更多选项」，再点击「通过 Code 打开」

* 如果没有「通过 Code 打开」，则自行打开编辑器后，把 `pyStrategy` 文件夹拖入到编辑器中

```text
InfiniTrader_Simulation/
  dat/
    future/
      gold/
        image/
          pyStrategy/
            demo/
              instance_files/
                pythongo/
                  self_strategy/
```

之后的开发会一直在该工作目录中进行。

### 创建策略 [#create-strategy]

在左侧文件栏中选中 `self_strategy` 文件夹，再点击「新建文件」按钮，在出现的输入框中输入策略文件名，这里我们取名 `DemoTest.py`（注意不要和自带的策略重名）

![image](https://infinitrader-file.quantdo.com.cn/pythongo/img/v2/20240115145326.png)

当然你也可以直接在 `self_strategy` 文件夹直接右键新建 `.py` 策略文件

### 编写代码 [#coding]

现在我们来写一个最简单的一旦运行策略就按照无限易 PythonGO 窗口的参数下单的策略

#### 定义参数映射 [#def-params]

参数映射，是指可以通过无限易 PythonGO 窗口参数栏对策略的参数进行修改的映射操作

现阶段，我们的参数映射都是通过 `pydantic` 这个强大的数据验证库，它可以**根据我们定义的类型注释**严格控制数据类型，在我们写代码的过程中就可以感受到该库的强大之处。

我们通过一个「参数映射模型」即可完成映射

```py filename="DemoTest.py" {4,7-13}
from typing import Literal

# 从 base 库中导入定义参数和状态映射模型必须的三个方法
from pythongo.base import BaseParams, BaseState, Field

class Params(BaseParams):
    """参数映射模型"""
    exchange: str = Field(default="", title="交易所代码")
    instrument_id: str = Field(default="", title="合约代码")
    order_price: int | float = Field(default=0, title="报单价格")
    order_volume: int = Field(default=1, title="报单手数")
    order_direction: Literal["buy", "sell"] = Field(default="buy", title="报单方向")
```

上面的代码表示：

* 我们自己的参数映射模型叫做 `Params`，继承自 `BaseParams`

* 我们想从无限易 PythonGO 窗口参数栏传入定义的这 5 个值（或者说修改 5 个值）

* 类型注释在参数映射模型中是一定要写的，**所有的值类型都会按照定义的类型注释被解析和自动转换**，其中 `Literal` 的作用是表示这个变量只允许使用定义好的字面值，当前代码表示 `order_direction` 只允许使用 `buy` 或者 `sell` 这两个字符串

* `Field` 用来自定义元数据并将其添加到参数映射模型的字段中

* `default`（必填）定义这个参数默认值，相当于 `self.exchange = ""{:py}`

* `title`（必填）定义这个参数的中文名，会在无限易 PythonGO 窗口显示

效果如图所示：

![image](https://infinitrader-file.quantdo.com.cn/pythongo/img/v2/20240116103532.png)

#### 定义状态映射 [#def-state]

状态映射，是指可以通过无限易 PythonGO 窗口状态栏对策略的参数或变量进行实时查看的映射操作（如没该需求可以不定义）

定义方法和参数映射是一样的，通过一个「状态映射模型」即可完成映射

```py filename="DemoTest.py" {2,5-7}
# 从 base 库中导入定义参数和状态映射模型必须的三个方法
from pythongo.base import BaseParams, BaseState, Field

class State(BaseState):
    """状态映射模型"""
    order_id: int | None = Field(default=None, title="报单编号")
```

上面的代码表示：

* 我们自己的状态映射模型叫做 `State`，继承自 `BaseState`

* 我们想从无限易 PythonGO 窗口状态栏查看报单编号（`order_id`）的值（注意：这个报单编号需要我们自己赋值，和报单成功后的返回的报单编号没有主动映射关系，仅仅是同名，你也可以定义为任意名称）

* 其他和参数映射说明一样

效果如图所示：

![image](https://infinitrader-file.quantdo.com.cn/pythongo/img/v2/20240116110046.png)

#### 定义策略类 [#def-class]

当我们把映射模型定义好之后，就要开始写策略类了

根据规范 [策略规范 - 导入父类](/styleguide/strategy_rules#import) 导入我们需要的父类基础策略模版 `BaseStrategy`，然后基于我们之前学过的知识 [运行原理 - 加载策略](./how_it_works.mdx#load)，我们知道了「策略类名」要和「策略文件名」保持一致：

```py filename="DemoTest.py" {2,5-6}
# 从 base 库中导入基础策略模版 BaseStrategy 
from pythongo.base import BaseParams, BaseState, BaseStrategy, Field

class DemoTest(BaseStrategy):
    """我的第一个策略"""
    ...
```

根据 [PythonGO 代码规范](../styleguide/style_rules.mdx#docstring-function)，我们还需要给策略写一个函数文档字符串，来告诉无限易这个策略的描述

效果如图所示：

![image](https://infinitrader-file.quantdo.com.cn/pythongo/img/v2/20240322100955.png)

#### 实例化映射模型 [#init-map-models]

上面定义好了两个映射模型，也定义好了策略类，现在我们把映射模型实例化，作为策略的实例属性，这样才可以在策略中获取到定义的映射数据

```py filename="DemoTest.py" {24-25} copy
from typing import Literal

from pythongo.base import BaseParams, BaseState, BaseStrategy, Field

class Params(BaseParams):
    """参数映射模型"""
    exchange: str = Field(default="", title="交易所代码")
    instrument_id: str = Field(default="", title="合约代码")
    order_price: int | float = Field(default=0, title="报单价格")
    order_volume: int = Field(default=1, title="报单手数")
    order_direction: Literal["buy", "sell"] = Field(default="buy", title="报单方向")

class State(BaseState):
    """状态映射模型"""
    order_id: int | None = Field(default=None, title="报单编号")

class DemoTest(BaseStrategy):
    """我的第一个策略"""
    def __init__(self) -> None:
        super().__init__()
        self.params_map = Params()
        self.state_map = State()
```

#### 定义回调 [#def-pythongo-callback]

在 PythonGO 的父类基础策略模版中，以 `on` 开头的函数都是回调函数

在 [运行原理](./how_it_works) 中，我们大致的了解了回调函数，那在当前的示例中我们只需要用到三个回调函数，根据 [策略规范 - 回调函数](../styleguide/strategy_rules.mdx#callback) 按顺序定义如下：

##### `on_start()`

[查看启动策略回调定义](../modules/pythongo_base.mdx#on_start)

我们的策略的逻辑是一旦运行就按照无限易 PythonGO 窗口的参数下单，那下单函数就应该写在本回调中

我们使用 [报单函数 - send_order](../modules/pythongo_base.mdx#send_order) 来进行报单操作，对应的报单数据我们从参数 `self.params_map` 中获取，得到的报单编号，我们赋值给状态映射模型中的 `order_id`，然后需要调用 `update_status_bar` 函数才可以刷新状态栏的值：

```py filename="DemoTest.py" {4-10,12}
def on_start(self) -> None:
    super().on_start()

    self.state_map.order_id = self.send_order(
        exchange=self.params_map.exchange,
        instrument_id=self.params_map.instrument_id,
        volume=self.params_map.order_volume,
        price=self.params_map.order_price,
        order_direction=self.params_map.order_direction
    )

    self.update_status_bar()
```

[`update_status_bar` 函数定义](../modules/pythongo_base.mdx#update_status_bar)

##### `on_stop()`

[查看暂停策略回调定义](../modules/pythongo_base.mdx#on_stop)

在暂停回调中，我们输出一句自定义信息

```py filename="DemoTest.py" {3}
def on_stop(self) -> None:
    super().on_stop()
    self.output("我的第一个策略暂停了")
```

##### `on_order()`

[查看报单变化回调定义](../modules/pythongo_base.mdx#on_order)

在报单变化回调中，我们只需要输出看看报单后回调收到的报单数据（`OrderData`）信息。要注意的是，参数 `order` 是一个实例对象，不是字典对象，所以他的取值是用 `.` 取值的，比如 `order.exchange`，但是我们直接输出 `order`，显示的内容确是字典，这是因为我们对这个数据对象做了处理，如果没做处理的话，看到的是内存地址 `<order.OrderData at 0x96b06c0>`

```py filename="DemoTest.py" {5}
from pythongo.classdef import OrderData

def on_order(self, order: OrderData) -> None:
    super().on_order(order)
    self.output("报单信息：", order)
```

#### 完整代码 [#full-code]

是的，一个简单的策略就完成了，代码不多，希望你可以仔细阅读这些代码

现在这个策略会根据你在无限易 PythonGO 窗口填写的参数信息（交易所代码，合约代码，报单价格，报单手数，报单方向）来进行报单，最终的代码是这样：

```py filename="DemoTest.py" copy
from typing import Literal

from pythongo.base import BaseParams, BaseState, BaseStrategy, Field
from pythongo.classdef import OrderData

class Params(BaseParams):
    """参数映射模型"""
    exchange: str = Field(default="", title="交易所代码")
    instrument_id: str = Field(default="", title="合约代码")
    order_price: int | float = Field(default=0, title="报单价格")
    order_volume: int = Field(default=1, title="报单手数")
    order_direction: Literal["buy", "sell"] = Field(default="buy", title="报单方向")

class State(BaseState):
    """状态映射模型"""
    order_id: int | None = Field(default=None, title="报单编号")

class DemoTest(BaseStrategy):
    """我的第一个策略"""
    def __init__(self) -> None:
        super().__init__()
        self.params_map = Params()
        self.state_map = State()

    def on_order(self, order: OrderData) -> None:
        super().on_order(order)
        self.output("报单信息：", order)

    def on_start(self) -> None:
        super().on_start()

        self.state_map.order_id = self.send_order(
            exchange=self.params_map.exchange,
            instrument_id=self.params_map.instrument_id,
            volume=self.params_map.order_volume,
            price=self.params_map.order_price,
            order_direction=self.params_map.order_direction
        )

        self.update_status_bar()

    def on_stop(self) -> None:
        super().on_stop()
        self.output("我的第一个策略暂停了")
```

然后按照 [操作入门](./quick_start.mdx) 来加载我们刚写的第一个策略即可，快去试一试！
