---
name: ding-skills
description: 钉钉操作助手（DingTalk）。当用户通过钉钉对话、或提到以下任何场景时必须使用此技能：查人（查下某某、搜一下某人、找一下谁谁）、查部门、查手机号、查工号、约会议（预约会议、创建会议、安排会议、开个会）、发消息（给某人发消息、群里发个通知）、查审批（我的审批、待审批、审批状态）、发起审批、同意/拒绝审批、查日程、创建日程、查员工数、查离职、开视频会议、钉钉知识库（查钉钉知识库、在钉钉创建文档、搜索钉钉文档、覆写钉钉文档）。注意：当用户从钉钉渠道发送消息时，"知识库"默认指钉钉知识库，不是飞书知识库。Use when user mentions anything about DingTalk or when the message comes from a DingTalk channel: looking up people, searching users/departments, scheduling meetings, creating conferences, sending messages, managing approvals, checking calendar events, querying employee info, DingTalk knowledge base operations (list workspaces, create/search/overwrite documents). When user is on DingTalk channel, "知识库" means DingTalk knowledge base, NOT Feishu.
---

# Ding Skills

钉钉全功能技能集：用户管理、部门管理、消息发送、OA审批、视频会议、日程管理。

## 前置要求

- 已设置环境变量 `DINGTALK_APP_KEY` 和 `DINGTALK_APP_SECRET`
- 钉钉应用已创建并拥有相应 API 权限

## 环境变量配置

```bash
export DINGTALK_APP_KEY="<your-app-key>"
export DINGTALK_APP_SECRET="<your-app-secret>"
export DINGTALK_ROBOT_CODE="<your-robot-code>"  # 可选，发消息时使用
```


## 重要：常用工作流（必读）

大部分钉钉 API 需要 `userId` 或 `unionId`，但用户通常只会说人名。**遇到人名时，必须先查人再执行操作。**

### 工作流1：按人名预约会议 / 创建视频会议

当用户说"帮我和张三、李四开个会"或"预约一个会议，参会人：张三、李四"时：

```
步骤1: python scripts/search_user.py "张三"  → 得到 userId
步骤2: python scripts/get_user.py "<userId>"  → 得到 unionId
步骤3: 对每个参会人重复步骤1-2
步骤4: python scripts/create_schedule_conference.py "<主题>" "<发起人unionId>" "<开始时间>" "<结束时间>" "<参会人unionId1,unionId2>" "[会议地点]"
```

### 工作流2：按人名发消息

当用户说"给张三发个消息"时：

```
步骤1: python scripts/search_user.py "张三"  → 得到 userId
步骤2: python scripts/send_user_message.py "<userId>" "<消息内容>"
```

注意：robotCode 自动从环境变量 DINGTALK_ROBOT_CODE 读取，也可作为第3个参数手动传入。

### 工作流3：按人名查审批

当用户说"查下张三的待审批"时：

```
步骤1: python scripts/search_user.py "张三"  → 得到 userId
步骤2: python scripts/list_user_todo_approvals.py "<userId>"
```

### 工作流4：按人名查日程

当用户说"查下张三今天的日程"时：

```
步骤1: python scripts/search_user.py "张三"  → 得到 userId
步骤2: python scripts/get_user.py "<userId>"  → 得到 unionId
步骤3: python scripts/list_events.py "<unionId>" "[开始时间]" "[结束时间]"
```

### 工作流5：在知识库中创建文档

当用户说"在知识库里创建一个文档"时：

```
步骤1: python scripts/search_user.py "张三"  → 得到 userId
步骤2: python scripts/get_user.py "<userId>"  → 得到 unionId
步骤3: python scripts/list_workspaces.py "<unionId>"  → 得到 workspaceId
步骤4: python scripts/create_doc.py "<workspaceId>" "<文档名>" "<unionId>"
```

### 工作流6：搜索知识库文档获取链接

当用户说"帮我找一下知识库里的《周报》"时：

