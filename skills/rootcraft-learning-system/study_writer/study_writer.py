#!/usr/bin/env python3
"""
RootCraft Learning System - 学习资料自动生成器
将9步学习流程的内容自动保存为文件
"""
import os
import json
from datetime import datetime
from pathlib import Path

# 基础路径
BASE_DIR = Path("/root/.openclaw/workspace/study")


def sanitize_topic(topic: str) -> str:
    """将主题转换为安全的目录名"""
    if not topic or not topic.strip():
        raise ValueError("主题不能为空")
    
    # 移除首尾空白
    topic = topic.strip()
    
    # 拒绝保留路径段
    if topic in ('.', '..', ''):
        raise ValueError(f"无效的主题名称: {topic}")
    
    # 替换危险字符
    sanitized = topic.replace("/", "-").replace("\\", "-").replace(":", "-")
    
    # 移除开头和结尾的点（防止隐藏文件和路径遍历）
    sanitized = sanitized.strip(".")
    
    if not sanitized:
        raise ValueError(f"主题名称无效，请使用有效的目录名")
    
    return sanitized


def create_study_files(topic: str, content: dict, anki_cards: list = None) -> dict:
    """
    创建学习文件
    
    Args:
        topic: 学习主题
        content: 包含9步内容的字典
        anki_cards: Anki卡片列表（可选）
    
    Returns:
        包含各文件路径的字典
    """
    # 创建目录
    topic_dir = BASE_DIR / sanitize_topic(topic)
    
    # 解析并验证最终路径
    topic_dir = topic_dir.resolve()
    
    # 确保路径在预期目录内（防止路径遍历）
    if not str(topic_dir).startswith(str(BASE_DIR.resolve())):
        raise ValueError(f"安全错误：路径超出允许范围")
    
    topic_dir.mkdir(parents=True, exist_ok=True)
    
    # Key别名映射：用户可能使用的key → 文件需要的key
    key_aliases = {
        "goals": ["goals", "goal", "学习目标"],
        "first_principles": ["first_principles", "first_principle", "first_principles", "第一性原理", "axiom"],
        "taxonomy": ["taxonomy", "taxonomy_structure", "分类学", "知识分类", "知识体系"],
        "feynman": ["feynman", "feynman_technique", "费曼", "费曼 technique", "概念检验"],
        "recursive_questions": ["recursive_questions", "recursive", "追问", "问题链", "递归"],
        "aha_moments": ["aha_moments", "aha", "aha_moment", "领悟", "啊哈"],
        "resources": ["resources", "multi_perspective", "多视角", "学习资源", "multi_perspectives"],
        "projects": ["projects", "practice", "practice_application", "实践", "实践应用"],
        "feedback": ["feedback", "反馈", "反馈与迭代", "常见问题"],
        "review": ["review", "复习", "持续复习", "复习计划", "复习"],
        "mindmap": ["mindmap", "思维导图", "知识图谱"],
    }
    
    def get_content_for_file(file_key):
        """根据文件需要的key，获取用户提供的对应内容"""
        # 先直接尝试
        if file_key in content and content[file_key]:
            return content[file_key]
        
        # 尝试别名映射
        aliases = key_aliases.get(file_key, [file_key])
        for alias in aliases:
            if alias in content and content[alias]:
                return content[alias]
        
        # 返回空使用默认（稍后增强）
        return None
    
    files = {
        "01-goals.md": get_content_for_file("goals") or "# 学习目标\n\n## 目标设定\n- 请填写您的学习目标\n\n## 评估标准\n- [ ] 理解基本概念\n- [ ] 掌握核心技能\n- [ ] 能够实践应用\n",
        "02-first-principles.md": get_content_for_file("first_principles") or "# 第一性原理\n\n## 核心定义\n本主题的本质是什么？\n\n## 基本公理\n### 公理1\n（填写）\n\n### 公理2\n（填写）\n\n## 关键洞察\n> 核心领悟：\n",
        "03-taxonomy.md": get_content_for_file("taxonomy") or "# 知识分类体系\n\n## 基础层\n- 核心概念\n- 基础知识\n- 术语体系\n\n## 核心层\n- 核心知识\n- 技术方法\n- 工具生态\n\n## 应用层\n- 实践场景\n- 行业应用\n- 项目案例\n\n## 进阶层\n- 前沿趋势\n- 扩展知识\n- 深度研究\n",
        "04-feynman.md": get_content_for_file("feynman") or "# 费曼 Technique\n\n## 核心概念解释\n### 概念1\n- 一句话定义：\n- 核心要点：\n- 举例说明：\n\n### 概念2\n- 一句话定义：\n- 核心要点：\n\n## 递归追问\n- Q1: 最根本的原因是什么？\n- Q2: 还有更基础的吗？\n\n## Aha Moment\n记录你的领悟时刻：\n",
        "04b-recursive-questions.md": get_content_for_file("recursive_questions") or "# 递归追问链\n\n## 为什么系列\n\n### 为什么要学这个？\n答：因为[填写核心原因]\n\n### 为什么这个重要？\n答：因为[填写重要性]\n\n## 问题树\n\n### 第一层（表面问题）\n- Q1: 这个技术的核心是什么？\n- Q2: 它解决什么问题？\n\n### 第二层（原因）\n- Q1a: 为什么会这样？\n- Q1b: 根本原因是什么？\n\n### 第三层（本质）\n- 终极问题：这个领域最基础的原理是什么？\n\n## 连续追问示例\n问：为什么要学Python？\n答：因为Python很流行。\n问：为什么Python流行？\n答：因为简单易学。\n问：为什么简单易学就能流行？\n答：因为降低了编程门槛...\n",
        "04c-aha-moments.md": get_content_for_file("aha_moments") or "# Aha Moment 领悟记录\n\n## 什么是Aha Moment？\n> 茅塞顿开、豁然开朗的瞬间\n\n---\n\n## 我的领悟记录\n\n### 领悟1：\n**时间**：[填写日期]\n**问题**：[之前疑惑的问题]\n**领悟**：[突然明白的那一刻]\n**价值**：[这个领悟有什么帮助]\n\n### 领悟2：\n**时间**：[填写日期]\n**问题**：[之前疑惑的问题]\n**领悟**：[突然明白的那一刻]\n**价值**：[这个领悟有什么帮助]\n\n---\n\n## 常见Aha Moment类型\n1. **概念突破**：某个模糊的概念突然清晰\n2. **关联打通**：发现两个不相关概念的内在联系\n3. **本质看穿**：看到背后的简单\n4. **融会贯通**：多个知识点串联成线\n\n## 如何触发更多Aha Moment\n- 带着问题学习\n- 定期回顾和思考\n- 尝试解释给他人听\n- 跨领域学习\n",
        "05-resources.md": get_content_for_file("resources") or "# 多视角学习\n\n## 技术视角\n- 技术原理：\n- 实现方法：\n- 优缺点：\n\n## 应用视角\n- 实际应用场景：\n- 行业案例：\n\n## 历史视角\n- 发展历程：\n- 关键里程碑：\n\n## 哲学视角\n- 思维方式：\n- 底层逻辑：\n",
        "06-projects.md": get_content_for_file("projects") or "# 实践应用\n\n## 最小可运行方案\n### 环境准备\n```bash\n# 安装依赖\n```\n\n### 核心代码示例\n```python\n# 示例代码\ndef main():\n    pass\n```\n\n## 实战项目\n### 项目1\n- 目标：\n- 步骤：\n- 成果：\n\n### 项目2\n- 目标：\n- 步骤：\n- 成果：\n\n## 工具推荐\n| 工具 | 用途 |\n|------|------|\n| | |\n",
        "07-feedback.md": get_content_for_file("feedback") or "# 反馈与迭代\n\n## 学习记录\n### 第一次学习\n- 学习内容：\n- 理解程度：\n- 遇到的问题：\n\n### 第二次学习\n- 学习内容：\n- 理解程度：\n- 解决的问题：\n\n## 常见问题\nQ: \nA: \n\n## 迭代计划\n- [ ] 问题1\n- [ ] 问题2\n",
        "08-review.md": get_content_for_file("review") or "# 复习计划\n\n## 艾宾浩斯遗忘曲线复习表\n\n### 第一轮\n| 次数 | 时间点 | 内容 |\n|------|--------|------|\n| 1 | 10分钟 | 核心概念速回顾 |\n| 2 | 1天后 | 基础知识点 |\n| 3 | 3天后 | 进阶知识 |\n\n### 第二轮\n| 次数 | 时间点 | 内容 |\n|------|--------|------|\n| 4 | 7天后 | 整体串联 |\n| 5 | 14天后 | 重点强化 |\n| 6 | 30天后 | 全面复盘 |\n\n## 记忆技巧\n1. 联想记忆\n2. 间隔重复\n3. 主动回忆\n",
        "09-mindmap.md": get_content_for_file("mindmap") or "# 思维导图\n\n## 中心主题\n[主题名称]\n\n## 一级分支\n\n### 分支1：基础概念\n- 概念1.1\n- 概念1.2\n- 概念1.3\n\n### 分支2：核心知识\n- 知识点2.1\n- 知识点2.2\n- 知识点2.3\n\n### 分支3：技术方法\n- 方法3.1\n- 方法3.2\n- 方法3.3\n\n### 分支4：实践应用\n- 应用4.1\n- 应用4.2\n- 应用4.3\n\n## 关键连接\n- 连接1：\n- 连接2：\n\n## 核心要点\n1. 最重要的概念：\n2. 最重要的方法：\n3. 最重要的应用：\n",
    }
    
    saved_files = {}
    
    # 写入学习文件
    for filename, file_content in files.items():
        filepath = topic_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(file_content)
        saved_files[filename] = str(filepath)
    
    # 生成Anki卡片
    if anki_cards:
        import csv
        anki_file = topic_dir / "anki_cards.csv"
        with open(anki_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["front", "back", "tags"])
            for card in anki_cards:
                writer.writerow([card.get("front", ""), card.get("back", ""), ";".join(card.get("tags", []))])
        saved_files["anki_cards.csv"] = str(anki_file)
    
    return saved_files


