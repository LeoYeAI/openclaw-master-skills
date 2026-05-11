# Setup Clerk Auth

Add Clerk authentication to an existing React or Next.js project.

---

## Your Task

Follow these steps to configure Clerk authentication.

### 1. Check Prerequisites

Verify the project has:
- React 18+ or Next.js 14+
- A Clerk account (clerk.com)

### 2. Install Clerk

**For React + Vite:**
```bash
npm install @clerk/clerk-react
```

**For Next.js:**
```bash
npm install @clerk/nextjs
```

### 3. Get Clerk Keys

From Clerk Dashboard (dashboard.clerk.com):
1. Select or create application
2. Go to API Keys
3. Copy `CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY`

### 4. Configure Environment Variables

**For React (`.env.local`):**
```bash
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
```

**For Next.js (`.env.local`):**
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

### 5. Add Clerk Provider

**For React (`src/main.tsx`):**

```typescript
import { ClerkProvider } from '@clerk/clerk-react';

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!PUBLISHABLE_KEY) {
  throw new Error('Missing Clerk Publishable Key');
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
      <App />
    </ClerkProvider>
  </React.StrictMode>
);
```

**For Next.js (`src/app/layout.tsx`):**

```typescript
import { ClerkProvider } from '@clerk/nextjs';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
```

### 6. Add Middleware (Next.js only)

Create `src/middleware.ts` (Next.js 15) or `src/proxy.ts` (Next.js 16):

```typescript
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';

const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/api/public(.*)',
]);

export default clerkMiddleware(async (auth, request) => {
  if (!isPublicRoute(request)) {
    await auth.protect();
  }
});

export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
};
```

### 7. Create Auth Pages

**For React (using Clerk components):**

```typescript
// src/pages/sign-in.tsx
import { SignIn } from '@clerk/clerk-react';

export default function SignInPage() {
  return <SignIn routing="path" path="/sign-in" />;
}

// src/pages/sign-up.tsx
import { SignUp } from '@clerk/clerk-react';

export default function SignUpPage() {
  return <SignUp routing="path" path="/sign-up" />;
}
```

**For Next.js:**
```bash
# Creates src/app/sign-in/[[...sign-in]]/page.tsx
# Creates src/app/sign-up/[[...sign-up]]/page.tsx
```

### 8. Add User Button

```typescript
import { UserButton, SignedIn, SignedOut, SignInButton } from '@clerk/clerk-react';

function Header() {
  return (
    <header>
      <SignedIn>
        <UserButton afterSignOutUrl="/" />
      </SignedIn>
      <SignedOut>
        <SignInButton mode="modal" />
      </SignedOut>
    </header>
  );
}
```

### 9. Configure Clerk Dashboard

1. Set Redirect URLs:
   - Sign-in: `/sign-in`
   - Sign-up: `/sign-up`
   - After sign-in: `/dashboard`
   - After sign-up: `/dashboard`

2. Enable desired auth methods (Email, Google, GitHub, etc.)

### 10. Provide Next Steps

```
✅ Clerk authentication configured!

📁 Added:
   - ClerkProvider in app entry
   - Middleware for protected routes (Next.js)
   - Environment variables

🔐 Auth Components:
   <SignIn />        - Full sign-in page
   <SignUp />        - Full sign-up page
   <UserButton />    - User avatar + menu
   <SignInButton />  - Sign-in trigger
   <SignedIn />      - Render when authenticated
   <SignedOut />     - Render when not authenticated

🪝 Hooks:
   useUser()         - Get current user
   useAuth()         - Get auth state
   useClerk()        - Full Clerk instance

📚 Skill loaded: clerk-auth
   - API version 2025-04-10 (v2 tokens)
   - JWT template configuration
   - Custom claims support
```

---

## API Version Note

Clerk deprecated JWT v1 tokens on April 14, 2025. Ensure you're using:
- `@clerk/nextjs@6.x` or `@clerk/clerk-react@5.x`
- API version `2025-04-10` or later
