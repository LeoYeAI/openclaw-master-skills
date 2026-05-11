# PythonLAB 回测 - 使用教程

## 准备工作 [#preparation]

要使用 PythonLAB 回测功能，我们需要一个 [QuantFair 模拟帐号](https://quantfair.quantdo.com.cn/)，如果没有的话可以去注册，否则无法使用回测功能。

有了 QuantFair 模拟帐号还不够，我们还需要去[个人中心](https://quantfair.quantdo.com.cn/user/dashboard)申请密钥。申请完成后会得到 `AccessKey` 和 `AccessSecret`，后面我们会把密钥配置在回测程序中。

**最后，在数据服务一栏中，申请免费试用即可。** 否则会提示 `NO_AVAILABLE_ORDER`。

## 注意事项 [#notice]

* 只支持**新版 PythonGO**

* 回测使用的历史数据是 **Tick 数据**

* 回测撮合模式使用简单的**见价成交**

* 回测结果仅供参考，不代表实盘结果

* 无法回测标准套利合约

* 没有线图窗口

## 编写代码 [#coding]

写代码之前需要使用编辑器打开正确的工作目录，具体操作方法可以参考[教程 - 第一个策略 - 工作目录](/tutorial/first_strategy#work-directory)。

### 入口文件 [#create-entry-file]

我们需要创建回测入口文件 `app.py`，该文件必须位于 `pyStrategy` 目录下，与 `pythongo` 目录同级，如下所示：

```text
InfiniTrader_Simulation/
  pyStrategy/
    demo/
      DemoDMA.py
    instance_files/
      pythongo/
        self_strategy/
          app.py
```

注意：入口文件可以是任意文件名

### 导入 [#import]

首先，我们需要导入我们自己写的**策略类**，以及**参数映射模型**，后续会把这两个类传递给运行回测

```python filename="app.py"
from demo.DemoDMA import DemoDMA, Params
```

然后我们再导入回测运行主函数 `run`，和回测配置模型 `Config`

```python filename="app.py"
from pythongo.backtesting.engine import run
from pythongo.backtesting.models import Config
```

### 设置策略参数 [#set-strategy-params]

除了导入代码以外，其余所有的代码，都必须写在 `if __name == "__main__"{:py}` 下

```python filename="app.py" {6-12}
from demo.DemoDMA import DemoDMA, Params
from pythongo.backtesting.engine import run
from pythongo.backtesting.models import Config

if __name__ == "__main__":
    params = Params(
        exchange="SHFE",
        instrument_id="ag2604",
        fast_period=5,
        slow_period=20
    )

    ...
```

根据该参数映射模型定义的参数，我们只传入四个参数，其余参数使用默认值。

在自己编写代码的时候，实例参数请按照实际情况填写。

这一步相当于在无限易 PythonGO 窗口中的实例参数栏[填写对应的参数值](/tutorial/quick_start#fill-params)

### 设置回测参数 [#set-backtesting-params]

策略的参数设置好之后，我们需要设置回测的参数，其中必填的参数是 `access_key` 和 `access_secret`，这两个参数，就是我们前面提到的申请后的密钥，请规范填写

```python filename="app.py" {9-12}
from demo.DemoDMA import DemoDMA, Params
from pythongo.backtesting.engine import run
from pythongo.backtesting.models import Config

if __name__ == "__main__":
    ...

    backtesting_config = Config(
        access_key="",
        access_secret=""
    )

    ...
```

其余参数（例如手续费）请查看[回测 - pythongo.backtesting - models](/backtesting/pythongo_backtesting/models#config)，如有需要可自行设置。

### 设置运行参数 [#set-backtesting-config]

运行参数告诉回测程序运行所需的参数

* `config` 传入上面定义的回测参数 `backtesting_config`

* 策略类 `strategy_cls` 需要传入实例化后的类，也就是带上括号

* `strategy_params` 传入上面定义的策略参数

* `start_date` 和 `end_date` 代表回测数据开始播放的日期和结束日期（不包含结束日期）

* `initial_capital` 设置初始资金，默认是 100 万

具体参数请查看[回测 - pythongo.backtesting - engine](/backtesting/pythongo_backtesting/engine#run)

```python filename="app.py" {9-16}
from demo.DemoDMA import DemoDMA, Params
from pythongo.backtesting.engine import run
from pythongo.backtesting.models import Config

if __name__ == "__main__":
    ...

    run(
        config=backtesting_config,
        strategy_cls=DemoDMA(),
        strategy_params=params,
        start_date="2025-08-01",
        end_date="2025-08-05",
        initial_capital=100_0000
    )
```

### 完整代码 [#full-code]

回测上期所的 `ag2604` 合约，快均线周期 `5`，慢均线周期 `20`，Tick 数据从 `2025-08-01` 开始，到 `2025-08-05` 结束（不包含结束日期），初始资金 100 万。

```python filename="app.py" copy
from demo.DemoDMA import DemoDMA, Params
from pythongo.backtesting.engine import run
from pythongo.backtesting.models import Config

if __name__ == "__main__":
    params = Params(
        exchange="SHFE",
        instrument_id="ag2604",
        fast_period=5,
        slow_period=20
    )

    backtesting_config = Config(
        access_key="",
        access_secret=""
    )

    run(
        config=backtesting_config,
        strategy_cls=DemoDMA(),
        strategy_params=params,
        start_date="2025-08-01", # 注意，年月日要求 yyyy-mm-dd 格式，月和日如果不足两位，则需要补充一个 0
        end_date="2025-08-05",
        initial_capital=100_0000
    )
```

## 运行 [#run]

回测的运行，实际上就和正常的 Python 脚本一样了，直接运行 `.py` 文件即可，这里简单写一下运行 Python 文件的**两种方法**，任选其一：

* 在 Visual Studio Code 编辑器中，确保当前正在编辑 `app.py`，如果安装了 Python 的扩展（如没有，请查看[教程 - 第一个策略 - 准备工作](/tutorial/first_strategy#preparation)），直接右键代码区域，在右键菜单中找到 `Run Python` 或者 `运行 Python`，在二级菜单中再点击 `Run Python File in Terminal` 或者 `在终端中运行 Python 文件`，即可开始回测。

* 在命令行中切换到 PythonGO 的工作目录，执行 `python app.py` 即可开始回测，`app.py` 是回测入口文件。
