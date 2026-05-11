---
name: mm-music-expert
description: Create music with MiniMax music models (music-2.5+, music-2.5). Use when generating songs, instrumental tracks, or chanting from lyrics and style prompts via MiniMax Music Generation API. Guides music novices through an interactive workflow to produce professional-quality music.
---

# MiniMax Music Expert

Generate music using MiniMax Music Generation API. Default model: **music-2.5+** (recommended).
This skill is designed to help **music novices** create professional-quality music through guided interaction.

## Environment Setup

```bash
export MINIMAX_MUSIC_API_KEY="your_api_key"
```

---

## Agent Workflow (MUST FOLLOW)

When a user requests music creation, **always** follow this 4-step interactive workflow. Do NOT skip steps or jump directly to generation.

### Step 1: Understand & Clarify Requirements

Analyze the user's input and identify which dimensions are already covered vs. missing. Then ask targeted follow-up questions to fill the gaps.

**Dimension checklist** — check which are provided, ask about the rest. Each question MUST provide lettered options (A/B/C/...) for the user to choose from:

| Dimension | Question with options |
|-----------|---------------------|
| **Type** | "这首歌的类型？ **A.** 有人声演唱的歌曲 **B.** 纯音乐/背景音乐(无人声) **C.** 哼唱/吟唱(旋律人声无歌词)" |
| **Genre/Style** | "你喜欢什么音乐风格？ **A.** 流行 **B.** 摇滚 **C.** 民谣 **D.** 电子/EDM **E.** 嘻哈/说唱 **F.** 爵士 **G.** 古风/中国风 **H.** R&B **I.** 其他(请描述)" |
| **Mood/Emotion** | "希望传达什么情绪？ **A.** 欢快活泼 **B.** 温柔抒情 **C.** 忧伤感怀 **D.** 激昂热血 **E.** 治愈放松 **F.** 大气磅礴/史诗感 **G.** 浪漫甜蜜 **H.** 其他(请描述)" |
| **Scene/Use case** | "这首歌打算用在什么场景？ **A.** 短视频/Vlog BGM **B.** 个人收藏/送人 **C.** 游戏/动画 **D.** 咖啡馆/餐厅 **E.** 婚礼/庆典 **F.** 运动/健身 **G.** 其他(请描述)" |
| **Tempo/Rhythm** | "节奏方面的偏好？ **A.** 慢速抒情(60-80 BPM) **B.** 中速舒缓(80-110 BPM) **C.** 中快轻快(110-130 BPM) **D.** 快速动感(130-160 BPM) **E.** 不确定，交给你来定" |
| **Instruments** | "有没有想要的乐器？ **A.** 钢琴为主 **B.** 吉他(民谣/电吉他) **C.** 中国民乐(笛子/琵琶/古筝/二胡) **D.** 弦乐(小提琴/大提琴) **E.** 电子合成器 **F.** 管乐(萨克斯/小号) **G.** 不确定，根据风格搭配 **H.** 其他(请描述)" |
| **Vocal** | "人声方面？(纯音乐跳过) **A.** 温柔女声 **B.** 有力女声 **C.** 温柔男声 **D.** 有力男声 **E.** 烟嗓/沙哑 **F.** 不确定，交给你来定" |
| **Lyrics** | "歌词方面？(纯音乐跳过) **A.** 我已有歌词 **B.** 我给主题/关键词，你来写 **C.** 全部交给AI自动生成" |
| **Dynamic Arc** | "歌曲的情绪走向？ **A.** 由浅入深，慢慢推向高潮 **B.** 开头就炸裂，全程高能 **C.** 先抑后扬(安静开头→爆发副歌) **D.** 起伏交替(安静→爆发→安静→更大爆发) **E.** 全程平稳舒缓 **F.** 不确定，交给你来编排" |
| **Reference** | "有没有喜欢的参考？(optional) **A.** 有，类似某个歌手/歌曲(请说明) **B.** 没有特别参考" |

