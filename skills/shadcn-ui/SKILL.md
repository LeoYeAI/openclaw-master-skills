---
name: shadcn-ui
version: 1.0.0
description: Use when building UI with shadcn/ui components, Tailwind CSS layouts, form patterns with react-hook-form and zod, theming, dark mode, sidebar layouts, mobile navigation, or any shadcn component question.
triggers:
  - shadcn
  - shadcn/ui
  - radix
  - component library
  - UI components
  - form pattern
  - react-hook-form
  - dark mode
  - theming
  - sidebar layout
  - dialog
  - sheet
  - toast
  - dropdown menu
  - command palette
  - data table
role: specialist
scope: implementation
output-format: code
---

# shadcn/ui Expert

Comprehensive guide for building production UIs with shadcn/ui, Tailwind CSS, react-hook-form, and zod.

## Core Concepts

shadcn/ui is **not** a component library — it's a collection of copy-paste components built on Radix UI primitives. You own the code. Components are added to your project, not installed as dependencies.

## Installation

```bash
# Initialize shadcn/ui in a Next.js project
npx shadcn@latest init

# Add individual components
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add dialog
npx shadcn@latest add form
npx shadcn@latest add input
npx shadcn@latest add select
npx shadcn@latest add table
npx shadcn@latest add toast
npx shadcn@latest add dropdown-menu
npx shadcn@latest add sheet
npx shadcn@latest add tabs
npx shadcn@latest add sidebar

# Add multiple at once
npx shadcn@latest add button card input label textarea select checkbox
```

---

## Component Categories & When to Use

### Layout & Navigation
| Component | Use When |
|-----------|----------|
| `sidebar` | App-level navigation with collapsible sections |
| `navigation-menu` | Top-level site navigation with dropdowns |
| `breadcrumb` | Showing page hierarchy/location |
| `tabs` | Switching between related views in same context |
| `separator` | Visual divider between content sections |
| `sheet` | Slide-out panel (mobile nav, filters, detail views) |
| `resizable` | Adjustable panel layouts |

### Forms & Input
| Component | Use When |
|-----------|----------|
| `form` | Any form with validation (wraps react-hook-form) |
| `input` | Text, email, password, number inputs |
| `textarea` | Multi-line text input |
| `select` | Choosing from a list (native-like) |
| `combobox` | Searchable select (uses `command` + `popover`) |
| `checkbox` | Boolean or multi-select toggles |
| `radio-group` | Single selection from small set |
| `switch` | On/off toggle (settings, preferences) |
| `slider` | Numeric range selection |
| `date-picker` | Date selection (uses `calendar` + `popover`) |
| `toggle` | Pressed/unpressed state (toolbar buttons) |

### Feedback & Overlay
| Component | Use When |
|-----------|----------|
| `dialog` | Modal confirmation, forms, or detail views |
| `alert-dialog` | Destructive action confirmation ("Are you sure?") |
| `sheet` | Side panel for forms, filters, mobile nav |
| `toast` | Brief non-blocking notifications (via `sonner`) |
| `alert` | Inline status messages (info, warning, error) |
| `tooltip` | Hover hints for icons/buttons |
| `popover` | Rich content on click (color pickers, date pickers) |
| `hover-card` | Preview content on hover (user profiles, links) |
| `skeleton` | Loading placeholders |
| `progress` | Task completion indicators |

### Data Display
| Component | Use When |
|-----------|----------|
| `table` | Tabular data display |
| `data-table` | Tables with sorting, filtering, pagination (uses `@tanstack/react-table`) |
| `card` | Content containers with header, body, footer |
| `badge` | Status labels, tags, counts |
| `avatar` | User profile images |
| `accordion` | Collapsible FAQ or settings sections |
| `carousel` | Image/content slideshows |
| `scroll-area` | Custom scrollable containers |

### Actions
| Component | Use When |
|-----------|----------|
| `button` | Primary actions, form submissions |
| `dropdown-menu` | Context menus, action menus |
| `context-menu` | Right-click menus |
| `menubar` | Application menu bars |
| `command` | Command palette / search (⌘K) |

---

## Form Patterns (react-hook-form + zod)

### Complete Form Example

```bash
npx shadcn@latest add form input select textarea checkbox button
```

```tsx
'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { toast } from 'sonner'

const formSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  role: z.enum(['admin', 'user', 'editor'], { required_error: 'Select a role' }),
  bio: z.string().max(500).optional(),
  notifications: z.boolean().default(false),
})

type FormValues = z.infer<typeof formSchema>

export function UserForm() {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      email: '',
      bio: '',
      notifications: false,
    },
  })

  async function onSubmit(values: FormValues) {
    try {
      await createUser(values)
      toast.success('User created successfully')
      form.reset()
    } catch (error) {
      toast.error('Failed to create user')
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name</FormLabel>
              <FormControl>
                <Input placeholder="John Doe" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" placeholder="john@example.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="role"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Role</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a role" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="admin">Admin</SelectItem>
                  <SelectItem value="editor">Editor</SelectItem>
                  <SelectItem value="user">User</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="bio"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Bio</FormLabel>
              <FormControl>
                <Textarea placeholder="Tell us about yourself..." {...field} />
              </FormControl>
              <FormDescription>Max 500 characters</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="notifications"
          render={({ field }) => (
            <FormItem className="flex flex-row items-start space-x-3 space-y-0">
              <FormControl>
                <Checkbox checked={field.value} onCheckedChange={field.onChange} />
              </FormControl>
              <div className="space-y-1 leading-none">
                <FormLabel>Email notifications</FormLabel>
                <FormDescription>Receive emails about account activity</FormDescription>
              </div>
            </FormItem>
          )}
        />

        <Button type="submit" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? 'Creating...' : 'Create User'}
        </Button>
      </form>
    </Form>
  )
}
```

