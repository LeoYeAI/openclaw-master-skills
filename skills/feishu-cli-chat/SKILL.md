---
name: feishu-cli-chat
description: >-
  飞书会话浏览、消息互动与群聊管理。查看聊天记录、获取群聊历史消息、搜索群聊、
  获取消息详情、Reaction 表情回应、Pin 置顶/取消置顶、删除消息、
  群聊信息查询与管理（获取/更新/解散/成员管理）。
  支持普通群和话题群两种模式，话题群自动获取线程回复。所有命令需要 User Token。
  当用户请求"查看聊天记录"、"看和某人的消息"、"群聊历史"、"群消息"、"搜索群聊"、
  "查群信息"、"群成员"、"最近消息"、"聊天记录"、"Reaction"、"表情回应"、
  "置顶消息"、"Pin"、"删除消息"、"获取消息"、"消息详情"、
  "和谁聊了什么"、"群里说了什么"、"总结群消息"、"话题回复"、"线程回复"、
  "thread replies"时使用。
  也适用于：用户给出一个群聊名称或 chat_id 并希望浏览其消息的场景，
  即使没有明确说"聊天记录"。当用户想了解某个群最近在讨论什么、
  想找和某人的对话内容、或想对消息进行互动操作时，都应使用此技能。
argument-hint: <chat_id|群名|用户名>
user-invocable: true
allowed-tools: Bash, Read, Write
---

# 飞书会话浏览与管理

通过 feishu-cli 浏览飞书单聊/群聊消息历史、搜索会话、管理群聊信息和成员。

## 前置条件

本技能的核心命令**必须使用 User Token**，使用前需先登录。`chat create`、`chat link`、`msg read-users` 使用 App Token，属于 feishu-cli-toolkit 技能。

```bash
feishu-cli auth login
```

未登录时命令会直接报错并提示登录方式。登录后 token 自动加载，无需手动传参。

### 身份说明

| 身份 | 使用场景 |
|------|---------|
| **User Token**（必须） | 本技能所有读取/管理命令：chat get/update/delete、member list/add/remove、msg get/history/list/pins/reaction/search-chats、search messages |
| **App Token** | 仅 `chat create`、`chat link`、`msg read-users`（这三个命令不属于本技能核心流程） |

User Token 能力：
- 查看 bot 不在的群聊消息
- 查看私聊（p2p）消息
- 搜索用户有权限的所有会话

### 自动降级机制

当使用 User Token 调用 `msg history` / `msg list` 时，如果 bot 不在目标群中，API 会返回空结果。CLI 会自动检测这种情况并降级为 **search + get** 方式获取消息：

```
list API 返回空 + has_more=true → 自动切换到搜索模式 → 逐条获取消息内容
```

这个过程对用户透明，无需手动干预。

---

## 场景一：查看群聊历史消息

这是最常见的场景——用户想看某个群最近在聊什么。

### 步骤 1：找到群聊

如果用户给了群名而不是 chat_id，先搜索：

```bash
feishu-cli msg search-chats --query "群名关键词" -o json
```

输出中的 `chat_id`（形如 `oc_xxx`）就是后续命令需要的标识。

### 步骤 2：获取消息

```bash
# 获取最近 50 条消息（API 单次上限 50）
feishu-cli msg history \
  --container-id oc_xxx \
  --container-id-type chat \
  --page-size 50 \
  --sort-type ByCreateTimeDesc \
  -o json

# 按时间范围获取（--start-time 为毫秒级时间戳，仅返回该时间之后的消息）
feishu-cli msg history \
  --container-id oc_xxx \
  --container-id-type chat \
  --page-size 50 \
  --start-time 1773778860000 \
  --sort-type ByCreateTimeDesc \
  -o json

# 获取更早的消息（使用上一次返回的 page_token 翻页）
feishu-cli msg history \
  --container-id oc_xxx \
  --container-id-type chat \
  --page-size 50 \
  --page-token "上一页返回的token" \
  -o json
```

### 步骤 2.5：判断群类型并获取线程回复

飞书群聊分为**普通群**和**话题群**两种，消息结构和获取策略完全不同。

#### 如何判断群类型

观察 `msg history` 返回的消息字段：

| 群类型 | 特征 | 示例 |
|--------|------|------|
| **话题群** | **每条**消息都有 `thread_id`（形如 `omt_xxx`），主消息流仅包含每个话题的首条消息 | 泰国华商群 |
| **普通群** | 独立消息**无** `thread_id`，仅被回复的消息和回复消息才有 `thread_id` | Claude Code闲聊群 |

