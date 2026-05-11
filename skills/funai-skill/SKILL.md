---
name: Funai-skill
description: 橙星梦工厂AI视频制作工具，通过对话式操作，用户可以创建项目、配置剧本、生成角色/分镜/视频、查询任务状态。当用户要求使用橙星梦工厂平台、创建 AI 漫剧项目、或通过 API 与平台交互时使用。触发词：橙星梦工厂、ai.fun.tv、漫剧制作、AI漫剧、FunAI。
---

# 橙星梦工厂 Agent Skill

橙星梦工厂是一个 AI 驱动的漫剧制作平台。通过 API 创建项目、提交剧本、提取角色、生成分镜、配置成片并最终合成视频。

> **内测提示**
>
> 当前您正在使用的是 **Funai-skill 内测版**。
> Agent 在与用户交互时，应明确告知当前处于内测阶段。

> **重要结论**
>
> 真实后端不是“只看 `workflow.currentStep` 的线性流程”，而是：
>
> - 一层是项目级步骤：`workflow.currentStep`
> - 一层是章节级隐藏任务：`comicPreset.data.chapters[]` 中的 `sceneCaptionsTaskStatus`、`dialogTaskStatus`、`sceneTaskStatus`
>
> Agent 如果只看 `currentStep` 就继续调用下一步，非常容易报错。

## Skill 更新约束（创建类操作前必须执行）

**本地机器可读版本文件**：`VERSION`

> 说明：对外文案不再重复写死版本号；实际版本以本地 `VERSION` 与远端 setup 元数据中的 `latest_version / minimum_required_version` 为准。

每当 Agent 准备调用本 Skill 执行任何会创建、推进、修改平台任务的操作前，**必须先访问固定更新入口**：

`https://neirong.funshion.net/skills/setup-skill.md`

至少检查以下字段：

- `latest_version`
- `minimum_required_version`
- `force_update`
- `skill_package_url`

执行规则：

1. 如果本地尚未安装本 Skill，必须先自动安装。
2. 如果远端要求强制更新，或本地版本低于 `minimum_required_version`，必须先自动更新。
3. 版本检查完成后，才能继续执行创建项目、提交剧本、推进步骤、生图、生视频、回退、合成等操作。

## 快速配置

### 1. 获取 Token

引导用户访问 `https://ai.fun.tv/#/openclaw` 并登录，获取 Token 后由 Agent 代为写入配置文件。

### 2. 配置 Token

```bash
cp config/.env.example config/.env
# 编辑 config/.env
# AIFUN_TOKEN=...
```

### 3. 验证配置

```bash
./scripts/api-client.sh setup-check
./scripts/api-client.sh check
```

### 4. 运行完整自检示例

```bash
./examples/create-comic.sh
```

> 示例脚本是**自检脚本**，会使用 `select-options` 返回的实时默认值自动创建测试项目。
>
> 面向真实用户的 Agent 交互中，仍然必须先读取实时可选项；其中 `aspect / style` 必须展示给用户并让用户选择，`generateType / scriptType` 可按当前默认值静默使用，`model / videoModel` 在用户未指定时可继续使用实时默认值。
>
> 另外，示例脚本为了验证整条链路，会在自检场景下先提交剧本再展示“确认点”；这不代表真实用户交互可以跳过“先确认再继续”的节奏要求。

## Agent 必须遵守的执行规则

### 0. 默认模式静默使用，不要主动向用户解释

除非用户明确提出要切换模式，否则 Agent 应直接使用平台默认模式：

- `generateType = 1`（文生图）
- `scriptType = 解说漫模式`（以 `select-options` 返回的默认剧本模式为准）

但这条“静默默认”**只适用于模式层级**，不适用于项目视觉配置。

创建项目时，以下两个字段**不能静默默认**，必须让用户明确选择：

- `aspect`（画面比例）
- `style`（风格）

**重要**：

- 这是 Agent 的内部默认决策，不要主动把“现在默认使用文生图 / 解说漫模式”当成一个需要告诉用户的配置项。
- 只有当用户明确要求切换到其他模式时，才需要说明并调整。
- 即使静默使用默认模式，底层仍然必须先调 `select-options`，并使用当次接口返回的默认值，而不是写死常量。
- `aspect / style` 不能因为接口返回了 `isDefault` 就直接替用户决定，必须向用户展示可选项并让用户确认。

