import { React } from 'uebersicht'

export const command = `
  DATA=$(curl -s --max-time 8 "wttr.in/?format=j1" 2>/dev/null)
  if [ -z "$DATA" ]; then
    echo "temp:--"
    echo "feels:--"
    echo "humidity:--"
    echo "wind:--"
    echo "code:113"
    echo "desc:Unknown"
  else
    TEMP=$(echo "$DATA" | /usr/bin/python3 -c "import sys,json; d=json.load(sys.stdin); print(d['current_condition'][0]['temp_C'])" 2>/dev/null || echo "--")
    FEELS=$(echo "$DATA" | /usr/bin/python3 -c "import sys,json; d=json.load(sys.stdin); print(d['current_condition'][0]['FeelsLikeC'])" 2>/dev/null || echo "--")
    HUMIDITY=$(echo "$DATA" | /usr/bin/python3 -c "import sys,json; d=json.load(sys.stdin); print(d['current_condition'][0]['humidity'])" 2>/dev/null || echo "--")
    WIND=$(echo "$DATA" | /usr/bin/python3 -c "import sys,json; d=json.load(sys.stdin); print(d['current_condition'][0]['windspeedKmph'])" 2>/dev/null || echo "--")
    CODE=$(echo "$DATA" | /usr/bin/python3 -c "import sys,json; d=json.load(sys.stdin); print(d['current_condition'][0]['weatherCode'])" 2>/dev/null || echo "113")
    DESC=$(echo "$DATA" | /usr/bin/python3 -c "import sys,json; d=json.load(sys.stdin); print(d['current_condition'][0]['weatherDesc'][0]['value'])" 2>/dev/null || echo "Unknown")
    echo "temp:$TEMP"
    echo "feels:$FEELS"
    echo "humidity:$HUMIDITY"
    echo "wind:$WIND"
    echo "code:$CODE"
    echo "desc:$DESC"
  fi
`

export const refreshFrequency = 600000

export const className = `
  position: fixed;
  top: 40px;
  left: 40px;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
  pointer-events: none;
`

const parseOutput = (raw) => {
  const result = { temp: '--', feels: '--', humidity: '--', wind: '--', code: '113', desc: 'Unknown' }
  if (!raw) return result
  raw.trim().split('\n').forEach(line => {
    const idx = line.indexOf(':')
    if (idx > -1) {
      const key = line.slice(0, idx).trim()
      const val = line.slice(idx + 1).trim()
      if (result.hasOwnProperty(key)) result[key] = val
    }
  })
  return result
}

const classifyWeather = (code) => {
  const codeNum = parseInt(code) || 113
  const rainCodes = [176, 293, 296, 299, 302, 305, 308]
  const snowCodes = [227, 230, 323, 326, 329, 332, 335, 338]
  const cloudyCodes = [119, 122]

  if (rainCodes.includes(codeNum)) return 'rain'
  if (snowCodes.includes(codeNum)) return 'snow'
  if (cloudyCodes.includes(codeNum)) return 'cloudy'
  if (codeNum === 116) return 'partly-cloudy'
  return 'sunny'
}

const getGradient = (weather) => {
  switch (weather) {
    case 'rain':
      return 'linear-gradient(160deg, rgba(40, 50, 70, 0.85), rgba(30, 40, 60, 0.9))'
    case 'snow':
      return 'linear-gradient(160deg, rgba(50, 60, 90, 0.85), rgba(40, 50, 80, 0.9))'
    case 'cloudy':
      return 'linear-gradient(160deg, rgba(55, 60, 70, 0.85), rgba(40, 45, 55, 0.9))'
    case 'partly-cloudy':
      return 'linear-gradient(160deg, rgba(50, 55, 75, 0.85), rgba(45, 50, 65, 0.9))'
    default: // sunny
      return 'linear-gradient(160deg, rgba(60, 45, 30, 0.85), rgba(50, 35, 25, 0.9))'
  }
}

const getAccentColor = (weather) => {
  switch (weather) {
    case 'rain':    return 'rgba(100, 160, 220, 0.8)'
    case 'snow':    return 'rgba(160, 190, 240, 0.8)'
    case 'cloudy':  return 'rgba(140, 155, 170, 0.7)'
    case 'partly-cloudy': return 'rgba(180, 180, 200, 0.7)'
    default:        return 'rgba(255, 200, 100, 0.8)'
  }
}

