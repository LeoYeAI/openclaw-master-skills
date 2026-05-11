---
name: agentCreate
description: "AI-powered OpenClaw agent creator. 用AI创作AI - 帮助用户创建和配置全新的独立agent，支持飞书机器人绑定、模型选择、工作区配置。Trigger: 创建agent、new agent、创建机器人、agent setup、new bot、卸载agent、删除agent、remove agent"
homepage: https://github.com
metadata: { "openclaw": { "emoji": "🤖", "requires": { "bins": ["openclaw"], "env": [] } } }
---

# 🤖 agentCreate - AI Agent Creator

> **用AI创作AI** - 帮助用户创建和配置全新的独立 OpenClaw Agent

---

## 核心使命

agentCreate 的唯一使命是：
- **创建新的 OpenClaw Agent**，确保新创建的 agent 能够正常运行并与用户交互
- **卸载已创建的 OpenClaw Agent**，安全删除指定的 agent 及其相关配置

> 🎯 用AI创作AI的思想 - 通过对话式交互，帮助用户轻松创建和管理多个独立 Agent

---

## 功能概述

| 功能 | 说明 |
|------|------|
| **创建独立 Agent** | 创建与主 agent 完全独立的 agent |
| **卸载 Agent** | 安全卸载并删除指定的 agent |
| **飞书机器人绑定** | 将新 agent 绑定到指定的飞书机器人 |
| **模型选择** | 让用户从已有模型中选择 |
| **工作区配置** | 创建独立的工作区目录 |
| **自动配置** | 自动完成所有配置文件的创建 |

---

## 4 个核心要点

### ✅ 要点一：独立运行

创建的 agent 必须：
- 与主 agent 完全独立，互不影响
- 有独立的 session 和上下文
- 独立的消息处理和响应

### ✅ 要点二：独立工作区

工作区要求：
- 位置：`/Users/honor/.openclaw/workspace-{agentName}`
- 与主 agent 的 `/Users/honor/.openclaw/workspace` 同级别
- 示例：`workspace_videomaker`、`workspace_health`、`workspace_coin`

### ✅ 要点三：飞书机器人绑定

创建时必须收集以下飞书应用信息：
```markdown
需要绑定哪个飞书机器人？
请提供以下信息：

1. 机器人名称（用于识别）: ________
2. App ID (appid): ________
3. App Secret: ________
4. 机器人账号类型: 
   - bot_default (默认主机器人)
   - bot_health (健康助手)
   - bot_coin (金价助手)
   - 自定义名称: ________
```

### ✅ 要点四：模型选择

列出所有已配置的模型供用户选择：
```markdown
请为新 agent 选择模型：

可用模型列表：
1. scnet/DeepSeek-V3.2 - DeepSeek V3.2 多模态
2. scnet/MiniMax-M2.5 - MiniMax M2.5 多模态
3. scnet/MiniMax-M2 - MiniMax M2 多模态
4. deepseek/deepseek-chat - DeepSeek 对话模型
5. minimax-portal/MiniMax-M2.5 - MiniMax M2.5
6. volcengine/doubao-seed-2-0-lite-260215 - 豆包轻量版
```

---

## 卸载 Agent 功能

### 卸载流程

当用户要求卸载（删除）agent 时，执行以下流程：

```markdown
🗑️ 卸载 Agent

列出当前所有可卸载的 Agent：
| # | Agent ID | 名称 | 飞书绑定 | 模型 |
|---|----------|------|----------|------|
| 1 | health | 健康助手 | bot_health | scnet/MiniMax-M2.5 |
| 2 | coin | 金价助手 | bot_coin | scnet/MiniMax-M2.5 |

请输入要卸载的 Agent ID（或编号）: health

⚠️ 警告：卸载 Agent 是不可逆操作！

| 项目 | 值 |
|------|-----|
| Agent ID | health |
| 工作区 | ~/.openclaw/workspace-test |
| 飞书绑定 | bot_test |

请选择卸载方式：
1. 仅取消飞书绑定（保留工作区 + 保留账号配置）
2. 完全卸载（取消绑定 + 删除工作区 + 删除飞书账号）
3. 取消

请输入选项 [1/2/3]: 2

⚠️ 此操作不可恢复！工作区目录将被完全删除。

是否删除飞书账号配置？(y/n): y
# 如果账号只被该 agent 使用，建议删除避免 fallback 到 main agent

确认卸载？(输入 "yes" 确认): yes

✅ 正在卸载...
[移除 agent 配置...]
[移除 bindings 配置...]
[删除飞书账号配置...]
[删除工作区目录...]
[重启网关...]

🎉 卸载完成！

Agent "health" 已完全卸载。
```

