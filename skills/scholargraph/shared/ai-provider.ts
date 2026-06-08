/**
 * AI Provider Adapter - 多 AI 提供商适配器
 * 支持 ZAI、OpenAI、Anthropic、Azure、Ollama、Qwen
 */

import type {
  AIProviderType,
  AIProviderConfig,
  ChatMessage,
  ChatOptions,
  WebSearchResultItem
} from './types';
import { ApiInitializationError, ApiCallError, getErrorMessage } from './errors';
import { withRetry } from './utils';

/**
 * 统一的 AI 接口
 */
export interface AIProvider {
  chat(messages: ChatMessage[], options?: ChatOptions): Promise<string>;
  webSearch?(query: string, num?: number): Promise<WebSearchResultItem[]>;
  dispose?(): void;
}

/**
 * 获取环境变量中的 AI 提供商类型
 */
function getProviderTypeFromEnv(): AIProviderType {
  const envProvider = process.env.AI_PROVIDER?.toLowerCase();
  const validProviders = ['zai', 'openai', 'anthropic', 'azure', 'ollama', 'qwen', 'minimax', 'deepseek', 'zhipu', 'baichuan', 'moonshot', 'yi', 'doubao', 'groq', 'together'];
  if (envProvider && validProviders.includes(envProvider)) {
    return envProvider as AIProviderType;
  }
  return 'zai';
}

/**
 * 创建 AI 提供商实例
 */
export async function createAIProvider(config?: AIProviderConfig): Promise<AIProvider> {
  const type = config?.type || getProviderTypeFromEnv();

  switch (type) {
    case 'zai':
      return createZAIProvider(config);
    case 'openai':
      return createOpenAIProvider(config);
    case 'anthropic':
      return createAnthropicProvider(config);
    case 'azure':
      return createAzureOpenAIProvider(config);
    case 'ollama':
      return createOllamaProvider(config);
    case 'qwen':
      return createQwenProvider(config);
    case 'minimax':
      return createMiniMaxProvider(config);
    case 'deepseek':
      return createDeepSeekProvider(config);
    case 'zhipu':
      return createZhipuProvider(config);
    case 'baichuan':
      return createBaichuanProvider(config);
    case 'moonshot':
      return createMoonshotProvider(config);
    case 'yi':
      return createYiProvider(config);
    case 'doubao':
      return createDoubaoProvider(config);
    case 'groq':
      return createGroqProvider(config);
    case 'together':
      return createTogetherProvider(config);
    default:
      throw new ApiInitializationError(`Unsupported AI provider: ${type}`);
  }
}

/**
 * ZAI 提供商实现
 */
async function createZAIProvider(config?: AIProviderConfig): Promise<AIProvider> {
  try {
    const ZAI = (await import('z-ai-web-dev-sdk')).default;
    const zai = await withRetry(() => ZAI.create(), { maxRetries: 3 });

    return {
      async chat(messages: ChatMessage[], options?: ChatOptions): Promise<string> {
        const completion = await zai.chat.completions.create({
          messages: messages.map(m => ({ role: m.role, content: m.content })),
          temperature: options?.temperature ?? 0.2
        });
        return completion.choices[0]?.message?.content || '';
      },

      async webSearch(query: string, num: number = 10): Promise<WebSearchResultItem[]> {
        const results = await zai.functions.invoke('web_search', { query, num });
        return (results as WebSearchResultItem[]).map(item => ({
          name: item.name,
          url: item.url,
          snippet: item.snippet,
          date: item.date,
          host_name: item.host_name
        }));
      }
    };
  } catch (error) {
    throw new ApiInitializationError(
      `Failed to initialize ZAI provider: ${getErrorMessage(error)}`,
      error instanceof Error ? error : undefined
    );
  }
}

/**
 * OpenAI 提供商实现
 */
