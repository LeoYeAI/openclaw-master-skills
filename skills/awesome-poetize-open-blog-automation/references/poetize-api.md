# Poetize Blog API Reference

This skill targets the existing Poetize backend API feature in this repository.
OpenClaw only needs `base_url` and `api_key` to use it.
For personal blogs, treat free publishing as the default and paid publishing as an uncommon opt-in path.

## Skill Runtime Requirements

The backend API itself is unchanged, but this skill now adds a strategy layer on top:

- mutating commands require `--brief-file`
- `publish_post.py` always requires an article brief
- `manage_blog.py update-article` requires an ops brief
- `manage_blog.py hide-article` requires an ops brief
- template files live in `assets/article-brief.template.json` and `assets/ops-brief.template.json`

## Auth

- Header: `X-API-KEY: <api-key>`
- Source in admin UI: API 配置页
- Required for public blog automation APIs

## Primary Endpoints

- Create article: `POST /api/api/article/create`
- Create article async: `POST /api/api/article/createAsync`
- Update article: `POST /api/api/article/update`
- Update article async: `POST /api/api/article/updateAsync`
- Query article task: `GET /api/api/article/task/{taskId}`
- Payment plugin status: `GET /api/api/payment/plugin/status`
- Configure payment plugin: `POST /api/api/payment/plugin/configure`
- Test payment plugin connection: `POST /api/api/payment/plugin/testConnection`
- Article theme status: `GET /api/api/article-theme/status`
- Activate article theme: `POST /api/api/article-theme/activate`
- Article analytics: `GET /api/api/article/analytics/{id}`
- Site visit trends: `GET /api/api/analytics/site/visits?days=7|30`
- SEO status: `GET /api/api/seo/status`
- Controlled SEO config: `GET /api/api/seo/config`
- Update controlled SEO config: `POST /api/api/seo/config`
- Trigger sitemap update: `POST /api/api/seo/sitemap/update`
- Upload cover/resource: `POST /api/api/resource/upload`
- Get article detail: `GET /api/api/article/{id}`
- List categories: `GET /api/api/categories`
- List tags: `GET /api/api/tags`

## Important Backend Behavior

- `sortName` and `labelName` can be sent instead of `sortId` and `labelId`
- If names are unknown, the backend can resolve or create them during article save
- The bundled OpenClaw script does not auto-create categories or tags by default.
- It first calls `/api/api/categories` and `/api/api/tags`, reuses exact matches, and stops for confirmation when a new category/tag would be created.
- When exact taxonomy matches fail, the scripts can return close category or tag candidates.
- Those fuzzy candidates are suggestions only and must be confirmed before querying, updating, or publishing.
- Create and update responses return `id` and `articleUrl`
- Async create/update return `taskId` and `taskStatusUrl`
- Task status returns `articleId`, `articleUrl`, `stage`, `translationStatus`, and completion flags when available
- Update requests can omit `sort`, `label`, `viewStatus`, and other unchanged fields
- Hiding an article is implemented as an update with `viewStatus: false`
- Article deletion is not part of this skill or API workflow
- If the user wants deletion-like takedown behavior, use article hiding instead
- `skipAiTranslation` is accepted in the JSON body
- Manual translation can be attached through:
  - `pendingTranslationLanguage`
  - `pendingTranslationTitle`
  - `pendingTranslationContent`
- Draft saves are implemented as private articles; the helper script auto-generates `password` and `tips` if omitted
- The skill runtime can override `viewStatus` and `payType` to satisfy brief validation rules before calling the backend
- `publish_post.py` can upload local Markdown images and local HTML `<img src="...">` references through `/api/api/resource/upload` before article creation or update
- Local article images default to resource type `articlePicture`

## Recommended Front Matter

Use YAML-like front matter with simple scalar values.

Common article switches:

- `commentStatus`: 是否启用评论
- `recommendStatus`: 是否推荐
- `viewStatus`: 是否可见
- `submitToSearchEngine`: 是否推送至搜索引擎

Recommended defaults unless the user says otherwise:

- `commentStatus: true`
- `recommendStatus: false`
- `viewStatus: true`
- `submitToSearchEngine: true` for public articles, `false` for private articles

```md
---
title: "用 AI 自动化写博客的实际落地路径"
sort: "AI实践"
label: "自动化"
cover: "https://example.com/cover.jpg"
payType: 0
paymentPluginKey: "afdian"
viewStatus: false
commentStatus: true
recommendStatus: true
submitToSearchEngine: false
password: "draft-2026"
tips: "内部预览稿"
skipAiTranslation: true
---

# 用 AI 自动化写博客的实际落地路径

正文...
```

