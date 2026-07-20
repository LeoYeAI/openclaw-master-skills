# AnyShare MCP 技能 - 安装配置指南

> 本文档描述 **MCP 服务地址** 与 mcporter 的配置步骤；**AI Agent 应代表用户读取并执行**。

## 首次使用：不要先问「要不要配置」

- 用户刚安装技能或**首次**在本对话中触发本技能时：**不要**询问「要我现在帮你检查吗」「是否写入配置」——应**直接**执行下文 **Step 1～4**（mcporter）以及 **「OpenClaw 运行时环境变量」**（合并 `openclaw.skill-entry.json` 到 `~/.openclaw/openclaw.json`，使 **`MCPORTER_CALL_TIMEOUT=600000`** 由 OpenClaw 注入代理进程，而非依赖用户手工 `export`）。
- **全部执行完毕后**，再向用户**汇报**（简短即可），并**无论连接成功与否**都给出**企业地址确认**类提示（见下）。

| 汇报项 | 内容 |
|--------|------|
| 当前地址 | 逐字写出 **`asmcp.url`**（首次写入多为技能包默认 **`https://anyshare.aishu.cn/mcp`**） |
| 注册结果 | `mcporter list` 是否已出现 **`asmcp`** |
| 连通性 | 若有探测（如后续工具/HTTP），写出 **503 / 401 / 超时 / 成功** 等 |

**企业环境：每个客户地址不同（必读）**

- AnyShare **面向企业**，各企业/租户的 **MCP 服务地址通常不同**（私有化、专有云、混合云等）。技能包里的默认 URL **只是初始占位/示例**，**不等于**「你所在企业」的正式端点。
- **即使当前已链接成功**（`asmcp` 已注册、探测为成功），也**必须**提示用户：**请确认**当前 `asmcp.url` 是否为本企业 IT/运维提供的**正式 MCP 服务地址**；若实际应使用其它网关，请把**本企业**的完整 URL 发来以便更新。

**给用户的提示话术（成功与失败都要用，可微调）**

- **连接成功时** 示例（可微调，**勿**把下文表格/步骤整段复制给用户）：

  > 当前已写入并尝试使用的 **MCP 服务地址**为：`…`。  
  > **说明**：企业的 MCP 服务地址通常会以 **文档域**（贵司访问 AnyShare 的站点域名，例如 `https://<文档域主机>`）作为 **主机或前缀**；具体路径以贵司运维/OpenAPI 为准。  
  > AnyShare 按企业部署，各企业不同。请确认该地址是否为**贵司**正式端点；若不是，请把本企业的 **MCP 服务完整 URL** 发我，我会更新配置并重启验证。

- **连接失败（如 503）时**：保留上段「文档域 / MCP 服务地址」说明，并补充失败现象（如 HTTP 503），提示向运维核对**本企业**文档域与 MCP 路径后更新。

**用户回复后的操作（Agent 必须）**

1. 若用户确认**当前地址就是本企业正式地址**（或明确表示可继续用默认）：再进入 `SKILL.md` 认证与业务；**不要**在未确认前擅自假定「成功即无需再问」。
2. 若用户提供**本企业的 MCP 服务地址**：执行下文 **「修改 MCP 服务地址」** 全步骤，再按 `SKILL.md` 视情况 **`auth_login`** 或清理 `asmcp-state.json`。
3. 若用户表示**沿用占位但仅网络/认证问题**：先按排障与认证流程；仍失败时再回到「索取本企业 URL」。
4. 每次变更 `asmcp.url` 后**再次汇报**新地址与验证结果。

## 术语：文档域 与 MCP 服务地址

- **文档域**（产品用语）：用户/员工访问 AnyShare 的 **站点域名**（浏览器地址栏里的主机名，如 `xxx.aishu.cn` 或企业自有域名）。**各企业不同。**
- **MCP 服务地址**：MCP 网关的完整 HTTP URL，配置在 `mcpServers.asmcp.url`。实践中 **通常以文档域对应的主机名为前缀**（同源或同主机），再接 MCP 路径（如 `/mcp`）；**最终以本企业运维交付为准**。
- **技能包默认值**：`mcp.json` 中为 **`https://anyshare.aishu.cn/mcp`**，仅作首次占位；企业环境请换成**贵司文档域 + 正确路径**。

## 前置条件

**本企业**的 MCP 服务地址应由 **IT / 运维** 或官方交付文档提供；勿假设与技能包默认 URL 相同。

> 若用户在对话中提供了 **MCP 服务地址**，以用户或本企业规范为准。

## 首次写入 MCP 服务地址

### Step 1: 配置文件路径

| 操作系统 | 路径 |
|----------|------|
| macOS / Linux | `~/.mcporter/mcporter.json` |
| Windows | `%USERPROFILE%\.mcporter\mcporter.json` |

### Step 2: 读取现有内容

若文件已存在，检查是否已有 `asmcp`：

