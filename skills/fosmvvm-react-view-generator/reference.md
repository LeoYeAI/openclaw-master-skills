# FOSMVVM React View Generator - Reference Templates

Complete file templates for generating React ViewModelViews.

> **Conceptual context:** See [SKILL.md](SKILL.md) for when and why to use this skill.
> **Architecture context:** See [FOSMVVMArchitecture.md](../../docs/FOSMVVMArchitecture.md) for full FOSMVVM understanding.

## Placeholders

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `{ViewName}` | View name (without "View" suffix) | `TaskList`, `SignIn` |
| `{ViewModel}` | Full ViewModel type name | `TaskListViewModel` |
| `{ServerRequest}` | Full ServerRequest type name | `GetTasksRequest` |
| `{Feature}` | Feature/module grouping | `Tasks`, `Auth` |

---

## Specification Document Format

Specifications serve as documentation and reference. When Claude reads specification files into conversation context, the skill references that information during generation. Recommended format:

```markdown
# {Feature} UI Specification

## ServerRequest
Type: {RequestTypeName}
Protocol: ShowRequest | ViewModelRequest | CreateRequest | UpdateRequest | DeleteRequest

### Query Parameters
- {param}: {type} - {description}

### Fragment Parameters
- {param}: {type} - {description}

### Request Body
- {field}: {type} - {description}

## ViewModel
Type: {ViewModelTypeName}

### Properties
- {property}: {type} - {description}

### Error ViewModels
- {ErrorViewModelType}: when {condition}

## UI Behaviors
- **Display Mode:** list | detail | form | dashboard
- **Filtering:** by {fields}
- **Sorting:** by {fields}
- **Search:** across {fields}
- **Pagination:** yes/no

## User Interactions

### {Interaction Name}
**Trigger:** {button click | form submit | link click}
**Action:** {description}
**ServerRequest:** {RequestType}
**Parameters:** {what gets passed}
**Success:** {what happens}
**Errors:** {error types and handling}

## Platform-Specific Notes
- **React:** {any React-specific behavior}
- **SwiftUI:** {any SwiftUI-specific behavior}
```

---

# Template 1: Test File for Display-Only Component

**Location:** `src/components/{Feature}/{ViewName}View.test.js`

**Generated FIRST - Tests FAIL initially**

```javascript
// {ViewName}View.test.js
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import { render, screen } from '@testing-library/react';
import {ViewName}View from './{ViewName}View';

describe('{ViewName}View', () => {
  it('renders with success ViewModel', () => {
    const viewModel = {
      title: 'Test Title',
      description: 'Test Description',
      statusLabel: 'Active'
    };

    render(<{ViewName}View viewModel={viewModel} />);

    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
    expect(screen.getByText('Active')).toBeInTheDocument();
  });

  it('renders conditional content when available', () => {
    const viewModel = {
      title: 'Test Title',
      description: 'Test Description',
      subtitle: 'Test Subtitle',
      isActive: true,
      activeLabel: 'Currently Active'
    };

    render(<{ViewName}View viewModel={viewModel} />);

    expect(screen.getByText('Test Subtitle')).toBeInTheDocument();
    expect(screen.getByText('Currently Active')).toBeInTheDocument();
  });

  it('hides conditional content when not available', () => {
    const viewModel = {
      title: 'Test Title',
      description: 'Test Description',
      isActive: false
    };

    render(<{ViewName}View viewModel={viewModel} />);

    expect(screen.queryByText('Currently Active')).not.toBeInTheDocument();
  });

  it('renders NotFoundViewModel', () => {
    const viewModel = {
      errorType: 'NotFoundError',
      errorTitle: 'Not Found',
      errorMessage: 'The requested item was not found',
      suggestedAction: 'Try searching for a different item'
    };

    render(<{ViewName}View viewModel={viewModel} />);

    expect(screen.getByText('Not Found')).toBeInTheDocument();
    expect(screen.getByText(/was not found/)).toBeInTheDocument();
    expect(screen.getByText(/Try searching/)).toBeInTheDocument();
  });
});
```

---

# Template 2: Test File for Interactive Component

**Location:** `src/components/{Feature}/{ViewName}View.test.js`

