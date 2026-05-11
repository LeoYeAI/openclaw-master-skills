"""Shop 技能模块 - 商品相关 API 调用命令"""

import typer
import asyncio
from typing import Optional
from .api_client import api_client

shop_app = typer.Typer(name="shop", help="商品相关 API 调用命令")


def sync_run(coroutine):
    """同步运行异步函数"""
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)


def format_output(result, json_output: bool = False):
    """格式化输出为 JSON 或原始格式"""
    import json

    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        typer.echo(result)


def handle_errors(func):
    """错误处理装饰器，提供结构化的错误输出"""
    import functools
    import traceback
    import json as json_module

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 从参数中获取 json_output
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


@shop_app.command("getproducturibydesc")
@handle_errors
def get_product_uri_by_desc(
    desc: str = typer.Option(..., "-desc", "--description", help="产品描述"),
    limit: int = typer.Option(
        5, "-limit", "--limit", help="返回数量限制，-1 表示返回所有结果"
    ),
    json_output: bool = typer.Option(False, "-j", "--json", help="输出 JSON 格式"),
):
    """
    通过语义查询，获取产品描述对应的 URI 地址

    示例：shop getproducturibydesc -desc "含量 45% 13-5-27" -limit 5
    """

    async def _run():
        result = await api_client.post(
            "/api/proxy/openviking/api/v1/search/find",
            {
                "query": desc,
                "limit": limit,
                "target_uri": "viking://resources",
                "score_threshold": 0.2,
            },
        )
        return result

    result = sync_run(_run())
    format_output(result, json_output)


@shop_app.command("getproductdetailbyuri")
@handle_errors
def get_product_detail_by_uri(
    uri: str = typer.Option(..., "-uri", "--uri", help="需要读取的 URI 地址"),
    offset: int = typer.Option(
        0, "-offset", "--offset", help="Starting line number (0-indexed)"
    ),
    limit: int = typer.Option(
        -1, "-limit", "--limit", help="Number of lines to read, -1 means read to end"
    ),
    json_output: bool = typer.Option(False, "-j", "--json", help="输出 JSON 格式"),
):
    """
    读取 URI 地址对应的完整内容

    示例：shop getproductdetailbyuri -uri "viking://resources/products/xxx.md" -offset 0 -limit -1
    """

    async def _run():
        result = await api_client.get(
            "/api/proxy/openviking/api/v1/content/read",
            {"uri": uri, "offset": offset, "limit": limit},
        )
        return result

    result = sync_run(_run())
    format_output(result, json_output)


@shop_app.command("getgoodsinfo")
def get_goods_info(
    product_code: str,
    json_output: bool = typer.Option(False, "-j", "--json", help="输出 JSON 格式"),
):
    """
    通过产品编号查询商品信息（排除 AI 幻觉）

    示例：shop getgoodsinfo "Y163U1305276020000"
    """

    async def _run():
        result = await api_client.post(
            "/api/proxy/shoptest/admin/AI/goods/info", {"productCode": product_code}
        )
        return result

    result = sync_run(_run())
    format_output(result, json_output)


@shop_app.command("getsalercode")
def get_saler_code(
    json_output: bool = typer.Option(False, "-j", "--json", help="输出 JSON 格式"),
):
    """
    获取业务员信息

    示例：shop getsalercode
    """

    async def _run():
        result = await api_client.get("/protected/user-info")
        return result

    result = sync_run(_run())
    format_output(result, json_output)


@shop_app.command("getdealercode")
def get_dealer_code(
    saler_code: str = typer.Argument(..., help="业务员编号"),
    json_output: bool = typer.Option(False, "-j", "--json", help="输出 JSON 格式"),
):
    """
    通过业务员编号获取客户编号列表

    示例：shop getdealercode "EZB2019063"
    """

    async def _run():
        result = await api_client.post(
            "/api/proxy/shoptest/admin/AI/dealer/listWithScope",
            {"salerCode": saler_code},
        )
        return result

    result = sync_run(_run())

    # 过滤字段，只保留有用信息
    if (
        not json_output
        and isinstance(result, dict)
        and "data" in result
        and isinstance(result["data"], list)
    ):
        filtered_data = []
        for dealer in result["data"]:
            filtered_dealer = {
                "dealerCode": dealer.get("dealerCode", ""),
                "dealerName": dealer.get("dealerName", ""),
                "dealerContact": dealer.get("dealerContact", ""),
                "dealerTel": dealer.get("dealerTel", ""),
                "dealerAddress": dealer.get("dealerAddress", ""),
                "balance": dealer.get("balance", "0"),
                # 保存草稿必需的字段
                "smsDealerId": dealer.get("smsDealerId", ""),
                "smsSalerId": dealer.get("smsSalerId", ""),
                "salerCode": dealer.get("salerCode", ""),
            }
            filtered_data.append(filtered_dealer)
        result["data"] = filtered_data

    format_output(result, json_output)


