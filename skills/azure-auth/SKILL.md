---
name: azure-auth
description: |
  Microsoft Entra ID (Azure AD) authentication for React SPAs with MSAL.js and Cloudflare Workers JWT validation using jose library. Full-stack pattern with Authorization Code Flow + PKCE. Prevents 8 documented errors.

  Use when: implementing Microsoft SSO, troubleshooting AADSTS50058 loops, AADSTS700084 refresh token errors, React Router redirects, setActiveAccount re-render issues, or validating Entra ID tokens in Workers.
user-invocable: true
---

# Azure Auth - Microsoft Entra ID for React + Cloudflare Workers

**Package Versions**: @azure/msal-react@5.0.2, @azure/msal-browser@5.0.2, jose@6.1.3
**Breaking Changes**: MSAL v4→v5 migration (January 2026), Azure AD B2C sunset (May 2025 - new signups blocked, existing until 2030), ADAL retirement (Sept 2025 - complete)
**Last Updated**: 2026-01-21

---

## Architecture Overview

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────────┐
│   React SPA         │────▶│  Microsoft Entra ID  │────▶│  Cloudflare Worker  │
│   @azure/msal-react │     │  (login.microsoft)   │     │  jose JWT validation│
└─────────────────────┘     └──────────────────────┘     └─────────────────────┘
        │                                                          │
        │  Authorization Code + PKCE                               │
        │  (access_token, id_token)                                │
        └──────────────────────────────────────────────────────────┘
                    Bearer token in Authorization header
```

**Key Constraint**: MSAL.js does NOT work in Cloudflare Workers (relies on browser/Node.js APIs). Use jose library for backend token validation.

---

## Quick Start

### 1. Install Dependencies

```bash
# Frontend (React SPA)
npm install @azure/msal-react @azure/msal-browser

# Backend (Cloudflare Workers)
npm install jose
```

### 2. Azure Portal Setup

1. Go to **Microsoft Entra ID** → **App registrations** → **New registration**
2. Set **Redirect URI** to `http://localhost:5173` (SPA type)
3. Note the **Application (client) ID** and **Directory (tenant) ID**
4. Under **Authentication**:
   - Enable **Access tokens** and **ID tokens**
   - Add production redirect URI
5. Under **API permissions**:
   - Add `User.Read` (Microsoft Graph)
   - Grant admin consent if required

---

## Frontend: MSAL React Setup

### Configuration (src/auth/msal-config.ts)

```typescript
import { Configuration, LogLevel } from "@azure/msal-browser";

export const msalConfig: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_AZURE_CLIENT_ID,
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_AZURE_TENANT_ID}`,
    redirectUri: window.location.origin,
    postLogoutRedirectUri: window.location.origin,
    navigateToLoginRequestUrl: true,
  },
  cache: {
    cacheLocation: "localStorage", // or "sessionStorage"
    storeAuthStateInCookie: true, // Required for Safari/Edge issues
  },
  system: {
    loggerOptions: {
      logLevel: LogLevel.Warning,
      loggerCallback: (level, message) => {
        if (level === LogLevel.Error) console.error(message);
      },
    },
  },
};

// Scopes for token requests
export const loginRequest = {
  scopes: ["User.Read", "openid", "profile", "email"],
};

// Scopes for API calls (add your API scope here)
export const apiRequest = {
  scopes: [`api://${import.meta.env.VITE_AZURE_CLIENT_ID}/access_as_user`],
};
```

### MsalProvider Setup (src/main.tsx)

```typescript
import React from "react";
import ReactDOM from "react-dom/client";
import { PublicClientApplication, EventType } from "@azure/msal-browser";
import { MsalProvider } from "@azure/msal-react";
import { msalConfig } from "./auth/msal-config";
import App from "./App";

// CRITICAL: Initialize MSAL outside component tree to prevent re-instantiation
const msalInstance = new PublicClientApplication(msalConfig);

