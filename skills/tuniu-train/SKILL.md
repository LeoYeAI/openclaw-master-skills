---
name: tuniu-train
description: 途牛火车票助手 - 通过 exec + curl 调用 MCP 实现车次列表搜索、查询车次详情、预订下单。适用于用户查询车次列表、查询车次详情或提交火车票订单时使用。
version: 1.0.0
metadata: {"openclaw": {"emoji": "🚄", "category": "travel", "tags": ["途牛", "火车票", "车次详情", "下单"], "requires": {"bins": ["curl"]}, "env": {"TUNIU_API_KEY": {"type": "string", "description": "途牛开放平台 API key，用于 apiKey 请求头", "required": true}}}}
---

# 途牛火车票助手

当用户查询车次列表、查询具体车次详情或火车票预订时，使用此 skill 通过 exec 执行 curl 调用途牛火车票 MCP 服务。

## 运行环境要求

本 skill 通过 **shell exec** 执行 **curl** 向 MCP endpoint 发起 HTTP POST 请求，使用 JSON-RPC 2.0 / `tools/call` 协议。**运行环境必须提供 curl 或等效的 HTTP 调用能力**（如 wget、fetch 等可发起 POST 的客户端），否则无法调用 MCP 服务。

## 隐私与个人信息（PII）说明

预订功能会将用户提供的**个人信息**（联系人姓名、手机号、乘客姓名、证件号等）通过 HTTP POST 发送至途牛火车票 MCP 远端服务（`https://openapi.tuniu.cn/mcp/train`） ，以完成火车票预订。使用本 skill 即表示用户知晓并同意上述 PII 被发送到外部服务。请勿在日志或回复中暴露用户个人信息。

## 适用场景

- 按出发站、到达站、出发日期查询车次列表（第一页、翻页）
- 查看指定车次的坐等价格信息
- 用户确认后创建火车票预订订单

## 配置要求

### 必需配置

- **TUNIU_API_KEY**：途牛开放平台 API key，用于 `apiKey` 请求头

