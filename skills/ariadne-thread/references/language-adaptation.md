# Language Adaptation

The 4-level index and design principles are universal. Below is how they map to specific language ecosystems.

## C / C++

| Aspect | Convention |
|--------|-----------|
| Directory layout | `include/` + `src/` + `tests/` (compiled); or flat `lib/` (header-only) |
| File naming | `snake_case.h` / `snake_case.cpp` (or `.hpp`/`.cc` per project) |
| Module boundary | Namespace + directory; public API = public headers in `include/` (or entry header for header-only) |
| Build system | CMake (`CMakeLists.txt`), MSBuild (`.sln`/`.vcxproj`), Makefile, or Meson |
| Package manager | vcpkg, Conan, or FetchContent |
| L0 Build commands | CMake: `cmake -B build && cmake --build build && ctest --test-dir build`; MSBuild: `msbuild project.sln /p:Configuration=Release /p:Platform=x64` |
| L2 Contract annotations | Doxygen `@pre`, `@post`, `@throws`, `@threadsafe` |
| Include order | system → third-party → project (with blank line separators) |
| Header guards | `#pragma once` (or `#ifndef PROJECT_MODULE_FILE_H`) |
| Naming | `snake_case` functions, `PascalCase` classes, `kCamelCase` or `SCREAMING_SNAKE` constants |

**Header-only libraries**: All code lives in headers (no `.cpp` files). The "public API" is the entry header (e.g., `library.hpp`) that includes everything. There is no build step for the library itself — consumers include the header and link required system libraries. Tests and examples typically live in separate projects or sibling directories. When indexing, treat the main header directory as a single module with logical sub-groups in `INDEX.md`.

## TypeScript / JavaScript

| Aspect | Convention |
|--------|-----------|
| Directory layout | `src/` flat or by domain; tests co-located as `*.test.ts` |
| File naming | `kebab-case.ts` |
| Module boundary | Directory + barrel `index.ts` (thin, < 20 lines) |
| Build system | `tsc`, esbuild, Vite |
| Package manager | npm, pnpm, bun |
| L2 Contract annotations | JSDoc `@pre`, `@post`, `@throws`, `@sideeffect` |
| Import order | builtins → packages → internal absolute → relative |
| Naming | `camelCase` functions, `PascalCase` classes, `SCREAMING_SNAKE` constants |

## Python

| Aspect | Convention |
|--------|-----------|
| Directory layout | `src/[package]/` + `tests/`; `__init__.py` for packages |
| File naming | `snake_case.py` |
| Module boundary | Package directory + `__init__.py` (public re-exports) |
| Build system | pip, uv, Poetry, setuptools |
| L2 Contract annotations | Docstring sections: `Pre:`, `Post:`, `Raises:`, `Side Effects:` |
| Import order | stdlib → third-party → local (isort / Ruff) |
| Naming | `snake_case` functions, `PascalCase` classes, `UPPER_CASE` constants |

## Go

| Aspect | Convention |
|--------|-----------|
| Directory layout | `cmd/` (entry points) + `internal/` (private) + `pkg/` (public) |
| File naming | `snake_case.go` |
| Module boundary | Package directory; exported = capitalized |
| Build system | `go build`, `go test` |
| L2 Contract annotations | Doc comments with `Precondition:`, `Returns:`, `Errors:` |
| Import order | stdlib → third-party → internal (goimports) |
| Naming | `camelCase`/`PascalCase` (exported), no underscores |

## Rust

| Aspect | Convention |
|--------|-----------|
| Directory layout | `src/` with `lib.rs` / `main.rs`; modules as dirs with `mod.rs` |
| File naming | `snake_case.rs` |
| Module boundary | `mod` + `pub` visibility |
| Build system | Cargo (`cargo build`, `cargo test`) |
| L2 Contract annotations | Doc comments with `# Panics`, `# Errors`, `# Safety` sections |
| Naming | `snake_case` functions, `PascalCase` types, `SCREAMING_SNAKE` constants |

## Java / Kotlin

| Aspect | Convention |
|--------|-----------|
| Directory layout | `src/main/java/...` + `src/test/java/...` (Maven/Gradle) |
| File naming | `PascalCase.java` (one public class per file) |
| Module boundary | Package + module-info.java (Java 9+) |
| Build system | Maven (`mvn`), Gradle (`gradle`) |
| L2 Contract annotations | Javadoc `@throws`, `@apiNote`, custom `@pre`/`@post` tags |
| Naming | `camelCase` methods, `PascalCase` classes, `SCREAMING_SNAKE` constants |
