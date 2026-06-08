/**
 * Paper Visualization & Graph Visualization Unit Tests
 * 论文可视化 + 交互式图谱模块单元测试
 */

import { describe, test, expect } from 'bun:test';
import { SlideBuilder } from '../paper-viz/scripts/slide-builder';
import { generatePaperHtml } from '../paper-viz/scripts/html-generator';
import { ACADEMIC_DARK_THEME, ACADEMIC_LIGHT_THEME } from '../paper-viz/scripts/types';
import { GraphDataAdapter } from '../graph-viz/scripts/graph-data-adapter';
import { PaperVizBridge } from '../graph-viz/scripts/paper-viz-bridge';
import { generateGraphHtml } from '../graph-viz/scripts/html-generator';
import {
  validatePaperVizParams,
  validateGraphInteractiveParams,
} from '../shared/validators';
import type { PaperAnalysis } from '../paper-analyzer/scripts/types';

// ==================== Mock Data ====================

function mockAnalysis(): PaperAnalysis {
  return {
    metadata: {
      title: 'Attention Is All You Need',
      authors: ['Vaswani, A.', 'Shazeer, N.', 'Parmar, N.'],
      venue: 'NeurIPS 2017',
      year: '2017',
      doi: '10.5555/3295222.3295349',
      arxivId: '1706.03762',
      url: 'https://arxiv.org/abs/1706.03762',
      keywords: ['transformer', 'attention', 'NLP'],
    },
    abstract: 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.',
    summary: 'This paper proposes the Transformer architecture based entirely on attention mechanisms.',
    keyPoints: [
      { point: 'Self-attention mechanism', importance: 'critical', location: 'Section 3', explanation: 'Replaces recurrence with attention' },
      { point: 'Multi-head attention', importance: 'important', location: 'Section 3.2', explanation: 'Allows attending to different subspaces' },
      { point: 'Positional encoding', importance: 'supporting', location: 'Section 3.5', explanation: 'Injects sequence order information' },
      { point: 'Layer normalization', importance: 'supporting', location: 'Section 3.1', explanation: 'Stabilizes training' },
      { point: 'Feed-forward networks', importance: 'supporting', location: 'Section 3.3', explanation: 'Point-wise fully connected layers' },
    ],
    methodology: {
      overview: 'Encoder-decoder architecture using self-attention',
      approach: 'Pure attention-based model without recurrence',
      novelty: 'First model to rely entirely on self-attention',
      assumptions: ['Parallel computation is available'],
      strengths: ['Parallelizable', 'Long-range dependencies'],
      weaknesses: ['Quadratic memory complexity'],
    },
    experiments: {
      datasets: ['WMT 2014 EN-DE', 'WMT 2014 EN-FR'],
      metrics: ['BLEU'],
      baselines: ['ConvS2S', 'GNMT'],
      mainResults: 'Achieved 28.4 BLEU on EN-DE, 41.0 on EN-FR',
      ablations: ['Attention head count', 'Model dimension'],
      analysis: 'Performance scales with model size',
    },
    contributions: [
      { description: 'Transformer architecture', type: 'methodological', significance: 'major' },
      { description: 'Multi-head attention', type: 'methodological', significance: 'major' },
    ],
    limitations: [
      { description: 'Quadratic complexity with sequence length', impact: 'high', potentialSolution: 'Sparse attention' },
    ],
    futureWork: ['Apply to other domains', 'Reduce memory requirements'],
    citations: { keyReferences: ['Bahdanau et al. 2014'], citationCount: 100000 },
    relatedWork: [
      { category: 'Sequence Models', papers: ['LSTM', 'GRU'], comparison: 'Transformer avoids recurrence' },
    ],
    reproducibility: { score: 90, codeAvailable: true, datasetAvailable: true, detailsAvailable: true, notes: 'Highly reproducible' },
    recommendations: { forResearchers: ['Study attention patterns'], forPractitioners: ['Use pre-trained models'], furtherReading: ['BERT', 'GPT'] },
    generatedAt: '2024-01-01T00:00:00Z',
  };
}

