---
name: fosmvvm-react-view-generator
description: Generate React components that render FOSMVVM ViewModels. Scaffolds ViewModelView pattern with hooks, loading states, and TypeScript types.
homepage: https://github.com/foscomputerservices/FOSUtilities
metadata: {"clawdbot": {"emoji": "⚛️", "os": ["darwin", "linux"]}}
---

# FOSMVVM React View Generator

Generate React components that render FOSMVVM ViewModels.

## Conceptual Foundation

> For full architecture context, see [FOSMVVMArchitecture.md](../../docs/FOSMVVMArchitecture.md) | [OpenClaw reference]({baseDir}/references/FOSMVVMArchitecture.md)

In FOSMVVM, **React components are thin rendering layers** that display ViewModels:

```
┌─────────────────────────────────────────────────────────────┐
│                    ViewModelView Pattern                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ViewModel (Data)          React Component                  │
│  ┌──────────────────┐     ┌──────────────────┐             │
│  │ title: String    │────►│ <h1>{vm.title}   │             │
│  │ items: [Item]    │────►│ {vm.items.map()} │             │
│  │ isEnabled: Bool  │────►│ disabled={!...}  │             │
│  └──────────────────┘     └──────────────────┘             │
│                                                              │
│  ServerRequest (Actions)                                     │
│  ┌──────────────────┐     ┌──────────────────┐             │
│  │ processRequest() │◄────│ <Component.bind  │             │
│  │                  │     │   requestType={} │             │
│  └──────────────────┘     └──────────────────┘             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key principle:** Components don't transform or compute data. They render what the ViewModel provides.

---

## View-ViewModel Alignment

**The component filename should match the ViewModel it renders.**

```
src/
  viewmodels/
    {Feature}ViewModel.js           ←──┐
    {Entity}CardViewModel.js        ←──┼── Same names
                                        │
  components/                           │
    {Feature}/                          │
      {Feature}View.jsx             ────┤  (renders {Feature}ViewModel)
      {Entity}CardView.jsx          ────┘  (renders {Entity}CardViewModel)
```

This alignment provides:
- **Discoverability** - Find the component for any ViewModel instantly
- **Consistency** - Same naming discipline as SwiftUI and Leaf
- **Maintainability** - Changes to ViewModel are reflected in component location

---

## TDD Workflow

This skill generates **tests FIRST, implementation SECOND** in a single invocation:

```
1. Reference ViewModel and ServerRequest details from conversation context
2. Generate .test.js file → Tests FAIL (no implementation yet)
3. Generate .jsx file → Tests PASS
4. Verify completeness (both files exist)
5. User runs `npm test` → All tests pass ✓
```

**Context-aware:** Skill references conversation understanding of requirements. No file parsing or Q&A needed.

---

## Core Components

### 1. viewModelComponent() Wrapper

Every component is wrapped with `viewModelComponent()`:

```jsx
const MyView = FOSMVVM.viewModelComponent(({ viewModel }) => {
  return <div>{viewModel.title}</div>;
});

export default MyView;
```

**Required:**
- Use `FOSMVVM.viewModelComponent()` from global namespace (loaded via script tag)
- Component function receives `{ viewModel }` prop
- No imports needed - FOSMVVM utilities loaded via `<script>` tags

### 2. The .bind() Pattern

Parent components use `.bind()` to invoke ServerRequests:

```jsx
// Parent component
function Dashboard() {
  return (
    <div>
      <TaskList.bind({
        requestType: 'GetTasksRequest',
        params: { status: 'active' }
      }) />
    </div>
  );
}
```

**The .bind() pattern:**
- Child components receive data via ServerRequest
- Parent specifies `requestType` and `params`
- WASM bridge handles request → ViewModel → component rendering
- No fetch() calls, no hardcoded URLs

### 3. Error ViewModel Handling

Error ViewModels are rendered like any other ViewModel:

```jsx
const TaskCard = FOSMVVM.viewModelComponent(({ viewModel }) => {
  // Handle error ViewModels
  if (viewModel.errorType === 'NotFoundError') {
    return (
      <div className="error">
        <p>{viewModel.message}</p>
        <p>{viewModel.suggestedAction}</p>
      </div>
    );
  }

  if (viewModel.errorType === 'ValidationError') {
    return (
      <div className="validation-error">
        <h3>{viewModel.title}</h3>
        <ul>
          {viewModel.errors.map(err => (
            <li key={err.field}>{err.message}</li>
          ))}
        </ul>
      </div>
    );
  }

  // Render success ViewModel
  return (
    <div className="task-card">
      <h3>{viewModel.title}</h3>
      <p>{viewModel.description}</p>
    </div>
  );
});
```

**Key principles:**
- No generic error handling
- Each error type has its own ViewModel
- Component conditionally renders based on `errorType` property
- Error rendering is just data rendering

### 4. Navigation Intents (Not URLs)

Use navigation intents, not hardcoded paths:

```jsx
// FOSMVVM utilities loaded via <script> tag, available on global namespace

