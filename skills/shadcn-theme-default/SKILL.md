---
name: shadcn-theme-default
description: Enforces the default shadcn/ui Neutral theme (black/white/gray) with OKLCH CSS variables, Tailwind v4 integration, and dark mode support
user-invocable: true
---

# shadcn/ui Default Theme — Neutral (Black/White/Gray)

You are a frontend engineer responsible for applying and maintaining the default shadcn/ui Neutral theme across the project. When creating components, pages, layouts, or any visual element, you MUST use the theme tokens defined below. Never hardcode hex, RGB, or HSL values — always reference CSS variables via Tailwind utility classes.

This skill only modifies CSS and Tailwind configuration files. It never reads or modifies `.env`, `.env.local`, or credential files.

## Planning Protocol (MANDATORY — execute before ANY action)

Before modifying any styling file or component, you MUST complete this planning phase:

1. **Understand the request.** Determine what visual change is needed: new component styling, theme adjustment, dark mode fix, or full theme setup.

2. **Survey the current state.** Check: (a) `src/app/globals.css` (or equivalent) for existing CSS variables, (b) `tailwind.config.ts` or `@theme` directives for Tailwind integration, (c) `components.json` for shadcn/ui configuration, (d) whether dark mode is already configured. Do NOT read `.env` or credential files.

3. **Build an execution plan.** Write out which files will be created or modified and in what order. Theme variables must be set before component styling.

4. **Identify risks.** Flag: (a) overwriting custom theme values the user may have set, (b) breaking existing component styles by changing variable names, (c) Tailwind version incompatibility (v3 uses `hsl()`, v4 uses `oklch()`).

5. **Execute sequentially.** Apply changes in order: CSS variables first, then Tailwind config, then component updates.

6. **Summarize.** Report what changed and confirm both light and dark modes render correctly.

Do NOT skip this protocol.

---

## Theme Architecture

shadcn/ui uses CSS custom properties (variables) following a **background/foreground** naming convention:

- The **background** variable (e.g., `--primary`) is used for the element's fill/background.
- The **foreground** variable (e.g., `--primary-foreground`) is used for text/icons on top of that background.

In Tailwind, these map to:
- `bg-primary` uses `var(--primary)`
- `text-primary-foreground` uses `var(--primary-foreground)`

The color space is **OKLCH** (Oklab Lightness Chroma Hue), which is perceptually uniform and the default in shadcn/ui since Tailwind v4.

---

## Complete CSS Variables — Default Neutral Theme

### Light Mode (`:root`)

```css
:root {
  /* Border radius */
  --radius: 0.625rem;

  /* Core surfaces */
  --background: oklch(1 0 0);                      /* pure white */
  --foreground: oklch(0.145 0 0);                   /* near black */

  /* Card */
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);

  /* Popover */
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);

  /* Primary — used for main CTA buttons, links, active states */
  --primary: oklch(0.205 0 0);                      /* very dark gray / near black */
  --primary-foreground: oklch(0.985 0 0);            /* near white */

  /* Secondary — used for secondary buttons, subtle backgrounds */
  --secondary: oklch(0.97 0 0);                     /* very light gray */
  --secondary-foreground: oklch(0.205 0 0);

  /* Muted — used for disabled states, placeholder text backgrounds */
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);              /* medium gray */

  /* Accent — used for hover states, highlighted items */
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);

  /* Destructive — used for delete buttons, error states */
  --destructive: oklch(0.577 0.245 27.325);          /* red */
  --destructive-foreground: oklch(0.985 0 0);

  /* Borders and inputs */
  --border: oklch(0.922 0 0);                        /* light gray border */
  --input: oklch(0.922 0 0);                         /* input border */
  --ring: oklch(0.708 0 0);                          /* focus ring — medium gray */

  /* Chart colors (for Recharts, Chart.js, etc.) */
  --chart-1: oklch(0.646 0.222 41.116);              /* warm orange */
  --chart-2: oklch(0.6 0.118 184.704);               /* teal */
  --chart-3: oklch(0.398 0.07 227.392);              /* dark blue */
  --chart-4: oklch(0.828 0.189 84.429);              /* yellow-green */
  --chart-5: oklch(0.769 0.188 70.08);               /* golden */

  /* Sidebar */
  --sidebar: oklch(0.985 0 0);
  --sidebar-foreground: oklch(0.145 0 0);
  --sidebar-primary: oklch(0.205 0 0);
  --sidebar-primary-foreground: oklch(0.985 0 0);
  --sidebar-accent: oklch(0.97 0 0);
  --sidebar-accent-foreground: oklch(0.205 0 0);
  --sidebar-border: oklch(0.922 0 0);
  --sidebar-ring: oklch(0.708 0 0);
}
```

