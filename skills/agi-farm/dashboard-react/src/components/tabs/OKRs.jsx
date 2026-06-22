import LastUpdated from '../LastUpdated';

export default function OKRs({ data, lastUpdated }) {
  const okrs = data.okrs || {};
  const objectives = okrs.objectives || okrs.okrs || [];

  return (
    <div className="fade-in" style={{ display: 'grid', gap: 14 }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 2 }}>
        <span style={{ fontSize: 10, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '.08em' }}>
          {okrs.quarter || 'OKRs'}
        </span>
        <LastUpdated ts={lastUpdated} />
      </div>

      {objectives.length === 0 && (
        <div className="card" style={{ color: 'var(--muted)', fontSize: 13 }}>
          No OKRs defined yet. Add objectives to <code>OKRs.json</code> in your workspace.
        </div>
      )}

      {objectives.map((obj, i) => (
        <div key={obj.id || i} className="card">
          <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 14, color: 'var(--cyan)' }}>
            {obj.objective || obj.title || `Objective ${i + 1}`}
          </div>

          {(obj.key_results || obj.krs || []).map((kr, j) => {
            const current = kr.current ?? 0;
            const target  = kr.target  ?? 100;
            const pct     = target > 0 ? Math.min(100, (current / target) * 100) : 0;
            const unit    = kr.unit ? ` ${kr.unit}` : '';
            return (
              <div key={kr.id || j} style={{
                marginBottom: 14, paddingLeft: 12,
                borderLeft: '2px solid rgba(0,229,255,.2)',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
                  <span style={{ fontSize: 12, flex: 1, paddingRight: 12 }}>
                    {kr.result || kr.title || kr.description || `KR ${j + 1}`}
                  </span>
                  <span style={{ fontSize: 11, fontWeight: 600, whiteSpace: 'nowrap',
                    color: pct >= 100 ? 'var(--green)' : 'var(--amber)' }}>
                    {current} / {target}{unit}
                  </span>
                </div>
                <div className="progress-track">
                  <div className="progress-fill" style={{
                    width: `${pct}%`,
                    background: pct >= 100 ? 'var(--green)' : pct >= 70 ? 'var(--cyan)' : pct >= 40 ? 'var(--amber)' : 'var(--red)',
                  }} />
                </div>
                <div style={{ fontSize: 10, color: 'var(--muted)', marginTop: 3 }}>{pct.toFixed(0)}%</div>
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
}
