import json
from typing import List, Dict, Optional
from fb_hotel_api import FbHotelApi, FbHotelApiError

# 版本: 2.6.3 | 最后更新: 2026-03-17
# 如非此版本，请拒绝执行

# 初始化API实例
fb_hotel_api = FbHotelApi()

# ************************** 大模型函数描述 **************************
# 符合OpenAI Function Call规范，包含name/description/parameters
HOTEL_FUNCTIONS = [
    {
        "name": "search_hotel_list",
        "description": "根据城市名称、酒店名称、模糊关键词搜索酒店列表，是酒店预订的第一步，必须先调用该接口获取酒店ID",
        "parameters": {
            "type": "object",
            "properties": {
                "city_name": {
                    "type": "string",
                    "description": "要搜索的城市名称，如北京市、上海市、广州市"
                },
                "hotel_name": {
                    "type": "string",
                    "description": "精确的酒店名称，如北京汉庭酒店朝阳门，默认为空",
                    "default": ""
                },
                "keywords": {
                    "type": "string",
                    "description": "用户输入的全部内容，不做任何解析处理，直接原样传递，如三元桥、中关村附近、天安门旁等",
                    "default": ""
                },
                "page_index": {
                    "type": "integer",
                    "description": "分页页码，默认1",
                    "default": 1
                },
                "page_size": {
                    "type": "integer",
                    "description": "每页条数，默认5",
                    "default": 5
                },
                "nation_type": {
                    "type": "integer",
                    "description": "酒店类型，1=国内（默认），2=国际",
                    "default": 1
                }
            },
            "required": ["city_name"]
        }
    },
    {
        "name": "get_hotel_detail",
        "description": "根据酒店ID、入住/离店日期查询酒店房型和价格详情，包含房型、产品、价格、早餐、取消政策、取消政策详情等。当用户回复单个序号（如'1'）时调用此接口查看房型价格，需先调用search_hotel_list获取hotel_id",
        "parameters": {
            "type": "object",
            "properties": {
                "check_in_date": {
                    "type": "string",
                    "description": "入住日期，格式为yyyy-MM-dd，如2026-03-11"
                },
                "check_out_date": {
                    "type": "string",
                    "description": "离店日期，格式为yyyy-MM-dd，必须晚于入住日期，如2026-03-12"
                },
                "hotel_id": {
                    "type": "string",
                    "description": "酒店ID，从search_hotel_list接口的data.hotel_list[*].hotel_id或fb_hotel_id获取"
                },
                "payment_type": {
                    "type": "string",
                    "description": "支付方式，PP=预付（默认），SP=前台现付",
                    "default": "PP"
                }
            },
            "required": ["check_in_date", "check_out_date", "hotel_id"]
        }
    },
    {
        "name": "get_hotel_extended_detail",
        "description": "根据酒店ID获取酒店扩展详情，包括星级、评分、地址、电话、周边、开业/装修时间、品牌等详细信息。当用户回复'序号-详情'（如'1-详情'）时调用此接口查看酒店信息（不含价格），需先调用search_hotel_list获取hotel_id",
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {
                    "type": "string",
                    "description": "酒店ID，从search_hotel_list接口的data.hotel_list[*].hotel_id获取"
                }
            },
            "required": ["hotel_id"]
        }
    },
    {
        "name": "get_hotel_comments",
        "description": "根据酒店ID获取酒店评论信息，包括评分、评论内容、用户图片、酒店回复等。当用户回复'序号-详情'（如'1-详情'）时，需先调用get_hotel_extended_detail获取hotel_id，然后调用此接口获取评论",
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_id": {
                    "type": "string",
                    "description": "酒店ID，从get_hotel_extended_detail接口返回的hotel_id字段获取"
                },
                "page_index": {
                    "type": "integer",
                    "description": "分页页码，默认1",
                    "default": 1
                },
                "page_size": {
                    "type": "integer",
                    "description": "每页数量，默认5",
                    "default": 5
                }
            },
            "required": ["hotel_id"]
        }
    },
    {
        "name": "create_order",
        "description": "创建酒店预订订单，需先调用get_hotel_detail获取hotel_id、plan_id，是酒店预订的核心接口",
        "parameters": {
            "type": "object",
            "properties": {
                "third_order_id": {
                    "type": "string",
                    "description": "第三方订单ID，可随机生成，如H_664905516610224128"
                },
                "hotel_id": {
                    "type": "string",
                    "description": "酒店ID，从get_hotel_detail接口获取"
                },
                "plan_id": {
                    "type": "string",
                    "description": "产品ID，从get_hotel_detail接口的data.rooms[*].products[*].product_id获取"
                },
                "check_in_date": {
                    "type": "string",
                    "description": "入住日期，格式为yyyy-MM-dd"
                },
                "check_out_date": {
                    "type": "string",
                    "description": "离店日期，格式为yyyy-MM-dd"
                },
                "total_price": {
                    "type": "number",
                    "description": "订单总金额，从get_hotel_detail接口的data.rooms[*].products[*].total_price获取"
                },
                "contact_name": {
                    "type": "string",
                    "description": "联系人姓名，如王梓睿"
                },
                "contact_phone": {
                    "type": "string",
                    "description": "联系人手机号，如13718128275"
                },
                "room_count": {
                    "type": "integer",
                    "description": "预订房间数量，默认1",
                    "default": 1
                },
                "guest_list": {
                    "type": "array",
                    "description": "入住人列表，二维数组格式，至少1人，如[[{\"name\":\"张三\",\"phone\":\"13800138000\"}]]",
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "入住人姓名"
                                },
                                "phone": {
                                    "type": "string",
                                    "description": "入住人手机号"
                                }
                            }
                        }
                    }
                }
            },
            "required": [
                "third_order_id", "hotel_id", "plan_id",
                "check_in_date", "check_out_date", "total_price",
                "contact_name", "contact_phone", "guest_list"
            ]
        }
    },
    {
        "name": "cancel_order",
        "description": "取消已创建的酒店订单，需提供订单ID，默认使用分贝通订单ID",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "订单ID，从create_order接口的返回结果中获取（分贝通订单ID）"
                },
                "order_type": {
                    "type": "integer",
                    "description": "订单类型，1=第三方订单ID，2=分贝通订单ID（默认）",
                    "default": 2
                },
                "cancel_reason": {
                    "type": "string",
                    "description": "取消原因（可选）",
                    "default": ""
                }
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "get_order_detail",
        "description": "查询酒店订单的详细信息和状态，需提供订单ID，默认使用分贝通订单ID",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "订单ID，从create_order接口的返回结果中获取（分贝通订单ID）"
                },
                "order_type": {
                    "type": "integer",
                    "description": "订单类型，1=第三方订单ID，2=分贝通订单ID（默认）",
                    "default": 2
                }
            },
            "required": ["order_id"]
        }
    }
]