@shop_app.command("getproductlist")
def get_product_list(
    dealer_code: str = typer.Option(
        ..., "-dealercode", "--dealer-code", help="客户编号"
    ),
    search_value: str = typer.Option(
        ...,
        "-search",
        "--search-value",
        help='产品编号（验证权限）或空格分隔的关键词（模糊查询，如："45% 复合肥"）',
    ),
    json_output: bool = typer.Option(False, "-j", "--json", help="输出 JSON 格式"),
):
    """
    通过客户编号和搜索值查询可购买的产品列表

    支持两种模式：
    1. 精确验证：search_value 传产品编码，验证客户是否有权购买此产品
    2. 模糊查询：search_value 传空格分隔的关键词，查询符合条件的产品列表

    示例：
      shop getproductlist -dealercode "J620522007" -search "Y163U1305276020000"  # 验证产品权限
      shop getproductlist -dealercode "J620522007" -search "45% 复合肥"         # 模糊查询
    """

    async def _run():
        result = await api_client.post(
            "/api/proxy/shoptest/admin/AI/goods/list",
            {"dealerCode": dealer_code, "searchValue": search_value},
        )
        return result

    result = sync_run(_run())

    # 过滤字段，只保留有用信息
    if (
        not json_output
        and isinstance(result, dict)
        and "data" in result
        and isinstance(result["data"], list)
    ):
        filtered_data = []
        for product in result["data"]:
            filtered_product = {
                "productCode": product.get("productCode", ""),
                "productName": product.get("productName", ""),
                "productNutrient": product.get("productNutrient", ""),
                "productBagWeight": product.get("productBagWeight", ""),
                "productBrand": product.get("productBrand", ""),
            }
            filtered_data.append(filtered_product)
        result["data"] = filtered_data

    format_output(result, json_output)


@shop_app.command("getdeliverybase")
def get_delivery_base(
    product_code: str = typer.Option(
        ..., "-productcode", "--product-code", help="产品编号"
    ),
    dealer_code: str = typer.Option(
        ..., "-dealercode", "--dealer-code", help="客户编号"
    ),
    json_output: bool = typer.Option(False, "-j", "--json", help="输出 JSON 格式"),
):
    """
    通过客户编号和产品编号获取发货基地列表

    示例：shop getdeliverybase -productcode "Y68000500000023100" -dealercode "J620522007"
    """

    async def _run():
        result = await api_client.post(
            "/api/proxy/shoptest/admin/AI/goods/getProductInit",
            {"productCode": product_code, "dealerCode": dealer_code},
        )
        return result

    result = sync_run(_run())

    # 过滤字段，只保留发货基地列表
    if not json_output and isinstance(result, dict):
        # deliveryBaseList 可能在 data 里面
        base_list = []
        if "data" in result and isinstance(result["data"], dict):
            base_list = result["data"].get("deliveryBaseList", [])
        elif "deliveryBaseList" in result:
            base_list = result.get("deliveryBaseList", [])

        filtered_bases = []
        for base in base_list:
            filtered_bases.append(
                {
                    "dictLabel": base.get("dictLabel", ""),
                    "dictValue": base.get("dictValue", ""),
                }
            )

        # 返回精简结构
        result = {
            "msg": result.get("msg", "success"),
            "code": result.get("code", 200),
            "deliveryBaseList": filtered_bases,
        }

    format_output(result, json_output)


