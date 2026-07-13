# 反爬虫处理指南

## 概述

1688平台有反爬虫机制，当检测到异常流量时会触发验证码。本指南说明如何识别和处理这些情况。

## 识别反爬虫

### 真正的反爬虫标志
页面上出现以下文字：
```
"Sorry, we have detected unusual traffic from your network."
```

### 常见的反爬虫表现
1. **滑块验证码**：页面上出现需要拖动的滑块元素
2. **URL变化**：页面跳转到包含 `_____tmd_____` 的URL
3. **搜索框消失**：无法找到搜索输入框
4. **页面内容异常**：显示验证页面而非搜索结果

### 不是反爬虫的情况
- URL包含 `_____tmd_____` 但页面正常显示
- 网络连接错误
- 页面加载超时
- JavaScript执行错误

## 解决方法

### 1. 滑块验证码解决

使用 `slider_captcha.py` 脚本：

```bash
python slider_captcha.py --selector "#nc_1_n1z" --distance 260 --duration 1.5
```

**参数说明：**
- `--selector`: 滑块元素的CSS选择器
- `--distance`: 拖动距离（像素）
- `--duration`: 拖动持续时间（秒）

**常见滑块选择器：**
```css
#nc_1_n1z
.nc_iconfont.btn_slide
span[aria-label="滑块"]
[data-spm-anchor-id*="slide"]
.btn_slide
```

### 2. 手动解决

如果自动解决失败，可以：
1. 在Chrome浏览器中手动拖动滑块
2. 完成验证后等待页面恢复
3. 继续执行脚本

### 3. 预防措施

**搜索间隔**：
```python
# 每个关键词之间等待3-5秒
import time
time.sleep(3)  # 等待3秒
```

**批量搜索示例：**
```python
keywords = ["帽子", "外套", "袜子", "手套", "围巾"]
for i, keyword in enumerate(keywords):
    search_1688(keyword)
    if i < len(keywords) - 1:
        time.sleep(3)  # 间隔3秒
```

## 技术细节

### 滑块验证码的工作原理

1. **检测**：页面加载时检测是否为验证码页面
2. **定位**：找到滑块元素的位置
3. **拖动**：模拟人类拖动行为
   - 分段移动
   - 随机抖动
   - 缓动函数（smoothstep）
4. **验证**：检查滑块是否消失

### 代码实现

```python
# 模拟人类拖动
def solve_slider(page, selector, distance, duration):
    slider = page.query_selector(selector)
    box = slider.bounding_box()
    
    start_x = box['x'] + box['width'] / 2
    start_y = box['y'] + box['height'] / 2
    end_x = start_x + distance
    end_y = start_y + random.randint(-5, 5)
    
    # 按下鼠标
    page.mouse.move(start_x, start_y)
    page.mouse.down()
    
    # 分段拖动（模拟人类）
    steps = int(duration * 20)
    for i in range(steps):
        progress = (i + 1) / steps
        ease_progress = progress * progress * (3 - 2 * progress)
        
        target_x = start_x + (end_x - start_x) * ease_progress
        target_y = start_y + (end_y - start_y) * ease_progress
        
        # 添加随机抖动
        jitter_x = random.randint(-2, 2)
        jitter_y = random.randint(-1, 1)
        
        page.mouse.move(target_x + jitter_x, target_y + jitter_y)
        time.sleep(duration / steps)
    
    # 释放鼠标
    page.mouse.move(end_x, end_y)
    page.mouse.up()
```

## 故障排除

| 问题 | 原因 | 解决 |
|------|------|------|
| 滑块拖动失败 | 选择器错误 | 检查选择器是否正确 |
| 拖动后无反应 | 距离不够 | 增加 `--distance` 参数 |
| 验证仍然失败 | 速度太快 | 增加 `--duration` 参数 |
| 找不到滑块 | 页面未加载 | 等待页面完全加载后再执行 |

## 最佳实践

1. **预防为主**：保持合理的搜索间隔
2. **及时处理**：发现验证码立即解决，不要等待
3. **验证结果**：解决后检查页面是否恢复正常
4. **记录日志**：记录触发验证码的频率和条件

## 相关脚本

- `slider_captcha.py` - 自动解决滑块验证码
- `search_box_v2.py` - 搜索脚本（含反爬虫检测）
- `check_antibot.py` - 检查是否为反爬虫页面（可选）
