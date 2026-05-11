/**
 * TotalReclaw Skill - Test Conversation Fixtures
 *
 * Scripted test conversations for functional testing of the TotalReclaw skill.
 * These fixtures simulate realistic conversation flows to test:
 * - Automatic fact extraction (post-turn)
 * - Explicit memory commands
 * - Pre-compaction extraction
 * - Fact retrieval and injection
 * - Contradiction handling (UPDATE actions)
 */

import type { OpenClawContext, ConversationTurn } from '../../src/types';

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Create a date with a consistent offset from a base time
 */
function createDate(baseDate: Date, offsetMinutes: number): Date {
  return new Date(baseDate.getTime() + offsetMinutes * 60 * 1000);
}

/**
 * Create a conversation turn
 */
function createTurn(
  role: 'user' | 'assistant',
  content: string,
  timestamp: Date
): ConversationTurn {
  return { role, content, timestamp };
}

/**
 * Build history from an array of turns
 */
function buildHistory(turns: Array<{ role: 'user' | 'assistant'; content: string }>, baseDate: Date): ConversationTurn[] {
  return turns.map((turn, index) => createTurn(turn.role, turn.content, createDate(baseDate, index * 2)));
}

/**
 * Create an OpenClawContext for testing
 */
function createContext(
  history: ConversationTurn[],
  userMessage: string,
  overrides: Partial<Omit<OpenClawContext, 'history' | 'userMessage'>> = {}
): OpenClawContext {
  return {
    userMessage,
    history,
    agentId: 'test-agent',
    sessionId: 'test-session',
    tokenCount: history.reduce((acc, turn) => acc + Math.ceil(turn.content.length / 4), 0),
    tokenLimit: 4000,
    ...overrides,
  };
}

// ============================================================================
// Types for Test Conversations
// ============================================================================

/**
 * Represents a single turn in a test scenario
 */
export interface TestTurn {
  role: 'user' | 'assistant';
  content: string;
  /** Optional: What should happen after this turn */
  expectedBehavior?: {
    /** Should extraction be triggered? */
    triggerExtraction?: boolean;
    /** Expected facts to be extracted (partial match) */
    expectedFacts?: Array<{
      factText: string;
      type?: string;
      action?: 'ADD' | 'UPDATE' | 'DELETE' | 'NOOP';
    }>;
    /** Should memory retrieval occur? */
    triggerRetrieval?: boolean;
    /** Expected memory to be retrieved */
    expectedRetrieval?: string;
    /** Explicit memory command detected */
    explicitCommand?: 'remember' | 'forget' | 'recall';
  };
}

/**
 * A complete test conversation fixture
 */
export interface TestConversation {
  /** Unique identifier */
  id: string;
  /** Human-readable name */
  name: string;
  /** Description of what this tests */
  description: string;
  /** The conversation turns */
  turns: TestTurn[];
  /** Tags for categorization */
  tags: string[];
  /** Expected final state */
  expectedFinalState?: {
    /** Number of facts stored */
    factsStored?: number;
    /** Number of facts updated */
    factsUpdated?: number;
    /** Number of facts deleted */
    factsDeleted?: number;
    /** Key facts that should be retrievable */
    retrievableFacts?: string[];
  };
}

/**
 * A context snapshot for testing at a specific point in conversation
 */
export interface ContextSnapshot {
  /** The OpenClaw context at this point */
  context: OpenClawContext;
  /** Current turn index */
  turnIndex: number;
  /** Total turns in conversation */
  totalTurns: number;
  /** What behavior is expected at this point */
  expectedBehavior?: TestTurn['expectedBehavior'];
}

// ============================================================================
// Conversation 1: Basic Memory Storage (12 turns)
// ============================================================================

