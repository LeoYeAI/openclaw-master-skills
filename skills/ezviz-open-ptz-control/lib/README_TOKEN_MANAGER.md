# Ezviz Global Token Manager (萤石全局 Token 管理器)

提供全局 Token 缓存管理，支持多个萤石技能共享同一个 Token。

## 功能特性

- ✅ **全局 Token 缓存** - 存储在系统临时目录
- ✅ **自动过期检测** - 智能判断 Token 是否过期
- ✅ **到期前自动刷新** - 提前 5 分钟刷新，避免边界问题
- ✅ **多账号支持** - 基于 appKey:appSecret 哈希区分不同账号
- ✅ **原子写入** - 确保数据安全，防止并发写入问题
- ✅ **安全权限** - 缓存文件权限 600（仅所有者可读写）

## 缓存位置

| 系统 | 路径 |
|------|------|
| macOS | `/var/folders/xx/xxxx/T/ezviz_global_token_cache/` |
| Linux | `/tmp/ezviz_global_token_cache/` |
| Windows | `C:\Users\{user}\AppData\Local\Temp\ezviz_global_token_cache\` |

## 使用方法

### Python 导入

```python
from token_manager import get_cached_token, refresh_token, clear_token_cache

# 获取 Token（优先使用缓存，过期自动刷新）
token_result = get_cached_token(app_key, app_secret)
if token_result["success"]:
    access_token = token_result["access_token"]
    print(f"Token: {access_token}")
    print(f"Expires: {token_result['expire_time']}")
    print(f"From Cache: {token_result['from_cache']}")

# 强制刷新 Token（不使用缓存）
token_result = refresh_token(app_key, app_secret)

# 清除特定账号的缓存
clear_token_cache(app_key, app_secret)

# 清除所有缓存
clear_token_cache()
```

### 环境变量控制

```bash
# 启用缓存（默认）
export EZVIZ_TOKEN_CACHE=1

# 禁用缓存（每次运行重新获取 Token）
export EZVIZ_TOKEN_CACHE=0
```

### CLI 命令行使用

```bash
# 获取 Token
python3 token_manager.py get --app-key YOUR_KEY --app-secret YOUR_SECRET

# 强制刷新 Token
python3 token_manager.py refresh --app-key YOUR_KEY --app-secret YOUR_SECRET

# 列出所有缓存的 Token
python3 token_manager.py list

# 清除所有缓存
python3 token_manager.py clear

# 清除特定账号的缓存
python3 token_manager.py clear --app-key YOUR_KEY --app-secret YOUR_SECRET
```

## API 参考

### `get_cached_token(app_key, app_secret, use_cache=None)`

获取访问 Token，优先使用缓存版本（如果有效）。

**参数**:
- `app_key`: 萤石 app key
- `app_secret`: 萤石 app secret
- `use_cache`: 是否使用缓存（默认：检查 `EZVIZ_TOKEN_CACHE` 环境变量）
  - `False` 或 `"0"`: 禁用缓存
  - `True` 或 `"1"`: 启用缓存

**返回**:
```python
{
    "success": True,
    "access_token": "at.xxxxxxxxxxxxx",
    "expire_time": 1234567890000,  # 毫秒时间戳
    "from_cache": True  # 是否来自缓存
}
```

### `refresh_token(app_key, app_secret, cache_key=None)`

从萤石 API 获取新 Token 并保存到缓存。

**参数**:
- `app_key`: 萤石 app key
- `app_secret`: 萤石 app secret
- `cache_key`: 预计算的缓存键（可选）

**返回**: 同 `get_cached_token`

### `clear_token_cache(app_key=None, app_secret=None)`

清除 Token 缓存。

**参数**:
- `app_key`: 特定 app key（可选，不提供则清除所有）
- `app_secret`: 特定 app secret（可选，需与 app_key 一起使用）

**返回**: `True` 表示成功

### `list_cached_tokens()`

列出所有缓存的 Token（不显示实际 Token 值）。

**返回**:
```python
[
    {
        "cache_key": "abc123...",
        "app_key_prefix": "key123...",
        "expire_time": 1234567890000,
        "expire_str": "2026-03-26 10:00:00",
        "is_valid": True,
        "created_at": 1234567890000
    }
]
```

## 缓存文件格式

```json
{
  "cache_key_hash": {
    "cache_key": "abc123...",
    "access_token": "at.xxxxxxxxxxxxx",
    "expire_time": 1234567890000,
    "created_at": 1234567890000,
    "app_key_prefix": "key123..."
  }
}
```

## 安全注意事项

1. **文件权限**: 缓存文件权限设置为 600（仅所有者可读写）
2. **临时目录**: 使用系统临时目录，避免持久化存储
3. **原子写入**: 使用临时文件 + rename 确保写入安全
4. **可选禁用**: 支持通过环境变量完全禁用缓存

## 为什么缓存 Token？

- ⚡ **性能**: 避免每次运行都调用 API 获取 Token（减少等待时间）
- 🌐 **稳定性**: 减少 API 调用次数，降低网络失败风险
- 💰 **限流保护**: 避免频繁调用触发 API 限流
- 🔄 **多技能共享**: 多个萤石技能可以共享同一个 Token

## 故障排除

### 缓存文件权限问题

```bash
# 检查权限
ls -la /tmp/ezviz_global_token_cache/global_token_cache.json
# 应该显示：-rw------- (600)

# 修复权限
chmod 600 /tmp/ezviz_global_token_cache/global_token_cache.json
```

### 缓存损坏

```bash
# 清除所有缓存
rm -rf /tmp/ezviz_global_token_cache/

# 或使用 CLI
python3 token_manager.py clear
```

### 调试模式

```bash
# 查看详细日志
export EZVIZ_DEBUG=1
python3 scripts/main.py ...
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-03-18 | 初始版本，支持全局 Token 缓存 |
| 1.0.1 | 2026-03-18 | 添加多账号支持 |
| 1.0.2 | 2026-03-19 | 添加 CLI 接口，改进错误处理 |

---

**最后更新**: 2026-03-19  
**版本**: 1.0.2
