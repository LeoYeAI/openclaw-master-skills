import LastUpdated from '../LastUpdated';

export default function Budget({ data, lastUpdated }) {
  const { budget = {} } = data;
  const limits      = budget.limits  || {};
  const current     = budget.current || {};
  const alerts      = budget.alerts  || {};
  const byAgent     = budget.per_agent || {};
  const byModel     = budget.per_model || {};
  const notes       = budget.notes || null;
  const lastUpdatedData = budget.last_updated || null;

  const periods = [
    { label: 'Daily',   spent: current.daily_usd   ?? 0, limit: limits.daily_usd   ?? 0, threshold: alerts.daily_threshold_pct   ?? 70 },
    { label: 'Weekly',  spent: current.weekly_usd  ?? 0, limit: limits.weekly_usd  ?? 0, threshold: alerts.weekly_threshold_pct  ?? 70 },
    { label: 'Monthly', spent: current.monthly_usd ?? 0, limit: limits.monthly_usd ?? 0, threshold: 80 },
  ];

  return (
    <div className="fade-in" style={{ display: 'grid', gap: 14 }}>

      {/* Notes banner */}
      {notes && (
        <div style={{ padding: '10px 14px', background: 'rgba(255,214,0,.07)', border: '1px solid rgba(255,214,0,.25)',
          borderRadius: 6, fontSize: 11, color: 'var(--amber)', display: 'flex', alignItems: 'flex-start', gap: 8 }}>
          <span>⚠</span>
          <div>
            <span>{notes}</span>
            {lastUpdatedData && (
              <span style={{ color: 'var(--muted)', marginLeft: 12 }}>
                Last updated: {new Date(lastUpdatedData).toLocaleString()}
              </span>
            )}
          </div>
          <LastUpdated ts={lastUpdated} />
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 14 }}>
        {periods.map(({ label, spent, limit, threshold }) => {
          const pct = limit > 0 ? Math.min(100, (spent / limit) * 100) : 0;
          const over = pct >= threshold;
          return (
            <div key={label} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <span className="section-title">{label}</span>
                <span style={{ fontSize: 11, fontWeight: 700, color: over ? 'var(--red)' : 'var(--cyan)' }}>
                  ${spent.toFixed(2)} / ${limit}
                </span>
              </div>
              {/* Progress with threshold marker */}
              <div className="progress-track" style={{ position: 'relative' }}>
                <div className="progress-fill" style={{
                  width: `${pct}%`,
                  background: pct > threshold ? 'var(--red)' : pct > threshold * 0.8 ? 'var(--amber)' : 'var(--cyan)',
                }} />
                {/* Threshold marker */}
                <div style={{
                  position: 'absolute', top: -2, bottom: -2,
                  left: `${threshold}%`, width: 1,
                  background: 'var(--amber)', opacity: 0.6,
                }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4, fontSize: 10, color: 'var(--muted)' }}>
                <span>{pct.toFixed(1)}% used</span>
                <span style={{ color: 'var(--amber)' }}>⚠ at {threshold}%</span>
              </div>
            </div>
          );
        })}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
        <BreakdownTable title="By Agent" data={byAgent} />
        <BreakdownTable title="By Model" data={byModel} />
      </div>
    </div>
  );
}

function BreakdownTable({ title, data }) {
  const entries = Object.entries(data).sort(([, a], [, b]) => {
    const sa = typeof a === 'object' ? (a.spent ?? 0) : a;
    const sb = typeof b === 'object' ? (b.spent ?? 0) : b;
    return sb - sa;
  });
  return (
    <div className="card">
      <div className="section-title">{title}</div>
      {entries.length === 0
        ? <div style={{ color: 'var(--muted)', fontSize: 11, paddingTop: 8 }}>No spend data yet</div>
        : <table style={{ width: '100%', fontSize: 11, borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <th style={{ textAlign: 'left',  padding: '4px 0', color: 'var(--muted)', fontSize: 10 }}>Name</th>
                <th style={{ textAlign: 'right', padding: '4px 0', color: 'var(--muted)', fontSize: 10 }}>Spent</th>
                <th style={{ textAlign: 'right', padding: '4px 0', color: 'var(--muted)', fontSize: 10 }}>Calls</th>
              </tr>
            </thead>
            <tbody>
              {entries.map(([name, v]) => {
                const spent = typeof v === 'object' ? (v.spent ?? 0) : v;
                const calls = typeof v === 'object' ? (v.calls ?? '—') : '—';
                return (
                  <tr key={name} style={{ borderBottom: '1px solid rgba(255,255,255,.03)' }}>
                    <td style={{ padding: '5px 0', maxWidth: 140, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{name}</td>
                    <td style={{ padding: '5px 0', textAlign: 'right', color: 'var(--cyan)', fontWeight: 600 }}>${spent.toFixed(3)}</td>
                    <td style={{ padding: '5px 0', textAlign: 'right', color: 'var(--muted)' }}>{calls}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
      }
    </div>
  );
}
