# 轻量 plan 模板（`plan_template: lite`）

用于**单一交付物**、**执行清单项 ≤2** 的工作坊；信息量少于 `plan-output.md` 全量模板时选用。

**使用规则**（见 `SKILL.md`「plan 模板选择」）：须在 `plan.md` 首行或紧接标题下写 **`plan_template: lite`**，并在 **§风险** 写明「未使用全量 plan 模板，差异：…」。

---

**plan_version**: 1  
**plan_template**: lite

## 1. 一句话目标

（须与 `state.md` **阶段 0** 的 **期望交付物类型** 一致；若不一致，说明原因或已递增 `plan_version`）

## 2. 背景与约束（条目即可）

- 用户/读者：
- 不在范围内：

## 3. 共识（小表或列表）

| 议题 | 共识 | 未决 |
|------|------|------|

## 4. 交付物与验收

| 交付物 | 路径 | 验收标准 |
|--------|------|----------|
| | `deliverables/...` | |

## 5. 风险

| 风险 | 应对 |
|------|------|

## 6. 用户确认

- [ ] 用户已确认，可执行  
- 时间：

## 7. 机器执行脚本（可选）

若需由 `workshops/scripts/generate_execution.py` 根据本 plan **生成** `scripts/run_openrouter_images.py`，任选一种写法（可并存，**execution_prompts_file 优先**）：

```
execution_preset: dragon-head-images
```

或指向本会话下的提示词 Markdown（内为英文「可执行提示词」代码块）：

```
execution_prompts_file: deliverables/ai-image-prompts-xxx.md
```

若本节留空，生成器会尝试自动使用 `deliverables/*prompt*.md` 中解析到的提示词。生成命令：

`python3 workshops/scripts/generate_execution.py --workshop workshops/<session_id> --from-plan`
