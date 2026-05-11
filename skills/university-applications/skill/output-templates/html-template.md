# HTML Webpage Output Template

## Instructions

Generate a fully responsive, interactive HTML webpage with search, filter, and sort capabilities. This is the richest output format with the best user experience.

## Features

- 🔍 Real-time search across all fields
- 🏫 Filter by university
- 📚 Filter by degree type
- 💰 Sort by tuition fee
- 📅 Sort by deadline
- 📱 Responsive design (mobile-friendly)
- 🌙 Dark mode toggle
- 📊 Interactive statistics dashboard
- 🔗 Direct links to official program pages

## Output Format

Generate a complete, self-contained HTML file (no external dependencies):

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HK University Master's Admissions</title>
<style>
  /* === CSS Reset === */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  /* === CSS Variables === */
  :root {
    --primary: #1a237e;
    --primary-light: #3f51b5;
    --primary-bg: #e8eaf6;
    --accent: #ff6f00;
    --bg: #f5f5f5;
    --card-bg: #ffffff;
    --text: #333333;
    --text-light: #666666;
    --border: #e0e0e0;
    --success: #2e7d32;
    --warning: #f57c00;
    --radius: 8px;
    --shadow: 0 2px 8px rgba(0,0,0,0.1);
  }
  [data-theme="dark"] {
    --primary: #7986cb;
    --primary-light: #9fa8da;
    --primary-bg: #1a1a2e;
    --bg: #121212;
    --card-bg: #1e1e1e;
    --text: #e0e0e0;
    --text-light: #aaaaaa;
    --border: #333333;
    --shadow: 0 2px 8px rgba(0,0,0,0.3);
  }

  /* === Layout === */
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Microsoft YaHei', sans-serif;
    background: var(--bg); color: var(--text);
    line-height: 1.6; font-size: 14px;
  }

  /* Header */
  .header {
    background: var(--primary); color: white;
    padding: 30px 20px; text-align: center;
  }
  .header h1 { font-size: 2em; margin-bottom: 5px; }
  .header p { opacity: 0.85; font-size: 1.1em; }

  /* Container */
  .container { max-width: 1400px; margin: 0 auto; padding: 20px; }

  /* Stats Dashboard */
  .stats-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px; margin: 20px 0;
  }
  .stat-card {
    background: var(--card-bg); border-radius: var(--radius);
    padding: 20px; text-align: center; box-shadow: var(--shadow);
    border-top: 3px solid var(--primary-light);
  }
  .stat-card .number { font-size: 2em; font-weight: 700; color: var(--primary); }
  .stat-card .label { font-size: 0.85em; color: var(--text-light); text-transform: uppercase; }

  /* Controls */
  .controls {
    background: var(--card-bg); border-radius: var(--radius);
    padding: 20px; margin: 20px 0; box-shadow: var(--shadow);
    display: flex; flex-wrap: wrap; gap: 15px; align-items: center;
  }
  .search-box {
    flex: 1; min-width: 250px; padding: 10px 15px;
    border: 2px solid var(--border); border-radius: var(--radius);
    font-size: 1em; background: var(--bg); color: var(--text);
  }
  .search-box:focus { border-color: var(--primary-light); outline: none; }
  select {
    padding: 10px 15px; border: 2px solid var(--border);
    border-radius: var(--radius); font-size: 0.95em;
    background: var(--bg); color: var(--text); cursor: pointer;
  }
  .btn {
    padding: 10px 20px; border: none; border-radius: var(--radius);
    cursor: pointer; font-size: 0.95em; font-weight: 600; transition: all 0.2s;
  }
  .btn-primary { background: var(--primary); color: white; }
  .btn-primary:hover { background: var(--primary-light); }

  /* Program Cards */
  .programs-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    gap: 20px; margin: 20px 0;
  }
  .program-card {
    background: var(--card-bg); border-radius: var(--radius);
    box-shadow: var(--shadow); overflow: hidden; transition: transform 0.2s;
  }
  .program-card:hover { transform: translateY(-3px); box-shadow: 0 4px 16px rgba(0,0,0,0.15); }
  .card-header {
    background: var(--primary); color: white; padding: 15px 20px;
  }
  .card-header h3 { font-size: 1.05em; margin-bottom: 3px; }
  .card-header .uni-name { font-size: 0.85em; opacity: 0.85; }
  .card-body { padding: 15px 20px; }
  .card-row {
    display: flex; justify-content: space-between;
    padding: 6px 0; border-bottom: 1px solid var(--border);
    font-size: 0.9em;
  }
  .card-row:last-child { border-bottom: none; }
  .card-label { font-weight: 600; color: var(--text-light); min-width: 120px; }
  .card-value { text-align: right; flex: 1; }
  .card-footer { padding: 12px 20px; background: var(--primary-bg); text-align: center; }
  .card-footer a {
    color: var(--primary); font-weight: 600; text-decoration: none;
  }
  .card-footer a:hover { text-decoration: underline; }

  /* Tags */
  .tag {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 0.8em; font-weight: 600; margin: 2px;
  }
  .tag-ft { background: #e8f5e9; color: #2e7d32; }
  .tag-pt { background: #fff3e0; color: #e65100; }
  .tag-degree { background: var(--primary-bg); color: var(--primary); }

  /* University comparison table */
  .comparison-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
  .comparison-table th {
    background: var(--primary); color: white; padding: 10px 12px;
    text-align: left; position: sticky; top: 0;
  }
  .comparison-table td { padding: 8px 12px; border-bottom: 1px solid var(--border); }
  .comparison-table tr:hover { background: var(--primary-bg); }

  /* Dark mode toggle */
  .theme-toggle {
    position: fixed; bottom: 20px; right: 20px;
    width: 50px; height: 50px; border-radius: 50%;
    background: var(--primary); color: white; border: none;
    font-size: 1.5em; cursor: pointer; box-shadow: var(--shadow);
    z-index: 1000;
  }

  /* Disclaimer */
  .disclaimer {
    background: #fff3e0; border-left: 4px solid #ff9800;
    padding: 15px 20px; margin: 20px 0; border-radius: 0 var(--radius) var(--radius) 0;
    font-size: 0.9em;
  }
  [data-theme="dark"] .disclaimer { background: #332200; }

  /* Footer */
  .footer {
    text-align: center; padding: 30px; color: var(--text-light);
    border-top: 1px solid var(--border); margin-top: 40px; font-size: 0.9em;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .header h1 { font-size: 1.5em; }
    .programs-grid { grid-template-columns: 1fr; }
    .controls { flex-direction: column; }
    .search-box { min-width: 100%; }
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
  }

  /* Tabs */
  .tabs { display: flex; gap: 5px; margin: 20px 0 0 0; flex-wrap: wrap; }
  .tab {
    padding: 10px 20px; border: none; border-radius: var(--radius) var(--radius) 0 0;
    cursor: pointer; font-size: 0.95em; font-weight: 600;
    background: var(--border); color: var(--text-light); transition: all 0.2s;
  }
  .tab.active { background: var(--card-bg); color: var(--primary); }
  .tab-content { display: none; }
  .tab-content.active { display: block; }
</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
  <h1>🎓 Hong Kong University Master's Admissions</h1>
  <p>Official data from 9 universities | [X] programmes | [Academic Year]</p>
</div>

<div class="container">

  <!-- DISCLAIMER -->
  <div class="disclaimer">
    ⚠️ <strong>Official Data Only:</strong> All information is sourced from official university websites.
    Click the "Official Page" links to verify current details. Data collected: [Date].
  </div>

  <!-- STATS DASHBOARD -->
  <div class="stats-grid">
    <div class="stat-card"><div class="number" id="totalPrograms">0</div><div class="label">Total Programs</div></div>
    <div class="stat-card"><div class="number">9</div><div class="label">Universities</div></div>
    <div class="stat-card"><div class="number" id="avgTuition">0</div><div class="label">Avg Tuition (HKD)</div></div>
    <div class="stat-card"><div class="number" id="degreeTypes">0</div><div class="label">Degree Types</div></div>
  </div>

  <!-- TABS -->
  <div class="tabs">
    <button class="tab active" onclick="switchTab('programs')">📋 All Programs</button>
    <button class="tab" onclick="switchTab('comparison')">📊 Comparison</button>
    <button class="tab" onclick="switchTab('timeline')">📅 Timeline</button>
  </div>

  <!-- TAB: ALL PROGRAMS -->
  <div id="tab-programs" class="tab-content active">
    <!-- CONTROLS -->
    <div class="controls">
      <input type="text" class="search-box" id="searchBox"
             placeholder="🔍 Search programs, universities, faculties...">
      <select id="filterUni"><option value="">All Universities</option></select>
      <select id="filterDegree"><option value="">All Degrees</option></select>
      <select id="sortBy">
        <option value="name">Sort: Name</option>
        <option value="tuition-asc">Sort: Tuition ↑</option>
        <option value="tuition-desc">Sort: Tuition ↓</option>
        <option value="deadline">Sort: Deadline</option>
      </select>
    </div>
    <p id="resultCount" style="margin:10px 0;color:var(--text-light)"></p>
    <div class="programs-grid" id="programsGrid">
      <!-- Program cards will be generated by JavaScript -->
    </div>
  </div>

  <!-- TAB: COMPARISON -->
  <div id="tab-comparison" class="tab-content">
    <!-- Comparison tables -->
  </div>

  <!-- TAB: TIMELINE -->
  <div id="tab-timeline" class="tab-content">
    <!-- Application deadline timeline -->
  </div>

  <!-- FOOTER -->
  <div class="footer">
    <p>Data sourced exclusively from official university websites</p>
    <p>Generated by HK University Admissions Skill</p>
  </div>
</div>

<!-- DARK MODE TOGGLE -->
<button class="theme-toggle" onclick="toggleTheme()" title="Toggle dark mode">🌙</button>

<script>
// === DATA (populated during generation) ===
const programs = [
  // Each program object follows this structure:
  // { uni, uniZh, faculty, name, nameZh, degree, mode, duration, tuitionTotal, tuitionAnnual,
  //   appOpen, deadlineMain, deadlineLate, ielts, toefl, otherEng, otherReq, desc, url }
];

// === INITIALIZE ===
function init() {
  populateFilters();
  renderPrograms(programs);
  updateStats();
}

// === FILTERS & SEARCH ===
function populateFilters() {
  const unis = [...new Set(programs.map(p => p.uni))].sort();
  const degrees = [...new Set(programs.map(p => p.degree))].sort();
  const uniSelect = document.getElementById('filterUni');
  const degreeSelect = document.getElementById('filterDegree');
  unis.forEach(u => { const o = document.createElement('option'); o.value = u; o.textContent = u; uniSelect.appendChild(o); });
  degrees.forEach(d => { const o = document.createElement('option'); o.value = d; o.textContent = d; degreeSelect.appendChild(o); });
}

function getFilteredPrograms() {
  const search = document.getElementById('searchBox').value.toLowerCase();
  const uni = document.getElementById('filterUni').value;
  const degree = document.getElementById('filterDegree').value;
  const sort = document.getElementById('sortBy').value;

  let filtered = programs.filter(p => {
    const matchSearch = !search || [p.name, p.nameZh, p.uni, p.faculty, p.degree, p.desc]
      .join(' ').toLowerCase().includes(search);
    const matchUni = !uni || p.uni === uni;
    const matchDegree = !degree || p.degree === degree;
    return matchSearch && matchUni && matchDegree;
  });

  if (sort === 'tuition-asc') filtered.sort((a, b) => parseFee(a.tuitionTotal) - parseFee(b.tuitionTotal));
  else if (sort === 'tuition-desc') filtered.sort((a, b) => parseFee(b.tuitionTotal) - parseFee(a.tuitionTotal));
  else if (sort === 'deadline') filtered.sort((a, b) => new Date(a.deadlineMain) - new Date(b.deadlineMain));
  else filtered.sort((a, b) => a.name.localeCompare(b.name));

  return filtered;
}

function parseFee(fee) { return parseInt(String(fee).replace(/[^0-9]/g, '')) || 0; }

function renderPrograms(list) {
  const grid = document.getElementById('programsGrid');
  document.getElementById('resultCount').textContent = list.length + ' programs found';
  grid.innerHTML = list.map(p => `
    <div class="program-card">
      <div class="card-header">
        <h3>${p.name}</h3>
        <div class="uni-name">${p.uni} · ${p.faculty}</div>
      </div>
      <div class="card-body">
        <div class="card-row">
          <span class="card-label">Degree</span>
          <span class="card-value"><span class="tag tag-degree">${p.degree}</span></span>
        </div>
        <div class="card-row">
          <span class="card-label">Mode</span>
          <span class="card-value">${p.mode.split(/[&,]/).map(m => 
            '<span class="tag '+(m.trim().startsWith('Full')?'tag-ft':'tag-pt')+'">'+m.trim()+'</span>'
          ).join(' ')}</span>
        </div>
        <div class="card-row"><span class="card-label">Duration</span><span class="card-value">${p.duration}</span></div>
        <div class="card-row"><span class="card-label">Tuition</span><span class="card-value">${p.tuitionTotal}</span></div>
        <div class="card-row"><span class="card-label">Deadline</span><span class="card-value">${p.deadlineMain}</span></div>
        <div class="card-row"><span class="card-label">IELTS</span><span class="card-value">${p.ielts}</span></div>
        <div class="card-row"><span class="card-label">TOEFL</span><span class="card-value">${p.toefl}</span></div>
      </div>
      <div class="card-footer">
        <a href="${p.url}" target="_blank" rel="noopener">🔗 Official Programme Page</a>
      </div>
    </div>
  `).join('');
}

function updateStats() {
  document.getElementById('totalPrograms').textContent = programs.length;
  const fees = programs.map(p => parseFee(p.tuitionTotal)).filter(f => f > 0);
  const avg = fees.length ? Math.round(fees.reduce((a, b) => a + b, 0) / fees.length) : 0;
  document.getElementById('avgTuition').textContent = avg.toLocaleString();
  document.getElementById('degreeTypes').textContent = new Set(programs.map(p => p.degree)).size;
}

// === EVENT LISTENERS ===
['searchBox', 'filterUni', 'filterDegree', 'sortBy'].forEach(id => {
  document.getElementById(id).addEventListener(id === 'searchBox' ? 'input' : 'change', () => {
    renderPrograms(getFilteredPrograms());
  });
});

// === TABS ===
function switchTab(tabName) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById('tab-' + tabName).classList.add('active');
  event.target.classList.add('active');
}

// === THEME ===
function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  document.querySelector('.theme-toggle').textContent = next === 'dark' ? '☀️' : '🌙';
}

// Initialize on load
document.addEventListener('DOMContentLoaded', init);
</script>
</body>
</html>
```

## Data Population

When generating the HTML, populate the `programs` array with actual data:

```javascript
const programs = [
  {
    uni: "HKU",
    uniZh: "香港大學",
    faculty: "Faculty of Engineering",
    name: "MSc in Computer Science",
    nameZh: "計算機科學理學碩士",
    degree: "MSc",
    mode: "Full-time",
    duration: "1 year",
    tuitionTotal: "HKD 180,000",
    tuitionAnnual: "HKD 180,000",
    appOpen: "1 Sep 2025",
    deadlineMain: "30 Nov 2025",
    deadlineLate: "28 Feb 2026",
    ielts: "6.0 (sub 5.5)",
    toefl: "80",
    otherEng: "N/A",
    otherReq: "Bachelor's in CS or related",
    desc: "Covers advanced topics in computer science...",
    url: "https://www.msc-cs.hku.hk"
  },
  // ... more programs
];
```

## Delivery Instructions

Present in a code block with `html` language tag. Tell the user:

> **How to use:**
> 1. Copy the entire HTML content into a file named `hk_admissions.html`
> 2. Open in any web browser
> 3. Use the search bar to find programs
> 4. Filter by university or degree type
> 5. Sort by tuition or deadline
> 6. Click "Official Programme Page" links to visit university sites
> 7. Toggle dark mode with the 🌙 button