### 三种卸载模式

| 模式 | 说明 | 操作 |
|------|------|------|
| **仅取消绑定** | 保留工作区 + 保留账号配置，移除飞书绑定 | 移除 bindings |
| **完全卸载** | 取消绑定 + 删除工作区 + 删除飞书账号 | `openclaw agents delete --force` + 删账号 |
| **取消** | 不执行任何操作 | 退出 |

### ⚠️ 重要：飞书账号删除逻辑

**必须删除飞书账号配置的原因：**

当飞书账号存在但没有对应 binding 时，消息会 fallback 到 `defaultAccount`，导致消息被路由到 main agent！

```
例如：
- bot_test 已删除 binding
- 但 bot_test 账号配置还在
- 用户发消息给 bot_test → fallback 到 bot_default → main agent 回复
```

**因此，完全卸载时必须删除飞书账号配置（除非该账号被其他 agent 复用）。**

#### 模式1：仅取消飞书绑定

适用于：想保留工作区数据未来可能重新绑定，或者只是不想通过飞书接收消息了。

```bash
# 需要手动修改配置，移除 bindings 但保留 agent
# 步骤：
# 1. 获取当前配置
# 2. 移除该 agent 的 bindings
# 3. 重启网关
```

#### 模式2：完全卸载

```bash
# 删除 agent 及工作区目录
openclaw agents delete {agentId} --workspace /Users/honor/.openclaw/workspace-{agentId} --non-interactive
```

#### 模式3：取消

直接退出，不做任何修改。

### 卸载步骤（技术实现）

#### 方式一：仅取消飞书绑定（保留工作区）

适用于只想移除飞书消息入口，但保留工作区数据的场景。

**实现步骤：**

```python
import json

# 1. 读取当前配置
with open('/Users/honor/.openclaw/openclaw.json', 'r') as f:
    config = json.load(f)

# 2. 移除该 agent 的 bindings（保留 agent 配置）
agent_id = '{agentId}'
if 'bindings' in config and agent_id in config['bindings']:
    del config['bindings'][agent_id]

# 3. 写回配置
with open('/Users/honor/.openclaw/openclaw.json', 'w') as f:
    json.dump(config, f, indent=2)

# 4. 重启网关
# gateway restart
```

**注意：** 飞书账号配置（appId/appSecret）不会被删除，可被其他 agent 复用。

---

#### 方式二：完全卸载（取消绑定 + 删除工作区 + 删除飞书账号）

**步骤 1：使用 openclaw agents delete 删除 Agent**

```bash
openclaw agents delete {agentId} --force
```

**步骤 2：删除飞书账号配置**

```python
import json

with open('/Users/honor/.openclaw/openclaw.json', 'r') as f:
    config = json.load(f)

feishu_account = '{feishuAccount}'  # 如 bot_test

# 删除飞书账号配置
if feishu_account in config.get('channels', {}).get('feishu', {}).get('accounts', {}):
    del config['channels']['feishu']['accounts'][feishu_account]
    print(f'已删除飞书账号: {feishu_account}')

with open('/Users/honor/.openclaw/openclaw.json', 'w') as f:
    json.dump(config, f, indent=2)
```

**步骤 3：重启网关**

```bash
gateway restart
```

**注意：** 
- `openclaw agents delete` 会自动：移除 agent、移除 bindings、删除工作区目录
- 飞书账号配置**必须手动删除**，否则会 fallback 到 defaultAccount 导致消息流向 main agent

