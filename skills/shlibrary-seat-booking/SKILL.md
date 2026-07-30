---
name: shlibrary-seat-booking
description: 上海图书馆东馆三楼座位预约。支持浏览器自动化登录获取认证信息，以及基于API的座位预约（指定座位或系统自动分配）。适用于需要自动化预约图书馆座位的场景。
homepage: https://github.com/jenslewie/jenslewie-skills/tree/main/shlibrary-seat-booking
metadata:
  openclaw:
    emoji: "📚"
    homepage: https://github.com/jenslewie/jenslewie-skills/tree/main/shlibrary-seat-booking
    requires:
      bins:
        - node
        - npm
        - npx
    install:
      - kind: brew
        formula: node
        bins: [node, npm, npx]
        label: Install Node.js
      - kind: node
        package: playwright
        bins: [playwright]
        label: Install Playwright
---

# 上海图书馆座位预约

通过上海图书馆预约接口，预约东馆三楼阅览座位。

## 功能特性

- **浏览器辅助登录** - 手动完成登录后，自动获取认证信息
- **读取本地认证信息** - 从 profile 文件读取认证信息
- **登录态自动刷新** - profile 文件来源的认证缺失或失效时，会自动拉起登录流程
- **支持时段标签** - "上午 / 下午 / 晚上"映射到具体时间
- **支持中文参数值** - 支持 `--area 南区 --seat-row 4排 --seat-no 2号` 这样的直观输入
- **整天预约模式** - 一键预约当天所有时段
- **检查指定座位可用性** - 指定座位预约前自动检查目标座位
- **提交指定座位预约** - 预约特定座位
- **系统自动分配预约** - 让系统分配可用座位
- **查询整天公共可用座位** - 查询某一天全部时段都可用的座位列表
- **查询当前账号已有预约** - 查看预约记录
- **取消指定预约** - 取消已有预约
- **多账号支持** - 通过 `--profile` 切换不同账号

## 前置条件

1. **拥有上海图书馆读者证**（已开通借阅功能）
2. **已安装依赖**（如果使用浏览器登录功能）
3. 如果使用预约模式，需要知道 **日期和时段**
4. 如果使用指定座位模式，还需要知道 **区域、排号和座位号**
5. 如果要切换到另一个账号，可以额外准备一个 `profile` 对应的认证文件
6. 不要求事先手动登录或手动保存认证文件；当使用 profile 文件时，`book_seat.js` 会在认证缺失或失效时自动拉起登录流程

## 适用方式

当前推荐统一使用子命令入口：

- `availability`：查询某天全部时段都可用的座位
- `list`：查询当前账号已有预约
- `cancel`：取消指定预约
- `book`：预约座位

当前脚本支持两类预约：

- 指定座位模式：先查这个座位是否可用，再决定是否提交预约
- 自动分配模式：不指定区域/排号/座位号，直接请求系统分配一个可用座位

参数约定：

- `availability --date [日期] [--area 区域...]`
  - `--date`：必填，表示查询哪一天
  - `--area`：可选，表示只扫描哪些区域；不传就查询全部区域
- `list [--profile 名称]`
  - 不接受其他业务参数
- `cancel --reservation-id [预约ID]`
  - `--reservation-id`：必填，只负责指定要取消哪条预约
- `book --date [日期] [--period 时段] [--area 区域] [--seat-row 排号] [--seat-no 座位号]`
  - 只有 `--date`：整天自动分配
  - `--date + --period`：单时段自动分配
  - `--date + --area + --seat-row + --seat-no`：整天指定座位
  - `--date + --period + --area + --seat-row + --seat-no`：单时段指定座位
  - 参数值支持中文格式，例如：`--area 南区 --seat-row 4排 --seat-no 2号`

## 常用命令速查

```bash
# 查询当前账号预约
node ./scripts/book_seat.js list

# 查询指定账号预约
node ./scripts/book_seat.js list --profile user1

# 查询 3 月 20 日在多个区域里整天都可用的座位
node ./scripts/book_seat.js availability --profile user1 --date 2026-03-20 --area 北区 西区 东区

# 查询 3 月 20 日全部区域里整天都可用的座位
node ./scripts/book_seat.js availability --profile user1 --date 2026-03-20

# 取消预约
node ./scripts/book_seat.js cancel --profile user1 --reservation-id 5187335

# 按时段自动分配
node ./scripts/book_seat.js book --profile user1 --date 2026-03-24 --period 上午

# 按时段指定座位
node ./scripts/book_seat.js book --profile user1 --date 2026-03-24 --period 下午 --area 南区 --seat-row 4 --seat-no 5

# 整天自动分配
node ./scripts/book_seat.js book --profile user1 --date 2026-03-24

# 整天指定座位
node ./scripts/book_seat.js book --profile user1 --date 2026-03-24 --area 南区 --seat-row 4 --seat-no 5
```

