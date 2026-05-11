---
name: xianyu-auto-fulfillment
description: >
  闲鱼自动发货框架 - 一个可扩展的闲鱼虚拟商品自动化发货系统。提供核心的付款检测逻辑，发货流程完全可自定义。
  - 核心功能：自动检测买家付款（系统卡片识别）
  - 可扩展：支持任意发货方式（秘钥、链接、图片、文件、自定义API等）
  - 灵活配置：通过脚本或配置文件自定义发货逻辑
  - 内置模板：提供多种常见发货场景的模板
  - 使用 agent-browser 进行网页自动化
metadata: {"clawdbot":{"emoji":"🐟","requires":["agent-browser"]}}
read_when:
  - Automating Xianyu (闲鱼) virtual goods delivery
  - Monitoring chat messages for payment confirmation
  - Customizable fulfillment workflow for various product types
---

# 🐟 闲鱼自动发货框架

一个可扩展的闲鱼虚拟商品自动化发货系统。核心提供付款检测，发货流程完全可自定义。

## 🎯 设计理念

```
┌─────────────────────────────────────────────────────────────┐
│                    核心检测层（框架提供）                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  监控聊天    │ -> │  检测付款    │ -> │  触发发货    │  │
│  │  - 新消息    │    │  - 系统卡片  │    │  - 调用钩子  │  │
│  │  - 未读标记  │    │  - 状态判断  │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  自定义发货层（用户实现）                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  秘钥发货    │  │  链接发货    │  │  图片发货    │  ...  │
│  │  - 固定秘钥  │  │  - 网盘链接  │  │  - 二维码    │       │
│  │  - 秘钥池    │  │  - 下载地址  │  │  - 截图      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  文件发货    │  │  API发货     │  │  自定义逻辑  │  ...  │
│  │  - 发送文件  │  │  - 调用接口  │  │  - 按需定制  │       │
│  │  - 上传网盘  │  │  - 返回数据  │  │              │       │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

**核心原则：**
- **关注点分离**：检测逻辑由框架提供，发货逻辑由用户自定义
- **可扩展性**：支持任意类型的发货方式
- **零侵入**：框架不强制特定的发货方式
- **开箱即用**：提供常用场景的完整模板

---

## 🏗️ 核心概念

### 1. 付款检测（框架核心）

自动检测闲鱼聊天中的系统付款卡片：

```
✅ 检测条件（AND 关系）：
  - 消息类型：系统卡片（不是用户文本）
  - 卡片内容："我已付款，等待你发货"
  - 按钮标识：有"去发货"按钮

❌ 排除情况：
  - 用户手打的："我已付款了"、"老板发货"等
  - 没有"去发货"按钮的消息
  - "待付款"状态的卡片
```

### 2. 发货钩子（用户实现）

当检测到付款后，框架调用用户定义的发货钩子：

```bash
# 钩子函数签名
fulfill_order() {
    # 输入：无（通过环境变量或全局变量获取上下文）
    # 输出：0（成功）或非0（失败）
    # 作用：自定义发货逻辑
}
```

### 3. 订单上下文

发货时可用的上下文信息：

| 变量 | 说明 | 示例 |
|-----|------|------|
| `$BUYER_NICKNAME` | 买家昵称 | "atting丶" |
| `$ORDER_AMOUNT` | 订单金额 | "9.90" |
| `$ORDER_TIME` | 下单时间 | "2026-02-28 15:30:00" |
| `$PRODUCT_TITLE` | 商品标题 | "VIP会员兑换码" |
| `$BUYER_AVATAR` | 买家头像URL | "https://..." |

---

## 📦 内置发货模板

框架提供了多种常见发货场景的完整模板，可直接使用或作为参考。

### 模板 1：秘钥发货（固定秘钥）

**适用场景：**
- 测试商品（所有人用同一个秘钥）
- 免费资源分享
- 公开教程

**使用方法：**

```bash
#!/bin/bash
# fulfillment-templates/01-fixed-key.sh

