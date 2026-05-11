/**
 * TotalReclaw Skill - Server Integration Tests
 *
 * Tests the full integration with a mock HTTP server.
 * Tests authentication flows, store/search/retrieve operations,
 * and error handling scenarios.
 */

import {
  TotalReclawSkill,
  createTotalReclawSkill,
} from '../../src/totalreclaw-skill';
import type {
  TotalReclawSkillConfig,
  RememberToolParams,
  RecallToolParams,
  ForgetToolParams,
  ExportToolParams,
  OpenClawContext,
  ConversationTurn,
} from '../../src/types';
import type { Fact, RerankedResult } from '@totalreclaw/client';

// ============================================================================
// Types
// ============================================================================

interface MockServerResponse {
  status: number;
  body?: any;
  headers?: Record<string, string>;
}

interface MockHttpRequest {
  method: string;
  url: string;
  headers: Record<string, string>;
  body?: any;
}

// ============================================================================
// Mock HTTP Server (in-process simulation)
// ============================================================================

/**
 * Mock HTTP server for testing
 * Simulates the TotalReclaw server API
 */
class MockTotalReclawServer {
  private routes: Map<string, Map<string, (req: MockHttpRequest) => MockServerResponse>> = new Map();
  private users: Map<string, { salt: Buffer; hash: string }> = new Map();
  private facts: Map<string, Fact> = new Map();
  private requests: MockHttpRequest[] = [];
  private isRunning = false;
  private shouldFail = false;
  private failureType: 'network' | 'auth' | 'server' = 'network';
  private latencyMs = 0;

  constructor() {
    this.setupDefaultRoutes();
  }

  private setupDefaultRoutes(): void {
    // Register endpoint
    this.addRoute('POST', '/api/v1/register', (req) => {
      const { masterPassword } = req.body;
      const userId = `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      const salt = Buffer.from(`salt-${userId}`);

      this.users.set(userId, {
        salt,
        hash: `hash-${masterPassword}`,
      });

      return {
        status: 200,
        body: { userId, salt: salt.toString('base64') },
      };
    });

    // Login endpoint
    this.addRoute('POST', '/api/v1/login', (req) => {
      const { userId, masterPassword } = req.body;
      const user = this.users.get(userId);

      if (!user) {
        return { status: 401, body: { error: 'User not found' } };
      }

      if (user.hash !== `hash-${masterPassword}`) {
        return { status: 401, body: { error: 'Invalid password' } };
      }

      return {
        status: 200,
        body: { token: `token-${userId}` },
      };
    });

    // Store fact endpoint
    this.addRoute('POST', '/api/v1/facts', (req) => {
      const authHeader = req.headers['Authorization'];
      if (!authHeader || !authHeader.startsWith('Bearer token-')) {
        return { status: 401, body: { error: 'Unauthorized' } };
      }

      const { text, metadata, embedding, blindIndices } = req.body;
      const factId = `fact-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

      const fact: Fact = {
        id: factId,
        text,
        createdAt: new Date(),
        decayScore: 0.5,
        embedding: embedding || new Array(1024).fill(0).map(() => Math.random() * 0.1),
        metadata: metadata || {},
      };

      this.facts.set(factId, fact);

      return {
        status: 201,
        body: { factId },
      };
    });

    // Search facts endpoint
    this.addRoute('POST', '/api/v1/facts/search', (req) => {
      const authHeader = req.headers['Authorization'];
      if (!authHeader || !authHeader.startsWith('Bearer token-')) {
        return { status: 401, body: { error: 'Unauthorized' } };
      }

      const { query, k, blindTrapdoors } = req.body;
      const results: RerankedResult[] = [];

      // Simple text matching for mock
      const queryLower = query.toLowerCase();
      let count = 0;

      for (const [id, fact] of this.facts) {
        if (count >= k) break;

        if (fact.text.toLowerCase().includes(queryLower) || query === '') {
          results.push({
            fact,
            score: 0.8 - (count * 0.05),
            vectorScore: 0.7,
            textScore: 0.9,
            decayAdjustedScore: 0.75,
          });
          count++;
        }
      }

      return {
        status: 200,
        body: { results },
      };
    });

    // Get fact endpoint
    this.addRoute('GET', '/api/v1/facts/:id', (req) => {
      const authHeader = req.headers['Authorization'];
      if (!authHeader || !authHeader.startsWith('Bearer token-')) {
        return { status: 401, body: { error: 'Unauthorized' } };
      }

      const factId = req.url.split('/').pop();
      const fact = this.facts.get(factId!);

      if (!fact) {
        return { status: 404, body: { error: 'Fact not found' } };
      }

      return {
        status: 200,
        body: { fact },
      };
    });

    // Delete fact endpoint
    this.addRoute('DELETE', '/api/v1/facts/:id', (req) => {
      const authHeader = req.headers['Authorization'];
      if (!authHeader || !authHeader.startsWith('Bearer token-')) {
        return { status: 401, body: { error: 'Unauthorized' } };
      }

      const factId = req.url.split('/').pop();

      if (!this.facts.has(factId!)) {
        return { status: 404, body: { error: 'Fact not found' } };
      }

      this.facts.delete(factId!);

      return { status: 204 };
    });

    // Export endpoint
    this.addRoute('GET', '/api/v1/export', (req) => {
      const authHeader = req.headers['Authorization'];
      if (!authHeader || !authHeader.startsWith('Bearer token-')) {
        return { status: 401, body: { error: 'Unauthorized' } };
      }

      return {
        status: 200,
        body: {
          version: '1.0.0',
          exportedAt: new Date().toISOString(),
          facts: Array.from(this.facts.values()),
          lshConfig: {
            n_bits_per_table: 64,
            n_tables: 12,
            candidate_pool: 3000,
          },
          keyParams: {
            salt: Buffer.from('mock-salt').toString('base64'),
            memoryCost: 65536,
            timeCost: 3,
            parallelism: 4,
          },
        },
      };
    });
  }

