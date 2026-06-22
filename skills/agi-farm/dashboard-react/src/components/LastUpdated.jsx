export default function LastUpdated({ ts, count }) {
  if (!ts) return null;
  return (
    <span style={{ fontSize: 9, color: 'var(--muted)', marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6 }}>
      {count != null && <span style={{ color: 'var(--cyan)', opacity: 0.6 }}>#{count}</span>}
      ↻ {ts.toLocaleTimeString()}
    </span>
  );
}
