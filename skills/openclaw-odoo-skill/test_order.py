#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# 添加 odoo_skill 目录到路径
skill_dir = Path(__file__).parent / "odoo_skill"
sys.path.insert(0, str(skill_dir.parent))

from odoo_skill.client import OdooClient
from odoo_skill.smart_actions import SmartActionHandler

# 加载配置
config_path = Path(__file__).parent / "config.json"
with open(config_path) as f:
    config = json.load(f)

print(config["url"])
# 创建客户端
client = OdooClient.from_values(
    url=config["url"],
    db=config["db"],
    username=config["username"],
    api_key=config["api_key"],
    timeout=config.get("timeout", 60)
)

# 测试连接
status = client.test_connection()
print(f"✅ 已连接到 Odoo {status['server_version']}")

# 创建智能操作处理器
smart = SmartActionHandler(client)

# 创建报价单 - 客户 ky_wang, 产品 ipod3, 数量 5
result = smart.smart_create_quotation(
    customer_name="ky_wang",
    product_lines=[
        {"name": "ipod3", "quantity": 5}
    ]
)

print("\n" + "="*50)
print(result["summary"])
print("="*50)

# 显示详细信息
order = result["order"]
print(f"\n订单详情:")
print(f"  订单号：{order['name']}")
print(f"  状态：{order['state']}")
print(f"  客户：{order['partner_id'][1]}")
print(f"  总额：{order['amount_total']}")