# 工作流模板参考

## 模板1: 表单数据自动处理

```yaml
workflow:
  name: 表单数据自动处理
  trigger:
    type: webhook
    endpoint: /webhook/form-submission
  inputs:
    - name: form_data
      type: object
      source: form_submission
  steps:
    - id: validate
      action: fetch
      config:
        # 验证数据格式
      on_success: deduplicate
      on_failure: notify_error
    - id: deduplicate
      action: transform
      config:
        # 基于email/phone去重
      on_success: enrich
    - id: enrich
      action: fetch
      config:
        # 补充企业/个人信息
      on_success: score
    - id: score
      action: decide
      config:
        rules:
          - condition: "score >= 80"
            goto: alert_high_priority
          - condition: "score >= 40"
            goto: add_nurture_sequence
          - condition: "default"
            goto: auto_reply
    - id: alert_high_priority
      action: send
      config:
        channel: slack
        message: "新高质量线索"
    - id: add_nurture_sequence
      action: send
      config:
        # 加入邮件培育序列
    - id: auto_reply
      action: send
      config:
        # 发送资料包
    - id: log_to_crm
      action: store
      config:
        destination: crm_leads.json
```

## 模板2: 定时数据报表

```yaml
workflow:
  name: 每日销售报表
  trigger:
    type: schedule
    cron: "0 8 * * 1-5"  # 工作日早8点
  inputs:
    - name: sales_data
      source: sales_api
    - name: crm_data
      source: crm_api
  steps:
    - id: fetch_sales
      action: fetch
      source: sales_api
    - id: fetch_crm
      action: fetch
      source: crm_api
    - id: calculate_kpis
      action: transform
      config:
        metrics:
          - revenue
          - deals_closed
          - conversion_rate
          - avg_deal_size
    - id: detect_anomalies
      action: decide
      rules:
        - condition: "revenue_change > 20%"
          goto: anomaly_alert
        - condition: "default"
          goto: generate_report
    - id: anomaly_alert
      action: notify
      config:
        channel: ops_slack
    - id: generate_report
      action: transform
      output: reports/daily_YYYY-MM-DD.md
    - id: distribute
      action: send
      config:
        - exec_summary: leadership_slack
        - full_report: stakeholder_email
```

## 模板3: 社交内容批量发布

```yaml
workflow:
  name: 社交内容批量发布
  trigger:
    type: schedule
    cron: "0 9,12,17 * * *"  # 每天9点、12点、17点
  steps:
    - id: fetch_queue
      action: fetch
      source: content_queue.json
    - id: format_per_platform
      action: transform
      config:
        platforms:
          - twitter: max_280_chars
          - linkedin: professional_tone
          - instagram: visual_focus
    - id: post_parallel
      type: parallel
      branches:
        - steps: [post_twitter]
        - steps: [post_linkedin]
        - steps: [post_instagram]
    - id: log_results
      action: store
      destination: logs/publish_YYYY-MM-DD.json
```
