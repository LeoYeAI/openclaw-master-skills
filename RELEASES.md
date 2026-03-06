# Release Notes

每次更新的详细发布说明。

---

## v0.2.0 — 2026-03-02

### 🚀 Major Update: 126 Curated Skills

**Total skills: 126**  
**New this release: 105**


#### AI Tools (anthropics/skills + wshobson)

- `algorithmic-art` — Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration. Use this when users r
- `doc-coauthoring` — Guide users through a structured workflow for co-authoring documentation. Use when user wants to write documentation, pr
- `internal-comms` — A set of resources to help me write all kinds of internal communications, using the formats that my company likes to use
- `prompt-engineering-patterns` — Master advanced prompt engineering techniques to maximize LLM performance, reliability, and controllability in productio
- `rag-implementation` — Build Retrieval-Augmented Generation (RAG) systems for LLM applications with vector databases and semantic search. Use w
- `slack-gif-creator` — Knowledge and utilities for creating animated GIFs optimized for Slack. Provides constraints, validation tools, and anim
- `theme-factory` — Toolkit for styling artifacts with a theme. These artifacts can be slides, docs, reportings, HTML landing pages, etc. Th
- `web-artifacts-builder` — Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (

#### Productivity (obra/superpowers + obra/episodic-memory)

- `dispatching-parallel-agents` — Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies
- `finishing-a-development-branch` — Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completio
- `receiving-code-review` — Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or techni
- `remembering-conversations` — Use when user asks 'how should I...' or 'what's the best approach...' after exploring code, OR when you've tried to solv
- `requesting-code-review` — Use when completing tasks, implementing major features, or before merging to verify work meets requirements
- `subagent-driven-development` — Use when executing implementation plans with independent tasks in the current session
- `using-git-worktrees` — Use when starting feature work that needs isolation from current workspace or before executing implementation plans - cr
- `using-superpowers` — Use when starting any conversation - establishes how to find and use skills, requiring Skill tool invocation before ANY 
- `verification-before-completion` — Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verifi
- `writing-skills` — Use when creating new skills, editing existing skills, or verifying skills work before deployment

#### Marketing (coreyhaines31/marketingskills)

- `ab-test-setup` — When the user wants to plan, design, or implement an A/B test or experiment. Also use when the user mentions "A/B test,"
- `analytics-tracking` — When the user wants to set up, improve, or audit analytics tracking and measurement. Also use when the user mentions "se
- `competitor-alternatives` — When the user wants to create competitor comparison or alternative pages for SEO and sales enablement. Also use when the
- `copy-editing` — When the user wants to edit, review, or improve existing marketing copy. Also use when the user mentions 'edit this copy
- `email-sequence` — When the user wants to create or optimize an email sequence, drip campaign, automated email flow, or lifecycle email pro
- `form-cro` — When the user wants to optimize any form that is NOT signup/registration — including lead capture forms, contact forms, 
- `free-tool-strategy` — When the user wants to plan, evaluate, or build a free tool for marketing purposes — lead generation, SEO value, or bran
- `launch-strategy` — When the user wants to plan a product launch, feature announcement, or release strategy. Also use when the user mentions
- `marketing-ideas` — When the user needs marketing ideas, inspiration, or strategies for their SaaS or software product. Also use when the us
- `marketing-psychology` — When the user wants to apply psychological principles, mental models, or behavioral science to marketing. Also use when 
- `onboarding-cro` — When the user wants to optimize post-signup onboarding, user activation, first-run experience, or time-to-value. Also us
- `page-cro` — When the user wants to optimize, improve, or increase conversions on any marketing page — including homepage, landing pa
- `paid-ads` — When the user wants help with paid advertising campaigns on Google Ads, Meta (Facebook/Instagram), LinkedIn, Twitter/X, 
- `popup-cro` — When the user wants to create or optimize popups, modals, overlays, slide-ins, or banners for conversion purposes. Also 
- `pricing-strategy` — When the user wants help with pricing decisions, packaging, or monetization strategy. Also use when the user mentions 'p
- `product-marketing-context` — When the user wants to create or update their product marketing context document. Also use when the user mentions 'produ
- `programmatic-seo` — When the user wants to create SEO-driven pages at scale using templates and data. Also use when the user mentions "progr
- `referral-program` — When the user wants to create, optimize, or analyze a referral program, affiliate program, or word-of-mouth strategy. Al
- `signup-flow-cro` — When the user wants to optimize signup, registration, account creation, or trial activation flows. Also use when the use
- `social-content` — When the user wants help creating, scheduling, or optimizing social media content for LinkedIn, Twitter/X, Instagram, Ti

#### Frontend (vercel/antfu/hyf0/wshobson)

- `next-best-practices` — Next.js best practices - file conventions, RSC boundaries, data patterns, async APIs, metadata, error handling, route ha
- `next-cache-components` — Next.js 16 Cache Components - PPR, use cache directive, cacheLife, cacheTag, updateTag
- `nextjs-app-router-patterns` — Master Next.js 14+ App Router with Server Components, streaming, parallel routes, and advanced data fetching. Use when b
- `nuxt` — Nuxt full-stack Vue framework with SSR, auto-imports, and file-based routing. Use when working with Nuxt apps, server ro
- `pinia` — Pinia official Vue state management library, type-safe and extensible. Use when defining stores, working with state/gett
- `pnpm` — Node.js package manager with strict dependency resolution. Use when running pnpm specific commands, configuring workspac
- `react-state-management` — Master modern React state management with Redux Toolkit, Zustand, Jotai, and React Query. Use when setting up global sta
- `responsive-design` — Implement modern responsive layouts using container queries, fluid typography, CSS Grid, and mobile-first breakpoint str
- `slidev` — Create and present web-based slides for developers using Markdown, Vue components, code highlighting, animations, and in
- `turborepo` — name: turborepo
- `unocss` — UnoCSS instant atomic CSS engine, superset of Tailwind CSS. Use when configuring UnoCSS, writing utility rules, shortcut
- `vercel-ai-sdk` — Answer questions about the AI SDK and help build AI-powered features. Use when developers: (1) Ask about AI SDK function
- `vercel-composition-patterns` — React composition patterns that scale. Use when refactoring components with
- `vite` — Vite build tool configuration, plugin API, SSR, and Vite 8 Rolldown migration. Use when working with Vite projects, vite
- `vitepress` — VitePress static site generator powered by Vite and Vue. Use when building documentation sites, configuring themes, or w
- `vitest` — Vitest fast unit testing framework powered by Vite with Jest-compatible API. Use when writing tests, mocking, configurin
- `vue` — Vue 3 Composition API, script setup macros, reactivity system, and built-in components. Use when writing Vue SFCs, defin
- `vue-best-practices` — MUST be used for Vue.js tasks. Strongly recommends Composition API with `<script setup>` and TypeScript as the standard 
- `vue-best-practices-hyf0` — MUST be used for Vue.js tasks. Strongly recommends Composition API with `<script setup>` and TypeScript as the standard 
- `vue-debug-guides` — Vue 3 debugging and error handling for runtime errors, warnings, async failures, and SSR/hydration issues. Use when diag
- `vue-jsx-best-practices` — JSX syntax in Vue (e.g., class vs className, JSX plugin config).
- `vue-pinia-best-practices` — Pinia stores, state management patterns, store setup, and reactivity with stores.
- `vue-router-best-practices` — Vue Router 4 patterns, navigation guards, route params, and route-component lifecycle interactions.
- `vue-router-best-practices-hyf0` — Vue Router 4 patterns, navigation guards, route params, and route-component lifecycle interactions.
- `vue-testing-best-practices` — Use for Vue.js testing. Covers Vitest, Vue Test Utils, component testing, mocking, testing patterns, and Playwright for 
- `vue-testing-best-practices-hyf0` — Use for Vue.js testing. Covers Vitest, Vue Test Utils, component testing, mocking, testing patterns, and Playwright for 
- `web-component-design` — Master React, Vue, and Svelte component patterns including CSS-in-JS, composition strategies, and reusable component arc

#### Mobile (expo/callstackincubator)

- `expo-api-routes` — Guidelines for creating API routes in Expo Router with EAS Hosting
- `expo-building-native-ui` — Complete guide for building beautiful apps with Expo Router. Covers fundamentals, styling, components, navigation, anima
- `expo-cicd-workflows` — Helps understand and write EAS workflow YAML files for Expo projects. Use this skill when the user asks about CI/CD or w
- `expo-deployment` — Deploying Expo apps to iOS App Store, Android Play Store, web hosting, and API routes
- `expo-dev-client` — Build and distribute Expo development clients locally or via TestFlight
- `expo-native-data-fetching` — Use when implementing or debugging ANY network request, API call, or data fetching. Covers fetch API, React Query, SWR, 
- `expo-tailwind-setup` — Set up Tailwind CSS v4 in Expo with react-native-css and NativeWind v5 for universal styling
- `expo-ui-jetpack-compose` — `@expo/ui/jetpack-compose` package lets you use Jetpack Compose Views and modifiers in your app.
- `expo-ui-swift-ui` — `@expo/ui/swift-ui` package lets you use SwiftUI Views and modifiers in your app.
- `expo-use-dom` — Use Expo DOM components to run web code in a webview on native and as-is on web. Migrate web code to native incrementall
- `react-native-best-practices` — Provides React Native performance optimization guidelines for FPS, TTI, bundle size, memory leaks, re-renders, and anima
- `upgrading-expo` — Guidelines for upgrading Expo SDK versions and fixing dependency issues
- `upgrading-react-native` — Upgrades React Native apps to newer versions by applying rn-diff-purge template diffs, updating package.json dependencie

#### Backend (wshobson/agents)

- `api-design-principles` — Master REST and GraphQL API design principles to build intuitive, scalable, and maintainable APIs that delight developer
- `architecture-patterns` — Implement proven backend architecture patterns including Clean Architecture, Hexagonal Architecture, and Domain-Driven D
- `microservices-patterns` — Design microservices architectures with service boundaries, event-driven communication, and resilience patterns. Use whe
- `modern-javascript-patterns` — Master ES6+ features including async/await, destructuring, spread operators, arrow functions, promises, modules, iterato
- `nodejs-backend-patterns` — Build production-ready Node.js backend services with Express/Fastify, implementing middleware patterns, error handling, 
- `python-design-patterns` — Python design patterns including KISS, Separation of Concerns, Single Responsibility, and composition over inheritance. 
- `python-performance-optimization` — Profile and optimize Python code using cProfile, memory profilers, and performance best practices. Use when debugging sl
- `python-testing-patterns` — Implement comprehensive testing strategies with pytest, fixtures, mocking, and test-driven development. Use when writing
- `typescript-advanced-types` — Master TypeScript's advanced type system including generics, conditional types, mapped types, template literals, and uti

#### Database (wshobson/agents)

- `postgresql-table-design` — Design a PostgreSQL-specific schema. Covers best-practices, data types, indexing, constraints, performance patterns, and

#### Auth (better-auth/skills)

- `better-auth-best-practices` — Skill for integrating Better Auth - the comprehensive TypeScript authentication framework.
- `create-auth-skill` — Skill for creating auth layers in TypeScript/JavaScript apps using Better Auth.

#### DevOps (github/awesome-copilot)

- `add-educational-comments` — Add educational comments to the file specified, or prompt asking for file to comment if one is not provided.
- `agent-governance` — name: agent-governance
- `agentic-eval` — name: agentic-eval
- `ai-prompt-engineering-safety-review` — Comprehensive AI prompt engineering safety review and improvement prompt. Analyzes prompts for safety, bias, security vu
- `apple-appstore-reviewer` — Serves as a reviewer of the codebase with instructions on looking for Apple App Store optimizations or rejection reasons
- `architecture-blueprint-generator` — Comprehensive project architecture blueprint generator that analyzes codebases to create detailed architectural document
- `boost-prompt` — Interactive prompt refinement workflow: interrogates scope, deliverables, constraints; copies final markdown to clipboar
- `breakdown-feature-implementation` — Prompt for creating detailed feature implementation plans, following Epoch monorepo structure.
- `chrome-devtools` — Expert-level browser automation, debugging, and performance analysis using Chrome DevTools MCP. Use for interacting with
- `code-exemplars-blueprint-generator` — Technology-agnostic prompt generator that creates customizable AI prompts for scanning codebases and identifying high-qu
- `git-commit` — Execute git commit with conventional commit message analysis, intelligent staging, and message generation. Use when user

#### Web Automation (firecrawl/browser-use/squirrelscan)

- `audit-website` — Audit websites for SEO, performance, security, technical, content, and 15 other issue cateories with 230+ rules using th
- `browser-use` — Automates browser interactions for web testing, form filling, screenshots, and data extraction. Use when the user needs 
- `firecrawl` — name: firecrawl

#### Other (various)

- `react-doctor` — Run after making React changes to catch issues early. Use when reviewing code, finishing a feature, or fixing bugs in a 

---

## v0.1.0 — 2026-03-02

### 🎉 Initial Release

**Total skills: 21**

- `openclaw-guardian` — Deploy and manage a Guardian watchdog process for OpenClaw Gateway. Provides automated health monitoring, self-repair vi
- `pdf` — Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables fr
- `docx` — Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files). Triggers inclu
- `xlsx` — Use this skill any time a spreadsheet file is the primary input or output. This means any task where the user wants to: 
- `pptx` — Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide d
- `skill-creator` — Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a sk
- `brand-guidelines` — Applies Anthropic's official brand colors and typography to any sort of artifact that may benefit from having Anthropic'
- `webapp-testing` — Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functional
- `canvas-design` — Create beautiful visual art in .png and .pdf documents using design philosophy. You should use this skill when the user 
- `mcp-builder` — Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services
- `brainstorming` — You MUST use this before any creative work - creating features, building components, adding functionality, or modifying 
- `systematic-debugging` — Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
- `test-driven-development` — Use when implementing any feature or bugfix, before writing implementation code
- `writing-plans` — Use when you have a spec or requirements for a multi-step task, before touching code
- `executing-plans` — Use when you have a written implementation plan to execute in a separate session with review checkpoints
- `seo-audit` — When the user wants to audit, review, or diagnose SEO issues on their site. Also use when the user mentions "SEO audit,"
- `copywriting` — When the user wants to write, rewrite, or improve marketing copy for any page — including homepage, landing pages, prici
- `content-strategy` — When the user wants to plan a content strategy, decide what content to create, or figure out what topics to cover. Also 
- `vercel-react-best-practices` — React and Next.js performance optimization guidelines from Vercel Engineering. This skill should be used when writing, r
- `web-design-guidelines` — Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit 
- `supabase-postgres-best-practices` — Postgres performance optimization and best practices from Supabase. Use this skill when writing, reviewing, or optimizin
