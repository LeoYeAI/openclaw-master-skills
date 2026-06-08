---
name: nextjs-expert
version: 1.0.0
description: Use when building Next.js 14/15 applications with the App Router. Invoke for routing, layouts, Server Components, Client Components, Server Actions, Route Handlers, authentication, middleware, data fetching, caching, revalidation, streaming, Suspense, loading states, error boundaries, dynamic routes, parallel routes, intercepting routes, or any Next.js architecture question.
triggers:
  - Next.js
  - Next
  - nextjs
  - App Router
  - Server Components
  - Client Components
  - Server Actions
  - use server
  - use client
  - Route Handler
  - middleware
  - layout.tsx
  - page.tsx
  - loading.tsx
  - error.tsx
  - revalidatePath
  - revalidateTag
  - NextAuth
  - Auth.js
  - generateStaticParams
  - generateMetadata
role: specialist
scope: implementation
output-format: code
---

# Next.js Expert

Comprehensive Next.js 15 App Router specialist. Adapted from buildwithclaude by Dave Poon (MIT).

## Role Definition

You are a senior Next.js engineer specializing in the App Router, React Server Components, and production-grade full-stack applications with TypeScript.

## Core Principles

1. **Server-first**: Components are Server Components by default. Only add `'use client'` when you need hooks, event handlers, or browser APIs.
2. **Push client boundaries down**: Keep `'use client'` as low in the tree as possible.
3. **Async params**: In Next.js 15, `params` and `searchParams` are `Promise` types — always `await` them.
4. **Colocation**: Keep components, tests, and styles near their routes.
5. **Type everything**: Use TypeScript strictly.

---

## App Router File Conventions

### Route Files

| File | Purpose |
|------|---------|
| `page.tsx` | Unique UI for a route, makes it publicly accessible |
| `layout.tsx` | Shared UI wrapper, preserves state across navigations |
| `loading.tsx` | Loading UI using React Suspense |
| `error.tsx` | Error boundary for route segment (must be `'use client'`) |
| `not-found.tsx` | UI for 404 responses |
| `template.tsx` | Like layout but re-renders on navigation |
| `default.tsx` | Fallback for parallel routes |
| `route.ts` | API endpoint (Route Handler) |

### Folder Conventions

| Pattern | Purpose | Example |
|---------|---------|---------|
| `folder/` | Route segment | `app/blog/` → `/blog` |
| `[folder]/` | Dynamic segment | `app/blog/[slug]/` → `/blog/:slug` |
| `[...folder]/` | Catch-all segment | `app/docs/[...slug]/` → `/docs/*` |
| `[[...folder]]/` | Optional catch-all | `app/shop/[[...slug]]/` → `/shop` or `/shop/*` |
| `(folder)/` | Route group (no URL) | `app/(marketing)/about/` → `/about` |
| `@folder/` | Named slot (parallel routes) | `app/@modal/login/` |
| `_folder/` | Private folder (excluded) | `app/_components/` |

### File Hierarchy (render order)

1. `layout.tsx` → 2. `template.tsx` → 3. `error.tsx` (boundary) → 4. `loading.tsx` (boundary) → 5. `not-found.tsx` (boundary) → 6. `page.tsx`

---

## Pages and Routing

### Basic Page (Server Component)

```tsx
// app/about/page.tsx
export default function AboutPage() {
  return (
    <main>
      <h1>About Us</h1>
      <p>Welcome to our company.</p>
    </main>
  )
}
```

### Dynamic Routes

```tsx
// app/blog/[slug]/page.tsx
interface PageProps {
  params: Promise<{ slug: string }>
}

export default async function BlogPost({ params }: PageProps) {
  const { slug } = await params
  const post = await getPost(slug)
  return <article>{post.content}</article>
}
```

### Search Params

```tsx
// app/search/page.tsx
interface PageProps {
  searchParams: Promise<{ q?: string; page?: string }>
}

export default async function SearchPage({ searchParams }: PageProps) {
  const { q, page } = await searchParams
  const results = await search(q, parseInt(page || '1'))
  return <SearchResults results={results} />
}
```

### Static Generation

```tsx
export async function generateStaticParams() {
  const posts = await getAllPosts()
  return posts.map((post) => ({ slug: post.slug }))
}

// Allow dynamic params not in generateStaticParams
export const dynamicParams = true
```

---

## Layouts

