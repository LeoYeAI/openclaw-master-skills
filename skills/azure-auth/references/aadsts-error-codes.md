# AADSTS Error Codes Reference

Common Azure AD Security Token Service error codes and how to resolve them.

## Authentication Flow Errors

### AADSTS50058 - Silent Sign-In Failed

**Message**: "A silent sign-in request was sent but no user is signed in."

**Cause**: Called `acquireTokenSilent` when no user session exists in cache.

**Fix**:
```typescript
const accounts = instance.getAllAccounts();
if (accounts.length === 0) {
  // No cached user - must do interactive login first
  await instance.loginRedirect(loginRequest);
  return;
}

// Now safe to try silent acquisition
const response = await instance.acquireTokenSilent({
  ...apiRequest,
  account: accounts[0],
});
```

---

### AADSTS700084 - Refresh Token Expired

**Message**: "The refresh token was issued to a single page app (SPA), and therefore has a fixed, limited lifetime of 1.00:00:00, which cannot be extended."

**Cause**: SPA refresh tokens have a 24-hour lifetime that cannot be extended.

**Fix**:
```typescript
try {
  const response = await instance.acquireTokenSilent(request);
  return response.accessToken;
} catch (error) {
  if (error instanceof InteractionRequiredAuthError) {
    // Refresh token expired, need fresh login
    await instance.acquireTokenRedirect(request);
  }
  throw error;
}
```

**Note**: This is by design for SPAs. For longer-lived sessions, consider using a backend that can hold refresh tokens securely.

---

### AADSTS65001 - Consent Not Granted

**Message**: "The user or administrator has not consented to use the application."

**Cause**: Required permissions haven't been consented to by user or admin.

**Fix Options**:

1. **User consent** - User clicks "Accept" on consent prompt
2. **Admin consent** - Admin grants consent for entire organization
3. **Prompt for consent**:
```typescript
await instance.loginRedirect({
  ...loginRequest,
  prompt: "consent", // Force consent dialog
});
```

---

### AADSTS90102 - Redirect URI Mismatch

**Message**: "redirect_uri value must match the redirect URI configured for the application."

**Cause**: The redirect URI in code doesn't exactly match Azure Portal configuration.

**Fix**:
1. Check Azure Portal > App registrations > Authentication > Redirect URIs
2. Ensure exact match including:
   - Protocol (http vs https)
   - Port number (localhost:5173 vs localhost:3000)
   - Trailing slash (with vs without)
3. For development, add `http://localhost:5173`

---

### AADSTS50011 - Reply URL Mismatch

**Message**: "The reply URL specified in the request does not match the reply URLs configured for the application."

**Cause**: Similar to AADSTS90102 - redirect URI doesn't match.

**Common issues**:
- Trailing slash mismatch: `http://localhost:5173` vs `http://localhost:5173/`
- Protocol mismatch: `http://` vs `https://`
- Wrong port in development

---

### AADSTS50076 - MFA Required

**Message**: "Due to a configuration change made by your administrator, you must use multi-factor authentication."

**Cause**: Conditional Access policy requires MFA but user hasn't completed it.

**Fix**: This requires user action - complete MFA challenge. Your app should handle this gracefully:
```typescript
if (error.errorCode === "50076") {
  // Trigger interactive login which will show MFA prompt
  await instance.acquireTokenRedirect(request);
}
```

---

### AADSTS50105 - User Not Assigned

**Message**: "The signed in user is not assigned to a role for the application."

**Cause**: Enterprise app requires user assignment, but user isn't assigned.

**Fix**:
1. Azure Portal > Enterprise applications > Your app
2. Properties > "Assignment required?" - set to No, or
3. Users and groups > Add user/group assignment

---

## Token Validation Errors

### AADSTS500011 - Resource Not Found

**Message**: "The resource principal named [name] was not found in the tenant."

**Cause**: The API URI or scope doesn't exist in the tenant.

