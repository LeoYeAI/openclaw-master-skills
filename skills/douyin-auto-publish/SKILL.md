---
name: douyin-upload
description: 抖音创作者平台视频上传发布。触发条件：用户要求上传视频到抖音、发布抖音视频、自动上传视频到抖音创作者平台
---

# douyin-upload

使用 OpenClaw Browser 工具自动上传视频到抖音创作者平台。

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

## 前置要求

- OpenClaw Gateway 已运行
- 电脑已安装 Chrome 浏览器
- **首次使用需要在弹出的浏览器窗口中登录抖音账号**（只需一次，之后自动复用登录态）

## 核心原则

**⚠️ 安全说明：**

本 skill 使用独立的命名 profile（`douyin-profile`），与你的真实 Chrome 浏览器完全隔离。只需在首次使用时登录抖音一次，之后登录态自动复用。AI 不会访问你的真实 Chrome 数据。

**配置选项：**

- ✅ `profile="douyin-profile"` + `target="host"` - 使用独立的命名 profile，登录态持久化，与 Chrome 隔离（推荐）
- ✅ `target="sandbox"` - 独立沙盒环境，每次需要重新登录，最安全但不便捷
- ❌ `profile="user"` - 直接附加到真实 Chrome，会继承所有 cookies 和登录态，不推荐
- ❌ 不填 profile - 使用默认隔离浏览器，行为可能不稳定

**推荐配置：使用 `profile="douyin-profile"` 配合 `target="host"`。**

## 工作流程

### Step 1: 打开上传页面

```javascript
browser(action="navigate", target="host", profile="douyin-profile", url="https://creator.douyin.com/creator-micro/content/upload")
```

### Step 2: 关闭弹窗

如果页面出现弹窗，先关闭：

```javascript
// 1. 获取当前页面所有可交互元素
browser(action="snapshot", target="host", profile="douyin-profile", compact=true, depth=2)

// 2. 在返回结果中查找包含或匹配"我知道了"的按钮，拿到其 ref
// 3. 点击该按钮
browser(action="act", target="host", profile="douyin-profile", request={"kind": "click", "ref": "<找到的ref>"})
```

**关键：不要硬编码 ref！** 先 snapshot，再从结果中根据文字内容找到对应元素的 ref。

### Step 4: 准备视频文件

浏览器 tool 只能上传到 `/tmp/openclaw/uploads` 目录：

```bash
mkdir -p /tmp/openclaw/uploads
cp <视频路径> /tmp/openclaw/uploads/
```

### Step 5: 点击上传按钮

```javascript
// 1. 获取上传页面的元素列表
browser(action="snapshot", target="host", profile="douyin-profile", compact=true, depth=2)

// 2. 查找包含或匹配"上传视频"文字的按钮，拿到 ref
// 3. 点击上传按钮
browser(action="act", target="host", profile="douyin-profile", request={"kind": "click", "ref": "<找到的ref>"})
```

### Step 6: 上传文件

点击上传按钮后会弹出文件选择框：

```javascript
// 1. 先 snapshot 找到 Choose File 或文件输入/上传框的 ref
browser(action="snapshot", target="host", profile="douyin-profile", compact=true, depth=2)

// 2. 上传文件
browser(action="upload", target="host", profile="douyin-profile", paths=["/tmp/openclaw/uploads/<文件名>"], ref="<找到的ref>")
```

### Step 7: 等待视频解析

页面自动跳转到发布编辑页，显示进度条"0% 文件解析中，请稍等..."，等待视频解析完成后继续。

### Step 8: 填写标题

```javascript
// 1. 获取当前页面元素
browser(action="snapshot", target="host", profile="douyin-profile", compact=true, depth=2)

// 2. 查找标题输入框（placeholder 包含或匹配"标题"或"输入标题"的输入框）
// 3. 点击输入框并输入标题
browser(action="act", target="host", profile="douyin-profile", request={"kind": "click", "ref": "<找到的ref>"})
browser(action="act", target="host", profile="douyin-profile", request={"kind": "type", "ref": "<找到的ref>", "text": "<用户提供的标题>"})
```

### Step 9: 设置作品权限

```bash
# 读取已保存的可见范围偏好
cat ~/.openclaw/skills/douyin-auto-publish/config.json
```

**如果 `default_visibility` 字段已存在，使用保存的值。**

**如果 `default_visibility` 字段不存在**，向用户询问：

```
「请选择默认的可见范围：
 - 公开：所有用户可见
 - 好友可见：仅好友可见
 - 仅自己可见：仅自己可见（最安全）
 请回复您希望的数字或文字。」
```

**根据用户回复保存偏好**：
```bash
# 读取现有配置
current=$(cat ~/.openclaw/skills/douyin-auto-publish/config.json)

# 用户选择"公开"
echo $current | jq -s '.[0] * {"default_visibility":"public"}' > ~/.openclaw/skills/douyin-auto-publish/config.json

# 用户选择"好友可见"
echo $current | jq -s '.[0] * {"default_visibility":"friends"}' > ~/.openclaw/skills/douyin-auto-publish/config.json

# 用户选择"仅自己可见"
echo $current | jq -s '.[0] * {"default_visibility":"private"}' > ~/.openclaw/skills/douyin-auto-publish/config.json
```

**如果 jq 不可用**，可以使用简单覆盖：
```bash
# 用户选择"公开"
echo '{"default_visibility":"public"}' > ~/.openclaw/skills/douyin-auto-publish/config.json
```

**如果用户明确指定了可见范围**，优先使用用户指定的值（而不是默认值），本次不修改保存的偏好。

