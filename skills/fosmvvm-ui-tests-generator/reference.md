# FOSMVVM UI Tests Generator - Reference Templates

Complete file templates for generating UI tests for FOSMVVM ViewModelViews.

> **Conceptual context:** See [SKILL.md](SKILL.md) for when and why to use this skill.
> **Architecture context:** See [FOSMVVMArchitecture.md](../../docs/FOSMVVMArchitecture.md) for full FOSMVVM understanding.

## Placeholders

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `{ProjectName}` | Your project/app name | `MyApp`, `TaskManager` |
| `{ViewName}` | ViewModelView name (without "View" suffix) | `TaskList`, `Dashboard` |
| `{ViewModel}` | Full ViewModel type name | `TaskListViewModel` |
| `{Operations}` | Full ViewModelOperations type name | `TaskListViewModelOperations` |
| `{Feature}` | Feature/module grouping | `Tasks`, `Settings` |
| `{BundleId}` | App bundle identifier | `com.example.MyApp` |

---

# Template 1: Base Test Case Class

**One per project** - All UI tests inherit from this.

**Location:** `Tests/UITests/Support/{ProjectName}ViewModelViewTestCase.swift`

```swift
// {ProjectName}ViewModelViewTestCase.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import FOSFoundation
import FOSMVVM
import FOSTestingUI
import Foundation
import XCTest

class {ProjectName}ViewModelViewTestCase<VM: ViewModel, VMO: ViewModelOperations>:
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
            appBundleIdentifier: "{BundleId}"
        )

        continueAfterFailure = false // Stop the test and move on
    }
}
```

---

# Template 2: XCUIElement Extensions

**One per project** - Helper methods for XCUIElement interactions.

**Location:** `Tests/UITests/Support/XCUIElement.swift`

```swift
// XCUIElement.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import XCTest

extension XCUIElement {
    /// Get the text value of the element
    var text: String? {
        value as? String
    }

    /// Type text and wait for it to appear
    func typeTextAndWait(_ string: String, timeout: TimeInterval = 2) {
        typeText(string)
        _ = wait(for: \.text, toEqual: string, timeout: timeout)
    }

    /// Tap, then type text and wait
    func selectTypeTextAndWait(_ string: String, timeout: TimeInterval = 2) {
        tap()
        typeTextAndWait(string, timeout: timeout)
    }

    /// Tap SwiftUI Menu elements
    ///
    /// SwiftUI Menu elements are often not marked as 'isHittable', so tap() will not work.
    /// This method taps the coordinate of the menu to skip the 'isHittable' test.
    func tapMenu() {
        if isHittable {
            tap()
        } else {
            coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.5)).tap()
        }
    }
}
```

---

# ViewModelOperations: When to Use

Not all views need ViewModelOperations. The decision depends on whether the view has user interactions that trigger business logic.

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

**For views without operations**, create an empty operations file alongside your ViewModel.

See **Template 10: Empty ViewModelOperations File** for the complete pattern.

---

# Template 3: Display-Only View Test (No Operations)

**For views that don't have ViewModelOperations** - Display-only, no user interactions.

**Location:** `Tests/UITests/Views/{Feature}/{ViewName}UITests.swift`

```swift
// {ViewName}UITests.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import FOSFoundation
import FOSMVVM
import FOSTestingUI
import Foundation
import ViewModels
import XCTest

final class {ViewName}UITests: {ProjectName}ViewModelViewTestCase<
    {ViewModel},
    {ViewName}StubOps
>, @unchecked Sendable {
    // MARK: UI Tests

    func testDisplaysTitle() async throws {
        let app = try presentView(
            viewModel: .stub(title: "Test Title")
        )

        XCTAssertTrue(app.titleLabel.exists)
    }

    func testDisplaysContent() async throws {
        let app = try presentView(
            viewModel: .stub(content: "Test Content")
        )

        XCTAssertTrue(app.contentText.exists)
    }

    func testDisplaysImage() async throws {
        let app = try presentView()

        XCTAssertTrue(app.mainImage.exists)
    }

    // MARK: Setup

    override func setUp() async throws {
        try await super.setUp()

        #if os(iOS)
        XCUIDevice.shared.orientation = .portrait
        #endif
    }
}

// MARK: - XCUIApplication Extensions

private extension XCUIApplication {
    var titleLabel: XCUIElement {
        staticTexts["titleLabel"]
    }

    var contentText: XCUIElement {
        staticTexts["contentText"]
    }

    var mainImage: XCUIElement {
        images["mainImage"]
    }
}
```

