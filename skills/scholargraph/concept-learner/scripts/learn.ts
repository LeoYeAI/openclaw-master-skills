/**
 * Concept Learner - Core Module
 * 概念学习核心模块
 *
 * 帮助用户快速构建知识框架：
 * - 概念定义与解释
 * - 核心组成要素
 * - 历史演进
 * - 应用场景
 * - 相关概念
 * - 学习路径
 */

import { createAIProvider, type AIProvider } from '../../shared/ai-provider';
import { extractJson } from '../../shared/utils';
import { ApiInitializationError, getErrorMessage } from '../../shared/errors';
import type { WebSearchResultItem } from '../../shared/types';
import type { LearnOptions, ConceptCard, ComparisonResult, LearningPathPlan, Paper, CodeExample } from './types';

export default class ConceptLearner {
  private ai: AIProvider | null = null;

  async initialize(): Promise<void> {
    if (!this.ai) {
      try {
        this.ai = await createAIProvider();
      } catch (error) {
        throw new ApiInitializationError(
          `Failed to initialize AI provider: ${getErrorMessage(error)}`,
          error instanceof Error ? error : undefined
        );
      }
    }
  }

  /**
   * 学习一个概念
   */
  async learn(concept: string, options: LearnOptions = {}): Promise<ConceptCard> {
    await this.initialize();

    const {
      depth = 'intermediate',
      includePapers = true,
      includeCode = false,
      language = 'zh-CN',
      focusAreas
    } = options;

    // 获取概念基础信息
    const basicInfo = await this.fetchConceptBasics(concept, language);

    // 获取相关论文
    let keyPapers: Paper[] = [];
    if (includePapers) {
      keyPapers = await this.fetchKeyPapers(concept);
    }

    // 获取代码示例
    let codeExamples: CodeExample[] = [];
    if (includeCode) {
      codeExamples = await this.fetchCodeExamples(concept);
    }

    // 生成学习路径
    const learningPath = await this.generateLearningPath(concept, depth, language);

    // 组装概念卡片
    const card: ConceptCard = {
      concept,
      ...basicInfo,
      learningPath,
      keyPapers,
      codeExamples,
      generatedAt: new Date().toISOString()
    };

    return card;
  }

  /**
   * 获取概念基础信息
   */
  private async fetchConceptBasics(concept: string, language: string): Promise<Partial<ConceptCard>> {
    const langPrompt = language === 'zh-CN'
      ? '请用中文回答'
      : 'Please answer in English';

    const prompt = `${langPrompt}

请为概念"${concept}"生成一份详细的知识卡片，包含以下内容：

1. **定义**: 给出清晰的定义，包括一句话简洁解释
2. **核心组成**: 列出3-5个核心组成部分，每个说明其作用和重要性
3. **历史演进**: 说明概念的起源、关键发展节点、当前状态
4. **应用场景**: 列出主要应用领域和具体案例
5. **相关概念**: 列出相关概念，区分前置知识、相关知识、衍生概念、替代方案

请以JSON格式返回，结构如下：
{
  "definition": "详细定义",
  "shortExplanation": "一句话解释",
  "coreComponents": [
    {"name": "组成名称", "description": "描述", "importance": "high|medium|low"}
  ],
  "history": {
    "origin": "起源背景",
    "keyDevelopments": [
      {"year": "年份", "event": "事件", "significance": "意义"}
    ],
    "currentStatus": "当前状态"
  },
  "applications": [
    {"domain": "领域", "examples": ["案例1", "案例2"], "impact": "影响"}
  ],
  "relatedConcepts": [
    {"concept": "概念名", "relationship": "prerequisite|related|derived|alternative", "briefExplanation": "简要说明"}
  ],
  "resources": [
    {"type": "paper|tutorial|course|book|code", "title": "标题", "url": "链接", "description": "描述", "difficulty": "beginner|intermediate|advanced"}
  ]
}`;

    const responseText = await this.ai!.chat([
      { role: 'system', content: '你是一位知识结构化专家，擅长将复杂概念转化为清晰的学习框架。' },
      { role: 'user', content: prompt }
    ], { temperature: 0.3 });

    // 使用改进的 JSON 提取
    const result = extractJson<Partial<ConceptCard>>(responseText);

    if (result.success && result.data) {
      return result.data;
    }

    console.error('Failed to parse concept response:', result.error);
    return {
      definition: responseText,
      shortExplanation: '',
      coreComponents: [],
      history: { origin: '', keyDevelopments: [], currentStatus: '' },
      applications: [],
      relatedConcepts: [],
      resources: []
    };
  }