function mockGraph() {
  return {
    nodes: [
      { id: 'n0', label: 'Transformer', category: 'foundation' as const, importance: 5, description: 'Architecture',
        literatureReferences: [
          { paperId: 'p1', title: 'Attention', relevance: 0.95, mentionType: 'foundational' as const, contexts: [] },
          { paperId: 'p2', title: 'BERT', relevance: 0.8, mentionType: 'application' as const, contexts: [] },
        ], keyPapers: ['p1', 'p2'] },
      { id: 'n1', label: 'Self-Attention', category: 'core' as const, importance: 4,
        literatureReferences: [
          { paperId: 'p1', title: 'Attention', relevance: 0.9, mentionType: 'foundational' as const, contexts: [] },
        ] },
      { id: 'n2', label: 'BERT', category: 'application' as const, importance: 4, literatureReferences: [] },
      { id: 'n3', label: 'Positional Encoding', category: 'advanced' as const, importance: 3 },
    ],
    edges: [
      { source: 'n0', target: 'n1', relation: 'component' as const },
      { source: 'n0', target: 'n2', relation: 'prerequisite' as const },
      { source: 'n1', target: 'n2', relation: 'derived' as const },
      { source: 'n0', target: 'n3', relation: 'related' as const },
    ],
    clusters: new Map<string, string[]>(),
    literatureIndex: {
      papers: new Map([
        ['p1', { id: 'p1', title: 'Attention Is All You Need', authors: ['Vaswani'], abstract: 'Transformer paper.', publishDate: '2017', url: 'https://arxiv.org/abs/1706.03762', paperType: 'research' as const, keywords: [] }],
        ['p2', { id: 'p2', title: 'BERT', authors: ['Devlin'], abstract: 'BERT paper.', publishDate: '2018', url: 'https://arxiv.org/abs/1810.04805', citations: 50000, paperType: 'research' as const, keywords: [] }],
      ]),
      paperToConcepts: new Map([['p1', ['n0', 'n1']], ['p2', ['n0', 'n2']]]),
    },
    conceptIndex: {
      conceptToPapers: new Map([
        ['n0', [
          { paperId: 'p1', title: 'Attention', relevance: 0.95, mentionType: 'foundational' as const, contexts: [] },
          { paperId: 'p2', title: 'BERT', relevance: 0.8, mentionType: 'application' as const, contexts: [] },
        ]],
        ['n1', [
          { paperId: 'p1', title: 'Attention', relevance: 0.9, mentionType: 'foundational' as const, contexts: [] },
        ]],
      ]),
    },
    graphMetadata: { name: 'test-graph', createdAt: '2024-01-01', updatedAt: '2024-01-01', sourceReviews: [], totalConcepts: 4, totalPapers: 2, totalRelations: 4 },
  };
}

// ==================== SlideBuilder ====================