### Root Layout (Required)

```tsx
// app/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

### Nested Layout with Data Fetching

```tsx
// app/dashboard/layout.tsx
import { getUser } from '@/lib/get-user'

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const user = await getUser()
  return (
    <div className="flex">
      <Sidebar user={user} />
      <main className="flex-1 p-6">{children}</main>
    </div>
  )
}
```

### Route Groups for Multiple Root Layouts

```
app/
├── (marketing)/
│   ├── layout.tsx          # Marketing layout with <html>/<body>
│   └── about/page.tsx
└── (app)/
    ├── layout.tsx          # App layout with <html>/<body>
    └── dashboard/page.tsx
```

### Metadata

```tsx
// Static
export const metadata: Metadata = {
  title: 'About Us',
  description: 'Learn more about our company',
}

// Dynamic
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params
  const post = await getPost(slug)
  return {
    title: post.title,
    openGraph: { title: post.title, images: [post.coverImage] },
  }
}

// Template in layouts
export const metadata: Metadata = {
  title: { template: '%s | Dashboard', default: 'Dashboard' },
}
```

---

## Server Components vs Client Components

### Decision Guide

**Server Component (default) when:**
- Fetching data or accessing backend resources
- Keeping sensitive info on server (API keys, tokens)
- Reducing client JavaScript bundle
- No interactivity needed

**Client Component (`'use client'`) when:**
- Using `useState`, `useEffect`, `useReducer`
- Using event handlers (`onClick`, `onChange`)
- Using browser APIs (`window`, `document`)
- Using custom hooks with state

### Composition Patterns

**Pattern 1: Server data → Client interactivity**

```tsx
// app/products/page.tsx (Server)
export default async function ProductsPage() {
  const products = await getProducts()
  return <ProductFilter products={products} />
}

// components/product-filter.tsx (Client)
'use client'
export function ProductFilter({ products }: { products: Product[] }) {
  const [filter, setFilter] = useState('')
  const filtered = products.filter(p => p.name.includes(filter))
  return (
    <>
      <input onChange={e => setFilter(e.target.value)} />
      {filtered.map(p => <ProductCard key={p.id} product={p} />)}
    </>
  )
}
```

**Pattern 2: Children as Server Components**

```tsx
// components/client-wrapper.tsx
'use client'
export function ClientWrapper({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false)
  return (
    <div>
      <button onClick={() => setIsOpen(!isOpen)}>Toggle</button>
      {isOpen && children}
    </div>
  )
}

// app/page.tsx (Server)
export default function Page() {
  return (
    <ClientWrapper>
      <ServerContent /> {/* Still renders on server! */}
    </ClientWrapper>
  )
}
```

**Pattern 3: Providers at the boundary**

```tsx
// app/providers.tsx
'use client'
import { ThemeProvider } from 'next-themes'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient()

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="system">
        {children}
      </ThemeProvider>
    </QueryClientProvider>
  )
}
```

### Shared Data with `cache()`

```tsx
import { cache } from 'react'

export const getUser = cache(async () => {
  const response = await fetch('/api/user')
  return response.json()
})

// Both layout and page call getUser() — only one fetch happens
```

---

## Data Fetching

### Async Server Components

```tsx
export default async function PostsPage() {
  const posts = await fetch('https://api.example.com/posts').then(r => r.json())
  return <ul>{posts.map(p => <li key={p.id}>{p.title}</li>)}</ul>
}
```

### Parallel Data Fetching

```tsx
export default async function DashboardPage() {
  const [user, posts, analytics] = await Promise.all([
    getUser(), getPosts(), getAnalytics()
  ])
  return <Dashboard user={user} posts={posts} analytics={analytics} />
}
```

### Streaming with Suspense

```tsx
import { Suspense } from 'react'

export default function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<StatsSkeleton />}>
        <SlowStats />
      </Suspense>
      <Suspense fallback={<ChartSkeleton />}>
        <SlowChart />
      </Suspense>
    </div>
  )
}
```

### Caching

```tsx
// Cache indefinitely (static)
const data = await fetch('https://api.example.com/data')

// Revalidate every hour
const data = await fetch(url, { next: { revalidate: 3600 } })

// No caching (always fresh)
const data = await fetch(url, { cache: 'no-store' })

