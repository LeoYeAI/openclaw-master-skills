---
name: han-jr-system
version: 1.0.0
description: 小翰系统：1688平台自动化供应商联系系统。使用场景：用户需要联系1688供应商、发送询价消息、收集报价时。触发于如联系1688铅笔供应商、搜索dgx spark供应商等任务。严格遵守逐家联系、验证优先、准确性优先原则。
---

# Han Jr System - 1688 供应商联系系统

## Overview

小翰系统提供完整的1688供应商联系自动化工作流，强调：
- **逐家联系**：一次只联系一家供应商，等待回复后再联系下一家
- **严格验证**：每个步骤后10秒First Check，失败则20秒Double Check
- **准确性优先**：宁可慢，不要错，所有操作必须验证后才报告成功
- **真实执行**：使用实际脚本（playwright + Chrome CDP），非模拟

## ⚠️ 重要：反爬虫解决办法

### 问题现象
当搜索频繁或触发安全机制时，页面会跳转到包含 `_____tmd_____` 的URL，并显示滑块验证码。

### 解决方法
使用 `slider_captcha.py` 脚本自动解决滑块验证码：

```bash
python slider_captcha.py --selector "#nc_1_n1z" --distance 260 --duration 1.5
```

**参数说明：**
- `--selector`: 滑块元素的CSS选择器（默认: `#nc_1_n1z`）
- `--distance`: 拖动距离（像素，默认: 260）
- `--duration`: 拖动持续时间（秒，默认: 1.5）

**滑块元素常见选择器：**
```
#nc_1_n1z
.nc_iconfont.btn_slide
span[aria-label="滑块"]
[data-spm-anchor-id*="slide"]
```

### 工作流程（含反爬虫处理）

```bash
# 1. 启动Chrome
python chrome_launch.py

# 2. 搜索供应商
python search_box_v2.py --keyword "铅笔" --num 5 --output suppliers.json

# 3. 如果遇到滑块验证码，自动解决
python slider_captcha.py --selector "#nc_1_n1z" --distance 260

# 4. 继续搜索或联系供应商
python search_box_v2.py --keyword "钢笔" --num 5 --output suppliers2.json
```

### 注意事项
1. **真正的反爬虫标志**：页面上出现 "Sorry, we have detected unusual traffic from your network."
2. **URL包含 `_____tmd_____` 不一定是反爬虫**，可能是其他错误
3. **解决验证码后**，页面会恢复正常，可以继续操作
4. **建议搜索间隔**：每个关键词之间等待 3-5 秒，避免频繁触发

## 依赖安装

首次使用前安装依赖：
```bash
pip install playwright requests beautifulsoup4 easyocr pillow numpy
playwright install chromium
```

## Workflow

### Step 1: 启动Chrome
```bash
python chrome_launch.py
```
- 启动Chrome with remote debugging (port 9222)
- 10秒First Check：验证CDP连接
- 失败则20秒Double Check

### Step 2: 搜索供应商（搜索框输入方式）
```bash
python search_box_v2.py --keyword "铅笔" --num 5 --output suppliers.json
```
- **必须通过搜索框输入关键词**，不要通过URL参数搜索
- 在1688真实搜索（非百度）
- 提取供应商名称、链接、价格、地区
- 10秒First Check：验证结果包含关键词
- 保存到JSON文件（UTF-8编码，避免乱码）

**重要：** 搜索框输入方式更稳定，不易触发反爬虫机制

### Step 3: 处理反爬虫/滑块验证码
```bash
python slider_captcha.py --selector "#nc_1_n1z" --distance 260
```
- 当页面出现滑块验证码时执行
- 模拟人类拖动行为（带随机抖动和缓动函数）
- 验证成功后继续操作

### Step 4: 联系供应商（逐家）
```bash
python 1688_send_message.py --offer <供应商链接> "需要铅笔，请报价"
```
- 打开供应商页面
- 点击"客服"按钮
- 发送询价消息
- 10秒First Check：截图验证消息已发送

### Step 5: 验证步骤
```bash
python verify_step.py --step "step_name" --text "期望文本" --double
```
- 截图当前页面
- OCR识别内容
- 检查是否包含期望文本
- 失败时自动Double Check

### Step 6: 完整工作流
```bash
python pencil_workflow.py
```
- 执行完整流程（启动→搜索→联系→验证）
- 自动处理所有步骤
- 记录到文件

## 脚本说明

### scripts/

