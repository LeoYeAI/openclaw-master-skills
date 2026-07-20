# Mermaid Syntax Reference

Quick reference guide for Mermaid diagram syntax used in the skill-mermaid-diagrams.

## Official Documentation

- **Mermaid Docs:** https://mermaid.js.org/
- **Syntax Reference:** https://mermaid.js.org/intro/syntax-reference.html
- **Theming Guide:** https://mermaid.js.org/config/theming.html
- **CLI Documentation:** https://github.com/mermaid-js/mermaid-cli

## Graph/Architecture Diagrams

### Basic Syntax

```mermaid
graph TB
    A[Rectangle] --> B{Decision}
    B -->|Yes| C[Result 1]
    B -->|No| D[Result 2]
```

### Direction Options

- `TB` or `TD` - Top to Bottom
- `BT` - Bottom to Top
- `LR` - Left to Right
- `RL` - Right to Left

### Node Shapes

```mermaid
graph LR
    A[Rectangle]
    B(Rounded)
    C([Stadium])
    D[[Subroutine]]
    E[(Database)]
    F((Circle))
    G{Diamond}
    H{{Hexagon}}
```

### Edge Types

```mermaid
graph LR
    A --> B    %% Solid arrow
    C -.-> D   %% Dotted arrow
    E ==> F    %% Thick arrow
    G --- H    %% Solid line
    I -.- J    %% Dotted line
    K === L    %% Thick line
```

### Edge Labels

```mermaid
graph LR
    A -->|Label| B
    C -.->|Dotted| D
    E ==>|Thick| F
```

### Subgraphs

```mermaid
graph TB
    subgraph "Container Name"
        A[Component 1]
        B[Component 2]
    end
    
    C[External] --> A
```

## Flowcharts

### Basic Syntax

```mermaid
flowchart TD
    Start([Start]) --> Decision{Check?}
    Decision -->|Yes| Action1[Process]
    Decision -->|No| Action2[Skip]
    Action1 --> End([End])
    Action2 --> End
```

### Extended Node Types (Flowchart-Specific)

```mermaid
flowchart LR
    A[/Parallelogram/]
    B[\Inverted Parallelogram\]
    C[/Trapezoid\]
    D[\Inverted Trapezoid/]
```

## Sequence Diagrams

### Basic Syntax

```mermaid
sequenceDiagram
    participant A as Alice
    participant B as Bob
    
    A->>B: Request
    B->>A: Response
    A->>B: Acknowledge
```

### Message Types

```mermaid
sequenceDiagram
    A->>B: Solid arrow
    A-->>B: Dotted arrow
    A-)B: Open arrow
    A--)B: Dotted open arrow
    A-xB: Cross (async)
    A--xB: Dotted cross
```

### Activation

```mermaid
sequenceDiagram
    participant A
    participant B
    
    A->>+B: Activate B
    B->>-A: Deactivate B
```

### Notes

```mermaid
sequenceDiagram
    participant A
    participant B
    
    Note right of A: Note on right
    Note left of B: Note on left
    Note over A,B: Note spanning both
```

## Styling and Theming

### Theme Configuration

```mermaid
%%{init: {'theme':'base', 'themeVariables': {
  'primaryColor':'#4A90E2',
  'primaryTextColor':'#fff',
  'primaryBorderColor':'#2E5C8A',
  'lineColor':'#333',
  'secondaryColor':'#7B68EE',
  'tertiaryColor':'#90EE90'
}}}%%
graph TB
    A[Node]
```

### Available Themes

- `default` - Mermaid default theme
- `base` - Customizable base theme (used in this skill)
- `dark` - Dark mode theme
- `forest` - Forest green theme
- `neutral` - Neutral gray theme

### Class Definitions

```mermaid
graph TB
    A[Node 1]
    B[Node 2]
    C[Node 3]
    
    classDef primary fill:#4A90E2,stroke:#2E5C8A,color:#fff
    classDef secondary fill:#7B68EE,stroke:#5A4FCF,color:#fff
    
    class A,B primary
    class C secondary
```

## Common Patterns Used in This Skill

### Architecture Pattern (System Components)

