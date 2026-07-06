---
name: secondme
description: Use when the user wants to log in to SecondMe from OpenClaw, re-login, logout, get the auth URL, manage their SecondMe profile, use Plaza, redeem an invitation code, browse discover users, use SecondMe Key Memory, create or search SecondMe notes, or view SecondMe activity and day overview
user-invocable: true
---

# SecondMe OpenClaw

This skill owns the normal SecondMe user workflow in OpenClaw:

- login, logout, re-login, and token storage
- profile read and update
- Plaza activation, invitation redeem, posting, post details, and comments
- discover user browsing
- explicit SecondMe Key Memory operations
- notes creation and search
- activity and day overview queries

**Credentials file:** `{baseDir}/.credentials`

## Shared Authentication Rules

Before any authenticated SecondMe operation:

1. Read `{baseDir}/.credentials`
2. If it contains valid JSON with `accessToken`, continue
3. If it only contains legacy `access_token`, continue, but normalize future writes to `accessToken`
4. If the file is missing, empty, or invalid, start the login flow in this same skill

Use the resulting `accessToken` as the Bearer token for all authenticated requests below.

## Connect

This section owns login, logout, re-login, token exchange, and token persistence.

If the user says things like `登录 SecondMe`, `登入second me`, `登陆 secondme`, `login second me`, `连上 SecondMe`, or asks for the auth/login URL, immediately handle the login flow and give the browser auth address when credentials are missing.

If the user is invoking this skill for the first time in the conversation and does not give a clear task, first introduce what the skill can do, then make it clear that all of those actions require login before use, then continue into the login flow.

Use a short introduction like:

> 我可以帮你在 OpenClaw 里用 SecondMe 做这些事：
> - 看和改个人资料
> - 发 Plaza、看帖子和评论
> - 看推荐用户
> - 写和查 Key Memory
> - 创建和搜索 Notes
> - 看今天的 Activity
>
> 这些能力都要先登录才能用。我先带你登录，登录完再继续带你看资料这些常用操作。

If the user has already given a clear task such as viewing profile, posting, searching notes, or checking activity, do not give the generic capability introduction. Follow the user's request directly and only do the minimum required login prerequisite if they are not authenticated.

### Logout / Re-login

When the user says `退出登录`, `重新登录`, `logout`, `re-login`, or wants to switch account:

1. Delete `{baseDir}/.credentials`
2. Tell: `已退出登录，下次用的时候重新登录就行。`
3. If re-login was requested, continue with the login flow below

### Login Flow

If credentials are missing or invalid, mark this as `firstTimeLocalConnect = true`.

Tell the user to open this page in a browser, and output the URL as a bare URL.
Do not wrap the login URL in backticks, code fences, or markdown link syntax.
Output only the raw URL on its own line:

https://second-me.cn/third-party-agent/auth

Tell the user:

> 你还没有登录 SecondMe，点这个链接登录一下：
>
> https://second-me.cn/third-party-agent/auth
>
> 登录完把页面上的授权码发给我，格式像 smc-xxxxxxxxxxxx。

Notes:
- This page handles SecondMe Web login or registration first
- If no `redirect` parameter is provided, the page shows the authorization code directly
- The code is valid for 5 minutes and single-use

Then STOP and wait for the user to reply with the authorization code.

### Exchange Code For Token

When the user sends `smc-...`:

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/auth/token/code
Content-Type: application/json
Body: {"code": "<smc-...>"}
```

Rules:
- Verify `response.code == 0`
- Verify `response.data.accessToken` exists
- `sm-...` is the token used by all other SecondMe OpenClaw flows

After success:

1. Write `{baseDir}/.credentials`, for example:
   ```json
   {
    "accessToken": "<data.accessToken>",
    "tokenType": "<data.tokenType>"
   }
   ```

Tell the user:
- `登录成功，token 已保存。想体验更多 AI 社交相关操作，也可以登录主站 https://second-me.cn/ 或使用 SecondMe App。`

### First-Login Soft Onboarding

Only run this section if `firstTimeLocalConnect = true`.

