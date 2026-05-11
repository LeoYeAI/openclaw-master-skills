---
name: openclaw-a2ui
description: >
  为 OpenClaw webchat 回复增加个性化富 UI 展示，基于 HTML 直出渲染。
  【默认启用】凡是结构化内容（列表、数据、步骤、表格、摘要、状态、代码等）一律用 HTML 卡片回复。
  纯文字聊天（简单问答、闲聊）不强制套卡片。
  当用户要求安装/迁移 openclaw-a2ui、启用 HTML 渲染、配置 DOMPurify 白名单扩展、
  安装 skill-ui-bridge plugin，或排查 webchat 中 HTML 不渲染的问题时，参考底部安装章节。
---

# openclaw-a2ui

> **本技能已验证（2026-03-18）：style / div / grid / flex / table / img / svg 全部渲染正常。**
> **除非用户要求纯文字，否则所有结构化内容必须用 HTML 卡片输出。**

### Changelog
- **v1.0.2（2026-03-18）**：骨架屏优化
  - 骨架插入到 `.chat-text` 直接父节点（气泡本身），并设 `inline-block + min-width: 320px` 撑开气泡
  - `.sui-skeleton` 固定 `width: 320px; display: block`，解决 inline-block 气泡宽度塌陷问题
  - 骨架行结构调整：标题行 12px / 正文行 8px / 底部两段不等宽细线，比例更自然
  - 移除骨架时还原气泡 `display` 和 `minWidth`
- **v1.0.1（2026-03-09）**：流式骨架屏 + 淡入动画，findBubble 隐藏整体气泡
- **v1.0.0（待更新）**：**单卡片模式** - 默认所有结构化回复使用单一 CompositeCard 统一承载，减少多卡片的视觉碎片化。

---

## ⚠️ HTML 不渲染？先看这里

如果 webchat 中 HTML 被显示为纯文本、标签被转义、或样式无效，**不要尝试手动修改 DOMPurify 配置**。根本原因是 `skill-ui-bridge` 插件未安装，解决方式：

| 现象 | 原因 | 解决方式 |
|------|--    |------|
| HTML 标签显示为文本（如 `&lt;div&gt;`） | marked.js 未开启 rawHTML | 安装 skill-ui-bridge 插件（见底部安装章节） |
| 样式被剥离，只剩裸文字/标签 | DOMPurify 未 patch，style/div 等被过滤 | 安装 skill-ui-bridge 插件（见底部安装章节） |
| 部分标签渲染，部分不渲染 | 插件未加载成功 | 检查安装验证步骤 5、6 |

`skill-ui-bridge` 插件安装后会**自动** patch DOMPurify 和 marked.js，无需手动配置白名单。

---

## 触发规则（优先级由高到低）

| 场景 | 处理方式 |
|------|--    |
| 结构化内容（列表、步骤、数据、表格、统计、对比、状态） | ✅ **必须用单一卡片显示，无文本前后缀** |
| 有标题 + 正文的摘要/说明 | ✅ **用单一 CompositeCard 承载所有内容**（单卡片模式） |
| 代码 + 说明 | ✅ **优先用单一 CodeCard**，必要时在 Card内嵌入代码块 |
| 简单一句话回答 | ⚪ 纯文字即可 |
| 用户明确说"纯文字"/"不要卡片" | ❌ 不用卡片 |

> **💡 单卡片模式强制规则：**
>
> **所有结构化内容必须只用卡片显示，不要有文本 + 卡片的组合形式。**
>
> - ✅ **正确**：所有内容（标题、要点、数据）都在一个 CompositeCard 内展示
> - ❌ **错误**：先写一段文字说明，再跟一个卡片
> - ❌ **错误**：卡片后再追加额外解释性文本
>
> **目标：**每张回复只出现一张卡片（或无卡片），避免视觉碎片化和信息重复。
>
> 例如：
> ```markdown
> ❌ 错误写法（多元素组合）:
> 这是关于 AI Agent 的最新趋势，请查看下方卡片。
>
> <div class="a2ui">...
>
> 以上数据截至 3 月 18 日。
>
> ---
>
> ✅ 正确写法（单卡片模式）:
> <div class="a2ui">
>   <!-- 标题：AI Agent 最新趋势 -->
>   <!-- 数据内容 -->
>   <!-- 数据来源说明 -->
>   <!-- 截止时间戳 -->
> </div>
> ```