```javascript
// 1. 获取当前页面元素
browser(action="snapshot", target="host", profile="douyin-profile", compact=true, depth=2)

// 2. 查找包含或匹配用户指定可见范围（或默认偏好）的单选框
//    - public/公开："公开"
//    - friends/好友可见："好友可见"
//    - private/仅自己可见："仅自己可见"
// 3. 点击选中
browser(action="act", target="host", profile="douyin-profile", request={"kind": "click", "ref": "<找到的ref>"})
```

### Step 10: 确认并发布

**每次发布前必须向用户展示视频信息并获得明确确认，不支持跳过确认。**

在点击发布之前，必须向用户展示以下信息并获得明确确认：

```javascript
// 1. 获取当前页面元素（用于后续发布）
browser(action="snapshot", target="host", profile="douyin-profile", compact=true, depth=2)

// 2. 向用户确认以下信息：
//    - 文件名: <视频文件名>
//    - 标题: <用户提供的标题>
//    - 可见范围: <公开/仅自己可见/好友可见>
//    示例：「确认发布以下视频？
//         文件名: demo.mp4
//         标题: 我的视频标题
//         可见范围: 公开
//         请回复「是」确认发布，或「取消」中止操作。」

// 3. 只有在用户明确回复"是"、"确认"、"发布"等肯定回复后，才执行发布
//    如果用户回复"取消"或其他否定内容，告知用户发布已取消并停止操作

// 4. 确认后，点击发布按钮
browser(action="act", target="host", profile="douyin-profile", request={"kind": "click", "ref": "<找到的ref>"})
```

成功标志：页面显示「共 X 个作品」「已发布」状态。

## 完整流程模板

```javascript
// 1. 打开上传页面
browser(action="navigate", target="host", profile="douyin-profile", url="https://creator.douyin.com/creator-micro/content/upload")

// 2. 关闭弹窗
browser(action="snapshot", target="host", profile="douyin-profile", compact=true, depth=2)
// → 从结果中找"我知道了"按钮的 ref，然后点击

// 3. 准备视频文件（需在 terminal 执行）
// mkdir -p /tmp/openclaw/uploads && cp <path> /tmp/openclaw/uploads/

// 4. 点击上传按钮
browser(action="snapshot", target="host", profile="douyin-profile", compact=true, depth=2)
// → 从结果中找"上传视频"按钮的 ref，然后点击

// 5. 上传文件
browser(action="snapshot", target="host", profile="douyin-profile", compact=true, depth=2)
// → 从结果中找文件输入框的 ref，然后上传
browser(action="upload", target="host", profile="douyin-profile", paths=["/tmp/openclaw/uploads/<文件名>"], ref="<ref>")

// 6. 等待解析后填写标题
sleep 15
browser(action="snapshot", target="host", profile="douyin-profile", compact=true, depth=2)
// → 从结果中找标题输入框的 ref，然后点击并输入

// 7. 设置可见范围
// → 读取 config.json 检查 default_visibility 是否已设置
// → 如果未设置，向用户询问偏好（公开/好友可见/仅自己可见）并保存
// → 根据用户指定或保存的偏好，找到对应的单选框 ref 并点击
browser(action="snapshot", target="host", profile="douyin-profile", compact=true, depth=2)
// → 从结果中找对应可见范围选项的 ref，然后点击

// 8. 确认发布
// → 向用户展示：文件名、标题、可见范围
// → 必须等待用户回复"是"后才继续，否则取消发布

// 9. 点击发布
browser(action="snapshot", target="host", profile="douyin-profile", compact=true, depth=2)
// → 从结果中找"发布"按钮的 ref，然后点击
```

## 重要提示

1. **每次操作前都要先 snapshot** - ref 是动态的，每次快照都不同
2. **从 snapshot 结果中根据文字内容查找 ref** - 不要硬编码
3. **页面跳转后需要重新 snapshot** - 元素 ref 会失效
4. **视频必须复制到 `/tmp/openclaw/uploads/`** - 浏览器 tool 的限制
5. **当用户还需要未提及的操作时, 也是同样的方法匹配对应的ref, 然后找到匹配的选项**

## 可选：使用沙盒模式（更安全）

如果你希望完全隔离登录状态，可以使用 `target="sandbox"`：

```javascript
// 1. 打开上传页面
browser(action="navigate", target="sandbox", url="https://creator.douyin.com/creator-micro/content/upload")

// 2. 沙盒环境没有登录态，首次使用需要通过页面上的二维码登录抖音账号
// 3. 后续每次使用都需要重新登录
```

**沙盒模式的优点：**
- 完全隔离的浏览器环境，不会访问任何已有浏览器数据
- 更安全，适合注重隐私的用户

**沙盒模式的缺点：**
- 每次使用都需要重新登录抖音账号
- 无法复用登录态

## 常见问题

**Q: 为什么提示需要登录？**
A: 首次使用需要在弹出的 douyin-profile 浏览器中登录抖音账号（扫描二维码）。只需登录一次，之后登录态会自动复用。如果想避免登录态持久化，可以使用 `target="sandbox"` 模式。

**Q: douyin-profile 与真实 Chrome 有什么区别？**
A: douyin-profile 是一个独立的命名浏览器 profile，与你的真实 Chrome 浏览器完全隔离。AI 使用这个独立的 profile 进行操作，不会访问你的真实 Chrome 数据、cookies 或登录态。

**Q: 如何使用更安全的沙盒模式？**
A: 使用 `target="sandbox"` 代替 `target="host"`。沙盒模式会创建独立的浏览器环境，不会访问你的真实 Chrome 数据，但每次都需要重新登录抖音账号。

**Q: Element not found 错误？**
A: 页面可能跳转了，需要重新执行 snapshot 获取最新元素。

**Q: 为什么 ref 每次都不一样？**
A: 抖音页面动态渲染，每次 snapshot 生成的 ref 不同。这是正常现象。

