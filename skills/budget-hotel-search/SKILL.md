---
name: fb-hotel-skill
description: 分贝通酒店预定助手，实时查询搜索酒店、展示酒店列表、查询酒店房型、展示房型产品和报价、预定酒店、查看订单、取消订单、查看酒店基础信息和酒店评论信息。
version: 3.2.0
metadata: {"openclaw": {"emoji": "🏨", "category": "travel", "tags": ["分贝通", "酒店", "房型", "预订", "退订", "报价"], "requires": {"bins": ["python3"]}, "required": true}}
---
# 分贝通酒店预定助手 (fb-hotel-skill)

## 技能描述

分贝通酒店预定助手，实时查询搜索酒店、展示酒店列表、查询酒店房型、展示房型产品和报价、预定酒店、查看订单、取消订单、查看酒店基础信息和酒店评论信息。

---

## 🔐 鉴权流程（必须先完成）

**重要**：使用任何功能前，用户必须先完成鉴权流程。鉴权成功后获得的 `identity_code`（access-token）会自动保存在 `~/.fbt-auth.json` 文件中，新会话会自动沿用。

### 鉴权步骤

#### 步骤 1：发送验证码
```
用户回复: 分贝通登录
AI: 请输入您的手机号以接收验证码（例如：13800138000）

用户输入: 13800138000
AI: ✅ 验证码已发送到 138****8000，请在5分钟内输入验证码
```

**API调用**：
```python
from scripts.fb_hotel_api import send_verification_code

result = send_verification_code("13800138000")
# 成功响应: {"code": 0, "msg": "success", "data": true}
```

#### 步骤 2：验证并获取 identity_code
```
用户输入: 1234
AI: 🎉 认证成功！身份编码已保存到 ~/.fbt-auth.json，有效期90天
    现在可以使用分贝通企业接口了
```

**API调用**：
```python
from scripts.fb_hotel_api import verify_and_get_token

success, result = verify_and_get_token("13800138000", "1234")
if success:
    access_token = result  # fbsk-xxx
    # token 已自动保存到 ~/.fbt-auth.json
else:
    print(f"验证失败: {result}")
```

#### 步骤 3：自动注入（后续调用）

后续所有 API 调用会自动从 `~/.fbt-auth.json` 读取 token：

```python
from scripts.fb_hotel_api import FbHotelApi

# 无需传入 token，自动从文件读取
api = FbHotelApi()
result = api.search_hotel_list(city_name="北京市", keywords="国贸")
```

### Token 存储管理

| 文件 | 路径 | 说明 |
|-----|------|------|
| 鉴权文件 | `~/.fbt-auth.json` | 保存 identity_code 和手机号 |

**文件格式**：
```json
{
  "identity_code": "fbsk-2db251f6c8d74ce69ae3dcb82ed1055b",
  "mobile": "138****8000",
  "created_at": "2026-03-25T09:48:00",
  "updated_at": "2026-03-25T09:48:00"
}
```

### API 函数

```python
from scripts.fb_hotel_api import (
    save_auth_token,    # 保存 token
    load_auth_token,    # 读取 token
    get_auth_info,      # 获取完整认证信息
    clear_auth_token    # 清除认证信息
)

# 保存 token
save_auth_token("fbsk-xxx", "13800138000")

# 读取 token
token = load_auth_token()

# 获取完整信息
info = get_auth_info()  # {"identity_code": "...", "mobile": "..."}

# 清除认证
clear_auth_token()
```

### 接口鉴权说明

| skill_type | 接口名称 | 需要认证 |
|------------|---------|---------|
| `getMobileCaptcha` | 获取手机号验证码 | ❌ 否 |
| `getIdentityCode` | 获取身份编码 | ❌ 否 |
| `searchHotelList` | 搜索酒店列表 | ✅ 是 |
| `queryHotelPrice` | 查询酒店价格详情 | ✅ 是 |
| `queryHotelDetail` | 查询酒店扩展详情 | ✅ 是 |
| `queryHotelComment` | 查询酒店评论 | ✅ 是 |
| `createOrder` | 酒店下单 | ✅ 是 |
| `cancelOrder` | 取消订单 | ✅ 是 |
| `queryOrder` | 查询订单 | ✅ 是 |

---

⚠️ 【重要约束】
- 必须调用 `scripts/fb_hotel_api.py` 中的函数获取数据
- 禁止自行编造酒店信息、价格或评论
- 接口返回什么数据就展示什么，不要修改
- **首次使用必须先完成分贝通企业认证**

---

## 对接信息

### 环境配置

| 环境 | 域名 |
|-----|------|
| **FAT 测试环境** | `https://app-gate.fenbeitong.com` |
| **线上环境** | `https://app-gate.fenbeitong.com` |