**Generated FIRST - Tests FAIL initially**

```javascript
// {ViewName}View.test.js
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import { render, screen, fireEvent } from '@testing-library/react';
import {ViewName}View from './{ViewName}View';

describe('{ViewName}View', () => {
  it('renders with success ViewModel', () => {
    const viewModel = {
      title: 'Test Title',
      description: 'Test Description',
      actionLabel: 'Perform Action',
      cancelLabel: 'Cancel',
      operations: {
        performAction: jest.fn(),
        cancel: jest.fn()
      }
    };

    render(<{ViewName}View viewModel={viewModel} />);

    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Perform Action')).toBeInTheDocument();
  });

  it('calls performAction when action button clicked', () => {
    const mockPerformAction = jest.fn();
    const viewModel = {
      title: 'Test Title',
      actionLabel: 'Perform Action',
      cancelLabel: 'Cancel',
      operations: {
        performAction: mockPerformAction,
        cancel: jest.fn()
      }
    };

    render(<{ViewName}View viewModel={viewModel} />);

    fireEvent.click(screen.getByText('Perform Action'));

    expect(mockPerformAction).toHaveBeenCalledTimes(1);
  });

  it('calls cancel when cancel button clicked', () => {
    const mockCancel = jest.fn();
    const viewModel = {
      title: 'Test Title',
      actionLabel: 'Perform Action',
      cancelLabel: 'Cancel',
      operations: {
        performAction: jest.fn(),
        cancel: mockCancel
      }
    };

    render(<{ViewName}View viewModel={viewModel} />);

    fireEvent.click(screen.getByText('Cancel'));

    expect(mockCancel).toHaveBeenCalledTimes(1);
  });

  it('disables action button when not allowed', () => {
    const viewModel = {
      title: 'Test Title',
      actionLabel: 'Perform Action',
      cancelLabel: 'Cancel',
      canPerformAction: false,
      operations: {
        performAction: jest.fn(),
        cancel: jest.fn()
      }
    };

    render(<{ViewName}View viewModel={viewModel} />);

    const actionButton = screen.getByText('Perform Action');
    expect(actionButton).toBeDisabled();
  });

  it('renders ValidationErrorViewModel', () => {
    const viewModel = {
      errorType: 'ValidationError',
      errorTitle: 'Validation Failed',
      validationErrors: [
        { field: 'email', message: 'Email is required' },
        { field: 'password', message: 'Password must be at least 8 characters' }
      ]
    };

    render(<{ViewName}View viewModel={viewModel} />);

    expect(screen.getByText('Validation Failed')).toBeInTheDocument();
    expect(screen.getByText('Email is required')).toBeInTheDocument();
    expect(screen.getByText(/Password must be at least 8/)).toBeInTheDocument();
  });
});
```

---

# Template 3: Display-Only Component

**Location:** `src/components/{Feature}/{ViewName}View.jsx`

**Generated SECOND - Makes tests PASS**

```jsx
// {ViewName}View.jsx
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

// FOSMVVM utilities loaded via <script> tag, available on global namespace

const {ViewName}View = FOSMVVM.viewModelComponent(({ viewModel }) => {
  // Handle error ViewModels
  if (viewModel.errorType === 'NotFoundError') {
    return (
      <div className="error not-found">
        <h3>{viewModel.errorTitle}</h3>
        <p>{viewModel.errorMessage}</p>
        <p className="suggestion">{viewModel.suggestedAction}</p>
      </div>
    );
  }

  // Render success ViewModel
  return (
    <div className="{feature}-card">
      <h2>{viewModel.title}</h2>
      <p>{viewModel.description}</p>

      {viewModel.subtitle && (
        <p className="subtitle">{viewModel.subtitle}</p>
      )}

      {viewModel.isActive && (
        <span className="badge">{viewModel.activeLabel}</span>
      )}

      <div className="metadata">
        <span className="status">{viewModel.statusLabel}</span>
        <span className="date">{viewModel.createdAt}</span>
      </div>
    </div>
  );
});

export default {ViewName}View;

// Parent component usage:
// <{ViewName}View.bind({
//   requestType: '{ServerRequest}',
//   params: { id: itemId }
// }) />
```

