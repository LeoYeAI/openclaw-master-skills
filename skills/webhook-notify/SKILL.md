---
name: webhook-notify
description: 通用Webhook通知工具，支持钉钉、企业微信、Slack、飞书等多种平台的webhook消息发送，以及自定义HTTP POST请求。适用于告警通知、自动化触发、系统监控等场景。
metadata: {"clawdbot":{"emoji":"🔔","requires":{"anyBins":["curl"]},"os":["linux","darwin","win32"]}}
---

# Webhook 通知工具

一个统一的webhook发送工具，支持多种主流平台的webhook通知。

## 支持的平台

| 平台 | 消息类型 | 支持功能 |
|------|---------|---------|
| **钉钉** | Text/Markdown/Link/ActionCard | @用户、@所有人、按钮交互 |
| **企业微信** | Text/Markdown/Image/File/News | 图文消息、@用户 |
| **飞书** | Text/Post/Interactive/ShareCard | 富文本、卡片、按钮 |
| **Slack** | Text/Block/Attachment | 格式化消息、按钮 |
| **自定义HTTP** | JSON/Form-Data/Raw | 完全自定义请求 |

## 快速开始

### 1. 发送钉钉消息

```powershell
# 文本消息
$webhook = "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"
Send-WebhookDingTalk -WebhookUrl $webhook -Message "【告警】系统异常" -AtAll $true

# Markdown 消息
Send-WebhookDingTalk -WebhookUrl $webhook -Type markdown -Title告警" -Content "## 内容`n详情：xxx"

# 包含附件的卡片消息
Send-WebhookDingTalk -WebhookUrl $webhook -Type actionCard -Title "告警详情" -Text "系统CPU使用率超过90%" -Buttons @(@{title="查看详情";url="https://example.com"})
```

### 2. 发送企业微信消息

```powershell
$webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"

# 文本消息 @指定用户
Send-WebhookWeCom -WebhookUrl $webhook -Message "告警信息" -AtUsers @("13800138000")

# Markdown 消息
Send-WebhookWeCom -WebhookUrl $webhook -Type markdown -Content "**告警**`n系统异常，请及时处理"
```

### 3. 发送飞书消息

```powershell
$webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK"

# 文本消息
Send-WebhookFeishu -WebhookUrl $webhook -Message "【openclaw】告警"

# 富文本卡片
Send-WebhookFeishu -WebhookUrl $webhook -Type post -Title "系统告警" -Content @(@{tag="text";text="CPU使用率：95%"})
```

### 4. 发送Slack消息

```powershell
$webhook = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# 简单文本
Send-WebhookSlack -WebhookUrl $webhook -Message "System Alert: CPU high"

# 格式化消息 (Block Kit)
Send-WebhookSlack -WebhookUrl $webhook -Type block -Blocks @(
    @{type="section";text=@{type="mrkdwn";text="*Alert*`nCPU: 95%"}}
    @{type="actions";elements=@(@{type="button";text=@{type="plain_text";text="View"};url="https://example.com"})}
)
```

### 5. 自定义HTTP请求

```powershell
# 完全自定义
Send-WebhookCustom -Url "https://your-webhook.com/endpoint" `
    -Method POST `
    -ContentType "application/json" `
    -Body @{message="custom webhook data"} `
    -Headers @{"X-Custom-Header"="value"}
```

---

## 函数参考

### Send-WebhookDingTalk

发送钉钉webhook消息。

**参数**:
- `WebhookUrl` (string): webhook地址
- `Message` (string): 文本消息内容
- `Type` (string): 消息类型 `text`|`markdown`|`actionCard`，默认 `text`
- `Title` (string): 消息标题（用于markdown和actionCard）
- `Content` (string): markdown内容
- `Text` (string): actionCard的文本内容
- `BtnOrientation` (string): 按钮方向 `0`横向|`1`纵向
- `Buttons` (array): 按钮列表 `@(@{title="btn1";url="url1"})`
- `AtMobiles` (array): @的手机号列表
- `AtUserIds` (array): @的userId列表
- `IsAtAll` (bool): 是否@所有人
- `Keyword` (string): 添加关键字（安全限制）

**示例**:

```powershell
# 文本消息 @所有人
Send-WebhookDingTalk -WebhookUrl $url -Message "【openclaw】告警" -IsAtAll $true

# Markdown @指定用户
Send-WebhookDingTalk -WebhookUrl $url -Type markdown -Title "告警" -Content "系统异常" -AtMobiles @("13800138000")

# ActionCard带按钮
Send-WebhookDingTalk -WebhookUrl $url -Type actionCard -Title "告警" `
    -Text "CPU使用率：95%" `
    -Buttons @(@{title="查看详情";url="https://example.com"}, @{title="忽略";url="https://example.com/ignore"})
