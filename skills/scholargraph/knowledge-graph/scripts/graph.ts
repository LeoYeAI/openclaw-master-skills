/**
 * Knowledge Graph Builder - Core Module
 * 知识图谱构建核心模块
 *
 * 功能：
 * - 从概念列表构建知识图谱
 * - 识别概念间关系
 * - 生成可视化输出
 */

import { createAIProvider, type AIProvider } from '../../shared/ai-provider';
import { extractJson } from '../../shared/utils';
import { ApiInitializationError, getErrorMessage } from '../../shared/errors';

/**
 * 文献引用信息
 */
export interface LiteratureReference {
  /** 论文ID */
  paperId: string;
  /** 论文标题 */
  title: string;
  /** 相关度 (0-1) */
  relevance: number;
  /** 引用类型 */
  mentionType: 'foundational' | 'methodological' | 'application';
  /** 引用上下文 */
  contexts: string[];
}

/**
 * 概念定义（可多来源）
 */
export interface ConceptDefinition {
  /** 定义内容 */
  text: string;
  /** 来源论文ID */
  sourceId: string;
  /** 来源论文标题 */
  sourceTitle: string;
}

/**
 * 论文元数据（用于索引）
 */
export interface PaperMetadata {
  /** 论文ID */
  id: string;
  /** 标题 */
  title: string;
  /** 作者 */
  authors: string[];
  /** 摘要 */
  abstract: string;
  /** 发表日期 */
  publishDate: string;
  /** URL */
  url: string;
  /** PDF URL */
  pdfUrl?: string;
  /** 引用数 */
  citations?: number;
  /** 论文类型 */
  paperType: 'review' | 'research';
  /** 关键词 */
  keywords: string[];
  /** 额外元数据 */
  metadata?: Record<string, unknown>;
}

/**
 * 文献索引（论文→概念映射）
 */
export interface LiteratureIndex {
  /** 论文ID → 论文元数据 */
  papers: Map<string, PaperMetadata>;
  /** 论文ID → 关联概念ID列表 */
  paperToConcepts: Map<string, string[]>;
}

/**
 * 概念索引（概念→论文映射）
 */
export interface ConceptIndex {
  /** 概念ID → 论文引用列表 */
  conceptToPapers: Map<string, LiteratureReference[]>;
}

/**
 * 图谱元数据
 */
export interface GraphMetadata {
  /** 图谱名称 */
  name: string;
  /** 创建时间 */
  createdAt: string;
  /** 更新时间 */
  updatedAt: string;
  /** 来源综述 */
  sourceReviews: string[];
  /** 统计 */
  totalConcepts: number;
  totalPapers: number;
  totalRelations: number;
}

export interface KnowledgeNode {
  id: string;
  label: string;
  category: 'foundation' | 'core' | 'advanced' | 'application';
  importance: number;
  description?: string;
  /** 文献引用列表 */
  literatureReferences?: LiteratureReference[];
  /** 多来源定义 */
  definitions?: ConceptDefinition[];
  /** 关键论文ID */
  keyPapers?: string[];
  /** 节点元数据 */
  metadata?: {
    extractedFrom?: string[];
    lastUpdated?: string;
    confidence?: number;
  };
}

export interface KnowledgeEdge {
  source: string;
  target: string;
  relation: 'prerequisite' | 'related' | 'derived' | 'component';
  label?: string;
}

export interface KnowledgeGraphData {
  nodes: KnowledgeNode[];
  edges: KnowledgeEdge[];
  clusters: Map<string, string[]>;
  /** 文献索引 */
  literatureIndex?: LiteratureIndex;
  /** 概念索引 */
  conceptIndex?: ConceptIndex;
  /** 图谱元数据 */
  graphMetadata?: GraphMetadata;
}

export default class KnowledgeGraphBuilder {
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
   * 从概念列表构建知识图谱
   */
  async build(concepts: string[]): Promise<KnowledgeGraphData> {
    await this.initialize();

    // 识别概念间关系
    const relations = await this.identifyRelations(concepts);

    // 构建节点
    const nodes: KnowledgeNode[] = concepts.map((concept, index) => ({
      id: `node_${index}`,
      label: concept,
      category: this.categorizeConcept(concept, relations),
      importance: this.calculateImportance(concept, relations)
    }));

    // 构建边
    const edges: KnowledgeEdge[] = relations.map(r => ({
      source: nodes.find(n => n.label === r.source)?.id || r.source,
      target: nodes.find(n => n.label === r.target)?.id || r.target,
      relation: r.relation,
      label: r.relation
    }));

    // 构建聚类
    const clusters = this.buildClusters(nodes, edges);

    return { nodes, edges, clusters };
  }

