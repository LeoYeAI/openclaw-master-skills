# MV Patterns Reference

Source provided by user: "SwiftUI in 2025: Forget MVVM" (Thomas Ricouard).

Use this as guidance when deciding whether to introduce a view model.

Key points:
- Default to MV: views are lightweight state expressions and orchestration points.
- Prefer `@State`, `@Environment`, `@Query`, `task`, and `onChange` over view models.
- Inject services and shared models via `@Environment`; keep logic in services/models.
- Split large views into smaller views instead of moving logic into a view model.
- Avoid manual data fetching that duplicates SwiftUI/SwiftData mechanisms.
- Test models/services and business logic; views should stay simple and declarative.

# SwiftUI in 2025: Forget MVVM

*Let me tell you why*

**Thomas Ricouard**
10 min read · Jun 2, 2025

---

It’s 2025, and I’m still getting asked the same question:

> “Where are your ViewModels?”

Every time I share this opinion or code from my open-source projects like my BlueSky client **IcySky**, or even the Medium iOS app, developers are surprised to see clean, simple views without a single ViewModel in sight.

Let me be clear:

You don’t need ViewModels in SwiftUI.
You never did.
You never will.

---

## The MVVM Trap

When SwiftUI launched in 2019, many developers brought their UIKit baggage with them. We were so used to the *Massive View Controller* problem that we immediately reached for MVVM as our savior.

But SwiftUI isn’t UIKit.

It was designed from the ground up with a different philosophy, highlighted in multiple WWDC sessions like:

- *Data Flow Through SwiftUI (WWDC19)*
- *Data Essentials in SwiftUI (WWDC20)*
- *Discover Observation in SwiftUI (WWDC23)*

Those sessions barely mention ViewModels.

Why? Because ViewModels are almost alien to SwiftUI’s data flow model.

SwiftUI views are **structs**, not classes. They are lightweight, disposable, and recreated frequently. Adding a ViewModel means fighting the framework’s core design.

---

## Views as Pure State Expressions

In my latest IcySky app, every view follows the same pattern I’ve advocated for years.

```swift
struct FeedView: View {

    @Environment(BlueSkyClient.self) private var client
    @Environment(AppTheme.self) private var theme

    enum ViewState {
        case loading
        case error(String)
        case loaded([Post])
    }

    @State private var viewState: ViewState = .loading
    @State private var isRefreshing = false

    var body: some View {
        NavigationStack {
            List {
                switch viewState {
                case .loading:
                    ProgressView("Loading feed...")
                        .frame(maxWidth: .infinity)
                        .listRowSeparator(.hidden)

                case .error(let message):
                    ErrorStateView(
                        message: message,
                        retryAction: { await loadFeed() }
                    )
                    .listRowSeparator(.hidden)

                case .loaded(let posts):
                    ForEach(posts) { post in
                        PostRowView(post: post)
                            .listRowInsets(.init())
                    }
                }
            }
            .listStyle(.plain)
            .refreshable { await refreshFeed() }
            .task { await loadFeed() }
        }
    }
}
The state is defined inside the view, using an enum.

No ViewModel.
No indirection.
The view is a direct expression of state.

The Magic of Environment
Instead of dependency injection through ViewModels, SwiftUI gives us @Environment.

swift
Copy code
@Environment(BlueSkyClient.self) private var client

private func loadFeed() async {
    do {
        let posts = try await client.getFeed()
        viewState = .loaded(posts)
    } catch {
        viewState = .error(error.localizedDescription)
    }
}
Your services live in the environment, are testable in isolation, and encapsulate complexity.

The view orchestrates UI flow — nothing else.

Real-World Complexity
“This only works for simple apps.”

No.

IcySky handles authentication, complex feeds, navigation, and user interaction — without ViewModels.

The Medium iOS app (millions of users) is now mostly SwiftUI and uses very few ViewModels, most of them legacy from 2019.

For new features, we inject services into the environment and build lightweight views with local state.

Using .task(id:) and .onChange()
SwiftUI’s modifiers act as small state reducers.

swift
Copy code
.task(id: searchText) {
    guard !searchText.isEmpty else { return }
    await searchFeed(query: searchText)
}
.onChange(of: isInSearch, initial: false) {
    guard !isInSearch else { return }
    Task { await fetchSuggestedFeed() }
}
Readable. Local. Explicit.

App-Level Environment Setup
swift
Copy code
@main
struct IcySkyApp: App {

    @Environment(\.scenePhase) var scenePhase

    @State var client: BSkyClient?
    @State var auth: Auth = .init()
    @State var currentUser: CurrentUser?
    @State var router: AppRouter = .init(initialTab: .feed)

    var body: some Scene {
        WindowGroup {
            TabView(selection: $router.selectedTab) {
                if client != nil && currentUser != nil {
                    ForEach(AppTab.allCases) { tab in
                        AppTabRootView(tab: tab)
                            .tag(tab)
                            .toolbarVisibility(.hidden, for: .tabBar)
                    }
                } else {
                    ProgressView()
                        .containerRelativeFrame([.horizontal, .vertical])
                }
            }
            .environment(client)
            .environment(currentUser)
            .environment(auth)
            .environment(router)
        }
    }
}
All dependencies are injected once and available everywhere.

SwiftData: The Perfect Example
SwiftData was built to work directly in views.

swift
Copy code
struct BookListView: View {

    @Query private var books: [Book]
    @Environment(\.modelContext) private var modelContext

    var body: some View {
        List {
            ForEach(books) { book in
                BookRowView(book: book)
                    .swipeActions {
                        Button("Delete", role: .destructive) {
                            modelContext.delete(book)
                        }
                    }
            }
        }
    }
}
Now compare that to forcing a ViewModel:

swift
Copy code
@Observable
class BookListViewModel {
    private var modelContext: ModelContext
    var books: [Book] = []

    init(modelContext: ModelContext) {
        self.modelContext = modelContext
        fetchBooks()
    }

    func fetchBooks() {
        let descriptor = FetchDescriptor<Book>()
        books = try! modelContext.fetch(descriptor)
    }
}
Manual fetching. Manual refresh. Boilerplate everywhere.

You’re fighting the framework.

Testing Reality
Testing SwiftUI views provides minimal value.

Instead:

Unit test services and business logic

Test models and transformations

Use SwiftUI previews for visual regression

Use UI automation for E2E tests

If needed, use ViewInspector for view introspection.

The 2025 Reality
SwiftUI is mature:

@Observable

Better Environment

Improved async & task lifecycle

Almost everything you need lives inside the view.

I’ll reconsider ViewModels when Apple lets us access Environment outside views.

Until then, vanilla SwiftUI is the canon.

Why This Matters
Every ViewModel adds:

More complexity

More objects to sync

More indirection

More cognitive overhead

SwiftUI gives you:

@State

@Environment

@Observable

Binding

Use them. Trust the framework.

The Bottom Line
In 2025, there’s no excuse for cluttering SwiftUI apps with unnecessary ViewModels.

Let views be pure expressions of state.

Focus complexity where it belongs: services and business logic.

Goodbye MVVM 🚮
Long live the View 👑

Happy coding 🚀