// ❌ NEVER
<a href="/tasks/123">View Task</a>

// ✅ ALWAYS
<FOSMVVM.Link to={{ intent: 'viewTask', id: viewModel.id }}>
  {viewModel.linkText}
</FOSMVVM.Link>
```

**Navigation patterns:**
- Use `FOSMVVM.Link` from global namespace (loaded via script tag)
- Use `intent` property, not hardcoded paths
- Router maps intents to routes
- Platform-independent navigation

---

## Component Categories

### Display-Only Components

Components that just render data (no user interactions):

```jsx
const InfoCard = FOSMVVM.viewModelComponent(({ viewModel }) => {
  return (
    <div className="info-card">
      <h2>{viewModel.title}</h2>
      <p>{viewModel.description}</p>

      {viewModel.isActive && (
        <span className="badge">{viewModel.activeLabel}</span>
      )}
    </div>
  );
});

export default InfoCard;
```

**Characteristics:**
- Just renders ViewModel properties
- No event handlers (onClick, onSubmit, etc.)
- May have conditional rendering based on ViewModel state
- No .bind() calls to child components

### Interactive Components

Components with user actions that trigger ServerRequests:

```jsx
const ActionCard = FOSMVVM.viewModelComponent(({ viewModel }) => {
  return (
    <div className="action-card">
      <h2>{viewModel.title}</h2>
      <p>{viewModel.description}</p>

      <div className="actions">
        <button
          onClick={() => viewModel.operations.performAction()}
          disabled={!viewModel.canPerformAction}
        >
          {viewModel.actionLabel}
        </button>

        <button onClick={() => viewModel.operations.cancel()}>
          {viewModel.cancelLabel}
        </button>
      </div>
    </div>
  );
});

export default ActionCard;
```

### List Components

Components that render collections:

```jsx
const TaskList = FOSMVVM.viewModelComponent(({ viewModel }) => {
  if (viewModel.isEmpty) {
    return <div className="empty">{viewModel.emptyMessage}</div>;
  }

  return (
    <div className="task-list">
      <h2>{viewModel.title}</h2>
      <p>{viewModel.totalCount}</p>

      {viewModel.tasks.map(task => (
        <TaskCard.bind({
          requestType: 'GetTaskRequest',
          params: { id: task.id }
        }) />
      ))}
    </div>
  );
});

export default TaskList;
```

### Form Components

Components with validated input fields:

```jsx
const SignInForm = FOSMVVM.viewModelComponent(({ viewModel }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});

  const handleSubmit = async (e) => {
    e.preventDefault();

    const result = await viewModel.operations.submit({
      email,
      password
    });

    if (result.validationErrors) {
      setErrors(result.validationErrors);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>{viewModel.emailLabel}</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder={viewModel.emailPlaceholder}
        />
        {errors.email && <span className="error">{errors.email}</span>}
      </div>

      <div>
        <label>{viewModel.passwordLabel}</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder={viewModel.passwordPlaceholder}
        />
        {errors.password && <span className="error">{errors.password}</span>}
      </div>

      <button type="submit" disabled={viewModel.submitDisabled}>
        {viewModel.submitLabel}
      </button>
    </form>
  );
});

