# AI Illustration Prompts

Prompts templates for generating PPT illustrations using nanobanana (Gemini).

## Prompt Structure

```
{主题/内容} + {风格描述} + {颜色/配色} + {构图/布局} + {用途说明}
```

---

## Cover Page Prompts

### Technology/Digital Theme

```
数字化科技背景图，抽象数据流动效果，深蓝色渐变主色调，
现代化智慧城市轮廓，几何图形装饰，简洁专业，
适合PPT封面，16:9横幅，扁平化设计风格
```

### Business/Corporate Theme

```
商务专业背景图，现代办公楼与城市天际线，
蓝色主色调，简洁大气，企业风格，
适合PPT封面，16:9横幅，摄影风格
```

### Industry/Engineering Theme

```
工程建设行业背景图，现代化基础设施，
蓝色科技感，城市道路与桥梁，专业商务风格，
适合PPT封面，16:9横幅，扁平化设计
```

---

## Content Page Prompts

### Concept Illustration

```
{主题}概念插图，{具体描述}，
扁平化设计风格，{主色调}主色调，
简洁专业，适合PPT内容页，16:9横幅
```

### Process/Flow Diagram Style

```
{流程名称}流程概念图，简洁扁平风格，
{主色调}主色调，箭头和连接线，
现代化设计，适合PPT内容页，16:9横幅
```

### Team/People Illustration

```
团队协作概念图，专业人员工作场景，
扁平化插画风格，{主色调}配色，
简洁现代，适合PPT内容页，16:9横幅
```

---

## Data Page Prompts

### Data Visualization

```
数据分析可视化概念图，图表和仪表盘元素，
科技感设计，{主色调}配色，
简洁现代，适合PPT数据展示页，16:9横幅
```

### Charts & Metrics

```
数据指标展示概念图，简洁图表设计，
{主色调}渐变色，现代商务风格，
适合PPT数据页，16:9横幅，扁平化设计
```

---

## Summary Page Prompts

### Success/Achievement

```
成功成就概念图，积极向上的视觉元素，
{主色调}配色，简洁专业，
适合PPT总结页，16:9横幅，扁平化风格
```

### Future/Vision

```
未来愿景概念图，科技感城市或抽象图形，
{主色调}渐变，现代化设计，
适合PPT愿景页，16:9横幅，简洁专业
```

---

## End Page Prompts

### Thank You

```
感谢致谢背景图，简洁优雅，
{主色调}渐变，几何装饰元素，
适合PPT结束页，16:9横幅，极简风格
```

### Contact/Closing

```
商务结束页背景，简洁专业，
{主色调}主色调，几何图形装饰，
适合PPT结束页，16:9横幅，现代风格
```

---

## Style Adaptation

### Color Mapping

| Hex Color | Chinese Description | English Description |
|-----------|---------------------|---------------------|
| `#003366` | 深蓝色、海军蓝 | deep blue, navy |
| `#3366CC` | 蓝色 | blue |
| `#1E3A8A` | 深蓝色 | dark blue |
| `#22C55E` | 绿色 | green |
| `#F97316` | 橙色 | orange |
| `#EF4444` | 红色 | red |
| `#8B5CF6` | 紫色 | purple |
| `#FFFFFF` | 白色 | white |
| `#F3F4F6` | 浅灰色 | light gray |

### Style Keywords by Industry

| Industry | Style Keywords |
|----------|----------------|
| 科技/互联网 | 科技感、数字化、现代、简洁、几何 |
| 金融/银行 | 专业、稳重、商务、蓝色系 |
| 政府/公共 | 正式、权威、深蓝色、简洁 |
| 教育/培训 | 清新、友好、活力、多彩 |
| 医疗/健康 | 干净、专业、绿色/蓝色、简洁 |
| 制造/工业 | 工业风、专业、蓝色、技术感 |

---

## Example Prompts by Slide Type

### Slide 1: Cover - "Digital Road Project"

```
智慧道路数字化概念背景图，现代化城市道路俯视图，
数据流线条和连接点，深蓝色渐变主色调，
科技感设计，简洁专业，适合PPT封面，16:9横幅
```

### Slide 3: Content - "Project Overview"

```
项目概述概念图，城市基础设施鸟瞰图，
简洁扁平化设计，蓝色主色调，
现代化城市道路，适合PPT内容页，16:9横幅
```

### Slide 6: Data - "Evaluation Results"

```
评估结果数据展示概念图，仪表盘和图表元素，
科技感设计，蓝色渐变配色，
简洁现代，适合PPT数据页，16:9横幅
```

### Slide 10: Summary - "Project Achievements"

```
项目成果展示概念图，成功里程碑元素，
深蓝色主色调，积极向上，
简洁专业，适合PPT总结页，16:9横幅
```

---

## Prompt Generation Function

```javascript
function generateImagePrompt(slideInfo, styleColors, industry) {
  const colorWord = colorMapping[styleColors.primary] || "蓝色";
  const styleWords = industryStyles[industry] || "专业,简洁";
  
  const templates = {
    cover: `${slideInfo.topic}概念背景图，现代化${industry}场景，${colorWord}渐变主色调，${styleWords}，适合PPT封面，16:9横幅`,
    
    content: `${slideInfo.topic}概念插图，${slideInfo.description}，扁平化设计，${colorWord}主色调，适合PPT内容页，16:9横幅`,
    
    data: `${slideInfo.topic}数据展示概念图，图表和仪表盘，科技感设计，${colorWord}配色，适合PPT数据页，16:9横幅`,
    
    summary: `${slideInfo.topic}成果展示概念图，积极向上，${colorWord}主色调，简洁专业，适合PPT总结页，16:9横幅`,
    
    end: `感谢致谢背景图，简洁优雅，${colorWord}渐变，适合PPT结束页，16:9横幅`
  };
  
  return templates[slideInfo.type] || templates.content;
}
```

---

## Best Practices

1. **保持简洁**：提示词不要太长，重点突出
2. **指定风格**：扁平化、摄影风格、插画风格等
3. **明确颜色**：使用主色调描述
4. **固定比例**：始终使用 `16:9横幅` 确保适合 PPT
5. **避免文字**：AI 生成的文字通常不准确，配图应避免文字元素
6. **风格一致**：整个 PPT 的配图应保持风格统一