@shop_app.command("getdealeraddresses")
def get_dealer_addresses(
    dealer_code: str = typer.Argument(..., help="客户编号"),
    json_output: bool = typer.Option(False, "-j", "--json", help="输出 JSON 格式"),
):
    """
    通过客户编号获取客户设置好的收货地址

    示例：shop getdealeraddresses "J620522007"
    """

    async def _run():
        result = await api_client.post(
            "/api/proxy/shoptest/admin/AI/address/list", {"dealerCode": dealer_code}
        )
        return result

    result = sync_run(_run())

    # 非 JSON 模式下过滤字段
    if (
        not json_output
        and isinstance(result, dict)
        and "data" in result
        and isinstance(result["data"], list)
    ):
        filtered_data = []
        for addr in result["data"]:
            filtered_addr = {
                "addressId": addr.get("addressId"),
                "provinceCode": addr.get("provinceCode", ""),
                "provinceName": addr.get("provinceName", ""),
                "cityCode": addr.get("cityCode", ""),
                "cityName": addr.get("cityName", ""),
                "countyCode": addr.get("countyCode", ""),
                "countyName": addr.get("countyName", ""),
                "addressDetail": addr.get("addressDetail", ""),
                "contactPerson": addr.get("contactPerson", ""),
                "contactTel": addr.get("contactTel", ""),
            }
            filtered_data.append(filtered_addr)
        result["data"] = filtered_data

    format_output(result, json_output)


@shop_app.command("getstock")
def get_stock(
    logincode: str = typer.Option(..., "-logincode", "--logincode", help="客户编码"),
    productcode: str = typer.Option(
        ..., "-productcode", "--productcode", help="产品编号"
    ),
    sendbase: str = typer.Option(..., "-sendbase", "--sendbase", help="发货基地编码"),
    advertflag: str = typer.Option("0", "-advertflag", "--advertflag", help="固定为 0"),
    json_output: bool = typer.Option(False, "-j", "--json", help="输出 JSON 格式"),
):
    """
    查询产品基地库存信息和所属子公司名称

    示例：shop getstock -logincode "J620522007" -productcode "Y68000500000023100" -sendbase "10"
    """

    async def _run():
        result = await api_client.post(
            "/api/proxy/shoptest/admin/AI/goods/getStock",
            {
                "loginCode": logincode,
                "list": [
                    {
                        "sendBase": sendbase,
                        "productCode": productcode,
                        "advertFlag": advertflag,
                    }
                ],
            },
        )
        return result

    result = sync_run(_run())

    # 过滤字段，只保留有用信息
    if (
        not json_output
        and isinstance(result, dict)
        and "data" in result
        and isinstance(result["data"], list)
    ):
        filtered_data = []
        for item in result["data"]:
            filtered_item = {
                "companyName": item.get("companyName", ""),
                "companyCode": item.get("companyCode", ""),
                "productName": item.get("productName", ""),
                "productCode": item.get("productCode", ""),
                "productNum": item.get("productNum", 0),
            }
            filtered_data.append(filtered_item)
        result["data"] = filtered_data

    format_output(result, json_output)


@shop_app.command("addaddress")
def add_address(
    dealer_code: str = typer.Option(
        ..., "-dealercode", "--dealer-code", help="客户编码"
    ),
    dealer_name: str = typer.Option(..., "-name", "--dealer-name", help="客户名称"),
    contact_person: str = typer.Option(
        ..., "-contact", "--contact-person", help="联系人"
    ),
    contact_tel: str = typer.Option(..., "-phone", "--contact-tel", help="联系电话"),
    province_code: str = typer.Option(
        ..., "-provincecode", "--province-code", help="省份编码"
    ),
    province_name: str = typer.Option(
        ..., "-provincename", "--province-name", help="省份名称"
    ),
    city_code: str = typer.Option(..., "-citycode", "--city-code", help="城市编码"),
    city_name: str = typer.Option(..., "-cityname", "--city-name", help="城市名称"),
    county_code: str = typer.Option(
        ..., "-countycode", "--county-code", help="区县编码"
    ),
    county_name: str = typer.Option(
        ..., "-countyname", "--county-name", help="区县名称"
    ),
    address_detail: str = typer.Option(
        ..., "-detail", "--address-detail", help="详细地址"
    ),
    address_txt: str = typer.Option(
        ..., "-addrtxt", "--address-txt", help="省市区文本"
    ),
    address_type: str = typer.Option("1", "-type", "--address-type", help="地址类型"),
    address_typename: str = typer.Option(
        "经销商", "-typename", "--address-type-name", help="地址类型名称"
    ),
    latitude: str = typer.Option("", "-lat", "--latitude", help="纬度"),
    longitude: str = typer.Option("", "-lng", "--longitude", help="经度"),
    json_output: bool = typer.Option(False, "-j", "--json", help="输出 JSON 格式"),
):
    """
    新增客户收货地址

    示例：shop addaddress -dealercode "J620522007" -name "牛建建" -contact "牛一" -phone "13121007444" -provincecode "420000" -provincename "湖北省" -citycode "420800" -cityname "荆门市" -countycode "420802" -countyname "东宝区" -detail "泉口街道馨梦缘公寓" -addrtxt "湖北省荆门市东宝区"
    """

    async def _run():
        result = await api_client.post(
            "/api/proxy/shoptest/admin/AI/address/addAddress",
            {
                "dealerCode": dealer_code,
                "dealerName": dealer_name,
                "addressType": address_type,
                "addressTypeName": address_typename,
                "contactPerson": contact_person,
                "contactTel": contact_tel,
                "latitude": latitude,
                "longitude": longitude,
                "provinceName": province_name,
                "addressDetail": address_detail,
                "cityName": city_name,
                "countyName": county_name,
                "addressTxt": address_txt,
                "provinceCode": province_code,
                "cityCode": city_code,
                "countyCode": county_code,
            },
        )
        return result

    result = sync_run(_run())
    format_output(result, json_output)


