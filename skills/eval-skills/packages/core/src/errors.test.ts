import { EvalSkillsError, EvalSkillsErrorCode } from "./errors.js";

describe("EvalSkillsError", () => {
  describe("constructor", () => {
    it("should create error with code, message, and details", () => {
      const error = new EvalSkillsError(
        EvalSkillsErrorCode.SKILL_NOT_FOUND,
        "Skill not found",
        { skillId: "test-skill" }
      );

      expect(error.code).toBe(EvalSkillsErrorCode.SKILL_NOT_FOUND);
      expect(error.details).toEqual({ skillId: "test-skill" });
    });

    it("should create error without details", () => {
      const error = new EvalSkillsError(EvalSkillsErrorCode.CONFIG_INVALID, "Invalid config");

      expect(error.code).toBe(EvalSkillsErrorCode.CONFIG_INVALID);
      expect(error.details).toBeUndefined();
    });
  });

  describe("message formatting", () => {
    it("should include error code prefix in message", () => {
      const error = new EvalSkillsError(EvalSkillsErrorCode.SKILL_NOT_FOUND, "Skill not found");

      expect(error.message).toBe("[E1001] Skill not found");
    });

    it("should format message correctly for all error codes", () => {
      const testCases: Array<{ code: EvalSkillsErrorCode; expectedPrefix: string }> = [
        { code: EvalSkillsErrorCode.SKILL_NOT_FOUND, expectedPrefix: "[E1001]" },
        { code: EvalSkillsErrorCode.SKILL_SCHEMA_INVALID, expectedPrefix: "[E1002]" },
        { code: EvalSkillsErrorCode.SKILL_INVOKE_TIMEOUT, expectedPrefix: "[E1003]" },
        { code: EvalSkillsErrorCode.SKILL_INVOKE_FAILED, expectedPrefix: "[E1004]" },
        { code: EvalSkillsErrorCode.ADAPTER_NOT_FOUND, expectedPrefix: "[E2001]" },
        { code: EvalSkillsErrorCode.ADAPTER_AUTH_FAILED, expectedPrefix: "[E2002]" },
        { code: EvalSkillsErrorCode.ADAPTER_CONN_FAILED, expectedPrefix: "[E2003]" },
        { code: EvalSkillsErrorCode.BENCHMARK_NOT_FOUND, expectedPrefix: "[E3001]" },
        { code: EvalSkillsErrorCode.BENCHMARK_SCHEMA_ERR, expectedPrefix: "[E3002]" },
        { code: EvalSkillsErrorCode.EVAL_PARTIAL_FAIL, expectedPrefix: "[E4001]" },
        { code: EvalSkillsErrorCode.EVAL_THRESHOLD_FAIL, expectedPrefix: "[E4002]" },
        { code: EvalSkillsErrorCode.EVAL_NO_TASKS, expectedPrefix: "[E4003]" },
        { code: EvalSkillsErrorCode.CONFIG_INVALID, expectedPrefix: "[E5001]" },
        { code: EvalSkillsErrorCode.CONFIG_LLM_MISSING, expectedPrefix: "[E5002]" },
      ];

      for (const { code, expectedPrefix } of testCases) {
        const error = new EvalSkillsError(code, "Test message");
        expect(error.message.startsWith(expectedPrefix)).toBe(true);
      }
    });
  });

  describe("error name", () => {
    it("should have name set to EvalSkillsError", () => {
      const error = new EvalSkillsError(EvalSkillsErrorCode.SKILL_NOT_FOUND, "Test");

      expect(error.name).toBe("EvalSkillsError");
    });
  });

  describe("Error inheritance", () => {
    it("should be instanceof Error", () => {
      const error = new EvalSkillsError(EvalSkillsErrorCode.SKILL_NOT_FOUND, "Test");

      expect(error).toBeInstanceOf(Error);
    });

    it("should be instanceof EvalSkillsError", () => {
      const error = new EvalSkillsError(EvalSkillsErrorCode.SKILL_NOT_FOUND, "Test");

      expect(error).toBeInstanceOf(EvalSkillsError);
    });

    it("should have stack trace", () => {
      const error = new EvalSkillsError(EvalSkillsErrorCode.SKILL_NOT_FOUND, "Test");

      expect(error.stack).toBeDefined();
      expect(error.stack).toContain("EvalSkillsError");
    });

    it("should be catchable as Error", () => {
      let caughtError: Error | undefined;

      try {
        throw new EvalSkillsError(EvalSkillsErrorCode.SKILL_NOT_FOUND, "Test");
      } catch (e) {
        caughtError = e as Error;
      }

      expect(caughtError).toBeDefined();
      expect(caughtError).toBeInstanceOf(Error);
    });
  });

  describe("toJSON", () => {
    it("should return correct JSON structure with all fields", () => {
      const error = new EvalSkillsError(
        EvalSkillsErrorCode.SKILL_NOT_FOUND,
        "Skill not found",
        { skillId: "test-skill", searchPath: "/path/to/skills" }
      );

      const json = error.toJSON();

      expect(json).toEqual({
        name: "EvalSkillsError",
        code: "E1001",
        message: "[E1001] Skill not found",
        details: { skillId: "test-skill", searchPath: "/path/to/skills" },
      });
    });

    it("should return correct JSON structure without details", () => {
      const error = new EvalSkillsError(EvalSkillsErrorCode.CONFIG_INVALID, "Invalid configuration");

      const json = error.toJSON();

      expect(json).toEqual({
        name: "EvalSkillsError",
        code: "E5001",
        message: "[E5001] Invalid configuration",
        details: undefined,
      });
    });

    it("should be serializable to JSON string", () => {
      const error = new EvalSkillsError(
        EvalSkillsErrorCode.ADAPTER_AUTH_FAILED,
        "Authentication failed",
        { endpoint: "https://api.example.com" }
      );

      const jsonString = JSON.stringify(error.toJSON());
      const parsed = JSON.parse(jsonString);

      expect(parsed.name).toBe("EvalSkillsError");
      expect(parsed.code).toBe("E2002");
      expect(parsed.details.endpoint).toBe("https://api.example.com");
    });
  });

  describe("error codes enum", () => {
    it("should have correct skill-related error codes", () => {
      expect(EvalSkillsErrorCode.SKILL_NOT_FOUND).toBe("E1001");
      expect(EvalSkillsErrorCode.SKILL_SCHEMA_INVALID).toBe("E1002");
      expect(EvalSkillsErrorCode.SKILL_INVOKE_TIMEOUT).toBe("E1003");
      expect(EvalSkillsErrorCode.SKILL_INVOKE_FAILED).toBe("E1004");
    });

    it("should have correct adapter-related error codes", () => {
      expect(EvalSkillsErrorCode.ADAPTER_NOT_FOUND).toBe("E2001");
      expect(EvalSkillsErrorCode.ADAPTER_AUTH_FAILED).toBe("E2002");
      expect(EvalSkillsErrorCode.ADAPTER_CONN_FAILED).toBe("E2003");
    });

    it("should have correct benchmark-related error codes", () => {
      expect(EvalSkillsErrorCode.BENCHMARK_NOT_FOUND).toBe("E3001");
      expect(EvalSkillsErrorCode.BENCHMARK_SCHEMA_ERR).toBe("E3002");
    });

    it("should have correct evaluation-related error codes", () => {
      expect(EvalSkillsErrorCode.EVAL_PARTIAL_FAIL).toBe("E4001");
      expect(EvalSkillsErrorCode.EVAL_THRESHOLD_FAIL).toBe("E4002");
      expect(EvalSkillsErrorCode.EVAL_NO_TASKS).toBe("E4003");
    });

    it("should have correct config-related error codes", () => {
      expect(EvalSkillsErrorCode.CONFIG_INVALID).toBe("E5001");
      expect(EvalSkillsErrorCode.CONFIG_LLM_MISSING).toBe("E5002");
    });
  });

  describe("edge cases", () => {
    it("should handle empty message", () => {
      const error = new EvalSkillsError(EvalSkillsErrorCode.SKILL_NOT_FOUND, "");

      expect(error.message).toBe("[E1001] ");
    });

    it("should handle empty details object", () => {
      const error = new EvalSkillsError(EvalSkillsErrorCode.SKILL_NOT_FOUND, "Test", {});

      expect(error.details).toEqual({});
    });

    it("should handle complex nested details", () => {
      const complexDetails = {
        nested: {
          array: [1, 2, 3],
          object: { key: "value" },
        },
        nullValue: null,
        undefinedValue: undefined,
      };

      const error = new EvalSkillsError(EvalSkillsErrorCode.SKILL_NOT_FOUND, "Test", complexDetails);

      expect(error.details).toEqual(complexDetails);
    });

    it("should handle special characters in message", () => {
      const message = 'File "test.json" contains invalid characters: <>&';
      const error = new EvalSkillsError(EvalSkillsErrorCode.BENCHMARK_SCHEMA_ERR, message);

      expect(error.message).toContain(message);
    });

    it("should handle unicode in message and details", () => {
      const error = new EvalSkillsError(
        EvalSkillsErrorCode.SKILL_NOT_FOUND,
        "技能未找到: 测试技能",
        { skillName: "测试技能" }
      );

      expect(error.message).toContain("技能未找到");
      expect(error.details?.skillName).toBe("测试技能");
    });
  });
});