async function createOpenAIProvider(config?: AIProviderConfig): Promise<AIProvider> {
  try {
    const { default: OpenAI } = await import('openai');
    const client = new OpenAI({
      apiKey: config?.apiKey || process.env.OPENAI_API_KEY,
      baseURL: config?.baseUrl || process.env.OPENAI_BASE_URL
    });
    const model = config?.model || process.env.OPENAI_MODEL || 'gpt-4o';

    return {
      async chat(messages: ChatMessage[], options?: ChatOptions): Promise<string> {
        const completion = await client.chat.completions.create({
          model: options?.model || model,
          messages: messages.map(m => ({ role: m.role, content: m.content })),
          temperature: options?.temperature ?? 0.2,
          max_tokens: options?.maxTokens
        });
        return completion.choices[0]?.message?.content || '';
      },

      // OpenAI 不支持原生 web search
      // 可以通过 Serper API 或其他搜索 API 实现
      async webSearch(query: string, num: number = 10): Promise<WebSearchResultItem[]> {
        // 检查是否配置了 Serper API
        const serperKey = process.env.SERPER_API_KEY;
        if (serperKey) {
          return searchWithSerper(query, num, serperKey);
        }
        console.warn('OpenAI provider does not support web search without SERPER_API_KEY');
        return [];
      }
    };
  } catch (error) {
    throw new ApiInitializationError(
      `Failed to initialize OpenAI provider: ${getErrorMessage(error)}`,
      error instanceof Error ? error : undefined
    );
  }
}

/**
 * Anthropic 提供商实现
 */
async function createAnthropicProvider(config?: AIProviderConfig): Promise<AIProvider> {
  try {
    const { default: Anthropic } = await import('@anthropic-ai/sdk');
    const client = new Anthropic({
      apiKey: config?.apiKey || process.env.ANTHROPIC_API_KEY
    });
    const model = config?.model || process.env.ANTHROPIC_MODEL || 'claude-sonnet-4-20250514';

    return {
      async chat(messages: ChatMessage[], options?: ChatOptions): Promise<string> {
        // 分离 system 消息
        const systemMessage = messages.find(m => m.role === 'system');
        const otherMessages = messages.filter(m => m.role !== 'system');

        const response = await client.messages.create({
          model: options?.model || model,
          max_tokens: options?.maxTokens || 4096,
          system: systemMessage?.content,
          messages: otherMessages.map(m => ({
            role: m.role as 'user' | 'assistant',
            content: m.content
          }))
        });

        const textBlock = response.content.find(block => block.type === 'text');
        return textBlock && textBlock.type === 'text' ? textBlock.text : '';
      },

      // Anthropic 不支持原生 web search
      async webSearch(query: string, num: number = 10): Promise<WebSearchResultItem[]> {
        const serperKey = process.env.SERPER_API_KEY;
        if (serperKey) {
          return searchWithSerper(query, num, serperKey);
        }
        console.warn('Anthropic provider does not support web search without SERPER_API_KEY');
        return [];
      }
    };
  } catch (error) {
    throw new ApiInitializationError(
      `Failed to initialize Anthropic provider: ${getErrorMessage(error)}`,
      error instanceof Error ? error : undefined
    );
  }
}

/**
 * Azure OpenAI 提供商实现
 */
async function createAzureOpenAIProvider(config?: AIProviderConfig): Promise<AIProvider> {
  try {
    const { default: OpenAI } = await import('openai');

    const endpoint = config?.baseUrl || process.env.AZURE_OPENAI_ENDPOINT;
    const apiKey = config?.apiKey || process.env.AZURE_OPENAI_API_KEY;
    const deployment = config?.model || process.env.AZURE_OPENAI_DEPLOYMENT || 'gpt-4o';

    if (!endpoint || !apiKey) {
      throw new Error('Azure OpenAI requires AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY');
    }

    const client = new OpenAI({
      apiKey,
      baseURL: `${endpoint}/openai/deployments/${deployment}`,
      defaultQuery: { 'api-version': '2024-02-15-preview' },
      defaultHeaders: { 'api-key': apiKey }
    });

    return {
      async chat(messages: ChatMessage[], options?: ChatOptions): Promise<string> {
        const completion = await client.chat.completions.create({
          model: deployment,
          messages: messages.map(m => ({ role: m.role, content: m.content })),
          temperature: options?.temperature ?? 0.2,
          max_tokens: options?.maxTokens
        });
        return completion.choices[0]?.message?.content || '';
      },

      async webSearch(query: string, num: number = 10): Promise<WebSearchResultItem[]> {
        const serperKey = process.env.SERPER_API_KEY;
        if (serperKey) {
          return searchWithSerper(query, num, serperKey);
        }
        console.warn('Azure OpenAI provider does not support web search without SERPER_API_KEY');
        return [];
      }
    };
  } catch (error) {
    throw new ApiInitializationError(
      `Failed to initialize Azure OpenAI provider: ${getErrorMessage(error)}`,
      error instanceof Error ? error : undefined
    );
  }
}

/**
 * Ollama 本地提供商实现
 */
