---
name: minium-test-generator
version: 11.0.0
description: Minium 录制脚本转测试用例工具。自动解析录制脚本，生成符合规范的测试用例和页面对象，确保步骤完整、逻辑一致。
license: MIT
---

# Minium 测试用例生成器

## 📖 描述

本技能用于将 Minium 录制脚本自动转换为符合项目规范的测试用例，确保步骤一个不漏，逻辑完全一致。

**核心能力**:
- ✅ 解析录制脚本，提取所有步骤
- ✅ 生成符合规范的页面对象和测试用例
- ✅ 自动验证步骤完整性
- ✅ 避免漏掉步骤和简化逻辑

---

## ⚡ 核心规则（必须遵守！）

### 🚨 第一条：必须先确认目录，再生成！

**当用户提供录制文件时，禁止直接生成！**

**正确流程：**

```
第 1 步：询问目录
→ "好的，我来帮你生成测试用例。请问测试用例目录在哪里？（完整路径）"
→ 等待用户回复

第 2 步：检查目录是否存在
→ 如果目录不存在 → 走【新建项目】流程
→ 如果目录已存在 → 走【添加到现有目录】流程

第 3 步：确认创建方式
→ 向用户展示将要创建/添加的文件列表
→ 等待用户确认

第 4 步：生成内容
→ 新建：创建完整项目结构
→ 添加：仅新增文件，不覆盖已有文件
```

**错误示范（禁止！）：**
- ❌ 用户给录制脚本 → 直接生成（未询问目录）
- ❌ 假设目录结构
- ❌ 覆盖用户原有文件

---

### 🚨 第二条：已存在目录 → 先阅读现有代码结构！

**当目录已存在时，禁止直接生成！**

**正确流程：**

```
第 1 步：读取现有文件结构
→ 列出目录内容（pages/、test_cases/、*.py 等）

第 2 步：阅读已有代码
→ 阅读 pages/ 中的现有 Page Object
→ 分析命名规范、类命名、元素定位风格
→ 阅读 test_*.py 中的现有测试用例
→ 分析测试结构、断言风格、等待方式

第 3 步：总结现有规则
→ Page Object 命名规则（如：驼峰/下划线）
→ 元素定位规则（如：优先 selector 还是 xpath）
→ 测试用例结构（如：是否使用 mark_step_start）
→ 截图点命名规则（如：step_1、tap_1 等）

第 4 步：按现有规则生成新用例
→ 新 Page Object 遵循已有命名和结构
→ 新测试用例遵循已有风格和格式
→ 不引入与现有代码冲突的规范
```

**示例：**
```
我：检测到目录已存在，我先阅读一下现有代码结构...

[阅读 pages/ 和 test_*.py 后]

我：现有代码规则如下：
- Page Object 命名：大驼峰（如 GroupHomepage）
- 元素定位：优先 selector，xpath 备用
- 测试结构：使用 mark_step_start 和 capture
- 截图点命名：动作 + 序号（如 tap_1、scroll_2）

我将按此规则生成新用例，确认吗？
```

---

### 🚨 第三条：同一个页面 → 只需追加方法，不要新建文件！

**当 Page Object 文件已存在时：**

```
❌ 错误做法：
- 创建新文件：pages/xxx_new.py
- 或创建重复文件：pages/xxx/xxx_v2.py
- 或创建分散的多个小方法

✅ 正确做法：
- 在原有文件末尾追加新方法
- 保持原有代码不变
- 同一个页面的操作整合到一个方法里
- 使用 basedef.py 中封装的方法（tap()、send_key()）
```

**示例：**
```
原文件：publish_start_group.py (已有 1000 行)

❌ 错误：创建多个分散小方法
    def input_theme(self): ...
    def click_help_entry(self): ...
    def click_reward_switch(self): ...

✅ 正确：整合到一个完整方法
    def pub_group_supply(self, theme_text="xxx"):
        """跟团供货模式发布完整流程"""
        self.send_key(self.theme_input, theme_text)
        self.tap(self.promise_btn)
        self.scroll_to(400)
        self.tap(self.help_entry)
        ...
```

---

### 🚨 第四条：根据页面路径选择 testcase 目录！

**用例存放目录规则：**

