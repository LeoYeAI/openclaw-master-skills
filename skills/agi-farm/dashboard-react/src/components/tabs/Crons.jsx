import { useState } from 'react';
import LastUpdated from '../LastUpdated';

async function apiPost(path) {
  const r = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
  return r.json();
}

function fmtDuration(ms) {
  if (!ms) return '—';
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${Math.round(ms / 60000)}m ${Math.round((ms % 60000) / 1000)}s`;
}

function fmtNext(sec) {
  if (sec === null || sec === undefined) return '—';
  if (sec < 0) return 'overdue';
  if (sec < 60) return `${sec}s`;
  if (sec < 3600) return `${Math.round(sec / 60)}m`;
  return `${Math.round(sec / 3600)}h`;
}

function fmtLast(sec) {
  if (sec === null || sec === undefined) return '—';
  if (sec < 60) return `${sec}s ago`;
  if (sec < 3600) return `${Math.round(sec / 60)}m ago`;
  return `${Math.round(sec / 3600)}h ago`;
}

function StatusDot({ status, errors }) {
  if (errors >= 3) return <span className="dot dot-error" title={`${errors} consecutive errors`} />;
  if (status === 'error') return <span className="dot dot-error" />;
  if (status === 'running') return <span className="dot dot-active" />;
  if (status === 'ok') return <span className="dot dot-available" />;
  return <span className="dot dot-offline" />;
}

function CronRow({ job, agents, onTrigger, onToggle }) {
  const [triggering, setTriggering] = useState(false);
  const [toggling, setToggling] = useState(false);
  const [localEnabled, setLocalEnabled] = useState(job.enabled !== false);
  const agent = agents.find(a => a.id === job.agentId);
  const errors = job._consecutive_errors || 0;
  const isError = errors >= 3 || job._status === 'error';

  async function trigger() {
    setTriggering(true);
    await apiPost(`/api/cron/${job.id}/trigger`);
    onTrigger?.(job.id);
    setTimeout(() => setTriggering(false), 2000);
  }

  async function toggle() {
    setToggling(true);
    const res = await apiPost(`/api/cron/${job.id}/toggle`);
    if (res.ok) setLocalEnabled(res.enabled);
    setToggling(false);
    onToggle?.(job.id, res.enabled);
  }

  return (
    <>
      <tr style={{
        borderBottom: '1px solid rgba(255,255,255,.03)',
        background: isError ? 'rgba(255,23,68,.03)' : 'transparent',
        opacity: localEnabled ? 1 : 0.5,
      }}>
        <td style={{ padding: '8px 12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <StatusDot status={job._status} errors={errors} />
            <div>
              <div style={{ fontSize: 12, fontWeight: errors >= 3 ? 700 : 400,
                color: isError ? 'var(--red)' : 'var(--text)' }}>{job.name}</div>
              {job.description && <div style={{ fontSize: 10, color: 'var(--muted)' }}>{job.description.slice(0, 60)}</div>}
            </div>
          </div>
        </td>
        <td style={{ padding: '8px 12px', fontSize: 11 }}>
          {agent ? <span>{agent.emoji} {agent.name}</span> : <span style={{ color: 'var(--muted)' }}>{job.agentId}</span>}
        </td>
        <td style={{ padding: '8px 12px', fontSize: 10, color: 'var(--muted)', fontFamily: 'monospace' }}>
          {job.schedule?.kind === 'every'
            ? `every ${Math.round((job.schedule.everyMs || 0) / 60000)}m`
            : (job.schedule?.cronExpression || job.schedule?.kind || '—')}
        </td>
        <td style={{ padding: '8px 12px', fontSize: 11, color: fmtNext(job._next_run_sec) === 'overdue' ? 'var(--red)' : 'var(--muted)' }}>
          {fmtNext(job._next_run_sec)}
        </td>
        <td style={{ padding: '8px 12px', fontSize: 11, color: 'var(--muted)' }}>
          {fmtLast(job._last_run_sec)}
        </td>
        <td style={{ padding: '8px 12px', fontSize: 11, color: 'var(--muted)' }}>
          {fmtDuration(job._duration_ms)}
        </td>
        <td style={{ padding: '8px 12px' }}>
          {isError && (
            <span style={{ fontSize: 10, padding: '2px 6px', borderRadius: 3, fontWeight: 700,
              background: 'rgba(255,23,68,.15)', color: 'var(--red)', border: '1px solid rgba(255,23,68,.3)' }}>
              {errors}× err
            </span>
          )}
          {!isError && job._status === 'ok' && (
            <span style={{ fontSize: 10, padding: '2px 6px', borderRadius: 3,
              background: 'rgba(0,230,118,.1)', color: 'var(--green)', border: '1px solid rgba(0,230,118,.25)' }}>ok</span>
          )}
        </td>
        <td style={{ padding: '8px 12px' }}>
          <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <button onClick={trigger} disabled={triggering} title="Trigger now" style={{
              background: 'rgba(0,229,255,.1)', border: '1px solid rgba(0,229,255,.3)',
              color: 'var(--cyan)', padding: '3px 8px', borderRadius: 4,
              cursor: triggering ? 'not-allowed' : 'pointer', fontSize: 10, fontFamily: 'inherit',
            }}>{triggering ? '...' : '▶ Run'}</button>
            <button onClick={toggle} disabled={toggling} title={localEnabled ? 'Disable' : 'Enable'} style={{
              background: localEnabled ? 'rgba(255,214,0,.08)' : 'rgba(0,230,118,.08)',
              border: `1px solid ${localEnabled ? 'rgba(255,214,0,.3)' : 'rgba(0,230,118,.3)'}`,
              color: localEnabled ? 'var(--amber)' : 'var(--green)',
              padding: '3px 8px', borderRadius: 4, cursor: toggling ? 'not-allowed' : 'pointer',
              fontSize: 10, fontFamily: 'inherit',
            }}>{toggling ? '...' : localEnabled ? '⏸ Off' : '▶ On'}</button>
          </div>
        </td>
      </tr>
      {isError && job._last_error && (
        <tr style={{ background: 'rgba(255,23,68,.04)' }}>
          <td colSpan={8} style={{ padding: '4px 12px 8px 40px', fontSize: 10, color: 'var(--red)', fontFamily: 'monospace' }}>
            ↳ {job._last_error}
          </td>
        </tr>
      )}
    </>
  );
}

export default function Crons({ data, lastUpdated }) {
  const { crons = [], agents = [] } = data;
  const [filter, setFilter] = useState('all');

  const erroring  = crons.filter(j => (j._consecutive_errors || 0) >= 3 || j._status === 'error');
  const running   = crons.filter(j => j._status === 'running');
  const disabled  = crons.filter(j => j.enabled === false);

  const filtered = crons.filter(j => {
    if (filter === 'error')   return (j._consecutive_errors || 0) >= 3 || j._status === 'error';
    if (filter === 'running') return j._status === 'running';
    if (filter === 'disabled') return j.enabled === false;
    return true;
  });

  // Group by agent
  const byAgent = {};
  filtered.forEach(j => {
    const a = j.agentId || 'unknown';
    if (!byAgent[a]) byAgent[a] = [];
    byAgent[a].push(j);
  });

  return (
    <div className="fade-in" style={{ display: 'grid', gap: 14 }}>
      {/* Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10 }}>
        {[
          ['Total', crons.length, 'var(--muted)'],
          ['Erroring', erroring.length, erroring.length ? 'var(--red)' : 'var(--muted)'],
          ['Running', running.length, running.length ? 'var(--cyan)' : 'var(--muted)'],
          ['Disabled', disabled.length, disabled.length ? 'var(--amber)' : 'var(--muted)'],
        ].map(([l, v, c]) => (
          <div key={l} className="card" style={{ textAlign: 'center', cursor: 'pointer' }}
            onClick={() => setFilter(l.toLowerCase())}>
            <div className="section-title">{l}</div>
            <div style={{ fontSize: 22, fontWeight: 700, color: c }}>{v}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
        {['all','error','running','disabled'].map(f => (
          <button key={f} onClick={() => setFilter(f)} style={{
            background: filter === f ? 'rgba(0,229,255,.15)' : 'var(--surface)',
            border: `1px solid ${filter === f ? 'rgba(0,229,255,.4)' : 'var(--border)'}`,
            color: filter === f ? 'var(--cyan)' : 'var(--muted)',
            padding: '4px 12px', borderRadius: 4, fontSize: 11, cursor: 'pointer', fontFamily: 'inherit',
          }}>{f}</button>
        ))}
        <LastUpdated ts={lastUpdated} />
      </div>

      {/* Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ background: 'var(--bg3)', borderBottom: '1px solid var(--border)' }}>
              {['Job', 'Agent', 'Schedule', 'Next', 'Last Run', 'Duration', 'Status', 'Actions'].map(h => (
                <th key={h} style={{ padding: '8px 12px', textAlign: 'left', fontSize: 10,
                  color: 'var(--muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.05em' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr><td colSpan={8} style={{ padding: '20px', color: 'var(--muted)', textAlign: 'center' }}>No cron jobs match filter</td></tr>
            )}
            {filtered.map(j => (
              <CronRow key={j.id} job={j} agents={agents} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