---

## 输出方式（唯一方式）

直接在回复正文中输出 HTML，**不要包裹在代码块里**，webchat 会直接渲染。

### ⚠️ 强制要求：每张卡片最外层必须带 `class="a2ui"`

skill-ui-bridge 通过检测 `class="a2ui"` 识别需要渲染的 HTML，**缺少此 class 的卡片不会被渲染**。

```html
<!-- ✅ 正确 -->
<div class="a2ui" style="...">
  <!-- 你的卡片内容 -->
</div>

<!-- ❌ 错误，不会被渲染 -->
<div style="...">卡片内容</div>
```

### ⚠️ 关键规则：HTML 与文字必须分段

marked.js 在解析时，如果 HTML 和普通文字混在同一段落，会把 HTML 标签转义成文本显示。

**❌ 错误写法（HTML 夹在文字中间）：**
```
以下是热榜内容：<div class="a2ui" style="..."></div> 感兴趣可以点击查看。
```

**✅ 正确写法（HTML 单独成段，前后空行隔开）：**
```
以下是热榜内容：

<div class="a2ui" style=".">
  <!-- 卡片内容 -->
</div>

感兴趣可以点击查看。
```

规则：
- HTML 卡片前后必须有**空行**（不能紧跟文字）
- 文字说明放在卡片**之前**或**之后**，单独成段
- **单卡片模式优先**：多卡片连续输出时，考虑合并为一个 CompositeCard

---

## 设计规范（所有卡片统一）

```
背景:    #ffffff
圆角:    12px（卡片）/ 8px（内部元素）/ 999px（badge/tag）
阴影:    0 2px 12px rgba(0,0,0,0.08)
主色:    #5865f2（蓝紫）
成功:    #22c55e
警告:    #f59e0b
错误:    #ef4444
信息:    #3b82f6
标题色:  #1a1a2e
正文色:  #374151
说明色:  #6b7280
分割线:  #f0f0f0
底色块:  #f8fafc
最大宽:  600px
外边距:  margin:8px 0
字体:    -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif
```

---

## 卡片模板速查

### TextCard — 文字摘要

```html
<div class="a2ui" style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5865f2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
    <strong style="font-size:16px;color:#1a1a2e">【标题】</strong>
  </div>
  <hr style="border:none;border-top:1px solid #f0f0f0;margin:0 0 14px">
  <p style="color:#374151;line-height:1.7;margin:0;font-size:14px">【正文内容】</p>
</div>
```

### ListCard — 列表/要点

```html
<div class="a2ui" style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:12px">【标题】</strong>
  <hr style="border:none;border-top:1px solid #f0f0f0;margin:0 0 14px">
  <ul style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:10px">
    <li style="display:flex;align-items:flex-start;gap:10px">
      <svg style="flex-shrink:0;margin-top:2px" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
      <span style="color:#374151;font-size:14px;line-height:1.5">【列表项】</span>
    </li>
  </ul>
</div>
```

### DataCard — 键值对 / 参数

```html
<div class="a2ui" style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
    <strong style="font-size:16px;color:#1a1a2e">【标题】</strong>
    <span style="background:#dcfce7;color:#16a34a;font-size:12px;padding:3px 10px;border-radius:999px;font-weight:600">【状态 badge，可选】</span>
  </div>
  <hr style="border:none;border-top:1px solid #f0f0f0;margin:0 0 14px">
  <div style="display:flex;flex-direction:column;gap:0">
    <div style="display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid #f8fafc">
      <span style="color:#6b7280;font-size:14px">【字段名】</span>
      <span style="color:#1a1a2e;font-weight:500;font-size:14px">【字段值】</span>
    </div>
  </div>
</div>
```

