/**
 * BrainX V5 - Unit Tests for db.js
 * Run with: node --test tests/unit/db.test.js
 */

const { describe, it, before, after } = require('node:test');
const assert = require('node:assert');

// Mock pg module
const mockQueryResults = [];
const mockClient = {
  query: async (text, params) => {
    mockQueryResults.push({ text, params });
    return { rows: [{ ok: 1 }] };
  },
  release: () => {}
};

const mockPool = {
  query: async (text, params) => {
    mockQueryResults.push({ text, params });
    return { rows: [{ ok: 1 }] };
  },
  connect: async () => mockClient
};

// Mock the pg module before requiring db.js
const Module = require('module');
const originalRequire = Module.prototype.require;
Module.prototype.require = function(id) {
  if (id === 'pg') {
    return { Pool: function() { return mockPool; } };
  }
  return originalRequire.apply(this, arguments);
};

// Now require db.js with the mock
const db = require('../../lib/db');

// Restore original require
Module.prototype.require = originalRequire;

describe('db', () => {
  before(() => {
    mockQueryResults.length = 0;
  });

  after(() => {
    mockQueryResults.length = 0;
  });

  describe('query', () => {
    it('should execute query and return results', async () => {
      const result = await db.query('SELECT 1 as ok');
      
      assert.strictEqual(result.rows[0].ok, 1);
      assert.strictEqual(mockQueryResults.length, 1);
      assert.strictEqual(mockQueryResults[0].text, 'SELECT 1 as ok');
    });

    it('should pass parameters correctly', async () => {
      await db.query('SELECT * FROM test WHERE id = $1', [123]);
      
      assert.deepStrictEqual(mockQueryResults[mockQueryResults.length - 1].params, [123]);
    });
  });

  describe('withClient', () => {
    it('should provide client to callback', async () => {
      let clientReceived = null;
      await db.withClient(async (client) => {
        clientReceived = client;
        return 'result';
      });
      
      assert.strictEqual(clientReceived !== null, true);
      assert.strictEqual(typeof clientReceived.query, 'function');
    });

    it('should release client after use', async () => {
      let released = false;
      const testClient = {
        ...mockClient,
        release: () => { released = true; }
      };
      
      // Temporarily override pool.connect
      const originalConnect = mockPool.connect;
      mockPool.connect = async () => testClient;
      
      await db.withClient(async () => 'result');
      
      assert.strictEqual(released, true);
      
      // Restore
      mockPool.connect = originalConnect;
    });
  });

  describe('health', () => {
    it('should return true when database is healthy', async () => {
      const isHealthy = await db.health();
      
      assert.strictEqual(isHealthy, true);
    });
  });
});