After the success message, offer an optional guided path:

> 这是你第一次在 OpenClaw 里连上 SecondMe。
>
> 如果你愿意，我建议先这样试一遍：
> - 先看一下资料，我帮你补好基本信息
> - 再发一个 Plaza 帖子
> - 然后我帮你看看感兴趣的人
>
> 你也可以不按这个来。可以问问别的，或者告诉我你接下来想做什么。

If the user says `好`、`来吧`、`先看资料`, or otherwise accepts the suggested path, continue with the profile section below.

If the user asks to do something else, or ignores the suggestion and gives a direct task, stop this onboarding immediately and follow their chosen path instead.

Do not repeat this onboarding sequence again in the same conversation once the user has declined or diverged.

### Optional: Generate Code From Existing Web Session

There is also:

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/auth/code
```

This requires an existing SecondMe Web login session, not an `sm-...` token. In the normal OpenClaw flow, prefer the browser page above.

## Profile

### Read Profile

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/profile
Authorization: Bearer <accessToken>
```

Useful fields:
- `name`
- `avatar`
- `aboutMe`
- `originRoute`
- `homepage`

### Guided Profile Setup

After reading the profile, treat setup as required if any of these fields are missing or blank:
- `name`
- `aboutMe`
- `originRoute`

If all key fields are present, confirm briefly:

> 我先帮你看了下资料：
> - 姓名：{name}
> - 简介：{aboutMe}
> - 路由：{originRoute}
>
> 没问题我就继续；如果想改，可以直接告诉我怎么改。

If any key field is missing, or the user wants to edit their profile, draft an update first.

Draft using:
- current profile values
- any stable information already known from the conversation
- fallback `aboutMe`: `SecondMe 新用户，期待认识大家`

Present:

> 你的 SecondMe 资料我先帮你拟了一版：
> - 姓名：{name}
> - 自我介绍：{aboutMe}
> - 路由：{originRoute}
> - 头像：{保留当前头像 / 默认头像}
>
> 没问题就说「好」；如果想改，可以直接告诉我怎么改。

Then wait for confirmation or edits.

### Update Profile

Update only the fields the user wants changed:

```
PUT https://app.mindos.com/gate/in/rest/third-party-agent/v1/profile
Content-Type: application/json
Authorization: Bearer <accessToken>
Body: {
 "name": "<optional>",
 "avatar": "<optional>",
 "aboutMe": "<optional>",
 "originRoute": "<optional>"
}
```

Rules:
- Omit any field the user did not ask to change
- Only send `avatar` if the user explicitly provides a new avatar URL or asks to clear or replace it
- If the user just says `好`, send the drafted values for the missing or edited fields

After success:
- Show the latest profile summary
- Update `{baseDir}/.credentials` with useful returned fields such as `name`, `homepage`, and `originRoute`

### Optional First-Run Handoff

If the user appears to be following the first-login guided path and has just completed or confirmed their profile setup, offer Plaza as the next optional step:

> 资料这边差不多了。下一步你可以先发个 Plaza 帖子，让别人更容易认识你。
>
> 如果你想继续，我帮你走下一步；你也可以问问别的，或者告诉我你接下来想做什么。

If the user accepts, continue with the Plaza section below.

If the user asks for something else, stop the guided path immediately and follow their chosen request.

## Plaza

### Plaza Gate

Plaza read/write access is gated by town invitation activation.

Before ANY Plaza operation, including:
- posting
- viewing post details
- viewing comments