### 统一接口入口

**所有接口统一使用同一入口**：
```
POST /business/hotel/open/push/skill/access
```

通过 `skill_type` 参数区分不同操作。

### 请求格式

**Headers**:
```
Content-Type: application/json
access-token: fbsk-xxx  （认证类接口除外）
```

**Body**:
```json
{
    "skill_type": "searchHotelList",
    // 其他参数...
}
```

---

## 核心接口列表

### 一、认证类接口

#### 1. 获取手机号验证码

**skill_type**: `getMobileCaptcha`

**请求示例**：
```bash
curl --location 'https://app-gate.fenbeitong.com/business/hotel/open/push/skill/access' \
--header 'Content-Type: application/json' \
--data '{
    "skill_type":"getMobileCaptcha",
    "mobile":"18301187051"
}'
```

**响应示例**：
```json
{
    "request_id": "nQabT9pHt5u5m0mA",
    "code": 0,
    "msg": "success",
    "data": true
}
```

#### 2. 获取身份编码

**skill_type**: `getIdentityCode`

**请求示例**：
```bash
curl --location 'https://app-gate.fenbeitong.com/business/hotel/open/push/skill/access' \
--header 'Content-Type: application/json' \
--data '{
    "skill_type":"getIdentityCode",
    "mobile":"18301187051",
    "captcha":"1234"
}'
```

**响应示例**：
```json
{
    "request_id": "oKXv9eCYuFIXoxRn",
    "code": 0,
    "msg": "success",
    "data": {
        "identity_code": "fbsk-2db251f6c8d74ce69ae3dcb82ed1055b"
    }
}
```

---

### 二、酒店查询接口

#### 1. 搜索酒店列表

**skill_type**: `searchHotelList`

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| city_name | string | 是 | 城市名称（如"北京市"） |
| keywords | string | 否 | 关键词（用户输入原样传递） |
| hotel_name | string | 否 | 酒店名称 |
| page_index | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认5 |

**请求示例**：
```bash
curl --location 'https://app-gate.fenbeitong.com/business/hotel/open/push/skill/access' \
--header 'access-token: fbsk-2db251f6c8d74ce69ae3dcb82ed1055b' \
--header 'Content-Type: application/json' \
--data '{
    "skill_type":"searchHotelList",
    "city_name":"北京市",
    "keywords":"预订北京国贸附近1公里的酒店",
    "page_index":1,
    "page_size":5
}'
```

**响应字段**：
| 字段 | 说明 |
|-----|------|
| hotel_id | 酒店ID |
| name | 酒店名称 |
| star_level_name | 星级类型（高档型、豪华型等） |
| address | 地址 |
| district_name | 区域 |
| business_zone_name | 商圈 |
| score | 评分 |
| min_price | 最低价 |
| main_logo | 酒店图片 |

#### 2. 查询酒店价格详情

**skill_type**: `queryHotelPrice`

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| hotel_id | string | 是 | 酒店ID |
| check_in_date | string | 是 | 入住日期 yyyy-MM-dd |
| check_out_date | string | 是 | 退房日期 yyyy-MM-dd |
| payment_type | string | 否 | 支付方式 PP=预付 SP=现付 |
| nation_type | int | 否 | 1=国内 2=国际 |

**请求示例**：
```bash
curl --location 'https://app-gate.fenbeitong.com/business/hotel/open/push/skill/access' \
--header 'access-token: fbsk-2db251f6c8d74ce69ae3dcb82ed1055b' \
--header 'Content-Type: application/json' \
--data '{
    "skill_type":"queryHotelPrice",
    "nation_type":1,
    "payment_type":"PP",
    "hotel_id":"5a39df2fbbfdc4732360eaa9",
    "check_in_date":"2026-03-27",
    "check_out_date":"2026-03-28"
}'
```

**响应字段**：
| 字段 | 说明 |
|-----|------|
| hotel | 酒店基本信息 |
| rooms[] | 房型列表 |
| rooms[].room_id | 房型ID |
| rooms[].room_name | 房型名称 |
| rooms[].bed_type | 床型 |
| rooms[].window_type | 窗户类型 |
| rooms[].area | 面积 |
| rooms[].status | 是否可预订 |
| rooms[].plan_list[] | 产品列表 |
| plan_list[].plan_id | 产品ID |
| plan_list[].plan_name | 产品名称 |
| plan_list[].breakfast | 早餐 |
| plan_list[].cancel_type | 取消政策类型 |
| plan_list[].cancel_rule | 取消政策详情 |
| plan_list[].total_price | 总价 |
| plan_list[].status | 是否可预订 |

#### 3. 查询酒店扩展详情

**skill_type**: `queryHotelDetail`

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| hotel_id | string | 是 | 酒店ID |

