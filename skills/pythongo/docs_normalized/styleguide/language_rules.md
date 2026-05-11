# 语言规范

任何代码语言都有代码规范，有了规范才能让我们写出清晰易读易懂的代码，以下列出 PythonGO 的语言规范，实际上就是 Python 的语言规范。
 

> [!INFO]
> 代码编辑器统一使用 [Visual Studio Code](https://code.visualstudio.com/download)

## 导入 [#import]

正常情况下，导包使用 `import{:py}` 语句

```python

pythongo.utils.KLineGenerator(...)
```

可以适当使用 `from{:py}` 语句来省略太长的包名

```python
from pythongo import utils

utils.KLineGenerator(...)
```

或者直接导入包中的对象

```python
from pythongo.utils import KLineGenerator

KLineGenerator(...)
```

### 导入顺序 [#import-sort]

按照如下导入顺序来编写你的 `import{:py}` 语句， 标准库 -> 第三方库 -> 本地库，例如：

```python
# 标准库

from datetime import datetime

# 第三方库

# 本地库

```

### 注意事项 [#import-tips]

严格禁止使用星号 `*` 导入

```python
from pythongo import *
```

缩写导入只适用于库的缩写是约定俗成的，比如 `numpy` 和 `pandas`，其他所有库都不建议使用缩写导入

```python

```

## 异常 [#exception]

任何报错都有解决方法，对于 `try / except{:py}` 语句要严格控制使用频率。

## True / False 的求值 [#true-false-condition]

Python 在计算布尔值时会把一些值视为 `False{:py}`。简单来说，所有的「空」值都是假值。 因此， `0, None, [], {}, ""{:py}` 作为布尔值使用时相当于 `False{:py}`

当我们判断一个值 `foo` 是否为 `True{:py}` 或者 `False{:py}` 时，可以直接使用 `if foo:{:py}`

但是当值 `foo` 可能为 `None{:py}` 值时，一定要使用 `if foo is None:{:py}`（或者 `is not None{:py}`）来判断 `None{:py}` 值，因为在某些情况下，`0{:py}` 值并不代表 `False{:py}`

当你想条件为 `False{:py}` 时进入判断，应该写成

```python
if foo is False:
    # do something
```

因为这样明确了当 `foo` 值或结果为 `False{:py}` 时才进入 `if{:py}` 判断，不会造成歧义。

## 类型注释 [#type-hints]

由于 Python 是动态语言，一个变量被赋值后，运行时可以改变该变量的类型，所以有时候当变量的类型被改变后，我们的编辑器不能识别该变量的类型，导致无法使用编辑器的函数自动补全功能。

而在新版本的 Python 中，我们可以通过类型注释来实现给每个变量定义一个类型，提高代码可读性和可维护性。

以下代码告诉我们 `foo` 函数需要传入两个 `int{:py}` 类型的参数 `a` 和 `b`，函数返回的结果也是 `int{:py}` 类型

```python
def foo(a: int, b: int) -> int:
    return a + b
```

编写类型注释是一个非常好的习惯，更具体的类型注释文档可以查看 [官方文档 - 对类型提示的支持](https://docs.python.org/zh-cn/3/library/typing.html)，或者网上搜索相关内容。
