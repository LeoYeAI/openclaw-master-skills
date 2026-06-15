import assert from "node:assert/strict";
import { mkdtemp, readFile, readdir } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import { localizeMarkdownMedia } from "./media-localizer.js";

const PNG_1X1_BASE64 =
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7Z0ioAAAAASUVORK5CYII=";

test("localizeMarkdownMedia saves embedded base64 images into imgs directory", async () => {
  const tempDir = await mkdtemp(path.join(os.tmpdir(), "url-to-markdown-media-"));
  const dataUri = `data:image/png;base64,${PNG_1X1_BASE64}`;
  const markdown = [
    "---",
    `coverImage: "${dataUri}"`,
    "---",
    "",
    "# Embedded Image",
    "",
    `![inline](${dataUri})`,
    "",
  ].join("\n");

  const result = await localizeMarkdownMedia(markdown, {
    markdownPath: path.join(tempDir, "post.md"),
  });

  assert.equal(result.downloadedImages, 1);
  assert.equal(result.downloadedVideos, 0);
  assert.match(result.markdown, /coverImage: "imgs\/img-001\.png"/);
  assert.match(result.markdown, /!\[inline\]\(imgs\/img-001\.png\)/);

  const files = await readdir(path.join(tempDir, "imgs"));
  assert.deepEqual(files, ["img-001.png"]);

  const bytes = await readFile(path.join(tempDir, "imgs", "img-001.png"));
  assert.equal(bytes.length, Buffer.from(PNG_1X1_BASE64, "base64").length);
});
