/**
 * Cloudflare Worker with Clerk Authentication
 *
 * This template demonstrates:
 * - JWT token verification with @clerk/backend
 * - Protected API routes
 * - Type-safe Hono context with auth state
 * - Proper error handling
 *
 * Dependencies:
 * - @clerk/backend@^2.17.2
 * - hono@^4.10.1
 */

import { Hono } from 'hono'
import { verifyToken } from '@clerk/backend'
import { cors } from 'hono/cors'

// Type-safe environment bindings
type Bindings = {
  CLERK_SECRET_KEY: string
  CLERK_PUBLISHABLE_KEY: string
}

// Context variables with auth state
type Variables = {
  userId: string | null
  sessionClaims: any | null
}

const app = new Hono<{ Bindings: Bindings; Variables: Variables }>()

// CORS middleware (adjust origins for production)
app.use('*', cors({
  origin: ['http://localhost:5173', 'https://yourdomain.com'],
  credentials: true,
}))

/**
 * Auth Middleware - Verifies Clerk JWT tokens
 *
 * CRITICAL SECURITY:
 * - Always set authorizedParties to prevent CSRF attacks
 * - Use secretKey, not deprecated apiKey
 * - Token is in Authorization: Bearer <token> header
 */
app.use('/api/*', async (c, next) => {
  const authHeader = c.req.header('Authorization')

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    // No auth header - continue as unauthenticated
    c.set('userId', null)
    c.set('sessionClaims', null)
    return next()
  }

  // Extract token from "Bearer <token>"
  const token = authHeader.substring(7)

  try {
    // Verify token with Clerk
    const { data, error } = await verifyToken(token, {
      secretKey: c.env.CLERK_SECRET_KEY,

      // IMPORTANT: Set to your actual domain(s) to prevent CSRF
      // Source: https://clerk.com/docs/reference/backend/verify-token
      authorizedParties: [
        'http://localhost:5173', // Development
        'https://yourdomain.com', // Production
      ],
    })

    if (error) {
      console.error('[Auth] Token verification failed:', error.message)
      c.set('userId', null)
      c.set('sessionClaims', null)
    } else {
      // 'sub' claim contains the user ID
      c.set('userId', data.sub)
      c.set('sessionClaims', data)
    }
  } catch (err) {
    console.error('[Auth] Token verification error:', err)
    c.set('userId', null)
    c.set('sessionClaims', null)
  }

  return next()
})

/**
 * Public Routes - No authentication required
 */

app.get('/api/public', (c) => {
  return c.json({
    message: 'This endpoint is public',
    timestamp: new Date().toISOString(),
  })
})

app.get('/api/health', (c) => {
  return c.json({
    status: 'ok',
    version: '1.0.0',
  })
})

/**
 * Protected Routes - Require authentication
 */

app.get('/api/protected', (c) => {
  const userId = c.get('userId')

  if (!userId) {
    return c.json({ error: 'Unauthorized' }, 401)
  }

  return c.json({
    message: 'This endpoint is protected',
    userId,
    timestamp: new Date().toISOString(),
  })
})

app.get('/api/user/profile', (c) => {
  const userId = c.get('userId')
  const sessionClaims = c.get('sessionClaims')

  if (!userId) {
    return c.json({ error: 'Unauthorized' }, 401)
  }

  // Access custom claims from JWT template (if configured)
  return c.json({
    userId,
    email: sessionClaims?.email,
    role: sessionClaims?.role,
    organizationId: sessionClaims?.organization_id,
  })
})

/**
 * POST Example - Create resource with auth
 */

app.post('/api/items', async (c) => {
  const userId = c.get('userId')

  if (!userId) {
    return c.json({ error: 'Unauthorized' }, 401)
  }

  const body = await c.req.json()

  // Validate and process body
  // Example: save to D1, KV, or R2

  return c.json({
    success: true,
    itemId: crypto.randomUUID(),
    userId,
  }, 201)
})

/**
 * Role-Based Access Control Example
 */

app.get('/api/admin/dashboard', (c) => {
  const userId = c.get('userId')
  const sessionClaims = c.get('sessionClaims')

  if (!userId) {
    return c.json({ error: 'Unauthorized' }, 401)
  }

  // Check role from custom JWT claims
  const role = sessionClaims?.role

  if (role !== 'admin') {
    return c.json({ error: 'Forbidden: Admin access required' }, 403)
  }

  return c.json({
    message: 'Admin dashboard data',
    userId,
  })
})

/**
 * Error Handling
 */

app.onError((err, c) => {
  console.error('[Error]', err)
  return c.json({ error: 'Internal Server Error' }, 500)
})

app.notFound((c) => {
  return c.json({ error: 'Not Found' }, 404)
})

/**
 * Export the Hono app
 *
 * ES Module format for Cloudflare Workers
 */
export default app
