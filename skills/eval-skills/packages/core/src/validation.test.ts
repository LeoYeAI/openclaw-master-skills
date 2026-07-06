import { validateSkill, validateBenchmark } from "./validation.js";

describe("validateSkill", () => {
  const validSkill = {
    id: "test-skill",
    name: "Test Skill",
    version: "1.0.0",
    description: "A test skill",
    tags: ["test"],
    inputSchema: { type: "object" },
    outputSchema: { type: "object" },
    adapterType: "http",
    entrypoint: "http://localhost:3000",
    metadata: { author: "tester" },
  };

  it("validates a correct skill", () => {
    const result = validateSkill(validSkill);
    expect(result.id).toBe("test-skill");
    expect(result.tags).toEqual(["test"]);
  });

  it("rejects invalid id format", () => {
    expect(() => validateSkill({ ...validSkill, id: "UPPER CASE" })).toThrow();
  });

  it("rejects invalid version format", () => {
    expect(() => validateSkill({ ...validSkill, version: "abc" })).toThrow();
  });

  it("rejects invalid adapterType", () => {
    expect(() => validateSkill({ ...validSkill, adapterType: "invalid" })).toThrow();
  });

  it("rejects empty entrypoint", () => {
    expect(() => validateSkill({ ...validSkill, entrypoint: "" })).toThrow();
  });

  it("applies defaults for missing optional fields", () => {
    const minimal = {
      id: "minimal",
      name: "Min",
      version: "0.1.0",
      description: "",
      adapterType: "http",
      entrypoint: "http://localhost",
    };
    const result = validateSkill(minimal);
    expect(result.tags).toEqual([]);
    expect(result.metadata).toEqual({});
  });
});

describe("validateBenchmark", () => {
  const validBenchmark = {
    id: "test-bench",
    name: "Test Benchmark",
    version: "1.0.0",
    domain: "testing",
    scoringMethod: "mean",
    tasks: [
      {
        id: "t1",
        description: "Test task",
        inputData: { x: 1 },
        expectedOutput: { type: "exact", value: "1" },
        evaluator: { type: "exact" },
      },
    ],
  };

  it("validates a correct benchmark", () => {
    const result = validateBenchmark(validBenchmark);
    expect(result.id).toBe("test-bench");
    expect(result.tasks).toHaveLength(1);
  });

  it("rejects invalid scoringMethod", () => {
    expect(() =>
      validateBenchmark({ ...validBenchmark, scoringMethod: "invalid" }),
    ).toThrow();
  });

  it("rejects empty id", () => {
    expect(() => validateBenchmark({ ...validBenchmark, id: "" })).toThrow();
  });

  it("applies default metadata", () => {
    const result = validateBenchmark(validBenchmark);
    expect(result.metadata).toEqual({});
  });
});