```
步骤1: python scripts/search_user.py "张三"  → 得到 userId
步骤2: python scripts/get_user.py "<userId>"  → 得到 unionId
步骤3: python scripts/search_doc.py "<unionId>" "周报"  → 得到文档链接
```

### 通用规则

- **用户说人名** → 必须先调用 `search_user.py` 获取 userId
- **需要 unionId 的 API**（日历、会议相关） → 再调用 `get_user.py` 从 userId 获取 unionId
- **需要 userId 的 API**（消息、审批、部门相关） → search_user.py 的结果可直接使用
- **可以并行查询**多个用户以提高效率

## 功能列表

### 1. 搜索用户 (search-user)

根据姓名搜索用户，返回匹配的 UserId 列表。

```bash
python scripts/search_user.py "<搜索关键词>"
```

输出：

```json
{
  "success": true,
  "keyword": "张三",
  "totalCount": 3,
  "hasMore": false,
  "userIds": ["123456789", "987654321"]
}
```

### 2. 查询用户详情 (get-user)

获取指定用户的详细信息。

```bash
python scripts/get_user.py "<userId>"
```

输出：

```json
{
  "success": true,
  "user": {
    "userid": "user001",
    "name": "张三",
    "mobile": "138****1234",
    "dept_id_list": [12345],
    "unionid": "xxxxx"
  }
}
```

### 3. 根据手机号查询用户 (get-user-by-mobile)

```bash
python scripts/get_user_by_mobile.py "<手机号>"
```

输出：

```json
{ "success": true, "mobile": "13800138000", "userId": "user001" }
```

### 4. 根据 unionid 查询用户 (get-user-by-unionid)

```bash
python scripts/get_user_by_unionid.py "<unionid>"
```

输出：

```json
{ "success": true, "unionid": "xxxxx", "userId": "user001" }
```

### 5. 获取员工人数 (get-user-count)

```bash
python scripts/get_user_count.py [--onlyActive]
```

输出：

```json
{ "success": true, "onlyActive": false, "count": 150 }
```

### 6. 获取用户待审批数量 (get-user-todo-count)

```bash
python scripts/get_user_todo_count.py "<userId>"
```

输出：

```json
{ "success": true, "userId": "user001", "count": 5 }
```

### 7. 获取未登录用户列表 (list-inactive-users)

```bash
python scripts/list_inactive_users.py "<queryDate>" [--deptIds "id1,id2"] [--offset 0] [--size 100]
```

queryDate 格式: yyyyMMdd

输出：

```json
{ "success": true, "queryDate": "20240115", "userIds": ["user001"], "hasMore": false }
```

### 8. 查询离职记录列表 (list-resigned-users)

```bash
python scripts/list_resigned_users.py "<startTime>" ["<endTime>"] [--nextToken "xxx"] [--maxResults 100]
```

startTime/endTime 格式: ISO8601

输出：

```json
{
  "success": true,
  "startTime": "2024-01-01T00:00:00+08:00",
  "records": [{ "userId": "user001", "name": "张三", "leaveTime": "2024-01-15T10:00:00Z" }]
}
```

### 9. 搜索部门 (search-department)

```bash
python scripts/search_department.py "<搜索关键词>"
```

输出：

```json
{ "success": true, "keyword": "技术部", "totalCount": 2, "departmentIds": [12345, 67890] }
```

### 10. 获取部门详情 (get-department)

```bash
python scripts/get_department.py "<deptId>"
```

输出：

```json
{ "success": true, "department": { "deptId": 12345, "name": "技术部", "parentId": 1 } }
```

### 11. 获取子部门列表 (list-sub-departments)

根部门 deptId = 1。

```bash
python scripts/list_sub_departments.py "<deptId>"
```

输出：

```json
{ "success": true, "deptId": 1, "subDepartmentIds": [12345, 67890] }
```

### 12. 获取部门用户列表 (list-department-users)

自动分页获取所有用户（简略信息）。

```bash
python scripts/list_department_users.py "<deptId>"
```

输出：

