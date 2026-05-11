const { createDefaultPreset } = require("ts-jest");

const tsJestTransformCfg = createDefaultPreset().transform;

/** @type {import("jest").Config} **/
module.exports = {
  testEnvironment: "node",
  transform: {
    ...tsJestTransformCfg,
  },
  testMatch: [
    "**/__tests__/**/*.test.ts",
    "**/src/**/*.test.ts"
  ],
  testPathIgnorePatterns: [
    "/node_modules/",
    "/dist/",
    "\\.d\\.ts$",
    "/benchmarks/",
    "/integration/"
  ],
};