---

# Template 4: Basic UI Test File (With Operations)

**One per ViewModelView** - Tests for a simple interactive view.

**Location:** `Tests/UITests/Views/{Feature}/{ViewName}UITests.swift`

```swift
// {ViewName}UITests.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import FOSFoundation
import FOSMVVM
import FOSTestingUI
import Foundation
import ViewModels
import XCTest

final class {ViewName}UITests: {ProjectName}ViewModelViewTestCase<
    {ViewModel},
    {Operations}
>, @unchecked Sendable {
    // MARK: UI Tests

    func testInitialState() async throws {
        let app = try presentView()

        XCTAssertTrue(app.mainContent.exists)
    }

    func testButtonEnabled() async throws {
        let app = try presentView(
            viewModel: .stub(enabled: true)
        )

        XCTAssertTrue(app.actionButton.isEnabled)
    }

    func testButtonDisabled() async throws {
        let app = try presentView(
            viewModel: .stub(enabled: false)
        )

        XCTAssertFalse(app.actionButton.isEnabled)
    }

    // MARK: Operation Tests

    func testActionButton() async throws {
        let app = try presentView(
            configuration: .default
        )

        app.actionButton.tap()

        let stubOps = try viewModelOperations()
        XCTAssertTrue(stubOps.actionCalled)
    }

    // MARK: Setup

    override func setUp() async throws {
        try await super.setUp()

        #if os(iOS)
        XCUIDevice.shared.orientation = .portrait
        #endif
    }
}

// MARK: - XCUIApplication Extensions

private extension XCUIApplication {
    var mainContent: XCUIElement {
        otherElements["mainContent"]
    }

    var actionButton: XCUIElement {
        buttons.element(matching: .button, identifier: "actionButton")
    }
}
```

---

# Template 5: Advanced UI Test File (With Operations)

**For views with multiple interactions** - Comprehensive test coverage.

**Location:** `Tests/UITests/Views/{Feature}/{ViewName}UITests.swift`

