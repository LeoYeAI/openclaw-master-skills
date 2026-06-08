import { Router } from "express";
import { getDb } from "../db.js";
import { broadcast } from "../services/events.js";
import { wrapRouter, validate } from "../middleware.js";

const router = Router();

function slugify(text) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 80);
}

function excerpt(content, len = 200) {
  if (!content) return "";
  const plain = content.replace(/[#*_`>\[\]()!]/g, "").replace(/\n+/g, " ").trim();
  return plain.length > len ? plain.slice(0, len) + "…" : plain;
}

function wordCount(content) {
  if (!content) return 0;
  return content.split(/\s+/).filter(Boolean).length;
}

// ════════════════════════════════════════════════════════
//  COLLECTIONS
// ════════════════════════════════════════════════════════

router.get("/collections", (req, res) => {
  const db = getDb();
  const collections = db.prepare(`
    SELECT c.*, COUNT(d.id) as doc_count
    FROM collections c
    LEFT JOIN documents d ON d.collection_id = c.id AND d.status = 'published'
    GROUP BY c.id
    ORDER BY c.sort_order, c.name
  `).all();

  // Build tree structure
  const map = {};
  const roots = [];
  for (const c of collections) { map[c.id] = { ...c, children: [] }; }
  for (const c of collections) {
    if (c.parent_id && map[c.parent_id]) {
      map[c.parent_id].children.push(map[c.id]);
    } else {
      roots.push(map[c.id]);
    }
  }

  res.json({ tree: roots, flat: collections });
});

router.post("/collections", (req, res) => {
  const db = getDb();
  const { name, description, icon, color, parent_id, sort_order } = req.body;
  if (!name?.trim()) return res.status(400).json({ error: "Name is required" });

  const slug = slugify(name);
  const info = db.prepare(`
    INSERT INTO collections (name, slug, description, icon, color, parent_id, sort_order)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `).run(name.trim(), slug, description || "", icon || "📁", color || "#6366f1", parent_id || null, sort_order ?? 0);

  const col = db.prepare("SELECT * FROM collections WHERE rowid = ?").get(info.lastInsertRowid);
  broadcast("library:collection_created", col);
  res.status(201).json(col);
});

router.patch("/collections/:id", (req, res) => {
  const db = getDb();
  const fields = ["name", "description", "icon", "color", "parent_id", "sort_order"];
  const updates = [];
  const values = [];
  for (const f of fields) {
    if (req.body[f] !== undefined) {
      updates.push(`${f} = ?`);
      values.push(req.body[f]);
      if (f === "name") { updates.push("slug = ?"); values.push(slugify(req.body[f])); }
    }
  }
  if (updates.length === 0) return res.status(400).json({ error: "No fields to update" });
  values.push(req.params.id);
  db.prepare(`UPDATE collections SET ${updates.join(", ")} WHERE id = ?`).run(...values);
  res.json(db.prepare("SELECT * FROM collections WHERE id = ?").get(req.params.id));
});

router.delete("/collections/:id", (req, res) => {
  const db = getDb();
  // Move docs to uncategorized rather than deleting them
  db.prepare("UPDATE documents SET collection_id = NULL WHERE collection_id = ?").run(req.params.id);
  db.prepare("DELETE FROM collections WHERE id = ?").run(req.params.id);
  res.json({ ok: true });
});

// ════════════════════════════════════════════════════════
//  DOCUMENTS
// ════════════════════════════════════════════════════════

// ── List / Browse ─────────────────────────────────────
router.get("/documents", (req, res) => {
  const db = getDb();
  const { collection_id, doc_type, status, project_id, author_agent, tag, pinned, limit, offset } = req.query;

  let sql = `SELECT d.id, d.title, d.slug, d.doc_type, d.format, d.collection_id,
             d.excerpt, d.word_count, d.author_agent, d.project_id, d.task_id,
             d.status, d.pinned, d.version, d.created_at, d.updated_at, d.published_at,
             c.name as collection_name, c.icon as collection_icon,
             p.name as project_name
             FROM documents d
             LEFT JOIN collections c ON c.id = d.collection_id
             LEFT JOIN projects p ON p.id = d.project_id
             WHERE 1=1`;
  const params = [];

  if (collection_id) { sql += " AND d.collection_id = ?"; params.push(collection_id); }
  if (doc_type)      { sql += " AND d.doc_type = ?"; params.push(doc_type); }
  if (status)        { sql += " AND d.status = ?"; params.push(status); }
  else               { sql += " AND d.status != 'archived'"; }
  if (project_id)    { sql += " AND d.project_id = ?"; params.push(project_id); }
  if (author_agent)  { sql += " AND d.author_agent = ?"; params.push(author_agent); }
  if (pinned === "1"){ sql += " AND d.pinned = 1"; }
  if (tag) {
    sql += " AND d.id IN (SELECT doc_id FROM doc_tags WHERE tag_id = ?)";
    params.push(tag);
  }

  sql += " ORDER BY d.pinned DESC, d.updated_at DESC";
  sql += ` LIMIT ? OFFSET ?`;
  params.push(parseInt(limit) || 50, parseInt(offset) || 0);

  const docs = db.prepare(sql).all(...params);

  // Attach tags
  const tagStmt = db.prepare(`
    SELECT t.id, t.name, t.color FROM tags t
    JOIN doc_tags dt ON dt.tag_id = t.id WHERE dt.doc_id = ?
  `);
  for (const d of docs) { d.tags = tagStmt.all(d.id); }

  res.json(docs);
});

// ── Search (FTS) ──────────────────────────────────────
router.get("/search", (req, res) => {
  const db = getDb();
  const { q, limit } = req.query;
  if (!q?.trim()) return res.json([]);

  const results = db.prepare(`
    SELECT d.id, d.title, d.slug, d.doc_type, d.format, d.collection_id,
           d.excerpt, d.author_agent, d.status, d.updated_at,
           c.name as collection_name, c.icon as collection_icon,
           highlight(documents_fts, 1, '<mark>', '</mark>') as content_highlight,
           rank
    FROM documents_fts
    JOIN documents d ON d.rowid = documents_fts.rowid
    LEFT JOIN collections c ON c.id = d.collection_id
    WHERE documents_fts MATCH ?
    ORDER BY rank
    LIMIT ?
  `).all(q.trim(), parseInt(limit) || 20);

  res.json(results);
});

// ── Get One (full content) ────────────────────────────
router.get("/documents/:id", (req, res) => {
  const db = getDb();
  const doc = db.prepare(`
    SELECT d.*, c.name as collection_name, c.icon as collection_icon,
           p.name as project_name, t.title as task_title
    FROM documents d
    LEFT JOIN collections c ON c.id = d.collection_id
    LEFT JOIN projects p ON p.id = d.project_id
    LEFT JOIN tasks t ON t.id = d.task_id
    WHERE d.id = ?
  `).get(req.params.id);

  if (!doc) return res.status(404).json({ error: "Document not found" });

  doc.tags = db.prepare(`
    SELECT t.id, t.name, t.color FROM tags t
    JOIN doc_tags dt ON dt.tag_id = t.id WHERE dt.doc_id = ?
  `).all(doc.id);

  doc.version_history = db.prepare(`
    SELECT id, version, change_note, changed_by, created_at
    FROM document_versions WHERE doc_id = ? ORDER BY version DESC LIMIT 20
  `).all(doc.id);

  res.json(doc);
});

// ── Create ────────────────────────────────────────────
router.post("/documents", (req, res) => {
  const db = getDb();
  const {
    title, content, doc_type, format, collection_id,
    author_agent, project_id, task_id, source_path,
    status, pinned, tags
  } = req.body;

  if (!title?.trim()) return res.status(400).json({ error: "Title is required" });

  const VALID_DOC_TYPES = ["research", "report", "documentation", "reference", "template", "note", "analysis", "brief", "guide", "other", "document"];
  const VALID_FORMATS = ["markdown", "html", "code", "json", "text", "csv"];
  const VALID_STATUSES = ["draft", "published", "archived"];

  const err = validate(req.body, {
    title: { required: true, type: "string", maxLength: 500 },
    content: { type: "string", maxLength: 5000000 },
    doc_type: { type: "string", oneOf: VALID_DOC_TYPES },
    format: { type: "string", oneOf: VALID_FORMATS },
    status: { type: "string", oneOf: VALID_STATUSES },
    author_agent: { type: "string", maxLength: 100 },
  });
  if (err) return res.status(400).json({ error: err });

  const slug = slugify(title);
  const pubStatus = status || "published";

  const info = db.prepare(`
    INSERT INTO documents (title, slug, content, doc_type, format, collection_id,
      excerpt, word_count, author_agent, project_id, task_id, source_path,
      status, pinned, published_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    title.trim(), slug, content || "", doc_type || "document", format || "markdown",
    collection_id || null,
    excerpt(content), wordCount(content),
    author_agent || null, project_id || null, task_id || null, source_path || null,
    pubStatus, pinned ? 1 : 0,
    pubStatus === "published" ? new Date().toISOString() : null
  );

  const doc = db.prepare("SELECT * FROM documents WHERE rowid = ?").get(info.lastInsertRowid);

  // Save initial version
  db.prepare(`
    INSERT INTO document_versions (doc_id, version, content, change_note, changed_by)
    VALUES (?, 1, ?, 'Initial version', ?)
  `).run(doc.id, content || "", author_agent || "user");

  // Apply tags
  if (Array.isArray(tags) && tags.length > 0) {
    const tagStmt = db.prepare("INSERT OR IGNORE INTO doc_tags (doc_id, tag_id) VALUES (?, ?)");
    for (const tagId of tags) { tagStmt.run(doc.id, tagId); }
  }

  db.prepare(`
    INSERT INTO activity_log_v2 (entity_type, entity_id, action, new_value, actor, message)
    VALUES ('document', ?, 'published', ?, ?, ?)
  `).run(doc.id, doc.status, author_agent || "user", `Document published: "${title.trim()}"`);

  broadcast("library:published", doc);
  res.status(201).json(doc);
});

// ── Update (creates a new version) ────────────────────
router.patch("/documents/:id", (req, res) => {
  const db = getDb();
  const existing = db.prepare("SELECT * FROM documents WHERE id = ?").get(req.params.id);
  if (!existing) return res.status(404).json({ error: "Document not found" });

  const fields = ["title", "content", "doc_type", "format", "collection_id",
    "author_agent", "project_id", "task_id", "source_path", "status", "pinned"];
  const updates = [];
  const values = [];
  let contentChanged = false;

  for (const f of fields) {
    if (req.body[f] !== undefined) {
      updates.push(`${f} = ?`);
      values.push(f === "pinned" ? (req.body[f] ? 1 : 0) : req.body[f]);
      if (f === "content") contentChanged = true;
      if (f === "title") { updates.push("slug = ?"); values.push(slugify(req.body[f])); }
    }
  }

  if (updates.length === 0) return res.status(400).json({ error: "No fields to update" });

  // Auto-update derived fields
  if (contentChanged) {
    updates.push("excerpt = ?", "word_count = ?", "version = version + 1");
    values.push(excerpt(req.body.content), wordCount(req.body.content));
  }
  updates.push("updated_at = datetime('now')");
  if (req.body.status === "published" && existing.status !== "published") {
    updates.push("published_at = datetime('now')");
  }

  values.push(req.params.id);
  db.prepare(`UPDATE documents SET ${updates.join(", ")} WHERE id = ?`).run(...values);

  // Record version if content changed
  if (contentChanged) {
    const newVersion = existing.version + 1;
    db.prepare(`
      INSERT INTO document_versions (doc_id, version, content, change_note, changed_by)
      VALUES (?, ?, ?, ?, ?)
    `).run(req.params.id, newVersion, req.body.content, req.body.change_note || "", req.body._actor || "user");
  }

  // Update tags if provided
  if (Array.isArray(req.body.tags)) {
    db.prepare("DELETE FROM doc_tags WHERE doc_id = ?").run(req.params.id);
    const tagStmt = db.prepare("INSERT OR IGNORE INTO doc_tags (doc_id, tag_id) VALUES (?, ?)");
    for (const tagId of req.body.tags) { tagStmt.run(req.params.id, tagId); }
  }

  const updated = db.prepare("SELECT * FROM documents WHERE id = ?").get(req.params.id);
  broadcast("library:updated", updated);
  res.json(updated);
});

// ── Delete ────────────────────────────────────────────
router.delete("/documents/:id", (req, res) => {
  const db = getDb();
  db.prepare("DELETE FROM documents WHERE id = ?").run(req.params.id);
  broadcast("library:deleted", { id: req.params.id });
  res.json({ ok: true });
});

// ── Get specific version ──────────────────────────────
router.get("/documents/:id/versions/:version", (req, res) => {
  const db = getDb();
  const ver = db.prepare(
    "SELECT * FROM document_versions WHERE doc_id = ? AND version = ?"
  ).get(req.params.id, parseInt(req.params.version));
  if (!ver) return res.status(404).json({ error: "Version not found" });
  res.json(ver);
});

// ════════════════════════════════════════════════════════
//  TAGS (shared with tasks — reuse the tags table)
// ════════════════════════════════════════════════════════

router.get("/tags", (req, res) => {
  const db = getDb();
  const tags = db.prepare(`
    SELECT t.*, COUNT(dt.doc_id) as doc_count
    FROM tags t
    LEFT JOIN doc_tags dt ON dt.tag_id = t.id
    GROUP BY t.id ORDER BY t.name
  `).all();
  res.json(tags);
});

router.post("/tags", (req, res) => {
  const db = getDb();
  const { name, color } = req.body;
  if (!name?.trim()) return res.status(400).json({ error: "Name is required" });
  try {
    const info = db.prepare("INSERT INTO tags (name, color) VALUES (?, ?)").run(name.trim(), color || "#6366f1");
    res.status(201).json(db.prepare("SELECT * FROM tags WHERE rowid = ?").get(info.lastInsertRowid));
  } catch (err) {
    if (err.message.includes("UNIQUE")) return res.status(409).json({ error: "Tag already exists" });
    throw err;
  }
});

// ════════════════════════════════════════════════════════
//  STATS
// ════════════════════════════════════════════════════════

router.get("/stats", (req, res) => {
  const db = getDb();
  const total = db.prepare("SELECT COUNT(*) as c FROM documents WHERE status != 'archived'").get().c;
  const byType = db.prepare(
    "SELECT doc_type, COUNT(*) as count FROM documents WHERE status != 'archived' GROUP BY doc_type"
  ).all().reduce((a, r) => { a[r.doc_type] = r.count; return a; }, {});
  const byCollection = db.prepare(`
    SELECT c.name, c.icon, COUNT(d.id) as count
    FROM collections c LEFT JOIN documents d ON d.collection_id = c.id AND d.status != 'archived'
    GROUP BY c.id ORDER BY count DESC
  `).all();
  const recentlyPublished = db.prepare(
    "SELECT id, title, doc_type, author_agent, published_at FROM documents WHERE status = 'published' ORDER BY published_at DESC LIMIT 5"
  ).all();
  const totalWords = db.prepare("SELECT COALESCE(SUM(word_count), 0) as w FROM documents WHERE status != 'archived'").get().w;

  res.json({ total, byType, byCollection, recentlyPublished, totalWords });
});

wrapRouter(router);
export default router;
