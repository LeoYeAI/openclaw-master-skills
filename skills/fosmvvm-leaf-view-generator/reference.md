# FOSMVVM Leaf View Generator - Reference Templates

Complete templates for generating Leaf views that render ViewModels.

> **Conceptual context:** See [SKILL.md](SKILL.md) for when and why to use this skill.
> **Architecture context:** See [FOSMVVMArchitecture.md](../../docs/FOSMVVMArchitecture.md) for full FOSMVVM understanding.

---

## Placeholders

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `{Feature}` | Feature area (PascalCase) | `Dashboard`, `UserManagement`, `KanbanBoard` |
| `{feature}` | Same, kebab-case for CSS | `dashboard`, `user-management`, `kanban-board` |
| `{Entity}` | Entity name (PascalCase) | `User`, `Idea`, `Document` |
| `{entity}` | Same, kebab-case for HTML | `user`, `idea`, `document` |
| `{WebAppTarget}` | WebApp SPM target | `WebApp`, `KairosWebApp` |
| `{ViewModelsTarget}` | Shared ViewModels target | `ViewModels` |

---

## View-ViewModel Alignment

**Critical:** Leaf filenames must match the ViewModel they render.

| ViewModel | Leaf Template |
|-----------|---------------|
| `{Feature}ViewModel` | `{Feature}View.leaf` |
| `{Entity}CardViewModel` | `{Entity}CardView.leaf` |
| `{Entity}RowViewModel` | `{Entity}RowView.leaf` |
| `{Modal}ViewModel` | `{Modal}View.leaf` |

---

## Template 1: Base Layout

**Location:** `Sources/{WebAppTarget}/Resources/Views/base.leaf`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>#import("title")</title>
    <link rel="stylesheet" href="/styles/main.css">
</head>
<body>
    <header class="site-header">
        #import("header")
    </header>

    <main class="site-content">
        #import("content")
    </main>

    <footer class="site-footer">
        #import("footer")
    </footer>

    <script src="/scripts/main.js"></script>
</body>
</html>
```

---

## Template 2: Full-Page Template

**Location:** `Sources/{WebAppTarget}/Resources/Views/{Feature}/{Feature}View.leaf`

**Renders:** `{Feature}ViewModel`

```html
#extend("base"):

#export("title"):
#(viewModel.pageTitle)
#endexport

#export("content"):
<div class="{feature}-container">
    <header class="{feature}-header">
        <h1>#(viewModel.title)</h1>
        #if(viewModel.subtitle):
        <p class="subtitle">#(viewModel.subtitle)</p>
        #endif
    </header>

    <main class="{feature}-content">
        #for(item in viewModel.items):
        #extend("{Feature}/{Entity}CardView")
        #endfor

        #if(viewModel.items.count == 0):
        <div class="empty-state">
            <p>#(viewModel.emptyMessage)</p>
        </div>
        #endif
    </main>
</div>
#endexport

#endextend
```

---

## Template 3: Card Fragment

**Location:** `Sources/{WebAppTarget}/Resources/Views/{Feature}/{Entity}CardView.leaf`

**Renders:** `{Entity}CardViewModel`

```html
<div class="{entity}-card"
     data-{entity}-id="#(card.id)"
     data-status="#(card.status)"
     data-category="#(card.category)"
     draggable="true">

    <div class="card-header">
        <span class="category-badge #(card.category)">#(card.categoryDisplayName)</span>
        #if(card.isHighPriority):
        <span class="priority-badge">#(card.priorityLabel)</span>
        #endif
    </div>

    <div class="card-content">
        <p class="card-text">#(card.contentPreview)</p>
    </div>

    <div class="card-footer">
        <div class="card-creator">
            <span class="creator-avatar">#(card.creatorInitial)</span>
            <span class="creator-name">#(card.creatorName)</span>
        </div>
        <span class="card-date">#(card.createdAt)</span>
    </div>
</div>
```

**Key points:**
- NO `#extend("base")` - this is a fragment
- Single root element (`<div class="{entity}-card">`)
- `data-{entity}-id` for JS identification
- `data-status`, `data-category` store raw enum values
- Display names (`categoryDisplayName`) for visible text
- `LocalizableDate` property (`createdAt`) renders automatically