1. **分析录制脚本中的页面路径**
   - 查看 URL 中的路径结构，如：
     - `/pro/pages/homepage/group-homepage/...` → 包含 `homepage`
     - `/pro/pages/home/leaders-management/...` → 包含 `home`
     - `/pro/pages/seq-publish/...` → 包含 `seq-publish`

2. **检查现有 testcase 目录结构**
   - 列出 `testcase/` 下的子目录
   - 对比页面路径中的关键词，选择最匹配的目录
   - 例如：页面路径包含 `home` → 找 `testcase/home_page/` 或 `testcase/home/`

3. **没有合适的目录时**
   - 根据页面路径中的关键词创建新目录
   - 例如：页面路径是 `/pro/pages/seq-publish/...` → 创建 `testcase/seq_publish/`

**核心原则：看项目的实际目录结构，不要硬编码映射关系！**

---

### 🚨 第五条：先阅读用户代码，再决定使用什么方法！

**Page Object 核心规则：**

1. **先阅读用户的基类代码（如 basedef.py）**
   - 检查用户是否封装了点击、输入等方法
   - 如果有封装 → 使用用户的封装方法
   - 如果没有封装 → 生成封装方法并使用

2. **检查用户的封装方式**
   - 点击方法：可能是 `tap()`, `click()`, `click_element()` 等
   - 输入方法：可能是 `send_key()`, `input_text()`, `type()` 等
   - 滚动方法：可能是 `scroll_to()`, `scroll()` 等

3. **元素定位策略**
   - **第一选择：CSS selector**（如 `view.btn-know.button`）
   - **用户反馈找不到元素时** → 补充 xpath
   - **还找不到时** → 补充 text 匹配
   - **不要一开始就生成一堆备用方案！**

4. **元素定位与操作分离**
   - 元素常量：使用中文注释说明用途
   - **每个元素都必须有对应的操作方法**
   - 禁止只有元素定义没有方法

5. **方法命名规范**
   - 动词开头：`click_xxx`, `input_xxx`, `select_xxx`
   - 语义清晰：方法名能清楚表达操作意图

6. **不要返回 self（除非需要链式调用）**
   - 大部分方法不需要返回 `self`
   - 只有需要连续调用时才返回

7. **不要照搬录制脚本的等待时间！**
   - 录制脚本中的 `self.page.wait_for(x)` 是录制工具自动生成的
   - 用户的基类方法（如 `tap()`, `send_key()`）内部已有等待逻辑
   - **禁止生成多余的 `sleep()` 或 `wait_for()`**
   - 除非用户明确要求添加等待

8. **不需要生成 `.bat` 运行脚本**
   - 用户有自己的运行方式（如 `run.py`）
   - 除非用户明确要求，否则不生成 `.bat` 文件

**示例：**

```python
# 情况 1：用户已有封装方法（如 basedef.py 中有 tap() 和 send_key()）
class SelectFollowReward(BaseDef):
    reward_value_input = "..."
    confirm_btn = "..."
    
    def input_reward_value(self, value):
        self.send_key(self.reward_value_input, str(value))  # 使用用户的封装
    
    def click_confirm(self):
        self.tap(self.confirm_btn)  # 使用用户的封装

# 情况 2：用户没有封装方法
class SelectFollowReward(BaseDef):
    reward_value_input = "..."
    confirm_btn = "..."
    
    def input_reward_value(self, value):
        self.page.get_element(self.reward_value_input).input(str(value))
    
    def click_confirm(self):
        self.page.get_element(self.confirm_btn).tap()
```

**新建项目结构：**
```
tests/
├── pages/                  # Page Object 层
│   ├── __init__.py         # 导出所有页面对象
│   ├── [页面].py           # 每个页面一个类
│   └── README.md           # PO 模型说明
├── test_cases/             # 测试用例文档
│   └── [用例名].md         # Markdown 格式用例
├── conftest.py             # Pytest 配置
├── run_test.py             # 测试启动脚本
└── test_[用例名].py        # 可执行测试脚本
```

---

## ⚡ 工作流程

### 场景 A：新建项目（目录不存在）

**当用户提供的目录不存在时：**

