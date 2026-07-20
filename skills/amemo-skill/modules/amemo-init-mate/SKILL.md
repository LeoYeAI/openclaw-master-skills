---
name: amemo-init-mate
description: 当用户说「刷新助手记忆」「初始化助手记忆」「重置记忆」时调用，从云端拉取最新记忆内容并写入本地 memory/MEMORY.md。
---

# amemo-init-mate — 初始化 AI 助手

## 接口信息

- **路由**: POST https://skill.amemo.cn/init-mate
- **Bean**: MateBean
- **Content-Type**: application/json

## 请求参数

> **注意**：服务端要求所有字段必须存在。`userToken` 必填，`mateMemory` 可选但字段必须存在（可传 `null`）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| userToken | str | **是** | 用户登录凭证（通过 amemo-login 获取） |
| mateMemory | str | 否 | 初始记忆内容，不传则传 `null` |

## 请求示例

```bash
# 初始化（不传记忆内容）
curl -X POST https://skill.amemo.cn/init-mate \
  -H "Content-Type: application/json" \
  -d '{"userToken": "<token>", "mateMemory": null}'

# 初始化并设置记忆
curl -X POST https://skill.amemo.cn/init-mate \
  -H "Content-Type: application/json" \
  -d '{"userToken": "<token>", "mateMemory": "用户偏好：喜欢简洁风格"}'
```

## 响应示例

```json
{"code": 200, "desc": "success", "data": "..."}
```

## 注意事项

- 所有字段必须存在，即使不传值也要传 `null`
- 必须先通过 `amemo-login` 获取 userToken
- `mateMemory` 为可选，用于设定助手初始记忆

## 执行流程（由主模块调度）

### 执行步骤

```
1. 识别触发词（刷新/初始化/重置 + 助手记忆）
    ↓
2. 检查 userToken 是否存在
    ├── 无 token → 引导登录流程
    ↓
3. 检查 memory 目录是否存在
    ├── 不存在 → 自动创建 memory 目录
    ↓
4. 调用 POST /init-mate 接口
    ↓
5. 解析响应
    └── data.mateMemory: AI 助手记忆内容（Markdown 格式）
    ↓
6. 更新本地 MEMORY.md
    ├── 如果 memory 目录不存在 → 先创建
    ├── 写入 mateMemory 内容到 memory/MEMORY.md
    ↓
7. 返回结果给用户
```

### 更新 MEMORY.md 模板

将 `mateMemory` 内容完整写入 `memory/MEMORY.md`：

```markdown
{mateMemory}
```

### 成功提示模板

```
✅ 助手记忆已刷新！

已同步 {count} 条记忆信息到本地 MEMORY.md

记忆内容包括：
• 用户偏好设置
• 工作习惯和规律
• 常用工具和技术栈
• 个人目标和关注点

现在 AI 助手将根据您的记忆提供更个性化的服务。
```

### 失败处理

**文件写入失败时：**
```
⚠️ 记忆同步失败：无法写入 MEMORY.md 文件

可能原因：
• 目录权限不足
• 磁盘空间已满

请检查后重试，或联系管理员。
```

**接口调用失败时：**
```
⚠️ 无法获取助手记忆，请检查：
• amemo 服务是否正常运行
• 网络连接是否正常

错误信息：{error_message}
```