---

# Template 4: Interactive Component

**Location:** `src/components/{Feature}/{ViewName}View.jsx`

**Generated SECOND - Makes tests PASS**

```jsx
// {ViewName}View.jsx
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

// FOSMVVM utilities loaded via <script> tag, available on global namespace

const {ViewName}View = FOSMVVM.viewModelComponent(({ viewModel }) => {
  // Handle error ViewModels
  if (viewModel.errorType === 'ValidationError') {
    return (
      <div className="error validation-error">
        <h3>{viewModel.errorTitle}</h3>
        <ul className="validation-errors">
          {viewModel.validationErrors.map(err => (
            <li key={err.field}>
              <strong>{err.field}:</strong> {err.message}
            </li>
          ))}
        </ul>
      </div>
    );
  }

  if (viewModel.errorType === 'NotFoundError') {
    return (
      <div className="error not-found">
        <h3>{viewModel.errorTitle}</h3>
        <p>{viewModel.errorMessage}</p>
        <p className="suggestion">{viewModel.suggestedAction}</p>
      </div>
    );
  }

  // Render success ViewModel
  return (
    <div className="{feature}-action-card">
      <h2>{viewModel.title}</h2>
      <p>{viewModel.description}</p>

      <div className="actions">
        <button
          className="btn-cancel"
          onClick={() => viewModel.operations.cancel()}
        >
          {viewModel.cancelLabel}
        </button>

        <button
          className="btn-primary"
          onClick={() => viewModel.operations.performAction()}
          disabled={!viewModel.canPerformAction}
        >
          {viewModel.actionLabel}
        </button>
      </div>
    </div>
  );
});

export default {ViewName}View;
```

---

# Template 5: List Component

**Location:** `src/components/{Feature}/{ViewName}View.jsx`

**Generated SECOND - Makes tests PASS**

```jsx
// {ViewName}View.jsx
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

// FOSMVVM utilities loaded via <script> tag, available on global namespace
import {Entity}CardView from './{Entity}CardView';

const {ViewName}View = FOSMVVM.viewModelComponent(({ viewModel }) => {
  // Handle error ViewModels
  if (viewModel.errorType === 'NotFoundError') {
    return (
      <div className="error not-found">
        <h3>{viewModel.errorTitle}</h3>
        <p>{viewModel.errorMessage}</p>
        <p className="suggestion">{viewModel.suggestedAction}</p>
      </div>
    );
  }

  // Handle empty state
  if (viewModel.isEmpty) {
    return (
      <div className="empty-state">
        <p>{viewModel.emptyMessage}</p>
      </div>
    );
  }

  // Render success ViewModel
  return (
    <div className="{feature}-list">
      <header className="list-header">
        <h2>{viewModel.title}</h2>
        <p className="count">{viewModel.totalCount}</p>
      </header>

      <div className="list-filters">
        <select
          value={viewModel.currentFilter}
          onChange={(e) => viewModel.operations.filterBy(e.target.value)}
        >
          {viewModel.filterOptions.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div className="list-items">
        {viewModel.items.map(item => (
          <{Entity}CardView.bind({
            requestType: 'Get{Entity}Request',
            params: { id: item.id }
          }) />
        ))}
      </div>

      {viewModel.hasMore && (
        <button
          className="btn-load-more"
          onClick={() => viewModel.operations.loadMore()}
        >
          {viewModel.loadMoreLabel}
        </button>
      )}
    </div>
  );
});

export default {ViewName}View;
```

---

# Template 6: Form Component

**Location:** `src/components/{Feature}/{ViewName}View.jsx`

**Generated SECOND - Makes tests PASS**