// Handle redirect promise on page load
msalInstance.initialize().then(() => {
  // Set active account after redirect
  // IMPORTANT: Use getAllAccounts() (returns array), NOT getActiveAccount() (returns single account or null)
  const accounts = msalInstance.getAllAccounts();
  if (accounts.length > 0) {
    msalInstance.setActiveAccount(accounts[0]);
  }

  // Listen for sign-in events
  msalInstance.addEventCallback((event) => {
    if (event.eventType === EventType.LOGIN_SUCCESS && event.payload) {
      const account = (event.payload as { account: any }).account;
      msalInstance.setActiveAccount(account);
    }
  });

  ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
      <MsalProvider instance={msalInstance}>
        <App />
      </MsalProvider>
    </React.StrictMode>
  );
});
```

### Protected Route Component

```typescript
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { InteractionStatus } from "@azure/msal-browser";
import { loginRequest } from "./msal-config";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { instance, inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();

  // Wait for MSAL to finish any in-progress operations
  if (inProgress !== InteractionStatus.None) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    // Trigger login redirect
    instance.loginRedirect(loginRequest);
    return <div>Redirecting to login...</div>;
  }

  return <>{children}</>;
}
```

### Acquiring Tokens for API Calls

```typescript
import { useMsal } from "@azure/msal-react";
import { InteractionRequiredAuthError } from "@azure/msal-browser";
import { apiRequest } from "./msal-config";

export function useApiToken() {
  const { instance, accounts } = useMsal();

  async function getAccessToken(): Promise<string | null> {
    if (accounts.length === 0) return null;

    const request = {
      ...apiRequest,
      account: accounts[0],
    };

    try {
      // Try silent token acquisition first
      const response = await instance.acquireTokenSilent(request);
      return response.accessToken;
    } catch (error) {
      if (error instanceof InteractionRequiredAuthError) {
        // Silent acquisition failed, need interactive login
        // This handles expired refresh tokens (AADSTS700084)
        await instance.acquireTokenRedirect(request);
        return null;
      }
      throw error;
    }
  }

  return { getAccessToken };
}
```

---

## Backend: Cloudflare Workers JWT Validation

### Why jose Instead of MSAL

MSAL.js relies on browser APIs (localStorage, sessionStorage) and Node.js crypto modules that don't exist in Cloudflare Workers' V8 isolate runtime. The jose library is pure JavaScript and works perfectly in Workers.

### JWT Validation (src/auth/validate-token.ts)

```typescript
import * as jose from "jose";

interface EntraTokenPayload {
  aud: string;       // Audience (your client ID or API URI)
  iss: string;       // Issuer (https://login.microsoftonline.com/{tenant}/v2.0)
  sub: string;       // Subject (user's unique ID)
  oid: string;       // Object ID (user's Azure AD object ID)
  preferred_username: string;
  name: string;
  email?: string;
  roles?: string[];  // App roles if configured
  scp?: string;      // Scopes (space-separated)
}

// Cache JWKS to avoid fetching on every request
let jwksCache: jose.JWTVerifyGetKey | null = null;
let jwksCacheTime = 0;
const JWKS_CACHE_DURATION = 3600000; // 1 hour

async function getJWKS(tenantId: string): Promise<jose.JWTVerifyGetKey> {
  const now = Date.now();

  if (jwksCache && now - jwksCacheTime < JWKS_CACHE_DURATION) {
    return jwksCache;
  }

  // CRITICAL: Azure AD JWKS is NOT at .well-known/jwks.json
  // Must fetch from openid-configuration first
  const configUrl = `https://login.microsoftonline.com/${tenantId}/v2.0/.well-known/openid-configuration`;
  const configResponse = await fetch(configUrl);
  const config = await configResponse.json() as { jwks_uri: string };

  // Now fetch JWKS from the correct URL
  jwksCache = jose.createRemoteJWKSet(new URL(config.jwks_uri));
  jwksCacheTime = now;

  return jwksCache;
}

