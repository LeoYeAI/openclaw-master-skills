import assert from "node:assert/strict";
import test from "node:test";

import { cleanContent } from "./content-cleaner.js";
import { convertWithLegacyExtractor } from "./legacy-converter.js";
import { extractMetadataFromHtml } from "./markdown-conversion-shared.js";

const CAPTURED_AT = "2026-03-24T03:00:00.000Z";

const NEXT_DATA_HTML = `<!doctype html>
<html>
  <head>
    <title>Hydrated Story</title>
  </head>
  <body>
    <div class="cookie-banner">Accept cookies</div>
    <main>
      <p>Short teaser text that should not win over the structured article payload.</p>
    </main>
    <script id="__NEXT_DATA__" type="application/json">
      {
        "props": {
          "pageProps": {
            "article": {
              "title": "Hydrated Story",
              "description": "A structured article payload from Next.js",
              "body": "<p>The full article lives in __NEXT_DATA__ and should still be extracted even when the cleaned HTML removes scripts before the selector and readability passes run.</p><p>A second paragraph keeps the content comfortably above the minimum extraction threshold and proves the legacy extractor still has access to the original structured payload.</p>"
            }
          }
        }
      }
    </script>
  </body>
</html>`;

test("legacy extractor still uses original __NEXT_DATA__ after HTML cleaning", () => {
  const url = "https://example.com/posts/hydrated-story";
  const baseMetadata = extractMetadataFromHtml(NEXT_DATA_HTML, url, CAPTURED_AT);
  const cleanedHtml = cleanContent(NEXT_DATA_HTML, url);

  const result = convertWithLegacyExtractor(NEXT_DATA_HTML, baseMetadata, cleanedHtml);

  assert.equal(result.conversionMethod, "legacy:next-data");
  assert.match(result.markdown, /The full article lives in .*NEXT.*DATA/);
  assert.match(result.markdown, /A second paragraph keeps the content comfortably above the minimum extraction threshold/);
  assert.doesNotMatch(result.markdown, /Short teaser text that should not win/);
  assert.equal(result.rawHtml, NEXT_DATA_HTML);
});