```jsx
// {ViewName}View.jsx
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import { useState } from 'react';
// FOSMVVM utilities loaded via <script> tag, available on global namespace

const {ViewName}View = FOSMVVM.viewModelComponent(({ viewModel }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: ''
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));

    // Clear error for this field when user types
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setIsSubmitting(true);

    const result = await viewModel.operations.submit(formData);

    setIsSubmitting(false);

    if (result.validationErrors) {
      setErrors(result.validationErrors);
    } else if (result.success) {
      // Handle success (e.g., show success message, navigate)
    }
  };

  // Render success ViewModel
  return (
    <div className="{feature}-form">
      <h2>{viewModel.title}</h2>
      <p>{viewModel.description}</p>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">{viewModel.emailLabel}</label>
          <input
            id="email"
            type="email"
            value={formData.email}
            onChange={(e) => handleChange('email', e.target.value)}
            placeholder={viewModel.emailPlaceholder}
            className={errors.email ? 'error' : ''}
          />
          {errors.email && (
            <span className="error-message">{errors.email}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="password">{viewModel.passwordLabel}</label>
          <input
            id="password"
            type="password"
            value={formData.password}
            onChange={(e) => handleChange('password', e.target.value)}
            placeholder={viewModel.passwordPlaceholder}
            className={errors.password ? 'error' : ''}
          />
          {errors.password && (
            <span className="error-message">{errors.password}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="name">{viewModel.nameLabel}</label>
          <input
            id="name"
            type="text"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder={viewModel.namePlaceholder}
            className={errors.name ? 'error' : ''}
          />
          {errors.name && (
            <span className="error-message">{errors.name}</span>
          )}
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="btn-cancel"
            onClick={() => viewModel.operations.cancel()}
          >
            {viewModel.cancelLabel}
          </button>

          <button
            type="submit"
            className="btn-primary"
            disabled={isSubmitting || viewModel.submitDisabled}
          >
            {isSubmitting ? viewModel.submittingLabel : viewModel.submitLabel}
          </button>
        </div>
      </form>
    </div>
  );
});

export default {ViewName}View;
```

---

# Template 7: Test File for List Component

**Location:** `src/components/{Feature}/{ViewName}View.test.js`

**Generated FIRST - Tests FAIL initially**

```javascript
// {ViewName}View.test.js
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import { render, screen, fireEvent } from '@testing-library/react';
import {ViewName}View from './{ViewName}View';

describe('{ViewName}View', () => {
  it('renders list with items', () => {
    const viewModel = {
      title: 'Test List',
      totalCount: '3 items',
      isEmpty: false,
      items: [
        { id: '1', title: 'Item 1' },
        { id: '2', title: 'Item 2' },
        { id: '3', title: 'Item 3' }
      ],
      filterOptions: [
        { value: 'all', label: 'All Items' },
        { value: 'active', label: 'Active Only' }
      ],
      currentFilter: 'all',
      hasMore: false,
      operations: {
        filterBy: jest.fn(),
        loadMore: jest.fn()
      }
    };

    render(<{ViewName}View viewModel={viewModel} />);

    expect(screen.getByText('Test List')).toBeInTheDocument();
    expect(screen.getByText('3 items')).toBeInTheDocument();
  });

  it('renders empty state when no items', () => {
    const viewModel = {
      isEmpty: true,
      emptyMessage: 'No items found'
    };

    render(<{ViewName}View viewModel={viewModel} />);

    expect(screen.getByText('No items found')).toBeInTheDocument();
  });

  it('calls filterBy when filter changes', () => {
    const mockFilterBy = jest.fn();
    const viewModel = {
      title: 'Test List',
      totalCount: '3 items',
      isEmpty: false,
      items: [{ id: '1', title: 'Item 1' }],
      filterOptions: [
        { value: 'all', label: 'All Items' },
        { value: 'active', label: 'Active Only' }
      ],
      currentFilter: 'all',
      hasMore: false,
      operations: {
        filterBy: mockFilterBy,
        loadMore: jest.fn()
      }
    };

    render(<{ViewName}View viewModel={viewModel} />);

    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'active' } });

    expect(mockFilterBy).toHaveBeenCalledWith('active');
  });

  it('shows load more button when hasMore is true', () => {
    const viewModel = {
      title: 'Test List',
      totalCount: '50 items',
      isEmpty: false,
      items: [{ id: '1', title: 'Item 1' }],
      filterOptions: [],
      currentFilter: 'all',
      hasMore: true,
      loadMoreLabel: 'Load More',
      operations: {
        filterBy: jest.fn(),
        loadMore: jest.fn()
      }
    };

    render(<{ViewName}View viewModel={viewModel} />);

    expect(screen.getByText('Load More')).toBeInTheDocument();
  });

  it('calls loadMore when load more button clicked', () => {
    const mockLoadMore = jest.fn();
    const viewModel = {
      title: 'Test List',
      totalCount: '50 items',
      isEmpty: false,
      items: [{ id: '1', title: 'Item 1' }],
      filterOptions: [],
      currentFilter: 'all',
      hasMore: true,
      loadMoreLabel: 'Load More',
      operations: {
        filterBy: jest.fn(),
        loadMore: mockLoadMore
      }
    };

    render(<{ViewName}View viewModel={viewModel} />);

    fireEvent.click(screen.getByText('Load More'));

    expect(mockLoadMore).toHaveBeenCalledTimes(1);
  });
});
```