**Rules:**
- 不要一次抛出所有问题。根据用户已提供的信息，只问**缺失的关键维度**（通常 2-4 个问题）
- 每个问题**必须带字母选项**(A/B/C/...)，降低用户决策成本
- 选项末尾提供"其他"或"交给你来定"的兜底选项，避免用户被选项限制
- 如果用户的需求已经很明确（覆盖了 Type + Genre + Mood + 至少一个其他维度），可以直接进入 Step 2

**示例交互：**
> 用户: "帮我做一首关于杭州的歌"
> Agent: "好的！关于这首杭州之歌，我还想确认几个方面，你可以直接回复选项字母：
>
> 1. 🎵 **风格**：**A.** 中国风民谣 **B.** 流行 **C.** 古风 **D.** R&B **E.** 其他
> 2. 🎤 **情绪**：**A.** 温柔抒情 **B.** 大气磅礴 **C.** 欢快明朗 **D.** 忧伤怀旧
> 3. 🎶 **人声**：**A.** 温柔女声 **B.** 有力女声 **C.** 温柔男声 **D.** 有力男声
> 4. 🎭 **情绪走向**：**A.** 由浅入深慢慢推向高潮 **B.** 先抑后扬 **C.** 全程舒缓 **D.** 起伏交替
> 5. ✍️ **歌词**：**A.** 我已有歌词 **B.** 我给主题你来写 **C.** AI自动生成
>
> 直接回复如 `1A 2B 3A 4A 5B` 即可！"

### Step 2: Design Song Blueprint & Present Draft

**This is the most important step.** Do NOT write a flat prompt. First design a **Song Blueprint** (段落蓝图) that plans each section's musical characteristics, then derive the prompt and lyrics from it.

#### Step 2a: Create Song Blueprint

Based on gathered requirements, plan the section-by-section musical journey. Each section should have distinct characteristics.

**Blueprint format:**

```
🎼 **歌曲蓝图**

| 段落 | 情绪/能量 | 乐器/编曲 | 人声表现 | 制作特点 |
|------|-----------|-----------|----------|----------|
| [Intro] | ... | ... | ... | ... |
| [Verse 1] | ... | ... | ... | ... |
| [Pre Chorus] | ... | ... | ... | ... |
| [Chorus] | ... | ... | ... | ... |
| ... | ... | ... | ... | ... |
```

**Blueprint example** (用户需求: "一首关于杭州的中国风民谣，温柔开头，副歌大气"):

```
🎼 **歌曲蓝图**

| 段落 | 情绪/能量 | 乐器/编曲 | 人声表现 | 制作特点 |
|------|-----------|-----------|----------|----------|
| [Intro] | 宁静悠远 ⚡① | 古筝独奏琶音 | — | 空间感大，远处水声质感 |
| [Verse 1] | 细腻叙述 ⚡② | +笛子旋律，轻拨琵琶 | 温柔低吟，呼吸感 | 亲密感，少混响 |
| [Verse 2] | 情感渐浓 ⚡③ | +二胡加入，节奏轻启 | 声线渐开，带感情 | 开始加宽声场 |
| [Pre Chorus] | 蓄势待发 ⚡⑤ | 弦乐铺底渐强，鼓点加入 | 力度上升，情绪推动 | 渐强(crescendo) |
| [Chorus] | 大气磅礴 ⚡⑧ | 全编制爆发：弦乐+鼓+笛+琵琶 | 高亢嘹亮，饱满和声 | "音墙"，宽广声场 |
| [Bridge] | 回归内省 ⚡③ | 仅钢琴+古筝 | 轻声吟唱 | 突然安静，对比反差 |
| [Chorus] | 最终爆发 ⚡⑨ | 全编制+合唱层叠 | 全力释放，高音 | 最高能量 |
| [Outro] | 渐归平静 ⚡② | 古筝回归独奏 | — | 渐弱收尾 |
```