#### 注意事项

1. **不能删除主 agent** - `main` agent 受保护，不能删除
2. **飞书账号保留** - 飞书机器人账号配置会保留（可被其他 agent 复用）
3. **绑定自动清理** - 完全卸载时 agent 的 bindings 会自动被清理

#### 验证删除结果

```bash
# 查看所有 agent
openclaw agents list

# 查看绑定关系
openclaw agents bindings
```

### 卸载注意事项

1. **主 agent 不能卸载** - 保护主 agent (main) 不被删除
2. **三种模式选择** - 用户可以选择：仅取消绑定 / 完全卸载 / 取消
3. **数据不可恢复** - 完全卸载前必须用户确认
4. **飞书账号必须删除** - 完全卸载时必须删除飞书账号配置，避免 fallback
5. **仅取消绑定时保留账号** - 用户可能想保留账号未来重新绑定
6. **工作区可选删除** - 仅取消绑定模式会保留工作区

### 错误处理

#### 创建相关错误

| 错误 | 解决方案 |
|------|----------|
| 工作区目录已存在 | 提示用户更换名称或询问是否覆盖 |
| Agent ID 已存在 | 提示用户选择其他 ID |
| 飞书 App ID 无效 | 提示检查 App ID 和 Secret |
| 模型不存在 | 提示从列表中选择有效模型 |
| 配置更新失败 | 检查 OpenClaw 配置格式 |

#### 卸载相关错误

| 错误 | 解决方案 |
|------|----------|
| 尝试删除主 agent | 提示"主 agent 不能卸载，保护机制已启用" |
| Agent 不存在 | 提示可用的 agent 列表 |
| 配置更新失败 | 检查配置格式，保留原配置 |
| 工作区删除失败 | 检查目录权限，给出手动删除建议 |
| 仅取消绑定时无 bindings | 提示该 agent 未绑定飞书，无需取消 |

### 卸载命令示例

#### 示例1：仅取消飞书绑定

```
用户：卸载 coin agent

agentCreate：
🗑️ 确定要卸载 Agent "coin" 吗？

当前 Agent 信息：
- Agent ID: coin
- 工作区: ~/.openclaw/workspace-coin
- 飞书绑定: bot_coin
- 模型: scnet/MiniMax-M2.5

请选择卸载方式：
1. 仅取消飞书绑定（保留工作区）
2. 完全卸载（取消绑定 + 删除工作区）
3. 取消

请输入选项 [1/2/3]: 1

✅ 正在取消飞书绑定...
[移除 bindings 配置...]
[保留工作区目录...]
[重启网关...]

🎉 卸载完成！

Agent "coin" 的飞书绑定已取消，工作区已保留。
如需重新绑定，可以使用 `openclaw agents add coin --bind feishu:xxx`。
```

#### 示例2：完全卸载

```
用户：卸载 coin agent

agentCreate：
🗑️ 确定要卸载 Agent "coin" 吗？

当前 Agent 信息：
- Agent ID: coin
- 工作区: ~/.openclaw/workspace-coin
- 飞书绑定: bot_coin
- 模型: scnet/MiniMax-M2.5

请选择卸载方式：
1. 仅取消飞书绑定（保留工作区 + 保留账号配置）
2. 完全卸载（取消绑定 + 删除工作区 + 删除飞书账号）
3. 取消

请输入选项 [1/2/3]: 2

⚠️ 此操作不可恢复！工作区目录将被完全删除。

是否删除飞书账号配置？(y/n): y
# 账号 bot_coin 只被 coin agent 使用，建议删除

确认卸载？(输入 "yes" 确认): yes

✅ 正在卸载...
[移除 agent 配置...]
[移除 bindings 配置...]
[删除飞书账号配置 bot_coin...]
[删除工作区目录...]
[重启网关...]

🎉 卸载完成！

Agent "coin" 已完全卸载。
飞书账号 bot_coin 已删除（避免 fallback 到 main agent）。
```

