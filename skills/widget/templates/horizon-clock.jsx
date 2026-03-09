export const command = `date '+%H:%M:%S|||%Y年%-m月%-d日|||%A'`

export const refreshFrequency = 1000

export const className = `
  position: fixed;
  bottom: 90px;
  left: 50%;
  transform: translateX(-50%);
  width: 400px;
  height: 140px;
  border-radius: 16px;
  overflow: hidden;
  pointer-events: none;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
`

// ---------------------------------------------------------------------------
// Color interpolation helpers
// ---------------------------------------------------------------------------
function hexToRgb(hex) {
  const n = parseInt(hex.replace('#', ''), 16)
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255]
}

function rgbToHex([r, g, b]) {
  return '#' + [r, g, b].map(v => v.toString(16).padStart(2, '0')).join('')
}

function lerpColor(a, b, t) {
  const ra = hexToRgb(a)
  const rb = hexToRgb(b)
  return rgbToHex(ra.map((v, i) => Math.round(v + (rb[i] - v) * t)))
}

// ---------------------------------------------------------------------------
// Sky gradient calculation
// ---------------------------------------------------------------------------
const SKY_STOPS = [
  { hour: 0,  top: '#0a0e27', bot: '#1a1a4e' },
  { hour: 5,  top: '#0a0e27', bot: '#1a1a4e' },
  { hour: 6,  top: '#1a1a4e', bot: '#ff6b35' },
  { hour: 7,  top: '#ffd700', bot: '#ff6b35' },
  { hour: 8,  top: '#87CEEB', bot: '#a8d8ea' },
  { hour: 12, top: '#4a90d9', bot: '#87CEEB' },
  { hour: 15, top: '#4a90d9', bot: '#6ab0de' },
  { hour: 17, top: '#ff8c00', bot: '#ffa040' },
  { hour: 18, top: '#ff4500', bot: '#ff6b35' },
  { hour: 19, top: '#8b1a1a', bot: '#ff4500' },
  { hour: 20, top: '#2d1b4e', bot: '#8b1a1a' },
  { hour: 21, top: '#2d1b4e', bot: '#1a1a4e' },
  { hour: 24, top: '#0a0e27', bot: '#1a1a4e' },
]

function getSkyGradient(hour, minute) {
  const t = hour + minute / 60
  let lo = SKY_STOPS[0]
  let hi = SKY_STOPS[SKY_STOPS.length - 1]
  for (let i = 0; i < SKY_STOPS.length - 1; i++) {
    if (t >= SKY_STOPS[i].hour && t < SKY_STOPS[i + 1].hour) {
      lo = SKY_STOPS[i]
      hi = SKY_STOPS[i + 1]
      break
    }
  }
  const frac = (hi.hour === lo.hour) ? 0 : (t - lo.hour) / (hi.hour - lo.hour)
  const top = lerpColor(lo.top, hi.top, frac)
  const bot = lerpColor(lo.bot, hi.bot, frac)
  return `linear-gradient(to bottom, ${top}, ${bot})`
}

// ---------------------------------------------------------------------------
// Sun / Moon position along an arc
// ---------------------------------------------------------------------------
function getCelestialPos(hour, minute, width, height) {
  // Sun arc: rises at 6:00 (left edge), peaks at 12:00 (center top), sets at 18:00 (right edge)
  const dayProgress = (hour + minute / 60 - 6) / 12 // 0 at 6:00, 1 at 18:00
  const clampedDay = Math.max(0, Math.min(1, dayProgress))

  // Night arc: moon rises at 18:00, peaks at 0:00, sets at 6:00
  let nightHour = hour + minute / 60
  if (nightHour >= 18) nightHour -= 18
  else nightHour += 6
  const nightProgress = nightHour / 12
  const clampedNight = Math.max(0, Math.min(1, nightProgress))

  const padding = 30
  const arcWidth = width - padding * 2

  const sunX = padding + clampedDay * arcWidth
  const sunY = height - 45 - Math.sin(clampedDay * Math.PI) * (height - 60)

  const moonX = padding + clampedNight * arcWidth
  const moonY = height - 45 - Math.sin(clampedNight * Math.PI) * (height - 60)

  const isDaytime = hour >= 6 && hour < 18
  const sunVisible = hour >= 5 && hour < 19
  const moonVisible = hour >= 18 || hour < 7

  return { sunX, sunY, moonX, moonY, isDaytime, sunVisible, moonVisible }
}

// ---------------------------------------------------------------------------
// City skyline SVG path
// ---------------------------------------------------------------------------
const SKYLINE_PATH = [
  // Start from bottom-left
  'M0,140',
  // Building 1 - short wide
  'L0,105 L15,105 L15,95 L35,95 L35,105 L45,105',
  // Building 2 - medium with flat top
  'L45,80 L55,80 L55,75 L70,75 L70,80 L80,80 L80,105',
  // Building 3 - tall narrow tower with antenna
  'L90,105 L90,60 L95,60 L97,42 L99,60 L104,60 L104,105',
  // Building 4 - medium stepped
  'L115,105 L115,85 L125,85 L125,72 L140,72 L140,85 L150,85 L150,105',
  // Building 5 - short
  'L160,105 L160,92 L180,92 L180,105',
  // Building 6 - tallest skyscraper with spire
  'L190,105 L190,55 L195,55 L198,30 L201,55 L210,55 L210,68 L220,68 L220,105',
  // Building 7 - dome-topped
  'L235,105 L235,78 Q247,60 260,78 L260,105',
  // Building 8 - medium blocky
  'L275,105 L275,82 L285,82 L285,75 L300,75 L300,82 L310,82 L310,105',
  // Building 9 - wide low
  'L325,105 L325,90 L350,90 L350,95 L365,95 L365,105',
  // Building 10 - last one with stepped top
  'L375,105 L375,80 L385,80 L385,70 L395,70 L395,80 L400,80 L400,105',
  // Close the bottom
  'L400,140 Z',
].join(' ')