⚡① ~ ⚡⑩ = energy level, 用于可视化段落间的能量变化曲线。

**Blueprint design principles:**
- **段落间必须有对比**：相邻段落的能量/乐器/人声至少有一项明显不同
- **能量曲线要有起伏**：避免全程同一能量级。典型曲线：低→中→高→低→最高→低
- **Chorus 必须是能量峰值**：确保副歌和主歌之间有显著的编曲差异
- **Bridge 通常是"呼吸空间"**：在两次 Chorus 之间提供反差

#### Step 2b: Derive Prompt from Blueprint

将蓝图中的信息转化为 prompt。好的 prompt 需要**同时描述整体基调和段落间的动态变化**。

**Prompt construction formula:**
```
[整体风格/BPM] + [人声描述 + 段落间变化] + [核心乐器] + [动态弧线描述] + [声场/制作特点]
```

**Example** (based on the 杭州 blueprint above):
```
A poetic and cinematic Chinese folk pop at 78 BPM, featuring a tender female vocal that transitions from intimate whispering in the verses to powerful soaring belting in the choruses with layered harmonies. The arrangement builds from a solo guzheng intro, gradually adding dizi (bamboo flute), pipa, and erhu through the verses, swelling to a full orchestral "wall of sound" with strings and percussion in the choruses, before retreating to a quiet guzheng outro. The production shifts from a dry, intimate space in the verses to a wide, reverberant arena soundscape in the choruses.
```

Key: The prompt explicitly describes **what changes between sections** — not just a flat list of attributes.

#### Step 2c: Write Lyrics with Section Directions

Write lyrics using **annotated structure tags** and **parenthetical directions** to reinforce the blueprint:

```
[Intro]
（古筝琶音，空灵悠远）

[Verse 1: 温柔低吟]
西湖 烟雨 朦胧了 谁的眼
断桥 残雪 化作 心头的暖

[Verse 2: 情感渐浓]
（笛声加入，轻柔的鼓点）
三潭 映月 点亮了 千年夜
灵隐 钟声 唤醒 梦中的蝶

[Pre Chorus: 情绪递进]
（弦乐渐强 / Rising strings）
这片土地 承载了 多少故事
每一寸 都是 我的根

[Chorus: 大气爆发]
（Full band kicks in / 全编制爆发）
杭州 我的杭州
你是 我心中 永远的歌
...

[Bridge: 回归平静]
（Music drops to piano and guzheng only / 仅剩钢琴与古筝）
闭上眼 你还在那里
...

[Chorus: 最终高潮]
（Maximum energy / 最高能量，加入合唱层）
杭州 我的杭州
...

[Outro: 渐弱收尾]
（古筝独奏，渐弱 / Guzheng solo, fading out）
```

#### Step 2d: Present Complete Draft

Combine all above into the final presentation:

```
📋 **生成方案**

**模式**：Standard Song

🎼 **歌曲蓝图**：
[the blueprint table]

**Prompt**：
[the full prompt — with dynamic arc description]

**歌词**：
[the full lyrics — with annotated tags and parenthetical directions]

**说明**：[1-2 sentences on creative choices]

---
请确认是否满意，或告诉我需要调整的地方（如某段落的情绪、乐器、歌词等）。
```

**Rules:**
- **Always create the blueprint first**, then derive prompt and lyrics from it
- Prompt must describe **section transitions**, not just a flat style
- Lyrics must use **annotated structure tags** (e.g., `[Chorus: 大气爆发]`) and **parenthetical directions** (e.g., `（Full band kicks in）`) to control each section's sound
- Show the complete blueprint, prompt, and lyrics — never hide details
- Wait for explicit user confirmation before proceeding to Step 3

### Step 3: Generate Music

After user confirms (or after applying their revisions and getting re-confirmation):

1. Determine the output file name from context (e.g., `./audio/杭州之歌.mp3`)
2. Run the generation command:

```bash
python scripts/generate_music.py \
  --lyrics "<final_lyrics>" \
  --prompt "<final_prompt>" \
  --output ./audio/<filename>.mp3
```

For instrumental mode, add `--is-instrumental true` and omit `--lyrics`.
For auto-lyrics mode, add `--lyrics-optimizer true` and omit `--lyrics`.

3. Inform user that generation is in progress (API call may take 30-120 seconds)

### Step 4: Post-Generation Feedback

After the audio file is generated:

1. Tell the user the file location and invite them to listen
2. Ask for feedback:

```
🎵 音乐已生成！文件保存在：`./audio/<filename>.mp3`

请试听后告诉我你的感受：
- ✅ 满意，完成
- 🔄 需要调整（请告诉我具体想改什么，比如节奏太快、想换个风格、歌词某处要改等）
```

3. If user requests changes:
   - Analyze what needs modification (prompt, lyrics, or both)
   - Return to **Step 2** with the revised draft
   - Repeat until user is satisfied

**Common revision patterns:**

| User feedback | Action |
|---------------|--------|
| "节奏太快/太慢" | Adjust BPM in prompt |
| "风格不对" | Revise genre/style keywords in prompt |
| "人声不喜欢" | Adjust vocal description in prompt |
| "歌词某段要改" | Modify specific lyrics section |
| "想加点 rap" | Add `[Verse: Rap]` section in lyrics, update prompt |
| "乐器不对" | Revise instrument list in prompt |
| "感觉太单调" | Add dynamic arc description, enrich structure tags with annotations |
| "想要更有层次感" | Add parenthetical production directions in lyrics, describe section transitions in prompt |

---

## Model & Mode Reference

### Model Differences

| Feature | music-2.5 | music-2.5+ (recommended) |
|---------|-----------|--------------------------|
| Standard song (with lyrics) | ✅ lyrics required | ✅ lyrics required |
| Pure music (`is_instrumental`) | ❌ not supported | ✅ prompt required, lyrics optional |
| Auto-generate lyrics (`lyrics_optimizer`) | ✅ | ✅ |
| `prompt` field | Optional [0, 2000] chars | Optional for songs; **Required** [1, 2000] for instrumental |
| `lyrics` field | **Required** [1, 3500] chars | **Required** for songs; optional for instrumental |

### Generation Modes

| Mode | When to use | Key Args |
|------|-------------|----------|
| **Standard Song** | User has/wants lyrics + singing | `--lyrics` + `--prompt` |
| **Pure Music** | "纯音乐" / "instrumental" / "背景音乐" / "无人声" | `--is-instrumental true` + `--prompt` |
| **Chanting** | "哼唱" / "吟唱" / "humming" | `--lyrics` (syllables) + `--prompt` |
| **Auto Lyrics** | User wants AI to write lyrics | `--lyrics-optimizer true` + `--prompt` |

---

## Prompt Crafting (Best Practices)

Prompt 控制音乐的整体风格、情绪和制作方向。**好的 prompt 不是扁平的属性罗列，而是描述音乐如何在段落间变化。**

### 核心维度（必须覆盖）

| 维度 | 说明 | 示例 |
|------|------|------|
| **Genre + Era/Region** | 具体风格 + 时代或地域 | `1980s J-Rock`, `Chinese folk R&B`, `昭和年代Disco` |
| **BPM** | 明确的节拍速度 | `92 BPM`, `136 BPM`, `140 BPM` |
| **Vocal + Transition** | 性别、音色 + **段落间如何变化** | `soft airy female vocal that transitions from intimate whispering in verses to powerful soaring belting in choruses` |
| **Instruments + Layering** | 核心乐器 + **各段落如何叠加/退出** | `builds from solo guzheng, adding dizi and pipa through verses, swelling to full orchestral in choruses` |
| **Mood** | 2-3 个情绪描述词 | `passionate, nostalgic, hopeful` |
| **Dynamic Arc** | **段落间的能量演进曲线** | `from intimate dry verse into wide reverberant chorus, retreating to quiet bridge before final explosive chorus` |