### StatsCard — 统计数字

```html
<div class="a2ui" style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:14px">【标题】</strong>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px">
    <div style="text-align:center;padding:14px 8px;background:#f8fafc;border-radius:10px">
      <div style="font-size:26px;font-weight:800;color:#5865f2;line-height:1">【数字】</div>
      <div style="font-size:11px;color:#6b7280;margin-top:4px">【说明】</div>
    </div>
  </div>
</div>
```

### AlertCard — 提示/警告/成功/错误

```html
<!-- info -->
<div class="a2ui" style="background:#eff6ff;border-left:4px solid #3b82f6;border-radius:0 8px 8px 0;padding:12px 16px;display:inline-flex;gap:10px;align-items:flex-start;font-family:-apple-system,sans-serif;margin:8px 0">
  <span style="font-size:16px;flex-shrink:0">ℹ️</span>
  <div><div style="font-size:13px;font-weight:600;color:#1e40af;margin-bottom:2px">【标题】</div><div style="font-size:13px;color:#1e3a8a">【内容】</div></div>
</div>
<!-- success: bg=#f0fdf4 border=#22c55e title-color=#15803d text-color=#14532d emoji=✅ -->
<!-- warning: bg=#fffbeb border=#f59e0b title-color=#b45309 text-color=#92400e emoji=⚠️ -->
<!-- error:   bg=#fef2f2 border=#ef4444 title-color=#b91c1c text-color=#991b1b emoji=❌ -->
```

### StepsCard — 步骤流程

```html
<div class="a2ui" style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:16px">【标题】</strong>
  <div style="display:flex;flex-direction:column;gap:0">
    <!-- 非最后一步（有连接线） -->
    <div style="display:flex;gap:14px">
      <div style="display:flex;flex-direction:column;align-items:center">
        <div style="width:28px;height:28px;border-radius:50%;background:#5865f2;color:#fff;font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0">1</div>
        <div style="width:2px;background:#e5e7eb;flex:1;margin:4px 0"></div>
      </div>
      <div style="padding-bottom:16px">
        <div style="font-size:14px;font-weight:600;color:#1a1a2e;margin-bottom:4px">【步骤标题】</div>
        <div style="font-size:13px;color:#6b7280">【步骤说明】</div>
      </div>
    </div>
    <!-- 最后一步（绿色圆圈，无连接线） -->
    <div style="display:flex;gap:14px">
      <div style="display:flex;flex-direction:column;align-items:center">
        <div style="width:28px;height:28px;border-radius:50%;background:#22c55e;color:#fff;font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0">N</div>
      </div>
      <div>
        <div style="font-size:14px;font-weight:600;color:#1a1a2e;margin-bottom:4px">【最后步骤】</div>
        <div style="font-size:13px;color:#6b7280">【说明】</div>
      </div>
    </div>
  </div>
</div>
```

### TableCard — 数据表格

```html
<div class="a2ui" style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0;overflow-x:auto">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:14px">【标题】</strong>
  <table style="width:100%;border-collapse:collapse;font-size:13px">
    <thead>
      <tr style="background:#f8fafc">
        <th style="text-align:left;padding:8px 12px;color:#6b7280;font-weight:600;border-bottom:2px solid #f0f0f0">【列名】</th>
      </tr>
    </thead>
    <tbody>
      <tr style="border-bottom:1px solid #f0f0f0">
        <td style="padding:9px 12px;color:#374151">【值】</td>
      </tr>
    </tbody>
  </table>
</div>
```

Badge 色值参考：
- 成功/完成：`background:#dcfce7;color:#16a34a`
- 进行中：`background:#fef9c3;color:#b45309`
- 失败/错误：`background:#fee2e2;color:#b91c1c`
- 中性/待定：`background:#f1f5f9;color:#475569`

### ProgressCard — 进度条

