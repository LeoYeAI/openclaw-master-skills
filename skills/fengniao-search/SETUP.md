# 风鸟企业查询 Skill 本地验证说明

## 适用范围

本文只用于本地验证当前 skill，不要求修改用户主目录、shell 启动文件或 agent 全局配置。

## 前置条件

- Node.js 18 或以上版本
- 一个可用的 `FN_API_KEY`

验证 Node.js 版本：

```bash
node -v
```

## 获取 API Key

请访问静态页面 `https://www.riskbird.com/skills` 获取公用 API Key。

- 进入页面后，在页面中部找到“公用 API Key”展示区，点击区块内的复制按钮
- 复制当前页面展示的可用 Key
- 公用 Key 与额度说明以页面当前展示为准
- 左上角“美亚风鸟” Logo 可点击跳转风鸟官网

## 临时设置 API Key

只在当前终端会话中设置，关闭终端后失效。

**macOS / Linux**

```bash
export FN_API_KEY="你的API Key"
```

**Windows PowerShell**

```powershell
$env:FN_API_KEY = "你的API Key"
```

**Windows CMD**

```cmd
set FN_API_KEY=你的API Key
```

## 校验环境变量

建议在调用查询前先确认当前会话已经能读到 `FN_API_KEY`。

**macOS / Linux**

```bash
printenv FN_API_KEY
```

**Windows PowerShell**

```powershell
$env:FN_API_KEY
```

也可以使用更显式的写法：

```powershell
Get-Item Env:FN_API_KEY -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Value
```

如果你是在另一个 PowerShell 进程里执行校验命令，优先使用单引号包裹命令，避免外层 shell 提前展开变量：

```powershell
powershell -Command '$env:FN_API_KEY'
```

不要把下面这类命令的报错直接当成“环境变量未配置”的证据：

```powershell
powershell -Command "echo $env:FN_API_KEY"
```

原因是外层 shell 可能先展开 `$env:FN_API_KEY`；当它为空时，传给内层 PowerShell 的就只剩 `echo`，从而触发 `Write-Output` 缺少 `InputObject` 的误报。

## 本地验证命令

```bash
# 1. 测试工具发现（无需联网）
node scripts/tool.mjs discover "企业基本信息"

# 2. 测试模糊搜索（需要有效 API Key）
node scripts/tool.mjs call biz_fuzzy_search --params '{"key":"腾讯"}'

# 3. 测试维度查询（用上一步返回的 entid）
node scripts/tool.mjs call biz_basic_info --params '{"entid":"AerjZTfkSh0"}'
```

## 当前发布包的安全边界

- 只从环境变量 `FN_API_KEY` 读取凭证
- 只读取 skill 包内的 `tools.json` 和 `references/` 文件
- 不读取用户主目录中的 agent 配置或 shell 启动配置
- 不写入本地文件
- API 凭证通过 HTTP 请求头发送，不放入 URL 参数

## 生产环境说明

公开发布包固定使用测试地址 `https://test.riskbird.com/test-qbb-api`。

如果你有自有付费账号并需要切换生产地址，请在私有 fork 中审阅并修改源码后自行使用，不建议在公开市场包中暴露可切换端点。
