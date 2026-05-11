# Dashboard Templates

HTML/CSS templates and components for dashboard generation.

## Color Scheme (Dark Theme)

```css
/* Primary Colors */
--bg-primary: #1a1a2e;
--bg-secondary: #0f0f1e;
--bg-card: rgba(255, 255, 255, 0.05);
--border-color: rgba(255, 255, 255, 0.1);

/* Text Colors */
--text-primary: #e0e0e0;
--text-secondary: #aaa;
--text-muted: #666;

/* Accent Colors */
--accent-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--accent-purple: #667eea;
--accent-violet: #764ba2;

/* Status Colors */
--status-ok: #10b981;
--status-warning: #f59e0b;
--status-error: #ef4444;
--status-info: #3b82f6;
```

## Card Component (CSS)

```css
.card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-icon {
  font-size: 1.5em;
  margin-right: 10px;
}

.card-title {
  font-size: 1.2em;
  font-weight: 600;
}
```

## Progress Bar (Pure CSS)

```html
<div class="progress-bar">
  <div class="progress-fill" style="width: 75%">75%</div>
</div>

<style>
.progress-bar {
  width: 100%;
  height: 24px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  overflow: hidden;
  margin: 10px 0;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 0.85em;
  font-weight: 600;
}
</style>
```

## Status Badge (CSS)

```html
<span class="status-badge status-ok">Healthy</span>
<span class="status-badge status-warning">Warning</span>
<span class="status-badge status-error">Error</span>
<span class="status-badge status-info">Info</span>

<style>
.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 600;
}

.status-ok { background: #10b981; color: #fff; }
.status-warning { background: #f59e0b; color: #fff; }
.status-error { background: #ef4444; color: #fff; }
.status-info { background: #3b82f6; color: #fff; }
</style>
```

## Pie Chart (Pure SVG)

```html
<svg viewBox="0 0 32 32" class="pie-chart">
  <!-- Background circle -->
  <circle r="16" cx="16" cy="16" fill="#1a1a2e" />
  
  <!-- Segment 1: 75% (stroke-dasharray: percentage 100-percentage) -->
  <circle r="5" cx="16" cy="16" 
    fill="transparent"
    stroke="#667eea"
    stroke-width="10"
    stroke-dasharray="75 25"
    transform="rotate(-90 16 16)" />
  
  <!-- Segment 2: 25% starts at 75% -->
  <circle r="5" cx="16" cy="16" 
    fill="transparent"
    stroke="#764ba2"
    stroke-width="10"
    stroke-dasharray="25 75"
    transform="rotate(180 16 16)" />
</svg>

<style>
.pie-chart {
  width: 100px;
  height: 100px;
}
</style>
```

## Bar Chart (Pure CSS)

```html
<div class="bar-chart">
  <div class="bar-item">
    <div class="bar-label">Movies</div>
    <div class="bar-container">
      <div class="bar-fill" style="width: 80%">1,234</div>
    </div>
  </div>
  <div class="bar-item">
    <div class="bar-label">TV Shows</div>
    <div class="bar-container">
      <div class="bar-fill" style="width: 60%">892</div>
    </div>
  </div>
  <div class="bar-item">
    <div class="bar-label">Music</div>
    <div class="bar-container">
      <div class="bar-fill" style="width: 40%">567</div>
    </div>
  </div>
</div>

<style>
.bar-chart {
  margin: 20px 0;
}

.bar-item {
  margin-bottom: 15px;
}

.bar-label {
  color: #aaa;
  font-size: 0.9em;
  margin-bottom: 5px;
}

.bar-container {
  width: 100%;
  height: 30px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  padding-left: 10px;
  color: #fff;
  font-weight: 600;
  font-size: 0.9em;
  transition: width 0.3s ease;
}
</style>
```

## Metric Card (Large Number Display)

```html
<div class="metric-card">
  <div class="metric-big">1,234</div>
  <div class="metric-label">Total Movies</div>
  <div class="metric-change positive">+12 this week</div>
</div>

<style>
.metric-card {
  text-align: center;
  padding: 20px;
}

.metric-big {
  font-size: 3em;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 10px;
}

.metric-label {
  color: #aaa;
  font-size: 0.9em;
  margin-bottom: 5px;
}

.metric-change {
  font-size: 0.85em;
  font-weight: 600;
}

.metric-change.positive { color: #10b981; }
.metric-change.negative { color: #ef4444; }
</style>
```

