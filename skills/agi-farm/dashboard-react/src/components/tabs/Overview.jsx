import AgentMiniCard from '../AgentMiniCard';
import LastUpdated from '../LastUpdated';

export default function Overview({ data, lastUpdated }) {
  const {
    agents = [], tasks = [], task_counts: tc = {}, sla_at_risk = [],
    projects = [], budget = {}, knowledge_count = 0, memory_lines = 0, broadcast = '',
    crons = [], alerts = [], dispatcher = {},
  } = data;

  const errorCrons  = crons.filter(j => (j._consecutive_errors || 0) >= 3).length;
  const totalCrons  = crons.length;
  const critAlerts  = alerts.filter(a => a.severity === 'critical').length;
  const limits  = budget.limits  || {};
  const current = budget.current || {};
  const spent = current.daily_usd ?? 0;
  const limit = limits.daily_usd ?? 1;
  const threshold = (budget.alerts?.daily_threshold_pct ?? 70);

  const broadcastPreview = broadcast.split('\n').filter(l => l.trim()).slice(-3);

  return (
    <div className="fade-in" style={{ display: 'grid', gap: 14 }}>
      {/* Stats row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6,1fr)', gap: 10 }}>
        {[
          ['Pending',     tc.pending                 ?? 0, 'var(--amber)'],
          ['In Progress', tc['in-progress']           ?? 0, 'var(--cyan)'],
          ['Complete',    tc.complete                 ?? 0, 'var(--green)'],
          ['HITL 🚨',     tc.needs_human_decision     ?? 0, 'var(--purple)'],
          ['Knowledge',   knowledge_count,                  'var(--cyan)'],
          ['Memory',      `${memory_lines}L`,               'var(--muted)'],
        ].map(([l, v, c]) => (
          <div key={l} className="card" style={{ textAlign: 'center' }}>
            <div className="section-title">{l}</div>
            <div style={{ fontSize: 22, fontWeight: 700,
              color: l === 'HITL 🚨' && v > 0 ? 'var(--red)' : c }}>{v}</div>
          </div>
        ))}
      </div>

      {/* Critical alerts strip */}
      {critAlerts > 0 && (
        <div style={{ padding:'10px 14px', background:'rgba(255,23,68,.08)', border:'1px solid rgba(255,23,68,.35)',
          borderRadius:6, display:'flex', alignItems:'center', gap:10 }}>
          <span style={{ fontSize:16 }}>🚨</span>
          <span style={{ fontSize:12, color:'var(--red)', fontWeight:600 }}>{critAlerts} critical alert{critAlerts>1?'s':''} require attention</span>
          <span style={{ fontSize:11, color:'var(--muted)', marginLeft:'auto' }}>→ Alerts tab</span>
        </div>
      )}

      {/* Cron health + Dispatcher strip */}
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
        <div className="card" style={{ borderColor: errorCrons ? 'rgba(255,214,0,.3)' : 'var(--border)' }}>
          <div style={{ display:'flex', alignItems:'center', gap:8 }}>
            <span style={{ fontSize:16 }}>⚙️</span>
            <div>
              <div className="section-title" style={{ marginBottom:2 }}>Cron Health</div>
              <div style={{ fontSize:13, fontWeight:700, color: errorCrons ? 'var(--amber)' : 'var(--green)' }}>
                {errorCrons ? `${errorCrons}/${totalCrons} erroring` : `${totalCrons}/${totalCrons} healthy`}
              </div>
            </div>
          </div>
        </div>
        <div className="card">
          <div style={{ display:'flex', alignItems:'center', gap:8 }}>
            <span style={{ fontSize:16 }}>🤖</span>
            <div>
              <div className="section-title" style={{ marginBottom:2 }}>Dispatcher</div>
              <div style={{ fontSize:11, color:'var(--muted)' }}>
                Last: {dispatcher.last_run ? new Date(dispatcher.last_run).toLocaleTimeString() : '—'}
                {dispatcher.last_summary?.triggered?.length > 0 &&
                  <span style={{ color:'var(--cyan)', marginLeft:8 }}>↑ {dispatcher.last_summary.triggered.length} triggered</span>}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Budget bar */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: 6 }}>
          <span className="section-title" style={{ marginBottom: 0 }}>Daily Budget</span>
          <span style={{ fontSize: 11, color: 'var(--muted)', marginLeft: 8 }}>${spent.toFixed(2)} / ${limit}</span>
          <LastUpdated ts={lastUpdated} />
        </div>
        <div className="progress-track" style={{ position: 'relative' }}>
          <div className="progress-fill" style={{
            width: `${Math.min(100, (spent/limit)*100)}%`,
            background: spent/limit > threshold/100 ? 'var(--red)' : 'var(--cyan)',
          }} />
          <div style={{ position:'absolute', top:-2, bottom:-2, left:`${threshold}%`, width:1, background:'var(--amber)', opacity:0.5 }} />
        </div>
      </div>

      {/* SLA at risk — always show */}
      <div className="card" style={{ borderColor: sla_at_risk.length > 0 ? 'rgba(255,23,68,.4)' : 'var(--border)' }}>
        <div className="section-title" style={{ color: sla_at_risk.length > 0 ? 'var(--red)' : 'var(--muted)' }}>
          {sla_at_risk.length > 0 ? `⚠ SLA At Risk (${sla_at_risk.length})` : '✅ No SLA at risk'}
        </div>
        {sla_at_risk.map(t => (
          <div key={t.id} style={{ display:'flex', gap:10, padding:'4px 0', fontSize:11 }}>
            <span style={{ color:'var(--muted)', minWidth:60 }}>{t.id}</span>
            <span style={{ flex:1 }}>{t.title}</span>
            <span style={{ color:'var(--red)' }}>{t.sla?.deadline || ''}</span>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
        {/* Agent grid */}
        <div className="card">
          <div className="section-title">Agent Status</div>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(140px,1fr))', gap:8 }}>
            {agents.map(a => <AgentMiniCard key={a.id} agent={a} />)}
          </div>
        </div>

        {/* Recent tasks */}
        <div className="card">
          <div className="section-title">Recent Tasks</div>
          {tasks.slice(-10).reverse().map(t => <TaskRow key={t.id} task={t} />)}
          {tasks.length === 0 && <div style={{ color:'var(--muted)', fontSize:11 }}>No tasks yet</div>}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
        {/* Active projects */}
        <div className="card">
          <div className="section-title">Active Projects</div>
          {projects.filter(p => ['active','ACTIVE'].includes(p.status)).length === 0
            ? <div style={{ color:'var(--muted)', fontSize:11 }}>No active projects</div>
            : projects.filter(p => ['active','ACTIVE'].includes(p.status)).map(p => (
                <div key={p.id} style={{ padding:'8px 10px', marginBottom:8, background:'var(--surface)', borderRadius:6, border:'1px solid var(--border)' }}>
                  <div style={{ fontWeight:600, fontSize:12, marginBottom:3 }}>{p.name || p.id}</div>
                  <div style={{ color:'var(--muted)', fontSize:11 }}>{p.description || ''}</div>
                </div>
              ))
          }
        </div>

        {/* Broadcast preview */}
        <div className="card">
          <div className="section-title">Broadcast (last 3)</div>
          {broadcastPreview.length === 0
            ? <div style={{ color:'var(--muted)', fontSize:11 }}>No broadcasts yet</div>
            : broadcastPreview.map((line, i) => {
                const low = line.toLowerCase();
                let color = 'var(--text)';
                if (low.includes('[critical]') || low.includes('🔴')) color = 'var(--red)';
                else if (low.includes('[blocked]')) color = 'var(--amber)';
                else if (low.includes('[hitl]') || low.includes('🚨')) color = 'var(--purple)';
                else if (low.includes('[done]') || low.includes('✅')) color = 'var(--green)';
                return <div key={i} style={{ color, fontSize:11, padding:'3px 0', lineHeight:1.5, wordBreak:'break-word' }}>{line}</div>;
              })
          }
        </div>
      </div>
    </div>
  );
}

function TaskRow({ task: t }) {
  const pri = (t.sla?.priority || t.priority || '').toUpperCase();
  const s   = (t.status || '').toLowerCase().replace(/ /g,'-');
  const cls = {'complete':'badge-complete','pending':'badge-pending','in-progress':'badge-in-progress',
    'failed':'badge-failed','needs_human_decision':'badge-hitl','blocked':'badge-blocked'}[s] || 'badge-pending';
  return (
    <div style={{ display:'flex', alignItems:'center', gap:8, padding:'5px 0', borderBottom:'1px solid rgba(255,255,255,.04)' }}>
      <span style={{ color:'var(--muted)', fontSize:10, minWidth:50 }}>{t.id||'—'}</span>
      <span style={{ flex:1, fontSize:11, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{t.title||'—'}</span>
      {pri && <span className={pri==='P1'?'p1':pri==='P2'?'p2':'p3'}>{pri}</span>}
      <span className={`badge ${cls}`}>{t.status||'—'}</span>
    </div>
  );
}