### Form with Server Action

```tsx
'use client'

import { useFormState } from 'react-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'

export function ContactForm() {
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
  })

  async function onSubmit(values: FormValues) {
    const formData = new FormData()
    Object.entries(values).forEach(([key, value]) => formData.append(key, String(value)))
    await submitContact(formData)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        {/* fields */}
      </form>
    </Form>
  )
}
```

---

## Theming & Dark Mode

### Setup with next-themes

```bash
npm install next-themes
npx shadcn@latest add dropdown-menu
```

```tsx
// app/providers.tsx
'use client'
import { ThemeProvider } from 'next-themes'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      {children}
    </ThemeProvider>
  )
}
```

```tsx
// components/theme-toggle.tsx
'use client'
import { Moon, Sun } from 'lucide-react'
import { useTheme } from 'next-themes'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

export function ThemeToggle() {
  const { setTheme } = useTheme()
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon">
          <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme('light')}>Light</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme('dark')}>Dark</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme('system')}>System</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

### Custom Colors in `globals.css`

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    /* ... etc */
  }
}
```

---

## Common Layouts

### App Shell with Sidebar

```tsx
import { SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import { AppSidebar } from '@/components/app-sidebar'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <main className="flex-1">
        <header className="flex h-14 items-center gap-4 border-b px-6">
          <SidebarTrigger />
          <h1 className="text-lg font-semibold">Dashboard</h1>
        </header>
        <div className="p-6">{children}</div>
      </main>
    </SidebarProvider>
  )
}
```

### Responsive Header with Mobile Nav

```tsx
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { Menu } from 'lucide-react'

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur">
      <div className="container flex h-14 items-center">
        <div className="mr-4 hidden md:flex">
          <Logo />
          <nav className="flex items-center gap-6 text-sm ml-6">
            <Link href="/dashboard">Dashboard</Link>
            <Link href="/settings">Settings</Link>
          </nav>
        </div>

        {/* Mobile hamburger */}
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="outline" size="icon" className="md:hidden">
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-[300px]">
            <nav className="flex flex-col gap-4 mt-8">
              <Link href="/dashboard">Dashboard</Link>
              <Link href="/settings">Settings</Link>
            </nav>
          </SheetContent>
        </Sheet>

        <div className="flex flex-1 items-center justify-end gap-2">
          <ThemeToggle />
          <UserMenu />
        </div>
      </div>
    </header>
  )
}
```

### Card Grid

```tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export function StatsGrid({ stats }: { stats: Stat[] }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <Card key={stat.label}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{stat.label}</CardTitle>
            <stat.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stat.value}</div>
            <p className="text-xs text-muted-foreground">{stat.description}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
```

---

## Tailwind CSS Patterns

### Common Utility Patterns

```tsx
// Centering
<div className="flex items-center justify-center min-h-screen">

// Container with max-width
<div className="container mx-auto px-4">

// Responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

// Sticky header
<header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur">

// Truncated text
<p className="truncate">Very long text...</p>

// Line clamp
<p className="line-clamp-3">Multi-line truncation...</p>

// Aspect ratio
<div className="aspect-video rounded-lg overflow-hidden">

// Animations
<div className="animate-pulse">    {/* Loading skeleton */}
<div className="animate-spin">     {/* Spinner */}
<div className="transition-all duration-200 hover:scale-105">
```

### Button Variants

```tsx
<Button>Default</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>
<Button variant="destructive">Delete</Button>
<Button size="sm">Small</Button>
<Button size="lg">Large</Button>
<Button size="icon"><Plus className="h-4 w-4" /></Button>
<Button disabled>Disabled</Button>
<Button asChild><Link href="/page">As Link</Link></Button>
```

---

## Toast Notifications

```bash
npx shadcn@latest add sonner
```

```tsx
// app/layout.tsx
import { Toaster } from '@/components/ui/sonner'

export default function RootLayout({ children }) {
  return (
    <html><body>{children}<Toaster /></body></html>
  )
}

// Usage anywhere
import { toast } from 'sonner'

toast.success('User created')
toast.error('Something went wrong')
toast.info('New update available')
toast.warning('This action cannot be undone')
toast.promise(asyncAction(), {
  loading: 'Creating...',
  success: 'Created!',
  error: 'Failed to create',
})
```

---

## Command Palette (⌘K)

```tsx
'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'

export function CommandPalette() {
  const [open, setOpen] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }
    document.addEventListener('keydown', down)
    return () => document.removeEventListener('keydown', down)
  }, [])

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Navigation">
          <CommandItem onSelect={() => { router.push('/dashboard'); setOpen(false) }}>
            Dashboard
          </CommandItem>
          <CommandItem onSelect={() => { router.push('/settings'); setOpen(false) }}>
            Settings
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  )
}
```
