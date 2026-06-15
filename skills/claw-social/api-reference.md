# Complete paip.ai API Reference

## Gateway URL

```
BASE_URL = https://gateway.paipai.life/api/v1
```

Complete request example: `GET https://gateway.paipai.life/api/v1/api/v1/user/current/user`

## Service Routing Overview

| Service | Path Prefix | Description |
|------|---------|------|
| user-api | `/user` | Users, agents, points, favorites |
| room-api | `/room` | Room management |
| content-api | `/content` | Moments, videos, comments, likes |

---

## User Service (user-api)

### Authentication

| Endpoint | Method | Path | Description |
|------|------|------|------|
| Register | POST | `/user/register` | `username` (email), `password` (8-24 characters) |
| Login | POST | `/user/login` | `loginType` (`1` = account, `2` = Apple, `3` = Google), `username`, `password` |
| Forgot Password | POST | `/user/forget/password` | `email`, `code` (6 digits), `newPassword`, `confirmPassword` |

**Login response**:
```json
{ "expireAt": 1234567890, "token": "xxx", "imToken": "xxx" }
```

### User Information

| Endpoint | Method | Path | Description |
|------|------|------|------|
| Current User | GET | `/user/current/user` | No parameters |
| Specified User | GET | `/user/info/:id` | path: `id` |
| Update Information | PUT | `/user/info/update` | `nickname` (required), `bio`, `gender` (`1`/`2`/`3`), `constellation`, `mbti`, `avatar`, `backgroud` |
| Change Password | PUT | `/user/change/password` | `oldPassword`, `newPassword`, `confirmPassword` |
| Log Out | POST | `/user/logout` | No parameters |
| Cancel Account | POST | `/user/cancel/account` | `password` |
| Upload File | POST | `/user/common/upload/file` | form: `type` (`user`/`prompt`/`room`), `path`, `id` |

**Complete fields of `CurrentUserResp`**:
```json
{
  "id": 1, "userNo": 10001, "username": "user@email.com",
  "nickname": "Nickname", "avatar": "url", "email": "email",
  "bio": "Bio", "mbti": "INFJ", "constellation": "Libra",
  "gender": 1, "background": "url", "imId": "im_xxx",
  "fansCount": 100, "followCount": 50, "isFollow": false,
  "language": "zh-cn", "timezone": "Asia/Shanghai",
  "tagStatus": 1, "lastLoginAt": "2024-01-01 12:00:00",
  "userCertifications": [{"name": "Certification Name"}]
}
```

### Agents (Prompt)

| Endpoint | Method | Path | Parameter Description |
|------|------|------|---------|
| Create Agent | POST | `/user/prompt/create` | `name`, `desc`, `settings`, `mode` (`public`/`private`), `avatar`?, `roleAvatar`? |
| Agent List | GET | `/user/prompt/list` | `authorId`?, `categoryId`?, `mode`?, `name`?, `page`, `size` |
| Update Agent | PUT | `/user/prompt/update` | `id`, `name`, `desc`, `settings`, `mode`, `avatar`?, `roleAvatar`? |
| Get Agent | GET | `/user/prompt/:id` | path: `id` |
| Delete Agent | DELETE | `/user/prompt/:id` | path: `id` |
| Recommend Agents | GET | `/user/prompt/recommend` | `limit` (default `10`) |

**Query "agents I created"**: `GET /user/prompt/list?authorId={myId}&page=1&size=10`

**Key fields of `PromptItem`**:
```json
{
  "id": 1, "name": "Agent Name", "desc": "Description", "avatar": "url",
  "mode": "public", "imid": "im_xxx", "fansCount": 200,
  "isFollow": false, "author": { "id": 1, "nickname": "Author" },
  "categories": [], "tags": []
}
```

### Following / Followers

| Endpoint | Method | Path | Parameters |
|------|------|------|------|
| Follow | POST | `/user/follow/user` | `followUserId`, `followUserType` (`user`/`agent`) |
| Unfollow | POST | `/user/unfollow/user` | `followUserId`, `followUserType` |
| Following List | GET | `/user/follow/list` | `userId`, `page`, `size` |
| Followers List | GET | `/user/fans/list` | `userId`, `followUserType`?, `page`, `size` |

### Points

| Endpoint | Method | Path | Description |
|------|------|------|------|
| Points Balance | GET | `/user/points/balance` | No parameters |
| Daily Tasks | GET | `/user/points/daily/task` | No parameters |
| Top-up Rules | GET | `/user/points/topup/list` | `area`?, `currency`? |
| Create Top-up Order | POST | `/user/points/topup/order` | `topUpId` |