// Keyframes CSS injected via <style>
const keyframesCSS = `
@keyframes wc-raindrop {
  0% {
    transform: translateY(-20px) translateX(0px);
    opacity: 0;
  }
  10% {
    opacity: 0.7;
  }
  90% {
    opacity: 0.5;
  }
  100% {
    transform: translateY(200px) translateX(-15px);
    opacity: 0;
  }
}

@keyframes wc-snowflake {
  0% {
    transform: translateY(-20px) translateX(0px) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 0.8;
  }
  50% {
    transform: translateY(90px) translateX(20px) rotate(180deg);
    opacity: 0.6;
  }
  90% {
    opacity: 0.3;
  }
  100% {
    transform: translateY(200px) translateX(-10px) rotate(360deg);
    opacity: 0;
  }
}

@keyframes wc-sun-glow {
  0% {
    transform: scale(1);
    opacity: 0.15;
  }
  50% {
    transform: scale(1.3);
    opacity: 0.35;
  }
  100% {
    transform: scale(1);
    opacity: 0.15;
  }
}

@keyframes wc-sun-particle {
  0% {
    transform: translateY(0px) scale(0.8);
    opacity: 0;
  }
  30% {
    opacity: 0.5;
  }
  70% {
    opacity: 0.3;
  }
  100% {
    transform: translateY(-40px) scale(0.2);
    opacity: 0;
  }
}

@keyframes wc-cloud-drift {
  0% {
    transform: translateX(-30px);
    opacity: 0;
  }
  20% {
    opacity: 0.35;
  }
  80% {
    opacity: 0.25;
  }
  100% {
    transform: translateX(230px);
    opacity: 0;
  }
}

@keyframes wc-cloud-pulse {
  0% {
    opacity: 0.15;
    transform: scale(1);
  }
  50% {
    opacity: 0.3;
    transform: scale(1.08);
  }
  100% {
    opacity: 0.15;
    transform: scale(1);
  }
}
`

const makeRainParticles = (count) => {
  return Array.from({ length: count }, (_, index) => {
    const left = Math.random() * 100
    const delay = Math.random() * 3
    const duration = 0.8 + Math.random() * 0.6
    const width = 1 + Math.random() * 1.5
    const height = 12 + Math.random() * 18
    const opacity = 0.3 + Math.random() * 0.4
    return (
      <div key={`rain-${index}`} style={{
        position: 'absolute',
        left: `${left}%`,
        top: '-10px',
        width: `${width}px`,
        height: `${height}px`,
        background: `linear-gradient(180deg, rgba(120, 180, 240, ${opacity}), rgba(80, 140, 220, 0.1))`,
        borderRadius: '1px',
        animation: `wc-raindrop ${duration}s ${delay}s linear infinite`,
        opacity: 0,
      }} />
    )
  })
}

const makeSnowParticles = (count) => {
  return Array.from({ length: count }, (_, index) => {
    const left = Math.random() * 100
    const delay = Math.random() * 5
    const duration = 3 + Math.random() * 4
    const size = 2 + Math.random() * 4
    const opacity = 0.3 + Math.random() * 0.5
    return (
      <div key={`snow-${index}`} style={{
        position: 'absolute',
        left: `${left}%`,
        top: '-10px',
        width: `${size}px`,
        height: `${size}px`,
        background: `rgba(220, 230, 255, ${opacity})`,
        borderRadius: '50%',
        boxShadow: `0 0 ${size * 2}px rgba(200, 215, 255, ${opacity * 0.5})`,
        animation: `wc-snowflake ${duration}s ${delay}s ease-in-out infinite`,
        opacity: 0,
      }} />
    )
  })
}

const makeSunParticles = (count) => {
  const particles = []
  // Central glow orbs
  particles.push(
    <div key="sun-glow-1" style={{
      position: 'absolute',
      top: '10px',
      right: '10px',
      width: '60px',
      height: '60px',
      borderRadius: '50%',
      background: 'radial-gradient(circle, rgba(255, 200, 80, 0.4), transparent 70%)',
      animation: 'wc-sun-glow 4s ease-in-out infinite',
    }} />
  )
  particles.push(
    <div key="sun-glow-2" style={{
      position: 'absolute',
      top: '20px',
      right: '20px',
      width: '40px',
      height: '40px',
      borderRadius: '50%',
      background: 'radial-gradient(circle, rgba(255, 180, 60, 0.3), transparent 70%)',
      animation: 'wc-sun-glow 3s 1s ease-in-out infinite',
    }} />
  )
  // Floating warm particles
  for (let index = 0; index < count; index++) {
    const left = 50 + Math.random() * 50
    const top = Math.random() * 60
    const delay = Math.random() * 4
    const duration = 3 + Math.random() * 3
    const size = 2 + Math.random() * 3
    particles.push(
      <div key={`sun-p-${index}`} style={{
        position: 'absolute',
        left: `${left}%`,
        top: `${top}%`,
        width: `${size}px`,
        height: `${size}px`,
        borderRadius: '50%',
        background: `rgba(255, 210, 100, ${0.2 + Math.random() * 0.3})`,
        boxShadow: `0 0 ${size * 3}px rgba(255, 190, 70, 0.3)`,
        animation: `wc-sun-particle ${duration}s ${delay}s ease-out infinite`,
        opacity: 0,
      }} />
    )
  }
  return particles
}

