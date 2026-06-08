/**
 * Graph Storage - SQLite 持久化存储
 * 使用 bun:sqlite 实现知识图谱的持久化
 */

import { Database } from 'bun:sqlite';
import type {
  KnowledgeGraphData,
  KnowledgeNode,
  KnowledgeEdge,
  PaperMetadata,
  LiteratureReference,
  LiteratureIndex,
  ConceptIndex,
  GraphMetadata
} from './graph';

/** 数据库目录路径 */
const DEFAULT_DB_DIR = './data';
const DEFAULT_DB_NAME = 'knowledge-graphs.db';

export default class GraphStorage {
  private db: Database;

  constructor(dbPath?: string) {
    const path = dbPath || `${DEFAULT_DB_DIR}/${DEFAULT_DB_NAME}`;

    // 确保目录存在
    const fs = require('fs');
    const dir = path.substring(0, path.lastIndexOf('/'));
    if (dir && !fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    this.db = new Database(path);
    this.db.exec('PRAGMA journal_mode = WAL');
    this.db.exec('PRAGMA foreign_keys = ON');
    this.initSchema();
  }

  /**
   * 初始化数据库表结构
   */
  private initSchema(): void {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS graphs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        source_reviews TEXT,
        total_concepts INTEGER DEFAULT 0,
        total_papers INTEGER DEFAULT 0,
        total_relations INTEGER DEFAULT 0
      );

      CREATE TABLE IF NOT EXISTS nodes (
        id TEXT NOT NULL,
        graph_id INTEGER NOT NULL,
        label TEXT NOT NULL,
        category TEXT NOT NULL,
        importance INTEGER DEFAULT 1,
        description TEXT,
        definitions TEXT,
        key_papers TEXT,
        metadata TEXT,
        PRIMARY KEY (id, graph_id),
        FOREIGN KEY (graph_id) REFERENCES graphs(id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS edges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        graph_id INTEGER NOT NULL,
        source TEXT NOT NULL,
        target TEXT NOT NULL,
        relation TEXT NOT NULL,
        label TEXT,
        FOREIGN KEY (graph_id) REFERENCES graphs(id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS papers (
        id TEXT NOT NULL,
        graph_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        authors TEXT,
        abstract TEXT,
        publish_date TEXT,
        url TEXT,
        pdf_url TEXT,
        citations INTEGER,
        paper_type TEXT,
        keywords TEXT,
        metadata TEXT,
        PRIMARY KEY (id, graph_id),
        FOREIGN KEY (graph_id) REFERENCES graphs(id) ON DELETE CASCADE
      );

      CREATE TABLE IF NOT EXISTS concept_paper_index (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        graph_id INTEGER NOT NULL,
        concept_id TEXT NOT NULL,
        paper_id TEXT NOT NULL,
        relevance REAL NOT NULL,
        mention_type TEXT,
        mention_contexts TEXT,
        indexed_at TEXT NOT NULL,
        FOREIGN KEY (graph_id) REFERENCES graphs(id) ON DELETE CASCADE
      );

      CREATE INDEX IF NOT EXISTS idx_concept_paper ON concept_paper_index(graph_id, concept_id, relevance DESC);
      CREATE INDEX IF NOT EXISTS idx_paper_concept ON concept_paper_index(graph_id, paper_id);
      CREATE INDEX IF NOT EXISTS idx_nodes_graph ON nodes(graph_id);
      CREATE INDEX IF NOT EXISTS idx_edges_graph ON edges(graph_id);
      CREATE INDEX IF NOT EXISTS idx_papers_graph ON papers(graph_id);
    `);
  }

  /**
   * 保存图谱
   */
  saveGraph(graph: KnowledgeGraphData, name: string): void {
    const now = new Date().toISOString();
    const sourceReviews = graph.graphMetadata?.sourceReviews || [];

    const saveTransaction = this.db.transaction(() => {
      // 删除旧图谱（如果存在）
      const existing = this.db.query('SELECT id FROM graphs WHERE name = ?').get(name) as { id: number } | null;
      if (existing) {
        this.db.run('DELETE FROM graphs WHERE id = ?', [existing.id]);
      }

      // 插入图谱元数据
      this.db.run(
        `INSERT INTO graphs (name, created_at, updated_at, source_reviews, total_concepts, total_papers, total_relations)
         VALUES (?, ?, ?, ?, ?, ?, ?)`,
        [
          name,
          graph.graphMetadata?.createdAt || now,
          now,
          JSON.stringify(sourceReviews),
          graph.nodes.length,
          graph.literatureIndex?.papers.size || 0,
          graph.edges.length
        ]
      );

      const graphId = (this.db.query('SELECT last_insert_rowid() as id').get() as { id: number }).id;

      // 插入节点
      const insertNode = this.db.prepare(
        `INSERT INTO nodes (id, graph_id, label, category, importance, description, definitions, key_papers, metadata)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
      );
      for (const node of graph.nodes) {
        insertNode.run(
          node.id,
          graphId,
          node.label,
          node.category,
          node.importance,
          node.description || null,
          node.definitions ? JSON.stringify(node.definitions) : null,
          node.keyPapers ? JSON.stringify(node.keyPapers) : null,
          node.metadata ? JSON.stringify(node.metadata) : null
        );
      }

      // 插入边
      const insertEdge = this.db.prepare(
        `INSERT INTO edges (graph_id, source, target, relation, label)
         VALUES (?, ?, ?, ?, ?)`
      );
      for (const edge of graph.edges) {
        insertEdge.run(graphId, edge.source, edge.target, edge.relation, edge.label || null);
      }

      // 插入文献
      if (graph.literatureIndex) {
        const insertPaper = this.db.prepare(
          `INSERT INTO papers (id, graph_id, title, authors, abstract, publish_date, url, pdf_url, citations, paper_type, keywords, metadata)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
        );
        for (const [paperId, paper] of graph.literatureIndex.papers) {
          insertPaper.run(
            paperId,
            graphId,
            paper.title,
            JSON.stringify(paper.authors),
            paper.abstract || null,
            paper.publishDate || null,
            paper.url || null,
            paper.pdfUrl || null,
            paper.citations || null,
            paper.paperType || null,
            JSON.stringify(paper.keywords || []),
            paper.metadata ? JSON.stringify(paper.metadata) : null
          );
        }
      }

      // 插入索引
      if (graph.conceptIndex) {
        const insertIndex = this.db.prepare(
          `INSERT INTO concept_paper_index (graph_id, concept_id, paper_id, relevance, mention_type, mention_contexts, indexed_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)`
        );
        for (const [conceptId, refs] of graph.conceptIndex.conceptToPapers) {
          for (const ref of refs) {
            insertIndex.run(
              graphId,
              conceptId,
              ref.paperId,
              ref.relevance,
              ref.mentionType,
              JSON.stringify(ref.contexts || []),
              now
            );
          }
        }
      }
    });

    saveTransaction();
  }

  /**
   * 加载图谱
   */
  loadGraph(name: string): KnowledgeGraphData | null {
    const graphRow = this.db.query('SELECT * FROM graphs WHERE name = ?').get(name) as Record<string, any> | null;
    if (!graphRow) return null;

    const graphId = graphRow.id;

    // 加载节点
    const nodeRows = this.db.query('SELECT * FROM nodes WHERE graph_id = ?').all(graphId) as Record<string, any>[];
    const nodes: KnowledgeNode[] = nodeRows.map(row => ({
      id: row.id,
      label: row.label,
      category: row.category,
      importance: row.importance,
      description: row.description || undefined,
      definitions: row.definitions ? JSON.parse(row.definitions) : undefined,
      keyPapers: row.key_papers ? JSON.parse(row.key_papers) : undefined,
      metadata: row.metadata ? JSON.parse(row.metadata) : undefined,
      literatureReferences: []
    }));

    // 加载边
    const edgeRows = this.db.query('SELECT * FROM edges WHERE graph_id = ?').all(graphId) as Record<string, any>[];
    const edges: KnowledgeEdge[] = edgeRows.map(row => ({
      source: row.source,
      target: row.target,
      relation: row.relation,
      label: row.label || undefined
    }));

    // 加载文献
    const paperRows = this.db.query('SELECT * FROM papers WHERE graph_id = ?').all(graphId) as Record<string, any>[];
    const papers = new Map<string, PaperMetadata>();
    for (const row of paperRows) {
      papers.set(row.id, {
        id: row.id,
        title: row.title,
        authors: row.authors ? JSON.parse(row.authors) : [],
        abstract: row.abstract || '',
        publishDate: row.publish_date || '',
        url: row.url || '',
        pdfUrl: row.pdf_url || undefined,
        citations: row.citations || undefined,
        paperType: row.paper_type || 'research',
        keywords: row.keywords ? JSON.parse(row.keywords) : [],
        metadata: row.metadata ? JSON.parse(row.metadata) : undefined
      });
    }

    // 加载索引
    const indexRows = this.db.query('SELECT * FROM concept_paper_index WHERE graph_id = ?').all(graphId) as Record<string, any>[];

    const conceptToPapers = new Map<string, LiteratureReference[]>();
    const paperToConcepts = new Map<string, string[]>();

    for (const row of indexRows) {
      // 概念→论文
      const refs = conceptToPapers.get(row.concept_id) || [];
      refs.push({
        paperId: row.paper_id,
        title: papers.get(row.paper_id)?.title || '',
        relevance: row.relevance,
        mentionType: row.mention_type || 'foundational',
        contexts: row.mention_contexts ? JSON.parse(row.mention_contexts) : []
      });
      conceptToPapers.set(row.concept_id, refs);

      // 论文→概念
      const concepts = paperToConcepts.get(row.paper_id) || [];
      if (!concepts.includes(row.concept_id)) {
        concepts.push(row.concept_id);
        paperToConcepts.set(row.paper_id, concepts);
      }
    }

    // 设置节点的 literatureReferences
    for (const node of nodes) {
      node.literatureReferences = conceptToPapers.get(node.id) || [];
    }

    // 构建聚类
    const clusters = new Map<string, string[]>();
    for (const category of ['foundation', 'core', 'advanced', 'application']) {
      const categoryNodes = nodes.filter(n => n.category === category).map(n => n.id);
      if (categoryNodes.length > 0) {
        clusters.set(category, categoryNodes);
      }
    }

    return {
      nodes,
      edges,
      clusters,
      literatureIndex: { papers, paperToConcepts },
      conceptIndex: { conceptToPapers },
      graphMetadata: {
        name,
        createdAt: graphRow.created_at,
        updatedAt: graphRow.updated_at,
        sourceReviews: graphRow.source_reviews ? JSON.parse(graphRow.source_reviews) : [],
        totalConcepts: graphRow.total_concepts,
        totalPapers: graphRow.total_papers,
        totalRelations: graphRow.total_relations
      }
    };
  }

  /**
   * 列出所有图谱
   */
  listGraphs(): GraphMetadata[] {
    const rows = this.db.query('SELECT * FROM graphs ORDER BY updated_at DESC').all() as Record<string, any>[];
    return rows.map(row => ({
      name: row.name,
      createdAt: row.created_at,
      updatedAt: row.updated_at,
      sourceReviews: row.source_reviews ? JSON.parse(row.source_reviews) : [],
      totalConcepts: row.total_concepts,
      totalPapers: row.total_papers,
      totalRelations: row.total_relations
    }));
  }

  /**
   * 删除图谱
   */
  deleteGraph(name: string): boolean {
    const result = this.db.run('DELETE FROM graphs WHERE name = ?', [name]);
    return result.changes > 0;
  }

  /**
   * 检查图谱是否存在
   */
  graphExists(name: string): boolean {
    const row = this.db.query('SELECT 1 FROM graphs WHERE name = ?').get(name);
    return row !== null;
  }

  /**
   * 通过SQL查询概念关联的论文（高性能）
   */
  queryPapersByConcept(
    graphName: string,
    conceptLabel: string,
    options: { minRelevance?: number; limit?: number; paperType?: string; sortBy?: string } = {}
  ): Array<PaperMetadata & { relevance: number; mentionType: string }> {
    const { minRelevance = 0, limit = 10, paperType, sortBy = 'relevance' } = options;

    let orderClause: string;
    switch (sortBy) {
      case 'citations': orderClause = 'p.citations DESC'; break;
      case 'date': orderClause = 'p.publish_date DESC'; break;
      default: orderClause = 'cpi.relevance DESC'; break;
    }

    let query = `
      SELECT p.*, cpi.relevance, cpi.mention_type
      FROM papers p
      JOIN concept_paper_index cpi ON p.id = cpi.paper_id AND p.graph_id = cpi.graph_id
      JOIN nodes n ON cpi.concept_id = n.id AND cpi.graph_id = n.graph_id
      JOIN graphs g ON g.id = p.graph_id
      WHERE g.name = ? AND n.label = ? AND cpi.relevance >= ?
    `;

    const params: any[] = [graphName, conceptLabel, minRelevance];

    if (paperType && paperType !== 'all') {
      query += ' AND p.paper_type = ?';
      params.push(paperType);
    }

    query += ` ORDER BY ${orderClause} LIMIT ?`;
    params.push(limit);

    const rows = this.db.query(query).all(...params) as Record<string, any>[];

    return rows.map(row => ({
      id: row.id,
      title: row.title,
      authors: row.authors ? JSON.parse(row.authors) : [],
      abstract: row.abstract || '',
      publishDate: row.publish_date || '',
      url: row.url || '',
      pdfUrl: row.pdf_url || undefined,
      citations: row.citations || undefined,
      paperType: row.paper_type || 'research',
      keywords: row.keywords ? JSON.parse(row.keywords) : [],
      relevance: row.relevance,
      mentionType: row.mention_type
    }));
  }

  /**
   * 通过SQL查询论文关联的概念（高性能）
   */
  queryConceptsByPaper(
    graphName: string,
    paperUrl: string
  ): Array<{ id: string; label: string; category: string; importance: number; relevance: number }> {
    const rows = this.db.query(`
      SELECT n.id, n.label, n.category, n.importance, cpi.relevance
      FROM nodes n
      JOIN concept_paper_index cpi ON n.id = cpi.concept_id AND n.graph_id = cpi.graph_id
      JOIN papers p ON cpi.paper_id = p.id AND cpi.graph_id = p.graph_id
      JOIN graphs g ON g.id = n.graph_id
      WHERE g.name = ? AND p.url = ?
      ORDER BY cpi.relevance DESC
    `).all(graphName, paperUrl) as Record<string, any>[];

    return rows.map(row => ({
      id: row.id,
      label: row.label,
      category: row.category,
      importance: row.importance,
      relevance: row.relevance
    }));
  }

  /**
   * 关闭数据库
   */
  close(): void {
    this.db.close();
  }
}