# 配置
SECRET_KEY="YOUR_SECRET_KEY_HERE"

# 发货钩子
fulfill_order() {
    echo "📦 发送固定秘钥..."

    # 发送秘钥到聊天
    agent-browser type "您的秘钥：$SECRET_KEY，祝您使用愉快！"
    sleep 1
    agent-browser click "发 送"

    return 0
}

# 导出钩子（由框架调用）
export -f fulfill_order
```

---

### 模板 2：秘钥发货（秘钥池）

**适用场景：**
- 每个订单使用不同秘钥
- 批量售卖虚拟商品
- 需要追踪每个秘钥使用情况

**使用方法：**

```bash
#!/bin/bash
# fulfillment-templates/02-key-pool.sh

# 配置
KEY_POOL_FILE="keys.txt"
USED_KEYS_FILE="used-keys.txt"

# 初始化秘钥池
init_key_pool() {
    if [ ! -f "$KEY_POOL_FILE" ]; then
        echo "# 秘钥池文件 - 每行一个秘钥" > "$KEY_POOL_FILE"
        echo "# 示例：" >> "$KEY_POOL_FILE"
        echo "KEY-ABC123" >> "$KEY_POOL_FILE"
        echo "KEY-DEF456" >> "$KEY_POOL_FILE"
        echo "KEY-GHI789" >> "$KEY_POOL_FILE"
    fi
}

# 从秘钥池获取一个秘钥
get_key_from_pool() {
    if [ ! -f "$KEY_POOL_FILE" ]; then
        echo "❌ 秘钥池文件不存在：$KEY_POOL_FILE"
        return 1
    fi

    # 读取第一个非注释行
    key=$(grep -v "^#" "$KEY_POOL_FILE" | grep -v "^$" | head -1)

    if [ -z "$key" ]; then
        echo "❌ 秘钥池已空！"
        return 1
    fi

    # 从秘钥池中移除已使用的
    sed -i '' "/^$key$/d" "$KEY_POOL_FILE" 2>/dev/null || \
    sed -i "/^$key$/d" "$KEY_POOL_FILE" 2>/dev/null

    # 记录到已使用秘钥
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $key" >> "$USED_KEYS_FILE"

    echo "$key"
}

# 发货钩子
fulfill_order() {
    echo "📦 从秘钥池获取秘钥..."

    # 初始化秘钥池
    init_key_pool

    # 获取秘钥
    key=$(get_key_from_pool)
    if [ $? -ne 0 ]; then
        echo "❌ 获取秘钥失败"
        return 1
    fi

    echo "✅ 获取到秘钥：$key"

    # 发送秘钥
    agent-browser type "您的秘钥：$key，祝您使用愉快！"
    sleep 1
    agent-browser click "发 送"

    return 0
}

export -f fulfill_order
```

---

### 模板 3：链接发货（网盘/下载链接）

**适用场景：**
- 数字资源下载（软件、电子书、课程）
- 大文件分享（视频、音频）
- 云盘分享

**使用方法：**

```bash
#!/bin/bash
# fulfillment-templates/03-link-delivery.sh

# 配置
DOWNLOAD_LINK="https://pan.baidu.com/s/XXXXXXXXXXXX"
EXTRACTION_CODE="abcd"

# 发货钩子
fulfill_order() {
    echo "📦 发送下载链接..."

    # 发送链接和提取码
    agent-browser type "您的下载链接已准备好！\n\n📁 网盘链接：$DOWNLOAD_LINK\n🔑 提取码：$EXTRACTION_CODE\n\n如有问题，随时联系我！"
    sleep 1
    agent-browser click "发 送"

    return 0
}

export -f fulfill_order
```

---

### 模板 4：图片发货（二维码/截图）

**适用场景：**
- 发送二维码（公众号、加好友、领取页面）
- 发送教程截图
- 发送凭证/卡密图片

**使用方法：**

```bash
#!/bin/bash
# fulfillment-templates/04-image-delivery.sh

