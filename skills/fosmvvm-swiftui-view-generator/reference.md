# FOSMVVM SwiftUI View Generator - Reference Templates

Complete file templates for generating SwiftUI ViewModelViews.

> **Conceptual context:** See [SKILL.md](SKILL.md) for when and why to use this skill.
> **Architecture context:** See [FOSMVVMArchitecture.md](../../docs/FOSMVVMArchitecture.md) for full FOSMVVM understanding.

## Placeholders

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `{ViewName}` | View name (without "View" suffix) | `TaskList`, `SignIn` |
| `{ViewModel}` | Full ViewModel type name | `TaskListViewModel` |
| `{Operations}` | Full ViewModelOperations type name | `TaskListViewModelOperations` |
| `{ViewsTarget}` | SwiftUI views SPM target | `MyAppViews` |
| `{ViewModelsTarget}` | ViewModels SPM target | `MyAppViewModels` |
| `{Feature}` | Feature/module grouping | `Tasks`, `Auth` |

---

# Template 1: Display-Only View (No Operations)

**For views that just render data** - No user interactions, no business logic.

**Location:** `Sources/{ViewsTarget}/{Feature}/{ViewName}View.swift`

```swift
// {ViewName}View.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import FOSMVVM
import Foundation
import SwiftUI
import {ViewModelsTarget}

/// Displays {description}
public struct {ViewName}View: ViewModelView {
    private let viewModel: {ViewModel}

    public var body: some View {
        HStack(alignment: .top) {
            Image(systemName: viewModel.iconName)
                .resizable()
                .frame(width: 50, height: 50)

            Spacer()

            VStack(alignment: .leading) {
                Text(viewModel.title)
                    .font(.headline)

                LabeledContent {
                    Text(viewModel.statusText)
                        .bold()
                } label: {
                    Text(viewModel.statusLabel)
                }

                if let subtitle = viewModel.subtitle {
                    Text(subtitle)
                        .font(.caption)
                }
            }
        }
        .padding()
        .background(Color.secondary.opacity(0.1))
        .cornerRadius(8)
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

#Preview("With Data") {
    {ViewName}View.previewHost(
        bundle: MyAppResourceAccess.localizationBundle,
        viewModel: .stub(
            title: "Sample Title",
            statusText: "Active"
        )
    )
}
#endif
```

---

# Template 2: Simple Interactive View

**For views with basic user interactions** - Buttons that trigger operations.

**Location:** `Sources/{ViewsTarget}/{Feature}/{ViewName}View.swift`

```swift
// {ViewName}View.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import FOSMVVM
import Foundation
import SwiftUI
import {ViewModelsTarget}

/// Interactive view for {description}
public struct {ViewName}View: ViewModelView {
    @State private var error: Error?

    #if DEBUG
    @State private var repaintToggle = false
    #endif

    private let viewModel: {ViewModel}
    private let operations: {Operations}

    public var body: some View {
        VStack {
            Text(viewModel.title)
                .font(.title)

            Text(viewModel.description)
                .font(.body)

            Spacer()

            HStack {
                Button(role: .cancel, action: cancel) {
                    Text(viewModel.cancelButtonLabel)
                        .foregroundStyle(.red)
                }

                Spacer()

                Button(action: performAction) {
                    Text(viewModel.actionButtonLabel)
                        .fontWeight(.semibold)
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding()
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

# Template 3: Form View with Validation

**For views with validated form inputs** - Uses FormFieldView and Validations.

**Location:** `Sources/{ViewsTarget}/{Feature}/{ViewName}View.swift`

```swift
// {ViewName}View.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import FOSMVVM
import Foundation
import SwiftUI
import {ViewModelsTarget}

/// Form for {description}
public struct {ViewName}View: ViewModelView {
    @Environment(Validations.self) private var validations
    @Environment(MVVMEnvironment.self) private var mvvmEnv
    @Environment(\.focusState) private var focusField

    @State private var error: Error?
    @State private var submitSuccess: Bool = false

    #if DEBUG
    @State private var repaintToggle = false
    #endif

    private let viewModel: {ViewModel}
    private let operations: {Operations}