def generate_default_content(topic: str) -> dict:
    """生成默认的学习内容模板"""
    
    return {
        "goals": f"""# 学习目标与评估标准

## 学习目标

掌握{topic}的核心知识和实践技能

## 评估标准

- [ ] 理解基本概念和原理
- [ ] 掌握核心知识点
- [ ] 能够进行实践应用
- [ ] 可以独立解决问题

## 时间规划

- 基础概念：30分钟
- 深入学习：1小时  
- 实战项目：2小时
- 总计：约3-4小时
""",
        
        "first_principles": f"""# 第一性原理分析

## 核心定义

{topic}的本质是什么？

## 本质问题

### 核心是什么？
（回答最基本的问题）

### 为什么重要？
（回答价值问题）

### 基础元素有哪些？
（回答组成问题）

## 核心公式/原理

```
（这里放核心公式）
```

## 关键洞察

> 一句话总结核心领悟
""",
        
        "taxonomy": f"""# 知识分类体系（MECE）

```
{topic}
├── 基础概念
│   ├── 概念1
│   └── 概念2
│
├── 核心知识
│   ├── 知识1
│   └── 知识2
│
├── 技术方法
│   ├── 方法1
│   └── 方法2
│
└── 实践应用
    ├── 应用1
    └── 应用2
```

## MECE检查

- 覆盖度：✓ 
- 独立度：✓
""",
        
        "feynman": f"""# 费曼 Technique

## 核心概念解释

### 什么是{topic}？
> 用一句话简单解释（像对5岁孩子说话）

## 检验清单

- [ ] 能用一句话解释核心概念
- [ ] 能举出日常生活中的例子
- [ ] 能回答基础追问

## 常见问题

**Q: {topic}的难点在哪？**
A: （回答）

**Q: 入门需要什么基础？**
A: （回答）
""",
        
        "recursive_questions": f"""# 递归追问链

## 追问链

```
Q: {topic}是什么？
A: 

Q: 为什么要学{topic}？
A: 

Q: {topic}的核心是什么？
A: 

Q: 如何应用{topic}？
A: 

Q: 进阶路径是什么？
A: 
```
""",
        
        "aha_moments": f"""# Aha Moment 记录

> 在学习过程中，记录每一个"啊哈"时刻

## 记录格式

```
## [日期] 领悟标题

### 问题
（之前不理解的点）

### 领悟
（突然明白的那一刻）

### 关联
（这个领悟让我联想到什么）
```

---

## 开始记录

在这里写下你的Aha Moment：
""",
        
        "resources": f"""# 学习资源

## 文档/教程

- 资源1
- 资源2

## 工具

| 工具 | 用途 | 链接 |
|------|------|------|
| 工具1 | 用途1 | 链接 |
| 工具2 | 用途2 | 链接 |

## 推荐项目

- 项目1
- 项目2
""",
        
        "projects": f"""# 实践项目

## 项目1：基础示例

```python
# 代码示例
```

## 项目2：进阶实践

```python
# 代码示例
```

## 进阶挑战

- [ ] 挑战1
- [ ] 挑战2
""",
        
        "feedback": f"""# 反馈与迭代

## 学习记录

### 第1次学习
- **内容**：
- **收获**：
- **问题**：

## 迭代计划

- [ ] 待完成项1
- [ ] 待完成项2
""",
        
        "review": f"""# 复习计划（艾宾浩斯遗忘曲线）

## 复习时间表

| 次数 | 时间点 | 内容 |
|------|--------|------|
| 第1次 | 10分钟后 | 核心概念速回顾 |
| 第2次 | 1天后 | 基础知识点 |
| 第3次 | 3天后 | 进阶知识 |
| 第4次 | 7天后 | 实践应用 |
| 第5次 | 14天后 | 整体串联 |
| 第6次 | 30天后 | 总结复盘 |

## 复习要点

### 第1次复习
- [ ] 核心概念

### 第2次复习
- [ ] 基础知识点

## 复习提示

可以使用Anki卡片辅助记忆
""",
        
        "mindmap": f"""# 思维导图

## {topic} 知识图谱

```
                    ┌─────────────────────┐
                    │  {topic}           │
                    └──────────┬──────────┘
                               │
      ┌────────────────────────┼────────────────────────┐
      │                        │                        │
      ▼                        ▼                        ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  基础概念     │    │  核心知识       │    │  实践应用       │
├───────────────┤    ├─────────────────┤    ├─────────────────┤
│• 概念1       │    │• 知识1         │    │• 应用1         │
│• 概念2       │    │• 知识2         │    │• 应用2         │
└───────────────┘    └─────────────────┘    └─────────────────┘
```

## 关键连接

（描述知识点之间的联系）

## 核心思维

> 一句话总结核心思维
"""
    }


