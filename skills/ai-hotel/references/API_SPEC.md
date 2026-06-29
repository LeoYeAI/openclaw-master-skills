# 分贝通酒店 API 规范文档

> 版本: 3.0.0 | 更新日期: 2026-03-25

## 概述

分贝通酒店API提供统一的接口入口，通过 `skill_type` 参数区分不同操作。

### 基础信息

| 配置项 | FAT环境 | 线上环境 |
|-------|---------|---------|
| 域名 | `https://app-gate.fenbeitong.com` | `https://app-gate.fenbeitong.com` |
| 接口入口 | `/business/hotel/open/push/skill/access` | `/business/hotel/open/push/skill/access` |
| 请求方式 | POST | POST |
| Content-Type | application/json | application/json |

### 认证方式

- **认证接口**：无需 access-token
- **业务接口**：Header 中传递 `access-token: fbsk-xxx`

---

## 一、认证类接口

### 1.1 获取手机号验证码

**skill_type**: `getMobileCaptcha`

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| skill_type | string | 是 | 固定值: getMobileCaptcha |
| mobile | string | 是 | 手机号 |

**请求示例**：
```json
{
    "skill_type": "getMobileCaptcha",
    "mobile": "18301187051"
}
```

**响应示例**：
```json
{
    "request_id": "nQabT9pHt5u5m0mA",
    "trace_id": "",
    "code": 0,
    "type": 0,
    "msg": "success",
    "data": true
}
```

**错误响应**：
```json
{
    "request_id": "BJ20y0tlTSGvuOzT",
    "code": -32,
    "msg": "短信验证码不正确"
}
```

---

### 1.2 获取身份编码

**skill_type**: `getIdentityCode`

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| skill_type | string | 是 | 固定值: getIdentityCode |
| mobile | string | 是 | 手机号 |
| captcha | string | 是 | 验证码 |

**请求示例**：
```json
{
    "skill_type": "getIdentityCode",
    "mobile": "18301187051",
    "captcha": "1234"
}
```

**响应示例**：
```json
{
    "request_id": "oKXv9eCYuFIXoxRn",
    "trace_id": "",
    "code": 0,
    "type": 0,
    "msg": "success",
    "data": {
        "identity_code": "fbsk-2db251f6c8d74ce69ae3dcb82ed1055b"
    }
}
```

---

## 二、酒店查询接口

### 2.1 搜索酒店列表

**skill_type**: `searchHotelList`

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| skill_type | string | 是 | 固定值: searchHotelList |
| city_name | string | 是 | 城市名称（如"北京市"） |
| keywords | string | 否 | 关键词（用户输入原样传递） |
| hotel_name | string | 否 | 酒店名称 |
| page_index | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认5 |

