const BADGE_COLOR = { 'HITL': 'var(--red)', 'Alerts': 'var(--red)', 'Crons': 'var(--amber)' };

export default function Nav({ tabs, active, onChange, badges = {} }) {
  return (
    <nav style={{
      height: 44, background: 'var(--bg3)', borderBottom: '1px solid var(--border)',
      display: 'flex', alignItems: 'stretch', padding: '0 16px', gap: 2,
      position: 'sticky', top: 52, zIndex: 99, overflowX: 'auto',
    }}>
      {tabs.map(tab => {
        const badge = badges[tab];
        return (
          <button key={tab} onClick={() => onChange(tab)} style={{
            background: 'none', border: 'none', cursor: 'pointer', padding: '0 14px',
            fontSize: 12, fontFamily: 'inherit', fontWeight: active === tab ? 600 : 400,
            color: active === tab ? 'var(--cyan)' : 'var(--muted)',
            borderBottom: active === tab ? '2px solid var(--cyan)' : '2px solid transparent',
            transition: 'all .15s', whiteSpace: 'nowrap',
            position: 'relative', display: 'flex', alignItems: 'center', gap: 5,
          }}>
            {tab}
            {badge > 0 && (
              <span style={{
                fontSize: 9, fontWeight: 700, padding: '1px 5px', borderRadius: 8,
                background: BADGE_COLOR[tab] || 'var(--cyan)',
                color: '#fff', lineHeight: 1.4, minWidth: 16, textAlign: 'center',
                animation: tab === 'HITL' ? 'pulse 2s infinite' : 'none',
              }}>{badge}</span>
            )}
          </button>
        );
      })}
    </nav>
  );
}