def generate_and_save(topic: str, content: dict = None, anki_cards: list = None) -> dict:
    """
    主函数：生成学习资料并保存
    
    Args:
        topic: 学习主题
        content: 自定义内容（可选）
        anki_cards: 自定义Anki卡片（可选）
    
    Returns:
        包含各文件路径的字典
    """
    if content is None:
        content = generate_default_content(topic)
    
    if anki_cards is None:
        anki_cards = generate_default_anki_cards(topic)
    
    saved = create_study_files(topic, content, anki_cards)
    return saved


def generate_default_anki_cards(topic: str) -> list:
    """生成默认的Anki卡片模板"""
    return [
        {
            "front": f"什么是{topic}？",
            "back": "（请填写核心定义）",
            "tags": ["rootcraft", "concept", topic]
        },
        {
            "front": f"{topic}的核心要点是什么？",
            "back": "（请填写核心要点）",
            "tags": ["rootcraft", "keypoint", topic]
        },
        {
            "front": f"{topic}的一个例子？",
            "back": "（请填写例子）",
            "tags": ["rootcraft", "example", topic]
        },
        {
            "front": f"为什么要学习{topic}？",
            "back": "（请填写原因）",
            "tags": ["rootcraft", "why", topic]
        },
        {
            "front": f"{topic}的应用场景？",
            "back": "（请填写应用场景）",
            "tags": ["rootcraft", "application", topic]
        }
    ]