/**
 * Tests basic automatic memory extraction after the extraction threshold.
 *
 * Scenario:
 * - Turns 1-4: Regular chat (below extraction threshold of 5)
 * - Turn 5: User states preference "I prefer TypeScript over JavaScript for new projects"
 * - Turns 6-10: More chat (trigger extraction at turn 5+)
 * - Turn 11: Query "What programming language do I prefer?"
 * - Turn 12: Expected response references memory
 */
export const CONVERSATION_BASIC_MEMORY: TestConversation = {
  id: 'basic-memory-storage',
  name: 'Basic Memory Storage',
  description: 'Tests automatic extraction triggered after turn threshold with preference recall',
  tags: ['extraction', 'preference', 'recall', 'basic'],
  turns: [
    // Turns 1-4: Regular chat (below threshold)
    {
      role: 'user',
      content: 'Hello! I am starting a new project today.',
    },
    {
      role: 'assistant',
      content: 'Hello! That sounds exciting. What kind of project are you working on?',
    },
    {
      role: 'user',
      content: 'It is a web application for managing personal tasks.',
    },
    {
      role: 'assistant',
      content: 'A task management app is a great project! Do you have any specific features in mind?',
    },
    // Turn 5: Key preference statement
    {
      role: 'user',
      content: 'I prefer TypeScript over JavaScript for new projects. The type safety really helps catch bugs early.',
      expectedBehavior: {
        // Extraction may not trigger yet (depends on implementation)
        triggerExtraction: false,
      },
    },
    {
      role: 'assistant',
      content: 'TypeScript is an excellent choice for that. The static typing definitely makes larger codebases more maintainable.',
    },
    // Turns 6-10: More conversation (extraction should trigger)
    {
      role: 'user',
      content: 'Exactly. I have been using it for about two years now.',
    },
    {
      role: 'assistant',
      content: 'That is great experience. Are you planning to use any specific framework with TypeScript?',
    },
    {
      role: 'user',
      content: 'I am thinking about using React with Next.js for this project.',
      expectedBehavior: {
        triggerExtraction: true,
        expectedFacts: [
          {
            factText: 'User prefers TypeScript over JavaScript for new projects',
            type: 'preference',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'React with Next.js is a powerful combination. The server-side rendering and routing are great features.',
    },
    {
      role: 'user',
      content: 'Yes, and the developer experience is fantastic too.',
    },
    // Turn 11: Query about preference
    {
      role: 'assistant',
      content: 'Is there anything specific about the project architecture you would like to discuss?',
    },
    {
      role: 'user',
      content: 'Actually, what programming language do I prefer for new projects?',
      expectedBehavior: {
        triggerRetrieval: true,
        expectedRetrieval: 'TypeScript',
      },
    },
    // Turn 12: Expected response with memory
    {
      role: 'assistant',
      content: 'Based on what you told me, you prefer TypeScript over JavaScript for new projects because of the type safety and early bug detection.',
    },
  ],
  expectedFinalState: {
    factsStored: 1,
    retrievableFacts: ['User prefers TypeScript over JavaScript for new projects'],
  },
};

// ============================================================================
// Conversation 2: Multiple Facts (15 turns)
// ============================================================================

/**
 * Tests extraction and retrieval of multiple distinct facts.
 *
 * Scenario:
 * - Turn 3: "I work on TotalReclaw, a zero-knowledge memory vault"
 * - Turn 6: "I use z.ai GLM-5 as my LLM"
 * - Turn 9: "My project is in TypeScript"
 * - Turn 12: Query about one specific fact
 * - Expected: Correct fact retrieved from multiple stored
 */
export const CONVERSATION_MULTIPLE_FACTS: TestConversation = {
  id: 'multiple-facts',
  name: 'Multiple Facts Extraction',
  description: 'Tests extraction of multiple distinct facts and selective retrieval',
  tags: ['extraction', 'multiple-facts', 'selective-retrieval'],
  turns: [
    {
      role: 'user',
      content: 'Hi there! I want to talk about my work.',
    },
    {
      role: 'assistant',
      content: 'Hello! I would love to hear about your work. What are you working on?',
    },
    // Turn 3: First fact
    {
      role: 'user',
      content: 'I work on TotalReclaw, a zero-knowledge memory vault for AI agents. It is like a password manager but for AI memory.',
      expectedBehavior: {
        expectedFacts: [
          {
            factText: 'User works on TotalReclaw, a zero-knowledge memory vault for AI agents',
            type: 'fact',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'That sounds fascinating! A zero-knowledge memory vault is an interesting concept. How does the encryption work?',
    },
    {
      role: 'user',
      content: 'It uses end-to-end encryption so the server never sees plaintext data.',
    },
    // Turn 6: Second fact
    {
      role: 'assistant',
      content: 'Very cool. What AI model are you using to build this?',
    },
    {
      role: 'user',
      content: 'I use z.ai GLM-5 as my LLM for most of the processing. It works well for the extraction tasks.',
      expectedBehavior: {
        triggerExtraction: true,
        expectedFacts: [
          {
            factText: 'User uses z.ai GLM-5 as their LLM',
            type: 'fact',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'GLM-5 is a capable model. What programming language is the project written in?',
    },
    {
      role: 'user',
      content: 'The backend is in Rust for performance, but most of the codebase is in TypeScript.',
    },
    // Turn 9: Third fact
    {
      role: 'assistant',
      content: 'TypeScript and Rust make for a powerful combination. How is the project structured?',
    },
    {
      role: 'user',
      content: 'My project is in TypeScript primarily. We have a skill module that integrates with OpenClaw for memory management.',
      expectedBehavior: {
        triggerExtraction: true,
        expectedFacts: [
          {
            factText: 'User\'s project is primarily in TypeScript',
            type: 'fact',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'Great architecture! What stage is the project at?',
    },
    {
      role: 'user',
      content: 'We are in the PoC phase, working on the core extraction and storage logic.',
    },
    // Turn 12: Query about one specific fact
    {
      role: 'assistant',
      content: 'Is there anything specific about the project you would like to discuss?',
    },
    {
      role: 'user',
      content: 'What LLM do I use for my project?',
      expectedBehavior: {
        triggerRetrieval: true,
        expectedRetrieval: 'z.ai GLM-5',
      },
    },
    {
      role: 'assistant',
      content: 'You mentioned that you use z.ai GLM-5 as your LLM for processing tasks in your TotalReclaw project.',
    },
  ],
  expectedFinalState: {
    factsStored: 3,
    retrievableFacts: [
      'User works on TotalReclaw, a zero-knowledge memory vault for AI agents',
      'User uses z.ai GLM-5 as their LLM',
      'User\'s project is primarily in TypeScript',
    ],
  },
};

// ============================================================================
// Conversation 3: Contradiction/UPDATE (10 turns)
// ============================================================================

/**
 * Tests handling of contradictory statements that should trigger UPDATE actions.
 *
 * Scenario:
 * - Turn 3: "I prefer dark mode"
 * - Turn 7: "Actually, I changed my mind, I prefer light mode now"
 * - Turn 9: Query about preference
 * - Expected: Only "light mode" stored (UPDATE action)
 */
export const CONVERSATION_CONTRADICTION_UPDATE: TestConversation = {
  id: 'contradiction-update',
  name: 'Contradiction Update',
  description: 'Tests handling of contradictory statements that should trigger UPDATE action',
  tags: ['extraction', 'contradiction', 'update', 'preference'],
  turns: [
    {
      role: 'user',
      content: 'Hi! I want to customize my development environment.',
    },
    {
      role: 'assistant',
      content: 'Hello! I can help you with that. What aspects of your environment are you looking to customize?',
    },
    // Turn 3: Initial preference
    {
      role: 'user',
      content: 'I prefer dark mode in all my editors. It is easier on my eyes during late-night coding sessions.',
      expectedBehavior: {
        expectedFacts: [
          {
            factText: 'User prefers dark mode in all editors',
            type: 'preference',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'Dark mode is great for reducing eye strain. Which editors are you using?',
    },
    {
      role: 'user',
      content: 'I mainly use VS Code and sometimes IntelliJ for Java projects.',
    },
    {
      role: 'assistant',
      content: 'Good choices! Both have excellent dark mode themes. Have you tried any specific themes?',
    },
    // Turn 7: Contradiction/Update
    {
      role: 'user',
      content: 'Actually, I changed my mind, I prefer light mode now. The dark mode was making it hard to read documentation side-by-side.',
      expectedBehavior: {
        triggerExtraction: true,
        expectedFacts: [
          {
            factText: 'User prefers light mode',
            type: 'preference',
            action: 'UPDATE',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'That makes sense. Light mode can definitely be better when you need to switch between code and documentation frequently.',
    },
    {
      role: 'user',
      content: 'Yes, and it also matches my terminal setup better.',
    },
    // Turn 9: Query about preference
    {
      role: 'assistant',
      content: 'Is there anything else about your setup you would like to configure?',
    },
    {
      role: 'user',
      content: 'What is my preferred theme mode?',
      expectedBehavior: {
        triggerRetrieval: true,
        expectedRetrieval: 'light mode',
      },
    },
  ],
  expectedFinalState: {
    factsStored: 1,
    factsUpdated: 1,
    retrievableFacts: ['User prefers light mode'],
  },
};

// ============================================================================
// Conversation 4: Explicit Command (6 turns)
// ============================================================================

/**
 * Tests explicit memory commands that trigger immediate storage.
 *
 * Scenario:
 * - Turn 2: "Remember that I'm building this for my startup"
 * - Expected: Immediate storage with boosted importance
 * - Turn 5: Query about the startup
 * - Expected: Memory retrieved
 */
export const CONVERSATION_EXPLICIT_COMMAND: TestConversation = {
  id: 'explicit-command',
  name: 'Explicit Memory Command',
  description: 'Tests explicit "remember" command that triggers immediate storage with boosted importance',
  tags: ['extraction', 'explicit-command', 'remember', 'high-importance'],
  turns: [
    {
      role: 'user',
      content: 'I want to tell you something important about my work.',
    },
    // Turn 2: Explicit command
    {
      role: 'user',
      content: 'Remember that I\'m building this for my startup called "MemoraTech". It is going to revolutionize how AI agents handle memory.',
      expectedBehavior: {
        triggerExtraction: true,
        explicitCommand: 'remember',
        expectedFacts: [
          {
            factText: 'User is building this for their startup called MemoraTech',
            type: 'goal',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'I have noted that. MemoraTech sounds like an exciting venture! What specific aspects of AI memory are you focusing on?',
    },
    {
      role: 'user',
      content: 'We are focusing on privacy-first, encrypted memory that users fully control.',
    },
    {
      role: 'assistant',
      content: 'That aligns well with growing privacy concerns. How is the startup progressing?',
    },
    // Turn 5: Query about startup
    {
      role: 'user',
      content: 'What is the name of my startup and what am I building?',
      expectedBehavior: {
        triggerRetrieval: true,
        expectedRetrieval: 'MemoraTech',
      },
    },
    {
      role: 'assistant',
      content: 'You mentioned you are building this for your startup called MemoraTech, which aims to revolutionize how AI agents handle memory with a focus on privacy-first, encrypted solutions.',
    },
  ],
  expectedFinalState: {
    factsStored: 1,
    retrievableFacts: ['User is building this for their startup called MemoraTech'],
  },
};

// ============================================================================
// Conversation 5: Pre-Compaction (25 turns)
// ============================================================================

/**
 * Tests pre-compaction extraction when conversation approaches token limit.
 *
 * Scenario:
 * - Long conversation that would trigger pre-compaction
 * - Multiple facts spread across turns
 * - Simulate context approaching limit
 * - Expected: All facts extracted and stored before compaction
 */
export const CONVERSATION_PRE_COMPACTION: TestConversation = {
  id: 'pre-compaction',
  name: 'Pre-Compaction Extraction',
  description: 'Tests pre-compaction extraction when context approaches token limit',
  tags: ['extraction', 'pre-compaction', 'long-conversation', 'multiple-facts'],
  turns: [
    // Early conversation - facts should be extracted normally
    {
      role: 'user',
      content: 'I am working on a comprehensive project plan and want to discuss all the details with you.',
    },
    {
      role: 'assistant',
      content: 'I would be happy to help you with your project plan. Let us start from the beginning. What is the project about?',
    },
    // Fact 1: Project name
    {
      role: 'user',
      content: 'The project is called "DataSync Pro" - it is a real-time data synchronization platform.',
      expectedBehavior: {
        expectedFacts: [
          {
            factText: 'User\'s project is called DataSync Pro',
            type: 'fact',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'DataSync Pro sounds like an ambitious project. Real-time synchronization is a complex domain. What technologies are you planning to use?',
    },
    // Fact 2: Technology choice
    {
      role: 'user',
      content: 'We decided to use Apache Kafka for the message queue and PostgreSQL for storage.',
      expectedBehavior: {
        expectedFacts: [
          {
            factText: 'User uses Apache Kafka for message queue',
            type: 'decision',
            action: 'ADD',
          },
          {
            factText: 'User uses PostgreSQL for storage',
            type: 'decision',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'Excellent choices. Kafka is great for high-throughput scenarios and PostgreSQL is very reliable. What about the frontend?',
    },
    // Fact 3: Frontend choice
    {
      role: 'user',
      content: 'For the frontend, I chose React with TypeScript. We need type safety for the complex data structures.',
      expectedBehavior: {
        expectedFacts: [
          {
            factText: 'User uses React with TypeScript for frontend',
            type: 'decision',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'React with TypeScript is a solid combination for enterprise applications. What about the deployment strategy?',
    },
    // Fact 4: Deployment
    {
      role: 'user',
      content: 'We are deploying to AWS using Kubernetes for orchestration.',
      expectedBehavior: {
        expectedFacts: [
          {
            factText: 'User deploys to AWS using Kubernetes',
            type: 'decision',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'Kubernetes on AWS gives you great scalability. Have you thought about the team structure?',
    },
    // Fact 5: Team
    {
      role: 'user',
      content: 'The team consists of 5 developers and 2 DevOps engineers. I am the tech lead.',
      expectedBehavior: {
        expectedFacts: [
          {
            factText: 'User is the tech lead of a team of 5 developers and 2 DevOps engineers',
            type: 'fact',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'A well-rounded team for this kind of project. What is your timeline?',
    },
    // Fact 6: Timeline
    {
      role: 'user',
      content: 'We have a 6-month timeline for the MVP launch, targeting June 2026.',
      expectedBehavior: {
        expectedFacts: [
          {
            factText: 'User has a 6-month timeline for MVP launch targeting June 2026',
            type: 'goal',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'That is an aggressive but achievable timeline. What are the main technical challenges you anticipate?',
    },
    // Filler conversation to approach token limit
    {
      role: 'user',
      content: 'The biggest challenge is handling conflict resolution when multiple clients update the same data simultaneously.',
    },
    {
      role: 'assistant',
      content: 'Conflict resolution is indeed tricky. Are you planning to use operational transforms or CRDTs?',
    },
    {
      role: 'user',
      content: 'We are evaluating both approaches. CRDTs seem promising but add complexity.',
    },
    {
      role: 'assistant',
      content: 'CRDTs can be complex to implement correctly. Have you looked at existing libraries like Yjs or Automerge?',
    },
    {
      role: 'user',
      content: 'Yes, we have experimented with Yjs. It works well but we need some custom conflict resolution rules.',
    },
    {
      role: 'assistant',
      content: 'Custom rules on top of CRDTs can be challenging. What kind of custom rules do you need?',
    },
    // Fact 7: Custom requirement
    {
      role: 'user',
      content: 'We need priority-based resolution where certain users have override authority in specific contexts.',
      expectedBehavior: {
        expectedFacts: [
          {
            factText: 'User needs priority-based conflict resolution with user override authority',
            type: 'fact',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'Priority-based resolution is a common requirement in enterprise scenarios. How will you handle permission management?',
    },
    {
      role: 'user',
      content: 'We are integrating with the company\'s existing LDAP system for authentication and authorization.',
    },
    {
      role: 'assistant',
      content: 'LDAP integration is a good choice for enterprise environments. What about audit logging?',
    },
    // Fact 8: Compliance requirement
    {
      role: 'user',
      content: 'Audit logging is critical. We need to comply with SOC 2 Type II requirements.',
      expectedBehavior: {
        expectedFacts: [
          {
            factText: 'User needs to comply with SOC 2 Type II requirements',
            type: 'fact',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'SOC 2 compliance adds important considerations around logging and access controls. Have you worked with these requirements before?',
    },
    // Approaching compaction threshold
    {
      role: 'user',
      content: 'This is our first SOC 2 project, so we hired a consultant to help with the compliance framework.',
    },
    {
      role: 'assistant',
      content: 'Hiring a consultant is a smart move for your first compliance project. They can help you avoid common pitfalls.',
    },
    // Turn that should trigger pre-compaction extraction
    {
      role: 'user',
      content: 'Let me summarize everything we discussed so far before we continue with the implementation details...',
      expectedBehavior: {
        triggerExtraction: true,
        // Pre-compaction should extract all accumulated facts
        expectedFacts: [
          { factText: 'DataSync Pro', action: 'ADD' },
          { factText: 'Apache Kafka', action: 'ADD' },
          { factText: 'PostgreSQL', action: 'ADD' },
          { factText: 'React with TypeScript', action: 'ADD' },
          { factText: 'AWS using Kubernetes', action: 'ADD' },
          { factText: 'tech lead', action: 'ADD' },
          { factText: 'June 2026', action: 'ADD' },
          { factText: 'SOC 2 Type II', action: 'ADD' },
        ],
      },
    },
  ],
  expectedFinalState: {
    factsStored: 8,
    retrievableFacts: [
      'User\'s project is called DataSync Pro',
      'User uses Apache Kafka for message queue',
      'User uses PostgreSQL for storage',
      'User uses React with TypeScript for frontend',
      'User deploys to AWS using Kubernetes',
      'User is the tech lead of a team of 5 developers and 2 DevOps engineers',
      'User has a 6-month timeline for MVP launch targeting June 2026',
      'User needs to comply with SOC 2 Type II requirements',
    ],
  },
};

// ============================================================================
// Additional Edge Case Conversations
// ============================================================================

/**
 * Tests explicit "forget" command.
 */
export const CONVERSATION_FORGET_COMMAND: TestConversation = {
  id: 'forget-command',
  name: 'Forget Command',
  description: 'Tests explicit "forget" command to remove stored memories',
  tags: ['extraction', 'explicit-command', 'forget', 'delete'],
  turns: [
    {
      role: 'user',
      content: 'I want to update some information you might have about me.',
    },
    {
      role: 'user',
      content: 'Remember that my favorite color is blue.',
      expectedBehavior: {
        triggerExtraction: true,
        explicitCommand: 'remember',
        expectedFacts: [
          {
            factText: 'User\'s favorite color is blue',
            type: 'preference',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'Got it! I have noted that your favorite color is blue.',
    },
    {
      role: 'user',
      content: 'Actually, forget about my favorite color. That is not important anymore.',
      expectedBehavior: {
        triggerExtraction: true,
        explicitCommand: 'forget',
        expectedFacts: [
          {
            factText: 'User\'s favorite color is blue',
            action: 'DELETE',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'I have removed that information from my memory.',
    },
    {
      role: 'user',
      content: 'What is my favorite color?',
      expectedBehavior: {
        triggerRetrieval: true,
        // Should NOT find any stored preference
        expectedRetrieval: undefined,
      },
    },
  ],
  expectedFinalState: {
    factsStored: 0,
    factsDeleted: 1,
    retrievableFacts: [],
  },
};

/**
 * Tests retrieval of memories when no relevant facts exist.
 */
export const CONVERSATION_NO_MATCHING_MEMORIES: TestConversation = {
  id: 'no-matching-memories',
  name: 'No Matching Memories',
  description: 'Tests retrieval behavior when query does not match any stored facts',
  tags: ['retrieval', 'no-match', 'edge-case'],
  turns: [
    {
      role: 'user',
      content: 'Hi, I want to talk about my hobbies.',
    },
    {
      role: 'assistant',
      content: 'Hello! What hobbies would you like to discuss?',
    },
    {
      role: 'user',
      content: 'I enjoy hiking and photography on weekends.',
      expectedBehavior: {
        expectedFacts: [
          {
            factText: 'User enjoys hiking and photography on weekends',
            type: 'fact',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'Hiking and photography are wonderful hobbies! They go well together.',
    },
    {
      role: 'user',
      content: 'What is my favorite programming language?',
      expectedBehavior: {
        triggerRetrieval: true,
        // No programming language preference stored
        expectedRetrieval: undefined,
      },
    },
    {
      role: 'assistant',
      content: 'I do not have any information about your programming language preferences. Would you like to tell me about that?',
    },
  ],
  expectedFinalState: {
    factsStored: 1,
    retrievableFacts: ['User enjoys hiking and photography on weekends'],
  },
};

/**
 * Tests episodic memory extraction (time-bound events).
 */
export const CONVERSATION_EPISODIC_MEMORY: TestConversation = {
  id: 'episodic-memory',
  name: 'Episodic Memory',
  description: 'Tests extraction of time-bound events and episodic memories',
  tags: ['extraction', 'episodic', 'time-bound', 'events'],
  turns: [
    {
      role: 'user',
      content: 'I had an interesting day yesterday.',
    },
    {
      role: 'assistant',
      content: 'What happened? I would love to hear about it.',
    },
    {
      role: 'user',
      content: 'Yesterday, on February 21st, I presented TotalReclaw to a group of investors. It went really well!',
      expectedBehavior: {
        expectedFacts: [
          {
            factText: 'User presented TotalReclaw to investors on February 21st',
            type: 'episodic',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'Congratulations! How did the investors respond to the presentation?',
    },
    {
      role: 'user',
      content: 'They were very interested in the privacy aspects. Two of them asked for follow-up meetings.',
      expectedBehavior: {
        expectedFacts: [
          {
            factText: 'Two investors requested follow-up meetings after User\'s TotalReclaw presentation',
            type: 'episodic',
            action: 'ADD',
          },
        ],
      },
    },
    {
      role: 'assistant',
      content: 'That is a great sign! Follow-up meetings often lead to term sheets. When are those meetings scheduled?',
    },
  ],
  expectedFinalState: {
    factsStored: 2,
    retrievableFacts: [
      'User presented TotalReclaw to investors on February 21st',
      'Two investors requested follow-up meetings after User\'s TotalReclaw presentation',
    ],
  },
};

// ============================================================================
// Exports
// ============================================================================

/**
 * All test conversations organized by category
 */
export const TEST_CONVERSATIONS = {
  basic: [CONVERSATION_BASIC_MEMORY],
  extraction: [
    CONVERSATION_BASIC_MEMORY,
    CONVERSATION_MULTIPLE_FACTS,
    CONVERSATION_CONTRADICTION_UPDATE,
    CONVERSATION_EPISODIC_MEMORY,
  ],
  explicit: [
    CONVERSATION_EXPLICIT_COMMAND,
    CONVERSATION_FORGET_COMMAND,
  ],
  preCompaction: [CONVERSATION_PRE_COMPACTION],
  retrieval: [
    CONVERSATION_BASIC_MEMORY,
    CONVERSATION_NO_MATCHING_MEMORIES,
  ],
  edgeCases: [
    CONVERSATION_FORGET_COMMAND,
    CONVERSATION_NO_MATCHING_MEMORIES,
    CONVERSATION_EPISODIC_MEMORY,
  ],
};

/**
 * Get all test conversations as a flat array
 */
export function getAllConversations(): TestConversation[] {
  return [
    CONVERSATION_BASIC_MEMORY,
    CONVERSATION_MULTIPLE_FACTS,
    CONVERSATION_CONTRADICTION_UPDATE,
    CONVERSATION_EXPLICIT_COMMAND,
    CONVERSATION_PRE_COMPACTION,
    CONVERSATION_FORGET_COMMAND,
    CONVERSATION_NO_MATCHING_MEMORIES,
    CONVERSATION_EPISODIC_MEMORY,
  ];
}

/**
 * Get a test conversation by ID
 */
export function getConversationById(id: string): TestConversation | undefined {
  return getAllConversations().find((conv) => conv.id === id);
}

/**
 * Get conversations by tag
 */
export function getConversationsByTag(tag: string): TestConversation[] {
  return getAllConversations().filter((conv) => conv.tags.includes(tag));
}

/**
 * Generate OpenClawContext snapshots for a conversation
 * Useful for testing extraction at specific points
 */
export function createContextSnapshots(
  conversation: TestConversation,
  baseDate: Date = new Date('2026-02-22T10:00:00Z')
): ContextSnapshot[] {
  const snapshots: ContextSnapshot[] = [];
  const history: ConversationTurn[] = [];

  for (let i = 0; i < conversation.turns.length; i++) {
    const turn = conversation.turns[i];
    const timestamp = createDate(baseDate, i * 2);

    // Add the turn to history (for next context)
    history.push(createTurn(turn.role, turn.content, timestamp));

    // Create context for the NEXT user message (or current state)
    const nextUserTurn = conversation.turns.slice(i + 1).find((t) => t.role === 'user');
    const userMessage = nextUserTurn?.content || turn.content;

    snapshots.push({
      context: createContext(history, userMessage),
      turnIndex: i,
      totalTurns: conversation.turns.length,
      expectedBehavior: turn.expectedBehavior,
    });
  }

  return snapshots;
}

/**
 * Create a context for testing retrieval at a specific query
 */
export function createRetrievalTestContext(
  conversation: TestConversation,
  queryTurnIndex: number,
  baseDate: Date = new Date('2026-02-22T10:00:00Z')
): OpenClawContext {
  const history = buildHistory(
    conversation.turns.slice(0, queryTurnIndex).map((t) => ({ role: t.role, content: t.content })),
    baseDate
  );

  const queryTurn = conversation.turns[queryTurnIndex];

  return createContext(history, queryTurn?.content || '', {
    // Set high token count to simulate long conversation
    tokenCount: Math.min(
      history.reduce((acc, turn) => acc + Math.ceil(turn.content.length / 4), 0),
      3800 // Near limit
    ),
  });
}

/**
 * Create a context simulating pre-compaction state
 */
export function createPreCompactionTestContext(
  conversation: TestConversation,
  turnIndex: number,
  tokenLimit: number = 4000,
  baseDate: Date = new Date('2026-02-22T10:00:00Z')
): OpenClawContext {
  const history = buildHistory(
    conversation.turns.slice(0, turnIndex).map((t) => ({ role: t.role, content: t.content })),
    baseDate
  );

  const currentTurn = conversation.turns[turnIndex];

  return createContext(history, currentTurn?.content || '', {
    tokenCount: Math.floor(tokenLimit * 0.95), // 95% of limit
    tokenLimit,
  });
}

// Re-export types for convenience
export type { OpenClawContext, ConversationTurn };