**请求示例**：
```json
{
    "skill_type": "searchHotelList",
    "city_name": "北京市",
    "keywords": "预订北京国贸附近1公里的酒店",
    "page_index": 1,
    "page_size": 5
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|-----|------|------|
| code | int | 状态码，200=成功 |
| success | bool | 是否成功 |
| data.page_index | int | 当前页码 |
| data.page_size | int | 每页数量 |
| data.hotel_list[] | array | 酒店列表 |
| hotel_list[].hotel_id | string | 酒店ID |
| hotel_list[].fb_hotel_id | string | 分贝通酒店ID |
| hotel_list[].name | string | 酒店名称 |
| hotel_list[].star_level | string | 星级代码 |
| hotel_list[].star_level_name | string | 星级名称（经济型/舒适型/高档型/豪华型） |
| hotel_list[].star_num | int | 星级数字（2-5） |
| hotel_list[].address | string | 地址 |
| hotel_list[].phone | string | 电话 |
| hotel_list[].score | float | 评分 |
| hotel_list[].group_name | string | 集团名称 |
| hotel_list[].brand_name | string | 品牌名称 |
| hotel_list[].geolat | string | 纬度 |
| hotel_list[].geolon | string | 经度 |
| hotel_list[].nation_type | int | 1=国内 2=国际 |
| hotel_list[].city_code | string | 城市代码 |
| hotel_list[].city_name | string | 城市名称 |
| hotel_list[].district_code | string | 区域代码 |
| hotel_list[].district_name | string | 区域名称 |
| hotel_list[].business_zone_name | string | 商圈名称 |
| hotel_list[].main_logo | string | 酒店图片URL |
| hotel_list[].min_price | int | 最低价格 |

**响应示例**：
```json
{
    "code": 200,
    "success": true,
    "data": {
        "page_index": 1,
        "page_size": 5,
        "hotel_list": [
            {
                "hotel_id": "5a39df2fbbfdc4732360e860",
                "fb_hotel_id": "5a39df2fbbfdc4732360e860",
                "name": "北京建国饭店",
                "star_level": "2",
                "star_level_name": "高档型",
                "star_num": 4,
                "address": "建外大街5号",
                "phone": "+86-10-65002233",
                "score": 4.5,
                "group_name": "如家",
                "brand_name": "建国",
                "geolat": "39.909191096371885",
                "geolon": "116.45275202237526",
                "nation_type": 1,
                "city_code": "1000001",
                "city_name": "北京市",
                "district_code": "72",
                "district_name": "朝阳区",
                "business_zone_name": "国贸地区",
                "main_logo": "http://dimg04.c-ctrip.com/images/...",
                "min_price": 572
            }
        ]
    },
    "msg": "操作成功"
}
```

---

### 2.2 查询酒店价格详情

**skill_type**: `queryHotelPrice`

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| skill_type | string | 是 | 固定值: queryHotelPrice |
| hotel_id | string | 是 | 酒店ID |
| check_in_date | string | 是 | 入住日期 yyyy-MM-dd |
| check_out_date | string | 是 | 退房日期 yyyy-MM-dd |
| payment_type | string | 否 | 支付方式 PP=预付 SP=现付，默认PP |
| nation_type | int | 否 | 1=国内 2=国际，默认1 |

**请求示例**：
```json
{
    "skill_type": "queryHotelPrice",
    "nation_type": 1,
    "payment_type": "PP",
    "hotel_id": "5a39df2fbbfdc4732360eaa9",
    "check_in_date": "2026-03-27",
    "check_out_date": "2026-03-28"
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|-----|------|------|
| data.hotel | object | 酒店基本信息 |
| data.rooms[] | array | 房型列表 |
| rooms[].room_id | string | 房型ID |
| rooms[].room_name | string | 房型名称 |
| rooms[].bed_type | string | 床型描述 |
| rooms[].window_type | string | 窗户类型 |
| rooms[].area | string | 面积 |
| rooms[].status | bool | 是否可预订 |
| rooms[].plan_list[] | array | 产品列表 |
| plan_list[].plan_id | string | 产品ID |
| plan_list[].plan_name | string | 产品名称 |
| plan_list[].breakfast | object | 早餐信息 |
| plan_list[].cancel_type | object | 取消政策类型 |
| plan_list[].cancel_rule | string | 取消政策详情 |
| plan_list[].last_cancel_time | string | 最晚取消时间 |
| plan_list[].instant_confirm | bool | 是否即时确认 |
| plan_list[].payment_type | string | 支付方式 |
| plan_list[].room_count | int | 可预订房间数 |
| plan_list[].status | bool | 是否可预订 |
| plan_list[].total_price | float | 总价 |
| plan_list[].avg_price | float | 均价 |
| plan_list[].price_list[] | array | 每日价格列表 |

**响应示例**：
```json
{
    "code": 200,
    "success": true,
    "data": {
        "hotel": {
            "hotel_id": "5a39df2fbbfdc4732360eaa9",
            "name": "汉庭酒店(北京长虹桥店)",
            "star_level_name": "经济型",
            "star_num": 2,
            "address": "农展馆南里12号院5号楼",
            "score": 4.8
        },
        "rooms": [
            {
                "room_id": "e75914b2db3847929aa714339030063e",
                "room_name": "测试房型",
                "bed_type": "2张1.80m大床",
                "window_type": "有窗",
                "area": "22㎡",
                "status": true,
                "plan_list": [
                    {
                        "plan_id": "69b1250f792aedbe7f7653ee",
                        "plan_name": "标准价",
                        "breakfast": {"key": 1, "value": "单早"},
                        "cancel_type": {"key": 2, "value": "限时取消"},
                        "cancel_rule": "3月26日 12:00前免费取消，过时取消扣除全部房费",
                        "last_cancel_time": "2026-03-26 12:00:00",
                        "total_price": 1.06,
                        "avg_price": 1.06,
                        "status": true
                    }
                ]
            }
        ]
    }
}
```

---

### 2.3 查询酒店扩展详情

**skill_type**: `queryHotelDetail`

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| skill_type | string | 是 | 固定值: queryHotelDetail |
| hotel_id | string | 是 | 酒店ID |

**请求示例**：
```json
{
    "skill_type": "queryHotelDetail",
    "hotel_id": "5a39df2fbbfdc4732360eaa9"
}
```

---

### 2.4 查询酒店评论

**skill_type**: `queryHotelComment`

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| skill_type | string | 是 | 固定值: queryHotelComment |
| hotel_id | string | 是 | 酒店ID |
| page_index | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认5 |

**请求示例**：
```json
{
    "skill_type": "queryHotelComment",
    "hotel_id": "8502475",
    "page_size": 5
}
```

---

## 三、订单接口

### 3.1 酒店下单

**skill_type**: `createOrder`

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| skill_type | string | 是 | 固定值: createOrder |
| nation_type | int | 是 | 1=国内 2=国际 |
| payment_type | string | 是 | PP=预付 SP=现付 |
| hotel_id | string | 是 | 酒店ID |
| check_in_date | string | 是 | 入住日期 yyyy-MM-dd |
| check_out_date | string | 是 | 退房日期 yyyy-MM-dd |
| room_id | string | 是 | 房型ID |
| plan_id | string | 是 | 产品ID |
| total_price | float | 是 | 总价 |
| room_count | int | 是 | 房间数 |
| contact | object | 是 | 联系人信息 |
| contact.name | string | 是 | 联系人姓名 |
| contact.phone | string | 是 | 联系人电话 |
| guestList1 | array | 是 | 入住人列表（二维数组） |

**重要**：`guestList1` 必须是二维数组格式！

**请求示例**：
```json
{
    "skill_type": "createOrder",
    "nation_type": 1,
    "payment_type": "PP",
    "hotel_id": "5a39df2fbbfdc4732360eaa9",
    "check_in_date": "2026-03-27",
    "check_out_date": "2026-03-28",
    "room_id": "7617d7bbb3a94537a58bb3d33108b429",
    "plan_id": "69c23ae4e37c7d156e3e0c01",
    "total_price": 280,
    "room_count": 1,
    "contact": {
        "name": "周聪",
        "phone": "18301187051"
    },
    "guestList1": [
        [
            {
                "name": "周聪",
                "phone": "13126525502"
            }
        ]
    ]
}
```

---

### 3.2 取消订单

**skill_type**: `cancelOrder`

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| skill_type | string | 是 | 固定值: cancelOrder |
| order_id | string | 是 | 订单ID |
| cancel_reason | string | 否 | 取消原因 |

**请求示例**：
```json
{
    "skill_type": "cancelOrder",
    "order_id": "69c23b67e37c7d156e3e0c1b",
    "cancel_reason": "取消原因"
}
```

---

### 3.3 查询订单

**skill_type**: `queryOrder`

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| skill_type | string | 是 | 固定值: queryOrder |
| order_id | string | 是 | 订单ID |

**请求示例**：
```json
{
    "skill_type": "queryOrder",
    "order_id": "69c23b67e37c7d156e3e0c1b"
}
```

---

## 四、收银台支付

订单创建成功后，使用以下URL引导用户完成支付：

### 4.1 支付链接

```
{域名}/business/hotel/open/push/redirect?orderId={order_id}&type=0&token={access_token}
```

### 4.2 查看订单链接

```
{域名}/business/hotel/open/push/redirect?orderId={order_id}&type=1&token={access_token}
```

### 参数说明

| 参数 | 说明 |
|-----|------|
| orderId | 订单ID（创建订单时返回） |
| type | 0=支付页面，1=订单详情页面 |
| token | 身份编码（access-token） |

---

## 五、错误码说明

| 错误码 | 说明 |
|-------|------|
| 0 | 成功 |
| 200 | 成功 |
| -32 | 短信验证码不正确 |
| 500 | 服务器错误 |

---

## 六、枚举值

### 支付方式 (payment_type)

| 值 | 说明 |
|---|------|
| PP | 预付（需入住前完成支付） |
| SP | 前台现付 |

### 酒店类型 (nation_type)

| 值 | 说明 |
|---|------|
| 1 | 国内酒店 |
| 2 | 国际酒店 |

### 星级类型 (star_level_name)

| 名称 | 对应星级 |
|-----|---------|
| 经济型 | 2星级 |
| 舒适型 | 3星级 |
| 高档型 | 4星级 |
| 豪华型 | 5星级 |

---

## 七、cURL 示例

### 发送验证码
```bash
curl --location 'https://app-gate.fenbeitong.com/business/hotel/open/push/skill/access' \
--header 'Content-Type: application/json' \
--data '{
    "skill_type":"getMobileCaptcha",
    "mobile":"18301187051"
}'
```

### 搜索酒店
```bash
curl --location 'https://app-gate.fenbeitong.com/business/hotel/open/push/skill/access' \
--header 'access-token: fbsk-2db251f6c8d74ce69ae3dcb82ed1055b' \
--header 'Content-Type: application/json' \
--data '{
    "skill_type":"searchHotelList",
    "city_name":"北京市",
    "keywords":"国贸附近",
    "page_index":1,
    "page_size":5
}'
```

### 查询酒店价格
```bash
curl --location 'https://app-gate.fenbeitong.com/business/hotel/open/push/skill/access' \
--header 'access-token: fbsk-2db251f6c8d74ce69ae3dcb82ed1055b' \
--header 'Content-Type: application/json' \
--data '{
    "skill_type":"queryHotelPrice",
    "hotel_id":"5a39df2fbbfdc4732360e860",
    "check_in_date":"2026-03-27",
    "check_out_date":"2026-03-28"
}'
```

### 创建订单
```bash
curl --location 'https://app-gate.fenbeitong.com/business/hotel/open/push/skill/access' \
--header 'access-token: fbsk-2db251f6c8d74ce69ae3dcb82ed1055b' \
--header 'Content-Type: application/json' \
--data '{
    "skill_type":"createOrder",
    "nation_type":1,
    "payment_type":"PP",
    "hotel_id":"5a39df2fbbfdc4732360eaa9",
    "check_in_date":"2026-03-27",
    "check_out_date":"2026-03-28",
    "room_id":"7617d7bbb3a94537a58bb3d33108b429",
    "plan_id":"69c23ae4e37c7d156e3e0c01",
    "total_price":280,
    "room_count":1,
    "contact":{"name":"张三","phone":"13800138000"},
    "guestList1":[[{"name":"张三","phone":"13800138000"}]]
}'
```