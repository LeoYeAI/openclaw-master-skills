/**
 * Progress Tracker - Type Definitions
 * 进展追踪器类型定义
 */

export interface WatchConfig {
  id: string;
  type: 'keyword' | 'author' | 'conference' | 'institution';
  value: string;
  frequency: 'daily' | 'weekly' | 'monthly';
  filters?: WatchFilters;
  active: boolean;
  createdAt: string;
  lastChecked?: string;
}

export interface WatchFilters {
  minCitations?: number;
  sources?: string[];
  categories?: string[];
  yearRange?: [number, number];
}

export interface TrackerSettings {
  maxResultsPerWatch: number;
  enableNotifications: boolean;
  reportSchedule: {
    daily: string;
    weekly: string;
    monthly: string;
  };
}

export interface ProgressReport {
  reportType: 'daily' | 'weekly' | 'monthly';
  period: {
    start: string;
    end: string;
  };
  summary: ReportSummary;
  papers: PaperUpdate[];
  trending: TrendingTopic[];
  recommendations: PaperRecommendation[];
  generatedAt: string;
}

export interface ReportSummary {
  totalPapers: number;
  highlightedPapers: number;
  newKeywords: string[];
  trendingTopics: string[];
  watchStats: {
    watchId: string;
    watchValue: string;
    matchCount: number;
  }[];
}

export interface PaperUpdate {
  id: string;
  title: string;
  authors: string[];
  publishDate: string;
  source: string;
  url: string;
  abstract?: string;
  keywords: string[];
  matchedWatches: string[];
  relevanceScore: number;
  importance: 'high' | 'medium' | 'low';
  summary?: string;
  citations?: number;
}

export interface TrendingTopic {
  topic: string;
  paperCount: number;
  changePercent: number;
  keyPapers: string[];
  trend: 'rising' | 'stable' | 'declining';
}

export interface PaperRecommendation {
  paper: PaperUpdate;
  reason: string;
  priority: number;
}

export interface UpdateOptions {
  since?: string;
  limit?: number;
  watchIds?: string[];
}

export interface ReportOptions {
  type: 'daily' | 'weekly' | 'monthly';
  includeSummaries?: boolean;
  highlightImportant?: boolean;
  topic?: string;
}

export interface TrendAnalysis {
  topic: string;
  timeframe: 'week' | 'month' | 'quarter';
  paperCount: number;
  previousCount: number;
  changePercent: number;
  topPapers: PaperUpdate[];
  emergingKeywords: string[];
  decliningKeywords: string[];
}

export interface WatchHistory {
  watchId: string;
  timestamp: string;
  papersFound: number;
  papers: PaperUpdate[];
}
