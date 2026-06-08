/**
 * Query Expander - 查询扩展模块
 *
 * 将用户模糊的研究兴趣转化为具体的搜索关键词
 */

import { createAIProvider, type AIProvider } from '../../shared/ai-provider';
import { ApiInitializationError, getErrorMessage } from '../../shared/errors';

export interface QueryExpansionResult {
  // 确认的用户需求信息
  confirmation: {
    coreTheme?: string;        // 核心主题
    subField?: string;         // 子领域/方向
    applicationScenario?: string; // 应用场景
    timeRange?: string;        // 时间范围
    preferredSources?: string; // 偏好来源
  };

  // 生成的关键词列表
  keywords: Array<{
    term: string;              // 关键词
    description: string;       // 简短说明
    type: 'core' | 'synonym' | 'abbreviation' | 'related' | 'application'; // 关键词类型
  }>;

  // 追问问题（如果需要更多信息）
  followUpQuestions?: string[];

  // 是否需要更多信息
  needsMoreInfo: boolean;
}

export default class QueryExpander {
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
   * 扩展用户查询，生成多个搜索关键词
   */
  async expandQuery(userInput: string, context?: string): Promise<QueryExpansionResult> {
    await this.initialize();

    const systemPrompt = `你是一个专业的学术文献搜索助手 "Literature Search Prompt Engineer"。
你的任务是根据用户模糊的研究兴趣，通过分析来厘清领域，并生成多个可执行的搜索关键词。

## 工作流程

### 阶段 1：理解需求
用户给你的输入可能是模糊的，你需要分析以下信息：
1. **核心主题**：具体想研究什么？
2. **子领域/方向**：更具体的角度？
3. **应用场景**：研究目的是什么？
4. **时间范围**：需要多新的论文？
5. **偏好来源**：对某些期刊/会议有偏好吗？

### 阶段 2：生成关键词
生成关键词的策略：
- **核心词**：用户提到的核心概念
- **同义词**：常见的替换词
- **缩写**：全称和缩写都要
- **相关术语**：上下游技术、工具、框架
- **应用领域**：具体应用场景

### 输出格式
返回 JSON 格式：
{
  "confirmation": {
    "coreTheme": "核心主题",
    "subField": "子领域",
    "applicationScenario": "应用场景",
    "timeRange": "时间范围",
    "preferredSources": "偏好来源"
  },
  "keywords": [
    {
      "term": "关键词",
      "description": "说明",
      "type": "core|synonym|abbreviation|related|application"
    }
  ],
  "followUpQuestions": ["问题1", "问题2"],
  "needsMoreInfo": true/false
}`;

    const userPrompt = context
      ? `用户输入：${userInput}\n\n上下文信息：${context}\n\n请分析用户需求并生成搜索关键词。`
      : `用户输入：${userInput}\n\n请分析用户需求并生成搜索关键词。`;

    try {
      const response = await this.ai!.chat([
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ], { temperature: 0.7 });

      // 尝试解析 JSON 响应
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const result = JSON.parse(jsonMatch[0]);
        return result as QueryExpansionResult;
      }

      // 如果无法解析 JSON，返回基础结果
      return {
        confirmation: {
          coreTheme: userInput
        },
        keywords: [
          {
            term: userInput,
            description: '用户原始输入',
            type: 'core'
          }
        ],
        needsMoreInfo: true,
        followUpQuestions: [
          '你更偏向于哪个具体方向？',
          '是为了写论文、找创新点，还是为了工程应用？'
        ]
      };
    } catch (error) {
      throw new Error(`Query expansion failed: ${getErrorMessage(error)}`);
    }
  }

  /**
   * 交互式查询扩展（多轮对话）
   */
  async interactiveExpand(
    userInput: string,
    conversationHistory: Array<{ role: 'user' | 'assistant'; content: string }> = []
  ): Promise<QueryExpansionResult> {
    await this.initialize();

    const systemPrompt = `你是一个专业的学术文献搜索助手。通过多轮对话来帮助用户明确研究方向并生成搜索关键词。

每次对话都要：
1. 理解用户的回答
2. 更新对用户需求的理解
3. 如果信息足够，生成关键词列表
4. 如果信息不足，提出1-2个关键问题

返回 JSON 格式的结果。`;

    const messages = [
      { role: 'system' as const, content: systemPrompt },
      ...conversationHistory,
      { role: 'user' as const, content: userInput }
    ];

    try {
      const response = await this.ai!.chat(messages, { temperature: 0.7 });

      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const result = JSON.parse(jsonMatch[0]);
        return result as QueryExpansionResult;
      }

      return {
        confirmation: {},
        keywords: [],
        needsMoreInfo: true,
        followUpQuestions: ['请提供更多信息以帮助我理解你的研究方向。']
      };
    } catch (error) {
      throw new Error(`Interactive expansion failed: ${getErrorMessage(error)}`);
    }
  }

  /**
   * 格式化输出结果（用于 CLI 显示）
   */
  formatResult(result: QueryExpansionResult): string {
    let output = '\n📋 确认信息：\n';

    const { confirmation } = result;
    if (confirmation.coreTheme) output += `- 核心主题：${confirmation.coreTheme}\n`;
    if (confirmation.subField) output += `- 子领域：${confirmation.subField}\n`;
    if (confirmation.applicationScenario) output += `- 应用场景：${confirmation.applicationScenario}\n`;
    if (confirmation.timeRange) output += `- 时间范围：${confirmation.timeRange}\n`;
    if (confirmation.preferredSources) output += `- 偏好来源：${confirmation.preferredSources}\n`;

    if (result.keywords.length > 0) {
      output += '\n🔍 建议关键词：\n';
      result.keywords.forEach((kw, index) => {
        const typeEmoji = {
          core: '🎯',
          synonym: '🔄',
          abbreviation: '📝',
          related: '🔗',
          application: '💡'
        }[kw.type] || '•';
        output += `${index + 1}. ${typeEmoji} ${kw.term} - ${kw.description}\n`;
      });
    }

    if (result.followUpQuestions && result.followUpQuestions.length > 0) {
      output += '\n❓ 追问：\n';
      result.followUpQuestions.forEach((q, index) => {
        output += `${index + 1}. ${q}\n`;
      });
    }

    return output;
  }
}