if __name__ == "__main__":
    # 测试
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else "测试主题"
    path = generate_and_save(topic)
    print(f"✅ 已生成学习资料: {path}")


# ============================================================
# 质检模块 v1.1.1
# ============================================================

def quality_check(topic: str) -> dict:
    """
    质检模块：检查学习流程是否完整输出所有文件
    
    Args:
        topic: 学习主题
        
    Returns:
        质检报告字典
    """
    topic_dir = BASE_DIR / sanitize_topic(topic)
    topic_dir = topic_dir.resolve()
    
    # v1.1.1 要求的12个文件
    required_files = [
        ('01-goals.md', '学习目标'),
        ('02-first-principles.md', '第一性原理'),
        ('03-taxonomy.md', '分类学拆解'),
        ('04-feynman.md', '费曼+追问'),
        ('05-multi-perspective.md', '多视角学习'),  # 或 05-resources.md
        ('06-projects.md', '实践应用'),
        ('07-feedback.md', '反馈与迭代'),
        ('08-review.md', '持续复习'),
        ('08-exam.md', '试卷文件'),  # 新增
        ('09-mindmap.md', '思维导图'),
        ('04c-aha-moments.md', 'Aha Moment'),
        ('anki_cards.csv', 'Anki卡片'),
    ]
    
    check_results = []
    all_passed = True
    
    for filename, description in required_files:
        filepath = topic_dir / filename
        if filepath.exists():
            check_results.append({
                'file': filename,
                'description': description,
                'status': '✅',
                'path': str(filepath)
            })
        else:
            # 检查可能的替代文件名
            alternatives = {
                '05-multi-perspective.md': ['05-resources.md'],
            }
            found = False
            if filename in alternatives:
                for alt in alternatives[filename]:
                    alt_path = topic_dir / alt
                    if alt_path.exists():
                        check_results.append({
                            'file': alt,
                            'description': description,
                            'status': '✅',
                            'path': str(alt_path),
                            'note': f'替代文件: {filename}'
                        })
                        found = True
                        break
            
            if not found:
                check_results.append({
                    'file': filename,
                    'description': description,
                    'status': '❌',
                    'path': None
                })
                all_passed = False
    
    return {
        'topic': topic,
        'topic_dir': str(topic_dir),
        'all_passed': all_passed,
        'total': len(required_files),
        'passed': sum(1 for r in check_results if r['status'] == '✅'),
        'failed': sum(1 for r in check_results if r['status'] == '❌'),
        'results': check_results
    }


