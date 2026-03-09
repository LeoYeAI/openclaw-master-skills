import { React, run } from 'uebersicht'

export const command = `
VOL=$(osascript -e 'output volume of (get volume settings)')
MUTED=$(osascript -e 'output muted of (get volume settings)')
printf "%s|||%s" "$VOL" "$MUTED"
`

export const refreshFrequency = 800

export const className = `
  position: fixed;
  bottom: 250px;
  right: 40px;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
  pointer-events: auto;
  user-select: none;
  -webkit-user-select: none;
`

const clamp = (value, min, max) => Math.max(min, Math.min(max, value))

const setVolume = (value) => {
  const safeValue = clamp(value, 0, 100)
  return run(`osascript -e 'set volume output volume ${safeValue}'`)
}

const setMuted = (muted) =>
  run(`osascript -e 'set volume ${muted ? 'with' : 'without'} output muted'`)

const Widget = ({ output }) => {
  const [volumeText = '0', mutedText = 'false'] = (output || '').trim().split('|||')
  const volume = clamp(parseInt(volumeText, 10) || 0, 0, 100)
  const muted = mutedText.trim() === 'true'

  const accent = muted
    ? 'rgba(255,255,255,0.26)'
    : volume < 35
      ? '#8cc8ff'
      : volume < 70
        ? '#86e2b4'
        : '#ffd27a'

  const radius = 42
  const circumference = 2 * Math.PI * radius
  const arcLength = circumference * 0.75
  const filledLength = (volume / 100) * arcLength

  const buttonStyle = {
    flex: 1,
    height: '34px',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: '10px',
    background: 'rgba(255,255,255,0.05)',
    color: 'rgba(255,255,255,0.88)',
    fontSize: '15px',
    fontFamily: 'inherit',
    cursor: 'pointer',
  }

  return (
    <div
      style={{
        width: '160px',
        padding: '14px',
        background: 'rgba(8, 12, 20, 0.72)',
        backdropFilter: 'blur(24px)',
        WebkitBackdropFilter: 'blur(24px)',
        borderRadius: '18px',
        border: '1px solid rgba(255,255,255,0.08)',
        boxShadow: '0 14px 40px rgba(0,0,0,0.35)',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '12px',
        }}
      >
        <div
          style={{
            fontSize: '11px',
            letterSpacing: '1.8px',
            textTransform: 'uppercase',
            color: 'rgba(255,255,255,0.44)',
          }}
        >
          Volume
        </div>
        <button
          onClick={() => setMuted(!muted)}
          style={{
            border: 'none',
            background: 'transparent',
            color: muted ? 'rgba(255,255,255,0.46)' : 'rgba(255,255,255,0.82)',
            fontSize: '12px',
            letterSpacing: '1px',
            textTransform: 'uppercase',
            cursor: 'pointer',
            padding: 0,
          }}
        >
          {muted ? 'Unmute' : 'Mute'}
        </button>
      </div>

      <div
        style={{
          position: 'relative',
          width: '132px',
          height: '132px',
          margin: '0 auto 12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <svg width="132" height="132" style={{ position: 'absolute', inset: 0 }}>
          <circle
            cx="66"
            cy="66"
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.08)"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${arcLength} ${circumference}`}
            transform="rotate(135, 66, 66)"
          />
          <circle
            cx="66"
            cy="66"
            r={radius}
            fill="none"
            stroke={accent}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${filledLength} ${circumference}`}
            transform="rotate(135, 66, 66)"
            style={{ transition: 'stroke-dasharray 160ms ease, stroke 160ms ease' }}
          />
        </svg>

        <div style={{ textAlign: 'center' }}>
          <div
            style={{
              fontSize: '34px',
              fontWeight: '700',
              lineHeight: 1,
              color: muted ? 'rgba(255,255,255,0.32)' : 'rgba(255,255,255,0.95)',
              fontVariantNumeric: 'tabular-nums',
            }}
          >
            {muted ? '0' : volume}
          </div>
          <div
            style={{
              marginTop: '5px',
              fontSize: '10px',
              letterSpacing: '1.4px',
              textTransform: 'uppercase',
              color: muted ? 'rgba(255,255,255,0.32)' : 'rgba(255,255,255,0.52)',
            }}
          >
            {muted ? 'Muted' : 'Output'}
          </div>
        </div>

        <button
          onClick={() => setVolume(volume - 5)}
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            width: '50%',
            height: '100%',
            opacity: 0,
            cursor: 'w-resize',
          }}
          aria-label="Decrease volume"
        />
        <button
          onClick={() => setVolume(volume + 5)}
          style={{
            position: 'absolute',
            right: 0,
            top: 0,
            width: '50%',
            height: '100%',
            opacity: 0,
            cursor: 'e-resize',
          }}
          aria-label="Increase volume"
        />
      </div>

      <div style={{ display: 'flex', gap: '8px' }}>
        <button onClick={() => setVolume(volume - 10)} style={buttonStyle}>
          -
        </button>
        <button
          onClick={() => setMuted(!muted)}
          style={{
            ...buttonStyle,
            flex: 1.4,
            color: muted ? '#ffd27a' : 'rgba(255,255,255,0.88)',
          }}
        >
          {muted ? 'Muted' : 'Sound'}
        </button>
        <button onClick={() => setVolume(volume + 10)} style={buttonStyle}>
          +
        </button>
      </div>
    </div>
  )
}

export const render = ({ output }) => <Widget output={output} />
