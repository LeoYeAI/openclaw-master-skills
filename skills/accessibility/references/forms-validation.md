# Accessible Forms and Validation

Forms are critical for web interaction. This guide covers accessible form patterns, validation, and error handling.

---

## Form Label Requirements

### Every Input Needs a Label

```html
<!-- ✅ CORRECT - explicit label -->
<label for="email">Email address</label>
<input type="email" id="email" name="email">

<!-- ✅ CORRECT - implicit label -->
<label>
  Email address
  <input type="email" name="email">
</label>

<!-- ❌ WRONG - no label -->
<input type="email" placeholder="Email address">

<!-- ❌ WRONG - aria-label when visible label should exist -->
<input type="email" aria-label="Email address">
<!-- Screen reader gets it, but visual users don't -->
```

**Rule**: Use visible `<label>` elements. Placeholders are not labels.

---

## Required Fields

### Mark Required Fields

```html
<!-- ✅ Visual + programmatic -->
<label for="name">
  Full name <span aria-label="required">*</span>
</label>
<input
  type="text"
  id="name"
  name="name"
  required
  aria-required="true"
>

<!-- ✅ Text indicator -->
<label for="email">
  Email address (required)
</label>
<input type="email" id="email" required>

<!-- ❌ WRONG - visual only -->
<label for="phone">Phone *</label>
<input type="tel" id="phone">
<!-- Missing required attribute -->
```

### Group Required Indicator

```html
<form>
  <p><span aria-label="required">*</span> indicates required field</p>

  <label for="name">Name *</label>
  <input type="text" id="name" required>
</form>
```

---

## Input Types and Autocomplete

### Use Correct Input Types

```html
<!-- Text -->
<input type="text" autocomplete="name">
<input type="email" autocomplete="email">
<input type="tel" autocomplete="tel">
<input type="url">

<!-- Password -->
<input type="password" autocomplete="current-password">
<input type="password" autocomplete="new-password">

<!-- Numbers and Dates -->
<input type="number" min="1" max="10">
<input type="date" autocomplete="bday">

<!-- Choices -->
<input type="checkbox">
<input type="radio">
<select>...</select>
```

**Benefit**: Correct keyboard on mobile, better autofill.

---

## Field Instructions

### Use aria-describedby for Hints

```html
<label for="password">Password</label>
<input
  type="password"
  id="password"
  aria-describedby="password-requirements"
>
<div id="password-requirements">
  Must be at least 8 characters with one uppercase letter and one number.
</div>
```

### Complex Instructions

```html
<fieldset>
  <legend>Create your password</legend>

  <label for="new-password">New password</label>
  <input
    type="password"
    id="new-password"
    aria-describedby="password-reqs password-strength"
  >

  <div id="password-reqs">
    <ul>
      <li>At least 8 characters</li>
      <li>One uppercase letter</li>
      <li>One number</li>
    </ul>
  </div>

  <div id="password-strength" role="status" aria-live="polite">
    <!-- Dynamically updated: "Weak", "Medium", "Strong" -->
  </div>
</fieldset>
```

---

## Error Handling

### Identify Errors (WCAG 3.3.1)

```html
<label for="email">Email address</label>
<input
  type="email"
  id="email"
  aria-invalid="true"
  aria-describedby="email-error"
>
<span id="email-error" role="alert">
  Error: Please enter a valid email address
</span>
```

**Critical**:
- `aria-invalid="true"` on input
- `aria-describedby` points to error message
- Error message has `role="alert"` for announcement

### Error Summary

```html
<div role="alert" aria-labelledby="error-heading">
  <h2 id="error-heading">There are 2 errors in this form</h2>
  <ul>
    <li><a href="#email">Email format is incorrect</a></li>
    <li><a href="#password">Password is too short</a></li>
  </ul>
</div>

<!-- Links jump to fields -->
<label for="email">Email</label>
<input type="email" id="email" aria-invalid="true">
```

### Inline Validation

```typescript
function EmailInput() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [touched, setTouched] = useState(false);

  const validate = (value: string) => {
    if (!value) return 'Email is required';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
      return 'Email format is incorrect. Example: name@example.com';
    }
    return '';
  };

  const handleBlur = () => {
    setTouched(true);
    setError(validate(email));
  };

  return (
    <div>
      <label htmlFor="email">Email address</label>
      <input
        type="email"
        id="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        onBlur={handleBlur}
        aria-invalid={touched && !!error}
        aria-describedby={error ? 'email-error' : undefined}
      />
      {touched && error && (
        <span id="email-error" role="alert" className="error">
          {error}
        </span>
      )}
    </div>
  );
}
```

---

## Live Regions for Dynamic Updates

### Success Messages

```html
<div role="status" aria-live="polite">
  Form submitted successfully
</div>
```

### Error Announcements

```html
<div role="alert" aria-live="assertive" aria-atomic="true">
  Error: Please fix the 3 errors above before submitting
</div>
```

### Character Counter

```html
<label for="bio">Bio</label>
<textarea
  id="bio"
  maxlength="500"
  aria-describedby="bio-counter"
></textarea>
<div id="bio-counter" role="status" aria-live="polite">
  450 characters remaining
</div>
```

---

## Fieldsets and Radio Groups

### Radio Button Groups

```html
<fieldset>
  <legend>How did you hear about us?</legend>

  <label>
    <input type="radio" name="source" value="search">
    Search engine
  </label>

  <label>
    <input type="radio" name="source" value="social">
    Social media
  </label>

  <label>
    <input type="radio" name="source" value="friend">
    Friend referral
  </label>
</fieldset>
```

