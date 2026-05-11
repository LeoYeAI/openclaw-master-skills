# {{Project Name}} — Plan

<!-- ============================================================
  PLAN FILE
  ============================================================
  File name:  plans/<slug>-plan.md

  This is a freeform architecture/design document. It is NOT
  synced to SQLite. Agents read it at session start for context.
  It is the right place for:
    - High-level vision and goals
    - Architecture decisions (with rationale)
    - Phase breakdowns and milestones
    - Open questions and tradeoffs
    - Anything too long or structural for a task line

  There is no required format. The sections below are suggested
  starting points — delete or rename them freely.
  ============================================================ -->

## Vision

<!-- What is this project trying to accomplish? What does success look like?
     One paragraph. Be concrete. -->

## Architecture

<!-- How is the system structured? Key components, data flows, external dependencies.
     Diagrams (ASCII or Mermaid) welcome. -->

## Decisions

<!-- Resolved design decisions. Format: short title + rationale.
     Example:
     | # | Decision | Resolution |
     |---|---|---|
     | 1 | Auth strategy | Use OAuth2 PKCE — avoids storing client secrets server-side |
     | 2 | Storage | SQLite for local, S3 for media — keeps infra simple |
-->

## Open Questions

<!-- Unresolved questions or tradeoffs still being evaluated.
     Remove items as they are resolved (move to Decisions above).
     Example:
     - Should we paginate the feed at 20 or 50 items?
     - Redis vs. in-process cache for rate limiting?
-->

## Phases / Milestones

<!-- Optional. Break down the project into phases or milestones.
     Example:
     ### Phase 1 — MVP
     - Core sync logic
     - Basic CLI

     ### Phase 2 — Polish
     - Error handling
     - Tests
-->
