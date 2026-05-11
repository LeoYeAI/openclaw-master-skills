# Code Dimensions to Detect

Reference only — not in context. Consult when categorizing a new preference.

## Stack Decisions
- Mobile framework (Flutter, React Native, Swift, Kotlin)
- Web framework (Next.js, Nuxt, SvelteKit, vanilla)
- Backend (Node, Python, Go, Rust, serverless)
- Database (Postgres, SQLite, MongoDB, Pocketbase, Supabase)
- Hosting (Vercel, self-hosted, Docker, cloud)
- Auth approach (built-in, Auth0, Clerk, custom)
- State management (none, Redux, Zustand, Riverpod)
- CSS approach (Tailwind, CSS modules, styled-components)

## Code Style
- Formatting (Prettier yes/no, tabs/spaces, line length)
- Naming (camelCase, snake_case, kebab-case for files)
- Comments (minimal, verbose, JSDoc, none)
- Type strictness (strict, loose, any allowed)
- Error handling style (try-catch, Result types, early returns)
- Import organization (grouped, alphabetical, auto)

## Project Structure
- Monorepo vs separate repos
- Folder organization (by feature, by type, flat)
- Config files location (root, dedicated folder)
- Test location (colocated, separate folder)
- Documentation approach (README, docs folder, inline)

## Dependencies
- Dependency philosophy (minimal, use libraries, build custom)
- Version pinning (exact, caret, latest)
- Package manager (npm, pnpm, yarn, bun)

## Testing
- Test framework preference
- Coverage expectations
- Test style (unit heavy, integration heavy, e2e)
- TDD vs test-after

## Git & Workflow
- Commit style (conventional, free-form)
- Branch strategy (trunk, gitflow, simple)
- PR size preference
- CI/CD approach

## Language-Specific
- User may have different preferences per language
- Format: "Python: black formatter" or "TypeScript: strict mode"

## Context-Specific
- Different rules for different project types
- Format: "For MVPs: skip tests" or "For production: full typing"

## Anti-Patterns (Never)
- Tools/libraries user explicitly rejected
- Patterns user said they dislike
- Past mistakes to not repeat
