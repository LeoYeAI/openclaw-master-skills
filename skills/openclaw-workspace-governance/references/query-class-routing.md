# Reference Draft — Query-Class Routing

Status: draft-for-skill
Role: stable routing reference

## Purpose

Define how a complex OpenClaw workspace should answer different classes of questions without using one blunt retrieval policy for everything.

This reference assumes:
- source-of-truth layers already exist
- current-state and historical layers are separated
- semantic search is useful but not uniformly trustworthy across all question classes

---

## Core Principle

Do not ask:
- “What is the best retrieval source overall?”

Ask instead:
- “What kind of question is this?”
- “Which layer should answer it first?”
- “What role should semantic search play for this class?”

Routing should follow **query class first**, not tool preference first.

---

## Main Query Classes

### 1. System-state
Examples:
- 当前整体状态
- 系统状态
- health / consistency / retrieval reliability
- current maintenance posture

Primary answer path:
1. health/consistency layer
2. bridge/current-state layer
3. runtime snapshot if runtime-specific detail is needed
4. structured memory later

Semantic search role:
- supporting recall only
- may become stronger supporting recall if validated for this class
- should not replace bridge/health as primary authority

---

### 2. Governance / rule-boundary
Examples:
- 谁负责什么
- 哪些改动需要审核
- 是否需要用户审批
- 哪个文件算正式规则

Primary answer path:
1. canon/governance docs
2. source-of-truth rules
3. supporting historical context if needed

Semantic search role:
- background only
- never primary

---

### 3. Runtime-now
Examples:
- 当前主会话模型是什么
- 现在 runtime 是怎么跑的
- 当前 specialist/agent arrangement 是什么

Primary answer path:
1. runtime snapshot
2. bridge/current-state layer
3. canon for boundary questions only

Semantic search role:
- discovery/supporting only

---

### 4. Weekly-review / approval-state
Examples:
- weekly review status
- review state
- 审批状态
- approved / rejected / pending

Primary answer path:
1. current review-state file / bridge file
2. supporting review history if needed

Semantic search role:
- supporting recall only
- may be stronger supporting recall if validated for this class
- still should not outrank the current review-state source

---

### 5. User-preference / profile
Examples:
- 用户偏好
- style preference
- automation preference
- profile constraints

Primary answer path:
1. curated profile/manual sources
2. durable long-term memory if appropriate
3. structured memory only as support

Semantic search role:
- secondary only
- use for additional evidence, not for main authority
- be cautious because chat logs and noisier historical material may outrank cleaner profile sources

---

### 6. Historical trace / evidence
Examples:
- 上次怎么修的
- 哪天引入了某规则
- exact evidence trail
- historical change sequence

Primary answer path:
1. evidence discovery
2. direct file verification

Semantic search role:
- useful discovery layer
- often helpful for locating candidate files
- never enough by itself for definitive historical claims without verification

---

### 7. Maintenance / upkeep
Examples:
- 现在先维护什么
- 哪些文件要刷
- 哪些文档还活着
- 哪些已经历史化

Primary answer path:
1. working set
2. refresh checklist
3. current health/consistency and bridge docs
4. index/inventory docs if broader classification is needed

Semantic search role:
- usually unnecessary for ordinary maintenance questions
- use only if the maintained set itself is unclear

---

## Semantic Search Roles by Class

### Stronger supporting recall
Possible for:
- system-state
- weekly-review / review-state

Condition:
- runtime/cache alignment is known good
- validation has shown acceptable results for the class

### Secondary / conservative only
Keep for:
- user-preference / profile
- governance / rule-boundary

### Discovery-oriented
Keep for:
- historical trace / evidence
- some runtime exploration tasks

---

## Routing Mistakes to Avoid

Do not:
- use semantic search as a blanket primary answer source
- use governance canon for system-state questions when a fresher bridge exists
- let old topic cards outrank fresh bridge/state docs on current-state questions
- let chat logs outrank curated profile sources on preference questions
- answer historical questions from summaries without evidence verification

---

## Practical Rule

When in doubt:
1. classify the query first
2. choose the primary layer second
3. only then decide whether semantic search should help

Not the other way around.

---

## v1 Boundary

This reference defines routing logic and semantic-search role boundaries.

It does not guarantee every semantic backend will behave identically.
That is why validation and backend-specific diagnostics still matter.
