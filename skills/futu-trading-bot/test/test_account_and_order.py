from pathlib import Path
from account_manager import get_account_info
from trade_service import submit_order

info = get_account_info()
print("1) get_account_info:", info.get("success"), "saved:", Path("json/account_info.json").exists())
accounts = info.get("accounts") or []
sim = next((a for a in accounts if "SIMULATE" in str(a.get("account_type", "")).upper()), None)
real = next((a for a in accounts if "REAL" in str(a.get("account_type", "")).upper()), None)
if sim:
    r1 = submit_order(code="HK.00700", side="BUY", qty=200, price=150, order_type="NORMAL", acc_id=int(sim["account_id"]), trd_env="SIMULATE")
    print("2) SIM submit_order:", r1)
else:
    print("2) SIM submit_order: skipped (no simulate account)")
if real:
    r2 = submit_order(code="HK.00700", side="BUY", qty=200, price=150, order_type="NORMAL", acc_id=int(real["account_id"]), trd_env="REAL")
    print("3) REAL submit_order:", r2)
else:
    print("3) REAL submit_order: skipped (no real account)")
