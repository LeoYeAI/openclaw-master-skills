/**
 * patterns.js — AI writing pattern detection engine.
 *
 * 24 pattern detectors organized into 5 categories, with a registry
 * that supports dynamic add/remove and custom word lists.
 *
 * Architecture:
 *   - Each pattern is an object with id, name, category, description,
 *     weight (1-5), and a detect(text) function
 *   - detect() returns [{ match, index, line, column, suggestion, confidence }]
 *   - The registry holds all patterns and provides query methods
 *   - Vocabulary is sourced from vocabulary.js (500+ words/phrases)
 */

const { TIER_1, TIER_2, TIER_3, AI_PHRASES } = require('./vocabulary');
// Stats imported for cross-module analysis when needed
// const { tokenize } = require('./stats');

// ─── Helpers ─────────────────────────────────────────────

/**
 * Find all regex matches with line numbers and columns.
 * Returns [{ match, index, line, column, suggestion, confidence }]
 */
function findMatches(text, regex, suggestion, confidence = 'high') {
  const results = [];
  const lines = text.split('\n');
  let offset = 0;

  for (let lineNum = 0; lineNum < lines.length; lineNum++) {
    const line = lines[lineNum];
    const lineRegex = new RegExp(
      regex.source,
      regex.flags.includes('g') ? regex.flags : `${regex.flags}g`,
    );
    let m;
    while ((m = lineRegex.exec(line)) !== null) {
      results.push({
        match: m[0],
        index: offset + m.index,
        line: lineNum + 1,
        column: m.index + 1,
        suggestion: typeof suggestion === 'function' ? suggestion(m[0]) : suggestion,
        confidence,
      });
    }
    offset += line.length + 1;
  }
  return results;
}

/** Count regex occurrences. */
function countMatches(text, regex) {
  const m = text.match(regex);
  return m ? m.length : 0;
}

