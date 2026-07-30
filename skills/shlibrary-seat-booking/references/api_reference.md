# 上海图书馆座位预约 API 参考

## 基础信息

- **基础URL**: `https://yuyue.library.sh.cn`
- **楼层ID**: `4`（3楼）
- **认证方式**: 预约系统请求通常会携带 `accessToken`、`sign`、`timestamp`、`x-encode`、`clientId`、`source`，并带有对应的 `Referer` / `Origin`
- **当前脚本行为**: `x-encode` 由脚本在每次请求前动态生成；`accessToken`、`sign`、`timestamp` 来自 `queryAuthInfo`
- **关于 `clientId`**: 当前抓到的官网 Web 预约链路里，`clientId` 一直是 `1837178870`。它更像“官网 Web 客户端的应用 ID”，不是设备唯一标识；对同一套 Web 流程，通常跨设备也会保持一致，但未来如果馆方切换前端应用或渠道，这个值也可能变化

## CLI 到 API 的映射

当前命令行入口只有 4 个子命令：

- `availability`
- `list`
- `cancel`
- `book`

它们和底层 API 的对应关系如下。

### `availability --date ... [--area ...]`

用途：
- 查询某一天“全部时段都可用”的座位

调用链：
- 先调用“获取区域列表”，如果未指定 `--area` 就扫描全部区域
- 对每个区域调用“获取排号列表”
- 对每个排号、每个时段调用“获取可用座位”
- 最后在脚本内做交集计算，筛出“当天所有时段都可用”的座位

对应 API：
- `GET /eastLibReservation/area?floorId=4`
- `GET /eastLibReservation/seatReservation/querySeatRow?seatArea={areaId}`
- `GET /eastLibReservation/seatReservation/queryAllAvailableSeatNo?...`

说明：
- 这是只读查询，不会创建预约

### `list [--profile ...]`

用途：
- 查询当前账号已有预约

对应 API：
- `POST /eastLibReservation/reservation/myReservationList`

说明：
- 脚本会按日期分组打印预约记录
- 返回里会包含 `reservationId`，供 `cancel` 使用

### `cancel --reservation-id ...`

用途：
- 取消指定预约

对应 API：
- `GET /eastLibReservation/seatReservation/calcelReservation?reservationId={reservationId}`

说明：
- `reservationId` 通常先通过 `list` 查出来

### `book --date ...`

用途：
- 创建预约

`book` 会根据参数组合走不同分支：

- `book --date [日期]`
  - 整天自动分配
  - 对当天所有时段逐段调用“系统自动分配预约”

- `book --date [日期] --period [上午|下午|晚上]`
  - 单时段自动分配
  - 调用一次“系统自动分配预约”

- `book --date [日期] --area [区域] --seat-row [排号] --seat-no [座位号]`
  - 整天指定座位
  - 对当天所有时段逐段先查座位、再提交指定座位预约

- `book --date [日期] --period [上午|下午|晚上] --area [区域] --seat-row [排号] --seat-no [座位号]`
  - 单时段指定座位
  - 先查座位、再提交指定座位预约

对应 API：
- 查询目标座位是否可用：
  - `GET /eastLibReservation/seatReservation/queryAllAvailableSeatNo?...`
- 提交指定座位预约：
  - `POST /eastLibReservation/seatReservation/reservation`
  - `seatReservationType = 2`
- 提交系统自动分配预约：
  - `POST /eastLibReservation/seatReservation/reservation`
  - `seatReservationType = 1`

说明：
- 整天预约不是一个单独的后端 API，而是脚本按当天多个时段逐段调用预约接口
- 整天模式默认顺序是：`下午 -> 晚上 -> 上午`
- 逐段提交之间会有短延迟，降低“请勿重复提交”类频控问题

## API 列表

### 1. 获取时间段列表

获取指定日期可预约的时间段。

**请求:**
```http
GET /eastLibReservation/api/period?date={date}&reservationType=14&libraryId=1
```

**参数:**
- `date` (`string`): 日期，格式 `YYYY-MM-DD`
- `reservationType` (`int`): 预约类型，固定值 `14`
- `libraryId` (`int`): 图书馆 ID，固定值 `1`

**响应示例:**
```json
{
  "resultStatus": {
    "code": 0,
    "message": "操作成功。"
  },
  "resultValue": [
    {
      "beginTime": "09:15:00",
      "endTime": "12:45:00",
      "periodId": 35,
      "periodTime": "09:15-12:45",
      "state": 1,
      "quotaVo": {
        "remaining": 41
      }
    }
  ]
}
```

---

### 2. 获取区域列表

获取指定楼层的所有区域。

**请求:**
```http
GET /eastLibReservation/area?floorId=4
```

