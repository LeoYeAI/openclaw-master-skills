/**
 * Custom JWT Session Claims Type Definitions
 *
 * This file provides TypeScript type safety for custom JWT claims in Clerk.
 * Place this in your project's types/ directory (e.g., types/globals.d.ts).
 *
 * After adding this, sessionClaims will have auto-complete and type checking
 * for your custom claims.
 *
 * Usage:
 * ```typescript
 * import { auth } from '@clerk/nextjs/server'
 *
 * const { sessionClaims } = await auth()
 * const role = sessionClaims?.metadata?.role // Type: 'admin' | 'moderator' | 'user' | undefined
 * ```
 */

export {}

declare global {
  /**
   * Extend Clerk's CustomJwtSessionClaims interface with your custom claims.
   *
   * IMPORTANT: The structure must match your JWT template exactly.
   */
  interface CustomJwtSessionClaims {
    /**
     * Custom metadata claims
     */
    metadata: {
      /**
       * User's role in the application
       * Maps to: {{user.public_metadata.role}}
       */
      role?: 'admin' | 'moderator' | 'user'

      /**
       * Whether user has completed onboarding
       * Maps to: {{user.public_metadata.onboardingComplete}}
       */
      onboardingComplete?: boolean

      /**
       * User's department
       * Maps to: {{user.public_metadata.department}}
       */
      department?: string

      /**
       * User's permissions array
       * Maps to: {{user.public_metadata.permissions}}
       */
      permissions?: string[]

      /**
       * Organization ID for multi-tenant apps
       * Maps to: {{user.public_metadata.org_id}}
       */
      organizationId?: string

      /**
       * Organization slug for multi-tenant apps
       * Maps to: {{user.public_metadata.org_slug}}
       */
      organizationSlug?: string

      /**
       * User's role in organization
       * Maps to: {{user.public_metadata.org_role}}
       */
      organizationRole?: string
    }

    /**
     * User's email address (if included in template)
     * Maps to: {{user.primary_email_address}}
     */
    email?: string

    /**
     * User's full name (if included in template)
     * Maps to: {{user.full_name}}
     */
    full_name?: string

    /**
     * User ID (if included in template)
     * Maps to: {{user.id}}
     * Note: Also available as 'sub' in default claims
     */
    user_id?: string
  }
}

/**
 * Example Usage in Next.js Server Component:
 *
 * ```typescript
 * import { auth } from '@clerk/nextjs/server'
 *
 * export default async function AdminPage() {
 *   const { sessionClaims } = await auth()
 *
 *   // TypeScript knows about these properties now
 *   if (sessionClaims?.metadata?.role !== 'admin') {
 *     return <div>Unauthorized</div>
 *   }
 *
 *   return <div>Admin Dashboard</div>
 * }
 * ```
 *
 * Example Usage in Cloudflare Workers:
 *
 * ```typescript
 * import { verifyToken } from '@clerk/backend'
 *
 * const { data } = await verifyToken(token, { secretKey })
 *
 * // Access custom claims with type safety
 * const role = data.metadata?.role
 * const isAdmin = role === 'admin'
 * ```
 */
