/**
 * Server Component with Clerk Auth
 *
 * Demonstrates using auth() and currentUser() in Server Components
 *
 * CRITICAL (v6): auth() is now async - must use await
 */

import { auth, currentUser } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function DashboardPage() {
  /**
   * Option 1: Lightweight auth check
   *
   * Use auth() when you only need userId/sessionId
   * This is faster than currentUser()
   */
  const { userId, sessionId } = await auth()

  // Redirect if not authenticated (shouldn't happen if middleware configured)
  if (!userId) {
    redirect('/sign-in')
  }

  /**
   * Option 2: Full user object
   *
   * Use currentUser() when you need full user data
   * Heavier than auth(), so use sparingly
   */
  const user = await currentUser()

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      <div className="mt-4 space-y-2">
        <p>
          <strong>User ID:</strong> {userId}
        </p>
        <p>
          <strong>Session ID:</strong> {sessionId}
        </p>
        <p>
          <strong>Email:</strong>{' '}
          {user?.primaryEmailAddress?.emailAddress}
        </p>
        <p>
          <strong>Name:</strong> {user?.firstName} {user?.lastName}
        </p>

        {/* Access public metadata */}
        {user?.publicMetadata && (
          <div>
            <strong>Role:</strong>{' '}
            {(user.publicMetadata as any).role || 'user'}
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * API Route Example (app/api/user/route.ts)
 */
/*
import { auth, currentUser } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
  const { userId } = await auth()

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const user = await currentUser()

  return NextResponse.json({
    userId,
    email: user?.primaryEmailAddress?.emailAddress,
    name: `${user?.firstName} ${user?.lastName}`,
  })
}
*/

/**
 * Protected API Route with POST (app/api/items/route.ts)
 */
/*
import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const { userId } = await auth()

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const body = await request.json()

  // Validate and process
  // Example: save to database with userId

  return NextResponse.json({
    success: true,
    itemId: crypto.randomUUID(),
    userId,
  }, { status: 201 })
}
*/
