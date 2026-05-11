# 代码规范

## 命名 [#named]

**命名是最重要的一点，我们要避免使用意义不明的变量名**

Python 中的命名方式，我们一般使用**小写下划线命名法**，但是有一些特殊情况，需要使用**驼峰命名法**，以下列出对应的命名规则：

| 类型 | 命名法 | 示例 |
|---|---|---|
| 包 | 小写下划线 | `package_name` |
| 模块 | 小写下划线 | `module_name` |
| 类 | 大驼峰 | `ClassName` |
| 异常 | 大驼峰 | `ExceptionName` |
| 函数 | 小写下划线 | `function_name` |
| 全局常量/类常量 | 大写下划线 | `GLOBAL_CONSTANT_NAME` |
| 全局变量/类变量 | 小写下划线 | `global_var_name` |
| 实例变量 | 小写下划线 | `instance_var_name` |
| 方法名 | 小写下划线 | `method_name` |
| 函数参数/方法参数 | 小写下划线 | `function_parameter_name` |
| 局部变量 | 小写下划线 | `local_var_name` |

可以看到，当给类或者异常命名的时候（理论上异常就是类）我们使用驼峰命名法，其余所有情况几乎都使用小写下划线命名法；但这其中还有一个另类 - 全局常量，给全局常量命名的时候我们使用全大写的下划线命名法。

函数名，变量名和文件名应该是描述性的，严格避免缩写，需让人清晰易懂，禁止使用单字符给变量命名，比如：

```python
a = 32
n = "PythonGO"
```

当然，也有例外情况：

* 使用计数器和迭代器的时候使用的变量 `i`, `j`, `k`, `v`
* `try / except{:py}` 语句中代表异常的 `e`
* `with{:py}` 语句中代表文件句柄的 `f`

## 字符串 [#string]

从 Python 3.6 版本开始，便有了更方便的格式字符串方法 `f-string`，过去都是使用 `+{:py}` 符号拼接字符串，现在可以以更方便的方法来实现

```python
name = "PythonGO"

print(f"this is {name}, a powerful framework.")

>>> "this is PythonGO, a powerful framework."
```

也可以使用更高级的格式化功能

格式化时间

```python
today = datetime(year=2024, month=1, day=1)

print(f"{today:%B %d, %Y}")

>>> "January 01, 2024"
```

自动键值对：变量名 - 变量值，代码中起作用的是 `={:py}` 符号

```python
foo = "bar"

print(f"{ foo = }")

>>> " foo = 'bar'"
```

更多关于关于 `f-string` 的内容可以阅读 [官方文档 - f 字符串](https://docs.python.org/zh-cn/3/reference/lexical_analysis.html#f-strings)

## 行宽 [#line-length]

建议一行不超过 80 个字符，太长需手动续行，如下情况需要每个参数一行

```python
# 正确
kline_generator = KLineGenerator(
    callback=...,
    exchange=...,
    instrument_id=...,
    style=...,
    real_time_callback=...
)

# 错误
kline_generator = KLineGenerator(callback=..., exchange=..., instrument_id=..., style=..., real_time_callback=...)

# 当函数的入参有三个或三个以上时，必须带参数入参，以下为错误示范
kline_generator = KLineGenerator(a, b, c, d, e)
```

## 注释和文档字符串 [#docstring]

Python 的文档字符串用于注释代码。文档字符串是位于包、模块、类或函数里第一个语句的字符串。文档字符串一定要用三重双引号 `"""` 的格式。

我们写函数方法的时候，需要写上对应的文档字符串和一些注释，这样既可以让自己下次读代码的时候快速了解该函数方法的用处，也可以让别人更好的读懂你的代码。

### 函数文档 [#docstring-function]

函数没有参数时

```python
def get_some_data():
    """获取某些数据"""
```

函数有参数时

*如有必要，你可以对返回值也添加文档，格式为 `Returns:`*

```python
def get_some_data(param_a: str, param_b: int) -> list[str]:
    """
    获取某些数据

    Args:
        param_a: 参数 A
        param_b: 参数 B
    """
```

类的文档字符串是写在 `class` 下的

```python
class DemoClass(object):
    """
    这是一个示例类

    Args:
        param_a: 参数 A
        param_b: 参数 B
    """

    def __init__(self, param_a: str, param_b: int) -> None:
        ...
```

注意：所有类必须显式的继承 `object{:py}`，请避免以下写法：

```python
class DemoClass():
    ...

class DemoClass:
    ...
```

### 代码注释 [#docstring-comment]

当某一段代码比较难以理解的时候，可以对其编写注释，注释符号 `#` 前面应该为两个空格，后面为一个空格

```python
if is_true is False:  # 当条件为 False 的时候才进入判断
    ...
```

----

参考资料：

* [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)

* [PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/)
