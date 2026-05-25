import assert from "node:assert/strict";
import test from "node:test";

import {
  extractImageFromResponse,
  getMimeType,
  getOpenAISize,
  parseAspectRatio,
} from "./openai.ts";

test("OpenAI aspect-ratio parsing and size selection match model families", () => {
  assert.deepEqual(parseAspectRatio("16:9"), { width: 16, height: 9 });
  assert.equal(parseAspectRatio("wide"), null);
  assert.equal(parseAspectRatio("0:1"), null);

  assert.equal(getOpenAISize("dall-e-3", "16:9", "2k"), "1792x1024");
  assert.equal(getOpenAISize("dall-e-3", "9:16", "normal"), "1024x1792");
  assert.equal(getOpenAISize("dall-e-2", "16:9", "2k"), "1024x1024");
  assert.equal(getOpenAISize("gpt-image-1.5", "16:9", "2k"), "1536x1024");
  assert.equal(getOpenAISize("gpt-image-1.5", "4:3", "2k"), "1024x1024");
});

test("OpenAI mime-type detection covers supported reference image extensions", () => {
  assert.equal(getMimeType("frame.png"), "image/png");
  assert.equal(getMimeType("frame.jpg"), "image/jpeg");
  assert.equal(getMimeType("frame.webp"), "image/webp");
  assert.equal(getMimeType("frame.gif"), "image/gif");
});

test("OpenAI response extraction supports base64 and URL download flows", async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  const fromBase64 = await extractImageFromResponse({
    data: [{ b64_json: Buffer.from("hello").toString("base64") }],
  });
  assert.equal(Buffer.from(fromBase64).toString("utf8"), "hello");

  globalThis.fetch = async () =>
    new Response(Uint8Array.from([1, 2, 3]), {
      status: 200,
      headers: { "Content-Type": "application/octet-stream" },
    });

  const fromUrl = await extractImageFromResponse({
    data: [{ url: "https://example.com/image.png" }],
  });
  assert.deepEqual([...fromUrl], [1, 2, 3]);

  await assert.rejects(
    () => extractImageFromResponse({ data: [{}] }),
    /No image in response/,
  );
});
