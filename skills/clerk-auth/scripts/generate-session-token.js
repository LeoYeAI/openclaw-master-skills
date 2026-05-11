#!/usr/bin/env node

/**
 * Clerk Session Token Generator
 *
 * Generates valid session tokens for testing Clerk authentication.
 * Session tokens are valid for 60 seconds and must be refreshed regularly.
 *
 * Usage:
 *   node generate-session-token.js
 *   node generate-session-token.js --create-user
 *   node generate-session-token.js --user-id user_abc123
 *   node generate-session-token.js --refresh
 *
 * Environment Variables:
 *   CLERK_SECRET_KEY - Your Clerk secret key (required)
 *
 * @see https://clerk.com/docs/guides/development/testing/overview
 */

const https = require('https')

// Configuration
const CLERK_SECRET_KEY = process.env.CLERK_SECRET_KEY
const API_BASE = 'https://api.clerk.com/v1'

// Parse CLI arguments
const args = process.argv.slice(2)
const shouldCreateUser = args.includes('--create-user')
const shouldRefresh = args.includes('--refresh')
const userIdArg = args.find(arg => arg.startsWith('--user-id='))
const providedUserId = userIdArg ? userIdArg.split('=')[1] : null

// Validate secret key
if (!CLERK_SECRET_KEY) {
  console.error('❌ Error: CLERK_SECRET_KEY environment variable is required')
  console.error('\nUsage: CLERK_SECRET_KEY=sk_test_... node generate-session-token.js')
  process.exit(1)
}

// Make HTTPS request
function makeRequest(path, method = 'GET', data = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(`${API_BASE}${path}`)

    const options = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      method,
      headers: {
        'Authorization': `Bearer ${CLERK_SECRET_KEY}`,
        'Content-Type': 'application/json',
      },
    }

    const req = https.request(options, (res) => {
      let body = ''
      res.on('data', (chunk) => body += chunk)
      res.on('end', () => {
        try {
          const json = JSON.parse(body)

          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(json)
          } else {
            reject({
              statusCode: res.statusCode,
              error: json,
            })
          }
        } catch (err) {
          reject({
            statusCode: res.statusCode,
            error: body,
            parseError: err.message,
          })
        }
      })
    })

    req.on('error', reject)

    if (data) {
      req.write(JSON.stringify(data))
    }

    req.end()
  })
}

// Create test user
async function createUser() {
  console.log('📝 Creating test user...')

  const email = `test+clerk_test_${Date.now()}@example.com`
  const password = 'TestPassword123!'

  try {
    const user = await makeRequest('/users', 'POST', {
      email_address: [email],
      password: password,
      skip_password_checks: true,
    })

    console.log('✅ User created:')
    console.log(`   User ID: ${user.id}`)
    console.log(`   Email: ${email}`)
    console.log(`   Password: ${password}`)

    return user.id
  } catch (err) {
    console.error('❌ Failed to create user:', err.error)
    throw err
  }
}

// Get existing user (first user in instance)
async function getExistingUser() {
  console.log('🔍 Finding existing user...')

  try {
    const response = await makeRequest('/users?limit=1')

    if (response.data && response.data.length > 0) {
      const user = response.data[0]
      console.log(`✅ Found user: ${user.id}`)
      return user.id
    } else {
      console.log('⚠️  No users found. Use --create-user to create one.')
      return null
    }
  } catch (err) {
    console.error('❌ Failed to get user:', err.error)
    throw err
  }
}

// Create session for user
async function createSession(userId) {
  console.log(`🔐 Creating session for user ${userId}...`)

  try {
    const session = await makeRequest('/sessions', 'POST', {
      user_id: userId,
    })

    console.log(`✅ Session created: ${session.id}`)
    return session.id
  } catch (err) {
    console.error('❌ Failed to create session:', err.error)
    throw err
  }
}

// Create session token
async function createSessionToken(sessionId) {
  try {
    const response = await makeRequest(`/sessions/${sessionId}/tokens`, 'POST')
    return response.jwt
  } catch (err) {
    console.error('❌ Failed to create session token:', err.error)
    throw err
  }
}

// Refresh session token (same as create)
async function refreshSessionToken(sessionId) {
  console.log('🔄 Refreshing session token...')
  const token = await createSessionToken(sessionId)
  console.log('✅ Token refreshed')
  return token
}

// Main function
async function main() {
  console.log('🎫 Clerk Session Token Generator\n')

  try {
    // Step 1: Get or create user
    let userId = providedUserId

    if (!userId) {
      if (shouldCreateUser) {
        userId = await createUser()
      } else {
        userId = await getExistingUser()
      }
    } else {
      console.log(`📌 Using provided user ID: ${userId}`)
    }

    if (!userId) {
      console.log('\n💡 Tip: Run with --create-user to create a test user')
      process.exit(1)
    }

    // Step 2: Create session
    const sessionId = await createSession(userId)

    // Step 3: Create token
    console.log('🎫 Generating session token...')
    const token = await createSessionToken(sessionId)

    console.log('\n✅ Session Token Generated!\n')
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
    console.log('Token (valid for 60 seconds):')
    console.log(token)
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')

    console.log('📋 Usage in API requests:\n')
    console.log('curl https://yourdomain.com/api/protected \\')
    console.log(`  -H "Authorization: Bearer ${token.substring(0, 50)}..."\n`)

    // Step 4: Refresh mode (optional)
    if (shouldRefresh) {
      console.log('🔄 Refresh mode enabled. Token will refresh every 50 seconds.')
      console.log('Press Ctrl+C to stop.\n')

      // Refresh every 50 seconds
      setInterval(async () => {
        try {
          const newToken = await refreshSessionToken(sessionId)
          console.log(`\n🎫 New Token: ${newToken}\n`)
        } catch (err) {
          console.error('❌ Failed to refresh token:', err)
          process.exit(1)
        }
      }, 50000)
    } else {
      console.log('💡 Tip: Add --refresh flag to auto-refresh token every 50 seconds')
      console.log(`💡 Tip: Reuse this session with --user-id=${userId}`)
    }

  } catch (err) {
    console.error('\n❌ Error:', err)
    process.exit(1)
  }
}

// Run main function
main()
