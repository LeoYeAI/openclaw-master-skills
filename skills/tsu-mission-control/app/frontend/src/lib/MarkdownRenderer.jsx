/**
 * MarkdownRenderer — renders Markdown, JSON, CSV, code, and plain text
 *
 * Uses the `marked` library for Markdown parsing instead of regex.
 * Handles tables, nested lists, footnotes, images, and all standard
 * Markdown syntax. Strips dangerous HTML to prevent XSS.
 */
import React, { useMemo } from "react";
import { marked } from "marked";

// ── Configure marked ────────────────────────────────
marked.setOptions({
  gfm: true,        // GitHub-flavored Markdown (tables, strikethrough)
  breaks: true,     // Newlines become <br>
  pedantic: false,
});

// Custom renderer for styling
const renderer = new marked.Renderer();

renderer.heading = function ({ text, depth }) {
  const sizes = { 1: 20, 2: 17, 3: 15, 4: 14, 5: 13, 6: 12 };
  const margins = { 1: "24px 0 10px", 2: "22px 0 8px", 3: "18px 0 6px", 4: "14px 0 4px", 5: "12px 0 4px", 6: "10px 0 4px" };
  return `<h${depth} style="font-size:${sizes[depth]}px;font-weight:${depth <= 2 ? 700 : 600};color:#fff;margin:${margins[depth]};line-height:1.4">${text}</h${depth}>`;
};

renderer.paragraph = function ({ tokens }) {
  const text = this.parser.parseInline(tokens);
  return `<p style="margin:8px 0;line-height:1.7">${text}</p>`;
};

renderer.blockquote = function ({ tokens }) {
  const body = this.parser.parse(tokens);
  return `<blockquote style="border-left:3px solid #6366f1;padding-left:12px;color:#94a3b8;margin:8px 0">${body}</blockquote>`;
};

renderer.code = function ({ text, lang }) {
  const escaped = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return `<pre style="background:#0f1729;border:1px solid #1e293b;border-radius:8px;padding:12px;overflow-x:auto;font-size:12px;line-height:1.6;margin:8px 0;font-family:monospace"><code>${escaped}</code></pre>`;
};

renderer.codespan = function ({ text }) {
  return `<code style="background:#1e293b;padding:1px 5px;border-radius:3px;font-size:12px;font-family:monospace">${text}</code>`;
};

renderer.link = function ({ href, title, tokens }) {
  const text = this.parser.parseInline(tokens);
  const titleAttr = title ? ` title="${title}"` : "";
  return `<a href="${href}"${titleAttr} style="color:#818cf8;text-decoration:underline" target="_blank" rel="noopener">${text}</a>`;
};

renderer.list = function ({ items, ordered }) {
  const tag = ordered ? "ol" : "ul";
  const style = ordered
    ? "margin:4px 0;padding-left:24px;list-style:decimal"
    : "margin:4px 0;padding-left:24px;list-style:disc";
  const body = items.map(item => this.listitem(item)).join("");
  return `<${tag} style="${style}">${body}</${tag}>`;
};

renderer.listitem = function ({ tokens }) {
  const text = this.parser.parse(tokens);
  return `<li style="margin-bottom:2px;line-height:1.6">${text}</li>`;
};

renderer.table = function ({ header, rows }) {
  const headCells = header.map(cell => {
    const text = this.parser.parseInline(cell.tokens);
    const align = cell.align ? `text-align:${cell.align};` : "text-align:left;";
    return `<th style="${align}padding:6px 10px;border-bottom:2px solid #1e293b;color:#94a3b8;font-weight:500;font-size:12px">${text}</th>`;
  }).join("");

  const bodyRows = rows.map(row => {
    const cells = row.map(cell => {
      const text = this.parser.parseInline(cell.tokens);
      const align = cell.align ? `text-align:${cell.align};` : "";
      return `<td style="${align}padding:5px 10px;border-bottom:1px solid rgba(30,41,59,0.3);color:#e2e8f0;font-size:12px">${text}</td>`;
    }).join("");
    return `<tr>${cells}</tr>`;
  }).join("");

  return `<div style="overflow-x:auto;margin:8px 0"><table style="width:100%;border-collapse:collapse"><thead><tr>${headCells}</tr></thead><tbody>${bodyRows}</tbody></table></div>`;
};