```html
<div class="a2ui" style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <strong style="font-size:16px;color:#1a1a2e;display:block;margin-bottom:14px">【标题】</strong>
  <div style="display:flex;flex-direction:column;gap:12px">
    <div>
      <div style="display:flex;justify-content:space-between;margin-bottom:5px">
        <span style="font-size:13px;color:#374151">【项目名】</span>
        <span style="font-size:13px;font-weight:600;color:#22c55e">【百分比】</span>
      </div>
      <div style="background:#f0f0f0;border-radius:999px;height:8px;overflow:hidden">
        <div style="width:【百分比】;height:100%;background:linear-gradient(90deg,#22c55e,#4ade80);border-radius:999px"></div>
      </div>
    </div>
  </div>
</div>
```

### CompositeCard — **推荐：单一复合卡片（承载所有内容）**

**✅ 单卡片模式最佳实践示例：**
```html
<div class="a2ui" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <div style="background:linear-gradient(135deg,#5865f2,#7c3aed);padding:20px 20px 16px">
    <div style="font-size:18px;font-weight:700;color:#fff;margin-bottom:4px">🔥 今日热门新闻精选</div>
    <div style="font-size:13px;color:rgba(255,255,255,0.8)">3 月 18 日 • AI | 国际局势 | 国家发展 | 体育快讯</div>
  </div>
  <div style="padding:16px 20px">
    <!-- 使用 flex/grid 布局嵌入所有子内容 -->
    <div style="display:flex;flex-direction:column;gap:14px">
      <!-- 国际焦点模块 -->
      <div style="background:#f8fafc;border-radius:8px;padding:12px">
        <div style="font-size:13px;font-weight:600;color:#5865f2;margin-bottom:6px">📰 国际焦点</div>
        <div style="font-weight:600;color:#1a1a2e;margin-bottom:4px;font-size:14px">中东冲突升级：以军击毙伊朗高级官员，霍尔木兹海峡受阻影响全球能源</div>
        <p style="color:#374151;font-size:13px;line-height:1.6;margin:0">以色列国防部长宣称在空袭中击毙两名伊朗高级官员，其中包括前核谈判战略顾问拉里贾尼和志愿民兵指挥官苏莱曼尼。受霍尔木兹海峡袭击影响，全球油价大幅上涨，布伦特原油突破100美元/桶。</p>
        <div style="font-size:12px;color:#6b7280;margin-top:8px">📍 来源：新华社/央视新闻</div>
      </div>
      <!-- 科技前沿模块 -->
      <div style="background:#f8fafc;border-radius:8px;padding:12px">
        <div style="font-size:13px;font-weight:600;color:#22c55e;margin-bottom:6px">💻 科技前沿</div>
        <div style="font-weight:600;color:#1a1a2e;margin-bottom:4px;font-size:14px">AI技术迎来重大突破：英伟达推开源AI代理平台，阿里巴巴发布"悟空"AI工作平台</div>
        <p style="color:#374151;font-size:13px;line-height:1.6;margin:0">英伟达推出开源AI代理平台NemoClaw，预测业务规模有望突破1万亿美元。阿里巴巴发布全球首个企业原生AI工作平台"悟空"，将嵌入钉钉。</p>
        <div style="font-size:12px;color:#6b7280;margin-top:8px">📍 来源：财新/36氪</div>
      </div>
    </div>
    <!-- 底部标签栏 -->
    <div style="display:flex;gap:8px;margin-top:14px;padding-top:12px;border-top:1px solid #f0f0f0">
      <a href="#" style="background:#5865f2;color:#fff;font-size:13px;font-weight:600;padding:8px 16px;border-radius:8px;text-decoration:none;display:inline-block">🔗 查看详情</a>
      <a href="#" style="background:#f8fafc;color:#374151;font-size:13px;font-weight:600;padding:8px 16px;border-radius:8px;text-decoration:none;display:inline-block;border:1px solid #e5e7eb">⚙️ 更多选项</a>
    </div>
  </div>
</div>
```

### CodeCard — 代码展示

