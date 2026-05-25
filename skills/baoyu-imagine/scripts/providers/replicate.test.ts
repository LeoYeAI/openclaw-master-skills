import assert from "node:assert/strict";
import test from "node:test";

import type { CliArgs } from "../types.ts";
import {
  buildInput,
  extractOutputUrl,
  parseModelId,
} from "./replicate.ts";

function makeArgs(overrides: Partial<CliArgs> = {}): CliArgs {
  return {
    prompt: null,
    promptFiles: [],
    imagePath: null,
    provider: null,
    model: null,
    aspectRatio: null,
    size: null,
    quality: null,
    imageSize: null,
    referenceImages: [],
    n: 1,
    batchFile: null,
    jobs: null,
    json: false,
    help: false,
    ...overrides,
  };
}

test("Replicate model parsing accepts official formats and rejects malformed ones", () => {
  assert.deepEqual(parseModelId("google/nano-banana-pro"), {
    owner: "google",
    name: "nano-banana-pro",
    version: null,
  });
  assert.deepEqual(parseModelId("owner/model:abc123"), {
    owner: "owner",
    name: "model",
    version: "abc123",
  });

  assert.throws(
    () => parseModelId("just-a-model-name"),
    /Invalid Replicate model format/,
  );
});

test("Replicate input builder maps aspect ratio, image count, quality, and refs", () => {
  assert.deepEqual(
    buildInput(
      "A robot painter",
      makeArgs({
        aspectRatio: "16:9",
        quality: "2k",
        n: 3,
      }),
      ["data:image/png;base64,AAAA"],
    ),
    {
      prompt: "A robot painter",
      aspect_ratio: "16:9",
      number_of_images: 3,
      resolution: "2K",
      output_format: "png",
      image_input: ["data:image/png;base64,AAAA"],
    },
  );

  assert.deepEqual(
    buildInput("A robot painter", makeArgs({ quality: "normal" }), ["ref"]),
    {
      prompt: "A robot painter",
      aspect_ratio: "match_input_image",
      resolution: "1K",
      output_format: "png",
      image_input: ["ref"],
    },
  );
});

test("Replicate output extraction supports string, array, and object URLs", () => {
  assert.equal(
    extractOutputUrl({ output: "https://example.com/a.png" } as never),
    "https://example.com/a.png",
  );
  assert.equal(
    extractOutputUrl({ output: ["https://example.com/b.png"] } as never),
    "https://example.com/b.png",
  );
  assert.equal(
    extractOutputUrl({ output: { url: "https://example.com/c.png" } } as never),
    "https://example.com/c.png",
  );

  assert.throws(
    () => extractOutputUrl({ output: { invalid: true } } as never),
    /Unexpected Replicate output format/,
  );
});
