# douyin-upload

自动上传视频到抖音创作者平台。

## ⚠️ 重要声明

**本 Skill 的使用条件：**

1. **主动请求触发**：本 Skill 只会在用户主动请求的情况下才会使用，例如：
   - 用户直接要求 Agent 使用此 Skill 上传视频
   - 用户在预先配置好的 cron job 中执行此 Skill

2. **需要用户主动提供信息**：使用本 Skill 时，需要用户主动提供以下信息：
   - 视频文件路径（如 `~/Videos/my_video.mp4`）
   - 视频标题（如「汽车保养小技巧」）
   - 作品可见范围（公开/好友可见/仅自己可见）
   - 其他可能需要的信息

3. **强制用户确认**：每次发布前，必须向用户展示视频信息并获得明确确认后才能发布，**不支持跳过确认**。

## 安装 Skill

### 从 ClawHub 安装（推荐）

```bash
# 1. 登录 ClawHub（浏览器认证）
clawhub login

# 2. 安装 skill
openclaw skills install douyin-auto-publish
```

> ClawHub 地址: https://clawhub.com

### 手动安装

```bash
# 将 skill 文件夹复制到 ~/.openclaw/skills/
```

## 准备工作（只需做一次）

### 首次登录抖音

1. 首次使用时会自动弹出 douyin-profile 浏览器窗口
2. 在该窗口中访问 [抖音创作者平台](https://creator.douyin.com/creator-micro/home)
3. 使用抖音账号登录（扫描二维码或账号密码）
4. 建议保持登录状态

**只需登录一次**，之后 AI 会自动复用你的登录状态。

## ⚠️ 安全警告

**使用此 Skill 前请注意：**

1. **独立 Profile**：`profile="douyin-profile"` 使用独立的命名浏览器 profile，与你的真实 Chrome 浏览器完全隔离

2. **强制确认**：每次发布前都会展示视频信息并需要你明确确认，不支持跳过确认。

3. **隔离建议**：如果你对账号安全有较高要求，建议使用 `target="sandbox"` 模式，它会创建完全独立的浏览器环境

## target 参数选择(默认为host)

OpenClaw Browser 工具支持不同的 `target` 参数，适用于不同场景：

| target | 说明 | 适用场景 | 注意事项 |
|--------|------|----------|----------|
| `host` | 控制本地浏览器，配合 profile 使用 | **推荐**：配合 douyin-profile 使用 | 确保使用 `profile="douyin-profile"` |
| `sandbox` | 独立的沙盒浏览器 | 隔离环境、保护隐私 | 无登录态，每次需重新登录 |
| `node` | 控制已连接的节点设备 | 远程控制手机/平板浏览器 | 需要先配对节点 |

### profile 参数（仅 target="host" 时有效）

| profile | 说明 | 适用场景 | 注意事项 |
|---------|------|----------|----------|
| `douyin-profile` | 独立的命名 profile | **推荐**：登录态持久化，与 Chrome 隔离 | 首次使用需登录一次 |
| 不填 | 使用默认隔离浏览器 | 行为可能不稳定 | 需手动登录一次 |
| `user` | 附加到你真实的 Chrome 会话 | 需要使用已保存的 cookies | 不推荐，会继承所有登录态 |

### 推荐配置

**日常使用（推荐）：**
```javascript
browser(action="navigate", target="host", profile="douyin-profile", url="...")
```

**隐私隔离：**
```javascript
browser(action="navigate", target="sandbox", url="...")
```

## 使用方法

告诉 AI：「帮我上传视频到抖音」并提供：

- 视频文件路径
- 视频标题
- 可见范围（公开/好友可见/仅自己可见）

AI 会自动完成全部流程。**在发布前，AI 会要求你确认视频信息，请回复「是」确认发布。**

## 示例

```
用户: 帮我上传 ~/Videos/my_video.mp4 到抖音，标题是「汽车保养小技巧」，公开可见
```

## 工作流程

```
1. 打开抖音上传页面
2. 关闭弹窗（如有）
3. 上传视频文件
4. 填写标题
5. 设置可见范围（首次运行时询问默认偏好，之后使用保存的值）
6. 【确认发布】展示视频信息并等待用户确认"是"
7. 发布
```

## 常见问题

**Q: 为什么提示需要登录？**
A: 首次使用需要在弹出的 douyin-profile 浏览器中登录抖音账号（扫描二维码）。只需登录一次，之后会自动复用。

**Q: 应该用 `target="host"` 还是 `target="sandbox"`？**
A:
- 用 `target="host"`：需要使用已有登录态，AI 使用独立的 douyin-profile 浏览器
- 用 `target="sandbox"`：需要完全隔离环境，每次都需要重新登录

**Q: douyin-profile 与真实 Chrome 有什么区别？**
A:
- douyin-profile：独立的命名 profile，与真实 Chrome 完全隔离，登录态持久化
- `profile="user"`：直接附加到真实 Chrome，会继承所有 cookies 和登录态（不推荐）

**Q: `profile="user"` 和不填 profile 有什么区别？**
A:
- 不填 profile：使用 OpenClaw 的隔离浏览器，需手动登录一次抖音
- `profile="user"`：直接附加到你真实的 Chrome，会继承所有 cookies 和登录态，但需要你在电脑前

**Q: 支持哪些视频格式？**
A: 与抖音网页版支持格式相同，通常为 MP4、MOV 等常见格式。

**Q: 可以设置定时发布吗？**
A: 目前仅支持立即发布。

**Q: 可以关闭发布前确认吗？**
A: 不可以。为了保障账号安全，每次发布前都会展示视频信息并需要您明确确认，不支持跳过确认。

**Q: 如何修改默认的可见范围？**
A: 首次运行时会询问您默认的可见范围偏好。如需修改，可删除 `~/.openclaw/skills/douyin-auto-publish/config.json` 文件，重新运行时会再次询问。

## 相关链接

- [OpenClaw 文档](https://docs.openclaw.ai)
- [抖音创作者平台](https://creator.douyin.com/creator-micro/home)
