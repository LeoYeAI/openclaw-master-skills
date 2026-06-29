---
name: uupt-delivery-skill
description: >-
  UU跑腿同城配送服务。支持订单询价、发单下单、查询订单、取消订单、骑手实时追踪。当用户表达任何与"送"、"取"、"寄"、"跑腿"、"发单"、"配送"相关的配送需求时使用此skill。
version: 1.3.0
metadata:
  openclaw:
    requires:
      env: []
      bins:
        - node
        - python3
    homepage: https://open.uupt.com
    install:
      - kind: node
        package: axios
        bins: []
      - kind: python
        package: requests
        bins: []
---

# UU跑腿同城配送服务 Skill

UU跑腿同城配送服务为用户提供便捷的同城即时配送能力，包括订单询价、发单、订单管理和跑男实时追踪等功能。

## 功能特性

- 📱 手机号一键注册（首次使用自动引导）
- 💰 订单询价（计算配送费用）
- 📦 创建配送订单
- 💳 微信扫码支付（余额不足时自动生成支付二维码）
- 📋 查询订单详情
- ❌ 取消订单
- 🏃 跑男实时位置追踪
- 💾 配置本地持久化存储

## 运行环境选择

本 skill 同时提供 **Node.js** 和 **Python** 两种版本，可根据你的环境选择：

| 环境 | 依赖安装 | 脚本位置 |
|------|---------|---------|
| Node.js | `npm install` | `scripts/*.js` 和 `index.js` |
| Python | `pip install -r requirements.txt` | `uupt_delivery.py` |

Agent 会自动检测可用环境并选择合适的版本执行。

## 首次使用

**无需手动配置任何凭证。** 首次使用时，执行任何功能脚本会自动检测是否需要注册：

- 如果输出中包含 `[REGISTRATION_REQUIRED]`，说明需要先完成手机号验证
- Agent 应自动进入**场景零（首次注册）**引导用户完成注册
- 注册完成后，openId 自动保存到本地配置文件，后续使用无需重复注册

高级用户也可手动设置环境变量 `UUPT_OPEN_ID` 跳过注册流程。

## 触发条件

用户表达了以下意图之一：
- 询问配送价格（如"从A地址送到B地址多少钱"、"帮我算下配送费"）
- 下单配送（如"帮我发个跑腿单"、"我要寄东西"、"同城配送"）
- 查询订单（如"查看订单状态"、"订单到哪了"）
- 取消订单（如"取消这个订单"、"不想发了"）
- 追踪跑男（如"骑手在哪"、"跑男到哪了"、"配送进度"）
- 包含"跑腿"、"配送"、"寄送"、"订单"、"骑手"、"跑男"等关键词

## 场景判断

收到用户请求后，先判断属于哪个场景：

- **场景零**：首次注册 — 任何功能执行时检测到 `[REGISTRATION_REQUIRED]`，自动引导手机号验证
- **场景一**：订单询价 - 用户想知道配送费用，需要提供起始地址和目的地址
- **场景二**：创建订单 - 用户确认发单，需要询价返回的 priceToken 和收件人电话
- **场景三**：查询订单详情 - 用户想查看订单状态，需要订单编号
- **场景四**：取消订单 - 用户要取消订单，需要订单编号
- **场景五**：跑男追踪 - 用户想查看跑男实时位置，需要订单编号

---

## 场景零：首次注册 / 获取授权

当执行任何功能脚本时，如果输出中包含 `[REGISTRATION_REQUIRED]`，说明用户尚未完成注册授权，需要通过手机号短信验证获取 openId。

### 触发条件

- 执行任何脚本时输出包含 `[REGISTRATION_REQUIRED]`
- 这是一个**自动触发**场景，不需要用户主动发起

### 执行步骤

**Step 1: 询问手机号**

向用户询问：「首次使用需要验证手机号，请输入您的手机号码」

**Step 2: 发送短信验证码**

**Node.js 版本：**
```bash
node scripts/register.js --mobile="用户手机号"
```

**Python 版本：**
```bash
python uupt_delivery.py register --mobile="用户手机号"
```

处理结果：
- 输出 `[SMS_SENT]` → 验证码发送成功，提示用户查看手机短信，进入 Step 3
- 输出 `[IMAGE_CAPTCHA_REQUIRED]` → 需要图片验证码，处理方式：
  - 输出中包含 `IMAGE_DATA=data:image/png;base64,...` 的 base64 图片数据
  - 将 base64 图片展示给用户（可使用 show_widget 工具展示 `<img src="IMAGE_DATA中的内容">`）
  - 请用户识别图片中的数字
  - 用户回复后，重新调用（带 `--imageCode` 参数）：
    ```bash
    node scripts/register.js --mobile="手机号" --imageCode="用户输入的数字"
    ```