  /**
   * 获取关键论文
   */
  private async fetchKeyPapers(concept: string): Promise<Paper[]> {
    try {
      // 优先使用 Semantic Scholar API
      const papers = await this.searchSemanticScholar(concept);
      if (papers.length > 0) {
        return papers;
      }

      // 回退到 web search（如果可用）
      if (this.ai!.webSearch) {
        const results: WebSearchResultItem[] = await this.ai!.webSearch(
          `${concept} paper arxiv research`,
          5
        );

        return results.slice(0, 5).map((item) => ({
          title: item.name,
          authors: [],
          year: item.date?.split('-')[0] || '',
          url: item.url,
          summary: item.snippet || ''
        }));
      }

      console.warn('No paper search method available');
      return [];
    } catch (error) {
      console.error('Failed to fetch papers:', getErrorMessage(error));
      return [];
    }
  }

  /**
   * 从 Semantic Scholar 搜索论文
   */
  private async searchSemanticScholar(concept: string): Promise<Paper[]> {
    try {
      const fields = 'paperId,title,abstract,authors,year,citationCount,venue,url';
      const url = `https://api.semanticscholar.org/graph/v1/paper/search?query=${encodeURIComponent(concept)}&limit=5&fields=${fields}`;

      const response = await fetch(url);
      if (!response.ok) {
        console.warn(`Semantic Scholar API error: ${response.status}`);
        return [];
      }

      const data = await response.json() as {
        data?: Array<{
          paperId: string;
          title: string;
          abstract?: string;
          authors?: Array<{ name: string }>;
          year?: number;
          citationCount?: number;
          venue?: string;
          url?: string;
        }>;
      };

      if (!data.data) return [];

      return data.data.map(paper => ({
        title: paper.title,
        authors: paper.authors?.map(a => a.name) || [],
        year: paper.year?.toString() || '',
        url: paper.url || `https://www.semanticscholar.org/paper/${paper.paperId}`,
        summary: paper.abstract?.substring(0, 200) + '...' || ''
      }));
    } catch (error) {
      console.error('Semantic Scholar search error:', getErrorMessage(error));
      return [];
    }
  }

  /**
   * 获取代码示例
   */
  private async fetchCodeExamples(concept: string): Promise<CodeExample[]> {
    const prompt = `为概念"${concept}"生成1-2个简洁的代码示例，帮助理解其实现原理。

返回JSON格式：
{
  "examples": [
    {
      "title": "示例标题",
      "description": "说明这个示例展示什么",
      "language": "python|javascript|etc",
      "code": "代码内容"
    }
  ]
}`;

    try {
      const responseText = await this.ai!.chat([
        { role: 'system', content: '你是一位代码教学专家，擅长用简洁的代码说明复杂概念。' },
        { role: 'user', content: prompt }
      ], { temperature: 0.2 });

      const result = extractJson<{ examples?: CodeExample[] }>(responseText);

      if (result.success && result.data?.examples) {
        return result.data.examples;
      }
    } catch (error) {
      console.error('Failed to generate code examples:', getErrorMessage(error));
    }

    return [];
  }

  /**
   * 生成学习路径
   */
  private async generateLearningPath(
    concept: string,
    depth: string,
    language: string
  ): Promise<ConceptCard['learningPath']> {
    const langPrompt = language === 'zh-CN' ? '请用中文回答' : 'Please answer in English';

    const prompt = `${langPrompt}

为学习"${concept}"设计一条从入门到${depth === 'advanced' ? '精通' : '进阶'}的学习路径。

返回JSON格式：
{
  "stages": [
    {
      "stage": "阶段名称（如：基础概念）",
      "concepts": ["需要学习的概念1", "概念2"],
      "estimatedTime": "预计时间",
      "resources": ["推荐资源1", "资源2"]
    }
  ]
}`;

    try {
      const responseText = await this.ai!.chat([
        { role: 'system', content: '你是一位学习路径规划专家。' },
        { role: 'user', content: prompt }
      ], { temperature: 0.3 });

      const result = extractJson<{ stages?: ConceptCard['learningPath'] }>(responseText);

      if (result.success && result.data?.stages) {
        return result.data.stages;
      }
    } catch (error) {
      console.error('Failed to generate learning path:', getErrorMessage(error));
    }

    return [];
  }

  /**
   * 对比两个概念
   */
  async compare(concept1: string, concept2: string, language: string = 'zh-CN'): Promise<ComparisonResult> {
    await this.initialize();

    const langPrompt = language === 'zh-CN' ? '请用中文回答' : 'Please answer in English';

    const prompt = `${langPrompt}

对比分析"${concept1}"和"${concept2}"两个概念：

返回JSON格式：
{
  "similarities": ["相似点1", "相似点2"],
  "differences": ["差异点1", "差异点2"],
  "useCases": {
    "preferConcept1": ["适合使用${concept1}的场景"],
    "preferConcept2": ["适合使用${concept2}的场景"]
  }
}`;

    const responseText = await this.ai!.chat([
      { role: 'system', content: '你是一位技术对比分析专家。' },
      { role: 'user', content: prompt }
    ], { temperature: 0.2 });

    const result = extractJson<{
      similarities?: string[];
      differences?: string[];
      useCases?: { preferConcept1?: string[]; preferConcept2?: string[] };
    }>(responseText);

    if (result.success && result.data) {
      return {
        concept1,
        concept2,
        similarities: result.data.similarities || [],
        differences: result.data.differences || [],
        useCases: {
          preferConcept1: result.data.useCases?.preferConcept1 || [],
          preferConcept2: result.data.useCases?.preferConcept2 || []
        }
      };
    }

    return {
      concept1,
      concept2,
      similarities: [],
      differences: [],
      useCases: { preferConcept1: [], preferConcept2: [] }
    };
  }

