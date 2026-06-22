import { useState, useMemo } from 'react';
import LastUpdated from '../LastUpdated';

export default function Knowledge({ data, lastUpdated }) {
  const { knowledge = [], agents = [] } = data;
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');

  const categories = useMemo(() => {
    const cats = new Set(knowledge.map(e => e.category || 'general'));
    return ['all', ...Array.from(cats).sort()];
  }, [knowledge]);

  const filtered = useMemo(() => {
    return knowledge.filter(e => {
      const matchCat = category === 'all' || (e.category || 'general') === category;
      const q = search.toLowerCase();
      const matchSearch = !q || (e.content || e.summary || '').toLowerCase().includes(q)
        || (e.title || '').toLowerCase().includes(q)
        || (e.tags || []).some(t => t.toLowerCase().includes(q));
      return matchCat && matchSearch;
    });
  }, [knowledge, search, category]);

  return (
    <div className="fade-in" style={{ display: 'grid', gap: 14 }}>
      {/* Search + filter */}
      <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
        <input value={search} onChange={e => setSearch(e.target.value)}
          placeholder="Search knowledge base..."
          style={{ flex: 1, minWidth: 200, background: 'var(--bg3)', border: '1px solid var(--border)',
            borderRadius: 5, padding: '7px 12px', fontSize: 12, color: 'var(--text)',
            fontFamily: 'inherit', outline: 'none' }} />
        {categories.map(c => (
          <button key={c} onClick={() => setCategory(c)} style={{
            background: category === c ? 'rgba(0,229,255,.15)' : 'var(--surface)',
            border: `1px solid ${category === c ? 'rgba(0,229,255,.4)' : 'var(--border)'}`,
            color: category === c ? 'var(--cyan)' : 'var(--muted)',
            padding: '5px 12px', borderRadius: 4, fontSize: 11, cursor: 'pointer', fontFamily: 'inherit',
            textTransform: 'capitalize',
          }}>{c}</button>
        ))}
        <LastUpdated ts={lastUpdated} />
      </div>

      <div style={{ fontSize: 11, color: 'var(--muted)' }}>
        {filtered.length} / {knowledge.length} entries
        {knowledge.length === 0 && ' — Cipher will populate this during synthesis crons'}
      </div>

      {/* Entries */}
      {filtered.length === 0 && (
        <div className="card" style={{ color: 'var(--muted)', fontSize: 13 }}>
          {knowledge.length === 0
            ? 'Knowledge base is empty. Cipher\'s synthesis cron populates SHARED_KNOWLEDGE.json every 6 hours.'
            : 'No entries match your search.'}
        </div>
      )}

      <div style={{ display: 'grid', gap: 10 }}>
        {filtered.map((entry, i) => {
          const agent = agents.find(a => a.id === entry.added_by || a.id === entry.author);
          return (
            <div key={entry.id || i} className="card">
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10, marginBottom: 8 }}>
                <div style={{ flex: 1 }}>
                  {entry.title && <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 4 }}>{entry.title}</div>}
                  <div style={{ fontSize: 12, color: 'var(--text)', lineHeight: 1.6 }}>
                    {entry.content || entry.summary || entry.insight || '—'}
                  </div>
                </div>
                <span style={{ fontSize: 10, padding: '2px 7px', borderRadius: 3, flexShrink: 0,
                  background: 'rgba(0,229,255,.07)', color: 'var(--cyan)', border: '1px solid rgba(0,229,255,.2)',
                  textTransform: 'capitalize' }}>{entry.category || 'general'}</span>
              </div>

              {entry.tags?.length > 0 && (
                <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginBottom: 8 }}>
                  {entry.tags.map(t => (
                    <span key={t} style={{ fontSize: 9, padding: '1px 5px', borderRadius: 3,
                      background: 'rgba(255,214,0,.08)', color: 'var(--amber)', border: '1px solid rgba(255,214,0,.2)' }}>{t}</span>
                  ))}
                </div>
              )}

              <div style={{ fontSize: 10, color: 'var(--muted)', display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                {agent && <span>{agent.emoji} {agent.name}</span>}
                {entry.source_task && <span>Task: <span style={{ color: 'var(--cyan)' }}>{entry.source_task}</span></span>}
                {entry.added_at && <span>{new Date(entry.added_at).toLocaleString()}</span>}
                {entry.confidence && <span>Confidence: {Math.round(entry.confidence * 100)}%</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