    public var body: some View {
        Form {
            FormFieldView(
                fieldModel: viewModel.$email,
                focusField: focusField,
                fieldValidator: viewModel.validateEmail,
                validations: validations
            )

            FormFieldView(
                fieldModel: viewModel.$password,
                focusField: focusField,
                fieldValidator: viewModel.validatePassword,
                validations: validations
            )

            FormFieldView(
                fieldModel: viewModel.$name,
                focusField: focusField,
                fieldValidator: viewModel.validateName,
                validations: validations
            )

            Button(errorBinding: $error, asyncAction: submit) {
                Text(viewModel.submitButtonLabel)
            }
            .disabled(validations.hasError)
        }
        .onAsyncSubmit {
            await submit()
        }
        .alert(
            errorBinding: $error,
            title: viewModel.errorTitle,
            message: viewModel.errorMessage,
            dismissButtonLabel: viewModel.dismissButtonLabel
        )
        .sheet(isPresented: $submitSuccess) {
            VStack {
                Text(viewModel.successMessage)
                Button(viewModel.closeButtonLabel) {
                    submitSuccess = false
                }
            }
            .padding()
        }
        #if os(macOS)
        .padding([.leading, .trailing])
        #endif
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
    func submit() async {
        guard validations.status?.hasError != true else {
            return
        }

        let validations = validations
        do {
            let response = try await operations.submit(
                email: viewModel.email,
                password: viewModel.password,
                name: viewModel.name,
                mvvmEnv: mvvmEnv
            )

            submitSuccess = response?.success == true
        } catch let error as SubmitRequest.ResponseError {
            if !error.validationResults.isEmpty {
                validations.replace(with: error.validationResults)
            } else {
                self.error = error
            }
        } catch {
            self.error = error
        }

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
    .environment(Validations())
    .frame(minWidth: 300, minHeight: 200)
}
#endif
```

---

# Template 4: View with Async Loading

**For views that load data asynchronously** - With loading states and error handling.

**Location:** `Sources/{ViewsTarget}/{Feature}/{ViewName}View.swift`

```swift
// {ViewName}View.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import FOSMVVM
import Foundation
import SwiftUI
import {ViewModelsTarget}

/// View that loads and displays {description}
public struct {ViewName}View: ViewModelView {
    @Environment(AppState.self) private var appState
    @State private var items: [ItemViewModel] = []
    @State private var error: Error?
    @State private var isLoading = false

    #if DEBUG
    @State private var repaintToggle = false
    #endif

    private let viewModel: {ViewModel}
    private let operations: {Operations}

    public var body: some View {
        VStack {
            Text(viewModel.title)
                .font(.headline)
                .padding()

            if isLoading {
                ProgressView()
            } else if items.isEmpty {
                Text(viewModel.emptyStateMessage)
                    .foregroundStyle(.secondary)
            } else {
                contentView
            }

            Spacer()

            Button(errorBinding: $error, asyncAction: refresh) {
                HStack {
                    Image(systemName: "arrow.clockwise")
                    Text(viewModel.refreshButtonLabel)
                }
            }
            .padding()
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

    private var contentView: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 8) {
                ForEach(items) { item in
                    ItemRowView(item: item)
                }
            }
        }
    }

    public init(viewModel: {ViewModel}) {
        self.viewModel = viewModel
        self.operations = viewModel.operations
    }
}

private extension {ViewName}View {
    func loadItems() async throws {
        isLoading = true
        let stream = operations.loadItems()
        toggleRepaint()

        for try await item in stream {
            items.append(item)
        }

        isLoading = false
        toggleRepaint()
    }

    @Sendable func refresh() async throws {
        items.removeAll()
        try await loadItems()
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
    .environment(AppState())
}
#endif
```

---

# Template 5: Container View with Child Bindings

**For views that compose child views** - Uses .bind() to pass data to children.

**Location:** `Sources/{ViewsTarget}/{Feature}/{ViewName}View.swift`

```swift
// {ViewName}View.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import FOSMVVM
import Foundation
import SwiftUI
import {ViewModelsTarget}

/// Container view that manages {description}
public struct {ViewName}View: ViewModelView {
    @Environment(AppState.self) private var appState

    #if DEBUG
    @State private var repaintToggle = false
    #endif

    private let viewModel: {ViewModel}
    private let operations: {Operations}