# 配置
QR_CODE_IMAGE="$HOME/Desktop/qr-code.png"

# 发货钩子
fulfill_order() {
    echo "📦 发送二维码图片..."

    # 先发送文字说明
    agent-browser type "请扫描下方二维码添加好友/领取商品："
    sleep 1
    agent-browser click "发 送"

    # 等待一下再发送图片
    sleep 2

    # 上传并发送图片（需要根据闲鱼界面调整）
    agent-browser snapshot
    # 找到图片上传按钮并点击
    agent-browser find role button click --name "图片" || \
    agent-browser click "＋" || \
    agent-browser find aria-label "图片" click

    # 等待文件选择器
    sleep 1

    # 上传文件（方法1：使用 file 输入）
    # 注意：需要根据实际界面调整
    agent-browser find role textbox click --name "选择文件"
    # 使用系统对话框上传（需要用户手动选择或使用工具如 yd）

    # 或使用快捷键（如果支持）
    # osascript -e 'tell application "System Events" to keystroke "g" using {command down, shift down}'

    return 0
}

export -f fulfill_order
```

---

### 模板 5：API发货（调用外部服务）

**适用场景：**
- 调用自动生成秘钥的API
- 集成第三方发货服务
- 调用自己的服务器

**使用方法：**

```bash
#!/bin/bash
# fulfillment-templates/05-api-delivery.sh

# 配置
API_ENDPOINT="https://your-api.com/generate-key"
API_KEY="YOUR_API_KEY"

# 调用API生成秘钥
call_api_generate_key() {
    local buyer_nickname="$1"
    local product_title="$2"

    echo "📡 调用API生成秘钥..."

    response=$(curl -s -X POST "$API_ENDPOINT" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"buyer\": \"$buyer_nickname\",
            \"product\": \"$product_title\",
            \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
        }")

    # 解析响应（假设返回 {"key": "xxx", "success": true}）
    if command -v jq &> /dev/null; then
        key=$(echo "$response" | jq -r '.key')
        success=$(echo "$response" | jq -r '.success')
    else
        # 如果没有jq，使用grep
        key=$(echo "$response" | grep -o '"key":"[^"]*"' | cut -d'"' -f4)
        success=$(echo "$response" | grep -o '"success":[^,]*' | cut -d':' -f2)
    fi

    if [ "$success" = "true" ] && [ -n "$key" ]; then
        echo "$key"
        return 0
    else
        echo "❌ API调用失败：$response"
        return 1
    fi
}

# 发货钩子
fulfill_order() {
    echo "📦 通过API发货..."

    # 获取订单上下文
    local buyer="$BUYER_NICKNAME"
    local product="$PRODUCT_TITLE"

    # 调用API
    key=$(call_api_generate_key "$buyer" "$product")
    if [ $? -ne 0 ]; then
        echo "❌ 生成秘钥失败"
        return 1
    fi

    echo "✅ 生成秘钥：$key"

    # 发送秘钥
    agent-browser type "您的秘钥：$key，祝您使用愉快！"
    sleep 1
    agent-browser click "发 送"

    return 0
}

export -f fulfill_order
```

---

### 模板 6：文件发货（发送本地文件）

**适用场景：**
- 发送PDF/电子书
- 发送压缩包（资源包）
- 发送软件安装包

**使用方法：**

```bash
#!/bin/bash
# fulfillment-templates/06-file-delivery.sh

# 配置
PRODUCT_FILE="$HOME/Downloads/product.pdf"