## Front Matter to Payload Mapping

- `title` -> `articleTitle`
- `sort` -> `sortName`
- `sortId` -> `sortId`
- `label` -> `labelName`
- `labelId` -> `labelId`
- `cover` -> `articleCover`
- `cover: " "` -> send a single-space cover placeholder when the user wants to publish without uploading a cover
- `coverBlank: true` -> same as `cover: " "`
- `coverFile` -> upload to `/api/api/resource/upload`, then use returned URL as `cover`
- local Markdown image paths such as `![图](./assets/demo.png)` -> upload to `/api/api/resource/upload`, then rewrite the Markdown content to use the returned URL
- local HTML image tags such as `<img src="./assets/demo.png">` -> upload to `/api/api/resource/upload`, then rewrite `src` to the returned URL
- `video` -> `videoUrl`
- `viewStatus` -> `viewStatus`
- `commentStatus` -> `commentStatus`
- `recommendStatus` -> `recommendStatus`
- `submitToSearchEngine` -> `submitToSearchEngine`
- If these switches are omitted on create, the backend defaults are:
  - `commentStatus = true`
  - `recommendStatus = false`
  - `viewStatus = true`
  - `submitToSearchEngine = viewStatus`
- `payType` -> `payType`
- `payAmount` -> `payAmount`
- `freePercent` -> `freePercent`
- `paymentPluginKey` -> choose the payment plugin checked through `/api/api/payment/plugin/status`
- `paymentConfigFile` -> local JSON file used with `/api/api/payment/plugin/configure` when the target payment plugin still needs configuration
- `requirePaid` -> fail instead of auto-downgrading to `payType: 0`
- `allowCreateTaxonomy` -> allow creating both category and tag when they do not already exist
- `allowCreateSort` -> allow creating a missing category
- `allowCreateLabel` -> allow creating a missing tag
- `password` -> `password`
- `tips` -> `tips`
- `skipAiTranslation` -> `skipAiTranslation`
- `pendingTranslationLanguage` -> `pendingTranslationLanguage`
- `pendingTranslationTitle` -> `pendingTranslationTitle`
- `pendingTranslationContent` -> `pendingTranslationContent`
- `uploadLocalImages: false` -> disable automatic upload and rewrite of local Markdown or HTML images
- `markdownImageType` -> optional upload resource type override for local article images, default `articlePicture`
- `markdownImageStoreType` -> optional storage backend override for local article images
- `coverStoreType` -> optional storage backend override for local cover uploads

## Paywall Fields

- Default recommendation for personal blogs: `payType: 0`
- `payType: 0` 免费文章
- `payType: 1` 按文章付费
- `payType: 2` 会员专属
- `payType: 3` 赞赏解锁
- `payType: 4` 固定金额解锁
- `payAmount` 仅在付费模式需要时传入
- `freePercent` 为免费预览百分比，未传时后端默认 `30`
- 当 `payType > 0` 时，后台要求插件管理里已有启用且已配置的 `payment` 插件，否则 API 会拒绝创建或更新付费文章
- 若已安装 payment 插件但尚未配置，可先调用 `/api/api/payment/plugin/status` 获取 `configSchema` 和 `missingFields`，再调用 `/api/api/payment/plugin/configure`
- `status` 接口不会返回 token/privateKey 等敏感字段明文，只会返回是否已填写
- 单空格封面只是和后台发文页保持一致，表示“本次不上传自定义封面”；前台读取文章时是否展示默认/随机封面，仍由现有博客展示逻辑决定

## Payload Minimums

Required for create:

- `articleTitle`
- `articleContent`
- `sortId` or `sortName`
- `labelId` or `labelName`

Recommended workflow for category/tag safety:

1. Call `GET /api/api/categories`
2. Call `GET /api/api/tags`
3. Reuse exact matches when possible
4. Only allow new category/tag creation after explicit confirmation

Required for update:

- `id`
- `articleTitle`
- `articleContent`

Optional for update:

- `sortId` or `sortName`
- `labelId` or `labelName`
- `viewStatus`
- any other publish flags that should remain unchanged

If `viewStatus` is `false`, also require:

- `password`
- `tips`

## Upload Request

Upload a local cover file or local article image before creating or updating an article:

```http
POST /api/api/resource/upload
X-API-KEY: <api-key>
Content-Type: multipart/form-data
```

Fields:

- `file`: binary file
- `type`: optional, usually `articleCover`
- `relativePath`: optional custom storage path
- `storeType`: optional storage backend override