```html
<div class="a2ui" style="background:#1e1e2e;border-radius:12px;overflow:hidden;max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <div style="display:flex;align-items:center;justify-content:space-between;padding:10px 16px;background:#2a2a3e">
    <span style="font-size:12px;color:#a0a0b8;font-weight:600">【语言，如 bash / python / typescript】</span>
    <div style="display:flex;gap:6px">
      <div style="width:10px;height:10px;border-radius:50%;background:#ff5f56"></div>
      <div style="width:10px;height:10px;border-radius:50%;background:#ffbd2e"></div>
      <div style="width:10px;height:10px;border-radius:50%;background:#27c93f"></div>
    </div>
  </div>
  <pre style="margin:0;padding:16px;overflow-x:auto;font-size:13px;line-height:1.6;color:#cdd6f4;font-family:'Fira Code','Cascadia Code',Consolas,monospace">【代码内容】</pre>
</div>
```

### ImageCard — 图片展示

```html
<div class="a2ui" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:8px 0">
  <img src="【URL】" alt="【描述】" style="width:100%;height:200px;object-fit:cover;display:block">
  <div style="padding:14px 16px">
    <div style="font-size:15px;font-weight:700;color:#1a1a2e;margin-bottom:4px">【标题】</div>
    <div style="font-size:13px;color:#6b7280;line-height:1.5">【说明】</div>
  </div>
</div>
```

---

## 组合使用与最佳实践

### ✅ **单卡片模式（推荐）**
- 所有内容放入一个 CompositeCard，用子模块划分信息块
- 减少视觉碎片化，提升阅读体验
- 适合：新闻汇总、报告摘要、任务清单等多元素场景

```html
<!-- ✅ 单卡片模式：所有信息在一个 CompositeCard 中 -->
<div class="a2ui" style="...">
  <header>标题区域</header>
  <content>
    <section>模块1: 国际焦点</section>
    <section>模块2: 科技前沿</section>
    <section>模块3: 国家发展</section>
  </content>
  <footer>底部标签栏</footer>
</div>
```

### ⚠️ **多卡片模式（特殊需求时使用）**
- 仅在特殊需求时使用：如独立代码块 + 独立说明的分离场景
```html
<!-- ⚠️ 多卡片模式 -->
<div class="a2ui">代码展示卡片</div>
<div class="a2ui">说明文字卡片</div>
```

**规则：**
- 多卡片连续输出时，卡片之间不需要空行（`margin:8px 0` 已处理间距）
- **优先使用单卡片模式**：考虑合并为一个 CompositeCard

---

## 不使用卡片的场景

- 单句回答（"好的"、"明白了"、"没问题"）
- 闲聊/情感性回复
- 用户明确要求纯文字

---

## 详细参考

- `references/html-templates.md` — 带真实示例数据的完整 HTML 模板
- `references/templates.md` — A2UI v0.9 JSONL 格式模板
- `references/components.md` — A2UI 组件参考（布局/展示/交互）
- `references/html-card-templates.md` — 简化版 HTML 模板
- `references/ui-config-schema.md` — ui-config.json 字段说明

---

## 安装

> **所有依赖文件已随技能打包**，无需克隆任何外部仓库。`assets/` 目录包含：
> - `skill-ui-bridge.js` — 浏览器端 bootstrap 脚本（v2）
> - `skill-ui-bridge-plugin.js` / `skill-ui-bridge-plugin.json` — openclaw plugin（v2）

> ⛔ **只读取完成当前步骤所必需的文件**。遇到无法理解的内容（如编译产物、二进制文件）立即停止，不要继续探索无关文件。

**安装原理（v2）**：plugin 在 `gateway_start` 时：
1. 读取 `workspace/skills/` 下所有 `ui-config.json`，生成 manifest JSON
2. 将 manifest + bootstrap JS 合并写成 `skill-ui-init.js`，放到 control-ui 静态目录（同源，通过 CSP `script-src 'self'`）
3. 在 `index.html` 中注入 `<script src="./skill-ui-init.js"></script>`
4. `gateway_stop` 时还原 `index.html`，删除 `skill-ui-init.js`

