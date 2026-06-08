/**
 * Paper Analyzer - Type Definitions
 * 论文分析器类型定义
 */

export interface AnalyzeOptions {
  url?: string;
  file?: string;
  text?: string;
  mode?: 'quick' | 'standard' | 'deep';
  depth?: 'quick' | 'standard' | 'deep';
  includeCitations?: boolean;
  includeRelatedWork?: boolean;
  focusAreas?: string[];
  language?: 'zh-CN' | 'en-US';
}

export interface PaperAnalysis {
  metadata: PaperMetadata;
  abstract: string;
  summary: string;
  keyPoints: KeyPoint[];
  methodology: MethodologyAnalysis;
  experiments: ExperimentAnalysis;
  contributions: Contribution[];
  limitations: Limitation[];
  futureWork: string[];
  citations: CitationAnalysis;
  relatedWork: RelatedWork[];
  reproducibility: ReproducibilityAnalysis;
  recommendations: AnalysisRecommendations;
  generatedAt: string;
}

export interface PaperMetadata {
  title: string;
  authors: string[];
  venue?: string;
  year: string;
  doi?: string;
  arxivId?: string;
  url: string;
  keywords: string[];
}

export interface KeyPoint {
  point: string;
  importance: 'critical' | 'important' | 'supporting';
  location: string;
  explanation: string;
}

export interface MethodologyAnalysis {
  overview: string;
  approach: string;
  novelty: string;
  assumptions: string[];
  strengths: string[];
  weaknesses: string[];
}

export interface ExperimentAnalysis {
  datasets: string[];
  metrics: string[];
  baselines: string[];
  mainResults: string;
  ablations: string[];
  analysis: string;
}

export interface Contribution {
  description: string;
  type: 'methodological' | 'empirical' | 'theoretical' | 'dataset' | 'tool';
  significance: 'major' | 'moderate' | 'minor';
}

export interface Limitation {
  description: string;
  impact: 'high' | 'medium' | 'low';
  potentialSolution?: string;
}

export interface CitationAnalysis {
  keyReferences: string[];
  citationCount?: number;
  influentialCitations?: string[];
}

export interface RelatedWork {
  category: string;
  papers: string[];
  comparison: string;
}

export interface ReproducibilityAnalysis {
  score: number;
  codeAvailable: boolean;
  datasetAvailable: boolean;
  detailsAvailable: boolean;
  notes: string;
}

export interface AnalysisRecommendations {
  forResearchers: string[];
  forPractitioners: string[];
  furtherReading: string[];
}

export interface ComparisonResult {
  papers: PaperMetadata[];
  commonThemes: string[];
  differences: string[];
  methodologicalComparison: string;
  performanceComparison: string;
  synthesis: string;
}

export interface CritiqueResult {
  strengths: string[];
  weaknesses: string[];
  gaps: string[];
  suggestions: string[];
  overallAssessment: string;
}
