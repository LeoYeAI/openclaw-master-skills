# ClawHub 发布指南

## Skill 包已准备完成

**位置**: `~/.openclaw/workspace/skills/sidecar-onestep-clawhub/`

**包含文件:**
```
sidecar-onestep-clawhub/
├── SKILL.md         # 主技能文件（中英文双语）
├── README.md        # 安装说明
├── package.json     # 元数据
├── assets/          # 资源文件目录
└── templates/       # 模板目录
```

## 发布到 ClawHub

### 1. 登录 ClawHub

```bash
clawhub login
```

按照提示完成登录（需要浏览器授权）。

### 2. 验证登录状态

```bash
clawhub whoami
```

### 3. 发布 Skill

```bash
cd ~/.openclaw/workspace/skills/sidecar-onestep-clawhub

clawhub publish . \
  --slug sidecar-onestep \
  --name "SidecarOneStep" \
  --version 1.3.9 \
  --changelog "Initial release with MCP integration, async connection support, 10 tools for Sidecar management" \
  --tags latest,stable
```

### 4. 验证发布

```bash
# 搜索 skill
clawhub search sidecar

# 查看 skill 详情
clawhub info sidecar-onestep
```

## Skill 特性

### 核心功能
- 📱 **设备管理** - 列出、连接、断开 iPad 设备
- 🔗 **连接模式** - 支持有线/无线连接
- 🌐 **HTTP 服务器** - Web 控制台
- 📊 **状态监控** - 实时连接状态
- 📝 **日志查看** - 调试和故障排查
- 🔄 **异步任务** - 非阻塞操作

### MCP 工具 (10 个)
1. `list_devices` - 列出可用设备
2. `connect_device` - 同步连接
3. `connect_device_async` - 异步连接（推荐）
4. `get_job_status` - 查询任务状态
5. `cancel_job` - 取消任务
6. `disconnect_device` - 断开设备
7. `start_http_server` - 启动 HTTP 服务器
8. `stop_http_server` - 停止 HTTP 服务器
9. `get_status` - 获取状态
10. `get_logs` - 查看日志

### 依赖
- **应用**: SidecarOneStep.app
- **CLI**: mcporter (MCP 客户端)
- **平台**: macOS 11.0+

## 用户安装流程

### 1. 安装应用
```bash
# 下载
curl -L -o SidecarOneStep.dmg https://github.com/yi-nology/sidecarOneStep/releases/download/v1.3.9/SidecarOneStep_Installer.dmg

# 安装
hdiutil attach SidecarOneStep.dmg
cp -R /Volumes/SidecarOneStep\ Installer/SidecarOneStep.app /Applications/
```

### 2. 安装 Skill
```bash
clawhub install sidecar-onestep
```

### 3. 配置 MCP
```bash
mcporter config add sidecar-onestep \
  --command /Applications/SidecarOneStep.app/Contents/MacOS/SidecarOneStep \
  --args mcp
```

## 版本信息

- **Skill Version**: 1.3.9
- **App Version**: 1.3.9 (Build 29)
- **Release Date**: 2026-03-10
- **Author**: MurphyYi
- **License**: MIT

## 相关链接

- 🏠 官网: https://sidecaronestep.app.murphyyi.com/
- 🐙 GitHub: https://github.com/yi-nology/sidecarOneStep
- 📦 下载: https://github.com/yi-nology/sidecarOneStep/releases/latest

---

**准备就绪！** 运行上面的 `clawhub publish` 命令即可发布到 ClawHub。
