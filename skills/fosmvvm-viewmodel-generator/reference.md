# FOSMVVM ViewModel Generator - Reference Templates

Complete file templates for generating ViewModels.

> **Conceptual context:** See [SKILL.md](SKILL.md) for when and why to use this skill.
> **Architecture context:** See [ViewModelArchitecture.md](../../docs/ViewModelArchitecture.md) for full FOSMVVM understanding.

## Placeholders

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `{Name}` | ViewModel name (PascalCase, without "ViewModel" suffix) | `Dashboard`, `Card` |
| `{ViewModelsTarget}` | Your ViewModels SPM target | `ViewModels` |
| `{ResourcesPath}` | Your localization resources path | `Sources/Resources` |
| `{WebServerTarget}` | Your server-side target (server-hosted only) | `WebServer` |

---

# Server-Hosted Templates

Use these templates for apps with a backend server.

---

## Template 1: Top-Level ViewModel (RequestableViewModel)

For pages or screens that are fetched directly via API.

**Location:** `Sources/{ViewModelsTarget}/{Feature}/{Name}ViewModel.swift`

```swift
import FOSFoundation
import FOSMVVM
import Foundation

/// ViewModel for the {Name} screen.
///
/// This is a top-level ViewModel - it has an associated Request type
/// and is built by a ViewModelFactory on the server.
@ViewModel
public struct {Name}ViewModel: RequestableViewModel {
    public typealias Request = {Name}Request

    // MARK: - Localized UI Text

    @LocalizedString public var pageTitle
    // Add more @LocalizedString properties for static UI text

    // MARK: - Data

    // Add data properties the View needs to display
    // public let items: [ItemViewModel]

    // MARK: - Child ViewModels

    // Add nested ViewModels for components
    // public let createModal: CreateModalViewModel

    // MARK: - Identity

    public var vmId: ViewModelId = .init()

    // MARK: - Initialization

    public init(/* parameters */) {
        // Initialize all properties
    }
}

// MARK: - Stubbable

public extension {Name}ViewModel {
    static func stub() -> Self {
        .init(/* default values for previews */)
    }
}
```

---

## Template 2: Child ViewModel (Instance)

For components that appear multiple times (cards, rows, list items).

**Location:** `Sources/{ViewModelsTarget}/{Feature}/{Name}ViewModel.swift`

```swift
import FOSFoundation
import FOSMVVM
import Foundation

/// ViewModel for a {Name} component.
///
/// This is a child ViewModel - built by its parent's Factory.
/// Each instance represents a different data entity.
@ViewModel
public struct {Name}ViewModel: Codable, Sendable {
    // MARK: - Data Identity

    /// The database entity ID - enables round-trip to server
    public let id: ModelIdType

    // MARK: - Content

    public let title: String
    // Add more content properties

    // MARK: - Formatted Values

    public let createdAt: LocalizableDate  // NOT String - formatted client-side

    // MARK: - Identity

    public var vmId: ViewModelId

    // MARK: - Initialization

    public init(
        id: ModelIdType,
        title: String,
        createdAt: Date
    ) {
        self.id = id
        self.title = title
        self.createdAt = LocalizableDate(value: createdAt)
        self.vmId = .init(id: id)  // Instance identity from data ID
    }
}

// MARK: - Stubbable

public extension {Name}ViewModel {
    static func stub() -> Self {
        .stub(id: .init())
    }

    static func stub(
        id: ModelIdType = .init(),
        title: String = "Sample Title",
        createdAt: Date = .now
    ) -> Self {
        .init(
            id: id,
            title: title,
            createdAt: createdAt
        )
    }
}
```

---

## Template 3: Child ViewModel (Singleton)

For components that appear once (modals, headers, toolbars).

**Location:** `Sources/{ViewModelsTarget}/{Feature}/{Name}ViewModel.swift`

```swift
import FOSFoundation
import FOSMVVM
import Foundation

/// ViewModel for the {Name} component.
///
/// This is a singleton child ViewModel - only one instance per parent.
@ViewModel
public struct {Name}ViewModel: Codable, Sendable {
    // MARK: - Localized UI Text

    @LocalizedString public var title
    @LocalizedString public var submitButtonLabel
    @LocalizedString public var cancelButtonLabel

    // MARK: - Identity

    public var vmId: ViewModelId = .init()

    // MARK: - Initialization

    public init() {}
}

// MARK: - Stubbable

public extension {Name}ViewModel {
    static func stub() -> Self {
        .init()
    }
}
```

