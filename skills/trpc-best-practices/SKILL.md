---
name: tRPC
description: Expert guidance for tRPC (TypeScript Remote Procedure Call) including router setup, procedures, middleware, context, client configuration, and Next.js integration. Use this when building type-safe APIs, integrating tRPC with Next.js, or implementing client-server communication with full TypeScript inference.
---

# tRPC

Expert assistance with tRPC - End-to-end typesafe APIs with TypeScript.

## Overview

tRPC enables building fully typesafe APIs without schemas or code generation:
- Full TypeScript inference from server to client
- No code generation needed
- Excellent DX with autocomplete and type safety
- Works great with Next.js, React Query, and more

## Quick Start

### Installation
```bash
# Core packages
npm install @trpc/server@next @trpc/client@next @trpc/react-query@next

# Peer dependencies
npm install @tanstack/react-query@latest zod
```

### Basic Setup (Next.js App Router)

**1. Create tRPC Router**
```typescript
// server/trpc.ts
import { initTRPC } from '@trpc/server'
import { z } from 'zod'

const t = initTRPC.create()

export const router = t.router
export const publicProcedure = t.procedure
```

**2. Define API Router**
```typescript
// server/routers/_app.ts
import { router, publicProcedure } from '../trpc'
import { z } from 'zod'

export const appRouter = router({
  hello: publicProcedure
    .input(z.object({ name: z.string() }))
    .query(({ input }) => {
      return { greeting: `Hello ${input.name}!` }
    }),

  createUser: publicProcedure
    .input(z.object({
      name: z.string(),
      email: z.string().email(),
    }))
    .mutation(async ({ input }) => {
      const user = await db.user.create({ data: input })
      return user
    }),
})

export type AppRouter = typeof appRouter
```

**3. Create API Route**
```typescript
// app/api/trpc/[trpc]/route.ts
import { fetchRequestHandler } from '@trpc/server/adapters/fetch'
import { appRouter } from '@/server/routers/_app'

const handler = (req: Request) =>
  fetchRequestHandler({
    endpoint: '/api/trpc',
    req,
    router: appRouter,
    createContext: () => ({}),
  })

export { handler as GET, handler as POST }
```

**4. Setup Client Provider**
```typescript
// app/providers.tsx
'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { httpBatchLink } from '@trpc/client'
import { useState } from 'react'
import { trpc } from '@/lib/trpc'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient())
  const [trpcClient] = useState(() =>
    trpc.createClient({
      links: [
        httpBatchLink({
          url: 'http://localhost:3000/api/trpc',
        }),
      ],
    })
  )

  return (
    <trpc.Provider client={trpcClient} queryClient={queryClient}>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </trpc.Provider>
  )
}
```

**5. Create tRPC Client**
```typescript
// lib/trpc.ts
import { createTRPCReact } from '@trpc/react-query'
import type { AppRouter } from '@/server/routers/_app'

export const trpc = createTRPCReact<AppRouter>()
```

**6. Use in Components**
```typescript
'use client'

import { trpc } from '@/lib/trpc'

export default function Home() {
  const hello = trpc.hello.useQuery({ name: 'World' })
  const createUser = trpc.createUser.useMutation()

  return (
    <div>
      <p>{hello.data?.greeting}</p>
      <button
        onClick={() => createUser.mutate({
          name: 'John',
          email: 'john@example.com'
        })}
      >
        Create User
      </button>
    </div>
  )
}
```

## Router Definition

### Basic Router
```typescript
import { router, publicProcedure } from './trpc'
import { z } from 'zod'

export const userRouter = router({
  // Query - for fetching data
  getById: publicProcedure
    .input(z.string())
    .query(async ({ input }) => {
      return await db.user.findUnique({ where: { id: input } })
    }),

  // Mutation - for creating/updating/deleting
  create: publicProcedure
    .input(z.object({
      name: z.string(),
      email: z.string().email(),
    }))
    .mutation(async ({ input }) => {
      return await db.user.create({ data: input })
    }),

  // Subscription - for real-time updates
  onUpdate: publicProcedure
    .subscription(() => {
      return observable<User>((emit) => {
        // Implementation
      })
    }),
})
```

### Nested Routers
```typescript
import { router } from './trpc'
import { userRouter } from './routers/user'
import { postRouter } from './routers/post'
import { commentRouter } from './routers/comment'

export const appRouter = router({
  user: userRouter,
  post: postRouter,
  comment: commentRouter,
})

// Usage on client:
// trpc.user.getById.useQuery('123')
// trpc.post.list.useQuery()
// trpc.comment.create.useMutation()
```

