import { useState, useMemo, useCallback } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid, ReferenceLine, Legend,
} from 'recharts';
import LastUpdated from '../LastUpdated';

const STATUS_COLOR = { active:'var(--cyan)', complete:'var(--green)', paused:'var(--amber)', archived:'var(--muted)', pending:'var(--muted)' };
const RISK_COLOR   = { critical:'var(--red)', high:'var(--red)', medium:'var(--amber)', low:'var(--muted)' };
const RISK_ICON    = { blocked:'🚫', hitl_pending:'🚨', overdue:'⏰', agent_error:'🔴', sla_breach:'💥' };
const ACT_ICON     = { task_complete:'✅', task_failed:'❌', decision:'🧠', risk:'⚠️', milestone:'🏁' };
const HEALTH_COLOR = { green:'var(--green)', amber:'var(--amber)', red:'var(--red)' };

function relTime(iso) {
  if (!iso) return '—';
  try {
    const diff = Math.round((Date.now() - new Date(iso)) / 60000);
    if (diff < 1) return 'just now';
    if (diff < 60) return `${diff}m ago`;
    if (diff < 1440) return `${Math.round(diff/60)}h ago`;
    return `${Math.round(diff/1440)}d ago`;
  } catch { return iso; }
}

function dueLabel(iso, done) {
  if (!iso) return null;
  try {
    const diff = Math.ceil((new Date(iso) - Date.now()) / 86400000);
    if (done) return { label: new Date(iso).toLocaleDateString(), color:'var(--muted)' };
    if (diff < 0)  return { label:`${Math.abs(diff)}d overdue`, color:'var(--red)' };
    if (diff === 0) return { label:'due today', color:'var(--amber)' };
    if (diff === 1) return { label:'due tomorrow', color:'var(--amber)' };
    return { label:`in ${diff}d`, color:'var(--muted)' };
  } catch { return { label:iso, color:'var(--muted)' }; }
}

function healthScore(p) {
  const risks = (p._risks||[]).filter(r=>!r.resolved);
  const pct   = p._progress_pct ?? 0;
  const due   = p.target_completion ? Math.ceil((new Date(p.target_completion)-Date.now())/86400000) : 999;
  const tc    = p._task_counts||{};
  if (risks.some(r=>r.severity==='critical') || (tc.blocked||0)>2 || due < -3) return 'red';
  if (risks.length>1 || (tc.hitl||0)>0 || due < 0 || pct < 30) return 'amber';
  return 'green';
}