用户需在[途牛开放平台](https://open.tuniu.com/mcp)注册并获取上述密钥。

### 可选配置

- **TRAIN_MCP_URL**：MCP 服务地址，默认 `https://openapi.tuniu.cn/mcp/train`

## 调用方式

**直接调用工具**：使用以下请求头调用 `tools/call` 即可：

- `apiKey: $TUNIU_API_KEY`
- `Content-Type: application/json`
- `Accept: application/json, text/event-stream`

## 可用工具

**重要**：下方示例中的参数均为占位，调用时需**根据用户当前需求**填入实际值（出发站、出发日期、车次号、出行人、联系方式等），勿直接照抄示例值。

### 1. 查询车次列表 (searchLowestPriceTrain)

**首次查询**：必填 `departureCityName`、`arrivalCityName`、`departureDate`（格式 yyyy-MM-dd），非必填 `departureTime`(出发时间范围,如`08:00-12:00`)、`arrivalTime`(到达时间范围,如`18:00-20:00`)。


入参示例:
```markdown
{
    "departureCityName": "南京",//出发站
    "arrivalCityName": "上海",//到达站
    "departureDate": "2026-03-20",//出发日期
    "departureTime": "08:00-12:00",//出发时间范围
    "arrivalTime": "18:00-20:00"//到达时间范围
}
```

出参示例：
```markdown
{
  "successCode": true,
  "data": [
    {
      "trainNum": "1461",//车次号
      "departStationName": "南京",//出发站名称
      "destStationName": "上海",//到达站名称
      "trainType": "direct",
      "departureTime": "2026-03-20 03:04",//出发时间
      "arrivalTime": "2026-03-20 06:45",//到达时间
      "price": {
        "gjrwPrice": "",//高级软卧价格,“”表示无此坐等
        "rwPrice": "140.5",//软卧价格
        "rzPrice": "",//软座价格
        "swzPrice": "",//商务座价格
        "tdzPrice": "",//特等座价格
        "wzPrice": "",//无座价格
        "ywPrice": "94.5",//硬卧价格
        "yzPrice": "40.5",//硬座价格
        "edzPrice": "",//二等座价格
        "ydzPrice": "",//一等座价格
        "dwPrice": "",//动卧价格
        "ydwPrice": "",//一等卧价格
        "edwPrice": ""//二等卧价格
      },
      "duration": "3时41分",//运行时长
      "seatAvailable": {
        "gjrwNum": null,//高级软卧余票数量,null表示无此坐等,0表示没有余票,大于0表示有票
        "rwNum": 0,//软卧余票数量
        "rzNum": null,//软座余票数量
        "swzNum": null,//商务座余票数量
        "tdzNum": null,//特等座余票数量
        "wzNum": null,//无座余票数量
        "ywNum": 0,//硬卧余票数量
        "yzNum": 0,//硬座余票数量
        "edzNum": null,//二等座余票数量
        "ydzNum": null,//一等座余票数量
        "dwNum": null,//动卧余票数量
        "ydwNum": null,//一等卧余票数量
        "edwNum": null//二等卧余票数量
      }
    }
  ],
  "queryId": "65979499413539",//快照id
  "totalPageNum": 10//总页数
}
```


**非首次查询**：传入首次查询返回的快照id(queryId)和 `pageNum`（2=第二页，3=第三页…）。用户说「还有吗」「翻页」「下一页」时用queryId + pageNum 再次调用即可。

入参示例：
```markdown
{
    "queryId": "65979499413539",//快照id
    "pageNum": 2//页数
}
```

出参示例：
```markdown
{
  "successCode": true,
  "data": [
    {
      "trainNum": "K1505",//车次号
      "departStationName": "南京",//出发站名称
      "destStationName": "上海",//到达站名称
      "trainType": "direct",
      "departureTime": "2026-03-20 18:41",//出发时间
      "arrivalTime": "2026-03-20 22:22",//到达时间
      "price": {
        "gjrwPrice": "",//高级软卧价格,“”表示无此坐等
        "rwPrice": "146.5",//软卧价格
        "rzPrice": "",//软座价格
        "swzPrice": "",//商务座价格
        "tdzPrice": "",//特等座价格
        "wzPrice": "46.5",//无座价格
        "ywPrice": "100.5",//硬卧价格
        "yzPrice": "46.5",//硬座价格
        "edzPrice": "",//二等座价格
        "ydzPrice": "",//一等座价格
        "dwPrice": "",//动卧价格
        "ydwPrice": "",//一等卧价格
        "edwPrice": ""//二等卧价格
      },
      "duration": "3时41分",//运行时长
      "seatAvailable": {
        "gjrwNum": null,//高级软卧余票数量,null表示无此坐等,0表示没有余票,大于0表示有票
        "rwNum": 4,//软卧余票数量
        "rzNum": null,//软座余票数量
        "swzNum": null,//商务座余票数量
        "tdzNum": null,//特等座余票数量
        "wzNum": 0,//无座余票数量
        "ywNum": 17,//硬卧余票数量
        "yzNum": 0,//硬座余票数量
        "edzNum": null,//二等座余票数量
        "ydzNum": null,//一等座余票数量
        "dwNum": null,//动卧余票数量
        "ydwNum": null,//一等卧余票数量
        "edwNum": null//二等卧余票数量
      }
    }
  ]
}
```


**触发词**：查询某日出发某站到某站的火车票

```bash
# 首次查询：出发站、到达站、出发日期按用户需求填写（日期格式 yyyy-MM-dd）
curl -s -X POST "${TRAIN_MCP_URL:-https://openapi.tuniu.cn/mcp/train}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"searchLowestPriceTrain","arguments":{"departureCityName":"<用户指定的出发站>","arrivalCityName":"<用户指定的到达站>","departureDate":"<用户指定的出发日期 yyyy-MM-dd>","departureTime":"<用户指定的出发时间范围,如08:00-12:00>","arrivalTime":"<用户指定的到达时间范围,如18:00-20:00>"}}}'
```

```bash
# 非首次查询：快照id(queryId) + pageNum
curl -s -X POST "${TRAIN_MCP_URL:-https://openapi.tuniu.cn/mcp/train}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"searchLowestPriceTrain","arguments":{"queryId":"<快照id>","pageNum":2}}}'
```

### 2. 查询车次详情 (queryTrainDetail)

**入参**：`departureStationName`、`arrivalStationName`、`departureDate`（yyyy-MM-dd）、`trainNum`（车次号，从搜索结果获取）均为必填。

入参示例：
```markdown
{
    "departureStationName": "南京南",//出发站
    "arrivalStationName": "上海虹桥",//到达站
    "departureDate": "2026-03-20",//出发日期
    "trainNum": "G203"//车次号
}
```

**返回**：`trainInfo`（车次详情）、`seatInfo`（坐等信息，含 resId、price等）。**resId、price、departsDate 为下单必填，需保留供 bookTrain 使用。**

出参示例：
```markdown
{
  "successCode": true,
  "data": {
    "isVoucherSaleForDetail": true,
    "isVoucherSaleForGrab": "0",
    "trainInfo": {
      "id": "16203",
      "trainId": "16203",//车次id
      "trainNum": "G203",//车次号
      "trainType": 0,//车次类型;0:高铁;1:城际;2:动车;3:直达;4:特快;5:普快;6:其他
      "trainTypeCode": 0,//车次类型code
      "trainTypeName": "高铁",//车次类型名称
      "departCityId": "1602",//出发城市id
      "destCityId": "2500",//到达城市id
      "departStationName": "南京南",//出发站名称
      "departStationCode": "1175373",//出发站code
      "departStationType": "始发",//出发站是否始发;0:始发；1:终点；2:过路
      "departStationTypeCode": 0,//出发站是否始发code;0:始发；1:终点；2:过路
      "departureCityName": "南京",//出发城市名称
      "destStationName": "上海虹桥",//到达站名称
      "destStationCode": "1175076",//到达站code
      "destStationType": "过路",//到达站是否终点;0:始发；1:终点；2:过路
      "destStationTypeCode": 2,//到达站是否终点code;0:始发；1:终点；2:过路
      "arrivalCityName": "上海",//到达城市名称
      "departTime": "06:32",//出发时间
      "arriveTime": "07:53",//到达时间
      "saleStatus": "在售",//售卖状态;0:在售;1:停售;2:预售
      "saleStatusId": 0,//售卖状态id;0:在售;1:停售;2:预售
      "duration": "1时21分",//运行时长
      "durationDay": 1,//历时天数;1:当天;2:第二天
      "departsDate": "2026-03-20",//出发日期
      "arriveDate": "2026-03-20",//到达日期
      "memoDay": "",
      "memoHour": "",
      "departureDates": {
        "yesterday": "2026-03-19",
        "today": "2026-03-20",
        "tomorrow": "2026-03-21"
      },
      "leftNumber": 99,
      "seat": "二等座",
      "price": 141.0,
      "promotionPrice": 141.0,
      "resId": 99,
      "canGrap": true,
      "oneLeftNumber": 0,
      "supportSeatSelection": true,
      "supportIdCheckin": true,
      "supportTransferFlag": false
    },
    "seatInfo": [
      {
        "leftNumber": 99,//余票数量
        "seatId": 3,//坐等id;0：商务座;1：特等座;2：一等座;3：二等座;4：高级软卧;5：软卧;6：硬卧;7：软座;8：硬座;9：无座;10：动卧;19.一等卧;20.二等卧
        "seatName": "二等座",//坐等名称
        "price": 141.0,//坐等价格
        "adultPrice": 141.0,
        "promotionPrice": 141.0,
        "resId": 2121337089,//资源id
        "seatStatus": "有",//坐等状态
        "seatSequence": 0,
        "lowestPrice": null,
        "isConfigSeat": false,
        "configSeatInfo": null,
        "isSupportVoucherSection": true,
        "trainVoucherInfo": []
      },
      {
        "leftNumber": 0,
        "seatId": 2,
        "seatName": "一等座",
        "price": 238.0,
        "adultPrice": 238.0,
        "promotionPrice": 238.0,
        "resId": 2121337088,
        "seatStatus": "",
        "seatSequence": 6,
        "lowestPrice": null,
        "isConfigSeat": false,
        "configSeatInfo": null,
        "isSupportVoucherSection": false,
        "trainVoucherInfo": []
      },
      {
        "leftNumber": 0,
        "seatId": 0,
        "seatName": "商务座",
        "price": 459.0,
        "adultPrice": 459.0,
        "promotionPrice": 459.0,
        "resId": 2121337087,
        "seatStatus": "",
        "seatSequence": 9,
        "lowestPrice": null,
        "isConfigSeat": false,
        "configSeatInfo": null,
        "isSupportVoucherSection": false,
        "trainVoucherInfo": []
      },
      {
        "leftNumber": 0,
        "seatId": 9,
        "seatName": "无座",
        "price": 141.0,
        "adultPrice": 141.0,
        "promotionPrice": 141.0,
        "resId": 2121337090,
        "seatStatus": "",
        "seatSequence": 13,
        "lowestPrice": null,
        "isConfigSeat": false,
        "configSeatInfo": null,
        "isSupportVoucherSection": false,
        "trainVoucherInfo": []
      }
    ],
    "isOpen": 1,
    "needAdd": false,
    "departureDates": {
      "yesterday": "2026-03-19",
      "today": "2026-03-20",
      "tomorrow": "2026-03-21"
    },
    "couponsConfig": {
      "displaySwitch": true,
      "recommendText": "用车特价券售卖"
    }
  }
}
```

**触发词**：查询G203车次详情

```bash
# departureStationName、arrivalStationName、departureDate 从搜索结果或用户需求取，trainNum 从搜索结果取
curl -s -X POST "${TRAIN_MCP_URL:-https://openapi.tuniu.cn/mcp/train}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"queryTrainDetail","arguments":{"departureStationName":"<出发站>","arrivalStationName":"<到达站>","departureDate":"<出发日期 yyyy-MM-dd>","trainNum":"<车次号>"}}}'
```

### 3. 预定订单 (bookTrain)

**前置条件**：
- 必须先调用 `searchLowestPriceTrain` 获取车次列表信息
- 必须调用 `queryTrainDetail` 获取车次详情；从返回的 `seatInfo` 中选取坐等，拿到 `resId`、`price`、，从`trainInfo`中获取`departureDate`

**必填参数**：resources(资源信息)、adultTourists（乘客信息）、contact（联系人信息）、acceptStandingTicket(是否接受无座)。

**resources 格式**：

| 字段 | 类型 | 说明 |
|------|------|------|
| resourceId | long | 资源id |
| departsDate | string | 出发日期 |
| adultPrice | BigDecimal | 价格 |


**adultTourists 格式**：

| 字段 | 类型 | 说明                 |
|------|------|--------------------|
| name | string | 姓名                 |
| psptType | number | 证件类型;1:身份证,;2:护照   |
| psptId | string | 证件号码               |
| isStuDisabledArmyPolice| number | 乘客类型;0:成人 |
| tel | string | 手机号                |

**contact 格式**：

| 字段 | 类型 | 说明 |
|------|------|------|
| tel | string | 联系人手机号 |

入参示例：
```markdown
{
	"acceptStandingTicket": false,
	"adultTourists": [
		{
			"name": "张宁",//乘客姓名
			"psptId": "110101199001014534",//乘客证件号码
			"psptType": 1,//证件类型;1:身份证;2:护照
			"isStuDisabledArmyPolice": 0,//乘客类型;0:身份证
			"tel": "18888888888"//乘客手机号
		}
	],
	"contact": {
		"tel": "18888888888"//联系人手机号
	},
	"resources": [
		{
			"resourceId": 2107616437,//坐等对应资源id
			"adultPrice": 104.5,//坐等对应价格
			"departsDate": "2026-03-24"//出发日期
		}
	]
}
```

**返回**：`orderId`（下单成功的订单号）、`orderDetailUrl`（订单详情url）。

出参示例：
```markdown
{
	"successCode": true,
	"data": {
		"orderId": <订单号>,
		"orderDetailUrl": "<订单详情url>"
	}
}
```


**触发词**：预订、下单、订火车票

```bash
# resId、price、departureDate 从最近一次 queryTrainDetail 结果取；乘客信息、联系人按用户需求填
curl -s -X POST "${TRAIN_MCP_URL:-https://openapi.tuniu.cn/mcp/train}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "tools/call",
    "params": {
      "name": "bookTrain",
      "arguments": {
        "acceptStandingTicket": false,
        "adultTourists": [
          {
              "isStuDisabledArmyPolice": 0,
              "name": "<乘客姓名>",
              "psptId": "<乘客证件号码>",
              "psptType": <证件类型>,
              "tel": "<乘客手机号>"
          }
        ],
        "contact": {
          "tel": "<联系人手机号>"
        },
        "resources": [
          {
              "adultPrice": <坐等对应的价格>,
              "departsDate": "<出发日期>",
              "resourceId": <坐等对应的资源id>,
              "resourceType": 8
          }
        ]
      }
    }
  }'
```


### 4. 查询订单详情 (queryTrainOrderDetail)
**入参**：`orderId`必填。

入参示例：
```markdown
{
    "orderId": <订单号>
}
```

**返回**：`successCode`（成功标识,true:成功;false:失败）、`errorMessage`（失败原因）、`data`(订单详细信息)。

出参示例：
```markdown
{
  "successCode": true,
  "data": {
    "localProductType": "COMMON",//火车票订单本地产品类型,默认COMMON
    "orderId": 1257118322,//订单号
    "mainOrderId": null,
    "statusName": "已取消",//对客订单状态名;待出票;处理中;待付款;购票成功;取消中;退票中;退票成功;已取消;购票失败;已取纸质票;退票失败
    "payStatusName": "未付款",//订单支付状态:未付款;已付款完成;已退款完成
    "payStatus": 1,//支付状态;1:待付款;2:等待付款;3:部分付款;4:已付款完成;5:等待退款;6:已退款完成;7:已部分退款;8:已线下退款
    "payAmount": 0,//支付金额
    "totalPrice": 0,//订单总价
    "reducePrice": 0,//立减金额
    "travelCouponPrice": 0,//旅游券金额
    "bussinessCardPrice": 0,//商旅卡金额
    "isAdvancePay": 1,//是否为虚占提前支付订单;0:不是提前支付;1:是提前支付
    "isJoinActivity": 0,//是否是参加活动订单;0:没有参加活动;1:参加了24小时抢票赔付活动
    "promotionPrice": 0,促销活动金额
    "dispatchDeliverPrice": 0,//配送费
    "dispatchPurchasePrice": 0,//代购费
    "trainOrderType": "单程票",//火车票订单类型
    "deliveryType": "自取票",//取票方式
    "failReason": "",//失败原因
    "addTime": "2026-03-13 13:11:47",//下单时间
    "updateTime": "2026-03-13 13:22:42",//更新时间
    "clearTime": "2026-03-13 13:41:48",//清位时间
    "contact": {
      "name": "",
      "appellation": null,
      "email": "",
      "phone": "",
      "tel": "18888888888",//联系人手机号
      "fabId": null
    },
    "touristList": [
      {
        "touristId": 68472893,//订单乘客id
        "touristName": "张宁",//乘客姓名
        "touristType": 0,//出游人类型;0:成人;1:儿童;5:学生
        "psptType": 1,//证件类型;1:身份证;2:因私护照
        "psptId": "110101199001014534",//证件号
        "birthday": "1990-01-01"//出生日期
      }
    ],
    "trainTicketList": [
      {
        "resourceId": 353895332,//资源id
        "resourceStatus": 0,
        "trainId": 20463,//车次id
        "trainNum": "K463",//车次号
        "trainType": 5,//车次类型;0:高铁,1:城际,2:动车,3:直达,4:特快,5:普快,6:其他
        "trainTypeName": "普快",//车次类型名称;0:高铁,1:城际,2:动车,3:直达,4:特快,5:普快,6:其他
        "departCityId": 1602,//出发城市id
        "destCityId": 2500,//到达城市id
        "departCityName": "南京",//出发城市名称
        "destCityName": "上海",//到达城市名称
        "departStationId": 1175374,//出发站id
        "destStationId": 1175075,//到达站id
        "departStationName": "南京站",//出发站名称
        "destStationName": "上海站",//到达站名称
        "departArriveTime": null,
        "departDepartTime": "08:42",//出发时间
        "destArriveTime": "13:47",//到达时间
        "destDepartTime": null,
        "duration": 305,//历时(分钟)
        "durationDay": 1,//历时(天),1表示当天,2表示第二天,以此类推
        "departStationType": 2,//过路类型：0:始发；1:终点；2:过路
        "destStationType": 1,//过路类型：0:始发；1:终点；2:过路
        "seatType": 8,//坐等类型;0:商务座;1:特等座;2:一等座;3:二等座;4:高级软卧;5:软卧;6:硬卧;7:软座;8:硬座;9:无座
        "externalOrderId": "",
        "apiOrderId": "0",//api订单号
        "vendorId": 0,//供应商id
        "departsDate": "2026-03-25",//出发日期
        "seatTypeName": "硬座",//坐等类型名称
        "trainStopFlag": "0",//列车停运标识;0:非停运标识;1:停运标识
        "detailInfos": [
          {
            "resBookId": 39889485,//票id
            "touristId": 68472893,//乘客id
            "touristName": "张宁",//乘客姓名
            "touristType": 0,
            "ticketCode": "",
            "price": 46.5,//票价
            "status": 0,//票状态;0:待购票;1:购票中;2:已购票;3:购票失败;4:退票中;5:已退票;6:已取纸质票;7:线下改签;8:取消中;9:已取消;10:退票失败;11:线下退票;12:改签中;13:改签已取消;14:改签失败;15:已改签;16:改签票;17:改签取消中;18:改签已占位;19:改签取消失败;20:改签确认中;99:其他
            "statusName": "",
            "resMainId": 532359500,
            "ticketUrgeRefundStatus": null
          }
        ]
      }
    ],
    "changeTrainTicketList": null,
    "insuranceList": [],
    "delivery": null,
    "refundList": [],
    "isDispatchTicket": 0,
    "dispatch": null,
    "deliveryInformation": null,
    "grab": null,
    "orderTypeName": [
      "13-到站提醒未开启",
      "18-线下电子票"
    ],
    "name12306": null,
    "occupyType": 0,
    "maintainStatus": 0,
    "acceptStandingTicket": false,
    "canUrgeRefund": 0,
    "urgeRefundStatus": null,
    "price": 0,
    "userId": 46024923,//会员id
    "userType": 0,
    "source": 3,
    "startCityCode": "1602",
    "bookCity": "0",
    "productId": "47664942",
    "sourceType": -1,
    "boughtPromotions": null,
    "canChanged": 0,
    "supportRefund": 0,
    "alternateTrainList": null,
    "failReasonCode": "",
    "insCashBackPrice": 0,
    "priceDetail": {
      "trainTicketPrice": 0,//车票金额
      "insurancePrice": 0,//报销金额
      "resVoucherPrice": 0,//红包券金额
      "voucherVipPrice": 0,//贵宾厅金额
      "grabRateVoucherPrice": 0,//抢票套餐金额
      "lossTotalPrice": 0,//核损金额
      "couponTravelTotalPrice": 0,//旅游券金额
      "trainReducePrice": 0,//火车票立减优惠金额
      "orderDiscountAmount": 0,//订单立减金额
      "insuranceCashbackPrice": 0,//火车票报销返现金额
      "promotionPrdTotalPrice": 0,//促销金额
      "bussinessCardPrice": 0,//商旅卡金额
      "dispatchDeliverPrice": 0,//配送费
      "dispatchPurchasePrice": 0,//配送出票手续费
      "refundInsTotalPrice": 0,//退票险金额
      "trainOrderFreePrice": 0,//一元免单
      "memberRightsPrice": 0,//会员权益价格
      "grabUpgradeVoucherPrice": 0,//加油包
      "niuPlusGrabVoucherPrice": 0,
      "niuPlusTicketDiscountPrice": 0,
      "paidAmount": 0,//已付款金额
      "refundPrice": 0,//已退款金额
      "servicePackagePrice": 0,//服务包价格
      "grabCashBackPrice": 0,
      "refundApplyAdjustPrice": 0
    },
    "withHoldType": 0,
    "payType": 0,
    "servicePackageInfo": {
      "packageOrderRelationId": 702379,
      "packageType": 29,//服务包类型
      "packageName": "15元便捷通道费",//服务包名称
      "salePrice": 15,//售卖单价
      "number": 1,//订购数量
      "status": 0//订购状态;0:未购买;1:已购买;2:已退订
    },
    "onlinePayFlag": 0,
    "payChannels": null,//套皮支付支持的支付渠道;支付宝:33000010;银联:00011000;微信:33000020
    "refundServiceFee": 0,//退票服务费
    "changeServiceFee": 0,//改签服务费
    "trainPersonalTailorVo": null,//定制信息
    "changeTicketFee": null,//12306收取的改签费
    "rewardInfo": null,//优惠返现信息
    "trainAccountAbnormal": 0,
    "waitListDescUrl": "https://m.tuniu.com/event/mobileCms/index/actId/zpo5kwg3",
    "waitListCanCancel": false,
    "showWaitListCreateOrder": false,
    "waitListTitle": null,
    "waitListSubTitle": null
  }
}
```

**触发词**：查询订单详情123456

```bash
# departureStationName、arrivalStationName、departureDate 从搜索结果或用户需求取，trainNum 从搜索结果取
curl -s -X POST "${TRAIN_MCP_URL:-https://openapi.tuniu.cn/mcp/train}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"queryTrainOrderDetail","arguments":{"orderId":"<订单号>"}}}'
```



### 5. 取消订单 (cancelOrder)
**入参**：`orderId`必填。

入参示例：
```markdown
{
    "orderId": <订单号>
}
```

**返回**：`successCode`（取消成功标识,true:取消成功;false:取消失败）、`errorMessage`（取消失败原因）。

出参示例：
```markdown
{
    "successCode": true,//true:取消成功;false:取消失败
    "errorMessage": null//取消失败返回失败原因
}
```

**触发词**：取消订单123456

```bash
# departureStationName、arrivalStationName、departureDate 从搜索结果或用户需求取，trainNum 从搜索结果取
curl -s -X POST "${TRAIN_MCP_URL:-https://openapi.tuniu.cn/mcp/train}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"cancelOrder","arguments":{"orderId":"<订单号>"}}}'
```





## 响应处理

### 成功响应

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [{"type": "text", "text": "..."}]
  },
  "id": 2
}
```

- **本项目中** 工具结果统一放在 **`result.content[0].text`** 中。`text` 为 **JSON 字符串**，需先 `JSON.parse(result.content[0].text)` 再使用。
- 解析后为业务对象，各工具结构不同：
  - **车次列表**（searchLowestPriceTrain）：`successCode`、`data`（车次列表，含 trainNum、departStationName、destStationName、price、seatAvailable 等）。
  - **车次详情**（queryTrainDetail）：`successCode`、`trainInfo`、`seatInfo`（含 resId、price等）。
  - **预定下单**（bookTrain）：`successCode`、`orderId`、`orderDetailUrl`。
- 错误时 `text` 解析后为 `{ "successCode": false, "errorMessage": "错误信息" }`，可从 `errorMessage` 字段取提示文案。

### 错误响应

本项目中错误分两类，需分别处理：

**1. 传输/会话层错误**（无 `result`，仅有顶层 `error`，通常伴随 HTTP 4xx/5xx）：

```json
{
  "jsonrpc": "2.0",
  "error": {"code": -32000, "message": "..."},
  "id": null
}
```
- **Method Not Allowed**：GET 等非 POST 请求
- **Internal server error**（code -32603）：服务内部异常

**2. 工具层错误**（HTTP 仍为 200，有 `result`）：与成功响应结构相同，但 `result.content[0].text` 解析后为 `{ "successCode": false, "errorMessage": "错误信息" }`。例如参数校验失败、舱位信息失效、下单失败等，从 `errorMessage` 字段取文案提示用户或重试。

## 输出格式建议

- **车次列表**：以表格或清单展示车次号、出发/到达站、时间、价格、坐等、剩余座位；可提示「可以说翻页/下一页」
- **车次详情**：分块展示坐等、价格；提示用户可预订
- **预订成功**：明确写出订单号、订单详情链接

## 使用示例

以下示例中，所有参数均从**用户表述或上一轮结果**中解析并填入，勿用固定值。

**用户**：查询2026年3月20日南京到上海的火车票

**AI 执行**：按用户意图填参：departureCityName=南京、arrivalCityName=上海、departureDate=2026-03-20，调用 searchLowestPriceTrain（请求头需带 apiKey、Content-Type、Accept）。解析 result.content[0].text，整理车次列表回复。

**用户**：还有吗？/ 下一页

**AI 执行**：用首次查询返回的快照id(queryId) + pageNum=2（或 3、4…）再次调用 searchLowestPriceTrain。

**用户**：查一下南京南到上海虹桥G203车次详情

**AI 执行**：从上一轮列表确认出发站南京南，到达站上海虹桥，出发日期2026-03-20，车次号G203，调用 queryTrainDetail；解析坐等后展示价格、余票信息，并提示可预订。

**用户**：预定二等座，乘客姓名途牛，乘客身份证号 310101199001011234，乘客手机号 13564789999，联系人手机号 13800138000

**AI 执行**：从最近一次 queryTrainDetail 结果取 resId、price、departsDate；按用户提供的乘客信息填 adultTourists（name=途牛、psptType=1、psptId=310101199001011234、tel=13564789999），contact（tel=13800138000）。成功后回复订单号、订单详情url，并提醒用户完成支付。

## 注意事项

1. **密钥安全**：不要在回复或日志中暴露 TUNIU_API_KEY
2. **PII 安全**：联系人手机号、乘客姓名、证件号等仅在预订时发送至 MCP 服务，勿在日志或回复中暴露
3. **认证**：若遇协议或认证错误，可重试或检查 TUNIU_API_KEY
4. **日期格式**：所有日期均为 yyyy-MM-dd
5. **下单前**：bookTrain 的 resId、price、departsDate 必须来自最近一次 queryTrainDetail 的返回
6. **翻页**：用户要「更多」「下一页」时用快照id(queryId) + pageNum（≥2）调用即可
7. **支付提醒**：下单成功后必须提示用户点击 orderDetailUrl 完成支付