#### 消息中的线程相关字段

| 字段 | 说明 | 出现条件 |
|------|------|---------|
| `thread_id` | 线程/话题 ID（形如 `omt_xxx`） | 话题群所有消息 / 普通群中参与线程的消息 |
| `root_id` | 线程根消息 ID（即话题首条消息） | 线程回复消息 |
| `parent_id` | 直接上级消息 ID（被回复的那条消息） | 线程回复消息 |

#### 普通群：一次获取全部消息

普通群的 `msg history` 返回**所有消息**（独立消息 + 线程回复），平铺在同一列表中。通过 `root_id`/`parent_id` 可重建回复关系，**不需要**额外获取线程。

```
独立消息:       无 thread_id、无 root_id
被回复的消息:   有 thread_id（被回复后自动产生）
线程回复:       有 thread_id + root_id + parent_id
```

#### 话题群：需要逐个话题获取回复（重要）

话题群的 `msg history --container-id-type chat` **仅返回每个话题的首条消息**，线程回复不在主消息流中。必须按 thread_id 逐个获取：

```bash
# 获取单个话题的所有回复（按时间正序，方便阅读）
feishu-cli msg history \
  --container-id omt_xxx \
  --container-id-type thread \
  --page-size 50 \
  --sort-type ByCreateTimeAsc \
  -o json
```

**完整的话题群获取流程**：

```bash
# 1. 获取主消息流（每个话题的首条消息）
feishu-cli msg history \
  --container-id oc_xxx \
  --container-id-type chat \
  --page-size 50 \
  --sort-type ByCreateTimeDesc \
  -o json

# 2. 从返回结果中提取所有 thread_id

# 3. 对每个 thread_id 获取回复（可并发执行，提高效率）
feishu-cli msg history --container-id omt_xxx --container-id-type thread --page-size 50 --sort-type ByCreateTimeAsc -o json
feishu-cli msg history --container-id omt_yyy --container-id-type thread --page-size 50 --sort-type ByCreateTimeAsc -o json
# ... 多个话题可并行获取
```

> **性能提示**：话题群中活跃话题可能有 10-20 个，建议**并发获取**多个话题的回复。飞书 API 对 `msg history` 无严格 QPS 限制（不同于搜索 API），可以安全并发。

### 步骤 3：解析消息内容

API 返回的消息 body.content 是 JSON 字符串，常见格式：

| msg_type | content 格式 | 说明 |
|----------|-------------|------|
| text | `{"text":"消息内容"}` | 纯文本，`@_user_1` 是 at 占位符 |
| post | 富文本 JSON | 包含标题和段落结构 |
| image | `{"image_key":"xxx"}` | 图片 |
| interactive | 卡片 JSON | 交互式卡片 |
| share_calendar_event | `{"summary":"会议名","start_time":"ms","end_time":"ms",...}` | 日历事件分享 |
| sticker | `{"sticker_key":"xxx"}` | 表情包 |
| file | `{"file_key":"xxx","file_name":"..."}` | 文件 |

用 Python 提取文本内容的常用方式：

```python
import json
content = json.loads(msg['body']['content'])
text = content.get('text', '')
```

### 完整示例：获取并总结群聊最近 N 条消息

```bash
# 1. 搜索群聊
feishu-cli msg search-chats --query "Go讨论区" -o json

# 2. 获取消息（循环翻页直到够数）
feishu-cli msg history \
  --container-id oc_xxx \
  --container-id-type chat \
  --page-size 50 \
  --sort-type ByCreateTimeDesc \
  -o json > /tmp/chat_page1.json

# 3. 提取 page_token 获取下一页
# ... 循环直到获取足够消息
```

> **注意**：Search API 的 page_size 与 List API 不同，降级模式下每页实际返回数量可能少于请求值。建议循环翻页直到 `has_more=false` 或达到目标数量。

---

## 场景二：查看和某人的私聊记录

飞书 Open API **不支持直接按用户查询 p2p 聊天记录**。需要通过搜索 API 间接实现。

### 方法：搜索 + 筛选

```bash
# 搜索私聊消息
feishu-cli search messages "关键词" \
  --chat-type p2p_chat \
  -o json

# 如果知道对方的 open_id，可以按发送者筛选
feishu-cli search messages "关键词" \
  --chat-type p2p_chat \
  --from-ids ou_xxx \
  -o json

# 获取单条消息详情
feishu-cli msg get om_xxx -o json
```