```swift
// {ViewName}UITests.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import FOSFoundation
import FOSMVVM
import FOSTestingUI
import Foundation
import ViewModels
import XCTest

final class {ViewName}UITests: {ProjectName}ViewModelViewTestCase<
    {ViewModel},
    {Operations}
>, @unchecked Sendable {
    // MARK: UI State Tests

    func testEmptyState() async throws {
        let app = try presentView(
            viewModel: .stub(items: [])
        )

        XCTAssertTrue(app.emptyStateMessage.exists)
        XCTAssertFalse(app.itemList.exists)
    }

    func testItemsDisplayed() async throws {
        let app = try presentView(
            viewModel: .stub(
                items: [
                    .stub(id: .init(), title: "Item 1"),
                    .stub(id: .init(), title: "Item 2")
                ]
            )
        )

        XCTAssertFalse(app.emptyStateMessage.exists)
        XCTAssertTrue(app.itemList.exists)
    }

    func testLoadingState() async throws {
        let app = try presentView(
            viewModel: .stub(isLoading: true)
        )

        XCTAssertTrue(app.loadingIndicator.exists)
    }

    // MARK: Interaction Tests

    func testSelectItem() async throws {
        let app = try presentView()

        XCTAssertFalse(app.detailButton.isEnabled)

        app.firstItemButton.tap()

        XCTAssertTrue(app.detailButton.isEnabled)
    }

    func testFormInput() async throws {
        let app = try presentView()

        app.nameTextField.tap()
        app.nameTextField.typeTextAndWait("Test Name")

        app.emailTextField.tap()
        app.emailTextField.typeTextAndWait("test@example.com")

        app.submitButton.tap()

        let stubOps = try viewModelOperations()
        XCTAssertTrue(stubOps.submitCalled)
    }

    // MARK: Operation Tests

    func testRefresh() async throws {
        let app = try presentView(
            configuration: .requireAuth()
        )

        app.refreshButton.tap()

        let stubOps = try viewModelOperations()
        XCTAssertTrue(stubOps.refreshCalled)
    }

    func testDelete() async throws {
        let app = try presentView(
            configuration: .requireAuth()
        )

        app.firstItemButton.tap()
        app.deleteButton.tap()

        let stubOps = try viewModelOperations()
        XCTAssertTrue(stubOps.deleteCalled)
        XCTAssertFalse(stubOps.submitCalled)
    }

    func testCancel() async throws {
        let app = try presentView()

        app.cancelButton.tap()

        let stubOps = try viewModelOperations()
        XCTAssertTrue(stubOps.cancelCalled)
    }

    // MARK: Navigation Tests

    func testNavigationToDetail() async throws {
        let app = try presentView()

        app.firstItemButton.tap()
        app.viewDetailButton.tap()

        XCTAssertTrue(app.detailView.exists)
    }

    // MARK: Error Handling Tests

    func testErrorDisplayed() async throws {
        let app = try presentView(
            viewModel: .stub(hasError: true)
        )

        XCTAssertTrue(app.errorAlert.exists)
    }

    func testErrorDismissal() async throws {
        let app = try presentView(
            viewModel: .stub(hasError: true)
        )

        app.dismissErrorButton.tap()

        XCTAssertFalse(app.errorAlert.exists)
    }

    // MARK: Setup

    override class var runsForEachTargetApplicationUIConfiguration: Bool {
        false
    }

    override func setUp() async throws {
        try await super.setUp()

        #if os(iOS)
        XCUIDevice.shared.orientation = .portrait
        #endif
    }
}

// MARK: - XCUIApplication Extensions

private extension XCUIApplication {
    // Main Content
    var itemList: XCUIElement {
        tables["itemList"]
    }

    var emptyStateMessage: XCUIElement {
        staticTexts["emptyStateMessage"]
    }

    var loadingIndicator: XCUIElement {
        activityIndicators["loadingIndicator"]
    }

    // Buttons
    var refreshButton: XCUIElement {
        buttons.element(matching: .button, identifier: "refreshButton")
    }

    var submitButton: XCUIElement {
        buttons.element(matching: .button, identifier: "submitButton")
    }

    var cancelButton: XCUIElement {
        buttons.element(matching: .button, identifier: "cancelButton")
    }

    var deleteButton: XCUIElement {
        buttons.element(matching: .button, identifier: "deleteButton")
    }

    var detailButton: XCUIElement {
        buttons.element(matching: .button, identifier: "detailButton")
    }

    var viewDetailButton: XCUIElement {
        buttons.element(matching: .button, identifier: "viewDetailButton")
    }

    var dismissErrorButton: XCUIElement {
        buttons.element(matching: .button, identifier: "dismissErrorButton")
    }

    // Items
    var firstItemButton: XCUIElement {
        buttons.element(matching: .button, identifier: "itemButton").firstMatch
    }

    // Text Fields
    var nameTextField: XCUIElement {
        textFields["nameTextField"]
    }

    var emailTextField: XCUIElement {
        textFields["emailTextField"]
    }

    // Views
    var detailView: XCUIElement {
        otherElements["detailView"]
    }

    var errorAlert: XCUIElement {
        alerts["errorAlert"]
    }
}
```

---

# Template 6: Display-Only View (No Operations)

**For views that only display data** - No user interactions, no operations.

**Location:** `Sources/{ViewsTarget}/{Feature}/{ViewName}View.swift`

