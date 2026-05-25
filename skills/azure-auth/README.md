# azure-auth

Microsoft Entra ID (Azure AD) authentication for React SPAs + Cloudflare Workers backend.

## Auto-Trigger Keywords

This skill activates when you mention:

### Technologies
- Azure AD, Azure Active Directory, Microsoft Entra ID, Entra ID
- MSAL, MSAL.js, msal-react, msal-browser, @azure/msal-react, @azure/msal-browser
- Microsoft authentication, Microsoft SSO, Microsoft login
- Azure B2C, Entra External ID

### Use Cases
- Microsoft SSO, Azure SSO, corporate SSO, enterprise SSO
- Office 365 login, Microsoft 365 authentication
- Azure AD token validation, Entra token validation
- JWT validation Azure, validate Azure token
- JWKS Azure, Azure AD JWKS

### Errors
- AADSTS50058, AADSTS700084, AADSTS65001, AADSTS90102
- no_cached_authority_error
- interaction_in_progress
- redirect loop MSAL, infinite loop MSAL
- acquireTokenSilent failed
- refresh token expired SPA

### Patterns
- Azure AD React, MSAL React setup
- Azure AD Cloudflare Workers
- MsalProvider, PublicClientApplication
- Authorization Code Flow PKCE Azure
- Multi-tenant Azure AD

## What This Skill Provides

1. **MSAL React Setup** - Configuration, provider, hooks
2. **Protected Routes** - Auth-gated components with proper loading states
3. **Token Acquisition** - Silent + interactive fallback patterns
4. **Workers JWT Validation** - jose-based validation (MSAL doesn't work in Workers)
5. **Error Prevention** - AADSTS codes, redirect loops, JWKS quirks
6. **Multi-Tenant Support** - Single vs multi-tenant patterns

## Key Files

- `SKILL.md` - Complete documentation
- `templates/msal-config.ts` - MSAL configuration
- `templates/msal-provider.tsx` - React provider setup
- `templates/protected-route.tsx` - Auth-protected component wrapper
- `templates/workers-jwt-validation.ts` - Cloudflare Workers token validation
- `rules/azure-auth.md` - Correction rules for common mistakes
- `references/aadsts-error-codes.md` - Error code reference

## Critical Notes

1. **MSAL.js does NOT work in Cloudflare Workers** - Use jose library for backend
2. **Azure AD JWKS URL is non-standard** - Fetch from openid-configuration first
3. **SPA refresh tokens expire in 24 hours** - Handle InteractionRequiredAuthError
4. **storeAuthStateInCookie: true** - Required for Safari/Edge compatibility
5. **Azure AD B2C sunset (complete, May 2025)** - Use Entra External ID for new consumer apps
6. **ADAL retirement (complete, Sept 2025)** - Migrate from ADAL to MSAL; no more security updates

## Package Versions

```json
{
  "@azure/msal-react": "3.0.23",
  "@azure/msal-browser": "4.27.0",
  "jose": "5.9.6"
}
```
