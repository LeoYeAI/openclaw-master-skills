---
name: fosmvvm-ui-tests-generator
description: Generate UI tests for FOSMVVM SwiftUI views using XCTest and FOSTestingUI. Covers accessibility identifiers, ViewModelOperations, and test data transport.
homepage: https://github.com/foscomputerservices/FOSUtilities
metadata: {"clawdbot": {"emoji": "🖥️", "os": ["darwin"]}}
---

# FOSMVVM UI Tests Generator

Generate comprehensive UI tests for ViewModelViews in FOSMVVM applications.

## Conceptual Foundation

> For full architecture context, see [FOSMVVMArchitecture.md](../../docs/FOSMVVMArchitecture.md) | [OpenClaw reference]({baseDir}/references/FOSMVVMArchitecture.md)

UI testing in FOSMVVM follows a specific pattern that leverages:
- **FOSTestingUI** framework for test infrastructure
- **ViewModelOperations** for verifying business logic was invoked
- **Accessibility identifiers** for finding UI elements
- **Test data transporter** for passing operation stubs to the app

```
┌─────────────────────────────────────────────────────────────┐
│                    UI Test Architecture                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Test File (XCTest)                 App Under Test          │
│  ┌──────────────────┐              ┌──────────────────┐     │
│  │ MyViewUITests    │              │ MyView           │     │
│  │                  │              │                  │     │
│  │ presentView() ───┼─────────────►│ Show view with   │     │
│  │   with stub VM   │              │   stubbed data   │     │
│  │                  │              │                  │     │
│  │ Interact via ────┼─────────────►│ UI elements with │     │
│  │   identifiers    │              │   .uiTestingId   │     │
│  │                  │              │                  │     │
│  │ Assert on UI     │              │ .testData────────┼──┐  │
│  │   state          │              │   Transporter    │  │  │
│  │                  │              └──────────────────┘  │  │
│  │ viewModelOps() ◄─┼─────────────────────────────────────┘  │
│  │   verify calls   │              Stub Operations          │
│  └──────────────────┘                                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Base Test Case Class

Every project should have a base test case that inherits from `ViewModelViewTestCase`:

```swift
class MyAppViewModelViewTestCase<VM: ViewModel, VMO: ViewModelOperations>:
    ViewModelViewTestCase<VM, VMO>, @unchecked Sendable {

    @MainActor func presentView(
        configuration: TestConfiguration,
        viewModel: VM = .stub(),
        timeout: TimeInterval = 3
    ) throws -> XCUIApplication {
        try presentView(
            testConfiguration: configuration.toJSON(),
            viewModel: viewModel,
            timeout: timeout
        )
    }

    override func setUp() async throws {
        try await super.setUp(
            bundle: Bundle.main,
            resourceDirectoryName: "",
            appBundleIdentifier: "com.example.MyApp"
        )

        continueAfterFailure = false
    }
}
```

**Key points:**
- Generic over `ViewModel` and `ViewModelOperations`
- Wraps FOSTestingUI's `presentView()` with project-specific configuration
- Sets up bundle and app bundle identifier
- `continueAfterFailure = false` stops tests immediately on failure

### 2. Individual UI Test Files

Each ViewModelView gets a corresponding UI test file.

**For views WITH operations:**

```swift
final class MyViewUITests: MyAppViewModelViewTestCase<MyViewModel, MyViewOps> {
    // UI Tests - verify UI state
    func testButtonEnabled() async throws {
        let app = try presentView(viewModel: .stub(enabled: true))
        XCTAssertTrue(app.myButton.isEnabled)
    }

    // Operation Tests - verify operations were called
    func testButtonTap() async throws {
        let app = try presentView(configuration: .requireSomeState())
        app.myButton.tap()

        let stubOps = try viewModelOperations()
        XCTAssertTrue(stubOps.myOperationCalled)
    }
}

private extension XCUIApplication {
    var myButton: XCUIElement {
        buttons.element(matching: .button, identifier: "myButtonIdentifier")
    }
}
```

**For views WITHOUT operations** (display-only):

Use an empty stub operations protocol:

```swift
// In your test file
protocol MyViewStubOps: ViewModelOperations {}
struct MyViewStubOpsImpl: MyViewStubOps {}

