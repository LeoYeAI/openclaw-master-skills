import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    include: ["tests/**/*.test.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      include: ["src/**/*.ts"],
      exclude: ["src/index.ts"],
    },
    testTimeout: 30_000,
    hookTimeout: 30_000,
    // Integration tests can be slow (RPC calls to Base Sepolia)
    poolOptions: {
      threads: {
        singleThread: true,
      },
    },
  },
});