```swift
// {ViewName}View.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import FOSFoundation
import FOSMVVM
import Foundation
import SwiftUI
import ViewModels

public struct {ViewName}View: ViewModelView {
    private let viewModel: {ViewModel}

    public var body: some View {
        VStack {
            Text(viewModel.title)
                .font(.headline)
                .uiTestingIdentifier("titleLabel")

            Text(viewModel.description)
                .uiTestingIdentifier("descriptionText")

            if let imageURL = viewModel.imageURL {
                AsyncImage(url: imageURL)
                    .uiTestingIdentifier("mainImage")
            }
        }
        .padding()
    }

    public init(viewModel: {ViewModel}) {
        self.viewModel = viewModel
    }
}

#if DEBUG
#Preview {
    {ViewName}View.previewHost(
        bundle: MyAppResourceAccess.localizationBundle
    )
}
#endif
```

---

# Template 7: View with Test Infrastructure (With Operations)

**The view being tested** - Includes test support for operations.

**Location:** `Sources/{ViewsTarget}/{Feature}/{ViewName}View.swift`

```swift
// {ViewName}View.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import FOSFoundation
import FOSMVVM
import Foundation
import SwiftUI
import ViewModels

public struct {ViewName}View: ViewModelView {
    #if DEBUG
    @State private var repaintToggle = false
    #endif

    private let viewModel: {ViewModel}
    private let operations: {Operations}

    public var body: some View {
        VStack {
            Text(viewModel.title)
                .font(.headline)

            Button(action: performAction) {
                Text(viewModel.actionButtonLabel)
            }
            .uiTestingIdentifier("actionButton")

            Button(role: .cancel, action: cancel) {
                Text(viewModel.cancelButtonLabel)
            }
            .uiTestingIdentifier("cancelButton")
        }
        #if DEBUG
        .testDataTransporter(viewModelOps: operations, repaintToggle: $repaintToggle)
        #endif
    }

    public init(viewModel: {ViewModel}) {
        self.viewModel = viewModel
        self.operations = viewModel.operations
    }
}

private extension {ViewName}View {
    func performAction() {
        operations.performAction()
        toggleRepaint()
    }

    func cancel() {
        operations.cancel()
        toggleRepaint()
    }

    func toggleRepaint() {
        #if DEBUG
        repaintToggle.toggle()
        #endif
    }
}

#if DEBUG
#Preview {
    {ViewName}View.previewHost(
        bundle: MyAppResourceAccess.localizationBundle
    )
}
#endif
```

---

# Template 8: View with Async Operations

**For views with async operations** - Includes error handling.

**Location:** `Sources/{ViewsTarget}/{Feature}/{ViewName}View.swift`

```swift
// {ViewName}View.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import FOSFoundation
import FOSMVVM
import Foundation
import SwiftUI
import ViewModels

public struct {ViewName}View: ViewModelView {
    @State private var error: Error?
    @State private var isLoading = false

    #if DEBUG
    @State private var repaintToggle = false
    #endif

    private let viewModel: {ViewModel}
    private let operations: {Operations}

    public var body: some View {
        VStack {
            if isLoading {
                ProgressView()
                    .uiTestingIdentifier("loadingIndicator")
            } else {
                contentView
            }
        }
        .task(errorBinding: $error) {
            try await loadData()
        }
        .alert(
            errorBinding: $error,
            title: viewModel.errorTitle,
            message: viewModel.errorMessage,
            dismissButtonLabel: viewModel.dismissButtonLabel
        )
        #if DEBUG
        .testDataTransporter(viewModelOps: operations, repaintToggle: $repaintToggle)
        #endif
    }

    private var contentView: some View {
        VStack {
            Text(viewModel.title)

            Button(errorBinding: $error, asyncAction: submit) {
                Text(viewModel.submitButtonLabel)
            }
            .uiTestingIdentifier("submitButton")
        }
    }

    public init(viewModel: {ViewModel}) {
        self.viewModel = viewModel
        self.operations = viewModel.operations
    }
}

private extension {ViewName}View {
    func loadData() async throws {
        isLoading = true
        try await operations.loadData()
        isLoading = false
        toggleRepaint()
    }

    @Sendable func submit() async throws {
        try await operations.submit()
        toggleRepaint()
    }

    func toggleRepaint() {
        #if DEBUG
        repaintToggle.toggle()
        #endif
    }
}

#if DEBUG
#Preview {
    {ViewName}View.previewHost(
        bundle: MyAppResourceAccess.localizationBundle
    )
}
#endif
```