---

# Template 8: Test File for Form Component

**Location:** `src/components/{Feature}/{ViewName}View.test.js`

**Generated FIRST - Tests FAIL initially**

```javascript
// {ViewName}View.test.js
//
// Copyright (c) 2026 Your Organization. All rights reserved.
// License: Your License

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import {ViewName}View from './{ViewName}View';

describe('{ViewName}View', () => {
  it('renders form with all fields', () => {
    const viewModel = {
      title: 'Sign In',
      description: 'Enter your credentials',
      emailLabel: 'Email',
      emailPlaceholder: 'you@example.com',
      passwordLabel: 'Password',
      passwordPlaceholder: 'Enter password',
      nameLabel: 'Name',
      namePlaceholder: 'Your name',
      submitLabel: 'Submit',
      cancelLabel: 'Cancel',
      submitDisabled: false,
      operations: {
        submit: jest.fn(),
        cancel: jest.fn()
      }
    };

    render(<{ViewName}View viewModel={viewModel} />);

    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByLabelText('Name')).toBeInTheDocument();
  });

  it('updates field values when user types', () => {
    const viewModel = {
      title: 'Sign In',
      emailLabel: 'Email',
      passwordLabel: 'Password',
      nameLabel: 'Name',
      submitLabel: 'Submit',
      cancelLabel: 'Cancel',
      submitDisabled: false,
      operations: {
        submit: jest.fn(),
        cancel: jest.fn()
      }
    };

    render(<{ViewName}View viewModel={viewModel} />);

    const emailInput = screen.getByLabelText('Email');
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

    expect(emailInput.value).toBe('test@example.com');
  });

  it('calls submit operation with form data', async () => {
    const mockSubmit = jest.fn().mockResolvedValue({ success: true });
    const viewModel = {
      title: 'Sign In',
      emailLabel: 'Email',
      passwordLabel: 'Password',
      nameLabel: 'Name',
      submitLabel: 'Submit',
      cancelLabel: 'Cancel',
      submitDisabled: false,
      operations: {
        submit: mockSubmit,
        cancel: jest.fn()
      }
    };

    render(<{ViewName}View viewModel={viewModel} />);

    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText('Password'), {
      target: { value: 'password123' }
    });
    fireEvent.change(screen.getByLabelText('Name'), {
      target: { value: 'Test User' }
    });

    fireEvent.click(screen.getByText('Submit'));

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
        name: 'Test User'
      });
    });
  });

  it('displays validation errors from server', async () => {
    const mockSubmit = jest.fn().mockResolvedValue({
      validationErrors: {
        email: 'Email is required',
        password: 'Password must be at least 8 characters'
      }
    });

    const viewModel = {
      title: 'Sign In',
      emailLabel: 'Email',
      passwordLabel: 'Password',
      nameLabel: 'Name',
      submitLabel: 'Submit',
      cancelLabel: 'Cancel',
      submitDisabled: false,
      operations: {
        submit: mockSubmit,
        cancel: jest.fn()
      }
    };

    render(<{ViewName}View viewModel={viewModel} />);

    fireEvent.click(screen.getByText('Submit'));

    await waitFor(() => {
      expect(screen.getByText('Email is required')).toBeInTheDocument();
      expect(screen.getByText(/Password must be at least 8/)).toBeInTheDocument();
    });
  });

  it('clears field error when user types', async () => {
    const mockSubmit = jest.fn().mockResolvedValue({
      validationErrors: {
        email: 'Email is required'
      }
    });

    const viewModel = {
      title: 'Sign In',
      emailLabel: 'Email',
      submitLabel: 'Submit',
      operations: {
        submit: mockSubmit
      }
    };

    render(<{ViewName}View viewModel={viewModel} />);

    // Submit to get validation error
    fireEvent.click(screen.getByText('Submit'));

    await waitFor(() => {
      expect(screen.getByText('Email is required')).toBeInTheDocument();
    });

    // Type in field to clear error
    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'test@example.com' }
    });

    expect(screen.queryByText('Email is required')).not.toBeInTheDocument();
  });

  it('disables submit button during submission', async () => {
    let resolveSubmit;
    const mockSubmit = jest.fn().mockReturnValue(
      new Promise(resolve => {
        resolveSubmit = resolve;
      })
    );

    const viewModel = {
      title: 'Sign In',
      emailLabel: 'Email',
      submitLabel: 'Submit',
      submittingLabel: 'Submitting...',
      submitDisabled: false,
      operations: {
        submit: mockSubmit
      }
    };

    render(<{ViewName}View viewModel={viewModel} />);

    const submitButton = screen.getByText('Submit');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Submitting...')).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
    });

    resolveSubmit({ success: true });

    await waitFor(() => {
      expect(submitButton).not.toBeDisabled();
    });
  });
});
```

