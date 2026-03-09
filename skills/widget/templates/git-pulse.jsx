export const command = `
  # Get commit counts per date for the last 12 weeks
  echo "---COMMITS---"
  find ~ -maxdepth 3 -name ".git" -type d 2>/dev/null | head -10 | while read gitdir; do
    repodir="$(dirname "$gitdir")"
    git -C "$repodir" log --format="%Y-%m-%d" --since="12 weeks ago" 2>/dev/null
  done | sort | uniq -c | awk '{print $1, $2}'

  # Get today's commits per repo for "most active repo"
  echo "---REPOS---"
  today=$(date '+%Y-%m-%d')
  find ~ -maxdepth 3 -name ".git" -type d 2>/dev/null | head -10 | while read gitdir; do
    repodir="$(dirname "$gitdir")"
    reponame="$(basename "$repodir")"
    count=$(git -C "$repodir" log --format="%Y-%m-%d" --since="$today 00:00" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$count" -gt 0 ] 2>/dev/null; then
      echo "$count $reponame"
    fi
  done | sort -rn | head -1

  # Get current branch of the most recently modified repo
  echo "---BRANCH---"
  find ~ -maxdepth 3 -name ".git" -type d 2>/dev/null | head -10 | while read gitdir; do
    repodir="$(dirname "$gitdir")"
    modtime=$(stat -f "%m" "$repodir/.git" 2>/dev/null || echo "0")
    echo "$modtime $repodir"
  done | sort -rn | head -1 | awk '{print $2}' | while read repodir; do
    git -C "$repodir" branch --show-current 2>/dev/null
  done
`

export const refreshFrequency = 300000

export const className = `
  position: fixed;
  top: 40px;
  right: 40px;
  font-family: -apple-system, BlinkMacSystemFont, 'SF Mono', 'Menlo', monospace;
  pointer-events: none;
`

const WEEKS = 12
const DAYS_TOTAL = WEEKS * 7
const CELL_SIZE = 12
const CELL_GAP = 3
const DAY_LABELS = ['Mon', '', 'Wed', '', 'Fri', '', '']
const MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

const getColor = (count) => {
  if (count <= 0) return 'rgba(255,255,255,0.05)'
  if (count <= 2) return '#0e4429'
  if (count <= 5) return '#006d32'
  if (count <= 9) return '#26a641'
  return '#39d353'
}

const parseOutput = (raw) => {
  const result = {
    commits: {},
    topRepo: '',
    todayRepoCount: 0,
    branch: '',
  }
  if (!raw) return result

  const text = raw.trim()
  const commitSection = text.split('---COMMITS---')[1]?.split('---REPOS---')[0] || ''
  const repoSection = text.split('---REPOS---')[1]?.split('---BRANCH---')[0] || ''
  const branchSection = text.split('---BRANCH---')[1] || ''

  // Parse commit counts
  commitSection.trim().split('\n').forEach(line => {
    const trimmed = line.trim()
    if (!trimmed) return
    const parts = trimmed.split(/\s+/)
    if (parts.length >= 2) {
      const count = parseInt(parts[0], 10)
      const date = parts[1]
      if (!isNaN(count) && /^\d{4}-\d{2}-\d{2}$/.test(date)) {
        result.commits[date] = (result.commits[date] || 0) + count
      }
    }
  })

  // Parse top repo
  const repoLine = repoSection.trim().split('\n')[0]?.trim()
  if (repoLine) {
    const parts = repoLine.split(/\s+/)
    if (parts.length >= 2) {
      result.todayRepoCount = parseInt(parts[0], 10) || 0
      result.topRepo = parts.slice(1).join(' ')
    }
  }

  // Parse branch
  result.branch = branchSection.trim().split('\n')[0]?.trim() || ''

  return result
}

const formatDate = (d) => {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

// Convert JS getDay (0=Sun) to row index (0=Mon, 6=Sun)
const jsToRow = (jsDay) => jsDay === 0 ? 6 : jsDay - 1

const buildGrid = (commits) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const todayRow = jsToRow(today.getDay())

  // The rightmost column (col = WEEKS-1) contains today.
  // We need to find the Saturday (or Sunday) that starts the first column.
  // Going back from today: the last column started on the Monday of this week.
  // Today is at row=todayRow in col=WEEKS-1.
  // The first day on the grid is at row=0, col=0 (a Monday).
  // Days back from today to that Monday:
  //   (WEEKS - 1) * 7 + todayRow
  const daysBack = (WEEKS - 1) * 7 + todayRow

  const grid = []
  for (let r = 0; r < 7; r++) {
    grid[r] = []
    for (let c = 0; c < WEEKS; c++) {
      grid[r][c] = { date: null, count: 0 }
    }
  }

  const monthLabels = []
  const seenMonths = new Set()

  // Fill grid: iterate each cell by (col, row) order
  // offset=0 corresponds to the earliest date (row=0, col=0), which is a Monday
  // offset=daysBack corresponds to today
  for (let col = 0; col < WEEKS; col++) {
    for (let row = 0; row < 7; row++) {
      const offset = col * 7 + row
      // Cells beyond today in the last partial column are future dates
      if (offset > daysBack) continue
      const d = new Date(today)
      d.setDate(today.getDate() - (daysBack - offset))
      const dateStr = formatDate(d)
      grid[row][col] = { date: dateStr, count: commits[dateStr] || 0 }

      // Track month boundaries (when row=0, i.e. Monday of each week)
      if (row === 0) {
        const monthKey = `${d.getFullYear()}-${d.getMonth()}`
        if (!seenMonths.has(monthKey)) {
          seenMonths.add(monthKey)
          monthLabels.push({ col, label: MONTH_NAMES[d.getMonth()] })
        }
      }
    }
  }

  return { grid, monthLabels }
}