---

# Template 9: View with Form and List

**Complex view example** - Form input and list display.

**Location:** `Sources/{ViewsTarget}/{Feature}/{ViewName}View.swift`

```swift
// {ViewName}View.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import FOSFoundation
import FOSMVVM
import Foundation
import SwiftUI
import ViewModels

public struct {ViewName}View: ViewModelView {
    @State private var items: [ItemViewModel] = []
    @State private var selectedId: ModelIdType?
    @State private var error: Error?

    #if DEBUG
    @State private var repaintToggle = false
    #endif

    private let viewModel: {ViewModel}
    private let operations: {Operations}

    public var body: some View {
        VStack {
            Text(viewModel.title)
                .font(.headline)

            if items.isEmpty {
                Text(viewModel.emptyStateMessage)
                    .uiTestingIdentifier("emptyStateMessage")
            } else {
                ScrollView {
                    VStack {
                        ForEach(items) { item in
                            Button { selectItem(item.id) } label: {
                                HStack {
                                    Text(item.title)
                                    if item.id == selectedId {
                                        Spacer()
                                        Image(systemName: "checkmark")
                                    }
                                }
                            }
                            .uiTestingIdentifier("itemButton")
                        }
                    }
                }
                .uiTestingIdentifier("itemList")
            }

            Spacer()

            HStack {
                Button(role: .cancel, action: cancel) {
                    Text(viewModel.cancelButtonLabel)
                }
                .uiTestingIdentifier("cancelButton")

                Spacer()

                Button(errorBinding: $error, asyncAction: submit) {
                    Text(viewModel.submitButtonLabel)
                }
                .buttonStyle(PrimaryButtonStyle())
                .uiTestingIdentifier("submitButton")
                .disabled(selectedId == nil)
            }
        }
        .task(errorBinding: $error) {
            try await loadItems()
        }
        .alert(
            errorBinding: $error,
            title: viewModel.errorTitle,
            message: viewModel.errorMessage,
            dismissButtonLabel: viewModel.dismissButtonLabel
        )
        #if DEBUG
        .testDataTransporter(viewModelOps: operations, repaintToggle: $repaintToggle)
        #endif
    }

    public init(viewModel: {ViewModel}) {
        self.viewModel = viewModel
        self.operations = viewModel.operations
    }
}

private extension {ViewName}View {
    func loadItems() async throws {
        let stream = operations.loadItems()
        toggleRepaint()

        for try await item in stream {
            items.append(item)
        }
    }

    func selectItem(_ id: ModelIdType) {
        if selectedId == id {
            selectedId = nil
        } else {
            selectedId = id
        }
        toggleRepaint()
    }

    @Sendable func submit() async throws {
        guard let selectedId else { return }
        try await operations.submit(itemId: selectedId)
        toggleRepaint()
    }

    func cancel() {
        operations.cancel()
        toggleRepaint()
    }

    func toggleRepaint() {
        #if DEBUG
        repaintToggle.toggle()
        #endif
    }
}

#if DEBUG
#Preview {
    {ViewName}View.previewHost(
        bundle: MyAppResourceAccess.localizationBundle
    )
}
#endif
```

---

# Template 10: ViewModelOperations File (With Operations)

**For interactive views** - Operations protocol, real implementation, and stub for testing.

**Structure:**
- **Protocol** - Defines the operations interface
- **Real implementation** (struct) - Does the actual work (API calls, business logic)
- **Stub implementation** (class) - Tracks calls for testing, returns mock data

