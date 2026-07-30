#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

from account_manager import get_account_info, unlock_trade
from quote_service import get_market_snapshot
from trade_service import submit_order

# 1. 获取账户信息
print("获取账户信息...")
accounts = get_account_info()
if not accounts.get('success'):
    print("获取账户失败:", accounts.get('message'))
    sys.exit(1)

# 选择模拟账户
if not accounts.get('accounts'):
    print("没有找到账户")
    sys.exit(1)

# 查找模拟账户
sim_accounts = [acc for acc in accounts['accounts'] if acc['account_type'] == 'SIMULATE']
if not sim_accounts:
    print("没有找到模拟账户")
    sys.exit(1)

acc = sim_accounts[0]
acc_id = acc['account_id']
print(f"使用模拟账户: {acc_id} ({acc['account_type']})")

# 2. 解锁交易
print("解锁交易...")
unlock = unlock_trade()
if not unlock.get('success'):
    print("解锁失败:", unlock.get('message'))
    sys.exit(1)

# 3. 获取腾讯股价
print("查询腾讯股价...")
tencent = "HK.00700"
quote = get_market_snapshot([tencent])
if not quote.get('success'):
    print("获取报价失败:", quote.get('message'))
    sys.exit(1)

price = quote['data'][0]['last_price']
print(f"腾讯当前价: {price}")

# 4. 下单100股
print(f"下单100股腾讯 @ {price}...")
order = submit_order(
    code=tencent,
    side="BUY",
    qty=100,
    acc_id=acc_id,
    trd_env="SIMULATE",
    price=price,
    order_type="NORMAL"
)

if order.get('success'):
    print("下单成功!")
    print(f"订单ID: {order['order_id']}")
else:
    print("下单失败:", order.get('message'))