const makeCloudParticles = (count) => {
  const particles = []
  // Drifting clouds
  for (let index = 0; index < Math.min(count, 8); index++) {
    const top = 10 + Math.random() * 60
    const delay = Math.random() * 12
    const duration = 10 + Math.random() * 10
    const height = 6 + Math.random() * 10
    const width = 30 + Math.random() * 40
    const opacity = 0.1 + Math.random() * 0.2
    particles.push(
      <div key={`cloud-d-${index}`} style={{
        position: 'absolute',
        left: '-30px',
        top: `${top}%`,
        width: `${width}px`,
        height: `${height}px`,
        borderRadius: '50%',
        background: `rgba(180, 190, 210, ${opacity})`,
        filter: `blur(${3 + Math.random() * 4}px)`,
        animation: `wc-cloud-drift ${duration}s ${delay}s linear infinite`,
        opacity: 0,
      }} />
    )
  }
  // Pulsing haze patches
  for (let index = 0; index < count - 8; index++) {
    const left = Math.random() * 80
    const top = Math.random() * 70
    const delay = Math.random() * 5
    const duration = 4 + Math.random() * 4
    const size = 15 + Math.random() * 25
    particles.push(
      <div key={`cloud-p-${index}`} style={{
        position: 'absolute',
        left: `${left}%`,
        top: `${top}%`,
        width: `${size}px`,
        height: `${size * 0.6}px`,
        borderRadius: '50%',
        background: `rgba(160, 175, 200, ${0.08 + Math.random() * 0.12})`,
        filter: `blur(${4 + Math.random() * 3}px)`,
        animation: `wc-cloud-pulse ${duration}s ${delay}s ease-in-out infinite`,
      }} />
    )
  }
  return particles
}

const getParticles = (weather) => {
  switch (weather) {
    case 'rain':          return makeRainParticles(28)
    case 'snow':          return makeSnowParticles(24)
    case 'cloudy':        return makeCloudParticles(20)
    case 'partly-cloudy': return makeCloudParticles(14)
    default:              return makeSunParticles(20)
  }
}

const WeatherCanvas = ({ output }) => {
  const { useEffect, useRef } = React
  const styleRef = useRef(null)

  // Inject keyframes into document once
  useEffect(() => {
    if (!document.getElementById('wc-keyframes-style')) {
      const styleEl = document.createElement('style')
      styleEl.id = 'wc-keyframes-style'
      styleEl.textContent = keyframesCSS
      document.head.appendChild(styleEl)
      styleRef.current = styleEl
    }
    return () => {
      const el = document.getElementById('wc-keyframes-style')
      if (el) el.remove()
    }
  }, [])

  const data = parseOutput(output)
  const weather = classifyWeather(data.code)
  const gradient = getGradient(weather)
  const accent = getAccentColor(weather)
  const particles = getParticles(weather)

  return (
    <div style={{
      position: 'relative',
      width: '200px',
      height: '180px',
      background: gradient,
      backdropFilter: 'blur(24px)',
      WebkitBackdropFilter: 'blur(24px)',
      borderRadius: '18px',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      boxShadow: '0 12px 40px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.06)',
      overflow: 'hidden',
      padding: '18px 20px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
    }}>
      {/* Particle layer */}
      <div style={{
        position: 'absolute',
        inset: 0,
        overflow: 'hidden',
        borderRadius: '18px',
        pointerEvents: 'none',
      }}>
        {particles}
      </div>

      {/* Content layer */}
      <div style={{ position: 'relative', zIndex: 1 }}>
        {/* Weather description */}
        <div style={{
          fontSize: '11px',
          letterSpacing: '1px',
          color: accent,
          textTransform: 'uppercase',
          fontWeight: 500,
          marginBottom: '4px',
        }}>
          {data.desc}
        </div>

        {/* Temperature */}
        <div style={{
          fontSize: '72px',
          fontWeight: 100,
          lineHeight: 1,
          color: 'rgba(255, 255, 255, 0.92)',
          letterSpacing: '-4px',
          textShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
        }}>
          {data.temp}
          <span style={{
            fontSize: '28px',
            fontWeight: 200,
            opacity: 0.5,
            letterSpacing: '0px',
            marginLeft: '2px',
            verticalAlign: 'top',
            lineHeight: '1.2',
            display: 'inline-block',
          }}>
            °
          </span>
        </div>
      </div>

      {/* Bottom info row */}
      <div style={{
        position: 'relative',
        zIndex: 1,
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '10px',
        color: 'rgba(255, 255, 255, 0.4)',
        letterSpacing: '0.3px',
      }}>
        <span>
          Feels {data.feels}°
        </span>
        <span>
          {data.humidity}%
        </span>
        <span>
          {data.wind}km/h
        </span>
      </div>
    </div>
  )
}

export const render = ({ output }) => <WeatherCanvas output={output} />