async function createOllamaProvider(config?: AIProviderConfig): Promise<AIProvider> {
  const baseUrl = config?.baseUrl || process.env.OLLAMA_BASE_URL || 'http://localhost:11434';
  const model = config?.model || process.env.OLLAMA_MODEL || 'llama3';

  return {
    async chat(messages: ChatMessage[], options?: ChatOptions): Promise<string> {
      const response = await fetch(`${baseUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: options?.model || model,
          messages: messages.map(m => ({ role: m.role, content: m.content })),
          stream: false,
          options: {
            temperature: options?.temperature ?? 0.2
          }
        })
      });

      if (!response.ok) {
        throw new ApiCallError(`Ollama API error: ${response.status}`, {
          endpoint: `${baseUrl}/api/chat`,
          responseStatus: response.status
        });
      }

      const data = await response.json() as { message?: { content?: string } };
      return data.message?.content || '';
    },

    // Ollama 不支持 web search
    async webSearch(query: string, num: number = 10): Promise<WebSearchResultItem[]> {
      const serperKey = process.env.SERPER_API_KEY;
      if (serperKey) {
        return searchWithSerper(query, num, serperKey);
      }
      console.warn('Ollama provider does not support web search without SERPER_API_KEY');
      return [];
    }
  };
}

/**
 * 使用 Serper API 进行 web 搜索
 */
async function searchWithSerper(
  query: string,
  num: number,
  apiKey: string
): Promise<WebSearchResultItem[]> {
  try {
    const response = await fetch('https://google.serper.dev/search', {
      method: 'POST',
      headers: {
        'X-API-KEY': apiKey,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        q: query,
        num
      })
    });

    if (!response.ok) {
      throw new ApiCallError(`Serper API error: ${response.status}`, {
        endpoint: 'https://google.serper.dev/search',
        responseStatus: response.status
      });
    }

    const data = await response.json() as {
      organic?: Array<{
        title: string;
        link: string;
        snippet?: string;
        date?: string;
      }>;
    };

    return (data.organic || []).map(item => ({
      name: item.title,
      url: item.link,
      snippet: item.snippet,
      date: item.date
    }));
  } catch (error) {
    console.error('Serper search error:', getErrorMessage(error));
    return [];
  }
}

/**
 * Qwen (通义千问) 提供商实现
 * 使用 OpenAI 兼容的 API 格式
 */
async function createQwenProvider(config?: AIProviderConfig): Promise<AIProvider> {
  const baseUrl = config?.baseUrl || process.env.QWEN_BASE_URL || 'https://dashscope.aliyuncs.com/compatible-mode/v1';
  const apiKey = config?.apiKey || process.env.QWEN_API_KEY || process.env.DASHSCOPE_API_KEY;
  const model = config?.model || process.env.QWEN_MODEL || 'qwen-plus';

  if (!apiKey) {
    throw new ApiInitializationError('Qwen requires QWEN_API_KEY or DASHSCOPE_API_KEY');
  }

  return {
    async chat(messages: ChatMessage[], options?: ChatOptions): Promise<string> {
      const response = await fetch(`${baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: options?.model || model,
          messages: messages.map(m => ({ role: m.role, content: m.content })),
          temperature: options?.temperature ?? 0.2,
          max_tokens: options?.maxTokens
        })
      });

      if (!response.ok) {
        const errorText = await response.text().catch(() => '');
        throw new ApiCallError(`Qwen API error: ${response.status} ${errorText}`, {
          endpoint: `${baseUrl}/chat/completions`,
          responseStatus: response.status
        });
      }

      const data = await response.json() as {
        choices?: Array<{ message?: { content?: string } }>;
      };
      return data.choices?.[0]?.message?.content || '';
    },

    // Qwen 不支持原生 web search
    async webSearch(query: string, num: number = 10): Promise<WebSearchResultItem[]> {
      const serperKey = process.env.SERPER_API_KEY;
      if (serperKey) {
        return searchWithSerper(query, num, serperKey);
      }
      console.warn('Qwen provider does not support web search without SERPER_API_KEY');
      return [];
    }
  };
}

/**
 * MiniMax 提供商实现
 * 支持 MiniMax Coding Plan (api.minimaxi.com) 和标准 MiniMax API
 */
