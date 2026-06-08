# WeChat Publisher - 快速开始指南

## 5 分钟快速上手

### 步骤 1：安装工具（1 分钟）

```bash
npm install -g wechat-md-publisher
```

### 步骤 2：配置账号（2 分钟）

1. 获取微信公众号凭证：
   - 登录 https://mp.weixin.qq.com/
   - 进入「设置与开发」→「基本配置」
   - 复制 AppID 和 AppSecret

2. 添加账号：

```bash
wechat-pub account add \
  --name "我的公众号" \
  --app-id "wx_your_app_id" \
  --app-secret "your_app_secret" \
  --default
```

### 步骤 3：创建测试文章（1 分钟）

```bash
cat > test-article.md << 'EOF'
---
title: 测试文章
author: 测试作者
---

# 欢迎使用 WeChat Publisher

这是一篇测试文章。

## 主要特性

- 完整的草稿管理
- 8 个精美主题
- 智能图片处理
EOF
```

### 步骤 4：发布文章（1 分钟）

```bash
wechat-pub publish create --file test-article.md --theme orangeheart
```

### 验证成功

如果看到以下输出，说明配置成功：

```
✓ 渲染完成
✓ 图片处理完成
✓ 创建草稿成功
✓ 发布成功

发布 ID: 2247483647_1
```

现在可以在微信公众平台查看你的文章了！

## 常用命令速查

```bash
# 查看所有主题
wechat-pub theme list

# 创建草稿
wechat-pub draft create --file article.md --theme lapis

# 查看草稿列表
wechat-pub draft list

# 查看已发布文章
wechat-pub publish list

# 删除草稿
wechat-pub draft delete <media-id>
```

## 下一步

- 阅读完整文档：[SKILL.md](../SKILL.md)
- 查看主题示例：[themes.md](./themes.md)
- 了解 API 用法：https://github.com/sipingme/wechat-md-publisher