### 1. 创建项目前必须先调 `select-options`

```bash
POST /service/workflow/project/story/select-options
{"appCode":"ai-story","generateType":"1"}
```

规则：

- 必须使用接口返回的 `ratios`、`generateTypes`、`models`、`videoModels`、`styles`、`scriptTypes`
- **禁止**硬编码风格、模型、比例、剧本类型
- `isDefault` 是**请求相关**的，不要把历史默认值写死在代码或文档里
- 如果用户没有明确要求切换模式，则直接静默使用当次接口返回的默认 `generateType / scriptType`
- 但 `aspect / style` 必须向用户展示并让用户选择，不能静默默认
- `model / videoModel` 若用户没有额外要求，可以继续使用 `select-options` 返回的当前默认值
- 面向用户交互时，不需要主动把“文生图 / 解说漫模式”当作默认项拿出来解释；但必须明确让用户选择 `aspect / style`

### 2. 解说剧 / 解说漫模式下，AI 代写剧本必须写成旁白叙述式小说体

如果用户让 AI 帮忙写剧本，而当前走的是**解说剧 / 解说漫模式**，Agent 必须把剧本写成**旁白叙述式的小说 / 故事正文**，而不是分镜脚本。

必须符合：

- 连续叙事
- 以旁白持续讲述故事推进为主
- 可以穿插少量自然对白，但整体仍应是讲述型正文
- 适合后续交给平台自动拆分角色、分镜与解说

禁止出现这类写法：

- `镜头1` / `镜头2`
- `旁白：...` 这种显式台本标签
- `林舟说：...`
- `【音效：脚步声】` / `砰！` / `咚——` 这类音效描述
- 舞台说明式条目
- 分镜表 / 台本格式

正确风格示意：

```text
清晨，城市公园的林荫道上，年轻人林舟正在慢跑。阳光穿过树叶，在青石板路上投下斑驳的金色光影。

他刚想加快脚步，一只金毛犬忽然从灌木旁窜了出来，差点撞上他的膝盖。林舟猛地停住脚步，呼吸一乱，循声抬头望去。

不远处，一个扎着马尾的女孩正快步跑来。她一边抓紧手里的牵引绳，一边有些不好意思地朝林舟笑了笑。
```

错误风格示意：

```text
镜头1：公园远景。
旁白：清晨的城市公园里，林舟正在跑步。
林舟说：今天一定要把状态跑出来。
镜头2：金毛犬冲出。
```

### 3. 创建项目成功后，先展示项目链接

创建成功后必须立即把项目链接告诉用户：

```text
https://ai.fun.tv/#/comic/multiple?projectId={projectId}
```

### 4. 不要只看 `workflow.currentStep`

以下三类 readiness 都要检查：

| 场景 | 检查位置 | 继续条件 |
|------|----------|----------|
| 项目处于哪个大步骤 | `GET /project/{projectId}` → `workflow.currentStep` | 当前步骤正确 |
| 角色图是否完成 | `GET /comic/roles/{presetResourceId}` → `roles[].taskStatus` / `imgUrl` | 全部 `SUCCESS` 且 `imgUrl` 非空 |
| 章节级隐藏任务是否完成 | `GET /resource/comicPreset/{presetResourceId}` → `chapters[]` | 对应状态字段为 `SUCCESS` |

### 5. 不要硬编码 `tts` / `voice-clone-select` 输入

`novel_extract_roles` 不是只传 `chapterNum` 就够。真实可运行的做法是：

1. 先调 `GET /comic/roles/{presetResourceId}`
2. 从 `data.voiceInputs[0]` 或 `data.roles[0].inputs[0]` 取出 live 的 `tts` 输入对象
3. 将它和 `chapterNum` 一起提交

### 6. 不要把 `sceneUuid` 当 `sceneId`

`scene-list` 里的 `sceneUuid` 只是短 ID，不能直接用于分镜/视频接口。

正确流程：

