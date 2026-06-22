import { useState, useEffect } from 'react';
import LastUpdated from '../LastUpdated';

const FILTERS = ['all','pending','in-progress','complete','failed','blocked','🚨 hitl'];
const PAGE_SIZE = 25;

function useTick(intervalMs = 10000) {
  const [tick, setTick] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setTick(n => n + 1), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);
  return tick;
}

function DeadlineBadge({ deadline }) {
  useTick(10000); // recalculate every 10s
  if (!deadline) return <span style={{ color: 'var(--muted)' }}>—</span>;
  try {
    const d    = new Date(deadline);
    const diff = Math.round((d - Date.now()) / 60000); // minutes
    const abs  = Math.abs(diff);
    const over = diff < 0;
    const color = over ? 'var(--red)' : diff < 60 ? 'var(--amber)' : 'var(--muted)';
    const label = abs < 60
      ? `${over ? '-' : ''}${abs}m`
      : abs < 1440
        ? `${over ? '-' : ''}${Math.round(abs/60)}h`
        : d.toLocaleDateString();
    return (
      <span title={d.toLocaleString()} style={{ color, fontSize: 11, fontWeight: over ? 700 : 400 }}>
        {label}{over ? ' overdue' : ''}
      </span>
    );
  } catch {
    return <span style={{ color: 'var(--muted)', fontSize: 11 }}>{deadline}</span>;
  }
}

