---
name: amemo-save-mate
description: 当用户说「永久记住XXX」「记住这个」「保存永久记忆」时调用，将记忆内容追加写入本地 MEMORY.md 并同步到云端。
---

# amemo-save-mate — 保存助手记忆

## 接口信息

- **路由**: POST https://skill.amemo.cn/save-mate
- **Bean**: MateBean
- **Content-Type**: application/json

## 请求参数

> **注意**：服务端要求所有字段必须存在。`userToken` 和 `mateMemory` 必填且有值。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| userToken | str | **是** | 用户登录凭证 |
| mateMemory | str | **是** | 要保存的记忆内容（不能为空） |

## 请求示例

```bash
# 保存记忆
curl -X POST https://skill.amemo.cn/save-mate \
  -H "Content-Type: application/json" \
  -d '{"userToken": "<token>", "mateMemory": "用户喜欢 Python，常用 FastAPI 框架"}'
```

## 响应示例

```json
{"code": 200, "desc": "success", "data": "..."}
```

## 注意事项

- `userToken` 和 `mateMemory` 都必须有值，不能为空
- 与 `amemo-init-mate` 不同，此接口用于追加/更新记忆，而非重置
- 必须携带有效的 userToken

## 执行流程（由主模块调度）

### 执行步骤

```
1. 识别触发词（保存永久记忆/永久记住 XXX/记住这个）
    ↓
2. 检查 userToken 是否存在
    ├── 无 token → 引导登录流程
    ↓
3. 提取记忆内容
    ├── 触发词为"永久记住 XXX" → 直接提取 XXX 作为记忆内容
    ├── 触发词为"记住这个" → 提取当前对话中用户最近说的关键信息
    └── 触发词为"保存永久记忆" → 读取 memory/MEMORY.md 文件内容
    ↓
4. 将新记忆内容追加写入 memory/MEMORY.md
    ├── 文件不存在 → 自动创建
    └── 文件存在 → 在文件末尾追加新条目
    ↓
5. 调用 POST /save-mate 接口，传入完整 MEMORY.md 内容
    ↓
6. 返回保存结果
```

### 保存触发场景

**场景一：用户说"永久记住 XXX"（最常见）**
```
用户：永久记住我喜欢喝美式咖啡
    ↓
AI 提取记忆内容：「我喜欢喝美式咖啡」
    ↓
AI 将内容写入 memory/MEMORY.md：
    - 我喜欢喝美式咖啡
    ↓
调用 /save-mate 同步到服务器
    ↓
回复用户：✅ 已记住「我喜欢喝美式咖啡」
```

**场景二：用户说"记住这个"**
```
用户在对话中分享了某个信息后说"记住这个"
    ↓
AI 提取上一条对话中的关键信息作为记忆内容
    ↓
写入 MEMORY.md → 同步到服务器
```

**场景三：用户说"保存永久记忆"**
```
用户：保存永久记忆
    ↓
AI 读取 memory/MEMORY.md 全部内容
    ↓
调用 /save-mate 同步到服务器
```

### 成功提示模板

**"永久记住 XXX" 场景：**
```
✅ 已记住：「{记忆内容}」

已同步到云端，所有设备均可读取。
```

**"保存永久记忆" 场景：**
```
✅ 永久记忆已保存！

已同步 {lines} 行记忆内容到云端，所有设备均可读取。
```

### 失败处理

**MEMORY.md 不存在时：**
```
⚠️ 暂无本地记忆可保存

请先：
1. 使用「刷新助手记忆」获取云端记忆
2. 或直接编辑 memory/MEMORY.md 添加内容

然后再说「保存永久记忆」
```

**读取失败时：**
```
⚠️ 无法读取本地记忆文件

请检查 memory/MEMORY.md 是否存在且可读。
```

**接口调用失败时：**
```
⚠️ 记忆保存失败

错误信息：{error_message}

请检查网络连接后重试。
```