| 脚本 | 功能 | 用法 |
|------|------|------|
| `chrome_launch.py` | 启动Chrome并验证 | `python chrome_launch.py` |
| `search_box_v2.py` | 1688搜索（搜索框输入） | `python search_box_v2.py --keyword "铅笔" --num 5` |
| `slider_captcha.py` | **解决滑块验证码** | `python slider_captcha.py --selector "#nc_1_n1z"` |
| `batch_contact_final.py` | **批量联系供应商（推荐）** | `python batch_contact_final.py --keyword "棒球帽" --message "询价" --num 20` |
| `wangwang_chat_manager.py` | **旺旺聊天管理器** | `python wangwang_chat_manager.py --list` |
| `search_contact_fixed.py` | **搜索旺旺联系人（重要）** | `python search_contact_fixed.py --name "供应商"` |
| `supplier_manager.py` | **供应商管理系统** | `python supplier_manager.py list` |
| `1688_send_message.py` | 发送询价消息 | `python 1688_send_message.py --offer "链接" "消息"` |
| `verify_step.py` | 截图OCR验证 | `python verify_step.py --step "name" --text "期望"` |
| `batch_search.py` | 批量搜索多个关键词 | `python batch_search.py` |
| `pencil_workflow.py` | 完整工作流 | `python pencil_workflow.py` |

### references/

- `soul_rules.md` - SOUL.md核心规则摘要
- `popup_handling.md` - 1688弹窗处理指南
- `inquiry_template.md` - 询价消息模板
- `antibot_handling.md` - **反爬虫处理指南（重要）**

## 关键规则

1. **逐家联系**：一次只联系一家，等待回复后再下一家
2. **硬性验证**：每个步骤后必须10秒First Check，失败则20秒Double Check
3. **验证后才报告**：绝不报告"应该成功了"，只报告"已验证成功"
4. **准确性>速度**：宁可慢，不要错
5. **Chrome启动**：必须使用指定命令，失败告知用户
6. **搜索方式**：**必须通过搜索框输入**，不要通过URL参数搜索
7. **编码**：所有输出和文件必须使用UTF-8编码，避免乱码
8. **反爬虫处理**：遇到滑块验证码使用 `slider_captcha.py` 解决
9. **聊天页面管理**：**每次只能有一个旺旺聊天页面打开**，发送完消息后必须关闭，再回到搜索结果页联系下一家

## 🔍 旺旺图标定位规则（重要）

### 搜索结果页旺旺图标
在搜索结果页，每张产品卡片右下角有旺旺图标：

**HTML特征：**
```html
<span class="J_WangWang ww-light ww-static" data-nick="供应商名称">
  <a href="https://air.1688.com/app/ocms-fusion-components-1688/def_cbu_web_im/..." 
     target="_blank" class="ww-link ww-inline ww-online">
    <span>旺旺在线</span>
  </a>
</span>
```

**选择器优先级（按可靠性排序）：**
1. `.J_WangWang` - 主要class名
2. `.ww-light` 或 `.ww-link` - 旺旺链接
3. `a[href*="air.1688.com"][href*="im"]` - 聊天页面链接
4. `a:has-text("旺旺在线")` - 包含"旺旺在线"文本
5. `[data-spm-anchor-id*="offerlist"]` - 商品列表中的旺旺

**使用方法：**
```bash
# 从搜索结果页直接联系供应商
python search_and_contact.py --keyword "棒球帽" --message "询价内容" --num 10
```

### 店铺页旺旺图标
在供应商店铺页，旺旺图标通常在：
- 页面顶部/侧边栏
- 产品详情页右下角
- 特征：`img[src*="O1CN01is8OHl"]` 或 `img[src*="wangwang"]`

**使用方法：**
```bash
# 进入店铺页联系
python contact_supplier_wangwang.py --link "店铺链接" --message "询价内容"
```

---

## 📋 旺旺聊天页面 iframe 处理方法（重要）

### 问题
旺旺聊天页面使用 iframe 架构，消息输入框不在主页面，而是在特定的 frame 中。

### 解决方案

#### Frame 结构
旺旺聊天页面通常包含 4 个 frames：
- **Frame 0**: 主聊天框架（联系人列表）
- **Frame 1**: 消息输入区域 ← **在这里发送消息**
- **Frame 2**: 分析/统计
- **Frame 3**: 空白

