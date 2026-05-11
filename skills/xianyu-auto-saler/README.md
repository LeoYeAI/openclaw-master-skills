# 🐟 闲鱼自动发货框架

一个可扩展的闲鱼虚拟商品自动化发货系统。核心提供付款检测，发货流程完全可自定义。

## ✨ 核心特点

- 🔍 **自动检测付款**：智能识别闲鱼系统付款卡片
- 🎯 **可扩展设计**：支持任意发货方式（秘钥、链接、图片、文件、API等）
- 📦 **开箱即用**：7种内置发货模板，直接复制使用
- 🔧 **零侵入**：框架不强制特定发货方式，完全自定义
- 🌐 **真实浏览器**：使用 agent-browser，避免被封

## 🚀 快速开始

### 1. 安装依赖

```bash
npm install -g agent-browser
agent-browser install
```

### 2. 选择发货模板

```bash
# 查看可用模板
ls -l fulfillment-templates/

# 复制模板（以秘钥池为例）
cp fulfillment-templates/02-key-pool.sh my-fulfillment.sh
```

### 3. 配置模板

```bash
# 编辑配置
nano my-fulfillment.sh

# 修改 SECRET_KEY 或 KEY_POOL_FILE 等配置
```

### 4. 创建秘钥池（如使用模板2）

```bash
# 创建秘钥池文件
echo "KEY-ABC123" > keys.txt
echo "KEY-DEF456" >> keys.txt
echo "KEY-GHI789" >> keys.txt
```

### 5. 首次登录闲鱼

```bash
# 使用有界面模式打开闲鱼
agent-browser --headed --profile "$HOME/Library/Application Support/Google/Chrome/Default" open "https://www.goofish.com/im"

# 在浏览器中完成登录（首次需要）
```

### 6. 启动监控

```bash
# 启动监控脚本
./monitor.sh

# 查看日志
tail -f fulfillment-$(date +%Y%m%d).log
```

---

## 📦 内置发货模板

| 模板 | 文件 | 适用场景 |
|-----|------|---------|
| 固定秘钥 | `01-fixed-key.sh` | 测试商品、免费资源 |
| 秘钥池 | `02-key-pool.sh` | 批量售卖，每人不同秘钥 |
| 链接发货 | `03-link-delivery.sh` | 网盘链接、下载地址 |
| 图片发货 | `04-image-delivery.sh` | 二维码、教程截图 |
| API发货 | `05-api-delivery.sh` | 调用外部服务生成秘钥 |
| 文件发货 | `06-file-delivery.sh` | 发送PDF、压缩包等文件 |
| 混合发货 | `07-hybrid-delivery.sh` | 组合多种发货方式 |

---

## 🎯 发货流程

```
1. 监控聊天
   ↓
2. 检测付款（系统卡片识别）
   ↓
3. 触发货钩子
   ↓
4. 执行自定义发货逻辑
   ↓
5. 记录日志
   ↓
6. 继续监控
```

---

## 📋 自定义发货流程

### 方法 1：使用内置模板（推荐）

```bash
# 1. 复制模板
cp fulfillment-templates/02-key-pool.sh my-fulfillment.sh

# 2. 编辑配置
nano my-fulfillment.sh

# 3. 修改配置项（如 KEY_POOL_FILE）
```

### 方法 2：从头创建

```bash
#!/bin/bash
# my-fulfillment.sh

# 配置
MY_CONFIG="value"

# 实现发货钩子
fulfill_order() {
    # 你的发货逻辑
    echo "📦 发货中..."

    # 发送消息
    agent-browser type "您的商品信息..."
    sleep 1
    agent-browser click "发 送"

    return 0
}

export -f fulfill_order
```

### 方法 3：使用其他语言

```python
#!/usr/bin/env python3
# my-fulfillment.py

import os

def fulfill_order():
    buyer = os.getenv('BUYER_NICKNAME', 'Unknown')
    print(f"📦 发货给 {buyer}")

    # 你的Python逻辑
    # ...

    return 0  # 0表示成功

if __name__ == '__main__':
    exit(fulfill_order())
```

然后在Bash钩子中调用：
```bash
fulfill_order() {
    python3 my-fulfillment.py
    return $?
}
```

---

## 🔧 配置选项

编辑 `monitor.sh` 修改配置：

```bash
# 发货脚本路径
FULFILLMENT_SCRIPT="./my-fulfillment.sh"

# 闲鱼聊天URL
CHAT_URL="https://www.goofish.com/im"

# Chrome配置文件路径
PROFILE="$HOME/Library/Application Support/Google/Chrome/Default"

# 检查间隔（秒）
CHECK_INTERVAL=30
```

---

## 📝 日志格式

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

---

## ⚠️ 重要提示

### 付款检测规则

**可以发货 ✅：**
- 系统消息卡片（带图标）
- 卡片内容："我已付款，等待你发货"
- 有"去发货"按钮

**不能发货 ❌：**
- 用户手打的文本（如"我已付款了"、"老板发货"等）
- 没有"去发货"按钮的消息
- "待付款"状态的卡片

### 安全建议

- ❌ 不要在代码中硬编码敏感信息
- ✅ 使用环境变量或配置文件
- ✅ 定期更换秘钥
- ✅ 记录所有发货日志
- ✅ 设置订单频率限制

### 反机器人检测

- ✅ 使用真实的 Chrome 配置文件
- ✅ 使用 `--headed` 模式（显示浏览器）
- ❌ 不要修改 User-Agent
- ❌ 不要使用代理或 VPN

---

## 📁 文件结构