**响应示例:**
```json
{
  "resultStatus": {
    "code": 0,
    "message": "操作成功。"
  },
  "resultValue": [
    {
      "id": 2,
      "areaName": "东区"
    },
    {
      "id": 3,
      "areaName": "西区"
    },
    {
      "id": 4,
      "areaName": "北区"
    },
    {
      "id": 5,
      "areaName": "南区"
    }
  ]
}
```

**区域 ID 映射:**
- `2`: 东区
- `3`: 西区
- `4`: 北区
- `5`: 南区

---

### 3. 获取排号列表

获取指定区域的排号列表。

**请求:**
```http
GET /eastLibReservation/seatReservation/querySeatRow?seatArea={areaId}
```

**参数:**
- `seatArea` (`int`): 区域 ID

**响应示例:**
```json
{
  "resultStatus": {
    "code": 0,
    "message": "操作成功。"
  },
  "resultValue": [
    {"seatRow": "1排"},
    {"seatRow": "2排"},
    ...
    {"seatRow": "25排"}
  ]
}
```

---

### 4. 获取可用座位

获取指定排号在指定时间段内的可用座位。

**请求:**
```http
GET /eastLibReservation/seatReservation/queryAllAvailableSeatNo?seatArea={areaId}&seatRow={row}&reservationStartTime={start}&reservationEndTime={end}
```

**参数:**
- `seatArea` (`int`): 区域 ID
- `seatRow` (`string`): 排号，需 URL 编码，例如 `4%E6%8E%92`（`4排`）
- `reservationStartTime` (`string`): 开始时间，格式 `YYYY-MM-DD HH:mm:ss`
- `reservationEndTime` (`string`): 结束时间，格式 `YYYY-MM-DD HH:mm:ss`

**响应示例:**
```json
{
  "resultStatus": {
    "code": 0,
    "message": "操作成功。"
  },
  "resultValue": [
    {
      "seatNo": "2号",
      "seatId": 374
    },
    {
      "seatNo": "5号",
      "seatId": 377
    }
  ]
}
```

---

### 5. 提交座位预约

提交座位预约请求。

**请求:**
```http
POST /eastLibReservation/seatReservation/reservation
Content-Type: application/json
```

**请求体:**
```json
{
  "areaId": 5,
  "floorId": "4",
  "reservationStartDate": "2026-03-22 09:15:00",
  "reservationEndDate": "2026-03-22 12:45:00",
  "seatId": 374,
  "seatReservationType": 2,
  "seatRowColumn": "4排2号"
}
```

**参数说明:**
- `areaId` (`int`): 区域 ID
- `floorId` (`string`): 楼层 ID，固定值 `"4"`
- `reservationStartDate` (`string`): 预约开始时间
- `reservationEndDate` (`string`): 预约结束时间
- `seatId` (`int`): 座位 ID
- `seatReservationType` (`int`): 预约类型，固定值 `2`
- `seatRowColumn` (`string`): 座位描述，例如 `"4排2号"`

**响应示例:**
```json
{
  "resultStatus": {
    "code": 0,
    "message": "预约成功"
  },
  "resultValue": {
    "currReservationStatus": "已预约",
    "reservationUser": "***",
    "reservationMobile": "138****5437",
    "reservationDate": "2026-03-22 09:15-12:45",
    "reservationSeat": "3楼 南区 4排 2号",
    "reservationId": 5186281
  }
}
```

---

### 6. 系统自动分配座位

不指定具体座位，由系统在可用座位中自动分配。

**请求:**
```http
POST /eastLibReservation/seatReservation/reservation
Content-Type: application/json
```

**请求体:**
```json
{
  "areaId": null,
  "floorId": "4",
  "reservationStartDate": "2026-03-22 09:15:00",
  "reservationEndDate": "2026-03-22 12:45:00",
  "seatLabels": [],
  "seatReservationType": 1
}
```

**参数说明:**
- `areaId` (`null`): 不指定区域，由系统自动分配
- `floorId` (`string`): 楼层 ID，固定值 `"4"`
- `reservationStartDate` (`string`): 预约开始时间
- `reservationEndDate` (`string`): 预约结束时间
- `seatLabels` (`array`): 固定传空数组 `[]`
- `seatReservationType` (`int`): 自动分配模式固定值 `1`

**成功响应示例:**
```json
{
  "resultStatus": {
    "code": 0,
    "message": "预约成功"
  },
  "resultValue": {
    "currReservationStatus": "已预约",
    "reservationUser": "***",
    "reservationMobile": "138****5437",
    "reservationDate": "2026-03-22 09:15-12:45",
    "reservationSeat": "3楼 南区 4排 5号",
    "reservationId": 5187294
  }
}
```

**失败响应示例:**
```json
{
  "resultStatus": {
    "code": -1,
    "message": "您好，用户***在该时间段有其他预约,本次预约失败"
  },
  "resultValue": null
}
```