    public var body: some View {
        VStack {
            Text(viewModel.pageTitle)
                .font(.title)
                .padding()

            switch viewModel.state {
            case .idle:
                Button(action: startFlow) {
                    HStack {
                        Spacer()
                        Text(viewModel.startButtonLabel)
                        Spacer()
                    }
                }
                .buttonStyle(.borderedProminent)

            case .selectingItem:
                ItemSelectorView.bind(appState: .init())

            case .itemSelected(let itemId):
                statusView

                ItemDetailView.bind(
                    appState: .init(
                        itemId: itemId,
                        isActive: viewModel.isActive,
                        level: viewModel.level
                    )
                )

                if appState.item != nil, viewModel.isActive {
                    Button(action: proceedToNext) {
                        HStack {
                            Spacer()
                            Text(viewModel.nextButtonLabel)
                            Spacer()
                        }
                    }
                    .buttonStyle(.borderedProminent)
                }

            case .selectingDetails:
                DetailSelectorView.bind(appState: .init())

            case .completed(let itemId, let detailId):
                statusView

                ItemDetailView.bind(
                    appState: .init(
                        itemId: itemId,
                        isActive: viewModel.isActive,
                        level: viewModel.level
                    )
                )

                DetailInfoView.bind(
                    appState: .init(
                        detailId: detailId,
                        isEnabled: viewModel.isEnabled,
                        status: viewModel.status
                    )
                )
            }

            Spacer()
        }
        .padding([.leading, .trailing])
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
    func startFlow() {
        appState.state = .selectingItem
        operations.startFlow()
        toggleRepaint()
    }

    func proceedToNext() {
        guard case .itemSelected(let itemId) = viewModel.state else {
            return
        }
        appState.state = .selectingDetails(itemId: itemId)
        operations.proceedToDetails()
        toggleRepaint()
    }

    var statusView: some View {
        HStack {
            Text(viewModel.statusLabel)
            Image(systemName: viewModel.isActive ? "checkmark.circle.fill" : "circle")
            Text(viewModel.isActive ? viewModel.activeText : viewModel.inactiveText)
        }
        .padding(.bottom)
    }

    func toggleRepaint() {
        #if DEBUG
        repaintToggle.toggle()
        #endif
    }
}

#if DEBUG
#Preview("Idle") {
    {ViewName}View.previewHost(
        bundle: MyAppResourceAccess.localizationBundle,
        viewModel: .stub(state: .idle)
    )
    .environment(AppState.stub())
}

#Preview("Item Selected") {
    {ViewName}View.previewHost(
        bundle: MyAppResourceAccess.localizationBundle,
        viewModel: .stub(
            state: .itemSelected(itemId: .init()),
            isActive: true,
            level: .high
        )
    )
    .environment(AppState.stub())
}

#Preview("Completed") {
    {ViewName}View.previewHost(
        bundle: MyAppResourceAccess.localizationBundle,
        viewModel: .stub(
            state: .completed(itemId: .init(), detailId: .init()),
            isActive: true,
            isEnabled: true
        )
    )
    .environment(AppState.stub())
}
#endif
```

---

# Template 6: List View with Selection

**For views with selectable lists** - Manages selection state and item interaction.

**Location:** `Sources/{ViewsTarget}/{Feature}/{ViewName}View.swift`

```swift
// {ViewName}View.swift
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import FOSMVVM
import Foundation
import SwiftUI
import {ViewModelsTarget}

/// List view for selecting {description}
public struct {ViewName}View: ViewModelView {
    @State private var items: [ItemData] = []
    @State private var selectedId: ModelIdType?
    @State private var isProcessing: Bool = false
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
                .padding(.top)

            HStack {
                Text(viewModel.listHeaderLabel)
                Spacer()
                Text(isProcessing ? viewModel.processingLabel : viewModel.scanningLabel)
            }
            .padding(.horizontal)

            Divider()

            ScrollView {
                VStack(alignment: .leading) {
                    if orderedItems.isEmpty {
                        Text(viewModel.emptyStateMessage)
                            .foregroundStyle(.secondary)
                    }

                    ForEach(orderedItems) { item in
                        Button { selectItem(id: item.id) } label: {
                            HStack {
                                Text(item.displayName)

                                if item.id == selectedId {
                                    Spacer()
                                    if isProcessing {
                                        ProgressView()
                                    } else {
                                        Image(systemName: "checkmark.circle.fill")
                                    }
                                }
                            }
                        }
                        .padding(.vertical, 8)
                        .padding(.horizontal)
                        .background(
                            item.id == selectedId
                                ? Color.accentColor.opacity(0.2)
                                : Color.clear
                        )

                        Divider()
                    }
                }
            }

            Spacer()

