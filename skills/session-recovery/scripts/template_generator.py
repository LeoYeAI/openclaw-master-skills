#!/usr/bin/env python3
"""
自动模板生成器
功能：根据当前项目状态，生成每日记录模板
"""

import os
from datetime import datetime
from pathlib import Path

def generate_daily_template():
    """生成每日工作记录模板"""
    
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    time_str = today.strftime("%H:%M")
    
    template = f"""# {date_str} 工作记录

**会话时间：** {date_str} {time_str} - 
**状态：** 活跃
**主要任务：** （待填写）

---

## 📋 计划任务

### 高优先级
- [ ] （待填写）
- [ ] （待填写）

### 中优先级
- [ ] （待填写）
- [ ] （待填写）

---

## ✅ 完成的任务

### 1. 任务名称
**状态：** ✅ 完成
**详情：** （待填写）
**文档：** （待填写）

---

## 🎯 关键决策

### 决策1：标题
**问题：** （问题描述）
**选择：** （做出的选择）
**理由：** （为什么这样选择）
**影响：** （对项目的影响）

---

## 📚 学到的经验

### 经验1：标题
**场景：** （什么情况下）
**发现：** （发现了什么）
**解决：** （如何解决）
**教训：** （下次记住什么）

---

## 📂 文件操作记录

### 创建的文件
- `文件名` - 说明

### 修改的文件
- `文件名` - 修改内容

### 删除的文件
- `文件名` - 删除原因

---

## 🔄 遇到的问题

### 问题1：标题
**描述：** （问题描述）
**原因：** （问题原因）
**解决：** （解决方法）
**状态：** ✅ 已解决 / ⏸️ 部分解决 / ❌ 未解决

---

## 💡 改进想法

### 短期改进
- （可以在近期实施的改进）

### 长期优化
- （需要长期规划的优化）

---

## 📊 工作统计

**本次会话：**
- ⏱️ 时长：约 X 分钟
- 📄 创建文档：X 个
- ✅ 完成任务：X 个
- 💬 发送文件：X 个

---

**下次会话重点：**
1. （优先级1）
2. （优先级2）
3. （优先级3）

---

**下次会话见！** 👋

_记住：会话结束时更新本文档_
"""
    
    return template

def main():
    # 创建 memory 目录
    memory_dir = Path("memory")
    memory_dir.mkdir(exist_ok=True)
    
    # 生成文件路径
    today = datetime.now().strftime("%Y-%m-%d")
    file_path = memory_dir / f"{today}.md"
    
    # 检查文件是否已存在
    if file_path.exists():
        print(f"⚠️  今日记录已存在: {file_path}")
        response = input("是否覆盖？(y/N): ")
        if response.lower() != 'y':
            print("❌ 取消操作")
            return
    
    # 生成并保存模板
    template = generate_daily_template()
    file_path.write_text(template, encoding='utf-8')
    
    print(f"✅ 已创建今日工作记录模板")
    print(f"📄 文件位置: {file_path}")
    print()
    print("📝 下一步：")
    print("   1. 编辑文件，填写今日工作内容")
    print("   2. 会话结束时，完成所有待填项")
    print("   3. 运行 ./scripts/update_status.sh 同步到 STATUS.md")

if __name__ == "__main__":
    main()