// Cache with tags
const data = await fetch(url, { next: { tags: ['posts'] } })
```

---

## Loading and Error States

### Loading UI

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-1/4 mb-4" />
      <div className="space-y-3">
        <div className="h-4 bg-gray-200 rounded w-full" />
        <div className="h-4 bg-gray-200 rounded w-5/6" />
      </div>
    </div>
  )
}
```

### Error Boundary

```tsx
// app/dashboard/error.tsx
'use client'

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="p-4 bg-red-50 border border-red-200 rounded">
      <h2 className="text-red-800 font-bold">Something went wrong!</h2>
      <p className="text-red-600">{error.message}</p>
      <button onClick={reset} className="mt-2 px-4 py-2 bg-red-600 text-white rounded">
        Try again
      </button>
    </div>
  )
}
```

### Not Found

```tsx
// app/posts/[slug]/page.tsx
import { notFound } from 'next/navigation'

export default async function PostPage({ params }: PageProps) {
  const { slug } = await params
  const post = await getPost(slug)
  if (!post) notFound()
  return <article>{post.content}</article>
}
```

---

## Server Actions

### Defining Actions

```tsx
// app/actions.ts
'use server'

import { z } from 'zod'
import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'

const schema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().min(10),
})

export async function createPost(formData: FormData) {
  const session = await auth()
  if (!session?.user) throw new Error('Unauthorized')

  const parsed = schema.safeParse({
    title: formData.get('title'),
    content: formData.get('content'),
  })

  if (!parsed.success) return { error: parsed.error.flatten() }

  const post = await db.post.create({
    data: { ...parsed.data, authorId: session.user.id },
  })

  revalidatePath('/posts')
  redirect(`/posts/${post.slug}`)
}
```

### Form with useFormState and useFormStatus

```tsx
// components/submit-button.tsx
'use client'
import { useFormStatus } from 'react-dom'

export function SubmitButton() {
  const { pending } = useFormStatus()
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Submitting...' : 'Submit'}
    </button>
  )
}

// components/create-post-form.tsx
'use client'
import { useFormState } from 'react-dom'
import { createPost } from '@/app/actions'

export function CreatePostForm() {
  const [state, formAction] = useFormState(createPost, {})
  return (
    <form action={formAction}>
      <input name="title" />
      {state.error?.title && <p className="text-red-500">{state.error.title[0]}</p>}
      <textarea name="content" />
      <SubmitButton />
    </form>
  )
}
```

### Optimistic Updates

```tsx
'use client'
import { useOptimistic, useTransition } from 'react'

export function TodoList({ initialTodos }: { initialTodos: Todo[] }) {
  const [isPending, startTransition] = useTransition()
  const [optimisticTodos, addOptimistic] = useOptimistic(
    initialTodos,
    (state, newTodo: string) => [...state, { id: 'temp', title: newTodo, completed: false }]
  )

  async function handleSubmit(formData: FormData) {
    const title = formData.get('title') as string
    startTransition(async () => {
      addOptimistic(title)
      await addTodo(formData)
    })
  }

  return (
    <>
      <form action={handleSubmit}>
        <input name="title" />
        <button>Add</button>
      </form>
      <ul>
        {optimisticTodos.map(todo => (
          <li key={todo.id} className={todo.id === 'temp' ? 'opacity-50' : ''}>{todo.title}</li>
        ))}
      </ul>
    </>
  )
}
```

### Revalidation

```tsx
'use server'
import { revalidatePath, revalidateTag } from 'next/cache'

export async function updatePost(id: string, formData: FormData) {
  await db.post.update({ where: { id }, data: { ... } })

  revalidateTag(`post-${id}`)     // Invalidate by cache tag
  revalidatePath('/posts')         // Invalidate specific page
  revalidatePath(`/posts/${id}`)   // Invalidate dynamic route
  revalidatePath('/posts', 'layout') // Invalidate layout and all pages under it
}
```

---

## Route Handlers (API Routes)

### Basic CRUD

```tsx
// app/api/posts/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const page = parseInt(searchParams.get('page') ?? '1')
  const limit = parseInt(searchParams.get('limit') ?? '10')

  const [posts, total] = await Promise.all([
    db.post.findMany({ skip: (page - 1) * limit, take: limit }),
    db.post.count(),
  ])

  return NextResponse.json({ data: posts, pagination: { page, limit, total } })
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  const post = await db.post.create({ data: body })
  return NextResponse.json(post, { status: 201 })
}
```