**Fix**:
1. Verify scope format: `api://{client-id}/{scope-name}`
2. Check App Registration > Expose an API > Scopes
3. Ensure API is in the same tenant or configured for multi-tenant

---

### AADSTS700016 - Application Not Found

**Message**: "Application with identifier '[app-id]' was not found in the directory."

**Cause**: Client ID doesn't exist in the specified tenant.

**Fix**:
1. Verify client ID is correct
2. Check tenant ID matches where app is registered
3. For multi-tenant apps, ensure "Accounts in any organizational directory" is selected

---

### AADSTS7000218 - PKCE Required

**Message**: "The request body must contain the following parameter: 'code_challenge'."

**Cause**: App is configured for PKCE but request doesn't include code challenge.

**Fix**: MSAL v3+ uses PKCE by default. If you see this error:
1. Ensure you're using @azure/msal-browser v2+ or @azure/msal-react v2+
2. Don't override the auth flow configuration

---

## Session/Cache Errors

### interaction_in_progress

**Message**: "Interaction is currently in progress. Please ensure that this interaction has been completed before calling an interactive API."

**Cause**: Called an interactive method while another is in progress.

**Fix**:
```typescript
import { InteractionStatus } from "@azure/msal-browser";

function MyComponent() {
  const { inProgress } = useMsal();

  const handleLogin = async () => {
    // Check if an interaction is already in progress
    if (inProgress !== InteractionStatus.None) {
      console.log("Waiting for current interaction to complete...");
      return;
    }

    await instance.loginRedirect(loginRequest);
  };
}
```

---

### no_cached_authority_error

**Message**: "No cached authority error."

**Cause**: MSAL couldn't find cached authority metadata, common with NextJS dynamic routes.

**Fix**:
```typescript
// Ensure MSAL is initialized before any routing
// In _app.tsx:
const [isReady, setIsReady] = useState(false);

useEffect(() => {
  msalInstance.initialize().then(() => {
    // Handle redirect promise
    msalInstance.handleRedirectPromise().then(() => {
      setIsReady(true);
    });
  });
}, []);

if (!isReady) return <Loading />;
```

---

## Multi-Tenant Errors

### AADSTS50020 - User Account Not in Tenant

**Message**: "User account from identity provider does not exist in tenant."

**Cause**: User from external tenant trying to access single-tenant app.

**Fix Options**:
1. Configure app as multi-tenant in Azure Portal
2. Add user as guest in your tenant
3. Use `authority: "https://login.microsoftonline.com/common"` for multi-tenant

---

### AADSTS90072 - External User Not Allowed

**Message**: "The tenant doesn't allow external users."

**Cause**: B2B guest access is disabled in the target tenant.

**Fix**: Tenant admin must enable guest access in Azure AD settings.

---

## Quick Reference Table

| Code | Short Name | Quick Fix |
|------|------------|-----------|
| AADSTS50058 | No user | Check `getAllAccounts()` before silent acquisition |
| AADSTS700084 | Refresh expired | Catch `InteractionRequiredAuthError`, redirect to login |
| AADSTS65001 | No consent | Prompt for consent or request admin consent |
| AADSTS90102 | URI mismatch | Match redirect URI exactly in Azure Portal |
| AADSTS50011 | Reply mismatch | Check trailing slashes and protocol |
| AADSTS50076 | MFA required | Let user complete MFA challenge |
| AADSTS50105 | Not assigned | Assign user in Enterprise Applications |
| AADSTS500011 | API not found | Verify scope URI format |
| AADSTS700016 | App not found | Check client ID and tenant ID |

---

## Resources

- [Azure AD Error Codes Reference](https://learn.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes)
- [MSAL.js Error Handling](https://learn.microsoft.com/en-us/entra/msal/javascript/browser/errors)
- [Troubleshooting Guide](https://learn.microsoft.com/en-us/azure/active-directory/develop/troubleshoot-publisher-verification)
