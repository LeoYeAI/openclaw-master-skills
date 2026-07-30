# Account Manager 文档

所属项目：**Futu Trade Bot Skills**

## 模块位置
`src/account_manager.py`

## 概述
账户模块用于：
- 查询账户列表
- 解锁交易权限
- 锁定交易权限

并提供便捷函数供脚本/LLM 直接调用。

## 对外接口

### `get_account_info()`
```python
get_account_info() -> Dict[str, Any]
```

行为：
- 调用富途 `get_acc_list()`。
- 返回账户列表结构：`accounts`。
- 每次调用都会覆盖写本地文件：`json/account_info.json`。

成功返回示例：
```python
{
  "success": True,
  "accounts": [
    {
      "account_id": "2817...",
      "account_type": "REAL",
      "market": "['HK', 'US']",
      "acc_type": "MARGIN",
      "security_firm": "FUTUSECURITIES",
      "sim_acc_type": "N/A",
      "acc_status": "ACTIVE"
    }
  ],
  "error_msg": None
}
```

### `unlock_trade(password=None, password_md5=None)`
```python
unlock_trade(
    password: Optional[str] = None,
    password_md5: Optional[str] = None
) -> Dict[str, Any]
```

密码优先级：
1. 显式参数 `password_md5`
2. 显式参数 `password`（运行时自动转 MD5）
3. 配置 `trade_password_md5`
4. 配置 `trade_password`（运行时自动转 MD5）

### `lock_trade(password=None, password_md5=None)`
```python
lock_trade(
    password: Optional[str] = None,
    password_md5: Optional[str] = None
) -> Dict[str, Any]
```

实现调用：
- 富途 `unlock_trade(..., is_unlock=False)`

## 统一返回格式
```python
{
  "success": bool,
  "error_msg": Optional[str]
}
```

## 本地文件输出
`get_account_info()` 会写入：
- 文件：`json/account_info.json`
- 策略：每次覆盖
- 结构：
```json
{
  "updated_at": "2026-03-06T14:44:51",
  "data": { "...": "..." }
}
```

## 使用示例
```python
from account_manager import get_account_info, unlock_trade, lock_trade

print(get_account_info())
print(unlock_trade())  # 使用配置中的密码或MD5
print(lock_trade())    # 用完建议锁回
```

## 注意事项
- 依赖 OpenD 连接可用。
- 明文密码和 MD5 密码都属于敏感信息，均应避免泄露。
- 对外函数返回后会显式关闭账户相关 context，避免 SDK 线程阻止进程退出。
