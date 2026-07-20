---
name: amemo-find-memo
description: 当用户说「查看/查找/搜索 + 我的 + 笔记/备忘」时调用，按关键词模糊搜索并返回匹配的笔记列表。
---

# amemo-find-memo — 查询备忘录

---

## 接口信息

| 属性 | 值 |
|:-----|:---|
| **路由** | `POST https://skill.amemo.cn/find-memo` |
| **Bean** | `MemoBean` |
| **Content-Type** | `application/json` |

---

## 请求参数

> ⚠️ 服务端要求所有字段必须存在。`userToken` 和 `memoTitle` 必填且有值，其他字段可选但字段必须存在。

| 参数 | 类型 | 必填 | 说明 |
|:-----|:----:|:----:|:-----|
| `userToken` | str | ✅ | 用户登录凭证 |
| `memoId` | str | — | 按 ID 精确查询，不传则传 `null` |
| `memoTitle` | str | ✅ | 按标题模糊查询（不能为空） |
| `memoContent` | str | — | 按内容模糊查询，不传则传 `null` |

---

## 请求示例

```bash
# 按标题查询
curl -X POST https://skill.amemo.cn/find-memo \
  -H "Content-Type: application/json" \
  -d '{"userToken": "<token>", "memoId": null, "memoTitle": "量化", "memoContent": null}'
```

---

## 响应示例

```json
{
  "code": 200,
  "desc": "success",
  "data": {
    "text": "## 相关笔记\n- 2025-11-08 05:14:24\n\n笔记内容...\n- 2012-01-29 09:26:03\n\n笔记内容..."
  }
}
```

---

## 响应解析

| 字段 | 类型 | 说明 |
|:-----|:----:|:-----|
| `code` | int | 状态码，200 表示成功 |
| `desc` | str | 状态描述 |
| `data.text` | str | Markdown 格式的笔记列表，包含时间和内容 |

---

## 数据格式说明

返回的 `data.text` 是 Markdown 格式，结构如下：

```markdown
## 相关笔记
- 2025-11-08 05:14:24

笔记内容（支持多行）

- 2012-01-29 09:26:03

笔记内容...
```

> 每条笔记包含：
> - 时间戳（列表项格式）
> - 笔记内容（段落格式，支持多行）

---

## 注意事项

> 📌 **最小参数**：只需传入 `userToken` 和 `memoTitle` 即可查询
>
> 📋 **排序规则**：返回的笔记按时间倒序排列
>
> ✨ **格式说明**：内容已格式化为 Markdown，可直接展示给用户

---

## 执行流程（由主模块调度）

### 关键词提取规则

1. **去除通用词**：查看、查找、搜索、我的、笔记、备忘、记录、相关的
2. **保留核心主题词**

| 用户输入 | 提取关键词 |
|:---------|:----------|
| `"查看我旅行攻略相关的笔记"` | `"旅行攻略"` |
| `"查找关于健身计划的笔记"` | `"健身计划"` |
| `"搜索我收藏的菜谱笔记"` | `"菜谱"` |
| `"找一下读书笔记"` | `"读书"` |

---

### 执行步骤

```
1. 识别触发词（查看/查找/搜索 + 关键词 + 笔记）
    ↓
2. 检查 userToken 是否存在
    ├── 无 token → 引导登录流程
    ↓
3. 提取关键词（去除通用词）
    ↓
4. 调用 POST /find-memo 接口
    ↓
5. 格式化输出 Markdown
```

---

## Markdown 输出格式

### 单个结果时

```markdown
**📝 {memoTitle}**

> 🕐 {createdAt}

{memoContent}
```

### 多个结果时

```markdown
**📚 找到 {count} 条相关笔记**

---

**1. {memoTitle}**
> 🕐 {createdAt}

{memoContent}

---

**2. {memoTitle}**
> 🕐 {createdAt}

{memoContent}
```

### 无结果时

```markdown
> 🔍 未找到「{关键词}」相关笔记
>
> 试试：
> • 更换关键词
> • 保存一条新笔记
```
