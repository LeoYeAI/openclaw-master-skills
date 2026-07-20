# skill-mermaid-diagrams

Generate professional, consistently-styled Mermaid diagrams for technical content. 12 template types with automatic validation and rendering.

## Templates

| Template | Best For |
|----------|----------|
| **architecture** | System components, tool pipelines, agent interactions |
| **flowchart** | Decision trees, process flows, validation workflows |
| **sequence** | API call sequences, actor communication, message flows |
| **concept-map** | Hierarchical concepts, mental models, knowledge graphs |
| **radial-concept** | Progressive summarization, abstraction layers |
| **timeline** | Project phases, evolution timelines, staged processes |
| **comparison** | Quadrant analysis, cost vs performance (X/Y plotting) |
| **comparison-table** | Side-by-side feature comparison |
| **gantt** | Project planning, milestone tracking, task dependencies |
| **mindmap** | Brainstorming, organic thought structures |
| **class-diagram** | Object models, database schemas, UML |
| **state-diagram** | State machines, lifecycles, workflow stages |

All templates share a consistent color scheme and professional styling.

## Quick Start

**1. Install dependencies**

```bash
npm install -g @mermaid-js/mermaid-cli
```

**2. Create a content file** (see `assets/example-content.json`)

```json
{
  "chapter": "chapter-01.md",
  "diagrams": [
    {
      "template": "architecture",
      "placeholders": {
        "SYSTEM_NAME": "My System",
        "COMPONENT_1_LABEL": "Frontend",
        "COMPONENT_2_LABEL": "Backend",
        "COMPONENT_3_LABEL": "Database",
        "EXTERNAL_1_LABEL": "User",
        "EXTERNAL_2_LABEL": "API Client",
        "FLOW_1": "Request",
        "FLOW_2": "Process",
        "FLOW_3": "Query",
        "FLOW_4": "Response"
      }
    }
  ]
}
```

**3. Generate and validate**

```bash
node scripts/generate.mjs --content content.json --out diagrams/
node scripts/validate.mjs --dir diagrams/
```

Output: `.mmd` source + `.svg` vector + `.png` raster for each diagram.

## Subagent Pattern

When used as a skill, spawn a subagent:

```
Generate 3 Mermaid diagrams for /path/to/chapter.md and save to diagrams/chapter-01/
```

The subagent reads the chapter, selects templates, generates placeholder values, runs the scripts, and validates output.

## Project Structure

```
assets/          # 12 Mermaid templates (.mmd) + example content
scripts/         # generate, validate, semantic-validate, auto-correct
references/      # Mermaid syntax quick reference
tests/           # Semantic validation test suite
SKILL.md         # Full skill documentation
```

## Documentation

See [SKILL.md](SKILL.md) for complete documentation including:
- Template placeholder reference
- Validation workflow
- Customization guide
- Troubleshooting

## License

MIT