---

# Quick Reference: Common Test Patterns

## Test: Success ViewModel Rendering

```javascript
it('renders with success ViewModel', () => {
  const viewModel = {
    title: 'Test Title',
    description: 'Test Description'
  };

  render(<MyView viewModel={viewModel} />);

  expect(screen.getByText('Test Title')).toBeInTheDocument();
});
```

## Test: Error ViewModel Rendering

```javascript
it('renders NotFoundViewModel', () => {
  const viewModel = {
    errorType: 'NotFoundError',
    errorTitle: 'Not Found',
    errorMessage: 'Item not found'
  };

  render(<MyView viewModel={viewModel} />);

  expect(screen.getByText('Not Found')).toBeInTheDocument();
});
```

## Test: Button Click

```javascript
it('calls operation when button clicked', () => {
  const mockOperation = jest.fn();
  const viewModel = {
    submitLabel: 'Submit',
    operations: { submit: mockOperation }
  };

  render(<MyView viewModel={viewModel} />);

  fireEvent.click(screen.getByText('Submit'));

  expect(mockOperation).toHaveBeenCalled();
});
```

## Test: Form Input

```javascript
it('updates input value', () => {
  const viewModel = {
    emailLabel: 'Email',
    operations: { submit: jest.fn() }
  };

  render(<MyView viewModel={viewModel} />);

  const input = screen.getByLabelText('Email');
  fireEvent.change(input, { target: { value: 'test@example.com' } });

  expect(input.value).toBe('test@example.com');
});
```

## Test: Async Operation

```javascript
it('calls async operation', async () => {
  const mockSubmit = jest.fn().mockResolvedValue({ success: true });
  const viewModel = {
    submitLabel: 'Submit',
    operations: { submit: mockSubmit }
  };

  render(<MyView viewModel={viewModel} />);

  fireEvent.click(screen.getByText('Submit'));

  await waitFor(() => {
    expect(mockSubmit).toHaveBeenCalled();
  });
});
```

---

# Quick Reference: Component Patterns

## Pattern: Basic Component Structure

```jsx
// FOSMVVM utilities loaded via <script> tag, available on global namespace

const MyView = FOSMVVM.viewModelComponent(({ viewModel }) => {
  return <div>{viewModel.title}</div>;
});

export default MyView;
```

## Pattern: Error Handling

```jsx
const MyView = FOSMVVM.viewModelComponent(({ viewModel }) => {
  if (viewModel.errorType === 'NotFoundError') {
    return <div className="error">{viewModel.errorMessage}</div>;
  }

  return <div>{viewModel.title}</div>;
});
```

