# 平台格式自动适配功能实现总结

## 实现的功能

### 1. 平台自动检测
```python
def detect_platform_from_context(content: str) -> str:
    """根据上下文中的标记检测当前平台"""
    # 支持的平台：
    # - telegram (telegram, tg::, tg:, telega)
    # - discord (discord, dc::, dc:, discord.gg)
    # - whatsapp (whatsapp, wa::, wa:, whatsapp.com)
    # - slack (slack, slack://)
```

### 2. 平台特定格式适配
```python
def format_for_platform(content: str, platform: str) -> str:
    """根据平台调整内容格式"""
    # Telegram: Markdown 格式，直接使用
    # Discord: 链接用 <> 包裹防止 embed
    # WhatsApp: 表格转换为纯文本列表
    # Slack: mrkdwn 格式优化
```

### 3. CLI 参数支持
```bash
# 平台参数
python3 restore_context.py --platform telegram
python3 restore_context.py --platform discord
python3 restore_context.py --platform whatsapp
python3 restore_context.py --platform slack

# 自动检测（默认启用）
python3 restore_context.py --auto-detect-platform

# 组合使用
python3 restore_context.py --platform discord --level minimal
python3 restore_context.py --platform telegram --summary
python3 restore_context.py --platform telegram --timeline --period weekly

# 向后兼容
python3 restore_context.py --telegram  # 仍然有效
```

### 4. 消息分块策略
```python
# Telegram: 4000 字符限制
# Discord: 2000 字符限制
# 其他平台: 4000 字符限制（默认）

def split_for_platform(content: str, platform: str) -> list[str]:
    """根据平台限制分割长消息"""
```

## 优先级顺序

1. **`--platform` 显式指定**（最高优先级）
2. **`--telegram` 标志**（向后兼容）
3. **自动检测**（如果 `--auto-detect-platform` 启用）

## 文件修改

- `restore_context.py`: 添加平台检测和格式化功能
- `test_platform_adapter.py`: 测试脚本

## 使用示例

### 检测平台
```python
from restore_context import detect_platform_from_context

detect_platform_from_context("telegram context")  # 'telegram'
detect_platform_from_context("discord message")    # 'discord'
detect_platform_from_context("whatsapp text")       # 'whatsapp'
detect_platform_from_context("slack channel")      # 'slack'
detect_platform_from_context("random text")         # 'unknown'
```

### 格式化输出
```python
from restore_context import format_for_platform, PLATFORM_DISCORD

content = "Check out https://google.com"
formatted = format_for_platform(content, PLATFORM_DISCORD)
# 输出: "Check out <https://google.com>" (链接被包裹)
```

### CLI 使用
```bash
# Telegram 模式
python3 restore_context.py --platform telegram

# Discord 模式
python3 restore_context.py --platform discord

# WhatsApp 模式
python3 restore_context.py --platform whatsapp --level minimal

# 摘要输出
python3 restore_context.py --platform telegram --summary
```
