export default function RD({ data }) {
  const { experiments = [], backlog = [] } = data;
  const benchmarks   = data.benchmarks   || {};
  const evaluations  = benchmarks.evaluations || [];
  const lastRun      = benchmarks.last_run;

  return (
    <div className="fade-in" style={{ display: 'grid', gap: 14 }}>
      {/* Experiments */}
      <div className="card">
        <div className="section-title">Nova Experiments ({experiments.length})</div>
        {experiments.length === 0
          ? <div style={{ color: 'var(--muted)', fontSize: 11 }}>No experiments yet.</div>
          : <table style={{ width: '100%', fontSize: 11, borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  {['ID','Title','Status','Started','Result'].map(h => (
                    <th key={h} style={{ textAlign:'left', padding:'4px 8px', fontSize:10, color:'var(--muted)', fontWeight:600, textTransform:'uppercase' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {experiments.map((e, i) => {
                  const st  = (e.status || '').toLowerCase();
                  const col = st === 'complete' ? 'var(--green)' : st === 'running' ? 'var(--cyan)' : st === 'failed' ? 'var(--red)' : 'var(--muted)';
                  return (
                    <tr key={e.id || i} style={{ borderBottom: '1px solid rgba(255,255,255,.03)' }}>
                      <td style={{ padding:'6px 8px', color:'var(--cyan)', fontFamily:'monospace' }}>{e.id || '—'}</td>
                      <td style={{ padding:'6px 8px', maxWidth:200 }}>
                        <div style={{ overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{e.title || e.hypothesis || '—'}</div>
                      </td>
                      <td style={{ padding:'6px 8px' }}>
                        <span className="badge" style={{ color:col, background:`${col}22`, border:`1px solid ${col}44` }}>{e.status || '—'}</span>
                      </td>
                      <td style={{ padding:'6px 8px', color:'var(--muted)' }}>{e.started_at ? new Date(e.started_at).toLocaleDateString() : '—'}</td>
                      <td style={{ padding:'6px 8px', color:'var(--muted)', maxWidth:200 }}>
                        <div style={{ overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{e.result || e.outcome || '—'}</div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
        }
      </div>

      {/* Improvement Backlog */}
      <div className="card">
        <div className="section-title">Evolve Backlog ({backlog.length})</div>
        {backlog.length === 0
          ? <div style={{ color: 'var(--muted)', fontSize: 11 }}>No items yet.</div>
          : backlog.slice(0, 20).map((item, i) => {
              const pri = (item.priority || '').toUpperCase();
              const priNorm = pri === 'HIGH' ? 'P1' : pri === 'MEDIUM' ? 'P2' : pri === 'LOW' ? 'P3' : pri;
              return (
                <div key={item.id || i} style={{ display:'flex', alignItems:'center', gap:10, padding:'6px 0', borderBottom:'1px solid rgba(255,255,255,.03)' }}>
                  {priNorm && <span className={priNorm === 'P1' ? 'p1' : priNorm === 'P2' ? 'p2' : 'p3'}>{priNorm}</span>}
                  <span style={{ flex:1, fontSize:11, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{item.title || item.description || '—'}</span>
                  <span style={{ fontSize:10, color:'var(--muted)' }}>{item.category || item.type || ''}</span>
                  {item.status === 'done' && <span style={{ fontSize:10, color:'var(--green)' }}>✓</span>}
                </div>
              );
            })
        }
      </div>

      {/* Model Benchmarks */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 10 }}>
          <span className="section-title" style={{ marginBottom: 0 }}>Model Benchmarks</span>
          {lastRun && <span style={{ fontSize: 10, color: 'var(--muted)', marginLeft: 'auto' }}>Last run: {new Date(lastRun).toLocaleDateString()}</span>}
        </div>
        {evaluations.length === 0
          ? <div style={{ color: 'var(--muted)', fontSize: 11 }}>No benchmark runs yet.</div>
          : <table style={{ width:'100%', fontSize:11, borderCollapse:'collapse' }}>
              <thead>
                <tr style={{ borderBottom:'1px solid var(--border)' }}>
                  {['Model','Score','Latency','Notes'].map(h => (
                    <th key={h} style={{ textAlign:'left', padding:'4px 8px', fontSize:10, color:'var(--muted)', fontWeight:600 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {evaluations.map((ev, i) => (
                  <tr key={i} style={{ borderBottom:'1px solid rgba(255,255,255,.03)' }}>
                    <td style={{ padding:'6px 8px', fontFamily:'monospace', fontSize:10 }}>{ev.model || '—'}</td>
                    <td style={{ padding:'6px 8px', color:'var(--amber)' }}>⭐{(ev.score ?? 0).toFixed(2)}</td>
                    <td style={{ padding:'6px 8px', color:'var(--muted)' }}>{ev.latency_ms ? `${ev.latency_ms}ms` : '—'}</td>
                    <td style={{ padding:'6px 8px', color:'var(--muted)', fontSize:10 }}>{ev.notes || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
        }
      </div>
    </div>
  );
}