  /**
   * 识别概念间关系
   */
  private async identifyRelations(
    concepts: string[]
  ): Promise<Array<{ source: string; target: string; relation: string }>> {
    const prompt = `分析以下概念之间的关系:

概念列表: ${concepts.join(', ')}

请识别概念之间的依赖和关联关系。返回JSON格式:
{
  "relations": [
    {
      "source": "源概念",
      "target": "目标概念",
      "relation": "prerequisite|related|derived|component"
    }
  ]
}

说明:
- prerequisite: 前置关系，学习target需要先学习source
- related: 相关关系，两个概念有关联但无直接依赖
- derived: 衍生关系，target是从source发展而来
- component: 组成关系，target是source的组成部分`;

    const responseText = await this.ai!.chat([
      { role: 'system', content: '你是一位知识体系分析专家。' },
      { role: 'user', content: prompt }
    ], { temperature: 0.2 });

    const result = extractJson<{ relations?: Array<{ source: string; target: string; relation: string }> }>(responseText);

    if (result.success && result.data?.relations) {
      return result.data.relations;
    }

    console.error('Error parsing relations response:', result.error);
    return [];
  }

  /**
   * 对概念分类
   */
  private categorizeConcept(
    concept: string,
    relations: Array<{ source: string; target: string; relation: string }>
  ): 'foundation' | 'core' | 'advanced' | 'application' {
    // 基于关系数量判断类别
    const asSource = relations.filter(r => r.source === concept).length;
    const asTarget = relations.filter(r => r.target === concept).length;

    if (asSource > asTarget + 2) {
      return 'foundation';
    } else if (asTarget > asSource + 2) {
      return 'application';
    } else if (asSource + asTarget > 4) {
      return 'core';
    }
    return 'advanced';
  }

  /**
   * 计算概念重要性
   */
  private calculateImportance(
    concept: string,
    relations: Array<{ source: string; target: string; relation: string }>
  ): number {
    const degree = relations.filter(r => r.source === concept || r.target === concept).length;
    return Math.min(5, Math.max(1, degree));
  }

  /**
   * 构建聚类
   */
  private buildClusters(
    nodes: KnowledgeNode[],
    edges: KnowledgeEdge[]
  ): Map<string, string[]> {
    const clusters = new Map<string, string[]>();

    // 按类别聚类
    const categories = ['foundation', 'core', 'advanced', 'application'];
    for (const category of categories) {
      const clusterNodes = nodes.filter(n => n.category === category).map(n => n.id);
      if (clusterNodes.length > 0) {
        clusters.set(category, clusterNodes);
      }
    }

    return clusters;
  }

  /**
   * 发现学习路径
   */
  findPath(
    graph: KnowledgeGraphData,
    from: string,
    to: string
  ): string[] {
    const { nodes, edges } = graph;

    // BFS寻找路径
    const fromNode = nodes.find(n => n.label === from || n.id === from);
    const toNode = nodes.find(n => n.label === to || n.id === to);

    if (!fromNode || !toNode) return [];

    const visited = new Set<string>();
    const queue: Array<{ node: string; path: string[] }> = [
      { node: fromNode.id, path: [fromNode.label] }
    ];

    while (queue.length > 0) {
      const { node, path } = queue.shift()!;

      if (node === toNode.id) {
        return path;
      }

      if (visited.has(node)) continue;
      visited.add(node);

      // 找到相邻节点
      const neighbors = edges
        .filter(e => e.source === node)
        .map(e => e.target);

      for (const neighbor of neighbors) {
        if (!visited.has(neighbor)) {
          const neighborNode = nodes.find(n => n.id === neighbor);
          queue.push({
            node: neighbor,
            path: [...path, neighborNode?.label || neighbor]
          });
        }
      }
    }

    return [];
  }

  /**
   * 导出为Mermaid格式
   */
  toMermaid(graph: KnowledgeGraphData): string {
    const { nodes, edges } = graph;

    let mermaid = 'graph TD\n';

    // 添加节点
    for (const node of nodes) {
      const shape = this.getMermaidShape(node.category);
      mermaid += `    ${node.id}${shape.left}${node.label}${shape.right}\n`;
    }

    // 添加边
    for (const edge of edges) {
      const arrow = this.getMermaidArrow(edge.relation);
      mermaid += `    ${edge.source} ${arrow} ${edge.target}\n`;
    }

    // 添加样式
    mermaid += '\n    %% 样式定义\n';
    mermaid += '    classDef foundation fill:#e1f5fe,stroke:#01579b\n';
    mermaid += '    classDef core fill:#fff3e0,stroke:#e65100\n';
    mermaid += '    classDef advanced fill:#f3e5f5,stroke:#4a148c\n';
    mermaid += '    classDef application fill:#e8f5e9,stroke:#1b5e20\n';

    for (const node of nodes) {
      mermaid += `    class ${node.id} ${node.category}\n`;
    }

    return mermaid;
  }