            HStack {
                Button(role: .cancel, action: cancel) {
                    Text(viewModel.cancelButtonLabel)
                        .foregroundStyle(.red)
                }

                Spacer()

                Button(errorBinding: $error, asyncAction: submit) {
                    Text(viewModel.submitButtonLabel)
                        .fontWeight(.semibold)
                        .frame(minWidth: 120)
                }
                .buttonStyle(.borderedProminent)
                .disabled(selectedId == nil || isProcessing)
            }
            .padding()
        }
        .task(errorBinding: $error) { try await loadItems() }
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

        for try await nextItem in stream {
            items.append(nextItem)
        }
    }

    func cancel() {
        operations.cancel()
        toggleRepaint()
    }

    func selectItem(id: ModelIdType) {
        if selectedId == id {
            selectedId = nil
        } else {
            selectedId = id
        }
        toggleRepaint()
    }

    @Sendable func submit() async throws {
        guard
            let selectedId,
            let item = items.first(where: { $0.id == selectedId })
        else {
            return
        }

        operations.cancel()
        isProcessing = true

        try await operations.submit(item: item)

        isProcessing = false
        toggleRepaint()
    }

    var orderedItems: [ItemData] {
        items.sorted(by: { $0.displayName < $1.displayName })
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

# Quick Reference

## View Component Checklist

**All Views:**
- [ ] Conforms to `ViewModelView`
- [ ] `private let viewModel: {ViewModel}`
- [ ] `public init(viewModel:)`
- [ ] Previews with `.previewHost()`

**Interactive Views (with operations):**
- [ ] `private let operations: {Operations}`
- [ ] `@State private var repaintToggle = false` (DEBUG)
- [ ] `.testDataTransporter(viewModelOps:repaintToggle:)` (DEBUG)
- [ ] `toggleRepaint()` called after all operations
- [ ] Operations stored from `viewModel.operations` in init

**Form Views:**
- [ ] `@Environment(Validations.self) private var validations`
- [ ] `@Environment(\.focusState) private var focusField`
- [ ] `FormFieldView` for each input field
- [ ] `.disabled(validations.hasError)` on submit button
- [ ] Separate handling for validation errors vs general errors

**Container Views:**
- [ ] `@Environment(AppState.self) private var appState`
- [ ] Child views use `.bind(appState:)`
- [ ] AppState created from ViewModel data

## Common Patterns

### Error Handling

```swift
@State private var error: Error?

.alert(
    errorBinding: $error,
    title: viewModel.errorTitle,
    message: viewModel.errorMessage,
    dismissButtonLabel: viewModel.dismissButtonLabel
)
```

### Async Actions

```swift
Button(errorBinding: $error, asyncAction: submit) {
    Text(viewModel.submitLabel)
}

private func submit() async {
    do {
        try await operations.submit()
    } catch {
        self.error = error
    }
    toggleRepaint()
}
```

### Task on Appear

```swift
.task(errorBinding: $error) {
    try await loadData()
}

private func loadData() async throws {
    try await operations.loadData()
    toggleRepaint()
}
```

### Conditional Rendering

```swift
if viewModel.isEmpty {
    Text(viewModel.emptyStateMessage)
} else {
    ForEach(viewModel.items) { item in
        ItemRow(item: item)
    }
}
```

### Child View Binding

```swift
ChildView.bind(
    appState: .init(
        id: viewModel.selectedId,
        isActive: viewModel.isActive
    )
)
```

## Preview Patterns

```swift
#if DEBUG
// Basic preview
#Preview {
    MyView.previewHost(
        bundle: MyAppResourceAccess.localizationBundle
    )
    .environment(AppState())
}

// Named preview with data
#Preview("With Items") {
    MyView.previewHost(
        bundle: MyAppResourceAccess.localizationBundle,
        viewModel: .stub(
            items: [.stub(), .stub()],
            isEmpty: false
        )
    )
    .environment(AppState())
}

// Multiple states
#Preview("Loading") {
    MyView.previewHost(
        bundle: MyAppResourceAccess.localizationBundle,
        viewModel: .stub(isLoading: true)
    )
}

#Preview("Empty") {
    MyView.previewHost(
        bundle: MyAppResourceAccess.localizationBundle,
        viewModel: .stub(isEmpty: true)
    )
}
#endif
```

---

# Checklists

## Before Creating a View:
- [ ] ViewModel exists and is understood
- [ ] Determined if operations are needed
- [ ] Identified if form with validation
- [ ] Identified if container with child views
- [ ] Reviewed ViewModel properties to understand data

## After Creating a View:
- [ ] View conforms to ViewModelView
- [ ] Init stores viewModel (and operations if needed)
- [ ] Test infrastructure added if operations present
- [ ] Previews added for different states
- [ ] Error handling in place if async operations
- [ ] Validation handling in place if form
- [ ] Child view bindings correct if container