### Dark Mode (`.dark`)

```css
.dark {
  /* Core surfaces */
  --background: oklch(0.145 0 0);                   /* near black */
  --foreground: oklch(0.985 0 0);                    /* near white */

  /* Card */
  --card: oklch(0.205 0 0);                          /* dark gray */
  --card-foreground: oklch(0.985 0 0);

  /* Popover */
  --popover: oklch(0.269 0 0);
  --popover-foreground: oklch(0.985 0 0);

  /* Primary — inverted for dark mode */
  --primary: oklch(0.922 0 0);                       /* light gray */
  --primary-foreground: oklch(0.205 0 0);             /* dark gray */

  /* Secondary */
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);

  /* Muted */
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);

  /* Accent */
  --accent: oklch(0.371 0 0);
  --accent-foreground: oklch(0.985 0 0);

  /* Destructive */
  --destructive: oklch(0.704 0.191 22.216);
  --destructive-foreground: oklch(0.985 0 0);

  /* Borders and inputs — use alpha channel in dark mode */
  --border: oklch(1 0 0 / 10%);
  --input: oklch(1 0 0 / 15%);
  --ring: oklch(0.556 0 0);

  /* Chart colors (dark mode variants) */
  --chart-1: oklch(0.488 0.243 264.376);             /* blue-purple */
  --chart-2: oklch(0.696 0.17 162.48);               /* green-teal */
  --chart-3: oklch(0.769 0.188 70.08);               /* golden */
  --chart-4: oklch(0.627 0.265 303.9);               /* purple */
  --chart-5: oklch(0.645 0.246 16.439);              /* warm red */

  /* Sidebar */
  --sidebar: oklch(0.205 0 0);
  --sidebar-foreground: oklch(0.985 0 0);
  --sidebar-primary: oklch(0.488 0.243 264.376);
  --sidebar-primary-foreground: oklch(0.985 0 0);
  --sidebar-accent: oklch(0.269 0 0);
  --sidebar-accent-foreground: oklch(0.985 0 0);
  --sidebar-border: oklch(1 0 0 / 10%);
  --sidebar-ring: oklch(0.439 0 0);
}
```

---

## Tailwind v4 Integration

In Tailwind v4, register the CSS variables as colors using the `@theme inline` directive. Add this to your main CSS file after the variable definitions:

```css
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --color-chart-1: var(--chart-1);
  --color-chart-2: var(--chart-2);
  --color-chart-3: var(--chart-3);
  --color-chart-4: var(--chart-4);
  --color-chart-5: var(--chart-5);
  --color-sidebar: var(--sidebar);
  --color-sidebar-foreground: var(--sidebar-foreground);
  --color-sidebar-primary: var(--sidebar-primary);
  --color-sidebar-primary-foreground: var(--sidebar-primary-foreground);
  --color-sidebar-accent: var(--sidebar-accent);
  --color-sidebar-accent-foreground: var(--sidebar-accent-foreground);
  --color-sidebar-border: var(--sidebar-border);
  --color-sidebar-ring: var(--sidebar-ring);
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
}
```

### Tailwind v3 (legacy)

If the project uses Tailwind v3, the variables use HSL format instead of OKLCH. Add to `tailwind.config.ts`:

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
};
export default config;
```

---

## Dark Mode Setup

### Next.js (App Router) with next-themes

```bash
npm install next-themes
```

Create `src/components/shared/theme-provider.tsx`:

```typescript
"use client";

import { ThemeProvider as NextThemesProvider } from "next-themes";

export function ThemeProvider({ children, ...props }: React.ComponentProps<typeof NextThemesProvider>) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>;
}
```

Wrap the app in `src/app/layout.tsx`:

```typescript
import { ThemeProvider } from "@/components/shared/theme-provider";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

### Theme Toggle Component

```typescript
"use client";

import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      aria-label="Toggle theme"
    >
      <span className="sr-only">Toggle theme</span>
      {/* Sun icon for light, Moon icon for dark */}
      <svg
        className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" />
      </svg>
      <svg
        className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
      </svg>
    </Button>
  );
}
```

### Nuxt / SvelteKit / Other Frameworks

For non-Next.js frameworks, toggle the `.dark` class on the `<html>` element:

```typescript
// Generic dark mode toggle
function toggleDarkMode() {
  document.documentElement.classList.toggle("dark");
  const isDark = document.documentElement.classList.contains("dark");
  localStorage.setItem("theme", isDark ? "dark" : "light");
}

// On page load, respect user preference
function initTheme() {
  const stored = localStorage.getItem("theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  if (stored === "dark" || (!stored && prefersDark)) {
    document.documentElement.classList.add("dark");
  }
}
```

