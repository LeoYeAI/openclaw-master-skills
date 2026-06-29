# Mermaid Diagram Examples

Common diagram patterns used in Architecture Visualization documents.

## 1. System Architecture (Layered)

```mermaid
graph TB
    subgraph "用户交互层"
        A[用户] --> B[AI代理会话]
    end
    
    subgraph "技能层"
        B --> C[Core Skill]
        C --> D[Component A]
        C --> E[Component B]
        C --> F[Component C]
    end
    
    subgraph "持久化层"
        G[Data Store 1]
        H[Data Store 2]
        
        F --> G
        F --> H
    end
    
    subgraph "知识层"
        I[Global Config]
        J[Project Config]
        
        G --> I
        H --> J
    end
    
    style C fill:#4CAF50
    style D fill:#FFC107
    style E fill:#FFC107
    style F fill:#FFC107
    style G fill:#2196F3
    style H fill:#2196F3
```

**Use when**: Showing component hierarchy and data flow in layers

---

## 2. Data Flow

```mermaid
flowchart LR
    A[Input] --> B[Processor]
    B --> C{Decision}
    
    C -->|Path A| D[Output A]
    C -->|Path B| E[Output B]
    
    D --> F[Storage]
    E --> F
    
    style B fill:#FF9800
    style C fill:#9C27B0
    style F fill:#4CAF50
```

**Use when**: Showing how data moves through the system

---

## 3. Sequence Diagram

```mermaid
sequenceDiagram
    participant U as 用户
    participant A as AI代理
    participant S as 系统
    participant D as 数据存储
    
    U->>A: 发出请求
    A->>S: 处理请求
    
    alt 成功
        S->>D: 保存数据
        D-->>S: 确认
        S-->>A: 返回结果
        A->>U: 显示结果
    else 失败
        S-->>A: 返回错误
        A->>U: 显示错误信息
    end
    
    Note over A,D: 后台异步处理
```

**Use when**: Showing interactions between components over time

---

## 4. Decision Tree

```mermaid
flowchart TD
    Start[开始] --> Q1{条件1?}
    
    Q1 -->|是| Q2{条件2?}
    Q1 -->|否| R1[结果A]
    
    Q2 -->|是| R2[结果B]
    Q2 -->|否| Q3{条件3?}
    
    Q3 -->|是| R3[结果C]
    Q3 -->|否| R4[结果D]
    
    style Q1 fill:#FF9800
    style Q2 fill:#FF9800
    style Q3 fill:#FF9800
    style R2 fill:#4CAF50
    style R3 fill:#4CAF50
```

**Use when**: Showing conditional logic and branching

---

## 5. State Machine

```mermaid
stateDiagram-v2
    [*] --> Pending: 创建
    
    Pending --> InProgress: 开始处理
    Pending --> Cancelled: 取消
    
    InProgress --> Completed: 完成
    InProgress --> Failed: 失败
    InProgress --> Pending: 暂停
    
    Failed --> InProgress: 重试
    
    Completed --> [*]
    Cancelled --> [*]
    
    note right of Pending
        初始状态
        等待处理
    end note
    
    note right of Completed
        终态
        不可再转换
    end note
```

**Use when**: Showing lifecycle and state transitions

---

## 6. File System Topology

```mermaid
graph TD
    Root[项目根目录] --> A[src/]
    Root --> B[config/]
    Root --> C[docs/]
    
    A --> A1[components/]
    A --> A2[utils/]
    
    A1 --> A11[ComponentA.tsx]
    A1 --> A12[ComponentB.tsx]
    
    B --> B1[app.config.js]
    B --> B2[db.config.js]
    
    C --> C1[README.md]
    C --> C2[API.md]
    
    style A fill:#4CAF50
    style B fill:#FF9800
    style C fill:#2196F3
    style A11 fill:#E3F2FD
    style A12 fill:#E3F2FD
```

**Use when**: Showing directory structure and file organization

---

## 7. Comparison Graph

```mermaid
graph TB
    subgraph "方案A"
        A1[特点1]
        A2[特点2]
        A3[特点3]
    end
    
    subgraph "方案B"
        B1[特点1]
        B2[特点2]
        B3[特点3]
    end
    
    subgraph "方案C"
        C1[特点1]
        C2[特点2]
    end
    
    style A1 fill:#4CAF50
    style A2 fill:#4CAF50
    style A3 fill:#FFC107
    style B1 fill:#4CAF50
    style B2 fill:#FFC107
    style B3 fill:#f44336
```

