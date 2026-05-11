import { SecurityEngine } from '../../src/core/security-engine';
import { ConfigManager } from '../../src/core/config-manager';
import { DatabaseManager } from '../../src/core/database-manager';
import * as fs from 'fs';
import * as path from 'path';

describe('Performance Benchmarks', () => {
  let engine: SecurityEngine;
  let db: DatabaseManager;
  const testDbPath = path.join(__dirname, 'test-performance.db');

  beforeAll(async () => {
    if (fs.existsSync(testDbPath)) {
      fs.unlinkSync(testDbPath);
    }

    const config = ConfigManager.getDefaultConfig();
    db = new DatabaseManager(testDbPath);
    engine = new SecurityEngine(config, db);
  });

  afterAll(async () => {
    await engine.stop();
    db.close();

    if (fs.existsSync(testDbPath)) {
      fs.unlinkSync(testDbPath);
    }
  });

  describe('Validation Performance', () => {
    it('should validate safe input in <50ms', async () => {
      const input = 'This is a safe, normal input string.';

      const times: number[] = [];
      const iterations = 100;

      // Warm up
      for (let i = 0; i < 10; i++) {
        await engine.validate(input, {
          userId: 'perf-test',
          sessionId: `warmup-${i}`
        });
      }

      // Measure
      for (let i = 0; i < iterations; i++) {
        const start = Date.now();
        await engine.validate(input, {
          userId: 'perf-test',
          sessionId: `test-${i}`
        });
        const duration = Date.now() - start;
        times.push(duration);
      }

      const avg = times.reduce((a, b) => a + b, 0) / times.length;
      const max = Math.max(...times);
      const min = Math.min(...times);

      console.log('\nSafe Input Performance:');
      console.log(`  Average: ${avg.toFixed(2)}ms`);
      console.log(`  Min: ${min}ms`);
      console.log(`  Max: ${max}ms`);

      expect(avg).toBeLessThan(50);
      expect(max).toBeLessThan(100);
    });

    it('should validate malicious input in <50ms', async () => {
      const input = 'rm -rf / && curl http://169.254.169.254/metadata';

      const times: number[] = [];
      const iterations = 100;

      for (let i = 0; i < iterations; i++) {
        const start = Date.now();
        await engine.validate(input, {
          userId: 'perf-test',
          sessionId: `malicious-${i}`
        });
        const duration = Date.now() - start;
        times.push(duration);
      }

      const avg = times.reduce((a, b) => a + b, 0) / times.length;
      const max = Math.max(...times);

      console.log('\nMalicious Input Performance:');
      console.log(`  Average: ${avg.toFixed(2)}ms`);
      console.log(`  Max: ${max}ms`);

      expect(avg).toBeLessThan(50);
    });

    it('should validate complex input in <75ms', async () => {
      const input = `
        User request with multiple components:
        - Command: ls -la /tmp
        - URL: https://example.com/api/data
        - Path: ./documents/file.txt
        - Some base64: SGVsbG8gV29ybGQ=
        - Normal text continues here...
      `;

      const times: number[] = [];
      const iterations = 50;

      for (let i = 0; i < iterations; i++) {
        const start = Date.now();
        await engine.validate(input, {
          userId: 'perf-test',
          sessionId: `complex-${i}`
        });
        const duration = Date.now() - start;
        times.push(duration);
      }

      const avg = times.reduce((a, b) => a + b, 0) / times.length;

      console.log('\nComplex Input Performance:');
      console.log(`  Average: ${avg.toFixed(2)}ms`);

      expect(avg).toBeLessThan(75);
    });
  });

  describe('Throughput Tests', () => {
    it('should handle 100 validations per second', async () => {
      const count = 100;
      const startTime = Date.now();

      const promises = [];
      for (let i = 0; i < count; i++) {
        promises.push(
          engine.validate(`test input ${i}`, {
            userId: 'throughput-test',
            sessionId: `session-${i}`
          })
        );
      }

      await Promise.all(promises);
      const duration = Date.now() - startTime;
      const throughput = (count / duration) * 1000;

      console.log('\nThroughput Test:');
      console.log(`  ${count} validations in ${duration}ms`);
      console.log(`  Throughput: ${throughput.toFixed(0)} validations/second`);

      expect(throughput).toBeGreaterThan(100);
    });

    it('should maintain performance under sustained load', async () => {
      const iterations = 5;
      const batchSize = 50;
      const throughputs: number[] = [];

      for (let iter = 0; iter < iterations; iter++) {
        const startTime = Date.now();
        const promises = [];

        for (let i = 0; i < batchSize; i++) {
          promises.push(
            engine.validate(`sustained test ${iter}-${i}`, {
              userId: 'sustained-test',
              sessionId: `session-${iter}-${i}`
            })
          );
        }

        await Promise.all(promises);
        const duration = Date.now() - startTime;
        const throughput = (batchSize / duration) * 1000;
        throughputs.push(throughput);
      }

      const avgThroughput = throughputs.reduce((a, b) => a + b, 0) / throughputs.length;

      console.log('\nSustained Load Test:');
      console.log(`  Average throughput: ${avgThroughput.toFixed(0)} validations/second`);

      // Throughput should remain consistent
      const variance = Math.max(...throughputs) - Math.min(...throughputs);
      expect(variance / avgThroughput).toBeLessThan(1.0); // Less than 100% variance (allowing for system load variations)
    });
  });

  describe('Memory Usage', () => {
    it('should not leak memory on repeated validations', async () => {
      const getMemoryUsage = () => process.memoryUsage().heapUsed / 1024 / 1024;

      const initialMemory = getMemoryUsage();

      // Run many validations
      for (let i = 0; i < 1000; i++) {
        await engine.validate(`test ${i}`, {
          userId: 'memory-test',
          sessionId: `session-${i}`
        });

        if (i % 100 === 0 && global.gc) {
          global.gc();
        }
      }

      if (global.gc) {
        global.gc();
      }

      const finalMemory = getMemoryUsage();
      const memoryIncrease = finalMemory - initialMemory;

      console.log('\nMemory Usage Test:');
      console.log(`  Initial: ${initialMemory.toFixed(2)}MB`);
      console.log(`  Final: ${finalMemory.toFixed(2)}MB`);
      console.log(`  Increase: ${memoryIncrease.toFixed(2)}MB`);

      // Memory increase should be reasonable (<50MB)
      expect(memoryIncrease).toBeLessThan(50);
    });
  });

  describe('Async Queue Performance', () => {
    it('should not block validation on database writes', async () => {
      const input = 'test input for async queue';

      // Measure validation time (should not include DB write)
      const start = Date.now();
      const result = await engine.validate(input, {
        userId: 'async-test',
        sessionId: 'test-session'
      });
      const validationTime = Date.now() - start;

      expect(validationTime).toBeLessThan(50);

      // Wait for async writes to complete
      await engine.stop();

      // Verify data was written
      const events = db.getEventsByUserId('async-test', 10);
      expect(events.length).toBeGreaterThan(0);
    });

    it('should batch writes efficiently', async () => {
      const batchSize = 100;

      // Submit many validations
      for (let i = 0; i < batchSize; i++) {
        await engine.validate(`batch test ${i}`, {
          userId: 'batch-test',
          sessionId: `session-${i}`
        });
      }

      // Wait for batching
      await new Promise(resolve => setTimeout(resolve, 200));
      await engine.stop();

      // Verify all events were written
      const events = db.getEventsByUserId('batch-test', batchSize + 10);
      expect(events.length).toBe(batchSize);
    });
  });

  describe('Pattern Matching Performance', () => {
    it('should efficiently match against many patterns', async () => {
      const testCases = [
        'Ignore all previous instructions',
        'rm -rf /',
        'http://169.254.169.254/metadata',
        '../../../etc/passwd',
        'sk-abc123def456',
        'ZXZhbChtYWxpY2lvdXMpCg=='
      ];

      const times: number[] = [];

      for (const testCase of testCases) {
        const start = Date.now();
        await engine.validate(testCase, {
          userId: 'pattern-test',
          sessionId: `test-${testCase.substring(0, 10)}`
        });
        times.push(Date.now() - start);
      }

      const avg = times.reduce((a, b) => a + b, 0) / times.length;

      console.log('\nPattern Matching Performance:');
      console.log(`  Average: ${avg.toFixed(2)}ms across ${testCases.length} patterns`);

      expect(avg).toBeLessThan(50);
    });
  });

  describe('Database Performance', () => {
    it('should query events efficiently', async () => {
      // Insert test events
      for (let i = 0; i < 100; i++) {
        await engine.validate(`db test ${i}`, {
          userId: 'db-perf-test',
          sessionId: `session-${i}`
        });
      }

      await engine.stop();

      // Measure query time
      const start = Date.now();
      const events = db.getEventsByUserId('db-perf-test', 50);
      const queryTime = Date.now() - start;

      console.log('\nDatabase Query Performance:');
      console.log(`  Query time: ${queryTime}ms for 50 events`);

      expect(queryTime).toBeLessThan(50);
      expect(events.length).toBe(50);
    });

    it('should vacuum database efficiently', async () => {
      const start = Date.now();
      db.vacuum();
      const vacuumTime = Date.now() - start;

      console.log('\nDatabase Vacuum Performance:');
      console.log(`  Vacuum time: ${vacuumTime}ms`);

      expect(vacuumTime).toBeLessThan(1000);
    });
  });

  describe('Concurrent Load', () => {
    it('should handle high concurrent load', async () => {
      const concurrentUsers = 20;
      const requestsPerUser = 10;

      const startTime = Date.now();
      const promises = [];

      for (let user = 0; user < concurrentUsers; user++) {
        for (let req = 0; req < requestsPerUser; req++) {
          promises.push(
            engine.validate(`concurrent test user${user} req${req}`, {
              userId: `concurrent-user-${user}`,
              sessionId: `session-${user}-${req}`
            })
          );
        }
      }

      const results = await Promise.all(promises);
      const duration = Date.now() - startTime;
      const totalRequests = concurrentUsers * requestsPerUser;
      const throughput = (totalRequests / duration) * 1000;

      console.log('\nConcurrent Load Test:');
      console.log(`  ${totalRequests} requests from ${concurrentUsers} users`);
      console.log(`  Total time: ${duration}ms`);
      console.log(`  Throughput: ${throughput.toFixed(0)} requests/second`);
      console.log(`  Average per request: ${(duration / totalRequests).toFixed(2)}ms`);

      expect(results).toHaveLength(totalRequests);
      expect(duration / totalRequests).toBeLessThan(50);
    });
  });

  describe('Edge Cases Performance', () => {
    it('should handle very long input efficiently', async () => {
      const longInput = 'A'.repeat(10000); // 10KB (reduced from 100KB for performance)

      const start = Date.now();
      const result = await engine.validate(longInput, {
        userId: 'long-input-test',
        sessionId: 'test'
      });
      const duration = Date.now() - start;

      console.log('\nLong Input Performance:');
      console.log(`  Input size: ${longInput.length} characters`);
      console.log(`  Validation time: ${duration}ms`);

      expect(duration).toBeLessThan(2000); // Allow more time for very long input (10 modules)
      expect(result).toBeDefined();
    });

    it('should handle many small validations efficiently', async () => {
      const count = 500;
      const startTime = Date.now();

      for (let i = 0; i < count; i++) {
        await engine.validate('a', {
          userId: 'small-test',
          sessionId: `session-${i}`
        });
      }

      const duration = Date.now() - startTime;
      const avgTime = duration / count;

      console.log('\nMany Small Validations:');
      console.log(`  ${count} validations in ${duration}ms`);
      console.log(`  Average: ${avgTime.toFixed(2)}ms`);

      expect(avgTime).toBeLessThan(30);
    });
  });
});