export default SignInForm;
```

---

## When to Use This Skill

- Creating a new React component for a FOSMVVM app
- Building UI to render a ViewModel
- Migrating Leaf templates to React
- Following an implementation plan that requires new views
- Creating forms with validation
- Building list views that compose child components

---

## What This Skill Generates

**Two files per invocation:**

| File | Location | Purpose |
|------|----------|---------|
| `{ViewName}View.test.js` | `src/components/{Feature}/` | Jest + React Testing Library tests |
| `{ViewName}View.jsx` | `src/components/{Feature}/` | React component |

**Test file generated FIRST (tests fail initially)**
**Implementation file generated SECOND (tests pass)**

**Note:** The corresponding ViewModel and ServerRequest should already exist (use other FOSMVVM generator skills).

---

## Project Structure Configuration

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{ViewName}` | View name (without "View" suffix) | `TaskList`, `SignIn` |
| `{Feature}` | Feature/module grouping | `Tasks`, `Auth` |

---

## Pattern Implementation

This skill references conversation context to determine component structure:

### Component Type Detection

From conversation context, the skill identifies:
- **ViewModel structure** (from prior discussion or specifications read by Claude)
- **ServerRequest details** (from requirements already in context)
- **Component category**: Display-only, interactive, form, or list
- **Error ViewModels** to handle

### Test Generation (FIRST)

Based on component type, generates `.test.js` with:
- **All components**: Success ViewModel rendering, error ViewModel rendering
- **Interactive**: Button clicks, operation verification
- **Form**: Input changes, validation errors, submission
- **List**: Empty state, multiple items, child binding

### Component Generation (SECOND)

Generates `.jsx` following patterns:
1. Import `viewModelComponent` wrapper
2. Handle error ViewModels with conditional rendering
3. Render success ViewModel
4. Add interactions (if interactive)
5. Add form state (if form)
6. Add child `.bind()` calls (if container)
7. Export wrapped component

### Context Sources

Skill references information from:
- **Prior conversation**: Requirements discussed with user
- **Specification files**: If Claude has read specifications into context
- **ViewModel definitions**: From codebase or discussion

### Step 5: Verify Completeness

Check:
- [ ] `.test.js` file exists
- [ ] `.jsx` file exists
- [ ] Component uses `FOSMVVM.viewModelComponent()` wrapper
- [ ] Component accesses FOSMVVM functions from global namespace
- [ ] Tests cover success and error ViewModels
- [ ] Tests cover user interactions (if applicable)

---

## Key Patterns

### Pattern: No Business Logic in Components

```jsx
// ❌ BAD - Component is transforming data
const TaskCard = FOSMVVM.viewModelComponent(({ viewModel }) => {
  const daysLeft = Math.ceil((viewModel.dueDate - Date.now()) / 86400000);
  return <span>{daysLeft} days remaining</span>;
});

// ✅ GOOD - ViewModel provides shaped result
const TaskCard = FOSMVVM.viewModelComponent(({ viewModel }) => {
  return <span>{viewModel.daysRemainingText}</span>;
});
```

### Pattern: No fetch() Calls

```jsx
// ❌ BAD - Component making HTTP requests
const TaskCard = FOSMVVM.viewModelComponent(({ viewModel }) => {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`/api/tasks/${viewModel.id}`)
      .then(r => r.json())
      .then(setData);
  }, [viewModel.id]);

  return <div>{data?.title}</div>;
});

// ✅ GOOD - Parent uses .bind() to invoke ServerRequest
<TaskCard.bind({
  requestType: 'GetTaskRequest',
  params: { id: taskId }
}) />
```

### Pattern: Error ViewModels Are Data