**Use when**: Comparing features across different options

---

## 8. Gantt Chart (Timeline)

```mermaid
gantt
    title 实施时间线
    dateFormat YYYY-MM-DD
    section 阶段1
    任务A           :a1, 2026-03-01, 7d
    任务B           :a2, after a1, 5d
    
    section 阶段2
    任务C           :b1, 2026-03-15, 10d
    任务D           :b2, after b1, 7d
    
    section 阶段3
    任务E           :c1, after b2, 14d
```

**Use when**: Showing project timelines or lifecycle stages

---

## 9. Mind Map

```mermaid
mindmap
  root((核心概念))
    分支A
      子项A1
      子项A2
        细节A2a
        细节A2b
    分支B
      子项B1
      子项B2
    分支C
      子项C1
        细节C1a
      子项C2
```

**Use when**: Showing hierarchical relationships and categories

---

## 10. Class Diagram (for OO systems)

```mermaid
classDiagram
    class SystemA {
        +attribute1
        +attribute2
        +method1()
        +method2()
    }
    
    class SystemB {
        +attribute3
        -privateMethod()
        +publicMethod()
    }
    
    class Interface {
        <<interface>>
        +interfaceMethod()
    }
    
    SystemA --> SystemB : uses
    SystemB ..|> Interface : implements
    
    class ExtensionA {
        +newFeature()
    }
    
    Interface <|-- ExtensionA : extends
```

**Use when**: Documenting object-oriented architecture

---

## Color Coding Standards

Consistent colors help readers quickly understand diagrams:

| Color | Hex | Mermaid | Use For |
|-------|-----|---------|---------|
| 🟢 Green | `#4CAF50` | `fill:#4CAF50` | Success, output, final state |
| 🔵 Blue | `#2196F3` | `fill:#2196F3` | Data, storage, information |
| 🟠 Orange | `#FF9800` | `fill:#FF9800` | Processing, transformation |
| 🟣 Purple | `#9C27B0` | `fill:#9C27B0` | Decision, logic, control flow |
| 🟡 Yellow | `#FFC107` | `fill:#FFC107` | Warning, attention, medium priority |
| 🔴 Red | `#f44336` | `fill:#f44336` | Error, critical, failure |
| 🟤 Brown | `#795548` | `fill:#795548` | Deprecated, legacy |
| ⚪ Light Blue | `#E3F2FD` | `fill:#E3F2FD` | Secondary elements |

---

## Best Practices

### DO ✅

- **Use subgraphs** for logical grouping
- **Apply consistent colors** across all diagrams
- **Keep node labels short** (3-5 words max)
- **Add style** to important nodes
- **Use notes** for additional context
- **Test rendering** before finalizing

### DON'T ❌

- **Don't overcrowd** - max 15-20 nodes per diagram
- **Don't mix styles** - stick to one color scheme
- **Don't use tiny text** - readable labels matter
- **Don't skip legends** - explain colors if not obvious
- **Don't nest too deep** - max 3 levels of subgraphs

---

## Common Syntax Errors

### Missing quotes
```mermaid
❌ graph TD
    A[Node with spaces] --> B[Another node]
```

```mermaid
✅ graph TD
    A["Node with spaces"] --> B["Another node"]
```

### Invalid node IDs
```mermaid
❌ graph TD
    1-Node --> 2-Node
```

```mermaid
✅ graph TD
    N1[Node 1] --> N2[Node 2]
```

### Broken arrows
```mermaid
❌ A -> B
```

```mermaid
✅ A --> B  (flowchart/graph)
✅ A->>B    (sequence diagram)
```

---

## Mermaid Resources

- **Official Docs**: https://mermaid.js.org/
- **Live Editor**: https://mermaid.live/
- **Cheat Sheet**: https://jojozhuang.github.io/tutorial/mermaid-cheat-sheet/

---

**Tip**: Start with simple diagrams and add complexity gradually. A simple, clear diagram beats a complex, confusing one every time. 📊
