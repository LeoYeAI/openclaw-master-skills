import { useState } from 'react';
import LastUpdated from '../LastUpdated';

function CommsPanel({ content, label, color }) {
  if (!content || content.trim() === '' || content.trim() === `# ${label}\n\n_No messages._`) {
    return <div style={{ color: 'var(--muted)', fontSize: 11, padding: '8px 0' }}>No {label.toLowerCase()} messages.</div>;
  }

  const lines = content.split('\n');
  return (
    <div style={{ fontFamily: 'monospace', fontSize: 11, lineHeight: 1.7, maxHeight: 400, overflowY: 'auto' }}>
      {lines.map((line, i) => {
        let lineColor = 'var(--text)';
        if (line.startsWith('## '))      lineColor = color;
        else if (line.startsWith('# '))  lineColor = color;
        else if (line.startsWith('---')) lineColor = 'rgba(255,255,255,.1)';
        else if (line.startsWith('- '))  lineColor = 'var(--muted)';
        else if (line.startsWith('**'))  lineColor = 'var(--amber)';
        return (
          <div key={i} style={{ color: lineColor, padding: '1px 0',
            borderBottom: line.startsWith('---') ? '1px solid rgba(255,255,255,.06)' : 'none' }}>
            {line || '\u00A0'}
          </div>
        );
      })}
    </div>
  );
}

export default function Comms({ data, lastUpdated }) {
  const { comms = {}, agents = [] } = data;
  const [selectedAgent, setSelectedAgent] = useState(agents[0]?.id || null);
  const [view, setView] = useState('inbox');

  const agentComms = comms[selectedAgent] || { inbox: '', outbox: '' };
  const agent = agents.find(a => a.id === selectedAgent);

  // Count messages per agent
  const countMessages = (text) => (text?.match(/^## /gm) || []).length;

  return (
    <div className="fade-in" style={{ display: 'grid', gridTemplateColumns: '200px 1fr', gap: 14, minHeight: 500 }}>
      {/* Agent selector */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <div className="section-title">Agents</div>
        {agents.map(a => {
          const ac = comms[a.id] || {};
          const inboxCount = countMessages(ac.inbox);
          const outboxCount = countMessages(ac.outbox);
          return (
            <button key={a.id} onClick={() => setSelectedAgent(a.id)} style={{
              background: selectedAgent === a.id ? 'rgba(0,229,255,.12)' : 'var(--surface)',
              border: `1px solid ${selectedAgent === a.id ? 'rgba(0,229,255,.4)' : 'var(--border)'}`,
              borderRadius: 6, padding: '8px 10px', cursor: 'pointer', textAlign: 'left',
              display: 'flex', alignItems: 'center', gap: 8, fontFamily: 'inherit',
            }}>
              <span style={{ fontSize: 18 }}>{a.emoji}</span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: selectedAgent === a.id ? 'var(--cyan)' : 'var(--text)',
                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{a.name}</div>
                <div style={{ fontSize: 10, color: 'var(--muted)' }}>
                  📬{inboxCount} · 📤{outboxCount}
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Comms viewer */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {agent && <span style={{ fontSize: 20 }}>{agent.emoji}</span>}
          {agent && <span style={{ fontWeight: 700, fontSize: 14 }}>{agent.name}</span>}
          <div style={{ display: 'flex', gap: 4, marginLeft: 8 }}>
            {['inbox','outbox'].map(v => (
              <button key={v} onClick={() => setView(v)} style={{
                background: view === v ? 'rgba(0,229,255,.15)' : 'var(--surface)',
                border: `1px solid ${view === v ? 'rgba(0,229,255,.4)' : 'var(--border)'}`,
                color: view === v ? 'var(--cyan)' : 'var(--muted)',
                padding: '4px 12px', borderRadius: 4, fontSize: 11, cursor: 'pointer', fontFamily: 'inherit',
                textTransform: 'capitalize',
              }}>{v === 'inbox' ? '📬' : '📤'} {v}</button>
            ))}
          </div>
          <LastUpdated ts={lastUpdated} />
        </div>

        <div className="card" style={{ flex: 1 }}>
          <CommsPanel
            content={agentComms[view]}
            label={view === 'inbox' ? 'Inbox' : 'Outbox'}
            color={view === 'inbox' ? 'var(--cyan)' : 'var(--green)'}
          />
        </div>
      </div>
    </div>
  );
}
