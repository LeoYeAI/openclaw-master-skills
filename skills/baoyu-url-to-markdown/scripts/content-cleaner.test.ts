import assert from "node:assert/strict";
import test from "node:test";

import { cleanContent } from "./content-cleaner.js";

const SAMPLE_HTML = `<!doctype html>
<html>
  <head>
    <title>Example Story</title>
    <style>.cookie-banner { position: fixed; }</style>
    <script>window.__noise = true;</script>
  </head>
  <body>
    <!-- comment that should be removed -->
    <header>
      <nav>
        <a href="/home">Home</a>
        <a href="/topics">Topics</a>
      </nav>
    </header>
    <div class="cookie-banner">Accept cookies</div>
    <aside>Sidebar links</aside>
    <main>
      <article class="content">
        <h1>Actual Story Title</h1>
        <p>
          This is the first paragraph of the real story body, and it is intentionally long enough
          to survive the cleaner's main-content heuristics without being mistaken for navigation.
        </p>
        <p>
          This is the second paragraph with more useful detail, a
          <a href="/read-more">supporting link</a>, and a normal image.
        </p>
        <img src="/images/cover.jpg" alt="Cover">
        <img src="data:image/png;base64,AAAA" alt="Inline data">
      </article>
    </main>
    <footer>Footer boilerplate</footer>
  </body>
</html>`;

test("cleanContent keeps the article body and removes obvious boilerplate", () => {
  const cleaned = cleanContent(SAMPLE_HTML, "https://example.com/posts/story");

  assert.match(cleaned, /Actual Story Title/);
  assert.match(cleaned, /https:\/\/example\.com\/read-more/);
  assert.match(cleaned, /https:\/\/example\.com\/images\/cover\.jpg/);

  assert.doesNotMatch(cleaned, /Accept cookies/);
  assert.doesNotMatch(cleaned, /Sidebar links/);
  assert.doesNotMatch(cleaned, /Footer boilerplate/);
  assert.doesNotMatch(cleaned, /window\.__noise/);
  assert.doesNotMatch(cleaned, /comment that should be removed/);
  assert.doesNotMatch(cleaned, /data:image\/png;base64/);
});