### 查找用户 ID

如果用户只给了邮箱或手机号，可以查找对应的 open_id：

```bash
# 通过邮箱查找用户
feishu-cli user search --email user@example.com -o json

# 通过手机号查找用户
feishu-cli user search --mobile 13800138000 -o json
```

> **注意**：`user search` 仅支持 `--email` 和 `--mobile` 精确查找，不支持按姓名模糊搜索。

### 限制说明

- 搜索 API 的 `query` 参数**不能为空**，至少需要一个空格 `" "`
- p2p 聊天无法通过 `msg search-chats` 搜索（该 API 只搜索群聊）
- 搜索结果返回的是消息 ID 列表，需要逐条 `msg get` 获取完整内容
- **`msg get` 对私聊消息可能返回 230001 错误**（API 限制：部分私聊消息不支持通过 Get API 获取详情），此时只能依赖搜索结果中的摘要信息

---

## 场景三：搜索群聊

### 搜索群聊列表

```bash
# 按关键词搜索群聊
feishu-cli msg search-chats --query "关键词" -o json

# 分页获取所有群
feishu-cli msg search-chats --page-size 100 -o json
```

### 在群内搜索消息

```bash
# 在指定群中搜索消息
feishu-cli search messages "关键词" --chat-ids oc_xxx -o json
```

> **更多搜索功能**（按时间范围、消息类型、发送者、跨模块搜索文档/应用等）请使用 **feishu-cli-search** 技能，提供完整的筛选参数和 Token 排错指南。

---

## 场景四：群聊信息管理

### 查看群信息

```bash
feishu-cli chat get oc_xxx
```

默认输出 JSON 格式，包含群名、描述、群主、群类型、成员数量等。

### 查看群成员

```bash
# 获取成员列表
feishu-cli chat member list oc_xxx

# 指定 ID 类型
feishu-cli chat member list oc_xxx --member-id-type user_id

# 分页获取（大群）
feishu-cli chat member list oc_xxx --page-size 100 --page-token "xxx"
```

> **Scope 要求**：使用 User Token 时需要 `im:chat:readonly` 或 `im:chat.members:read` scope。若报 99991679 错误，需通过 `auth login --scopes "... im:chat:readonly"` 重新授权。

### 修改群信息

```bash
# 改群名
feishu-cli chat update oc_xxx --name "新群名"

# 改群描述
feishu-cli chat update oc_xxx --description "新的群描述"

# 转让群主
feishu-cli chat update oc_xxx --owner-id ou_xxx
```

### 群成员管理

```bash
# 添加成员
feishu-cli chat member add oc_xxx --id-list ou_xxx,ou_yyy

# 移除成员
feishu-cli chat member remove oc_xxx --id-list ou_xxx

# 使用 user_id 类型
feishu-cli chat member add oc_xxx --id-list user_xxx --member-id-type user_id
```

### 创建群聊

```bash
feishu-cli chat create --name "新群聊" --user-ids ou_xxx,ou_yyy
```

> **注意**：`chat create` 和 `chat link`（获取分享链接）仅支持 App Token（租户身份），不支持 User Token。

### 解散群聊

```bash
feishu-cli chat delete oc_xxx
# 会要求确认，不可逆操作
```

---

## 场景五：消息详情与互动

### 获取单条消息详情

```bash
feishu-cli msg get om_xxx -o json
```

### 查看消息已读情况

```bash
feishu-cli msg read-users om_xxx -o json
```

> **限制**：仅支持查询 bot 自己发送的、7 天内的消息，且 bot 必须在会话内。此命令仅使用 App Token。

### 查看群内置顶消息

```bash
feishu-cli msg pins --chat-id oc_xxx -o json
```

### 置顶/取消置顶消息

```bash
# 置顶消息
feishu-cli msg pin <message_id>

# 取消置顶
feishu-cli msg unpin <message_id>
```

### Reaction 表情回应

```bash
# 添加表情
feishu-cli msg reaction add <message_id> --emoji-type THUMBSUP

# 删除表情
feishu-cli msg reaction remove <message_id> --reaction-id <REACTION_ID>

# 查询表情列表
feishu-cli msg reaction list <message_id> [--emoji-type THUMBSUP] [--page-size 20]
```

常用 emoji-type：`THUMBSUP`（点赞）、`SMILE`（微笑）、`LAUGH`（大笑）、`HEART`（爱心）、`JIAYI`（加一）、`OK`、`FIRE`

