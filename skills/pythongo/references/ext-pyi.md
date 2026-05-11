# ext.pyi

这是从 `ext.pyi` 转换而来的 reference 文件。
当需要判断 PythonGO 的类定义、方法归属、方法签名、返回值类型、参数名时，优先参考这里的内容。

```python
from .models import Tick

def load_ticks(exchange: str, path: str, natural_day: str) -> list[Tick]:
    """
    使用 Rust 加载 Tick CSV 文件。
    
    Args:
        exchange (str): 交易所代码 (如 SHFE)
        path (str): CSV 文件路径
        
        
    Returns:
        list[Tick]: 返回一系列 Tick 对象 (兼容 models.Tick 接口)
    """
    ...

```