```

---

### Send-WebhookWeCom

发送企业微信webhook消息。

**参数**:
- `WebhookUrl` (string): webhook地址
- `Message` (string): 文本消息内容
- `Type` (string): 消息类型 `text`|`markdown`|`image`|`news`|`file`
- `Content` (string): markdown内容
- `MdId` (string): 媒体ID（用于image/file）
- `Articles` (array): 图文消息列表
- `AtUsers` (array): @的手机号列表
- `IsAtAll` (bool): 是否@所有人

**示例**:

```powershell
# 文本消息
Send-WebhookWeCom -WebhookUrl $url -Message "系统告警"

# Markdown
Send-WebhookWeCom -WebhookUrl $url -Type markdown -Content "**标题**`n内容"

# 图文消息
Send-WebhookWeCom -WebhookUrl $url -Type news -Articles @(
    @{title="标题";description="描述";url="http://example.com";picurl="http://example.com/img.jpg"}
)
```

---

### Send-WebhookFeishu

发送飞书webhook消息。

**参数**:
- `WebhookUrl` (string): webhook地址
- `Message` (string): 文本消息内容
- `Type` (string): 消息类型 `text`|`post`|`interactive`|`shareCard`
- `Title` (string): 卡片标题
- `Content` (array): 富文本内容元素
- `Elements` (array): 交互元素（按钮等）
- `AtUsers` (array): @的open_id列表

**示例**:

```powershell
# 文本消息
Send-WebhookFeishu -WebhookUrl $url -Message "【openclaw】告警"

# 富文本卡片
Send-WebhookFeishu -WebhookUrl $url -Type post -Title "系统告警" -Content @(
    @{tag="text";text="CPU使用率：95%"}
)

# 交互卡片
Send-WebhookFeishu -WebhookUrl $url -Type interactive -Title "确认操作" `
    -Elements @(@{tag="button";text=@{tag="plain_text";content="确认"};type="primary";url="https://example.com"})
```

---

### Send-WebhookSlack

发送Slack webhook消息。

**参数**:
- `WebhookUrl` (string): webhook地址
- `Message` (string): 文本消息内容
- `Type` (string): 消息类型 `text`|`block`
- `Blocks` (array): Block Kit块
- `Attachments` (array): 附件列表
- `Channel` (string): 目标频道（覆盖默认）
- `Username` (string): 发送者名称
- `IconEmoji` (string): 图标emoji
- `IconUrl` (string): 图标URL

**示例**:

```powershell
# 简单文本
Send-WebhookSlack -WebhookUrl $url -Message "System Alert"

# Block Kit
Send-WebhookSlack -WebhookUrl $url -Type block -Blocks @(
    @{type="section";text=@{type="mrkdwn";text="*Alert*`nCPU: 95%"}},
    @{type="actions";elements=@(@{type="button";text=@{type="plain_text";text="View"};url="https://example.com"})}
)
```

---

### Send-WebhookCustom

发送自定义HTTP请求。

**参数**:
- `Url` (string): 目标URL
- `Method` (string): HTTP方法 `GET`|`POST`|`PUT`|`DELETE`，默认 `POST`
- `Body` (object 或 string): 请求体
- `ContentType` (string): Content-Type，默认 `application/json`
- `Headers` (hashtable): 请求头
- `Timeout` (int): 超时秒数，默认 30
- `UseBasicAuth` (bool): 使用基础认证
- `Username` (string): 用户名
- `Password` (string): 密码

**示例**:

```powershell
# JSON POST
Send-WebhookCustom -Url "https://api.example.com/webhook" `
    -Body @{event="alert";severity="high"} `
    -Headers @{"X-API-Key"="your-key"}

# 自定义Header
Send-WebhookCustom -Url "https://..." `
    -Method PUT `
    -Body "raw string body" `
    -ContentType "text/plain" `
    -Headers @{"Authorization"="Bearer token"}
```

---

## 高级用法

### 1. 环境变量配置

为了避免暴露敏感信息，建议将webhook URL存储在环境变量中：

**PowerShell 配置**:
```powershell
# 临时设置（当前会话）
$env:DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=..."
$env:WECOM_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=..."