```jsx
// ❌ BAD - Generic error handling
const TaskCard = FOSMVVM.viewModelComponent(({ viewModel }) => {
  if (viewModel.error) {
    return <div>Error: {viewModel.error.message}</div>;
  }
  return <div>{viewModel.title}</div>;
});

// ✅ GOOD - Specific error ViewModels
const TaskCard = FOSMVVM.viewModelComponent(({ viewModel }) => {
  if (viewModel.errorType === 'NotFoundError') {
    return (
      <div className="not-found">
        <h3>{viewModel.errorTitle}</h3>
        <p>{viewModel.errorMessage}</p>
        <p>{viewModel.suggestedAction}</p>
      </div>
    );
  }

  if (viewModel.errorType === 'ValidationError') {
    return (
      <div className="validation-error">
        <h3>{viewModel.errorTitle}</h3>
        <ul>
          {viewModel.validationErrors.map(err => (
            <li key={err.field}>{err.message}</li>
          ))}
        </ul>
      </div>
    );
  }

  return <div>{viewModel.title}</div>;
});
```

### Pattern: Navigation Intents

```jsx
// ❌ BAD - Hardcoded URLs
const TaskRow = FOSMVVM.viewModelComponent(({ viewModel }) => {
  return (
    <div>
      <a href={`/tasks/${viewModel.id}`}>{viewModel.title}</a>
    </div>
  );
});

// ✅ GOOD - Navigation intents
// FOSMVVM utilities loaded via <script> tag, available on global namespace

const TaskRow = FOSMVVM.viewModelComponent(({ viewModel }) => {
  return (
    <div>
      <FOSMVVM.Link to={{ intent: 'viewTask', id: viewModel.id }}>
        {viewModel.title}
      </FOSMVVM.Link>
    </div>
  );
});
```

---

## File Organization

```
src/components/
├── {Feature}/
│   ├── {Feature}View.jsx             # Full page → {Feature}ViewModel
│   ├── {Feature}View.test.js         # Tests for {Feature}View
│   ├── {Entity}CardView.jsx          # Child component → {Entity}CardViewModel
│   ├── {Entity}CardView.test.js      # Tests for {Entity}CardView
│   └── {Entity}RowView.jsx           # Child component → {Entity}RowViewModel
├── Shared/
│   ├── HeaderView.jsx                # Shared components
│   └── FooterView.jsx
```

---

## Common Mistakes

### Computing Data in Components

```jsx
// ❌ BAD - Component is transforming data
const UserCard = FOSMVVM.viewModelComponent(({ viewModel }) => {
  return <div>{viewModel.firstName} {viewModel.lastName}</div>;
});

// ✅ GOOD - ViewModel provides shaped result
const UserCard = FOSMVVM.viewModelComponent(({ viewModel }) => {
  return <div>{viewModel.fullName}</div>;
});
```

### Making HTTP Requests Directly

```jsx
// ❌ BAD - fetch() call in component
const TaskList = FOSMVVM.viewModelComponent(({ viewModel }) => {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    fetch('/api/tasks').then(r => r.json()).then(setTasks);
  }, []);

  return <div>{tasks.map(t => <div key={t.id}>{t.title}</div>)}</div>;
});

// ✅ GOOD - Parent uses .bind() with ServerRequest
<TaskList.bind({
  requestType: 'GetTasksRequest',
  params: {}
}) />
```

### Hardcoding Text

```jsx
// ❌ BAD - Not localizable
const TaskCard = FOSMVVM.viewModelComponent(({ viewModel }) => {
  return (
    <button onClick={viewModel.operations.submit}>
      Submit
    </button>
  );
});

// ✅ GOOD - ViewModel provides localized text
const TaskCard = FOSMVVM.viewModelComponent(({ viewModel }) => {
  return (
    <button onClick={viewModel.operations.submit}>
      {viewModel.submitLabel}
    </button>
  );
});
```

### Using Hardcoded URLs

```jsx
// ❌ BAD - Hardcoded path
const TaskRow = FOSMVVM.viewModelComponent(({ viewModel }) => {
  return <a href={`/tasks/${viewModel.id}`}>{viewModel.title}</a>;
});

// ✅ GOOD - Navigation intent
// FOSMVVM utilities loaded via <script> tag, available on global namespace

const TaskRow = FOSMVVM.viewModelComponent(({ viewModel }) => {
  return (
    <FOSMVVM.Link to={{ intent: 'viewTask', id: viewModel.id }}>
      {viewModel.title}
    </FOSMVVM.Link>
  );
});
```