---

## Available shadcn/ui Components

The following components are available and all respect the theme tokens above. Install via `npx shadcn@latest add <component>`:

Accordion, Alert, Alert Dialog, Aspect Ratio, Avatar, Badge, Breadcrumb, Button, Button Group, Calendar, Card, Carousel, Chart, Checkbox, Collapsible, Combobox, Command, Context Menu, Data Table, Date Picker, Dialog, Drawer, Dropdown Menu, Empty, Field, Hover Card, Input, Input Group, Input OTP, Item, Kbd, Label, Menubar, Native Select, Navigation Menu, Pagination, Popover, Progress, Radio Group, Resizable, Scroll Area, Select, Separator, Sheet, Sidebar, Skeleton, Slider, Sonner, Spinner, Switch, Table, Tabs, Textarea, Toast, Toggle, Toggle Group, Tooltip, Typography.

---

## Tailwind Utility Class Reference

Use these Tailwind classes to apply theme tokens. NEVER use arbitrary values like `bg-[#000]` or `text-[#fff]`.

### Backgrounds
| Purpose | Class |
|---------|-------|
| Page background | `bg-background` |
| Card surface | `bg-card` |
| Popover surface | `bg-popover` |
| Primary fill (CTA buttons) | `bg-primary` |
| Secondary fill (secondary buttons) | `bg-secondary` |
| Muted fill (disabled, subtle) | `bg-muted` |
| Accent fill (hover, highlight) | `bg-accent` |
| Destructive fill (delete, error) | `bg-destructive` |
| Sidebar background | `bg-sidebar` |

### Text
| Purpose | Class |
|---------|-------|
| Body text | `text-foreground` |
| Text on primary bg | `text-primary-foreground` |
| Text on secondary bg | `text-secondary-foreground` |
| Muted/placeholder text | `text-muted-foreground` |
| Text on accent bg | `text-accent-foreground` |
| Text on destructive bg | `text-destructive-foreground` |
| Text on card bg | `text-card-foreground` |

### Borders
| Purpose | Class |
|---------|-------|
| Standard border | `border-border` |
| Input border | `border-input` |
| Focus ring | `ring-ring` |
| Sidebar border | `border-sidebar-border` |

### Border Radius
| Purpose | Class |
|---------|-------|
| Small radius | `rounded-sm` (calc(var(--radius) - 4px)) |
| Medium radius | `rounded-md` (calc(var(--radius) - 2px)) |
| Large radius | `rounded-lg` (var(--radius) = 0.625rem) |
| Extra large radius | `rounded-xl` (calc(var(--radius) + 4px)) |

---

## Component Styling Patterns

### Standard Button Variants

```tsx
// Primary (default) — dark bg, light text
<Button>Save changes</Button>
// Uses: bg-primary text-primary-foreground

// Secondary — light bg, dark text
<Button variant="secondary">Cancel</Button>
// Uses: bg-secondary text-secondary-foreground

// Destructive — red bg, white text
<Button variant="destructive">Delete</Button>
// Uses: bg-destructive text-destructive-foreground

// Outline — transparent bg, border
<Button variant="outline">Edit</Button>
// Uses: border-input bg-background text-foreground

// Ghost — no bg, text only
<Button variant="ghost">More</Button>
// Uses: text-foreground, hover:bg-accent hover:text-accent-foreground

// Link — text styled as link
<Button variant="link">Learn more</Button>
// Uses: text-primary underline
```

### Card Pattern

```tsx
<div className="rounded-lg border border-border bg-card p-6 text-card-foreground shadow-sm">
  <h3 className="text-lg font-semibold text-foreground">Title</h3>
  <p className="text-sm text-muted-foreground">Description text</p>
</div>
```

### Input Pattern

```tsx
<input
  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
  placeholder="Enter value..."
/>
```

### Alert/Badge Pattern

```tsx
{/* Info badge */}
<span className="inline-flex items-center rounded-md bg-secondary px-2.5 py-0.5 text-xs font-medium text-secondary-foreground">
  Active
</span>

{/* Destructive badge */}
<span className="inline-flex items-center rounded-md bg-destructive px-2.5 py-0.5 text-xs font-medium text-destructive-foreground">
  Error
</span>
```

---

## Full globals.css Template

This is the complete `globals.css` file for a project using the default Neutral theme:

```css
@import "tailwindcss";

@custom-variant dark (&:is(.dark *));

:root {
  --radius: 0.625rem;
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.97 0 0);
  --secondary-foreground: oklch(0.205 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --destructive-foreground: oklch(0.985 0 0);
  --border: oklch(0.922 0 0);
  --input: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --chart-1: oklch(0.646 0.222 41.116);
  --chart-2: oklch(0.6 0.118 184.704);
  --chart-3: oklch(0.398 0.07 227.392);
  --chart-4: oklch(0.828 0.189 84.429);
  --chart-5: oklch(0.769 0.188 70.08);
  --sidebar: oklch(0.985 0 0);
  --sidebar-foreground: oklch(0.145 0 0);
  --sidebar-primary: oklch(0.205 0 0);
  --sidebar-primary-foreground: oklch(0.985 0 0);
  --sidebar-accent: oklch(0.97 0 0);
  --sidebar-accent-foreground: oklch(0.205 0 0);
  --sidebar-border: oklch(0.922 0 0);
  --sidebar-ring: oklch(0.708 0 0);
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.269 0 0);
  --popover-foreground: oklch(0.985 0 0);
  --primary: oklch(0.922 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.371 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.704 0.191 22.216);
  --destructive-foreground: oklch(0.985 0 0);
  --border: oklch(1 0 0 / 10%);
  --input: oklch(1 0 0 / 15%);
  --ring: oklch(0.556 0 0);
  --chart-1: oklch(0.488 0.243 264.376);
  --chart-2: oklch(0.696 0.17 162.48);
  --chart-3: oklch(0.769 0.188 70.08);
  --chart-4: oklch(0.627 0.265 303.9);
  --chart-5: oklch(0.645 0.246 16.439);
  --sidebar: oklch(0.205 0 0);
  --sidebar-foreground: oklch(0.985 0 0);
  --sidebar-primary: oklch(0.488 0.243 264.376);
  --sidebar-primary-foreground: oklch(0.985 0 0);
  --sidebar-accent: oklch(0.269 0 0);
  --sidebar-accent-foreground: oklch(0.985 0 0);
  --sidebar-border: oklch(1 0 0 / 10%);
  --sidebar-ring: oklch(0.439 0 0);
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --color-chart-1: var(--chart-1);
  --color-chart-2: var(--chart-2);
  --color-chart-3: var(--chart-3);
  --color-chart-4: var(--chart-4);
  --color-chart-5: var(--chart-5);
  --color-sidebar: var(--sidebar);
  --color-sidebar-foreground: var(--sidebar-foreground);
  --color-sidebar-primary: var(--sidebar-primary);
  --color-sidebar-primary-foreground: var(--sidebar-primary-foreground);
  --color-sidebar-accent: var(--sidebar-accent);
  --color-sidebar-accent-foreground: var(--sidebar-accent-foreground);
  --color-sidebar-border: var(--sidebar-border);
  --color-sidebar-ring: var(--sidebar-ring);
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

---

## components.json (shadcn/ui config)

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "src/app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  },
  "iconLibrary": "lucide"
}
```

---

## Rules for the Agent

1. **ALWAYS use theme tokens.** Never write `bg-black`, `text-white`, `bg-gray-100`, `border-gray-200`, or any hardcoded color class. Use `bg-background`, `text-foreground`, `bg-muted`, `border-border` instead.

2. **Respect the background/foreground pairing.** If you use `bg-primary`, the text on top must be `text-primary-foreground`. Never mix pairs (e.g., never use `text-foreground` on a `bg-primary` surface).

3. **Dark mode is automatic.** The CSS variables handle the switch. Never write conditional dark mode classes like `dark:bg-gray-900` — the variables already flip values.

4. **Use the radius tokens.** Instead of `rounded-lg` with a fixed value, use the radius variables: `rounded-sm`, `rounded-md`, `rounded-lg`, `rounded-xl`.

5. **Chart colors follow the sequence.** For multi-series charts, use `chart-1` through `chart-5` in order.

6. **Sidebar uses its own token set.** When styling sidebar components, use `bg-sidebar`, `text-sidebar-foreground`, `border-sidebar-border`, etc. — not the generic tokens.

7. **Detect Tailwind version.** Before applying any theme, run this detection sequence:
   - Check `package.json` for `tailwindcss` version: `cat package.json | grep tailwindcss`
   - If version starts with `4.` → use OKLCH variables with `@theme inline` in `globals.css`
   - If version starts with `3.` → use HSL variables with `tailwind.config.ts` extension
   - If version is ambiguous, check for `@theme` directive in existing CSS files (indicates v4) or `tailwind.config.ts` with `hsl(var(--...))` patterns (indicates v3)
   - **Never mix OKLCH and HSL** — applying v4 OKLCH variables to a v3 project will break all colors

8. **Installing new components.** Use `npx shadcn@latest add <component>`. The CLI respects `components.json` and generates components with the correct theme tokens.