function TaskRow({ task: t, expanded, onToggle }) {
  const pri   = (t.sla?.priority || t.priority || '').toUpperCase();
  const s     = (t.status || '').toLowerCase().replace(/ /g, '-');
  const cls   = {
    'complete': 'badge-complete', 'pending': 'badge-pending',
    'in-progress': 'badge-in-progress', 'failed': 'badge-failed',
    'needs_human_decision': 'badge-hitl', 'blocked': 'badge-blocked',
  }[s] || 'badge-pending';
  const isHitl = t.status === 'needs_human_decision';

  return (
    <>
      <tr
        onClick={onToggle}
        style={{
          borderBottom: expanded ? 'none' : '1px solid rgba(255,255,255,.03)',
          background: isHitl ? 'rgba(255,23,68,.04)' : 'transparent',
          cursor: 'pointer',
        }}
      >
        <td style={{ padding: '8px 12px', color: 'var(--cyan)', fontFamily: 'monospace', fontSize: 11 }}>{t.id || '—'}</td>
        <td style={{ padding: '8px 12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            {isHitl && <span>🚨</span>}
            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 280 }}>{t.title || '—'}</span>
          </div>
        </td>
        <td style={{ padding: '8px 12px', color: 'var(--muted)', fontSize: 11 }}>{t.assigned_to || '—'}</td>
        <td style={{ padding: '8px 12px' }}>{pri && <span className={pri === 'P1' ? 'p1' : pri === 'P2' ? 'p2' : 'p3'}>{pri}</span>}</td>
        <td style={{ padding: '8px 12px' }}><span className={`badge ${cls}`}>{t.status || '—'}</span></td>
        <td style={{ padding: '8px 12px' }}><DeadlineBadge deadline={t.sla?.deadline || t.sla?.target} /></td>
        <td style={{ padding: '8px 12px', color: 'var(--muted)', fontSize: 11, textAlign: 'center' }}>
          {expanded ? '▲' : '▼'}
        </td>
      </tr>

      {/* Expanded detail row */}
      {expanded && (
        <tr style={{ background: 'rgba(0,229,255,.03)', borderBottom: '1px solid rgba(0,229,255,.08)' }}>
          <td colSpan={7} style={{ padding: '10px 14px 14px 14px' }}>
            <div style={{ display: 'grid', gap: 10 }}>
              {/* HITL reason */}
              {t.hitl_reason && (
                <div style={{ padding: '8px 12px', background: 'rgba(224,64,251,.08)', border: '1px solid rgba(224,64,251,.25)', borderRadius: 6 }}>
                  <span style={{ fontSize: 10, color: 'var(--purple)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.05em' }}>🚨 HITL Reason</span>
                  <div style={{ fontSize: 12, color: 'var(--text)', marginTop: 4 }}>{t.hitl_reason}</div>
                </div>
              )}

              {/* Description */}
              {t.description && (
                <div>
                  <div style={{ fontSize: 10, color: 'var(--muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.05em', marginBottom: 4 }}>Description</div>
                  <div style={{ fontSize: 12, color: 'var(--text)', lineHeight: 1.6 }}>{t.description}</div>
                </div>
              )}

              {/* Output */}
              {t.output && (
                <div>
                  <div style={{ fontSize: 10, color: 'var(--green)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.05em', marginBottom: 4 }}>✅ Output</div>
                  <div style={{ fontSize: 12, color: 'var(--text)', lineHeight: 1.6, background: 'rgba(0,230,118,.04)', padding: '8px 10px', borderRadius: 5, border: '1px solid rgba(0,230,118,.15)' }}>
                    {t.output}
                  </div>
                </div>
              )}

              {/* Meta row */}
              <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', fontSize: 10, color: 'var(--muted)', borderTop: '1px solid rgba(255,255,255,.04)', paddingTop: 8 }}>
                {t.type        && <span>Type: <span style={{ color: 'var(--cyan)' }}>{t.type}</span></span>}
                {t.proc_id     && <span>Proc: <span style={{ color: 'var(--cyan)' }}>{t.proc_id}</span></span>}
                {t.created_at  && <span>Created: {new Date(t.created_at).toLocaleString()}</span>}
                {t.completed_at && <span style={{ color: 'var(--green)' }}>Completed: {new Date(t.completed_at).toLocaleString()}</span>}
                {t.depends_on?.length > 0 && <span>Depends on: {t.depends_on.join(', ')}</span>}
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

export default function Tasks({ data, lastUpdated }) {
  const { tasks = [] } = data;
  const [filter, setFilter]   = useState('all');
  const [page, setPage]       = useState(0);
  const [expanded, setExpanded] = useState(null);

  const filtered = tasks.filter(t => {
    if (filter === 'all') return true;
    if (filter === '🚨 hitl') return t.status === 'needs_human_decision';
    return t.status === filter;
  });

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const paged      = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  const toggle = (id) => setExpanded(prev => prev === id ? null : id);

  // Reset page when filter changes
  const setFilterAndReset = (f) => { setFilter(f); setPage(0); setExpanded(null); };

  const filterCount = (f) => f === '🚨 hitl'
    ? tasks.filter(t => t.status === 'needs_human_decision').length
    : tasks.filter(t => t.status === f).length;

  return (
    <div className="fade-in">
      {/* Filter bar */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 14, flexWrap: 'wrap', alignItems: 'center' }}>
        {FILTERS.map(f => (
          <button key={f} onClick={() => setFilterAndReset(f)} style={{
            background: filter === f ? 'rgba(0,229,255,.15)' : 'var(--surface)',
            border: `1px solid ${filter === f ? 'rgba(0,229,255,.5)' : 'var(--border)'}`,
            color: filter === f ? 'var(--cyan)' : 'var(--muted)',
            padding: '4px 12px', borderRadius: 4, fontSize: 11, cursor: 'pointer', fontFamily: 'inherit',
          }}>
            {f}{f !== 'all' && ` (${filterCount(f)})`}
          </button>
        ))}
        <span style={{ marginLeft: 'auto', fontSize: 10, color: 'var(--muted)' }}>
          {filtered.length} task{filtered.length !== 1 ? 's' : ''}
        </span>
        <LastUpdated ts={lastUpdated} />
      </div>

      {/* Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ background: 'var(--bg3)', borderBottom: '1px solid var(--border)' }}>
              {['ID', 'Title', 'Assigned To', 'Priority', 'Status', 'Deadline', ''].map(h => (
                <th key={h} style={{ padding: '8px 12px', textAlign: 'left', fontSize: 10,
                  color: 'var(--muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.05em' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paged.length === 0 && (
              <tr><td colSpan={7} style={{ padding: '20px 12px', color: 'var(--muted)', textAlign: 'center' }}>No tasks</td></tr>
            )}
            {paged.map(t => (
              <TaskRow key={t.id} task={t} expanded={expanded === t.id} onToggle={() => toggle(t.id)} />
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', gap: 8, marginTop: 12, alignItems: 'center', justifyContent: 'center' }}>
          <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0}
            style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: page === 0 ? 'var(--muted)' : 'var(--cyan)',
              padding: '4px 12px', borderRadius: 4, cursor: page === 0 ? 'not-allowed' : 'pointer', fontFamily: 'inherit', fontSize: 11 }}>
            ← Prev
          </button>
          <span style={{ fontSize: 11, color: 'var(--muted)' }}>
            Page {page + 1} / {totalPages} ({filtered.length} total)
          </span>
          <button onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page === totalPages - 1}
            style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: page === totalPages - 1 ? 'var(--muted)' : 'var(--cyan)',
              padding: '4px 12px', borderRadius: 4, cursor: page === totalPages - 1 ? 'not-allowed' : 'pointer', fontFamily: 'inherit', fontSize: 11 }}>
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
