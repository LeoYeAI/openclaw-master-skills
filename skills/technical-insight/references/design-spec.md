# Tech Insight Design Specifications

## Visual Identity Guidelines

### Color Palette
- **Background**: #000000 (pure black) or #0a0a0a (near black)
- **Primary Text**: #ffffff (pure white)
- **Secondary Text**: #9ca3af (slate-400)
- **Accent Colors**: 
  - Architecture: #8b5cf6 (violet-500) - purple for architecture elements
  - Mechanisms: #10b981 (emerald-500) - green for core mechanisms  
  - Barriers: #f59e0b (amber-500) - amber for competitive barriers
  - Risks: #ef4444 (red-500) - red for risks and warnings
  - Roadmap: #3b82f6 (blue-500) - blue for future evolution

### Typography
- **Chinese Fonts**: HarmonyOS Sans SC, 思源黑体, system-ui
- **English Fonts**: Inter, Roboto, system-ui, JetBrains Mono (for code)
- **Title Weight**: font-black (900) or font-bold (700)
- **Body Weight**: font-light (300) or font-normal (400)
- **Code Font**: JetBrains Mono, Consolas, monospace with syntax highlighting

### Layout Principles
- **Aspect Ratio**: 9:16 (vertical/portrait)
- **Padding**: Minimum 48px on all sides
- **Line Height**: 1.6 for body text, 1.4 for code blocks
- **Max Line Length**: 60 characters for readability
- **Whitespace**: Generous spacing between elements, especially around code blocks

## Data Visualization Standards

### Architecture Diagrams
- Component boxes with clear boundaries and labels
- Arrow directions indicating data flow (solid) vs control flow (dashed)
- Color coding by component type (storage, compute, network, etc.)
- Layered layout showing logical separation (presentation, business, data layers)

### Sequence Diagrams (Mechanisms)
- Lifelines as vertical dashed lines with participant labels
- Activation bars showing method execution duration
- Arrows for synchronous calls (solid) vs asynchronous (dashed)
- Return values shown as dashed arrows with labels

### Risk Matrices
- Heatmap-style grids with color intensity indicating severity
- X-axis: Probability (Low → High)
- Y-axis: Impact (Low → High)  
- Circular markers sized by priority (Probability × Impact)
- Hover tooltips with detailed risk descriptions and mitigation strategies

### Roadmap Timelines
- Horizontal timeline with milestone markers
- Color-coded phases (current, near-term, long-term)
- Dependency arrows showing feature relationships
- Confidence indicators (solid = confirmed, dashed = planned)

### Code Blocks
- Syntax highlighting with dark theme colors
- Line numbers for reference
- Highlighted key lines with accent colors
- Collapsible sections for long code snippets
- Copy-to-clipboard functionality

## Animation Guidelines

### Transitions
- Slide transitions: fade with 300ms duration
- Element entrance: subtle slide-up with 200ms stagger
- Code block highlighting: smooth color transitions
- No distracting animations or bounce effects

### Interactive Elements
- Hover states with 10% brightness increase
- Clickable elements with subtle underline or border
- Keyboard navigation support (← → arrows)
- Code block line highlighting on hover

### Background Effects
- Subtle animated light spots in background
- Very low opacity (5-10%)
- Slow movement (30s+ cycle time)
- Never interfere with text or diagram readability