说明：

- 不传 `--profile` 就使用默认账号
- `--profile <name>` 会读取默认 profile 根目录下的 `profiles/<name>.json`
- 默认 profile 根目录是 `~/.config/shlibrary-seat-booking`
- 也可以通过 `--profile-dir` 或 `--auth-file` 显式指定认证文件位置
- 如果 profile 文件缺失或认证失效，脚本会自动拉起登录

## 快速开始

### 方式1: 浏览器自动化登录（推荐）

Skill 提供了基于 Node.js + Playwright 的浏览器自动化脚本，可以自动完成登录并获取认证信息：

#### 安装依赖

```bash
# 在 skill 目录内安装 Playwright
cd /path/to/shlibrary-seat-booking
npm install playwright

# 安装浏览器二进制
npx playwright install chromium
```

说明：

- 请在 skill 目录内执行 `npm install playwright`，这样 `node ./scripts/*.js` 才能稳定加载本地 `playwright` 依赖
- `npx playwright install chromium` 会联网下载 Chromium 浏览器二进制

#### 运行登录脚本

```bash
# 默认账号登录
node ./scripts/login.js

# 指定profile登录
node ./scripts/login.js --profile user1

# 指定 profile 根目录
node ./scripts/login.js --profile user1 --profile-dir ~/.config/shlibrary-seat-booking

# 直接指定认证文件
node ./scripts/login.js --auth-file ~/.config/shlibrary-seat-booking/profiles/user1.json
```

脚本会：
1. 打开浏览器并访问登录页面
2. 由你手动完成用户名、密码、验证码登录
3. 登录成功后自动检测并继续
4. 自动进入 `seatyy` / `service/yuyue`，优先直接调用 `queryAuthInfo`
5. 只有门户没有自动准备好时，才兜底尝试点击“预约”入口
6. 保存到对应的认证文件（默认 `~/.config/shlibrary-seat-booking/profiles/default.json`）

#### 技术实现

- **纯 Node.js 实现** - 使用 Playwright 打开浏览器
- **手动登录 + 自动提取** - 登录动作由你完成，认证提取由脚本完成
- **优先直连门户接口** - 先走 `seatyy -> service/yuyue -> queryAuthInfo`
- **调用 queryAuthInfo** - 自动获取 `accessToken`、`sign`、`timestamp`
- **多账号支持** - 通过 `--profile` 参数管理多个账号

### 方式2: 手动获取认证信息

如果你更喜欢手动操作，或者想排查认证问题：

1. 先通过门户进入预约系统（通常会经过 `service/seatyy` 或 `service/yuyue`）
2. 使用读者证登录
3. 按 F12 打开浏览器开发者工具
4. 切换到 Network（网络）标签
5. 进入任意可触发预约系统接口的页面
6. 查看任意预约 API 请求的 Request Headers
7. 复制以下三个参数：
   - `accessToken`
   - `sign`
   - `timestamp`
8. `x-encode` 不需要手动保存，脚本会在每次发请求前动态生成

### 2. 保存认证信息

如果使用浏览器自动化登录，认证信息会自动保存。

如果手动获取，将认证信息保存到文件：

```bash
mkdir -p ~/.config/shlibrary-seat-booking/profiles
cat > ~/.config/shlibrary-seat-booking/profiles/default.json << 'EOF'
{
  "accessToken": "你的accessToken",
  "sign": "你的sign",
  "timestamp": "你的timestamp"
}
EOF
chmod 600 ~/.config/shlibrary-seat-booking/profiles/default.json
```

**注意**:
- 认证信息会失效，但接口没有提供稳定可读的明确过期时间
- `book_seat.js` 会先探测登录态；如果认证来自 profile 文件且缺失或失效，会自动拉起 `login.js`
- 如果接口返回 `code 101 / 获取用户信息时出现异常`，脚本也会按失效登录态处理
- 是否“过期”以接口探测结果为准，不建议只靠本地时间戳人工判断
- 不要把真实凭证提交到仓库或发给别人

