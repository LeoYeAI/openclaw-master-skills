---
platform_id: "{{platform_id}}"
platform_name: "{{platform_name}}"
auth_methods:
  - type: "{{auth_type}}"
    priority: 1
    label: "{{auth_label}}"
capabilities:
  - {{capability_1}}
  - {{capability_2}}
session_check:
  method: "{{check_method}}"
  endpoint: "{{check_endpoint}}"
  success_indicator: "{{success_indicator}}"
estimated_session_duration_days: {{session_days}}
auto_refresh_supported: {{auto_refresh}}
---

## 认证流程

### {{auth_type_name}}

{{auth_steps}}

## 登录态验证

{{validation_method}}

判定逻辑：
- {{success_condition}} → `healthy`
- {{failure_condition}} → `expired`
- 网络错误 → `unknown`

## 操作指令

### {{capability_1}}

{{capability_1_instructions}}

### {{capability_2}}

{{capability_2_instructions}}

## 频率控制

| 操作 | 建议频率 | 说明 |
|------|----------|------|
| {{operation}} | {{rate}} | {{reason}} |

## 已知问题

1. {{known_issue_1}}