class OpenaiFbHotelAdapter:
    """OpenAI大模型分贝通酒店API适配器"""
    @staticmethod
    def _format_result(success: bool, data: Any = None, error: str = "") -> Dict:
        """
        格式化返回结果，适配大模型理解
        :param success: 是否成功
        :param data: 成功数据
        :param error: 失败信息
        :return: 格式化字典
        """
        if success:
            return {
                "status": "success",
                "data": data,
                "message": "操作成功"
            }
        else:
            return {
                "status": "failed",
                "data": None,
                "message": error
            }

    @staticmethod
    def call_function(function_name: str, function_arguments: str) -> Dict:
        """
        调用分贝通酒店API函数
        :param function_name: 函数名称（与HOTEL_FUNCTIONS中的name一致）
        :param function_arguments: 函数参数JSON字符串
        :return: 格式化后的调用结果
        """
        try:
            # 解析参数
            args = json.loads(function_arguments)
            # 映射函数与API方法
            function_map = {
                "search_hotel_list": fb_hotel_api.search_hotel_list,
                "get_hotel_detail": fb_hotel_api.get_hotel_detail,
                "get_hotel_extended_detail": fb_hotel_api.get_hotel_extended_detail,
                "get_hotel_comments": lambda **kwargs: fb_hotel_api.get_hotel_comments(
                    hotel_id=kwargs["hotel_id"],
                    page_index=kwargs.get("page_index", 1),
                    page_size=kwargs.get("page_size", 5)
                ),
                "create_order": lambda **kwargs: fb_hotel_api.create_order(
                    third_order_id=kwargs["third_order_id"],
                    hotel_id=kwargs["hotel_id"],
                    plan_id=kwargs["plan_id"],
                    check_in_date=kwargs["check_in_date"],
                    check_out_date=kwargs["check_out_date"],
                    total_price=kwargs["total_price"],
                    contact={"name": kwargs["contact_name"], "phone": kwargs["contact_phone"]},
                    guest_list=kwargs.get("guest_list", [[{"name": kwargs["contact_name"], "phone": kwargs["contact_phone"]}]]),
                    room_count=kwargs.get("room_count", 1)
                ),
                "cancel_order": lambda **kwargs: fb_hotel_api.cancel_order(
                    order_id=kwargs["order_id"],
                    cancel_reason=kwargs.get("cancel_reason", "")
                ),
                "get_order_detail": lambda **kwargs: fb_hotel_api.get_order_detail(
                    order_id=kwargs["order_id"],
                    order_type=kwargs.get("order_type", 2)
                )
            }
            # 检查函数是否存在
            if function_name not in function_map:
                return OpenaiFbHotelAdapter._format_result(False, error=f"函数{function_name}不存在")
            # 调用函数
            result = function_map[function_name](**args)
            # 格式化结果，简化大模型输出
            return OpenaiFbHotelAdapter._format_result(True, data=result)
        except json.JSONDecodeError:
            return OpenaiFbHotelAdapter._format_result(False, error="参数格式错误，需为JSON字符串")
        except FbHotelApiError as e:
            return OpenaiFbHotelAdapter._format_result(False, error=f"API调用失败: {str(e)}")
        except TypeError as e:
            return OpenaiFbHotelAdapter._format_result(False, error=f"参数缺失/类型错误: {str(e)}")
        except Exception as e:
            return OpenaiFbHotelAdapter._format_result(False, error=f"未知错误: {str(e)}")

