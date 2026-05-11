# 自定义主题

在这个目录下放置文件夹，即可为 slide-creator 添加自己的设计预设。

## 目录结构

```
themes/
  your-theme-name/
    reference.md      ← 必填：风格描述文件，Claude 读取
    starter.html      ← 可选：预置 HTML 模板（适合有复杂视觉系统的主题）
```

## reference.md 格式

参考内置风格文件（如 `references/chinese-chan.md`）：

```markdown
# 主题名称 — Style Reference

一句话描述。灵感来源 / 美学风格 / 氛围。

---

## Colors

```css
:root {
    --bg:      #...;
    --text:    #...;
    --accent:  #...;
}
```

## Typography
...

## Layout
...

## Best For
适用场景、目标受众、使用场合。
```

## starter.html（可选）

如果你的主题包含复杂的视觉元素（动态背景、特殊布局系统等），可以提供一份 `starter.html`。Claude 会直接以它为基础填充内容，而不是从零开始实现视觉系统。可参考 `references/blue-sky-starter.html`。

## 样板案例

`_example-coral-dawn/` — 一份完整的样板主题，可以直接复制修改。
以 `_` 开头的目录会被 slide-creator 自动忽略，不会出现在预设列表中。

也可参考：
- `references/chinese-chan.md` — 内置风格，格式完全相同
- `references/blue-sky-starter.html` — 完整的 starter 模板示例

## 分享主题

将主题文件夹发布为 git 仓库，其他人 clone 进自己的 `themes/` 目录即可使用：

```bash
git clone https://github.com/yourname/slide-creator-theme-yourtheme \
  ~/.claude/skills/slide-creator/themes/yourtheme
```