#### 4. 查询酒店评论

**skill_type**: `queryHotelComment`

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| hotel_id | string | 是 | 酒店ID |
| page_index | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**请求示例**：
```bash
curl --location 'https://app-gate.fenbeitong.com/business/hotel/open/push/skill/access' \
--header 'access-token: fbsk-2db251f6c8d74ce69ae3dcb82ed1055b' \
--header 'Content-Type: application/json' \
--data '{
    "skill_type":"queryHotelComment",
    "hotel_id":"8502475",
    "page_size":5
}'
```

---

### 三、订单接口

#### 1. 酒店下单

**skill_type**: `createOrder`

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| nation_type | int | 是 | 1=国内 2=国际 |
| payment_type | string | 是 | PP=预付 SP=现付 |
| hotel_id | string | 是 | 酒店ID |
| check_in_date | string | 是 | 入住日期 |
| check_out_date | string | 是 | 退房日期 |
| room_id | string | 是 | 房型ID |
| plan_id | string | 是 | 产品ID |
| total_price | float | 是 | 总价 |
| room_count | int | 是 | 房间数 |
| contact | object | 是 | 联系人信息 |
| guestList1 | array | 是 | 入住人列表（二维数组） |

**请求示例**：
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
    "contact":{
        "name":"周聪",
        "phone":"18301187051"
    },
    "guestList1":[
        [
            {
                "name":"周聪",
                "phone":"13126525502"
            }
        ]
    ]
}'
```

**重要**：`guestList1` 参数必须为二维数组格式！

#### 2. 取消订单

**skill_type**: `cancelOrder`

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| order_id | string | 是 | 订单ID |
| cancel_reason | string | 否 | 取消原因 |

**请求示例**：
```bash
curl --location 'https://app-gate.fenbeitong.com/business/hotel/open/push/skill/access' \
--header 'access-token: fbsk-2db251f6c8d74ce69ae3dcb82ed1055b' \
--header 'Content-Type: application/json' \
--data '{
    "skill_type":"cancelOrder",
    "order_id": "69c23b67e37c7d156e3e0c1b",
    "cancel_reason":"取消原因"
}'
```

#### 3. 查询订单

**skill_type**: `queryOrder`

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| order_id | string | 是 | 订单ID |

**请求示例**：
```bash
curl --location 'https://app-gate.fenbeitong.com/business/hotel/open/push/skill/access' \
--header 'access-token: fbsk-2db251f6c8d74ce69ae3dcb82ed1055b' \
--header 'Content-Type: application/json' \
--data '{
    "skill_type":"queryOrder",
    "order_id": "69c23b67e37c7d156e3e0c1b"
}'
```

---

### 四、收银台支付

订单创建成功后，通过以下链接引导用户完成支付：

| 类型 | 链接格式 |
|-----|---------|
| 立即支付 | `{域名}/business/hotel/open/push/redirect?orderId={order_id}&type=0&token={access_token}` |
| 查看订单 | `{域名}/business/hotel/open/push/redirect?orderId={order_id}&type=1&token={access_token}` |

**FAT环境示例**：
- 支付：`https://app-gate.fenbeitong.com/business/hotel/open/push/redirect?orderId={order_id}&type=0&token=fbsk-xxx`
- 订单：`https://app-gate.fenbeitong.com/business/hotel/open/push/redirect?orderId={order_id}&type=1&token=fbsk-xxx`

---

## 使用流程

### 1. 酒店搜索

**触发条件**：用户输入「酒店搜索/订酒店/找酒店/搜酒店」+ 城市/关键词

**步骤**：
1. 检查用户认证状态
2. 调用 `search_hotel_list()` 获取酒店列表
3. 格式化展示酒店列表（表格形式）

**展示格式**：
```
🏨 北京国贸附近酒店

| 序号 | 酒店名称 | 星级 | 区域 | 最低价 |
|:---:|---------|:---:|------|---:|
| 1 | 北京建国饭店 | 高档型 | 朝阳区 | ¥572 |
| 2 | 北京共享际5L饭店 | 高档型 | 朝阳区 | ¥712 |

💡 回复序号查看房型价格，如"1"
💡 回复"序号-详情"查看酒店信息和评论，如"1-详情"
```

### 2. 查看房型价格

**触发条件**：用户回复序号（如"1"）

**步骤**：
1. 获取酒店ID（从之前的搜索结果）
2. 调用 `query_hotel_price()` 获取房型和产品
3. 过滤 status=false 的房型和产品
4. 展示前5个房型，每个房型展示前5个产品

