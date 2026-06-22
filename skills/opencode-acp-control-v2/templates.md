# OpenCode Prompt Templates

Templates para tareas comunes de código.

## 🎯 Uso

```json
{"jsonrpc":"2.0","id":2,"method":"session/prompt","params":{"sessionId":"sess_xyz","prompt":[{"type":"text","text":"<template>"}]}}
```

---

## 📋 Templates por categoría

### Refactoring

**Simple refactor:**
```
Refactor the following code to improve readability and maintainability:

<code>

Focus on:
- Clear naming
- DRY principles
- Separation of concerns
```

**Extract function/method:**
```
Extract the logic in <file>:<line_start>-<line_end> into a separate function.

Requirements:
- Meaningful function name
- Proper parameters
- Add JSDoc/TSDoc
- Handle edge cases
```

**Convert to TypeScript:**
```
Convert this JavaScript code to TypeScript with proper types:

<code>

Add:
- Interface definitions
- Type annotations
- Generic types where appropriate
```

---

### Features

**Add new feature:**
```
Implement <feature_name> for <context>.

Requirements:
<list_requirements>

Files to modify:
- <file1>: <what to do>
- <file2>: <what to do>

Constraints:
- Keep existing functionality
- Follow existing patterns
- Add tests
```

**Add API endpoint:**
```
Add a new API endpoint: <method> <path>

Requirements:
- Request validation
- Error handling
- Response format: <format>
- Auth: <yes/no/type>

Example request:
<example>

Example response:
<example>
```

**Add component:**
```
Create a new React component: <ComponentName>

Props:
- <prop1>: <type> - <description>
- <prop2>: <type> - <description>

Features:
- <feature1>
- <feature2>

Styling: Tailwind CSS
```

---

### Bug fixes

**Debug and fix:**
```
There's a bug in <file>:<line_range>.

Symptoms:
<describe_symptoms>

Expected behavior:
<expected>

Actual behavior:
<actual>

Steps to reproduce:
1. <step1>
2. <step2>

Please:
1. Identify the root cause
2. Fix the bug
3. Add a test to prevent regression
```

**Fix TypeScript error:**
```
Fix this TypeScript error:

Error: <error_message>
File: <file>:<line>

Code:
<code>

Provide:
- The fix
- Explanation of why it was wrong
```

---

### Testing

**Add unit tests:**
```
Add unit tests for <file_or_function>.

Requirements:
- Test framework: Vitest
- Coverage: >80%
- Test cases:
  - Happy path
  - Edge cases
  - Error cases
  - Boundary conditions
```

**Add integration tests:**
```
Add integration tests for <feature>.

Requirements:
- Test framework: Vitest
- Test API endpoints
- Test DB interactions
- Mock external services
```

---

### Documentation

**Add JSDoc/TSDoc:**
```
Add comprehensive JSDoc/TSDoc comments to <file>.

Include:
- Description
- @param for all parameters
- @returns for return value
- @throws for errors
- @example for usage
```

**Update README:**
```
Update README.md for <project_name>.

Include:
- Description
- Installation steps
- Usage examples
- Configuration options
- API reference (if applicable)
- Contributing guidelines
```

---

### Database

**Create migration:**
```
Create a Supabase migration for:

Changes:
- <change1>
- <change2>

Requirements:
- Safe for existing data
- Include rollback
- Add indexes if needed
- Update RLS policies if needed
```

**Add RLS policy:**
```
Add RLS policy for <table>.

Requirements:
- Users can only <action> their own data
- Admin role can <action> all data
- Service role bypasses RLS
```

---

### Performance

**Optimize query:**
```
Optimize this query/function:

<code>

Current issues:
- Slow: <why>
- Called frequently: <context>

Requirements:
- Maintain functionality
- Add appropriate indexes
- Consider caching
```

**Reduce bundle size:**
```
Analyze and reduce bundle size for <file_or_component>.

Current size: <size>

Techniques to consider:
- Code splitting
- Tree shaking
- Dynamic imports
- Lazy loading
```

---

### Security

**Security audit:**
```
Perform a security audit of <file_or_feature>.

Check for:
- Input validation
- SQL injection
- XSS vulnerabilities
- CSRF protection
- Authentication/authorization
- Sensitive data exposure
- Rate limiting

Provide:
- Vulnerabilities found
- Severity levels
- Fixes for each
```

---

## 🎨 Customización

Para crear tus propios templates:

1. Copia un template existente
2. Modifica para tu caso de uso
3. Guarda en `templates/custom/<name>.md`
4. Úsalo en tus prompts

---

*Templates v1.0 - 2026-03-05*
