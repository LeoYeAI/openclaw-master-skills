---
name: macos-hig-designer
description: Design native macOS apps following Apple's Human Interface Guidelines and Liquid Glass design system. Use when building SwiftUI/AppKit macOS apps, validating designs, or implementing macOS-specific patterns.
domain: design
homepage: https://github.com/soponcd/timeflow-skills/tree/main/teams/skills/macos-hig-designer
metadata:
  clawdbot:
    emoji: 🖥️
---

# macOS HIG Designer

Design native macOS applications following Apple's Human Interface Guidelines with macOS Tahoe's Liquid Glass design system.

## Workflow Decision Tree

```
User Request
    │
    ├─► "Review my macOS UI code"
    │       └─► Run HIG Compliance Check (Section 11)
    │           └─► Report violations with fixes
    │
    ├─► "Modernize this macOS code"
    │       └─► Identify deprecated APIs
    │           └─► Apply Modern API Replacements (Section 10)
    │
    └─► "Build [feature] for macOS"
            └─► Design with HIG principles first
                └─► Implement with modern SwiftUI patterns
```

## 1. Design Principles (macOS Tahoe)

### Three Core Tenets

| Principle | Description | Implementation |
|-----------|-------------|----------------|
| **Hierarchy** | Visual layers through Liquid Glass translucency | Use `.glassEffect()`, materials, and depth |
| **Harmony** | Concentric alignment between hardware/software | Round corners, consistent radii, flowing shapes |
| **Consistency** | Platform conventions that adapt to context | Follow standard patterns, respect user preferences |

### Liquid Glass Philosophy

Liquid Glass combines transparency, reflection, refraction, and fluidity with a frosted aesthetic:

```swift
// macOS Tahoe Liquid Glass effect
.glassEffect()                    // Primary Liquid Glass material
.glassEffect(.regular.tinted)     // Tinted variant (26.1+)

// Pre-Tahoe fallback
.background(.ultraThinMaterial)
.background(.regularMaterial)
.background(.thickMaterial)
```

**When to use Liquid Glass:**
- Sidebars, toolbars, and navigation chrome
- Floating panels and popovers
- Dock and widget backgrounds
- System-level UI elements

**When NOT to use:**
- Primary content areas (documents, media)
- Dense data displays (tables, lists with many items)
- Text-heavy interfaces where readability is critical

## 2. Navigation Patterns

### NavigationSplitView (Primary Pattern)

Three-column layout for document-based and content-heavy apps:

```swift
struct ContentView: View {
    @State private var selection: Item.ID?
    @State private var columnVisibility: NavigationSplitViewVisibility = .all

    var body: some View {
        NavigationSplitView(columnVisibility: $columnVisibility) {
            // Sidebar (source list)
            List(items, selection: $selection) { item in
                NavigationLink(value: item) {
                    Label(item.title, systemImage: item.icon)
                }
            }
            .navigationSplitViewColumnWidth(min: 180, ideal: 220, max: 300)
        } content: {
            // Content column (optional middle)
            ContentListView(selection: selection)
        } detail: {
            // Detail view
            DetailView(item: selectedItem)
        }
    }
}
```

### Sidebar Patterns

```swift
// Source list with sections
List(selection: $selection) {
    Section("Library") {
        ForEach(libraryItems) { item in
            Label(item.name, systemImage: item.icon)
                .tag(item)
        }
    }

    Section("Collections") {
        ForEach(collections) { collection in
            Label(collection.name, systemImage: "folder")
                .tag(collection)
                .badge(collection.count)
        }
    }
}
.listStyle(.sidebar)
```

### Inspector Panel (Trailing Sidebar)

```swift
struct DocumentView: View {
    @State private var showInspector = true

    var body: some View {
        MainContentView()
            .inspector(isPresented: $showInspector) {
                InspectorView()
                    .inspectorColumnWidth(min: 200, ideal: 250, max: 400)
            }
            .toolbar {
                ToolbarItem {
                    Button {
                        showInspector.toggle()
                    } label: {
                        Label("Inspector", systemImage: "sidebar.trailing")
                    }
                }
            }
    }
}
```

## 3. Window Management

### Window Configuration

```swift
@main
struct MyApp: App {
    var body: some Scene {
        // Main document window
        WindowGroup {
            ContentView()
        }
        .windowStyle(.automatic)
        .windowToolbarStyle(.unified)
        .defaultSize(width: 900, height: 600)
        .defaultPosition(.center)

        // Settings window
        Settings {
            SettingsView()
        }

        // Utility window
        Window("Inspector", id: "inspector") {
            InspectorWindow()
        }
        .windowStyle(.plain)
        .windowResizability(.contentSize)
        .defaultPosition(.topTrailing)

        // Menu bar extra
        MenuBarExtra("Status", systemImage: "circle.fill") {
            StatusMenu()
        }
        .menuBarExtraStyle(.window)
    }
}
```