---

## Template 4: Row Fragment

**Location:** `Sources/{WebAppTarget}/Resources/Views/{Feature}/{Entity}RowView.leaf`

**Renders:** `{Entity}RowViewModel`

```html
<tr class="{entity}-row"
    data-{entity}-id="#(row.id)"
    data-status="#(row.status)">

    <td class="name-cell">
        <span class="avatar">#(row.initial)</span>
        <span class="name">#(row.name)</span>
    </td>

    <td class="status-cell">
        <span class="status-badge #(row.status)">#(row.statusDisplayName)</span>
    </td>

    <td class="date-cell">
        #(row.createdAt)
    </td>

    <td class="actions-cell">
        <button class="edit-btn" data-action="edit">#(row.editButtonTitle)</button>
        <button class="delete-btn" data-action="delete">#(row.deleteButtonTitle)</button>
    </td>
</tr>
```

---

## Template 5: Column/Container Fragment

**Location:** `Sources/{WebAppTarget}/Resources/Views/{Feature}/{Entity}ColumnView.leaf`

**Renders:** `{Entity}ColumnViewModel`

```html
<div class="{entity}-column" data-status="#(column.status)">
    <div class="column-header">
        <span class="status-indicator #(column.status)"></span>
        <h3 class="column-title">#(column.displayName)</h3>
        <span class="column-count">#(column.count)</span>
    </div>

    <div class="column-cards">
        #for(card in column.cards):
        #extend("{Feature}/{Entity}CardView")
        #endfor

        #if(column.cards.count == 0):
        <div class="empty-column">#(column.emptyMessage)</div>
        #endif
    </div>
</div>
```

---

## Template 6: Modal Fragment

**Location:** `Sources/{WebAppTarget}/Resources/Views/{Feature}/{Action}ModalView.leaf`

**Renders:** `{Action}ModalViewModel`

```html
<div class="modal" id="{action}-modal">
    <div class="modal-backdrop" onclick="Modal.hide()"></div>
    <div class="modal-content">
        <div class="modal-header">
            <h2>#(modal.title)</h2>
            <button class="close-btn" onclick="Modal.hide()">&times;</button>
        </div>

        <form id="{action}-form" data-action="{action}">
            <div class="modal-body">
                <div class="form-group">
                    <label for="content">#(modal.contentLabel)</label>
                    <textarea id="content" name="content"
                              placeholder="#(modal.contentPlaceholder)"
                              required></textarea>
                </div>

                <div class="form-group">
                    <label for="category">#(modal.categoryLabel)</label>
                    <select id="category" name="category" required>
                        #for(option in modal.categoryOptions):
                        <option value="#(option.value)">#(option.displayName)</option>
                        #endfor
                    </select>
                </div>
            </div>

            <div class="modal-footer">
                <button type="button" class="btn-cancel" onclick="Modal.hide()">
                    #(modal.cancelButtonTitle)
                </button>
                <button type="submit" class="btn-submit">
                    #(modal.submitButtonTitle)
                </button>
            </div>
        </form>
    </div>
</div>
```

---

## WebApp Route Examples

### Rendering a Full Page

```swift
// GET /{feature}
app.get("{feature}") { req async throws -> View in
    let serverRequest = {Feature}ViewModelRequest()
    guard let response = try await serverRequest.processRequest(baseURL: app.serverBaseURL) else {
        throw Abort(.internalServerError)
    }

    return try await req.view.render(
        "{Feature}/{Feature}View",
        ["viewModel": response]
    )
}
```

### Rendering a Fragment (HTML-over-the-wire)

```swift
// POST /move-{entity}
app.post("move-{entity}") { req async throws -> Response in
    let body = try req.content.decode(Move{Entity}Request.RequestBody.self)
    let serverRequest = Move{Entity}Request(requestBody: body)
    guard let response = try await serverRequest.processRequest(baseURL: app.serverBaseURL) else {
        throw Abort(.internalServerError)
    }

    // Return HTML fragment, not full page
    return try await req.view.render(
        "{Feature}/{Entity}CardView",
        ["card": response.viewModel]
    ).encodeResponse(for: req)
}
```