```text
comicPreset/{presetResourceId}
→ chapters[].sceneTaskId
→ GET /task/{sceneTaskId}
→ data.resourceId (storyboardId)
→ GET /resource/{storyboardId}
→ data.data.scenes[].id (完整 sceneId)
```

### 7. 优先向用户返回 `videoPlayUrl`

如果后端返回了新的可播放字段：

- scene 视频资源：`videoPlayUrl`
- 最终成片资源：`videoPlayUrl`

则正确做法是：

- 对外只返回 `videoPlayUrl`
- 高层 helper、示例脚本、模型可见输出中不要暴露原始视频 `url`
- 项目链接仍可作为补充入口一起返回

### 8. `scene/ai/video` 必须使用 scene 当前基准分镜图

图转视频的正确图片来源是当前 scene 的**基准分镜图**：

- 优先使用 `GET /storyboard/scene/{sceneId}/prompt/detail?sceneId={sceneId}` 中的 `video.imageId`
- 再到 `GET /storyboard/scene/{sceneId}/resources` 中找到与这个 `imageId` 对应的 image 资源
- 如果当前仍有 `selected == true` 的 image，它通常就是同一张图

不要直接使用：

- `GET /comic/roles/{presetResourceId}` 返回的 `roles[].imgUrl`

**重要**：这不是“后端一定会报错”的约束，而是“Agent 必须主动保证语义正确”的约束。

live 测试里，后端接受了 `roles[].imgUrl + roles[].imageResourceId`，并成功生成了一条 video 资源。也就是说，传错图时接口可能仍然返回 `200 success`，但生成出来的是**语义错误的视频**。

所以：

- 正确图源 = scene 当前基准分镜图（优先 `video.imageId` 对应的 image）
- 错误图源 = 角色图 / 其他非当前 scene 图片
- 不要依赖后端帮你兜底

## 面向 Agent 的权威执行顺序

### 第 0 步：先做 setup 检查

先读取 `https://neirong.funshion.net/skills/setup-skill.md`，确认本地 skill 版本可用。

### 第 1 步：获取项目可选项

```bash
POST /service/workflow/project/story/select-options
{"appCode":"ai-story","generateType":"1"}
```

### 第 2 步：创建项目

使用上一步接口返回的实时值创建项目。

> live 后端通常会让 `novel_config` 自动完成，所以项目创建后常见的 `currentStep` 是 `novel_input`，这是正常现象。

> 如果用户没有特别说明，不要额外告诉用户“当前默认使用文生图 / 解说漫模式”。
>
> 但在真正创建项目之前，必须先让用户明确选择：
>
> - 画面比例 `aspect`
> - 风格 `style`
>
> 只有这两个字段确认后，才可以结合实时默认的 `generateType / scriptType / model / videoModel` 创建项目。

### 第 3 步：提交剧本

```bash
POST /service/workflow/project/step/next
{
  "userProjectId": "项目ID",
  "step": "novel_input",
  "inputs": [
    {"name": "content", "type": "text", "value": "剧本内容"},
    {"name": "scriptType", "type": "text", "value": "0"},
    {"name": "isSplit", "type": "text", "value": "0"}
  ]
}
```

返回 `resultId` 后轮询 `GET /task/{resultId}`。

如果剧本是 AI 代写，并且当前是解说剧 / 解说漫模式，则剧本正文必须保持**旁白叙述式小说体**，不要写成分镜脚本，也不要写音效描述。

### 第 4 步：智能分集

```bash
POST /service/workflow/project/step/next
{"userProjectId":"项目ID","step":"novel_opt","inputs":[]}
```

返回 `resultId` 后轮询任务。

### 第 5 步：等待角色图完成，再执行角色步骤

先调：

```bash
GET /service/workflow/comic/roles/{presetResourceId}
```

必须满足：

- `roles[].taskStatus == SUCCESS`
- `roles[].imgUrl` 非空

然后再调：

```json
POST /service/workflow/project/step/next
{
  "userProjectId": "项目ID",
  "step": "novel_extract_roles",
  "inputs": [
    {"type": "number", "name": "chapterNum", "value": 1},
    { ...来自 roles/voiceInputs 的 tts 输入对象... }
  ]
}
```