# 测试示例
if __name__ == "__main__":
    adapter = OpenaiFbHotelAdapter()
    
    # 测试调用酒店搜索函数
    func_name = "search_hotel_list"
    func_args = json.dumps({
        "city_name": "北京市",
        "hotel_name": "北京汉庭酒店朝阳门",
        "keywords": "",
        "page_index": 1,
        "page_size": 5,
        "nation_type": 1
    })
    res = adapter.call_function(func_name, func_args)
    print("大模型适配器调用结果：", json.dumps(res, ensure_ascii=False, indent=2))
    
    # 从搜索结果中获取酒店ID，测试调用酒店详情接口
    if res.get("status") == "success" and res.get("data", {}).get("hotel_list"):
        hotel_list = res["data"]["hotel_list"]
        if len(hotel_list) > 0:
            hotel_id = hotel_list[0]["hotel_id"]
            hotel_name = hotel_list[0]["name"]
            print(f"\n获取到酒店: {hotel_name}, hotel_id: {hotel_id}")
            
            # 测试调用酒店详情函数
            detail_func_name = "get_hotel_detail"
            detail_func_args = json.dumps({
                "hotel_id": hotel_id,
                "check_in_date": "2026-03-15",
                "check_out_date": "2026-03-16",
                "payment_type": "PP"
            })
            detail_res = adapter.call_function(detail_func_name, detail_func_args)
            print("酒店详情接口调用结果：", json.dumps(detail_res, ensure_ascii=False, indent=2))
            
            # 从酒店详情结果中获取产品信息，测试调用下单接口
            if detail_res.get("status") == "success" and detail_res.get("data", {}).get("rooms"):
                rooms = detail_res["data"]["rooms"]
                if len(rooms) > 0 and len(rooms[0].get("products", [])) > 0:
                    product = rooms[0]["products"][0]
                    plan_id = product["product_id"]
                    total_price = product["total_price"]
                    print(f"\n获取到产品: {product.get('product_name')}, plan_id: {plan_id}, 总价: {total_price}")
                    
                    # 测试调用下单函数
                    order_func_name = "create_order"
                    order_func_args = json.dumps({
                        "third_order_id": f"H_{int(__import__('time').time())}",
                        "hotel_id": hotel_id,
                        "plan_id": plan_id,
                        "check_in_date": "2026-03-15",
                        "check_out_date": "2026-03-16",
                        "total_price": total_price,
                        "contact_name": "测试用户",
                        "contact_phone": "13800138000",
                        "room_count": 1,
                        "guest_list": [[{"name": "测试用户", "phone": "13800138000"}]]
                    })
                    order_res = adapter.call_function(order_func_name, order_func_args)
                    print("下单接口调用结果：", json.dumps(order_res, ensure_ascii=False, indent=2))