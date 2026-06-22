import { useEffect, useRef } from 'react';

export default function Broadcast({ data }) {
  const { broadcast = '' } = data;
  const ref = useRef(null);

  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight;
  }, [broadcast]);

  const lines = broadcast.split('\n');

  return (
    <div className="fade-in">
      <div style={{
        background: 'var(--bg2)', border: '1px solid var(--border)', borderRadius: 8,
        padding: 16, fontFamily: 'JetBrains Mono, monospace', fontSize: 12,
        height: 'calc(100vh - 160px)', overflowY: 'auto',
      }} ref={ref}>
        {lines.length === 0 || broadcast.trim() === ''
          ? <span style={{ color: 'var(--muted)' }}>No broadcasts yet.</span>
          : lines.map((line, i) => <BroadcastLine key={i} line={line} />)
        }
        <div style={{ height: 8 }} />
      </div>
    </div>
  );
}

function BroadcastLine({ line }) {
  const low = line.toLowerCase();
  let color = 'var(--text)';
  if (low.includes('[critical]') || low.includes('🔴'))   color = 'var(--red)';
  else if (low.includes('[blocked]') || low.includes('⚠')) color = 'var(--amber)';
  else if (low.includes('[hitl]')    || low.includes('🚨')) color = 'var(--purple)';
  else if (low.includes('[done]')    || low.includes('✅')) color = 'var(--green)';
  else if (line.startsWith('#'))                           color = 'var(--cyan)';
  else if (line.startsWith('---'))                        color = 'rgba(84,110,122,.5)';
  else if (low.includes('task_id:') || low.includes('from:')) color = 'var(--muted)';

  return (
    <div style={{
      color, padding: '1px 0', lineHeight: 1.6, whiteSpace: 'pre-wrap', wordBreak: 'break-word',
    }}>
      {line || '\u00A0'}
    </div>
  );
}
