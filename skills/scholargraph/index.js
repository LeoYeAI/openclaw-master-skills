#!/usr/bin/env node

/**
 * ScholarGraph - Academic Literature Intelligence Toolkit
 * Entry point for the skill
 */

// Re-export all modules for programmatic usage
export { default as LiteratureSearch } from './literature-search/scripts/search.ts';
export { default as ConceptLearner } from './concept-learner/scripts/learn.ts';
export { default as KnowledgeGapDetector } from './knowledge-gap-detector/scripts/detect.ts';
export { default as ProgressTracker } from './progress-tracker/scripts/track.ts';
export { default as PaperAnalyzer } from './paper-analyzer/scripts/analyze.ts';
export { default as KnowledgeGraphBuilder } from './knowledge-graph/scripts/graph.ts';

// Re-export types
export * from './shared/types.ts';

// Re-export configuration
export { ConfigManager, defaultConfig } from './config.ts';

// Main CLI entry point
if (import.meta.main) {
  // Import and run CLI
  await import('./cli.ts');
}