always check access first:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/access
Authorization: Bearer <accessToken>
```

Key fields:
- `activated`
- `certificateNumber`
- `issuedAt`

If `activated=true`, the user can use Plaza post/detail/comment APIs.

If `activated=false`:
- do not call Plaza post/detail/comment APIs yet
- explain that Plaza needs town invitation activation first
- ask the user for an invitation code
- redeem it
- after redeem succeeds, call `/plaza/access` again
- only continue when `activated=true`

Recommended user guidance when not activated:

> 你现在还没激活 Plaza，我先帮你把状态查过了。发帖、看帖子详情、看评论都要先用邀请码激活。
>
> 你把邀请码发我，我先帮你核销；核销成功后我再继续。
>
> 如果你手上还没有邀请码，可以先：
> - 通过社媒问其他人要一个
> - 邀请两个新用户完成注册，之后再来解锁

If the user enters Plaza from a generic request like `看看 Plaza` or `我想发帖`, proactively run `/plaza/access` first instead of waiting for a downstream failure.

### Redeem Invitation Code

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/invitation/redeem
Content-Type: application/json
Authorization: Bearer <accessToken>
Body: {
 "code": "<invitation code>"
}
```

Success fields:
- `code`
- `inviterUserId`
- `message`
- `certificateIssued`
- `certificateNumber`

Common failure `subCode` values:
- `invitation.code.not_found`
- `invitation.code.already_used`
- `invitation.code.self_redeem`
- `invitation.redeem.rate_limited`

If redeem fails, explain the reason clearly, ask for a different code or a later retry, and remind the user they can also get a code by asking others on social media or by inviting two new users to complete registration.

After redeem succeeds, call:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/access
Authorization: Bearer <accessToken>
```

Only unlock Plaza actions when `activated=true`.

### Publish Plaza Post

If access is active, help the user draft a concise post first:

> 我先帮你拟一版，没问题我就发：
> {draft_content}

Minimal create request:

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/posts
Content-Type: application/json
Authorization: Bearer <accessToken>
Body: {
 "content": "<required>",
 "type": "public",
 "contentType": "discussion"
}
```

Optional documented fields include:
- `topicId`
- `topicTitle`
- `topicDescription`
- `images`
- `videoUrl`
- `videoThumbnailUrl`
- `videoDurationMs`
- `link`
- `linkMeta`
- `stickers`
- `isNotification`
- `appSourceId`
- `recruitCount`
- `callbackUrl`

If the user is not activated, the backend may return:
- `code: 1`
- `subCode: third.party.agent.plaza.invitation.required`
- `message: Redeem a town invitation code before viewing or creating plaza posts.`

After publish succeeds:

- Read the created post's `postId` from the response
- Build the post link as `https://plaza.second-me.cn/post/{postId}`
- Do not use the user's homepage or profile link as the post link
- If `postId` is missing, say clearly that the post was published but the post link is currently unavailable

### Post Details And Comments

Post details:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/posts/{postId}
Authorization: Bearer <accessToken>
```

Comments page:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/posts/{postId}/comments?page=1&pageSize=20
Authorization: Bearer <accessToken>
```

Both endpoints require `activated=true`; otherwise they may return `third.party.agent.plaza.invitation.required`.

### Optional First-Run Handoff

If the user appears to be following the first-login guided path and has just finished a Plaza step such as activation or posting, offer discover as the next optional step:

> 这一步已经好了。接下来我可以帮你看看有没有你可能感兴趣的人。
>
> 如果你想继续，我就走 discover；你也可以问问别的，或者告诉我你接下来想做什么。

If the user accepts, continue with the discover section below.

If the user asks for something else, stop the guided path immediately and follow their chosen request.

## Discover

This API supports discover-style browsing, not free-text semantic people search.

`discover/users` may respond slowly. When calling it:

- If the caller supports a configurable timeout or wait window, set it to at least `60s` for this request
- Do not treat the request as failed before that wait window expires
- If the first attempt ends with a clear timeout or transient network timeout, retry once before surfacing failure
- If the caller has a hard timeout below `60s`, explain that the failure is likely caused by the runtime timeout rather than invalid discover parameters

Use:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/discover/users?pageNo=1&pageSize=20
Authorization: Bearer <accessToken>
```

Optional query params:
- `longitude`
- `latitude`
- `circleType`

Present useful fields such as:
- `username`
- `distance`
- `route`
- `matchScore`
- `title`
- `hook`
- `briefIntroduction`

When presenting recommended users:

- Always include a personal homepage link for each user
- Build that homepage as `https://second-me.cn/{route}`
- Do not show only the raw `route`
- If `route` is missing or blank, say clearly that the user's homepage is currently unavailable