async function createMiniMaxProvider(config?: AIProviderConfig): Promise<AIProvider> {
  const baseUrl = config?.baseUrl || process.env.MINIMAX_BASE_URL || 'https://api.minimaxi.com/v1';
  const apiKey = config?.apiKey || process.env.MINIMAX_API_KEY;
  const model = config?.model || process.env.MINIMAX_MODEL || 'MiniMax-M1';

  if (!apiKey) {
    throw new ApiInitializationError('MiniMax requires MINIMAX_API_KEY');
  }

  return createOpenAICompatibleProvider(baseUrl, apiKey, model, 'MiniMax');
}

/**
 * DeepSeek 提供商实现
 */
async function createDeepSeekProvider(config?: AIProviderConfig): Promise<AIProvider> {
  const baseUrl = config?.baseUrl || process.env.DEEPSEEK_BASE_URL || 'https://api.deepseek.com/v1';
  const apiKey = config?.apiKey || process.env.DEEPSEEK_API_KEY;
  const model = config?.model || process.env.DEEPSEEK_MODEL || 'deepseek-chat';

  if (!apiKey) {
    throw new ApiInitializationError('DeepSeek requires DEEPSEEK_API_KEY');
  }

  return createOpenAICompatibleProvider(baseUrl, apiKey, model, 'DeepSeek');
}

/**
 * 智谱 AI (GLM) 提供商实现
 */
async function createZhipuProvider(config?: AIProviderConfig): Promise<AIProvider> {
  const baseUrl = config?.baseUrl || process.env.ZHIPU_BASE_URL || 'https://open.bigmodel.cn/api/paas/v4';
  const apiKey = config?.apiKey || process.env.ZHIPU_API_KEY;
  const model = config?.model || process.env.ZHIPU_MODEL || 'glm-4';

  if (!apiKey) {
    throw new ApiInitializationError('Zhipu requires ZHIPU_API_KEY');
  }

  return createOpenAICompatibleProvider(baseUrl, apiKey, model, 'Zhipu');
}

/**
 * 百川 AI 提供商实现
 */
async function createBaichuanProvider(config?: AIProviderConfig): Promise<AIProvider> {
  const baseUrl = config?.baseUrl || process.env.BAICHUAN_BASE_URL || 'https://api.baichuan-ai.com/v1';
  const apiKey = config?.apiKey || process.env.BAICHUAN_API_KEY;
  const model = config?.model || process.env.BAICHUAN_MODEL || 'Baichuan4';

  if (!apiKey) {
    throw new ApiInitializationError('Baichuan requires BAICHUAN_API_KEY');
  }

  return createOpenAICompatibleProvider(baseUrl, apiKey, model, 'Baichuan');
}

/**
 * Moonshot (Kimi) 提供商实现
 */
async function createMoonshotProvider(config?: AIProviderConfig): Promise<AIProvider> {
  const baseUrl = config?.baseUrl || process.env.MOONSHOT_BASE_URL || 'https://api.moonshot.cn/v1';
  const apiKey = config?.apiKey || process.env.MOONSHOT_API_KEY;
  const model = config?.model || process.env.MOONSHOT_MODEL || 'moonshot-v1-8k';

  if (!apiKey) {
    throw new ApiInitializationError('Moonshot requires MOONSHOT_API_KEY');
  }

  return createOpenAICompatibleProvider(baseUrl, apiKey, model, 'Moonshot');
}

/**
 * 零一万物 (Yi) 提供商实现
 */
async function createYiProvider(config?: AIProviderConfig): Promise<AIProvider> {
  const baseUrl = config?.baseUrl || process.env.YI_BASE_URL || 'https://api.lingyiwanwu.com/v1';
  const apiKey = config?.apiKey || process.env.YI_API_KEY;
  const model = config?.model || process.env.YI_MODEL || 'yi-large';

  if (!apiKey) {
    throw new ApiInitializationError('Yi requires YI_API_KEY');
  }

  return createOpenAICompatibleProvider(baseUrl, apiKey, model, 'Yi');
}

/**
 * 豆包 (字节跳动) 提供商实现
 */
async function createDoubaoProvider(config?: AIProviderConfig): Promise<AIProvider> {
  const baseUrl = config?.baseUrl || process.env.DOUBAO_BASE_URL || 'https://ark.cn-beijing.volces.com/api/v3';
  const apiKey = config?.apiKey || process.env.DOUBAO_API_KEY;
  const model = config?.model || process.env.DOUBAO_MODEL || 'doubao-pro-4k';

  if (!apiKey) {
    throw new ApiInitializationError('Doubao requires DOUBAO_API_KEY');
  }

  return createOpenAICompatibleProvider(baseUrl, apiKey, model, 'Doubao');
}

