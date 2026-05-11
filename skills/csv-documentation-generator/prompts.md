# CSV Documentation Generator - Prompt Library

本文件包含 AI Agent 生成 GxP 验证文档时使用的 Prompt 模板和思维约束。

---

## 1. GAMP 5 Second Edition - Critical Thinking Constraints

> **GAMP 5 M12 Critical Thinking**: AI agents MUST apply critical thinking principles per GAMP 5 Second Edition Appendix M12. Do NOT use rigid templates or "tick-in-the-box" approaches. Scale validation effort proportionally to system risk and complexity.

### M12.1 Validation Planning Constraints

When generating VP documents, AI agents MUST:

1. **Conduct Business Process Analysis**
   - Identify the business process the system supports
   - Create or reference business process flow diagrams
   - Understand data flow to identify GxP-regulated data

2. **Identify GxP Scope**
   - Determine which data are GxP records requiring audit trails
   - NOT all data requires audit trails - apply context-based judgment
   - Consider data that directly impacts patient safety or product quality

3. **Avoid One-Size-Fits-All Approaches**
   - Higher risk systems require more rigorous validation
   - Lower risk systems can use simplified approaches
   - Justify the chosen validation approach

### M12.2 Requirements Development Constraints

When generating URS documents, AI agents MUST:

1. **Apply Context-Based Audit Trail Requirements**
   ```
   WRONG: "All data modifications require audit trails"
   RIGHT: "GxP-regulated records require audit trails. 
           Non-GxP data (e.g., user preferences) do not require audit trails."
   ```

2. **Identify Primary Records**
   - Identify which records are the "authoritative copy" (primary record)
   - Data may flow through multiple systems - identify where compliance is maintained

3. **Use Risk-Based Prioritization**
   - Critical requirements (patient safety, data integrity) are [必须]
   - Less critical requirements are [应该] or [可以]
   - Higher risk requirements require more rigorous testing

### M12.3 Risk Assessment Constraints (Hierarchical Risk)

When generating RA documents, AI agents MUST:

1. **Apply Hierarchical Risk Structure**
   ```
   Parent Function Risk (Major) → determines testing rigor
           ↓
   Subsidiary Functions (Children) → risk cannot exceed parent
   ```

2. **Follow Risk Recursion Rules**
   - A subsidiary function CANNOT have higher risk than its parent
   - If a subsidiary appears high-risk, reconsider the parent assessment
   - Rationale: If overall function is acceptable risk, subsidiary issues may be acceptable

3. **Avoid Over-Testing Low-Risk Functions**
   - Low-risk parent function → subsidiary functions don't need detailed assessment
   - High-risk parent function → more granular assessment justified
   - Use risk recursion to scale effort appropriately

### M12.4 Testing Constraints

When generating test cases, AI agents MUST:

1. **Differentiate Proving vs Non-Proving Steps**
   - Proving steps: Demonstrate requirement fulfillment (evidence needed)
   - Non-proving steps: Setup activities (no evidence needed)

2. **Scale Evidence to Risk**
   - High-risk functions: Detailed evidence, screenshots
   - Low-risk functions: Summary evidence acceptable
   - Avoid excessive documentation for low-risk items

### M12.5 Supplier Assessment Constraints

When generating supplier assessment content:

1. **Leverage Supplier Documentation**
   - Use supplier audits, SOC 2 reports, ISO certifications
   - Avoid duplicating supplier testing efforts

2. **Assess Based on System Category**
   - Category 3/4: Leverage supplier validation
   - Category 5: Full in-house validation required

### Constraint Violation Examples

| WRONG Approach | GAMP 5 M12 Correct Approach |
|---------------|---------------------------|
| "Enable audit trail for all data" | "Enable audit trail for GxP records only" |
| "Test all functions equally" | "Scale testing rigor to risk level" |
| "Detailed testing for all subsidiaries" | "Subsidiary risk ≤ parent risk" |
| "Maximum documentation for all systems" | "Proportionate to system complexity/risk" |

---

## 2. Document Generation Triggering Conditions

### VP (Validation Plan)

**Trigger Keywords:**
- "验证计划", "validation plan", "VP"
- "项目启动", "project start"
- "系统上线", "system launch"