# 永久设置（系统环境变量）
[System.Environment]::SetEnvironmentVariable('DINGTALK_WEBHOOK', 'https://...', 'User')
```

**使用环境变量**:
```powershell
Send-WebhookDingTalk -WebhookUrl $env:DINGTALK_WEBHOOK -Message "告警"
```

**Linux/Mac 配置**:
```bash
# ~/.bashrc 或 ~/.zshrc
export DINGTALK_WEBHOOK="https://oapi.dingtalk.com/robot/send?access_token=..."
export WECOM_WEBHOOK="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=..."
```

---

### 2. 配置文件

创建配置文件 `webhook-config.ps1`:

```powershell
# webhook-config.ps1
$Script:WebhookConfig = @{
    DingTalk = @{
        DefaultUrl = $env:DINGTALK_WEBHOOK
        Monitoring = @{
            Url = $env:DINGTALK_MONITORING_WEBHOOK
            Keyword = "【openclaw】"
        }
    }
    WeCom = @{
        DevTeam = $env:WECOM_DEV_TEAM_WEBHOOK
        Alert = $env:WECOM_ALERT_WEBHOOK
    }
    Slack = @{
        Alerts = "https://hooks.slack.com/services/..."
    }
}
```

**使用配置**:
```powershell
. .\webhook-config.ps1
Send-WebhookDingTalk -WebhookUrl $WebhookConfig.DingTalk.Monitoring.Url -Message "告警" -Keyword $WebhookConfig.DingTalk.Monitoring.Keyword
```

---

### 3. 模板化消息

创建消息模板 `message-templates.ps1`:

```powershell
# 系统告警模板
function Get-SystemAlertMessage {
    param(
        [string]$Severity,
        [string]$Component,
        [string]$Details
    )
    $severityIcon = switch ($Severity) {
        "critical" { "🚨" }
        "warning"  { "⚠️" }
        "info"     { "ℹ️" }
        default   { "📌" }
    }

    return @"
$severityIcon 系统告警

- 严重等级: $Severity
- 组件: $Component
- 详情: $Details
- 时间: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

请及时处理！
"@
}

# 使用模板
$msg = Get-SystemAlertMessage -Severity "critical" -Component "CPU" -Details "使用率: 95%"
Send-WebhookDingTalk -WebhookUrl $env:DINGTALK_WEBHOOK -Message $msg
```

---

### 4. 批量发送

```powershell
# 发送到多个webhook
$webhooks = @(
    $env:DINGTALK_WEBHOOK,
    $env:WECOM_WEBHOOK,
    $env:FEISHU_WEBHOOK
)

foreach ($url in $webhooks) {
    if ($url -match "dingtalk") {
        Send-WebhookDingTalk -WebhookUrl $url -Message "告警"
    } elseif ($url -match "qyapi.weixin") {
        Send-WebhookWeCom -WebhookUrl $url -Message "告警"
    }
}
```

---

### 5. 重试机制

```powershell
function Send-WebhookWithRetry {
    param(
        [string]$Url,
        [int]$MaxRetries = 3,
        [scriptblock]$SendAction
    )

    $attempt = 0
    while ($attempt -lt $MaxRetries) {
        $attempt++
        try {
            & $SendAction
            return $true
        } catch {
            Write-Host "尝试 $attempt/$MaxRetries 失败: $_"
            if ($attempt -lt $MaxRetries) {
                Start-Sleep -Seconds 2
            }
        }
    }
    return $false
}

# 使用重试
Send-WebhookWithRetry -Url $env:DINGTALK_WEBHOOK -MaxRetries 3 -SendAction {
    Send-WebhookDingTalk -WebhookUrl $env:DINGTALK_WEBHOOK -Message "测试消息"
}
```

---

### 6. Webhook测试工具

```powershell
function Test-Webhook {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Url,

        [ValidateSet('DingTalk', 'WeCom', 'Feishu', 'Slack', 'Custom')]
        [string]$Platform
    )

    $testMessage = "【Webhook测试】`n时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n平台: $Platform`n状态: ✅ 成功"

    switch ($Platform) {
        'DingTalk' {
            Send-WebhookDingTalk -WebhookUrl $Url -Message $testMessage
        }
        'WeCom' {
            Send-WebhookWeCom -WebhookUrl $Url -Message $testMessage
        }
        'Feishu' {
            Send-WebhookFeishu -WebhookUrl $Url -Message $testMessage
        }
        'Slack' {
            Send-WebhookSlack -WebhookUrl $Url -Message $testMessage
        }
        default {
            Send-WebhookCustom -Url $Url -Body @{message="webhook test"}
        }
    }
}

