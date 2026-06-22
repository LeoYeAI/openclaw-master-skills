import { useState } from 'react';
import LastUpdated from '../LastUpdated';

const SEV_COLOR  = { critical: 'var(--red)', high: 'var(--red)', medium: 'var(--amber)', low: 'var(--muted)' };
const TYPE_ICON  = { hitl: '🚨', sla_breach: '⏰', agent_error: '🔴', cron_error: '⚙️', blocked: '🚫' };
const TYPE_LABEL = { hitl: 'HITL', sla_breach: 'SLA', agent_error: 'Agent', cron_error: 'Cron', blocked: 'Blocked' };

function relTime(iso) {
  if (!iso) return '';
  try {
    const diff = Math.round((Date.now() - new Date(iso)) / 60000);
    if (diff < 1) return 'just now';
    if (diff < 60) return `${diff}m ago`;
    return `${Math.round(diff / 60)}h ago`;
  } catch { return ''; }
}

export default function AlertsTab({ data, lastUpdated }) {
  const { alerts = [], agents = [] } = data;
  const [dismissed, setDismissed] = useState(new Set());
  const [typeFilter, setTypeFilter] = useState('all');

  const active = alerts.filter(a => !dismissed.has(a.id));
  const filtered = active.filter(a => typeFilter === 'all' || a.type === typeFilter);

  const types = ['all', ...new Set(alerts.map(a => a.type))];
  const bySev = { critical: 0, high: 0, medium: 0, low: 0 };
  active.forEach(a => { if (bySev[a.severity] !== undefined) bySev[a.severity]++; });

  return (
    <div className="fade-in" style={{ display: 'grid', gap: 14 }}>
      {/* Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10 }}>
        {Object.entries(bySev).map(([sev, count]) => (
          <div key={sev} className="card" style={{ textAlign: 'center' }}>
            <div className="section-title" style={{ textTransform: 'capitalize' }}>{sev}</div>
            <div style={{ fontSize: 22, fontWeight: 700, color: count ? SEV_COLOR[sev] : 'var(--muted)' }}>{count}</div>
          </div>
        ))}
      </div>

      {/* Filters + header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
        {types.map(t => (
          <button key={t} onClick={() => setTypeFilter(t)} style={{
            background: typeFilter === t ? 'rgba(0,229,255,.15)' : 'var(--surface)',
            border: `1px solid ${typeFilter === t ? 'rgba(0,229,255,.4)' : 'var(--border)'}`,
            color: typeFilter === t ? 'var(--cyan)' : 'var(--muted)',
            padding: '4px 12px', borderRadius: 4, fontSize: 11, cursor: 'pointer', fontFamily: 'inherit',
          }}>{TYPE_ICON[t] || ''} {TYPE_LABEL[t] || t}</button>
        ))}
        {dismissed.size > 0 && (
          <button onClick={() => setDismissed(new Set())} style={{
            marginLeft: 'auto', background: 'none', border: '1px solid var(--border)',
            color: 'var(--muted)', padding: '4px 10px', borderRadius: 4, fontSize: 11,
            cursor: 'pointer', fontFamily: 'inherit',
          }}>↺ Restore {dismissed.size} dismissed</button>
        )}
        <LastUpdated ts={lastUpdated} />
      </div>

      {/* Alert list */}
      {filtered.length === 0 && (
        <div className="card" style={{ color: 'var(--green)', fontSize: 13 }}>
          ✅ {alerts.length === 0 ? 'No alerts — all systems nominal.' : 'All alerts dismissed for this session.'}
        </div>
      )}

      {filtered.map(alert => {
        const color = SEV_COLOR[alert.severity] || 'var(--muted)';
        const agent = agents.find(a => a.id === alert.agent_id);
        return (
          <div key={alert.id} style={{
            background: 'var(--bg2)', borderRadius: 8,
            border: `1px solid ${color}44`,
            boxShadow: `0 0 12px ${color}0d`,
            display: 'flex', gap: 14, padding: '14px 16px', alignItems: 'flex-start',
          }}>
            <span style={{ fontSize: 22, flexShrink: 0 }}>{TYPE_ICON[alert.type] || '⚠️'}</span>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4, flexWrap: 'wrap' }}>
                <span style={{ fontWeight: 700, fontSize: 13 }}>{alert.title}</span>
                <span style={{ fontSize: 10, padding: '1px 6px', borderRadius: 3, fontWeight: 700,
                  textTransform: 'uppercase', color, background: `${color}18`, border: `1px solid ${color}44` }}>
                  {alert.severity}
                </span>
              </div>
              {alert.detail && <div style={{ fontSize: 12, color: 'var(--muted)', lineHeight: 1.5, marginBottom: 4 }}>{alert.detail}</div>}
              <div style={{ fontSize: 10, color: 'var(--muted)', display: 'flex', gap: 10 }}>
                {agent && <span>{agent.emoji} {agent.name}</span>}
                <span>{TYPE_LABEL[alert.type]}</span>
                <span>{relTime(alert.ts)}</span>
                {alert.task_id && <span style={{ color: 'var(--cyan)' }}>{alert.task_id}</span>}
                {alert.cron_id && <span style={{ color: 'var(--cyan)', fontFamily: 'monospace', fontSize: 9 }}>{alert.cron_id.slice(0, 8)}…</span>}
              </div>
            </div>
            <button onClick={() => setDismissed(prev => new Set([...prev, alert.id]))}
              title="Dismiss alert" style={{
                background: 'none', border: '1px solid var(--border)', color: 'var(--muted)',
                padding: '3px 8px', borderRadius: 4, cursor: 'pointer', fontSize: 10, fontFamily: 'inherit', flexShrink: 0,
              }}>✕</button>
          </div>
        );
      })}
    </div>
  );
}
