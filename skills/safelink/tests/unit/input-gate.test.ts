import { describe, it, expect } from "vitest";
import {
  stripPII,
  hasPII,
  validateInput,
  EvmAddress,
  USDCRate,
  SafeTaskDescription,
  PolicySchema,
  validateEndpointUrlStrict,
} from "../../src/security/input-gate.js";
import { z } from "zod";

describe("stripPII", () => {
  it("strips private key hex strings", () => {
    const input = "use key 0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890";
    const result = stripPII(input);
    expect(result).toContain("[PRIVATE_KEY_REDACTED]");
    expect(result).not.toContain("abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890");
  });

  it("strips Anthropic API keys", () => {
    const input = "My key is sk-ant-api03-abcdefghijklmnopqrstuvwxyz1234567890";
    const result = stripPII(input);
    expect(result).toContain("[API_KEY_REDACTED]");
    expect(result).not.toContain("sk-ant-api03");
  });

  it("strips email addresses", () => {
    const result = stripPII("Contact me at alice@example.com for details");
    expect(result).toContain("[EMAIL_REDACTED]");
    expect(result).not.toContain("alice@example.com");
  });

  it("preserves normal task descriptions", () => {
    const input = "Summarize the Q4 earnings report and provide bullet points";
    const result = stripPII(input);
    expect(result).toBe(input);
  });

  it("handles empty string", () => {
    expect(stripPII("")).toBe("");
  });

  it("strips phone numbers", () => {
    const result = stripPII("Call me at 416-555-1234 tomorrow");
    expect(result).toContain("[PHONE_REDACTED]");
    expect(result).not.toContain("416-555-1234");
  });
});

describe("hasPII", () => {
  it("detects email PII", () => {
    expect(hasPII("send to user@domain.com")).toBe(true);
  });

  it("returns false for clean text", () => {
    expect(hasPII("analyze market trends for Q3")).toBe(false);
  });
});

describe("EvmAddress", () => {
  it("accepts valid checksummed address", () => {
    const addr = "0x742d35Cc6634C0532925a3b8D4C9cF55B6E9e54b";
    expect(() => EvmAddress.parse(addr)).not.toThrow();
  });

  it("accepts lowercase valid address", () => {
    const addr = "0x742d35cc6634c0532925a3b8d4c9cf55b6e9e54b";
    expect(() => EvmAddress.parse(addr)).not.toThrow();
  });

  it("rejects zero address", () => {
    expect(() =>
      EvmAddress.parse("0x0000000000000000000000000000000000000000")
    ).toThrow("Zero address not allowed");
  });

  it("rejects short address", () => {
    expect(() => EvmAddress.parse("0x1234")).toThrow();
  });

  it("rejects non-hex characters", () => {
    expect(() =>
      EvmAddress.parse("0xGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
    ).toThrow();
  });
});

describe("USDCRate", () => {
  it("accepts valid rate", () => {
    expect(USDCRate.parse(0.05)).toBe(0.05);
  });

  it("rejects zero", () => {
    expect(() => USDCRate.parse(0)).toThrow();
  });

  it("rejects negative", () => {
    expect(() => USDCRate.parse(-1)).toThrow();
  });

  it("rejects rate > 100", () => {
    expect(() => USDCRate.parse(101)).toThrow();
  });
});

describe("SafeTaskDescription", () => {
  it("strips PII from task description", () => {
    const result = SafeTaskDescription.parse(
      "Send email to ceo@corp.com with summary"
    );
    expect(result).not.toContain("ceo@corp.com");
    expect(result).toContain("[EMAIL_REDACTED]");
  });

  it("rejects empty string", () => {
    expect(() => SafeTaskDescription.parse("")).toThrow();
  });

  it("rejects strings over 2000 chars", () => {
    expect(() => SafeTaskDescription.parse("x".repeat(2001))).toThrow();
  });
});

describe("PolicySchema", () => {
  it("applies defaults when empty", () => {
    const policy = PolicySchema.parse({});
    expect(policy.max_task_seconds).toBe(300);
    expect(policy.require_escrow).toBe(true);
    expect(policy.allowed_chains).toContain("base-sepolia");
  });

  it("accepts valid policy", () => {
    const policy = PolicySchema.parse({
      max_task_seconds: 600,
      allowed_chains: ["base-sepolia", "base-mainnet"],
      require_escrow: false,
      max_rate_usdc: 5,
      auto_approve_below_risk: 20,
    });
    expect(policy.max_task_seconds).toBe(600);
    expect(policy.require_escrow).toBe(false);
  });

  it("rejects max_task_seconds > 3600", () => {
    expect(() => PolicySchema.parse({ max_task_seconds: 3601 })).toThrow();
  });
});

describe("validateInput", () => {
  const Schema = z.object({ name: z.string(), value: z.number() });

  it("returns validated data", () => {
    const result = validateInput(Schema, { name: "test", value: 42 });
    expect(result).toEqual({ name: "test", value: 42 });
  });

  it("throws ValidationError on invalid input", () => {
    expect(() => validateInput(Schema, { name: "test", value: "not-a-number" })).toThrow(
      "Input validation failed"
    );
  });
});

describe("validateEndpointUrlStrict", () => {
  it("accepts public https endpoint with public DNS resolution", async () => {
    const url = await validateEndpointUrlStrict(
      "https://agent.example.com/task",
      async () => [{ address: "93.184.216.34", family: 4 }]
    );
    expect(url.hostname).toBe("agent.example.com");
  });

  it("rejects endpoint resolving to private IP", async () => {
    await expect(
      validateEndpointUrlStrict(
        "https://agent.example.com/task",
        async () => [{ address: "10.0.0.5", family: 4 }]
      )
    ).rejects.toThrow(/private\/reserved IP range/i);
  });

  it("rejects unresolved hostnames", async () => {
    await expect(
      validateEndpointUrlStrict("https://agent.example.com/task", async () => [])
    ).rejects.toThrow(/did not resolve/i);
  });
});