---

## Template 4: ViewModel with Nested Child Types

For ViewModels that contain child types used only by this parent. Shows proper placement, conformances, and two-tier Stubbable pattern.

**Reference:** `Sources/KairosModels/Governance/GovernancePrincipleCardViewModel.swift`

**File:** `Sources/{Module}/{Feature}/{Name}ViewModel.swift`

```swift
// {Name}ViewModel.swift
//
// Copyright 2026 {YourOrganization}
// Licensed under the Apache License, Version 2.0

import FOSFoundation
import FOSMVVM
import Foundation

@ViewModel
public struct {Name}ViewModel: Codable, Sendable, Identifiable {
    // MARK: - Localized Strings

    @LocalizedString public var {field}Label

    // MARK: - Data Identity

    public let id: ModelIdType

    // MARK: - Content

    public let title: String
    public let description: String

    // MARK: - Collections (referencing nested types)

    /// Array of child summaries (only populated when expanded).
    public let childSummaries: [ChildSummary]?

    /// Related items that reference this entity.
    public let relatedItems: [RelatedItemReference]?

    // MARK: - Nested Types

    /// Summary of a child item for display in lists.
    public struct ChildSummary: Codable, Sendable, Identifiable, Stubbable {
        public let id: ModelIdType
        public let name: String
        public let createdAt: Date

        public init(id: ModelIdType, name: String, createdAt: Date) {
            self.id = id
            self.name = name
            self.createdAt = createdAt
        }
    }

    /// Reference to a related item.
    public struct RelatedItemReference: Codable, Sendable, Identifiable, Stubbable {
        public let id: ModelIdType
        public let title: String
        public let status: String

        public init(id: ModelIdType, title: String, status: String) {
            self.id = id
            self.title = title
            self.status = status
        }
    }

    // MARK: - View Identity

    public let vmId: ViewModelId

    public init(
        id: ModelIdType,
        title: String,
        description: String,
        childSummaries: [ChildSummary]? = nil,
        relatedItems: [RelatedItemReference]? = nil
    ) {
        self.vmId = .init(id: id)
        self.id = id
        self.title = title
        self.description = description
        self.childSummaries = childSummaries
        self.relatedItems = relatedItems
    }
}

// MARK: - Parent Stubbable

public extension {Name}ViewModel {
    // Tier 1: Zero-arg (delegates to tier 2)
    static func stub() -> Self {
        .stub(id: .init())
    }

    // Tier 2: Parameterized with defaults
    static func stub(
        id: ModelIdType = .init(),
        title: String = "A Title",
        description: String = "A Description",
        childSummaries: [ChildSummary]? = [.stub()],
        relatedItems: [RelatedItemReference]? = [.stub()]
    ) -> Self {
        .init(
            id: id,
            title: title,
            description: description,
            childSummaries: childSummaries,
            relatedItems: relatedItems
        )
    }
}

// MARK: - Nested Type Stubbable Extensions (fully qualified names)

public extension {Name}ViewModel.ChildSummary {
    // Tier 1: Zero-arg (delegates to tier 2)
    static func stub() -> Self {
        .stub(id: .init())
    }

    // Tier 2: Parameterized with defaults
    static func stub(
        id: ModelIdType = .init(),
        name: String = "A Name",
        createdAt: Date = .now
    ) -> Self {
        .init(id: id, name: name, createdAt: createdAt)
    }
}

public extension {Name}ViewModel.RelatedItemReference {
    // Tier 1: Zero-arg (delegates to tier 2)
    static func stub() -> Self {
        .stub(id: .init())
    }

    // Tier 2: Parameterized with defaults
    static func stub(
        id: ModelIdType = .init(),
        title: String = "A Title",
        status: String = "Active"
    ) -> Self {
        .init(id: id, title: title, status: status)
    }
}
```

**Key Points:**
- Nested types placed AFTER properties that reference them
- Nested types placed BEFORE `vmId` and parent init
- Each nested type conforms to: `Codable, Sendable, Identifiable, Stubbable`
- Extensions use fully qualified names: `{Parent}.{NestedType}`
- Two-tier Stubbable: zero-arg always delegates to parameterized
- Section markers: `// MARK: - Nested Types`