```json
{
  "success": true,
  "deptId": 12345,
  "users": [{ "userId": "user001", "name": "张三" }, { "userId": "user002", "name": "李四" }]
}
```

### 13. 获取部门用户详情 (list-department-user-details)

分页获取，支持 cursor 和 size。

```bash
python scripts/list_department_user_details.py "<deptId>" [--cursor 0] [--size 100]
```

输出：

```json
{ "success": true, "deptId": 12345, "users": [...], "hasMore": true, "nextCursor": 100 }
```

### 14. 获取部门用户 ID 列表 (list-department-user-ids)

```bash
python scripts/list_department_user_ids.py "<deptId>"
```

输出：

```json
{ "success": true, "deptId": 12345, "userIds": ["user001", "user002"] }
```

### 15. 获取部门父部门链 (list-department-parents)

```bash
python scripts/list_department_parents.py "<deptId>"
```

输出：

```json
{ "success": true, "deptId": 12345, "parentIdList": [12345, 67890, 1] }
```

### 16. 获取用户所属部门父部门链 (list-user-parent-departments)

```bash
python scripts/list_user_parent_departments.py "<userId>"
```

输出：

```json
{ "success": true, "userId": "user001", "parentIdList": [12345, 1] }
```

### 17. 获取群内机器人列表 (get-bot-list)

```bash
python scripts/get_bot_list.py "<openConversationId>"
```

输出：

```json
{
  "success": true,
  "openConversationId": "cid",
  "botList": [{ "robotCode": "code", "robotName": "name" }]
}
```

### 18. 机器人发送群消息 (send-group-message)

robotCode 自动从环境变量 `DINGTALK_ROBOT_CODE` 读取，也可作为第3个参数手动传入。

```bash
python scripts/send_group_message.py "<openConversationId>" "<消息内容>" ["<robotCode>"]
```

输出：

```json
{ "success": true, "openConversationId": "cid", "robotCode": "code", "processQueryKey": "key", "message": "消息内容" }
```

### 19. 机器人发送单聊消息 (send-user-message)

robotCode 自动从环境变量 `DINGTALK_ROBOT_CODE` 读取，也可作为第3个参数手动传入。

```bash
python scripts/send_user_message.py "<userId>" "<消息内容>" ["<robotCode>"]
```

输出：

```json
{ "success": true, "userId": "user001", "robotCode": "code", "processQueryKey": "key", "message": "消息内容" }
```

### 20. 获取审批实例 ID 列表 (list-approval-instance-ids)

```bash
python scripts/list_approval_instance_ids.py "<processCode>" --startTime <timestamp> --endTime <timestamp> [--size 20] [--nextToken "xxx"]
```

输出：

```json
{ "success": true, "processCode": "PROC-XXX", "instanceIds": ["id1", "id2"], "totalCount": 2, "hasMore": false }
```

### 21. 获取审批实例详情 (get-approval-instance)

```bash
python scripts/get_approval_instance.py "<instanceId>"
```

输出：

```json
{
  "success": true,
  "instanceId": "xxx-123",
  "instance": {
    "processInstanceId": "xxx-123",
    "title": "请假申请",
    "status": "COMPLETED",
    "formComponentValues": [...],
    "tasks": [...]
  }
}
```

### 22. 查询用户发起的审批 (list-user-initiated-approvals)

```bash
python scripts/list_user_initiated_approvals.py "<userId>" [--startTime <ts>] [--endTime <ts>] [--maxResults 20]
```

输出：

```json
{ "success": true, "userId": "user001", "instances": [...], "totalCount": 5, "hasMore": false }
```

### 23. 查询用户抄送的审批 (list-user-cc-approvals)

```bash
python scripts/list_user_cc_approvals.py "<userId>" [--startTime <ts>] [--endTime <ts>] [--maxResults 20]
```

### 24. 查询用户待审批实例 (list-user-todo-approvals)

```bash
python scripts/list_user_todo_approvals.py "<userId>" [--maxResults 20]
```

输出：

```json
{ "success": true, "userId": "user001", "instances": [...], "totalCount": 3, "hasMore": false }
```

