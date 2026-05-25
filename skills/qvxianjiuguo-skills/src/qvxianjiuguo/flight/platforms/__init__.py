"""机票搜索平台处理器

支持四个平台：
- qunar: 去哪儿
- ctrip: 携程
- fliggy: 飞猪
- ly: 同程
"""

from .platforms import (
    PlatformHandler,
    QunarHandler,
    CtripHandler,
    FliggyHandler,
    LyHandler,
    PLATFORMS,
    get_platform_handler,
)

__all__ = [
    "PlatformHandler",
    "QunarHandler",
    "CtripHandler",
    "FliggyHandler",
    "LyHandler",
    "PLATFORMS",
    "get_platform_handler",
]
