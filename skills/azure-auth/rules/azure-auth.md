# Azure Auth Correction Rules

Rules for Microsoft Entra ID (Azure AD) authentication with MSAL React and Cloudflare Workers.

## MSAL Configuration

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `cacheLocation: "sessionStorage"` without cookie flag | Add `storeAuthStateInCookie: true` for Safari/Edge |
| Creating MSAL instance inside component | Create outside component tree to prevent re-instantiation |
| Using implicit flow | Authorization Code Flow with PKCE (MSAL v3 default) |
| `authority: "https://login.microsoftonline.com/common"` for enterprise | Use tenant-specific authority for single-tenant apps |

## Token Acquisition

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `acquireTokenSilent` without checking accounts | Check `getAllAccounts().length > 0` first |
| Catching generic error on acquireTokenSilent | Catch `InteractionRequiredAuthError` specifically |
| Ignoring AADSTS700084 | Handle as "refresh token expired, need interactive login" |
| Calling interactive method without checking inProgress | Check `inProgress !== InteractionStatus.None` first |

## Cloudflare Workers JWT Validation

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Using MSAL.js in Workers | Use jose library (MSAL doesn't work in Workers) |
| Fetching JWKS from `.well-known/jwks.json` | Fetch from `openid-configuration` first, use `jwks_uri` |
| Hardcoding JWKS public key | Fetch dynamically and cache (keys rotate) |
| Single issuer validation for multi-tenant | Validate issuer matches `tid` claim from token |

## React Router Integration

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Using `MsalAuthenticationTemplate` on redirect URI page | Don't render auth components on redirect page |
| Ignoring hash fragment in React Router v6 | Implement custom `NavigationClient` |
| Calling `loginRedirect` in render | Use `useEffect` or event handler |

## Azure Portal Configuration

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| "Web" platform for SPA | "Single-page application" platform type |
| Implicit grant only | Enable "Access tokens" and "ID tokens" under Authentication |
| Skipping redirect URI for localhost | Add `http://localhost:5173` (or your dev port) |

## Common AADSTS Errors

| Error Code | Meaning | Fix |
|------------|---------|-----|
| AADSTS50058 | Silent sign-in, no user | Check for cached accounts before silent acquisition |
| AADSTS700084 | Refresh token expired (24hr SPA limit) | Trigger interactive login |
| AADSTS65001 | Consent not granted | Request admin consent or prompt user |
| AADSTS90102 | Redirect URI mismatch | Verify URI in Azure Portal matches exactly |
| AADSTS50011 | Reply URL doesn't match | Check trailing slashes, http vs https |

## Environment Variables

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Hardcoding client ID | Use `import.meta.env.VITE_AZURE_CLIENT_ID` |
| Exposing tenant ID in git | Store in `.env` (gitignored) or CI/CD secrets |
| Using `process.env` in Vite | Use `import.meta.env` for Vite projects |

## Azure AD B2C (Sunset May 2025)

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Setting up new Azure AD B2C | Use Microsoft Entra External ID for consumer apps |
| B2C authority URL for new projects | Entra External ID authority format |
