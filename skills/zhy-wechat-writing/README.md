# zhy-wechat-writing

主写作 skill，用于生成微信公众号文章的完整工作流。

## What It Does

最小能力包括：

- 根据主题检索资料
- 生成可追溯证据池
- 生成公众号初稿
- 自动审稿
- 润色与输出 Markdown 成稿

可选增强能力：

- `zhy-article-illustrator`：自动配图
- `zhy-markdown2wechat`：转微信公众号 HTML
- `zhy-wechat-publish`：保存到公众号草稿箱

## Install

```bash
npx skills add https://github.com/zhylq/yuan-skills --skill zhy-wechat-writing
```

## Dependencies

### 必需运行时工具

- `WebSearch`：搜索候选来源
- `webfetch`：抓取网页正文

### 可选辅助 skills

| Skill | 何时需要 | 作用 |
|---|---|---|
| `zhy-article-illustrator` | 需要自动配图时 | 生成插图版文章 |
| `zhy-markdown2wechat` | 需要公众号 HTML 时 | 将 Markdown 转为内联 HTML |
| `zhy-wechat-publish` | 需要保存到草稿箱时 | 上传 HTML 到微信公众号草稿箱 |

## Key Inputs

### 必填

- `topic`：文章主题

### 常用可选参数

- `urls`：参考链接列表
- `slug`：文章目录名
- `search_count`：候选搜索条数
- `with_illustrations`：是否自动配图
- `with_html_theme`：是否输出公众号 HTML
- `post_to_wechat`：是否保存到公众号草稿箱

### 配图相关参数

- `illustration_density`
- `illustration_upload`
- `illustration_aspect_ratio`
- `illustration_prompt_profile`
- `illustration_text_language`
- `illustration_english_terms_whitelist`
- `illustration_image_provider`
- `illustration_image_model`
- `illustration_image_size`
- `illustration_image_base_url`

## Output

典型输出路径：

- `articles/<slug>/article.md`
- `articles/<slug>/sources/evidence.md`
- `articles/<slug>/sources/review.md`
- `articles/<slug>/article.illustrated.md`（可选）
- `articles/<slug>/article.zhy.html`（可选）

## Environment

本 skill 自身不强制要求 `.env`。

但如果你启用了可选步骤，则需要对应辅助 skill 的环境配置：

- 配图：查看 `zhy-article-illustrator/README.md`
- 草稿箱发布：查看 `zhy-wechat-publish/README.md`

## Recommended Usage

### 只写文章

安装：

- `zhy-wechat-writing`

### 写文章 + 转 HTML

安装：

- `zhy-wechat-writing`
- `zhy-markdown2wechat`

### 完整链路

安装：

- `zhy-wechat-writing`
- `zhy-article-illustrator`
- `zhy-markdown2wechat`
- `zhy-wechat-publish`