### Window Styles

| Style | Use Case |
|-------|----------|
| `.automatic` | Standard app windows |
| `.hiddenTitleBar` | Content-focused (media players) |
| `.plain` | Utility windows, panels |
| `.unified` | Integrated toolbar appearance |
| `.unifiedCompact` | Compact toolbar height |

### Window State Restoration

```swift
WindowGroup {
    ContentView()
}
.handlesExternalEvents(matching: Set(arrayLiteral: "main"))
.commands {
    CommandGroup(replacing: .newItem) {
        Button("New Document") {
            // Handle new document
        }
        .keyboardShortcut("n")
    }
}
```

### Document-Based Apps

```swift
@main
struct DocumentApp: App {
    var body: some Scene {
        DocumentGroup(newDocument: MyDocument()) { file in
            DocumentView(document: file.$document)
        }
        .commands {
            CommandGroup(after: .saveItem) {
                Button("Export...") { }
                    .keyboardShortcut("e", modifiers: [.command, .shift])
            }
        }
    }
}

struct MyDocument: FileDocument {
    static var readableContentTypes: [UTType] { [.plainText] }

    init(configuration: ReadConfiguration) throws { }
    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper { }
}
```

## 4. Toolbar & Menu Bar

### Toolbar Configuration

```swift
.toolbar {
    // Leading items (macOS places these before title)
    ToolbarItem(placement: .navigation) {
        Button(action: goBack) {
            Label("Back", systemImage: "chevron.left")
        }
    }

    // Principal (centered)
    ToolbarItem(placement: .principal) {
        Picker("View Mode", selection: $viewMode) {
            Label("Icons", systemImage: "square.grid.2x2").tag(ViewMode.icons)
            Label("List", systemImage: "list.bullet").tag(ViewMode.list)
        }
        .pickerStyle(.segmented)
    }

    // Trailing items
    ToolbarItemGroup(placement: .primaryAction) {
        Button(action: share) {
            Label("Share", systemImage: "square.and.arrow.up")
        }

        Button(action: toggleInspector) {
            Label("Inspector", systemImage: "sidebar.trailing")
        }
    }
}
.toolbarRole(.editor) // or .browser, .automatic
```

### Custom Menu Bar

```swift
.commands {
    // Replace existing menu group
    CommandGroup(replacing: .newItem) {
        Button("New Project") { }
            .keyboardShortcut("n")
        Button("New from Template...") { }
            .keyboardShortcut("n", modifiers: [.command, .shift])
    }

    // Add to existing group
    CommandGroup(after: .sidebar) {
        Button("Toggle Inspector") { }
            .keyboardShortcut("i", modifiers: [.command, .option])
    }

    // Custom menu
    CommandMenu("Canvas") {
        Button("Zoom In") { }
            .keyboardShortcut("+")
        Button("Zoom Out") { }
            .keyboardShortcut("-")
        Divider()
        Button("Fit to Window") { }
            .keyboardShortcut("0")
    }
}
```

### Menu Bar Apps

```swift
MenuBarExtra("App Status", systemImage: statusIcon) {
    VStack(alignment: .leading, spacing: 8) {
        Text("Status: \(status)")
            .font(.headline)

        Divider()

        Button("Open Main Window") {
            openWindow(id: "main")
        }

        Button("Quit") {
            NSApplication.shared.terminate(nil)
        }
        .keyboardShortcut("q")
    }
    .padding()
}
.menuBarExtraStyle(.window) // or .menu for simple dropdown
```

## 5. Keyboard Shortcuts

### Standard macOS Shortcuts

Always implement these when applicable:

| Action | Shortcut | Implementation |
|--------|----------|----------------|
| New | ⌘N | `.keyboardShortcut("n")` |
| Open | ⌘O | `.keyboardShortcut("o")` |
| Save | ⌘S | `.keyboardShortcut("s")` |
| Close | ⌘W | `.keyboardShortcut("w")` |
| Undo | ⌘Z | `.keyboardShortcut("z")` |
| Redo | ⇧⌘Z | `.keyboardShortcut("z", modifiers: [.command, .shift])` |
| Cut | ⌘X | `.keyboardShortcut("x")` |
| Copy | ⌘C | `.keyboardShortcut("c")` |
| Paste | ⌘V | `.keyboardShortcut("v")` |
| Select All | ⌘A | `.keyboardShortcut("a")` |
| Find | ⌘F | `.keyboardShortcut("f")` |
| Preferences | ⌘, | `.keyboardShortcut(",")` |
| Hide | ⌘H | System handled |
| Quit | ⌘Q | System handled |