  addRoute(method: string, path: string, handler: (req: MockHttpRequest) => MockServerResponse): void {
    if (!this.routes.has(path)) {
      this.routes.set(path, new Map());
    }
    this.routes.get(path)!.set(method, handler);
  }

  handleRequest(req: MockHttpRequest): MockServerResponse {
    this.requests.push(req);

    // Simulate failure if configured
    if (this.shouldFail) {
      if (this.failureType === 'network') {
        throw new Error('ECONNREFUSED');
      } else if (this.failureType === 'auth') {
        return { status: 401, body: { error: 'Unauthorized' } };
      } else {
        return { status: 500, body: { error: 'Internal server error' } };
      }
    }

    // Simulate latency
    if (this.latencyMs > 0) {
      Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, this.latencyMs);
    }

    // Find matching route
    for (const [path, handlers] of this.routes) {
      if (this.pathMatches(req.url, path)) {
        const handler = handlers.get(req.method);
        if (handler) {
          return handler(req);
        }
      }
    }

    return { status: 404, body: { error: 'Not found' } };
  }

  private pathMatches(actual: string, pattern: string): boolean {
    const actualParts = actual.split('/');
    const patternParts = pattern.split('/');

    if (actualParts.length !== patternParts.length) {
      return false;
    }

    for (let i = 0; i < patternParts.length; i++) {
      if (patternParts[i].startsWith(':')) {
        continue;
      }
      if (actualParts[i] !== patternParts[i]) {
        return false;
      }
    }

    return true;
  }

  // Test helpers
  start(): void {
    this.isRunning = true;
  }

  stop(): void {
    this.isRunning = false;
    this.facts.clear();
    this.users.clear();
    this.requests = [];
  }

  setFailure(type: 'network' | 'auth' | 'server'): void {
    this.shouldFail = true;
    this.failureType = type;
  }

  clearFailure(): void {
    this.shouldFail = false;
  }

  setLatency(ms: number): void {
    this.latencyMs = ms;
  }

  getRequests(): MockHttpRequest[] {
    return [...this.requests];
  }

  getFacts(): Fact[] {
    return Array.from(this.facts.values());
  }

  addFact(fact: Fact): void {
    this.facts.set(fact.id, fact);
  }
}

