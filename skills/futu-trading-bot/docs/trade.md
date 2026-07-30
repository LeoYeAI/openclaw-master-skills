# Trade Service 文档

所属项目：**Futu Trade Bot Skills**

## 模块位置
`src/trade_service.py`

## 概述
交易模块负责下单、改单、撤单与全部撤单，内部包含参数校验和富途 API 调用。

## 设计原则
- 交易环境不做内部管理，调用方必须显式传入。
- 不提供账户环境切换接口（无 `switch_account_env`）。
- 不做幂等去重校验。

## 对外接口

### `submit_order(...)`
```python
submit_order(
    code: str,
    side: str,
    qty: int,
    acc_id: int,
    trd_env: str,
    price: Optional[float] = None,
    order_type: str = "NORMAL",
    aux_price: Optional[float] = None,
    remark: Optional[str] = None,
    time_in_force: str = "DAY",
) -> Dict[str, Any]
```

说明：
- `acc_id` 必传。
- `trd_env` 必传，仅支持 `REAL`、`SIMULATE`。
- `code` 目前按港股校验：必须以 `HK.` 开头。
- 会校验下单数量是否为 `lot_size` 整数倍。

### `modify_order(...)`
```python
modify_order(
    op: str,
    order_id: str,
    trd_env: str,
    qty: Optional[float] = None,
    price: Optional[float] = None,
    acc_id: int = 0,
    **kwargs,
) -> Dict[str, Any]
```

`op` 支持：
- `NORMAL`
- `CANCEL`
- `DISABLE`
- `ENABLE`
- `DELETE`

### `cancel_order(...)`
```python
cancel_order(order_id: str, trd_env: str, acc_id: int = 0) -> Dict[str, Any]
```

### `cancel_all_orders(...)`
```python
cancel_all_orders(trd_env: str, acc_id: int = 0, trdmarket: Optional[str] = None) -> Dict[str, Any]
```

### `close_trade_service()`
```python
close_trade_service() -> None
```
用于显式关闭内部交易/行情 context。一般情况下，对外交易函数已经会在返回后自动关闭。

## 下单校验流程（`submit_order`）
1. 订单模型参数校验（Pydantic）。
2. 股票代码格式校验。
3. 获取并校验 `lot_size`。
4. 价格、数量、触发价等基础校验。
5. 通过市场快照验证股票可用。
6. 调用富途 `place_order`。

## 连接生命周期
- `submit_order`、`modify_order`、`cancel_order`、`cancel_all_orders` 返回后都会显式关闭内部 context。
- `modify_order` 和 `cancel_all_orders` 会在调用前自行确保 context 已初始化，因此不依赖此前的 `submit_order` 调用状态。
- 这种设计适合一次性脚本与 agent 调用，避免 Futu SDK 内部线程阻止进程退出。

## 返回格式
统一返回字典，至少包含：
- `success`: 是否成功
- `message`: 结果描述

成功下单通常包含：
- `order_id`
- `lot_size`
- `trd_env`

## 使用示例
```python
from trade_service import submit_order

result = submit_order(
    code="HK.00700",
    side="BUY",
    qty=200,
    acc_id=6017237,
    trd_env="SIMULATE",
    price=150,
    order_type="NORMAL",
)
print(result)
```

## 注意事项
- `REAL` 环境会尝试真实交易，请先确认交易权限状态。
- 真实交易密码解锁/锁定由 `account_manager` 处理，不在本模块内自动完成。
