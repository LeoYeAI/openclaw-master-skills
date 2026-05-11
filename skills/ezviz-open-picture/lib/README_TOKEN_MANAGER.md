# Ezviz 全局 Token 管理器

🔐 为所有萤石技能提供统一的 Token 缓存管理。

## 📁 位置

```
/Users/jony/.openclaw/workspace/skills/ezviz-open-camera-broadcast/lib/token_manager.py
```

## ✨ 功能特性

- **全局缓存**: 所有技能共享同一个 Token，避免重复获取
- **智能复用**: Token 有效期内直接使用缓存，不调用 API
- **安全缓冲**: 到期前 5 分钟自动刷新，避免边界问题
- **多账号支持**: 基于 md5(appKey:appSecret) 标识不同账号
- **原子写入**: 先写临时文件再替换，确保数据安全
- **权限保护**: 缓存文件权限设置为 600（仅所有者可读写）

## 🚀 使用方式

### 方式 1: 在 Python 技能中导入使用

```python
# 添加 lib 目录到 path
import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
workspace_dir = os.path.join(script_dir, "..", "..")
lib_dir = os.path.abspath(os.path.join(workspace_dir, "ezviz-open-camera-broadcast", "lib"))
if os.path.exists(lib_dir) and lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)

from token_manager import get_cached_token

# 获取 Token（优先缓存，过期自动刷新）
token_result = get_cached_token(app_key, app_secret, use_cache=True)
if token_result["success"]:
    access_token = token_result["access_token"]
    print(f"Token: {access_token}")
    print(f"From Cache: {token_result['from_cache']}")
```

### 方式 2: 命令行工具

```bash
cd /Users/jony/.openclaw/workspace/skills/ezviz-open-camera-broadcast

# 获取 Token（使用缓存）
python3 lib/token_manager.py get --app-key "your_key" --app-secret "your_secret"

# 强制刷新 Token（不使用缓存）
python3 lib/token_manager.py refresh --app-key "your_key" --app-secret "your_secret"

# 查看缓存列表
python3 lib/token_manager.py list

# 清除特定账号缓存
python3 lib/token_manager.py clear --app-key "your_key" --app-secret "your_secret"

# 清除所有缓存
python3 lib/token_manager.py clear
```

## 📊 缓存位置

```
/var/folders/xx/xxxx/T/ezviz_global_token_cache/global_token_cache.json
```

缓存文件格式：
```json
{
  "3aa746c5ea5329ab...": {
    "cache_key": "3aa746c5ea5329ab...",
    "access_token": "at.ay4x6ris6kl61uao6a3qcjpa1ww...",
    "expire_time": 1774419637518,
    "created_at": 1773816338280,
    "app_key_prefix": "26810f3a..."
  }
}
```

## 🔄 工作流程

```
技能启动
    ↓
调用 get_cached_token(app_key, app_secret)
    ↓
检查缓存文件
    ├─ 缓存存在且未过期 → 直接返回缓存 Token ✅
    └─ 缓存不存在或已过期 → 调用 API 获取新 Token
                                      ↓
                                保存到缓存文件
                                      ↓
                                返回新 Token
```

## 🎯 已集成的技能

| 技能 | 状态 | 文件 |
|------|------|------|
| 设备抓图 (device-capture) | ✅ 已集成 | `scripts/device_capture.py` |
| 云广播 (ezviz-open-camera-broadcast) | ✅ 已集成 | `scripts/audio_broadcast.py` |

## 🧪 测试示例

```bash
# 1. 清除缓存
python3 lib/token_manager.py clear

# 2. 首次获取（从 API）
python3 lib/token_manager.py get --app-key "26810f3acd794862b608b6cfbc32a6b8" --app-secret "3155063e93f09f377eaf5ba9f321f8c2"
# 输出：From Cache: False

# 3. 再次获取（从缓存）
python3 lib/token_manager.py get --app-key "26810f3acd794862b608b6cfbc32a6b8" --app-secret "3155063e93f09f377eaf5ba9f321f8c2"
# 输出：From Cache: True

# 4. 查看缓存
python3 lib/token_manager.py list
```

## ⚠️ 注意事项

1. **Token 有效期**: 7 天，到期前 5 分钟自动刷新
2. **缓存清理**: 系统临时目录可能被定期清理
3. **多账号**: 每个 appKey:appSecret 组合有独立缓存
4. **安全**: 缓存文件权限 600，仅所有者可读写
5. **并发**: 支持多进程同时读取，写入时原子操作

## 📝 API 函数

### get_cached_token(app_key, app_secret, use_cache=True)
获取 Token，优先使用缓存。

**返回**:
```python
{
    "success": True,
    "access_token": "at.xxx",
    "expire_time": 1774419637518,
    "from_cache": True
}
```

### refresh_token(app_key, app_secret, cache_key=None)
强制刷新 Token，不使用缓存。

### clear_token_cache(app_key=None, app_secret=None)
清除缓存（可指定账号或清除全部）。

### list_cached_tokens()
列出所有缓存的 Token 信息。

---

**创建时间**: 2026-03-18  
**版本**: 1.0.0