  /**
   * 获取Mermaid节点形状
   */
  private getMermaidShape(category: string): { left: string; right: string } {
    switch (category) {
      case 'foundation':
        return { left: '[', right: ']' };
      case 'core':
        return { left: '((', right: '))' };
      case 'advanced':
        return { left: '{{', right: '}}' };
      case 'application':
        return { left: '[[', right: ']]' };
      default:
        return { left: '[', right: ']' };
    }
  }

  /**
   * 获取Mermaid箭头样式
   */
  private getMermaidArrow(relation: string): string {
    switch (relation) {
      case 'prerequisite':
        return '-->';
      case 'related':
        return '-.->';
      case 'derived':
        return '==>';
      case 'component':
        return '--o';
      default:
        return '-->';
    }
  }

  /**
   * 导出为JSON
   */
  toJSON(graph: KnowledgeGraphData): string {
    return JSON.stringify({
      nodes: graph.nodes,
      edges: graph.edges,
      clusters: Object.fromEntries(graph.clusters),
      literatureIndex: graph.literatureIndex ? {
        papers: Object.fromEntries(graph.literatureIndex.papers),
        paperToConcepts: Object.fromEntries(graph.literatureIndex.paperToConcepts)
      } : undefined,
      conceptIndex: graph.conceptIndex ? {
        conceptToPapers: Object.fromEntries(graph.conceptIndex.conceptToPapers)
      } : undefined,
      graphMetadata: graph.graphMetadata
    }, null, 2);
  }

  /**
   * 从JSON导入
   */
  fromJSON(json: string): KnowledgeGraphData {
    const data = JSON.parse(json);
    const result: KnowledgeGraphData = {
      nodes: data.nodes,
      edges: data.edges,
      clusters: new Map(Object.entries(data.clusters || {}))
    };

    if (data.literatureIndex) {
      result.literatureIndex = {
        papers: new Map(Object.entries(data.literatureIndex.papers || {})),
        paperToConcepts: new Map(Object.entries(data.literatureIndex.paperToConcepts || {}))
      };
    }

    if (data.conceptIndex) {
      result.conceptIndex = {
        conceptToPapers: new Map(Object.entries(data.conceptIndex.conceptToPapers || {}))
      };
    }

    if (data.graphMetadata) {
      result.graphMetadata = data.graphMetadata;
    }

    return result;
  }

  /**
   * 获取拓扑排序（学习顺序）
   */
  getTopologicalOrder(graph: KnowledgeGraphData): string[] {
    const { nodes, edges } = graph;
    const inDegree = new Map<string, number>();
    const adjacency = new Map<string, string[]>();

    // 初始化
    for (const node of nodes) {
      inDegree.set(node.id, 0);
      adjacency.set(node.id, []);
    }

    // 计算入度
    for (const edge of edges) {
      if (edge.relation === 'prerequisite' || edge.relation === 'component') {
        inDegree.set(edge.target, (inDegree.get(edge.target) || 0) + 1);
        adjacency.get(edge.source)?.push(edge.target);
      }
    }

    // Kahn算法
    const queue: string[] = [];
    const result: string[] = [];

    for (const [node, degree] of inDegree) {
      if (degree === 0) {
        queue.push(node);
      }
    }

    while (queue.length > 0) {
      const current = queue.shift()!;
      const nodeLabel = nodes.find(n => n.id === current)?.label || current;
      result.push(nodeLabel);

      for (const neighbor of adjacency.get(current) || []) {
        const newDegree = (inDegree.get(neighbor) || 0) - 1;
        inDegree.set(neighbor, newDegree);
        if (newDegree === 0) {
          queue.push(neighbor);
        }
      }
    }

    return result;
  }
}

// CLI 支持
if (import.meta.main) {
  const args = process.argv.slice(2);
  const concepts = args.filter(a => !a.startsWith('--'));
  const outputIndex = args.indexOf('--output');
  const outputFile = outputIndex > -1 ? args[outputIndex + 1] : null;
  const formatIndex = args.indexOf('--format');
  const format = formatIndex > -1 ? args[formatIndex + 1] : 'mermaid';

  if (concepts.length === 0) {
    console.error('Usage: graph.ts <concept1> <concept2> ... [--output <file>] [--format mermaid|json]');
    process.exit(1);
  }

  const builder = new KnowledgeGraphBuilder();

  builder.initialize().then(() => builder.build(concepts)).then(graph => {
    let output: string;

    if (format === 'json') {
      output = builder.toJSON(graph);
    } else {
      output = builder.toMermaid(graph);
    }

    if (outputFile) {
      const fs = require('fs');
      fs.writeFileSync(outputFile, output);
      console.log(`Graph saved to ${outputFile}`);
    } else {
      console.log(output);
    }
  }).catch(err => {
    console.error('Error:', getErrorMessage(err));
    process.exit(1);
  });
}
