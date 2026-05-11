import { defineConfig } from "vitest/config";
import path from "path";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    include: ["tests/unit/**/*.test.ts"],
    // 让 vitest 直接 transform TS 源码（不依赖预编译的 .js）
    // 这样 v8 coverage 能正确映射到 .ts 文件
    transformMode: {
      web: ["js", "ts"],
      ssr: ["js", "ts"],
    },
    deps: {
      inline: ["better-sqlite3"],  // native module，不做 transform
    },
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov"],
      // 覆盖编译后的 .js 文件，通过 source map 映射回 .ts
      include: ["src/**/*.js"],
      exclude: [
        "src/**/*.d.ts",
        "src/**/*.d.ts.map",
        "src/tools/**/*.js",  // tools/ 是 MCP handler 包装层，逻辑在核心模块
        "src/server.js",
        "src/stdio.js",
      ],
      thresholds: {
        // 核心模块分支覆盖率门禁（映射到 .ts 文件名）
        "src/security.ts": { branches: 70, functions: 70 },
        "src/dedup.ts": { branches: 60, functions: 70 },
        "src/utils.ts": { branches: 70, functions: 100 },
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
});