## Pattern: Conditional Rendering

```jsx
const MyView = FOSMVVM.viewModelComponent(({ viewModel }) => {
  return (
    <div>
      <h2>{viewModel.title}</h2>
      {viewModel.subtitle && <p>{viewModel.subtitle}</p>}
      {viewModel.isActive && <span>{viewModel.activeLabel}</span>}
    </div>
  );
});
```

## Pattern: Button Handler

```jsx
const MyView = FOSMVVM.viewModelComponent(({ viewModel }) => {
  return (
    <button
      onClick={() => viewModel.operations.submit()}
      disabled={!viewModel.canSubmit}
    >
      {viewModel.submitLabel}
    </button>
  );
});
```

## Pattern: Child Binding

```jsx
const ListView = viewModelComponent(({ viewModel }) => {
  return (
    <div>
      {viewModel.items.map(item => (
        <ItemCard.bind({
          requestType: 'GetItemRequest',
          params: { id: item.id }
        }) />
      ))}
    </div>
  );
});
```

## Pattern: Navigation

```jsx
// FOSMVVM utilities loaded via <script> tag, available on global namespace

const MyView = FOSMVVM.viewModelComponent(({ viewModel }) => {
  return (
    <FOSMVVM.Link to={{ intent: 'viewDetails', id: viewModel.id }}>
      {viewModel.linkText}
    </FOSMVVM.Link>
  );
});
```

---

# Checklists

## Component Checklist

**All Components:**
- [ ] Uses `FOSMVVM.viewModelComponent()` from global namespace (script tag loaded)
- [ ] Wrapped with `viewModelComponent()`
- [ ] Receives `{ viewModel }` prop
- [ ] Exported as default
- [ ] Filename matches ViewModel name

**Error Handling:**
- [ ] Checks `viewModel.errorType` for error ViewModels
- [ ] Renders specific UI for each error type
- [ ] No generic error handling

**Interactive Components:**
- [ ] Event handlers call `viewModel.operations.*`
- [ ] No direct fetch() calls
- [ ] Button disabled states based on ViewModel properties

**List Components:**
- [ ] Empty state rendering when `viewModel.isEmpty`
- [ ] Child components use `.bind()` pattern
- [ ] No hardcoded request types or URLs

**Form Components:**
- [ ] useState for form data
- [ ] Field-level error display
- [ ] Clear errors on input change
- [ ] Disable submit during submission

## Test Checklist

**All Tests:**
- [ ] Imports from `@testing-library/react`
- [ ] `describe` block for component
- [ ] Test rendering with success ViewModel
- [ ] Test rendering with error ViewModels

**Interactive Tests:**
- [ ] Test button click handlers
- [ ] Test operation calls with jest.fn()
- [ ] Test disabled states

**List Tests:**
- [ ] Test empty state
- [ ] Test multiple items
- [ ] Test filter/sort operations

**Form Tests:**
- [ ] Test input value changes
- [ ] Test form submission
- [ ] Test validation errors
- [ ] Test error clearing on input
- [ ] Test submit button disabled during submission

---

## Completeness Verification

Before completing generation, verify:

- [ ] `.test.js` file exists
- [ ] `.jsx` file exists
- [ ] Component uses `FOSMVVM.viewModelComponent()` from global namespace (script tag loaded)
- [ ] Component wrapped with `viewModelComponent()`
- [ ] Tests cover success ViewModel
- [ ] Tests cover error ViewModels
- [ ] Tests cover user interactions (if applicable)
- [ ] No hardcoded URLs in component
- [ ] No fetch() calls in component
- [ ] No business logic in component (data transformation, calculations)

---

## Common File Locations

```
src/
├── components/
│   ├── {Feature}/
│   │   ├── {ViewName}View.jsx
│   │   ├── {ViewName}View.test.js
│   │   ├── {Entity}CardView.jsx
│   │   ├── {Entity}CardView.test.js
│   │   └── {Entity}RowView.jsx
│   └── Shared/
│       ├── HeaderView.jsx
│       └── FooterView.jsx
├── viewmodels/
│   └── {Feature}ViewModel.js
└── requests/
    └── {Feature}Request.js
```
