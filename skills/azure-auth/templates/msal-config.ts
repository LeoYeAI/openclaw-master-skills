/**
 * MSAL Configuration for Microsoft Entra ID (Azure AD)
 *
 * Replace environment variables with your Azure app registration values:
 * - VITE_AZURE_CLIENT_ID: Application (client) ID from Azure Portal
 * - VITE_AZURE_TENANT_ID: Directory (tenant) ID from Azure Portal
 */

import { Configuration, LogLevel } from "@azure/msal-browser";

export const msalConfig: Configuration = {
  auth: {
    // Application (client) ID from Azure Portal
    clientId: import.meta.env.VITE_AZURE_CLIENT_ID,

    // Authority URL - single tenant
    // For multi-tenant, use: "https://login.microsoftonline.com/common"
    // For work/school only: "https://login.microsoftonline.com/organizations"
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_AZURE_TENANT_ID}`,

    // Redirect URI - must match Azure Portal configuration exactly
    redirectUri: window.location.origin,

    // Where to redirect after logout
    postLogoutRedirectUri: window.location.origin,

    // Navigate back to the original page after login
    navigateToLoginRequestUrl: true,
  },

  cache: {
    // Where to store auth state
    // "localStorage" persists across tabs, "sessionStorage" is per-tab
    cacheLocation: "localStorage",

    // CRITICAL: Required for Safari and Edge compatibility
    // These browsers have stricter cookie policies that can break auth state
    storeAuthStateInCookie: true,
  },

  system: {
    loggerOptions: {
      logLevel: LogLevel.Warning,
      loggerCallback: (level, message, containsPii) => {
        if (containsPii) return; // Never log PII

        switch (level) {
          case LogLevel.Error:
            console.error("[MSAL]", message);
            break;
          case LogLevel.Warning:
            console.warn("[MSAL]", message);
            break;
          case LogLevel.Info:
            console.info("[MSAL]", message);
            break;
          case LogLevel.Verbose:
            console.debug("[MSAL]", message);
            break;
        }
      },
    },
    // Prevent popup/iframe timeouts on slow networks
    windowHashTimeout: 60000,
    iframeHashTimeout: 6000,
    loadFrameTimeout: 0,
  },
};

/**
 * Scopes for initial login
 * - openid, profile, email are standard OIDC scopes
 * - User.Read allows reading the signed-in user's profile from Microsoft Graph
 */
export const loginRequest = {
  scopes: ["openid", "profile", "email", "User.Read"],
};

/**
 * Scopes for calling your own API
 * Replace with your API's scope URI from Azure Portal:
 * App Registration > Expose an API > Add a scope
 *
 * Format: api://{client_id}/{scope_name}
 */
export const apiRequest = {
  scopes: [`api://${import.meta.env.VITE_AZURE_CLIENT_ID}/access_as_user`],
};

/**
 * Scopes for Microsoft Graph API calls
 * Add additional Graph scopes as needed:
 * - Mail.Read, Mail.Send for email
 * - Calendars.Read, Calendars.ReadWrite for calendar
 * - Files.Read, Files.ReadWrite for OneDrive
 */
export const graphRequest = {
  scopes: ["User.Read"],
};