**Step 3: 输入短信验证码**

提示用户：「验证码已发送，请输入您收到的短信验证码」

**Step 4: 完成授权**

**Node.js 版本：**
```bash
node scripts/register.js --mobile="手机号" --smsCode="用户输入的验证码"
```

**Python 版本：**
```bash
python uupt_delivery.py register --mobile="手机号" --sms-code="用户输入的验证码"
```

处理结果：
- 输出 `[REGISTRATION_SUCCESS]` → 注册成功，openId 已自动保存到配置文件
  - 告知用户注册成功
  - **立即继续执行用户最初要求的功能**（无需用户再次操作）
- 输出 `[REGISTRATION_FAILED]` → 注册失败
  - **不需要重新询问手机号**
  - 从 Step 2 开始重试（重新发送验证码 → 用户输入新验证码 → 重新授权）
  - 最多重试 3 次
  - 3 次仍失败 → 告知用户稍后再试或联系客服

### 回复模板（注册成功后）

```
注册成功！您的账号已激活。
现在为您继续执行之前的操作...
```

---

## 场景一：订单询价

计算从起始地址到目的地址的配送费用。用户可以只询价不发单。

### 执行步骤

1. **执行询价脚本**：从用户输入中提取起始地址、目的地址、城市（可选）
2. **如果输出 `[REGISTRATION_REQUIRED]`**：进入场景零完成注册后，重新执行询价

### 使用方法

**Node.js 版本：**
```bash
node scripts/order-price.js --fromAddress="郑州市金水区农业路经三路交叉口" --toAddress="郑州市二七区德化街100号" --cityName="郑州市"
```

**Python 版本：**
```bash
python uupt_delivery.py price --from-address="郑州市金水区农业路经三路交叉口" --to-address="郑州市二七区德化街100号" --city="郑州市"
```

### 参数说明

| 参数 (JS) | 参数 (Python) | 说明 | 必填 |
|-----------|--------------|------|------|
| `--fromAddress` | `--from-address` | 起始地址（完整地址） | 是 |
| `--toAddress` | `--to-address` | 目的地址（完整地址） | 是 |
| `--cityName` | `--city` | 城市名称（需要带"市"字） | 否 |

### 返回结果

返回包含 `priceToken` 和价格信息，价格单位为分，需要格式化为元展示给用户。

### 回复模板

```
💰 配送费用查询结果：

起点：{fromAddress}
终点：{toAddress}
预估费用：{price/100} 元

📝 如需下单，请提供收件人电话。
```

---

## 场景二：创建订单（发单）

当用户明确表示要发单/下单时，**询价后直接创建订单**，无需二次确认。

### 触发条件

用户表达了发单意图，如：
- "帮我发个单"、"我要寄东西"、"帮我下单"
- "从A送到B，收件人电话xxx"
- "帮我配送xxx到xxx"

### 执行步骤

1. **获取必要信息**：起始地址、目的地址、收件人电话（必须在发单前获取）
2. **调用询价接口**：获取 priceToken
3. **立即创建订单**：使用 priceToken 直接创建订单，**不询问用户是否确认**
4. **处理返回结果**：根据余额情况进行不同处理

### 使用方法

**Step 1: 先询价获取 priceToken**

**Node.js 版本：**
```bash
node scripts/order-price.js --fromAddress="起始地址" --toAddress="目的地址"
```

**Python 版本：**
```bash
python uupt_delivery.py price --from-address="起始地址" --to-address="目的地址"
```

**Step 2: 立即创建订单**

**Node.js 版本：**
```bash
node scripts/create-order.js --priceToken="xxx" --receiverPhone="13800138000"
```

**Python 版本：**
```bash
python uupt_delivery.py create --price-token="xxx" --receiver-phone="13800138000"
```

### 参数说明

| 参数 (JS) | 参数 (Python) | 说明 | 必填 |
|-----------|--------------|------|------|
| `--priceToken` | `--price-token` | 询价接口返回的 token | 是 |
| `--receiverPhone` | `--receiver-phone` | 收件人手机号 | 是 |

### 返回结果处理

**情况一：余额充足，订单创建成功**

直接返回订单编号，告知用户订单已创建成功。

