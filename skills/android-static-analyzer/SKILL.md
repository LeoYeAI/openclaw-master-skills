---
name: android-static-analyzer
description: 分析 Android 项目源码，用 LLM 从多维度生成 AI 自动化测试所需的先验知识文档，打包上报测试平台。核心价值：让 AI 测试 Agent 在运行前就知道「测什么、怎么断言、有哪些陷阱」。触发词：「分析我的 Android 项目」「生成测试画像」「理解这个 App 的业务」「提取测试先验知识」「帮我分析 Android 源码」
---

# Android Static Analyzer — AI 测试先验知识生成器

## 核心定位

AI 自动化测试要能"智能地"测试 App，需要知道以下 5 件事：
1. **测什么**（业务目标和范围）
2. **怎么走**（操作路径和前置状态）
3. **预期什么**（每一步操作后应该发生什么）
4. **如何断言**（怎么判断测试通过/失败）
5. **有哪些陷阱**（死路/外部依赖/不可逆操作）

本 Skill 从源码中提取上述所有信息，生成 **9 份文档**，打包成 static-profile。

**与 AITestSDK 分工**：
- AITestSDK（运行期）→ 控件树、NavEdge、Activity 清单、实时 UI 状态
- 本 Skill（编码期）→ 业务语义、断言依据、状态依赖、测试策略

**绝不重复** AITestSDK 已有的结构数据（Activity 数量、控件 ID 枚举等）。

---

## 执行步骤

### Step 1：获取项目路径

询问用户项目路径。也接受：APK、GitHub 链接、直接粘贴的代码。

### Step 2：读取核心源码

```bash
# 定位项目
find <path> -name "AndroidManifest.xml" -not -path "*/build/*" | head -3
find <path> -name "*Activity*.kt" -not -path "*/build/*"
find <path> -name "README*" -maxdepth 3 -not -path "*/build/*"
find <path> -name "build.gradle.kts" -not -path "*/build/*" | head -2
```

按优先级 `read` 每个文件前 300 行（优先读 Activity 源文件）。

**读取时重点关注：**
- `startActivity()` / `navigate()` → 页面跳转
- `Toast.makeText()` 的文本 → 操作反馈（成功/失败提示）
- `if/else + return` → 约束条件和阻断逻辑
- `isEnabled` / `isVisible` / `visibility = View.GONE/VISIBLE` → UI 状态变化
- 硬编码字符串（特殊校验码、账号、特定数值）
- `FLAG_ACTIVITY_CLEAR_TOP` → 清栈跳转（影响回退路径）
- 异步回调（网络请求完成后跳转等）

### Step 3：LLM 生成 8 份文档

拿到源码后，逐个生成以下文档。每份文档聚焦一个维度，独立分析。

---

#### 📋 文档1：业务全景（Business Overview）

```
分析维度：
- App 属于什么业务领域
- 核心功能模块有哪些
- 哪些功能已实现 vs 暂未开放（仅 Toast）
- 技术栈（从 build.gradle 推断导航框架/网络库/DI 框架）

输出 JSON：
{
  "businessType": "移动电商/工具/社交/...",
  "summary": "一句话描述这个 App 是干什么的",
  "modules": ["模块名: 功能描述"],
  "unimplemented": ["功能名: 现状描述（如：点击仅弹Toast）"],
  "techStack": {
    "navigation": "startActivity / Jetpack Navigation",
    "network": "Retrofit / 无网络",
    "di": "Hilt / 无"
  }
}
```

---

#### 🔄 文档2：用户旅程地图（User Journey Map）

```
分析维度：
- 用户从 Launcher Activity 开始的所有完整路径
- 每条路径的触发方式和前置条件
- 每个步骤的关键控件 ID
- 路径的终点和预期状态
- 是否存在快捷路径（绕过正常流程）

输出 JSON：
{
  "journeys": [
    {
      "name": "流程名（如：核心购买流程）",
      "priority": "P0必测/P1重要/P2可选",
      "steps": [
        {
          "step": 1,
          "page": "LoginFlowActivity",
          "action": "输入用户名和密码，点击登录",
          "keyControls": ["et_username", "et_password", "btn_login"],
          "waitCondition": "等待页面跳转或 Toast 出现"
        }
      ],
      "preconditions": ["前置状态：App 处于未登录状态"],
      "expectedFinalState": "页面跳转至 HomeFlowActivity"
    }
  ]
}
```

---

