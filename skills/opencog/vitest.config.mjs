import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include:    ["tests/**/*.test.mjs"],
    environment: "node",
    globals:     false,
    // Tests hit the real chain — give them time
    testTimeout: 60_000,
    hookTimeout: 60_000,
    // Run serially — trade tests are stateful (buy then sell)
    pool:       "forks",
    poolOptions: { forks: { singleFork: true } },
    sequence:   { concurrent: false },
  },
});