如果跳过这一步，常见报错是：

- `角色 [xxx] 图片未完成`

如果用户在这一阶段要求修改角色形象，则必须满足：

1. 当前 `workflow.currentStep == novel_extract_roles`
2. 先对目标角色发起新图生成
3. 等待新图在角色候选图列表里变成 `SUCCESS` 且 `imgUrl` 非空
4. 再显式应用这张新图
5. 最后重新读取角色列表，确认角色主图已切换，并把新的图片 URL 返回给用户

只生图不应用，不算修改完成。

### 第 6 步：等待 `sceneCaptionsTaskStatus=SUCCESS`，再执行智能分镜

先调：

```bash
GET /service/workflow/resource/comicPreset/{presetResourceId}
```

等待：

```text
chapters[chapterNum].sceneCaptionsTaskStatus == SUCCESS
```

补充说明：live 数据里，这类章节字段在短时间内可能先出现空值，再进入 `RUNNING / SUCCESS`。空值不一定代表异常，更不能据此提前推进下一步。

然后再调：

```json
POST /service/workflow/project/step/next
{
  "userProjectId": "项目ID",
  "step": "novel_scene_captions",
  "inputs": [
    {"type": "number", "name": "chapterNum", "value": 1},
    {"name": "imgGenTypeRef", "value": 1}
  ]
}
```

这个步骤返回的是 **`dialogTaskId`**，不是 `resultId`。

如果调早了，常见报错是：

- `该章节提取分镜场景任务未完成，请稍后再试`

### 第 7 步：轮询 `dialogTaskId` 后，还要再等 `sceneTaskStatus=SUCCESS`

轮询 `dialogTaskId` 成功后，仍然不能立刻推进到成片。

还需要再看：

```text
chapters[chapterNum].sceneTaskStatus == SUCCESS
```

补充说明：live 数据里，`sceneTaskStatus` 在一段时间内可能为空，再变成 `SUCCESS`；判断 readiness 时应继续轮询，而不是把空值直接当失败。

如果调早了，常见报错是：

- `该章节分镜图任务未完成，请稍后再试`

### 第 8 步：推进到成片步骤

等 `sceneTaskStatus=SUCCESS` 后，再调：

```json
POST /service/workflow/project/step/next
{
  "userProjectId": "项目ID",
  "step": "novel_chapter_scenes",
  "inputs": [{"type": "number", "name": "chapterNum", "value": 1}]
}
```

### 第 9 步：解析 storyboard 与 sceneId

用 `sceneTaskId -> task -> resourceId -> resource` 链路拿到：

- `storyboardId`
- `scenes[].id`
- `scenes[].image`

### 第 9.5 步：单场景图转视频（如用户明确要求）

先确认：

1. 当前步骤已处于 `novel_chapter_scenes`
2. `sceneTaskStatus == SUCCESS`
3. 使用完整 `sceneId`
4. 先取 `prompt/detail.video.imageId`，再从 `resources` 中找到对应 image 资源

推荐 payload 形态：

```json
{
  "sceneId": "完整 sceneId",
  "prompt": "来自 prompt/detail 的视频提示词",
  "cameraPrompt": "来自 prompt/detail 的镜头提示词",
  "model": "doubao-pro",
  "duration": "-1",
  "firstImage": "scene 当前基准分镜图 URL",
  "tailImage": "",
  "clarity": "720p",
  "imageId": "scene 当前基准 image 资源ID"
}
```

不要写成：

```text
firstImage = roles[].imgUrl
imageId = roles[].imageResourceId
```

因为这可能不会报错，却会生成错误语义的视频。

### 第 10 步：成片配置与合成

这里必须明确区分**成片设置阶段**和**视频合成阶段**。

#### 第 10A 步：进入 `novel_chapter_video` = 进入成片设置阶段

当章节从 `novel_chapter_scenes` 推进到 `novel_chapter_video` 后，用户并不是立刻就能看到最终成片。

live 测试里，这个阶段常见特征是：

- `workflow.currentStep = novel_chapter_video`
- `chapters[].currentStep = novel_chapter_video`
- `chapters[].currentSubStep = setting`