### Dynamic Route Handler

```tsx
// app/api/posts/[id]/route.ts
export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const post = await db.post.findUnique({ where: { id } })
  if (!post) return NextResponse.json({ error: 'Not found' }, { status: 404 })
  return NextResponse.json(post)
}

export async function DELETE(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  await db.post.delete({ where: { id } })
  return new NextResponse(null, { status: 204 })
}
```

### Streaming / SSE

```tsx
export async function GET() {
  const encoder = new TextEncoder()
  const stream = new ReadableStream({
    async start(controller) {
      for (let i = 0; i < 10; i++) {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ count: i })}\n\n`))
        await new Promise(r => setTimeout(r, 1000))
      }
      controller.close()
    },
  })
  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' },
  })
}
```

---

## Parallel and Intercepting Routes

### Parallel Routes (Slots)

```
app/
├── @modal/
│   ├── (.)photo/[id]/page.tsx   # Intercepted route (modal)
│   └── default.tsx
├── photo/[id]/page.tsx          # Full page route
├── layout.tsx
└── page.tsx
```

```tsx
// app/layout.tsx
export default function Layout({ children, modal }: {
  children: React.ReactNode
  modal: React.ReactNode
}) {
  return <>{children}{modal}</>
}
```

### Modal Component

```tsx
'use client'
import { useRouter } from 'next/navigation'

export function Modal({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center"
         onClick={() => router.back()}>
      <div className="bg-white rounded-lg p-6 max-w-2xl" onClick={e => e.stopPropagation()}>
        {children}
      </div>
    </div>
  )
}
```

---

## Authentication (NextAuth.js v5 / Auth.js)

### Setup

```tsx
// auth.ts
import NextAuth from 'next-auth'
import GitHub from 'next-auth/providers/github'
import Credentials from 'next-auth/providers/credentials'

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    GitHub({ clientId: process.env.GITHUB_ID, clientSecret: process.env.GITHUB_SECRET }),
    Credentials({
      credentials: { email: {}, password: {} },
      authorize: async (credentials) => {
        const user = await getUserByEmail(credentials.email as string)
        if (!user || !await verifyPassword(credentials.password as string, user.password)) return null
        return user
      },
    }),
  ],
  callbacks: {
    jwt: ({ token, user }) => { if (user) { token.id = user.id; token.role = user.role } return token },
    session: ({ session, token }) => { session.user.id = token.id as string; session.user.role = token.role as string; return session },
  },
})

// app/api/auth/[...nextauth]/route.ts
import { handlers } from '@/auth'
export const { GET, POST } = handlers
```

### Middleware Protection

```tsx
// middleware.ts
export { auth as middleware } from '@/auth'

export const config = {
  matcher: ['/dashboard/:path*', '/api/protected/:path*'],
}
```

### Server Component Auth Check

```tsx
import { auth } from '@/auth'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  const session = await auth()
  if (!session) redirect('/login')
  return <h1>Welcome, {session.user?.name}</h1>
}
```

### Server Action Auth Check

```tsx
'use server'
import { auth } from '@/auth'

export async function deletePost(id: string) {
  const session = await auth()
  if (!session?.user) throw new Error('Unauthorized')

  const post = await db.post.findUnique({ where: { id } })
  if (post?.authorId !== session.user.id) throw new Error('Forbidden')

  await db.post.delete({ where: { id } })
  revalidatePath('/posts')
}
```

---

## Route Segment Config

```tsx
export const dynamic = 'force-dynamic'    // 'auto' | 'force-dynamic' | 'error' | 'force-static'
export const revalidate = 3600            // seconds
export const runtime = 'nodejs'           // or 'edge'
export const maxDuration = 30             // seconds
```

---

## Anti-Patterns to Avoid

1. ❌ Adding `'use client'` to entire pages — push it down to interactive leaves
2. ❌ Fetching data in Client Components when it could be a Server Component
3. ❌ Sequential `await` when fetches are independent — use `Promise.all()`
4. ❌ Passing functions as props across server/client boundary (use Server Actions)
5. ❌ Using `useEffect` for data fetching in App Router (use async Server Components)
6. ❌ Forgetting `await params` in Next.js 15 (they're Promises now)
7. ❌ Missing `loading.tsx` or `<Suspense>` boundaries for async pages
8. ❌ Not validating Server Action inputs (always validate with zod)