# 发货钩子
fulfill_order() {
    echo "📦 发送文件..."

    if [ ! -f "$PRODUCT_FILE" ]; then
        echo "❌ 文件不存在：$PRODUCT_FILE"
        return 1
    fi

    # 先发送文字说明
    agent-browser type "文件已准备好，请查收："
    sleep 1
    agent-browser click "发 送"

    # 等待一下再发送文件
    sleep 2

    # 上传文件（需要根据闲鱼界面调整）
    agent-browser snapshot
    # 找到文件上传按钮
    agent-browser find role button click --name "文件" || \
    agent-browser click "＋" || \
    agent-browser find aria-label "文件" click

    # 等待文件选择器
    sleep 1

    # 这里需要根据实际界面实现文件上传
    # 可能需要使用自动化工具如 yd 或 osascript

    return 0
}

export -f fulfill_order
```

---

### 模板 7：混合发货（组合多种方式）

**适用场景：**
- 同时发送秘钥和链接
- 发送多个步骤的指引
- 复杂的发货流程

**使用方法：**

```bash
#!/bin/bash
# fulfillment-templates/07-hybrid-delivery.sh

# 配置
SECRET_KEY="YOUR_KEY"
DOWNLOAD_LINK="https://example.com/download"
TUTORIAL_LINK="https://example.com/tutorial"

# 发货钩子
fulfill_order() {
    echo "📦 混合发货..."

    # 发送第1条消息：秘钥
    agent-browser type "🔑 秘钥：$SECRET_KEY"
    sleep 1
    agent-browser click "发 送"

    sleep 1

    # 发送第2条消息：下载链接
    agent-browser type "📥 下载链接：$DOWNLOAD_LINK"
    sleep 1
    agent-browser click "发 送"

    sleep 1

    # 发送第3条消息：教程链接
    agent-browser type "📖 使用教程：$TUTORIAL_LINK\n\n如有问题随时联系我！"
    sleep 1
    agent-browser click "发 送"

    return 0
}

export -f fulfill_order
```

---

## 🛠️ 自定义发货流程

### 方法 1：使用内置模板（推荐）

选择最接近你需求的模板，复制并修改配置：

```bash
# 复制模板
cp fulfillment-templates/02-key-pool.sh my-fulfillment.sh

# 编辑配置
nano my-fulfillment.sh
```

### 方法 2：从头创建

创建自己的发货脚本：

```bash
#!/bin/bash
# my-fulfillment.sh

# 添加你的配置
MY_CONFIG="value"

# 实现发货钩子
fulfill_order() {
    # 你的发货逻辑

    return 0
}

# 导出钩子
export -f fulfill_order
```

### 方法 3：高级自定义（Python/Node.js等）

如果你更熟悉其他语言，也可以用其他语言实现发货逻辑：

```python
#!/usr/bin/env python3
# my-fulfillment.py

import os
import json

def fulfill_order():
    """发货钩子"""
    buyer = os.getenv('BUYER_NICKNAME', 'Unknown')
    product = os.getenv('PRODUCT_TITLE', 'Unknown')

    print(f"📦 发货给 {buyer}")

    # 你的Python发货逻辑
    key = generate_key()  # 你的秘钥生成逻辑

    print(f"✅ 生成秘钥：{key}")

    # 返回0表示成功，非0表示失败
    return 0

if __name__ == '__main__':
    exit(fulfill_order())
```

然后在Bash脚本中调用：
```bash
fulfill_order() {
    python3 my-fulfillment.py
    return $?
}
```

---

## 🚀 框架核心实现

### 主监控脚本

```bash
#!/bin/bash
# monitor.sh - 主监控脚本

set -e

# 配置
FULFILLMENT_SCRIPT="./my-fulfillment.sh"
CHAT_URL="https://www.goofish.com/im"
PROFILE="$HOME/Library/Application Support/Google/Chrome/Default"
LOG_FILE="fulfillment-$(date +%Y%m%d).log"
CHECK_INTERVAL=30  # 检查间隔（秒）

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 加载发货钩子
load_fulfillment_hook() {
    if [ -f "$FULFILLMENT_SCRIPT" ]; then
        log "📦 加载发货脚本：$FULFILLMENT_SCRIPT"
        source "$FULFILLMENT_SCRIPT"
    else
        log "❌ 发货脚本不存在：$FULFILLMENT_SCRIPT"
        exit 1
    fi
}

