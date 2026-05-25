import assert from "node:assert/strict";
import test, { type TestContext } from "node:test";

import {
  getDefaultModel,
  getModelFamily,
  getQwen2SizeFromAspectRatio,
  getSizeFromAspectRatio,
  normalizeSize,
  parseAspectRatio,
  parseSize,
  resolveSizeForModel,
} from "./dashscope.ts";

function useEnv(
  t: TestContext,
  values: Record<string, string | null>,
): void {
  const previous = new Map<string, string | undefined>();
  for (const [key, value] of Object.entries(values)) {
    previous.set(key, process.env[key]);
    if (value == null) {
      delete process.env[key];
    } else {
      process.env[key] = value;
    }
  }

  t.after(() => {
    for (const [key, value] of previous.entries()) {
      if (value == null) {
        delete process.env[key];
      } else {
        process.env[key] = value;
      }
    }
  });
}

test("DashScope default model prefers env override and otherwise uses qwen-image-2.0-pro", (t) => {
  useEnv(t, { DASHSCOPE_IMAGE_MODEL: null });
  assert.equal(getDefaultModel(), "qwen-image-2.0-pro");

  process.env.DASHSCOPE_IMAGE_MODEL = "qwen-image-max";
  assert.equal(getDefaultModel(), "qwen-image-max");
});

test("DashScope aspect-ratio parsing accepts numeric ratios only", () => {
  assert.deepEqual(parseAspectRatio("3:2"), { width: 3, height: 2 });
  assert.equal(parseAspectRatio("square"), null);
  assert.equal(parseAspectRatio("-1:2"), null);
});

test("DashScope model family routing distinguishes qwen-2.0, fixed-size qwen, and legacy models", () => {
  assert.equal(getModelFamily("qwen-image-2.0-pro"), "qwen2");
  assert.equal(getModelFamily("qwen-image"), "qwenFixed");
  assert.equal(getModelFamily("z-image-turbo"), "legacy");
  assert.equal(getModelFamily("wanx-v1"), "legacy");
});

test("Legacy DashScope size selection keeps the previous quality-based heuristic", () => {
  assert.equal(getSizeFromAspectRatio(null, "normal"), "1024*1024");
  assert.equal(getSizeFromAspectRatio("16:9", "normal"), "1280*720");
  assert.equal(getSizeFromAspectRatio("16:9", "2k"), "2048*1152");
  assert.equal(getSizeFromAspectRatio("invalid", "2k"), "1536*1536");
});

test("Qwen 2.0 recommended sizes follow the official common-ratio table", () => {
  assert.equal(getQwen2SizeFromAspectRatio(null, "normal"), "1024*1024");
  assert.equal(getQwen2SizeFromAspectRatio(null, "2k"), "1536*1536");
  assert.equal(getQwen2SizeFromAspectRatio("16:9", "normal"), "1280*720");
  assert.equal(getQwen2SizeFromAspectRatio("21:9", "2k"), "2048*872");
});

test("Qwen 2.0 derives free-form sizes within pixel budget for uncommon ratios", () => {
  const size = getQwen2SizeFromAspectRatio("5:2", "normal");
  const parsed = parseSize(size);
  assert.ok(parsed);
  assert.ok(parsed.width * parsed.height >= 512 * 512);
  assert.ok(parsed.width * parsed.height <= 2048 * 2048);
  assert.ok(Math.abs(parsed.width / parsed.height - 2.5) < 0.08);
});

test("resolveSizeForModel validates explicit qwen-image-2.0 sizes by total pixels", () => {
  assert.equal(
    resolveSizeForModel("qwen-image-2.0-pro", {
      size: "2048x872",
      aspectRatio: null,
      quality: "2k",
    }),
    "2048*872",
  );

  assert.throws(
    () =>
      resolveSizeForModel("qwen-image-2.0-pro", {
        size: "4096x4096",
        aspectRatio: null,
        quality: "2k",
      }),
    /total pixels between/,
  );
});

test("resolveSizeForModel enforces fixed sizes for qwen-image-max/plus/image", () => {
  assert.equal(
    resolveSizeForModel("qwen-image-max", {
      size: null,
      aspectRatio: "1:1",
      quality: "2k",
    }),
    "1328*1328",
  );

  assert.equal(
    resolveSizeForModel("qwen-image", {
      size: "1664x928",
      aspectRatio: "9:16",
      quality: "normal",
    }),
    "1664*928",
  );

  assert.throws(
    () =>
      resolveSizeForModel("qwen-image-max", {
        size: null,
        aspectRatio: "21:9",
        quality: "2k",
      }),
    /supports only fixed ratios/,
  );

  assert.throws(
    () =>
      resolveSizeForModel("qwen-image-plus", {
        size: "1024x1024",
        aspectRatio: null,
        quality: "2k",
      }),
    /support only these sizes/,
  );
});

test("DashScope size normalization converts WxH into provider format", () => {
  assert.equal(normalizeSize("1024x1024"), "1024*1024");
  assert.equal(normalizeSize("2048*1152"), "2048*1152");
});