function exportMarkdown(p, agents) {
  const tc = p._task_counts||{};
  const lines = [
    `# ${p.name}`,
    `**Status**: ${p.status} | **Progress**: ${p._progress_pct??0}% | **Health**: ${healthScore(p).toUpperCase()}`,
    `**Owner**: ${agents.find(a=>a.id===p.owner)?.name||p.owner}`,
    p.target_completion ? `**Target**: ${new Date(p.target_completion).toLocaleDateString()}` : '',
    `**Tasks**: ${tc.done||0}/${tc.total||0} done`, '',
    `## Description`, p.description||'—', '',
    `## Milestones`,
    ...(p.milestones||[]).map(ms=>`- [${ms.status==='complete'?'x':' '}] **${ms.title}** (${ms.status})`),
    '', `## Risks`,
    ...(p._risks||[]).filter(r=>!r.resolved).map(r=>`- 🚨 [${r.severity}] ${r.description}`),
    '', `## Decisions`,
    ...(p.decisions||[]).map(d=>`- 🧠 **${d.decision}**`),
    '', `_Exported ${new Date().toLocaleString()}_`,
  ];
  const blob = new Blob([lines.join('\n')], {type:'text/markdown'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href=url; a.download=`${p.id}.md`; a.click();
  URL.revokeObjectURL(url);
}

function Badge({ label, color, size=10 }) {
  return <span style={{ fontSize:size, padding:'2px 7px', borderRadius:3, fontWeight:600, textTransform:'uppercase', letterSpacing:'.04em', color, background:`${color}18`, border:`1px solid ${color}44` }}>{label}</span>;
}

function ProgressRing({ pct, size=56, color='var(--cyan)' }) {
  const r=( size-8)/2, circ=2*Math.PI*r, dash=circ*(pct/100);
  return (
    <svg width={size} height={size} style={{ transform:'rotate(-90deg)', flexShrink:0 }}>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(255,255,255,.06)" strokeWidth={6}/>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={6} strokeDasharray={`${dash} ${circ}`} strokeLinecap="round" style={{ transition:'stroke-dasharray .4s ease' }}/>
      <text x={size/2} y={size/2} textAnchor="middle" dominantBaseline="middle" style={{ fontSize:11, fontWeight:700, fill:color, transform:'rotate(90deg)', transformOrigin:`${size/2}px ${size/2}px` }}>{pct}%</text>
    </svg>
  );
}

function AgentChip({ agentId, agents, isOwner }) {
  const a = agents.find(ag=>ag.id===agentId);
  return <span style={{ display:'inline-flex', alignItems:'center', gap:4, fontSize:10, padding:'2px 7px', borderRadius:3, background:isOwner?'rgba(0,229,255,.12)':'rgba(255,255,255,.04)', border:`1px solid ${isOwner?'rgba(0,229,255,.4)':'var(--border)'}`, color:isOwner?'var(--cyan)':'var(--text)' }}>{a?.emoji||'🤖'} {a?.name||agentId}{isOwner?' 👑':''}</span>;
}

function HealthDot({ health }) {
  return <span title={`Health: ${health}`} style={{ display:'inline-block', width:10, height:10, borderRadius:'50%', background:HEALTH_COLOR[health], flexShrink:0, boxShadow:`0 0 6px ${HEALTH_COLOR[health]}` }}/>;
}

function DeadlineBadge({ iso }) {
  const d = dueLabel(iso, false);
  if (!d) return null;
  return <span style={{ fontSize:10, color:d.color, fontWeight:600 }}>⏱ {d.label}</span>;
}

function GanttChart({ project: p }) {
  const milestones = p.milestones||[];
  if (!milestones.length) return <div style={{ fontSize:11, color:'var(--muted)' }}>No milestones to display.</div>;
  const start = new Date(p.created_at||Date.now());
  const end   = new Date(p.target_completion||Date.now()+30*86400000);
  const total = Math.max(1, end - start);
  const nowPct = Math.max(0, Math.min(100, ((Date.now()-start)/total)*100));
  const STATUS_C = { complete:'var(--green)', 'in-progress':'var(--cyan)', pending:'rgba(255,255,255,.15)', blocked:'var(--red)' };
  return (
    <div style={{ position:'relative', paddingTop:8 }}>
      <div style={{ display:'flex', justifyContent:'space-between', fontSize:9, color:'var(--muted)', marginBottom:6 }}>
        <span>{start.toLocaleDateString()}</span>
        <span style={{ color:'var(--amber)' }}>TODAY</span>
        <span>{end.toLocaleDateString()}</span>
      </div>
      <div style={{ position:'relative', background:'rgba(255,255,255,.03)', borderRadius:4, padding:'4px 0' }}>
        <div style={{ position:'absolute', left:`${nowPct}%`, top:0, bottom:0, width:1, background:'var(--amber)', opacity:.7, zIndex:2 }}/>
        {milestones.map(ms => {
          const msDue   = ms.due ? new Date(ms.due) : end;
          const widthPct = Math.max(2, Math.min(100, ((msDue-start)/total)*100));
          return (
            <div key={ms.id} style={{ display:'flex', alignItems:'center', gap:8, marginBottom:6, paddingRight:8 }}>
              <div style={{ fontSize:10, color:'var(--muted)', width:140, flexShrink:0, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }} title={ms.title}>{ms.title}</div>
              <div style={{ flex:1, position:'relative', height:16, background:'rgba(255,255,255,.03)', borderRadius:3 }}>
                <div style={{ position:'absolute', left:0, width:`${widthPct}%`, height:'100%', borderRadius:3, background:STATUS_C[ms.status]||'rgba(255,255,255,.15)', opacity:ms.status==='complete'?.6:1, transition:'width .4s ease' }}/>
                {ms.status==='complete' && <span style={{ position:'absolute', right:4, top:1, fontSize:9, color:'var(--green)' }}>✓</span>}
              </div>
              <div style={{ fontSize:9, color:'var(--muted)', width:40, flexShrink:0, textAlign:'right' }}>{ms.due?new Date(ms.due).toLocaleDateString('en',{month:'short',day:'numeric'}):'—'}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function BurndownChart({ project: p, tasks }) {
  const projTasks = tasks.filter(t=>(p.task_ids||[]).includes(t.id));
  const total = projTasks.length;
  if (!total) return <div style={{ fontSize:11, color:'var(--muted)' }}>No tasks linked yet.</div>;
  const start = new Date(p.created_at||Date.now());
  const end   = new Date(p.target_completion||Date.now()+7*86400000);
  const days  = Math.max(1, Math.ceil((end-start)/86400000));
  const completions = projTasks.filter(t=>t.completed_at).map(t=>Math.max(0,Math.ceil((new Date(t.completed_at)-start)/86400000))).sort((a,b)=>a-b);
  const todayDay = Math.ceil((Date.now()-start)/86400000);
  const data = Array.from({length:days+1},(_,i)=>({
    day: i,
    ideal: Math.round(total-(total/days)*i),
    actual: i<=todayDay ? total-completions.filter(c=>c<=i).length : undefined,
  }));
  return (
    <ResponsiveContainer width="100%" height={180}>
      <LineChart data={data} margin={{ top:4, right:12, left:0, bottom:4 }}>
        <CartesianGrid stroke="rgba(255,255,255,.04)"/>
        <XAxis dataKey="day" tick={{ fontSize:9, fill:'var(--muted)' }}/>
        <YAxis tick={{ fontSize:9, fill:'var(--muted)' }}/>
        <Tooltip contentStyle={{ background:'var(--bg2)', border:'1px solid var(--border)', fontSize:11 }}/>
        <Legend wrapperStyle={{ fontSize:10 }}/>
        <Line type="monotone" dataKey="ideal" stroke="rgba(255,255,255,.2)" strokeDasharray="4 2" dot={false} name="Ideal"/>
        <Line type="monotone" dataKey="actual" stroke="var(--cyan)" strokeWidth={2} dot={false} name="Actual"/>
        <ReferenceLine x={todayDay} stroke="var(--amber)" strokeDasharray="3 3"/>
      </LineChart>
    </ResponsiveContainer>
  );
}

function BudgetChart({ project: p }) {
  const alloc = p.budget?.allocated_usd||0;
  const spent = p.budget?.spent_usd||0;
  const remaining = Math.max(0, alloc-spent);
  const pct = alloc ? Math.round((spent/alloc)*100) : 0;
  const data = [{ name:'Budget', Spent:spent, Remaining:remaining }];
  return (
    <div>
      <div style={{ fontSize:10, color:'var(--muted)', marginBottom:6 }}>
        ${spent.toFixed(2)} spent of ${alloc.toFixed(2)} ({pct}%)
        {pct>80 && <span style={{ color:'var(--red)', marginLeft:6 }}>⚠️ Near limit</span>}
      </div>
      <ResponsiveContainer width="100%" height={80}>
        <BarChart data={data} layout="vertical" margin={{ top:0, right:0, left:0, bottom:0 }}>
          <XAxis type="number" tick={{ fontSize:9, fill:'var(--muted)' }} domain={[0,alloc||1]}/>
          <YAxis type="category" dataKey="name" hide/>
          <Tooltip contentStyle={{ background:'var(--bg2)', border:'1px solid var(--border)', fontSize:11 }} formatter={v=>`$${v.toFixed(2)}`}/>
          <Bar dataKey="Spent" stackId="a" fill="var(--cyan)" radius={[3,0,0,3]}/>
          <Bar dataKey="Remaining" stackId="a" fill="rgba(255,255,255,.06)" radius={[0,3,3,0]}/>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function AgentWorkload({ project: p, tasks, agents }) {
  const projTasks = tasks.filter(t=>(p.task_ids||[]).includes(t.id));
  const data = (p.team||[]).map(aid => {
    const a = agents.find(ag=>ag.id===aid)||{};
    const ts = projTasks.filter(t=>t.assigned_to===aid);
    return { name:`${a.emoji||'🤖'} ${a.name||aid}`, Open:ts.filter(t=>!['complete','failed'].includes(t.status)).length, Done:ts.filter(t=>t.status==='complete').length, Blocked:ts.filter(t=>['blocked','needs_human_decision'].includes(t.status)).length };
  }).filter(d=>d.Open+d.Done+d.Blocked>0);
  if (!data.length) return <div style={{ fontSize:11, color:'var(--muted)' }}>No task assignments yet.</div>;
  return (
    <ResponsiveContainer width="100%" height={Math.max(80, data.length*40)}>
      <BarChart data={data} layout="vertical" margin={{ top:0, right:12, left:80, bottom:0 }}>
        <XAxis type="number" tick={{ fontSize:9, fill:'var(--muted)' }} allowDecimals={false}/>
        <YAxis type="category" dataKey="name" tick={{ fontSize:10, fill:'var(--text)' }} width={90}/>
        <Tooltip contentStyle={{ background:'var(--bg2)', border:'1px solid var(--border)', fontSize:11 }}/>
        <Legend wrapperStyle={{ fontSize:10 }}/>
        <Bar dataKey="Done" fill="var(--green)" stackId="a"/>
        <Bar dataKey="Open" fill="var(--cyan)" stackId="a"/>
        <Bar dataKey="Blocked" fill="var(--red)" stackId="a" radius={[0,3,3,0]}/>
      </BarChart>
    </ResponsiveContainer>
  );
}

function OKRLinks({ project: p, okrs }) {
  if (!okrs?.objectives?.length) return <div style={{ fontSize:11, color:'var(--muted)' }}>No OKRs loaded.</div>;
  const linked = okrs.objectives.filter(obj =>
    (p.okr_ids||[]).includes(obj.id) ||
    (p.tags||[]).some(t=>obj.objective.toLowerCase().includes(t.toLowerCase()))
  );
  if (!linked.length) return <div style={{ fontSize:11, color:'var(--muted)' }}>No OKR linkage — add <code>okr_ids</code> to PROJECTS.json.</div>;
  return (
    <div style={{ display:'grid', gap:8 }}>
      {linked.map(obj=>(
        <div key={obj.id} style={{ padding:'10px 12px', background:'var(--surface)', borderRadius:6, border:'1px solid var(--border)' }}>
          <div style={{ fontSize:11, fontWeight:600, marginBottom:6 }}>🎯 {obj.objective}</div>
          {(obj.key_results||[]).map(kr=>{
            const pct = kr.target ? Math.min(100, Math.round((kr.current/kr.target)*100)) : 0;
            const c = pct>=100?'var(--green)':pct>=50?'var(--cyan)':'var(--amber)';
            return (
              <div key={kr.id} style={{ marginBottom:6 }}>
                <div style={{ display:'flex', justifyContent:'space-between', marginBottom:3, fontSize:10 }}>
                  <span style={{ color:'var(--muted)' }}>{kr.result}</span>
                  <span style={{ color:c, fontWeight:600 }}>{kr.current}/{kr.target} {kr.unit}</span>
                </div>
                <div className="progress-track" style={{ height:4 }}><div className="progress-fill" style={{ width:`${pct}%`, background:c, height:4 }}/></div>
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
}

function MilestoneRow({ ms, agents }) {
  const due = dueLabel(ms.due, ms.status==='complete');
  const agent = agents.find(a=>a.id===ms.assigned_to);
  const icon = { complete:'✅', 'in-progress':'🔄', pending:'⏳', blocked:'🚫' }[ms.status]||'⏳';
  return (
    <div style={{ display:'flex', alignItems:'center', gap:10, padding:'8px 0', borderBottom:'1px solid rgba(255,255,255,.04)', opacity:ms.status==='complete'?.7:1 }}>
      <span style={{ fontSize:16, flexShrink:0 }}>{icon}</span>
      <div style={{ flex:1, minWidth:0 }}>
        <div style={{ fontSize:12, textDecoration:ms.status==='complete'?'line-through':'none', color:ms.status==='complete'?'var(--muted)':'var(--text)' }}>{ms.title}</div>
        <div style={{ fontSize:10, color:'var(--muted)', marginTop:2, display:'flex', gap:8 }}>
          {agent && <span>{agent.emoji} {agent.name}</span>}
          {(ms.task_ids||[]).length>0 && <span>{ms.task_ids.length} task{ms.task_ids.length>1?'s':''}</span>}
          {ms.auto_complete && <span style={{ color:'var(--cyan)' }}>⚡ auto</span>}
        </div>
      </div>
      {due && <span style={{ fontSize:10, color:due.color, flexShrink:0 }}>{due.label}</span>}
      <Badge label={ms.status} color={STATUS_COLOR[ms.status]||'var(--muted)'}/>
    </div>
  );
}

function RiskRow({ risk: r, agents }) {
  const color = RISK_COLOR[r.severity]||'var(--muted)';
  const agent = agents.find(a=>a.id===r.detected_by);
  return (
    <div style={{ display:'flex', gap:10, padding:'8px 10px', marginBottom:6, borderRadius:6, background:`${color}0d`, border:`1px solid ${color}33` }}>
      <span style={{ fontSize:16, flexShrink:0 }}>{RISK_ICON[r.type]||'⚠️'}</span>
      <div style={{ flex:1 }}>
        <div style={{ fontSize:12, color:'var(--text)', marginBottom:2 }}>{r.description}</div>
        <div style={{ fontSize:10, color:'var(--muted)', display:'flex', gap:10 }}>
          {agent && <span>{agent.emoji} {agent.name}</span>}
          <span>{relTime(r.detected_at)}</span>
        </div>
      </div>
      <Badge label={r.severity} color={color}/>
    </div>
  );
}

function ActivityItem({ item, agents }) {
  const agent = agents.find(a=>a.id===item.agent);
  return (
    <div style={{ display:'flex', gap:10, padding:'7px 0', borderBottom:'1px solid rgba(255,255,255,.03)' }}>
      <span style={{ fontSize:14, flexShrink:0 }}>{ACT_ICON[item.type]||'•'}</span>
      <div style={{ flex:1, minWidth:0 }}>
        <div style={{ fontSize:11, color:'var(--text)', lineHeight:1.4, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{item.text}</div>
        <div style={{ fontSize:10, color:'var(--muted)', marginTop:2 }}>{agent&&<span>{agent.emoji} {agent.name} · </span>}{relTime(item.ts)}</div>
      </div>
    </div>
  );
}

function SessionTrace({ sessions, agents }) {
  if (!sessions?.length) return <div style={{ fontSize:11, color:'var(--muted)' }}>No sessions recorded yet.</div>;
  return (
    <table style={{ width:'100%', fontSize:11, borderCollapse:'collapse' }}>
      <thead><tr style={{ borderBottom:'1px solid var(--border)' }}>{['Task','Agent','Proc ID','Status','Completed'].map(h=><th key={h} style={{ textAlign:'left', padding:'4px 8px', fontSize:10, color:'var(--muted)', fontWeight:600 }}>{h}</th>)}</tr></thead>
      <tbody>
        {sessions.map((s,i)=>{
          const agent = agents.find(a=>a.id===s.assigned_to);
          const st = (s.status||'').toLowerCase().replace(/ /g,'-');
          const cls = { complete:'badge-complete', failed:'badge-failed', 'in-progress':'badge-in-progress' }[st]||'badge-pending';
          return <tr key={i} style={{ borderBottom:'1px solid rgba(255,255,255,.03)' }}><td style={{ padding:'5px 8px', color:'var(--cyan)', fontFamily:'monospace', fontSize:10 }}>{s.task_id}</td><td style={{ padding:'5px 8px' }}>{agent?`${agent.emoji} ${agent.name}`:s.assigned_to}</td><td style={{ padding:'5px 8px', color:'var(--muted)', fontFamily:'monospace', fontSize:10 }}>{s.proc_id||'—'}</td><td style={{ padding:'5px 8px' }}><span className={`badge ${cls}`}>{s.status}</span></td><td style={{ padding:'5px 8px', color:'var(--muted)' }}>{s.completed_at?relTime(s.completed_at):'—'}</td></tr>;
        })}
      </tbody>
    </table>
  );
}

function ProjectTaskBoard({ tasks, projectTaskIds, agents }) {
  const [expanded, setExpanded] = useState(null);
  const projTasks = tasks.filter(t=>projectTaskIds.includes(t.id));
  const cols = [
    { key:'pending', label:'Pending', color:'var(--muted)' },
    { key:'in-progress', label:'In Progress', color:'var(--cyan)' },
    { key:'needs_human_decision', label:'🚨 HITL', color:'var(--purple)' },
    { key:'blocked', label:'Blocked', color:'var(--red)' },
    { key:'complete', label:'Complete', color:'var(--green)' },
    { key:'failed', label:'Failed', color:'var(--red)' },
  ];
  if (!projTasks.length) return <div style={{ fontSize:11, color:'var(--muted)' }}>No tasks linked yet.</div>;
  return (
    <div style={{ display:'grid', gap:12 }}>
      {cols.map(col=>{
        const colTasks = projTasks.filter(t=>t.status===col.key);
        if (!colTasks.length) return null;
        return (
          <div key={col.key}>
            <div style={{ fontSize:10, fontWeight:600, color:col.color, textTransform:'uppercase', letterSpacing:'.06em', marginBottom:6 }}>{col.label} ({colTasks.length})</div>
            {colTasks.map(t=>{
              const isExp = expanded===t.id;
              const agent = agents.find(a=>a.id===t.assigned_to);
              const pri = (t.sla?.priority||t.priority||'').toUpperCase();
              return (
                <div key={t.id} onClick={()=>setExpanded(isExp?null:t.id)} style={{ marginBottom:6, padding:'8px 10px', background:'var(--surface)', border:`1px solid ${isExp?'rgba(0,229,255,.3)':'var(--border)'}`, borderRadius:6, cursor:'pointer' }}>
                  <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                    <span style={{ fontSize:10, color:'var(--muted)', fontFamily:'monospace', minWidth:50 }}>{t.id}</span>
                    <span style={{ flex:1, fontSize:11, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{t.title}</span>
                    {pri&&<span className={pri==='P1'?'p1':pri==='P2'?'p2':'p3'}>{pri}</span>}
                    {agent&&<span style={{ fontSize:11 }}>{agent.emoji}</span>}
                    <span style={{ fontSize:10, color:'var(--muted)' }}>{isExp?'▲':'▼'}</span>
                  </div>
                  {isExp&&(
                    <div style={{ marginTop:10, display:'grid', gap:8 }}>
                      {t.hitl_reason&&<div style={{ padding:'6px 10px', background:'rgba(224,64,251,.08)', border:'1px solid rgba(224,64,251,.25)', borderRadius:5, fontSize:11, color:'var(--purple)' }}>🚨 {t.hitl_reason}</div>}
                      {t.description&&<div style={{ fontSize:11, color:'var(--muted)', lineHeight:1.5 }}>{t.description}</div>}
                      {t.output&&<div style={{ fontSize:11, color:'var(--text)', lineHeight:1.5, padding:'6px 10px', background:'rgba(0,230,118,.04)', border:'1px solid rgba(0,230,118,.15)', borderRadius:5 }}>✅ {t.output}</div>}
                      <div style={{ display:'flex', gap:16, fontSize:10, color:'var(--muted)', flexWrap:'wrap' }}>
                        {t.proc_id&&<span>Proc: <span style={{ color:'var(--cyan)' }}>{t.proc_id}</span></span>}
                        {t.completed_at&&<span>Done: {new Date(t.completed_at).toLocaleString()}</span>}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}

function ProjectCard({ project: p, agents, selected, onClick }) {
  const tc = p._task_counts||{}, mc = p._milestone_counts||{}, pct = p._progress_pct??0;
  const risks = (p._risks||[]).filter(r=>!r.resolved);
  const health = healthScore(p);
  return (
    <div onClick={onClick} className="card" style={{ cursor:'pointer', transition:'all .15s', borderColor:selected?'rgba(0,229,255,.6)':risks.length?'rgba(255,23,68,.3)':'var(--border)', boxShadow:selected?'0 0 0 1px rgba(0,229,255,.2), var(--shadow)':'none' }}>
      <div style={{ display:'flex', alignItems:'flex-start', gap:10, marginBottom:10 }}>
        <ProgressRing pct={pct} color={pct===100?'var(--green)':risks.length?'var(--red)':'var(--cyan)'}/>
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ display:'flex', alignItems:'center', gap:6, marginBottom:4, flexWrap:'wrap' }}>
            <HealthDot health={health}/>
            <span style={{ fontWeight:700, fontSize:13 }}>{p.name}</span>
            <Badge label={p.status} color={STATUS_COLOR[p.status]||'var(--muted)'}/>
          </div>
          <div style={{ fontSize:10, color:'var(--muted)', fontFamily:'monospace' }}>{p.id}</div>
        </div>
      </div>
      <div style={{ fontSize:11, color:'var(--muted)', lineHeight:1.5, marginBottom:10, overflow:'hidden', display:'-webkit-box', WebkitLineClamp:2, WebkitBoxOrient:'vertical' }}>{p.description}</div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:6, marginBottom:10 }}>
        {[['Tasks',`${tc.done||0}/${tc.total||0}`,'var(--cyan)'],['Milestones',`${mc.done||0}/${mc.total||0}`,'var(--green)'],['Quality',p._quality_score?`⭐${p._quality_score}`:'—','var(--amber)'],['Vel/day',p._velocity??'—','var(--muted)']].map(([l,v,c])=>(
          <div key={l} style={{ textAlign:'center', padding:'5px 4px', background:'var(--surface)', borderRadius:4 }}>
            <div style={{ fontSize:9, color:'var(--muted)', marginBottom:2 }}>{l}</div>
            <div style={{ fontSize:12, fontWeight:700, color:c }}>{v}</div>
          </div>
        ))}
      </div>
      {risks.length>0&&<div style={{ fontSize:10, color:'var(--red)', marginBottom:8, padding:'4px 8px', background:'rgba(255,23,68,.07)', borderRadius:4, border:'1px solid rgba(255,23,68,.2)' }}>🚨 {risks.length} risk{risks.length>1?'s':''}: {risks[0].description.slice(0,60)}{risks[0].description.length>60?'…':''}</div>}
      <div style={{ display:'flex', alignItems:'center', gap:6, flexWrap:'wrap' }}>
        <AgentChip agentId={p.owner} agents={agents} isOwner/>
        {(p.tags||[]).slice(0,2).map(t=><span key={t} style={{ fontSize:9, padding:'1px 5px', borderRadius:3, background:'rgba(0,229,255,.06)', color:'var(--cyan)', border:'1px solid rgba(0,229,255,.15)' }}>{t}</span>)}
        <span style={{ marginLeft:'auto', display:'flex', gap:8, alignItems:'center' }}>
          <DeadlineBadge iso={p.target_completion}/>
          {p._last_activity&&<span style={{ fontSize:9, color:'var(--muted)' }}>↺ {relTime(p._last_activity)}</span>}
        </span>
      </div>
    </div>
  );
}

const SECTIONS = ['Overview','Milestones','Gantt','Tasks','Burndown','Risks','Team','Workload','Budget','OKRs','Activity','Sessions','Decisions'];

function ProjectDetail({ project: p, agents, tasks, okrs, onClose }) {
  const [section, setSection] = useState('Overview');
  const tc = p._task_counts||{}, mc = p._milestone_counts||{}, pct = p._progress_pct??0;
  const risks = (p._risks||[]).filter(r=>!r.resolved);
  const health = healthScore(p);
  return (
    <div style={{ background:'var(--bg2)', border:'1px solid rgba(0,229,255,.25)', borderRadius:10, overflow:'hidden', marginBottom:4 }}>
      <div style={{ padding:'16px 20px', background:'var(--bg3)', borderBottom:'1px solid var(--border)', display:'flex', alignItems:'flex-start', gap:16 }}>
        <ProgressRing pct={pct} size={70} color={pct===100?'var(--green)':risks.length?'var(--red)':'var(--cyan)'}/>
        <div style={{ flex:1 }}>
          <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:6, flexWrap:'wrap' }}>
            <HealthDot health={health}/>
            <span style={{ fontSize:18, fontWeight:700 }}>{p.name}</span>
            <Badge label={p.status} color={STATUS_COLOR[p.status]||'var(--muted)'} size={11}/>
            {p.priority_weight&&<Badge label={`P${p.priority_weight}`} color="var(--amber)" size={10}/>}
            {risks.length>0&&<Badge label={`${risks.length} risk${risks.length>1?'s':''}`} color="var(--red)" size={10}/>}
            <Badge label={`${health} health`} color={HEALTH_COLOR[health]} size={10}/>
          </div>
          <div style={{ fontSize:12, color:'var(--muted)', lineHeight:1.5, marginBottom:8 }}>{p.description}</div>
          <div style={{ display:'flex', gap:16, fontSize:10, color:'var(--muted)', flexWrap:'wrap', alignItems:'center' }}>
            <span>Owner: <AgentChip agentId={p.owner} agents={agents} isOwner/></span>
            {p.target_completion&&<DeadlineBadge iso={p.target_completion}/>}
            {p.created_at&&<span>Created: {new Date(p.created_at).toLocaleDateString()}</span>}
            {(p.tags||[]).map(t=><span key={t} style={{ padding:'1px 5px', borderRadius:3, background:'rgba(0,229,255,.06)', color:'var(--cyan)', border:'1px solid rgba(0,229,255,.15)' }}>{t}</span>)}
          </div>
        </div>
        <div style={{ display:'flex', gap:6, flexShrink:0 }}>
          <button onClick={()=>exportMarkdown(p,agents)} style={{ background:'none', border:'1px solid var(--border)', color:'var(--muted)', borderRadius:4, padding:'4px 10px', cursor:'pointer', fontSize:11, fontFamily:'inherit' }}>⬇ MD</button>
          <button onClick={onClose} style={{ background:'none', border:'1px solid var(--border)', color:'var(--muted)', borderRadius:4, padding:'4px 10px', cursor:'pointer', fontSize:11, fontFamily:'inherit' }}>✕</button>
        </div>
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(8,1fr)', borderBottom:'1px solid var(--border)', background:'var(--bg2)' }}>
        {[['Tasks Done',`${tc.done||0}/${tc.total||0}`,'var(--cyan)'],['In Progress',tc.active||0,'var(--amber)'],['Blocked',tc.blocked||0,tc.blocked?'var(--red)':'var(--muted)'],['HITL',tc.hitl||0,tc.hitl?'var(--purple)':'var(--muted)'],['Milestones',`${mc.done||0}/${mc.total||0}`,'var(--green)'],['Quality',p._quality_score?`⭐${p._quality_score}`:'—','var(--amber)'],['Vel/day',p._velocity??'—','var(--muted)'],['Budget',`$${p.budget?.spent_usd??0}/$${p.budget?.allocated_usd??0}`,'var(--cyan)']].map(([l,v,c])=>(
          <div key={l} style={{ textAlign:'center', padding:'10px 4px', borderRight:'1px solid var(--border)' }}>
            <div style={{ fontSize:9, color:'var(--muted)', marginBottom:3, textTransform:'uppercase', letterSpacing:'.04em' }}>{l}</div>
            <div style={{ fontSize:14, fontWeight:700, color:c }}>{v}</div>
          </div>
        ))}
      </div>
      <div style={{ display:'flex', borderBottom:'1px solid var(--border)', background:'var(--bg3)', overflowX:'auto', padding:'0 16px', gap:2 }}>
        {SECTIONS.map(s=>{
          const badge = s==='Risks'&&risks.length?risks.length:s==='Tasks'&&tc.total?tc.total:s==='Milestones'&&mc.total?mc.total:null;
          return <button key={s} onClick={()=>setSection(s)} style={{ background:'none', border:'none', cursor:'pointer', padding:'8px 12px', fontSize:11, fontFamily:'inherit', whiteSpace:'nowrap', fontWeight:section===s?600:400, color:section===s?'var(--cyan)':'var(--muted)', borderBottom:section===s?'2px solid var(--cyan)':'2px solid transparent' }}>{s}{badge?` (${badge})`:''}</button>;
        })}
      </div>
      <div style={{ padding:20 }}>
        {section==='Overview'&&(
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:20 }}>
            <div>
              <div className="section-title">Milestone Progress</div>
              <div className="progress-track" style={{ marginBottom:8 }}><div className="progress-fill" style={{ width:`${mc.total?Math.round((mc.done/mc.total)*100):0}%`, background:mc.done===mc.total&&mc.total>0?'var(--green)':'var(--cyan)' }}/></div>
              {(p.milestones||[]).slice(0,4).map(ms=><MilestoneRow key={ms.id} ms={ms} agents={agents}/>)}
            </div>
            <div>
              <div className="section-title">Recent Activity</div>
              {(p._activity||[]).slice(0,6).map((a,i)=><ActivityItem key={i} item={a} agents={agents}/>)}
              {(!p._activity||p._activity.length===0)&&<div style={{ fontSize:11, color:'var(--muted)' }}>No activity yet.</div>}
            </div>
            {risks.length>0&&<div style={{ gridColumn:'1/-1' }}><div className="section-title" style={{ color:'var(--red)' }}>🚨 Active Risks</div>{risks.slice(0,3).map(r=><RiskRow key={r.id} risk={r} agents={agents}/>)}</div>}
            {p.notes&&<div style={{ gridColumn:'1/-1', padding:'10px 14px', background:'rgba(0,229,255,.03)', border:'1px solid rgba(0,229,255,.12)', borderRadius:6 }}><div className="section-title">Notes</div><div style={{ fontSize:12, color:'var(--text)', lineHeight:1.6 }}>{p.notes}</div></div>}
          </div>
        )}
        {section==='Milestones'&&<div><div style={{ display:'flex', justifyContent:'space-between', marginBottom:12 }}><span style={{ fontSize:11, color:'var(--muted)' }}>{mc.done}/{mc.total} complete</span>{p.target_completion&&<DeadlineBadge iso={p.target_completion}/>}</div>{(p.milestones||[]).length===0?<div style={{ fontSize:11, color:'var(--muted)' }}>No milestones defined yet.</div>:(p.milestones||[]).map(ms=><MilestoneRow key={ms.id} ms={ms} agents={agents}/>)}</div>}
        {section==='Gantt'&&<div><div className="section-title" style={{ marginBottom:12 }}>Timeline — Milestones</div><GanttChart project={p}/></div>}
        {section==='Tasks'&&<ProjectTaskBoard tasks={tasks} projectTaskIds={p.task_ids||[]} agents={agents}/>}
        {section==='Burndown'&&<div><div className="section-title" style={{ marginBottom:12 }}>Task Burndown</div><BurndownChart project={p} tasks={tasks}/></div>}
        {section==='Risks'&&<div>{risks.length===0?<div style={{ fontSize:11, color:'var(--green)' }}>✅ No active risks.</div>:risks.map(r=><RiskRow key={r.id} risk={r} agents={agents}/>)}</div>}
        {section==='Team'&&(
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(200px,1fr))', gap:12 }}>
            {(p.team||[]).map(aid=>{
              const agent=agents.find(a=>a.id===aid); const isOwner=aid===p.owner;
              const dot={ active:'dot-active', available:'dot-available', busy:'dot-busy', error:'dot-error' }[agent?.status]||'dot-offline';
              return <div key={aid} className="card" style={{ borderColor:isOwner?'rgba(0,229,255,.4)':'var(--border)' }}><div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:8 }}><span style={{ fontSize:24 }}>{agent?.emoji||'🤖'}</span><div><div style={{ fontWeight:700, fontSize:13 }}>{agent?.name||aid}</div><div style={{ fontSize:10, color:'var(--muted)' }}>{agent?.role||''}</div></div>{isOwner&&<span style={{ marginLeft:'auto', fontSize:14 }}>👑</span>}</div><div style={{ display:'flex', alignItems:'center', gap:6, marginBottom:8 }}><span className={`dot ${dot}`}/><span style={{ fontSize:10, color:'var(--muted)' }}>{agent?.status||'unknown'}</span></div><div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:4, fontSize:10 }}><div style={{ textAlign:'center', background:'var(--surface)', padding:'4px', borderRadius:4 }}><div style={{ color:'var(--muted)' }}>Done</div><div style={{ fontWeight:700, color:'var(--cyan)' }}>{agent?.tasks_completed||0}</div></div><div style={{ textAlign:'center', background:'var(--surface)', padding:'4px', borderRadius:4 }}><div style={{ color:'var(--muted)' }}>Quality</div><div style={{ fontWeight:700, color:'var(--amber)' }}>⭐{(agent?.avg_quality||0).toFixed(1)}</div></div></div></div>;
            })}
          </div>
        )}
        {section==='Workload'&&<div><div className="section-title" style={{ marginBottom:12 }}>Agent Task Workload</div><AgentWorkload project={p} tasks={tasks} agents={agents}/></div>}
        {section==='Budget'&&<div><div className="section-title" style={{ marginBottom:12 }}>Budget</div><BudgetChart project={p}/></div>}
        {section==='OKRs'&&<div><div className="section-title" style={{ marginBottom:12 }}>OKR Linkage</div><OKRLinks project={p} okrs={okrs}/></div>}
        {section==='Activity'&&<div>{(p._activity||[]).length===0?<div style={{ fontSize:11, color:'var(--muted)' }}>No activity yet.</div>:(p._activity||[]).map((a,i)=><ActivityItem key={i} item={a} agents={agents}/>)}</div>}
        {section==='Sessions'&&<SessionTrace sessions={p._sessions} agents={agents}/>}
        {section==='Decisions'&&<div>{(p.decisions||[]).length===0?<div style={{ fontSize:11, color:'var(--muted)' }}>No decisions logged yet.</div>:(p.decisions||[]).map(d=>{ const agent=agents.find(a=>a.id===d.decided_by); return <div key={d.id} style={{ marginBottom:12, padding:'12px 14px', background:'var(--surface)', border:'1px solid var(--border)', borderRadius:6 }}><div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:6 }}><span style={{ fontSize:14 }}>🧠</span><span style={{ flex:1, fontWeight:600, fontSize:12 }}>{d.decision}</span><span style={{ fontSize:10, color:'var(--muted)' }}>{relTime(d.decided_at)}</span></div>{d.rationale&&<div style={{ fontSize:11, color:'var(--muted)', lineHeight:1.5, marginBottom:6 }}>{d.rationale}</div>}<div style={{ fontSize:10, color:'var(--muted)', display:'flex', gap:12 }}>{agent&&<span>{agent.emoji} {agent.name}</span>}{d.task_id&&<span>Task: <span style={{ color:'var(--cyan)' }}>{d.task_id}</span></span>}</div></div>; })}</div>}
      </div>
    </div>
  );
}

function FilterBar({ agents, filters, setFilters, sortKey, setSortKey, sortDir, setSortDir, total, visible }) {
  const s = { background:'var(--surface)', border:'1px solid var(--border)', color:'var(--text)', borderRadius:4, padding:'4px 10px', fontSize:11, fontFamily:'inherit' };
  return (
    <div style={{ display:'flex', gap:8, alignItems:'center', flexWrap:'wrap', marginBottom:12 }}>
      <input placeholder="🔍 Search…" value={filters.search} onChange={e=>setFilters(f=>({...f,search:e.target.value}))} style={{ ...s, flex:'1 1 140px', minWidth:100 }}/>
      <select value={filters.status} onChange={e=>setFilters(f=>({...f,status:e.target.value}))} style={s}><option value="">All statuses</option>{['active','complete','paused','archived','pending'].map(x=><option key={x} value={x}>{x}</option>)}</select>
      <select value={filters.health} onChange={e=>setFilters(f=>({...f,health:e.target.value}))} style={s}><option value="">All health</option><option value="green">🟢 Green</option><option value="amber">🟡 Amber</option><option value="red">🔴 Red</option></select>
      <select value={filters.owner} onChange={e=>setFilters(f=>({...f,owner:e.target.value}))} style={s}><option value="">All owners</option>{agents.map(a=><option key={a.id} value={a.id}>{a.emoji} {a.name}</option>)}</select>
      <select value={sortKey} onChange={e=>setSortKey(e.target.value)} style={s}><option value="priority_weight">Priority</option><option value="_progress_pct">Progress</option><option value="target_completion">Deadline</option><option value="health">Health</option><option value="_last_activity">Activity</option></select>
      <button onClick={()=>setSortDir(d=>d==='asc'?'desc':'asc')} style={{ ...s, cursor:'pointer', padding:'4px 8px' }}>{sortDir==='asc'?'↑':'↓'}</button>
      {(filters.search||filters.status||filters.health||filters.owner)&&<button onClick={()=>setFilters({search:'',status:'',health:'',owner:''})} style={{ ...s, cursor:'pointer', color:'var(--muted)' }}>✕ Clear</button>}
      <span style={{ fontSize:10, color:'var(--muted)', marginLeft:'auto' }}>{visible}/{total}</span>
    </div>
  );
}

export default function Projects({ data, lastUpdated }) {
  const { projects=[], agents=[], tasks=[], okrs } = data;
  const [selected, setSelected]   = useState(null);
  const [filters,  setFilters]    = useState({ search:'', status:'', health:'', owner:'' });
  const [sortKey,  setSortKey]    = useState('priority_weight');
  const [sortDir,  setSortDir]    = useState('desc');
  const [collapsed,setCollapsed]  = useState(false);

  const filtered = useMemo(()=>{
    let ps = [...projects];
    const { search, status, health, owner } = filters;
    if (search) ps = ps.filter(p=>[p.name,p.description||'',p.id].join(' ').toLowerCase().includes(search.toLowerCase()));
    if (status) ps = ps.filter(p=>p.status===status);
    if (health) ps = ps.filter(p=>healthScore(p)===health);
    if (owner)  ps = ps.filter(p=>p.owner===owner);
    const hR = { red:0, amber:1, green:2 };
    ps.sort((a,b)=>{
      let av, bv;
      if (sortKey==='health') { av=hR[healthScore(a)]; bv=hR[healthScore(b)]; }
      else if (sortKey==='target_completion') { av=a.target_completion?new Date(a.target_completion).getTime():9e15; bv=b.target_completion?new Date(b.target_completion).getTime():9e15; }
      else if (sortKey==='_last_activity') { av=a._last_activity?new Date(a._last_activity).getTime():0; bv=b._last_activity?new Date(b._last_activity).getTime():0; }
      else { av=a[sortKey]??0; bv=b[sortKey]??0; }
      return sortDir==='asc'?(av>bv?1:-1):(av<bv?1:-1);
    });
    return ps;
  }, [projects, filters, sortKey, sortDir]);

  const selProj = projects.find(p=>p.id===selected);
  const toggle  = useCallback(id=>setSelected(prev=>prev===id?null:id),[]);
  const active  = filtered.filter(p=>p.status==='active');
  const other   = filtered.filter(p=>p.status!=='active');
  const totalRisks = projects.reduce((n,p)=>n+(p._risks||[]).filter(r=>!r.resolved).length,0);
  const redCount   = projects.filter(p=>healthScore(p)==='red').length;
  const amberCount = projects.filter(p=>healthScore(p)==='amber').length;

  return (
    <div className="fade-in" style={{ display:'grid', gap:14 }}>
      <div style={{ display:'flex', alignItems:'center', gap:12, flexWrap:'wrap' }}>
        <div style={{ display:'flex', gap:10, fontSize:11, alignItems:'center' }}>
          <span style={{ color:'var(--muted)' }}>{projects.length} project{projects.length!==1?'s':''}</span>
          {redCount>0&&<Badge label={`🔴 ${redCount} critical`} color="var(--red)"/>}
          {amberCount>0&&<Badge label={`🟡 ${amberCount} at-risk`} color="var(--amber)"/>}
          {totalRisks>0&&<Badge label={`${totalRisks} risk${totalRisks>1?'s':''}`} color="var(--red)"/>}
        </div>
        <div style={{ marginLeft:'auto', display:'flex', gap:6 }}>
          <button onClick={()=>setCollapsed(c=>!c)} style={{ background:'none', border:'1px solid var(--border)', color:'var(--muted)', borderRadius:4, padding:'3px 9px', cursor:'pointer', fontSize:10, fontFamily:'inherit' }}>{collapsed?'⊞ Expand All':'⊟ Collapse All'}</button>
        </div>
        <LastUpdated ts={lastUpdated}/>
      </div>
      <FilterBar agents={agents} filters={filters} setFilters={setFilters} sortKey={sortKey} setSortKey={setSortKey} sortDir={sortDir} setSortDir={setSortDir} total={projects.length} visible={filtered.length}/>
      {selProj&&<ProjectDetail project={selProj} agents={agents} tasks={tasks} okrs={okrs} onClose={()=>setSelected(null)}/>}
      {!collapsed&&active.length>0&&<><div className="section-title">Active Projects</div><div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(340px,1fr))', gap:14 }}>{active.map(p=><ProjectCard key={p.id} project={p} agents={agents} selected={selected===p.id} onClick={()=>toggle(p.id)}/>)}</div></>}
      {!collapsed&&other.length>0&&<><div className="section-title" style={{ marginTop:8 }}>Other</div><div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(340px,1fr))', gap:14 }}>{other.map(p=><ProjectCard key={p.id} project={p} agents={agents} selected={selected===p.id} onClick={()=>toggle(p.id)}/>)}</div></>}
      {filtered.length===0&&<div className="card" style={{ color:'var(--muted)', fontSize:13 }}>{projects.length===0?'No projects yet. Cooper writes to PROJECTS.json during sprint planning.':'No projects match your filters.'}</div>}
    </div>
  );
}