# 检测付款
check_payment() {
    log "🔍 检测付款状态..."

    # 获取聊天快照
    local snapshot=$(agent-browser snapshot)

    # 检测付款卡片
    if echo "$snapshot" | grep -q "我已付款，等待你发货" && \
       echo "$snapshot" | grep -q "button.*去发货"; then
        log "✅ 检测到付款"
        return 0
    else
        log "⏸️  暂无新付款"
        return 1
    fi
}

# 提取订单上下文
extract_order_context() {
    # 从聊天快照中提取订单信息
    local snapshot=$(agent-browser snapshot)

    # 提取买家昵称（根据实际页面结构调整）
    BUYER_NICKNAME=$(echo "$snapshot" | grep -oP '(?<=nickname":")[^"]*')

    # 提取商品标题
    PRODUCT_TITLE=$(echo "$snapshot" | grep -oP '(?<=title":")[^"]*')

    # 导出为环境变量
    export BUYER_NICKNAME
    export PRODUCT_TITLE
    export ORDER_TIME=$(date '+%Y-%m-%d %H:%M:%S')

    log "📋 订单信息：买家=$BUYER_NICKNAME, 商品=$PRODUCT_TITLE"
}

# 执行发货
execute_fulfillment() {
    log "🚀 执行发货..."

    # 提取订单上下文
    extract_order_context

    # 调用发货钩子
    if declare -f fulfill_order > /dev/null; then
        fulfill_order
        local result=$?
        if [ $result -eq 0 ]; then
            log "✅ 发货成功"
        else
            log "❌ 发货失败（返回码：$result）"
        fi
        return $result
    else
        log "❌ 发货钩子函数未定义"
        return 1
    fi
}

# 主循环
main() {
    log "🚀 启动闲鱼自动发货系统"

    # 加载发货钩子
    load_fulfillment_hook

    # 打开闲鱼
    agent-browser --headed --profile "$PROFILE" open "$CHAT_URL"
    sleep 5

    # 监控循环
    while true; do
        if check_payment; then
            execute_fulfillment

            # 发货后等待一段时间再检查下一个
            sleep 60
        else
            sleep $CHECK_INTERVAL
        fi
    done
}

# 运行
main
```

---

## 📋 完整工作流程

### 首次设置

```bash
# 1. 创建工作目录
mkdir -p ~/xianyu-auto-fulfillment
cd ~/xianyu-auto-fulfillment

# 2. 安装依赖
npm install -g agent-browser
agent-browser install

# 3. 复制模板
cp /path/to/xianyu-auto-fulfillment/fulfillment-templates/02-key-pool.sh my-fulfillment.sh

# 4. 编辑配置
nano my-fulfillment.sh

# 5. 创建秘钥池
echo "KEY-ABC123" > keys.txt
echo "KEY-DEF456" >> keys.txt

# 6. 首次运行（手动登录）
agent-browser --headed --profile "$PROFILE" open "https://www.goofish.com/im"
# 在浏览器中登录闲鱼

# 7. 启动监控
chmod +x monitor.sh
./monitor.sh
```

---

## 🔧 配置选项

### 环境变量

| 变量 | 说明 | 默认值 |
|-----|------|--------|
| `FULFILLMENT_SCRIPT` | 发货脚本路径 | `./my-fulfillment.sh` |
| `CHAT_URL` | 闲鱼聊天URL | `https://www.goofish.com/im` |
| `PROFILE` | Chrome配置文件路径 | `~/Library/Application Support/Google/Chrome/Default` |
| `CHECK_INTERVAL` | 检查间隔（秒） | `30` |
| `LOG_FILE` | 日志文件路径 | `fulfillment-YYYYMMDD.log` |