#### ✅ 文档3：验证点与断言（Assertions）

**这是最关键的文档。** AI 测试 Agent 需要知道每个操作后如何判断成功或失败。

```
分析维度：
- 每个关键操作后，UI 应该发生什么变化？
- 成功时：跳转到哪个页面 / 出现什么 Toast 文本 / 哪个控件变化
- 失败时：停在哪个页面 / 出现什么错误提示
- 操作后需要等待多久才能断言（同步/异步）

输出 JSON：
{
  "assertions": [
    {
      "scenario": "场景描述（如：空账号点登录）",
      "page": "LoginFlowActivity",
      "trigger": "btn_login",
      "successCondition": {
        "type": "pageSwitch / toast / controlChange",
        "target": "跳转到 HomeFlowActivity",
        "detail": "Activity 变为 HomeFlowActivity"
      },
      "failureCondition": {
        "type": "toast",
        "target": "Toast 文本包含「请输入手机号/邮箱」",
        "detail": "页面停留在 LoginFlowActivity"
      },
      "waitMs": 500,
      "note": "登录是同步操作，无需长等待"
    },
    {
      "scenario": "功能B前置条件未满足时触发操作",
      "page": "<TargetActivity>",
      "trigger": "<action_button>",
      "successCondition": {
        "type": "pageSwitch",
        "target": "跳转到 PageB"
      },
      "failureCondition": {
        "type": "toast",
        "target": "Toast 文本包含「请满足前置条件」"
      },
      "note": "前置条件：<checkbox_id> 等必要条件未满足时，操作应被阻断"
    }
  ]
}
```

---

#### 🔗 文档4：状态依赖图（State Dependencies）

```
分析维度：
- 哪些功能需要 App 处于特定状态才能访问？
- 功能间的依赖关系（如：必须先登录才能访问核心功能）
- 操作会如何改变状态（如：核心操作完成后页面状态重置）
- 状态的持久化方式（内存 vs SharedPreferences vs 数据库）

输出 JSON：
{
  "stateDependencies": [
    {
      "feature": "进入功能模块B",
      "requires": ["用户已完成登录流程"],
      "howToReach": "从登录页完成登录后，进入 HomeFlowActivity 点击对应入口"
    },
    {
      "feature": "触发核心操作",
      "requires": ["已进入目标页面", "至少满足一项前置条件（如 <checkbox_id> 已勾选）"],
      "howToReach": "进入 <TargetActivity>，满足前置条件后点击 <action_button>"
    }
  ],
  "stateChanges": [
    {
      "action": "核心操作完成",
      "before": "已进入目标页面，操作前状态已满足",
      "after": "清栈跳转回 HomeFlowActivity，页面状态未持久化（内存数据）",
      "implication": "测试操作完成后，重新进入目标页面需要重新构造前置状态"
    }
  ]
}
```

---

#### ⚠️ 文档5：边界与异常场景（Edge Cases）

```
分析维度：
- 数值边界：最小值、最大值、边界值±1
- 空值/非法输入：每个表单的验证规则
- 状态边界：某个功能恰好在满足/不满足条件时的行为
- 并发/重复操作：快速点击两次会怎样

输出 JSON：
{
  "edgeCases": [
    {
      "scenario": "数值输入最小值（边界）",
      "page": "PageA",
      "setup": "<value_display_id> 当前为最小值",
      "action": "点击减少数量按钮",
      "expected": "数量保持最小值，出现 Toast「已达最小值」",
      "testValue": "最小值时再减",
      "assertType": "toast + noChange"
    },
    {
      "scenario": "数值输入超上限（超界）",
      "page": "PageA",
      "setup": "<value_display_id> 当前为最大值",
      "action": "点击增加数量按钮",
      "expected": "数量保持最大值，出现 Toast「超出范围」",
      "assertType": "toast + noChange"
    },
    {
      "scenario": "输入框大小写敏感验证",
      "page": "PageA",
      "action": "输入框输入特殊值的小写形式，点击提交",
      "expected": "Toast 提示「操作成功」（大小写不敏感）",
      "assertType": "toast"
    }
  ]
}
```

---

#### 🚫 文档6：陷阱与禁区（Traps & Forbidden）