**回复模板：**
```
订单创建成功！

订单编号：{order_code}
配送费用：{price/100} 元

骑手正在接单中，请保持电话畅通。
```

---

**情况二：余额不足，需要微信支付**

当返回的 JSON 中 `data.orderUrl` 不为空且以 `weixin://` 开头时，表示需要微信扫码支付。

**识别标记**：脚本输出包含 `[PAYMENT_REQUIRED]` 和 `[WECHAT_PAY_QRCODE]` 时表示需要微信支付。

**关键输出**：
- `QRCODE_FILE=/tmp/wechat_pay_xxx.png` — 本地二维码图片文件路径
- `QRCODE_URL=https://api.qrserver.com/v1/create-qr-code/?...` — 在线二维码链接（兆底方案）

**处理流程：**

1. **展示支付二维码给用户**：

从脚本输出中提取：
- `QRCODE_FILE=` 后的本地文件路径
- `QRCODE_URL=` 后的在线链接

**回复模板（同时提供两种方式）**：

```
账户余额不足，需要完成微信支付

订单编号：{order_code}
配送费用：XX.XX 元

请使用微信扫描二维码完成支付：

[微信支付二维码]({QRCODE_FILE})

📱 如果二维码未显示，请在手机上点击此链接查看：
{QRCODE_URL}

支付完成后请回来告诉我。
```

**重要说明**：
- 使用 Markdown 图片语法引用本地文件：`[微信支付二维码]({QRCODE_FILE})`
- **必须同时提供在线链接作为兆底方案**，用户可在手机上点击链接查看二维码图片
- `{QRCODE_URL}` 格式如：`https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=weixin://wxpay/bizpayurl?pr=xxx`

2. **等待用户返回**：用户支付后会回来

3. **确认支付状态**：当用户回来时，询问用户是否已完成支付：
```
您好，请问是否已完成支付？
- 是，已支付完成
- 否，还未支付
```

4. **用户确认支付完成后**：立即调用订单详情接口查询订单状态

**Node.js 版本：**
```bash
node scripts/order-detail.js --orderCode="{order_code}"
```

**Python 版本：**
```bash
python uupt_delivery.py detail --order-code="{order_code}"
```

5. **展示订单详情**：

```
支付成功！订单详情如下：

订单编号：{order_code}
订单状态：{status}
起点：{from_address}
终点：{to_address}
配送费：{price/100} 元

骑手正在接单中，请保持电话畅通。
```

### 完整交互流程示例

```
用户：帮我从金水区农业路送到二七区德化街，收件人电话 13800138000

Agent：
1. 执行询价 → 获取 priceToken
2. 立即执行创建订单（不询问确认）
3. 如果余额充足 → 返回成功信息
4. 如果余额不足 → 输出支付链接

--- 用户去支付 ---

用户：我支付完了

Agent：
1. 询问确认：请问是否已完成支付？
2. 用户确认后 → 查询订单详情
3. 展示订单状态
```

---

## 场景三：查询订单详情

查看订单的当前状态和详细信息。

### 执行步骤

1. **获取订单编号**：从用户输入或上下文中获取订单编号
2. **调用查询接口**

### 使用方法

**Node.js 版本：**
```bash
node scripts/order-detail.js --orderCode="UU123456789"
```

**Python 版本：**
```bash
python uupt_delivery.py detail --order-code="UU123456789"
```

### 参数说明

| 参数 (JS) | 参数 (Python) | 说明 | 必填 |
|-----------|--------------|------|------|
| `--orderCode` | `--order-code` | 订单编号 | 是 |

### 回复模板

```
📋 订单详情：

订单编号：{order_code}
订单状态：{status}
起点：{from_address}
终点：{to_address}
配送费：{price/100} 元
骑手信息：{driver_name} {driver_phone}
```

---

## 场景四：取消订单

取消未完成的配送订单。

### 执行步骤

1. **获取订单编号**：从用户输入获取
2. **确认取消原因**：询问用户取消原因（可选）
3. **调用取消接口**

### 使用方法

**Node.js 版本：**
```bash
node scripts/cancel-order.js --orderCode="UU123456789" --reason="用户改变主意"
```

**Python 版本：**
```bash
python uupt_delivery.py cancel --order-code="UU123456789" --reason="用户改变主意"
```

### 参数说明

| 参数 (JS) | 参数 (Python) | 说明 | 必填 |
|-----------|--------------|------|------|
| `--orderCode` | `--order-code` | 订单编号 | 是 |
| `--reason` | `--reason` | 取消原因 | 否 |

