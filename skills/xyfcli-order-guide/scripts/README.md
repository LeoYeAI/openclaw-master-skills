# xyfcli - 下单订货 CLI 工具

本目录包含 xyfcli CLI 工具源码，作为 xyfcli-order-guide Skill 的一部分提供。

## 安装

本工具已随 Skill 一起提供。安装时执行（仅一次）：

```bash
cd ~/.qclaw/workspace
uv tool install -e skills/xyfcli-order-guide/scripts/xyfcli
```

## 快速开始

```bash
# 查看帮助
xyfcli --help

# 查看配置
xyfcli config show

# 设置 API 地址和 Token
xyfcli config set --base-url http://127.0.0.1:8000 --token your_token
```

## 功能模块

### 配置管理 (config)

| 命令 | 说明 |
|------|------|
| `config show` | 显示当前配置 |
| `config set` | 设置配置项 |
| `config init` | 初始化配置文件 |
| `config reset` | 重置为默认配置 |

**示例：**
```bash
# 显示配置
xyfcli config show

# 设置 API 和 Token
xyfcli config set --base-url http://127.0.0.1:8000 --token gateway_token_xxx
```

### Shop 命令

| 命令 | 说明 |
|------|------|
| `getproducturibydesc` | 通过产品描述查询产品 URI |
| `getproductdetailbyuri` | 通过 URI 获取产品详情 |
| `getgoodsinfo` | 查询商品信息 |
| `getsalercode` | 获取业务员编号 |
| `getdealercode` | 获取客户列表 |
| `getproductlist` | 获取可购买产品列表 |
| `getdeliverybase` | 获取发货基地列表 |
| `getdealeraddresses` | 获取收货地址 |

### Order 命令

| 命令      | 说明   |
| ------- | ---- |
| `place` | 完成下单 |



**示例：**
```bash
# 手动下单
xyfcli order place \
  -dealer "J620522007" \
  -name "牛建建" \
  -sales "EZB2019063" \
  -products "Y163U1305276020000" \
  -q "10" \
  -base "10" \
  -addr-id "123"
```

## 项目结构

```
xyfcli/
├── xyfcli/
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py
│   ├── config.py
│   ├── config_cmd.py
│   ├── api_client.py
│   ├── shop.py
│   └── order.py
├── pyproject.toml
└── README.md
```

## 依赖

- Python >= 3.13
- typer >= 0.24.1
- httpx >= 0.28.1
