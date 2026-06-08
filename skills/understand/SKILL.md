---
name: understand
description: Analyze a codebase to produce an interactive knowledge graph for understanding architecture, components, and relationships
argument-hint: [options]
---

# /understand

Analyze the current codebase and produce a `knowledge-graph.json` file in `.understand-anything/`. This file powers the interactive dashboard for exploring the project's architecture.

## Options

- `$ARGUMENTS` may contain:
  - `--full` — Force a full rebuild, ignoring any existing graph
  - A directory path — Scope analysis to a specific subdirectory

---

## Phase 0 — Pre-flight

Determine whether to run a full analysis or incremental update.

1. Set `PROJECT_ROOT` to the current working directory.
2. Get the current git commit hash:
   ```bash
   git rev-parse HEAD
   ```
3. Create the intermediate output directory:
   ```bash
   mkdir -p $PROJECT_ROOT/.understand-anything/intermediate
   ```
4. Check if `$PROJECT_ROOT/.understand-anything/knowledge-graph.json` exists. If it does, read it.
5. Check if `$PROJECT_ROOT/.understand-anything/meta.json` exists. If it does, read it to get `gitCommitHash`.
6. **Decision logic:**

   | Condition | Action |
   |---|---|
   | `--full` flag in `$ARGUMENTS` | Full analysis (all phases) |
   | No existing graph or meta | Full analysis (all phases) |
   | Existing graph + unchanged commit hash | Report "Graph is up to date" and STOP |
   | Existing graph + changed files | Incremental update (re-analyze changed files only) |

   For incremental updates, get the changed file list:
   ```bash
   git diff <lastCommitHash>..HEAD --name-only
   ```
   If this returns no files, report "Graph is up to date" and STOP.

