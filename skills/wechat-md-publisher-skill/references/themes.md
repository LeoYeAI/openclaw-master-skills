# WeChat Publisher - 主题使用指南

## 8 个内置主题

所有主题来自 [@wenyan-md/core](https://github.com/caol64/wenyan-core)，专为微信公众号优化。

### 1. default - 默认主题

**风格**：简洁经典，适合正式文章

**适用场景**：
- 企业公告
- 正式通知
- 技术文档
- 学术文章

**使用**：
```bash
wechat-pub publish create --file article.md --theme default
```

---

### 2. orangeheart - Orange Heart

**风格**：温暖优雅，橙色调

**适用场景**：
- 情感类文章
- 生活分享
- 品牌故事
- 温馨内容

**使用**：
```bash
wechat-pub publish create --file article.md --theme orangeheart
```

---

### 3. rainbow - Rainbow

**风格**：活泼清爽，多彩

**适用场景**：
- 轻松趣味内容
- 儿童教育
- 创意分享
- 娱乐资讯

**使用**：
```bash
wechat-pub publish create --file article.md --theme rainbow
```

---

### 4. lapis - Lapis

**风格**：清新极简，蓝色调

**适用场景**：
- 技术文章
- 专业内容
- 产品介绍
- 数据分析

**使用**：
```bash
wechat-pub publish create --file article.md --theme lapis
```

---

### 5. pie - Pie

**风格**：现代锐利，灵感来自 sspai.com

**适用场景**：
- 产品评测
- 设计分享
- 效率工具
- 科技资讯

**使用**：
```bash
wechat-pub publish create --file article.md --theme pie
```

---

### 6. maize - Maize

**风格**：柔和舒适，米黄色调

**适用场景**：
- 教育内容
- 知识分享
- 读书笔记
- 文化艺术

**使用**：
```bash
wechat-pub publish create --file article.md --theme maize
```

---

### 7. purple - Purple

**风格**：简约文艺，紫色调

**适用场景**：
- 个人博客
- 文艺创作
- 摄影作品
- 艺术展示

**使用**：
```bash
wechat-pub publish create --file article.md --theme purple
```

---

### 8. phycat - 物理猫-薄荷

**风格**：薄荷绿，结构清晰

**适用场景**：
- 科普文章
- 教程指南
- 步骤说明
- 知识讲解

**使用**：
```bash
wechat-pub publish create --file article.md --theme phycat
```

---

## 主题选择建议

### 按内容类型选择

| 内容类型 | 推荐主题 | 备选主题 |
|---------|---------|---------|
| 技术文章 | lapis | default, pie |
| 生活分享 | orangeheart | maize, rainbow |
| 产品介绍 | pie | lapis, default |
| 教育内容 | maize | phycat, default |
| 情感文章 | orangeheart | purple, maize |
| 科普教程 | phycat | lapis, maize |
| 创意内容 | rainbow | purple, orangeheart |
| 正式公告 | default | lapis |

### 按品牌调性选择

- **专业严谨**：default, lapis
- **温暖亲切**：orangeheart, maize
- **年轻活力**：rainbow, pie
- **文艺清新**：purple, phycat

---

## 测试所有主题

想要对比不同主题的效果？可以批量测试：

```bash
# 创建测试文章
cat > test.md << 'EOF'
---
title: 主题测试
---

# 标题一

这是正文内容。

## 标题二

- 列表项 1
- 列表项 2

**粗体文本** 和 *斜体文本*
EOF

# 测试所有主题
for theme in default orangeheart rainbow lapis pie maize purple phycat; do
    echo "测试主题: $theme"
    wechat-pub draft create --file test.md --theme $theme
done
```

然后在微信公众平台查看对比效果。

---

## 自定义主题

如果内置主题不满足需求，可以创建自定义主题：

### 1. 创建 CSS 文件

```css
/* my-theme.css */
:root {
    --primary-color: #ff6b6b;
    --text-color: #2c3e50;
}

#wenyan {
    font-size: 16px;
    line-height: 1.8;
}

#wenyan h1 {
    color: var(--primary-color);
    border-bottom: 3px solid var(--primary-color);
}
```

### 2. 添加主题

```bash
wechat-pub theme add-local --name my-theme --path ./my-theme.css
```

### 3. 使用主题

```bash
wechat-pub publish create --file article.md --theme my-theme
```

---

## 主题预览

想要在发布前预览主题效果？

1. 先创建草稿：
```bash
wechat-pub draft create --file article.md --theme orangeheart
```

2. 在微信公众平台查看草稿预览

3. 满意后再发布：
```bash
wechat-pub publish submit <media-id>
```

---

## 常见问题

### Q: 如何查看所有可用主题？

```bash
wechat-pub theme list
```

### Q: 主题可以修改吗？

内置主题不可修改，但可以：
- 创建自定义主题
- 基于内置主题修改后另存为新主题

### Q: 发布后可以更换主题吗？

不可以。已发布的文章主题无法更改，需要：
1. 删除原文章
2. 用新主题重新发布

### Q: 哪个主题最受欢迎？

根据社区反馈：
1. **orangeheart** - 温暖优雅，适用范围广
2. **lapis** - 专业清爽，技术文章首选
3. **pie** - 现代时尚，年轻用户喜爱

建议根据自己的内容风格和受众选择。