/** Word count. */
function wordCount(text) {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

// ─── Vocabulary Detection Helpers ────────────────────────

/**
 * Build a case-insensitive word-boundary regex for a word.
 * Escapes special regex chars in the word.
 */
function wordRegex(word) {
  const escaped = word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  // For multi-word phrases, don't use word boundaries on internal spaces
  if (word.includes(' ')) {
    return new RegExp(`\\b${escaped}\\b`, 'gi');
  }
  return new RegExp(`\\b${escaped}\\b`, 'gi');
}

/**
 * Scan text for words from a tier list. Returns matches with word-specific suggestions.
 */
function scanWordList(text, wordList, suggestionPrefix, confidence = 'high') {
  const results = [];
  for (const word of wordList) {
    const regex = wordRegex(word);
    const matches = findMatches(
      text,
      regex,
      `${suggestionPrefix}: "${word}". Use a simpler, more specific alternative.`,
      confidence,
    );
    results.push(...matches);
  }
  return results;
}

/**
 * Scan text for AI phrases. Returns matches with phrase-specific fixes.
 */
function scanPhrases(text, phrases, tierFilter = null) {
  const results = [];
  for (const { pattern, tier, fix } of phrases) {
    if (tierFilter !== null && tier !== tierFilter) continue;
    const matches = findMatches(
      text,
      pattern,
      fix.startsWith('(') ? fix : `Replace with: ${fix}`,
      tier === 1 ? 'high' : tier === 2 ? 'medium' : 'low',
    );
    results.push(...matches);
  }
  return results;
}

// ─── Significance / Promotional Phrase Lists ─────────────
// (Kept here for patterns that need inline regex arrays)

const SIGNIFICANCE_PHRASES = [
  /marking a pivotal/gi,
  /pivotal moment/gi,
  /pivotal role/gi,
  /key role/gi,
  /crucial role/gi,
  /vital role/gi,
  /significant role/gi,
  /is a testament/gi,
  /stands as a testament/gi,
  /serves as a testament/gi,
  /serves as a reminder/gi,
  /reflects broader/gi,
  /broader trends/gi,
  /broader movement/gi,
  /evolving landscape/gi,
  /evolving world/gi,
  /setting the stage for/gi,
  /marking a shift/gi,
  /key turning point/gi,
  /indelible mark/gi,
  /deeply rooted/gi,
  /focal point/gi,
  /symbolizing its ongoing/gi,
  /enduring legacy/gi,
  /lasting impact/gi,
  /contributing to the/gi,
  /underscores the importance/gi,
  /highlights the significance/gi,
  /represents a shift/gi,
  /shaping the future/gi,
  /the evolution of/gi,
  /rich tapestry/gi,
  /rich heritage/gi,
  /stands as a beacon/gi,
  /marks a milestone/gi,
  /paving the way/gi,
  /charting a course/gi,
];

const PROMOTIONAL_WORDS = [
  /\bnestled\b/gi,
  /\bin the heart of\b/gi,
  /\bbreathtaking\b/gi,
  /\bmust-visit\b/gi,
  /\bstunning\b/gi,
  /\brenowned\b/gi,
  /\bnatural beauty\b/gi,
  /\brich cultural heritage\b/gi,
  /\brich history\b/gi,
  /\bcommitment to\b/gi,
  /\bexemplifies\b/gi,
  /\bworld-class\b/gi,
  /\bstate-of-the-art\b/gi,
  /\bgame-changing\b/gi,
  /\bgame changer\b/gi,
  /\bunparalleled\b/gi,
  /\bprofound\b/gi,
  /\bbest-in-class\b/gi,
  /\btrailblazing\b/gi,
  /\bvisionary\b/gi,
  /\bcutting-edge\b/gi,
  /\bworldwide recognition\b/gi,
];

const VAGUE_ATTRIBUTION_PHRASES = [
  /\bexperts (believe|argue|say|suggest|note|agree|contend|have noted)\b/gi,
  /\bindustry (reports|observers|experts|analysts|leaders|insiders)\b/gi,
  /\bobservers have (cited|noted|pointed out)\b/gi,
  /\bsome critics argue\b/gi,
  /\bsome experts (say|believe|suggest)\b/gi,
  /\bseveral sources\b/gi,
  /\baccording to reports\b/gi,
  /\bwidely (regarded|considered|recognized|acknowledged)\b/gi,
  /\bit is widely (known|believed|accepted)\b/gi,
  /\bmany (experts|scholars|researchers|analysts) (believe|argue|suggest)\b/gi,
  /\bstudies (show|suggest|indicate|have shown)\b/gi,
  /\bresearch (shows|suggests|indicates|has shown)\b/gi,
  /\bsources close to\b/gi,
  /\bpeople familiar with\b/gi,
];

const CHALLENGES_PHRASES = [
  /despite (its|these|the|their) (challenges|setbacks|obstacles|difficulties|limitations)/gi,
  /faces (several|many|numerous|various) challenges/gi,
  /continues to thrive/gi,
  /continues to grow/gi,
  /future (outlook|prospects) (remain|look|appear)/gi,
  /challenges and (future|legacy|opportunities)/gi,
  /despite these (challenges|hurdles|obstacles)/gi,
  /overcoming (obstacles|challenges|adversity)/gi,
  /weather(ing|ed) the storm/gi,
];

const COPULA_AVOIDANCE = [
  /\bserves as( a)?\b/gi,
  /\bstands as( a)?\b/gi,
  /\bmarks a\b/gi,
  /\brepresents a\b/gi,
  /\bboasts (a|an|over|more)\b/gi,
  /\bfeatures (a|an|over|more)\b/gi,
  /\boffers (a|an)\b/gi,
  /\bfunctions as\b/gi,
  /\bacts as( a)?\b/gi,
  /\boperates as( a)?\b/gi,
];

// ─── Pattern Definitions ─────────────────────────────────

const patterns = [
  // ── CONTENT PATTERNS (1-6) ──────────────────────────────

  {
    id: 1,
    name: 'Significance inflation',
    category: 'content',
    description:
      'Inflated claims about significance, legacy, or broader trends. LLMs puff up importance of mundane things.',
    weight: 4,
    detect(text) {
      const results = [];
      for (const regex of SIGNIFICANCE_PHRASES) {
        results.push(
          ...findMatches(
            text,
            regex,
            'Remove inflated significance claim. State concrete facts instead.',
            'high',
          ),
        );
      }
      return results;
    },
  },

  {
    id: 2,
    name: 'Notability name-dropping',
    category: 'content',
    description:
      'Listing media outlets or sources to claim notability without providing context or specific claims.',
    weight: 3,
    detect(text) {
      const mediaList =
        /\b(cited|featured|covered|mentioned|reported|published|recognized|highlighted) (in|by) .{0,20}(The New York Times|BBC|CNN|The Washington Post|The Guardian|Wired|Forbes|Reuters|Bloomberg|Financial Times|The Verge|TechCrunch|The Hindu|Al Jazeera|Time|Newsweek|The Economist|Nature|Science).{0,100}(,\s*(and\s+)?(The New York Times|BBC|CNN|The Washington Post|The Guardian|Wired|Forbes|Reuters|Bloomberg|Financial Times|The Verge|TechCrunch|The Hindu|Al Jazeera|Time|Newsweek|The Economist|Nature|Science))+/gi;
      const results = findMatches(
        text,
        mediaList,
        'Instead of listing outlets, cite one specific claim from one source.',
        'high',
      );
      results.push(
        ...findMatches(
          text,
          /\bactive social media presence\b/gi,
          'Remove — not meaningful without specific context.',
          'high',
        ),
      );
      results.push(
        ...findMatches(
          text,
          /\bwritten by a leading expert\b/gi,
          'Name the expert and their specific credential.',
          'medium',
        ),
      );
      results.push(
        ...findMatches(
          text,
          /\bhas been (featured|recognized|acknowledged) (by|in)\b/gi,
          'Cite the specific feature with a concrete claim.',
          'medium',
        ),
      );
      return results;
    },
  },

  {
    id: 3,
    name: 'Superficial -ing analyses',
    category: 'content',
    description: 'Tacking "-ing" participial phrases onto sentences to fake depth.',
    weight: 4,
    detect(text) {
      const ingPhrases =
        /,\s*(highlighting|underscoring|emphasizing|ensuring|reflecting|symbolizing|contributing to|cultivating|fostering|encompassing|showcasing|demonstrating|illustrating|representing|signaling|indicating|solidifying|reinforcing|cementing|underscoring|bolstering|reaffirming|illuminating|epitomizing)\b[^.]{5,}/gi;
      return findMatches(
        text,
        ingPhrases,
        'Remove trailing -ing phrase. If the point matters, give it its own sentence with specifics.',
        'high',
      );
    },
  },

  {
    id: 4,
    name: 'Promotional language',
    category: 'content',
    description: 'Ad-copy language that sounds like a tourism brochure or press release.',
    weight: 3,
    detect(text) {
      const results = [];
      for (const regex of PROMOTIONAL_WORDS) {
        results.push(
          ...findMatches(
            text,
            regex,
            'Replace promotional language with neutral, factual description.',
            'high',
          ),
        );
      }
      return results;
    },
  },

  {
    id: 5,
    name: 'Vague attributions',
    category: 'content',
    description: 'Attributing claims to unnamed experts, industry reports, or vague authorities.',
    weight: 4,
    detect(text) {
      const results = [];
      for (const regex of VAGUE_ATTRIBUTION_PHRASES) {
        results.push(
          ...findMatches(
            text,
            regex,
            "Name the specific source, study, or person. If you can't, remove the claim.",
            'high',
          ),
        );
      }
      return results;
    },
  },

  {
    id: 6,
    name: 'Formulaic challenges',
    category: 'content',
    description: 'Boilerplate "Despite challenges... continues to thrive" sections.',
    weight: 3,
    detect(text) {
      const results = [];
      for (const regex of CHALLENGES_PHRASES) {
        results.push(
          ...findMatches(
            text,
            regex,
            'Replace with specific challenges and concrete outcomes.',
            'high',
          ),
        );
      }
      return results;
    },
  },

  // ── LANGUAGE PATTERNS (7-12) ────────────────────────────

  {
    id: 7,
    name: 'AI vocabulary',
    category: 'language',
    description:
      'Words and phrases that appear far more frequently in AI-generated text. 500+ words tracked across 3 tiers.',
    weight: 5,
    detect(text) {
      const results = [];
      const words = wordCount(text);

      // Tier 1: always flag
      results.push(...scanWordList(text, TIER_1, 'Tier 1 AI word', 'high'));

      // Tier 2: flag if 2+ tier-2 words appear
      const tier2Matches = scanWordList(text, TIER_2, 'Tier 2 AI word', 'medium');
      if (tier2Matches.length >= 2) {
        results.push(...tier2Matches);
      }

      // Tier 3: flag only at high density (>3% of words are tier-3)
      if (words > 50) {
        const tier3Count = TIER_3.reduce((count, word) => {
          const regex = wordRegex(word);
          return count + countMatches(text, regex);
        }, 0);
        const density = tier3Count / words;
        if (density > 0.03) {
          results.push(...scanWordList(text, TIER_3, 'Tier 3 AI word (high density)', 'low'));
        }
      }

      // AI phrases (from vocabulary.js)
      results.push(
        ...scanPhrases(
          text,
          AI_PHRASES.filter(
            (p) =>
              p.fix &&
              !p.fix.startsWith('(remove') &&
              !['to', 'because', 'now', 'if', 'can', 'first', 'finally'].includes(p.fix),
          ),
        ),
      );

      return results;
    },
  },

  {
    id: 8,
    name: 'Copula avoidance',
    category: 'language',
    description:
      'Using "serves as", "functions as", "boasts" instead of simple "is", "has", "are".',
    weight: 3,
    detect(text) {
      const results = [];
      for (const regex of COPULA_AVOIDANCE) {
        results.push(
          ...findMatches(text, regex, 'Use simple "is", "are", or "has" instead.', 'high'),
        );
      }
      return results;
    },
  },

  {
    id: 9,
    name: 'Negative parallelisms',
    category: 'language',
    description:
      '"It\'s not just X, it\'s Y" or "Not only X but Y" constructions — overused by LLMs.',
    weight: 3,
    detect(text) {
      const negParallel =
        /\b(it'?s|this is) not (just|merely|only|simply) .{3,60}(,|;|—)\s*(it'?s|this is|but)\b/gi;
      const notOnly = /\bnot only .{3,60} but (also )?\b/gi;
      return [
        ...findMatches(
          text,
          negParallel,
          'Rewrite directly. State what the thing IS, not what it "isn\'t just".',
          'high',
        ),
        ...findMatches(
          text,
          notOnly,
          'Simplify. Remove the "not only...but also" frame.',
          'medium',
        ),
      ];
    },
  },

  {
    id: 10,
    name: 'Rule of three',
    category: 'language',
    description: 'Forcing ideas into groups of three. LLMs love triads that sound "comprehensive".',
    weight: 2,
    detect(text) {
      // Abstract noun triads
      const buzzyTriad =
        /\b(\w+tion|\w+ity|\w+ment|\w+ness|\w+ance|\w+ence),\s+(\w+tion|\w+ity|\w+ment|\w+ness|\w+ance|\w+ence),\s+and\s+(\w+tion|\w+ity|\w+ment|\w+ness|\w+ance|\w+ence)\b/gi;
      const results = findMatches(
        text,
        buzzyTriad,
        'Rule of three with abstract nouns. Pick the one or two that actually matter.',
        'medium',
      );

      // Buzzy adjective triads
      const buzzAdj = [
        'seamless',
        'intuitive',
        'powerful',
        'innovative',
        'dynamic',
        'robust',
        'comprehensive',
        'cutting-edge',
        'scalable',
        'agile',
        'efficient',
        'effective',
        'engaging',
        'impactful',
        'meaningful',
        'transformative',
        'sustainable',
        'resilient',
        'inclusive',
        'accessible',
      ];
      const adjPattern = buzzAdj.join('|');
      const adjTriad = new RegExp(
        `\\b(${adjPattern}),\\s+(${adjPattern}),\\s+and\\s+(${adjPattern})\\b`,
        'gi',
      );
      results.push(
        ...findMatches(
          text,
          adjTriad,
          'Buzzy adjective triad. Pick one and make it specific.',
          'medium',
        ),
      );

      return results;
    },
  },

  {
    id: 11,
    name: 'Synonym cycling',
    category: 'language',
    description:
      'Referring to the same thing by different names in consecutive sentences to avoid repetition.',
    weight: 2,
    detect(text) {
      const synonymSets = [
        ['protagonist', 'main character', 'central figure', 'hero', 'lead character', 'lead'],
        ['company', 'firm', 'organization', 'enterprise', 'corporation', 'establishment', 'entity'],
        ['city', 'metropolis', 'urban center', 'municipality', 'locale', 'township'],
        ['building', 'structure', 'edifice', 'facility', 'complex', 'establishment'],
        ['tool', 'instrument', 'mechanism', 'apparatus', 'device', 'utility'],
        ['country', 'nation', 'state', 'republic', 'sovereign state'],
        ['problem', 'challenge', 'issue', 'obstacle', 'hurdle', 'difficulty'],
        ['solution', 'approach', 'methodology', 'framework', 'strategy', 'paradigm'],
      ];

      const results = [];
      const sentences = text.split(/[.!?]+/).filter((s) => s.trim().length > 0);

      for (const synonyms of synonymSets) {
        for (let i = 0; i < sentences.length - 1; i++) {
          const found = [];
          for (let j = i; j < Math.min(i + 4, sentences.length); j++) {
            const lower = sentences[j].toLowerCase();
            for (const syn of synonyms) {
              if (lower.includes(syn) && !found.includes(syn)) {
                found.push(syn);
              }
            }
          }
          if (found.length >= 3) {
            results.push({
              match: `Synonym cycling: ${found.join(' → ')}`,
              index: text.indexOf(sentences[i]),
              line: text.substring(0, text.indexOf(sentences[i])).split('\n').length,
              column: 1,
              suggestion: `Pick one term and stick with it. Found "${found.join('", "')}" used as synonyms in nearby sentences.`,
              confidence: 'medium',
            });
            break;
          }
        }
      }
      return results;
    },
  },

  {
    id: 12,
    name: 'False ranges',
    category: 'language',
    description: '"From X to Y" where X and Y aren\'t on a meaningful scale.',
    weight: 2,
    detect(text) {
      const doubleRange = /\bfrom .{3,40} to .{3,40},\s*from .{3,40} to .{3,40}/gi;
      const results = findMatches(
        text,
        doubleRange,
        "False range — X and Y probably aren't on a meaningful scale. Just list the topics.",
        'high',
      );

      const abstractRange =
        /\bfrom (the )?(dawn|birth|inception|beginning|advent|emergence|rise|earliest) .{3,60} to (the )?(modern|current|present|contemporary|latest|cutting-edge|digital|future)/gi;
      results.push(
        ...findMatches(
          text,
          abstractRange,
          "Unnecessarily broad range. Be specific about what you're actually covering.",
          'medium',
        ),
      );

      return results;
    },
  },

  // ── STYLE PATTERNS (13-18) ──────────────────────────────

  {
    id: 13,
    name: 'Em dash overuse',
    category: 'style',
    description: 'LLMs overuse em dashes (—) as a crutch for punchy writing.',
    weight: 2,
    detect(text) {
      const emDashes = text.match(/—/g) || [];
      const words = wordCount(text);
      const ratio = words > 0 ? emDashes.length / (words / 100) : 0;

      if (ratio > 1.0 && emDashes.length >= 2) {
        return findMatches(
          text,
          /—/g,
          `High em dash density (${emDashes.length} in ${words} words). Replace most with commas, periods, or parentheses.`,
          'medium',
        );
      }
      return [];
    },
  },

  {
    id: 14,
    name: 'Boldface overuse',
    category: 'style',
    description:
      'Mechanical emphasis of phrases in bold. AI uses **bold** as a highlighting crutch.',
    weight: 2,
    detect(text) {
      const boldMatches = text.match(/\*\*[^*]+\*\*/g) || [];
      if (boldMatches.length >= 3) {
        return findMatches(
          text,
          /\*\*[^*]+\*\*/g,
          'Excessive boldface. Remove emphasis — let the writing carry the weight.',
          'medium',
        );
      }
      return [];
    },
  },

  {
    id: 15,
    name: 'Inline-header lists',
    category: 'style',
    description: 'Lists where each item starts with a bolded header followed by a colon.',
    weight: 3,
    detect(text) {
      const inlineHeaders = /^[*-]\s+\*\*[^*]+:\*\*\s/gm;
      const matches = text.match(inlineHeaders) || [];
      if (matches.length >= 2) {
        return findMatches(
          text,
          inlineHeaders,
          'Inline-header list pattern. Convert to a paragraph or use a simpler list.',
          'high',
        );
      }
      return [];
    },
  },

  {
    id: 16,
    name: 'Title Case headings',
    category: 'style',
    description: 'Capitalizing Every Main Word In Headings. AI chatbots default to this.',
    weight: 1,
    detect(text) {
      const headingRegex = /^#{1,6}\s+(.+)$/gm;
      const results = [];
      let m;
      while ((m = headingRegex.exec(text)) !== null) {
        const heading = m[1].trim();
        const words = heading.split(/\s+/);
        if (words.length >= 3) {
          const skipWords =
            /^(I|AI|API|CLI|URL|HTML|CSS|JS|TS|NPM|NYC|USA|UK|EU|LLM|GPT|SaaS|IoT|CEO|CTO|VP|PR|HR|IT|UI|UX)\b/;
          const capitalizedCount = words.filter(
            (w) => /^[A-Z]/.test(w) && !skipWords.test(w),
          ).length;
          if (capitalizedCount / words.length > 0.7) {
            const lineNum = text.substring(0, m.index).split('\n').length;
            results.push({
              match: m[0],
              index: m.index,
              line: lineNum,
              column: 1,
              suggestion:
                'Use sentence case for headings (only capitalize first word and proper nouns).',
              confidence: 'medium',
            });
          }
        }
      }
      return results;
    },
  },

  {
    id: 17,
    name: 'Emoji overuse',
    category: 'style',
    description: 'Decorating headings or bullet points with emojis in professional/technical text.',
    weight: 2,
    detect(text) {
      const emojiCount = countMatches(text, /[\u{1F300}-\u{1F9FF}\u{2600}-\u{27BF}]/gu);
      if (emojiCount >= 3) {
        return findMatches(
          text,
          /[\u{1F300}-\u{1F9FF}\u{2600}-\u{27BF}\u{2300}-\u{23FF}\u{2B50}]/gu,
          'Remove emoji decoration from professional text.',
          'high',
        );
      }
      return [];
    },
  },

  {
    id: 18,
    name: 'Curly quotes',
    category: 'style',
    description:
      'ChatGPT uses Unicode curly quotes (\u201C\u201D\u2018\u2019) instead of straight quotes.',
    weight: 1,
    detect(text) {
      return findMatches(
        text,
        /[\u201C\u201D\u2018\u2019]/g,
        'Replace curly quotes with straight quotes.',
        'high',
      );
    },
  },

  // ── COMMUNICATION PATTERNS (19-21) ─────────────────────

  {
    id: 19,
    name: 'Chatbot artifacts',
    category: 'communication',
    description:
      'Leftover chatbot phrases: "I hope this helps!", "Let me know if...", "Here is an overview".',
    weight: 5,
    detect(text) {
      // Use the phrase-level detection from vocabulary.js
      return scanPhrases(
        text,
        AI_PHRASES.filter(
          (p) => p.fix === '(remove)' || p.fix === '(remove — start with the content)',
        ),
      );
    },
  },

  {
    id: 20,
    name: 'Cutoff disclaimers',
    category: 'communication',
    description: 'AI knowledge-cutoff disclaimers left in text.',
    weight: 4,
    detect(text) {
      return scanPhrases(
        text,
        AI_PHRASES.filter(
          (p) =>
            p.fix === '(remove)' &&
            (p.pattern.source.includes('training') ||
              p.pattern.source.includes('details are') ||
              p.pattern.source.includes('available')),
        ),
      );
    },
  },

  {
    id: 21,
    name: 'Sycophantic tone',
    category: 'communication',
    description:
      'Overly positive, people-pleasing language: "Great question!", "You\'re absolutely right!".',
    weight: 4,
    detect(text) {
      return scanPhrases(
        text,
        AI_PHRASES.filter(
          (p) =>
            p.fix &&
            (p.fix.includes('(remove)') || p.fix.includes('address the substance')) &&
            (p.pattern.source.includes('question') ||
              p.pattern.source.includes('point') ||
              p.pattern.source.includes('right') ||
              p.pattern.source.includes('observation')),
        ),
      );
    },
  },

  // ── FILLER & HEDGING (22-24) ────────────────────────────

  {
    id: 22,
    name: 'Filler phrases',
    category: 'filler',
    description:
      'Wordy filler that can be shortened: "in order to" → "to", "due to the fact that" → "because".',
    weight: 3,
    detect(text) {
      return scanPhrases(
        text,
        AI_PHRASES.filter(
          (p) =>
            p.fix &&
            !p.fix.startsWith('(') &&
            [
              'to',
              'because',
              'now',
              'if',
              'can',
              'to / for',
              'first',
              'finally',
              'for / regarding',
              'because / since',
            ].includes(p.fix),
        ),
      );
    },
  },

  {
    id: 23,
    name: 'Excessive hedging',
    category: 'filler',
    description: 'Stacking qualifiers: "could potentially possibly", "might arguably perhaps".',
    weight: 3,
    detect(text) {
      return scanPhrases(
        text,
        AI_PHRASES.filter(
          (p) =>
            p.fix &&
            (p.fix.includes('could') ||
              p.fix.includes('might') ||
              p.fix.includes('may') ||
              p.fix.includes('perhaps') ||
              p.fix.includes('maybe')),
        ),
      );
    },
  },

  {
    id: 24,
    name: 'Generic conclusions',
    category: 'filler',
    description: 'Vague upbeat endings: "The future looks bright", "Exciting times lie ahead".',
    weight: 3,
    detect(text) {
      return scanPhrases(
        text,
        AI_PHRASES.filter(
          (p) =>
            p.fix &&
            (p.fix.includes('specific fact') ||
              p.fix.includes('concrete') ||
              p.fix.includes('cite evidence') ||
              p.fix.includes('what you do know') ||
              p.fix.includes('what happens next')),
        ),
      );
    },
  },
];

// ─── Pattern Registry ────────────────────────────────────

class PatternRegistry {
  constructor() {
    this._patterns = [...patterns];
    this._customWords = { tier1: [], tier2: [], tier3: [] };
  }

  /** Get all patterns. */
  all() {
    return this._patterns;
  }

  /** Get pattern by ID. */
  get(id) {
    return this._patterns.find((p) => p.id === id);
  }

  /** Get patterns by category. */
  byCategory(category) {
    return this._patterns.filter((p) => p.category === category);
  }

  /** Add a custom pattern. */
  add(pattern) {
    if (!pattern.id || !pattern.name || !pattern.detect) {
      throw new Error('Pattern must have id, name, and detect function');
    }
    this._patterns.push(pattern);
  }

  /** Remove a pattern by ID. */
  remove(id) {
    this._patterns = this._patterns.filter((p) => p.id !== id);
  }

  /** Add custom words to a tier. */
  addWords(tier, words) {
    const key = `tier${tier}`;
    if (!this._customWords[key]) throw new Error(`Invalid tier: ${tier}`);
    this._customWords[key].push(...words);
  }

  /** Get full vocabulary for a tier (built-in + custom). */
  getVocabulary(tier) {
    const builtIn = tier === 1 ? TIER_1 : tier === 2 ? TIER_2 : TIER_3;
    return [...builtIn, ...(this._customWords[`tier${tier}`] || [])];
  }

  /** List all pattern IDs and names. */
  list() {
    return this._patterns.map((p) => ({
      id: p.id,
      name: p.name,
      category: p.category,
      weight: p.weight,
    }));
  }

  /** Get categories. */
  categories() {
    return [...new Set(this._patterns.map((p) => p.category))];
  }
}

// Singleton registry
const registry = new PatternRegistry();

// ─── Exports ─────────────────────────────────────────────

module.exports = {
  patterns,
  registry,
  PatternRegistry,
  findMatches,
  countMatches,
  wordCount,
  scanWordList,
  scanPhrases,
  // Re-export vocabulary for backward compat
  TIER_1,
  TIER_2,
  TIER_3,
  AI_PHRASES,
  SIGNIFICANCE_PHRASES,
  PROMOTIONAL_WORDS,
  VAGUE_ATTRIBUTION_PHRASES,
  CHALLENGES_PHRASES,
  COPULA_AVOIDANCE,
};
