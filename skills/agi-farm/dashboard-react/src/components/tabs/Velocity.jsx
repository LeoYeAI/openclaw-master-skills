import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import LastUpdated from '../LastUpdated';

const COLORS = ['#00e5ff','#00e676','#ffd600','#ff1744','#e040fb','#ff6d00','#1de9b6'];

export default function Velocity({ data, lastUpdated }) {
  const { velocity = {}, tasks = [] } = data;
  const daily   = velocity.daily           || [];
  const summary = velocity.weekly_summary  || {};
  const metrics = velocity.metrics         || {};

  const barData = (() => {
    const days = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date(); d.setDate(d.getDate() - i);
      const dateStr = d.toISOString().split('T')[0];
      const row = daily.find(r => r.date === dateStr) || {};
      days.push({
        name: d.toLocaleDateString('en-US', { weekday: 'short', month: 'numeric', day: 'numeric' }),
        completed: row.tasks_completed || 0,
        failed:    row.tasks_failed    || 0,
        quality:   row.avg_quality     ?? null,
      });
    }
    return days;
  })();

  const typeCounts = {};
  tasks.forEach(t => { const ty = t.type || 'other'; typeCounts[ty] = (typeCounts[ty] || 0) + 1; });
  const pieData = Object.entries(typeCounts).map(([name, value]) => ({ name, value }));

  const tooltipStyle = { background: '#0d0d1a', border: '1px solid rgba(0,229,255,.2)', borderRadius: 6, fontSize: 11 };

  return (
    <div className="fade-in" style={{ display: 'grid', gap: 14 }}>
      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5,1fr)', gap: 10 }}>
        {[
          ['Completed',   summary.tasks_completed ?? 0,                            'var(--green)'],
          ['Failed',      summary.tasks_failed    ?? 0,                            'var(--red)'],
          ['Avg Quality', (summary.avg_quality    ?? 0).toFixed(2),               'var(--amber)'],
          ['SLA Breaches',summary.sla_breaches    ?? 0,                            'var(--purple)'],
          ['Tasks/Day',   (metrics.throughput_rate_tasks_per_day ?? 0).toFixed(1),'var(--cyan)'],
        ].map(([l, v, c]) => (
          <div key={l} className="card" style={{ textAlign: 'center' }}>
            <div className="section-title">{l}</div>
            <div style={{ fontSize: 20, fontWeight: 700, color: c }}>{v}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 14 }}>
        {/* 7-day bars */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 10 }}>
            <span className="section-title" style={{ marginBottom: 0 }}>7-Day Throughput</span>
            <LastUpdated ts={lastUpdated} />
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={barData} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.06)" />
              <XAxis dataKey="name" tick={{ fill: '#546e7a', fontSize: 10 }} />
              <YAxis tick={{ fill: '#546e7a', fontSize: 10 }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="completed" fill="#00e5ff" name="Completed" radius={[3,3,0,0]} />
              <Bar dataKey="failed"    fill="#ff1744" name="Failed"    radius={[3,3,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Task type donut */}
        <div className="card">
          <div className="section-title">Task Types</div>
          {pieData.length === 0
            ? <div style={{ color: 'var(--muted)', fontSize: 11, paddingTop: 16 }}>No data yet</div>
            : <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" nameKey="name">
                    {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={tooltipStyle} />
                  <Legend wrapperStyle={{ fontSize: 10 }} />
                </PieChart>
              </ResponsiveContainer>
          }
        </div>
      </div>

      {/* Quality trend */}
      <div className="card">
        <div className="section-title">Quality Trend (7-day)</div>
        <ResponsiveContainer width="100%" height={160}>
          <LineChart data={barData} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,.06)" />
            <XAxis dataKey="name" tick={{ fill: '#546e7a', fontSize: 10 }} />
            <YAxis domain={[0, 5]} tick={{ fill: '#546e7a', fontSize: 10 }} />
            <Tooltip contentStyle={tooltipStyle} />
            <Line type="monotone" dataKey="quality" stroke="#ffd600" strokeWidth={2}
              dot={{ fill: '#ffd600', r: 3 }} connectNulls name="Avg Quality" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
