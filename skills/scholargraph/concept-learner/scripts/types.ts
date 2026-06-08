/**
 * Concept Learner - Type Definitions
 * 概念学习器类型定义
 */

export interface LearnOptions {
  depth?: 'beginner' | 'intermediate' | 'advanced';
  includePapers?: boolean;
  includeCode?: boolean;
  language?: 'zh-CN' | 'en-US';
  focusAreas?: string[];
}

export interface ConceptCard {
  concept: string;
  definition: string;
  shortExplanation: string;
  coreComponents: CoreComponent[];
  history: ConceptHistory;
  applications: Application[];
  relatedConcepts: RelatedConcept[];
  learningPath: LearningStage[];
  resources: LearningResource[];
  keyPapers?: Paper[];
  codeExamples?: CodeExample[];
  generatedAt: string;
}

export interface CoreComponent {
  name: string;
  description: string;
  importance: 'high' | 'medium' | 'low';
}

export interface ConceptHistory {
  origin: string;
  keyDevelopments: KeyDevelopment[];
  currentStatus: string;
}

export interface KeyDevelopment {
  year: string;
  event: string;
  significance: string;
}

export interface Application {
  domain: string;
  examples: string[];
  impact: string;
}

export interface RelatedConcept {
  concept: string;
  relationship: 'prerequisite' | 'related' | 'derived' | 'alternative';
  briefExplanation: string;
}

export interface LearningStage {
  stage: string;
  concepts: string[];
  estimatedTime: string;
  resources: string[];
}

export interface LearningResource {
  type: 'paper' | 'tutorial' | 'course' | 'book' | 'code';
  title: string;
  url?: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
}

export interface Paper {
  title: string;
  authors: string[];
  year: string;
  venue?: string;
  url?: string;
  summary: string;
}

export interface CodeExample {
  title: string;
  description: string;
  language: string;
  code: string;
  source?: string;
}

export interface ComparisonResult {
  concept1: string;
  concept2: string;
  similarities: string[];
  differences: string[];
  useCases: {
    preferConcept1: string[];
    preferConcept2: string[];
  };
  relationshipDiagram?: string;
}

export interface LearningPathPlan {
  topic: string;
  currentLevel: string;
  targetLevel: string;
  estimatedDuration: string;
  stages: LearningStage[];
  milestones: string[];
  recommendedOrder: string[];
}