// ============================================================================
// Mock TotalReclaw Client (wraps mock server)
// ============================================================================

/**
 * Mock TotalReclaw client that uses the mock server
 */
class MockTotalReclawClientWithServer {
  private server: MockTotalReclawServer;
  private userId: string | null = null;
  private token: string | null = null;
  private salt: Buffer | null = null;

  constructor(server: MockTotalReclawServer) {
    this.server = server;
  }

  async init(): Promise<void> {
    // Simulate init
  }

  async register(masterPassword: string): Promise<string> {
    const response = this.server.handleRequest({
      method: 'POST',
      url: '/api/v1/register',
      headers: {},
      body: { masterPassword },
    });

    if (response.status !== 200) {
      throw new Error(response.body?.error || 'Registration failed');
    }

    this.userId = response.body.userId;
    this.salt = Buffer.from(response.body.salt, 'base64');

    // Auto-login after registration
    await this.login(this.userId!, masterPassword, this.salt!);

    return this.userId!;
  }

  async login(userId: string, masterPassword: string, salt: Buffer): Promise<void> {
    const response = this.server.handleRequest({
      method: 'POST',
      url: '/api/v1/login',
      headers: {},
      body: { userId, masterPassword },
    });

    if (response.status !== 200) {
      throw new Error(response.body?.error || 'Login failed');
    }

    this.userId = userId;
    this.salt = salt;
    this.token = response.body.token;
  }

  getUserId(): string | null {
    return this.userId;
  }

  getSalt(): Buffer | null {
    return this.salt;
  }

  async remember(text: string, metadata?: any): Promise<string> {
    const response = this.server.handleRequest({
      method: 'POST',
      url: '/api/v1/facts',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
      body: { text, metadata },
    });

    if (response.status === 401) {
      throw new Error('Unauthorized');
    }

    if (response.status !== 201) {
      throw new Error(response.body?.error || 'Failed to store fact');
    }

    return response.body.factId;
  }

  async recall(query: string, k: number): Promise<RerankedResult[]> {
    const response = this.server.handleRequest({
      method: 'POST',
      url: '/api/v1/facts/search',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
      body: { query, k },
    });

    if (response.status === 401) {
      throw new Error('Unauthorized');
    }

    if (response.status !== 200) {
      throw new Error(response.body?.error || 'Failed to search facts');
    }

    return response.body.results;
  }

  async forget(factId: string): Promise<void> {
    const response = this.server.handleRequest({
      method: 'DELETE',
      url: `/api/v1/facts/${factId}`,
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });

    if (response.status === 401) {
      throw new Error('Unauthorized');
    }

    if (response.status === 404) {
      throw new Error('Fact not found');
    }

    if (response.status !== 204) {
      throw new Error(response.body?.error || 'Failed to delete fact');
    }
  }

  async export(): Promise<any> {
    const response = this.server.handleRequest({
      method: 'GET',
      url: '/api/v1/export',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });

    if (response.status === 401) {
      throw new Error('Unauthorized');
    }

    if (response.status !== 200) {
      throw new Error(response.body?.error || 'Failed to export');
    }

    return response.body;
  }
}

// ============================================================================
// Test Utilities
// ============================================================================

/**
 * Create a mock conversation turn
 */
function createTurn(role: 'user' | 'assistant', content: string): ConversationTurn {
  return {
    role,
    content,
    timestamp: new Date(),
  };
}

/**
 * Create a mock OpenClaw context
 */
