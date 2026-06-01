# 🦞 Minium 测试用例生成器

**版本**: 1.0.0  
**创建时间**: 2026-03-23  
**适用场景**: 微信小程序 Minium 自动化测试

---

## 📖 技能简介

本技能用于将 Minium 录制脚本自动转换为符合项目规范的页面对象和测试用例。

**核心特点**:
- ✅ **步骤完整性** - 确保录制脚本中的每个步骤都被转换，一个不漏
- ✅ **代码规范性** - 遵循项目代码规范（元素在上，方法在下）
- ✅ **自动化生成** - 一键生成页面对象、测试用例、步骤对照表
- ✅ **验证工具** - 自动验证步骤完整性，防止遗漏

---

## 🚀 快速开始

**最简单的方式**: 直接复制录制脚本内容发送给我，我自动生成！

详细教程请查看：[快速开始.md](快速开始.md)

---

## 📁 目录结构

```
minium-test-generator/
├── SKILL.md                          # 技能说明文档
├── 快速开始.md                        # 5 分钟上手指南
├── core-skills/                       # 核心技能
│   └── 避免漏掉步骤.md                 # 如何避免漏掉步骤
├── docs/                              # 文档
│   ├── 代码生成质量控制流程.md         # 完整流程
│   ├── 代码审查清单.md                 # 提交前检查
│   ├── 代码规范.md                     # 代码规范
│   ├── 步骤对照表模板.md               # 通用模板
│   └── 项目基础规范.md                 # 项目规范
├── scripts/                           # 工具脚本
│   ├── generate_pages.py              # 生成脚本
│   ├── parse_steps.py                 # 解析工具
│   └── validate_steps.py              # 验证工具
└── examples/                          # 示例
    ├── README.md                      # 示例说明
    └── generated_test.py              # 测试用例示例
```

---

## 🎯 核心功能

### 1. 脚本解析

- 自动解析 Minium 录制脚本
- 提取所有步骤标记（step_1, step_2, ...）
- 识别操作类型（tap, input, scroll, ...）
- 识别特殊逻辑（三层判断、else 判断等）
- 按页面分组操作

### 2. 代码生成

- 生成页面对象类方法（符合项目规范）
- 生成测试用例（步骤完整）
- 生成步骤对照表（Markdown 格式）

### 3. 步骤验证

- 对比录制脚本和测试用例
- 检查缺失的步骤
- 检查相邻步骤元素是否混淆
- 检查特殊逻辑是否保留
- 检查页面跳转等待
- 生成验证报告

---

## 📋 代码规范

### 页面类

- ✅ 所有元素声明在类顶部
- ✅ 所有方法在元素声明下面
- ✅ 中文注释说明元素功能
- ✅ 方法注释标注对应步骤

### 测试用例

- ✅ 每个步骤都有注释标注
- ✅ 同一个页面的操作调用一个方法
- ✅ 流程说明清晰完整
- ✅ 步骤一个不漏

### 元素选择器

- ✅ **优先使用 CSS 选择器**（简洁高效）
- ⚠️ XPath 作为备选（当 CSS 无法定位时）
- ✅ 三层降级策略（CSS → XPath → inner_text）

详细规范请查看：[docs/代码规范.md](docs/代码规范.md)

---

## 🔧 工具说明

### parse_steps.py

**功能**: 解析录制脚本，生成步骤清单

**参数**:
```bash
--input     录制脚本路径（必需）
--output    步骤清单输出路径（必需）
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

**参数**:
```bash
--input     录制脚本路径（必需）
--output    测试用例输出目录（必需）
--pages     页面类目录（必需）
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

**功能**: 步骤验证工具

**参数**:
```bash
--input     录制脚本路径（必需）
--test      测试用例路径（必需）
--report    生成验证报告路径（可选）
```

**检查项**:
1. 步骤数量是否一致
2. 相邻步骤是否使用了相同的元素
3. 特殊逻辑是否保留
4. 页面跳转是否都有等待

**示例**:
```bash
python scripts/validate_steps.py \
    --input recorded_script.py \
    --test testcase/xxx/test_xxx.py \
    --report validation_report.md
```

---

## ⚠️ 注意事项

### 1. 步骤完整性

- ✅ 生成后**必须**验证步骤完整性
- ✅ 使用 `validate_steps.py` 工具
- ❌ 不要跳过验证步骤