### Merging Routers
```typescript
import { router, publicProcedure } from './trpc'

const userRouter = router({
  list: publicProcedure.query(() => {/* ... */}),
  getById: publicProcedure.input(z.string()).query(() => {/* ... */}),
})

const postRouter = router({
  list: publicProcedure.query(() => {/* ... */}),
  create: publicProcedure.input(z.object({})).mutation(() => {/* ... */}),
})

// Merge into app router
export const appRouter = router({
  user: userRouter,
  post: postRouter,
})
```

## Input Validation with Zod

### Basic Validation
```typescript
import { z } from 'zod'

export const userRouter = router({
  create: publicProcedure
    .input(z.object({
      name: z.string().min(2).max(50),
      email: z.string().email(),
      age: z.number().int().positive().optional(),
      role: z.enum(['user', 'admin']),
    }))
    .mutation(async ({ input }) => {
      // input is fully typed!
      return await db.user.create({ data: input })
    }),
})
```

### Complex Validation
```typescript
const createPostInput = z.object({
  title: z.string().min(5).max(100),
  content: z.string().min(10),
  published: z.boolean().default(false),
  tags: z.array(z.string()).min(1).max(5),
  metadata: z.object({
    views: z.number().default(0),
    likes: z.number().default(0),
  }).optional(),
})

export const postRouter = router({
  create: publicProcedure
    .input(createPostInput)
    .mutation(async ({ input }) => {
      return await db.post.create({ data: input })
    }),
})
```

### Reusable Schemas
```typescript
// schemas/user.ts
export const userSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
})

export const createUserSchema = userSchema.omit({ id: true })
export const updateUserSchema = userSchema.partial()

// Use in router
export const userRouter = router({
  create: publicProcedure
    .input(createUserSchema)
    .mutation(({ input }) => {/* ... */}),

  update: publicProcedure
    .input(z.object({
      id: z.string(),
      data: updateUserSchema,
    }))
    .mutation(({ input }) => {/* ... */}),
})
```

## Context

### Creating Context
```typescript
// server/context.ts
import { inferAsyncReturnType } from '@trpc/server'
import { FetchCreateContextFnOptions } from '@trpc/server/adapters/fetch'

export async function createContext(opts: FetchCreateContextFnOptions) {
  // Get session from cookies/headers
  const session = await getSession(opts.req)

  return {
    session,
    db,
  }
}

export type Context = inferAsyncReturnType<typeof createContext>
```

### Using Context in tRPC
```typescript
// server/trpc.ts
import { initTRPC } from '@trpc/server'
import { Context } from './context'

const t = initTRPC.context<Context>().create()

export const router = t.router
export const publicProcedure = t.procedure
```

### Accessing Context in Procedures
```typescript
export const userRouter = router({
  me: publicProcedure.query(({ ctx }) => {
    // ctx.session, ctx.db are available
    if (!ctx.session) {
      throw new TRPCError({ code: 'UNAUTHORIZED' })
    }

    return ctx.db.user.findUnique({
      where: { id: ctx.session.userId }
    })
  }),
})
```

## Middleware

### Creating Middleware
```typescript
// server/trpc.ts
import { initTRPC, TRPCError } from '@trpc/server'

const t = initTRPC.context<Context>().create()

// Logging middleware
const loggerMiddleware = t.middleware(async ({ path, type, next }) => {
  const start = Date.now()
  const result = await next()
  const duration = Date.now() - start

  console.log(`${type} ${path} took ${duration}ms`)

  return result
})

// Auth middleware
const isAuthed = t.middleware(({ ctx, next }) => {
  if (!ctx.session) {
    throw new TRPCError({ code: 'UNAUTHORIZED' })
  }

  return next({
    ctx: {
      // Infers session is non-nullable
      session: ctx.session,
    },
  })
})

// Create procedures with middleware
export const publicProcedure = t.procedure.use(loggerMiddleware)
export const protectedProcedure = t.procedure.use(loggerMiddleware).use(isAuthed)
```

