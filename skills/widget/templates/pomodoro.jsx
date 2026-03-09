import { React } from 'uebersicht'

export const refreshFrequency = false

export const className = `
  position: fixed;
  bottom: 90px;
  left: 40px;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
`

const WORK_SECS = 25 * 60
const BREAK_SECS = 5 * 60

const PomodoroWidget = () => {
  const { useState, useEffect } = React
  const [phase, setPhase] = useState('work')
  const [remaining, setRemaining] = useState(WORK_SECS)
  const [running, setRunning] = useState(false)
  const [sessions, setSessions] = useState(0)

  // 每秒倒计时
  useEffect(() => {
    if (!running) return
    const timer = setInterval(() => {
      setRemaining(r => Math.max(0, r - 1))
    }, 1000)
    return () => clearInterval(timer)
  }, [running])

  // remaining 到 0 时切换阶段
  useEffect(() => {
    if (remaining !== 0) return
    setRunning(false)
    if (phase === 'work') {
      setSessions(s => s + 1)
      setPhase('break')
      setRemaining(BREAK_SECS)
    } else {
      setPhase('work')
      setRemaining(WORK_SECS)
    }
  }, [remaining])

  const mins = String(Math.floor(remaining / 60)).padStart(2, '0')
  const secs = String(remaining % 60).padStart(2, '0')
  const total = phase === 'work' ? WORK_SECS : BREAK_SECS
  const progress = 1 - remaining / total
  const isWork = phase === 'work'
  const accent = isWork ? 'rgba(255,82,82,0.9)' : 'rgba(82,196,255,0.9)'
  const accentBg = isWork ? 'rgba(255,82,82,0.12)' : 'rgba(82,196,255,0.12)'
  const circumference = 2 * Math.PI * 36

  return (
    <div style={{
      background: 'rgba(0,0,0,0.45)',
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
      borderRadius: '20px',
      border: '1px solid rgba(255,255,255,0.1)',
      padding: '20px 24px',
      width: '180px',
      color: 'rgba(255,255,255,0.9)',
    }}>
      <div style={{ fontSize: '11px', letterSpacing: '1.5px', textTransform: 'uppercase', color: accent, marginBottom: '16px', fontWeight: 600 }}>
        {isWork ? '专注' : '休息'} · {sessions} 🍅
      </div>

      <div style={{ position: 'relative', width: '88px', margin: '0 auto 16px' }}>
        <svg width="88" height="88" style={{ transform: 'rotate(-90deg)' }}>
          <circle cx="44" cy="44" r="36" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="4" />
          <circle cx="44" cy="44" r="36" fill="none" stroke={accent} strokeWidth="4"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={circumference * (1 - progress)}
            style={{ transition: 'stroke-dashoffset 0.5s ease' }}
          />
        </svg>
        <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '22px', fontWeight: '300', letterSpacing: '-1px' }}>
          {mins}:{secs}
        </div>
      </div>

      <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
        <button onClick={() => setRunning(r => !r)} style={{ background: accentBg, border: `1px solid ${accent}`, borderRadius: '10px', color: accent, fontSize: '12px', fontWeight: 600, padding: '6px 14px', cursor: 'pointer', fontFamily: 'inherit' }}>
          {running ? '暂停' : '开始'}
        </button>
        <button onClick={() => { setRunning(false); setPhase('work'); setRemaining(WORK_SECS); setSessions(0) }} style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '10px', color: 'rgba(255,255,255,0.5)', fontSize: '12px', fontWeight: 600, padding: '6px 10px', cursor: 'pointer', fontFamily: 'inherit' }}>
          重置
        </button>
      </div>
    </div>
  )
}

export const render = () => <PomodoroWidget />
