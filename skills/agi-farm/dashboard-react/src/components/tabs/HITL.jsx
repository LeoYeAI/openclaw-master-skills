import { useState } from 'react';
import LastUpdated from '../LastUpdated';

async function apiPost(path, body = {}) {
  const r = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  return r.json();
}

function relTime(iso) {
  if (!iso) return '—';
  try {
    const diff = Math.round((Date.now() - new Date(iso)) / 60000);
    if (diff < 1) return 'just now';
    if (diff < 60) return `${diff}m ago`;
    if (diff < 1440) return `${Math.round(diff / 60)}h ago`;
    return `${Math.round(diff / 1440)}d ago`;
  } catch { return iso; }
}

function HITLCard({ task, agents, onAction }) {
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(null);
  const agent = agents.find(a => a.id === task.assigned_to);
  const waitTime = relTime(task.created_at);
  const pri = (task.sla?.priority || task.priority || '').toUpperCase();

  async function act(action) {
    setLoading(action);
    try {
      await apiPost(`/api/hitl/${task.id}/${action}`, { note: note || undefined });
      onAction(task.id, action);
    } catch (e) { console.error(e); }
    setLoading(null);
  }

  return (
    <div style={{
      background: 'var(--bg2)', border: '1px solid rgba(224,64,251,.35)',
      borderRadius: 10, padding: 18, display: 'grid', gap: 14,
      boxShadow: '0 0 20px rgba(224,64,251,.08)',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
        <span style={{ fontSize: 28 }}>🚨</span>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4, flexWrap: 'wrap' }}>
            <span style={{ fontWeight: 700, fontSize: 15 }}>{task.title}</span>
            <span style={{ fontSize: 10, fontFamily: 'monospace', color: 'var(--muted)' }}>{task.id}</span>
            {pri && <span className={pri === 'P1' ? 'p1' : pri === 'P2' ? 'p2' : 'p3'}>{pri}</span>}
          </div>
          <div style={{ fontSize: 11, color: 'var(--muted)' }}>
            {agent && <span>{agent.emoji} {agent.name} · </span>}
            Waiting <span style={{ color: 'var(--amber)', fontWeight: 600 }}>{waitTime}</span>
            {task.sla?.deadline && <span> · Due {new Date(task.sla.deadline).toLocaleString()}</span>}
          </div>
        </div>
      </div>

      {/* HITL Reason */}
      <div style={{ padding: '12px 14px', background: 'rgba(224,64,251,.08)', border: '1px solid rgba(224,64,251,.25)', borderRadius: 7 }}>
        <div style={{ fontSize: 10, color: 'var(--purple)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: 6 }}>Decision Required</div>
        <div style={{ fontSize: 13, color: 'var(--text)', lineHeight: 1.6 }}>{task.hitl_reason || 'Human decision required before proceeding.'}</div>
      </div>

      {/* Description */}
      {task.description && (
        <div>
          <div style={{ fontSize: 10, color: 'var(--muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.05em', marginBottom: 4 }}>Context</div>
          <div style={{ fontSize: 12, color: 'var(--text)', lineHeight: 1.6 }}>{task.description}</div>
        </div>
      )}

      {/* Note input */}
      <div>
        <div style={{ fontSize: 10, color: 'var(--muted)', marginBottom: 6 }}>Optional note (sent to agent)</div>
        <input value={note} onChange={e => setNote(e.target.value)}
          placeholder="Add context for the agent..."
          style={{ width: '100%', background: 'var(--bg3)', border: '1px solid var(--border)', borderRadius: 5,
            padding: '8px 10px', fontSize: 12, color: 'var(--text)', fontFamily: 'inherit', outline: 'none',
            boxSizing: 'border-box' }} />
      </div>

      {/* Action buttons */}
      <div style={{ display: 'flex', gap: 10 }}>
        <button onClick={() => act('approve')} disabled={!!loading} style={{
          flex: 1, padding: '10px', background: 'rgba(0,230,118,.15)', border: '1px solid rgba(0,230,118,.4)',
          color: 'var(--green)', borderRadius: 6, cursor: loading ? 'not-allowed' : 'pointer',
          fontFamily: 'inherit', fontSize: 13, fontWeight: 700, transition: 'all .15s',
        }}>
          {loading === 'approve' ? '...' : '✅ Approve — Continue'}
        </button>
        <button onClick={() => act('reject')} disabled={!!loading} style={{
          flex: 1, padding: '10px', background: 'rgba(255,23,68,.1)', border: '1px solid rgba(255,23,68,.35)',
          color: 'var(--red)', borderRadius: 6, cursor: loading ? 'not-allowed' : 'pointer',
          fontFamily: 'inherit', fontSize: 13, fontWeight: 700, transition: 'all .15s',
        }}>
          {loading === 'reject' ? '...' : '❌ Reject — Block Task'}
        </button>
      </div>
    </div>
  );
}

export default function HITLTab({ data, lastUpdated }) {
  const { hitl_tasks = [], agents = [] } = data;
  const [resolved, setResolved] = useState(new Set());

  const pending = hitl_tasks.filter(t => !resolved.has(t.id));

  function onAction(taskId) {
    setResolved(prev => new Set([...prev, taskId]));
  }

  return (
    <div className="fade-in" style={{ display: 'grid', gap: 14 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 14, fontWeight: 700, color: pending.length ? 'var(--red)' : 'var(--green)' }}>
          {pending.length ? `🚨 ${pending.length} decision${pending.length > 1 ? 's' : ''} awaiting your input` : '✅ No pending HITL decisions'}
        </span>
        <LastUpdated ts={lastUpdated} />
      </div>

      {pending.length === 0 && (
        <div className="card" style={{ color: 'var(--muted)', fontSize: 13 }}>
          All clear — no human decisions required right now. Agents are running autonomously.
        </div>
      )}

      {pending.map(t => (
        <HITLCard key={t.id} task={t} agents={agents} onAction={onAction} />
      ))}

      {resolved.size > 0 && (
        <div style={{ padding: '10px 14px', background: 'rgba(0,230,118,.06)', border: '1px solid rgba(0,230,118,.2)', borderRadius: 6, fontSize: 12, color: 'var(--green)' }}>
          ✅ {resolved.size} decision{resolved.size > 1 ? 's' : ''} resolved this session — agents notified via task status update.
        </div>
      )}
    </div>
  );
}
