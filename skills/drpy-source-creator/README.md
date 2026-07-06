# drpy视频源创建技能

## 简介

这是一个专门用于创建、调试和优化drpy视频源的OpenClaw技能。drpy源是一种用于TVBox、海阔视界、ZYPlayer等播放器的视频源格式，使用JavaScript编写，支持动态内容抓取和解析。

## 技能特点

### 🎯 实战导向
- 基于真实网站分析（皮皮影视案例）
- 提供完整的分析流程和调试方法
- 总结常见错误和解决方案

### 📚 完整文档
- **SKILL.md** - 主要技能文档，包含快速开始和实战案例
- **references/** - 详细参考文档（属性、模板、解析、排查、格式化）
- **assets/** - 实用模板文件（基础模板、MXPro示例、皮皮影视实战）
- **scripts/** - 辅助工具脚本（压缩、验证、分析）

### 🔧 实用工具
- **analyze_site.py** - 网站结构分析工具
- **validate_drpy.js** - 源格式验证工具
- **minify_drpy.js** - 代码压缩工具

## 快速开始

### 1. 分析目标网站
```bash
python scripts/analyze_site.py https://www.example.com
```

### 2. 使用基础模板
参考 `assets/basic_template.js` 创建新源

### 3. 验证源格式
```bash
node scripts/validate_drpy.js your-source.js
```

### 4. 压缩代码
```bash
node scripts/minify_drpy.js your-source.js
```

## 核心原则

### ✅ 正确的工作流程
1. **分析** - 用Python获取HTML，确认选择器存在
2. **编写** - 基于实际HTML结构编写选择器
3. **测试** - 从简到繁，逐步验证功能
4. **优化** - 添加筛选、搜索等高级功能

### ❌ 常见错误
- 直接复制参考代码，不验证选择器
- 假设所有网站结构相同
- 忽略搜索功能的验证码限制
- 使用错误的URL模板格式

## 文件结构

```
drpy-source-creator/
├── SKILL.md                    # 主要技能文档
├── README.md                   # 本文件
├── references/
│   ├── attributes.md          # 属性详解
│   ├── templates.md           # 模板继承
│   ├── parsing.md             # 解析函数
│   ├── troubleshooting.md     # 问题排查
│   └── formatting.md          # 代码格式化
├── assets/
│   ├── basic_template.js      # 基础模板
│   ├── mxpro_example.js       # MXPro示例
│   └── pitv_example.js        # 皮皮影视实战
└── scripts/
    ├── analyze_site.py        # 网站分析工具
    ├── validate_drpy.js       # 格式验证工具
    └── minify_drpy.js         # 代码压缩工具
```

## 实战案例：皮皮影视

### 分析结果
- **网站**: https://www.pitv.cc
- **模板**: 海螺模板（hl-1）
- **关键选择器**:
  - 列表容器: `.hl-vod-list`
  - 列表项: `.hl-list-item`
  - 图片: `img&&data-original`
  - 状态: `.hl-pic-text span` (不是.remarks)
- **搜索**: 需要验证码，禁用

### 配置要点
```javascript
var rule = {
  title: '皮皮影视',
  host: 'https://www.pitv.cc',
  url: '/show/fyclassfyfilter/page/fypage/',
  searchable: 0,  // 搜索需要验证码
  
  // 关键修正：.remarks改为.hl-pic-text span
  推荐: '.hl-vod-list;li;a&&title;a&&data-original;.hl-pic-text span&&Text;a&&href',
  一级: '.hl-vod-list&&.hl-list-item;a&&title;a&&data-original;.hl-pic-text span&&Text;a&&href',
  
  // 二级选择器使用实际存在的class
  二级: {
    title: 'h1&&Text',
    img: '.hl-lazy&&data-original',
    tabs: '.hl-plays-from&&a',
    lists: '.hl-plays-list:eq(#id)&&a',
  },
}
```

## 学习路径

### 初学者
1. 阅读 `SKILL.md` 快速开始部分
2. 使用 `assets/basic_template.js` 创建简单源
3. 运行 `scripts/analyze_site.py` 分析目标网站
4. 参考 `assets/pitv_example.js` 了解实战案例

### 进阶用户
1. 阅读 `references/parsing.md` 学习高级解析技巧
2. 使用 `references/templates.md` 掌握模板继承
3. 参考 `references/troubleshooting.md` 解决复杂问题
4. 使用 `scripts/validate_drpy.js` 验证源质量

## 更新日志

### v1.0 (2026-03-17)
- 初始版本
- 添加皮皮影视实战案例
- 创建网站分析工具
- 完善问题排查文档

## 贡献

欢迎提交Issue和PR，帮助改进这个技能。

## 许可证

MIT License