# DingTalk Skills (ding-skills)

钉钉全功能技能集，涵盖用户管理、部门管理、消息发送、OA审批、视频会议与日程管理。

## 环境准备

```bash
pip install -r requirements.txt

export DINGTALK_APP_KEY="your-app-key"
export DINGTALK_APP_SECRET="your-app-secret"
```

---

## 一、用户管理

### 1. 搜索用户 (search-user)
```bash
python scripts/search_user.py "<搜索关键词>"
```

### 2. 查询用户详情 (get-user)
```bash
python scripts/get_user.py "<userId>"
```

### 3. 根据手机号查询用户 (get-user-by-mobile)
```bash
python scripts/get_user_by_mobile.py "<手机号>"
```

### 4. 根据 unionid 查询用户 (get-user-by-unionid)
```bash
python scripts/get_user_by_unionid.py "<unionid>"
```

### 5. 获取员工人数 (get-user-count)
```bash
python scripts/get_user_count.py [--onlyActive]
```

### 6. 获取用户待审批数量 (get-user-todo-count)
```bash
python scripts/get_user_todo_count.py "<userId>"
```

### 7. 获取未登录用户列表 (list-inactive-users)
```bash
python scripts/list_inactive_users.py "<queryDate>" [--deptIds "id1,id2"] [--offset 0] [--size 100]
```
queryDate 格式: yyyyMMdd

### 8. 查询离职记录 (list-resigned-users)
```bash
python scripts/list_resigned_users.py "<startTime>" ["<endTime>"] [--nextToken "xxx"] [--maxResults 100]
```
时间格式: ISO8601

---

## 二、部门管理

### 9. 搜索部门 (search-department)
```bash
python scripts/search_department.py "<搜索关键词>"
```

### 10. 获取部门详情 (get-department)
```bash
python scripts/get_department.py "<deptId>"
```

### 11. 获取子部门列表 (list-sub-departments)
```bash
python scripts/list_sub_departments.py "<deptId>"
```
根部门 deptId = 1

### 12. 获取部门用户列表 (list-department-users)
```bash
python scripts/list_department_users.py "<deptId>"
```
自动分页获取所有用户（简略信息）

### 13. 获取部门用户详情 (list-department-user-details)
```bash
python scripts/list_department_user_details.py "<deptId>" [--cursor 0] [--size 100]
```

### 14. 获取部门用户 ID 列表 (list-department-user-ids)
```bash
python scripts/list_department_user_ids.py "<deptId>"
```

### 15. 获取部门父部门链 (list-department-parents)
```bash
python scripts/list_department_parents.py "<deptId>"
```

### 16. 获取用户所属部门父部门链 (list-user-parent-departments)
```bash
python scripts/list_user_parent_departments.py "<userId>"
```

---

## 三、消息与机器人

### 17. 获取群内机器人列表 (get-bot-list)
```bash
python scripts/get_bot_list.py "<openConversationId>"
```

### 18. 机器人发送群消息 (send-group-message)
```bash
python scripts/send_group_message.py "<openConversationId>" "<robotCode>" "<消息内容>"
```

### 19. 机器人发送单聊消息 (send-user-message)
```bash
python scripts/send_user_message.py "<userId>" "<robotCode>" "<消息内容>"
```

---

## 四、OA 审批

### 20. 获取审批实例 ID 列表 (list-approval-instance-ids)
```bash
python scripts/list_approval_instance_ids.py "<processCode>" --startTime <timestamp> --endTime <timestamp> [--size 20] [--nextToken "xxx"]
```

### 21. 获取审批实例详情 (get-approval-instance)
```bash
python scripts/get_approval_instance.py "<instanceId>"
```

### 22. 查询用户发起的审批 (list-user-initiated-approvals)
```bash
python scripts/list_user_initiated_approvals.py "<userId>" [--startTime <ts>] [--endTime <ts>] [--maxResults 20]
```

### 23. 查询用户抄送的审批 (list-user-cc-approvals)
```bash
python scripts/list_user_cc_approvals.py "<userId>" [--startTime <ts>] [--endTime <ts>] [--maxResults 20]
```

### 24. 查询用户待审批实例 (list-user-todo-approvals)
```bash
python scripts/list_user_todo_approvals.py "<userId>" [--maxResults 20]
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

### 27. 撤销审批实例 (terminate-approval-instance)
```bash
python scripts/terminate_approval_instance.py "<instanceId>" "<operatingUserId>" ["<remark>"]
```

### 28. 执行审批任务 (execute-approval-task)
```bash
python scripts/execute_approval_task.py "<instanceId>" "<userId>" "<agree|refuse>" [--taskId "xxx"] [--remark "审批意见"]
```

### 29. 转交审批任务 (transfer-approval-task)
```bash
python scripts/transfer_approval_task.py "<instanceId>" "<userId>" "<transferToUserId>" [--taskId "xxx"] [--remark "转交原因"]
```

### 30. 添加审批评论 (add-approval-comment)
```bash
python scripts/add_approval_comment.py "<instanceId>" "<commentUserId>" "<评论内容>"
```

---

## 五、视频会议

### 31. 创建即时视频会议 (create-video-conference)
```bash
python scripts/create_video_conference.py "<会议主题>" "<发起人unionId>" "[邀请人unionId1,unionId2]"
```

### 32. 关闭视频会议 (close-video-conference)
```bash
python scripts/close_video_conference.py "<conferenceId>" "<操作人unionId>"
```

---

## 六、预约会议与日程管理

### 33. 创建预约会议 (create-schedule-conference)
```bash
python scripts/create_schedule_conference.py "<会议主题>" "<创建人unionId>" "<开始时间>" "<结束时间>" "[参会人unionId1,unionId2]"
```
时间格式: `"2026-03-16 14:00"`

### 34. 取消预约会议 (cancel-schedule-conference)
```bash
python scripts/cancel_schedule_conference.py "<scheduleConferenceId>" "<创建人unionId>"
```

### 35. 查询日程列表 (list-events)
```bash
python scripts/list_events.py "<用户unionId>" [--time-min "2026-03-01 00:00"] [--time-max "2026-03-31 23:59"]
```

### 36. 查询日程详情 (get-event)
```bash
python scripts/get_event.py "<用户unionId>" "<eventId>"
```

### 37. 删除日程 (delete-event)
```bash
python scripts/delete_event.py "<用户unionId>" "<eventId>" [--push-notification]
```

### 38. 添加日程参与者 (add-event-attendee)
```bash
python scripts/add_event_attendee.py "<用户unionId>" "<eventId>" "<参与者unionId1,unionId2>"
```

### 39. 移除日程参与者 (remove-event-attendee)
```bash
python scripts/remove_event_attendee.py "<用户unionId>" "<eventId>" "<参与者unionId1,unionId2>"
```

---

## 参数说明

| 参数 | 说明 |
|------|------|
| `userId` | 钉钉企业内用户 ID |
| `unionId` | 钉钉用户全局唯一标识符 |
| `deptId` | 部门 ID，根部门为 1 |
| `processCode` | 审批模板编码 |
| `instanceId` | 审批实例 ID |
| `conferenceId` | 视频会议 ID |
| `eventId` | 日历日程 ID |
| `openConversationId` | 群会话开放 ID |
| `robotCode` | 机器人编码 |

## 技术栈

- Python 3 + requests
- 直接调用钉钉 REST API（无 SDK 依赖）
- 共享客户端模块：`scripts/dingtalk_client.py`
