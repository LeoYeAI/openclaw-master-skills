# 简化接口定义示例

## 示例1：用户注册接口

```
接口名称: 用户注册
接口路径: POST /api/users/register
请求参数:
  - username: string, 必填, 3-20字符, 字母数字下划线
  - password: string, 必填, 6-20字符, 必须包含字母和数字
  - email: string, 必填, 邮箱格式
  - phone: string, 可选, 11位手机号
  - invite_code: string, 可选, 6位邀请码
返回字段:
  - id: integer
  - username: string
  - email: string
  - token: string
  - created_at: datetime
业务规则:
  - 用户名不能重复
  - 邮箱不能重复
  - 手机号不能重复（如提供）
  - 邀请码必须有效（存在于系统中）
```

## 示例2：用户登录接口

```
接口名称: 用户登录
接口路径: POST /api/users/login
请求参数:
  - account: string, 必填, 用户名、邮箱或手机号
  - password: string, 必填, 密码
  - remember_me: boolean, 可选, 记住登录状态
返回字段:
  - user: object
    - id: integer
    - username: string
    - email: string
    - phone: string
  - token: string
  - expires_in: integer
业务规则:
  - 密码错误5次锁定账号30分钟
  - token有效期24小时（remember_me=false）或7天（remember_me=true）
```

## 示例3：查询用户列表

```
接口名称: 查询用户列表
接口路径: GET /api/users
请求参数:
  - page: integer, 可选, 页码, 默认1, 最小1
  - page_size: integer, 可选, 每页数量, 默认20, 最小1, 最大100
  - status: enum, 可选, [active, inactive, suspended]
  - keyword: string, 可选, 搜索关键词, 最大50字符
  - sort_by: enum, 可选, [id, username, created_at], 默认id
  - sort_order: enum, 可选, [asc, desc], 默认desc
返回字段:
  - total: integer
  - page: integer
  - page_size: integer
  - list: array
    - id: integer
    - username: string
    - email: string
    - status: string
    - created_at: datetime
业务规则:
  - 只能查看有权限的用户数据
  - 支持模糊搜索用户名和邮箱
  - 按指定字段排序
```

## 示例4：创建订单接口

```
接口名称: 创建订单
接口路径: POST /api/orders
请求参数:
  - user_id: integer, 必填, 用户ID
  - product_ids: array, 必填, 商品ID列表
  - address_id: integer, 必填, 地址ID
  - coupon_code: string, 可选, 优惠券代码
  - remark: string, 可选, 备注, 最大200字符
返回字段:
  - order_id: string
  - order_number: string
  - total_amount: number
  - status: string
  - created_at: datetime
业务规则:
  - 用户必须存在且状态正常
  - 商品必须存在且有库存
  - 地址必须存在且属于该用户
  - 优惠券必须有效且未过期
  - 订单金额必须大于0
  - 单个用户同一时间最多5个未支付订单
```

## 示例5：文件上传接口

```
接口名称: 上传头像
接口路径: POST /api/users/avatar
请求参数:
  - user_id: integer, 必填, 用户ID
  - file: file, 必填, 图片文件
  - file_type: enum, 必填, [jpg, png, gif]
返回字段:
  - url: string
  - filename: string
  - size: integer
  - upload_time: datetime
业务规则:
  - 只能上传自己的头像
  - 文件大小不能超过2MB
  - 支持JPG、PNG、GIF格式
  - 上传后自动删除旧头像
```

## 格式说明

### 接口基本信息

```
接口名称: [接口的中文名称]
接口路径: [HTTP方法] [URL路径]
```

### 请求参数

```
请求参数:
  - [参数名]: [类型], [必填/可选], [约束条件], [描述]
```

**类型支持**：string, integer, number, boolean, array, object, file, enum

**约束条件**：
- 字符串：长度范围（如3-20字符）、正则表达式（如字母数字下划线）、格式（如邮箱）
- 数字：取值范围（如0-150）、精度
- 数组：元素类型、元素数量
- 对象：嵌套字段定义（缩进表示层级）
- 枚举：有效值列表（如[active, inactive, suspended]）

### 返回字段

```
返回字段:
  - [字段名]: [类型]
  - [字段名]: [类型]
    - [子字段]: [类型]  # 对象类型
  - [字段名]: array
    - [元素字段]: [类型]  # 数组元素类型
```

### 业务规则

```
业务规则:
  - [规则描述]
  - [规则描述]
```

常见的业务规则：
- 唯一性：用户名不能重复
- 存在性：用户必须存在
- 状态：只有审核通过的才能操作
- 权限：只能操作自己的数据
- 数量：最多创建10个
- 关联：订单必须关联有效的用户

## 使用脚本生成

```bash
# 从简化定义生成
python scripts/generate-checklist.py \
  --input examples/simple-example.md \
  --format simple \
  --output output/checklist.md

# 从字符串生成
python scripts/generate-checklist.py \
  --input "接口名称: 测试接口
接口路径: POST /api/test
请求参数:
  - name: string, 必填
返回字段:
  - id: integer" \
  --format simple
```
