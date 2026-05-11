# Anima-AIOS 架构原则

**版本：** v6.0.0
**更新日期：** 2026-03-24
**制定者：** 立文、清禾

---

## 🎯 核心设计哲学

### 铁律

**架构只能演进，不能退化。** —— 立文

每次版本迭代前必须对照原始架构检查：五层在不在、宫殿在不在、金字塔在不在、衰减在不在。少了任何一个，不许发版。

---

## 🏗️ 架构总览

### 单一代码目录

v6 起统一为 `anima-aios/` 单一目录，不再区分 core/skill 双层。

```
anima-aios/
├── core/           # 所有核心模块（业务逻辑 + 数据处理）
├── health/         # 健康系统
├── anima_tools.py  # 对外工具接口（Skill 层）
├── anima_doctor.py # Doctor 诊断入口
├── tests/          # 测试
├── scripts/        # 运维脚本
├── config/         # 配置
└── docs/           # 文档
```

### 五层记忆模型

```
L1 工作记忆   ← OpenClaw 原生 memory/（自动监听）
L2 情景记忆   ← facts/episodic/（LLM 质量评估）
L3 语义记忆   ← facts/semantic/（LLM 去重提炼）
L4 知识宫殿   ← palace/ + pyramid/（LLM 分类 + 金字塔提炼）
L5 元认知层   ← 画像 + EXP + 衰减 + 健康
```

---

## 📐 设计原则

### 1. 零侵入原则
- 不修改 OpenClaw 源码
- 通过 watchdog 文件监听与 OpenClaw 打通
- Agent 日常工作完全无感知

### 2. LLM 优先，规则兜底
- 质量评估、去重、分类优先调用 LLM
- LLM 不可用时自动降级为关键词/规则匹配
- 不因 LLM 故障导致系统不可用

### 3. 路径不硬编码
- 所有路径通过 config 或环境变量配置
- 默认值兼容现有数据（/home/画像）
- 支持 ANIMA_FACTS_BASE、ANIMA_AGENT_NAME 等环境变量

### 4. 向后兼容
- v5 的 EXP / facts / 画像数据零修改
- v6 新增目录（palace/ pyramid/ health/ decay/）不影响 v5 数据
- 每个 v6 模块可通过 config 单独禁用

### 5. 保守模式优先
- 自动提炼（auto_distill）默认关闭
- 宫殿分类采用延迟防抖，不实时分类
- 新功能先观察再放开

---

## 🔒 发版检查清单

发版前必须全部通过：

- [ ] L1 — OpenClaw memory_write 自动触发 Anima 同步
- [ ] L2 — facts/episodic/ 自动归档
- [ ] L3 — 提炼引擎能从 L2 提取知识
- [ ] L4 宫殿 — palace_index 创建/检索正常
- [ ] L4 金字塔 — 四层可写可查
- [ ] L5 衰减 — 衰减计算正确
- [ ] L5 健康 — 5 个模块全部运行
- [ ] LLM 处理 — 质量评估/去重/分类正常
- [ ] 宫殿分类调度 — 延迟防抖正常
- [ ] v5 兼容 — EXP/画像/任务/排行正常
- [ ] 回滚可用 — 禁用 v6 模块后 v5 不受影响
- [ ] SKILL.md — 只写已实现功能
- [ ] 集成测试 — 全部通过

---

_先诚实，再迭代。代码要配得上宣传。—— 清禾_
