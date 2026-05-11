/**
 * Next.js Middleware with Clerk Authentication
 *
 * This middleware protects routes using Clerk's clerkMiddleware.
 * Place this file in the root of your Next.js project.
 *
 * Dependencies:
 * - @clerk/nextjs@^6.33.3
 *
 * CRITICAL (v6 Breaking Change):
 * - auth.protect() is now async - must use await
 * - Source: https://clerk.com/changelog/2024-10-22-clerk-nextjs-v6
 */

import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

/**
 * Define public routes (routes that don't require authentication)
 *
 * Glob patterns supported:
 * - '/path' - exact match
 * - '/path(.*)' - path and all sub-paths
 * - '/api/public/*' - wildcard
 */
const isPublicRoute = createRouteMatcher([
  '/',                    // Homepage
  '/sign-in(.*)',         // Sign-in page and sub-paths
  '/sign-up(.*)',         // Sign-up page and sub-paths
  '/api/public(.*)',      // Public API routes
  '/api/webhooks(.*)',    // Webhook endpoints
  '/about',               // Static pages
  '/pricing',
  '/contact',
])

/**
 * Alternative: Define protected routes instead
 *
 * Uncomment this pattern if you prefer to explicitly protect
 * specific routes rather than inverting the logic:
 */
/*
const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/profile(.*)',
  '/admin(.*)',
  '/api/private(.*)',
])

export default clerkMiddleware(async (auth, request) => {
  if (isProtectedRoute(request)) {
    await auth.protect()
  }
})
*/

/**
 * Default Pattern: Protect all routes except public ones
 *
 * CRITICAL:
 * - auth.protect() MUST be awaited (async in v6)
 * - Without await, route protection will not work
 */
export default clerkMiddleware(async (auth, request) => {
  if (!isPublicRoute(request)) {
    await auth.protect()
  }
})

/**
 * Matcher Configuration
 *
 * Defines which paths run middleware.
 * This is the recommended configuration from Clerk.
 */
export const config = {
  matcher: [
    // Skip Next.js internals and static files
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',

    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
}

/**
 * Advanced: Role-Based Protection
 *
 * Protect routes based on user role or organization membership:
 */
/*
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isAdminRoute = createRouteMatcher(['/admin(.*)'])
const isOrgRoute = createRouteMatcher(['/org(.*)'])

export default clerkMiddleware(async (auth, request) => {
  // Admin routes require 'admin' role
  if (isAdminRoute(request)) {
    await auth.protect((has) => {
      return has({ role: 'admin' })
    })
  }

  // Organization routes require organization membership
  if (isOrgRoute(request)) {
    await auth.protect((has) => {
      return has({ permission: 'org:member' })
    })
  }

  // All other routes use default protection
  if (!isPublicRoute(request)) {
    await auth.protect()
  }
})

export const config = {
  matcher: [
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
  ],
}
*/

/**
 * Troubleshooting:
 *
 * 1. Routes not protected?
 *    - Ensure auth.protect() is awaited
 *    - Check matcher configuration includes your routes
 *    - Verify middleware.ts is in project root
 *
 * 2. Infinite redirects?
 *    - Ensure sign-in/sign-up routes are in isPublicRoute
 *    - Check NEXT_PUBLIC_CLERK_SIGN_IN_URL in .env.local
 *
 * 3. API routes returning HTML?
 *    - Verify '/(api|trpc)(.*)' is in matcher
 *    - Check API routes are not in isPublicRoute if protected
 *
 * Official Docs: https://clerk.com/docs/reference/nextjs/clerk-middleware
 */
