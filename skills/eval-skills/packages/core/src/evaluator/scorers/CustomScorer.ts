import type { Scorer, ScorerResult } from "./BaseScorer.js";
import type { ExpectedOutput } from "../../types/index.js";
import path from "node:path";
import { Worker } from "node:worker_threads";

/**
 * 自定义评分器
 * 动态加载用户提供的 JS/TS 文件作为评分函数
 * 使用 Worker 线程进行隔离执行
 */
export class CustomScorer implements Scorer {
  readonly type = "custom";

  async score(output: unknown, expected: ExpectedOutput): Promise<ScorerResult> {
    if (!expected.customScorerPath) {
      return {
        score: 0,
        passed: false,
        reason: "Missing 'customScorerPath' in expected output"
      };
    }

    const scorerPath = path.resolve(expected.customScorerPath);

    // Worker code to import and execute the scorer
    // Using CJS require for worker runtime dependencies, but dynamic import for the scorer module
    const workerCode = `
      const { parentPort, workerData } = require('node:worker_threads');
      const { pathToFileURL } = require('node:url');
      
      async function run() {
        try {
          const { scorerPath, output, expected } = workerData;
          const modulePath = pathToFileURL(scorerPath).href;
          const scorerModule = await import(modulePath);
          const scorerFn = scorerModule.default;
          
          if (typeof scorerFn !== 'function') {
            throw new Error('Default export is not a function');
          }
          
          const result = await scorerFn(output, expected);
          parentPort.postMessage({ success: true, result });
        } catch (error) {
          parentPort.postMessage({ success: false, error: error.message });
        }
      }
      
      run();
    `;

    return new Promise<ScorerResult>((resolve) => {
      const worker = new Worker(workerCode, {
        eval: true,
        workerData: { scorerPath, output, expected },
        resourceLimits: { maxOldGenerationSizeMb: 128 },
      });

      const timeout = setTimeout(() => {
        worker.terminate();
        resolve({
          score: 0,
          passed: false,
          reason: "Custom scorer timed out (5s limit)"
        });
      }, 5000);

      worker.on("message", (msg) => {
        clearTimeout(timeout);
        // We don't terminate immediately here to allow graceful exit if needed, 
        // but since it's a one-off script, we can terminate.
        worker.terminate();

        if (!msg.success) {
          resolve({
            score: 0,
            passed: false,
            reason: `Custom scorer error: ${msg.error}`
          });
          return;
        }

        const result = msg.result;
        
        if (typeof result === "boolean") {
          resolve(result 
              ? { score: 1.0, passed: true }
              : { score: 0.0, passed: false, reason: "Custom scorer returned false" });
        } else if (typeof result === "number") {
           const score = Math.max(0, Math.min(1, result));
           resolve({
              passed: score >= 1.0,
              score,
              reason: "Custom scorer returned score " + result,
           });
        } else if (typeof result === 'object' && result !== null) {
            resolve({
              passed: !!result.passed,
              score: typeof result.score === 'number' ? result.score : (result.passed ? 1 : 0),
              reason: result.reason || "Custom scorer execution",
            });
        } else {
            resolve({
                score: 0,
                passed: false,
                reason: `Custom scorer returned invalid type: ${typeof result}`
            });
        }
      });

      worker.on("error", (err) => {
        clearTimeout(timeout);
        resolve({
          score: 0,
          passed: false,
          reason: `Worker error: ${err.message}`
        });
      });
      
      worker.on("exit", (code) => {
          if (code !== 0) {
              clearTimeout(timeout);
              // Only resolve if not already resolved (Promise handles this internally, 
              // but we want to avoid resolving with exit code error if message was successful)
              // Actually if message was received, promise is resolved. 
              // This is for crash cases.
          }
      });
    });
  }
}