### 25. 查询用户已审批实例 (list-user-done-approvals)

```bash
python scripts/list_user_done_approvals.py "<userId>" [--startTime <ts>] [--endTime <ts>] [--maxResults 20]
```

### 26. 发起审批实例 (create-approval-instance)

```bash
python scripts/create_approval_instance.py "<processCode>" "<originatorUserId>" "<deptId>" '<formValuesJson>' [--ccList "user1,user2"]
```

formValuesJson 示例: `'[{"name":"标题","value":"请假申请"}]'`

输出：

```json
{ "success": true, "processCode": "PROC-XXX", "originatorUserId": "user001", "instanceId": "xxx-new" }
```

### 27. 撤销审批实例 (terminate-approval-instance)

```bash
python scripts/terminate_approval_instance.py "<instanceId>" "<operatingUserId>" ["<remark>"]
```

输出：

```json
{ "success": true, "instanceId": "xxx-123", "message": "审批实例已撤销" }
```

### 28. 执行审批任务 (execute-approval-task)

同意或拒绝审批任务。

```bash
python scripts/execute_approval_task.py "<instanceId>" "<userId>" "<agree|refuse>" [--taskId "xxx"] [--remark "审批意见"]
```

输出：

```json
{ "success": true, "instanceId": "xxx-123", "userId": "user001", "action": "agree", "message": "已同意审批" }
```

### 29. 转交审批任务 (transfer-approval-task)

```bash
python scripts/transfer_approval_task.py "<instanceId>" "<userId>" "<transferToUserId>" [--taskId "xxx"] [--remark "转交原因"]
```

输出：

```json
{ "success": true, "instanceId": "xxx-123", "userId": "user001", "transferToUserId": "user002", "message": "审批任务已转交" }
```

### 30. 添加审批评论 (add-approval-comment)

```bash
python scripts/add_approval_comment.py "<instanceId>" "<commentUserId>" "<评论内容>"
```

输出：

```json
{ "success": true, "instanceId": "xxx-123", "userId": "user001", "message": "评论已添加" }
```

### 31. 创建即时视频会议 (create-video-conference)

立即创建视频会议并邀请参会人。

```bash
python scripts/create_video_conference.py "<会议主题>" "<发起人unionId>" "[邀请人unionId1,unionId2]"
```

输出：

```json
{ "success": true, "title": "测试会议", "conferenceId": "xxx", "conferencePassword": "123456" }
```

### 32. 关闭视频会议 (close-video-conference)

```bash
python scripts/close_video_conference.py "<conferenceId>" "<操作人unionId>"
```

输出：

```json
{ "success": true, "conferenceId": "xxx", "message": "视频会议已关闭" }
```

### 33. 创建预约会议 (create-schedule-conference)

通过日历 API 创建预约会议，自动关联钉钉视频会议，日程会出现在钉钉日历中。

```bash
python scripts/create_schedule_conference.py "<会议主题>" "<创建人unionId>" "<开始时间>" "<结束时间>" "[参会人unionId1,unionId2]" "[会议地点]"
```

时间格式: `"2026-03-16 14:00"` 或 ISO 8601

输出：

```json
{
  "success": true,
  "title": "周会",
  "eventId": "NXZCUEtxOGZMN3JpcDQ3ZE45UVRFdz09",
  "onlineMeetingUrl": "dingtalk://...",
  "conferenceId": "xxx",
  "startTime": "2026-03-16T14:00:00+08:00",
  "endTime": "2026-03-16T15:00:00+08:00",
  "attendeeCount": 2
}
```

### 34. 取消预约会议 (cancel-schedule-conference)

```bash
python scripts/cancel_schedule_conference.py "<scheduleConferenceId>" "<创建人unionId>"
```

输出：

```json
{ "success": true, "scheduleConferenceId": "xxx", "message": "预约会议已取消" }
```

### 35. 查询日程列表 (list-events)

```bash
python scripts/list_events.py "<用户unionId>" [--time-min "2026-03-01 00:00"] [--time-max "2026-03-31 23:59"]
```

