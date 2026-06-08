/**
 * @module graph-viz/graph-data-adapter
 * @description 将 KnowledgeGraphData 转换为 D3 可视化数据
 *
 * 核心计算：
 * - 节点半径 = 15 + sqrt(paperCount) * 8, 上限 60
 * - 边粗细 = relationWeight + sharedPaperCount * 0.5, 范围 [1, 8]
 */

import type {
  KnowledgeGraphData,
  KnowledgeNode,
  KnowledgeEdge,
  LiteratureReference,
} from '../../knowledge-graph/scripts/graph';
import type {
  D3GraphData,
  D3GraphNode,
  D3GraphEdge,
  NodeCategory,
  RelationType,
  EdgeStyle,
} from './types';
import {
  CATEGORY_COLORS,
  RELATION_WEIGHTS,
  RELATION_STYLES,
} from './types';

/**
 * GraphDataAdapter — KnowledgeGraphData → D3GraphData 转换器
 *
 * @example
 * ```ts
 * const adapter = new GraphDataAdapter();
 * const d3Data = adapter.convert(knowledgeGraph);
 * ```
 */
export class GraphDataAdapter {
  /**
   * 将 KnowledgeGraphData 转换为 D3GraphData
   * @param graph - 知识图谱数据
   * @returns D3 可视化数据
   */
  convert(graph: KnowledgeGraphData): D3GraphData {
    const nodeMap = new Map<string, KnowledgeNode>();
    for (const node of graph.nodes) {
      nodeMap.set(node.id, node);
    }

    // 计算每个节点的论文数量
    const paperCounts = this.computePaperCounts(graph);

    // 计算每条边的共享论文数
    const sharedPaperCounts = this.computeSharedPaperCounts(graph);

    const nodes: D3GraphNode[] = graph.nodes.map((node) =>
      this.convertNode(node, paperCounts.get(node.id) ?? 0)
    );

    const edges: D3GraphEdge[] = graph.edges.map((edge) =>
      this.convertEdge(edge, sharedPaperCounts.get(this.edgeKey(edge)) ?? 0)
    );

    const totalPapers = graph.literatureIndex?.papers?.size ?? 0;

    return {
      nodes,
      edges,
      metadata: {
        name: graph.graphMetadata?.name ?? 'Knowledge Graph',
        totalNodes: nodes.length,
        totalEdges: edges.length,
        totalPapers,
        generatedAt: new Date().toISOString(),
      },
    };
  }

  /**
   * 计算节点半径
   * @param paperCount - 关联论文数
   * @returns 半径（px）
   */
  static computeRadius(paperCount: number): number {
    const r = 15 + Math.sqrt(paperCount) * 8;
    return Math.min(r, 60);
  }

  /**
   * 计算边线宽度
   * @param relation - 关系类型
   * @param sharedPaperCount - 共享论文数
   * @returns 线宽（px）
   */
  static computeStrokeWidth(relation: RelationType, sharedPaperCount: number): number {
    const base = RELATION_WEIGHTS[relation] ?? 1;
    const width = base + sharedPaperCount * 0.5;
    return Math.max(1, Math.min(width, 8));
  }

  /** 转换单个节点 */
  private convertNode(node: KnowledgeNode, paperCount: number): D3GraphNode {
    const category = node.category as NodeCategory;
    return {
      id: node.id,
      label: node.label,
      category,
      importance: node.importance,
      description: node.description ?? '',
      radius: GraphDataAdapter.computeRadius(paperCount),
      paperCount,
      keyPaperIds: node.keyPapers ?? [],
      color: CATEGORY_COLORS[category] ?? CATEGORY_COLORS.core,
    };
  }

  /** 转换单条边 */
  private convertEdge(edge: KnowledgeEdge, sharedPaperCount: number): D3GraphEdge {
    const relation = edge.relation as RelationType;
    const strokeWidth = GraphDataAdapter.computeStrokeWidth(relation, sharedPaperCount);
    const relStyle = RELATION_STYLES[relation] ?? RELATION_STYLES.related;

    const style: EdgeStyle = {
      color: relStyle.color,
      dasharray: relStyle.dasharray,
      opacity: Math.min(0.4 + strokeWidth * 0.08, 0.9),
    };

    return {
      source: edge.source,
      target: edge.target,
      relation,
      label: edge.label ?? relation,
      strokeWidth,
      sharedPaperCount,
      style,
    };
  }

  /** 计算每个节点的关联论文数 */
  private computePaperCounts(graph: KnowledgeGraphData): Map<string, number> {
    const counts = new Map<string, number>();

    for (const node of graph.nodes) {
      // 来源1: literatureReferences
      const refCount = node.literatureReferences?.length ?? 0;

      // 来源2: conceptIndex
      let indexCount = 0;
      if (graph.conceptIndex?.conceptToPapers) {
        const refs = graph.conceptIndex.conceptToPapers.get(node.id);
        if (refs) indexCount = refs.length;
      }

      counts.set(node.id, Math.max(refCount, indexCount));
    }

    return counts;
  }

  /** 计算每条边两端节点共享的论文数 */
  private computeSharedPaperCounts(graph: KnowledgeGraphData): Map<string, number> {
    const shared = new Map<string, number>();

    if (!graph.conceptIndex?.conceptToPapers) {
      // 无索引数据时全部返回 0
      for (const edge of graph.edges) {
        shared.set(this.edgeKey(edge), 0);
      }
      return shared;
    }

    const ctp = graph.conceptIndex.conceptToPapers;

    for (const edge of graph.edges) {
      const sourcePapers = new Set(
        (ctp.get(edge.source) ?? []).map((r) => r.paperId)
      );
      const targetPapers = (ctp.get(edge.target) ?? []).map((r) => r.paperId);

      let count = 0;
      for (const pid of targetPapers) {
        if (sourcePapers.has(pid)) count++;
      }

      shared.set(this.edgeKey(edge), count);
    }

    return shared;
  }

  /** 生成边的唯一 key */
  private edgeKey(edge: KnowledgeEdge): string {
    return `${edge.source}--${edge.target}`;
  }
}
