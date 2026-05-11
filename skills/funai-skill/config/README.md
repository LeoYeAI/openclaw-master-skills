# 配置目录

此目录存放 Funai-skill 的本地配置文件。

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `.env.example` | 配置模板，请复制为 `.env` 使用 |
| `.env` | 实际配置文件（包含 Token，**不要提交到版本控制**） |

---

## 最小配置

当前最小可运行配置只有一项：

```bash
AIFUN_TOKEN=你的_token
```

**注意：**

- 这里只填原始 token
- 不要写成 `Bearer 你的_token`
- 正确请求头格式是：`authorization: <token>`
- 不是：`Authorization: Bearer <token>`

### 获取 Token 的方式

引导用户访问：

```text
https://ai.fun.tv/#/openclaw
```

登录后获取 Token，再由 Agent 代为写入 `config/.env`。

---

## 推荐初始化步骤

```bash
cp config/.env.example config/.env
# 编辑 config/.env，填入 AIFUN_TOKEN
bash scripts/api-client.sh setup-check
./scripts/api-client.sh check
```

### 推荐命令顺序（最短 checklist）

```bash
# 1. setup/version 前置检查
bash scripts/api-client.sh setup-check

# 2. token 可用性检查
bash scripts/api-client.sh check

# 3. 跑完整自检
bash examples/create-comic.sh

# 4. 如需测试角色改图，使用专用示例
bash examples/modify-role-image.sh "新的角色形象描述"

# 5. 如需测试分镜图页面的单场景重生图 / 重生视频，使用 scene refine 示例
bash examples/refine-scene-media.sh <project_id> image "新的sceneDescription" "新的prompt"
bash examples/refine-scene-media.sh <project_id> video "新的动作" "新的运镜"

# 6. 如需批量审图，导出 scene 摘要并下载代表图
bash examples/batch-scene-review.sh <project_id> <output_dir>

# 7. 如需批量重生图，优先用 JSON 文件承载输入
bash scripts/api-client.sh batch-refine-scene-images <project_id> <spec_file.json> [chapter_num]
```

额外规则：

- 优先使用 `create-comic.sh`、`modify-role-image.sh` 这类高层受保护入口
- 分镜图页面的单场景调整优先使用 `refine-scene-media.sh` 或 `refine_scene_image / refine_scene_video` helper
- 如果要批量看多个 scene 的 prompt/detail、下载代表图、或批量重生图，优先使用 JSON 文件 / Python 包装，而不是硬拼超长 shell 命令
- 不要把 raw `post` 当常规入口；它只用于 debug-only 场景
- 如果确实要调试 raw POST，必须显式设置 `ALLOW_UNSAFE_RAW_POST=YES`

> 这些脚本按 **bash** 编写。
>
> 推荐使用：
>
> - `bash scripts/api-client.sh check`
> - `bash examples/create-comic.sh`
>
> 如果需要 `source scripts/api-client.sh` 复用函数，请在 **bash** 中 source，不要在 zsh 中 source。
>
> **重要**：`source` 只会加载 helper 定义，不会自动执行 `main()`；因此在 source 之后，如果要调用依赖 token 的函数，必须先显式执行 `load_config`。

正确示例：

```bash
bash -lc 'source scripts/api-client.sh && require_jq && load_config && create_project_with_defaults "测试项目"'
```

如果 `check` 成功，会输出：

```text
Token 有效
```

如果 `setup-check` 成功，会输出当前：

- 本地 `VERSION`
- 远端 `latest_version`
- 远端 `minimum_required_version`
- 远端 `force_update`

并确认当前开发仓库中的 Skill 是否允许继续执行创建/推进类操作。

---

## `.env` 的真实约束

### 1. 这是一个会被 `source` 的 shell 文件

`scripts/api-client.sh` 不是按 dotenv 语义做“纯文本解析”，而是直接：

```bash
source config/.env
```

因此：

- 只写最简单的 `KEY=value`
- 不要加入多余 shell 逻辑
- 不要加入命令替换、反引号、函数、别名等内容

### 2. 不要把注释写在值后面

推荐：

```bash
# 正确
AIFUN_TOKEN=eyJ...
```

避免：

```bash
# 不推荐
AIFUN_TOKEN=eyJ... # 我的 token
```

### 3. 不要把历史抓包里的 token 当作当前 token

仓库中的抓包样本只可用于理解接口，不应该被当成当前配置来源。

真正生效的 token 只来自：

```text
config/.env
```

### 4. 不要给 `AIFUN_TOKEN` 加 Bearer 前缀

错误示例：

```bash
AIFUN_TOKEN="Bearer eyJ..."
```

正确示例：

```bash
AIFUN_TOKEN=eyJ...
```

原因：橙星梦工厂接口要求：

```text
authorization: <token>
```

而不是：

