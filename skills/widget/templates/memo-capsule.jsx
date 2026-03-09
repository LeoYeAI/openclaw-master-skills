import { React } from 'uebersicht'

export const refreshFrequency = false

export const className = `
  position: fixed;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
`

const STORAGE_KEY = 'widgetdesk-memo-capsule'
const POSITION_KEY = 'widgetdesk-memo-capsule-position'
const MAX_LEN = 180
const WIDTH = 320
const DEFAULT_TOP = 40

const loadMemo = () => {
  const fallback = { draft: '', updatedAt: null }
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (!saved) return fallback
    const parsed = JSON.parse(saved)
    return {
      draft: typeof parsed.draft === 'string' ? parsed.draft : '',
      updatedAt: parsed.updatedAt || null,
    }
  } catch {
    return fallback
  }
}

const saveMemo = (draft) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    draft,
    updatedAt: new Date().toISOString(),
  }))
}

const defaultPosition = () => {
  const viewportWidth = typeof window !== 'undefined' ? window.innerWidth : 1440
  return {
    x: Math.max(40, Math.round(viewportWidth / 2 - WIDTH / 2)),
    y: DEFAULT_TOP,
  }
}

const loadPosition = () => {
  const fallback = defaultPosition()
  try {
    const saved = localStorage.getItem(POSITION_KEY)
    if (!saved) return fallback
    const parsed = JSON.parse(saved)
    if (typeof parsed.x !== 'number' || typeof parsed.y !== 'number') return fallback
    return parsed
  } catch {
    return fallback
  }
}

const savePosition = (pos) => {
  localStorage.setItem(POSITION_KEY, JSON.stringify(pos))
}

const formatUpdatedAt = (value) => {
  if (!value) return 'Empty'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Saved'
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const MemoCapsule = () => {
  const { useMemo, useState, useEffect, useRef, useCallback } = React
  const initial = useMemo(() => loadMemo(), [])
  const initialPos = useMemo(() => loadPosition(), [])
  const [draft, setDraft] = useState(initial.draft)
  const [updatedAt, setUpdatedAt] = useState(initial.updatedAt)
  const [copied, setCopied] = useState(false)
  const [pos, setPos] = useState(initialPos)
  const dragging = useRef(false)
  const offset = useRef({ x: 0, y: 0 })

  useEffect(() => {
    saveMemo(draft)
    setUpdatedAt(new Date().toISOString())
  }, [draft])

  useEffect(() => {
    if (!copied) return
    const timer = setTimeout(() => setCopied(false), 1200)
    return () => clearTimeout(timer)
  }, [copied])

  useEffect(() => {
    savePosition(pos)
  }, [pos])

  const onDragStart = useCallback((event) => {
    dragging.current = true
    offset.current = {
      x: event.clientX - pos.x,
      y: event.clientY - pos.y,
    }
    event.preventDefault()
  }, [pos.x, pos.y])

  useEffect(() => {
    const onMove = (event) => {
      if (!dragging.current) return
      const next = {
        x: Math.max(16, event.clientX - offset.current.x),
        y: Math.max(16, event.clientY - offset.current.y),
      }
      setPos(next)
    }

    const onUp = () => {
      dragging.current = false
    }

    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
    return () => {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }
  }, [])

  const remaining = MAX_LEN - draft.length

  const onChange = (event) => {
    setDraft(event.target.value.slice(0, MAX_LEN))
  }

  const onClear = () => {
    setDraft('')
  }

  const onCopy = async () => {
    if (!draft.trim()) return
    try {
      await navigator.clipboard.writeText(draft)
      setCopied(true)
    } catch {}
  }

  return (
    <div style={{
      position: 'fixed',
      left: `${pos.x}px`,
      top: `${pos.y}px`,
      width: `${WIDTH}px`,
      background: 'rgba(8, 12, 20, 0.72)',
      backdropFilter: 'blur(24px)',
      WebkitBackdropFilter: 'blur(24px)',
      borderRadius: '18px',
      border: '1px solid rgba(255,255,255,0.08)',
      boxShadow: '0 14px 40px rgba(0, 0, 0, 0.35)',
      padding: '16px 18px 14px',
      color: 'rgba(255,255,255,0.92)',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'baseline',
        justifyContent: 'space-between',
        gap: '12px',
        marginBottom: '12px',
        cursor: dragging.current ? 'grabbing' : 'grab',
        userSelect: 'none',
      }}>
        <div>
          <div style={{
            fontSize: '10px',
            letterSpacing: '1.8px',
            textTransform: 'uppercase',
            color: 'rgba(255,255,255,0.34)',
            marginBottom: '6px',
          }}>
            Memo
          </div>
          <div
            onMouseDown={onDragStart}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              fontSize: '18px',
              fontWeight: 600,
              letterSpacing: '-0.3px',
            }}
          >
            Capsule
          </div>
        </div>
        <div style={{
          textAlign: 'right',
          fontVariantNumeric: 'tabular-nums',
        }}>
          <div style={{
            fontSize: '11px',
            color: copied ? 'rgba(124, 255, 186, 0.92)' : 'rgba(255,255,255,0.34)',
            textTransform: 'uppercase',
            letterSpacing: '1.4px',
          }}>
            {copied ? 'Copied' : formatUpdatedAt(updatedAt)}
          </div>
          <div style={{
            fontSize: '26px',
            fontWeight: 300,
            letterSpacing: '-1px',
            color: 'rgba(255,255,255,0.88)',
            lineHeight: 1.1,
            marginTop: '4px',
          }}>
            {remaining}
          </div>
        </div>
      </div>

      <textarea
        value={draft}
        onChange={onChange}
        placeholder="Jot something down..."
        style={{
          width: '100%',
          minHeight: '116px',
          resize: 'none',
          border: 'none',
          outline: 'none',
          borderRadius: '14px',
          padding: '14px 14px 12px',
          boxSizing: 'border-box',
          background: 'rgba(255,255,255,0.04)',
          color: 'rgba(255,255,255,0.92)',
          fontSize: '14px',
          lineHeight: 1.5,
          boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.05)',
          fontFamily: 'inherit',
        }}
      />

      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        gap: '10px',
        marginTop: '12px',
      }}>
        <button
          onClick={onClear}
          style={{
            border: '1px solid rgba(255,255,255,0.12)',
            background: 'rgba(255,255,255,0.04)',
            color: 'rgba(255,255,255,0.58)',
            borderRadius: '10px',
            padding: '8px 12px',
            fontSize: '12px',
            fontWeight: 600,
            cursor: 'pointer',
            fontFamily: 'inherit',
          }}
        >
          Clear
        </button>
        <button
          onClick={onCopy}
          style={{
            border: '1px solid rgba(124, 191, 255, 0.28)',
            background: 'rgba(124, 191, 255, 0.12)',
            color: 'rgba(160, 214, 255, 0.96)',
            borderRadius: '10px',
            padding: '8px 14px',
            fontSize: '12px',
            fontWeight: 600,
            cursor: draft.trim() ? 'pointer' : 'default',
            opacity: draft.trim() ? 1 : 0.45,
            fontFamily: 'inherit',
          }}
        >
          Copy
        </button>
      </div>
    </div>
  )
}

export const render = () => <MemoCapsule />