### Custom Shortcuts

```swift
Button("Toggle Sidebar") {
    toggleSidebar()
}
.keyboardShortcut("s", modifiers: [.command, .control])

// Function keys
Button("Refresh") { }
    .keyboardShortcut(KeyEquivalent.init(Character(UnicodeScalar(NSF5FunctionKey)!)))

// Arrow keys
Button("Next") { }
    .keyboardShortcut(.rightArrow)
```

## 6. Components with Liquid Glass

### Control Sizing

| Size | Shape | Use Case |
|------|-------|----------|
| Mini | Rounded rect | Compact toolbars, dense UIs |
| Small | Rounded rect | Secondary controls, sidebars |
| Regular | Rounded rect | Primary controls (default) |
| Large | Capsule | Prominent actions |
| Extra Large | Capsule + Glass | Hero CTAs, onboarding |

```swift
// Size modifiers
Button("Action") { }
    .controlSize(.mini)     // Smallest
    .controlSize(.small)    // Compact
    .controlSize(.regular)  // Default
    .controlSize(.large)    // Prominent
    .controlSize(.extraLarge) // Hero (macOS 15+)
```

### Buttons

```swift
// Primary action (prominent)
Button("Save Changes") { }
    .buttonStyle(.borderedProminent)
    .controlSize(.large)

// Secondary action
Button("Cancel") { }
    .buttonStyle(.bordered)

// Tertiary/link style
Button("Learn More") { }
    .buttonStyle(.plain)
    .foregroundStyle(.link)

// Destructive
Button("Delete", role: .destructive) { }
    .buttonStyle(.bordered)

// Toolbar button
Button { } label: {
    Label("Add", systemImage: "plus")
}
.buttonStyle(.borderless)
```

### Text Fields

```swift
// Standard text field
TextField("Search", text: $query)
    .textFieldStyle(.roundedBorder)

// Search field with tokens
TextField("Search", text: $query)
    .searchable(text: $query, tokens: $tokens) { token in
        Label(token.name, systemImage: token.icon)
    }

// Secure field
SecureField("Password", text: $password)
    .textFieldStyle(.roundedBorder)
```

### Tables

```swift
Table(items, selection: $selection) {
    TableColumn("Name", value: \.name)
        .width(min: 100, ideal: 150)

    TableColumn("Date") { item in
        Text(item.date, format: .dateTime)
    }
    .width(100)

    TableColumn("Status") { item in
        StatusBadge(status: item.status)
    }
    .width(80)
}
.tableStyle(.inset(alternatesRowBackgrounds: true))
.contextMenu(forSelectionType: Item.ID.self) { selection in
    Button("Open") { }
    Button("Delete", role: .destructive) { }
}
```

### Popovers and Sheets

```swift
// Popover
Button("Info") {
    showPopover = true
}
.popover(isPresented: $showPopover, arrowEdge: .bottom) {
    InfoView()
        .frame(width: 300, height: 200)
        .padding()
}

// Sheet
.sheet(isPresented: $showSheet) {
    SheetContent()
        .frame(minWidth: 400, minHeight: 300)
}

// Alert
.alert("Delete Item?", isPresented: $showAlert) {
    Button("Cancel", role: .cancel) { }
    Button("Delete", role: .destructive) {
        deleteItem()
    }
} message: {
    Text("This action cannot be undone.")
}
```

## 7. Typography & Colors

### System Typography

```swift
// Semantic styles (preferred)
Text("Title").font(.largeTitle)      // 26pt bold
Text("Headline").font(.headline)      // 13pt semibold
Text("Subheadline").font(.subheadline) // 11pt regular
Text("Body").font(.body)              // 13pt regular
Text("Callout").font(.callout)        // 12pt regular
Text("Caption").font(.caption)        // 10pt regular
Text("Caption 2").font(.caption2)     // 10pt regular

// Monospaced for code
Text("let x = 1").font(.system(.body, design: .monospaced))
```

### Semantic Colors

```swift
// Foreground
.foregroundStyle(.primary)            // Primary text
.foregroundStyle(.secondary)          // Secondary text
.foregroundStyle(.tertiary)           // Tertiary text
.foregroundStyle(.quaternary)         // Quaternary text

// Backgrounds
.background(.background)              // Window background
.background(.regularMaterial)         // Translucent material

// Accent colors
.tint(.accentColor)                   // App accent color
.foregroundStyle(.link)               // Clickable links

// Semantic colors
Color.red                             // System red (adapts to light/dark)
Color.blue                            // System blue
```

