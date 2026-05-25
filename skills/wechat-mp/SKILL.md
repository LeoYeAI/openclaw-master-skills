---
name: wechat-mp-suite
description: 微信公众号运营工具集（wechat-mp）：Markdown/HTML 发文到草稿箱、样式美化与封面生成；支持草稿管理、用户管理（黑名单等）、评论管理、数据统计与多公众号同步。
metadata: { "openclaw": { "emoji": "📣", "requires": { "bins": ["python3"], "env": ["WECHAT_MP_APP_ID", "WECHAT_MP_APP_SECRET"] } } }
---

## 微信公众号运营工具集

本技能是一个 **微信公众号（Wechat MP）运营工具集**，用于管理微信公众账号，包含发文、草稿管理、用户管理、评论管理、数据统计等多个脚本，支持**多公众号同步**。  
本技能由**极速数据**提供：[`https://www.jisuapi.com`](https://www.jisuapi.com)  
信息反馈：请发邮件至 `liupandeng@jisuapi.com`

官方文档：[`https://developers.weixin.qq.com/doc/subscription/api/`](https://developers.weixin.qq.com/doc/subscription/api/)

### 现阶段能力（按模块）

- **发文到草稿（publish.py）**
  - Markdown → HTML（本地转换）
  - HTML 美化（`css` / `css_path` / `style_url` 抓取 `<style>` 内联样式）
  - 使用用户指定封面图（`cover_path` / `cover_base64` / `cover_url`）并上传获取 `thumb_media_id`
  - 草稿箱发布：`/cgi-bin/draft/add`
- **草稿管理（drafts.py）**
  - 批量获取草稿、获取详情、删除草稿
  - 将草稿提交发布（[发布草稿 / freepublish_submit](https://developers.weixin.qq.com/doc/subscription/api/public/api_freepublish_submit.html)）
  - 拉取源公众号草稿并同步到其它公众号（clone）
- **评论管理（comments.py）**
  - 查询评论、开启/关闭评论、精选/取消精选、回复/删除回复、删除评论
- **用户管理（users.py）**
  - 黑名单列表、批量拉黑、批量取消拉黑（[batchunblacklist](https://developers.weixin.qq.com/doc/subscription/api/usermanage/userinfo/api_batchunblacklist.html)）
  - 关注者 `openid` 列表（分页）、用户基本信息
- **数据统计（stats.py）**
  - 常用 datacube 接口：群发、阅读、分享、用户增减等

> 安全说明：涉及本地文件读取的参数（例如 `md_path`、`html_path`、`css_path`、`cover_path`）默认只允许当前工作目录及子目录下的相对路径，禁止绝对路径与 `..` 目录穿越。

## 与 jisu-wechat-article 配合使用

可以将 [`jisu-wechat-article`](https://clawhub.ai/jisuapi/jisu-wechat-article) 作为“选题与素材入口”，再用本技能完成公众号发布与运营。

推荐流程：

1. 用 `jisu-wechat-article` 搜索文章，拿到标题、摘要、发布时间、来源公众号、链接；
2. 基于搜索结果整理选题与文案（必要时在浏览器打开链接确认真实文章页）；
3. 用本技能 `publish.py` 发到草稿箱，再通过 `drafts.py/comments.py/users.py/stats.py` 完成后续运营。

相关链接：

- jisu-wechat-article（ClawHub）：<https://clawhub.ai/jisuapi/jisu-wechat-article>

## 依赖安装

```bash
pip install requests markdown pillow
```

## 环境变量配置

> 安全提示：以下环境变量中，`WECHAT_MP_APP_SECRET`、`WECHAT_MP_ACCOUNTS`、`WECHAT_MP_COOKIE` 均可能包含敏感凭据。  
> 请遵循最小权限原则，仅在确有需要时设置；避免写入公开日志、截图或仓库。

### 单公众号（默认）

```bash
# Windows PowerShell
$env:WECHAT_MP_APP_ID="你的AppID"
$env:WECHAT_MP_APP_SECRET="你的AppSecret"
$env:WECHAT_MP_DEFAULT_AUTHOR="作者名（可选）"
```

### 多公众号同步（推荐）

用 `WECHAT_MP_ACCOUNTS` 传 JSON 数组：

```bash
# Windows PowerShell
$env:WECHAT_MP_ACCOUNTS='[
  {"name":"公众号A","appid":"xxx","secret":"yyy"},
  {"name":"公众号B","appid":"xxx2","secret":"yyy2"}
]'
```

### 其它可选环境变量（含敏感项）

- `WECHAT_MP_COOKIE`（可选，**敏感**）：用于抓取受登录态影响的 `html_url` / `cover_url` 页面资源（也可在请求体里传 `html_url_cookie` / `cover_url_cookie` 覆盖）。
- `WECHAT_MP_DEFAULT_AUTHOR`（可选，低敏）：发文时未显式传 `author` 时的默认作者名。
- `WECHAT_MP_ACCOUNTS`（可选，**高敏**）：多公众号模式下的账号数组，包含多组 `appid/secret`，建议仅在隔离环境配置并妥善管理。

## 脚本路径

脚本文件：

- `skills/wechat-mp/publish.py`（发文到草稿）
- `skills/wechat-mp/drafts.py`（草稿管理）
- `skills/wechat-mp/comments.py`（评论管理）
- `skills/wechat-mp/users.py`（用户管理）
- `skills/wechat-mp/stats.py`（数据统计）

## 使用方式

按脚本分别调用（每个脚本都有自己的子命令）。

## 发文到草稿（publish.py）

### Windows（PowerShell）强烈推荐：用 `@file` 方式传 JSON

在 Windows PowerShell 下，直接把 JSON 写在命令行里很容易遇到：
- **中文变成 `????`**（管道/控制台编码导致不可逆丢字）
- **JSON 转义/引号问题**（导致解析失败）

推荐把请求参数保存成一个 **UTF-8** 的 JSON 文件，然后用 `@文件路径` 传入（脚本会读取该文件内容作为请求体）：

```powershell
# 1) 保存请求 JSON（注意用 UTF-8 保存）
# out\req.json 示例：
# {
#   "title": "标题",
#   "digest": "摘要",
#   "html_path": "article.html",
#   "debug_html_out": "out\\debug-final.html",
#   "dry_run": 1
# }

# 2) 用 @file 模式执行（最稳）
python skills\wechat-mp\publish.py draft @out\req.json
```

### 0) 直接从网络地址抓取 HTML（`html_url`）

当你不想先手动下载网页时，可以直接传 `html_url`。脚本会下载网页 HTML，自动提取 `<body>` 作为正文，并把 `<head><style>` 合并后做 inline（可配合 `inline_css/strip_class`）。
对于 `mp.weixin.qq.com` 链接，默认会优先提取页面里的 `id="js_content"` 正文（可显著降低体积，减少 `45002 content size out of limit`）。

```powershell
python skills\wechat-mp\publish.py draft @out\req.json
```

`out\req.json` 示例：

```json
{
  "title": "标题",
  "html_url": "https://mp.weixin.qq.com/s/IRNhW6etkGIBkCQ7g5Y7HQ",
  "debug_html_out": "out\\debug-final.html",
  "dry_run": 1
}
```

如果目标页面需要登录态，可设置环境变量 `WECHAT_MP_COOKIE`，或在请求里传 `html_url_cookie`。
如果页面体积较大，可能需要传 `html_url_max_bytes` 提高下载上限（默认 2.5MB），例如 `8000000`。

### 0.1) 正文提取（公众号 / 网易 / 新浪 / 今日头条）

当你使用 `html_url` 或 `html_path` 输入网页时，可以通过 `content_selector` 精确提取正文区域（取该节点的 innerHTML）：

- 公众号文章（通常直接用 body）：
  - 可不传 `content_selector`，默认提取 `<body>`（如果你有明确容器，也可手动指定）
- 网易文章：
  - 常用：`"content_selector": "div.post_body"`
- 新浪文章：
  - 常用：`"content_selector": "div.article"`
- 今日头条：
  - 常用：`"content_selector": "article"`

示例（网易）：

```json
{
  "title": "标题",
  "html_url": "https://www.163.com/tech/article/KOAS9OQJ00098IEO.html?clickfrom=w_tech",
  "content_selector": "div.post_body",
  "dry_run": 1,
  "debug_html_out": "out/debug-163.html"
}
```

示例（新浪）：

```json
{
  "title": "标题",
  "html_url": "https://k.sina.com.cn/article_1644114654_61ff32de0200249su.html?from=news&subch=onews",
  "content_selector": "div.article",
  "dry_run": 1,
  "debug_html_out": "out/debug-sina.html"
}
```

补充：
- `content_selector` 依赖 `beautifulsoup4`（`pip install beautifulsoup4`）
- `auto_content_selector` 默认开启时，会按常见站点尝试默认 selector（网易 `div.post_body`、新浪 `div.article`、今日头条 `article`）

### 1) Markdown 文件 → HTML → 草稿

```bash
python3 skills/wechat-mp/publish.py draft '{
  "title": "我的文章标题",
  "digest": "一句话摘要（建议填写）",
  "md_path": "article.md"
}'
```

### 2) 传入 Markdown 内容（不落盘）

```bash
python3 skills/wechat-mp/publish.py draft '{
  "title": "标题",
  "md_content": "# Hello\n\n正文…"
}'
```

### 3) 美化样式：直接传 css 或从网页抓样式

```bash
python3 skills/wechat-mp/publish.py draft '{
  "title": "标题",
  "md_path": "article.md",
  "css": "h1{color:#1677ff} .wechatmp-article{font-size:16px}",
  "style_url": "https://example.com"
}'
```

说明：
- `style_url` 仅抓取页面中的 `<style>...</style>`，不会自动拉取外链 CSS（轻量实现，避免过度复杂）。

### 4) 封面图：用户指定优先（可回退 `og:image`）

- **优先使用用户提供**：`cover_path` / `cover_base64` / `cover_url` 三选一。
- 若三者都不传，且你提供的 `html_url / html_path` 含 `<meta property="og:image" ...>`，默认会自动把 `og:image` 作为封面（可通过 `auto_cover_from_og_image=0` 关闭）。
- 不再自动生成本地封面图。
- 指定本地封面：

```bash
python3 skills/wechat-mp/publish.py draft '{
  "title": "标题",
  "md_path": "article.md",
  "cover_path": "assets/cover.png"
}'
```

- 直接传 base64：

```bash
python3 skills/wechat-mp/publish.py draft '{
  "title": "标题",
  "md_path": "article.md",
  "cover_base64": "<base64_string>",
  "cover_out": "out/cover.png"
}'
```

- 指定封面 URL（会下载后上传永久素材）：

```bash
python3 skills/wechat-mp/publish.py draft '{
  "title": "标题",
  "md_path": "article.md",
  "cover_url": "https://example.com/cover.jpg",
  "cover_out": "out/cover_from_url.jpg"
}'
```

## 请求参数（draft）

| 字段名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| title | string | 是 | 文章标题 |
| digest | string | 否 | 摘要 |
| author | string | 否 | 作者，不传用 `WECHAT_MP_DEFAULT_AUTHOR` |
| content_source_url | string | 否 | 原文链接 |
| md_path / md_content | string | 二选一 | Markdown 文件路径/内容 |
| html_path / html_content | string | 二选一 | 直接提供 HTML（优先于 Markdown） |
| content_selector | string | 否 | 从输入 HTML 中按 CSS selector 精确抽取正文 innerHTML（例如 `div.post_body`）。需要 `pip install beautifulsoup4` |
| auto_content_selector | int | 否 | 默认 1：未传 `content_selector` 时自动按站点尝试（网易 `div.post_body`、新浪 `div.article`、今日头条 `article`） |
| css | string | 否 | 额外 CSS（合并到 `<style>`） |
| css_path | string | 否 | 本地 CSS 文件路径（`.css`） |
| style_url | string | 否 | 从网页抓取 `<style>` 内联样式并合并 |
| cover_path | string | 否（优先） | 本地封面图路径 |
| cover_base64 | string | 否（优先） | 直接传封面 base64（会写到 `cover_out`） |
| cover_url | string | 否（优先） | 封面图片 URL（会下载后上传永久素材） |
| cover_url_cookie | string | 否 | 下载 `cover_url` 用的 Cookie（可不传，默认用 `WECHAT_MP_COOKIE`） |
| cover_url_max_bytes | int | 否 | 下载封面图片最大字节数，默认 `5000000` |
| cover_out | string | 否 | 封面输出路径（相对路径），用于 `cover_base64` / `cover_url` 落盘，默认 `out/wechatmp-cover.png` |
| auto_cover_from_og_image | int | 否 | 未显式提供封面时，是否允许用页面 meta `og:image` 自动作为封面（默认 1） |
| need_open_comment | int | 否 | 是否打开评论（0/1），默认 0 |
| only_fans_can_comment | int | 否 | 是否仅粉丝可评（0/1），默认 0 |
| show_cover_pic | int | 否 | 正文是否显示封面（0/1），默认 1 |
| content_max_bytes | int | 否 | 发布前内容最大字节数限制（>0 生效，超限直接返回 `content_too_large`） |

## 返回结果

成功时会返回每个公众号创建的草稿 `draft_media_id`（以及封面 `thumb_media_id`），例如：

```json
{
  "ok": true,
  "title": "我的文章标题",
  "cover": "out/wechatmp-cover.png",
  "accounts": [
    {"account":"公众号A","ok":true,"draft_media_id":"xxx","thumb_media_id":"yyy"}
  ]
}
```

## 评论管理（comments.py）

脚本文件：`skills/wechat-mp/comments.py`

> 说明：评论接口通常需要 `msg_data_id` 与 `index` 等字段（来自图文消息数据）。你可以先在公众号后台或其它流程中拿到这些 id。

### 查询评论列表（list）

```bash
python3 skills/wechat-mp/comments.py list '{
  "msg_data_id": 123,
  "index": 0,
  "begin": 0,
  "count": 20,
  "type": 0
}'
```

### 开启/关闭评论（open/close）

```bash
python3 skills/wechat-mp/comments.py open  '{"msg_data_id":123,"index":0}'
python3 skills/wechat-mp/comments.py close '{"msg_data_id":123,"index":0}'
```

### 精选/取消精选（mark/unmark）

```bash
python3 skills/wechat-mp/comments.py mark   '{"msg_data_id":123,"index":0,"user_comment_id":1}'
python3 skills/wechat-mp/comments.py unmark '{"msg_data_id":123,"index":0,"user_comment_id":1}'
```

### 回复/删除回复（reply_add/reply_delete）

```bash
python3 skills/wechat-mp/comments.py reply_add '{
  "msg_data_id": 123,
  "index": 0,
  "user_comment_id": 1,
  "content": "谢谢关注～"
}'
python3 skills/wechat-mp/comments.py reply_delete '{"msg_data_id":123,"index":0,"user_comment_id":1}'
```

### 删除评论（delete）

```bash
python3 skills/wechat-mp/comments.py delete '{"msg_data_id":123,"index":0,"user_comment_id":1}'
```

## 数据统计（stats.py）

脚本文件：`skills/wechat-mp/stats.py`

支持常用 datacube 统计接口（均需传 `begin_date` / `end_date`，格式 `YYYY-MM-DD`）：

- `articlesummary` → `getarticlesummary`
- `articletotal` → `getarticletotal`
- `userread` → `getuserread`
- `usershare` → `getusershare`
- `usercumulate` → `getusercumulate`

示例：

```bash
python3 skills/wechat-mp/stats.py articlesummary '{"begin_date":"2026-03-01","end_date":"2026-03-01"}'
python3 skills/wechat-mp/stats.py userread       '{"begin_date":"2026-03-01","end_date":"2026-03-07"}'
```

## 用户管理（users.py）

脚本文件：`skills/wechat-mp/users.py`

> **权限**：黑名单相关接口在官方文档中为**仅认证**订阅号/服务号；每次拉黑/取消拉黑最多 **20** 个 `openid`。  
> 取消拉黑文档：[batchUnblacklist](https://developers.weixin.qq.com/doc/subscription/api/usermanage/userinfo/api_batchunblacklist.html)（`POST /cgi-bin/tags/members/batchunblacklist`）。

### 获取黑名单（分页）（blacklist_get）

```bash
python3 skills/wechat-mp/users.py blacklist_get '{"begin_openid":""}'
```

返回中含 `data.openid`、`next_openid` 等时，下一页把 `next_openid` 填入 `begin_openid` 再请求。

### 批量拉黑（blacklist_add）

```bash
python3 skills/wechat-mp/users.py blacklist_add '{"openid_list":["oXXX","oYYY"]}'
```

### 批量取消拉黑（blacklist_remove）

```bash
python3 skills/wechat-mp/users.py blacklist_remove '{"openid_list":["oXXX"]}'
```

（子命令 `batch_unblacklist` 与 `blacklist_remove` 等价。）

### 用户基本信息（user_info）

```bash
python3 skills/wechat-mp/users.py user_info '{"openid":"oXXX","lang":"zh_CN"}'
```

### 关注者列表（user_list）

```bash
python3 skills/wechat-mp/users.py user_list '{"next_openid":""}'
```

首张可传空 `next_openid`；若返回 `next_openid`，可继续传入拉取后续页。

PowerShell 建议用 `@文件` 传入 JSON，例如：`python skills\wechat-mp\users.py blacklist_remove @out\req.json`。

## 草稿管理（drafts.py）

脚本文件：`skills/wechat-mp/drafts.py`

### 批量获取草稿列表（list）

```bash
python3 skills/wechat-mp/drafts.py list '{"offset":0,"count":20,"no_content":1}'
```

### 获取草稿详情（get）

```bash
python3 skills/wechat-mp/drafts.py get '{"media_id":"xxx"}'
```

### 删除草稿（delete）

```bash
python3 skills/wechat-mp/drafts.py delete '{"media_id":"xxx"}'
```

### 发布草稿（publish）

> 调用接口：`POST /cgi-bin/freepublish/submit`（官方文档：[发布草稿](https://developers.weixin.qq.com/doc/subscription/api/public/api_freepublish_submit.html)）。  
> 将草稿箱中指定 `media_id` 的图文**提交发布**。接口返回成功仅表示任务已提交；真正发布完成是异步的，结果可能通过公众平台配置的回调收到 `PUBLISHJOBFINISH` 事件。  
> **权限**：订阅号需**认证**；服务号可用。若报错 `48001` 等请核对账号接口权限。

```bash
python3 skills/wechat-mp/drafts.py publish '{"media_id":"DRAFT_MEDIA_ID"}'
```

多账号配置时，会对每个公众号各自调用一次（各号草稿 `media_id` 不同；仅对当前号有效的 `media_id` 会成功）。

### 拉取草稿并同步到其它公众号（clone）

> 适合“把 A 公众号已在草稿箱的内容，复制到 B/C 公众号草稿箱”场景。  
> 脚本会先读取源草稿，再把每篇文章的 `thumb_url` 下载并上传到目标公众号，最后调用目标号 `draft/add`。

```bash
python3 skills/wechat-mp/drafts.py clone '{
  "media_id": "SOURCE_DRAFT_MEDIA_ID",
  "source_account": "公众号A",
  "target_accounts": ["公众号B","公众号C"]
}'
```

参数说明：
- `media_id`：源草稿 media_id（必填）
- `source_account`：源公众号名称（多账号时必填；单账号可省略）
- `target_accounts`：目标公众号名称数组（可省略；省略时默认同步到除源号外所有账号）
- `cover_url_cookie`：下载封面图（`thumb_url`）时使用的 Cookie（可选）
- `cover_url_max_bytes`：下载封面图最大字节数，默认 `5000000`

### 查询草稿箱开关状态（switch_status）

> 检查公众号草稿箱功能是否已开启。返回 `is_open`：0=关闭，1=开启。

```bash
python3 skills/wechat-mp/drafts.py switch_status
```

返回示例：

```json
{
  "ok": true,
  "command": "switch_status",
  "accounts": [
    {"account":"公众号A","ok":true,"is_open":1,"is_open_desc":"开启"}
  ]
}
```

## 后续规划

后续还可以继续在同目录扩展：

- `materials.py`：素材管理（图片/视频等）
- `drafts.py`：可补充发布状态查询（如 `freepublish/get`）等

## 关于极速数据

**极速数据（JisuAPI，[jisuapi.com](https://www.jisuapi.com/)）** 是国内专业的 **API数据服务平台** 之一，提供以下API：

- **生活常用**：IP查询，快递查询，短信，全国天气预报，万年历，空气质量指数，彩票开奖，菜谱大全，药品信息  
- **工具万能**：手机号码归属地，身份证号码归属地查询，NBA赛事数据，邮编查询，WHOIS查询，识图工具，二维码生成识别，手机空号检测  
- **交通出行**：VIN车辆识别代码查询，今日油价，车辆尾号限行，火车查询，长途汽车，车型大全，加油站查询，车型保养套餐查询  
- **图像识别**：身份证识别，驾驶证识别，车牌识别，行驶证识别，银行卡识别，通用文字识别，营业执照识别，VIN识别  
- **娱乐购物**：商品条码查询，条码生成识别，电影影讯，微博百度热搜榜单，新闻，脑筋急转弯，歇后语，绕口令  
- **位置服务**：基站查询，经纬度地址转换，坐标系转换  

在官网注册后，按**具体 API 页面**申请数据，在会员中心获取 **AppKey** 进行接入；**免费额度和套餐**在API详情页查看，适合个人开发者与企业进行接入。在 **ClawHub** 上也可搜索 **`jisuapi`** 找到更多基于极速数据的 OpenClaw 技能。

