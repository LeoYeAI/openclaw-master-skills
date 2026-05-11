# 🚀 闲鱼监控 - 快速启动指南

## 使用子代理自动监控闲鱼

### 前置条件

1. ✅ 已安装 agent-browser
   ```bash
   npm install -g agent-browser
   agent-browser install
   ```

2. ✅ 已在浏览器中登录闲鱼

3. ✅ 已选择发货模板并配置

---

## 启动步骤

### 第 1 步：配置发货模板

```bash
cd /Users/yuehuali/Desktop/xianyu-auto-fulfillment

# 选择秘钥池模板（推荐）
cp fulfillment-templates/02-key-pool.sh my-fulfillment.sh
```

### 第 2 步：创建秘钥池

```bash
# 复制示例文件
cp keys.example.txt keys.txt

# 编辑秘钥池（每行一个秘钥）
nano keys.txt

# 示例内容：
# KEY-ABC123
# KEY-DEF456
# KEY-GHI789
```

### 第 3 步：启动监控

**最简单的方式 - 在对话中启动：**

直接告诉 AI 助手：

> "启动闲鱼监控子代理，每分钟检查一次闲鱼新消息，检测到付款后使用秘钥池模板自动发货"

AI 助手会自动：
1. 创建子代理会话
2. 加载监控脚本
3. 启动浏览器
4. 开始循环监控

---

## 监控工作流程

```
每 60 秒循环
    ↓
1. 检查是否有新消息
    ↓
2. 如果有新消息，进入聊天
    ↓
3. 检测是否需要发货
   （检测付款卡片："我已付款，等待你发货" + "去发货"按钮）
    ↓
4. 如果需要发货
   - 加载发货模板
   - 从秘钥池获取秘钥
   - 发送秘钥到聊天
   - 返回聊天列表
    ↓
5. 等待 60 秒，继续下一次检查
```

---

## 停止监控

在对话中告诉 AI 助手：

> "停止闲鱼监控" 或 "终止子代理"

---

## 查看日志

```bash
# 实时查看日志
tail -f fulfillment-$(date +%Y%m%d).log
```

---

## 文件说明

| 文件 | 说明 |
|-----|------|
| `xianyu-monitor-agent.sh` | 主监控脚本（由子代理运行） |
| `start-monitor.sh` | 启动说明脚本 |
| `stop-monitor.sh` | 停止说明脚本 |
| `monitor-config.sh` | 监控配置文件 |
| `my-fulfillment.sh` | 你的发货脚本（自定义） |
| `keys.txt` | 秘钥池文件 |

---

## 发货模板选择

| 模板 | 适用场景 | 文件 |
|-----|---------|------|
| 固定秘钥 | 测试商品 | `01-fixed-key.sh` |
| 秘钥池 | 批量售卖（推荐） | `02-key-pool.sh` |
| 链接发货 | 网盘链接 | `03-link-delivery.sh` |
| 图片发货 | 二维码 | `04-image-delivery.sh` |
| API发货 | 外部服务 | `05-api-delivery.sh` |
| 文件发货 | 本地文件 | `06-file-delivery.sh` |
| 混合发货 | 多种组合 | `07-hybrid-delivery.sh` |

---

## 常见问题

### Q: 如何更换发货模板？

```bash
# 1. 复制新模板
cp fulfillment-templates/03-link-delivery.sh my-fulfillment.sh

# 2. 编辑配置
nano my-fulfillment.sh

# 3. 重启监控
# 在对话中：先"停止闲鱼监控"，再"启动闲鱼监控"
```

### Q: 如何修改检查间隔？

编辑 `xianyu-monitor-agent.sh`，修改：
```bash
CHECK_INTERVAL=30  # 改为你想要的间隔（秒）
```

### Q: 监控会自动重启吗？

不会。如果需要持久运行，建议：
1. 使用 OpenClaw 子代理的 session 模式
2. 或使用系统工具如 `tmux`/`screen` 运行

### Q: 如何查看运行状态？

```bash
# 查看日志
tail -f fulfillment-$(date +%Y%m%d).log

# 查看进程
ps aux | grep xianyu-monitor-agent.sh
```

---

## 技术细节

### 付款检测规则

**可以发货 ✅：**
- 系统消息卡片（带图标）
- 卡片内容："我已付款，等待你发货"
- 有"去发货"按钮

**不能发货 ❌：**
- 用户手打的文本
- 没有"去发货"按钮的消息
- "待付款"状态

### 安全特性

- ✅ 使用真实 Chrome 配置文件（保持登录状态）
- ✅ 使用有界面模式（避免反机器人检测）
- ✅ 每次发货后自动返回聊天列表
- ✅ 完整的日志记录
- ✅ 支持手动停止

---

**需要帮助？** 查看 `SKILL.md` 获取完整文档。