function createContext(overrides: Partial<OpenClawContext> = {}): OpenClawContext {
  return {
    userMessage: 'Hello!',
    history: [
      createTurn('user', 'Hi'),
      createTurn('assistant', 'Hello! How can I help?'),
    ],
    agentId: 'test-agent',
    sessionId: 'test-session',
    tokenCount: 100,
    tokenLimit: 4000,
    ...overrides,
  };
}

/**
 * Create a mock fact
 */
function createMockFact(overrides: Partial<Fact> = {}): Fact {
  return {
    id: `fact-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    text: 'Test fact',
    createdAt: new Date(),
    decayScore: 0.5,
    embedding: new Array(1024).fill(0).map(() => Math.random() * 0.1),
    metadata: {},
    ...overrides,
  };
}

// ============================================================================
// Server Integration Tests
// ============================================================================

describe('Server Integration Tests', () => {
  let mockServer: MockTotalReclawServer;
  let mockClient: MockTotalReclawClientWithServer;

  beforeEach(() => {
    mockServer = new MockTotalReclawServer();
    mockServer.start();
    mockClient = new MockTotalReclawClientWithServer(mockServer);
  });

  afterEach(() => {
    mockServer.stop();
  });

  // ============================================================================
  // Authentication Tests
  // ============================================================================

  describe('Authentication Flow', () => {
    it('should register a new user', async () => {
      const userId = await mockClient.register('test-password-123');

      expect(userId).toBeDefined();
      expect(userId).toMatch(/^user-/);
      expect(mockClient.getUserId()).toBe(userId);
      expect(mockClient.getSalt()).toBeDefined();
    });

    it('should login with existing credentials', async () => {
      // First register
      const userId = await mockClient.register('test-password-123');
      const salt = mockClient.getSalt()!;

      // Create new client and login
      const newClient = new MockTotalReclawClientWithServer(mockServer);
      await newClient.login(userId, 'test-password-123', salt);

      expect(newClient.getUserId()).toBe(userId);
    });

    it('should fail login with wrong password', async () => {
      // First register
      const userId = await mockClient.register('test-password-123');
      const salt = mockClient.getSalt()!;

      // Create new client and try to login with wrong password
      const newClient = new MockTotalReclawClientWithServer(mockServer);

      await expect(
        newClient.login(userId, 'wrong-password', salt)
      ).rejects.toThrow('Invalid password');
    });

    it('should fail login with non-existent user', async () => {
      await expect(
        mockClient.login('nonexistent-user', 'password', Buffer.from('salt'))
      ).rejects.toThrow('User not found');
    });

    it('should complete full register -> login -> access flow', async () => {
      // Register
      const userId = await mockClient.register('secure-password');
      const salt = mockClient.getSalt()!;

      // Verify can store
      const factId = await mockClient.remember('Test memory');
      expect(factId).toBeDefined();

      // Login again
      const newClient = new MockTotalReclawClientWithServer(mockServer);
      await newClient.login(userId, 'secure-password', salt);

      // Verify can access stored data
      const results = await newClient.recall('Test', 10);
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].fact.text).toBe('Test memory');
    });
  });

  // ============================================================================
  // Store -> Search -> Retrieve Flow Tests
  // ============================================================================

  describe('Store -> Search -> Retrieve Flow', () => {
    beforeEach(async () => {
      await mockClient.register('test-password');
    });

    it('should store and retrieve a single memory', async () => {
      // Store
      const factId = await mockClient.remember('User prefers dark mode');

      expect(factId).toBeDefined();
      expect(factId).toMatch(/^fact-/);

      // Search
      const results = await mockClient.recall('dark mode', 10);

      expect(results.length).toBeGreaterThan(0);
      expect(results[0].fact.text).toContain('dark mode');
    });

    it('should store multiple memories and search across them', async () => {
      // Store multiple
      await mockClient.remember('User prefers TypeScript');
      await mockClient.remember('User uses VS Code');
      await mockClient.remember('User likes dark mode');

      // Search
      const results = await mockClient.recall('prefers', 10);

      expect(results.length).toBeGreaterThan(0);
      expect(results.some(r => r.fact.text.includes('TypeScript'))).toBe(true);
    });

    it('should respect the k parameter in search', async () => {
      // Store multiple
      for (let i = 0; i < 10; i++) {
        await mockClient.remember(`Memory number ${i}`);
      }

      // Search with k=3
      const results = await mockClient.recall('Memory', 3);

      expect(results.length).toBeLessThanOrEqual(3);
    });

    it('should return empty array for no matches', async () => {
      await mockClient.remember('User likes coffee');

      const results = await mockClient.recall('xyzzy nonexistent query', 10);

      expect(results).toHaveLength(0);
    });

    it('should handle case-insensitive search', async () => {
      await mockClient.remember('User prefers DARK Mode');

      const results = await mockClient.recall('dark mode', 10);

      expect(results.length).toBeGreaterThan(0);
    });

    it('should store memories with metadata', async () => {
      const metadata = {
        importance: 0.8,
        source: 'explicit',
        tags: ['preference'],
      };

      const factId = await mockClient.remember('User prefers TypeScript', metadata);

      const results = await mockClient.recall('TypeScript', 10);
      expect(results[0].fact.metadata).toEqual(metadata);
    });

    it('should support delete operation', async () => {
      const factId = await mockClient.remember('Temporary memory');

      // Verify stored
      let results = await mockClient.recall('Temporary', 10);
      expect(results.length).toBeGreaterThan(0);

      // Delete
      await mockClient.forget(factId);

      // Verify deleted
      results = await mockClient.recall('Temporary', 10);
      expect(results).toHaveLength(0);
    });

    it('should throw error when deleting non-existent fact', async () => {
      await expect(
        mockClient.forget('nonexistent-fact-id')
      ).rejects.toThrow('Fact not found');
    });
  });

  // ============================================================================
  // Export Flow Tests
  // ============================================================================

  describe('Export Flow', () => {
    beforeEach(async () => {
      await mockClient.register('test-password');
    });

    it('should export all memories', async () => {
      await mockClient.remember('Memory 1');
      await mockClient.remember('Memory 2');
      await mockClient.remember('Memory 3');

      const exported = await mockClient.export();

      expect(exported.version).toBe('1.0.0');
      expect(exported.facts).toBeDefined();
      expect(exported.facts.length).toBe(3);
      expect(exported.lshConfig).toBeDefined();
      expect(exported.keyParams).toBeDefined();
    });

    it('should export empty memories list', async () => {
      const exported = await mockClient.export();

      expect(exported.facts).toHaveLength(0);
    });

    it('should include configuration in export', async () => {
      const exported = await mockClient.export();

      expect(exported.lshConfig.n_bits_per_table).toBeDefined();
      expect(exported.lshConfig.n_tables).toBeDefined();
      expect(exported.keyParams.salt).toBeDefined();
    });
  });

  // ============================================================================
  // Error Handling Tests
  // ============================================================================

  describe('Error Handling', () => {
    beforeEach(async () => {
      await mockClient.register('test-password');
    });

    describe('Network errors', () => {
      it('should handle network connection failure', async () => {
        mockServer.setFailure('network');

        await expect(
          mockClient.remember('Test memory')
        ).rejects.toThrow('ECONNREFUSED');
      });

      it('should handle network timeout gracefully', async () => {
        mockServer.setLatency(100);

        // Should still complete, just slower
        const factId = await mockClient.remember('Test memory');
        expect(factId).toBeDefined();

        mockServer.setLatency(0);
      });
    });

    describe('Authentication errors', () => {
      it('should handle 401 unauthorized on store', async () => {
        mockServer.setFailure('auth');

        await expect(
          mockClient.remember('Test memory')
        ).rejects.toThrow('Unauthorized');
      });

      it('should handle 401 unauthorized on search', async () => {
        mockServer.setFailure('auth');

        await expect(
          mockClient.recall('test', 10)
        ).rejects.toThrow('Unauthorized');
      });

      it('should handle 401 unauthorized on export', async () => {
        mockServer.setFailure('auth');

        await expect(
          mockClient.export()
        ).rejects.toThrow('Unauthorized');
      });
    });

    describe('Server errors', () => {
      it('should handle 500 server error', async () => {
        mockServer.setFailure('server');

        await expect(
          mockClient.remember('Test memory')
        ).rejects.toThrow('Internal server error');
      });

      it('should recover after server error clears', async () => {
        // Cause error
        mockServer.setFailure('server');
        await expect(
          mockClient.remember('Test memory')
        ).rejects.toThrow();

        // Clear error
        mockServer.clearFailure();

        // Should work now
        const factId = await mockClient.remember('Test memory');
        expect(factId).toBeDefined();
      });
    });

    describe('Validation errors', () => {
      it('should handle empty text in store', async () => {
        // This depends on server validation
        // Mock server accepts it, but we test the flow
        const factId = await mockClient.remember('');
        expect(factId).toBeDefined();
      });

      it('should handle very long text in store', async () => {
        const longText = 'a'.repeat(10000);
        const factId = await mockClient.remember(longText);
        expect(factId).toBeDefined();
      });

      it('should handle special characters in search query', async () => {
        await mockClient.remember('Test memory with special chars: <>&"');

        const results = await mockClient.recall('<>&"', 10);
        expect(results.length).toBeGreaterThan(0);
      });
    });
  });

  // ============================================================================
  // Concurrent Operations Tests
  // ============================================================================

  describe('Concurrent Operations', () => {
    beforeEach(async () => {
      await mockClient.register('test-password');
    });

    it('should handle concurrent stores', async () => {
      const promises = Array.from({ length: 10 }, (_, i) =>
        mockClient.remember(`Memory ${i}`)
      );

      const factIds = await Promise.all(promises);

      expect(factIds).toHaveLength(10);
      factIds.forEach(id => expect(id).toMatch(/^fact-/));
    });

    it('should handle concurrent searches', async () => {
      await mockClient.remember('Memory 1');
      await mockClient.remember('Memory 2');

      const promises = Array.from({ length: 5 }, () =>
        mockClient.recall('Memory', 10)
      );

      const results = await Promise.all(promises);

      results.forEach(r => {
        expect(r.length).toBeGreaterThan(0);
      });
    });

    it('should handle mixed concurrent operations', async () => {
      const operations = [
        mockClient.remember('Memory 1'),
        mockClient.recall('test', 10),
        mockClient.remember('Memory 2'),
        mockClient.recall('Memory', 10),
        mockClient.remember('Memory 3'),
      ];

      const results = await Promise.all(operations);

      expect(results).toHaveLength(5);
    });
  });

  // ============================================================================
  // Performance Tests
  // ============================================================================

  describe('Performance', () => {
    beforeEach(async () => {
      await mockClient.register('test-password');
    });

    it('should complete store operation quickly', async () => {
      const startTime = Date.now();

      await mockClient.remember('Test memory');

      const duration = Date.now() - startTime;
      expect(duration).toBeLessThan(100); // Should be nearly instant
    });

    it('should complete search operation quickly with many memories', async () => {
      // Store 100 memories
      for (let i = 0; i < 100; i++) {
        await mockClient.remember(`Memory number ${i}`);
      }

      const startTime = Date.now();

      const results = await mockClient.recall('Memory', 10);

      const duration = Date.now() - startTime;
      expect(duration).toBeLessThan(100);
      expect(results.length).toBeLessThanOrEqual(10);
    });

    it('should handle export of many memories efficiently', async () => {
      // Store 50 memories
      for (let i = 0; i < 50; i++) {
        await mockClient.remember(`Memory ${i}`);
      }

      const startTime = Date.now();

      const exported = await mockClient.export();

      const duration = Date.now() - startTime;
      expect(duration).toBeLessThan(100);
      expect(exported.facts.length).toBe(50);
    });
  });
});
