---
name: ppt-generator
description: 将用户讲稿一键生成乔布斯风极简科技感竖屏HTML演示稿。当用户需要生成PPT、演示文稿、Slides、幻灯片，或要求科技风/极简风/乔布斯风格的演示时触发此技能。输出为单个可直接运行的HTML文件。
---

# PPT Generator

将讲稿转换为乔布斯风极简科技感竖屏HTML演示稿。

## 设计哲学

- **极简主义** - 一屏只讲一件事
- **强视觉对比** - 深色背景 + 白色文字
- **高留白** - 禁止密集排版
- **强节奏感** - 让观众想继续看

## 生成流程（必须严格遵循）

### Step 1: 读取讲稿
读取用户原始讲稿，不修改原稿内容。

### Step 2: 生成提炼版讲稿
将内容精简、增强冲击力、适配演示场景，输出 Markdown 格式。

### Step 3: 生成乔布斯风标题
为每个章节生成标题，必须满足：
- ≤12 字
- 采用以下形式之一：对比式、问题式、断言式、数字式、比喻式
- 自检：是否让人想继续听？

### Step 4: 设计幻灯片结构
规划页面顺序和类型，参考 [references/slide-types.md](references/slide-types.md)。

### Step 5: 生成HTML
使用 [assets/template.html](assets/template.html) 作为基础模板生成完整HTML。

### Step 6: 填充内容
添加动态背景光斑、交互逻辑、平滑切换动画。

## 输出顺序（必须依次输出）

1. **提炼后的讲稿**（Markdown）
2. **幻灯片结构大纲**
3. **完整HTML代码**

## 视觉规范速查

| 项目 | 规范 |
|------|------|
| 比例 | 9:16 竖屏 |
| 背景 | #000000 或 #0a0a0a + 模糊光斑动画 |
| 主文字 | #ffffff |
| 辅助文字 | #9ca3af |
| 中文字体 | HarmonyOS Sans SC / 思源黑体 |
| 英文字体 | Inter / Roboto |
| 标题字重 | font-black / font-bold |
| 正文字重 | font-light / font-normal |

详细规范见 [references/design-spec.md](references/design-spec.md)。

## 交互要求

- 键盘 ← → 翻页
- 底部进度导航条
- 平滑切换动画

## 技术栈

- TailwindCSS（国内CDN）
- 复杂页面使用 Vue3（CDN）
- 单个HTML文件，可直接打开运行

## 严禁行为

- 堆字 / 密集排版
- 花哨配色
- 复杂图表
- 横屏比例
- 偏离极简科技风

## 默认规则

- 未指定页数：自动生成 8~20 页
- 未指定风格：默认乔布斯风