### Using Protected Procedures
```typescript
export const postRouter = router({
  // Public - anyone can access
  list: publicProcedure.query(() => {
    return db.post.findMany({ where: { published: true } })
  }),

  // Protected - requires authentication
  create: protectedProcedure
    .input(z.object({ title: z.string() }))
    .mutation(({ ctx, input }) => {
      // ctx.session is guaranteed to exist
      return db.post.create({
        data: {
          ...input,
          authorId: ctx.session.userId,
        },
      })
    }),
})
```

### Role-Based Middleware
```typescript
const requireRole = (role: string) =>
  t.middleware(({ ctx, next }) => {
    if (!ctx.session || ctx.session.role !== role) {
      throw new TRPCError({ code: 'FORBIDDEN' })
    }
    return next()
  })

export const adminProcedure = protectedProcedure.use(requireRole('admin'))

export const userRouter = router({
  delete: adminProcedure
    .input(z.string())
    .mutation(({ input }) => {
      return db.user.delete({ where: { id: input } })
    }),
})
```

## Client Usage

### Queries
```typescript
'use client'

import { trpc } from '@/lib/trpc'

export default function UserList() {
  // Basic query
  const users = trpc.user.list.useQuery()

  // Query with input
  const user = trpc.user.getById.useQuery('user-123')

  // Disabled query
  const profile = trpc.user.getProfile.useQuery(
    { id: userId },
    { enabled: !!userId }
  )

  // With options
  const posts = trpc.post.list.useQuery(undefined, {
    refetchInterval: 5000,
    staleTime: 1000,
  })

  if (users.isLoading) return <div>Loading...</div>
  if (users.error) return <div>Error: {users.error.message}</div>

  return (
    <ul>
      {users.data?.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  )
}
```

### Mutations
```typescript
'use client'

export default function CreateUser() {
  const utils = trpc.useContext()

  const createUser = trpc.user.create.useMutation({
    onSuccess: () => {
      // Invalidate and refetch
      utils.user.list.invalidate()
    },
    onError: (error) => {
      console.error('Failed to create user:', error)
    },
  })

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)

    createUser.mutate({
      name: formData.get('name') as string,
      email: formData.get('email') as string,
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" required />
      <input name="email" type="email" required />
      <button type="submit" disabled={createUser.isLoading}>
        {createUser.isLoading ? 'Creating...' : 'Create User'}
      </button>
    </form>
  )
}
```

### Optimistic Updates
```typescript
const updatePost = trpc.post.update.useMutation({
  onMutate: async (newPost) => {
    // Cancel outgoing refetches
    await utils.post.list.cancel()

    // Snapshot previous value
    const previousPosts = utils.post.list.getData()

    // Optimistically update
    utils.post.list.setData(undefined, (old) =>
      old?.map(post =>
        post.id === newPost.id ? { ...post, ...newPost } : post
      )
    )

    return { previousPosts }
  },
  onError: (err, newPost, context) => {
    // Rollback on error
    utils.post.list.setData(undefined, context?.previousPosts)
  },
  onSettled: () => {
    // Refetch after success or error
    utils.post.list.invalidate()
  },
})
```

### Infinite Queries
```typescript
// Server
export const postRouter = router({
  list: publicProcedure
    .input(z.object({
      cursor: z.string().optional(),
      limit: z.number().min(1).max(100).default(10),
    }))
    .query(async ({ input }) => {
      const posts = await db.post.findMany({
        take: input.limit + 1,
        cursor: input.cursor ? { id: input.cursor } : undefined,
      })

      let nextCursor: string | undefined = undefined
      if (posts.length > input.limit) {
        const nextItem = posts.pop()
        nextCursor = nextItem!.id
      }

      return { posts, nextCursor }
    }),
})

// Client
export default function InfinitePosts() {
  const posts = trpc.post.list.useInfiniteQuery(
    { limit: 10 },
    {
      getNextPageParam: (lastPage) => lastPage.nextCursor,
    }
  )

  return (
    <div>
      {posts.data?.pages.map((page, i) => (
        <div key={i}>
          {page.posts.map(post => (
            <div key={post.id}>{post.title}</div>
          ))}
        </div>
      ))}

      <button
        onClick={() => posts.fetchNextPage()}
        disabled={!posts.hasNextPage || posts.isFetchingNextPage}
      >
        {posts.isFetchingNextPage ? 'Loading...' : 'Load More'}
      </button>
    </div>
  )
}
```

## Error Handling