### 进阶维度（提升精度）

| 维度 | 说明 | 示例 |
|------|------|------|
| **Production/Mix** | 混音风格、**段落间空间变化** | `dry intimate space in verses, wide reverberant arena soundscape in choruses` |
| **Sound Design** | 特定风格的声学特征 | `rock saturation`, `80s Minneapolis sound`, `modern electronic wide transients` |
| **Scene/Use case** | 使用场景 | `anime theme`, `club/party`, `coffee shop BGM` |
| **Avoid** | 排除元素 | `no autotune`, `avoid heavy reverb`, `no trap hi-hats` |

### Prompt 构建公式（推荐）

```
[整体风格 + BPM] + [人声描述 + 段落间变化] + [乐器编排 + 段落间叠加/退出] + [动态弧线] + [声场/制作变化]
```

**English template (highest precision):**
```
A [mood] [BPM] [genre] track featuring a [vocal] that [transitions from X in verses to Y in choruses], with arrangement building from [sparse intro instruments] through [verse additions] to [full chorus instrumentation], [bridge contrast], before [final chorus climax]. Production shifts from [verse sound] to [chorus sound].
```

**Example:**
```
A poetic and cinematic Chinese folk pop at 78 BPM, featuring a tender female vocal that transitions from intimate whispering in the verses to powerful soaring belting in the choruses with layered harmonies. The arrangement builds from a solo guzheng intro, gradually adding dizi, pipa, and erhu through the verses, swelling to a full orchestral "wall of sound" with strings and percussion in the choruses, retreating to quiet guzheng in the bridge, before a final explosive chorus with choir layers. Production shifts from dry intimate space in verses to wide reverberant arena soundscape in choruses.
```

**Chinese description template:**
```
78 BPM 的诗意中国风民谣，温柔女声演唱。主歌低吟浅唱、气息感十足，到副歌转为高亢嘹亮的全力释放。编曲从古筝独奏开头，主歌逐渐加入笛子、琵琶，到副歌时弦乐、鼓点全编制爆发形成"音墙"，Bridge回归古筝独奏的宁静，尾声再次爆发后古筝收尾渐弱。
```

**Simple tag template (for straightforward requests):**
```
[风格], [情绪], [BPM], [乐器], [人声类型]
```
示例: `Pop,中国风R&B` / `Afro House,Tropical House` / `流行，女生，舒缓`

### 常见用户需求 → Prompt 转换

| 用户需求 | Prompt 方向 |
|----------|------------|
| "主旋律大气磅礴" | prompt 描述动态弧线: `arrangement builds from gentle opening to massive orchestral chorus with powerful brass, strings and timpani, creating an epic arena soundscape` |
| "副歌加一段 rap" | prompt: `with melodic rap in verses transitioning to anthemic singing in choruses`; 歌词: `[Verse 1: Rap]` + `[Chorus: Singing]` |
| "歌颂我的家乡·杭州" | 主题在歌词；prompt 描述风格+动态: `Chinese folk pop, building from intimate solo guzheng verse to full ensemble chorus` |
| "使用笛子、琵琶等民乐" | prompt 描述乐器如何分布: `featuring dizi (bamboo flute) as verse melody, pipa as rhythmic texture, erhu joining in bridge, full silk-bamboo ensemble in chorus` |
| "复古迪斯科" | `复古迪斯科风格，主歌以放克吉他切分律动为主，副歌管弦与合成器全面加入，庆典般的能量爆发` |
| "治愈系轻音乐" | `healing ambient, starting with solo piano, gradually layering soft strings and gentle pads, building warmth` + `--is-instrumental true` |
| "开头要炸裂" | `explosive intro with heavy bass and drum impact, settling into groove for verses, building back to maximum energy chorus` |
| "想要有层次感" | prompt 显式描述每段的乐器增减: `verse: acoustic guitar + light drums → pre-chorus: add synth pads + bass → chorus: full band with layered vocals → bridge: strip to piano only` |