```
我：好的，我来帮你生成测试用例。

检测到目录不存在，我将为你创建完整的测试项目结构：

📁 [用户提供的路径]/
├── pages/                  # Page Object 层
│   ├── __init__.py
│   ├── [页面 1].py
│   └── [页面 2].py
├── test_cases/             # 测试用例文档
│   └── [用例名].md
├── conftest.py             # Pytest 配置
├── run_test.py             # 测试启动脚本
└── test_[用例名].py        # 可执行测试脚本

确认开始创建吗？
```

**用户确认后：**
- 创建所有目录和文件
- 生成 Page Object 框架
- 生成第一个测试用例

---

### 场景 B：添加到现有目录（目录已存在）

**当用户提供的目录已存在时：**

```
我：好的，我来帮你生成测试用例。

检测到目录已存在，我将在现有目录下添加新用例：

📁 [用户提供的路径]/
├── pages/                  # 新增 Page Object
│   └── [新页面].py
├── test_cases/             # 新增测试用例文档
│   └── [新用例名].md
└── test_[新用例名].py      # 新增测试脚本

⚠️ 不会覆盖已有文件

确认开始创建吗？
```

**用户确认后：**
- 仅创建新文件
- 不修改已有文件
- 如需更新已有 Page Object，先询问用户

---

## 📋 目录检查方法

**使用 exec 检查目录是否存在：**

```bash
# Windows PowerShell
Test-Path "<用户提供的路径>"

# 返回 True → 目录存在 → 走添加流程
# 返回 False → 目录不存在 → 走新建流程
```

**检查子目录结构：**

```bash
# 检查是否有 pages 目录
Test-Path "<路径>/pages"

# 检查是否有 test_cases 目录
Test-Path "<路径>/test_cases"

# 检查是否有 conftest.py
Test-Path "<路径>/conftest.py"
```

**根据检查结果判断：**
- 如果 `pages/` 存在 → 追加新 Page Object
- 如果 `pages/` 不存在 → 创建 `pages/` 目录
- 如果 `test_cases/` 存在 → 追加新用例文档
- 如果 `test_cases/` 不存在 → 创建 `test_cases/` 目录

---

## 📝 完整对话示例

### 示例 1：新建项目

```
你：帮我生成测试用例
[粘贴录制脚本]

我：好的，我来帮你生成测试用例。

首先，请告诉我：
1. 测试用例目录在哪里？（完整路径）

你：D:\projects\minium-tests\scenario-a

我：好的，我来检查目录...

检测到目录不存在，我将为你创建完整的测试项目结构：

📁 D:\projects\minium-tests\scenario-a\
├── pages/
│   ├── __init__.py
│   ├── homepage.py
│   └── detail_page.py
├── test_cases/
│   └── scenario_a.md
├── conftest.py
├── run_test.py
└── test_scenario_a.py

确认开始创建吗？

你：确认

我：✅ 项目结构已创建完成！

[输出所有文件内容]
```

### 示例 2：添加到现有目录

```
你：帮我生成测试用例
[粘贴录制脚本]

我：好的，我来帮你生成测试用例。

首先，请告诉我：
1. 测试用例目录在哪里？（完整路径）

你：C:\workspace\expression-trainer-miniprogram\tests

我：好的，我来检查目录...

检测到目录已存在，我将在现有目录下添加新用例：

📁 C:\workspace\expression-trainer-miniprogram\tests\
├── pages/                  # 新增 Page Object
│   └── [新页面].py
├── test_cases/             # 新增测试用例文档
│   └── [新用例名].md
└── test_[新用例名].py      # 新增测试脚本

⚠️ 不会覆盖已有文件

确认开始创建吗？

你：确认

我：✅ 测试用例已添加完成！

[输出新增文件内容]
```

---

## ⚡ 快速触发

**当你有以下需求时，直接说即可**:

1. **"我给你一个录制文件，帮我生成测试用例"** → 触发流程
2. **"帮我生成测试用例"** + 录制脚本内容 → 触发流程
3. **"验证一下测试用例是否完整"** → 直接验证
4. **"解析这个录制脚本"** → 直接解析

**示例**:
```
你：我给你一个录制文件，帮我生成测试用例
[从你的录制脚本目录找到 Python 文件，复制内容粘贴]

我：好的，我来帮你生成测试用例。

首先，请告诉我：
1. 测试用例目录在哪里？（完整路径）
2. 是否有现有的测试项目结构？
```

