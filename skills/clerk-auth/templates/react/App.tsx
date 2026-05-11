/**
 * React App Component with Clerk Hooks
 *
 * Demonstrates:
 * - useUser() for user data
 * - useAuth() for session tokens
 * - useClerk() for auth methods
 * - Proper loading state handling
 */

import { useUser, useAuth, useClerk, SignInButton, UserButton } from '@clerk/clerk-react'

function App() {
  // Get user object (includes email, metadata, etc.)
  const { isLoaded, isSignedIn, user } = useUser()

  // Get auth state and session methods
  const { userId, getToken } = useAuth()

  // Get Clerk instance for advanced operations
  const { openSignIn, signOut } = useClerk()

  /**
   * CRITICAL: Always check isLoaded before rendering
   *
   * Why: Prevents flash of wrong content while Clerk initializes
   * Source: https://clerk.com/docs/references/react/use-user
   */
  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  /**
   * Unauthenticated View
   */
  if (!isSignedIn) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen gap-4">
        <h1 className="text-4xl font-bold">Welcome</h1>
        <p className="text-gray-600">Sign in to continue</p>

        {/* Option 1: Clerk's pre-built button */}
        <SignInButton mode="modal">
          <button className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
            Sign In
          </button>
        </SignInButton>

        {/* Option 2: Custom button with openSignIn() */}
        {/* <button
          onClick={() => openSignIn()}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg"
        >
          Sign In
        </button> */}
      </div>
    )
  }

  /**
   * Authenticated View
   */
  return (
    <div className="container mx-auto p-8">
      <header className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Dashboard</h1>

        {/* Clerk's pre-built user button (profile + sign out) */}
        <UserButton afterSignOutUrl="/" />
      </header>

      <div className="space-y-4">
        <div className="p-6 bg-white rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">User Information</h2>

          <dl className="space-y-2">
            <div>
              <dt className="font-medium text-gray-700">User ID</dt>
              <dd className="text-gray-900">{userId}</dd>
            </div>

            <div>
              <dt className="font-medium text-gray-700">Email</dt>
              <dd className="text-gray-900">
                {user.primaryEmailAddress?.emailAddress}
              </dd>
            </div>

            <div>
              <dt className="font-medium text-gray-700">Name</dt>
              <dd className="text-gray-900">
                {user.firstName} {user.lastName}
              </dd>
            </div>

            {/* Access public metadata */}
            {user.publicMetadata && Object.keys(user.publicMetadata).length > 0 && (
              <div>
                <dt className="font-medium text-gray-700">Metadata</dt>
                <dd className="text-gray-900">
                  <pre className="text-sm bg-gray-100 p-2 rounded">
                    {JSON.stringify(user.publicMetadata, null, 2)}
                  </pre>
                </dd>
              </div>
            )}
          </dl>
        </div>

        {/* Example: Call protected API */}
        <ProtectedAPIExample getToken={getToken} />

        {/* Custom sign out button */}
        <button
          onClick={() => signOut()}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Sign Out
        </button>
      </div>
    </div>
  )
}

/**
 * Example Component: Calling Protected API
 */
function ProtectedAPIExample({ getToken }: { getToken: () => Promise<string | null> }) {
  const [data, setData] = React.useState<any>(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  const fetchProtectedData = async () => {
    setLoading(true)
    setError(null)

    try {
      // Get fresh session token (auto-refreshes)
      const token = await getToken()

      if (!token) {
        throw new Error('No session token available')
      }

      // Call your API with Authorization header
      const response = await fetch('https://your-worker.workers.dev/api/protected', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const result = await response.json()
      setData(result)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4">Protected API Call</h2>

      <button
        onClick={fetchProtectedData}
        disabled={loading}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {loading ? 'Loading...' : 'Fetch Protected Data'}
      </button>

      {error && (
        <div className="mt-4 p-4 bg-red-50 text-red-700 rounded">
          Error: {error}
        </div>
      )}

      {data && (
        <div className="mt-4">
          <pre className="text-sm bg-gray-100 p-4 rounded overflow-auto">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

export default App

/**
 * Troubleshooting:
 *
 * 1. "Missing Publishable Key" error?
 *    - Check .env.local has VITE_CLERK_PUBLISHABLE_KEY
 *    - Restart dev server after adding env var
 *
 * 2. Flash of unauthenticated content?
 *    - Always check isLoaded before rendering
 *    - Show loading state while isLoaded is false
 *
 * 3. Token not working with API?
 *    - Ensure getToken() is called fresh (don't cache)
 *    - Check Authorization header format: "Bearer <token>"
 *    - Verify API is using @clerk/backend to verify token
 */