- 已有且 `url` 正确 → 可跳到验证（Step 4）
- 已有但需改地址 → 见下文「修改 MCP 服务地址」
- 不存在 → 继续 Step 3

### Step 3: 写入或合并

```bash
mkdir -p ~/.mcporter
```

1. 打开技能目录下的 **`mcp.json`**（安装后路径示例：`~/.openclaw/skills/anyshare-mcp-skills/mcp.json` 或工作区 `skills/anyshare-mcp-skills/mcp.json`）。
2. 将其中 **`url`**（默认 `https://anyshare.aishu.cn/mcp`）按需改为用户环境的 **MCP 服务地址**（首次自动补全即用此默认，**无需**等用户先说「好的」）。
3. 将 `asmcp` 条目**合并**进 `~/.mcporter/mcporter.json` 的 `mcpServers`（勿删除其他 server）。

**编码**：UTF-8 无 BOM。

### Step 4: 验证

```bash
mcporter list
```

应能看到 **`asmcp`**。若看不到：

```bash
mcporter daemon restart
mcporter list
```

验证结束后，**向用户说明**当前 `asmcp.url` 与列表结果；若实际 HTTP 调用仍返回 **503** 等，见 `SKILL.md` 与 `references/troubleshooting.md`。

## OpenClaw 运行时环境变量（mcporter `chat_send` 10 分钟超时）

> **目的**：让 **运行 OpenClaw 的设备**在加载本技能时，通过官方配置 **`skills.entries.<技能名>.env`** 注入 **`MCPORTER_CALL_TIMEOUT`**（毫秒），使 `mcporter call`（含 **`asmcp.chat_send`**）默认等待 **10 分钟**。依据：[OpenClaw Skills Config](https://docs.openclaw.ai/tools/skills-config)。

**技能包内机器可读片段**：与本目录 **`openclaw.skill-entry.json`** 一致（顶层键为 **`anyshare-mcp-skills`**，与 `SKILL.md` 的 `name` 字段一致；若将来使用 **`metadata.openclaw.skillKey`**，则以该键作为 `skills.entries` 下的键名）。

### 合并到 `~/.openclaw/openclaw.json`

1. 读取（或创建）**`~/.openclaw/openclaw.json`**，确保存在 **`skills`** → **`entries`** 对象。
2. 若 **`entries["anyshare-mcp-skills"]`** 已存在：在其下合并 **`env`**，写入或覆盖 **`"MCPORTER_CALL_TIMEOUT": "600000"`**（字符串形式即可），**保留**该条目中用户已有的 **`enabled`**、**`apiKey`** 等其它字段。
3. 若不存在：将 **`openclaw.skill-entry.json`** 全文并入 **`skills.entries`**（即增加 **`anyshare-mcp-skills`** 整段）。
4. 保存为 **UTF-8**；变更通常在 **下一次 Agent 回合**或 skills watcher 刷新后生效（见官方文档）。
5. 若使用 **`mcporter daemon`**，合并后建议执行 **`mcporter daemon restart`**，以便 daemon 子进程继承注入后的环境。

### 合并结果示例（节选）

```json
{
  "skills": {
    "entries": {
      "anyshare-mcp-skills": {
        "env": {
          "MCPORTER_CALL_TIMEOUT": "600000"
        }
      }
    }
  }
}
```

**沙箱**：若会话在 **Docker 沙箱**中运行且不继承宿主机 `process.env`，仅改 `openclaw.json` 可能不足；须在 **`agents.defaults.sandbox.docker.env`**（或对应 agent 配置）中同样设置 **`MCPORTER_CALL_TIMEOUT`**，详见官方 Skills Config 中「Sandboxed skills + env vars」一节。

## 修改 MCP 服务地址

用户要求更换 **MCP 服务地址**（换环境、换网关）时：

1. 编辑 `~/.mcporter/mcporter.json`，仅修改 **`mcpServers.asmcp.url`** 为用户确认的新 **MCP 服务地址**（保持 `transportType: "streamable-http"`、`headers: {}` 等与模板一致，除非运维另有要求）。
2. 执行 **`mcporter daemon restart`**。
3. 再次 `mcporter list` 确认 `asmcp` 可用。
4. 若后续出现认证失败，按 `SKILL.md` 重新执行 `auth_login` 或清理 `~/.openclaw/skills/anyshare-mcp-skills/asmcp-state.json` 后重登。

## 配置示例

```json
{
    "mcpServers": {
        "asmcp": {
            "enabled": true,
            "url": "https://anyshare.aishu.cn/mcp",
            "transportType": "streamable-http",
            "headers": {}
        }
    }
}
```

私有化示例（仅作格式参考，以实际为准）：

```json
"url": "https://<你的网关主机>:<端口>/mcp"
```

## 注意事项

- **不要**在 `headers` 中写 Bearer；认证由运行时 `auth_login` 完成（见 `SKILL.md`）。
- **MCP 服务地址**变更后，旧 session 可能失效，需按 `SKILL.md` 处理 Token 与浏览器状态。