---

## Template 5: ViewModelRequest

For top-level ViewModels - the Request type for fetching from server.

**Location:** `Sources/{ViewModelsTarget}/{Feature}/{Name}Request.swift`

```swift
import FOSFoundation
import FOSMVVM
import Foundation

/// Request to fetch the {Name}ViewModel from the server.
public final class {Name}Request: ViewModelRequest, @unchecked Sendable {
    public typealias Query = EmptyQuery
    public typealias ResponseError = EmptyError

    public var responseBody: {Name}ViewModel?

    public init(
        query: EmptyQuery? = nil,
        fragment: EmptyFragment? = nil,
        requestBody: EmptyBody? = nil,
        responseBody: {Name}ViewModel? = nil
    ) {
        self.responseBody = responseBody
    }
}
```

---

## Template 6: ViewModelFactory

For top-level ViewModels - builds the ViewModel from database.

**Location:** `Sources/{WebServerTarget}/ViewModelFactories/{Name}ViewModel+Factory.swift`

```swift
import Fluent
import FOSFoundation
import FOSMVVM
import FOSMVVMVapor
import Foundation
import Vapor
import ViewModels

/// Factory that builds {Name}ViewModel from database.
extension {Name}ViewModel: VaporViewModelFactory {
    public typealias VMRequest = {Name}Request

    public static func model(context: VaporModelFactoryContext<VMRequest>) async throws -> Self {
        let db = context.req.db

        // Query database for required data
        // let items = try await Item.query(on: db).all()

        // Build child ViewModels
        // let itemViewModels = items.map { item in
        //     ItemViewModel(
        //         id: item.id!,
        //         title: item.title,
        //         createdAt: item.createdAt ?? .now
        //     )
        // }

        return .init(
            // Pass built children
        )
    }
}
```

---

## Template 7: Localization YAML

**Location:** `{ResourcesPath}/ViewModels/{Feature}/{Name}ViewModel.yml`

```yaml
en:
  {Name}ViewModel:
    pageTitle: "Page Title"
    headerText: "Welcome"
    submitButtonLabel: "Submit"
    cancelButtonLabel: "Cancel"
```

---

# Client-Hosted Templates

Use these templates for standalone apps without a backend server.

---

## Template 8: Client-Hosted Top-Level ViewModel

For standalone apps - the macro generates the factory automatically.

**Location:** `Sources/{ViewModelsTarget}/{Feature}/{Name}ViewModel.swift`

```swift
import FOSFoundation
import FOSMVVM
import Foundation

/// ViewModel for the {Name} screen.
///
/// Client-hosted: Factory is auto-generated from init parameters.
/// The AppState struct is derived from the init signature.
@ViewModel(options: [.clientHostedFactory])
public struct {Name}ViewModel {
    // MARK: - Localized UI Text

    @LocalizedString public var pageTitle
    // Add more @LocalizedString properties for static UI text

    // MARK: - Data (from AppState)

    // Properties populated from init parameters
    // public let settings: UserSettings
    // public let items: [ItemViewModel]

    // MARK: - Identity

    public var vmId: ViewModelId = .init()

    // MARK: - Initialization

    /// Parameters here become AppState properties.
    /// The macro generates:
    /// - struct AppState { let settings: UserSettings; let items: [ItemViewModel] }
    /// - static func model(context:) that builds Self from context.appState
    public init(settings: UserSettings, items: [ItemViewModel]) {
        self.settings = settings
        self.items = items
    }
}

// MARK: - Stubbable

public extension {Name}ViewModel {
    static func stub() -> Self {
        .init(
            settings: .stub(),
            items: [.stub()]
        )
    }
}
```

**What the macro generates:**

```swift
// Auto-generated by @ViewModel(options: [.clientHostedFactory])
extension {Name}ViewModel {
    public typealias Request = ClientHostedRequest

    public struct AppState: Hashable, Sendable {
        public let settings: UserSettings
        public let items: [ItemViewModel]

        public init(settings: UserSettings, items: [ItemViewModel]) {
            self.settings = settings
            self.items = items
        }
    }

    public final class ClientHostedRequest: ViewModelRequest, @unchecked Sendable {
        public var responseBody: {Name}ViewModel?
        public typealias ResponseError = EmptyError
        public init(...) { ... }
    }

    public static func model(
        context: ClientHostedModelFactoryContext<Request, AppState>
    ) async throws -> Self {
        .init(
            settings: context.appState.settings,
            items: context.appState.items
        )
    }
}
```