### Vibrancy and Materials

```swift
// Materials (adapt to background content)
.background(.ultraThinMaterial)       // Most transparent
.background(.thinMaterial)
.background(.regularMaterial)         // Default
.background(.thickMaterial)
.background(.ultraThickMaterial)      // Least transparent

// Vibrancy in sidebars
List { }
    .listStyle(.sidebar)
    .scrollContentBackground(.hidden)
    .background(.ultraThinMaterial)
```

## 8. Spacing & Layout

### 8-Point Grid System

```swift
// Standard spacing values
VStack(spacing: 8) { }                // Standard
VStack(spacing: 16) { }               // Section spacing
VStack(spacing: 20) { }               // Group spacing

// Padding
.padding(8)                           // Tight
.padding(12)                          // Standard
.padding(16)                          // Comfortable
.padding(20)                          // Spacious

// Content margins
.contentMargins(16)                   // Uniform margins
.contentMargins(.horizontal, 20)      // Horizontal only
```

### Safe Areas

```swift
// Respect toolbar safe area
.safeAreaInset(edge: .top) {
    ToolbarContent()
}

// Ignore safe area for backgrounds
.ignoresSafeArea(.container, edges: .top)

// Content that should avoid toolbar
.safeAreaPadding(.top)
```

### Minimum Touch/Click Targets

```swift
// Minimum 44x44 points for clickable elements
Button { } label: {
    Image(systemName: "gear")
}
.frame(minWidth: 44, minHeight: 44)

// Use contentShape for larger hit areas
RoundedRectangle(cornerRadius: 8)
    .frame(width: 200, height: 100)
    .contentShape(Rectangle())
    .onTapGesture { }
```

### Adaptive Layouts

```swift
// Responsive to window size
GeometryReader { geometry in
    if geometry.size.width > 600 {
        HStack { content }
    } else {
        VStack { content }
    }
}

// Grid that adapts
LazyVGrid(columns: [
    GridItem(.adaptive(minimum: 150, maximum: 250))
], spacing: 16) {
    ForEach(items) { ItemView(item: $0) }
}
```

## 9. Accessibility

### VoiceOver

```swift
// Labels and hints
Button { } label: {
    Image(systemName: "plus")
}
.accessibilityLabel("Add item")
.accessibilityHint("Creates a new item in your library")

// Grouping related elements
VStack {
    Text(item.title)
    Text(item.subtitle)
}
.accessibilityElement(children: .combine)

// Custom actions
.accessibilityAction(named: "Delete") {
    deleteItem()
}
```

### Keyboard Navigation

```swift
// Focus management
@FocusState private var focusedField: Field?

TextField("Name", text: $name)
    .focused($focusedField, equals: .name)
    .onSubmit {
        focusedField = .email
    }

// Focusable custom views
.focusable()
.onMoveCommand { direction in
    handleArrowKey(direction)
}
```

### Dynamic Type

```swift
// Scales with user preference
Text("Content")
    .dynamicTypeSize(.large ... .accessibility3)

// Fixed size when necessary (use sparingly)
Text("Fixed")
    .dynamicTypeSize(.large)
```

### Reduce Motion

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

.animation(reduceMotion ? .none : .spring(), value: isExpanded)

// Alternative non-animated transitions
.transaction { transaction in
    if reduceMotion {
        transaction.animation = nil
    }
}
```

### High Contrast

```swift
@Environment(\.colorSchemeContrast) var contrast

// Increase contrast when needed
.foregroundStyle(contrast == .increased ? .primary : .secondary)
```

## 10. Modern API Replacements

### Deprecated → Modern

| Deprecated | Modern | Notes |
|------------|--------|-------|
| `NavigationView` | `NavigationSplitView` / `NavigationStack` | Split for macOS, Stack for simple flows |
| `.navigationViewStyle(.columns)` | `NavigationSplitView` | Built-in column support |
| `List { }.listStyle(.sidebar)` with `NavigationLink` | `NavigationSplitView` sidebar | Proper split view behavior |
| `.toolbar { ToolbarItem(...) }` in detail | `.toolbar` on NavigationSplitView | Toolbar applies to correct scope |
| `NSWindowController` | `WindowGroup` / `Window` | Pure SwiftUI window management |
| `NSMenu` / `NSMenuItem` | `.commands { }` / `CommandMenu` | Declarative menus |
| `NSToolbar` | `.toolbar { }` | SwiftUI toolbar API |
| `NSTouchBar` | `.touchBar { }` | SwiftUI Touch Bar |
| `NSOpenPanel.begin()` | `.fileImporter()` | SwiftUI file dialog |
| `NSSavePanel.begin()` | `.fileExporter()` | SwiftUI save dialog |
| `.background(Color.clear)` for materials | `.background(.regularMaterial)` | Proper material support |
| Custom blur effects | `.glassEffect()` (Tahoe) | Native Liquid Glass |

### AppKit Interop (When Needed)

```swift
// Wrap AppKit view
struct NSViewWrapper: NSViewRepresentable {
    func makeNSView(context: Context) -> NSView {
        // Create and configure NSView
    }

