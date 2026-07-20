#!/usr/bin/env node
/**
 * Semantic Validation Framework
 * 
 * Validates logical consistency between template choice and content structure.
 */

/**
 * Semantic validation rules
 */
const VALIDATION_RULES = {
  flowchart_requires_decisions: {
    template: 'flowchart',
    check: (placeholders) => {
      const hasDecisions = Object.keys(placeholders).some(k => 
        k.includes('DECISION') || k.includes('CHOICE')
      );
      return {
        pass: hasDecisions,
        level: 'WARNING',
        message: hasDecisions ? null : 'Flowchart without DECISION placeholders suggests sequential flow. Consider state-diagram or timeline.',
        suggestion: hasDecisions ? null : {
          templates: ['state-diagram', 'timeline'],
          reason: 'Sequential progression without branching logic'
        }
      };
    }
  },
  
  timeline_requires_events: {
    template: 'timeline',
    check: (placeholders) => {
      const events = Object.keys(placeholders).filter(k => k.startsWith('EVENT'));
      const dates = Object.keys(placeholders).filter(k => k.startsWith('DATE'));
      const match = events.length === dates.length && events.length > 0;
      return {
        pass: match,
        level: 'ERROR',
        message: match ? null : `Timeline has ${events.length} events but ${dates.length} dates.`,
        suggestion: null
      };
    }
  },
  
  architecture_requires_components: {
    template: 'architecture',
    check: (placeholders) => {
      const hasComponents = Object.keys(placeholders).some(k =>
        k.includes('COMPONENT') || k.includes('SYSTEM') || k.includes('EXTERNAL')
      );
      return {
        pass: hasComponents,
        level: 'WARNING',
        message: hasComponents ? null : 'Architecture without COMPONENT/SYSTEM placeholders.',
        suggestion: hasComponents ? null : {
          templates: ['flowchart', 'sequence'],
          reason: 'Process flow, not component structure'
        }
      };
    }
  },
  
  sequence_requires_actors: {
    template: 'sequence',
    check: (placeholders) => {
      const actors = Object.keys(placeholders).filter(k => k.startsWith('ACTOR'));
      const messages = Object.keys(placeholders).filter(k => k.startsWith('MESSAGE'));
      const hasInteractions = actors.length >= 2 && messages.length > 0;
      return {
        pass: hasInteractions,
        level: 'WARNING',
        message: hasInteractions ? null : `Sequence needs multiple actors and messages.`,
        suggestion: hasInteractions ? null : {
          templates: ['flowchart', 'state-diagram'],
          reason: 'Single-actor process flow'
        }
      };
    }
  },
  
  state_diagram_requires_states: {
    template: 'state-diagram',
    check: (placeholders) => {
      const states = Object.keys(placeholders).filter(k => k.startsWith('STATE'));
      const transitions = Object.keys(placeholders).filter(k => k.includes('TRANSITION'));
      const hasProgression = states.length >= 3 && transitions.length >= 2;
      return {
        pass: hasProgression,
        level: 'WARNING',
        message: hasProgression ? null : `State diagram needs multiple states and transitions.`,
        suggestion: hasProgression ? null : {
          templates: ['flowchart'],
          reason: 'Simple decision flow'
        }
      };
    }
  },
  
  comparison_table_vs_quadrant: {
    template: 'comparison',
    check: (placeholders) => {
      const hasCoordinates = Object.keys(placeholders).some(k => k.includes('X_') || k.includes('Y_'));
      return {
        pass: hasCoordinates,
        level: 'ERROR',
        message: hasCoordinates ? null : 'Comparison (quadrant) requires X/Y coordinates. Use comparison-table for side-by-side.',
        suggestion: hasCoordinates ? null : {
          templates: ['comparison-table'],
          reason: 'Feature comparison without 2D positioning'
        }
      };
    }
  },
  
  gantt_requires_temporal: {
    template: 'gantt',
    check: (placeholders) => {
      const tasks = Object.keys(placeholders).filter(k => k.includes('TASK'));
      const starts = Object.keys(placeholders).filter(k => k.includes('START'));
      const durations = Object.keys(placeholders).filter(k => k.includes('DURATION'));
      const hasTemporal = tasks.length > 0 && starts.length > 0 && durations.length > 0;
      return {
        pass: hasTemporal,
        level: 'ERROR',
        message: hasTemporal ? null : 'Gantt requires tasks with start dates and durations.',
        suggestion: hasTemporal ? null : {
          templates: ['timeline', 'state-diagram'],
          reason: 'Sequential progression without time constraints'
        }
      };
    }
  },
  
  class_diagram_requires_oop: {
    template: 'class-diagram',
    check: (placeholders) => {
      const classes = Object.keys(placeholders).filter(k => k.includes('CLASS'));
      const attrs = Object.keys(placeholders).filter(k => k.includes('ATTR'));
      const methods = Object.keys(placeholders).filter(k => k.includes('METHOD'));
      const hasOOP = classes.length >= 2 && (attrs.length > 0 || methods.length > 0);
      return {
        pass: hasOOP,
        level: 'WARNING',
        message: hasOOP ? null : 'Class diagram needs multiple classes with attributes/methods.',
        suggestion: hasOOP ? null : {
          templates: ['architecture', 'flowchart'],
          reason: 'Component structure or process flow, not object model'
        }
      };
    }
  }
};

export function validateSemantics(template, placeholders) {
  const results = {
    template,
    passed: true,
    errors: [],
    warnings: [],
    suggestions: []
  };
  
  const rules = Object.entries(VALIDATION_RULES).filter(([_, rule]) => rule.template === template);
  
  for (const [ruleName, rule] of rules) {
    const result = rule.check(placeholders);
    
    if (!result.pass) {
      if (result.level === 'ERROR') {
        results.errors.push({ rule: ruleName, message: result.message, suggestion: result.suggestion });
        results.passed = false;
      } else if (result.level === 'WARNING') {
        results.warnings.push({ rule: ruleName, message: result.message, suggestion: result.suggestion });
      }
    }
    
    if (result.suggestion) {
      results.suggestions.push({ rule: ruleName, ...result.suggestion });
    }
  }
  
  return results;
}

export function generateCorrections(validationResults, originalContent) {
  const corrections = [];
  
  for (const suggestion of validationResults.suggestions) {
    for (const suggestedTemplate of suggestion.templates) {
      corrections.push({
        suggestedTemplate,
        reason: suggestion.reason,
        confidence: 0.8,
        originalTemplate: validationResults.template
      });
    }
  }
  
  return corrections.sort((a, b) => b.confidence - a.confidence);
}