## Grid Layout

```css
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

/* Responsive breakpoints */
@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 1200px) {
  .grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

## Stat Row (Key-Value Pair)

```html
<div class="stat-row">
  <span class="stat-label">Total Episodes</span>
  <span class="stat-value">4,567</span>
</div>

<style>
.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-label {
  color: #aaa;
}

.stat-value {
  font-weight: 600;
  color: #fff;
}
```

## Loading Spinner (Pure CSS)

```html
<div class="spinner"></div>

<style>
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
```

## Timeline Component

```html
<div class="timeline">
  <div class="timeline-item">
    <div class="timeline-marker"></div>
    <div class="timeline-content">
      <div class="timeline-time">2 hours ago</div>
      <div class="timeline-text">Movie added: Dune Part Two</div>
    </div>
  </div>
  <div class="timeline-item">
    <div class="timeline-marker"></div>
    <div class="timeline-content">
      <div class="timeline-time">5 hours ago</div>
      <div class="timeline-text">Episode downloaded: Foundation S02E08</div>
    </div>
  </div>
</div>

<style>
.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: rgba(255, 255, 255, 0.1);
}

.timeline-item {
  position: relative;
  margin-bottom: 20px;
}

.timeline-marker {
  position: absolute;
  left: -26px;
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #667eea;
  border: 2px solid #1a1a2e;
}

.timeline-content {
  padding-left: 10px;
}

.timeline-time {
  color: #888;
  font-size: 0.85em;
  margin-bottom: 4px;
}

.timeline-text {
  color: #e0e0e0;
}
</style>
```

## Responsive Dashboard Shell

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ClawARR Dashboard</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #1a1a2e 0%, #0f0f1e 100%);
      color: #e0e0e0;
      padding: 20px;
      min-height: 100vh;
    }
    
    .container {
      max-width: 1400px;
      margin: 0 auto;
    }
    
    header {
      text-align: center;
      margin-bottom: 30px;
      padding: 20px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    h1 {
      font-size: 2.5em;
      margin-bottom: 10px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    
    .section {
      margin-bottom: 40px;
    }
    
    .section-title {
      font-size: 1.5em;
      margin-bottom: 15px;
      padding-left: 10px;
      border-left: 4px solid #667eea;
    }
    
    footer {
      text-align: center;
      padding: 20px;
      color: #666;
      font-size: 0.9em;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>📊 ClawARR Dashboard</h1>
      <p>Media Stack Monitoring</p>
    </header>
    
    <div class="section">
      <h2 class="section-title">Your Content Here</h2>
      <!-- Cards, charts, stats go here -->
    </div>
    
    <footer>
      <p>ClawARR Suite Dashboard • Auto-generated</p>
    </footer>
  </div>
</body>
</html>
```

## Usage in Scripts

When generating dashboards from bash scripts:

1. **Inline all CSS** - No external stylesheets
2. **No CDN dependencies** - Self-contained HTML
3. **Use data URIs for images** if needed (base64 encoded)
4. **Fallback fonts** - Use system font stack
5. **Progressive enhancement** - Work without JavaScript

Example placeholder replacement pattern:
```bash
cat > output.html << 'EOF'
<div class="stat-value">PLACEHOLDER_VALUE</div>
EOF

sed -i '' "s/PLACEHOLDER_VALUE/$actual_value/g" output.html
```

## Accessibility Considerations

- Use semantic HTML tags (`<header>`, `<section>`, `<footer>`)
- Ensure sufficient color contrast (WCAG AA: 4.5:1 for normal text)
- Provide text alternatives for visual data (e.g., table fallback for charts)
- Support keyboard navigation where applicable
- Responsive design for mobile/tablet viewing

## Browser Compatibility

These templates are tested and work in:
- Safari 14+
- Chrome 90+
- Firefox 88+
- Edge 90+

All styles use standard CSS (no vendor prefixes needed for modern browsers).
