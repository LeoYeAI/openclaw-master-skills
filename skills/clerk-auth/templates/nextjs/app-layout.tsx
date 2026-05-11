/**
 * Next.js App Router Layout with Clerk
 *
 * Place this in app/layout.tsx
 *
 * Dependencies:
 * - @clerk/nextjs@^6.33.3
 */

import { ClerkProvider } from '@clerk/nextjs'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'My App',
  description: 'Authenticated with Clerk',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className={inter.className}>{children}</body>
      </html>
    </ClerkProvider>
  )
}

/**
 * With Dark Mode Support (using next-themes):
 *
 * 1. Install: npm install next-themes
 * 2. Use this pattern:
 */
/*
import { ClerkProvider } from '@clerk/nextjs'
import { ThemeProvider } from 'next-themes'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
      <html lang="en" suppressHydrationWarning>
        <body>
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            {children}
          </ThemeProvider>
        </body>
      </html>
    </ClerkProvider>
  )
}
*/

/**
 * With Clerk Appearance Customization:
 */
/*
import { ClerkProvider } from '@clerk/nextjs'
import { dark } from '@clerk/themes'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider
      appearance={{
        baseTheme: dark,
        variables: {
          colorPrimary: '#3b82f6',
          colorBackground: '#0f172a',
        },
        elements: {
          formButtonPrimary: 'bg-blue-500 hover:bg-blue-600',
          card: 'shadow-xl',
        },
      }}
    >
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  )
}
*/