@shop_app.command("editaddress")
def edit_address(
    address_id: int = typer.Option(..., "-id", "--address-id", help="地址ID"),
    dealer_code: str = typer.Option(
        ..., "-dealercode", "--dealer-code", help="客户编码"
    ),
    dealer_name: str = typer.Option(..., "-name", "--dealer-name", help="客户名称"),
    contact_person: str = typer.Option(
        ..., "-contact", "--contact-person", help="联系人"
    ),
    contact_tel: str = typer.Option(..., "-phone", "--contact-tel", help="联系电话"),
    province_code: str = typer.Option(
        ..., "-provincecode", "--province-code", help="省份编码"
    ),
    province_name: str = typer.Option(
        ..., "-provincename", "--province-name", help="省份名称"
    ),
    city_code: str = typer.Option(..., "-citycode", "--city-code", help="城市编码"),
    city_name: str = typer.Option(..., "-cityname", "--city-name", help="城市名称"),
    county_code: str = typer.Option(
        ..., "-countycode", "--county-code", help="区县编码"
    ),
    county_name: str = typer.Option(
        ..., "-countyname", "--county-name", help="区县名称"
    ),
    address_detail: str = typer.Option(
        ..., "-detail", "--address-detail", help="详细地址"
    ),
    address_txt: str = typer.Option(
        ..., "-addrtxt", "--address-txt", help="省市区文本"
    ),
    address_type: str = typer.Option("1", "-type", "--address-type", help="地址类型"),
    address_typename: str = typer.Option(
        "经销商", "-typename", "--address-type-name", help="地址类型名称"
    ),
    latitude: str = typer.Option("", "-lat", "--latitude", help="纬度"),
    longitude: str = typer.Option("", "-lng", "--longitude", help="经度"),
    json_output: bool = typer.Option(False, "-j", "--json", help="输出 JSON 格式"),
):
    """
    修改客户收货地址

    示例：shop editaddress -id 15098 -dealercode "J620522007" -name "牛建建" -contact "牛一" -phone "13121007444" -provincecode "420000" -provincename "湖北省" -citycode "420800" -cityname "荆门市" -countycode "420802" -countyname "东宝区" -detail "泉口街道馨梦缘公寓" -addrtxt "湖北省荆门市东宝区"
    """

    async def _run():
        result = await api_client.post(
            "/api/proxy/shoptest/admin/AI/address/editAddress",
            {
                "addressId": address_id,
                "dealerCode": dealer_code,
                "dealerName": dealer_name,
                "addressType": address_type,
                "addressTypeName": address_typename,
                "contactPerson": contact_person,
                "contactTel": contact_tel,
                "latitude": latitude,
                "longitude": longitude,
                "provinceName": province_name,
                "addressDetail": address_detail,
                "cityName": city_name,
                "countyName": county_name,
                "addressTxt": address_txt,
                "provinceCode": province_code,
                "cityCode": city_code,
                "countyCode": county_code,
            },
        )
        return result

    result = sync_run(_run())
    format_output(result, json_output)
