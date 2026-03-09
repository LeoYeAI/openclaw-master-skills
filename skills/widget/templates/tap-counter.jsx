import { React } from 'uebersicht'

export const refreshFrequency = false

export const className = `
  position: fixed;
  bottom: 90px;
  right: 40px;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
  pointer-events: auto;
  user-select: none;
  -webkit-user-select: none;
`

const STORAGE_KEY = 'widgetdesk-tap-counter'
const DEFAULT_VALUE = 12

const loadValue = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw === null) return DEFAULT_VALUE
    const parsed = JSON.parse(raw)
    return typeof parsed === 'number' && Number.isFinite(parsed) ? parsed : DEFAULT_VALUE
  } catch {
    return DEFAULT_VALUE
  }
}

const saveValue = (value) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(value))
}

const buttonBase = {
  border: '1px solid rgba(255,255,255,0.08)',
  borderRadius: '12px',
  background: 'rgba(255,255,255,0.05)',
  color: 'rgba(255,255,255,0.9)',
  fontFamily: 'inherit',
  cursor: 'pointer',
}

const TapCounter = () => {
  const { useState, useEffect } = React
  const [count, setCount] = useState(() => loadValue())

  useEffect(() => {
    saveValue(count)
  }, [count])

  return (
    <div
      style={{
        width: '220px',
        background: 'rgba(8, 12, 20, 0.72)',
        backdropFilter: 'blur(24px)',
        WebkitBackdropFilter: 'blur(24px)',
        borderRadius: '18px',
        border: '1px solid rgba(255,255,255,0.08)',
        boxShadow: '0 14px 40px rgba(0,0,0,0.35)',
        padding: '16px',
        color: 'rgba(255,255,255,0.92)',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '14px',
        }}
      >
        <div>
          <div
            style={{
              fontSize: '10px',
              letterSpacing: '1.8px',
              textTransform: 'uppercase',
              color: 'rgba(255,255,255,0.38)',
              marginBottom: '5px',
            }}
          >
            Interactive
          </div>
          <div
            style={{
              fontSize: '18px',
              fontWeight: 600,
              letterSpacing: '-0.4px',
            }}
          >
            Tap Counter
          </div>
        </div>

        <button
          onClick={() => setCount(DEFAULT_VALUE)}
          style={{
            ...buttonBase,
            height: '30px',
            padding: '0 10px',
            fontSize: '11px',
            letterSpacing: '1px',
            textTransform: 'uppercase',
            color: 'rgba(255,255,255,0.65)',
          }}
        >
          Reset
        </button>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '56px 1fr 56px',
          gap: '10px',
          alignItems: 'center',
        }}
      >
        <button
          onClick={() => setCount((value) => value - 1)}
          style={{
            ...buttonBase,
            height: '56px',
            fontSize: '28px',
            lineHeight: 1,
          }}
          aria-label="Decrease count"
        >
          -
        </button>

        <div
          style={{
            minHeight: '88px',
            borderRadius: '16px',
            background: 'linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03))',
            boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.05)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <div
            style={{
              fontSize: '44px',
              fontWeight: 300,
              letterSpacing: '-2px',
              lineHeight: 1,
              fontVariantNumeric: 'tabular-nums',
            }}
          >
            {count}
          </div>
          <div
            style={{
              marginTop: '8px',
              fontSize: '11px',
              letterSpacing: '1.5px',
              textTransform: 'uppercase',
              color: 'rgba(255,255,255,0.42)',
            }}
          >
            Local state
          </div>
        </div>

        <button
          onClick={() => setCount((value) => value + 1)}
          style={{
            ...buttonBase,
            height: '56px',
            fontSize: '28px',
            lineHeight: 1,
            background: 'rgba(122, 240, 177, 0.12)',
            border: '1px solid rgba(122, 240, 177, 0.32)',
            color: 'rgba(162, 255, 208, 0.98)',
          }}
          aria-label="Increase count"
        >
          +
        </button>
      </div>
    </div>
  )
}

export const render = () => <TapCounter />
