export const command = `
  echo "cpu:$(top -l 1 | grep "CPU usage" | awk '{print $3}' | tr -d '%' 2>/dev/null || echo '?')"
  echo "bat:$(pmset -g batt | grep -o '[0-9]*%' | head -1 | tr -d '%' || echo '?')"
  echo "mem:$(python3 -c "
import subprocess
r = subprocess.run(['vm_stat'], capture_output=True, text=True)
lines = r.stdout.split('\n')
ps = {}
for l in lines[1:]:
    if ':' in l:
        k, v = l.split(':', 1)
        try: ps[k.strip()] = int(v.strip().rstrip('.'))
        except: pass
total = ps.get('Pages free',0)+ps.get('Pages active',0)+ps.get('Pages inactive',0)+ps.get('Pages wired down',0)
used = ps.get('Pages active',0)+ps.get('Pages wired down',0)
print(round(used/total*100) if total else '?')
" 2>/dev/null || echo '?')"
`

export const refreshFrequency = 5000

export const className = `
  position: fixed;
  top: 40px;
  right: 40px;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Mono', monospace;
  pointer-events: none;
`

const parseOutput = (raw) => {
  const result = { cpu: '?', bat: '?', mem: '?' }
  if (!raw) return result
  raw.split('\n').forEach(line => {
    const idx = line.indexOf(':')
    if (idx > -1) {
      const key = line.slice(0, idx).trim()
      const val = line.slice(idx + 1).trim()
      if (result.hasOwnProperty(key)) result[key] = val
    }
  })
  return result
}

const Bar = ({ value, color }) => {
  const pct = isNaN(parseInt(value)) ? 0 : Math.min(100, parseInt(value))
  return (
    <div style={{
      width: '80px',
      height: '4px',
      background: 'rgba(255,255,255,0.1)',
      borderRadius: '2px',
      overflow: 'hidden',
    }}>
      <div style={{
        width: `${pct}%`,
        height: '100%',
        background: color,
        borderRadius: '2px',
        transition: 'width 0.4s ease',
      }} />
    </div>
  )
}

const StatRow = ({ label, value, color }) => (
  <div style={{
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '10px',
  }}>
    <div style={{ width: '32px', fontSize: '10px', color: 'rgba(255,255,255,0.4)', letterSpacing: '0.5px' }}>
      {label}
    </div>
    <Bar value={value} color={color} />
    <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.7)', width: '36px', textAlign: 'right' }}>
      {value}%
    </div>
  </div>
)

export const render = ({ output }) => {
  const stats = parseOutput(output)
  const batVal = parseInt(stats.bat)
  const batColor = batVal < 20
    ? 'rgba(255, 82, 82, 0.9)'
    : batVal < 50
    ? 'rgba(255, 196, 0, 0.9)'
    : 'rgba(82, 196, 82, 0.9)'

  return (
    <div style={{
      background: 'rgba(0, 0, 0, 0.4)',
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
      borderRadius: '14px',
      border: '1px solid rgba(255,255,255,0.08)',
      padding: '14px 16px',
    }}>
      <div style={{
        fontSize: '10px',
        letterSpacing: '1.5px',
        color: 'rgba(255,255,255,0.3)',
        marginBottom: '12px',
        textTransform: 'uppercase',
      }}>
        系统
      </div>
      <StatRow label="CPU" value={stats.cpu} color="rgba(130, 180, 255, 0.9)" />
      <StatRow label="MEM" value={stats.mem} color="rgba(180, 130, 255, 0.9)" />
      <StatRow label="BAT" value={stats.bat} color={batColor} />
    </div>
  )
}
