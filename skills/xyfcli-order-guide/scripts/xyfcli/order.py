"""Order 下单技能模块 - 完整的下单流程"""

import typer
import asyncio
import json
from typing import Optional, List, Dict, Any, Tuple
from .api_client import api_client

order_app = typer.Typer(name="order", help="下单订货流程技能")


def sync_run(coroutine):
    """同步运行异步函数"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)


def handle_errors(func):
    """错误处理装饰器，提供结构化的错误输出"""
    import functools
    import traceback
    import json as json_module

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        json_output = kwargs.get("json_output", False)

        try:
            return func(*args, **kwargs)
        except Exception as e:
            if json_output:
                error_data = {
                    "error": True,
                    "type": type(e).__name__,
                    "message": str(e),
                    "traceback": traceback.format_exc()
                    if hasattr(e, "__traceback__")
                    else None,
                }
                typer.echo(json_module.dumps(error_data, ensure_ascii=False, indent=2))
                raise typer.Exit(code=1)
            else:
                raise

    return wrapper


def build_save_order_drafts_request(full_data: Dict[str, Any]) -> Dict[str, Any]:
    """构建保存订单草稿的请求数据格式"""

    # 运输方式文本到代码的映射
    transport_mode_map = {
        "汽运": "01",
        "铁运": "02",
        "船运": "03",
        "集装箱运输": "04",
    }

    # 提货方式文本到代码的映射
    pickup_mode_map = {
        "自派车": "Z001",
        "统派车（公司付款）": "Z002",
        "统派车（客户付款）": "Z003",
    }

    # 获取运输方式代码（默认为01）
    transport_mode_text = full_data.get("transport_mode", "汽运")
    transfer_mode_code = transport_mode_map.get(transport_mode_text, "01")

    # 获取提货方式代码（默认为Z001）
    pickup_mode_text = full_data.get("pickup_mode", "自派车")
    take_mode_code = pickup_mode_map.get(pickup_mode_text, "Z001")

    # 构建订单地址产品列表
    order_address_product_list = []
    for prod in full_data["product_list"]:
        order_address_product_list.append(
            {
                "productCode": prod["product_code"],
                "productName": prod["product_name"],
                "productNum": prod["quantity"],
                "companyCode": prod["company_code"],
                "companyName": prod["company_name"],
                "coverImage": prod["cover_image"],
                "nowPrice": 0,
                "deliveryBase": full_data["departure_base"],
                "deliveryBaseName": full_data["departure_base_name"],
                "advertFlag": prod["advert_flag"],
                "advertFlagName": prod["advert_flag_name"],
                "decimalFlag": prod["decimal_flag"],
                "saleQuantity": 1,
                "stockQty": prod["stock_qty"],
                "unit": prod["unit"],
                "dealerCode": full_data["customer_code"],
                "unitName": "吨",
                "leftNum": prod["quantity"],
            }
        )

    # 构建订单产品列表
    order_product_list = []
    for prod in full_data["product_list"]:
        order_product_list.append(
            {
                "productCode": prod["product_code"],
                "productName": prod["product_name"],
                "productNum": prod["quantity"],
                "companyCode": prod["company_code"],
                "companyName": prod["company_name"],
                "coverImage": prod["cover_image"],
                "nowPrice": 0,
                "deliveryBase": full_data["departure_base"],
                "deliveryBaseName": full_data["departure_base_name"],
                "advertFlag": prod["advert_flag"],
                "advertFlagName": prod["advert_flag_name"],
                "decimalFlag": prod["decimal_flag"],
                "saleQuantity": 1,
                "stockQty": prod["stock_qty"],
                "unit": prod["unit"],
                "dealerCode": full_data["customer_code"],
                "unitName": "吨",
                "actualPrice": 0,
                "taxRateNum": prod["tax_rate"],
                "basePrice": "0.00",
                "packagePrice": "0.00",
                "branchOfficePrice": "0.00",
                "customerPrice": "0.00",
                "increasePrice": "0",
                "dzcPrice": "0.00",
                "railwayShortFreight": "0.00",
                "railwayFreight": "0.00",
                "carFreight": "0.00",
                "consignmentFreight": "0.00",
                "discountJson": "{}",
            }
        )

    # 构建完整的请求数据
    request_data = {
        "orderType": "1",
        "transferMode": transfer_mode_code,
        "takeMode": take_mode_code,
        "shippingPayType": "0",
        "orderAddressList": [
            {
                "provinceCode": full_data["address_detail"]["province_code"],
                "provinceName": full_data["address_detail"]["province_name"],
                "cityCode": full_data["address_detail"]["city_code"],
                "cityName": full_data["address_detail"]["city_name"],
                "countyCode": full_data["address_detail"]["county_code"],
                "countyName": full_data["address_detail"]["county_name"],
                "addressDetail": full_data["address_detail"]["address_detail"],
                "consigneePerson": full_data["receiver_name"],
                "consigneeTel": full_data["receiver_phone"],
                "vehicleOwner": full_data["vehicle_owner"],
                "licensePlate": full_data["license_plate"],
                "vehicleOwnerTel": full_data["vehicle_owner_tel"],
                "orderAddressProductList": order_address_product_list,
            }
        ],
        "orderProductList": order_product_list,
        "orderProductDetailList": [],
        "orderBalanceList": [],
        "dealerCode": full_data["customer_code"],
        "smsDealerId": full_data["sms_dealer_id"],
        "salerCode": full_data["sales_code"],
        "smsSalerId": full_data["sms_saler_id"],
        "deliveryBase": full_data["departure_base"],
        "tranConsignee": "",
        "tranTel": "",
        "tranAddress": "",
        "tranUnit": full_data["customer_name"],
        "billReceipt": "N",
        "billAddress": "",
        "invoiceFlag": "N",
        "invoiceType": "",
        "invoiceUnit": "",
        "invoiceNo": "",
        "invoiceAddress": "",
        "invoiceTel": "",
        "invoiceBank": "",
        "invoiceAccount": "",
        "vehicleOwner": full_data["vehicle_owner"],
        "licensePlate": full_data["license_plate"],
        "vehicleOwnerTel": full_data["vehicle_owner_tel"],
        "arrivalStationName": "",
        "deliveryStationName": "",
        "warehouse": "",
        "remark": full_data["remark"],
        "oneVote": "N",
        "logisticsFlag": True,
        "intendFreightRate": full_data["intend_freight_rate"],
        "deliveryBaseName": full_data["departure_base_name"],
    }

    return request_data


async def find_address(addr_list: List[Dict], addr_id: int) -> Optional[Dict]:
    """查找地址

    必须传入 addr_id 进行精确匹配
    """
    return next((a for a in addr_list if a.get("addressId") == addr_id), None)


async def find_dealer(dealer_list: List[Dict], dealer_code: str) -> Optional[Dict]:
    """查找客户"""
    return next((d for d in dealer_list if d.get("dealerCode") == dealer_code), None)


async def find_base_by_value(base_list: List[Dict], value: str) -> Optional[Dict]:
    """查找基地"""
    # 先尝试匹配 dictValue
    base = next((b for b in base_list if b.get("dictValue") == value), None)
    if base:
        return base
    # 再尝试匹配 dictLabel
    return next((b for b in base_list if b.get("dictLabel") == value), None)


async def collect_order_data(
    dealer_code: str,
    sales_code: str,
    product_codes: List[str],
    quantities: List[float],
    departure_base: str,
    addr_id: int,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    收集订单完整数据

    Returns:
        (完整数据字典，错误信息)
        成功时错误信息为 None
        失败时数据字典为 None
    """
    try:
        # 1. 收集客户信息
        dealer_resp = await api_client.post(
            "/api/proxy/shoptest/admin/AI/dealer/listWithScope",
            {"salerCode": sales_code},
        )

        if dealer_resp.get("code") != 200:
            return None, f"获取客户信息失败：{dealer_resp.get('msg', '未知错误')}"

        dealer = await find_dealer(dealer_resp["data"], dealer_code)
        if not dealer:
            available_dealers = [
                f"  [{i + 1}] {d['dealerName']} ({d['dealerCode']})"
                for i, d in enumerate(dealer_resp["data"][:5])
            ]
            return None, (
                f"未找到客户 '{dealer_code}'\n\n"
                f"可用的客户：\n" + "\n".join(available_dealers)
            )

        sms_dealer_id = dealer.get("smsDealerId", "")
        sms_saler_id = dealer.get("smsSalerId", "")

        # 2. 收集地址信息
        addr_resp = await api_client.post(
            "/api/proxy/shoptest/admin/AI/address/list", {"dealerCode": dealer_code}
        )

        if addr_resp.get("code") != 200:
            return None, f"获取地址列表失败：{addr_resp.get('msg', '未知错误')}"

        addr = await find_address(addr_resp["data"], addr_id)
        if not addr:
            return None, f"未找到地址 ID {addr_id}"

        # 3. 并行收集产品信息
        # 3.1 并行获取所有产品基本信息
        info_tasks = [
            api_client.post(
                "/api/proxy/shoptest/admin/AI/goods/info", {"productCode": pc}
            )
            for pc in product_codes
        ]
        info_responses = await asyncio.gather(*info_tasks)

        # 3.2 并行获取所有产品库存
        stock_tasks = [
            api_client.post(
                "/api/proxy/shoptest/admin/AI/goods/getStock",
                {
                    "loginCode": dealer_code,
                    "list": [
                        {
                            "sendBase": departure_base,
                            "productCode": product_code,
                            "advertFlag": "0",
                        }
                    ],
                },
            )
            for product_code in product_codes
        ]
        stock_responses = await asyncio.gather(*stock_tasks)

        # 3.3 串行组装产品详情
        products_detail = []
        for i, (product_code, quantity) in enumerate(zip(product_codes, quantities)):
            prod_resp = info_responses[i]
            stock_resp = stock_responses[i]

            if prod_resp.get("code") != 200:
                return None, (
                    f"获取产品 {i + 1} ({product_code}) 信息失败：\n"
                    f"{prod_resp.get('msg', '未知错误')}"
                )

            prod_info = prod_resp.get("data", {})
            if not prod_info:
                return None, f"产品 {product_code} 不存在或无权购买"

            stock = None
            if stock_resp.get("code") == 200 and stock_resp.get("data"):
                stock = stock_resp["data"][0]

            products_detail.append(
                {
                    "product_code": product_code,
                    "quantity": quantity,
                    "product_name": prod_info.get("productName", ""),
                    "company_code": stock.get("companyCode", "") if stock else "",
                    "company_name": stock.get("companyName", "") if stock else "",
                    "cover_image": prod_info.get("coverImage", ""),
                    "decimal_flag": str(prod_info.get("decimalFlag", "1")),
                    "unit": prod_info.get("unit", "TO"),
                    "advert_flag": prod_info.get("advertFlag", "0"),
                    "advert_flag_name": prod_info.get("advertFlagName", "成品"),
                    "tax_rate": str(prod_info.get("taxRate", "3")),
                    "stock_qty": str(stock.get("stockNum", "0")) if stock else "0",
                }
            )

        # 4. 获取基地名称
        base_resp = await api_client.post(
            "/api/proxy/shoptest/admin/AI/goods/getProductInit",
            {"productCode": product_codes[0], "dealerCode": dealer_code},
        )

        delivery_base_name = departure_base
        if base_resp.get("code") == 200:
            base_list = base_resp["data"].get("deliveryBaseList", [])
            base = await find_base_by_value(base_list, departure_base)
            if base:
                delivery_base_name = base["dictLabel"]

        # 5. 构建完整数据
        full_data = {
            "customer_code": dealer_code,
            "customer_name": dealer["dealerName"],
            "sales_code": sales_code,
            "product_list": products_detail,
            "departure_base": departure_base,
            "departure_base_name": delivery_base_name,
            "destination": addr["addressDetail"],
            "transport_mode": "汽运",
            "pickup_mode": "统派车（客户付款）",
            "receiver_name": addr["contactPerson"],
            "receiver_phone": addr["contactTel"],
            "sms_dealer_id": sms_dealer_id,
            "sms_saler_id": sms_saler_id,
            "address_detail": {
                "province_code": addr["provinceCode"],
                "province_name": addr["provinceName"],
                "city_code": addr["cityCode"],
                "city_name": addr["cityName"],
                "county_code": addr["countyCode"],
                "county_name": addr["countyName"],
                "address_detail": addr["addressDetail"],
                "consignee_person": addr["contactPerson"],
                "consignee_tel": addr["contactTel"],
            },
            "vehicle_owner": "",
            "license_plate": "",
            "vehicle_owner_tel": "",
            "remark": "",
            "intend_freight_rate": "0",
        }

        return full_data, None

    except Exception as e:
        return None, f"数据收集中发生异常：{str(e)}"