---

## Lyrics Writing (Best Practices)

### 结构标签

官方支持的 14 种标签：

```
[Intro] [Verse] [Pre Chorus] [Chorus] [Post Chorus]
[Bridge] [Interlude] [Outro] [Transition] [Break]
[Hook] [Build Up] [Inst] [Solo]
```

### 结构标签高级用法

**编号区分**：用编号区分不同段落，使每段有不同表现：
```
[Verse 1]
街边红灯 摇曳 破了 暮色
[Verse 2]
玉米 粒粒 颗颗 都是 地道
```

**注释标签**：在标签后用冒号加注释，指导该段落的演绎方式：
```
[Intro Hook: Heavy Hanmai Style & 808 Drop]
[Verse 1: Aggressive Rap]
[Pre-Chorus: Build Up]
[Chorus: Maximum Energy]
[Bridge: Comical Trombone Solo]
[Outro: Speed Up]
[Drop / Chorus]
```

### 段落对比编排（关键：避免歌曲单调）

**核心原则**：每个段落的歌词中应通过注释标签 + 括号指令明确告诉模型这一段的音乐特征，确保相邻段落之间产生对比。

**完整示例**（注意每个段落的括号指令如何控制乐器和能量的变化）：
```
[Intro]
（古筝独奏琶音，空旷悠远）

[Verse 1: 温柔叙述]
（轻柔的笛子旋律加入，亲密的混音空间）
西湖 烟雨 朦胧了 谁的眼
断桥 残雪 化作 心头的暖

[Pre Chorus: 情绪递进]
（弦乐渐强，鼓点轻启 / Strings building, drums entering）
这片土地 承载了 多少故事

[Chorus: 全力爆发]
（Full band kicks in / 全编制爆发，宽广音场）
杭州 我的杭州
你是我心中 永远的歌

[Bridge: 突然安静]
（Music drops to piano only / 仅剩钢琴，安静的呼吸空间）
闭上眼 你还在那里

[Chorus: 最终高潮]
（Maximum energy, choir layers added / 最高能量，加入合唱）
杭州 我的杭州
```

**对比维度清单**（至少变化 1-2 项）：
| 维度 | Verse (低能量) | Chorus (高能量) |
|------|---------------|----------------|
| 乐器数量 | 1-2 件 | 全编制 |
| 音场宽度 | 亲密/干 | 宽广/混响 |
| 人声力度 | 低吟/轻唱 | 高亢/嘹亮 |
| 节奏密度 | 稀疏/无鼓 | 密集/强劲鼓点 |
| 动态层次 | 轻 (p/mp) | 强 (f/ff) |

### 括号指令（关键技巧）

在歌词中使用 `()` 或 `（）` 插入演奏/音效/人声指令，模型会尝试执行：

**乐器控制：**
```
[Intro]
（琵琶琶音）
[Outro]
（二胡拉出一个帅气的尾音）
（鼓声重击收尾）
```

**音效/声音设计：**
```
(Sound of glass breaking / 玻璃破碎声)
(Phone ringing sound / 电话铃声)
(Sudden change to 8-bit game sound / 突然变成红白机音效)
(Abrupt silence / 突然安静)
(Sound of a chicken / 一声鸡叫): 咯咯哒？
```

**人声技巧：**
```
(Robotic Voice / 机械音)
(Super fast flow / 极快语速)
(Pitch rising higher and higher / 音调越来越高)
(Deep Voice / 深沉男声)
(Gang Vocals, Everyone shouting)
(Manic laughter)
```