---

## Localizable+Leaf Integration

FOSMVVM provides `LeafDataRepresentable` conformance for all Localizable types.

**Location:** `FOSUtilities/Sources/FOSMVVMVapor/Extensions/Localizable+Leaf.swift`

```swift
import FOSMVVM
import LeafKit

extension LocalizableString: LeafDataRepresentable {
    public var leafData: LeafData {
        .string((try? localizedString) ?? "")
    }
}

extension LocalizableDate: LeafDataRepresentable {
    public var leafData: LeafData {
        .string((try? localizedString) ?? "")
    }
}

// Also: LocalizableInt, LocalizableArray, LocalizableCompoundValue, LocalizableSubstitutions
```

**Why this matters:**
- `LocalizableString` encodes as plain string → works by default
- `LocalizableDate` encodes as keyed container → needs explicit LeafData conversion
- Without this, dates render as `[ds: "2", ls: "Dec 27, 2025", v: "..."]`

---

## Data Attribute Reference

| Purpose | Pattern | JS Access |
|---------|---------|-----------|
| Entity ID | `data-{entity}-id` | `element.dataset.{entity}Id` |
| Status | `data-status` | `element.dataset.status` |
| Category | `data-{category}` | `element.dataset.{category}` |
| Action | `data-action` | `element.dataset.action` |

**HTML (kebab-case):**
```html
<div data-user-id="#(user.id)" data-status="#(user.status)">
```

**JS (camelCase):**
```javascript
const userId = element.dataset.userId;
const status = element.dataset.status;
```

---

## Conditional Rendering Patterns

### Optional Properties

```html
#if(card.assignee):
<div class="assignee">
    <span class="name">#(card.assignee.name)</span>
</div>
#else:
<div class="unassigned">#(card.unassignedLabel)</div>
#endif
```

### Boolean Flags

```html
#if(card.isHighPriority):
<span class="priority-badge">#(card.priorityLabel)</span>
#endif
```

### Empty States

```html
#if(items.count == 0):
<div class="empty-state">
    <p>#(viewModel.emptyMessage)</p>
</div>
#else:
#for(item in items):
#extend("{Feature}/{Entity}CardView")
#endfor
#endif
```

---

## Troubleshooting

### Dates Show Debug Description

**Symptom:** `[ds: "2", ls: "Dec 27, 2025", v: "1766598117.309064"]`

**Fix:**
1. Verify `Localizable+Leaf.swift` exists in FOSMVVMVapor
2. Verify `LeafKit` is a dependency
3. Run `swift package clean && swift build`

### Data Attributes Missing in JS

**Symptom:** `element.dataset.entityId` is `undefined`

**Fix:**
1. HTML uses `data-entity-id` (kebab-case)
2. JS reads as `dataset.entityId` (camelCase)
3. Verify template variable: `#(card.id)` is not empty

### Localized String Shows Key Path

**Symptom:** Shows `{Entity}CardViewModel.statusDisplayName` instead of "Active"

**Fix:**
1. YAML file exists: `{Entity}CardViewModel.yml`
2. YAML has the key: `statusDisplayName: "Active"`
3. ViewModel uses `@LocalizedString`

---

## Checklist

### Full-Page Template
- [ ] Extends base layout: `#extend("base"):`
- [ ] Exports title: `#export("title"):...#endexport`
- [ ] Exports content: `#export("content"):...#endexport`
- [ ] Filename matches ViewModel: `{Feature}View.leaf` → `{Feature}ViewModel`

### Fragment Template
- [ ] NO `#extend("base")` - just the component
- [ ] Single root element
- [ ] `data-{entity}-id` for JS identification
- [ ] Raw enum values in data attributes
- [ ] Display names from ViewModel properties
- [ ] Filename matches ViewModel: `{Entity}CardView.leaf` → `{Entity}CardViewModel`

### ViewModel Properties
- [ ] `id: ModelIdType` for data-{entity}-id
- [ ] Raw enum for data-{field} attributes
- [ ] `@LocalizedString` for display names
- [ ] `@LocalizedDate` for dates
