/**
 * Complementary Search Strategy
 * 互补搜索策略 - 根据查询自动选择最优数据源组合
 */

import type { SearchSource } from '../../shared/types';
import type { SearchSourceRegistry } from './adapters/registry';

/** Domain detection keywords */
const DOMAIN_KEYWORDS: Record<string, string[]> = {
  biomedical: [
    'gene', 'protein', 'genome', 'clinical', 'drug', 'disease', 'medical',
    'surgery', 'patient', 'therapy', 'cancer', 'cell', 'dna', 'rna',
    'molecular', 'biology', 'pathology', 'neuroscience', 'brain',
    'pharmaceutical', 'crispr', 'biomarker', 'epidemiology', 'virus',
    'vaccine', 'immune', 'metabol', 'cardio', 'oncology',
    '基因', '蛋白质', '临床', '药物', '疾病', '细胞', '分子', '生物'
  ],
  cs: [
    'algorithm', 'neural network', 'deep learning', 'machine learning',
    'transformer', 'nlp', 'computer vision', 'natural language', 'software',
    'compiler', 'database', 'distributed', 'operating system', 'gpu',
    'reinforcement learning', 'generative', 'llm', 'language model',
    'attention mechanism', 'bert', 'gpt', 'convolutional', 'recurrent',
    'classification', 'segmentation', 'object detection',
    '算法', '神经网络', '深度学习', '机器学习', '自然语言'
  ],
  engineering: [
    'circuit', 'signal processing', 'antenna', 'semiconductor', 'vlsi',
    'embedded', 'control system', 'robotics', 'sensor', 'actuator',
    'power electronics', 'communication system', 'wireless', '5g', '6g',
    'iot', 'fpga', 'microprocessor', 'rf',
    '电路', '信号处理', '半导体', '传感器', '机器人'
  ],
  physics: [
    'quantum', 'particle', 'cosmology', 'astrophysics', 'condensed matter',
    'gravitational', 'photon', 'dark matter', 'dark energy', 'superconductor',
    'plasma', 'relativity', 'boson', 'fermion', 'higgs', 'string theory',
    'thermodynamics', 'optics', 'laser', 'nuclear',
    '量子', '粒子', '宇宙', '凝聚态', '光学'
  ]
};

/** Default priority order */
const DEFAULT_PRIORITY: SearchSource[] = [
  'semantic_scholar', 'openalex', 'arxiv', 'pubmed',
  'crossref', 'dblp', 'core', 'ieee', 'web'
];

/** Domain-specific priority orders */
const DOMAIN_PRIORITIES: Record<string, SearchSource[]> = {
  biomedical: ['pubmed', 'semantic_scholar', 'openalex', 'crossref'],
  cs: ['semantic_scholar', 'arxiv', 'dblp', 'openalex'],
  engineering: ['ieee', 'semantic_scholar', 'openalex', 'crossref'],
  physics: ['arxiv', 'semantic_scholar', 'openalex'],
  general: ['semantic_scholar', 'openalex', 'crossref', 'arxiv']
};

export interface StrategyConfig {
  defaultPriority?: SearchSource[];
  domainPriorities?: Record<string, SearchSource[]>;
  maxConcurrentSources?: number;
  useComplementaryStrategy?: boolean;
}

export class ComplementarySearchStrategy {
  private config: Required<StrategyConfig>;

  constructor(config?: StrategyConfig) {
    this.config = {
      defaultPriority: config?.defaultPriority || DEFAULT_PRIORITY,
      domainPriorities: config?.domainPriorities || DOMAIN_PRIORITIES,
      maxConcurrentSources: config?.maxConcurrentSources || 4,
      useComplementaryStrategy: config?.useComplementaryStrategy ?? true
    };
  }

  /**
   * Detect academic domain from query keywords
   */
  detectDomain(query: string): string {
    const lowerQuery = query.toLowerCase();

    const scores: Record<string, number> = {};
    for (const [domain, keywords] of Object.entries(DOMAIN_KEYWORDS)) {
      scores[domain] = keywords.filter(kw => lowerQuery.includes(kw)).length;
    }

    // Find domain with highest score
    let bestDomain = 'general';
    let bestScore = 0;
    for (const [domain, score] of Object.entries(scores)) {
      if (score > bestScore) {
        bestScore = score;
        bestDomain = domain;
      }
    }

    return bestScore > 0 ? bestDomain : 'general';
  }

  /**
   * Select optimal sources for a query
   */
  selectSources(
    query: string,
    registry: SearchSourceRegistry,
    domainHint?: string
  ): SearchSource[] {
    if (!this.config.useComplementaryStrategy) {
      return this.config.defaultPriority
        .filter(s => registry.isAvailable(s))
        .slice(0, this.config.maxConcurrentSources);
    }

    const domain = domainHint || this.detectDomain(query);
    const priority = this.config.domainPriorities[domain] || this.config.defaultPriority;

    const selected: SearchSource[] = [];
    const usedIds = new Set<SearchSource>();

    // 1. Add sources from domain priority list
    for (const sourceId of priority) {
      if (selected.length >= this.config.maxConcurrentSources) break;
      if (registry.isAvailable(sourceId) && !usedIds.has(sourceId)) {
        selected.push(sourceId);
        usedIds.add(sourceId);
      }
    }

    // 2. Fill remaining slots from default priority
    if (selected.length < this.config.maxConcurrentSources) {
      for (const sourceId of this.config.defaultPriority) {
        if (selected.length >= this.config.maxConcurrentSources) break;
        if (registry.isAvailable(sourceId) && !usedIds.has(sourceId)) {
          selected.push(sourceId);
          usedIds.add(sourceId);
        }
      }
    }

    return selected;
  }

  /**
   * Get the detected or hinted domain for display
   */
  getDomainInfo(query: string, domainHint?: string): { domain: string; isHinted: boolean } {
    if (domainHint) {
      return { domain: domainHint, isHinted: true };
    }
    return { domain: this.detectDomain(query), isHinted: false };
  }
}
