import { React } from 'uebersicht'

export const command = `
TRACK_INFO=$(osascript << 'END'
tell application "Music"
  try
    if player state is not stopped then
      set trackName to name of current track
      set artistName to artist of current track
      set trackPos to player position
      set trackDur to duration of current track
      set playState to player state as string
      return trackName & "|||" & artistName & "|||" & (round trackPos) & "|||" & (round trackDur) & "|||" & playState
    else
      return "stopped"
    end if
  on error
    return "stopped"
  end try
end tell
END
)
echo "$TRACK_INFO"
`

export const refreshFrequency = 2000

export const className = `
  position: fixed;
  bottom: 90px;
  left: 50%;
  transform: translateX(-50%);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
`

const parse = (raw) => {
  if (!raw || raw.trim() === 'stopped') return null
  const p = raw.trim().split('|||')
  if (p.length < 5) return null
  return {
    title:     p[0] || '',
    artist:    p[1] || '',
    position:  parseInt(p[2]) || 0,
    duration:  parseInt(p[3]) || 1,
    isPlaying: p[4].trim() === 'playing',
  }
}

const fmt = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`

const BAR_COUNT = 28

const EqBars = ({ isPlaying }) => {
  const { useState, useEffect, useRef } = React
  const [heights, setHeights] = useState(() =>
    Array.from({ length: BAR_COUNT }, (_, i) =>
      0.15 + Math.abs(Math.sin(i * 0.4)) * 0.3
    )
  )
  const peaksRef = useRef(heights.map(h => h))

  useEffect(() => {
    if (!isPlaying) {
      // 停止时缓慢归零
      const t = setInterval(() => {
        setHeights(h => {
          const next = h.map(v => Math.max(0.04, v * 0.85))
          if (next.every(v => v <= 0.05)) clearInterval(t)
          return next
        })
      }, 80)
      return () => clearInterval(t)
    }

    const t = setInterval(() => {
      setHeights(prev => prev.map((_, i) => {
        // 模拟不同频率段的响应特征
        const bass    = i < 6  ? 0.5 + Math.random() * 0.5 : 0
        const mid     = i < 16 ? 0.3 + Math.random() * 0.5 : 0
        const treble  = 0.1 + Math.random() * 0.4
        const base    = Math.max(bass, mid, treble)
        // 峰值保持
        if (base > peaksRef.current[i]) peaksRef.current[i] = base
        else peaksRef.current[i] *= 0.92
        return Math.min(1, base * 0.7 + peaksRef.current[i] * 0.3)
      }))
    }, 100)
    return () => clearInterval(t)
  }, [isPlaying])

  return (
    <div style={{
      display: 'flex',
      alignItems: 'flex-end',
      gap: '3px',
      height: '48px',
      padding: '0 2px',
    }}>
      {heights.map((h, i) => {
        // 颜色从青绿渐变到蓝紫
        const hue = 175 + (i / BAR_COUNT) * 60
        const light = 45 + h * 25
        return (
          <div key={i} style={{
            flex: 1,
            height: `${Math.max(3, h * 100)}%`,
            background: `hsl(${hue}, 90%, ${light}%)`,
            borderRadius: '1.5px 1.5px 0 0',
            boxShadow: h > 0.6 ? `0 0 6px hsl(${hue}, 90%, ${light}%)` : 'none',
            transition: 'height 0.09s ease-out',
            opacity: isPlaying ? 1 : 0.35,
          }} />
        )
      })}
    </div>
  )
}

const Player = ({ output }) => {
  const track = parse(output)
  const progress = track ? track.position / track.duration : 0

  return (
    <div style={{
      width: '320px',
      background: 'rgba(4, 8, 20, 0.88)',
      backdropFilter: 'blur(30px)',
      WebkitBackdropFilter: 'blur(30px)',
      borderRadius: '16px',
      border: '1px solid rgba(80, 200, 255, 0.12)',
      boxShadow: '0 16px 48px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.05)',
      overflow: 'hidden',
    }}>

      {/* 顶部标题栏 */}
      <div style={{
        padding: '10px 16px 0',
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
      }}>
        <div style={{
          width: '6px', height: '6px', borderRadius: '50%',
          background: track?.isPlaying ? 'rgba(80,220,160,1)' : 'rgba(255,255,255,0.15)',
          boxShadow: track?.isPlaying ? '0 0 8px rgba(80,220,160,0.8)' : 'none',
          transition: 'all 0.4s',
        }} />
        <span style={{
          fontSize: '10px',
          letterSpacing: '2px',
          color: 'rgba(80, 200, 255, 0.5)',
          textTransform: 'uppercase',
          fontWeight: 500,
        }}>
          {track?.isPlaying ? 'Now Playing' : 'Paused'}
        </span>
      </div>

      {/* 均衡器 */}
      <div style={{ padding: '10px 16px 6px' }}>
        <EqBars isPlaying={!!track?.isPlaying} />
      </div>

      {/* 分隔线 */}
      <div style={{
        height: '1px',
        background: 'linear-gradient(90deg, transparent, rgba(80,200,255,0.15), transparent)',
        margin: '0 16px',
      }} />

      {/* 曲目信息 */}
      <div style={{ padding: '12px 16px 8px' }}>
        {track ? (
          <>
            <div style={{
              fontSize: '15px',
              fontWeight: '600',
              color: 'rgba(255,255,255,0.92)',
              letterSpacing: '-0.2px',
              marginBottom: '3px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}>
              {track.title}
            </div>
            <div style={{
              fontSize: '12px',
              color: 'rgba(80, 200, 255, 0.55)',
              letterSpacing: '0.3px',
            }}>
              {track.artist}
            </div>
          </>
        ) : (
          <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.2)' }}>
            打开 Music 开始播放
          </div>
        )}
      </div>

      {/* 进度条 */}
      <div style={{ padding: '0 16px 14px' }}>
        <div style={{
          position: 'relative',
          height: '2px',
          background: 'rgba(255,255,255,0.06)',
          borderRadius: '1px',
          marginBottom: '6px',
        }}>
          <div style={{
            position: 'absolute',
            left: 0, top: 0,
            height: '100%',
            width: `${progress * 100}%`,
            background: 'linear-gradient(90deg, rgba(80,180,255,0.8), rgba(120,220,200,0.9))',
            borderRadius: '1px',
            transition: 'width 1.5s linear',
          }} />
          <div style={{
            position: 'absolute',
            top: '50%',
            left: `${Math.min(progress * 100, 98)}%`,
            transform: 'translate(-50%, -50%)',
            width: '7px', height: '7px',
            borderRadius: '50%',
            background: 'rgba(160, 230, 255, 0.95)',
            boxShadow: '0 0 8px rgba(120,200,255,0.8)',
            transition: 'left 1.5s linear',
            opacity: track ? 1 : 0,
          }} />
        </div>

        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '10px',
          color: 'rgba(255,255,255,0.2)',
          fontVariantNumeric: 'tabular-nums',
          letterSpacing: '0.3px',
        }}>
          <span>{track ? fmt(track.position) : '0:00'}</span>
          <span>{track ? fmt(track.duration) : '0:00'}</span>
        </div>
      </div>

    </div>
  )
}

export const render = ({ output }) => <Player output={output} />
