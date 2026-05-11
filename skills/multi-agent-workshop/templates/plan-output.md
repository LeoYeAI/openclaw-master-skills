# 可执行方案模板（复制到 `workshops/<session_id>/plan.md` 并填全）

**版本**：`plan_version: 1`（大改 scope 时递增；在 §8 或文末简短记 `CHANGELOG`：日期 + 一句变更）  
**单一交付物且清单很短？** 可选用 `plan-lite.md`（须标 `plan_template: lite`），见 `SKILL.md`「plan 模板选择」。

## 1. 一句话目标

（可验收的一句话；须与 `state.md` **阶段 0** 的 **期望交付物类型** 一致；若改口径须递增 `plan_version` 并披露）

## 2. 背景与约束

- 用户/客户：
- 截止时间 / 硬约束：
- 不在范围内（明确不写）：

## 3. 共识与分歧处理

| 议题 | 共识 | 未决项（若无可写「无」） |
|------|------|--------------------------|
| | | |

## 4. 主指标与验收

| 指标 | 目标值 | 衡量方式 / 时间 |
|------|--------|-----------------|
| | | |

## 5. 里程碑

| 阶段 | 交付物 | 目标日期 |
|------|--------|----------|
| | | |

## 6. 执行清单（可勾选）

| 序号 | 任务 | Owner（角色） | 依赖 | 验收标准 | 状态 |
|------|------|---------------|------|----------|------|
| 1 | | 运营/产品/技术 | | | ☐ |

## 7. 风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| | | | |

## 8. 用户确认

- [ ] 用户已确认本方案，可进入执行阶段  
- 确认时间：（导演填写或让用户补充）

## 9. 机器执行脚本（可选）

若需由 `workshops/scripts/generate_execution.py` 根据 plan **生成** workshop 内可运行脚本，在下方填写（**execution_prompts_file 优先于 execution_preset**）：

```
execution_preset: dragon-head-images
execution_prompts_file: deliverables/你的提示词.md
```

留空时，对 `--from-plan` 会尝试自动读取 `deliverables/*prompt*.md`。详见 `workshops/scripts/README.md`。