def print_quality_report(qc_result: dict):
    """打印质检报告"""
    print("\n" + "=" * 50)
    print("        📋 质检报告")
    print("=" * 50)
    print(f"主题: {qc_result['topic']}")
    print(f"目录: {qc_result['topic_dir']}")
    print("-" * 50)
    
    for r in qc_result['results']:
        status_icon = r['status']
        note = f" ({r.get('note', '')})" if r.get('note') else ""
        print(f"{status_icon} {r['description']}: {r['file']}{note}")
    
    print("-" * 50)
    print(f"📊 总计: {qc_result['passed']}/{qc_result['total']} 通过")
    
    if qc_result['all_passed']:
        print("✅ 质检通过！学习流程完整")
    else:
        print(f"⚠️ 质检未通过！缺少 {qc_result['failed']} 个文件")
    
    print("=" * 50)
    return qc_result


# ============================================================
# 试卷生成模块 v1.1.1
# ============================================================

import re

def generate_exam_paper(topic: str, content: dict = None) -> str:
    """
    生成试卷文件
    
    Args:
        topic: 学习主题
        content: 可选的自定义内容，用于生成更具针对性的题目
        
    Returns:
        试卷内容字符串
    """
    # 从内容中提取关键概念
    key_concepts = []
    if content:
        # 提取标题和列表项
        for key in ['first_principles', 'taxonomy', 'feynman', 'goals']:
            if key in content:
                # 提取 ## 后的标题
                titles = re.findall(r'##?\s*([^#\n]+)', content[key])
                key_concepts.extend([t.strip() for t in titles[:2]])
                # 提取列表项
                items = re.findall(r'^[-|*]\s*([^#\n]+)', content[key], re.MULTILINE)
                key_concepts.extend([i.strip()[:30] for i in items[:3]])
    
    # 去重并清理
    key_concepts = [k for k in key_concepts if k and len(k) > 2][:8]
    
    if not key_concepts:
        key_concepts = [f"{topic}的核心知识", "第一性原理", "费曼 Technique", "艾宾浩斯遗忘曲线"]
    
    # 选择题选项
    q_options = [
        "大量可理解输入 + 有效输出",
        "死记硬背单词和语法规则", 
        "只看中文翻译学英语",
        "只做选择题不开口",
    ]
    
    # 生成试卷
    exam_content = f"""# {topic} - 试卷

**考试说明**：
- 本试卷包含4种题型，共10-12道题
- 建议考试时间：60分钟
- 满分：100分

---

## 一、选择题（每题4分，共20分）

1. （难度：基础）{key_concepts[0] if key_concepts else topic}的核心定义是什么？
   A. {q_options[0]}
   B. {q_options[1]}
   C. {q_options[2]}
   D. {q_options[3]}

2. （难度：基础）下列关于{topic}的描述，正确的是？
   A. {q_options[0]}
   B. {q_options[1]}
   C. {q_options[2]}
   D. {q_options[3]}

3. （难度：进阶）{topic}的第一性原理是什么？
   A. {q_options[0]}
   B. {q_options[1]}
   C. {q_options[2]}
   D. {q_options[3]}

4. （难度：进阶）在学习{topic}时最重要的是什么？
   A. {q_options[0]}
   B. {q_options[1]}
   C. {q_options[2]}
   D. {q_options[3]}

5. （难度：提高）如何应用{topic}解决实际问题？
   A. {q_options[0]}
   B. {q_options[1]}
   C. {q_options[2]}
   D. {q_options[3]}

---

## 二、填空题（每题4分，共20分）

1. {topic}的核心要素包括_____、_____、_____。

2. 第一性原理强调从_____出发思考问题。

3. 费曼 Technique 的核心是_____。

4. 艾宾浩斯遗忘曲线告诉我们_____是最重要的。

5. 学习{topic}需要经历_____个阶段。

---

## 三、简答题（每题10分，共30分）

1. 请用一句话解释什么是{topic}？

   答题要点：
   - 定义：
   - 核心：

2. 为什么第一性原理在学习中很重要？

   答题要点：
   - 本质：
   - 价值：

3. 如何将费曼 Technique 应用到{topic}的学习中？

   答题要点：
   - 步骤：
   - 目的：

---

## 四、操作/实践题（每题15分，共30分）

1. **实践应用题**：
   请设计一个最小可运行的{topic}学习方案，包含：
   - 学习目标
   - 第一性原理分析
   - 实践步骤

   
   **参考答案**：
   （请根据实际情况填写）

2. **迁移应用题**：
   假设你要向一个完全不懂{topic}的人解释这个概念，请用费曼 Technique 写出你的讲解稿（至少200字）。

   
   **写作提示**：
   - 用简单的语言
   - 避免专业术语
   - 善用类比

---

## 参考答案

### 一、选择题
1. B | 2. C | 3. A | 4. D | 5. B

### 二、填空题
1. 概念A、概念B、概念C
2. 本质/基本事实
3. 用简单语言解释复杂概念
4. 及时复习
5. 9

### 三、简答题
（开放性问题，言之有理即可）

### 四、操作/实践题
（开放性题目，请根据实际情况作答）

---

**试卷生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**生成工具**：RootCraft Learning System v1.1.1
"""
    return exam_content


def save_exam_paper(topic: str, content: dict = None) -> str:
    """
    生成并保存试卷文件
    
    Returns:
        试卷文件路径
    """
    topic_dir = BASE_DIR / sanitize_topic(topic)
    topic_dir = topic_dir.resolve()
    
    # 确保目录存在
    topic_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成试卷内容
    exam_content = generate_exam_paper(topic, content)
    
    # 保存试卷
    exam_file = topic_dir / "08-exam.md"
    with open(exam_file, "w", encoding="utf-8") as f:
        f.write(exam_content)
    
    return str(exam_file)