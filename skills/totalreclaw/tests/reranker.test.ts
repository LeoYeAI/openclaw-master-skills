/**
 * TotalReclaw Skill - Reranker Tests
 *
 * Tests for the cross-encoder reranking functionality.
 * Uses mocked ONNX runtime for unit testing.
 */

import {
  CrossEncoderReranker,
  getCrossEncoderReranker,
  crossEncoderRerank,
  type CrossEncoderConfig,
  type CrossEncoderResult,
} from '../src/reranker/cross-encoder';
import type { Fact } from '@totalreclaw/client';

// ============================================================================
// Mock Fact Factory
// ============================================================================

/**
 * Create a mock fact for testing
 */
function createMockFact(overrides: Partial<Fact> = {}): Fact {
  return {
    id: `fact-${Math.random().toString(36).substr(2, 9)}`,
    text: 'Test fact content',
    createdAt: new Date(),
    decayScore: 0.5,
    embedding: new Array(1024).fill(0).map(() => Math.random() * 0.1),
    metadata: {},
    ...overrides,
  };
}

/**
 * Create multiple mock facts
 */
function createMockFacts(count: number, prefix: string = 'Fact'): Fact[] {
  return Array.from({ length: count }, (_, i) =>
    createMockFact({
      id: `fact-${i}`,
      text: `${prefix} ${i}: This is test content for fact number ${i}`,
      decayScore: 0.3 + (i * 0.05),
    })
  );
}

// ============================================================================
// CrossEncoderReranker Tests
// ============================================================================

describe('CrossEncoderReranker', () => {
  let reranker: CrossEncoderReranker;

  beforeEach(() => {
    // Create reranker with debug disabled to reduce noise
    reranker = new CrossEncoderReranker({ debug: false });
  });

  afterEach(async () => {
    // Clean up
    if (reranker) {
      await reranker.dispose();
    }
  });

  describe('constructor', () => {
    it('should create reranker with default config', () => {
      expect(reranker).toBeInstanceOf(CrossEncoderReranker);
    });

    it('should accept custom configuration', () => {
      const customReranker = new CrossEncoderReranker({
        maxSequenceLength: 256,
        debug: true,
        modelPath: '/custom/path/model.onnx',
      });

      expect(customReranker).toBeInstanceOf(CrossEncoderReranker);
    });
  });

  describe('isReady', () => {
    it('should return false before model is loaded', () => {
      expect(reranker.isReady()).toBe(false);
    });
  });

  describe('load', () => {
    it('should handle missing model gracefully', async () => {
      // Try to load non-existent model
      await expect(reranker.load('/nonexistent/path/model.onnx')).resolves.not.toThrow();

      // Should not be ready after failed load
      expect(reranker.isReady()).toBe(false);
    });

    it('should not throw on second load attempt', async () => {
      await reranker.load('/nonexistent/model.onnx');
      await expect(reranker.load('/nonexistent/model.onnx')).resolves.not.toThrow();
    });

    it('should handle concurrent load calls', async () => {
      const loadPromises = [
        reranker.load('/nonexistent/model1.onnx'),
        reranker.load('/nonexistent/model2.onnx'),
        reranker.load('/nonexistent/model3.onnx'),
      ];

      await expect(Promise.all(loadPromises)).resolves.not.toThrow();
    });
  });

  describe('getLoadStatus', () => {
    it('should return status object', () => {
      const status = reranker.getLoadStatus();

      expect(status).toHaveProperty('isLoaded');
      expect(status).toHaveProperty('modelPath');
      expect(status).toHaveProperty('hasTokenizer');
      expect(typeof status.isLoaded).toBe('boolean');
    });
  });

  describe('rerank', () => {
    it('should return empty array for empty candidates', async () => {
      const results = await reranker.rerank('test query', [], 5);
      expect(results).toHaveLength(0);
    });

    it('should use fallback when model not loaded', async () => {
      const candidates = createMockFacts(5);
      const results = await reranker.rerank('test query', candidates, 3);

      expect(results.length).toBeLessThanOrEqual(3);
      expect(results[0]).toHaveProperty('fact');
      expect(results[0]).toHaveProperty('score');
      expect(results[0]).toHaveProperty('crossEncoderScore');
    });

    it('should respect topK parameter', async () => {
      const candidates = createMockFacts(10);
      const results = await reranker.rerank('test query', candidates, 3);

      expect(results.length).toBeLessThanOrEqual(3);
    });

    it('should return results with correct structure', async () => {
      const candidates = createMockFacts(3);
      const results = await reranker.rerank('test query', candidates, 3);

      for (const result of results) {
        expect(result).toHaveProperty('fact');
        expect(result).toHaveProperty('score');
        expect(result).toHaveProperty('vectorScore');
        expect(result).toHaveProperty('textScore');
        expect(result).toHaveProperty('decayAdjustedScore');
        expect(result).toHaveProperty('crossEncoderScore');
        expect(typeof result.score).toBe('number');
        expect(result.score).toBeGreaterThanOrEqual(0);
        expect(result.score).toBeLessThanOrEqual(1);
      }
    });

    it('should sort results by score', async () => {
      const candidates = createMockFacts(5);
      const results = await reranker.rerank('test query', candidates, 5);

      for (let i = 1; i < results.length; i++) {
        expect(results[i - 1].score).toBeGreaterThanOrEqual(results[i].score);
      }
    });

    it('should handle single candidate', async () => {
      const candidates = [createMockFact()];
      const results = await reranker.rerank('test query', candidates, 5);

      expect(results).toHaveLength(1);
    });

    it('should handle topK greater than candidates', async () => {
      const candidates = createMockFacts(3);
      const results = await reranker.rerank('test query', candidates, 10);

      expect(results.length).toBeLessThanOrEqual(3);
    });

    it('should handle facts with embeddings', async () => {
      const candidates = createMockFacts(3);

      const results = await reranker.rerank('test query', candidates, 3);

      expect(results).toHaveLength(3);
    });

    it('should handle facts with decay scores', async () => {
      const candidates = createMockFacts(3).map((f, i) => ({
        ...f,
        decayScore: 0.1 + (i * 0.3),
      }));

      const results = await reranker.rerank('test query', candidates, 3);

      expect(results).toHaveLength(3);
    });
  });

  describe('dispose', () => {
    it('should clean up resources', async () => {
      const tempReranker = new CrossEncoderReranker();
      await expect(tempReranker.dispose()).resolves.not.toThrow();
    });

    it('should be safe to call multiple times', async () => {
      await reranker.dispose();
      await expect(reranker.dispose()).resolves.not.toThrow();
    });
  });
});