```
分析维度：
- 死路：点了没跳转/只弹 Toast 的功能入口
- 不可逆操作：执行后会破坏测试状态
- 外部依赖：需要真实环境才能完成（支付/短信/网络）
- 危险操作：会删除数据、清空状态、影响其他测试

输出 JSON：
{
  "deadEnds": [
    {
      "page": "LoginFlowActivity",
      "control": "tv_register / tv_forgot",
      "reason": "点击仅弹 Toast「功能暂未开放」，不跳转",
      "action": "测试时直接跳过，不要点击"
    }
  ],
  "externalDependencies": [
    {
      "feature": "微信/支付宝登录",
      "dependency": "需要手机安装对应 App 并已登录",
      "testStrategy": "Demo 中直接跳转 HomeActivity，无真实鉴权，可测试"
    }
  ],
  "irreversibleActions": [
    {
      "action": "提交订单",
      "consequence": "FLAG_ACTIVITY_CLEAR_TOP 清栈，返回首页，页面状态重置",
      "recovery": "重新走加购流程"
    }
  ],
  "dangerous": []
}
```

---

#### 🎯 文档7：测试策略与优先级（Test Strategy）

```
分析维度：
- 哪些是 P0（核心链路，必须通过才能上线）
- 哪些是 P1（重要功能，尽量覆盖）
- 哪些是 P2（边界/次要，有时间再测）
- 建议的测试执行顺序（考虑状态依赖）
- 每轮测试的最小集合（Smoke Test）

输出 JSON：
{
  "smokeTest": ["最小可行测试集，5步内验证核心链路"],
  "priorities": {
    "P0": ["必测场景，任何一个失败都是 Blocker"],
    "P1": ["重要场景"],
    "P2": ["边界/次要场景"],
    "skip": ["明确跳过的场景和原因"]
  },
  "suggestedOrder": [
    {"step": 1, "action": "先完成登录，建立已登录状态"},
    {"step": 2, "action": "走核心购买链路验证主流程"}
  ],
  "riskAreas": ["容易漏测但很重要的场景"]
}
```

---

#### 🔧 文档8：测试数据字典（Test Data）

```
分析维度：
- 有效数据（能触发成功路径的数据）
- 无效数据（能触发错误提示的数据）
- 边界数据（触发边界行为的数据）
- 硬编码的特殊值（校验码/魔法数字）

输出 JSON：
{
  "validInputs": [{"field": "校验码", "values": ["CODE123"], "effect": "校验通过"}],
  "invalidInputs": [{"field": "校验码", "values": ["WRONG"], "effect": "提示无效"}],
  "boundaryValues": [
    {"field": "数值型控件", "min": 1, "max": 10, "testValues": [0, 1, 10, 11]}
  ],
  "enumOptions": {
    "选项A": ["值1", "值2", "值3"]
  },
  "specialCases": ["空字符串", "超长输入", "特殊字符", "大小写变体"]
}
```

---

#### 🧪 文档9：可执行测试用例（Executable Test Cases）

这是最关键的文档，为 AI Agent 提供可直接执行的测试步骤，包含完整前置状态设置。

```
分析维度：
- 每个关键场景的完整操作序列（含前置状态设置）
- 边界值测试（最小值/最大值/非法值）
- 负向测试（应该失败的场景）
- 每个步骤后的验证点

输出 JSON：
{
  "testCases": [
    {
      "id": "tc_001",
      "name": "表单提交成功跳转（正向）",
      "page": "PageA",
      "priority": "P0",
      "category": "happy_path",
      "setup": [
        {"action": "input", "target": "et_field1", "value": "有效值", "description": "填入有效数据"},
        {"action": "input", "target": "et_field2", "value": "有效值", "description": "填入有效数据"}
      ],
      "execute": {
        "action": "tap",
        "target": "btn_submit",
        "description": "点击提交"
      },
      "verify": {
        "type": "pageSwitch",
        "expected": "跳转到 PageB",
        "failSign": "停留在 PageA 或弹错误 Toast",
        "isBug": "有效输入无法提交是 Bug"
      },
      "waitMs": 500
    },
    {
      "id": "tc_002",
      "name": "数值控件减少操作有效性验证（边界）",
      "page": "PageA",
      "priority": "P1",
      "category": "boundary",
      "setup": [
        {"action": "readValue", "target": "tv_counter", "saveAs": "beforeVal", "description": "记录操作前的值"}
      ],
      "execute": {
        "action": "tap",
        "target": "btn_minus",
        "description": "点击减少按钮"
      },
      "verify": {
        "type": "valueChange",
        "readTarget": "tv_counter",
        "compareWith": "beforeVal",
        "expected": "值减少1",
        "failSign": "值未变化（按钮无响应）",
        "isBug": "减少按钮点击后值不变是 Bug"
      },
      "waitMs": 300
    },
    {
      "id": "tc_003",
      "name": "输入框大小写不敏感验证（负向）",
      "page": "PageA",
      "priority": "P1",
      "category": "boundary",
      "setup": [],
      "execute": {
        "action": "sequence",
        "steps": [
          {"action": "input", "target": "et_code", "value": "code123", "description": "输入小写形式"},
          {"action": "tap", "target": "btn_apply", "description": "点击应用"}
        ]
      },
      "verify": {
        "type": "toast",
        "expected": "Toast含「操作成功」（大小写不敏感）",
        "failSign": "Toast含「无效」或「格式错误」",
        "isBug": "小写输入被拒绝而大写接受，说明存在大小写敏感 Bug"
      },
      "waitMs": 300
    }
  ]
}
```