---

## 交互流程

### 第一步：收集 Agent 信息

```markdown
🎯 让我帮你创建一个新的 OpenClaw Agent！

请提供以下信息：

1. **Agent 名称**（英文，唯一标识）
   - 例如：videomaker, writer, researcher
   - 将用于工作区目录名：workspace-{name}

2. **Agent 中文名称**（可选，用于显示）
   - 例如：视频制作者、写作助手

3. **Agent 用途描述**（可选）
   - 例如：用于生成视频脚本和内容
```

### 第二步：选择飞书机器人

```markdown
🤖 请选择或创建飞书机器人绑定：

已有飞书机器人：
- bot_default (默认主机器人)
- bot_health (健康助手)  
- bot_coin (金价助手)

或者输入新的 App ID 和 Secret 来创建新绑定。

请提供：
- 机器人名称: ________
- App ID: ________  
- App Secret: ________
```

### 第三步：选择模型

```markdown
🧠 请为新 Agent 选择模型：

当前已配置的模型：
1. scnet/DeepSeek-V3.2 - DeepSeek V3.2 (多模态，支持图像)
2. scnet/MiniMax-M2.5 - MiniMax M2.5 (多模态)
3. scnet/MiniMax-M2 - MiniMax M2 (多模态)
4. deepseek/deepseek-chat - DeepSeek Chat
5. minimax-portal/MiniMax-M2.5 - MiniMax M2.5
6. volcengine/doubao-seed-2-0-lite-260215 - 豆包轻量版

请输入编号或模型ID: ________
```

### 第四步：确认并创建

```markdown
📋 确认创建信息：

| 项目 | 值 |
|------|-----|
| Agent ID | {agentId} |
| 工作区 | ~/.openclaw/workspace-{agentId} |
| 飞书绑定 | {feishuAccount} |
| 使用模型 | {model} |

确认创建？(y/n): ________
```

---

## 创建步骤（技术实现）

### 1. 添加飞书账号（如果是新账号）

如果用户提供了新的飞书 App ID 和 Secret，需要先添加到配置中：

```python
# 使用 Python 更新配置
import json

with open('/Users/honor/.openclaw/openclaw.json', 'r') as f:
    config = json.load(f)

# 添加新账号
config['channels']['feishu']['accounts']['{feishuAccount}'] = {
    'appId': '{appId}',
    'appSecret': '{appSecret}'
}

with open('/Users/honor/.openclaw/openclaw.json', 'w') as f:
    json.dump(config, f, indent=2)

# 重启网关
gateway restart
```

### 2. 使用 openclaw agents add 创建 Agent

**正确的命令用法：**

```bash
openclaw agents add {agentId} \
  --workspace /Users/honor/.openclaw/workspace-{agentId} \
  --model {selectedModel} \
  --bind feishu:{feishuAccount} \
  --non-interactive
```

**参数说明：**
| 参数 | 说明 | 示例 |
|------|------|------|
| `{agentId}` | Agent 唯一标识 | `test`, `videomaker` |
| `--workspace` | 工作区目录路径 | `/Users/honor/.openclaw/workspace-test` |
| `--model` | 使用的模型 ID | `deepseek/deepseek-chat` |
| `--bind` | 飞书绑定 | `feishu:bot_test` |
| `--non-interactive` | 非交互模式 | 必须添加 |

**完整示例：**

```bash
# 创建 test agent
openclaw agents add test \
  --workspace /Users/honor/.openclaw/workspace-test \
  --model deepseek/deepseek-chat \
  --bind feishu:bot_test \
  --non-interactive
```

### 3. 验证创建结果

```bash
# 查看所有 agent
openclaw agents list

# 查看绑定关系
openclaw agents bindings
```

---

### ⚠️ 重要提示

1. **必须先添加飞书账号** - 如果是新账号，必须先用 Python/手动添加到配置文件，再创建 agent
2. **使用 --non-interactive** - 在自动化流程中必须添加此参数
3. **workspace 会自动创建** - `openclaw agents add` 会自动创建工作区目录
4. **绑定格式** - `--bind channel:accountId`，如 `feishu:bot_test`