这表示当前处于**成片设置阶段**，此时需要准备并确认成片参数。

#### 第 10B 步：保存成片设置

顺序如下：

1. `POST /storyboard/prepareVideoComposite`
2. `GET /storyboard/getVideoSetting?userProjectId=...&type=2&chapterNum=1`
3. `POST /storyboard/saveVideoComposeConfig`

这一阶段主要对应：

- 封面设置
- 字幕设置
- 背景音乐
- 以及后续生成视频前需要确认的合成相关参数

在 live 测试中，`saveVideoComposeConfig` 成功后，章节仍可能保持：

- `currentSubStep = setting`

也就是说，**保存设置成功 ≠ 已经开始合成视频**。

#### 第 10C 步：点击“生成视频” = 真正发起视频合成

只有当调用：

4. `POST /project/step/action` with `step=novel_chapter_video`

之后，才是真正开始视频合成。

live 测试里，这一步会：

- 返回新的 `resultId`（视频合成任务 ID）
- 将章节的 `videoTaskId` 更新为新的任务 ID
- 让章节 `currentSubStep` 从 `setting` 进入 `video`

然后才需要：

5. 轮询返回的 `resultId`

live 自检里，这个最终合成任务可能会在 `QUEUED` 状态停留明显长于普通步骤；不要沿用前面普通任务的短轮询预算直接判超时。

#### 第 10D 步：只有合成任务成功后，用户才能看到最终成片

只有在视频合成任务 `SUCCESS` 后：

- 才会得到新的最终视频 `resourceId`
- 用户这时才能在平台里看到最终成片结果

换句话说：

- 进入 `novel_chapter_video` 不是最终成片完成
- 保存封面 / 字幕 / 背景音乐也不是最终成片完成
- **必须等视频合成任务成功后，最终成片才真正可见**

`saveVideoComposeConfig` 的可运行 payload 需要至少包含：

- `selectCover`
- `coverList`
- `selectCoverUrl`
- `selectMusicId`
- `selectTitleFont`
- `selectSubtitleFont`
- `title`
- `bgmVolume`
- `type`
- `chapterNum`
- `userProjectId`

#### 回退后必须重新合成

live 测试确认：

- 在 `novel_chapter_video` 合成成功后，章节会记录当前的 `videoTaskId`
- 一旦回退到 `novel_chapter_scenes` 再做调整，重新进入 `novel_chapter_video` 后，旧的合成结果不会自动变成新的最终成片
- 再次调用 `project/step/action` 时，会产生**新的** `videoTaskId`
- 最终也会生成**新的**视频 `resourceId`

这说明：

> **每次从成片步骤回退调整后，都必须重新合成视频。**

## 任务简报与逐步确认机制

Agent 的角色应该像“持续陪伴的智能漫剧助理”，而不是闷头执行器。

每完成一个用户可感知的重要任务，都应立即给用户一条简报，至少包含：

1. 刚完成了什么
2. 本步产出了什么关键结果
3. 下一步准备做什么
4. 如果需要用户决策，明确告诉用户要选什么
5. 明确询问用户：是否继续；如果当前步骤支持修改，再询问是否要修改当前结果

如果项目已创建，简报优先附上项目链接：

```text
https://ai.fun.tv/#/comic/multiple?projectId={projectId}
```

### 强制节奏要求

除纯技术性的中间动作外，Agent **不得**在用户没有确认的情况下自动把整条链路一路做完。

正确节奏是：

```text
完成一个大步骤
→ 详细汇报当前结果
→ 询问用户是否满意、是否继续下一步；如果当前步骤支持修改，再询问是否需要修改
→ 等用户确认后再继续
```

这里的“大步骤”至少包括：

- 创建项目完成
- 剧本写完 / 提交完成
- 角色整理完成
- 智能分镜完成
- 分镜图生成完成
- 图转视频完成
- 成片配置完成 / 合成完成

### 三个强制停点（不可跳过）

以下三个节点完成后，Agent 必须**立即停下来等待用户确认**，不能自动进入下一步：