/**
 * Groq 提供商实现
 */
async function createGroqProvider(config?: AIProviderConfig): Promise<AIProvider> {
  const baseUrl = config?.baseUrl || process.env.GROQ_BASE_URL || 'https://api.groq.com/openai/v1';
  const apiKey = config?.apiKey || process.env.GROQ_API_KEY;
  const model = config?.model || process.env.GROQ_MODEL || 'llama-3.1-70b-versatile';

  if (!apiKey) {
    throw new ApiInitializationError('Groq requires GROQ_API_KEY');
  }

  return createOpenAICompatibleProvider(baseUrl, apiKey, model, 'Groq');
}

/**
 * Together AI 提供商实现
 */
async function createTogetherProvider(config?: AIProviderConfig): Promise<AIProvider> {
  const baseUrl = config?.baseUrl || process.env.TOGETHER_BASE_URL || 'https://api.together.xyz/v1';
  const apiKey = config?.apiKey || process.env.TOGETHER_API_KEY;
  const model = config?.model || process.env.TOGETHER_MODEL || 'meta-llama/Llama-3-70b-chat-hf';

  if (!apiKey) {
    throw new ApiInitializationError('Together requires TOGETHER_API_KEY');
  }

  return createOpenAICompatibleProvider(baseUrl, apiKey, model, 'Together');
}

/**
 * 通用 OpenAI 兼容提供商工厂函数
 */
function createOpenAICompatibleProvider(
  baseUrl: string,
  apiKey: string,
  model: string,
  providerName: string
): AIProvider {
  return {
    async chat(messages: ChatMessage[], options?: ChatOptions): Promise<string> {
      const response = await fetch(`${baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: options?.model || model,
          messages: messages.map(m => ({ role: m.role, content: m.content })),
          temperature: options?.temperature ?? 0.2,
          max_tokens: options?.maxTokens
        })
      });

      if (!response.ok) {
        const errorText = await response.text().catch(() => '');
        throw new ApiCallError(`${providerName} API error: ${response.status} ${errorText}`, {
          endpoint: `${baseUrl}/chat/completions`,
          responseStatus: response.status
        });
      }

      const data = await response.json() as {
        choices?: Array<{ message?: { content?: string } }>;
      };
      return data.choices?.[0]?.message?.content || '';
    },

    async webSearch(query: string, num: number = 10): Promise<WebSearchResultItem[]> {
      const serperKey = process.env.SERPER_API_KEY;
      if (serperKey) {
        return searchWithSerper(query, num, serperKey);
      }
      console.warn(`${providerName} provider does not support web search without SERPER_API_KEY`);
      return [];
    }
  };
}

/**
 * 检查 AI 提供商是否可用
 */
export function isProviderAvailable(type: AIProviderType): boolean {
  switch (type) {
    case 'zai':
      return true;
    case 'openai':
      return !!process.env.OPENAI_API_KEY;
    case 'anthropic':
      return !!process.env.ANTHROPIC_API_KEY;
    case 'azure':
      return !!(process.env.AZURE_OPENAI_ENDPOINT && process.env.AZURE_OPENAI_API_KEY);
    case 'ollama':
      return true;
    case 'qwen':
      return !!(process.env.QWEN_API_KEY || process.env.DASHSCOPE_API_KEY);
    case 'minimax':
      return !!process.env.MINIMAX_API_KEY;
    case 'deepseek':
      return !!process.env.DEEPSEEK_API_KEY;
    case 'zhipu':
      return !!process.env.ZHIPU_API_KEY;
    case 'baichuan':
      return !!process.env.BAICHUAN_API_KEY;
    case 'moonshot':
      return !!process.env.MOONSHOT_API_KEY;
    case 'yi':
      return !!process.env.YI_API_KEY;
    case 'doubao':
      return !!process.env.DOUBAO_API_KEY;
    case 'groq':
      return !!process.env.GROQ_API_KEY;
    case 'together':
      return !!process.env.TOGETHER_API_KEY;
    default:
      return false;
  }
}

/**
 * 获取可用的 AI 提供商列表
 */
export function getAvailableProviders(): AIProviderType[] {
  const providers: AIProviderType[] = [
    'zai', 'openai', 'anthropic', 'azure', 'ollama', 'qwen',
    'minimax', 'deepseek', 'zhipu', 'baichuan', 'moonshot', 'yi', 'doubao',
    'groq', 'together'
  ];
  return providers.filter(isProviderAvailable);
}
