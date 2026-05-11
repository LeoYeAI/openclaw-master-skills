# Contributing to OpenClaw Security Suite

Thank you for your interest in contributing to the OpenClaw Security Suite! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Adding Security Patterns](#adding-security-patterns)
- [Reporting Security Vulnerabilities](#reporting-security-vulnerabilities)

## Code of Conduct

This project follows a Code of Conduct that all contributors are expected to adhere to:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- TypeScript knowledge
- Understanding of security concepts (for pattern contributions)

### Setup Development Environment

1. Clone the repository:
```bash
git clone https://github.com/PaoloRollo/openclaw-sec.git
cd openclaw-sec
```

2. Install dependencies:
```bash
npm install
```

3. Run tests to ensure everything works:
```bash
npm test
```

4. Build the project:
```bash
npm run build
```

## Development Workflow

### 1. Create a Branch

Create a feature branch from `main`:
```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `test/` - Test additions/modifications
- `refactor/` - Code refactoring

### 2. Make Your Changes

- Follow Test-Driven Development (TDD) when possible
- Write tests before implementation
- Ensure all existing tests pass
- Add appropriate error handling
- Update documentation as needed

### 3. Commit Your Changes

Follow conventional commit format:
```bash
git commit -m "feat: add new security pattern for X"
git commit -m "fix: correct validation logic in Y"
git commit -m "docs: update configuration examples"
git commit -m "test: add benchmark for Z module"
```

Commit types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `chore:` - Maintenance tasks

## Pull Request Process

### Before Submitting

1. **Run all tests**: `npm test`
2. **Run benchmarks**: `npm run test -- benchmarks` (ensure no regression)
3. **Build successfully**: `npm run build`
4. **Update documentation**: If you changed APIs or added features
5. **Add tests**: For all new functionality

### Submission Checklist

- [ ] Tests pass locally (`npm test`)
- [ ] Code follows TypeScript and ESLint standards
- [ ] Commit messages follow conventional format
- [ ] Documentation updated (if applicable)
- [ ] Benchmarks run without performance regression
- [ ] PR description clearly explains changes

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing done

## Performance Impact
Any performance implications?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Benchmarks run
- [ ] No breaking changes (or clearly documented)
```

## Coding Standards

### TypeScript Style

- Use **strict mode** TypeScript
- Prefer `const` over `let`, avoid `var`
- Use explicit types, avoid `any` except when absolutely necessary
- Use async/await over promises where readable
- Export interfaces and types for public APIs

### Code Organization

```typescript
// 1. Imports (organized: external, then internal)
import Database from 'better-sqlite3';
import { Severity, Finding } from '../types';

// 2. Type definitions
interface MyConfig {
  enabled: boolean;
}

// 3. Constants
const DEFAULT_TIMEOUT = 5000;

// 4. Class/function implementation
export class MyModule {
  // Constructor first
  constructor(config: MyConfig) { }

  // Public methods
  async validate(): Promise<void> { }

  // Private methods
  private helper(): void { }
}
```

### Error Handling

Always include comprehensive error handling:

```typescript
try {
  // Operation
} catch (error) {
  throw new CustomError(
    'Descriptive error message',
    { cause: error, context: { relevant: 'data' } }
  );
}
```

### Documentation

Add JSDoc comments for public APIs:

```typescript
/**
 * Validates a URL for SSRF vulnerabilities
 * @param url - The URL to validate
 * @returns Promise resolving to findings array
 * @throws {ValidationError} If URL is malformed
 */
async validate(url: string): Promise<Finding[]> { }
```

## Testing Requirements

### Test Coverage

- Minimum 80% code coverage for new code
- All public methods must have tests
- Test both success and error paths
- Include edge cases and boundary conditions

### Test Structure

```typescript
describe('ModuleName', () => {
  let module: ModuleName;

  beforeEach(() => {
    module = new ModuleName(config);
  });

  test('detects specific threat', async () => {
    const result = await module.scan('malicious input');
    expect(result).toHaveLength(1);
    expect(result[0].severity).toBe(Severity.CRITICAL);
  });

  test('handles safe input correctly', async () => {
    const result = await module.scan('safe input');
    expect(result).toHaveLength(0);
  });

  test('validates input parameters', () => {
    expect(() => module.scan(null as any)).toThrow();
  });
});
```

### Running Tests

```bash
# Run all tests
npm test

# Run specific test file
npm test path-validator

# Run with coverage
npm test -- --coverage

# Run benchmarks
npm test -- benchmarks
```

## Adding Security Patterns

Security patterns are the core of this project. When adding new patterns:

### 1. Research the Attack

- Understand the attack vector thoroughly
- Find real-world examples
- Determine severity level appropriately

### 2. Create the Pattern

```typescript
export const myNewPattern: SecurityPattern = {
  id: 'category_language_001',
  category: 'prompt_injection',
  subcategory: 'my_subcategory',
  pattern: /regex-pattern-here/i,
  severity: Severity.HIGH,
  language: 'en',
  description: 'Clear description of what this detects',
  examples: [
    'example attack 1',
    'example attack 2',
    'example attack 3'
  ],
  falsePositiveRisk: 'low', // or 'medium' or 'high'
  enabled: true,
  tags: ['relevant', 'tags']
};
```

### 3. Test the Pattern

Create comprehensive tests:
- Should detect the attack
- Should not false-positive on legitimate input
- Should handle edge cases
- Should work with obfuscation attempts

### 4. Document False Positives

If your pattern has known false positives:
- Document them in the pattern description
- Set appropriate `falsePositiveRisk`
- Consider making it configurable

### 5. Benchmark Impact

Run benchmarks to ensure no performance regression:
```bash
npm test -- benchmarks/performance
```

## Reporting Security Vulnerabilities

**IMPORTANT**: Do not report security vulnerabilities through public GitHub issues.

Instead:
1. Email security details to [security contact - to be added]
2. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you on a fix.

## Recognition

Contributors will be:
- Listed in the project README
- Credited in release notes
- Acknowledged in documentation

Thank you for helping make OpenClaw Security Suite better and more secure!

## Questions?

If you have questions about contributing:
- Open a GitHub Discussion
- Check existing issues and PRs
- Review the README and documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