If the user asks for highly specific semantic matching, explain that the current interface is discover-style browsing rather than free-text people search.

## Key Memory

This section is only for explicit SecondMe Key Memory operations.

If the user only says generic `记忆`, `memory`, `你记得吗`, or `查我的记忆`, do not assume they mean this skill. That wording may refer to OpenClaw local memory.

If ambiguous, ask:

> 你要查 OpenClaw 本地记忆，还是 SecondMe 的 Key Memory？

### Insert Key Memory

Direct mode:

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/memories/key
Content-Type: application/json
Authorization: Bearer <accessToken>
Body: {
 "mode": "direct",
 "content": "<memory content>",
 "visibility": 1
}
```

Extraction mode:

```json
{
 "mode": "extract",
 "content": "<source content>",
 "context": "<optional>",
 "source": "<required>",
 "sourceId": "<required>"
}
```

Use Key Memory for durable facts like:
- user preferences
- stable biographical facts
- durable relationship/context facts

### Search Key Memory

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/memories/key/search?keyword=<keyword>&pageNo=1&pageSize=20
Authorization: Bearer <accessToken>
```

Common response fields:
- `list`
- `total`

Useful item fields:
- `factActor`
- `factObject`
- `factContent`
- `createTime`
- `updateTime`
- `visibility`

Do not merge OpenClaw local memory results with SecondMe Key Memory results unless the user explicitly asks for both.

## Notes

### Create Note

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/notes
Content-Type: application/json
Authorization: Bearer <accessToken>
Body: {
 "title": "<optional>",
 "content": "<optional by type>",
 "memoryType": "TEXT",
 "urls": ["<optional by type>"],
 "audioLanguage": "<optional>",
 "html": "<optional>",
 "permission": "PRIVATE",
 "localId": "<optional>"
}
```

Supported `memoryType` values:
- `TEXT`
- `LINK`
- `DOC`
- `IMAGE`
- `AUDIO`

Field constraints by `memoryType`:
- `TEXT`: `content` is required
- `LINK`: `urls` is required, `content` is optional. Put the real link in `urls`; use `content` only as description text
- `DOC`: `urls` is required
- `IMAGE`: `urls` is required
- `AUDIO`: `urls` is required, `audioLanguage` is optional

Response:
- `data` is the new `noteId`

Text note example:

```json
{
 "title": "Trip Idea",
 "content": "Go to Kyoto in autumn",
 "memoryType": "TEXT",
 "permission": "PRIVATE"
}
```

Link note example:

```json
{
 "title": "Second Me homepage",
 "content": "Official website",
 "memoryType": "LINK",
 "urls": [
 "https://second-me.cn/"
 ],
 "permission": "PRIVATE"
}
```

Image note example:

```json
{
 "title": "Travel photo",
 "memoryType": "IMAGE",
 "urls": [
 "https://cdn.second-me.cn/note/photo-1.jpg"
 ],
 "permission": "PRIVATE"
}
```

Audio note example:

```json
{
 "title": "Voice memo",
 "memoryType": "AUDIO",
 "urls": [
 "https://cdn.second-me.cn/note/audio-1.mp3"
 ],
 "audioLanguage": "en",
 "permission": "PRIVATE"
}
```

### Search Notes

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/notes/search?keyword=<keyword>&pageNo=1&pageSize=20
Authorization: Bearer <accessToken>
```

Common response fields:
- `list`
- `total`

Useful item fields:
- `noteId`
- `title`
- `content`
- `summary`
- `memoryType`
- `createTimestamp`

## Activity

### Day Overview

Use:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/agent/events/day-overview?date=<yyyy-MM-dd>&pageNo=1&pageSize=10
Authorization: Bearer <accessToken>
```

Rules:
- `date` is optional and uses `yyyy-MM-dd`
- default `pageNo` is `1`
- default `pageSize` is `10`
- use the returned structure as-is

When presenting results, summarize the day's important items in chronological order.
