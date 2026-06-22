import LastUpdated from '../LastUpdated';

export default function Agents({ data, lastUpdated }) {
  const { agents = [], cache_age_seconds } = data;
  const cacheAge = cache_age_seconds ?? null;

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 12, gap: 12 }}>
        <span style={{ fontSize: 10, color: 'var(--muted)' }}>
          {agents.length} agents
        </span>
        {cacheAge != null && (
          <span style={{ fontSize: 10, color: cacheAge > 25 ? 'var(--amber)' : 'var(--muted)' }}>
            🔄 Agent/cron data cached {cacheAge}s ago (refreshes every 30s)
          </span>
        )}
        <LastUpdated ts={lastUpdated} />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(280px,1fr))', gap: 14 }}>
        {agents.map(a => <AgentCard key={a.id} agent={a} />)}
      </div>
    </div>
  );
}

function AgentCard({ agent: a }) {
  const dotCls = { active:'dot-active', available:'dot-available', busy:'dot-busy', error:'dot-error' }[a.status] || 'dot-offline';
  const badgeCls = { active:'badge-active', available:'badge-available', busy:'badge-busy', error:'badge-error' }[a.status] || 'badge-offline';
  const cred = a.credibility ?? 1.0;
  return (
    <div className="card">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
        <span style={{ fontSize: 28 }}>{a.emoji || '🤖'}</span>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, fontSize: 15 }}>{a.name}</div>
          <div style={{ color: 'var(--muted)', fontSize: 11 }}>{a.role}</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, justifyContent: 'flex-end' }}>
            <span className={`dot ${dotCls}`} />
            <span className={`badge ${badgeCls}`}>{a.status}</span>
          </div>
          {a.inbox_count > 0 && (
            <div style={{ fontSize: 11, color: 'var(--amber)', marginTop: 4 }}>📬 {a.inbox_count} msgs</div>
          )}
        </div>
      </div>

      {/* Model */}
      <div style={{ fontSize: 10, color: 'var(--muted)', marginBottom: 10, fontFamily: 'monospace' }}>
        {a.model || '—'}
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8, marginBottom: 10 }}>
        <Stat label="Done" value={a.tasks_completed ?? 0} />
        <Stat label="Failed" value={a.tasks_failed ?? 0} color="var(--red)" />
        <Stat label="Quality" value={`⭐${(a.avg_quality || 0).toFixed(1)}`} color="var(--amber)" />
      </div>

      {/* Credibility */}
      <div style={{ marginBottom: 10 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: 'var(--muted)', marginBottom: 4 }}>
          <span>Credibility</span><span>{(cred * 100).toFixed(0)}%</span>
        </div>
        <div className="progress-track">
          <div className="progress-fill" style={{
            width: `${cred * 100}%`,
            background: cred > .8 ? 'var(--green)' : cred > .5 ? 'var(--amber)' : 'var(--red)',
          }} />
        </div>
      </div>

      {/* Specializations */}
      {a.specializations?.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
          {a.specializations.map(s => (
            <span key={s} style={{ fontSize: 9, padding: '2px 6px', background: 'rgba(0,229,255,.07)',
              color: 'var(--cyan)', border: '1px solid rgba(0,229,255,.2)', borderRadius: 3 }}>{s}</span>
          ))}
        </div>
      )}
    </div>
  );
}

function Stat({ label, value, color = 'var(--text)' }) {
  return (
    <div style={{ textAlign: 'center', padding: '6px', background: 'var(--surface)', borderRadius: 4 }}>
      <div style={{ fontSize: 9, color: 'var(--muted)', marginBottom: 2 }}>{label}</div>
      <div style={{ fontSize: 14, fontWeight: 700, color }}>{value}</div>
    </div>
  );
}
