---
name: json-render-generative-ui
description: Generative UI framework that renders AI-generated JSON specs into type-safe UI components across React, Vue, Svelte, Solid, React Native, video, PDF, and email.
triggers:
  - use json-render to generate UI
  - render AI-generated components with json-render
  - generative UI with json-render
  - create a json-render catalog
  - stream AI UI with json-render
  - json-render shadcn components
  - build dynamic UI from AI prompts
  - json-render react renderer setup
---

# json-render Generative UI Framework

> Skill by [ara.so](https://ara.so) — Daily 2026 Skills collection.

json-render is a **Generative UI framework** that lets AI generate dynamic interfaces from natural language prompts, constrained to a predefined component catalog. AI outputs JSON; json-render renders it safely and predictably across any platform.

## Installation

```bash
# React (core)
npm install @json-render/core @json-render/react

# React + shadcn/ui (36 pre-built components)
npm install @json-render/shadcn

# React Native
npm install @json-render/core @json-render/react-native

# Vue
npm install @json-render/core @json-render/vue

# Svelte
npm install @json-render/core @json-render/svelte

# SolidJS
npm install @json-render/core @json-render/solid

# Video (Remotion)
npm install @json-render/core @json-render/remotion

# PDF
npm install @json-render/core @json-render/react-pdf

# Email
npm install @json-render/core @json-render/react-email @react-email/components @react-email/render

# 3D (React Three Fiber)
npm install @json-render/core @json-render/react-three-fiber @react-three/fiber @react-three/drei three

# OG Images / SVG / PNG
npm install @json-render/core @json-render/image

# State management adapters
npm install @json-render/zustand   # or redux, jotai, xstate

# MCP integration (Claude, ChatGPT, Cursor)
npm install @json-render/mcp

# YAML wire format
npm install @json-render/yaml
```

## Core Concepts

| Concept | Description |
|---|---|
| **Catalog** | Defines allowed components and actions (the guardrails for AI) |
| **Spec** | AI-generated JSON describing which components to render and with what props |
| **Registry** | Maps catalog component names to actual render implementations |
| **Renderer** | Platform-specific component that takes a spec + registry and renders UI |
| **Actions** | Named events AI can trigger (e.g. `export_report`, `refresh_data`) |

## Spec Format

The flat spec format uses a root key + elements map:

```typescript
const spec = {
  root: "card-1",
  elements: {
    "card-1": {
      type: "Card",
      props: { title: "Dashboard" },
      children: ["metric-1", "metric-2", "button-1"],
    },
    "metric-1": {
      type: "Metric",
      props: { label: "Revenue", value: "124000", format: "currency" },
      children: [],
    },
    "metric-2": {
      type: "Metric",
      props: { label: "Growth", value: "0.18", format: "percent" },
      children: [],
    },
    "button-1": {
      type: "Button",
      props: { label: "Export Report", action: "export_report" },
      children: [],
    },
  },
};
```

## Step 1: Define a Catalog

```typescript
import { defineCatalog } from "@json-render/core";
import { schema } from "@json-render/react/schema";
import { z } from "zod";

const catalog = defineCatalog(schema, {
  components: {
    Card: {
      props: z.object({ title: z.string() }),
      description: "A card container with a title",
    },
    Metric: {
      props: z.object({
        label: z.string(),
        value: z.string(),
        format: z.enum(["currency", "percent", "number"]).nullable(),
      }),
      description: "Displays a single metric value with optional formatting",
    },
    Button: {
      props: z.object({
        label: z.string(),
        action: z.string(),
      }),
      description: "Clickable button that triggers an action",
    },
    Stack: {
      props: z.object({
        direction: z.enum(["row", "column"]).default("column"),
        gap: z.number().optional(),
      }),
      description: "Layout container that stacks children",
    },
  },
  actions: {
    export_report: { description: "Export the current dashboard to PDF" },
    refresh_data: { description: "Refresh all metric data" },
    navigate: {
      description: "Navigate to a page",
      payload: z.object({ path: z.string() }),
    },
  },
});
```

## Step 2: Define a Registry (React)

```tsx
import { defineRegistry, Renderer } from "@json-render/react";

function format(value: string, fmt: string | null): string {
  if (fmt === "currency") return `$${Number(value).toLocaleString()}`;
  if (fmt === "percent") return `${(Number(value) * 100).toFixed(1)}%`;
  return value;
}

const { registry } = defineRegistry(catalog, {
  components: {
    Card: ({ props, children }) => (
      <div className="rounded-lg border p-4 shadow-sm">
        <h3 className="text-lg font-semibold mb-3">{props.title}</h3>
        {children}
      </div>
    ),

    Metric: ({ props }) => (
      <div className="flex flex-col">
        <span className="text-sm text-gray-500">{props.label}</span>
        <span className="text-2xl font-bold">
          {format(props.value, props.format)}
        </span>
      </div>
    ),

    Button: ({ props, emit }) => (
      <button
        className="px-4 py-2 bg-blue-600 text-white rounded"
        onClick={() => emit("press")}
      >
        {props.label}
      </button>
    ),

    Stack: ({ props, children }) => (
      <div
        style={{
          display: "flex",
          flexDirection: props.direction ?? "column",
          gap: props.gap ?? 8,
        }}
      >
        {children}
      </div>
    ),
  },
});
```

## Step 3: Render the Spec

```tsx
import { Renderer } from "@json-render/react";

function Dashboard({ spec, onAction }) {
  return (
    <Renderer
      spec={spec}
      registry={registry}
      onAction={(action, payload) => {
        console.log("Action triggered:", action, payload);
        onAction?.(action, payload);
      }}
    />
  );
}
```

## Generating Specs with AI (Vercel AI SDK)

```typescript
import { generateObject } from "ai";
import { openai } from "@ai-sdk/openai";
import { getCatalogSchema, getCatalogPrompt } from "@json-render/core";

async function generateDashboard(userPrompt: string) {
  const { object: spec } = await generateObject({
    model: openai("gpt-4o"),
    schema: getCatalogSchema(catalog),
    system: getCatalogPrompt(catalog),
    prompt: userPrompt,
  });

  return spec;
}

// Usage
const spec = await generateDashboard(
  "Create a sales dashboard showing revenue, conversion rate, and an export button"
);
```

## Streaming Specs

```tsx
import { streamObject } from "ai";
import { openai } from "@ai-sdk/openai";
import { getCatalogSchema, getCatalogPrompt, parseSpecStream } from "@json-render/core";
import { Renderer } from "@json-render/react";
import { useState, useEffect } from "react";

function StreamingDashboard({ prompt }: { prompt: string }) {
  const [spec, setSpec] = useState(null);

  useEffect(() => {
    async function stream() {
      const { partialObjectStream } = await streamObject({
        model: openai("gpt-4o"),
        schema: getCatalogSchema(catalog),
        system: getCatalogPrompt(catalog),
        prompt,
      });

      for await (const partial of partialObjectStream) {
        setSpec(partial); // Renderer handles partial specs gracefully
      }
    }
    stream();
  }, [prompt]);

  if (!spec) return <div>Generating UI...</div>;
  return <Renderer spec={spec} registry={registry} />;
}
```

## Using Pre-built shadcn/ui Components

```tsx
import { defineCatalog } from "@json-render/core";
import { schema } from "@json-render/react/schema";
import { defineRegistry, Renderer } from "@json-render/react";
import { shadcnComponentDefinitions } from "@json-render/shadcn/catalog";
import { shadcnComponents } from "@json-render/shadcn";

// Pick any of the 36 available shadcn components
const catalog = defineCatalog(schema, {
  components: {
    Card: shadcnComponentDefinitions.Card,
    Stack: shadcnComponentDefinitions.Stack,
    Heading: shadcnComponentDefinitions.Heading,
    Text: shadcnComponentDefinitions.Text,
    Button: shadcnComponentDefinitions.Button,
    Badge: shadcnComponentDefinitions.Badge,
    Table: shadcnComponentDefinitions.Table,
    Chart: shadcnComponentDefinitions.Chart,
    Input: shadcnComponentDefinitions.Input,
    Select: shadcnComponentDefinitions.Select,
  },
  actions: {
    submit: { description: "Submit a form" },
    export: { description: "Export data" },
  },
});

const { registry } = defineRegistry(catalog, {
  components: {
    Card: shadcnComponents.Card,
    Stack: shadcnComponents.Stack,
    Heading: shadcnComponents.Heading,
    Text: shadcnComponents.Text,
    Button: shadcnComponents.Button,
    Badge: shadcnComponents.Badge,
    Table: shadcnComponents.Table,
    Chart: shadcnComponents.Chart,
    Input: shadcnComponents.Input,
    Select: shadcnComponents.Select,
  },
});

function AIPage({ spec }) {
  return <Renderer spec={spec} registry={registry} />;
}
```

## Vue Renderer

```typescript
import { h, defineComponent } from "vue";
import { defineCatalog } from "@json-render/core";
import { schema } from "@json-render/vue/schema";
import { defineRegistry, Renderer } from "@json-render/vue";
import { z } from "zod";

const catalog = defineCatalog(schema, {
  components: {
    Card: {
      props: z.object({ title: z.string() }),
      description: "Card container",
    },
    Button: {
      props: z.object({ label: z.string() }),
      description: "Button",
    },
  },
  actions: {
    click: { description: "Button clicked" },
  },
});

const { registry } = defineRegistry(catalog, {
  components: {
    Card: ({ props, children }) =>
      h("div", { class: "card" }, [
        h("h3", null, props.title),
        children,
      ]),
    Button: ({ props, emit }) =>
      h("button", { onClick: () => emit("click") }, props.label),
  },
});

// In your Vue SFC:
// <template>
//   <Renderer :spec="spec" :registry="registry" />
// </template>
```

## React Native Renderer

```tsx
import { defineCatalog } from "@json-render/core";
import { schema } from "@json-render/react-native/schema";
import {
  standardComponentDefinitions,
  standardActionDefinitions,
} from "@json-render/react-native/catalog";
import { defineRegistry, Renderer } from "@json-render/react-native";

// 25+ standard mobile components out of the box
const catalog = defineCatalog(schema, {
  components: { ...standardComponentDefinitions },
  actions: standardActionDefinitions,
});

const { registry } = defineRegistry(catalog, {
  components: {}, // use all standard implementations
});

export function AIScreen({ spec }) {
  return <Renderer spec={spec} registry={registry} />;
}
```

## PDF Generation

```typescript
import { renderToBuffer } from "@json-render/react-pdf";

const invoiceSpec = {
  root: "doc",
  elements: {
    doc: {
      type: "Document",
      props: { title: "Invoice #1234" },
      children: ["page-1"],
    },
    "page-1": {
      type: "Page",
      props: { size: "A4" },
      children: ["heading-1", "table-1"],
    },
    "heading-1": {
      type: "Heading",
      props: { text: "Invoice #1234", level: "h1" },
      children: [],
    },
    "table-1": {
      type: "Table",
      props: {
        columns: [
          { header: "Item", width: "60%" },
          { header: "Amount", width: "40%", align: "right" },
        ],
        rows: [
          ["Widget A", "$10.00"],
          ["Widget B", "$25.00"],
          ["Total", "$35.00"],
        ],
      },
      children: [],
    },
  },
};

// Returns a Buffer you can send as a response
const buffer = await renderToBuffer(invoiceSpec);

// In a Next.js route handler:
export async function GET() {
  const buffer = await renderToBuffer(invoiceSpec);
  return new Response(buffer, {
    headers: { "Content-Type": "application/pdf" },
  });
}
```

## Email Generation

```typescript
import { renderToHtml } from "@json-render/react-email";
import { schema, standardComponentDefinitions } from "@json-render/react-email";
import { defineCatalog } from "@json-render/core";

const catalog = defineCatalog(schema, {
  components: standardComponentDefinitions,
});

const emailSpec = {
  root: "html-1",
  elements: {
    "html-1": {
      type: "Html",
      props: { lang: "en" },
      children: ["head-1", "body-1"],
    },
    "head-1": { type: "Head", props: {}, children: [] },
    "body-1": {
      type: "Body",
      props: { style: { backgroundColor: "#f6f9fc" } },
      children: ["container-1"],
    },
    "container-1": {
      type: "Container",
      props: { style: { maxWidth: "600px", margin: "0 auto" } },
      children: ["heading-1", "text-1", "button-1"],
    },
    "heading-1": {
      type: "Heading",
      props: { text: "Welcome aboard!" },
      children: [],
    },
    "text-1": {
      type: "Text",
      props: { text: "Thanks for signing up. Click below to get started." },
      children: [],
    },
    "button-1": {
      type: "Button",
      props: { text: "Get Started", href: "https://example.com" },
      children: [],
    },
  },
};

const html = await renderToHtml(emailSpec);
```

## MCP Integration (Claude, ChatGPT, Cursor)

```typescript
import { createMCPServer } from "@json-render/mcp";

const server = createMCPServer({
  catalog,
  name: "my-ui-server",
  version: "1.0.0",
});

server.start();
```

## State Management Integration

```typescript
import { create } from "zustand";
import { createZustandAdapter } from "@json-render/zustand";

const useStore = create((set) => ({
  data: {},
  setData: (data) => set({ data }),
}));

const stateStore = createZustandAdapter(useStore);

// Pass to Renderer for action handling with state
<Renderer spec={spec} registry={registry} stateStore={stateStore} />;
```

## YAML Wire Format

```typescript
import { parseYAML, toYAML } from "@json-render/yaml";

// AI can output YAML instead of JSON (often more token-efficient)
const yamlSpec = `
root: card-1
elements:
  card-1:
    type: Card
    props:
      title: Hello World
    children: [button-1]
  button-1:
    type: Button
    props:
      label: Click Me
    children: []
`;

const spec = parseYAML(yamlSpec);
```

## Full Next.js App Router Example

```tsx
// app/dashboard/page.tsx
import { generateObject } from "ai";
import { openai } from "@ai-sdk/openai";
import { getCatalogSchema, getCatalogPrompt } from "@json-render/core";
import { DashboardRenderer } from "./DashboardRenderer";
import { catalog } from "@/lib/catalog";

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: { q?: string };
}) {
  const prompt = searchParams.q ?? "Show me a sales overview dashboard";

  const { object: spec } = await generateObject({
    model: openai("gpt-4o"),
    schema: getCatalogSchema(catalog),
    system: getCatalogPrompt(catalog),
    prompt,
  });

  return <DashboardRenderer spec={spec} />;
}
```

```tsx
// app/dashboard/DashboardRenderer.tsx
"use client";
import { Renderer } from "@json-render/react";
import { registry } from "@/lib/registry";
import { useRouter } from "next/navigation";

export function DashboardRenderer({ spec }) {
  const router = useRouter();

  return (
    <Renderer
      spec={spec}
      registry={registry}
      onAction={(action, payload) => {
        switch (action) {
          case "navigate":
            router.push(payload.path);
            break;
          case "export_report":
            window.open("/api/export", "_blank");
            break;
          case "refresh_data":
            router.refresh();
            break;
        }
      }}
    />
  );
}
```

## Common Patterns

### Conditional Component Availability

```typescript
// Restrict catalog based on user role
function getCatalogForRole(role: "admin" | "viewer") {
  const base = { Card, Stack, Heading, Text, Metric };
  const adminOnly = role === "admin" ? { Button, Form, Table } : {};
  const adminActions = role === "admin"
    ? { export: { description: "Export data" } }
    : {};

  return defineCatalog(schema, {
    components: { ...base, ...adminOnly },
    actions: adminOnly ? adminActions : {},
  });
}
```

### Dynamic Props with Runtime Data

```tsx
// Components can fetch their own data
const { registry } = defineRegistry(catalog, {
  components: {
    LiveMetric: ({ props }) => {
      const { data } = useSWR(`/api/metrics/${props.metricId}`);
      return (
        <div>
          <span>{props.label}</span>
          <span>{data?.value ?? "..."}</span>
        </div>
      );
    },
  },
});
```

### Type-Safe Action Handling

```typescript
import { type ActionHandler } from "@json-render/core";

const handleAction: ActionHandler<typeof catalog> = (action, payload) => {
  // action and payload are fully typed based on your catalog definition
  if (action === "navigate") {
    router.push(payload.path); // payload.path is typed as string
  }
};
```

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| AI generates unknown component type | Component not in catalog | Add component to `defineCatalog` or update AI prompt |
| Props validation error | AI hallucinated a prop | Tighten Zod schema, add `.strict()` or `.describe()` hints |
| Renderer shows nothing | `root` key doesn't match an `elements` key | Check spec structure; root must reference a valid element ID |
| Partial spec renders incorrectly | Streaming not handled | Use `parseSpecStream` utility or check for null elements before render |
| Actions not firing | `onAction` not passed to `Renderer` | Pass `onAction` prop to `<Renderer>` |
| shadcn components unstyled | Missing Tailwind config | Ensure `@json-render/shadcn` paths are in `tailwind.config.js` content array |
| TypeScript errors in registry | Catalog/registry mismatch | Ensure `defineRegistry(catalog, ...)` uses the same `catalog` instance |

## Environment Variables

```bash
# For AI generation (use your preferred provider)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# For MCP server
MCP_SERVER_PORT=3001
```

## Key API Reference

```typescript
// Core
defineCatalog(schema, { components, actions })  // Define guardrails
getCatalogSchema(catalog)                        // Get Zod schema for AI
getCatalogPrompt(catalog)                        // Get system prompt for AI

// React
defineRegistry(catalog, { components })          // Create typed registry
<Renderer spec={spec} registry={registry} onAction={fn} />

// Core utilities
parseSpecStream(stream)    // Parse streaming partial specs
toYAML(spec)              // Convert spec to YAML
parseYAML(yaml)           // Parse YAML spec to JSON

// PDF
renderToBuffer(spec)       // → Buffer
renderToStream(spec)       // → ReadableStream

// Email
renderToHtml(spec)         // → HTML string
renderToText(spec)         // → plain text string
```
