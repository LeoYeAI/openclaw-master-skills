# APS Knowledge Base — JSON Schemas

## Table of Contents
1. [APS Rule](#1-aps-rule)
2. [Client Profile (_profile.json)](#2-client-profile)
3. [Problem Schema](#3-problem-schema)
4. [Proposal (pending_review)](#4-proposal)
5. [Decision Log Entry](#5-decision-log-entry)
6. [Rule Index (_index.json)](#6-rule-index)

---

## 1. APS Rule

File location: `domain_rules/<category>/rule_<NNN>.json`

```json
{
  "id": "rule_003",
  "type": "operator_constraint",
  "name": "高风险机器持证操作规则",
  "description": "未维护超过 Z 小时的机器，必须由持 HSE 证书的操作员监督...",
  "parameters": {
    "Z": { "label": "未维护时长阈值（小时）", "type": "number", "default": 200 },
    "A": { "label": "连续工作上限（小时）", "type": "number", "default": 0.5 },
    "B": { "label": "强制休息时长（小时）", "type": "number", "default": 0.083 }
  },
  "trigger_condition": "machine.hours_since_maintenance > Z",
  "constraint_type": "soft",
  "penalty_weight": 0.8,
  "scope": {
    "applies_to": ["stage_2", "machine_2"],
    "operators": ["Bob"],
    "industry": "manufacturing",
    "process_type": "any"
  },
  "status": "active",
  "metadata": {
    "created_at": "2026-03-18T14:32:00Z",
    "created_by": "ai_agent",
    "confirmed_by": "big_boss",
    "confirmed_at": "2026-03-18T14:35:00Z",
    "deprecated_at": null,
    "deprecation_reason": null,
    "source_session": "session_20260318",
    "source_quote": "machine 2 of stage 2 has not been serviced for a long time",
    "last_used_at": "2026-03-20T09:00:00Z",
    "use_count": 3,
    "confidence": 0.95,
    "last_verified_at": "2026-03-20T09:00:00Z",
    "expires_at": null,
    "tags": ["HSE", "maintenance", "operator_qualification"]
  }
}
```

**`type` enum**: `machine_constraint` | `operator_constraint` | `material_constraint` | `setup_time` | `due_date`

**`constraint_type` enum**: `hard` | `soft`

**`status` enum**: `proposed` | `active` | `deprecated` | `archived`

---

## 2. Client Profile

File location: `client_memory/_profile.json`

```json
{
  "profile_version": "1.2",
  "customer_name": "示例制造有限公司",
  "last_updated": "2026-03-20T10:00:00Z",
  "shop_floor": {
    "type": "flow_shop",
    "stages": 2,
    "machines_per_stage": 2,
    "topology": "parallel",
    "release_time": 0,
    "transfer_time": 0,
    "confirmed": true,
    "confirmed_by": "plant_manager",
    "confirmed_at": "2026-03-18T10:15:00Z"
  },
  "operators": {
    "active": ["Bob", "Alice", "Chen"],
    "certified_hse": ["Bob"]
  },
  "planning_process": {
    "order_source": "sales_manager_wechat",
    "has_erp": false,
    "typical_batch_size": "4-8",
    "replanning_triggers": ["rush_order", "machine_breakdown", "inventory_shortage"],
    "decision_makers": {
      "schedule_owner": "plant_manager",
      "inventory_check": "inventory_manager",
      "delivery_approval": "sales_manager"
    }
  },
  "preferences": {
    "primary_objective": "minimize_makespan",
    "secondary_objective": "maximize_on_time_delivery",
    "output_format": ["gantt_chart", "wechat_message"],
    "language": "zh-CN",
    "time_unit": "minutes"
  }
}
```

---

## 3. Problem Schema

File location: `problem_schemas/flow_shop.json`

```json
{
  "schema_version": "1.0",
  "problem_type": "flow_shop",
  "display_name": "两阶段流水车间",
  "required_fields": ["jobs", "stages"],
  "optional_fields": ["release_times", "due_dates", "soft_constraints"],
  "example": {
    "problem_type": "flow_shop",
    "objective": "minimize_makespan",
    "jobs": [
      { "id": "001", "processing_times": [10, 20] },
      { "id": "002", "processing_times": [25, 20] }
    ],
    "stages": [
      { "id": 1, "machines": 2, "parallel": true },
      { "id": 2, "machines": 2, "parallel": true }
    ],
    "hard_constraints": [
      { "type": "machine_non_preemptive" },
      { "type": "precedence", "rule": "stage_1_before_stage_2" }
    ],
    "soft_constraints": []
  }
}
```

---

## 4. Proposal (pending_review)

File location: `pending_review/proposed_<id>_<timestamp>.json`

For a new rule proposal, the schema is the full rule schema with `status: "proposed"` and `confirmed_by: null`.

For a memory update proposal:

```json
{
  "type": "client_memory_update",
  "memory_type": "shop_floor",
  "updates": {
    "stages": 3,
    "confirmed": false
  },
  "reason": "Plant manager mentioned a new pre-processing stage added this month",
  "proposed_at": "2026-03-20T11:00:00Z",
  "source_session": "session_20260320",
  "source_quote": "we added a pre-treatment stage last month"
}
```

---

## 5. Decision Log Entry

File location: `client_memory/decision_history/session_<YYYYMMDD>.json`

```json
{
  "session_id": "session_20260320",
  "timestamp": "2026-03-20T09:15:00Z",
  "problem_type": "flow_shop",
  "solver_used": "cp_sat",
  "makespan_minutes": 55,
  "jobs_scheduled": ["001", "002", "003", "004"],
  "decision_summary": {
    "stage1_machine1": ["001", "003"],
    "stage1_machine2": ["002", "004"],
    "stage2_machine1": ["001", "003"],
    "stage2_machine2": ["002", "004"]
  },
  "triggered_by_rules": ["rule_003"],
  "rule_params_used": {
    "rule_003": { "Z": 200, "A": 0.5, "B": 0.083 }
  },
  "soft_constraints_violated": [],
  "human_confirmed": true,
  "confirmed_by": "plant_manager"
}
```

---

## 6. Rule Index

File location: `domain_rules/_index.json`

A flat list of all rules with lightweight metadata for fast scanning without
loading every individual file:

```json
{
  "last_rebuilt": "2026-03-20T10:00:00Z",
  "total_active": 3,
  "rules": [
    {
      "id": "rule_001",
      "name": "机器A3换模时间规则",
      "type": "setup_time",
      "status": "active",
      "file_path": "domain_rules/machine_rules/rule_001.json",
      "tags": ["setup", "mold_change"],
      "use_count": 12
    },
    {
      "id": "rule_003",
      "name": "高风险机器持证操作规则",
      "type": "operator_constraint",
      "status": "active",
      "file_path": "domain_rules/operator_rules/rule_003.json",
      "tags": ["HSE", "maintenance"],
      "use_count": 3
    }
  ]
}
```