```mermaid
%%{init: {'theme':'base', 'themeVariables': {...}}}%%
graph TB
    subgraph "System Name"
        Component1[Main Component]
        Component2[Secondary Component]
    end
    
    External((User))
    
    External -->|Request| Component1
    Component1 -->|Process| Component2
    Component2 -->|Response| External
    
    classDef primary fill:#4A90E2,stroke:#2E5C8A,color:#fff
    class Component1,Component2 primary
```

### Flowchart Pattern (Decision Trees)

```mermaid
%%{init: {'theme':'base', 'themeVariables': {...}}}%%
flowchart TD
    Start([Begin]) --> Decision{Condition?}
    Decision -->|Yes| Action1[Do This]
    Decision -->|No| Action2[Do That]
    Action1 --> End([Finish])
    Action2 --> End
    
    classDef startEnd fill:#90EE90,stroke:#6DBE6D,color:#333
    classDef decision fill:#FFD700,stroke:#DAA520,color:#333
    classDef action fill:#4A90E2,stroke:#2E5C8A,color:#fff
    
    class Start,End startEnd
    class Decision decision
    class Action1,Action2 action
```

### Sequence Pattern (Actor Interactions)

```mermaid
%%{init: {'theme':'base', 'themeVariables': {...}}}%%
sequenceDiagram
    participant User
    participant System
    participant Database
    
    User->>System: Request
    activate System
    System->>Database: Query
    activate Database
    Database-->>System: Data
    deactivate Database
    System-->>User: Response
    deactivate System
```

## Best Practices for This Skill

1. **Always include theme initialization block** at the top of each .mmd file
2. **Use consistent color scheme** across all diagrams:
   - Primary Blue: `#4A90E2` (main components)
   - Secondary Purple: `#7B68EE` (supporting elements)
   - Tertiary Green: `#90EE90` (external actors, success)
   - Warning Yellow: `#FFD700` (decisions, cautions)
   - Error Red: `#FF6B6B` (failures, critical paths)

3. **Keep labels concise** - max 8 words per label
4. **Use semantic naming** for placeholders (SYSTEM_NAME, COMPONENT_1, FLOW_1)
5. **Validate syntax** before rendering with `mmdc`
6. **Test rendering** with transparent background (`-b transparent`)

## Troubleshooting Common Syntax Errors

### Error: "Syntax error in graph"
**Cause:** Malformed node or edge definition  
**Fix:** Check for missing brackets, quotes, or arrows

### Error: "Unexpected token"
**Cause:** Special characters not escaped  
**Fix:** Wrap labels in quotes: `A["Label with special chars!"]`

### Error: "Cannot read property"
**Cause:** Invalid theme variable  
**Fix:** Check variable names against Mermaid theme schema

### Error: "Duplicate ID"
**Cause:** Node ID used twice  
**Fix:** Use unique IDs for each node (A, B, C, etc.)

## Advanced Features

### Links in Nodes

```mermaid
graph LR
    A["Node with link"]
    click A "https://example.com" "Tooltip text"
```

### Comments

```mermaid
graph TB
    %% This is a comment
    A[Node] --> B[Another Node]
    %% Comments are ignored during rendering
```

### Direction-Specific Styling

```mermaid
graph LR
    A --> B
    B --> C
    C --> D
    
    linkStyle 0 stroke:#ff3,stroke-width:4px
    linkStyle 1 stroke:#f33,stroke-width:2px
```

## Rendering Configuration (CLI)

### Basic Rendering

```bash
mmdc -i input.mmd -o output.svg
```

### With Options

```bash
mmdc -i input.mmd -o output.svg \
  -t base \                    # Theme
  -b transparent \             # Background
  -w 1200 \                    # Width (PNG only)
  -H 800                       # Height (PNG only)
```

### Multiple Outputs

```bash
mmdc -i input.mmd -o output.svg  # Vector
mmdc -i input.mmd -o output.png -w 1200  # Raster
```

## Additional Resources

- **Live Editor:** https://mermaid.live/ (test syntax interactively)
- **VS Code Extension:** Markdown Preview Mermaid Support
- **GitHub Support:** Mermaid diagrams render in GitHub Markdown
- **Examples Gallery:** https://mermaid.js.org/ecosystem/integrations.html

---

**Note:** This reference covers the subset of Mermaid syntax used in the skill-mermaid-diagrams. For comprehensive documentation, see https://mermaid.js.org/
