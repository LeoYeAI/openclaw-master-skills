# article-to-infographic v2.0.0 发布包

## 文件说明
- `article-to-infographic-v2.0.0.tar.gz` - Skill 完整发布包

## 内容清单
- SKILL.md - 主技能文档（三步确认流程）
- skill.json - 元数据（版本 2.0.0）
- references/style-presets.md - 6种视觉样式预设
- references/illustrations-guide.md - 插图集成指南
- scripts/html_to_png.py - PNG 导出脚本

## ClawHub 发布命令
```bash
clawhub publish article-to-infographic-v2.0.0 \
  --slug "article-to-infographic" \
  --name "Article to Infographic" \
  --version "2.0.0" \
  --changelog "3-step workflow, Premium Magazine style, CJK optimization"
```

## 特性亮点
✅ 强制三步确认流程（大纲/风格/输出）
✅ 容错PNG导出（4种方法回退）
✅ 中文字体优化
✅ 6种视觉风格（含Premium Magazine高级风格）

生成时间: 2026-02-24
作者: 龙虾 × 麦虾