describe('SlideBuilder', () => {
  test('generates correct slide types in order', () => {
    const pres = new SlideBuilder().buildFromAnalysis(mockAnalysis());
    const types = pres.slides.map(s => s.type);
    expect(types[0]).toBe('title');
    expect(types[1]).toBe('abstract');
    expect(types.includes('key-points')).toBe(true);
    expect(types.includes('methodology')).toBe(true);
    expect(types.includes('experiments')).toBe(true);
    expect(types.includes('contributions')).toBe(true);
    expect(types.includes('limitations')).toBe(true);
    expect(types.includes('references')).toBe(true);
  });

  test('generates 8+ slides for complete analysis', () => {
    const pres = new SlideBuilder().buildFromAnalysis(mockAnalysis());
    expect(pres.slides.length).toBeGreaterThanOrEqual(8);
  });

  test('title slide has center layout', () => {
    const pres = new SlideBuilder().buildFromAnalysis(mockAnalysis());
    expect(pres.slides[0].layout).toBe('center');
  });

  test('splits key points when exceeding maxPointsPerSlide', () => {
    const pres = new SlideBuilder({ maxPointsPerSlide: 3 }).buildFromAnalysis(mockAnalysis());
    const kpSlides = pres.slides.filter(s => s.type === 'key-points');
    expect(kpSlides.length).toBe(2);
  });

  test('excludes references when disabled', () => {
    const pres = new SlideBuilder({ includeReferences: false }).buildFromAnalysis(mockAnalysis());
    expect(pres.slides.filter(s => s.type === 'references').length).toBe(0);
  });

  test('sets correct metadata on presentation', () => {
    const pres = new SlideBuilder().buildFromAnalysis(mockAnalysis());
    expect(pres.title).toBe('Attention Is All You Need');
    expect(pres.authors).toEqual(['Vaswani, A.', 'Shazeer, N.', 'Parmar, N.']);
    expect(pres.url).toBe('https://arxiv.org/abs/1706.03762');
    expect(pres.date).toBe('2017');
  });

  test('uses specified theme', () => {
    const pres = new SlideBuilder({ theme: ACADEMIC_LIGHT_THEME }).buildFromAnalysis(mockAnalysis());
    expect(pres.theme.name).toBe('Academic Light');
    expect(pres.theme.backgroundColor).toBe('#FFFFFF');
  });

  test('handles empty keyPoints gracefully', () => {
    const a = mockAnalysis();
    a.keyPoints = [];
    const pres = new SlideBuilder().buildFromAnalysis(a);
    const kp = pres.slides.filter(s => s.type === 'key-points');
    expect(kp.length).toBe(1);
    expect(kp[0].blocks[0].content).toContain('No key points');
  });

  test('each slide has unique id', () => {
    const pres = new SlideBuilder().buildFromAnalysis(mockAnalysis());
    const ids = pres.slides.map(s => s.id);
    expect(new Set(ids).size).toBe(ids.length);
  });
});

// ==================== HTML Generator (paper-viz) ====================

describe('generatePaperHtml', () => {
  test('generates valid HTML document', () => {
    const pres = new SlideBuilder().buildFromAnalysis(mockAnalysis());
    const html = generatePaperHtml(pres);
    expect(html).toContain('<!DOCTYPE html>');
    expect(html).toContain('</html>');
  });

  test('contains slide sections with type attributes', () => {
    const pres = new SlideBuilder().buildFromAnalysis(mockAnalysis());
    const html = generatePaperHtml(pres);
    expect(html).toContain('data-type="title"');
    expect(html).toContain('data-type="abstract"');
    expect(html).toContain('data-type="methodology"');
  });

  test('contains CSS variables from theme', () => {
    const pres = new SlideBuilder().buildFromAnalysis(mockAnalysis());
    const html = generatePaperHtml(pres);
    expect(html).toContain('--primary: #60A5FA');
    expect(html).toContain('--bg: #0F172A');
  });

  test('contains navigation and edit UI', () => {
    const pres = new SlideBuilder().buildFromAnalysis(mockAnalysis());
    const html = generatePaperHtml(pres);
    expect(html).toContain('nav-dots');
    expect(html).toContain('slideCounter');
    expect(html).toContain('editIndicator');
  });

  test('contains paper link', () => {
    const pres = new SlideBuilder().buildFromAnalysis(mockAnalysis());
    const html = generatePaperHtml(pres);
    expect(html).toContain('paper-link');
    expect(html).toContain('arxiv.org');
  });

  test('escapes HTML in content', () => {
    const a = mockAnalysis();
    a.metadata.title = 'Test <script>alert("xss")</script>';
    const pres = new SlideBuilder().buildFromAnalysis(a);
    const html = generatePaperHtml(pres);
    expect(html).not.toContain('<script>alert');
    expect(html).toContain('&lt;script&gt;');
  });
});

// ==================== GraphDataAdapter ====================