---

## Template 9: Client-Hosted Complete Example

A settings screen for a standalone iPhone app.

### SettingsViewModel.swift

```swift
import FOSFoundation
import FOSMVVM
import Foundation

@ViewModel(options: [.clientHostedFactory])
public struct SettingsViewModel {
    // MARK: - Localized UI Text

    @LocalizedString public var pageTitle
    @LocalizedString public var themeLabel
    @LocalizedString public var notificationsLabel
    @LocalizedString public var saveButtonLabel

    // MARK: - Data

    public let currentTheme: Theme
    public let notificationsEnabled: Bool

    // MARK: - Identity

    public var vmId: ViewModelId = .init()

    // MARK: - Initialization

    public init(currentTheme: Theme, notificationsEnabled: Bool) {
        self.currentTheme = currentTheme
        self.notificationsEnabled = notificationsEnabled
    }
}

public extension SettingsViewModel {
    static func stub() -> Self {
        .init(currentTheme: .light, notificationsEnabled: true)
    }
}

public enum Theme: String, Codable, Sendable {
    case light, dark, system
}
```

### SettingsViewModel.yml

```yaml
en:
  SettingsViewModel:
    pageTitle: "Settings"
    themeLabel: "Theme"
    notificationsLabel: "Notifications"
    saveButtonLabel: "Save Changes"
```

### Usage in SwiftUI View

```swift
struct SettingsView: View {
    @State private var viewModel: SettingsViewModel?

    var body: some View {
        // Render viewModel
    }

    func loadViewModel() async {
        // Create AppState from local storage/preferences
        let appState = SettingsViewModel.AppState(
            currentTheme: UserDefaults.standard.theme,
            notificationsEnabled: UserDefaults.standard.notificationsEnabled
        )

        // Build context with localization
        let context = ClientHostedModelFactoryContext<
            SettingsViewModel.Request,
            SettingsViewModel.AppState
        >(appState: appState, localizationStore: myYamlStore)

        // Get localized ViewModel
        viewModel = try await SettingsViewModel.model(context: context)
    }
}
```

---

# Server-Hosted Complete Example

## Complete Example: Dashboard with Cards

### DashboardViewModel.swift

```swift
import FOSFoundation
import FOSMVVM
import Foundation

@ViewModel
public struct DashboardViewModel: RequestableViewModel {
    public typealias Request = DashboardRequest

    @LocalizedString public var pageTitle
    @LocalizedString public var emptyStateMessage

    public let cards: [CardViewModel]
    public let totalCount: LocalizableInt

    public var vmId: ViewModelId = .init()

    public init(cards: [CardViewModel], totalCount: Int) {
        self.cards = cards
        self.totalCount = LocalizableInt(value: totalCount)
    }
}

public extension DashboardViewModel {
    static func stub() -> Self {
        .init(
            cards: [.stub(), .stub()],
            totalCount: 2
        )
    }
}
```

### CardViewModel.swift

```swift
import FOSFoundation
import FOSMVVM
import Foundation

@ViewModel
public struct CardViewModel: Codable, Sendable {
    public let id: ModelIdType
    public let title: String
    public let description: String
    public let createdAt: LocalizableDate

    public var vmId: ViewModelId

    public init(
        id: ModelIdType,
        title: String,
        description: String,
        createdAt: Date
    ) {
        self.id = id
        self.title = title
        self.description = description
        self.createdAt = LocalizableDate(value: createdAt)
        self.vmId = .init(id: id)
    }
}

public extension CardViewModel {
    static func stub() -> Self {
        .stub(id: .init())
    }

    static func stub(
        id: ModelIdType = .init(),
        title: String = "Sample Card",
        description: String = "This is a sample card for previews.",
        createdAt: Date = .now
    ) -> Self {
        .init(
            id: id,
            title: title,
            description: description,
            createdAt: createdAt
        )
    }
}
```

### DashboardRequest.swift