**Location:** `Sources/{ViewModelsTarget}/{Feature}/{ViewName}ViewModelOperations.swift`

```swift
// {ViewName}ViewModelOperations.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import FOSFoundation
import FOSMVVM
import Foundation
#if canImport(SwiftUI)
import SwiftUI
#endif

#if canImport(SwiftUI)

// MARK: - Operations Protocol

public protocol {ViewName}ViewModelOperations: ViewModelOperations {
    func performAction() async throws
    func cancel()
    func loadData() -> AsyncThrowingStream<ItemData, Error>
}

// MARK: - Real Implementation

public struct {ViewName}Ops: {ViewName}ViewModelOperations {
    public func performAction() async throws {
        // Real implementation that calls APIs, updates state, etc.
    }

    public func cancel() {
        // Real cancellation logic
    }

    public func loadData() -> AsyncThrowingStream<ItemData, Error> {
        AsyncThrowingStream { continuation in
            Task {
                do {
                    // Real data loading logic
                    let data = try await fetchFromAPI()
                    continuation.yield(data)
                    continuation.finish()
                } catch {
                    continuation.finish(throwing: error)
                }
            }
        }
    }

    public init() {}
}

#endif

// MARK: - Stubbing and Testing

#if canImport(SwiftUI)
public final class {ViewName}StubOps: {ViewName}ViewModelOperations, @unchecked Sendable {
    // Track which operations were called
    public private(set) var performActionCalled: Bool
    public private(set) var cancelCalled: Bool
    public private(set) var loadDataCalled: Bool

    public func performAction() async throws {
        performActionCalled = true
    }

    public func cancel() {
        cancelCalled = true
    }

    public func loadData() -> AsyncThrowingStream<ItemData, Error> {
        loadDataCalled = true
        return AsyncThrowingStream { continuation in
            // Return stub data for testing
            continuation.yield(.stub())
            continuation.finish()
        }
    }

    public init() {
        self.performActionCalled = false
        self.cancelCalled = false
        self.loadDataCalled = false
    }
}
#endif
```

---

# Template 11: Empty ViewModelOperations File (Display-Only)

**For display-only views** - Empty protocol and minimal stub.

**Location:** `Sources/{ViewModelsTarget}/{Feature}/{ViewName}ViewModelOperations.swift`

```swift
// {ViewName}ViewModelOperations.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import FOSMVVM
import Foundation

// MARK: - Operations Protocol

public protocol {ViewName}ViewModelOperations: ViewModelOperations {}

// MARK: - Stubbing and Testing

#if canImport(SwiftUI)
public final class {ViewName}StubOps: {ViewName}ViewModelOperations, @unchecked Sendable {
    public init() {}
}
#endif
```

---

# Quick Reference

## Test Infrastructure Checklist

**All Views:**
- [ ] `.uiTestingIdentifier()` on ALL elements you want to test

**Views WITH Operations (interactive views):**
- [ ] `#if DEBUG` block with `@State private var repaintToggle = false`
- [ ] `.testDataTransporter(viewModelOps:repaintToggle:)` modifier on body
- [ ] `operations` property stored from `viewModel.operations`
- [ ] `toggleRepaint()` helper function
- [ ] `toggleRepaint()` called after EVERY operation invocation

**Views WITHOUT Operations (display-only):**
- [ ] No `repaintToggle` needed
- [ ] No `.testDataTransporter()` needed
- [ ] No `operations` property needed
- [ ] No `toggleRepaint()` needed

## UI Testing Identifier Conventions

| Element Type | Accessor Pattern | Identifier Example |
|--------------|------------------|-------------------|
| Button | `buttons.element(matching: .button, identifier: "...")` | `"submitButton"` |
| Text Field | `textFields["..."]` | `"emailTextField"` |
| Static Text | `staticTexts["..."]` | `"errorMessage"` |
| Activity Indicator | `activityIndicators["..."]` | `"loadingIndicator"` |
| Table | `tables["..."]` | `"itemList"` |
| Alert | `alerts["..."]` | `"errorAlert"` |
| Other Elements | `otherElements["..."]` | `"mainContent"` |

