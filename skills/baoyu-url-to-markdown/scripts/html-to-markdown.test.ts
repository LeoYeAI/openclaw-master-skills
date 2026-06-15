import assert from "node:assert/strict";
import test from "node:test";

import { extractContent } from "./html-to-markdown.js";

const EMBEDDED_IMAGE_HTML = `<!doctype html>
<html>
  <body>
    <main>
      <article>
        <h1>Embedded Image Story</h1>
        <p>
          This paragraph is intentionally long enough to satisfy the extractor thresholds so the
          resulting markdown keeps the main article body and the embedded image reference.
        </p>
        <img src="data:image/png;base64,AAAA" alt="inline">
      </article>
    </main>
  </body>
</html>`;

test("extractContent preserves base64 images when requested for media download", async () => {
  const result = await extractContent(EMBEDDED_IMAGE_HTML, "https://example.com/embedded", {
    preserveBase64Images: true,
  });

  assert.match(result.markdown, /!\[inline\]\(data:image\/png;base64,AAAA\)/);
});
