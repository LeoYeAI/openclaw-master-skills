/**
 * @module graph-viz/types
 * @description 交互式知识图谱可视化的数据类型定义
 */

/** 节点类别 */
export type NodeCategory = 'foundation' | 'core' | 'advanced' | 'application';

/** 关系类型 */
export type RelationType = 'prerequisite' | 'related' | 'derived' | 'component';

/** 类别颜色映射 */
export const CATEGORY_COLORS: Record<NodeCategory, string> = {
  foundation: '#4FC3F7',
  core: '#FFB74D',
  advanced: '#CE93D8',
  application: '#81C784',
};

/** 关系权重映射 */
export const RELATION_WEIGHTS: Record<RelationType, number> = {
  prerequisite: 3,
  derived: 2.5,
  component: 2,
  related: 1,
};

/** D3 力导向图节点 */
export interface D3GraphNode {
  /** 节点唯一 ID */
  id: string;
  /** 显示标签 */
  label: string;
  /** 类别 */
  category: NodeCategory;
  /** 重要度 (1-5) */
  importance: number;
  /** 节点描述 */
  description: string;
  /** 节点半径（根据关联论文数计算） */
  radius: number;
  /** 关联论文数量 */
  paperCount: number;
  /** 关键论文 ID 列表 */
  keyPaperIds: string[];
  /** 节点颜色 */
  color: string;
  /** D3 力模拟坐标（运行时填充） */
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

/** D3 力导向图边 */
export interface D3GraphEdge {
  /** 源节点 ID */
  source: string;
  /** 目标节点 ID */
  target: string;
  /** 关系类型 */
  relation: RelationType;
  /** 显示标签 */
  label: string;
  /** 边线宽度（根据关系权重 + 共享论文数计算） */
  strokeWidth: number;
  /** 共享论文数 */
  sharedPaperCount: number;
  /** 样式 */
  style: EdgeStyle;
}

/** 边样式 */
export interface EdgeStyle {
  /** 颜色 */
  color: string;
  /** SVG dash 样式（虚线/实线） */
  dasharray: string;
  /** 透明度 */
  opacity: number;
}

/** D3 完整图谱数据 */
export interface D3GraphData {
  /** 节点列表 */
  nodes: D3GraphNode[];
  /** 边列表 */
  edges: D3GraphEdge[];
  /** 图谱元数据 */
  metadata: GraphVizMetadata;
}

/** 图谱可视化元数据 */
export interface GraphVizMetadata {
  /** 图谱名称 */
  name: string;
  /** 总节点数 */
  totalNodes: number;
  /** 总边数 */
  totalEdges: number;
  /** 总论文数 */
  totalPapers: number;
  /** 生成时间 */
  generatedAt: string;
}

/** 节点关联的论文摘要（嵌入图谱 HTML） */
export interface NodePaperSummary {
  /** 论文 ID */
  id: string;
  /** 标题 */
  title: string;
  /** 作者 */
  authors: string[];
  /** 摘要（截断） */
  abstract: string;
  /** URL */
  url: string;
  /** 引用数 */
  citations?: number;
  /** 关联度 */
  relevance: number;
  /** 引用类型 */
  mentionType: string;
}

/** 嵌入图谱的论文数据 payload */
export interface PaperPayload {
  /** 节点 ID → 论文列表 */
  [nodeId: string]: NodePaperSummary[];
}

/** 图谱 HTML 生成选项 */
export interface GraphHtmlOptions {
  /** 是否嵌入论文数据 */
  includePaperData?: boolean;
  /** 论文数据 payload */
  paperPayload?: PaperPayload;
  /** 画布宽度 */
  width?: number;
  /** 画布高度 */
  height?: number;
}

/** 关系样式映射 */
export const RELATION_STYLES: Record<RelationType, Omit<EdgeStyle, 'opacity'>> = {
  prerequisite: { color: '#EF5350', dasharray: '' },
  derived: { color: '#AB47BC', dasharray: '8 4' },
  component: { color: '#42A5F5', dasharray: '4 2' },
  related: { color: '#78909C', dasharray: '2 4' },
};