export async function validateEntraToken(
  token: string,
  env: {
    AZURE_TENANT_ID: string;
    AZURE_CLIENT_ID: string;
  }
): Promise<EntraTokenPayload | null> {
  try {
    const jwks = await getJWKS(env.AZURE_TENANT_ID);

    const { payload } = await jose.jwtVerify(token, jwks, {
      issuer: `https://login.microsoftonline.com/${env.AZURE_TENANT_ID}/v2.0`,
      audience: env.AZURE_CLIENT_ID, // or your API URI: api://{client_id}
    });

    return payload as unknown as EntraTokenPayload;
  } catch (error) {
    console.error("Token validation failed:", error);
    return null;
  }
}
```

### Worker Middleware Pattern

```typescript
import { validateEntraToken } from "./auth/validate-token";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // Skip auth for public routes
    const url = new URL(request.url);
    if (url.pathname === "/" || url.pathname.startsWith("/public")) {
      return handlePublicRoute(request, env);
    }

    // Extract Bearer token
    const authHeader = request.headers.get("Authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return new Response(JSON.stringify({ error: "Missing authorization" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }

    const token = authHeader.slice(7);
    const user = await validateEntraToken(token, env);

    if (!user) {
      return new Response(JSON.stringify({ error: "Invalid token" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Add user to request context
    const requestWithUser = new Request(request);
    // Pass user info downstream (e.g., via headers or context)

    return handleProtectedRoute(request, env, user);
  },
};
```

---

## Common Errors & Fixes

### 1. AADSTS50058 - Silent Sign-In Loop

**Error**: "A silent sign-in request was sent but no user is signed in"

**Cause**: `acquireTokenSilent` called when no cached user exists.

**Fix**:
```typescript
// Always check for accounts before silent acquisition
const accounts = instance.getAllAccounts();
if (accounts.length === 0) {
  // No cached user, trigger interactive login
  await instance.loginRedirect(loginRequest);
  return;
}
```

### 2. AADSTS700084 - Refresh Token Expired

**Error**: "The refresh token was issued to a single page app (SPA), and therefore has a fixed, limited lifetime of 1.00:00:00"

**Cause**: SPA refresh tokens expire after 24 hours. Cannot be extended.

**Fix**:
```typescript
try {
  const response = await instance.acquireTokenSilent(request);
} catch (error) {
  if (error instanceof InteractionRequiredAuthError) {
    // Refresh token expired, need fresh login
    await instance.acquireTokenRedirect(request);
  }
}
```

### 3. React Router v6 Redirect Loop

**Error**: Infinite redirects between login page and app.

**Cause**: React Router v6 may strip the hash fragment containing auth response.

**Fix**: Use custom NavigationClient:
```typescript
import { NavigationClient } from "@azure/msal-browser";
import { useNavigate } from "react-router-dom";

class CustomNavigationClient extends NavigationClient {
  private navigate: ReturnType<typeof useNavigate>;

  constructor(navigate: ReturnType<typeof useNavigate>) {
    super();
    this.navigate = navigate;
  }

  async navigateInternal(url: string, options: { noHistory: boolean }) {
    const relativePath = url.replace(window.location.origin, "");
    if (options.noHistory) {
      this.navigate(relativePath, { replace: true });
    } else {
      this.navigate(relativePath);
    }
    return false; // Prevent MSAL from doing its own navigation
  }
}

// In your App component:
const navigate = useNavigate();
useEffect(() => {
  const navigationClient = new CustomNavigationClient(navigate);
  instance.setNavigationClient(navigationClient);
}, [instance, navigate]);
```

### 4. NextJS Dynamic Route Error

**Error**: `no_cached_authority_error` in dynamic routes.

**Cause**: MSAL instance not properly initialized before component renders.

**Fix**: Initialize MSAL in `_app.tsx` before any routing:
```typescript
// pages/_app.tsx
import { PublicClientApplication } from "@azure/msal-browser";
import { MsalProvider } from "@azure/msal-react";
import { msalConfig } from "../auth/msal-config";

// Initialize outside component
const msalInstance = new PublicClientApplication(msalConfig);

// Ensure initialization completes before render
export default function App({ Component, pageProps }) {
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    msalInstance.initialize().then(() => setIsInitialized(true));
  }, []);

  if (!isInitialized) return <div>Loading...</div>;

  return (
    <MsalProvider instance={msalInstance}>
      <Component {...pageProps} />
    </MsalProvider>
  );
}
```

### 5. Safari/Edge Cookie Issues

**Error**: Auth state lost, infinite loop on Safari or Edge. On iOS 18 Safari specifically, silent token refresh fails with AADSTS50058 even when third-party cookies are enabled.

**Source**: [GitHub Issue #7384](https://github.com/AzureAD/microsoft-authentication-library-for-js/issues/7384)

**Cause**: These browsers have stricter cookie policies affecting session storage. iOS 18 Safari doesn't store the required session cookies for login.microsoftonline.com, even with third-party cookies explicitly allowed in settings.

**Testing Note**: Works in Chrome on iOS 18, but fails in Safari on iOS 18.

**Fix**: Enable cookie storage in MSAL config:
```typescript
cache: {
  cacheLocation: "localStorage",
  storeAuthStateInCookie: true, // REQUIRED for Safari/Edge
}
```

**iOS 18 Safari Limitation**: If users still experience issues on iOS 18 Safari after enabling cookie storage, this is a known browser limitation with no current workaround. Recommend using Chrome on iOS or desktop browser.

### 6. JWKS URL Not Found (Workers)

**Error**: Failed to fetch JWKS from `.well-known/jwks.json`.

**Cause**: Azure AD doesn't serve JWKS at the standard OpenID Connect path.

**Fix**: Fetch `openid-configuration` first, then use `jwks_uri`:
```typescript
// WRONG - Azure AD doesn't use this path
const jwks = createRemoteJWKSet(
  new URL(`https://login.microsoftonline.com/${tenantId}/.well-known/jwks.json`)
);

// CORRECT - Fetch config first
const config = await fetch(
  `https://login.microsoftonline.com/${tenantId}/v2.0/.well-known/openid-configuration`
).then(r => r.json());
const jwks = createRemoteJWKSet(new URL(config.jwks_uri));
```

### 7. React Router Loader State Conflict

**Error**: React warning about updating state during render when using `acquireTokenSilent` in React Router loaders.

**Source**: [GitHub Issue #7068](https://github.com/AzureAD/microsoft-authentication-library-for-js/issues/7068)

**Cause**: Using the same `PublicClientApplication` instance in both the router loader and `MsalProvider` causes state updates during rendering.

**Fix**: Call `initialize()` again in the loader:
```typescript
const protectedLoader = async () => {
  await msalInstance.initialize(); // Prevents state conflict
  const response = await msalInstance.acquireTokenSilent(request);
  return { data };
};
```

### 8. setActiveAccount Doesn't Trigger Re-render (Community-sourced)

**Error**: Components using `useMsal()` don't update after calling `setActiveAccount()`.

**Source**: [GitHub Issue #6989](https://github.com/AzureAD/microsoft-authentication-library-for-js/issues/6989)

**Verified**: Multiple users confirmed in GitHub issue

**Cause**: `setActiveAccount()` updates the MSAL instance but doesn't notify React of the change.

**Fix**: Force re-render with state:
```typescript
const [accountKey, setAccountKey] = useState(0);

const switchAccount = (newAccount) => {
  msalInstance.setActiveAccount(newAccount);
  setAccountKey(prev => prev + 1); // Force update
};
```

---

## Multi-Tenant vs Single-Tenant

### Single Tenant (Recommended for Enterprise)

```typescript
authority: `https://login.microsoftonline.com/${TENANT_ID}`,
```

- Only users from your organization can sign in
- Token issuer: `https://login.microsoftonline.com/{tenant_id}/v2.0`

### Multi-Tenant

```typescript
authority: "https://login.microsoftonline.com/common",
// or for work/school accounts only:
authority: "https://login.microsoftonline.com/organizations",
```

- Users from any Azure AD tenant can sign in
- Token issuer varies by user's tenant
- **Backend validation must handle multiple issuers**:

```typescript
// Multi-tenant issuer validation
const tenantId = payload.tid; // Tenant ID from token
const expectedIssuer = `https://login.microsoftonline.com/${tenantId}/v2.0`;
if (payload.iss !== expectedIssuer) {
  throw new Error("Invalid issuer");
}
```

---

## Environment Variables

### Frontend (.env)

```bash
VITE_AZURE_CLIENT_ID=your-client-id-guid
VITE_AZURE_TENANT_ID=your-tenant-id-guid
```

### Backend (wrangler.jsonc)

```jsonc
{
  "name": "my-api",
  "vars": {
    "AZURE_TENANT_ID": "your-tenant-id-guid",
    "AZURE_CLIENT_ID": "your-client-id-guid"
  }
}
```

---

## Azure AD B2C Sunset

**Timeline**:
- **May 1, 2025**: Azure AD B2C no longer available for new customer signups
- **March 15, 2026**: Azure AD B2C P2 discontinued for all customers
- **May 2030**: Microsoft will continue supporting existing B2C customers with standard support

**Source**: [Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/2119363/migrating-existing-azure-ad-b2c-to-microsoft-entra)

**Existing B2C Customers**: Can continue using B2C until 2030, but should plan migration to Entra External ID.

**New Projects**: Use **Microsoft Entra External ID** for consumer/customer identity scenarios.

**Migration Status**: As of January 2026, automated migration tools are in testing phase. Manual migration guidance available at Microsoft Learn.

**Migration Path**:
- Different authority URL format (`{tenant}.ciamlogin.com` vs `{tenant}.b2clogin.com`)
- Updated SDK support (same MSAL libraries)
- New pricing model (consumption-based)
- Self-Service Password Reset (SSPR) approach available for user migration
- Seamless migration samples on GitHub (preview)

See: https://learn.microsoft.com/en-us/entra/external-id/
Migration Guide: https://learn.microsoft.com/en-us/entra/external-id/customers/how-to-migrate-users

---

## ADAL Retirement (Complete)

**Status**: Azure AD Authentication Library (ADAL) was retired on September 30, 2025. Apps using ADAL no longer receive security updates.

**If you're migrating from ADAL**:
1. ADAL → MSAL migration is required
2. ADAL used v1.0 endpoints; MSAL uses v2.0 endpoints
3. Token cache format differs - users must re-authenticate
4. Scopes replace "resources" in token requests

**Key Migration Changes**:
```typescript
// ADAL (deprecated) - resource-based
acquireToken({ resource: "https://graph.microsoft.com" })

// MSAL (current) - scope-based
acquireTokenSilent({ scopes: ["https://graph.microsoft.com/User.Read"] })
```

See: https://learn.microsoft.com/en-us/entra/msal/javascript/migration/msal-net-migration

---

## Resources

- [MSAL React Documentation](https://learn.microsoft.com/en-us/entra/msal/javascript/react/)
- [Microsoft Entra ID App Registration](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app)
- [MSAL.js GitHub Issues](https://github.com/AzureAD/microsoft-authentication-library-for-js/issues)
- [jose Library](https://github.com/panva/jose)
- [Cloudflare Workers + Azure AD Blog](https://hajekj.net/2021/11/12/cloudflare-workers-and-azure-ad/)
