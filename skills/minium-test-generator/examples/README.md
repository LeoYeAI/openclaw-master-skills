# Minium 测试用例生成器 - 示例文件

本目录包含通用的示例文件，展示如何使用生成器技能。

---

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `README.md` | 本说明文件 |
| `generated_test.py` | 通用的测试用例模板 |

---

## 📝 使用说明

### 1. 准备你的录制脚本

将 Minium 录制的 `.py` 文件保存到项目目录，例如：
```python
#!/usr/bin/env python3
import minium

class FirstTest(minium.MiniTest):
    def test(self):
        self.logger.info("我的测试场景")
        
        # step_0: 打开页面
        self.app.relaunch("/pages/home/home")
        
        # step_1: 点击元素
        element = self.page.get_element("view.button")
        element.tap()
        
        # ... 更多步骤
```

### 2. 复制给我生成

**最简单的方式**: 直接复制录制脚本内容发送给我，我自动生成！

或者你也可以手动运行生成脚本：
```bash
# 进入你的项目目录
cd <你的项目目录>

# 运行生成脚本
python <技能包路径>/scripts/generate_pages.py \
    --input <录制脚本路径> \
    --output <测试用例输出目录> \
    --pages <页面类目录>
```

### 3. 验证步骤

```bash
# 运行验证工具
python <技能包路径>/scripts/validate_steps.py \
    --input <录制脚本路径> \
    --test <测试用例路径>
```

### 4. 运行测试

```bash
# 使用你的测试运行命令
<你的测试运行命令>
```

---

## 📊 示例结构

### 生成的页面类

```python
# -*- coding: utf-8 -*-
"""
页面名称
页面路径：/pages/xxx/xxx
"""

from time import sleep
from base.basedef import BaseDef


class YourPage(BaseDef):
    """页面对象类"""

    # ========== 元素声明 ==========
    # 按钮名称：元素描述
    element_name = '选择器'

    def your_method(self):
        """
        方法说明
        
        录制脚本对应步骤:
            step_x: 步骤描述
        """
        # step_x: 操作说明
        self.tap(self.element_name)
```

### 生成的测试用例

```python
# -*- coding: utf-8 -*-
"""
测试用例名称
生成时间：2026-03-23
录制脚本：FirstTest.minium
"""

from base.basepage import BasePage
from pages.pages.your_page.your_page import YourPage


class TestYourFeature(BasePage):
    """测试用例类"""

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.YourPage = YourPage(self)

    def test_your_flow(self):
        """
        测试流程说明
        
        录制脚本步骤：X 步（一个不漏）
        """
        
        # ========== step_1: 页面 - 操作 ==========
        self.YourPage.your_method()
        
        self.logger.info("流程执行完成")
```

---

## ⚠️ 注意事项

### 1. 替换示例内容

`generated_test.py` 只是一个**通用模板**，实际使用时需要：

- ✅ 替换为你自己的页面类导入
- ✅ 替换为你的实际测试逻辑
- ✅ 根据你的录制脚本调整步骤

### 2. 遵循项目规范

- ✅ 元素声明在类顶部
- ✅ 方法在元素声明下面
- ✅ 在方法注释中标注对应步骤
- ✅ 使用 `validate_steps.py` 验证步骤完整性

### 3. 避免业务耦合

技能包是**通用的**，不应包含：

- ❌ 特定业务逻辑
- ❌ 特定业务方法
- ❌ 特定业务数据

这些应该在**你的项目代码**中实现，而不是技能包中。

---

## 📖 相关文档

- [SKILL.md](../SKILL.md) - 完整技能说明
- [../快速开始.md](../快速开始.md) - 5 分钟上手指南
- [../docs/代码规范.md](../docs/代码规范.md) - 代码规范详细说明
- [../docs/项目基础规范.md](../docs/项目基础规范.md) - 项目结构和基类封装
- [../core-skills/避免漏掉步骤.md](../core-skills/避免漏掉步骤.md) - 核心技能

---

_最后更新：2026-03-24_