这个错误表示当前账号在同一时间段已经有其他预约，系统拒绝重复预约。

---

### 7. 查询我的预约

查询当前账号已有的预约记录。

**请求:**
```http
POST /eastLibReservation/reservation/myReservationList
Content-Type: application/json
```

**请求体:**
```json
{
  "status": 0,
  "size": 100000,
  "page": 1
}
```

**参数说明:**
- `status` (`int`): 查询状态，当前使用 `0`
- `size` (`int`): 每页返回条数，当前脚本使用 `100000`
- `page` (`int`): 页码，当前脚本使用 `1`

**成功响应示例:**
```json
{
  "resultStatus": {
    "code": 0,
    "message": "操作成功。"
  },
  "resultValue": {
    "totalPages": 1,
    "content": [
      {
        "reservationDate": "2026-03-22",
        "reservationList": [
          {
            "reservationId": 5187335,
            "reservationStatusName": "已预约",
            "startTime": "09:15",
            "endTime": "12:45",
            "seatNo": "3楼南区10排7号",
            "areaId": 5,
            "flgCancel": 1
          }
        ]
      }
    ],
    "totalElements": 1
  }
}
```

常用字段说明：

- `reservationId`: 预约 ID
- `reservationStatusName`: 当前状态，例如 `已预约`、`已签到`
- `startTime` / `endTime`: 预约时间段
- `seatNo`: 座位展示名称
- `areaId`: 区域 ID
- `flgCancel`: 是否允许取消，`1` 表示可取消

---

### 8. 取消预约

按预约 ID 取消一条已有预约。

**请求:**
```http
GET /eastLibReservation/seatReservation/calcelReservation?reservationId={reservationId}
```

**参数说明:**
- `reservationId` (`int|string`): 要取消的预约 ID

**成功响应示例:**
```json
{
  "resultStatus": {
    "code": 0,
    "message": "取消预约成功"
  },
  "resultValue": null
}
```

调用前建议先用“查询我的预约”接口确认：

- 该预约 ID 是否存在
- `flgCancel` 是否为 `1`

---

## 认证信息

所有API请求都需要在Header中携带以下认证参数：

- `accessToken`: 访问令牌
- `clientId`: 当前官网 Web 预约链路观察到的客户端应用 ID，当前值为 `1837178870`；它不是设备 ID，也不保证永远不变
- `sign`: 签名
- `timestamp`: 时间戳
- `x-encode`: 动态请求头。前端会在每次请求前用随机串做 Base64 后再用固定 RSA 公钥加密生成

### 获取认证信息

当前更推荐通过门户登录后调用 `queryAuthInfo` 获取认证信息，而不是手动长期维护请求头。

浏览器手动排查时，可参考这条路径：

1. 先通过门户进入预约系统（通常会经过 `service/seatyy` 或 `service/yuyue`）
2. 使用读者证登录
3. 打开浏览器开发者工具（F12）
4. 进入任意可触发预约系统请求的页面
5. 查看预约 API 请求的 Request Headers
6. 复制 `accessToken`、`sign`、`timestamp`
7. `x-encode` 不需要手动保存，脚本会在每次请求前动态生成

### 保存认证信息

将认证信息保存到默认 profile 文件 `~/.config/shlibrary-seat-booking/profiles/default.json`：

```json
{
  "accessToken": "你的accessToken",
  "sign": "你的sign",
  "timestamp": "你的timestamp"
}
```

**注意**:

- 认证信息会失效，但接口没有提供稳定可读的明确过期时间
- 是否失效应以接口探测结果为准，不建议只靠本地 `timestamp` 人工判断
- 如果接口返回 `code 101 / 获取用户信息时出现异常`，当前脚本也会按失效登录态处理
- 当前默认文件路径是 `~/.config/shlibrary-seat-booking/profiles/default.json`
- 不要把真实凭证提交到仓库或分享给他人

---

## 错误码

- `0`: 成功
- `101`: 获取用户信息时出现异常。当前脚本按失效登录态处理
- `14001`: 参数错误
- 其他：详见响应中的 `message` 字段

---

## 使用示例

### 查询某天全部时段都可用的座位

```bash
node scripts/book_seat.js availability --date 2026-03-22 --area 南区
```

### 查询当前账号预约

```bash
node scripts/book_seat.js list --profile user1
```

### 取消一条预约

```bash
node scripts/book_seat.js cancel --profile user1 --reservation-id 5187335
```

### 单时段预约指定座位

```bash
node scripts/book_seat.js book --profile user1 --date 2026-03-22 --period 上午 --area 南区 --seat-row 4 --seat-no 2
```

### 整天自动分配

```bash
node scripts/book_seat.js book --profile user1 --date 2026-03-22
```