如果你需要管理多个账号，也可以按 profile 名称保存多个文件：

```bash
~/.config/shlibrary-seat-booking/profiles/default.json
~/.config/shlibrary-seat-booking/profiles/user1.json
~/.config/shlibrary-seat-booking/profiles/user2.json
```

认证读取优先级是：

- `--auth-file`：直接读取显式指定的单文件
- `--profile-dir + --profile`：读取 `<profile-dir>/profiles/<profile>.json`
- 默认 profile 根目录 + `--profile`：读取 `~/.config/shlibrary-seat-booking/profiles/<profile>.json`
- 什么都不传：读取 `~/.config/shlibrary-seat-booking/profiles/default.json`

认证写入规则是：

- 传了 `--auth-file`：登录成功后写回该文件
- 传了 `--profile-dir + --profile`：写 `<profile-dir>/profiles/<profile>.json`
- 只传 `--profile`：写 `~/.config/shlibrary-seat-booking/profiles/<profile>.json`
- 什么都不传：写 `~/.config/shlibrary-seat-booking/profiles/default.json`

补充说明：

- `book_seat.js` 会先探测登录态；如果 profile 文件缺失或登录态失效，会自动拉起 `login.js`

### 3. 预约座位

#### 预约座位

统一使用 `book` 子命令：

```bash
# 整天自动分配
node ./scripts/book_seat.js \
  book --date 2026-03-24

# 单时段自动分配
node ./scripts/book_seat.js \
  book --date 2026-03-24 --period 上午

# 整天指定座位
node ./scripts/book_seat.js \
  book --date 2026-03-24 --area 南区 --seat-row 4 --seat-no 5

# 单时段指定座位
node ./scripts/book_seat.js \
  book --date 2026-03-24 --period 下午 --area 南区 --seat-row 4 --seat-no 5
```

脚本执行流程：

1. 按优先级读取认证文件
2. 如果认证缺失或失效，自动拉起登录流程
3. 根据参数组合判断是自动分配还是指定座位、整天还是单时段
4. 如果是指定座位，先查询目标时段的可用座位
5. 如果座位可用，再提交预约
6. 输出预约成功或失败信息

#### 系统自动分配

如果你只关心时间段，不关心具体座位，可以让系统自动分配：

```bash
# 预约3月22日上午，由系统自动分配座位
node ./scripts/book_seat.js \
  book --date 2026-03-22 --period 上午
```

自动分配模式的流程：

1. 按优先级读取认证文件
2. 如果认证缺失或失效，自动拉起登录流程
3. 直接调用预约接口，请求系统分配可用座位
4. 输出预约成功或失败信息

也支持按时段标签自动分配：

```bash
node ./scripts/book_seat.js \
  book --date 2026-03-22 --period 上午
```

如果要替另一个账号查预约：

```bash
node ./scripts/book_seat.js \
  list --profile user1
```

### 4. 查询已有预约

如果你想先确认账号当前已经约了哪些时间段，可以直接查询：

```bash
node ./scripts/book_seat.js list
```

查询模式会：

1. 按优先级读取认证文件
2. 如果认证缺失或失效，自动拉起登录流程
3. 调用"我的预约"接口
4. 按日期分组打印当前账号的预约记录
5. 展示每条记录的时间段、座位、预约状态、预约 ID 和是否可取消

### 5. 查询整天公共可用座位

如果你想先筛出“某一天全部时段都可用”的位置，可以直接查询。这里日期是必填参数，区域通过 `--area` 可选传入：

```bash
node ./scripts/book_seat.js \
  availability --profile user1 --date 2026-03-20 --area 北区 西区 东区
```

如果你不指定区域，脚本会自动扫描全部区域：

```bash
node ./scripts/book_seat.js \
  availability --profile user1 --date 2026-03-20
```

这个模式会：

1. 读取对应 profile 的认证信息
2. 如果认证缺失或失效，自动拉起登录流程
3. 根据日期判断当天是 2 个时段还是 3 个时段
4. 扫描目标区域的所有排号和可用座位
5. 计算每个区域在当天全部时段的座位交集
6. 输出每个区域“所有时段都可用”的座位列表