final class MyViewUITests: MyAppViewModelViewTestCase<MyViewModel, MyViewStubOpsImpl> {
    // UI Tests only - no operation verification
    func testDisplaysCorrectly() async throws {
        let app = try presentView(viewModel: .stub(title: "Test"))
        XCTAssertTrue(app.titleLabel.exists)
    }
}
```

**When to use each:**
- **With operations**: Interactive views that perform actions (forms, buttons that call APIs, etc.)
- **Without operations**: Display-only views (cards, detail views, static content)

### 3. XCUIElement Helper Extensions

Common helpers for interacting with UI elements:

```swift
extension XCUIElement {
    var text: String? {
        value as? String
    }

    func typeTextAndWait(_ string: String, timeout: TimeInterval = 2) {
        typeText(string)
        _ = wait(for: \.text, toEqual: string, timeout: timeout)
    }

    func tapMenu() {
        if isHittable {
            tap()
        } else {
            coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.5)).tap()
        }
    }
}
```

### 4. View Requirements

**For views WITH operations:**

```swift
public struct MyView: ViewModelView {
    #if DEBUG
    @State private var repaintToggle = false
    #endif

    private let viewModel: MyViewModel
    private let operations: MyViewModelOperations

    public var body: some View {
        Button(action: doSomething) {
            Text(viewModel.buttonLabel)
        }
        .uiTestingIdentifier("myButtonIdentifier")
        #if DEBUG
        .testDataTransporter(viewModelOps: operations, repaintToggle: $repaintToggle)
        #endif
    }

    public init(viewModel: MyViewModel) {
        self.viewModel = viewModel
        self.operations = viewModel.operations
    }

    private func doSomething() {
        operations.doSomething()
        toggleRepaint()
    }

    private func toggleRepaint() {
        #if DEBUG
        repaintToggle.toggle()
        #endif
    }
}
```

**For views WITHOUT operations** (display-only):

```swift
public struct MyView: ViewModelView {
    private let viewModel: MyViewModel

    public var body: some View {
        VStack {
            Text(viewModel.title)
            Text(viewModel.description)
        }
        .uiTestingIdentifier("mainContent")
    }

    public init(viewModel: MyViewModel) {
        self.viewModel = viewModel
    }
}
```

**Critical patterns (for views WITH operations):**
- `@State private var repaintToggle = false` for triggering test data transport
- `.testDataTransporter(viewModelOps:repaintToggle:)` modifier in DEBUG
- `toggleRepaint()` called after every operation invocation
- `operations` stored as property from `viewModel.operations`

**Display-only views:**
- No `repaintToggle` needed
- No `.testDataTransporter()` modifier needed
- Just add `.uiTestingIdentifier()` to elements you want to test

## ViewModelOperations: Optional

Not all views need ViewModelOperations:

**Views that NEED operations:**
- Forms with submit/cancel actions
- Views that call business logic or APIs
- Interactive views that trigger app state changes
- Views with user-initiated async operations

**Views that DON'T NEED operations:**
- Display-only cards or detail views
- Static content views
- Pure navigation containers
- Server-hosted views that just render data

**For views without operations:**

Create an empty operations file alongside your ViewModel:

```swift
// MyDisplayViewModelOperations.swift
import FOSMVVM
import Foundation

public protocol MyDisplayViewModelOperations: ViewModelOperations {}

#if canImport(SwiftUI)
public final class MyDisplayViewStubOps: MyDisplayViewModelOperations, @unchecked Sendable {
    public init() {}
}
#endif
```

Then use it in tests:

```swift
final class MyDisplayViewUITests: MyAppViewModelViewTestCase<
    MyDisplayViewModel,
    MyDisplayViewStubOps
> {
    // Only test UI state, no operation verification
}
```

The view itself doesn't need:
- `repaintToggle` state
- `.testDataTransporter()` modifier
- `operations` property
- `toggleRepaint()` function

Just add `.uiTestingIdentifier()` to elements you want to verify.

## Test Categories

### UI State Tests

Verify that the UI displays correctly based on ViewModel state:

```swift
func testButtonDisabledWhenNotReady() async throws {
    let app = try presentView(viewModel: .stub(ready: false))
    XCTAssertFalse(app.submitButton.isEnabled)
}

