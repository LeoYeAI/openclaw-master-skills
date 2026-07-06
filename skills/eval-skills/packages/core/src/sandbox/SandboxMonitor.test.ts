/**
 * @file sandbox/SandboxMonitor.test.ts
 * @description SandboxMonitor 单元测试
 */

import { describe, it, expect } from "vitest";
import { SandboxMonitor } from "./SandboxMonitor.js";
import type { SandboxViolation } from "./types.js";

function makeViolation(
  overrides: Partial<SandboxViolation> = {},
): SandboxViolation {
  return {
    type: "command_injection",
    severity: "critical",
    detail: "test detail",
    timestamp: new Date().toISOString(),
    skillId: "test_skill",
    ...overrides,
  };
}

describe("SandboxMonitor — stats accumulation", () => {
  it("should accumulate violation counts correctly", () => {
    const monitor = new SandboxMonitor();

    monitor.recordViolation(makeViolation({ severity: "critical" }));
    monitor.recordViolation(makeViolation({ severity: "error", type: "path_traversal" }));
    monitor.recordViolation(makeViolation({ severity: "warn", type: "output_truncated" }));

    const stats = monitor.getStats("test_skill")!;
    expect(stats.totalViolations).toBe(3);
    expect(stats.criticalCount).toBe(1);
    expect(stats.errorCount).toBe(1);
    expect(stats.warnCount).toBe(1);
    expect(stats.byType["command_injection"]).toBe(1);
    expect(stats.byType["path_traversal"]).toBe(1);
  });

  it("should track multiple skills independently", () => {
    const monitor = new SandboxMonitor();

    monitor.recordViolation(makeViolation({ skillId: "skill_a" }));
    monitor.recordViolation(makeViolation({ skillId: "skill_b" }));
    monitor.recordViolation(makeViolation({ skillId: "skill_a" }));

    const statsA = monitor.getStats("skill_a")!;
    const statsB = monitor.getStats("skill_b")!;

    expect(statsA.totalViolations).toBe(2);
    expect(statsB.totalViolations).toBe(1);
  });
});

describe("SandboxMonitor — circuit breaker", () => {
  it("should trip circuit breaker after threshold critical violations", () => {
    const monitor = new SandboxMonitor({
      circuitBreakerThreshold: 2,
    });

    const brokenEvents: any[] = [];
    monitor.on("circuit-open", (e) => brokenEvents.push(e));

    expect(monitor.isCircuitBroken("evil_skill")).toBe(false);

    monitor.recordViolation(makeViolation({ skillId: "evil_skill", severity: "critical" }));
    expect(monitor.isCircuitBroken("evil_skill")).toBe(false); // 还没到阈值

    monitor.recordViolation(makeViolation({ skillId: "evil_skill", severity: "critical" }));
    expect(monitor.isCircuitBroken("evil_skill")).toBe(true); // 达到阈值

    // 再次触发 critical
    monitor.recordViolation(makeViolation({ skillId: "evil_skill", severity: "critical" }));
    expect(monitor.isCircuitBroken("evil_skill")).toBe(true);

    expect(brokenEvents.length).toBe(1);
    expect(brokenEvents[0].skillId).toBe("evil_skill");
  });

  it("should not trip circuit breaker for non-critical violations", () => {
    const monitor = new SandboxMonitor({
      circuitBreakerThreshold: 2,
    });

    monitor.recordViolation(makeViolation({ skillId: "skill_x", severity: "warn" }));
    monitor.recordViolation(makeViolation({ skillId: "skill_x", severity: "warn" }));
    monitor.recordViolation(makeViolation({ skillId: "skill_x", severity: "error" }));

    expect(monitor.isCircuitBroken("skill_x")).toBe(false);
  });

  it("should allow manual circuit breaker reset", () => {
    const monitor = new SandboxMonitor({
      circuitBreakerThreshold: 1,
    });

    monitor.recordViolation(makeViolation({ skillId: "skill_y", severity: "critical" }));
    expect(monitor.isCircuitBroken("skill_y")).toBe(true);

    monitor.resetCircuit("skill_y");
    expect(monitor.isCircuitBroken("skill_y")).toBe(false);
  });
});

describe("SandboxMonitor — report generation", () => {
  it("should generate markdown report with violation summary", () => {
    const monitor = new SandboxMonitor({ circuitBreakerThreshold: 1 });

    monitor.recordViolation(makeViolation({ skillId: "bad_skill_1", severity: "critical" }));
    monitor.recordViolation(makeViolation({ skillId: "bad_skill_2", severity: "warn" }));

    const report = monitor.generateReport();

    expect(report).toContain("Sandbox Security Report");
    expect(report).toContain("bad_skill_1");
    expect(report).toContain("bad_skill_2");
    expect(report).toContain("BLOCKED"); // bad_skill_1 应被熔断
    expect(report).toContain("OK");  // bad_skill_2 正常
  });

  it("should return clean report when no violations", () => {
    const monitor = new SandboxMonitor();
    const report = monitor.generateReport();
    expect(report).toContain("No violations recorded");
  });
});

describe("SandboxMonitor — events", () => {
  it("should emit violation event for each record", () => {
    const monitor = new SandboxMonitor();
    const events: SandboxViolation[] = [];
    monitor.on("violation", (v) => events.push(v));

    monitor.recordViolation(makeViolation({ skillId: "skill_z" }));
    monitor.recordViolation(makeViolation({ skillId: "skill_z", severity: "warn" }));

    expect(events.length).toBe(2);
  });
});
