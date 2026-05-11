/**
 * React + Vite Entry Point with Clerk
 *
 * Place this in src/main.tsx
 *
 * Dependencies:
 * - @clerk/clerk-react@^5.51.0
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import { ClerkProvider } from '@clerk/clerk-react'
import App from './App.tsx'
import './index.css'

// Get publishable key from environment
// CRITICAL: Must use VITE_ prefix for Vite to expose to client
const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!PUBLISHABLE_KEY) {
  throw new Error('Missing VITE_CLERK_PUBLISHABLE_KEY in .env.local')
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
      <App />
    </ClerkProvider>
  </React.StrictMode>,
)

/**
 * With Dark Mode Support (using custom theme):
 */
/*
import { ClerkProvider } from '@clerk/clerk-react'
import { dark } from '@clerk/themes'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ClerkProvider
      publishableKey={PUBLISHABLE_KEY}
      appearance={{
        baseTheme: dark,
        variables: {
          colorPrimary: '#3b82f6',
        },
      }}
    >
      <App />
    </ClerkProvider>
  </React.StrictMode>,
)
*/

/**
 * Environment Variables:
 *
 * Create .env.local with:
 * VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
 *
 * CRITICAL:
 * - Must use VITE_ prefix (Vite requirement)
 * - Never commit .env.local to version control
 * - Use different keys for development and production
 */