## Common XCUIElement Patterns

```swift
// First match in a list
var firstItem: XCUIElement {
    buttons.element(matching: .button, identifier: "itemButton").firstMatch
}

// Wait for existence
XCTAssertTrue(app.someElement.waitForExistence(timeout: 3))

// Check enabled state
XCTAssertTrue(app.submitButton.isEnabled)
XCTAssertFalse(app.submitButton.isEnabled)

// Check existence
XCTAssertTrue(app.errorAlert.exists)
XCTAssertFalse(app.errorAlert.exists)

// Get text value
XCTAssertEqual(app.label.text, "Expected Text")

// Tap menu (for non-hittable SwiftUI menus)
app.menuButton.tapMenu()
```

## Operation Verification Pattern

```swift
func testSomeOperation() async throws {
    let app = try presentView(configuration: .default)

    // Perform UI interaction
    app.actionButton.tap()

    // Verify operation was called
    let stubOps = try viewModelOperations()
    XCTAssertTrue(stubOps.actionCalled)
    XCTAssertFalse(stubOps.otherActionCalled)
}
```

## Test Configuration Pattern

```swift
// Basic presentation
let app = try presentView()

// With custom ViewModel
let app = try presentView(
    viewModel: .stub(enabled: false, items: [])
)

// With test configuration
let app = try presentView(
    configuration: .requireAuth(userId: "123")
)

// Both ViewModel and configuration
let app = try presentView(
    configuration: .requireDevice(),
    viewModel: .stub(connected: true)
)
```

---

# Checklists

## Base Setup (Once Per Project):
- [ ] Base test case class created
- [ ] XCUIElement extensions created
- [ ] App bundle identifier configured
- [ ] Test target created in Xcode

## Per View Test:
- [ ] Test file created with correct generic parameters
- [ ] UI state tests added
- [ ] Operation tests added
- [ ] XCUIApplication extension with element accessors
- [ ] setUp() method configured if needed
- [ ] All interactive elements have corresponding accessors

## View Preparation:
- [ ] `@State private var repaintToggle` property
- [ ] `.testDataTransporter()` modifier
- [ ] `operations` stored from `viewModel.operations`
- [ ] `toggleRepaint()` helper function
- [ ] `toggleRepaint()` called after operations
- [ ] All interactive elements have `.uiTestingIdentifier()`

---

# Common Patterns

## Pattern 1: Testing Button States

```swift
func testButtonDisabledInitially() async throws {
    let app = try presentView()
    XCTAssertFalse(app.submitButton.isEnabled)
}

func testButtonEnabledAfterInput() async throws {
    let app = try presentView()

    app.nameField.typeTextAndWait("Test")

    XCTAssertTrue(app.submitButton.isEnabled)
}
```

## Pattern 2: Testing Async Operations

```swift
func testLoadData() async throws {
    let app = try presentView()

    // Wait for loading to complete
    XCTAssertTrue(app.waitForExistence(timeout: 3))

    let stubOps = try viewModelOperations()
    XCTAssertTrue(stubOps.loadDataCalled)
}
```

## Pattern 3: Testing Error States

```swift
func testErrorHandling() async throws {
    let app = try presentView(
        viewModel: .stub(hasError: true)
    )

    XCTAssertTrue(app.errorAlert.exists)
    app.dismissButton.tap()
    XCTAssertFalse(app.errorAlert.exists)
}
```

## Pattern 4: Testing Navigation

```swift
func testNavigation() async throws {
    let app = try presentView()

    app.itemRow.tap()
    XCTAssertTrue(app.detailView.waitForExistence(timeout: 2))

    app.backButton.tap()
    XCTAssertTrue(app.listView.waitForExistence(timeout: 2))
}
```