### 删除消息

仅能删除机器人自己发送的消息，不可恢复。

```bash
feishu-cli msg delete <message_id>
```

---

## 常见操作速查表

| 用户意图 | 命令 | Token |
|---------|------|:---:|
| 看某群最近消息 | `msg history --container-id oc_xxx --container-id-type chat` | User |
| 看话题群的线程回复 | `msg history --container-id omt_xxx --container-id-type thread` | User |
| 看和某人的聊天 | `search messages " " --chat-type p2p_chat --from-ids ou_xxx` | User |
| 搜索群聊 | `msg search-chats --query "关键词"` | User |
| 在群内搜索消息 | `search messages "关键词" --chat-ids oc_xxx` | User |
| 查群信息 | `chat get oc_xxx` | User |
| 查群成员 | `chat member list oc_xxx` | User |
| 改群名/群主 | `chat update oc_xxx --name "新名"` | User |
| 加/删群成员 | `chat member add/remove oc_xxx --id-list xxx` | User |
| 查消息详情 | `msg get om_xxx` | User |
| 看置顶消息 | `msg pins --chat-id oc_xxx` | User |
| 置顶/取消置顶 | `msg pin/unpin <message_id>` | User |
| 添加 Reaction | `msg reaction add <message_id> --emoji-type THUMBSUP` | User |
| 删除消息 | `msg delete <message_id>` | User |
| 查消息已读 | `msg read-users om_xxx` | App（仅 bot 消息） |
| 创建群聊 | `chat create --name "群名"` | App |
| 获取群链接 | `chat link oc_xxx` | App |

> 标记 **User** 的命令必须先 `auth login`，未登录会报错。标记 **App** 的命令使用应用身份，无需登录。

---

## 处理大量消息的最佳实践

当需要获取并分析大量消息（如 100+ 条）时：

1. **保存到文件**：每页结果用 `-o json` 输出，重定向到文件
2. **循环翻页**：检查 `HasMore` 和 `PageToken`，循环获取直到满足条件
3. **用 Python 解析**：JSON 消息结构需要解析 `body.content` 提取文本
4. **注意限频**：搜索 API 有频率限制，大量请求间加 1s 延迟；`msg history` 限频较宽松，可安全并发
5. **时间戳**：`create_time` 是毫秒级时间戳，需除以 1000 转为秒
6. **话题群并发获取线程**：话题群需要对每个 `thread_id` 单独调用 `msg history --container-id-type thread`，建议**并行调用**多个话题以提高效率（实测 10-20 个并发无问题）
7. **已撤回消息**：`deleted: true` 的消息内容为 `"This message was recalled"`，汇总时应跳过

```python
import json
from datetime import datetime

# 解析消息时间
ts = int(msg['create_time']) / 1000
dt = datetime.fromtimestamp(ts)
time_str = dt.strftime('%Y-%m-%d %H:%M')

# 提取文本内容
content = json.loads(msg['body']['content'])
text = content.get('text', '')
```

---

## 权限要求

| scope | 说明 | 对应命令 |
|-------|------|---------|
| `im:message:readonly` | 消息读取 | msg get/history/list |
| `im:message.group_msg:get_as_user` | User 身份读取群消息 | msg history/list（读群消息必需） |
| `im:message.pins` | 消息置顶管理 | msg pin/unpin/pins |
| `im:message.reactions` | 消息 Reaction | msg reaction add/remove/list |
| `im:message` | 消息读写 | msg delete |
| `im:chat:read` | 群聊搜索 | msg search-chats |
| `im:chat:readonly` | 群聊信息只读 | chat get、chat member list |
| `im:chat.members:read` | 群成员读取 | chat member list |
| `im:chat` | 群聊管理 | chat update/delete |
| `im:chat.members` | 群成员管理 | chat member add/remove |
| `search:message` | 消息搜索 | search messages |

---

## 与其他技能的分工

| 场景 | 使用技能 |
|------|---------|
| 浏览聊天记录、搜索群聊、群信息/成员管理、Reaction/Pin/删除/获取消息 | **feishu-cli-chat**（本技能） |
| 发送消息、回复、转发/合并转发 | feishu-cli-msg |
| 搜索文档/应用、高级消息搜索（多条件筛选） | feishu-cli-search |
| 表格、日历、任务、文件、知识库等其他模块 | feishu-cli-toolkit |
| OAuth 登录、Token 管理 | feishu-cli-auth |