**展示格式**：
```
🏨 汉庭酒店(北京长虹桥店)
📍 农展馆南里12号院5号楼 | ⭐4.8分 | 经济型
📅 入住：2026-03-27 → 退房：2026-03-28

**房型1：测试房型**
床型：2张1.80m大床 | 窗户：有窗 | 面积：22㎡
| 序号 | 价格 | 早餐 | 取消政策 | 取消详情 |
|:---:|---:|:---:|:---:|---|
| 1-1 | ¥1 | 单早 | ✅限时取消 | 3月26日 12:00前免费取消... |

💡 回复"房型序号-产品序号"预订，如"1-1"
```

### 3. 创建订单

**触发条件**：用户回复"房型序号-产品序号"（如"1-1"）

**步骤**：
1. 收集入住人信息（姓名、手机号）
2. 构建请求参数（注意 guestList1 为二维数组）
3. 调用 `create_order()` 创建订单
4. 展示订单信息和支付链接

**展示格式**：
```
✅ 订单创建成功！

🏨 订单号：69c23b67e37c7d156e3e0c1b
📅 入住：2026-03-27 → 退房：2026-03-28
🛏️ 房型：测试房型
💰 价格：¥280
📋 最晚取消时间：2026-03-26 12:00:00

🔗 [立即支付](https://app-gate.fenbeitong.com/...)
🔗 [查看订单详情](https://app-gate.fenbeitong.com/...)
```

---

## Python API 参考

```python
from scripts.fb_hotel_api import FbHotelApi, send_verification_code, verify_and_get_token

# 初始化（使用默认token或指定token）
api = FbHotelApi(access_token="fbsk-xxx")

# 发送验证码
result = send_verification_code("13800138000")

# 验证并获取token
success, token = verify_and_get_token("13800138000", "1234")

# 搜索酒店
result = api.search_hotel_list(
    city_name="北京市",
    keywords="国贸附近",
    page_size=5
)

# 查询酒店价格
result = api.query_hotel_price(
    hotel_id="5a39df2fbbfdc4732360e860",
    check_in_date="2026-03-27",
    check_out_date="2026-03-28"
)

# 查询酒店扩展详情
result = api.query_hotel_detail(hotel_id="5a39df2fbbfdc4732360e860")

# 查询酒店评论
result = api.query_hotel_comment(hotel_id="8502475", page_size=5)

# 创建订单
result = api.create_order(
    hotel_id="5a39df2fbbfdc4732360eaa9",
    room_id="7617d7bbb3a94537a58bb3d33108b429",
    plan_id="69c23ae4e37c7d156e3e0c01",
    check_in_date="2026-03-27",
    check_out_date="2026-03-28",
    total_price=280,
    contact={"name": "张三", "phone": "13800138000"},
    guest_list=[[{"name": "张三", "phone": "13800138000"}]]
)

# 查询订单
result = api.query_order(order_id="69c23b67e37c7d156e3e0c1b")

# 取消订单
result = api.cancel_order(order_id="69c23b67e37c7d156e3e0c1b", cancel_reason="不想要了")

# 格式化输出
print(api.format_hotel_list(result))
print(api.format_hotel_price(result, "2026-03-27", "2026-03-28"))
```

---

## 📝 格式化输出模块

**文件位置**：`scripts/formatter.py`

### 展示配置

| 配置项 | 默认值 | 说明 |
|-------|-------|------|
| HOTEL_LIST_LIMIT | 5 | 酒店列表展示数量 |
| ROOM_LIST_LIMIT | 5 | 房型展示数量 |
| PLAN_LIST_LIMIT | 5 | 每个房型展示的产品数量 |

### 格式化函数

```python
from scripts.formatter import (
    format_hotel_list,      # 酒店列表格式化
    format_hotel_rooms,     # 房型价格格式化
    format_order_result,    # 订单创建结果格式化
    format_trip_plan,       # 行程规划格式化
    format_order_confirmation,  # 订单确认格式化
    format_order_detail_full    # 完整订单详情格式化
)
```

### 展示字段规范

**酒店列表必须包含**：
- 序号、酒店名称、评分、星级、地址、最低价

**房型价格必须包含**：
- 序号、房型名称、床型、面积、窗户类型
- 价格、早餐、取消政策类型、取消详情

**订单详情必须包含**：
- 订单号、酒店信息、房型信息
- 床型、面积、窗户、早餐、价格
- 取消政策类型和详情
- **[立即支付]** 按钮（不是"查看订单详情"）

---

## 版本历史

| 版本 | 日期 | 变更说明 |
|-----|------|---------|
| 3.1.0 | 2026-03-25 | 新增格式化输出模块，固化展示逻辑 |
| 3.0.0 | 2026-03-25 | 统一接口入口，新增认证流程，重构API |
| 2.9.1 | 2026-03-20 | 修复订单创建问题 |
| 1.9.1 | 2026-03-15 | 新增酒店评论查询 |