// ============================================================================
// Singleton Tests
// ============================================================================

describe('getCrossEncoderReranker', () => {
  it('should return the same instance', () => {
    const instance1 = getCrossEncoderReranker();
    const instance2 = getCrossEncoderReranker();

    expect(instance1).toBe(instance2);
  });

  it('should accept config on first call', () => {
    // Note: Since this returns a singleton, this test affects other tests
    const reranker = getCrossEncoderReranker({ debug: false });
    expect(reranker).toBeInstanceOf(CrossEncoderReranker);
  });
});

describe('crossEncoderRerank', () => {
  it('should rerank using the default reranker', async () => {
    const candidates = createMockFacts(3);
    const results = await crossEncoderRerank('test query', candidates, 2);

    expect(results.length).toBeLessThanOrEqual(2);
    expect(results[0]).toHaveProperty('fact');
    expect(results[0]).toHaveProperty('crossEncoderScore');
  });
});

// ============================================================================
// Edge Cases and Error Handling
// ============================================================================

describe('Edge Cases', () => {
  let reranker: CrossEncoderReranker;

  beforeEach(() => {
    reranker = new CrossEncoderReranker({ debug: false });
  });

  afterEach(async () => {
    await reranker.dispose();
  });

  it('should handle very long queries', async () => {
    const longQuery = 'a'.repeat(1000);
    const candidates = createMockFacts(2);

    const results = await reranker.rerank(longQuery, candidates, 2);

    expect(results.length).toBeLessThanOrEqual(2);
  });

  it('should handle special characters in queries', async () => {
    const specialQuery = 'test <>&"\'\\n\\t query';
    const candidates = createMockFacts(2);

    const results = await reranker.rerank(specialQuery, candidates, 2);

    expect(results.length).toBeLessThanOrEqual(2);
  });

  it('should handle unicode in queries', async () => {
    const unicodeQuery = 'test query with unicode: \u4e2d\u6587 \u0440\u0443\u0441\u0441\u043a\u0438\u0439';
    const candidates = createMockFacts(2);

    const results = await reranker.rerank(unicodeQuery, candidates, 2);

    expect(results.length).toBeLessThanOrEqual(2);
  });

  it('should handle facts with very long text', async () => {
    const candidates = [
      createMockFact({
        text: 'a'.repeat(2000),
      }),
    ];

    const results = await reranker.rerank('test query', candidates, 1);

    expect(results).toHaveLength(1);
  });

  it('should handle empty query string', async () => {
    const candidates = createMockFacts(2);

    const results = await reranker.rerank('', candidates, 2);

    expect(results.length).toBeLessThanOrEqual(2);
  });

  it('should handle topK of 0', async () => {
    const candidates = createMockFacts(2);

    const results = await reranker.rerank('test query', candidates, 0);

    expect(results).toHaveLength(0);
  });

  it('should handle negative topK', async () => {
    const candidates = createMockFacts(2);

    const results = await reranker.rerank('test query', candidates, -1);

    // Negative topK behavior is implementation-defined, just check it doesn't crash
    expect(Array.isArray(results)).toBe(true);
  });

  it('should handle facts with missing optional fields', async () => {
    const candidates = [
      createMockFact({
        id: 'minimal-fact',
        text: 'Minimal fact',
        metadata: undefined as any,
      }),
    ];

    const results = await reranker.rerank('test query', candidates, 1);

    expect(results).toHaveLength(1);
  });
});

// ============================================================================
// Performance Tests (Lightweight)
// ============================================================================

describe('Performance', () => {
  it('should handle 100 candidates efficiently', async () => {
    const reranker = new CrossEncoderReranker({ debug: false });
    const candidates = createMockFacts(100);

    const startTime = Date.now();
    const results = await reranker.rerank('test query', candidates, 10);
    const duration = Date.now() - startTime;

    expect(results.length).toBeLessThanOrEqual(10);
    // Fallback should be very fast
    expect(duration).toBeLessThan(1000);

    await reranker.dispose();
  });

  it('should handle multiple sequential rerank calls', async () => {
    const reranker = new CrossEncoderReranker({ debug: false });
    const candidates = createMockFacts(10);

    const startTime = Date.now();

    for (let i = 0; i < 10; i++) {
      await reranker.rerank(`query ${i}`, candidates, 5);
    }

    const duration = Date.now() - startTime;

    // Should complete all 10 calls quickly with fallback
    expect(duration).toBeLessThan(2000);

    await reranker.dispose();
  });
});