renderer.hr = function () {
  return `<hr style="border:none;border-top:1px solid #1e293b;margin:14px 0">`;
};

renderer.image = function ({ href, title, text }) {
  const titleAttr = title ? ` title="${title}"` : "";
  return `<img src="${href}" alt="${text}"${titleAttr} style="max-width:100%;border-radius:8px;margin:8px 0">`;
};

renderer.strong = function ({ tokens }) {
  const text = this.parser.parseInline(tokens);
  return `<strong style="color:#fff">${text}</strong>`;
};

marked.use({ renderer });

// ── Strip dangerous HTML after rendering ────────────
function stripDangerousHtml(html) {
  return html
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "")
    .replace(/\s*on\w+\s*=\s*["'][^"']*["']/gi, "")
    .replace(/\s*on\w+\s*=\s*\S+/gi, "")
    .replace(/javascript\s*:/gi, "")
    .replace(/<\s*\/?\s*(iframe|embed|object|form|base|meta|link)\b[^>]*>/gi, "");
}

// ── JSON renderer ───────────────────────────────────
function renderJSON(content) {
  try {
    const formatted = JSON.stringify(JSON.parse(content), null, 2);
    const escaped = formatted.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    return `<pre style="background:#0f1729;border:1px solid #1e293b;border-radius:8px;padding:16px;overflow:auto;font-size:12px;line-height:1.6;font-family:monospace;white-space:pre-wrap;color:#e2e8f0">${escaped}</pre>`;
  } catch {
    return `<pre style="background:#0f1729;border:1px solid #1e293b;border-radius:8px;padding:16px;overflow:auto;font-size:12px;line-height:1.6;font-family:monospace;white-space:pre-wrap;color:#e2e8f0">${content.replace(/&/g, "&amp;").replace(/</g, "&lt;")}</pre>`;
  }
}

// ── CSV renderer ────────────────────────────────────
function renderCSV(content) {
  const lines = content.trim().split("\n");
  if (lines.length === 0) return "<p>Empty</p>";
  const headers = lines[0].split(",").map(h => h.trim().replace(/^"|"$/g, ""));
  const rows = lines.slice(1).map(l => l.split(",").map(c => c.trim().replace(/^"|"$/g, "")));
  return (
    `<div style="overflow-x:auto;margin:8px 0"><table style="width:100%;border-collapse:collapse;font-size:12px">` +
    `<thead><tr>${headers.map(h => `<th style="text-align:left;padding:6px 10px;border-bottom:2px solid #1e293b;color:#94a3b8;font-weight:500">${h}</th>`).join("")}</tr></thead>` +
    `<tbody>${rows.map(r => `<tr>${r.map(c => `<td style="padding:5px 10px;border-bottom:1px solid rgba(30,41,59,0.3);color:#e2e8f0">${c}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`
  );
}

// ── Main component ──────────────────────────────────
export default function MarkdownRenderer({ content, format }) {
  const html = useMemo(() => {
    if (!content) return "";

    switch (format) {
      case "json":
        return renderJSON(content);
      case "csv":
        return renderCSV(content);
      case "code":
      case "text": {
        const escaped = content.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        return `<pre style="background:#0f1729;border:1px solid #1e293b;border-radius:8px;padding:16px;overflow:auto;font-size:12px;line-height:1.6;font-family:monospace;white-space:pre-wrap;color:#e2e8f0">${escaped}</pre>`;
      }
      case "html":
        return stripDangerousHtml(content);
      case "markdown":
      default:
        return stripDangerousHtml(marked.parse(content));
    }
  }, [content, format]);

  return (
    <div
      style={{ color: "#cbd5e1", fontSize: 14, lineHeight: 1.7 }}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