### 回复模板

```
订单已取消

订单编号：{order_code}
取消原因：{reason}

如需重新下单，请告诉我配送地址。
```

---

## 场景五：跑男实时追踪

查询配送骑手的实时位置和状态。

### 执行步骤

1. **获取订单编号**：从用户输入获取
2. **调用跑男追踪接口**

### 使用方法

**Node.js 版本：**
```bash
node scripts/driver-track.js --orderCode="UU123456789"
```

**Python 版本：**
```bash
python uupt_delivery.py track --order-code="UU123456789"
```

### 参数说明

| 参数 (JS) | 参数 (Python) | 说明 | 必填 |
|-----------|--------------|------|------|
| `--orderCode` | `--order-code` | 订单编号 | 是 |

### 回复模板

```
跑男实时位置：

骑手姓名：{driver_name}
联系电话：{driver_phone}
当前位置：{current_location}
预计送达：{estimated_time}
```

---

## 配置管理

配置分为两层：

- **`defaults.json`**：内置应用凭证（appId、appSecret、apiUrl），随 Skill 分发，**请勿修改**
- **`config.json`**：用户级配置（openId），通过注册流程自动生成

设置认证信息的方式（优先级从高到低）：

1. **环境变量**：
   ```bash
   export UUPT_OPEN_ID=your_open_id        # 最常用，跳过注册流程
   export UUPT_API_URL=https://api-open.uupt.com/openapi/v3/  # 可选
   ```
2. **配置文件**：`config.json`（注册成功后自动生成）
3. **预制默认**：`defaults.json`（内置 appId 和 appSecret）

### 可选 API 环境

| 环境 | URL |
|------|-----|
| 生产环境 | `https://api-open.uupt.com/openapi/v3/` |
| 测试环境 | `http://api-open.test.uupt.com/openapi/v3/` |

---

## 在代码中使用

### Node.js

```javascript
const { orderPrice, createOrder, orderDetail, cancelOrder, driverTrack } = require('./index');

// 订单询价
const priceResult = await orderPrice({
  fromAddress: '郑州市金水区农业路经三路交叉口',
  toAddress: '郑州市二七区德化街100号',
  cityName: '郑州市'
});

// 创建订单
const orderResult = await createOrder({
  priceToken: priceResult.data.priceToken,
  receiverPhone: '13800138000'
});

// 检查是否需要支付
if (orderResult.data.orderUrl) {
  console.log('需要支付，打开链接:', orderResult.data.orderUrl);
}

// 查询订单
const detailResult = await orderDetail({
  orderCode: orderResult.data.order_code
});
```

### Python

```python
from uupt_delivery import order_price, create_order, order_detail, cancel_order, driver_track

# 订单询价
price_result = order_price(
    from_address='郑州市金水区农业路经三路交叉口',
    to_address='郑州市二七区德化街100号',
    city_name='郑州市'
)

# 创建订单
order_result = create_order(
    price_token=price_result['data']['priceToken'],
    receiver_phone='13800138000'
)

# 检查是否需要支付
if order_result['data'].get('orderUrl'):
    print('需要支付，打开链接:', order_result['data']['orderUrl'])

# 查询订单
detail_result = order_detail(
    order_code=order_result['data']['order_code']
)
```

---

## 注意事项

- **首次使用**：首次使用时需要通过手机号验证获取授权，之后无需重复操作
- **图片验证码**：如果发送短信验证码时返回 `[IMAGE_CAPTCHA_REQUIRED]`，需要展示 base64 图片让用户识别数字后重试
- **注册重试**：授权失败时自动重试，最多 3 次（不用重新输入手机号）
- **询价有效期**：priceToken 有时效性，建议获取后尽快创建订单
- **地址完整性**：地址信息越完整，配送越准确
- **城市默认值**：如未指定城市，默认使用"郑州市"
- **价格单位**：API 返回的价格单位是分，展示时需除以 100 转换为元
- **订单状态**：创建订单后请关注订单状态变化
- **余额不足**：当返回 `[PAYMENT_REQUIRED]` 和 `[WECHAT_PAY_QRCODE]` 时，需展示微信支付二维码引导用户扫码支付
- **配置文件**：`defaults.json` 为内置凭证，请勿修改或删除

## 相关链接

- [UU跑腿开放平台](https://open.uupt.com)
- [API 文档](https://open.uupt.com/docs)
