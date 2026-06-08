import React, { useState, useEffect, useCallback, useRef } from "react";
import MarkdownRenderer from "../lib/MarkdownRenderer";
import usePagination from "../hooks/usePagination";
// ── Style constants ───────────────────────────────────
const C = {
  bg: "#0a0e1a", card: "#1a2035", border: "#1e293b", accent: "#6366f1", accentH: "#818cf8",
  text: "#e2e8f0", muted: "#94a3b8", dim: "#64748b", faint: "#475569",
  green: "#10b981", amber: "#f59e0b", red: "#ef4444", purple: "#a855f7", blue: "#3b82f6",
};

const DOC_TYPE_ICONS = {
  research: "🔬", report: "📊", documentation: "📖", reference: "📚",
  template: "📋", note: "📝", analysis: "📈", brief: "📄", guide: "🗺", other: "📎",
};
const FORMAT_LABELS = { markdown: "MD", html: "HTML", code: "Code", json: "JSON", text: "Text", csv: "CSV" };

// ── Main Library Component ────────────────────────────
export default function Library({ projects, agents, refresh, api: apiClient }) {
  const [collections, setCollections] = useState({ tree: [], flat: [] });
  const [tags, setTags] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedCollection, setSelectedCollection] = useState(null);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [typeFilter, setTypeFilter] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [showNewCollection, setShowNewCollection] = useState(false);
  const searchTimer = useRef(null);

  // ── Paginated document loading ────────────────────
  const fetchDocs = useCallback(async (offset, limit) => {
    const params = { offset, limit };
    if (selectedCollection) params.collection_id = selectedCollection;
    if (typeFilter) params.doc_type = typeFilter;
    return await apiClient.getDocuments(params);
  }, [apiClient, selectedCollection, typeFilter]);

  const {
    items: documents, loading: docsLoading, hasMore, loadMore, reset: resetDocs
  } = usePagination(fetchDocs, { pageSize: 25, deps: [selectedCollection, typeFilter] });

  // ── Load other data ───────────────────────────────
  const loadCollections = useCallback(async () => {
    try { setCollections(await apiClient.getCollections()); } catch {}
  }, [apiClient]);

  const loadTags = useCallback(async () => {
    try { setTags(await apiClient.getLibraryTags()); } catch {}
  }, [apiClient]);

  const loadStats = useCallback(async () => {
    try { setStats(await apiClient.getLibraryStats()); } catch {}
  }, [apiClient]);

  useEffect(() => { loadCollections(); loadTags(); loadStats(); }, []);

  // ── Search ──────────────────────────────────────
  const handleSearch = (q) => {
    setSearchQuery(q);
    clearTimeout(searchTimer.current);
    if (!q.trim()) { setSearchResults(null); return; }
    searchTimer.current = setTimeout(async () => {
      try { setSearchResults(await apiClient.searchLibrary(q)); } catch {}
    }, 300);
  };

  // ── Open doc ────────────────────────────────────
  const openDocument = async (id) => {
    try {
      const doc = await apiClient.getDocument(id);
      setSelectedDoc(doc);
    } catch (err) { alert(`Failed to load: ${err.message}`); }
  };

  // ── Create document ─────────────────────────────
  const handleCreate = async (data) => {
    try {
      const doc = await apiClient.createDocument(data);
      setShowCreate(false);
      resetDocs();
      loadStats();
      loadCollections();
      setSelectedDoc(doc);
    } catch (err) { alert(`Failed: ${err.message}`); }
  };

  // ── Create collection ───────────────────────────
  const handleCreateCollection = async (data) => {
    try {
      await apiClient.createCollection(data);
      setShowNewCollection(false);
      loadCollections();
    } catch (err) { alert(`Failed: ${err.message}`); }
  };

  // ── Delete / Archive ────────────────────────────
  const handleDelete = async (id) => {
    if (!confirm("Delete this document?")) return;
    try {
      await apiClient.deleteDocument(id);
      setSelectedDoc(null);
      resetDocs(); loadStats(); loadCollections();
    } catch (err) { alert(`Failed: ${err.message}`); }
  };

  const handlePin = async (id, pinned) => {
    try {
      await apiClient.updateDocument(id, { pinned: !pinned });
      resetDocs();
      if (selectedDoc?.id === id) openDocument(id);
    } catch {}
  };

  // ── Computed ────────────────────────────────────
  const displayDocs = searchResults || documents;
  const collectionName = selectedCollection
    ? collections.flat.find(c => c.id === selectedCollection)?.name
    : "All Documents";

  // ════════════════════════════════════════════════
  //  READING PANEL (when a doc is selected)
  // ════════════════════════════════════════════════
  if (selectedDoc) {
    const d = selectedDoc;
    return (
      <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 110px)" }}>
        {/* Top bar */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 0 12px", borderBottom: `1px solid ${C.border}`, marginBottom: 16, flexShrink: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <button onClick={() => setSelectedDoc(null)} style={{ fontSize: 12, color: C.dim, background: "none", border: "none", cursor: "pointer" }}>← Back</button>
            <span style={{ color: C.border }}>|</span>
            {d.collection_icon && <span>{d.collection_icon}</span>}
            <span style={{ fontSize: 11, color: C.faint }}>{d.collection_name || "Uncategorized"}</span>
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            <button onClick={() => handlePin(d.id, d.pinned)} style={{ fontSize: 11, padding: "4px 10px", borderRadius: 6, background: d.pinned ? C.amber + "20" : "transparent", color: d.pinned ? C.amber : C.dim, border: `1px solid ${C.border}`, cursor: "pointer" }}>{d.pinned ? "★ Pinned" : "☆ Pin"}</button>
            <button onClick={() => handleDelete(d.id)} style={{ fontSize: 11, padding: "4px 10px", borderRadius: 6, color: C.red, background: "transparent", border: `1px solid ${C.border}`, cursor: "pointer" }}>Delete</button>
          </div>
        </div>

        {/* Document header */}
        <div style={{ marginBottom: 20, flexShrink: 0 }}>
          <div style={{ display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap", marginBottom: 8 }}>
            <span style={{ fontSize: 20 }}>{DOC_TYPE_ICONS[d.doc_type] || "📄"}</span>
            <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 4, color: C.accent, background: C.accent + "20" }}>{d.doc_type}</span>
            <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 4, color: C.dim, background: C.border }}>{FORMAT_LABELS[d.format] || d.format}</span>
            <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 4, color: C.green, background: C.green + "20" }}>{d.status}</span>
            <span style={{ fontSize: 10, color: C.faint }}>v{d.version}</span>
            {d.tags?.map(t => (
              <span key={t.id} style={{ fontSize: 9, padding: "2px 7px", borderRadius: 4, color: t.color, background: t.color + "20" }}>#{t.name}</span>
            ))}
          </div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: "#fff", margin: "0 0 8px" }}>{d.title}</h1>
          <div style={{ display: "flex", gap: 16, fontSize: 11, color: C.faint, flexWrap: "wrap" }}>
            {d.author_agent && <span>By: <span style={{ color: C.muted }}>{d.author_agent}</span></span>}
            {d.project_name && <span>Project: <span style={{ color: C.muted }}>{d.project_name}</span></span>}
            {d.task_title && <span>Task: <span style={{ color: C.muted }}>{d.task_title}</span></span>}
            <span>{d.word_count.toLocaleString()} words</span>
            <span>Published: {d.published_at ? new Date(d.published_at).toLocaleDateString() : "—"}</span>
            <span>Updated: {new Date(d.updated_at).toLocaleDateString()}</span>
          </div>
        </div>

        {/* Content area */}
        <div style={{ flex: 1, overflow: "auto", padding: "0 4px 20px" }}>
          <div style={{ maxWidth: 780 }}>
            <MarkdownRenderer content={d.content} format={d.format} />
          </div>
        </div>

        {/* Version history footer */}
        {d.version_history?.length > 1 && (
          <div style={{ borderTop: `1px solid ${C.border}`, padding: "10px 0 0", marginTop: 12, flexShrink: 0 }}>
            <div style={{ fontSize: 10, color: C.dim, marginBottom: 4 }}>Version History</div>
            <div style={{ display: "flex", gap: 6, overflowX: "auto" }}>
              {d.version_history.map(v => (
                <span key={v.id} style={{ fontSize: 10, padding: "3px 8px", borderRadius: 6, background: v.version === d.version ? C.accent + "20" : C.border, color: v.version === d.version ? C.accent : C.faint, whiteSpace: "nowrap" }}>
                  v{v.version} · {v.changed_by} · {v.change_note || new Date(v.created_at).toLocaleDateString()}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // ════════════════════════════════════════════════
  //  BROWSE VIEW (collection sidebar + doc list)
  // ════════════════════════════════════════════════
  return (
    <div style={{ display: "flex", gap: 16, height: "calc(100vh - 110px)" }}>
      {/* ── Collection Sidebar ─────────────────────── */}
      <div style={{ width: 220, flexShrink: 0, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
          <span style={{ fontSize: 11, fontWeight: 600, color: C.muted, textTransform: "uppercase", letterSpacing: 1 }}>Collections</span>
          <button onClick={() => setShowNewCollection(true)} style={{ fontSize: 14, color: C.dim, background: "none", border: "none", cursor: "pointer", lineHeight: 1 }} title="New collection">+</button>
        </div>

        <div style={{ flex: 1, overflow: "auto" }}>
          {/* All documents */}
          <button onClick={() => setSelectedCollection(null)}
            style={{ width: "100%", display: "flex", alignItems: "center", gap: 8, padding: "7px 10px", borderRadius: 8, border: "none", cursor: "pointer", fontSize: 12, marginBottom: 2, background: !selectedCollection ? C.accent + "20" : "transparent", color: !selectedCollection ? C.accentH : C.muted, textAlign: "left" }}>
            <span>📚</span><span style={{ flex: 1 }}>All Documents</span>
            <span style={{ fontSize: 10, color: C.faint }}>{stats?.total || 0}</span>
          </button>

          {/* Collection tree */}
          {collections.tree.map(col => (
            <div key={col.id}>
              <button onClick={() => setSelectedCollection(selectedCollection === col.id ? null : col.id)}
                style={{ width: "100%", display: "flex", alignItems: "center", gap: 8, padding: "7px 10px", borderRadius: 8, border: "none", cursor: "pointer", fontSize: 12, marginBottom: 2, background: selectedCollection === col.id ? C.accent + "20" : "transparent", color: selectedCollection === col.id ? C.accentH : C.muted, textAlign: "left" }}>
                <span>{col.icon}</span><span style={{ flex: 1 }}>{col.name}</span>
                <span style={{ fontSize: 10, color: C.faint }}>{col.doc_count}</span>
              </button>
              {/* Children */}
              {col.children?.map(child => (
                <button key={child.id} onClick={() => setSelectedCollection(selectedCollection === child.id ? null : child.id)}
                  style={{ width: "100%", display: "flex", alignItems: "center", gap: 8, padding: "6px 10px 6px 28px", borderRadius: 8, border: "none", cursor: "pointer", fontSize: 11, marginBottom: 1, background: selectedCollection === child.id ? C.accent + "20" : "transparent", color: selectedCollection === child.id ? C.accentH : C.dim, textAlign: "left" }}>
                  <span>{child.icon}</span><span style={{ flex: 1 }}>{child.name}</span>
                  <span style={{ fontSize: 10, color: C.faint }}>{child.doc_count}</span>
                </button>
              ))}
            </div>
          ))}
        </div>

        {/* Stats footer */}
        {stats && (
          <div style={{ borderTop: `1px solid ${C.border}`, paddingTop: 10, marginTop: 10, fontSize: 10, color: C.faint }}>
            <div>{stats.total} documents · {stats.totalWords.toLocaleString()} words</div>
          </div>
        )}
      </div>

      {/* ── Document List ──────────────────────────── */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        {/* Toolbar */}
        <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 12, flexShrink: 0 }}>
          <input value={searchQuery} onChange={e => handleSearch(e.target.value)}
            placeholder="Search documents..."
            style={{ flex: 1, background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: "7px 12px", fontSize: 12, color: "#fff", outline: "none", boxSizing: "border-box" }} />
          <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)}
            style={{ fontSize: 11, background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: "7px 10px", color: C.muted, outline: "none" }}>
            <option value="">All Types</option>
            {["research", "report", "documentation", "reference", "template", "note", "analysis", "brief", "guide"].map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
          <button onClick={() => setShowCreate(true)}
            style={{ fontSize: 12, padding: "7px 14px", borderRadius: 8, background: C.accent, color: "#fff", border: "none", cursor: "pointer", whiteSpace: "nowrap" }}>
            + New Doc
          </button>
        </div>

        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8, flexShrink: 0 }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: "#fff" }}>
            {searchResults ? `Search results for "${searchQuery}"` : collectionName}
          </span>
          <span style={{ fontSize: 11, color: C.faint }}>{displayDocs.length} document{displayDocs.length !== 1 ? "s" : ""}</span>
        </div>

        {/* Doc list */}
        <div style={{ flex: 1, overflow: "auto", display: "flex", flexDirection: "column", gap: 6 }}>
          {displayDocs.map(d => (
            <div key={d.id} onClick={() => openDocument(d.id)}
              style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 10, padding: 14, cursor: "pointer", transition: "transform .15s, box-shadow .15s" }}
              onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-1px)"; e.currentTarget.style.boxShadow = "0 4px 20px rgba(0,0,0,0.3)"; }}
              onMouseLeave={e => { e.currentTarget.style.transform = ""; e.currentTarget.style.boxShadow = ""; }}>
              <div style={{ display: "flex", gap: 12 }}>
                {/* Icon */}
                <div style={{ width: 36, height: 36, borderRadius: 8, background: C.accent + "10", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, flexShrink: 0 }}>
                  {DOC_TYPE_ICONS[d.doc_type] || "📄"}
                </div>
                {/* Content */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 3, flexWrap: "wrap" }}>
                    {d.pinned === 1 && <span style={{ fontSize: 10, color: C.amber }}>★</span>}
                    <span style={{ fontSize: 13, fontWeight: 500, color: "#fff" }}>{d.title}</span>
                    <span style={{ fontSize: 9, padding: "1px 6px", borderRadius: 3, color: C.accent, background: C.accent + "15" }}>{d.doc_type}</span>
                    <span style={{ fontSize: 9, padding: "1px 5px", borderRadius: 3, color: C.dim, background: C.border }}>{FORMAT_LABELS[d.format]}</span>
                  </div>
                  <div style={{ fontSize: 11, color: C.dim, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", marginBottom: 4 }}>
                    {d.content_highlight
                      ? <span dangerouslySetInnerHTML={{ __html: d.content_highlight.slice(0, 150) }} />
                      : (d.excerpt || "No content")}
                  </div>
                  <div style={{ display: "flex", gap: 10, fontSize: 10, color: C.faint, flexWrap: "wrap" }}>
                    {d.collection_icon && <span>{d.collection_icon} {d.collection_name}</span>}
                    {d.author_agent && <span>by {d.author_agent}</span>}
                    {d.project_name && <span>{d.project_name}</span>}
                    <span>{d.word_count?.toLocaleString()} words</span>
                    <span>{new Date(d.updated_at).toLocaleDateString()}</span>
                    {d.tags?.map(t => <span key={t.id} style={{ color: t.color }}>#{t.name}</span>)}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {/* Load more */}
          {!searchResults && hasMore && displayDocs.length > 0 && (
            <div style={{ textAlign: "center", padding: "12px 0" }}>
              <button onClick={loadMore} disabled={docsLoading}
                style={{ fontSize: 12, padding: "6px 20px", borderRadius: 8, background: C.accent + "15", color: C.accent, border: "none", cursor: docsLoading ? "wait" : "pointer", opacity: docsLoading ? 0.5 : 1 }}>
                {docsLoading ? "Loading..." : "Load More"}
              </button>
            </div>
          )}
          {docsLoading && displayDocs.length === 0 && (
            <div style={{ textAlign: "center", padding: "32px 0", color: C.dim, fontSize: 12 }}>Loading documents...</div>
          )}

          {displayDocs.length === 0 && !docsLoading && (
            <div style={{ textAlign: "center", padding: "48px 0" }}>
              <div style={{ fontSize: 28, marginBottom: 8 }}>📚</div>
              <div style={{ fontSize: 14, color: C.muted, marginBottom: 4 }}>
                {searchResults ? "No documents match your search" : "No documents in this collection yet"}
              </div>
              <div style={{ fontSize: 11, color: C.faint }}>
                Documents are published here by agents via hooks, or you can create them manually.
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── Create Document Modal ──────────────────── */}
      {showCreate && <CreateDocModal
        collections={collections.flat}
        projects={projects}
        agents={agents}
        tags={tags}
        onSubmit={handleCreate}
        onClose={() => setShowCreate(false)}
      />}

      {/* ── Create Collection Modal ────────────────── */}
      {showNewCollection && <CreateCollectionModal
        collections={collections.flat}
        onSubmit={handleCreateCollection}
        onClose={() => setShowNewCollection(false)}
      />}
    </div>
  );
}

// ── Create Document Modal ─────────────────────────────
function CreateDocModal({ collections, projects, agents, tags, onSubmit, onClose }) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [docType, setDocType] = useState("document");
  const [format, setFormat] = useState("markdown");
  const [collectionId, setCollectionId] = useState("");
  const [projectId, setProjectId] = useState("");
  const [selectedTags, setSelectedTags] = useState([]);

  return (
    <div onClick={onClose} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", display: "flex", justifyContent: "center", alignItems: "flex-start", zIndex: 50, overflowY: "auto", padding: "32px 16px" }}>
      <div onClick={e => e.stopPropagation()} style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24, width: "100%", maxWidth: 580 }}>
        <h2 style={{ fontSize: 16, fontWeight: 600, color: "#fff", margin: "0 0 16px" }}>New Document</h2>

        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <input value={title} onChange={e => setTitle(e.target.value)} placeholder="Document title"
            style={{ width: "100%", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "8px 12px", fontSize: 14, color: "#fff", outline: "none", boxSizing: "border-box" }} autoFocus />

          <div style={{ display: "flex", gap: 8 }}>
            <select value={docType} onChange={e => setDocType(e.target.value)}
              style={{ flex: 1, fontSize: 11, background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6, padding: "6px 8px", color: C.muted, outline: "none" }}>
              {["research", "report", "documentation", "reference", "template", "note", "analysis", "brief", "guide", "other"].map(t =>
                <option key={t} value={t}>{DOC_TYPE_ICONS[t]} {t}</option>
              )}
            </select>
            <select value={format} onChange={e => setFormat(e.target.value)}
              style={{ flex: 1, fontSize: 11, background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6, padding: "6px 8px", color: C.muted, outline: "none" }}>
              {["markdown", "html", "code", "json", "text", "csv"].map(f => <option key={f} value={f}>{f}</option>)}
            </select>
          </div>

          <div style={{ display: "flex", gap: 8 }}>
            <select value={collectionId} onChange={e => setCollectionId(e.target.value)}
              style={{ flex: 1, fontSize: 11, background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6, padding: "6px 8px", color: C.muted, outline: "none" }}>
              <option value="">No collection</option>
              {collections.map(c => <option key={c.id} value={c.id}>{c.icon} {c.name}</option>)}
            </select>
            <select value={projectId} onChange={e => setProjectId(e.target.value)}
              style={{ flex: 1, fontSize: 11, background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6, padding: "6px 8px", color: C.muted, outline: "none" }}>
              <option value="">No project</option>
              {projects?.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>

          {/* Tags */}
          {tags.length > 0 && (
            <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
              {tags.map(t => (
                <button key={t.id} onClick={() => setSelectedTags(s => s.includes(t.id) ? s.filter(x => x !== t.id) : [...s, t.id])}
                  style={{ fontSize: 10, padding: "3px 8px", borderRadius: 4, border: "none", cursor: "pointer", color: selectedTags.includes(t.id) ? t.color : C.dim, background: selectedTags.includes(t.id) ? t.color + "25" : C.border }}>
                  #{t.name}
                </button>
              ))}
            </div>
          )}

          <textarea value={content} onChange={e => setContent(e.target.value)} placeholder="Document content..."
            style={{ width: "100%", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "10px 12px", fontSize: 12, color: C.text, outline: "none", resize: "vertical", height: 200, fontFamily: format === "code" || format === "json" ? "monospace" : "inherit", lineHeight: 1.6, boxSizing: "border-box" }} />

          <div style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}>
            <button onClick={onClose} style={{ fontSize: 12, padding: "6px 14px", color: C.dim, background: "none", border: "none", cursor: "pointer" }}>Cancel</button>
            <button onClick={() => { if (title.trim()) onSubmit({ title: title.trim(), content, doc_type: docType, format, collection_id: collectionId || undefined, project_id: projectId || undefined, tags: selectedTags }); }}
              style={{ fontSize: 12, padding: "6px 16px", borderRadius: 8, background: C.accent, color: "#fff", border: "none", cursor: "pointer" }}>Publish</button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Create Collection Modal ───────────────────────────
function CreateCollectionModal({ collections, onSubmit, onClose }) {
  const [name, setName] = useState("");
  const [icon, setIcon] = useState("📁");
  const [parentId, setParentId] = useState("");

  const emojis = ["📁", "🔬", "📊", "📖", "📚", "📋", "📝", "📈", "🗺", "📎", "🎯", "💡", "🔧", "🏗", "📐"];

  return (
    <div onClick={onClose} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", display: "flex", justifyContent: "center", alignItems: "center", zIndex: 50 }}>
      <div onClick={e => e.stopPropagation()} style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24, width: "100%", maxWidth: 400 }}>
        <h2 style={{ fontSize: 16, fontWeight: 600, color: "#fff", margin: "0 0 16px" }}>New Collection</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <input value={name} onChange={e => setName(e.target.value)} placeholder="Collection name"
            style={{ width: "100%", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "8px 12px", fontSize: 13, color: "#fff", outline: "none", boxSizing: "border-box" }} autoFocus />
          <div>
            <div style={{ fontSize: 10, color: C.faint, marginBottom: 4 }}>Icon</div>
            <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
              {emojis.map(e => (
                <button key={e} onClick={() => setIcon(e)}
                  style={{ fontSize: 18, padding: "4px 6px", borderRadius: 6, border: icon === e ? `2px solid ${C.accent}` : `1px solid ${C.border}`, background: icon === e ? C.accent + "15" : "transparent", cursor: "pointer" }}>{e}</button>
              ))}
            </div>
          </div>
          <select value={parentId} onChange={e => setParentId(e.target.value)}
            style={{ fontSize: 11, background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6, padding: "6px 8px", color: C.muted, outline: "none" }}>
            <option value="">Top level</option>
            {collections.map(c => <option key={c.id} value={c.id}>{c.icon} {c.name}</option>)}
          </select>
          <div style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}>
            <button onClick={onClose} style={{ fontSize: 12, padding: "6px 14px", color: C.dim, background: "none", border: "none", cursor: "pointer" }}>Cancel</button>
            <button onClick={() => { if (name.trim()) onSubmit({ name: name.trim(), icon, parent_id: parentId || undefined }); }}
              style={{ fontSize: 12, padding: "6px 16px", borderRadius: 8, background: C.accent, color: "#fff", border: "none", cursor: "pointer" }}>Create</button>
          </div>
        </div>
      </div>
    </div>
  );
}