---

## 📁 录制脚本获取方式


---

## 🎯 触发条件

**核心触发场景**: 用户提供 Minium 录制脚本，要求生成或验证测试用例

### 1. 用户提供录制文件时 ⭐ 主要触发场景

**触发词**:
- "我给你一个录制文件"
- "我有一份录制脚本"
- "这是我录制的测试脚本"
- "录制文件如下"
- 用户直接粘贴录制脚本代码

**文件路径示例**:
```
<你的录制脚本目录>\[场景名称]\[时间戳]\xxx.py
```

**响应流程**:
```
你：我给你一个录制文件，帮我生成测试用例
[粘贴录制脚本内容]

我：好的，我来帮你生成测试用例。

首先，请告诉我：
1. 测试用例目录在哪里？（完整路径）
2. 是否有现有的测试项目结构？
```

---

### 2. 要求生成测试用例时 ⭐ 主要触发场景

**触发词**:
- "帮我生成测试用例"
- "把这个录制脚本转成测试用例"
- "根据录制脚本生成代码"
- "生成 Minium 测试代码"
- "生成页面对象和测试用例"

**响应流程**:
```
你：帮我生成测试用例
[粘贴录制脚本内容]

我：好的，我来帮你生成测试用例。

首先，请告诉我：
1. 测试用例目录在哪里？（完整路径）
2. 是否有现有的测试项目结构？
```

---

### 3. 要求验证测试用例时

**触发词**:
- "验证一下测试用例是否完整"
- "检查有没有漏掉步骤"
- "验证步骤是否一致"
- "看看有没有漏掉什么步骤"

**示例**:
```
你：帮我验证一下这个测试用例有没有漏掉步骤
录制脚本：<你的录制脚本目录>\xxx.py
测试用例：<你的项目目录>\testcase\xxx\test_xxx.py

我：好的，我来对比验证...
```

---

### 4. 要求解析录制脚本时

**触发词**:
- "解析这个录制脚本"
- "提取录制脚本的步骤"
- "生成步骤清单"
- "看看有多少步"

**示例**:
```
你：帮我解析这个录制脚本，看看有多少步
[从你的录制脚本目录找到 Python 文件，复制内容粘贴]

我：好的，我来运行 parse_steps.py 解析...
```

---

## 🛠️ 技能工具

### parse_steps.py

**功能**: 解析录制脚本，生成步骤清单

**用法**:
```bash
python <技能包路径>/scripts/parse_steps.py \
    --input <录制脚本路径> \
    --output <输出路径>
```

**示例**:
```bash
python scripts/parse_steps.py \
    --input recorded_script.py \
    --output steps_checklist.md
```

---

### generate_pages.py

**功能**: 生成页面对象和测试用例

**用法**:
```bash
python <技能包路径>/scripts/generate_pages.py \
    --input <录制脚本路径> \
    --output <测试用例输出目录> \
    --pages <页面类目录>
```

**示例**:
```bash
python scripts/generate_pages.py \
    --input recorded_script.py \
    --output testcase/xxx/ \
    --pages pages/pages/
```

---

### validate_steps.py

**功能**: 验证测试用例是否漏掉步骤

**用法**:
```bash
python <技能包路径>/scripts/validate_steps.py \
    --input <录制脚本路径> \
    --test <测试用例路径> \
    --report <验证报告路径>
```

**检查项**:
1. 步骤数量是否一致
2. 相邻步骤是否使用了相同的元素
3. 特殊逻辑是否保留
4. 页面跳转是否都有等待

---

## 📋 工作流程

### 阶段 1: 解析录制脚本

```bash
# 1. 运行解析脚本
python scripts/parse_steps.py \
    --input recorded_script.py \
    --output steps_checklist.md

# 2. 查看生成的步骤清单
cat steps_checklist.md
```

**输出**:
- 普通步骤列表
- 特殊逻辑步骤列表（带⚠️标记）
- 循环步骤列表（带🔄标记）
- 步骤对照表模板

---

### 阶段 2: 生成测试用例

