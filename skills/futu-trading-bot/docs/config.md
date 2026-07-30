# Config Manager 文档

所属项目：**Futu Trade Bot Skills**

## 模块位置
`src/config_manager.py`

## 作用
统一加载并提供项目配置（富途连接参数、交易密码、日志参数）。

## 配置文件读取规则
1. 优先读取：`json/config.json`
2. 回退读取：`json/config_example.json`（存在时）
3. 兼容读取：`json/config.example.json`（旧命名存在时）
4. 若都不存在，抛出 `FileNotFoundError`

## 配置示例
```json
{
  "futu_api": {
    "host": "127.0.0.1",
    "port": 11111,
    "security_firm": "FUTUSECURITIES",
    "trade_password": "",
    "trade_password_md5": "",
    "default_env": "SIMULATE"
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s"
  }
}
```

## 默认值（缺省字段自动补全）
- `host`: `127.0.0.1`
- `port`: `11111`
- `security_firm`: `FUTUSECURITIES`
- `trade_password`: `""`
- `trade_password_md5`: `""`
- `default_env`: `SIMULATE`

## 主要接口
- `get_futu_config()`
- `get_host()`
- `get_port()`
- `get_security_firm()`
- `get_trade_password()`
- `get_trade_password_md5()`
- `get_default_env()`
- `get_default_env_str()`

## 与其他模块关系
- `account_manager` 使用本模块读取主机、端口、券商、交易密码。
- `trade_service` 使用本模块读取主机、端口、券商。

## 安全建议
- `json/config.json` 不应入库，需加入 `.gitignore`。
- 使用最小权限：`chmod 600 json/config.json`。
- 不在日志中输出真实密码或 MD5 值。