**Pre-fill Data (from context or user):**
- `{PROJECT_NAME}`, `{SYSTEM_NAME}`
- `{GAMP_CATEGORY}` - If not specified, prompt user with GAMP category selection
- `{CHANGE_DESCRIPTION}` - If change project, auto-fill from change request

**填充规则:**
1. 如果是**变更项目**：自动生成变更说明章节，从`{CHANGE_DESCRIPTION}`提取关键风险
2. 如果是**新项目**：生成完整规划章节
3. 基于`{GAMP_CATEGORY}`自动调整验证生命周期范围

### URS (User Requirements Specification)

**Trigger Keywords:**
- "用户需求", "URS", "user requirements"
- "需求规格", "requirements specification"

**Pre-fill Data:**
- `{SYSTEM_NAME}`, `{SYSTEM_VERSION}`
- `{GAMP_CATEGORY}`
- Business process description (from user or discovery)
- GxP records identification (from VP business process analysis)

**填充规则:**
1. 首先询问系统的业务背景和数据流
2. 识别GxP记录范围（与用户确认）
3. 基于GxP范围自动确定审计追踪需求
4. 按结构填充需求，每个需求追溯到FS

### FS (Functional Specification)

**Trigger Keywords:**
- "功能规格", "FS", "functional specification"
- "设计规格", "design specification"

**Pre-fill Data:**
- URS requirements (auto-linked by ID)
- System architecture (from TS or user description)
- GxP scope (from URS)

**填充规则:**
1. 自动从URS追溯到FS需求ID
2. 每个FS功能必须追溯到至少一个URS-ID
3. 区分配置项(COTS)和定制项

### RA (Risk Assessment)

**Trigger Keywords:**
- "风险评估", "RA", "risk assessment"
- "风险分析", "risk analysis"

**Pre-fill Data:**
- `{CHANGE_DESCRIPTION}` - If change project
- URS requirements (for risk identification)
- GxP scope (from URS)

**填充规则:**
1. 如果有`{CHANGE_DESCRIPTION}`，自动生成变更风险评估
2. 追溯URS优先级到RA风险等级
3. 应用层级风险规则：子功能风险≤父功能风险

### IQ/OQ/PQ (Qualification Protocols)

**Trigger Keywords:**
- "安装确认", "IQ", "installation qualification"
- "操作确认", "OQ", "operational qualification"
- "性能确认", "PQ", "performance qualification"

**Pre-fill Data:**
- System configuration (from TS)
- Risk assessment results (from RA)

**填充规则:**
1. 根据RA中的风险等级调整测试范围
2. 高风险功能→完整IQ/OQ/PQ
3. 低风险功能→简化测试

### VSR (Validation Summary Report)

**Trigger Keywords:**
- "验证总结", "VSR", "validation summary"
- "验证报告", "validation report"

**Pre-fill Data:**
- All test results (from IQ/OQ/PQ)
- Requirements traceability (from RTM)
- Deviation records (from testing)

**填充规则:**
1. 自动汇总所有测试结果
2. 自动生成Lessons Learned章节
3. 自动生成Periodic Review计划

---

## 3. Content Fill Prompt Library

### URS需求填充Prompt

When generating URS, AI SHOULD follow this structure:

```
1. 首先了解业务背景:
   - 询问系统的业务类型和用途
   - 识别系统的用户群体
   - 了解数据的生命周期

2. 识别GxP记录范围:
   - 哪些数据影响患者安全?
   - 哪些数据需要审计追踪?
   - 主记录(Primary Record)是什么?

3. 填充需求格式:
   | ID | 需求描述 | 优先级 | 验证方法 |
   |----|---------|--------|---------|
   | URS-{SEQ} | 系统应[功能]+[对象]+[条件] | [{必须}/{应该}/{可以}] | [{测试}/{审查}] |

4. 需求描述规则:
   - 正确: "系统应在用户登录失败5次后锁定账户30分钟"
   - 错误: "系统应该安全"
```

### FS功能填充Prompt

When generating FS, AI SHOULD follow this structure:

```
1. 追溯到URS:
   - 每个FS功能必须引用对应的URS-ID
   - 使用追溯表总览

2. 功能描述格式:
   - 描述系统如何实现URS需求
   - 包含用户界面、业务流程、边界条件

3. 配置项vs定制项:
   - COTS标准配置: 标记为"配置"
   - 需要二次开发: 标记为"定制"
```

### RA风险填充Prompt

When generating RA, AI SHOULD follow this structure:

```
1. 层级风险评估:
   - 首先评估主要功能(Major/Parent)的风险
   - 子功能(Subsidiary)风险不得高于父功能

2. RPN计算:
   RPN = 严重性(S) × 可能性(L) × 可检测性(D)
   
   | RPN范围 | 风险等级 | 行动 |
   |---------|---------|------|
   | 1-25 | 低 | 接受 |
   | 26-50 | 中 | 缓解措施 |
   | 51-75 | 高 | 必须缓解 |
   | 76-125 | 严重 | 暂停上线 |

3. 追溯到URS优先级:
   - URS [必须] + 安全/合规 → 高风险
   - URS [应该] → 中风险
   - URS [可以] → 低风险
```

---

## 4. Data Flow Definitions (Procedural)

### Document Interdependencies (Procedural)

```
┌─────────────────────────────────────────────────────────────────┐
│                        数据流动链                                 │
└─────────────────────────────────────────────────────────────────┘

[用户/AI 填写 VP 变更描述]
        │
        ▼
[RA 自动生成变更风险评估]
        │
        ▼ (追溯)
[FS 基于URS风险调整测试范围]
        │
        ▼
[IQ/OQ/PQ 测试范围自动调整]
        │
        ▼
[VSR 自动汇总变更影响]
```

### Specific Data Mappings

| 源文档 | 数据项 | 目标文档 | 填充位置 |
|--------|--------|----------|----------|
| VP | `{CHANGE_DESCRIPTION}` | RA | 1.5 变更说明 |
| URS | GxP记录识别 | FS | 审计追踪需求 |
| URS | 需求优先级 | RA | 风险等级基准 |
| FS | URS追溯表 | RTM | 追溯矩阵 |
| RA | 风险等级 | IQ/OQ/PQ | 测试范围 |
| IQ/OQ/PQ | 测试结果 | VSR | 4.验证结果汇总 |

### Automatic Traceability建立规则

1. **URS → FS**: AI在填充FS时必须引用URS-ID
2. **FS → TS**: 技术规格支持功能规格
3. **URS → RA**: 风险等级基于URS优先级
4. **RA → Test**: 测试范围基于风险等级
5. **All → RTM**: 追溯矩阵自动汇总

---

## 5. Bilingual Output Prompts

### 智能双语模式 (Smart Bilingual)

此 skill 支持智能双语输出，根据 `--bilingual` 和 `--language` 参数生成不同语言版本：

| 参数组合 | 行为 |
|---------|------|
| `--bilingual true --language zh` | Headers 保持双语 (`目的 / Purpose`)，内容填充中文 |
| `--bilingual true --language en` | Headers 保持双语 (`目的 / Purpose`)，内容填充英文 |
| `--bilingual false --language zh` | 纯中文输出 |
| `--bilingual false --language en` | 纯英文输出 |

### 模板双语格式

模板使用以下格式来表示双语内容：

```markdown
| 中文 / English | 描述 / Description |
|----------------|-------------------|
| 用户管理 / User Management | 用户 / User |
```

**处理规则：**
- Header 行：保持双语格式
- Content 行：根据 `--language` 选择一种语言

### 双语表格Header

```markdown
| 中文 | English |
|------|---------|
| 验证计划 | Validation Plan |
| 用户需求 | User Requirements |
```

### 双语章节

```markdown
## 1. 目的 / Purpose

本文档定义了... / This document defines...
```

### 内容填充语言选择

当 AI agent 填充模板内容时，应根据 `--language` 参数选择语言：

- `--language zh`：所有 AI 填充内容使用中文
- `--language en`：所有 AI 填充内容使用英文

这允许：
1. 同一项目可生成不同语言版本用于不同受众
2. 保留标题双语便于对照理解
3. AI 可根据用户上下文自动选择语言