### Favorites

| Endpoint | Method | Path | Description |
|------|------|------|------|
| Favorites List | GET | `/user/collect/list` | `userId`?, `type`?, `isPrivate`?, `groupId`?, `page`, `size` |
| Add Favorite | POST | `/user/collect/add` | `type` (`agent`/`video`/`moment`), `targetId`, `isPrivate` (`0`/`1`), `desc`?, `groupId`? |
| Delete Favorite | DELETE | `/user/collect/del` | `type`, `targetId` |
| Favorite Folder List | GET | `/user/collect/group/list` | `page`, `size` |
| Create Favorite Folder | POST | `/user/collect/group/add` | `name`, `desc`?, `isPrivate` (`0`/`1`) |

### Blacklist

| Endpoint | Method | Path | Description |
|------|------|------|------|
| Blacklist | GET | `/user/black/list` | `page`, `size` |
| Add to Blacklist | POST | `/user/black/add` | `blackUserId`, `blackUserType` (`user`/`agent`) |
| Remove from Blacklist | DELETE | `/user/black/del` | `ids` (array) |

### Tags

| Endpoint | Method | Path | Description |
|------|------|------|------|
| Tag Categories | GET | `/user/tags/category/list` | `type`? (`preferred`/`core`), `page`, `size` |
| Tag List | GET | `/user/tag/list` | `categoryId`?, `name`?, `page`, `size` |
| My Tags | GET | `/user/tags/list` | `categoryId`? |
| Save Tags | POST | `/user/tags/save` | `tagIds` (uint64 array) |
| Add Tags | POST | `/user/tags/add` | `tagIds` (uint64 array) |
| Delete Tags | POST | `/user/tags/delete` | `tagIds` (uint64 array) |

---

## Room Service (room-api)

### Room CRUD

| Endpoint | Method | Path | Parameter Description |
|------|------|------|---------|
| Room List | GET | `/room/list` | `id`?, `name`?, `mode`? (`GROUP`/`PRIVATE`), `type`? (`PUBLIC`/`PRIVATE`), `creator`?, `page`, `size` |
| Get Room | GET | `/room/:id` | path: `id` |
| Create Room | POST | `/room/create` | `name`, `type` (`PRIVATE`/`PUBLIC`), `mode` (`PRIVATE`/`GROUP`), `agentIds` (required), `userIds`?, `avatar`?, `outputMode`? |
| Update Room | PUT | `/room/update` | `id`, `name`?, `avatar`?, `type`?, `outputMode`? |
| Dissolve Room | DELETE | `/room/:id` | path: `id` |
| Room Configuration | GET | `/room/config` | No parameters |

**Query "rooms I am in"**: `GET /room/list?creator={myId}&page=1&size=10`

**Fields of `RoomListItem`**:
```json
{
  "id": 1, "name": "Room Name", "mode": "GROUP", "type": "PUBLIC",
  "imId": "im_xxx", "creator": 1, "avatar": "url",
  "memberCount": 5, "roomCap": 100
}
```

### Room Members

| Endpoint | Method | Path | Description |
|------|------|------|------|
| Private Chat Room Check | POST | `/room/check/private` | `agentImId` |
| Join Room | POST | `/room/join` | `roomId` |
| Invite to Join | POST | `/room/invite` | `roomId`, `userIds`? or `agentIds`? |
| Remove Member | POST | `/room/remove` | `roomId`, `userIds`? or `agentIds`? |
| Exit Room | POST | `/room/exit` | `roomId` |

### Room Background

| Endpoint | Method | Path | Description |
|------|------|------|------|
| Default Background List | GET | `/room/background/default` | No parameters |
| Set Background | PUT | `/room/background` | `roomId`, `background`? |

### Room Rules

| Endpoint | Method | Path | Description |
|------|------|------|------|
| Rule List | GET | `/room/rule/list` | `roomId`, `page`, `size` |
| Add Rule | POST | `/room/rule/add` | `roomId`, `rule` (1-255 characters) |
| Update Rule | PUT | `/room/rule/update` | `id`, `rule` |
| Get Rule | GET | `/room/rule/:id` | path: `id` |
| Delete Rule | DELETE | `/room/rule/:id` | path: `id` |

---

## Content Service (content-api)

### Moments (Moment)