# 测试钉钉webhook
Test-Webhook -Url $env:DINGTALK_WEBHOOK -Platform DingTalk
```

---

## 安全最佳实践

### 1. 关键字验证

钉钉和企业微信webhook通常需要设置关键字验证：

```powershell
# 确保 webhook URL 包含必要的参数或消息中包含关键字
Send-WebhookDingTalk -WebhookUrl $url -Message "【openclaw】告警内容" -Keyword "openclaw"
```

### 2. 签名验证（企业微信）

如果使用企业微信签名验证：

```powershell
function Get-WeComSignature {
    param(
        [string]$Content,
        [string]$Key
    )

    $hmacsha = New-Object System.Security.Cryptography.HMACSHA256
    $hmacsha.key = [Text.Encoding]::UTF8.GetBytes($Key)
    $signature = $hmacsha.ComputeHash([Text.Encoding]::UTF8.GetBytes($Content))
    return [System.BitConverter]::ToString($signature).Replace('-', '').ToLower()
}

# 使用签名
$timestamp = [int][double]::Parse((Get-Date -UFormat %s))
$sign = Get-WeComSignature -Content $timestamp -Key $env:WECOM_KEY
$webhook = "$env:WECOM_WEBHOOK&timestamp=$timestamp&sign=$sign"
```

---

## 常见错误处理

### 错误1: 关键字缺失

**错误信息**:钉钉: `{"errcode": 310000, "errmsg": "keywords not in content"}`

**解决**:
```powershell
# 确保消息包含关键字
Send-WebhookDingTalk -WebhookUrl $url -Message "【openclaw】告警" -Keyword "openclaw"
```

---

### 错误2: 超时

**错误信息**: 请求超时

**解决**:
```powershell
# 增加超时时间
Send-WebhookDingTalk -WebhookUrl $url -Message "测试" -Timeout 60
```

---

### 错误3: IP限制

**错误信息**: `{"errcode": 310000, "errmsg": "IP not in whitelist"}`

**解决**:
在钉钉机器人设置中添加服务器IP到白名单。

---

## 完整示例

### 示例1: 系统监控告警

```powershell
# 系统资源监控告警
function Send-SystemAlert {
    param(
        [string]$Component,
        [string]$CurrentValue,
        [string]$Threshold,
        [string]$WebhookUrl = $env:DINGTALK_WEBHOOK
    )

    $status = if ([double]$CurrentValue -gt [double]$Threshold) { "🚨 严重" } else { "⚠️ 警告" }

    $message = @"
【openclaw】$status | $Component 异常

- 当前值: $CurrentValue
- 阈值: $Threshold
- 时间: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

请及时处理！
"@

    Send-WebhookDingTalk -WebhookUrl $WebhookUrl -Message $message -IsAtAll $true
}

# 使用
Send-SystemAlert -Component "CPU" -CurrentValue "95%" -Threshold "85%"
Send-SystemAlert -Component "内存" -CurrentValue "14.5/16 GB" -Threshold "90%"
```

---

### 示例2: 部署通知

```powershell
# 部署完成通知
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
时间: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@ `
        -Buttons @(
            @{title="查看部署";url=$Url},
            @{title="回滚";url="$Url/rollback"}
        )
}

Send-DeployNotification -Project "MyApp" -Version "v1.2.3" -Environment "production" -Url "https://deploy.example.com"
```

---

### 示例3: Elasticsearch 异常告警

```powershell
# ES 日志监控告警
function Send-ESAlert {
    param(
        [hashtable]$Analysis,
        [string]$WebhookUrl = $env:DINGTALK_WEBHOOK
    )

    if (-not $Analysis['alert']) {
        return
    }

    $content = @"
📊 异常总数: $($Analysis['total']) 条

## 受影响设备TOP5
$($Analysis['hostname_stats'].GetEnumerator() | ForEach-Object { "$($_.Key): $($_.Value) 条" } | Out-String)

## 异常类型TOP5  
$($Analysis['brief_stats'].GetEnumerator() | ForEach-Object { "$($_.Key): $($_.Value) 条" } | Out-String)

## 最新日志
$($Analysis['recent_logs'] | ForEach-Object { "$($_.timestamp.Substring(11,8)) [$($_.hostname))] $($_.brief)`n$($_.message)`n" } | Out-String)
"@

    Send-WebhookDingTalk -WebhookUrl $WebhookUrl `
        -Type markdown `
        -Title "[openclaw] ES异常告警" `
        -Content $content `
        -IsAtAll $true
}
```

---

## 配置文件位置

将 webhook 函数库保存为：
- Windows: `E:\devdir\clawd\skills\webhook-notify\webhook-functions.ps1`
- 引用方式: `. "E:\devdir\clawd\skills\webhook-notify\webhook-functions.ps1"`

---

## 版本历史

- **v1.0** (2026-03-19): 初始版本，支持钉钉、企业微信、飞书、Slack和自定义HTTP

---

## 技术支持

如有问题或建议，请检查：
1. Webhook URL配置是否正确
2. 网络连接是否正常（防火墙/代理）
3. 消息格式是否符合平台要求
4. 关键字/签名等安全配置是否正确
