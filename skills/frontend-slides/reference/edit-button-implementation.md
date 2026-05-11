# Edit Button Implementation (Inline Editing)

Only include when user opted "Yes" for inline editing in Phase 1. Otherwise skip all edit-related HTML/CSS/JS.

**Critical:** Do NOT use CSS `~` sibling selector for hover show/hide — `pointer-events: none` on the toggle breaks the hover chain. Use **JS-based hover with delay timeout**.

## HTML

```html
<div class="edit-hotzone"></div>
<button class="edit-toggle" id="editToggle" title="编辑模式 (E)">✏️</button>
```

## CSS (visibility via JS classes only)

```css
.edit-hotzone {
    position: fixed; top: 0; left: 0;
    width: 80px; height: 80px;
    z-index: 10000;
    cursor: pointer;
}
.edit-toggle {
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s ease;
    z-index: 10001;
}
.edit-toggle.show,
.edit-toggle.active {
    opacity: 1;
    pointer-events: auto;
}
```

## JavaScript

- Click on toggle → `editor.toggleEditMode()`
- Hotzone mouseenter → clear hideTimeout, `editToggle.classList.add('show')`
- Hotzone mouseleave → `hideTimeout = setTimeout(() => { if (!editor.isActive) editToggle.classList.remove('show'); }, 400)`
- Same timeout on editToggle mouseleave so moving to button doesn’t hide it
- Hotzone click → `editor.toggleEditMode()`
- Key E (when not in contenteditable) → `editor.toggleEditMode()`

Implement editor with: toggle edit mode, contenteditable on slide text, auto-save to localStorage, export/save file.