输出：

```json
{
  "success": true,
  "totalCount": 5,
  "events": [{ "id": "eventId", "summary": "周会", "start": {...}, "end": {...} }]
}
```

### 36. 查询日程详情 (get-event)

```bash
python scripts/get_event.py "<用户unionId>" "<eventId>"
```

输出：

```json
{
  "success": true,
  "event": { "id": "eventId", "summary": "周会", "attendees": [...], "onlineMeetingInfo": {...} }
}
```

### 37. 删除日程 (delete-event)

```bash
python scripts/delete_event.py "<用户unionId>" "<eventId>" [--push-notification]
```

输出：

```json
{ "success": true, "eventId": "xxx", "message": "日程已删除" }
```

### 38. 添加日程参与者 (add-event-attendee)

```bash
python scripts/add_event_attendee.py "<用户unionId>" "<eventId>" "<参与者unionId1,unionId2>"
```

输出：

```json
{ "success": true, "eventId": "xxx", "addedCount": 2, "message": "已添加 2 位参与者" }
```

### 39. 移除日程参与者 (remove-event-attendee)

```bash
python scripts/remove_event_attendee.py "<用户unionId>" "<eventId>" "<参与者unionId1,unionId2>"
```

输出：

```json
{ "success": true, "eventId": "xxx", "removedCount": 1, "message": "已移除 1 位参与者" }
```

### 40. 获取知识库列表 (list-workspaces)

获取用户能访问的所有知识库。

```bash
python scripts/list_workspaces.py "<操作人unionId>"
```

输出：

```json
{
  "success": true,
  "totalCount": 2,
  "workspaces": [
    { "workspaceId": "xxx", "name": "技术部知识库", "type": "TEAM", "url": "https://...", "rootNodeId": "yyy" }
  ]
}
```

### 41. 创建知识库文档 (create-doc)

在指定知识库中创建新文档。

```bash
python scripts/create_doc.py "<workspaceId>" "<文档名>" "<操作人unionId>" ["<docType>"]
```

docType 可选值：`alidoc`（钉钉文档，默认）、`alisheet`（表格）、`alinote`（笔记）

输出：

```json
{
  "success": true,
  "name": "周报",
  "docType": "alidoc",
  "workspaceId": "xxx",
  "nodeId": "yyy",
  "docKey": "zzz",
  "url": "https://..."
}
```

### 42. 搜索知识库文档 (search-doc)

根据文档名关键词搜索知识库文档，返回文档链接。

```bash
python scripts/search_doc.py "<操作人unionId>" "<文档名关键词>" ["<workspaceId>"]
```

不指定 workspaceId 时搜索所有知识库。

输出：

```json
{
  "success": true,
  "keyword": "周报",
  "totalCount": 3,
  "documents": [
    { "name": "3月第2周周报", "nodeId": "xxx", "url": "https://...", "category": "ALIDOC", "workspaceName": "技术部知识库" }
  ]
}
```

### 43. 覆写文档内容 (overwrite-doc)

覆写知识库文档的全部内容（全量替换，非追加）。

```bash
python scripts/overwrite_doc.py "<workspaceId>" "<nodeId>" "<操作人unionId>" "<内容>"
```

输出：

```json
{ "success": true, "workspaceId": "xxx", "nodeId": "yyy", "message": "文档内容已覆写" }
```

## 错误处理

所有脚本在错误时返回统一格式：

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  }
}
```

常见错误码：
- `MISSING_CREDENTIALS` - 未设置环境变量
- `INVALID_ARGS` - 参数不足
- `UNKNOWN_ERROR` - API 调用异常

## 重要说明

- `userId` 是企业内部用户 ID，`unionId` 是全局唯一标识
- 会议、日程、知识库相关的 API 使用 `unionId`，可通过 get-user 查询获取
- 根部门 deptId 为 1
- 知识库 `workspaceId` 通过 list-workspaces 获取，`nodeId` 通过 search-doc 获取