describe('GraphDataAdapter', () => {
  describe('computeRadius', () => {
    test('0 papers → radius 15', () => {
      expect(GraphDataAdapter.computeRadius(0)).toBe(15);
    });

    test('1 paper → radius 23', () => {
      expect(GraphDataAdapter.computeRadius(1)).toBe(23);
    });

    test('25 papers → radius ~55', () => {
      expect(GraphDataAdapter.computeRadius(25)).toBeCloseTo(55, 0);
    });

    test('100 papers → radius 60 (capped)', () => {
      expect(GraphDataAdapter.computeRadius(100)).toBe(60);
    });

    test('400 papers → still 60 (capped)', () => {
      expect(GraphDataAdapter.computeRadius(400)).toBe(60);
    });
  });

  describe('computeStrokeWidth', () => {
    test('prerequisite + 0 shared → 3', () => {
      expect(GraphDataAdapter.computeStrokeWidth('prerequisite', 0)).toBe(3);
    });

    test('related + 3 shared → 2.5', () => {
      expect(GraphDataAdapter.computeStrokeWidth('related', 3)).toBe(2.5);
    });

    test('prerequisite + 20 shared → 8 (capped)', () => {
      expect(GraphDataAdapter.computeStrokeWidth('prerequisite', 20)).toBe(8);
    });

    test('related + 0 shared → 1', () => {
      expect(GraphDataAdapter.computeStrokeWidth('related', 0)).toBe(1);
    });

    test('derived + 0 shared → 2.5', () => {
      expect(GraphDataAdapter.computeStrokeWidth('derived', 0)).toBe(2.5);
    });

    test('component + 0 shared → 2', () => {
      expect(GraphDataAdapter.computeStrokeWidth('component', 0)).toBe(2);
    });
  });

  describe('convert', () => {
    test('converts all nodes and edges', () => {
      const d3 = new GraphDataAdapter().convert(mockGraph());
      expect(d3.nodes.length).toBe(4);
      expect(d3.edges.length).toBe(4);
    });

    test('assigns correct category colors', () => {
      const d3 = new GraphDataAdapter().convert(mockGraph());
      expect(d3.nodes.find(n => n.label === 'Transformer')?.color).toBe('#4FC3F7');
      expect(d3.nodes.find(n => n.label === 'Self-Attention')?.color).toBe('#FFB74D');
      expect(d3.nodes.find(n => n.label === 'BERT')?.color).toBe('#81C784');
      expect(d3.nodes.find(n => n.label === 'Positional Encoding')?.color).toBe('#CE93D8');
    });

    test('computes paper counts from literatureReferences', () => {
      const d3 = new GraphDataAdapter().convert(mockGraph());
      expect(d3.nodes.find(n => n.label === 'Transformer')?.paperCount).toBe(2);
      expect(d3.nodes.find(n => n.label === 'Self-Attention')?.paperCount).toBe(1);
      expect(d3.nodes.find(n => n.label === 'BERT')?.paperCount).toBe(0);
    });

    test('sets metadata', () => {
      const d3 = new GraphDataAdapter().convert(mockGraph());
      expect(d3.metadata.name).toBe('test-graph');
      expect(d3.metadata.totalNodes).toBe(4);
      expect(d3.metadata.totalEdges).toBe(4);
      expect(d3.metadata.totalPapers).toBe(2);
    });

    test('edge styles match relation types', () => {
      const d3 = new GraphDataAdapter().convert(mockGraph());
      const prereq = d3.edges.find(e => e.relation === 'prerequisite');
      expect(prereq?.style.color).toBe('#EF5350');
      expect(prereq?.style.dasharray).toBe('');

      const derived = d3.edges.find(e => e.relation === 'derived');
      expect(derived?.style.color).toBe('#AB47BC');
      expect(derived?.style.dasharray).toBe('8 4');
    });

    test('handles graph without conceptIndex', () => {
      const g = mockGraph();
      (g as any).conceptIndex = undefined;
      const d3 = new GraphDataAdapter().convert(g);
      expect(d3.nodes.length).toBe(4);
    });
  });
});

// ==================== PaperVizBridge ====================