  /**
   * 规划学习路径
   */
  async planLearningPath(
    topic: string,
    options: {
      currentLevel: string;
      targetLevel: string;
      timeCommitment: string;
    }
  ): Promise<LearningPathPlan> {
    await this.initialize();

    const { currentLevel, targetLevel, timeCommitment } = options;

    const prompt = `为学习主题"${topic}"规划学习路径：

当前水平：${currentLevel}
目标水平：${targetLevel}
可用时间：${timeCommitment}

返回JSON格式：
{
  "topic": "${topic}",
  "currentLevel": "${currentLevel}",
  "targetLevel": "${targetLevel}",
  "estimatedDuration": "总预计时长",
  "stages": [
    {
      "stage": "阶段名",
      "concepts": ["概念"],
      "estimatedTime": "时间",
      "resources": ["资源"]
    }
  ],
  "milestones": ["里程碑1", "里程碑2"],
  "recommendedOrder": ["建议学习顺序"]
}`;

    const responseText = await this.ai!.chat([
      { role: 'system', content: '你是一位学习路径规划专家。' },
      { role: 'user', content: prompt }
    ], { temperature: 0.3 });

    const result = extractJson<LearningPathPlan>(responseText);

    if (result.success && result.data) {
      return result.data;
    }

    return {
      topic,
      currentLevel,
      targetLevel,
      estimatedDuration: '',
      stages: [],
      milestones: [],
      recommendedOrder: []
    };
  }

  /**
   * 导出为Markdown
   */
  toMarkdown(card: ConceptCard): string {
    const md = `# ${card.concept} - 概念学习卡片

## 📖 定义

${card.definition}

**一句话解释**: ${card.shortExplanation}

## 🔧 核心组成

${card.coreComponents.map(c => `
### ${c.name}
${c.description}

*重要性*: ${c.importance}
`).join('\n')}

## 📜 历史演进

**起源**: ${card.history.origin}

${card.history.keyDevelopments.map(d => `
- **${d.year}**: ${d.event} - ${d.significance}
`).join('\n')}

**当前状态**: ${card.history.currentStatus}

## 🎯 应用场景

${card.applications.map(a => `
### ${a.domain}
- 案例: ${a.examples.join(', ')}
- 影响: ${a.impact}
`).join('\n')}

## 🔗 相关概念

| 概念 | 关系 | 说明 |
|------|------|------|
${card.relatedConcepts.map(c => `| ${c.concept} | ${c.relationship} | ${c.briefExplanation} |`).join('\n')}

## 📚 学习路径

${card.learningPath.map((stage, i) => `
### 阶段${i + 1}: ${stage.stage}
- 学习内容: ${stage.concepts.join(', ')}
- 预计时间: ${stage.estimatedTime}
- 推荐资源: ${stage.resources.join(', ')}
`).join('\n')}

## 📄 关键论文

${card.keyPapers?.map(p => `
- [${p.title}](${p.url || '#'}) (${p.year}) - ${p.summary}
`).join('\n') || '暂无'}

${card.codeExamples && card.codeExamples.length > 0 ? `
## 💻 代码示例

${card.codeExamples.map((example, i) => `
### 示例 ${i + 1}: ${example.title}

${example.description}

\`\`\`${example.language}
${example.code}
\`\`\`
`).join('\n')}
` : ''}

---
*生成时间: ${card.generatedAt}*
`;

    return md;
  }
}

// CLI 支持
if (import.meta.main) {
  const args = process.argv.slice(2);
  const concept = args[0];

  if (!concept) {
    console.error('Usage: bun run learn.ts <concept> [--depth beginner|intermediate|advanced] [--output <file>]');
    process.exit(1);
  }

  const depthIndex = args.indexOf('--depth');
  const depth = depthIndex > -1 ? args[depthIndex + 1] as 'beginner' | 'intermediate' | 'advanced' : 'intermediate';

  const outputIndex = args.indexOf('--output');
  const outputFile = outputIndex > -1 ? args[outputIndex + 1] : null;

  const learner = new ConceptLearner();

  learner.learn(concept, { depth }).then(card => {
    if (outputFile) {
      const fs = require('fs');
      fs.writeFileSync(outputFile, learner.toMarkdown(card));
      console.log(`Concept card saved to ${outputFile}`);
    } else {
      console.log(JSON.stringify(card, null, 2));
    }
  }).catch(err => {
    console.error('Error:', getErrorMessage(err));
    process.exit(1);
  });
}