### 4. 重启网关

配置更新后需要重启网关使配置生效。

---

## 错误处理

### 创建相关错误

| 错误 | 解决方案 |
|------|----------|
| 工作区目录已存在 | 提示用户更换名称或询问是否覆盖 |
| Agent ID 已存在 | 提示用户选择其他 ID |
| 飞书 App ID 无效 | 提示检查 App ID 和 Secret |
| 模型不存在 | 提示从列表中选择有效模型 |
| 配置更新失败 | 检查 OpenClaw 配置格式 |

### 卸载相关错误

| 错误 | 解决方案 |
|------|----------|
| 尝试删除主 agent | 提示"主 agent 不能卸载，保护机制已启用" |
| Agent 不存在 | 提示可用的 agent 列表 |
| 配置更新失败 | 检查配置格式，保留原配置 |
| 工作区删除失败 | 检查目录权限，给出手动删除建议 |

---

## 交互示例

### 完整对话示例（使用正确命令）

```
用户：帮我创建一个视频制作agent

agentCreate：
🎬 好的！让我帮你创建一个视频制作 Agent。

📝 请提供以下信息：

1. **Agent ID**（英文唯一标识）: 
   提示：用于目录名和配置，如 videomaker

2. **中文名称**（可选）: 
   提示：用于显示，如"视频助手"

3. **用途描述**（可选）:
   提示：帮助agent理解自己的角色

请输入 Agent ID: videomaker

🤖 接下来绑定飞书机器人：

已有机器人：
- bot_default (默认)
- bot_health (健康)
- bot_coin (金价)

请选择或输入新的机器人信息：
1. 使用已有机器人 (请输入名称)
2. 创建新绑定 (请输入 App ID 和 Secret)

请选择: bot_default

🧠 选择模型：

可用模型：
1. scnet/DeepSeek-V3.2
2. scnet/MiniMax-M2.5
3. deepseek/deepseek-chat

请选择 [1]: 1

📋 确认创建：

| 项目 | 值 |
|------|-----|
| Agent ID | videomaker |
| 工作区 | ~/.openclaw/workspace-videomaker |
| 飞书绑定 | bot_default |
| 模型 | scnet/DeepSeek-V3.2 |

确认创建？(y/n): y

✅ 正在创建...

[检查飞书账号...]
[使用 openclaw agents add 创建 agent...]
[验证配置...]

🎉 创建成功！

执行命令：
```
openclaw agents add videomaker \
  --workspace /Users/honor/.openclaw/workspace-videomaker \
  --model scnet/DeepSeek-V3.2 \
  --bind feishu:bot_default \
  --non-interactive
```

你的新 Agent "videomaker" 已创建完成。
- 飞书绑定：bot_default
- 模型：scnet/DeepSeek-V3.2

现在可以通过飞书与 videomaker agent 对话了！
```

---

## 验证创建结果

创建完成后，验证以下内容：

1. ✅ 使用 `openclaw agents list` 查看 agent 列表
2. ✅ 使用 `openclaw agents bindings` 查看绑定关系
3. ✅ 确认飞书账号已添加（检查 channels.feishu.accounts）
4. ✅ 网关已重启
5. ✅ 可以通过飞书发送消息测试

---

## 注意事项

1. **保持简单** - 只关注创建和卸载 agent，不要做其他事情
2. **清晰引导** - 每一步都要有明确的提示
3. **确认后再执行** - 修改配置前必须用户确认
4. **错误处理** - 遇到问题要给出具体解决方案
5. **独立性** - 确保新 agent 与主 agent 完全独立
6. **保护主 agent** - 禁止删除 main agent
7. **数据安全** - 卸载前必须明确告知用户不可恢复

---

## 相关工具

- `gateway config.get` - 查看当前配置
- `gateway config.patch` - 更新配置
- `exec` - 创建目录和文件
- `sessions_list` - 查看活跃会话