Recommended OpenClaw asset flow:

1. Save the user-provided image into the same working directory tree as the Markdown draft
2. Reference it from Markdown with a relative path such as `![截图](./assets/screenshot.png)`
3. Let `publish_post.py` upload that file through `/api/api/resource/upload`
4. Let the script replace the local path with the returned URL before it calls `/api/api/article/createAsync` or `/api/api/article/updateAsync`

## Async Task Flow

1. `POST /api/api/article/createAsync` or `POST /api/api/article/updateAsync`
2. Read `taskId` from the response
3. Poll `GET /api/api/article/task/{taskId}`
4. Stop when `completed=true`

Final states:

- `success`: article saved and follow-up processing completed
- `partial_success`: article saved, but a follow-up step such as translation failed
- `failed`: task failed

## Payment Plugin Flow

1. `GET /api/api/payment/plugin/status`
2. 若返回 `missingFields`，准备 payment 配置
3. `POST /api/api/payment/plugin/configure`
4. `POST /api/api/payment/plugin/testConnection`
5. 连接成功后，再发布 `payType > 0` 的文章

Example configure request:

```http
POST /api/api/payment/plugin/configure
X-API-KEY: <api-key>
Content-Type: application/json
```

```json
{
  "pluginKey": "afdian",
  "pluginConfig": {
    "userId": "your-user-id",
    "apiToken": "your-api-token"
  },
  "activate": true
}
```

## Article Ops Flow

For existing article operations:

1. `GET /api/api/article/list`
2. Prefer exact title match on `articleTitle` or use `id`
3. `GET /api/api/article/{id}` to inspect the current state
4. `POST /api/api/article/updateAsync` to update or hide
5. `GET /api/api/article/task/{taskId}` to poll when needed

For article listing by taxonomy:

- `manage_blog.py list-articles --sort-id <id>`
- `manage_blog.py list-articles --label-id <id>`
- `manage_blog.py list-articles --sort-name "<exact category name>"`
- `manage_blog.py list-articles --label-name "<exact tag name>"`
- When name-based filters are used, the script first calls `/api/api/categories` or `/api/api/tags`
- It prefers exact matches
- If exact matches fail, it returns close candidates and stops for confirmation
- It never auto-selects a fuzzy category or tag candidate

## Strategy Brief Requirements

Article create and refresh briefs must provide:

- `taskType`
- `primaryGoal`
- `targetAudience`
- `publishIntent`
- `reasoning`
- `selectedAngle`
- `alternativesConsidered`

Optional article brief fields with runtime meaning:

- `monetizationIntent`
- `whyPaid`

Ops briefs for update and hide must provide:

- `taskType`
- `primaryGoal`
- `reasoning`
- `expectedOutcome`

Deletion policy:

- Do not delete articles through this skill.
- Use hide instead when the user wants a post taken down from normal public access.

For hiding an article:

- send `viewStatus: false`
- also send `password`
- also send `tips`

## Theme And Analytics Flow

- `GET /api/api/article-theme/status`
- `POST /api/api/article-theme/activate`
- `GET /api/api/article/analytics/{id}`
- `GET /api/api/analytics/site/visits?days=7`
- `GET /api/api/analytics/site/visits?days=30`

## Controlled SEO Flow

- `GET /api/api/seo/status`
- `GET /api/api/seo/config`
- `POST /api/api/seo/config`
- `POST /api/api/seo/sitemap/update`

`GET /api/api/seo/status` returns:

- `enabled`
- `searchEnginePushEnabled`
- `siteVerificationConfigured`
- `sitemapAvailable`
- `lastSitemapUpdateTime`
- `searchEnginePingEnabled`
- `sitemapBaseUrl`
- `summary`

`POST /api/api/seo/sitemap/update` returns:

- `triggered`
- `lastSitemapUpdateTime`
- `searchEnginePingEnabled`
- `siteBaseUrl`
- `message`

Allowed SEO config fields:

- `enable`
- `site_description`
- `site_keywords`
- `default_author`
- `og_image`
- `site_logo`
- `og_site_name`
- `og_type`
- `twitter_card`
- `twitter_site`
- `twitter_creator`
- `baidu_push_enabled`
- `google_index_enabled`
- `bing_push_enabled`
- `baidu_site_verification`
- `google_site_verification`

Explicitly not supported through API-key:

- `custom_head_code`
- `robots_txt`
- PWA icons and screenshots
- native app related fields
- raw image-processing endpoints
- backend SEO cache-management endpoints