describe('PaperVizBridge', () => {
  test('builds payloads for nodes with papers', () => {
    const payload = new PaperVizBridge().buildAllPaperPayloads(mockGraph());
    expect(Object.keys(payload)).toContain('n0');
    expect(Object.keys(payload)).toContain('n1');
  });

  test('n0 has 2 papers sorted by relevance', () => {
    const payload = new PaperVizBridge().buildAllPaperPayloads(mockGraph());
    expect(payload['n0'].length).toBe(2);
    expect(payload['n0'][0].relevance).toBeGreaterThanOrEqual(payload['n0'][1].relevance);
  });

  test('excludes nodes with no papers', () => {
    const payload = new PaperVizBridge().buildAllPaperPayloads(mockGraph());
    expect(payload['n2']).toBeUndefined();
    expect(payload['n3']).toBeUndefined();
  });

  test('respects minRelevance filter', () => {
    const payload = new PaperVizBridge({ minRelevance: 0.85 }).buildAllPaperPayloads(mockGraph());
    expect(payload['n0'].length).toBe(1);
    expect(payload['n0'][0].id).toBe('p1');
  });

  test('respects maxPapersPerNode', () => {
    const payload = new PaperVizBridge({ maxPapersPerNode: 1 }).buildAllPaperPayloads(mockGraph());
    expect(payload['n0'].length).toBe(1);
  });

  test('truncates abstract', () => {
    const payload = new PaperVizBridge({ abstractMaxLength: 10 }).buildAllPaperPayloads(mockGraph());
    const p = payload['n0'].find(p => p.id === 'p1');
    expect(p!.abstract.length).toBeLessThanOrEqual(13);
    expect(p!.abstract).toContain('...');
  });

  test('paper summary has all required fields', () => {
    const payload = new PaperVizBridge().buildAllPaperPayloads(mockGraph());
    const p = payload['n0'][0];
    expect(p.id).toBeTruthy();
    expect(p.title).toBeTruthy();
    expect(Array.isArray(p.authors)).toBe(true);
    expect(typeof p.relevance).toBe('number');
    expect(typeof p.mentionType).toBe('string');
    expect(typeof p.url).toBe('string');
  });
});

// ==================== Graph HTML Generator ====================

describe('generateGraphHtml', () => {
  test('generates valid HTML with D3 CDN', () => {
    const d3 = new GraphDataAdapter().convert(mockGraph());
    const html = generateGraphHtml(d3);
    expect(html).toContain('<!DOCTYPE html>');
    expect(html).toContain('d3.v7.min.js');
  });

  test('embeds GRAPH_DATA and PAPER_DATA', () => {
    const d3 = new GraphDataAdapter().convert(mockGraph());
    const payload = new PaperVizBridge().buildAllPaperPayloads(mockGraph());
    const html = generateGraphHtml(d3, { includePaperData: true, paperPayload: payload });
    expect(html).toContain('GRAPH_DATA');
    expect(html).toContain('PAPER_DATA');
  });

  test('contains SVG, search, panel, legend', () => {
    const d3 = new GraphDataAdapter().convert(mockGraph());
    const html = generateGraphHtml(d3);
    expect(html).toContain('<svg');
    expect(html).toContain('searchInput');
    expect(html).toContain('panel-content');
    expect(html).toContain('legend');
  });

  test('contains graph title', () => {
    const d3 = new GraphDataAdapter().convert(mockGraph());
    const html = generateGraphHtml(d3);
    expect(html).toContain('test-graph');
  });
});

// ==================== Validators ====================

describe('validatePaperVizParams', () => {
  test('accepts valid params', () => {
    expect(validatePaperVizParams({ url: 'https://arxiv.org/abs/1706.03762', mode: 'deep', theme: 'academic-dark' }).valid).toBe(true);
  });

  test('rejects missing url', () => {
    const r = validatePaperVizParams({});
    expect(r.valid).toBe(false);
    expect(r.errors.some(e => e.field === 'url')).toBe(true);
  });

  test('rejects invalid mode', () => {
    const r = validatePaperVizParams({ url: 'https://example.com', mode: 'turbo' });
    expect(r.valid).toBe(false);
  });

  test('rejects invalid theme', () => {
    const r = validatePaperVizParams({ url: 'https://example.com', theme: 'neon' });
    expect(r.valid).toBe(false);
  });

  test('accepts without optional fields', () => {
    expect(validatePaperVizParams({ url: 'https://example.com' }).valid).toBe(true);
  });
});

describe('validateGraphInteractiveParams', () => {
  test('accepts valid name', () => {
    expect(validateGraphInteractiveParams({ graphName: 'my-graph' }).valid).toBe(true);
  });

  test('rejects missing name', () => {
    expect(validateGraphInteractiveParams({}).valid).toBe(false);
  });

  test('rejects empty name', () => {
    expect(validateGraphInteractiveParams({ graphName: '  ' }).valid).toBe(false);
  });
});