#### 正确的发送消息代码
```python
# 遍历所有 frames 找到输入框
for frame in chat_page.frames:
    try:
        # 在 frame 中查找输入框
        inp = frame.locator("pre[contenteditable='true']").first
        if inp.is_visible():
            inp.click()
            inp.fill(message)
            
            # 点击发送按钮
            btn = frame.locator("button:has-text('发送')").first
            if btn.is_visible():
                btn.click()
                print("✓ 消息已发送")
                break
    except:
        continue
```

#### 关键要点
1. ✅ 使用 `page.frames` 遍历所有 frames
2. ✅ 消息输入框通常在 **Frame 1**
3. ✅ 使用 `frame.locator()` 在特定 frame 中查找元素
4. ✅ 不需要点击联系人，直接发送消息即可

#### 完整示例
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    
    # 打开聊天页面
    chat_page = browser.contexts[0].new_page()
    chat_page.goto("旺旺链接", wait_until="domcontentloaded")
    time.sleep(4)
    
    # 发送消息
    message = "我要定制..."
    for frame in chat_page.frames:
        try:
            inp = frame.locator("pre[contenteditable='true']").first
            if inp.is_visible():
                inp.click()
                inp.fill(message)
                btn = frame.locator("button:has-text('发送')").first
                btn.click()
                print("✓ 消息已发送")
                break
        except:
            continue
    
    chat_page.close()
    browser.close()
```

#### 注意事项
- 聊天页面加载需要 4-5 秒等待时间
- 发送完消息后等待 1-2 秒再关闭页面
- 每次只打开一个聊天页面，发送完必须关闭

## 示例：完整工作流程（含反爬虫处理）

### 场景1：批量联系供应商
```bash
# 1. 启动Chrome
python chrome_launch.py

# 2. 批量联系供应商（推荐）
python batch_contact_final.py --keyword "棒球帽" --message "我要定制1000顶，多少钱？" --num 20

# 3. 查看旺旺聊天页面列表
python wangwang_chat_manager.py --list

# 4. 打开第一个旺旺聊天页查看回复
python wangwang_chat_manager.py --open 0 --history

# 5. 回复消息
python wangwang_chat_manager.py --reply "好的，请发样品"
```

### 场景2：传统流程
```bash
# 1. 启动Chrome
python chrome_launch.py

# 2. 搜索第一个关键词
python search_box_v2.py --keyword "帽子" --num 5 --output hat_suppliers.json

# 3. 如果遇到滑块验证码，解决它
# （页面URL包含 _____tmd_____ 且显示滑块）
python slider_captcha.py --selector "#nc_1_n1z" --distance 260

# 4. 继续搜索其他关键词
python search_box_v2.py --keyword "外套" --num 5 --output coat_suppliers.json

# 5. 查看结果
cat hat_suppliers.json
cat coat_suppliers.json

# 6. 联系第一家供应商
python 1688_send_message.py --offer "https://detail.1688.com/offer/xxx.html" "需要帽子，请报价"

# 7. 验证发送成功
python verify_step.py --step "message_sent" --text "报价" --double
```

---

## 🆕 新功能1：旺旺聊天管理器

### 功能说明
`wangwang_chat_manager.py` 是一个全新的工具，用于管理旺旺聊天页面：

1. **列出所有旺旺聊天页** - 查看当前打开的所有旺旺聊天页面
2. **打开指定聊天页** - 切换到指定的旺旺聊天页面
3. **搜索联系人** - 在联系人列表中搜索特定供应商
4. **查看聊天记录** - 获取并显示聊天记录
5. **回复消息** - 在指定聊天页面发送回复
6. **打开最后访问的页面** - 快速回到上次访问的旺旺页

### 使用方法

```bash
# 列出所有旺旺聊天页
python wangwang_chat_manager.py --list

# 打开第1个旺旺聊天页
python wangwang_chat_manager.py --open 0

# 搜索联系人
python wangwang_chat_manager.py --open 0 --search "供应商名称"

# 查看聊天记录
python wangwang_chat_manager.py --open 0 --history

# 回复消息
python wangwang_chat_manager.py --open 0 --reply "好的，请报价"

# 打开最后访问的旺旺页
python wangwang_chat_manager.py --last

# 打开最后访问的页并回复
python wangwang_chat_manager.py --last --reply "收到"
```

### 工作流程示例

```bash
# 1. 先联系一批供应商
python batch_contact_final.py --keyword "帽子" --message "询价" --num 10

# 2. 等待一段时间后，查看有哪些供应商回复了
python wangwang_chat_manager.py --list

# 3. 打开第一个聊天页查看回复
python wangwang_chat_manager.py --open 0 --history