**编曲/动态：**
```
(Heavy Bass kicks in / 重低音爆发)
(Rising synth / 情绪递进)
(Music stops briefly, only Trombone playing funny melody)
(BPM increases significantly to Happy Hardcore speed)
(Fading out with beat / 渐弱)
(Maximum Volume / 最大音量)
(Beat returns - Manyao Style)
```

### 拟声词/象声词

在歌词中直接写拟声词可产生特殊音效效果：
```
Boom Boom Boom!
A-Ba A-Ba A-Ba A-Ba!
Bi-bu Bi-bu Bi-bu Bi-bu (救护车音效)
Womp Womp Womp
嗡——啪!
```

### 中文空格分词（节奏控制）

中文歌词中加空格控制字词的演唱节奏和断句：
```
街边红灯 摇曳 破了 暮色          ← 空格控制断句节奏
半城 烟火 尽是 诱人 醇香
```
对比无空格版本：
```
街边红灯摇曳破了暮色              ← 模型自行断句，节奏不可控
```

### 双语歌词

中英混合歌词可产生跨文化效果：
```
霓虹灯在闪烁 (Flash, Flash)
别管现在几点钟 (Tik, Tok)
Zuo! You! Shang! Xia! (左! 右! 上! 下!)
```

### 典型歌曲结构模板

**标准流行曲：**
```
[Intro]
[Verse 1]
[Pre Chorus]
[Chorus]
[Verse 2]
[Bridge]
[Chorus]
[Outro]
```

**EDM/舞曲：**
```
[Intro]
[Verse 1]
[Pre-Chorus: Build Up]
[Drop / Chorus]
[Verse 2]
[Build Up]
[Drop / Chorus: Maximum Energy]
[Outro]
```

**带 Rap 的歌曲：**
```
[Intro]
[Verse 1: Rap]
[Pre Chorus]
[Chorus]
[Verse 2: Melodic Rap]
[Bridge]
[Chorus]
[Outro]
```

---

## Script Reference

| File | Purpose |
|------|---------|
| `scripts/generate_music.py` | Main CLI: lyrics + prompt → audio file |
| `scripts/utils_audio.py` | Hex decoding, file saving, URL download |

### Key CLI Arguments

| Arg | Default | Description |
|-----|---------|-------------|
| `--lyrics` | — | Song lyrics (required unless instrumental or lyrics-optimizer) |
| `--prompt` | — | Style/scene description (required for instrumental) |
| `--model` | `music-2.5+` | Model name |
| `--is-instrumental` | false | Pure music mode (music-2.5+ only) |
| `--lyrics-optimizer` | false | Auto-generate lyrics from prompt |
| `--output` | — | Output file path (required) |
| `--output-format` | `url` | Response format: `hex` or `url` |
| `--format` | — | Audio codec: `mp3`, `wav`, `pcm` |
| `--sample-rate` | — | 16000 / 24000 / 32000 / 44100 |
| `--bitrate` | — | 32000 / 64000 / 128000 / 256000 |
| `--stream` | false | Streaming mode (hex only) |
| `--aigc-watermark` | false | Append watermark (non-stream only) |
| `--download` | false | Download when output-format=url |

## API Payload Quick Reference

**Standard Song:**
```json
{
  "model": "music-2.5+",
  "prompt": "indie folk, melancholic",
  "lyrics": "[Verse]\n街灯微亮晚风轻抚\n影子拉长独自漫步\n[Chorus]\n推开木门香气弥漫",
  "audio_setting": { "sample_rate": 44100, "bitrate": 256000, "format": "mp3" }
}
```

**Pure Music (music-2.5+ only):**
```json
{
  "model": "music-2.5+",
  "prompt": "coffee shop, ambient, relaxing, piano",
  "is_instrumental": true
}
```

**Auto Lyrics:**
```json
{
  "model": "music-2.5+",
  "prompt": "upbeat pop, summer vibes",
  "lyrics_optimizer": true
}
```

For full API details, see `references/minimax_music_api.md`.