```
xianyu-auto-fulfillment/
├── SKILL.md                          # 完整技能文档
├── README.md                         # 本文件
├── _meta.json                        # 元数据
├── monitor.sh                        # 主监控脚本
├── fulfillment-templates/            # 发货模板目录
│   ├── 01-fixed-key.sh              # 固定秘钥
│   ├── 02-key-pool.sh               # 秘钥池
│   ├── 03-link-delivery.sh          # 链接发货
│   ├── 04-image-delivery.sh         # 图片发货
│   ├── 05-api-delivery.sh           # API发货
│   ├── 06-file-delivery.sh          # 文件发货
│   └── 07-hybrid-delivery.sh        # 混合发货
├── my-fulfillment.sh                # 你的发货脚本（自定义）
├── keys.txt                         # 秘钥池文件（可选）
├── used-keys.txt                   # 已使用秘钥记录（自动生成）
└── fulfillment-YYYYMMDD.log        # 发货日志（自动生成）
```

---

## 🐛 故障排查

### 问题：无法检测付款

```bash
# 手动检查页面
agent-browser snapshot

# 检查是否有付款卡片
agent-browser snapshot | grep "我已付款"
agent-browser snapshot | grep "去发货"
```

### 问题：发货脚本未加载

```bash
# 检查脚本是否存在
ls -l my-fulfillment.sh

# 检查执行权限
chmod +x my-fulfillment.sh

# 检查函数是否导出
bash -n my-fulfillment.sh
```

### 问题：按钮点击失败

```bash
# 使用 ref 点击
agent-browser snapshot -i
agent-browser click @e8

# 或使用角色查找
agent-browser find role button click --name "发送"
```

更多故障排查请参考 `SKILL.md`。

---

## 🤝 贡献

欢迎贡献新的发货模板！

1. 在 `fulfillment-templates/` 目录下创建新文件
2. 遵循命名规范：`XX-description.sh`
3. 添加详细注释
4. 提供配置示例
5. 更新文档

---

## 📄 许可证

MIT License

---

## 🆘 获取帮助

- 📖 完整文档：查看 `SKILL.md`
- 📦 模板示例：查看 `fulfillment-templates/`
- 📝 日志查看：`fulfillment-YYYYMMDD.log`

---

## 🤖 子代理监控（推荐）

使用 OpenClaw 的子代理功能，每分钟自动检查闲鱼并处理发货。

### 快速启动

```bash
# 1. 配置发货模板
cp fulfillment-templates/02-key-pool.sh my-fulfillment.sh
# 编辑 my-fulfillment.sh 配置秘钥池等

# 2. 创建秘钥池
cp keys.example.txt keys.txt
# 编辑 keys.txt 添加真实秘钥

# 3. 启动子代理
./start-monitor.sh
```

### 启动方式

**方式 1：在 OpenClaw 对话中启动（最简单）**

直接告诉 AI 助手：
```
"启动闲鱼监控子代理，每分钟检查一次闲鱼，使用秘钥池模板发货"
```

**方式 2：使用 OpenClaw 命令行**

```bash
openclaw sessions_spawn \
  --mode session \
  --label xianyu-monitor \
  --agentId main \
  --task "启动闲鱼监控代理，每分钟检查一次闲鱼新消息，检测到付款后使用 fulfillment-templates/02-key-pool.sh 模板发货"
```

**方式 3：直接运行监控脚本**

```bash
chmod +x xianyu-monitor-agent.sh
./xianyu-monitor-agent.sh
```

### 停止监控

```bash
# 方式 1：在对话中
"停止闲鱼监控"

# 方式 2：使用停止脚本
./stop-monitor.sh

# 方式 3：手动终止
ps aux | grep xianyu-monitor-agent.sh
kill <PID>
```

### 监控脚本功能

- ✅ 每分钟自动检查闲鱼新消息
- ✅ 自动进入有未读消息的聊天
- ✅ 智能检测付款卡片（"我已付款，等待你发货" + "去发货"按钮）
- ✅ 自动执行发货流程
- ✅ 发货完成后返回聊天列表
- ✅ 完整的日志记录
- ✅ 支持任意发货模板

### 监控日志

```bash
# 查看今天的日志
tail -f fulfillment-$(date +%Y%m%d).log
```

日志示例：
```
[2026-02-28 16:00:00] 🚀 启动闲鱼监控代理
[2026-02-28 16:00:05] 🌐 打开闲鱼聊天页面...
[2026-02-28 16:00:08] ✅ 闲鱼聊天页面已打开
[2026-02-28 16:00:08] 🔍 检查新消息...
[2026-02-28 16:00:10] ⏸️  暂无新消息
[2026-02-28 16:00:10] ⏳ 等待 60 秒...
[2026-02-28 16:01:10] 🔍 检查新消息...
[2026-02-28 16:01:12] ✅ 检测到新消息
[2026-02-28 16:01:12] 💬 进入最新聊天...
[2026-02-28 16:01:14] ✅ 已进入聊天
[2026-02-28 16:01:14] 📋 检查订单状态...
[2026-02-28 16:01:15] ✅ 检测到付款，需要发货
[2026-02-28 16:01:15] 🚀 执行发货流程...
[2026-02-28 16:01:15] 📦 加载发货模板：02-key-pool.sh
[2026-02-28 16:01:15] 📦 从秘钥池获取秘钥...
[2026-02-28 16:01:15] ✅ 获取到秘钥：KEY-ABC123
[2026-02-28 16:01:15] 📋 订单信息：买家=atting丶, 商品=VIP会员
[2026-02-28 16:01:18] ✅ 发货成功
[2026-02-28 16:01:22] ✅ 已返回聊天列表
[2026-02-28 16:01:22] ⏳ 等待 60 秒...
```

---

**免责声明：** 本框架仅供学习和个人使用，请遵守闲鱼的使用条款。作者不对使用本框架造成的任何后果负责。
