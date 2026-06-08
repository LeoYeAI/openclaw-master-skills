/**
 * Knowledge Gap Detector - Type Definitions
 * 知识盲区检测器类型定义
 */

export interface DetectOptions {
  domain: string;
  knownConcepts: string[];
  targetLevel?: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  focusAreas?: string[];
  excludeConcepts?: string[];
}

export interface ProfileBasedOptions {
  profilePath: string;
  domain: string;
}

export interface LearningPathAnalysisOptions {
  currentPath: string[];
  targetRole: string;
  industry?: string;
}

export interface CrossDisciplinaryOptions {
  primaryDomain: string;
  relatedDomains: string[];
  knownConcepts?: string[];
}

export interface GapReport {
  domain: string;
  analysisDate: string;
  summary: GapSummary;
  criticalGaps: KnowledgeGap[];
  recommendedGaps: KnowledgeGap[];
  optionalGaps: KnowledgeGap[];
  crossDisciplinary: KnowledgeGap[];
  emergingTopics: KnowledgeGap[];
  suggestedOrder: string[];
  estimatedEffort: EstimatedEffort;
}

export interface GapSummary {
  totalGaps: number;
  criticalCount: number;
  recommendedCount: number;
  optionalCount: number;
  coveragePercentage: number;
}

export interface KnowledgeGap {
  concept: string;
  category: 'critical' | 'recommended' | 'optional' | 'cross-disciplinary' | 'emerging';
  reason: string;
  importance: 1 | 2 | 3 | 4 | 5;
  prerequisites: string[];
  relatedKnown: string[];
  resources: LearningResource[];
  estimatedTime: string;
  impactIfLearned: string;
}

export interface LearningResource {
  type: 'paper' | 'tutorial' | 'course' | 'book' | 'documentation';
  title: string;
  url?: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
}

export interface EstimatedEffort {
  critical: string;
  recommended: string;
  total: string;
}

export interface KnowledgeProfile {
  domain: string;
  knownConcepts: string[];
  skillLevel: Record<string, 'beginner' | 'intermediate' | 'advanced'>;
  learningGoals: string[];
  lastUpdated: string;
}

export interface DomainConcept {
  name: string;
  importance: number;
  prerequisites: string[];
  related: string[];
  category: 'foundation' | 'core' | 'advanced' | 'emerging';
  description: string;
}

export interface CitationBasedGap {
  paperTitle: string;
  missingConcepts: string[];
  relevance: number;
}
