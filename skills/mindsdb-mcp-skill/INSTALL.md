# MindsDB MCP 安装配置指南

## 前置要求

- Claude Desktop (2024年11月后版本)
- 本地MindsDB实例或MindsDB Cloud账户

## 安装步骤

### 1. 安装MindsDB

MindsDB已内置MCP服务器功能，无需单独安装MCP服务器。

```bash
# 安装MindsDB
pip install mindsdb

# 启动MindsDB
mindsdb
```

### 2. 配置Claude Desktop

根据你的操作系统，找到配置文件：

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### 3. 编辑配置文件

在配置文件中添加MindsDB MCP服务器配置：

```json
{
  "mcpServers": {
    "mindsdb": {
      "type": "url",
      "url": "http://localhost:47334/mcp/sse",
      "name": "mindsdb-mcp",
      "authorization_token": "your-mindsdb-token"
    }
  }
}
```

### 4. 配置参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `url` | MCP服务器地址 | `http://localhost:47334/mcp/sse` 或 `https://cloud.mindsdb.com/mcp/sse` |
| `authorization_token` | 认证令牌（可选） | `your-mindsdb-token` |

### 5. 使用MindsDB Cloud

如果你使用MindsDB Cloud，配置如下：

```json
{
  "mcpServers": {
    "mindsdb": {
      "type": "url",
      "url": "https://cloud.mindsdb.com/mcp/sse?api_key=your-api-key",
      "name": "mindsdb-cloud-mcp"
    }
  }
}
```

## 验证安装

### 1. 重启Claude Desktop

完全关闭并重新启动Claude Desktop应用。

### 2. 检查MCP服务器状态

在Claude Desktop中输入：

```
列出所有可用的MCP工具
```

你应该能看到MindsDB相关的工具。

### 3. 测试连接

```
连接到MindsDB并显示版本信息
```

## 常见安装问题

### 问题1: 找不到配置文件

**解决方案:**
- Windows: 按 `Win + R`，输入 `%APPDATA%\Claude`
- macOS: 打开终端，输入 `open ~/Library/Application\ Support/Claude`
- Linux: 打开终端，输入 `ls ~/.config/Claude`

### 问题2: MCP服务器无法启动

**解决方案:**
1. 检查Node.js版本：`node --version` (需要18+)
2. 重新安装MCP服务器：`npm install -g @mindsdb/mcp-server`
3. 查看错误日志

### 问题3: Claude Desktop无法连接

**解决方案:**
1. 确认配置文件格式正确（JSON格式）
2. 检查路径是否正确
3. 重启Claude Desktop
4. 查看Claude Desktop日志

### 问题4: API密钥无效

**解决方案:**
1. 访问 https://cloud.mindsdb.com 重新生成API密钥
2. 确认API密钥没有过期
3. 检查API密钥权限

## 高级配置

### 自定义端口

```json
{
  "env": {
    "MINDSDB_PORT": "8080"
  }
}
```

### 使用代理

```json
{
  "env": {
    "HTTP_PROXY": "http://proxy.example.com:8080",
    "HTTPS_PROXY": "http://proxy.example.com:8080"
  }
}
```

### 启用调试模式

```json
{
  "env": {
    "DEBUG": "mindsdb:*"
  }
}
```

## 卸载

### 卸载MCP服务器

```bash
npm uninstall -g @mindsdb/mcp-server
```

### 移除配置

从 `claude_desktop_config.json` 中删除MindsDB配置。

## 更新

```bash
npm update -g @mindsdb/mcp-server
```

## 获取帮助

- MindsDB文档: https://docs.mindsdb.com
- MCP协议: https://modelcontextprotocol.io
- GitHub Issues: https://github.com/mindsdb/mcp-server/issues
