# 阶段 5：plan 建立 — `phase_5_plan` / `awaiting_approval`

## 导演检查清单
- [ ] 选对模板：**全量** `plan-output.md` 或 **lite** `plan-lite.md`（标 `plan_template: lite`）
- [ ] `plan_version`、共识、风险、用户确认章节（全量 §8 / lite §6）
- [ ] `orchestrator.py set <sid> plan_version 1` → `orchestrator.py advance <sid>` → 自动进入 `awaiting_approval`
- [ ] 用户确认后 → `orchestrator.py set <sid> approved_at "..."` → `orchestrator.py advance <sid>` → `phase_6_execution`

## 参考
- `SKILL.md`「阶段 5」、`templates/plan-output.md`、`templates/plan-lite.md`