### Server Errors
```typescript
import { TRPCError } from '@trpc/server'

export const postRouter = router({
  getById: publicProcedure
    .input(z.string())
    .query(async ({ input }) => {
      const post = await db.post.findUnique({ where: { id: input } })

      if (!post) {
        throw new TRPCError({
          code: 'NOT_FOUND',
          message: 'Post not found',
        })
      }

      return post
    }),

  create: protectedProcedure
    .input(z.object({ title: z.string() }))
    .mutation(async ({ ctx, input }) => {
      if (!ctx.session.verified) {
        throw new TRPCError({
          code: 'FORBIDDEN',
          message: 'Email must be verified',
        })
      }

      try {
        return await db.post.create({ data: input })
      } catch (error) {
        throw new TRPCError({
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to create post',
          cause: error,
        })
      }
    }),
})
```

### Error Codes
- `BAD_REQUEST` - Invalid input
- `UNAUTHORIZED` - Not authenticated
- `FORBIDDEN` - Not authorized
- `NOT_FOUND` - Resource not found
- `TIMEOUT` - Request timeout
- `CONFLICT` - Resource conflict
- `PRECONDITION_FAILED` - Precondition check failed
- `PAYLOAD_TOO_LARGE` - Request too large
- `METHOD_NOT_SUPPORTED` - HTTP method not supported
- `TOO_MANY_REQUESTS` - Rate limited
- `CLIENT_CLOSED_REQUEST` - Client closed request
- `INTERNAL_SERVER_ERROR` - Server error

### Client Error Handling
```typescript
const createPost = trpc.post.create.useMutation({
  onError: (error) => {
    if (error.data?.code === 'UNAUTHORIZED') {
      router.push('/login')
    } else if (error.data?.code === 'FORBIDDEN') {
      alert('You do not have permission')
    } else {
      alert('Something went wrong')
    }
  },
})
```

## Server-Side Calls

### In Server Components
```typescript
// app/users/page.tsx
import { createCaller } from '@/server/routers/_app'
import { createContext } from '@/server/context'

export default async function UsersPage() {
  const ctx = await createContext({ req: {} as any })
  const caller = createCaller(ctx)

  const users = await caller.user.list()

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  )
}
```

### Create Caller
```typescript
// server/routers/_app.ts
export const createCaller = createCallerFactory(appRouter)

// Usage
const caller = createCaller(ctx)
const user = await caller.user.getById('123')
```

## Advanced Patterns

### Request Batching
```typescript
import { httpBatchLink } from '@trpc/client'

const trpcClient = trpc.createClient({
  links: [
    httpBatchLink({
      url: '/api/trpc',
      maxURLLength: 2083, // Reasonable limit
    }),
  ],
})
```

### Request Deduplication
Automatic with React Query - multiple components requesting same data will only make one request.

### Custom Headers
```typescript
const trpcClient = trpc.createClient({
  links: [
    httpBatchLink({
      url: '/api/trpc',
      headers: () => {
        return {
          Authorization: `Bearer ${getToken()}`,
        }
      },
    }),
  ],
})
```

### Error Formatting
```typescript
// server/trpc.ts
const t = initTRPC.context<Context>().create({
  errorFormatter({ shape, error }) {
    return {
      ...shape,
      data: {
        ...shape.data,
        zodError:
          error.cause instanceof ZodError
            ? error.cause.flatten()
            : null,
      },
    }
  },
})
```

## Testing

### Testing Procedures
```typescript
import { appRouter } from '@/server/routers/_app'
import { createCaller } from '@/server/routers/_app'

describe('user router', () => {
  it('creates user', async () => {
    const ctx = { session: mockSession, db: mockDb }
    const caller = createCaller(ctx)

    const user = await caller.user.create({
      name: 'John',
      email: 'john@example.com',
    })

    expect(user.name).toBe('John')
  })
})
```

## Best Practices

1. **Use Zod for validation** - Always validate inputs
2. **Keep procedures small** - Single responsibility
3. **Use middleware for auth** - Don't repeat auth checks
4. **Type your context** - Full type safety
5. **Organize routers** - Split into logical domains
6. **Handle errors properly** - Use appropriate error codes
7. **Leverage React Query** - Use its caching and refetching
8. **Batch requests** - Enable batching for better performance
9. **Use optimistic updates** - Better UX
10. **Document procedures** - Add JSDoc comments

## Resources

- Docs: https://trpc.io
- Next.js Guide: https://trpc.io/docs/nextjs
- Examples: https://github.com/trpc/trpc/tree/main/examples