### agent-browser 配置

```bash
export AGENT_BROWSER_PROFILE="$HOME/Library/Application Support/Google/Chrome/Default"
export AGENT_BROWSER_HEADED=true
export AGENT_BROWSER_TIMEOUT=25000
```

---

## 📝 日志记录

### 日志格式

```
[2026-02-28 15:30:00] 🚀 启动闲鱼自动发货系统
[2026-02-28 15:30:05] 📦 加载发货脚本：my-fulfillment.sh
[2026-02-28 15:30:10] 🔍 检测付款状态...
[2026-02-28 15:30:15] ✅ 检测到付款
[2026-02-28 15:30:15] 📋 订单信息：买家=atting丶, 商品=VIP会员
[2026-02-28 15:30:16] 🚀 执行发货...
[2026-02-28 15:30:16] 📦 从秘钥池获取秘钥...
[2026-02-28 15:30:16] ✅ 获取到秘钥：KEY-ABC123
[2026-02-28 15:30:18] ✅ 发货成功
```

### 查看日志

```bash
# 查看今天的日志
cat fulfillment-$(date +%Y%m%d).log

# 实时监控日志
tail -f fulfillment-$(date +%Y%m%d).log

# 搜索发货记录
grep "发货成功" fulfillment-$(date +%Y%m%d).log
```

---

## 🔔 通知提醒

### macOS 通知

```bash
# 在发货钩子中添加
osascript -e 'display notification "闲鱼订单已完成" with title "发货成功"'
```

### Telegram 通知

```bash
# 在发货钩子中添加
send_telegram_notification() {
    local message="闲鱼订单已完成\n\n买家：$BUYER_NICKNAME\n秘钥：$key"
    curl -s -X POST "https://api.telegram.org/botYOUR_BOT_TOKEN/sendMessage" \
        -d "chat_id=YOUR_CHAT_ID" \
        -d "text=$message"
}
```

### 企业微信通知

```bash
# 企业微信机器人
send_wework_notification() {
    local webhook_url="YOUR_WEBHOOK_URL"
    local data=$(cat <<EOF
{
    "msgtype": "text",
    "text": {
        "content": "闲鱼订单已完成\n买家：$BUYER_NICKNAME\n秘钥：$key"
    }
}
EOF
)
    curl -s -X POST "$webhook_url" -H "Content-Type: application/json" -d "$data"
}
```

---

## ⚠️ 故障排查

### 问题 1：无法检测付款

**症状：** `check_payment` 始终返回"暂无新付款"

**排查步骤：**
1. 确认买家已付款（在闲鱼APP中查看）
2. 确认是系统卡片，不是用户文本
3. 检查快照内容：`agent-browser snapshot | grep "我已付款"`
4. 确认是否有"去发货"按钮

**解决方案：**
```bash
# 手动检查页面
agent-browser snapshot

# 检查是否有付款卡片
agent-browser snapshot | grep "我已付款"
agent-browser snapshot | grep "去发货"
```

---

### 问题 2：发货脚本未加载

**症状：** `❌ 发货钩子函数未定义`

**排查步骤：**
1. 检查脚本是否存在：`ls -l my-fulfillment.sh`
2. 检查是否有执行权限：`chmod +x my-fulfillment.sh`
3. 检查是否正确导出函数：`export -f fulfill_order`
4. 检查脚本语法：`bash -n my-fulfillment.sh`

**解决方案：**
```bash
# 确保脚本中有这一行
export -f fulfill_order

# 检查函数是否定义
declare -f fulfill_order
```

---

### 问题 3：Chrome 登录失效

**症状：** 闲鱼要求重新登录

**解决方案：**
```bash
# 手动登录一次
agent-browser --headed --profile "$PROFILE" open "https://www.goofish.com/im"
# 在浏览器中完成登录
```

---

### 问题 4：按钮点击失败