```bash
# 运行生成脚本
python scripts/generate_pages.py \
    --input recorded_script.py \
    --output testcase/xxx/ \
    --pages pages/pages/
```

**输出**:
- 页面对象类（追加到已有文件）
- 测试用例（新建文件）
- 步骤对照表

---

### 阶段 3: 验证

```bash
# 运行验证工具
python scripts/validate_steps.py \
    --input recorded_script.py \
    --test testcase/xxx/test_xxx.py \
    --report validation_report.md
```

**输出**:
- 步骤数量验证
- 相邻步骤检查
- 特殊逻辑检查
- 页面跳转等待检查

---

## ⚠️ 质量控制

### 核心原则

1. **不漏掉任何步骤** - 录制脚本的每一步都要在测试用例中有对应
2. **不简化特殊逻辑** - 三层判断、else 判断必须完整保留
3. **不混淆相邻步骤** - 相邻步骤的元素 XPath 必须不同
4. **页面跳转必须等待** - 每个页面跳转后都要添加 `wait_for_page_success()`

### 检查清单

在生成测试用例后，必须检查：

- [ ] 步骤数量是否与录制脚本一致？
- [ ] 特殊逻辑步骤是否保留完整？
- [ ] 相邻步骤的元素是否不同？
- [ ] 页面跳转后是否都添加了等待？
- [ ] 是否运行了 `validate_steps.py` 验证？

---

## 📖 参考文档

| 文档 | 说明 |
|------|------|
| [core-skills/避免漏掉步骤.md](core-skills/避免漏掉步骤.md) | **核心技能：如何避免漏掉步骤** |
| [docs/代码生成质量控制流程.md](docs/代码生成质量控制流程.md) | 完整的质量控制流程 |
| [docs/代码审查清单.md](docs/代码审查清单.md) | 提交前必须逐项检查 |
| [docs/代码规范.md](docs/代码规范.md) | 代码规范详细说明 |

---

## 🧪 使用示例

### 示例 1: 用户提供录制文件

**你**:
```
我给你一个录制文件，帮我生成测试用例

[从你的录制脚本目录找到 Python 文件，复制内容粘贴]
```

**我**:
```
好的，我来使用 minium-test-generator 技能为你生成测试用例。

第 1 步：解析录制脚本...
python scripts/parse_steps.py --input recorded_script.py --output steps_checklist.md

第 2 步：生成测试用例...
python scripts/generate_pages.py --input recorded_script.py --output testcase/xxx/ --pages pages/pages/

第 3 步：验证步骤完整性...
python scripts/validate_steps.py --input recorded_script.py --test testcase/xxx/test_xxx.py --report validation_report.md

✅ 生成完成！测试用例已保存到 testcase/xxx/test_xxx.py
验证报告：validation_report.md
```

---

### 示例 2: 验证测试用例

**你**:
```
帮我验证一下这个测试用例有没有漏掉步骤
录制脚本：<你的录制脚本目录>\recorded_script.py
测试用例：<你的项目目录>\testcase\xxx\test_xxx.py
```

**我**:
```
好的，我来运行 validate_steps.py 验证...

python scripts/validate_steps.py \
    --input <你的录制脚本目录>\recorded_script.py \
    --test <你的项目目录>\testcase\xxx\test_xxx.py \
    --report validation_report.md

验证结果:
✅ 所有步骤都已转换（X 步，一个不漏）
✅ 相邻步骤元素检查通过
✅ 特殊逻辑检查通过
✅ 页面跳转等待检查通过
```

---

## 📊 技能统计

| 指标 | 数值 |
|------|------|
| 支持的文件格式 | Minium 录制脚本 (.py) |
| 生成的文件格式 | Python 测试用例 (.py) |
| 验证检查项 | 4 项 |
| 支持的特殊逻辑 | 三层判断、else 判断、循环、页面跳转 |
| 典型录制脚本路径 | `<你的录制脚本目录>\[场景名称]\[时间戳]\` |

---

## 🚀 快速开始

```bash
# 1. 查看技能文档
cat <技能包路径>/README.md

# 2. 学习核心技能
cat <技能包路径>/core-skills/避免漏掉步骤.md

# 3. 使用工具
python <技能包路径>/scripts/parse_steps.py --help
```

---

_最后更新：2026-03-23_