1. **小说 / 剧本生成完成后**
   - 必须把完整或核心剧本内容回给用户
   - 明确询问：是否需要修改剧情、人物设定、语气风格
   - 用户确认后，才能继续提交剧本或进入后续步骤

2. **角色生成完成后**
   - 必须把每个角色的**角色图片的URL**返回给用户
   - 如果当前项目仍处于 `novel_extract_roles`（角色与配音）步骤，应主动询问用户是否需要修改某个角色的形象
   - 如果用户要求修改，必须先生成新图、等待新图完成、再显式应用新图；只有主图真正切换后，才算修改完成
   - 修改完成后，必须把新的角色图片 URL 返回给用户
   - 用户确认无误后，才能继续进入场景 / 分镜相关步骤

3. **场景 / 分镜生成完成后**
   - 必须把场景的**场景描述**返回给用户
   - 如果有可展示的分镜图，也应一并返回或说明项目链接中的查看方式
   - 如果用户对一个或多个场景不满意，应允许在 `novel_chapter_scenes` 步骤继续调整单场景的图片提示词或视频提示词后重新生成
   - 必须主动询问用户：
     1. 是否要将分镜图继续转为视频
     2. 还是直接进入“成片”界面，用当前分镜图直接合成
   - 用户明确选择后，才能继续进入图转视频或成片步骤

### 角色确认时必须包含的内容

角色确认阶段的回报，至少要包含：

- 角色名称
- 角色图片

不能只说“角色已生成完成”，而不把角色图片回给用户。

### 角色确认时的修改规则

角色形象修改只允许在 **角色与配音** 步骤执行。

角色确认阶段：

- 可以询问“是否要修改角色形象”
- 但前提是当前仍停留在 `novel_extract_roles`
- 如果项目已推进到后续步骤，就不能再按角色改图链路修改
- 只要执行了修改，就必须等待新图完成、显式应用，并把新的图片 URL 返回给用户

### 场景确认时必须包含的内容

场景确认阶段的回报，至少要包含：

- 场景名称或场景编号
- 场景描述
- 如已生成可视化结果，可附分镜图或项目链接查看方式

不能只说“场景已生成完成”，而不把场景描述回给用户确认。

### 场景不满意时的调整规则

如果用户对某一个或多个 scene 的结果不满意，Agent 应先判断问题属于哪一类：

- **图片本身不对**：调整 `sceneDescription + prompt` 后重生图
- **图片基本正确，但视频表现不对**：调整 `prompt(动作) + cameraPrompt(运镜)` 后重生视频

#### 分镜图重生图

重生图时，真实提示词由两部分共同组成：

- `sceneDescription`
- `prompt`

其中 `prompt` 里可能包含：

```text
@[人物](id:xxxx)
```

这类 live 人物引用用于保持角色一致性，不应随意删除。

#### 图转视频

图转视频时应区分：

- `prompt` = 动作
- `cameraPrompt` = 运镜

这里不要再使用图片侧的 `@[人物](id:xxxx)` 结构，而应直接写纯文本动作和镜头描述。

#### 多模态模型的可选增强

如果当前 Agent / 模型具备多模态看图能力，可在每次重生图或重生视频后先查看当前结果，再决定是否继续微调：

- 图片侧优先检查当前 `selected=true` 的 scene image
- 视频侧优先检查当前视频资源的 `videoCover`

然后再针对问题定向修改 prompt，而不是盲目重试。

### 分镜图完成后的下一步必须让用户二选一

当分镜图已经生成完成时，Agent 不能直接默认进入成片。

必须主动问用户：

1. **是否需要将分镜图转为视频**（会增加梦想值消耗）
2. **还是直接进入成片界面合成**（默认更省）

只有拿到这个选择后，才能继续往下执行。

### 哪些动作可以不单独等待确认

以下仍然属于同一步内部的技术动作，可以合并在一步里完成：

- 轮询任务状态
- 读取 `comicPreset` / `storyboard` / `task`
- 解析 `sceneId` / `storyboardId`
- 回退到分镜图步骤
- 读取 `select-options`

但是一旦形成了新的用户可感知结果，就必须停下来等确认。

## 生图 / 生视频约束