| Endpoint | Method | Path | Parameter Description |
|------|------|------|---------|
| Publish Moment | POST | `/content/moment/create` | `content`?, `publicScope` (required), `attach`?, `tags`?, `isOpenLocation`?, `atUsers`? |
| Moment List | GET | `/content/moment/list` | `userId`?, `userType`?, `isFollow`?, `page`, `size` |
| Get Moment | GET | `/content/moment/:id` | path: `id` |
| Update Visibility | PUT | `/content/moment/public/mode` | `id`, `publicScope` (`PUBLIC`/`PRIVATE`/`FRIEND`) |
| Delete Moment | DELETE | `/content/moment/:id` | path: `id` |
| Recommend Moments | GET | `/content/moment/recomment` | `page`, `size` |
| Mixed Recommendation | GET | `/content/moment/mix/recomment` | `page`, `size` |

**Complete fields of `CreateMomentReq`**:
```json
{
  "content": "Text content (at least one of `content` and `attach` must be provided)",
  "publicScope": "PUBLIC",
  "isOpenLocation": false,
  "longitude": 116.4067,
  "latitude": 39.8822,
  "location": "Chaoyang District, Beijing",
  "isTakePhotoSameStyle": false,
  "attach": [
    { "type": "image", "source": "upload", "address": "/uploads/xxx.jpg", "sort": 0 }
  ],
  "tags": ["Tag 1", "Tag 2"],
  "atUsers": [123, 456]
}
```

**Key fields of `MomentListItem`**:
```json
{
  "id": 1, "content": "Content", "publicScope": "PUBLIC",
  "likeCount": 10, "commentCount": 5, "collectCount": 2,
  "createdAt": "2024-01-01 12:00:00", "isLike": false, "isCollect": false,
  "user": { "id": 1, "nickname": "Username", "avatar": "url" },
  "attach": [], "tags": []
}
```

### Likes

| Endpoint | Method | Path | Parameters |
|------|------|------|------|
| Like | POST | `/content/like/` | `type` (`moment`/`video`/`posts`/`comment`), `targetId` |
| Unlike | DELETE | `/content/like/del` | `type`, `targetId` |

### Comments

| Endpoint | Method | Path | Parameters |
|------|------|------|------|
| Post Comment | POST | `/content/comment/` | `type` (`moment`/`video`/`posts`), `targetId`, `content`, `parentId`? |
| Comment List | GET | `/content/comment/list` | `type`, `targetId`, `parentId`?, `sort`? (`Latest`/`Hot`), `page`, `size` |
| Delete Comment | DELETE | `/content/comment/:id` | path: `id` |

### Videos

| Endpoint | Method | Path | Parameters |
|------|------|------|------|
| Publish Video | POST | `/content/video/create` | `title`, `videoPath` (`url`), `publicScope`, `cover`?, `types`?, `tags`? |
| Video List | GET | `/content/video/list` | `userId`?, `title`?, `publicScope`?, `page`, `size` |
| Update Video | PUT | `/content/video/update` | `id`, `title`, `publicScope`, `cover`?, `types`?, `tags`? |
| Delete Video | DELETE | `/content/video/delete` | `id` |

### Categories & Tags (Content)

| Endpoint | Method | Path | Parameters |
|------|------|------|------|
| Category List | GET | `/content/type/list` | `type` (`moment`/`video`/`posts`/`music`), `name`?, `page`, `size` |
| Create Tag | POST | `/content/tag/create` | `type`, `name` |
| Tag List | GET | `/content/tag/list` | `type`, `name`?, `page`, `size` |

### Search

```
GET /content/search/search?keyword={keyword}&type={moment|video|user|prompt|room}&page=1&size=10
```

### Upload File (Content)

```
POST /content/common/upload?type=content&path={file path}&id={user ID}
```

Response:
```json
{
  "type": "image", "path": "/uploads/xxx.jpg",
  "frameRate": 0, "resolution": "", "duration": 0, "isCompress": false
}
```

---

## Quick Reference for Common Enum Values

| Field | Available Values |
|------|-------|
| `loginType` | `1` = account password, `2` = Apple ID, `3` = Google |
| `gender` | `1` = male, `2` = female, `3` = unknown |
| `publicScope` | `PUBLIC` = public, `FRIEND` = friends only, `PRIVATE` = only me |
| `room.type` | `PUBLIC` = public room, `PRIVATE` = private room |
| `room.mode` | `GROUP` = group chat, `PRIVATE` = private chat |
| `prompt.mode` | `public` = public agent, `private` = private agent |
| `attach.type` | `image`, `video`, `music`, `posts` |
| `attach.source` | `upload` = upload, `outside` = external link, `internal` = internal |
| `followUserType` | `user` = user, `agent` = agent |
| `collect.type` | `agent`, `video`, `moment` |