```swift
import FOSFoundation
import FOSMVVM
import Foundation

public final class DashboardRequest: ViewModelRequest, @unchecked Sendable {
    public typealias Query = EmptyQuery
    public typealias ResponseError = EmptyError

    public var responseBody: DashboardViewModel?

    public init(
        query: EmptyQuery? = nil,
        fragment: EmptyFragment? = nil,
        requestBody: EmptyBody? = nil,
        responseBody: DashboardViewModel? = nil
    ) {
        self.responseBody = responseBody
    }
}
```

### DashboardViewModel+Factory.swift

```swift
import Fluent
import FOSFoundation
import FOSMVVM
import FOSMVVMVapor
import Foundation
import Vapor
import ViewModels

extension DashboardViewModel: VaporViewModelFactory {
    public typealias VMRequest = DashboardRequest

    public static func model(context: VaporModelFactoryContext<VMRequest>) async throws -> Self {
        let db = context.req.db

        let items = try await Item.query(on: db)
            .sort(\.$createdAt, .descending)
            .all()

        let cardViewModels = items.map { item in
            CardViewModel(
                id: item.id!,
                title: item.title,
                description: item.description,
                createdAt: item.createdAt ?? .now
            )
        }

        return .init(
            cards: cardViewModels,
            totalCount: items.count
        )
    }
}
```

### DashboardViewModel.yml

```yaml
en:
  DashboardViewModel:
    pageTitle: "Dashboard"
    emptyStateMessage: "No items yet. Create your first one!"
```

---

## Quick Reference: Property Types

| Data Type | ViewModel Property Type | Why |
|-----------|------------------------|-----|
| Static UI text | `@LocalizedString` | Resolved from YAML |
| Dynamic data in text | `@LocalizedSubs` | Substitutions like "Hello, %{name}!" |
| Composed text | `@LocalizedCompoundString` | Joins pieces with locale-aware ordering |
| User content | `String` | Already localized or raw data |
| Database ID | `ModelIdType` | Type-safe round trips |
| Date/time | `LocalizableDate` | Client formats for locale/timezone |
| Count/number | `LocalizableInt` | Client formats with grouping |
| Child component | `ChildViewModel` | Nested ViewModel |
| List of children | `[ChildViewModel]` | Array of nested ViewModels |

---

## Contextual Localization Examples

### @LocalizedSubs - Dynamic Data in Text

When you need to embed dynamic values in localized text:

```swift
@ViewModel
public struct WelcomeViewModel {
    @LocalizedSubs(substitutions: \.subs) var welcomeMessage

    private let userName: String
    private let userIndex: LocalizableInt

    private var subs: [String: any Localizable] {
        [
            "userName": LocalizableString.constant(userName),
            "userIndex: userIndex
        ],
    }
}
```

```yaml
en:
  WelcomeViewModel:
    welcomeMessage: "Welcome back, %{userName}:%{userIndex}!"

ja:
  WelcomeViewModel:
    welcomeMessage: "お帰りなさい、%{userName}:%{userIndex}さん！"
```

The `%{userName}` and `%{userIndex}` substitution points are placed correctly per locale.
Use LocalizableInt and not Int to ensure proper localization of numbers in all locales.

### @LocalizedCompoundString - Composed Text

When you need to join multiple pieces with locale-aware ordering:

```swift
@ViewModel
public struct UserNameViewModel {
    @LocalizedStrings var namePieces  // Array of strings from YAML
    @LocalizedString var separator
    @LocalizedCompoundString(pieces: \._namePieces, separator: \._separator) var fullName
}
```

This handles RTL languages and locales where name order differs (e.g., family name first).

---

## Checklists

### All ViewModels:
- [ ] `@ViewModel` macro applied
- [ ] `vmId: ViewModelId` property
- [ ] `stub()` method for testing/previews
- [ ] `Codable, Sendable` conformance

### Server-Hosted Top-Level:
- [ ] `: RequestableViewModel` conformance
- [ ] `typealias Request = {Name}Request`
- [ ] Request file created
- [ ] Factory file created
- [ ] YAML file created

### Client-Hosted Top-Level:
- [ ] `@ViewModel(options: [.clientHostedFactory])` macro
- [ ] Init parameters define the AppState
- [ ] YAML file created (bundled in app)
- [ ] No Request or Factory files needed

### Instance ViewModels (either mode):
- [ ] `id: ModelIdType` property
- [ ] `vmId = .init(id: id)` in init

### ViewModels with Localization (either mode):
- [ ] `@LocalizedString` for static text
- [ ] YAML file with matching keys
