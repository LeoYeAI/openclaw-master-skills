export const command = `
  echo "time:$(date '+%H:%M:%S')"
  echo "weekday:$(date '+%A')"
  echo "datestr:$(date '+%Y年%-m月%-d日')"
`

export const refreshFrequency = 1000

export const className = `
  position: fixed;
  bottom: 90px;
  right: 40px;
  text-align: right;
  pointer-events: none;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
  color: rgba(255, 255, 255, 0.92);
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.6);
`

export const render = ({ output }) => {
  const lines = {}
  ;(output || '').split('\n').forEach(line => {
    const idx = line.indexOf(':')
    if (idx > -1) lines[line.slice(0, idx)] = line.slice(idx + 1)
  })

  const [hh, mm, ss] = (lines.time || '--:--:--').split(':')

  return (
    <div>
      <div style={{
        fontSize: '72px',
        fontWeight: '200',
        letterSpacing: '-3px',
        lineHeight: 1,
      }}>
        {hh}:{mm}
        <span style={{ fontSize: '36px', opacity: 0.5, marginLeft: '6px' }}>:{ss}</span>
      </div>
      <div style={{
        fontSize: '15px',
        opacity: 0.65,
        marginTop: '8px',
        letterSpacing: '0.5px',
      }}>
        {lines.datestr}　{lines.weekday}
      </div>
    </div>
  )
}