说明：

- 可以通过 `--area` 传一个或多个区域，例如 `--area 北区 西区 东区`
- 也可以传区域 ID：`2 / 3 / 4 / 5`
- 如果不传区域，脚本会扫描全部区域
- 周一会按 2 个时段求交集，其他日期按 3 个时段求交集
- 这是只读查询，不会创建任何预约

### 6. 取消预约

如果你已经知道预约 ID，可以直接取消：

```bash
node ./scripts/book_seat.js cancel --reservation-id 5187335
```

取消模式会：

1. 按优先级读取认证文件
2. 如果认证缺失或失效，自动拉起登录流程
3. 调用取消预约接口
4. 输出成功或失败结果

更稳的使用顺序通常是：

1. 先执行 `list`
2. 找到目标记录的 `预约ID`
3. 再执行 `cancel --reservation-id [预约ID]`

## 时段映射规则

当前脚本按业务规则使用固定 mapping：

- 周一
  - `下午` -> `13:45:00-16:45:00`
  - `晚上` -> `17:00:00-20:30:00`
  - `上午` -> 不可用
- 周二到周日
  - `上午` -> `09:15:00-12:45:00`
  - `下午` -> `13:00:00-16:30:00`
  - `晚上` -> `16:45:00-20:15:00`

如果图书馆后续调整了开放时段，这部分规则也需要同步更新。

## 整天预约顺序

当使用整天预约模式时，脚本会按这个顺序逐段尝试：

1. `下午`
2. `晚上`
3. `上午`

这是一种 `best-effort` 策略：

- 某一段失败不会中断其他时段
- 最后会统一汇总成功和失败结果
- 每个时段提交后会等待约 `1` 秒，再继续下一段，尽量降低"请勿重复提交"这类频控问题

## 自动重试策略

当前脚本对部分临时性失败做了短重试：

- 当接口返回 `系统拥挤，请稍后再试` 时
- 预约和取消都会自动重试
- 默认最多重试 `3` 次
- 每次重试间隔约 `1.5` 秒

像这些明确的业务失败不会自动重试：

- `座位已约满`
- `该时间段有其他预约`
- `目标座位不可用`

## 区域 ID 对照

- `2`: 东区
- `3`: 西区
- `4`: 北区
- `5`: 南区

## 预约规则

- **放号时间**: 每日12:00开放从当天算起第7天的座位预约
- **签到时间**: 预约开始时间后15分钟内必须扫码签到
- **取消预约**: 可在"我的预约"中提前取消
- **违规处理**: 3次违规将暂停预约权限30天

## 参考资料

- **API文档**: 详见 [references/api_reference.md](references/api_reference.md)
- **预约规则**: https://yuyue.library.sh.cn/notice/seatAllNotice.html

## 故障排除

### 认证失败
- 检查认证信息是否过期
- 检查 `accessToken`、`sign`、`timestamp` 三个字段是否都存在
- 重新登录获取新的认证信息
- 如果返回 `code 101 / 获取用户信息时出现异常`，也按登录态失效处理

### 座位不可用
- 该座位可能已被他人预约
- 脚本会打印当前可用座位列表，可改约其他座位

### 系统自动分配失败
- 如果接口返回"该时间段有其他预约"，说明当前账号在同一时段已有预约，不能重复预约
- 如果接口返回无可用座位，需要更换时间段再试

### 查询已有预约失败
- 检查认证信息是否过期
- 如果接口返回登录页或非 JSON，通常是认证失效
- 如果接口返回 `code 101 / 获取用户信息时出现异常`，通常也需要重新登录
- 重新抓取 `accessToken`、`sign`、`timestamp` 后重试

### 取消预约失败
- 检查该 `预约ID` 是否存在
- 确认该记录当前 `可取消: 是`
- 如果接口提示状态不允许取消，说明该预约可能已签到、已过期或已取消

### 接口返回非 JSON 或 HTTP 错误
- 这通常表示认证失效、请求被拦截、或接口返回了登录页/错误页
- 先重新获取认证信息，再重试
- 必要时参考 [references/api_reference.md](references/api_reference.md) 核对请求参数

### API调用失败
- 检查网络连接
- 确认认证信息正确
- 查看脚本输出中的 HTTP 状态码、响应片段和错误信息