    func updateNSView(_ nsView: NSView, context: Context) {
        // Update when SwiftUI state changes
    }
}

// Access NSWindow
.background(WindowAccessor { window in
    window?.titlebarAppearsTransparent = true
})
```

## 11. Review Checklist

### Liquid Glass & Materials

- [ ] Sidebars use `.glassEffect()` or appropriate material
- [ ] Toolbars have translucent appearance
- [ ] Content areas remain clear (not overly translucent)
- [ ] Materials adapt properly to light/dark mode
- [ ] Fallback materials provided for pre-Tahoe

### Navigation & Windows

- [ ] `NavigationSplitView` used for multi-column layouts
- [ ] Sidebar has proper min/max width constraints
- [ ] Inspector panel available for detail/properties
- [ ] Window restoration configured
- [ ] Document-based apps use `DocumentGroup`
- [ ] Multiple window sizes tested

### Controls & Interaction

- [ ] Control sizes appropriate for context
- [ ] Primary actions use `.borderedProminent`
- [ ] Destructive actions properly marked with `.destructive` role
- [ ] Tables have context menus
- [ ] Popovers have appropriate sizing

### Keyboard & Shortcuts

- [ ] Standard shortcuts implemented (⌘N, ⌘S, ⌘W, etc.)
- [ ] Custom shortcuts don't conflict with system
- [ ] All interactive elements keyboard accessible
- [ ] Focus order logical
- [ ] Menu bar commands have shortcuts

### Accessibility

- [ ] All images have accessibility labels
- [ ] Custom controls have proper roles
- [ ] VoiceOver tested
- [ ] Keyboard navigation complete
- [ ] Reduce Motion respected
- [ ] High Contrast mode tested

### Platform Conventions

- [ ] App uses system appearance (not custom chrome)
- [ ] Settings in Preferences window (not separate)
- [ ] File dialogs use system sheets
- [ ] Drag and drop supported where expected
- [ ] Services menu integration (if applicable)

### Visual Polish

- [ ] 8-point grid alignment
- [ ] Consistent spacing throughout
- [ ] Semantic colors used (adapts to themes)
- [ ] Typography follows SF Pro guidelines
- [ ] Minimum 44pt touch targets

## Quick Reference: Control Shapes by Size

```
┌─────────────────────────────────────────────────────┐
│  Mini/Small/Medium      │    Large/XLarge           │
│  ┌──────────────────┐   │    ╭──────────────────╮   │
│  │   Rounded Rect   │   │    │     Capsule      │   │
│  └──────────────────┘   │    ╰──────────────────╯   │
│                         │                           │
│  Compact layouts        │    Hero actions           │
│  Toolbars, sidebars     │    Onboarding, CTAs       │
└─────────────────────────────────────────────────────┘
```

## Quick Reference: Window Styles

```
┌─────────────────────────────────────────────────────┐
│  .automatic        Standard window with titlebar    │
│  .hiddenTitleBar   Full content, titlebar hidden    │
│  .plain            No chrome, utility panels        │
│  .unified          Toolbar merges with titlebar     │
│  .unifiedCompact   Compact unified toolbar          │
└─────────────────────────────────────────────────────┘
```

## Quick Reference: Navigation Patterns

```
┌─────────────┬───────────────┬─────────────────────┐
│  Sidebar    │   Content     │      Detail         │
│             │               │                     │
│  Source     │   List or     │   Selected item     │
│  List       │   Grid        │   properties        │
│             │               │                     │
│  Collections│   Items       │   Inspector panel   │
│  Folders    │   Browse      │   Edit view         │
│             │               │                     │
│  Min: 180   │   Flexible    │   Min: 300          │
│  Max: 300   │               │   Ideal: 400+       │
└─────────────┴───────────────┴─────────────────────┘
       NavigationSplitView (three-column)
```
