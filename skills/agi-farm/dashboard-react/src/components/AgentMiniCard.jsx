export default function AgentMiniCard({ agent: a }) {
  const dotCls = { active:'dot-active', available:'dot-available', busy:'dot-busy', error:'dot-error' }[a.status] || 'dot-offline';
  return (
    <div className="card" style={{ padding: 10 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
        <span style={{ fontSize: 18 }}>{a.emoji || '🤖'}</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontWeight: 600, fontSize: 12, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{a.name}</div>
          <div style={{ color: 'var(--muted)', fontSize: 10 }}>{a.role}</div>
        </div>
        {a.inbox_count > 0 && (
          <span style={{ fontSize: 10, color: 'var(--amber)', fontWeight: 600 }}>📬{a.inbox_count}</span>
        )}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <span className={`dot ${dotCls}`} />
        <span style={{ fontSize: 10, color: 'var(--muted)', textTransform: 'capitalize' }}>{a.status}</span>
        <span style={{ marginLeft: 'auto', fontSize: 10, color: 'var(--muted)' }}>
          ⭐{(a.avg_quality || 0).toFixed(1)}
        </span>
      </div>
    </div>
  );
}