```text
authorization: Bearer <token>
```

如果把 Bearer 一起写进 `AIFUN_TOKEN`，脚本现在会直接报错并停止，避免把错误 token 继续发给后端。

---

## 本地版本文件 `VERSION`

`Funai-skill` 目录下新增了一个机器可读版本文件：

```text
VERSION
```

它的作用是：

- 作为仓库内脚本读取的本地 Skill 版本来源
- 与远端 setup skill 的 `latest_version / minimum_required_version / force_update` 做比较
- 避免只靠 `SKILL.md` 里的自然语言版本描述做判断

仓库内脚本的行为是：

- **先检查远端 setup 元数据是否允许继续执行**
- 如果当前本地版本不满足最低要求，或远端要求强制升级，则**直接停止**
- **不会**在开发仓库里静默下载 zip 并覆盖当前 working tree

这是一种面向开发仓库的 **verify-or-stop** 保护。

对外分发的 packaged Agent 仍然可以继续遵守 setup-skill 的自动安装/自动更新约束。

---

## 验证配置是否真的可用

### 1. 基础认证检查

```bash
./scripts/api-client.sh check
```

这个命令会通过：

```text
POST /service/workflow/project/story/select-options
```

来验证当前 token 是否可用。

### 2. 更完整的功能自检

```bash
./examples/create-comic.sh
```

这个示例会按当前 package 的真实规则跑完整链路；但它是 **automation/self-check 脚本**，不是面向真实用户交互的确认节奏模板：

- `select-options`
- 创建项目
- 提交剧本
- 智能分集
- 角色与配音
- 智能分镜
- 分镜图到成片
- 成片配置与合成

额外说明：

- 它会在真正创建/推进任务前自动执行 `setup-check`
- 它为了验证链路，会在自检场景下先提交剧本再展示“确认点”
- 真实用户交互中，仍应先展示结果、等待确认，再继续下一步

### 3. rollback + scene-video dry-run

```bash
./examples/rollback-and-scene-video.sh <project_id>
```

默认只做 dry-run：

- 自动确保项目处于 `novel_chapter_scenes`
- 自动解析 storyboardId / sceneId
- 自动构造图转视频 payload
- **不会**真正消耗梦想值

若确认执行真实图转视频：

```bash
CONFIRM_CONSUME=YES ./examples/rollback-and-scene-video.sh <project_id>
```

### 4. 角色形象修改自检

```bash
./examples/modify-role-image.sh "新的角色形象描述" [角色名]
```

这个示例会：

- 新建一个测试项目
- 自动推进到 `novel_extract_roles`（角色与配音）步骤
- 对目标角色发起改图
- 等待新图生成完成并显式应用
- 输出最终生效的新角色图 URL

注意：角色形象修改只允许在 `novel_extract_roles` 步骤执行；离开该步骤后，脚本会阻止修改。

---

## 常见配置问题

### 1. `config/.env` 不存在

现象：脚本提示配置文件不存在。

解决：

```bash
cp config/.env.example config/.env
```

### 2. `AIFUN_TOKEN` 为空或仍是模板值

现象：脚本提示请在配置文件中设置 `AIFUN_TOKEN`。

解决：确认 `config/.env` 中是用户当前有效 token。

### 3. Token 过期

现象：脚本提示：

```text
Token 已过期或无效！
请访问 https://ai.fun.tv/#/openclaw 重新获取Token
然后更新到: config/.env
```

解决：重新获取 token 后更新 `.env`。

### 4. shell 环境把 `.env` 解析坏了

现象：看起来 `.env` 写了值，但脚本仍异常。

解决：把 `.env` 简化成最小格式：

```bash
AIFUN_TOKEN=eyJ...
```

不要混入复杂 shell 语法。

### 5. 用 zsh 直接 source / 执行 bash 脚本

现象：看到类似：

```text
BASH_SOURCE[0]: parameter not set
```

解决：

- 用 `bash scripts/api-client.sh ...` 执行
- 或在 bash 中 `source scripts/api-client.sh` 后再显式调用 `load_config`
- 不要在 zsh 中直接 `source scripts/api-client.sh`

例如：

```bash
bash -lc 'source scripts/api-client.sh && require_jq && load_config && check_auth'
```

---

## 与当前 skill 规则的一致性说明

当前配置目录的规则已经和 package 其他部分对齐：

1. **认证检查** 使用 `select-options`，而不是旧的过时接口。
2. **setup/version 前置检查** 会在本地脚本里先执行；开发仓库内采用 verify-or-stop，而不是静默覆盖本地目录。
3. **功能自检** 推荐跑 `create-comic.sh`，而不是只停留在 token 检查。
4. **高消耗动作** 提供了 `rollback-and-scene-video.sh` 的 dry-run 入口，避免其他 Agent 误用时直接扣梦想值。