const computeStats = (commits) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const todayStr = formatDate(today)
  const todayCount = commits[todayStr] || 0

  // Calculate streak: consecutive days with commits ending at today (or yesterday if today has 0)
  let streak = 0
  let checkDate = new Date(today)
  if (!commits[todayStr]) {
    checkDate.setDate(checkDate.getDate() - 1)
  }
  for (let i = 0; i < DAYS_TOTAL; i++) {
    const ds = formatDate(checkDate)
    if (commits[ds] && commits[ds] > 0) {
      streak++
      checkDate.setDate(checkDate.getDate() - 1)
    } else {
      break
    }
  }

  // Total commits in 12 weeks
  let total = 0
  Object.values(commits).forEach(c => { total += c })

  return { todayCount, streak, total }
}

const GitPulseInner = ({ output }) => {
  const data = parseOutput(output)
  const { grid, monthLabels } = buildGrid(data.commits)
  const stats = computeStats(data.commits)

  const labelWidth = 28
  const gridWidth = WEEKS * (CELL_SIZE + CELL_GAP) - CELL_GAP
  const monthLabelHeight = 16

  return (
    <div style={{
      background: 'rgba(0, 0, 0, 0.5)',
      backdropFilter: 'blur(24px)',
      WebkitBackdropFilter: 'blur(24px)',
      borderRadius: '16px',
      border: '1px solid rgba(255,255,255,0.08)',
      padding: '16px 18px 14px',
      color: 'rgba(255,255,255,0.9)',
      minWidth: `${labelWidth + gridWidth + 20}px`,
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '12px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: stats.todayCount > 0 ? '#39d353' : 'rgba(255,255,255,0.2)',
            boxShadow: stats.todayCount > 0 ? '0 0 6px rgba(57,211,83,0.5)' : 'none',
          }} />
          <span style={{
            fontSize: '12px',
            fontWeight: 600,
            letterSpacing: '0.5px',
            color: 'rgba(255,255,255,0.8)',
          }}>
            Git Pulse
          </span>
          {data.branch && (
            <span style={{
              fontSize: '10px',
              color: 'rgba(255,255,255,0.35)',
              background: 'rgba(255,255,255,0.06)',
              padding: '2px 6px',
              borderRadius: '4px',
            }}>
              {data.branch}
            </span>
          )}
        </div>
        <div style={{
          fontSize: '11px',
          color: stats.streak > 0 ? '#39d353' : 'rgba(255,255,255,0.35)',
          fontWeight: 600,
        }}>
          {stats.streak > 0 ? `${stats.streak}d streak` : 'no streak'}
        </div>
      </div>

      {/* Month labels */}
      <div style={{
        display: 'flex',
        marginLeft: `${labelWidth}px`,
        marginBottom: '4px',
        height: `${monthLabelHeight}px`,
        position: 'relative',
        width: `${gridWidth}px`,
      }}>
        {monthLabels.map((m, i) => (
          <span key={i} style={{
            position: 'absolute',
            left: `${m.col * (CELL_SIZE + CELL_GAP)}px`,
            fontSize: '9px',
            color: 'rgba(255,255,255,0.3)',
            letterSpacing: '0.3px',
          }}>
            {m.label}
          </span>
        ))}
      </div>

      {/* Heatmap grid */}
      <div style={{ display: 'flex', gap: '0px' }}>
        {/* Day labels */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: `${CELL_GAP}px`,
          marginRight: '4px',
          width: `${labelWidth - 4}px`,
        }}>
          {DAY_LABELS.map((label, i) => (
            <div key={i} style={{
              height: `${CELL_SIZE}px`,
              fontSize: '9px',
              color: 'rgba(255,255,255,0.25)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              paddingRight: '4px',
            }}>
              {label}
            </div>
          ))}
        </div>

        {/* Grid columns */}
        <div style={{ display: 'flex', gap: `${CELL_GAP}px` }}>
          {Array.from({ length: WEEKS }, (_, col) => (
            <div key={col} style={{ display: 'flex', flexDirection: 'column', gap: `${CELL_GAP}px` }}>
              {Array.from({ length: 7 }, (_, row) => {
                const cell = grid[row][col]
                const color = getColor(cell.count)
                return (
                  <div key={row} style={{
                    width: `${CELL_SIZE}px`,
                    height: `${CELL_SIZE}px`,
                    borderRadius: '2px',
                    background: color,
                    transition: 'background 0.3s ease',
                  }} />
                )
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: '12px',
        paddingTop: '10px',
        borderTop: '1px solid rgba(255,255,255,0.06)',
      }}>
        <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.5)' }}>
          <span style={{ color: 'rgba(255,255,255,0.8)', fontWeight: 600 }}>{stats.todayCount}</span>
          <span> commit{stats.todayCount !== 1 ? 's' : ''} today</span>
        </div>
        <div style={{ fontSize: '10px', color: 'rgba(255,255,255,0.3)' }}>
          {data.topRepo
            ? <span>{data.topRepo}</span>
            : <span>{stats.total} in 12w</span>
          }
        </div>
      </div>

      {/* Legend */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        gap: '4px',
        marginTop: '8px',
      }}>
        <span style={{ fontSize: '9px', color: 'rgba(255,255,255,0.25)', marginRight: '4px' }}>Less</span>
        {[0, 1, 3, 6, 10].map((level, i) => (
          <div key={i} style={{
            width: '8px',
            height: '8px',
            borderRadius: '2px',
            background: getColor(level),
          }} />
        ))}
        <span style={{ fontSize: '9px', color: 'rgba(255,255,255,0.25)', marginLeft: '4px' }}>More</span>
      </div>
    </div>
  )
}

export const render = ({ output }) => {
  return <GitPulseInner output={output} />
}
