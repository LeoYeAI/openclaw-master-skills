/**
 * @module graph-viz/paper-viz-bridge
 * @description 图谱→论文演示的数据桥接
 *
 * 从 KnowledgeGraphData 的 literatureIndex 和 conceptIndex 中
 * 为每个节点构建论文摘要数据，嵌入图谱 HTML 供前端使用。
 */

import type {
  KnowledgeGraphData,
  KnowledgeNode,
  LiteratureReference,
  PaperMetadata,
} from '../../knowledge-graph/scripts/graph';
import type { PaperPayload, NodePaperSummary } from './types';

/** 桥接配置选项 */
export interface BridgeOptions {
  /** 每个节点最多包含的论文数 */
  maxPapersPerNode?: number;
  /** 最小相关度阈值 */
  minRelevance?: number;
  /** 摘要截断长度 */
  abstractMaxLength?: number;
}

const DEFAULT_OPTIONS: Required<BridgeOptions> = {
  maxPapersPerNode: 10,
  minRelevance: 0.1,
  abstractMaxLength: 300,
};

/**
 * PaperVizBridge — 构建图谱节点的论文数据 payload
 *
 * @example
 * ```ts
 * const bridge = new PaperVizBridge();
 * const payload = bridge.buildAllPaperPayloads(graph);
 * // payload 可直接传给 generateGraphHtml 的 paperPayload 选项
 * ```
 */
export class PaperVizBridge {
  private options: Required<BridgeOptions>;

  constructor(options?: BridgeOptions) {
    this.options = { ...DEFAULT_OPTIONS, ...options };
  }

  /**
   * 为所有节点构建论文数据
   * @param graph - 知识图谱数据
   * @returns 节点 ID → 论文列表的映射
   */
  buildAllPaperPayloads(graph: KnowledgeGraphData): PaperPayload {
    const payload: PaperPayload = {};

    for (const node of graph.nodes) {
      const papers = this.buildNodePapers(node, graph);
      if (papers.length > 0) {
        payload[node.id] = papers;
      }
    }

    return payload;
  }

  /**
   * 为单个节点构建论文列表
   * @param node - 知识节点
   * @param graph - 知识图谱数据
   * @returns 论文摘要列表（按相关度排序）
   */
  buildNodePapers(node: KnowledgeNode, graph: KnowledgeGraphData): NodePaperSummary[] {
    const paperMap = new Map<string, NodePaperSummary>();

    // 来源 1: node.literatureReferences
    if (node.literatureReferences) {
      for (const ref of node.literatureReferences) {
        if (ref.relevance < this.options.minRelevance) continue;
        const meta = this.findPaperMetadata(ref.paperId, graph);
        paperMap.set(ref.paperId, this.buildSummary(ref, meta));
      }
    }

    // 来源 2: conceptIndex.conceptToPapers
    if (graph.conceptIndex?.conceptToPapers) {
      const refs = graph.conceptIndex.conceptToPapers.get(node.id);
      if (refs) {
        for (const ref of refs) {
          if (ref.relevance < this.options.minRelevance) continue;
          if (paperMap.has(ref.paperId)) continue; // 去重
          const meta = this.findPaperMetadata(ref.paperId, graph);
          paperMap.set(ref.paperId, this.buildSummary(ref, meta));
        }
      }
    }

    // 按相关度降序排序，截断
    return Array.from(paperMap.values())
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, this.options.maxPapersPerNode);
  }

  /** 从图谱 literatureIndex 中查找论文元数据 */
  private findPaperMetadata(paperId: string, graph: KnowledgeGraphData): PaperMetadata | null {
    if (graph.literatureIndex?.papers) {
      return graph.literatureIndex.papers.get(paperId) ?? null;
    }
    return null;
  }

  /** 构建论文摘要 */
  private buildSummary(ref: LiteratureReference, meta: PaperMetadata | null): NodePaperSummary {
    const maxLen = this.options.abstractMaxLength;

    return {
      id: ref.paperId,
      title: meta?.title ?? ref.title,
      authors: meta?.authors ?? [],
      abstract: meta?.abstract
        ? (meta.abstract.length > maxLen
          ? meta.abstract.slice(0, maxLen) + '...'
          : meta.abstract)
        : '',
      url: meta?.url ?? '',
      citations: meta?.citations,
      relevance: ref.relevance,
      mentionType: ref.mentionType,
    };
  }
}