func testButtonEnabledWhenReady() async throws {
    let app = try presentView(viewModel: .stub(ready: true))
    XCTAssertTrue(app.submitButton.isEnabled)
}
```

### Operation Tests

Verify that user interactions invoke the correct operations:

```swift
func testSubmitButtonInvokesOperation() async throws {
    let app = try presentView(configuration: .requireAuth())
    app.submitButton.tap()

    let stubOps = try viewModelOperations()
    XCTAssertTrue(stubOps.submitCalled)
    XCTAssertFalse(stubOps.cancelCalled)
}
```

### Navigation Tests

Verify navigation flows work correctly:

```swift
func testNavigationToDetailView() async throws {
    let app = try presentView()
    app.itemRow.tap()

    XCTAssertTrue(app.detailView.exists)
}
```

## When to Use This Skill

- Adding UI tests for a new ViewModelView
- Setting up UI test infrastructure for a FOSMVVM project
- Following an implementation plan that requires test coverage
- Validating user interaction flows

## What This Skill Generates

### Initial Setup (once per project)

| File | Location | Purpose |
|------|----------|---------|
| `{ProjectName}ViewModelViewTestCase.swift` | `Tests/UITests/Support/` | Base test case for all UI tests |
| `XCUIElement.swift` | `Tests/UITests/Support/` | Helper extensions for XCUIElement |

### Per ViewModelView

| File | Location | Purpose |
|------|----------|---------|
| `{ViewName}ViewModelOperations.swift` | `Sources/{ViewModelsTarget}/{Feature}/` | Operations protocol and stub (if view has interactions) |
| `{ViewName}UITests.swift` | `Tests/UITests/Views/{Feature}/` | UI tests for the view |

**Note:** Views without user interactions use an empty operations file with just the protocol and minimal stub.

## Project Structure Configuration

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{ProjectName}` | Your project/app name | `MyApp`, `TaskManager` |
| `{ViewName}` | The ViewModelView name (without "View" suffix) | `TaskList`, `Dashboard` |
| `{Feature}` | Feature/module grouping | `Tasks`, `Settings` |

## How to Use This Skill

**Invocation:**
/fosmvvm-ui-tests-generator

**Prerequisites:**
- View and ViewModel structure understood from conversation context
- ViewModelOperations type identified (or confirmed as display-only)
- Interactive elements and user flows discussed

**Workflow integration:**
This skill is typically used after implementing ViewModelViews. The skill references conversation context automatically—no file paths or Q&A needed. Often follows fosmvvm-swiftui-view-generator or fosmvvm-react-view-generator.

## Pattern Implementation

This skill references conversation context to determine test structure:

### Test Type Detection

From conversation context, the skill identifies:
- **First test vs additional test** (whether base test infrastructure exists)
- **ViewModel type** (from prior discussion or View implementation)
- **ViewModelOperations type** (from View implementation or context)
- **Interactive vs display-only** (whether operations need verification)

### View Analysis

From requirements already in context:
- **Interactive elements** (buttons, fields, controls requiring test coverage)
- **User flows** (navigation paths, form submission, drag-and-drop)
- **State variations** (enabled/disabled, visible/hidden, error states)
- **Operation triggers** (which UI actions invoke which operations)

### Infrastructure Planning

Based on project state:
- **Base test case** (create if first test, reuse if exists)
- **XCUIElement extensions** (helper methods for common interactions)
- **App bundle identifier** (for launching test host)

### Test File Generation

For the specific view:
1. Test class inheriting from base test case
2. UI state tests (verify display based on ViewModel)
3. Operation tests (verify user interactions invoke operations)
4. XCUIApplication extension with element accessors

### View Requirements

Ensure test identifiers and data transport:
1. `.uiTestingIdentifier()` on all interactive elements
2. `@State private var repaintToggle` (if has operations)
3. `.testDataTransporter()` modifier (if has operations)
4. `toggleRepaint()` calls after operations (if has operations)

### Context Sources

Skill references information from:
- **Prior conversation**: View requirements, user flows discussed
- **View implementation**: If Claude has read View code into context
- **ViewModelOperations**: From codebase or discussion

## Key Patterns

### Test Configuration Pattern

Use `TestConfiguration` for tests that need specific app state:

```swift
func testWithSpecificState() async throws {
    let app = try presentView(
        configuration: .requireAuth(userId: "123")
    )
    // Test with authenticated state
}
```

### Element Accessor Pattern

Define element accessors in a private extension:

```swift
private extension XCUIApplication {
    var submitButton: XCUIElement {
        buttons.element(matching: .button, identifier: "submitButton")
    }

    var cancelButton: XCUIElement {
        buttons.element(matching: .button, identifier: "cancelButton")
    }

    var firstItem: XCUIElement {
        buttons.element(matching: .button, identifier: "itemButton").firstMatch
    }
}
```

### Operation Verification Pattern

After user interactions, verify operations were called:

```swift
func testDecrementButton() async throws {
    let app = try presentView(configuration: .requireDevice())
    app.decrementButton.tap()

    let stubOps = try viewModelOperations()
    XCTAssertTrue(stubOps.decrementCalled)
    XCTAssertFalse(stubOps.incrementCalled)
}
```

### Orientation Setup Pattern

Set device orientation in `setUp()` if needed:

```swift
override func setUp() async throws {
    try await super.setUp()

    #if os(iOS)
    XCUIDevice.shared.orientation = .portrait
    #endif
}
```

## View Testing Checklist

**All views:**
- [ ] `.uiTestingIdentifier()` on all elements you want to test

**Views WITH operations (interactive views):**
- [ ] `@State private var repaintToggle = false` property
- [ ] `.testDataTransporter(viewModelOps:repaintToggle:)` modifier
- [ ] `toggleRepaint()` helper function
- [ ] `toggleRepaint()` called after every operation invocation
- [ ] `operations` stored from `viewModel.operations` in init

**Views WITHOUT operations (display-only):**
- [ ] No `repaintToggle` needed
- [ ] No `.testDataTransporter()` needed
- [ ] No `operations` property needed
- [ ] `operations` stored from `viewModel.operations` in init

## Common Test Patterns

### Testing Async Operations

```swift
func testAsyncOperation() async throws {
    let app = try presentView()
    app.loadButton.tap()

    // Wait for UI to update
    _ = app.waitForExistence(timeout: 3)

    let stubOps = try viewModelOperations()
    XCTAssertTrue(stubOps.loadCalled)
}
```

### Testing Form Input

```swift
func testFormInput() async throws {
    let app = try presentView()

    let emailField = app.emailTextField
    emailField.tap()
    emailField.typeTextAndWait("user@example.com")

    app.submitButton.tap()

    let stubOps = try viewModelOperations()
    XCTAssertTrue(stubOps.submitCalled)
}
```

### Testing Error States

```swift
func testErrorDisplay() async throws {
    let app = try presentView(viewModel: .stub(hasError: true))

    XCTAssertTrue(app.errorAlert.exists)
    XCTAssertEqual(app.errorMessage.text, "An error occurred")
}
```

## File Templates

See [reference.md](reference.md) for complete file templates.

## Naming Conventions

| Concept | Convention | Example |
|---------|------------|---------|
| Base test case | `{ProjectName}ViewModelViewTestCase` | `MyAppViewModelViewTestCase` |
| UI test file | `{ViewName}UITests` | `TaskListViewUITests` |
| Test method (UI state) | `test{Condition}` | `testButtonEnabled` |
| Test method (operation) | `test{Action}` | `testSubmitButton` |
| Element accessor | `{elementName}` | `submitButton`, `emailTextField` |
| UI testing identifier | `{elementName}Identifier` or `{elementName}` | `"submitButton"`, `"emailTextField"` |

## See Also

- [Architecture Patterns](../shared/architecture-patterns.md) - Mental models and patterns
- [FOSMVVMArchitecture.md](../../docs/FOSMVVMArchitecture.md) - Full FOSMVVM architecture
- [fosmvvm-viewmodel-generator](../fosmvvm-viewmodel-generator/SKILL.md) - For creating ViewModels
- [fosmvvm-swiftui-app-setup](../fosmvvm-swiftui-app-setup/SKILL.md) - For app test host setup
- [reference.md](reference.md) - Complete file templates

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-23 | Initial skill for UI tests |
| 1.1 | 2026-01-24 | Update to context-aware approach (remove file-parsing/Q&A). Skill references conversation context instead of asking questions or accepting file paths. |