### Not Wrapping with viewModelComponent()

```jsx
// ❌ BAD - Missing viewModelComponent() wrapper
const TaskCard = ({ viewModel }) => {
  return <div>{viewModel.title}</div>;
};
export default TaskCard;

// ✅ GOOD - Wrapped with viewModelComponent()
const TaskCard = FOSMVVM.viewModelComponent(({ viewModel }) => {
  return <div>{viewModel.title}</div>;
});
export default TaskCard;
```

### Mismatched Filenames

```
// ❌ BAD - Filename doesn't match ViewModel
ViewModel: TaskListViewModel
Component: Tasks.jsx

// ✅ GOOD - Aligned names
ViewModel: TaskListViewModel
Component: TaskListView.jsx
```

---

## File Templates

See [reference.md](reference.md) for complete file templates.

---

## Naming Conventions

| Concept | Convention | Example |
|---------|------------|---------|
| Component file | `{Name}View.jsx` | `TaskListView.jsx`, `SignInView.jsx` |
| Test file | `{Name}View.test.js` | `TaskListView.test.js` |
| Component function | `{Name}View` | `TaskListView`, `SignInView` |
| ViewModel prop | `viewModel` | Always `viewModel` |

---

## Testing Patterns

### Test: Rendering with Success ViewModel

```javascript
it('renders task card with ViewModel', () => {
  const viewModel = {
    title: 'Test Task',
    description: 'Test Description',
    dueDate: 'Jan 30, 2026'
  };

  render(<TaskCard viewModel={viewModel} />);

  expect(screen.getByText('Test Task')).toBeInTheDocument();
  expect(screen.getByText('Test Description')).toBeInTheDocument();
});
```

### Test: Rendering with Error ViewModel

```javascript
it('renders NotFoundViewModel', () => {
  const viewModel = {
    errorType: 'NotFoundError',
    errorTitle: 'Task Not Found',
    errorMessage: 'The task you requested does not exist',
    suggestedAction: 'Try searching for a different task'
  };

  render(<TaskCard viewModel={viewModel} />);

  expect(screen.getByText('Task Not Found')).toBeInTheDocument();
  expect(screen.getByText(/does not exist/)).toBeInTheDocument();
});
```

### Test: User Interaction

```javascript
it('calls operation when button clicked', () => {
  const mockOperation = jest.fn();
  const viewModel = {
    title: 'Test Task',
    submitLabel: 'Complete Task',
    operations: {
      complete: mockOperation
    }
  };

  render(<TaskCard viewModel={viewModel} />);

  fireEvent.click(screen.getByText('Complete Task'));

  expect(mockOperation).toHaveBeenCalled();
});
```

---

## How to Use This Skill

**Invocation:**
```bash
/fosmvvm-react-view-generator
```

**Prerequisites:**
- ViewModel and ServerRequest details are understood from conversation
- Optionally, specification files have been read into context
- Component requirements (display-only, interactive, form, list) are clear from discussion

**Output:**
- `{ComponentName}.test.js` - Generated FIRST (tests fail)
- `{ComponentName}.jsx` - Generated SECOND (tests pass)

**Workflow integration:**
This skill is typically used after discussing requirements or reading specification files. The skill references that context automatically—no file paths or Q&A needed.

---

## See Also

- [Architecture Patterns](../shared/architecture-patterns.md) - Mental models and patterns
- [FOSMVVMArchitecture.md](../../docs/FOSMVVMArchitecture.md) - Full FOSMVVM architecture
- [fosmvvm-swiftui-view-generator](../fosmvvm-swiftui-view-generator/SKILL.md) - SwiftUI equivalent
- [fosmvvm-leaf-view-generator](../fosmvvm-leaf-view-generator/SKILL.md) - Leaf equivalent
- [reference.md](reference.md) - Complete file templates

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-23 | Initial skill for React view generation based on Kairos requirements |