7. **Collect project context for subagent injection:**
   - Read `README.md` (or `README.rst`, `readme.md`) from `$PROJECT_ROOT` if it exists. Store as `$README_CONTENT` (first 3000 characters).
   - Read the primary package manifest (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`) if it exists. Store as `$MANIFEST_CONTENT`.
   - Capture the top-level directory tree:
     ```bash
     find $PROJECT_ROOT -maxdepth 2 -type f -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' | head -100
     ```
     Store as `$DIR_TREE`.
   - Detect the project entry point by checking for common patterns: `src/index.ts`, `src/main.ts`, `src/App.tsx`, `main.py`, `main.go`, `src/main.rs`, `index.js`. Store first match as `$ENTRY_POINT`.

---

## Phase 1 — SCAN (Full analysis only)

Dispatch a subagent using the prompt template at `./project-scanner-prompt.md`. Read the template file and pass the full content as the subagent's prompt, appending the following additional context:

> **Additional context from main session:**
>
> Project README (first 3000 chars):
> ```
> $README_CONTENT
> ```
>
> Package manifest:
> ```
> $MANIFEST_CONTENT
> ```
>
> Use this context to produce more accurate project name, description, and framework detection. The README and manifest are authoritative — prefer their information over heuristics.

Pass these parameters in the dispatch prompt:

> Scan this project directory to discover all source files, detect languages and frameworks.
> Project root: `$PROJECT_ROOT`
> Write output to: `$PROJECT_ROOT/.understand-anything/intermediate/scan-result.json`

After the subagent completes, read `$PROJECT_ROOT/.understand-anything/intermediate/scan-result.json` to get:
- Project name, description
- Languages, frameworks
- File list with line counts
- Complexity estimate

**Gate check:** If >200 files, inform the user and suggest scoping with a subdirectory argument. Proceed only if user confirms or add guidance that this may take a while.

---

## Phase 2 — ANALYZE

### Full analysis path

Batch the file list from Phase 1 into groups of **5-10 files each** (aim for balanced batch sizes).

For each batch, dispatch a subagent using the prompt template at `./file-analyzer-prompt.md`. Run up to **3 subagents concurrently** using parallel dispatch. Read the template once, then for each batch pass the full template content as the subagent's prompt, appending the following additional context:

> **Additional context from main session:**
>
> Project: `<projectName>` — `<projectDescription>`
> Frameworks detected: `<frameworks from Phase 1>`
> Languages: `<languages from Phase 1>`
>
> Framework-specific guidance:
> - If React/Next.js: files in `app/` or `pages/` are routes, `components/` are UI, `lib/` or `utils/` are utilities
> - If Express/Fastify: files in `routes/` are API endpoints, `middleware/` is middleware, `models/` or `db/` is data
> - If Python Django: `views.py` are controllers, `models.py` is data, `urls.py` is routing, `templates/` is UI
> - If Go: `cmd/` is entry points, `internal/` is private packages, `pkg/` is public packages
>
> Use this context to produce more accurate summaries and better classify file roles.

Fill in batch-specific parameters below and dispatch:

> Analyze these source files and produce GraphNode and GraphEdge objects.
> Project root: `$PROJECT_ROOT`
> Project: `<projectName>`
> Languages: `<languages>`
> Batch index: `<batchIndex>`
> Write output to: `$PROJECT_ROOT/.understand-anything/intermediate/batch-<batchIndex>.json`
>
> All project files (for import resolution):
> `<full file path list from scan>`
>
> Files to analyze in this batch:
> 1. `<path>` (<sizeLines> lines)
> 2. `<path>` (<sizeLines> lines)
> ...

After ALL batches complete, read each `batch-<N>.json` file and merge:
- Combine all `nodes` arrays. If duplicate node IDs exist, keep the later occurrence.
- Combine all `edges` arrays. Deduplicate by the composite key `source + target + type`.

### Incremental update path

Use the changed files list from Phase 0. Batch and dispatch file-analyzer subagents using the same process as above, but only for changed files.

After batches complete, merge with the existing graph:
1. Remove old nodes whose `filePath` matches any changed file
2. Remove old edges whose `source` or `target` references a removed node
3. Add new nodes and edges from the fresh analysis

---

## Phase 3 — ASSEMBLE

Merge all file-analyzer results into a single set of nodes and edges. Then perform basic integrity cleanup:

- Remove any edge whose `source` or `target` references a node ID that does not exist in the merged node set
- Remove duplicate node IDs (keep the last occurrence)
- Log any removed edges or nodes for the final summary

---

## Phase 4 — ARCHITECTURE

Dispatch a subagent using the prompt template at `./architecture-analyzer-prompt.md`. Read the template file and pass the full content as the subagent's prompt, appending the following additional context:

> **Additional context from main session:**
>
> Frameworks detected: `<frameworks from Phase 1>`
>
> Directory tree (top 2 levels):
> ```
> $DIR_TREE
> ```
>
> Framework-specific layer hints:
> - If React/Next.js: `app/` or `pages/` → UI Layer, `api/` → API Layer, `lib/` → Service Layer, `components/` → UI Layer
> - If Express: `routes/` → API Layer, `controllers/` → Service Layer, `models/` → Data Layer, `middleware/` → Middleware Layer
> - If Python Django: `views/` → API Layer, `models/` → Data Layer, `templates/` → UI Layer, `management/` → CLI Layer
> - If Go: `cmd/` → Entry Points, `internal/` → Service Layer, `pkg/` → Shared Library, `api/` → API Layer
>
> Use the directory tree and framework hints to inform layer assignments. Directory structure is strong evidence for layer boundaries.

Pass these parameters in the dispatch prompt:

> Analyze this codebase's structure to identify architectural layers.
> Project root: `$PROJECT_ROOT`
> Write output to: `$PROJECT_ROOT/.understand-anything/intermediate/layers.json`
> Project: `<projectName>` — `<projectDescription>`
>
> File nodes:
> ```json
> [list of {id, name, filePath, summary, tags} for all file-type nodes]
> ```
>
> Import edges:
> ```json
> [list of edges with type "imports"]
> ```

After the subagent completes, read `$PROJECT_ROOT/.understand-anything/intermediate/layers.json` to get the layer assignments.

`layers.json` may be either:
- a top-level JSON array of layer objects, or
- an envelope object such as `{ "layers": [...] }` from the current prompt/template output

Normalize either form into a final top-level `layers` array before assembling the graph. Each final saved layer object MUST match this exact shape:

```json
[
  {
    "id": "layer:<kebab-case-name>",
    "name": "<layer name>",
    "description": "<what belongs in this layer>",
    "nodeIds": ["file:src/App.tsx", "file:src/main.tsx"]
  }
]
```

Rules:
- `id` is required and must be unique
- `nodeIds` is required and must contain graph node IDs, not raw file paths
- If the intermediate output is an envelope object, unwrap its `layers` array before any other normalization
- If the subagent returns file paths, convert them to file node IDs before assembling the final graph
- Drop any `nodeIds` that do not exist in the merged node set
- Do not use a `nodes` field in the final saved layer objects

**For incremental updates:** Always re-run architecture analysis on the full merged node set, since layer assignments may shift when files change.

**Context for incremental updates:** When re-running architecture analysis, also inject the previous layer definitions:

> Previous layer definitions (for naming consistency):
> ```json
> [previous layers from existing graph]
> ```
>
> Maintain the same layer names and IDs where possible. Only add/remove layers if the file structure has materially changed.

---

## Phase 5 — TOUR

Dispatch a subagent using the prompt template at `./tour-builder-prompt.md`. Read the template file and pass the full content as the subagent's prompt, appending the following additional context:

> **Additional context from main session:**
>
> Project README (first 3000 chars):
> ```
> $README_CONTENT
> ```
>
> Project entry point: `$ENTRY_POINT`
>
> Use the README to align the tour narrative with the project's own documentation. Start the tour from the entry point if one was detected. The tour should tell the same story the README tells, but through the lens of actual code structure.

Pass these parameters in the dispatch prompt:

> Create a guided learning tour for this codebase.
> Project root: `$PROJECT_ROOT`
> Write output to: `$PROJECT_ROOT/.understand-anything/intermediate/tour.json`
> Project: `<projectName>` — `<projectDescription>`
> Languages: `<languages>`
>
> Nodes (summarized):
> ```json
> [list of {id, name, filePath, summary, type} for key nodes]
> ```
>
> Layers:
> ```json
> [layers from Phase 4]
> ```
>
> Key edges:
> ```json
> [imports and calls edges]
> ```

After the subagent completes, read `$PROJECT_ROOT/.understand-anything/intermediate/tour.json` to get the tour steps.

`tour.json` may be either:
- a top-level JSON array of tour step objects, or
- an envelope object such as `{ "steps": [...] }` from the current prompt/template output

Normalize either form into a final top-level `tour` array before assembling the graph. Each final saved tour step object MUST match this exact shape:

```json
[
  {
    "order": 1,
    "title": "Start at the app entry",
    "description": "This step explains how the frontend boots and mounts.",
    "nodeIds": ["file:src/main.tsx", "file:src/App.tsx"]
  }
]
```

Rules:
- If the intermediate output is an envelope object, unwrap its `steps` array before any other normalization
- `description` is required; do not use `whyItMatters` in the final saved tour steps
- `nodeIds` is required; do not use `nodesToInspect` in the final saved tour steps
- `nodeIds` must reference existing graph node IDs
- Preserve optional `languageLesson` when present
- Sort by `order` before saving

---

## Phase 5.5 — NORMALIZE

Before assembling the final graph:

- Unwrap legacy or prompt-shaped envelopes before field renaming:
  - `{ "layers": [...] }` -> use the contained array as the working `layers` value
  - `{ "steps": [...] }` -> use the contained array as the working `tour` value
- Convert any layer `nodes` field to `nodeIds`
- Convert any tour `nodesToInspect` field to `nodeIds`
- Convert any tour `whyItMatters` field to `description`
- If layers or tour reference file paths, map them to file node IDs using the `file:<relative-path>` convention
- Synthesize missing layer IDs as `layer:<kebab-case-name>`
- Drop unresolved layer and tour node references
- Ensure the final `layers` value is an array of `{ id, name, description, nodeIds }`
- Ensure the final `tour` value is an array of `{ order, title, description, nodeIds }`, preserving optional `languageLesson`

---

## Phase 6 — REVIEW

Assemble the full KnowledgeGraph JSON object:

```json
{
  "version": "1.0.0",
  "project": {
    "name": "<projectName>",
    "languages": ["<languages>"],
    "frameworks": ["<frameworks>"],
    "description": "<projectDescription>",
    "analyzedAt": "<ISO 8601 timestamp>",
    "gitCommitHash": "<commit hash from Phase 0>"
  },
  "nodes": [<all merged nodes from Phase 3>],
  "edges": [<all merged edges from Phase 3>],
  "layers": [<layers from Phase 4>],
  "tour": [<steps from Phase 5>]
}
```

1. Before writing the assembled graph, validate that:
   - `layers` is an array of objects with these required fields: `id`, `name`, `description`, `nodeIds`
   - `tour` is an array of objects with these required fields: `order`, `title`, `description`, `nodeIds`
   - `tour[*].languageLesson` is allowed as an optional string field
   - Every `layers[*].nodeIds` entry exists in the merged node set
   - Every `tour[*].nodeIds` entry exists in the merged node set

   If validation fails, automatically normalize and rewrite the graph into this shape before saving. If the graph still fails final validation after the normalization pass, save it with warnings but mark dashboard auto-launch as skipped.

2. Write the assembled graph to `$PROJECT_ROOT/.understand-anything/intermediate/assembled-graph.json`.

3. Dispatch a subagent using the prompt template at `./graph-reviewer-prompt.md`. Read the template file and pass the full content as the subagent's prompt, appending the following additional context:

> **Additional context from main session:**
>
> Phase 1 scan results (file inventory):
> ```json
> [list of {path, sizeLines} from scan-result.json]
> ```
>
> Phase warnings/errors accumulated during analysis:
> - [list any batch failures, skipped files, or warnings from Phases 2-5]
>
> Cross-validate: every file in the scan inventory should have a corresponding `file:` node in the graph. Flag any missing files. Also flag any graph nodes whose `filePath` doesn't appear in the scan inventory.

Pass these parameters in the dispatch prompt:

   > Validate the knowledge graph at `$PROJECT_ROOT/.understand-anything/intermediate/assembled-graph.json`.
   > Project root: `$PROJECT_ROOT`
   > Read the file and validate it for completeness and correctness.
   > Write output to: `$PROJECT_ROOT/.understand-anything/intermediate/review.json`

4. After the subagent completes, read `$PROJECT_ROOT/.understand-anything/intermediate/review.json`.

5. **If `approved: false`:**
   - Review the `issues` list
   - Apply automated fixes where possible:
     - Remove edges with dangling references
     - Fill missing required fields with sensible defaults (e.g., empty `tags` -> `["untagged"]`, empty `summary` -> `"No summary available"`)
     - Remove nodes with invalid types
   - Re-run the final graph validation after automated fixes
   - If critical issues remain after one fix attempt, save the graph anyway but include the warnings in the final report and mark dashboard auto-launch as skipped

6. **If `approved: true`:** Proceed to Phase 7.

---

## Phase 7 — SAVE

1. Write the final knowledge graph to `$PROJECT_ROOT/.understand-anything/knowledge-graph.json`.

2. Write metadata to `$PROJECT_ROOT/.understand-anything/meta.json`:
   ```json
   {
     "lastAnalyzedAt": "<ISO 8601 timestamp>",
     "gitCommitHash": "<commit hash>",
     "version": "1.0.0",
     "analyzedFiles": <number of files analyzed>
   }
   ```

3. Clean up intermediate files:
   ```bash
   rm -rf $PROJECT_ROOT/.understand-anything/intermediate
   ```

4. Report a summary to the user containing:
   - Project name and description
   - Files analyzed / total files
   - Nodes created (broken down by type: file, function, class)
   - Edges created (broken down by type)
   - Layers identified (with names)
   - Tour steps generated (count)
   - Any warnings from the reviewer
   - Path to the output file: `$PROJECT_ROOT/.understand-anything/knowledge-graph.json`

5. Only automatically launch the dashboard by invoking the `/understand-dashboard` skill if final graph validation passed after normalization/review fixes.
   If final validation did not pass, report that the graph was saved with warnings and dashboard launch was skipped.

---

## Error Handling

- If any subagent dispatch fails, retry **once** with the same prompt plus additional context about the failure.
- Track all warnings and errors from each phase in a `$PHASE_WARNINGS` list. Pass this list to the graph-reviewer in Phase 6 for comprehensive validation.
- If it fails a second time, skip that phase and continue with partial results.
- ALWAYS save partial results — a partial graph is better than no graph.
- Report any skipped phases or errors in the final summary so the user knows what happened.
- NEVER silently drop errors. Every failure must be visible in the final report.

---

## Reference: KnowledgeGraph Schema

### Node Types
| Type | Description | ID Convention |
|---|---|---|
| `file` | Source file | `file:<relative-path>` |
| `function` | Function or method | `func:<relative-path>:<name>` |
| `class` | Class, interface, or type | `class:<relative-path>:<name>` |
| `module` | Logical module or package | `module:<name>` |
| `concept` | Abstract concept or pattern | `concept:<name>` |

### Edge Types (18 total)
| Category | Types |
|---|---|
| Structural | `imports`, `exports`, `contains`, `inherits`, `implements` |
| Behavioral | `calls`, `subscribes`, `publishes`, `middleware` |
| Data flow | `reads_from`, `writes_to`, `transforms`, `validates` |
| Dependencies | `depends_on`, `tested_by`, `configures` |
| Semantic | `related`, `similar_to` |

### Edge Weight Conventions
| Edge Type | Weight |
|---|---|
| `contains` | 1.0 |
| `inherits`, `implements` | 0.9 |
| `calls`, `exports` | 0.8 |
| `imports` | 0.7 |
| `depends_on` | 0.6 |
| `tested_by` | 0.5 |
| All others | 0.5 (default) |
