# Webhook 通知工具 📢

一个统一的webhook发送工具，支持多种主流平台的webhook通知。

## ✨ 特性

- 🎯 **多平台支持**：钉钉、企业微信、飞书、Slack
- 🔧 **完全自定义**：支持任意HTTP POST请求
- 📝 **多种消息格式**：文本、Markdown、富文本卡片
- 👥 **灵活路由**：支持@用户、@所有人
- 🔒 **安全可靠**：支持环境变量配置、关键字验证
- 🧪 **易于测试**：内置webhook测试工具

---

## 📦 安装

### 1. 下载文件

将以下文件下载到你的工作目录：

```
webhook-notify/
├── SKILL.md              # 技能文档（完整使用指南）
├── webhook-functions.ps1 # PowerShell函数库
├── examples.ps1          # 使用示例
└── README.md             # 本文档
```

### 2. 引用函数库

在PowerShell脚本中引用：

```powershell
# 方法1: 绝对路径
. "E:\devdir\clawd\skills\webhook-notify\webhook-functions.ps1"

# 方法2: 相对路径
. ".\webhook-functions.ps1"

# 方法3: 添加到PowerShell Profile（全局可用）
# 将以下内容添加到 $PROFILE 文件
# . "E:\devdir\clawd\skills\webhook-notify\webhook-functions.ps1"
```

---

## 🚀 快速开始

### 1. 配置环境变量

**Windows PowerShell**:
```powershell
# 临时设置（当前会话）
$env:DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"
$env:WECOM_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
$env:FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK"

# 永久设置（系统环境变量）
[System.Environment]::SetEnvironmentVariable('DINGTALK_WEBHOOK', 'https://...', 'User')
```

**Linux/Mac**:
```bash
# ~/.bashrc 或 ~/.zshrc
export DINGTALK_WEBHOOK="https://oapi.dingtalk.com/robot/send?access_token=..."
export WECOM_WEBHOOK="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=..."
```

---

### 2. 发送第一条消息

```powershell
# 引用函数库
. "E:\devdir\clawd\skills\webhook-notify\webhook-functions.ps1"

# 发送钉钉消息
Send-WebhookDingTalk -WebhookUrl $env:DINGTALK_WEBHOOK -Message "【openclaw】测试消息"
```

---

## 📖 常见用法

### 钉钉

```powershell
# 文本消息 @所有人
Send-WebhookDingTalk -WebhookUrl $env:DINGTALK_WEBHOOK `
    -Message "【告警】系统异常" `
    -IsAtAll $true

# Markdown消息
Send-WebhookDingTalk -WebhookUrl $env:DINGTALK_WEBHOOK `
    -Type markdown `
    -Title "告警" `
    -Content "## 系统异常`n- CPU: 95%`n- 内存: 90%"

# ActionCard带按钮
Send-WebhookDingTalk -WebhookUrl $env:DINGTALK_WEBHOOK `
    -Type actionCard `
    -Title "告警详情" `
    -Text "CPU使用率：95%" `
    -Buttons @(
        @{title="查看详情";url="https://example.com"},
        @{title="确认";url="https://example.com/ack"}
    )
```

---

### 企业微信

```powershell
# 文本消息 @指定用户
Send-WebhookWeCom -WebhookUrl $env:WECOM_WEBHOOK `
    -Message "告警信息" `
    -AtUsers @("13800138000")

# Markdown消息
Send-WebhookWeCom -WebhookUrl $env:WECOM_WEBHOOK `
    -Type markdown `
    -Content "**告警**`n系统异常，请及时处理"
```

---

### 飞书

```powershell
# 文本消息
Send-WebhookFeishu -WebhookUrl $env:FEISHU_WEBHOOK `
    -Message "【openclaw】告警"

# 富文本卡片
Send-WebhookFeishu -WebhookUrl $env:FEISHU_WEBHOOK `
    -Type post `
    -Title "系统告警" `
    -Content @(
        @{tag="text";text="CPU使用率：95%"},
        @{tag="text";text="时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"}
    )
```

---

### Slack

```powershell
# 简单文本
Send-WebhookSlack -WebhookUrl $env:SLACK_WEBHOOK `
    -Message "System Alert: CPU high" `
    -Username "OpenClaw Bot" `
    -IconEmoji ":warning:"

# Block Kit
Send-WebhookSlack -WebhookUrl $env:SLACK_WEBHOOK `
    -Type block `
    -Blocks @(
        @{type="section";text=@{type="mrkdwn";text="*Alert*`nCPU: 95%"}},
        @{type="actions";elements=@(@{type="button";text=@{type="plain_text";text="View"};url="https://example.com"})}
    )
```

---

### 自定义HTTP请求

```powershell
Send-WebhookCustom -Url "https://api.example.com/webhook" `
    -Body @{
        event = "alert"
        severity = "high"
        timestamp = (Get-Date -Format "o")
    } `
    -Headers @{"X-API-Key"="your-key"}
```

---

## 🧪 测试Webhook

```powershell
# 引用函数库
. "E:\devdir\clawd\skills\webhook-notify\webhook-functions.ps1"

# 测试钉钉
Test-Webhook -Url $env:DINGTALK_WEBHOOK -Platform DingTalk

# 测试企业微信
Test-Webhook -Url $env:WECOM_WEBHOOK -Platform WeCom