# 4. 如果有回复，继续沟通
python wangwang_chat_manager.py --reply "请问最低价格是多少？"

# 5. 查看其他供应商的回复
python wangwang_chat_manager.py --open 1 --history
```

---

## 🆕 新功能2：搜索旺旺联系人（重要）

### 功能说明
`search_contact_fixed.py` 用于搜索特定供应商并获取最新对话记录：

1. **在搜索框输入供应商名称**
2. **按 Enter 触发搜索**
3. **点击第一个联系人**
4. **等待聊天内容加载（5秒）**
5. **获取完整对话记录**
6. **同步到本地数据库**

### 重要步骤（已验证）

```bash
# 搜索供应商并获取最新对话
python search_contact_fixed.py --name "东莞宝瑞森"
```

**关键要点：**
- 搜索框选择器：`input.ant-input` (placeholder="搜索联系人")
- 输入后按 `Enter` 触发搜索
- 等待 **4秒** 让搜索结果加载
- 点击联系人后等待 **5秒** 让聊天内容加载
- 使用 `bring_to_front()` 确保页面激活
- 截图验证每一步

### 工作流程

```bash
# 1. 搜索并获取供应商最新回复
python search_contact_fixed.py --name "供应商名称"

# 2. 查看生成的截图验证
# step2_search_results.png - 搜索结果
# step4_chat_loaded.png - 聊天内容

# 3. 查看数据库中的记录
python supplier_manager.py get --id 27
```

---

## 🆕 新功能3：供应商管理系统

### 功能说明
`supplier_manager.py` 是一个本地供应商管理系统，可以：

1. **记录供应商信息** - 名称、产品、价格、链接、联系方式等
2. **管理沟通历史** - 记录所有发出的消息和收到的回复
3. **标记供应商状态** - 待联系、已联系、已回复、已成交等
4. **搜索和筛选** - 按状态、产品类型筛选供应商
5. **导入导出** - 从搜索结果导入，导出供应商列表

### 数据文件
所有数据保存在 `suppliers_database.json` 文件中

### 使用方法

```bash
# 从搜索结果导入供应商
python supplier_manager.py import

# 列出所有供应商
python supplier_manager.py list

# 列出已回复的供应商
python supplier_manager.py list --status 已回复

# 查看供应商详情
python supplier_manager.py get --id 1

# 添加沟通记录（发出消息）
python supplier_manager.py communicate --id 1 --message "询价内容" --direction out

# 添加沟通记录（收到回复）
python supplier_manager.py communicate --id 1 --message "供应商回复内容" --direction in

# 更新供应商状态
python supplier_manager.py update --id 1 --status 已回复

# 显示统计信息
python supplier_manager.py stats

# 导出供应商列表
python supplier_manager.py export --file my_suppliers.json
```

### 工作流程示例

```bash
# 1. 搜索并联系供应商
python batch_contact_final.py --keyword "棒球帽" --message "询价" --num 20

# 2. 导入到供应商管理系统
python supplier_manager.py import

# 3. 查看所有供应商
python supplier_manager.py list

# 4. 记录沟通历史
python supplier_manager.py communicate --id 1 --message "已发送询价" --direction out

# 5. 收到回复后更新
python supplier_manager.py communicate --id 1 --message "价格5元，可以接单" --direction in
python supplier_manager.py update --id 1 --status 已回复

# 6. 查看详情
python supplier_manager.py get --id 1

# 7. 查看统计
python supplier_manager.py stats
```

## 故障排除

| 问题 | 解决 |
|------|------|
| Chrome启动失败 | 检查路径是否正确，是否有其他Chrome占用9222端口 |
| 搜索无结果 | 检查网络连接，1688是否可访问 |
| 消息发送失败 | 检查Chrome是否已登录1688 |
| OCR识别失败 | 安装easyocr: `pip install easyocr` |
| **滑块验证码** | **使用 `slider_captcha.py` 脚本解决** |
| **页面乱码** | **确保使用UTF-8编码输出和保存文件** |
| **搜索被拦截** | **使用搜索框输入方式，避免URL参数搜索** |

---

**注意**：所有脚本使用真实浏览器操作，非模拟。执行前确保已安装依赖。

**重要提醒**：
- 搜索必须通过搜索框输入
- 输出必须使用UTF-8编码
- 遇到滑块验证码使用 `slider_captcha.py` 解决
- 真正的反爬虫页面会显示 "Sorry, we have detected unusual traffic from your network."