// ---------------------------------------------------------------------------
// Render
// ---------------------------------------------------------------------------
export const render = ({ output }) => {
  const raw = (output || '').trim()
  const parts = raw.split('|||')
  const time = parts[0] || '--:--:--'
  const dateStr = parts[1] || ''
  const weekday = parts[2] || ''

  const [hhStr, mmStr] = time.split(':')
  const hour = parseInt(hhStr, 10) || 0
  const minute = parseInt(mmStr, 10) || 0

  const skyBg = getSkyGradient(hour, minute)
  const { sunX, sunY, moonX, moonY, sunVisible, moonVisible } = getCelestialPos(hour, minute, 400, 140)

  const containerStyle = {
    position: 'relative',
    width: '400px',
    height: '140px',
    background: skyBg,
    borderRadius: '16px',
    overflow: 'hidden',
  }

  // Sun style
  const sunStyle = {
    position: 'absolute',
    left: sunX - 10,
    top: sunY - 10,
    width: '20px',
    height: '20px',
    borderRadius: '50%',
    background: 'radial-gradient(circle, #fff8a8 30%, #ffd700 60%, rgba(255,180,0,0) 100%)',
    boxShadow: '0 0 18px 8px rgba(255,200,50,0.6), 0 0 40px 15px rgba(255,160,0,0.25)',
    opacity: sunVisible ? 1 : 0,
    transition: 'opacity 0.5s',
    pointerEvents: 'none',
  }

  // Moon crescent - we use two overlapping circles
  const moonStyle = {
    position: 'absolute',
    left: moonX - 9,
    top: moonY - 9,
    width: '18px',
    height: '18px',
    opacity: moonVisible ? 1 : 0,
    transition: 'opacity 0.5s',
    pointerEvents: 'none',
  }

  // Time display
  const timeParts = time.split(':')
  const hh = timeParts[0] || '--'
  const mm = timeParts[1] || '--'
  const ss = timeParts[2] || '--'

  const textLayerStyle = {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 10,
    paddingBottom: '18px',
  }

  const timeStyle = {
    fontSize: '64px',
    fontWeight: 100,
    color: '#ffffff',
    lineHeight: 1,
    textShadow: '0 1px 6px rgba(0,0,0,0.5), 0 0 20px rgba(0,0,0,0.2)',
    letterSpacing: '-2px',
  }

  const secondsStyle = {
    fontSize: '28px',
    fontWeight: 100,
    opacity: 0.5,
    marginLeft: '4px',
    letterSpacing: '0px',
  }

  const dateStyle = {
    fontSize: '12px',
    fontWeight: 300,
    color: 'rgba(255,255,255,0.75)',
    marginTop: '4px',
    textShadow: '0 1px 4px rgba(0,0,0,0.5)',
    letterSpacing: '0.5px',
  }

  // Skyline SVG
  const skylineSvgStyle = {
    position: 'absolute',
    bottom: 0,
    left: 0,
    width: '400px',
    height: '140px',
    zIndex: 5,
    pointerEvents: 'none',
  }

  return (
    <div style={containerStyle}>
      {/* Sun */}
      <div style={sunStyle} />

      {/* Moon crescent via SVG */}
      <div style={moonStyle}>
        <svg width="18" height="18" viewBox="0 0 18 18">
          <circle cx="9" cy="9" r="8" fill="#e8e4d4" />
          <circle cx="13" cy="7" r="7" fill="transparent"
            style={{ filter: 'none' }} />
          <circle cx="13" cy="7" r="7"
            fill={(() => {
              // Match the darker sky color for the "bite" out of the moon
              const t = hour + minute / 60
              let lo = SKY_STOPS[0]
              let hi = SKY_STOPS[SKY_STOPS.length - 1]
              for (let i = 0; i < SKY_STOPS.length - 1; i++) {
                if (t >= SKY_STOPS[i].hour && t < SKY_STOPS[i + 1].hour) {
                  lo = SKY_STOPS[i]
                  hi = SKY_STOPS[i + 1]
                  break
                }
              }
              const frac = (hi.hour === lo.hour) ? 0 : (t - lo.hour) / (hi.hour - lo.hour)
              return lerpColor(lo.top, hi.top, frac)
            })()}
          />
          <circle cx="9" cy="9" r="8" fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth="0.5" />
        </svg>
      </div>

      {/* City skyline silhouette */}
      <svg style={skylineSvgStyle} viewBox="0 0 400 140" preserveAspectRatio="none">
        <path d={SKYLINE_PATH} fill="#000000" />
      </svg>

      {/* Time & date text layer */}
      <div style={textLayerStyle}>
        <div style={timeStyle}>
          {hh}:{mm}
          <span style={secondsStyle}>:{ss}</span>
        </div>
        <div style={dateStyle}>
          {dateStr}  {weekday}
        </div>
      </div>
    </div>
  )
}