# 测试飞书
Test-Webhook -Url $env:FEISHU_WEBHOOK -Platform Feishu
```

---

## 💡 实际应用场景

### 1. 系统监控告警

```powershell
function Send-SystemAlert {
    param(
        [string]$Component,
        [string]$CurrentValue,
        [string]$Threshold
    )
    
    $status = if ([double]$CurrentValue -gt [double]$Threshold) { "🚨 严重" } else { "⚠️ 警告" }
    
    $alertMessage = @"
【openclaw】$status | $Component 异常

- 当前值: $CurrentValue
- 阈值: $Threshold
- 时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

请及时处理！
"@
    
    Send-WebhookDingTalk -WebhookUrl $env:DINGTALK_WEBHOOK `
        -Message $alertMessage `
        -IsAtAll ($status -eq "🚨 严重")
}

# 使用
Send-SystemAlert -Component "CPU" -CurrentValue "95%" -Threshold "85%"
```

---

### 2. Elasticsearch日志监控

```powershell
function Send-ESAlert {
    param(
        [hashtable]$Analysis
    )
    
    if (-not $Analysis['alert']) { return }
    
    $content = @"
📊 异常总数: $($Analysis['total']) 条

## 受影响设备TOP5
$($Analysis['hostname_stats'].GetEnumerator() | ForEach-Object { "$($_.Key): $($_.Value) 条" } | Out-String)

## 最新日志
$($Analysis['recent_logs'] | Select-Object -First 5 | ForEach-Object { "$($_.timestamp.Substring(11,8)) [$($_.hostname))] $($_.brief)" } | Out-String)
"@
    
    Send-WebhookDingTalk -WebhookUrl $env:DINGTALK_WEBHOOK `
        -Type markdown `
        -Title "[openclaw] ES异常告警" `
        -Content $content `
        -IsAtAll $true
}
```

---

### 3. 部署通知

```powershell
function Send-DeployNotification {
    param(
        [string]$Project,
        [string]$Version,
        [string]$Environment,
        [string]$Url
    )
    
    Send-WebhookDingTalk -WebhookUrl $env:DINGTALK_WEBHOOK `
        -Type actionCard `
        -Title "✅ 部署成功" `
        -Text @"
项目: $Project
版本: $Version
环境: $Environment
时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@ `
        -Buttons @(
            @{title="查看部署";url=$Url},
            @{title="回滚";url="$Url/rollback"}
        )
}

Send-DeployNotification -Project "MyApp" -Version "v1.2.3" -Environment "production" -Url "https://deploy.example.com"
```

---

## ⚠️ 常见问题

### Q1: 钉钉报错 "keywords not in content"

**原因**: 消息中缺少机器人设置的关键字

**解决**:
```powershell
# 确保消息包含关键字
Send-WebhookDingTalk -WebhookUrl $url -Message "【openclaw】告警" -Keyword "openclaw"
```

---

### Q2: 如何@指定手机号？

```powershell
# 钉钉
Send-WebhookDingTalk -WebhookUrl $url -Message "告警" -AtMobiles @("13800138000")

# 企业微信
Send-WebhookWeCom -WebhookUrl $url -Message "告警" -AtUsers @("13800138000")
```

---

### Q3: 如何设置环境变量永久生效？

**Windows**:
```powershell
# 设置当前用户环境变量（重启PowerShell生效）
[System.Environment]::SetEnvironmentVariable('DINGTALK_WEBHOOK', 'https://...', 'User')

# 设置系统环境变量（需要管理员权限）
[System.Environment]::SetEnvironmentVariable('DINGTALK_WEBHOOK', 'https://...', 'Machine')
```

**Linux/Mac**:
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
echo 'export DINGTALK_WEBHOOK="https://..."' >> ~/.bashrc
source ~/.bashrc
```

---

### Q4: 如何批量发送到多个webhook？

```powershell
$webhooks = @(
    @{Type="DingTalk";Url=$env:DINGTALK_WEBHOOK},
    @{Type="WeCom";Url=$env:WECOM_WEBHOOK},
    @{Type="Feishu";Url=$env:FEISHU_WEBHOOK}
)

$message = "批量测试消息"

foreach ($webhook in $webhooks) {
    switch ($webhook.Type) {
        'DingTalk' { Send-WebhookDingTalk -WebhookUrl $webhook.Url -Message $message }
        'WeCom'    { Send-WebhookWeCom -WebhookUrl $webhook.Url -Message $message }
        'Feishu'   { Send-WebhookFeishu -WebhookUrl $webhook.Url -Message $message }
    }
}
```

---

### Q5: 如何调试webhook发送？

```powershell
# 1. 使用Test-Webhook函数测试连通性
Test-Webhook -Url $env:DINGTALK_WEBHOOK -Platform DingTalk

# 2. 查看详细错误信息（使用-Verbose）
Send-WebhookDingTalk -WebhookUrl $env:DINGTALK_WEBHOOK -Message "测试" -Verbose

# 3. 捕获错误
try {
    Send-WebhookDingTalk -WebhookUrl $env:DINGTALK_WEBHOOK -Message "测试"
} catch {
    Write-Error "发送失败: $_"
}
```

---

## 📚 更多资源

### 官方文档

- [钉钉机器人API](https://open.dingtalk.com/document/robots/custom-robot-access)
- [企业微信机器人API](https://developer.work.weixin.qq.com/document/path/91770)
- [飞书机器人API](https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNkjE3)
- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)

---

### 本地文档

- `SKILL.md` - 完整的函数参考和高级用法
- `examples.ps1` - 13个实用示例

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

## 📞 支持

如有问题，请检查：
1. Webhook URL配置是否正确
2. 网络连接是否正常（防火墙/代理）
3. 消息格式是否符合平台要求
4. 关键字/签名等安全配置是否正确

查看 `SKILL.md` 获取完整文档。