### 2. 元素选择器

- ✅ **优先使用 CSS 选择器**（简洁高效）
- ⚠️ XPath 作为备选
- ❌ 避免使用动态 class 名

### 3. 方法封装

- ✅ 同一个页面的连续操作封装到一个方法
- ✅ 在方法注释中列出所有对应步骤
- ❌ 不要一个操作一个方法

### 4. 等待时间

- ✅ `tap()` 不需要额外等待
- ✅ 滚动后建议加等待
- ❌ 不要每个操作都加等待

---

## 🐛 常见问题

### Q: 元素找不到怎么办？

**A**: 优先使用 CSS 选择器，失败后用 XPath。

```python
# ✅ 推荐：三层降级策略
def click_setting_btn(self):
    # 第 1 层：CSS 选择器（首选）
    element_is_exists = self.page.element_is_exists("view.setting-btn")
    if element_is_exists:
        element = self.page.get_element("view.setting-btn")
    else:
        # 第 2 层：XPath（备选）
        element_is_exists = self.page.element_is_exists(xpath="/page-wrapper/.../view[2]/view")
        if element_is_exists:
            element = self.page.get_element_by_xpath("/page-wrapper/.../view[2]/view")
        else:
            # 第 3 层：inner_text（最后手段）
            element = self.page.get_element_by_xpath("//*", inner_text="未设置")
    element.tap()
```

### Q: 如何验证步骤是否漏掉？

**A**: 使用 `validate_steps.py` 脚本自动验证。

```bash
python scripts/validate_steps.py \
    --input recorded_script.py \
    --test testcase/xxx/test_xxx.py
```

### Q: 测试执行失败怎么办？

**A**: 
1. 查看测试报告中的错误信息
2. 检查元素选择器是否正确
3. 检查是否有步骤遗漏
4. 查看测试截图
5. 告诉我错误信息，我帮你修正

---

## 📖 文档索引

### 核心文档

| 文档 | 说明 | 阅读时间 |
|------|------|---------|
| [SKILL.md](SKILL.md) | 完整技能说明 | 15 分钟 |
| [快速开始.md](快速开始.md) | 5 分钟上手指南 | 5 分钟 |
| [docs/项目基础规范.md](docs/项目基础规范.md) | 项目结构和基类封装说明 | 10 分钟 |

### 核心技能 ⭐

| 文档 | 说明 | 阅读时间 |
|------|------|---------|
| [core-skills/避免漏掉步骤.md](core-skills/避免漏掉步骤.md) | **核心技能：如何避免漏掉步骤** | 10 分钟 |

### 质量控制文档 ⚠️

| 文档 | 说明 | 阅读时间 |
|------|------|---------|
| [docs/代码生成质量控制流程.md](docs/代码生成质量控制流程.md) | 完整的质量控制流程 | 15 分钟 |
| [docs/代码审查清单.md](docs/代码审查清单.md) | 提交前必须逐项检查 | 10 分钟 |
| [docs/代码规范.md](docs/代码规范.md) | 代码规范详细说明 | 10 分钟 |
| [docs/步骤对照表模板.md](docs/步骤对照表模板.md) | 步骤对照表模板 | 5 分钟 |

### 示例文档

| 文档 | 说明 | 阅读时间 |
|------|------|---------|
| [examples/README.md](examples/README.md) | 示例文件说明 | 5 分钟 |

---

## ⚠️ 前置条件

在使用本技能前，请确保你的项目符合以下规范：

1. ✅ **项目结构** - 查看 [`docs/项目基础规范.md`](docs/项目基础规范.md)
2. ✅ **基类封装** - 需要 `base/basedef.py` 和 `base/basepage.py`
3. ✅ **录制脚本** - Minium 录制的 `.py` 文件

**重要**: 如果你的项目没有 `basedef.py` 和 `basepage.py` 基类，请先参考 [`docs/项目基础规范.md`](docs/项目基础规范.md) 进行封装。

---

## 📞 技术支持

- **问题反馈**: 查看 `docs/代码规范.md` 的常见问题章节
- **示例代码**: 查看 `examples/` 目录
- **技能文档**: 查看 `SKILL.md`
- **核心技能**: 查看 `core-skills/避免漏掉步骤.md`

---

_最后更新：2026-03-24_