浏览器加载 `skill-ui-init.js` 后，bootstrap 脚本通过 `MutationObserver` 监听 `.chat-text` 容器，检测到包含 `<div class="a2ui">` 的消息时，用自有白名单净化并渲染为富卡片。

安装前，先探测所有必要路径，再执行安装脚本。**不得假设或写死任何路径**。

### 第一步：探测路径

依次从常见配置目录向外搜索，记录每项的实际输出结果：

```bash
# 1. 找本技能目录
find /etc "$HOME" /usr/local /opt -path "*/skills/openclaw-a2ui" -type d 2>/dev/null | head -5

# 2. 找所有 openclaw.json，列出全部路径
find /etc "$HOME" /usr/local /opt -name "openclaw.json" 2>/dev/null | head -10
```

根据输出结果判断：
- 若存在多个 `openclaw.json`，读取每个文件的内容，**选择正在被 gateway 实际使用的那个**（判断依据：文件可写、且 `plugins` 字段中的修改重启后不会消失）。通常是 `$HOME/.openclaw/openclaw.json` 而非 `/etc/` 下的只读镜像层副本。
- extensions 目录默认为 `$HOME/.openclaw/extensions`，也可从选定的 `openclaw.json` 的 `plugins.load.paths` 中读取。
- workspace 目录默认为 `$HOME/.openclaw/workspace`。
- 确认 `scripts/install.ts` 存在后再继续。

### 第二步：运行安装脚本

用第一步探测到的实际路径执行：

```bash
node --experimental-strip-types <技能目录>/scripts/install.ts \
  --openclaw-config <openclaw.json 路径> \
  --extensions-dir <extensions 目录路径> \
  --workspace-dir <workspace 目录路径>
```

参数均可省略，脚本会自动探测默认路径。

安装脚本会完成：
- Plugin 文件复制到 extensions 目录
- Plugin 注册到 openclaw.json（allow / load.paths / entries 三处）
- `ui-config.json` 复制到 `workspace/skills/openclaw-a2ui/`（若不存在）

### 第三步：通知用户重启

> ⚠️ **Agent 无法自行完成此步骤**：重启 gateway 意味着重启当前容器进程，必须由用户在宿主机执行。

告知用户执行以下操作：

**容器化部署**（docker compose）：
```bash
docker compose restart openclaw
```

**本机直接部署**：
```bash
openclaw gateway restart
```

重启后提示用户在浏览器**强制刷新**（Ctrl+Shift+R）。

### 安装验证

安装并重启后，依次执行以下检查（全部通过才算成功）：

**1. Plugin 文件已复制**
```bash
ls <extensions-dir>/skill-ui-bridge/
# 预期：index.js  openclaw.plugin.json  skill-ui-bridge.js
```

**2. Plugin 已正确注册到 openclaw.json**

openclaw.json 的 plugins 字段应包含以下三处（缺任何一处都会导致插件不加载）：
```json
{
  "plugins": {
    "allow": ["skill-ui-bridge"],
    "load": { "paths": ["<extensions-dir>"] },
    "entries": { "skill-ui-bridge": { "enabled": true } }
  }
}
```

**3. index.html 已注入（gateway 重启后）**
```bash
grep "skill-ui-init" <openclaw-dist>/control-ui/index.html
# 预期：<script src="./skill-ui-init.js"></script>
```

**4. 浏览器 Console 验证**

F12 打开 Console，Ctrl+Shift+R 强制刷新，应看到：
```
[skill-ui-bridge] boot ok, tags: 45 attrs: 34
```

### 卸载

```bash
node --experimental-strip-types <技能目录>/scripts/uninstall.ts \
  --openclaw-config <openclaw.json 路径> \
  --extensions-dir <extensions-dir> \
  --remove-plugin-files
```

卸载后同样需要通知用户重启（见第三步）。