**症状：** `agent-browser click "发 送"` 无效

**解决方案：**
```bash
# 方法1：使用 ref 点击
agent-browser snapshot -i  # 获取可交互元素的 ref
agent-browser click @e8

# 方法2：使用角色查找
agent-browser find role button click --name "发送"

# 方法3：使用 ARIA 标签
agent-browser find aria-label "发送" click
```

---

## 🎓 最佳实践

### 1. 错误处理

```bash
fulfill_order() {
    # 启用严格模式
    set -e

    # 检查必要条件
    if [ -z "$SECRET_KEY" ]; then
        echo "❌ SECRET_KEY 未配置"
        return 1
    fi

    # 执行发货
    agent-browser type "您的秘钥：$SECRET_KEY"
    sleep 1

    # 验证发送成功
    if agent-browser find text "您的秘钥" > /dev/null; then
        echo "✅ 发送成功"
        return 0
    else
        echo "❌ 发送失败"
        return 1
    fi
}
```

### 2. 重试机制

```bash
fulfill_order() {
    local max_retries=3
    local retry_count=0

    while [ $retry_count -lt $max_retries ]; do
        if send_key "$SECRET_KEY"; then
            echo "✅ 发货成功"
            return 0
        else
            retry_count=$((retry_count + 1))
            echo "⚠️  发送失败，重试 $retry_count/$max_retries..."
            sleep 2
        fi
    done

    echo "❌ 发货失败，已达最大重试次数"
    return 1
}
```

### 3. 订单限流

```bash
# 防止同一买家短时间内重复下单
check_rate_limit() {
    local buyer="$BUYER_NICKNAME"
    local last_fulfillment_file=".last_fulfillment_$buyer"
    local min_interval=300  # 5分钟

    if [ -f "$last_fulfillment_file" ]; then
        local last_time=$(cat "$last_fulfillment_file")
        local current_time=$(date +%s)
        local elapsed=$((current_time - last_time))

        if [ $elapsed -lt $min_interval ]; then
            echo "⚠️  买家 $buyer 距上次发货仅 ${elapsed}秒，跳过"
            return 1
        fi
    fi

    date +%s > "$last_fulfillment_file"
    return 0
}

fulfill_order() {
    if ! check_rate_limit; then
        return 1
    fi

    # 正常发货逻辑
    ...
}
```

### 4. 日志增强

```bash
log_order() {
    local status="$1"
    local key="$2"

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $status | 买家：$BUYER_NICKNAME | 商品：$PRODUCT_TITLE | 秘钥：$key" >> "$LOG_FILE"
}

fulfill_order() {
    log_order "开始发货" "$key"

    if send_key "$key"; then
        log_order "发货成功" "$key"
        return 0
    else
        log_order "发货失败" "$key"
        return 1
    fi
}
```

---

## 🤝 贡献指南

欢迎贡献新的发货模板！

### 提交模板

1. 在 `fulfillment-templates/` 目录下创建新文件
2. 遵循命名规范：`XX-description.sh`
3. 添加详细注释
4. 提供配置示例
5. 更新本文档

### 模板结构

```bash
#!/bin/bash
# fulfillment-templates/XX-description.sh

# === 配置区 ===
# 在这里添加你的配置

# === 函数区 ===
# 在这里实现你的发货逻辑

# 发货钩子（必须实现）
fulfill_order() {
    # 你的发货逻辑
    return 0
}

export -f fulfill_order
```

---

## 📄 许可证

MIT License

---

## 🆘 获取帮助

- 查看模板目录：`fulfillment-templates/`
- 查看日志：`fulfillment-YYYYMMDD.log`
- GitHub Issues：[提交问题](https://github.com/your-repo/issues)
- Discord 社区：[加入讨论](https://discord.gg/clawd)

---

**免责声明：** 本框架仅供学习和个人使用，请遵守闲鱼的使用条款。作者不对使用本框架造成的任何后果负责。