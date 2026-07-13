# SidecarOneStep Skill

macOS Sidecar 增强工具 - MCP 集成技能包

## 安装

### 1. 安装 SidecarOneStep 应用

```bash
# 下载最新版本
curl -L -o SidecarOneStep.dmg https://github.com/yi-nology/sidecarOneStep/releases/download/v1.3.9/SidecarOneStep_Installer.dmg

# 安装
hdiutil attach SidecarOneStep.dmg
cp -R /Volumes/SidecarOneStep\ Installer/SidecarOneStep.app /Applications/
```

### 2. 安装 Skill

```bash
clawhub install sidecar-onestep
```

### 3. 启用 MCP

1. 打开 SidecarOneStep
2. 进入"设置" → "开发/集成"
3. 启用"MCP (stdio)"

## 功能

- 📱 列出可用 iPad 设备
- 🔗 连接/断开设备（支持有线/无线）
- 📊 查询连接状态
- 🌐 启动/停止 HTTP 控制服务器
- 📝 查看服务器日志
- 🔄 异步任务管理

## 使用

查看完整的 SKILL.md 文档获取详细使用说明。

## 许可证

MIT License