生图或生视频必须在 **分镜图步骤** 下执行，不能在成片步骤直接执行。

检查顺序：

1. `GET /project/{projectId}` 看 `workflow.currentStep`
2. 如果当前是 `novel_chapter_video`，先 `POST /project/step/prev`
3. 回到 `novel_chapter_scenes` 后再继续

live 测试确认：

- 回退成功后，`workflow.currentStep` 会变成 `novel_chapter_scenes`
- 章节的 `currentSubStep` 可能仍保留为 `video`

这不代表异常。真正要继续操作前，应继续确认：

- `sceneTaskStatus == SUCCESS`
- scene 当前基准 image 资源可用

## 梦想值规则

### 默认不消耗梦想值的推荐流程

默认流程是：

```text
分镜图生成完成 → 直接配置成片 → 合成最终视频
```

但这不意味着 Agent 可以自动一路执行到底。

正确做法是：

```text
分镜图生成完成
→ 先向用户展示分镜结果并询问是否修改 / 是否继续
→ 用户确认后再进入成片配置与合成
```

### 需要用户确认的高消耗操作

以下操作会消耗梦想值，必须先明确征得用户同意：

- 批量转视频 `check/batchAiVideo` 对应的真实转视频动作
- 单张图转视频 `scene/ai/video`
- 重绘分镜图 `scene/ai/image`

### `check/batchAiVideo` 只是查询，不是执行

它返回的是：

- `noVideoCount`
- 当前还有多少画面没有转动态

不要把这个接口误认为“已经开始批量转视频”。

## 常见问题与解决方案

### 1. Token 过期

- 错误：`401` / `未登录或登陆状态已失效`
- 解决：重新获取 token，更新 `config/.env`

### 2. 角色步骤失败

- 错误：`角色 [xxx] 图片未完成`
- 原因：角色图还没生成完，或者没有传 live `tts` 输入
- 解决：先检查 `GET /comic/roles/{presetResourceId}`，等角色就绪后把 `voiceInputs[0]` 一起提交

### 3. 智能分镜步骤失败

- 错误：`该章节提取分镜场景任务未完成，请稍后再试`
- 解决：等待 `sceneCaptionsTaskStatus=SUCCESS`

### 4. 推进成片步骤失败

- 错误：`该章节分镜图任务未完成，请稍后再试`
- 解决：等待 `sceneTaskStatus=SUCCESS`

### 5. `sceneUuid` 误用

- 错误：`分镜场景资源不存在`
- 原因：把短 ID 当成完整 `sceneId`
- 解决：按 `sceneTaskId -> storyboardId -> scenes[].id` 解析完整 sceneId

### 6. 图转视频拿错图片来源

- 现象：接口可能返回 `200 success`，但生成出来的视频内容与当前分镜不一致
- 原因：把 `roles[].imgUrl` / `roles[].imageResourceId` 当成了 `scene/ai/video` 的 `firstImage` / `imageId`
- 解决：必须改用 scene 当前基准分镜图资源（优先 `prompt/detail.video.imageId` 对应的 image 资源）

### 7. 视频配置保存失败

- 错误：`请选择封面`
- 原因：`saveVideoComposeConfig` 缺少 `coverList` / `selectCover` / `selectCoverUrl`
- 解决：先取 `getVideoSetting`，再按返回内容构造完整 payload

## 代码与参考文档

- `scripts/api-client.sh`：可复用的 API 工具函数与等待逻辑
- `examples/create-comic.sh`：按真实后端行为执行的完整自检流程
- `references/01-project-management.md`：项目创建与配置选项
- `references/02-script-management.md`：各步骤请求体与隐藏章节状态
- `references/03-character-management.md`：角色图状态与 `tts` 输入
- `references/05-storyboard-management.md`：storyboard / sceneId / 分镜资源
- `references/06-video-generation.md`：成片配置、批量视频检查与合成
- `references/07-task-status.md`：task 轮询与章节级隐藏状态
- `references/09-error-codes.md`：常见错误与处理方式
- `references/10-models-and-config.md`：实时配置与 workflow 总览
- `references/11-best-practices.md`：面向 Agent 的执行建议