**Screen reader**: Reads legend before each option.

### Checkbox Groups

```html
<fieldset>
  <legend>Select your interests</legend>

  <label>
    <input type="checkbox" name="interests" value="design">
    Design
  </label>

  <label>
    <input type="checkbox" name="interests" value="development">
    Development
  </label>
</fieldset>
```

---

## Custom Form Controls

### Custom Checkbox

```html
<label class="custom-checkbox">
  <input type="checkbox" class="visually-hidden">
  <span class="checkbox-visual" aria-hidden="true">
    <!-- Custom visual -->
  </span>
  I agree to the terms
</label>

<style>
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.custom-checkbox input:focus + .checkbox-visual {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}
</style>
```

**Pattern**: Hide native input visually, not from screen readers. Style custom visual.

### Custom Select (Combobox)

```html
<label for="country-select">Country</label>
<div class="custom-select">
  <input
    type="text"
    id="country-select"
    role="combobox"
    aria-expanded="false"
    aria-controls="country-list"
    aria-autocomplete="list"
    aria-activedescendant=""
  >
  <ul id="country-list" role="listbox" hidden>
    <li role="option" id="option-us">United States</li>
    <li role="option" id="option-uk">United Kingdom</li>
  </ul>
</div>
```

**Complex**: Requires full keyboard support, ARIA state management. Prefer native `<select>` when possible.

---

## Form Submission

### Prevent Accidental Submission

```html
<form>
  <!-- Inputs -->

  <!-- Explicit submit button -->
  <button type="submit">Submit form</button>

  <!-- Other buttons must specify type="button" -->
  <button type="button" onclick="clearForm()">Clear</button>
</form>
```

### Confirmation for Destructive Actions

```html
<form onsubmit="return confirm('Are you sure you want to delete your account? This cannot be undone.')">
  <!-- Form fields -->
  <button type="submit" class="destructive">Delete account</button>
</form>
```

### Loading States

```html
<button type="submit" disabled aria-live="polite">
  <span aria-hidden="true"><!-- Spinner --></span>
  Submitting...
</button>
```

---

## Multi-Step Forms

### Progress Indicator

```html
<nav aria-label="Form progress">
  <ol>
    <li><a href="#step1" aria-current="step">Personal info</a></li>
    <li><a href="#step2">Address</a></li>
    <li><a href="#step3">Payment</a></li>
  </ol>
</nav>
```

### Step Navigation

```html
<form>
  <fieldset id="step1">
    <legend>Step 1: Personal information</legend>
    <!-- Fields -->
    <button type="button" onclick="goToStep(2)">Next</button>
  </fieldset>

  <fieldset id="step2" hidden>
    <legend>Step 2: Address</legend>
    <!-- Fields -->
    <button type="button" onclick="goToStep(1)">Previous</button>
    <button type="button" onclick="goToStep(3)">Next</button>
  </fieldset>

  <fieldset id="step3" hidden>
    <legend>Step 3: Payment</legend>
    <!-- Fields -->
    <button type="button" onclick="goToStep(2)">Previous</button>
    <button type="submit">Submit</button>
  </fieldset>
</form>
```

---

## File Uploads

### Accessible File Input

```html
<label for="resume">Upload resume (PDF, DOC, max 5MB)</label>
<input
  type="file"
  id="resume"
  name="resume"
  accept=".pdf,.doc,.docx"
  aria-describedby="file-requirements"
>
<div id="file-requirements">
  Accepted formats: PDF, Word Document. Maximum size: 5MB.
</div>
```

### Upload Status

```html
<div role="status" aria-live="polite" aria-atomic="true">
  Uploading file... 45% complete
</div>
```

---

## Common Patterns

### Login Form

```html
<form>
  <h2>Sign in to your account</h2>

  <label for="username">Username or email</label>
  <input
    type="text"
    id="username"
    name="username"
    autocomplete="username"
    required
  >

  <label for="password">Password</label>
  <input
    type="password"
    id="password"
    name="password"
    autocomplete="current-password"
    required
  >

  <label>
    <input type="checkbox" name="remember">
    Remember me
  </label>

  <button type="submit">Sign in</button>
  <a href="/forgot-password">Forgot password?</a>
</form>
```

### Contact Form

```html
<form>
  <h2>Contact us</h2>

  <label for="name">Name *</label>
  <input type="text" id="name" required autocomplete="name">

  <label for="email">Email *</label>
  <input type="email" id="email" required autocomplete="email">

  <label for="message">Message *</label>
  <textarea id="message" required rows="5"></textarea>

  <button type="submit">Send message</button>

  <div role="alert" aria-live="assertive" aria-atomic="true">
    <!-- Error/success message appears here -->
  </div>
</form>
```

---

## Testing Checklist

- [ ] All inputs have associated labels
- [ ] Required fields marked (visual + programmatic)
- [ ] Error messages linked with aria-describedby
- [ ] aria-invalid set on fields with errors
- [ ] Error summary at top of form with role="alert"
- [ ] Success/error messages use live regions
- [ ] Correct input types and autocomplete
- [ ] Tab order is logical
- [ ] Can submit with keyboard (Enter key)
- [ ] Focus visible on all form controls
- [ ] Tested with screen reader

---

**Key Takeaway**: Accessible forms require visible labels, clear error messages, and proper ARIA attributes. Test with keyboard and screen reader.