@order_app.command("place")
@handle_errors
def place_order(
    dealer_code: str = typer.Option(..., "-dealer", "--dealer-code", help="客户编码"),
    dealer_name: str = typer.Option(..., "-name", "--dealer-name", help="客户名称"),
    sales_code: str = typer.Option(..., "-sales", "--sales-code", help="业务员编码"),
    product_codes: str = typer.Option(
        ..., "-products", "--product-codes", help="商品编号列表，逗号分隔"
    ),
    departure_base: str = typer.Option(
        ..., "-base", "--departure-base", help="发货基地编码"
    ),
    # 地址参数（必传）
    addr_id: int = typer.Option(
        ..., "-addr-id", "--addr-id", help="系统中已保存的地址 ID（必传）"
    ),
    # 可选参数
    transport_mode: str = typer.Option(
        "汽运",
        "-transport",
        "--transport-mode",
        help="运输方式：汽运/铁运/船运/集装箱运输，默认汽运",
    ),
    pickup_mode: str = typer.Option(
        "统派车（公司付款）",
        "-pickup",
        "--pickup-mode",
        help="提货方式：自派车/统派车（公司付款）/统派车（客户付款），默认统派车（公司付款）",
    ),
    receiver_name: Optional[str] = typer.Option(
        None,
        "-receiver",
        "--receiver-name",
        help="收货人姓名（不传则使用地址中的联系人）",
    ),
    receiver_phone: Optional[str] = typer.Option(
        None, "-phone", "--receiver-phone", help="收货人电话（不传则使用地址中的电话）"
    ),
    quantities: str = typer.Option(
        ...,
        "-q",
        "--quantities",
        help="商品数量列表，逗号分隔，与商品编号一一对应（必传）",
    ),
    vehicle_owner: str = typer.Option(
        "", "-vehicle", "--vehicle-owner", help="承运车主"
    ),
    license_plate: str = typer.Option("", "-plate", "--license-plate", help="车牌号"),
    vehicle_owner_tel: str = typer.Option(
        "", "-vphone", "--vehicle-phone", help="车主电话"
    ),
    remark: str = typer.Option("", "-remark", "--remark", help="备注"),
    freight_rate: str = typer.Option("0", "-freight", "--freight-rate", help="运费率"),
    json_output: bool = typer.Option(False, "-j", "--json", help="输出 JSON 格式"),
):
    """
    保存订单草稿到系统

    自动收集所有必需信息并生成订单预览页面，可在页面上修改后保存到草稿箱。

    示例：
      order place -dealer "J620522007" -name "牛建建" -sales "EZB2019063" \\
                  -products "Y33001317150050000" -q "5" -base "10" \\
                  -addr-id 15099 -receiver "张三" -phone "13800138000"

    示例（多产品）：
      order place -dealer "J620522007" -name "牛建建" -sales "EZB2019063" \\
                  -products "Y33001317150050000,Y53001515150021000" -q "5,3" -base "10" \\
                  -addr-id 15099 -receiver "张三" -phone "13800138000"

    示例（指定运输方式和提货方式）：
      order place -dealer "J620522007" -name "牛建建" -sales "EZB2019063" \\
                  -products "Y33001317150050000" -q "5" -base "10" \\
                  -addr-id 15099 -transport "铁运" -pickup "自派车"
    """
    # 解析商品编号列表
    product_code_list = [p.strip() for p in product_codes.split(",") if p.strip()]

    if not product_code_list:
        raise typer.BadParameter("产品编号不能为空")

    # 解析数量列表
    try:
        quantity_list = [float(q.strip()) for q in quantities.split(",") if q.strip()]
        if len(quantity_list) != len(product_code_list):
            raise typer.BadParameter(
                f"数量列表长度 ({len(quantity_list)}) 与商品编号列表长度 ({len(product_code_list)}) 不匹配"
            )
        for q in quantity_list:
            if q <= 0:
                raise typer.BadParameter(f"商品数量必须为正数，当前值：{q}")
    except ValueError:
        raise typer.BadParameter("数量列表必须为逗号分隔的数字")

    # 收集完整数据
    if not json_output:
        typer.echo("正在收集订单信息...")

    full_data, error = sync_run(
        collect_order_data(
            dealer_code,
            sales_code,
            product_code_list,
            quantity_list,
            departure_base,
            addr_id,
        )
    )

    # 错误处理：终止并返回原因
    if error:
        typer.echo(f"\n❌ 错误：{error}", err=True)
        typer.echo("\n请检查输入参数后重试。")
        raise typer.Exit(code=1)

    # 使用用户提供的收货人信息（如果提供），否则使用地址中的联系人
    if receiver_name:
        full_data["receiver_name"] = receiver_name
    if receiver_phone:
        full_data["receiver_phone"] = receiver_phone

    # 使用用户提供的可选信息
    full_data["transport_mode"] = transport_mode
    full_data["pickup_mode"] = pickup_mode
    full_data["vehicle_owner"] = vehicle_owner
    full_data["license_plate"] = license_plate
    full_data["vehicle_owner_tel"] = vehicle_owner_tel
    full_data["remark"] = remark
    full_data["intend_freight_rate"] = freight_rate

    if not json_output:
        typer.echo("订单信息收集完成，正在保存订单草稿...")

    # 调用后端生成页面 URL
    # 构建新格式的请求数据
    order_request_data = build_save_order_drafts_request(full_data)

    result = sync_run(
        api_client.post(
            "/api/proxy/shoptest/admin/AI/order/saveOrderDrafts", order_request_data
        )
    )

    # 输出结果
    if json_output:
        output_data = {
            "success": result.get("code") == 200,
            "message": result.get("msg", ""),
            "data": result.get("data"),
            "order_info": full_data,
        }
        typer.echo(json.dumps(output_data, ensure_ascii=False, indent=2))
    else:
        # 检查API返回是否成功
        if result.get("code") == 200:
            typer.echo("\n" + "=" * 60)
            typer.echo("✅ 订单草稿保存成功！")
            typer.echo("=" * 60)
            typer.echo(f"\n📋 消息：{result.get('msg', '操作成功')}")
            if result.get("data"):
                typer.echo(f"\n📄 响应数据：")
                typer.echo(json.dumps(result.get("data"), ensure_ascii=False, indent=2))
            typer.echo("\n" + "=" * 60)
            typer.echo("\n📦 订单摘要：")
            typer.echo(
                f"  客户：{full_data['customer_name']} ({full_data['customer_code']})"
            )
            typer.echo(f"  业务员：{full_data['sales_code']}")
            typer.echo(f"  发货基地：{full_data['departure_base_name']}")
            typer.echo(f"  产品数量：{len(full_data['product_list'])} 个")
            for i, prod in enumerate(full_data["product_list"], 1):
                typer.echo(f"    [{i}] {prod['product_code']} × {prod['quantity']}")
            typer.echo(f"  收货地址：{full_data['destination']}")
            typer.echo(
                f"  收货人：{full_data['receiver_name']} {full_data['receiver_phone']}"
            )
            typer.echo("=" * 60)
        else:
            typer.echo("\n" + "=" * 60, err=True)
            typer.echo("❌ 订单草稿保存失败！", err=True)
            typer.echo("=" * 60, err=True)
            typer.echo(f"\n错误码：{result.get('code')}", err=True)
            typer.echo(f"错误消息：{result.get('msg', '未知错误')}", err=True)
            if result.get("data"):
                typer.echo(f"\n详细数据：")
                typer.echo(json.dumps(result.get("data"), ensure_ascii=False, indent=2))
            raise typer.Exit(code=1)