---

### Step 4：生成 quickSummary（最重要）

基于 9 份文档，用自然语言写一段 300 字以内的总结，直接给 AI 测试 Agent 读：

```
这是一个【业务类型】的 App（包名：xxx）。

【核心流程】：从 XxxActivity 开始，依次经过...最终到达...。
关键步骤：①先完成前置条件（如登录）→ ②进入目标页面 → ③满足操作前置状态 → ④执行核心操作 → ⑤验证结果。

【断言要点】：
- 登录成功：页面跳转到 HomeFlowActivity，出现「登录成功」Toast
- 核心操作成功：页面跳转到目标页面，出现「操作成功」Toast
- 流程完成：操作成功后状态更新，视情况清栈返回上一页面

【必须注意】：
- 前置条件未满足时操作会被阻断（Toast提示），需先确认 <checkbox_id> 等必要条件
- 数值型控件有范围限制，超界有 Toast 提示但不改变数值
- 死路入口（如仅弹 Toast 的功能）不要点击，避免测试中断

【测试数据】：校验码等特殊值参见文档8；账号密码任意非空字符串均可登录（Demo 无真实验证）。

【测试顺序建议】：完成登录等前置状态 → 进入目标页面 → 执行核心操作 → 验证断言。

【关键测试用例】：①必填项为空提交被阻断②数值增减按钮操作有效③大小写不敏感校验④空状态下数值显示合理
```

### Step 5：打包 static-profile

```json
{
  "appPackage": "com.xxx",
  "appVersion": "x.x.x",
  "generatedAt": "ISO时间戳",
  "source": "android-static-analyzer-skill",
  "quickSummary": "...（上面的自然语言总结）",
  "docs": {
    "businessOverview": {},
    "userJourneys": {},
    "assertions": {},
    "stateDependencies": {},
    "edgeCases": {},
    "trapsAndForbidden": {},
    "testStrategy": {},
    "testData": {},
    "testCases": { "testCases": [] }
  }
}
```

### Step 6：保存到本地文件

将 static-profile.json 保存到项目根目录：

```bash
echo '<json>' > <project_path>/static-profile.json
```

然后告诉用户：
- 文件路径：`<project_path>/static-profile.json`
- 在测试平台「自动测试」页面，点「导入先验知识」按钮，选择此文件上传即可
- 或者平台 server 启动后执行：`curl -X POST http://localhost:2601/api/v1/sdk/static-profile -H "Content-Type: application/json" -d @<project_path>/static-profile.json`

**不要自动 POST 到平台**，由用户手动导入。

---

## 质量检查清单

生成完成后，对照检查：

- [ ] quickSummary 读完能直接开始测试，不需要再查其他文档
- [ ] 每个关键操作都有成功和失败两种断言条件
- [ ] 所有边界值都有对应的测试数据和预期行为
- [ ] 死路已明确列出并说明跳过原因
- [ ] 状态依赖图能指导测试的执行顺序
- [ ] 不可逆操作有对应的恢复策略
- [ ] 外部依赖已声明（测试前需要什么环境）

## 输出原则

- **可执行 > 可描述**：每条信息都要说清楚「AI 测试 Agent 拿到这个怎么用」
- **断言要具体**：不说「登录成功跳转」，说「Activity 变为 HomeFlowActivity 且出现含「欢迎」的 Toast」
- **陷阱要预警**：明确说「不要点 tv_register」，不只说「注册未开放」
- **数据要可直接用**：校验码、账号、边界值都是可以直接填入输入框的值
